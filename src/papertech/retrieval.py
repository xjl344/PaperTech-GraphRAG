"""Bounded RRF fusion and a clearly labelled offline diagnostic backend."""
import json
import math
import re
import unicodedata
from .citations import prompt_evidence


ALIASES = {'知识图谱':'knowledge graph', '多跳':'multi hop', '检索增强':'retrieval augmented',
           '幻觉':'hallucination', '海马':'HippoRAG', '图检索':'graph retrieval',
           '图谱':'knowledge graph', '基准':'benchmark'}


def normalize(question):
    question = ' '.join(unicodedata.normalize('NFKC', question).split())
    extra = [v for k,v in ALIASES.items() if k in question]
    return question + (' ' + ' '.join(extra) if extra else '')


def fuse(full, dense, graph=None):
    scores, sources = {}, {}
    for channel, rows in (('fulltext', full), ('dense', dense), ('graph', graph or [])):
        for rank, row in enumerate(rows[:20], 1):
            cid = row['chunk_id']
            scores[cid] = scores.get(cid, 0) + 1 / (60+rank)
            sources.setdefault(cid, []).append(dict(channel=channel, rank=rank, score=row['score']))
    return [dict(chunk_id=cid, score=score, sources=sources[cid]) for cid,score in sorted(scores.items(), key=lambda x:(-x[1],x[0]))][:40]


def offline_retrieve(chunks, vectors, question, vector=None):
    """Python BM25 diagnostic only; never described as Neo4j/Lucene verification."""
    tokenize = lambda text: re.findall(r'[a-z0-9]+', text.lower())
    terms = set(tokenize(question))
    docs = [tokenize(c['title']+' '+c['text']) for c in chunks]
    average = sum(map(len, docs)) / max(1,len(docs))
    freq = {term:sum(term in doc for doc in docs) for term in terms}
    full, dense = [], []
    for c, doc in zip(chunks, docs):
        score = 0
        for term in terms:
            n = doc.count(term)
            if n:
                score += math.log(1+(len(docs)-freq[term]+.5)/(freq[term]+.5)) * n*2.2/(n+1.2*(.25+.75*len(doc)/average))
        if score > 0:
            full.append(dict(chunk_id=c['chunk_id'], score=score))
        if vector and c['text_sha256'] in vectors:
            dense.append(dict(chunk_id=c['chunk_id'], score=sum(a*b for a,b in zip(vector,vectors[c['text_sha256']]))))
    return sorted(full,key=lambda x:-x['score'])[:20], sorted(dense,key=lambda x:-x['score'])[:20]


def contextual_text(chunk):
    """Read-only retrieval/rerank view with paper title and section; never mutates source text."""
    title = str(chunk.get('title') or '').strip()
    section = str(chunk.get('section') or 'unidentified').strip()
    text = chunk.get('text') or ''
    if not title:
        return text
    return f'Title: {title}\nSection: {section}\n\n{text}'


def rerank_view(chunk, contextual=True):
    """Return a shallow candidate payload for reranking without altering original spans."""
    if not contextual:
        return dict(chunk)
    return dict(chunk, text=contextual_text(chunk))


