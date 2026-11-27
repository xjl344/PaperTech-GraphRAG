"""Validate response syntax, request whitelist, exact quotes and inline references."""
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


def prompt_evidence(e):
    return {**{k:e[k] for k in ('chunk_id','title','page_start','page_end')},
            'quote_options':quote_options(e['quote'])}


class Citation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_id: str
    quote: str = Field(min_length=12, max_length=2000)


class CitationChoice(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunk_id: str
    quote_id: str = Field(pattern=r'^q[1-9][0-9]*$',max_length=8)


class Generated(BaseModel):
    model_config = ConfigDict(extra='forbid')
    answer: str = Field(min_length=1, max_length=20000)
    citations: list[Citation | CitationChoice] = Field(max_length=24)
    status: Literal['ok','partial','refused']


def validate_answer(raw, evidence):
    result = Generated.model_validate_json(raw)
    allowed = {e['chunk_id']:e for e in evidence}
    found = set(re.findall(r'\[([^\[\]\n]+)\]', result.answer))
    declared = {c.chunk_id for c in result.citations}
    if found != declared or declared - allowed.keys():
        raise ValueError('Unknown, missing or inconsistent inline citations')
    if result.status != 'refused' and not declared:
        raise ValueError('Answer has no citations')
    citations = []
    for citation in result.citations:
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
        citations.append(dict(e, quote=quote))
    return result.answer, citations, result.status
