"""Export Codex's source-based, post-hoc review of saved answers; never generate answers.

JUDGMENTS below are explicit AI reading judgments, not keyword-based grading.
Substring assertions only protect the audit trail against changed input files.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation_datasets import stable_id, write_json
from papertech.settings import settings

DEFAULT = ROOT / 'artifacts/reports/stage-4/benchmark-source-coverage-v1/extra-path-budget-runs/2dba52fe57084f1c998bf35849c79936'
ARMS = ('Path-0', 'Path-800', 'Path-1200')
KEY = 'codex_semantic_review_v1'

# label, reference unit, supporting chunk suffix, answer excerpt for each arm.
# None means the required content was omitted, even when its source was available.
JUDGMENTS = {
    'R11': [
        ('KG-GPT 的 MetaQA 1/2/3-hop 与 Hits@1', 'kggptds', '3f7eb65828761447433c66c28ad111a4',
         [None, 'KG-GPT 的 MetaQA 结果只列 1-hop、2-hop、3-hop 的 Hits@1', 'KG-GPT 的表头为“MetaQA 1-hop/2-hop/3-hop”且指标为“Hits@1”']),
        ('Wiki-Movies 是 MetaQA-3hop 的知识图谱', 'rogmeta', '297df214042add51d3facf35d1934a3d',
         ['based on Wiki-Movies KGs', 'MetaQA-3hop 数据集所基于的知识图', 'RoG 的 MetaQA-3hop 建立在 Wiki-Movies KG 上']),
        ('RoG 扩展实验取 1000 个训练样本', 'rogmeta', '297df214042add51d3facf35d1934a3d',
         ['从训练集取 1000 个样本', '1000 个训练样本', 'We select 1000 samples from the training split']),
        ('Freebase 是向 Wiki-Movies 迁移前的训练来源', 'rogmeta', 'f5c88d605f651f26c093f30b836a98aa', [None, None, None]),
    ],
    'R12': [
        ('MusicBrainz-x-Wikidata 连接 MusicBrainz 和 Wikidata', 'totmusic', 'f4962498025654850621ee329d0af7d6',
         ['同时用 MusicBrainz 与 Wikidata', '同时使用 MusicBrainz 与 Wikidata', '同时使用 MusicBrainz 和 Wikidata']),
        ('前者要求跨两个 KG 综合推理', 'totmusic', 'f4962498025654850621ee329d0af7d6',
         ['综合多个 KG 信息回答单个问题', '侧重跨两个 KG 综合信息', '侧重跨两个知识图谱来源综合信息']),
        ('CLQA-Wiki 来自 Wikidata 子集', 'lpbench', 'ab66789d9bc91de68948962d6c3f0011',
         ['从 Wikidata 的一个子集构建', '从 Wikidata 的一个子集构建', '从 Wikidata 的一个子集构建']),
        ('CLQA-Wiki 覆盖多跳、比较、交集、并集', 'lpbench', 'ab66789d9bc91de68948962d6c3f0011',
         ['multi-hop、comparison、intersection、union 四类问题', '多跳、比较、交集和并集类型问题', '多跳、比较、交集和并集类型问题']),
    ],
    'R13': [
        ('AdvHotpotQA 是 HotpotQA 的挑战子集', 'tog2ds', '16f86a00cebdf5e10d83c3a540fbc7f7', [None, None, None]),
        ('HippoRAG 每个验证集取 1000 题并汇集支持/干扰段落', 'hippods', '3fa28005a4df0de5249826585cf9d713', [None, None, None]),
        ('ToG-2 使用 full Wikipedia/Wikidata', 'tog2ds', '16f86a00cebdf5e10d83c3a540fbc7f7', [None, None, None]),
        ('不直接用结果数字排名（只计谨慎结论，设置解释另计）', 'tog2ds', '16f86a00cebdf5e10d83c3a540fbc7f7',
         ['不能直接用结果数字比较', '不能仅凭这些设置说明直接把', '不能仅凭结果数字直接比较']),
    ],
    'R23': [
        ('ToG 调用上界 2ND+D+1，并联系搜索宽度/深度', 'togr', '91a4a2e6943ad6a8074492d3f7229692',
         ['2ND + D + 1，其中 N 是宽度、D 是深度', '2ND+D+1 是最大计算复杂度', '2ND+D+1 是最大计算复杂度']),
        ('ToG-R 调用上界 ND+D+1', 'togr', 'aa272a627cf75d5bf907fe3a860356c4',
         ['ToG-R 最多需要 ND + D + 1 次', 'ToG-R 则“needs at most ND + D + 1 calls', 'ToG-R 最多需要 ND+D+1 次']),
        ('以随机剪枝替代 LLM 剪枝解释调用减少', 'togr', 'aa272a627cf75d5bf907fe3a860356c4',
         ['随机束搜索（random beam search）代替 LLM 约束的束搜索', None, None]),
        ('Tree-of-Traversals max depth 强制进入 done', 'totbound', 'dac5f23e1b87249cf88eff5c6cc54355', [None, None, None]),
        ('max expansions 达限后失败停止并返回 Cannot find answer', 'totbound', 'dac5f23e1b87249cf88eff5c6cc54355', [None, None, None]),
        ('调用上界不能直接换算墙钟时间或跨方法排名', 'totbound', 'dac5f23e1b87249cf88eff5c6cc54355',
         ['不能把 ToG 的公式上限和默认深度/宽度当作跨算法的可比运行时指标', '调用次数的理论边界而非可比运行时', '不能把这些公式/上限直接换算成统一的运行时排名']),
    ],
}
CONCLUSIONS = {
    'R11': '局部更完整：加路径两组补出 KG-GPT 跳数/指标，但仍漏 Freebase 的迁移训练角色，三组均未完整回答。',
    'R12': '持平：基线已答出全部核心内容。partial→ok 是程序状态变化，不是语义知识提升；题干不要求 109 题，未提数量不扣分。',
    'R13': '核心内容持平且缺失：三组均漏子集关系与两篇语料设置。800 组另有无依据的确定断言；1200 组不确定性措辞较稳。',
    'R23': '局部退化：加路径两组省掉基线已解释的随机剪枝机制；三组都缺 Tree-of-Traversals 两种预算的具体停止行为。',
}
FLAGS = {
    ('R13', 'Path-0'): [
        ('原文没有说明', '把本轮未检索到关系扩张为论文没有说明；冻结参考原文实际给出了挑战子集关系。'),
        ('可比性所必需的条件在原文中缺失', '证据上下文不全不等于论文中没有实验设置。'),
    ],
    ('R13', 'Path-800'): [
        ('底座模型设置不一致', '给定证据没有说明 HippoRAG 的底座，不能把未知断言为不一致。'),
        ('AdvHotpotQA 检索结果数字', 'ToG-2 表格 EM 是问答结果，不能当作检索指标。'),
        ('二者并非同一数据集，关系不明确', '未识别挑战子集关系；所附 HippoRAG 单侧引用不能支持两者关系判断。'),
    ],
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(folder):
    summary = read(folder / 'summary.json')
    comparison = read(folder / 'comparison.json')
    bench_path = ROOT / 'artifacts/eval/stage-4' / summary['benchmark'] / 'benchmark.json'
    bench = read(bench_path)
    assert sha(bench_path) == summary['benchmark_sha256']
    rows = {(r['case_id'], r['arm']): r for r in summary['results']}
    payloads = {(r['extra']['metadata']['case_id'], r['_arm']): r
                for r in read(folder / 'langsmith-experiments.json')['runs']}
    changed = {cid for cid in comparison['results'] if any(
        rows[cid, a]['prompt_fingerprint'] != rows[cid, 'Path-0']['prompt_fingerprint'] for a in ARMS[1:])}
    assert changed == set(JUDGMENTS)
    references = {cid: comparison['references'][cid] for cid in JUDGMENTS}
    sources = {x['chunk_id']: x for ref in references.values() for x in ref['source_evidence']}
    for cid in JUDGMENTS:
        for arm in ARMS:
            for e in rows[cid, arm]['evidence']:
                sources.setdefault(e['chunk_id'], {**e, 'text': e['quote'], 'scope': 'actual_prompt_excerpt'})
    reviews = []
    for cid, rubric in JUDGMENTS.items():
        for ai, arm in enumerate(ARMS):
            row, payload = rows[cid, arm], payloads[cid, arm]
            assert row['evidence'] == rows[cid, 'Path-0']['evidence']
            items = []
            for index, (label, uid, suffix, excerpts) in enumerate(rubric):
                chunk, quote = 'chunk_' + suffix, excerpts[ai]
                assert chunk in sources
                if quote is not None:
                    assert quote in row['answer'], (cid, arm, quote)
                available = any(e['chunk_id'] == chunk for e in row['evidence'])
                # Some reference chunks differ from the equally supporting chunk in the prompt.
                # Do not mislabel the ToG formula's availability merely from primary ID mismatch.
                supporting_prompt_chunks = [chunk] if available else []
                if cid == 'R23' and index == 0:
                    alt = 'chunk_f99077c01e2b49914150ff933b0cf783'
                    assert any(e['chunk_id'] == alt for e in row['evidence'])
                    supporting_prompt_chunks.append(alt)
                inference = (cid == 'R13' and index == 3) or (cid == 'R23' and index == 5)
                items.append(dict(item_id=f'{cid}.{index+1}', label=label, score=int(quote is not None),
                    verdict='已回答' if quote is not None else '遗漏', answer_excerpt=quote,
                    reference_unit=uid, reference_excerpt=bench['units'][uid]['source_text'],
                    reference_chunk_id=chunk, supporting_prompt_chunks=supporting_prompt_chunks,
                    source_available=bool(supporting_prompt_chunks),
                    citation_support=('跨来源审慎推断，不冒充原文直接排名结论' if inference else
                        '回答所引原文支持该要点' if quote is not None else '未作出该必要陈述'),
                    note=('基线表述为随机束搜索，接受其机制概括；未明确写出实体剪枝范围。' if cid == 'R23' and index == 2 and ai == 0 else
                          '只给不能直接比较这一结论分；必要设置另三项均未答出。' if cid == 'R13' and index == 3 else '')))
            issues = []
            for excerpt, reason in FLAGS.get((cid, arm), []):
                assert excerpt in row['answer']
                issues.append(dict(answer_excerpt=excerpt, reason=reason))
            score = sum(i['score'] for i in items)
            project = next(p['project_id'] for p in comparison['dataset_sync']['experiments'] if p['arm'] == arm)
            experiment_url = comparison['dataset_sync']['dataset_url'].split('/datasets/')[0] + '/projects/p/' + project + '/r/' + payload['id']
            reviews.append(dict(case_id=cid, arm=arm, experiment_run_id=payload['id'],
                reference_example_id=payload['reference_example_id'],
                experiment_run_url=experiment_url,
                trace_url=row['trace_url'], retrieval_trace_url=row['retrieval_trace_url'], original_status=row['status'], answer=row['answer'],
                evidence=row['evidence'], citations=row['citations'], generation_paths=row['generation_paths'],
                usage=row['usage'], stage_timings=row['stage_timings'], items=items,
                covered=score, total=len(items), coverage=score / len(items),
                all_required_points=score == len(items), unsupported_or_misleading=issues,
                conclusion=CONCLUSIONS[cid],
                feedback_value=dict(review_kind='codex_ai_source_review', rubric_version=KEY,
                    post_hoc=True, case_id=cid, arm=arm, covered=score, total=len(items),
                    all_required_points=score == len(items), items=items,
                    unsupported_or_misleading=issues, conclusion=CONCLUSIONS[cid])))
    aggregates = {}
    for arm in ARMS:
        rr = [r for r in reviews if r['arm'] == arm]
        aggregates[arm] = dict(reviewed_answers=len(rr), covered=sum(r['covered'] for r in rr),
            total=sum(r['total'] for r in rr), all_required_points=sum(r['all_required_points'] for r in rr))
    assert all(a == dict(reviewed_answers=4, covered=11, total=18, all_required_points=1) for a in aggregates.values())
    return dict(review_kind='codex_ai_source_review', rubric_version=KEY,
        reviewer='Codex AI；非盲审、非独立人工专家',
        status='completed', run_id=summary['run_id'], benchmark=summary['benchmark'],
        benchmark_sha256=sha(bench_path), summary_sha256=sha(folder / 'summary.json'),
        comparison_sha256=sha(folder / 'comparison.json'), script_sha256=sha(Path(__file__)),
        reviewed_at=datetime.now(timezone.utc).isoformat(), new_model_calls=0,
        scope='仅实际增加路径改变输入的 R11/R12/R13/R23；4 题×3 组。其余 12 题未做此次语义审查，不得外推为 16 题准确率。',
        rubric='事后诊断口径，不是新预注册基准成绩。按冻结题干/参考答案拆分 18 个必要要点，各要点 0/1；接受有来源的同义表述。要点数不等权于题数，不从程序 ok/partial 推断语义分数。',
        limitations='每组每题仅一次生成；所见一增一退不能单独证明路径因果或统计显著性。正确克制与完整回答分开记录。未发现额外问题不等于穷尽证明回答完全正确。',
        conclusion='未观察到整体提升：三组均答出 11/18 个必要要点，完整覆盖全部必要要点均 1/4 题；R11 局部增、R23 局部退，R12/R13 核心持平。',
        aggregates=aggregates, by_category={'cross': aggregates}, references=references,
        source_evidence=sources, reviews=reviews, dataset_sync=comparison['dataset_sync'])


def render(folder, review):
    lines = ['# 额外路径预算：答案语义审查', '', review['conclusion'], '',
        review['scope'], '', review['reviewer'] + '。' + review['rubric'], '',
        '原文 6000 字节不变，额外路径预算 0/800/1200。使用已有回答，新模型调用为 0。', '',
        '| 题号 | Path-0 | Path-800 | Path-1200 | 判读 |', '|---|---:|---:|---:|---|']
    for cid in JUDGMENTS:
        rr = [r for r in review['reviews'] if r['case_id'] == cid]
        lines.append('| ' + cid + ' | ' + ' | '.join(f"{r['covered']}/{r['total']}" for r in rr) + ' | ' + CONCLUSIONS[cid] + ' |')
    lines += ['', '三组各 11/18 要点；全部必要要点完整覆盖均为 1/4 题。该结果不是 16 题总体正确率。', '',
        'R11 缺 Freebase 迁移原文，R13 缺子集/语料设置原文，R23 缺 Tree-of-Traversals 预算原文。新增路径主要是 EVALUATED_ON，另有 ToG-R→ToG 的 IMPROVES_UPON，未补齐这些缺口。', '',
        '全 16 题的生成含引用校验 P95：6.090→6.656→7.288 秒；输入 Token：30630→31450→31872。多花预算后，当前证据未显示整体语义收益。', '',
        review['limitations'], '', '[原 16 题总览、柱状图、分类、Token 与完整详情](dashboard.html) · [语义审查网页](semantic-review.html) · [结构化逐项审查](semantic-review.json)', '',
        '[LangSmith 三组对照](' + review['dataset_sync']['comparison_url'] + ')', '']
    for cid in JUDGMENTS:
        ref = review['references'][cid]
        lines += ['## ' + cid, '', '参考答案：' + ref['expected_answer'], '', CONCLUSIONS[cid], '']
        for r in [r for r in review['reviews'] if r['case_id'] == cid]:
            lines += ['### ' + r['arm'] + f"：{r['covered']}/{r['total']}", '',
                '程序状态 `' + r['original_status'] + '` 仅作记录。', '', '**完整回答**', '', r['answer'], '',
                '| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |', '|---|---|---|---|---|']
            for i in r['items']:
                src = review['source_evidence'][i['reference_chunk_id']]
                values = [i['label'], i['verdict'], i['answer_excerpt'] or '未回答',
                    src['title'] + ' p.' + str(src['page_start']) + ' `' + i['reference_chunk_id'] + '`',
                    ', '.join(i['supporting_prompt_chunks']) or '未提供；谨慎结论允许跨来源分析']
                lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
                if i['note']:
                    lines += ['', '判分说明：' + i['note'], '']
            for issue in r['unsupported_or_misleading']:
                lines += ['', '- 无依据/误导表述：“' + issue['answer_excerpt'] + '”。' + issue['reason']]
            lines += ['', '[本题 Experiment 运行记录](' + r['experiment_run_url'] + ')；reference_example_id `' + r['reference_example_id'] + '`。', '',
                '原生成 Trace：' + (r['trace_url'] or '原记录未提供 URL；可由上述已同步的 Experiment 查看已有回答与 Token 子运行。'), '']
        lines += ['### 参考原文与位置', '']
        for source in ref['source_evidence']:
            lines += ['**' + source['title'] + ' p.' + str(source['page_start']) + ' · ' + source['chunk_id'] + '**', '',
                source['source_relative_path'], '', '```text', source['text'], '```', '']
    (folder / 'semantic-review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # Standard-library HTML: complete answers and provenance available without dependencies.
    body = '<h1>额外路径预算：答案语义审查</h1><p>' + escape(review['conclusion']) + '</p><p>' + escape(review['scope']) + '</p>'
    body += '<p>' + escape(review['reviewer'] + '。' + review['rubric']) + '</p><p><a href="dashboard.html">原16题完整总览</a> · <a href="semantic-review.md">逐项文字报告</a> · <a href="semantic-review.json">完整结构化审查</a></p>'
    for arm, a in review['aggregates'].items():
        body += '<div>' + arm + '：' + str(a['covered']) + '/' + str(a['total']) + ' 要点；全部覆盖 ' + str(a['all_required_points']) + '/4 题</div><progress max="18" value="' + str(a['covered']) + '"></progress>'
    for cid in JUDGMENTS:
        body += '<h2>' + cid + '</h2><p>' + escape(CONCLUSIONS[cid]) + '</p>'
        for r in [r for r in review['reviews'] if r['case_id'] == cid]:
            body += '<details open><summary>' + r['arm'] + f"：{r['covered']}/{r['total']}" + '</summary><pre>' + escape(r['answer']) + '</pre><table><tr><th>必要要点</th><th>判定</th><th>回答原句</th></tr>'
            for i in r['items']:
                body += '<tr><td>' + escape(i['label']) + '</td><td>' + i['verdict'] + '</td><td>' + escape(i['answer_excerpt'] or '遗漏') + '</td></tr>'
            body += '</table><details><summary>引用支持、原文可用性、措辞问题与来源位置</summary><pre>' + escape(json.dumps(r, ensure_ascii=False, indent=2)) + '</pre></details></details>'
        body += '<details><summary>完整参考原文与位置</summary><pre>' + escape(json.dumps(review['references'][cid], ensure_ascii=False, indent=2)) + '</pre></details>'
    body += '<p>' + escape(review['limitations']) + '</p>'
    (folder / 'semantic-review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>路径预算语义审查</title><style>body{max-width:1200px;margin:24px auto;font:16px/1.7 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f9;padding:14px}td,th{border:1px solid #ddd;padding:8px}table{border-collapse:collapse;width:100%}details{margin:18px 0}progress{width:65%;height:22px}</style>' + body + '</html>', encoding='utf-8')


def sync(folder, review):
    from langsmith import Client
    status_path = folder / 'semantic-review-sync.json'
    status = dict(status='pending', key=KEY, expected=12, verified=0, new_model_calls=0)
    write_json(status_path, status)
    cfg = settings(ROOT)
    client = Client(api_key=cfg['LANGSMITH_API_KEY'], api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com', timeout_ms=20000, auto_batch_tracing=False)
    try:
        for r in review['reviews']:
            remote = client.read_run(r['experiment_run_id'])
            assert str(remote.reference_example_id) == r['reference_example_id']
            assert remote.outputs['answer'] == r['answer']
        jobs = [dict(run_id=r['experiment_run_id'], key=KEY, score=r['coverage'], value=r['feedback_value'],
            feedback_id=stable_id(r['experiment_run_id'], KEY), stop_after_attempt=1,
            comment='Codex AI 非盲原文审查；事后诊断，非独立人工分数。只审查输入改变的4题，不外推16题总体。') for r in review['reviews']]
        run_ids = [j['run_id'] for j in jobs]
        found = {str(f.id): f for f in client.list_feedback(run_ids=run_ids, feedback_key=[KEY])}
        for j in jobs:
            if j['feedback_id'] not in found:
                client.create_feedback(**j)
        found = {str(f.id): f for f in client.list_feedback(run_ids=run_ids, feedback_key=[KEY])}
        for j in jobs:
            f = found[j['feedback_id']]
            assert abs(f.score-j['score']) <= .000050001
            assert f.value == j['value']
            assert str(f.run_id) == j['run_id']
        status.update(status='verified', verified=len(jobs), reference_examples_verified=12,
            feedback_ids=[j['feedback_id'] for j in jobs], checked_at=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        # Preserve local review; a later --sync retries only missing feedback, never generation.
        status.update(status='pending', error_type=type(exc).__name__)
        raise
    finally:
        write_json(status_path, status)
        client.close()
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, default=DEFAULT)
    parser.add_argument('--sync', action='store_true')
    args = parser.parse_args()
    folder = args.run_dir.resolve()
    review = build(folder)
    write_json(folder / 'semantic-review.json', review)
    render(folder, review)
    verification = dict(local_verified=True, reviewed_answers=len(review['reviews']),
        reference_examples=len(review['references']), aggregates=review['aggregates'], new_model_calls=0,
        checks=['frozen benchmark hash', '12 answer excerpts', '4 changed-input cases', 'identical original evidence', 'all source IDs resolved', 'reference example/run alignment'],
        input_hashes=dict(summary=review['summary_sha256'], benchmark=review['benchmark_sha256'], comparison=review['comparison_sha256']))
    if args.sync:
        verification['remote'] = sync(folder, review)
    else:
        verification['remote'] = dict(status='not_requested')
    assert sha(folder / 'summary.json') == review['summary_sha256']
    assert sha(folder / 'comparison.json') == review['comparison_sha256']
    write_json(folder / 'semantic-review-verification.json', verification)
    print(json.dumps(verification, ensure_ascii=False))


if __name__ == '__main__':
    main()
