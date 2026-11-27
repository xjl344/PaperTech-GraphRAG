"""Frozen query-router recall ablation; no reranking or generation."""
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

from .audit import Audit, now
from .cloud_embeddings import compatible, configured
from .corpus import load_corpus, valid_vector
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, clean, source_detail
from .graph_store import GraphStore
from .local_models import vector_cache
from .providers import Providers
from .retrieval import normalize
from .settings import settings
from .subquery_diagnostic import sha

VERSION = 'benchmark-subquery-recall-v1'
ARMS = ('Original', 'Expanded')
ROUTER = 'artifacts/reports/stage-4/benchmark-query-router-v1/runs/6181b95b9e3545f58ab4ceaa8c1789d9/summary.json'
VECTORS = '.cache/retrieval-comparison/12b6c032bb3f4992944a1148ddc92bce/query-vectors.json'
PARENT = 'artifacts/reports/stage-4/benchmark-relation-holdout-v1/runs/12b6c032bb3f4992944a1148ddc92bce/summary.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def merge_queries(queries, cap=40):
    """Rank-major round robin. Preserve every discovery, including after cap."""
    merged = {}
    for rank in range(20):
        for query in queries:
            for channel in ('fulltext', 'dense'):
                rows = query['channels'][channel]
                if rank >= len(rows):
                    continue
                hit = rows[rank]; cid = hit['chunk_id']
                item = merged.setdefault(cid, dict(chunk_id=cid, found_by=[], discoveries=[]))
                if query['id'] not in item['found_by']:
                    item['found_by'].append(query['id'])
                item['discoveries'].append(dict(query_id=query['id'], channel=channel,
                    rank=rank+1, score=hit['score']))
    result = []
    for rank, item in enumerate(merged.values(), 1):
        result.append(dict(item, merged_rank=rank, retained=rank <= cap))
    return result


def score(candidates, case, units, chunks):
    all_ids = {r['chunk_id'] for r in candidates}
    kept = {r['chunk_id'] for r in candidates if r['retained']}
    facts = []
    for uid in case['units']:
        unit = units[uid]; supports = set(unit['known_support_chunks'])
        matches = [r for r in candidates if r['chunk_id'] in supports]
        retained = bool(kept & supports)
        facts.append(dict(unit_id=uid, required_fact=unit['answer_point'],
            known_support_chunks=unit['known_support_chunks'], union_hit=bool(matches), retained=retained,
            reason='retained' if retained else 'candidate_cap' if matches else 'upstream_missing',
            matches=deepcopy(matches)))
    count = len(facts)
    papers = set(case['source_papers'])
    return dict(union_coverage=sum(f['union_hit'] for f in facts)/count,
        cap40_coverage=sum(f['retained'] for f in facts)/count,
        union_all=all(f['union_hit'] for f in facts), cap40_all=all(f['retained'] for f in facts),
        union_paper_coverage=len({chunks[c]['paper_id'] for c in all_ids} & papers)/len(papers),
        cap40_paper_coverage=len({chunks[c]['paper_id'] for c in kept} & papers)/len(papers)), facts


