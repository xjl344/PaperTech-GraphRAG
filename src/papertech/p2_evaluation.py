"""Paired end-to-end Phase-2 evaluation: P0-SingleQuery vs P2-Planner-OwnerRerank on 40 v4 questions."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
import math
from pathlib import Path
import sqlite3
import time
import uuid

from .audit import now
from .corpus import load_corpus
from .evaluation import criterion_source_coverage, linear_quantile, support_metrics
from .evaluation_datasets import METRICS, load_benchmark, output_payload, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, PROFILE, detailed_output
from .ingest import atomic_json
from .local_models import run_worker
from .providers import Providers
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings
from .workflow import Workflow

VERSION = 'benchmark-v4-planner-v1'
PARENT_BENCH = 'benchmark-v4'
ARMS = ('P0-SingleQuery', 'P2-Planner-OwnerRerank')
ARM_CONFIGS = {
    'P0-SingleQuery': dict(
        graph_enabled=False, rerank_contextual=True, evidence_budget=18000, evidence_max=12,
        source_policy='named_first', score_policy='relative', reservation_policy='round_robin',
        citation_protocol='source-choice-v2', query_planner=False, premise_check=False,
    ),
    'P2-Planner-OwnerRerank': dict(
        graph_enabled=False, rerank_contextual=True, evidence_budget=18000, evidence_max=12,
        source_policy='named_first', score_policy='relative', reservation_policy='round_robin',
        citation_protocol='source-choice-v2', query_planner=True, premise_check=True,
    ),
}
CODE_FILES = (
    'src/papertech/query_planner.py', 'src/papertech/rerank_runtime.py',
    'src/papertech/rerank_service.py', 'src/papertech/retrieval.py',
    'src/papertech/evidence_context.py', 'src/papertech/citations.py',
    'src/papertech/providers.py', 'src/papertech/workflow.py',
    'src/papertech/graph_store.py', 'src/papertech/evaluation.py',
    'src/papertech/evaluation_datasets.py', 'src/papertech/evaluation_details.py',
    'src/papertech/p2_evaluation.py', 'scripts/eval-stage4.py',
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FlexibleCachedProviders(Providers):
    """Reuse frozen base query vectors while allowing live batch embedding for new subqueries."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vectors = {}
        self.cache_hits = 0
        self.live_subquery_embeds = 0

    def embedding(self, request_id, texts):
        missing = [t for t in dict.fromkeys(texts) if t not in self.vectors]
        if missing:
            fetched = super().embedding(request_id, missing)
            for text, vec in zip(missing, fetched):
                self.vectors[text] = list(vec)
            self.live_subquery_embeds += len(missing)
        self.cache_hits += len(texts) - len(missing)
        return [list(self.vectors[t]) for t in texts]


def freeze(root):
    directory = root / 'artifacts/eval/stage-4' / VERSION
    bench_path = directory / 'benchmark.json'
    code_hashes = {name: sha(root / name) for name in CODE_FILES}
    if bench_path.exists():
        bench, digest, _ = load_benchmark(root, VERSION)
        if bench.get('code_sha256') != code_hashes:
            raise RuntimeError('frozen_p2_code_changed')
        return bench, digest, directory
    parent, parent_sha, _ = load_benchmark(root, PARENT_BENCH)
    cfg = settings(root)
    selected_keys = ('DEEPSEEK_MODEL', 'CLOUD_BGE_MODEL', 'CLOUD_BGE_PROVIDER',
        'LOCAL_RERANKER_PATH', 'LOCAL_RERANKER_PYTHON', 'LOCAL_RERANKER_DEVICE',
        'LOCAL_RERANKER_DTYPE', 'LOCAL_RERANKER_PERSISTENT')
    models = {key: cfg.get(key) for key in selected_keys}
    models['LOCAL_RERANKER_BATCH_SIZE'] = int(cfg.get('LOCAL_RERANKER_BATCH_SIZE', 4))
    bench = deepcopy(parent)
    bench.update(
        version=VERSION,
        created_at=now(),
        parent_benchmark=PARENT_BENCH,
        parent_benchmark_sha256=parent_sha,
        arms=list(ARMS),
        arm_configs=deepcopy(ARM_CONFIGS),
        models=models,
        code_sha256=code_hashes,
        dataset_description='阶段4 P2 40题配对实测：P0-SingleQuery vs P2-Planner-OwnerRerank（云端 Flash 规划拆分 + 英文关键词全文检索 + 归属重排 + 子查询保底 + premise_check）；纯 Hybrid 不动图谱。',
        prior_exposure='沿用 benchmark-v4 40 题开发集（8 事实控制 + 24 跨论文关系 + 8 反例），属于已曝光开发集，不作为独立泛化验收。',
        comparison=dict(mode='p2_planner_hybrid_ablation', arms=list(ARMS), graph_enabled=False, generation=True),
        controls=dict(
            arms=list(ARMS),
            arm_configs=deepcopy(ARM_CONFIGS),
            backend='neo4j',
            graph_enabled=False,
            fulltext_top=20, dense_top=20, multi_query_cap=64,
            reranker_batch_size=models['LOCAL_RERANKER_BATCH_SIZE'],
            generation_max_tokens=2048, planner_max_tokens=600, thinking='disabled',
            execution_order='alternate arm order by case index',
            query_vector='shared frozen Cloudflare batch for Q00; single live Cloudflare batch for generated subqueries',
            gold_exclusion='question text only; planner and generator never see gold facts, source pools, or reference answers',
        ),
    )
    directory.mkdir(parents=True, exist_ok=True)
    write_json(bench_path, bench)
    digest = sha(bench_path)
    (directory / 'benchmark.sha256').write_text(digest + '\n', encoding='utf-8')
    return bench, digest, directory


