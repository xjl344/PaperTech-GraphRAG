"""Independently verify saved recall results and explain each source transition.

No retrieval or model execution. --sync-review uploads deterministic explanation
feedback to the existing experiments, with readback; safe to resume.
"""
import argparse
from collections import Counter
import html
import json
import math
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import load_benchmark,stable_id,write_json
from papertech.settings import settings
from papertech.subquery_recall_diagnostic import VERSION,ARMS,read,RecallDataset,report


def verify(folder):
    s=read(folder/'summary.json');bench,digest,_=load_benchmark(ROOT,VERSION)
    assert s['status']=='completed' and s['benchmark_sha256']==digest
    assert len(s['results'])==48
    expected={(c['id'],a) for c in bench['cases'] for a in ARMS}
    assert {(r['case_id'],r['arm']) for r in s['results']}==expected
    units=bench['units'];cases={c['id']:c for c in bench['cases']}
    for row in s['results']:
        cid=row['case_id'];case=cases[cid]
        assert row['question']==case['question']
        assert row['historical_baseline_check']['same_candidate_set']
        assert row['rerank_pairs']==row['generation_calls']==0
        plan=bench['query_plans'][cid]
        texts=[case['question']]+([] if row['arm']=='Original' else [q['text'] for q in plan['subqueries']])
        assert [q['text'] for q in row['queries']]==texts
        # Reconstruct discovery stream independently, without invoking tested merger.
        stream=[];provenance={}
        for rank in range(1,21):
            for q in row['queries']:
                for channel in ['fulltext','dense']:
                    if len(q['channels'][channel])<rank:continue
                    hit=q['channels'][channel][rank-1];chunk=hit['chunk_id']
                    if chunk not in provenance:stream.append(chunk);provenance[chunk]=[]
                    provenance[chunk].append(dict(query_id=q['id'],channel=channel,rank=rank,score=hit['score']))
        assert [c['chunk_id'] for c in row['candidates']]==stream
        assert len(stream)==len(set(stream))
        for i,candidate in enumerate(row['candidates'],1):
            assert candidate['merged_rank']==i and candidate['retained']==(i<=40)
            assert candidate['discoveries']==provenance[candidate['chunk_id']]
            assert candidate['found_by']==list(dict.fromkeys(x['query_id'] for x in candidate['discoveries']))
        union=set(stream);kept=set(stream[:40]);facts={f['unit_id']:f for f in row['facts']}
        hits=retained=0
        for uid in case['units']:
            pool=set(units[uid]['known_support_chunks']);f=facts[uid]
            assert f['union_hit']==bool(union&pool) and f['retained']==bool(kept&pool)
            assert {m['chunk_id'] for m in f['matches']}==union&pool
            hits+=bool(union&pool);retained+=bool(kept&pool)
        assert math.isclose(row['metrics']['union_coverage'],hits/len(case['units']))
        assert math.isclose(row['metrics']['cap40_coverage'],retained/len(case['units']))
        if plan['route']=='fallback':
            assert len(row['queries'])==1
    assert sum(len(c['units']) for c in bench['cases'])==49
    assert s['embedding']['new_text_count']==57 and s['embedding']['provider_attempts']==1
    return s,bench,digest


