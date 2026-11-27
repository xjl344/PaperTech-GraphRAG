"""Run the isolated Qwen2.5-14B mechanism KG pilot; never writes production Neo4j."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from papertech.kg_rebuild_pilot import VERSION,freeze,run,smoke

parser=argparse.ArgumentParser(description=__doc__)
group=parser.add_mutually_exclusive_group(required=True)
group.add_argument('--freeze',action='store_true',help='freeze selected paper/chunk set, schema, model digest and hashes')
group.add_argument('--smoke',action='store_true',help='extract one Method section chunk from each paper to measure 14B')
group.add_argument('--run',action='store_true',help='extract every eligible non-reference chunk from the three papers')
parser.add_argument('--resume',help='resume a previously interrupted full pilot run ID')
parser.add_argument('--limit',type=int,help='only process first N pilot chunks; intended for smoke profiling')
args=parser.parse_args()
if args.resume and not args.run:parser.error('--resume requires --run')
if args.limit and not args.run:parser.error('--limit is only supported with --run')
if args.freeze:
    b=freeze(ROOT);print(json.dumps(dict(version=VERSION,sha256=b['sha256'],model=b['model'],model_digest=b['model_digest'],papers=b['papers'],chunk_count=len(b['chunks']),relations=b['relations']),ensure_ascii=False,indent=2))
elif args.smoke:
    r=smoke(ROOT);print(json.dumps(dict(version=VERSION,model=r['model'],model_digest=r['model_digest'],total_pilot_chunks=r['total_chunks'],sample_count=r['sample_count'],summary=r['summary'],chunks=[dict(paper_title=x['paper_title'],section=x['section'],page_start=x['page_start'],status=x['status'],claims=len(x.get('relations',[])),rejected=len(x.get('rejected',[])),seconds=x.get('seconds')) for x in r['results']]),ensure_ascii=False,indent=2))
else:
    d,r=run(ROOT,resume_id=args.resume,limit=args.limit);print(json.dumps(dict(run_id=d.name,report=str(d/'report.json'),summary=r['summary']),ensure_ascii=False,indent=2))
