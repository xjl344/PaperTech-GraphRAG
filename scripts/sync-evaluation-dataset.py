"""Create versioned evaluation datasets; optionally import existing paired results."""
import argparse
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import dataset_recorder, result_mode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', required=True)
    parser.add_argument('--run-summary', type=Path)
    parser.add_argument('--upload', action='store_true', help='Sync to LangSmith; never invokes a model')
    parser.add_argument('--answer-mode', choices=('summary', 'full'))
    parser.add_argument('--enrich-details', action='store_true', help='Add per-question details to existing matching reference examples')
    args = parser.parse_args()
    logging.getLogger('langsmith').setLevel(logging.CRITICAL)
    recorder = dataset_recorder(ROOT, args.benchmark, allow_enrichment=args.enrich_details)
    try:
        if args.upload:
            if args.run_summary:
                status = recorder.sync_run(args.run_summary, args.answer_mode or result_mode(ROOT, args.benchmark))
                summary = json.loads(args.run_summary.read_text(encoding='utf-8'))
                summary['dataset_sync'] = status
                write_json(args.run_summary, summary)
            else:
                recorder.sync_dataset()
        print(json.dumps(recorder.status, ensure_ascii=False))
    except Exception as exc:
        recorder.status.update(status='pending_sync', error_type=type(exc).__name__)
        write_json(recorder.status_path, recorder.status)
        print(json.dumps(recorder.status, ensure_ascii=False))
        raise SystemExit(1) from None
    finally:
        recorder.close()


if __name__ == '__main__':
    main()
