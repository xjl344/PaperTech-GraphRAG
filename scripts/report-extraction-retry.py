"""Export metadata-only evidence for the explicitly scoped Stage 3 retry."""
import json
from collections import Counter
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.ingest import atomic_json
from papertech.settings import settings


ORIGINAL = '2ec77731331a4875ac6ed256bfebdc62'
RETRIES = ['a29ba1ff8a9e4480974bd2fab772318b', '36c03f4aa7c94e85812a998982a09145']


def main():
    destination = ROOT / 'artifacts/reports/stage-3/retry-diagnostics'
    connection = sqlite3.connect('file:' + (ROOT / 'data/kg.sqlite3').as_posix() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        original = dict(connection.execute('SELECT * FROM kg_runs WHERE run_id=?', (ORIGINAL,)).fetchone())
        failures = [dict(r) for r in connection.execute("SELECT chunk_id,paper_title,status,error_code FROM kg_tasks WHERE run_id=? AND status='failed'", (ORIGINAL,))]
        allowed = {r['chunk_id'] for r in failures}
        runs, attempts, results, verification = [], [], {}, []
        for run_id in RETRIES:
            run = dict(connection.execute('SELECT * FROM kg_runs WHERE run_id=?', (run_id,)).fetchone())
            tasks = [dict(r) for r in connection.execute('SELECT * FROM kg_tasks WHERE run_id=? ORDER BY ordinal', (run_id,))]
            if any(t['chunk_id'] not in allowed for t in tasks):
                raise ValueError('retry_scope_exceeded')
            for task in tasks:
                results[task['chunk_id']] = task
            runs.append(dict(run=run, tasks=tasks))
            for row in connection.execute('SELECT * FROM kg_attempts WHERE run_id=? ORDER BY rowid', (run_id,)):
                diagnostic = json.loads(row['diagnostic_json'])
                diagnostic.pop('raw_response', None)
                attempts.append(dict(run_id=run_id, chunk_id=row['chunk_id'], trace_id=row['trace_id'], **diagnostic))
            verification.append(json.loads((ROOT / 'artifacts/reports/stage-3/runs' / run_id / 'live-verification.json').read_text(encoding='utf-8')))
        if len(results) != 3 or any(t['status'] != 'completed' for t in results.values()):
            raise ValueError('retry_not_fully_recovered')
        if any(v['status'] != 'verified' for v in verification):
            raise ValueError('remote_verification_incomplete')
        rejects = Counter()
        for chunk_id in allowed:
            cache = connection.execute('SELECT rejected_json FROM kg_cache WHERE chunk_id=? AND status=\'completed\' ORDER BY updated_at DESC LIMIT 1', (chunk_id,)).fetchone()
            for rejected in json.loads(cache[0]):
                rejects[rejected['reason']] += 1
        summary = dict(original_run=original, original_failures=failures, runs=runs, attempts=attempts,
                       recovered_chunks=3, final_results=list(results.values()),
                       known_input_tokens=sum(a.get('input_tokens') or 0 for a in attempts),
                       known_output_tokens=sum(a.get('output_tokens') or 0 for a in attempts),
                       unknown_usage_calls=sum(a.get('input_tokens') is None or a.get('output_tokens') is None for a in attempts),
                       valid_candidates=sum(t['candidate_count'] for t in results.values()),
                       program_rejections=dict(rejects), remote_verification=verification,
                       review_counts=dict(connection.execute('SELECT review_status,count(*) FROM kg_claims GROUP BY review_status').fetchall()))
        summary['effective_completed_chunks'] = connection.execute('''
            SELECT count(*) FROM kg_tasks t WHERE t.run_id=? AND EXISTS (
                SELECT 1 FROM kg_cache c WHERE c.chunk_id=t.chunk_id AND c.corpus_id=? AND c.model=?
                AND c.prompt_version=? AND c.schema_version=? AND c.status='completed')''',
            (ORIGINAL, original['corpus_id'], original['model'], original['prompt_version'], original['schema_version'])).fetchone()[0]
        serialized = json.dumps(summary, ensure_ascii=False)
        for key, value in settings(ROOT).items():
            if value and any(word in key.upper() for word in ('KEY', 'PASSWORD', 'TOKEN', 'SECRET')) and value in serialized:
                raise ValueError('configured_secret_detected')
        atomic_json(destination / 'summary.json', summary)
        print(json.dumps({k: summary[k] for k in ('recovered_chunks','known_input_tokens','known_output_tokens','unknown_usage_calls','valid_candidates','program_rejections','review_counts')}, ensure_ascii=False))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
