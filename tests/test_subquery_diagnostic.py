"""Source provenance and safe output handling for local question parsing."""
import unittest
from papertech.subquery_diagnostic import validate_split, row_metrics


def item(method, local=(), shared=(), assignment='explicit'):
    return dict(method=method,local_aspect=list(local),shared_task=list(shared),assignment=assignment,reason='题面')


class SubqueryDiagnosticTests(unittest.TestCase):
    def test_roundtrip_and_shared_task(self):
        q='HippoRAG 的节点 specificity、KG-GPT 的 top-k 分别改变什么？'
        body=dict(methods=[item('HippoRAG',['的节点 specificity'],['分别改变什么？']),
                           item('KG-GPT',['的 top-k'],['分别改变什么？'])],unresolved=[])
        out=validate_split(q,body)
        self.assertEqual(out['subqueries'][0]['text'],'HippoRAG 的节点 specificity 分别改变什么？')
        for row in out['subqueries']:
            for s in row['source_spans']:self.assertEqual(q[s['start']:s['end']],s['text'])

    def test_new_words_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'fragment_not_in_question'):
            validate_split('KGP 与 RoG 怎么比较？',dict(methods=[item('KGP',['KG 路径']),item('RoG')],unresolved=[]))

    def test_missing_extra_reordered_methods_are_rejected(self):
        for methods in ([item('KGP')],[item('RoG'),item('KGP')],[item('KGP'),item('RoG'),item('ToG')]):
            with self.assertRaisesRegex(ValueError,'missing_extra_or_reordered'):
                validate_split('KGP 与 RoG 怎么比较？',dict(methods=methods,unresolved=[]))

    def test_explicit_pronoun_removal_is_auditable(self):
        q='KGP 与 RoG，前者的段落和后者的路径怎么比较？'
        out=validate_split(q,dict(methods=[item('KGP',['前者的段落'],assignment='pronoun'),
             item('RoG',['后者的路径'],assignment='pronoun')],unresolved=[]))
        self.assertEqual(out['subqueries'][0]['text'],'KGP 的段落')
        self.assertEqual(out['subqueries'][0]['source_spans'][0]['text'],'前者的段落')
        self.assertEqual(out['subqueries'][0]['transformations'][0]['kind'],'remove_resolved_pronoun')

    def test_unresolved_must_also_come_from_question(self):
        q='KGP 与 RoG 怎么比较？'
        with self.assertRaisesRegex(ValueError,'fragment_not_in_question'):
            validate_split(q,dict(methods=[item('KGP'),item('RoG')],unresolved=['不存在']))

    def test_method_only_metric_not_confused_with_method_span(self):
        rows=[dict(text='KGP',subquery_source='method_only',source_spans=[dict(role='method')])]
        self.assertEqual(row_metrics(rows,True,True)['non_method_only_count'],0)

    def test_local_shared_duplication_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'local_and_shared_fragments_overlap'):
            validate_split('KGP 与 RoG 怎么比较？',dict(methods=[item('KGP',['怎么比较？'],['怎么比较？']),item('RoG')],unresolved=[]))

    def test_shared_pronouns_rejected(self):
        with self.assertRaisesRegex(ValueError,'shared_task_has_method_or_unresolved_pronoun'):
            validate_split('KGP 与 RoG，前者处理文本。',dict(methods=[item('KGP',shared=['前者处理文本']),item('RoG')],unresolved=[]))

    def test_nonobject_method_rejected(self):
        with self.assertRaisesRegex(ValueError,'missing_extra_or_reordered'):
            validate_split('KGP 与 RoG 怎么比较？',dict(methods=['KGP'],unresolved=[]))

    def test_order_based_assignment_requires_explicit_parallel_marker(self):
        q='LPKG 和 RoG 分别使用自然语言子问题与关系路径。'
        body=dict(methods=[item('LPKG',['自然语言子问题'],assignment='ordered'),
                           item('RoG',['关系路径'],assignment='ordered')],unresolved=[])
        self.assertEqual(len(validate_split(q,body)['subqueries']),2)
        with self.assertRaisesRegex(ValueError,'ordered_assignment_not_explicit'):
            validate_split('LPKG 和 RoG 使用两种表示。',body)

    def test_duplicate_fragment_is_not_duplicated(self):
        q='KGP 与 RoG 怎么比较？'
        out=validate_split(q,dict(methods=[item('KGP',shared=['怎么比较？','怎么比较？']),item('RoG')],unresolved=[]))
        self.assertEqual(out['subqueries'][0]['shared_task'],['怎么比较？','怎么比较？'])
        self.assertEqual(len(out['subqueries'][0]['source_spans']),1)


if __name__=='__main__':unittest.main()
