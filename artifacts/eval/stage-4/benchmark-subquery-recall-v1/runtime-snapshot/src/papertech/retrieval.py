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


def select_evidence(ranked, chunk_map, budget=6000, evidence_max=8):
    if isinstance(evidence_max, bool) or not isinstance(evidence_max, int) or not 1 <= evidence_max <= 40:
        raise ValueError('invalid_evidence_max')
    # UTF-8 byte length is a conservative upper bound for common byte BPE tokenizers.
    evidence, used = [], 0
    for row in ranked:
        c = chunk_map[row['chunk_id']]
        if not c.get('source_spans') or not c.get('page_start') or not c.get('text'):
            continue
        if 'rerank_score' in row and row['rerank_score'] < .05:
            continue
        e = {key:c[key] for key in ('chunk_id','paper_id','parse_id','title','page_start','page_end','source_relative_path','source_spans')}
        e.update(quote=c['text'], retrieval_sources=row['sources'], rerank_score=row.get('rerank_score'))
        cost = len(json.dumps(prompt_evidence(e),ensure_ascii=False).encode('utf-8')) + 80
        # Position geometry is exported locally but not sent to the LLM.
        e['context_bytes'] = cost
        if used + cost > budget:
            continue
        evidence.append(e)
        used += cost
        if len(evidence) == evidence_max:
            break
    return evidence, used
