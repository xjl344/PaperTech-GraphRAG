import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
stream=io.StringIO()
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_rag*.py')
result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
target=ROOT/'artifacts/reports/stage-2'
target.mkdir(parents=True,exist_ok=True)
(target/'test-results.txt').write_text(stream.getvalue(),encoding='utf-8')
(target/'test-summary.json').write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),real_cloud_calls=0),indent=2),encoding='utf-8')
print(stream.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)
