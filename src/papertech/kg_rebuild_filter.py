"""Offline semantic filters for the independent mechanism-KG pilot.

This module does not call a model and does not write the production graph.  It
re-validates the archived v4 JSON output with conservative, auditable rules.
The filters are intentionally separate from ``kg_rebuild_pilot`` so the old
pilot remains reproducible and its artifact hash is not changed.
"""

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from .corpus import load_corpus
from .kg import locate_quote


VERSION = "kg-rebuild-pilot-14b-v5-filter"
INPUT_VERSION = "kg-rebuild-pilot-14b-v4"
RELATIONS = {
    ("Method", "HAS_COMPONENT", "Component"),
    ("Component", "IMPLEMENTS", "Mechanism"),
    ("Method", "CONTROLLED_BY", "Parameter"),
}

GENERIC_ENTITIES = {
    "a", "an", "approach", "framework", "method", "methods", "model",
    "models", "system", "systems", "component", "components", "t", "d",
    "the approach", "our approach", "the method", "the framework",
}
METHOD_ALIASES = {
    "g-retriever": ("g-retriever", "g retriever"),
    "structgpt": ("structgpt", "struct gpt"),
    "stark": ("stark",),
}
TECHNOLOGY_WORDS = {
    "gat", "gatv2", "gnn", "gnns", "lora", "bm25", "dpr", "ance",
    "sentencebert", "sentence-bert", "bert", "llm", "llms", "gcn",
    "graphsage", "sparql", "pcst", "faiss", "rag", "rags", "t5",
    "qwen", "gpt", "transformer", "transformers",
}
COMPOSITION_RE = re.compile(
    r"\b(?:compris(?:e|es|ing)|consist(?:s|ed|ing)?\s+of|include(?:s|d|ing)?|"
    r"contain(?:s|ed|ing)?|composed\s+of|made\s+up\s+of|(?:main\s+)?steps?|"
    r"stages?|modules?|components?|we\s+(?:devise|use|employ|design|introduce)|"
    r"our\s+(?:method|framework)\s+(?:uses|employs|contains|includes))\b", re.I,
)
PARAMETER_RE = re.compile(
    r"^(?:top[- ]?k|k|n|m|d|h|w|l|r|p|q|lambda|\u03bb|theta|\u03b8|"
    r"temperature|depth|beam(?:[- ]?size)?|window(?:[- ]?size)?|threshold|"
    r"number\s+of\s+\w+|\w+[- ]?parameter)\b|\b(?:top[- ]?k|k\s*=|"
    r"lambda|\u03bb|theta|\u03b8|temperature|threshold)\b", re.I,
)
PRIOR_RE = re.compile(
    r"\b(?:prior|previous|existing|related|baseline|other)\s+(?:stud(?:y|ies)|"
    r"work|method(?:s)?|approach(?:es)?|framework(?:s)?|model(?:s)?)\b|"
    r"\b(?:prior\s+studies|previous\s+work|related\s+work|existing\s+works?)\b",
    re.I,
)
FUNCTION_RE = re.compile(
    r"\b(?:extract|select|get|initialize|fill|filter|answer|search|retrieve|"
    r"finish|expand|think|intersection)\w*\s*\([^\n)]{0,100}\)|"
    r"\b(?:str|t|d)\s*(?:\)|:|=)|\b(?:select|answer|expand)\s+\w+\s*\?",
    re.I,
)
MARKER_RE = re.compile(r"^[\s\u2013\u2014\u2212+\-\u0394\u2206(\[]|^w\s*/?\s*o\b", re.I)


def _norm(value):
    return " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())


def _first_lines(text, count=3):
    return [line.strip() for line in str(text).splitlines() if line.strip()][:count]


def _section_heading_is_reliable(chunk):
    """The parser's section label is advisory unless the chunk contains it."""
    section = _norm(chunk.get("section", ""))
    if not section or section == "unidentified":
        return False
    section = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", section)
    for line in _first_lines(chunk.get("text", ""), 4):
        candidate = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", _norm(line))
        if candidate == section or candidate.startswith(section + " "):
            return True
    return False


