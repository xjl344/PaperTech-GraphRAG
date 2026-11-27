"""Backfill missing real LangSmith trace links without rerunning retrieval."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from langsmith import Client
from papertech.evaluation_datasets import write_json
from papertech.retrieval_comparison import RetrievalDataset, make_report
from papertech.settings import settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-directory', type=Path, required=True)
    args = parser.parse_args()
    folder = args.run_directory.resolve()
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    cfg = settings(ROOT)
    client = Client(api_key=cfg['LANGSMITH_API_KEY'],
        api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
        timeout_ms=20000, auto_batch_tracing=False)
    try:
        experiments_path = folder / 'langsmith-experiments.json'
        experiment_data = json.loads(experiments_path.read_text(encoding='utf-8'))
        payloads = {p['extra']['metadata']['request_id']: p for p in experiment_data['runs']}
        missing = [r for r in summary['results'] if not r.get('trace_url')]
        updated = []
        for row in missing:
            remote = client.read_run(row['trace_id'])
            if remote.end_time is None:
                raise ValueError('trace_not_finished')
            url = client.get_run_url(run=remote)
            if not url:
                raise ValueError('trace_url_unavailable')
            row['trace_url'] = url
            write_json(folder / f"{row['case_id']}-{row['arm']}.json", row)
            updated.append(dict(experiment_run_id=payloads[row['request_id']]['id'],
                request_id=row['request_id'], trace_url=url))
        by_arm = {arm: {str(r.id): r for r in client.list_runs(
            project_id=next(e['project_id'] for e in summary['dataset_sync']['experiments'] if e['arm'] == arm),
            is_root=True)} for arm in ('Dense-only', 'Graph-only', 'Hybrid')}
        actual_remote_links = {}
        for row in summary['results']:
            payload = payloads[row['request_id']]
            remote = by_arm[row['arm']].get(payload['id'])
            if remote is None or str(remote.reference_example_id) != payload['reference_example_id']:
                raise ValueError('experiment_run_readback_mismatch')
            actual_remote_links[row['request_id']] = remote.outputs.get('trace_url')
            # Keep the export snapshot faithful to what LangSmith actually stores.
            payload['outputs'] = remote.outputs
        write_json(experiments_path, experiment_data)
        write_json(folder / 'summary.json', summary)
        write_json(folder / 'trace-links.json', dict(run_id=summary['run_id'], links=[dict(
            case_id=r['case_id'], arm=r['arm'], trace_id=r['trace_id'], trace_url=r['trace_url'],
            experiment_run_id=payloads[r['request_id']]['id'],
            experiment_output_contains_trace_url=bool(actual_remote_links[r['request_id']]))
            for r in summary['results']], all_trace_spans_readable=True))
        recorder = RetrievalDataset(ROOT, summary['benchmark'])
        try:
            make_report(recorder, summary, folder)
        finally:
            recorder.close()
        write_json(folder / 'trace-url-backfill.json', dict(updated=len(updated), total=120,
            all_traces_have_urls=all(r.get('trace_url') for r in summary['results']),
            experiment_outputs_missing_trace_url=sum(not value for value in actual_remote_links.values()),
            note='Completed remote experiment runs are immutable; their saved outputs are preserved exactly. Complete trace URLs are indexed locally.'))
        print(json.dumps(dict(updated=len(updated), total=120,
            all_traces_have_urls=all(r.get('trace_url') for r in summary['results']),
            experiment_outputs_missing_trace_url=sum(not value for value in actual_remote_links.values())), ensure_ascii=False))
    finally:
        client.close()


if __name__ == '__main__':
    main()
