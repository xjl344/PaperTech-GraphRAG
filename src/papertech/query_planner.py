"""Lightweight cloud Query Planner: split complex queries and generate English search keywords."""
import json
import re

from .entity_aliases import GROUPS, mentions
from .query_router_diagnostic import _locate_quote

PLANNER_VERSION = 'cloud-query-planner-v1'
ENGLISH_TOKEN_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.+/\-\s]{0,60}$')

PLANNER_SYSTEM = (
    '你是学术论文检索查询规划器。只分析用户题面，不回答问题，绝不使用外部知识补充论文内容或猜测未提及的方法名。'
    '请判断问题是否包含多个可独立查证的检索目标（例如跨论文方法比较、多对象属性核对、多机制对比），'
    '并为英文论文库的全文检索提取核心英文技术关键词。\n'
    '规则：\n'
    '1. decision 只能是 "no_split"（单一整体检索目标）或 "split"（2至4个独立检索目标）。\n'
    '2. 仅涉及单一论文或单一概念的简单事实题，选择 "no_split"，subqueries 必须为空数组 []。\n'
    '3. 当需要分别查证不同论文/方法/维度时，选择 "split"，输出 2 至 4 条简短、可独立检索的 subqueries；'
    '每条只包含题面已有信息，可消解明确指代，但严禁编造题面未出现的新论文或新方法名。\n'
    '4. english_keywords（顶层和每条子查询）填 2 至 6 个适合在英文论文中做 BM25 检索的英文术语/短语'
    '（可将题面中文技术概念译为常见英文学术术语，例如“停止条件”-> "termination condition", "stopping criteria"；'
    '“微调”-> "fine-tuning"；但不得编造题面未提到的具体数据集或新方法名）。\n'
    '5. quotes 必须是从题面逐字截取的 1 至 4 条连续原文片段，用于支撑你的拆分或判断。\n'
    '只输出严格 JSON 对象，不要 Markdown 包裹：\n'
    '{"decision":"no_split或split","reason":"简短说明","english_keywords":["..."],'
    '"subqueries":[{"id":"SQ01","text":"...","english_keywords":["..."]}],"quotes":["..."]}'
)


def _clean_keywords(values):
    if not isinstance(values, list):
        return []
    seen, out = set(), []
    for item in values:
        if not isinstance(item, str):
            continue
        text = ' '.join(item.strip().split())
        if not text or not ENGLISH_TOKEN_RE.fullmatch(text):
            continue
        key = text.casefold()
        if key not in seen:
            seen.add(key)
            out.append(text)
    return out[:8]


def _invented_corpus_methods(question, texts):
    """Reject subqueries that hallucinate a known corpus method name not mentioned in the question."""
    mentioned = {g['names'][0] for g in GROUPS if any(mentions(question, n) for n in g['names'])}
    invented = []
    combined = '\n'.join(texts)
    for g in GROUPS:
        canonical = g['names'][0]
        if canonical in mentioned:
            continue
        if any(mentions(combined, n) for n in g['names']):
            invented.append(canonical)
    return invented


def validate_plan(question, body):
    """Validate planner JSON strictly; return auditable plan dict or raise ValueError."""
    if not isinstance(body, dict):
        raise ValueError('planner_not_object')
    required = {'decision', 'reason', 'english_keywords', 'subqueries', 'quotes'}
    if not required.issubset(body.keys()):
        raise ValueError('planner_missing_fields')
    decision = body['decision']
    if decision not in ('no_split', 'split'):
        raise ValueError('planner_invalid_decision')
    reason = body.get('reason')
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('planner_invalid_reason')
    quotes = body.get('quotes')
    if not isinstance(quotes, list) or not 1 <= len(quotes) <= 4 or not all(isinstance(q, str) and q.strip() for q in quotes):
        raise ValueError('planner_invalid_quotes')
    spans = [_locate_quote(question, q) for q in quotes]
    top_keywords = _clean_keywords(body.get('english_keywords'))
    raw_sub = body.get('subqueries')
    if not isinstance(raw_sub, list):
        raise ValueError('planner_invalid_subqueries')
    subqueries = []
    if decision == 'no_split':
        if raw_sub:
            raise ValueError('planner_subqueries_on_no_split')
    else:
        if not 2 <= len(raw_sub) <= 4:
            raise ValueError('planner_invalid_subquery_count')
        seen_text = set()
        for idx, item in enumerate(raw_sub, 1):
            if not isinstance(item, dict):
                raise ValueError('planner_subquery_not_object')
            text = ' '.join(str(item.get('text') or '').split())
            if not text or len(text) > 400:
                raise ValueError('planner_subquery_text_invalid')
            key = text.casefold()
            if key in seen_text:
                raise ValueError('planner_duplicate_subquery')
            seen_text.add(key)
            subqueries.append(dict(
                id=f'SQ{idx:02d}',
                text=text,
                english_keywords=_clean_keywords(item.get('english_keywords')),
            ))
        invented = _invented_corpus_methods(question, [s['text'] for s in subqueries])
        if invented:
            raise ValueError('planner_invented_method:' + ','.join(invented))
    return dict(
        planner_version=PLANNER_VERSION,
        decision=decision,
        reason=reason.strip()[:300],
        english_keywords=top_keywords,
        subqueries=subqueries,
        quote_spans=spans,
        fallback=False,
    )


def build_fulltext_query(question, english_keywords=None):
    """Combine English tokens from the question and planner keywords; fall back to raw question."""
    english_in_q = re.findall(r'[A-Za-z][A-Za-z0-9_.\-]*', question)
    tokens, seen = [], set()
    for phrase in list(english_in_q) + list(english_keywords or []):
        for tok in re.findall(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', phrase):
            if len(tok) < 2 and tok.lower() not in ('k',):
                continue
            low = tok.casefold()
            if low not in seen:
                seen.add(low)
                tokens.append(tok)
    if tokens:
        return ' '.join(tokens[:40])
    return question


def merge_multi_query_candidates(per_query_hits, per_channel_quota=8, cap=64):
    """Stable multi-query union retaining discovery provenance and per-query/channel top-N quotas."""
    items, order = {}, []
    for q in per_query_hits:
        qid = q['id']
        for channel in ('fulltext', 'dense'):
            for rank, hit in enumerate(q['channels'].get(channel) or [], 1):
                cid = hit['chunk_id']
                if cid not in items:
                    items[cid] = dict(chunk_id=cid, first_discovery=len(order) + 1,
                                      discoveries=[], found_by=[], sources=[], score=0.0)
                    order.append(cid)
                item = items[cid]
                item['discoveries'].append(dict(query_id=qid, channel=channel, rank=rank, score=hit['score']))
                item['sources'].append(dict(query_id=qid, channel=channel, rank=rank, score=hit['score']))
                item['score'] += 1.0 / (60 + rank)
                if qid not in item['found_by']:
                    item['found_by'].append(qid)
    all_items = [items[cid] for cid in order]
    reserved = [x for x in all_items if any(d['rank'] <= per_channel_quota for d in x['discoveries'])]
    reserved_ids = {x['chunk_id'] for x in reserved}
    def priority(x):
        return (-len(x['found_by']), min(d['rank'] for d in x['discoveries']), -x['score'], x['first_discovery'])
    selected = sorted(reserved, key=priority)[:cap]
    selected_ids = {x['chunk_id'] for x in selected}
    fill = sorted((x for x in all_items if x['chunk_id'] not in selected_ids), key=priority)
    selected.extend(fill[:max(0, cap - len(selected))])
    return selected
