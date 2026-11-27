"""Unit tests for P0 optimizations: contextual rerank, budgeted round-robin selection, and v2 citations."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx

from papertech.citations import prompt_evidence, quote_options, validate_answer
from papertech.corpus import load_corpus
from papertech.entity_aliases import GROUPS
from papertech.evidence_context import assemble
from papertech.providers import Providers
from papertech.retrieval import contextual_text, rerank_view, select_evidence
from papertech.workflow import Workflow

ROOT = Path(__file__).resolve().parents[1]


class P0OptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, chunks = load_corpus(ROOT)
        cls.chunks = {c['chunk_id']: c for c in chunks}

    def test_contextual_rerank_view_adds_title_and_section_without_mutating_chunk(self):
        original = dict(chunk_id='c1', title='LPKG: Learning to Plan', section='3 Methodology',
                        text='Our planner decomposes multi-hop queries.')
        view = rerank_view(original, contextual=True)
        self.assertEqual(view['text'], 'Title: LPKG: Learning to Plan\nSection: 3 Methodology\n\nOur planner decomposes multi-hop queries.')
        self.assertEqual(original['text'], 'Our planner decomposes multi-hop queries.')
        self.assertEqual(rerank_view(original, contextual=False)['text'], original['text'])
        self.assertEqual(contextual_text(dict(text='plain only')), 'plain only')

    def test_round_robin_keeps_top_long_chunk_instead_of_demoting_to_short_chunk(self):
        chunks = {}
        for group in GROUPS:
            if group['names'][0] in ('LPKG', 'RoG'):
                name = group['names'][0]
                chunks[group['source_chunk']] = dict(self.chunks[group['source_chunk']], paper_id=name)
        def add(cid, paper, words):
            chunks[cid] = dict(chunk_id=cid, paper_id=paper, parse_id='v', title=paper, section='Method',
                page_start=1, page_end=1, source_spans=[{}], source_relative_path='p.pdf',
                text=('Detailed conclusion about planning training data. ' * words))
        add('lpkg_long_best', 'LPKG', 60)
        add('lpkg_short_second', 'LPKG', 10)
        add('rog_best', 'RoG', 50)
        ranked = [
            dict(chunk_id='lpkg_long_best', sources=[], rerank_score=0.92),
            dict(chunk_id='lpkg_short_second', sources=[], rerank_score=0.55),
            dict(chunk_id='rog_best', sources=[], rerank_score=0.88),
        ]
        evidence, _, detail = assemble(ranked, chunks, [], 'LPKG和RoG的规划训练有何区别？',
            budget=18000, evidence_max=12, score_policy='relative', reservation_policy='round_robin')
        selected_ids = [e['chunk_id'] for e in evidence]
        self.assertIn('lpkg_long_best', selected_ids)
        self.assertIn('rog_best', selected_ids)
        self.assertEqual(detail['missing_comparison_groups'], [])
        self.assertEqual(detail['score_policy'], 'relative')
        self.assertEqual(detail['reservation_policy'], 'round_robin')

    def test_relative_threshold_rescues_reserved_cross_paper_source_and_filters_noise(self):
        chunks = {}
        for group in GROUPS:
            if group['names'][0] in ('HippoRAG', 'RoG'):
                name = group['names'][0]
                chunks[group['source_chunk']] = dict(self.chunks[group['source_chunk']], paper_id=name)
        for cid, paper in (('h1', 'HippoRAG'), ('r1', 'RoG'), ('n1', 'Other'), ('n2', 'Other')):
            chunks[cid] = dict(chunk_id=cid, paper_id=paper, parse_id='v', title=paper, section='Experiments',
                page_start=1, page_end=1, source_spans=[{}], source_relative_path='p.pdf',
                text='Source evidence supports this specific experiment setting.')
        ranked = [
            dict(chunk_id='h1', sources=[], rerank_score=0.90),
            dict(chunk_id='r1', sources=[], rerank_score=0.03),   # reserved named paper above 0.01 floor
            dict(chunk_id='n1', sources=[], rerank_score=0.08),   # below 0.15 * 0.90 = 0.135
            dict(chunk_id='n2', sources=[], rerank_score=0.005),  # below 0.01 hard floor
        ]
        evidence, _, detail = assemble(ranked, chunks, [], '比较HippoRAG和RoG',
            budget=18000, evidence_max=12, score_policy='relative', reservation_policy='round_robin')
        ids = {e['chunk_id'] for e in evidence}
        self.assertEqual(ids, {'h1', 'r1'})
        r1 = next(e for e in evidence if e['chunk_id'] == 'r1')
        self.assertTrue(r1.get('low_score_reserved'))
        self.assertEqual(detail['missing_comparison_groups'], [])
        # Pure noise below 0.01 floor still returns empty to enable refusal.
        empty, _ = select_evidence([dict(chunk_id='n2', sources=[], rerank_score=0.005)],
            chunks, budget=18000, evidence_max=12, score_policy='relative')
        self.assertEqual(empty, [])

    def test_citation_v2_short_ids_combined_and_ignores_math_or_paper_brackets(self):
        ev = [
            dict(chunk_id='chunk_11111111111111111111111111111111', paper_id='p1', title='G-Retriever',
                 page_start=4, page_end=4, quote='Soft prompt matrix [Pe; Xe] is processed by self-attention layers [12].'),
            dict(chunk_id='chunk_22222222222222222222222222222222', paper_id='p2', title='HippoRAG',
                 page_start=2, page_end=2, quote='HippoRAG runs Personalized PageRank over the KG index.'),
        ]
        self.assertEqual(prompt_evidence(ev[0], eid='E1')['eid'], 'E1')
        self.assertNotIn('chunk_id', prompt_evidence(ev[0], eid='E1'))
        good = dict(
            answer='原文采用 [Pe; Xe] 拼接软提示（见原文 [12]）[E1]，而另一方法使用 PPR [E1, E2] [注]。',
            citations=[dict(eid='E1', quote_id='q1'), dict(eid='E2', quote_id='q1')],
            status='ok',
        )
        answer, citations, status = validate_answer(json.dumps(good, ensure_ascii=False), ev)
        self.assertEqual(status, 'ok')
        self.assertIn('[Pe; Xe]', answer)
        self.assertEqual([c['chunk_id'] for c in citations], [ev[0]['chunk_id'], ev[1]['chunk_id']])
        self.assertEqual([c['eid'] for c in citations], ['E1', 'E2'])
        self.assertEqual(citations[0]['quote'], quote_options(ev[0]['quote'])[0]['quote'])

        # Unknown E99, unknown chunk_fake, mixed malformed bracket, and missing declaration must all fail.
        for bad in (
            dict(good, answer='编造编号 [E99]', citations=[dict(eid='E1', quote_id='q1')]),
            dict(good, answer='编造块 [chunk_fake]', citations=[dict(eid='E1', quote_id='q1')]),
            dict(good, answer='混杂括号 [E1, 非法文本]', citations=[dict(eid='E1', quote_id='q1')]),
            dict(good, answer='漏声明 [E1] 和 [E2]', citations=[dict(eid='E1', quote_id='q1')]),
            dict(good, citations=[dict(eid='E1', quote_id='q99'), dict(eid='E2', quote_id='q1')]),
        ):
            with self.assertRaises(Exception):
                validate_answer(json.dumps(bad, ensure_ascii=False), ev)

    def test_workflow_p0_defaults_send_contextual_rerank_and_v2_citations(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        cfg = dict(NEO4J_URI='bolt://mock.invalid', NEO4J_USER='user', NEO4J_PASSWORD='dummy',
                   DEEPSEEK_BASE_URL='https://mock.invalid/v1', DEEPSEEK_API_KEY='test-secret', DEEPSEEK_MODEL='mock',
                   CLOUD_BGE_BASE_URL='', CLOUD_BGE_API_KEY='', CLOUD_BGE_MODEL='')
        chunk = dict(chunk_id='chunk_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', paper_id='p', parse_id='v',
                     title='HippoRAG', section='3 Method', text_sha256='hash',
                     text='Our method uses Personalized PageRank over KG nodes.', source_relative_path='a.pdf',
                     source_spans=[{'pdf_page': 1}], page_start=1, page_end=1)
        received_rerank = []
        received_prompt = []
        def fake_worker(r, c, mode, items, query=None, timeout=300):
            received_rerank.append((mode, items, query))
            return dict(outputs=[0.85], model_id='m', device='cuda', dtype='float16', batch_size=4)
        def fake_http(request):
            received_prompt.append(json.loads(request.content))
            body = dict(answer='该方法在图节点上运行 PPR（矩阵 [A; B]）[E1]。',
                        citations=[dict(eid='E1', quote_id='q1')], status='ok')
            return httpx.Response(200, json=dict(model='mock',
                choices=[{'message': {'content': json.dumps(body, ensure_ascii=False)}}],
                usage={'prompt_tokens': 120, 'completion_tokens': 25}))
        with patch('papertech.workflow.load_corpus', return_value=('corpus', [], [chunk])), \
             patch('papertech.workflow.vector_cache', return_value=({'model_id': 'model'}, {})), \
             patch('papertech.workflow.GraphStore'), \
             patch('papertech.workflow.run_worker', side_effect=fake_worker):
            w = Workflow(root, cfg, query_mode='cloud', rerank=True, graph_enabled=False)
            self.addCleanup(w.close)
            w.store.retrieve.return_value = ([dict(chunk_id=chunk['chunk_id'], score=5.0)], [])
            w.providers.client.close()
            w.providers = Providers(cfg, w.audit, httpx.Client(transport=httpx.MockTransport(fake_http)), sleeper=lambda _: None)
            result = w.ask('HippoRAG 如何检索？')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['citations'][0]['chunk_id'], chunk['chunk_id'])
        self.assertEqual(result['citations'][0]['eid'], 'E1')
        self.assertTrue(received_rerank[0][1][0]['text'].startswith('Title: HippoRAG\nSection: 3 Method\n\n'))
        self.assertEqual(chunk['text'], 'Our method uses Personalized PageRank over KG nodes.')
        self.assertEqual(result['retrieval_summary']['reranker']['contextual_input'], 'title+section+text')
        self.assertEqual(result['retrieval_summary']['reranker']['batch_size'], 4)
        user_payload = json.loads(received_prompt[0]['messages'][1]['content'])
        self.assertEqual(user_payload['evidence'][0]['eid'], 'E1')
        self.assertNotIn('chunk_id', user_payload['evidence'][0])


if __name__ == '__main__':
    unittest.main()
