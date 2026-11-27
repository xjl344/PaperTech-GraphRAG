from unittest import TestCase
from unittest.mock import patch

from papertech.rerank_window_diagnostic import rerank_inputs


class FixedCandidateWindowTests(TestCase):
    def test_score_all_windows_without_gold_and_keep_candidate_identity(self):
        candidates=[dict(chunk_id='a',score=.2),dict(chunk_id='b',score=.1)]
        chunks={'a':dict(text='alpha beta'),'b':dict(text='gamma')}
        windows={'a':[dict(text='alpha',start_char=0,end_char=5),dict(text='beta',start_char=6,end_char=10)],
            'b':[dict(text='gamma',start_char=0,end_char=5)]}
        with patch('papertech.rerank_window_diagnostic.run_worker',return_value=dict(outputs=[.1,.8,.6])) as worker:
            result=rerank_inputs(None,{},'query',candidates,chunks,windows,'Quote-window')
        self.assertEqual([r['chunk_id'] for r in result['ranked']],['a','b'])
        self.assertEqual(result['ranked'][0]['rerank_score'],.8)
        self.assertEqual(result['ranked'][0]['winning_window']['text'],'beta')
        self.assertEqual(result['model_pairs'],3)
        self.assertFalse(result['reference_information_used'])
        self.assertEqual(worker.call_args.kwargs['query'],'query')
        self.assertEqual(worker.call_args.args[3],[dict(text='alpha'),dict(text='beta'),dict(text='gamma')])

    def test_whole_block_uses_original_text_for_every_candidate(self):
        candidates=[dict(chunk_id='a',score=.2),dict(chunk_id='b',score=.1)]
        chunks={'a':dict(text='full alpha text'),'b':dict(text='full beta text')}
        with patch('papertech.rerank_window_diagnostic.run_worker',return_value=dict(outputs=[.2,.9])) as worker:
            result=rerank_inputs(None,{},'query',candidates,chunks,{},'Whole-block')
        self.assertEqual(set(r['chunk_id'] for r in result['ranked']),{'a','b'})
        self.assertEqual(result['ranked'][0]['chunk_id'],'b')
        self.assertEqual(result['model_pairs'],2)
        self.assertEqual(worker.call_args.args[3],[dict(text='full alpha text'),dict(text='full beta text')])
