"""Verify saved decomposition outputs and optionally their LangSmith import."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.entity_aliases import method_spans,subqueries
from papertech.evaluation_datasets import stable_id,write_json
from papertech.evaluation_details import clean
from papertech.settings import settings


def verify(path,remote=False):
    summary=json.loads(path.read_text(encoding='utf8'))
    folder=ROOT/'artifacts/eval/stage-4'/summary['benchmark']
    benchmark=json.loads((folder/'benchmark.json').read_text(encoding='utf8'))
    digest=hashlib.sha256((folder/'benchmark.json').read_bytes()).hexdigest()
    assert summary['benchmark_sha256']==digest==(folder/'benchmark.sha256').read_text().strip()
    assert summary['status']=='completed'
    cases={c['id']:c for c in benchmark['cases']}
    assert len(cases)==24
    assert len(summary['results'])==48
    assert {(r['case_id'],r['arm']) for r in summary['results']}=={(cid,a) for cid in cases for a in ('Rule','Local-LLM')}
    no_anchor=[];calls=0;fragments=0
    for row in summary['results']:
        q=cases[row['case_id']]['question']
        assert q==row['question']
        rid=stable_id(digest,summary['run_id'],row['case_id'],row['arm'])
        assert row['trace_url'].endswith(rid)
        assert row['seconds']>=0
        if row['arm']=='Rule':
            assert row['subqueries']==subqueries(q)
            assert row['model_calls']==0 and row['usage'] is None
        else:
            calls+=row['model_calls']
            if not method_spans(q):
                no_anchor.append(row['case_id'])
                assert row['model_calls']==0 and row['subqueries']==[]
            else:
                assert row['model_calls']==1
                assert row['usage'] is not None
                assert row['usage']['total_tokens']==row['usage']['prompt_tokens']+row['usage']['completion_tokens']
            if not row['valid']:assert row['validation_errors'] and not row['subqueries']
        for query in row['subqueries']:
            for span in query['source_spans']:
                fragments+=1
                assert span['text']==q[span['start']:span['end']]
    assert calls==20 and no_anchor==['R07','R10','R18','R23']
    result=dict(verified=True,questions=24,paired_results=48,model_calls=calls,
        no_anchor_cases=no_anchor,exact_source_spans=fragments,
        generation_scope='question decomposition only; no retrieval, embeddings, reranking or answer generation')
    if remote:
        from langsmith import Client
        cfg=settings(ROOT)
        client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',timeout_ms=20000,auto_batch_tracing=False)
        state=json.loads((path.parent/'langsmith-status.json').read_text(encoding='utf8'))
        examples=list(client.list_examples(dataset_id=state['dataset_id']))
        expected_examples=json.loads((folder/'langsmith-dataset.json').read_text(encoding='utf8'))['examples']
        expected_examples={e['id']:e for e in expected_examples}
        assert len(examples)==24
        assert all(e.inputs==expected_examples[str(e.id)]['inputs'] and e.outputs==expected_examples[str(e.id)]['outputs'] for e in examples)
        imports=[]
        for exp in state['experiments']:
            arm=exp['arm']
            expected={stable_id(digest,summary['run_id'],r['case_id'],arm):r for r in summary['results'] if r['arm']==arm}
            runs=list(client.list_runs(project_id=exp['project_id']))
            roots={str(r.id):r for r in runs if not r.parent_run_id}
            children={str(r.id):r for r in runs if r.parent_run_id}
            assert set(roots)==set(expected)
            assert all(r.outputs==clean(expected[rid]) and str(r.reference_example_id)==stable_id(digest,expected[rid]['case_id']) for rid,r in roots.items())
            feedback={str(f.id):f for f in client.list_feedback(run_ids=list(expected))}
            nfeedback=0
            for rid,row in expected.items():
                for key,value in row['metrics'].items():
                    assert abs(feedback[stable_id(rid,key)].score-float(value))<.000051
                    nfeedback+=1
                if row['usage']:
                    child=children[stable_id(rid,'local-decomposition-usage')]
                    assert str(child.parent_run_id)==rid
                    assert child.prompt_tokens==row['usage']['prompt_tokens']
                    assert child.completion_tokens==row['usage']['completion_tokens']
            imports.append(dict(arm=arm,roots_verified=len(roots),usage_spans_verified=len(children),mechanical_feedback_verified=nfeedback))
        result['remote']=dict(dataset_examples=24,experiments=imports)
    write_json(path.parent/'verification.json',result)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary',type=Path,required=True)
    parser.add_argument('--remote',action='store_true')
    args=parser.parse_args();verify(args.run_summary.resolve(),args.remote)
