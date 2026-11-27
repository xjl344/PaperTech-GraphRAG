"""Check frozen routing inputs, saved output pairs and optional LangSmith readback."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from papertech.query_router_diagnostic import rule_candidate,validate
from papertech.evaluation_datasets import stable_id,write_json
from papertech.evaluation_details import clean
from papertech.settings import settings


def verify(path,remote=False):
    s=json.loads(path.read_text(encoding='utf8'));folder=ROOT/'artifacts/eval/stage-4'/s['benchmark']
    b=json.loads((folder/'benchmark.json').read_text(encoding='utf8'))
    digest=hashlib.sha256((folder/'benchmark.json').read_bytes()).hexdigest()
    assert digest==s['benchmark_sha256']==(folder/'benchmark.sha256').read_text().strip()
    assert s['status']=='completed' and len(s['results'])==48
    cases={c['id']:c for c in b['cases']}
    assert set(cases)=={f'R{i:02d}' for i in range(1,25)}
    assert {(r['case_id'],r['arm']) for r in s['results']}=={(c,a) for c in cases for a in ('Rule','Local-LLM')}
    calls=0
    for row in s['results']:
        q=cases[row['case_id']]['question'];assert q==row['question']==row['original_query']
        candidate=rule_candidate(q);assert row['rule_candidate']==candidate
        rid=stable_id(digest,s['run_id'],row['case_id'],row['arm']);assert row['trace_url'].endswith(rid)
        if row['arm']=='Rule':assert row['model_calls']==0 and row['subqueries']==[]
        else:
            calls+=row['model_calls'];assert row['model_calls']==1
            assert row['model_input']==dict(question=q,rule_candidate=[r['text'] for r in candidate])
            assert row['usage']['total_tokens']==row['usage']['prompt_tokens']+row['usage']['completion_tokens']
            if row['valid']:
                out=validate(q,row['parsed_output'],candidate)
                assert row['route']==out['route'] and row['subqueries']==out['subqueries']
            else:assert row['route']=='fallback' and row['validation_errors'] and not row['subqueries']
    assert calls==24
    result=dict(status='verified',questions=24,paired_results=48,model_calls=24,input_isolation=True,original_always_retained=True)
    if remote:
        from langsmith import Client
        cfg=settings(ROOT);cl=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',timeout_ms=20000,auto_batch_tracing=False)
        state=json.loads((path.parent/'langsmith-status.json').read_text(encoding='utf8'))
        examples={str(e.id):e for e in cl.list_examples(dataset_id=state['dataset_id'])}
        expected=json.loads((folder/'langsmith-dataset.json').read_text(encoding='utf8'))['examples']
        assert len(examples)==24 and all(examples[e['id']].inputs==e['inputs'] and examples[e['id']].outputs==e['outputs'] for e in expected)
        experiments=[]
        for exp in state['experiments']:
            wanted={stable_id(digest,s['run_id'],r['case_id'],r['arm']):r for r in s['results'] if r['arm']==exp['arm']}
            runs=list(cl.list_runs(project_id=exp['project_id']));roots={str(r.id):r for r in runs if not r.parent_run_id};children={str(r.id):r for r in runs if r.parent_run_id}
            assert set(roots)==set(wanted)
            feedback={str(f.id):f for f in cl.list_feedback(run_ids=list(wanted))};count=0
            for rid,row in wanted.items():
                assert roots[rid].outputs==clean(row) and str(roots[rid].reference_example_id)==stable_id(digest,row['case_id'])
                for key,value in row['metrics'].items():
                    assert abs(feedback[stable_id(rid,key)].score-value)<.000051;count+=1
                if row['usage']:
                    child=children[stable_id(rid,'local-decomposition-usage')]
                    assert child.inputs==row['model_input']
                    assert child.prompt_tokens==row['usage']['prompt_tokens'] and child.completion_tokens==row['usage']['completion_tokens']
            experiments.append(dict(arm=exp['arm'],roots=24,usage_spans=len(children),feedback=count))
        result['remote']=dict(examples=24,experiments=experiments)
    write_json(path.parent/'verification.json',result);print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-summary',type=Path,required=True);p.add_argument('--remote',action='store_true')
    args=p.parse_args();verify(args.run_summary.resolve(),args.remote)
