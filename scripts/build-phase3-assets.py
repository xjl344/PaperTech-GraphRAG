"""Build Phase-3 assets: 14-paper verbatim Method Cards + local BGE-M3 claim/slot vectors."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from papertech.method_cards import build_auxiliary_vectors, build_method_cards
from papertech.settings import settings

GRAPH_PATH = ROOT / 'artifacts/eval/stage-4/benchmark-v3/isolated-graph.sqlite3'
CARDS_PATH = ROOT / 'artifacts/exports/pilot-v1/method-cards-v1.json'


def main():
    cfg = settings(ROOT)
    if CARDS_PATH.exists():
        print(json.dumps(dict(method_cards='reused_existing', path=str(CARDS_PATH)), ensure_ascii=False), flush=True)
    else:
        payload, digest = build_method_cards(ROOT, cfg, CARDS_PATH)
        print(json.dumps(dict(method_cards='built', papers=payload['paper_count'],
                              rejected_citations=payload['total_rejected_citations'], sha256=digest), ensure_ascii=False), flush=True)
    vec_summary = build_auxiliary_vectors(ROOT, cfg, GRAPH_PATH, CARDS_PATH)
    print(json.dumps(dict(auxiliary_vectors=vec_summary), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
