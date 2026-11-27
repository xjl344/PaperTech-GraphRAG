import json,sys,uuid
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from papertech.router_fix_replay import replay,VERSION,SOURCE,RUN
from papertech.query_router_diagnostic import rule_candidate
from papertech.evaluation_details import dataset_recorder
from papertech.evaluation_datasets import write_json

bench=replay(ROOT);rec=dataset_recorder(ROOT,VERSION);old=json.loads((ROOT/'artifacts/reports/stage-4'/SOURCE/'runs'/RUN/'summary.json').read_text(encoding='utf8'))
plans=bench['query_plans'];old_rows={(r['case_id'],r['arm']):r for r in old['results']}
run_id=uuid.uuid4().hex;folder=ROOT/'artifacts/reports/stage-4'/VERSION/'runs'/run_id;folder.mkdir(parents=True)
summary=dict(run_id=run_id,benchmark=VERSION,benchmark_sha256=rec.digest,status='completed',started=datetime.now(timezone.utc).isoformat(),results=[],replay_source_run=RUN)
for case in bench['cases']:
    cid=case['id'];q=case['question'];base=old_rows[(cid,'Rule')]
    current_start=datetime.now(timezone.utc).isoformat();current_end=datetime.now(timezone.utc).isoformat()
    rule=dict(base,case_id=cid,question=q,arm='Rule',started=current_start,finished=current_end,trace_url='https://smith.langchain.com/r/'+__import__('papertech.evaluation_datasets',fromlist=['stable_id']).stable_id(rec.digest,run_id,cid,'Rule'))
    local_old=old_rows[(cid,'Local-LLM')];plan=plans[cid]
    local=dict(local_old,case_id=cid,question=q,arm='Local-LLM',started=current_start,finished=current_end,route=plan['route'],subqueries=plan['subqueries'],unresolved=plan['unresolved'],reason=plan['reason'],
        valid=plan['valid'],validation_errors=plan['validation_errors'],source_spans=plan['source_spans'],quote_normalized=plan.get('quote_normalized',False),
        parsed_output=plan['parsed_output'],replay=True,model_calls=0,usage=None,seconds=0.0,trace_url='https://smith.langchain.com/r/'+__import__('papertech.evaluation_datasets',fromlist=['stable_id']).stable_id(rec.digest,run_id,cid,'Local-LLM'))
    local['metrics']=dict(valid_output=int(local['valid']),split_applied=int(bool(local['subqueries'])),subquery_count=len(local['subqueries']),original_retained=1,model_calls=0,replayed=1)
    summary['results'].extend([rule,local]);write_json(folder/f'{cid}-Rule.json',rule);write_json(folder/f'{cid}-Local-LLM.json',local)
write_json(folder/'summary.json',summary)
rec.sync_dataset();summary['dataset_sync']=rec.sync_run(folder/'summary.json');write_json(folder/'summary.json',summary)
from papertech.query_router_diagnostic import report
report(summary,folder)
write_json(folder/'replay-diff.json',dict(changes=bench['replay_changes'],source_run=RUN,benchmark_sha256=rec.digest))
print(json.dumps(dict(version=VERSION,run_id=run_id,cases=24,changes=bench['replay_changes'],langsmith=summary['dataset_sync']),ensure_ascii=False))
rec.close()
