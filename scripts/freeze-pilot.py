"""Freeze a pilot snapshot, or verify an existing snapshot without modifying it."""

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'artifacts/exports'
SELECTION = ROOT / 'artifacts/reports/stage-0-step-3'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def within(base, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f'Invalid relative path: {relative}')
    target = (base / path).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f'Path outside allowed root: {relative}')
    return target


def read_json(data):
    return json.loads(data.decode('utf-8-sig'))


def source_digest(relative):
    with within(ROOT / 'database', relative).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_pilots(pilots, previews, baseline):
    if len(pilots) != 14:
        raise ValueError('Expected the approved 14-paper scope')
    for field in ('candidate_id', 'relative_path', 'sha256'):
        if len({p[field] for p in pilots}) != len(pilots):
            raise ValueError(f'Duplicate pilot {field}')
    for pilot in pilots:
        ident = pilot['candidate_id']
        if not pilot.get('reason', '').strip() or pilot['status'] != 'text_available':
            raise ValueError(f'Missing selection reason or preflight not passed: {ident}')
        if baseline.get(pilot['relative_path']) != pilot['sha256']:
            raise ValueError(f'Inventory hash differs: {ident}')
        if source_digest(pilot['relative_path']) != pilot['sha256']:
            raise ValueError(f'Source hash differs: {ident}')
        preview = read_json(previews[pilot['preview_file']])
        if preview['page_count'] != pilot['page_count'] or len(preview['pages']) != pilot['page_count']:
            raise ValueError(f'Preview page count differs: {ident}')
        evidence = pilot['selection_evidence']
        page = preview['pages'][evidence['pdf_page'] - 1]
        start, end = evidence['start_char'], evidence['end_char']
        if not 0 <= start < end <= len(page['text']):
            raise ValueError(f'Invalid evidence range: {ident}')
        if page['text'][start:end] != evidence['quote']:
            raise ValueError(f'Evidence quote differs: {ident}')


def baseline_from(data):
    return {r['relative_path']: r['sha256'] for r in csv.DictReader(io.StringIO(data.decode('utf-8-sig')))}


