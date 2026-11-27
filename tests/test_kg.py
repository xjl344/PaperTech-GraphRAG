"""Schema, provenance, resume, and graph-boundary tests for Stage 3."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import httpx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.graph_store import GraphStore
from papertech.kg import ExtractionError, KGLedger, OllamaExtractor, validate_output


class KGLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'.cache')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.paper=dict(paper_id='paper-a',title='Graph Paper',source_sha256='source-sha')
        self.chunk=dict(paper_id='paper-a',chunk_id='chunk-a',parse_id='parse-a',text_sha256='sha-a',
                        text='Our Method-X improves upon Method-Y for graph retrieval.',
                        source_relative_path='Methods/paper.pdf',source_sha256='source-sha',
                        page_start=3,page_end=3,content_kind='body')
        self.body={'relations':[dict(subject_type='Method',subject='Method-X',predicate='IMPROVES_UPON',
                                     object_type='Method',object='Method-Y',
                                     evidence_quote='Our Method-X improves upon Method-Y for graph retrieval.',
                                     claim_kind='author_assertion',confidence=.8)]}

    def test_only_allowed_signatures_and_exact_quotes_survive(self):
        good,bad=validate_output(self.body,self.chunk,self.paper)
        self.assertEqual(len(good),1)
        self.assertEqual(good[0]['subject_norm'],'method-x')
        self.assertEqual(bad,[])
        invalid={'relations':[dict(self.body['relations'][0],predicate='INVENTED'),
                              dict(self.body['relations'][0],evidence_quote='paraphrased quote')]}
        good,bad=validate_output(invalid,self.chunk,self.paper)
        self.assertEqual(good,[])
        self.assertEqual({row['reason'] for row in bad},
                         {'relation_signature_not_allowed','evidence_quote_not_exact_in_chunk'})

    def test_whitespace_variants_keep_the_original_source_quote(self):
        relation = dict(self.body['relations'][0],
                        evidence_quote='Our Method-X improves\n upon  Method-Y for graph retrieval.')
        good, bad = validate_output({'relations': [relation]}, self.chunk, self.paper)
        self.assertEqual(bad, [])
        self.assertEqual(good[0]['evidence_quote'], self.chunk['text'])
        self.assertEqual(good[0]['quote_match_method'], 'whitespace_normalized')

    def test_punctuation_and_spelling_must_still_match(self):
        relation = dict(self.body['relations'][0], evidence_quote='Our Method X improves upon Method-Y for graph retrieval.')
        good, bad = validate_output({'relations': [relation]}, self.chunk, self.paper)
        self.assertEqual(good, [])
        self.assertEqual(bad[0]['reason'], 'evidence_quote_not_exact_in_chunk')

    def test_existing_ledger_schema_is_migrated(self):
        ledger = KGLedger(self.root)
        ledger.close()
        import sqlite3
        connection = sqlite3.connect(self.root / 'data/kg.sqlite3')
        connection.execute('ALTER TABLE kg_claims DROP COLUMN quote_match_method')
        connection.commit()
        connection.close()
        migrated = KGLedger(self.root)
        self.addCleanup(migrated.close)
        columns = {row['name'] for row in migrated.conn.execute('PRAGMA table_info(kg_claims)')}
        self.assertIn('quote_match_method', columns)

    def test_paper_relation_is_bound_to_current_source_paper(self):
        row=dict(subject_type='Paper',subject='a different cited paper',predicate='PROPOSES',
                 object_type='Method',object='Method-X',evidence_quote='Our Method-X improves upon Method-Y for graph retrieval.',
                 claim_kind='author_assertion',confidence=.8)
        good,_=validate_output({'relations':[row]},self.chunk,self.paper)
        self.assertEqual(good[0]['subject'],self.paper['title'])
        self.assertEqual(good[0]['subject_norm'],self.paper['paper_id'])

    def test_chunk_extraction_is_cached_and_claim_waits_for_review(self):
        ledger=KGLedger(self.root)
        self.addCleanup(ledger.close)
        paper_map={self.paper['paper_id']:self.paper}
        run_id=ledger.start_run('corpus-a','qwen2.5:7b-instruct',[self.chunk],paper_map)

        class Extractor:
            model='qwen2.5:7b-instruct'
            calls=0
            def extract(inner,self_chunk,self_paper):
                inner.calls+=1
                relations,_=validate_output(self.body,self.chunk,self.paper)
                return dict(relations=relations,rejected=[],input_tokens=123,output_tokens=35)

        extractor=Extractor()
        result=ledger.process_chunk(run_id,'corpus-a',self.chunk,self.paper,extractor)
        ledger.finish_run(run_id)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(extractor.calls,1)
        self.assertEqual(ledger.pending_claims('corpus-a')[0]['review_status'],'pending')
        with self.assertRaises(ValueError):
            ledger.mark_graph_written(ledger.pending_claims('corpus-a')[0]['claim_id'])
        second_run=ledger.start_run('corpus-a',extractor.model,[self.chunk],paper_map)
        self.assertEqual(ledger.progress(second_run)['run']['reused_chunks'],1)
        ledger.finish_run(second_run)
        self.assertEqual(extractor.calls,1)
        self.assertEqual(ledger.progress(second_run)['run']['input_tokens'],123)

    def test_extraction_http_uses_local_structured_endpoint(self):
        seen=[]
        def handler(request):
            seen.append(request)
            return httpx.Response(200,json={'response':json.dumps(self.body),'prompt_eval_count':90,'eval_count':24,'total_duration':1000})
        client=httpx.Client(transport=httpx.MockTransport(handler))
        extractor=OllamaExtractor(client=client)
        extractor.extract(self.chunk,self.paper)
        self.assertEqual(str(seen[0].url),'http://127.0.0.1:11434/api/generate')
        payload=json.loads(seen[0].content)
        self.assertEqual(payload['model'],'qwen2.5:7b-instruct')
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['format']['type'],'object')
        client.close()

    def test_confirmed_truncation_is_recorded_then_retried_with_more_budget(self):
        budgets = []
        def handler(request):
            budget = json.loads(request.content)['options']['num_predict']
            budgets.append(budget)
            if budget == 1200:
                return httpx.Response(200, json=dict(response='{"relations":[', done=True, done_reason='length',
                                                    prompt_eval_count=80, eval_count=1200))
            return httpx.Response(200, json=dict(response=json.dumps(self.body), done=True, done_reason='stop',
                                                prompt_eval_count=80, eval_count=200))
        client = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(client.close)
        ledger = KGLedger(self.root)
        self.addCleanup(ledger.close)
        run = ledger.start_run('corpus-a', 'qwen2.5:7b-instruct', [self.chunk], {'paper-a': self.paper})
        result = ledger.process_chunk(run, 'corpus-a', self.chunk, self.paper, OllamaExtractor(client=client))
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(budgets, [1200, 2400])
        attempts = ledger.conn.execute('SELECT * FROM kg_attempts ORDER BY rowid').fetchall()
        self.assertEqual([a['status'] for a in attempts], ['failed', 'completed'])
        self.assertEqual(sum(a['output_tokens'] for a in attempts), 1400)
        first = json.loads(attempts[0]['diagnostic_json'])
        self.assertEqual(first['raw_response'], '{"relations":[')
        self.assertEqual(first['done_reason'], 'length')
        self.assertEqual(first['error_code'], 'output_limit_reached')
        events = ''.join(r[0] for r in ledger.live().conn.execute('SELECT payload FROM events'))
        self.assertNotIn('raw_response', events)
        self.assertNotIn(self.chunk['text'], events)
        self.assertEqual(ledger.pending_claims('corpus-a')[0]['review_status'], 'pending')

    def test_bad_json_without_limit_evidence_is_not_retried(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(200, json=dict(response='{"relations":', done_reason='stop',
                                                prompt_eval_count=80, eval_count=20))
        client = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(client.close)
        events = []
        with self.assertRaises(ExtractionError) as failure:
            OllamaExtractor(client=client).extract(self.chunk, self.paper, observer=lambda e,d: events.append((e, dict(d))))
        self.assertEqual(len(calls), 1)
        self.assertFalse(failure.exception.diagnostic['output_limit_reached'])
        self.assertIn('parse_error', failure.exception.diagnostic)
        self.assertEqual([e for e, _ in events], ['start', 'end'])

    def test_repeated_truncation_stops_at_bounded_budget(self):
        budgets = []
        def handler(request):
            budget = json.loads(request.content)['options']['num_predict']
            budgets.append(budget)
            return httpx.Response(200, json=dict(response='{}', done_reason='length', eval_count=budget))
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(ExtractionError):
                OllamaExtractor(client=client).extract(self.chunk, self.paper)
        self.assertEqual(budgets, [1200, 2400, 4800])

    def test_http_service_error_is_diagnosed_without_budget_retry(self):
        budgets = []
        def handler(request):
            budgets.append(json.loads(request.content)['options']['num_predict'])
            return httpx.Response(500, json={'error': 'model runner failed to start'})
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(ExtractionError) as failure:
                OllamaExtractor(client=client).extract(self.chunk, self.paper)
        self.assertEqual(budgets, [1200])
        self.assertEqual(failure.exception.diagnostic['error_code'], 'ollama_http_500')
        self.assertEqual(failure.exception.diagnostic['service_error'], 'model runner failed to start')


class GraphStoreTests(unittest.TestCase):
    def test_only_valid_approved_allowlisted_claim_can_be_written(self):
        store=GraphStore.__new__(GraphStore)
        store.corpus_id='corpus-a'
        calls=[]
        def execute(query,**params):
            calls.append((query,params))
            if 'RETURN p.source_sha256' in query:
                return [dict(source_sha256='source-sha',paper_id='paper-a',parse_id='parse-a',page_start=3,page_end=3,
                             source_relative_path='Methods/paper.pdf',text='evidence quote')]
            return [dict(claim_id=params['claim_id'])]
        store.execute=execute
        claim=dict(claim_id='claim-a',corpus_id='corpus-a',paper_id='paper-a',paper_title='Graph Paper',
                   chunk_id='chunk-a',subject_type='Method',subject='Method-X',subject_norm='method-x',
                   predicate='IMPROVES_UPON',object_type='Method',object='Method-Y',object_norm='method-y',
                   evidence_quote='evidence quote',page_start=3,page_end=3,claim_kind='author_assertion',
                   quote_match_method='exact',
                   confidence=.8,validation_status='valid',review_status='approved',model='qwen',
                   prompt_version='p1',schema_version='s1',source_relative_path='Methods/paper.pdf',parse_id='parse-a')
        claim['source_sha256']='source-sha'
        claim['created_at']='2026-11-14T00:00:00+00:00'
        claim['review_note']='AI delegated review by Codex; evidence-review-v1; source supports relation'
        claim['reviewed_at']='2026-11-14T08:00:00+00:00'
        self.assertEqual(store.write_kg_claim(claim), 'claim-a')
        self.assertIn('MERGE (s)-[r:IMPROVES_UPON {claim_id:$claim_id}]->(o)', calls[1][0])
        self.assertEqual(calls[1][1]['relation_props']['review_status'],'approved')
        self.assertEqual(calls[1][1]['claim_props']['review_kind'],'ai_delegated')
        self.assertEqual(calls[1][1]['relation_props']['reviewer'],'Codex')
        self.assertEqual(calls[1][1]['relation_props']['review_note'],claim['review_note'])
        calls.clear()
        with self.assertRaises(ValueError):
            store.write_kg_claim(dict(claim,review_status='pending'))
        self.assertEqual(calls,[])

    def test_graph_expansion_is_fixed_at_two_hops_and_bounded(self):
        store=GraphStore.__new__(GraphStore)
        store.corpus_id='corpus-a'
        captured=[]
        store.execute=lambda query,**params:(captured.append((query,params)) or [])
        store.expand_graph([f'c{i}' for i in range(100)],max_paths=1000,max_seed_entities=1000)
        self.assertEqual(len(captured[-1][1]['seed_ids']),40)
        self.assertEqual(captured[-1][1]['max_seeds'],40)
        self.assertEqual(store.last_graph_audit['max_paths'],40)
        self.assertEqual(store.last_graph_audit['max_hops'],2)
        self.assertEqual(store.last_graph_audit['per_node'],8)


if __name__=='__main__':
    unittest.main()
