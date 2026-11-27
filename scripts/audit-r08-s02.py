"""Explain the persistent R08.S02 rerank miss from the frozen source text."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import load_benchmark,stable_id,write_json
from papertech.settings import settings
from papertech.subquery_rerank_clean_diagnostic import VERSION,CleanRerankDataset


def terms(text):
    return set(re.findall(r'[A-Za-z][A-Za-z0-9_-]*|[\u4e00-\u9fff]{2,}', text.lower()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('summary',type=Path);parser.add_argument('--upload',action='store_true');args=parser.parse_args()
    folder=args.summary.parent;summary=json.loads(args.summary.read_text(encoding='utf8'));bench,digest,_=load_benchmark(ROOT,VERSION)
    _,_,chunks=load_corpus(ROOT);chunkmap={c['chunk_id']:c for c in chunks}
    rows=[r for r in summary['results'] if r['case_id']=='R08']
    case=next(c for c in bench['cases'] if c['id']=='R08');unit=bench['units']['R08.S02'];ids=set(unit['known_support_chunks'])
    sources=[]
    for cid in ids:
        source=chunkmap[cid];q=next(r for r in rows if r['arm']=='Owner-Clean');
        ranked={x['chunk_id']:x for x in q['ranked_candidates']};item=ranked[cid]
        sources.append(dict(chunk_id=cid,title=source['title'],page_start=source['page_start'],page_end=source['page_end'],section=source.get('section'),
            source_relative_path=source['source_relative_path'],text=source['text'],source_spans=source['source_spans'],
            owner_clean_score=item['score_by']['selected'],owner_clean_rank=next(i for i,x in enumerate(q['ranked_candidates'],1) if x['chunk_id']==cid),
            original_score=item['score_by']['original'],original_rank=next(i for i,x in enumerate(next(r for r in rows if r['arm']=='Original-Reused')['ranked_candidates'],1) if x['chunk_id']==cid),
            lexical_overlap=sorted(terms(case['question']) & terms(source['text']))))
    queries=[]
    for row in rows:
        queries.extend(dict(arm=row['arm'],query=q['cleaned'],original_query=q['original'],removed=q['removed']) for q in row['cleanup'] if q['id']=='SQ02')
    result=dict(case_id='R08',unit_id='R08.S02',question=case['question'],required_fact=unit['answer_point'],
        subquery='STaRK 的候选重排设置暴露了哪些成本或输入长度限制？',subqueries=queries,sources=sources,
        diagnosis=dict(summary='原文块确实包含STaRK重排设置和成本信息，但没有直接陈述输入长度限制；题面把两个不同维度绑在一个子查询中。',
            supported_details=['使用GPT-4-turbo和Claude3做LLM rerank','合成问题k=20、人工问题k=10','每个候选由LLM按文本和关系信息给0到1满意度分','由于计算成本高，只在测试问题随机10%上评估','Recall@20用于合成问题'],
            absent_or_mismatched=['原文没有明确的输入token/上下文长度上限','题面中的“输入长度限制”更接近ToG-2侧要求，混入STaRK子查询后增加了未被该块支撑的语义条件'],
            interpretation='低分不能单独证明候选来源错误；更可能是查询要求包含原文没有的输入长度维度，且块中关键事实以k=20/k=10、random 10%和computational costs表达。应将STaRK检索目标拆成“候选数/评估采样/成本”，把输入长度限制留给ToG-2子查询。'))
    write_json(folder/'r08-s02-audit.json',result)
    page=['<!doctype html><meta charset="utf-8"><title>R08.S02 原文语义审计</title><style>body{max-width:1100px;margin:30px auto;font:16px system-ui;line-height:1.65}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:14px}</style>',
        '<h1>R08.S02：STaRK 重排设置为何持续低分</h1><p>'+html.escape(result['diagnosis']['summary'])+'</p>',
        '<h2>题面与子查询</h2><pre>'+html.escape(json.dumps(dict(question=result['question'],subqueries=result['subqueries']),ensure_ascii=False,indent=2))+'</pre>',
        '<h2>支持原文与位置</h2>']
    for source in sources:
        page.append('<h3>'+html.escape(source['title'])+'，第'+str(source['page_start'])+'页</h3><pre>'+html.escape(json.dumps(source,ensure_ascii=False,indent=2))+'</pre>')
    page.append('<h2>判读</h2><pre>'+html.escape(json.dumps(result['diagnosis'],ensure_ascii=False,indent=2))+'</pre>')
    (folder/'r08-s02-audit.html').write_text(''.join(page),encoding='utf8')
    (folder/'r08-s02-audit.md').write_text('# R08.S02 原文语义审计\n\n'+result['diagnosis']['summary']+'\n\n'+result['diagnosis']['interpretation']+'\n',encoding='utf8')
    if args.upload:
        rec=CleanRerankDataset(ROOT,VERSION)
        try:
            client=rec.connect();status=json.loads((folder/'langsmith-status.json').read_text(encoding='utf8'))
            feedback=[]
            for arm in ('Owner-Clean','Original-Reused','Max-Original-Owner'):
                project=next(x for x in status['experiments'] if x['arm']==arm);run_id=stable_id(digest,summary['run_id'],'R08',arm)
                fid=stable_id(run_id,'r08_s02_semantic_audit_v1');comment=json.dumps(result,ensure_ascii=False,indent=2)
                feedback.append(dict(run_id=run_id,key='r08_s02_semantic_audit_v1',feedback_id=fid,comment=comment,session_id=project['project_id'],stop_after_attempt=1))
            existing={str(f.id) for f in client.list_feedback(run_ids=[x['run_id'] for x in feedback])}
            for item in feedback:
                if item['feedback_id'] not in existing:client.create_feedback(**item)
            found={str(f.id) for f in client.list_feedback(run_ids=[x['run_id'] for x in feedback])}
            if set(x['feedback_id'] for x in feedback)-found:raise RuntimeError('audit_feedback_readback_failed')
            write_json(folder/'r08-s02-audit-sync.json',dict(status='verified',feedback_count=len(feedback),sha256=hashlib.sha256((folder/'r08-s02-audit.json').read_bytes()).hexdigest()))
        finally:rec.close()
    print(json.dumps(dict(status='verified',audit=str(folder/'r08-s02-audit.html'),uploaded=args.upload),ensure_ascii=False))


if __name__=='__main__':main()
