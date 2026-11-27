"""Durable requests, node spans, provider attempts, candidates and trace outbox."""
import json
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def redact(value):
    if isinstance(value, dict):
        return {k: '[REDACTED]' if re.search('key|password|authorization|secret', k, re.I) else redact(v) for k,v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r'(?i)(Bearer\s+)[\w.\-]+', r'\1[REDACTED]', value)
    return value


class Audit:
    def __init__(self, root, defer_live_flush=False):
        from .live_traces import LiveTraces
        self.live = LiveTraces(root, defer_flush=defer_live_flush)
        self.live_requests = {}
        (root / 'data').mkdir(exist_ok=True)
        self.conn = sqlite3.connect(root / 'data/rag.sqlite3', timeout=20)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, started TEXT, finished TEXT, question TEXT, status TEXT, result TEXT);
        CREATE TABLE IF NOT EXISTS stages (id TEXT PRIMARY KEY, request_id TEXT, name TEXT, started TEXT, finished TEXT, seconds REAL, status TEXT, detail TEXT);
        CREATE TABLE IF NOT EXISTS calls (id TEXT PRIMARY KEY, request_id TEXT, provider TEXT, attempt INTEGER, started TEXT, finished TEXT, seconds REAL, status TEXT, http_status INTEGER, usage TEXT, cost REAL);
        CREATE TABLE IF NOT EXISTS candidates (request_id TEXT, chunk_id TEXT, channel TEXT, rank INTEGER, score REAL);
        CREATE TABLE IF NOT EXISTS blocks (provider TEXT PRIMARY KEY, reason TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS traces (id TEXT PRIMARY KEY, request_id TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, url TEXT, error TEXT);
        ''')

    def start(self, question):
        request_id = str(uuid.uuid4())
        self.conn.execute('INSERT INTO requests VALUES (?,?,NULL,?,?,NULL)', (request_id, now(), question, 'running'))
        self.conn.commit()
        self.live_requests[request_id] = self.live.start('papertech-question-live', dict(request_id=request_id))
        return request_id

    def finish(self, request_id, result):
        self.conn.execute('UPDATE requests SET finished=?,status=?,result=? WHERE id=?', (now(), result['status'], json.dumps(redact(result), ensure_ascii=False), request_id))
        self.conn.commit()
        trace = self.live_requests.get(request_id)
        if trace and self.live.conn.execute('SELECT finished FROM spans WHERE id=?', (trace,)).fetchone()[0] is None:
            summary=result.get('retrieval_summary') or {}
            self.live.end(trace, dict(status=result['status'], retrieval_summary=redact(summary),
                                     stage_timings=result.get('stage_timings',[]),
                                     evidence_count=len(result.get('evidence') or []),
                                     citation_count=len(result.get('citations') or []),
                                     generation_path_count=len(result.get('generation_paths') or []),
                                     usage=result.get('usage'), errors=result.get('errors',[])),
                          error='workflow_error' if result['status'] == 'error' else None)

    def stage(self, request_id, name, fn):
        span = str(uuid.uuid4())
        start = time.monotonic()
        self.conn.execute('INSERT INTO stages VALUES (?,?,?,?,NULL,NULL,?,NULL)', (span, request_id, name, now(), 'running'))
        self.conn.commit()
        live_span = self.live.start(name, dict(request_id=request_id), parent=self.live_requests.get(request_id))
        try:
            result = fn()
        except Exception as exc:
            # Error class only: provider exception messages may echo headers or raw payload.
            self.conn.execute('UPDATE stages SET finished=?,seconds=?,status=?,detail=? WHERE id=?', (now(), time.monotonic()-start, 'error', type(exc).__name__, span))
            self.conn.commit()
            self.live.end(live_span, dict(status='error'), error=type(exc).__name__)
            raise
        self.conn.execute('UPDATE stages SET finished=?,seconds=?,status=?,detail=? WHERE id=?', (now(), time.monotonic()-start, 'ok', json.dumps(redact(result), ensure_ascii=False), span))
        self.conn.commit()
        metadata=dict(status='ok',seconds=time.monotonic()-start)
        if isinstance(result,dict):
            if isinstance(result.get('retrieval_summary'),dict):
                metadata['retrieval_summary']=redact(result['retrieval_summary'])
            for key in ('status','usage','model_name','errors','limitations'):
                if key in result:
                    metadata[key]=redact(result[key])
        self.live.end(live_span,metadata)
        return result

    def blocked(self, provider):
        return self.conn.execute('SELECT 1 FROM blocks WHERE provider=?', (provider,)).fetchone() is not None

    def block(self, provider):
        self.conn.execute('INSERT OR REPLACE INTO blocks VALUES (?,?,?)', (provider, 'HTTP402: manual reset required', now()))
        self.conn.commit()

    def record_candidates(self, request_id, channel, rows):
        self.conn.executemany('INSERT INTO candidates VALUES (?,?,?,?,?)', [(request_id,r['chunk_id'],channel,i+1,r['score']) for i,r in enumerate(rows)])
        self.conn.commit()

    def queue_trace(self, request_id):
        request = dict(self.conn.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone())
        stages = [dict(r) for r in self.conn.execute('SELECT * FROM stages WHERE request_id=? ORDER BY started', (request_id,))]
        calls = [dict(r) for r in self.conn.execute('SELECT * FROM calls WHERE request_id=? ORDER BY started', (request_id,))]
        candidates = [dict(r) for r in self.conn.execute('SELECT * FROM candidates WHERE request_id=? ORDER BY channel,rank', (request_id,))]
        trace_id = str(uuid.uuid4())
        payload = redact(dict(request=request, stages=stages, calls=calls, candidates=candidates))
        self.conn.execute('INSERT INTO traces(id,request_id,payload,status) VALUES (?,?,?,?)', (trace_id, request_id, json.dumps(payload, ensure_ascii=False), 'pending'))
        self.conn.commit()
        return trace_id

    def close(self):
        self.live.close()
        self.conn.close()
