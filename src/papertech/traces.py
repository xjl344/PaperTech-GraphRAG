"""Explicit, bounded LangSmith outbox flush. No key => no network requests."""
import json
import uuid

from .audit import redact


def flush_traces(audit, cfg, limit=5, client=None):
    if not cfg.get('LANGSMITH_API_KEY'):
        return dict(status='not_configured', uploaded=0)
    if client is None:
        try:
            from langsmith import Client
            client = Client(api_key=cfg['LANGSMITH_API_KEY'], api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                            timeout_ms=10000, auto_batch_tracing=False)
        except Exception as exc:
            return dict(status='unavailable',uploaded=0,error=type(exc).__name__)
    uploaded = 0
    rows = audit.conn.execute("SELECT * FROM traces WHERE status='pending' ORDER BY rowid LIMIT ?", (max(0,min(limit,20)),)).fetchall()
    for row in rows:
        payload = json.loads(row['payload'])
        request = payload['request']
        root_id = uuid.UUID(row['id'])
        result = json.loads(request['result']) if request['result'] else {}
        try:
            # Stable IDs prevent producing a new run identity on ambiguous retries.
            client.create_run(id=root_id, name='papertech-question', run_type='chain',
                inputs=redact(dict(question=request['question'])), outputs=redact(result),
                start_time=request['started'], end_time=request['finished'],
                project_name=cfg.get('LANGSMITH_PROJECT') or 'papertech',
                extra=dict(metadata=dict(request_id=request['id'], candidates=payload['candidates'],calls=payload['calls'])))
            for span in payload['stages']:
                client.create_run(id=uuid.UUID(span['id']),parent_run_id=root_id,name=span['name'],run_type='chain',
                    inputs={},outputs=dict(detail=span['detail'],status=span['status']),
                    start_time=span['started'],end_time=span['finished'],
                    project_name=cfg.get('LANGSMITH_PROJECT') or 'papertech')
            # Ask SDK for actual tenant URL; do not fabricate a trace URL.
            remote_run = client.read_run(root_id)
            url = client.get_run_url(run=remote_run)
            audit.conn.execute("UPDATE traces SET status='uploaded',attempts=attempts+1,url=?,error=NULL WHERE id=?", (url,row['id']))
            result['trace_url'] = url
            audit.finish(request['id'],result)
            uploaded += 1
        except Exception as exc:
            audit.conn.execute('UPDATE traces SET attempts=attempts+1,error=? WHERE id=?', (type(exc).__name__,row['id']))
            # Break on connectivity/auth errors; no tight retry loop.
            audit.conn.commit()
            break
        audit.conn.commit()
    return dict(status='flushed',uploaded=uploaded,pending=audit.conn.execute("SELECT count(*) FROM traces WHERE status='pending'").fetchone()[0])
