"""Re-retrieve only R11 using its offline router-fix replay; reuse all other rows."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import json
import time
import uuid

from .audit import Audit
from .cloud_embeddings import compatible,configured
from .corpus import load_corpus,valid_vector
from .evaluation_datasets import load_benchmark,write_json
from .evaluation_details import dataset_recorder
from .graph_store import GraphStore
from .local_models import vector_cache
from .providers import Providers
from .retrieval import normalize
from .settings import settings
from .subquery_diagnostic import sha
from .subquery_recall_diagnostic import (ARMS,RecallDataset,merge_queries,read,score,report as recall_report)

VERSION='benchmark-subquery-recall-router-fix-v1'
ROUTER_FIX='benchmark-query-router-fix-v1'
ROUTER_FIX_RUN='c22f0bb403e744139598cee5161cde3b'
SOURCE_RECALL_RUN='e158c260284d4273b8b55c9bd7a8b8f7'
SOURCE_RECALL_BASE=Path('artifacts/reports/stage-4')/'benchmark-subquery-recall-v1'/'runs'/SOURCE_RECALL_RUN
SOURCE_RECALL_BENCH='benchmark-subquery-recall-v1'


class RouterFixRecallDataset(RecallDataset):
    pass


def freeze(root):
    folder=root/'artifacts/eval/stage-4'/VERSION
    if (folder/'benchmark.json').exists():return load_benchmark(root,VERSION)[0]
    source,digest,_=load_benchmark(root,SOURCE_RECALL_BENCH)
    fixed,router_digest,_=load_benchmark(root,ROUTER_FIX)
    replay=read(root/'artifacts/reports/stage-4'/ROUTER_FIX/'runs'/ROUTER_FIX_RUN/'summary.json')
    if replay['status']!='completed':raise ValueError('router_replay_incomplete')
    plans=deepcopy(source['query_plans'])
    new=next(r for r in replay['results'] if r['case_id']=='R11' and r['arm']=='Local-LLM')
    plans['R11'].update(route=new['route'],subqueries=deepcopy(new['subqueries']),unresolved=deepcopy(new['unresolved']),reason=new['reason'],
        validation_errors=new['validation_errors'],valid=new['valid'],quote_normalized=new.get('quote_normalized',False),source_spans=deepcopy(new['source_spans']))
    bench=deepcopy(source);bench['version']=VERSION;bench['query_plans']=plans
    bench.update(parent_benchmark_sha256=digest,router_fix_benchmark_sha256=router_digest,
        dataset_description='24道已曝光跨论文开发题：仅用修复后的R11四条子查询重新召回；其余候选复用原运行。只测召回，不重排或生成。',
        prior_exposure='开发题和来源已使用；R11查询仅修复引用空白校验后离线重放；非泛化验收。',
        comparison=dict(mode='R11_router_fix_recall_replay',arms=list(ARMS)),
        controls=dict(source_recall_run=SOURCE_RECALL_RUN,router_replay_run=ROUTER_FIX_RUN,
            no_prompt_change=True,only_changed_case_retrieved='R11',other_cases='reuse original recall results byte-for-byte except replay metadata',
            R11_original='reuse previous original-question result and its frozen Q0 channel hits',
            R11_expanded='reuse Q0; freshly retrieve only the four fixed router subqueries using the same production indexes and compatible BGE',
            fulltext_top=20,dense_top=20,ann_query_k=100,merge=source['controls']['merge'],cap=40,
            reranking=False,answer_generation=False,evidence_selection=False),
        scoring=dict(source['scoring'],primary='R11 candidate source coverage before/after quote-normalization routing fix; remaining 23 cases are unchanged replay context',
            causal_limit='R11 is one diagnostic item; source support pools are frozen and non-exhaustive; no rerank or answer quality claim.'),
        additional_inputs_sha256={
            'artifacts/eval/stage-4/benchmark-query-router-fix-v1/benchmark.json':sha(root/'artifacts/eval/stage-4'/ROUTER_FIX/'benchmark.json'),
            f'artifacts/reports/stage-4/{ROUTER_FIX}/runs/{ROUTER_FIX_RUN}/summary.json':sha(root/'artifacts/reports/stage-4'/ROUTER_FIX/'runs'/ROUTER_FIX_RUN/'summary.json'),
            f'artifacts/reports/stage-4/{SOURCE_RECALL_BENCH}/runs/{SOURCE_RECALL_RUN}/summary.json':sha(root/SOURCE_RECALL_BASE/'summary.json')},
        code_sha256={p:sha(root/p) for p in ('src/papertech/router_fix_recall.py','src/papertech/subquery_recall_diagnostic.py',
            'src/papertech/query_router_diagnostic.py','src/papertech/graph_store.py','src/papertech/retrieval.py',
            'scripts/eval-stage4.py','src/papertech/evaluation_details.py')})
    write_json(folder/'benchmark.json',bench);(folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    return bench


def execute(root):
    bench=freeze(root);rec=RouterFixRecallDataset(root,VERSION);cfg=settings(root)
    try:
        for p,d in {**bench['code_sha256'],**bench['inputs_sha256'],**bench['additional_inputs_sha256']}.items():
            if sha(root/p)!=d:raise ValueError('frozen_input_or_code_changed:'+p)
        # Dataset readback must pass before requesting even the embedding batch.
        rec.sync_dataset()
        previous=read(root/SOURCE_RECALL_BASE/'summary.json')
        corpus,_,chunks=load_corpus(root);chunkmap={c['chunk_id']:c for c in chunks}
        meta,_=vector_cache(root)
        if corpus!=bench['corpus_id'] or not configured(cfg) or not compatible(root,cfg,meta['model_id']):
            raise ValueError('corpus_or_embedding_compatibility_failed')
        store=GraphStore(cfg,bench['corpus_id'],meta['model_id']);index=store.inspect()
        if index['counts']!=[dict(chunks=980,papers=14)] or any(x['state']!='ONLINE' for x in index['indexes']):
            store.close();raise ValueError('index_not_ready')
        run_id=uuid.uuid4().hex;folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/run_id;folder.mkdir(parents=True)
        summary=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=rec.digest,status='running',
            started=datetime.now(timezone.utc).isoformat(),results=[],source_run=SOURCE_RECALL_RUN,
            retrieval_scope='only R11 fixed subqueries re-retrieved; all other results reused')
        write_json(folder/'index-snapshot.json',index)
        old={ (r['case_id'],r['arm']):r for r in previous['results'] }
        # Replay all non-target rows and both unchanged original-question rows.
        for key,row in old.items():
            copied=deepcopy(row);copied.update(replayed=True,replayed_from=SOURCE_RECALL_RUN)
            if key==('R11','Expanded'):continue
            summary['results'].append(copied)
        router=bench['query_plans']['R11'];case=next(c for c in bench['cases'] if c['id']=='R11')
        q0=deepcopy(next(q for q in old[('R11','Expanded')]['queries'] if q['id']=='Q0'))
        new_queries=[dict(id=q['id'],text=q['text']) for q in router['subqueries']]
        # The only paid/networked model operation is one small, auditable embedding batch.
        audit=Audit(root);provider=Providers(cfg,audit);request_id=audit.start('[router-fix recall: R11 subquery embedding]')
        vectors=read(root/'.cache/retrieval-comparison/12b6c032bb3f4992944a1148ddc92bce/query-vectors.json')
        normalized=[normalize(q['text']) for q in new_queries]
        unique=list(dict.fromkeys(x for x in normalized if x not in vectors))
        start=time.monotonic();embed_started=datetime.now(timezone.utc).isoformat()
        if unique:
            outputs=provider.embedding(request_id,unique)
            for text,vector in zip(unique,outputs):vectors[text]=valid_vector(vector)
        embed_seconds=time.monotonic()-start
        calls=[dict(r) for r in audit.conn.execute('SELECT provider,attempt,started,finished,seconds,status,http_status,usage FROM calls WHERE request_id=?',(request_id,))]
        write_json(root/'.cache/subquery-recall-router-fix'/run_id/'query-vectors.json',vectors)
        summary['embedding']=dict(new_text_count=len(unique),calls=calls,seconds=embed_seconds,started=embed_started,
            finished=datetime.now(timezone.utc).isoformat(),token_status='provider-reported only; null means unavailable',
            original_vectors_reused=True,model_id=meta['model_id'],compatibility_gate=True)
        queries=[q0];units={u:bench['units'][u] for u in case['units']}
        try:
            for q,text in zip(new_queries,normalized):
                t0=time.monotonic();started=datetime.now(timezone.utc).isoformat()
                full,dense=store.retrieve(text,vectors[text])
                queries.append(dict(id=q['id'],text=q['text'],normalized=text,channels=dict(fulltext=full,dense=dense),
                    started=started,finished=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-t0))
            candidates=merge_queries(queries)
            metrics,facts=score(candidates,case,units,chunkmap)
            oldrow=old[('R11','Expanded')]
            row=dict(case_id='R11',question=case['question'],category='cross',arm='Expanded',status='ok',route=router['route'],
                query_plan=router,queries=queries,candidates=candidates,metrics=metrics,facts=facts,
                started=queries[-1]['started'],finished=datetime.now(timezone.utc).isoformat(),
                retrieval_seconds=sum(q.get('seconds',0) for q in queries[1:]),
                embedding_text_count=len(unique),embedding_call_scope='R11 only; four fixed subqueries, one shared batch; original vector reused',
                rerank_pairs=0,generation_calls=0,replayed=False,replay_baseline=oldrow['metrics'],
                retrieval_change='reused Q0; freshly queried four restored subqueries; no other query plans changed')
            summary['results'].append(row)
            summary['results'].sort(key=lambda x:(x['case_id'],ARMS.index(x['arm'])))
            summary.update(status='completed',finished=datetime.now(timezone.utc).isoformat())
            write_json(folder/'summary.json',summary)
            write_json(folder/'r11-new-retrieval.json',row)
            # A deterministic, machine-checkable route diff proves other plans are unchanged.
            unchanged=[]
            for cid in [f'R{i:02d}' for i in range(1,25) if i!=11]:
                unchanged.append(dict(case_id=cid,query_plan_unchanged=bench['query_plans'][cid]==previous_plan(root,cid),retrieval_replayed=True))
            diff=dict(router_changes=read(root/'artifacts/eval/stage-4'/ROUTER_FIX/'route-diff.json')['changes'],
                only_retrieved_case='R11',other_cases=unchanged,
                r11_before=oldrow['metrics'],r11_after=metrics,r11_source_changes=source_delta(oldrow['facts'],facts))
            write_json(folder/'route-and-recall-diff.json',diff)
            from .subquery_recall_diagnostic import report as report_recall
            report_recall(rec,summary,folder)
            status=rec.sync_run(folder/'summary.json');summary['langsmith']=status;write_json(folder/'summary.json',summary)
            report_recall(rec,summary,folder)
            print(json.dumps(dict(run_id=run_id,r11_before=oldrow['metrics'],r11_after=metrics,langsmith=status),ensure_ascii=False),flush=True)
        finally:
            provider.client.close();audit.finish(request_id,dict(status='ok',retrieval_summary=dict(r11_query_count=4)));audit.close();store.close()
    finally:rec.close()


def previous_plan(root,cid):
    summary=read(root/SOURCE_RECALL_BASE/'summary.json')
    return next(r for r in summary['results'] if r['case_id']==cid and r['arm']=='Expanded')['query_plan']


def source_delta(before,after):
    left={x['unit_id']:x for x in before};right={x['unit_id']:x for x in after}
    return [dict(unit_id=k,before=left[k]['reason'],after=right[k]['reason'],added=right[k]['retained'] and not left[k]['retained'],removed=left[k]['retained'] and not right[k]['retained']) for k in right if left[k]['retained']!=right[k]['retained'] or left[k]['union_hit']!=right[k]['union_hit']]
