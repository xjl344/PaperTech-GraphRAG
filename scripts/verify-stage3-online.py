"""Three functional acceptance cases, not the stage-4 retrieval benchmark.

Uses configured real providers. Saves every result before remote verification.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.ingest import atomic_json
from papertech.settings import settings
from papertech.workflow import Workflow
from papertech.local_models import run_worker
from papertech.rerank_service import close_workers

CASES=[
    dict(id='tog2-datasets',question='ToG-2（Think-on-Graph 2.0）在哪些数据集上进行了评估？请给出原文证据，不要把任务和数据集混为一谈。',
         checks=['real cloud embedding','approved bounded graph paths','GPU reranking','grounded generation paths','valid citations']),
    dict(id='tog-comparison',question='比较 ToG 与 ToG-2 的检索方式和评估数据集。分别引用两篇论文；如果缺少一致的实验条件，请说明能否直接判定谁更好。',
         checks=['independent evidence from both papers','comparison limitations','no unsupported winner']),
    dict(id='hipporag',question='HippoRAG 如何利用 Personalized PageRank 做检索？图路径能证明什么，不能证明什么？请引用原文。',
         checks=['actual generated answer','evidence supports answer','associations are not causal claims']),
]


class GPUSampler:
    def __init__(self):
        self.stop=threading.Event(); self.rows=[]; self.errors=[]
        self.thread=threading.Thread(target=self.run,daemon=True)
    def run(self):
        while not self.stop.is_set():
            try:
                r=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu',
                                  '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5,
                                 creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if r.returncode==0:
                    values=[int(v.strip()) for v in r.stdout.splitlines()[0].split(',')]
                    self.rows.append(dict(time=time.time(),used_mib=values[0],total_mib=values[1],gpu_util_percent=values[2]))
                else:self.errors.append('nvidia_smi_failed')
            except Exception as exc:self.errors.append(type(exc).__name__)
            self.stop.wait(1)
    def __enter__(self):self.thread.start(); return self
    def __exit__(self,*args):self.stop.set(); self.thread.join(timeout=6)


def verify_remote(workflow, results):
    live=workflow.audit.live
    live.flush()
    ids={workflow.audit.live_requests[r['request_id']] for r in results}
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
            update=live.conn.execute("SELECT payload FROM events WHERE span_id=? AND operation='update' ORDER BY seq DESC LIMIT 1",(row['id'],)).fetchone()
            payload=json.loads(update[0]) if update else {}
            usage_ok=None
            if 'prompt_tokens' in payload:
                usage_ok=(remote.prompt_tokens==payload['prompt_tokens'] and remote.completion_tokens==payload['completion_tokens'])
            checks.append(dict(id=row['id'],name=row['name'],remote_finished=remote.end_time is not None,native_usage_matches=usage_ok))
        except Exception as exc:
            checks.append(dict(id=row['id'],error=type(exc).__name__,remote_finished=False))
    pending=sum(1 for r in live.conn.execute("SELECT span_id FROM events WHERE status='pending'") if r[0] in ids)
    return dict(verified=pending==0 and bool(checks) and all(c['remote_finished'] and c.get('native_usage_matches') is not False for c in checks),
                pending=pending,span_count=len(checks),spans=checks)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',choices=[c['id'] for c in CASES],action='append',default=None)
    args=parser.parse_args()
    destination=ROOT/'artifacts/reports/stage-3/online/runs'/uuid.uuid4().hex
    destination.mkdir(parents=True)
    selected=[c for c in CASES if not args.case or c['id'] in args.case]
    cfg=settings(ROOT)
    atomic_json(destination/'acceptance-contract.json',dict(scope='stage3 functional acceptance, not stage4 benchmark',
        quotation_protocol='source-choice-v1',model=cfg.get('DEEPSEEK_MODEL'),
        query_provider=cfg.get('CLOUD_BGE_PROVIDER'),query_model=cfg.get('CLOUD_BGE_MODEL'),
        cases=selected,limits=dict(candidates=40,evidence=8,context_bytes=6000,hops=2,per_node=8,paths=40),
        semantic_review='Codex delegated review, not an independent human or LLM judge score'))
    workflow=Workflow(ROOT,cfg)
    results=[]; report=dict(directory=str(destination),results=results)
    print(json.dumps(dict(directory=str(destination),cases=len(selected)),ensure_ascii=False),flush=True)
    try:
        with GPUSampler() as sampler:
            warm_id=workflow.audit.start('[GPU reranker warm-up metadata]')
            try:
                cold=workflow.audit.stage(warm_id,'gpu_warmup',lambda:run_worker(ROOT,cfg,'rerank',
                    [dict(text='HippoRAG uses personalized PageRank for retrieval.')],query='HippoRAG retrieval',timeout=180))
                cold.pop('outputs',None)
                workflow.audit.finish(warm_id,dict(status='completed',retrieval_summary=dict(reranker=cold)))
                report['prewarm']=cold
                atomic_json(destination/'prewarm.json',cold)
            except Exception as exc:
                workflow.audit.finish(warm_id,dict(status='error',errors=[type(exc).__name__]))
                raise
            for case in selected:
                started=time.monotonic()
                result=workflow.ask(case['question'])
                result.update(case_id=case['id'],question=case['question'],wall_seconds=time.monotonic()-started)
                result['provider_calls']=[dict(r) for r in workflow.audit.conn.execute(
                    'SELECT provider,attempt,seconds,status,http_status,usage FROM calls WHERE request_id=? ORDER BY started',(result['request_id'],))]
                summary=result['retrieval_summary'] or {}
                reranker=summary.get('reranker')
                result['functional_acceptance']=(result['status'] in ('ok','partial') and bool(result['citations'])
                    and summary.get('dense_hits',0)>0 and isinstance(reranker,dict) and reranker.get('device')=='cuda'
                    and any(c['provider']=='cloudflare' and c['http_status']==200 for c in result['provider_calls'])
                    and any(c['provider']=='deepseek' and c['http_status']==200 for c in result['provider_calls'])
                    and not result['errors']
                    and (case['id']!='tog2-datasets' or bool(result['generation_paths']))
                    and (case['id']!='tog-comparison' or not summary.get('missing_comparison_groups')))
                atomic_json(destination/(case['id']+'.json'),result)
                results.append(result)
                atomic_json(destination/'summary.json',report)
                print(json.dumps(dict(case=case['id'],status=result['status'],errors=result['errors'],
                    evidence=len(result['evidence']),paths=len(result['generation_paths']),wall_seconds=result['wall_seconds'],
                    trace_url=result['trace_url']),ensure_ascii=False),flush=True)
        report['gpu_samples']=dict(samples=sampler.rows,errors=sampler.errors,
            peak_global_used_mib=max((r['used_mib'] for r in sampler.rows),default=None),
            meaning='whole device snapshot every ~1s, includes other applications; not process-only memory')
        atomic_json(destination/'gpu-samples.json',report['gpu_samples'])
        report['remote_verification']=verify_remote(workflow,results)
        atomic_json(destination/'summary.json',report)
        atomic_json(ROOT/'artifacts/reports/stage-3/online/latest.json',dict(directory=str(destination)))
        print(json.dumps(dict(remote_verified=report['remote_verification']['verified'],report=str(destination/'summary.json'))),flush=True)
    finally:
        workflow.close(); close_workers()
    return 0 if results and all(r['functional_acceptance'] for r in results) and report['remote_verification']['verified'] else 1


if __name__=='__main__':sys.exit(main())