def paired_p2_comparisons(summary):
    pairs = {}
    for row in summary['results']:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    comparisons = {}
    for case_id, rows in pairs.items():
        if set(rows) != set(ARMS):
            comparisons[case_id] = dict(status='incomplete_pair', available_arms=sorted(rows))
            continue
        base, opt = rows[ARMS[0]], rows[ARMS[1]]
        b_ids = {e['chunk_id'] for e in base.get('evidence') or []}
        o_ids = {e['chunk_id'] for e in opt.get('evidence') or []}
        diffs = {}
        for key in METRICS:
            a, b = base['metrics'].get(key), opt['metrics'].get(key)
            diffs[key] = (b - a) if a is not None and b is not None else None
        comparisons[case_id] = dict(
            status='paired',
            p2_minus_p0=diffs,
            p0_status=base['status'],
            p2_status=opt['status'],
            planner_decision=((opt.get('retrieval_summary') or {}).get('query_plan') or {}).get('decision'),
            shared_evidence=sorted(b_ids & o_ids),
            p2_added_evidence=sorted(o_ids - b_ids),
            p2_removed_evidence=sorted(b_ids - o_ids),
            interpretation='客观记录 P2 相对 P0 基线的支持池覆盖、路由决策、引用状态与证据集合差异，不自动等同人工语义评分。',
        )
    return comparisons


def _p2_run_payloads(bench, digest, summary):
    if summary['benchmark_sha256'] != digest or summary['benchmark'] != bench['version']:
        raise ValueError('run_benchmark_mismatch')
    cases = {c['id']: c for c in bench['cases']}
    seen, payloads = set(), []
    started = datetime.fromisoformat(summary['started'])
    for index, row in enumerate(summary['results']):
        case_id, arm = row['case_id'], row['arm']
        case = cases[case_id]
        if arm not in ARMS or (case_id, arm) in seen:
            raise ValueError('duplicate_or_invalid_experiment_row')
        if row['question'] != case['question'] or row['category'] != case['category']:
            raise ValueError('run_case_mismatch')
        seen.add((case_id, arm))
        run_id = stable_id(digest, summary['run_id'], case_id, arm)
        timestamp = started + timedelta(microseconds=index)
        metrics = {k: row['metrics'].get(k) for k in METRICS if case['category'] != 'negative'}
        out = output_payload(row, 'full')
        out['answer_local_file'] = row['case_id'] + ('-p2.json' if arm == ARMS[1] else '-p0.json')
        payloads.append(dict(
            id=run_id, name='stage4-p2-paired-evaluation', run_type='chain',
            inputs=dict(question=case['question']), outputs=out,
            reference_example_id=stable_id(digest, case_id),
            start_time=timestamp, end_time=timestamp,
            extra=dict(metadata=dict(benchmark=bench['version'], benchmark_sha256=digest,
                original_run_id=summary['run_id'], request_id=row['request_id'], case_id=case_id,
                arm=arm, capture_mode='evaluation_result_import', detail_profile=PROFILE)),
            tags=[bench['version'], arm, case['category']],
            _arm=arm, _metrics=metrics,
        ))
    if summary['status'] == 'completed' and len(seen) != len(cases) * len(ARMS):
        raise ValueError('incomplete_paired_results')
    return payloads


class P2Dataset(DetailedEvaluationDataset):
    def __init__(self, root, version=VERSION, client=None, allow_enrichment=False):
        super().__init__(root, version, client, allow_enrichment=allow_enrichment)
        self.payload['description'] = self.bench['dataset_description']
        self.payload['metadata'].pop('no_model_comparison_run', None)
        for example in self.payload['examples']:
            example['outputs']['result_display']['location'] = '本题关联的 P0-SingleQuery / P2-Planner-OwnerRerank Experiment runs'
        write_json(self.directory / 'langsmith-dataset.json', self.payload)
        for example in self.payload['examples']:
            write_json(self.directory / 'cases' / (example['metadata']['case_id'] + '.json'), example)
        write_json(self.directory / 'detail-contract.json', dict(detail_profile=PROFILE,
            benchmark_sha256=self.digest,
            examples_sha256=hashlib.sha256(json.dumps(self.payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()))

    def sync_run(self, summary_path, answer_mode='full'):
        if answer_mode != 'full':
            raise ValueError('detailed_benchmark_requires_full_results')
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        payloads = _p2_run_payloads(self.bench, self.digest, summary)
        cases = {case['id']: case for case in self.bench['cases']}
        rows = {(row['case_id'], row['arm']): row for row in summary['results']}
        comparisons = paired_p2_comparisons(summary)
        ledger = self.root / 'data/rag.sqlite3'
        for payload in payloads:
            meta = payload['extra']['metadata']
            case_id, arm = meta['case_id'], meta['arm']
            row = rows[case_id, arm]
            out = detailed_output(row, cases[case_id], self.bench, self.chunks)
            out['answer_local_file'] = case_id + ('-p2.json' if arm == ARMS[1] else '-p0.json')
            out['paired_comparison'] = comparisons[case_id]
            if row.get('premise_check') is not None:
                out['premise_check'] = deepcopy(row['premise_check'])
            payload['outputs'] = out
            if ledger.exists():
                with sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True) as conn:
                    timing = conn.execute('SELECT started,finished FROM requests WHERE id=?', (row['request_id'],)).fetchone()
                if timing and timing[0] and timing[1]:
                    payload['start_time'], payload['end_time'] = map(datetime.fromisoformat, timing)
                    payload['outputs']['request_wall_seconds'] = (payload['end_time'] - payload['start_time']).total_seconds()
                    meta['timing_note'] = 'Actual request ledger timestamps; includes live tracing overhead, excludes shared Q00 embedding batch and warmup.'
            usage = row.get('usage')
            if usage and usage.get('prompt_tokens') is not None and usage.get('completion_tokens') is not None:
                payload.update(prompt_tokens=usage['prompt_tokens'], completion_tokens=usage['completion_tokens'],
                    total_tokens=usage['prompt_tokens'] + usage['completion_tokens'])
            payload['_metrics'].update(
                retrieval_compute_seconds=row.get('retrieval_compute_seconds'),
                request_wall_seconds=payload['outputs'].get('request_wall_seconds'),
                evidence_count=len(row.get('evidence') or []),
                citation_ok=1.0 if row.get('status') != 'citation_error' else 0.0,
            )
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(
            benchmark=self.bench['version'], benchmark_sha256=self.digest, detail_profile=PROFILE,
            runs=json.loads(json.dumps(payloads, default=str))))
        write_json(summary_path.parent / 'per-question-comparison.json', comparisons)
        dataset = self.sync_dataset()
        client, experiments = self.client, []
        for arm in ARMS:
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='P2 对照逐题完整结果：路由拆分、回答、候选、证据、引用、前提核验、耗时、Token 与两组差异。',
                metadata=dict(detail_profile=PROFILE, benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], arm=arm, original_status=summary['status']))
            if str(project.reference_dataset_id) != str(dataset.id):
                raise ValueError('experiment_dataset_mismatch')
            expected = {p['id']: p for p in payloads if p['_arm'] == arm}
            existing = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(existing) - set(expected):
                raise ValueError('unexpected_experiment_runs')
            for rid, run in existing.items():
                if run.outputs != expected[rid]['outputs'] or str(run.reference_example_id) != expected[rid]['reference_example_id']:
                    raise ValueError('remote_experiment_modified')
            def upload(payload):
                client.create_run(project_name=name, **{k: v for k, v in payload.items() if not k.startswith('_')})
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upload, [p for rid, p in expected.items() if rid not in existing]))
            present = {str(f.id) for f in client.list_feedback(run_ids=list(expected))} if expected else set()
            jobs = []
            for payload in expected.values():
                for key, value in payload['_metrics'].items():
                    fid = stable_id(payload['id'], key)
                    if value is not None and fid not in present:
                        jobs.append(dict(run_id=payload['id'], key=key, score=float(value), feedback_id=fid,
                            session_id=project.id, start_time=payload['start_time'], stop_after_attempt=1,
                            comment='P2 对照自动指标；覆盖与引用状态不代表人工语义正确率。'))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), jobs))
            verified = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(verified) != set(expected) or any(run.outputs != expected[rid]['outputs'] or
                    str(run.reference_example_id) != expected[rid]['reference_example_id'] for rid, run in verified.items()):
                raise ValueError('detailed_run_readback_mismatch')
            native_usage = self.sync_generation_usage(expected, verified, name)
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))} if expected else {}
            checked = 0
            for payload in expected.values():
                for key, value in payload['_metrics'].items():
                    if value is None:
                        continue
                    fid = stable_id(payload['id'], key)
                    if fid not in feedback or not math.isclose(feedback[fid].score, float(value), rel_tol=0, abs_tol=0.000050001):
                        raise ValueError('feedback_readback_mismatch')
                    checked += 1
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(verified),
                feedback_verified=checked, generation_usage_runs_verified=native_usage['verified'], detail_profile=PROFILE))
        self.status.update(status='experiments_verified', original_run_id=summary['run_id'],
            answer_mode='full', result_status=summary['status'], experiments=experiments,
            comparison_url=f"{dataset.url}/compare?selectedSessions=" + ','.join(e['project_id'] for e in experiments))
        write_json(summary_path.parent / 'langsmith-status.json', self.status)
        write_json(self.status_path, self.status)
        return self.status


