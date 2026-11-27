"""Audit saved candidate fusion and actual tokenizer truncation, without inference."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def audit_fusion(summary, benchmark):
    cases = {c['id']: c for c in benchmark['cases']}
    records = []
    for row in summary['results']:
        if row['arm'] != 'Hybrid':
            continue
        channels = row['candidate_channels']
        scores = {}
        for rows in channels.values():
            for rank, candidate in enumerate(rows, 1):
                cid = candidate['chunk_id']
                scores[cid] = scores.get(cid, 0) + 1 / (60 + rank)
        fused = sorted(scores, key=lambda cid: (-scores[cid], cid))
        present = {r['chunk_id'] for r in row['ranked']}
        assert present == set(fused[:40])
        missing = []
        for uid in cases[row['case_id']]['units']:
            unit = benchmark['units'][uid]
            pool = set(unit['known_support_chunks'])
            if not pool & present:
                missing.append(dict(unit_id=uid, primary_chunk=unit['primary_chunk'],
                    channel_hits={key: [i for i, c in enumerate(rows, 1) if c['chunk_id'] in pool]
                        for key, rows in channels.items()},
                    loss='not_in_channel_top20' if not pool & set(fused) else 'fusion_cap'))
        records.append(dict(case_id=row['case_id'], category=row['category'],
            channel_counts={k: len(v) for k, v in channels.items()}, union_count=len(fused),
            fusion_dropped_ids=sorted(set(fused) - present),
            cap40_vs_cap60_identical=fused[:40] == fused[:60], missing_sources=missing))
    return dict(questions=len(records), fusion_dropped_candidates=sum(len(r['fusion_dropped_ids']) for r in records),
        cap60_changes=sum(not r['cap40_vs_cap60_identical'] for r in records), records=records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('summary', type=Path)
    parser.add_argument('--tokenizer-job', type=Path)
    args = parser.parse_args()
    if args.tokenizer_job:
        os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
        from transformers import AutoTokenizer
        job = json.loads(args.tokenizer_job.read_text(encoding='utf8'))
        tokenizer = AutoTokenizer.from_pretrained(job['model_path'], local_files_only=True)
        records = []
        windows = {}
        for pair in job['pairs']:
            full = tokenizer(pair['query'], pair['text'], truncation=False)['input_ids']
            kept = tokenizer(pair['query'], pair['text'], truncation=True, max_length=1024)['input_ids']
            records.append({k: pair[k] for k in ('case_id', 'arm', 'chunk_id', 'rank', 'score')} | dict(
                query_tokens=len(tokenizer(pair['query'], add_special_tokens=False)['input_ids']),
                document_tokens=len(tokenizer(pair['text'], add_special_tokens=False)['input_ids']),
                pair_tokens=len(full), retained_tokens=len(kept), truncated_tokens=len(full)-len(kept),
                input_ids_identical=full == kept))
            if pair['case_id'] in ('F02', 'F07', 'R05', 'R24') and pair['arm'] == 'Hybrid':
                text = pair['text']
                # Exact original-text windows. Binary search for the furthest end
                # fitting 160 document tokens; 50% character overlap, no gold.
                fragments, start = [], 0
                while start < len(text):
                    low, high = start + 1, len(text)
                    while low < high:
                        mid = (low + high + 1) // 2
                        if len(tokenizer(text[start:mid], add_special_tokens=False)['input_ids']) <= 160:
                            low = mid
                        else:
                            high = mid - 1
                    end = low
                    fragment = text[start:end]
                    fragments.append(dict(start_char=start, end_char=end, text=fragment,
                        document_tokens=len(tokenizer(fragment, add_special_tokens=False)['input_ids']),
                        pair_tokens=len(tokenizer(pair['query'], fragment, truncation=False)['input_ids'])))
                    if end == len(text):
                        break
                    start += max(1, (end - start) // 2)
                windows[pair['chunk_id']] = fragments
        result = dict(pairs=len(records), truncated_pairs=sum(not r['input_ids_identical'] for r in records),
            max_pair_tokens=max(r['pair_tokens'] for r in records), tokenizer_class=type(tokenizer).__name__,
            tokenizer_truncation_side=tokenizer.truncation_side, rows=records)
        Path(job['output']).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
        Path(job['windows_output']).write_text(json.dumps(windows, ensure_ascii=False, indent=2), encoding='utf8')
        print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))
        return
    from papertech.evaluation_datasets import load_benchmark, write_json
    summary = json.loads(args.summary.read_text(encoding='utf8'))
    benchmark, _, _ = load_benchmark(ROOT, summary['benchmark'])
    result = audit_fusion(summary, benchmark)
    write_json(args.summary.parent / 'fusion-input-audit.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'records'}))


if __name__ == '__main__':
    main()
