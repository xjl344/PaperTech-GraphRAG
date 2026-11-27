"""Validate response syntax, request whitelist, exact quotes and inline references."""
import json
import re
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


def quote_options(text):
    """Lossless source slices: the model selects IDs instead of retyping PDF text."""
    parts=[]; start=0
    while start<len(text):
        end=min(len(text),start+900)
        if end<len(text):
            boundary=max(text.rfind('. ',start+300,end),text.rfind('\n',start+300,end))
            if boundary>start:
                end=boundary+1
        piece=text[start:end].strip()
        if len(piece)>=12:
            parts.append(piece)
        elif piece and parts:
            # Extend through the original whitespace; never reconstruct a quotation.
            prior=text.rfind(parts[-1],0,start)
            parts[-1]=text[prior:end].strip()
        start=end
    return [dict(quote_id='q'+str(i+1),quote=p) for i,p in enumerate(parts)]


def prompt_evidence(e, eid=None, include_chunk_id=False):
    if eid is not None:
        item = {'eid': eid}
        if include_chunk_id:
            item['chunk_id'] = e['chunk_id']
        for k in ('title', 'page_start', 'page_end'):
            item[k] = e[k]
        item['quote_options'] = quote_options(e['quote'])
        return item
    return {**{k:e[k] for k in ('chunk_id','title','page_start','page_end')},
            'quote_options':quote_options(e['quote'])}


def evidence_aliases(evidence):
    eid_to_evidence = {f'E{index}': e for index, e in enumerate(evidence, 1)}
    cid_to_eid = {e['chunk_id']: f'E{index}' for index, e in enumerate(evidence, 1)}
    return eid_to_evidence, cid_to_eid


class Citation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_id: str
    quote: str = Field(min_length=12, max_length=2000)


