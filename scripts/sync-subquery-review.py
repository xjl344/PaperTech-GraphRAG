"""Attach explicit agent review feedback to saved decomposition experiment runs."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import stable_id,write_json
from papertech.settings import settings


def sync(path):
    from langsmith import Client
    summary=json.loads(path.read_text(encoding='utf8'))
    notes=json.loads((path.parent/'review-notes.json').read_text(encoding='utf8'))
    state=json.loads((path.parent/'langsmith-status.json').read_text(encoding='utf8'))
    assert summary['status']=='completed' and notes['status']=='completed'
    assert len(notes['cases'])==24
    cfg=settings(ROOT)
    client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',timeout_ms=20000,auto_batch_tracing=False)
    project=next(e for e in state['experiments'] if e['arm']=='Local-LLM')
    rows={r['case_id']:r for r in summary['results'] if r['arm']=='Local-LLM'}
    jobs=[]
    for case in notes['cases']:
        row=rows[case['id']]
        rid=stable_id(summary['benchmark_sha256'],summary['run_id'],case['id'],'Local-LLM')
        metrics={'agent_review.paired_preference':{'胜':1,'平':.5,'负':0}[case['paired']]}
        if case['usable'] is not None:metrics['agent_review.usable_split']=int(case['usable'])
        for key,value in metrics.items():
            jobs.append(dict(run_id=rid,key=key,score=float(value),feedback_id=stable_id(rid,key),session_id=project['project_id'],
                comment='Codex题面审阅，非独立人工评分。'+case['note'],source_info=dict(origin=notes['origin'],paired_policy=notes['paired_policy'])))
    run_ids=[stable_id(summary['benchmark_sha256'],summary['run_id'],cid,'Local-LLM') for cid in rows]
    present={str(f.id):f for f in client.list_feedback(run_ids=run_ids)}
    for job in jobs:
        if job['feedback_id'] not in present:client.create_feedback(**job)
    for attempt in range(8):
        present={str(f.id):f for f in client.list_feedback(run_ids=run_ids)}
        valid=all(j['feedback_id'] in present and abs(present[j['feedback_id']].score-j['score'])<.000051 for j in jobs)
        if valid:break
        if attempt==7:raise ValueError('review_feedback_readback_incomplete')
        time.sleep(2)
    result=dict(status='review_feedback_verified',reviewed_cases=24,feedback_verified=len(jobs),origin=notes['origin'])
    write_json(path.parent/'review-sync-status.json',result)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary',type=Path,required=True)
    sync(parser.parse_args().run_summary.resolve())