def classify_chunk(chunk):
    """Return a content type plus reasons; uncertain chunks remain body."""
    text = str(chunk.get("text", ""))
    lines = _first_lines(text, 8)
    first = lines[0] if lines else ""
    section = _norm(chunk.get("section", ""))
    if chunk.get("content_kind") == "references" or section in {"references", "bibliography"}:
        return {"kind": "references", "reasons": ["parser_references"]}

    # Captions are excluded only when the whole block is caption-like. A PDF
    # block can straddle a caption and the following paragraph, so retain it as
    # body_mixed rather than deleting a valid method passage.
    caption = re.match(r"^(?:figure|fig\.?|table|tab\.?)\s*\d+[.:)]?\s*", first, re.I)
    if caption:
        rest = text[len(first):].strip()
        body_cues = re.search(r"\b(?:this paragraph|we propose|the proposed|in this section|we introduce|our method)\b", rest, re.I)
        if (len(rest) < 500 and not body_cues) or len(_first_lines(rest, 8)) <= 4 and not body_cues:
            kind = "figure_caption" if caption.group(0).casefold().startswith(("figure", "fig")) else "table"
            return {"kind": kind, "reasons": ["caption_prefix"]}
        return {"kind": "body_mixed", "reasons": ["caption_and_body_same_block"]}

    # Tables commonly arrive as short, repeated rows without a caption. Use
    # several signals together to avoid classifying ordinary prose with years.
    short_rows = [line for line in text.splitlines() if line.strip()]
    numeric_rows = sum(bool(re.search(r"\d", line)) for line in short_rows)
    if (len(short_rows) >= 5 and len(short_rows) <= 45 and
            sum(len(line.split()) <= 12 for line in short_rows) / len(short_rows) >= .72 and
            numeric_rows / len(short_rows) >= .35 and
            (re.search(r"\bw/o\b|\bwithout\b|\baccuracy\b|\bhit@\d|\bmr(r|r)\b", text, re.I))):
        return {"kind": "table", "reasons": ["short_numeric_rows"]}

    # Code/example blocks are not method-component evidence. Keep normal
    # method prose containing one equation as body.
    code_signals = len(re.findall(r"\b(?:def|function|initialize|select_entities|get_edges)\s*\(?", text, re.I))
    explicit_examples = bool(re.search(r"(?:>>>\s*(?:input|output)|\bcode\s+example\b|\bpseudocode\b|\bAlgorithm\s+\d+)", text, re.I))
    prompt_example = bool(re.search(r"\bPrompt\s+for\s+STARK[- ](?:AMAZON|MAG|PRIME)\b", text, re.I))
    if code_signals >= 3 or explicit_examples or prompt_example:
        return {"kind": "example", "reasons": ["code_or_pseudocode_signals"]}

    return {"kind": "body", "reasons": []}


def _paper_role(paper):
    title = _norm(paper.get("title", ""))
    if "benchmark" in title or re.search(r"\bstark\b", title):
        return "benchmark"
    return "method"


def _method_aliases(paper):
    title = _norm(paper.get("title", ""))
    for key, aliases in METHOD_ALIASES.items():
        if key in title:
            if key == "structgpt":
                return (*aliases, "irr", "iterative reading-then-reasoning")
            return aliases
    return tuple()


def _is_method_anchored(candidate, quote, paper):
    subject = _norm(candidate.get("subject", ""))
    aliases = _method_aliases(paper)
    if not aliases:
        return False
    return any(alias in subject or alias in _norm(quote) for alias in aliases)


def _is_named_technology(value):
    norm = _norm(value)
    if norm in TECHNOLOGY_WORDS:
        return True
    # Acronyms and CamelCase names are useful conservative indicators; a long
    # English action phrase is not.
    raw = str(value).strip()
    return bool(re.search(r"\b[A-Z]{2,}[0-9]*\b", raw) or re.search(r"[a-z][A-Z][A-Za-z0-9]+", raw))


