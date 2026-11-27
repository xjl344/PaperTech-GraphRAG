"""Paired statistics and readable per-question explanations from saved results."""
from collections import Counter
import csv
import html
import json
import random

from .evaluation import linear_quantile
from .evaluation_datasets import write_json

ARMS = ('Graph-only', 'Hybrid')


def paired_statistics(rows, case_ids, resamples=10000, seed=20261122):
    pairs = {}
    for row in rows:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    deltas = [pairs[c]['Graph-only']['metrics']['evidence_coverage'] -
        pairs[c]['Hybrid']['metrics']['evidence_coverage'] for c in case_ids
        if set(pairs.get(c, {})) == set(ARMS)]
    if not deltas:
        return dict(count=0, mean_delta=None, ci95=None, graph_wins=0, ties=0, hybrid_wins=0)
    rng = random.Random(seed)
    samples = sorted(sum(rng.choices(deltas, k=len(deltas))) / len(deltas) for _ in range(resamples))
    return dict(count=len(deltas), mean_delta=sum(deltas)/len(deltas),
        ci95=[linear_quantile(samples, .025), linear_quantile(samples, .975)],
        graph_wins=sum(d > 1e-12 for d in deltas), ties=sum(abs(d) <= 1e-12 for d in deltas),
        hybrid_wins=sum(d < -1e-12 for d in deltas),
        resamples=resamples, seed=seed, interpretation='固定诊断题集的配对重采样；不是总体泛化保证。')


def pool_coverage(row, case, bench):
    ids = {r['chunk_id'] for r in row['ranked']}
    return sum(bool(ids & set(bench['units'][u]['known_support_chunks'])) for u in case['units']) / len(case['units'])


