"""End-to-end LangGraph tests with real audit and explicitly mocked HTTP/database."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx

from papertech.providers import Providers
from papertech.workflow import Workflow

ROOT=Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'.cache')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.cfg=dict(NEO4J_URI='bolt://mock.invalid',NEO4J_USER='user',NEO4J_PASSWORD='dummy',
                      DEEPSEEK_BASE_URL='https://mock.invalid/v1',DEEPSEEK_API_KEY='test-secret',DEEPSEEK_MODEL='mock',
                      CLOUD_BGE_BASE_URL='',CLOUD_BGE_API_KEY='',CLOUD_BGE_MODEL='')
        self.chunk=dict(chunk_id='chunk_test',paper_id='p',parse_id='v',title='HippoRAG',text_sha256='hash',
                        text='HippoRAG uses personalized PageRank for retrieval.',source_relative_path='a.pdf',
                        source_spans=[{'pdf_page':1}],page_start=1,page_end=1)
        self.patches=[patch('papertech.workflow.load_corpus',return_value=('corpus',[],[self.chunk])),
                      patch('papertech.workflow.vector_cache',return_value=({'model_id':'model'},{})),
                      patch('papertech.workflow.GraphStore')]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()

    def workflow(self, body=None, handler=None):
        w=Workflow(self.root,self.cfg,query_mode='cloud',rerank=False)
        w.store.retrieve.return_value=([dict(chunk_id='chunk_test',score=3)],[])
        w.store.expand_graph.return_value=[]
        if handler is None:
            handler=lambda r:httpx.Response(200,json=dict(model='mock',choices=[{'message':{'content':json.dumps(body)}}],usage={'prompt_tokens':100,'completion_tokens':30}))
        w.providers.client.close()
        w.providers=Providers(self.cfg,w.audit,httpx.Client(transport=httpx.MockTransport(handler)),sleeper=lambda _:None)
        self.addCleanup(w.close)
        return w

    def test_successful_mock_generation_real_graph_and_audit(self):
        body=dict(answer='作者使用 PageRank [chunk_test]',citations=[dict(chunk_id='chunk_test',quote='personalized PageRank for retrieval')],status='ok')
        w=self.workflow(body)
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['graph_paths'],[])
        self.assertEqual(result['citations'][0]['page_start'],1)
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM stages').fetchone()[0],7)
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM traces').fetchone()[0],1)
        self.assertEqual(result['usage_status'],'known')
        self.assertIsNone(result['estimated_cost'])

    def test_no_key_returns_evidence_not_fake_answer(self):
        w=self.workflow()
        w.cfg['DEEPSEEK_API_KEY']=''
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'evidence_only')
        self.assertTrue(result['evidence'])
        self.assertEqual(result['citations'],[])
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],0)

    def test_out_of_corpus_no_hits_refuses_before_generation(self):
        w=self.workflow()
        w.store.retrieve.return_value=([],[])
        result=w.ask('How to grow tomatoes on Mars?')
        self.assertEqual(result['status'],'refused')
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],0)

    def test_bad_citation_rejected_no_regeneration(self):
        w=self.workflow(dict(answer='fake [chunk_fake]',citations=[dict(chunk_id='chunk_fake',quote='personalized PageRank for retrieval')],status='ok'))
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'citation_error')
        self.assertEqual(result['citations'],[])
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],1)

    def test_conflicting_evidence_partial_keeps_gap(self):
        body=dict(answer='当前只有作者在特定条件下的报告 [chunk_test]；缺少一致实验条件，无法裁定冲突。',citations=[dict(chunk_id='chunk_test',quote='personalized PageRank for retrieval')],status='partial')
        w=self.workflow(body)
        result=w.ask('Compare conflicting reports')
        self.assertEqual(result['status'],'partial')
        self.assertIn('无法裁定',result['answer'])

    def test_timeout_result_unknown_preserved(self):
        def handler(request): raise httpx.ReadTimeout('unknown',request=request)
        w=self.workflow(handler=handler)
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['usage_status'],'usage_unknown')
        self.assertIsNone(result['estimated_cost'])

    def test_invalid_input_audited_no_calls(self):
        w=self.workflow()
        for q in ('','a'*2001):
            self.assertEqual(w.ask(q)['status'],'invalid_input')
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM requests').fetchone()[0],2)
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],0)

    def test_neo4j_disconnect_audited_no_generation(self):
        w=self.workflow()
        w.store.retrieve.side_effect=ConnectionError('disconnect')
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'error')
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],0)

    def test_reranker_failure_keeps_fulltext_evidence(self):
        w=self.workflow()
        w.cfg['DEEPSEEK_API_KEY']=''
        w.rerank_enabled=True
        with patch('papertech.workflow.run_worker',side_effect=RuntimeError('unavailable')):
            result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'evidence_only')
        self.assertTrue(result['evidence'])
        self.assertIn('reranker_skipped:RuntimeError',result['errors'])

    def test_graph_timeout_keeps_hybrid_and_records_degradation(self):
        w=self.workflow()
        w.cfg['DEEPSEEK_API_KEY']=''
        w.store.expand_graph.side_effect=TimeoutError('deadline')
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['status'],'evidence_only')
        self.assertTrue(result['evidence'])
        self.assertEqual(result['graph_paths'],[])
        self.assertIn('graph_expansion_skipped:TimeoutError',result['errors'])

    def test_gpu_oom_skips_without_cpu_retry(self):
        w=self.workflow()
        w.cfg['DEEPSEEK_API_KEY']=''
        w.rerank_enabled=True
        with patch('papertech.workflow.run_worker',side_effect=RuntimeError('CUDA out of memory')) as worker:
            result=w.ask('HippoRAG retrieval')
        self.assertEqual(worker.call_count,1)
        self.assertTrue(result['evidence'])
        self.assertEqual(result['retrieval_summary']['reranker'],'skipped')

    def test_nan_rerank_scores_are_not_used_to_filter_evidence(self):
        w=self.workflow()
        w.cfg['DEEPSEEK_API_KEY']=''
        w.rerank_enabled=True
        with patch('papertech.workflow.run_worker',return_value=dict(outputs=[float('nan')])):
            result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['retrieval_summary']['reranker'],'skipped')
        self.assertIsNone(result['evidence'][0]['rerank_score'])
        self.assertIn('reranker_skipped:ValueError',result['errors'])

    def test_grounded_graph_paths_reach_provider_prompt(self):
        received=[]
        body=dict(answer='作者使用 PageRank [chunk_test]',citations=[dict(chunk_id='chunk_test',quote='personalized PageRank for retrieval')],status='ok')
        def handler(request):
            received.append(json.loads(request.content))
            return httpx.Response(200,json=dict(choices=[{'message':{'content':json.dumps(body)}}]))
        w=self.workflow(handler=handler)
        path=dict(nodes=[dict(name='HippoRAG',type='Method'),dict(name='QA',type='Problem')],
                  edges=[dict(subject='HippoRAG',predicate='ADDRESSES',object='QA',claim_id='c')],
                  evidence=[dict(chunk_id='chunk_test',quote='personalized PageRank for retrieval',claim_id='c')])
        w.store.expand_graph.return_value=[path]
        result=w.ask('HippoRAG retrieval')
        prompt=json.loads(received[0]['messages'][1]['content'])
        self.assertEqual(len(prompt['graph_paths']),1)
        self.assertEqual(prompt['graph_paths'],result['retrieval_summary']['prompt_graph_paths'])
        reference=prompt['graph_paths'][0]['evidence'][0]
        self.assertNotIn('quote',reference)
        self.assertEqual(reference['chunk_id'],'chunk_test')
        self.assertTrue(set(reference['quote_ids']).issubset({q['quote_id'] for q in prompt['evidence'][0]['quote_options']}))
        start,end=reference['source_span']
        self.assertEqual(result['evidence'][0]['quote'][start:end],result['generation_paths'][0]['evidence'][0]['quote'])

    def test_cloud_embedding_without_compatibility_not_sent(self):
        w=self.workflow()
        w.cfg.update(CLOUD_BGE_BASE_URL='https://mock.invalid/v1',CLOUD_BGE_API_KEY='dummy',CLOUD_BGE_MODEL='bge-m3')
        w.cfg['DEEPSEEK_API_KEY']=''
        result=w.ask('HippoRAG retrieval')
        self.assertEqual(result['retrieval_summary']['dense_hits'],0)
        self.assertIn('cloud_embedding_compatibility_unverified:fulltext_only',result['errors'])
        self.assertEqual(w.audit.conn.execute('SELECT count(*) FROM calls').fetchone()[0],0)
