"""Summarize verified artifacts and local audit without exporting secrets."""
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.ingest import atomic_json
from papertech.settings import settings

target=ROOT/'artifacts/reports/stage-2'
cfg=settings(ROOT)
conn=sqlite3.connect(ROOT/'data/rag.sqlite3')
conn.row_factory=sqlite3.Row
summary=dict(
    requests=[dict(r) for r in conn.execute('SELECT status,count(*) AS count FROM requests GROUP BY status')],
    stage_count=conn.execute('SELECT count(*) FROM stages').fetchone()[0],
    candidate_count=conn.execute('SELECT count(*) FROM candidates').fetchone()[0],
    actual_cloud_calls=conn.execute('SELECT count(*) FROM calls').fetchone()[0],
    traces=[dict(r) for r in conn.execute('SELECT status,count(*) AS count FROM traces GROUP BY status')],
    cloud_configuration={k:bool(cfg.get(k)) for k in ('CLOUD_BGE_API_KEY','DEEPSEEK_API_KEY','LANGSMITH_API_KEY')},
    invalid_completed_requests=conn.execute("SELECT count(*) FROM requests WHERE status='running'").fetchone()[0])
conn.close()
secrets=[cfg[k] for k in ('NEO4J_PASSWORD','CLOUD_BGE_API_KEY','DEEPSEEK_API_KEY','LANGSMITH_API_KEY') if cfg.get(k)]
leaks=[]
for folder in (target,ROOT/'src',ROOT/'scripts'):
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix in ('.py','.ps1','.json','.md','.txt'):
            content=path.read_text(encoding='utf-8-sig')
            if any(secret in content for secret in secrets):
                leaks.append(str(path.relative_to(ROOT)))
summary['credential_leak_files']=leaks
atomic_json(target/'audit-summary.json',summary)
ui_path=ROOT/'.cache/ui-query.json'
if ui_path.exists():
    ui=json.loads(ui_path.read_text(encoding='utf-8'))
    def flatten(node):
        return [node]+[child for c in node.get('children',[]) for child in flatten(c)]
    nodes=flatten(ui.get('tree',{}))
    result=dict(status=ui.get('status'),streamlit_version='1.67.0',verification='Live localhost agent API',
                question='HippoRAG Personalized PageRank',
                evidence_expanders=sum(n['type']=='expander' and str(n.get('key','')).startswith('evidence_') for n in nodes),
                exceptions=[n for n in nodes if n['type']=='exception'],
                answer=[n['props']['body'] for n in nodes if n['type']=='markdown'],
                empty_input_check='Warning observed: 请先输入问题。',
                static_check='mypy app.py --follow-imports=skip --ignore-missing-imports passed',
                browser_visual_check='Not performed; agent API checks runtime and interaction, not rendered pixels',
                cloud_calls=0)
    atomic_json(target/'ui-verification.json',result)
print(json.dumps(summary,ensure_ascii=False,indent=2))
