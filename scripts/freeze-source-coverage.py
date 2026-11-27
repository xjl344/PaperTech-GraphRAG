"""Freeze a failure-selected diagnostic subset before source-selection changes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation_datasets import load_benchmark, write_json

VERSION = 'benchmark-source-coverage-v1'
PARENT_RUN = 'a2ab6cdee7144b96b7627ac96582fc87'
BASELINE_FILES = ('src/papertech/entity_aliases.py', 'src/papertech/evidence_context.py',
                  'src/papertech/workflow.py', 'src/papertech/retrieval.py')


def main():
    target = ROOT / 'artifacts/eval/stage-4' / VERSION
    if target.exists():
        raise SystemExit('diagnostic_version_already_exists; do not overwrite a frozen subset')
    parent, digest, _ = load_benchmark(ROOT, 'benchmark-v2')
    run_path = ROOT / 'artifacts/reports/stage-4/benchmark-v2/runs' / PARENT_RUN / 'summary.json'
    raw = run_path.read_bytes()
    summary = json.loads(raw)
    if summary['benchmark_sha256'] != digest or summary['status'] != 'completed':
        raise ValueError('parent_run_mismatch')
    graph = {row['case_id']: row for row in summary['results'] if row['arm'] == 'Hybrid+Graph'}
    selected, reasons = [], {}
    for case in parent['cases']:
        if case['category'] != 'cross':
            continue
        required = {parent['units'][key]['paper_id'] for key in case['units']}
        present = {item['paper_id'] for item in graph[case['id']]['evidence']}
        if required - present:
            selected.append(deepcopy(case))
            reasons[case['id']] = dict(required_papers=sorted(required),
                baseline_selected_papers=sorted(present), missing_papers=sorted(required - present))
    if len(selected) != 16:
        raise ValueError('unexpected_failure_subset_size')
    bench = deepcopy(parent)
    bench.update(version=VERSION, cases=selected,
        units={key: deepcopy(parent['units'][key]) for case in selected for key in case['units']},
        prior_exposure='Failure-selected from an observed development run; diagnostic only, not an unbiased quality estimate.',
        parent_benchmark=dict(version=parent['version'], sha256=digest, run_id=PARENT_RUN,
            summary_sha256=hashlib.sha256(raw).hexdigest()),
        selection=dict(rule='All cross-text cases where the parent Graph arm omitted at least one required paper from final evidence.',
            selected_case_ids=[case['id'] for case in selected], reasons=reasons),
        comparison=dict(arms=['Graph-before', 'Graph-after'], mode='frozen_candidate_evidence_replay',
            changed='question-driven source recognition and evidence reservation',
            fixed=['question', 'reference facts', 'ranked candidates and scores', 'retrieved graph paths',
                '6000-byte budget', 'rerank threshold', 'path assembly policy'],
            generation='No generation replayed; parent answers remain historical context only.'))
    bench['scoring'] = deepcopy(parent['scoring'])
    bench['scoring'].update(primary='All required source papers retained; measured using inherited references only after assembly.',
        denominator='16 failure-selected cross-text cases; before/after paired evidence replay. Not comparable to full v2 averages.',
        latency='Evidence assembly only, excluding retrieval, reranking and generation. Historical timings are separate.',
        answer_review='No new answers generated. No answer accuracy or citation success change is claimed.')
    bench['code_sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in BASELINE_FILES}
    write_json(target / 'benchmark.json', bench)
    (target / 'benchmark.sha256').write_text(hashlib.sha256((target / 'benchmark.json').read_bytes()).hexdigest() + '\n', encoding='utf-8')
    for name in BASELINE_FILES:
        destination = target / 'baseline' / Path(name).name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())
    print(json.dumps(dict(version=VERSION, questions=len(selected), selected_case_ids=[case['id'] for case in selected]), ensure_ascii=False))


if __name__ == '__main__':
    main()
