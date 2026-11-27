"""Budgeted comparison coverage and paths grounded in the selected source text."""
import json
from .entity_aliases import GROUPS, mentions
from .retrieval import select_evidence


def requested_groups(question, chunk_map):
    groups=[]
    for group in GROUPS:
        if any(mentions(question,name) for name in group['names']):
            source=chunk_map.get(group['source_chunk'])
            if source:
                groups.append(dict(name=group['names'][0],paper_id=source['paper_id']))
    return groups


def assemble(ranked, chunk_map, paths, question, comparison=False, budget=6000):
    groups=requested_groups(question,chunk_map) if comparison else []
    prioritized=[]; used_ids=set()
    # Reserve a high-ranked source from each explicitly requested paper before filling.
    for group in groups:
        for row in ranked:
            if chunk_map[row['chunk_id']]['paper_id']==group['paper_id'] and row.get('rerank_score',1)>=.05:
                prioritized.append(row); used_ids.add(row['chunk_id']); break
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
    gaps=[]
    if missing:
        gaps.append('缺少以下方法的独立论文证据：'+', '.join(missing))
    if comparison:
        gaps.append('检索到同一数据集不代表实验条件可比；仅按原文核对数据划分、底座模型、指标和协议，缺项须说明。')
    return evidence,selected_paths,dict(context_bytes=used+graph_bytes,evidence_bytes=used,graph_context_bytes=graph_bytes,
                                     comparison_groups=groups,missing_comparison_groups=missing,limitations=gaps)
