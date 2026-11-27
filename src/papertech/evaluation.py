"""Evidence-unit scoring; alternatives are OR, required units are AND."""


def criterion_source_coverage(case, evidence_ids, units):
    """Post-execution source availability, never a semantic correctness score."""
    selected = set(evidence_ids)
    records = []
    for criterion in case.get('assessment', {}).get('criteria', []):
        required = criterion['unit_ids']
        matches = {key: sorted(selected & set(units[key]['known_support_chunks'])) for key in required}
        records.append(dict(criterion_id=criterion['id'], requirement=criterion['requirement'],
            selected_matches_by_unit=matches, missing_units=[key for key in required if not matches[key]],
            required_sources_available=all(matches.values()) if required else None,
            semantic_status='not_reviewed', semantic_score=None))
    return records


def support_metrics(ranked_ids,evidence_ids,units):
    if not units:
        return dict(recall5=None,recall8=None,mrr40=None,evidence_coverage=None,all_units=None)
    pools=[set(u['known_support_chunks']) for u in units]
    def coverage(ids):return sum(bool(set(ids)&pool) for pool in pools)/len(pools)
    first=next((i for i,cid in enumerate(ranked_ids[:40],1) if any(cid in pool for pool in pools)),None)
    selected=coverage(evidence_ids)
    return dict(recall5=coverage(ranked_ids[:5]),recall8=coverage(ranked_ids[:8]),
                mrr40=1/first if first else 0,evidence_coverage=selected,all_units=selected==1)


def linear_quantile(values,q):
    if not values:return None
    values=sorted(values)
    position=(len(values)-1)*q
    lower=int(position); upper=min(lower+1,len(values)-1)
    return values[lower]+(position-lower)*(values[upper]-values[lower])
