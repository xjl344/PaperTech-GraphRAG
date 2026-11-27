import json
from pathlib import Path
import sys
import unittest

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.kg_rebuild_extract import VERSION, disposition, extract, prompt_for


class FreshExtractionTests(unittest.TestCase):
    def setUp(self):
        self.paper = dict(title='G-Retriever: A framework', source_sha256='pdfsha')
        self.quote = 'G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation.'
        self.chunk = dict(paper_id='p', chunk_id='c', ordinal=0, parse_id='parse',
            text=self.quote, section='Related Work', content_kind='body',
            page_start=2, page_end=2, source_relative_path='paper.pdf', source_spans=[])

    def test_stark_skipped_without_a_model_request(self):
        class NoCalls:
            def post(self, *args, **kwargs):
                raise AssertionError('excluded block should not invoke a model')
        row = extract(NoCalls(), self.chunk, dict(self.paper, title='STaRK: Benchmarking retrieval'))
        self.assertEqual(row['status'], 'skipped')
        self.assertFalse(row['model_called'])
        self.assertEqual(row['skip_reason'], 'benchmark_paper_not_applicable')

    def test_fresh_output_passes_structural_and_semantic_validation(self):
        candidate = dict(subject_type='Method', subject='G-Retriever', predicate='HAS_COMPONENT',
                         object_type='Component', object='retrieval', evidence_quote=self.quote,
                         claim_kind='author_assertion', confidence=.9)
        requests = []
        def respond(request):
            requests.append(json.loads(request.content))
            return httpx.Response(200, json=dict(response=json.dumps(dict(relations=[candidate])),
                done_reason='stop', prompt_eval_count=400, eval_count=100, total_duration=1_000_000_000))
        with httpx.Client(transport=httpx.MockTransport(respond)) as client:
            row = extract(client, self.chunk, self.paper)
        self.assertEqual(row['status'], 'completed')
        self.assertEqual(len(requests), 1)
        self.assertEqual(row['parsed_output'], dict(relations=[candidate]))
        self.assertEqual(row['raw_count'], len(row['relations']) + len(row['rejected']))
        claim = row['relations'][0]
        self.assertEqual(claim['graph_version'], VERSION)
        self.assertNotIn('input_graph_version', claim)
        self.assertEqual(self.chunk['text'][claim['quote_start']:claim['quote_end']], self.quote)
        self.assertEqual(row['input_tokens'], 400)

    def test_pure_example_is_excluded_and_bad_section_label_is_advisory(self):
        self.assertIsNone(disposition(self.chunk, self.paper)[1])
        example = dict(self.chunk, text='>>> input: call(T)\n>>> output: [A, B]')
        self.assertEqual(disposition(example, self.paper)[1], 'chunk_kind_excluded:example')
        self.assertIn('章节（仅启发式）', prompt_for(self.chunk, self.paper))


if __name__ == '__main__':
    unittest.main()
