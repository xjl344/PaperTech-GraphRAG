import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from papertech.evidence_context import assemble
from papertech.retrieval import select_evidence
from papertech.staged_retrieval_diagnostics import merge_channels


class StagedResourceTests(unittest.TestCase):
    def fixture(self):
        chunks={str(i):dict(chunk_id=str(i),paper_id='A' if i<10 else 'B',parse_id='v',title='Paper',
            page_start=1,page_end=1,source_spans=[{}],source_relative_path='paper.pdf',text='Short factual evidence '+str(i)) for i in range(14)}
        ranked=[dict(chunk_id=cid,sources=[],rerank_score=.9-i*.01) for i,cid in enumerate(chunks)]
        return chunks,ranked

    def test_count_limit_is_independent_of_byte_budget(self):
        chunks,ranked=self.fixture()
        a,_=select_evidence(ranked,chunks,budget=100000)
        b,_=select_evidence(ranked,chunks,budget=100000,evidence_max=12)
        self.assertEqual((len(a),len(b)),(8,12))
        for invalid in (0,True,1.5,41):
            with self.assertRaises(ValueError):
                select_evidence(ranked,chunks,evidence_max=invalid)

    def test_named_policy_is_separate_from_scores_and_count(self):
        chunks,ranked=self.fixture();before=copy.deepcopy(ranked)
        groups=[dict(paper_id='A',name='A'),dict(paper_id='B',name='B')]
        with patch('papertech.evidence_context.requested_groups',return_value=groups):
            named=assemble(ranked,chunks,[],'question',budget=100000,evidence_max=8)[0]
            score=assemble(ranked,chunks,[],'question',budget=100000,evidence_max=8,source_policy='score_order')[0]
        self.assertEqual({r['paper_id'] for r in named},{'A','B'})
        self.assertEqual({r['paper_id'] for r in score},{'A'})
        self.assertEqual(ranked,before)

    def test_expanded_rrf_does_not_silently_cut_new_dense_candidates(self):
        channels=dict(dense=[dict(chunk_id=str(i),score=1-i*.01) for i in range(60)],
            fulltext=[dict(chunk_id=str(i),score=1) for i in range(50,70)])
        result=merge_channels(channels)
        self.assertEqual(len(result),70)
        self.assertEqual(set(r['chunk_id'] for r in result),set(str(i) for i in range(70)))
        self.assertTrue(all(r['sources'] for r in result))
