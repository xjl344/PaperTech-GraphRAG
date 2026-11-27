"""Local PDF preflight for pilot selection, not the stage-1 ingestion pipeline."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts/reports/stage-0-step-3'
CANDIDATES = [('Methods', n) for n in (15, 18, 24, 35, 59, 112, 181, 191, 209, 211, 215, 229)] + [('Surveys', 10), ('Resources', 2)]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def probe(path):
    import pymupdf

    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise ValueError('PDF requires a password')
        if not 0 < len(doc) <= 80:
            raise ValueError('PDF page count outside preflight budget (1..80)')
        pages = []
        for number, page in enumerate(doc, 1):
            # Coordinate sorting interleaves columns on these arXiv PDFs.
            text = page.get_text('text', sort=False)
            if len(text) > 200_000:
                raise ValueError('Page text exceeds preflight budget')
            pages.append({'pdf_page': number, 'characters': len(text), 'text': text})
        return {
            'page_count': len(doc),
            'total_characters': sum(p['characters'] for p in pages),
            'short_pages': [p['pdf_page'] for p in pages if len(p['text'].strip()) < 100],
            'pdf_metadata_title': doc.metadata.get('title', ''),
            'pages': pages,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe-one', type=Path)
    args = parser.parse_args()
    if args.probe_one:
        try:
            print(json.dumps(probe(args.probe_one), ensure_ascii=True))
        except Exception as exc:
            print(json.dumps({'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=True))
            sys.exit(1)
        return

    with (ROOT / 'database/papers_index.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = {(r['分类'], int(r['序号'])): r for r in csv.DictReader(stream)}
    with (ROOT / 'artifacts/reports/stage-0-step-2/manifest.csv').open(encoding='utf-8-sig', newline='') as stream:
        baseline = {r['relative_path']: r['sha256'] for r in csv.DictReader(stream)}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for category, number in CANDIDATES:
        row = rows[(category, number)]
        relative = f"{category}/{row['本地文件']}"
        path = ROOT / 'database' / relative
        record = {'candidate_id': f'{category}-{number:03d}', 'title': row['标题'], 'relative_path': relative, 'status': 'failed'}
        try:
            before = digest(path)
            record['sha256'] = before
            if before != baseline.get(relative):
                raise ValueError('Source differs from stage-0-step-2 hash baseline')
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), '--probe-one', str(path)],
                capture_output=True, text=True, encoding='utf-8', timeout=45,
            )
            if result.returncode != 0:
                raise RuntimeError((result.stdout or result.stderr)[-1200:])
            data = json.loads(result.stdout)
            after = digest(path)
            if after != before:
                raise ValueError('Source changed during probe')
            record.update({k: v for k, v in data.items() if k != 'pages'})
            record['source_hash_unchanged'] = True
            record['status'] = 'text_available' if data['total_characters'] >= 2000 else 'text_too_short'
            preview = OUTPUT / f"{record['candidate_id']}-preview.json"
            preview.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            record['preview_file'] = preview.name
        except Exception as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
        records.append(record)
        print(f"{record['candidate_id']}: {record['status']}", flush=True)
    summary = {
        'checked_at': datetime.now().astimezone().isoformat(),
        'python': sys.version,
        'pymupdf': importlib.metadata.version('PyMuPDF'),
        'text_extraction': 'get_text(text, sort=False); plain text preflight, not a layout fidelity guarantee',
        'scope': '14 title-screened candidates only; local text extraction without OCR, model calls or chunking',
        'limits': {'candidates': 14, 'pages_per_pdf': 80, 'seconds_per_pdf': 45, 'characters_per_page': 200000},
        'candidates': records,
    }
    (OUTPUT / 'candidate-checks.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    if any(r['status'] == 'failed' for r in records):
        sys.exit(1)


if __name__ == '__main__':
    main()
