"""Development diagnostics: recall width, fixed-score resources, then recall intervention."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import html
import importlib.util
import json
import math
from pathlib import Path
import time
import uuid

from .audit import now
from .corpus import load_corpus
from .entity_aliases import is_comparison
from .evaluation import support_metrics, criterion_source_coverage, linear_quantile
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, detailed_output
from .evidence_context import assemble
from .graph_store import GraphStore
from .local_models import run_worker, vector_cache
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings

WIDTH = 'benchmark-recall-width-v1'
RESOURCE = 'benchmark-resource-selection-v1'
RECALL = 'benchmark-recall-intervention-v1'
VERSIONS = (WIDTH, RESOURCE, RECALL)
PARENT = 'artifacts/reports/stage-4/benchmark-relation-holdout-v1/runs/12b6c032bb3f4992944a1148ddc92bce'
RESOURCE_CONFIG = {
    'Named-6000-8': dict(budget=6000,evidence_max=8,source_policy='named_first'),
    'Named-6000-12': dict(budget=6000,evidence_max=12,source_policy='named_first'),
    'Named-8000-8': dict(budget=8000,evidence_max=8,source_policy='named_first'),
    'Named-8000-12': dict(budget=8000,evidence_max=12,source_policy='named_first'),
    'Score-6000-8': dict(budget=6000,evidence_max=8,source_policy='score_order'),
    'Score-8000-12': dict(budget=8000,evidence_max=12,source_policy='score_order'),
}
FILES = ('src/papertech/staged_retrieval_diagnostics.py','src/papertech/retrieval.py',
    'src/papertech/evidence_context.py','src/papertech/workflow.py','src/papertech/graph_store.py',
    'src/papertech/rerank_runtime.py','src/papertech/rerank_service.py','scripts/rerank-service.py',
    'src/papertech/entity_aliases.py','src/papertech/evaluation_details.py','scripts/eval-stage4.py',
    'scripts/explain-relation-holdout.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def previous(root,version):
    latest=read_json(root/'artifacts/reports/stage-4'/version/'latest.json')
    folder=Path(latest['directory'])
    summary=read_json(folder/'summary.json')
    if summary['status']!='completed':
        raise ValueError('previous_diagnostic_not_completed')
    return folder,summary


def parent_rows(root):
    return {r['case_id']:r for r in read_json(root/PARENT/'summary.json')['results'] if r['arm']=='Hybrid'}


def freeze(root,version):
    folder=root/'artifacts/eval/stage-4'/version
    if (folder/'benchmark.json').exists():
        return load_benchmark(root,version)[0]
    parent,digest,_=load_benchmark(root,'benchmark-relation-holdout-v1')
    bench=deepcopy(parent)
    summary=read_json(root/PARENT/'summary.json')
    cfg=settings(root)
    if any(cfg.get(k)!=v for k,v in summary['execution_config']['models'].items()):
        raise ValueError('parent_model_configuration_changed')
    vector_path=root/'.cache/retrieval-comparison'/summary['run_id']/'query-vectors.json'
    arms=('Dense20','Dense40','Dense60') if version==WIDTH else tuple(RESOURCE_CONFIG)
    controls=dict(stage='upstream_recall_width' if version==WIDTH else 'fixed_scores_resource_selection',
        fulltext_top=20,rrf_k=60,generation=False,embedding_calls=0,
        named_policy='existing named-paper reservation, not necessary-source reservation',
        no_gold_in_inputs=True,model_config=summary['execution_config']['models'])
    if version==WIDTH:
        controls.update(dense_values=[20,40,60],ann_query_k=100,fusion_cap='20+dense_k, no truncation',
            rerank_calls=0,evidence_selection=False,query_vectors_sha256=sha(vector_path),
            index_requirement='current corpus/model and top20 prefix identical to parent')
    if version==RESOURCE:
        controls.update(configurations=RESOURCE_CONFIG,rerank_calls=0,candidate_changes=False,
            score_changes=False,byte_and_count_ablation=True)
    if version==RECALL:
        width_folder,width_summary=previous(root,WIDTH)
        base={r['case_id']:r for r in width_summary['results'] if r['arm']=='Dense20'}
        cross={c['id'] for c in bench['cases'] if c['category']=='cross'}
        choice=None
        for k in (40,60):
            extra=[r for r in width_summary['results'] if r['arm']==f'Dense{k}' and r['case_id'] in cross]
            if any(r['source_metrics']['candidate_pool_coverage']>base[r['case_id']]['source_metrics']['candidate_pool_coverage'] for r in extra):
                choice=k
                break
        if choice is None:
            raise ValueError('no_width_gain_use_query_decomposition_design_instead')
        resource_folder,resource_summary=previous(root,RESOURCE)
        arms=('Dense20','Dense'+str(choice))
        controls.update(stage='recall_width_intervention',dense_values=[20,choice],fulltext_top=20,
            candidate_cap=20+choice,selection=RESOURCE_CONFIG['Named-8000-12'],
            score_policy='reuse identical original-query scores for saved candidates; score only newly admitted chunks with original question',
            gate='smallest k recovering any missing cross source; fixed before new reranker calls',
            target_adoption='cross regression count must not exceed improvement count; not automatic production adoption')
        bench['width_results']=str(width_folder/'summary.json')
        bench['width_results_sha256']=sha(width_folder/'summary.json')
        bench['resource_results']=str(resource_folder/'summary.json')
        bench['resource_results_sha256']=sha(resource_folder/'summary.json')
    bench.update(version=version,parent_benchmark_sha256=digest,parent_run=PARENT,
        parent_summary_sha256=sha(root/PARENT/'summary.json'),query_vectors_path=str(vector_path),
        arms=list(arms),controls=controls,
        dataset_description=f'40题开发诊断 {version}；复用已曝光题目与来源，不作泛化验收。'+
            ('只测上游候选覆盖，不重排或生成。' if version==WIDTH else '分开记录候选覆盖、证据预算与必要来源覆盖；不生成答案。'),
        prior_exposure='这40题与来源已参与前轮诊断和本轮方案讨论；仅开发回归，不是新题泛化测试。',
        comparison=dict(mode='staged_diagnostic',arms=list(arms),generation=False),
        scoring=dict(primary='cross candidate_pool_coverage' if version==WIDTH else 'cross final necessary-source macro coverage',
            negative_policy='8道反例来源诊断单列，不计主召回，不评拒答正确率',
            semantic_review='not assessed; no generation',source_pools='unchanged, non-exhaustive, pre-frozen',
            pairing='case-level win/tie/loss vs declared control; individual source-stage transitions also shown',
            causal_limit='development set only; source-paper inclusion is not necessary-fact support'),
        code_sha256={name:sha(root/name) for name in FILES})
    write_json(folder/'benchmark.json',bench)
    (folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    return bench


def merge_channels(channels):
    scores,sources={},{}
    for channel,rows in channels.items():
        for i,row in enumerate(rows,1):
            cid=row['chunk_id']
            scores[cid]=scores.get(cid,0)+1/(60+i)
            sources.setdefault(cid,[]).append(dict(channel=channel,rank=i,score=row['score']))
    return [dict(chunk_id=cid,score=scores[cid],sources=sources[cid]) for cid in sorted(scores,key=lambda c:(-scores[c],c))]


def fetch_dense(store,vector):
    # Identical ANN query width k=100 to the parent; only the returned limit changes.
    return store.execute('CALL db.index.vector.queryNodes("papertech_vector",$k,$vector) YIELD node,score '
        'WHERE node.corpus_id=$corpus RETURN node.chunk_id AS chunk_id,score ORDER BY score DESC LIMIT $limit',
        k=100,vector=vector,corpus=store.corpus_id,limit=60)


def selection_replay(root,row,chunks):
    spec=importlib.util.spec_from_file_location('staged_selection_replay',root/'scripts/explain-relation-holdout.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.replay_selection(row,chunks)


def score_row(row,case,bench,chunks,root):
    ranked={r['chunk_id']:(i,r) for i,r in enumerate(row['ranked'],1)}
    selected={e['chunk_id'] for e in row['evidence']}
    row['metrics']=support_metrics(list(ranked),list(selected),[bench['units'][u] for u in case['units']])
    def coverage(ids):
        return sum(bool(set(ids)&set(bench['units'][u]['known_support_chunks'])) for u in case['units'])/len(case['units'])
    row['source_metrics']=dict(candidate_pool_coverage=coverage(ranked),
        candidate_all_units=coverage(ranked)==1,
        required_paper_coverage=len({chunks[e]['paper_id'] for e in selected}&set(case['source_papers']))/len(case['source_papers']))
    width=bench['version']==WIDTH
    if width:
        row['metrics'].update(evidence_coverage=None,all_units=None)
        row['source_metrics']['required_paper_coverage']=None
    decisions={} if width else selection_replay(root,row,chunks)
    facts=[]
    for uid in case['units']:
        unit=bench['units'][uid];pool=set(unit['known_support_chunks'])
        hits=[cid for cid in ranked if cid in pool]
        match=hits[0] if hits else None
        if width:
            reason='candidate_available' if match else 'upstream_missing'
        elif selected&pool:
            reason='covered'
        elif not hits:
            reason='upstream_missing'
        elif all(ranked[cid][1]['rerank_score']<.05 for cid in hits):
            reason='reranker_threshold'
        else:
            reason='context_selection'
        facts.append(dict(unit_id=uid,required_fact=unit['answer_point'],reason=reason,
            known_support_chunks=unit['known_support_chunks'],candidate_rank=ranked[match][0] if match else None,
            rerank_score=ranked[match][1].get('rerank_score') if match else None,
            selected_matches=sorted(selected&pool),channel_positions={k:[i for i,r in enumerate(rs,1) if r['chunk_id'] in pool] for k,rs in row['candidate_channels'].items()},
            selection_decisions=[decisions[cid] for cid in hits] if decisions else []))
    row['diagnosis']=dict(facts=facts,reason_counts=dict(Counter(f['reason'] for f in facts)),
        limitation='来源池未穷尽；论文保底不等于必要段落保底；本轮不评答案语义。')
    row['criterion_source_coverage']=criterion_source_coverage(dict(assessment=dict(criteria=case['reference_criteria'])),selected,bench['units']) if not width else []
    row['selection_replay_verified']=not width


class StagedDataset(DetailedEvaluationDataset):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.payload['metadata'].update(no_model_comparison_run=False,development_diagnostic=True)
        for e in self.payload['examples']:
            case=next(c for c in self.bench['cases'] if c['id']==e['metadata']['case_id'])
            e['metadata']['review_origin']='Codex source review; exposed development set'
            e['outputs'].update(reference_criteria=case['reference_criteria'],selection_bias=self.bench['prior_exposure'])
            e['outputs']['result_display'].update(location=' / '.join(self.bench['arms'])+' Experiments',
                fields=['候选通道完整排名与分数','全部候选原文及位置','必要来源上游/重排/预算缺口',
                    '逐题配对差异','时延/调用量与Token状态','证据原文/图路径','原始及本轮Experiment Trace'])
            write_json(self.directory/'cases'/(case['id']+'.json'),e)
        write_json(self.directory/'langsmith-dataset.json',self.payload)

    def sync_run(self,summary_path,answer_mode='full'):
        summary_path=Path(summary_path);summary=read_json(summary_path);folder=summary_path.parent
        if summary['benchmark_sha256']!=self.digest:
            raise ValueError('benchmark_mismatch')
        dataset=self.sync_dataset();cases={c['id']:c for c in self.bench['cases']}
        comparisons=paired(summary,self.bench)
        payloads=[];seen=set()
        for row in summary['results']:
            cid,arm=row['case_id'],row['arm']
            if (cid,arm) in seen or arm not in self.bench['arms'] or row['question']!=cases[cid]['question']:
                raise ValueError('invalid_or_duplicate_row')
            seen.add((cid,arm))
            out=detailed_output(row,cases[cid],self.bench,self.chunks)
            out.update({k:deepcopy(row[k]) for k in ('diagnosis','source_metrics','selection_config',
                'selection_replay_verified','model_calls','new_model_pairs','compute_scope','input_tokens_status')})
            out.update(per_case_comparison=comparisons.get(cid),generation_calls=0,generation_tokens=0,
                original_trace_url=row['trace_url'],original_trace_note='原始召回/重排Trace，非本轮重测；本轮完整诊断记录在本Experiment根Trace。')
            metrics=dict(row['metrics'],**row['source_metrics'],compute_seconds=row['retrieval_compute_seconds'],
                candidate_count=len(row['ranked']),evidence_count=len(row['evidence']),context_bytes=row['retrieval_summary'].get('context_bytes',0),
                new_model_pairs=row['new_model_pairs'],generation_calls=0)
            if cases[cid]['category']=='negative':
                metrics={k:v for k,v in metrics.items() if k not in row['metrics'] and k not in row['source_metrics']}
            payloads.append(dict(id=stable_id(self.digest,summary['run_id'],cid,arm),name='staged-retrieval-diagnostic',
                run_type='chain',inputs=dict(question=row['question']),outputs=out,
                reference_example_id=stable_id(self.digest,cid),start_time=row['started'],end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=self.bench['version'],arm=arm,case_id=cid,generation=False,
                    original_run_id=summary['run_id'],capture_mode='recorded_diagnostic_import',development_only=True)),
                tags=[self.bench['version'],arm,row['category']],_arm=arm,_metrics={k:v for k,v in metrics.items() if v is not None}))
        expected_pairs={(c,a) for c in cases for a in self.bench['arms']}
        if summary['status']=='completed' and seen!=expected_pairs:
            raise ValueError('missing_results')
        write_json(folder/'langsmith-experiments.json',dict(runs=payloads))
        experiments=[];trace_links={}
        for arm in self.bench['arms']:
            expected={p['id']:p for p in payloads if p['_arm']==arm}
            if not expected:
                continue
            name=f'papertech-{self.bench["version"]}-{summary["run_id"][:12]}-{arm}'
            project=self.client.create_project(name,reference_dataset_id=dataset.id,upsert=True,
                description=self.bench['dataset_description'],metadata=dict(benchmark_sha256=self.digest,arm=arm))
            if str(project.reference_dataset_id)!=str(dataset.id):
                raise ValueError('wrong_reference_dataset')
            def read_runs():
                return {str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            found=read_runs()
            if set(found)-set(expected) or any(r.outputs!=expected[rid]['outputs'] for rid,r in found.items()):
                raise ValueError('remote_modified')
            def upload(p):
                data={k:v for k,v in p.items() if not k.startswith('_')}
                data['start_time']=datetime.fromisoformat(data['start_time']);data['end_time']=datetime.fromisoformat(data['end_time'])
                self.client.create_run(project_name=name,**data)
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upload,[p for rid,p in expected.items() if rid not in found]))
            jobs=[dict(run_id=p['id'],key=k,score=float(v),feedback_id=stable_id(p['id'],k),session_id=project.id,
                comment='已曝光开发题上的来源覆盖或计算量；不是答案准确率。') for p in expected.values() for k,v in p['_metrics'].items()]
            feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda j:self.client.create_feedback(**j),[j for j in jobs if j['feedback_id'] not in feedback]))
            for attempt in range(8):
                found=read_runs();feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
                valid=set(found)==set(expected) and all(r.outputs==expected[rid]['outputs'] and
                    r.inputs==expected[rid]['inputs'] and str(r.reference_example_id)==expected[rid]['reference_example_id'] and
                    r.start_time==datetime.fromisoformat(expected[rid]['start_time']) and r.end_time==datetime.fromisoformat(expected[rid]['end_time']) for rid,r in found.items())
                valid=valid and all(j['feedback_id'] in feedback and math.isclose(feedback[j['feedback_id']].score,j['score'],rel_tol=0,abs_tol=.000050001) for j in jobs)
                if valid:
                    break
                if attempt==7:
                    raise ValueError('readback_incomplete')
                time.sleep(2)
            for rid,r in found.items():
                trace_links[rid]=self.client.get_run_url(run=r)
            self.client.update_project(project.id,end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(found),feedback_verified=len(jobs)))
        self.status.update(status='experiments_verified',result_status=summary['status'],experiments=experiments,
            comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments))
        write_json(folder/'experiment-trace-links.json',trace_links)
        write_json(folder/'langsmith-status.json',self.status);write_json(self.status_path,self.status)
        return deepcopy(self.status)


def paired(summary,bench):
    grouped={}
    for r in summary['results']:
        grouped.setdefault(r['case_id'],{})[r['arm']]=r
    result={};control=bench['arms'][0]
    for cid,group in grouped.items():
        if control not in group:
            continue
        result[cid]={}
        for arm,r in group.items():
            def value(row):
                return row['source_metrics']['candidate_pool_coverage'] if bench['version']==WIDTH else row['metrics']['evidence_coverage']
            delta=value(r)-value(group[control])
            result[cid][arm]=dict(control=control,delta=delta,outcome='win' if delta>1e-12 else 'loss' if delta<-1e-12 else 'tie',
                added_sources=sorted({e['chunk_id'] for e in r['evidence']}-{e['chunk_id'] for e in group[control]['evidence']}),
                removed_sources=sorted({e['chunk_id'] for e in group[control]['evidence']}-{e['chunk_id'] for e in r['evidence']}))
    return result


def report(recorder,summary,folder):
    bench=recorder.bench;arms=bench['arms'];rows=summary['results'];comparisons=paired(summary,bench)
    stats={}
    for cat in ('all_positive','fact','cross','negative'):
        stats[cat]={}
        for arm in arms:
            rs=[r for r in rows if r['arm']==arm and (r['category']!='negative' if cat=='all_positive' else r['category']==cat)]
            def avg(key,source='metrics'):
                values=[r[source].get(key) for r in rs if r[source].get(key) is not None]
                return sum(values)/len(values) if values else None
            outcomes=Counter(comparisons[r['case_id']][arm]['outcome'] for r in rs if r['case_id'] in comparisons)
            stats[cat][arm]=dict(count=len(rs),candidate_coverage=avg('candidate_pool_coverage','source_metrics'),
                recall5=avg('recall5'),recall8=avg('recall8'),final_coverage=avg('evidence_coverage'),
                all_units=sum(r['metrics']['all_units'] is True for r in rs),
                average_context_bytes=sum(r['retrieval_summary'].get('context_bytes',0) for r in rs)/len(rs) if rs else None,
                average_evidence_count=sum(len(r['evidence']) for r in rs)/len(rs) if rs else None,
                compute_p50=linear_quantile([r['retrieval_compute_seconds'] for r in rs],.5),
                compute_p95=linear_quantile([r['retrieval_compute_seconds'] for r in rs],.95),
                paired=dict(win=outcomes['win'],tie=outcomes['tie'],loss=outcomes['loss']),
                missing_reasons=dict(Counter(f['reason'] for r in rs for f in r['diagnosis']['facts'] if f['reason'] not in ('covered','candidate_available'))))
    write_json(folder/'comparison.json',dict(status=summary['status'],categories=stats,paired=comparisons))
    esc=html.escape
    lines=[f'# {bench["version"]}', '',f"状态：{summary['status']}。40道已曝光开发题；无生成，不作泛化验收。",'',
        '|组别|跨论文候选覆盖|跨论文最终覆盖|全来源题数|跨论文胜/平/负|','|---|---:|---:|---:|---|']
    pct=lambda v:'N/A' if v is None else f'{v:.2%}'
    page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+bench['version']+'</title>',
        '<style>body{font:15px system-ui;max-width:1300px;margin:32px auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:12px}td,th{border:1px solid #ccc;padding:8px}table{border-collapse:collapse}details{margin:12px 0}</style>',
        f'<h1>{bench["version"]}：{summary["status"]}</h1><p>40道已曝光开发题；参考来源未改动。本轮无生成，覆盖不是答案准确率。</p>']
    if summary.get('dataset_sync',{}).get('comparison_url'):
        url=summary['dataset_sync']['comparison_url'];lines.extend(['','[LangSmith实验对照]('+url+')',''])
        page.append(f'<p><a href="{esc(url,quote=True)}">LangSmith实验对照</a></p>')
    for arm in arms:
        x=stats['cross'][arm];p=x['paired']
        lines.append(f"|{arm}|{pct(x['candidate_coverage'])}|{pct(x['final_coverage'])}|{x['all_units']}/24|{p['win']}/{p['tie']}/{p['loss']}|")
    for cat in ('all_positive','fact','cross'):
        key='candidate_coverage' if bench['version']==WIDTH else 'final_coverage'
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 {60+len(arms)*42}"><title>{cat}</title>']
        for i,arm in enumerate(arms):
            v=stats[cat][arm][key];width=(v or 0)*620;y=12+i*42
            svg.append(f'<text x="0" y="{y+20}">{arm}</text><rect x="220" y="{y}" width="{width}" height="26" fill="{("#3975b7","#308575","#bc643d")[i%3]}"/><text x="{230+width}" y="{y+20}">{pct(v)}</text>')
        svg.append(f'<text x="220" y="{45+len(arms)*42}">0%</text><text x="810" y="{45+len(arms)*42}">100%</text></svg>')
        chart=''.join(svg);(folder/f'coverage-{cat}.svg').write_text(chart,encoding='utf8')
        page.extend([f'<h2>{cat}</h2>',chart])
    page.append('<h2>分类指标、计算时延和预算</h2><pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre>')
    lines.extend(['','生成Token=0；新Embedding调用=0。历史模型Token不计作本轮消费。离线回放耗时、数据库检索耗时与新重排推理耗时分别记录，不当作完整在线响应时延。',
        '8道negative只列来源诊断，不计主指标；论文覆盖与必要原文覆盖分开。','',
        '|题号|组别|候选覆盖|最终覆盖|与控制组差异|失败来源及阶段|','|---|---|---:|---:|---|---|'])
    export=[]
    for case in bench['cases']:
        cid=case['id'];page.append(f'<h2 id="{cid}">{cid} {esc(case["question"])}</h2>')
        example=next(e for e in recorder.payload['examples'] if e['metadata']['case_id']==cid)
        page.append('<details><summary>参考要点、全部来源原文与位置、评分口径</summary><pre>'+esc(json.dumps(example['outputs'],ensure_ascii=False,indent=2))+'</pre></details>')
        for row in [r for r in rows if r['case_id']==cid]:
            arm=row['arm'];delta=comparisons[cid][arm]
            gaps='；'.join(f"{f['unit_id']} {f['reason']}" for f in row['diagnosis']['facts'] if f['reason'] not in ('covered','candidate_available')) or '齐全'
            lines.append(f"|{cid}|{arm}|{pct(row['source_metrics']['candidate_pool_coverage'])}|{pct(row['metrics']['evidence_coverage'])}|{delta['outcome']} {delta['delta']:+.2%}|{gaps}|")
            out=detailed_output(row,case,bench,recorder.chunks)
            out.update(diagnosis=row['diagnosis'],selection_config=row['selection_config'],paired=delta,source_metrics=row['source_metrics'],model_calls=row['model_calls'])
            page.append(f'<details><summary>{arm}：候选{pct(row["source_metrics"]["candidate_pool_coverage"])}，最终{pct(row["metrics"]["evidence_coverage"])}；{esc(gaps)}</summary><pre>'+esc(json.dumps(out,ensure_ascii=False,indent=2))+'</pre></details>')
            export.append(dict(case_id=cid,arm=arm,category=case['category'],question=case['question'],
                candidate_coverage=row['source_metrics']['candidate_pool_coverage'],final_coverage=row['metrics']['evidence_coverage'],
                delta=delta['delta'],outcome=delta['outcome'],gaps=gaps,candidates=len(row['ranked']),evidence=len(row['evidence']),
                context_bytes=row['retrieval_summary'].get('context_bytes',0),seconds=row['retrieval_compute_seconds']))
    import csv
    if export:
        with (folder/'per-question.csv').open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(export[0]));writer.writeheader();writer.writerows(export)
    (folder/'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (folder/'dashboard.html').write_text('\n'.join(page)+'</html>',encoding='utf8')


def make_row(case,arm,parent,ranked,channels,selection,seconds,bench,chunks,root,model_runs=None):
    started=now()
    width=bench['version']==WIDTH
    evidence,details=[],{}
    if not width:
        evidence,_,details=assemble(ranked,chunks,[],case['question'],is_comparison(case['question']),path_budget=0,**selection)
    row=dict(case_id=case['id'],category=case['category'],arm=arm,question=case['question'],
        request_id='replay-'+uuid.uuid4().hex,started=started,finished=now(),status='candidates_only' if width else 'evidence_only' if evidence else 'no_evidence',
        ranked=deepcopy(ranked),candidate_channels=deepcopy(channels),evidence=evidence,graph_paths=[],generation_paths=[],citations=[],
        errors=[],usage=None,model_name=None,answer='仅检索阶段诊断，无生成回答。',generate_requested=False,provider_calls=[],
        trace_url=parent['trace_url'],retrieval_summary=dict(details,arm=arm,candidate_count=len(ranked),graph_fallback=False),
        selection_config=selection,retrieval_compute_seconds=seconds,compute_timings=[],stage_timings=[],
        model_calls=model_runs or [],new_model_pairs=sum(r.get('pairs',0) for r in model_runs or []),
        compute_scope='shared database read only; no rerank' if width else 'saved scores and evidence selection only' if bench['version']==RESOURCE else 'new candidate GPU inference plus evidence selection; existing scores reused',
        input_tokens_status='generation=0; embedding=0; reused scores no new tokens; new reranker pairs counted, tokenizer/billing tokens unknown')
    score_row(row,case,bench,chunks,root)
    row['finished']=now()
    return row


def verify_local(recorder,summary,folder):
    bench=recorder.bench;rows=summary['results'];parents=parent_rows(recorder.root)
    expected={(c['id'],a) for c in bench['cases'] for a in bench['arms']}
    if summary['status']=='completed' and ({(r['case_id'],r['arm']) for r in rows}!=expected or len(rows)!=len(expected)):
        raise ValueError('wrong_result_count')
    cases={c['id']:c for c in bench['cases']}
    for row in rows:
        assert row['question']==cases[row['case_id']]['question']
        assert not row['generate_requested'] and row['usage'] is None and not row['provider_calls']
        if bench['version']==RESOURCE:
            assert row['ranked']==parents[row['case_id']]['ranked']
            if row['arm']=='Named-6000-8':
                assert row['evidence']==parents[row['case_id']]['evidence']
        if bench['version']!=WIDTH:
            assert len(row['evidence'])<=row['selection_config']['evidence_max']
            assert row['retrieval_summary']['context_bytes']<=row['selection_config']['budget']
            assert row['selection_replay_verified']
        for e in row['evidence']:
            c=recorder.chunks[e['chunk_id']]
            assert e['quote']==c['text'] and e['source_spans']==c['source_spans']
    result=dict(status='passed',results=len(rows),counts=dict(Counter(r['arm'] for r in rows)),
        unchanged_references=True,generation_calls=0,embedding_calls=0,selection_replays=0 if bench['version']==WIDTH else len(rows),
        code_unchanged={name:sha(recorder.root/name) for name in FILES}==bench['code_sha256'])
    assert result['code_unchanged']
    write_json(folder/'verification.json',result)
    return result


def execute(root,version,prepare_only=False,resume=None):
    root=Path(root);bench=freeze(root,version);recorder=StagedDataset(root,version)
    if resume:
        folder=Path(resume);summary=read_json(folder/'summary.json')
        summary['dataset_sync']=recorder.sync_run(folder/'summary.json')
        write_json(folder/'summary.json',summary);report(recorder,summary,folder);recorder.close()
        print(json.dumps(summary['dataset_sync'],ensure_ascii=False),flush=True)
        return
    if {name:sha(root/name) for name in FILES}!=bench['code_sha256']:
        raise ValueError('frozen_code_changed')
    if prepare_only:
        print(json.dumps(dict(status='not_run',version=version,cases=40,arms=bench['arms'],sha256=recorder.digest),ensure_ascii=False))
        recorder.close();return
    recorder.sync_dataset()  # Always before index queries or model inference.
    folder=root/'artifacts/reports/stage-4'/version/'runs'/uuid.uuid4().hex
    summary=dict(run_id=folder.name,benchmark=version,benchmark_sha256=recorder.digest,started=now(),status='running',results=[])
    write_json(folder/'summary.json',summary);report(recorder,summary,folder)
    parents=parent_rows(root);cfg=settings(root);store=None
    try:
        if any(cfg.get(k)!=v for k,v in bench['controls']['model_config'].items()):
            raise ValueError('frozen_model_configuration_changed')
        if version==WIDTH:
            meta,_=vector_cache(root);store=GraphStore(cfg,bench['corpus_id'],meta['model_id'])
            index=store.inspect()
            if index['counts']!=[dict(chunks=980,papers=14)] or any(i['state']!='ONLINE' for i in index['indexes']):
                raise ValueError('index_not_ready')
            write_json(folder/'index-snapshot.json',index)
            vectors=read_json(Path(bench['query_vectors_path']))
            if sha(Path(bench['query_vectors_path']))!=bench['controls']['query_vectors_sha256']:
                raise ValueError('query_vector_cache_changed')
        if version==RECALL:
            width_summary=read_json(Path(bench['width_results']))
            if sha(Path(bench['width_results']))!=bench['width_results_sha256']:
                raise ValueError('width_results_changed')
            width_rows={(r['case_id'],r['arm']):r for r in width_summary['results']}
            warm=run_worker(root,cfg,'rerank',[dict(text='Evidence supports retrieval.')],query='evidence',timeout=240)
            warm.pop('outputs',None);summary['warmup']=warm
            expected_model=parents['F01']['retrieval_summary']['reranker']['model_id']
            if warm['model_id']!=expected_model:
                raise ValueError('reranker_changed')
        for n,case in enumerate(bench['cases']):
            cid=case['id'];parent=parents[cid]
            if version==WIDTH:
                begin=time.monotonic();dense=fetch_dense(store,vectors[normalize(case['question'])]);seconds=time.monotonic()-begin
                previous_dense=parent['candidate_channels']['dense']
                if [r['chunk_id'] for r in dense[:20]]!=[r['chunk_id'] for r in previous_dense] or any(not math.isclose(a['score'],b['score'],abs_tol=1e-6) for a,b in zip(dense[:20],previous_dense)):
                    raise ValueError('dense_top20_index_drift')
                for arm in bench['arms']:
                    k=int(arm.removeprefix('Dense'));channels=dict(dense=dense[:k],fulltext=parent['candidate_channels']['fulltext'])
                    ranked=merge_channels(channels)
                    row=make_row(case,arm,parent,ranked,channels,{},seconds,bench,recorder.chunks,root)
                    summary['results'].append(row)
            elif version==RESOURCE:
                for arm,selection in RESOURCE_CONFIG.items():
                    begin=time.monotonic()
                    row=make_row(case,arm,parent,parent['ranked'],parent['candidate_channels'],selection,0,bench,recorder.chunks,root)
                    row['retrieval_compute_seconds']=time.monotonic()-begin
                    summary['results'].append(row)
            else:
                selected_k=bench['controls']['dense_values'][1]
                expanded=deepcopy(width_rows[(cid,'Dense'+str(selected_k))])
                scores={r['chunk_id']:r['rerank_score'] for r in parent['ranked']}
                new=[r for r in expanded['ranked'] if r['chunk_id'] not in scores]
                runs=[]
                for offset in range(0,len(new),40):
                    batch=new[offset:offset+40]
                    out=run_worker(root,cfg,'rerank',[recorder.chunks[r['chunk_id']] for r in batch],query=normalize(case['question']),timeout=300)
                    for r,score in zip(batch,out.pop('outputs')):
                        scores[r['chunk_id']]=score
                    if out['model_id']!=expected_model:
                        raise ValueError('reranker_changed')
                    runs.append(dict(out,pairs=len(batch)))
                for arm in bench['arms']:
                    if arm=='Dense20':
                        ranked=parent['ranked'];channels=parent['candidate_channels'];calls=[]
                    else:
                        ranked=[dict(r,rerank_score=scores[r['chunk_id']]) for r in expanded['ranked']]
                        ranked.sort(key=lambda r:-r['rerank_score']);channels=expanded['candidate_channels'];calls=runs
                    begin=time.monotonic()
                    row=make_row(case,arm,parent,ranked,channels,bench['controls']['selection'],sum(r['inference_seconds'] for r in calls),bench,recorder.chunks,root,calls)
                    row['retrieval_compute_seconds']+=time.monotonic()-begin
                    summary['results'].append(row)
            for row in [r for r in summary['results'] if r['case_id']==cid]:
                write_json(folder/f'{cid}-{row["arm"]}.json',row)
            write_json(folder/'summary.json',summary)
            print(json.dumps(dict(case=cid,version=version,completed=len(summary['results']),
                values={r['arm']:dict(pool=r['source_metrics']['candidate_pool_coverage'],final=r['metrics']['evidence_coverage']) for r in summary['results'] if r['case_id']==cid}),ensure_ascii=False),flush=True)
        summary.update(status='completed',finished=now())
    except BaseException as exc:
        summary.update(status='interrupted',error_type=type(exc).__name__,finished=now())
        raise
    finally:
        write_json(folder/'summary.json',summary)
        try:
            summary['verification']=verify_local(recorder,summary,folder)
            if summary['results']:
                summary['dataset_sync']=recorder.sync_run(folder/'summary.json')
        except Exception as exc:
            summary['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
        write_json(folder/'summary.json',summary);report(recorder,summary,folder)
        write_json(folder.parent.parent/'latest.json',dict(directory=str(folder),status=summary['status']))
        if store:
            store.close()
        recorder.close();close_workers()
        print(json.dumps(dict(status=summary['status'],directory=str(folder),sync=summary.get('dataset_sync')),ensure_ascii=False),flush=True)
