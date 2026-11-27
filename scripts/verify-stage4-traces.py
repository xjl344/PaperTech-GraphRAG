"""Batch-read only unresolved LangSmith spans; never replay model requests."""
import argparse
import json
import logging
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.settings import settings
from papertech.ingest import atomic_json
from papertech.audit import now


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark',default='benchmark-v1',choices=('benchmark-v1','benchmark-v2'))
    parser.add_argument('--run-summary',type=Path)
    args=parser.parse_args()
    report_root=ROOT/'artifacts/reports/stage-4'
    if args.benchmark!='benchmark-v1':report_root=report_root/args.benchmark
    folder=args.run_summary.resolve().parent if args.run_summary else Path(json.loads((report_root/'latest.json').read_text())['directory'])
    path=folder/'summary.json'; summary=json.loads(path.read_text(encoding='utf-8'))
    verification=summary['remote_verification']
    unresolved=[row['id'] for row in verification['spans'] if not row['finished'] or row.get('native_usage_matches') is False]
    if not unresolved:
        print(json.dumps(dict(verified=verification['verified'],unresolved=0)));return 0
    initial=folder/'remote-verification-initial.json'
    if not initial.exists():atomic_json(initial,verification)
    cfg=settings(ROOT)
    from langsmith import Client
    logging.getLogger('langsmith').setLevel(logging.CRITICAL)
    client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                  timeout_ms=10000,auto_batch_tracing=False)
    conn=sqlite3.connect(ROOT/'data/live-traces.sqlite3')
    try:
        remote={}
        for offset in range(0,len(unresolved),50):
            ids=unresolved[offset:offset+50]
            remote.update({str(run.id):run for run in client.list_runs(run_ids=ids,limit=len(ids),
                  select=['id','name','end_time','prompt_tokens','completion_tokens'])})
        for row in verification['spans']:
            if row['id'] not in unresolved:continue
            run=remote.get(row['id'])
            if run is None:continue
            event=conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1",(row['id'],)).fetchone()
            payload=json.loads(event[0]) if event else {}
            row.update(name=run.name,finished=run.end_time is not None,native_usage_matches=None,verification_mode='batch_recovery')
            row.pop('error',None)
            if 'prompt_tokens' in payload:
                row['native_usage_matches']=(run.prompt_tokens==payload['prompt_tokens'] and run.completion_tokens==payload['completion_tokens'])
        verification['verified']=not verification['pending_events'] and all(row['finished'] and row.get('native_usage_matches') is not False for row in verification['spans'])
        verification.update(rechecked_at=now(),recheck_mode='batch unresolved only; no model calls replayed')
        summary['remote_verification']=verification
        atomic_json(path,summary)
        atomic_json(folder/'remote-verification-final.json',verification)
        print(json.dumps(dict(verified=verification['verified'],batch_requested=len(unresolved),batch_returned=len(remote),
            unresolved=sum(not r['finished'] or r.get('native_usage_matches') is False for r in verification['spans']))))
        return 0 if verification['verified'] else 1
    except Exception as exc:
        print(json.dumps(dict(status='unconfirmed',error_code=type(exc).__name__)))
        return 1
    finally:client.close();conn.close()


if __name__=='__main__':sys.exit(main())
