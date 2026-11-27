"""Provenance, failure isolation, versioning and recovery tests using synthetic PDFs."""

import io
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import pymupdf
from papertech.ingest import file_hash, ingest_batch
from papertech.pdf import ParseError, audit_document, configuration, identities, parse_document


class IngestTests(unittest.TestCase):
    def setUp(self):
        cache = (ROOT / '.cache/temp').resolve()
        cache.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='ingest-test-', dir=cache)
        self.project = Path(self.temp.name).resolve()
        self.assertTrue(self.project.is_relative_to(cache))
        (self.project / 'database').mkdir()
        self.config = configuration()

    def tearDown(self):
        self.temp.cleanup()

    def evidence(self, name, value):
        folder = ROOT / 'artifacts/reports/stage-1'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

    def pdf(self, name, texts=None):
        path = self.project / 'database' / name
        if texts is None:
            texts = [
                '1 Introduction\n' + 'Linked evidence explains local retrieval and graph paths.\n' * 12,
                'More evidence continues across pages.\n' * 8 + '\nReferences\n[1] Example reference title.\n',
                'Appendix A\n' + 'Additional implementation details and bounded experiment setup.\n' * 6,
            ]
        with pymupdf.open() as doc:
            for text in texts:
                page = doc.new_page()
                if text:
                    remaining = page.insert_textbox(pymupdf.Rect(40, 40, 550, 790), text, fontsize=10)
                    self.assertGreaterEqual(remaining, 0)
            doc.save(path)
        return {'candidate_id': name, 'relative_path': name, 'sha256': file_hash(path)}

    def parse(self, entry):
        return parse_document(self.project / 'database' / entry['relative_path'], entry['relative_path'], entry['sha256'], self.config)

    def batch(self, entries, config=None, force=False):
        manifest = {'manifest_version': 'test-v1', 'pilots': entries}
        with redirect_stdout(io.StringIO()):
            return ingest_batch(self.project, manifest, 'test-manifest-hash', config or self.config, force=force)

    def counts(self):
        with closing(sqlite3.connect(self.project / 'data/ingest.sqlite3')) as conn:
            return tuple(conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ('papers', 'parses', 'chunks'))

    def test_cross_page_offsets_references_and_complete_coverage(self):
        entry = self.pdf('normal.pdf')
        doc = self.parse(entry)
        self.assertEqual(audit_document(doc), len(doc['chunks']))
        self.assertTrue(any(c['page_start'] != c['page_end'] for c in doc['chunks']))
        references = [c for c in doc['chunks'] if c['content_kind'] == 'references']
        self.assertTrue(references)
        self.assertTrue(all(not c['relation_extraction_eligible'] for c in references))
        self.assertTrue(any(c['content_kind'] == 'appendix' for c in doc['chunks']))
        self.assertTrue(all(c['estimated_tokens'] <= 500 for c in doc['chunks']))

    def test_tampered_offset_is_rejected(self):
        doc = self.parse(self.pdf('offset.pdf'))
        doc['chunks'][0]['source_spans'][0]['start_char'] += 1
        with self.assertRaises(ValueError):
            audit_document(doc)

    def test_missing_reference_boundary_disables_relation_inputs(self):
        entry = self.pdf('no-refs.pdf', ['Only unstructured paragraphs without section names.\n' * 20])
        doc = self.parse(entry)
        self.assertIn('references_boundary_missing_all_relation_extraction_disabled', doc['warnings'])
        self.assertFalse(any(c['relation_extraction_eligible'] for c in doc['chunks']))

    def test_empty_and_short_text_are_distinct_failures(self):
        for name, texts, expected in [('empty.pdf', [''], 'empty_text'), ('short.pdf', ['Tiny text.'], 'text_too_short')]:
            with self.subTest(expected=expected):
                with self.assertRaises(ParseError) as error:
                    self.parse(self.pdf(name, texts))
                self.assertEqual(error.exception.code, expected)

    def test_reference_year_and_generic_label_do_not_reopen_body(self):
        entry = self.pdf('reference-boundaries.pdf', [
            '1 Introduction\n' + 'A repeatable paragraph with original evidence.\n' * 8,
            'References\nDoe, J.\n2021. FEVEROUS: Fact extraction and verification.\nMethod\n'
            + 'Further citation details remain in the reference area.\n' * 5,
            'A\nALGORITHM DETAILS\n' + 'Appendix content is distinct from citations.\n' * 8,
        ])
        doc = self.parse(entry)
        page_two = [c for c in doc['chunks'] if any(s['pdf_page'] == 2 for s in c['source_spans'])]
        self.assertTrue(page_two)
        self.assertTrue(all(c['content_kind'] == 'references' and not c['relation_extraction_eligible'] for c in page_two))
        self.assertTrue(any(c['content_kind'] == 'appendix' and c['relation_extraction_eligible'] for c in doc['chunks']))
        audit_document(doc)

    def test_source_and_processing_versions_change_identity(self):
        paper, parsed = identities('folder/a.pdf', 'a' * 64, self.config)
        config = {**self.config, 'parser_version': 'pdf-v2-test'}
        next_paper, next_parse = identities('folder/a.pdf', 'a' * 64, config)
        self.assertEqual(paper, next_paper)
        self.assertNotEqual(parsed, next_parse)
        self.assertNotEqual(paper, identities('folder/a.pdf', 'b' * 64, self.config)[0])
        self.assertNotEqual(paper, identities('other/a.pdf', 'a' * 64, self.config)[0])

    def test_idempotence_force_reparse_and_version_history(self):
        entry = self.pdf('stable.pdf')
        # Use the real parser in-process for repeated-state tests; the isolation test below uses real subprocesses.
        def local_worker(path, relative, digest, config, temp, timeout):
            doc = parse_document(path, relative, digest, config)
            temp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
            return doc
        with patch('papertech.ingest.worker', side_effect=local_worker):
            first = self.batch([entry])
            counts = self.counts()
            reuse = self.batch([entry])
            forced = self.batch([entry], force=True)
            self.assertEqual(reuse['task_counts'], {'reused': 1})
            self.assertEqual(self.counts(), counts)
            self.assertEqual(first['tasks'][0]['parse_id'], forced['tasks'][0]['parse_id'])
            newer = self.batch([entry], {**self.config, 'parser_version': 'pdf-v2-test'})
            self.assertNotEqual(first['tasks'][0]['parse_id'], newer['tasks'][0]['parse_id'])
            self.assertEqual(self.counts()[:2], (1, 2))
            changed = self.pdf('stable.pdf', ['A newly reviewed source revision.\n' * 20])
            updated = self.batch([changed])
            self.assertNotEqual(first['tasks'][0]['paper_id'], updated['tasks'][0]['paper_id'])
            self.assertEqual(self.counts()[:2], (2, 3))
            self.evidence('version-history-test.json', {
                'fixture': 'synthetic PDF; source changes are applied only inside a test directory',
                'first': first, 'cache_reuse': reuse, 'force_reparse': forced,
                'new_processing_version': newer, 'reviewed_new_source': updated,
                'final_papers_parses_chunks': self.counts(),
            })

    def test_real_worker_failure_does_not_block_following_paper(self):
        bad = self.project / 'database/broken.pdf'
        bad.write_bytes(b'not a PDF')
        bad_entry = {'candidate_id': 'broken', 'relative_path': 'broken.pdf', 'sha256': file_hash(bad)}
        good = self.pdf('after-failure.pdf')
        result = self.batch([bad_entry, good])
        self.assertEqual([t['status'] for t in result['tasks']], ['failed', 'degraded'])
        self.assertEqual(result['tasks'][0]['error_code'], 'pdf_parse_error')
        self.assertEqual(result['status'], 'completed_with_failures')
        failures = json.loads((self.project / 'artifacts/logs/ingest' / result['run_id'] / 'failure-queue.json').read_text(encoding='utf-8'))
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0]['error_summary'])
        counts = self.counts()
        retried = self.batch([bad_entry, good])
        self.assertEqual([t['status'] for t in retried['tasks']], ['failed', 'reused'])
        self.assertEqual(self.counts(), counts)
        self.evidence('failure-isolation-test.json', {
            'fixture': 'corrupt synthetic PDF followed by a readable synthetic PDF; real subprocess parser',
            'run': result, 'failure_queue': failures, 'retried_run': retried,
            'papers_parses_chunks_unchanged_on_retry': self.counts() == counts,
        })

    def test_worker_timeout_is_recorded_and_batch_continues(self):
        entries = [self.pdf('slow.pdf'), self.pdf('next.pdf')]
        with patch('papertech.ingest.worker', side_effect=ParseError('parse_timeout', 'Injected timeout')):
            result = self.batch(entries)
        self.assertEqual(result['task_counts'], {'failed': 2})
        self.assertTrue(all(t['error_code'] == 'parse_timeout' for t in result['tasks']))

    def test_frozen_source_mismatch_is_not_silently_imported(self):
        entry = self.pdf('changed.pdf')
        entry['sha256'] = '0' * 64
        result = self.batch([entry])
        self.assertEqual(result['tasks'][0]['error_code'], 'source_hash_mismatch')
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_interrupted_run_is_recovered_without_false_success(self):
        entry = self.pdf('interrupted.pdf')
        with patch('papertech.ingest.worker', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.batch([entry])
        with closing(sqlite3.connect(self.project / 'data/ingest.sqlite3')) as conn:
            self.assertEqual(conn.execute('SELECT status FROM tasks').fetchone()[0], 'running')
        result = self.batch([entry])
        with closing(sqlite3.connect(self.project / 'data/ingest.sqlite3')) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM runs WHERE status='interrupted'").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM tasks WHERE status='interrupted'").fetchone()[0], 1)
            interrupted = conn.execute("SELECT run_id,status,error_code,error_summary FROM tasks WHERE status='interrupted'").fetchall()
        self.assertEqual(result['status'], 'completed')
        self.evidence('interruption-recovery-test.json', {'interrupted_tasks': interrupted, 'recovery_run': result})


if __name__ == '__main__':
    unittest.main(verbosity=2)