def explain(s,bench):
    results=[];grouped={}
    for row in s['results']:grouped.setdefault(row['case_id'],{})[row['arm']]=row
    for case in bench['cases']:
        cid=case['id'];b,e=grouped[cid]['Original'],grouped[cid]['Expanded']
        before={f['unit_id']:f for f in b['facts']};items=[]
        for f in e['facts']:
            uid=f['unit_id'];old=before[uid]
            new_queries=[d for m in f['matches'] for d in m['discoveries'] if d['query_id']!='Q0']
            origins='；'.join(dict.fromkeys(f'{d["query_id"]} 的 {d["channel"]} 第{d["rank"]}名' for d in new_queries))
            ranks='、'.join(str(m['merged_rank']) for m in f['matches'])
            if old['retained'] and not f['retained']:
                kind='lost_baseline_source'
                message=f'基线已命中；扩展并集仍命中，但轮转合并第{ranks}名，超过40条上限，被截掉。'
            elif not old['union_hit'] and f['retained']:
                kind='recovered_and_retained'
                message=f'基线漏召回；由{origins}补回，合并第{ranks}名，保留在40条内。'
            elif not old['union_hit'] and f['union_hit']:
                kind='recovered_but_capped'
                message=f'基线漏召回；由{origins}补回，合并第{ranks}名，仍被40条上限截掉。'
            elif not f['union_hit']:
                kind='still_upstream_missing'
                message='所有已执行查询的全文Top20和向量Top20均未命中冻结支持池；不是重排或上下文预算丢弃。'
                if e['route']=='fallback':message+='本题分流校验失败，只有原问题召回，没有运行子查询。'
            else:
                kind='baseline_source_retained'
                message=f'基线已经命中，扩展后合并第{ranks}名仍在40条内；本来源没有新增覆盖收益。'
            items.append(dict(unit_id=uid,paper=bench['units'][uid]['title'],required_fact=f['required_fact'],
                kind=kind,explanation=message,baseline_hit=old['union_hit'],expanded_union_hit=f['union_hit'],
                expanded_cap40_hit=f['retained'],matches=f['matches']))
        notes=[]
        if cid=='R19':notes.append('冻结规则查询漏掉G-Retriever，误以LLM为主语。本题必要来源由保留的原题覆盖，持平不能证明该拆分正确。')
        if cid=='R08':notes.append('ToG-2 的必要来源实际由 STaRK 子查询 SQ02 找到；发现通道不等于论文/子查询归属，后续重排不能假定二者相同。')
        if cid=='R24':notes.append('题目覆盖率1/3持平，但S01新增、S03丢失；严格的逐来源无退化条件未满足。')
        results.append(dict(case_id=cid,question=case['question'],route=e['route'],notes=notes,sources=items,
            original_queries=[dict(id=q['id'],text=q['text']) for q in e['queries']],
            baseline=b['metrics'],expanded=e['metrics']))
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('summary',type=Path)
    parser.add_argument('--sync-review',action='store_true')
    args=parser.parse_args();folder=args.summary.parent
    s,bench,digest=verify(folder);reviews=explain(s,bench)
    transitions=dict(Counter(f['kind'] for r in reviews for f in r['sources']))
    latency={a:dict(p50=statistics.median(vals),p95=sorted(vals)[math.ceil(.95*len(vals))-1],
        total=sum(vals),count=len(vals)) for a in ARMS
        if (vals:=[r['retrieval_seconds'] for r in s['results'] if r['arm']==a])}
    data=dict(validation='48 rows, 49 sources per arm, exact historical baseline sets, independent channel/provenance/coverage recomputation passed',
        source_transitions=transitions,latency=latency,results=reviews,
        conclusion='子查询对上游召回有开发集增益；40候选截断损失5个并集来源，其中含1个基线已有来源。不自动接入生产，不声称最终答案收益。')
    write_json(folder/'source-review.json',data)
    links=read(folder/'experiment-trace-links.json') if (folder/'experiment-trace-links.json').exists() else {}
    def esc(text):return html.escape(str(text))
    chunks=['<!doctype html><meta charset="utf-8"><title>逐题召回原因</title><style>body{max-width:1150px;margin:30px auto;font:16px system-ui;line-height:1.65}table{border-collapse:collapse}th,td{border:1px solid #ccc;padding:10px;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#2563eb}</style>',
        '<h1>24题：子查询是否帮助检索召回</h1><p><a href="index.html">完整总览、柱状图、全部候选原文与Trace</a></p>',
        '<p>同样最多40条候选：逐题平均来源覆盖59.72% → 68.06%，29/49 → 33/49。全部并集：77.78%，38/49。两种口径检索都调用81次，基线24次；同候选上限不等于同检索成本。</p>',
        '<p>只检查必要来源是否进入候选池。未执行重排、证据组装或答案生成；题目均已曝光，不是泛化验收。</p>',
        '<pre>'+esc(json.dumps(dict(source_transitions=transitions,latency=latency),ensure_ascii=False,indent=2))+'</pre>']
    md=['# 24题子查询召回：逐题来源原因','',data['conclusion'],'',
        '逐题平均覆盖：59.72% → 同40条68.06% / 全并集77.78%。完整结果与原文见 index.html。','']
    for review in reviews:
        cid=review['case_id'];md.extend([f'## {cid}（{review["route"]}）','',review['question'],''])
        chunks.append(f'<h2 id="{cid}">{cid}（{review["route"]}）</h2><p>{esc(review["question"])}</p>')
        for arm in ARMS:
            url=links.get(stable_id(digest,s['run_id'],cid,arm))
            if url:chunks.append(f'<a href="{esc(url)}">{arm} Trace</a> ')
        for note in review['notes']:chunks.append('<p><strong>'+esc(note)+'</strong></p>');md.extend([note,''])
        chunks.append('<table><tr><th>必要来源</th><th>对应事实</th><th>原因</th></tr>')
        for f in review['sources']:
            chunks.append(f'<tr><td>{esc(f["unit_id"])}</td><td>{esc(f["required_fact"])}</td><td>{esc(f["explanation"])}</td></tr>')
            md.append(f'- **{f["unit_id"]}**：{f["explanation"]}')
        chunks.append('</table><details><summary>本题原问题与子查询</summary><pre>'+esc(json.dumps(review['original_queries'],ensure_ascii=False,indent=2))+'</pre></details>')
        md.append('')
    (folder/'source-review.html').write_text(''.join(chunks),encoding='utf8')
    (folder/'source-review.md').write_text('\n'.join(md)+'\n',encoding='utf8')
    if args.sync_review:
        rec=RecallDataset(ROOT,VERSION)
        try:
            client=rec.connect();status=read(folder/'langsmith-status.json')
            assert status['status']=='experiments_verified'
            jobs=[]
            for arm in ARMS:
                project=next(p for p in status['experiments'] if p['arm']==arm)
                ids=[stable_id(digest,s['run_id'],r['case_id'],arm) for r in reviews]
                existing={str(f.id):f for f in client.list_feedback(run_ids=ids)}
                for review,rid in zip(reviews,ids):
                    fid=stable_id(rid,'recall_source_explanation_v1')
                    comment=json.dumps(dict(origin='deterministic source-stage diagnosis, not semantic scoring',
                        **review),ensure_ascii=False)
                    jobs.append((fid,comment,rid,project['project_id']))
                    if fid not in existing:
                        client.create_feedback(run_id=rid,key='recall_source_explanation_v1',
                            feedback_id=fid,comment=comment,session_id=project['project_id'],stop_after_attempt=1)
            remote={str(f.id):f for f in client.list_feedback(run_ids=[j[2] for j in jobs])}
            assert all(fid in remote and remote[fid].comment==comment for fid,comment,_,_ in jobs)
            write_json(folder/'source-review-sync.json',dict(status='verified',feedback_count=len(jobs),
                benchmark_sha256=digest,source_review_sha256=__import__('hashlib').sha256((folder/'source-review.json').read_bytes()).hexdigest()))
        finally:rec.close()
    # Refresh existing overview to reflect completed remote status; no calls to models.
    rec=RecallDataset(ROOT,VERSION)
    try:report(rec,s,folder)
    finally:rec.close()
    print(json.dumps(dict(verified=True,source_transitions=transitions,latency=latency),ensure_ascii=False))


if __name__=='__main__':main()
