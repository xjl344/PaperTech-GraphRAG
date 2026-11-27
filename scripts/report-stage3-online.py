"""Read local acceptance records and recheck current provenance without model calls."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus
from papertech.graph_store import GraphStore
from papertech.ingest import atomic_json
from papertech.settings import settings
from papertech.citations import validate_answer,prompt_evidence


def main():
    target=ROOT/'artifacts/reports/stage-3/online'
    summaries=sorted(target.glob('runs/*/summary.json'),key=lambda p:p.stat().st_mtime_ns)
    runs=[json.loads(p.read_text(encoding='utf-8')) for p in summaries]
    latest={}
    for run in runs:
        for result in run['results']:latest[result['case_id']]=result
    corpus,papers,chunks=load_corpus(ROOT)
    cmap={c['chunk_id']:c for c in chunks}
    cfg=settings(ROOT)
    checks=[]; graph=GraphStore(cfg,corpus)
    try:
        claims=graph.execute('''MATCH (cl:KGClaim {corpus_id:$corpus,review_status:'approved'})
            OPTIONAL MATCH (cl)-[:SUPPORTED_BY]->(c:Chunk)
            OPTIONAL MATCH (cl)-[:STATED_IN]->(p:Paper)
            RETURN properties(cl) AS claim,c.chunk_id AS source_chunk,p.paper_id AS source_paper''',corpus=corpus)
        errors=[]
        for row in claims:
            cl=row['claim']; chunk=cmap.get(row['source_chunk'])
            if not chunk or cl['chunk_id']!=row['source_chunk'] or cl['paper_id']!=row['source_paper'] or cl['paper_id']!=chunk['paper_id']:
                errors.append(cl['claim_id']);continue
            if cl['evidence_quote'] not in chunk['text'] or cl['parse_id']!=chunk['parse_id'] or cl['page_start']!=chunk['page_start'] or cl['page_end']!=chunk['page_end']:
                errors.append(cl['claim_id'])
        graph_counts=graph.execute('''MATCH ()-[r]->() WHERE r.corpus_id=$corpus AND r.review_status='approved'
            RETURN type(r) AS type,count(*) AS count''',corpus=corpus)
        version=graph.execute('CALL dbms.components() YIELD versions RETURN versions')
    finally:graph.close()
    for case_id,result in latest.items():
        selected={e['chunk_id']:e for e in result['evidence']}
        valid_sources=all(cid in cmap and e['quote'] in cmap[cid]['text'] and e['paper_id']==cmap[cid]['paper_id'] for cid,e in selected.items())
        paths_grounded=all(ev['chunk_id'] in selected and ev['quote'] in selected[ev['chunk_id']]['quote']
                           for p in result['generation_paths'] for ev in p['evidence'])
        # The validator accepts exact quotes too; recheck exported source choices as text.
        body=dict(answer=result['answer'],status=result['status'],citations=[dict(chunk_id=c['chunk_id'],quote=c['quote']) for c in result['citations']])
        validate_answer(json.dumps(body,ensure_ascii=False),result['evidence'])
        s=result['retrieval_summary']
        serialized=len(json.dumps([prompt_evidence(e) for e in result['evidence']],ensure_ascii=False).encode())+len(json.dumps(result['generation_paths'],ensure_ascii=False).encode())
        checks.append(dict(case_id=case_id,request_id=result['request_id'],status=result['status'],sources_valid=valid_sources,
            citations_valid=True,generation_paths_grounded=paths_grounded,paths=len(result['generation_paths']),
            context_bytes=s['context_bytes'],actual_evidence_and_paths_bytes=serialized,
            bounds_ok=len(result['evidence'])<=8 and s['candidate_count']<=40 and len(result['graph_paths'])<=40 and serialized<=6000,
            trace_url=result['trace_url'],wall_seconds=result['wall_seconds'],reranker=s['reranker']))
    attempts=[r for run in runs for r in run['results']]
    totals=dict(deepseek_calls=0,known_input_tokens=0,known_output_tokens=0,deepseek_unknown_calls=0,
                embedding_calls=0,embedding_unknown_calls=0,automatic_retries=0)
    for r in attempts:
        for call in r['provider_calls']:
            usage=json.loads(call['usage']) if call['usage'] else None
            if call['attempt']>1:totals['automatic_retries']+=1
            if call['provider']=='deepseek':
                totals['deepseek_calls']+=1
                if usage:
                    totals['known_input_tokens']+=usage.get('prompt_tokens',0)
                    totals['known_output_tokens']+=usage.get('completion_tokens',0)
                else:totals['deepseek_unknown_calls']+=1
            else:
                totals['embedding_calls']+=1
                if not usage:totals['embedding_unknown_calls']+=1
    # Report classifications for the original failed citations; never silently normalize them.
    audit=sqlite3.connect(ROOT/'data/rag.sqlite3')
    failed=[]
    for result in attempts:
        if result['status']!='citation_error':continue
        detail=audit.execute("SELECT detail FROM stages WHERE request_id=? AND name='generate'",(result['request_id'],)).fetchone()
        raw=json.loads(json.loads(detail[0])['raw'])
        allowed={e['chunk_id']:e['quote'] for e in result['evidence']}
        mismatches=[]
        for c in raw.get('citations',[]):
            text=allowed.get(c['chunk_id'],''); quote=c.get('quote','')
            if quote not in text:
                normalized=' '.join(quote.split()) in ' '.join(text.split())
                mismatches.append(dict(chunk_id=c['chunk_id'],reason='whitespace_retyped' if normalized else 'source_text_rewritten_or_wrong_selection'))
        failed.append(dict(request_id=result['request_id'],case_id=result['case_id'],mismatches=mismatches,
                           resolution='failed result retained; source-choice-v1 used on subsequent acceptance requests'))
    audit.close()
    secrets=[value for key,value in cfg.items() if value and len(value)>=8 and any(t in key for t in ('API_KEY','AUTH_TOKEN','PASSWORD','ACCOUNT_ID'))]
    scanpaths=list((ROOT/'src/papertech').glob('*.py'))+list((ROOT/'scripts').glob('*stage3*'))+list((ROOT/'tests').glob('test*.py'))
    scanpaths+=list(target.rglob('*.json'))+list(target.glob('*.log'))+[ROOT/n for n in ('README.md','plan.md','requirements.md','validation.md','PROJECT_CHARTER.md','.env.example')]
    leaks=[]
    for path in scanpaths:
        if path.is_file():
            text=path.read_text(encoding='utf-8-sig',errors='replace')
            if any(secret in text for secret in secrets):leaks.append(str(path.relative_to(ROOT)))
    code_paths=[p for p in (ROOT/'src/papertech').glob('*.py')]+[ROOT/'scripts/verify-stage3-online.py']
    versions={n:importlib.metadata.version(n) for n in ('neo4j','httpx','pydantic','langgraph','langsmith')}
    report=dict(corpus_id=corpus,papers=len(papers),chunks=len(chunks),source_hashes_unchanged=True,
        approved_claims=len(claims),claim_provenance_errors=errors,semantic_edges=graph_counts,neo4j_version=version,
        current_case_checks=checks,token_totals_all_attempts=totals,citation_failures=failed,
        langsmith_all_runs_verified=all(run['remote_verification']['verified'] for run in runs),
        source_runs=[str(p.relative_to(ROOT)) for p in summaries],versions=versions,
        current_code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths},
        snapshot_boundary='current code hashes, not a retroactive freeze of earlier requests; stage4 requires a pre-run full freeze',
        secret_scan=dict(files=len(scanpaths),files_with_matches=leaks))
    atomic_json(target/'verification.json',report)
    print(json.dumps({k:report[k] for k in ('papers','chunks','approved_claims','claim_provenance_errors','token_totals_all_attempts','langsmith_all_runs_verified','secret_scan')},ensure_ascii=False,indent=2))
    return 0 if not errors and not leaks and all(c['sources_valid'] and c['generation_paths_grounded'] and c['bounds_ok'] for c in checks) else 1


if __name__=='__main__':sys.exit(main())
