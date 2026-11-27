import unittest

from papertech.subquery_recall_diagnostic import merge_queries, score, paired


def query(qid, full, dense):
    return dict(id=qid, channels={key:[dict(chunk_id=c,score=1/(i+1)) for i,c in enumerate(items)]
        for key,items in (('fulltext',full),('dense',dense))})


class RecallDiagnosticTests(unittest.TestCase):
    def test_all_discoveries_survive_dedup_and_cap(self):
        rows=merge_queries([query('Q0',['x','y'],['x']),query('SQ1',['y'],['x','z'])],cap=1)
        self.assertEqual([r['chunk_id'] for r in rows],['x','y','z'])
        self.assertEqual(rows[0]['found_by'],['Q0','SQ1'])
        self.assertEqual(len(rows[0]['discoveries']),3)
        self.assertEqual([r['retained'] for r in rows],[True,False,False])
        self.assertEqual(rows[0]['discoveries'][-1],dict(query_id='SQ1',channel='dense',rank=1,score=1.0))

    def test_fixed_budget_can_lose_original_source(self):
        base=query('Q0',[f'f{i}' for i in range(20)],[f'd{i}' for i in range(20)])
        extra=query('SQ1',[f'e{i}' for i in range(20)],[f'g{i}' for i in range(20)])
        self.assertTrue(all(c['retained'] for c in merge_queries([base])))
        expanded=merge_queries([base,extra])
        self.assertEqual(len(expanded),80)
        self.assertFalse(next(c for c in expanded if c['chunk_id']=='f19')['retained'])
        self.assertEqual(sum(c['retained'] for c in expanded),40)

    def test_paper_coverage_does_not_imply_source_coverage(self):
        case=dict(units=['u','v'],source_papers=['p'])
        units=dict(u=dict(answer_point='a',known_support_chunks=['needed']),
            v=dict(answer_point='b',known_support_chunks=['absent']))
        chunks={cid:dict(paper_id='p') for cid in ('other','needed')}
        candidates=merge_queries([query('Q0',['other','needed'],[])],cap=1)
        metrics,facts=score(candidates,case,units,chunks)
        self.assertEqual(metrics['cap40_paper_coverage'],1)
        self.assertEqual(metrics['union_coverage'],.5)
        self.assertEqual(metrics['cap40_coverage'],0)
        self.assertEqual([f['reason'] for f in facts],['candidate_cap','upstream_missing'])

    def test_equal_coverage_can_hide_substitution(self):
        rows=[]
        for arm,hit in (('Original','a'),('Expanded','b')):
            rows.append(dict(case_id='case',arm=arm,metrics=dict(union_coverage=.5,cap40_coverage=.5),
                facts=[dict(unit_id=u,union_hit=u==hit,retained=u==hit) for u in ('a','b')]))
        p=paired(dict(results=rows))['case']['cap40_coverage']
        self.assertEqual(p['outcome'],'tie')
        self.assertEqual(p['added'],['b']);self.assertEqual(p['removed'],['a'])

    def test_fallback_is_identical(self):
        original=query('Q0',['a','b'],['b','c'])
        self.assertEqual(merge_queries([original]),merge_queries([original]+[]))


if __name__=='__main__':
    unittest.main()
