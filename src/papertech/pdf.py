"""Read-only PDF extraction and deterministic chunks. No network/model clients."""

import argparse
import hashlib
import importlib.metadata
import json
import re
import sys
from pathlib import Path


class ParseError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def stable_hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def configuration(version='pdf-v1.1', target=500):
    return {
        'parser_version': version, 'pymupdf_version': importlib.metadata.version('PyMuPDF'),
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'target_estimated_tokens': target, 'token_estimator': 'ascii-groups-of-4-and-unicode-char-v1',
        'sort_text': False, 'ocr': False, 'max_pages': 200, 'max_page_characters': 200000,
        'min_document_characters': 200, 'short_page_characters': 100,
    }


def identities(relative, source_hash, config):
    paper = 'paper_' + stable_hash({'path': relative.replace('\\', '/').casefold(), 'sha256': source_hash})[:32]
    parsed = 'parse_' + stable_hash({'paper_id': paper, 'config': config})[:32]
    return paper, parsed


def token_offsets(text):
    """Deterministic estimate, deliberately not a model tokenizer."""
    for match in re.finditer(r'[A-Za-z0-9_]+|[^\s]', text):
        value = match.group()
        width = 4 if value.isascii() and value[0].isalnum() else len(value)
        for start in range(match.start(), match.end(), max(width, 1)):
            yield start, min(start + max(width, 1), match.end())


def estimate_tokens(text):
    return sum(1 for _ in token_offsets(text))


KNOWN = re.compile(
    r'^(abstract|introduction|related works?|background|preliminaries|method(?:ology)?|'
    r'our (?:approach|method)|experiments?|results?(?: and discussion)?|discussion|'
    r'conclusions?|limitations|ethics statement|acknowledg(?:e)?ments?|references|bibliography|'
    r'supplementary(?: material)?|appendix(?:\s+[A-Z](?:\.\d+)?)?(?::\s+[A-Za-z ]+)?)$', re.I)
NUMBERED = re.compile(r'^[1-9]\d?(?:\.\d+)*\.?\s+[A-Z][A-Za-z0-9 ,:()/&\-–]{2,100}$')
APPENDIX = re.compile(r'^[A-Z](?:\.\d+)*\s+[A-Z][A-Z0-9 ,:()/&\-]{2,100}$')


def heading(line):
    label = line.strip()
    if not label or len(label) > 110 or len(label.split()) > 13:
        return None
    if KNOWN.fullmatch(label) or NUMBERED.fullmatch(label) or APPENDIX.fullmatch(label):
        normalized = re.sub(r'^\d+(?:\.\d+)*\.?\s+', '', label).strip().casefold()
        kind = 'references' if normalized in ('references', 'bibliography') else 'body'
        if normalized.startswith(('appendix', 'supplementary')) or APPENDIX.fullmatch(label):
            kind = 'appendix'
        return label, kind
    return None


def extract_pages(path, config):
    import pymupdf

    warnings = []
    pages = []
    try:
        with pymupdf.open(path) as doc:
            if doc.needs_pass:
                raise ParseError('password_required', 'PDF requires a password; no OCR or password guessing')
            if not 0 < len(doc) <= config['max_pages']:
                raise ParseError('page_budget', 'PDF outside the configured page-count budget')
            for number, page in enumerate(doc, 1):
                text = page.get_text('text', sort=False)
                if len(text) > config['max_page_characters']:
                    raise ParseError('page_text_budget', f'PDF page {number} exceeds text budget')
                if len(text.strip()) < config['short_page_characters']:
                    warnings.append(f'short_text_page:{number}')
                blocks = []
                cursor = 0
                for block in page.get_text('blocks', sort=False):
                    if len(block) > 6 and block[6] != 0:
                        continue
                    block_text = block[4]
                    start = text.find(block_text, cursor)
                    if start < 0:
                        warnings.append(f'block_geometry_unmapped:{number}')
                        continue
                    end = start + len(block_text)
                    blocks.append({'start_char': start, 'end_char': end,
                                   'bbox': [round(float(x), 3) for x in block[:4]]})
                    cursor = end
                pages.append({'pdf_page': number, 'text': text, 'text_sha256': text_hash(text),
                              'width': float(page.rect.width), 'height': float(page.rect.height), 'blocks': blocks})
    except ParseError:
        raise
    except Exception as exc:
        raise ParseError('pdf_parse_error', f'{type(exc).__name__}: {str(exc)[:350]}') from exc
    length = sum(len(p['text'].strip()) for p in pages)
    if length == 0:
        raise ParseError('empty_text', 'PDF contains no extracted text; OCR is not enabled')
    if length < config['min_document_characters']:
        raise ParseError('text_too_short', f'Extracted only {length} non-padding characters')
    return pages, warnings


