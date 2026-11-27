"""Validate report denominators, unknown usage and unchanged historical scores."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evaluation_report', ROOT / 'scripts/report-evaluation.py')
reporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporter)


class EvaluationReportTests(unittest.TestCase):
    def test_negatives_are_excluded_from_recall_but_kept_in_status_and_usage(self):
        source = dict(category='cross', status='partial', metrics=dict(recall5=.5, recall8=1.,
            mrr40=.25, evidence_coverage=.5, all_units=False), retrieval_compute_seconds=2.,
            generate_requested=True, provider_calls=[dict(usage=None)])
        negative = dict(source, category='negative', status='refused',
            metrics=dict(recall5=None, recall8=None, mrr40=None, evidence_coverage=None, all_units=None),
            retrieval_compute_seconds=100.)
        result = reporter.aggregate([source, negative])
        self.assertEqual(result['scored_questions'], 1)
        self.assertEqual(result['questions'], 2)
        self.assertEqual(result['recall5'], .5)
        self.assertEqual(result['p95_seconds'], 2.)
        self.assertEqual(result['usage_unknown'], 2)
        self.assertEqual(result['input_tokens'], 0)
        self.assertEqual(result['statuses'], {'partial': 1, 'refused': 1})

    def test_historical_aggregates_match_the_frozen_v1_report(self):
        from papertech.corpus import load_corpus
        from papertech.evaluation_datasets import load_benchmark
        benchmark, digest, _ = load_benchmark(ROOT, 'benchmark-v1')
        folder = ROOT / 'artifacts/reports/stage-4'
        summary = json.loads((folder / 'runs/4981b3a1a81b49f1a47e3bd8022275cc/summary.json').read_text(encoding='utf-8'))
        frozen = json.loads((folder / 'comparison.json').read_text(encoding='utf-8'))
        _, _, chunks = load_corpus(ROOT)
        result = reporter.build(benchmark, digest, summary, {c['chunk_id']: c for c in chunks})
        for arm in reporter.ARMS:
            for key in (*reporter.METRICS, 'all_units', 'p50_seconds', 'p95_seconds'):
                self.assertEqual(result['aggregates'][arm][key], frozen['aggregates'][arm][key])
        self.assertEqual(result['paired_changes'], {key: frozen['paired_changes'].get(key, {'gain': 0, 'tie': 24, 'regression': 0}) for key in reporter.METRICS})


if __name__ == '__main__':
    unittest.main()
