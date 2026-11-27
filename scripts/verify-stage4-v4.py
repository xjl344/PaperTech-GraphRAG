"""Verify a completed v4 evaluation and its recorded remote readbacks; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation import criterion_source_coverage
from papertech.evaluation_datasets import load_benchmark, write_json


def verify(folder):
    bench, digest, _ = load_benchmark(ROOT, 'benchmark-v4')
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    contract = json.loads((folder / 'execution-contract.json').read_text(encoding='utf-8'))
    report = json.loads((folder / 'report/comparison.json').read_text(encoding='utf-8'))
    exports = json.loads((folder / 'langsmith-experiments.json').read_text(encoding='utf-8'))
    cases = {case['id']: case for case in bench['cases']}
    rows = {(r['case_id'], r['arm']): r for r in summary['results']}
    checks = {}
    checks['completed_40_pairs'] = (summary['status'] == 'completed' and len(summary['results']) == 80
        and set(rows) == {(cid, arm) for cid in cases for arm in ('Hybrid', 'Hybrid+Graph')})
    checks['frozen_reference_and_runtime'] = (summary['benchmark_sha256'] == digest == contract['benchmark_sha256']
        and summary['execution_config'] == contract['runtime'])
    checks['code_unchanged'] = all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == value
        for name, value in contract['runtime']['code_sha256'].items())
    graph = contract['runtime']['graph_snapshot']
    checks['graph_unchanged'] = hashlib.sha256((ROOT / graph['database']).read_bytes()).hexdigest() == graph['sha256']
    checks['same_base_candidates'] = all(
        [c for c in rows[cid, 'Hybrid']['candidate_channels'] if c['channel'] != 'graph'] ==
        [c for c in rows[cid, 'Hybrid+Graph']['candidate_channels'] if c['channel'] != 'graph'] for cid in cases)
    checks['shared_vectors'] = summary['shared_vector_cache_hits'] == 80 and len(summary['shared_embedding_calls']) == 1
    checks['isolated_graph_treatment'] = all(
        not row['graph_paths'] and not row['retrieval_summary']['graph_executed'] if row['arm'] == 'Hybrid' else
        row['retrieval_summary'].get('graph_audit', {}).get('graph_sha256') == graph['sha256']
        for row in rows.values())
    checks['reference_excluded_from_inputs'] = all(
        row['question'] == cases[row['case_id']]['question'] and
        row['criterion_source_coverage'] == criterion_source_coverage(cases[row['case_id']],
            [e['chunk_id'] for e in row['evidence']], bench['units']) for row in rows.values())
    checks['147_source_criteria_per_arm'] = all(sum(len(row['criterion_source_coverage'])
        for row in rows.values() if row['arm'] == arm) == 147 for arm in ('Hybrid', 'Hybrid+Graph'))
    checks['budgets'] = all(len(row['evidence']) <= 8 and len(row['generation_paths']) <= 4
        and len(row['graph_paths']) <= 40 and row['retrieval_summary']['evidence_bytes'] <= 6000
        and row['retrieval_summary']['graph_context_bytes'] <= 1200
        and row['retrieval_summary']['serialized_content_bytes'] <= 7200 for row in rows.values())
    checks['report_sources_and_bases'] = report['source_checks_passed'] and report['base_candidates_identical']
    checks['original_traces_read_back'] = summary.get('remote_verification', {}).get('verified') is True
    sync = summary.get('dataset_sync', {})
    checks['remote_examples_and_experiments'] = (sync.get('status') == 'experiments_verified'
        and sync.get('examples_verified') == 40 and len(sync.get('experiments', [])) == 2)
    checks['remote_results_feedback_and_tokens'] = True
    for experiment in sync.get('experiments', []):
        arm = experiment['arm']
        payloads = [p for p in exports['runs'] if p['_arm'] == arm]
        expected_feedback = sum(v is not None for p in payloads for v in p['_metrics'].values())
        known_calls = sum(bool(call.get('usage')) for p in payloads for call in p['outputs']['provider_calls'])
        checks['remote_results_feedback_and_tokens'] &= (
            experiment['runs_verified'] == len(payloads) == 40 and experiment['feedback_verified'] == expected_feedback
            and experiment['generation_usage_runs_verified'] == known_calls)
    checks['exported_results_match_local'] = len(exports['runs']) == 80 and all(
        p['inputs'] == {'question': cases[p['extra']['metadata']['case_id']]['question']}
        and p['outputs']['criterion_source_coverage'] == rows[p['extra']['metadata']['case_id'], p['_arm']]['criterion_source_coverage']
        for p in exports['runs'])
    result = dict(status='passed' if all(checks.values()) else 'failed', run_id=summary['run_id'], checks=checks,
        model_calls=0, note='检查核对来源、配置、配对、预算及已回读的远端记录；不是独立答案语义评分。')
    write_json(folder / 'verification.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-directory', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.run_directory)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
