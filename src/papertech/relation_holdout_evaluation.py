"""Frozen two-arm new-question retrieval experiment. References enter post-hoc scoring only."""
from collections import Counter, deque
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

from .audit import now
from .evaluation import support_metrics, criterion_source_coverage, linear_quantile
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, detailed_output
from .evidence_context import assemble
from .isolated_graph import IsolatedGraph
from .local_models import run_worker
from .providers import Providers
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings
from .workflow import Workflow

VERSION = 'benchmark-relation-holdout-v1'
ARMS = ('Graph-only', 'Hybrid')
FILES = ('src/papertech/relation_holdout_evaluation.py', 'src/papertech/retrieval_comparison.py', 'scripts/eval-stage4.py',
    'src/papertech/graph_store.py', 'src/papertech/isolated_graph.py',
    'src/papertech/workflow.py', 'src/papertech/retrieval.py',
    'src/papertech/entity_aliases.py', 'src/papertech/evidence_context.py',
    'src/papertech/evaluation.py', 'src/papertech/evaluation_details.py',
    'src/papertech/evaluation_datasets.py', 'src/papertech/providers.py',
    'src/papertech/local_models.py', 'src/papertech/rerank_service.py', 'scripts/rerank-service.py',
    'src/papertech/relation_holdout_protocol.py', 'src/papertech/relation_holdout_report.py')
