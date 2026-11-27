"""Rebuild saved generic-routing reports without invoking inference."""
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import write_json
from papertech.query_router_diagnostic import report


def main(path):
    s=json.loads(path.read_text(encoding='utf8'));folder=path.parent
    report(s,folder)
    rows=[r for r in s['results'] if r['arm']=='Local-LLM']
    labels=dict(no_split='不拆',rule='规则拆',llm='模型拆',unclear='无法确定',fallback='校验失败')
    counts=Counter(r['route'] for r in rows)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 270"><title>通用分流实际决策数量，不是准确率</title>']
    for i,(key,label) in enumerate(labels.items()):
        y=15+45*i;n=counts[key]
        svg.append(f'<text x="0" y="{y+20}">{label}</text><rect x="140" y="{y}" height="28" width="{n*26}" fill="#3975b7"/><text x="{150+n*26}" y="{y+20}">{n}</text>')
    svg.append('<text x="140" y="260">决策题数，非路由正确率</text></svg>')
    chart=''.join(svg);(folder/'routes.svg').write_text(chart,encoding='utf8')
    lines=['# 通用分流器结果说明','',f"运行状态：{s['status']}。已完成模型判断 {len(rows)}/24。",'',
        'Rule Experiment 是保持原题的基线；Local-LLM Experiment 是通用分流器。',
        '两组均保留原题，分流器只提出补充检索子查询；未运行任何检索、Embedding、重排或答案生成。',
        '模型每题调用一次，在同一响应中完成分流和必要的拆分；选择规则分流也有模型判断成本。',
        '运行只输入题面与通用语法产生的候选，不传题号、方法别名目录、参考答案或正文。',
        '全部24题都是跨论文开发题，因此无法用本轮证明对简单题/不拆题的分类准确率。',
        '校验通过仅说明结构、引文和词面限制通过；中文新事实、技术项归属、目标遗漏仍需审阅。','',
        '|题号|实际分流|模型理由|子查询|','|---|---|---|---|']
    for row in rows:
        lines.append('|'+row['case_id']+'|'+labels[row['route']]+'|'+row['reason'].replace('|','/')+'|'+'<br>'.join(q['text'].replace('|','/') for q in row['subqueries'])+'|')
    panel='<section><h1>通用分流总览</h1><p>每题一次模型判断；选择规则拆分也计入模型成本。Rule组=保持原题基线，Local-LLM组=通用分流器。24题均为跨论文开发题，不能验证简单题误拆率。</p>'+chart+'</section>'
    notes_path=folder/'review-notes.json'
    if notes_path.exists():
        notes=json.loads(notes_path.read_text(encoding='utf8'))
        stats=dict(review_status=notes['status'],origin=notes['origin'],
            routing=dict(Counter(c['route_quality'] for c in notes['cases'])),
            query_quality=dict(Counter(c['query_quality'] for c in notes['cases'])))
        write_json(folder/'review-summary.json',stats)
        lines+=['','## 逐题语义审阅','','审阅：'+notes['origin'],
            '路由判断与子查询质量分开；以下是代理审阅，不是独立人工评分。','',
            '|题号|路由判断|子查询质量|观察|','|---|---|---|---|']
        for c in notes['cases']:lines.append('|'+c['id']+'|'+c['route_quality']+'|'+c['query_quality']+'|'+c['note'].replace('|','/')+'|')
        panel+='<h2>逐题语义审阅</h2><pre>'+html.escape(json.dumps(notes,ensure_ascii=False,indent=2))+'</pre>'
    (folder/'quality-review.md').write_text('\n'.join(lines),encoding='utf8')
    page=folder/'dashboard.html';page.write_text(page.read_text(encoding='utf8').replace('<h1>',panel+'<h1>',1),encoding='utf8')
    write_json(folder.parent.parent/'latest.json',dict(run_id=s['run_id'],status=s['status'],directory=str(folder.relative_to(ROOT))))
    print(json.dumps(dict(status=s['status'],rows=len(rows),routes=dict(counts)),ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-summary',type=Path,required=True)
    main(p.parse_args().run_summary.resolve())
