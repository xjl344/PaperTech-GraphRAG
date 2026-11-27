"""Execution settings for graph-focused evaluations, separate from frozen gold."""
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

from .isolated_graph import IsolatedGraph


def v4_contract(root, benchmark, cfg):
    snapshot = benchmark['graph_snapshot']
    path = (root / snapshot['database']).resolve()
    if not path.is_relative_to((root / 'artifacts/eval/stage-4/benchmark-v3').resolve()):
        raise ValueError('graph_snapshot_outside_frozen_namespace')
    if hashlib.sha256(path.read_bytes()).hexdigest() != snapshot['sha256']:
        raise ValueError('graph_snapshot_modified')
    selected_keys = ('DEEPSEEK_MODEL', 'CLOUD_BGE_MODEL', 'CLOUD_BGE_PROVIDER',
        'LOCAL_RERANKER_PATH', 'LOCAL_RERANKER_PYTHON', 'LOCAL_RERANKER_DEVICE', 'LOCAL_RERANKER_DTYPE',
        'LOCAL_RERANKER_PERSISTENT')
    models = {key: cfg.get(key) for key in selected_keys}
    if not all(cfg.get('DEEPSEEK' + suffix) for suffix in ('_BASE_URL', '_API_KEY', '_MODEL')):
        raise ValueError('generation_not_configured')
    if cfg.get('LOCAL_RERANKER_DEVICE') != 'cuda':
        raise ValueError('gpu_reranker_required')
    files = ('scripts/eval-stage4.py', 'src/papertech/evaluation_runtime.py',
        'src/papertech/isolated_graph.py', 'src/papertech/workflow.py', 'src/papertech/graph_store.py',
        'src/papertech/retrieval.py', 'src/papertech/evidence_context.py', 'src/papertech/entity_aliases.py',
        'src/papertech/providers.py', 'src/papertech/citations.py', 'src/papertech/evaluation.py',
        'src/papertech/evaluation_details.py', 'src/papertech/evaluation_datasets.py',
        'src/papertech/local_models.py', 'src/papertech/rerank_service.py', 'scripts/rerank-service.py')
    return dict(benchmark=benchmark['version'], graph_snapshot=snapshot,
        models=models,
        endpoint_fingerprints={key: hashlib.sha256(cfg.get(key, '').encode()).hexdigest()
            for key in ('DEEPSEEK_BASE_URL', 'CLOUD_BGE_BASE_URL', 'CLOUDFLARE_ACCOUNT_ID', 'NEO4J_URI')},
        dependencies={name: version(name) for name in ('neo4j', 'langsmith', 'langgraph', 'httpx')},
        code_sha256={name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files},
        controls=dict(arms=['Hybrid', 'Hybrid+Graph'], backend='neo4j', graph_backend='isolated_sqlite',
            fulltext_top=20, dense_top=20, fusion_max=40, graph_candidates_max=20,
            graph_seed_chunks=12, graph_seed_entities=40, graph_max_paths=40, graph_hops=2,
            graph_per_node=8, evidence_max=8, evidence_bytes=6000, path_bytes=1200, context_bytes=7200,
            path_budget_mode='additional', generation_max_tokens=2048, thinking='disabled',
            generation_requests_max=2 * sum(c['generate'] for c in benchmark['cases']),
            sampling='provider default; one sample per arm',
            treatment_scope='graph candidates plus up to 1200 additional path bytes; not an equal actual input-token ablation',
            execution_order='alternate which arm goes first', query_vector='one shared Cloudflare batch',
            gold_exclusion='question text only; reference tables and claim unit/path IDs denied by SQLite authorizer'),
        latency='retrieval compute excludes audit upload, generation, and shared embedding batch; request wall time reported separately',
        status='frozen_before_execution')


def open_v4_graph(root, contract):
    snapshot = contract['graph_snapshot']
    return IsolatedGraph(root / snapshot['database'], snapshot['sha256'])
