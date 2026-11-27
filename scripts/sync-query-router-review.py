"""Upload saved agent routing reviews without rerunning models."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import stable_id,write_json
from papertech.settings import settings


def sync(path):
    from langsmith import Client
    s=json.loads(path.read_text(encoding='utf8'));folder=path.parent
    notes=json.loads((folder/'review-notes.json').read_text(encoding='utf8'))
    state=json.loads((folder/'langsmith-status.json').read_text(encoding='utf8'))
    assert s['status']=='completed' and notes['status']=='completed' and len(notes['cases'])==24
    cfg=settings(ROOT);cl=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',timeout_ms=20000,auto_batch_tracing=False)
    exp=next(e for e in state['experiments'] if e['arm']=='Local-LLM')
    jobs=[]
    for c in notes['cases']:
        rid=stable_id(s['benchmark_sha256'],s['run_id'],c['id'],'Local-LLM')
        metrics={'agent_review.route_reasonable':{'合理':1,'可商榷':.5,'不合理':0}[c['route_quality']]}
        if c['usable'] is not None:metrics['agent_review.query_usable']=int(c['usable'])
        for key,score in metrics.items():
            jobs.append(dict(run_id=rid,key=key,score=float(score),feedback_id=stable_id(rid,key),session_id=exp['project_id'],
                comment='Codex题面审阅，非独立人工评分。'+c['note'],source_info=dict(origin=notes['origin'])))
    ids=list(dict.fromkeys(j['run_id'] for j in jobs))
    found={str(f.id):f for f in cl.list_feedback(run_ids=ids)}
    for j in jobs:
        if j['feedback_id'] not in found:cl.create_feedback(**j)
    for attempt in range(8):
        found={str(f.id):f for f in cl.list_feedback(run_ids=ids)}
        if all(j['feedback_id'] in found and abs(found[j['feedback_id']].score-j['score'])<.000051 for j in jobs):break
        if attempt==7:raise ValueError('review_readback_incomplete')
        time.sleep(2)
    status=dict(status='review_verified',cases=24,feedback=len(jobs),origin=notes['origin'],
        route_quality=dict(Counter(c['route_quality'] for c in notes['cases'])))
    write_json(folder/'review-sync-status.json',status);print(json.dumps(status,ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-summary',type=Path,required=True)
    sync(p.parse_args().run_summary.resolve())
