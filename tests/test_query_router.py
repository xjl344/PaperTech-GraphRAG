import unittest
from papertech.query_router_diagnostic import rule_candidate,validate


class RouterTests(unittest.TestCase):
    def body(self,decision='no_split',**kwargs):
        return dict(decision=decision,reason='目标结构',queries=kwargs.get('queries',[]),
            quotes=kwargs.get('quotes',['输入']),unresolved=[])

    def test_generic_rule_works_for_unknown_subjects(self):
        rows=rule_candidate('Alpha 的输入编码与 Beta 的输出聚合分别怎样工作？')
        self.assertEqual(len(rows),2)
        self.assertIn('输入编码',rows[0]['text'])
        self.assertNotIn('Beta',rows[0]['text'])

    def test_no_rule_for_unassigned_parallel_details(self):
        self.assertEqual(rule_candidate('Alpha 与 Beta 怎样编码？比较压缩与池化。'),[])

    def test_no_anchors_required_for_descriptive_split(self):
        q='找一种连接概念的方法和一种连接段落的方法，比较输入。'
        b=self.body('llm',queries=['连接概念的方法使用什么输入？','连接段落的方法使用什么输入？'],quotes=['连接概念的方法','连接段落的方法'])
        self.assertEqual(len(validate(q,b,[])['subqueries']),2)

    def test_unsupported_latin_method_rejected(self):
        with self.assertRaisesRegex(ValueError,'new_latin_term'):
            validate('输入怎么处理？',self.body('llm',queries=['HippoRAG 的输入？','输入处理？']),[])

    def test_rule_cannot_be_chosen_without_candidate(self):
        with self.assertRaisesRegex(ValueError,'rule_route_without_candidate'):
            validate('输入怎么处理？',self.body('rule'),[])

    def test_no_split_cannot_sneak_queries(self):
        with self.assertRaisesRegex(ValueError,'queries_on_non_llm_route'):
            validate('输入怎么处理？',self.body(queries=['输入怎么处理？']),[])

    def test_quote_must_exist(self):
        with self.assertRaisesRegex(ValueError,'quote_not_in_question'):
            validate('输入怎么处理？',self.body(quotes=['不存在']),[])

    def test_quote_whitespace_normalization_maps_to_original_offsets(self):
        question='面对结构化材料，G-Retriever 与 StructGPT 分别怎样缩小输入？'
        quote='面对结构化材料，G-Retriever与StructGPT分别怎样缩小输入？'
        result=validate(question,self.body('llm',queries=['G-Retriever缩小输入？','StructGPT缩小输入？'],quotes=[quote]),[])
        span=result['source_spans'][0]
        self.assertTrue(span['quote_normalized'])
        self.assertEqual(span['normalization'],'whitespace')
        self.assertEqual(question[span['start']:span['end']],question)
        self.assertEqual(span['quoted_text'],quote)

    def test_quote_punctuation_normalization_maps_to_original_offsets(self):
        question='比较（图检索）：它怎样工作？'
        quote='比较(图检索):它怎样工作?'
        result=validate(question,self.body('no_split',quotes=[quote]),[])
        span=result['source_spans'][0]
        self.assertTrue(span['quote_normalized'])
        self.assertEqual(span['normalization'],'whitespace_and_punctuation')
        self.assertEqual(question[span['start']:span['end']],question)

    def test_exact_quote_keeps_existing_span_shape(self):
        question='输入怎么处理？'
        result=validate(question,self.body(quotes=[question]),[])
        self.assertFalse(result['source_spans'][0]['quote_normalized'])
        self.assertEqual(result['source_spans'][0]['text'],question)

    def test_fallback_and_no_split_are_distinct(self):
        self.assertEqual(validate('输入怎么处理？',self.body(),[])['route'],'no_split')


if __name__=='__main__':unittest.main()
