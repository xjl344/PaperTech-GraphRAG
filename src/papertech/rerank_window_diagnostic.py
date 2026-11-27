"""Fixed Hybrid candidates: full paragraphs versus gold-free quotation windows."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import html
import json
import math
from pathlib import Path
import time
import uuid

from .audit import Audit, now
from .corpus import load_corpus
from .entity_aliases import is_comparison
from .evaluation import support_metrics
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, detailed_output
from .evidence_context import assemble
from .local_models import run_worker
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings

VERSION = 'benchmark-rerank-window-v1'
ARMS = ('Whole-block', 'Quote-window')
CASE_IDS = ('F02', 'F07', 'R05', 'R24')
PARENT_RUN = 'artifacts/reports/stage-4/benchmark-relation-holdout-v1/runs/12b6c032bb3f4992944a1148ddc92bce'
FILES = ('src/papertech/rerank_window_diagnostic.py', 'src/papertech/rerank_runtime.py',
    'src/papertech/rerank_service.py', 'scripts/rerank-service.py', 'scripts/audit-rerank-inputs.py',
    'src/papertech/local_models.py', 'src/papertech/retrieval.py', 'src/papertech/evidence_context.py',
    'src/papertech/entity_aliases.py', 'src/papertech/evaluation_details.py', 'scripts/eval-stage4.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(root):
    directory = root / 'artifacts/eval/stage-4' / VERSION
    if (directory / 'benchmark.json').exists():
        return load_benchmark(root, VERSION)[0]
    parent, parent_sha, _ = load_benchmark(root, 'benchmark-relation-holdout-v1')
    summary_path = root / PARENT_RUN / 'summary.json'
    summary = json.loads(summary_path.read_text(encoding='utf8'))
    bench = deepcopy(parent)
    bench['cases'] = [deepcopy(c) for c in parent['cases'] if c['id'] in CASE_IDS]
    if tuple(c['id'] for c in bench['cases']) != CASE_IDS:
        raise ValueError('diagnostic_case_selection_changed')
    bench['units'] = {u: parent['units'][u] for c in bench['cases'] for u in c['units']}
    windows = json.loads((root / '.cache/rerank-input-audit/windows.json').read_text(encoding='utf8'))
    corpus, _, chunks = load_corpus(root)
    cm = {c['chunk_id']: c for c in chunks}
    selected = {r['case_id']: r for r in summary['results'] if r['arm'] == 'Hybrid' and r['case_id'] in CASE_IDS}
    candidates = {cid: sorted(deepcopy(row['ranked']), key=lambda r: (-r['score'], r['chunk_id']))
        for cid, row in selected.items()}
    ids = {r['chunk_id'] for rows in candidates.values() for r in rows}
    windows = {cid: windows[cid] for cid in sorted(ids)}
    for cid, fragments in windows.items():
        cursor = 0
        for fragment in fragments:
            fragment.pop('pair_tokens', None)  # Pair length depends on the query.
            start, end = fragment['start_char'], fragment['end_char']
            if start > cursor or fragment['text'] != cm[cid]['text'][start:end] or fragment['document_tokens'] > 160:
                raise ValueError('window_provenance_or_coverage_invalid')
            cursor = max(cursor, end)
        if cursor != len(cm[cid]['text']):
            raise ValueError('incomplete_window_coverage')
    input_audit = json.loads((root / '.cache/rerank-input-audit/audit.json').read_text(encoding='utf8'))
    if any(r['pair_tokens'] != r['query_tokens'] + r['document_tokens'] + 4 for r in input_audit['rows']):
        raise ValueError('tokenizer_pair_special_token_count_changed')
    bench.update(version=VERSION, parent_benchmark_sha256=parent_sha, parent_run=PARENT_RUN,
        parent_summary_sha256=sha(summary_path), corpus_id=corpus,
        distribution=dict(Counter(c['category'] for c in bench['cases'])),
        dataset_description='4题定点重排诊断：F02/F07单篇控制题，R05/R24复合题。固定Hybrid候选；整块vs无金标滑动引文窗口。不是总体检索质量评测。',
        prior_exposure='按已观察到的异常选择4题，有选择偏差；窗口仅依原文长度生成，不用参考答案、来源池或图Claim选窗。',
        comparison=dict(mode='fixed_candidate_rerank_input', arms=list(ARMS), generation=False),
        controls=dict(arms=list(ARMS), candidate_pool='same saved Hybrid candidates; no new recall',
            max_pair_tokens=1024, window_document_tokens=160, window_overlap='50% characters',
            window_score='max over all windows of each candidate; all candidates treated equally',
            window_selection='gold-free source-text lengths only; no claims or reference requirements',
            context='original full source chunks only, 6000 UTF-8 bytes, maximum 8; score threshold .05',
            order='alternate arm order by case index', generation_calls=0),
        scoring=dict(primary='R05/R24必要来源逐个记录候选存在性、重排排名与分数；池外来源标N/A，不补入。',
            secondary='Recall@5/@8、最终必要来源覆盖；整块分数与历史分数复现误差；仅4题描述性诊断。',
            causal_limit='两组原始输入均未超过1024时，排名变化不能归因于避免截断；可能涉及段落聚焦和max聚合偏差。',
            semantic_review='not assessed, generation not run',negative_policy='no negative cases in this selected subset'),
        frozen_candidates=candidates, windows=windows,
        parent_model_config=summary['execution_config']['models'],
        parent_reranker_model_id=next(r for r in summary['results'] if r['arm']=='Hybrid')['retrieval_summary']['reranker']['model_id'],
        parent_rows={cid: dict(scores={r['chunk_id']: r['rerank_score'] for r in row['ranked']},
            trace_url=row['trace_url']) for cid,row in selected.items()},
        tokenizer_audit=input_audit,
        code_sha256={name: sha(root / name) for name in FILES})
    write_json(directory / 'benchmark.json', bench)
    (directory / 'benchmark.sha256').write_text(sha(directory / 'benchmark.json')+'\n', encoding='utf8')
    return bench


def rerank_inputs(root, cfg, query, candidates, chunks, windows, arm):
    """Only query and frozen candidate text enter the model. No references."""
    tasks = []
    for candidate in candidates:
        cid = candidate['chunk_id']
        spans = [dict(text=chunks[cid]['text'], start_char=0, end_char=len(chunks[cid]['text']))] if arm == 'Whole-block' else windows[cid]
        tasks.extend(dict(chunk_id=cid, **span) for span in spans)
    scores, runs = [], []
    for start in range(0, len(tasks), 40):
        result = run_worker(root, cfg, 'rerank', [dict(text=t['text']) for t in tasks[start:start+40]], query=query, timeout=300)
        scores.extend(result.pop('outputs'))
        runs.append(result)
    if len(scores) != len(tasks):
        raise ValueError('rerank_result_length_mismatch')
    details = {}
    for task, score in zip(tasks, scores):
        details.setdefault(task['chunk_id'], []).append(dict(task, score=score))
    ranked = []
    for candidate in candidates:
        cid = candidate['chunk_id']
        best = max(details[cid], key=lambda t: t['score'])
        ranked.append(dict(candidate, rerank_score=best['score'], winning_window=dict(best), window_count=len(details[cid])))
    ranked.sort(key=lambda r: -r['rerank_score'])
    return dict(ranked=ranked, input_windows=details, model_runs=runs,
        model_pairs=len(tasks), reference_information_used=False)


class DiagnosticDataset(DetailedEvaluationDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload['metadata'].update(no_model_comparison_run=False, diagnostic_selected_cases=True)
        for e in self.payload['examples']:
            cid = e['metadata']['case_id']
            e['metadata']['review_origin'] = 'Codex source review; selected diagnostic subset'
            e['outputs'].update(reference_criteria=next(c for c in self.bench['cases'] if c['id']==cid)['reference_criteria'],
                frozen_candidate_ids=[r['chunk_id'] for r in self.bench['frozen_candidates'][cid]],
                input_window_policy=self.bench['controls'],selection_bias=self.bench['prior_exposure'])
            e['outputs']['result_display'].update(location='Whole-block / Quote-window Experiments',
                fields=['全部固定候选与原文','每个引文窗口与字符位置及分数','必要来源排名与缺口',
                    '真实Token长度与截断量','时延与评分对数','两组差异','原始Trace'])
            write_json(self.directory/'cases'/(cid+'.json'),e)
        write_json(self.directory/'langsmith-dataset.json',self.payload)

    def sync_run(self, summary_path, answer_mode='full'):
        folder = Path(summary_path).parent
        summary = json.loads(Path(summary_path).read_text(encoding='utf8'))
        if summary['benchmark_sha256'] != self.digest:
            raise ValueError('benchmark_mismatch')
        dataset = self.sync_dataset()
        cases = {c['id']:c for c in self.bench['cases']}
        seen, payloads = set(), []
        if any(not r.get('trace_url') for r in summary['results']):
            raise ValueError('trace_links_required_before_upload')
        paired = {cid:{r['arm']:r['target_ranks'] for r in summary['results'] if r['case_id']==cid} for cid in cases}
        for row in summary['results']:
            cid, arm = row['case_id'],row['arm']
            if (cid,arm) in seen or arm not in ARMS or row['question'] != cases[cid]['question']:
                raise ValueError('invalid_result')
            seen.add((cid,arm))
            out = detailed_output(row,cases[cid],self.bench,self.chunks)
            out.update({k:deepcopy(row[k]) for k in ('target_ranks','input_windows','tokenizer_audit',
                'model_pairs','model_runs','historical_full_score_max_error','usage_status','trace_url',
                'reranker_input_tokens_processed')})
            out.update(paired_required_source_ranks=paired[cid],generation_calls=0,generation_tokens=0,
                note='输入窗口无参考信息；max-window可能有窗口数量偏差；不是答案准确率。')
            metrics = dict(row['metrics'],rerank_compute_seconds=row['retrieval_compute_seconds'],
                rerank_model_pairs=row['model_pairs'],candidate_count=len(row['ranked']),generation_calls=0)
            payloads.append(dict(id=stable_id(self.digest,summary['run_id'],cid,arm),
                name='fixed-candidate-rerank-input',run_type='chain',inputs=dict(question=row['question']),outputs=out,
                reference_example_id=stable_id(self.digest,cid),start_time=row['started'],end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=VERSION,arm=arm,case_id=cid,generation=False,
                    original_run_id=summary['run_id'],candidate_source='frozen Hybrid',selected_diagnostic_subset=True)),
                tags=[VERSION,arm,row['category']],_arm=arm,_metrics={k:v for k,v in metrics.items() if v is not None}))
        if summary['status']=='completed' and seen != {(cid,a) for cid in cases for a in ARMS}:
            raise ValueError('incomplete_paired_results')
        write_json(folder/'langsmith-experiments.json',dict(runs=payloads))
        experiments=[]
        for arm in ARMS:
            expected={p['id']:p for p in payloads if p['_arm']==arm}
            if not expected:
                continue
            name=f'papertech-{VERSION}-{summary["run_id"][:12]}-{arm}'
            project=self.client.create_project(name,reference_dataset_id=dataset.id,upsert=True,
                description=self.bench['dataset_description'],metadata=dict(arm=arm,benchmark_sha256=self.digest))
            found={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            if set(found)-set(expected) or any(r.outputs!=expected[rid]['outputs'] for rid,r in found.items()):
                raise ValueError('remote_result_modified')
            for rid,p in expected.items():
                if rid not in found:
                    data={k:v for k,v in p.items() if not k.startswith('_')}
                    data['start_time']=datetime.fromisoformat(data['start_time'])
                    data['end_time']=datetime.fromisoformat(data['end_time'])
                    self.client.create_run(project_name=name,**data)
            jobs=[dict(run_id=p['id'],key=k,score=float(v),feedback_id=stable_id(p['id'],k),
                session_id=project.id,comment='固定候选输入诊断；来源覆盖不是答案准确率。') for p in expected.values() for k,v in p['_metrics'].items()]
            feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda j:self.client.create_feedback(**j),[j for j in jobs if j['feedback_id'] not in feedback]))
            for attempt in range(6):
                found={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
                feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
                valid=set(found)==set(expected) and all(r.outputs==expected[rid]['outputs'] and
                    r.inputs==expected[rid]['inputs'] and str(r.reference_example_id)==expected[rid]['reference_example_id'] for rid,r in found.items())
                valid=valid and all(j['feedback_id'] in feedback and math.isclose(feedback[j['feedback_id']].score,j['score'],abs_tol=.000050001) for j in jobs)
                if valid:
                    break
                if attempt==5:
                    raise ValueError('remote_readback_incomplete')
                time.sleep(2)
            self.client.update_project(project.id,end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(found),feedback_verified=len(jobs)))
        self.status.update(status='experiments_verified',experiments=experiments,
            comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments))
        write_json(self.status_path,self.status)
        write_json(folder/'langsmith-status.json',self.status)
        return deepcopy(self.status)


def report(recorder, summary, folder):
    esc=html.escape
    rows=summary['results']
    def average(group,key):
        return sum(r['metrics'][key] for r in group)/len(group) if group else None
    groups={category:{a:[r for r in rows if r['arm']==a and (category=='all' or r['category']==category)] for a in ARMS}
        for category in ('all','fact','cross')}
    stats={cat:{a:dict(count=len(group),evidence_coverage=average(group,'evidence_coverage'),recall5=average(group,'recall5'),
        model_pairs=sum(r['model_pairs'] for r in group),seconds=sum(r['retrieval_compute_seconds'] for r in group))
        for a,group in arms.items()} for cat,arms in groups.items()}
    write_json(folder/'comparison.json',dict(status=summary['status'],categories=stats))
    lines=['# 固定候选重排输入诊断','',f"状态：{summary['status']}。4道定点题，不是40题总体重测。",'',
        '整块与所有无金标160-token引文窗口分别评分；窗口组以每块最高分排序。最终证据仍用完整原文和原6000字节预算。','',
        '|题目|来源单元|整块排名/分数|窗口排名/分数|','|---|---|---:|---:|']
    page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>固定候选重排诊断</title>',
        '<style>body{font:15px system-ui;max-width:1200px;margin:32px auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:12px}td,th{padding:8px;border:1px solid #ccc}table{border-collapse:collapse}details{margin:12px 0}</style>',
        f'<h1>固定候选重排输入诊断：{summary["status"]}</h1>',
        '<p>F02/F07控制题，R05/R24异常题；两组均复用Hybrid候选。窗口只依原文分词长度生成，不用金标。max聚合存在窗口数量偏差，结果不能单独证明截断或总体优势。</p>']
    if summary.get('dataset_sync',{}).get('comparison_url'):
        url=summary['dataset_sync']['comparison_url']
        page.append(f'<p><a href="{esc(url,quote=True)}">LangSmith实验对照</a></p>')
        lines.extend(['','[LangSmith对照]('+url+')',''])
    page.append('<h2>分类覆盖与计算量</h2><pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre>')
    for cat in ('all','fact','cross'):
        parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 130"><title>{cat} final source coverage</title>']
        for i,a in enumerate(ARMS):
            v=stats[cat][a]['evidence_coverage']
            label='未运行' if v is None else f'{v:.2%}'
            width=(v or 0)*580;y=15+i*45
            parts.append(f'<text x="0" y="{y+20}">{a}</text><rect x="150" y="{y}" width="{width}" height="27" fill="{("#3975b7","#bc643d")[i]}"/><text x="{160+width}" y="{y+20}">{label}</text>')
        parts.append('<text x="150" y="125">0%</text><text x="705" y="125">100%</text></svg>')
        svg=''.join(parts)
        (folder/f'coverage-{cat}.svg').write_text(svg,encoding='utf8')
        page.extend([f'<h3>{cat}</h3>',svg])
    for case in recorder.bench['cases']:
        pair={r['arm']:r for r in rows if r['case_id']==case['id']}
        if set(pair)==set(ARMS):
            for i,target in enumerate(pair[ARMS[0]]['target_ranks']):
                other=pair[ARMS[1]]['target_ranks'][i]
                def fmt(t):
                    return '不在固定候选池' if t['rank'] is None else f"{t['rank']} / {t['score']:.6f}"
                lines.append(f"|{case['id']}|{target['unit_id']}|{fmt(target)}|{fmt(other)}|")
        page.append(f'<h2>{case["id"]} {esc(case["question"])}</h2>')
        example=next(e for e in recorder.payload['examples'] if e['metadata']['case_id']==case['id'])
        page.append('<details><summary>参考要点、来源原文与位置、评分口径</summary><pre>'+esc(json.dumps(example['outputs'],ensure_ascii=False,indent=2))+'</pre></details>')
        for arm,row in pair.items():
            page.append(f'<h3>{arm}</h3><pre>'+esc(json.dumps(row['target_ranks'],ensure_ascii=False,indent=2))+'</pre>')
            page.append('<details><summary>全部候选、窗口、分数、原文、证据、Token及耗时</summary><pre>'+esc(json.dumps(
                dict(detailed_output(row,case,recorder.bench,recorder.chunks),input_windows=row['input_windows'],
                    target_ranks=row['target_ranks'],tokenizer_audit=row['tokenizer_audit'],model_runs=row['model_runs']),ensure_ascii=False,indent=2))+'</pre></details>')
    lines.extend(['','[完整分类图表与逐题证据](dashboard.html)。','',
        '模型实际分词对数与输入Token长度已记录；它们是本地计算量，不是供应商账单Token。Embedding与生成调用均为0。',
        '未入池的必要来源不能因换重排输入而恢复。所有来源覆盖均不是答案语义正确率。'])
    (folder/'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (folder/'dashboard.html').write_text('\n'.join(page)+'</html>',encoding='utf8')


def execute(root,prepare_only=False,resume=None):
    root=Path(root)
    bench=freeze(root)
    recorder=DiagnosticDataset(root,VERSION)
    if resume:
        folder=Path(resume)
        summary=json.loads((folder/'summary.json').read_text(encoding='utf8'))
        summary['dataset_sync']=recorder.sync_run(folder/'summary.json')
        write_json(folder/'summary.json',summary)
        report(recorder,summary,folder)
        print(json.dumps(summary['dataset_sync'],ensure_ascii=False),flush=True)
        recorder.close()
        return
    if {name:sha(root/name) for name in FILES}!=bench['code_sha256']:
        raise ValueError('frozen_diagnostic_code_changed')
    if prepare_only:
        print(json.dumps(dict(status='not_run',benchmark=VERSION,sha256=recorder.digest,cases=CASE_IDS),ensure_ascii=False))
        recorder.close()
        return
    cfg=settings(root)
    if any(cfg.get(k)!=v for k,v in bench['parent_model_config'].items()):
        raise ValueError('model_configuration_changed')
    recorder.sync_dataset()  # Required gate before any model inference.
    run_id=uuid.uuid4().hex
    folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/run_id
    summary=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=recorder.digest,status='running',started=now(),results=[])
    write_json(folder/'summary.json',summary)
    report(recorder,summary,folder)
    audit=Audit(root)
    roots=[]
    try:
        rid=audit.start('[fixed-candidate reranker warmup]');roots.append(audit.live_requests[rid])
        warm=audit.stage(rid,'warmup',lambda:run_worker(root,cfg,'rerank',[dict(text='Evidence for a factual query.')],query='evidence',timeout=240))
        warm.pop('outputs',None)
        if warm['model_id']!=bench['parent_reranker_model_id']:
            raise ValueError('reranker_fingerprint_changed')
        audit.finish(rid,dict(status='completed',retrieval_summary=warm))
        summary['warmup']=warm
        for n,case in enumerate(bench['cases']):
            order=ARMS[n%2:]+ARMS[:n%2]
            candidates=bench['frozen_candidates'][case['id']]
            for arm in order:
                rid=audit.start(case['question']);roots.append(audit.live_requests[rid])
                started=now();begin=time.monotonic()
                result=audit.stage(rid,'rerank_'+arm,lambda:rerank_inputs(root,cfg,normalize(case['question']),
                    candidates,recorder.chunks,bench['windows'],arm))
                seconds=sum(r['inference_seconds'] for r in result['model_runs'])
                evidence,_,details=assemble(result['ranked'],recorder.chunks,[],case['question'],is_comparison(case['question']),budget=6000,path_budget=0)
                row=dict(case_id=case['id'],category=case['category'],arm=arm,question=case['question'],
                    request_id=rid,started=started,finished=now(),status='evidence_only' if evidence else 'no_evidence',errors=[],
                    ranked=result['ranked'],evidence=evidence,graph_paths=[],generation_paths=[],citations=[],
                    candidate_channels=dict(frozen_hybrid=[dict(chunk_id=r['chunk_id'],score=r['score']) for r in candidates]),
                    retrieval_summary=dict(details,arm=arm,candidate_count=len(candidates),graph_fallback=False),
                    answer='仅重排输入诊断，无答案生成。',usage=None,generate_requested=False,provider_calls=[],
                    retrieval_compute_seconds=seconds,request_wall_seconds=time.monotonic()-begin,
                    compute_timings=[dict(name='rerank_inference',seconds=seconds)],model_name=None,
                    input_windows=result['input_windows'],model_pairs=result['model_pairs'],model_runs=result['model_runs'],
                    usage_status='generation=0; embedding=0; reranker input lengths/pairs reported locally, no billing usage',
                    historical_full_score_max_error=max(abs(r['rerank_score']-bench['parent_rows'][case['id']]['scores'][r['chunk_id']]) for r in result['ranked']) if arm=='Whole-block' else None)
                row['metrics']=support_metrics([r['chunk_id'] for r in row['ranked']],[e['chunk_id'] for e in evidence],[bench['units'][u] for u in case['units']])
                indexed={r['chunk_id']:(i,r['rerank_score']) for i,r in enumerate(row['ranked'],1)}
                row['target_ranks']=[]
                for uid in case['units']:
                    unit=bench['units'][uid]
                    matches=[(cid,*indexed[cid]) for cid in unit['known_support_chunks'] if cid in indexed]
                    best=min(matches,key=lambda m:m[1]) if matches else (unit['primary_chunk'],None,None)
                    row['target_ranks'].append(dict(unit_id=uid,requirement=unit['answer_point'],chunk_id=best[0],
                        rank=best[1],score=best[2],candidate_present=bool(matches),selected=any(e['chunk_id'] in unit['known_support_chunks'] for e in evidence)))
                row['tokenizer_audit']=[r for r in bench['tokenizer_audit']['rows'] if r['arm']=='Hybrid' and r['case_id']==case['id']]
                qtokens=row['tokenizer_audit'][0]['query_tokens']
                counts={r['chunk_id']:r['document_tokens'] for r in row['tokenizer_audit']}
                for cid, fragments in row['input_windows'].items():
                    for fragment in fragments:
                        fragment['pair_tokens'] = qtokens + fragment.get('document_tokens',counts[cid]) + 4
                row['reranker_input_tokens_processed'] = sum(w['pair_tokens'] for ws in row['input_windows'].values() for w in ws)
                audit.finish(rid,row)
                row['trace_id']=audit.live_requests[rid]
                row['trace_url']=None
                summary['results'].append(row)
                write_json(folder/f'{case["id"]}-{arm}.json',row)
                write_json(folder/'summary.json',summary)
                print(json.dumps(dict(case=case['id'],arm=arm,model_pairs=row['model_pairs'],coverage=row['metrics']['evidence_coverage'],targets=row['target_ranks']),ensure_ascii=False),flush=True)
        summary.update(status='completed',finished=now())
    except BaseException as exc:
        summary.update(status='interrupted',error_type=type(exc).__name__,finished=now())
        raise
    finally:
        write_json(folder/'summary.json',summary)
        try:
            from .relation_holdout_evaluation import verify_traces, hydrate_trace_urls
            for attempt in range(5):
                verification=verify_traces(audit.live,roots)
                if verification['verified']:
                    break
                time.sleep(2)
            summary['trace_verification']=verification
            if not verification['verified']:
                raise ValueError('trace_readback_pending')
            hydrate_trace_urls(recorder.connect(),summary,folder)
            write_json(folder/'summary.json',summary)
            if summary['results']:
                summary['dataset_sync']=recorder.sync_run(folder/'summary.json')
        except Exception as exc:
            summary['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
        write_json(folder/'summary.json',summary)
        report(recorder,summary,folder)
        write_json(folder.parent.parent/'latest.json',dict(directory=str(folder),status=summary['status']))
        audit.close();recorder.close();close_workers()
        print(json.dumps(dict(status=summary['status'],directory=str(folder),sync=summary.get('dataset_sync')),ensure_ascii=False),flush=True)