def freeze(root):
    folder = root/'artifacts/eval/stage-4'/VERSION
    if (folder/'benchmark.json').exists():
        return load_benchmark(root, VERSION)[0]
    parent, digest, _ = load_benchmark(root, 'benchmark-relation-holdout-v1')
    router = read(root/ROUTER)
    if router['status'] != 'completed':
        raise ValueError('router_not_completed')
    plans = {r['case_id']: dict(question=r['question'], route=r['route'],
        subqueries=deepcopy(r['subqueries']), unresolved=r['unresolved'], reason=r['reason'],
        historical_seconds=r['seconds'], historical_usage=r['usage'], trace_url=r['trace_url'])
        for r in router['results'] if r['arm'] == 'Local-LLM'}
    bench = deepcopy(parent)
    bench['cases'] = [c for c in parent['cases'] if c['id'].startswith('R')]
    if set(plans) != {c['id'] for c in bench['cases']} or len(plans) != 24:
        raise ValueError('expected_all_24_router_cases')
    for c in bench['cases']:
        c['generate'] = False
        if c['question'] != plans[c['id']]['question']:
            raise ValueError('router_question_changed')
    bench['units'] = {u: parent['units'][u] for c in bench['cases'] for u in c['units']}
    bench.pop('graph_snapshot', None)
    bench.pop('code_sha256', None)
    bench.update(version=VERSION, parent_benchmark_sha256=digest, arms=list(ARMS), query_plans=plans,
        distribution=dict(cross=24), comparison=dict(mode='subquery_recall', arms=list(ARMS)),
        dataset_description='24道已曝光跨论文开发题：原题 vs 原题加冻结通用分流子查询。仅检索，不重排、不生成。',
        prior_exposure='本题集及来源已用于开发和拆分审阅；新版本仅冻结新对照，不是新泛化测试。',
        inputs_sha256={ROUTER:sha(root/ROUTER), VECTORS:sha(root/VECTORS), PARENT:sha(root/PARENT)},
        controls=dict(fulltext_top=20, dense_top=20, ann_query_k=100, cap=40,
            merge='rank ascending, query order original then SQ, channel order fulltext then dense; first discovery order; no cross-query RRF',
            original_question='always retained as an input; its candidates can be displaced by the fixed cap',
            union='uncapped union reported separately; increases search budget',
            router='reuse all frozen outputs including bad splits and fallback; no manual fixes',
            embedding='original vectors cached; normalized new subqueries batched once, identical compatible cloud BGE',
            retrieval='production GraphStore.retrieve on existing Neo4j fulltext and vector indexes; no graph traversal',
            reranking=False, answer_generation=False, evidence_selection=False),
        scoring=dict(primary='paired per-question necessary-source coverage at cap40; uncapped coverage separate',
            gold='any known_support_chunks match counts; non-exhaustive frozen support pools',
            separate='paper inclusion is not required source passage coverage; neither is answer accuracy',
            pairing='win/tie/loss plus source additions/removals, including equal-score substitutions',
            cost='new embedding call and shared batch time separate; retrieval per query measured; historical router cost separate',
            semantic_review='not assessed; no generated answers', negative_policy='not applicable: 24 cross-paper questions only'),
        code_sha256={p:sha(root/p) for p in ('src/papertech/subquery_recall_diagnostic.py',
            'src/papertech/retrieval.py','src/papertech/graph_store.py','scripts/eval-stage4.py',
            'src/papertech/evaluation_details.py')})
    write_json(folder/'benchmark.json', bench)
    (folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n', encoding='utf8')
    for p in bench['code_sha256']:
        dest = folder/'runtime-snapshot'/p
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes((root/p).read_bytes())
    return bench


def paired(summary):
    result = {}
    for cid in sorted({r['case_id'] for r in summary['results']}):
        group = {r['arm']:r for r in summary['results'] if r['case_id'] == cid}
        if set(group) != set(ARMS):
            continue
        result[cid] = {}
        for metric, field in (('union_coverage','union_hit'), ('cap40_coverage','retained')):
            b, e = group['Original'], group['Expanded']
            delta = e['metrics'][metric] - b['metrics'][metric]
            before = {f['unit_id'] for f in b['facts'] if f[field]}
            after = {f['unit_id'] for f in e['facts'] if f[field]}
            result[cid][metric] = dict(delta=delta,
                outcome='win' if delta>1e-12 else 'loss' if delta < -1e-12 else 'tie',
                added=sorted(after-before), removed=sorted(before-after))
    return result


class RecallDataset(DetailedEvaluationDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload['description'] = self.bench['dataset_description']
        for e in self.payload['examples']:
            e['metadata']['review_origin'] = 'Codex source review; exposed development data'
            e['outputs']['evaluation_config']['planned_output'] = '仅候选召回：同40条上限与全部并集；不重排、不生成'
            e['outputs']['result_display'].update(location='Original / Expanded Experiments',
                fields=['原题与冻结子查询','每查询每通道排名/分数','found_by 与合并截断',
                    '全部候选原文及位置','逐必要来源覆盖与缺口','两组逐题得失','调用/时延/Token状态','Trace'])
            write_json(self.directory/'cases'/(e['metadata']['case_id']+'.json'),e)
        write_json(self.directory/'langsmith-dataset.json',self.payload)

    def sync_run(self, summary_path, answer_mode='full'):
        path = Path(summary_path); s = read(path)
        if s['benchmark_sha256'] != self.digest:
            raise ValueError('benchmark_mismatch')
        dataset = self.sync_dataset(); pairs = paired(s); payloads = []
        keys = [(r['case_id'],r['arm']) for r in s['results']]
        expected_pairs = {(c['id'],a) for c in self.bench['cases'] for a in ARMS}
        if len(set(keys)) != len(keys) or not set(keys) <= expected_pairs:
            raise ValueError('invalid_pairs')
        if s['status'] == 'completed' and set(keys) != expected_pairs:
            raise ValueError('missing_pairs')
        for row in s['results']:
            output = clean(deepcopy(row)); output.pop('trace_url', None)
            output.update(per_case_comparison=pairs.get(row['case_id']),
                candidate_sources=[source_detail(self.chunks[c['chunk_id']]) for c in row['candidates']],
                shared_embedding=s.get('embedding'), latency_note='实际召回时延；不含复用的历史分流耗时和共享embedding批次',
                generation='not_run', reranking='not_run', evidence_selection='not_run',
                interpretation='支持来源ID覆盖，非答案正确率；不穷尽全部可能的证据。')
            payloads.append(dict(id=stable_id(self.digest,s['run_id'],row['case_id'],row['arm']),
                name='subquery-recall-diagnostic',run_type='chain',inputs=dict(question=row['question']),outputs=output,
                reference_example_id=stable_id(self.digest,row['case_id']),start_time=row['started'],end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=VERSION,arm=row['arm'],case_id=row['case_id'],development_only=True,
                    capture_mode='recorded_retrieval_import',original_run_id=s['run_id'])),
                _arm=row['arm'],_metrics=dict(row['metrics'],candidate_union_count=len(row['candidates']),
                    candidate_kept_count=sum(c['retained'] for c in row['candidates']),
                    retrieval_seconds=row['retrieval_seconds'],query_count=len(row['queries']),
                    rerank_pairs=0,generation_calls=0)))
        write_json(path.parent/'langsmith-experiments.json',dict(runs=payloads))
        experiments = []; links = {}
        for arm in ARMS:
            expected = {p['id']:p for p in payloads if p['_arm']==arm}
            name = f'papertech-{VERSION}-{s["run_id"][:12]}-{arm}'
            project = self.client.create_project(name,reference_dataset_id=dataset.id,upsert=True,
                description=self.bench['dataset_description'],metadata=dict(arm=arm,benchmark_sha256=self.digest))
            if str(project.reference_dataset_id) != str(dataset.id):
                raise ValueError('wrong_reference_dataset')
            found = {str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            if set(found)-set(expected) or any(r.outputs!=expected[rid]['outputs'] for rid,r in found.items()):
                raise ValueError('remote_modified')
            def upload(p):
                data = {k:v for k,v in p.items() if not k.startswith('_')}
                data['start_time']=datetime.fromisoformat(data['start_time']); data['end_time']=datetime.fromisoformat(data['end_time'])
                self.client.create_run(project_name=name,**data)
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(upload,[p for rid,p in expected.items() if rid not in found]))
            jobs = [dict(run_id=p['id'], key=k, score=float(v), feedback_id=stable_id(p['id'],k),
                session_id=project.id, stop_after_attempt=1,comment='已曝光开发题的来源覆盖/检索成本；非答案准确率。')
                for p in expected.values() for k,v in p['_metrics'].items()]
            feedback = {str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(lambda j:self.client.create_feedback(**j),[j for j in jobs if j['feedback_id'] not in feedback]))
            for attempt in range(6):
                found = {str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
                feedback = {str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
                valid = set(found)==set(expected) and all(r.outputs==expected[rid]['outputs'] and
                    r.inputs==expected[rid]['inputs'] and str(r.reference_example_id)==expected[rid]['reference_example_id']
                    for rid,r in found.items())
                valid = valid and all(j['feedback_id'] in feedback and math.isclose(feedback[j['feedback_id']].score,j['score'],abs_tol=.000050001,rel_tol=0) for j in jobs)
                if valid:
                    break
                if attempt==5:
                    raise ValueError('readback_incomplete')
                time.sleep(2)
            for rid,r in found.items():
                links[rid]=self.client.get_run_url(run=r)
            self.client.update_project(project.id,end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(found),feedback_verified=len(jobs)))
        self.status.update(status='experiments_verified',result_status=s['status'],experiments=experiments,
            comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments))
        write_json(path.parent/'experiment-trace-links.json',links)
        write_json(path.parent/'langsmith-status.json',self.status);write_json(self.status_path,self.status)
        return self.status


