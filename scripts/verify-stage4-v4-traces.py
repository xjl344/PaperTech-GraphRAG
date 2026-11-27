"""Batch-read v4 live traces from LangSmith; never replay model requests."""
import argparse
import json
import logging
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.ingest import atomic_json
from papertech.settings import settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary', type=Path, required=True)
    args = parser.parse_args()
    summary_path = args.run_summary.resolve()
    folder = summary_path.parent
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    request_ids = {row['request_id'] for row in summary['results']}
    conn = sqlite3.connect(ROOT / 'data/live-traces.sqlite3')
    conn.row_factory = sqlite3.Row
    try:
        roots = [dict(row) for row in conn.execute("SELECT * FROM spans WHERE parent_id IS NULL")
            if json.loads(row['metadata']).get('request_id') in request_ids]
        ids = {row['id'] for row in roots}
        all_rows = [dict(row) for row in conn.execute('SELECT * FROM spans')]
        while True:
            grown = ids | {row['id'] for row in all_rows if row['parent_id'] in ids}
            if grown == ids:
                break
            ids = grown
        selected = [row for row in all_rows if row['id'] in ids]
        if len(roots) != len(request_ids):
            raise RuntimeError(f'local_trace_roots_missing:{len(roots)}/{len(request_ids)}')
        pending = conn.execute("SELECT count(*) FROM events WHERE status='pending'").fetchone()[0]
        expected = {}
        for row in selected:
            event = conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1", (row['id'],)).fetchone()
            expected[row['id']] = json.loads(event['payload']) if event else {}
    finally:
        conn.close()

    cfg = settings(ROOT)
    from langsmith import Client
    logging.getLogger('langsmith').setLevel(logging.CRITICAL)
    client = Client(api_key=cfg['LANGSMITH_API_KEY'],
        api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
        timeout_ms=10000, auto_batch_tracing=False)
    try:
        remote = {}
        ids_list = list(ids)
        for offset in range(0, len(ids_list), 50):
            batch = ids_list[offset:offset + 50]
            remote.update({str(run.id): run for run in client.list_runs(run_ids=batch, limit=len(batch),
                select=['id', 'name', 'end_time', 'prompt_tokens', 'completion_tokens'])})
        spans = []
        for row in selected:
            run = remote.get(row['id'])
            local_finished = row['finished'] is not None
            native_usage_matches = None
            payload = expected[row['id']]
            if 'prompt_tokens' in payload:
                native_usage_matches = bool(run) and run.prompt_tokens == payload.get('prompt_tokens') \
                    and run.completion_tokens == payload.get('completion_tokens')
            spans.append(dict(id=row['id'], name=run.name if run else row['name'],
                root=row['parent_id'] is None, local_finished=local_finished,
                remote_found=bool(run), remote_finished=bool(run and run.end_time),
                native_usage_matches=native_usage_matches))
            if row['parent_id'] is None and run:
                url = client.get_run_url(run=run)
                for result in summary['results']:
                    if result['request_id'] == json.loads(row['metadata']).get('request_id'):
                        result['trace_url'] = url
                        path = folder / (result['case_id'] + ('-graph.json' if result['arm'] == 'Hybrid+Graph' else '-hybrid.json'))
                        atomic_json(path, result)
                        break
        verified = pending == 0 and len(remote) == len(selected) and all(
            item['remote_finished'] and item['native_usage_matches'] is not False for item in spans)
        verification = dict(verified=verified, pending_events=pending, span_count=len(spans), spans=spans,
            recheck_mode='batch local v4 roots and descendants; no model calls replayed')
        summary['remote_verification'] = verification
        atomic_json(summary_path, summary)
        atomic_json(folder / 'remote-verification-final.json', verification)
        print(json.dumps(dict(verified=verified, local_roots=len(roots), local_spans=len(selected),
            remote_spans=len(remote), pending_events=pending), ensure_ascii=False))
        return 0 if verified else 1
    finally:
        client.close()


if __name__ == '__main__':
    raise SystemExit(main())
