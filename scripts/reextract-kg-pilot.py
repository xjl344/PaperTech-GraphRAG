"""Freshly extract the frozen 120 chunks using 14B and the new KG filters."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.kg_rebuild_extract import run

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--resume', help='resume run ID without repeating completed model calls')
parser.add_argument('--sync-only', action='store_true', help='upload existing results without model calls')
args = parser.parse_args()
if args.sync_only and not args.resume:
    parser.error('--sync-only requires --resume')
run(ROOT, args.resume, args.sync_only)