REASONS = {
    'covered': '支持池来源已进入上下文',
    'no_entity_anchor': '未匹配到实体；图组不回退到文本检索',
    'outside_graph_scope': '冻结支持池来源未关联到当前图的 Claim',
    'outside_two_hops': '来源在图中，但不在问题锚点的两跳内',
    'bounded_traversal_miss': '来源在两跳范围内，但本轮有界遍历未返回；结合截断日志复核',
    'candidate_cap': '路径已找到来源，但被统一候选上限截断',
    'retrieval_pool_miss': '召回候选中未命中冻结支持池；不等于没有其他有效原文',
    'reranker_threshold': '候选中的支持来源均低于统一重排阈值 0.05',
    'invalid_source_metadata': '候选支持来源缺少可定位原文或页码',
    'context_selection': '支持来源已召回，但未被来源保留/预算/最多8块的选择策略保留',
    'execution_error': '检索或重排执行失败，不能解释为正常漏召回',
    'not_applicable': '本题没有冻结来源单元，检索覆盖不适用',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(root):
    from .relation_holdout_protocol import freeze_protocol
    return freeze_protocol(root, VERSION, ARMS, FILES)


from .retrieval_comparison import (RetrievalWorkflow as BaseRetrievalWorkflow,
    diagnose, graph_inventory, REASONS)


class RetrievalWorkflow(BaseRetrievalWorkflow):
    def produce(self, question, arm, vector, request_id):
        if arm not in ARMS:
            raise ValueError('excluded_arm')
        return super().produce(question, arm, vector, request_id)


class RetrievalDataset(DetailedEvaluationDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload['description'] = self.bench['dataset_description']
        self.payload['metadata'].update(no_model_comparison_run=False, experiment_type='retrieval_only')
        for e in self.payload['examples']:
            e['metadata']['review_origin'] = 'Codex source review; not independent human annotation'
            e['outputs']['result_display'].update(location='Graph-only / Hybrid 两组 Experiment',
                fields=['全部候选原文及分数', '最终证据与位置', '实体/路径/截断', '逐事实失败归因', '两组差异', '时延与上下文字节', '零生成与Token未报告说明', '原始Trace'])
            case = next(c for c in self.bench['cases'] if c['id'] == e['metadata']['case_id'])
            e['outputs'].update(reference_criteria=case['reference_criteria'], novelty=case['novelty'],
                query_form=case['query_form'], graph_source_link_stratum=case['graph_source_link_stratum'])
            e['outputs']['evaluation_config'].update(generate=False, planned_output='仅检索对照；无模型答案、无答案准确率')
            write_json(self.directory / 'cases' / (e['metadata']['case_id'] + '.json'), e)
        write_json(self.directory / 'langsmith-dataset.json', self.payload)

    def sync_run(self, summary_path, answer_mode='full'):
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        if summary['benchmark_sha256'] != self.digest:
            raise ValueError('run_benchmark_mismatch')
        if any(not r.get('trace_url') for r in summary['results']):
            raise ValueError('trace_urls_required_before_experiment_import')
        dataset = self.sync_dataset()
        cases = {c['id']: c for c in self.bench['cases']}
        comparisons = compare_cases(summary)
        payloads = []
        seen = set()
        for row in summary['results']:
            cid, arm = row['case_id'], row['arm']
            if arm not in ARMS or (cid, arm) in seen or row['question'] != cases[cid]['question']:
                raise ValueError('invalid_run_row')
            seen.add((cid, arm))
            out = detailed_output(row, cases[cid], self.bench, self.chunks)
            out.update(diagnosis=row['diagnosis'], two_arm_comparison=comparisons[cid],
                source_metrics=row['source_metrics'], usage_status=row['usage_status'],
                generation_calls=0, generation_tokens=0, request_wall_seconds=row['request_wall_seconds'],
                answer_local_file=f'{cid}-{arm}.json', experiment_type='retrieval_only',
                answer='本轮不生成答案；仅比较检索来源。')
            metrics = {**row['metrics'], **row['source_metrics'],
                'retrieval_compute_seconds': row['retrieval_compute_seconds'],
                'request_wall_seconds': row['request_wall_seconds'],
                'candidate_count': len(row['ranked']), 'evidence_count': len(row['evidence']),
                'context_bytes': row['retrieval_summary'].get('context_bytes', 0), 'generation_calls': 0}
            if cases[cid]['category'] == 'negative':
                metrics = {k: v for k, v in metrics.items() if k not in row['metrics'] and k not in row['source_metrics']}
            rid = stable_id(self.digest, summary['run_id'], cid, arm)
            payloads.append(dict(id=rid, name='stage4-independent-retrieval', run_type='chain',
                inputs=dict(question=row['question']), outputs=out,
                reference_example_id=stable_id(self.digest, cid),
                start_time=row['started'], end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=VERSION, benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], arm=arm, case_id=cid, request_id=row['request_id'],
                    capture_mode='retrieval_result_import', generation=False)),
                tags=[VERSION, arm, row['category']], _arm=arm,
                _metrics={k: v for k, v in metrics.items() if v is not None}))
        if summary['status'] == 'completed' and seen != {(cid, arm) for cid in cases for arm in ARMS}:
            raise ValueError('incomplete_two_arm_run')
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(runs=payloads))
        experiments, client = [], self.client
        for arm in ARMS:
            expected = {p['id']: p for p in payloads if p['_arm'] == arm}
            if not expected:
                continue
            name = f'papertech-{VERSION}-{summary["run_id"][:12]}-{arm}'
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='独立检索开发集：统一40候选上限、6000字节原文、同一重排器；无答案生成。',
                metadata=dict(benchmark_sha256=self.digest, arm=arm, generation=False))
            if str(project.reference_dataset_id) != str(dataset.id):
                raise ValueError('experiment_dataset_mismatch')
            def read_runs():
                return {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            found = read_runs()
            if set(found) - set(expected) or any(r.outputs != expected[rid]['outputs'] for rid, r in found.items()):
                raise ValueError('remote_experiment_modified')
            def upload(p):
                data = {k: v for k, v in p.items() if not k.startswith('_')}
                data['start_time'] = datetime.fromisoformat(data['start_time'])
                data['end_time'] = datetime.fromisoformat(data['end_time'])
                client.create_run(project_name=name, **data)
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upload, [p for rid, p in expected.items() if rid not in found]))
            jobs = [dict(run_id=p['id'], key=k, score=float(v), feedback_id=stable_id(p['id'], k),
                session_id=project.id, start_time=datetime.fromisoformat(p['start_time']), stop_after_attempt=1,
                comment='检索支持池覆盖/实测耗时；不是答案正确率。反例不计覆盖总分。')
                for p in expected.values() for k, v in p['_metrics'].items()]
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))}
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), [j for j in jobs if j['feedback_id'] not in feedback]))
            for attempt in range(6):
                found = read_runs()
                feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))}
                valid = set(found) == set(expected) and all(r.outputs == expected[rid]['outputs'] and
                    str(r.reference_example_id) == expected[rid]['reference_example_id'] and
                    r.start_time == datetime.fromisoformat(expected[rid]['start_time']) and
                    r.end_time == datetime.fromisoformat(expected[rid]['end_time']) for rid, r in found.items())
                valid = valid and all(j['feedback_id'] in feedback and math.isclose(feedback[j['feedback_id']].score,
                    j['score'], abs_tol=.000050001, rel_tol=0) for j in jobs)
                if valid:
                    break
                if attempt == 5:
                    raise ValueError('experiment_feedback_readback_mismatch')
                time.sleep(2)
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(found),
                feedback_verified=len(jobs), generation_calls=0))
        self.status.update(status='experiments_verified', result_status=summary['status'],
            original_run_id=summary['run_id'], experiments=experiments,
            comparison_url=dataset.url + '/compare?selectedSessions=' + ','.join(e['project_id'] for e in experiments))
        write_json(summary_path.parent / 'langsmith-status.json', self.status)
        write_json(self.status_path, self.status)
        return deepcopy(self.status)


