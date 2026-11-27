"""Versioned LangSmith datasets and paired experiments, with local replay artifacts.

Only question text is an input. Reference answers stay in reference outputs, never
in production model inputs. Source PDFs, source chunks, vectors and raw responses
are excluded. Generated answer text is opt-in under the project's dataset policy.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import uuid

from .audit import redact
from .settings import settings

NAMESPACE = uuid.UUID('32c1d04b-2a7a-4eb0-aac2-90bf90a0ae3b')
POLICY = 'artifacts/eval/dataset-policy.json'
METRICS = ('recall5', 'recall8', 'mrr40', 'evidence_coverage', 'all_units')


def stable_id(*parts):
    return str(uuid.uuid5(NAMESPACE, '/'.join(str(p) for p in parts)))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def load_benchmark(root, version):
    if not version.startswith('benchmark-') or Path(version).name != version:
        raise ValueError('invalid_benchmark_version')
    directory = root / 'artifacts/eval/stage-4' / version
    raw = (directory / 'benchmark.json').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != (directory / 'benchmark.sha256').read_text().strip():
        raise ValueError('benchmark_modified')
    bench = json.loads(raw)
    if bench['version'] != version:
        raise ValueError('benchmark_version_mismatch')
    return bench, digest, directory


def dataset_payload(bench, digest):
    examples = []
    for case in bench['cases']:
        references = []
        for key in case['units']:
            unit = bench['units'][key]
            references.append(dict(unit_id=key, answer_point=unit['answer_point'],
                paper_id=unit['paper_id'], title=unit['title'],
                primary_chunk=unit['primary_chunk'], pages=[unit['page_start'], unit['page_end']],
                known_support_chunks=unit['known_support_chunks']))
        examples.append(dict(id=stable_id(digest, case['id']), inputs=dict(question=case['question']),
            outputs=dict(expected_answer=case.get('expected_answer') or '\n'.join(r['answer_point'] for r in references),
                answerable=case['answerable'], negative_kind=case['negative_kind'],
                source_references=references, relation_outline=case.get('reasoning_chain'),
                must_not_claim=case.get('must_not_claim')),
            metadata=dict(case_id=case['id'], category=case['category'], benchmark=bench['version'],
                benchmark_sha256=digest, corpus_id=bench['corpus_id'],
                review_origin='Codex delegated source review; not independent human scoring'),
            split=[case['category']]))
    return dict(name='papertech-stage4-' + bench['version'],
        description='论文 RAG 开发集；参考来源有限、非独立金标。两组共用题目和预算；不预设 Graph 胜出。',
        metadata=dict(benchmark=bench['version'], benchmark_sha256=digest,
            capture_scope='questions, paraphrased reference points and source IDs; no source text or vectors',
            prior_exposure=bench.get('prior_exposure'), scoring=bench['scoring']), examples=examples)


def output_payload(row, answer_mode):
    if answer_mode not in ('summary', 'full'):
        raise ValueError('invalid_answer_mode')
    output = {k: row.get(k) for k in ('status', 'metrics', 'retrieval_compute_seconds', 'usage',
        'model_name', 'errors', 'trace_url')}
    output['selected_chunk_ids'] = [e['chunk_id'] for e in row.get('evidence', [])]
    output['citation_chunk_ids'] = [e['chunk_id'] for e in row.get('citations', [])]
    output['graph_path_count'] = len(row.get('graph_paths') or [])
    output['generation_path_count'] = len(row.get('generation_paths') or [])
    output['answer_capture'] = answer_mode
    output['answer_local_file'] = row['case_id'] + ('-graph.json' if row['arm'] == 'Hybrid+Graph' else '-hybrid.json')
    if answer_mode == 'full':
        output['answer'] = row.get('answer')
    else:
        output['answer_summary'] = '完整回答保存在本地逐题 JSON；此实验输出显示状态、检索覆盖、来源 ID 和时延。'
    return redact(output)


def run_payloads(bench, digest, summary, answer_mode):
    if summary['benchmark_sha256'] != digest or summary['benchmark'] != bench['version']:
        raise ValueError('run_benchmark_mismatch')
    cases = {c['id']: c for c in bench['cases']}
    seen, payloads = set(), []
    started = datetime.fromisoformat(summary['started'])
    for index, row in enumerate(summary['results']):
        case_id, arm = row['case_id'], row['arm']
        case = cases[case_id]
        if arm not in ('Hybrid', 'Hybrid+Graph') or (case_id, arm) in seen:
            raise ValueError('duplicate_or_invalid_experiment_row')
        if row['question'] != case['question'] or row['category'] != case['category']:
            raise ValueError('run_case_mismatch')
        seen.add((case_id, arm))
        run_id = stable_id(digest, summary['run_id'], case_id, arm)
        # Historical imports must not impersonate original live span timings.
        timestamp = started + timedelta(microseconds=index)
        metrics = {k: row['metrics'].get(k) for k in METRICS if case['category'] != 'negative'}
        payloads.append(dict(id=run_id, name='stage4-paired-evaluation', run_type='chain',
            inputs=dict(question=case['question']), outputs=output_payload(row, answer_mode),
            reference_example_id=stable_id(digest, case_id),
            start_time=timestamp, end_time=timestamp,
            extra=dict(metadata=dict(benchmark=bench['version'], benchmark_sha256=digest,
                original_run_id=summary['run_id'], request_id=row['request_id'], case_id=case_id,
                arm=arm, capture_mode='evaluation_result_import',
                timing_note='Original retrieval duration is outputs.retrieval_compute_seconds; span duration is not the original request latency.')),
            tags=[bench['version'], arm, case['category']],
            _arm=arm, _metrics=metrics))
    if summary['status'] == 'completed' and len(seen) != len(cases) * 2:
        raise ValueError('completed_run_missing_pairs')
    return payloads


class EvaluationDataset:
    def __init__(self, root, version, client=None):
        self.root = Path(root)
        self.bench, self.digest, self.directory = load_benchmark(self.root, version)
        self.payload = dataset_payload(self.bench, self.digest)
        self.client = client
        self.owns_client = client is None
        self.status_path = self.directory / 'langsmith-status.json'
        self.status = dict(benchmark=version, benchmark_sha256=self.digest,
            dataset_name=self.payload['name'], examples_expected=len(self.payload['examples']), status='local_ready')
        write_json(self.directory / 'langsmith-dataset.json', self.payload)

    def connect(self):
        if self.client is None:
            from langsmith import Client
            cfg = settings(self.root)
            if not cfg.get('LANGSMITH_API_KEY'):
                raise ValueError('langsmith_not_configured')
            self.client = Client(api_key=cfg['LANGSMITH_API_KEY'],
                api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                timeout_ms=20000, auto_batch_tracing=False)
        return self.client

    def sync_dataset(self):
        client = self.connect()
        matches = list(client.list_datasets(dataset_name=self.payload['name']))
        if matches:
            dataset = matches[0]
            if (dataset.metadata or {}).get('benchmark_sha256') != self.digest:
                raise ValueError('remote_dataset_version_conflict')
        else:
            dataset = client.create_dataset(self.payload['name'], description=self.payload['description'],
                metadata=self.payload['metadata'])
        expected = {e['id']: e for e in self.payload['examples']}
        existing = {str(e.id): e for e in client.list_examples(dataset_id=dataset.id)}
        if set(existing) - set(expected):
            raise ValueError('unexpected_remote_examples')
        for eid, example in existing.items():
            if example.inputs != expected[eid]['inputs'] or example.outputs != expected[eid]['outputs']:
                raise ValueError('remote_example_modified')
        missing = [dict(id=eid, inputs=e['inputs'], reference_outputs=e['outputs'],
            metadata=e['metadata'], split=e['split']) for eid, e in expected.items() if eid not in existing]
        if missing:
            client.create_examples(dataset_id=dataset.id, examples=missing)
        verified = {str(e.id): e for e in client.list_examples(dataset_id=dataset.id)}
        if set(verified) != set(expected) or any(e.inputs != expected[eid]['inputs'] or
                e.outputs != expected[eid]['outputs'] for eid, e in verified.items()):
            raise ValueError('dataset_readback_mismatch')
        self.status.update(status='dataset_verified', dataset_id=str(dataset.id),
            dataset_url=dataset.url, examples_verified=len(verified))
        write_json(self.status_path, self.status)
        return dataset

    def sync_run(self, summary_path, answer_mode='summary'):
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        payloads = run_payloads(self.bench, self.digest, summary, answer_mode)
        notes_path = self.directory / 'review-notes.json'
        if notes_path.exists():
            notes = json.loads(notes_path.read_text(encoding='utf-8'))
            for payload in payloads:
                meta = payload['extra']['metadata']
                note = notes['cases'].get(meta['case_id'], {}).get(meta['arm'])
                if note:
                    payload['outputs']['source_review'] = dict(origin=notes['review_origin'], note=note)
        export_path = summary_path.parent / 'langsmith-experiments.json'
        # Save a replay artifact before attempting remote writes; no model replay needed.
        export = dict(benchmark=self.bench['version'], benchmark_sha256=self.digest,
            original_run_id=summary['run_id'], answer_mode=answer_mode,
            runs=json.loads(json.dumps(payloads, default=str)))
        write_json(export_path, export)
        dataset = self.sync_dataset()
        client = self.client
        experiments = []
        for arm in ('Hybrid', 'Hybrid+Graph'):
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='历史/本地结果导入，按 reference_example_id 配对；不重跑模型。',
                metadata=dict(benchmark_sha256=self.digest, original_run_id=summary['run_id'], arm=arm,
                    answer_capture=answer_mode, original_status=summary['status']))
            rows = [p for p in payloads if p['_arm'] == arm]
            existing = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            expected = {p['id']: p for p in rows}
            if set(existing) - set(expected):
                raise ValueError('unexpected_experiment_runs')
            for rid, remote in existing.items():
                if remote.outputs != expected[rid]['outputs'] or str(remote.reference_example_id) != expected[rid]['reference_example_id']:
                    raise ValueError('remote_experiment_modified')
            def upload_run(payload):
                fields = {k: v for k, v in payload.items() if not k.startswith('_')}
                client.create_run(project_name=name, **fields)
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upload_run, [p for p in rows if p['id'] not in existing]))
            # Deterministic feedback IDs allow retrying a partial import without duplicates.
            feedback = list(client.list_feedback(run_ids=list(expected))) if rows else []
            present = {str(f.id) for f in feedback}
            jobs = []
            for row in rows:
                for key, value in row['_metrics'].items():
                    fid = stable_id(row['id'], key)
                    if value is not None and fid not in present:
                        jobs.append(dict(run_id=row['id'], key=key, score=float(value), feedback_id=fid,
                            comment='Frozen support-unit metric; not answer correctness or independent semantic scoring.',
                            source_info=dict(benchmark_sha256=self.digest, original_run_id=summary['run_id']),
                            session_id=project.id, start_time=row['start_time'],
                            stop_after_attempt=1))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), jobs))
            remote_rows = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(remote_rows) != set(expected) or any(str(r.reference_example_id) != expected[rid]['reference_example_id'] or
                    r.outputs != expected[rid]['outputs'] for rid, r in remote_rows.items()):
                raise ValueError('experiment_readback_mismatch')
            expected_feedback = {stable_id(row['id'], key) for row in rows for key, value in row['_metrics'].items() if value is not None}
            remote_feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))} if rows else {}
            if not expected_feedback.issubset(remote_feedback):
                raise ValueError('feedback_readback_incomplete')
            for row in rows:
                for key, value in row['_metrics'].items():
                    if value is not None and not math.isclose(remote_feedback[stable_id(row['id'], key)].score,
                            float(value), rel_tol=0, abs_tol=0.000050001):
                        raise ValueError('feedback_score_mismatch')
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, name=name, project_id=str(project.id),
                runs_verified=len(remote_rows), feedback_verified=len(expected_feedback),
                feedback_precision='Remote feedback is rounded to 4 decimals; full precision remains in outputs.metrics and local results.',
                url=f"{dataset.url}/compare?selectedSessions={project.id}"))
        self.status.update(status='experiments_verified', experiments=experiments,
            original_run_id=summary['run_id'], answer_mode=answer_mode,
            comparison_url=f"{dataset.url}/compare?selectedSessions=" + ','.join(e['project_id'] for e in experiments))
        write_json(summary_path.parent / 'langsmith-status.json', self.status)
        write_json(self.status_path, self.status)
        return self.status

    def close(self):
        if self.client is not None and self.owns_client:
            self.client.close()


def answer_policy(root):
    path = root / POLICY
    policy = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return policy.get('answer_mode', 'summary')
