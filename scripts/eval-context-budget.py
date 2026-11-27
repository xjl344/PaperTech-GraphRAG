"""Three-arm context budget replay on the existing 16-question diagnostic dataset."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import csv
import hashlib
import importlib.util
import json
import logging
from pathlib import Path
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.entity_aliases import is_comparison
from papertech.evidence_context import assemble, content_bytes, path_prompt
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import DetailedEvaluationDataset

spec=importlib.util.spec_from_file_location('source_replay_tools',ROOT/'scripts/eval-source-coverage.py')
tools=importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)
VERSION=tools.VERSION
ARMS=('Budget-before','Evidence-first','Compact-paths')
BASELINE=ROOT/'artifacts/reports/stage-4'/VERSION/'context-budget-baseline'
CODE=('src/papertech/evidence_context.py','src/papertech/workflow.py','src/papertech/providers.py',
      'scripts/eval-context-budget.py','scripts/eval-source-coverage.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline():
    contract=json.loads((BASELINE/'contract.json').read_text(encoding='utf-8'))
    for name,digest in contract['files'].items():
        if sha(BASELINE/Path(name).name)!=digest:
            raise ValueError('step1_snapshot_changed')
    # Source recognition and candidate scoring are fixed in this experiment.
    for name in ('src/papertech/entity_aliases.py','src/papertech/retrieval.py','src/papertech/citations.py'):
        if sha(ROOT/name)!=contract['files'][name]:
            raise ValueError('fixed_stage_changed:'+name)
    spec=importlib.util.spec_from_file_location('papertech._context_budget_baseline',BASELINE/'evidence_context.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parent=ROOT/'artifacts/reports/stage-4'/VERSION/'runs'/contract['parent_run_id']/'summary.json'
    if sha(parent)!=contract['parent_summary_sha256']:
        raise ValueError('step1_results_changed')
    return module.assemble,contract,json.loads(parent.read_text(encoding='utf-8'))


def replay(recorder,folder,run_id):
    old,contract,parent=baseline()
    originals={row['case_id']:row for row in parent['results'] if row['arm']=='Graph-after'}
    execution=dict(benchmark=VERSION,benchmark_sha256=recorder.digest,run_id=run_id,
        mode='context_budget_evidence_replay',arms=list(ARMS),budget_bytes=6000,max_evidence=8,max_paths=4,
        parent_run_id=parent['run_id'],parent_summary_sha256=contract['parent_summary_sha256'],
        baseline_contract_sha256=sha(BASELINE/'contract.json'),
        fixed=['16 questions and reference facts','ranked candidates and scores','retrieved graph paths',
               'source reservation','rerank score threshold','6000-byte context budget'],
        interventions={'Budget-before':'Step1 path reservation may evict evidence; full quotes in paths.',
            'Evidence-first':'Keep selected original text. Full paths only use leftover budget.',
            'Compact-paths':'Same original text as Evidence-first. Path references use existing chunk/quote IDs.'},
        metrics='No gold enters assembly. Compare retained source papers, frozen fact coverage, paths, bytes and assembly time.',
        scope='Evidence/path payload budget excludes question, system prompt and limitations; bytes are not tokens.',
        model_calls=0,code_sha256={name:sha(ROOT/name) for name in CODE})
    write_json(folder/'execution-contract.json',execution)
    summary=dict(benchmark=VERSION,benchmark_sha256=recorder.digest,run_id=run_id,status='running',
        mode=execution['mode'],parent_run_id=parent['run_id'],arms=list(ARMS),results=[],
        model_calls=0,generation_calls=0,new_generation_tokens=None,code_sha256=execution['code_sha256'])
    write_json(folder/'summary.json',summary)
    for case in recorder.bench['cases']:
        original=originals[case['id']]
        for index,arm in enumerate(ARMS):
            started=datetime.now(timezone.utc)
            begin=time.perf_counter()
            arguments=(original['ranked'],recorder.chunks,original['graph_paths'],case['question'],is_comparison(case['question']))
            if index==0:
                evidence,paths,detail=old(*arguments)
                if evidence!=original['evidence'] or paths!=original['generation_paths']:
                    raise ValueError('step1_baseline_not_reproduced:'+case['id'])
                prompt_paths=deepcopy(paths)
            else:
                evidence,paths,detail=assemble(*arguments,path_format='full' if index==1 else 'references')
                prompt_paths=detail['prompt_graph_paths']
            elapsed=time.perf_counter()-begin
            ended=datetime.now(timezone.utc)
            exact=content_bytes(evidence,prompt_paths)
            if detail['context_bytes']>6000 or exact>6000 or len(evidence)>8 or len(paths)>4:
                raise ValueError('context_budget_or_count_exceeded')
            allowed={e['chunk_id']:e for e in evidence}
            expected=[path_prompt(path,allowed,'references' if index==2 else 'full') for path in paths]
            if any(path is None for path in expected) or expected!=prompt_paths:
                raise ValueError('path_provenance_or_prompt_mismatch')
            if index and not {e['chunk_id'] for e in original['evidence']}.issubset(allowed):
                raise ValueError('evidence_first_removed_original_text')
            detail.update(prompt_graph_paths=prompt_paths,serialized_content_bytes=exact,
                path_policy='step1_path_reservation' if index==0 else 'evidence_first',
                path_format='references' if index==2 else 'full')
            row=dict(case_id=case['id'],question=case['question'],category=case['category'],arm=arm,
                status='evidence_only',answer='本轮仅回放上下文预算与路径表示，没有生成新回答。',
                evidence=evidence,graph_paths=deepcopy(original['graph_paths']),generation_paths=paths,
                prompt_graph_paths=prompt_paths,ranked=deepcopy(original['ranked']),citations=[],usage=None,
                model_name=None,provider_calls=[],generate_requested=False,order=index+1,errors=[],
                limitations=detail['limitations'],retrieval_summary=detail,
                compute_timings=[dict(name='evidence',seconds=elapsed)],
                stage_timings=[dict(name='evidence',seconds=elapsed,status='ok')],
                assembly_seconds=elapsed,start_time=started.isoformat(),end_time=ended.isoformat(),
                trace_url=original['trace_url'],request_id=original['request_id'],
                source_metrics=tools.source_metrics(case,recorder.bench,evidence),
                parent_generation=deepcopy(original['parent_generation']))
            row['metrics']=support_metrics([x['chunk_id'] for x in row['ranked']],
                [x['chunk_id'] for x in evidence],[recorder.bench['units'][u] for u in case['units']])
            summary['results'].append(row)
            write_json(folder/(case['id']+'-'+arm+'.json'),row)
            write_json(folder/'summary.json',summary)
    for case in recorder.bench['cases']:
        a,b=[next(row for row in summary['results'] if row['case_id']==case['id'] and row['arm']==arm) for arm in ARMS[1:]]
        if a['evidence']!=b['evidence']:
            raise ValueError('path_format_changed_source_selection')
    summary.update(status='completed',finished=datetime.now(timezone.utc).isoformat())
    write_json(folder/'summary.json',summary)
    return summary


def diagnostics(summary):
    records={}
    for cid in dict.fromkeys(row['case_id'] for row in summary['results']):
        rows={row['arm']:row for row in summary['results'] if row['case_id']==cid}
        original=rows[ARMS[0]]
        before={e['chunk_id'] for e in original['evidence']}
        changes={}
        for arm,row in rows.items():
            after={e['chunk_id'] for e in row['evidence']}
            changes[arm]=dict(added_chunk_ids=sorted(after-before),removed_chunk_ids=sorted(before-after),
                fact_coverage_delta=row['metrics']['evidence_coverage']-original['metrics']['evidence_coverage'],
                paths=len(row['generation_paths']),graph_context_bytes=row['retrieval_summary']['graph_context_bytes'])
        note='固定候选与来源保留；只修改原文/路径预算及路径表示。无新生成，事实覆盖不等于语义准确率。'
        if cid=='R12':note+='原文优先恢复被路径占位挤出的 Tree-of-Traversals 的 totmusic 支持块；路径在剩余预算不足时省略。'
        if cid=='R18':note+='事实覆盖仍为 0；本题基线没有入选图路径，第一步的来源占位与段落选择问题未被第二步解决。'
        if cid=='R20':note+='固定候选中的 KGP 来源门槛缺口仍保留，预算策略不能产生新候选。'
        if cid=='R19':note+='紧凑路径使用已提供原文的 chunk/quote ID，减少重复文本；原始引句完整保存在审计路径。'
        records[cid]=dict(case_id=cid,changes=changes,note=note,
            review_kind='程序差异与 Codex 定向说明；非独立专家语义评分')
    return records


def payloads(recorder,summary):
    result=tools.payloads_for(recorder,summary)
    rows={(r['case_id'],r['arm']):r for r in summary['results']}
    for p in result:
        row=rows[p['extra']['metadata']['case_id'],p['_arm']]
        d=row['retrieval_summary']
        p['outputs'].update(prompt_graph_paths=row['prompt_graph_paths'],
            timing_note='原生时延仅为本次证据组装回放；没有重新检索、重排或生成。',
            context_budget=dict(policy=d['path_policy'],path_format=d['path_format'],
                budget_bytes=6000,serialized_content_bytes=d['serialized_content_bytes'],
                budget_boundary='evidence and graph_paths only; excludes question, system prompt and limitations'))
        p['_metrics'].update(serialized_content_bytes=d['serialized_content_bytes'],
            generation_path_count=len(row['generation_paths']))
        p['extra']['metadata'].update(capture_mode=summary['mode'],step='context_budget_v1',
            path_policy=d['path_policy'],path_format=d['path_format'])
    return result


def report(recorder,summary,folder):
    notes=diagnostics(summary)
    output=payloads(recorder,summary)
    groups={cid:{row['arm']:row for row in summary['results'] if row['case_id']==cid} for cid in notes}
    aggs={}
    for arm in ARMS:
        rows=[row for row in summary['results'] if row['arm']==arm]
        avg=lambda fn:sum(fn(row) for row in rows)/len(rows)
        aggs[arm]=dict(questions=len(rows),all_required_papers=sum(r['source_metrics']['all_required_papers'] for r in rows),
            required_paper_coverage=avg(lambda r:r['source_metrics']['required_paper_coverage']),
            evidence_coverage=avg(lambda r:r['metrics']['evidence_coverage']),all_units=sum(r['metrics']['all_units'] for r in rows),
            evidence_count=avg(lambda r:len(r['evidence'])),generation_path_queries=sum(bool(r['generation_paths']) for r in rows),
            generation_path_count=sum(len(r['generation_paths']) for r in rows),
            context_bytes=avg(lambda r:r['retrieval_summary']['context_bytes']),
            graph_context_bytes=avg(lambda r:r['retrieval_summary']['graph_context_bytes']),
            serialized_content_bytes=avg(lambda r:r['retrieval_summary']['serialized_content_bytes']),
            assembly_milliseconds=1000*avg(lambda r:r['assembly_seconds']),generation_calls=0,
            statuses=dict(Counter(r['status'] for r in rows)))
    changes={arm:dict(Counter('gain' if g[arm]['metrics']['evidence_coverage']>g[ARMS[0]]['metrics']['evidence_coverage'] else
        'regression' if g[arm]['metrics']['evidence_coverage']<g[ARMS[0]]['metrics']['evidence_coverage'] else 'tie'
        for g in groups.values())) for arm in ARMS[1:]}
    data=dict(benchmark=VERSION,run_id=summary['run_id'],mode=summary['mode'],arms=list(ARMS),
        aggregates=aggs,fact_coverage_changes=changes,diagnostics=notes,dataset_sync=summary.get('dataset_sync'),
        references={e['metadata']['case_id']:e['outputs'] for e in recorder.payload['examples']},
        results={cid:{arm:next(p['outputs'] for p in output if p['_arm']==arm and p['extra']['metadata']['case_id']==cid)
            for arm in ARMS} for cid in groups})
    write_json(folder/'comparison.json',data)
    write_json(folder/'diagnostics.json',notes)
    lines=['# 第二步：上下文预算三组回放','',
        '复用 16 道失败诊断题及原金标，固定候选、分数、图路径、第一步来源保留与 6000 字节预算。没有新模型调用。','',
        '| 指标 | 第一步基线 | 原文优先、完整路径 | 原文优先、紧凑路径 |','|---|---:|---:|---:|']
    for label,key,percent in [('必要论文全部入选题数','all_required_papers',False),('必要论文覆盖','required_paper_coverage',True),
            ('冻结事实覆盖','evidence_coverage',True),('必要事实全覆盖题数','all_units',False),('平均原文块数','evidence_count',False),
            ('含生成路径题数','generation_path_queries',False),('平均路径字节','graph_context_bytes',False),
            ('平均证据/路径实际序列化字节','serialized_content_bytes',False),('平均组装毫秒','assembly_milliseconds',False)]:
        vals=[f"{100*aggs[a][key]:.2f}%" if percent else f"{aggs[a][key]:.3f}" for a in ARMS]
        lines.append('| '+label+' | '+' | '.join(vals)+' |')
    lines+=['',f'事实覆盖逐题变化（对第一步基线）：{changes}。','',
        '| 题目 | 基线 / 原文优先 / 紧凑路径事实覆盖 | 原文块数 | 路径条数 |','|---|---|---|---|']
    for cid,g in groups.items():
        lines.append('| '+cid+' | '+' / '.join(f"{g[a]['metrics']['evidence_coverage']:.3f}" for a in ARMS)+' | '+
            ' / '.join(str(len(g[a]['evidence'])) for a in ARMS)+' | '+' / '.join(str(len(g[a]['generation_paths'])) for a in ARMS)+' |')
    lines+=['','R12 恢复一项支持；R18 未恢复、R20 来源缺口保留。紧凑表示不改变原文选择。',
        '路径可能因剩余空间不足而省略，不能由本轮推断路径更少必然有利于生成。',
        '预算以 UTF-8 字节计，不是 Token；仅覆盖 evidence/graph_paths，不包含问题、系统提示词和缺口说明。',
        '全部历史回答、引用、Token、Trace 在 parent_generation 中单列，不能作为本轮新回答。',
        '诊断题是有偏失败集；未重新生成、未做独立语义评分，也未验证实时检索的整体收益。','',
        '[汇总柱状图与全部逐题详情](dashboard.html) · [逐题 CSV](per-question.csv)']
    if summary.get('dataset_sync',{}).get('comparison_url'):
        lines+=['','[LangSmith 三组对照]('+summary['dataset_sync']['comparison_url']+')']
    (folder/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    with (folder/'per-question.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['case_id','arm','fact_coverage','source_coverage','evidence_count',
            'path_count','budget_context_bytes','serialized_content_bytes','graph_context_bytes','assembly_seconds','status','new_generation_calls'])
        writer.writeheader()
        for row in summary['results']:
            d=row['retrieval_summary']
            writer.writerow(dict(case_id=row['case_id'],arm=row['arm'],fact_coverage=row['metrics']['evidence_coverage'],
                source_coverage=row['source_metrics']['required_paper_coverage'],evidence_count=len(row['evidence']),
                path_count=len(row['generation_paths']),budget_context_bytes=d['context_bytes'],
                serialized_content_bytes=d['serialized_content_bytes'],graph_context_bytes=d['graph_context_bytes'],
                assembly_seconds=row['assembly_seconds'],status=row['status'],new_generation_calls=0))
    (folder/'dashboard.html').write_text(HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\u003c')),encoding='utf-8')
    return data


HTML=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第二步：上下文预算对照</title>
<style>body{font:15px/1.7 system-ui,"Microsoft YaHei";max-width:1440px;margin:auto;padding:24px;background:#f5f7fb;color:#20304a}section{background:white;border:1px solid #dbe2ed;border-radius:10px;padding:20px;margin:20px 0}.plots{display:grid;grid-template-columns:1fr 1fr;gap:20px}.arms{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.bar{height:20px;margin:5px 0}.a0{background:#64748b}.a1{background:#3974b9}.a2{background:#d8843d}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}pre{white-space:pre-wrap;word-break:break-word;max-height:650px;overflow:auto;background:#f6f7fa;padding:12px;font-size:12px}button,input{font:inherit;padding:6px}a{color:#245cad}summary{cursor:pointer}@media(max-width:900px){.arms,.plots{grid-template-columns:1fr}}</style>
<h1>第二步：原文与图路径的预算</h1><p id="run"></p><p>16 道固定失败诊断题；三组共用候选、分数、来源保留和 6000 字节预算。只回放证据组装，没有新模型生成。</p><nav id="links"></nav>
<section><h2>汇总指标与柱状图</h2><div class="plots" id="charts"></div><p id="basic"></p></section>
<section><h2>分类与状态</h2><p>题型：跨文本关系 16 题。三组各 16 条 evidence_only；新检索、重排、生成均 0 次，新生成 Token 不适用。时延为单次证据组装，不是完整请求时延。</p><p>字节预算仅包含原文证据与图路径，问题、系统提示词及缺口说明另计。事实覆盖来自有限支持池，不是答案准确率。</p></section>
<section><h2>逐题对照</h2><input id="search" placeholder="搜索题号或问题"><p id="count"></p><div style="overflow:auto"><table><thead><tr><th>题目</th><th>三组事实覆盖</th><th>原文块数</th><th>路径数</th><th></th></tr></thead><tbody id="rows"></tbody></table></div></section>
<section id="detail"><h2>选择题目查看完整结果</h2></section><script>
const DATA=__DATA__,ARMS=DATA.arms,LABELS={'Budget-before':'第一步基线','Evidence-first':'原文优先、完整路径','Compact-paths':'原文优先、紧凑路径'};
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
$('run').textContent=DATA.run_id+' · 16 题 / 48 条回放结果';$('links').innerHTML='<a href="comparison.md">文字报告</a> · <a href="comparison.json">完整数据 JSON</a> · <a href="per-question.csv">逐题 CSV</a>'+(DATA.dataset_sync?.comparison_url?' · <a target="_blank" rel="noopener" href="'+esc(DATA.dataset_sync.comparison_url)+'">LangSmith 三组对照</a>':'');
$('charts').innerHTML=[['必要论文全部入选题数','all_required_papers',16],['必要论文覆盖','required_paper_coverage',1],['冻结事实覆盖','evidence_coverage',1],['全部必要事实覆盖题数','all_units',16],['平均原文块数','evidence_count',8],['含生成路径题数','generation_path_queries',16],['平均路径字节','graph_context_bytes',null],['平均实际序列化字节','serialized_content_bytes',6000],['平均证据组装毫秒','assembly_milliseconds',null]].map(([label,key,scale])=>{const max=scale??Math.max(0.001,...ARMS.map(a=>DATA.aggregates[a][key]));return '<div><b>'+label+'</b>'+ARMS.map((a,i)=>{const v=DATA.aggregates[a][key];return '<div>'+LABELS[a]+'：'+(scale===1?(100*v).toFixed(2)+'%':v.toFixed(3))+'</div><div class="bar a'+i+'" style="width:'+(100*v/max)+'%"></div>'}).join('')+'</div>'}).join('');
$('basic').textContent='相对第一步的事实覆盖变化：'+JSON.stringify(DATA.fact_coverage_changes)+'。原文优先不为路径移除证据；紧凑路径以 chunk_id、quote_ids 及字符位置关联原文。';
function table(){const q=$('search').value.toLowerCase(),items=Object.entries(DATA.results).filter(([id,p])=>(id+' '+p[ARMS[0]].question).toLowerCase().includes(q));$('count').textContent='显示 '+items.length+' / 16 题';$('rows').innerHTML=items.map(([id,p])=>'<tr><td>'+id+'<br>'+esc(p[ARMS[0]].question)+'</td><td>'+ARMS.map(a=>(100*p[a].metrics.evidence_coverage).toFixed(1)+'%').join(' / ')+'</td><td>'+ARMS.map(a=>p[a].evidence.length).join(' / ')+'</td><td>'+ARMS.map(a=>p[a].generation_paths.length).join(' / ')+'</td><td><button data-id="'+id+'">详情</button></td></tr>').join('');$('rows').querySelectorAll('button').forEach(b=>b.onclick=()=>show(b.dataset.id))}
function block(name,value,open=false){return '<details'+(open?' open':'')+'><summary>'+esc(name)+'</summary><pre>'+esc(JSON.stringify(value,null,2))+'</pre></details>'}
function show(id){let html='<h2>'+id+'</h2>'+block('参考答案、全部来源位置与评分口径',DATA.references[id])+block('三组增减、退化与缺口诊断',DATA.diagnostics[id],true)+'<div class="arms">';for(const a of ARMS){const x=DATA.results[id][a];html+='<div><h3>'+LABELS[a]+'</h3>'+block('本轮状态、指标、耗时与 Token',{status:x.status,answer:x.answer,metrics:x.metrics,source_metrics:x.source_metrics,assembly_seconds:x.assembly_seconds,generation_calls:x.generation_calls,new_generation_tokens:x.new_generation_tokens},true)+block('入选原文证据及位置',x.evidence,true)+block('路径发送给模型时的内容（本轮未调用）',x.prompt_graph_paths)+block('完整入选路径与原始引句血缘',x.generation_paths)+block('全部检索图路径',x.graph_paths)+block('全部固定候选及分数',x.ranked_candidates)+block('逐事实支持及缺口',{fact_coverage:x.fact_coverage,missing_required_facts:x.missing_required_facts})+block('预算、来源保留与限制',x.retrieval_summary)+block('历史回答、引用、Token 与 Trace（不是本轮新结果）',x.parent_generation);if(x.parent_generation.trace_url)html+='<a target="_blank" rel="noopener" href="'+esc(x.parent_generation.trace_url)+'">父运行 Trace</a>';html+='</div>'}html+='</div>';$('detail').innerHTML=html;$('detail').scrollIntoView({behavior:'smooth'})}
$('search').oninput=table;table();</script></html>'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upload',action='store_true')
    parser.add_argument('--resume',type=Path,help='Rebuild or upload saved results without replay.')
    args=parser.parse_args()
    logging.getLogger('langsmith').setLevel(logging.CRITICAL)
    recorder=DetailedEvaluationDataset(ROOT,VERSION)
    try:
        dataset=recorder.sync_dataset() if args.upload else None
        if args.resume:
            folder=args.resume.parent
            summary=json.loads(args.resume.read_text(encoding='utf-8'))
            if summary['benchmark_sha256']!=recorder.digest or summary['mode']!='context_budget_evidence_replay':
                raise ValueError('context_budget_resume_mismatch')
        else:
            run_id=uuid.uuid4().hex
            folder=ROOT/'artifacts/reports/stage-4'/VERSION/'context-budget-runs'/run_id
            summary=replay(recorder,folder,run_id)
        write_json(folder/'langsmith-experiments.json',dict(runs=payloads(recorder,summary)))
        if args.upload:
            try:
                summary['dataset_sync']=tools.sync_results(recorder,dataset,summary,folder,arms=ARMS,
                    payloads=payloads(recorder,summary),notes=diagnostics(summary),diagnostic_key='context_budget_diagnostics',
                    description='第二步：第一步基线、原文优先完整路径、原文优先紧凑路径。固定16题候选和6000字节，无新生成。')
                write_json(folder/'langsmith-status.json',dict(summary['dataset_sync'],run_id=summary['run_id'],mode=summary['mode']))
            except Exception as exc:
                summary['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
                write_json(folder/'summary.json',summary)
                report(recorder,summary,folder)
                raise
        write_json(folder/'summary.json',summary)
        data=report(recorder,summary,folder)
        write_json(ROOT/'artifacts/reports/stage-4'/VERSION/'latest-context-budget.json',dict(directory=str(folder),run_id=summary['run_id']))
        print(json.dumps(dict(directory=str(folder),aggregates=data['aggregates'],fact_coverage_changes=data['fact_coverage_changes'],
            dataset_sync=summary.get('dataset_sync'),model_calls=0),ensure_ascii=False))
    finally:
        recorder.close()


if __name__=='__main__':
    main()