def freeze(target, version):
    if target.exists():
        raise FileExistsError(f'Snapshot already exists; use --verify-only: {target}')
    files = {}
    originals = {
        'selection.json': SELECTION / 'pilot-selection.json',
        'selection.csv': SELECTION / 'pilot-selection.csv',
        'selection-notes.json': SELECTION / 'pilot-notes.json',
        'selection-report.md': SELECTION / 'report.md',
        'candidate-checks.json': SELECTION / 'candidate-checks.json',
        'environment-freeze.txt': SELECTION / 'environment-freeze.txt',
        'corpus-manifest.csv': ROOT / 'artifacts/reports/stage-0-step-2/manifest.csv',
        'corpus-summary.json': ROOT / 'artifacts/reports/stage-0-step-2/summary.json',
        'requirements-pdf.txt': ROOT / 'requirements-pdf.txt',
        'probe-pilot.py': ROOT / 'scripts/probe-pilot.py',
        'build-pilot-list.py': ROOT / 'scripts/build-pilot-list.py',
        'freeze-pilot.py': Path(__file__).resolve(),
    }
    for name, path in originals.items():
        files[f'inputs/{name}'] = path.read_bytes()
    selection = read_json(files['inputs/selection.json'])
    pilots = selection['pilots']
    if selection['count'] != len(pilots):
        raise ValueError('Selection count differs')
    baseline = baseline_from(files['inputs/corpus-manifest.csv'])
    previews = {}
    for pilot in pilots:
        name = pilot['preview_file']
        previews[name] = within(SELECTION, name).read_bytes()
        files[f'evidence/previews/{name}'] = previews[name]
    validate_pilots(pilots, previews, baseline)
    selected_paths = {p['relative_path'] for p in pilots}
    fingerprint = sha(encoded(sorted((p['relative_path'], p['sha256']) for p in pilots)))
    manifest = {
        'schema_version': 1,
        'manifest_version': version,
        'frozen_at': datetime.now().astimezone().isoformat(),
        'status': 'frozen_selection',
        'topic': selection['topic'],
        'decision': selection['decision'],
        'count': len(pilots),
        'total_pdf_pages': sum(p['page_count'] for p in pilots),
        'corpus_fingerprint_sha256': fingerprint,
        'source_root': 'database (relative to project root)',
        'python_at_freeze': sys.version,
        'provenance': {f'inputs/{name}': path.relative_to(ROOT).as_posix() for name, path in originals.items()},
        'evidence_previews_root': 'evidence/previews',
        'scope_note': 'Selection and preflight only; no stable chunks, index, QA evaluation or semantic relationship acceptance.',
        'pilots': pilots,
    }
    files['pilot-manifest.json'] = encoded(manifest)
    excluded = [{'relative_path': path, 'sha256': digest, 'reason': 'Outside this topic-focused preflight; not assessed as failed or low quality'}
                for path, digest in sorted(baseline.items()) if path.lower().endswith('.pdf') and path not in selected_paths]
    files['excluded-files.json'] = encoded(excluded)
    table = io.StringIO(newline='')
    columns = ['candidate_id', 'name', 'role', 'title', 'relative_path', 'sha256', 'page_count', 'reason', 'title_note']
    writer = csv.DictWriter(table, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(pilots)
    files['pilot-manifest.csv'] = table.getvalue().encode('utf-8-sig')
    files['checksums.json'] = encoded({name: sha(data) for name, data in sorted(files.items())})
    # Stage in the same parent and publish by directory rename only after every write succeeds.
    EXPORTS.mkdir(parents=True, exist_ok=True)
    staging = EXPORTS / f'.{version}.pending-{uuid.uuid4().hex}'
    staging.mkdir()
    for relative, data in files.items():
        path = within(staging, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    # Recheck sources immediately before publication; failed staging remains for diagnosis.
    validate_pilots(pilots, previews, baseline)
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite snapshot: {target}')
    staging.rename(target)


def verify(target, version):
    checksums = read_json((target / 'checksums.json').read_bytes())
    actual = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
    if actual != set(checksums) | {'checksums.json'}:
        raise ValueError('Snapshot contains missing or unexpected files')
    for relative, expected in checksums.items():
        if sha(within(target, relative).read_bytes()) != expected:
            raise ValueError(f'Snapshot checksum differs: {relative}')
    manifest_bytes = (target / 'pilot-manifest.json').read_bytes()
    manifest = read_json(manifest_bytes)
    if manifest['manifest_version'] != version or manifest['status'] != 'frozen_selection':
        raise ValueError('Snapshot version or status differs')
    pilots = manifest['pilots']
    if manifest['count'] != len(pilots):
        raise ValueError('Manifest count differs')
    previews = {p['preview_file']: within(target / 'evidence/previews', p['preview_file']).read_bytes() for p in pilots}
    baseline = baseline_from((target / 'inputs/corpus-manifest.csv').read_bytes())
    validate_pilots(pilots, previews, baseline)
    expected_fingerprint = sha(encoded(sorted((p['relative_path'], p['sha256']) for p in pilots)))
    if manifest['corpus_fingerprint_sha256'] != expected_fingerprint:
        raise ValueError('Corpus fingerprint differs')
    return {
        'status': 'passed',
        'verified_at': datetime.now().astimezone().isoformat(),
        'manifest_version': version,
        'manifest_sha256': sha(manifest_bytes),
        'corpus_fingerprint_sha256': expected_fingerprint,
        'pilot_count': len(pilots),
        'snapshot_files_verified': len(checksums),
        'source_hashes_verified': len(pilots),
        'selection_evidence_ranges_verified': len(pilots),
        'source_root': str(ROOT / 'database'),
        'verification_scope': 'Snapshot byte integrity, exact selection evidence offsets, baseline/current PDF hashes; no stage-1 ingestion acceptance.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='pilot-v1')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'pilot-v[1-9][0-9]*', args.version):
        parser.error('Version must be pilot-v followed by a positive integer')
    target = EXPORTS / args.version
    if not args.verify_only:
        freeze(target, args.version)
    print(json.dumps(verify(target, args.version), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
