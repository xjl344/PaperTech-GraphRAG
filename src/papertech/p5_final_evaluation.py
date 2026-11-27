"""Final 40-question end-to-end paired evaluation on new API:
P3-RoundRobin-V2 vs P4-BalancedMMR-V3 (isolating Balanced-MMR + source-choice-v3 [E1:q2]).
"""
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
from .isolated_graph import IsolatedGraph
from .local_models import run_worker, vector_metadata
from .method_cards import MethodCardNavigator, load_aux_vectors
from .p3_evaluation import CARDS_REL, CLAIM_VECS_REL, SLOT_VECS_REL, SharedPlanAndVectorProviders
from .providers import Providers
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings
from .workflow import Workflow

VERSION = 'benchmark-v5-final-v1'
PARENT_BENCH = 'benchmark-v4'
ARMS = ('P3-RoundRobin-V2', 'P4-BalancedMMR-V3')
ARM_CONFIGS = {
    'P3-RoundRobin-V2': dict(
        graph_enabled=True, graph_query_aware=True, use_method_cards=True, path_budget=1200,
        rerank_contextual=True, rerank_windowed=False, evidence_budget=18000, evidence_max=12,
        source_policy='named_first', score_policy='relative', reservation_policy='round_robin',
        citation_protocol='source-choice-v2', query_planner=True, premise_check=True,
    ),
    'P4-BalancedMMR-V3': dict(
        graph_enabled=True, graph_query_aware=True, use_method_cards=True, path_budget=1200,
        rerank_contextual=True, rerank_windowed=False, evidence_budget=18000, evidence_max=12,
        source_policy='named_first', score_policy='relative', reservation_policy='subquery_balanced',
        citation_protocol='source-choice-v3', query_planner=True, premise_check=True,
    ),
}
CODE_FILES = (
    'src/papertech/entity_aliases.py', 'src/papertech/local_models.py',
    'src/papertech/isolated_graph.py', 'src/papertech/method_cards.py',
    'src/papertech/query_planner.py', 'src/papertech/rerank_runtime.py',
    'src/papertech/rerank_service.py', 'src/papertech/retrieval.py',
    'src/papertech/evidence_context.py', 'src/papertech/citations.py',
    'src/papertech/providers.py', 'src/papertech/workflow.py',
    'src/papertech/graph_store.py', 'src/papertech/p5_final_evaluation.py',
    'scripts/eval-stage4.py',
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _verify_remote_batched_strict(live, root_ids):
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
    for attempt in range(5):
        missing = [sid for sid in span_ids if sid not in found or found[sid].end_time is None]
        if not missing:
            break
        for i in range(0, len(missing), 50):
            batch = missing[i:i + 50]
            for run in live.client.list_runs(run_ids=batch, limit=len(batch),
                    select=['id', 'name', 'end_time', 'prompt_tokens', 'completion_tokens']):
                found[str(run.id)] = run
        if any(sid not in found or found[sid].end_time is None for sid in span_ids) and attempt < 4:
            time.sleep(3)
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


def freeze(root):
    directory = root / 'artifacts/eval/stage-4' / VERSION
    bench_path = directory / 'benchmark.json'
    cards_path = root / CARDS_REL
    cards_sha = sha(cards_path)
    code_hashes = {name: sha(root / name) for name in CODE_FILES}
    if bench_path.exists():
        bench, digest, _ = load_benchmark(root, VERSION)
        if bench.get('code_sha256') != code_hashes or bench.get('method_cards_sha256') != cards_sha:
            raise RuntimeError('frozen_p5_code_or_cards_changed')
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
        version=VERSION, created_at=now(), parent_benchmark=PARENT_BENCH, parent_benchmark_sha256=parent_sha,
        method_cards_path=CARDS_REL, method_cards_sha256=cards_sha,
        arms=list(ARMS), arm_configs=deepcopy(ARM_CONFIGS), models=models, code_sha256=code_hashes,
        dataset_description='阶段4最终版端到端40题配对闭环对照（新 deepseek-v4.1-flash 端点）：P3-RoundRobin-V2 vs P4-BalancedMMR-V3（严格验证 Balanced-MMR 与 [E1:q2] 单点引用协议的端到端覆盖率与引用通过率）。',
        prior_exposure='沿用 benchmark-v4 40 题开发集，用于新端点下的端到端闭环复验；后续另建未见测试集检验泛化。',
        comparison=dict(mode='final_40q_end_to_end_balanced_mmr_and_v3_citations', arms=list(ARMS), generation=True),
        controls=dict(
            arms=list(ARMS), arm_configs=deepcopy(ARM_CONFIGS), backend='neo4j',
            shared_planner_and_vectors='identical query plan, query vectors, and upstream QA-Graph+MethodCard pool per question',
            execution_order='alternate arm order by case index',
            gold_exclusion='question text only; gold pools and reference tables isolated',
        ),
    )
    directory.mkdir(parents=True, exist_ok=True)
    write_json(bench_path, bench)
    digest = sha(bench_path)
    (directory / 'benchmark.sha256').write_text(digest + '\n', encoding='utf-8')
    return bench, digest, directory


