"""Read-only bounded traversal of a frozen evidence graph, without gold mappings."""
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import sqlite3
import time

from .entity_aliases import query_matches


class IsolatedGraph:
    supports_query_vectors = True

    def __init__(self, path, expected_sha256, claim_vectors=None):
        self.path = Path(path).resolve()
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        if self.sha256 != expected_sha256:
            raise ValueError('isolated_graph_hash_mismatch')
        self.conn = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)
        self.conn.row_factory = sqlite3.Row
        allowed = {'entities', 'edges', 'claims', 'claim_sources', 'source_chunks', 'papers', 'graph_meta'}
        def authorize(action, table, column, database, trigger):
            if action == sqlite3.SQLITE_READ and (table not in allowed or
                    table == 'claims' and column in ('unit_id', 'path_id')):
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        self.conn.set_authorizer(authorize)
        self.catalog = [dict(id=r['entity_id'], name=r['name'], type=r['entity_type'])
            for r in self.conn.execute('SELECT entity_id,name,entity_type FROM entities ORDER BY entity_id')]
        self.claim_vectors = dict(claim_vectors or {})
        self.last_graph_audit = {}

    def close(self):
        self.conn.close()

    @staticmethod
    def interleave(groups):
        return [item for batch in zip_longest(*groups) for item in batch if item is not None]

    @staticmethod
    def _dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def _claim_scores(self, query_vectors):
        if not query_vectors or not self.claim_vectors:
            return {}
        valid_q = [q for q in query_vectors if q]
        if not valid_q:
            return {}
        return {cid: max(self._dot(q, vec) for q in valid_q) for cid, vec in self.claim_vectors.items()}

    def expand_graph(self, seed_chunk_ids, max_paths=40, max_seed_entities=40, question='', per_node=8, query_vectors=None):
        started = time.monotonic()
        max_paths = max(0, min(int(max_paths), 40))
        degree = max(1, min(int(per_node), 8))
        max_seeds = max(1, min(int(max_seed_entities), 40))
        claim_scores = self._claim_scores(query_vectors)
        query_aware = bool(claim_scores)
        matched = query_matches(question, self.catalog)
        seeds = list(matched[:max_seeds])
        seed_ids_seen = {e['id'] for e in seeds}
        semantic_seed_claims = []
        if query_aware:
            # Dual-channel seeding: also anchor endpoints of top-similarity claims (sim >= 0.50).
            top_claims = sorted(claim_scores.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
            top_ids = [cid for cid, sim in top_claims if sim >= 0.50]
            if top_ids:
                semantic_seed_claims = top_ids
                marks = ','.join('?' for _ in top_ids)
                edge_rows = self.conn.execute(f'SELECT subject_id,object_id,claim_id FROM edges WHERE claim_id IN ({marks})', top_ids).fetchall()
                by_cid = {r['claim_id']: (r['subject_id'], r['object_id']) for r in edge_rows}
                catalog_map = {e['id']: e for e in self.catalog}
                for cid in top_ids:
                    for eid in by_cid.get(cid, ()):
                        if eid in catalog_map and eid not in seed_ids_seen and len(seeds) < max_seeds:
                            seeds.append(catalog_map[eid])
                            seed_ids_seen.add(eid)
        source_ranks = {cid: i for i, cid in enumerate(seed_chunk_ids[:12])}
        if not seeds and source_ranks:
            marks = ','.join('?' for _ in source_ranks)
            rows = self.conn.execute(f'''SELECT DISTINCT e.subject_id,e.object_id
                FROM edges e JOIN claim_sources s ON s.claim_id=e.claim_id
                WHERE s.chunk_id IN ({marks}) ORDER BY e.claim_id LIMIT 40''', list(source_ranks))
            ids = {eid for row in rows for eid in row}
            seeds = [e for e in self.catalog if e['id'] in ids][:max_seeds]
        self.last_graph_audit = dict(backend='isolated_sqlite', graph_sha256=self.sha256,
            anchors=matched, semantic_seed_claims=semantic_seed_claims, query_aware=query_aware,
            seed_count=len(seeds), max_hops=2, max_paths=max_paths,
            per_node=degree, deadline_seconds=10, degree_truncated=[],
            reference_tables_access='denied by SQLite authorizer',
            direction_policy='traversal may be reverse; each edge preserves original subject/object')
        catalog = {e['id']: e for e in self.catalog}
        adjacency = {}
        frontier = seeds
        self.conn.set_progress_handler(lambda: int(time.monotonic() - started > 10), 1000)
        try:
            for depth in range(2):
                next_ids = []
                for node in frontier[:40]:
                    eid = node['id']
                    if eid in adjacency:
                        continue
                    rows = list(self.conn.execute('''SELECT e.subject_id,e.object_id,c.claim_id,
                        c.subject,c.object,c.predicate,c.evidence_quote,c.provenance_json
                        FROM edges e JOIN claims c ON c.claim_id=e.claim_id
                        WHERE e.subject_id=? OR e.object_id=? ORDER BY c.claim_id''', (eid, eid)))
                    if query_aware:
                        rows.sort(key=lambda r: (-claim_scores.get(r['claim_id'], 0.0),
                            source_ranks.get(json.loads(r['provenance_json'])['chunk_id'], 99), r['claim_id']))
                    else:
                        rows.sort(key=lambda r: (source_ranks.get(json.loads(r['provenance_json'])['chunk_id'], 99), r['claim_id']))
                    if len(rows) > degree:
                        self.last_graph_audit['degree_truncated'].append(eid)
                    neighbors = []
                    for row in rows[:degree]:
                        prov = json.loads(row['provenance_json'])
                        target = row['object_id'] if row['subject_id'] == eid else row['subject_id']
                        neighbors.append(dict(target=target,
                            sim=claim_scores.get(row['claim_id'], 0.0),
                            paper_id=prov.get('paper_id'),
                            edge=dict(predicate=row['predicate'], claim_id=row['claim_id'],
                                subject=row['subject'], object=row['object']),
                            evidence=dict(claim_id=row['claim_id'], chunk_id=prov['chunk_id'],
                                page_start=prov['page_start'], page_end=prov['page_end'],
                                quote=row['evidence_quote'], predicate=row['predicate'])))
                        if target not in adjacency and target not in next_ids:
                            next_ids.append(target)
                    adjacency[eid] = neighbors
                frontier = [catalog[eid] for eid in next_ids[:40]]
                if time.monotonic() - started > 10:
                    raise TimeoutError('isolated_graph_deadline')
            one, two = [], []
            for seed in seeds:
                one_paths, two_paths = [], []
                for first in adjacency.get(seed['id'], []):
                    nodes = [seed, catalog[first['target']]]
                    one_paths.append(dict(nodes=nodes, edges=[first['edge']], evidence=[first['evidence']],
                        _score=first['sim']))
                    for second in adjacency.get(first['target'], []):
                        if second['target'] == seed['id'] or first['edge']['claim_id'] == second['edge']['claim_id']:
                            continue
                        cross_bonus = 0.05 if (first.get('paper_id') and second.get('paper_id') and first['paper_id'] != second['paper_id']) else 0.0
                        two_paths.append(dict(nodes=nodes + [catalog[second['target']]],
                            edges=[first['edge'], second['edge']], evidence=[first['evidence'], second['evidence']],
                            _score=(first['sim'] + second['sim']) / 2.0 + cross_bonus))
                one.append(one_paths)
                two.append(two_paths)
            candidates = self.interleave(one) + self.interleave(two)
            if query_aware:
                candidates.sort(key=lambda p: (-p['_score'], len(p['edges']), tuple(e['claim_id'] for e in p['edges'])))
            result, seen = [], set()
            for path in candidates:
                key = tuple(sorted(e['claim_id'] for e in path['edges']))
                if key in seen:
                    continue
                seen.add(key)
                if len(result) < max_paths:
                    clean_path = {k: v for k, v in path.items() if k != '_score'}
                    if query_aware:
                        clean_path['relevance_score'] = round(path['_score'], 4)
                    result.append(clean_path)
            self.last_graph_audit.update(returned_paths=len(result), expanded_nodes=len(adjacency),
                elapsed_seconds=time.monotonic() - started)
            return result
        finally:
            self.conn.set_progress_handler(None, 0)
