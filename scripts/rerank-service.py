"""Private stdio worker owned by the parent process; JSON protocol on stdout only."""
import contextlib
import json
import os
from pathlib import Path
import site
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')


def main():
    with contextlib.redirect_stdout(sys.stderr):
        config = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        if config.get('site_packages'):
            site.addsitedir(config['site_packages'])
        from papertech.rerank_runtime import Reranker
        engine = Reranker(config)
    print(json.dumps(dict(status='ready', model_id=engine.model_id, device=engine.device)), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with contextlib.redirect_stdout(sys.stderr):
                result = engine.run(request['query'], request['items'])
            print(json.dumps(dict(status='ok', result=result)), flush=True)
        except Exception as exc:
            # No raw text or model errors in the protocol.
            print(json.dumps(dict(status='error', error_code=type(exc).__name__)), flush=True)


if __name__ == '__main__':
    main()