def paired_p5_comparisons(summary):
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
        diffs = {k: (opt['metrics'][k] - base['metrics'][k]
                     if opt['metrics'].get(k) is not None and base['metrics'].get(k) is not None else None)
                 for k in METRICS}
        comparisons[case_id] = dict(
            status='paired', p4_minus_p3=diffs, p3_status=base['status'], p4_status=opt['status'],
            shared_evidence=sorted(b_ids & o_ids), added_evidence=sorted(o_ids - b_ids), removed_evidence=sorted(b_ids - o_ids),
            interpretation='客观记录 Balanced-MMR 与 source-choice-v3 相对 P3-V2 的端到端覆盖与引用协议差异，不代替人工语义评分。',
        )
    return comparisons


class P5FinalDataset(DetailedEvaluationDataset):
    def __init__(self, root, version=VERSION, client=None, allow_enrichment=False):
        super().__init__(root, version, client, allow_enrichment=allow_enrichment)
        self.payload['description'] = self.bench['dataset_description']
        self.payload['metadata'].pop('no_model_comparison_run', None)
        for example in self.payload['examples']:
            example['outputs']['result_display']['location'] = '本题关联的 P3-RoundRobin-V2 / P4-BalancedMMR-V3 Experiment runs'
        write_json(self.directory / 'langsmith-dataset.json', self.payload)
        for example in self.payload['examples']:
            write_json(self.directory / 'cases' / (example['metadata']['case_id'] + '.json'), example)
        write_json(self.directory / 'detail-contract.json', dict(detail_profile=PROFILE,
            benchmark_sha256=self.digest,
            examples_sha256=hashlib.sha256(json.dumps(self.payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()))

    def sync_run(self, summary_path, answer_mode='full'):
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        cases = {c['id']: c for c in self.bench['cases']}
        rows = {(r['case_id'], r['arm']): r for r in summary['results']}
        comparisons = paired_p5_comparisons(summary)
        started = datetime.fromisoformat(summary['started'])
        ledger = self.root / 'data/rag.sqlite3'
        payloads = []
        for idx, row in enumerate(summary['results']):
            cid, arm = row['case_id'], row['arm']
            case = cases[cid]
            rid = stable_id(self.digest, summary['run_id'], cid, arm)
            ts = started + timedelta(microseconds=idx)
            out = detailed_output(row, case, self.bench, self.chunks)
            out['answer_local_file'] = cid + ('-p4-v3.json' if arm == ARMS[1] else '-p3-v2.json')
            out['paired_comparison'] = comparisons[cid]
            if row.get('premise_check') is not None:
                out['premise_check'] = deepcopy(row['premise_check'])
            metrics = {k: row['metrics'].get(k) for k in METRICS if case['category'] != 'negative'}
            payload = dict(
                id=rid, name='stage4-p5-final-evaluation', run_type='chain',
                inputs=dict(question=case['question']), outputs=out,
                reference_example_id=stable_id(self.digest, cid),
                start_time=ts, end_time=ts,
                extra=dict(metadata=dict(benchmark=self.bench['version'], benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], request_id=row['request_id'], case_id=cid,
                    arm=arm, capture_mode='evaluation_result_import', detail_profile=PROFILE)),
                tags=[self.bench['version'], arm, case['category']],
                _arm=arm, _metrics=metrics,
            )
            if ledger.exists():
                with sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True) as conn:
                    timing = conn.execute('SELECT started,finished FROM requests WHERE id=?', (row['request_id'],)).fetchone()
                if timing and timing[0] and timing[1]:
                    payload['start_time'], payload['end_time'] = map(datetime.fromisoformat, timing)
                    payload['outputs']['request_wall_seconds'] = (payload['end_time'] - payload['start_time']).total_seconds()
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
            payloads.append(payload)
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(
            benchmark=self.bench['version'], benchmark_sha256=self.digest, detail_profile=PROFILE,
            runs=json.loads(json.dumps(payloads, default=str))))
        write_json(summary_path.parent / 'per-question-comparison.json', comparisons)
        dataset = self.sync_dataset()
        client, experiments = self.client, []
        for arm in ARMS:
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='最终版 40 题端到端对照：Balanced-MMR 与 source-choice-v3 单点引用协议完整结果。',
                metadata=dict(detail_profile=PROFILE, benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], arm=arm, original_status=summary['status']))
            expected = {p['id']: p for p in payloads if p['_arm'] == arm}
            existing = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
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
                            comment='最终版端到端对照自动指标；覆盖与引用状态不代表人工语义正确率。'))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), jobs))
            verified = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(verified) != set(expected):
                raise ValueError('p5_run_readback_mismatch')
            native_usage = self.sync_generation_usage(expected, verified, name)
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))} if expected else {}
            checked = sum(1 for p in expected.values() for k, v in p['_metrics'].items()
                          if v is not None and stable_id(p['id'], k) in feedback)
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(verified),
                feedback_verified=checked, generation_usage_runs_verified=native_usage['verified'], detail_profile=PROFILE))
        self.status.update(status='experiments_verified', original_run_id=summary['run_id'],
            answer_mode='full', result_status=summary['status'], experiments=experiments,
            comparison_url=f"{dataset.url}/compare?selectedSessions=" + ','.join(e['project_id'] for e in experiments))
        write_json(summary_path.parent / 'langsmith-status.json', self.status)
        write_json(self.status_path, self.status)
        return self.status


