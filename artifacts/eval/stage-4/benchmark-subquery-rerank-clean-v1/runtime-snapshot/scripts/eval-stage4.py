"""Execute the frozen paired development evaluation using production methods.

No gold text, keywords or IDs are passed to retrieval/generation. Each pair shares
the same cloud query vector. Append-only run outputs; no automatic paid replay.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.audit import now
from papertech.evaluation import support_metrics,criterion_source_coverage
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import dataset_recorder,result_mode
from papertech.ingest import atomic_json,exclusive_lock
from papertech.local_models import run_worker
from papertech.providers import Providers
from papertech.rerank_service import close_workers
from papertech.retrieval import normalize
from papertech.settings import settings
from papertech.workflow import Workflow
from papertech.evaluation_runtime import v4_contract,open_v4_graph

class CachedProviders(Providers):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.vectors={}; self.cache_hits=0
    def embedding(self,request_id,texts):
        if any(t not in self.vectors for t in texts):
            raise RuntimeError('frozen_query_vector_not_present')
        self.cache_hits+=len(texts)
        return [list(self.vectors[t]) for t in texts]


def verify_remote(live,root_ids):
    live.flush()
    ids=set(root_ids)
    rows=[dict(r) for r in live.conn.execute('SELECT * FROM spans')]
    while True:
        grown=ids|{r['id'] for r in rows if r['parent_id'] in ids}
        if grown==ids:break
        ids=grown
    checks=[]
    for row in rows:
        if row['id'] not in ids:continue
        try:
            remote=live.client.read_run(row['id'])
            event=live.conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1",(row['id'],)).fetchone()
            payload=json.loads(event[0]) if event else {}
            usage_ok=None
            if 'prompt_tokens' in payload:
                usage_ok=remote.prompt_tokens==payload['prompt_tokens'] and remote.completion_tokens==payload['completion_tokens']
            checks.append(dict(id=row['id'],name=row['name'],finished=remote.end_time is not None,native_usage_matches=usage_ok))
        except Exception as exc:checks.append(dict(id=row['id'],finished=False,error=type(exc).__name__))
    pending=sum(1 for row in live.conn.execute("SELECT span_id FROM events WHERE status='pending'") if row[0] in ids)
    return dict(verified=bool(checks) and not pending and all(c['finished'] and c.get('native_usage_matches') is not False for c in checks),
                pending_events=pending,span_count=len(checks),spans=checks)


def execute(benchmark_name='benchmark-v1'):
    bench_dir=ROOT/'artifacts/eval/stage-4'/benchmark_name
    raw=(bench_dir/'benchmark.json').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=(bench_dir/'benchmark.sha256').read_text().strip():raise RuntimeError('benchmark_modified')
    benchmark=json.loads(raw)
    if benchmark['version']!=benchmark_name:raise RuntimeError('benchmark_version_mismatch')
    is_v4=benchmark_name=='benchmark-v4'
    for name,expected in benchmark.get('code_sha256',{}).items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('frozen_code_changed:'+name)
    cfg=settings(ROOT)
    if not is_v4 and 'code_sha256' not in benchmark:raise RuntimeError('unsupported_execution_contract')
    contract=v4_contract(ROOT,benchmark,cfg) if is_v4 else None
    recorder=dataset_recorder(ROOT,benchmark_name)
    # Create the shared reference dataset before any new model calls.
    if cfg.get('LANGSMITH_API_KEY'):
        try:recorder.sync_dataset()
        except Exception as exc:
            recorder.status.update(status='pending_sync',error_type=type(exc).__name__)
            write_json(recorder.status_path,recorder.status)
            recorder.close()
            raise RuntimeError('dataset_sync_required_before_model_calls') from None
    run_id=uuid.uuid4().hex
    report_root=ROOT/'artifacts/reports/stage-4'
    if benchmark_name!='benchmark-v1':report_root=report_root/benchmark_name
    destination=report_root/'runs'/run_id
    destination.mkdir(parents=True)
    expander=open_v4_graph(ROOT,contract) if is_v4 else None
    workflow=Workflow(ROOT,cfg,query_mode='cloud',path_budget=1200,graph_expander=expander) if is_v4 else Workflow(ROOT,cfg)
    workflow.providers.client.close()
    provider=CachedProviders(cfg,workflow.audit)
    workflow.providers=provider
    if workflow.corpus_id!=benchmark['corpus_id']:raise RuntimeError('corpus_changed')
    if not is_v4:
        for key,value in benchmark['models'].items():
            if cfg.get(key)!=value:raise RuntimeError('model_configuration_changed:'+key)
    report=dict(run_id=run_id,started=now(),benchmark_sha256=digest,benchmark=benchmark_name,status='running',results=[])
    if contract:report['execution_config']=contract
    atomic_json(destination/'execution-contract.json',dict(benchmark_sha256=digest,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        evaluation_sha256=hashlib.sha256((ROOT/'src/papertech/evaluation.py').read_bytes()).hexdigest(),
        dataset_export_sha256=hashlib.sha256((ROOT/'src/papertech/evaluation_datasets.py').read_bytes()).hexdigest(),
        detail_export_sha256=hashlib.sha256((ROOT/'src/papertech/evaluation_details.py').read_bytes()).hexdigest(),
        dataset_policy=json.loads((ROOT/'artifacts/eval/dataset-policy.json').read_text(encoding='utf-8')),
        latency_boundary=contract['latency'] if is_v4 else benchmark['scoring']['latency'],
        runtime=contract,generation_sampling='provider default, same payload configuration in both arms; one sample each; stochastic variance not estimated'))
    atomic_json(destination/'summary.json',report)
    print(json.dumps(dict(run_id=run_id,cases=len(benchmark['cases']),
        generation_pairs=sum(c['generate'] for c in benchmark['cases']))),flush=True)
    root_ids=[]
    try:
        if is_v4:
            index=workflow.store.inspect()
            if index['counts']!=[dict(chunks=980,papers=14)] or any(r['state']!='ONLINE' for r in index['indexes']):
                raise RuntimeError('index_preflight_failed')
            atomic_json(destination/'index-snapshot.json',index)
        # Prewarm once, outside timed query processing.
        rid=workflow.audit.start('[stage4 shared GPU warmup metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        warm=workflow.audit.stage(rid,'gpu_warmup',lambda:run_worker(ROOT,cfg,'rerank',
            [dict(text='Source evidence supports retrieval.')],query='source evidence',timeout=180))
        warm.pop('outputs',None)
        if is_v4 and warm.get('device')!='cuda':raise RuntimeError('gpu_reranker_unavailable')
        workflow.audit.finish(rid,dict(status='completed',retrieval_summary=dict(reranker=warm)))
        report['prewarm']=warm
        # One batch request. Do not send papers or reference answers to Cloudflare.
        texts=[normalize(c['question']) for c in benchmark['cases']]
        if not workflow.compatible():raise RuntimeError('cloud_compatibility_gate_failed')
        rid=workflow.audit.start('[stage4 shared cloud query-vector batch metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        start=time.monotonic()
        vectors=workflow.audit.stage(rid,'shared_query_embeddings',lambda:Providers.embedding(provider,rid,texts))
        report['shared_embedding_batch_seconds']=time.monotonic()-start
        provider.vectors=dict(zip(texts,vectors))
        cache=ROOT/'.cache/stage4'/run_id
        cache.mkdir(parents=True)
        atomic_json(cache/'query-vectors.json',dict(zip(texts,vectors)))
        workflow.audit.finish(rid,dict(status='completed',retrieval_summary=dict(query_count=len(texts),vector_dimensions=1024)))
        report['shared_embedding_calls']=[dict(r) for r in workflow.audit.conn.execute(
            'SELECT provider,status,http_status,seconds,usage FROM calls WHERE request_id=?',(rid,))]
        for number,case in enumerate(benchmark['cases'],1):
            arms=['Hybrid','Hybrid+Graph'] if number%2 else ['Hybrid+Graph','Hybrid']
            for arm in arms:
                workflow.graph_enabled=arm=='Hybrid+Graph'
                request_started=time.monotonic()
                rid=workflow.audit.start(case['question'])
                root_ids.append(workflow.audit.live_requests[rid])
                state=dict(request_id=rid,question=case['question'],errors=[],citations=[],evidence=[],graph_paths=[],
                           usage=None,estimated_cost=None,model_name=None,status='running')
                timings=[]
                def retrieve_pipeline():
                    for name in ('validate','retrieve','graph_expand','rerank','evidence'):
                        if state.get('status') in ('refused','error','invalid_input'):break
                        began=time.monotonic()
                        state.update(getattr(workflow,name)(state))
                        timings.append(dict(name=name,seconds=time.monotonic()-began))
                    return dict(retrieval_summary=state.get('retrieval_summary'),status=state['status'],errors=state['errors'],timings=timings)
                workflow.audit.stage(rid,'retrieval_pipeline',retrieve_pipeline)
                if is_v4 and (state.get('status')=='error' or any(e.startswith(('embedding_unavailable','reranker_skipped','graph_expansion_skipped')) for e in state['errors'])):
                    # Stop before a paid answer if the declared retrieval treatment failed.
                    workflow.audit.finish(rid,dict(status='error',errors=state['errors']))
                    raise RuntimeError('declared_retrieval_configuration_failed')
                if state['status']=='running':
                    if case['generate']:
                        state.update(workflow.audit.stage(rid,'generate',lambda:workflow.generate(state)))
                        state.update(workflow.audit.stage(rid,'citations',lambda:workflow.citations(state)))
                    else:
                        state.update(status='evidence_only',answer='本题按预先冻结口径仅比较检索证据。')
                result={k:state.get(k) for k in ('request_id','status','answer','citations','evidence','graph_paths','generation_paths',
                         'limitations','retrieval_summary','usage','model_name','errors','raw','ranked')}
                result.update(case_id=case['id'],question=case['question'],category=case['category'],arm=arm,order=arms.index(arm)+1,
                    generate_requested=case['generate'],compute_timings=timings,retrieval_compute_seconds=sum(t['seconds'] for t in timings),
                    embedding_source='shared frozen cloud vector; network batch time reported separately',
                    stage_timings=[dict(r) for r in workflow.audit.conn.execute('SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started',(rid,))],
                    provider_calls=[dict(r) for r in workflow.audit.conn.execute('SELECT provider,attempt,status,http_status,seconds,usage FROM calls WHERE request_id=? ORDER BY started',(rid,))])
                result['metrics']=support_metrics([r['chunk_id'] for r in state.get('ranked',[])],[e['chunk_id'] for e in state['evidence']],
                    [benchmark['units'][u] for u in case['units']])
                if is_v4:
                    result['execution_config']=contract
                    result['request_wall_seconds']=time.monotonic()-request_started
                    result['candidate_channels']=[dict(r) for r in workflow.audit.conn.execute(
                        'SELECT channel,rank,chunk_id,score FROM candidates WHERE request_id=? ORDER BY channel,rank',(rid,))]
                    result['criterion_source_coverage']=criterion_source_coverage(case,
                        [e['chunk_id'] for e in state['evidence']],benchmark['units'])
                workflow.audit.finish(rid,result)
                result['trace_url']=workflow.audit.live.url(workflow.audit.live_requests[rid])
                workflow.audit.finish(rid,result)
                atomic_json(destination/(case['id']+'-'+('graph' if workflow.graph_enabled else 'hybrid')+'.json'),result)
                report['results'].append(result)
                atomic_json(destination/'summary.json',report)
                print(json.dumps(dict(case=case['id'],arm=arm,status=result['status'],recall5=result['metrics']['recall5'],
                    evidence_coverage=result['metrics']['evidence_coverage'],seconds=result['retrieval_compute_seconds'],errors=result['errors']),ensure_ascii=False),flush=True)
        report['remote_verification']=verify_remote(workflow.audit.live,root_ids)
        if is_v4 and hashlib.sha256(expander.path.read_bytes()).hexdigest()!=expander.sha256:
            raise RuntimeError('graph_changed_during_execution')
        if is_v4 and v4_contract(ROOT,benchmark,cfg)!=contract:
            raise RuntimeError('execution_configuration_changed_during_run')
        report.update(status='completed',finished=now(),shared_vector_cache_hits=provider.cache_hits)
        atomic_json(destination/'summary.json',report)
        atomic_json(report_root/'latest.json',dict(directory=str(destination)))
        print(json.dumps(dict(status='completed',directory=str(destination),remote_verified=report['remote_verification']['verified'])),flush=True)
    except Exception as exc:
        report.update(status='interrupted',error_code=type(exc).__name__,finished=now())
        atomic_json(destination/'summary.json',report)
        print(json.dumps(dict(status='interrupted',error_code=type(exc).__name__,directory=str(destination))),flush=True)
        raise
    finally:
        # Upload recorded results, including partial runs, without replaying any model.
        try:
            if cfg.get('LANGSMITH_API_KEY') and report['results']:
                report['dataset_sync']=recorder.sync_run(destination/'summary.json',result_mode(ROOT,benchmark_name))
        except Exception as exc:
            report['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
            recorder.status.update(report['dataset_sync'])
            write_json(recorder.status_path,recorder.status)
        finally:
            atomic_json(destination/'summary.json',report)
            recorder.close(); workflow.close(); close_workers()
            if expander:expander.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark',choices=('benchmark-v1','benchmark-v2','benchmark-v4','benchmark-source-coverage-v1','benchmark-retrieval-v1','benchmark-relation-holdout-v1','benchmark-rerank-window-v1','benchmark-recall-width-v1','benchmark-resource-selection-v1','benchmark-recall-intervention-v1','benchmark-subquery-quality-v1','benchmark-subquery-quality-v2','benchmark-query-router-v1','benchmark-subquery-recall-v1','benchmark-subquery-recall-policy-v1','benchmark-subquery-rerank-clean-v1'),default='benchmark-v1',
        help='Select a frozen benchmark; v2 is relation-focused and writes separate outputs')
    parser.add_argument('--path-budget-comparison', action='store_true', help='Fixed real candidates, path quotas 0/800/1200, fresh paired answers')
    parser.add_argument('--extra-path-budget-comparison', action='store_true', help='Keep 6000 evidence bytes and add independent 0/800/1200 path bytes')
    parser.add_argument('--retrieval-comparison', action='store_true', help='Independent retrieval only; arms are defined by the selected benchmark')
    parser.add_argument('--prepare-only', action='store_true', help='Freeze the independent retrieval protocol without running models')
    parser.add_argument('--resume', type=Path, help='Upload saved independent retrieval results; never re-run models')
    args=parser.parse_args()
    if args.benchmark == 'benchmark-subquery-rerank-clean-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison or args.resume:
            parser.error('clean subquery rerank does not accept path budgets or resume')
        from papertech.subquery_rerank_clean_diagnostic import execute as execute_clean_rerank
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_clean_rerank(ROOT,prepare_only=args.prepare_only)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-subquery-recall-policy-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison or args.resume:
            parser.error('subquery recall policy replay does not accept path budgets or resume')
        from papertech.subquery_recall_policy import execute as execute_policy
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_policy(ROOT,prepare_only=args.prepare_only)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-subquery-recall-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('subquery recall diagnostic does not use graph paths')
        from papertech.subquery_recall_diagnostic import execute as execute_recall
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_recall(ROOT,prepare_only=args.prepare_only,resume=args.resume)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-query-router-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('query routing does not use path budgets')
        from papertech.query_router_diagnostic import execute as execute_router
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_router(ROOT,prepare_only=args.prepare_only,resume=args.resume)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-subquery-quality-v1':
        parser.error('v1 is a preserved interrupted diagnostic; use sync-evaluation-dataset.py for uploads, or v2 for new execution')
    if args.benchmark == 'benchmark-subquery-quality-v2':
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('subquery quality diagnosis does not retrieve or generate answers')
        from papertech.subquery_diagnostic import execute as execute_subqueries
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_subqueries(ROOT, prepare_only=args.prepare_only, resume=args.resume)
        raise SystemExit(0)
    if args.benchmark in ('benchmark-recall-width-v1','benchmark-resource-selection-v1','benchmark-recall-intervention-v1'):
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('staged retrieval diagnostics do not use graph path budget comparisons')
        from papertech.staged_retrieval_diagnostics import execute as execute_staged
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_staged(ROOT, args.benchmark, prepare_only=args.prepare_only, resume=args.resume)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-rerank-window-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('reranker input diagnosis uses fixed candidates only')
        from papertech.rerank_window_diagnostic import execute as execute_diagnostic
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_diagnostic(ROOT, prepare_only=args.prepare_only, resume=args.resume)
        raise SystemExit(0)
    if args.benchmark == 'benchmark-relation-holdout-v1':
        if args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('new-question benchmark is retrieval only')
        from papertech.relation_holdout_evaluation import execute as execute_holdout
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_holdout(ROOT, prepare_only=args.prepare_only, resume=args.resume)
        raise SystemExit(0)
    if args.retrieval_comparison:
        if args.benchmark != 'benchmark-retrieval-v1' or args.path_budget_comparison or args.extra_path_budget_comparison:
            parser.error('retrieval comparison requires benchmark-retrieval-v1 and no path comparison')
        from papertech.retrieval_comparison import execute as execute_retrieval
        with exclusive_lock(ROOT/'.cache/stage4-retrieval-eval.lock'):
            execute_retrieval(ROOT, prepare_only=args.prepare_only, resume=args.resume)
        raise SystemExit(0)
    if args.prepare_only or args.resume or args.benchmark == 'benchmark-retrieval-v1':
        parser.error('use --retrieval-comparison for the independent retrieval benchmark')
    if args.path_budget_comparison and args.extra_path_budget_comparison:
        parser.error('choose only one path budget comparison mode')
    if args.path_budget_comparison or args.extra_path_budget_comparison:
        if args.benchmark != 'benchmark-source-coverage-v1':
            parser.error('path quota comparison requires benchmark-source-coverage-v1')
        entry='eval-extra-path-budget.py' if args.extra_path_budget_comparison else 'eval-path-budget.py'
        spec=importlib.util.spec_from_file_location('path_budget_eval',ROOT/'scripts'/entry)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with exclusive_lock(ROOT/'.cache/path-budget-eval.lock'):module.execute()
    else:
        if args.benchmark == 'benchmark-source-coverage-v1':
            parser.error('use --path-budget-comparison for this diagnostic experiment')
        with exclusive_lock(ROOT/'.cache/stage4-eval.lock'):execute(args.benchmark)
