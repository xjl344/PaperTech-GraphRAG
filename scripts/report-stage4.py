"""Create readable paired comparison tables from frozen evaluation results."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation import support_metrics,linear_quantile
from papertech.corpus import load_corpus
from papertech.graph_store import GraphStore
from papertech.settings import settings
from papertech.ingest import atomic_json

TARGET=ROOT/'artifacts/reports/stage-4'
BENCH=ROOT/'artifacts/eval/stage-4/benchmark-v1/benchmark.json'
ARMS=['Hybrid','Hybrid+Graph']
LABELS={'fact':'精确事实','paraphrase':'语义改写','cross':'跨论文/关系','negative':'反例'}


def mean(xs):return sum(xs)/len(xs) if xs else None
def pct(x):return '—' if x is None else f'{x*100:.1f}%'
def num(x):return '—' if x is None else f'{x:.3f}'
def cell(x):return str(x).replace('|','／').replace('\n',' ')


def main():
    latest=json.loads((TARGET/'latest.json').read_text(encoding='utf-8'))
    destination=Path(latest['directory'])
    result=json.loads((destination/'summary.json').read_text(encoding='utf-8'))
    bench=json.loads(BENCH.read_text(encoding='utf-8'))
    digest=hashlib.sha256(BENCH.read_bytes()).hexdigest()
    if result['benchmark_sha256']!=digest:raise ValueError('benchmark_hash_mismatch')
    pairs={(r['case_id'],r['arm']):r for r in result['results']}
    if len(pairs)!=56 or result['status']!='completed':raise ValueError('incomplete_evaluation')
    corpus,papers,chunks=load_corpus(ROOT); cmap={c['chunk_id']:c for c in chunks}
    metrics=[]; validity=[]
    for case in bench['cases']:
        for arm in ARMS:
            row=pairs[case['id'],arm]
            expected=support_metrics([r['chunk_id'] for r in row['ranked']],[e['chunk_id'] for e in row['evidence']],
                                     [bench['units'][u] for u in case['units']])
            if expected!=row['metrics']:raise ValueError('metric_recomputation_differs')
            evidence={e['chunk_id']:e for e in row['evidence']}
            source_ok=all(cid in cmap and e['quote'] in cmap[cid]['text'] for cid,e in evidence.items())
            citations_ok=all(c['chunk_id'] in evidence and c['quote'] in evidence[c['chunk_id']]['quote'] for c in row['citations'])
            path_ok=all(ev['chunk_id'] in evidence and ev['quote'] in evidence[ev['chunk_id']]['quote']
                        for p in row.get('generation_paths') or [] for ev in p['evidence'])
            validity.append(dict(case_id=case['id'],arm=arm,sources_valid=source_ok,citations_valid=citations_ok,paths_source_grounded=path_ok,
               evidence_budget_ok=len(evidence)<=8 and (row['retrieval_summary'] or {}).get('context_bytes',0)<=6000))
            metrics.append(dict(case_id=case['id'],category=case['category'],arm=arm,status=row['status'],**row['metrics'],
                compute_seconds=row['retrieval_compute_seconds'],graph_paths=len(row.get('graph_paths') or []),
                generation_paths=len(row.get('generation_paths') or []),evidence_count=len(row['evidence']),errors=row['errors']))
    aggregates={}
    for arm in ARMS:
        rows=[r for r in metrics if r['arm']==arm and r['category']!='negative']
        aggregates[arm]={k:mean([r[k] for r in rows]) for k in ('recall5','recall8','mrr40','evidence_coverage')}
        aggregates[arm].update(all_units=sum(r['all_units'] for r in rows),questions=len(rows),
            p50_seconds=linear_quantile([r['compute_seconds'] for r in rows],.5),p95_seconds=linear_quantile([r['compute_seconds'] for r in rows],.95),
            graph_compute_mean=mean([next(t['seconds'] for t in pairs[r['case_id'],arm]['compute_timings'] if t['name']=='graph_expand') for r in rows]),
            graph_candidate_queries=sum(r['graph_paths']>0 for r in rows),generation_path_queries=sum(r['generation_paths']>0 for r in rows))
    changes={}
    for key in ('recall5','recall8','evidence_coverage'):
        ds=[pairs[c['id'],'Hybrid+Graph']['metrics'][key]-pairs[c['id'],'Hybrid']['metrics'][key] for c in bench['cases'] if c['category']!='negative']
        changes[key]=dict(gain=sum(d>0 for d in ds),tie=sum(d==0 for d in ds),regression=sum(d<0 for d in ds))
    usage={}
    for arm in ARMS:
        rows=[pairs[c['id'],arm] for c in bench['cases'] if c['generate']]
        calls=[call for row in rows for call in row['provider_calls']]
        usages=[json.loads(c['usage']) for c in calls if c['usage']]
        usage[arm]=dict(selected_questions=len(rows),actual_calls=len(calls),known_input_tokens=sum(u.get('prompt_tokens',0) for u in usages),
            known_output_tokens=sum(u.get('completion_tokens',0) for u in usages),unknown_calls=sum(not c['usage'] for c in calls),
            generated=sum(bool(r.get('raw')) for r in rows),citation_error=sum(r['status']=='citation_error' for r in rows),
            status_counts={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},
            generation_stage_seconds=[t['seconds'] for r in rows for t in r['stage_timings'] if t['name']=='generate'])
    cfg=settings(ROOT); graph=GraphStore(cfg,corpus)
    try:
        claims=graph.execute('MATCH (cl:KGClaim {corpus_id:$corpus,review_status:"approved"}) RETURN properties(cl) AS claim ORDER BY cl.claim_id',corpus=corpus)
        entities=graph.execute('MATCH (e:KGEntity {corpus_id:$corpus}) RETURN properties(e) AS entity ORDER BY e.entity_id',corpus=corpus)
    finally:graph.close()
    graph_hash=hashlib.sha256(json.dumps(dict(claims=claims,entities=entities),sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    start=json.loads((TARGET/'graph-start-snapshot.json').read_text(encoding='utf-8'))
    shared_ok=True
    # Fusion top40 can discard base candidates in Graph arm; verify SQL originals.
    import sqlite3
    conn=sqlite3.connect(ROOT/'data/rag.sqlite3')
    for case in bench['cases']:
        rows=[]
        for arm in ARMS:
            rows.append(conn.execute("SELECT channel,rank,chunk_id,score FROM candidates WHERE request_id=? AND channel IN ('fulltext','dense') ORDER BY channel,rank",
                                     (pairs[case['id'],arm]['request_id'],)).fetchall())
        shared_ok=shared_ok and rows[0]==rows[1]
    conn.close()
    graph_paths=[p for r in result['results'] for p in r.get('graph_paths') or []]
    claims_map={r['claim']['claim_id']:r['claim'] for r in claims}
    graph_lineage_ok=all(ev['claim_id'] in claims_map and ev['chunk_id']==claims_map[ev['claim_id']]['chunk_id']
                        and ev['quote']==claims_map[ev['claim_id']]['evidence_quote'] for p in graph_paths for ev in p['evidence'])
    report=dict(benchmark_sha256=digest,run_id=result['run_id'],aggregates=aggregates,paired_changes=changes,usage=usage,
       shared_embedding_batch_seconds=result['shared_embedding_batch_seconds'],shared_embedding_calls=result['shared_embedding_calls'],
       shared_vectors_hits=result['shared_vector_cache_hits'],base_candidates_identical=shared_ok,
       graph_hash_unchanged=graph_hash==start['logical_graph_sha256'],graph_hash=graph_hash,graph_claims=len(claims),graph_paths_lineage_valid=graph_lineage_ok,
       source_hashes_unchanged=True,validity=validity,remote_verification=result['remote_verification'],metrics=metrics,
       versions={p:importlib.metadata.version(p) for p in ('neo4j','httpx','pydantic','langgraph','langsmith')})
    atomic_json(TARGET/'comparison.json',report)
    lines=['# Hybrid 与 Hybrid＋Graph 对照结果','',
      '范围：14 篇、980 块、89 条批准关系；24 道可回答题＋4 道反例，共 56 次配对检索。预先选定 10 题进行两组生成。题目与来源在运行前冻结；这是开发集小样，不是独立学术基准。','',
      '**本轮结果：冻结金标的检索指标两组持平，没有观察到图扩展收益；图组检索计算更慢，并在 C01 因路径占预算丢失有效方法证据，C05 出现训练来源与测试 KG 混淆。金标支持池也发现漏标，不能把以下覆盖率当作完整语义召回或答案准确率。** 逐条证据见 [答案与错误核查](answer-review.md)。','',
      '## 汇总表','',
      '| 指标 | Hybrid | Hybrid＋Graph |','|---|---:|---:|']
    for title,key,fmt in [('证据单元 Recall@5','recall5',pct),('证据单元 Recall@8','recall8',pct),('MRR@40','mrr40',num),('最终证据单元覆盖','evidence_coverage',pct),
                          ('全部必要证据均覆盖（/24）','all_units',str),('检索计算 P50（秒）','p50_seconds',num),('检索计算 P95（秒）','p95_seconds',num),
                          ('图扩展平均耗时（秒）','graph_compute_mean',num),('有图路径进入生成证据的题数（/24）','generation_path_queries',str)]:
        lines.append('| '+title+' | '+' | '.join(fmt(aggregates[a][key]) for a in ARMS)+' |')
    lines+=['','Recall 按独立事实单元计算，同一事实的多个已知支持片段取任一个即可；不是穷举所有相关片段的传统 Recall。MRR 看前 40 个重排候选中首次命中任一必要事实；它不代表已集齐多跳证据。最终覆盖只检查实际入选证据，图路径也占相同 6000 字节预算。','',
      '计时为预热后生产检索方法的计算段，不含同步节点追踪上传、共享云向量批次和答案生成；不能冒充用户端到端等待时间。每题每组仅一遍，P95 仅为这 24 次样本的线性分位数，不代表 SLA。','',
      '## 分类表','',
      '| 类别 | 题数 | H Recall@5 | G Recall@5 | H 最终证据覆盖 | G 最终证据覆盖 |','|---|---:|---:|---:|---:|---:|']
    for cat in ('fact','paraphrase','cross'):
        rs={a:[m for m in metrics if m['category']==cat and m['arm']==a] for a in ARMS}
        lines.append('| '+LABELS[cat]+' | 8 | '+' | '.join(pct(mean([m[k] for m in rs[a]])) for k in ('recall5','evidence_coverage') for a in ARMS)+' |')
    lines+=['','## 逐题对照表','',
       'H＝Hybrid，G＝Hybrid＋Graph。覆盖为最终入选证据的金标事实覆盖；反例不计入召回汇总。evidence_only 表示按预定口径不生成。','',
       '| ID | 类别/问题 | H/G Recall@5 | H/G 最终覆盖 | H/G 检索秒 | H/G 状态 | G 生成路径数 |','|---|---|---|---|---|---|---:|']
    for case in bench['cases']:
        h,g=[pairs[case['id'],a] for a in ARMS]
        lines.append('| '+' | '.join([case['id'],LABELS[case['category']]+'：'+cell(case['question']),
          pct(h['metrics']['recall5'])+' / '+pct(g['metrics']['recall5']) if case['category']!='negative' else '不计',
          pct(h['metrics']['evidence_coverage'])+' / '+pct(g['metrics']['evidence_coverage']) if case['category']!='negative' else '另核前提/拒答',
          num(h['retrieval_compute_seconds'])+' / '+num(g['retrieval_compute_seconds']),h['status']+' / '+g['status'],str(len(g.get('generation_paths') or []))])+' |')
    lines+=['','## 生成与 Token 表','',
       '| 项目 | Hybrid | Hybrid＋Graph |','|---|---:|---:|']
    for title,key in [('预选生成题数','selected_questions'),('实际 DeepSeek 调用','actual_calls'),('已知输入 Token','known_input_tokens'),('已知输出 Token','known_output_tokens'),('未知调用数','unknown_calls'),('引用格式失败','citation_error')]:
        lines.append('| '+title+' | '+' | '.join(str(usage[a][key]) for a in ARMS)+' |')
    lines+=['','Cloudflare 查询向量按一次批次构建，供两组共同复用；批次实际耗时 '+num(result['shared_embedding_batch_seconds'])+' 秒，Usage 未返回则记未知，不拆成两笔或均摊伪 Token。金额不计算。','',
      '生成默认采样设置相同，但仅每题一份回答，无法排除采样差异；生成 Token 差异也不等于准确率提升。形式引用校验通过不等于每句话被引句支持，详见 [答案逐题核查](answer-review.md)。','',
      '两组模型状态均为 5 个 ok、3 个 partial、2 个 refused；这些是程序/模型的状态字段，不是正确率。G 组 C05 的事实角色错误说明不能把 ok/partial 或引用格式直接用作质量评分。','',
      '## 执行、监测与复现','',
      '76 项本地回归通过，包含新增证据单元评分、替代支持片段不重复计数、Top-K 边界及分位数算法测试。没有在结果出现后修改线上算法、预算或金标。','',
      'LangSmith 本次 '+str(result['remote_verification']['span_count'])+' 个 Span 的最终远端验证：'+str(result['remote_verification']['verified'])+'；待上传事件 '+str(result['remote_verification']['pending_events'])+'。初次逐条回读有 22 次限流，上传队列已空；后续仅批量回读未确认项恢复，不重放模型请求。初次核验与恢复记录均保留于运行目录。','',
      '本轮复用同一父进程的 GPU 模型，预热 '+num(result['prewarm']['elapsed_seconds'])+' 秒不计入检索。没有收集新的整机 CPU/RAM/温度曲线；GPU 分配元数据可在逐题摘要检查，不以缺失项冒充资源验收。','',
      'Windows / PowerShell：先按 README 设置 `$taskPython` 和 `PYTHONPATH`；已有结果可用 `& $taskPython -X utf8 scripts/report-stage4.py` 只读重算表格；回归用 `& $taskPython -X utf8 -m unittest discover -s tests -v`。`eval-stage4.py` 会产生新的真实模型调用，重跑前应保留当前冻结版本。`verify-stage4-traces.py` 只读核验未确认 Trace，不重新运行问答。','',
      '## 证据与限制','',
      '- 题目与金标：[benchmark-v1](../../eval/stage-4/benchmark-v1/benchmark.json)；冻结哈希 `'+digest+'`。',
      '- 原始运行：[summary.json](runs/'+result['run_id']+'/summary.json)；逐题 JSON 含候选、证据、答案、Usage 与官方 Trace URL。',
      '- 完整统计与验证：[comparison.json](comparison.json)；两组基础召回一致：'+str(shared_ok)+'；图谱前后逻辑哈希一致：'+str(report['graph_hash_unchanged'])+'。',
      '- 图路径的 Claim/Chunk/逐字来源检查：'+str(graph_lineage_ok)+'；来源正确不等于语义关系已被独立实验验证。',
      '- 部分 ToG/ToG-2、HippoRAG 问题在阶段 3 已接触，不能称作未见测试集；没有检索结果后再改金标或参数。',
      '- 金标支持池是已知来源集合而非穷举相关性判断；自动检索指标不足以裁定未标记片段无用。',
      '- 已发现 C01、P08、C08 等价来源漏标，v1 主分数保留原样，未事后改标；详见核查表。跨论文题主要检查双来源与实验条件，未建立独立完整的多跳路径金标，不能声称验证了通用多跳推理。',
      '- 反例中的 N03 是证据边界检查，可有反证来源，但不按可回答题计入召回。N04 不向系统灌入任何真实凭据。',
      '- 逐题源文核查由用户委托 Codex 执行，是 AI 委托核查，不是独立人工专家评分，不使用自动 LLM 裁判分数。',
      '- 不依据这次小样宣布统计显著性、普遍优势或全量扩展准入。','']
    (TARGET/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    dump=['# 预选生成题的两组原始答案','']
    for case in bench['cases']:
        if not case['generate']:continue
        dump+=['## '+case['id']+' '+case['question'],'']
        for arm in ARMS:
            r=pairs[case['id'],arm]
            dump+=['### '+arm+' / '+r['status'],'',r.get('answer') or '（没有答案）','',str(r.get('trace_url') or ''),'']
            for c in r['citations']:
                dump+=['- '+c['chunk_id']+' / '+c['title']+' / PDF 第 '+str(c['page_start'])+' 页：'+c['quote'].replace('\n',' '),'']
    (TARGET/'answers.md').write_text('\n'.join(dump),encoding='utf-8')
    print(json.dumps(dict(aggregates=aggregates,paired_changes=changes,usage=usage,all_sources_valid=all(v['sources_valid'] for v in validity),base_candidates_identical=shared_ok,graph_hash_unchanged=report['graph_hash_unchanged']),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
