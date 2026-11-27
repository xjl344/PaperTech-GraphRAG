"""Freeze candidates, apply explicit delegated reviews, and verify graph provenance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.graph_store import GraphStore
from papertech.ingest import atomic_json
from papertech.kg import KGLedger, utcnow
from papertech.settings import settings

DEST = ROOT / 'artifacts/reports/stage-3/delegated-review'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', choices=['prepare', 'show', 'apply', 'verify', 'report'])
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, default=50)
    parser.add_argument('--context', action='store_true')
    parser.add_argument('--indices', default='')
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    cfg = settings(ROOT)
    corpus_id, papers, chunks = load_corpus(ROOT)
    chunk_map = {c['chunk_id']: c for c in chunks}
    ledger = KGLedger(ROOT)
    try:
        if args.task == 'prepare':
            target = DEST / 'snapshot.json'
            if target.exists():
                raise ValueError('Review snapshot exists; refusing to overwrite')
            claims = ledger.list_claims(corpus_id, limit=2000)
            snapshot = dict(created_at=utcnow(), corpus_id=corpus_id,
                            reviewer='Codex', review_kind='ai_delegated',
                            policy_version='evidence-review-v1',
                            scope='All extracted candidates; source-grounded semantic review, not independent human validation',
                            claims=[dict(index=i, claim=c, source=chunk_map[c['chunk_id']])
                                    for i, c in enumerate(claims, 1)])
            atomic_json(target, snapshot)
            config = dict(langsmith_api_key_present=bool(cfg.get('LANGSMITH_API_KEY')),
                          langsmith_project=cfg.get('LANGSMITH_PROJECT') or 'papertech',
                          langsmith_endpoint=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com')
            atomic_json(DEST / 'monitoring-config-check.json', config)
            progress = ledger.progress()
            atomic_json(DEST / 'extraction-state.json', progress)
            print(json.dumps(dict(candidates=len(claims), states=dict(Counter(c['review_status'] for c in claims)),
                                  configuration=config), ensure_ascii=False))
        elif args.task == 'show':
            snapshot = json.loads((DEST / 'snapshot.json').read_text(encoding='utf-8'))
            selected = {int(i) for i in args.indices.split(',')} if args.indices else None
            seen_sources = set()
            for row in snapshot['claims']:
                if (row['index'] in selected) if selected else (args.start <= row['index'] <= args.end):
                    c = row['claim']
                    print(json.dumps(dict(i=row['index'], paper=c['paper_title'], page=c['page_start'],
                                          relation=[c['subject_type'], c['subject'], c['predicate'], c['object_type'], c['object']],
                                          kind=c['claim_kind'], quote=c['evidence_quote'],
                                          **({'source': row['source']['text']} if args.context and c['chunk_id'] not in seen_sources else {})), ensure_ascii=False))
                    seen_sources.add(c['chunk_id'])
        elif args.task == 'apply':
            snapshot = json.loads((DEST / 'snapshot.json').read_text(encoding='utf-8'))
            decisions = []
            for path in sorted(DEST.glob('decisions-*.tsv')):
                for line in path.read_text(encoding='utf-8').splitlines():
                    if not line.strip():
                        continue
                    index, decision, reason = line.split('|', 2)
                    decisions.append(dict(index=int(index), decision={'A':'approved','R':'rejected'}[decision], reason=reason))
            by_index = {d['index']: d for d in decisions}
            if len(by_index) != len(decisions) or set(by_index) != {r['index'] for r in snapshot['claims']}:
                raise ValueError('Decisions must cover every frozen candidate exactly once')
            atomic_json(DEST / 'decisions.json', decisions)
            # Validate the entire decision set before writing any status.
            current = {c['claim_id']: c for c in ledger.list_claims(corpus_id, limit=2000)}
            for row in snapshot['claims']:
                c, d = row['claim'], by_index[row['index']]
                if d['decision'] not in ('approved', 'rejected') or not d.get('reason'):
                    raise ValueError('Every decision requires a status and a specific reason')
                if c['corpus_id'] != corpus_id or current[c['claim_id']]['review_status'] not in ('pending', d['decision']):
                    raise ValueError('Corpus or existing decision changed since snapshot')
                source = chunk_map[c['chunk_id']]
                if c['evidence_quote'] not in source['text'] or c['parse_id'] != source['parse_id']:
                    raise ValueError('Review source no longer matches')
            graph = GraphStore(cfg, corpus_id)
            results = []
            try:
                graph.ensure_kg_schema()
                for row in snapshot['claims']:
                    c, d = row['claim'], by_index[row['index']]
                    note = 'AI delegated review by Codex; evidence-review-v1; ' + d['reason']
                    ledger.update_review(c['claim_id'], d['decision'], note)
                    result = dict(index=row['index'], claim_id=c['claim_id'], decision=d['decision'],
                                  reason=d['reason'], reviewed_at=utcnow(), reviewer='Codex', review_kind='ai_delegated')
                    if d['decision'] == 'approved':
                        fresh = dict(ledger.conn.execute('SELECT * FROM kg_claims WHERE claim_id=?', (c['claim_id'],)).fetchone())
                        try:
                            graph.write_kg_claim(fresh)
                            ledger.mark_graph_written(c['claim_id'])
                            result['graph_status'] = 'confirmed'
                        except Exception as exc:
                            result['graph_status'] = 'unconfirmed'
                            result['error_code'] = type(exc).__name__
                    else:
                        result['graph_status'] = 'excluded'
                    results.append(result)
                    atomic_json(DEST / 'review-results.json', results)
            finally:
                graph.close()
            print(json.dumps(dict(reviewed=len(results), decisions=dict(Counter(r['decision'] for r in results)),
                                  graph=dict(Counter(r['graph_status'] for r in results))), ensure_ascii=False))
        elif args.task == 'verify':
            graph = GraphStore(cfg, corpus_id)
            try:
                claims = ledger.list_claims(corpus_id, limit=2000)
                approved = [c for c in claims if c['review_status'] == 'approved']
                before = graph.execute('MATCH (c:KGClaim {corpus_id:$corpus}) RETURN c.claim_id AS id', corpus=corpus_id)
                if {r['id'] for r in before} != {c['claim_id'] for c in approved}:
                    raise ValueError('Neo4j claims differ from approved ledger set')
                # Real idempotence check: write approved claims a second time.
                for c in approved:
                    graph.write_kg_claim(c)
                counts = graph.execute('''MATCH (c:KGClaim {corpus_id:$corpus})
                    OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(s:Chunk)
                    OPTIONAL MATCH (c)-[:STATED_IN]->(p:Paper)
                    RETURN count(DISTINCT c) AS claims, count(DISTINCT s) AS sources,
                        sum(CASE WHEN s IS NULL OR p IS NULL OR s.paper_id<>p.paper_id
                            OR NOT s.text CONTAINS c.evidence_quote THEN 1 ELSE 0 END) AS bad_lineage,
                        sum(CASE WHEN coalesce(c.review_kind,'')<>'ai_delegated' OR c.reviewed_at IS NULL
                            OR coalesce(c.review_note,'')='' THEN 1 ELSE 0 END) AS missing_review_metadata''', corpus=corpus_id)
                edges = graph.execute('''MATCH ()-[r]->() WHERE r.corpus_id=$corpus AND r.claim_id IS NOT NULL
                    RETURN r.claim_id AS id, count(r) AS n''', corpus=corpus_id)
                if len(edges) != len(approved) or any(r['n'] != 1 for r in edges) or counts[0]['bad_lineage'] or counts[0]['missing_review_metadata']:
                    raise ValueError('Duplicate edges or invalid provenance')
                paths = graph.expand_graph([c['chunk_id'] for c in approved][:40])
                allowed = {c['claim_id'] for c in approved}
                if any(len(p['edges']) > 2 or any(e['claim_id'] not in allowed for e in p['edges']) for p in paths):
                    raise ValueError('Graph traversal crossed an unapproved claim or depth budget')
                report = dict(verified_at=utcnow(), corpus_id=corpus_id, ledger=dict(Counter(c['review_status'] for c in claims)),
                              lineage=counts, semantic_edges=len(edges), repeat_write='passed',
                              path_count=len(paths), paths=paths, graph=graph.inspect())
                atomic_json(DEST / 'verification.json', report)
                print(json.dumps({k:v for k,v in report.items() if k not in ('paths','graph')}, ensure_ascii=False))
            finally:
                graph.close()
        else:
            snapshot = json.loads((DEST / 'snapshot.json').read_text(encoding='utf-8'))
            results = json.loads((DEST / 'review-results.json').read_text(encoding='utf-8'))
            decisions = {r['index']: r for r in results}
            states = json.loads((DEST / 'extraction-state.json').read_text(encoding='utf-8'))
            run_id = states['run']['run_id']
            failures = [dict(row) for row in ledger.conn.execute(
                "SELECT chunk_id,paper_title,error_code,started_at,finished_at FROM kg_tasks WHERE run_id=? AND status='failed'",
                (run_id,))]
            approved = [r['claim'] for r in snapshot['claims'] if decisions[r['index']]['decision']=='approved']
            summary = dict(created_at=utcnow(), candidates=len(results),
                           decisions=dict(Counter(r['decision'] for r in results)),
                           approved_relations=dict(Counter(c['predicate'] for c in approved)),
                           approved_source_papers=len({c['paper_id'] for c in approved}),
                           failed_extractions=failures, review_kind='ai_delegated',
                           paper_counts=[dict(paper=p['title'], approved=sum(c['paper_id']==p['paper_id'] for c in approved),
                                              rejected=sum(row['claim']['paper_id']==p['paper_id'] and decisions[row['index']]['decision']=='rejected'
                                                           for row in snapshot['claims'])) for p in papers],
                           hashes={name:hashlib.sha256((DEST/name).read_bytes()).hexdigest()
                                   for name in ('snapshot.json','decisions.json','review-results.json')})
            atomic_json(DEST/'summary.json', summary)
            lines = ['# 阶段 3 委托审核逐条记录', '',
                     '审核人：Codex；类型：用户明确委托的 AI 语义审核；策略：evidence-review-v1。', '',
                     '这不是独立人工专家核验，也不是阶段 4 的答案评测。原始候选、引句和实体均未改写；',
                     '证据不完整或类型错误时拒绝原候选，不把审核结果反写成模型原始输出。', '',
                     '判据：主体归属准确、端点类型正确、关系方向正确、引句及上下文支持、保留配置/采样限制；',
                     '性能超过、调用技术、分类表或文字相似本身都不能证明技术继承。', '']
            for row in snapshot['claims']:
                c, d = row['claim'], decisions[row['index']]
                lines += [f"## {row['index']} · {'批准' if d['decision']=='approved' else '拒绝'}", '',
                          f"论文：{c['paper_title']}；PDF {c['page_start']}–{c['page_end']} 页。", '',
                          f"关系：{c['subject']} —{c['predicate']}→ {c['object']}", '',
                          f"Claim：`{c['claim_id']}`；Chunk：`{c['chunk_id']}`。", '',
                          '原文引句：', '', *['> '+part for part in c['evidence_quote'].splitlines()], '',
                          '决定理由：'+d['reason'], '']
            (DEST/'review-log.md').write_text('\n'.join(lines), encoding='utf-8')
            outbox = json.loads((DEST/'langsmith-outbox.json').read_text(encoding='utf-8'))
            forbidden = {'text','quote','evidence_quote','embedding','vector','api_key','password','authorization','subject','object'}
            def inspect_payload(value):
                if isinstance(value, dict):
                    if forbidden.intersection(k.casefold() for k in value):
                        raise ValueError('Trace metadata payload contains a forbidden field')
                    for child in value.values():
                        inspect_payload(child)
                elif isinstance(value, list):
                    for child in value:
                        inspect_payload(child)
            inspect_payload(outbox)
            scanned = list(DEST.glob('*.json')) + list(DEST.glob('*.md')) + list(DEST.glob('*.tsv'))
            secret_values = [str(v) for k,v in cfg.items() if v and len(str(v)) >= 8 and
                             any(word in k.upper() for word in ('KEY','PASSWORD','TOKEN','SECRET'))]
            for path in scanned:
                content = path.read_text(encoding='utf-8')
                if any(secret in content for secret in secret_values):
                    raise ValueError('A configured secret was detected in review artifacts')
            atomic_json(DEST/'safety-verification.json', dict(verified_at=utcnow(),
                        trace_metadata_only=True, configured_secret_matches=0, scanned_files=len(scanned)))
            print(json.dumps(summary, ensure_ascii=False))
    finally:
        ledger.close()


if __name__ == '__main__':
    main()
