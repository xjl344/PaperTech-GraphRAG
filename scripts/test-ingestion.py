"""Run ingestion tests and persist plain-text plus machine-readable results."""

import hashlib
import io
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_ingest.py')
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
report = ROOT / 'artifacts/reports/stage-1'
report.mkdir(parents=True, exist_ok=True)
(report / 'test-results.txt').write_text(stream.getvalue(), encoding='utf-8')
summary = {'checked_at': datetime.now().astimezone().isoformat(), 'tests_run': result.testsRun,
           'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
           'status': 'passed' if result.wasSuccessful() else 'failed',
           'test_source_sha256': hashlib.sha256((ROOT / 'tests/test_ingest.py').read_bytes()).hexdigest()}
(report / 'test-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(stream.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)
