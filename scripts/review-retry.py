"""Apply Codex's six explicit, source-grounded decisions from the scoped retry."""
import json
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.graph_store import GraphStore
from papertech.ingest import atomic_json
from papertech.kg import KGLedger
from papertech.settings import settings

DECISIONS = {
    'd2350719a4fcb3a21345ae6de3dbc06663edd674d5c0c3d9bd12979c8c628182': '第6页实验设置明确列出本文方法在 WebQSP 上评测；主体由论文标题和 our method 的上下文确定，关系方向正确。保留原端点中的文献括注，不推断别名已对齐。',
    '92fe432be0263da02d46697156e8def8e01a484fc0575e601a48c94c764dbaa8': '第6页实验设置明确列出本文方法在 QALD10-en 上评测，Usbeck 等括注对应数据集来源；不把该事实扩展为效果领先。保留原始端点。',
    'aa5d8832d286fec19f5aa77263e18175b203d50b079b82fc01b1f58739ea0cfd': '原文明确在 AdvHotpotQA 上评测，并说明它是 HotpotQA 的挑战子集；接纳对象仅为 AdvHotpotQA，不扩展为完整 HotpotQA。',
    '65ec672b2a88972a9ad9cfdb91c4ad5d5d7c0a2e7aac8df5732b48e22b65c481': '原文明确将 Zero-Shot RE 列为本文方法的 slot filling 评测数据集；实体类型、方向与原文一致，空格差异不改写端点。',
    '2091716a5266d9c67422ee7b6999ca3f2d919372399e2d7f9d9a5f7a059521b7': '原文明确将 FEVER 列为本文方法的事实验证评测数据集，后文说明其指标为 Accuracy；接纳评测关系，不推断性能。',
    '9862ae42f4dba2b44cb0f3564ed8bbac523753f89d7f7f5396b799d55c09d789': '原文明确将 Creak 列为本文方法的事实验证评测数据集，后文说明其指标为 Accuracy；主体归属及评测方向可由上下文支持。',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    corpus, _, chunks = load_corpus(ROOT)
    sources = {c['chunk_id']: c for c in chunks}
    ledger = KGLedger(ROOT)
    graph = GraphStore(settings(ROOT), corpus)
    destination = ROOT / 'artifacts/reports/stage-3/retry-diagnostics'
    target = destination / 'review-results.json'
    try:
        if args.verify_only:
            claims = [dict(ledger.conn.execute('SELECT * FROM kg_claims WHERE claim_id=?', (claim_id,)).fetchone()) for claim_id in DECISIONS]
            if not target.exists() or any(c['review_status'] != 'approved' or not c['graph_written'] for c in claims):
                raise ValueError('Expected completed review records')
            for claim in claims:
                graph.write_kg_claim(claim)
            actual = graph.execute('MATCH (c:KGClaim) WHERE c.claim_id IN $ids AND c.review_status=\'approved\' RETURN count(c) AS claims', ids=list(DECISIONS))
            edges = graph.execute('MATCH (:KGEntity)-[r:EVALUATED_ON]->(:KGEntity) WHERE r.claim_id IN $ids RETURN count(r) AS edges', ids=list(DECISIONS))
            if actual[0]['claims'] != 6 or edges[0]['edges'] != 6:
                raise ValueError('Graph verification mismatch')
            atomic_json(destination / 'review-verification.json', dict(approved=6, graph_claims=6, semantic_edges=6, repeat_write='passed'))
            print(json.dumps(dict(approved=6, graph_claims=6, repeat_write='passed')))
            return
        if target.exists():
            raise ValueError('Review results already exist; refusing to rewrite decisions')
        claims = [dict(ledger.conn.execute('SELECT * FROM kg_claims WHERE claim_id=?', (claim_id,)).fetchone()) for claim_id in DECISIONS]
        for claim in claims:
            source = sources[claim['chunk_id']]
            if claim['corpus_id'] != corpus or claim['review_status'] != 'pending' or claim['evidence_quote'] not in source['text'] or claim['parse_id'] != source['parse_id']:
                raise ValueError('Review source or decision changed')
        atomic_json(destination / 'review-snapshot.json', dict(claims=claims, source=sources[claims[0]['chunk_id']], decisions=DECISIONS))
        graph.ensure_kg_schema()
        results = []
        for claim in claims:
            note = 'AI delegated review by Codex; evidence-review-v1; ' + DECISIONS[claim['claim_id']]
            fresh = ledger.update_review(claim['claim_id'], 'approved', note)
            graph.write_kg_claim(fresh)
            ledger.mark_graph_written(claim['claim_id'])
            results.append(dict(claim_id=claim['claim_id'], decision='approved', reason=DECISIONS[claim['claim_id']],
                                reviewer='Codex', review_kind='ai_delegated', reviewed_at=fresh['reviewed_at'], graph_status='confirmed'))
            atomic_json(target, results)
        for claim in claims:
            row = ledger.conn.execute('SELECT * FROM kg_claims WHERE claim_id=?', (claim['claim_id'],)).fetchone()
            graph.write_kg_claim(dict(row))
        actual = graph.execute('MATCH (c:KGClaim) WHERE c.claim_id IN $ids RETURN count(c) AS claims', ids=list(DECISIONS))
        if actual[0]['claims'] != 6:
            raise ValueError('Graph verification mismatch')
        atomic_json(destination / 'review-verification.json', dict(approved=6, graph_claims=actual[0]['claims'], repeat_write='passed'))
        print(json.dumps(dict(approved=6, graph_claims=6, repeat_write='passed')))
    finally:
        graph.close()
        ledger.close()


if __name__ == '__main__':
    main()
