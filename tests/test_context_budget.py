"""Evidence must survive path insertion and reference prompts remain grounded."""
import copy
import json
from pathlib import Path
import unittest

from papertech.citations import prompt_evidence
from papertech.evidence_context import assemble, content_bytes, path_prompt


class ContextBudgetTests(unittest.TestCase):
    def fixture(self):
        chunks={}
        for index in range(4):
            cid='c'+str(index)
            chunks[cid]=dict(chunk_id=cid,paper_id='p',parse_id='v',title='Paper',page_start=1,page_end=1,
                source_spans=[{}],source_relative_path='paper.pdf',text=('Text evidence supports this method. '*10)+str(index))
        ranked=[dict(chunk_id=cid,sources=[],rerank_score=.9) for cid in chunks]
        quote=chunks['c0']['text'][:160]
        path=dict(nodes=[dict(name='Method',type='Method'),dict(name='Dataset',type='Dataset')],
            edges=[dict(subject='Method',object='Dataset',predicate='EVALUATED_ON',claim_id='cl')],
            evidence=[dict(chunk_id='c0',claim_id='cl',quote=quote)])
        return chunks,ranked,path

    def test_paths_never_remove_evidence_even_when_they_do_not_fit(self):
        chunks,ranked,path=self.fixture()
        base,_,detail=assemble(ranked,chunks,[],'question',budget=2400)
        constrained=detail['evidence_bytes']
        evidence,paths,summary=assemble(ranked,chunks,[path],'question',budget=constrained)
        self.assertEqual(evidence,base)
        self.assertEqual(paths,[])
        self.assertLessEqual(summary['context_bytes'],constrained)

    def test_full_and_reference_formats_choose_identical_original_text(self):
        chunks,ranked,path=self.fixture()
        before=copy.deepcopy(path)
        full,fullpaths,a=assemble(ranked,chunks,[path],'question',path_format='full')
        compact,compactpaths,b=assemble(ranked,chunks,[path],'question',path_format='references')
        self.assertEqual(full,compact)
        self.assertEqual(fullpaths,compactpaths)
        self.assertEqual(path,before)
        self.assertEqual(a['prompt_graph_paths'][0]['evidence'][0]['quote'],path['evidence'][0]['quote'])
        reference=b['prompt_graph_paths'][0]['evidence'][0]
        self.assertNotIn('quote',reference)
        start,end=reference['source_span']
        self.assertEqual(chunks['c0']['text'][start:end],path['evidence'][0]['quote'])
        self.assertLess(b['graph_context_bytes'],a['graph_context_bytes'])

    def test_invalid_path_provenance_is_not_sent(self):
        chunks,ranked,path=self.fixture()
        for bad in (dict(path,evidence=[dict(chunk_id='absent',quote='invented')]),
                    dict(path,evidence=[dict(chunk_id='c0',quote='invented')])):
            evidence,paths,detail=assemble(ranked,chunks,[bad],'question')
            self.assertEqual(paths,[])
            self.assertEqual(detail['prompt_graph_paths'],[])
            self.assertTrue(evidence)

    def test_reference_handles_quote_crossing_quote_option_boundaries(self):
        text=''.join('Sentence %03d has reliable evidence. ' % i for i in range(80))
        source=dict(chunk_id='c',quote=text)
        path=dict(nodes=[],edges=[],evidence=[dict(chunk_id='c',quote=text[850:1050])])
        prompt=path_prompt(path,{'c':source})
        reference=prompt['evidence'][0]
        self.assertGreaterEqual(len(reference['quote_ids']),2)
        self.assertEqual(reference['source_span'],[850,1050])
        self.assertTrue(set(reference['quote_ids']).issubset({o['quote_id'] for o in prompt_evidence(
            dict(source,title='paper',page_start=1,page_end=1))['quote_options']}))

    def test_graph_list_overhead_and_serialized_content_stay_inside_budget(self):
        chunks,ranked,path=self.fixture()
        paths=[dict(path,edges=[dict(path['edges'][0],claim_id=str(i))]) for i in range(10)]
        evidence,selected,detail=assemble(ranked,chunks,paths,'question',budget=2600)
        self.assertLessEqual(len(selected),4)
        self.assertLessEqual(detail['context_bytes'],2600)
        self.assertEqual(detail['serialized_content_bytes'],content_bytes(evidence,detail['prompt_graph_paths']))
        self.assertLessEqual(detail['serialized_content_bytes'],2600)
        self.assertEqual(detail['graph_context_bytes'],len(json.dumps(detail['prompt_graph_paths'],ensure_ascii=False).encode()))

    def test_unknown_path_format_rejected_even_without_paths(self):
        chunks,ranked,_=self.fixture()
        with self.assertRaises(ValueError):
            assemble(ranked,chunks,[],'question',path_format='invented')

    def test_reserved_quota_can_admit_path_without_exceeding_total(self):
        chunks,ranked,path=self.fixture()
        # Construct a boundary where legacy evidence leaves no room for a path.
        base,_,detail=assemble(ranked,chunks,[],'question')
        budget=detail['evidence_bytes']
        _,legacy,_=assemble(ranked,chunks,[path],'question',budget=budget)
        evidence,selected,summary=assemble(ranked,chunks,[path],'question',budget=budget,path_budget=800,path_budget_mode='reserved')
        self.assertFalse(legacy)
        self.assertTrue(selected)
        self.assertLess(len(evidence),len(base))
        self.assertLessEqual(summary['evidence_bytes'],budget-800)
        self.assertLessEqual(summary['graph_context_bytes'],800)
        self.assertLessEqual(summary['serialized_content_bytes'],budget)

    def test_quota_does_not_admit_missing_or_fabricated_source(self):
        chunks,ranked,path=self.fixture()
        for bad in (dict(path,evidence=[dict(chunk_id='c0',quote='invented')]),
                    dict(path,evidence=[dict(chunk_id='absent',quote='invented')])):
            _,selected,_=assemble(ranked,chunks,[bad],'question',path_budget=1200)
            self.assertFalse(selected)
        _,selected,_=assemble(ranked,chunks,[path],'question',path_budget=6000,path_budget_mode='reserved')
        self.assertFalse(selected)

    def test_quota_includes_cumulative_json_bytes_and_rejects_invalid_values(self):
        chunks,ranked,path=self.fixture()
        paths=[dict(path,edges=[dict(path['edges'][0],claim_id=str(i))]) for i in range(10)]
        _,selected,summary=assemble(ranked,chunks,paths,'question',path_budget=800)
        self.assertTrue(selected)
        self.assertLessEqual(len(selected),4)
        self.assertEqual(summary['graph_context_bytes'],len(json.dumps(summary['prompt_graph_paths'],ensure_ascii=False).encode()))
        self.assertLessEqual(summary['graph_context_bytes'],800)
        for invalid in (-1,6001,1.5,True):
            with self.assertRaisesRegex(ValueError,'invalid_path_budget'):
                assemble(ranked,chunks,paths,'question',path_budget=invalid,path_budget_mode='reserved')

    def test_additional_budget_keeps_every_original_block_and_admits_paths(self):
        chunks,ranked,path=self.fixture()
        base,_,detail=assemble(ranked,chunks,[],'question')
        budget=detail['evidence_bytes']
        baseline=assemble(ranked,chunks,[path],'question',budget=budget)
        self.assertFalse(baseline[1])
        for extra in (800,1200):
            evidence,selected,summary=assemble(ranked,chunks,[path],'question',budget=budget,path_budget=extra)
            self.assertEqual(evidence,base)
            self.assertTrue(selected)
            self.assertEqual(summary['evidence_budget_bytes'],budget)
            self.assertEqual(summary['total_budget_bytes'],budget+extra)
            self.assertLessEqual(summary['evidence_bytes'],budget)
            self.assertLessEqual(summary['graph_context_bytes'],extra)
            self.assertLessEqual(summary['serialized_content_bytes'],budget+extra)
        self.assertEqual(baseline,assemble(ranked,chunks,[path],'question',budget=budget,path_budget=0))

    def test_additional_budget_rejects_ungrounded_paths_and_counts_list_bytes(self):
        chunks,ranked,path=self.fixture()
        bad=dict(path,evidence=[dict(chunk_id='c0',quote='invented')])
        paths=[bad]+[dict(path,edges=[dict(path['edges'][0],claim_id=str(i))]) for i in range(10)]
        evidence,selected,summary=assemble(ranked,chunks,paths,'question',path_budget=800)
        self.assertEqual(evidence,assemble(ranked,chunks,[],'question')[0])
        self.assertTrue(selected)
        self.assertNotIn(bad,selected)
        self.assertLessEqual(len(selected),4)
        self.assertLessEqual(summary['graph_context_bytes'],800)
        self.assertEqual(summary['graph_context_bytes'],len(json.dumps(summary['prompt_graph_paths'],ensure_ascii=False).encode()))
        for invalid in (-1,1.5,True):
            with self.assertRaisesRegex(ValueError,'invalid_path_budget'):
                assemble(ranked,chunks,paths,'question',path_budget=invalid)

    def test_workflow_passes_extra_budget_without_reducing_originals(self):
        from papertech.workflow import Workflow
        chunks,ranked,path=self.fixture()
        workflow=Workflow.__new__(Workflow)
        workflow.chunk_map=chunks
        workflow.path_budget=1200
        workflow.evidence_budget=6000
        workflow.evidence_max=8
        workflow.source_policy='named_first'
        state=dict(ranked=ranked,graph_paths=[path],question='question',retrieval_summary={},errors=[])
        result=workflow.evidence(state)
        expected=assemble(ranked,chunks,[path],'question',path_budget=0)[0]
        self.assertEqual(result['evidence'],expected)
        self.assertEqual(result['retrieval_summary']['context_budget_bytes'],7200)
        self.assertEqual(result['retrieval_summary']['evidence_budget_bytes'],6000)
        self.assertTrue(result['generation_paths'])


if __name__=='__main__':
    unittest.main()
