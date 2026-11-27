"""Verify saved context-budget replay artifacts and remote statistics; no models."""
import argparse
import hashlib
import importlib.util
import json
import logging
import math
from pathlib import Path
import sys
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import load_benchmark,write_json
from papertech.evaluation import support_metrics
from papertech.evaluation_details import DetailedEvaluationDataset
from papertech.evidence_context import assemble,content_bytes,path_prompt
from papertech.entity_aliases import is_comparison


def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary',type=Path,required=True)
    parser.add_argument('--remote',action='store_true')
    args=parser.parse_args()
    folder=args.run_summary.resolve().parent
    summary=read(folder/'summary.json');report=read(folder/'comparison.json');execution=read(folder/'execution-contract.json')
    spec=importlib.util.spec_from_file_location('budget_eval',ROOT/'scripts/eval-context-budget.py')
    evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
    recorder=DetailedEvaluationDataset(ROOT,summary['benchmark'])
    remote_stats=[]
    try:
        _,contract,parent=evaluator.baseline()
        assert summary['status']=='completed' and summary['model_calls']==summary['generation_calls']==0
        assert summary['new_generation_tokens'] is None
        assert len(summary['results'])==48 and len(recorder.bench['cases'])==16
        assert report['dataset_sync']==summary['dataset_sync']
        assert execution['benchmark_sha256']==summary['benchmark_sha256']==recorder.digest
        assert execution['code_sha256']==summary['code_sha256']
        correction_path=folder/'report-correction.json'
        correction=read(correction_path) if correction_path.exists() else None
        for name,digest in execution['code_sha256'].items():
            if sha(ROOT/name)==digest:
                continue
            assert name=='scripts/eval-context-budget.py' and correction
            assert correction['kind']=='report_only_literal_correction' and correction['case_id']=='R12'
            assert correction['algorithm_changed'] is False and correction['model_calls']==0
            assert correction['original_sha256']==digest and correction['corrected_sha256']==sha(ROOT/name)
            assert correction['execution_contract_sha256']==sha(folder/'execution-contract.json')
            old='原文优先恢复被路径占位挤出的 LPKG 支持块'.encode()
            new='原文优先恢复被路径占位挤出的 Tree-of-Traversals 的 totmusic 支持块'.encode()
            current=(ROOT/name).read_bytes()
            assert current.count(new)==1
            assert hashlib.sha256(current.replace(new,old)).hexdigest()==digest
        originals={r['case_id']:r for r in parent['results'] if r['arm']=='Graph-after'}
        cases={case['id']:case for case in recorder.bench['cases']}
        for row in summary['results']:
            assert read(folder/(row['case_id']+'-'+row['arm']+'.json'))==row
            original=originals[row['case_id']]
            assert row['ranked']==original['ranked'] and row['graph_paths']==original['graph_paths']
            assert row['parent_generation']==original['parent_generation']
            assert not row['provider_calls'] and row['usage'] is None and row['status']=='evidence_only'
            allowed={e['chunk_id']:e for e in row['evidence']}
            for e in row['evidence']:
                chunk=recorder.chunks[e['chunk_id']]
                assert e['quote']==chunk['text'] and e['paper_id']==chunk['paper_id'] and e['source_spans']==chunk['source_spans']
            reference_format='references' if row['arm']=='Compact-paths' else 'full'
            assert [path_prompt(path,allowed,reference_format) for path in row['generation_paths']]==row['prompt_graph_paths']
            exact=content_bytes(row['evidence'],row['prompt_graph_paths'])
            assert exact==row['retrieval_summary']['serialized_content_bytes'] and exact<=6000
            assert row['retrieval_summary']['context_bytes']<=6000 and len(row['evidence'])<=8 and len(row['generation_paths'])<=4
            case=cases[row['case_id']]
            assert row['metrics']==support_metrics([r['chunk_id'] for r in row['ranked']],list(allowed),
                [recorder.bench['units'][key] for key in case['units']])
            if row['arm']=='Budget-before':
                assert row['evidence']==original['evidence'] and row['generation_paths']==original['generation_paths']
            else:
                assert {e['chunk_id'] for e in original['evidence']}.issubset(allowed)
                evidence,paths,detail=assemble(row['ranked'],recorder.chunks,row['graph_paths'],row['question'],
                    is_comparison(row['question']),path_format=reference_format)
                assert evidence==row['evidence'] and paths==row['generation_paths'] and detail==row['retrieval_summary']
        for cid in cases:
            rows={r['arm']:r for r in summary['results'] if r['case_id']==cid}
            assert rows['Evidence-first']['evidence']==rows['Compact-paths']['evidence']
        for version in ('benchmark-v1','benchmark-v2','benchmark-source-coverage-v1'):
            load_benchmark(ROOT,version)
        if args.remote:
            logging.getLogger('langsmith').setLevel(logging.CRITICAL)
            dataset=recorder.sync_dataset()
            client=recorder.client
            expected={p['id']:p for p in evaluator.payloads(recorder,summary)}
            for project in summary['dataset_sync']['experiments']:
                wanted={rid:p for rid,p in expected.items() if p['_arm']==project['arm']}
                found={str(run.id):run for run in client.list_runs(project_id=project['project_id'],is_root=True)}
                assert set(found)==set(wanted)
                for rid,run in found.items():
                    assert run.outputs==wanted[rid]['outputs'] and str(run.reference_example_id)==wanted[rid]['reference_example_id']
                    assert run.start_time==datetime.fromisoformat(wanted[rid]['start_time']) and run.end_time==datetime.fromisoformat(wanted[rid]['end_time'])
                    assert not run.prompt_tokens and not run.completion_tokens
                stats=client.read_project(project_id=project['project_id'],include_stats=True)
                agg=report['aggregates'][project['arm']]
                assert stats.run_count==16 and not stats.prompt_tokens and not stats.completion_tokens
                for key in ('evidence_coverage','required_paper_coverage'):
                    assert stats.feedback_stats[key]['n']==16
                    assert math.isclose(stats.feedback_stats[key]['avg'],agg[key],abs_tol=.000051)
                for key in ('all_required_papers','all_units'):
                    assert math.isclose(stats.feedback_stats[key]['avg'],agg[key]/16,abs_tol=.000051)
                assert stats.feedback_stats['context_budget_diagnostics']['n']==16
                notes=evaluator.diagnostics(summary)
                diagnostic_feedback=list(client.list_feedback(run_ids=list(wanted),feedback_key=['context_budget_diagnostics']))
                assert len(diagnostic_feedback)==16
                for feedback in diagnostic_feedback:
                    case_id=wanted[str(feedback.run_id)]['extra']['metadata']['case_id']
                    assert feedback.value==notes[case_id]
                remote_stats.append(dict(arm=project['arm'],runs=16,prompt_tokens=stats.prompt_tokens,
                    completion_tokens=stats.completion_tokens,feedback_stats=stats.feedback_stats))
        dashboard=read(folder/'dashboard-verification.json');assert dashboard['passed']
        raw=(folder/'test-results.txt').read_bytes()
        tests=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
        assert 'Ran 105 tests' in tests and tests.strip().endswith('OK')
        result=dict(status='verified',verified_at=datetime.now(timezone.utc).isoformat(),run_id=summary['run_id'],
            questions=16,results=48,arms=summary['arms'],benchmark_sha256=recorder.digest,model_calls=0,new_generation_tokens=None,
            baseline_step1_reproduced=True,parent_run_hash_unchanged=True,candidates_scores_and_retrieved_paths_fixed=True,
            source_quotes_and_locations_valid=True,serialized_content_within_6000_bytes=True,reference_paths_resolve=True,
            evidence_first_does_not_remove_baseline_chunks=True,compact_and_full_select_same_evidence=True,
            final_code_replays_saved_results=True,legacy_benchmark_hashes_valid=True,tests_passed=105,dashboard=dashboard,
            remote_examples_verified=16 if args.remote else None,remote_results_verified=48 if args.remote else None,
            remote_numeric_feedback_verified=480 if args.remote else None,remote_diagnostic_feedback_verified=48 if args.remote else None,
            remote_project_stats=remote_stats,execution_contract_sha256=sha(folder/'execution-contract.json'),
            initial_code_sha256=execution['code_sha256'],final_code_sha256={name:sha(ROOT/name) for name in evaluator.CODE},
            report_only_correction=correction,
            limitations=['有偏失败诊断集，非总体性能估计','未重新检索、重排或生成','R18未恢复、R20来源缺口保留',
                '紧凑路径无额外事实覆盖收益','只测原文与路径字节，非全部Prompt或Token预算','无独立语义评分或浏览器视觉验收'])
        write_json(folder/'delivery-verification.json',result)
        print(json.dumps({key:result[key] for key in ('status','questions','results','model_calls','tests_passed','remote_results_verified')},ensure_ascii=False))
    finally:
        recorder.close()


if __name__=='__main__':main()
