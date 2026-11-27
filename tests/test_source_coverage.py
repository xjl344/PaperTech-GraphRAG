"""Source reservation must work without benchmark facts or new model calls."""
from pathlib import Path
import importlib.util
import json
import unittest

from papertech.corpus import load_corpus
from papertech.entity_aliases import GROUPS, is_comparison, mentions, source_groups
from papertech.evidence_context import assemble

ROOT = Path(__file__).resolve().parents[1]


class SourceCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, chunks = load_corpus(ROOT)
        cls.chunks = {chunk['chunk_id']: chunk for chunk in chunks}

    def test_catalog_provenance_covers_all_fourteen_papers(self):
        papers = set()
        for group in GROUPS:
            source = self.chunks[group['source_chunk']]
            self.assertIn(group['quote'], source['text'])
            papers.add(source['paper_id'])
        self.assertEqual(papers, {chunk['paper_id'] for chunk in self.chunks.values()})

    def test_multiple_sources_need_no_comparison_keyword(self):
        question = '结合KGP和CuriousLLM原文，后者怎样增强前者？'
        self.assertTrue(is_comparison(question))
        self.assertEqual({g['name'] for g in source_groups(question, self.chunks)}, {'KGP', 'CuriousLLM'})
        self.assertTrue(mentions('请解释RoG的训练步骤', 'RoG'))
        self.assertFalse(mentions('myRoGModel', 'RoG'))
        self.assertFalse(mentions('ToG-2', 'ToG'))
        self.assertFalse(mentions('Think-on-Graph 2.0', 'Think-on-Graph'))
        self.assertTrue(mentions('G–Retriever', 'G-Retriever'))

    def test_variant_and_parent_share_one_source_without_merging_names(self):
        groups = source_groups('ToG/ToG-R 与 Tree-of-Traversals 的搜索边界', self.chunks)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]['requested_names'], ['ToG', 'ToG-R'])
        self.assertFalse(is_comparison('ToG/ToG-R 的调用次数'))

    def synthetic(self):
        chunks = {}
        for group in GROUPS:
            if group['names'][0] not in ('HippoRAG', 'RoG', 'KGP'):
                continue
            name = group['names'][0]
            chunks[group['source_chunk']] = dict(self.chunks[group['source_chunk']], paper_id=name)
        def add(cid, paper, length):
            chunks[cid] = dict(chunk_id=cid, paper_id=paper, parse_id='v', title=paper,
                page_start=1, page_end=1, source_spans=[{}], source_relative_path='source.pdf',
                text=('Source evidence supports the method. ' * length))
        return chunks, add

    def test_reserve_lower_ranked_second_paper_before_repeated_first_paper(self):
        chunks, add = self.synthetic()
        for index in range(6):
            add(str(index), 'HippoRAG', 30)
        add('rog', 'RoG', 30)
        ranked = [dict(chunk_id=str(i), sources=[], rerank_score=.9) for i in range(6)]
        ranked.append(dict(chunk_id='rog', sources=[], rerank_score=.3))
        evidence, _, detail = assemble(ranked, chunks, [], 'HippoRAG和RoG如何检索？')
        self.assertEqual({item['paper_id'] for item in evidence}, {'HippoRAG', 'RoG'})
        self.assertEqual(detail['missing_comparison_groups'], [])
        self.assertLessEqual(detail['context_bytes'], 6000)

    def test_shorter_relevant_option_can_leave_room_for_other_sources(self):
        chunks, add = self.synthetic()
        add('long', 'HippoRAG', 90)
        add('short', 'HippoRAG', 10)
        add('rog', 'RoG', 30)
        ranked = [dict(chunk_id=cid, sources=[], rerank_score=.5) for cid in ('long', 'short', 'rog')]
        evidence, _, detail = assemble(ranked, chunks, [], 'HippoRAG和RoG的区别', budget=2600)
        self.assertEqual({item['paper_id'] for item in evidence}, {'HippoRAG', 'RoG'})
        self.assertIn('short', {item['chunk_id'] for item in evidence})
        self.assertLessEqual(detail['context_bytes'], 2600)

    def test_low_score_or_absent_source_remains_a_reported_gap(self):
        chunks, add = self.synthetic()
        add('hippo', 'HippoRAG', 10)
        add('rog', 'RoG', 10)
        ranked = [dict(chunk_id='hippo', sources=[], rerank_score=.8),
                  dict(chunk_id='rog', sources=[], rerank_score=.01)]
        _, _, detail = assemble(ranked, chunks, [], 'HippoRAG、RoG和KGP分别是什么？')
        missing = {item['name']: item['missing_reason'] for item in detail['source_coverage'] if item['missing_reason']}
        self.assertEqual(missing, {'RoG': 'no_eligible_source_candidate', 'KGP': 'no_eligible_source_candidate'})

    def test_failure_subset_keeps_parent_questions_and_reference_facts(self):
        from papertech.evaluation_datasets import load_benchmark
        from papertech.evaluation_details import enrich_examples
        from papertech.evaluation_datasets import dataset_payload
        diagnostic, digest, _ = load_benchmark(ROOT, 'benchmark-source-coverage-v1')
        parent, _, _ = load_benchmark(ROOT, 'benchmark-v2')
        parent_cases = {case['id']: case for case in parent['cases']}
        self.assertEqual(len(diagnostic['cases']), 16)
        for case in diagnostic['cases']:
            self.assertEqual(case, parent_cases[case['id']])
        for key, fact in diagnostic['units'].items():
            self.assertEqual(fact, parent['units'][key])
        exported = enrich_examples(dataset_payload(diagnostic, digest), diagnostic, self.chunks)
        for example in exported['examples']:
            self.assertEqual(set(example['inputs']), {'question'})
            self.assertFalse(example['outputs']['evaluation_config']['generate'])
            self.assertIn('selection_reason', example['metadata'])

    def test_baseline_snapshot_reproduces_all_selected_parent_evidence(self):
        from papertech.evaluation_datasets import load_benchmark
        spec = importlib.util.spec_from_file_location('coverage_replay', ROOT / 'scripts/eval-source-coverage.py')
        evaluator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluator)
        bench, _, directory = load_benchmark(ROOT, 'benchmark-source-coverage-v1')
        old = evaluator.baseline_assembler(directory, bench)
        parent = json.loads((ROOT / 'artifacts/reports/stage-4/benchmark-v2/runs' /
            bench['parent_benchmark']['run_id'] / 'summary.json').read_text(encoding='utf-8'))
        selected = {case['id'] for case in bench['cases']}
        for row in parent['results']:
            if row['arm'] != 'Hybrid+Graph' or row['case_id'] not in selected:
                continue
            comparison = any(word in row['question'].casefold() for word in ('比较', '对比', 'compare', 'versus'))
            evidence, paths, _ = old(row['ranked'], self.chunks, row['graph_paths'], row['question'], comparison)
            self.assertEqual(evidence, row['evidence'])
            self.assertEqual(paths, row['generation_paths'])


if __name__ == '__main__':
    unittest.main()
