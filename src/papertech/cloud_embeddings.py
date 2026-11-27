"""Fail-closed compatibility gate for existing local BGE-M3 document vectors."""
import json
import time
import hashlib
import re

from .corpus import valid_vector
from .ingest import atomic_json
from .local_models import run_worker, vector_cache

VERSION = 'bge-query-compatibility-v1'
PROBES = ['Knowledge graph retrieval augmented generation.', '知识图谱与多跳推理。',
          'HippoRAG uses personalized PageRank for retrieval.', 'No evidence means no supported answer.']


def configured(cfg):
    if cfg.get('CLOUD_BGE_PROVIDER') == 'cloudflare':
        return (bool(re.fullmatch(r'[a-fA-F0-9]{32}', cfg.get('CLOUDFLARE_ACCOUNT_ID', '')))
                and bool(cfg.get('CLOUDFLARE_AUTH_TOKEN')) and cfg.get('CLOUD_BGE_MODEL') == '@cf/baai/bge-m3')
    return all(cfg.get('CLOUD_BGE' + suffix) for suffix in ('_BASE_URL', '_API_KEY', '_MODEL'))


def endpoint(cfg):
    # Keep account IDs out of reports; bind approval to the actual account nonetheless.
    if cfg.get('CLOUD_BGE_PROVIDER') == 'cloudflare':
        return 'https://api.cloudflare.com/client/v4/ai/run'
    return cfg.get('CLOUD_BGE_BASE_URL', '').rstrip('/')


def account_fingerprint(cfg):
    if cfg.get('CLOUD_BGE_PROVIDER') == 'cloudflare':
        return hashlib.sha256(cfg.get('CLOUDFLARE_ACCOUNT_ID', '').encode()).hexdigest()
    return None


def query_mode(cfg, requested=None):
    selected = requested or cfg.get('QUERY_EMBEDDING_MODE', 'local')
    if selected not in ('auto', 'local', 'cloud', 'none'):
        raise ValueError('Invalid QUERY_EMBEDDING_MODE')
    if selected == 'auto':
        return 'cloud' if configured(cfg) else 'local'
    return selected


def compatible(root, cfg, local_model_id):
    try:
        record = json.loads((root / 'data/cloud-compatibility.json').read_text(encoding='utf-8'))
        age = time.time() - record['verified_timestamp']
        return (record.get('passed') is True and record.get('gate_version') == VERSION
                and record.get('local_model_id') == local_model_id
                and record.get('endpoint') == endpoint(cfg)
                and record.get('account_fingerprint') == account_fingerprint(cfg)
                and record.get('model') == cfg.get('CLOUD_BGE_MODEL')
                and record.get('provider') == (cfg.get('CLOUD_BGE_PROVIDER') or 'deepinfra')
                and 0 <= age < 30 * 86400)
    except (OSError, ValueError, TypeError, KeyError):
        return False


def check_compatibility(root, cfg, provider, request_id, runner=None):
    path = root / 'data/cloud-compatibility.json'
    result = dict(passed=False, status='checking', gate_version=VERSION, threshold=.999,
                  provider=cfg.get('CLOUD_BGE_PROVIDER') or 'deepinfra',
                  endpoint=endpoint(cfg), account_fingerprint=account_fingerprint(cfg), model=cfg.get('CLOUD_BGE_MODEL'),
                  verified_timestamp=0, probe_count=len(PROBES), sends_paper_text=False)
    # Invalidate old approval before I/O, including exceptions/interruption or a missing key.
    atomic_json(path, result)
    try:
        if not provider.configured('CLOUD_BGE'):
            result['status'] = 'not_configured'
        else:
            indexed, _ = vector_cache(root)
            local = (runner or run_worker)(root, cfg, 'query', [dict(text=t) for t in PROBES], timeout=300)
            if local['model_id'] != indexed['model_id']:
                raise ValueError('local_model_differs_from_index')
            if len(local['outputs']) != len(PROBES):
                raise ValueError('local_probe_count_mismatch')
            normalized = [valid_vector(v) for v in local['outputs']]
            cloud = provider.embedding(request_id, PROBES)
            if len(cloud) != len(PROBES):
                raise ValueError('cloud_probe_count_mismatch')
            cosines = [sum(a*b for a,b in zip(v, valid_vector(w))) for v,w in zip(normalized, cloud)]
            passed = min(cosines) >= result['threshold']
            result.update(passed=passed, status='passed' if passed else 'incompatible', cosines=cosines,
                          local_model_id=local['model_id'], verified_timestamp=time.time() if passed else 0,
                          note='Four probe gate, not a retrieval-quality evaluation; expires in 30 days.')
    except Exception as exc:
        # Do not copy HTTP error messages or credentials into reports.
        result.update(status='validation_error', error_code=type(exc).__name__)
    atomic_json(path, result)
    return result
