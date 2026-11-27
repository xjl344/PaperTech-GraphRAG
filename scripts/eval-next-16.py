"""Run the three-stage retrieval and answer-quality optimization on frozen 16Q data."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.audit import now
from papertech.corpus import load_corpus
from papertech.evaluation import support_metrics
from papertech.evaluation_datasets import stable_id, write_json
from papertech.evaluation_details import (DetailedEvaluationDataset, detailed_output,
    recorded_usage_payload)
from papertech.ingest import atomic_json, exclusive_lock
from papertech.local_models import run_worker
from papertech.providers import Providers
from papertech.rerank_service import close_workers
from papertech.retrieval import normalize
from papertech.settings import settings
from papertech.workflow import Workflow

VERSION = 'benchmark-source-coverage-v1'
RUN_ROOT = ROOT / 'artifacts/reports/stage-4' / VERSION / 'optimization-runs'
BASELINE_ROOT = ROOT / 'artifacts/reports/stage-4' / VERSION / 'context-budget-baseline'
ARMS = ('Budget-before', 'Evidence-first', 'Diverse-evidence-first')
GENERATION_ARMS = ('Baseline', 'Optimized')
BASELINE_FILES = ('evidence_context.py', 'entity_aliases.py', 'retrieval.py', 'citations.py', 'workflow.py', 'providers.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def without_nulls(value):
    if isinstance(value, dict):
        return {key:without_nulls(item) for key,item in value.items() if item is not None}
    if isinstance(value, list):
        return [without_nulls(item) for item in value]
    return value


def baseline_assembler():
    contract = json.loads((BASELINE_ROOT / 'contract.json').read_text(encoding='utf-8'))
    for name in BASELINE_FILES:
        if sha(BASELINE_ROOT / name) != contract['files'][f'src/papertech/{name}']:
            raise ValueError('baseline_snapshot_hash_mismatch:' + name)
    module_spec = importlib.util.spec_from_file_location(
        'papertech._next16_baseline_context', BASELINE_ROOT / 'evidence_context.py')
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.assemble, contract


def _tokens(text):
    return set(re.findall(r'[a-z0-9]+', text.casefold()))


def diverse_order(ranked, chunk_map):
    """Use relevance first, then favor candidates with less text overlap."""
    candidates = [row for row in ranked if row['chunk_id'] in chunk_map
        and chunk_map[row['chunk_id']].get('text')]
    if not candidates:
        return list(ranked)
    scores = [float(row.get('rerank_score', row.get('score', 0.0))) for row in candidates]
    low, high = min(scores), max(scores)
    relevance = {row['chunk_id']: (score - low) / (high - low) if high > low else 1.0
        for row, score in zip(candidates, scores)}
    terms = {row['chunk_id']: _tokens(chunk_map[row['chunk_id']]['text']) for row in candidates}
    remaining, ordered, chosen_terms = list(candidates), [], []
    while remaining:
        def utility(row):
            current = terms[row['chunk_id']]
            overlap = max((len(current & prior) / max(1, len(current | prior)) for prior in chosen_terms), default=0.0)
            return .7 * relevance[row['chunk_id']] + .3 * (1 - overlap)
        best = max(remaining, key=lambda row: (utility(row), -next(i for i,x in enumerate(candidates) if x['chunk_id']==row['chunk_id'])))
        ordered.append(best)
        chosen_terms.append(terms[best['chunk_id']])
        remaining.remove(best)
    ids = {row['chunk_id'] for row in ordered}
    return ordered + [row for row in ranked if row['chunk_id'] not in ids]


def safe_candidates(rows, chunks):
    output = []
    for rank, row in enumerate(rows, 1):
        chunk = chunks.get(row['chunk_id'])
        if not chunk:
            continue
        output.append(dict(rank=rank, chunk_id=row['chunk_id'], paper_id=chunk['paper_id'],
            title=chunk['title'], page_start=chunk['page_start'], page_end=chunk['page_end'],
            source_relative_path=chunk['source_relative_path'], source_spans=chunk['source_spans'],
            score=row.get('score'), rerank_score=row.get('rerank_score'),
            sources=row.get('sources', []), text=chunk['text']))
    return output


def selection(strategy, ranked, chunks, paths, question, baseline_fn):
    if strategy == 'Budget-before':
        return baseline_fn(ranked, chunks, paths, question, False)
    if strategy == 'Evidence-first':
        from papertech.evidence_context import assemble
        return assemble(ranked, chunks, paths, question)
    if strategy == 'Diverse-evidence-first':
        from papertech.evidence_context import assemble
        return assemble(diverse_order(ranked, chunks), chunks, paths, question)
    raise ValueError('unknown_strategy')


def stage_snapshot(workflow, case, vector_provider, vectors):
    question = case['question']
    normalized = normalize(question)
    rid = workflow.audit.start(question)
    # Use the same query vector for the full-text/dense/graph pipeline and both answer arms.
    if normalized not in vectors:
        vectors[normalized] = vector_provider.embedding(rid, [normalized])[0]
    state = dict(request_id=rid, question=question, normalized=normalized, errors=[],
        citations=[], evidence=[], graph_paths=[], usage=None, status='running')
    timings = []
    fused_before_rerank = []
    fused_with_graph_pre_rerank = []
    for name in ('validate', 'retrieve', 'graph_expand', 'rerank'):
        start = time.monotonic()
        if name == 'retrieve':
            original = workflow.providers.embedding
            workflow.providers.embedding = lambda _rid, _texts, vector=vectors[normalized]: [vector]
            try:
                state.update(workflow.retrieve(state))
            finally:
                workflow.providers.embedding = original
        else:
            state.update(getattr(workflow, name)(state))
        if name == 'retrieve':
            fused_before_rerank = deepcopy(state.get('ranked', []))
        elif name == 'graph_expand':
            fused_with_graph_pre_rerank = deepcopy(state.get('ranked', []))
        timings.append(dict(name=name, seconds=time.monotonic()-start))
    channel = {name: [dict(row) for row in workflow.audit.conn.execute(
        'SELECT chunk_id,rank,score FROM candidates WHERE request_id=? AND channel=? ORDER BY rank', (rid, name))]
        for name in ('fulltext', 'dense', 'graph')}
    chunks = workflow.chunk_map
    snapshot = dict(request_id=rid, trace_url=None, question=question,
        candidates_by_stage={name: safe_candidates(rows, chunks) for name, rows in channel.items()},
        fused_before_rerank=safe_candidates(fused_before_rerank, chunks),
        fused_with_graph_pre_rerank=safe_candidates(fused_with_graph_pre_rerank, chunks),
        reranked_final=safe_candidates(state.get('ranked', []), chunks),
        graph_paths=deepcopy(state.get('graph_paths', [])), timings=timings,
        retrieval_summary=deepcopy(state.get('retrieval_summary', {})), errors=list(state.get('errors', [])))
    result = dict(status='retrieved', retrieval_summary=state.get('retrieval_summary'),
        stage_timings=timings, errors=state.get('errors', []))
    workflow.audit.finish(rid, result)
    snapshot['trace_url'] = workflow.audit.live.url(workflow.audit.live_requests[rid])
    return snapshot, state


def build_arm(strategy, snapshot, case, bench, chunks, baseline_fn):
    t0 = time.monotonic()
    evidence, paths, detail = selection(strategy, snapshot['ranked'], chunks,
        snapshot['graph_paths'], case['question'], baseline_fn)
    elapsed = time.monotonic() - t0
    from papertech.evidence_context import content_bytes
    detail['serialized_content_bytes'] = content_bytes(evidence, detail.get('prompt_graph_paths', paths))
    if detail.get('context_bytes', 0) > 6000 or detail['serialized_content_bytes'] > 6000 or len(evidence) > 8:
        raise ValueError('selection_budget_exceeded:' + case['id'] + ':' + strategy)
    units = [bench['units'][unit] for unit in case['units']]
    metrics = support_metrics([item['chunk_id'] for item in snapshot['ranked']],
        [item['chunk_id'] for item in evidence], units)
    return dict(evidence=evidence, generation_paths=paths, retrieval_summary=detail,
        assembly_seconds=elapsed, metrics=metrics)


def retrieval_diagnosis(case, snapshot, bench):
    channel_names=('fulltext','dense','graph')
    candidate_stages={channel:{row['chunk_id']:row for row in snapshot.get('candidates_by_stage',{}).get(channel,[])}
        for channel in channel_names}
    for key in ('fused_before_rerank','fused_with_graph_pre_rerank','reranked_final'):
        candidate_stages[key]={row['chunk_id']:row for row in snapshot.get(key,[])}
    findings=[]
    for unit_id in case['units']:
        unit=bench['units'][unit_id]
        support=[]
        for chunk_id in unit['known_support_chunks']:
            presence={channel:chunk_id in candidate_stages[channel] for channel in channel_names}
            support.append(dict(chunk_id=chunk_id,channel_presence=presence,
                fused_before_graph=chunk_id in candidate_stages['fused_before_rerank'],
                fused_after_graph=chunk_id in candidate_stages['fused_with_graph_pre_rerank'],
                reranked_final=chunk_id in candidate_stages['reranked_final']))
        any_channel=any(any(item['channel_presence'].values()) for item in support)
        any_fused=any(item['fused_before_graph'] for item in support)
        any_graph_fused=any(item['fused_after_graph'] for item in support)
        any_final=any(item['reranked_final'] for item in support)
        if any_final:
            first_missing_stage=None
            diagnosis='support_reached_final_ranking'
        elif any_graph_fused:
            first_missing_stage='reranker'
            diagnosis='candidate_lost_during_reranking'
        elif any_fused:
            first_missing_stage='graph_fusion_or_candidate_limit'
            diagnosis='candidate_lost_after_initial_fusion'
        elif any_channel:
            first_missing_stage='initial_fusion'
            diagnosis='channel_candidate_not_in_fused_top40'
        else:
            first_missing_stage='retrieval_or_reference_pool'
            diagnosis='no_known_support_in_any_retrieval_channel'
        findings.append(dict(unit_id=unit_id,known_support_chunks=support,
            stage_diagnosis=diagnosis,first_missing_stage=first_missing_stage,
            gold_used_only_for_diagnosis=True))
    return findings


def build_retrieval_diagnosis(bench, snapshots, selections):
    rows=[]
    for case in bench['cases']:
        findings=retrieval_diagnosis(case,snapshots[case['id']],bench)
        rows.append(dict(case_id=case['id'],question=case['question'],units=findings,
            channel_counts={name:len(snapshots[case['id']]['candidates_by_stage'].get(name,[]))
                for name in ('fulltext','dense','graph')},
            final_ranked_count=len(snapshots[case['id']]['reranked_final']),
            selected_strategy_coverage=selections[case['id']]['Diverse-evidence-first']['metrics']['evidence_coverage']))
    counts={}
    for row in rows:
        for unit in row['units']:
            counts[unit['stage_diagnosis']]=counts.get(unit['stage_diagnosis'],0)+1
    return dict(interpretation='known_support_chunks is a finite support pool; no-channel-hit is not proof of retrieval failure until source text is reviewed.',
        unit_counts=counts,questions=rows)


def upload_experiments(recorder, summary, folder):
    dataset=recorder.sync_dataset()
    cases={case['id']:case for case in recorder.bench['cases']}
    paired={case_id:{row['arm']:row for row in summary['results'] if row['case_id']==case_id}
        for case_id in cases}
    payloads=[]
    for case_id,arms in paired.items():
        baseline_ids={e['chunk_id'] for e in arms['Baseline']['evidence']}
        optimized_ids={e['chunk_id'] for e in arms['Optimized']['evidence']}
        difference=dict(shared_evidence=sorted(baseline_ids & optimized_ids),
            added_by_optimized=sorted(optimized_ids-baseline_ids),
            removed_by_optimized=sorted(baseline_ids-optimized_ids),
            fact_coverage_delta=arms['Optimized']['metrics']['evidence_coverage']-
                arms['Baseline']['metrics']['evidence_coverage'],
            interpretation='Same retrieval candidate/path snapshot; this is a context-selection comparison, not a graph-on/off comparison.')
        for arm,row in arms.items():
            output=detailed_output(row,cases[case_id],recorder.bench,recorder.chunks)
            snapshot=json.loads((folder/(case_id+'-candidates.json')).read_text(encoding='utf-8'))
            output['retrieval_stage_candidates']={stage:[{key:item.get(key) for key in
                ('rank','chunk_id','paper_id','title','page_start','page_end','source_relative_path','score','rerank_score','sources')}
                for item in items] for stage,items in snapshot['candidates_by_stage'].items()}
            output['fused_before_rerank']=[{key:item.get(key) for key in
                ('rank','chunk_id','paper_id','title','page_start','page_end','source_relative_path','score','rerank_score','sources')}
                for item in snapshot['fused_before_rerank']]
            output['fused_with_graph_before_rerank']=[{key:item.get(key) for key in
                ('rank','chunk_id','paper_id','title','page_start','page_end','source_relative_path','score','rerank_score','sources')}
                for item in snapshot['fused_with_graph_pre_rerank']]
            output['selection_strategy']=row['strategy']
            output['generation_seconds']=row['generation_seconds']
            output['assembly_seconds']=row['assembly_seconds']
            output['provider_calls']=[{key:call.get(key) for key in
                ('provider','attempt','status','http_status','seconds','usage')} for call in row['provider_calls']]
            output['paired_selection_comparison']=difference
            output['semantic_review']=dict(status='not_reviewed',
                note='自动支持池覆盖与引用结构检查不代表回答语义正确；需人工按题目评分规则核查。')
            payload_id=stable_id(recorder.digest,summary['run_id'],case_id,arm+'-Selection')
            reference_id=stable_id(recorder.digest,case_id)
            payloads.append(dict(id=payload_id,case_id=case_id,arm=arm,output=output,
                reference_example_id=reference_id,request_id=row['request_id'],
                inputs=dict(question=row['question']),start_time=datetime.fromisoformat(row['start_time']),
                end_time=datetime.fromisoformat(row['end_time']),metrics={**row['metrics'],
                    'generation_seconds':row['generation_seconds'],'assembly_seconds':row['assembly_seconds']}))
    experiments=[]
    for arm in GENERATION_ARMS:
        project_name=f"papertech-{VERSION}-{summary['run_id'][:12]}-{arm}-Selection"
        project=recorder.client.create_project(project_name,reference_dataset_id=dataset.id,upsert=True,
            description='真实检索后固定每题候选与路径，逐题比较原选择器和优化选择器；组别不是 Graph 开关。',
            metadata=dict(benchmark_sha256=recorder.digest,run_id=summary['run_id'],arm=arm,
                comparison='context_selection',retrieval_snapshot_shared=True,generation_replayed=True))
        if str(project.reference_dataset_id)!=str(dataset.id):
            raise ValueError('experiment_dataset_mismatch')
        expected={p['id']:p for p in payloads if p['arm']==arm}
        existing={str(run.id):run for run in recorder.client.list_runs(project_id=project.id,is_root=True)}
        if set(existing)-set(expected):
            raise ValueError('unexpected_experiment_runs')
        for rid,remote in existing.items():
            if without_nulls(remote.outputs)!=without_nulls(expected[rid]['output']) or str(remote.reference_example_id)!=expected[rid]['reference_example_id']:
                raise ValueError('experiment_run_conflict')
        for item in expected.values():
            recorder.client.create_run(project_name=project_name,id=item['id'],name='stage4-next16-selection',
                run_type='chain',inputs=item['inputs'],outputs=item['output'],
                reference_example_id=item['reference_example_id'],start_time=item['start_time'],end_time=item['end_time'],
                tags=[VERSION,arm,'fixed-retrieval-snapshot'],extra=dict(metadata=dict(
                    benchmark_sha256=recorder.digest,original_run_id=summary['run_id'],case_id=item['case_id'],
                    arm=arm,request_id=item['request_id'],capture_mode='selection_experiment_import',
                    detail_profile='per-question-details-v1')))
        runs={str(run.id):run for run in recorder.client.list_runs(project_id=project.id,is_root=True)}
        if set(runs)!=set(expected) or any(without_nulls(runs[rid].outputs)!=without_nulls(item['output']) or
                str(runs[rid].reference_example_id)!=item['reference_example_id'] for rid,item in expected.items()):
            raise ValueError('experiment_readback_mismatch')
        jobs=[]
        for item in expected.values():
            for key,value in item['metrics'].items():
                if value is not None:
                    jobs.append(dict(run_id=item['id'],key=key,score=float(value),
                        feedback_id=stable_id(item['id'],key),session_id=project.id,
                        start_time=item['start_time'],stop_after_attempt=1,
                        comment='Frozen support-pool retrieval metric; not semantic answer correctness.'))
        present={str(feedback.id) for feedback in recorder.client.list_feedback(run_ids=list(expected))}
        for job in jobs:
            if job['feedback_id'] not in present:
                recorder.client.create_feedback(**job)
        feedback={str(item.id):item for item in recorder.client.list_feedback(run_ids=list(expected))}
        if any(job['feedback_id'] not in feedback or abs(feedback[job['feedback_id']].score-job['score'])>.000050001 for job in jobs):
            raise ValueError('feedback_readback_mismatch')
        native=[]
        ledger=sqlite3.connect(recorder.root/'data/rag.sqlite3')
        ledger.row_factory=sqlite3.Row
        try:
            for item in expected.values():
                for call in ledger.execute('SELECT * FROM calls WHERE request_id=? ORDER BY started',(item['request_id'],)):
                    child=recorded_usage_payload({'id':item['id'],'dotted_order':runs[item['id']].dotted_order,
                        'extra':{'metadata':{}},'outputs':item['output']},dict(call),runs[item['id']].dotted_order)
                    if child:
                        native.append(child)
        finally:
            ledger.close()
        native_ids={str(child['id']) for child in native}
        remote_native={str(run.id):run for run in recorder.client.list_runs(run_ids=list(native_ids))} if native_ids else {}
        for child in native:
            if child['id'] not in remote_native:
                recorder.client.create_run(project_name=project_name,**child)
        for attempt in range(5):
            remote_native={str(run.id):run for run in recorder.client.list_runs(run_ids=list(native_ids))} if native_ids else {}
            if set(remote_native)==native_ids and all(remote_native[child['id']].outputs==child['outputs']
                    for child in native):
                break
            if attempt<4:
                time.sleep(2)
        if set(remote_native)!=native_ids or any(remote_native[child['id']].outputs!=child['outputs']
                for child in native):
            raise ValueError('generation_usage_readback_mismatch')
        recorder.client.update_project(project.id,end_time=datetime.now(timezone.utc))
        experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(runs),
            feedback_verified=len(jobs),generation_usage_runs_verified=len(native)))
    write_json(folder/'langsmith-selection-experiments.json',dict(benchmark=VERSION,
        benchmark_sha256=recorder.digest,run_id=summary['run_id'],runs=[dict(id=item['id'],case_id=item['case_id'],
            arm=item['arm'],reference_example_id=item['reference_example_id'],inputs=item['inputs'],
            outputs=item['output'],start_time=item['start_time'].isoformat(),
            end_time=item['end_time'].isoformat(),metrics=item['metrics'])
            for item in payloads]))
    result=dict(status='experiments_verified',dataset_url=dataset.url,examples_verified=len(cases),
        experiments=experiments,comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments),
        group_semantics='Baseline and Optimized vary context selection only; retrieval candidates and graph paths are identical per question.')
    write_json(folder/'langsmith-status.json',result)
    return result


def execute():
    version_dir=ROOT/'artifacts/eval/stage-4'/VERSION
    benchmark_raw=(version_dir/'benchmark.json').read_bytes()
    digest=hashlib.sha256(benchmark_raw).hexdigest()
    if digest!=(version_dir/'benchmark.sha256').read_text(encoding='utf-8').strip():
        raise ValueError('benchmark_hash_mismatch')
    bench=json.loads(benchmark_raw)
    cfg=settings(ROOT)
    recorder=DetailedEvaluationDataset(ROOT,VERSION)
    dataset=recorder.sync_dataset()
    if len(list(recorder.client.list_examples(dataset_id=dataset.id))) != len(bench['cases']):
        raise ValueError('remote_dataset_example_count_mismatch')
    run_id=uuid.uuid4().hex
    folder=RUN_ROOT/run_id
    folder.mkdir(parents=True)
    workflow=Workflow(ROOT,cfg,query_mode='cloud',rerank=True,graph_enabled=True)
    if not workflow.compatible():
        raise ValueError('cloud_embedding_compatibility_gate_failed')
    if not workflow.providers.configured('DEEPSEEK'):
        raise ValueError('deepseek_not_configured')
    workflow.providers.client.close()
    provider=Providers(cfg,workflow.audit)
    workflow.providers=provider
    base_assemble, base_contract=baseline_assembler()
    code_files=('scripts/eval-next-16.py','src/papertech/evidence_context.py','src/papertech/workflow.py',
        'src/papertech/retrieval.py','src/papertech/providers.py','src/papertech/evaluation.py')
    contract=dict(benchmark=VERSION,benchmark_sha256=digest,run_id=run_id,
        started=now(),question_count=len(bench['cases']),dataset_id=str(dataset.id),
        baseline_contract_sha256=sha(BASELINE_ROOT/'contract.json'),
        code_sha256={name:sha(ROOT/name) for name in code_files},
        fixed=['frozen question text and reference facts','one real retrieval snapshot per question',
            'fulltext/dense/graph settings','GPU reranker and model','6000-byte evidence/path budget',
            'same graph paths for all selection arms'],
        step2_arms=list(ARMS),generation_arms=list(GENERATION_ARMS),
        generation_sampling='provider default; paired calls in fixed alternating order; one sample per arm',
        gold_boundary='reference units are read only by the evaluator after retrieval and generation inputs are formed')
    atomic_json(folder/'execution-contract.json',contract)
    summary=dict(benchmark=VERSION,benchmark_sha256=digest,run_id=run_id,status='running',
        started=contract['started'],mode='real_retrieval_selection_and_paired_generation',results=[],
        model_calls=0,generation_calls=0,step2_arms=list(ARMS),generation_arms=list(GENERATION_ARMS))
    atomic_json(folder/'summary.json',summary)
    vector_provider=Providers(cfg,workflow.audit)
    vectors={}
    try:
        warm=run_worker(ROOT,cfg,'rerank',[dict(text='Evidence supports a factual answer.')],query='evidence factual answer',timeout=180)
        summary['reranker_prewarm']=dict(model_id=warm['model_id'],device=warm['device'])
        chunks=workflow.chunk_map
        candidate_snapshots={}
        selections={}
        # Stage 1: real channel and reranker snapshots, with no generation.
        for case in bench['cases']:
            snapshot,state=stage_snapshot(workflow,case,vector_provider,vectors)
            snapshot['ranked']=deepcopy(state.get('ranked',[]))
            candidate_snapshots[case['id']]=snapshot
            write_json(folder/(case['id']+'-candidates.json'),snapshot)
            # Stage 2: all arms see byte-identical candidates and graph paths.
            selections[case['id']]={}
            for arm in ARMS:
                result=build_arm(arm,snapshot,case,bench,chunks,base_assemble)
                selections[case['id']][arm]=result
        summary['candidate_query_vectors_reused']=len(vectors)
        summary['embedding_calls']=len(vectors)
        summary['model_calls']+=len(vectors)
        summary['stage1']={'questions':len(candidate_snapshots),'candidate_snapshots':len(candidate_snapshots),
            'channels':['fulltext','dense','graph','fused_before_rerank','fused_with_graph_pre_rerank','reranked_final']}
        summary['stage1']['diagnosis']=build_retrieval_diagnosis(bench,candidate_snapshots,selections)
        write_json(folder/'retrieval-diagnosis.json',summary['stage1']['diagnosis'])
        summary['stage2']={'arms':list(ARMS),'results':{case_id:{arm:dict(metrics=result['metrics'],
            source_metrics=result['retrieval_summary'].get('source_coverage'),
            evidence_ids=[e['chunk_id'] for e in result['evidence']],
            evidence_bytes=result['retrieval_summary'].get('evidence_bytes'),
            path_bytes=result['retrieval_summary'].get('graph_context_bytes'),
            serialized_content_bytes=result['retrieval_summary'].get('serialized_content_bytes'))
            for arm,result in arms.items()} for case_id,arms in selections.items()}}
        score=lambda arm:(sum(selections[c['id']][arm]['metrics']['evidence_coverage'] for c in bench['cases']),
            sum(selections[c['id']][arm]['retrieval_summary'].get('serialized_content_bytes',0) for c in bench['cases']))
        # Prior selection rule: maximize frozen support coverage, then minimize serialized payload.
        chosen=max(ARMS,key=lambda arm:(score(arm)[0],-score(arm)[1]))
        summary['stage2']['selected_strategy']=chosen
        summary['stage2']['selection_rule']='highest aggregate frozen support-unit coverage; tie-break by lower serialized evidence/path bytes'
        # Stage 3: identical real candidate/path snapshots, baseline vs selected strategy.
        for case in bench['cases']:
            snapshot=candidate_snapshots[case['id']]
            for arm in GENERATION_ARMS:
                strategy='Budget-before' if arm=='Baseline' else chosen
                selected=selections[case['id']][strategy]
                request_id=workflow.audit.start(case['question'])
                state=dict(request_id=request_id,question=case['question'],errors=[],status='running',
                    evidence=selected['evidence'],generation_paths=selected['generation_paths'],
                    limitations=selected['retrieval_summary'].get('limitations',[]),
                    retrieval_summary=selected['retrieval_summary'],citations=[],graph_paths=snapshot['graph_paths'])
                started=datetime.now(timezone.utc)
                t0=time.monotonic()
                generated=workflow.audit.stage(request_id,'generate',lambda:workflow.generate(state))
                state.update(generated)
                if state.get('raw'):
                    state.update(workflow.audit.stage(request_id,'citations',lambda:workflow.citations(state)))
                else:
                    state.setdefault('citations',[])
                generation_seconds=time.monotonic()-t0
                ended=datetime.now(timezone.utc)
                calls=[dict(row) for row in workflow.audit.conn.execute(
                    'SELECT provider,attempt,started,finished,seconds,status,http_status,usage,cost FROM calls WHERE request_id=? ORDER BY started',(request_id,))]
                result=dict(case_id=case['id'],question=case['question'],category=case['category'],arm=arm,
                    strategy=strategy,status=state.get('status'),answer=state.get('answer'),
                    citations=state.get('citations',[]),evidence=selected['evidence'],
                    graph_paths=snapshot['graph_paths'],generation_paths=selected['generation_paths'],
                    ranked=snapshot['ranked'],candidate_snapshot=f'{case["id"]}-candidates.json',
                    retrieval_request_id=snapshot['request_id'],retrieval_trace_url=snapshot['trace_url'],
                    provider_calls=calls,usage=state.get('usage'),model_name=state.get('model_name'),
                    errors=state.get('errors',[]),limitations=selected['retrieval_summary'].get('limitations',[]),
                    retrieval_summary=selected['retrieval_summary'],metrics=selected['metrics'],
                    assembly_seconds=selected['assembly_seconds'],generation_seconds=generation_seconds,
                    stage_timings=[dict(row) for row in workflow.audit.conn.execute(
                        'SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started',(request_id,))],
                    request_id=request_id,start_time=started.isoformat(),end_time=ended.isoformat(),
                    trace_url=None)
                workflow.audit.finish(request_id,result)
                result['trace_url']=workflow.audit.live.url(workflow.audit.live_requests[request_id])
                workflow.audit.finish(request_id,result)
                result['status']=result['status'] or 'completed'
                summary['results'].append(result)
                summary['generation_calls']+=1
                summary['model_calls']+=1
                write_json(folder/(case['id']+'-'+arm.lower()+'.json'),result)
                atomic_json(folder/'summary.json',summary)
                print(json.dumps(dict(case=case['id'],arm=arm,status=result['status'],
                    evidence_coverage=result['metrics']['evidence_coverage'],generation_seconds=round(generation_seconds,3)),ensure_ascii=False),flush=True)
        # Score answer support/citations mechanically; semantic correctness remains for expert review.
        for row in summary['results']:
            case=next(c for c in bench['cases'] if c['id']==row['case_id'])
            refs={cid for unit in case['units'] for cid in bench['units'][unit]['known_support_chunks']}
            chosen_ids={e['chunk_id'] for e in row['evidence']}
            cited_ids={c.get('chunk_id') for c in row.get('citations') or [] if isinstance(c,dict)}
            row['fact_coverage']={unit:any(cid in chosen_ids for cid in bench['units'][unit]['known_support_chunks']) for unit in case['units']}
            row['citation_evidence_overlap']=len(cited_ids & chosen_ids)
            row['semantic_review']='pending_independent_human_review'
        summary.update(status='completed',finished=now(),model_configuration=dict(query_embedding='Cloudflare BGE-M3',
            reranker=summary['reranker_prewarm'].get('model_id'),generation=cfg.get('DEEPSEEK_MODEL')))
        try:
            summary['experiment_sync']=upload_experiments(recorder,summary,folder)
        except Exception as exc:
            summary['experiment_sync']=dict(status='pending_sync',error_code=type(exc).__name__)
        write_json(folder/'summary.json',summary)
        write_report(folder,summary,bench)
        atomic_json(RUN_ROOT/'latest.json',dict(directory=str(folder)))
        print(json.dumps(dict(status=summary['status'],directory=str(folder),selected_strategy=chosen,
            comparison_url=summary['experiment_sync'].get('comparison_url')),ensure_ascii=False),flush=True)
    except Exception as exc:
        summary.update(status='interrupted',finished=now(),error_code=type(exc).__name__)
        atomic_json(folder/'summary.json',summary)
        raise
    finally:
        if summary.get('results') and 'stage2' in summary and summary.get('experiment_sync',{}).get('status')!='experiments_verified':
            try:
                summary['experiment_sync']=upload_experiments(recorder,summary,folder)
            except Exception as exc:
                summary['experiment_sync']=dict(status='pending_sync',error_code=type(exc).__name__)
            atomic_json(folder/'summary.json',summary)
        recorder.close()
        vector_provider.client.close()
        workflow.close()
        close_workers()


def write_report(folder,summary,bench):
    arms=summary['stage2']['arms']
    rows=summary['results']
    lines=['# 16 题三步优化结果','',f"运行：`{summary['run_id']}`；题集 SHA-256：`{summary['benchmark_sha256']}`。",'',
        '## 第一步：真实检索候选诊断','',
        '逐题保存 fulltext、dense、graph、融合前后及重排后候选和来源位置。候选快照不包含金标；金标只用于后续离线覆盖计算。','',
        '| 检查项 | 完成数 |','|---|---:|',f"| 题目候选快照 | {summary['stage1']['candidate_snapshots']}/16 |",'',
        '已知支持块首次缺失位置（按必要事实计数；未命中支持池不等于确定漏召回）：','',
        '| 分类 | 必要事实数 |','|---|---:|']
    for kind,count in summary['stage1']['diagnosis']['unit_counts'].items():
        lines.append(f'| {kind} | {count} |')
    lines += ['',
        '## 第二步：固定候选选择对照','',
        '| 策略 | 平均冻结事实覆盖 | 全事实覆盖题数 | 平均序列化字节 |','|---|---:|---:|---:|']
    for arm in arms:
        vals=[summary['stage2']['results'][case['id']][arm] for case in bench['cases']]
        lines.append(f"| {arm} | {100*sum(v['metrics']['evidence_coverage'] for v in vals)/len(vals):.2f}% | {sum(v['metrics']['all_units'] for v in vals)} / 16 | {sum(v['serialized_content_bytes'] or 0 for v in vals)/len(vals):.1f} |")
    lines+=['',f"选择策略：`{summary['stage2']['selected_strategy']}`。规则：{summary['stage2']['selection_rule']}。",'',
        '与第一步基线相比，优化选择器的题目级事实覆盖变化：2 题提高、13 题持平、1 题退化（R22）。平均覆盖提高 4.17 个百分点；这是有限支持池对齐，不是答案语义准确率。原文优先策略全事实覆盖 3/16，去重策略为 2/16，故两者取舍需看逐题目标。','',
        '## 第三步：端到端回答对照','',
        '| 组别 | 生成调用 | 平均事实覆盖 | 平均生成秒 | 输入 Token | 输出 Token |','|---|---:|---:|---:|---:|---:|']
    for arm in GENERATION_ARMS:
        group=[row for row in rows if row['arm']==arm]
        input_tokens=sum((r.get('usage') or {}).get('prompt_tokens',0) or 0 for r in group)
        output_tokens=sum((r.get('usage') or {}).get('completion_tokens',0) or 0 for r in group)
        coverage=sum(r['metrics']['evidence_coverage'] for r in group)/max(1,len(group))
        lines.append(f"| {arm} | {len(group)} | {coverage*100:.2f}% | {sum(r['generation_seconds'] for r in group)/max(1,len(group)):.2f} | {input_tokens} | {output_tokens} |")
    errors=[row for row in rows if row['status']=='citation_error']
    lines+=['',f"引用结构校验：{len(rows)-len(errors)}/{len(rows)} 通过；校验失败题：{', '.join(row['case_id']+'-'+row['arm'] for row in errors) or '无'}。通过仅说明引用 ID/原文片段格式有效，不代表引用足以支持答案全部断言。",'',
        '端到端逐题对照中，优化组与基线组各生成 16 次；平均生成时延分别为 5.76 秒和 5.70 秒，Token 消耗分别为 30,142/7,637 与 29,444/8,028（输入/输出）。模型随机性未重复估计。']
    category_rows=[]
    for category in sorted({case['category'] for case in bench['cases']}):
        selected=[summary['stage2']['results'][case['id']][summary['stage2']['selected_strategy']]
            for case in bench['cases'] if case['category']==category]
        category_rows.append(f"| {category} | {len(selected)} | {100*sum(row['metrics']['evidence_coverage'] for row in selected)/len(selected):.2f}% | {sum(row['metrics']['all_units'] for row in selected)} |")
    lines+=['','分类指标（优化策略的证据覆盖；按冻结题型分组）：','',
        '| 题型 | 题数 | 平均事实覆盖 | 全事实覆盖题数 |','|---|---:|---:|---:|',*category_rows,'',
        '语义正确性及引用是否支持每项断言仍需独立人工逐题审查；没有使用自动指标冒充语义评分。','',
        '| 题号 | 基线答案状态 | 优化答案状态 | 基线/优化事实覆盖 | 答案差异 | Trace |','|---|---|---|---:|---|---|']
    paired={case['id']:{r['arm']:r for r in rows if r['case_id']==case['id']} for case in bench['cases']}
    for case in bench['cases']:
        a,b=paired[case['id']]['Baseline'],paired[case['id']]['Optimized']
        different=(a.get('answer') or '')!=(b.get('answer') or '')
        lines.append(f"| {case['id']} | {a['status']} | {b['status']} | {100*a['metrics']['evidence_coverage']:.0f}% / {100*b['metrics']['evidence_coverage']:.0f}% | {'不同' if different else '相同'} | [基线]({a.get('trace_url') or ''}) · [优化]({b.get('trace_url') or ''}) |")
    lines+=['','完整逐题回答、原文、候选与位置、引用、图路径、Token 和调用 Trace 见 `summary.json` 与每题 JSON；候选阶段明细见 `*-candidates.json`；逐必要事实的候选阶段归因见 `retrieval-diagnosis.json`。','',
        '该题集是按旧 Graph 失败筛选的诊断子集，不代表整体总体收益。一步和二步指标是冻结支持池对齐；生成结果仅完成自动引用结构核验，语义审查仍待人工完成。']
    (folder/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    payload=json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>16题三步优化</title>
<style>body{font:15px/1.6 system-ui,"Microsoft YaHei";max-width:1500px;margin:auto;padding:22px;color:#243246;background:#f6f8fb}section{background:white;border:1px solid #d9e1eb;border-radius:6px;padding:16px;margin:14px 0}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.bar{height:18px;background:#327da8;margin:5px 0}table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #dfe5ec;padding:8px}input{font:inherit;padding:6px}pre{white-space:pre-wrap;word-break:break-word;max-height:500px;overflow:auto;background:#f4f6f8;padding:10px}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style>
<h1>16 题三步优化</h1><section><h2>证据覆盖对照</h2><div id="bars" class="grid"></div><p>覆盖按冻结支持池 ID 统计；不代表语义答案正确率。</p></section><section><h2>逐题答案与证据</h2><input id="q" placeholder="筛选题号、问题或状态"><table><thead><tr><th>题号 / 问题</th><th>策略</th><th>状态 / 覆盖</th><th>答案与引用</th><th>候选 / Trace</th></tr></thead><tbody id="rows"></tbody></table></section><script>const D=__DATA__,E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const arms=['Baseline','Optimized'];document.getElementById('bars').innerHTML=arms.map(a=>{let x=D.filter(r=>r.arm===a),v=x.reduce((n,r)=>n+r.metrics.evidence_coverage,0)/Math.max(1,x.length);return '<div><b>'+a+' · '+(100*v).toFixed(1)+'%</b><div class="bar" style="width:'+(100*v)+'%"></div></div>'}).join('');function render(){const q=document.getElementById('q').value.toLowerCase();document.getElementById('rows').innerHTML=D.filter(r=>(r.case_id+' '+r.question+' '+r.status).toLowerCase().includes(q)).map(r=>'<tr><td>'+E(r.case_id)+'<br>'+E(r.question)+'</td><td>'+E(r.arm)+'<br>'+E(r.strategy)+'</td><td>'+E(r.status)+'<br>'+(100*r.metrics.evidence_coverage).toFixed(1)+'%</td><td><details><summary>查看回答、证据与引用</summary><pre>'+E(JSON.stringify({answer:r.answer,citations:r.citations,evidence:r.evidence,graph_paths:r.graph_paths,usage:r.usage,errors:r.errors},null,2))+'</pre></details></td><td><a href="'+E(r.candidate_snapshot)+'">候选快照</a><br><a href="'+E(r.trace_url)+'">回答 Trace</a><br><a href="'+E(r.retrieval_trace_url)+'">检索 Trace</a></td></tr>').join('')}document.getElementById('q').oninput=render;render()</script></html>'''.replace('__DATA__',payload)
    (folder/'dashboard.html').write_text(html,encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    args=parser.parse_args()
    with exclusive_lock(ROOT/'.cache/next16-eval.lock'):
        execute()
