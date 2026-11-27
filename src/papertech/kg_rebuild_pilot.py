"""Independent 14B mechanism-edge extraction pilot.

This module deliberately does not import the production KG ledger or graph
writer. Its output is a versioned JSON graph artifact for review only.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
import uuid

import httpx

from .corpus import load_corpus
from .kg import locate_quote
from .subquery_diagnostic import sha

VERSION='kg-rebuild-pilot-14b-v4'
MODEL='qwen2.5:14b'
OLLAMA_URL='http://127.0.0.1:11434'
PILOT_PAPERS=(
    'paper_42a876c95c3fe85af679c0dbc03a8a7d',  # G-Retriever
    'paper_cedbfddc8030ded4258640a1e0a0a733',  # StructGPT
    'paper_0d99e8c368a360985899fcc4ff0ba156',  # STaRK
)
SMOKE_ORDINALS={PILOT_PAPERS[0]:18,PILOT_PAPERS[1]:11,PILOT_PAPERS[2]:22}
RELATIONS={
    ('Method','HAS_COMPONENT','Component'),
    ('Component','IMPLEMENTS','Mechanism'),
    ('Method','CONTROLLED_BY','Parameter'),
}
ENTITY_TYPES=('Method','Component','Mechanism','Parameter')
PREDICATES=tuple(sorted(x[1] for x in RELATIONS))
OPTIONS=dict(temperature=0,seed=42,num_ctx=4096,num_predict=3000)
SCHEMA={
    'type':'object','additionalProperties':False,
    'properties':{'relations':{'type':'array','maxItems':20,'items':{
        'type':'object','additionalProperties':False,'properties':{
            'subject_type':{'type':'string','enum':['Method','Component']},
            'subject':{'type':'string'},'predicate':{'type':'string','enum':list(PREDICATES)},
            'object_type':{'type':'string','enum':list(ENTITY_TYPES)},'object':{'type':'string'},
            'evidence_quote':{'type':'string'},'claim_kind':{'type':'string','enum':['author_assertion','system_inference']},
            'confidence':{'type':'number','minimum':0,'maximum':1}},
        'required':['subject_type','subject','predicate','object_type','object','evidence_quote','claim_kind','confidence']}},},
    'required':['relations']}


def utcnow(): return datetime.now(timezone.utc).isoformat()
def stable_id(*parts): return hashlib.sha256('\0'.join(map(str,parts)).encode()).hexdigest()


def prompt_for(chunk,paper):
    relations='\n'.join(f'- {s} --{p}--> {o}' for s,p,o in sorted(RELATIONS))
    return f'''你是论文原文关系抽取器。只从给定的单个原文块抽取明确写出的机制关系，不使用外部知识，不把模型推断当作事实，不读取参考文献区。
只允许以下三种关系：
{relations}

约束：
1. 只输出原文明确表达的关系。没有明确证据就不输出。
2. 每条 evidence_quote 必须是给定原文中连续的、可定位的原文片段；允许换行或连续空格不同，但不得改写。
3. claim_kind 必须为 author_assertion；无法确定作者明确陈述时不要输出。system_inference 仅用于记录被拒绝的候选，不应作为有效关系。
4. subject/object 名称要短且具体，不要把整句放进去；不要创造论文中不存在的组件、机制或参数。
5. 最多20条；按原文出现顺序输出。关系可以为空。
6. 三类关系的类型必须严格对应；禁止 Method --IMPLEMENTS--> Mechanism。HAS_COMPONENT 表示方法明确包含的模块或阶段；IMPLEMENTS 表示组件明确实现的操作机制；CONTROLLED_BY 表示调节方法行为的参数，不是报告的性能数字。
7. 标题仅用于辨认论文，不足以证明某个组件归属该方法。只有本块明确的框架描述或指代才可建立归属；不要把相关工作里的其他方法归到本文方法下。
论文：{paper['title']}
页码：{chunk['page_start']}-{chunk['page_end']}
章节：{chunk.get('section','')}
原文块：
<chunk>
{chunk['text']}
</chunk>'''


def validate(body,chunk,paper):
    if not isinstance(body,dict) or set(body)!= {'relations'} or not isinstance(body['relations'],list):
        return [],[{'reason':'invalid_top_level'}]
    valid=[];rejected=[]
    for i,candidate in enumerate(body['relations'][:20]):
        if not isinstance(candidate,dict):rejected.append({'index':i,'reason':'not_object'});continue
        expected_fields={'subject_type','subject','predicate','object_type','object','evidence_quote','claim_kind','confidence'}
        s,p,o= candidate.get('subject_type'),candidate.get('predicate'),candidate.get('object_type')
        subject,obj,quote,kind,confidence=(candidate.get(k) for k in ('subject','object','evidence_quote','claim_kind','confidence'))
        reason=None
        if set(candidate)!=expected_fields:reason='output_fields_invalid'
        elif (s,p,o) not in RELATIONS:reason='relation_signature_not_allowed'
        elif not all(isinstance(x,str) and x.strip() for x in (subject,obj,quote)):reason='empty_field'
        elif max(map(len,(subject,obj,quote)))>1000:reason='field_too_long'
        elif kind!='author_assertion':reason='system_inference_rejected'
        elif not isinstance(confidence,(int,float)) or isinstance(confidence,bool) or not 0<=confidence<=1:reason='confidence_invalid'
        elif locate_quote(chunk['text'],quote) is None:reason='evidence_quote_not_in_chunk'
        if reason:
            rejected.append({'index':i,'reason':reason,'candidate':candidate});continue
        matched=locate_quote(chunk['text'],quote)
        quote_start=chunk['text'].index(matched)
        valid.append(dict(claim_id=stable_id(VERSION,chunk['paper_id'],chunk['chunk_id'],s,subject,p,obj,matched),
            graph_version=VERSION,paper_id=chunk['paper_id'],paper_title=paper['title'],chunk_id=chunk['chunk_id'],
            subject_type=s,subject=subject.strip(),predicate=p,object_type=o,object=obj.strip(),
            evidence_quote=matched,quote_match_method='exact' if quote in chunk['text'] else 'whitespace_normalized',
            quote_start=quote_start,quote_end=quote_start+len(matched),source_spans=deepcopy(chunk.get('source_spans',[])),
            page_start=chunk['page_start'],page_end=chunk['page_end'],section=chunk.get('section'),claim_kind=kind,
            confidence=float(confidence),review_status='pending',source_relative_path=chunk['source_relative_path'],
            source_sha256=paper['source_sha256'],parse_id=chunk['parse_id'],model=MODEL,prompt_version=VERSION,
            schema_version=VERSION))
    if len(body['relations'])>20:rejected.append({'reason':'relation_count_exceeded','count':len(body['relations'])})
    return valid,rejected


def selected_corpus(root):
    corpus,papers,chunks=load_corpus(root);selected=set(PILOT_PAPERS)
    papers=[p for p in papers if p['paper_id'] in selected]
    chunks=[c for c in chunks if c['paper_id'] in selected and c['relation_extraction_eligible'] and c['content_kind']!='references']
    if {p['paper_id'] for p in papers}!=selected:raise ValueError('pilot_paper_missing')
    if not chunks:raise ValueError('pilot_no_chunks')
    return corpus,papers,chunks


def freeze(root):
    folder=root/'artifacts/eval/stage-3'/VERSION;folder.mkdir(parents=True,exist_ok=True)
    path=folder/'pilot.json'
    if path.exists():
        bench=json.loads(path.read_text(encoding='utf8'))
        verify_freeze(root,bench)
        return bench
    corpus,papers,chunks=selected_corpus(root)
    with httpx.Client(timeout=15) as client:
        models=client.get(OLLAMA_URL+'/api/tags').raise_for_status().json().get('models',[])
    model=next((x for x in models if x.get('name')==MODEL),None)
    if not model:raise ValueError('qwen14b_model_not_available')
    bench=dict(version=VERSION,created_at=utcnow(),model=MODEL,base_corpus_id=corpus,
        model_digest=model.get('digest'),
        graph_namespace=VERSION,legacy_graph_excluded=True,options=OPTIONS,prompt_template=prompt_for(dict(text='{text}',page_start='{start}',page_end='{end}',section='{section}'),dict(title='{title}')),output_schema=SCHEMA,
        papers=[dict(paper_id=p['paper_id'],title=p['title'],source_sha256=p['source_sha256']) for p in papers],
        chunks=[dict(chunk_id=c['chunk_id'],paper_id=c['paper_id'],text_sha256=c['text_sha256'],page_start=c['page_start'],page_end=c['page_end'],section=c.get('section'),content_kind=c.get('content_kind')) for c in chunks],
        relations=[dict(subject_type=s,predicate=p,object_type=o) for s,p,o in sorted(RELATIONS)],
        smoke_samples=[dict(paper_id=c['paper_id'],chunk_id=c['chunk_id'],ordinal=c['ordinal'],selection='fixed substantive methods/process passage; smoke only') for c in smoke_chunks(chunks)],
        controls=dict(max_items=20,all_eligible_non_reference_chunks=True,paragraph_second_pass=False,
            valid_claim_kind='author_assertion only',source_quote_required=True,production_chain_untouched=True),
        hashes=dict(corpus_manifest=sha(root/'artifacts/reports/stage-1/current-parses.json'),
            code=sha(root/'src/papertech/kg_rebuild_pilot.py')))
    bench['sha256']=hashlib.sha256(json.dumps(bench,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    (path).write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return bench


def verify_freeze(root,bench):
    payload={k:v for k,v in bench.items() if k!='sha256'}
    if hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()!=bench['sha256']:
        raise ValueError('pilot_manifest_hash_mismatch')
    if bench['hashes']['code']!=sha(root/'src/papertech/kg_rebuild_pilot.py'):
        raise ValueError('pilot_code_changed_create_new_version')
    corpus,papers,chunks=selected_corpus(root)
    if corpus!=bench['base_corpus_id'] or [(c['chunk_id'],c['text_sha256']) for c in chunks]!=[(c['chunk_id'],c['text_sha256']) for c in bench['chunks']]:
        raise ValueError('pilot_corpus_changed')
    if {p['paper_id']:p['source_sha256'] for p in papers}!={p['paper_id']:p['source_sha256'] for p in bench['papers']}:
        raise ValueError('pilot_sources_changed')


class PilotExtractor:
    def __init__(self,client=None,base_url=OLLAMA_URL,model=MODEL):
        self.client=client or httpx.Client(timeout=httpx.Timeout(900,connect=10));self.owns=client is None;self.base_url=base_url.rstrip('/');self.model=model
    def close(self):
        if self.owns:self.client.close()
    def extract(self,chunk,paper):
        attempted_at=utcnow()
        started=time.monotonic();response=self.client.post(self.base_url+'/api/generate',json=dict(model=self.model,prompt=prompt_for(chunk,paper),stream=False,format=SCHEMA,options=OPTIONS,keep_alive='30m'));response.raise_for_status();body=response.json()
        if body.get('done_reason')=='length':raise ValueError('output_truncated')
        parsed=json.loads(body['response']);valid,rejected=validate(parsed,chunk,paper)
        return dict(chunk_id=chunk['chunk_id'],status='completed',relations=valid,rejected=rejected,raw_count=len(parsed.get('relations',[])) if isinstance(parsed,dict) else None,
            input_tokens=body.get('prompt_eval_count'),output_tokens=body.get('eval_count'),duration_ns=body.get('total_duration'),seconds=time.monotonic()-started,
            done_reason=body.get('done_reason'),attempted_at=attempted_at,finished_at=utcnow(),parsed_output=parsed,
            runtime={k:body.get(k) for k in ('load_duration','prompt_eval_duration','eval_duration')})


def graph_from_claims(claims):
    entities={};edges=[]
    for c in claims:
        for typ,name in ((c['subject_type'],c['subject']),(c['object_type'],c['object'])):
            key=(c['paper_id'],typ,name.casefold());entities.setdefault(key,dict(entity_id=stable_id(VERSION,*key),paper_id=c['paper_id'],entity_type=typ,name=name,graph_version=VERSION))
        edges.append(dict(claim_id=c['claim_id'],subject_id=entities[(c['paper_id'],c['subject_type'],c['subject'].casefold())]['entity_id'],object_id=entities[(c['paper_id'],c['object_type'],c['object'].casefold())]['entity_id'],predicate=c['predicate'],chunk_id=c['chunk_id'],evidence_quote=c['evidence_quote'],paper_id=c['paper_id'],review_status='pending'))
    return list(entities.values()),edges


def smoke_chunks(chunks):
    """Pick frozen, question-independent passages to check schema and latency."""
    selected=[]
    for paper_id in PILOT_PAPERS:
        rows=[c for c in chunks if c['paper_id']==paper_id]
        selected.append(next((c for c in rows if c['ordinal']==SMOKE_ORDINALS[paper_id]),rows[0]))
    return selected


def smoke(root):
    bench=freeze(root);_,papers,chunks=selected_corpus(root);paper_map={p['paper_id']:p for p in papers}
    # Section labels are unreliable (a table header can be called "Method").
    selected=smoke_chunks(chunks)
    cache_path=root/'.cache'/VERSION/'validated-cache.json';cache_path.parent.mkdir(parents=True,exist_ok=True)
    cache=json.loads(cache_path.read_text(encoding='utf8')) if cache_path.exists() else {}
    extractor=PilotExtractor();results=[]
    try:
        for chunk in selected:
            key=stable_id(VERSION,MODEL,chunk['chunk_id'],chunk['text_sha256'])
            if key in cache:result=deepcopy(cache[key]);result['reused_from_cache']=True
            else:
                result=extractor.extract(chunk,paper_map[chunk['paper_id']]);cache[key]=deepcopy(result)
                cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            result.update(paper_id=chunk['paper_id'],paper_title=paper_map[chunk['paper_id']]['title'],section=chunk.get('section'),page_start=chunk['page_start'],chunk_id=chunk['chunk_id'])
            results.append(result)
    finally:extractor.close()
    folder=root/'artifacts/reports/stage-3'/VERSION;folder.mkdir(parents=True,exist_ok=True)
    payload=dict(version=VERSION,model=MODEL,model_digest=bench['model_digest'],total_chunks=len(chunks),sample_count=len(results),results=results,
        summary=dict(status='completed' if all(r['status']=='completed' for r in results) else 'completed_with_failures',claims=sum(len(r.get('relations',[])) for r in results),rejected=sum(len(r.get('rejected',[])) for r in results),seconds=sum(r.get('seconds',0) for r in results),input_tokens=sum(r.get('input_tokens') or 0 for r in results),output_tokens=sum(r.get('output_tokens') or 0 for r in results)))
    (folder/'smoke.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return payload


def run(root,resume_id=None,limit=None):
    bench=freeze(root);folder=root/'artifacts/reports/stage-3'/VERSION;run_id=resume_id or uuid.uuid4().hex;run_dir=folder/'runs'/run_id;run_dir.mkdir(parents=True,exist_ok=True)
    checkpoint=run_dir/'checkpoint.json'
    if resume_id and not checkpoint.exists():raise ValueError('pilot_resume_checkpoint_missing')
    existing=json.loads(checkpoint.read_text(encoding='utf8')) if checkpoint.exists() else {'run_id':run_id,'pilot_sha256':bench['sha256'],'status':'running','results':[],'started_at':utcnow()}
    if existing.get('pilot_sha256')!=bench['sha256'] or existing.get('run_id')!=run_id:raise ValueError('pilot_resume_contract_mismatch')
    _,papers,chunks=selected_corpus(root);paper_map={p['paper_id']:p for p in papers}
    if limit is not None:
        if not 1<=limit<=len(chunks):raise ValueError('pilot_limit_out_of_range')
        chunks=chunks[:limit]
        allowed={c['chunk_id'] for c in chunks}
        if any(r['chunk_id'] not in allowed for r in existing['results']):raise ValueError('pilot_resume_limit_mismatch')
    existing['total_chunks']=len(chunks);done={r['chunk_id'] for r in existing['results']}
    cache_path=root/'.cache'/VERSION/'validated-cache.json';cache_path.parent.mkdir(parents=True,exist_ok=True)
    cache=json.loads(cache_path.read_text(encoding='utf8')) if cache_path.exists() else {}
    cache_key=lambda c:stable_id(VERSION,MODEL,c['chunk_id'],c['text_sha256'])
    extractor=PilotExtractor();started=utcnow()
    try:
        for index,chunk in enumerate(chunks,1):
            if chunk['chunk_id'] in done:continue
            try:
                key=cache_key(chunk)
                if key in cache:
                    result=deepcopy(cache[key]);result['reused_from_cache']=True
                else:
                    result=extractor.extract(chunk,paper_map[chunk['paper_id']])
                    cache[key]=deepcopy(result)
                    cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            except Exception as exc:result=dict(chunk_id=chunk['chunk_id'],status='failed',error_type=type(exc).__name__,error=str(exc),relations=[],rejected=[])
            result['ordinal']=index;result['paper_id']=chunk['paper_id'];existing['results'].append(result);existing['last_chunk']=result;existing['updated_at']=utcnow()
            checkpoint.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            print(json.dumps(dict(run_id=run_id,progress=f'{len(existing["results"])}/{len(chunks)}',chunk_id=chunk['chunk_id'],status=result['status'],claims=len(result.get('relations',[])),rejected=len(result.get('rejected',[])),seconds=result.get('seconds')),ensure_ascii=False),flush=True)
        existing.update(status='completed_with_failures' if any(r['status']=='failed' for r in existing['results']) else 'completed',finished_at=utcnow())
    finally:extractor.close()
    claims=[c for r in existing['results'] for c in r.get('relations',[])];entities,edges=graph_from_claims(claims)
    report=dict(run_id=run_id,benchmark=bench,summary=dict(status=existing['status'],started_at=existing['started_at'],finished_at=existing.get('finished_at'),total_chunks=len(chunks),completed_chunks=sum(r['status']=='completed' for r in existing['results']),failed_chunks=sum(r['status']=='failed' for r in existing['results']),chunks_with_claims=sum(bool(r.get('relations')) for r in existing['results']),claims=len(claims),rejected=sum(len(r.get('rejected',[])) for r in existing['results']),entities=len(entities),edges=len(edges),claims_by_predicate=dict(Counter(c['predicate'] for c in claims)),claims_by_paper=dict(Counter(c['paper_id'] for c in claims)),claim_kind_counts=dict(Counter(c['claim_kind'] for c in claims)),quote_match_counts=dict(Counter(c['quote_match_method'] for c in claims)),cached_results=sum(bool(r.get('reused_from_cache')) for r in existing['results']),input_tokens=sum(r.get('input_tokens') or 0 for r in existing['results']),output_tokens=sum(r.get('output_tokens') or 0 for r in existing['results']),model_seconds=sum(r.get('seconds') or 0 for r in existing['results'])))
    (run_dir/'checkpoint.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(run_dir/'claims.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(run_dir/'graph.json').write_text(json.dumps(dict(graph_version=VERSION,entities=entities,edges=edges),ensure_ascii=False,indent=2)+'\n',encoding='utf8');(run_dir/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return run_dir,report
