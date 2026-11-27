"""Explicit LangGraph RAG: validate -> retrieve -> rerank -> evidence -> generate -> verify."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import time
import math
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from .audit import Audit
from .cloud_embeddings import compatible, query_mode as resolve_query_mode
from .citations import validate_answer_with_meta
from .corpus import load_corpus, valid_vector
from .graph_store import GraphStore
from .local_models import run_worker, vector_cache, vector_metadata
from .providers import Providers, ProviderError
from .query_planner import build_fulltext_query, merge_multi_query_candidates, validate_plan
from .retrieval import normalize, offline_retrieve, fuse, select_evidence, rerank_view, chunk_windows
from .evidence_context import assemble
from .entity_aliases import GROUPS, is_comparison, mentions


_COMPLEX_QUERY_CUES = re.compile(r'(?:有人说|是否|对吗|准确吗|能否|还是|分别|各自|以及|对比|比较|差异|区别|不同|；|;)')


def should_skip_planner(question):
    """Fast-path simple single-paper factual queries to save ~3s cloud planner latency."""
    text = (question or '').strip()
    if not text or len(text) > 65 or is_comparison(text):
        return False
    if text.count('？') + text.count('?') > 1:
        return False
    if _COMPLEX_QUERY_CUES.search(text):
        return False
    named_papers = {g.get('source_group', g['names'][0]) for g in GROUPS
                    if any(mentions(text, name) for name in g['names'])}
    return len(named_papers) == 1


class State(TypedDict, total=False):
    question: str
    normalized: str
    classification: str
    request_id: str
    errors: list
    query_plan: dict
    active_queries: list
    query_vectors: list
    ranked: list
    evidence: list
    context_bytes: int
    answer: str
    citations: list
    premise_check: list | None
    status: str
    raw: str
    usage: dict | None
    estimated_cost: float | None
    model_name: str | None
    retrieval_summary: dict
    graph_paths: list
    generation_paths: list
    limitations: list


class Workflow:
    def __init__(self, root, cfg, backend='neo4j', query_mode=None, rerank=True, providers=None, graph_enabled=True,
                 path_budget=0, graph_expander=None, evidence_budget=18000, evidence_max=12, source_policy='named_first',
                 rerank_contextual=True, score_policy='relative', reservation_policy='round_robin',
                 citation_protocol='source-choice-v2', query_planner=False, premise_check=False,
                 graph_query_aware=False, method_cards=None, rerank_windowed=False,
                 planner_fast_path=False, async_trace_flush=False, _owned_graph_expander=None):
        if isinstance(path_budget, bool) or not isinstance(path_budget, int) or path_budget < 0:
            raise ValueError('invalid_path_budget')
        self.path_budget=path_budget
        if isinstance(evidence_budget, bool) or not isinstance(evidence_budget, int) or evidence_budget < 1:
            raise ValueError('invalid_evidence_budget')
        if isinstance(evidence_max, bool) or not isinstance(evidence_max, int) or not 1 <= evidence_max <= 40:
            raise ValueError('invalid_evidence_max')
        if source_policy not in ('named_first', 'score_order'):
            raise ValueError('invalid_source_policy')
        if not isinstance(rerank_contextual, bool):
            raise ValueError('invalid_rerank_contextual')
        if not isinstance(rerank_windowed, bool):
            raise ValueError('invalid_rerank_windowed')
        if score_policy not in ('fixed', 'relative'):
            raise ValueError('invalid_score_policy')
        if reservation_policy not in ('legacy', 'round_robin', 'subquery_balanced'):
            raise ValueError('invalid_reservation_policy')
        if citation_protocol not in ('source-choice-v1', 'source-choice-v2', 'source-choice-v3'):
            raise ValueError('invalid_citation_protocol')
        if not isinstance(query_planner, bool):
            raise ValueError('invalid_query_planner')
        if not isinstance(premise_check, bool):
            raise ValueError('invalid_premise_check')
        if not isinstance(graph_query_aware, bool):
            raise ValueError('invalid_graph_query_aware')
        if not isinstance(planner_fast_path, bool):
            raise ValueError('invalid_planner_fast_path')
        if not isinstance(async_trace_flush, bool):
            raise ValueError('invalid_async_trace_flush')
        self.evidence_budget, self.evidence_max, self.source_policy = evidence_budget, evidence_max, source_policy
        self.rerank_contextual, self.rerank_windowed, self.score_policy = rerank_contextual, rerank_windowed, score_policy
        self.reservation_policy, self.citation_protocol = reservation_policy, citation_protocol
        self.query_planner_enabled, self.premise_check_enabled = query_planner, premise_check
        self.planner_fast_path, self.async_trace_flush = planner_fast_path, async_trace_flush
        self.graph_query_aware, self.method_cards = graph_query_aware, method_cards
        self._owned_graph_expander = _owned_graph_expander
        self.root, self.cfg = root, cfg
        self.backend, self.query_mode, self.rerank_enabled = backend, resolve_query_mode(cfg, query_mode), rerank
        self.graph_enabled=graph_enabled
        self.graph_expander=graph_expander
        self.corpus_id, self.papers, self.chunks = load_corpus(root)
        self.chunk_map = {c['chunk_id']:c for c in self.chunks}
        # Lazy vector loading: production neo4j backend only needs model metadata, never all chunk vectors.
        self.metadata, self.vectors = vector_cache(root, load_vectors=(backend == 'offline'))
        self.audit = Audit(root, defer_live_flush=async_trace_flush)
        self.providers = providers or Providers(cfg, self.audit)
        self.store = GraphStore(cfg, self.corpus_id, self.metadata['model_id']) if backend == 'neo4j' else None
        graph = StateGraph(State)
        nodes = [('validate',self.validate),('retrieve',self.retrieve),('graph_expand',self.graph_expand),('rerank',self.rerank),
                 ('evidence',self.evidence),('generate',self.generate),('citations',self.citations)]
        previous = START
        for name, fn in nodes:
            graph.add_node(name, self.wrap(name,fn))
            graph.add_edge(previous,name)
            previous = name
        graph.add_edge(previous,END)
        self.graph = graph.compile()

    @classmethod
    def for_workbench(cls, root, cfg, backend='neo4j', query_mode=None, rerank=True,
                      query_planner=True, premise_check=True, use_graph_and_cards=True,
                      async_trace_flush=True, planner_fast_path=True, **kwargs):
        """Build the production-default workflow (Balanced-MMR + V3 citations + Planner + QA-Graph + MethodCards)."""
        root = Path(root)
        expander, navigator, owned = kwargs.pop('graph_expander', None), kwargs.pop('method_cards', None), None
        if use_graph_and_cards and backend == 'neo4j':
            try:
                model_id = vector_metadata(root)['model_id']
                from .method_cards import MethodCardNavigator, load_aux_vectors
                cards_path = root / 'artifacts/exports/pilot-v1/method-cards-v1.json'
                slot_vecs_path = root / 'data/method-card-embeddings.sqlite3'
                if navigator is None and cards_path.exists() and slot_vecs_path.exists():
                    navigator = MethodCardNavigator(cards_path, slot_vecs_path, model_id)
                graph_db = root / 'artifacts/eval/stage-4/benchmark-v3/isolated-graph.sqlite3'
                claim_vecs_path = root / 'data/claim-embeddings.sqlite3'
                if expander is None and graph_db.exists():
                    from .isolated_graph import IsolatedGraph
                    claim_vecs = load_aux_vectors(claim_vecs_path, model_id) if claim_vecs_path.exists() else None
                    digest = hashlib.sha256(graph_db.read_bytes()).hexdigest()
                    expander = IsolatedGraph(graph_db, digest, claim_vectors=claim_vecs)
                    owned = expander
            except Exception:
                pass
        defaults = dict(
            backend=backend, query_mode=query_mode, rerank=rerank,
            graph_enabled=use_graph_and_cards, graph_query_aware=use_graph_and_cards,
            path_budget=1200 if use_graph_and_cards else 0,
            graph_expander=expander, method_cards=navigator,
            evidence_budget=18000, evidence_max=12, source_policy='named_first',
            rerank_contextual=True, rerank_windowed=False, score_policy='relative',
            reservation_policy='subquery_balanced', citation_protocol='source-choice-v3',
            query_planner=query_planner, premise_check=premise_check,
            planner_fast_path=planner_fast_path, async_trace_flush=async_trace_flush,
            _owned_graph_expander=owned,
        )
        defaults.update(kwargs)
        return cls(root, cfg, **defaults)

    def wrap(self, name, fn):
        def run(state):
            if state.get('status') in ('invalid_input','error','refused','citation_error'):
                return {}
            return self.audit.stage(state['request_id'],name,lambda:fn(state))
        return run

    def validate(self, s):
        q = s['question']
        if not isinstance(q,str) or not q.strip() or len(q)>2000:
            return dict(status='invalid_input', answer='问题不能为空，且不得超过 2000 个字符。')
        classification = 'comparison' if is_comparison(q) else 'evidence_search'
        return dict(normalized=normalize(q), classification=classification)

    def compatible(self):
        return compatible(self.root, self.cfg, self.metadata['model_id'])

    def _plan_queries(self, s, errors):
        if not getattr(self, 'query_planner_enabled', False) or self.backend == 'offline' or not self.providers.configured('DEEPSEEK'):
            return None, [dict(id='Q00', text=s['normalized'], fulltext_query=None)]
        if getattr(self, 'planner_fast_path', False) and should_skip_planner(s['question']):
            local_kw = list(dict.fromkeys(re.findall(r'[A-Za-z][A-Za-z0-9._-]{1,}', s['question'])))[:8]
            plan = dict(decision='fast_path_single_paper', fast_path=True, english_keywords=local_kw,
                        subqueries=[], elapsed_seconds=0.0)
            return plan, [dict(id='Q00', text=s['normalized'],
                               fulltext_query=build_fulltext_query(s['question'], local_kw) if local_kw else None)]
        started = time.monotonic()
        try:
            body, _ = self.providers.plan_query(s['request_id'], s['question'])
            raw = body['choices'][0]['message']['content']
            plan = validate_plan(s['question'], json.loads(raw))
            plan['elapsed_seconds'] = time.monotonic() - started
            plan['usage'] = body.get('usage')
        except Exception as exc:
            code = exc.code if isinstance(exc, ProviderError) else type(exc).__name__
            errors.append('query_planner_fallback:' + code)
            plan = dict(decision='fallback', fallback=True, error=code, english_keywords=[], subqueries=[],
                        elapsed_seconds=time.monotonic() - started)
            return plan, [dict(id='Q00', text=s['normalized'], fulltext_query=None)]
        active = [dict(id='Q00', text=s['normalized'],
                       fulltext_query=build_fulltext_query(s['question'], plan['english_keywords']))]
        for sq in plan['subqueries']:
            active.append(dict(id=sq['id'], text=normalize(sq['text']),
                               fulltext_query=build_fulltext_query(sq['text'], sq['english_keywords'])))
        return plan, active

    def retrieve(self, s):
        errors = list(s['errors'])
        plan, active_queries = self._plan_queries(s, errors)
        query_texts = [q['text'] for q in active_queries]
        vectors = [None] * len(active_queries)
        try:
            if self.query_mode == 'local':
                output = run_worker(self.root, self.cfg, 'query', [dict(text=t) for t in query_texts], timeout=300)
                if output['model_id'] != self.metadata['model_id']:
                    raise ProviderError('local_embedding_model_changed')
                vectors = [valid_vector(v) for v in output['outputs']]
            elif self.query_mode == 'cloud':
                if not self.providers.configured('CLOUD_BGE'):
                    errors.append('cloud_embedding_not_configured:fulltext_only')
                elif not self.compatible():
                    errors.append('cloud_embedding_compatibility_unverified:fulltext_only')
                else:
                    vectors = self.providers.embedding(s['request_id'], query_texts)
            else:
                errors.append('dense_explicitly_disabled')
        except Exception as exc:
            errors.append('embedding_unavailable:' + (exc.code if isinstance(exc, ProviderError) else type(exc).__name__))

        def fetch_one(item):
            q, vec = item
            if self.store:
                if q.get('fulltext_query') is not None:
                    full, dense = self.store.retrieve(q['text'], vec, fulltext_query=q['fulltext_query'])
                else:
                    full, dense = self.store.retrieve(q['text'], vec)
            else:
                full, dense = offline_retrieve(self.chunks, self.vectors, q.get('fulltext_query') or q['text'], vec)
            # Current manifest whitelist applies even when a stale external index is present.
            full = [r for r in full if r['chunk_id'] in self.chunk_map][:20]
            dense = [r for r in dense if r['chunk_id'] in self.chunk_map][:20]
            return dict(id=q['id'], text=q['text'], fulltext_query=q.get('fulltext_query'),
                        channels=dict(fulltext=full, dense=dense))

        try:
            if len(active_queries) > 1:
                with ThreadPoolExecutor(max_workers=min(4, len(active_queries))) as pool:
                    per_query = list(pool.map(fetch_one, zip(active_queries, vectors)))
            else:
                per_query = [fetch_one((active_queries[0], vectors[0]))]
        except Exception as exc:
            return dict(status='error', answer='检索服务不可用；本次没有生成回答。', errors=errors + ['retrieval:' + type(exc).__name__])

        primary_full = per_query[0]['channels']['fulltext']
        primary_dense = per_query[0]['channels']['dense']
        for channel, rows in (('fulltext', primary_full), ('dense', primary_dense)):
            self.audit.record_candidates(s['request_id'], channel, rows)
        if len(per_query) > 1:
            ranked = merge_multi_query_candidates(per_query, per_channel_quota=8, cap=64)
            fusion_name = 'multi_query_quota_union cap=64'
        else:
            ranked = fuse(primary_full, primary_dense)
            fusion_name = 'RRF k=60'
        summary = dict(backend=self.backend, corpus_id=self.corpus_id, embedding_model_id=self.metadata['model_id'],
                       query_mode=self.query_mode, fulltext_hits=len(primary_full), dense_hits=len(primary_dense),
                       candidate_count=len(ranked), graph_executed=False, graph_hits=0, fusion=fusion_name,
                       fulltext_scoring='Neo4j Lucene fulltext (actual version in index report)' if self.store else 'Python BM25 diagnostic (not Neo4j)',
                       degraded=bool(errors))
        if plan is not None:
            summary['query_plan'] = plan
            summary['subquery_count'] = len(plan.get('subqueries') or [])
            summary['per_query_hits'] = {q['id']: dict(fulltext=len(q['channels']['fulltext']), dense=len(q['channels']['dense'])) for q in per_query}
        return dict(ranked=ranked, errors=errors, query_plan=plan or {}, active_queries=active_queries,
                    query_vectors=[v for v in vectors if v is not None], retrieval_summary=summary)

    def graph_expand(self, s):
        ranked = list(s.get('ranked', []))
        errors = list(s.get('errors', []))
        expander = getattr(self, 'graph_expander', None) or self.store
        navigator = getattr(self, 'method_cards', None)
        query_aware = getattr(self, 'graph_query_aware', False)
        q_vecs = s.get('query_vectors') or []
        if (not expander and not navigator) or not ranked or not self.graph_enabled:
            return dict(ranked=ranked, graph_paths=[], errors=errors,
                        retrieval_summary=dict(s['retrieval_summary'], graph_executed=False,
                                               graph_skip_reason='disabled' if not self.graph_enabled else 'no_seed_or_store'))
        paths = []
        graph_rows = []
        card_rows = []
        card_slots = []
        try:
            if expander:
                kwargs = dict(max_paths=40, max_seed_entities=40, question=s['question'], per_node=8)
                if query_aware and q_vecs and getattr(expander, 'supports_query_vectors', False):
                    kwargs['query_vectors'] = q_vecs
                paths = expander.expand_graph([row['chunk_id'] for row in ranked[:12]], **kwargs)
                graph_ids = []
                for path in paths:
                    for evidence in path.get('evidence', []):
                        chunk_id = evidence.get('chunk_id')
                        if chunk_id in self.chunk_map and chunk_id not in graph_ids:
                            graph_ids.append(chunk_id)
                graph_rows = [dict(chunk_id=cid, score=1.0 / (rank + 1)) for rank, cid in enumerate(graph_ids[:20])]
                self.audit.record_candidates(s['request_id'], 'graph', graph_rows)
        except Exception as exc:
            errors.append('graph_expansion_skipped:' + type(exc).__name__)
            if not navigator:
                return dict(ranked=ranked, graph_paths=[], errors=errors,
                            retrieval_summary=dict(s['retrieval_summary'], graph_executed=False, graph_error=type(exc).__name__))
        if navigator and q_vecs:
            try:
                card_rows, card_slots = navigator.navigate(s['question'], q_vecs, self.chunk_map, top_slots=8)
                if card_rows:
                    self.audit.record_candidates(s['request_id'], 'method_card', card_rows)
            except Exception as exc:
                errors.append('method_card_navigation_skipped:' + type(exc).__name__)
        # Preserve multi-query candidate provenance when Phase-2 planner is active; otherwise keep legacy RRF fuse.
        has_multi_query = any('found_by' in row for row in ranked)
        if has_multi_query or card_rows:
            by_id = {row['chunk_id']: dict(row, sources=list(row.get('sources') or []),
                                           found_by=list(row.get('found_by') or [])) for row in ranked}
            for rank, row in enumerate(graph_rows, 1):
                cid = row['chunk_id']
                if cid in by_id:
                    by_id[cid]['sources'].append(dict(channel='graph', rank=rank, score=row['score']))
                    by_id[cid]['graph_supported'] = True
                else:
                    by_id[cid] = dict(chunk_id=cid, score=1.0 / (60 + rank),
                                      sources=[dict(channel='graph', rank=rank, score=row['score'])],
                                      found_by=['GRAPH'], graph_supported=True)
            for rank, row in enumerate(card_rows, 1):
                cid = row['chunk_id']
                if cid in by_id:
                    by_id[cid]['sources'].append(dict(channel='method_card', rank=rank, score=row['score'], slot=row['slot']))
                    by_id[cid]['method_card_supported'] = True
                    by_id[cid]['method_card_score'] = row['score']
                else:
                    by_id[cid] = dict(chunk_id=cid, score=row['score'],
                                      sources=[dict(channel='method_card', rank=rank, score=row['score'], slot=row['slot'])],
                                      found_by=['MC'], method_card_supported=True, method_card_score=row['score'])
            ranked = list(by_id.values())[:76]
        else:
            ranked = fuse(
                [item for item in self.audit.conn.execute("SELECT chunk_id,score FROM candidates WHERE request_id=? AND channel='fulltext' ORDER BY rank", (s['request_id'],))],
                [item for item in self.audit.conn.execute("SELECT chunk_id,score FROM candidates WHERE request_id=? AND channel='dense' ORDER BY rank", (s['request_id'],))],
                graph_rows,
            )
        summary = dict(s['retrieval_summary'], graph_executed=bool(paths) or bool(card_rows),
                       graph_hits=len(graph_rows), graph_paths=len(paths), candidate_count=len(ranked),
                       graph_audit=expander.last_graph_audit if expander and isinstance(getattr(expander, 'last_graph_audit', None), dict) else {})
        if navigator:
            summary.update(method_card_hits=len(card_rows), method_card_slots=card_slots)
        return dict(ranked=ranked, graph_paths=paths, errors=errors, retrieval_summary=summary)

    def _rerank_score_batch(self, query_text, cids, contextual, windowed):
        if not windowed:
            candidates = [rerank_view(self.chunk_map[cid], contextual=contextual) for cid in cids]
            output = run_worker(self.root, self.cfg, 'rerank', candidates, query=query_text, timeout=300)
            if len(output['outputs']) != len(cids):
                raise ValueError('Reranker count mismatch')
            if any(not isinstance(score, (float, int)) or not math.isfinite(score) for score in output['outputs']):
                raise ValueError('Reranker nonfinite score')
            return {cid: float(sc) for cid, sc in zip(cids, output['outputs'])}, output
        # Windowed max-score reranking: score whole chunk + overlapping passage windows, keep max per chunk.
        items, owners = [], []
        for cid in cids:
            chunk = self.chunk_map[cid]
            whole = rerank_view(chunk, contextual=contextual)
            items.append(whole)
            owners.append(cid)
            wins = chunk_windows(chunk, max_chars=700, overlap=250, max_windows=5, contextual=contextual)
            if len(wins) > 1:
                for win in wins:
                    items.append(win)
                    owners.append(cid)
        best = {}
        total_infer, last_output = 0.0, None
        for start in range(0, len(items), 300):
            sub_items = items[start:start + 300]
            sub_owners = owners[start:start + 300]
            output = run_worker(self.root, self.cfg, 'rerank', sub_items, query=query_text, timeout=300)
            if len(output['outputs']) != len(sub_items):
                raise ValueError('Reranker count mismatch')
            if any(not isinstance(score, (float, int)) or not math.isfinite(score) for score in output['outputs']):
                raise ValueError('Reranker nonfinite score')
            for cid, score in zip(sub_owners, output['outputs']):
                val = float(score)
                if cid not in best or val > best[cid]:
                    best[cid] = val
            total_infer += float(output.get('inference_seconds') or 0.0)
            last_output = output
        last_output = dict(last_output, inference_seconds=total_infer, windowed_items=len(items))
        return best, last_output

    def rerank(self, s):
        ranked = s.get('ranked',[])
        errors = list(s['errors'])
        contextual = getattr(self, 'rerank_contextual', False)
        windowed = getattr(self, 'rerank_windowed', False)
        active_queries = s.get('active_queries') or []
        subqueries = [q for q in active_queries if q['id'] != 'Q00']
        if ranked and self.rerank_enabled:
            try:
                if subqueries:
                    # Owner-subquery reranking: score each candidate against each subquery that discovered it;
                    # candidates found only by Q00/graph are scored against the original normalized question.
                    owner_scores = {row['chunk_id']: {} for row in ranked}
                    batches = []
                    covered = set()
                    for sq in subqueries:
                        cids = [row['chunk_id'] for row in ranked if sq['id'] in (row.get('found_by') or ())]
                        if cids:
                            batches.append((sq['id'], sq['text'], cids))
                            covered.update(cids)
                    fallback_cids = [row['chunk_id'] for row in ranked if row['chunk_id'] not in covered]
                    if fallback_cids:
                        batches.append(('Q00', s['normalized'], fallback_cids))
                    total_infer, last_output = 0.0, None
                    for qid, qtext, cids in batches:
                        scored_map, output = self._rerank_score_batch(qtext, cids, contextual, windowed)
                        for cid, score in scored_map.items():
                            owner_scores[cid][qid] = score
                        total_infer += float(output.get('inference_seconds') or 0.0)
                        last_output = output
                    new_ranked = []
                    for row in ranked:
                        scores_map = owner_scores[row['chunk_id']]
                        best_qid, best_score = max(scores_map.items(), key=lambda kv: (kv[1], kv[0]))
                        new_ranked.append(dict(row, rerank_score=best_score, best_query_id=best_qid, owner_scores=scores_map))
                    ranked = sorted(new_ranked, key=lambda row: -row['rerank_score'])
                    summary = dict(s['retrieval_summary'], reranker={**dict(
                        model_id=last_output['model_id'], device=last_output['device'], max_pair_tokens=1024, truncation=True,
                        contextual_input='title+section+text' if contextual else 'text_only',
                        windowed=windowed,
                        rerank_mode='owner_subquery', rerank_batches=len(batches), total_inference_seconds=total_infer),
                        **{k: last_output[k] for k in ('dtype', 'persistent', 'model_reused', 'load_seconds',
                                                       'peak_cuda_memory_bytes', 'request_count', 'batch_size') if k in last_output}})
                else:
                    cids = [r['chunk_id'] for r in ranked]
                    scored_map, output = self._rerank_score_batch(s['normalized'], cids, contextual, windowed)
                    ranked = [dict(row, rerank_score=scored_map[row['chunk_id']]) for row in ranked]
                    ranked.sort(key=lambda row:-row['rerank_score'])
                    summary = dict(s['retrieval_summary'],reranker={**dict(model_id=output['model_id'],device=output['device'],max_pair_tokens=1024,truncation=True,
                        contextual_input='title+section+text' if contextual else 'text_only', windowed=windowed, rerank_mode='original_query'),
                        **{k:output[k] for k in ('dtype','persistent','model_reused','load_seconds','inference_seconds','elapsed_seconds','peak_cuda_memory_bytes','request_count','batch_size') if k in output}})
            except Exception as exc:
                errors.append('reranker_skipped:'+type(exc).__name__)
                summary = dict(s['retrieval_summary'],reranker='skipped')
        else:
            errors.append('reranker_disabled')
            summary = dict(s['retrieval_summary'],reranker='disabled')
        return dict(ranked=ranked,errors=errors,retrieval_summary=summary)

    def evidence(self, s):
        subquery_ids = [q['id'] for q in (s.get('active_queries') or []) if q['id'] != 'Q00']
        evidence,paths,detail = assemble(s.get('ranked',[]),self.chunk_map,s.get('graph_paths',[]),s['question'],s.get('classification')=='comparison',path_budget=self.path_budget,
            budget=self.evidence_budget, evidence_max=self.evidence_max, source_policy=self.source_policy,
            score_policy=getattr(self, 'score_policy', 'fixed'),
            reservation_policy=getattr(self, 'reservation_policy', 'legacy'),
            subquery_ids=subquery_ids or None)
        summary = dict(s['retrieval_summary'],evidence_count=len(evidence),**detail,context_budget_bytes=self.evidence_budget+self.path_budget,generation_path_count=len(paths),
                       evidence_sufficiency='retrieval_only; semantic support requires answer review',degraded=bool(s['errors']))
        if not evidence:
            return dict(evidence=[],status='refused',answer='没有找到足以支持回答的可定位证据。',retrieval_summary=summary)
        return dict(evidence=evidence,generation_paths=paths,limitations=detail['limitations'],context_bytes=detail['context_bytes'],retrieval_summary=summary)

    def generate(self,s):
        if not self.providers.configured('DEEPSEEK'):
            return dict(status='evidence_only',answer='已找到原文证据；DeepSeek API 尚未配置，未生成综合回答。')
        if self.backend == 'offline':
            # Offline diagnostic has no paid generation side effects, even if keys exist.
            return dict(status='evidence_only',answer='离线诊断已返回原文证据。')
        try:
            context = [{k:e[k] for k in ('chunk_id','title','page_start','page_end','quote')} for e in s['evidence']]
            body,cost = self.providers.answer(s['request_id'],s['question'],context,
                paths=s.get('retrieval_summary',{}).get('prompt_graph_paths',s.get('generation_paths',[])),
                limitations=s.get('limitations',[]),
                citation_protocol=getattr(self, 'citation_protocol', 'source-choice-v1'),
                premise_check=getattr(self, 'premise_check_enabled', False))
            raw = body['choices'][0]['message']['content']
            return dict(raw=raw,usage=body.get('usage'),estimated_cost=cost,model_name=body.get('model',self.cfg['DEEPSEEK_MODEL']))
        except Exception as exc:
            return dict(status='partial', answer='已保留原文证据；生成服务未得到可确认的有效回答。',errors=s['errors']+['generation:'+ (exc.code if isinstance(exc,ProviderError) else type(exc).__name__)])

    def citations(self,s):
        if not s.get('raw'):
            return {}
        try:
            answer,citations,status,checks = validate_answer_with_meta(s['raw'],s['evidence'])
            if s['retrieval_summary'].get('missing_comparison_groups') and status=='ok':
                status='partial'
                answer+='\n缺口：'+'；'.join(s.get('limitations',[])[:1])
            return dict(answer=answer,citations=citations,status=status,premise_check=checks)
        except Exception:
            return dict(status='citation_error',answer='生成结果未通过引用校验，已保留证据；未自动重新生成。',citations=[],errors=s['errors']+['invalid_generated_citations'])

    def ask(self,question):
        request_id = self.audit.start(question)
        initial = dict(request_id=request_id,question=question,errors=[],citations=[],evidence=[],graph_paths=[],usage=None,estimated_cost=None,model_name=None,status='running')
        try:
            s = self.graph.invoke(initial,config={'recursion_limit':12})
        except Exception as exc:
            s = dict(initial,status='error',answer='工作流失败，详见本地审计记录。',errors=[type(exc).__name__])
        result = {key:s.get(key) for key in ('request_id','answer','citations','evidence','retrieval_summary','model_name','usage','estimated_cost','status','errors','premise_check')}
        calls = self.audit.conn.execute('SELECT usage,cost FROM calls WHERE request_id=?',(request_id,)).fetchall()
        result.update(graph_paths=s.get('graph_paths',[]),generation_paths=s.get('generation_paths',[]),limitations=s.get('limitations',[]),trace_url=None,usage_status=('known' if all(row['usage'] for row in calls) else 'usage_unknown') if calls else 'not_called')
        result['stage_timings']=[dict(row) for row in self.audit.conn.execute('SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started',(request_id,))]
        result['estimated_cost'] = sum(row['cost'] for row in calls) if calls and all(row['cost'] is not None for row in calls) else None
        result['known_cost_subtotal'] = sum(row['cost'] for row in calls if row['cost'] is not None)
        total = self.audit.conn.execute('SELECT sum(cost) FROM calls').fetchone()[0]
        result['cost_warning'] = 'estimated_total_reached_CNY5' if total is not None and total >= 5 else None
        self.audit.finish(request_id,result)
        trace_id = self.audit.queue_trace(request_id)
        result['local_trace_id'] = trace_id
        self.audit.finish(request_id,result)
        if self.cfg.get('LANGSMITH_API_KEY'):
            if getattr(self, 'async_trace_flush', False):
                self.audit.live.flush_async()
                result['trace_flush_mode'] = 'async_background'
            else:
                self.audit.live.flush()
                live_id = self.audit.live_requests.get(request_id)
                result['trace_url'] = self.audit.live.url(live_id) if live_id else None
                self.audit.finish(request_id,result)
        return result

    def close(self):
        if getattr(self, '_owned_graph_expander', None) is not None:
            self._owned_graph_expander.close()
        if self.store:
            self.store.close()
        self.providers.client.close()
        self.audit.close()
