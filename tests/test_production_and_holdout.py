"""Unit tests for production defaults, fast-path planner, async trace flush, status recovery, and 18-case holdout."""
import json
from pathlib import Path
import tempfile
import unittest

from papertech.citations import validate_answer_with_meta
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark
from papertech.holdout_evaluation import _holdout_specs
from papertech.live_traces import LiveTraces
from papertech.providers import Providers
from papertech.workflow import Workflow, should_skip_planner

ROOT = Path(__file__).resolve().parents[1]


class TestProductionAndHoldout(unittest.TestCase):
    def setUp(self):
        self.ev = [dict(
            chunk_id='chunk_a1', title='HippoRAG', page_start=1, page_end=1,
            quote='HippoRAG uses Personalized PageRank over a schemaless KG constructed via OpenIE to retrieve multi-hop evidence.',
        )]

    def test_v3_missing_status_with_valid_inline_recovers_ok(self):
        raw = json.dumps({
            'premise_check': [{'premise': 'HippoRAG uses PPR', 'supported': True, 'evidence_eids': ['E1'], 'note': 'supported'}],
            'answer': 'HippoRAG 在无模式 KG 上运行 PPR 检索多跳证据 [E1:q1]。',
        }, ensure_ascii=False)
        ans, cites, status, checks = validate_answer_with_meta(raw, self.ev)
        self.assertEqual(status, 'ok')
        self.assertEqual(len(cites), 1)
        self.assertEqual(cites[0]['eid'], 'E1')
        self.assertEqual(len(checks), 1)

    def test_v3_empty_citations_list_and_underscore_note_tolerated(self):
        raw = json.dumps({
            'premise_check': [{'premise': 'HippoRAG uses PPR', 'supported': True, 'evidence_eids': ['E1'], 'note': 'ok'}],
            'status': 'ok',
            'answer': 'HippoRAG 在无模式 KG 上运行 PPR [E1:q1]。',
            'citations': [],
            '_note': 'benign model comment',
        }, ensure_ascii=False)
        ans, cites, status, _ = validate_answer_with_meta(raw, self.ev)
        self.assertEqual(status, 'ok')
        self.assertEqual(len(cites), 1)
        self.assertEqual(cites[0]['eid'], 'E1')

    def test_v3_missing_status_without_citations_or_refutation_still_fails(self):
        raw = json.dumps({'answer': '没有引用的回答。'}, ensure_ascii=False)
        with self.assertRaises(ValueError):
            validate_answer_with_meta(raw, self.ev)

    def test_legacy_v1_missing_status_still_fails(self):
        raw = json.dumps({
            'answer': '答案 [chunk_a1]。',
            'citations': [{'chunk_id': 'chunk_a1', 'quote_id': 'q1'}],
        }, ensure_ascii=False)
        with self.assertRaises(ValueError):
            validate_answer_with_meta(raw, self.ev)

    def test_status_field_precedes_answer_in_v3_prompt(self):
        captured = {}
        class DummyProviders(Providers):
            def __init__(self):
                self.cfg = {'DEEPSEEK_MODEL': 'test-model'}
            def post(self, request_id, provider, path, payload):
                captured['system'] = payload['messages'][0]['content']
                return {'choices': [{'message': {'content': '{}'}}]}, None
        p = DummyProviders()
        p.answer('r1', 'test?', self.ev, citation_protocol='source-choice-v3', premise_check=True)
        sys_prompt = captured['system']
        self.assertLess(sys_prompt.index('"status":'), sys_prompt.index('"answer":'))

    def test_should_skip_planner_fast_path(self):
        self.assertTrue(should_skip_planner('HippoRAG 如何使用 PPR 检索证据？'))
        self.assertTrue(should_skip_planner('G-Retriever 的 PCST 优化问题是什么？'))
        # Complex / multi-paper / false-premise / multi-question queries MUST NOT skip planner
        self.assertFalse(should_skip_planner('比较 HippoRAG 与 RoG 的检索机制'))
        self.assertFalse(should_skip_planner('HippoRAG 在 MuSiQue 上微调了 GPT-3.5，对吗？'))
        self.assertFalse(should_skip_planner('STaRK 覆盖哪三个领域？对 LLM Reranker 用什么 k？'))
        self.assertFalse(should_skip_planner('什么是知识图谱增强检索？'))

    def test_live_traces_defer_flush_does_not_flush_inline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            called = []
            class FakeClient:
                def create_run(self, **kw): called.append(('create', kw['id']))
                def update_run(self, **kw): called.append(('update', kw['run_id']))
                def close(self): pass
            lt = LiveTraces(root, cfg={'LANGSMITH_API_KEY': 'fake'}, client=FakeClient(), defer_flush=True)
            sid = lt.start('test_span', {'request_id': 'r1'})
            lt.end(sid, {'status': 'ok'})
            self.assertEqual(called, [])
            res = lt.flush()
            self.assertEqual(res['uploaded'], 2)
            self.assertEqual(len(called), 2)
            lt.close()

    def test_workbench_factory_defaults_offline_safe(self):
        wf = Workflow.for_workbench(ROOT, {}, backend='offline', query_mode='none', rerank=False)
        try:
            self.assertEqual(wf.reservation_policy, 'subquery_balanced')
            self.assertEqual(wf.citation_protocol, 'source-choice-v3')
            self.assertTrue(wf.query_planner_enabled)
            self.assertTrue(wf.premise_check_enabled)
            self.assertTrue(wf.planner_fast_path)
            self.assertTrue(wf.async_trace_flush)
            self.assertEqual(wf.evidence_budget, 18000)
            self.assertEqual(wf.evidence_max, 12)
        finally:
            wf.close()

    def test_holdout_benchmark_specs_integrity(self):
        _, _, chunks = load_corpus(ROOT)
        cmap = {c['chunk_id']: c for c in chunks}
        v4, _, _ = load_benchmark(ROOT, 'benchmark-v4')
        v4_q = {c['question'].strip() for c in v4['cases']}
        cases, units = _holdout_specs()
        self.assertEqual(len(cases), 18)
        self.assertEqual(sum(1 for c in cases if c['category'] == 'fact'), 6)
        self.assertEqual(sum(1 for c in cases if c['category'] == 'cross'), 8)
        self.assertEqual(sum(1 for c in cases if c['category'] == 'negative'), 4)
        papers = set()
        for uid, u in units.items():
            self.assertIn(u['primary_chunk'], cmap, uid)
            for cid in u['known_support_chunks']:
                self.assertIn(cid, cmap, (uid, cid))
                papers.add(cmap[cid]['title'])
        self.assertEqual(len(papers), 14)
        for c in cases:
            self.assertNotIn(c['question'].strip(), v4_q, c['id'])


if __name__ == '__main__':
    unittest.main()
