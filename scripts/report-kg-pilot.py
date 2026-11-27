"""Render a reviewable Markdown report for an isolated mechanism KG pilot run."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.kg_rebuild_pilot import VERSION,verify_freeze


def source_locations(claim):
    start,end=claim['quote_start'],claim['quote_end']
    locations=[]
    for span in claim.get('source_spans',[]):
        left=max(start,span['chunk_start_char'])
        right=min(end,span['chunk_end_char'])
        if left>=right:continue
        locations.append(dict(page=span['pdf_page'],
            start_char=span['start_char']+(left-span['chunk_start_char']),
            end_char=span['start_char']+(right-span['chunk_start_char'])))
    return locations


def md(value):
    return str(value).replace('|','\\|').replace('\r',' ').replace('\n',' ')


def render(run_dir):
    report=json.loads((run_dir/'report.json').read_text(encoding='utf8'))
    checkpoint=json.loads((run_dir/'checkpoint.json').read_text(encoding='utf8'))
    verify_freeze(ROOT,report['benchmark'])
    papers={p['paper_id']:p for p in report['benchmark']['papers']}
    rows=checkpoint['results']
    claims=[c for row in rows for c in row.get('relations',[])]
    rejected=[item for row in rows for item in row.get('rejected',[])]
    duplicate_counts=Counter((c['paper_id'],c['subject'].casefold(),c['predicate'],c['object'].casefold()) for c in claims)
    duplicate_count=sum(count-1 for count in duplicate_counts.values() if count>1)
    locations_ok=sum(bool(source_locations(c)) for c in claims)
    lines=[f"# {VERSION} extraction pilot review",'',
        '> Independent, non-production JSON graph. Every Claim remains pending manual semantic review.',
        '> A located quote and schema-valid relation do not by themselves establish semantic correctness.', '',
        '## Run summary','',
        f"- Run ID: `{report['run_id']}`",
        f"- Model: `{report['benchmark']['model']}` ({report['benchmark']['model_digest']})",
        f"- Status: `{report['summary']['status']}`; {report['summary']['completed_chunks']}/{report['summary']['total_chunks']} chunks completed; {report['summary']['failed_chunks']} failed",
        f"- Claims: {len(claims)} accepted from {report['summary']['chunks_with_claims']} chunks; {len(rejected)} candidates rejected",
        f"- Relation counts: `{json.dumps(report['summary']['claims_by_predicate'],ensure_ascii=False)}`",
        f"- Quote offsets map back to source page spans: {locations_ok}/{len(claims)}",
        f"- Duplicate subject–predicate–object triples across chunks: {duplicate_count}",
        f"- Tokens: {report['summary']['input_tokens']:,} input / {report['summary']['output_tokens']:,} output",
        f"- Model time: {report['summary']['model_seconds']:.1f}s; wall time: {report['summary']['started_at']} to {report['summary']['finished_at']}",
        '', '## Per-paper coverage','',
        '| Paper | Eligible chunks | Chunks with claims | Claim coverage | Accepted claims | Rejected candidates | Seconds | Input / output tokens |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for paper_id,paper in papers.items():
        pr=[r for r in rows if r['paper_id']==paper_id]
        pc=[c for r in pr for c in r.get('relations',[])]
        pj=[x for r in pr for x in r.get('rejected',[])]
        with_claims=sum(bool(r.get('relations')) for r in pr)
        coverage=with_claims/len(pr)*100 if pr else 0
        lines.append(f"| {md(paper['title'])} | {len(pr)} | {with_claims} | {coverage:.1f}% | {len(pc)} | {len(pj)} | {sum(r.get('seconds') or 0 for r in pr):.1f} | {sum(r.get('input_tokens') or 0 for r in pr):,} / {sum(r.get('output_tokens') or 0 for r in pr):,} |")
    lines.extend(['','## Rejection reasons',''])
    for reason,count in Counter(x['reason'] for x in rejected).most_common():
        lines.append(f'- `{reason}`: {count}')
    lines.extend(['','## Claims and original quotes',''])
    for paper_id,paper in papers.items():
        lines.extend([f"### {paper['title']}",''])
        paper_claims=[c for c in claims if c['paper_id']==paper_id]
        for index,c in enumerate(paper_claims,1):
            locs=source_locations(c)
            where=', '.join(f"p.{x['page']} chars {x['start_char']}–{x['end_char']}" for x in locs) or 'unmapped'
            quote=c['evidence_quote'].replace('\r','').replace('\n',' ')
            lines.extend([f"{index}. **{md(c['subject'])} — {c['predicate']} → {md(c['object'])}**; p.{c['page_start']}–{c['page_end']}; `{c['review_status']}`",
                f"   - Source span: {where}; chunk `{c['chunk_id']}`",
                f"   - Quote: “{quote}”",''])
        if not paper_claims:lines.extend(['No accepted claims.',''])
    lines.extend(['## Interpretation limits','',
        '- `author_assertion`, allowed relation signature, and quote matching are automated checks only.',
        '- Section/paragraph attribution, whether a statement describes this paper’s method or prior work, entity naming, and whether a reported setting is truly a control parameter require semantic review.',
        '- This pilot does not measure retrieval quality, graph reachability, or downstream QA accuracy.',
        '- No rows were written to the production graph.'])
    target=run_dir/'review.md'
    target.write_text('\n'.join(lines)+'\n',encoding='utf8')
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    run_dir=ROOT/'artifacts/reports/stage-3'/VERSION/'runs'/args.run_id
    if not (run_dir/'report.json').is_file():raise SystemExit(f'missing completed run: {run_dir}')
    print(render(run_dir))


if __name__=='__main__':main()
