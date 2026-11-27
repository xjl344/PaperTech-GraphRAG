"""Structured paper Method Cards with strict verbatim provenance and local BGE-M3 slot navigation."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .audit import Audit, now
from .citations import prompt_evidence, quote_options
from .corpus import load_corpus, valid_vector
from .entity_aliases import source_groups
from .evaluation_datasets import write_json
from .local_models import run_worker, vector_metadata
from .providers import Providers

CARD_VERSION = 'method-cards-v1'
SLOTS = (
    'method_name_and_aliases',
    'problem_and_task',
    'core_components',
    'retrieval_and_graph_mechanism',
    'training_and_tuning',
    'datasets_and_eval_setup',
    'key_hyperparameters_and_limits',
)

CARD_SYSTEM = (
    '你是学术论文结构化方法卡抽取器。仅根据提供的单篇论文原文块（带短编号 E1..Ek 与 quote_options）填写 7 个固定槽位，'
    '严禁使用外部知识或编造未在原文块中出现的细节；某槽位在给定片段中找不到明确依据时 summary 写 "not_found" 且 citations 为 []。\n'
    '7 个槽位：\n'
    '1. method_name_and_aliases：本文提出的方法/基准/框架名称、缩写与定位。\n'
    '2. problem_and_task：要解决的核心问题、任务类型与动机。\n'
    '3. core_components：核心模块、阶段或框架组成部分。\n'
    '4. retrieval_and_graph_mechanism：检索流程、图表示、遍历/搜索/剪枝/停止/重排机制。\n'
    '5. training_and_tuning：是否微调/训练、训练数据来源、冻结与可训练参数（区分训练来源与测试知识库）。\n'
    '6. datasets_and_eval_setup：评测数据集、底座 LLM、评价指标、采样或成本协议。\n'
    '7. key_hyperparameters_and_limits：关键超参（如深度、宽度、阈值、预算、top-k）、局限性或消融发现。\n'
    '每个槽位输出 {"summary":"简洁英文+中文核心要点（<=350字）","keywords":["英文关键术语"],"citations":[{"eid":"E1","quote_id":"q1"}]}。\n'
    '每条 citation 必须从提供的 eid 和 quote_options 中选择实际支持该槽位的编号。只输出严格 JSON 对象，顶层键为以上 7 个槽位名。'
)

_SLOT_CUES = re.compile(
    r'\b(?:abstract|propose|framework|architecture|algorithm|method|retriev|graph|travers|beam|prun|'
    r'stop|terminat|train|fine-tun|soft prompt|lora|dataset|benchmark|webqsp|cwq|freebase|stark|'
    r'experiment|metric|hyperparameter|threshold|budget|cost|limitation|ablation|conclusion)\b', re.I
)


def select_representative_chunks(paper_chunks, limit=14):
    """Corpus-only deterministic selection of diverse non-reference chunks covering method & experiments."""
    body = [c for c in sorted(paper_chunks, key=lambda x: x.get('ordinal', 0)) if c.get('content_kind') != 'references']
    if len(body) <= limit:
        return body
    chosen = []
    seen = set()
    def add(c):
        if c['chunk_id'] not in seen and len(chosen) < limit:
            chosen.append(c)
            seen.add(c['chunk_id'])
    # Always keep title/abstract/intro opening chunks and closing conclusion chunk.
    for c in body[:3]:
        add(c)
    add(body[-1])
    # Score remaining body chunks by density of general academic structure cues (never gold/questions).
    scored = []
    for idx, c in enumerate(body):
        if c['chunk_id'] in seen:
            continue
        sec = str(c.get('section') or '').casefold()
        sec_bonus = 4 if any(w in sec for w in ('method', 'approach', 'framework', 'experiment', 'setup', 'limitation', 'conclusion', 'training', 'benchmark')) else 0
        hits = len(set(m.group(0).casefold() for m in _SLOT_CUES.finditer(c['text'])))
        scored.append((-(hits + sec_bonus), idx, c))
    scored.sort(key=lambda x: (x[0], x[1]))
    for _, _, c in scored:
        add(c)
        if len(chosen) >= limit:
            break
    chosen.sort(key=lambda x: x.get('ordinal', 0))
    return chosen


def validate_card_payload(raw_body, selected_chunks):
    """Strictly validate every slot citation against verbatim source chunks; strip invalid citations."""
    eid_map = {f'E{i}': c for i, c in enumerate(selected_chunks, 1)}
    options_map = {eid: {q['quote_id']: q['quote'] for q in quote_options(c['text'])} for eid, c in eid_map.items()}
    card_slots = {}
    rejected_citations = 0
    for slot in SLOTS:
        entry = raw_body.get(slot)
        if not isinstance(entry, dict):
            card_slots[slot] = dict(summary='not_found', keywords=[], citations=[])
            continue
        summary = ' '.join(str(entry.get('summary') or 'not_found').split())[:600]
        keywords = [str(k).strip() for k in (entry.get('keywords') or []) if isinstance(k, str) and k.strip()][:12]
        valid_cites = []
        seen_pairs = set()
        for cite in (entry.get('citations') or [])[:8]:
            if not isinstance(cite, dict):
                rejected_citations += 1
                continue
            eid, qid = cite.get('eid'), cite.get('quote_id')
            if eid not in eid_map or qid not in options_map[eid]:
                rejected_citations += 1
                continue
            c = eid_map[eid]
            quote = options_map[eid][qid]
            if quote not in c['text']:
                rejected_citations += 1
                continue
            key = (c['chunk_id'], qid)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            valid_cites.append(dict(chunk_id=c['chunk_id'], quote_id=qid, page_start=c['page_start'],
                                   page_end=c['page_end'], quote=quote))
        if not valid_cites:
            summary = 'not_found'
        card_slots[slot] = dict(summary=summary, keywords=keywords, citations=valid_cites)
    return card_slots, rejected_citations


def build_method_cards(root, cfg, output_path=None):
    """Build and freeze 14-paper structured method cards with verbatim provenance."""
    target = Path(output_path) if output_path else (root / 'artifacts/exports/pilot-v1/method-cards-v1.json')
    corpus_id, papers, chunks = load_corpus(root)
    by_paper = {}
    for c in chunks:
        by_paper.setdefault(c['paper_id'], []).append(c)
    audit = Audit(root)
    providers = Providers(cfg, audit)
    cards = []
    total_rejected = 0
    try:
        for paper in papers:
            selected = select_representative_chunks(by_paper[paper['paper_id']], limit=14)
            formatted = [prompt_evidence(dict(c, quote=c['text']), eid=f'E{i}') for i, c in enumerate(selected, 1)]
            rid = audit.start(f"[method-card-build] {paper['title']}")
            body, _ = providers.post(rid, 'deepseek', 'chat/completions', dict(
                model=cfg['DEEPSEEK_MODEL'], thinking={'type': 'disabled'}, max_tokens=2048,
                response_format={'type': 'json_object'}, messages=[
                    {'role': 'system', 'content': CARD_SYSTEM},
                    {'role': 'user', 'content': json.dumps(dict(paper_title=paper['title'], evidence=formatted), ensure_ascii=False)},
                ]))
            raw = body['choices'][0]['message']['content']
            parsed = json.loads(raw)
            slots, rejected = validate_card_payload(parsed, selected)
            total_rejected += rejected
            cards.append(dict(
                paper_id=paper['paper_id'], title=paper['title'],
                source_relative_path=paper['source_relative_path'],
                source_sha256=paper['source_sha256'],
                selected_chunk_ids=[c['chunk_id'] for c in selected],
                slots=slots, rejected_citations=rejected, usage=body.get('usage'),
            ))
            audit.finish(rid, dict(status='completed', slots_populated=sum(s['summary'] != 'not_found' for s in slots.values())))
            print(json.dumps(dict(paper=paper['title'][:45], populated=sum(s['summary'] != 'not_found' for s in slots.values()),
                                  citations=sum(len(s['citations']) for s in slots.values()), rejected=rejected), ensure_ascii=False), flush=True)
    finally:
        providers.client.close()
        audit.close()
    payload = dict(version=CARD_VERSION, created_at=now(), corpus_id=corpus_id, model=cfg['DEEPSEEK_MODEL'],
                   paper_count=len(cards), total_rejected_citations=total_rejected, cards=cards)
    write_json(target, payload)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.sha256').write_text(digest + '\n', encoding='utf-8')
    return payload, digest


def claim_canonical_text(row):
    return f"{row['subject']} --{row['predicate']}--> {row['object']}. Evidence: {row['evidence_quote']}"


def slot_canonical_text(paper_title, slot_name, slot_data):
    kws = ', '.join(slot_data.get('keywords') or [])
    return f"Paper: {paper_title}\nAspect: {slot_name}\nKeywords: {kws}\nSummary: {slot_data['summary']}"


def build_auxiliary_vectors(root, cfg, graph_path, cards_path):
    """Build local BGE-M3 vectors for all frozen-graph claims and method-card slots (0 cloud text uploads)."""
    model_meta = vector_metadata(root)
    model_id = model_meta['model_id']
    # 1. Read all claims from frozen isolated graph (read-only).
    gconn = sqlite3.connect(Path(graph_path).resolve().as_uri() + '?mode=ro', uri=True)
    gconn.row_factory = sqlite3.Row
    try:
        claim_rows = [dict(r) for r in gconn.execute('SELECT claim_id,subject,predicate,object,evidence_quote FROM claims ORDER BY claim_id')]
    finally:
        gconn.close()
    cards_doc = json.loads(Path(cards_path).read_text(encoding='utf-8'))

    def cache_vectors(db_path, records):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS aux_vectors (model_id TEXT, item_id TEXT, text_sha256 TEXT, vector TEXT, PRIMARY KEY(model_id,item_id))')
        conn.commit()
        existing = {(r[0], r[1]): r[2] for r in conn.execute('SELECT item_id,text_sha256,vector FROM aux_vectors WHERE model_id=?', (model_id,))}
        todo = []
        for item_id, text in records:
            digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
            if (item_id, digest) not in existing:
                todo.append((item_id, digest, text))
        if todo:
            out = run_worker(root, cfg, 'query', [dict(text=t) for _, _, t in todo], timeout=1800)
            if out['model_id'] != model_id:
                raise RuntimeError('local_bge_model_id_mismatch')
            for (item_id, digest, _), vec in zip(todo, out['outputs']):
                normed = valid_vector(vec)
                conn.execute('INSERT OR REPLACE INTO aux_vectors VALUES (?,?,?,?)',
                             (model_id, item_id, digest, json.dumps(normed)))
            conn.commit()
        result = {}
        for item_id, text in records:
            digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
            row = conn.execute('SELECT vector FROM aux_vectors WHERE model_id=? AND item_id=? AND text_sha256=?',
                               (model_id, item_id, digest)).fetchone()
            result[item_id] = valid_vector(json.loads(row[0]))
        conn.close()
        return result, len(todo)

    claim_records = [(r['claim_id'], claim_canonical_text(r)) for r in claim_rows]
    claim_vecs, claim_new = cache_vectors(root / 'data/claim-embeddings.sqlite3', claim_records)

    slot_records = []
    for card in cards_doc['cards']:
        for slot_name, slot_data in card['slots'].items():
            if slot_data.get('summary') and slot_data['summary'] != 'not_found' and slot_data.get('citations'):
                sid = f"{card['paper_id']}::{slot_name}"
                slot_records.append((sid, slot_canonical_text(card['title'], slot_name, slot_data)))
    slot_vecs, slot_new = cache_vectors(root / 'data/method-card-embeddings.sqlite3', slot_records)
    return dict(model_id=model_id, claim_vectors=len(claim_vecs), claim_newly_computed=claim_new,
                slot_vectors=len(slot_vecs), slot_newly_computed=slot_new)


def load_aux_vectors(db_path, model_id):
    conn = sqlite3.connect(Path(db_path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        rows = conn.execute('SELECT item_id,vector FROM aux_vectors WHERE model_id=?', (model_id,)).fetchall()
        return {item_id: valid_vector(json.loads(vec)) for item_id, vec in rows}
    finally:
        conn.close()


class MethodCardNavigator:
    """Read-only vector navigator over verified Method Card slots; returns verbatim source chunk_ids only."""
    def __init__(self, cards_path, vectors_db, model_id):
        self.cards_path = Path(cards_path).resolve()
        self.sha256 = hashlib.sha256(self.cards_path.read_bytes()).hexdigest()
        doc = json.loads(self.cards_path.read_text(encoding='utf-8'))
        self.version = doc['version']
        self.cards = doc['cards']
        self.slot_vectors = load_aux_vectors(vectors_db, model_id)
        self.slots_index = []
        for card in self.cards:
            for slot_name, slot_data in card['slots'].items():
                sid = f"{card['paper_id']}::{slot_name}"
                if sid in self.slot_vectors and slot_data.get('citations'):
                    self.slots_index.append(dict(
                        slot_id=sid, paper_id=card['paper_id'], title=card['title'], slot=slot_name,
                        vector=self.slot_vectors[sid],
                        chunk_ids=list(dict.fromkeys(c['chunk_id'] for c in slot_data['citations'])),
                    ))

    @staticmethod
    def _dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def navigate(self, question, query_vectors, chunk_map, top_slots=8, min_sim=0.52):
        """Return candidate chunk rows pointed to by the most relevant Method Card slots."""
        valid_q = [q for q in (query_vectors or []) if q]
        if not valid_q or not self.slots_index:
            return [], []
        named_papers = {g['paper_id'] for g in source_groups(question, chunk_map)}
        scored = []
        for entry in self.slots_index:
            sim = max(self._dot(q, entry['vector']) for q in valid_q)
            boost = 0.04 if entry['paper_id'] in named_papers else 0.0
            scored.append((sim + boost, sim, entry))
        scored.sort(key=lambda x: (-x[0], x[2]['slot_id']))
        selected_slots = []
        seen_chunks = {}
        for eff, raw_sim, entry in scored:
            if raw_sim < min_sim and entry['paper_id'] not in named_papers:
                continue
            if raw_sim < (min_sim - 0.08):
                continue
            selected_slots.append(dict(slot_id=entry['slot_id'], title=entry['title'], slot=entry['slot'],
                                       similarity=round(raw_sim, 4), chunk_ids=entry['chunk_ids']))
            for cid in entry['chunk_ids']:
                if cid in chunk_map and (cid not in seen_chunks or raw_sim > seen_chunks[cid]['score']):
                    seen_chunks[cid] = dict(chunk_id=cid, score=round(raw_sim, 4), slot=entry['slot'], paper_id=entry['paper_id'])
            if len(selected_slots) >= top_slots:
                break
        chunk_rows = sorted(seen_chunks.values(), key=lambda x: (-x['score'], x['chunk_id']))
        return chunk_rows, selected_slots
