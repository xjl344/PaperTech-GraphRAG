"""Unit tests for Phase-3 scalable foundations, Query-aware IsolatedGraph, and MethodCardNavigator."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from papertech.entity_aliases import GROUPS, discover_aliases_from_corpus, load_alias_groups
from papertech.isolated_graph import IsolatedGraph
from papertech.local_models import vector_cache, vector_metadata
from papertech.method_cards import MethodCardNavigator, SLOTS, select_representative_chunks, validate_card_payload
from papertech.workflow import Workflow

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / 'artifacts/eval/stage-4/benchmark-v3/isolated-graph.sqlite3'
HASH = 'f2eaae0c534dfa501b66ed80b5cd94c2140163d7a760acb56babd0218bab5d73'


class P3GraphAndCardsTests(unittest.TestCase):
    def test_entity_aliases_loaded_from_json_and_discovers_new_papers(self):
        loaded = load_alias_groups()
        self.assertEqual(loaded, GROUPS)
        self.assertGreaterEqual(len(loaded), 14)
        papers = [dict(paper_id='p_new', title='GraphZero: Fast Multi-Hop QA')]
        chunks = [dict(chunk_id='c_new_0', paper_id='p_new', ordinal=0,
                       text='We propose GraphZero (GZ) for fast multi-hop reasoning.')]
        discovered = discover_aliases_from_corpus(papers, chunks, reviewed=[])
        self.assertEqual(len(discovered), 1)
        self.assertIn('GraphZero', discovered[0]['names'])
        self.assertIn('GZ', discovered[0]['names'])

    def test_lazy_vector_cache_skips_loading_vectors_on_neo4j_backend(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'data').mkdir(parents=True)
        conn = sqlite3.connect(root / 'data/embeddings.sqlite3')
        conn.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)')
        conn.execute('CREATE TABLE embeddings (model_id TEXT, text_hash TEXT, vector TEXT, tokens INTEGER)')
        conn.execute("INSERT INTO metadata VALUES ('model', ?)", (json.dumps({'model_id': 'm1'}),))
        conn.execute("INSERT INTO embeddings VALUES ('m1', 'h1', ?, 5)", (json.dumps([1.0] + [0.0] * 1023),))
        conn.commit()
        conn.close()
        self.assertEqual(vector_metadata(root)['model_id'], 'm1')
        meta, lazy = vector_cache(root, load_vectors=False)
        self.assertEqual(meta['model_id'], 'm1')
        self.assertEqual(lazy, {})
        _, full = vector_cache(root, load_vectors=True)
        self.assertIn('h1', full)

    def test_method_card_validation_strips_invalid_citations_and_preserves_verbatim(self):
        chunks = [
            dict(chunk_id='c1', page_start=1, page_end=1, ordinal=0, content_kind='body', section='Abstract',
                 text='We propose DemoMethod with two stages: retrieval and pruning.'),
            dict(chunk_id='c2', page_start=8, page_end=8, ordinal=1, content_kind='references', section='References',
                 text='[1] Reference entry excluded from cards.'),
        ]
        selected = select_representative_chunks(chunks, limit=5)
        self.assertEqual([c['chunk_id'] for c in selected], ['c1'])
        raw = {
            'method_name_and_aliases': dict(summary='DemoMethod', keywords=['DemoMethod'],
                                            citations=[dict(eid='E1', quote_id='q1'), dict(eid='E99', quote_id='q1')]),
            'training_and_tuning': dict(summary='Hallucinated training', keywords=[],
                                        citations=[dict(eid='E1', quote_id='q99')]),
        }
        slots, rejected = validate_card_payload(raw, selected)
        self.assertEqual(set(slots), set(SLOTS))
        self.assertEqual(rejected, 2)
        self.assertEqual(len(slots['method_name_and_aliases']['citations']), 1)
        self.assertEqual(slots['method_name_and_aliases']['citations'][0]['chunk_id'], 'c1')
        self.assertEqual(slots['training_and_tuning']['summary'], 'not_found')

    def test_query_aware_isolated_graph_orders_neighbors_by_claim_vector_similarity(self):
        # Assign synthetic unit vectors to two distinct claims of HippoRAG to verify query-aware ranking.
        g0 = IsolatedGraph(GRAPH, HASH)
        self.addCleanup(g0.close)
        hippo_claims = [r['claim_id'] for r in g0.conn.execute(
            "SELECT claim_id FROM claims WHERE subject='HippoRAG' OR object='HippoRAG' ORDER BY claim_id LIMIT 2")]
        self.assertEqual(len(hippo_claims), 2)
        v_a = [1.0] + [0.0] * 1023
        v_b = [0.0, 1.0] + [0.0] * 1022
        g = IsolatedGraph(GRAPH, HASH, claim_vectors={hippo_claims[0]: v_a, hippo_claims[1]: v_b})
        self.addCleanup(g.close)
        paths_b = g.expand_graph([], question='HippoRAG', max_paths=5, per_node=2, query_vectors=[v_b])
        self.assertTrue(g.last_graph_audit['query_aware'])
        self.assertEqual(paths_b[0]['edges'][0]['claim_id'], hippo_claims[1])
        self.assertGreater(paths_b[0]['relevance_score'], 0.9)

    def test_method_card_navigator_returns_verbatim_chunks_by_slot_vector(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        cards_path = root / 'cards.json'
        db_path = root / 'slot_vecs.sqlite3'
        cards_path.write_text(json.dumps(dict(version='method-cards-v1', cards=[
            dict(paper_id='p1', title='Paper One', slots={
                'training_and_tuning': dict(summary='Uses LoRA fine-tuning', keywords=['LoRA'],
                                            citations=[dict(chunk_id='c_train', quote_id='q1', page_start=4, page_end=4, quote='LoRA')]),
            })
        ])), encoding='utf-8')
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE aux_vectors (model_id TEXT, item_id TEXT, text_sha256 TEXT, vector TEXT)')
        v = [1.0] + [0.0] * 1023
        conn.execute("INSERT INTO aux_vectors VALUES ('m1', 'p1::training_and_tuning', 'h', ?)", (json.dumps(v),))
        conn.commit()
        conn.close()
        nav = MethodCardNavigator(cards_path, db_path, 'm1')
        rows, slots = nav.navigate('Paper One training', [v], {'c_train': dict(paper_id='p1')})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['chunk_id'], 'c_train')
        self.assertEqual(slots[0]['slot'], 'training_and_tuning')


if __name__ == '__main__':
    unittest.main()
