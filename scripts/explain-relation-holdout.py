"""Explain stage losses using saved rankings; optionally add LangSmith feedback."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.citations import prompt_evidence
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark, stable_id, write_json
from papertech.evidence_context import requested_groups, reserve_sources
from papertech.entity_aliases import is_comparison
from papertech.settings import settings


def replay_selection(row, chunks, budget=None, evidence_max=None, source_policy=None):
    original = row
    config = row.get('selection_config', {})
    budget = config.get('budget', 6000) if budget is None else budget
    evidence_max = config.get('evidence_max', 8) if evidence_max is None else evidence_max
    source_policy = config.get('source_policy', 'named_first') if source_policy is None else source_policy
    ranked = row['ranked']
    groups = requested_groups(row['question'], chunks)
    if source_policy == 'score_order' or (not is_comparison(row['question']) and len(groups) < 2):
        groups = []
    reserved, _ = reserve_sources(ranked,chunks,groups,budget,evidence_max=evidence_max)
    reserved_ids = {r['chunk_id'] for r in reserved}
    ordered = reserved + [r for r in ranked if r['chunk_id'] not in reserved_ids]
    selected, used, records = [], 0, {}
    ranks = {r['chunk_id']:i for i,r in enumerate(ranked,1)}
    for row in ordered:
        cid = row['chunk_id']
        c = chunks[cid]
        record = dict(chunk_id=cid, reranked_position=ranks[cid], rerank_score=row.get('rerank_score'),
            reserved_for_named_paper=cid in reserved_ids, budget_before=budget-used)
        if len(selected)==evidence_max:
            record.update(reason='evidence_count_cap',explanation=f'已选满{evidence_max}块，后续候选不再处理。')
        elif not c.get('source_spans') or not c.get('page_start') or not c.get('text'):
            record.update(reason='invalid_source_metadata',explanation='来源位置或原文不完整。')
        elif row.get('rerank_score',1) < .05:
            record.update(reason='reranker_threshold',explanation=f"重排分数{row['rerank_score']:.6f}低于0.05。")
        else:
            evidence = {k:c[k] for k in ('chunk_id','paper_id','parse_id','title','page_start','page_end','source_relative_path','source_spans')}
            evidence.update(quote=c['text'],retrieval_sources=row['sources'],rerank_score=row.get('rerank_score'))
            cost = len(json.dumps(prompt_evidence(evidence),ensure_ascii=False).encode())+80
            record['required_bytes']=cost
            if used+cost>budget:
                record.update(reason='context_byte_budget',explanation=f'完整来源需{cost}字节，轮到它时仅余{budget-used}字节，因预算被跳过。')
            else:
                selected.append(cid)
                used+=cost
                record.update(reason='selected',explanation='完整来源进入上下文。')
        records[cid]=record
    assert selected == [e['chunk_id'] for e in original['evidence']]
    assert used == original['retrieval_summary']['context_bytes']
    return records


def main():
    folder = Path(sys.argv[1])
    upload = '--upload' in sys.argv[2:]
    summary=json.loads((folder/'summary.json').read_text(encoding='utf8'))
    bench,digest,_=load_benchmark(ROOT,summary['benchmark'])
    _,_,chunks=load_corpus(ROOT)
    chunks={c['chunk_id']:c for c in chunks}
    cases={c['id']:c for c in bench['cases']}
    results=[]
    for row in summary['results']:
        decisions=replay_selection(row,chunks)
        facts=[]
        audit=row['retrieval_summary'].get('graph_audit',{})
        for fact in row['diagnosis']['facts']:
            detail=dict(unit_id=fact['unit_id'],required_fact=fact['required_fact'],stage_reason=fact['reason'],
                explanation=fact['explanation'],sources=[decisions[c] for c in fact['known_support_chunks'] if c in decisions])
            if row['arm']=='Graph-only' and fact['reason']!='covered':
                detail.update(matched_entities=[a['name'] for a in audit.get('anchors',[])],
                    globally_linked_support=fact['graph_global_matches'],
                    unbounded_two_hop_support=fact['graph_two_hop_matches'],
                    truncated_nodes=audit.get('degree_truncated',[]))
            elif fact['reason']=='retrieval_pool_miss':
                detail['channel_support_hits']={k:[r['chunk_id'] for r in rows if r['chunk_id'] in fact['known_support_chunks']]
                    for k,rows in row['candidate_channels'].items()}
            facts.append(detail)
        results.append(dict(case_id=row['case_id'],arm=row['arm'],category=row['category'],question=row['question'],
            trace_url=row['trace_url'],facts=facts,selection_replay_verified=True,
            interpretation='离线重放已保存候选的确定性选择逻辑；无重新召回、无模型调用、无金标改动。'))
    positive = [r for r in results if r['category']!='negative']
    losses = {a:dict(Counter(s['reason'] for r in positive if r['arm']==a for f in r['facts']
        if f['stage_reason']!='covered' for s in f['sources'])) for a in ('Graph-only','Hybrid')}
    output=dict(status='selection_replay_verified',benchmark_sha256=digest,results=results,source_drop_details=losses)
    write_json(folder/'stage-loss-analysis.json',output)
    page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>逐题检索阶段损失解释</title>',
        '<style>body{font:16px system-ui;max-width:1100px;margin:32px auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;padding:12px}details{margin:12px 0}</style>',
        '<h1>逐题检索阶段损失解释</h1><p>根据保存的候选与预算离线重放，核对每次证据选择完全一致。原文未截断；无模型重测。</p>',
        '<p><a href="dashboard.html">返回总体指标、图表与完整候选</a></p>']
    for cid,case in cases.items():
        page.append(f'<h2 id="{cid}">{cid} {html.escape(case["question"])}</h2>')
        for r in results:
            if r['case_id']!=cid:
                continue
            page.append(f'<h3>{r["arm"]}</h3>')
            for f in r['facts']:
                page.append('<p>'+html.escape(f['required_fact']+' → '+f['explanation'])+'</p>')
                for source in f['sources']:
                    page.append('<p>'+html.escape(f"重排第{source['reranked_position']}名："+source['explanation'])+'</p>')
            page.append('<details><summary>具体实体、来源、预算及评分</summary><pre>'+html.escape(json.dumps(r,ensure_ascii=False,indent=2))+'</pre></details>')
    (folder/'stage-loss-analysis.html').write_text('\n'.join(page)+'</html>',encoding='utf8')
    dashboard=folder/'dashboard.html'
    text=dashboard.read_text(encoding='utf8')
    if 'stage-loss-analysis.html' not in text:
        text=text.replace('<h1>', '<p><a href="stage-loss-analysis.html">逐题精确预算损失与阶段解释</a></p><h1>',1)
        dashboard.write_text(text,encoding='utf8')
    if upload:
        cfg=settings(ROOT)
        from langsmith import Client
        client=Client(api_key=cfg['LANGSMITH_API_KEY'],api_url=cfg['LANGSMITH_ENDPOINT'],auto_batch_tracing=False)
        payloads=[]
        for r in results:
            rid=stable_id(digest,summary['run_id'],r['case_id'],r['arm'])
            comment=json.dumps(r,ensure_ascii=False,indent=2)
            payloads.append(dict(run_id=rid,key='source_loss_detail',feedback_id=stable_id(rid,'source-loss-detail-v1'),
                value='all_sources_covered' if all(f['stage_reason']=='covered' for f in r['facts']) else 'source_gaps',comment=comment))
        feedback={str(f.id):f for f in client.list_feedback(run_ids=[p['run_id'] for p in payloads])}
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda p:client.create_feedback(**p),[p for p in payloads if p['feedback_id'] not in feedback]))
        found={str(f.id):f for f in client.list_feedback(run_ids=[p['run_id'] for p in payloads])}
        assert all(p['feedback_id'] in found and found[p['feedback_id']].comment==p['comment'] for p in payloads)
        output['langsmith_explanation_feedback_verified']=len(payloads)
        write_json(folder/'stage-loss-analysis.json',output)
        client.close()
    print(json.dumps(dict(results=len(results),selection_replays_verified=len(results),source_drop_details=losses,
        feedback_verified=output.get('langsmith_explanation_feedback_verified')),ensure_ascii=False))


if __name__=='__main__':
    main()
