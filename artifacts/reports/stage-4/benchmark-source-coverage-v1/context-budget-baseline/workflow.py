"""Explicit LangGraph RAG: validate -> retrieve -> rerank -> evidence -> generate -> verify."""
import json
from pathlib import Path
import time
import math
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from .audit import Audit
from .cloud_embeddings import compatible, query_mode as resolve_query_mode
from .citations import validate_answer
from .corpus import load_corpus, valid_vector
from .graph_store import GraphStore
from .local_models import run_worker, vector_cache
from .providers import Providers, ProviderError
from .retrieval import normalize, offline_retrieve, fuse, select_evidence
from .evidence_context import assemble
from .entity_aliases import is_comparison


class State(TypedDict, total=False):
    question: str
    normalized: str
    classification: str
    request_id: str
    errors: list
    ranked: list
    evidence: list
    context_bytes: int
    answer: str
    citations: list
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
    def __init__(self, root, cfg, backend='neo4j', query_mode=None, rerank=True, providers=None, graph_enabled=True):
        self.root, self.cfg = root, cfg
        self.backend, self.query_mode, self.rerank_enabled = backend, resolve_query_mode(cfg, query_mode), rerank
        self.graph_enabled=graph_enabled
        self.corpus_id, self.papers, self.chunks = load_corpus(root)
        self.chunk_map = {c['chunk_id']:c for c in self.chunks}
        self.metadata, self.vectors = vector_cache(root)
        self.audit = Audit(root)
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

    def retrieve(self, s):
        vector, errors = None, list(s['errors'])
        try:
            if self.query_mode == 'local':
                output = run_worker(self.root,self.cfg,'query',[dict(text=s['normalized'])], timeout=300)
                if output['model_id'] != self.metadata['model_id']:
                    raise ProviderError('local_embedding_model_changed')
                vector = valid_vector(output['outputs'][0])
            elif self.query_mode == 'cloud':
                if not self.providers.configured('CLOUD_BGE'):
                    errors.append('cloud_embedding_not_configured:fulltext_only')
                elif not self.compatible():
                    errors.append('cloud_embedding_compatibility_unverified:fulltext_only')
                else:
                    vector = self.providers.embedding(s['request_id'],[s['normalized']])[0]
            else:
                errors.append('dense_explicitly_disabled')
        except Exception as exc:
            errors.append('embedding_unavailable:'+ (exc.code if isinstance(exc,ProviderError) else type(exc).__name__))
        try:
            full,dense = self.store.retrieve(s['normalized'],vector) if self.store else offline_retrieve(self.chunks,self.vectors,s['normalized'],vector)
        except Exception as exc:
            return dict(status='error', answer='检索服务不可用；本次没有生成回答。', errors=errors+['retrieval:'+type(exc).__name__])
        # Current manifest whitelist applies even when a stale external index is present.
        full = [r for r in full if r['chunk_id'] in self.chunk_map][:20]
        dense = [r for r in dense if r['chunk_id'] in self.chunk_map][:20]
        for channel,rows in (('fulltext',full),('dense',dense)):
            self.audit.record_candidates(s['request_id'],channel,rows)
        ranked = fuse(full,dense)
        summary = dict(backend=self.backend, corpus_id=self.corpus_id, embedding_model_id=self.metadata['model_id'],
                       query_mode=self.query_mode, fulltext_hits=len(full), dense_hits=len(dense),
                       candidate_count=len(ranked), graph_executed=False, graph_hits=0, fusion='RRF k=60',
                       fulltext_scoring='Neo4j Lucene fulltext (actual version in index report)' if self.store else 'Python BM25 diagnostic (not Neo4j)',
                       degraded=bool(errors))
        return dict(ranked=ranked, errors=errors, retrieval_summary=summary)

    def graph_expand(self, s):
        ranked = list(s.get('ranked', []))
        errors = list(s.get('errors', []))
        if not self.store or not ranked or not self.graph_enabled:
            return dict(ranked=ranked, graph_paths=[], errors=errors,
                        retrieval_summary=dict(s['retrieval_summary'], graph_executed=False,
                                               graph_skip_reason='disabled' if not self.graph_enabled else 'no_seed_or_store'))
        try:
            paths = self.store.expand_graph([row['chunk_id'] for row in ranked[:12]], max_paths=40, max_seed_entities=40,
                                            question=s['question'],per_node=8)
            graph_ids = []
            for path in paths:
                for evidence in path.get('evidence', []):
                    chunk_id = evidence.get('chunk_id')
                    if chunk_id in self.chunk_map and chunk_id not in graph_ids:
                        graph_ids.append(chunk_id)
            graph_rows = [dict(chunk_id=cid, score=1.0/(rank+1)) for rank,cid in enumerate(graph_ids[:20])]
            for row in graph_rows:
                row['chunk_id'] = row['chunk_id']
            ranked = fuse(
                [item for item in self.audit.conn.execute("SELECT chunk_id,score FROM candidates WHERE request_id=? AND channel='fulltext' ORDER BY rank", (s['request_id'],))],
                [item for item in self.audit.conn.execute("SELECT chunk_id,score FROM candidates WHERE request_id=? AND channel='dense' ORDER BY rank", (s['request_id'],))],
                graph_rows,
            )
            self.audit.record_candidates(s['request_id'], 'graph', graph_rows)
            return dict(ranked=ranked, graph_paths=paths, errors=errors,
                        retrieval_summary=dict(s['retrieval_summary'], graph_executed=bool(paths), graph_hits=len(graph_rows),
                                               graph_paths=len(paths), candidate_count=len(ranked),
                                               graph_audit=self.store.last_graph_audit if isinstance(getattr(self.store,'last_graph_audit',None),dict) else {}))
        except Exception as exc:
            errors.append('graph_expansion_skipped:'+type(exc).__name__)
            return dict(ranked=ranked, graph_paths=[], errors=errors,
                        retrieval_summary=dict(s['retrieval_summary'], graph_executed=False, graph_error=type(exc).__name__))

    def rerank(self, s):
        ranked = s.get('ranked',[])
        errors = list(s['errors'])
        if ranked and self.rerank_enabled:
            try:
                output = run_worker(self.root,self.cfg,'rerank',[self.chunk_map[r['chunk_id']] for r in ranked], query=s['normalized'],timeout=300)
                if len(output['outputs']) != len(ranked):
                    raise ValueError('Reranker count mismatch')
                if any(not isinstance(score,(float,int)) or not math.isfinite(score) for score in output['outputs']):
                    raise ValueError('Reranker nonfinite score')
                ranked = [dict(row,rerank_score=score) for row,score in zip(ranked,output['outputs'])]
                ranked.sort(key=lambda row:-row['rerank_score'])
                summary = dict(s['retrieval_summary'],reranker={**dict(model_id=output['model_id'],device=output['device'],max_pair_tokens=1024,truncation=True),
                    **{k:output[k] for k in ('dtype','persistent','model_reused','load_seconds','inference_seconds','elapsed_seconds','peak_cuda_memory_bytes','request_count') if k in output}})
            except Exception as exc:
                errors.append('reranker_skipped:'+type(exc).__name__)
                summary = dict(s['retrieval_summary'],reranker='skipped')
        else:
            errors.append('reranker_disabled')
            summary = dict(s['retrieval_summary'],reranker='disabled')
        return dict(ranked=ranked,errors=errors,retrieval_summary=summary)

    def evidence(self, s):
        evidence,paths,detail = assemble(s.get('ranked',[]),self.chunk_map,s.get('graph_paths',[]),s['question'],s.get('classification')=='comparison')
        summary = dict(s['retrieval_summary'],evidence_count=len(evidence),**detail,context_budget_bytes=6000,generation_path_count=len(paths),
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
                                             paths=s.get('generation_paths',[]),limitations=s.get('limitations',[]))
            raw = body['choices'][0]['message']['content']
            return dict(raw=raw,usage=body.get('usage'),estimated_cost=cost,model_name=body.get('model',self.cfg['DEEPSEEK_MODEL']))
        except Exception as exc:
            return dict(status='partial', answer='已保留原文证据；生成服务未得到可确认的有效回答。',errors=s['errors']+['generation:'+ (exc.code if isinstance(exc,ProviderError) else type(exc).__name__)])

    def citations(self,s):
        if not s.get('raw'):
            return {}
        try:
            answer,citations,status = validate_answer(s['raw'],s['evidence'])
            if s['retrieval_summary'].get('missing_comparison_groups') and status=='ok':
                status='partial'
                answer+='\n缺口：'+'；'.join(s.get('limitations',[])[:1])
            return dict(answer=answer,citations=citations,status=status)
        except Exception:
            return dict(status='citation_error',answer='生成结果未通过引用校验，已保留证据；未自动重新生成。',citations=[],errors=s['errors']+['invalid_generated_citations'])

    def ask(self,question):
        request_id = self.audit.start(question)
        initial = dict(request_id=request_id,question=question,errors=[],citations=[],evidence=[],graph_paths=[],usage=None,estimated_cost=None,model_name=None,status='running')
        try:
            s = self.graph.invoke(initial,config={'recursion_limit':12})
        except Exception as exc:
            s = dict(initial,status='error',answer='工作流失败，详见本地审计记录。',errors=[type(exc).__name__])
        result = {key:s.get(key) for key in ('request_id','answer','citations','evidence','retrieval_summary','model_name','usage','estimated_cost','status','errors')}
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
            self.audit.live.flush()
            live_id = self.audit.live_requests.get(request_id)
            result['trace_url'] = self.audit.live.url(live_id) if live_id else None
            self.audit.finish(request_id,result)
        return result

    def close(self):
        if self.store:
            self.store.close()
        self.providers.client.close()
        self.audit.close()
