"""Enforce read-only gold separation, traversal bounds and treatment injection."""
import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import unittest

from papertech.isolated_graph import IsolatedGraph
from papertech.workflow import Workflow

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / 'artifacts/eval/stage-4/benchmark-v3/isolated-graph.sqlite3'
HASH = 'f2eaae0c534dfa501b66ed80b5cd94c2140163d7a760acb56babd0218bab5d73'


class IsolatedGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = IsolatedGraph(GRAPH, HASH)
        self.addCleanup(self.graph.close)

    def test_gold_tables_and_claim_reference_columns_are_denied(self):
        for statement in ('SELECT * FROM question_paths', 'SELECT * FROM question_units',
                'SELECT unit_id FROM claims', 'SELECT path_id FROM claims'):
            with self.assertRaises(sqlite3.DatabaseError):
                self.graph.conn.execute(statement).fetchall()
        with self.assertRaises(sqlite3.OperationalError):
            self.graph.conn.execute("UPDATE entities SET name='changed'")
        self.assertEqual(hashlib.sha256(GRAPH.read_bytes()).hexdigest(), HASH)

    def test_hash_conflict_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'hash_mismatch'):
            IsolatedGraph(GRAPH, '0' * 64)

    def test_traversal_preserves_source_direction_and_bounds(self):
        paths = self.graph.expand_graph([], question='比较 HippoRAG 与 RoG', max_paths=7, per_node=3)
        self.assertTrue(paths)
        self.assertLessEqual(len(paths), 7)
        self.assertEqual(self.graph.last_graph_audit['per_node'], 3)
        for path in paths:
            self.assertLessEqual(len(path['edges']), 2)
            self.assertEqual(len(path['nodes']), len(path['edges']) + 1)
            for edge, evidence, left, right in zip(path['edges'], path['evidence'], path['nodes'], path['nodes'][1:]):
                self.assertEqual({edge['subject'], edge['object']}, {left['name'], right['name']})
                row = self.graph.conn.execute('SELECT evidence_quote,provenance_json FROM claims WHERE claim_id=?',
                    (edge['claim_id'],)).fetchone()
                self.assertEqual(evidence['quote'], row['evidence_quote'])
                self.assertEqual(evidence['chunk_id'], json.loads(row['provenance_json'])['chunk_id'])
        self.graph.expand_graph([], question='ToG-2')
        anchors = self.graph.last_graph_audit['anchors']
        self.assertTrue(any(a['name'] == 'ToG-2' for a in anchors))
        self.assertFalse(any(a['name'] == 'ToG' for a in anchors))

    def test_hybrid_skips_injected_graph_and_graph_arm_uses_it(self):
        workflow = Workflow.__new__(Workflow)
        workflow.store = SimpleNamespace(expand_graph=lambda *a, **k: self.fail('old graph queried'))
        workflow.graph_expander = self.graph
        workflow.chunk_map = {'c': {}}
        workflow.graph_enabled = False
        state = dict(ranked=[dict(chunk_id='c')], errors=[], question='G-Retriever', retrieval_summary={})
        self.assertFalse(workflow.graph_expand(state)['retrieval_summary']['graph_executed'])
        called = []
        def expand(*args, **kwargs):
            called.append((args, kwargs))
            return []
        workflow.graph_expander = SimpleNamespace(expand_graph=expand)
        workflow.audit = SimpleNamespace(record_candidates=lambda *args: None,
            conn=SimpleNamespace(execute=lambda *args: []))
        workflow.graph_enabled = True
        state['request_id'] = 'test'
        result = workflow.graph_expand(state)
        self.assertEqual(result['errors'], [])
        self.assertEqual(called[0][1]['question'], state['question'])
        self.assertEqual(set(called[0][1]), {'max_paths', 'max_seed_entities', 'question', 'per_node'})


if __name__ == '__main__':
    unittest.main()
