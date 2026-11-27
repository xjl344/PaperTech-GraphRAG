"""Re-rank the frozen expanded candidate unions after conservative subquery cleanup."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import html
import json
import math
from pathlib import Path
import time
import uuid

from .corpus import load_corpus
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, clean, source_detail
from .evidence_context import assemble
from .local_models import run_worker
from .settings import settings
from .subquery_diagnostic import sha
from .subquery_recall_diagnostic import read, score as coverage_score

VERSION = 'benchmark-subquery-rerank-clean-v1'
SOURCE_VERSION = 'benchmark-subquery-recall-policy-v1'
SOURCE_RUN = '436a8f4429df42c3b6fafe2c12216b5b'
SOURCE_BASE = Path('artifacts/reports/stage-4') / SOURCE_VERSION / 'runs' / SOURCE_RUN
ARMS = ('Owner-Clean', 'Original-Reused', 'Max-Original-Owner')
REMOVALS = ('各自', '各会', '分别', '各')


def clean_text(text):
    """Remove only shared interrogative scaffolding; preserve target words."""
    original = text
    removed = []
    for token in REMOVALS:
        if token in text:
            removed.extend([token] * text.count(token))
            text = text.replace(token, '')
    text = ' '.join(text.split())
    return dict(original=original, cleaned=text, removed=removed,
                changed=original != text, policy='remove_shared_question_scaffolding_v1')


def candidates_from_source(summary):
    by_case = {}
    for row in summary['results']:
        if row['arm'] == 'Rerank-Original-Union40':
            by_case[row['case_id']] = deepcopy(row['candidates'])
    if len(by_case) != 24:
        raise ValueError('expanded_union_candidates_missing')
    return by_case


def source_rows(candidates):
    rows = []
    for item in candidates:
        row = deepcopy(item)
        row['sources'] = deepcopy(item.get('discoveries', []))
        rows.append(row)
    return rows


def evidence_fact_coverage(evidence, case, units):
    selected = {e['chunk_id'] for e in evidence}
    facts = []
    for uid in case['units']:
        pool = set(units[uid]['known_support_chunks'])
        facts.append(dict(unit_id=uid, required_fact=units[uid]['answer_point'],
                          selected=bool(selected & pool), selected_chunk_ids=sorted(selected & pool)))
    return facts


def score_row(ranked, case, units, chunks):
    candidates = [dict(x, retained=i <= 40) for i, x in enumerate(ranked, 1)]
    metrics, facts = coverage_score(candidates, case, units, chunks)
    metrics['top40_coverage'] = metrics['cap40_coverage']
    metrics['top40_all'] = metrics['cap40_all']
    return candidates, metrics, facts


def freeze(root):
    folder = root / 'artifacts/eval/stage-4' / VERSION
    if (folder / 'benchmark.json').exists():
        return load_benchmark(root, VERSION)[0]
    parent, digest, _ = load_benchmark(root, SOURCE_VERSION)
    source_summary = root / SOURCE_BASE / 'summary.json'
    source_bench = root / 'artifacts/eval/stage-4' / SOURCE_VERSION / 'benchmark.json'
    if not source_summary.exists() or not source_bench.exists():
        raise ValueError('source_policy_run_missing')
    bench = deepcopy(parent)
    bench.update(version=VERSION, parent_benchmark_sha256=digest, source_run_id=SOURCE_RUN,
        arms=list(ARMS), comparison=dict(mode='clean_subquery_rerank_and_evidence', arms=list(ARMS), generation=False),
        dataset_description='24道已曝光跨论文开发题：清洗子查询文本后，比较owner/原问题/max融合重排并回放6000字节/8块证据选择。',
        prior_exposure='题目、来源、候选和前轮重排均已用于开发；本轮不是泛化验收。',
        controls=dict(candidate_source='frozen expanded full union from prior policy run; no retrieval or embedding',
            cleanup='remove only shared scaffolding tokens: 分别, 各, 各自, 各会; keep method names, technical terms and substantive interrogatives',
            owner='score each chunk against every cleaned subquery that discovered it; max owner score selects owner-only',
            original='reuse previous original-question score on the identical candidate and model',
            max_fusion='max(original reused score, cleaned owner score)',
            fallback='chunks discovered by no subquery use original score for owner and max',
            candidate_cap=40,reranker_max_pair_tokens=1024,reranker_batch_size=1,
            evidence_budget_bytes=6000,evidence_max=8,evidence_policy='existing assemble named_first; no graph paths',
            generation=False),
        scoring=dict(primary='necessary source coverage after Top40 rerank and after 6000-byte/8-block evidence selection',
            source='any known_support_chunks match',semantic='not assessed; no answer generation',
            pairing='Original-Reused control; report wins/ties/losses and source substitutions',
            costs='only cleaned owner rerank pairs are new; original scores are reused; evidence selection is deterministic'),
        source_inputs_sha256={str(SOURCE_BASE/'summary.json'):sha(source_summary),
            str(root / 'artifacts/eval/stage-4' / SOURCE_VERSION / 'benchmark.json'):sha(source_bench)},
        code_sha256={p:sha(root/p) for p in ('src/papertech/subquery_rerank_clean_diagnostic.py',
            'src/papertech/evidence_context.py','src/papertech/retrieval.py','src/papertech/rerank_runtime.py',
            'src/papertech/rerank_service.py','scripts/eval-stage4.py','src/papertech/evaluation_details.py')})
    write_json(folder / 'benchmark.json', bench)
    (folder / 'benchmark.sha256').write_text(sha(folder / 'benchmark.json') + '\n', encoding='utf8')
    for p in bench['code_sha256']:
        dest = folder / 'runtime-snapshot' / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((root / p).read_bytes())
    return bench


class CleanRerankDataset(DetailedEvaluationDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload['description'] = self.bench['dataset_description']
        for e in self.payload['examples']:
            e['outputs']['evaluation_config']['planned_output'] = '清洗子查询重排与6000字节/8块证据选择；不生成答案'
            e['outputs']['result_display'].update(location='Owner-Clean / Original-Reused / Max-Original-Owner Experiments',
                fields=['清洗前后子查询','三种分数及排名','Top40必要来源覆盖','6000字节/8块证据选择','R08.S02原文语义审计','成本与Trace'])
            write_json(self.directory / 'cases' / (e['metadata']['case_id'] + '.json'), e)
        write_json(self.directory / 'langsmith-dataset.json', self.payload)

    def sync_run(self, summary_path):
        summary = read(summary_path); path = Path(summary_path)
        if summary['benchmark_sha256'] != self.digest:
            raise ValueError('benchmark_mismatch')
        dataset = self.sync_dataset(); payloads = []
        expected = {(c['id'], arm) for c in self.bench['cases'] for arm in ARMS}
        keys = [(r['case_id'], r['arm']) for r in summary['results']]
        if summary['status'] == 'completed' and set(keys) != expected:
            raise ValueError('pair_set_mismatch')
        for row in summary['results']:
            out = clean(deepcopy(row))
            out['candidate_source_excerpts'] = [source_detail(self.chunks[x['chunk_id']]) for x in row.get('candidates', [])]
            out['ranked_source_excerpts'] = [source_detail(self.chunks[x['chunk_id']]) for x in row.get('ranked_candidates', [])]
            out['evidence_source_excerpts'] = [source_detail(self.chunks[x['chunk_id']]) for x in row.get('evidence', [])]
            out.update(generation='not_run', answer_accuracy='not_assessed')
            metrics = deepcopy(row['metrics'])
            metrics.update(rerank_pairs=row.get('compute', {}).get('pairs', 0),
                           rerank_seconds=row.get('compute', {}).get('inference_seconds', 0),
                           evidence_coverage=row['evidence_metrics']['coverage'],
                           evidence_blocks=len(row.get('evidence', [])))
            payloads.append(dict(id=stable_id(self.digest, summary['run_id'], row['case_id'], row['arm']),
                name='clean-subquery-rerank', run_type='chain', inputs=dict(question=row['question']), outputs=out,
                reference_example_id=stable_id(self.digest, row['case_id']), start_time=row['started'], end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=VERSION, arm=row['arm'], case_id=row['case_id'], source_run_id=SOURCE_RUN)),
                _arm=row['arm'], _metrics=metrics))
        write_json(path.parent / 'langsmith-experiments.json', dict(runs=payloads))
        experiments = []
        for arm in ARMS:
            group = {p['id']: p for p in payloads if p['_arm'] == arm}
            name = f'papertech-{VERSION}-{summary["run_id"][:12]}-{arm}'
            project = self.client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description=self.bench['dataset_description'], metadata=dict(arm=arm, benchmark_sha256=self.digest))
            found = {str(r.id): r for r in self.client.list_runs(project_id=project.id, is_root=True)}
            if set(found) - set(group) or any(r.outputs != group[rid]['outputs'] for rid, r in found.items()):
                raise ValueError('remote_modified')
            def upload(p):
                obj = {k: v for k, v in p.items() if not k.startswith('_')}
                obj['start_time'] = datetime.fromisoformat(obj['start_time']); obj['end_time'] = datetime.fromisoformat(obj['end_time'])
                self.client.create_run(project_name=name, **obj)
            with ThreadPoolExecutor(max_workers=3) as pool:
                list(pool.map(upload, [p for rid, p in group.items() if rid not in found]))
            jobs = [dict(run_id=p['id'], key=k, score=float(v), feedback_id=stable_id(p['id'], k), session_id=project.id,
                stop_after_attempt=1, comment='重排/证据来源覆盖和计算成本；不是答案准确率。')
                for p in group.values() for k, v in p['_metrics'].items()
                if isinstance(v, (int, float)) and math.isfinite(v)]
            existing = {str(f.id): f for f in self.client.list_feedback(run_ids=list(group))}
            with ThreadPoolExecutor(max_workers=3) as pool:
                list(pool.map(lambda j: self.client.create_feedback(**j), [j for j in jobs if j['feedback_id'] not in existing]))
            actual = {str(r.id): r for r in self.client.list_runs(project_id=project.id, is_root=True)}
            feedback = {str(f.id): f for f in self.client.list_feedback(run_ids=list(group))}
            if set(actual) != set(group) or any(r.outputs != group[rid]['outputs'] or str(r.reference_example_id) != group[rid]['reference_example_id'] for rid, r in actual.items()):
                raise ValueError('experiment_readback_mismatch')
            if any(j['feedback_id'] not in feedback or not math.isclose(feedback[j['feedback_id']].score, j['score'], abs_tol=.000051) for j in jobs):
                raise ValueError('feedback_readback_mismatch')
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(actual), feedback_verified=len(jobs)))
            self.client.update_project(project.id, end_time=datetime.now(timezone.utc))
        self.status.update(status='experiments_verified', experiments=experiments,
            result_status='completed', comparison_url=dataset.url + '/compare?selectedSessions=' + ','.join(x['project_id'] for x in experiments))
        write_json(path.parent / 'langsmith-status.json', self.status); write_json(self.status_path, self.status)
        return self.status


def paired(summary):
    grouped = {}
    for row in summary['results']: grouped.setdefault(row['case_id'], {})[row['arm']] = row
    output = {}
    control = 'Original-Reused'
    for cid, group in grouped.items():
        output[cid] = {}
        base = group.get(control)
        if not base: continue
        for arm, row in group.items():
            if arm == control: continue
            for metric in ('top40_coverage', 'evidence_metrics'):
                before = {f['unit_id'] for f in base['facts'] if f['retained']}
                if metric == 'top40_coverage':
                    after = {f['unit_id'] for f in row['facts'] if f['retained']}; a = row['metrics'][metric]; b = base['metrics'][metric]
                else:
                    after = {f['unit_id'] for f in row['evidence_facts'] if f['selected']}; a = row['evidence_metrics']['coverage']; b = base['evidence_metrics']['coverage']
                d = a - b
                output[cid].setdefault(arm, {})[metric] = dict(delta=d, outcome='win' if d > 1e-12 else 'loss' if d < -1e-12 else 'tie',
                    added=sorted(after - before), removed=sorted(before - after))
    return output


def aggregate(summary):
    result = {}
    for arm in ARMS:
        rows = [r for r in summary['results'] if r['arm'] == arm]
        result[arm] = dict(count=len(rows), top40_coverage=sum(r['metrics']['top40_coverage'] for r in rows) / len(rows),
            top40_sources=sum(f['retained'] for r in rows for f in r['facts']), source_total=sum(len(r['facts']) for r in rows),
            top40_complete=sum(r['metrics']['top40_all'] for r in rows), evidence_coverage=sum(r['evidence_metrics']['coverage'] for r in rows) / len(rows),
            evidence_sources=sum(f['selected'] for r in rows for f in r['evidence_facts']), evidence_complete=sum(r['evidence_metrics']['all'] for r in rows),
            evidence_blocks=sum(len(r['evidence']) for r in rows), rerank_pairs=sum(r['compute']['pairs'] for r in rows),
            rerank_inference_seconds=sum(r['compute']['inference_seconds'] for r in rows))
    return result


def report(recorder, summary, folder):
    summary['aggregate'] = aggregate(summary); summary['paired'] = paired(summary)
    write_json(folder / 'summary.json', summary); write_json(folder / 'comparison.json', dict(aggregate=summary['aggregate'], paired=summary['paired']))
    esc = html.escape; parts = ['<!doctype html><meta charset="utf-8"><title>清洗子查询重排</title><style>body{max-width:1300px;margin:30px auto;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:14px}details{margin:16px 0}</style>',
        '<h1>清洗子查询：owner / 原问题 / max 融合</h1><p>候选并集完全复用上一轮；只重排和回放6000字节/8块证据选择。没有生成答案。</p>',
        '<pre>' + esc(json.dumps(summary['aggregate'], ensure_ascii=False, indent=2)) + '</pre>']
    for cid in sorted({r['case_id'] for r in summary['results']}):
        parts.append(f'<details><summary>{cid}</summary>')
        for row in [r for r in summary['results'] if r['case_id'] == cid]:
            parts.append('<h3>' + row['arm'] + '</h3><pre>' + esc(json.dumps(dict(cleanup=row.get('cleanup'), metrics=row['metrics'], facts=row['facts'], evidence_metrics=row['evidence_metrics'], evidence_facts=row['evidence_facts'], evidence=row['evidence'], compute=row['compute']), ensure_ascii=False, indent=2)) + '</pre>')
        parts.append('</details>')
    (folder / 'index.html').write_text(''.join(parts), encoding='utf8')
    write_json(folder / 'report-data.json', dict(aggregate=summary['aggregate'], paired=summary['paired'], results=summary['results']))


def execute(root, prepare_only=False):
    bench = freeze(root); recorder = CleanRerankDataset(root, VERSION)
    try:
        if prepare_only:
            print(json.dumps(dict(status='not_run', benchmark=VERSION, sha256=recorder.digest))); return
        cfg = settings(root)
        for p, digest in {**bench['code_sha256'], **bench['source_inputs_sha256']}.items():
            if sha(root / p) != digest: raise ValueError('frozen_input_or_code_changed:' + p)
        recorder.sync_dataset()
        source = read(root / SOURCE_BASE / 'summary.json'); candidates_by_case = candidates_from_source(source)
        _, _, chunks = load_corpus(root); chunkmap = {x['chunk_id']: x for x in chunks}
        source_bench, _, _ = load_benchmark(root, SOURCE_VERSION); cases = {c['id']: c for c in source_bench['cases']}
        run_id = uuid.uuid4().hex; folder = root / 'artifacts/reports/stage-4' / VERSION / 'runs' / run_id; folder.mkdir(parents=True)
        summary = dict(run_id=run_id, benchmark=VERSION, benchmark_sha256=recorder.digest, status='running', started=datetime.now(timezone.utc).isoformat(), results=[])
        write_json(folder / 'summary.json', summary)
        for cid, union in candidates_by_case.items():
            original_row = next(r for r in source['results'] if r['case_id'] == cid and r['arm'] == 'Rerank-Original-Union40')
            original_ranked = original_row['ranked_candidates']; original_scores = {x['chunk_id']: x['rerank_score'] for x in original_ranked}
            queries = original_row['queries']; cleaned = [dict(q, **clean_text(q['text'])) if q['id'] != 'Q0' else dict(q, original=q['text'], cleaned=q['text'], removed=[], changed=False, policy='not_applicable') for q in queries]
            qtext = {q['id']: q['cleaned'] for q in cleaned}; subqueries = {q['id']: q['cleaned'] for q in cleaned if q['id'] != 'Q0'}
            # Score each candidate against every cleaned subquery that discovered it.
            groups = {}
            for item in union:
                owners = [qid for qid in item['found_by'] if qid in subqueries] or ['Q0']
                for qid in owners: groups.setdefault(qid, []).append(item['chunk_id'])
            owner_scores = {}; requests=[]; pairs=0; inference=0.; wall=0.
            for qid, ids in groups.items():
                for start in range(0, len(ids), 40):
                    batch = ids[start:start+40]; t0 = time.monotonic()
                    result = run_worker(root, cfg, 'rerank', [chunkmap[x] for x in batch], query=qtext[qid], timeout=1800)
                    wall += time.monotonic() - t0; pairs += len(batch); inference += result.get('inference_seconds', 0)
                    requests.append(dict(query_id=qid, query=qtext[qid], original_query=next(q['original'] for q in cleaned if q['id'] == qid), pairs=len(batch), inference_seconds=result.get('inference_seconds'), elapsed_seconds=result.get('elapsed_seconds'), model_reused=result.get('model_reused')))
                    for chunk_id, value in zip(batch, result['outputs']): owner_scores.setdefault(chunk_id, {})[qid] = float(value)
            for arm in ARMS:
                ranked=[]
                for item in union:
                    owner = owner_scores.get(item['chunk_id'], {})
                    owner_score = max(owner.values()) if owner else original_scores[item['chunk_id']]
                    original = original_scores[item['chunk_id']]
                    selected = owner_score if arm == 'Owner-Clean' else original if arm == 'Original-Reused' else max(original, owner_score)
                    ranked.append(dict(item, score_by=dict(original=original, owner=owner, selected=selected), rerank_score=selected, sources=deepcopy(item.get('discoveries', []))))
                ranked.sort(key=lambda x: (-x['rerank_score'], x['first_discovery']))
                ranked, metrics, facts = score_row(ranked, cases[cid], source_bench['units'], chunkmap)
                evidence, _, detail = assemble(ranked, chunkmap, [], cases[cid]['question'], comparison=True, budget=6000, evidence_max=8, source_policy='named_first')
                efacts = evidence_fact_coverage(evidence, cases[cid], source_bench['units'])
                evidence_metrics=dict(coverage=sum(f['selected'] for f in efacts)/len(efacts), all=all(f['selected'] for f in efacts), context_bytes=detail['context_bytes'], evidence_count=len(evidence), missing_groups=detail['missing_comparison_groups'])
                row=dict(case_id=cid, question=cases[cid]['question'], arm=arm, cleanup=cleaned, queries=[dict(id=q['id'], text=q['original'], cleaned=q['cleaned'], removed=q['removed']) for q in cleaned],
                    candidates=source_rows(union), ranked_candidates=ranked, metrics=metrics, facts=facts, evidence=[dict(e) for e in evidence], evidence_facts=efacts, evidence_metrics=evidence_metrics,
                    selection=dict(budget=6000,evidence_max=8,source_policy='named_first',detail=detail), compute=dict(pairs=pairs if arm == 'Owner-Clean' else 0, inference_seconds=inference if arm == 'Owner-Clean' else 0, wall_seconds=wall if arm == 'Owner-Clean' else 0, requests=requests if arm == 'Owner-Clean' else [], new_owner_scores=arm == 'Owner-Clean'),
                    started=summary['started'], finished=datetime.now(timezone.utc).isoformat(), rerank_model=dict(device=cfg.get('LOCAL_RERANKER_DEVICE'), dtype=cfg.get('LOCAL_RERANKER_DTYPE'), max_pair_tokens=1024))
                summary['results'].append(row)
            write_json(folder / f'{cid}.json', [r for r in summary['results'] if r['case_id'] == cid]); write_json(folder / 'summary.json', summary)
            print(json.dumps(dict(case_id=cid, owner_pairs=pairs), ensure_ascii=False), flush=True)
        summary.update(status='completed', finished=datetime.now(timezone.utc).isoformat())
        report(recorder, summary, folder); recorder.sync_run(folder / 'summary.json'); report(recorder, summary, folder)
        print(json.dumps(recorder.status, ensure_ascii=False), flush=True)
    finally: recorder.close()
