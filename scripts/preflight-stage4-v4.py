"""Check live infrastructure and isolated traversal without paid generation."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation_datasets import load_benchmark, write_json
from papertech.evaluation_runtime import v4_contract, open_v4_graph
from papertech.graph_store import GraphStore
from papertech.local_models import run_worker, vector_cache
from papertech.rerank_service import close_workers
from papertech.settings import settings
from papertech.cloud_embeddings import compatible


def main():
    benchmark, digest, _ = load_benchmark(ROOT, 'benchmark-v4')
    cfg = settings(ROOT)
    contract = v4_contract(ROOT, benchmark, cfg)
    metadata, _ = vector_cache(ROOT)
    graph = open_v4_graph(ROOT, contract)
    store = GraphStore(cfg, benchmark['corpus_id'], metadata['model_id'])
    try:
        index = store.inspect()
        if index['counts'] != [dict(chunks=980, papers=14)]:
            raise RuntimeError('index_count_mismatch')
        if len(index['indexes']) != 2 or any(r['state'] != 'ONLINE' for r in index['indexes']):
            raise RuntimeError('indexes_not_ready')
        if not compatible(ROOT, cfg, metadata['model_id']):
            raise RuntimeError('cloud_compatibility_not_verified')
        probes = []
        for question in ('G-Retriever 怎样选择相关子图？', '比较 HippoRAG 与 RoG 的检索机制。', 'ToG-2 怎样检索？'):
            paths = graph.expand_graph([], question=question)
            if not paths:
                raise RuntimeError('isolated_graph_probe_empty')
            probes.append(dict(question=question, paths=len(paths), audit=graph.last_graph_audit))
        warm = run_worker(ROOT, cfg, 'rerank', [dict(text='Source evidence supports retrieval.')],
            query='source evidence', timeout=180)
        if warm.get('device') != 'cuda' or len(warm.get('outputs', [])) != 1:
            raise RuntimeError('gpu_warmup_failed')
        warm.pop('outputs')
        report = dict(status='passed', benchmark_sha256=digest, contract=contract,
            index=index, graph_probes=probes, gpu=warm, generation_calls=0, embedding_api_calls=0)
        write_json(ROOT / 'artifacts/reports/stage-4/benchmark-v4/preflight.json', report)
        print(json.dumps(dict(status='passed', model=cfg['DEEPSEEK_MODEL'], index_chunks=980,
            graph_sha256=graph.sha256, gpu=warm, generation_calls=0), ensure_ascii=False))
    finally:
        store.close()
        graph.close()
        close_workers()


if __name__ == '__main__':
    main()
