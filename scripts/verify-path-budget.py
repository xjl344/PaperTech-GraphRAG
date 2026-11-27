"""Verify/export saved path-quota results without any model calls."""
import argparse
from copy import deepcopy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import DetailedEvaluationDataset

spec = importlib.util.spec_from_file_location('quota_eval', ROOT/'scripts/eval-path-budget.py')
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def repair_diagnostics(recorder, summary, folder, remote=False):
    """Repair only path display matching; preserve all model inputs and results.

    Original graph nodes have id/canonical fields stripped from prompt nodes.
    Comparing original paths directly to prompt paths falsely marks selected
    paths as rejected. Match the grounded prompt representation instead.
    """
    before = deepcopy(summary)
    changed = []
    for row in summary['results']:
        allowed = {e['chunk_id']: e for e in row['evidence']}
        remaining_prompts = list(row['retrieval_summary']['prompt_graph_paths'])
        for path, detail in zip(row['graph_paths'], row['path_diagnostics']):
            prompt = evaluator.path_prompt(path, allowed)
            reason = ('selected' if prompt is not None and prompt in remaining_prompts
                else 'quota_or_max_paths' if prompt else 'supporting_source_not_selected'
                if any(e['chunk_id'] not in allowed for e in path['evidence']) else 'invalid_quote_provenance')
            if reason == 'selected':
                remaining_prompts.remove(prompt)
            if reason != detail['reason']:
                changed.append(dict(case_id=row['case_id'], arm=row['arm'], index=detail['index'],
                    old_reason=detail['reason'], new_reason=reason))
                detail['reason'] = reason
    correction_path = folder/'report-correction.json'
    if not changed:
        if remote and correction_path.exists():
            publish_corrected_diagnostics(recorder, summary, folder)
        return
    assert summary['status'] == 'completed'
    contract = evaluator.read(folder/'execution-contract.json')
    archive = folder/'execution-source/summary-before-diagnostic-correction.json'
    if archive.exists():
        assert evaluator.read(archive) == before
    else:
        write_json(archive, before)
    for old, new in zip(before['results'], summary['results']):
        assert {k: v for k, v in old.items() if k != 'path_diagnostics'} == {k: v for k, v in new.items() if k != 'path_diagnostics'}
    _, old_payloads, _ = evaluator.export(recorder, before)
    _, new_payloads, _ = evaluator.export(recorder, summary)
    correction = dict(kind='path_diagnostic_display_only', model_calls=0, generation_inputs_changed=False,
        answers_evidence_paths_metrics_timings_usage_unchanged=True,
        explanation='Original nodes include id/canonical but prompt nodes retain only name/type; compare grounded prompt representations.',
        original_script_sha256=contract['code_sha256']['scripts/eval-path-budget.py'],
        corrected_script_sha256=evaluator.sha(ROOT/'scripts/eval-path-budget.py'),
        archived_summary_sha256=evaluator.sha(archive), changes=changed)
    write_json(correction_path, correction)
    for row in summary['results']:
        write_json(folder/(row['case_id']+'-'+row['arm']+'.json'), row)
    write_json(folder/'summary.json', summary)
    evaluator.report(recorder, summary, folder)
    write_json(folder/'langsmith-experiments.json', dict(runs=new_payloads))
    if remote:
        publish_corrected_diagnostics(recorder, summary, folder)


def publish_corrected_diagnostics(recorder, summary, folder):
    correction = evaluator.read(folder/'report-correction.json')
    correction['corrected_script_sha256'] = evaluator.sha(ROOT/'scripts/eval-path-budget.py')
    correction['remote_policy'] = 'Server rejects duplicate run updates (409); create diagnostic-v2 export experiments, preserve original experiments and actual generation timestamps, no new model calls.'
    correction.setdefault('original_dataset_sync', deepcopy(summary['dataset_sync']))
    summary['export_revision'] = 'Diagnostic-v2'
    write_json(folder/'report-correction.json', correction)
    write_json(folder/'summary.json', summary)
    if correction.get('replacement_verified'):
        return
    dataset = recorder.sync_dataset()
    summary['dataset_sync'] = evaluator.sync(recorder, dataset, summary, folder)
    correction['replacement_verified'] = True
    correction['corrected_dataset_sync'] = deepcopy(summary['dataset_sync'])
    write_json(folder/'report-correction.json', correction)
    write_json(folder/'summary.json', summary)
    write_json(folder/'langsmith-status.json', summary['dataset_sync'])
    evaluator.report(recorder, summary, folder)


