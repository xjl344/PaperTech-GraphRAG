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


def reserve_sources_round_robin(ranked, chunk_map, groups, budget, evidence_max=12, score_policy='relative',
                                min_score=0.05, min_floor=0.01, per_group_rounds=2, subquery_ids=None):
    """Reserve highest-ranked evidence per named paper (and per subquery) without preferring shorter blocks."""
    floor = min_floor if score_policy == 'relative' else min_score
    options = {}
    for group in groups:
        options[group['paper_id']] = []
        for row in ranked:
            if chunk_map[row['chunk_id']]['paper_id'] != group['paper_id']:
                continue
            evidence, _ = select_evidence([row], chunk_map, budget=budget, min_score=floor, score_policy='fixed')
            if evidence:
                options[group['paper_id']].append((row, evidence[0]['context_bytes']))
    chosen, chosen_ids, remaining = [], set(), budget
    rounds = per_group_rounds if len(groups) >= 2 else 1
    for _ in range(rounds):
        for group in groups:
            if len(chosen) >= evidence_max:
                break
            for row, cost in options[group['paper_id']]:
                if row['chunk_id'] in chosen_ids or cost > remaining:
                    continue
                chosen.append(row)
                chosen_ids.add(row['chunk_id'])
                remaining -= cost
                break
    # Also ensure each planned subquery gets at least one top eligible chunk when budget allows.
    for sq_id in (subquery_ids or ()):
        if len(chosen) >= evidence_max:
            break
        sq_rows = [row for row in ranked if row.get('best_query_id') == sq_id or sq_id in (row.get('found_by') or ())]
        if any(row['chunk_id'] in chosen_ids for row in sq_rows[:2]):
            continue
        for row in sq_rows:
            if row['chunk_id'] in chosen_ids:
                continue
            evidence, _ = select_evidence([row], chunk_map, budget=budget, min_score=floor, score_policy='fixed')
            if not evidence:
                continue
            cost = evidence[0]['context_bytes']
            if cost <= remaining:
                chosen.append(row)
                chosen_ids.add(row['chunk_id'])
                remaining -= cost
                break
    # Protect up to 2 high-scoring graph/method-card supported bridge chunks that pass the quality bar.
    bridge_added = 0
    for row in ranked:
        if bridge_added >= 2 or len(chosen) >= evidence_max:
            break
        if row['chunk_id'] in chosen_ids:
            continue
        if not (row.get('graph_supported') or row.get('method_card_supported')):
            continue
        if 'rerank_score' in row and row['rerank_score'] < 0.08:
            continue
        evidence, _ = select_evidence([row], chunk_map, budget=budget, min_score=floor, score_policy='fixed')
        if evidence and evidence[0]['context_bytes'] <= remaining:
            chosen.append(row)
            chosen_ids.add(row['chunk_id'])
            remaining -= evidence[0]['context_bytes']
            bridge_added += 1
    return chosen, options


def reserve_sources_subquery_balanced(ranked, chunk_map, groups, budget, evidence_max=12, score_policy='relative',
                                      min_score=0.05, min_floor=0.01, subquery_ids=None, diversity_threshold=0.55):
    """Per-subquery calibrated round-robin reservation + MMR diversity to prevent one subquery dominating slots."""
    from .retrieval import lexical_jaccard
    floor = min_floor if score_policy == 'relative' else min_score
    options = {}
    for group in groups:
        options[group['paper_id']] = []
        for row in ranked:
            if chunk_map[row['chunk_id']]['paper_id'] != group['paper_id']:
                continue
            evidence, _ = select_evidence([row], chunk_map, budget=budget, min_score=floor, score_policy='fixed')
            if evidence:
                options[group['paper_id']].append((row, evidence[0]['context_bytes']))

    cost_cache = {}
    def chunk_cost(row):
        cid = row['chunk_id']
        if cid not in cost_cache:
            ev, _ = select_evidence([row], chunk_map, budget=budget, min_score=floor, score_policy='fixed')
            cost_cache[cid] = ev[0]['context_bytes'] if ev else None
        return cost_cache[cid]

    chosen, chosen_ids, remaining = [], set(), budget
    def too_similar(row):
        if diversity_threshold is None:
            return False
        c = chunk_map[row['chunk_id']]
        for prev in chosen:
            pc = chunk_map[prev['chunk_id']]
            if pc['paper_id'] == c['paper_id'] and lexical_jaccard(c['text'], pc['text']) >= diversity_threshold:
                return True
        return False

    def try_add(row, enforce_diversity=True):
        nonlocal remaining
        cid = row['chunk_id']
        if cid in chosen_ids or len(chosen) >= evidence_max:
            return False
        if enforce_diversity and too_similar(row):
            return False
        cost = chunk_cost(row)
        if cost is None or cost > remaining:
            return False
        chosen.append(row)
        chosen_ids.add(cid)
        remaining -= cost
        return True

    # Round 1: guarantee Top-1 per named paper.
    for group in groups:
        for row, _ in options[group['paper_id']]:
            if try_add(row, enforce_diversity=False):
                break

    # Build per-subquery calibrated rankings using owner_scores (or rerank_score for discovered items).
    sq_list = list(subquery_ids or ())
    sq_lists = {}
    sq_max = {}
    for sq_id in sq_list:
        items = []
        for row in ranked:
            oscores = row.get('owner_scores') or {}
            if sq_id in oscores:
                items.append((float(oscores[sq_id]), row))
            elif row.get('best_query_id') == sq_id or sq_id in (row.get('found_by') or ()):
                items.append((float(row.get('rerank_score') or 0.0), row))
        items.sort(key=lambda x: (-x[0], x[1]['chunk_id']))
        sq_lists[sq_id] = items
        sq_max[sq_id] = items[0][0] if items else 0.0

    # Round 1..2: bounded per-subquery round-robin (max 2 rounds; round 2 requires strong relevance so global Top-K is never crowded out).
    if sq_list:
        for rnd in range(2):
            for sq_id in sq_list:
                if len(chosen) >= evidence_max:
                    break
                peak = sq_max.get(sq_id, 0.0)
                min_rel_raw = max(0.25, 0.45 * peak) if rnd > 0 else floor
                picked = False
                for score, row in sq_lists[sq_id]:
                    if score < min_rel_raw:
                        break
                    if try_add(row, enforce_diversity=True):
                        picked = True
                        break
                if not picked and rnd == 0:
                    for score, row in sq_lists[sq_id]:
                        if score < floor:
                            break
                        if try_add(row, enforce_diversity=False):
                            break
    else:
        # No subqueries: give each named paper a second round as in round_robin.
        if len(groups) >= 2:
            for group in groups:
                for row, _ in options[group['paper_id']]:
                    if try_add(row, enforce_diversity=True):
                        break

    # Calibrated fill order for remaining slots: combine raw score with per-subquery normalized score.
    calibrated_rest = []
    for row in ranked:
        if row['chunk_id'] in chosen_ids:
            continue
        raw = float(row.get('rerank_score') or 0.0)
        oscores = row.get('owner_scores') or {}
        rel = 0.0
        for sq_id, sc in oscores.items():
            peak = sq_max.get(sq_id, 0.0)
            if peak > 1e-6 and sc >= 0.03:
                rel = max(rel, sc / peak)
        bridge_bonus = 0.03 if (row.get('graph_supported') or row.get('method_card_supported')) and raw >= 0.08 else 0.0
        calibrated = (0.65 * raw + 0.35 * rel + bridge_bonus) if sq_list else (raw + bridge_bonus)
        calibrated_rest.append((calibrated, row))
    calibrated_rest.sort(key=lambda x: (-x[0], x[1]['chunk_id']))
    return chosen, [row for _, row in calibrated_rest], options