def _mean(vals):
    nums = [v for v in vals if v is not None]
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
    gen_prompt = sum((r.get('usage') or {}).get('prompt_tokens') or 0 for r in rows)
    gen_comp = sum((r.get('usage') or {}).get('completion_tokens') or 0 for r in rows)
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
    wall_s = [r['request_wall_seconds'] for r in rows if r.get('request_wall_seconds') is not None]
    return dict(
        answerable=block(ans), factual_control=block(fact), cross_paper=block(cross),
        negative=dict(count=len(neg), statuses=dict(neg_statuses), refused=neg_statuses.get('refused', 0)),
        statuses=dict(statuses), citation_errors=statuses.get('citation_error', 0),
        avg_evidence_count=_mean([len(r.get('evidence') or []) for r in rows]),
        gen_prompt_tokens=gen_prompt, gen_completion_tokens=gen_comp, gen_total_tokens=gen_prompt + gen_comp,
        unit_attribution=dict(attr),
        wall_p50=linear_quantile(wall_s, 0.5) if wall_s else None,
        wall_p95=linear_quantile(wall_s, 0.95) if wall_s else None,
    )


def render_report(root, summary_path):
    summary_path = Path(summary_path)
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    bench, digest, _ = load_benchmark(root, summary['benchmark'])
    by_arm = {arm: [r for r in summary['results'] if r['arm'] == arm] for arm in ARMS}
    stats = {arm: _summarize_arm(by_arm[arm], bench) for arm in ARMS}
    comparisons = paired_p5_comparisons(summary)
    b, o = stats[ARMS[0]], stats[ARMS[1]]
    cases_by_id = {c['id']: c for c in bench['cases']}
    rows_by_key = {(r['case_id'], r['arm']): r for r in summary['results']}
    deltas = Counter()
    for cid, comp in comparisons.items():
        if cases_by_id[cid]['category'] == 'negative' or comp.get('status') != 'paired':
            continue
        d = comp['p4_minus_p3']['evidence_coverage']
        deltas['improved' if d > 1e-9 else ('regressed' if d < -1e-9 else 'tied')] += 1
    out_dir = summary_path.parent / 'report'
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / 'comparison.json', dict(benchmark=bench['version'], benchmark_sha256=digest,
        run_id=summary['run_id'], status=summary['status'], stats=stats, deltas=dict(deltas),
        dataset_sync=summary.get('dataset_sync'), remote_verification=summary.get('remote_verification'),
        per_case=comparisons))

    def pct(v): return f'{v*100:.2f}%' if v is not None else 'N/A'
    def pp(a, x): return f'{(x-a)*100:+.2f} pp' if a is not None and x is not None else 'N/A'
    def sec(v): return f'{v:.3f}s' if v is not None else 'N/A'
    ls_url = (summary.get('dataset_sync') or {}).get('comparison_url') or ''

    md = [
        f"# {bench['version']} 最终版端到端 40 题对照报告（P3-RoundRobin-V2 vs P4-BalancedMMR-V3）",
        '',
        f"- 运行 ID：`{summary['run_id']}`；模型：`{bench['models'].get('DEEPSEEK_MODEL')}`；题集 SHA-256：`{digest}`。",
        f"- 两组共享同一份 Query Plan、同批查询向量与相同 QA-Graph+MethodCard 候选池，严格隔离 **Balanced-MMR 证据选择 + `source-choice-v3` (`[E1:q2]`) 单点引用协议**。",
        '',
        '## 1. 核心指标对比（32 道可回答题 + 8 道反例）',
        '',
        '| 指标 | P3-RoundRobin-V2 | P4-BalancedMMR-V3 | 差值 (P4 − P3) |',
        '|---|---:|---:|---:|',
        f"| **32 题最终来源支持单元覆盖** | {pct(b['answerable']['evidence_coverage'])} | **{pct(o['answerable']['evidence_coverage'])}** | **{pp(b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage'])}** |",
        f"| **32 题必要来源全覆盖题数** | {b['answerable']['all_units']}/32 | **{o['answerable']['all_units']}/32** | **{o['answerable']['all_units']-b['answerable']['all_units']:+d} 题** |",
        f"| **24 题跨论文关系来源覆盖** | {pct(b['cross_paper']['evidence_coverage'])} ({b['cross_paper']['all_units']}/24) | **{pct(o['cross_paper']['evidence_coverage'])} ({o['cross_paper']['all_units']}/24)** | **{pp(b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage'])}** |",
        f"| 8 题事实控制覆盖 | {pct(b['factual_control']['evidence_coverage'])} ({b['factual_control']['all_units']}/8) | {pct(o['factual_control']['evidence_coverage'])} ({o['factual_control']['all_units']}/8) | {pp(b['factual_control']['evidence_coverage'], o['factual_control']['evidence_coverage'])} |",
        f"| 事实单元归因（64 单元） | `{b['unit_attribution']}` | `{o['unit_attribution']}` | covered {o['unit_attribution'].get('covered',0)-b['unit_attribution'].get('covered',0):+d} |",
        f"| **引用协议失败 (`citation_error`, 40题)** | {b['citation_errors']}/40 | **{o['citation_errors']}/40** | **{o['citation_errors']-b['citation_errors']:+d} 条** |",
        f"| **反例拒答数 (`refused`, 8题)** | {b['negative']['refused']}/8 | **{o['negative']['refused']}/8** | **{o['negative']['refused']-b['negative']['refused']:+d} 题** |",
        f"| 生成输入 / 输出 / 总 Token | {b['gen_prompt_tokens']:,} / {b['gen_completion_tokens']:,} / {b['gen_total_tokens']:,} | {o['gen_prompt_tokens']:,} / **{o['gen_completion_tokens']:,}** / {o['gen_total_tokens']:,} | 输出 {o['gen_completion_tokens']-b['gen_completion_tokens']:+,} |",
        f"| 请求墙钟 P50 / P95 | {sec(b['wall_p50'])} / {sec(b['wall_p95'])} | {sec(o['wall_p50'])} / {sec(o['wall_p95'])} | - |",
        f"| 全量 40 题程序状态 | `{b['statuses']}` | `{o['statuses']}` | - |",
        '',
        f"逐题覆盖变化（32 题）：**{deltas.get('improved',0)} 增 / {deltas.get('tied',0)} 平 / {deltas.get('regressed',0)} 退**。",
        '',
        '## 2. LangSmith 与核验',
        '',
        f"- 远端实时 Trace 批量核验：`verified={(summary.get('remote_verification') or {}).get('verified')}`，span 数 `{(summary.get('remote_verification') or {}).get('finished_count')}/{(summary.get('remote_verification') or {}).get('span_count')}`，pending `{(summary.get('remote_verification') or {}).get('pending_events')}`。",
        f"- Dataset/Experiment 同步：`status={(summary.get('dataset_sync') or {}).get('status')}`；对照链接：{ls_url or 'pending'}",
    ]
    (out_dir / 'findings.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    bars = [
        ('来源覆盖 (32题)', b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage']),
        ('跨论文覆盖 (24题)', b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage']),
        ('全覆盖比例 (32题)', b['answerable']['all_units']/32, o['answerable']['all_units']/32),
        ('引用通过率 (40题)', 1 - b['citation_errors']/40, 1 - o['citation_errors']/40),
        ('反例拒答率 (8题)', b['negative']['refused']/8, o['negative']['refused']/8),
    ]
    svg = ['<svg viewBox="0 0 780 240" width="100%" style="max-width:780px;background:#fff;border:1px solid #e5e7eb;border-radius:8px">']
    for idx, (label, bv, ov) in enumerate(bars):
        x = 50 + idx * 145
        bh, oh = int((bv or 0)*150), int((ov or 0)*150)
        svg.append(f'<rect x="{x}" y="{185-bh}" width="42" height="{bh}" fill="#94a3b8" rx="3"/>')
        svg.append(f'<text x="{x+21}" y="{179-bh}" font-size="11" text-anchor="middle">{(bv or 0)*100:.1f}%</text>')
        svg.append(f'<rect x="{x+48}" y="{185-oh}" width="42" height="{oh}" fill="#16a34a" rx="3"/>')
        svg.append(f'<text x="{x+69}" y="{179-oh}" font-size="11" text-anchor="middle" fill="#15803d">{(ov or 0)*100:.1f}%</text>')
        svg.append(f'<text x="{x+45}" y="208" font-size="11" text-anchor="middle">{html.escape(label)}</text>')
    svg.append('<rect x="460" y="10" width="12" height="12" fill="#94a3b8"/><text x="476" y="20" font-size="11">P3-RoundRobin-V2</text>')
    svg.append('<rect x="605" y="10" width="12" height="12" fill="#16a34a"/><text x="621" y="20" font-size="11">P4-BalancedMMR-V3</text>')
    svg.append('</svg>')

    cards = []
    for case in bench['cases']:
        cid = case['id']
        rb, ro = rows_by_key[(cid, ARMS[0])], rows_by_key[(cid, ARMS[1])]
        def panel(title, row):
            trace = row.get('trace_url') or ''
            tl = f'<a href="{html.escape(trace)}" target="_blank">Trace</a>' if trace else 'N/A'
            return (f"<div style='flex:1;min-width:300px;border:1px solid #e2e8f0;padding:10px;border-radius:6px;background:#f8fafc'>"
                    f"<h4>{html.escape(title)} · status=<code>{html.escape(str(row['status']))}</code> · cov={pct(row['metrics'].get('evidence_coverage'))} · cites={len(row.get('citations') or [])} · {tl}</h4>"
                    f"<pre style='white-space:pre-wrap;font-size:12px'>{html.escape(str(row.get('answer') or ''))}</pre></div>")
        cards.append(
            f"<details style='margin:8px 0;border:1px solid #cbd5e1;border-radius:6px;padding:8px'>"
            f"<summary><strong>{html.escape(cid)}</strong> [{html.escape(case['category'])}] {html.escape(case['question'])} — "
            f"V2: <code>{html.escape(str(rb['status']))}</code> ({pct(rb['metrics'].get('evidence_coverage'))}) → "
            f"V3: <code>{html.escape(str(ro['status']))}</code> ({pct(ro['metrics'].get('evidence_coverage'))})</summary>"
            f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-top:8px'>{panel(ARMS[0], rb)}{panel(ARMS[1], ro)}</div></details>"
        )
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(bench['version'])}</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:1280px;margin:20px auto;padding:0 16px}}</style></head>
<body><h1>{html.escape(bench['version'])} 最终版 40 题端到端对照仪表板</h1>
<p>运行 ID: <code>{html.escape(summary['run_id'])}</code> · LangSmith: {f'<a href="{html.escape(ls_url)}" target="_blank">{html.escape(ls_url)}</a>' if ls_url else 'pending'}</p>
<h2>汇总指标对比</h2>{''.join(svg)}<h2>40 题逐题对比</h2>{''.join(cards)}</body></html>"""
    (out_dir / 'dashboard.html').write_text(page, encoding='utf-8')
    return out_dir


def execute(root, prepare_only=False, resume=None):
    bench, digest, _ = freeze(root)
    cfg = settings(root)
    recorder = P5FinalDataset(root, VERSION)
    if resume is not None:
        try:
            summary_path = Path(resume)
            status = recorder.sync_run(summary_path, 'full') if cfg.get('LANGSMITH_API_KEY') else dict(status='skipped_no_key')
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
            summary['dataset_sync'] = status
            atomic_json(summary_path, summary)
            render_report(root, summary_path)
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

    model_id = vector_metadata(root)['model_id']
    claim_vectors = load_aux_vectors(root / CLAIM_VECS_REL, model_id)
    snap = bench['graph_snapshot']
    expander = IsolatedGraph(root / snap['database'], snap['sha256'], claim_vectors=claim_vectors)
    navigator = MethodCardNavigator(root / CARDS_REL, root / SLOT_VECS_REL, model_id)

    run_id = uuid.uuid4().hex
    report_root = root / 'artifacts/reports/stage-4' / VERSION
    destination = report_root / 'runs' / run_id
    destination.mkdir(parents=True)
    workflow = Workflow(root, cfg, query_mode='cloud', graph_enabled=True, graph_expander=expander, method_cards=navigator)
    workflow.providers.client.close()
    provider = SharedPlanAndVectorProviders(cfg, workflow.audit)
    workflow.providers = provider
    report = dict(run_id=run_id, started=now(), benchmark_sha256=digest, benchmark=VERSION,
                  status='running', arm_configs=deepcopy(ARM_CONFIGS), results=[])
    atomic_json(destination / 'summary.json', report)
    root_ids = []
    try:
        index = workflow.store.inspect()
        if index['counts'] != [dict(chunks=980, papers=14)] or any(r['state'] != 'ONLINE' for r in index['indexes']):
            raise RuntimeError('index_preflight_failed')
        rid = workflow.audit.start('[stage4 p5 shared GPU warmup metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        warm = workflow.audit.stage(rid, 'gpu_warmup', lambda: run_worker(root, cfg, 'rerank',
            [dict(text='Source evidence supports retrieval.')], query='source evidence', timeout=180))
        warm.pop('outputs', None)
        if warm.get('device') != 'cuda':
            raise RuntimeError('gpu_reranker_unavailable')
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(reranker=warm)))

        texts = [normalize(c['question']) for c in bench['cases']]
        if not workflow.compatible():
            raise RuntimeError('cloud_compatibility_gate_failed')
        rid = workflow.audit.start('[stage4 p5 shared cloud query-vector batch metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        vectors = workflow.audit.stage(rid, 'shared_query_embeddings', lambda: Providers.embedding(provider, rid, texts))
        provider.vectors = dict(zip(texts, vectors))
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(query_count=len(texts), vector_dimensions=1024)))

        for number, case in enumerate(bench['cases'], 1):
            order_arms = [ARMS[0], ARMS[1]] if number % 2 else [ARMS[1], ARMS[0]]
            for arm in order_arms:
                for key, val in ARM_CONFIGS[arm].items():
                    if key == 'query_planner':
                        workflow.query_planner_enabled = val
                    elif key == 'premise_check':
                        workflow.premise_check_enabled = val
                    elif key == 'use_method_cards':
                        workflow.method_cards = navigator if val else None
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
                if state['status'] == 'running' and case['generate']:
                    state.update(workflow.audit.stage(rid, 'generate', lambda: workflow.generate(state)))
                    state.update(workflow.audit.stage(rid, 'citations', lambda: workflow.citations(state)))
                result = {k: state.get(k) for k in ('request_id', 'status', 'answer', 'citations', 'premise_check',
                    'evidence', 'graph_paths', 'generation_paths', 'limitations', 'retrieval_summary', 'usage',
                    'model_name', 'errors', 'raw', 'ranked')}
                result.update(
                    case_id=case['id'], question=case['question'], category=case['category'], arm=arm,
                    order=order_arms.index(arm) + 1, generate_requested=case['generate'],
                    compute_timings=timings, retrieval_compute_seconds=sum(t['seconds'] for t in timings),
                    request_wall_seconds=time.monotonic() - req_started,
                    embedding_source='shared Q00 + shared planned subquery vectors across arms',
                    stage_timings=[dict(r) for r in workflow.audit.conn.execute('SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started', (rid,))],
                    provider_calls=[dict(r) for r in workflow.audit.conn.execute('SELECT provider,attempt,status,http_status,seconds,usage FROM calls WHERE request_id=? ORDER BY started', (rid,))],
                    criterion_source_coverage=criterion_source_coverage(case, [e['chunk_id'] for e in state['evidence']], bench['units']),
                )
                result['metrics'] = support_metrics([r['chunk_id'] for r in state.get('ranked', [])],
                    [e['chunk_id'] for e in state['evidence']], [bench['units'][u] for u in case['units']])
                workflow.audit.finish(rid, result)
                result['trace_url'] = workflow.audit.live.url(workflow.audit.live_requests[rid])
                workflow.audit.finish(rid, result)
                atomic_json(destination / (case['id'] + ('-p4-v3.json' if arm == ARMS[1] else '-p3-v2.json')), result)
                report['results'].append(result)
                atomic_json(destination / 'summary.json', report)
                print(json.dumps(dict(case=case['id'], arm=arm, status=result['status'],
                    ev_cov=result['metrics']['evidence_coverage'], cites=len(result['citations']),
                    wall=round(result['request_wall_seconds'], 2)), ensure_ascii=False), flush=True)

        report['remote_verification'] = _verify_remote_batched_strict(workflow.audit.live, root_ids)
        report.update(status='completed', finished=now())
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
            expander.close()
            close_workers()
    print(json.dumps(dict(status=report['status'], directory=str(destination),
        remote_verified=(report.get('remote_verification') or {}).get('verified'),
        dataset_sync=(report.get('dataset_sync') or {}).get('status')), ensure_ascii=False), flush=True)
    return report