def _claim_table_or_template(candidate, quote):
    value = f"{candidate.get('object', '')} {quote}"
    rows = [line.strip() for line in str(quote).splitlines() if line.strip()]
    table_like = (len(rows) >= 4 and
                  sum(len(line.split()) <= 14 for line in rows) / len(rows) >= .7 and
                  sum(bool(re.search(r"\d", line)) for line in rows) / len(rows) >= .35)
    return bool(table_like or FUNCTION_RE.search(value) or re.search(
        # Bracketed citation numbers such as [43] are normal evidence.  Only
        # retain placeholders/labels that look like a query template.
        r"\bmetapath\b|\?\s*\[[^\]]+\]|\[(?:carrier|target|transporter|"
        r"indication|contraindication|expression\s+(?:present|absent)|"
        r"interacts\s+with|parent-child|side\s+effect)\]|"
        r"\b(?:correct|incorrect|hallucination|false positive)\b",
        value, re.I,
    ))


def _semantic_reason(candidate, quote, chunk, paper, classification):
    subject_type = candidate.get("subject_type")
    predicate = candidate.get("predicate")
    object_type = candidate.get("object_type")
    subject = str(candidate.get("subject", "")).strip()
    obj = str(candidate.get("object", "")).strip()
    if (subject_type, predicate, object_type) not in RELATIONS:
        return "relation_signature_not_allowed"
    if not all(isinstance(candidate.get(k), str) and candidate[k].strip() for k in ("subject", "object", "evidence_quote")):
        return "empty_field"
    if candidate.get("claim_kind") != "author_assertion":
        return "system_inference_rejected"
    matched = locate_quote(chunk["text"], candidate["evidence_quote"])
    if matched is None:
        return "evidence_quote_not_in_chunk"
    if _paper_role(paper) == "benchmark":
        return "benchmark_paper_not_applicable"
    if MARKER_RE.search(subject) or MARKER_RE.search(obj):
        return "entity_marker_or_delta"
    if _norm(subject) in GENERIC_ENTITIES or _norm(obj) in GENERIC_ENTITIES:
        return "generic_entity"
    if _norm(subject) == _norm(obj):
        return "self_reference"
    if classification["kind"] in {"references", "table", "figure_caption", "example"}:
        return f"chunk_kind_excluded:{classification['kind']}"
    if _claim_table_or_template(candidate, matched):
        return "table_or_template_example"

    reliable_related = (_norm(chunk.get("section", "")).startswith("related work") and
                        _section_heading_is_reliable(chunk))
    if reliable_related and predicate in {"HAS_COMPONENT", "IMPLEMENTS"}:
        return "related_work_component_excluded"
    if predicate in {"HAS_COMPONENT", "IMPLEMENTS"} and PRIOR_RE.search(matched):
        return "prior_work_context"

    if predicate in {"HAS_COMPONENT", "CONTROLLED_BY"} and _norm(subject) not in GENERIC_ENTITIES and not _is_method_anchored(candidate, matched, paper):
        return "subject_not_method_anchored"

    if predicate == "HAS_COMPONENT":
        if re.search(r"\b(?:w\s*/?\s*o|without|ablation)\b", matched, re.I):
            return "ablation_does_not_establish_component"
        if not COMPOSITION_RE.search(matched):
            return "component_not_explicitly_listed"
        if FUNCTION_RE.search(f"{subject} {obj} {matched}"):
            return "function_example_not_component"
    elif predicate == "IMPLEMENTS":
        if subject_type != "Component":
            return "implementation_object_not_named_technology"
        mechanism_words = {"interface", "interfaces", "invocation", "function", "functions",
                           "query", "queries", "filtering", "linearization", "generation"}
        simple_mechanism = _norm(obj) in mechanism_words or len(_norm(obj).split()) <= 2
        if not (_is_named_technology(obj) or simple_mechanism):
            return "implementation_object_not_named_technology"
        if re.search(r"\b(?:selective|relevant|accurate|efficient|reading|reasoning|collecting|"
                     r"inferring|finding|dimension|transformation|processing)\b", _norm(obj)):
            return "implementation_object_is_action"
    elif predicate == "CONTROLLED_BY":
        if not PARAMETER_RE.search(obj):
            return "control_object_not_parameter"
        if not re.search(r"\b(?:set|parameter|control|controlled|top[- ]?k|denot|hyperparameter|vary|tune|number)\b|=", matched, re.I):
            return "control_quote_not_behavioral"
    return None