def assemble(ranked, chunk_map, paths, question, comparison=False, budget=6000, path_format='references', path_budget=0,
             path_budget_mode='additional', evidence_max=8, source_policy='named_first', score_policy='fixed',
             reservation_policy='legacy', subquery_ids=None, diversity_threshold=None):
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
    if score_policy not in ('fixed', 'relative'):
        raise ValueError('invalid_score_policy')
    if reservation_policy not in ('legacy', 'round_robin', 'subquery_balanced'):
        raise ValueError('invalid_reservation_policy')
    if isinstance(evidence_max, bool) or not isinstance(evidence_max, int) or not 1 <= evidence_max <= 40:
        raise ValueError('invalid_evidence_max')
    named=requested_groups(question,chunk_map)
    comparison=comparison or len(named)>=2
    groups=named if comparison and source_policy == 'named_first' else []
    evidence_budget=budget-path_budget if path_budget_mode == 'reserved' else budget
    total_budget=budget+path_budget if path_budget_mode == 'additional' else budget
    if reservation_policy == 'subquery_balanced':
        eff_div = 0.55 if diversity_threshold is None else diversity_threshold
        prioritized, rest, options = reserve_sources_subquery_balanced(
            ranked, chunk_map, groups, evidence_budget, evidence_max=evidence_max,
            score_policy=score_policy, subquery_ids=subquery_ids, diversity_threshold=eff_div)
        used_ids = {row['chunk_id'] for row in prioritized}
        prioritized.extend(rest)
    elif reservation_policy == 'round_robin':
        prioritized,options=reserve_sources_round_robin(ranked,chunk_map,groups,evidence_budget,
            evidence_max=evidence_max,score_policy=score_policy,subquery_ids=subquery_ids)
        used_ids={row['chunk_id'] for row in prioritized}
        prioritized.extend(r for r in ranked if r['chunk_id'] not in used_ids)
        eff_div = diversity_threshold
    else:
        prioritized,options=reserve_sources(ranked,chunk_map,groups,evidence_budget,evidence_max=evidence_max)
        used_ids={row['chunk_id'] for row in prioritized}
        prioritized.extend(r for r in ranked if r['chunk_id'] not in used_ids)
        eff_div = diversity_threshold
    max_per_paper=(max(4, (evidence_max + 1) // 2) if reservation_policy in ('round_robin', 'subquery_balanced') and len(groups) >= 2 else None)
    evidence,used=select_evidence(prioritized,chunk_map,budget=evidence_budget,evidence_max=evidence_max,
        score_policy=score_policy,reserved_ids=used_ids if reservation_policy in ('round_robin', 'subquery_balanced') else None,
        max_per_paper=max_per_paper, diversity_threshold=eff_div)
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
    if score_policy != 'fixed' or reservation_policy != 'legacy':
        detail.update(score_policy=score_policy, reservation_policy=reservation_policy)
    return evidence,selected_paths,detail
