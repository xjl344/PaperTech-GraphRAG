"""Parent-owned reusable worker. One request at a time; timeout kills, never replays."""
import atexit
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid

_workers = {}
_guard = threading.Lock()


def _resolve_interpreter(interpreter):
    """Resolve Windows venv shim to its base executable + site-packages while keeping -I isolation."""
    path = Path(interpreter)
    cfg_path = path.parent.parent / 'pyvenv.cfg'
    site_dir = path.parent.parent / 'Lib/site-packages'
    if os.name == 'nt' and cfg_path.exists() and site_dir.is_dir():
        for line in cfg_path.read_text(encoding='utf-8', errors='ignore').splitlines():
            key, _, val = line.partition('=')
            if key.strip().lower() == 'executable':
                base = Path(val.strip())
                if base.exists():
                    return str(base), str(site_dir)
    return str(interpreter), None


class Worker:
    def __init__(self, root, cfg):
        self.lock = threading.Lock()
        target = root / '.cache/rerank-services' / uuid.uuid4().hex
        target.mkdir(parents=True)
        job = target / 'config.json'
        batch_size = int(cfg.get('LOCAL_RERANKER_BATCH_SIZE', 4))
        raw_interpreter = cfg.get('LOCAL_RERANKER_PYTHON') or cfg['LOCAL_MODEL_PYTHON']
        interpreter, site_packages = _resolve_interpreter(raw_interpreter)
        payload = dict(model_path=cfg['LOCAL_RERANKER_PATH'],
                       device=cfg.get('LOCAL_RERANKER_DEVICE', 'cuda'),
                       dtype=cfg.get('LOCAL_RERANKER_DTYPE', 'float16'),
                       batch_size=batch_size)
        if site_packages:
            payload['site_packages'] = site_packages
        job.write_text(json.dumps(payload), encoding='utf-8')
        env = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
            env.pop(key, None)
        env.update(PYTHONNOUSERSITE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                   TEMP=str(root / '.cache/temp'), TMP=str(root / '.cache/temp'),
                   PYTHONPYCACHEPREFIX=str(root / '.cache/pycache'))
        self.log = (target / 'worker.log').open('w', encoding='utf-8')
        self.process = subprocess.Popen([interpreter, '-I', '-X', 'utf8', str(root / 'scripts/rerank-service.py'), str(job)],
            cwd=root, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log,
            text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.lines = queue.Queue()
        self.ready = False
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for line in self.process.stdout:
                self.lines.put(line)
        finally:
            self.lines.put(None)

    def receive(self, timeout):
        try:
            line = self.lines.get(timeout=max(.01, timeout))
        except queue.Empty:
            self.close()
            raise TimeoutError('reranker_timeout_no_replay')
        if line is None:
            self.close()
            raise RuntimeError('reranker_worker_exited')
        return json.loads(line)

    def run(self, query, items, timeout):
        started = time.monotonic()
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError('reranker_queue_timeout')
        try:
            if not self.ready:
                if self.receive(timeout-(time.monotonic()-started)).get('status') != 'ready':
                    raise RuntimeError('reranker_start_failed')
                self.ready = True
            if time.monotonic()-started>=timeout:
                self.close()
                raise TimeoutError('reranker_timeout_no_replay')
            self.process.stdin.write(json.dumps(dict(query=query, items=items), ensure_ascii=False) + '\n')
            self.process.stdin.flush()
            response = self.receive(timeout - (time.monotonic() - started))
            if response.get('status') != 'ok':
                raise RuntimeError('reranker_inference_failed:' + response.get('error_code', 'unknown'))
            result = response['result']
            result['elapsed_seconds'] = time.monotonic() - started
            result['persistent'] = True
            return result
        finally:
            self.lock.release()

    def close(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.wait(timeout=5)
        for pipe in (self.process.stdin, self.process.stdout):
            if pipe:
                pipe.close()
        self.log.close()


def rerank(root, cfg, query, items, timeout=300):
    key = (str(root.resolve()), cfg.get('LOCAL_RERANKER_PYTHON') or cfg.get('LOCAL_MODEL_PYTHON'),
           cfg.get('LOCAL_RERANKER_PATH'), cfg.get('LOCAL_RERANKER_DEVICE'), cfg.get('LOCAL_RERANKER_DTYPE'),
           int(cfg.get('LOCAL_RERANKER_BATCH_SIZE', 4)))
    with _guard:
        worker = _workers.get(key)
        if worker is None or worker.process.poll() is not None:
            worker = Worker(root, cfg)
            _workers[key] = worker
    return worker.run(query, items, timeout)


def close_workers():
    for worker in list(_workers.values()):
        worker.close()
    _workers.clear()


atexit.register(close_workers)
