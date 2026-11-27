"""Freeze graph-focused v4 questions against the unchanged v3 isolated graph.

Only reference artifacts are created. This script never runs retrieval, generation
or experiments. --check is read-only; --freeze refuses to overwrite an old version.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.evaluation_datasets import dataset_payload
from papertech.evaluation_details import enrich_examples

VERSION = 'benchmark-v4'
PARENT = ROOT / 'artifacts/eval/stage-4/benchmark-v3'
TARGET = ROOT / 'artifacts/eval/stage-4' / VERSION
BLUEPRINT = Path(__file__).with_name('stage4-v4-questions.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def parent_benchmark():
    parent = json.loads((PARENT / 'benchmark.json').read_bytes())
    if sha(PARENT / 'benchmark.json') != (PARENT / 'benchmark.sha256').read_text().strip():
        raise ValueError('parent_benchmark_hash_mismatch')
    graph = PARENT / 'isolated-graph.sqlite3'
    if sha(graph) != parent['graph_build']['graph_sha256']:
        raise ValueError('parent_graph_hash_mismatch')
    return parent, graph


def build():
    parent, graph = parent_benchmark()
    source = json.loads(BLUEPRINT.read_bytes())
    if source['version'] != VERSION or source['graph_version'] != parent['version']:
        raise ValueError('blueprint_version_mismatch')
    bench = deepcopy(parent)
    bench['version'] = VERSION
    bench['source_benchmark_sha256'] = sha(PARENT / 'benchmark.json')
    bench.pop('graph_build')
    bench.pop('validation')
    bench['graph_snapshot'] = dict(version=parent['version'],
        database=graph.relative_to(ROOT).as_posix(), sha256=sha(graph),
        node_count=198, claim_count=204, scope='same frozen isolated graph; no graph edits',
        construction='source-curated developer graph; not an independently extracted test graph')
    bench['freeze_inputs'].update(parent_benchmark_sha256=bench['source_benchmark_sha256'],
        question_blueprint_sha256=sha(BLUEPRINT))
    bench['prior_exposure'] = ('按已知图谱与原文设计的开发/诊断集；图与题目同源，不能作为未见测试集、'
        '自动抽图质量或 Graph 普遍优越性的证据。')
    bench['dataset_description'] = 'v4 图谱关系开发集：8 事实控制、24 跨论文关系、8 反例；同一 v3 图快照，逐项判分，尚未实测。'
    bench['controls'].update(graph_namespace=bench['graph_snapshot']['database'],
        graph_snapshot_sha256=sha(graph), gold_input_policy='Only question text goes into retrieval/generation.',
        comparison_status='not_run', runner_integration='pending: production Workflow still uses the old Neo4j graph',
        fairness='Both arms use the same source corpus, models, reranker and declared budgets; only graph expansion differs.',
        topology='Cross-paper cases compare source-backed subgraphs; no claim that all sources form one connected path.')
    bench['scoring'].update(
        answer_review='Per-case atomic reference criteria, scored 0/1 each by a named reviewer; evidence support and citation location checked separately.',
        semantic_score='Number of supported satisfied atomic criteria / all criteria. This is not calculated by source ID recall.',
        semantic_pass='All criteria satisfied with supporting citations; no critical unsupported claim. Negatives must correct/reject the premise within the evidence boundary.',
        critical_errors=['伪造继承/评测/全称优越性', '颠倒增强方向', '混淆训练与测试角色', '混淆预算耗尽与正确答案', '伪造数值或来源'],
        reporting='Overview, per-category metrics, charts, latency, tokens and full paired details must coexist after real execution.',
        graph_coverage='Source-backed expected subgraphs are a reference check, not measured retrieval success or answer correctness.')
    original = {c['id']: c for c in parent['cases']}
    bench['cases'] = []
    for entry in source['cases']:
        case = deepcopy(original[entry['id']])
        case.update(question=entry['question'], expected_answer=entry['answer'])
        criteria = []
        for index, (keys, text) in enumerate(entry['facts'], 1):
            keys = [keys] if isinstance(keys, str) else keys
            criteria.append(dict(id=f"{case['id']}.C{index:02}", requirement=text, unit_ids=keys,
                supporting_chunks_by_unit={k: bench['units'][k]['known_support_chunks'] for k in keys},
                source_rule='每个列出的 unit 均须有来源支持；同一 unit 内替代来源按 OR。' if keys else '无来源拒答项；不虚构证据或数值。',
                score_values=[0, 1]))
        predicates = sorted({c['predicate'] for c in bench['graph_claims'] if c['unit_id'] in case['units']})
        case['assessment'] = dict(axis=entry['axis'], criteria=criteria,
            max_score=len(criteria), focus_predicates=predicates,
            reference_path_scope='本题各来源单元的预期子图；可能是多条分支或互不相连的跨论文子图。',
            critical_error_rule='触发全局 critical_errors 时本题不判全对，并保留逐项分数与错误说明。',
            reviewer_status='not_reviewed', model_result_status='not_run')
        bench['cases'].append(case)
    return bench


def validate(bench):
    parent, graph = parent_benchmark()
    corpus, papers, chunk_rows = load_corpus(ROOT)
    chunks = {c['chunk_id']: c for c in chunk_rows}
    if corpus != bench['corpus_id'] or sha(graph) != bench['graph_snapshot']['sha256']:
        raise ValueError('corpus_or_graph_changed')
    if Counter(c['category'] for c in bench['cases']) != Counter(fact=8, cross=24, negative=8):
        raise ValueError('category_counts_mismatch')
    if len({c['id'] for c in bench['cases']}) != 40 or len({c['question'] for c in bench['cases']}) != 40:
        raise ValueError('duplicate_question_or_id')
    original = {c['id']: c for c in parent['cases']}
    # Read-only SQLite access; metadata and gold path tables are never runtime inputs.
    con = sqlite3.connect(graph.resolve().as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    try:
        claims = {r['claim_id']: dict(r) for r in con.execute('SELECT * FROM claims')}
        counts = {t: con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
            for t in ('entities', 'claims', 'edges')}
        if counts != dict(entities=198, claims=204, edges=204):
            raise ValueError('graph_counts_changed')
        for claim in claims.values():
            prov = json.loads(claim['provenance_json'])
            chunk = chunks[prov['chunk_id']]
            expected_hash = hashlib.sha256(claim['evidence_quote'].encode('utf-8')).hexdigest()
            if (not claim['evidence_quote'] or claim['evidence_quote'] not in chunk['text'] or claim['source_hash'] != expected_hash
                    or prov['paper_id'] != chunk['paper_id'] or prov['page_start'] != chunk['page_start']
                    or prov['page_end'] != chunk['page_end']):
                raise ValueError('graph_source_mismatch:' + claim['claim_id'])
        for unit in bench['units'].values():
            if set(unit['known_support_chunks']) != {s['chunk_id'] for s in unit['support_sources']}:
                raise ValueError('support_pool_not_fully_displayed')
            for src in unit['support_sources']:
                chunk = chunks[src['chunk_id']]
                if (src['text'] != chunk['text'] or src['text_sha256'] != chunk['text_sha256']
                        or not src['source_spans'] or chunk.get('content_kind') == 'references'):
                    raise ValueError('source_excerpt_or_location_mismatch')
        rows = []
        for case in bench['cases']:
            old = original[case['id']]
            if case['units'] != old['units'] or case['question'] == old['question']:
                raise ValueError('case_support_changed_or_question_not_revised:' + case['id'])
            if not case['generate'] or not case['expected_answer']:
                raise ValueError('missing_answer_or_generation_contract')
            if case['category'] == 'cross' and len(case['source_papers']) < 2:
                raise ValueError('cross_case_needs_multiple_papers')
            criteria = case['assessment']['criteria']
            if not criteria or len({r['id'] for r in criteria}) != len(criteria):
                raise ValueError('missing_or_duplicate_rubric')
            covered = {u for r in criteria for u in r['unit_ids']}
            if covered != set(case['units']):
                raise ValueError('rubric_source_units_mismatch:' + case['id'])
            path_count = 0
            for unit_id in case['units']:
                for path in bench['paths_by_unit'][unit_id]:
                    edge_rows = [claims[cid] for cid in path['claim_ids']]
                    if not edge_rows:
                        raise ValueError('empty_reference_path')
                    for left, right in zip(edge_rows, edge_rows[1:]):
                        if (left['object_type'], left['object']) != (right['subject_type'], right['subject']):
                            raise ValueError('non_contiguous_path')
                    actual_nodes = [dict(type=edge_rows[0]['subject_type'], name=edge_rows[0]['subject'])]
                    actual_nodes += [dict(type=r['object_type'], name=r['object']) for r in edge_rows]
                    if actual_nodes != path['nodes'] or any(r['unit_id'] != unit_id for r in edge_rows):
                        raise ValueError('reference_path_nodes_or_unit_mismatch')
                    path_count += 1
            rows.append(dict(case_id=case['id'], category=case['category'], axis=case['assessment']['axis'],
                source_papers=len(case['source_papers']), criteria=len(criteria), reference_paths=path_count,
                focus_predicates=case['assessment']['focus_predicates'],
                status='source_backed_reference_checked' if case['units'] else 'no_source_negative'))
        absent_names = ('NebulaGraphRAG-2099', 'LunarQA-2099')
        for name in absent_names:
            if any(name.casefold() in c['text'].casefold() for c in chunks.values()):
                raise ValueError('negative_anchor_present_in_corpus')
    finally:
        con.close()
    return dict(status='reference_checks_passed', benchmark=VERSION,
        questions=40, categories=dict(Counter(c['category'] for c in bench['cases'])),
        graph_counts=counts, source_papers=len(papers), source_units=len(bench['units']),
        atomic_criteria=sum(r['criteria'] for r in rows), covered_predicates=sorted({p for r in rows for p in r['focus_predicates']}),
        graph_unchanged=True, parent_benchmark_unchanged=True,
        semantic_gold_review='Codex source review; not independent human scoring',
        model_calls=0, model_comparison='not_run', cases=rows)


def payload_for(bench, digest, chunks):
    return enrich_examples(dataset_payload(bench, digest), bench, chunks)


def render_questions(bench):
    lines = ['# v4 图谱关系评测题集', '',
        '40 题：8 道事实控制题、24 道跨论文关系题、8 道反例。沿用 v3 冻结图，不修改旧题集或图谱。', '',
        '**状态：模型对照未运行；在线 Workflow 接入隔离图仍待完成。**', '',
        '这是按已知图谱和历史材料设计的开发集；不作为未见测试集或图扩展普遍胜出的证据。', '',
        '## 判分约定', '',
        '- 检索支持池覆盖、图参考路径、引用有效性、答案语义分开报告。',
        '- 每项必要事实按 0/1 记录，保留原文引用及审查说明；不能用命中块 ID 代替语义评分。',
        '- 全对需满足全部事实，且无关键关系错误或捏造；负例需纠正前提并限定证据边界。',
        '- 跨论文题可以需要多条独立子图，不把它们画成一条不存在的连续路径。',
        '- 下面的来源原文、预期路径、判分项均属于 reference outputs，仅 question 可进入被测输入。', '',
        '## 逐题参考答案、判分与原文', '']
    for case in bench['cases']:
        a = case['assessment']
        lines += [f"### {case['id']} · {a['axis']} · {case['category']}", '', case['question'], '',
            '**参考答案：** ' + case['expected_answer'], '', '**逐项判分：**', '']
        lines += [f"- `{r['id']}`：{r['requirement']}（来源：{', '.join(r['unit_ids']) or '无来源拒答'}）" for r in a['criteria']]
        lines += ['', '**考查关系：** ' + (', '.join(a['focus_predicates']) or '无来源实体与数值拒答'), '']
        if case.get('must_not_claim'):
            lines += ['**错误边界：** ' + case['must_not_claim'], '']
        seen = set()
        for unit_id in case['units']:
            for path in bench['paths_by_unit'][unit_id]:
                ids = path['claim_ids']
                claim_map = {c['claim_id']: c for c in bench['graph_claims']}
                edges = [claim_map[cid] for cid in ids]
                chain = edges[0]['subject'] + ''.join(f" —{e['predicate']}→ {e['object']}" for e in edges)
                lines += [f"- 参考路径 `{path['path_id']}`：{chain}"]
            lines.append('')
            for src in bench['units'][unit_id]['support_sources']:
                if src['chunk_id'] in seen:
                    continue
                seen.add(src['chunk_id'])
                lines += [f"**完整来源：** {src['title']}；PDF 页 {src['page_start']}—{src['page_end']}；"
                    f"`{src['source_relative_path']}`；块 `{src['chunk_id']}`。", '',
                    '字符位置：`' + json.dumps(src['source_spans'], ensure_ascii=False) + '`', '',
                    '```text', src['text'].rstrip(), '```', '']
    return '\n'.join(lines) + '\n'


def render_coverage(audit):
    lines = ['# v4 题目与图关系映射', '',
        f"本地参考校验通过：40 题，{audit['atomic_criteria']} 个逐项判分点，"
        f"覆盖 {len(audit['covered_predicates'])} 种实际关系谓词。模型对照未运行。", '',
        '39 题有原文支持；N06 是无来源负例。覆盖表示参考材料可核查，不是实测召回或答案正确率。', '',
        '| 题号 | 考查能力 | 来源论文数 | 判分项 | 参考路径数 |', '|---|---|---:|---:|---:|']
    lines += [f"| {r['case_id']} | {r['axis']} | {r['source_papers']} | {r['criteria']} | {r['reference_paths']} |" for r in audit['cases']]
    lines += ['', '图的 204 条关系记录由 89 条旧批准记录与 115 条定向整理记录组成；题目聚焦新增关系。',
        '所有跨论文关系均须引用各自来源；共同实体不自动建立继承、因果或受控性能关系。', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--freeze', action='store_true')
    action.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.freeze and TARGET.exists():
        raise RuntimeError('refusing_to_overwrite_frozen_v4')
    bench = build()
    audit = validate(bench)
    raw = encoded(bench)
    digest = hashlib.sha256(raw).hexdigest()
    _, _, chunk_rows = load_corpus(ROOT)
    payload = payload_for(bench, digest, {c['chunk_id']: c for c in chunk_rows})
    for case, example in zip(bench['cases'], payload['examples']):
        if example['inputs'] != {'question': case['question']}:
            raise ValueError('gold_leaked_into_inputs')
        if example['outputs']['assessment'] != case['assessment']:
            raise ValueError('rubric_not_exported')
    questions = render_questions(bench)
    page = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>v4 图谱关系题集</title>'
        '<style>body{max-width:1100px;margin:32px auto;padding:0 20px;font:16px/1.7 system-ui}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}input{width:100%;padding:10px;box-sizing:border-box}'
        'article{border-top:1px solid #ddd;margin-top:24px}summary{cursor:pointer}</style>'
        '<h1>v4 图谱关系题集 · 40 题</h1><p>未运行模型对照。8 事实控制＋24 跨论文关系＋8 反例。'
        '同一 v3 冻结图；开发集，不预设图扩展胜出。</p><label>搜索题号、问题或关系：'
        '<input id="search" type="search"></label>' + ''.join(
            '<article><h2>' + html.escape(e['metadata']['case_id'] + ' · ' + e['outputs']['assessment']['axis'])
            + '</h2><p>' + html.escape(e['inputs']['question']) + '</p><p><b>参考答案：</b>'
            + html.escape(e['outputs']['expected_answer'])
            + '</p><details><summary>逐项判分、原文位置、预期路径及完整参考信息</summary><pre>'
            + html.escape(encoded(e['outputs']).decode('utf-8')) + '</pre></details></article>'
            for e in payload['examples']) + '<script>document.getElementById("search").addEventListener("input",e=>{'
        'const q=e.target.value.toLowerCase();document.querySelectorAll("article").forEach(a=>'
        'a.hidden=!a.textContent.toLowerCase().includes(q))});</script></html>')
    files = {'benchmark.json': raw, 'benchmark.sha256': (digest + '\n').encode('ascii'),
        'langsmith-dataset.json': encoded(payload), 'coverage.json': encoded(audit),
        'questions.md': questions.encode('utf-8'), 'coverage.md': render_coverage(audit).encode('utf-8'),
        'questions.html': page.encode('utf-8')}
    files.update({'cases/' + e['metadata']['case_id'] + '.json': encoded(e) for e in payload['examples']})
    if args.freeze:
        TARGET.mkdir(parents=True)
        for name, content in files.items():
            path = TARGET / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        save(TARGET / 'langsmith-status.json', dict(benchmark=VERSION, benchmark_sha256=digest,
            status='local_dataset_ready_not_uploaded', examples_expected=40, model_comparison='not_run'))
    else:
        for name, content in files.items():
            actual = (TARGET / name).read_bytes()
            # The shared Windows uploader uses CRLF; reference JSON values must
            # match exactly, while the hashed benchmark keeps its exact bytes.
            matches = (json.loads(actual) == json.loads(content)
                if name.endswith('.json') and name != 'benchmark.json' else actual == content)
            if not matches:
                raise ValueError('frozen_artifact_mismatch:' + name)
    print(json.dumps(dict(status='frozen' if args.freeze else 'verified', benchmark=VERSION,
        benchmark_sha256=digest, questions=40, atomic_criteria=audit['atomic_criteria'],
        predicates=len(audit['covered_predicates']), graph_unchanged=True, model_calls=0,
        model_comparison='not_run'), ensure_ascii=False))


if __name__ == '__main__':
    main()
