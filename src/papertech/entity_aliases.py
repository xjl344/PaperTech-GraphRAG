"""Reviewed query aliases loaded from data; preserve original entity IDs and claim endpoints."""
import json
from pathlib import Path
import re
import unicodedata

ALIAS_VERSION = 'query-alias-v3'
_DEFAULT_ALIAS_FILE = Path(__file__).resolve().parents[2] / 'artifacts/exports/pilot-v1/entity-aliases.json'
_FALLBACK_GROUPS = [
    dict(names=['ToG', 'Think-on-Graph'], source_chunk='chunk_e09b5a88c34014513aad6c0d6121f790',
         quote='Think-on-Graph (ToG)'),
    dict(names=['ToG-2', 'Think-on-Graph 2.0'], source_chunk='chunk_9b63637ef18ed2d67ff105ef55092df3',
         quote='Think-on-Graph 2.0 (ToG-2)'),
    dict(names=['HippoRAG'], source_chunk='chunk_8e26b737d927e9880327e7178bfba648', quote='HippoRAG'),
    dict(names=['RoG', 'Reasoning on Graphs'], source_chunk='chunk_58e7ae48fdb49536bc066f6e74ccd2a0',
         quote='reasoning on graphs (RoG)'),
    dict(names=['KGP', 'Knowledge Graph Prompting for Multi-Document Question Answering'],
         source_chunk='chunk_b959214e888053dae53b16a5259d7ea9', quote='Graph Prompting (KGP)'),
    dict(names=['CuriousLLM'], source_chunk='chunk_8e57fb05b711b97bf1a88bf918fa57a5', quote='CuriousLLM'),
    dict(names=['StructGPT'], source_chunk='chunk_a7df67e7fd088df02cfb3cdf0e560925', quote='StructGPT'),
    dict(names=['LPKG', 'Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs'],
         source_chunk='chunk_8b71ee4b07d7db1c8c01c63db126733b', quote='https://github.com/zjukg/LPKG'),
    dict(names=['G-Retriever'], source_chunk='chunk_a001225c0afa46199e503f9e9f8bd803', quote='G-Retriever'),
    dict(names=['Tree-of-Traversals'], source_chunk='chunk_20ad4ca6811d52ca011e181dadb57ba4', quote='Tree-of-Traversals'),
    dict(names=['KG-GPT'], source_chunk='chunk_07c5e4db08e2494c1b3712c0d378b9cd', quote='KG-GPT'),
    dict(names=['MindMap'], source_chunk='chunk_edd332a9f7b5542fc6616a55c0486cec', quote='MindMap'),
    dict(names=['STaRK'], source_chunk='chunk_8de1e06d1827ae3f8e7d83e7e454573b', quote='STARK'),
    dict(names=['Unifying Large Language Models and Knowledge Graphs: A Roadmap'],
         source_chunk='chunk_e39fbc3c8ed02ca68ec4ab316c71905b', quote='A Roadmap'),
    dict(names=['ToG-R'], source_group='ToG', source_chunk='chunk_7ac089f731dde3a5b09b48a00fc48587', quote='relation-based ToG (ToG-R)'),
]


def load_alias_groups(path=None):
    """Load reviewed alias groups from a versioned JSON file, with safe fallback."""
    target = Path(path) if path is not None else _DEFAULT_ALIAS_FILE
    if target.exists():
        data = json.loads(target.read_text(encoding='utf-8'))
        groups = data.get('groups')
        if isinstance(groups, list) and groups:
            return groups
    return list(_FALLBACK_GROUPS)


