"""Question-only decomposition: ownership, alias boundaries and audit offsets."""
import unittest

from papertech.entity_aliases import method_spans, subqueries


class SubqueryTests(unittest.TestCase):
    def assert_roundtrip(self, question, rows):
        for row in rows:
            for span in row['source_spans']:
                self.assertEqual(question[span['start']:span['end']], span['text'])
            self.assertEqual(row['text'], ' '.join(s['text'] for s in row['source_spans']))

    def test_explicit_descriptors_share_only_question_text(self):
        q = 'HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？'
        rows = subqueries(q)
        self.assertEqual([r['text'] for r in rows], [
            'HippoRAG 的节点 specificity 分别改变了什么？',
            'G-Retriever 的节点/边奖励 分别改变了什么？',
            'KG-GPT 的 top-k 参数 分别改变了什么？'])
        self.assertTrue(all(r['subquery_source'] == 'span' for r in rows))
        self.assert_roundtrip(q, rows)

    def test_coordinated_methods_do_not_inherit_unassigned_details(self):
        q = 'MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。'
        rows = subqueries(q)
        self.assertEqual([r['text'] for r in rows], ['MindMap', 'G-Retriever'])
        self.assertTrue(all(r['subquery_source'] == 'method_only' for r in rows))
        self.assert_roundtrip(q, rows)

    def test_missing_one_descriptor_falls_back_symmetrically(self):
        rows = subqueries('LPKG 的测试集与 STaRK 各想补足什么缺口？')
        self.assertEqual([r['text'] for r in rows], ['LPKG', 'STaRK'])

    def test_no_anchor_single_method_and_same_paper_keep_original_path(self):
        for q in ('请比较两种图索引。', 'HippoRAG 如何检索？', 'ToG 与 ToG-R 的区别？',
                  'RoG 与 Reasoning on Graphs 的训练？'):
            with self.subTest(question=q):
                self.assertEqual(subqueries(q), [])

    def test_tog_variants_and_identifier_boundaries(self):
        q = 'myRoGModel、ToG-2、ToG-R、ToG 与 Think-on-Graph 2.0'
        self.assertEqual([m['method'] for m in method_spans(q)],
                         ['ToG-2', 'ToG-R', 'ToG', 'ToG-2'])

    def test_unicode_alias_offsets_and_multiple_spaces(self):
        q = 'Ｇ–Ｒｅｔｒｉｅｖｅｒ 的编码与 Think-on-Graph   2.0 的搜索分别改变什么？'
        rows = subqueries(q)
        self.assertEqual([r['method'] for r in rows], ['G-Retriever', 'ToG-2'])
        self.assert_roundtrip(q, rows)

    def test_repeated_alias_not_duplicate_query(self):
        q = 'KGP 与 CuriousLLM 如何比较？KGP 为什么需要原文？'
        rows = subqueries(q)
        self.assertEqual([r['method'] for r in rows], ['KGP', 'CuriousLLM'])

    def test_shared_pronouns_are_not_attached_to_each_method(self):
        q = 'HippoRAG 的权重与 KG-GPT 的参数分别说明两者为什么不同？'
        rows = subqueries(q)
        self.assertTrue(all(len(r['source_spans']) == 1 for r in rows))
        self.assertNotIn('两者', ' '.join(r['text'] for r in rows))

    def test_conjunction_and_task_characters_inside_descriptor_survive(self):
        q = 'KGP 的各种参与、RoG 的各向异性分别指什么？'
        rows = subqueries(q)
        self.assertIn('各种参与', rows[0]['text'])
        self.assertIn('各向异性', rows[1]['text'])
        self.assert_roundtrip(q, rows)

    def test_reordered_methods_keep_question_order(self):
        q = 'KG-GPT 的参数与 HippoRAG 的权重分别改变了什么？'
        self.assertEqual([r['method'] for r in subqueries(q)], ['KG-GPT', 'HippoRAG'])


if __name__ == '__main__':
    unittest.main()
