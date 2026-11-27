"""Offline replay of the archived router JSON after quote-normalization fix."""
from copy import deepcopy
from pathlib import Path
import json
from .evaluation_datasets import load_benchmark,write_json
from .query_router_diagnostic import validate,rule_candidate
from .subquery_diagnostic import sha

VERSION='benchmark-query-router-fix-v1'
SOURCE='benchmark-query-router-v1'
RUN='6181b95b9e3545f58ab4ceaa8c1789d9'

def replay(root):
    folder=root/'artifacts/eval/stage-4'/VERSION
    if (folder/'benchmark.json').exists():
        return load_benchmark(root,VERSION)[0]
    parent,digest,_=load_benchmark(root,SOURCE)
    old=json.loads((root/'artifacts/reports/stage-4'/SOURCE/'runs'/RUN/'summary.json').read_text(encoding='utf8'))
    bench=deepcopy(parent); plans={}; changes=[]
    for row in old['results']:
        if row['arm']!='Local-LLM': continue
        try:
            parsed=validate(row['question'],row['parsed_output'],row['rule_candidate'])
            after=dict(route=parsed['route'],subqueries=parsed['subqueries'],unresolved=parsed['unresolved'],reason=parsed['reason'],
                original_query=row['question'],validation_errors=[],valid=True,quote_normalized=any(s.get('quote_normalized') for s in parsed['source_spans']),source_spans=parsed['source_spans'],parsed_output=row['parsed_output'])
        except Exception as exc:
            after=dict(route='fallback',subqueries=[],unresolved=[],reason='校验失败，保留原题',validation_errors=[str(exc)],valid=False,
                quote_normalized=False,source_spans=[],parsed_output=row['parsed_output'],original_query=row['question'])
        plans[row['case_id']]=after
        if row['route']!=after['route'] or row['subqueries']!=after['subqueries']:
            changes.append(dict(case_id=row['case_id'],before=dict(route=row['route'],subqueries=row['subqueries'],valid=row['valid'],validation_errors=row['validation_errors']),after=after))
    if len(plans)!=24: raise ValueError('expected_24_router_rows')
    bench['version']=VERSION;bench['parent_benchmark_sha256']=digest;bench['query_plans']=plans
    bench['dataset_description']='24道已曝光跨论文开发题：修复quote规范化后的归档路由离线重放；只验证校验修复并重新召回。'
    bench['prior_exposure']='复用已归档模型输出；没有重新调用分流模型；不是泛化验收。'
    bench['comparison']=dict(mode='router_quote_normalization_replay',arms=['Rule','Local-LLM'])
    bench['controls']=dict(parent_router_version=SOURCE,parent_router_run=RUN,model_replay='archived parsed_output only; no Qwen call',
        validation_fix='exact quote, whitespace normalized, then punctuation normalized, original offset mapping',
        prompt_unchanged=True,retrieval='only changed plan R11 is re-retrieved in follow-up; other plans compared for identity',generation=False)
    bench['replay_changes']=changes
    bench['scoring']=dict(primary='R11 route restored and four archived subqueries retained',others='23 Local-LLM routes and subqueries byte-equivalent after replay',semantic='not assessed')
    bench['code_sha256']={p:sha(root/p) for p in ('src/papertech/query_router_diagnostic.py','src/papertech/router_fix_replay.py','scripts/eval-stage4.py','src/papertech/evaluation_details.py')}
    write_json(folder/'benchmark.json',bench);(folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    write_json(folder/'route-diff.json',dict(source_benchmark=SOURCE,source_run=RUN,changes=changes,all_cases=plans))
    return bench
