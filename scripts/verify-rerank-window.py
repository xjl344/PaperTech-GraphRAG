"""Recompute fixed-candidate input diagnosis and verify its remote experiments."""
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus
from papertech.entity_aliases import is_comparison
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import load_benchmark,stable_id,write_json
from papertech.evidence_context import assemble
from papertech.rerank_window_diagnostic import FILES,sha
from papertech.settings import settings


def main():
    folder=Path(sys.argv[1])
    summary=json.loads((folder/'summary.json').read_text(encoding='utf8'))
    bench,digest,directory=load_benchmark(ROOT,summary['benchmark'])
    assert summary['status']=='completed' and summary['benchmark_sha256']==digest
    assert {name:sha(ROOT/name) for name in FILES}==bench['code_sha256']
    assert len(summary['results'])==8
    assert len({(r['case_id'],r['arm']) for r in summary['results']})==8
    corpus,_,chunks=load_corpus(ROOT);chunks={c['chunk_id']:c for c in chunks}
    assert corpus==bench['corpus_id']
    cases={c['id']:c for c in bench['cases']}
    source_checks=0
    for row in summary['results']:
        cid=row['case_id'];case=cases[cid]
        frozen=bench['frozen_candidates'][cid]
        assert {r['chunk_id'] for r in row['ranked']}=={r['chunk_id'] for r in frozen}
        assert row['question']==case['question'] and row['usage'] is None
        assert not row['generate_requested'] and not row['provider_calls']
        assert row['model_pairs']==sum(len(ws) for ws in row['input_windows'].values())
        assert all(r['model_id']==bench['parent_reranker_model_id'] and r['device']=='cuda' for r in row['model_runs'])
        assert row['reranker_input_tokens_processed']==sum(w['pair_tokens'] for ws in row['input_windows'].values() for w in ws)
        for r in row['ranked']:
            windows=row['input_windows'][r['chunk_id']]
            assert r['rerank_score']==max(w['score'] for w in windows)
            for w in windows:
                assert w['text']==chunks[r['chunk_id']]['text'][w['start_char']:w['end_char']]
                assert w['pair_tokens']<=1024
                if row['arm']=='Quote-window':
                    assert w['document_tokens']<=160
                else:
                    assert len(windows)==1 and w['text']==chunks[r['chunk_id']]['text']
                source_checks+=1
        if row['arm']=='Whole-block':
            assert row['historical_full_score_max_error']==0
        metrics=support_metrics([r['chunk_id'] for r in row['ranked']],[e['chunk_id'] for e in row['evidence']],
            [bench['units'][u] for u in case['units']])
        assert metrics==row['metrics']
        evidence,_,details=assemble(row['ranked'],chunks,[],row['question'],is_comparison(row['question']),budget=6000,path_budget=0)
        assert evidence==row['evidence'] and details['context_bytes']==row['retrieval_summary']['context_bytes']
    assert summary['trace_verification']['verified']
    from langsmith import Client
    cfg=settings(ROOT)
    client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg['LANGSMITH_ENDPOINT'],auto_batch_tracing=False)
    payload=json.loads((directory/'langsmith-dataset.json').read_text(encoding='utf8'))
    remote={str(e.id):e for e in client.list_examples(dataset_id=summary['dataset_sync']['dataset_id'])}
    assert len(remote)==4
    for e in payload['examples']:
        assert set(remote[e['id']].inputs)=={'question'}
        assert remote[e['id']].inputs==e['inputs'] and remote[e['id']].outputs==e['outputs']
    exported=json.loads((folder/'langsmith-experiments.json').read_text(encoding='utf8'))['runs']
    feedback_checks=0
    for experiment in summary['dataset_sync']['experiments']:
        expected={p['id']:p for p in exported if p['_arm']==experiment['arm']}
        remote={str(r.id):r for r in client.list_runs(project_id=experiment['project_id'],is_root=True)}
        assert len(remote)==4 and set(remote)==set(expected)
        for rid,p in expected.items():
            assert remote[rid].outputs==p['outputs'] and remote[rid].inputs==p['inputs']
            assert str(remote[rid].reference_example_id)==p['reference_example_id']
        feedback={str(f.id):f for f in client.list_feedback(run_ids=list(expected))}
        for p in expected.values():
            for key,score in p['_metrics'].items():
                f=feedback[stable_id(p['id'],key)]
                assert math.isclose(f.score,float(score),abs_tol=.000050001)
                feedback_checks+=1
    result=dict(status='passed',benchmark_sha256=digest,results=8,dataset_examples=4,
        experiments=dict(Whole_block=4,Quote_window=4),metric_feedback_checked=feedback_checks,
        input_windows_verified=source_checks,whole_block_scores_exactly_reproduced=True,
        same_candidate_pools=True,selection_replay=True,reference_free_windowing=True,
        no_embedding_calls=True,no_generation_calls=True,tokenizer_pairs_audited=bench['tokenizer_audit']['pairs'],
        truncated_pairs=bench['tokenizer_audit']['truncated_pairs'],trace_verification=summary['trace_verification'])
    write_json(folder/'independent-verification.json',result)
    print(json.dumps(result,ensure_ascii=False))
    client.close()


if __name__=='__main__':
    main()
