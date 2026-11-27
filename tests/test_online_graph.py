"""Query alias separation, real traversal caps, comparison coverage and provenance."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.entity_aliases import GROUPS, query_matches, mentions
from papertech.evidence_context import assemble
from papertech.graph_store import GraphStore
from papertech.citations import quote_options,validate_answer


class OnlineGraphTests(unittest.TestCase):
    def test_quote_choices_preserve_pdf_newlines_and_reject_unknown_ids(self):
        text='The method uses graph\nretrieval and exact source evidence. '*30
        options=quote_options(text)
        self.assertTrue(all(q['quote'] in text for q in options))
        evidence=[dict(chunk_id='source',quote=text)]
        body=dict(answer='原文说明检索方法 [source]',status='ok',citations=[dict(chunk_id='source',quote_id='q1')])
        _,citations,_=validate_answer(json.dumps(body),evidence)
        self.assertEqual(citations[0]['quote'],options[0]['quote'])
        body['citations'][0]['quote_id']='q999'
        with self.assertRaises(ValueError):validate_answer(json.dumps(body),evidence)
        body['citations'][0]=dict(chunk_id='source',quote='The method uses graph retrieval and exact source evidence.')
        with self.assertRaises(ValueError):validate_answer(json.dumps(body),evidence)

    def test_tog_two_alias_does_not_anchor_original_tog(self):
        entities=[dict(id='a',name='ToG',type='Method'),dict(id='b',name='Think-on-Graph 2.0',type='Method'),
                  dict(id='c',name='ToG-2',type='Method'),dict(id='d',name='ToG-R',type='Method')]
        self.assertEqual({e['id'] for e in query_matches('Think-on-Graph 2.0 使用什么数据集？',entities)}, {'b','c'})
        self.assertFalse(mentions('ToG-2','ToG'))
        self.assertFalse(mentions('ToG-R','ToG'))
        self.assertEqual({e['id'] for e in query_matches('比较 ToG 和 ToG-2',entities)}, {'a','b','c'})

    def test_high_degree_node_expands_only_eight_neighbors_with_directed_claims(self):
        store=GraphStore.__new__(GraphStore); store.corpus_id='corpus'
        batches=[]
        def execute(query,**params):
            self.assertLessEqual(params['timeout_seconds'],10)
            if 'LIMIT 1000' in query:
                return [dict(id='seed',name='ToG',type='Method')]
            batches.append(params['ids'])
            self.assertEqual(params['degree_probe'],9)
            self.assertIn('LIMIT $degree_probe',query)
            rows=[]
            for origin in params['ids']:
                if origin=='seed':
                    for index in range(9):
                        rows.append(dict(origin=origin,target_id=str(index),target_name='D'+str(index),target_type='Dataset',
                                         edge=dict(predicate='EVALUATED_ON',claim_id=str(index),subject='ToG',object='D'+str(index)),
                                         evidence=dict(chunk_id='chunk',claim_id=str(index),quote='exact quote')))
            return rows
        store.execute=execute
        paths=store.expand_graph([],question='ToG',max_paths=40)
        self.assertEqual(len(paths),8)
        self.assertEqual(len(batches),2)
        self.assertEqual(len(batches[1]),8)
        self.assertIn('seed',store.last_graph_audit['degree_truncated'])
        self.assertTrue(all(p['edges'][0]['subject']=='ToG' for p in paths))

    def test_comparison_reserves_both_papers_and_only_passes_grounded_paths(self):
        def chunk(cid,paper,text,title):
            return dict(chunk_id=cid,paper_id=paper,text=text,title=title,parse_id='v',page_start=1,page_end=1,
                        source_spans=[{}],source_relative_path='source.pdf')
        source1,source2=[g['source_chunk'] for g in GROUPS[:2]]
        chunks={source1:chunk(source1,'p1','ToG evidence.','Think-on-Graph'),source2:chunk(source2,'p2','ToG-2 evidence.','Think-on-Graph 2.0')}
        chunks.update({str(i):chunk(str(i),'p1','ToG evidence. '*50,'Think-on-Graph') for i in range(8)})
        ranked=[dict(chunk_id=str(i),score=1,sources=[],rerank_score=.9) for i in range(8)]
        ranked+=[dict(chunk_id=source2,score=.1,sources=[],rerank_score=.8)]
        path=dict(nodes=[dict(name='ToG-2',type='Method'),dict(name='D',type='Dataset')],
                  edges=[dict(subject='ToG-2',object='D',predicate='EVALUATED_ON',claim_id='x')],
                  evidence=[dict(chunk_id=source2,quote='ToG-2 evidence.',claim_id='x')])
        evidence,paths,detail=assemble(ranked,chunks,[path],'比较 ToG 和 ToG-2',comparison=True)
        self.assertEqual({e['paper_id'] for e in evidence},{'p1','p2'})
        self.assertEqual(detail['missing_comparison_groups'],[])
        self.assertLessEqual(detail['context_bytes'],6000)
        # Source text now takes priority: a path cannot evict a selected block.
        without_paths=assemble(ranked,chunks,[],'比较 ToG 和 ToG-2',comparison=True)[0]
        self.assertEqual(evidence,without_paths)
        self.assertEqual(len(paths),0)
        roomy=assemble(ranked[:2]+[ranked[-1]],chunks,[path],'比较 ToG 和 ToG-2',comparison=True)
        self.assertEqual(len(roomy[1]),1)
        bad=dict(path,evidence=[dict(chunk_id=source2,quote='invented quote')])
        self.assertEqual(assemble(ranked,chunks,[bad],'ToG-2')[1],[])

    def test_missing_comparison_side_is_a_gap_not_a_negative_fact(self):
        chunks={g['source_chunk']:dict(chunk_id=g['source_chunk'],paper_id=str(i),text='source evidence',title='paper',
                parse_id='v',page_start=1,page_end=1,source_spans=[{}],source_relative_path='a.pdf') for i,g in enumerate(GROUPS)}
        ranked=[dict(chunk_id=GROUPS[0]['source_chunk'],sources=[],score=1)]
        evidence,paths,detail=assemble(ranked,chunks,[],'比较 ToG 和 ToG-2',comparison=True)
        self.assertEqual(detail['missing_comparison_groups'],['ToG-2'])