def supplement(recorder, summary, folder, aggregate):
    bench = recorder.bench
    cases = {c['id']: c for c in bench['cases']}
    rows = summary['results']
    def stats(ids):
        result = {}
        for a in ARMS:
            group = [r for r in rows if r['arm'] == a and r['case_id'] in ids]
            result[a] = aggregate(group)
            result[a]['candidate_pool_coverage40'] = (sum(pool_coverage(r, cases[r['case_id']], bench)
                for r in group)/len(group) if group else None)
            result[a]['required_paper_coverage'] = (sum(r['source_metrics']['required_paper_coverage']
                for r in group)/len(group) if group else None)
        return result
    cross = [c['id'] for c in bench['cases'] if c['category'] == 'cross']
    paired = paired_statistics(rows, cross)
    strata = {key: stats([cid for cid in cross if cases[cid]['graph_source_link_stratum'] == key])
        for key in ('all_source_blocks_linked', 'some_source_blocks_linked', 'no_source_blocks_linked')}
    forms = {key: stats([cid for cid in cross if cases[cid]['query_form'] == key]) for key in ('named', 'discovery')}
    positive = [c['id'] for c in bench['cases'] if c['category'] != 'negative']
    result = dict(status=summary['status'], primary_cross=stats(cross), all_positive=stats(positive),
        paired_cross=paired, source_link_strata=strata, query_forms=forms,
        note='挂图指来源块关联任意Claim；不表示必要关系已建边或两跳可达。来源覆盖不等于回答正确率。')
    write_json(folder / 'paired-analysis.json', result)
    if not rows:
        return
    grouped = {}
    for r in rows:
        grouped.setdefault(r['case_id'], {})[r['arm']] = r
    def percent(v):
        return '—' if v is None else f'{v:.2%}'
    def cell(group, a, key='evidence_coverage'):
        return percent(group[a][key])
    lines = ['# 新问题检索对照', '', f"状态：{summary['status']}。40题 × 两组；无答案生成。", '',
        '主指标：24道跨论文题的最终必要来源覆盖率，逐题宏平均。', '',
        '|指标|Graph-only|Hybrid|', '|---|---:|---:|']
    for title, key in [('候选池覆盖@40', 'candidate_pool_coverage40'), ('Recall@5', 'recall5'),
            ('Recall@8', 'recall8'), ('最终必要来源覆盖', 'evidence_coverage')]:
        lines.append(f"|跨论文 {title}|{cell(result['primary_cross'], 'Graph-only',key)}|{cell(result['primary_cross'], 'Hybrid',key)}|")
    for a in ARMS:
        s = result['primary_cross'][a]
        lines.append(f"\n{a}：跨论文全部必要来源覆盖 {s['all_units']}/24 题；检索计算 P50={s['latency_p50']:.3f}s，P95={s['latency_p95']:.3f}s。")
    if paired['count']:
        lo, hi = paired['ci95']
        lines.extend(['', f"配对覆盖差（Graph-only − Hybrid）：{paired['mean_delta']:+.2%}，95% bootstrap 区间 [{lo:+.2%}, {hi:+.2%}]。",
            f"逐题胜/平/负：{paired['graph_wins']}/{paired['ties']}/{paired['hybrid_wins']}。固定题集诊断，不能当作总体显著性保证。"])
    lines.extend(['', '生成调用=0，生成 Token=0。Embedding 为 Hybrid 独用的40题批量请求；其耗时另报，未计入单题计算时延。Embedding/Reranker 未报告的 Token 记未知，上下文长度单位为 UTF-8 字节。', '',
        '支持池为事前冻结的非穷尽来源池；未命中不能证明全部有效原文都缺失。8道错误前提题只列纠错来源，不计算答案或拒答正确率。', '',
        '同语料新问题迁移诊断：一部分是旧事实的新组合，图曾参考开发来源；本轮保持原图、别名、模型与阈值。', '',
        '## 跨论文来源挂接分层', '', '|来源块挂图情况|题数|Graph-only 最终覆盖|Hybrid 最终覆盖|', '|---|---:|---:|---:|'])
    extra = ['<section><h2>跨论文配对分析与分层</h2>', '<pre>' + html.escape(json.dumps(result,ensure_ascii=False,indent=2)) + '</pre>']
    for key, group in strata.items():
        lines.append(f"|{key}|{group['Hybrid']['count']}|{cell(group,'Graph-only')}|{cell(group,'Hybrid')}|")
    lines.extend(['', '## 逐题来源缺口', '', '|题号|类型|Graph-only|Hybrid|逐题解释|', '|---|---|---:|---:|---|'])
    records = []
    for case in bench['cases']:
        cid = case['id']
        pair = grouped.get(cid, {})
        if set(pair) != set(ARMS):
            continue
        explanations = []
        for a in ARMS:
            row = pair[a]
            issues = [f"{f['unit_id']}：{f['explanation']}" for f in row['diagnosis']['facts'] if f['reason'] != 'covered']
            explanations.append(a + '：' + ('；'.join(issues) if issues else '全部必要来源进入上下文'))
            records.append(dict(case_id=cid, category=case['category'], question=case['question'], arm=a,
                query_form=case['query_form'], graph_source_link_stratum=case['graph_source_link_stratum'],
                candidate_pool_coverage40=pool_coverage(row,case,bench), **row['metrics'],
                candidate_count=len(row['ranked']), evidence_count=len(row['evidence']),
                context_bytes=row['retrieval_summary'].get('context_bytes',0),
                compute_seconds=row['retrieval_compute_seconds'], request_wall_seconds=row['request_wall_seconds'],
                trace_url=row.get('trace_url'), explanation=explanations[-1]))
        lines.append(f"|{cid}|{case['category']}|{percent(pair['Graph-only']['metrics']['evidence_coverage'])}|{percent(pair['Hybrid']['metrics']['evidence_coverage'])}|{'；'.join(explanations)}|")
        extra.append(f'<p><a href="#{cid}">{cid}</a> ' + html.escape('；'.join(explanations)) + '</p>')
    extra.append('</section>')
    with (folder / 'per-question.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(records[0]) if records else [])
        writer.writeheader()
        writer.writerows(records)
    (folder / 'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    page = folder / 'dashboard.html'
    text = page.read_text(encoding='utf8')
    text = text.replace('<h2>40题逐题详情', '\n'.join(extra)+'<h2>40题逐题详情')
    if '<section>' not in text:
        text = text.replace('</html>', '\n'.join(extra)+'</html>')
    page.write_text(text,encoding='utf8')
