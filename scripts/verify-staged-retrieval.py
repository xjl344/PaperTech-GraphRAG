"""Independent source metrics, original-score preservation and remote readback."""
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark,stable_id,write_json
from papertech.settings import settings
from papertech.staged_retrieval_diagnostics import WIDTH,RESOURCE,RECALL,PARENT,FILES,sha


def main():
    folder=Path(sys.argv[1]);s=json.loads((folder/'summary.json').read_text(encoding='utf8'))
    b,d,directory=load_benchmark(ROOT,s['benchmark']);cases={c['id']:c for c in b['cases']}
    assert s['status']=='completed' and s['benchmark_sha256']==d
    assert {n:sha(ROOT/n) for n in FILES}==b['code_sha256']
    parent=json.loads((ROOT/PARENT/'summary.json').read_text(encoding='utf8'))
    parent={r['case_id']:r for r in parent['results'] if r['arm']=='Hybrid'}
    corpus,_,chunks=load_corpus(ROOT);chunks={c['chunk_id']:c for c in chunks}
    assert corpus==b['corpus_id']
    assert len(s['results'])==40*len(b['arms'])
    assert Counter(r['arm'] for r in s['results'])=={a:40 for a in b['arms']}
    assert len({(r['case_id'],r['arm']) for r in s['results']})==len(s['results'])
    checks=0;selected_checks=0;model_pairs=0
    for row in s['results']:
        case=cases[row['case_id']];p=parent[case['id']]
        ids=[r['chunk_id'] for r in row['ranked']];selected={r['chunk_id'] for r in row['evidence']}
        pools=[set(b['units'][u]['known_support_chunks']) for u in case['units']]
        fraction=lambda items:sum(bool(set(items)&pool) for pool in pools)/len(pools)
        assert row['question']==case['question'] and not row['errors']
        assert not row['generate_requested'] and not row['generation_paths'] and not row['provider_calls'] and row['usage'] is None
        first=next((i for i,cid in enumerate(ids,1) if i<=40 and any(cid in pool for pool in pools)),None)
        expected=dict(recall5=fraction(ids[:5]),recall8=fraction(ids[:8]),mrr40=1/first if first else 0,
            evidence_coverage=None if b['version']==WIDTH else fraction(selected),
            all_units=None if b['version']==WIDTH else fraction(selected)==1)
        assert expected==row['metrics']
        assert row['source_metrics']['candidate_pool_coverage']==fraction(ids)
        checks+=6
        union={r['chunk_id'] for rows in row['candidate_channels'].values() for r in rows}
        assert set(ids)==union
        if b['version']==WIDTH:
            assert row['model_calls']==[] and row['new_model_pairs']==0 and not selected
            assert row['candidate_channels']['dense'][:20]==p['candidate_channels']['dense']
            assert row['candidate_channels']['fulltext']==p['candidate_channels']['fulltext']
            assert len(row['candidate_channels']['dense'])==int(row['arm'].removeprefix('Dense'))
        else:
            assert row['selection_replay_verified']
            assert row['retrieval_summary']['context_bytes']<=row['selection_config']['budget']
            assert len(selected)<=row['selection_config']['evidence_max']
            if b['version']==RESOURCE:
                assert row['ranked']==p['ranked']
                if row['arm']=='Named-6000-8':
                    assert row['evidence']==p['evidence']
            else:
                previous={r['chunk_id']:r['rerank_score'] for r in p['ranked']}
                assert all(r['rerank_score']==previous[r['chunk_id']] for r in row['ranked'] if r['chunk_id'] in previous)
                new_ids=set(ids)-set(previous)
                assert row['new_model_pairs']==len(new_ids)
                assert all(call['model_id']==p['retrieval_summary']['reranker']['model_id'] and call['device']=='cuda' for call in row['model_calls'])
                model_pairs+=row['new_model_pairs']
        for e in row['evidence']:
            c=chunks[e['chunk_id']]
            assert e['quote']==c['text'] and e['source_spans']==c['source_spans']
            selected_checks+=1
        for fact in row['diagnosis']['facts']:
            pool=set(fact['known_support_chunks'])
            if b['version']==WIDTH:
                assert (fact['reason']=='candidate_available')==bool(set(ids)&pool)
            else:
                assert (fact['reason']=='covered')==bool(selected&pool)
    from langsmith import Client
    cfg=settings(ROOT);client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg['LANGSMITH_ENDPOINT'],auto_batch_tracing=False)
    payload=json.loads((directory/'langsmith-dataset.json').read_text(encoding='utf8'))
    remote={str(e.id):e for e in client.list_examples(dataset_id=s['dataset_sync']['dataset_id'])}
    assert len(remote)==40
    for e in payload['examples']:
        assert set(remote[e['id']].inputs)=={'question'}
        assert remote[e['id']].inputs==e['inputs'] and remote[e['id']].outputs==e['outputs']
    exported=json.loads((folder/'langsmith-experiments.json').read_text(encoding='utf8'))['runs']
    links=json.loads((folder/'experiment-trace-links.json').read_text(encoding='utf8'))
    assert len(links)==len(s['results']) and all(links.values())
    feedback_checks=0
    for experiment in s['dataset_sync']['experiments']:
        expected={p['id']:p for p in exported if p['_arm']==experiment['arm']}
        remote={str(r.id):r for r in client.list_runs(project_id=experiment['project_id'],is_root=True)}
        assert len(remote)==40 and set(remote)==set(expected)
        for rid,p in expected.items():
            r=remote[rid]
            assert r.inputs==p['inputs'] and r.outputs==p['outputs'] and str(r.reference_example_id)==p['reference_example_id']
            assert r.start_time==datetime.fromisoformat(p['start_time']) and r.end_time==datetime.fromisoformat(p['end_time'])
        feedback={str(f.id):f for f in client.list_feedback(run_ids=list(expected))}
        for p in expected.values():
            for key,value in p['_metrics'].items():
                f=feedback[stable_id(p['id'],key)];assert math.isclose(f.score,float(value),rel_tol=0,abs_tol=.000050001)
                feedback_checks+=1
    output=dict(status='passed',results=len(s['results']),examples=40,metric_recomputations=checks,
        checked_evidence_sources=selected_checks,remote_feedback_verified=feedback_checks,
        experiment_traces_verified=len(links),new_reranker_pairs=model_pairs,
        generation_calls=0,embedding_calls=0,reference_inputs_excluded=True,code_sha256_unchanged=True)
    write_json(folder/'independent-verification.json',output)
    print(json.dumps(output,ensure_ascii=False))
    client.close()


if __name__=='__main__':
    main()
