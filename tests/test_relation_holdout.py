import unittest
from unittest.mock import Mock

from papertech.relation_holdout_evaluation import RetrievalWorkflow
from papertech.relation_holdout_report import paired_statistics


class HoldoutContractTests(unittest.TestCase):
    def test_graph_only_has_no_text_or_vector_dependency(self):
        workflow = object.__new__(RetrievalWorkflow)
        workflow.graph_expander = Mock()
        workflow.graph_expander.expand_graph.return_value = [dict(evidence=[dict(chunk_id='source')])]
        workflow.graph_expander.last_graph_audit = dict(seed_count=1)
        workflow.chunk_map = {'source': {}}
        workflow.corpus_id = 'frozen'
        workflow.audit = Mock()
        workflow.store = Mock()
        workflow.store.retrieve.side_effect = AssertionError('text retrieval forbidden')
        result = workflow.produce('question only', 'Graph-only', None, 'test')
        workflow.graph_expander.expand_graph.assert_called_once_with([], question='question only',
            max_paths=40, max_seed_entities=40, per_node=8)
        workflow.store.retrieve.assert_not_called()
        self.assertEqual(set(result['candidate_channels']), {'graph'})
        self.assertFalse(result['retrieval_summary']['query_embedding_used'])

    def test_dense_arm_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'excluded_arm'):
            object.__new__(RetrievalWorkflow).produce('q', 'Dense-only', None, 'test')

    def test_paired_bootstrap_aligns_case_ids_and_excludes_other_cases(self):
        def row(cid, arm, score):
            return dict(case_id=cid, arm=arm, metrics=dict(evidence_coverage=score))
        rows = [row('b','Hybrid',1),row('a','Graph-only',1),row('outside','Graph-only',0),
            row('b','Graph-only',0),row('a','Hybrid',0),row('incomplete','Hybrid',1)]
        result = paired_statistics(rows, ['a','b','incomplete'], resamples=1000)
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['mean_delta'], 0)
        self.assertEqual((result['graph_wins'], result['hybrid_wins']), (1,1))
        self.assertEqual(result['ci95'], [-1,1])


if __name__ == '__main__':
    unittest.main()