def discover_aliases_from_corpus(papers, chunks, reviewed=None):
    """Data-driven alias discovery for scalable corpora (>14 papers), merged with reviewed overrides."""
    by_paper = {}
    for chunk in chunks:
        by_paper.setdefault(chunk['paper_id'], []).append(chunk)
    reviewed_list = list(reviewed) if reviewed is not None else load_alias_groups()
    covered_chunks = {g['source_chunk'] for g in reviewed_list if g.get('source_chunk')}
    discovered = list(reviewed_list)
    for paper in papers:
        pchunks = sorted(by_paper.get(paper['paper_id'], []), key=lambda c: c.get('ordinal', 0))
        if not pchunks or any(c['chunk_id'] in covered_chunks for c in pchunks):
            continue
        first = pchunks[0]
        title = str(paper.get('title') or '').strip()
        names = []
        colon = re.match(r'^([A-Za-z][A-Za-z0-9\-]{1,24})\s*:', title)
        if colon:
            names.append(colon.group(1))
        paren = re.search(r'\(([A-Za-z][A-Za-z0-9\-]{1,20})\)', first.get('text', '')[:1200])
        if paren and paren.group(1) not in names:
            names.append(paren.group(1))
        if title and title not in names:
            names.append(title)
        if names:
            discovered.append(dict(names=names, source_chunk=first['chunk_id'], quote=names[0], auto_discovered=True))
    return discovered


GROUPS = load_alias_groups()


def normalized(value):
    value = unicodedata.normalize('NFKC', value).casefold()
    value = value.translate(str.maketrans({'–': '-', '—': '-', '‐': '-', '‑': '-'}))
    return ' '.join(value.split())


def mentions(question, name):
    # Chinese characters may directly surround an English method name. Avoid
    # matching inside English identifiers or confusing ToG with ToG-2/ToG-R.
    suffix=r'(?![a-z0-9_-])'
    if normalized(name)=='think-on-graph':
        suffix+=r'(?!\s*2\.0)'
    return re.search(r'(?<![a-z0-9_-])' + re.escape(normalized(name)) + suffix, normalized(question)) is not None


def source_groups(question, chunk_map):
    """Resolve explicitly named papers using the corpus catalog, never gold."""
    groups = {}
    for group in GROUPS:
        if not any(mentions(question, name) for name in group['names']):
            continue
        source = chunk_map.get(group['source_chunk'])
        if source:
            paper_id = source['paper_id']
            if paper_id not in groups:
                groups[paper_id] = dict(name=group['names'][0], paper_id=paper_id,
                    requested_names=[group['names'][0]])
            elif group['names'][0] not in groups[paper_id]['requested_names']:
                groups[paper_id]['requested_names'].append(group['names'][0])
    return list(groups.values())


def is_comparison(question):
    named_papers = {group.get('source_group', group['names'][0]) for group in GROUPS
        if any(mentions(question, name) for name in group['names'])}
    # Variants in one paper count once. Multi-source questions need no magic verb.
    return len(named_papers) >= 2 or any(word in question.casefold() for word in ('比较', '对比', 'compare', 'versus'))


def canonical(name, entity_type='Method'):
    value = normalized(name)
    if entity_type == 'Method':
        for group in GROUPS:
            if value in {normalized(n) for n in group['names']}:
                return normalized(group['names'][0])
    return value


def query_matches(question, entities):
    selected = []
    for entity in entities:
        names = [entity['name']]
        if entity['type'] == 'Method':
            for group in GROUPS:
                if normalized(entity['name']) in {normalized(n) for n in group['names']}:
                    names = group['names']
        if any(mentions(question, name) for name in names):
            selected.append(dict(entity, canonical=canonical(entity['name'], entity['type'])))
    return sorted(selected, key=lambda e:(e['canonical'], e['id']))[:40]


SUBQUERY_VERSION = 'question-spans-v1'


def _question_offsets(question):
    """Normalize for alias lookup while mapping matches back to original offsets."""
    chars, offsets = [], []
    for index, char in enumerate(question):
        for value in normalized(char):
            chars.append(value)
            offsets.append(index)
        if char.isspace():
            chars.append(' ')
            offsets.append(index)
    return ''.join(chars), offsets