def compare_cases(summary):
    result = {}
    for row in summary['results']:
        result.setdefault(row['case_id'], {})[row['arm']] = dict(metrics=row['metrics'],
            selected_chunk_ids=[e['chunk_id'] for e in row['evidence']],
            candidate_count=len(row['ranked']), reasons=row['diagnosis']['reason_counts'])
    return result


def aggregate(rows):
    scored = [r for r in rows if r['category'] != 'negative']
    def mean(key):
        vals = [r['metrics'][key] for r in scored if r['metrics'][key] is not None]
        return sum(vals) / len(vals) if vals else None
    return dict(count=len(rows), scored_count=len(scored),
        **{k: mean(k) for k in ('recall5', 'recall8', 'mrr40', 'evidence_coverage')},
        all_units=sum(r['metrics']['all_units'] is True for r in scored),
        latency_p50=linear_quantile([r['retrieval_compute_seconds'] for r in rows], .5),
        latency_p95=linear_quantile([r['retrieval_compute_seconds'] for r in rows], .95),
        request_p95=linear_quantile([r['request_wall_seconds'] for r in rows], .95),
        average_candidates=sum(len(r['ranked']) for r in rows) / len(rows) if rows else None,
        average_context_bytes=sum(r['retrieval_summary'].get('context_bytes', 0) for r in rows) / len(rows) if rows else None,
        failure_counts=dict(Counter(f['reason'] for r in scored for f in r['diagnosis']['facts'] if f['reason'] != 'covered')),
        statuses=dict(Counter(r['status'] for r in rows)), generation_calls=0, generation_tokens=0)


