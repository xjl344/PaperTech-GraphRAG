"""Question-only local LLM decomposition; no retrieval or answer generation."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import html
import json
import re
from pathlib import Path
import time
import uuid

import httpx

from .entity_aliases import method_spans, subqueries
from .evaluation_datasets import load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, clean
from .settings import settings

VERSION = 'benchmark-subquery-quality-v2'
ARMS = ('Rule', 'Local-LLM')
MODEL = 'qwen2.5:14b'
BASE_URL = 'http://127.0.0.1:11434'
OPTIONS = dict(temperature=0, seed=42, num_ctx=8192, num_predict=2200)
PROMPT = '''任务是从题面提取子查询素材，绝不回答问题，也不使用论文知识。
只读取 question 和 allowed_methods。按 allowed_methods 顺序，每个方法输出一个单元。
所有 local_aspect、shared_task、unresolved 字符串必须逐字复制题面的连续片段，不改写，不增字，不自行补标点。方法名由程序添加。
local_aspect：只属于该方法的技术描述或任务对象。shared_task：适用于所有方法的共同问题、目的、比较维度和限制。
两个字段不可有重复或重叠的片段。方法专属描述不准放入 shared_task；shared_task 不准包含任何方法名或前者/后者/它们/两者等悬空指代。
若题面写明前者/后者，只按题面两个方法的出现顺序解析，标 assignment=pronoun；原文片段从前者或后者开始，程序负责去除代词。
若技术描述紧接自己的方法名，标 explicit。找不到明确属于某方法的描述，local_aspect 留空，标 shared_only，保留有信息的共享任务。
仅仅列出两个方法、然后列出两种技术，不能凭论文知识或列举顺序猜测对应关系。归属不明的技术片段放 unresolved，不强行分配，也不把它们都当 shared_task。
reason 最多12个汉字，只解释题面依据。不要重复方法名或说明论文答案。
示例题面：甲法与乙法怎样处理输入？前者处理表格，后者处理段落。
甲法的 local_aspect=["前者处理表格"]，乙法的 local_aspect=["后者处理段落"]，两者 shared_task=["怎样处理输入？"]，assignment=pronoun。
示例题面：甲法与乙法怎么编码？比较甲编码和乙编码。
不能猜测编码归属：local_aspect=[]，shared_task=["怎么编码？"]，assignment=shared_only，unresolved=["甲编码和乙编码"]。
必须保留有用的问句目标，不要仅给方法名。只输出 schema JSON。'''

STRING_LIST = dict(type='array', items=dict(type='string'))
SCHEMA = dict(type='object', additionalProperties=False,
    properties=dict(methods=dict(type='array', items=dict(type='object', additionalProperties=False,
        properties=dict(method=dict(type='string'), local_aspect=STRING_LIST, shared_task=STRING_LIST,
            assignment=dict(type='string', enum=['explicit','pronoun','ordered','shared_only']), reason=dict(type='string')),
        required=['method','local_aspect','shared_task','assignment','reason'])), unresolved=STRING_LIST),
    required=['methods','unresolved'])


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anchors_for(question):
    return list(dict.fromkeys(m['method'] for m in method_spans(question)))


def locate(question, text, role):
    if not isinstance(text, str) or not text.strip():
        raise ValueError('empty_or_nonstring_fragment')
    positions = [i for i in range(len(question)) if question.startswith(text, i)]
    if not positions:
        raise ValueError('fragment_not_in_question: ' + text)
    return dict(text=text, role=role, start=positions[0], end=positions[0]+len(text),
                possible_starts=positions, offset_ambiguous=len(positions)>1)


def validate_split(question, body):
    """Exact provenance is checked; semantic ownership still needs review."""
    allowed = anchors_for(question)
    if not isinstance(body, dict) or set(body) != {'methods','unresolved'}:
        raise ValueError('invalid_top_level_schema')
    if not isinstance(body['methods'], list) or not all(isinstance(m,dict) for m in body['methods']) or [m.get('method') for m in body['methods']] != allowed:
        raise ValueError('missing_extra_or_reordered_method')
    output = []
    for i, item in enumerate(body['methods'], 1):
        if set(item) != {'method','local_aspect','shared_task','assignment','reason'}:
            raise ValueError('invalid_method_schema')
        if item['assignment'] not in ('explicit','pronoun','ordered','shared_only') or not isinstance(item['reason'], str):
            raise ValueError('invalid_assignment')
        if item['assignment']=='ordered' and (len(allowed)<2 or not re.search(r'分别|依次|逐一',question)):
            raise ValueError('ordered_assignment_not_explicit_in_question')
        spans = []
        for role in ('local_aspect','shared_task'):
            if not isinstance(item[role], list):
                raise ValueError('invalid_fragment_array')
            if not all(isinstance(text,str) for text in item[role]):
                raise ValueError('invalid_fragment_type')
            spans.extend(locate(question, text, role) for text in dict.fromkeys(item[role]))
        for local in item['local_aspect']:
            if any(local in shared or shared in local for shared in item['shared_task']):
                raise ValueError('local_and_shared_fragments_overlap')
        if item['assignment']=='shared_only' and item['local_aspect']:
            raise ValueError('shared_only_has_local_aspect')
        if any(re.search(r'前者|后者|它们|两者|二者|三者', text) or method_spans(text) for text in item['shared_task']):
            raise ValueError('shared_task_has_method_or_unresolved_pronoun')
        if any(re.search(r'前者|后者', text) for text in item['local_aspect']) and item['assignment']!='pronoun':
            raise ValueError('pronoun_assignment_not_declared')
        # Build the actual query from verified source text; no free-form rewrite.
        parts, transformations = [], []
        for span in spans:
            text = span['text']
            if item['assignment']=='pronoun' and span['role']=='local_aspect':
                transformed=re.sub(r'^(?:比较|和)?\s*(?:前者|后者)\s*', '', text)
                if transformed != text:
                    text=transformed
                    transformations.append(dict(kind='remove_resolved_pronoun', source=span['text'], result=text))
            parts.append(text)
        output.append(dict(id=f'SQ{i:02d}', method=item['method'],
            text=' '.join([item['method']]+parts), subquery_source='llm_spans',
            local_aspect=item['local_aspect'], shared_task=item['shared_task'],
            assignment=item['assignment'], reason=item['reason'], source_spans=spans,
            transformations=transformations, method_only=not bool(parts)))
    if not isinstance(body['unresolved'], list):
        raise ValueError('invalid_unresolved_array')
    unresolved = [locate(question, text, 'unresolved') for text in body['unresolved']]
    return dict(subqueries=output, unresolved=unresolved)


def freeze(root):
    folder = root/'artifacts/eval/stage-4'/VERSION
    if (folder/'benchmark.json').exists():
        return load_benchmark(root, VERSION)[0]
    parent, digest, _ = load_benchmark(root, 'benchmark-relation-holdout-v1')
    with httpx.Client(timeout=15) as client:
        tags = client.get(BASE_URL+'/api/tags').raise_for_status().json()['models']
    model = next(m for m in tags if m['name']==MODEL)
    bench = deepcopy(parent)
    bench['cases'] = [c for c in bench['cases'] if c['id'].startswith('R')]
    if [c['id'] for c in bench['cases']] != [f'R{i:02d}' for i in range(1,25)]:
        raise ValueError('expected_24_cross_paper_cases')
    bench['units'] = {k: parent['units'][k] for c in bench['cases'] for k in c['units']}
    for case in bench['cases']:
        case['generate'] = False
    bench.update(version=VERSION, parent_benchmark_sha256=digest,
        dataset_description='24道已曝光跨论文开发题：规则与本地Qwen题面拆分质量；不是检索或答案准确率评测。',
        prior_exposure='既有开发题；本次仅比较题面解析，不声称泛化效果。',
        distribution=dict(cross=24), comparison=dict(mode='question_decomposition',arms=list(ARMS)),
        models=dict(local_decomposer=MODEL,model_digest=model['digest']),
        controls=dict(arms=list(ARMS),prompt=PROMPT,schema=SCHEMA,options=OPTIONS,
            inputs='question + explicit method names only',corpus_or_reference_in_model=False,
            no_anchor='keep original question, skip LLM',query_assembly='verified source snippets; resolved pronoun prefix may be removed',
            retrieval=False,embedding=False,reranking=False,answer_generation=False),
        scoring=dict(automatic=['valid source fragments','method coverage','non-method-only output','shared-task presence'],
            semantic='Codex review of task retention and ownership; not independent human scoring',
            rubric=['only named methods','no invented facts','no unsupported method/technical-term pairing',
                    'retain per-method retrieval target','record unresolved text','preserve no-anchor behavior'],
            primary='逐题保留目标与归属质量审阅；不把JSON成功当质量成功',
            latency='wall time includes model load; separately report load/prompt/eval durations',
            tokens='Ollama prompt_eval_count / eval_count; no estimation',
            negative_policy='not applicable: no answer evaluation'),
        code_sha256={name:sha(root/name) for name in (
            'src/papertech/entity_aliases.py','src/papertech/subquery_diagnostic.py',
            'scripts/eval-stage4.py','src/papertech/evaluation_details.py')})
    bench.pop('graph_snapshot', None)
    write_json(folder/'benchmark.json', bench)
    (folder/'benchmark.sha256').write_text(sha(folder/'benchmark.json')+'\n',encoding='utf8')
    return bench


class SubqueryDataset(DetailedEvaluationDataset):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.payload['description']=self.bench['dataset_description']
        for example in self.payload['examples']:
            example['outputs']['decomposition_rubric']=deepcopy(self.bench['scoring'])
            example['outputs']['evaluation_config']['planned_output']='题面子查询拆分；不运行检索或答案生成'
            example['outputs']['result_display'].update(location='Rule / Local-LLM Experiments',
                fields=['子查询原文','题面来源片段与偏移','归属与未解析内容','机械校验','时延与Token','逐题质量审阅','Trace'])
            write_json(self.directory/'cases'/(example['metadata']['case_id']+'.json'),example)
        write_json(self.directory/'langsmith-dataset.json',self.payload)

    def sync_run(self,summary_path,answer_mode='full'):
        folder=Path(summary_path).parent
        summary=json.loads(Path(summary_path).read_text(encoding='utf8'))
        if summary['benchmark_sha256']!=self.digest:
            raise ValueError('benchmark_mismatch')
        dataset=self.sync_dataset()
        payloads=[]
        for row in summary['results']:
            rid=stable_id(self.digest,summary['run_id'],row['case_id'],row['arm'])
            payloads.append(dict(id=rid,name='question-decomposition',run_type='chain',
                inputs=dict(question=row['question']),outputs=clean(row),
                reference_example_id=stable_id(self.digest,row['case_id']),start_time=row['started'],end_time=row['finished'],
                extra=dict(metadata=dict(benchmark=self.bench['version'],arm=row['arm'],case_id=row['case_id'],
                    task='question_decomposition',original_run_id=summary['run_id'])),_arm=row['arm'],_metrics=row['metrics']))
        if summary['status']=='completed' and {(r['case_id'],r['arm']) for r in summary['results']}!={(c['id'],a) for c in self.bench['cases'] for a in ARMS}:
            raise ValueError('incomplete_pairs')
        write_json(folder/'langsmith-experiments.json',dict(runs=payloads))
        experiments=[]
        for arm in ARMS:
            name=f'papertech-{self.bench["version"]}-{summary["run_id"][:12]}-{arm}'
            project=self.client.create_project(name,reference_dataset_id=dataset.id,upsert=True,
                description=self.bench['dataset_description'],metadata=dict(arm=arm,benchmark_sha256=self.digest))
            expected={p['id']:p for p in payloads if p['_arm']==arm}
            existing={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
            for rid,p in expected.items():
                if rid in existing:
                    if existing[rid].outputs!=p['outputs']:
                        raise ValueError('remote_result_changed')
                    continue
                data={k:v for k,v in p.items() if not k.startswith('_')}
                data['start_time']=datetime.fromisoformat(data['start_time'])
                data['end_time']=datetime.fromisoformat(data['end_time'])
                self.client.create_run(project_name=name,**data)
            for p in expected.values():
                usage=p['outputs'].get('usage')
                if not usage: continue
                child_id=stable_id(p['id'],'local-decomposition-usage')
                try:
                    self.client.read_run(child_id)
                    continue
                except Exception as exc:
                    if type(exc).__name__!='LangSmithNotFoundError': raise
                native=dict(input_tokens=usage['prompt_tokens'],output_tokens=usage['completion_tokens'],total_tokens=usage['total_tokens'])
                parent=self.client.read_run(p['id'])
                child_start=datetime.fromisoformat(p['start_time'])
                self.client.create_run(id=child_id,name=MODEL,run_type='llm',project_name=name,
                    parent_run_id=p['id'],trace_id=p['id'],
                    dotted_order=parent.dotted_order+'.'+child_start.strftime('%Y%m%dT%H%M%S%fZ')+child_id,
                    inputs=dict(question=p['inputs']['question'],allowed_methods=anchors_for(p['inputs']['question'])),
                    outputs=dict(subqueries=p['outputs']['subqueries'],usage_metadata=native),
                    start_time=datetime.fromisoformat(p['start_time']),end_time=datetime.fromisoformat(p['end_time']),
                    extra=dict(metadata=dict(ls_provider='ollama',ls_model_name=MODEL,usage_metadata=native)))
            present={str(f.id) for f in self.client.list_feedback(run_ids=list(expected))}
            jobs=[dict(run_id=p['id'],key=k,score=float(v),feedback_id=stable_id(p['id'],k),session_id=project.id,
                       comment='题面拆分机械指标；不是语义准确率或检索覆盖率。')
                  for p in expected.values() for k,v in p['_metrics'].items() if v is not None]
            for job in jobs:
                if job['feedback_id'] not in present: self.client.create_feedback(**job)
            for attempt in range(8):
                remote={str(r.id):r for r in self.client.list_runs(project_id=project.id,is_root=True)}
                feedback={str(f.id):f for f in self.client.list_feedback(run_ids=list(expected))}
                valid=set(remote)==set(expected) and all(r.outputs==expected[rid]['outputs'] and
                    r.inputs==expected[rid]['inputs'] and str(r.reference_example_id)==expected[rid]['reference_example_id'] for rid,r in remote.items())
                valid=valid and all(j['feedback_id'] in feedback and abs(feedback[j['feedback_id']].score-j['score'])<.000051 for j in jobs)
                if valid: break
                if attempt==7: raise ValueError('remote_readback_incomplete')
                time.sleep(2)
            experiments.append(dict(arm=arm,project_id=str(project.id),runs_verified=len(remote),feedback_verified=len(jobs)))
        self.status.update(status='experiments_verified',experiments=experiments,
            comparison_url=dataset.url+'/compare?selectedSessions='+','.join(e['project_id'] for e in experiments))
        write_json(folder/'langsmith-status.json',self.status)
        write_json(self.status_path,self.status)
        return deepcopy(self.status)


def row_metrics(rows,valid,applied):
    return dict(valid_source_output=int(valid),split_applied=int(applied),
        subquery_count=len(rows),non_method_only_count=sum(not r.get('method_only',r.get('subquery_source')=='method_only') for r in rows),
        task_present_count=sum(bool(r.get('shared_task')) or any(s['role']=='shared_question' for s in r.get('source_spans',[])) for r in rows))


def model_split(client,question):
    body=dict(question=question,allowed_methods=anchors_for(question))
    response=client.post(BASE_URL+'/api/chat',json=dict(model=MODEL,stream=False,format=SCHEMA,
        keep_alive='30m',options=OPTIONS,messages=[dict(role='system',content=PROMPT),
        dict(role='user',content=json.dumps(body,ensure_ascii=False))]))
    response.raise_for_status()
    data=response.json()
    content=data['message']['content']
    parsed=json.loads(content)
    result=dict(parsed_output=parsed,usage=dict(prompt_tokens=data['prompt_eval_count'],
        completion_tokens=data['eval_count'],total_tokens=data['prompt_eval_count']+data['eval_count']),
        runtime={k:data.get(k) for k in ('done_reason','total_duration','load_duration','prompt_eval_duration','eval_duration')})
    try:
        if data.get('done_reason')=='length': raise ValueError('output_truncated')
        result.update(validate_split(question,parsed),validation_errors=[],valid=True)
    except (ValueError,TypeError,KeyError) as exc:
        result.update(subqueries=[],unresolved=[],valid=False,validation_errors=[str(exc)])
    return result


def render(summary,folder):
    esc=html.escape
    stats={a:dict(cases=0,applied=0,subqueries=0,method_only=0,invalid=0,seconds=0,prompt_tokens=0,completion_tokens=0) for a in ARMS}
    for row in summary['results']:
        s=stats[row['arm']];s['cases']+=1;s['applied']+=bool(row['subqueries']);s['subqueries']+=len(row['subqueries'])
        s['method_only']+=sum(r.get('method_only',r.get('subquery_source')=='method_only') for r in row['subqueries'])
        s['invalid']+=not row['valid'];s['seconds']+=row['seconds']
        for k in ('prompt_tokens','completion_tokens'):s[k]+=(row.get('usage') or {}).get(k,0)
    write_json(folder/'comparison.json',dict(status=summary['status'],statistics=stats))
    lines=['# 规则与本地模型：子查询拆分质量','',f"状态：{summary['status']}；24道已曝光开发题，不是检索实验。",'',
        '机械校验不等于语义质量；引用题面原文也可能分错方法。未运行召回、Embedding、重排或答案生成。','',
        '|组|已完成题|拆分题|子查询|仅方法名|校验失败|秒|输入Token|输出Token|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a,s in stats.items():lines.append(f"|{a}|{s['cases']}|{s['applied']}|{s['subqueries']}|{s['method_only']}|{s['invalid']}|{s['seconds']:.2f}|{s['prompt_tokens']}|{s['completion_tokens']}|")
    page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>本地模型子查询拆分</title><style>body{font:16px/1.65 system-ui;max-width:1400px;margin:25px auto;padding:15px;background:#f3f6fa;color:#172235}article{background:white;padding:20px;margin:18px 0;border-radius:8px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}small{color:#526174}li{margin:8px 0}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style>',
        f'<h1>规则与本地 Qwen2.5-14B：题面拆分</h1><p>{esc(summary["status"])}；仅拆分，不跑检索。机械校验与语义质量分开。</p>',
        '<pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre>']
    # Required summary chart: output specificity is descriptive, not accuracy.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 130"><title>带题面描述的子查询数量，不是准确率</title>']
    for i,a in enumerate(ARMS):
        n=stats[a]['subqueries']-stats[a]['method_only'];y=15+i*45
        svg.append(f'<text x="0" y="{y+20}">{a}</text><rect x="140" y="{y}" width="{n*12}" height="27" fill="{("#3975b7","#bd653e")[i]}"/><text x="{150+n*12}" y="{y+20}">{n}</text>')
    svg.append('<text x="140" y="125">带题面描述的子查询数量；不是语义准确率</text></svg>')
    (folder/'specificity.svg').write_text(''.join(svg),encoding='utf8');page.append(''.join(svg))
    categories={}
    category_stats={}
    for cid in [f'R{i:02d}' for i in range(1,25)]:
        rows={r['arm']:r for r in summary['results'] if r['case_id']==cid}
        if not rows:continue
        question=next(iter(rows.values()))['question']
        kind='no_anchor' if not method_spans(question) else 'anchored'
        categories.setdefault(kind,[]).append(cid)
        for arm,row in rows.items():
            stat=category_stats.setdefault(kind,{}).setdefault(arm,
                dict(cases=0,subqueries=0,method_only=0,invalid=0,seconds=0,prompt_tokens=0,completion_tokens=0))
            stat['cases']+=1;stat['subqueries']+=len(row['subqueries'])
            stat['method_only']+=sum(r.get('method_only',r.get('subquery_source')=='method_only') for r in row['subqueries'])
            stat['invalid']+=not row['valid'];stat['seconds']+=row['seconds']
            for k in ('prompt_tokens','completion_tokens'):stat[k]+=(row.get('usage') or {}).get(k,0)
        lines+=['',f'## {cid}', '',question,'']
        page.append(f'<article id="{cid}"><h2>{cid}</h2><p>{esc(question)}</p><div class="pair">')
        for arm in ARMS:
            row=rows.get(arm)
            if row is None:page.append(f'<section><h3>{arm}</h3>未运行</section>');continue
            lines += [f'### {arm}','']
            page.append(f'<section><h3>{arm}</h3><ul>')
            for item in row['subqueries']:
                lines.append('- '+item['text']);page.append('<li>'+esc(item['text'])+'</li>')
            if not row['subqueries']:lines.append('- 保持原问题 / 校验失败，见详细记录');page.append('<li>保持原问题 / 校验失败，见详细记录</li>')
            page.append('</ul><details><summary>片段、归属、未解析内容与成本</summary><pre>'+esc(json.dumps(row,ensure_ascii=False,indent=2))+'</pre></details></section>')
            lines+=['','未解析：'+json.dumps(row.get('unresolved',[]),ensure_ascii=False), '校验：'+json.dumps(row.get('validation_errors',[]),ensure_ascii=False)]
        page.append('</div></article>')
    write_json(folder/'categories.json',dict(case_ids=categories,statistics=category_stats))
    lines+=['','## 分类统计','','```json',json.dumps(category_stats,ensure_ascii=False,indent=2),'```']
    page.append('<h2>分类与成本</h2><pre>'+esc(json.dumps(dict(case_ids=categories,statistics=category_stats),ensure_ascii=False,indent=2))+'</pre>')
    if summary.get('dataset_sync',{}).get('comparison_url'):
        url=summary['dataset_sync']['comparison_url'];lines+=['','[LangSmith 对照]('+url+')'];page.append('<a href="'+esc(url,quote=True)+'">LangSmith 对照</a>')
    (folder/'findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (folder/'dashboard.html').write_text(''.join(page)+'</html>',encoding='utf8')


def execute(root,prepare_only=False,resume=None):
    bench=freeze(root)
    recorder=SubqueryDataset(root,VERSION)
    cfg=settings(root)
    try:
        if cfg.get('LANGSMITH_API_KEY'):recorder.sync_dataset()
        if prepare_only:
            print(json.dumps(recorder.status,ensure_ascii=False));return
        if resume:
            path=Path(resume)
            summary=json.loads(path.read_text(encoding='utf8'))
            summary['dataset_sync']=recorder.sync_run(path)
            write_json(path,summary);render(summary,path.parent)
            print(json.dumps(summary['dataset_sync'],ensure_ascii=False));return
        for name,digest in bench['code_sha256'].items():
            if sha(root/name)!=digest:raise ValueError('frozen_code_changed:'+name)
        with httpx.Client(timeout=15) as health:
            tags=health.get(BASE_URL+'/api/tags').raise_for_status().json()['models']
        actual=next((m for m in tags if m['name']==MODEL),None)
        if not actual or actual.get('digest')!=bench['models']['model_digest']:
            raise ValueError('local_model_digest_changed')
        run_id=uuid.uuid4().hex
        folder=root/'artifacts/reports/stage-4'/VERSION/'runs'/run_id
        summary=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=recorder.digest,started=now(),status='running',results=[])
        write_json(folder/'summary.json',summary);render(summary,folder)
        print(json.dumps(dict(run_id=run_id,status='running',cases=24)),flush=True)
        with httpx.Client(timeout=httpx.Timeout(600,connect=10)) as client:
            try:
                for case in bench['cases']:
                    q=case['question']
                    for arm in ARMS:
                        started=now();clock=time.monotonic();applied=bool(subqueries(q))
                        common=dict(case_id=case['id'],question=q,category='cross',arm=arm,started=started,
                            validation_errors=[],unresolved=[],usage=None,valid=True,model_calls=0)
                        if arm=='Rule':common['subqueries']=subqueries(q)
                        elif not applied:common.update(subqueries=[],skip_reason='no_multiple_source_anchors')
                        else:
                            common.update(model_split(client,q),model_calls=1)
                        common.update(finished=now(),seconds=time.monotonic()-clock)
                        common['metrics']=row_metrics(common['subqueries'],common['valid'],applied)
                        common['trace_url']=f'https://smith.langchain.com/r/{stable_id(recorder.digest,run_id,case["id"],arm)}'
                        summary['results'].append(common)
                        write_json(folder/(case['id']+'-'+arm+'.json'),common)
                        write_json(folder/'summary.json',summary)
                        print(json.dumps(dict(case=case['id'],arm=arm,valid=common['valid'],seconds=round(common['seconds'],2),queries=[r['text'] for r in common['subqueries']]),ensure_ascii=False),flush=True)
                summary['status']='completed'
            except BaseException as exc:
                summary.update(status='interrupted',error_type=type(exc).__name__)
                raise
            finally:
                summary['finished']=now();write_json(folder/'summary.json',summary);render(summary,folder)
                try:
                    if cfg.get('LANGSMITH_API_KEY') and summary['results']:
                        summary['dataset_sync']=recorder.sync_run(folder/'summary.json')
                except Exception as exc:
                    summary['dataset_sync']=dict(status='pending_sync',error_type=type(exc).__name__)
                write_json(folder/'summary.json',summary);render(summary,folder)
        print(json.dumps(dict(folder=str(folder),status=summary['status'],dataset_sync=summary.get('dataset_sync')),ensure_ascii=False))
    finally:
        recorder.close()
