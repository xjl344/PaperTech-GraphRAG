"""Zero-cloud-cost local GPU ablation on frozen P3 candidates:
P3-Baseline vs Balanced-MMR vs WindowRerank+Balanced-MMR.
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
import time
import uuid

from .audit import now
from .corpus import load_corpus
from .entity_aliases import is_comparison
from .evaluation import criterion_source_coverage, linear_quantile, support_metrics
from .evaluation_datasets import METRICS, load_benchmark, output_payload, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, PROFILE, detailed_output
from .evidence_context import assemble
from .ingest import atomic_json
from .local_models import run_worker
from .rerank_service import close_workers
from .retrieval import chunk_windows, normalize, rerank_view
from .settings import settings

VERSION = 'benchmark-v5-rerank-diversity-v2'
PARENT_BENCH = 'benchmark-v5-graph-v1'
PARENT_RUN = 'artifacts/reports/stage-4/benchmark-v5-graph-v1/runs/688a7351cda240aead9317da1471a777'
PARENT_ARM = 'Strong-Hybrid+QA-Graph+MethodCard'
ARMS = ('P3-Baseline', 'Balanced-MMR', 'WindowRerank+Balanced-MMR')
CODE_FILES = (
    'src/papertech/retrieval.py', 'src/papertech/evidence_context.py',
    'src/papertech/rerank_runtime.py', 'src/papertech/rerank_service.py',
    'src/papertech/citations.py', 'src/papertech/providers.py',
    'src/papertech/workflow.py', 'src/papertech/p4_offline_evaluation.py',
    'scripts/eval-stage4.py',
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(root):
    directory = root / 'artifacts/eval/stage-4' / VERSION
    bench_path = directory / 'benchmark.json'
    code_hashes = {name: sha(root / name) for name in CODE_FILES}
    if bench_path.exists():
        bench, digest, _ = load_benchmark(root, VERSION)
        if bench.get('code_sha256') != code_hashes:
            raise RuntimeError('frozen_p4_code_changed')
        return bench, digest, directory
    parent, parent_sha, _ = load_benchmark(root, PARENT_BENCH)
    parent_summary_path = root / PARENT_RUN / 'summary.json'
    parent_summary_sha = sha(parent_summary_path)
    bench = deepcopy(parent)
    bench.update(
        version=VERSION,
        created_at=now(),
        parent_benchmark=PARENT_BENCH,
        parent_benchmark_sha256=parent_sha,
        parent_run=PARENT_RUN,
        parent_summary_sha256=parent_summary_sha,
        parent_arm=PARENT_ARM,
        arms=list(ARMS),
        code_sha256=code_hashes,
        dataset_description='阶段4 零云端费用离线三组消融（40题固定P3候选池）：P3-Baseline vs Balanced-MMR（跨子查询归一化均衡配额+MMR去重）vs WindowRerank+Balanced-MMR（+块内滑动引文窗精排）；0 次 DeepSeek/Cloudflare 调用。',
        prior_exposure='复用 benchmark-v5-graph-v1 固定候选池与查询规划，属于已曝光开发集纯本地检索/重排/选择消融，不生成新答案。',
        comparison=dict(mode='offline_rerank_and_selection_ablation', arms=list(ARMS), generation=False, cloud_calls=0),
        controls=dict(
            arms=list(ARMS),
            candidate_pool='frozen P3-Graph+MethodCard ranked candidates per question (0 new retrieval/cloud calls)',
            evidence_budget=18000, evidence_max=12, path_budget=1200,
            diversity_threshold=0.55,
            window_config=dict(max_chars=700, overlap=250, max_windows=5, aggregation='max(whole, windows)'),
            generation_calls=0, cloud_embedding_calls=0,
            gold_exclusion='gold pools never used in windowing, reranking, or selection',
        ),
    )
    directory.mkdir(parents=True, exist_ok=True)
    write_json(bench_path, bench)
    digest = sha(bench_path)
    (directory / 'benchmark.sha256').write_text(digest + '\n', encoding='utf-8')
    return bench, digest, directory


def _window_rerank_case(root, cfg, chunk_map, ranked, active_queries, orig_norm):
    """Re-score all candidate chunks using whole-block + overlapping 700-char contextual windows on local GPU."""
    subqueries = [q for q in active_queries if q['id'] != 'Q00']
    owner_scores = {row['chunk_id']: {} for row in ranked}
    batches = []
    covered = set()
    if subqueries:
        for sq in subqueries:
            cids = [row['chunk_id'] for row in ranked if sq['id'] in (row.get('found_by') or ())]
            if cids:
                batches.append((sq['id'], sq['text'], cids))
                covered.update(cids)
        fallback_cids = [row['chunk_id'] for row in ranked if row['chunk_id'] not in covered]
        if fallback_cids:
            batches.append(('Q00', orig_norm, fallback_cids))
    else:
        batches.append(('Q00', orig_norm, [row['chunk_id'] for row in ranked]))

    total_infer, total_windows = 0.0, 0
    for qid, qtext, cids in batches:
        items, owners = [], []
        for cid in cids:
            chunk = chunk_map[cid]
            items.append(rerank_view(chunk, contextual=True))
            owners.append(cid)
            wins = chunk_windows(chunk, max_chars=700, overlap=250, max_windows=5, contextual=True)
            if len(wins) > 1:
                for w in wins:
                    items.append(w)
                    owners.append(cid)
        total_windows += len(items)
        best = {}
        for start in range(0, len(items), 300):
            sub_items = items[start:start + 300]
            sub_owners = owners[start:start + 300]
            out = run_worker(root, cfg, 'rerank', sub_items, query=qtext, timeout=300)
            total_infer += float(out.get('inference_seconds') or 0.0)
            for cid, sc in zip(sub_owners, out['outputs']):
                val = float(sc)
                if cid not in best or val > best[cid]:
                    best[cid] = val
        for cid, sc in best.items():
            owner_scores[cid][qid] = sc

    new_ranked = []
    for row in ranked:
        smap = owner_scores[row['chunk_id']]
        best_qid, best_sc = max(smap.items(), key=lambda kv: (kv[1], kv[0]))
        new_ranked.append(dict(row, rerank_score=best_sc, best_query_id=best_qid, owner_scores=smap))
    new_ranked.sort(key=lambda r: -r['rerank_score'])
    return new_ranked, total_infer, total_windows


def _p4_comparisons(summary):
    pairs = {}
    for row in summary['results']:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    out = {}
    for cid, rows in pairs.items():
        if set(rows) != set(ARMS):
            out[cid] = dict(status='incomplete')
            continue
        base = rows[ARMS[0]]
        diffs = {}
        for arm in ARMS[1:]:
            diffs[arm + '_minus_base'] = {
                k: (rows[arm]['metrics'][k] - base['metrics'][k]
                    if rows[arm]['metrics'].get(k) is not None and base['metrics'].get(k) is not None else None)
                for k in METRICS
            }
        out[cid] = dict(status='paired', **diffs)
    return out


class P4OfflineDataset(DetailedEvaluationDataset):
    def __init__(self, root, version=VERSION, client=None, allow_enrichment=False):
        super().__init__(root, version, client, allow_enrichment=allow_enrichment)
        self.payload['description'] = self.bench['dataset_description']
        self.payload['metadata'].pop('no_model_comparison_run', None)
        for example in self.payload['examples']:
            example['outputs']['evaluation_config'].update(generate=False, cloud_calls=0,
                planned_output='零云端费用离线三组消融回放（不生成新答案）。')
            example['outputs']['result_display']['location'] = '本题关联的 P3-Baseline / Balanced-MMR / WindowRerank+Balanced-MMR Experiment runs'
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
        comparisons = _p4_comparisons(summary)
        started = datetime.fromisoformat(summary['started'])
        payloads = []
        for idx, row in enumerate(summary['results']):
            cid, arm = row['case_id'], row['arm']
            case = cases[cid]
            rid = stable_id(self.digest, summary['run_id'], cid, arm)
            ts = started + timedelta(microseconds=idx)
            out = detailed_output(row, case, self.bench, self.chunks)
            out['paired_comparison'] = comparisons[cid]
            metrics = {k: row['metrics'].get(k) for k in METRICS if case['category'] != 'negative'}
            metrics.update(retrieval_compute_seconds=row.get('retrieval_compute_seconds'),
                           evidence_count=len(row.get('evidence') or []))
            payloads.append(dict(
                id=rid, name='stage4-p4-offline-ablation', run_type='chain',
                inputs=dict(question=case['question']), outputs=out,
                reference_example_id=stable_id(self.digest, cid),
                start_time=ts, end_time=ts,
                extra=dict(metadata=dict(benchmark=self.bench['version'], benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], case_id=cid, arm=arm,
                    capture_mode='offline_ablation_replay', detail_profile=PROFILE)),
                tags=[self.bench['version'], arm, case['category']],
                _arm=arm, _metrics=metrics,
            ))
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(
            benchmark=self.bench['version'], benchmark_sha256=self.digest, detail_profile=PROFILE,
            runs=json.loads(json.dumps(payloads, default=str))))
        dataset = self.sync_dataset()
        client, experiments = self.client, []
        for arm in ARMS:
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='零云端费用离线消融三组对照：候选重排、证据覆盖与逐题差异。',
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
                            comment='零云端费用离线消融自动支持池指标。'))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), jobs))
            verified = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(verified) != set(expected):
                raise ValueError('p4_run_readback_mismatch')
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))} if expected else {}
            checked = sum(1 for p in expected.values() for k, v in p['_metrics'].items()
                          if v is not None and stable_id(p['id'], k) in feedback)
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(verified),
                feedback_verified=checked, detail_profile=PROFILE))
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
    def block(items):
        return dict(
            count=len(items),
            recall5=_mean([r['metrics']['recall5'] for r in items]),
            recall8=_mean([r['metrics']['recall8'] for r in items]),
            mrr40=_mean([r['metrics']['mrr40'] for r in items]),
            evidence_coverage=_mean([r['metrics']['evidence_coverage'] for r in items]),
            all_units=sum(1 for r in items if r['metrics'].get('all_units')),
        )
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
    secs = [r['retrieval_compute_seconds'] for r in rows]
    return dict(
        answerable=block(ans), factual_control=block(fact), cross_paper=block(cross),
        unit_attribution=dict(attr),
        avg_evidence_count=_mean([len(r['evidence']) for r in rows]),
        avg_context_bytes=_mean([r['retrieval_summary']['context_bytes'] for r in rows]),
        compute_p50=linear_quantile(secs, 0.5), compute_p95=linear_quantile(secs, 0.95),
    )


def render_report(root, summary_path):
    summary_path = Path(summary_path)
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    bench, digest, _ = load_benchmark(root, summary['benchmark'])
    by_arm = {arm: [r for r in summary['results'] if r['arm'] == arm] for arm in ARMS}
    stats = {arm: _summarize_arm(by_arm[arm], bench) for arm in ARMS}
    comps = _p4_comparisons(summary)
    out_dir = summary_path.parent / 'report'
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / 'comparison.json', dict(benchmark=bench['version'], benchmark_sha256=digest,
        run_id=summary['run_id'], stats=stats, dataset_sync=summary.get('dataset_sync'), per_case=comps))

    def pct(v): return f'{v*100:.2f}%' if v is not None else 'N/A'
    def sec(v): return f'{v:.3f}s' if v is not None else 'N/A'
    a0, a1, a2 = stats[ARMS[0]], stats[ARMS[1]], stats[ARMS[2]]
    ls_url = (summary.get('dataset_sync') or {}).get('comparison_url') or ''

    # Count per-case wins/ties/losses vs P3-Baseline
    cases_by_id = {c['id']: c for c in bench['cases']}
    def wtl(arm_key):
        c = Counter()
        for cid, comp in comps.items():
            if cases_by_id[cid]['category'] == 'negative': continue
            d = comp[arm_key + '_minus_base']['evidence_coverage']
            c['improved' if d > 1e-9 else ('regressed' if d < -1e-9 else 'tied')] += 1
        return f"{c['improved']} 增 / {c['tied']} 平 / {c['regressed']} 退"

    md = [
        f"# {bench['version']} 零云端费用离线三组消融报告",
        '',
        f"- 运行 ID：`{summary['run_id']}`；题集 SHA-256：`{digest}`；云端调用：**0 次 DeepSeek / 0 次 Cloudflare**。",
        f"- 固定父运行候选池：`{PARENT_RUN}`（`{PARENT_ARM}`），纯本地验证 **跨子查询均衡配额 + MMR 去重** 与 **块内滑动引文窗精排** 对残余 11 个池内未入选单元的改善。",
        '',
        '## 1. 三组核心指标对比（32 道可回答题）',
        '',
        '| 指标 | P3-Baseline | Balanced-MMR | WindowRerank+Balanced-MMR |',
        '|---|---:|---:|---:|',
        f"| SupportRecall@5 (32题) | {pct(a0['answerable']['recall5'])} | {pct(a1['answerable']['recall5'])} | **{pct(a2['answerable']['recall5'])}** |",
        f"| SupportRecall@8 (32题) | {pct(a0['answerable']['recall8'])} | {pct(a1['answerable']['recall8'])} | **{pct(a2['answerable']['recall8'])}** |",
        f"| MRR@40 (32题) | {a0['answerable']['mrr40']:.4f} | {a1['answerable']['mrr40']:.4f} | **{a2['answerable']['mrr40']:.4f}** |",
        f"| **最终来源支持单元覆盖 (32题)** | {pct(a0['answerable']['evidence_coverage'])} | **{pct(a1['answerable']['evidence_coverage'])}** | **{pct(a2['answerable']['evidence_coverage'])}** |",
        f"| **必要来源全覆盖题数 (32题)** | {a0['answerable']['all_units']}/32 | **{a1['answerable']['all_units']}/32** | **{a2['answerable']['all_units']}/32** |",
        f"| **跨论文关系来源覆盖 (24题)** | {pct(a0['cross_paper']['evidence_coverage'])} ({a0['cross_paper']['all_units']}/24) | **{pct(a1['cross_paper']['evidence_coverage'])} ({a1['cross_paper']['all_units']}/24)** | **{pct(a2['cross_paper']['evidence_coverage'])} ({a2['cross_paper']['all_units']}/24)** |",
        f"| 事实控制来源覆盖 (8题) | {pct(a0['factual_control']['evidence_coverage'])} ({a0['factual_control']['all_units']}/8) | {pct(a1['factual_control']['evidence_coverage'])} ({a1['factual_control']['all_units']}/8) | {pct(a2['factual_control']['evidence_coverage'])} ({a2['factual_control']['all_units']}/8) |",
        f"| 事实单元归因（64 单元） | `{a0['unit_attribution']}` | `{a1['unit_attribution']}` | `{a2['unit_attribution']}` |",
        f"| 相对基线逐题变化 (32题) | 基线 | {wtl(ARMS[1])} | {wtl(ARMS[2])} |",
        f"| 平均证据块 / 字节 | {a0['avg_evidence_count']:.2f} / {a0['avg_context_bytes']:.0f} B | {a1['avg_evidence_count']:.2f} / {a1['avg_context_bytes']:.0f} B | {a2['avg_evidence_count']:.2f} / {a2['avg_context_bytes']:.0f} B |",
        f"| 本地处理耗时 P50 / P95 | {sec(a0['compute_p50'])} / {sec(a0['compute_p95'])} | {sec(a1['compute_p50'])} / {sec(a1['compute_p95'])} | {sec(a2['compute_p50'])} / {sec(a2['compute_p95'])} |",
        '',
        '## 2. LangSmith 对照链接',
        '',
        f"- 同步状态：`{(summary.get('dataset_sync') or {}).get('status')}`；三组在线对照：{ls_url or 'pending'}",
        '',
        '> 说明：本轮为 0 云端费用的离线检索与证据选择消融，不含新答案生成，覆盖率不代表人工语义准确率。',
    ]
    (out_dir / 'findings.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    bars = [
        ('Recall@5 (32题)', a0['answerable']['recall5'], a1['answerable']['recall5'], a2['answerable']['recall5']),
        ('来源覆盖 (32题)', a0['answerable']['evidence_coverage'], a1['answerable']['evidence_coverage'], a2['answerable']['evidence_coverage']),
        ('跨论文覆盖 (24题)', a0['cross_paper']['evidence_coverage'], a1['cross_paper']['evidence_coverage'], a2['cross_paper']['evidence_coverage']),
        ('全覆盖比例 (32题)', a0['answerable']['all_units']/32, a1['answerable']['all_units']/32, a2['answerable']['all_units']/32),
    ]
    svg = ['<svg viewBox="0 0 820 245" width="100%" style="max-width:820px;background:#fff;border:1px solid #e5e7eb;border-radius:8px">']
    colors = ('#94a3b8', '#0284c7', '#16a34a')
    for idx, (label, v0, v1, v2) in enumerate(bars):
        x = 55 + idx * 190
        for j, v in enumerate((v0, v1, v2)):
            h = int((v or 0) * 150)
            bx = x + j * 44
            svg.append(f'<rect x="{bx}" y="{185-h}" width="38" height="{h}" fill="{colors[j]}" rx="3"/>')
            svg.append(f'<text x="{bx+19}" y="{179-h}" font-size="10" text-anchor="middle" fill="#0f172a">{(v or 0)*100:.1f}%</text>')
        svg.append(f'<text x="{x+62}" y="210" font-size="11" text-anchor="middle" fill="#0f172a">{html.escape(label)}</text>')
    for j, arm in enumerate(ARMS):
        lx = 260 + j * 185
        svg.append(f'<rect x="{lx}" y="10" width="12" height="12" fill="{colors[j]}"/><text x="{lx+16}" y="20" font-size="11">{html.escape(arm)}</text>')
    svg.append('</svg>')

    rows_by_key = {(r['case_id'], r['arm']): r for r in summary['results']}
    cards = []
    for case in bench['cases']:
        cid = case['id']
        r0, r1, r2 = rows_by_key[(cid, ARMS[0])], rows_by_key[(cid, ARMS[1])], rows_by_key[(cid, ARMS[2])]
        cards.append(
            f"<details style='margin:8px 0;border:1px solid #cbd5e1;border-radius:6px;padding:8px'>"
            f"<summary><strong>{html.escape(cid)}</strong> [{html.escape(case['category'])}] {html.escape(case['question'])} — "
            f"Base: {pct(r0['metrics']['evidence_coverage'])} → Bal-MMR: {pct(r1['metrics']['evidence_coverage'])} → Win+Bal-MMR: <strong>{pct(r2['metrics']['evidence_coverage'])}</strong></summary>"
            f"<div style='font-size:12px;margin-top:6px'><p>P3-Baseline ({len(r0['evidence'])}块): <code>{html.escape(', '.join(e['chunk_id'] for e in r0['evidence']))}</code></p>"
            f"<p>Balanced-MMR ({len(r1['evidence'])}块): <code>{html.escape(', '.join(e['chunk_id'] for e in r1['evidence']))}</code></p>"
            f"<p>WindowRerank+Balanced-MMR ({len(r2['evidence'])}块): <code>{html.escape(', '.join(e['chunk_id'] for e in r2['evidence']))}</code></p></div></details>"
        )
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(bench['version'])}</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:1200px;margin:20px auto;padding:0 16px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #cbd5e1;padding:6px 10px;font-size:13px}}th{{background:#f1f5f9}}</style></head>
<body><h1>{html.escape(bench['version'])} 零云端费用三组消融仪表板</h1>
<p>运行 ID: <code>{html.escape(summary['run_id'])}</code> · LangSmith 三组对照: {f'<a href="{html.escape(ls_url)}" target="_blank">{html.escape(ls_url)}</a>' if ls_url else 'pending'}</p>
<h2>三组指标对比柱状图</h2>{''.join(svg)}
<h2>逐题对比（40 题）</h2>{''.join(cards)}</body></html>"""
    (out_dir / 'dashboard.html').write_text(page, encoding='utf-8')
    return out_dir


