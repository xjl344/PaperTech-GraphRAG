"""Per-question evaluation records; legacy v1 export remains unchanged.

This exporter adds source excerpts and all recorded question-level results to the
LangSmith examples/experiments. PDFs, embeddings and raw HTTP payloads stay local.
It does not change the frozen questions, reference facts or retrieval workflow.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time

from .audit import redact
from .corpus import load_corpus
from .evaluation_datasets import (EvaluationDataset, METRICS, POLICY, output_payload,
    run_payloads, stable_id, write_json)

PROFILE = 'per-question-details-v1'
ARMS = ('Hybrid', 'Hybrid+Graph')
SOURCE_FIELDS = ('chunk_id', 'paper_id', 'parse_id', 'title', 'source_relative_path',
    'page_start', 'page_end', 'source_spans', 'text_sha256', 'section', 'text')
FORBIDDEN = {'raw', 'raw_response', 'embedding', 'embeddings', 'vector', 'vectors',
    'headers', 'authorization', 'api_key', 'password'}


def recorded_usage_payload(parent, call, parent_order):
    """Import one actual provider call as an LLM child, without replaying it.

    LangSmith aggregates native chain tokens from LLM children. Token fields on
    the chain create payload alone do not populate the native Experiment column.
    """
    usage = call.get('usage')
    if isinstance(usage, str):
        usage = json.loads(usage)
    if not usage or usage.get('prompt_tokens') is None or usage.get('completion_tokens') is None:
        return None
    if not call.get('started') or not call.get('finished'):
        raise ValueError('recorded_usage_timestamps_missing')
    start, end = map(datetime.fromisoformat, (call['started'], call['finished']))
    rid = stable_id(parent['id'], 'recorded_generation', call['id'])
    native = dict(input_tokens=usage['prompt_tokens'], output_tokens=usage['completion_tokens'],
        total_tokens=usage['prompt_tokens'] + usage['completion_tokens'])
    return dict(id=rid, name='recorded-generation-usage', run_type='llm',
        parent_run_id=parent['id'], trace_id=parent['id'],
        dotted_order=parent_order + '.' + start.strftime('%Y%m%dT%H%M%S%fZ') + rid,
        start_time=start, end_time=end, inputs={},
        outputs=dict(usage_metadata=native, status=call['status']),
        extra=dict(metadata=dict(usage_metadata=native, capture_mode='evaluation_result_import',
            source_call_id=call['id'])))


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if key.casefold() not in FORBIDDEN}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value


def source_detail(chunk):
    return {key: deepcopy(chunk[key]) for key in SOURCE_FIELDS if key in chunk}


def enrich_examples(payload, bench, chunks):
    """Add display fields without changing any existing frozen reference field."""
    payload = deepcopy(payload)
    cases = {case['id']: case for case in bench['cases']}
    for example in payload['examples']:
        case = cases[example['metadata']['case_id']]
        facts, source_ids = [], []
        for key in case['units']:
            unit = bench['units'][key]
            facts.append(dict(unit_id=key, required_fact=unit['answer_point'],
                primary_chunk=unit['primary_chunk'], supporting_chunks=unit['known_support_chunks'],
                coverage_rule='本事实的任一已核查支持来源即可；不同必要事实必须全部覆盖。'))
            source_ids.extend(unit['known_support_chunks'])
        example['outputs'].update(case_id=case['id'], category=case['category'],
            required_facts=facts,
            source_evidence=[source_detail(chunks[cid]) for cid in dict.fromkeys(source_ids)],
            required_source_papers=case['source_papers'], min_source_papers=case['min_source_papers'],
            relation_review=case.get('relation_review') or dict(
                evidence='核对全部必要事实、引用与原文；没有来源时不得补造。',
                semantics='核对关系方向、实体角色、任务/实验条件和题干前提。',
                uncertainty='必要证据不足时明确说明缺口；反例允许纠正前提。'),
            scoring_rules=deepcopy(bench['scoring']),
            evaluation_config=dict(generate=case['generate'],
                planned_output='完整模型回答与引用' if case['generate'] else '仅检索与证据评估（原冻结方案）',
                controls=deepcopy(bench['controls']), models=deepcopy(bench['models'])),
            result_display=dict(location='本题关联的 Hybrid / Hybrid+Graph Experiment runs',
                fields=['完整回答', '全部重排候选与分数', '入选原文与引用位置', '全部图路径与生成采用路径',
                    '逐事实覆盖/缺口', '逐阶段耗时', 'Token 与调用状态', '两组证据及指标差异', '原始 Trace 链接'],
                semantic_review='自动覆盖分数不是答案正确性；语义判读单独标注。'))
        example['metadata'].update(detail_profile=PROFILE,
            content_scope='逐题参考事实、原文证据和位置、关系判读、评分与运行配置；实际结果关联 Experiment。')
        if case.get('assessment'):
            # Reference-only fields: never passed to retrieval or generation.
            example['outputs'].update(assessment=deepcopy(case['assessment']),
                expected_graph_paths={key: deepcopy(bench['paths_by_unit'][key]) for key in case['units']},
                graph_snapshot=deepcopy(bench['graph_snapshot']))
        if bench.get('comparison', {}).get('mode') == 'frozen_candidate_evidence_replay':
            example['outputs']['evaluation_config'].update(generate=False,
                parent_generate=case['generate'], planned_output='固定旧候选的证据选择回放；不生成新回答。',
                comparison=deepcopy(bench['comparison']))
            example['outputs']['result_display'].update(location='本题关联的 Graph-before / Graph-after Experiment runs',
                fields=['全部冻结候选与分数', '入选原文与位置', '来源保留与缺口', '逐事实覆盖', '图路径',
                    '证据组装耗时', '历史回答、引用、Token 与 Trace（明确为父运行）'])
            example['metadata']['selection_reason'] = deepcopy(bench['selection']['reasons'][case['id']])
    payload['description'] = '40 题逐题详细记录：参考答案、必要事实、原文及位置、关系与评分要求；实际两组详细结果关联到每个 Example。'
    if bench.get('comparison', {}).get('mode') == 'frozen_candidate_evidence_replay':
        payload['description'] = f"{len(bench['cases'])} 道旧 Graph 缺来源题的诊断子集；固定候选做来源保留前后对照，无新模型生成，不作为总体质量估计。"
    payload['metadata'].update(detail_profile=PROFILE,
        capture_scope='Per-question reference evidence excerpts and locations; full recorded result fields in linked experiments. No PDFs, vectors or raw HTTP payloads.')
    if bench.get('graph_snapshot'):
        payload['description'] = bench['dataset_description']
        payload['metadata'].update(graph_snapshot=deepcopy(bench['graph_snapshot']), no_model_comparison_run=True)
    return payload


def detailed_output(row, case, bench, chunks):
    output = output_payload(row, 'full')
    output.update(detail_profile=PROFILE, case_id=case['id'], category=case['category'], arm=row['arm'])
    for key in ('question', 'order', 'generate_requested', 'evidence', 'citations', 'graph_paths',
            'generation_paths', 'limitations', 'retrieval_summary', 'compute_timings', 'stage_timings', 'embedding_source'):
        output[key] = deepcopy(row.get(key))
    if row.get('execution_config'):
        output['execution_config'] = deepcopy(row['execution_config'])
    for key in ('candidate_channels', 'criterion_source_coverage'):
        if key in row:
            output[key] = deepcopy(row[key])
    if row.get('raw'):
        # Keep answer content, not the supplier response envelope or headers.
        try:
            draft = json.loads(row['raw'])
            if isinstance(draft, dict) and isinstance(draft.get('answer'), str):
                output['generated_answer_draft'] = dict(answer=draft['answer'],
                    validation_status=row['status'], note='模型回答草稿；是否通过引用校验以 validation_status 为准。')
        except (ValueError, TypeError):
            pass
    output['ranked_candidates'] = []
    for rank, candidate in enumerate(row.get('ranked') or [], 1):
        cid = candidate['chunk_id']
        output['ranked_candidates'].append(dict(rank=rank,
            **{key: deepcopy(candidate[key]) for key in ('chunk_id', 'score', 'sources', 'rerank_score') if key in candidate},
            source=source_detail(chunks[cid])))
    output['provider_calls'] = [{key: deepcopy(call.get(key)) for key in
        ('provider', 'attempt', 'status', 'http_status', 'seconds', 'usage')}
        for call in row.get('provider_calls') or []]
    ranked = {candidate['chunk_id']: index for index, candidate in enumerate(row.get('ranked') or [], 1)}
    selected = {e['chunk_id'] for e in row.get('evidence') or []}
    coverage = []
    for key in case['units']:
        unit = bench['units'][key]
        pool = set(unit['known_support_chunks'])
        coverage.append(dict(unit_id=key, required_fact=unit['answer_point'],
            ranked_matches=[dict(chunk_id=cid, rank=ranked[cid]) for cid in ranked if cid in pool],
            selected_matches=sorted(selected & pool), selected_covered=bool(selected & pool)))
    output['fact_coverage'] = coverage
    output['missing_required_facts'] = [item['unit_id'] for item in coverage if not item['selected_covered']]
    output['semantic_review'] = dict(status='not_reviewed',
        note='以上是已冻结支持池的 ID 覆盖；仍需原文判断完整回答和关系是否受支持。')
    return redact(clean(output))


def paired_comparisons(summary):
    pairs = {}
    for row in summary['results']:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    comparisons = {}
    for case_id, rows in pairs.items():
        if set(rows) != set(ARMS):
            comparisons[case_id] = dict(status='incomplete_pair', available_arms=sorted(rows))
            continue
        hybrid, graph = rows['Hybrid'], rows['Hybrid+Graph']
        h = {e['chunk_id'] for e in hybrid.get('evidence') or []}
        g = {e['chunk_id'] for e in graph.get('evidence') or []}
        differences = {}
        for key in METRICS:
            a, b = hybrid['metrics'].get(key), graph['metrics'].get(key)
            differences[key] = b - a if a is not None and b is not None else None
        comparisons[case_id] = dict(status='paired', graph_minus_hybrid=differences,
            hybrid_status=hybrid['status'], graph_status=graph['status'],
            shared_evidence=sorted(h & g), graph_added_evidence=sorted(g - h), graph_removed_evidence=sorted(h - g),
            interpretation='此处为客观记录差异，不自动判定关系正确性或图扩展优越。')
    return comparisons


class DetailedEvaluationDataset(EvaluationDataset):
    def __init__(self, root, version, client=None, allow_enrichment=False):
        super().__init__(root, version, client)
        self.baseline = deepcopy(self.payload)
        self.allow_enrichment = allow_enrichment
        corpus, _, chunks = load_corpus(self.root)
        if corpus != self.bench['corpus_id']:
            raise ValueError('detail_corpus_changed')
        self.chunks = {chunk['chunk_id']: chunk for chunk in chunks}
        self.payload = enrich_examples(self.baseline, self.bench, self.chunks)
        self.status['detail_profile'] = PROFILE
        write_json(self.directory / 'langsmith-dataset.json', self.payload)
        for example in self.payload['examples']:
            write_json(self.directory / 'cases' / (example['metadata']['case_id'] + '.json'), example)
        write_json(self.directory / 'detail-contract.json', dict(detail_profile=PROFILE,
            benchmark_sha256=self.digest, exporter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            authorization='2026-11-15 用户明确要求本轮 40 道题的逐题详细信息均显示在数据集中；旧 v1 不变。',
            examples_sha256=hashlib.sha256(json.dumps(self.payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()))

    def sync_dataset(self):
        client = self.connect()
        matches = list(client.list_datasets(dataset_name=self.payload['name']))
        if matches:
            dataset = matches[0]
            if (dataset.metadata or {}).get('benchmark_sha256') != self.digest:
                raise ValueError('remote_dataset_version_conflict')
            baseline = {e['id']: e for e in self.baseline['examples']}
            expected = {e['id']: e for e in self.payload['examples']}
            upgrades = []
            for remote in client.list_examples(dataset_id=dataset.id):
                eid = str(remote.id)
                if eid not in expected or remote.inputs != expected[eid]['inputs']:
                    raise ValueError('remote_example_modified')
                if remote.outputs == expected[eid]['outputs']:
                    continue
                # Explicit additive migration only: inputs and prior gold must match exactly.
                if not self.allow_enrichment or remote.outputs != baseline[eid]['outputs']:
                    raise ValueError('detail_enrichment_required_or_remote_modified')
                upgrades.append(expected[eid])
            def upgrade(example):
                client.update_example(example_id=example['id'], outputs=example['outputs'],
                    metadata=example['metadata'], split=example['split'])
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upgrade, upgrades))
        dataset = super().sync_dataset()
        remote = list(client.list_examples(dataset_id=dataset.id))
        details_verified = sum((example.metadata or {}).get('detail_profile') == PROFILE and
            all(key in example.outputs for key in ('required_facts', 'source_evidence', 'relation_review',
                'scoring_rules', 'evaluation_config', 'result_display')) for example in remote)
        if details_verified != len(self.payload['examples']):
            raise ValueError('per_question_details_incomplete')
        self.status.update(detail_examples_verified=details_verified,
            source_excerpts_verified=sum(len(e.outputs['source_evidence']) for e in remote),
            result_status='reference_details_ready; actual results available only after evaluation')
        write_json(self.status_path, self.status)
        return dataset

    def sync_generation_usage(self, expected, parents, project_name):
        children = []
        ledger = self.root / 'data/rag.sqlite3'
        recorded_known_calls = sum(bool(call.get('usage')) for payload in expected.values()
            for call in payload['outputs'].get('provider_calls') or [])
        if ledger.exists():
            with sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True) as conn:
                conn.row_factory = sqlite3.Row
                for rid, payload in expected.items():
                    request_id = payload['extra']['metadata']['request_id']
                    for call in conn.execute('SELECT * FROM calls WHERE request_id=? ORDER BY started', (request_id,)):
                        child = recorded_usage_payload(payload, dict(call), parents[rid].dotted_order)
                        if child is not None:
                            children.append(child)
        if len(children) != recorded_known_calls:
            raise ValueError('recorded_generation_usage_ledger_incomplete')
        client = self.client
        wanted = {child['id']: child for child in children}
        if not wanted:
            return dict(known_usage_calls=0, verified=0)
        def read_children():
            found = {}
            ids = list(wanted)
            for offset in range(0, len(ids), 50):
                batch = ids[offset:offset + 50]
                found.update({str(run.id): run for run in client.list_runs(run_ids=batch, limit=len(batch),
                    select=['id', 'parent_run_id', 'outputs', 'start_time', 'end_time', 'prompt_tokens', 'completion_tokens'])})
            return found
        existing = read_children()
        def upload(child):
            client.create_run(project_name=project_name, **child)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(upload, [child for rid, child in wanted.items() if rid not in existing]))
        for attempt in range(5):
            found = read_children()
            if set(found) == set(wanted) and all(run.outputs == wanted[rid]['outputs'] and
                    str(run.parent_run_id) == wanted[rid]['parent_run_id'] and
                    run.start_time == wanted[rid]['start_time'] and run.end_time == wanted[rid]['end_time'] and
                    run.prompt_tokens == wanted[rid]['outputs']['usage_metadata']['input_tokens'] and
                    run.completion_tokens == wanted[rid]['outputs']['usage_metadata']['output_tokens']
                    for rid, run in found.items()):
                return dict(known_usage_calls=len(wanted), verified=len(found))
            if attempt < 4:
                time.sleep(2)
        raise ValueError('recorded_generation_usage_readback_mismatch')

    def sync_run(self, summary_path, answer_mode='full'):
        if answer_mode != 'full':
            raise ValueError('detailed_benchmark_requires_full_results')
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        payloads = run_payloads(self.bench, self.digest, summary, 'full')
        cases = {case['id']: case for case in self.bench['cases']}
        rows = {(row['case_id'], row['arm']): row for row in summary['results']}
        comparisons = paired_comparisons(summary)
        for payload in payloads:
            meta = payload['extra']['metadata']
            case_id, arm = meta['case_id'], meta['arm']
            payload['outputs'] = detailed_output(rows[case_id, arm], cases[case_id], self.bench, self.chunks)
            payload['outputs']['paired_comparison'] = comparisons[case_id]
            meta['detail_profile'] = PROFILE
            # Native Experiment latency must use the actual request ledger,
            # rather than the zero-duration historical import placeholder.
            ledger = self.root / 'data/rag.sqlite3'
            if ledger.exists():
                with sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True) as connection:
                    timing = connection.execute('SELECT started,finished FROM requests WHERE id=?',
                        (rows[case_id, arm]['request_id'],)).fetchone()
                if timing and timing[0] and timing[1]:
                    payload['start_time'], payload['end_time'] = map(datetime.fromisoformat, timing)
                    payload['outputs']['request_wall_seconds'] = (payload['end_time'] - payload['start_time']).total_seconds()
                    meta['timing_note'] = 'Actual request ledger timestamps; includes live tracing overhead, excludes shared batch embedding and warmup.'
            usage = rows[case_id, arm].get('usage')
            if usage and usage.get('prompt_tokens') is not None and usage.get('completion_tokens') is not None:
                payload.update(prompt_tokens=usage['prompt_tokens'], completion_tokens=usage['completion_tokens'],
                    total_tokens=usage['prompt_tokens'] + usage['completion_tokens'])
            payload['_metrics'].update(retrieval_compute_seconds=rows[case_id, arm].get('retrieval_compute_seconds'),
                request_wall_seconds=payload['outputs'].get('request_wall_seconds'),
                evidence_count=len(rows[case_id, arm].get('evidence') or []),
                generation_path_count=len(rows[case_id, arm].get('generation_paths') or []))
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(
            benchmark=self.bench['version'], benchmark_sha256=self.digest, detail_profile=PROFILE,
            runs=json.loads(json.dumps(payloads, default=str))))
        write_json(summary_path.parent / 'per-question-comparison.json', comparisons)
        dataset = self.sync_dataset()
        client, experiments = self.client, []
        for arm in ARMS:
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='逐题完整结果：回答、候选、证据、引用、路径、阶段耗时、Token 与两组差异。',
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
                            comment='支持池 ID 覆盖指标；逐事实来源见 outputs.fact_coverage，不代表语义正确率。'))
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


def dataset_recorder(root, version, **kwargs):
    if version == 'benchmark-holdout-v1':
        from .holdout_evaluation import HoldoutDataset
        return HoldoutDataset(root, version, **kwargs)
    if version == 'benchmark-v5-final-v1':
        from .p5_final_evaluation import P5FinalDataset
        return P5FinalDataset(root, version, **kwargs)
    if version in ('benchmark-v5-rerank-diversity-v1', 'benchmark-v5-rerank-diversity-v2'):
        from .p4_offline_evaluation import P4OfflineDataset
        return P4OfflineDataset(root, version, **kwargs)
    if version == 'benchmark-v5-graph-v1':
        from .p3_evaluation import P3Dataset
        return P3Dataset(root, version, **kwargs)
    if version == 'benchmark-v4-planner-v1':
        from .p2_evaluation import P2Dataset
        return P2Dataset(root, version, **kwargs)
    if version in ('benchmark-v4-p0-v1', 'benchmark-v4-p0-v2'):
        from .p0_evaluation import P0Dataset
        return P0Dataset(root, version, **kwargs)
    if version == 'benchmark-subquery-recall-router-fix-v1':
        from .router_fix_recall import RouterFixRecallDataset
        return RouterFixRecallDataset(root, version, **kwargs)
    if version == 'benchmark-subquery-rerank-clean-v1':
        from .subquery_rerank_clean_diagnostic import CleanRerankDataset
        return CleanRerankDataset(root, version, **kwargs)
    if version == 'benchmark-subquery-recall-policy-v1':
        from .subquery_recall_policy import PolicyDataset
        return PolicyDataset(root, version, **kwargs)
    if version == 'benchmark-subquery-recall-v1':
        from .subquery_recall_diagnostic import RecallDataset
        return RecallDataset(root, version, **kwargs)
    if version in ('benchmark-query-router-v1','benchmark-query-router-fix-v1'):
        from .query_router_diagnostic import RouterDataset
        return RouterDataset(root, version, **kwargs)
    if version in ('benchmark-subquery-quality-v1','benchmark-subquery-quality-v2'):
        from .subquery_diagnostic import SubqueryDataset
        return SubqueryDataset(root, version, **kwargs)
    if version in ('benchmark-recall-width-v1','benchmark-resource-selection-v1','benchmark-recall-intervention-v1'):
        from .staged_retrieval_diagnostics import StagedDataset
        return StagedDataset(root, version, **kwargs)
    if version == 'benchmark-rerank-window-v1':
        from .rerank_window_diagnostic import DiagnosticDataset
        return DiagnosticDataset(root, version, **kwargs)
    if version == 'benchmark-relation-holdout-v1':
        from .relation_holdout_evaluation import RetrievalDataset
        return RetrievalDataset(root, version, **kwargs)
    if version == 'benchmark-retrieval-v1':
        from .retrieval_comparison import RetrievalDataset
        return RetrievalDataset(root, version, **kwargs)
    if version == 'benchmark-v1':
        kwargs.pop('allow_enrichment', None)
        return EvaluationDataset(root, version, **kwargs)
    return DetailedEvaluationDataset(root, version, **kwargs)


def result_mode(root, version):
    if version == 'benchmark-v1':
        policy = json.loads((root / POLICY).read_text(encoding='utf-8'))
        return policy.get('version_overrides', {}).get(version, {}).get('answer_mode', 'summary')
    return 'full'
