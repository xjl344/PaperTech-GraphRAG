"""Rebuild summary, charts and all per-question results without model calls."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.evaluation import support_metrics, linear_quantile
from papertech.evaluation_datasets import load_benchmark, write_json

ARMS = ('Hybrid', 'Hybrid+Graph')
METRICS = ('recall5', 'recall8', 'mrr40', 'evidence_coverage')
LABELS = {'fact': '基础事实', 'paraphrase': '语义改写', 'cross': '跨文本关系', 'negative': '反例'}


def mean(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def aggregate(rows):
    scored = [row for row in rows if row['category'] != 'negative']
    times = [row['retrieval_compute_seconds'] for row in scored]
    calls = [call for row in rows for call in row.get('provider_calls') or []]
    tokens = []
    for call in calls:
        usage = call.get('usage')
        if isinstance(usage, str):
            usage = json.loads(usage)
        if usage:
            tokens.append(usage)
    return dict(questions=len(rows), scored_questions=len(scored),
        **{key: mean([row['metrics'].get(key) for row in scored]) for key in METRICS},
        all_units=sum(bool(row['metrics'].get('all_units')) for row in scored),
        p50_seconds=linear_quantile(times, .5), p95_seconds=linear_quantile(times, .95),
        request_p95_seconds=linear_quantile([row['request_wall_seconds'] for row in rows if row.get('request_wall_seconds') is not None], .95),
        graph_candidate_queries=sum(bool(row.get('graph_paths')) for row in rows),
        generation_path_queries=sum(bool(row.get('generation_paths')) for row in rows),
        statuses=dict(Counter(row['status'] for row in rows)),
        generation_requested=sum(bool(row.get('generate_requested')) for row in rows),
        generation_calls=len(calls),
        input_tokens=sum(usage.get('prompt_tokens', 0) for usage in tokens),
        output_tokens=sum(usage.get('completion_tokens', 0) for usage in tokens),
        usage_unknown=sum(not call.get('usage') for call in calls),
        query_coverage_note='反例不计入召回及检索计算时延汇总；请求墙钟 P95 单独报告，包含实际 tracing 开销。')


def build(benchmark, digest, summary, chunks, ledger=None):
    if summary['benchmark_sha256'] != digest or summary['benchmark'] != benchmark['version']:
        raise ValueError('benchmark_mismatch')
    controls = summary.get('execution_config', {}).get('controls', benchmark['controls'])
    cases = {case['id']: case for case in benchmark['cases']}
    pairs = {}
    validity = []
    for row in summary['results']:
        case = cases[row['case_id']]
        key = (case['id'], row['arm'])
        if key in pairs or row['arm'] not in ARMS or row['question'] != case['question']:
            raise ValueError('invalid_or_duplicate_result')
        expected = support_metrics([item['chunk_id'] for item in row.get('ranked') or []],
            [item['chunk_id'] for item in row.get('evidence') or []],
            [benchmark['units'][unit] for unit in case['units']])
        if expected != row['metrics']:
            raise ValueError('frozen_metric_recomputation_differs')
        row = dict(row)
        if row.get('raw'):
            try:
                draft = json.loads(row['raw'])
                if isinstance(draft, dict) and isinstance(draft.get('answer'), str):
                    row['generated_answer_draft'] = dict(answer=draft['answer'], validation_status=row['status'])
            except (ValueError, TypeError):
                pass
        if ledger is not None:
            timing = ledger.execute('SELECT started,finished FROM requests WHERE id=?', (row['request_id'],)).fetchone()
            if timing and timing[0] and timing[1]:
                from datetime import datetime
                row['request_wall_seconds'] = (datetime.fromisoformat(timing[1]) - datetime.fromisoformat(timing[0])).total_seconds()
        evidence = {item['chunk_id']: item for item in row.get('evidence') or []}
        validity.append(dict(case_id=case['id'], arm=row['arm'],
            sources_valid=all(cid in chunks and item['quote'] in chunks[cid]['text'] for cid, item in evidence.items()),
            citations_valid=all(c['chunk_id'] in evidence and c['quote'] in evidence[c['chunk_id']]['quote'] for c in row.get('citations') or []),
            generation_paths_grounded=all(item['chunk_id'] in evidence and item['quote'] in evidence[item['chunk_id']]['quote']
                for path in row.get('generation_paths') or [] for item in path['evidence']),
            budget_valid=len(evidence) <= controls['evidence_max'] and
                (row.get('retrieval_summary') or {}).get('context_bytes', 0) <= controls['context_bytes']))
        pairs[key] = row
    if summary['status'] == 'completed' and len(pairs) != len(cases) * 2:
        raise ValueError('missing_completed_pair')
    rows = list(pairs.values())
    aggregates = {arm: aggregate([row for row in rows if row['arm'] == arm]) for arm in ARMS}
    categories = {category: {arm: aggregate([row for row in rows if row['arm'] == arm and row['category'] == category])
        for arm in ARMS} for category in LABELS}
    changes = {key: dict(gain=0, tie=0, regression=0) for key in METRICS}
    case_records = []
    base_checks = []
    for case in benchmark['cases']:
        h, g = [pairs.get((case['id'], arm)) for arm in ARMS]
        differences = {}
        if h is not None and g is not None:
            for key in METRICS:
                delta = g['metrics'][key] - h['metrics'][key] if case['category'] != 'negative' else None
                differences[key] = delta
                if delta is not None:
                    changes[key]['gain' if delta > 0 else 'regression' if delta < 0 else 'tie'] += 1
            if ledger is not None:
                candidates = [ledger.execute("SELECT channel,rank,chunk_id,score FROM candidates WHERE request_id=? AND channel IN ('fulltext','dense') ORDER BY channel,rank", (row['request_id'],)).fetchall() for row in (h, g)]
                base_checks.append(candidates[0] == candidates[1])
        case_records.append(dict(case=case, results={arm: pairs.get((case['id'], arm)) for arm in ARMS}, differences=differences))
    return dict(benchmark=benchmark['version'], benchmark_sha256=digest, run_id=summary['run_id'],
        status=summary['status'], aggregates=aggregates, categories=categories, paired_changes=changes,
        total_cases=len(cases), recorded_results=len(rows), validity=validity,
        source_checks_passed=all(all(v[key] for key in ('sources_valid', 'citations_valid', 'generation_paths_grounded', 'budget_valid')) for v in validity),
        base_candidates_identical=all(base_checks) if base_checks else None,
        shared_embedding_batch_seconds=summary.get('shared_embedding_batch_seconds'),
        shared_embedding_calls=summary.get('shared_embedding_calls'),
        remote_verification=summary.get('remote_verification'),
        dataset_sync=summary.get('dataset_sync'), case_records=case_records,
        scoring=benchmark['scoring'], controls=controls,
        models=summary.get('execution_config', {}).get('models', benchmark['models']),
        execution_config=summary.get('execution_config'))


def markdown(report):
    def fmt(value):
        return '—' if value is None else f'{value:.4f}' if isinstance(value, float) else str(value)
    lines = [f"# {report['benchmark']} 实测对照", '',
        f"运行 `{report['run_id']}`；{report['total_cases']} 题、{report['recorded_results']} 条结果。", '',
        '[指标、柱状图和逐题详情](dashboard.html) · [机器可读汇总](comparison.json) · [逐题 CSV](per-question.csv)', '',
        '本轮是已接触语料的开发集；支持池并不穷举。检索覆盖不代表答案正确率；不同题集总分不能直接比较。', '',
        '| 指标 | Hybrid | Hybrid＋Graph |', '|---|---:|---:|']
    for label, key in [('SupportRecall@5', 'recall5'), ('SupportRecall@8', 'recall8'), ('MRR@40', 'mrr40'),
            ('来源支持单元覆盖', 'evidence_coverage'), ('必要来源单元全覆盖题数', 'all_units'), ('检索计算 P50 秒', 'p50_seconds'),
            ('检索计算 P95 秒', 'p95_seconds'), ('请求墙钟 P95 秒', 'request_p95_seconds'),
            ('实际生成调用', 'generation_calls'), ('已知输入 Token', 'input_tokens'), ('已知输出 Token', 'output_tokens'), ('未知用量调用', 'usage_unknown')]:
        lines.append('| ' + label + ' | ' + ' | '.join(fmt(report['aggregates'][arm][key]) for arm in ARMS) + ' |')
    sync = report.get('dataset_sync') or {}
    if sync.get('comparison_url'):
        lines += ['', f"[LangSmith 两组实验对照]({sync['comparison_url']})"]
    lines += ['', '检索计算时延不含共享问题向量、追踪上传与生成；请求墙钟含追踪开销，单独报告。反例不计入召回分母。', '',
        '## 分类对照', '', '| 类型 | 题数 | H/G Recall@5 | H/G 最终覆盖 |', '|---|---:|---|---|']
    for category, values in report['categories'].items():
        lines.append('| ' + LABELS[category] + ' | ' + str(values['Hybrid']['questions']) + ' | ' +
            ' / '.join(fmt(values[arm]['recall5']) for arm in ARMS) + ' | ' +
            ' / '.join(fmt(values[arm]['evidence_coverage']) for arm in ARMS) + ' |')
    lines += ['', '## 逐题结果', '', '| ID | 类型 | H/G 状态 | H/G Recall@5 | H/G 最终覆盖 | H/G 检索秒 |', '|---|---|---|---|---|---|']
    for record in report['case_records']:
        case = record['case']
        rows = [record['results'][arm] for arm in ARMS]
        def paired(key, metric=False):
            return ' / '.join(fmt((row['metrics'] if metric else row).get(key)) if row else '待完成' for row in rows)
        lines.append('| ' + ' | '.join([case['id'], LABELS[case['category']], paired('status'), paired('recall5', True),
            paired('evidence_coverage', True), paired('retrieval_compute_seconds')]) + ' |')
    lines += ['', '## 检查与限制', '',
        f"- 原文/引用/生成路径/预算程序检查：{report['source_checks_passed']}；两组基础候选一致：{report['base_candidates_identical']}。",
        '- 语义、角色与关系正确性需要独立看原文；程序状态 ok/partial 不是答案准确率。',
        '- 单次运行不能宣称统计显著性；计时边界、支持池和完整评测配置保存在 comparison.json。',
        '- LangSmith 实验的输入为问题，参考要点仅用于事后核查，没有输入检索或生成。', '']
    scope = report.get('controls', {})
    if scope.get('treatment_scope'):
        lines += ['- 本轮两组原文证据上限均为 6000 字节；图组可使用额外最多 1200 字节路径信息。'
            '本轮衡量这套图扩展配置的整体效果，没有将实际输入 Token 强制对齐。',
            '- 147 个判分点逐项记录所需来源是否进入上下文；semantic_score 为 null 表示尚无独立语义评分。', '']
    return '\n'.join(lines)


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>论文 RAG 实测对照</title><style>
body{margin:0;background:#f4f6fa;color:#18263c;font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1280px;margin:auto;padding:28px}h1{margin:0}h2{margin:0 0 18px}a{color:#245cad}section,.card{background:white;border:1px solid #dfe5ef;border-radius:12px;padding:22px;margin:18px 0}.cards,.plots,.arms{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.cards{grid-template-columns:repeat(4,minmax(0,1fr))}.card{margin:0}.card strong{display:block;font-size:27px}.muted,small{color:#58677c}.notice{border-left:4px solid #b7791f;padding:10px 16px;background:#fff9e9}.legend i{display:inline-block;width:12px;height:12px;margin-right:6px}.h{background:#316bc6}.g{background:#db813b}.bars{display:grid;grid-template-columns:1fr;gap:10px}.bar{height:23px;min-width:1px;border-radius:3px;white-space:nowrap;color:white;padding-left:6px;box-sizing:border-box;font-size:13px}.chartrow{margin-bottom:18px}.chartrow b{display:block;margin-bottom:5px}select,input,button{font:inherit;border:1px solid #bdc8d8;border-radius:6px;padding:7px 10px;background:white}button{cursor:pointer;color:#245cad}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:9px;border-bottom:1px solid #e5e9ef;text-align:left;vertical-align:top}th{background:#eff3f9}tr:hover{background:#f6f9fd}.scroll{overflow:auto}pre{white-space:pre-wrap;word-break:break-word;font:13px/1.6 ui-monospace,Consolas,monospace;background:#f4f6f9;padding:14px;border-radius:6px;max-height:600px;overflow:auto}details{border-top:1px solid #e1e7ef;padding:12px 0}summary{cursor:pointer;font-weight:600}.question{font-size:17px}#detail{scroll-margin:20px}@media(max-width:800px){.plots,.arms{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,1fr)}main{padding:14px}}
</style><main><h1>论文 RAG 实测对照</h1><p id="run" class="muted"></p><nav id="links"></nav><p class="notice">开发集小样本；检索支持池有限。覆盖率、引用形式及程序状态不能替代答案语义正确性，不同题集总分不能直接比较。</p>
<div class="cards" id="cards"></div><section><label>题型筛选 <select id="category"><option value="all">全部</option><option value="fact">基础事实</option><option value="paraphrase">语义改写</option><option value="cross">跨文本关系</option><option value="negative">反例</option></select></label><span class="legend">　<i class="h"></i>Hybrid　<i class="g"></i>Hybrid＋Graph</span></section>
<div class="plots"><section><h2>检索指标</h2><div id="quality"></div><small>反例单列，不计召回。MRR 是首次命中任一必要事实的倒数排名。</small></section><section><h2>检索与请求时延（秒）</h2><div id="latency"></div><small>计算时延不含共享向量、追踪上传和生成；墙钟时延包含本次实际追踪开销。</small></section><section><h2>Token 与生成调用</h2><div id="tokens"></div><small>只统计已知生成用量；共享 Cloudflare Usage 缺失保留未知，不均摊伪 Token。</small></section><section><h2>状态分布与图路径</h2><div id="states"></div><small>ok、partial、refused 等是程序状态，不是正确率。</small></section></div>
<section><h2>逐题对照</h2><input id="search" placeholder="搜索题号或问题" style="width:60%"><p id="count" class="muted"></p><div class="scroll"><table><thead><tr><th>题目</th><th>H/G 状态</th><th>H/G R@5</th><th>H/G 最终覆盖</th><th>H/G 检索秒</th><th>查看</th></tr></thead><tbody id="rows"></tbody></table></div></section>
<section id="detail"><h2>单题详情</h2><p>在上表选择任意一道题，查看参考证据与两组完整运行记录。</p></section><section><h2>验证、口径和限制</h2><div id="checks"></div><details><summary>冻结评分和运行配置</summary><pre id="config"></pre></details></section></main><script>
const DATA=__DATA__;
const LABELS={fact:'基础事实',paraphrase:'语义改写',cross:'跨文本关系',negative:'反例'},ARMS=['Hybrid','Hybrid+Graph'];
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),fmt=(x,pct=false)=>x===null||x===undefined?'—':pct?(100*x).toFixed(1)+'%':typeof x==='number'?Number.isInteger(x)?String(x):x.toFixed(3):esc(x);
$('run').textContent=DATA.benchmark+' · '+DATA.run_id+' · '+DATA.total_cases+' 题 / '+DATA.recorded_results+' 条结果 · '+DATA.status;
const sync=DATA.dataset_sync||{};$('links').innerHTML='<a href="comparison.md">文字报告</a> · <a href="comparison.json">完整统计 JSON</a> · <a href="per-question.csv">逐题 CSV</a>'+(sync.comparison_url?' · <a target="_blank" rel="noopener" href="'+esc(sync.comparison_url)+'">LangSmith 两组对照</a>':'');
$('cards').innerHTML=[['总题数',DATA.total_cases],['跨文本关系题',DATA.case_records.filter(r=>r.case.category==='cross').length],['已保存结果',DATA.recorded_results],['原文/引用/预算检查',DATA.source_checks_passed?'通过':'有待核对项']].map(([k,v])=>'<div class="card"><span>'+k+'</span><strong>'+v+'</strong></div>').join('');
function chart(id,metrics,aggs){let html='';for(const [label,key,ratio]of metrics){const vals=ARMS.map(a=>aggs[a][key]);const max=ratio?1:Math.max(...vals.filter(v=>v!==null&&v!==undefined),1);html+='<div class="chartrow"><b>'+label+'</b>';vals.forEach((v,i)=>{html+='<div style="display:flex;gap:8px;align-items:center;margin:5px 0"><div style="width:70%"><div class="bar '+(i?'g':'h')+'" style="width:'+(v===null||v===undefined?0:Math.max(0,100*v/max))+'%"></div></div><span>'+fmt(v,ratio)+'</span></div>'});html+='</div>'}$(id).innerHTML=html}
function draw(){const cat=$('category').value;const a=cat==='all'?DATA.aggregates:DATA.categories[cat];chart('quality',[['SupportRecall@5','recall5',true],['SupportRecall@8','recall8',true],['MRR@40','mrr40',true],['最终事实覆盖','evidence_coverage',true],['全部必要事实均覆盖（题）','all_units',false]],a);chart('latency',[['检索计算 P50','p50_seconds',false],['检索计算 P95','p95_seconds',false],['请求墙钟 P95','request_p95_seconds',false]],a);chart('tokens',[['已知输入 Token','input_tokens',false],['已知输出 Token','output_tokens',false],['实际生成调用','generation_calls',false],['用量未知调用','usage_unknown',false]],a);let s=Object.fromEntries(ARMS.map(arm=>[arm,{...a[arm],...a[arm].statuses}]));chart('states',[...new Set(ARMS.flatMap(arm=>Object.keys(a[arm].statuses)))].map(k=>[k,k,false]).concat([['出现图候选的题数','graph_candidate_queries',false],['生成采用图路径的题数','generation_path_queries',false]]),s);table()}
function table(){const cat=$('category').value,q=$('search').value.toLowerCase();const records=DATA.case_records.filter(r=>(cat==='all'||r.case.category===cat)&&(r.case.id+' '+r.case.question).toLowerCase().includes(q));$('count').textContent='显示 '+records.length+' / '+DATA.total_cases+' 题';$('rows').innerHTML=records.map(r=>{const pair=(k,m=false,pct=false)=>ARMS.map(a=>r.results[a]?fmt((m?r.results[a].metrics:r.results[a])[k],pct):'待完成').join(' / ');return '<tr><td><b>'+r.case.id+'</b> · '+LABELS[r.case.category]+'<br>'+esc(r.case.question)+'</td><td>'+pair('status')+'</td><td>'+pair('recall5',true,true)+'</td><td>'+pair('evidence_coverage',true,true)+'</td><td>'+pair('retrieval_compute_seconds')+'</td><td><button data-case="'+r.case.id+'">详情</button></td></tr>'}).join('');$('rows').querySelectorAll('button').forEach(b=>b.onclick=()=>show(b.dataset.case))}
function block(title,value,open=false){return '<details'+(open?' open':'')+'><summary>'+esc(title)+'</summary><pre>'+esc(typeof value==='string'?value:JSON.stringify(value,null,2))+'</pre></details>'}
function show(id){const r=DATA.case_records.find(r=>r.case.id===id),c=r.case;let html='<h2>'+id+' · '+LABELS[c.category]+'</h2><p class="question">'+esc(c.question)+'</p>';html+=block('参考答案、关系与评分要求',DATA.references[id]||c,true);html+='<div class="arms">';for(const a of ARMS){const x=r.results[a];html+='<div><h3>'+a+'</h3>';if(!x){html+='<p>尚无此组结果</p></div>';continue}html+='<p>状态：'+esc(x.status)+' · 检索 '+fmt(x.retrieval_compute_seconds)+' 秒</p>';html+=block('完整回答',x.answer||'没有生成回答',true)+block('逐题指标与另一组差异',{metrics:x.metrics,graph_minus_hybrid:r.differences})+block('全部候选与重排分数',x.ranked)+block('入选原文证据',x.evidence)+block('引用及来源位置',x.citations)+block('全部图路径',x.graph_paths)+block('生成采用的图路径',x.generation_paths)+block('耗时、Token 与调用',{compute_timings:x.compute_timings,stage_timings:x.stage_timings,provider_calls:x.provider_calls,usage:x.usage,request_wall_seconds:x.request_wall_seconds})+block('检索摘要及缺口',{retrieval_summary:x.retrieval_summary,limitations:x.limitations,errors:x.errors});if(x.trace_url)html+='<a target="_blank" rel="noopener" href="'+esc(x.trace_url)+'">原始 Trace</a>';html+='</div>'}html+='</div>';$('detail').innerHTML=html;$('detail').scrollIntoView({behavior:'smooth'})}
$('category').onchange=draw;$('search').oninput=table;$('config').textContent=JSON.stringify({scoring:DATA.scoring,controls:DATA.controls,models:DATA.models},null,2);$('checks').innerHTML='<p>基础全文/Dense 候选一致：'+fmt(DATA.base_candidates_identical)+'；原文/引用/生成路径及预算：'+(DATA.source_checks_passed?'通过':'待核对')+'。</p><p>逐题语义核查另行记录；没有用 LLM 裁判计算“答案准确率”。</p>';draw();
const originalShow=show;show=function(id){originalShow(id);if(DATA.diagnostics&&DATA.diagnostics[id])$('detail').innerHTML+=block('逐题引用协议、必要来源及未通过校验的模型草稿',DATA.diagnostics[id]);};
</script></html>'''

# Keep the original report layout while exposing the v4 execution diagnostics.
HTML = HTML.replace('最终事实覆盖', '来源支持单元覆盖').replace('全部必要事实均覆盖（题）', '必要来源单元全覆盖（题）')
HTML = HTML.replace("block('全部候选与重排分数',x.ranked)",
    "block('全部候选与重排分数',x.ranked)+block('各召回通道原始排序与分数',x.candidate_channels)"
    "+block('逐判分点来源覆盖与缺口（不是语义得分）',x.criterion_source_coverage)"
    "+block('模型回答草稿及校验状态',x.generated_answer_draft)")
HTML = HTML.replace('controls:DATA.controls,models:DATA.models}',
    'controls:DATA.controls,models:DATA.models,execution_config:DATA.execution_config}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', default='benchmark-v2')
    parser.add_argument('--run-summary', type=Path)
    args = parser.parse_args()
    bench, digest, directory = load_benchmark(ROOT, args.benchmark)
    report_root = ROOT / 'artifacts/reports/stage-4'
    if args.benchmark != 'benchmark-v1':
        report_root /= args.benchmark
    summary_path = args.run_summary or Path(json.loads((report_root / 'latest.json').read_text(encoding='utf-8'))['directory']) / 'summary.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    corpus, _, chunks = load_corpus(ROOT)
    if corpus != bench['corpus_id']:
        raise ValueError('corpus_changed')
    ledger_path = ROOT / 'data/rag.sqlite3'
    ledger = sqlite3.connect(ledger_path.as_uri() + '?mode=ro', uri=True) if ledger_path.exists() else None
    try:
        report = build(bench, digest, summary, {c['chunk_id']: c for c in chunks}, ledger)
    finally:
        if ledger:
            ledger.close()
    folder = summary_path.parent
    diagnostics_path = folder / 'per-question-diagnostics.json'
    if diagnostics_path.exists():
        diagnostics = json.loads(diagnostics_path.read_text(encoding='utf-8'))
        report['diagnostics'] = {}
        for item in diagnostics['records']:
            report['diagnostics'].setdefault(item['case_id'], {})[item['arm']] = item
    target = folder / 'report'
    target.mkdir(exist_ok=True)
    write_json(target / 'comparison.json', report)
    (target / 'comparison.md').write_text(markdown(report), encoding='utf-8')
    exports = json.loads((directory / 'langsmith-dataset.json').read_text(encoding='utf-8'))
    references = {example['metadata']['case_id']: example['outputs'] for example in exports['examples']}
    data = dict(report, references=references)
    embedded = json.dumps(data, ensure_ascii=False).replace('<', '\u003c')
    (target / 'dashboard.html').write_text(HTML.replace('__DATA__', embedded), encoding='utf-8')
    with (target / 'per-question.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        fields = ['case_id', 'category', 'arm', 'question', 'status'] + list(METRICS) + ['all_units', 'retrieval_compute_seconds', 'request_wall_seconds', 'trace_url']
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in report['case_records']:
            for arm, row in record['results'].items():
                if row:
                    writer.writerow(dict(case_id=record['case']['id'], category=record['case']['category'], arm=arm,
                        question=record['case']['question'], status=row['status'], **row['metrics'],
                        retrieval_compute_seconds=row['retrieval_compute_seconds'], request_wall_seconds=row.get('request_wall_seconds'), trace_url=row.get('trace_url')))
    write_json(report_root / 'latest-report.json', dict(directory=str(target), run_id=report['run_id'], benchmark=args.benchmark))
    print(json.dumps(dict(directory=str(target), aggregates=report['aggregates'], paired_changes=report['paired_changes'],
        source_checks_passed=report['source_checks_passed'], base_candidates_identical=report['base_candidates_identical']), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
