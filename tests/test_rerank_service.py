"""Worker lifetime guarantees independent of GPU availability."""
from pathlib import Path
import queue
import unittest
from unittest.mock import Mock,patch
from papertech import rerank_service as service


class RerankServiceTests(unittest.TestCase):
    def test_expired_request_is_not_sent_after_waiting_for_lock(self):
        worker=service.Worker.__new__(service.Worker)
        worker.lock=Mock(); worker.lock.acquire.return_value=True
        worker.ready=True; worker.process=Mock(); worker.close=Mock()
        with patch.object(service.time,'monotonic',side_effect=[0,11]):
            with self.assertRaisesRegex(TimeoutError,'no_replay'):
                worker.run('question',[dict(text='source')],timeout=10)
        worker.process.stdin.write.assert_not_called()
        worker.close.assert_called_once()
        worker.lock.release.assert_called_once()

    def test_receive_timeout_closes_worker_without_replaying(self):
        worker=service.Worker.__new__(service.Worker)
        worker.lines=queue.Queue()
        worker.close=Mock()
        with self.assertRaisesRegex(TimeoutError,'no_replay'):
            worker.receive(.01)
        worker.close.assert_called_once()

    def test_same_configuration_reuses_worker_across_workflow_instances(self):
        cfg=dict(LOCAL_RERANKER_PYTHON='python',LOCAL_RERANKER_PATH='model',
                 LOCAL_RERANKER_DEVICE='cuda',LOCAL_RERANKER_DTYPE='float16')
        with patch.dict(service._workers,{},clear=True),patch.object(service,'Worker') as constructor:
            worker=constructor.return_value
            worker.process.poll.return_value=None
            service.rerank(Path.cwd(),cfg,'first',[dict(text='source')])
            service.rerank(Path.cwd(),dict(cfg),'second',[dict(text='source')])
            constructor.assert_called_once()
            self.assertEqual(worker.run.call_count,2)

    def test_exited_worker_is_replaced_on_next_distinct_request(self):
        cfg=dict(LOCAL_RERANKER_PYTHON='python',LOCAL_RERANKER_PATH='model')
        with patch.dict(service._workers,{},clear=True),patch.object(service,'Worker') as constructor:
            constructor.return_value.process.poll.return_value=1
            service.rerank(Path.cwd(),cfg,'first',[])
            service.rerank(Path.cwd(),cfg,'second',[])
            self.assertEqual(constructor.call_count,2)
