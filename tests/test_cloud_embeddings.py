"""DeepInfra payload, no-key behavior and compatibility invalidation without network."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.audit import Audit
from papertech.cloud_embeddings import VERSION, check_compatibility, compatible, query_mode
from papertech.providers import ProviderError, Providers


class CloudEmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.audit = Audit(self.root)
        self.addCleanup(self.audit.close)
        self.request = self.audit.start('probe')
        self.cfg = dict(CLOUD_BGE_PROVIDER='deepinfra', CLOUD_BGE_BASE_URL='https://api.deepinfra.com/v1/openai',
                        CLOUD_BGE_MODEL='BAAI/bge-m3', CLOUD_BGE_API_KEY='dummy-test-key', QUERY_EMBEDDING_MODE='auto')
        self.vector = [1.] + [0.] * 1023

    def provider(self, handler):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(client.close)
        return Providers(self.cfg, self.audit, client=client, sleeper=lambda _: None)

    def test_deepinfra_payload_order_and_token_recording(self):
        seen = []
        def handler(request):
            seen.append(request)
            return httpx.Response(200, json=dict(data=[dict(index=1, embedding=self.vector), dict(index=0, embedding=self.vector)],
                                                 usage=dict(prompt_tokens=42, total_tokens=42)))
        result = self.provider(handler).embedding(self.request, ['hello', 'world'])
        self.assertEqual(len(result), 2)
        self.assertEqual(str(seen[0].url), 'https://api.deepinfra.com/v1/openai/embeddings')
        self.assertEqual(seen[0].headers['Authorization'], 'Bearer dummy-test-key')
        self.assertEqual(json.loads(seen[0].content), dict(model='BAAI/bge-m3', input=['hello', 'world'], encoding_format='float'))
        row = self.audit.conn.execute('SELECT * FROM calls').fetchone()
        self.assertEqual(row['provider'], 'deepinfra')
        self.assertEqual(json.loads(row['usage'])['prompt_tokens'], 42)
        self.assertIsNone(row['cost'])

    def test_bad_dimensions_rejected_and_tuple_input_not_sent(self):
        seen = []
        def handler(request):
            seen.append(request)
            return httpx.Response(200, json=dict(data=[dict(index=0, embedding=[1.] * 768)]))
        provider = self.provider(handler)
        with self.assertRaises(ProviderError):
            provider.embedding(self.request, ('hello',))
        self.assertEqual(seen, [])
        with self.assertRaises(ValueError):
            provider.embedding(self.request, ['hello'])

    def test_deepinfra_uncertain_500_not_retried(self):
        seen = []
        provider = self.provider(lambda request: seen.append(request) or httpx.Response(500))
        with self.assertRaises(ProviderError):
            provider.embedding(self.request, ['hello'])
        self.assertEqual(len(seen), 1)

    def test_missing_key_no_network_and_auto_local(self):
        self.cfg['CLOUD_BGE_API_KEY'] = ''
        handler = Mock(side_effect=AssertionError('Network must not be called'))
        provider = self.provider(handler)
        runner = Mock(side_effect=AssertionError('Local model must not be loaded'))
        self.assertEqual(query_mode(self.cfg), 'local')
        result = check_compatibility(self.root, self.cfg, provider, self.request, runner=runner)
        self.assertEqual(result['status'], 'not_configured')
        self.assertFalse(compatible(self.root, self.cfg, 'local-id'))
        handler.assert_not_called()
        runner.assert_not_called()

    def run_gate(self, cloud=None, model_id='local-id'):
        provider = Mock()
        provider.configured.return_value = True
        provider.embedding.return_value = cloud or [self.vector] * 4
        runner = Mock(return_value=dict(model_id=model_id, outputs=[self.vector] * 4))
        with patch('papertech.cloud_embeddings.vector_cache', return_value=({'model_id': 'local-id'}, {})):
            result = check_compatibility(self.root, self.cfg, provider, self.request, runner=runner)
        return result, provider

    def test_passing_probe_gate_matches_model_endpoint_and_expiry(self):
        result, _ = self.run_gate()
        self.assertTrue(result['passed'])
        self.assertEqual(query_mode(self.cfg), 'cloud')
        self.assertTrue(compatible(self.root, self.cfg, 'local-id'))
        self.assertFalse(compatible(self.root, self.cfg, 'changed-local-id'))
        self.assertFalse(compatible(self.root, dict(self.cfg, CLOUD_BGE_MODEL='qwen-other'), 'local-id'))
        result['verified_timestamp'] = time.time() - 31 * 86400
        (self.root / 'data/cloud-compatibility.json').write_text(json.dumps(result), encoding='utf-8')
        self.assertFalse(compatible(self.root, self.cfg, 'local-id'))

    def test_incompatible_same_dimension_vectors_revoke_old_approval(self):
        self.assertTrue(self.run_gate()[0]['passed'])
        orthogonal = [0., 1.] + [0.] * 1022
        result, _ = self.run_gate([orthogonal] * 4)
        self.assertFalse(result['passed'])
        self.assertEqual(result['status'], 'incompatible')
        self.assertFalse(compatible(self.root, self.cfg, 'local-id'))

    def test_local_model_change_and_cloud_error_revoke_old_approval(self):
        self.run_gate()
        result, provider = self.run_gate(model_id='changed')
        self.assertEqual(result['status'], 'validation_error')
        provider.embedding.assert_not_called()
        self.assertFalse(compatible(self.root, self.cfg, 'local-id'))

    def cloudflare(self):
        self.cfg.update(CLOUD_BGE_PROVIDER='cloudflare', CLOUDFLARE_ACCOUNT_ID='a'*32,
                        CLOUDFLARE_AUTH_TOKEN='dummy-cloudflare-token', CLOUD_BGE_MODEL='@cf/baai/bge-m3',
                        CLOUD_BGE_API_KEY='', CLOUD_BGE_BASE_URL='')

    def test_cloudflare_auth_payload_envelope_and_unknown_usage(self):
        self.cloudflare()
        seen = []
        def handler(request):
            seen.append(request)
            return httpx.Response(200, json=dict(success=True, result=dict(shape=[2,1024], data=[self.vector, self.vector])))
        provider = self.provider(handler)
        self.assertTrue(provider.configured('CLOUD_BGE'))
        self.assertEqual(query_mode(self.cfg), 'cloud')
        self.assertEqual(len(provider.embedding(self.request, ['hello', 'world'])), 2)
        self.assertEqual(str(seen[0].url), 'https://api.cloudflare.com/client/v4/accounts/' + 'a'*32 + '/ai/run/@cf/baai/bge-m3')
        self.assertEqual(seen[0].headers['Authorization'], 'Bearer dummy-cloudflare-token')
        self.assertEqual(json.loads(seen[0].content), dict(text=['hello','world']))
        row = self.audit.conn.execute('SELECT * FROM calls').fetchone()
        self.assertEqual(row['status'], 'usage_unknown')
        self.assertIsNone(row['usage'])
        self.assertEqual(row['provider'], 'cloudflare')

    def test_cloudflare_api_envelope_failure_and_http_errors_no_retry(self):
        self.cloudflare()
        for status, body in [(200, dict(success=False, errors=[dict(code=10000,message='secret-never-record')])),
                             (401, {}), (403, {}), (500, {})]:
            calls = []
            provider = self.provider(lambda r: calls.append(r) or httpx.Response(status, json=body))
            with self.assertRaises(ProviderError):
                provider.embedding(self.request, ['hello'])
            self.assertEqual(len(calls), 1)
        events = ''.join(r[0] for r in self.audit.live.conn.execute('SELECT payload FROM events'))
        self.assertNotIn('secret-never-record', events)
        self.assertNotIn('dummy-cloudflare-token', events)

    def test_cloudflare_wrong_shape_and_account_approval_binding(self):
        self.cloudflare()
        provider = self.provider(lambda r: httpx.Response(200, json=dict(success=True, result=dict(shape=[1,768],data=[[1.]*768]))))
        with self.assertRaisesRegex(ProviderError, 'shape_mismatch'):
            provider.embedding(self.request, ['hello'])
        self.assertTrue(self.run_gate()[0]['passed'])
        self.assertTrue(compatible(self.root, self.cfg, 'local-id'))
        self.assertFalse(compatible(self.root, dict(self.cfg, CLOUDFLARE_ACCOUNT_ID='b'*32), 'local-id'))
        self.assertFalse(self.provider(lambda r: None).configured('MISSING'))
        self.cfg['CLOUDFLARE_AUTH_TOKEN']=''
        self.assertFalse(provider.configured('CLOUD_BGE'))
        self.assertEqual(query_mode(self.cfg), 'local')
        self.run_gate()
        provider = Mock()
        provider.configured.return_value = True
        provider.embedding.side_effect = RuntimeError('do-not-record-secret')
        with patch('papertech.cloud_embeddings.vector_cache', return_value=({'model_id': 'local-id'}, {})):
            result = check_compatibility(self.root, self.cfg, provider, self.request,
                                         runner=Mock(return_value=dict(model_id='local-id', outputs=[self.vector] * 4)))
        self.assertFalse(result['passed'])
        self.assertNotIn('do-not-record-secret', json.dumps(result))
        self.assertFalse(compatible(self.root, self.cfg, 'local-id'))


if __name__ == '__main__':
    unittest.main()
