import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('next16_eval', ROOT / 'scripts/eval-next-16.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DiverseOrderTests(unittest.TestCase):
    def test_diversity_breaks_close_relevance_tie_for_redundant_text(self):
        ranked = [
            {'chunk_id': 'a', 'rerank_score': 0.95},
            {'chunk_id': 'b', 'rerank_score': 0.62},
            {'chunk_id': 'c', 'rerank_score': 0.57},
        ]
        chunks = {
            'a': {'text': 'graph retrieval selects evidence passages'},
            'b': {'text': 'graph retrieval selects evidence passages for QA'},
            'c': {'text': 'training data evaluates reasoning on benchmark questions'},
        }

        ordered = MODULE.diverse_order(ranked, chunks)

        self.assertEqual([row['chunk_id'] for row in ordered], ['a', 'c', 'b'])
        self.assertEqual({row['chunk_id'] for row in ordered}, {'a', 'b', 'c'})

    def test_unknown_chunks_remain_after_known_candidates(self):
        ranked = [{'chunk_id': 'a', 'rerank_score': 0.8}, {'chunk_id': 'missing', 'score': 0.2}]
        ordered = MODULE.diverse_order(ranked, {'a': {'text': 'source evidence'}})
        self.assertEqual([row['chunk_id'] for row in ordered], ['a', 'missing'])


if __name__ == '__main__':
    unittest.main()