def chunk_windows(chunk, max_chars=700, overlap=250, max_windows=5, contextual=True):
    """Gold-free overlapping passage windows for fine-grained reranking of long chunks."""
    text = chunk.get('text') or ''
    title = str(chunk.get('title') or '').strip()
    section = str(chunk.get('section') or 'unidentified').strip()
    prefix = f'Title: {title}\nSection: {section}\n\n' if (contextual and title) else ''
    if len(text) <= max_chars + 100:
        return [dict(chunk_id=chunk.get('chunk_id'), window_index=0, start_char=0, end_char=len(text), text=prefix + text)]
    windows = []
    start = 0
    step = max(120, max_chars - overlap)
    while start < len(text) and len(windows) < max_windows:
        end = min(len(text), start + max_chars)
        if end < len(text):
            boundary = max(text.rfind('. ', start + max_chars // 2, end),
                           text.rfind('\n', start + max_chars // 2, end))
            if boundary > start:
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            windows.append(dict(chunk_id=chunk.get('chunk_id'), window_index=len(windows),
                                start_char=start, end_char=end, text=prefix + piece))
        if end >= len(text):
            break
        next_start = max(start + 100, end - overlap)
        if next_start <= start:
            next_start = start + step
        start = next_start
    return windows or [dict(chunk_id=chunk.get('chunk_id'), window_index=0, start_char=0, end_char=len(text), text=prefix + text)]


def _token_shingles(text):
    tokens = re.findall(r'[a-z0-9]{2,}', (text or '').casefold())
    if len(tokens) < 3:
        return set(tokens)
    return {(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)}


def lexical_jaccard(text_a, text_b):
    a, b = _token_shingles(text_a), _token_shingles(text_b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def select_evidence(ranked, chunk_map, budget=6000, evidence_max=8, min_score=0.05, score_policy='fixed',
                    reserved_ids=None, min_floor=0.01, relative_ratio=0.15, relative_floor=0.03,
                    max_per_paper=None, diversity_threshold=None):
    if isinstance(evidence_max, bool) or not isinstance(evidence_max, int) or not 1 <= evidence_max <= 40:
        raise ValueError('invalid_evidence_max')
    if score_policy not in ('fixed', 'relative'):
        raise ValueError('invalid_score_policy')
    if max_per_paper is not None and (isinstance(max_per_paper, bool) or not isinstance(max_per_paper, int) or max_per_paper < 1):
        raise ValueError('invalid_max_per_paper')
    scores = [row['rerank_score'] for row in ranked if 'rerank_score' in row]
    top1 = max(scores) if scores else None
    reserved = set(reserved_ids or ())
    # UTF-8 byte length is a conservative upper bound for common byte BPE tokenizers.
    evidence, used, per_paper = [], 0, {}
    deferred = []
    for row in ranked:
        c = chunk_map[row['chunk_id']]
        if not c.get('source_spans') or not c.get('page_start') or not c.get('text'):
            continue
        is_reserved = row['chunk_id'] in reserved
        low_score_reserved = False
        if 'rerank_score' in row:
            score = row['rerank_score']
            if score_policy == 'fixed':
                if score < min_score:
                    continue
            else:
                if score < min_floor:
                    continue
                if is_reserved:
                    low_score_reserved = score < min_score
                elif top1 is not None and score < max(relative_floor, relative_ratio * top1):
                    continue
        if max_per_paper is not None and not is_reserved and per_paper.get(c['paper_id'], 0) >= max_per_paper:
            continue
        if diversity_threshold is not None and not is_reserved:
            # Defer near-duplicate chunks from the same paper so distinct aspects fill slots first.
            same_paper = [ev['quote'] for ev in evidence if ev['paper_id'] == c['paper_id']]
            if same_paper and any(lexical_jaccard(c['text'], prev) >= diversity_threshold for prev in same_paper):
                deferred.append((row, low_score_reserved))
                continue
        e = {key:c[key] for key in ('chunk_id','paper_id','parse_id','title','page_start','page_end','source_relative_path','source_spans')}
        e.update(quote=c['text'], retrieval_sources=row['sources'], rerank_score=row.get('rerank_score'))
        if low_score_reserved:
            e['low_score_reserved'] = True
        cost = len(json.dumps(prompt_evidence(e),ensure_ascii=False).encode('utf-8')) + 80
        # Position geometry is exported locally but not sent to the LLM.
        e['context_bytes'] = cost
        if used + cost > budget:
            continue
        evidence.append(e)
        used += cost
        per_paper[c['paper_id']] = per_paper.get(c['paper_id'], 0) + 1
        if len(evidence) == evidence_max:
            break
    # If slots and budget still remain after preferring diverse blocks, backfill deferred items.
    if deferred and len(evidence) < evidence_max:
        for row, low_score_reserved in deferred:
            if len(evidence) == evidence_max:
                break
            c = chunk_map[row['chunk_id']]
            if max_per_paper is not None and per_paper.get(c['paper_id'], 0) >= max_per_paper:
                continue
            e = {key:c[key] for key in ('chunk_id','paper_id','parse_id','title','page_start','page_end','source_relative_path','source_spans')}
            e.update(quote=c['text'], retrieval_sources=row['sources'], rerank_score=row.get('rerank_score'))
            if low_score_reserved:
                e['low_score_reserved'] = True
            cost = len(json.dumps(prompt_evidence(e),ensure_ascii=False).encode('utf-8')) + 80
            e['context_bytes'] = cost
            if used + cost > budget:
                continue
            evidence.append(e)
            used += cost
            per_paper[c['paper_id']] = per_paper.get(c['paper_id'], 0) + 1
    return evidence, used