def execute(root, prepare_only=False, resume=None):
    bench, digest, _ = freeze(root)
    cfg = settings(root)
    recorder = P4OfflineDataset(root, VERSION)
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
            raise RuntimeError('dataset_sync_required_before_execution') from None
    if prepare_only:
        recorder.close()
        print(json.dumps(dict(status='prepared', benchmark=VERSION, sha256=digest), ensure_ascii=False), flush=True)
        return dict(status='prepared', benchmark=VERSION, sha256=digest)

    _, _, chunks = load_corpus(root)
    chunk_map = {c['chunk_id']: c for c in chunks}
    parent_summary = json.loads((root / PARENT_RUN / 'summary.json').read_text(encoding='utf-8'))
    parent_rows = {r['case_id']: r for r in parent_summary['results'] if r['arm'] == PARENT_ARM}

    run_id = uuid.uuid4().hex
    report_root = root / 'artifacts/reports/stage-4' / VERSION
    destination = report_root / 'runs' / run_id
    destination.mkdir(parents=True)
    report = dict(run_id=run_id, started=now(), benchmark_sha256=digest, benchmark=VERSION,
                  status='running', cloud_calls=0, results=[])
    atomic_json(destination / 'summary.json', report)
    try:
        # Warm local GPU reranker once outside timed query compute.
        warm = run_worker(root, cfg, 'rerank', [dict(text='Source evidence supports retrieval.')],
                          query='source evidence', timeout=180)
        warm.pop('outputs', None)
        if warm.get('device') != 'cuda':
            raise RuntimeError('gpu_reranker_unavailable')
        report['prewarm'] = warm

        for case in bench['cases']:
            cid = case['id']
            prow = parent_rows[cid]
            q = case['question']
            comp_flag = is_comparison(q)
            base_ranked = deepcopy(prow['ranked'])
            graph_paths = deepcopy(prow.get('graph_paths') or [])
            plan = (prow.get('retrieval_summary') or {}).get('query_plan') or {}
            active_queries = [dict(id='Q00', text=normalize(q))]
            for sq in (plan.get('subqueries') or []):
                active_queries.append(dict(id=sq['id'], text=normalize(sq['text'])))
            sq_ids = [x['id'] for x in active_queries if x['id'] != 'Q00']

            # Arm 1: P3-Baseline (exact reproduction of round_robin on frozen P3 candidates)
            t0 = time.monotonic()
            ev0, paths0, det0 = assemble(base_ranked, chunk_map, graph_paths, q, comp_flag,
                budget=18000, path_budget=1200, evidence_max=12, source_policy='named_first',
                score_policy='relative', reservation_policy='round_robin', subquery_ids=sq_ids or None)
            s0 = time.monotonic() - t0

            # Arm 2: Balanced-MMR (per-subquery calibrated round-robin + lexical MMR diversity, 0 extra rerank)
            t1 = time.monotonic()
            ev1, paths1, det1 = assemble(base_ranked, chunk_map, graph_paths, q, comp_flag,
                budget=18000, path_budget=1200, evidence_max=12, source_policy='named_first',
                score_policy='relative', reservation_policy='subquery_balanced',
                subquery_ids=sq_ids or None, diversity_threshold=0.55)
            s1 = time.monotonic() - t1

            # Arm 3: WindowRerank+Balanced-MMR (local GPU sliding quote-window max-score + Balanced-MMR)
            t2 = time.monotonic()
            win_ranked, infer_s, win_count = _window_rerank_case(root, cfg, chunk_map, base_ranked, active_queries, normalize(q))
            ev2, paths2, det2 = assemble(win_ranked, chunk_map, graph_paths, q, comp_flag,
                budget=18000, path_budget=1200, evidence_max=12, source_policy='named_first',
                score_policy='relative', reservation_policy='subquery_balanced',
                subquery_ids=sq_ids or None, diversity_threshold=0.55)
            s2 = time.monotonic() - t2
            det2 = dict(det2, window_rerank_inference_seconds=round(infer_s, 4), window_rerank_items=win_count)

            for arm, ranked_arm, ev, gpaths, det, secs in (
                (ARMS[0], base_ranked, ev0, paths0, det0, s0),
                (ARMS[1], base_ranked, ev1, paths1, det1, s1),
                (ARMS[2], win_ranked, ev2, paths2, det2, s2),
            ):
                metrics = support_metrics([r['chunk_id'] for r in ranked_arm], [e['chunk_id'] for e in ev],
                                          [bench['units'][u] for u in case['units']])
                row = dict(
                    request_id=f'offline-{run_id[:8]}-{cid}-{arm}',
                    case_id=cid, question=q, category=case['category'], arm=arm,
                    status='evidence_only', answer='零云端费用离线消融：仅比较重排与证据选择。',
                    citations=[], evidence=ev, graph_paths=graph_paths, generation_paths=gpaths,
                    limitations=det['limitations'], retrieval_summary=dict(det, query_plan=plan),
                    usage=None, model_name=None, errors=[], ranked=ranked_arm,
                    retrieval_compute_seconds=secs, provider_calls=[],
                    criterion_source_coverage=criterion_source_coverage(case, [e['chunk_id'] for e in ev], bench['units']),
                    metrics=metrics,
                )
                report['results'].append(row)
            print(json.dumps(dict(case=cid,
                base=round(report['results'][-3]['metrics']['evidence_coverage'], 3) if case['category'] != 'negative' else None,
                bal=round(report['results'][-2]['metrics']['evidence_coverage'], 3) if case['category'] != 'negative' else None,
                win=round(report['results'][-1]['metrics']['evidence_coverage'], 3) if case['category'] != 'negative' else None,
                win_s=round(s2, 2)), ensure_ascii=False), flush=True)

        report.update(status='completed', finished=now())
        atomic_json(destination / 'summary.json', report)
        atomic_json(report_root / 'latest.json', dict(directory=str(destination)))
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
            close_workers()
    print(json.dumps(dict(status=report['status'], directory=str(destination),
        dataset_sync=(report.get('dataset_sync') or {}).get('status')), ensure_ascii=False), flush=True)
    return report
