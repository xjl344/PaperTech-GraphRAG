"""Meaningful fault injections and bounded pipeline checks, no real cloud calls."""
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.audit import Audit, redact
from papertech.citations import validate_answer
from papertech.corpus import valid_vector
from papertech.providers import Providers, ProviderError, retry_delay
from papertech.retrieval import fuse, select_evidence
from papertech.traces import flush_traces


class RagTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'.cache')
        self.root = Path(self.temp.name)
        self.audit = Audit(self.root)
        self.rid = self.audit.start('test question')
        self.cfg = dict(DEEPSEEK_BASE_URL='https://mock.invalid/v1',DEEPSEEK_API_KEY='secret-test-never-record',DEEPSEEK_MODEL='mock',
                        CLOUD_BGE_BASE_URL='https://mock.invalid/v1',CLOUD_BGE_API_KEY='secret-test-never-record',CLOUD_BGE_MODEL='mock')

    def tearDown(self):
        self.audit.close()
        self.temp.cleanup()

    def provider(self, handler):
        return Providers(self.cfg,self.audit,httpx.Client(transport=httpx.MockTransport(handler)),sleeper=lambda delay:None)

    def test_invalid_vectors_rejected(self):
        for v in ([1]*1023,[0]*1024,[math.nan]*1024,[math.inf]*1024):
            with self.assertRaises(ValueError): valid_vector(v)
        self.assertAlmostEqual(sum(x*x for x in valid_vector([1]*1024)),1)

    def test_persistent_402_block(self):
        seen=[]
        provider = self.provider(lambda r:(seen.append(r) or httpx.Response(402)))
        for _ in range(2):
            with self.assertRaises(ProviderError): provider.post(self.rid,'deepseek','chat/completions',{})
        self.assertEqual(len(seen),1)
        other = Audit(self.root)
        self.assertTrue(other.blocked('deepseek'))
        other.close()

    def test_429_retry_after_then_success(self):
        seen=[]
        delays=[]
        def handler(request):
            seen.append(request)
            return httpx.Response(429,headers={'Retry-After':'2'}) if len(seen)<3 else httpx.Response(200,json={'usage':{'total_tokens':1}})
        provider=self.provider(handler)
        provider.sleep=delays.append
        provider.post(self.rid,'siliconflow','embeddings',{})
        self.assertEqual(len(seen),3)
        self.assertEqual(delays,[2.,2.])

    def test_429_large_retry_after_does_not_early_retry(self):
        seen=[]
        provider=self.provider(lambda r:(seen.append(r) or httpx.Response(429,headers={'Retry-After':'120'})))
        with self.assertRaises(ProviderError): provider.post(self.rid,'deepseek','chat/completions',{})
        self.assertEqual(len(seen),1)
        self.assertIsNone(retry_delay('nan',0))

    def test_timeout_is_unknown_no_replay(self):
        seen=[]
        def handler(request):
            seen.append(request)
            raise httpx.ReadTimeout('Bearer secret-test-never-record',request=request)
        provider=self.provider(handler)
        with self.assertRaisesRegex(ProviderError,'result_unknown'): provider.post(self.rid,'deepseek','chat/completions',{})
        row=self.audit.conn.execute('SELECT * FROM calls').fetchone()
        self.assertEqual(len(seen),1)
        self.assertIsNone(row['usage'])
        self.assertIsNone(row['cost'])
        self.assertNotIn('secret-test',json.dumps(dict(row)))

    def test_400_401_422_and_uncertain_500_not_retried(self):
        for code in (400,401,422,500,503):
            seen=[]
            provider=self.provider(lambda r:(seen.append(r) or httpx.Response(code)))
            with self.assertRaises(ProviderError): provider.post(self.rid,'deepseek','chat/completions',{})
            self.assertEqual(len(seen),1)

    def test_siliconflow_5xx_bounded(self):
        seen=[]
        provider=self.provider(lambda r:(seen.append(r) or httpx.Response(503)))
        with self.assertRaises(ProviderError): provider.post(self.rid,'siliconflow','embeddings',{})
        self.assertEqual(len(seen),3)

    def test_missing_usage_cost_unknown(self):
        p=self.provider(lambda r:httpx.Response(200,json={'choices':[]}))
        _,cost=p.post(self.rid,'deepseek','chat/completions',{})
        self.assertIsNone(cost)
        self.assertEqual(self.audit.conn.execute('SELECT status FROM calls').fetchone()[0],'usage_unknown')

    def test_citation_whitelist_and_exact_quote(self):
        ev=[dict(chunk_id='chunk_real',paper_id='paper',page_start=1,page_end=2,quote='An exact original source sentence with evidence.')]
        good=dict(answer='作者报告结果 [chunk_real]',citations=[dict(chunk_id='chunk_real',quote='exact original source sentence')],status='ok')
        self.assertEqual(validate_answer(json.dumps(good),ev)[2],'ok')
        for bad in (dict(good,citations=[]),dict(good,answer='无引用的结论'),
                    dict(good,answer='伪造 [chunk_fake]',citations=[dict(chunk_id='chunk_fake',quote='exact original source sentence')]),
                    dict(good,citations=[dict(chunk_id='chunk_real',quote='fabricated original source sentence')])):
            with self.assertRaises(Exception): validate_answer(json.dumps(bad),ev)

    def test_fusion_budget_and_evidence_context(self):
        a=[dict(chunk_id=str(i),score=10-i/10) for i in range(20)]
        b=[dict(chunk_id=str(i),score=.9) for i in range(10,30)]
        ranked=fuse(a,b)
        self.assertLessEqual(len(ranked),40)
        self.assertEqual(len({r['chunk_id'] for r in ranked}),len(ranked))
        chunks={r['chunk_id']:dict(chunk_id=r['chunk_id'],paper_id='p',parse_id='v',title='title',page_start=1,page_end=1,source_spans=[{}],source_relative_path='a.pdf',text='evidence '*150) for r in ranked}
        evidence,used=select_evidence(ranked,chunks)
        self.assertLessEqual(len(evidence),8)
        self.assertLessEqual(used,6000)

    def test_trace_failure_then_recovery_and_redaction(self):
        self.audit.finish(self.rid,dict(status='evidence_only',answer='a',api_key='secret-test-never-record'))
        self.audit.queue_trace(self.rid)
        class MockTrace:
            failed=True
            def create_run(inner,**kwargs):
                if inner.failed: raise ConnectionError('secret-test-never-record')
            def read_run(inner,run_id):
                return dict(id=str(run_id))
            def get_run_url(inner,*,run):
                if not run.get('id'):
                    raise ValueError('URL lookup requires the remotely read Run')
                return 'https://mock.invalid/actual-test-run'
        client=MockTrace()
        cfg=dict(LANGSMITH_API_KEY='dummy',LANGSMITH_PROJECT='test')
        self.assertEqual(flush_traces(self.audit,cfg,client=client)['uploaded'],0)
        row=self.audit.conn.execute('SELECT * FROM traces').fetchone()
        self.assertEqual(row['status'],'pending')
        self.assertNotIn('secret-test',json.dumps(dict(row)))
        client.failed=False
        self.assertEqual(flush_traces(self.audit,cfg,client=client)['uploaded'],1)
        self.assertEqual(redact({'Authorization':'Bearer abc'}),{'Authorization':'[REDACTED]'})

    def test_request_record_precedes_mock_http(self):
        def handler(request):
            self.assertEqual(self.audit.conn.execute('SELECT status FROM requests WHERE id=?',(self.rid,)).fetchone()[0],'running')
            self.assertEqual(self.audit.conn.execute('SELECT status FROM calls').fetchone()[0],'sending')
            return httpx.Response(200,json={'usage':{'total_tokens':1}})
        self.provider(handler).post(self.rid,'siliconflow','embeddings',{})


if __name__ == '__main__': unittest.main()
