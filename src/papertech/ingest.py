"""SQLite task state and bounded local subprocess ingestion."""

import contextlib
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from .pdf import ParseError, audit_document, identities


def now():
    return datetime.now().astimezone().isoformat()


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.pending')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


@contextlib.contextmanager
def exclusive_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError('Another ingestion process holds the project lock') from exc
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def connect(project):
    target = project / 'data/ingest.sqlite3'
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY, relative_path TEXT NOT NULL, source_sha256 TEXT NOT NULL,
            created_at TEXT NOT NULL, UNIQUE(relative_path, source_sha256));
        CREATE TABLE IF NOT EXISTS parses (
            parse_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers(paper_id),
            parser_version TEXT NOT NULL, config_json TEXT NOT NULL, status TEXT NOT NULL,
            artifact_path TEXT NOT NULL, artifact_sha256 TEXT NOT NULL,
            page_count INTEGER NOT NULL, chunk_count INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY, parse_id TEXT NOT NULL REFERENCES parses(parse_id),
            paper_id TEXT NOT NULL REFERENCES papers(paper_id), ordinal INTEGER NOT NULL,
            text_sha256 TEXT NOT NULL, page_start INTEGER NOT NULL, page_end INTEGER NOT NULL,
            UNIQUE(parse_id, ordinal));
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, manifest_version TEXT NOT NULL, manifest_sha256 TEXT NOT NULL,
            config_json TEXT NOT NULL, status TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT);
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(run_id), ordinal INTEGER NOT NULL,
            candidate_id TEXT NOT NULL, relative_path TEXT NOT NULL, paper_id TEXT NOT NULL,
            parse_id TEXT NOT NULL, status TEXT NOT NULL, started_at TEXT, finished_at TEXT,
            elapsed_seconds REAL, page_count INTEGER, chunk_count INTEGER, document_status TEXT,
            error_code TEXT, error_summary TEXT, warnings_json TEXT, source_hash_before TEXT,
            source_hash_after TEXT, UNIQUE(run_id, ordinal));
    ''')
    return conn


def export_run(conn, project, run_id):
    run = dict(conn.execute('SELECT * FROM runs WHERE run_id=?', (run_id,)).fetchone())
    tasks = [dict(row) for row in conn.execute('SELECT * FROM tasks WHERE run_id=? ORDER BY ordinal', (run_id,))]
    counts = {}
    for task in tasks:
        counts[task['status']] = counts.get(task['status'], 0) + 1
    result = {**run, 'task_counts': counts, 'total_tasks': len(tasks),
              'pages': sum(t['page_count'] or 0 for t in tasks),
              'chunks': sum(t['chunk_count'] or 0 for t in tasks), 'tasks': tasks}
    folder = project / 'artifacts/logs/ingest' / run_id
    atomic_json(folder / 'summary.json', result)
    atomic_json(folder / 'failure-queue.json', [t for t in tasks if t['status'] in ('failed', 'interrupted')])
    return result


def recover_runs(conn, project):
    # Caller holds an OS lock, so unfinished runs cannot belong to a live concurrent ingest.
    runs = [r[0] for r in conn.execute("SELECT run_id FROM runs WHERE status='running'")]
    for run_id in runs:
        stamp = now()
        with conn:
            conn.execute("UPDATE tasks SET status='interrupted', finished_at=?, error_code='previous_run_interrupted', "
                         "error_summary='Previous process exited without a terminal task status' "
                         "WHERE run_id=? AND status IN ('pending','running')", (stamp, run_id))
            conn.execute("UPDATE runs SET status='interrupted',finished_at=? WHERE run_id=?", (stamp, run_id))
        export_run(conn, project, run_id)


def resolve_source(project, relative):
    base = (project / 'database').resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or not relative.lower().endswith('.pdf'):
        raise ParseError('invalid_source_path', 'Source must be a PDF inside database')
    return path


def worker(path, relative, expected_hash, config, temp, timeout):
    env = os.environ.copy()
    source_dir = str(Path(__file__).resolve().parents[1])
    env['PYTHONPATH'] = source_dir + os.pathsep + env.get('PYTHONPATH', '')
    env['TEMP'] = str(temp.parent)
    env['TMP'] = str(temp.parent)
    env['PYTHONPYCACHEPREFIX'] = str(temp.parent.parent / 'pycache')
    try:
        result = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'papertech.pdf', str(path), relative,
                                 expected_hash, json.dumps(config), str(temp)],
                                capture_output=True, text=True, encoding='utf-8', env=env, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ParseError('parse_timeout', f'PDF exceeded the {timeout}-second processing budget') from exc
    if result.returncode:
        try:
            error = json.loads(result.stdout)
        except ValueError:
            error = {'code': 'worker_crashed', 'message': result.stderr[-500:] or f'Exit code {result.returncode}'}
        raise ParseError(error['code'], error['message'])
    doc = json.loads(temp.read_text(encoding='utf-8'))
    audit_document(doc)
    return doc


def ingest_batch(project, manifest, manifest_hash, config, force=False, timeout=60):
    project = Path(project).resolve()
    if not 1 <= len(manifest['pilots']) <= 1000:
        raise ValueError('Batch must contain 1..1000 papers')
    if not 1 <= timeout <= 600 or not 50 <= config['target_estimated_tokens'] <= 2000:
        raise ValueError('Invalid processing budget')
    with exclusive_lock(project / '.cache/ingest.lock'), contextlib.closing(connect(project)) as conn:
        recover_runs(conn, project)
        run_id = datetime.now().strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:10]
        with conn:
            conn.execute('INSERT INTO runs VALUES (?,?,?,?,?,?,NULL)',
                         (run_id, manifest['manifest_version'], manifest_hash,
                          json.dumps(config, sort_keys=True), 'running', now()))
            for ordinal, entry in enumerate(manifest['pilots']):
                paper_id, parse_id = identities(entry['relative_path'], entry['sha256'], config)
                conn.execute('INSERT INTO tasks (task_id,run_id,ordinal,candidate_id,relative_path,paper_id,parse_id,status) '
                             'VALUES (?,?,?,?,?,?,?,?)',
                             (uuid.uuid4().hex, run_id, ordinal, entry['candidate_id'], entry['relative_path'], paper_id, parse_id, 'pending'))
        export_run(conn, project, run_id)
        for ordinal, entry in enumerate(manifest['pilots']):
            started = time.monotonic()
            paper_id, parse_id = identities(entry['relative_path'], entry['sha256'], config)
            with conn:
                conn.execute("UPDATE tasks SET status='running', started_at=? WHERE run_id=? AND ordinal=?", (now(), run_id, ordinal))
            before = after = None
            try:
                path = resolve_source(project, entry['relative_path'])
                if not path.is_file():
                    raise ParseError('missing_file', 'Source PDF not found')
                before = file_hash(path)
                if before != entry['sha256']:
                    raise ParseError('source_hash_mismatch', 'Source differs from the frozen manifest; use a reviewed new manifest version')
                with conn:
                    conn.execute('INSERT OR IGNORE INTO papers VALUES (?,?,?,?)', (paper_id, entry['relative_path'], before, now()))
                cached = conn.execute('SELECT * FROM parses WHERE parse_id=?', (parse_id,)).fetchone()
                if cached and not force:
                    artifact = (project / cached['artifact_path']).resolve()
                    if not artifact.is_relative_to((project / 'data/extracted').resolve()):
                        raise ParseError('invalid_artifact_path', 'Cached artifact outside data/extracted')
                    if not artifact.is_file() or file_hash(artifact) != cached['artifact_sha256']:
                        raise ParseError('cached_artifact_corrupt', 'Cached extraction missing or changed; history was retained')
                    doc = json.loads(artifact.read_text(encoding='utf-8'))
                    audit_document(doc)
                    status = 'reused'
                else:
                    temp = project / '.cache/temp' / (parse_id + '.' + uuid.uuid4().hex + '.json')
                    temp.parent.mkdir(parents=True, exist_ok=True)
                    doc = worker(path, entry['relative_path'], before, config, temp, timeout)
                    if doc['paper_id'] != paper_id or doc['parse_id'] != parse_id:
                        raise ParseError('worker_identity_mismatch', 'Worker returned an unexpected result identity')
                    artifact = project / 'data/extracted' / paper_id / parse_id / 'document.json'
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    if artifact.exists():
                        if artifact.read_bytes() != temp.read_bytes():
                            raise ParseError('non_deterministic_parse', 'Same source/version produced different extraction; old result retained')
                        temp.unlink()
                    else:
                        os.replace(temp, artifact)
                    status = doc['status']
                after = file_hash(path)
                if after != before:
                    raise ParseError('source_changed_during_parse', 'Source changed while processing; result not accepted')
                with conn:
                    conn.execute('INSERT OR IGNORE INTO parses VALUES (?,?,?,?,?,?,?,?,?,?)',
                                 (parse_id, paper_id, config['parser_version'], json.dumps(config, sort_keys=True),
                                  doc['status'], artifact.relative_to(project).as_posix(), file_hash(artifact),
                                  doc['page_count'], doc['chunk_count'], now()))
                    for chunk in doc['chunks']:
                        conn.execute('INSERT OR IGNORE INTO chunks VALUES (?,?,?,?,?,?,?)',
                                     (chunk['chunk_id'], parse_id, paper_id, chunk['ordinal'], chunk['text_sha256'],
                                      chunk['page_start'], chunk['page_end']))
                    conn.execute('UPDATE tasks SET status=?,finished_at=?,elapsed_seconds=?,page_count=?,chunk_count=?, '
                                 'document_status=?,warnings_json=?,source_hash_before=?,source_hash_after=? WHERE run_id=? AND ordinal=?',
                                 (status, now(), round(time.monotonic() - started, 4), doc['page_count'], doc['chunk_count'],
                                  doc['status'], json.dumps(doc['warnings']), before, after, run_id, ordinal))
            except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
                code = getattr(exc, 'code', 'processing_error')
                with conn:
                    conn.execute("UPDATE tasks SET status='failed',finished_at=?,elapsed_seconds=?,error_code=?,error_summary=?, "
                                 'source_hash_before=?,source_hash_after=? WHERE run_id=? AND ordinal=?',
                                 (now(), round(time.monotonic() - started, 4), code,
                                  str(exc).replace(str(project), '<project>')[:500], before, after, run_id, ordinal))
            export_run(conn, project, run_id)
            task = conn.execute('SELECT candidate_id,status,error_code FROM tasks WHERE run_id=? AND ordinal=?', (run_id, ordinal)).fetchone()
            print(f"{task['candidate_id']}: {task['status']}" + (f" ({task['error_code']})" if task['error_code'] else ''), flush=True)
        failures = conn.execute("SELECT COUNT(*) FROM tasks WHERE run_id=? AND status='failed'", (run_id,)).fetchone()[0]
        with conn:
            conn.execute('UPDATE runs SET status=?,finished_at=? WHERE run_id=?', ('completed_with_failures' if failures else 'completed', now(), run_id))
        return export_run(conn, project, run_id)
