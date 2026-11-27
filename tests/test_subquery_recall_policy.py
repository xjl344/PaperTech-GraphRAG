import unittest

from papertech.subquery_recall_policy import all_candidates, rank_query_hits, quota_pool


def q(qid, full, dense):
    def rows(ids):return [dict(chunk_id=x,score=1/i) for i,x in enumerate(ids,1)]
    return dict(id=qid,channels=dict(fulltext=rows(full),dense=rows(dense)))


class RecallPolicyTests(unittest.TestCase):
    def test_hit_count_then_best_rank_beats_first_discovery_rotation(self):
        queries=[q('Q0',['a','b','shared'],['c','shared']),q('SQ1',['x','shared'],['y']),q('SQ2',['shared','z'],[])]
        union=all_candidates(queries)
        ranked=rank_query_hits(union)
        shared=next(i for i,x in enumerate(ranked,1) if x['chunk_id']=='shared')
        self.assertEqual(shared,1)
        self.assertEqual(ranked[0]['found_by'],['Q0','SQ1','SQ2'])
        self.assertEqual(len(ranked[0]['discoveries']),4)

    def test_channel_quota_preserves_tail_and_fills_to_cap(self):
        queries=[q('Q0',[f'f{i}' for i in range(1,21)],[f'd{i}' for i in range(1,21)]),
            q('SQ1',['extra'],[])]
        union=all_candidates(queries)
        nine=quota_pool(union,9)
        retained={x['chunk_id'] for x in nine if x['retained']}
        self.assertIn('f9',retained)
        self.assertFalse(next(x for x in nine if x['chunk_id']=='f10')['quota_reserved'])
        self.assertEqual(sum(x['retained'] for x in nine),40)
        self.assertTrue(next(x for x in nine if x['chunk_id']=='extra')['retained'])

    def test_quota_deduplicates_chunks_across_query_channels(self):
        union=all_candidates([q('Q0',['a','b'],['a','c']),q('SQ1',['a'],['d'])])
        six=quota_pool(union,6)
        self.assertEqual(len(six),4)
        self.assertEqual(sum(x['quota_reserved'] for x in six),4)
        self.assertEqual(sum(x['retained'] for x in six),4)

    def test_overfull_quota_is_trimmed_by_query_hits_then_best_rank(self):
        queries=[q('Q0',[f'a{i}' for i in range(1,21)],[f'b{i}' for i in range(1,21)]),
            q('SQ1',[f'c{i}' for i in range(1,21)],[f'd{i}' for i in range(1,21)])]
        union=all_candidates(queries)
        result=quota_pool(union,20)
        kept=[x for x in result if x['retained']]
        self.assertEqual(len(kept),40)
        self.assertTrue(all(x['quota_reserved'] for x in kept))
        self.assertEqual(kept[0]['found_by'],['Q0'])


if __name__=='__main__':unittest.main()
