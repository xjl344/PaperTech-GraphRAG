"""Re-upload saved router-fix retrieval results with current Experiment timestamps.

Does not call embeddings, Neo4j, a reranker, or a generator.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import sys,uuid

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from papertech.evaluation_datasets import write_json
from papertech.evaluation_details import dataset_recorder
from papertech.router_fix_recall import VERSION
from papertech.subquery_recall_diagnostic import read,report

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('summary',type=Path);args=parser.parse_args()
source=read(args.summary);run_id=uuid.uuid4().hex;now=datetime.now(timezone.utc).isoformat()
folder=ROOT/'artifacts/reports/stage-4'/VERSION/'runs'/run_id;folder.mkdir(parents=True)
replayed=deepcopy(source);replayed['run_id']=run_id;replayed['started']=now;replayed['finished']=now
replayed['uploaded_from_run']=source['run_id'];replayed['experiment_timestamp_policy']='current upload time; retrieved candidates remain saved original/new retrieval outputs'
for row in replayed['results']:
    row['source_started']=row.get('started');row['source_finished']=row.get('finished')
    row['started']=now;row['finished']=now;row['upload_replay']=True
write_json(folder/'summary.json',replayed)
rec=dataset_recorder(ROOT,VERSION)
try:
    status=rec.sync_run(folder/'summary.json');replayed['langsmith']=status;write_json(folder/'summary.json',replayed);report(rec,replayed,folder)
    write_json(folder/'route-and-recall-diff.json',read(args.summary.parent/'route-and-recall-diff.json'))
    print(__import__('json').dumps(dict(run_id=run_id,status=status['status'],comparison_url=status['comparison_url']),ensure_ascii=False))
finally:rec.close()
