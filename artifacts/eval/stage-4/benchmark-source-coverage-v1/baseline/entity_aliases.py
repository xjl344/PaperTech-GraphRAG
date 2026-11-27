"""Reviewed query aliases only; preserve original entity IDs and claim endpoints."""
import re
import unicodedata

ALIAS_VERSION = 'query-alias-v1'
GROUPS = [
    dict(names=['ToG', 'Think-on-Graph'], source_chunk='chunk_e09b5a88c34014513aad6c0d6121f790',
         quote='Think-on-Graph (ToG)'),
    dict(names=['ToG-2', 'Think-on-Graph 2.0'], source_chunk='chunk_9b63637ef18ed2d67ff105ef55092df3',
         quote='Think-on-Graph 2.0 (ToG-2)'),
]


def normalized(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def mentions(question, name):
    suffix=r'(?![\w-])'
    if normalized(name)=='think-on-graph':
        suffix+=r'(?!\s*2\.0)'
    return re.search(r'(?<![\w-])' + re.escape(normalized(name)) + suffix, normalized(question)) is not None


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
