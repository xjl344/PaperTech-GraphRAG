"""Stage 3 local semantic graph extraction, review, and graph write CLI."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from papertech.corpus import load_corpus
from papertech.graph_store import GraphStore
from papertech.ingest import atomic_json
from papertech.kg import KGLedger, run_extraction
from papertech.settings import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', choices=['extract', 'inspect', 'review', 'sync-approved'])
    parser.add_argument('--resume', default='')
    parser.add_argument('--retry-failed', default='', metavar='RUN_ID', help='Create a separate run for only failed chunks of this run')
    parser.add_argument('--limit', type=int, default=0, help='Limit to the first N body chunks; useful for a smoke run')
    parser.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    parser.add_argument('--claim-id', default='')
    parser.add_argument('--decision', choices=['approved', 'rejected'])
    parser.add_argument('--note', default='')
    args = parser.parse_args()
    report_root = ROOT / 'artifacts/reports/stage-3'
    report_root.mkdir(parents=True, exist_ok=True)
    corpus_id, papers, chunks = load_corpus(ROOT)

    if args.task == 'extract':
        body_chunks = [chunk for chunk in chunks if chunk.get('content_kind') != 'references']
        if args.retry_failed:
            if args.resume or args.limit:
                parser.error('--retry-failed cannot be combined with --resume or --limit')
            ledger = KGLedger(ROOT)
            try:
                original = ledger.conn.execute('SELECT * FROM kg_runs WHERE run_id=?', (args.retry_failed,)).fetchone()
                if not original or original['corpus_id'] != corpus_id:
                    parser.error('Retry source run does not match the active corpus')
                failed = {r[0] for r in ledger.conn.execute("SELECT chunk_id FROM kg_tasks WHERE run_id=? AND status='failed'", (args.retry_failed,))}
                body_chunks = [c for c in body_chunks if c['chunk_id'] in failed]
                if not failed or len(body_chunks) != len(failed):
                    parser.error('No failed chunks, or source chunks changed')
            finally:
                ledger.close()
        if args.limit:
            if args.limit < 1:
                parser.error('--limit must be positive')
            body_chunks = body_chunks[:args.limit]
            if args.resume:
                parser.error('--limit cannot be combined with --resume')

        run_id = args.resume
        if not run_id:
            ledger = KGLedger(ROOT)
            try:
                run_id = ledger.start_run(corpus_id, 'qwen2.5:7b-instruct', body_chunks,
                                          {paper['paper_id']: paper for paper in papers})
            finally:
                ledger.close()
        run_dir = report_root / 'runs' / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        atomic_json(report_root / 'current-run.json', dict(run_id=run_id, corpus_id=corpus_id))

        def on_progress(index, total, result, progress):
            from papertech.kg import utcnow
            snapshot = dict(updated_at=utcnow(), run_id=run_id,
                            status=progress['run']['status'], total_chunks=progress['run']['total_chunks'],
                            completed_chunks=progress['run']['completed_chunks'], reused_chunks=progress['run']['reused_chunks'],
                            failed_chunks=progress['run']['failed_chunks'], accepted_candidates=progress['run']['accepted_candidates'],
                            rejected_candidates=progress['run']['rejected_candidates'], input_tokens=progress['run']['input_tokens'],
                            output_tokens=progress['run']['output_tokens'], papers=progress['papers'],
                            claims_by_review_status=progress['claims_by_review_status'], last_chunk=result)
            atomic_json(run_dir / 'progress.json', snapshot)
            print(json.dumps(dict(run_id=run_id, progress=f'{index}/{total}', chunk_id=result['chunk_id'],
                                  status=result['status'], candidates=result.get('candidate_count', 0),
                                  rejected=result.get('rejected_count', 0), input_tokens=result.get('input_tokens'),
                                  output_tokens=result.get('output_tokens')), ensure_ascii=False), flush=True)

        progress = run_extraction(ROOT, corpus_id, papers, body_chunks, run_id=run_id,
                                  ollama_url=args.ollama_url, progress_callback=on_progress, retry_of=args.retry_failed or None)
        atomic_json(run_dir / 'progress.json', progress)
        pending = KGLedger(ROOT)
        try:
            claims = pending.pending_claims(corpus_id, limit=500)
            atomic_json(run_dir / 'review-queue.json', claims)
        finally:
            pending.close()
        print(json.dumps(progress, ensure_ascii=False, indent=2))
        return 0 if progress['run']['status'] == 'completed' else 1

    ledger = KGLedger(ROOT)
    try:
        if args.task == 'inspect':
            result = ledger.progress()
            result = result or dict(run=None, papers=[], claims_by_review_status={})
            result['pending_review_preview'] = ledger.pending_claims(corpus_id, limit=10)
            if result['run']:
                graph = GraphStore(settings(ROOT), corpus_id)
                try:
                    result['neo4j'] = graph.inspect()
                finally:
                    graph.close()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.task == 'review':
            if not args.claim_id or not args.decision:
                parser.error('review requires --claim-id and --decision')
            claim = ledger.update_review(args.claim_id, args.decision, args.note)
            if args.decision == 'approved':
                graph = GraphStore(settings(ROOT), corpus_id)
                try:
                    graph.ensure_kg_schema()
                    graph.write_kg_claim(dict(claim, corpus_id=corpus_id, review_status='approved'))
                    ledger.mark_graph_written(args.claim_id)
                finally:
                    graph.close()
            print(json.dumps(dict(status=args.decision, claim_id=args.claim_id), ensure_ascii=False))
        else:
            graph = GraphStore(settings(ROOT), corpus_id)
            written, failed = [], []
            try:
                graph.ensure_kg_schema()
                rows = ledger.conn.execute("SELECT * FROM kg_claims WHERE corpus_id=? AND review_status='approved' AND graph_written=0 ORDER BY paper_title,page_start LIMIT 1000", (corpus_id,))
                for row in rows:
                    claim = dict(row)
                    try:
                        graph.write_kg_claim(claim)
                        ledger.mark_graph_written(claim['claim_id'])
                        written.append(claim['claim_id'])
                    except Exception as exc:
                        failed.append(dict(claim_id=claim['claim_id'], error=type(exc).__name__))
            finally:
                graph.close()
            result = dict(status='completed' if not failed else 'completed_with_failures', written=len(written), failed=failed)
            atomic_json(report_root / 'approved-sync.json', result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        ledger.close()


if __name__ == '__main__':
    sys.exit(main())
