"""Render saved decomposition diagnostics and optional reviewer notes; no inference."""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import write_json
from papertech.subquery_diagnostic import render


def report(path):
    summary=json.loads(path.read_text(encoding='utf8'))
    folder=path.parent
    render(summary,folder)
    rows=[r for r in summary['results'] if r['arm']=='Local-LLM' and r['model_calls']]
    errors=Counter(e.split(':',1)[0] for r in rows for e in r['validation_errors'])
    diagnostic=dict(completed_model_calls=len(rows),valid=sum(r['valid'] for r in rows),
        invalid=sum(not r['valid'] for r in rows),validation_error_types=dict(errors),
        model_wall_seconds=sum(r['seconds'] for r in rows),
        prompt_tokens=sum((r.get('usage') or {}).get('prompt_tokens',0) for r in rows),
        completion_tokens=sum((r.get('usage') or {}).get('completion_tokens',0) for r in rows),
        missing_usage_rows=[r['case_id'] for r in rows if not r.get('usage')],
        source_fragment_validity_is_not_semantic_accuracy=True)
    if rows:
        times=sorted(r['seconds'] for r in rows)
        diagnostic.update(mean_seconds=sum(times)/len(times),median_seconds=(times[(len(times)-1)//2]+times[len(times)//2])/2,
            load_seconds=sum((r.get('runtime') or {}).get('load_duration',0)/1e9 for r in rows),
            prompt_eval_seconds=sum((r.get('runtime') or {}).get('prompt_eval_duration',0)/1e9 for r in rows),
            eval_seconds=sum((r.get('runtime') or {}).get('eval_duration',0)/1e9 for r in rows))
    write_json(folder/'diagnostic-summary.json',diagnostic)
    text=['# 拆分诊断：读取已有实测结果','','程序校验失败不等于模型所有语义判断都错误；校验通过也不等于子查询可用。','',
          '```json',json.dumps(diagnostic,ensure_ascii=False,indent=2),'```','']
    if (folder/'review-notes.json').exists():
        review=json.loads((folder/'review-notes.json').read_text(encoding='utf8'))
        counts=Counter(c['paired'] for c in review['cases'])
        diagnostic['reviewer_paired_counts']=dict(counts)
        diagnostic['reviewer_usable_split_cases']=[c['id'] for c in review['cases'] if c['usable'] is True]
        diagnostic['reviewer_not_ready_cases']=[c['id'] for c in review['cases'] if c['usable'] is False]
        write_json(folder/'diagnostic-summary.json',diagnostic)
        text+=['## 逐题审阅','','审阅者：'+review['origin'],
            '语义判断是 Codex 对题面和拆分的审阅，不是独立人工评分；没有读取参考答案来评判拆分归属。','',
            '严格可用性比较：模型输出未过校验时，视为当前流水线不可用，不能静默修补后计分。','',
            '|题号|相对规则版|模型版质量观察|','|---|---|---|']
        for case in review['cases']:
            text.append('|'+case['id']+'|'+case['paired']+'|'+case['note'].replace('|',' / ')+'|')
        text+=['','配对统计：'+json.dumps(dict(counts),ensure_ascii=False),'']
    (folder/'quality-review.md').write_text('\n'.join(text),encoding='utf8')
    dashboard=folder/'dashboard.html'
    page=dashboard.read_text(encoding='utf8')
    panel='<section style="background:#fff3db;padding:20px"><h2>校验结果与质量审阅</h2><p>机械校验不是语义评分；失败结果保留原始模型文本。以下为审阅记录。</p><pre>'+html.escape('\n'.join(text))+'</pre></section>'
    dashboard.write_text(page.replace('<h1>',panel+'<h1>',1),encoding='utf8')
    # A stable entry point beside runs keeps the latest report easy to locate.
    link=folder.parent.parent/'latest.json'
    write_json(link,dict(run_id=summary['run_id'],summary=str(path.relative_to(ROOT)),
        dashboard=str(dashboard.relative_to(ROOT)),status=summary['status'],
        summary_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    print(json.dumps(diagnostic,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary',type=Path,required=True)
    report(parser.parse_args().run_summary.resolve())
