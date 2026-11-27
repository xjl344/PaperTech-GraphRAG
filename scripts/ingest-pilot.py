"""Run the complete frozen pilot through the local ingestion pipeline."""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from papertech.ingest import ingest_batch
from papertech.pdf import configuration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-version', default='pilot-v1')
    parser.add_argument('--parser-version', default='pdf-v1.1')
    parser.add_argument('--force', action='store_true', help='Re-extract and compare; never overwrite different historical output')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('freeze_pilot', ROOT / 'scripts/freeze-pilot.py')
    freeze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze)
    if not __import__('re').fullmatch(r'pilot-v[1-9][0-9]*', args.manifest_version):
        parser.error('Invalid manifest version')
    snapshot = ROOT / 'artifacts/exports' / args.manifest_version
    verification = freeze.verify(snapshot, args.manifest_version)
    manifest = json.loads((snapshot / 'pilot-manifest.json').read_text(encoding='utf-8'))
    cache = ROOT / '.cache/temp'
    cache.mkdir(parents=True, exist_ok=True)
    os.environ['TEMP'] = os.environ['TMP'] = str(cache)
    result = ingest_batch(ROOT, manifest, verification['manifest_sha256'], configuration(args.parser_version), force=args.force)
    print(json.dumps({k: result[k] for k in ('run_id', 'status', 'task_counts', 'pages', 'chunks')}, indent=2))
    return 1 if result['status'] != 'completed' else 0


if __name__ == '__main__':
    sys.exit(main())
