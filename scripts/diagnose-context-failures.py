"""Build a source-backed, per-question failure diagnosis from saved replays."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark, write_json

VERSION = 'benchmark-source-coverage-v1'
RUN_ID = '4b0e586edc95477d89a8fac736814162'
RUN = ROOT / 'artifacts/reports/stage-4' / VERSION / 'context-budget-runs' / RUN_ID
OUTPUT = ROOT / 'artifacts/reports/stage-4' / VERSION / 'failure-diagnosis'
ARMS = ('Budget-before', 'Evidence-first', 'Compact-paths')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_chunk(chunk):
    return {key: chunk.get(key) for key in (
        'chunk_id', 'paper_id', 'title', 'page_start', 'page_end', 'section',
        'source_relative_path', 'source_spans', 'text_sha256', 'text')}


def diagnose(bench, chunks, summary):
    cases = {case['id']: case for case in bench['cases']}
    grouped = {case_id: {arm: row for arm in ARMS for row in summary['results']
        if row['case_id'] == case_id and row['arm'] == arm} for case_id in cases}
    output = []
    for case_id, case in cases.items():
        rows = grouped[case_id]
        ranked = rows['Evidence-first']['ranked']
        ranks = {item['chunk_id']: rank for rank, item in enumerate(ranked, 1)}
        selected = {arm: {item['chunk_id'] for item in rows[arm]['evidence']} for arm in ARMS}
        units = []
        for unit_id in case['units']:
            unit = bench['units'][unit_id]
            support = []
            for chunk_id in unit['known_support_chunks']:
                candidate = next((row for row in ranked if row['chunk_id'] == chunk_id), None)
                support.append(dict(chunk_id=chunk_id, candidate_rank=ranks.get(chunk_id),
                    present_in_ranked_candidates=chunk_id in ranks,
                    selected_by_arm={arm: chunk_id in selected[arm] for arm in ARMS},
                    source=compact_chunk(chunks[chunk_id])))
            unit_coverage = {arm: any(s['selected_by_arm'][arm] for s in support) for arm in ARMS}
            units.append(dict(unit_id=unit_id, required_fact=unit['answer_point'],
                support_candidates=support, ranked_candidate_count=sum(s['present_in_ranked_candidates'] for s in support),
                covered_by_arm=unit_coverage,
                missing_after_evidence_first=not unit_coverage['Evidence-first']))

        missing = [unit for unit in units if unit['missing_after_evidence_first']]
        ranked_but_not_selected = [unit for unit in missing if unit['ranked_candidate_count']]
        no_known_support_in_ranked = [unit for unit in missing if not unit['ranked_candidate_count']]
        if not missing:
            diagnosis = 'known_support_pool_covered'
            certainty = 'limited'
            explanation = '冻结支持池中的必要事实块均已进入上下文；这不能证明答案语义正确或引用有效。'
            next_action = '对新生成答案做逐事实、关系方向和引用核查；不要继续调整本题预算。'
        elif ranked_but_not_selected and no_known_support_in_ranked:
            diagnosis = 'mixed_selection_and_candidate_or_pool_gap'
            certainty = 'partial'
            explanation = '部分缺失事实已有已知支持块进入候选但未入选；另有缺失事实在冻结支持池中没有候选命中。'
            next_action = '先分别验证未入选块的排名/预算原因，并核对候选池和冻结支持池是否完整，再选排序或召回实验。'
        elif ranked_but_not_selected:
            diagnosis = 'ranked_support_not_selected'
            certainty = 'high_for_selection_stage'
            explanation = '缺失事实的已知支持块存在于最终重排候选中，却未进入原文上下文；这是排序之后的证据选择/预算问题。'
            next_action = '比较支持块名次、上下文成本和被选块；优先测试支持感知的重排/选择或更细粒度切块。'
        else:
            diagnosis = 'no_known_support_in_final_ranked_list'
            certainty = 'cannot_distinguish_retrieval_from_reference_pool'
            explanation = '缺失事实的已知支持块没有出现在保存的最终候选列表中；快照不能区分上游未召回、重排截断或支持池漏标。'
            next_action = '回查该题完整检索通道/Trace 与原文支持池；先区分召回失败和参考支持块不完备，再决定检索或标注优化。'

        evidence = {}
        for arm in ARMS:
            row = rows[arm]
            evidence[arm] = [dict(**compact_chunk(chunks[item['chunk_id']]),
                rerank_score=item.get('rerank_score'), score=item.get('score'),
                retrieval_sources=item.get('sources')) for item in row['ranked']]
        output.append(dict(case_id=case_id, question=case['question'], category=case['category'],
            required_source_papers=case['source_papers'], required_units=units,
            metrics={arm: rows[arm]['metrics'] for arm in ARMS},
            source_metrics={arm: rows[arm]['source_metrics'] for arm in ARMS},
            selected_evidence={arm:[compact_chunk(chunks[item['chunk_id']]) for item in rows[arm]['evidence']] for arm in ARMS},
            ranked_candidates=evidence['Evidence-first'],
            candidate_count=len(ranked), candidate_count_by_channel={channel:sum(
                any(source['channel']==channel for source in item.get('sources',[])) for item in ranked)
                for channel in ('fulltext','dense','graph')},
            path_count={arm:len(rows[arm]['generation_paths']) for arm in ARMS},
            budget={arm:dict(total_bytes=rows[arm]['retrieval_summary']['serialized_content_bytes'],
                evidence_bytes=rows[arm]['retrieval_summary']['evidence_bytes'],
                path_bytes=rows[arm]['retrieval_summary']['graph_context_bytes'],
                limit_bytes=6000) for arm in ARMS},
            added_chunks={arm:sorted(selected[arm]-selected['Budget-before']) for arm in ARMS},
            removed_chunks={arm:sorted(selected['Budget-before']-selected[arm]) for arm in ARMS},
            diagnosis=dict(code=diagnosis, certainty=certainty, explanation=explanation,
                missing_units=[unit['unit_id'] for unit in missing],
                ranked_but_not_selected_units=[unit['unit_id'] for unit in ranked_but_not_selected],
                no_known_support_in_ranked_units=[unit['unit_id'] for unit in no_known_support_in_ranked],
                next_action=next_action),
            interpretation_limit='候选列表为已保存的最终排序列表，不含所有检索前候选；known_support_chunks 是有限且非独立人工标注的支持池。'))
    return output


def dashboard(data, summary):
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>16题失败归因</title>
<style>body{font:15px/1.65 system-ui,"Microsoft YaHei";max-width:1450px;margin:auto;padding:22px;background:#f5f7fb;color:#263449}section{background:white;border:1px solid #dbe2ed;border-radius:8px;padding:18px;margin:18px 0}.charts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.bar{height:18px;background:#3974b9;margin:4px 0}.warn{background:#d8843d}table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}pre{white-space:pre-wrap;word-break:break-word;max-height:480px;overflow:auto;background:#f6f7fa;padding:10px;font-size:12px}button,input{font:inherit;padding:6px}summary{cursor:pointer}a{color:#245cad}@media(max-width:800px){.charts{grid-template-columns:1fr}}</style>
<h1>16 道失败题逐题归因</h1><p>基于冻结支持池、第一步和第二步保存的候选/证据。没有模型调用；缺失候选不自动等于检索漏召回。</p><nav><a href="diagnosis.json">完整诊断数据 JSON</a> · <a href="diagnosis.md">逐题文字报告</a> · <a href="../context-budget-runs/4b0e586edc95477d89a8fac736814162/dashboard.html">上下文预算对照</a></nav>
<section><h2>失败类型分布</h2><div id="charts" class="charts"></div><p id="counts"></p><p>自动事实覆盖是对有限已知支持块的 ID 对齐，不是答案语义准确率。候选证据是最终排序列表快照。</p></section>
<section><h2>逐题分类</h2><input id="search" placeholder="搜索题号、论文或失败类型"><div style="overflow:auto"><table><thead><tr><th>题号</th><th>基线 / 原文优先 / 紧凑事实覆盖</th><th>缺失支持事实</th><th>失败分类及把握度</th><th></th></tr></thead><tbody id="rows"></tbody></table></div></section><section id="detail"><h2>选择题目查看全部证据</h2></section>
<script>const DATA=__DATA__, $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const labels={known_support_pool_covered:'已知支持块已覆盖',ranked_support_not_selected:'候选有支持块但未入选',no_known_support_in_final_ranked_list:'最终候选没有已知支持块',mixed_selection_and_candidate_or_pool_gap:'选择与候选/支持池混合缺口'};const counts={};for(const q of DATA)counts[q.diagnosis.code]=(counts[q.diagnosis.code]||0)+1;const max=Math.max(1,...Object.values(counts));$('charts').innerHTML=Object.entries(counts).map(([k,v])=>'<div><b>'+esc(labels[k]||k)+'：'+v+' 题</b><div class="bar '+(k.includes('no_known')||k.includes('mixed')?'warn':'')+'" style="width:'+(v/max*100)+'%"></div></div>').join('');$('counts').textContent='按主分类计数，共 '+DATA.length+' 题；题目可能同时包含多个缺失事实，详情中分别列出。';function block(title,x,open=false){return '<details'+(open?' open':'')+'><summary>'+esc(title)+'</summary><pre>'+esc(JSON.stringify(x,null,2))+'</pre></details>'}function table(){const q=$('search').value.toLowerCase();$('rows').innerHTML=DATA.filter(x=>(x.case_id+' '+x.question+' '+x.diagnosis.code).toLowerCase().includes(q)).map(x=>'<tr><td>'+x.case_id+'<br>'+esc(x.question)+'</td><td>'+['Budget-before','Evidence-first','Compact-paths'].map(a=>(100*x.metrics[a].evidence_coverage).toFixed(1)+'%').join(' / ')+'</td><td>'+esc(x.diagnosis.missing_units.join(', ')||'无')+'</td><td>'+esc(labels[x.diagnosis.code])+'<br>'+esc(x.diagnosis.certainty)+'</td><td><button data-id="'+x.case_id+'">详情</button></td></tr>').join('');$('rows').querySelectorAll('button').forEach(b=>b.onclick=()=>show(b.dataset.id))}function show(id){const x=DATA.find(y=>y.case_id===id);$('detail').innerHTML='<h2>'+id+'：'+esc(x.question)+'</h2><p>'+esc(x.diagnosis.explanation)+'</p><p><b>建议验证：</b>'+esc(x.diagnosis.next_action)+'</p>'+block('必要事实、支持块 ID、排名与上下文入选情况',x.required_units,true)+block('三组指标、来源覆盖、路径与预算',{metrics:x.metrics,source_metrics:x.source_metrics,path_count:x.path_count,budget:x.budget,added_chunks:x.added_chunks,removed_chunks:x.removed_chunks},true)+block('三组入选原文及位置',x.selected_evidence)+block('全部最终排序候选：排名、来源通道、原文与位置',x.ranked_candidates)+block('诊断依据与限制',x.diagnosis)}$('search').oninput=table;table();</script></html>'''.replace('__DATA__', payload)


def write_report(data, benchmark_hash, parent_hash):
    counts = Counter(row['diagnosis']['code'] for row in data)
    lines = ['# 16 道失败题逐题归因', '',
        '基于冻结支持块、第一步结果及第二步固定候选回放。没有新检索、生成或模型调用。候选排名数据只包含最终保存的候选列表。', '',
        f"题集 SHA-256：`{benchmark_hash}`；第二步父运行 SHA-256：`{parent_hash}`。", '',
        '| 主分类 | 题数 | 含义 |', '|---|---:|---|']
    meanings = {
        'known_support_pool_covered':'有限已知支持块均已入选；语义正确性未验证',
        'ranked_support_not_selected':'已知支持块出现在最终排序候选但未入选',
        'no_known_support_in_final_ranked_list':'最终候选中没有冻结支持池里的块；召回/支持池缺标尚不能区分',
        'mixed_selection_and_candidate_or_pool_gap':'同一题同时有排序后未入选与无已知支持候选的事实'}
    for key, count in counts.items():
        lines.append(f'| `{key}` | {count} | {meanings[key]} |')
    lines += ['', '这组题是按旧 Graph 失败筛选的诊断子集，分类比例不能外推总体。`known_support_chunks` 是有限支持池，候选是最终排序列表；没有命中已知块不能单独证明检索失败。', '',
        '## 逐题诊断', '', '| 题号 | 基线 / 原文优先 / 紧凑事实覆盖 | 主分类 | 缺失事实 | 判断与下一步验证 |', '|---|---|---|---|---|']
    arms = ('Budget-before','Evidence-first','Compact-paths')
    for row in data:
        cov = ' / '.join(f"{100*row['metrics'][arm]['evidence_coverage']:.1f}%" for arm in arms)
        d = row['diagnosis']
        lines.append(f"| {row['case_id']} | {cov} | `{d['code']}` | {', '.join(d['missing_units']) or '无'} | {d['explanation']} {d['next_action']} |")
    lines += ['', '## 优化优先级', '',
        '1. 对 `no_known_support_in_final_ranked_list` 题，补齐从 full-text/dense/graph 召回到 reranker 前后的逐通道候选快照，再对照原文核查有限支持池。当前只能确认已知支持块未出现在最终排序候选，不能直接断言漏召回。',
        '2. 对 `ranked_support_not_selected` 题，依据已知支持块名次、入选块字节成本和 top-8/6000 字节约束，测试支持互补意识的选择或切块策略。这才是预算与选择阶段能直接改善的组。',
        '3. 对 `known_support_pool_covered` 题，停止把更多上下文当首要目标，转向重新生成并逐题核查答案中的关系方向、实体角色、实验条件与引用。当前指标不能告诉我们答案是否正确。',
        '', '每题的完整候选原文、来源位置、支持事实、排名、入选差异、预算与建议都在 `diagnosis.json` 和交互页面中。',
        '', '[交互式分类图与 16 题完整详情](dashboard.html) · [机器可读诊断数据](diagnosis.json)']
    (OUTPUT / 'diagnosis.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary', type=Path, default=RUN / 'summary.json')
    args = parser.parse_args()
    folder = args.run_summary.resolve().parent
    summary = json.loads(args.run_summary.read_text(encoding='utf-8'))
    bench, digest, _ = load_benchmark(ROOT, VERSION)
    if summary['benchmark_sha256'] != digest or summary['run_id'] != RUN_ID:
        raise ValueError('diagnosis_input_contract_mismatch')
    corpus_id, _, chunks = load_corpus(ROOT)
    if corpus_id != bench['corpus_id']:
        raise ValueError('diagnosis_corpus_mismatch')
    chunk_map = {chunk['chunk_id']: chunk for chunk in chunks}
    data = diagnose(bench, chunk_map, summary)
    assert len(data) == 16
    for row in data:
        assert set(row['metrics']) == set(ARMS)
        for arm in ARMS:
            saved = next(result for result in summary['results']
                if result['case_id'] == row['case_id'] and result['arm'] == arm)
            assert len(row['selected_evidence'][arm]) == len(saved['evidence'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT / 'diagnosis.json', dict(benchmark=VERSION, benchmark_sha256=digest,
        source_run_id=summary['run_id'], source_run_summary_sha256=sha(args.run_summary),
        generated_from_saved_results=True, model_calls=0, categories=dict(Counter(
            row['diagnosis']['code'] for row in data)), questions=data))
    (OUTPUT / 'dashboard.html').write_text(dashboard(data, summary), encoding='utf-8')
    write_report(data, digest, sha(folder / 'summary.json'))
    print(json.dumps(dict(status='generated', questions=len(data), model_calls=0,
        categories=dict(Counter(row['diagnosis']['code'] for row in data)), directory=str(OUTPUT)), ensure_ascii=False))


if __name__ == '__main__':
    main()
