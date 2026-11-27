import unittest

from papertech.subquery_rerank_clean_diagnostic import clean_text


class CleanSubqueryTests(unittest.TestCase):
    def test_removes_only_shared_scaffolding(self):
        result = clean_text('KG-GPT 的 top-k 参数 分别改变了什么？')
        self.assertEqual(result['cleaned'], 'KG-GPT 的 top-k 参数 改变了什么？')
        self.assertEqual(result['removed'], ['分别'])
        self.assertIn('什么', result['cleaned'])

    def test_removes_each_marker_without_rewriting_method_or_topic(self):
        result = clean_text('ToG 的束搜索 各保留什么选择机会？')
        self.assertEqual(result['cleaned'], 'ToG 的束搜索 保留什么选择机会？')
        self.assertEqual(result['removed'], ['各'])
        self.assertIn('束搜索', result['cleaned'])

    def test_idempotent_and_noop_for_original_query(self):
        result = clean_text('参数更新与提示中示例数量的区别是什么？')
        self.assertFalse(result['changed'])
        self.assertEqual(result['cleaned'], result['original'])
        self.assertEqual(result['removed'], [])


if __name__ == '__main__':
    unittest.main()