def _quote_span(text, quote):
    matched = locate_quote(text, quote)
    if matched is None:
        return None, None, None
    start = text.find(matched)
    return matched, start, start + len(matched)


def validate_candidate(candidate, chunk, paper):
    """Validate one archived candidate and return (claim, rejection)."""
    classification = classify_chunk(chunk)
    reason = _semantic_reason(candidate, candidate.get("evidence_quote", ""), chunk, paper, classification)
    if reason:
        return None, {"reason": reason, "candidate": deepcopy(candidate), "chunk_kind": classification["kind"], "chunk_reasons": classification["reasons"]}
    matched, start, end = _quote_span(chunk["text"], candidate["evidence_quote"])
    claim = deepcopy(candidate)
    claim.update({
        "graph_version": VERSION,
        "input_graph_version": INPUT_VERSION,
        "paper_id": chunk["paper_id"],
        "paper_title": paper["title"],
        "chunk_id": chunk["chunk_id"],
        "evidence_quote": matched,
        "quote_match_method": "exact" if candidate["evidence_quote"] in chunk["text"] else "whitespace_normalized",
        "quote_start": start,
        "quote_end": end,
        "source_spans": deepcopy(chunk.get("source_spans", [])),
        "page_start": chunk["page_start"],
        "page_end": chunk["page_end"],
        "section": chunk.get("section"),
        "content_classification": classify_chunk(chunk),
        "review_status": "pending",
    })
    claim["claim_id"] = hashlib.sha256(json.dumps(
        [VERSION, chunk["paper_id"], chunk["chunk_id"], claim.get("subject_type"),
         _norm(claim.get("subject")), claim.get("predicate"), claim.get("object_type"),
         _norm(claim.get("object")), matched], ensure_ascii=False, sort_keys=True,
    ).encode()).hexdigest()
    return claim, None


