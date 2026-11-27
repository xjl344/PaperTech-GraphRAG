"""Process isolation, checkpointed vectors, no mutation of shared inference environments."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import uuid

from .corpus import valid_vector
from .rerank_service import _resolve_interpreter


def run_worker(root, cfg, mode, items, query=None, timeout=1800):
    if mode == 'rerank' and cfg.get('LOCAL_RERANKER_PERSISTENT', 'false').lower() == 'true':
        from .rerank_service import rerank
        return rerank(root, cfg, query, items, timeout)
    target = root / '.cache/model-jobs' / uuid.uuid4().hex
    target.mkdir(parents=True)
    output = target / 'result.json'
    raw_interpreter = (cfg.get('LOCAL_RERANKER_PYTHON') or cfg['LOCAL_MODEL_PYTHON']) if mode == 'rerank' else cfg['LOCAL_MODEL_PYTHON']
    interpreter, site_packages = _resolve_interpreter(raw_interpreter)
    job = dict(mode=mode, items=items, output=str(output),
               database=str(root / 'data/embeddings.sqlite3'),
               model_path=cfg['LOCAL_RERANKER_PATH' if mode == 'rerank' else 'LOCAL_BGE_PATH'],
               device=(cfg.get('LOCAL_RERANKER_DEVICE') or cfg.get('LOCAL_MODEL_DEVICE', 'cpu')) if mode == 'rerank' else cfg.get('LOCAL_MODEL_DEVICE', 'cpu'),
               dtype=cfg.get('LOCAL_RERANKER_DTYPE', 'float32') if mode == 'rerank' else 'float32', query=query)
    if site_packages:
        job['site_packages'] = site_packages
    (target / 'job.json').write_text(json.dumps(job, ensure_ascii=False), encoding='utf-8')
    env = dict(os.environ, HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
               TEMP=str(root / '.cache/temp'), TMP=str(root / '.cache/temp'),
               PYTHONPYCACHEPREFIX=str(root / '.cache/pycache'))
    # The project CLI and inference interpreter can use different Python ABIs.
    # Never let the parent's site-packages override the worker's own environment.
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        env.pop(key, None)
    env['PYTHONNOUSERSITE'] = '1'
    with (target / 'worker.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([interpreter, '-I', '-X', 'utf8', str(root / 'scripts/model-worker.py'), str(target / 'job.json')],
                                cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'Local model worker failed; inspect {target.relative_to(root)}/worker.log')
    return json.loads(output.read_text(encoding='utf-8'))


def vector_metadata(root):
    """Read only the embedding model metadata row without deserializing document vectors."""
    path = root / 'data/embeddings.sqlite3'
    if not path.exists():
        raise RuntimeError('Build local embeddings first')
    conn = sqlite3.connect(path)
    try:
        return json.loads(conn.execute("SELECT value FROM metadata WHERE key='model'").fetchone()[0])
    finally:
        conn.close()


def vector_cache(root, load_vectors=True):
    path = root / 'data/embeddings.sqlite3'
    if not path.exists():
        raise RuntimeError('Build local embeddings first')
    conn = sqlite3.connect(path)
    try:
        metadata = json.loads(conn.execute("SELECT value FROM metadata WHERE key='model'").fetchone()[0])
        if not load_vectors:
            return metadata, {}
        rows = conn.execute('SELECT text_hash,vector FROM embeddings WHERE model_id=?', (metadata['model_id'],))
        vectors = {h: valid_vector(json.loads(v)) for h, v in rows}
        return metadata, vectors
    finally:
        conn.close()
