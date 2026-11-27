"""Check dataset privacy boundaries and pairing before uploading external records."""
from copy import deepcopy
from pathlib import Path
import unittest

from papertech.evaluation_datasets import dataset_payload, load_benchmark, output_payload, run_payloads

ROOT = Path(__file__).resolve().parents[1]


class DatasetExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        cls.bench, cls.digest, _ = load_benchmark(ROOT, 'benchmark-v1')
        cls.summary = json.loads((ROOT / 'artifacts/reports/stage-4/runs/4981b3a1a81b49f1a47e3bd8022275cc/summary.json').read_text(encoding='utf-8'))

    def test_gold_stays_out_of_inputs_and_source_text_stays_local(self):
        import json
        payload = dataset_payload(self.bench, self.digest)
        for case, example in zip(self.bench['cases'], payload['examples']):
            self.assertEqual(example['inputs'], {'question': case['question']})
            self.assertIn('expected_answer', example['outputs'])
        serialized = json.dumps(payload)
        for unit in self.bench['units'].values():
            self.assertNotIn(json.dumps(unit['source_text']), serialized)
        self.assertEqual(payload, dataset_payload(self.bench, self.digest))

    def test_summary_export_excludes_answer_quotes_and_provider_payload(self):
        row = dict(self.summary['results'][0], raw={'secret': 'must-stay-local'})
        summary = output_payload(row, 'summary')
        self.assertNotIn('answer', summary)
        self.assertNotIn('raw', summary)
        self.assertNotIn('evidence', summary)
        self.assertNotIn('citations', summary)
        self.assertTrue(summary['selected_chunk_ids'])
        self.assertEqual(output_payload(row, 'full')['answer'], row['answer'])

    def test_pairs_share_reference_example_and_have_distinct_run_ids(self):
        rows = run_payloads(self.bench, self.digest, self.summary, 'summary')
        self.assertEqual(len(rows), 56)
        self.assertEqual(len({r['id'] for r in rows}), 56)
        self.assertEqual(len({r['reference_example_id'] for r in rows}), 28)
        reference_ids = {e['id'] for e in dataset_payload(self.bench, self.digest)['examples']}
        self.assertEqual({r['reference_example_id'] for r in rows}, reference_ids)
        self.assertTrue(all(not r['_metrics'] for r in rows if 'negative' in r['tags']))

    def test_mismatched_gold_or_question_cannot_be_imported(self):
        broken = deepcopy(self.summary)
        broken['benchmark_sha256'] = 'wrong-version'
        with self.assertRaisesRegex(ValueError, 'run_benchmark_mismatch'):
            run_payloads(self.bench, self.digest, broken, 'summary')
        broken = deepcopy(self.summary)
        broken['results'][0]['question'] = 'changed-question'
        with self.assertRaisesRegex(ValueError, 'run_case_mismatch'):
            run_payloads(self.bench, self.digest, broken, 'summary')

    def test_completed_run_requires_unique_and_complete_pairs(self):
        broken = deepcopy(self.summary)
        broken['results'].pop()
        with self.assertRaisesRegex(ValueError, 'completed_run_missing_pairs'):
            run_payloads(self.bench, self.digest, broken, 'summary')
        broken = deepcopy(self.summary)
        broken['results'].append(broken['results'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate_or_invalid'):
            run_payloads(self.bench, self.digest, broken, 'summary')


if __name__ == '__main__':
    unittest.main()
