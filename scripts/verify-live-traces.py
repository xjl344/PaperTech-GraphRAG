"""Flush durable live events or verify a selected extraction run against LangSmith."""
import argparse
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.ingest import atomic_json
from papertech.live_traces import LiveTraces


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', default='')
    parser.add_argument('--review-results', default='', help='Verify live review/write events for claims in this local result file')
    parser.add_argument('--flush', action='store_true')
    parser.add_argument('--allow-running', action='store_true')
    args = parser.parse_args()
    live = LiveTraces(ROOT)
    try:
        if args.flush:
            for _ in range(25):
                outcome = live.flush(limit=20)
                if not outcome['uploaded'] or outcome['status'] != 'sent':
                    break
        pending = live.conn.execute("SELECT count(*) FROM events WHERE status='pending'").fetchone()[0]
        if not args.run_id and not args.review_results:
            print(json.dumps(dict(pending=pending), ensure_ascii=False))
            return 0 if pending == 0 else 1
        if not live.cfg.get('LANGSMITH_API_KEY'):
            raise RuntimeError('langsmith_not_configured')
        from langsmith import Client
        logging.getLogger('langsmith').setLevel(logging.CRITICAL)
        client = Client(api_key=live.cfg['LANGSMITH_API_KEY'],
                        api_url=live.cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                        timeout_ms=10000, auto_batch_tracing=False)
        try:
            reviewed = {r['claim_id'] for r in json.loads(Path(args.review_results).read_text(encoding='utf-8'))} if args.review_results else set()
            roots = [dict(r) for r in live.conn.execute('SELECT * FROM spans WHERE parent_id IS NULL')
                     if (args.run_id and json.loads(r['metadata']).get('run_id') == args.run_id)
                     or json.loads(r['metadata']).get('claim_id') in reviewed]
            if not roots:
                raise RuntimeError('live_run_not_found')
            ids = {r['id'] for r in roots}
            rows = [dict(r) for r in live.conn.execute('SELECT * FROM spans')]
            while True:
                expanded = ids | {r['id'] for r in rows if r['parent_id'] in ids}
                if expanded == ids:
                    break
                ids = expanded
            selected = [r for r in rows if r['id'] in ids]
            results = []
            for row in selected:
                remote = client.read_run(row['id'])
                complete = row['finished'] is not None
                status_matches = (remote.end_time is not None) == complete
                usage = None
                updates = live.conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1", (row['id'],)).fetchone()
                if updates:
                    payload = json.loads(updates[0])
                    if 'prompt_tokens' in payload:
                        usage = remote.prompt_tokens == payload['prompt_tokens'] and remote.completion_tokens == payload['completion_tokens']
                url = client.get_run_url(run=remote) if row['parent_id'] is None else None
                if url:
                    with live.conn:
                        live.conn.execute('UPDATE spans SET url=? WHERE id=?', (url, row['id']))
                results.append(dict(id=row['id'], name=row['name'], local_finished=complete,
                                    remote_finished=remote.end_time is not None, status_matches=status_matches,
                                    native_usage_matches=usage, trace_url=url))
            selected_pending = sum(1 for r in live.conn.execute("SELECT span_id FROM events WHERE status='pending'") if r[0] in ids)
            verified = selected_pending == 0 and all(r['status_matches'] and r['native_usage_matches'] is not False for r in results)
            if not args.allow_running:
                verified = verified and all(r['local_finished'] for r in results)
            report = dict(run_id=args.run_id, status='verified' if verified else 'unconfirmed',
                          pending_events=selected_pending, span_count=len(results), spans=results)
            destination = Path(args.review_results).resolve().parent if args.review_results else ROOT / 'artifacts/reports/stage-3/runs' / args.run_id
            if not destination.is_dir():
                raise RuntimeError('run_report_directory_missing')
            filename = ('review-live-verification.json' if args.review_results else
                        'live-running-verification.json' if args.allow_running else 'live-verification.json')
            atomic_json(destination / filename, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if verified else 1
        finally:
            client.close()
    except Exception as exc:
        print(json.dumps(dict(status='unconfirmed', error_code=type(exc).__name__)))
        return 1
    finally:
        live.close()


if __name__ == '__main__':
    sys.exit(main())
