"""Offline candidate-pool policy and local reranker comparison for frozen queries."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import html
import json
import math
from pathlib import Path
import statistics
import time
import uuid

from .corpus import load_corpus
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, clean, source_detail
from .local_models import run_worker
from .settings import settings
from .subquery_diagnostic import sha
from .subquery_recall_diagnostic import read, score as coverage_score

VERSION = 'benchmark-subquery-recall-policy-v1'
BASE = Path('artifacts/reports/stage-4/benchmark-subquery-recall-v1/runs/e158c260284d4273b8b55c9bd7a8b8f7')
SOURCE_BENCH = 'benchmark-subquery-recall-v1'
SOURCE_RUN = 'e158c260284d4273b8b55c9bd7a8b8f7'
QUOTAS = (6, 9, 13, 20)
ARMS = tuple([f'Quota-N{n}' for n in QUOTAS] + ['RoundRobin-40', 'QueryHits-BestRank-40', 'Rerank-Original-Union40', 'Rerank-OwnerSubquery-Union40'])


def all_candidates(queries):
    """Query-major stable union, retaining every channel/rank discovery."""
    items = {}; order = []
    for q in queries:
        for channel in ('fulltext', 'dense'):
            for rank, hit in enumerate(q['channels'][channel], 1):
                cid = hit['chunk_id']
                if cid not in items:
                    items[cid] = dict(chunk_id=cid, first_discovery=len(order)+1, discoveries=[], found_by=[]); order.append(cid)
                item = items[cid]
                item['discoveries'].append(dict(query_id=q['id'], channel=channel, rank=rank, score=hit['score']))
                if q['id'] not in item['found_by']: item['found_by'].append(q['id'])
    return [items[cid] for cid in order]


def rank_query_hits(candidates, cap=40):
    def best(x): return min(d['rank'] for d in x['discoveries'])
    ordered = sorted(candidates, key=lambda x: (-len(set(x['found_by'])), best(x), x['first_discovery']))
    return [dict(x, policy_rank=i, retained=i <= cap) for i, x in enumerate(ordered, 1)]


def quota_pool(candidates, n, cap=40):
    if n not in QUOTAS: raise ValueError('unsupported_quota')
    reserved = [x for x in candidates if any(d['rank'] <= n for d in x['discoveries'])]
    reserved_ids = {x['chunk_id'] for x in reserved}
    # If the guarantees exceed the global budget, prefer repeated query support,
    # then the best rank, with first-discovery order as a deterministic tie-break.
    def priority(x):
        return (-len(set(x['found_by'])), min(d['rank'] for d in x['discoveries']), x['first_discovery'])
    selected = sorted(reserved, key=priority)[:cap]
    selected_ids = {x['chunk_id'] for x in selected}
    fill = sorted((x for x in candidates if x['chunk_id'] not in selected_ids), key=priority)
    selected.extend(fill[:max(0, cap-len(selected))])
    rank_by_id = {x['chunk_id']:i for i,x in enumerate(selected,1)}
    return [dict(x, quota_n=n, quota_reserved=x['chunk_id'] in reserved_ids,
        policy_rank=rank_by_id.get(x['chunk_id']), retained=x['chunk_id'] in rank_by_id) for x in candidates]


def score_pool(candidates, case, units, chunks):
    metrics, facts = coverage_score(candidates, case, units, chunks)
    retained={x['chunk_id'] for x in candidates if x.get('retained')}
    for fact in facts:
        fact['retained'] = bool(retained & set(fact['known_support_chunks']))
        fact['reason'] = 'retained' if fact['retained'] else 'candidate_cap' if fact['union_hit'] else 'upstream_missing'
    n=len(facts); metrics['cap40_coverage']=sum(f['retained'] for f in facts)/n
    metrics['cap40_all']=all(f['retained'] for f in facts)
    metrics['quota_reserved_count']=sum(bool(x.get('quota_reserved')) for x in candidates)
    metrics['selected_count']=len(retained)
    metrics['outside_quota_fill_count']=sum(x.get('retained',False) and not x.get('quota_reserved',False) for x in candidates)
    return metrics,facts


def freeze(root):
    folder=root/'artifacts/eval/stage-4'/VERSION
    if (folder/'runs').exists() and any((folder/'runs').iterdir()): return load_benchmark(root,VERSION)[0]
    parent,digest,_=load_benchmark(root,SOURCE_BENCH)
    summary=read(root/BASE/'summary.json')
    if summary['status']!='completed' or len(summary['results'])!=48: raise ValueError('source_run_incomplete')
    bench=deepcopy(parent); bench['version']=VERSION
    bench['source_run_id']=SOURCE_RUN; bench['source_benchmark_sha256']=digest
    bench['arms']=list(ARMS); bench['comparison']=dict(mode='query_pool_policy_and_reranking',arms=list(ARMS),generation=False)
    bench['dataset_description']='24道已曝光跨论文开发题：子查询配额、候选排序修正及固定候选的本地重排对照；不生成答案。'
    bench['prior_exposure']='题目和来源已用于前轮开发；本轮是离线策略诊断，不是泛化验收。'
    bench['controls']=dict(source_summary_sha256=sha(root/BASE/'summary.json'),quotas=list(QUOTAS),candidate_cap=40,
        quota='each query × each retrieval channel reserves top N; duplicate chunk reserved once; if reserved pool >40, retain sorted by distinct query count, best per-path rank, stable first-discovery; then fill from outside quota by same order',
        query_hit_sort='sort full union by number of distinct query IDs descending, best fulltext/dense rank ascending, stable first-discovery; one-based rank',
        reranking='same complete expanded union for both reranker arms; original question scores every candidate; owner arm scores each chunk against each subquery that found it, uses maximum score; if no subquery found it, use original-question score',
        rerank_selection='report top40 by score only; no threshold, diversity or evidence assembly',
        reranker_pair_max_tokens=1024,reranker_truncation=True,generation=False,cloud_calls=False,
        ownership='discovery provenance defines query ownership; it does not establish paper ownership or semantic relevance')
    bench['scoring']=dict(primary='necessary-source coverage among selected 40; separately report quota pools and all-union coverage',
        source='unit covered if any frozen known_support_chunks is present',
        paired='question-level win/tie/loss and per-unit additions/removals; score ties preserve stable first-discovery order',
        semantic='no generated answer; not answer accuracy',
        costs='candidate stages use saved hits only; local GPU pairs and seconds are reported for reranking; no query embedding or paid provider')
    bench['inputs_sha256']={str(BASE/'summary.json'):sha(root/BASE/'summary.json'),
        'artifacts/eval/stage-4/benchmark-subquery-recall-v1/benchmark.json':sha(root/'artifacts/eval/stage-4/benchmark-subquery-recall-v1/benchmark.json')}
    bench['code_sha256']={p:sha(root/p) for p in ('src/papertech/subquery_recall_policy.py','scripts/eval-stage4.py','src/papertech/evaluation_details.py','src/papertech/rerank_runtime.py','src/papertech/rerank_service.py')}
    write_json(folder/'benchmark.json',bench);(folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    for p in bench['code_sha256']:
        dest=folder/'runtime-snapshot'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((root/p).read_bytes())
    return bench


class PolicyDataset(DetailedEvaluationDataset):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.payload['description']=self.bench['dataset_description']
        for e in self.payload['examples']:
            e['outputs']['evaluation_config']['planned_output']='仅候选池覆盖与固定候选本地重排；不生成答案'
            e['outputs']['result_display'].update(location='8个候选策略 Experiment',fields=['查询通道与逐路名次',
                'N=6/9/13/20配额保留与补位','40条合并排名与覆盖','原问题/归属子查询重排分数和名次',
                '逐来源得失、成本、Trace'])
            write_json(self.directory/'cases'/(e['metadata']['case_id']+'.json'),e)
        write_json(self.directory/'langsmith-dataset.json',self.payload)

    def sync_run(self,summary_path):
        summary=read(summary_path);path=Path(summary_path);folder=path.parent
        if summary['benchmark_sha256']!=self.digest: raise ValueError('benchmark_mismatch')
        dataset=self.sync_dataset(); payloads=[]
        expected={(c['id'],arm) for c in self.bench['cases'] for arm in ARMS}
        keys=[(r['case_id'],r['arm']) for r in summary['results']]
        if len(keys)!=len(set(keys)) or (summary['status']=='completed' and set(keys)!=expected): raise ValueError('pair_set_mismatch')
        bycase={c['id']:c for c in self.bench['cases']}
        for row in summary['results']:
            output=clean(deepcopy(row));output['candidate_source_excerpts']=[source_detail(self.chunks[x['chunk_id']]) for x in row.get('candidates',[])]
            output['rerank_source_excerpts']=[source_detail(self.chunks[x['chunk_id']]) for x in row.get('ranked_candidates',[])]
            output['per_case_differences']=summary.get('paired',{}).get(row['case_id'],{}).get(row['arm'])
            output.update(generation='not_run',answer_accuracy='not_assessed',evidence_selection='not_run')
            metrics=deepcopy(row['metrics']);metrics.update(candidate_count=len(row.get('candidates',[])),
                rerank_pairs=row.get('compute',{}).get('pairs',0),rerank_seconds=row.get('compute',{}).get('inference_seconds',0))
            payloads.append(dict(id=stable_id(self.digest,summary['run_id'],row['case_id'],row['arm']),name='subquery-recall-policy',
                run_type='chain',inputs=dict(question=row['question']),outputs=output,
                reference_example_id=stable_id(self.digest,row['case_id']),start_time=row['started'],end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=VERSION,arm=row['arm'],case_id=row['case_id'],source_run_id=SOURCE_RUN)),
                _arm=row['arm'],_metrics=metrics))
        write_json(folder/'langsmith-experiments.json',dict(runs=payloads))
        experiments=[]
        for arm in ARMS:
            group={p['id']:p for p in payloads if p['_arm']==arm};name=f'papertech-{VERSION}-{summary["run_id"][:12]}-{arm}'
            project=self.client.create_project(name,reference_dataset_id=dataset.id,upsert=True,
                description=self.bench['dataset_description'],metadata=dict(arm=arm,benchmark_sha256=self.digest))
            found={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            if set(found)-set(group) or any(r.outputs!=group[rid]['outputs'] for rid,r in found.items()):raise ValueError('remote_modified')
            def upload(p):
                obj={k:v for k,v in p.items() if not k.startswith('_')}
                obj['start_time']=datetime.fromisoformat(obj['start_time']);obj['end_time']=datetime.fromisoformat(obj['end_time'])
                self.client.create_run(project_name=name,**obj)
            with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(upload,[p for rid,p in group.items() if rid not in found]))
            jobs=[dict(run_id=p['id'],key=k,score=float(v),feedback_id=stable_id(p['id'],k),session_id=project.id,
                stop_after_attempt=1,comment='来源覆盖/重排分数和计算成本；不是答案准确率。') for p in group.values() for k,v in p['_metrics'].items() if isinstance(v,(int,float)) and math.isfinite(v)]
            existing={str(f.id):f for f in self.client.list_feedback(run_ids=list(group))}
            with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:self.client.create_feedback(**j),[j for j in jobs if j['feedback_id'] not in existing]))
            actual={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(group))}
            if set(actual)!=set(group) or any(r.outputs!=group[rid]['outputs'] or str(r.reference_example_id)!=group[rid]['reference_example_id'] for rid,r in actual.items()):raise ValueError('experiment_readback_mismatch')
            if any(j['feedback_id'] not in feedback or not math.isclose(feedback[j['feedback_id']].score,j['score'],abs_tol=.000051) for j in jobs):raise ValueError('feedback_readback_mismatch')
            experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(actual),feedback_verified=len(jobs)))
            self.client.update_project(project.id,end_time=datetime.now(timezone.utc))
        self.status.update(status='experiments_verified',experiments=experiments,
            comparison_url=dataset.url+'/compare?selectedSessions='+','.join(x['project_id'] for x in experiments))
        write_json(folder/'langsmith-status.json',self.status);write_json(self.status_path,self.status)
        return self.status


def pair(summary):
    grouped={}
    for r in summary['results']:grouped.setdefault(r['case_id'],{})[r['arm']]=r
    out={}
    metric_by_arm={arm:('cap40_coverage' if arm.startswith('Quota-') or arm in ('RoundRobin-40','QueryHits-BestRank-40') else 'top40_coverage') for arm in ARMS}
    for cid,g in grouped.items():
        out[cid]={}
        for arm,row in g.items():
            metric=metric_by_arm[arm];value=row['metrics'][metric]
            baseline=g.get('RoundRobin-40')
            if baseline is None:continue
            old=baseline['metrics']['cap40_coverage'];before={f['unit_id'] for f in baseline['facts'] if f['retained']}
            after={f['unit_id'] for f in row['facts'] if f['retained']}
            d=value-old
            out[cid][arm]=dict(metric=metric,delta_vs_round_robin=d,
                outcome='win' if d>1e-12 else 'loss' if d< -1e-12 else 'tie',added=sorted(after-before),removed=sorted(before-after))
    return out


def report(recorder,summary,folder):
    stats={}
    for arm in ARMS:
        rows=[r for r in summary['results'] if r['arm']==arm]
        if not rows:continue
        key='cap40_coverage' if arm.startswith('Quota-') or arm in ('RoundRobin-40','QueryHits-BestRank-40') else 'top40_coverage'
        stats[arm]=dict(count=len(rows),coverage=sum(r['metrics'][key] for r in rows)/len(rows),
            source_hits=sum(f['retained'] for r in rows for f in r['facts']),
            source_total=sum(len(r['facts']) for r in rows),all_sources=sum(r['metrics'].get('cap40_all',r['metrics'].get('top40_all',False)) for r in rows),
            avg_candidate_union=sum(len(r.get('candidates',[])) for r in rows)/len(rows),
            avg_selected=sum(r['metrics'].get('selected_count',sum(f['retained'] for f in r['facts'])) for r in rows)/len(rows),
            rerank_pairs=sum(r.get('compute',{}).get('pairs',0) for r in rows),
            inference_seconds=sum(r.get('compute',{}).get('inference_seconds',0) for r in rows),
            wall_seconds=sum(r.get('compute',{}).get('wall_seconds',0) for r in rows),
            quota_reserved=sum(r['metrics'].get('quota_reserved_count',0) for r in rows),
            outside_quota_fill=sum(r['metrics'].get('outside_quota_fill_count',0) for r in rows))
    summary['paired']=pair(summary);summary['aggregate']=stats
    write_json(folder/'summary.json',summary);write_json(folder/'aggregate.json',dict(aggregate=stats,paired=summary['paired']))
    # Full per-question pages; report retains all candidate and reranker score rows locally.
    by_route={}
    for route in sorted({r['route'] for r in summary['results']}):
        by_route[route]={arm:dict(count=len(rs),coverage=sum(r['metrics']['cap40_coverage' if arm.startswith('Quota-') or arm in ('RoundRobin-40','QueryHits-BestRank-40') else 'top40_coverage'] for r in rs)/len(rs) if rs else None,
            source_hits=sum(f['retained'] for r in rs for f in r['facts']),source_total=sum(len(r['facts']) for r in rs))
            for arm in ARMS if (rs:=[r for r in summary['results'] if r['route']==route and r['arm']==arm])}
    write_json(folder/'by-route.json',by_route)
    colors=['#2563eb','#059669','#9333ea','#d97706','#0f766e','#be123c','#475569','#a16207']
    bars=[]
    for i,arm in enumerate(ARMS):
        if arm not in stats:continue
        y=30+i*42;value=stats[arm]['coverage']
        bars.append(f'<text x="4" y="{y+18}">{html.escape(arm)}</text><rect x="265" y="{y}" width="{value*480:.2f}" height="24" fill="{colors[i%len(colors)]}"/><text x="{270+value*480:.2f}" y="{y+18}">{value:.1%}</text>')
    chart='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 390" font-size="14">'+''.join(bars)+'</svg>'
    write_json(folder/'by-route.json',by_route)
    esc=html.escape;lines=['<!doctype html><meta charset="utf-8"><title>配额与重排对照</title><style>body{max-width:1300px;margin:30px auto;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:14px}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:8px;vertical-align:top}details{margin:16px 0}</style>',
        '<h1>子查询配额、合并排序与重排对照</h1><p>已曝光开发集，仅看候选来源覆盖。没有生成答案，不能解释为答案准确率。N配额逐查询逐通道保留前N；候选超过40时按查询支持数、最好名次、稳定顺序裁剪。</p>',
        '<h2>总体（配额/候选排序看40条覆盖；重排看完整并集重排后的Top40覆盖）</h2>'+chart+'<pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre><h2>路由分类</h2><pre>'+esc(json.dumps(by_route,ensure_ascii=False,indent=2))+'</pre><h2>逐题</h2>']
    cases={c['id']:c for c in recorder.bench['cases']}
    for cid,case in cases.items():
        rows=[r for r in summary['results'] if r['case_id']==cid]
        if not rows:continue
        lines.append(f'<details><summary>{cid}: {esc(case["question"])}</summary>')
        lines.append('<h3>必要事实</h3><pre>'+esc(json.dumps([dict(unit=u,answer_point=recorder.bench['units'][u]['answer_point'],support=recorder.bench['units'][u]['known_support_chunks']) for u in case['units']],ensure_ascii=False,indent=2))+'</pre>')
        for row in rows:
            lines.append(f'<h3>{row["arm"]}</h3><pre>'+esc(json.dumps(dict(metrics=row['metrics'],facts=row['facts'],compute=row.get('compute'),ranked_candidates=row.get('ranked_candidates'),selection=row.get('selection')),ensure_ascii=False,indent=2))+'</pre>')
        lines.append('</details>')
    (folder/'index.html').write_text(''.join(lines),encoding='utf8')
    write_json(folder/'report-data.json',dict(aggregate=stats,results=summary['results']))
    write_json(folder/'comparison.json',dict(aggregate=stats,by_route=by_route,paired=summary['paired']))


def execute(root,prepare_only=False):
    bench=freeze(root);rec=PolicyDataset(root,VERSION)
    try:
        if prepare_only:
            print(json.dumps(dict(status='not_run',benchmark=VERSION,sha256=rec.digest)));return
        cfg=settings(root)
        for p,d in {**bench['code_sha256'],**bench['inputs_sha256']}.items():
            if sha(root/p)!=d:raise ValueError('frozen_input_or_code_changed:'+p)
        rec.sync_dataset()
        source=read(root/BASE/'summary.json');expanded={r['case_id']:r for r in source['results'] if r['arm']=='Expanded'}
        corpus,_,chunks=load_corpus(root);chunkmap={x['chunk_id']:x for x in chunks}
        if corpus!=bench['corpus_id']:raise ValueError('corpus_changed')
        rid=uuid.uuid4().hex;folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/rid;folder.mkdir(parents=True)
        summary=dict(run_id=rid,benchmark=VERSION,benchmark_sha256=rec.digest,status='running',started=datetime.now(timezone.utc).isoformat(),results=[])
        write_json(folder/'summary.json',summary)
        cases={c['id']:c for c in bench['cases']}
        # Candidate-only policy arms use persisted full/dense channel results.
        for cid,source_row in expanded.items():
            queries=source_row['queries'];universe=all_candidates(queries);case=cases[cid]
            roundrobin=[]
            rr_source={x['chunk_id']:x for x in source_row['candidates']}
            for x in universe:
                if x['chunk_id'] in rr_source:
                    z=deepcopy(x);z['retained']=rr_source[x['chunk_id']]['retained'];z['merged_rank']=rr_source[x['chunk_id']]['merged_rank'];roundrobin.append(z)
            queryhit=rank_query_hits(universe)
            policies=[(f'Quota-N{n}',quota_pool(universe,n)) for n in QUOTAS]
            policies.extend([('RoundRobin-40',roundrobin),('QueryHits-BestRank-40',queryhit)])
            for arm,candidates in policies:
                metrics,facts=score_pool(candidates,case,bench['units'],chunkmap)
                row=dict(case_id=cid,question=case['question'],arm=arm,route=bench['query_plans'][cid]['route'],queries=[dict(id=q['id'],text=q['text']) for q in queries],
                    candidates=candidates,metrics=metrics,facts=facts,compute=dict(pairs=0,inference_seconds=0),started=summary['started'],finished=datetime.now(timezone.utc).isoformat())
                summary['results'].append(row)
        # Rerank the same complete union under both query-scoring policies.
        total_rerank_pairs=0;total_inference=0;model_info=None
        for cid,source_row in expanded.items():
            case=cases[cid];queries=source_row['queries'];universe=all_candidates(queries)
            qmap={q['id']:q['text'] for q in queries};subqueries={q['id']:q['text'] for q in queries if q['id']!='Q0'}
            texts={x['chunk_id']:chunkmap[x['chunk_id']]['text'] for x in universe}
            outputs={}
            for strategy in ('original','owner'):
                groups={}
                for item in universe:
                    owners=[q for q in item['found_by'] if q in subqueries] if strategy=='owner' else ['Q0']
                    if not owners:owners=['Q0']
                    for qid in owners:groups.setdefault(qid,[]).append(item['chunk_id'])
                scored={};pairs=0;inference=0.;elapsed=0.;requests=[]
                for qid,ids in groups.items():
                    for start in range(0,len(ids),40):
                        batch=ids[start:start+40];t0=time.monotonic()
                        result=run_worker(root,cfg,'rerank',[chunkmap[cid] for cid in batch],query=qmap[qid],timeout=1800)
                        elapsed+=time.monotonic()-t0;pairs+=len(batch);inference+=result.get('inference_seconds',0)
                        model_info={k:result.get(k) for k in ('model_id','device','dtype','max_pair_tokens','batch_size','persistent')}
                        requests.append(dict(query_id=qid,pairs=len(batch),seconds=result.get('inference_seconds'),elapsed_seconds=result.get('elapsed_seconds'),load_seconds=result.get('load_seconds'),model_reused=result.get('model_reused')))
                        for chunk_id,value in zip(batch,result['outputs']):
                            scored.setdefault(chunk_id,{})[qid]=float(value)
                ranked=[]
                for item in universe:
                    score_by=scored[item['chunk_id']]
                    selected=max(score_by.values()) if strategy=='owner' else score_by['Q0']
                    ranked.append(dict(item,score_by=score_by,rerank_score=selected))
                ranked.sort(key=lambda x:(-x['rerank_score'],x['first_discovery']))
                for i,item in enumerate(ranked,1):item.update(merged_rank=i,retained=i<=40)
                metrics,facts=score_pool(ranked,case,bench['units'],chunkmap)
                metrics['top40_coverage']=metrics['cap40_coverage'];metrics['top40_all']=metrics['cap40_all']
                arm='Rerank-Original-Union40' if strategy=='original' else 'Rerank-OwnerSubquery-Union40'
                summary['results'].append(dict(case_id=cid,question=case['question'],arm=arm,route=bench['query_plans'][cid]['route'],
                    queries=[dict(id=q['id'],text=q['text']) for q in queries],candidates=universe,ranked_candidates=ranked,
                    metrics=metrics,facts=facts,compute=dict(pairs=pairs,inference_seconds=inference,wall_seconds=elapsed,requests=requests,model=model_info),
                    ownership_policy='each candidate is scored against every subquery that discovered it; max score selects; Q0 fallback only when no subquery discovery',
                    started=summary['started'],finished=datetime.now(timezone.utc).isoformat()))
                total_rerank_pairs+=pairs;total_inference+=inference
                write_json(folder/f'{cid}-{strategy}-rerank.json',dict(case_id=cid,arm=arm,ranked_candidates=ranked,compute=summary['results'][-1]['compute'],metrics=metrics,facts=facts))
            write_json(folder/f'{cid}-candidate-policies.json',[r for r in summary['results'] if r['case_id']==cid and not r['arm'].startswith('Rerank-')])
            write_json(folder/'summary.json',summary)
            completed_pairs=sum(r.get('compute',{}).get('pairs',0) for r in summary['results'] if r['case_id']==cid)
            print(json.dumps(dict(case_id=cid,completed_rerank_pairs=completed_pairs)),flush=True)
        summary.update(status='completed',finished=datetime.now(timezone.utc).isoformat(),reranker_model=model_info,
            total_rerank_pairs=total_rerank_pairs,total_rerank_inference_seconds=total_inference)
        report(rec,summary,folder)
        rec.sync_run(folder/'summary.json');report(rec,summary,folder)
        print(json.dumps(rec.status,ensure_ascii=False),flush=True)
    finally:rec.close()
