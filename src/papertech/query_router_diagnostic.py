"""Generic question routing diagnostic; runtime receives question text only."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import re
import time
import uuid

import httpx

from .evaluation_datasets import load_benchmark, stable_id, write_json
from .settings import settings
from .subquery_diagnostic import SubqueryDataset, now, sha, render as render_pairs

VERSION='benchmark-query-router-v1'
MODEL='qwen2.5:14b'
URL='http://127.0.0.1:11434'
OPTIONS=dict(temperature=0,seed=42,num_ctx=8192,num_predict=1400)
PROMPT='''你是通用检索问题分流器，只看题面，不回答问题，不用外部知识补论文内容。
判断是否存在多个可独立查证的证据目标，而非按长度、方法名数量判断复杂度。
decision 四选一：no_split=一个整体检索目标；rule=输入提供的确定性规则候选足以表示各自检索目标；llm=有多个目标且需理解指代、跨句归属或隐式描述才能拆；unclear=题面不足以确定安全拆分。
比较题常需分别查证各对象；无方法名但明确要求找两类不同材料时也可以拆成描述性子查询，不猜测论文名。
如 rule_candidate 为空不得选择 rule；非空也须检查是否漏重要目标。rule 时 queries 留空，程序采用规则候选。
llm 时输出2至4个能独立检索的简短子查询，每个只包含题面已给的信息，可自然改写和消解明确指代。没有明确归属时不把列举的技术词按论文知识强行配对，可保留共同问题并把未归属文字放 unresolved。
no_split或unclear时queries为空，保留原题。quotes是支撑判断或拆分的1至4条连续题面原文，必须逐字存在；reason简短解释目标结构，不能说明论文答案。unresolved记录尚未解决的题面歧义，可为空。所有子查询仅用于补充检索，原题始终保留。只输出JSON。'''
STRINGS=dict(type='array',items=dict(type='string'))
SCHEMA=dict(type='object',additionalProperties=False,properties=dict(
    decision=dict(type='string',enum=['no_split','rule','llm','unclear']),reason=dict(type='string'),
    queries=STRINGS,quotes=STRINGS,unresolved=STRINGS),required=['decision','reason','queries','quotes','unresolved'])

_PUNCTUATION_EQUIVALENTS = str.maketrans({
    '？': '?', '，': ',', '、': ',', '：': ':', '（': '(', '）': ')',
})


def _normalized_quote_span(question, quote, punctuation=False):
    """Find a quote while retaining offsets into the original question.

    The normalized representation stores the original character offset for every
    retained character, so a match can never be used as a source span directly.
    """
    normalized_chars, offsets = [], []
    for index, char in enumerate(question):
        if char.isspace():
            continue
        normalized_chars.append(char.translate(_PUNCTUATION_EQUIVALENTS) if punctuation else char)
        offsets.append(index)
    target = ''.join(
        char.translate(_PUNCTUATION_EQUIVALENTS) if punctuation else char
        for char in quote if not char.isspace()
    )
    if not target:
        return None
    haystack = ''.join(normalized_chars)
    position = haystack.find(target)
    if position < 0:
        return None
    start = offsets[position]
    last = offsets[position + len(target) - 1]
    return start, last + 1


def _locate_quote(question, quote):
    """Return an auditable source span; exact matching remains the fast path."""
    position = question.find(quote)
    if position >= 0:
        return dict(text=quote, start=position, end=position + len(quote),
                    role='decision_support', quote_normalized=False,
                    normalization=None, quoted_text=quote)
    for punctuation, name in ((False, 'whitespace'), (True, 'whitespace_and_punctuation')):
        span = _normalized_quote_span(question, quote, punctuation=punctuation)
        if span is None:
            continue
        start, end = span
        return dict(text=question[start:end], start=start, end=end,
                    role='decision_support', quote_normalized=True,
                    normalization=name, quoted_text=quote)
    raise ValueError('quote_not_in_question: ' + quote)


def rule_candidate(question):
    """One generic grammar: explicit English subject + 的 + topic, parallel ask.

    No alias catalog, benchmark ids, corpus or special method names are used.
    This narrow grammar is deliberately allowed to decline the question.
    """
    sentence=re.split(r'[。？！?!]',question,1)[0]
    pattern=r'(?<![A-Za-z0-9_-])([A-Za-z][A-Za-z0-9_-]*)\s*的\s*'
    anchors=list(re.finditer(pattern,sentence))
    if len(anchors)<2 or len(anchors)>4:return []
    task=re.search(r'(?:怎样分别|如何分别|分别|各(?:会)?)(?:[^。？！?!]*)$',sentence[anchors[-1].end():])
    if not task:return []
    task_start=anchors[-1].end()+task.start()
    shared=sentence[task_start:]
    result=[]
    for i,anchor in enumerate(anchors):
        end=anchors[i+1].start() if i+1<len(anchors) else task_start
        topic=sentence[anchor.end():end].strip(' ，,、与和及')
        if not topic or re.search(r'[，,。；;？?]|前者|后者|它们',topic):return []
        result.append(dict(text=anchor.group(1)+' 的'+topic+' '+shared+'？',
            subject=anchor.group(1),topic=topic,rule='explicit_possessive_parallel_v1'))
    return result


def validate(question,body,candidate):
    if not isinstance(body,dict) or set(body)!=set(SCHEMA['required']):raise ValueError('schema_mismatch')
    decision=body['decision']
    if decision not in ('no_split','rule','llm','unclear'):raise ValueError('unknown_route')
    for key in ('queries','quotes','unresolved'):
        if not isinstance(body[key],list) or not all(isinstance(v,str) and v.strip() for v in body[key]):raise ValueError('invalid_'+key)
    if not body['quotes'] or len(body['quotes'])>4:raise ValueError('missing_or_too_many_quotes')
    spans=[]
    for quote in body['quotes']:
        spans.append(_locate_quote(question, quote))
    if decision=='rule' and not candidate:raise ValueError('rule_route_without_candidate')
    if decision!='llm' and body['queries']:raise ValueError('queries_on_non_llm_route')
    if decision=='llm' and not 2<=len(body['queries'])<=4:raise ValueError('invalid_subquery_count')
    if len(set(body['queries']))!=len(body['queries']):raise ValueError('duplicate_queries')
    # Mechanical invention check only. Chinese factual additions require review.
    source_terms={s.casefold() for s in re.findall(r'[A-Za-z][A-Za-z0-9_-]*',question)}
    for query in body['queries']:
        if len(query)>400:raise ValueError('query_too_long')
        extra={s.casefold() for s in re.findall(r'[A-Za-z][A-Za-z0-9_-]*',query)}-source_terms
        if extra:raise ValueError('new_latin_term: '+','.join(sorted(extra)))
    queries=candidate if decision=='rule' else [dict(text=t) for t in body['queries']]
    return dict(route=decision,subqueries=[dict(id=f'SQ{i:02d}',**q) for i,q in enumerate(queries,1)],
        source_spans=spans,unresolved=body['unresolved'],reason=body['reason'])


def infer(client,question,candidate):
    request=dict(question=question,rule_candidate=[q['text'] for q in candidate])
    response=client.post(URL+'/api/chat',json=dict(model=MODEL,stream=False,format=SCHEMA,options=OPTIONS,keep_alive='30m',
        messages=[dict(role='system',content=PROMPT),dict(role='user',content=json.dumps(request,ensure_ascii=False))]))
    response.raise_for_status();data=response.json()
    usage=dict(prompt_tokens=data['prompt_eval_count'],completion_tokens=data['eval_count'],
        total_tokens=data['prompt_eval_count']+data['eval_count'])
    out=dict(usage=usage,runtime={k:data.get(k) for k in ('done_reason','load_duration','prompt_eval_duration','eval_duration','total_duration')},
        model_input=request,model_calls=1)
    try:
        parsed=json.loads(data['message']['content']);out['parsed_output']=parsed
        if data.get('done_reason')=='length':raise ValueError('output_truncated')
        out.update(validate(question,parsed,candidate),valid=True,validation_errors=[])
    except (ValueError,TypeError,KeyError) as exc:
        out.update(valid=False,route='fallback',subqueries=[],validation_errors=[str(exc)],unresolved=[],reason='校验失败，保留原题')
    return out


def freeze(root):
    folder=root/'artifacts/eval/stage-4'/VERSION
    if (folder/'benchmark.json').exists():return load_benchmark(root,VERSION)[0]
    parent,digest,_=load_benchmark(root,'benchmark-relation-holdout-v1')
    with httpx.Client(timeout=10) as client:model=next(m for m in client.get(URL+'/api/tags').json()['models'] if m['name']==MODEL)
    bench=deepcopy(parent);bench['cases']=[c for c in bench['cases'] if c['id'].startswith('R')]
    bench['units']={u:parent['units'][u] for c in bench['cases'] for u in c['units']}
    for c in bench['cases']:c['generate']=False
    bench.update(version=VERSION,parent_benchmark_sha256=digest,
        dataset_description='24道开发题的通用分流诊断：原题保持 vs 问题结构分流。只测试路由和拆分，不运行召回。',
        prior_exposure='24题均已用于开发；结果不能证明泛化或简单题分类准确率。',
        models=dict(local_router=MODEL,model_digest=model['digest']),
        comparison=dict(mode='generic_question_routing',arms=['Rule','Local-LLM']),
        controls=dict(prompt=PROMPT,schema=SCHEMA,options=OPTIONS,rule='explicit_possessive_parallel_v1',
            runtime_input='question + generic rule candidates only; no catalog, references or case id',
            baseline='Rule label = original question retained without splitting',
            treatment='Local-LLM label = generic router: no_split / rule / llm / unclear; validation failure keeps original',
            original_question='always retained; subqueries auxiliary',no_anchor='not a gate; descriptive search targets allowed',
            generation=False,retrieval=False,embedding=False,reranking=False),
        scoring=dict(primary='逐题审阅目标独立性、分流合理性、拆分是否增添事实或丢任务',
            automatic='路由数、校验通过、子查询数、调用数、Token与耗时；不是语义准确率',
            semantic='Codex题面审阅，非独立人工；不使用答案来赋予方法技术关系',
            limit='此24题均为跨论文设计，不能评估简单题误拆率；模型分流本身每题一次调用',
            latency='wall time includes loading, route and decomposition in one request',negative_policy='not applicable'),
        distribution=dict(cross=24),code_sha256={name:sha(root/name) for name in (
            'src/papertech/query_router_diagnostic.py','scripts/eval-stage4.py','src/papertech/evaluation_details.py')})
    bench.pop('graph_snapshot',None)
    write_json(folder/'benchmark.json',bench);(folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    for name in bench['code_sha256']:
        dest=folder/'runtime-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((root/name).read_bytes())
    return bench


class RouterDataset(SubqueryDataset):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for e in self.payload['examples']:
            e['outputs']['result_display'].update(location='Rule=保持原题 / Local-LLM=通用分流',
                fields=['分流决策与理由','规则候选','补充子查询','未解析内容','机械校验','逐题审阅','Token时延Trace'])
            write_json(self.directory/'cases'/(e['metadata']['case_id']+'.json'),e)
        write_json(self.directory/'langsmith-dataset.json',self.payload)


def report(summary,folder):
    render_pairs(summary,folder)
    rows=[r for r in summary['results'] if r['arm']=='Local-LLM']
    stats=dict(status=summary['status'],questions=len(rows),routes=dict(Counter(r['route'] for r in rows)),
        proposed_routes=dict(Counter((r.get('parsed_output') or {}).get('decision','error') for r in rows)),
        valid=sum(r['valid'] for r in rows),subqueries=sum(len(r['subqueries']) for r in rows),
        wall_seconds=sum(r['seconds'] for r in rows),prompt_tokens=sum((r.get('usage') or {}).get('prompt_tokens',0) for r in rows),
        completion_tokens=sum((r.get('usage') or {}).get('completion_tokens',0) for r in rows),
        note='模型分流本身每题调用；所有题保留原问题；机械校验不保证语义正确。')
    if (folder/'review-notes.json').exists():stats['review']=json.loads((folder/'review-notes.json').read_text(encoding='utf8'))
    write_json(folder/'router-summary.json',stats)
    esc=__import__('html').escape
    lines=['# 通用分流器：24题实测','',json.dumps({k:v for k,v in stats.items() if k!='review'},ensure_ascii=False,indent=2),'',
        '|题号|决策|补充子查询|理由|','|---|---|---|']
    for r in rows:lines.append('|'+r['case_id']+'|'+r['route']+'|'+'<br>'.join(q['text'].replace('|','/') for q in r['subqueries'])+'|'+r['reason'].replace('|','/')+'|')
    (folder/'routing.md').write_text('\n'.join(lines),encoding='utf8')
    panel='<h1>通用分流器：逐题决策</h1><pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre>'
    page=folder/'dashboard.html';page.write_text(page.read_text(encoding='utf8').replace('<h1>',panel+'<h1>',1),encoding='utf8')


def execute(root,prepare_only=False,resume=None):
    bench=freeze(root);recorder=RouterDataset(root,VERSION);cfg=settings(root)
    try:
        if cfg.get('LANGSMITH_API_KEY'):recorder.sync_dataset()
        if prepare_only:print(json.dumps(recorder.status));return
        if resume:
            p=Path(resume);s=json.loads(p.read_text(encoding='utf8'));s['dataset_sync']=recorder.sync_run(p)
            write_json(p,s);report(s,p.parent);print(json.dumps(s['dataset_sync']));return
        for name,digest in bench['code_sha256'].items():
            if sha(root/name)!=digest:raise ValueError('frozen_code_changed:'+name)
        run_id=uuid.uuid4().hex;folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/run_id
        s=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=recorder.digest,started=now(),status='running',results=[])
        write_json(folder/'summary.json',s);report(s,folder)
        print(json.dumps(dict(run_id=run_id,cases=24,status='running')),flush=True)
        try:
            with httpx.Client(timeout=httpx.Timeout(600,connect=10)) as client:
                actual=next(m for m in client.get(URL+'/api/tags').json()['models'] if m['name']==MODEL)
                if actual['digest']!=bench['models']['model_digest']:raise ValueError('model_changed')
                for case in bench['cases']:
                    q=case['question'];candidate=rule_candidate(q)
                    for arm in ('Rule','Local-LLM'):
                        start=now();t=time.monotonic()
                        row=dict(case_id=case['id'],question=q,category='cross',arm=arm,started=start,
                            rule_candidate=candidate,route='no_split',reason='保持原问题基线',original_query=q,
                            subqueries=[],unresolved=[],usage=None,model_calls=0,valid=True,validation_errors=[])
                        if arm=='Local-LLM':row.update(infer(client,q,candidate))
                        row.update(finished=now(),seconds=time.monotonic()-t)
                        row['metrics']=dict(valid_output=int(row['valid']),split_applied=int(bool(row['subqueries'])),
                            subquery_count=len(row['subqueries']),original_retained=1,model_calls=row['model_calls'])
                        row['trace_url']='https://smith.langchain.com/r/'+stable_id(recorder.digest,run_id,case['id'],arm)
                        s['results'].append(row);write_json(folder/(case['id']+'-'+arm+'.json'),row);write_json(folder/'summary.json',s)
                        print(json.dumps(dict(case=case['id'],arm=arm,route=row['route'],queries=[x['text'] for x in row['subqueries']],seconds=round(row['seconds'],2)),ensure_ascii=False),flush=True)
            s['status']='completed'
        except BaseException as exc:
            s.update(status='interrupted',error_type=type(exc).__name__);raise
        finally:
            s['finished']=now();write_json(folder/'summary.json',s);report(s,folder)
            try:
                if cfg.get('LANGSMITH_API_KEY') and s['results']:s['dataset_sync']=recorder.sync_run(folder/'summary.json')
            except Exception as exc:s['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
            write_json(folder/'summary.json',s);report(s,folder)
        print(json.dumps(dict(folder=str(folder),status=s['status'],sync=s.get('dataset_sync')),ensure_ascii=False))
    finally:recorder.close()