def method_spans(question):
    """Return explicit alias occurrences, with zero-based, end-exclusive offsets."""
    lookup, offsets = _question_offsets(question)
    found = []
    for group in GROUPS:
        for alias in group['names']:
            suffix = r'(?![a-z0-9_-])'
            if normalized(alias) == 'think-on-graph':
                suffix += r'(?!\s*2\.0)'
            pattern = r'(?<![a-z0-9_-])' + r'\s+'.join(
                re.escape(part) for part in normalized(alias).split()) + suffix
            for match in re.finditer(pattern, lookup):
                start, end = offsets[match.start()], offsets[match.end() - 1] + 1
                found.append(dict(method=group['names'][0],
                    source_group=group.get('source_group', group['names'][0]),
                    start=start, end=end, text=question[start:end]))
    # Prefer the longest alias when overlapping names refer to the same mention.
    selected = []
    for item in sorted(found, key=lambda x: (x['start'], -(x['end'] - x['start']))):
        if not any(item['start'] < other['end'] and other['start'] < item['end']
                   for other in selected):
            selected.append(item)
    return selected


def subqueries(question):
    """Conservative question-only draft; does not change any retrieval callers.

    Extract attached descriptors only if every named method has one. Otherwise
    retain method names alone rather than infer ownership of shared details.
    An empty result means keep the original question (zero/one source paper).
    No corpus text, graph, answers, or evaluation identifiers are accepted.
    """
    occurrences = method_spans(question)
    if len({item['source_group'] for item in occurrences}) < 2:
        return []
    first = {}
    for item in occurrences:
        first.setdefault(item['method'], item)
    anchors = list(first.values())

    # Shared questions must be explicit, follow the final anchor, and contain
    # neither another method nor an unresolved comparative pronoun.
    shared = None
    tail_start = anchors[-1]['end']
    sentence_end = re.search(r'[。？！?!]', question[tail_start:])
    tail_end = tail_start + sentence_end.end() if sentence_end else len(question)
    match = re.search(r'(?:怎样分别|如何分别|分别|各(?=会|保留|想|自|需要|采用|如何|怎样|改变|指))[^。？！?!]*[？?]',
                      question[tail_start:tail_end])
    if match:
        start, end = tail_start + match.start(), tail_start + match.end()
        text = question[start:end]
        if not method_spans(text) and not re.search(r'两者|三者|前者|后者|它们|二者', text):
            shared = dict(start=start, end=end, role='shared_question', text=text)

    clauses = []
    for anchor in anchors:
        start, end = anchor['start'], len(question)
        following = [item['start'] for item in occurrences if item['start'] >= anchor['end']]
        if following:
            end = min(end, following[0])
        boundary = re.search(r'[，,、；;。？！?!]', question[anchor['end']:end])
        if boundary:
            end = anchor['end'] + boundary.start()
        if shared and anchor['end'] <= shared['start'] < end:
            end = shared['start']
        # Do not attach a common comparative task to the last method alone.
        task = re.search(r'是否|能否|怎样|如何|分别|意味着|是同一个',
                         question[anchor['end']:end])
        if task:
            end = anchor['end'] + task.start()
        raw = question[start:end]
        if following and end == following[0]:
            raw = re.sub(r'\s*(?:以及|和|与|及|跟|还有)\s*$', '', raw)
        raw = re.sub(r'(?:之后|以后|后)\s*$', '', raw).rstrip()
        end = start + len(raw)
        descriptor = question[anchor['end']:end].strip()
        attached = bool(re.match(r'(?:的\s*\S|复用|预测|生成|冻结|使用|通过|用)', descriptor))
        clauses.append((anchor, end, attached))

    use_clauses = all(attached for _, _, attached in clauses)
    result = []
    for index, (anchor, end, _) in enumerate(clauses, 1):
        source_end = end if use_clauses else anchor['end']
        spans = [dict(start=anchor['start'], end=source_end,
            role='method_clause' if use_clauses else 'method',
            text=question[anchor['start']:source_end])]
        if use_clauses and shared:
            spans.append(dict(shared))
        result.append(dict(id=f'SQ{index:02d}', method=anchor['method'],
            source_group=anchor['source_group'],
            text=' '.join(span['text'] for span in spans),
            subquery_source='span' if use_clauses else 'method_only',
            source_spans=spans,
            fallback_reason=None if use_clauses else 'coordinated_methods_with_unassigned_details',
            warnings=['shared_details_not_assigned'] if not use_clauses
                else ['cross_method_comparison_not_rewritten']))
    return result
