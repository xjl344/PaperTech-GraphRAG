"""Join already-completed diagnostics without changing references or rerunning models."""
from collections import Counter
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import load_benchmark,write_json
from papertech.staged_retrieval_diagnostics import WIDTH,RESOURCE,RECALL,PARENT,previous


def main():
    bench,_,_=load_benchmark(ROOT,'benchmark-relation-holdout-v1')
    parents=json.loads((ROOT/PARENT/'summary.json').read_text(encoding='utf8'))
    parents={r['case_id']:r for r in parents['results'] if r['arm']=='Hybrid'}
    stages={}
    for version in (WIDTH,RESOURCE,RECALL):
        folder,s=previous(ROOT,version)
        verification=json.loads((folder/'independent-verification.json').read_text(encoding='utf8'))
        assert verification['status']=='passed'
        stages[version]=dict(folder=str(folder),summary=s,
            comparison=json.loads((folder/'comparison.json').read_text(encoding='utf8')),verification=verification)
    cross=[c for c in bench['cases'] if c['category']=='cross']
    b_units={'R05.S02','R24.S03'}
    initial={}
    for c in cross:
        for f in parents[c['id']]['diagnosis']['facts']:
            group='covered' if f['reason']=='covered' else 'A' if f['reason']=='retrieval_pool_miss' else 'B' if f['unit_id'] in b_units else 'C'
            initial[f['unit_id']]=dict(case_id=c['id'],group=group,original_reason=f['reason'],requirement=f['required_fact'])
    transitions=[]
    for uid,initial_fact in initial.items():
        entry=dict(unit_id=uid,**initial_fact,stages={})
        for version,data in stages.items():
            case_id=initial_fact['case_id']
            entry['stages'][version]={}
            for row in data['summary']['results']:
                if row['case_id']!=case_id:
                    continue
                fact=next(f for f in row['diagnosis']['facts'] if f['unit_id']==uid)
                entry['stages'][version][row['arm']]=dict(reason=fact['reason'],rank=fact['candidate_rank'],
                    score=fact['rerank_score'],selected=bool(fact['selected_matches']),channel_positions=fact['channel_positions'],
                    selection_decisions=fact['selection_decisions'])
        transitions.append(entry)
    group_counts=dict(Counter(f['group'] for f in initial.values()))
    output=ROOT/'artifacts/reports/stage-4/staged-retrieval-followup-v1'
    aggregate={v:dict(folder=d['folder'],comparison=d['comparison'],verification=d['verification'],
        langsmith=d['summary']['dataset_sync']) for v,d in stages.items()}
    write_json(output/'stage-comparison.json',dict(initial_cross_source_groups=group_counts,stages=aggregate,source_transitions=transitions))
    lines=['# 上游、资源与召回分阶段诊断','',
        '全部使用已曝光的40道开发题，来源池与题目不变；每阶段使用新的冻结版本和LangSmith Dataset，不作为泛化验收。所有组均无生成。','',
        '## 初始缺口核正','',f'24道跨论文题共49个必要来源单元：{json.dumps(group_counts,ensure_ascii=False)}。',
        'A为未入池；B为指定的两个低排名来源；C为其余11个入池但未入上下文的来源。B/C互斥；原context_selection的12个包含R05.S02，另外R24.S03为阈值失败。',
        '现有策略已经优先为点名论文保留一块，且仅在已召回池内选取；同篇任意段落不能代替必要原文。','',
        '## 1. 单独扩Dense候选宽度','',
        '全文固定20，ANN查询范围仍为100，复用历史查询向量，只变返回量；无新Embedding、重排、生成。每题Dense20与历史索引结果完全一致。',
        '|组别（均含全文20）|跨论文候选覆盖|跨论文胜/平/负|A组补回来源数|','|---|---:|---|---:|']
    width_stats=stages[WIDTH]['comparison']['categories']['cross']
    for arm,x in width_stats.items():
        recovered=sum(t['group']=='A' and t['stages'][WIDTH][arm]['reason']=='candidate_available' for t in transitions)
        p=x['paired'];lines.append(f"|{arm}|{x['candidate_coverage']:.2%}|{p['win']}/{p['tie']}/{p['loss']}|{recovered}/20|")
    lines.extend(['','## 2. 固定候选、固定重排分数的资源和保底消融','',
        'Named为当前已有的点名论文优先；Score是取消该保底、只按分数的消融。6000/8000为UTF-8字节，8/12为最多块数。','',
        '|组别|跨论文最终覆盖|全部必要来源题数|胜/平/负（对当前默认）|C组来源进入数|','|---|---:|---:|---|---:|'])
    resources=stages[RESOURCE]['comparison']['categories']['cross']
    for arm,x in resources.items():
        recovered=sum(t['group']=='C' and t['stages'][RESOURCE][arm]['selected'] for t in transitions)
        p=x['paired'];lines.append(f"|{arm}|{x['final_coverage']:.2%}|{x['all_units']}/24|{p['win']}/{p['tie']}/{p['loss']}|{recovered}/11|")
    max_original=max(len(r['evidence']) for r in parents.values())
    lines.extend(['',f'原Hybrid全40题实际最多选中{max_original}块，不能把所有预算损失称为8块上限。是否加字节或加块数有效，应以独立消融为准。',
        '', '## 3. 根据扩k结果选择的召回干预','',
        '事前规则选择能补回跨论文必要来源的最小测试k。两组均使用8000字节、12块、现有Named策略，资源条件完全一致；仅增加Dense返回量及其去重候选。复用原候选的历史分数，只对新候选用原问题评分，不改模型、阈值或问题。',
        '|组别（均含全文20）|候选覆盖|最终覆盖|全部必要来源题数|胜/平/负|','|---|---:|---:|---:|---|'])
    recall=stages[RECALL]['comparison']['categories']['cross']
    for arm,x in recall.items():
        p=x['paired'];lines.append(f"|{arm}|{x['candidate_coverage']:.2%}|{x['final_coverage']:.2%}|{x['all_units']}/24|{p['win']}/{p['tie']}/{p['loss']}|")
    treatment=list(recall)[1];outcome=recall[treatment]['paired']
    lines.extend(['',f"按用户停止线：改善{outcome['win']}题，退化{outcome['loss']}题。"+
        ('退化题数超过改善题数，不应采纳该召回配置。' if outcome['loss']>outcome['win'] else '未触发退化题数超过改善题数的停止线；这只是开发回归条件，不代表已获泛化验收或自动切换生产。'),
        '', '## 逐来源阶段迁移','',
        '|来源单元|原分组|Dense40是否入池|Dense60是否入池|8000/12是否入证据|扩召回后是否入证据|','|---|---|---|---|---|---|'])
    for t in transitions:
        if t['group']=='covered':
            continue
        yn=lambda v:'是' if v else '否'
        lines.append(f"|{t['unit_id']}|{t['group']}|{yn(t['stages'][WIDTH]['Dense40']['reason']=='candidate_available')}|{yn(t['stages'][WIDTH]['Dense60']['reason']=='candidate_available')}|{yn(t['stages'][RESOURCE]['Named-8000-12']['selected'])}|{yn(t['stages'][RECALL][treatment]['selected'])}|")
    lines.extend(['','## 证据边界与下一步','',
        '资源扩大会让更多候选有机会进入上下文，不能保证指定必要段落；候选补回也不代表最终保留。方法论文出现、必要原文出现、答案语义正确是不同指标。',
        '本轮没有新增按方法偏置的召回通道。原有论文保底的效应由Named/Score消融单独展示，不能宣称是本轮新加策略；也不能从某块的分数下降断言必须放弃重排。',
        'Top60仍未找到某来源，只能说明当前原问题+固定模型+索引范围下未命中；不足以证明必须查询改写。查询拆分可作为下一项有单独变量控制的实验，本轮不生成改写问题或调用生成模型。','',
        '## 页面与远端实验',''])
    for v,d in stages.items():
        lines.append(f"- [{v} LangSmith]({d['summary']['dataset_sync']['comparison_url']})；[本地总览]({Path(d['folder']).as_posix()}/dashboard.html)。")
    lines.extend(['','[逐来源完整阶段记录](stage-comparison.json)。所有页面保留汇总、分类、柱状图、时延、调用量、完整原文、候选、证据与逐题配对；反例不计主分。'])
    text='\n'.join(lines)+'\n';(output/'findings.md').write_text(text,encoding='utf8')
    page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>分阶段检索诊断</title>',
        '<style>body{font:15px system-ui;max-width:1300px;margin:32px auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:12px}iframe{width:100%;height:650px;border:1px solid #ccc}</style>',
        '<h1>分阶段检索诊断</h1><pre>'+html.escape(text)+'</pre>']
    import os
    for v,d in stages.items():
        rel=Path(os.path.relpath(Path(d['folder'])/'dashboard.html',output)).as_posix()
        page.append(f'<h2>{v}</h2><a href="{rel}">打开完整总览、图表和40题详情</a><iframe src="{rel}" title="{v}" loading="lazy"></iframe>')
    (output/'dashboard.html').write_text('\n'.join(page)+'</html>',encoding='utf8')
    print(json.dumps(dict(status='completed',folder=str(output),initial_groups=group_counts,recall_outcomes=outcome),ensure_ascii=False))


if __name__=='__main__':
    main()
