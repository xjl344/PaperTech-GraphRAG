"""Fixed parameterized Cypher; Neo4j owns production full-text and vector retrieval."""
import hashlib
import json
import re
import time
from .entity_aliases import ALIAS_VERSION, query_matches
from neo4j import GraphDatabase, Query


RELATION_QUERY_TYPES = 'PROPOSES|ADDRESSES|EVALUATED_ON|COMPARES_WITH|IMPROVES_UPON'
RELATION_TYPES = {
    ('Paper', 'PROPOSES', 'Method'): 'PROPOSES',
    ('Method', 'ADDRESSES', 'Problem'): 'ADDRESSES',
    ('Method', 'EVALUATED_ON', 'Dataset'): 'EVALUATED_ON',
    ('Method', 'COMPARES_WITH', 'Method'): 'COMPARES_WITH',
    ('Method', 'IMPROVES_UPON', 'Method'): 'IMPROVES_UPON',
}


class GraphStore:
    def __init__(self, cfg, corpus_id, model_id=None):
        self.corpus_id = corpus_id
        self.model_id = model_id
        self.driver = GraphDatabase.driver(cfg['NEO4J_URI'], auth=(cfg['NEO4J_USER'], cfg['NEO4J_PASSWORD']),
                                          connection_timeout=10, max_transaction_retry_time=0)

    def close(self):
        self.driver.close()

    def ensure_kg_schema(self):
        self.driver.verify_connectivity()
        for statement in (
            'CREATE CONSTRAINT papertech_kg_entity IF NOT EXISTS FOR (e:KGEntity) REQUIRE e.entity_id IS UNIQUE',
            'CREATE CONSTRAINT papertech_kg_claim IF NOT EXISTS FOR (c:KGClaim) REQUIRE c.claim_id IS UNIQUE',
        ):
            self.execute(statement)

    def execute(self, query, timeout_seconds=20, **params):
        with self.driver.session(database='neo4j') as session:
            return session.run(Query(query, timeout=max(.1, min(timeout_seconds,20))), **params).data()

    def build(self, papers, chunks, metadata, vectors):
        if any(c['text_sha256'] not in vectors for c in chunks):
            raise ValueError('Missing current vectors; index write not started')
        self.driver.verify_connectivity()
        for statement in (
            'CREATE CONSTRAINT papertech_paper IF NOT EXISTS FOR (p:Paper) REQUIRE p.paper_id IS UNIQUE',
            'CREATE CONSTRAINT papertech_chunk IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE',
            'CREATE CONSTRAINT papertech_corpus IF NOT EXISTS FOR (v:Corpus) REQUIRE v.corpus_id IS UNIQUE',
            'CREATE CONSTRAINT papertech_kg_entity IF NOT EXISTS FOR (e:KGEntity) REQUIRE e.entity_id IS UNIQUE',
            'CREATE CONSTRAINT papertech_kg_claim IF NOT EXISTS FOR (c:KGClaim) REQUIRE c.claim_id IS UNIQUE',
            "CREATE FULLTEXT INDEX papertech_text IF NOT EXISTS FOR (c:Chunk) ON EACH [c.text, c.title] OPTIONS {indexConfig: {`fulltext.analyzer`: 'standard-no-stop-words', `fulltext.eventually_consistent`: false}}",
            "CREATE VECTOR INDEX papertech_vector IF NOT EXISTS FOR (c:Chunk) ON c.embedding OPTIONS {indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'}}",
        ):
            self.execute(statement)
        self.execute('CALL db.awaitIndexes(120)')
        self.execute('MERGE (v:Corpus {corpus_id:$corpus}) SET v.status="indexing",v.model_id=$model',corpus=self.corpus_id,model=metadata['model_id'])
        for paper in papers:
            self.execute('MERGE (p:Paper {paper_id:$id}) SET p.title=$title,p.source_relative_path=$path,p.source_sha256=$hash',
                         id=paper['paper_id'], title=paper['title'], path=paper['source_relative_path'], hash=paper['source_sha256'])
        for start in range(0, len(chunks), 40):
            rows = []
            for c in chunks[start:start+40]:
                if c['text_sha256'] not in vectors:
                    raise ValueError('Missing validated vector; partial index is not complete')
                rows.append(dict(chunk_id=c['chunk_id'], paper_id=c['paper_id'], parse_id=c['parse_id'], text=c['text'],
                                 title=c['title'], text_sha256=c['text_sha256'], page_start=c['page_start'], page_end=c['page_end'],
                                 source_spans=json.dumps(c['source_spans']), source_relative_path=c['source_relative_path'],
                                 content_kind=c['content_kind'], section=c['section'], embedding=vectors[c['text_sha256']],
                                 model_id=metadata['model_id'], corpus_id=self.corpus_id))
            self.execute('UNWIND $rows AS row MATCH (p:Paper {paper_id:row.paper_id}) MERGE (c:Chunk {chunk_id:row.chunk_id}) SET c += row MERGE (p)-[:HAS_CHUNK]->(c)', rows=rows)
        self.execute('CALL db.awaitIndexes(120)')
        self.execute('MATCH (v:Corpus {corpus_id:$corpus}) SET v.status="ready",v.expected_chunks=$chunks,v.expected_papers=$papers',corpus=self.corpus_id,chunks=len(chunks),papers=len(papers))
        return self.inspect()

    def inspect(self):
        return dict(corpus_id=self.corpus_id,corpus=self.execute('MATCH (v:Corpus {corpus_id:$corpus}) RETURN v.status AS status,v.model_id AS model_id,v.expected_chunks AS expected_chunks',corpus=self.corpus_id),
                    counts=self.execute('MATCH (c:Chunk) WHERE c.corpus_id=$corpus RETURN count(c) AS chunks,count(DISTINCT c.paper_id) AS papers', corpus=self.corpus_id),
                    semantic_counts=self.execute("MATCH (n) WHERE n.corpus_id=$corpus AND 'KGEntity' IN labels(n) RETURN count(n) AS entities",corpus=self.corpus_id),
                    indexes=self.execute("SHOW INDEXES YIELD name,type,state,options WHERE name IN ['papertech_text','papertech_vector'] RETURN name,type,state,options"),
                    version=self.execute('CALL dbms.components() YIELD name,versions,edition RETURN name,versions,edition'))

    def write_kg_claim(self, claim):
        signature=(claim['subject_type'],claim['predicate'],claim['object_type'])
        relation_type=RELATION_TYPES.get(signature)
        if not relation_type or claim['review_status']!='approved' or claim['validation_status']!='valid':
            raise ValueError('Only approved, validated, allowlisted claims can be written')
        source=self.execute('''MATCH (p:Paper {paper_id:$paper_id}),(c:Chunk {chunk_id:$chunk_id,corpus_id:$corpus})
            RETURN p.source_sha256 AS source_sha256,c.paper_id AS paper_id,c.parse_id AS parse_id,
            c.page_start AS page_start,c.page_end AS page_end,
            c.source_relative_path AS source_relative_path,c.text AS text''',
            paper_id=claim['paper_id'],chunk_id=claim['chunk_id'],corpus=self.corpus_id)
        if not source or source[0]['paper_id']!=claim['paper_id'] or source[0]['parse_id']!=claim['parse_id']:
            raise ValueError('Claim source Chunk does not match the current corpus')
        if not (claim['evidence_quote'] and claim['evidence_quote'] in source[0]['text']):
            raise ValueError('Claim quote is not an exact substring of its source Chunk')
        if source[0]['page_start']!=claim['page_start'] or source[0]['page_end']!=claim['page_end']:
            raise ValueError('Claim page range differs from source Chunk')
        if source[0]['source_relative_path']!=claim['source_relative_path']:
            raise ValueError('Claim source path differs from source Chunk')
        if source[0]['source_sha256']!=claim['source_sha256']:
            raise ValueError('Claim source hash differs from current Paper')
        entity_props=dict(corpus_id=self.corpus_id)
        if claim['subject_type']=='Paper':
            subject_query='MATCH (s:Paper {paper_id:$subject_norm})'
            subject_params={'subject_norm':claim['subject_norm']}
        else:
            subject_query='''MERGE (s:KGEntity {entity_id:$subject_id})
                SET s.corpus_id=$corpus,s.entity_type=$subject_type,s.name=coalesce(s.name,$subject),s.normalized_name=$subject_norm'''
            subject_params={'subject_id':hashlib.sha256(f"{self.corpus_id}\0{claim['subject_type']}\0{claim['subject_norm']}".encode()).hexdigest(),
                            'subject_type':claim['subject_type'],'subject':claim['subject'],'subject_norm':claim['subject_norm']}
        object_query='''MERGE (o:KGEntity {entity_id:$object_id})
            SET o.corpus_id=$corpus,o.entity_type=$object_type,o.name=coalesce(o.name,$object),o.normalized_name=$object_norm'''
        object_params={'object_id':hashlib.sha256(f"{self.corpus_id}\0{claim['object_type']}\0{claim['object_norm']}".encode()).hexdigest(),
                       'object_type':claim['object_type'],'object':claim['object'],'object_norm':claim['object_norm']}
        query=f'''MATCH (p:Paper {{paper_id:$paper_id}}),(chunk:Chunk {{chunk_id:$chunk_id,corpus_id:$corpus}})
            {subject_query}
            {object_query}
            MERGE (cl:KGClaim {{claim_id:$claim_id}}) SET cl += $claim_props
            MERGE (cl)-[:SUPPORTED_BY]->(chunk)
            MERGE (cl)-[:STATED_IN]->(p)
            MERGE (cl)-[:SUBJECT]->(s)
            MERGE (cl)-[:OBJECT]->(o)
            MERGE (s)-[r:{relation_type} {{claim_id:$claim_id}}]->(o) SET r += $relation_props
            RETURN cl.claim_id AS claim_id'''
        claim_props={key:claim[key] for key in ('claim_id','corpus_id','paper_id','paper_title','chunk_id','predicate',
                       'evidence_quote','quote_match_method','page_start','page_end','claim_kind','confidence','validation_status',
                       'review_status','model','prompt_version','schema_version','source_relative_path','source_sha256','parse_id','created_at')}
        review_note = claim.get('review_note') or ''
        delegated = review_note.startswith('AI delegated review by Codex; evidence-review-v1; ')
        claim_props.update(review_note=review_note, reviewed_at=claim.get('reviewed_at'),
                           reviewer='Codex' if delegated else 'not_recorded',
                           review_kind='ai_delegated' if delegated else 'not_recorded')
        relprops={key:claim_props[key] for key in ('claim_id','corpus_id','paper_id','chunk_id','evidence_quote',
                   'quote_match_method','page_start','page_end','claim_kind','confidence','review_status','model','prompt_version','schema_version',
                   'source_relative_path','source_sha256','parse_id','created_at')}
        relprops.update({key:claim_props[key] for key in ('review_note','reviewed_at','reviewer','review_kind')})
        params=dict(paper_id=claim['paper_id'],chunk_id=claim['chunk_id'],corpus=self.corpus_id,
                    claim_id=claim['claim_id'],claim_props=claim_props,relation_props=relprops,**subject_params,**object_params)
        if claim['subject_type']=='Paper':
            params['subject_norm']=claim['paper_id']
        result=self.execute(query,**params)
        if not result:
            raise RuntimeError('Claim graph write returned no confirmation')
        return result[0]['claim_id']

    def expand_graph(self, seed_chunk_ids, max_paths=40, max_seed_entities=40, question='', per_node=8):
        seed_chunk_ids=list(dict.fromkeys(seed_chunk_ids))[:40]
        max_paths=max(1,min(max_paths,40)); max_seeds=max(1,min(max_seed_entities,40))
        degree=max(1,min(per_node,8))
        deadline=time.monotonic()+10
        def run(query, **params):
            remaining=deadline-time.monotonic()
            if remaining<=0:
                raise TimeoutError('graph_expansion_deadline')
            return self.execute(query, timeout_seconds=remaining, corpus=self.corpus_id, **params)
        catalog=run('''MATCH (e:KGEntity {corpus_id:$corpus})
            WHERE EXISTS { MATCH (:KGClaim {corpus_id:$corpus,review_status:'approved'})-[:SUBJECT|OBJECT]->(e) }
            RETURN e.entity_id AS id,e.name AS name,e.entity_type AS type ORDER BY id LIMIT 1000''')
        matched=query_matches(question,catalog)
        seeds=matched[:max_seeds]
        if not seeds and seed_chunk_ids:
            seeds=run('''MATCH (e:KGEntity {corpus_id:$corpus})<-[:SUBJECT|OBJECT]-(c:KGClaim {corpus_id:$corpus,review_status:'approved'})
                -[:SUPPORTED_BY]->(s:Chunk {corpus_id:$corpus}) WHERE s.chunk_id IN $seed_ids
                RETURN DISTINCT e.entity_id AS id,e.name AS name,e.entity_type AS type ORDER BY id LIMIT $max_seeds''',
                seed_ids=seed_chunk_ids,max_seeds=max_seeds)
        self.last_graph_audit=dict(alias_version=ALIAS_VERSION, anchors=matched, seed_count=len(seeds),
                                   max_hops=2, per_node=degree, max_paths=max_paths, deadline_seconds=10,
                                   alias_policy='query equivalence only; original entities retained', degree_truncated=[])
        if not seeds:
            return []
        neighbor_query=f'''UNWIND $ids AS entity_id
            CALL (entity_id) {{
                MATCH (n:KGEntity {{entity_id:entity_id,corpus_id:$corpus}})-[r:{RELATION_QUERY_TYPES}]-(other:KGEntity {{corpus_id:$corpus}})
                WHERE r.review_status='approved' AND r.corpus_id=$corpus
                MATCH (cl:KGClaim {{claim_id:r.claim_id,corpus_id:$corpus,review_status:'approved'}})-[:SUPPORTED_BY]->(c:Chunk {{corpus_id:$corpus}})
                RETURN r,other,cl,c ORDER BY r.claim_id,other.entity_id LIMIT $degree_probe
            }}
            RETURN entity_id AS origin,other.entity_id AS target_id,other.name AS target_name,other.entity_type AS target_type,
                startNode(r).entity_id AS subject_id,endNode(r).entity_id AS object_id,
                {{predicate:type(r),claim_id:r.claim_id,subject:startNode(r).name,object:endNode(r).name}} AS edge,
                {{claim_id:cl.claim_id,chunk_id:c.chunk_id,page_start:cl.page_start,page_end:cl.page_end,
                  quote:cl.evidence_quote,predicate:cl.predicate}} AS evidence'''
        # Each frontier has at most 40 nodes, each contributes at most 8 edges.
        adjacency={}
        frontier=seeds
        for depth in range(2):
            ids=list(dict.fromkeys(n['id'] for n in frontier))[:40]
            if not ids:
                break
            rows=run(neighbor_query, ids=ids, degree_probe=degree+1)
            next_frontier=[]
            for node_id in ids:
                neighbors=[r for r in rows if r['origin']==node_id]
                if len(neighbors)>degree:
                    self.last_graph_audit['degree_truncated'].append(node_id)
                adjacency[node_id]=neighbors[:degree]
                next_frontier.extend(dict(id=r['target_id'],name=r['target_name'],type=r['target_type']) for r in neighbors[:degree] if r['target_id'] not in adjacency)
            frontier=next_frontier
        paths=[]; seen=set()
        # Retain one-hop paths before adding two-hop paths, in a stable order.
        for seed in seeds:
            for first in adjacency.get(seed['id'],[]):
                target=dict(id=first['target_id'],name=first['target_name'],type=first['target_type'])
                key=(first['edge']['claim_id'],)
                if key not in seen:
                    paths.append(dict(nodes=[seed,target],edges=[first['edge']],evidence=[first['evidence']]))
                    seen.add(key)
        for seed in seeds:
            for first in adjacency.get(seed['id'],[]):
                for second in adjacency.get(first['target_id'],[]):
                    if second['target_id']==seed['id'] or second['edge']['claim_id']==first['edge']['claim_id']:
                        continue
                    key=tuple(sorted((first['edge']['claim_id'],second['edge']['claim_id'])))
                    if key in seen:
                        continue
                    seen.add(key)
                    paths.append(dict(nodes=[seed,dict(id=first['target_id'],name=first['target_name'],type=first['target_type']),
                                             dict(id=second['target_id'],name=second['target_name'],type=second['target_type'])],
                                      edges=[first['edge'],second['edge']],evidence=[first['evidence'],second['evidence']]))
                    if len(paths)>=max_paths:
                        break
                if len(paths)>=max_paths:
                    break
            if len(paths)>=max_paths:
                break
        self.last_graph_audit.update(returned_paths=min(len(paths),max_paths), expanded_nodes=len(adjacency),
                                     elapsed_seconds=10-(deadline-time.monotonic()))
        return paths[:max_paths]

    def retrieve(self, question, vector=None, *, fulltext_enabled=True, dense_top=20):
        if not isinstance(dense_top, int) or isinstance(dense_top, bool) or not 1 <= dense_top <= 40:
            raise ValueError('dense_top_out_of_range')
        ready=self.execute('MATCH (v:Corpus {corpus_id:$corpus}) RETURN v.status AS status,v.model_id AS model_id',corpus=self.corpus_id)
        if not ready or ready[0]['status']!='ready':
            raise RuntimeError('Current corpus index is not complete')
        if vector and self.model_id and ready[0]['model_id']!=self.model_id:
            raise RuntimeError('Local/query embedding model differs from indexed model')
        # Escape Lucene syntax by admitting only word tokens; OR means recall union.
        words = re.findall(r'[^\W_]+(?:-[^\W_]+)*', question, flags=re.UNICODE)[:80]
        lucene = ' OR '.join('"' + w + '"' for w in words)
        full = self.execute('CALL db.index.fulltext.queryNodes("papertech_text",$q) YIELD node,score WHERE node.corpus_id=$corpus RETURN node.chunk_id AS chunk_id,score ORDER BY score DESC LIMIT 20', q=lucene, corpus=self.corpus_id) if words and fulltext_enabled else []
        dense = self.execute('CALL db.index.vector.queryNodes("papertech_vector",$k,$vector) YIELD node,score WHERE node.corpus_id=$corpus RETURN node.chunk_id AS chunk_id,score ORDER BY score DESC LIMIT $limit', k=100, vector=vector, corpus=self.corpus_id, limit=dense_top) if vector else []
        return full, dense
