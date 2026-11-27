"""One loaded local reranker, serialized small-batch inference, no downloads."""
import hashlib
import math
from pathlib import Path
import time


class Reranker:
    def __init__(self, config):
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        self.torch = torch
        self.device = config.get('device', 'cuda')
        self.dtype = config.get('dtype', 'float16')
        if self.device not in ('cpu', 'cuda') or self.dtype not in ('float16', 'float32'):
            raise ValueError('unsupported_device_or_dtype')
        if self.device == 'cuda' and not torch.cuda.is_available():
            raise RuntimeError('cuda_unavailable')
        if self.dtype == 'float16' and self.device != 'cuda':
            raise ValueError('fp16_requires_cuda')
        started = time.monotonic()
        path = Path(config['model_path'])
        fingerprint = hashlib.sha256()
        for file in sorted(x for x in path.iterdir() if x.suffix in ('.bin', '.safetensors', '.json', '.model')):
            fingerprint.update(file.name.encode())
            with file.open('rb') as stream:
                fingerprint.update(hashlib.file_digest(stream, 'sha256').digest())
        fingerprint.update(b'sigmoid-logits-fp16-pair1024-v1' if self.dtype == 'float16' else b'sigmoid-logits-fp32-pair1024-v1')
        self.model_id = fingerprint.hexdigest()
        torch.set_num_threads(4)
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            path, local_files_only=True, torch_dtype=torch.float16 if self.dtype == 'float16' else torch.float32
        ).to(self.device).eval()
        self.load_seconds = time.monotonic() - started
        self.requests = 0

    def run(self, query, items):
        if not isinstance(query, str) or not query.strip() or len(query) > 4000:
            raise ValueError('invalid_rerank_query')
        if not isinstance(items, list) or len(items) > 40 or any(not isinstance(x, dict) or not isinstance(x.get('text'), str) or len(x['text']) > 30000 for x in items):
            raise ValueError('invalid_rerank_candidates')
        torch = self.torch
        if self.device == 'cuda':
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
        started = time.monotonic()
        outputs = []
        # Batch size one bounds activation memory on the 6GB device.
        for item in items:
            encoded = self.tokenizer(query, item['text'], return_tensors='pt', truncation=True, max_length=1024)
            with torch.inference_mode():
                logits = self.model(**{k:v.to(self.device) for k,v in encoded.items()}).logits.float().reshape(-1)
                score = float(torch.sigmoid(logits[0]).cpu())
            if not math.isfinite(score):
                raise ValueError('nonfinite_rerank_score')
            outputs.append(score)
        if self.device == 'cuda':
            torch.cuda.synchronize()
        reused = self.requests > 0
        self.requests += 1
        return dict(outputs=outputs, model_id=self.model_id, device=self.device, dtype=self.dtype,
                    model_reused=reused, request_count=self.requests, load_seconds=self.load_seconds,
                    inference_seconds=time.monotonic() - started, batch_size=1, max_pair_tokens=1024,
                    peak_cuda_memory_bytes=torch.cuda.max_memory_allocated() if self.device == 'cuda' else None)
