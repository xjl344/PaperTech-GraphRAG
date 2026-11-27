"""Verify/export saved path-quota results without any model calls."""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import DetailedEvaluationDataset

spec = importlib.util.spec_from_file_location('quota_eval', ROOT/'scripts/eval-extra-path-budget.py')
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def explain(recorder, summary, folder):
    outputs, _, notes = evaluator.export(recorder, summary)
    lines = ['# 16 题路径预算逐题归因', '',
        '原文始终固定 6000 字节，额外增加路径预算；本表是程序证据归因，不是答案语义评分。', '',
        '0 保持原文优先、路径使用剩余空间；800/1200 为额外路径预算。三组原文逐块相同，总上限为 6000/6800/7200。', '',
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
                fingerprint = hashlib.sha256(json.dumps(dict(question=row['question'], evidence=row['evidence'],
                    paths=row['retrieval_summary']['prompt_graph_paths'], limitations=row['limitations']),
                    ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                assert fingerprint == row['prompt_fingerprint']
                # Every accepted citation must belong to an actual selected original text block.
                assert all(c['chunk_id'] in {e['chunk_id'] for e in row['evidence']} for c in row['citations'])
        explain(recorder, summary, folder)
        base = {r['case_id']:r for r in summary['results'] if r['arm']=='Path-0'}
        for arm in evaluator.ARMS:
            assert all(r['evidence'] == base[r['case_id']]['evidence'] for r in summary['results'] if r['arm']==arm)
            expected_changed = [r['case_id'] for r in summary['results'] if r['arm']==arm
                and r['prompt_fingerprint'] != base[r['case_id']]['prompt_fingerprint']]
            assert expected_changed == comparison['changed_input_questions'][arm]
        checks['local'] = dict(verified=True, groups=3, rows=48, baseline_questions_reproduced=16,
            identical_originals_in_all_arms=True, changed_input_questions=comparison['changed_input_questions'])
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
