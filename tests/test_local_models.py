"""Protect the Python 3.12 inference worker from Python 3.14 parent packages."""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.local_models import run_worker


class LocalWorkerTests(unittest.TestCase):
    def test_worker_does_not_inherit_parent_python_paths(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.cache') as directory:
            root = Path(directory)
            cfg = dict(LOCAL_MODEL_PYTHON='python312', LOCAL_BGE_PATH='model')
            def execute(command, **kwargs):
                self.assertIn('-I', command)
                for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
                    self.assertNotIn(key, kwargs['env'])
                self.assertEqual(kwargs['env']['PYTHONNOUSERSITE'], '1')
                job = json.loads(Path(command[-1]).read_text(encoding='utf-8'))
                Path(job['output']).write_text(json.dumps(dict(outputs=[[1]], device='cpu')), encoding='utf-8')
                return SimpleNamespace(returncode=0)
            with patch.dict(os.environ, dict(PYTHONPATH='python314-packages', PYTHONHOME='parent-python', PYTHONUSERBASE='parent-user')):
                with patch('papertech.local_models.subprocess.run', side_effect=execute):
                    self.assertEqual(run_worker(root, cfg, 'query', [dict(text='test')])['device'], 'cpu')
