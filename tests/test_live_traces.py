"""Live event ordering, offline recovery, and native usage without paper text."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.live_traces import LiveTraces


class LiveTraceTests(unittest.TestCase):
    def test_offline_recovery_preserves_start_before_finish_and_usage(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.cache') as directory:
            class Client:
                failed = True
                calls = []
                def create_run(inner, **payload):
                    if inner.failed:
                        raise ConnectionError('Bearer secret-must-not-be-persisted')
                    inner.calls.append(('create', payload))
                def update_run(inner, **payload):
                    from datetime import datetime
                    if not isinstance(payload['end_time'], datetime):
                        raise AttributeError('end_time must be a datetime')
                    inner.calls.append(('update', payload))
            client = Client()
            live = LiveTraces(Path(directory), cfg={'LANGSMITH_API_KEY': 'dummy'}, client=client)
            try:
                span = live.start('test-attempt', dict(chunk_id='c1'), kind='llm')
                self.assertEqual(live.conn.execute('SELECT finished FROM spans').fetchone()[0], None)
                self.assertEqual(client.calls, [])
                live.end(span, dict(status='failed'), error='output_limit_reached',
                         usage=dict(input_tokens=50, output_tokens=1200))
                self.assertNotIn('secret-must', json.dumps([dict(r) for r in live.conn.execute('SELECT * FROM events')]))
                client.failed = False
                self.assertEqual(live.flush()['uploaded'], 2)
                self.assertEqual([op for op, p in client.calls], ['create', 'update'])
                self.assertNotIn('end_time', client.calls[0][1])
                self.assertEqual(client.calls[1][1]['outputs']['usage_metadata']['total_tokens'], 1250)
                self.assertEqual(live.flush()['uploaded'], 0)
            finally:
                live.close()

    def test_current_span_is_sent_before_work_starts(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.cache') as directory:
            calls = []
            class Client:
                def create_run(inner, **payload):
                    calls.append('start')
                def update_run(inner, **payload):
                    calls.append('end')
            live = LiveTraces(Path(directory), cfg={'LANGSMITH_API_KEY': 'dummy'}, client=Client())
            try:
                span = live.start('test', {})
                self.assertEqual(calls, ['start'])
                calls.append('work')
                live.end(span, dict(status='completed'))
                self.assertEqual(calls, ['start', 'work', 'end'])
            finally:
                live.close()
