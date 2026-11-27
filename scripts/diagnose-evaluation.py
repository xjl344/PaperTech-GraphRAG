"""Inspect each recorded answer and attach diagnostics without replaying models."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.citations import validate_answer
from papertech.evaluation_datasets import load_benchmark, stable_id, write_json
from papertech.settings import settings


def diagnose(row, case, bench):
    evidence = row.get('evidence') or []
    selected_papers = sorted({item['paper_id'] for item in evidence})
    required = sorted({bench['units'][key]['paper_id'] for key in case['units']})
    draft = None
    if isinstance(row.get('raw'), str):
        try:
            value = json.loads(row['raw'])
            if isinstance(value, dict):
                draft = {key: value[key] for key in ('answer', 'citations', 'status') if key in value}
        except (ValueError, TypeError):
            pass
    validation = dict(status='not_generated', reason=None)
    if row.get('raw'):
        try:
            validate_answer(row['raw'], evidence)
            validation['status'] = 'passed'
        except Exception as exc:
            # No HTTP responses or credentials enter this diagnostic payload.
            validation.update(status='failed', error_type=type(exc).__name__,
                reason=str(exc)[:180] if isinstance(exc, ValueError) and type(exc).__name__ == 'ValueError' else 'generated_schema_validation_failed')
    if draft:
        inline = set(re.findall(r'\[([^\[\]\n]+)\]', draft.get('answer', '')))
        declared = {c.get('chunk_id') for c in draft.get('citations', []) if isinstance(c, dict)}
        allowed = {item['chunk_id'] for item in evidence}
        validation.update(undeclared_inline_references=sorted(inline - declared),
            declared_but_not_inline=sorted(declared - inline), unknown_chunk_references=sorted(declared - allowed))
    result = dict(case_id=case['id'], arm=row['arm'], program_status=row['status'],
        citation_protocol=validation,
        source_papers=dict(required=required, selected=selected_papers,
            required_papers_missing=sorted(set(required) - set(selected_papers)),
            selected_count=len(selected_papers), required_papers_present=set(required).issubset(selected_papers)),
        model_draft=draft if row['status'] == 'citation_error' else None,
        draft_notice='未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。' if row['status'] == 'citation_error' else None,
        review_kind='程序协议与来源覆盖诊断；非独立人工语义评分')
    if 'criterion_source_coverage' in row:
        result['criterion_source_coverage'] = row['criterion_source_coverage']
        ranked = {c['chunk_id'] for c in row.get('ranked') or []}
        selected = {e['chunk_id'] for e in evidence}
        channel_rows = row.get('candidate_channels') or []
        units = []
        for key in case['units']:
            pool = set(bench['units'][key]['known_support_chunks'])
            channels = {channel: [c['chunk_id'] for c in channel_rows
                if c['channel'] == channel and c['chunk_id'] in pool]
                for channel in ('fulltext', 'dense', 'graph')}
            stage = ('selected' if selected & pool else 'evidence_selection_or_budget'
                if ranked & pool else 'fusion_candidate_limit' if any(channels.values()) else 'not_recalled')
            units.append(dict(unit_id=key, required_fact=bench['units'][key]['answer_point'],
                channel_matches=channels, ranked_matches=sorted(ranked & pool),
                selected_matches=sorted(selected & pool), source_gap_stage=stage))
        result['source_gap_stages'] = units
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', default='benchmark-v2')
    parser.add_argument('--run-summary', type=Path, required=True)
    parser.add_argument('--upload', action='store_true')
    args = parser.parse_args()
    bench, digest, _ = load_benchmark(ROOT, args.benchmark)
    summary = json.loads(args.run_summary.read_text(encoding='utf-8'))
    if summary['benchmark_sha256'] != digest:
        raise ValueError('benchmark_mismatch')
    cases = {case['id']: case for case in bench['cases']}
    records = [diagnose(row, cases[row['case_id']], bench) for row in summary['results']]
    review_path = args.run_summary.parent / 'source-review.json'
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding='utf-8'))
        for record in records:
            note = review['cases'].get(record['case_id'], {}).get(record['arm'])
            if note:
                record['source_review'] = dict(origin=review['review_origin'], note=note)
    target = args.run_summary.parent / 'per-question-diagnostics.json'
    write_json(target, dict(benchmark=args.benchmark, run_id=summary['run_id'], records=records))
    lines = ['# 逐题协议与来源诊断', '',
        '以下检查重读已保存的输出，没有重新调用模型。引用通过只表示协议有效；来源齐全也不代表结论都受原文支持。', '',
        '| 题目 | 组别 | 程序状态 | 引用协议 | 原题所需论文均入选 | 缺少来源论文数 |', '|---|---|---|---|---|---:|']
    for item in records:
        lines.append('| ' + ' | '.join([item['case_id'], item['arm'], item['program_status'], item['citation_protocol']['status'],
            str(item['source_papers']['required_papers_present']), str(len(item['source_papers']['required_papers_missing']))]) + ' |')
    lines += ['', '## 引用失败细节', '']
    for item in records:
        if item['citation_protocol']['status'] == 'failed':
            lines += [f"### {item['case_id']} / {item['arm']}", '',
                '```json', json.dumps(item['citation_protocol'], ensure_ascii=False, indent=2), '```', '',
                item['draft_notice'] or '', '', (item['model_draft'] or {}).get('answer', '没有可解析草稿'), '']
    (args.run_summary.parent / 'diagnostics.md').write_text('\n'.join(lines), encoding='utf-8')
    verified = 0
    if args.upload:
        from langsmith import Client
        logging.getLogger('langsmith').setLevel(logging.CRITICAL)
        cfg = settings(ROOT)
        client = Client(api_key=cfg['LANGSMITH_API_KEY'], api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
            timeout_ms=20000, auto_batch_tracing=False)
        try:
            jobs = []
            run_ids = [stable_id(digest, summary['run_id'], record['case_id'], record['arm']) for record in records]
            runs = {}
            for offset in range(0, len(run_ids), 50):
                batch = run_ids[offset:offset + 50]
                runs.update({str(run.id): run for run in client.list_runs(run_ids=batch, limit=len(batch),
                    select=['id', 'session_id', 'start_time'])})
            for record in records:
                rid = stable_id(digest, summary['run_id'], record['case_id'], record['arm'])
                run = runs[rid]
                # Feedback lives alongside the recorded Experiment result and never overwrites it.
                fid = stable_id(rid, 'protocol_and_source_diagnostics_v1')
                jobs.append(dict(run_id=rid, key='protocol_and_source_diagnostics', value=record,
                    feedback_id=fid, session_id=run.session_id, start_time=run.start_time,
                    comment='逐题引用协议、必要论文来源与未接受草稿；不作为答案准确率。', stop_after_attempt=1))
            ids = {job['feedback_id'] for job in jobs}
            existing = {str(item.id): item for item in client.list_feedback(run_ids=[job['run_id'] for job in jobs],
                feedback_key=['protocol_and_source_diagnostics'])}
            for job in jobs:
                if job['feedback_id'] in existing and existing[job['feedback_id']].value != job['value']:
                    raise ValueError('diagnostic_feedback_modified')
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), [job for job in jobs if job['feedback_id'] not in existing]))
            received = {str(item.id): item for item in client.list_feedback(run_ids=[job['run_id'] for job in jobs],
                feedback_key=['protocol_and_source_diagnostics'])}
            if not ids.issubset(received) or any(received[job['feedback_id']].value != job['value'] for job in jobs):
                raise ValueError('diagnostic_feedback_readback_mismatch')
            verified = len(ids)
        finally:
            client.close()
    result = dict(records=len(records), citation_failures=sum(item['citation_protocol']['status'] == 'failed' for item in records),
        two_source_requirements_met=sum(item['source_papers']['required_papers_present'] and cases[item['case_id']]['category'] == 'cross' for item in records),
        remote_diagnostics_verified=verified, model_replays=0)
    write_json(args.run_summary.parent / 'diagnostic-verification.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