class CitationChoice(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_id: str
    quote_id: str = Field(pattern=r'^q[1-9][0-9]*$',max_length=8)


class CitationChoiceV2(BaseModel):
    model_config = ConfigDict(extra='forbid')
    eid: str = Field(pattern=r'^E[1-9][0-9]*$', max_length=8)
    quote_id: str = Field(pattern=r'^q[1-9][0-9]*$', max_length=8)


class PremiseCheck(BaseModel):
    model_config = ConfigDict(extra='forbid')
    premise: str = Field(min_length=1, max_length=500)
    supported: bool
    evidence_eids: list[str] = Field(default_factory=list, max_length=12)
    note: str = Field(default='', max_length=500)


class Generated(BaseModel):
    model_config = ConfigDict(extra='forbid')
    answer: str = Field(min_length=1, max_length=20000)
    citations: list[CitationChoiceV2 | CitationChoice | Citation] | None = Field(default=None, max_length=48)
    status: Literal['ok','partial','refused'] | None = None
    premise_check: list[PremiseCheck] | None = Field(default=None, max_length=16)


_EID_TOKEN = re.compile(r'^E[1-9][0-9]*$')
_EID_QUOTE_TOKEN = re.compile(r'^(E[1-9][0-9]*):(q[1-9][0-9]*)$')
_QUOTE_TOKEN = re.compile(r'^q[1-9][0-9]*$')
_CHUNK_TOKEN = re.compile(r'^chunk_[A-Za-z0-9_-]+$')


def _extract_inline_citations(answer, allowed, eid_map):
    """Parse [E1:q2], [E1:q2, E3:q1], [E1], [E1, E2], [chunk_xxx] without failing on math/paper brackets.

    Returns (found_chunk_ids, inline_pairs) where inline_pairs are ordered unique (eid, quote_id) pairs
    explicitly written in source-choice-v3 inline form.
    """
    found = set()
    inline_pairs = []
    seen_pairs = set()
    for inner in re.findall(r'\[([^\[\]\n]+)\]', answer):
        parts = [part.strip() for part in re.split(r'[,，]', inner) if part.strip()]
        if not parts:
            continue
        is_id = [bool(_EID_QUOTE_TOKEN.fullmatch(p) or _EID_TOKEN.fullmatch(p) or _CHUNK_TOKEN.fullmatch(p) or p in allowed) for p in parts]
        if not any(is_id):
            # Ordinary paper brackets such as [Pe; Xe], [12], or prose labels are not citations.
            continue
        is_valid_slot = [ok or bool(_QUOTE_TOKEN.fullmatch(p)) for ok, p in zip(is_id, parts)]
        if not all(is_valid_slot):
            raise ValueError('Malformed mixed citation bracket: ' + inner)
        last_eid = None
        for token, is_entity_id in zip(parts, is_id):
            if not is_entity_id:
                # Attach bare q2 qualifier in [E2, q2] to its preceding E2 if present.
                if last_eid and (last_eid, token) not in seen_pairs:
                    seen_pairs.add((last_eid, token))
                    inline_pairs.append((last_eid, token))
                continue
            m_pair = _EID_QUOTE_TOKEN.fullmatch(token)
            if m_pair:
                eid, qid = m_pair.group(1), m_pair.group(2)
                if eid not in eid_map:
                    raise ValueError('Unknown inline citation eid: ' + eid)
                found.add(eid_map[eid]['chunk_id'])
                last_eid = eid
                if (eid, qid) not in seen_pairs:
                    seen_pairs.add((eid, qid))
                    inline_pairs.append((eid, qid))
            elif _EID_TOKEN.fullmatch(token):
                if token not in eid_map:
                    raise ValueError('Unknown inline citation eid: ' + token)
                found.add(eid_map[token]['chunk_id'])
                last_eid = token
            elif token in allowed:
                found.add(token)
                last_eid = None
            else:
                raise ValueError('Unknown inline citation chunk_id: ' + token)
    return found, inline_pairs


def validate_answer_with_meta(raw, evidence):
    parsed_obj = json.loads(raw) if isinstance(raw, str) else raw
    if isinstance(parsed_obj, dict):
        # Strip benign underscore-prefixed model meta notes (e.g. "_note"), while still forbidding unknown schema fields.
        parsed_obj = {k: v for k, v in parsed_obj.items() if not (isinstance(k, str) and k.startswith('_'))}
    result = Generated.model_validate(parsed_obj)
    allowed = {e['chunk_id']:e for e in evidence}
    eid_map, cid_to_eid = evidence_aliases(evidence)
    found, inline_pairs = _extract_inline_citations(result.answer, allowed, eid_map)

    # source-choice-v3 single-point inline mode: derive citations directly from verified [E1:q2] markers
    # (also tolerate models emitting an empty "citations": [] alongside valid [E#:q#] inline citations).
    if result.citations is None or (result.citations == [] and inline_pairs):
        status = result.status
        if status is None:
            if not inline_pairs:
                if result.premise_check and any(not c.supported for c in result.premise_check):
                    status = 'refused'
                else:
                    raise ValueError('Answer missing status and inline [E#:q#] citations')
            else:
                status = 'ok'
        if status != 'refused' and not inline_pairs:
            raise ValueError('Answer has no inline [E#:q#] citations')
        if found and {eid_map[eid]['chunk_id'] for eid, _ in inline_pairs} != found:
            raise ValueError('Inline citation missing quote_id qualifier')
        citations = []
        for eid, qid in inline_pairs:
            e = eid_map[eid]
            options = {p['quote_id']: p['quote'] for p in quote_options(e['quote'])}
            if qid not in options:
                raise ValueError('Unknown quotation choice: ' + qid)
            quote = options[qid]
            if quote not in e['quote']:
                raise ValueError('Quote is not an exact substring of supplied evidence')
            citations.append(dict(e, eid=eid, quote_id=qid, quote=quote))
        checks = [c.model_dump() for c in result.premise_check] if result.premise_check is not None else None
        return result.answer, citations, status, checks

    # Legacy v1/v2 mode: explicit citations list must exactly match inline citations.
    if result.status is None:
        if result.premise_check is not None and result.citations:
            status = 'ok'
        else:
            raise ValueError('Missing required status field')
    else:
        status = result.status
    declared = set()
    for citation in result.citations:
        if isinstance(citation, CitationChoiceV2):
            if citation.eid not in eid_map:
                raise ValueError('Unknown citation eid')
            declared.add(eid_map[citation.eid]['chunk_id'])
        else:
            if citation.chunk_id not in allowed:
                raise ValueError('Unknown citation chunk_id')
            declared.add(citation.chunk_id)
    if found != declared or declared - allowed.keys():
        raise ValueError('Unknown, missing or inconsistent inline citations')
    if status != 'refused' and not declared:
        raise ValueError('Answer has no citations')
    citations = []
    for citation in result.citations:
        if isinstance(citation, CitationChoiceV2):
            e = eid_map[citation.eid]
            options = {p['quote_id']:p['quote'] for p in quote_options(e['quote'])}
            if citation.quote_id not in options:
                raise ValueError('Unknown quotation choice')
            quote = options[citation.quote_id]
        else:
            e = allowed[citation.chunk_id]
            if isinstance(citation,CitationChoice):
                options={p['quote_id']:p['quote'] for p in quote_options(e['quote'])}
                if citation.quote_id not in options:
                    raise ValueError('Unknown quotation choice')
                quote=options[citation.quote_id]
            else:
                quote=citation.quote
        if quote not in e['quote']:
            raise ValueError('Quote is not an exact substring of supplied evidence')
        citations.append(dict(e, eid=cid_to_eid[e['chunk_id']], quote=quote))
    checks = [c.model_dump() for c in result.premise_check] if result.premise_check is not None else None
    return result.answer, citations, status, checks


def validate_answer(raw, evidence):
    answer, citations, status, _ = validate_answer_with_meta(raw, evidence)
    return answer, citations, status
