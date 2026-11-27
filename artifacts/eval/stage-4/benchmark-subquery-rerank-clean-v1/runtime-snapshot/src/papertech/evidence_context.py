"""Budgeted comparison coverage and paths grounded in the selected source text."""
import json
from .entity_aliases import source_groups
from .retrieval import select_evidence
from .citations import prompt_evidence, quote_options


def path_prompt(path, allowed, path_format='references'):
    """Validate full path provenance, then encode references to supplied quotes.

    Full quotes remain in generation_paths for auditing. The provider receives
    chunk/quotation IDs and exact source offsets, without duplicating the text.
    """
    if path_format not in ('full', 'references'):
        raise ValueError('unknown_path_format')
    if not path.get('evidence'):
        return None
    references = []
    for item in path['evidence']:
        source = allowed.get(item.get('chunk_id'))
        quote = item.get('quote')
        if source is None or not isinstance(quote, str) or not quote or quote not in source['quote']:
            return None
        start = source['quote'].find(quote)
        end = start + len(quote)
        ids = []
        offset = 0
        for option in quote_options(source['quote']):
            position = source['quote'].find(option['quote'], offset)
            if position < 0:
                raise ValueError('quotation_option_position_missing')
            stop = position + len(option['quote'])
            if position < end and stop > start:
                ids.append(option['quote_id'])
            offset = stop
        if not ids:
            return None
        reference = dict(chunk_id=item['chunk_id'], quote_ids=ids, source_span=[start, end])
        if item.get('claim_id'):
            reference['claim_id'] = item['claim_id']
        references.append(reference)
    return dict(nodes=[dict(name=node['name'], type=node['type']) for node in path['nodes']],
        edges=path['edges'], evidence=path['evidence'] if path_format == 'full' else references)


def content_bytes(evidence, prompt_paths):
    """Exact serialized evidence/path payload, excluding question and rules."""
    return len(json.dumps(dict(evidence=[prompt_evidence(e) for e in evidence],
        graph_paths=prompt_paths), ensure_ascii=False).encode('utf-8'))


def requested_groups(question, chunk_map):
    return source_groups(question, chunk_map)


def reserve_sources(ranked, chunk_map, groups, budget, evidence_max=8):
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
        if fitting and len(chosen) < evidence_max:
            row, cost = fitting[0]
            chosen.append(row)
            remaining -= cost
    return chosen, options


def assemble(ranked, chunk_map, paths, question, comparison=False, budget=6000, path_format='references', path_budget=0, path_budget_mode='additional', evidence_max=8, source_policy='named_first'):
    """Add an independent path budget without shrinking original evidence.

    Zero keeps legacy leftovers. The reserved mode only reproduces the earlier
    experiment that subtracted a path quota from the evidence budget.
    """
    if path_budget_mode not in ('additional', 'reserved'):
        raise ValueError('invalid_path_budget_mode')
    if (isinstance(path_budget, bool) or not isinstance(path_budget, int) or path_budget < 0
            or (path_budget_mode == 'reserved' and path_budget > budget)):
        raise ValueError('invalid_path_budget')
    if path_format not in ('full', 'references'):
        raise ValueError('unknown_path_format')
    if source_policy not in ('named_first', 'score_order'):
        raise ValueError('invalid_source_policy')
    if isinstance(evidence_max, bool) or not isinstance(evidence_max, int) or not 1 <= evidence_max <= 40:
        raise ValueError('invalid_evidence_max')
    named=requested_groups(question,chunk_map)
    comparison=comparison or len(named)>=2
    groups=named if comparison and source_policy == 'named_first' else []
    evidence_budget=budget-path_budget if path_budget_mode == 'reserved' else budget
    total_budget=budget+path_budget if path_budget_mode == 'additional' else budget
    prioritized,options=reserve_sources(ranked,chunk_map,groups,evidence_budget,evidence_max=evidence_max)
    used_ids={row['chunk_id'] for row in prioritized}
    prioritized.extend(r for r in ranked if r['chunk_id'] not in used_ids)
    evidence,used=select_evidence(prioritized,chunk_map,budget=evidence_budget,evidence_max=evidence_max)
    allowed={e['chunk_id']:e for e in evidence}
    selected_paths=[]; prompt_paths=[]; graph_bytes=0
    for path in paths:
        prompt = path_prompt(path, allowed, path_format)
        if prompt is None:
            continue
        compact=dict(nodes=[dict(name=n['name'],type=n['type']) for n in path['nodes']],
                     edges=path['edges'],evidence=path['evidence'])
        next_bytes=len(json.dumps(prompt_paths + [prompt],ensure_ascii=False).encode('utf-8'))
        if (next_bytes>path_budget if path_budget else used+next_bytes>budget) or len(selected_paths)>=4:
            continue
        selected_paths.append(compact); prompt_paths.append(prompt); graph_bytes=next_bytes
    serialized=content_bytes(evidence,prompt_paths)
    if used+graph_bytes>total_budget or (evidence and serialized>total_budget):
        raise ValueError('serialized_evidence_budget_exceeded')
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
    detail=dict(context_bytes=used+graph_bytes,evidence_bytes=used,graph_context_bytes=graph_bytes,
                                     serialized_content_bytes=serialized, prompt_graph_paths=prompt_paths,
                                     path_policy='evidence_first',path_format=path_format,
                                     comparison_groups=groups,missing_comparison_groups=missing,
                                     source_coverage=source_coverage,limitations=gaps)
    # Do not change the legacy zero-quota result, including audit metadata.
    if path_budget:
        detail.update(path_policy='additional_path_budget' if path_budget_mode == 'additional' else 'reserved_path_quota',
                      evidence_budget_bytes=evidence_budget, path_budget_bytes=path_budget, total_budget_bytes=total_budget)
    return evidence,selected_paths,detail