def units_from_pages(pages, target):
    """Bounded text units split at heuristically detected headings and PDF blocks."""
    section, kind = 'unidentified', 'body'
    headings = []
    units = []
    for page in pages:
        text = page['text']
        events = {}
        cursor = 0
        lines = text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            found = heading(line)
            # Many papers typeset appendix labels and headings on separate lines.
            if re.fullmatch(r'[A-Z](?:\.\d+)*', line.strip()) and index + 1 < len(lines):
                title = lines[index + 1].strip()
                if 2 < len(title) <= 100 and title.isupper() and re.search(r'[A-Z]{3}', title):
                    found = (line.strip() + ' ' + title, 'appendix')
            if found:
                events[cursor] = found
            cursor += len(line)
        boundaries = {0, len(text), *events}
        for block in page['blocks']:
            boundaries.update((block['start_char'], block['end_char']))
        boundaries = sorted(boundaries)
        for start, end in zip(boundaries, boundaries[1:]):
            if start in events:
                next_section, next_kind = events[start]
                # References remain excluded until an explicit appendix/supplementary heading.
                # Generic labels and numbered/year-prefixed citation lines must not reopen body input.
                if kind != 'references' or next_kind in ('references', 'appendix'):
                    section = next_section
                    kind = 'appendix' if kind == 'appendix' and next_kind == 'body' else next_kind
                    headings.append({'pdf_page': page['pdf_page'], 'start_char': start,
                                     'label': section, 'kind': kind, 'detection': 'heuristic'})
            segment = text[start:end]
            tokens = list(token_offsets(segment))
            cuts = [0]
            for index in range(target, len(tokens), target):
                cuts.append(tokens[index][0])
            cuts.append(len(segment))
            for a, b in zip(cuts, cuts[1:]):
                if b > a:
                    units.append({'pdf_page': page['pdf_page'], 'start_char': start + a,
                                  'end_char': start + b, 'section': section, 'kind': kind})
    return units, headings


def make_chunks(pages, paper_id, parse_id, config):
    target = config['target_estimated_tokens']
    units, headings = units_from_pages(pages, target)
    has_references = any(h['kind'] == 'references' for h in headings)
    chunks, pending = [], []

    def flush():
        if not pending:
            return
        spans = []
        for unit in pending:
            if spans and spans[-1]['pdf_page'] == unit['pdf_page'] and spans[-1]['end_char'] == unit['start_char']:
                spans[-1]['end_char'] = unit['end_char']
            else:
                spans.append({k: unit[k] for k in ('pdf_page', 'start_char', 'end_char')})
        parts, offset = [], 0
        for span in spans:
            page = pages[span['pdf_page'] - 1]
            part = page['text'][span['start_char']:span['end_char']]
            span['chunk_start_char'] = offset
            span['chunk_end_char'] = offset + len(part)
            span['block_bboxes'] = [b['bbox'] for b in page['blocks']
                                   if b['start_char'] < span['end_char'] and b['end_char'] > span['start_char']]
            parts.append(part)
            offset += len(part) + 1
        text = '\n'.join(parts)
        if not text.strip():
            pending.clear()
            return
        digest = text_hash(text)
        identity_spans = [{k: s[k] for k in ('pdf_page', 'start_char', 'end_char')} for s in spans]
        chunk_id = 'chunk_' + stable_hash({'paper_id': paper_id, 'parse_id': parse_id,
                                         'spans': identity_spans, 'text_sha256': digest})[:32]
        chunks.append({'chunk_id': chunk_id, 'paper_id': paper_id, 'parse_id': parse_id,
                       'parser_version': config['parser_version'], 'ordinal': len(chunks),
                       'text': text, 'text_sha256': digest, 'source_spans': spans,
                       'page_start': spans[0]['pdf_page'], 'page_end': spans[-1]['pdf_page'],
                       'section': pending[0]['section'], 'section_detection': 'heuristic',
                       'content_kind': pending[0]['kind'],
                       'relation_extraction_eligible': has_references and pending[0]['kind'] != 'references',
                       'estimated_tokens': estimate_tokens(text), 'token_estimator': config['token_estimator']})
        pending.clear()

    for unit in units:
        if pending and (unit['section'], unit['kind']) != (pending[0]['section'], pending[0]['kind']):
            flush()
        pending_tokens = sum(estimate_tokens(pages[u['pdf_page'] - 1]['text'][u['start_char']:u['end_char']]) for u in pending)
        unit_tokens = estimate_tokens(pages[unit['pdf_page'] - 1]['text'][unit['start_char']:unit['end_char']])
        if pending and pending_tokens + unit_tokens > target:
            flush()
        pending.append(unit)
    flush()
    return chunks, headings, has_references