def _verify_remote_batched(live, root_ids):
    """Batch read-only verification via list_runs(run_ids=...) to avoid per-span rate limits."""
    live.flush()
    ids = set(root_ids)
    rows = [dict(r) for r in live.conn.execute('SELECT * FROM spans')]
    while True:
        grown = ids | {r['id'] for r in rows if r['parent_id'] in ids}
        if grown == ids:
            break
        ids = grown
    expected_rows = [r for r in rows if r['id'] in ids]
    span_ids = [r['id'] for r in expected_rows]
    found = {}
    for attempt in range(3):
        missing = [sid for sid in span_ids if sid not in found or found[sid].end_time is None]
        if not missing:
            break
        for i in range(0, len(missing), 50):
            batch = missing[i:i + 50]
            for run in live.client.list_runs(run_ids=batch, limit=len(batch),
                    select=['id', 'name', 'end_time', 'prompt_tokens', 'completion_tokens']):
                found[str(run.id)] = run
        if any(sid not in found or found[sid].end_time is None for sid in span_ids) and attempt < 2:
            time.sleep(2)
    checks = []
    for row in expected_rows:
        remote = found.get(row['id'])
        if remote is None:
            checks.append(dict(id=row['id'], name=row['name'], finished=False, error='missing'))
            continue
        event = live.conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1", (row['id'],)).fetchone()
        payload = json.loads(event[0]) if event else {}
        usage_ok = None
        if 'prompt_tokens' in payload:
            usage_ok = remote.prompt_tokens == payload['prompt_tokens'] and remote.completion_tokens == payload['completion_tokens']
        checks.append(dict(id=row['id'], name=row['name'], finished=remote.end_time is not None, native_usage_matches=usage_ok))
    pending = sum(1 for row in live.conn.execute("SELECT span_id FROM events WHERE status='pending'") if row[0] in ids)
    return dict(verified=bool(checks) and not pending and all(c['finished'] and c.get('native_usage_matches') is not False for c in checks),
                pending_events=pending, span_count=len(checks), finished_count=sum(c['finished'] for c in checks))


def _mean(values):
    nums = [v for v in values if v is not None]
    return sum(nums) / len(nums) if nums else None


