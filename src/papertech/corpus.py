"""Load only the verified active parse set, never all historical SQLite chunks."""
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load_corpus(root):
    active_path = root / 'artifacts/reports/stage-1/current-parses.json'
    active = json.loads(active_path.read_text(encoding='utf-8'))
    manifest_path = root / 'artifacts/exports/pilot-v1/pilot-manifest.json'
    if digest(manifest_path) != active['manifest_sha256']:
        raise ValueError('Frozen manifest hash mismatch')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    titles = {p['candidate_id']: p['title'] for p in manifest['pilots']}
    papers, chunks, seen = [], [], set()
    for entry in active['artifacts']:
        path = (root / entry['artifact_path']).resolve()
        if not path.is_relative_to((root / 'data/extracted').resolve()):
            raise ValueError('Artifact path outside extraction root')
        if digest(path) != entry['artifact_sha256']:
            raise ValueError('Active artifact hash mismatch')
        source = (root / 'database' / entry['source_relative_path']).resolve()
        if not source.is_relative_to((root / 'database').resolve()):
            raise ValueError('Source path outside database')
        if digest(source) != entry['source_sha256']:
            raise ValueError('Source PDF changed')
        doc = json.loads(path.read_text(encoding='utf-8'))
        for key in ('paper_id', 'parse_id', 'source_sha256', 'source_relative_path'):
            if doc[key] != entry[key]:
                raise ValueError(f'Artifact identity mismatch: {key}')
        if len(doc['chunks']) != entry['chunk_count']:
            raise ValueError('Active chunk count mismatch')
        paper = dict(entry, title=titles[entry['candidate_id']])
        papers.append(paper)
        for c in doc['chunks']:
            if c['chunk_id'] in seen or c['paper_id'] != entry['paper_id'] or c['parse_id'] != entry['parse_id']:
                raise ValueError('Duplicate or foreign chunk')
            if hashlib.sha256(c['text'].encode()).hexdigest() != c['text_sha256']:
                raise ValueError('Chunk text hash mismatch')
            seen.add(c['chunk_id'])
            chunks.append(dict(c, title=paper['title'], source_relative_path=entry['source_relative_path']))
    corpus_id = hashlib.sha256(active_path.read_bytes()).hexdigest()[:20]
    return corpus_id, papers, chunks


def valid_vector(values):
    if len(values) != 1024 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
        raise ValueError('Embedding must contain 1024 finite numbers')
    norm = math.sqrt(sum(v*v for v in values))
    if norm < 1e-12:
        raise ValueError('Zero embedding')
    return [v/norm for v in values]
