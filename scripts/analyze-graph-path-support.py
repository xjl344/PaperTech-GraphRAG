"""只读分析：图路径指向的块有多少真的命中冻结支持池。

目的（对应 2026-11-16 讨论）：决定 C 方案（路径只做后台证据选择、
不再发送给生成模型）是否值得实现。若图路径的 chunk 极少命中
冻结支持池，则 C 方案做了也不会提升覆盖。

只读约束（本脚本不产生任何新运行结果）：
  * 不调用任何模型、向量接口或检索后端；
  * 不写 benchmark / 运行目录 / 生产代码；
  * 仅读取已有候选快照与冻结题集，在 stdout 输出统计表，
    可选 `--output` 写一份 JSON 分析报告（不是评测结果）。

用法：
  python -X utf8 scripts/analyze-graph-path-support.py
  python -X utf8 scripts/analyze-graph-path-support.py --output artifacts/reports/stage-4/graph-path-support-probe.json
"""
import argparse
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK = os.path.join(ROOT, 'artifacts', 'eval', 'stage-4', 'benchmark-source-coverage-v1', 'benchmark.json')
RUNS = os.path.join(ROOT, 'artifacts', 'reports', 'stage-4', 'benchmark-source-coverage-v1', 'optimization-runs')
MAX_EVIDENCE = 8          # evidence_context.assemble: len(later) < 8
BASELINE_FLOOR = '第一步基线（Budget-before）'


def unit_pools(units):
    """unit_id -> 已知支持块集合（OR 语义，与 evaluation.support_metrics 一致）。"""
    return {uid: set(u['known_support_chunks']) for uid, u in units.items()}


def coverage(chunk_ids, unit_ids, pools):
    """按必要事实单元计算冻结支持池覆盖（OR：任一支持块命中即算）。"""
    if not unit_ids:
        return None
    ids = set(chunk_ids)
    return sum(bool(ids & pools[uid]) for uid in unit_ids) / len(unit_ids)


def graph_path_chunks(paths):
    """按出现顺序去重收集图路径指向的 chunk_id。"""
    seen, out = set(), []
    for path in paths or []:
        for item in path.get('evidence') or []:
            cid = item.get('chunk_id')
            if cid and cid not in seen:
                seen.add(cid)
                out.append(cid)
    return out


def latest_run():
    """最新一轮真实检索快照（optimization-runs/latest.json）所在目录。"""
    latest = os.path.join(RUNS, 'latest.json')
    if os.path.isfile(latest):
        with open(latest, encoding='utf-8') as handle:
            data = json.load(handle)
        for key in ('run_id', 'id', 'run'):
            if isinstance(data.get(key), str):
                return os.path.join(RUNS, data[key])
        if isinstance(data.get('summary'), str):
            return os.path.dirname(data['summary'])
    candidates = sorted(glob.glob(os.path.join(RUNS, '*', '*-candidates.json')),
                        key=os.path.getmtime, reverse=True)
    if not candidates:
        raise SystemExit('找不到候选快照：%s' % RUNS)
    return os.path.dirname(candidates[0])


def analyze(case_id, case, pools, run_dir):
    cand_path = os.path.join(run_dir, '%s-candidates.json' % case_id)
    if not os.path.isfile(cand_path):
        return {'case_id': case_id, 'skipped': '缺少候选快照'}
    with open(cand_path, encoding='utf-8') as handle:
        cand = json.load(handle)
    base = os.path.join(run_dir, '%s-baseline.json' % case_id)
    evid = []
    if os.path.isfile(base):
        with open(base, encoding='utf-8') as handle:
            evid = [e['chunk_id'] for e in (json.load(handle).get('evidence') or [])]

    unit_ids = case['units']
    paths = cand.get('graph_paths') or []
    path_chunks = graph_path_chunks(paths)
    reranked = [row['chunk_id'] for row in cand.get('reranked_final') or []]
    graph_stage = [row['chunk_id'] for row in cand.get('candidates_by_stage', {}).get('graph') or []]

    hits = [cid for cid in path_chunks if any(cid in pools[u] for u in unit_ids)]
    # 图路径独有的支持块：命中支持池但最终重排候选里没有 —— 图真正"补进来"的东西
    novel = [cid for cid in hits if cid not in set(reranked)]
    return {
        'case_id': case_id,
        'units': unit_ids,
        'path_count': len(paths),
        'graph_stage_chunks': len(graph_stage),
        'path_chunks': len(path_chunks),
        'path_chunks_hit_support': len(hits),
        'path_chunks_novel_support': len(novel),
        'coverage_final_ranked': coverage(reranked, unit_ids, pools),
        'coverage_baseline_evidence': coverage(evid, unit_ids, pools),
        'coverage_baseline_plus_paths': coverage(evid + path_chunks, unit_ids, pools),
        'missing_units': [uid for uid in unit_ids
                          if not set(path_chunks) & pools[uid]],
    }


