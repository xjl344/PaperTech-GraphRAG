"""User-facing PaperTech Q&A workbench styled with Minimalism & Swiss Academic design system."""
import html
import json
from pathlib import Path
import re
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from papertech.settings import settings
from papertech.corpus import load_corpus
from papertech.cloud_embeddings import configured as cloud_bge_configured

st.set_page_config(
    page_title='PaperTech 论文问答',
    page_icon=':material/menu_book:',
    layout='centered',
    initial_sidebar_state='collapsed',
)

# Design System: Minimalism & Swiss Style + Academic Palette (#2563EB Primary, #F8FAFC Canvas, #0F172A Ink)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@600;700&display=swap');

    :root {
        --pt-primary: #2563EB;
        --pt-primary-soft: #EFF6FF;
        --pt-primary-border: #BFDBFE;
        --pt-bg: #F8FAFC;
        --pt-surface: #FFFFFF;
        --pt-border: #E2E8F0;
        --pt-ink: #0F172A;
        --pt-muted: #475569;
        --pt-accent: #D97706;
    }

    [data-testid="stAppDeployButton"] { display: none; }
    .stApp {
        background-color: var(--pt-bg);
        color: var(--pt-ink);
        font-family: 'Atkinson Hyperlegible', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    .block-container {
        padding-top: 3.25rem;
        padding-bottom: 3.5rem;
        max-width: 840px;
    }

    /* Header */
    .pt-hero {
        margin-bottom: 1.25rem;
    }
    .pt-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: var(--pt-primary);
        background: var(--pt-primary-soft);
        border: 1px solid var(--pt-primary-border);
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 0.65rem;
    }
    .pt-title {
        font-family: 'Crimson Pro', 'Noto Serif SC', Georgia, serif;
        font-size: 2.15rem;
        font-weight: 700;
        line-height: 1.2;
        color: var(--pt-ink);
        margin: 0 0 0.4rem 0;
    }
    .pt-subtitle {
        color: var(--pt-muted);
        font-size: 0.98rem;
        line-height: 1.55;
        margin: 0;
    }

    /* Form & Interactive Controls (min 44px touch targets, clear focus rings) */
    [data-testid="stForm"] {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-radius: 12px;
        padding: 1rem 1.1rem 1.05rem 1.1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .stTextArea textarea {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        color: var(--pt-ink) !important;
        background: #FFFFFF !important;
        border-radius: 8px !important;
    }
    .stButton > button, .stFormSubmitButton > button {
        min-height: 44px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: background-color 180ms ease, border-color 180ms ease, transform 120ms ease !important;
    }
    .stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible {
        outline: 2px solid var(--pt-primary) !important;
        outline-offset: 2px !important;
    }
    .stButton > button[kind="secondary"] {
        background: var(--pt-surface) !important;
        border: 1px solid var(--pt-border) !important;
        color: var(--pt-ink) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.65rem 0.9rem !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        line-height: 1.45 !important;
        height: auto !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--pt-primary) !important;
        background: var(--pt-primary-soft) !important;
        color: var(--pt-primary) !important;
    }

    /* Answer Card */
    .pt-question-h2 {
        font-size: 1.32rem;
        font-weight: 700;
        line-height: 1.4;
        color: var(--pt-ink);
        margin: 1.4rem 0 0.75rem 0;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid var(--pt-border);
    }
    .pt-answer-card {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-radius: 12px;
        padding: 1.2rem 1.35rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
        font-size: 1.02rem;
        line-height: 1.82;
        color: var(--pt-ink);
    }
    .pt-cite {
        display: inline-block;
        font-size: 0.74rem;
        font-weight: 700;
        line-height: 1;
        color: var(--pt-primary);
        background: var(--pt-primary-soft);
        border: 1px solid var(--pt-primary-border);
        border-radius: 4px;
        padding: 2px 5px;
        margin: 0 2px;
        vertical-align: super;
    }

    /* Sources Section */
    .pt-sources-h3 {
        font-size: 1rem;
        font-weight: 700;
        color: var(--pt-ink);
        margin: 1.1rem 0 0.6rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pt-quote {
        background: #F8FAFC;
        border-left: 3px solid var(--pt-primary);
        padding: 0.85rem 1.05rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.94rem;
        line-height: 1.7;
        color: #1E293B;
        white-space: pre-wrap;
        margin: 0.25rem 0 0.65rem 0;
    }
    .pt-meta {
        color: var(--pt-muted);
        font-size: 0.84rem;
        line-height: 1.45;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition: none !important;
            animation: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def current_corpus():
    return load_corpus(ROOT)


def format_pages(page_start, page_end):
    if page_start is None:
        return ''
    if page_end is None or page_end == page_start:
        return f'第 {page_start} 页'
    return f'第 {page_start}–{page_end} 页'


def format_answer_and_sources(result, chunk_map):
    """Map internal [E1:q2] / [chunk_xxx] markers into clean sequential [1], [2] citations."""
    answer = str(result.get('answer') or '').strip()
    raw_citations = result.get('citations') or []
    sources = []
    pair_to_num = {}
    eid_to_nums = {}
    cid_to_nums = {}

    for item in raw_citations:
        cid = item.get('chunk_id', '')
        eid = item.get('eid', '')
        qid = item.get('quote_id', '')
        quote = (item.get('quote') or '').strip()
        dedup_key = (cid, quote)
        existing = next((idx for idx, s in enumerate(sources, 1) if s['_key'] == dedup_key), None)
        if existing is None:
            full_chunk = chunk_map.get(cid) or {}
            num = len(sources) + 1
            sources.append(dict(
                num=num,
                title=item.get('title') or full_chunk.get('title') or '未命名论文',
                page_start=item.get('page_start', full_chunk.get('page_start')),
                page_end=item.get('page_end', full_chunk.get('page_end')),
                quote=quote,
                full_text=(full_chunk.get('text') or '').strip(),
                filename=Path(item.get('source_relative_path') or full_chunk.get('source_relative_path') or '').name,
                chunk_id=cid,
                _key=dedup_key,
            ))
        else:
            num = existing
        if eid and qid:
            pair_to_num[(eid, qid)] = num
        if eid:
            eid_to_nums.setdefault(eid, [])
            if num not in eid_to_nums[eid]:
                eid_to_nums[eid].append(num)
        if cid:
            cid_to_nums.setdefault(cid, [])
            if num not in cid_to_nums[cid]:
                cid_to_nums[cid].append(num)

    def _replace_bracket(match):
        inner = match.group(1)
        parts = [p.strip() for p in re.split(r'[,，]', inner) if p.strip()]
        nums = []
        matched_any = False
        last_eid = None
        for token in parts:
            m_pair = re.fullmatch(r'(E[1-9][0-9]*):(q[1-9][0-9]*)', token)
            if m_pair:
                eid, qid = m_pair.group(1), m_pair.group(2)
                last_eid = eid
                if (eid, qid) in pair_to_num:
                    nums.append(pair_to_num[(eid, qid)])
                    matched_any = True
                elif eid in eid_to_nums:
                    nums.extend(eid_to_nums[eid])
                    matched_any = True
            elif re.fullmatch(r'E[1-9][0-9]*', token) and token in eid_to_nums:
                last_eid = token
                nums.extend(eid_to_nums[token])
                matched_any = True
            elif re.fullmatch(r'q[1-9][0-9]*', token) and last_eid and (last_eid, token) in pair_to_num:
                nums.append(pair_to_num[(last_eid, token)])
                matched_any = True
            elif token in cid_to_nums:
                nums.extend(cid_to_nums[token])
                matched_any = True
        if not matched_any:
            return match.group(0)
        uniq = list(dict.fromkeys(nums))
        return ''.join(f'[{n}]' for n in uniq)

    clean_answer = re.sub(r'\[([^\[\]\n]+)\]', _replace_bracket, answer)
    clean_answer = re.sub(r'(\[\d+\])\1+', r'\1', clean_answer)

    fallback_sources = []
    if not sources and result.get('evidence'):
        for idx, e in enumerate(result['evidence'][:5], 1):
            full_chunk = chunk_map.get(e.get('chunk_id', '')) or {}
            fallback_sources.append(dict(
                num=idx,
                title=e.get('title') or full_chunk.get('title') or '未命名论文',
                page_start=e.get('page_start', full_chunk.get('page_start')),
                page_end=e.get('page_end', full_chunk.get('page_end')),
                quote=(e.get('quote') or '').strip(),
                full_text=(full_chunk.get('text') or '').strip(),
                filename=Path(e.get('source_relative_path') or full_chunk.get('source_relative_path') or '').name,
                chunk_id=e.get('chunk_id', ''),
            ))
    return clean_answer, sources, fallback_sources


def render_answer_html(clean_answer):
    """Escape raw text safely, preserve line breaks, and turn [1] into crisp citation badges."""
    escaped = html.escape(clean_answer)
    with_badges = re.sub(r'\[(\d+)\]', r'<sup class="pt-cite">\1</sup>', escaped)
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', with_badges) if p.strip()]
    if not paragraphs:
        return f'<div class="pt-answer-card">{with_badges}</div>'
    body = ''.join(f'<p style="margin:0 0 0.75rem 0;">{p.replace(chr(10), "<br>")}</p>' for p in paragraphs[:-1])
    body += f'<p style="margin:0;">{paragraphs[-1].replace(chr(10), "<br>")}</p>'
    return f'<div class="pt-answer-card">{body}</div>'


cfg = settings(ROOT)
corpus_id, papers, chunks = current_corpus()
chunk_map = {c['chunk_id']: c for c in chunks}
default_mode = 'cloud' if cloud_bge_configured(cfg) else 'local'

# Sidebar (collapsed by default): indexed papers list + opt-in Developer Mode
with st.sidebar:
    st.subheader(f'已收录论文（{len(papers)} 篇）')
    for idx, p in enumerate(papers, 1):
        st.markdown(f"{idx}. {p['title']}")
    st.divider()
    dev_mode = st.toggle('开发者模式', value=False, key='dev_mode',
                         help='仅用于排查与调试，开启后显示检索参数、知识图谱审核与运行日志。')
    if dev_mode:
        st.caption('检索与生成开关')
        mode = st.segmented_control('问题向量来源', ['cloud', 'local', 'none'], default=default_mode,
                                    format_func=lambda x: {'cloud': '云端 BGE-M3', 'local': '本地 BGE-M3', 'none': '仅全文'}[x],
                                    key='query_mode')
        rerank = st.toggle('本地 GPU 重排 (FP16)', value=True, key='rerank')
        query_planner = st.toggle('云端查询规划器', value=True, key='query_planner')
        use_graph_cards = st.toggle('QA-Graph + 方法卡导航', value=True, key='use_graph_cards')
        premise_check = st.toggle('前提核验', value=True, key='premise_check')
        st.caption(f"模型：{cfg.get('DEEPSEEK_MODEL') or '未配置'}")
    else:
        mode, rerank, query_planner, use_graph_cards, premise_check = default_mode, True, True, True, True

# Header (Hero with inline SVG icon, sequential h1)
st.markdown(
    f"""
    <div class="pt-hero">
        <div class="pt-hero-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            已收录 {len(papers)} 篇论文 · 逐字原文可溯源
        </div>
        <h1 class="pt-title">PaperTech 论文问答</h1>
        <p class="pt-subtitle">输入研究问题或跨论文对比问题，回答中的每条结论均附带论文原文摘录与页码出处（左上角可查看收录清单）。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if 'history' not in st.session_state:
    st.session_state.history = []
if 'draft_question' not in st.session_state:
    st.session_state.draft_question = ''

EXAMPLES = [
    'HippoRAG 如何检索多跳证据？',
    '比较 HippoRAG 与 RoG 的多跳检索机制，各自是否需要微调？',
    'G-Retriever 为什么不把大图全部转成文本交给模型？',
]

# Input form
with st.form('question_form', clear_on_submit=False):
    question = st.text_area(
        '输入你的研究问题',
        value=st.session_state.draft_question,
        placeholder='例如：比较 ToG 与 ToG-2 的检索流程有什么不同？',
        height=96,
        max_chars=2000,
        label_visibility='collapsed',
    )
    col_btn, col_clear = st.columns([4, 1], gap='small')
    submit = col_btn.form_submit_button('提问', type='primary', use_container_width=True)
    clear_clicked = col_clear.form_submit_button('清空', use_container_width=True)

if clear_clicked:
    st.session_state.history = []
    st.session_state.draft_question = ''
    st.rerun()

# Full-width clickable example questions when conversation is empty (prevents text truncation)
if not st.session_state.history:
    st.caption('试试以下问题：')
    for idx, ex in enumerate(EXAMPLES):
        if st.button(ex, key=f'ex_{idx}', use_container_width=True):
            st.session_state.draft_question = ex
            question = ex
            submit = True

if submit:
    q_text = (question or '').strip()
    if not q_text:
        st.warning('请先输入问题。')
    else:
        st.session_state.draft_question = ''
        with st.spinner('正在查阅论文原文并整理回答…'):
            workflow = None
            try:
                from papertech.workflow import Workflow
                workflow = Workflow.for_workbench(
                    ROOT, cfg, query_mode=mode or default_mode, rerank=rerank,
                    query_planner=query_planner, premise_check=premise_check,
                    use_graph_and_cards=use_graph_cards, async_trace_flush=True,
                )
                res = workflow.ask(q_text)
                st.session_state.history.insert(0, dict(question=q_text, result=res))
            except Exception as exc:
                st.error('服务暂时不可用，请确认本地数据库已启动。' + (f'（{type(exc).__name__}）' if dev_mode else ''))
            finally:
                if workflow is not None:
                    workflow.close()

# Render Q&A results (newest first)
for turn_idx, turn in enumerate(st.session_state.history):
    q_text = turn['question']
    result = turn['result']
    clean_answer, sources, fallback_sources = format_answer_and_sources(result, chunk_map)

    if turn_idx > 0:
        st.divider()
    st.markdown(f'<h2 class="pt-question-h2">{html.escape(q_text)}</h2>', unsafe_allow_html=True)

    status = result.get('status')
    if status == 'refused':
        st.info('未在当前论文库中找到足以支持该前提或问题的直接依据。')
    elif status == 'partial':
        st.caption('提示：当前论文库仅包含部分相关信息，已在回答中说明缺口。')
    elif status in ('error', 'citation_error'):
        st.warning('本次未能生成可核验的完整回答，下方已保留查找到的相关论文片段供参考。')

    st.markdown(render_answer_html(clean_answer), unsafe_allow_html=True)

    display_sources = sources if sources else fallback_sources
    if display_sources:
        heading = f'原文来源（{len(display_sources)} 处）' if sources else f'相关论文片段（{len(display_sources)} 处）'
        st.markdown(
            f'''<h3 class="pt-sources-h3">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" aria-hidden="true">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                {html.escape(heading)}
            </h3>''',
            unsafe_allow_html=True,
        )
        for s in display_sources:
            page_txt = format_pages(s['page_start'], s['page_end'])
            label = f"[{s['num']}] {s['title']}" + (f" · {page_txt}" if page_txt else '')
            with st.expander(label, expanded=(turn_idx == 0 and s['num'] <= 2)):
                st.markdown(f'<div class="pt-quote">{html.escape(s["quote"])}</div>', unsafe_allow_html=True)
                meta_parts = [p for p in (s['filename'], page_txt) if p]
                if meta_parts:
                    st.markdown(f'<div class="pt-meta">出处：{html.escape(" · ".join(meta_parts))}（PDF 物理页码）</div>', unsafe_allow_html=True)
                if s['full_text'] and s['full_text'] != s['quote']:
                    with st.popover('查看所在完整段落'):
                        st.text(s['full_text'])

    # Developer-only diagnostic details (hidden for end users)
    if dev_mode:
        with st.expander('开发者诊断信息（前提核验 / 规划 / 耗时 / 原始 JSON）', expanded=False):
            timings = result.get('stage_timings') or []
            total_s = sum(t.get('seconds') or 0 for t in timings)
            st.caption(f"status=`{status}` · model=`{result.get('model_name')}` · total={total_s:.2f}s · req=`{result.get('request_id')}`")
            checks = result.get('premise_check') or []
            if checks:
                st.markdown('**前提核验**')
                st.dataframe([dict(前提=c.get('premise', ''), 支持=c.get('supported'), 证据=', '.join(c.get('evidence_eids') or []), 说明=c.get('note', ''))
                              for c in checks], use_container_width=True, hide_index=True)
            summary = result.get('retrieval_summary') or {}
            qplan = summary.get('query_plan') or {}
            if qplan:
                st.markdown(f"**查询规划**：`{qplan.get('decision')}`" + (' (fast_path)' if qplan.get('fast_path') else ''))
                if qplan.get('subqueries'):
                    st.dataframe(qplan['subqueries'], use_container_width=True, hide_index=True)
            if timings:
                st.dataframe(timings, use_container_width=True, hide_index=True)
            st.json({k: result.get(k) for k in ('retrieval_summary', 'errors', 'usage', 'local_trace_id', 'trace_flush_mode')}, expanded=False)
            st.download_button('导出 JSON', json.dumps(result, ensure_ascii=False, indent=2),
                               file_name=f"{result['request_id']}.json", mime='application/json', key=f'dl_{turn_idx}')

# Developer-only KG review console (hidden for end users)
if dev_mode:
    st.divider()
    with st.expander('开发者：知识图谱抽取进度与人工复核', expanded=False):
        from papertech.kg import KGLedger
        ledger = KGLedger(ROOT)
        try:
            progress = ledger.progress()
            if progress:
                run = progress['run']
                done = run['completed_chunks'] + run['reused_chunks']
                st.caption(f"进度：{done}/{run['total_chunks']} · {run['status']} · 已批准 {progress['claims_by_review_status'].get('approved', 0)} · 待复核 {progress['claims_by_review_status'].get('pending', 0)}")
            pending = ledger.pending_claims(corpus_id, limit=200)
            if pending:
                labels = [f"{c['paper_title']} · p.{c['page_start']} · {c['subject']} —{c['predicate']}→ {c['object']}" for c in pending]
                choice = st.selectbox('待复核关系', range(len(pending)), format_func=lambda i: labels[i], key='kg_review_choice')
                claim = pending[choice]
                st.info(claim['evidence_quote'])
                note = st.text_input('审核备注', key='kg_review_note')
                left, right = st.columns(2)
                if left.button('批准并写入图谱', type='primary', key='kg_approve'):
                    from papertech.graph_store import GraphStore
                    approved = ledger.update_review(claim['claim_id'], 'approved', note)
                    graph = GraphStore(settings(ROOT), corpus_id)
                    try:
                        graph.ensure_kg_schema()
                        graph.write_kg_claim(dict(approved, corpus_id=corpus_id, review_status='approved'))
                        ledger.mark_graph_written(claim['claim_id'])
                    finally:
                        graph.close()
                    st.success('已写入 Neo4j。')
                    st.rerun()
                if right.button('拒绝候选', key='kg_reject'):
                    ledger.update_review(claim['claim_id'], 'rejected', note)
                    st.rerun()
            else:
                st.caption('当前没有待复核的关系候选。')
        finally:
            ledger.close()
