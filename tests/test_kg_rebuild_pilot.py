import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.kg_rebuild_pilot import OPTIONS,RELATIONS,SCHEMA,VERSION,graph_from_claims,selected_corpus,smoke_chunks,validate
from papertech.kg_rebuild_filter import classify_chunk,validate_candidate,VERSION as FILTER_VERSION


class MechanismPilotTests(unittest.TestCase):
    def setUp(self):
        self.paper=dict(paper_id='p1',title='Paper',source_sha256='sha')
        self.chunk=dict(paper_id='p1',chunk_id='c1',parse_id='parse',text_sha256='textsha',
            text='The Retriever contains a graph encoder. The encoder implements message passing. The Retriever controls top-k.',
            page_start=2,page_end=2,section='Method',source_relative_path='paper.pdf')

    def candidate(self,subject_type,subject,predicate,object_type,obj,quote,kind='author_assertion'):
        return dict(subject_type=subject_type,subject=subject,predicate=predicate,object_type=object_type,
            object=obj,evidence_quote=quote,claim_kind=kind,confidence=.9)

    def test_only_three_mechanism_signatures_are_allowed(self):
        self.assertEqual(RELATIONS,{('Method','HAS_COMPONENT','Component'),
            ('Component','IMPLEMENTS','Mechanism'),('Method','CONTROLLED_BY','Parameter')})
        self.assertNotIn('anyOf',SCHEMA['properties']['relations']['items'])

    def test_explicit_mechanism_claims_keep_source_quote_and_pending_status(self):
        body={'relations':[
            self.candidate('Method','Retriever','HAS_COMPONENT','Component','graph encoder','The Retriever contains a graph encoder.'),
            self.candidate('Component','graph encoder','IMPLEMENTS','Mechanism','message passing','The encoder implements message passing.'),
            self.candidate('Method','Retriever','CONTROLLED_BY','Parameter','top-k','The Retriever controls top-k.')]}
        claims,rejected=validate(body,self.chunk,self.paper)
        self.assertEqual(len(claims),3);self.assertEqual(rejected,[])
        self.assertEqual({c['predicate'] for c in claims},{'HAS_COMPONENT','IMPLEMENTS','CONTROLLED_BY'})
        self.assertTrue(all(c['review_status']=='pending' and c['graph_version']==VERSION for c in claims))
        for claim in claims:
            self.assertEqual(self.chunk['text'][claim['quote_start']:claim['quote_end']],claim['evidence_quote'])

    def test_inference_and_unsupported_quotes_are_rejected(self):
        body={'relations':[
            self.candidate('Method','Retriever','HAS_COMPONENT','Component','graph encoder','The Retriever contains a graph encoder.','system_inference'),
            self.candidate('Method','Retriever','CONTROLLED_BY','Parameter','temperature','The Retriever controls temperature.')]}
        claims,rejected=validate(body,self.chunk,self.paper)
        self.assertEqual(claims,[])
        self.assertEqual({x['reason'] for x in rejected},{'system_inference_rejected','evidence_quote_not_in_chunk'})

    def test_wrong_endpoint_signature_is_rejected(self):
        invalid=self.candidate('Method','Retriever','IMPLEMENTS','Mechanism','message passing',
            'The encoder implements message passing.')
        claims,rejected=validate({'relations':[invalid]},self.chunk,self.paper)
        self.assertEqual(claims,[])
        self.assertEqual(rejected[0]['reason'],'relation_signature_not_allowed')

    def test_pilot_graph_is_version_tagged_and_provenance_bearing(self):
        claims,_=validate({'relations':[self.candidate('Method','Retriever','HAS_COMPONENT','Component','graph encoder','The Retriever contains a graph encoder.')]},self.chunk,self.paper)
        entities,edges=graph_from_claims(claims)
        self.assertEqual(len(entities),2);self.assertEqual(edges[0]['review_status'],'pending')
        self.assertEqual(edges[0]['chunk_id'],'c1');self.assertEqual(edges[0]['evidence_quote'],'The Retriever contains a graph encoder.')

    def test_selected_pilot_contains_exactly_three_papers_and_eligible_chunks(self):
        _,papers,chunks=selected_corpus(ROOT)
        self.assertEqual(len(papers),3)
        self.assertEqual({p['paper_id'] for p in papers},{
            'paper_42a876c95c3fe85af679c0dbc03a8a7d',
            'paper_cedbfddc8030ded4258640a1e0a0a733',
            'paper_0d99e8c368a360985899fcc4ff0ba156'})
        self.assertEqual(len(chunks),120)
        self.assertTrue(all(c['content_kind']!='references' and c['relation_extraction_eligible'] for c in chunks))

    def test_smoke_samples_are_substantive_and_context_is_bounded(self):
        _,_,chunks=selected_corpus(ROOT)
        samples=smoke_chunks(chunks)
        self.assertEqual(len(samples),3)
        self.assertEqual([(c['paper_id'],c['ordinal']) for c in samples],[
            ('paper_42a876c95c3fe85af679c0dbc03a8a7d',18),
            ('paper_cedbfddc8030ded4258640a1e0a0a733',11),
            ('paper_0d99e8c368a360985899fcc4ff0ba156',22)])
        self.assertEqual(OPTIONS['num_ctx'],4096)

    def filter_chunk(self, text, section='Method'):
        return dict(self.chunk, text=text, section=section, content_kind='body', source_spans=[])

    def test_filter_keeps_explicit_component_and_rejects_soft_prompting_parameter(self):
        paper=dict(self.paper, title='G-Retriever: a method')
        chunk=self.filter_chunk('G-Retriever consists of indexing, retrieval, subgraph construction and generation.\n'
                                'G-Retriever is fine-tuned via soft prompting.')
        keep=self.candidate('Method','G-Retriever','HAS_COMPONENT','Component','retrieval',
                            'G-Retriever consists of indexing, retrieval, subgraph construction and generation.')
        bad=self.candidate('Method','G-Retriever','CONTROLLED_BY','Parameter','soft prompting',
                           'G-Retriever is fine-tuned via soft prompting.')
        claim,reason=validate_candidate(keep,chunk,paper)
        self.assertIsNotNone(claim); self.assertIsNone(reason)
        claim,reason=validate_candidate(bad,chunk,paper)
        self.assertIsNone(claim); self.assertEqual(reason['reason'],'control_object_not_parameter')

    def test_filter_rejects_ablation_marker_and_generic_entities(self):
        paper=dict(self.paper, title='G-Retriever: a method')
        chunk=self.filter_chunk('G-Retriever consists of four stages. w/o Graph Encoder 54.62.')
        ablation=self.candidate('Method','G-Retriever','HAS_COMPONENT','Component','Graph Encoder',
                                'w/o Graph Encoder 54.62.')
        generic=self.candidate('Method','approach','HAS_COMPONENT','Component','retrieval',
                               'G-Retriever consists of four stages.')
        self.assertEqual(validate_candidate(ablation,chunk,paper)[1]['reason'],'ablation_does_not_establish_component')
        self.assertEqual(validate_candidate(generic,chunk,paper)[1]['reason'],'generic_entity')

    def test_filter_excludes_template_and_benchmark_chunks(self):
        paper=dict(self.paper, title='STaRK: Benchmarking LLM Retrieval')
        chunk=self.filter_chunk('metapath (drug ?[carrier] ?gene/protein): query template', section='A.4 STARK-PRIME')
        candidate=self.candidate('Method','metapath','HAS_COMPONENT','Component','carrier',
                                 'metapath (drug ?[carrier] ?gene/protein): query template')
        claim,reason=validate_candidate(candidate,chunk,paper)
        self.assertIsNone(claim); self.assertEqual(reason['reason'],'benchmark_paper_not_applicable')

    def test_filter_requires_named_technology_for_implements(self):
        paper=dict(self.paper, title='StructGPT: a method')
        chunk=self.filter_chunk('StructGPT includes an interface component. The component enables reading then reasoning.')
        candidate=self.candidate('Component','interface component','IMPLEMENTS','Mechanism','reading then reasoning',
                                 'The component enables reading then reasoning.')
        claim,reason=validate_candidate(candidate,chunk,paper)
        self.assertIsNone(claim); self.assertEqual(reason['reason'],'implementation_object_not_named_technology')

    def test_wrong_parser_related_work_label_does_not_delete_method_passage(self):
        paper=dict(self.paper, title='G-Retriever: a method')
        quote='G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation.'
        chunk=self.filter_chunk(quote, section='Related Work')
        candidate=self.candidate('Method','G-Retriever','HAS_COMPONENT','Component','retrieval',quote)
        claim,reason=validate_candidate(candidate,chunk,paper)
        self.assertIsNotNone(claim); self.assertIsNone(reason)

    def test_explicit_structgpt_interfaces_are_recognized_as_method_components(self):
        paper=dict(self.paper, title='StructGPT: a framework')
        quote='In our approach, we devise interfaces for KG to efficiently read the relevant information.'
        chunk=self.filter_chunk(quote, section='Method')
        candidate=self.candidate('Method','IRR','HAS_COMPONENT','Component','interfaces for KG',quote)
        claim,reason=validate_candidate(candidate,chunk,paper)
        self.assertIsNotNone(claim); self.assertIsNone(reason)

    def test_chunk_classifier_is_conservative_for_caption_plus_body(self):
        mixed=self.filter_chunk('Figure 3: Overview of the method.\nThis paragraph explains the proposed retrieval stage in detail and continues with enough prose to be a body block.', section='Method')
        self.assertEqual(classify_chunk(mixed)['kind'],'body_mixed')
        table=self.filter_chunk('Table 3: Results\nMethod 1 0.91\nMethod 2 0.88\nw/o encoder 0.70\nMethod 3 0.82\nMethod 4 0.80')
        self.assertEqual(classify_chunk(table)['kind'],'table')
        self.assertEqual(FILTER_VERSION,'kg-rebuild-pilot-14b-v5-filter')


if __name__=='__main__':unittest.main()
