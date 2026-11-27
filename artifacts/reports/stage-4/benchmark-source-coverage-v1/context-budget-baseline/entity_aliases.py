"""Reviewed query aliases only; preserve original entity IDs and claim endpoints."""
import re
import unicodedata

ALIAS_VERSION = 'query-alias-v2'
# Source identities come from each paper itself, not evaluation references.
# A variant may share its parent paper without merging their KG entity IDs.
GROUPS = [
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
