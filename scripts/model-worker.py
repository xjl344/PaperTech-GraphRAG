"""Isolated, offline-only local model worker; outputs/checkpoints stay on E:."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time


def process_memory():
    if os.name != 'nt':
        return None
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(k,ctypes.c_size_t) for k in (
            'PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
            'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    counters=Counters()
    counters.cb=ctypes.sizeof(counters)
    handle=ctypes.windll.kernel32.GetCurrentProcess
    handle.restype=wintypes.HANDLE
    get_info=ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    get_info.restype=wintypes.BOOL
    if get_info(handle(),ctypes.byref(counters),counters.cb):
        return dict(peak_working_set_bytes=counters.PeakWorkingSetSize,working_set_bytes=counters.WorkingSetSize)
    return None

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('job')
    args = p.parse_args()
    job = json.loads(Path(args.job).read_text(encoding='utf-8'))
    if job.get('site_packages'):
        import site
        site.addsitedir(job['site_packages'])
    import torch
    from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
    torch.set_num_threads(min(8, os.cpu_count() or 4))
    started = time.monotonic()
    model_path = Path(job['model_path'])
    files = sorted(x for x in model_path.iterdir() if x.suffix in ('.bin', '.safetensors', '.json', '.model'))
    fingerprint = hashlib.sha256()
    for path in files:
        fingerprint.update(path.name.encode())
        with path.open('rb') as stream:
            fingerprint.update(hashlib.file_digest(stream, 'sha256').digest())
    dtype_name = job.get('dtype', 'float32')
    if dtype_name not in ('float32', 'float16'):
        raise ValueError('Unsupported inference dtype')
    strategy = b'sigmoid-logits-fp16-pair1024-v1' if dtype_name == 'float16' else b'sigmoid-logits-fp32-pair1024-v1'
    fingerprint.update(strategy if job['mode']=='rerank' else b'cls-l2-fp32-noinstruction-v1')
    model_id = fingerprint.hexdigest()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    device = job.get('device', 'cpu')
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA explicitly requested but unavailable; install CUDA-enabled PyTorch in the configured inference environment')
    if dtype_name == 'float16' and (device != 'cuda' or job['mode'] != 'rerank'):
        raise ValueError('FP16 is enabled only for CUDA reranking; document embeddings retain FP32')
    factory = AutoModelForSequenceClassification if job['mode'] == 'rerank' else AutoModel
    model = factory.from_pretrained(model_path, local_files_only=True, use_safetensors=None).to(device=device, dtype=torch.float16 if dtype_name == 'float16' else torch.float32).eval()
    metadata = dict(model_id=model_id, device=device, dtype=dtype_name, torch=torch.__version__, pooling='sigmoid(logits)' if job['mode']=='rerank' else 'CLS+L2',
                    dimension=1024, max_length=8192, truncation=False)
    if job['mode'] == 'build':
        conn = sqlite3.connect(job['database'], timeout=30)
        conn.execute('CREATE TABLE IF NOT EXISTS embeddings (model_id TEXT, text_hash TEXT, vector TEXT, tokens INTEGER, PRIMARY KEY(model_id,text_hash))')
        conn.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)')
        conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', ('model', json.dumps(metadata)))
        conn.commit()
        rows = job['items']
    else:
        rows = job['items']
    outputs, cached, token_lengths = [], 0, []
    for index, item in enumerate(rows):
        if job['mode'] == 'build' and conn.execute('SELECT 1 FROM embeddings WHERE model_id=? AND text_hash=?', (model_id, item['text_sha256'])).fetchone():
            cached += 1
            continue
        if job['mode'] == 'rerank':
            encoded = tokenizer(job['query'], item['text'], return_tensors='pt', truncation=True, max_length=1024)
        else:
            encoded = tokenizer(item['text'], return_tensors='pt', truncation=False)
            if encoded['input_ids'].shape[1] > 8192:
                raise ValueError('Embedding input exceeds model capacity; refusing silent truncation')
        length = encoded['input_ids'].shape[1]
        token_lengths.append(length)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        with torch.inference_mode():
            result = model(**encoded)
            if job['mode'] == 'rerank':
                value = float(torch.sigmoid(result.logits.float().reshape(-1)[0]).cpu())
            else:
                vector = torch.nn.functional.normalize(result.last_hidden_state[:, 0].float(), p=2, dim=1)[0]
                if vector.numel() != 1024 or not bool(torch.isfinite(vector).all()) or float(vector.norm()) < 1e-12:
                    raise ValueError('Invalid local model output')
                value = vector.cpu().tolist()
        if job['mode'] == 'build':
            conn.execute('INSERT OR REPLACE INTO embeddings VALUES (?,?,?,?)', (model_id, item['text_sha256'], json.dumps(value), length))
            conn.commit()
        else:
            outputs.append(value)
        if (index + 1) % 10 == 0 or index == 0:
            print(json.dumps(dict(done=index+1, total=len(rows), cached=cached, elapsed=round(time.monotonic()-started, 2))), flush=True)
    metadata.update(elapsed_seconds=time.monotonic()-started, cpu_seconds=time.process_time(), memory=process_memory(),
                    peak_cuda_memory_bytes=torch.cuda.max_memory_allocated() if device == 'cuda' else None,
                    threads=torch.get_num_threads(), items=len(rows), cached=cached,
                    max_observed_tokens=max(token_lengths, default=None), outputs=outputs,
                    rerank_max_length=1024 if job['mode'] == 'rerank' else None)
    Path(job['output']).write_text(json.dumps(metadata), encoding='utf-8')
    print(json.dumps({k:v for k,v in metadata.items() if k != 'outputs'}), flush=True)


if __name__ == '__main__':
    main()
