"""Verify complete per-question exports and safe additive reference enrichment."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from papertech.corpus import load_corpus
from papertech.evaluation_datasets import dataset_payload, load_benchmark
from papertech.evaluation_details import (DetailedEvaluationDataset, PROFILE, clean,
    dataset_recorder, detailed_output, enrich_examples, paired_comparisons, result_mode,
    recorded_usage_payload)

ROOT = Path(__file__).resolve().parents[1]


class FakeClient:
    def __init__(self, payload, digest):
        self.dataset = SimpleNamespace(id='test-dataset', metadata={'benchmark_sha256': digest}, url='https://example.test/dataset')
        self.examples = {e['id']: SimpleNamespace(id=e['id'], inputs=deepcopy(e['inputs']),
            outputs=deepcopy(e['outputs']), metadata=deepcopy(e['metadata'])) for e in payload['examples']}
        self.updated = []

    def list_datasets(self, **kwargs):
        return [self.dataset]

    def list_examples(self, **kwargs):
        return list(self.examples.values())

    def update_example(self, example_id, outputs, metadata, split):
        self.examples[example_id].outputs = deepcopy(outputs)
        self.examples[example_id].metadata = deepcopy(metadata)
        self.updated.append(example_id)


class QuestionDetailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bench, cls.digest, _ = load_benchmark(ROOT, 'benchmark-v2')
        _, _, chunks = load_corpus(ROOT)
        cls.chunks = {chunk['chunk_id']: chunk for chunk in chunks}
        cls.baseline = dataset_payload(cls.bench, cls.digest)
        cls.payload = enrich_examples(cls.baseline, cls.bench, cls.chunks)

    def test_all_40_examples_show_facts_sources_and_rules_without_gold_in_inputs(self):
        self.assertEqual(len(self.payload['examples']), 40)
        for case, old, example in zip(self.bench['cases'], self.baseline['examples'], self.payload['examples']):
            self.assertEqual(example['inputs'], {'question': case['question']})
            for key, value in old['outputs'].items():
                self.assertEqual(example['outputs'][key], value)
            detail = example['outputs']
            self.assertEqual(len(detail['required_facts']), len(case['units']))
            expected = {cid for unit in case['units'] for cid in self.bench['units'][unit]['known_support_chunks']}
            self.assertEqual({s['chunk_id'] for s in detail['source_evidence']}, expected)
            for source in detail['source_evidence']:
                self.assertEqual(source['text'], self.chunks[source['chunk_id']]['text'])
                self.assertTrue(source['source_spans'])
            self.assertIn('relation_review', detail)
            self.assertIn('scoring_rules', detail)
            self.assertIn('evaluation_config', detail)
            self.assertNotIn('answer', detail)  # Reference material must not impersonate a model result.

    def test_graph_rubric_stays_in_references_and_survives_standard_export(self):
        bench = deepcopy(self.bench)
        case = bench['cases'][0]
        case['assessment'] = {'criteria': [{'id': 'C01', 'requirement': 'verify direction'}]}
        bench['paths_by_unit'] = {key: [{'claim_ids': ['reference-only-edge']}] for key in case['units']}
        bench['graph_snapshot'] = {'sha256': 'frozen-graph-hash', 'database': 'isolated-graph.sqlite3'}
        bench['dataset_description'] = 'graph-specific reference dataset'
        payload = enrich_examples(dataset_payload(bench, self.digest), bench, self.chunks)
        example = payload['examples'][0]
        self.assertEqual(example['inputs'], {'question': case['question']})
        self.assertEqual(example['outputs']['assessment'], case['assessment'])
        self.assertEqual(example['outputs']['expected_graph_paths'], bench['paths_by_unit'])
        self.assertEqual(payload['metadata']['graph_snapshot'], bench['graph_snapshot'])
        self.assertEqual(payload['description'], bench['dataset_description'])
        example['outputs']['assessment']['criteria'][0]['requirement'] = 'changed export'
        self.assertEqual(case['assessment']['criteria'][0]['requirement'], 'verify direction')

    def make_recorder(self, directory, allow):
        recorder = DetailedEvaluationDataset.__new__(DetailedEvaluationDataset)
        recorder.payload = deepcopy(self.payload)
        recorder.baseline = deepcopy(self.baseline)
        recorder.digest = self.digest
        recorder.allow_enrichment = allow
        recorder.client = FakeClient(self.baseline, self.digest)
        recorder.directory = Path(directory)
        recorder.status_path = Path(directory) / 'status.json'
        recorder.status = {'detail_profile': PROFILE}
        return recorder

    def test_additive_remote_upgrade_preserves_ids_gold_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.make_recorder(directory, True)
            ids_before = set(recorder.client.examples)
            recorder.sync_dataset()
            self.assertEqual(recorder.status['detail_examples_verified'], 40)
            self.assertEqual(set(recorder.client.examples), ids_before)
            self.assertEqual(len(recorder.client.updated), 40)
            recorder.sync_dataset()
            self.assertEqual(len(recorder.client.updated), 40)

    def test_enrichment_requires_matching_original_gold_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.make_recorder(directory, True)
            first = next(iter(recorder.client.examples.values()))
            first.outputs['expected_answer'] = 'independently changed gold'
            with self.assertRaisesRegex(ValueError, 'remote_modified'):
                recorder.sync_dataset()
            self.assertEqual(recorder.client.updated, [])
            recorder = self.make_recorder(directory, False)
            with self.assertRaisesRegex(ValueError, 'enrichment_required'):
                recorder.sync_dataset()

    def test_full_result_keeps_all_candidates_evidence_paths_and_usage(self):
        path = ROOT / 'artifacts/reports/stage-4/runs/4981b3a1a81b49f1a47e3bd8022275cc/C01-graph.json'
        row = json.loads(path.read_text(encoding='utf-8'))
        bench, _, _ = load_benchmark(ROOT, 'benchmark-v1')
        case = next(c for c in bench['cases'] if c['id'] == 'C01')
        row['raw'] = {'api_key': 'must-stay-local'}
        result = detailed_output(row, case, bench, self.chunks)
        self.assertEqual(result['answer'], row['answer'])
        self.assertEqual(len(result['ranked_candidates']), len(row['ranked']))
        for key in ('evidence', 'citations', 'graph_paths', 'generation_paths', 'usage', 'stage_timings'):
            self.assertEqual(result[key], row[key])
        self.assertEqual(len(result['fact_coverage']), len(case['units']))
        self.assertNotIn('raw', result)
        self.assertNotIn('must-stay-local', json.dumps(result))
        self.assertEqual(clean({'x': {'embedding': [1], 'quote': 'kept'}, 'headers': {'Authorization': 'secret'}}), {'x': {'quote': 'kept'}})

    def test_pair_comparison_reports_added_and_lost_evidence_without_semantic_score(self):
        summary = dict(results=[dict(case_id='X', arm='Hybrid', status='ok', metrics={'recall5': .5}, evidence=[{'chunk_id': 'a'}]),
            dict(case_id='X', arm='Hybrid+Graph', status='partial', metrics={'recall5': 1}, evidence=[{'chunk_id': 'b'}])])
        comparison = paired_comparisons(summary)['X']
        self.assertEqual(comparison['graph_minus_hybrid']['recall5'], .5)
        self.assertEqual(comparison['graph_added_evidence'], ['b'])
        self.assertEqual(comparison['graph_removed_evidence'], ['a'])
        self.assertNotIn('accuracy', comparison)

    def test_legacy_version_keeps_legacy_export_and_summary_policy(self):
        with patch('papertech.evaluation_details.EvaluationDataset') as legacy:
            dataset_recorder(ROOT, 'benchmark-v1', allow_enrichment=True)
            legacy.assert_called_once_with(ROOT, 'benchmark-v1')
        self.assertEqual(result_mode(ROOT, 'benchmark-v1'), 'summary')
        self.assertEqual(result_mode(ROOT, 'benchmark-v2'), 'full')

    def test_native_tokens_use_recorded_llm_child_and_actual_call_times(self):
        parent = dict(id='parent-evaluation-id')
        call = dict(id='provider-call-id', started='2026-11-15T07:45:42+00:00',
            finished='2026-11-15T07:45:45+00:00', status='ok',
            usage=json.dumps(dict(prompt_tokens=12, completion_tokens=3)))
        child = recorded_usage_payload(parent, call, 'parent-order')
        self.assertEqual(child['run_type'], 'llm')
        self.assertEqual(child['parent_run_id'], parent['id'])
        self.assertEqual(child['trace_id'], parent['id'])
        self.assertEqual(child['inputs'], {})
        self.assertEqual((child['end_time'] - child['start_time']).total_seconds(), 3)
        self.assertEqual(child['outputs']['usage_metadata'], dict(input_tokens=12, output_tokens=3, total_tokens=15))
        self.assertEqual(recorded_usage_payload(parent, call, 'parent-order')['id'], child['id'])

    def test_unknown_usage_is_not_imported_as_zero_native_tokens(self):
        self.assertIsNone(recorded_usage_payload(dict(id='parent'), dict(id='unknown', usage=None), 'order'))


if __name__ == '__main__':
    unittest.main()