def percent(value):
    return '—' if value is None else '%.1f%%' % (100 * value)


def main(argv=None):
    parser = argparse.ArgumentParser(description='只读统计：图路径指向的块命中冻结支持池的比例')
    parser.add_argument('--benchmark', default=BENCHMARK)
    parser.add_argument('--run-dir', default=None, help='候选快照目录；缺省取 optimization-runs/latest.json')
    parser.add_argument('--output', default=None, help='可选：把分析结果写成 JSON（不是评测结果）')
    args = parser.parse_args(argv)

    with open(args.benchmark, encoding='utf-8') as handle:
        bench = json.load(handle)
    pools = unit_pools(bench['units'])
    cases = {c['id']: c for c in bench['cases']}
    run_dir = args.run_dir or latest_run()
    print('题集:', bench['version'], '| 题数:', len(cases))
    print('候选快照目录:', os.path.relpath(run_dir, ROOT))
    print('说明：只读统计，无模型调用、无新检索。')
    print()

    rows = [analyze(cid, case, pools, run_dir) for cid, case in sorted(cases.items())]
    done = [r for r in rows if 'skipped' not in r]
    if not done:
        raise SystemExit('没有可用候选快照')

    header = ('题目', '路径数', '路径chunk', '命中支持池', '独有命中',
              '最终候选覆盖', '基线证据覆盖', '基线+路径覆盖')
    print('%-6s %6s %9s %11s %9s %13s %13s %13s' % header)
    print('-' * 92)
    for row in done:
        print('%-6s %6d %9d %11d %9d %13s %13s %13s' % (
            row['case_id'], row['path_count'], row['path_chunks'],
            row['path_chunks_hit_support'], row['path_chunks_novel_support'],
            percent(row['coverage_final_ranked']),
            percent(row['coverage_baseline_evidence']),
            percent(row['coverage_baseline_plus_paths'])))
    print('-' * 92)
    keyed = [r for r in done if r['coverage_baseline_evidence'] is not None]
    if keyed:
        mean = lambda k: statistics.mean([r[k] if r[k] is not None else 0 for r in keyed])
        print('均值     %6.1f %9.1f %11.1f %9.1f %13s %13s %13s' % (
            mean('path_count'), mean('path_chunks'), mean('path_chunks_hit_support'),
            mean('path_chunks_novel_support'),
            percent(mean('coverage_final_ranked')),
            percent(mean('coverage_baseline_evidence')),
            percent(mean('coverage_baseline_plus_paths'))))
        print()
        gain = [r['coverage_baseline_plus_paths'] - r['coverage_baseline_evidence'] for r in keyed]
        print('基线证据 + 图路径 相比 基线证据：%d 题提高 / %d 题持平 / %d 题无变化' % (
            sum(1 for g in gain if g > 1e-9), sum(1 for g in gain if abs(g) <= 1e-9),
            sum(1 for g in gain if g < -1e-9)))
        print('命中支持池的路径块总数:', sum(r['path_chunks_hit_support'] for r in keyed))
        print('图路径独有支持块（最终候选里没有）:', sum(r['path_chunks_novel_support'] for r in keyed))

    if args.output:
        payload = dict(
            kind='graph-path-support-probe', read_only=True, generated_from=os.path.relpath(run_dir, ROOT),
            benchmark=bench['version'], cases=len(done), rows=rows,
            note='这是只读诊断统计，不是新的评测运行，不代表答案正确率。')
        with open(args.output, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        print('\n已写入分析结果:', os.path.relpath(args.output, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())