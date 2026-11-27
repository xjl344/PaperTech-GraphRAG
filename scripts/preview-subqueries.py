"""Create a question-only subquery decomposition preview."""
import hashlib
import html
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.entity_aliases import SUBQUERY_VERSION, method_spans, subqueries


def review_case(case):
    question = case['question']
    anchors = method_spans(question)
    rows = subqueries(question)
    if not anchors:
        status = 'no_anchor'
    elif not rows:
        status = 'single_source'
    else:
        status = 'method_only' if any(r['subquery_source'] == 'method_only' for r in rows) else 'span'
    used = set()
    for row in rows:
        for span in row['source_spans']:
            if question[span['start']:span['end']] != span['text']:
                raise ValueError('Offset mismatch')
            used.update(range(span['start'], span['end']))
        if row['text'] != ' '.join(s['text'] for s in row['source_spans']):
            raise ValueError('Text outside question spans')
        if {a['method'] for a in method_spans(row['text'])} != {row['method']}:
            raise ValueError('Different named method in subquery')
    omitted, start = [], None
    for pos in range(len(question) + 1):
        missing = pos < len(question) and pos not in used
        if missing and start is None:
            start = pos
        if not missing and start is not None:
            if question[start:pos].strip():
                omitted.append(dict(start=start, end=pos, text=question[start:pos]))
            start = None
    return dict(id=case['id'], question=question, anchors=anchors, subqueries=rows,
                review_status=status, omitted_spans=omitted if rows else [],
                original_query_retained=not bool(rows), semantic_quality='not_scored',
                retrieval_effect='not_tested')