def make_report(recorder, summary, folder):
    esc = html.escape
    aggs = {a: aggregate([r for r in summary['results'] if r['arm'] == a]) for a in ARMS}
    categories = {cat: {a: aggregate([r for r in summary['results'] if r['arm'] == a and r['category'] == cat]) for a in ARMS}
        for cat in ('fact', 'cross', 'negative')}
    write_json(folder / 'comparison.json', dict(status=summary['status'], aggregates=aggs, categories=categories,
        comparison=compare_cases(summary), dataset_sync=summary.get('dataset_sync'), shared_embedding=summary.get('shared_embedding')))
    def pct(v):
        return '—' if v is None else f'{v:.2%}'
    columns = [('Recall@5', 'recall5', pct), ('Recall@8', 'recall8', pct),
        ('MRR@40', 'mrr40', lambda v: '—' if v is None else f'{v:.4f}'),
        ('最终支持池覆盖', 'evidence_coverage', pct), ('全支持单元覆盖题数', 'all_units', str),
        ('检索计算P50秒', 'latency_p50', lambda v: '—' if v is None else f'{v:.3f}'),
        ('检索计算P95秒', 'latency_p95', lambda v: '—' if v is None else f'{v:.3f}'),
        ('平均候选数', 'average_candidates', lambda v: '—' if v is None else f'{v:.2f}'),
        ('平均上下文UTF-8字节', 'average_context_bytes', lambda v: '—' if v is None else f'{v:.1f}'),
        ('生成调用 / 生成Token', 'generation_calls', lambda v: '0 / 0')]
    lines = ['# 两组独立检索对照', '', f'状态：`{summary["status"]}`；运行 `{summary["run_id"]}`。', '',
        '| 指标 | ' + ' | '.join(ARMS) + ' |', '|---|' + '---:|' * len(ARMS)]
    for name, key, fmt in columns:
        lines.append('| ' + name + ' | ' + ' | '.join(fmt(aggs[a][key]) for a in ARMS) + ' |')
    lines += ['', '覆盖总分仅计32道可回答题；8道反例单列诊断，不评拒答/答案准确率。支持池非穷尽。',
        '检索计算不含共享查询向量、GPU预热和Trace上传；完整请求墙钟另存JSON。',
        'Graph-only最多40条；Hybrid全文20+向量20，去重后最多40条。实际条数不强行补齐。',
        '统一原文6000 UTF-8字节、最多8块；图路径不进入上下文。生成Token为0；Embedding及重排Token未报告，不用上下文字节冒充Token。',
        '当前图为已接触开发来源的整理图，不是全库自动抽取图或未见测试。', '', '## 分类指标', '',
        '| 分类 | 组别 | Recall@5 | 最终覆盖 | 全覆盖题数 |', '|---|---|---:|---:|---:|']
    for cat, arms in categories.items():
        for a in ARMS:
            x = arms[a]
            lines.append(f'| {cat} | {a} | {pct(x["recall5"])} | {pct(x["evidence_coverage"])} | {x["all_units"] if cat != "negative" else "不适用"} |')
    lines += ['', '## 逐题来源覆盖与失败归因', '', '| 题号 | Graph-only | Hybrid |', '|---|---|---|']
    grouped = {c['id']: {r['arm']: r for r in summary['results'] if r['case_id'] == c['id']} for c in recorder.bench['cases']}
    for cid, rows in grouped.items():
        cells = []
        for a in ARMS:
            r = rows.get(a)
            if r is None:
                cells.append('未运行')
                continue
            counts = r['diagnosis']['reason_counts']
            note = '；'.join(f'{REASONS[k]}×{v}' for k, v in counts.items() if k != 'covered') or ('覆盖齐全' if counts else '不适用')
            cells.append(f'{pct(r["metrics"]["evidence_coverage"])}；{note}')
        lines.append('| ' + cid + ' | ' + ' | '.join(cells) + ' |')
    sync = summary.get('dataset_sync', {})
    if sync.get('comparison_url'):
        lines += ['', '[LangSmith两组对照](' + sync['comparison_url'] + ')']
    lines += ['', '[交互总览、柱状图与完整逐题证据](dashboard.html)；[原始汇总](summary.json)。']
    (folder / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    page = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>两组检索对照</title>',
        '<style>body{font:15px system-ui;max-width:1300px;margin:32px auto;padding:0 20px;color:#182536}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #ccd4de;padding:8px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:12px}details{margin:12px 0;padding:10px;border:1px solid #d5dce5}svg{max-width:100%;height:auto}.note{color:#526174}</style>',
        '<h1>Graph-only / Hybrid 检索对照</h1>', f'<p>状态：{esc(summary["status"])}；40题 × 2组。无答案生成。</p>',
        '<p class="note">覆盖仅指冻结支持池，非答案准确率。图谱构建已接触开发来源。生成Token=0；查询Embedding及重排Token未报告。上下文单位为UTF-8字节。</p>']
    if sync.get('comparison_url'):
        page.append(f'<p><a href="{esc(sync["comparison_url"], quote=True)}">LangSmith 两组 Experiment 对照</a>（{esc(sync.get("status", ""))}）</p>')
    page.append('<table><tr><th>指标</th>' + ''.join(f'<th>{a}</th>' for a in ARMS) + '</tr>')
    for name, key, fmt in columns:
        page.append('<tr><td>' + name + '</td>' + ''.join('<td>' + fmt(aggs[a][key]) + '</td>' for a in ARMS) + '</tr>')
    page.append('</table><h2>覆盖对照柱状图（零起点）</h2>')
    def chart(title, data, key):
        parts = [f'<h3>{title}</h3><svg viewBox="0 0 850 175" role="img" aria-label="{title}">',
            '<line x1="150" y1="15" x2="150" y2="145" stroke="#637287"/>']
        for i, a in enumerate(ARMS):
            v = data[a][key]
            width = 0 if v is None else v * 600
            y = 20 + i * 42
            parts.append(f'<text x="0" y="{y+20}" font-size="16">{a}</text><rect x="150" y="{y}" width="{width}" height="27" fill="{("#3975b7", "#bc643d", "#308575")[i]}"/><text x="{160+width}" y="{y+20}" font-size="15">{pct(v)}</text>')
        parts.append('<text x="150" y="168">0%</text><text x="722" y="168">100%</text></svg>')
        return ''.join(parts)
    for key, title in (('recall5', '全部可回答题 Recall@5'), ('evidence_coverage', '全部可回答题 最终支持池覆盖')):
        page.append(chart(title, aggs, key))
    for cat in ('fact', 'cross'):
        page.append(chart(cat + ' 分类最终覆盖', categories[cat], 'evidence_coverage'))
    page.append('<h2>失败原因（可回答题，按缺失支持单元计数）</h2><table><tr><th>原因</th>' + ''.join(f'<th>{a}</th>' for a in ARMS) + '</tr>')
    for key, title in REASONS.items():
        if any(aggs[a]['failure_counts'].get(key) for a in ARMS):
            page.append('<tr><td>' + title + '</td>' + ''.join(f'<td>{aggs[a]["failure_counts"].get(key, 0)}</td>' for a in ARMS) + '</tr>')
    page.append('</table><h2>40题逐题详情</h2><p>每题包含完整参考答案、来源与位置、两组候选/分数、图路径、失败归因、阶段耗时及Trace。反例仅检查来源，不评答案。</p>')
    for case in recorder.bench['cases']:
        cid = case['id']
        example = next(e for e in recorder.payload['examples'] if e['metadata']['case_id'] == cid)
        page.append(f'<details id="{cid}"><summary>{cid} [{case["category"]}] {esc(case["question"])}</summary>')
        page.append('<details><summary>完整参考答案、事实、原文与位置</summary><pre>' + esc(json.dumps(example['outputs'], ensure_ascii=False, indent=2)) + '</pre></details>')
        for a in ARMS:
            row = grouped[cid].get(a)
            if row is None:
                page.append(f'<h3>{a}：未运行</h3>')
                continue
            page.append(f'<h3>{a}：支持覆盖 {pct(row["metrics"]["evidence_coverage"])}</h3>')
            for fact in row['diagnosis']['facts']:
                page.append('<p>' + esc(fact['required_fact'] + ' → ' + fact['explanation']) + '</p>')
            if row.get('trace_url'):
                page.append(f'<p><a href="{esc(row["trace_url"], quote=True)}">原始Trace</a></p>')
            out = detailed_output(row, case, recorder.bench, recorder.chunks)
            out.update(diagnosis=row['diagnosis'], source_metrics=row['source_metrics'], usage_status=row['usage_status'])
            page.append('<details><summary>全部候选原文、证据、路径、评分与阶段耗时</summary><pre>' + esc(json.dumps(out, ensure_ascii=False, indent=2)) + '</pre></details>')
        page.append('</details>')
    page.append('</html>')
    (folder / 'dashboard.html').write_text('\n'.join(page), encoding='utf-8')
    from .relation_holdout_report import supplement
    supplement(recorder, summary, folder, aggregate)


