"""Stage 2 CLI. Cloud fields remain blank until explicitly configured by the user."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

from papertech.audit import Audit
from papertech.corpus import load_corpus
from papertech.ingest import atomic_json, exclusive_lock
from papertech.local_models import run_worker, vector_cache
from papertech.settings import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task',choices=['embed','index','inspect','ask','chat','compatibility','traces','reset-billing-block'])
    parser.add_argument('--question',default='')
    parser.add_argument('--backend',choices=['neo4j','offline'],default='neo4j')
    parser.add_argument('--query-mode',choices=['auto','cloud','local','none'],default=None)
    parser.add_argument('--skip-rerank',action='store_true')
    parser.add_argument('--query-planner',action='store_true',help='已默认开启（保留兼容参数）')
    parser.add_argument('--no-query-planner',action='store_true',help='关闭云端查询规划器')
    parser.add_argument('--no-fast-path',action='store_true',help='关闭简单单论文问题快速通道')
    parser.add_argument('--premise-check',action='store_true',help='已默认开启（保留兼容参数）')
    parser.add_argument('--no-premise-check',action='store_true',help='关闭前提核验')
    parser.add_argument('--no-graph-cards',action='store_true',help='关闭 QA-Graph 与 14 篇方法卡导航')
    parser.add_argument('--sync-traces',action='store_true',help='同步阻塞上传 LangSmith Trace（默认后台异步上传）')
    parser.add_argument('--legacy-mode',action='store_true',help='回退旧版 Workflow 默认配置')
    parser.add_argument('--sample',type=int,default=0)
    args = parser.parse_args()
    cfg = settings(ROOT)
    report_dir = ROOT/'artifacts/reports/stage-2'
    report_dir.mkdir(parents=True,exist_ok=True)
    if args.task in ('embed','index','inspect','compatibility'):
        corpus_id,papers,chunks = load_corpus(ROOT)
    if args.task == 'embed':
        with exclusive_lock(ROOT/'.cache/embed.lock'):
            result = run_worker(ROOT,cfg,'build',chunks[:args.sample] if args.sample>0 else chunks,timeout=7200)
            result.pop('outputs',None)
            result.update(corpus_id=corpus_id,cloud_calls=0)
            atomic_json(report_dir/('embedding-sample.json' if args.sample>0 else 'embedding.json'),result)
    elif args.task in ('index','inspect'):
        from papertech.graph_store import GraphStore
        metadata,vectors = vector_cache(ROOT)
        graph = GraphStore(cfg,corpus_id)
        index_audit = Audit(ROOT) if args.task=='index' else None
        index_request = index_audit.start('[index metadata] corpus='+corpus_id) if index_audit else None
        try:
            if args.task == 'index':
                with exclusive_lock(ROOT/'.cache/index.lock'):
                    result = index_audit.stage(index_request,'index',lambda:graph.build(papers,chunks,metadata,vectors))
                    index_audit.finish(index_request,dict(status='completed',**result))
                    index_audit.queue_trace(index_request)
            else:
                result = graph.inspect()
            atomic_json(report_dir/('index.json' if args.task=='index' else 'index-inspect.json'),result)
        except Exception as exc:
            if index_audit:
                index_audit.finish(index_request,dict(status='write_failed_or_unknown',error=type(exc).__name__))
            raise
        finally:
            graph.close()
            if index_audit:
                index_audit.close()
    elif args.task in ('ask','chat'):
        from papertech.workflow import Workflow
        if args.legacy_mode:
            workflow = Workflow(ROOT,cfg,args.backend,args.query_mode,not args.skip_rerank,
                                query_planner=args.query_planner,premise_check=args.premise_check)
        else:
            workflow = Workflow.for_workbench(
                ROOT, cfg, backend=args.backend, query_mode=args.query_mode, rerank=not args.skip_rerank,
                query_planner=not args.no_query_planner, premise_check=not args.no_premise_check,
                use_graph_and_cards=not args.no_graph_cards, async_trace_flush=not args.sync_traces,
                planner_fast_path=not args.no_fast_path,
            )
        try:
            if args.task=='chat':
                if not args.skip_rerank:
                    warm_id=workflow.audit.start('[interactive reranker warm-up metadata]')
                    try:
                        warm=workflow.audit.stage(warm_id,'gpu_warmup',lambda:run_worker(ROOT,cfg,'rerank',
                            [dict(text='Retrieval uses source evidence.')],query='source evidence',timeout=180))
                        warm.pop('outputs',None)
                        workflow.audit.finish(warm_id,dict(status='completed',retrieval_summary=dict(reranker=warm)))
                    except Exception as exc:
                        workflow.audit.finish(warm_id,dict(status='error',errors=[type(exc).__name__]))
                        print('重排预热失败；本会话跳过重排并记录降级。')
                        workflow.rerank_enabled=False
                print('会话已就绪；输入问题，输入 /exit 或按 Ctrl+Z 结束。')
                while True:
                    try:question=input('> ')
                    except EOFError:break
                    if question.strip()=='/exit':break
                    result=workflow.ask(question)
                    atomic_json(report_dir/'requests'/f"{result['request_id']}.json",result)
                    print(json.dumps(result,ensure_ascii=False,indent=2))
                return 0
            result = workflow.ask(args.question)
            atomic_json(report_dir/'requests'/f"{result['request_id']}.json",result)
        finally:
            workflow.close()
    elif args.task == 'compatibility':
        from papertech.providers import Providers
        from papertech.cloud_embeddings import check_compatibility
        audit = Audit(ROOT)
        rid = audit.start('[embedding compatibility diagnostic]')
        provider = Providers(cfg,audit)
        try:
            result = audit.stage(rid, 'cloud_embedding_compatibility',
                                 lambda:check_compatibility(ROOT,cfg,provider,rid))
            audit.finish(rid,dict(result,status='completed' if result['passed'] else 'pending'))
            result['request_id'] = rid
            result['live_trace_id'] = audit.live_requests.get(rid)
            result['trace_url'] = audit.live.url(result['live_trace_id'])
            audit.queue_trace(rid)
            atomic_json(report_dir/'cloud-compatibility.json',result)
        finally:
            provider.client.close()
            audit.close()
    elif args.task == 'traces':
        from papertech.traces import flush_traces
        audit = Audit(ROOT)
        try:
            result = flush_traces(audit,cfg)
        finally:
            audit.close()
    else:
        audit = Audit(ROOT)
        audit.conn.execute("DELETE FROM blocks WHERE provider IN ('deepseek','deepinfra','cloudflare')")
        audit.conn.commit()
        audit.close()
        result = dict(status='manual_billing_block_reset')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.task == 'compatibility' and not result['passed']:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
