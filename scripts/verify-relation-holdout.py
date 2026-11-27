"""Independently recompute the saved two-arm experiment; never rerun inference."""
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark, stable_id, write_json
from papertech.settings import settings


def main():
    folder = Path(sys.argv[1])
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf8'))
    bench, digest, directory = load_benchmark(ROOT, summary['benchmark'])
    corpus, _, chunks = load_corpus(ROOT)
    chunk_map = {c['chunk_id']: c for c in chunks}
    assert corpus == bench['corpus_id']
    assert digest == summary['benchmark_sha256']
    assert summary['status'] == 'completed'
    for name, expected in bench['code_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    graph_path = ROOT / bench['graph_snapshot']['database']
    assert hashlib.sha256(graph_path.read_bytes()).hexdigest() == bench['graph_snapshot']['sha256']
    cases = {c['id']: c for c in bench['cases']}
    arms = ('Graph-only', 'Hybrid')
    rows = summary['results']
    assert Counter(r['arm'] for r in rows) == {'Graph-only': 40, 'Hybrid': 40}
    assert len({(r['case_id'],r['arm']) for r in rows}) == 80
    metric_checks, provenance_checks = 0, 0
    for r in rows:
        case = cases[r['case_id']]
        assert r['question'] == case['question']
        assert r['status'] != 'error' and not r['errors']
        ids = [c['chunk_id'] for c in r['ranked']]
        selected = {e['chunk_id'] for e in r['evidence']}
        pools = [set(bench['units'][u]['known_support_chunks']) for u in case['units']]
        def fraction(available):
            return sum(bool(set(available) & p) for p in pools) / len(pools)
        first = next((i for i,cid in enumerate(ids,1) if any(cid in p for p in pools)),None)
        expected = dict(recall5=fraction(ids[:5]),recall8=fraction(ids[:8]),
            mrr40=1/first if first else 0,evidence_coverage=fraction(selected),all_units=fraction(selected)==1)
        assert r['metrics'] == expected, r['case_id']
        assert math.isclose(r['source_metrics']['candidate_pool_coverage40'],fraction(ids))
        metric_checks += len(expected)+1
        assert len(ids) <= 40 and len(selected) <= 8
        assert r['retrieval_summary']['context_bytes'] <= 6000
        assert not r['generate_requested'] and not r['generation_paths'] and not r['provider_calls']
        assert r['usage'] is None and r.get('trace_url')
        assert set(r['candidate_channels']) == ({'graph'} if r['arm']=='Graph-only' else {'fulltext','dense'})
        assert not r['retrieval_summary']['graph_fallback']
        assert r['retrieval_summary']['query_embedding_used'] == (r['arm']=='Hybrid')
        assert r['order'] == ((list(cases).index(r['case_id']) + (r['arm']=='Hybrid')) % 2 + 1)
        for e in r['evidence']:
            source = chunk_map[e['chunk_id']]
            assert e['quote'] == source['text'] and e['source_spans'] == source['source_spans']
            assert hashlib.sha256(source['text'].encode()).hexdigest() == source['text_sha256']
            provenance_checks += 1
        for d in r['diagnosis']['facts']:
            assert (d['reason']=='covered') == bool(selected & set(d['known_support_chunks']))
    exported = json.loads((folder/'langsmith-experiments.json').read_text(encoding='utf8'))['runs']
    expected_runs = {p['id']:p for p in exported}
    assert len(expected_runs)==80
    cfg = settings(ROOT)
    from langsmith import Client
    client = Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg['LANGSMITH_ENDPOINT'],auto_batch_tracing=False)
    dataset = client.read_dataset(dataset_id=summary['dataset_sync']['dataset_id'])
    remote_examples = {str(e.id):e for e in client.list_examples(dataset_id=dataset.id)}
    payload = json.loads((directory/'langsmith-dataset.json').read_text(encoding='utf8'))
    assert len(remote_examples)==40
    for e in payload['examples']:
        actual = remote_examples[e['id']]
        assert set(actual.inputs)=={'question'} and actual.inputs == e['inputs'] and actual.outputs == e['outputs']
    remote_counts, feedback_count = {}, 0
    for experiment in summary['dataset_sync']['experiments']:
        remote = {str(r.id):r for r in client.list_runs(project_id=experiment['project_id'],is_root=True)}
        group = {rid:p for rid,p in expected_runs.items() if p['_arm']==experiment['arm']}
        assert set(remote)==set(group)
        for rid,r in remote.items():
            p=group[rid]
            assert r.inputs==p['inputs'] and r.outputs==p['outputs']
            assert str(r.reference_example_id)==p['reference_example_id']
            assert r.start_time==datetime.fromisoformat(p['start_time']) and r.end_time==datetime.fromisoformat(p['end_time'])
        feedback = {str(f.id):f for f in client.list_feedback(run_ids=list(group))}
        for rid,p in group.items():
            for k,v in p['_metrics'].items():
                f = feedback[stable_id(rid,k)]
                assert math.isclose(f.score,float(v),abs_tol=.000050001,rel_tol=0)
                feedback_count+=1
        remote_counts[experiment['arm']]=len(remote)
    result=dict(status='passed',benchmark_sha256=digest,results=80,question_only_inputs=40,
        recomputed_metric_checks=metric_checks,checked_evidence_provenance=provenance_checks,
        remote_experiment_counts=remote_counts,remote_feedback_checked=feedback_count,
        trace_urls_complete=80,code_hashes_unchanged=True,graph_unchanged=True,generation_calls=0)
    write_json(folder/'independent-verification.json',result)
    print(json.dumps(result,ensure_ascii=False))
    client.close()


if __name__=='__main__':
    main()
