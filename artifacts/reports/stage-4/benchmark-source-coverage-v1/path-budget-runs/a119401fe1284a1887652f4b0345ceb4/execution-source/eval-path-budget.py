"""Compare reserved path quotas on frozen real candidates; resume only exports."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.audit import now
from papertech.evidence_context import assemble, content_bytes, path_prompt
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import stable_id, write_json
from papertech.evaluation_details import DetailedEvaluationDataset, detailed_output
from papertech.ingest import exclusive_lock
from papertech.settings import settings
from papertech.workflow import Workflow

VERSION = 'benchmark-source-coverage-v1'
ARMS = {'Path-0': 0, 'Path-800': 800, 'Path-1200': 1200}
RUN_ROOT = ROOT / 'artifacts/reports/stage-4' / VERSION / 'path-budget-runs'
PARENT = ROOT / 'artifacts/reports/stage-4' / VERSION / 'optimization-runs/5351b670c38d41348d772f73a4ab2517'
CODE = ('src/papertech/evidence_context.py', 'src/papertech/workflow.py',
        'src/papertech/providers.py', 'src/papertech/retrieval.py', 'src/papertech/citations.py',
        'src/papertech/evaluation.py', 'scripts/eval-path-budget.py', 'scripts/eval-stage4.py',
        'scripts/path-budget-dashboard.html')
NOTICE = '图路径仅用于定位和理解关联；引用必须来自 evidence 中可核对的原文，不能将图边本身当作论断证据。'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [plain(v) for v in value]
    return value


def percentile(values, q=.95):
    if not values:
        return None
    values = sorted(values)
    position = (len(values)-1)*q
    lo = int(position)
    return values[lo] + (values[min(lo+1, len(values)-1)]-values[lo])*(position-lo)


def source_metrics(case, bench, evidence):
    required = {bench['units'][uid]['paper_id'] for uid in case['units']}
    selected = {e['paper_id'] for e in evidence}
    return dict(all_required_papers=required.issubset(selected),
        required_paper_coverage=len(required & selected)/len(required),
        missing_paper_ids=sorted(required-selected))


def prepare(recorder, folder, run_id):
    parent = read(PARENT / 'summary.json')
    if parent['benchmark_sha256'] != recorder.digest:
        raise ValueError('parent_benchmark_mismatch')
    contract = dict(benchmark=VERSION, benchmark_sha256=recorder.digest, run_id=run_id,
        mode='fixed_real_candidates_reserved_path_quota_with_new_generation',
        parent_run_id=parent['run_id'], parent_summary_sha256=sha(PARENT/'summary.json'),
        total_budget_bytes=6000, arms=ARMS, max_evidence=8, max_paths=4,
        zero_semantics='legacy evidence-first; paths may use leftover space, not graph disabled',
        positive_semantics='hard quota within 6000; evidence gets 6000-path_budget; unused quota not lent back',
        fixed=['questions and reference facts', 'ranked candidates and scores', 'retrieved graph paths',
               'source reservation', 'same model and system prompt', 'same extra path grounding instruction'],
        scoring='Frozen support-pool ID coverage and necessary paper coverage; not semantic correctness.',
        generation_sampling='one fresh sample per arm; rotate arm order per question; no automatic retry of failed answers',
        latency_boundary='assembly+generation+citations measured; retrieval is replayed, no fresh end-to-end retrieval latency',
        gold_boundary='reference facts used by evaluator only, never sent into assembly or generation',
        extra_generation_instruction=NOTICE,
        code_sha256={name: sha(ROOT/name) for name in CODE}, candidates_sha256={})
    summary = dict(benchmark=VERSION, benchmark_sha256=recorder.digest, run_id=run_id,
        parent_run_id=parent['run_id'], mode=contract['mode'], arms=ARMS, status='not_run',
        started=now(), results=[], model_calls=0, generation_calls=0, dataset_sync=dict(status='pending'))
    for case in recorder.bench['cases']:
        snapshot = read(PARENT/(case['id']+'-candidates.json'))
        if snapshot['question'] != case['question']:
            raise ValueError('snapshot_question_mismatch')
        write_json(folder/(case['id']+'-candidates.json'), snapshot)
        contract['candidates_sha256'][case['id']] = sha(folder/(case['id']+'-candidates.json'))
        for arm, quota in ARMS.items():
            start = time.perf_counter()
            evidence, paths, detail = assemble(snapshot['ranked'], recorder.chunks, snapshot['graph_paths'],
                case['question'], path_budget=quota)
            elapsed = time.perf_counter()-start
            metrics = support_metrics([r['chunk_id'] for r in snapshot['ranked']],
                [e['chunk_id'] for e in evidence], [recorder.bench['units'][u] for u in case['units']])
            if quota == 0:
                old = parent['stage2']['results'][case['id']]['Evidence-first']
                if ([e['chunk_id'] for e in evidence] != old['evidence_ids'] or metrics != old['metrics']
                    or detail['evidence_bytes'] != old['evidence_bytes']
                    or detail['graph_context_bytes'] != old['path_bytes']
                    or detail['serialized_content_bytes'] != old['serialized_content_bytes']):
                    raise ValueError('zero_quota_did_not_reproduce_parent:'+case['id'])
            allowed = {e['chunk_id']: e for e in evidence}
            diagnostics = []
            for index, path in enumerate(snapshot['graph_paths']):
                prompt = path_prompt(path, allowed)
                reason = ('selected' if path in paths else 'quota_or_max_paths' if prompt else
                    'supporting_source_not_selected' if any(e['chunk_id'] not in allowed for e in path['evidence'])
                    else 'invalid_quote_provenance')
                diagnostics.append(dict(index=index, reason=reason,
                    support_chunks=[e['chunk_id'] for e in path['evidence']],
                    individual_prompt_bytes=len(json.dumps([prompt], ensure_ascii=False).encode()) if prompt else None))
            summary['results'].append(dict(case_id=case['id'], question=case['question'], category=case['category'],
                arm=arm, path_budget=quota, status='not_run', answer='尚未生成回答。',
                ranked=deepcopy(snapshot['ranked']), evidence=evidence, graph_paths=deepcopy(snapshot['graph_paths']),
                generation_paths=paths, retrieval_summary=detail, path_diagnostics=diagnostics,
                limitations=detail['limitations']+[NOTICE], citations=[], errors=[], provider_calls=[], usage=None,
                model_name=None, assembly_seconds=elapsed, metrics=metrics,
                source_metrics=source_metrics(case, recorder.bench, evidence),
                retrieval_trace_url=snapshot['trace_url'], retrieval_request_id=snapshot['request_id'],
                candidate_snapshot=case['id']+'-candidates.json', generate_requested=True,
                stage_timings=[], semantic_review='pending_independent_review'))
    write_json(folder/'execution-contract.json', contract)
    write_json(folder/'summary.json', summary)
    return summary


def verify(recorder, summary, folder, check_code=False):
    contract = read(folder/'execution-contract.json')
    assert contract['benchmark_sha256'] == summary['benchmark_sha256'] == recorder.digest
    assert len(summary['results']) == 3*len(recorder.bench['cases'])
    cases = {c['id']: c for c in recorder.bench['cases']}
    assert {(r['case_id'], r['arm']) for r in summary['results']} == {(cid, a) for cid in cases for a in ARMS}
    if check_code:
        assert all(sha(ROOT/name) == digest for name, digest in contract['code_sha256'].items())
    for row in summary['results']:
        case = cases[row['case_id']]
        snapshot_path = folder/row['candidate_snapshot']
        assert sha(snapshot_path) == contract['candidates_sha256'][row['case_id']]
        snapshot = read(snapshot_path)
        assert row['question'] == case['question'] and row['ranked'] == snapshot['ranked']
        assert row['graph_paths'] == snapshot['graph_paths']
        evidence, paths, detail = assemble(snapshot['ranked'], recorder.chunks, snapshot['graph_paths'],
            case['question'], path_budget=ARMS[row['arm']])
        assert (evidence, paths, detail) == (row['evidence'], row['generation_paths'], row['retrieval_summary'])
        assert content_bytes(evidence, detail['prompt_graph_paths']) <= 6000
        assert detail['context_bytes'] <= 6000 and len(paths) <= 4 and len(evidence) <= 8
        if row['path_budget']:
            assert detail['evidence_bytes'] <= 6000-row['path_budget']
            assert detail['graph_context_bytes'] <= row['path_budget']
        assert row['source_metrics'] == source_metrics(case, recorder.bench, evidence)
        assert row['metrics'] == support_metrics([r['chunk_id'] for r in snapshot['ranked']],
            [e['chunk_id'] for e in evidence], [recorder.bench['units'][u] for u in case['units']])
    write_json(folder/'local-verification.json', dict(verified=True, rows=len(summary['results']),
        benchmark_sha256=recorder.digest, baseline_reproduced_questions=len(cases),
        checks=['snapshot hashes', 'quota limits and total bytes', 'path source provenance',
                'same candidates across arms', 'frozen fact/source statistics'], checked_at=now()))


def generate(recorder, summary, folder, cfg):
    if summary['status'] != 'not_run':
        raise ValueError('generation_already_started; resume is export-only')
    verify(recorder, summary, folder, check_code=True)
    workflow = Workflow(ROOT, cfg, graph_enabled=True)
    try:
        if not workflow.providers.configured('DEEPSEEK'):
            raise ValueError('deepseek_not_configured')
        summary['status'] = 'running'
        write_json(folder/'summary.json', summary)
        lookup = {(r['case_id'], r['arm']): r for r in summary['results']}
        arms = list(ARMS)
        for number, case in enumerate(recorder.bench['cases']):
            # Rotation avoids always giving one arm the same position in the request sequence.
            for arm in arms[number % 3:]+arms[:number % 3]:
                row = lookup[case['id'], arm]
                request_id = workflow.audit.start(case['question'])
                state = dict(request_id=request_id, question=case['question'], errors=[], status='running',
                    evidence=row['evidence'], generation_paths=row['generation_paths'],
                    graph_paths=row['graph_paths'], retrieval_summary=row['retrieval_summary'],
                    limitations=row['limitations'], citations=[])
                row.update(request_id=request_id, start_time=now())
                # Persist intent before the paid call; interrupted calls are never auto-replayed.
                write_json(folder/'inflight.json', dict(case_id=case['id'], arm=arm, request_id=request_id, started=row['start_time']))
                start = time.perf_counter()
                state.update(workflow.audit.stage(request_id, 'generate', lambda: workflow.generate(state)))
                if state.get('raw'):
                    state.update(workflow.audit.stage(request_id, 'citations', lambda: workflow.citations(state)))
                seconds = time.perf_counter()-start
                row.update(status=state.get('status') or 'error', answer=state.get('answer'),
                    citations=state.get('citations', []), errors=state.get('errors', []),
                    usage=state.get('usage'), model_name=state.get('model_name'), generation_seconds=seconds,
                    measured_request_seconds=seconds+row['assembly_seconds'], end_time=now(),
                    stage_timings=[dict(r) for r in workflow.audit.conn.execute(
                        'SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started', (request_id,))],
                    provider_calls=[dict(r) for r in workflow.audit.conn.execute(
                        'SELECT * FROM calls WHERE request_id=? ORDER BY started', (request_id,))])
                row['trace_url'] = workflow.audit.live.url(workflow.audit.live_requests[request_id])
                # Keep a failed draft for audit; never display it as a validated answer.
                if row['status'] == 'citation_error':
                    row['unvalidated_draft'] = state.get('raw')
                workflow.audit.finish(request_id, row)
                summary['generation_calls'] += 1
                summary['model_calls'] += len(row['provider_calls'])
                write_json(folder/(case['id']+'-'+arm+'.json'), row)
                write_json(folder/'summary.json', summary)
                write_json(folder/'inflight.json', dict(status='saved', case_id=case['id'], arm=arm))
                print(json.dumps(dict(case_id=case['id'], arm=arm, status=row['status'],
                    paths=len(row['generation_paths']), seconds=round(seconds, 3)), ensure_ascii=False), flush=True)
        summary.update(status='completed', finished=now(), model=cfg.get('DEEPSEEK_MODEL'))
    except BaseException as exc:
        summary.update(status='interrupted', error_type=type(exc).__name__, finished=now())
        raise
    finally:
        write_json(folder/'summary.json', summary)
        workflow.close()


def export(recorder, summary):
    cases = {case['id']: case for case in recorder.bench['cases']}
    groups = {cid: {r['arm']: r for r in summary['results'] if r['case_id'] == cid} for cid in cases}
    notes = {}
    outputs, payloads = {}, []
    for cid, rows in groups.items():
        base = rows['Path-0']
        before = {e['chunk_id'] for e in base['evidence']}
        changes = {}
        for arm, row in rows.items():
            after = {e['chunk_id'] for e in row['evidence']}
            changes[arm] = dict(added_chunk_ids=sorted(after-before), removed_chunk_ids=sorted(before-after),
                fact_coverage_delta=row['metrics']['evidence_coverage']-base['metrics']['evidence_coverage'],
                source_coverage_delta=row['source_metrics']['required_paper_coverage']-base['source_metrics']['required_paper_coverage'],
                selected_paths=len(row['generation_paths']), path_bytes=row['retrieval_summary']['graph_context_bytes'],
                path_diagnostics=row['path_diagnostics'])
        notes[cid] = dict(case_id=cid, changes=changes,
            interpretation='固定候选，只比较 6000 字节总额内的路径配额；覆盖和程序状态不是答案正确率。')
        for arm, row in rows.items():
            out = detailed_output(row, cases[cid], recorder.bench, recorder.chunks)
            out.update(source_metrics=row['source_metrics'], path_budget=row['path_budget'],
                path_diagnostics=row['path_diagnostics'], paired_budget_comparison=changes,
                assembly_seconds=row['assembly_seconds'], generation_seconds=row.get('generation_seconds'),
                measured_request_seconds=row.get('measured_request_seconds'), trace_url=row.get('trace_url'),
                retrieval_trace_url=row['retrieval_trace_url'], candidate_snapshot=row['candidate_snapshot'],
                unvalidated_draft=row.get('unvalidated_draft'),
                latency_boundary='new assembly+generation+citations; retrieval candidates replayed; not full online latency')
            outputs[cid, arm] = out
            if not row.get('end_time'):
                continue
            metrics = dict(**row['metrics'],
                all_required_papers=row['source_metrics']['all_required_papers'],
                required_paper_coverage=row['source_metrics']['required_paper_coverage'],
                evidence_count=len(row['evidence']), path_bytes=row['retrieval_summary']['graph_context_bytes'],
                path_count=len(row['generation_paths']), assembly_seconds=row['assembly_seconds'],
                generation_seconds=row['generation_seconds'], measured_request_seconds=row['measured_request_seconds'])
            payloads.append(dict(id=stable_id(recorder.digest, summary['run_id'], cid, arm),
                name='reserved-path-quota', run_type='chain', inputs=dict(question=row['question']), outputs=out,
                reference_example_id=stable_id(recorder.digest, cid), start_time=row['start_time'], end_time=row['end_time'],
                tags=[VERSION, arm, 'fixed-retrieval-snapshot'],
                extra=dict(metadata=dict(benchmark_sha256=recorder.digest, case_id=cid, arm=arm,
                    request_id=row['request_id'], run_id=summary['run_id'], path_budget=row['path_budget'])),
                _metrics=metrics, _arm=arm))
    return outputs, payloads, notes


def sync(recorder, dataset, summary, folder):
    outputs, payloads, notes = export(recorder, summary)
    write_json(folder/'langsmith-experiments.json', dict(runs=payloads))
    client = recorder.client
    experiments = []
    for arm in ARMS:
        expected = {p['id']: p for p in payloads if p['_arm'] == arm}
        if not expected:
            continue
        name = f"papertech-{VERSION}-{summary['run_id'][:12]}-{arm}"
        project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
            description='固定真实候选，6000 字节总额内比较路径配额 0/800/1200；新生成，非图开关对照。',
            metadata=dict(benchmark_sha256=recorder.digest, arm=arm, path_budget=ARMS[arm], mode=summary['mode']))
        assert str(project.reference_dataset_id) == str(dataset.id)
        def read_runs():
            return {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
        found = read_runs()
        assert not set(found)-set(expected)
        assert all(plain(run.outputs) == plain(expected[rid]['outputs']) for rid, run in found.items())
        def upload(p):
            data = {k: v for k, v in p.items() if not k.startswith('_')}
            data['start_time'] = datetime.fromisoformat(data['start_time'])
            data['end_time'] = datetime.fromisoformat(data['end_time'])
            client.create_run(project_name=name, **data)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(upload, [p for rid, p in expected.items() if rid not in found]))
        jobs = [dict(run_id=p['id'], key=key, score=float(value), feedback_id=stable_id(p['id'], key),
            session_id=project.id, start_time=datetime.fromisoformat(p['start_time']), stop_after_attempt=1,
            comment='Frozen fact/source coverage or measured latency; not semantic answer correctness.')
            for p in expected.values() for key, value in p['_metrics'].items()]
        feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))}
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: client.create_feedback(**job), [j for j in jobs if j['feedback_id'] not in feedback]))
        for attempt in range(5):
            found = read_runs()
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))}
            if (set(found) == set(expected) and all(plain(found[rid].outputs) == plain(p['outputs']) and
                str(found[rid].reference_example_id) == p['reference_example_id'] and
                found[rid].start_time == datetime.fromisoformat(p['start_time']) and
                found[rid].end_time == datetime.fromisoformat(p['end_time']) for rid, p in expected.items()) and
                all(j['feedback_id'] in feedback and abs(feedback[j['feedback_id']].score-j['score']) <= .000050001 for j in jobs)):
                break
            if attempt == 4:
                raise ValueError('experiment_or_feedback_readback_failed')
            time.sleep(2)
        usage = recorder.sync_generation_usage({rid: {**p, 'outputs': p['outputs']} for rid, p in expected.items()}, found, name)
        client.update_project(project.id, end_time=datetime.now(timezone.utc))
        experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(found),
            feedback_verified=len(jobs), generation_usage=usage))
    return dict(status='experiments_verified', dataset_url=dataset.url, examples_verified=len(recorder.bench['cases']),
        experiments=experiments, comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments))


def aggregate(rows):
    mean = lambda fn: sum(fn(r) for r in rows)/len(rows) if rows else None
    completed = [r for r in rows if r.get('end_time')]
    return dict(questions=len(rows), generated=len(completed),
        evidence_coverage=mean(lambda r: r['metrics']['evidence_coverage']),
        all_units=sum(r['metrics']['all_units'] for r in rows),
        all_required_papers=sum(r['source_metrics']['all_required_papers'] for r in rows),
        required_paper_coverage=mean(lambda r: r['source_metrics']['required_paper_coverage']),
        evidence_count=mean(lambda r: len(r['evidence'])),
        path_bytes=mean(lambda r: r['retrieval_summary']['graph_context_bytes']),
        path_count=mean(lambda r: len(r['generation_paths'])),
        queries_with_paths=sum(bool(r['generation_paths']) for r in rows),
        assembly_p95_ms=1000*percentile([r['assembly_seconds'] for r in rows]) if rows else None,
        generation_p95_seconds=percentile([r['generation_seconds'] for r in completed]),
        measured_request_p95_seconds=percentile([r['measured_request_seconds'] for r in completed]),
        input_tokens=sum((r.get('usage') or {}).get('prompt_tokens', 0) for r in completed),
        output_tokens=sum((r.get('usage') or {}).get('completion_tokens', 0) for r in completed),
        unknown_usage=sum(not bool(r.get('usage')) for r in completed),
        statuses=dict(Counter(r['status'] for r in rows)))


def report(recorder, summary, folder):
    outputs, payloads, notes = export(recorder, summary)
    aggs = {arm: aggregate([r for r in summary['results'] if r['arm'] == arm]) for arm in ARMS}
    categories = {category: {arm: aggregate([r for r in summary['results'] if r['arm'] == arm and r['category'] == category])
        for arm in ARMS} for category in sorted({c['category'] for c in recorder.bench['cases']})}
    changes = {arm: dict(Counter('gain' if n['changes'][arm]['fact_coverage_delta'] > 0 else
        'regression' if n['changes'][arm]['fact_coverage_delta'] < 0 else 'tie' for n in notes.values())) for arm in ARMS}
    data = dict(run_id=summary['run_id'], benchmark=VERSION, status=summary['status'], arms=ARMS,
        benchmark_sha256=recorder.digest, aggregates=aggs, categories=categories, fact_coverage_changes=changes,
        dataset_sync=summary['dataset_sync'], diagnostics=notes,
        references={e['metadata']['case_id']: e['outputs'] for e in recorder.payload['examples']},
        results={cid: {arm: outputs[cid, arm] for arm in ARMS} for cid in notes})
    write_json(folder/'comparison.json', data)
    write_json(folder/'per-question-diagnosis.json', notes)
    lines = ['# 路径配额 0 / 800 / 1200 对照', '', f"运行 `{summary['run_id']}`；状态 `{summary['status']}`。",
        f'题集 `{VERSION}`；SHA-256 `{recorder.digest}`。', '',
        '总额仍为 6000 UTF-8 字节。0 沿用原文优先、路径用剩余空间；800/1200 分别给原文 5200/4800，保留路径硬配额，未用配额不返还。',
        '复用上一轮真实候选、分数和图路径，只做证据组装与新生成；不是新检索或 Graph 开关对照。', '',
        '| 指标 | Path-0 | Path-800 | Path-1200 |', '|---|---:|---:|---:|']
    for label, key in [('冻结事实覆盖', 'evidence_coverage'), ('全事实覆盖题数', 'all_units'),
        ('必要来源全部齐全题数', 'all_required_papers'), ('平均来源覆盖', 'required_paper_coverage'),
        ('平均原文块数', 'evidence_count'), ('平均路径字节', 'path_bytes'), ('有路径题数', 'queries_with_paths'),
        ('组装 P95 毫秒', 'assembly_p95_ms'), ('生成含引用校验 P95 秒', 'generation_p95_seconds'),
        ('本轮请求 P95 秒（不含检索）', 'measured_request_p95_seconds'),
        ('生成调用', 'generated'), ('输入 Token', 'input_tokens'), ('输出 Token', 'output_tokens'), ('未知 Usage', 'unknown_usage')]:
        cells = []
        for arm in ARMS:
            v = aggs[arm][key]
            cells.append('未运行' if v is None else f'{v*100:.2f}%' if key in ('evidence_coverage', 'required_paper_coverage') else f'{v:.3f}')
        lines.append('| '+label+' | '+' | '.join(cells)+' |')
    lines += ['', '各组状态：`'+json.dumps({arm: a['statuses'] for arm, a in aggs.items()}, ensure_ascii=False)+'`。', '',
        '所有题均为冻结分类 cross（跨文本）；分类指标见 comparison.json。',
        'P95 是 16 个单次样本的线性分位数；生成受服务波动和随机性影响。未新测检索/完整在线请求时延。',
        '事实覆盖按有限支持池 ID 统计，来源齐全只表示论文出现；程序 ok/partial 和引用格式均不是答案语义评分。', '',
        '| 题号 | 事实覆盖 0/800/1200 | 来源齐全 0/800/1200 | 原文块数 | 路径数 |', '|---|---|---|---|---|']
    lookup = {(r['case_id'], r['arm']): r for r in summary['results']}
    for cid in notes:
        rows = [lookup[cid, arm] for arm in ARMS]
        lines.append('| '+cid+' | '+' / '.join(f"{r['metrics']['evidence_coverage']*100:.1f}%" for r in rows)+' | '+
            ' / '.join('是' if r['source_metrics']['all_required_papers'] else '否' for r in rows)+' | '+
            ' / '.join(str(len(r['evidence'])) for r in rows)+' | '+' / '.join(str(len(r['generation_paths'])) for r in rows)+' |')
    if summary['dataset_sync'].get('comparison_url'):
        lines += ['', '[LangSmith 三组对照]('+summary['dataset_sync']['comparison_url']+')']
    lines += ['', '[汇总柱状图、分类指标与逐题详情](dashboard.html) · [逐题归因](per-question-diagnosis.json)', '',
        '每题展示原参考答案与来源、完整回答与引用、候选和分数、图路径、逐事实缺口、预算变化、阶段耗时、Token 和 Trace。',
        '本轮不改图 Schema、不重抽关系、不改题集、不调 reranker 或多样性策略。']
    (folder/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    html = (ROOT/'scripts/path-budget-dashboard.html').read_text(encoding='utf-8')
    (folder/'dashboard.html').write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')), encoding='utf-8')


def execute(prepare_only=False, resume=None, generate_from=None):
    cfg = settings(ROOT)
    recorder = DetailedEvaluationDataset(ROOT, VERSION)
    folder = None
    summary = None
    try:
        if resume or generate_from:
            path = (resume or generate_from).resolve()
            folder, summary = path.parent, read(path)
            verify(recorder, summary, folder)
        else:
            run_id = uuid.uuid4().hex
            folder = RUN_ROOT/run_id
            folder.mkdir(parents=True)
            summary = prepare(recorder, folder, run_id)
        report(recorder, summary, folder)
        if prepare_only:
            verify(recorder, summary, folder, check_code=True)
            print(json.dumps(dict(directory=str(folder), status=summary['status'], aggregates=read(folder/'comparison.json')['aggregates']), ensure_ascii=False), flush=True)
            return
        dataset = recorder.sync_dataset() if cfg.get('LANGSMITH_API_KEY') else None
        if dataset is not None:
            assert len(list(recorder.client.list_examples(dataset_id=dataset.id))) == len(recorder.bench['cases'])
        if not resume:
            generate(recorder, summary, folder, cfg)
        verify(recorder, summary, folder)
    finally:
        if summary is not None:
            if cfg.get('LANGSMITH_API_KEY') and summary.get('generation_calls'):
                try:
                    dataset = recorder.sync_dataset()
                    summary['dataset_sync'] = sync(recorder, dataset, summary, folder)
                except Exception as exc:
                    summary['dataset_sync'] = dict(status='pending_sync', error_type=type(exc).__name__)
                    print(json.dumps(dict(sync='pending_sync', error_type=type(exc).__name__)), flush=True)
            write_json(folder/'summary.json', summary)
            report(recorder, summary, folder)
            write_json(folder/'langsmith-status.json', summary['dataset_sync'])
            write_json(RUN_ROOT/'latest.json', dict(directory=str(folder), run_id=summary['run_id'], status=summary['status']))
            print(json.dumps(dict(directory=str(folder), status=summary['status'], generation_calls=summary['generation_calls'],
                dataset_sync=summary['dataset_sync']), ensure_ascii=False), flush=True)
        recorder.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prepare-only', action='store_true')
    group.add_argument('--resume', type=Path, help='Only verify/rebuild/upload saved results; never call models')
    group.add_argument('--generate-from', type=Path, help='Generate once from a prepared not_run summary')
    args = parser.parse_args()
    with exclusive_lock(ROOT/'.cache/path-budget-eval.lock'):
        execute(args.prepare_only, args.resume, args.generate_from)