def aggregate(rows):
    return {arm:dict(count=len(rs),
        **{k:sum(r['metrics'][k] for r in rs)/len(rs) for k in ('union_coverage','cap40_coverage')},
        union_sources=sum(f['union_hit'] for r in rs for f in r['facts']),
        cap40_sources=sum(f['retained'] for r in rs for f in r['facts']),
        total_sources=sum(len(r['facts']) for r in rs),
        union_complete=sum(r['metrics']['union_all'] for r in rs),
        cap40_complete=sum(r['metrics']['cap40_all'] for r in rs),
        avg_candidates=sum(len(r['candidates']) for r in rs)/len(rs),
        retrieval_seconds=sum(r['retrieval_seconds'] for r in rs),
        query_count=sum(len(r['queries']) for r in rs))
        for arm in ARMS if (rs := [r for r in rows if r['arm']==arm])}


def report(recorder,s,folder):
    pairs=paired(s);stats=aggregate(s['results'])
    groups={route:aggregate([r for r in s['results'] if r['route']==route]) for route in sorted({r['route'] for r in s['results']})}
    outcomes={k:dict(Counter(p[k]['outcome'] for p in pairs.values())) for k in ('union_coverage','cap40_coverage')}
    write_json(folder/'comparison.json',dict(status=s['status'],overall=stats,by_route=groups,paired=pairs,outcomes=outcomes))
    esc=html.escape
    def dump(obj):
        return '<pre>'+esc(json.dumps(obj,ensure_ascii=False,indent=2))+'</pre>'
    bars=[]
    for i,(arm,metric) in enumerate((a,m) for a in ARMS for m in ('union_coverage','cap40_coverage')):
        value=stats.get(arm,{}).get(metric,0);y=32+i*45
        bars.append(f'<text x="8" y="{y+18}">{arm} {metric}</text><rect x="260" y="{y}" width="{value*500:.2f}" height="26" fill="{"#2563eb" if arm=="Original" else "#059669"}"/><text x="{270+value*500:.2f}" y="{y+18}">{value:.2%}</text>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 890 230" font-size="15">'+''.join(bars)+'</svg>'
    (folder/'comparison.svg').write_text(svg,encoding='utf8')
    links=read(folder/'experiment-trace-links.json') if (folder/'experiment-trace-links.json').exists() else {}
    blocks=[];table=[]
    for case in recorder.bench['cases']:
        cid=case['id'];rows=[r for r in s['results'] if r['case_id']==cid]
        if len(rows)!=2:
            continue
        b,e=rows;p=pairs[cid]
        fmt=lambda r,k:f'{r["metrics"][k]:.1%}'
        table.append(f'<tr><td><a href="#{cid}">{cid}</a></td><td>{e["route"]}</td><td>{fmt(b,"union_coverage")} → {fmt(e,"union_coverage")}</td><td>{fmt(b,"cap40_coverage")} → {fmt(e,"cap40_coverage")}</td><td>{esc(str(p["cap40_coverage"]))}</td></tr>')
        parts=[f'<h2 id="{cid}">{cid}</h2><p>{esc(case["question"])}</p>',
            '<h3>参考答案、必要事实与评分</h3>'+dump(next(x['outputs'] for x in recorder.payload['examples'] if x['metadata']['case_id']==cid)),
            '<h3>逐题差异</h3>'+dump(p)]
        for r in rows:
            rid=stable_id(recorder.digest,s['run_id'],cid,r['arm']);url=links.get(rid)
            parts.append(f'<h3>{r["arm"]}</h3>'+ (f'<a href="{esc(url)}">LangSmith Trace</a>' if url else '<p>Trace 待同步</p>')+dump(r))
            parts.append('<details><summary>全部候选原文及位置</summary>'+dump([source_detail(recorder.chunks[c['chunk_id']]) for c in r['candidates']])+'</details>')
        blocks.append('<details open><summary>'+cid+'</summary>'+''.join(parts)+'</details>')
    status=read(folder/'langsmith-status.json') if (folder/'langsmith-status.json').exists() else {}
    page='<!doctype html><meta charset="utf-8"><title>子查询召回对照</title><style>body{max-width:1250px;margin:30px auto;font:16px system-ui;color:#172033}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:16px}td,th{padding:9px;border:1px solid #ddd}table{border-collapse:collapse;width:100%}details{margin:18px 0}svg{max-width:100%}</style>'
    page+='<h1>24题：原题 vs 原题＋通用分流子查询</h1><p>已曝光开发诊断；仅来源召回。未运行重排、证据选择或回答生成。并集收益增加检索预算；同40条候选指标单独比较。论文覆盖不等于必要段落覆盖，也不代表答案正确率。</p>'
    page+=f'<p>状态：{esc(s["status"])}；run={s["run_id"]}；benchmark SHA256={recorder.digest}</p>'+svg+'<h2>总览</h2>'+dump(dict(stats=stats,outcomes=outcomes))
    page+='<h2>分流分类</h2>'+dump(groups)+'<h2>调用、时延与Token</h2>'+dump(dict(embedding=s.get('embedding'),historical_router=s.get('historical_router_cost'),latency_boundary='召回逐查询实测；原题两组共享结果。共享embedding批次不均摊为单题实测；历史拆分成本另列。生成与重排调用0。'))
    page+='<h2>LangSmith</h2>'+dump(status)+'<h2>逐题对照</h2><table><tr><th>题目</th><th>route</th><th>全部并集</th><th>同40条</th><th>得失来源</th></tr>'+''.join(table)+'</table>'+''.join(blocks)
    (folder/'index.html').write_text(page,encoding='utf8')
    lines=['# 子查询召回开发诊断','',f'状态：{s["status"]}；{s["run_id"]}', '', '仅检索。非独立泛化验收，非答案正确率。', '',json.dumps(dict(overall=stats,outcomes=outcomes),ensure_ascii=False,indent=2),'', '| 题目 | 并集变化 | 同40候选变化 | 增补/丢失必要来源（40） |','|---|---|---|---|']
    for cid,p in pairs.items():
        lines.append(f'| {cid} | {p["union_coverage"]["delta"]:+.2%} | {p["cap40_coverage"]["delta"]:+.2%} | +{p["cap40_coverage"]["added"]} / -{p["cap40_coverage"]["removed"]} |')
    (folder/'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8')


def execute(root,prepare_only=False,resume=None):
    freeze(root);recorder=RecallDataset(root,VERSION)
    if prepare_only:
        print(json.dumps(dict(status='not_run',benchmark=VERSION,sha256=recorder.digest)));recorder.close();return
    if resume:
        folder=Path(resume).parent
        try:
            status=recorder.sync_run(resume);report(recorder,read(resume),folder)
            print(json.dumps(status,ensure_ascii=False),flush=True)
        finally:
            recorder.close()
        return
    bench=recorder.bench;cfg=settings(root)
    for p,digest in {**bench['code_sha256'],**bench['inputs_sha256']}.items():
        if sha(root/p)!=digest:
            raise ValueError('frozen_input_or_code_changed:'+p)
    # Fail before any paid call if reference dataset cannot be verified.
    recorder.sync_dataset()
    meta,_=vector_cache(root)
    if not configured(cfg) or not compatible(root,cfg,meta['model_id']):
        raise ValueError('cloud_bge_gate_not_valid')
    store=GraphStore(cfg,bench['corpus_id'],meta['model_id'])
    index=store.inspect()
    if index['counts']!=[dict(chunks=980,papers=14)] or any(i['state']!='ONLINE' for i in index['indexes']):
        raise ValueError('index_not_ready')
    run_id=uuid.uuid4().hex;folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/run_id
    folder.mkdir(parents=True)
    write_json(folder/'index-snapshot.json',index)
    plans=bench['query_plans'];vectors=read(root/VECTORS)
    new_texts=list(dict.fromkeys(normalize(q['text']) for p in plans.values() for q in p['subqueries'] if normalize(q['text']) not in vectors))
    historical=dict(calls=24,seconds=sum(p['historical_seconds'] for p in plans.values()),
        prompt_tokens=sum(p['historical_usage']['prompt_tokens'] for p in plans.values()),
        completion_tokens=sum(p['historical_usage']['completion_tokens'] for p in plans.values()),
        scope='此前已完成的分流开销，本轮复用；模拟线上运行仍需承担，不计为本轮新消费')
    summary=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=recorder.digest,status='running',started=now(),
        results=[],historical_router_cost=historical)
    write_json(folder/'summary.json',summary)
    print(json.dumps(dict(run_id=run_id,questions=24,new_embedding_texts=len(new_texts))),flush=True)
    audit=Audit(root);provider=Providers(cfg,audit);request_id=None
    try:
        if new_texts:
            request_id=audit.start('[subquery recall: shared embedding batch]')
            start=time.monotonic();started=now()
            outputs=provider.embedding(request_id,new_texts)
            seconds=time.monotonic()-start
            for text,values in zip(new_texts,outputs):
                vectors[text]=valid_vector(values)
            # Immediately checkpoint vectors; uploads and reports never contain them.
            write_json(root/'.cache/subquery-recall'/run_id/'query-vectors.json',vectors)
            calls=[dict(r) for r in audit.conn.execute('SELECT id,provider,attempt,started,finished,seconds,status,http_status,usage FROM calls WHERE request_id=?',(request_id,))]
            summary['embedding']=dict(new_text_count=len(new_texts),batch_count=1,provider_attempts=len(calls),
                seconds=seconds,started=started,finished=now(),calls=calls,
                token_status='provider-reported only; null means not reported',original_vectors='cached historical original queries',
                model_id=meta['model_id'],compatibility_gate=True)
            write_json(folder/'summary.json',summary)
            audit.finish(request_id,dict(status='ok',retrieval_summary=dict(embedding_text_count=len(new_texts))))
        old={r['case_id']:r for r in read(root/PARENT)['results'] if r['arm']=='Hybrid'}
        for case in bench['cases']:
            cid=case['id'];plan=plans[cid]
            # Runtime query runner receives text/vector only, never gold or support IDs.
            queries=[]
            for q in [dict(id='Q0',text=case['question'])]+plan['subqueries']:
                text=normalize(q['text']);start=time.monotonic();started=now()
                full,dense=store.retrieve(text,vectors[text])
                queries.append(dict(id=q['id'],text=q['text'],normalized=text,
                    channels=dict(fulltext=full,dense=dense),started=started,finished=now(),seconds=time.monotonic()-start))
                write_json(folder/(cid+'-queries.json'),queries)
            historical_ids={r['chunk_id'] for r in old[cid]['ranked']}
            current_ids={r['chunk_id'] for r in merge_queries(queries[:1])}
            baseline_check=dict(same_candidate_set=historical_ids==current_ids,
                added=sorted(current_ids-historical_ids),removed=sorted(historical_ids-current_ids))
            for arm in ARMS:
                active=queries[:1] if arm=='Original' else queries
                candidates=merge_queries(active);metrics,facts=score(candidates,case,bench['units'],recorder.chunks)
                row=dict(case_id=cid,question=case['question'],category=case['category'],arm=arm,status='ok',
                    route=plan['route'],query_plan=plan,queries=deepcopy(active),candidates=candidates,metrics=metrics,facts=facts,
                    started=active[0]['started'],finished=active[-1]['finished'],
                    retrieval_seconds=sum(q['seconds'] for q in active),historical_baseline_check=baseline_check,
                    embedding_text_count=0 if arm=='Original' else len(active)-1,
                    embedding_call_scope='0 original calls; all new subquery texts share one run-level batch; no per-question HTTP call',
                    rerank_pairs=0,generation_calls=0,context_bytes=None,evidence_blocks=None,
                    non_execution_reason='evidence selection, generation and context assembly outside this diagnostic')
                summary['results'].append(row);write_json(folder/(cid+'-'+arm+'.json'),row)
            write_json(folder/'summary.json',summary)
            print(json.dumps(dict(case_id=cid,baseline=summary['results'][-2]['metrics'],expanded=summary['results'][-1]['metrics'],historical_match=baseline_check['same_candidate_set'])),flush=True)
        summary.update(status='completed',finished=now())
    except BaseException as exc:
        summary.update(status='interrupted',finished=now(),error_type=type(exc).__name__)
        raise
    finally:
        write_json(folder/'summary.json',summary)
        report(recorder,summary,folder)
        try:
            recorder.sync_run(folder/'summary.json')
            report(recorder,summary,folder)
            print(json.dumps(dict(status=summary['status'],run_id=run_id,langsmith=recorder.status),ensure_ascii=False),flush=True)
        except Exception as exc:
            pending=dict(status='pending_sync',error_type=type(exc).__name__,summary=str(folder/'summary.json'))
            write_json(folder/'langsmith-status.json',pending)
            print(json.dumps(pending),flush=True)
        finally:
            provider.client.close();audit.close();store.close();recorder.close()