def explain(recorder, summary, folder):
    outputs, _, notes = evaluator.export(recorder, summary)
    lines = ['# 16 题路径预算逐题归因', '',
        '固定真实候选，三组总预算均为 6000 字节；本表是程序证据归因，不是答案语义评分。', '',
        '0 为原文优先、路径使用剩余空间；800/1200 为专用路径配额，原文预算分别为 5200/4800。', '',
        '[汇总报告](report.md) · [完整回答、原文及 Trace](dashboard.html)', '']
    for case in recorder.bench['cases']:
        cid = case['id']
        lines += ['## '+cid, '', case['question'], '',
            '| 项目 | Path-0 | Path-800 | Path-1200 |', '|---|---|---|---|']
        rows = [outputs[cid, a] for a in evaluator.ARMS]
        for label, fn in [('冻结事实覆盖', lambda r: f"{r['metrics']['evidence_coverage']*100:.1f}%"),
            ('必要来源齐全', lambda r: '是' if r['source_metrics']['all_required_papers'] else '否'),
            ('原文块数', lambda r: str(len(r['evidence']))),
            ('路径数', lambda r: str(len(r['generation_paths']))),
            ('路径字节', lambda r: str(r['retrieval_summary']['graph_context_bytes'])),
            ('未覆盖事实', lambda r: ', '.join(r['missing_required_facts']) or '无'),
            ('程序状态', lambda r: r['status'])]:
            lines.append('| '+label+' | '+' | '.join(fn(r) for r in rows)+' |')
        base = {f['unit_id']: f for f in rows[0]['fact_coverage']}
        for arm in ('Path-800', 'Path-1200'):
            row = outputs[cid, arm]
            change = notes[cid]['changes'][arm]
            lost = [f for f in row['fact_coverage'] if base[f['unit_id']]['selected_covered'] and not f['selected_covered']]
            gained = [f for f in row['fact_coverage'] if not base[f['unit_id']]['selected_covered'] and f['selected_covered']]
            lines += ['', '**'+arm+' 相对 Path-0：**', '',
                '- 新增原文：'+(', '.join(change['added_chunk_ids']) or '无'),
                '- 移除原文：'+(', '.join(change['removed_chunk_ids']) or '无'),
                '- 丢失事实：'+('；'.join(f['unit_id']+'：'+f['required_fact'] for f in lost) or '无'),
                '- 新增事实：'+('；'.join(f['unit_id']+'：'+f['required_fact'] for f in gained) or '无')]
            reasons = {}
            translations = dict(selected='已采用', quota_or_max_paths='配额不足或已达 4 条上限',
                supporting_source_not_selected='支持原文未入选，禁止发送路径', invalid_quote_provenance='引句来源校验未通过')
            for item in row['path_diagnostics']:
                key = translations[item['reason']]
                reasons[key] = reasons.get(key, 0)+1
            lines.append('- 图路径去向：'+('；'.join(k+' '+str(v)+' 条' for k, v in reasons.items()) or '原始快照无图路径'))
        lines += ['', '各组回答 Trace：'+' · '.join('['+arm+']('+str(outputs[cid, arm].get('trace_url'))+')'
            for arm in evaluator.ARMS if outputs[cid, arm].get('trace_url')), '']
    (folder/'per-question-diagnosis.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def check_dashboard(folder):
    # Execute the actual embedded script with a minimal DOM; this is not visual acceptance.
    source = r'''
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(process.argv[2],'utf8');
const source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els={};
const element=id=>els[id]??=( {innerHTML:'',textContent:'',value:'',querySelectorAll(){return []},scrollIntoView(){}} );
const box={document:{getElementById:element}};vm.createContext(box);vm.runInContext(source,box);
const initial=(els.rows.innerHTML.match(/<tr>/g)||[]).length;
if(initial!==16)throw Error('not 16 questions');
let inspected=0;for(const id of vm.runInContext('Object.keys(D.results)',box)){
 box.caseId=id;vm.runInContext('show(caseId)',box);
 if(!els.detail.innerHTML.includes('Path-1200')||!els.detail.innerHTML.includes('Path-800')||!els.detail.innerHTML.includes('Path-0'))throw Error('missing arm');
 if(!els.detail.innerHTML.includes('逐事实支持和缺口'))throw Error('missing fact details');inspected++;
}
els.search.value='R03';vm.runInContext('render()',box);
if((els.rows.innerHTML.match(/<tr>/g)||[]).length!==1)throw Error('search broken');
console.log(JSON.stringify({questions:initial,details_inspected:inspected,search:true,kind:'Node DOM simulation; no visual browser check'}));
'''
    result = subprocess.run(['node', '-', str(folder/'dashboard.html')], input=source,
        capture_output=True, text=True, encoding='utf-8', check=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-summary', type=Path, required=True)
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()
    folder = args.run_summary.resolve().parent
    summary = evaluator.read(args.run_summary)
    recorder = DetailedEvaluationDataset(ROOT, evaluator.VERSION)
    checks = {}
    try:
        repair_diagnostics(recorder, summary, folder, args.remote)
        evaluator.verify(recorder, summary, folder, check_code=True)
        assert summary['status'] == 'completed' and summary['generation_calls'] == 48
        comparison = evaluator.read(folder/'comparison.json')
        for arm in evaluator.ARMS:
            rows = [r for r in summary['results'] if r['arm'] == arm]
            assert evaluator.aggregate(rows) == comparison['aggregates'][arm]
            assert len(rows) == 16 and all(r.get('end_time') for r in rows)
            for row in rows:
                assert evaluator.read(folder/(row['case_id']+'-'+arm+'.json')) == row
                assert sum(d['reason'] == 'selected' for d in row['path_diagnostics']) == len(row['generation_paths'])
                # Every accepted citation must belong to an actual selected original text block.
                assert all(c['chunk_id'] in {e['chunk_id'] for e in row['evidence']} for c in row['citations'])
        explain(recorder, summary, folder)
        checks['local'] = dict(verified=True, groups=3, rows=48, baseline_questions_reproduced=16)
        checks['dashboard'] = check_dashboard(folder)
        if args.remote:
            dataset = recorder.sync_dataset()
            _, payloads, _ = evaluator.export(recorder, summary)
            remote = []
            for experiment in summary['dataset_sync']['experiments']:
                arm = experiment['arm']
                expected = {p['id']: p for p in payloads if p['_arm'] == arm}
                client = recorder.client
                found = {str(r.id): r for r in client.list_runs(project_id=experiment['project_id'], is_root=True)}
                assert set(found) == set(expected)
                for rid, p in expected.items():
                    assert evaluator.plain(found[rid].outputs) == evaluator.plain(p['outputs'])
                    assert str(found[rid].reference_example_id) == p['reference_example_id']
                    assert found[rid].start_time == datetime.fromisoformat(p['start_time'])
                    assert found[rid].end_time == datetime.fromisoformat(p['end_time'])
                feedback = {(str(f.run_id), f.key): f for f in client.list_feedback(run_ids=list(expected))}
                for rid, p in expected.items():
                    for key, value in p['_metrics'].items():
                        assert abs(feedback[rid, key].score-float(value)) <= .000050001
                stats = client.read_project(project_id=experiment['project_id'], include_stats=True)
                agg = comparison['aggregates'][arm]
                assert stats.run_count == 16
                assert stats.prompt_tokens == agg['input_tokens'] and stats.completion_tokens == agg['output_tokens']
                for key in ('evidence_coverage', 'required_paper_coverage', 'evidence_count'):
                    assert stats.feedback_stats[key]['n'] == 16
                    assert abs(stats.feedback_stats[key]['avg']-agg[key]) <= .000050001
                assert abs(stats.feedback_stats['all_required_papers']['avg']-agg['all_required_papers']/16) <= .000050001
                remote.append(dict(arm=arm, runs=16, feedback=len(feedback), prompt_tokens=stats.prompt_tokens,
                    completion_tokens=stats.completion_tokens, statistics_match=True))
            checks['remote'] = dict(verified=True, dataset_url=dataset.url, experiments=remote)
        write_json(folder/'delivery-verification.json', checks)
        print(json.dumps(checks, ensure_ascii=False))
    finally:
        recorder.close()


if __name__ == '__main__':
    main()
