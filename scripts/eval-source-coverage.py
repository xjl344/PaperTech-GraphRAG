"""Replay Graph source selection on a frozen failure subset; never call models."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import logging
import math
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.entity_aliases import ALIAS_VERSION, is_comparison
from papertech.evidence_context import assemble
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import load_benchmark, stable_id, write_json
from papertech.evaluation_details import DetailedEvaluationDataset, detailed_output

VERSION = 'benchmark-source-coverage-v1'
ARMS = ('Graph-before', 'Graph-after')


def baseline_assembler(directory, benchmark):
    modules = {}
    for filename in ('entity_aliases.py', 'evidence_context.py'):
        path = directory / 'baseline' / filename
        expected = benchmark['code_sha256']['src/papertech/' + filename]
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('baseline_snapshot_changed')
        spec = importlib.util.spec_from_file_location('papertech._baseline_' + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[path.stem] = module
    evidence = modules['evidence_context']
    evidence.GROUPS = modules['entity_aliases'].GROUPS
    evidence.mentions = modules['entity_aliases'].mentions
    return evidence.assemble


def source_metrics(case, bench, evidence):
    required = {bench['units'][key]['paper_id'] for key in case['units']}
    selected = {item['paper_id'] for item in evidence}
    return dict(required_paper_coverage=len(required & selected) / len(required),
        all_required_papers=required.issubset(selected), missing_paper_ids=sorted(required - selected))


def diagnostics(summary):
    pairs = {}
    for row in summary['results']:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    records = {}
    for case_id, pair in pairs.items():
        before, after = [pair[arm] for arm in ARMS]
        a, b = [{item['chunk_id'] for item in row['evidence']} for row in (before, after)]
        delta = after['metrics']['evidence_coverage'] - before['metrics']['evidence_coverage']
        note = '按固定候选回放，来源出现不等于论断得到支持；本轮没有生成新回答。'
        if delta < 0:
            note += '保留新来源后，冻结支持池事实覆盖退化，必须单列，不能按来源篇数宣布质量通过。'
        if case_id == 'R18':
            note += '新增 RoG 原文占用预算，原先 KG-GPT 的已标注主支持段未入选；当前 RoG 入选段也未命中主支持池。'
        if case_id == 'R20':
            note += '仍缺 KGP；当前固定候选中没有同时通过来源有效性、分数阈值及单块预算门槛的 KGP 片段，不能强行加入。'
        records[case_id] = dict(case_id=case_id, added_chunk_ids=sorted(b - a), removed_chunk_ids=sorted(a - b),
            fact_coverage_delta=delta, all_required_papers_before=before['source_metrics']['all_required_papers'],
            all_required_papers_after=after['source_metrics']['all_required_papers'],
            after_source_coverage=after['retrieval_summary'].get('source_coverage'),
            note=note, review_kind='程序差异诊断及 Codex 定向说明；非独立语义评分')
    return records


def replay(recorder):
    bench, directory = recorder.bench, recorder.directory
    parent_folder = ROOT / 'artifacts/reports/stage-4/benchmark-v2/runs' / bench['parent_benchmark']['run_id']
    raw = (parent_folder / 'summary.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != bench['parent_benchmark']['summary_sha256']:
        raise ValueError('frozen_parent_result_changed')
    parent = json.loads(raw)
    originals = {row['case_id']: row for row in parent['results'] if row['arm'] == 'Hybrid+Graph'}
    old_assemble = baseline_assembler(directory, bench)
    summary = dict(benchmark=VERSION, benchmark_sha256=recorder.digest, run_id=uuid.uuid4().hex,
        status='completed', mode='frozen_candidate_evidence_replay', results=[],
        model_calls=0, generation_calls=0, new_generation_tokens=None,
        parent_run_id=parent['run_id'], alias_version=ALIAS_VERSION,
        code_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
            'src/papertech/entity_aliases.py', 'src/papertech/evidence_context.py',
            'src/papertech/workflow.py', 'scripts/eval-source-coverage.py')})
    for case in bench['cases']:
        original = originals[case['id']]
        for arm in ARMS:
            started = datetime.now(timezone.utc)
            begin = time.perf_counter()
            old_comparison = any(word in case['question'].casefold() for word in ('比较', '对比', 'compare', 'versus'))
            fn, comparison = (old_assemble, old_comparison) if arm == ARMS[0] else (assemble, is_comparison(case['question']))
            evidence, paths, detail = fn(original['ranked'], recorder.chunks, original['graph_paths'], case['question'], comparison)
            seconds = time.perf_counter() - begin
            ended = datetime.now(timezone.utc)
            if arm == ARMS[0] and (evidence != original['evidence'] or paths != original['generation_paths']):
                raise ValueError('baseline_replay_mismatch:' + case['id'])
            if detail['context_bytes'] > 6000 or len(evidence) > 8:
                raise ValueError('evidence_budget_exceeded')
            row = dict(case_id=case['id'], question=case['question'], category=case['category'], arm=arm,
                status='evidence_only', answer='本轮仅回放证据选择，没有生成新回答。历史回答见 parent_generation。',
                evidence=evidence, graph_paths=deepcopy(original['graph_paths']), generation_paths=paths,
                ranked=deepcopy(original['ranked']), citations=[], usage=None, model_name=None,
                provider_calls=[], generate_requested=False, order=ARMS.index(arm) + 1,
                errors=[], limitations=detail['limitations'], retrieval_summary=detail,
                compute_timings=[dict(name='evidence', seconds=seconds)],
                stage_timings=[dict(name='evidence', seconds=seconds, status='ok')],
                assembly_seconds=seconds, start_time=started.isoformat(), end_time=ended.isoformat(),
                trace_url=original['trace_url'], request_id=original['request_id'],
                source_metrics=source_metrics(case, bench, evidence),
                parent_generation=dict(notice='上一轮历史结果，仅供解释；不是本轮新回答或新用量。',
                    **{key: deepcopy(original.get(key)) for key in ('answer', 'citations', 'status', 'usage', 'model_name', 'errors', 'trace_url')}))
            row['metrics'] = support_metrics([item['chunk_id'] for item in row['ranked']],
                [item['chunk_id'] for item in evidence], [bench['units'][key] for key in case['units']])
            # The evaluator, not production assembly, consults reference facts.
            summary['results'].append(row)
    return summary


def payloads_for(recorder, summary):
    cases = {case['id']: case for case in recorder.bench['cases']}
    payloads = []
    for row in summary['results']:
        outputs = detailed_output(row, cases[row['case_id']], recorder.bench, recorder.chunks)
        outputs.update(mode=summary['mode'], source_metrics=row['source_metrics'],
            parent_generation=row['parent_generation'], assembly_seconds=row['assembly_seconds'],
            generation_calls=0, new_generation_tokens=None,
            timing_note='本轮原生时延仅为证据组装回放，不是完整 RAG 请求时延；Trace 链接为父运行。')
        outputs.pop('retrieval_compute_seconds', None)
        metrics = dict(required_paper_coverage=row['source_metrics']['required_paper_coverage'],
            all_required_papers=row['source_metrics']['all_required_papers'],
            evidence_coverage=row['metrics']['evidence_coverage'], all_units=row['metrics']['all_units'],
            evidence_count=len(row['evidence']), context_bytes=row['retrieval_summary']['context_bytes'],
            graph_context_bytes=row['retrieval_summary']['graph_context_bytes'], assembly_seconds=row['assembly_seconds'])
        payloads.append(dict(id=stable_id(recorder.digest, summary['run_id'], row['case_id'], row['arm']),
            name='frozen-Graph-evidence-replay', run_type='chain', inputs=dict(question=row['question']), outputs=outputs,
            reference_example_id=stable_id(recorder.digest, row['case_id']),
            start_time=row['start_time'], end_time=row['end_time'], tags=[VERSION, row['arm'], 'no-generation'],
            extra=dict(metadata=dict(benchmark=VERSION, benchmark_sha256=recorder.digest,
                run_id=summary['run_id'], case_id=row['case_id'], arm=row['arm'],
                capture_mode='frozen_candidate_evidence_replay', parent_run_id=summary['parent_run_id'],
                model_calls=0, source_selection_only=True)), _metrics=metrics, _arm=row['arm']))
    return payloads


def sync_results(recorder, dataset, summary, folder, *, arms=ARMS, payloads=None,
                 notes=None, diagnostic_key='source_selection_diagnostics', description=None):
    client = recorder.client
    payloads = payloads_for(recorder, summary) if payloads is None else payloads
    write_json(folder / 'langsmith-experiments.json', dict(runs=payloads))
    experiments = []
    notes = diagnostics(summary) if notes is None else notes
    for arm in arms:
        name = f"papertech-{VERSION}-{summary['run_id'][:12]}-{arm}"
        project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
            description=description or '固定旧图候选的证据选择回放；before/after 来源保留对照。没有新模型回答。',
            metadata=dict(mode=summary['mode'], benchmark_sha256=recorder.digest, model_calls=0, arm=arm))
        if str(project.reference_dataset_id) != str(dataset.id):
            raise ValueError('experiment_dataset_mismatch')
        wanted = {p['id']: p for p in payloads if p['_arm'] == arm}
        def read_runs():
            return {str(run.id): run for run in client.list_runs(project_id=project.id, is_root=True)}
        existing = read_runs()
        if set(existing) - set(wanted):
            raise ValueError('unexpected_replay_run')
        for rid, run in existing.items():
            if run.outputs != wanted[rid]['outputs']:
                raise ValueError('replay_run_changed')
        def upload(p):
            fields = {key: value for key, value in p.items() if not key.startswith('_')}
            for key in ('start_time', 'end_time'):
                fields[key] = datetime.fromisoformat(fields[key])
            client.create_run(project_name=name, **fields)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(upload, [p for rid, p in wanted.items() if rid not in existing]))
        found = {str(f.id): f for f in client.list_feedback(run_ids=list(wanted))}
        jobs = [dict(run_id=p['id'], key=key, score=float(value), feedback_id=stable_id(p['id'], key),
            session_id=project.id, start_time=datetime.fromisoformat(p['start_time']), stop_after_attempt=1,
            comment='固定候选证据回放；来源篇数不等于事实支持或答案正确。')
            for p in wanted.values() for key, value in p['_metrics'].items()]
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: client.create_feedback(**job), [job for job in jobs if job['feedback_id'] not in found]))
        for attempt in range(5):
            runs = read_runs()
            found = {str(f.id): f for f in client.list_feedback(run_ids=list(wanted))}
            valid = set(runs) == set(wanted) and all(run.outputs == wanted[rid]['outputs'] and
                str(run.reference_example_id) == wanted[rid]['reference_example_id'] and
                run.start_time == datetime.fromisoformat(wanted[rid]['start_time']) and
                run.end_time == datetime.fromisoformat(wanted[rid]['end_time']) for rid, run in runs.items())
            feedback_ok = all(job['feedback_id'] in found and math.isclose(found[job['feedback_id']].score,
                job['score'], abs_tol=0.000050001, rel_tol=0) for job in jobs)
            if valid and feedback_ok:
                break
            if attempt == 4:
                raise ValueError('replay_readback_incomplete')
            time.sleep(2)
        diagnostic_jobs = [dict(run_id=p['id'], key=diagnostic_key,
            value=notes[p['extra']['metadata']['case_id']], feedback_id=stable_id(p['id'], diagnostic_key),
            session_id=project.id, start_time=datetime.fromisoformat(p['start_time']), stop_after_attempt=1,
            comment='来源选择前后差异，保留退化；不作为答案准确率。') for p in wanted.values()]
        existing_notes = {str(f.id): f for f in client.list_feedback(run_ids=list(wanted), feedback_key=[diagnostic_key])}
        if any(job['feedback_id'] in existing_notes and existing_notes[job['feedback_id']].value != job['value'] for job in diagnostic_jobs):
            raise ValueError('diagnostic_feedback_changed')
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: client.create_feedback(**job), [job for job in diagnostic_jobs if job['feedback_id'] not in existing_notes]))
        found_notes = {str(f.id): f for f in client.list_feedback(run_ids=list(wanted), feedback_key=[diagnostic_key])}
        if any(job['feedback_id'] not in found_notes or found_notes[job['feedback_id']].value != job['value'] for job in diagnostic_jobs):
            raise ValueError('diagnostic_feedback_readback_mismatch')
        client.update_project(project.id, end_time=datetime.now(timezone.utc))
        experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(runs), feedback_verified=len(jobs),
            diagnostic_feedback_verified=len(diagnostic_jobs)))
    return dict(status='experiments_verified', dataset_url=dataset.url, examples_verified=len(recorder.bench['cases']),
        experiments=experiments, comparison_url=dataset.url + '/compare?selectedSessions=' + ','.join(e['project_id'] for e in experiments))


def report(recorder, summary, folder):
    rows = summary['results']
    pairs = {case['id']: {row['arm']: row for row in rows if row['case_id'] == case['id']} for case in recorder.bench['cases']}
    aggregates = {}
    for arm in ARMS:
        selected = [row for row in rows if row['arm'] == arm]
        aggregates[arm] = dict(questions=len(selected), all_required_papers=sum(row['source_metrics']['all_required_papers'] for row in selected),
            required_paper_coverage=sum(row['source_metrics']['required_paper_coverage'] for row in selected) / len(selected),
            evidence_coverage=sum(row['metrics']['evidence_coverage'] for row in selected) / len(selected),
            all_units=sum(row['metrics']['all_units'] for row in selected),
            evidence_count=sum(len(row['evidence']) for row in selected) / len(selected),
            context_bytes=sum(row['retrieval_summary']['context_bytes'] for row in selected) / len(selected),
            assembly_milliseconds=1000 * sum(row['assembly_seconds'] for row in selected) / len(selected),
            generation_calls=0, statuses=dict(Counter(row['status'] for row in selected)))
    changes = Counter('gain' if pair[ARMS[1]]['metrics']['evidence_coverage'] > pair[ARMS[0]]['metrics']['evidence_coverage'] else
        'regression' if pair[ARMS[1]]['metrics']['evidence_coverage'] < pair[ARMS[0]]['metrics']['evidence_coverage'] else 'tie' for pair in pairs.values())
    payload_lookup = {(p['extra']['metadata']['case_id'], p['_arm']): p['outputs'] for p in payloads_for(recorder, summary)}
    export = dict(benchmark=VERSION, run_id=summary['run_id'], mode=summary['mode'], aggregates=aggregates,
        fact_coverage_changes=dict(changes), dataset_sync=summary.get('dataset_sync'),
        diagnostics=diagnostics(summary),
        references={e['metadata']['case_id']: e['outputs'] for e in recorder.payload['examples']},
        results={case_id: {arm: dict(payload=payload_lookup[case_id, arm],
            source_metrics=row['source_metrics'], metrics=row['metrics']) for arm, row in pair.items()} for case_id, pair in pairs.items()})
    write_json(folder / 'comparison.json', export)
    lines = ['# 来源保留第一步：固定图候选回放', '',
        '16 道从旧图组缺来源题中选出的诊断题；不是独立评测集。候选、分数、图路径和 6000 字节预算固定，没有新生成。', '',
        '| 指标 | 修改前 | 修改后 |', '|---|---:|---:|']
    for label, key in [('全部必要论文齐全题数', 'all_required_papers'), ('必要论文覆盖', 'required_paper_coverage'),
            ('冻结支持池事实覆盖', 'evidence_coverage'), ('全部必要事实齐全题数', 'all_units'),
            ('平均证据块数', 'evidence_count'), ('平均证据组装毫秒', 'assembly_milliseconds')]:
        lines.append(f"| {label} | {aggregates[ARMS[0]][key]:.4f} | {aggregates[ARMS[1]][key]:.4f} |")
    lines += ['', f'事实覆盖变化：{dict(changes)}。来源齐全不能替代选对段落。', '',
        '| 题目 | 修改前来源覆盖 | 修改后来源覆盖 | 修改前事实覆盖 | 修改后事实覆盖 |', '|---|---:|---:|---:|---:|']
    for case_id, pair in pairs.items():
        a, b = [pair[arm] for arm in ARMS]
        lines.append(f"| {case_id} | {a['source_metrics']['required_paper_coverage']:.3f} | {b['source_metrics']['required_paper_coverage']:.3f} | {a['metrics']['evidence_coverage']:.3f} | {b['metrics']['evidence_coverage']:.3f} |")
    if summary.get('dataset_sync', {}).get('comparison_url'):
        lines += ['', '[LangSmith 对照](' + summary['dataset_sync']['comparison_url'] + ')']
    lines += ['', '[柱状图、指标与逐题完整详情](dashboard.html)', '',
        '新生成调用 0；新生成 Token 不适用。历史回答、引用、Token、Trace 显式保存在 parent_generation，不能当作优化后的回答。',
        '原 v2 金标有限，未后验补标；本次只验证来源识别与选择，不声称答案质量改善。']
    lines += ['', '## 保留的问题', '',
        '- R18：新增 RoG 来源后，KG-GPT 的已标注支持段被预算挤出；事实覆盖从 50% 降到 0%。',
        '- R20：KGP 没有通过当前证据门槛的候选，仍保留缺口。',
        '- 这个子集专门选择了旧图组缺来源题，不能把提高幅度解释为总体性能提升。',
        '- 回放复用了旧图候选，不检验新版别名对实时图扩展的影响；未做新生成或语义准确率评估。']
    (folder / 'comparison.md').write_text('\n'.join(lines), encoding='utf-8')
    (folder / 'dashboard.html').write_text(HTML.replace('__DATA__', json.dumps(export, ensure_ascii=False).replace('<', '\u003c')), encoding='utf-8')


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Graph 来源保留诊断</title><style>body{font:15px/1.7 system-ui,"Microsoft YaHei";background:#f5f7fb;color:#20304a;margin:auto;max-width:1250px;padding:24px}section{background:white;border:1px solid #dbe2ed;border-radius:10px;padding:20px;margin:20px 0}.plots,.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}.bar{height:20px;background:#4273bc;margin:5px 0}.after{background:#d8843d}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:9px;border-bottom:1px solid #ddd}pre{white-space:pre-wrap;word-break:break-word;max-height:650px;overflow:auto;background:#f6f7fa;padding:12px}button,input{font:inherit;padding:6px}a{color:#245cad}summary{cursor:pointer} @media(max-width:800px){.plots,.pair{grid-template-columns:1fr}}</style>
<h1>Graph 来源保留：修改前 / 修改后</h1><p id="run"></p><p>16 道旧图组缺来源题；固定候选、重排分数、图路径与预算。只回放证据选择，没有重新检索或生成。来源齐全不等于事实和答案正确。</p><nav id="links"></nav>
<section><h2>汇总指标</h2><div id="charts" class="plots"></div><p id="basic"></p></section>
<section><h2>逐题对照</h2><input id="search" placeholder="搜索题号或问题"><p id="count"></p><div style="overflow:auto"><table><thead><tr><th>题目</th><th>来源覆盖：前 / 后</th><th>事实覆盖：前 / 后</th><th></th></tr></thead><tbody id="rows"></tbody></table></div></section>
<section id="detail"><h2>选择题目查看全部数据</h2></section>
<script>const DATA=__DATA__,ARMS=['Graph-before','Graph-after'];const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
$('run').textContent=DATA.benchmark+' · '+DATA.run_id+' · 16 题 / 32 条回放结果';
$('links').innerHTML='<a href="comparison.md">文字报告</a> · <a href="comparison.json">全部数据 JSON</a>'+(DATA.dataset_sync?.comparison_url?' · <a target="_blank" rel="noopener" href="'+esc(DATA.dataset_sync.comparison_url)+'">LangSmith 两组对照</a>':'');
$('charts').innerHTML=[['全部必要论文齐全题数','all_required_papers',16],['必要论文覆盖','required_paper_coverage',1],['冻结支持池事实覆盖','evidence_coverage',1],['全部事实齐全题数','all_units',16],['平均证据块数','evidence_count',8],['平均上下文字节','context_bytes',6000],['平均证据组装毫秒','assembly_milliseconds',Math.max(10,...ARMS.map(a=>DATA.aggregates[a].assembly_milliseconds))]].map(([label,key,max])=>'<div><b>'+label+'</b>'+ARMS.map((arm,i)=>{const v=DATA.aggregates[arm][key];return '<div>'+arm+'：'+(max===1?(100*v).toFixed(2)+'%':v.toFixed(2))+'</div><div class="bar '+(i?'after':'')+'" style="width:'+(100*v/max)+'%"></div>'}).join('')+'</div>').join('');
$('basic').textContent='新检索 0 次；新生成 0 次；新生成 Token 不适用。事实覆盖变化：'+JSON.stringify(DATA.fact_coverage_changes)+'。原生时延仅为证据组装，不代表端到端请求。';
function table(){const q=$('search').value.toLowerCase(),items=Object.entries(DATA.results).filter(([id])=>(id+' '+DATA.references[id].expected_answer+' '+DATA.results[id][ARMS[0]].payload.question).toLowerCase().includes(q));$('count').textContent='显示 '+items.length+' / 16 题';$('rows').innerHTML=items.map(([id,p])=>'<tr><td>'+id+'<br>'+esc(p[ARMS[0]].payload.question)+'</td><td>'+ARMS.map(a=>(100*p[a].source_metrics.required_paper_coverage).toFixed(1)+'%').join(' / ')+'</td><td>'+ARMS.map(a=>(100*p[a].metrics.evidence_coverage).toFixed(1)+'%').join(' / ')+'</td><td><button data-id="'+id+'">详情</button></td></tr>').join('');$('rows').querySelectorAll('button').forEach(b=>b.onclick=()=>show(b.dataset.id))}
function block(name,value,open=false){return '<details'+(open?' open':'')+'><summary>'+esc(name)+'</summary><pre>'+esc(JSON.stringify(value,null,2))+'</pre></details>'}
function show(id){const p=DATA.results[id];let html='<h2>'+id+'</h2>'+block('参考答案、全部原文与位置、关系要求及评分口径',DATA.references[id],true)+block('前后证据增减、来源缺口与退化诊断',DATA.diagnostics[id],true)+'<div class="pair">';for(const arm of ARMS){const x=p[arm].payload;html+='<div><h3>'+arm+'</h3>'+block('本轮状态与指标',{answer:x.answer,status:x.status,metrics:p[arm].metrics,source_metrics:p[arm].source_metrics,assembly_seconds:x.assembly_seconds},true)+block('入选原文、来源与位置',x.evidence,true)+block('来源保护及缺口',x.retrieval_summary)+block('逐事实支持与缺失',{fact_coverage:x.fact_coverage,missing_required_facts:x.missing_required_facts})+block('全部冻结候选及分数',x.ranked_candidates)+block('检索图路径',x.graph_paths)+block('入选上下文路径',x.generation_paths)+block('历史生成回答、引用、Token 与 Trace（不是本轮新结果）',x.parent_generation);if(x.parent_generation.trace_url)html+='<a target="_blank" rel="noopener" href="'+esc(x.parent_generation.trace_url)+'">上一轮原始 Trace</a>';html+='</div>'}html+='</div>';$('detail').innerHTML=html;$('detail').scrollIntoView({behavior:'smooth'})}
$('search').oninput=table;table();</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--resume', type=Path, help='Only rebuild/re-upload an existing summary; no replay.')
    args = parser.parse_args()
    logging.getLogger('langsmith').setLevel(logging.CRITICAL)
    recorder = DetailedEvaluationDataset(ROOT, VERSION)
    folder = None
    try:
        dataset = recorder.sync_dataset() if args.upload else None
        if args.resume:
            folder = args.resume.parent
            summary = json.loads(args.resume.read_text(encoding='utf-8'))
            if summary['benchmark_sha256'] != recorder.digest or summary['benchmark'] != VERSION:
                raise ValueError('resume_benchmark_mismatch')
        else:
            summary = replay(recorder)
            folder = ROOT / 'artifacts/reports/stage-4' / VERSION / 'runs' / summary['run_id']
            write_json(folder / 'summary.json', summary)
            for row in summary['results']:
                write_json(folder / (row['case_id'] + '-' + row['arm'] + '.json'), row)
        write_json(folder / 'langsmith-experiments.json', dict(runs=payloads_for(recorder, summary)))
        if args.upload:
            try:
                summary['dataset_sync'] = sync_results(recorder, dataset, summary, folder)
                recorder.status.update(summary['dataset_sync'], original_run_id=summary['run_id'], result_status=summary['status'])
                write_json(recorder.status_path, recorder.status)
                write_json(folder / 'langsmith-status.json', recorder.status)
            except Exception as exc:
                summary['dataset_sync'] = dict(status='pending_sync', error_type=type(exc).__name__)
                write_json(folder / 'summary.json', summary)
                raise
        write_json(folder / 'summary.json', summary)
        report(recorder, summary, folder)
        write_json(folder.parent.parent / 'latest.json', dict(directory=str(folder), run_id=summary['run_id']))
        print(json.dumps(dict(directory=str(folder), aggregates=json.loads((folder / 'comparison.json').read_text(encoding='utf-8'))['aggregates'],
            dataset_sync=summary.get('dataset_sync'), model_calls=0), ensure_ascii=False))
    finally:
        recorder.close()


if __name__ == '__main__':
    main()
