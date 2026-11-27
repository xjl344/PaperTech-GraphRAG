"""Test causal isolation and post-hoc source attribution, without services."""
from copy import deepcopy
from types import SimpleNamespace
import unittest

from papertech.graph_store import GraphStore
from papertech.retrieval_comparison import RetrievalWorkflow, diagnose, aggregate


class RetrievalComparisonTests(unittest.TestCase):
    def workflow(self):
        workflow = RetrievalWorkflow.__new__(RetrievalWorkflow)
        workflow.corpus_id = 'corpus'
        workflow.chunk_map = {f'c{i}': {} for i in range(60)}
        workflow.audit = SimpleNamespace(record_candidates=lambda *a: None)
        return workflow

    def test_dense_never_queries_graph_and_disables_fulltext(self):
        workflow = self.workflow()
        calls = []
        def retrieve(*a, **kw):
            calls.append((a, kw))
            return [], [dict(chunk_id=f'c{i}', score=1 / (i + 1)) for i in range(40)]
        workflow.store = SimpleNamespace(retrieve=retrieve)
        workflow.graph_expander = SimpleNamespace(expand_graph=lambda *a, **kw: self.fail('graph accessed'))
        result = workflow.produce('question', 'Dense-only', [1.0], 'r')
        self.assertEqual(len(result['ranked']), 40)
        self.assertEqual(set(result['candidate_channels']), {'dense'})
        self.assertEqual(calls[0][1], dict(fulltext_enabled=False, dense_top=40))

    def test_graph_has_no_text_seeds_and_never_calls_text_store(self):
        workflow = self.workflow()
        calls = []
        def expand(seeds, **kw):
            calls.append(seeds)
            return [dict(evidence=[dict(chunk_id='c1')])]
        workflow.graph_expander = SimpleNamespace(expand_graph=expand, last_graph_audit=dict(seed_count=1))
        workflow.store = SimpleNamespace(retrieve=lambda *a, **kw: self.fail('text store accessed'))
        result = workflow.produce('question', 'Graph-only', None, 'r')
        self.assertEqual(calls, [[]])
        self.assertEqual(set(result['candidate_channels']), {'graph'})
        self.assertFalse(result['retrieval_summary']['query_embedding_used'])

    def test_no_anchor_does_not_fallback(self):
        workflow = self.workflow()
        workflow.graph_expander = SimpleNamespace(expand_graph=lambda *a, **kw: [], last_graph_audit=dict(seed_count=0))
        workflow.store = SimpleNamespace(retrieve=lambda *a, **kw: self.fail('fallback'))
        self.assertEqual(workflow.produce('unknown', 'Graph-only', None, 'r')['ranked'], [])

    def test_hybrid_uses_both_channels_with_total_cap(self):
        workflow = self.workflow()
        workflow.store = SimpleNamespace(retrieve=lambda *a, **kw: (
            [dict(chunk_id=f'c{i}', score=1.0) for i in range(20)],
            [dict(chunk_id=f'c{i}', score=.5) for i in range(20, 40)]))
        result = workflow.produce('question', 'Hybrid', [1.0], 'r')
        self.assertEqual(len(result['ranked']), 40)
        self.assertEqual(set(result['candidate_channels']), {'fulltext', 'dense'})

    def test_dense_store_does_not_execute_lucene(self):
        store = GraphStore.__new__(GraphStore)
        store.corpus_id, store.model_id = 'corpus', 'm'
        statements = []
        def execute(query, **kw):
            statements.append(query)
            if 'MATCH (v:Corpus' in query:
                return [dict(status='ready', model_id='m')]
            return []
        store.execute = execute
        store.retrieve('question', [1.0], fulltext_enabled=False, dense_top=40)
        self.assertFalse(any('fulltext.queryNodes' in q for q in statements))
        self.assertTrue(any('vector.queryNodes' in q for q in statements))

    def test_failure_attribution_separates_retrieval_threshold_and_selection(self):
        bench = dict(units={'u': dict(known_support_chunks=['c'], answer_point='fact')})
        case = dict(units=['u'])
        chunks = {'c': dict(text='source', page_start=1, source_spans=[1])}
        row = dict(arm='Dense-only', status='evidence_only', ranked=[], evidence=[], graph_paths=[], retrieval_summary={})
        def reason(r):
            return diagnose(r, case, bench, chunks, None)['facts'][0]['reason']
        self.assertEqual(reason(row), 'retrieval_pool_miss')
        row['ranked'] = [dict(chunk_id='c', rerank_score=.01)]
        self.assertEqual(reason(row), 'reranker_threshold')
        row['ranked'][0]['rerank_score'] = .8
        self.assertEqual(reason(row), 'context_selection')
        row['evidence'] = [dict(chunk_id='c')]
        self.assertEqual(reason(row), 'covered')


if __name__ == '__main__':
    unittest.main()