def contract(root, bench, cfg):
    return dict(controls=bench['controls'], graph_snapshot=bench['graph_snapshot'],
        code_sha256={name: sha(root / name) for name in FILES},
        models={k: cfg.get(k) for k in ('CLOUD_BGE_MODEL', 'CLOUD_BGE_PROVIDER', 'LOCAL_RERANKER_PATH',
            'LOCAL_RERANKER_PYTHON', 'LOCAL_RERANKER_DEVICE', 'LOCAL_RERANKER_DTYPE', 'LOCAL_RERANKER_PERSISTENT')},
        endpoints={k: hashlib.sha256(cfg.get(k, '').encode()).hexdigest() for k in ('CLOUD_BGE_BASE_URL', 'NEO4J_URI')},
        latency='retrieval compute excludes shared embedding batch, GPU warmup, audit/trace network; request wall includes tracing',
        generation=False, reference_exclusion='only question/arm/query-vector passed to retrieval; scoring after evidence selection')


def verify(recorder, summary, folder):
    expected = {(c['id'], a) for c in recorder.bench['cases'] for a in ARMS}
    actual = {(r['case_id'], r['arm']) for r in summary['results']}
    if summary['status'] == 'completed' and (actual != expected or len(summary['results']) != len(expected)):
        raise ValueError('result_count_mismatch')
    for row in summary['results']:
        if len(row['ranked']) > 40 or len(row['evidence']) > 8 or row['retrieval_summary'].get('context_bytes', 0) > 6000:
            raise ValueError('budget_violation')
        if row['usage'] is not None or row['generate_requested'] or row['generation_paths'] or row['provider_calls']:
            raise ValueError('unexpected_generation_or_provider_call')
        channels = row['candidate_channels']
        allowed = {'Graph-only': {'graph'}, 'Hybrid': {'fulltext', 'dense'}}[row['arm']]
        if set(channels) != allowed or row['retrieval_summary']['graph_fallback']:
            raise ValueError('channel_isolation_failed')
        for e in row['evidence']:
            source = recorder.chunks[e['chunk_id']]
            if e['quote'] != source['text'] or e['source_spans'] != source['source_spans']:
                raise ValueError('source_provenance_changed')
    result = dict(status='passed', results=len(actual), expected=len(expected),
        counts=dict(Counter(r['arm'] for r in summary['results'])), generation_calls=0,
        budgets=True, channels=True, sources=True, benchmark_sha256=recorder.digest)
    write_json(folder / 'verification.json', result)
    return result


