"""Unit tests for Direction 1 (windowed rerank, subquery-balanced MMR) and Direction 2 (v3 [E1:q2] citations)."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx

from papertech.citations import quote_options, validate_answer_with_meta
from papertech.evidence_context import assemble
from papertech.providers import Providers
from papertech.retrieval import chunk_windows, lexical_jaccard
from papertech.workflow import Workflow

ROOT = Path(__file__).resolve().parents[1]


class P4WindowAndV3CitationTests(unittest.TestCase):
    def test_chunk_windows_splits_long_chunks_with_contextual_prefix_and_keeps_short_chunks_single(self):
        short = dict(chunk_id='c_short', title='ToG', section='3 Method', text='Short method description.')
        w_short = chunk_windows(short, max_chars=700, overlap=250)
        self.assertEqual(len(w_short), 1)
        self.assertTrue(w_short[0]['text'].startswith('Title: ToG\nSection: 3 Method\n\n'))

        long_text = ' '.join(f'Sentence {i:03d} explains specific pruning and traversal details.' for i in range(60))
        long_chunk = dict(chunk_id='c_long', title='ToG', section='3.2 Pruning', text=long_text)
        w_long = chunk_windows(long_chunk, max_chars=700, overlap=250, max_windows=5)
        self.assertGreaterEqual(len(w_long), 3)
        self.assertLessEqual(len(w_long), 5)
        self.assertTrue(all(w['text'].startswith('Title: ToG\nSection: 3.2 Pruning\n\n') for w in w_long))

    def test_subquery_balanced_and_mmr_rescue_second_subquery_high_value_chunk(self):
        chunks = {}
        # Paper A has 5 near-duplicate high-scoring chunks for SQ01
        base_a = 'StructGPT iteratively invokes interfaces over knowledge graphs and tables to answer questions. '
        for i in range(5):
            chunks[f'a{i}'] = dict(chunk_id=f'a{i}', paper_id='pA', parse_id='v', title='PaperA', section='Method',
                page_start=1, page_end=1, source_spans=[{}], source_relative_path='a.pdf',
                text=base_a * 4 + f'Variant note {i}.')
        # Paper B has 2 distinct chunks for SQ02 with lower absolute scores (0.48, 0.42)
        chunks['b0'] = dict(chunk_id='b0', paper_id='pB', parse_id='v', title='PaperB', section='Intro',
            page_start=1, page_end=1, source_spans=[{}], source_relative_path='b.pdf',
            text='PaperB introduces a new retrieval framework for textual graphs.')
        chunks['b1'] = dict(chunk_id='b1', paper_id='pB', parse_id='v', title='PaperB', section='Experiments',
            page_start=5, page_end=5, source_spans=[{}], source_relative_path='b.pdf',
            text='Evaluated on WebQSP and CWQ with top-k=20 sampling and cost budget limits.')
        ranked = [
            dict(chunk_id=f'a{i}', sources=[], found_by=['SQ01'], best_query_id='SQ01',
                 rerank_score=0.95 - i * 0.02, owner_scores={'SQ01': 0.95 - i * 0.02})
            for i in range(5)
        ] + [
            dict(chunk_id='b0', sources=[], found_by=['SQ02'], best_query_id='SQ02',
                 rerank_score=0.50, owner_scores={'SQ02': 0.50}),
            dict(chunk_id='b1', sources=[], found_by=['SQ02'], best_query_id='SQ02',
                 rerank_score=0.45, owner_scores={'SQ02': 0.45}),
        ]
        self.assertGreater(lexical_jaccard(chunks['a0']['text'], chunks['a1']['text']), 0.7)
        ev, _, _ = assemble(ranked, chunks, [], '比较两个方法的流程与评测设置', comparison=True,
                            budget=18000, evidence_max=4, score_policy='relative',
                            reservation_policy='subquery_balanced', subquery_ids=['SQ01', 'SQ02'])
        selected = {e['chunk_id'] for e in ev}
        # Both b0 and b1 (second subquery!) must enter top-4 instead of being crowded out by duplicate a1..a4!
        self.assertIn('a0', selected)
        self.assertIn('b0', selected)
        self.assertIn('b1', selected)

    def test_source_choice_v3_single_point_inline_citations_and_strict_rejections(self):
        ev = [
            dict(chunk_id='chunk_11111111111111111111111111111111', paper_id='p1', title='G-Retriever',
                 page_start=4, page_end=4, quote='Soft prompt matrix [Pe; Xe] is processed by LLM layers [12]. ' * 20),
            dict(chunk_id='chunk_22222222222222222222222222222222', paper_id='p2', title='HippoRAG',
                 page_start=2, page_end=2, quote='HippoRAG executes Personalized PageRank over the KG index.'),
        ]
        # No separate citations array required in v3! Auto-derived and verbatim-checked from [E1:q2, E2:q1].
        good_v3 = dict(
            premise_check=[dict(premise='两者机制不同', supported=True, evidence_eids=['E1', 'E2'], note='分别使用软提示与PPR')],
            answer='原文采用 [Pe; Xe] 矩阵（见文献 [12]）[E1:q2]，并结合图上 PPR [E1:q1, E2:q1]。',
            status='ok',
        )
        ans, cites, status, checks = validate_answer_with_meta(json.dumps(good_v3, ensure_ascii=False), ev)
        self.assertEqual(status, 'ok')
        self.assertIn('[Pe; Xe]', ans)
        self.assertEqual(len(cites), 3)
        self.assertEqual([(c['eid'], c['quote_id']) for c in cites], [('E1', 'q2'), ('E1', 'q1'), ('E2', 'q1')])
        self.assertEqual(cites[0]['quote'], quote_options(ev[0]['quote'])[1]['quote'])
        self.assertEqual(checks[0]['supported'], True)

        # Refused without any inline citation is allowed.
        refused_v3 = dict(answer='现有原文没有提到该关系的依据。', status='refused')
        _, rcites, rstatus, _ = validate_answer_with_meta(json.dumps(refused_v3, ensure_ascii=False), ev)
        self.assertEqual(rstatus, 'refused')
        self.assertEqual(rcites, [])

        # Strict security rejections in v3: unknown E99, unknown q99, missing quote_id on bare [E1], non-refused 0 cite.
        for bad in (
            dict(answer='编造证据 [E99:q1]', status='ok'),
            dict(answer='编造片段 [E1:q99]', status='ok'),
            dict(answer='漏写quote_id [E1]', status='ok'),
            dict(answer='无引用回答', status='ok'),
            dict(answer='混杂括号 [E1:q1, 随便文字]', status='ok'),
        ):
            with self.assertRaises(ValueError):
                validate_answer_with_meta(json.dumps(bad, ensure_ascii=False), ev)

    def test_workflow_windowed_rerank_and_v3_citations_end_to_end(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        cfg = dict(NEO4J_URI='bolt://mock.invalid', NEO4J_USER='user', NEO4J_PASSWORD='dummy',
                   DEEPSEEK_BASE_URL='https://mock.invalid/v1', DEEPSEEK_API_KEY='test-secret', DEEPSEEK_MODEL='mock',
                   CLOUD_BGE_BASE_URL='', CLOUD_BGE_API_KEY='', CLOUD_BGE_MODEL='')
        long_text = ('Background intro filler sentence. ' * 25) + 'ToG-R specifically explores relation-based traversal.'
        chunk = dict(chunk_id='chunk_cccccccccccccccccccccccccccccccc', paper_id='p', parse_id='v',
                     title='ToG', section='3 Method', text_sha256='hash', text=long_text,
                     source_relative_path='a.pdf', source_spans=[{'pdf_page': 1}], page_start=1, page_end=1)
        seen_counts = []
        def fake_worker(r, c, mode, items, query=None, timeout=300):
            seen_counts.append(len(items))
            # Whole chunk gets low score 0.08, final window containing ToG-R gets high score 0.91!
            scores = [0.91 if 'ToG-R' in it['text'] and len(it['text']) < len(long_text) else 0.08 for it in items]
            return dict(outputs=scores, model_id='m', device='cuda', dtype='float16', batch_size=4, inference_seconds=0.05)
        def fake_http(request):
            body = dict(premise_check=[dict(premise='ToG-R存在', supported=True, evidence_eids=['E1'], note='有原文')],
                        answer='原文说明 ToG-R 基于关系遍历 [E1:q1]。', status='ok')
            return httpx.Response(200, json=dict(model='mock',
                choices=[{'message': {'content': json.dumps(body, ensure_ascii=False)}}],
                usage={'prompt_tokens': 100, 'completion_tokens': 30}))
        with patch('papertech.workflow.load_corpus', return_value=('corpus', [], [chunk])), \
             patch('papertech.workflow.vector_cache', return_value=({'model_id': 'model'}, {})), \
             patch('papertech.workflow.GraphStore'), \
             patch('papertech.workflow.run_worker', side_effect=fake_worker):
            w = Workflow(root, cfg, query_mode='cloud', rerank=True, graph_enabled=False,
                         rerank_windowed=True, reservation_policy='subquery_balanced',
                         citation_protocol='source-choice-v3', premise_check=True)
            self.addCleanup(w.close)
            w.store.retrieve.return_value = ([dict(chunk_id=chunk['chunk_id'], score=5.0)], [])
            w.providers.client.close()
            w.providers = Providers(cfg, w.audit, httpx.Client(transport=httpx.MockTransport(fake_http)), sleeper=lambda _: None)
            result = w.ask('ToG-R 的机制是什么？')
        self.assertEqual(result['status'], 'ok')
        self.assertGreater(seen_counts[0], 1)
        self.assertAlmostEqual(result['evidence'][0]['rerank_score'], 0.91)
        self.assertEqual(result['citations'][0]['eid'], 'E1')
        self.assertEqual(result['citations'][0]['quote_id'], 'q1')


if __name__ == '__main__':
    unittest.main()
