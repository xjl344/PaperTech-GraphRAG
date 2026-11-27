"""Independently re-score saved three-arm results; no model calls or uploads."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import load_benchmark, write_json
from papertech.evidence_context import assemble
from papertech.isolated_graph import IsolatedGraph
from papertech.corpus import load_corpus
from papertech.entity_aliases import is_comparison
from papertech.retrieval_comparison import ARMS, VERSION, sha, diagnose


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-directory', type=Path, required=True)
    args = parser.parse_args()
    folder = args.run_directory.resolve()
    bench, digest, directory = load_benchmark(ROOT, VERSION)
    parent, parent_digest, _ = load_benchmark(ROOT, 'benchmark-v4')
    assert bench['parent_benchmark_sha256'] == parent_digest
    for case, original in zip(bench['cases'], parent['cases'], strict=True):
        assert {k: v for k, v in case.items() if k not in ('generate', 'parent_generate')} == {
            k: v for k, v in original.items() if k != 'generate'}
        assert not case['generate']
    assert bench['units'] == parent['units']
    corpus, _, chunks = load_corpus(ROOT)
    assert corpus == bench['corpus_id']
    chunks = {c['chunk_id']: c for c in chunks}
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    assert summary['status'] == 'completed'
    assert summary['benchmark_sha256'] == digest
    expected = {(c['id'], arm) for c in bench['cases'] for arm in ARMS}
    assert len(summary['results']) == len(expected) == 120
    assert {(r['case_id'], r['arm']) for r in summary['results']} == expected
    cases = {c['id']: c for c in bench['cases']}
    graph = IsolatedGraph(ROOT / bench['graph_snapshot']['database'], bench['graph_snapshot']['sha256'])
    try:
        for row in summary['results']:
            case = cases[row['case_id']]
            assert row['status'] in ('evidence_only', 'no_evidence')
            assert row['question'] == case['question']
            assert not row['generate_requested'] and row['usage'] is None and not row['provider_calls']
            assert row['trace_id']
            assert len(row['ranked']) <= 40 and len(row['evidence']) <= 8
            assert row['metrics'] == support_metrics([r['chunk_id'] for r in row['ranked']],
                [e['chunk_id'] for e in row['evidence']], [bench['units'][uid] for uid in case['units']])
            evidence, paths, detail = assemble(row['ranked'], chunks, [], row['question'],
                comparison=is_comparison(row['question']), budget=6000)
            assert evidence == row['evidence'] and not paths
            assert detail['context_bytes'] <= 6000 and detail['serialized_content_bytes'] <= 6000
            assert row['diagnosis'] == diagnose(row, case, bench, chunks, graph)
            stored = json.loads((folder / f'{row["case_id"]}-{row["arm"]}.json').read_text(encoding='utf-8'))
            assert stored == row
            allowed = {'Dense-only': {'dense'}, 'Graph-only': {'graph'}, 'Hybrid': {'fulltext', 'dense'}}[row['arm']]
            assert set(row['candidate_channels']) == allowed
            assert not row['retrieval_summary']['graph_fallback']
            if row['arm'] != 'Graph-only':
                assert not row['graph_paths']
            else:
                assert not row['retrieval_summary']['query_embedding_used']
            for e in row['evidence']:
                assert e['quote'] == chunks[e['chunk_id']]['text']
                assert e['source_spans'] == chunks[e['chunk_id']]['source_spans']
        assert summary['dataset_sync']['status'] == 'experiments_verified'
        assert len(summary['dataset_sync']['experiments']) == 3
        assert all(e['runs_verified'] == 40 for e in summary['dataset_sync']['experiments'])
        assert summary['trace_verification']['verified']
        assert all(sha(ROOT / path) == value for path, value in bench['code_sha256'].items())
        report = dict(status='passed', rows=120, cases=40, counts=dict(Counter(r['arm'] for r in summary['results'])),
            parent_questions_and_gold_unchanged=True, metrics_recomputed=True, selection_replayed=True,
            diagnosis_recomputed=True, source_provenance=True, channels_isolated=True,
            model_generation_calls=0, frozen_code_unchanged=True,
            langsmith=summary['dataset_sync'], trace_verification=summary['trace_verification'])
        write_json(folder / 'independent-verification.json', report)
        print(json.dumps(report, ensure_ascii=False))
    finally:
        graph.close()


if __name__ == '__main__':
    main()
