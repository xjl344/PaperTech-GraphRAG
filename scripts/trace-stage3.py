"""Export metadata-only historical Stage 3 spans and explicitly upload to LangSmith."""
import argparse
import copy
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.ingest import atomic_json
from papertech.settings import settings

DEST = ROOT / 'artifacts/reports/stage-3/delegated-review'
TRACE_FORMAT = 'stage3-metadata-v2'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    cfg = settings(ROOT)
    state = json.loads((DEST / 'extraction-state.json').read_text(encoding='utf-8'))
    run = state['run']
    project = cfg.get('LANGSMITH_PROJECT') or 'papertech'
    spans = []
    def span(identity, name, start, end, inputs, outputs, parent=None, error=None):
        run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'papertech-stage3/' + TRACE_FORMAT + '/' + identity))
        when = datetime.fromisoformat(start).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        order = when + run_id
        entry = dict(id=run_id, trace_id=parent['trace_id'] if parent else run_id,
                     dotted_order=parent['dotted_order']+'.'+order if parent else order,
                     name=name, run_type='chain', session_name=project, start_time=start,
                     end_time=end, inputs=inputs, outputs=outputs,
                     extra=dict(metadata=dict(stage='stage-3', metadata_only=True,
                                              trace_format=TRACE_FORMAT,
                                              capture_mode='retrospective_from_persisted_ledger',
                                              model=run['model'], prompt_version=run['prompt_version'],
                                              schema_version=run['schema_version'])))
        if parent:
            entry['parent_run_id'] = parent['id']
        if error:
            entry['error'] = error
        spans.append(entry)
        return entry
    root = span(run['run_id'], 'papertech-stage3-extraction', run['started_at'], run['finished_at'],
                dict(corpus_id=run['corpus_id'], total_chunks=run['total_chunks']),
                {k:run[k] for k in ('status','completed_chunks','reused_chunks','failed_chunks',
                                    'accepted_candidates','rejected_candidates','input_tokens','output_tokens')})
    conn = sqlite3.connect(ROOT / 'data/kg.sqlite3')
    conn.row_factory = sqlite3.Row
    try:
        for task in conn.execute('SELECT * FROM kg_tasks WHERE run_id=? ORDER BY ordinal', (run['run_id'],)):
            stamp = task['started_at'] or run['started_at']
            finish = stamp if task['status']=='reused' else (task['finished_at'] or run['finished_at'])
            entry = span(run['run_id']+'/'+task['chunk_id'], 'extract-chunk', stamp, finish,
                 dict(ordinal=task['ordinal'], chunk_id=task['chunk_id']),
                 {k:task[k] for k in ('status','candidate_count','rejected_count','input_tokens','output_tokens','error_code')},
                 parent=root, error=task['error_code'] if task['status']=='failed' else None)
            if task['status'] != 'reused':
                entry['run_type'] = 'llm'
                entry['extra']['metadata'].update(ls_provider='ollama', ls_model_name=run['model'])
                if task['input_tokens'] is not None and task['output_tokens'] is not None:
                    usage = dict(input_tokens=task['input_tokens'], output_tokens=task['output_tokens'],
                                 total_tokens=task['input_tokens']+task['output_tokens'])
                    entry['outputs']['usage_metadata'] = usage
                    entry['extra']['metadata']['usage_metadata'] = usage
                    entry.update(prompt_tokens=usage['input_tokens'], completion_tokens=usage['output_tokens'],
                                 total_tokens=usage['total_tokens'])
            else:
                entry['extra']['metadata']['cache_hit'] = True
                entry['extra']['metadata']['timing_basis'] = 'cache_reuse_at_run_initialization_no_task_clock'
    finally:
        conn.close()
    results_path = DEST / 'review-results.json'
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding='utf-8'))
        snapshot = json.loads((DEST / 'snapshot.json').read_text(encoding='utf-8'))
        review = span(run['run_id']+'/review', 'papertech-stage3-delegated-review', snapshot['created_at'],
                      max(r['reviewed_at'] for r in results),
                      dict(candidate_count=len(results), reviewer='Codex', review_kind='ai_delegated',
                           policy_version='evidence-review-v1'),
                      dict(approved=sum(r['decision']=='approved' for r in results),
                           rejected=sum(r['decision']=='rejected' for r in results),
                           graph_confirmed=sum(r['graph_status']=='confirmed' for r in results)))
        for result in results:
            span(run['run_id']+'/review/'+result['claim_id'], 'review-and-graph-write',
                 result['reviewed_at'], result['reviewed_at'],
                 dict(claim_id=result['claim_id'], candidate_index=result['index'], review_kind='ai_delegated'),
                 dict(decision=result['decision'], graph_status=result['graph_status']), parent=review,
                 error=result.get('error_code'))
    atomic_json(DEST / 'langsmith-outbox.json', spans)
    status = dict(status='pending_upload' if cfg.get('LANGSMITH_API_KEY') else 'not_configured', trace_format=TRACE_FORMAT,
                  run_count=len(spans), project=project, capture_mode='retrospective',
                  uploaded_verified=0, trace_urls=[],
                  limitations=['No live tracing was attached during extraction.',
                               'Only recorded final task attempts are available; failed attempts may have unknown usage.',
                               'No historical CPU/GPU samples or token streaming were captured.',
                               'Review span times describe persistence, not per-candidate reading duration.'])
    if (args.upload or args.verify_only) and cfg.get('LANGSMITH_API_KEY'):
        # Disable SDK logging: exception text can contain request metadata; persist safe class names only.
        logging.getLogger('langsmith').setLevel(logging.CRITICAL)
        from langsmith import Client
        client = None
        try:
            client = Client(api_key=cfg['LANGSMITH_API_KEY'],
                        api_url=cfg.get('LANGSMITH_ENDPOINT') or 'https://api.smith.langchain.com',
                        timeout_ms=15000, auto_batch_tracing=False)
            if client:
                if args.upload:
                    for start in range(0, len(spans), 100):
                        client.batch_ingest_runs(create=copy.deepcopy(spans[start:start+100]))
                remote = {}
                for entry in spans:
                    if 'parent_run_id' not in entry:
                        for actual in client.list_runs(project_name=project, trace_id=entry['id'],
                                                       select=['id','name','run_type','start_time','end_time','trace_id','parent_run_id',
                                                               'prompt_tokens','completion_tokens']):
                            remote[str(actual.id)] = actual
                expected_ids = {s['id'] for s in spans}
                verified_ids = {key for key, value in remote.items() if value.end_time is not None}
                if expected_ids != verified_ids:
                    atomic_json(DEST / 'remote-verification-mismatch.json',
                                dict(expected_count=len(expected_ids), verified_count=len(verified_ids),
                                     missing_ids=sorted(expected_ids-verified_ids)))
                    raise RuntimeError('Remote run verification incomplete')
                for entry in spans:
                    if 'parent_run_id' not in entry:
                        actual = client.read_run(entry['id'])
                        status['trace_urls'].append(dict(name=entry['name'], url=client.get_run_url(run=actual)))
                status.update(status='uploaded_verified', uploaded_verified=len(verified_ids))
                usage_expected = [s for s in spans if s.get('prompt_tokens') is not None]
                status.update(native_usage_runs_expected=len(usage_expected),
                              native_usage_runs_verified=sum(remote[s['id']].prompt_tokens==s['prompt_tokens'] and
                                                             remote[s['id']].completion_tokens==s['completion_tokens']
                                                             for s in usage_expected))
                if usage_expected:
                    probe = client.read_run(usage_expected[0]['id'])
                    status['native_usage_probe'] = dict(run_type=probe.run_type, prompt_tokens=probe.prompt_tokens,
                                                      completion_tokens=probe.completion_tokens,
                                                      output_usage=(probe.outputs or {}).get('usage_metadata'),
                                                      metadata_usage=(probe.extra or {}).get('metadata',{}).get('usage_metadata'))
        except Exception as exc:
            import traceback
            message = str(exc)
            for key, value in cfg.items():
                if value and any(word in key.upper() for word in ('KEY', 'PASSWORD', 'TOKEN', 'SECRET')):
                    message = message.replace(value, '[REDACTED]')
            status.update(status='upload_unconfirmed', error_code=type(exc).__name__,
                          error_detail=message[:900],
                          error_locations=[dict(file=Path(f.filename).name, line=f.lineno, function=f.name)
                                           for f in traceback.extract_tb(exc.__traceback__)])
        finally:
            if client:
                client.close()
    atomic_json(DEST / 'langsmith-status.json', status)
    print(json.dumps(status, ensure_ascii=False))


if __name__ == '__main__':
    main()