def filter_archived(root, input_run):
    """Revalidate the archived checkpoint and write a versioned report."""
    root = Path(root)
    checkpoint = Path(input_run) / "checkpoint.json"
    archived = json.loads(checkpoint.read_text(encoding="utf8"))
    _, papers, chunks = load_corpus(root)
    paper_map = {p["paper_id"]: p for p in papers}
    chunk_map = {c["chunk_id"]: c for c in chunks}
    results = []
    claims = []
    rejected = []
    for row in archived["results"]:
        chunk = chunk_map[row["chunk_id"]]
        paper = paper_map[row["paper_id"]]
        row_result = {"chunk_id": row["chunk_id"], "paper_id": row["paper_id"], "ordinal": row.get("ordinal"),
                      "content_classification": classify_chunk(chunk), "accepted": [], "rejected": []}
        # ``relations`` is the v4 validator's 79-item accepted set.  The
        # archived parsed_output also contains 31 candidates already rejected
        # for malformed quotes/signatures; those remain reported by v4 and are
        # not counted as fresh semantic candidates here.
        for candidate in row.get("relations", []):
            claim, failure = validate_candidate(candidate, chunk, paper)
            if claim:
                row_result["accepted"].append(claim)
                claims.append(claim)
            else:
                row_result["rejected"].append(failure)
                rejected.append(dict(failure, chunk_id=chunk["chunk_id"], paper_id=chunk["paper_id"], ordinal=row.get("ordinal")))
        results.append(row_result)
    by_paper = {}
    selected_papers = {row["paper_id"] for row in archived["results"]}
    for p in papers:
        if p["paper_id"] not in selected_papers:
            continue
        rows = [r for r in results if r["paper_id"] == p["paper_id"]]
        pc = [c for r in rows for c in r["accepted"]]
        pr = [x for r in rows for x in r["rejected"]]
        by_paper[p["paper_id"]] = {"title": p["title"], "chunks": len(rows), "chunks_with_claims": sum(bool(r["accepted"]) for r in rows),
                                    "accepted": len(pc), "rejected": len(pr), "content_kinds": dict(Counter(r["content_classification"]["kind"] for r in rows))}
    summary = {"status": "completed", "input_run": str(checkpoint.relative_to(root)), "input_claim_candidates": sum(len(r.get("relations", [])) for r in archived["results"]),
               "input_original_rejected": sum(len(r.get("rejected", [])) for r in archived["results"]),
               "accepted": len(claims), "rejected": len(rejected), "accepted_by_predicate": dict(Counter(c["predicate"] for c in claims)),
               "accepted_by_paper": dict(Counter(c["paper_id"] for c in claims)), "rejected_by_reason": dict(Counter(x["reason"] for x in rejected)),
               "by_paper": by_paper, "model_calls": 0, "source": "archived_parsed_output"}
    payload = {"version": VERSION, "input_version": INPUT_VERSION, "input_checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
               "summary": summary, "results": results, "claims": claims, "rejected": rejected}
    out = root / "artifacts/reports/stage-3" / VERSION
    out.mkdir(parents=True, exist_ok=True)
    (out / "filter-report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    lines = [
        f"# {VERSION}", "", "离线重验 v4 已接受的 79 条 Claim；没有重新调用模型。旧 v4 与生产图谱均未修改。", "",
        f"- 输入：`{summary['input_run']}`", f"- 候选：{summary['input_claim_candidates']} 条；v4 预先拒绝 {summary['input_original_rejected']} 条（保持原记录）",
        f"- 新规则接受：{summary['accepted']} 条；拒绝：{summary['rejected']} 条", "- 模型调用：0", "",
        "## 按论文汇总", "", "| 论文 | 输入候选 | 新规则接受 | 新规则拒绝 |", "|---|---:|---:|---:|",
    ]
    for info in by_paper.values():
        lines.append(f"| {info['title']} | {info['accepted'] + info['rejected']} | {info['accepted']} | {info['rejected']} |")
    lines.extend(["", "## 拒绝原因", ""])
    for reason, count in Counter(x["reason"] for x in rejected).most_common():
        lines.append(f"- `{reason}`：{count}")
    lines.extend(["", "## 逐条结果", ""])
    for row in results:
        if not row["accepted"] and not row["rejected"]:
            continue
        paper_title = paper_map[row["paper_id"]]["title"]
        lines.extend([f"### {paper_title} · 块 {row['ordinal']} · `{row['content_classification']['kind']}`", ""])
        for claim in row["accepted"]:
            lines.append(f"- **保留** `{claim['subject']} --{claim['predicate']}--> {claim['object']}`；页 {claim['page_start']}；引文：{claim['evidence_quote'].replace(chr(10), ' ')}")
        for item in row["rejected"]:
            candidate = item["candidate"]
            lines.append(f"- **拒绝：`{item['reason']}`** `{candidate.get('subject')} --{candidate.get('predicate')}--> {candidate.get('object')}`；引文：{candidate.get('evidence_quote', '').replace(chr(10), ' ')}")
        lines.append("")
    lines.extend(["", "## 解释边界", "", "这些是确定性规则对归档输出的重验结果，不是第二轮人工准确率。引用存在只说明可溯源，不代表语义真实；进入下一阶段前仍需人工复核保留项。STaRK 被标为基准论文，不以方法组件图谱作为抽取目标。", ""])
    (out / "filter-review.md").write_text("\n".join(lines), encoding="utf8")
    return out, payload