def _summarize_arm(rows, bench):
    ans = [r for r in rows if r['category'] != 'negative']
    cross = [r for r in rows if r['category'] in ('cross', 'cross_paper')]
    fact = [r for r in rows if r['category'] in ('fact', 'factual_control')]
    neg = [r for r in rows if r['category'] == 'negative']
    def block(items):
        return dict(
            count=len(items),
            recall5=_mean([r['metrics']['recall5'] for r in items]),
            recall8=_mean([r['metrics']['recall8'] for r in items]),
            mrr40=_mean([r['metrics']['mrr40'] for r in items]),
            evidence_coverage=_mean([r['metrics']['evidence_coverage'] for r in items]),
            all_units=sum(1 for r in items if r['metrics'].get('all_units')),
        )
    statuses = Counter(r['status'] for r in rows)
    neg_statuses = Counter(r['status'] for r in neg)
    # Sum ALL deepseek calls recorded on each request (generation + planner if any).
    all_prompt, all_comp = 0, 0
    gen_prompt, gen_comp = 0, 0
    plan_prompt, plan_comp = 0, 0
    plan_secs, plan_decisions = [], Counter()
    fact_splits, cross_splits = 0, 0
    for r in rows:
        u = r.get('usage') or {}
        gen_prompt += u.get('prompt_tokens') or 0
        gen_comp += u.get('completion_tokens') or 0
        plan = (r.get('retrieval_summary') or {}).get('query_plan') or {}
        if plan:
            dec = plan.get('decision') or 'none'
            plan_decisions[dec] += 1
            if plan.get('elapsed_seconds') is not None:
                plan_secs.append(plan['elapsed_seconds'])
            pu = plan.get('usage') or {}
            plan_prompt += pu.get('prompt_tokens') or 0
            plan_comp += pu.get('completion_tokens') or 0
            if dec == 'split':
                if r['category'] in ('fact', 'factual_control'):
                    fact_splits += 1
                elif r['category'] in ('cross', 'cross_paper'):
                    cross_splits += 1
        for call in r.get('provider_calls') or []:
            cu = call.get('usage')
            if isinstance(cu, str):
                cu = json.loads(cu)
            if isinstance(cu, dict):
                all_prompt += cu.get('prompt_tokens') or 0
                all_comp += cu.get('completion_tokens') or 0
    # Residual unit attribution across 32 answerable cases
    cases_by_id = {c['id']: c for c in bench['cases']}
    attr = Counter()
    for r in ans:
        case = cases_by_id[r['case_id']]
        pool_ranked = {x['chunk_id'] for x in r.get('ranked') or []}
        ev_ids = {e['chunk_id'] for e in r.get('evidence') or []}
        for uid in case['units']:
            gold = set(bench['units'][uid]['known_support_chunks'])
            if gold & ev_ids:
                attr['covered'] += 1
            elif gold & pool_ranked:
                attr['in_pool_not_selected'] += 1
            else:
                attr['upstream_pool_miss'] += 1
    compute_s = [r['retrieval_compute_seconds'] for r in rows if r.get('retrieval_compute_seconds') is not None]
    wall_s = [r['request_wall_seconds'] for r in rows if r.get('request_wall_seconds') is not None]
    rerank_s = [t['seconds'] for r in rows for t in r.get('compute_timings', []) if t['name'] == 'rerank']
    return dict(
        answerable=block(ans),
        factual_control=block(fact),
        cross_paper=block(cross),
        negative=dict(count=len(neg), statuses=dict(neg_statuses), refused=neg_statuses.get('refused', 0)),
        statuses=dict(statuses),
        citation_errors=statuses.get('citation_error', 0),
        avg_evidence_count=_mean([len(r.get('evidence') or []) for r in rows]),
        avg_context_bytes=_mean([(r.get('retrieval_summary') or {}).get('context_bytes') for r in rows]),
        gen_prompt_tokens=gen_prompt, gen_completion_tokens=gen_comp,
        plan_prompt_tokens=plan_prompt, plan_completion_tokens=plan_comp,
        all_prompt_tokens=all_prompt, all_completion_tokens=all_comp,
        total_tokens=all_prompt + all_comp,
        planner_decisions=dict(plan_decisions),
        fact_split_count=fact_splits, cross_split_count=cross_splits,
        planner_p50=linear_quantile(plan_secs, 0.5) if plan_secs else None,
        planner_p95=linear_quantile(plan_secs, 0.95) if plan_secs else None,
        unit_attribution=dict(attr),
        retrieval_compute_p50=linear_quantile(compute_s, 0.5) if compute_s else None,
        retrieval_compute_p95=linear_quantile(compute_s, 0.95) if compute_s else None,
        rerank_p50=linear_quantile(rerank_s, 0.5) if rerank_s else None,
        rerank_p95=linear_quantile(rerank_s, 0.95) if rerank_s else None,
        wall_p50=linear_quantile(wall_s, 0.5) if wall_s else None,
        wall_p95=linear_quantile(wall_s, 0.95) if wall_s else None,
    )