def parse_document(path, relative, source_hash, config):
    paper_id, parse_id = identities(relative, source_hash, config)
    pages, warnings = extract_pages(path, config)
    chunks, headings, has_references = make_chunks(pages, paper_id, parse_id, config)
    # Heuristic section boundaries are deliberately reported as degraded, never as verified structure.
    warnings.append('section_boundaries_heuristic')
    if not has_references:
        warnings.append('references_boundary_missing_all_relation_extraction_disabled')
    if len(headings) < 2:
        warnings.append('section_detection_unreliable_length_fallback')
    if not chunks:
        raise ParseError('no_chunks', 'No usable chunks after extraction')
    return {'schema_version': 1, 'paper_id': paper_id, 'parse_id': parse_id,
            'source_relative_path': relative, 'source_sha256': source_hash, 'config': config,
            'status': 'degraded' if warnings else 'success', 'warnings': sorted(set(warnings)),
            'geometry_granularity': 'PDF text block; character offsets refer to extracted page text',
            'page_count': len(pages), 'chunk_count': len(chunks), 'headings': headings,
            'pages': pages, 'chunks': chunks}


def audit_document(doc):
    paper_id, parse_id = identities(doc['source_relative_path'], doc['source_sha256'], doc['config'])
    if (paper_id, parse_id) != (doc['paper_id'], doc['parse_id']):
        raise ValueError('Document identity differs')
    if doc['page_count'] != len(doc['pages']) or doc['chunk_count'] != len(doc['chunks']):
        raise ValueError('Document counts differ')
    ids = set()
    coverage = {p['pdf_page']: [] for p in doc['pages']}
    for page in doc['pages']:
        if text_hash(page['text']) != page['text_sha256']:
            raise ValueError('Page hash differs')
    references_present = any(h['kind'] == 'references' for h in doc['headings'])
    for chunk in doc['chunks']:
        spans = chunk['source_spans']
        parts = []
        for span in spans:
            page = doc['pages'][span['pdf_page'] - 1]
            a, b = span['start_char'], span['end_char']
            if not 0 <= a < b <= len(page['text']):
                raise ValueError('Source range invalid')
            part = page['text'][a:b]
            if chunk['text'][span['chunk_start_char']:span['chunk_end_char']] != part:
                raise ValueError('Chunk offset differs')
            parts.append(part)
            coverage[span['pdf_page']].append((a, b))
        if '\n'.join(parts) != chunk['text'] or text_hash(chunk['text']) != chunk['text_sha256']:
            raise ValueError('Chunk text/hash differs')
        source_spans = [{k: s[k] for k in ('pdf_page', 'start_char', 'end_char')} for s in spans]
        expected = 'chunk_' + stable_hash({'paper_id': paper_id, 'parse_id': parse_id,
                                         'spans': source_spans, 'text_sha256': chunk['text_sha256']})[:32]
        if expected != chunk['chunk_id'] or expected in ids:
            raise ValueError('Chunk identity differs or duplicates')
        if (chunk['content_kind'] == 'references' or not references_present) and chunk['relation_extraction_eligible']:
            raise ValueError('References/uncertain reference region eligible for relation extraction')
        if chunk['estimated_tokens'] > doc['config']['target_estimated_tokens']:
            raise ValueError('Chunk exceeds estimated token budget')
        ids.add(expected)
    # All non-whitespace extracted text must be covered exactly once, including references.
    for page in doc['pages']:
        end = 0
        for a, b in sorted(coverage[page['pdf_page']]):
            if a < end or page['text'][end:a].strip():
                raise ValueError('Source text overlap or uncovered text')
            end = b
        if page['text'][end:].strip():
            raise ValueError('Uncovered page text')
    return len(ids)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('relative')
    parser.add_argument('source_hash')
    parser.add_argument('config_json')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        document = parse_document(args.source, args.relative, args.source_hash, json.loads(args.config_json))
        audit_document(document)
        args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as exc:
        print(json.dumps({'code': getattr(exc, 'code', 'worker_error'), 'message': str(exc)[:500]}, ensure_ascii=True))
        sys.exit(1)


if __name__ == '__main__':
    main()