def render_html(payload):
    esc = html.escape
    labels = {'span': '明确从句，仍待审阅', 'method_only': '仅方法名，任务信息不足',
              'no_anchor': '无锚点，不拆分', 'single_source': '仅一篇方法，不拆分'}
    cards = []
    for case in payload['cases']:
        items = []
        for row in case['subqueries']:
            spans = '; '.join(f"{s['role']} [{s['start']}:{s['end']}] {s['text']}" for s in row['source_spans'])
            items.append(f"<li><strong>{esc(row['text'])}</strong><small>{row['id']} · {row['subquery_source']}</small><p>{esc(spans)}</p></li>")
        omitted = ''.join(f"<li>[{s['start']}:{s['end']}] {esc(s['text'])}</li>" for s in case['omitted_spans'])
        reasons = ', '.join(dict.fromkeys(r['fallback_reason'] for r in case['subqueries'] if r['fallback_reason']))
        card = f"<article id='{case['id']}'><h2>{case['id']} <small>{labels[case['review_status']]}</small></h2><p>{esc(case['question'])}</p><ol>{''.join(items) or '<li>保持原问题</li>'}</ol><p>{esc(reasons)}</p>"
        if omitted:
            card += f"<details><summary>未进入子查询的题面片段（含连接词）</summary><ul>{omitted}</ul></details>"
        cards.append(card + '</article>')
    nav = ' '.join(f"<a href='#{c['id']}'>{c['id']}</a>" for c in payload['cases'])
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>子查询拆分审阅</title><style>body{font:16px/1.7 system-ui,sans-serif;background:#f4f6f9;color:#172235;max-width:1100px;margin:auto;padding:28px}article{background:white;padding:20px 24px;margin:18px 0;border:1px solid #d4dbe5;border-radius:8px}small{font-size:14px;font-weight:normal;color:#556278;display:block}li p{font-size:13px;color:#556278;overflow-wrap:anywhere}nav{line-height:2.4}nav a{margin-right:8px}details{border-top:1px solid #ddd;padding-top:10px}</style><h1>24 道跨论文题：子查询拆分审阅</h1>''' + f"<p>仅文本预览，未运行检索或模型。明确从句 {payload['counts'].get('span',0)} 题，方法名回退 {payload['counts'].get('method_only',0)} 题，无锚点 {payload['counts'].get('no_anchor',0)} 题。共 {payload['subquery_count']} 条子查询。</p><p>拆分只使用题面与既有别名；明确从句仍可能省略比较任务。方法名回退不代表质量合格。字符偏移为 0 起始、左闭右开。未运行 LangSmith 对照实验。</p><nav>{nav}</nav>{''.join(cards)}</html>"


def main():
    source = ROOT / 'artifacts/eval/stage-4/benchmark-relation-holdout-v1/benchmark.json'
    target = ROOT / 'artifacts/eval/stage-4/relation-holdout-subqueries-v1'
    target.mkdir(parents=True, exist_ok=True)
    benchmark = json.loads(source.read_text(encoding='utf-8'))
    questions = [dict(id=c['id'], question=c['question']) for c in benchmark['cases'] if c['id'].startswith('R')]
    if [c['id'] for c in questions] != [f'R{i:02d}' for i in range(1,25)]:
        raise ValueError('Expected R01 through R24 in source order')
    question_text = json.dumps(questions, ensure_ascii=False, indent=2) + '\n'
    (target / 'questions.json').write_text(question_text, encoding='utf-8', newline='\n')
    cases = [review_case(c) for c in questions]
    payload = dict(version=SUBQUERY_VERSION, source_benchmark='benchmark-relation-holdout-v1',
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   questions_sha256=hashlib.sha256(question_text.encode('utf-8')).hexdigest(),
                   splitter_sha256=hashlib.sha256((ROOT / 'src/papertech/entity_aliases.py').read_bytes()).hexdigest(),
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   status='preview_not_experiment', counts=dict(Counter(c['review_status'] for c in cases)),
                   subquery_count=sum(len(c['subqueries']) for c in cases),
                   model_calls=dict(embedding=0, rerank=0, generation=0),
                   langsmith_status='not_run_preview_only', cases=cases)
    (target / 'preview.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# 子查询拆分审阅预览', '',
             f'- 规则版本：`{SUBQUERY_VERSION}`',
             f'- 来源题集：`benchmark-relation-holdout-v1`',
             f'- 题集 SHA-256：`{payload["source_sha256"]}`',
             '- 约束：拆分仅使用题面和方法别名，不使用金标、正文或图谱；未调用模型。', '']
    lines += ['状态：仅文本预览，未运行检索、Embedding、重排、生成或 LangSmith 对照实验。', '',
              f"24 题分类：{payload['counts']}；共 {payload['subquery_count']} 条子查询。", '',
              '拆分函数只接收题面；脚本从旧题集中投影 id/question，不把金标交给拆分函数。',
              '字符偏移：Python 字符索引，0 起始、左闭右开。',
              '首版限制：任一方法缺少明确描述时，本题所有方法都退回方法名；不解前者/后者等指代。',
              '方法名回退表示任务信息不足；明确从句也不表示完整保留了比较任务。',
              '质量检查：R09、R20 只保留技术描述，没有完整问句；R15、R17 的整题回退过于保守。',
              '现有题目已用于开发，不能作为新的泛化验收。', '']
    for case in cases:
        lines += [f'## {case["id"]}', '', f'题面：{case["question"]}',
                  f'审阅状态：`{case["review_status"]}`']
        if not case['subqueries']:
            lines += ['子查询：无（保持原问题路径）', '']
            continue
        for row in case['subqueries']:
            lines += [f'- `{row["id"]}` {row["method"]} [{row["subquery_source"]}]：{row["text"]}',
                      f'  - spans: ' + '; '.join(
                          f'{s["role"]}[{s["start"]}:{s["end"]}]={s["text"]}'
                          for s in row['source_spans']),
                      f'  - fallback: `{row["fallback_reason"]}`; warnings: `{",".join(row["warnings"])}`']
        lines += ['', '未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：', '']
        lines.extend(f"- [{s['start']}:{s['end']}] {s['text']}" for s in case['omitted_spans'])
        lines.append('')
    (target / 'preview.md').write_text('\n'.join(lines), encoding='utf-8')
    (target / 'preview.html').write_text(render_html(payload), encoding='utf-8')
    print(json.dumps({'target': str(target), 'cases': len(cases), 'counts': payload['counts'],
                      'with_subqueries': sum(bool(c['subqueries']) for c in cases),
                      'method_only_cases': sum(any(r['subquery_source'] == 'method_only' for r in c['subqueries']) for c in cases),
                      'no_anchor_cases': sum(c['review_status'] == 'no_anchor' for c in cases)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
