"""Synchronous metadata-only LangSmith spans with a durable ordered event outbox."""
import copy
import json
import logging
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

from .settings import settings


def timestamp():
    return datetime.now(timezone.utc).isoformat()


class LiveTraces:
    def __init__(self, root, cfg=None, client=None, defer_flush=False):
        self.root = root
        self.cfg = settings(root) if cfg is None else cfg
        self.client = client
        self.owns_client = client is None
        self.defer_flush = bool(defer_flush)
        (root / 'data').mkdir(exist_ok=True)
        self.conn = sqlite3.connect(root / 'data/live-traces.sqlite3', timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS spans (
                id TEXT PRIMARY KEY, parent_id TEXT, name TEXT, started TEXT,
                finished TEXT, metadata TEXT, url TEXT);
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, span_id TEXT, operation TEXT,
                payload TEXT, status TEXT DEFAULT 'pending', error TEXT);
        ''')

    def start(self, name, metadata, parent=None, kind='chain'):
        span_id = str(uuid.uuid4())
        started = timestamp()
        metadata = dict(metadata, capture_mode='live', trace_format='papertech-live-v1')
        payload = dict(id=span_id, name=name, run_type=kind, inputs={},
                       start_time=started, project_name=self.cfg.get('LANGSMITH_PROJECT') or 'papertech',
                       extra=dict(metadata=metadata))
        if parent:
            payload['parent_run_id'] = parent
        with self.conn:
            self.conn.execute('INSERT INTO spans(id,parent_id,name,started,metadata) VALUES (?,?,?,?,?)',
                              (span_id, parent, name, started, json.dumps(metadata)))
            self._enqueue(span_id, 'create', payload)
        if not self.defer_flush:
            self.flush()
        return span_id

    def end(self, span_id, outputs=None, error=None, usage=None):
        finished = timestamp()
        outputs = dict(outputs or {})
        row = self.conn.execute('SELECT metadata FROM spans WHERE id=?', (span_id,)).fetchone()
        metadata = json.loads(row['metadata'])
        payload = dict(run_id=span_id, end_time=finished, outputs=outputs,
                       extra=dict(metadata=metadata))
        if error:
            payload['error'] = error
        if usage and usage.get('input_tokens') is not None and usage.get('output_tokens') is not None:
            native = dict(input_tokens=usage['input_tokens'], output_tokens=usage['output_tokens'],
                          total_tokens=usage['input_tokens'] + usage['output_tokens'])
            outputs['usage_metadata'] = native
            metadata['usage_metadata'] = native
            payload.update(prompt_tokens=native['input_tokens'], completion_tokens=native['output_tokens'],
                           total_tokens=native['total_tokens'])
        with self.conn:
            self.conn.execute('UPDATE spans SET finished=? WHERE id=?', (finished, span_id))
            self._enqueue(span_id, 'update', payload)
        if not self.defer_flush:
            self.flush()

    def flush_async(self, limit=50):
        """Drain pending trace outbox in a background thread using an isolated SQLite connection."""
        if not self.cfg.get('LANGSMITH_API_KEY'):
            return None
        root, cfg = self.root, dict(self.cfg)
        def _worker():
            worker = LiveTraces(root, cfg=cfg, defer_flush=True)
            try:
                for _ in range(8):
                    res = worker.flush(limit=limit)
                    if res.get('uploaded', 0) < limit or res.get('status') != 'sent':
                        break
            finally:
                worker.close()
        thread = threading.Thread(target=_worker, name='papertech-trace-flush', daemon=True)
        thread.start()
        return thread

    def _enqueue(self, span_id, operation, payload):
        self.conn.execute('INSERT INTO events(span_id,operation,payload) VALUES (?,?,?)',
                          (span_id, operation, json.dumps(payload, ensure_ascii=False)))

    def flush(self, limit=20):
        if not self.cfg.get('LANGSMITH_API_KEY'):
            return dict(status='not_configured', uploaded=0)
        uploaded = 0
        try:
            if self.client is None:
                from langsmith import Client
                logging.getLogger('langsmith').setLevel(logging.CRITICAL)
                self.client = Client(api_key=self.cfg['LANGSMITH_API_KEY'],
                                     api_url=self.cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                                     timeout_ms=10000, auto_batch_tracing=False)
            for event in self.conn.execute("SELECT * FROM events WHERE status='pending' ORDER BY seq LIMIT ?", (limit,)).fetchall():
                payload = json.loads(event['payload'])
                if event['operation'] == 'create':
                    self.client.create_run(**copy.deepcopy(payload))
                else:
                    # update_run expects datetime objects; SQLite stores ISO timestamps.
                    for field in ('start_time', 'end_time'):
                        if isinstance(payload.get(field), str):
                            payload[field] = datetime.fromisoformat(payload[field])
                    self.client.update_run(**copy.deepcopy(payload))
                with self.conn:
                    self.conn.execute("UPDATE events SET status='sent',error=NULL WHERE seq=?", (event['seq'],))
                uploaded += 1
        except Exception as exc:
            with self.conn:
                self.conn.execute("UPDATE events SET error=? WHERE seq=(SELECT min(seq) FROM events WHERE status='pending')",
                                  (type(exc).__name__,))
            return dict(status='pending', uploaded=uploaded, error=type(exc).__name__)
        return dict(status='sent', uploaded=uploaded)

    def close(self):
        if self.client is not None and self.owns_client:
            self.client.close()
        self.conn.close()

    def url(self, span_id):
        """Return the tenant URL only after the remote Run is actually readable."""
        try:
            if self.client is None:
                return None
            remote = self.client.read_run(span_id)
            url = self.client.get_run_url(run=remote)
            with self.conn:
                self.conn.execute('UPDATE spans SET url=? WHERE id=?', (url, span_id))
            return url
        except Exception:
            return None
