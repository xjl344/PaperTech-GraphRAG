"""Unit tests for Phase-2 cloud Query Planner, owner reranking, subquery reservation, and premise_check."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx

from papertech.citations import validate_answer_with_meta
from papertech.evidence_context import assemble
from papertech.providers import Providers
from papertech.query_planner import build_fulltext_query, merge_multi_query_candidates, validate_plan
from papertech.workflow import Workflow

ROOT = Path(__file__).resolve().parents[1]


class P2QueryPlannerTests(unittest.TestCase):
    def test_validate_plan_accepts_split_and_rejects_invented_corpus_method(self):
        question = 'Tree-of-Traversals 的停止条件与 CuriousLLM 的追问停止机制有何不同？'
        good = dict(
            decision='split',
            reason='两个独立方法的停止机制',
            english_keywords=['Tree-of-Traversals', 'CuriousLLM', 'stopping criteria'],
            subqueries=[
                dict(id='SQ01', text='Tree-of-Traversals 的停止条件', english_keywords=['Tree-of-Traversals', 'termination']),
                dict(id='SQ02', text='CuriousLLM 的追问停止机制', english_keywords=['CuriousLLM', 'follow-up', 'stop']),
            ],
            quotes=['Tree-of-Traversals 的停止条件', 'CuriousLLM 的追问停止机制'],
        )
        plan = validate_plan(question, good)
        self.assertEqual(plan['decision'], 'split')
        self.assertEqual(len(plan['subqueries']), 2)
        self.assertEqual(build_fulltext_query('停止条件是什么？', ['stopping criteria', 'max depth']), 'stopping criteria max depth')

        bad_invented = dict(good, subqueries=[
            dict(id='SQ01', text='Tree-of-Traversals 的停止条件', english_keywords=['Tree-of-Traversals']),
            dict(id='SQ02', text='HippoRAG 的检索方式', english_keywords=['HippoRAG']),
        ])
        with self.assertRaisesRegex(ValueError, 'planner_invented_method'):
            validate_plan(question, bad_invented)

    def test_citation_accepts_r15_quote_qualifier_and_premise_check(self):
        ev = [
            dict(chunk_id='chunk_11111111111111111111111111111111', paper_id='p1', title='Tree-of-Traversals',
                 page_start=2, page_end=2, quote='Tree search stops when node value exceeds threshold tau.'),
            dict(chunk_id='chunk_22222222222222222222222222222222', paper_id='p2', title='CuriousLLM',
                 page_start=3, page_end=3, quote='CuriousLLM outputs a special token when evidence is sufficient.'),
        ]
        # R15 style inline [E1, q1] qualifier must pass while [E99, q1] must fail.
        body = dict(
            premise_check=[dict(premise='两者终止条件相同', supported=False, evidence_eids=['E1', 'E2'], note='原文机制不同')],
            answer='前者依赖阈值 [E1, q1]，后者依赖特殊 token [E2, q1]。',
            citations=[dict(eid='E1', quote_id='q1'), dict(eid='E2', quote_id='q1')],
            status='refused',
        )
        answer, citations, status, checks = validate_answer_with_meta(json.dumps(body, ensure_ascii=False), ev)
        self.assertEqual(status, 'refused')
        self.assertEqual(len(citations), 2)
        self.assertEqual(checks[0]['supported'], False)
        bad = dict(body, answer='非法编号 [E99, q1]')
        with self.assertRaises(ValueError):
            validate_answer_with_meta(json.dumps(bad, ensure_ascii=False), ev)

    def test_multi_query_merge_and_subquery_reservation(self):
        hits = [
            dict(id='Q00', channels=dict(fulltext=[dict(chunk_id='c0', score=9)], dense=[dict(chunk_id='c1', score=.9)])),
            dict(id='SQ01', channels=dict(fulltext=[dict(chunk_id='c2', score=8)], dense=[])),
            dict(id='SQ02', channels=dict(fulltext=[], dense=[dict(chunk_id='c3', score=.85)])),
        ]
        merged = merge_multi_query_candidates(hits, per_channel_quota=8, cap=64)
        by_id = {x['chunk_id']: x for x in merged}
        self.assertEqual(by_id['c2']['found_by'], ['SQ01'])
        self.assertEqual(by_id['c3']['found_by'], ['SQ02'])

        chunks = {f'c{i}': dict(chunk_id=f'c{i}', paper_id=f'p{i}', parse_id='v', title=f'Paper {i}', section='Method',
                  page_start=1, page_end=1, source_spans=[{}], source_relative_path='p.pdf',
                  text=f'Evidence block {i} describes mechanism details.') for i in range(4)}
        ranked = [
            dict(chunk_id='c0', sources=[], found_by=['Q00'], best_query_id='Q00', rerank_score=0.90),
            dict(chunk_id='c1', sources=[], found_by=['Q00'], best_query_id='Q00', rerank_score=0.85),
            dict(chunk_id='c2', sources=[], found_by=['SQ01'], best_query_id='SQ01', rerank_score=0.40),
            dict(chunk_id='c3', sources=[], found_by=['SQ02'], best_query_id='SQ02', rerank_score=0.04),
        ]
        ev, _, _ = assemble(ranked, chunks, [], '抽象跨主题问题', budget=18000, evidence_max=12,
                            score_policy='relative', reservation_policy='round_robin', subquery_ids=['SQ01', 'SQ02'])
        self.assertTrue({'c0', 'c2', 'c3'}.issubset({e['chunk_id'] for e in ev}))

    def test_workflow_cloud_planner_batch_embedding_owner_rerank_and_premise_check(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        cfg = dict(NEO4J_URI='bolt://mock.invalid', NEO4J_USER='user', NEO4J_PASSWORD='dummy',
                   DEEPSEEK_BASE_URL='https://mock.invalid/v1', DEEPSEEK_API_KEY='test-secret', DEEPSEEK_MODEL='mock',
                   CLOUD_BGE_PROVIDER='cloudflare', CLOUDFLARE_ACCOUNT_ID='a' * 32, CLOUDFLARE_AUTH_TOKEN='tok',
                   CLOUD_BGE_MODEL='@cf/baai/bge-m3')
        c1 = dict(chunk_id='chunk_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', paper_id='p1', parse_id='v',
                  title='Tree-of-Traversals', section='3 Method', text_sha256='h1',
                  text='Tree-of-Traversals stops when tau threshold is exceeded.', source_relative_path='a.pdf',
                  source_spans=[{'pdf_page': 2}], page_start=2, page_end=2)
        c2 = dict(chunk_id='chunk_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', paper_id='p2', parse_id='v',
                  title='CuriousLLM', section='3 Method', text_sha256='h2',
                  text='CuriousLLM uses a special token NA for sufficient evidence.', source_relative_path='b.pdf',
                  source_spans=[{'pdf_page': 3}], page_start=3, page_end=3)
        rerank_queries = []
        http_calls = []
        def fake_worker(r, c, mode, items, query=None, timeout=300):
            rerank_queries.append((query, [x['chunk_id'] for x in items]))
            return dict(outputs=[0.88] * len(items), model_id='m', device='cuda', dtype='float16', batch_size=4, inference_seconds=0.1)
        def fake_http(request):
            payload = json.loads(request.content)
            http_calls.append((str(request.url), payload))
            if '/ai/run/' in str(request.url):
                n = len(payload['text'])
                return httpx.Response(200, json=dict(success=True, result=dict(shape=[n, 1024], data=[[0.1] * 1024 for _ in range(n)])))
            sys_msg = payload['messages'][0]['content']
            if '查询规划器' in sys_msg:
                plan = dict(decision='split', reason='两方法比较', english_keywords=['Tree-of-Traversals', 'CuriousLLM'],
                            subqueries=[
                                dict(id='SQ01', text='Tree-of-Traversals 停止条件', english_keywords=['Tree-of-Traversals', 'stop']),
                                dict(id='SQ02', text='CuriousLLM 充分证据信号', english_keywords=['CuriousLLM', 'sufficient']),
                            ], quotes=['Tree-of-Traversals', 'CuriousLLM'])
                return httpx.Response(200, json=dict(model='mock', choices=[{'message': {'content': json.dumps(plan, ensure_ascii=False)}}],
                                                     usage={'prompt_tokens': 80, 'completion_tokens': 40}))
            ans = dict(premise_check=[dict(premise='两者机制相同', supported=False, evidence_eids=['E1', 'E2'], note='不同')],
                       answer='两者停止机制不同：前者用阈值 [E1]，后者用 NA token [E2]。',
                       citations=[dict(eid='E1', quote_id='q1'), dict(eid='E2', quote_id='q1')], status='refused')
            return httpx.Response(200, json=dict(model='mock', choices=[{'message': {'content': json.dumps(ans, ensure_ascii=False)}}],
                                                 usage={'prompt_tokens': 150, 'completion_tokens': 50}))
        def fake_retrieve(q, vec, *, fulltext_query=None):
            if 'Tree-of-Traversals' in (fulltext_query or q):
                return ([dict(chunk_id=c1['chunk_id'], score=5.0)], [])
            return ([dict(chunk_id=c2['chunk_id'], score=5.0)], [])
        with patch('papertech.workflow.load_corpus', return_value=('corpus', [], [c1, c2])), \
             patch('papertech.workflow.vector_cache', return_value=({'model_id': 'model'}, {})), \
             patch('papertech.workflow.GraphStore'), \
             patch('papertech.workflow.compatible', return_value=True), \
             patch('papertech.workflow.run_worker', side_effect=fake_worker):
            w = Workflow(root, cfg, query_mode='cloud', rerank=True, graph_enabled=False,
                         query_planner=True, premise_check=True)
            self.addCleanup(w.close)
            w.store.retrieve.side_effect = fake_retrieve
            w.providers.client.close()
            w.providers = Providers(cfg, w.audit, httpx.Client(transport=httpx.MockTransport(fake_http)), sleeper=lambda _: None)
            result = w.ask('Tree-of-Traversals 与 CuriousLLM 停止条件是否相同？')
        self.assertEqual(result['status'], 'refused')
        self.assertEqual(result['premise_check'][0]['supported'], False)
        self.assertEqual(result['retrieval_summary']['query_plan']['decision'], 'split')
        self.assertEqual(result['retrieval_summary']['reranker']['rerank_mode'], 'owner_subquery')
        # Single Cloudflare embedding batch for Q00 + SQ01 + SQ02!
        embed_calls = [p for u, p in http_calls if '/ai/run/' in u]
        self.assertEqual(len(embed_calls), 1)
        self.assertEqual(len(embed_calls[0]['text']), 3)
        # Owner reranker called per subquery!
        self.assertEqual(len(rerank_queries), 2)


if __name__ == '__main__':
    unittest.main()
