import unittest
from papertech.evaluation import support_metrics,linear_quantile,criterion_source_coverage


class EvaluationTests(unittest.TestCase):
    def test_criterion_needs_all_sources_and_never_assigns_semantic_score(self):
        case = dict(assessment=dict(criteria=[dict(id='R01.C01', requirement='compare both', unit_ids=['a','b']),
            dict(id='N06.C01', requirement='refuse unsupported claim', unit_ids=[])]))
        units = {'a': dict(known_support_chunks=['a1','a2']), 'b': dict(known_support_chunks=['b1'])}
        partial = criterion_source_coverage(case, ['a2'], units)
        self.assertFalse(partial[0]['required_sources_available'])
        self.assertEqual(partial[0]['missing_units'], ['b'])
        self.assertIsNone(partial[0]['semantic_score'])
        self.assertIsNone(partial[1]['required_sources_available'])
        self.assertTrue(criterion_source_coverage(case, ['a2','b1'], units)[0]['required_sources_available'])

    def test_alternatives_do_not_count_as_extra_required_facts(self):
        units=[dict(known_support_chunks=['a','alternate']),dict(known_support_chunks=['b'])]
        m=support_metrics(['other','alternate','b'],['alternate'],units)
        self.assertEqual(m['recall5'],1)
        self.assertEqual(m['evidence_coverage'],.5)
        self.assertEqual(m['mrr40'],.5)
        self.assertFalse(m['all_units'])

    def test_empty_or_unjudged_negatives_do_not_become_perfect_recall(self):
        self.assertIsNone(support_metrics([],[],[])['recall5'])
        self.assertEqual(support_metrics([],[],[dict(known_support_chunks=['a'])])['recall5'],0)

    def test_topk_does_not_include_sixth_candidate(self):
        m=support_metrics(['1','2','3','4','5','gold'],[],[dict(known_support_chunks=['gold'])])
        self.assertEqual(m['recall5'],0)
        self.assertEqual(m['recall8'],1)

    def test_quantile_has_explicit_linear_interpolation(self):
        self.assertAlmostEqual(linear_quantile([1,2,3,4],.95),3.85)
        self.assertIsNone(linear_quantile([],.95))