def render_report(root, summary_path):
    summary_path = Path(summary_path)
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    bench, digest, _ = load_benchmark(root, summary['benchmark'])
    by_arm = {arm: [r for r in summary['results'] if r['arm'] == arm] for arm in ARMS}
    stats = {arm: _summarize_arm(by_arm[arm], bench) for arm in ARMS}
    comparisons = paired_p2_comparisons(summary)
    b, o = stats[ARMS[0]], stats[ARMS[1]]
    cases_by_id = {c['id']: c for c in bench['cases']}
    rows_by_key = {(r['case_id'], r['arm']): r for r in summary['results']}
    deltas = dict(recall5=Counter(), recall8=Counter(), evidence_coverage=Counter())
    for cid, comp in comparisons.items():
        if cases_by_id[cid]['category'] == 'negative' or comp.get('status') != 'paired':
            continue
        for key in deltas:
            d = comp['p2_minus_p0'].get(key)
            if d is None:
                continue
            tag = 'improved' if d > 1e-9 else ('regressed' if d < -1e-9 else 'tied')
            deltas[key][tag] += 1
    out_dir = summary_path.parent / 'report'
    out_dir.mkdir(parents=True, exist_ok=True)
    comparison_json = dict(benchmark=bench['version'], benchmark_sha256=digest, run_id=summary['run_id'],
        status=summary['status'], stats=stats, deltas={k: dict(v) for k, v in deltas.items()},
        dataset_sync=summary.get('dataset_sync'), remote_verification=summary.get('remote_verification'),
        per_case=comparisons)
    write_json(out_dir / 'comparison.json', comparison_json)

    def pct(v): return f'{v*100:.2f}%' if v is not None else 'N/A'
    def pp(a, x): return f'{(x-a)*100:+.2f} pp' if a is not None and x is not None else 'N/A'
    def f4(v): return f'{v:.4f}' if v is not None else 'N/A'
    def sec(v): return f'{v:.3f}s' if v is not None else 'N/A'

    ls_url = (summary.get('dataset_sync') or {}).get('comparison_url') or ''
    md = [
        f"# {bench['version']} 实测对比报告（P0-SingleQuery vs P2-Planner-OwnerRerank）",
        '',
        f"- 运行 ID：`{summary['run_id']}`；题集 SHA-256：`{digest}`；状态：`{summary['status']}`。",
        f"- 对照设计：40 题 × 2 组（纯 Hybrid，均关闭图扩展），在已验证胜出的 P0 配置（1.1a+1.2+1.3）上严格隔离第二步增量（云端 Flash Query Planner + 英文关键词全文检索 + 并发多查询召回 + 归属重排 + 子查询保底 + 结构化 `premise_check`）。",
        '',
        '## 1. 汇总指标（32 道可回答题 + 8 道反例）',
        '',
        '| 指标 | P0-SingleQuery | P2-Planner-OwnerRerank | 差值 (P2 − P0) |',
        '|---|---:|---:|---:|',
        f"| SupportRecall@5 (32题) | {pct(b['answerable']['recall5'])} | {pct(o['answerable']['recall5'])} | {pp(b['answerable']['recall5'], o['answerable']['recall5'])} |",
        f"| SupportRecall@8 (32题) | {pct(b['answerable']['recall8'])} | {pct(o['answerable']['recall8'])} | {pp(b['answerable']['recall8'], o['answerable']['recall8'])} |",
        f"| MRR@40 (32题) | {f4(b['answerable']['mrr40'])} | {f4(o['answerable']['mrr40'])} | {(o['answerable']['mrr40']-b['answerable']['mrr40']):+.4f} |",
        f"| **最终来源支持单元覆盖 (32题)** | {pct(b['answerable']['evidence_coverage'])} | **{pct(o['answerable']['evidence_coverage'])}** | **{pp(b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage'])}** |",
        f"| **必要来源全部覆盖题数 (32题)** | {b['answerable']['all_units']}/32 | **{o['answerable']['all_units']}/32** | **{o['answerable']['all_units']-b['answerable']['all_units']:+d} 题** |",
        f"| 事实单元归因（64 单元） | `{b['unit_attribution']}` | `{o['unit_attribution']}` | upstream_miss {o['unit_attribution'].get('upstream_pool_miss',0)-b['unit_attribution'].get('upstream_pool_miss',0):+d} |",
        f"| 引用协议失败 (`citation_error`, 40题) | {b['citation_errors']}/40 | {o['citation_errors']}/40 | {o['citation_errors']-b['citation_errors']:+d} 条 |",
        f"| 反例拒答数 (`refused`, 8题) | {b['negative']['refused']}/8 | {o['negative']['refused']}/8 | {o['negative']['refused']-b['negative']['refused']:+d} 题 |",
        '',
        f"逐题变化（32 题）：Recall@5 {deltas['recall5'].get('improved',0)} 增 / {deltas['recall5'].get('tied',0)} 平 / {deltas['recall5'].get('regressed',0)} 退；最终来源覆盖 {deltas['evidence_coverage'].get('improved',0)} 增 / {deltas['evidence_coverage'].get('tied',0)} 平 / {deltas['evidence_coverage'].get('regressed',0)} 退。",
        '',
        '## 2. 分类指标与路由行为',
        '',
        '| 类别 | 指标 | P0-SingleQuery | P2-Planner-OwnerRerank | 差值 |',
        '|---|---|---:|---:|---:|',
        f"| 事实控制 (8题) | 最终来源覆盖 / 全覆盖 | {pct(b['factual_control']['evidence_coverage'])} ({b['factual_control']['all_units']}/8) | {pct(o['factual_control']['evidence_coverage'])} ({o['factual_control']['all_units']}/8) | {pp(b['factual_control']['evidence_coverage'], o['factual_control']['evidence_coverage'])} |",
        f"| 事实控制 (8题) | Planner 拆分题数（误拆监测） | 0/8 | {o['fact_split_count']}/8 | - |",
        f"| 跨论文关系 (24题) | Recall@5 | {pct(b['cross_paper']['recall5'])} | {pct(o['cross_paper']['recall5'])} | {pp(b['cross_paper']['recall5'], o['cross_paper']['recall5'])} |",
        f"| 跨论文关系 (24题) | **最终来源覆盖 / 全覆盖** | {pct(b['cross_paper']['evidence_coverage'])} ({b['cross_paper']['all_units']}/24) | **{pct(o['cross_paper']['evidence_coverage'])} ({o['cross_paper']['all_units']}/24)** | **{pp(b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage'])}** |",
        f"| 跨论文关系 (24题) | Planner 拆分题数 | 0/24 | {o['cross_split_count']}/24 | - |",
        f"| 反例 (8题) | 程序状态分布 | `{b['negative']['statuses']}` | `{o['negative']['statuses']}` | refused {o['negative']['refused']-b['negative']['refused']:+d} |",
        '',
        '## 3. 时延、Planner 开销、Token 与状态',
        '',
        '| 项目 | P0-SingleQuery | P2-Planner-OwnerRerank |',
        '|---|---:|---:|',
        f"| Planner 路由决策分布 (40题) | - | `{o['planner_decisions']}` |",
        f"| Planner 耗时 P50 / P95（对比本地14B 32.9s） | - | {sec(o['planner_p50'])} / {sec(o['planner_p95'])} |",
        f"| 检索计算 P50 / P95（P2 含规划与多路重排） | {sec(b['retrieval_compute_p50'])} / {sec(b['retrieval_compute_p95'])} | {sec(o['retrieval_compute_p50'])} / {sec(o['retrieval_compute_p95'])} |",
        f"| 重排耗时 P50 / P95 | {sec(b['rerank_p50'])} / {sec(b['rerank_p95'])} | {sec(o['rerank_p50'])} / {sec(o['rerank_p95'])} |",
        f"| 请求墙钟 P50 / P95（含生成与追踪） | {sec(b['wall_p50'])} / {sec(b['wall_p95'])} | {sec(o['wall_p50'])} / {sec(o['wall_p95'])} |",
        f"| Planner 输入 / 输出 Token | 0 / 0 | {o['plan_prompt_tokens']:,} / {o['plan_completion_tokens']:,} |",
        f"| 生成输入 / 输出 Token | {b['gen_prompt_tokens']:,} / {b['gen_completion_tokens']:,} | {o['gen_prompt_tokens']:,} / {o['gen_completion_tokens']:,} |",
        f"| 全链路 DeepSeek 总 Token | {b['total_tokens']:,} | {o['total_tokens']:,} |",
        f"| 全量 40 题程序状态 | `{b['statuses']}` | `{o['statuses']}` |",
        '',
        '## 4. LangSmith 与核验',
        '',
        f"- 远端实时 Trace 批量核验：`verified={(summary.get('remote_verification') or {}).get('verified')}`，span 数 `{(summary.get('remote_verification') or {}).get('finished_count')}/{(summary.get('remote_verification') or {}).get('span_count')}`，pending `{(summary.get('remote_verification') or {}).get('pending_events')}`。",
        f"- Dataset/Experiment 同步：`status={(summary.get('dataset_sync') or {}).get('status')}`；对照链接：{ls_url or 'pending'}",
        '',
        '> 说明：上述支持池覆盖、反例程序拒答状态与引用状态均为自动统计，不等于独立人工语义正确率；本轮仍为已曝光开发集对照。',
    ]
    (out_dir / 'findings.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    bars = [
        ('Recall@5 (32题)', b['answerable']['recall5'], o['answerable']['recall5']),
        ('来源覆盖 (32题)', b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage']),
        ('跨论文覆盖 (24题)', b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage']),
        ('跨论文全覆盖 (24题)', b['cross_paper']['all_units'] / 24, o['cross_paper']['all_units'] / 24),
        ('反例拒答 (8题)', b['negative']['refused'] / 8, o['negative']['refused'] / 8),
        ('引用通过 (40题)', 1 - b['citation_errors'] / 40, 1 - o['citation_errors'] / 40),
    ]
    svg_parts = ['<svg viewBox="0 0 880 240" width="100%" style="max-width:880px;background:#fff;border:1px solid #e5e7eb;border-radius:8px">']
    for idx, (label, bv, ov) in enumerate(bars):
        x = 45 + idx * 138
        bh = int((bv or 0) * 150)
        oh = int((ov or 0) * 150)
        svg_parts.append(f'<rect x="{x}" y="{185-bh}" width="40" height="{bh}" fill="#94a3b8" rx="3"/>')
        svg_parts.append(f'<text x="{x+20}" y="{179-bh}" font-size="11" text-anchor="middle" fill="#334155">{(bv or 0)*100:.1f}%</text>')
        svg_parts.append(f'<rect x="{x+46}" y="{185-oh}" width="40" height="{oh}" fill="#059669" rx="3"/>')
        svg_parts.append(f'<text x="{x+66}" y="{179-oh}" font-size="11" text-anchor="middle" fill="#047857">{(ov or 0)*100:.1f}%</text>')
        svg_parts.append(f'<text x="{x+43}" y="208" font-size="11" text-anchor="middle" fill="#0f172a">{html.escape(label)}</text>')
    svg_parts.append('<rect x="560" y="10" width="12" height="12" fill="#94a3b8"/><text x="576" y="20" font-size="11">P0-SingleQuery</text>')
    svg_parts.append('<rect x="690" y="10" width="12" height="12" fill="#059669"/><text x="706" y="20" font-size="11">P2-Planner-OwnerRerank</text>')
    svg_parts.append('</svg>')

    case_cards = []
    for case in bench['cases']:
        cid = case['id']
        rb = rows_by_key.get((cid, ARMS[0]), {})
        ro = rows_by_key.get((cid, ARMS[1]), {})
        comp = comparisons.get(cid, {})
        diff_cov = (comp.get('p2_minus_p0') or {}).get('evidence_coverage')
        badge = ''
        if diff_cov is not None:
            color = '#16a34a' if diff_cov > 1e-9 else ('#dc2626' if diff_cov < -1e-9 else '#64748b')
            badge = f'<span style="color:{color};font-weight:600">覆盖差值 {diff_cov*100:+.1f}pp</span>'
        plan = (ro.get('retrieval_summary') or {}).get('query_plan') or {}
        plan_html = f"<p><strong>P2 Query Plan：</strong><code>{html.escape(str(plan.get('decision')))}</code> · keywords={html.escape(json.dumps(plan.get('english_keywords', []), ensure_ascii=False))} · subqueries={html.escape(json.dumps(plan.get('subqueries', []), ensure_ascii=False))}</p>"
        facts_html = ''.join(f"<li><code>{html.escape(u)}</code>: {html.escape(bench['units'][u]['answer_point'])}</li>" for u in case['units'])
        def arm_panel(title, row):
            ev_list = ''.join(
                f"<li><code>{html.escape(e['chunk_id'])}</code> ({html.escape(e['title'])} p.{e['page_start']}-{e['page_end']}, score={e.get('rerank_score') if e.get('rerank_score') is not None else 'N/A'})</li>"
                for e in (row.get('evidence') or [])
            )
            trace = row.get('trace_url') or ''
            trace_link = f'<a href="{html.escape(trace)}" target="_blank">LangSmith Trace</a>' if trace else 'N/A'
            pc = row.get('premise_check')
            pc_html = f"<p><strong>Premise Check：</strong></p><pre style='white-space:pre-wrap;font-size:11px'>{html.escape(json.dumps(pc, ensure_ascii=False, indent=2))}</pre>" if pc is not None else ''
            return (
                f"<div style='flex:1;min-width:300px;border:1px solid #e2e8f0;padding:10px;border-radius:6px;background:#f8fafc'>"
                f"<h4>{html.escape(title)} · status=<code>{html.escape(str(row.get('status')))}</code> · "
                f"cov={pct((row.get('metrics') or {}).get('evidence_coverage'))} · "
                f"ev={len(row.get('evidence') or [])} · {sec(row.get('retrieval_compute_seconds'))} · {trace_link}</h4>"
                f"{pc_html}<p><strong>回答：</strong></p><pre style='white-space:pre-wrap;font-size:12px'>{html.escape(str(row.get('answer') or ''))}</pre>"
                f"<p><strong>入选证据：</strong></p><ul style='font-size:12px'>{ev_list}</ul></div>"
            )
        case_cards.append(
            f"<details style='margin:10px 0;border:1px solid #cbd5e1;border-radius:8px;padding:10px'>"
            f"<summary><strong>{html.escape(cid)}</strong> [{html.escape(case['category'])}] {html.escape(case['question'])} — "
            f"P0: <code>{html.escape(str(rb.get('status')))}</code> ({pct((rb.get('metrics') or {}).get('evidence_coverage'))}) → "
            f"P2: <code>{html.escape(str(ro.get('status')))}</code> ({pct((ro.get('metrics') or {}).get('evidence_coverage'))}) {badge}</summary>"
            f"<div style='margin-top:8px'>{plan_html}<p><strong>参考要点：</strong></p><ul style='font-size:12px'>{facts_html or '<li>反例（无支持事实）</li>'}</ul>"
            f"<div style='display:flex;gap:12px;flex-wrap:wrap'>{arm_panel('P0-SingleQuery', rb)}{arm_panel('P2-Planner-OwnerRerank', ro)}</div></div></details>"
        )

    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(bench['version'])} 对照仪表板</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:1280px;margin:20px auto;padding:0 16px;color:#0f172a}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #cbd5e1;padding:6px 10px;text-align:left;font-size:13px}}th{{background:#f1f5f9}}</style></head>
<body><h1>{html.escape(bench['version'])} 端到端对照仪表板</h1>
<p>运行 ID: <code>{html.escape(summary['run_id'])}</code> · LangSmith 对照: {f'<a href="{html.escape(ls_url)}" target="_blank">{html.escape(ls_url)}</a>' if ls_url else 'pending'}</p>
<h2>汇总指标对比柱状图</h2>{''.join(svg_parts)}
<h2>汇总统计表（32 道可回答题 + 8 道反例）</h2>
<table><tr><th>指标</th><th>P0-SingleQuery</th><th>P2-Planner-OwnerRerank</th><th>差值</th></tr>
<tr><td>SupportRecall@5 (32题)</td><td>{pct(b['answerable']['recall5'])}</td><td>{pct(o['answerable']['recall5'])}</td><td>{pp(b['answerable']['recall5'], o['answerable']['recall5'])}</td></tr>
<tr><td>最终来源覆盖 (32题)</td><td>{pct(b['answerable']['evidence_coverage'])}</td><td>{pct(o['answerable']['evidence_coverage'])}</td><td>{pp(b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage'])}</td></tr>
<tr><td>必要来源全覆盖题数</td><td>{b['answerable']['all_units']}/32</td><td>{o['answerable']['all_units']}/32</td><td>{o['answerable']['all_units']-b['answerable']['all_units']:+d}</td></tr>
<tr><td>跨论文来源覆盖 (24题)</td><td>{pct(b['cross_paper']['evidence_coverage'])} ({b['cross_paper']['all_units']}/24)</td><td>{pct(o['cross_paper']['evidence_coverage'])} ({o['cross_paper']['all_units']}/24)</td><td>{pp(b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage'])}</td></tr>
<tr><td>反例拒答 (8题)</td><td>{b['negative']['refused']}/8</td><td>{o['negative']['refused']}/8</td><td>{o['negative']['refused']-b['negative']['refused']:+d}</td></tr>
<tr><td>引用协议失败 (40题)</td><td>{b['citation_errors']}</td><td>{o['citation_errors']}</td><td>{o['citation_errors']-b['citation_errors']:+d}</td></tr>
<tr><td>Planner 耗时 P50 / P95</td><td>-</td><td>{sec(o['planner_p50'])} / {sec(o['planner_p95'])}</td><td>-</td></tr>
<tr><td>全链路 DeepSeek 总 Token</td><td>{b['total_tokens']:,}</td><td>{o['total_tokens']:,}</td><td>{o['total_tokens']-b['total_tokens']:+,}</td></tr>
</table>
<h2>逐题完整详情（40 题）</h2>{''.join(case_cards)}
</body></html>"""
    (out_dir / 'dashboard.html').write_text(page, encoding='utf-8')
    return out_dir


def execute(root, prepare_only=False, resume=None):
    bench, digest, _ = freeze(root)
    cfg = settings(root)
    recorder = P2Dataset(root, VERSION)
    if resume is not None:
        try:
            summary_path = Path(resume)
            status = recorder.sync_run(summary_path, 'full') if cfg.get('LANGSMITH_API_KEY') else dict(status='skipped_no_key')
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
            summary['dataset_sync'] = status
            atomic_json(summary_path, summary)
            render_report(root, summary_path)
            print(json.dumps(dict(status='resumed', dataset_sync=status), ensure_ascii=False), flush=True)
            return status
        finally:
            recorder.close()
    if cfg.get('LANGSMITH_API_KEY'):
        try:
            recorder.sync_dataset()
        except Exception:
            recorder.status.update(status='pending_sync', error_type='sync_failed')
            write_json(recorder.status_path, recorder.status)
            recorder.close()
            raise RuntimeError('dataset_sync_required_before_model_calls') from None
    if prepare_only:
        recorder.close()
        print(json.dumps(dict(status='prepared', benchmark=VERSION, sha256=digest), ensure_ascii=False), flush=True)
        return dict(status='prepared', benchmark=VERSION, sha256=digest)

    run_id = uuid.uuid4().hex
    report_root = root / 'artifacts/reports/stage-4' / VERSION
    destination = report_root / 'runs' / run_id
    destination.mkdir(parents=True)
    workflow = Workflow(root, cfg, query_mode='cloud', graph_enabled=False)
    workflow.providers.client.close()
    provider = FlexibleCachedProviders(cfg, workflow.audit)
    workflow.providers = provider
    if workflow.corpus_id != bench['corpus_id']:
        raise RuntimeError('corpus_changed')
    report = dict(run_id=run_id, started=now(), benchmark_sha256=digest, benchmark=VERSION,
                  status='running', arm_configs=deepcopy(ARM_CONFIGS), results=[])
    atomic_json(destination / 'summary.json', report)
    root_ids = []
    try:
        index = workflow.store.inspect()
        if index['counts'] != [dict(chunks=980, papers=14)] or any(r['state'] != 'ONLINE' for r in index['indexes']):
            raise RuntimeError('index_preflight_failed')
        atomic_json(destination / 'index-snapshot.json', index)
        rid = workflow.audit.start('[stage4 p2 shared GPU warmup metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        warm = workflow.audit.stage(rid, 'gpu_warmup', lambda: run_worker(root, cfg, 'rerank',
            [dict(text='Source evidence supports retrieval.')], query='source evidence', timeout=180))
        warm.pop('outputs', None)
        if warm.get('device') != 'cuda':
            raise RuntimeError('gpu_reranker_unavailable')
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(reranker=warm)))
        report['prewarm'] = warm

        texts = [normalize(c['question']) for c in bench['cases']]
        if not workflow.compatible():
            raise RuntimeError('cloud_compatibility_gate_failed')
        rid = workflow.audit.start('[stage4 p2 shared cloud query-vector batch metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        t0 = time.monotonic()
        vectors = workflow.audit.stage(rid, 'shared_query_embeddings', lambda: Providers.embedding(provider, rid, texts))
        report['shared_embedding_batch_seconds'] = time.monotonic() - t0
        provider.vectors = dict(zip(texts, vectors))
        cache = root / '.cache/stage4-p2' / run_id
        cache.mkdir(parents=True)
        atomic_json(cache / 'query-vectors.json', provider.vectors)
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(query_count=len(texts), vector_dimensions=1024)))

        for number, case in enumerate(bench['cases'], 1):
            order_arms = [ARMS[0], ARMS[1]] if number % 2 else [ARMS[1], ARMS[0]]
            for arm in order_arms:
                for key, val in ARM_CONFIGS[arm].items():
                    if key == 'query_planner':
                        workflow.query_planner_enabled = val
                    elif key == 'premise_check':
                        workflow.premise_check_enabled = val
                    else:
                        setattr(workflow, key, val)
                req_started = time.monotonic()
                rid = workflow.audit.start(case['question'])
                root_ids.append(workflow.audit.live_requests[rid])
                state = dict(request_id=rid, question=case['question'], errors=[], citations=[], evidence=[],
                             graph_paths=[], usage=None, estimated_cost=None, model_name=None, status='running')
                timings = []
                def retrieve_pipeline():
                    for name in ('validate', 'retrieve', 'graph_expand', 'rerank', 'evidence'):
                        if state.get('status') in ('refused', 'error', 'invalid_input'):
                            break
                        began = time.monotonic()
                        state.update(getattr(workflow, name)(state))
                        timings.append(dict(name=name, seconds=time.monotonic() - began))
                    return dict(retrieval_summary=state.get('retrieval_summary'), status=state['status'],
                                errors=state['errors'], timings=timings)
                workflow.audit.stage(rid, 'retrieval_pipeline', retrieve_pipeline)
                if state.get('status') == 'error' or any(e.startswith(('embedding_unavailable', 'reranker_skipped')) for e in state['errors']):
                    workflow.audit.finish(rid, dict(status='error', errors=state['errors']))
                    raise RuntimeError('declared_retrieval_configuration_failed')
                if state['status'] == 'running':
                    if case['generate']:
                        state.update(workflow.audit.stage(rid, 'generate', lambda: workflow.generate(state)))
                        state.update(workflow.audit.stage(rid, 'citations', lambda: workflow.citations(state)))
                    else:
                        state.update(status='evidence_only', answer='本题按预先冻结口径仅比较检索证据。')
                result = {k: state.get(k) for k in ('request_id', 'status', 'answer', 'citations', 'premise_check',
                    'evidence', 'graph_paths', 'generation_paths', 'limitations', 'retrieval_summary', 'usage',
                    'model_name', 'errors', 'raw', 'ranked')}
                result.update(
                    case_id=case['id'], question=case['question'], category=case['category'], arm=arm,
                    order=order_arms.index(arm) + 1, generate_requested=case['generate'],
                    compute_timings=timings, retrieval_compute_seconds=sum(t['seconds'] for t in timings),
                    request_wall_seconds=time.monotonic() - req_started,
                    embedding_source='shared frozen Q00 vector + live batch for planned subqueries',
                    stage_timings=[dict(r) for r in workflow.audit.conn.execute('SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started', (rid,))],
                    provider_calls=[dict(r) for r in workflow.audit.conn.execute('SELECT provider,attempt,status,http_status,seconds,usage FROM calls WHERE request_id=? ORDER BY started', (rid,))],
                    candidate_channels=[dict(r) for r in workflow.audit.conn.execute('SELECT channel,rank,chunk_id,score FROM candidates WHERE request_id=? ORDER BY channel,rank', (rid,))],
                    criterion_source_coverage=criterion_source_coverage(case, [e['chunk_id'] for e in state['evidence']], bench['units']),
                )
                result['metrics'] = support_metrics([r['chunk_id'] for r in state.get('ranked', [])],
                    [e['chunk_id'] for e in state['evidence']], [bench['units'][u] for u in case['units']])
                workflow.audit.finish(rid, result)
                result['trace_url'] = workflow.audit.live.url(workflow.audit.live_requests[rid])
                workflow.audit.finish(rid, result)
                atomic_json(destination / (case['id'] + ('-p2.json' if arm == ARMS[1] else '-p0.json')), result)
                report['results'].append(result)
                atomic_json(destination / 'summary.json', report)
                plan_dec = ((state.get('retrieval_summary') or {}).get('query_plan') or {}).get('decision')
                print(json.dumps(dict(case=case['id'], arm=arm, plan=plan_dec, status=result['status'],
                    recall5=result['metrics']['recall5'], ev_cov=result['metrics']['evidence_coverage'],
                    ev_n=len(result['evidence']), seconds=round(result['retrieval_compute_seconds'], 3)), ensure_ascii=False), flush=True)

        atomic_json(cache / 'query-vectors.json', provider.vectors)
        report['remote_verification'] = _verify_remote_batched(workflow.audit.live, root_ids)
        report.update(status='completed', finished=now(),
                      shared_vector_cache_hits=provider.cache_hits,
                      live_subquery_embeddings=provider.live_subquery_embeds)
        atomic_json(destination / 'summary.json', report)
        atomic_json(report_root / 'latest.json', dict(directory=str(destination)))
    except Exception as exc:
        report.update(status='interrupted', error_code=type(exc).__name__, finished=now())
        atomic_json(destination / 'summary.json', report)
        raise
    finally:
        try:
            if cfg.get('LANGSMITH_API_KEY') and report['results']:
                report['dataset_sync'] = recorder.sync_run(destination / 'summary.json', 'full')
        except Exception as exc:
            report['dataset_sync'] = dict(status='pending_sync', error_type=type(exc).__name__)
            recorder.status.update(report['dataset_sync'])
            write_json(recorder.status_path, recorder.status)
        finally:
            atomic_json(destination / 'summary.json', report)
            if report['results']:
                render_report(root, destination / 'summary.json')
            recorder.close()
            workflow.close()
            close_workers()
    print(json.dumps(dict(status=report['status'], directory=str(destination),
        remote_verified=(report.get('remote_verification') or {}).get('verified'),
        dataset_sync=(report.get('dataset_sync') or {}).get('status')), ensure_ascii=False), flush=True)
    return report
