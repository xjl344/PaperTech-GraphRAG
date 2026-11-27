"""Real local integration verification; never calls a paid/cloud provider."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus, valid_vector
from papertech.graph_store import GraphStore
from papertech.ingest import atomic_json
from papertech.local_models import run_worker,vector_cache
from papertech.settings import settings
from papertech.workflow import Workflow


def main():
    cfg=settings(ROOT)
    if any(cfg.get(k) for k in ('DEEPSEEK_API_KEY','CLOUD_BGE_API_KEY','LANGSMITH_API_KEY')):
        raise RuntimeError('This offline acceptance runner requires blank cloud keys')
    corpus,papers,chunks=load_corpus(ROOT)
    metadata,vectors=vector_cache(ROOT)
    missing=[c['chunk_id'] for c in chunks if c['text_sha256'] not in vectors]
    if missing:
        raise RuntimeError(f'{len(missing)} current chunks still lack embeddings')
    for c in chunks:
        valid_vector(vectors[c['text_sha256']])
    graph=GraphStore(cfg,corpus)
    try:
        before=graph.inspect()
        started=time.monotonic()
        after=graph.build(papers,chunks,metadata,vectors)
        assert before['counts']==after['counts']
        counts=after['counts'][0]
        assert counts==dict(chunks=len(chunks),papers=len(papers))
        assert all(i['state']=='ONLINE' for i in after['indexes'])
        graph_check=dict(before=before,after=after,repeat_seconds=time.monotonic()-started)
        # Neo4j stores all current location fields and exactly 1024 numeric components.
        invalid=graph.execute('MATCH (c:Chunk) WHERE c.corpus_id=$corpus AND (size(c.embedding)<>1024 OR c.source_spans IS NULL OR c.source_relative_path IS NULL OR c.parse_id IS NULL) RETURN count(c) AS invalid',corpus=corpus)
        assert invalid[0]['invalid']==0
        relations=graph.execute('MATCH (:Paper)-[r:HAS_CHUNK]->(c:Chunk) WHERE c.corpus_id=$corpus RETURN count(r) AS source_edges',corpus=corpus)
        assert relations[0]['source_edges']==len(chunks)
    finally:
        graph.close()
    queries=[('HippoRAG 如何利用 Personalized PageRank 检索证据？','local',True),
             ('Think-on-Graph alternates graph retrieval and context retrieval','cloud',False),
             ('zzzxqvneverexisting71429','none',True)]
    requests=[]
    for question,mode,rerank in queries:
        workflow=Workflow(ROOT,cfg,query_mode=mode,rerank=rerank)
        try:
            started=time.monotonic()
            result=workflow.ask(question)
            result['verification_elapsed_seconds']=time.monotonic()-started
            atomic_json(ROOT/'artifacts/reports/stage-2/requests'/f"{result['request_id']}.json",result)
            summary=result['retrieval_summary']
            assert summary['candidate_count']<=40 and summary.get('evidence_count',0)<=8
            assert summary.get('context_bytes',0)<=6000
            assert result['graph_paths']==[] and result['trace_url'] is None
            assert result['status'] in ('evidence_only','refused'),result
            if mode=='local':
                assert summary['dense_hits']>0 and summary['fulltext_hits']>0
                assert result['evidence'] and any('Hippo' in e['title'] for e in result['evidence'])
                assert isinstance(summary['reranker'],dict),summary
            if mode=='cloud':
                assert summary['dense_hits']==0 and result['evidence']
            if mode=='none':
                assert result['status']=='refused'
            assert workflow.audit.conn.execute('SELECT count(*) FROM calls WHERE request_id=?',(result['request_id'],)).fetchone()[0]==0
            requests.append(dict(question=question,request_id=result['request_id'],status=result['status'],retrieval_summary=summary))
        finally:
            workflow.close()
    # Validate frozen manifest/source hashes again after inference and indexing.
    assert load_corpus(ROOT)[0]==corpus
    jars=ROOT/'.runtime/neo4j-community-5.26.12/lib'
    lucene=jars/'lucene-core-9.11.1.jar'
    scoring=dict(implementation='Neo4j full-text via Lucene; Lucene default BM25',analyzer='standard-no-stop-words',
                 lucene_version='9.11.1',fusion='RRF k=60; raw fulltext and cosine scores never directly compared',
                 fulltext_fields=['text','title'])
    if lucene.exists():
        with zipfile.ZipFile(lucene) as z:
            scoring['deployed_IndexSearcher_references_BM25Similarity']=b'BM25Similarity' in z.read('org/apache/lucene/search/IndexSearcher.class')
        scoring['lucene_jar_sha256']=hashlib.sha256(lucene.read_bytes()).hexdigest()
    report=dict(passed=True,scope='Real local integration, no real cloud requests',corpus_id=corpus,papers=len(papers),chunks=len(chunks),
                unique_text_vectors=len({c['text_sha256'] for c in chunks}),model=metadata,index=graph_check,
                source_edges=relations,invalid_locations_or_dimensions=invalid,requests=requests,scoring=scoring,
                pending=['Cloud bge-m3 compatibility/live API','DeepSeek live API/model parameters/usage/prices/billing','LangSmith real upload','Stage 3 human answer review and retrieval quality'])
    atomic_json(ROOT/'artifacts/reports/stage-2/verification.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