def execute(root, prepare_only=False, resume=None):
    root = Path(root)
    bench = freeze(root)
    cfg = settings(root)
    recorder = RetrievalDataset(root, VERSION)
    if resume:
        folder = Path(resume)
        summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
        try:
            hydrate_trace_urls(recorder.connect(), summary, folder)
            write_json(folder / 'summary.json', summary)
            summary['dataset_sync'] = recorder.sync_run(folder / 'summary.json')
            write_json(folder / 'summary.json', summary)
            make_report(recorder, summary, folder)
            print(json.dumps(summary['dataset_sync'], ensure_ascii=False), flush=True)
        finally:
            recorder.close()
        return
    current = contract(root, bench, cfg)
    if any(current[k] != bench['unchanged_runtime'][k] for k in ('models', 'endpoints')):
        raise ValueError('previous_models_or_endpoints_changed')
    if current['code_sha256'] != bench['code_sha256']:
        raise ValueError('frozen_code_changed_create_new_version')
    if sha(root / bench['graph_snapshot']['database']) != bench['graph_snapshot']['sha256']:
        raise ValueError('graph_modified')
    if prepare_only:
        print(json.dumps(dict(status='not_run', benchmark=VERSION, cases=len(bench['cases']),
            benchmark_sha256=recorder.digest, arms=ARMS, generation_calls=0), ensure_ascii=False), flush=True)
        recorder.close()
        return
    if not cfg.get('LANGSMITH_API_KEY'):
        raise ValueError('langsmith_required_for_requested_experiment')
    recorder.sync_dataset()  # Gate before any model inference or embedding requests.
    run_id = uuid.uuid4().hex
    folder = root / 'artifacts/reports/stage-4' / VERSION / 'runs' / run_id
    summary = dict(run_id=run_id, benchmark=VERSION, benchmark_sha256=recorder.digest,
        status='running', started=now(), results=[], execution_config=current)
    write_json(folder / 'summary.json', summary)
    write_json(folder / 'execution-contract.json', current)
    make_report(recorder, summary, folder)
    graph = IsolatedGraph(root / bench['graph_snapshot']['database'], bench['graph_snapshot']['sha256'])
    workflow = RetrievalWorkflow(root, cfg, query_mode='cloud', graph_enabled=False, graph_expander=graph)
    root_ids = []
    try:
        if workflow.corpus_id != bench['corpus_id'] or not workflow.compatible():
            raise ValueError('corpus_or_embedding_compatibility_failed')
        index = workflow.store.inspect()
        if index['counts'] != [dict(chunks=980, papers=14)] or any(i['state'] != 'ONLINE' for i in index['indexes']):
            raise ValueError('index_not_ready')
        write_json(folder / 'index-snapshot.json', index)
        rid = workflow.audit.start('[two-arm shared GPU warmup]')
        root_ids.append(workflow.audit.live_requests[rid])
        warm = workflow.audit.stage(rid, 'gpu_warmup', lambda: run_worker(root, cfg, 'rerank',
            [dict(text='Source evidence supports retrieval.')], query='source evidence', timeout=180))
        warm.pop('outputs', None)
        if warm.get('device') != 'cuda':
            raise ValueError('gpu_required')
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=warm))
        summary['prewarm'] = warm
        texts = [normalize(c['question']) for c in bench['cases']]
        rid = workflow.audit.start('[two-arm shared cloud query embeddings; Hybrid only]')
        root_ids.append(workflow.audit.live_requests[rid])
        began = time.monotonic()
        vectors = workflow.audit.stage(rid, 'shared_query_embeddings', lambda: Providers.embedding(workflow.providers, rid, texts))
        summary['shared_embedding'] = dict(seconds=time.monotonic() - began, query_count=len(texts),
            used_by=['Hybrid'], calls=[dict(r) for r in workflow.audit.conn.execute(
                'SELECT provider,status,http_status,seconds,usage FROM calls WHERE request_id=?', (rid,))],
            allocation='one batch used only by Hybrid; Graph-only uses none; per-question embedding time not measured')
        write_json(root / '.cache/retrieval-comparison' / run_id / 'query-vectors.json', dict(zip(texts, vectors)))
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(query_count=len(texts))))
        for n, case in enumerate(bench['cases']):
            order = ARMS[n % len(ARMS):] + ARMS[:n % len(ARMS)]
            for arm in order:
                started = now()
                wall = time.monotonic()
                rid = workflow.audit.start(case['question'])
                root_ids.append(workflow.audit.live_requests[rid])
                state = dict(request_id=rid, question=case['question'], normalized=normalize(case['question']),
                    classification='comparison', status='running', errors=[], ranked=[], evidence=[], graph_paths=[])
                timings = []
                def measured(name, fn):
                    def call():
                        began = time.monotonic()
                        value = fn()
                        timings.append(dict(name=name, seconds=time.monotonic() - began))
                        return value
                    return workflow.audit.stage(rid, name, call)
                state.update(measured('validate', lambda: workflow.validate(state)))
                try:
                    state.update(measured('candidate_retrieval', lambda: workflow.produce(
                        state['question'], arm, None if arm == 'Graph-only' else vectors[n], rid)))
                    if state['ranked']:
                        state.update(measured('rerank', lambda: workflow.rerank(state)))
                        if state['errors']:
                            raise RuntimeError('reranker_failed_no_fallback')
                    def select():
                        evidence, _, detail = assemble(state['ranked'], workflow.chunk_map, [], state['question'],
                            state['classification'] == 'comparison', budget=6000, path_budget=0)
                        return dict(evidence=evidence, retrieval_summary=dict(state['retrieval_summary'], **detail))
                    state.update(measured('evidence', select))
                    state['status'] = 'evidence_only' if state['evidence'] else 'no_evidence'
                except Exception as exc:
                    state.update(status='error', errors=state['errors'] + [type(exc).__name__])
                row = {k: deepcopy(state.get(k)) for k in ('request_id', 'question', 'status', 'errors',
                    'ranked', 'evidence', 'graph_paths', 'candidate_channels', 'retrieval_summary')}
                row['retrieval_summary'] = row['retrieval_summary'] or dict(arm=arm, graph_fallback=False)
                row['candidate_channels'] = row['candidate_channels'] or {k: [] for k in
                    {'Graph-only': ['graph'], 'Hybrid': ['dense', 'fulltext']}[arm]}
                row.update(case_id=case['id'], category=case['category'], arm=arm, order=order.index(arm) + 1,
                    started=started, finished=now(), generate_requested=False,
                    answer='本轮仅检索，不生成答案。', citations=[], generation_paths=[], usage=None,
                    usage_status='generation_not_run; embedding_usage_shared_if_reported; reranker_tokens_not_reported',
                    provider_calls=[], compute_timings=timings, model_name=None,
                    retrieval_compute_seconds=sum(t['seconds'] for t in timings),
                    request_wall_seconds=time.monotonic() - wall,
                    embedding_source='none' if arm == 'Graph-only' else 'shared frozen query vector',
                    execution_config=current)
                row['metrics'] = support_metrics([r['chunk_id'] for r in row['ranked']],
                    [e['chunk_id'] for e in row['evidence']], [bench['units'][u] for u in case['units']])
                selected_papers = {e['paper_id'] for e in row['evidence']}
                required = set(case['source_papers'])
                row['source_metrics'] = dict(required_paper_coverage=len(required & selected_papers) / len(required) if required else None,
                    all_required_papers=required <= selected_papers if required else None)
                from .relation_holdout_report import pool_coverage
                row['source_metrics']['candidate_pool_coverage40'] = pool_coverage(row, case, bench)
                row['diagnosis'] = diagnose(row, case, bench, workflow.chunk_map, graph)
                row['criterion_source_coverage'] = criterion_source_coverage(dict(assessment=dict(criteria=case['reference_criteria'])),
                    [e['chunk_id'] for e in row['evidence']], bench['units'])
                row['stage_timings'] = [dict(r) for r in workflow.audit.conn.execute(
                    'SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started', (rid,))]
                workflow.audit.finish(rid, row)
                row['trace_id'] = workflow.audit.live_requests[rid]
                row['trace_url'] = workflow.audit.live.url(row['trace_id'])
                row['finished'] = now()
                write_json(folder / f'{case["id"]}-{arm}.json', row)
                summary['results'].append(row)
                write_json(folder / 'summary.json', summary)
                print(json.dumps(dict(case=case['id'], arm=arm, status=row['status'],
                    candidates=len(row['ranked']), recall5=row['metrics']['recall5'],
                    coverage=row['metrics']['evidence_coverage'], errors=row['errors']), ensure_ascii=False), flush=True)
                if row['status'] == 'error':
                    raise RuntimeError('declared_retrieval_configuration_failed')
        if contract(root, bench, cfg) != current or sha(graph.path) != graph.sha256:
            raise RuntimeError('frozen_execution_changed')
        summary.update(status='completed', finished=now())
    except BaseException as exc:
        summary.update(status='interrupted', error_type=type(exc).__name__, finished=now())
        raise
    finally:
        write_json(folder / 'summary.json', summary)
        try:
            summary['trace_verification'] = verify_traces(workflow.audit.live, root_ids)
            if not summary['trace_verification']['verified']:
                raise ValueError('live_trace_readback_incomplete')
            hydrate_trace_urls(recorder.connect(), summary, folder)
            write_json(folder / 'summary.json', summary)
            summary['verification'] = verify(recorder, summary, folder)
            if summary['results']:
                summary['dataset_sync'] = recorder.sync_run(folder / 'summary.json')
        except Exception as exc:
            summary['dataset_sync'] = dict(status='pending_sync', error_type=type(exc).__name__)
        write_json(folder / 'summary.json', summary)
        make_report(recorder, summary, folder)
        write_json(folder.parent.parent / 'latest.json', dict(directory=str(folder), status=summary['status']))
        recorder.close()
        workflow.close()
        graph.close()
        close_workers()
        print(json.dumps(dict(status=summary['status'], directory=str(folder),
            sync=summary.get('dataset_sync'), traces=summary.get('trace_verification')), ensure_ascii=False), flush=True)


