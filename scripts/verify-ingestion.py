"""Independently verify frozen-source provenance, chunk locations and rerun stability."""

import importlib.util
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import pymupdf
from papertech.ingest import atomic_json, exclusive_lock, file_hash, now
from papertech.pdf import audit_document


def verify():
    output = ROOT / 'artifacts/reports/stage-1'
    output.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('freeze_pilot', ROOT / 'scripts/freeze-pilot.py')
    freeze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze)
    frozen = freeze.verify(ROOT / 'artifacts/exports/pilot-v1', 'pilot-v1')
    samples, paper_results, accepted = [], [], []
    montage = pymupdf.open()
    sheet = montage.new_page(width=1600, height=2100)
    with exclusive_lock(ROOT / '.cache/ingest.lock'), closing(sqlite3.connect(ROOT / 'data/ingest.sqlite3')) as conn:
        conn.row_factory = sqlite3.Row
        latest = conn.execute("SELECT * FROM runs WHERE status='completed' ORDER BY started_at DESC LIMIT 1").fetchone()
        if latest is None or latest['manifest_sha256'] != frozen['manifest_sha256']:
            raise ValueError('No completed ingestion of the frozen pilot manifest')
        runs = [dict(r) for r in conn.execute("SELECT * FROM runs WHERE status='completed' AND manifest_sha256=? AND config_json=? ORDER BY started_at",
                                              (latest['manifest_sha256'], latest['config_json']))]
        tasks = [dict(t) for t in conn.execute('SELECT * FROM tasks WHERE run_id=? ORDER BY ordinal', (latest['run_id'],))]
        if len(tasks) != 14 or any(t['status'] not in ('success', 'degraded', 'reused') for t in tasks):
            raise ValueError('Latest run does not have 14 accepted terminal task states')
        stable = len(runs) >= 2
        for run in runs:
            previous = [tuple(t) for t in conn.execute('SELECT candidate_id,paper_id,parse_id,page_count,chunk_count FROM tasks WHERE run_id=? ORDER BY ordinal', (run['run_id'],))]
            current = [(t['candidate_id'], t['paper_id'], t['parse_id'], t['page_count'], t['chunk_count']) for t in tasks]
            if previous != current:
                raise ValueError('Same source/config reruns have different identities or counts')
        references = cross_page = 0
        for index, task in enumerate(tasks):
            row = conn.execute('SELECT * FROM parses WHERE parse_id=?', (task['parse_id'],)).fetchone()
            if row is None:
                raise ValueError('Task has no committed parse result')
            artifact = (ROOT / row['artifact_path']).resolve()
            if not artifact.is_relative_to((ROOT / 'data/extracted').resolve()):
                raise ValueError('Artifact outside data/extracted')
            if file_hash(artifact) != row['artifact_sha256']:
                raise ValueError('Extraction artifact changed')
            doc = json.loads(artifact.read_text(encoding='utf-8'))
            audit_document(doc)
            if doc['parse_id'] != task['parse_id'] or doc['paper_id'] != task['paper_id']:
                raise ValueError('Task/document identities differ')
            actual_chunks = {tuple(r) for r in conn.execute('SELECT chunk_id,ordinal,text_sha256,page_start,page_end FROM chunks WHERE parse_id=?', (task['parse_id'],))}
            expected_chunks = {(c['chunk_id'], c['ordinal'], c['text_sha256'], c['page_start'], c['page_end']) for c in doc['chunks']}
            if actual_chunks != expected_chunks:
                raise ValueError('SQLite/file chunk records differ')
            source = (ROOT / 'database' / doc['source_relative_path']).resolve()
            if not source.is_relative_to((ROOT / 'database').resolve()) or file_hash(source) != doc['source_sha256']:
                raise ValueError('Source hash changed')
            if task['source_hash_before'] != task['source_hash_after'] or task['source_hash_before'] != doc['source_sha256']:
                raise ValueError('Task before/after hashes differ')
            body = next((c for c in doc['chunks'] if 'intro' in c['section'].lower()), doc['chunks'][0])
            chosen = [body]
            for predicate in (lambda c: c['page_end'] > c['page_start'], lambda c: c['content_kind'] == 'references'):
                sample = next((c for c in doc['chunks'] if predicate(c)), None)
                if sample and sample['chunk_id'] not in {c['chunk_id'] for c in chosen}:
                    chosen.append(sample)
            with pymupdf.open(source) as original:
                if len(original) != doc['page_count']:
                    raise ValueError('Original PDF page count differs')
                # Re-extract every source page independently; audit_document already checks every chunk span.
                for page, stored in zip(original, doc['pages']):
                    if page.get_text('text', sort=False) != stored['text']:
                        raise ValueError('Stored page text differs from a fresh PDF read')
                for chunk in chosen:
                    samples.append({'candidate_id': task['candidate_id'], 'paper_id': doc['paper_id'],
                                    'parse_id': doc['parse_id'], 'chunk_id': chunk['chunk_id'],
                                    'source_relative_path': doc['source_relative_path'],
                                    'source_spans': chunk['source_spans'], 'content_kind': chunk['content_kind'],
                                    'quote_prefix': chunk['text'][:350], 'result': 'exact_page_text_and_offsets_match'})
                page = original[body['source_spans'][0]['pdf_page'] - 1]
                boxes = body['source_spans'][0]['block_bboxes']
                for box in boxes:
                    annotation = page.add_rect_annot(pymupdf.Rect(box))
                    annotation.set_colors(stroke=(1, .5, 0))
                    annotation.set_border(width=.7)
                    annotation.update()
                pix = page.get_pixmap(matrix=pymupdf.Matrix(.8, .8), alpha=False)
                image_path = output / f"{task['candidate_id']}-location.png"
                pix.save(image_path)
                x, y = (index % 4) * 400, (index // 4) * 525
                sheet.insert_text((x + 5, y + 15), task['candidate_id'], fontsize=11)
                sheet.insert_image(pymupdf.Rect(x + 5, y + 22, x + 395, y + 520), stream=pix.tobytes('png'))
            if file_hash(source) != doc['source_sha256']:
                raise ValueError('Source changed during verification')
            reference_count = sum(c['content_kind'] == 'references' for c in doc['chunks'])
            cross_count = sum(c['page_end'] > c['page_start'] for c in doc['chunks'])
            references += reference_count
            cross_page += cross_count
            sizes = sorted(c['estimated_tokens'] for c in doc['chunks'])
            paper_results.append({'candidate_id': task['candidate_id'], 'paper_id': doc['paper_id'], 'parse_id': doc['parse_id'],
                                  'status': doc['status'], 'pages': doc['page_count'], 'chunks': doc['chunk_count'],
                                  'warnings': doc['warnings'], 'reference_chunks': reference_count,
                                  'cross_page_chunks': cross_count, 'sample_count': len(chosen),
                                  'max_estimated_tokens': max(sizes), 'median_estimated_tokens': sizes[len(sizes)//2],
                                  'source_hash_unchanged': True, 'all_chunk_ranges_verified': True})
            accepted.append({'candidate_id': task['candidate_id'], 'paper_id': doc['paper_id'], 'parse_id': doc['parse_id'],
                             'artifact_path': row['artifact_path'], 'artifact_sha256': row['artifact_sha256'],
                             'source_relative_path': doc['source_relative_path'], 'source_sha256': doc['source_sha256'],
                             'status': doc['status'], 'chunk_count': doc['chunk_count']})
        current_parse_ids = [t['parse_id'] for t in tasks]
        current_paper_ids = {t['paper_id'] for t in tasks}
        database_counts = {name: conn.execute(f'SELECT count(*) FROM {name}').fetchone()[0] for name in ('papers', 'parses', 'chunks')}
    sheet.get_pixmap().save(output / 'location-contact-sheet.png')
    montage.close()
    summary = {'verified_at': now(), 'status': 'passed' if stable else 'rerun_required',
               'manifest_version': 'pilot-v1', 'manifest_sha256': frozen['manifest_sha256'],
               'pilot_papers': len(current_paper_ids), 'current_parses': len(current_parse_ids),
               'pages': sum(p['pages'] for p in paper_results), 'chunks': sum(p['chunks'] for p in paper_results),
               'reference_chunks': references, 'cross_page_chunks': cross_page, 'location_samples': len(samples),
               'all_source_pages_freshly_verified': True, 'same_version_reruns_stable': stable,
               'matching_runs': [{'run_id': r['run_id'], 'started_at': r['started_at']} for r in runs],
               'database_counts_including_history': database_counts, 'papers': paper_results,
               'parser_config': json.loads(latest['config_json']),
               'scope': 'Exact page text and all character spans checked automatically; sampled page images rendered for visual review. Heuristic sections remain degraded.'}
    atomic_json(output / 'verification.json', summary)
    atomic_json(output / 'location-samples.json', samples)
    if stable:
        atomic_json(output / 'current-parses.json', {
            'manifest_version': 'pilot-v1', 'manifest_sha256': frozen['manifest_sha256'],
            'verified_run_id': latest['run_id'], 'parser_config': json.loads(latest['config_json']),
            'artifacts': accepted,
            'consumer_note': 'Use only these verified parses; earlier parser versions remain as audit history.',
        })
    print(json.dumps({k: v for k, v in summary.items() if k != 'papers'}, ensure_ascii=False, indent=2))
    if not stable:
        raise ValueError('Complete at least one same-version rerun before acceptance')


if __name__ == '__main__':
    verify()
