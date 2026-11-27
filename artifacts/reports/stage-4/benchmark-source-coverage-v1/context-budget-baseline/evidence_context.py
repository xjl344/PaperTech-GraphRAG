"""Budgeted comparison coverage and paths grounded in the selected source text."""
import json
from .entity_aliases import source_groups
from .retrieval import select_evidence


def requested_groups(question, chunk_map):
    return source_groups(question, chunk_map)


def reserve_sources(ranked, chunk_map, groups, budget):
    """Keep the best fitting relevant chunk per named paper, before filling.

    Leave the minimum feasible cost of later papers available. This prevents an
    early long chunk from consuming the budget when shorter relevant options
    could retain every source. No chunk text is shortened or gold inspected.
    """
    options = {}
    for group in groups:
        options[group['paper_id']] = []
        for row in ranked:
            if chunk_map[row['chunk_id']]['paper_id'] != group['paper_id']:
                continue
            evidence, _ = select_evidence([row], chunk_map, budget=budget)
            if evidence:
                options[group['paper_id']].append((row, evidence[0]['context_bytes']))
    chosen, remaining = [], budget
    for index, group in enumerate(groups):
        candidates = options[group['paper_id']]
        minimum_later = sum(min(cost for _, cost in options[later['paper_id']])
            for later in groups[index + 1:] if options[later['paper_id']])
        fitting = [(row, cost) for row, cost in candidates if cost + minimum_later <= remaining]
        if not fitting:
            fitting = [(row, cost) for row, cost in candidates if cost <= remaining]
        if fitting and len(chosen) < 8:
            row, cost = fitting[0]
            chosen.append(row)
            remaining -= cost
    return chosen, options


def assemble(ranked, chunk_map, paths, question, comparison=False, budget=6000):
    named=requested_groups(question,chunk_map)
    comparison=comparison or len(named)>=2
    groups=named if comparison else []
    prioritized,options=reserve_sources(ranked,chunk_map,groups,budget)
    used_ids={row['chunk_id'] for row in prioritized}
    prioritized.extend(r for r in ranked if r['chunk_id'] not in used_ids)
    evidence,used=select_evidence(prioritized,chunk_map,budget=budget)
    allowed={e['chunk_id']:e for e in evidence}
    selected_paths=[]; graph_bytes=0
    for path in paths:
        if not path.get('evidence') or any(e['chunk_id'] not in allowed or e['quote'] not in allowed[e['chunk_id']]['quote'] for e in path['evidence']):
            continue
        compact=dict(nodes=[dict(name=n['name'],type=n['type']) for n in path['nodes']],
                     edges=path['edges'],evidence=path['evidence'])
        size=len(json.dumps(compact,ensure_ascii=False).encode('utf-8'))
        if used+graph_bytes+size>budget or len(selected_paths)>=4:
            continue
        selected_paths.append(compact); graph_bytes+=size
    # If ordinary filling exhausted the budget, reserve space for one supported path.
    if paths and not selected_paths and len(evidence)>2:
        for path in paths:
            if not path.get('evidence') or any(e['chunk_id'] not in allowed for e in path['evidence']):
                continue
            compact=dict(nodes=[dict(name=n['name'],type=n['type']) for n in path['nodes']],edges=path['edges'],evidence=path['evidence'])
            size=len(json.dumps(compact,ensure_ascii=False).encode('utf-8'))
            required={e['chunk_id'] for e in path['evidence']}
            reduced=list(evidence)
            for e in reversed(evidence):
                protected=any(e['paper_id']==g['paper_id'] and sum(x['paper_id']==g['paper_id'] for x in reduced)==1 for g in groups)
                if used+size<=budget:
                    break
                if e['chunk_id'] not in required and not protected:
                    reduced.remove(e); used-=e['context_bytes']
            if used+size<=budget and all(e['quote'] in allowed[e['chunk_id']]['quote'] for e in path['evidence']):
                evidence=reduced; selected_paths=[compact]; graph_bytes=size; break
            # Restore the budget before trying another path.
            used=sum(e['context_bytes'] for e in evidence)
    missing=[g['name'] for g in groups if not any(e['paper_id']==g['paper_id'] for e in evidence)]
    source_coverage=[dict(**group, eligible_candidate_count=len(options[group['paper_id']]),
        selected_chunk_ids=[e['chunk_id'] for e in evidence if e['paper_id']==group['paper_id']],
        missing_reason=('no_eligible_source_candidate' if not options[group['paper_id']] else 'context_budget')
            if not any(e['paper_id']==group['paper_id'] for e in evidence) else None)
        for group in groups]
    gaps=[]
    if missing:
        gaps.append('缺少以下方法的独立论文证据：'+', '.join(missing))
    if comparison:
        gaps.append('检索到同一数据集不代表实验条件可比；仅按原文核对数据划分、底座模型、指标和协议，缺项须说明。')
    return evidence,selected_paths,dict(context_bytes=used+graph_bytes,evidence_bytes=used,graph_context_bytes=graph_bytes,
                                     comparison_groups=groups,missing_comparison_groups=missing,
                                     source_coverage=source_coverage,limitations=gaps)