def verify_traces(live, root_ids):
    live.flush(limit=10000)
    rows = [dict(r) for r in live.conn.execute('SELECT id,parent_id,finished FROM spans')]
    ids = set(root_ids)
    while True:
        grown = ids | {r['id'] for r in rows if r['parent_id'] in ids}
        if grown == ids:
            break
        ids = grown
    found = {}
    for offset in range(0, len(ids), 50):
        batch = sorted(ids)[offset:offset + 50]
        found.update({str(r.id): r for r in live.client.list_runs(run_ids=batch, limit=len(batch), select=['id', 'end_time', 'parent_run_id'])})
    pending = sum(r[0] in ids for r in live.conn.execute("SELECT span_id FROM events WHERE status='pending'"))
    return dict(verified=set(found) == ids and all(r.end_time for r in found.values()) and not pending,
        expected_spans=len(ids), verified_spans=len(found), roots=len(root_ids), pending_events=pending)


def hydrate_trace_urls(client, summary, folder):
    rows = summary['results']
    ids = [r['trace_id'] for r in rows]
    found = {}
    for offset in range(0, len(ids), 50):
        found.update({str(r.id): r for r in client.list_runs(run_ids=ids[offset:offset + 50], limit=50)})
    if set(ids) != set(found) or any(not r.end_time for r in found.values()):
        raise ValueError('result_trace_readback_incomplete')
    for row in rows:
        row['trace_url'] = client.get_run_url(run=found[row['trace_id']])
        if not row['trace_url']:
            raise ValueError('result_trace_url_missing')
        write_json(folder / f"{row['case_id']}-{row['arm']}.json", row)
