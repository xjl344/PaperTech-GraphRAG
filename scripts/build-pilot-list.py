"""Build a reviewable pilot list from local probe output and reviewed notes."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'artifacts/reports/stage-0-step-3'


def main():
    checks = json.loads((FOLDER / 'candidate-checks.json').read_text(encoding='utf-8'))
    lookup = {r['candidate_id']: r for r in checks['candidates']}
    notes = json.loads((FOLDER / 'pilot-notes.json').read_text(encoding='utf-8'))
    if len(notes) != 14 or len({n['id'] for n in notes}) != 14:
        raise ValueError('Expected 14 unique pilot notes')
    selected = []
    for note in notes:
        record = dict(lookup[note['id']])
        if record['status'] != 'text_available' or not record['source_hash_unchanged']:
            raise ValueError(f"Preflight not passed: {note['id']}")
        with (ROOT / 'database' / record['relative_path']).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != record['sha256']:
                raise ValueError(f"Source changed: {note['id']}")
        preview = json.loads((FOLDER / record['preview_file']).read_text(encoding='utf-8'))
        evidence = None
        for page in preview['pages']:
            start = page['text'].find(note['anchor'])
            if start >= 0:
                end = min(len(page['text']), start + 650)
                evidence = {'pdf_page': page['pdf_page'], 'start_char': start, 'end_char': end,
                            'quote': page['text'][start:end]}
                break
        if evidence is None:
            raise ValueError(f"Reviewed anchor missing: {note['id']}")
        record.update(note)
        record['selection_evidence'] = evidence
        record['question_status'] = 'selection example only; not a frozen evaluation item or gold answer'
        selected.append(record)

    result = {'selection_revision': 'draft-1', 'count': len(selected),
              'topic': 'LLM 与知识图谱结合的检索及多跳问答',
              'decision': '用户允许将原定 10 篇调整为 14 篇；候选均通过预检后全部保留。',
              'status': 'stage-0-step-3 selection; formal manifest freeze remains step 4',
              'pilots': selected}
    (FOLDER / 'pilot-selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    columns = ['candidate_id', 'name', 'role', 'relative_path', 'sha256', 'page_count', 'total_characters', 'reason', 'question', 'title_note']
    with (FOLDER / 'pilot-selection.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(selected)

    lines = ['# 阶段 0 / 步骤 3：试点选材', '',
             f"- 主题：{result['topic']}。", '- 规模：14 篇，含 12 篇方法、1 篇综述、1 篇基准。',
             '- 用户明确允许 14 篇，候选全部通过预检后保留；没有为固定数量剔除合格论文。',
             f"- 环境：Python 3.14.6 / PyMuPDF {checks['pymupdf']}；已安装并完成实际 PDF 解析。", '',
             '## 选择依据与问题示例', '',
             '| 编号 | 论文 | 用途与选择理由 | 可测试问题（非正式金标） | 证据 PDF 页 |',
             '|---|---|---|---|---|']
    for r in selected:
        lines.append(f"| {r['candidate_id']} | {r['name']} | {r['role']}：{r['reason']} | {r['question']} | {r['selection_evidence']['pdf_page']} |")
    lines += ['', '## 可解析性与来源检查', '',
              f"全部 14 篇逐页打开与提取，共 {sum(r['page_count'] for r in selected)} 页；单篇 {min(r['page_count'] for r in selected)}–{max(r['page_count'] for r in selected)} 页。没有空文本文件，没有去除首尾空白后少于 100 字符的页面，没有密码、超时或解析异常。", '',
              '14 篇源文件的 SHA-256 均与步骤 2 基线一致，且预检前后未变。清单再次生成时也重新核对源文件哈希。预检只写项目 artifacts，不保存或修改 PDF。', '',
              '首次 get_text(sort=True) 将部分双栏文字按坐标交错拼接；对照 PDF 首页和 sort=False 的文本后，采用原内容流顺序重跑全部预检。已渲染并检查 14 篇首页概览 first-pages-contact-sheet.png。视觉检查范围是首页，逐页字符统计不能证明所有公式、表格、段落阅读顺序均正确。', '',
              'selection_evidence 使用 PDF 的物理页号（从 1 开始），字符范围为对应预览页面文本中的 Python 字符索引，左闭右开。引句是定位窗口，可能止于句中；它们用于核查选材依据，不是阶段 1 的稳定片段或人工金标。', '',
              '## 比较机会与限制', '',
              'CuriousLLM 在正文第 1、3–5 页明确讨论 KGP、MDR-KG、追问机制和对照设置，可作为后续关系审核的候选。ToG 与 ToG-2 可对照图路径搜索及图/文混合检索机制；本步骤未据名称自动建立 IMPROVES_UPON 等关系。', '',
              '多篇论文涉及多跳 QA，但输入知识源、模型、训练方式、样本划分与指标不同，不能将论文报告分数直接排序当作公平优劣。G-Retriever、医疗领域 MindMap、STaRK 等提供任务差异；综述仅提供背景分类。当前集合支持证据查找和方法比较的初步题材，不承诺支撑既定 50 题分布或完整技术演进链。', '',
              '主题由实际目录和候选正文决定。其余 249 篇未进入本轮内容预检，原因是控制单步选材范围；不将它们标记为失败或低质量，也未宣称完成全部语料内容综述。', '',
              '## 标题与版本备注', '']
    for r in selected:
        if r.get('title_note'):
            lines.append(f"- {r['candidate_id']}：{r['title_note']}")
    lines += ['', '## 数据流、文件与复现', '',
              'papers_index.csv + 步骤 2 哈希清单 → probe-pilot.py 在独立子进程逐篇预检 → candidate-checks.json 与逐页预览 → 经阅读记录的 pilot-notes.json → build-pilot-list.py → 试点 JSON/CSV 和本报告。每篇预检限 80 页、45 秒、每页 200,000 字符；失败记录后继续其他候选。', '',
              '预检标识如 Methods-015 仅用于选材，不是正式 Paper ID。完整原始路径、哈希、页数、用途、示例问题和可回查引句位于 pilot-selection.json；CSV 便于人工查看。预览并非正式解析底座，尚无稳定分块、幂等入库或检索索引。', '',
              '```powershell', '.\\.venv\\Scripts\\python.exe -m pip install --only-binary=:all: --cache-dir .cache\\pip -r requirements-pdf.txt',
              '.\\.venv\\Scripts\\python.exe -X utf8 scripts\\probe-pilot.py',
              '.\\.venv\\Scripts\\python.exe -X utf8 scripts\\build-pilot-list.py', '```', '',
              '首次安装软件包需要网络；PDF 预检和清单生成均为本地操作。当前安装可导入并完成 14 篇解析，只能证明本次 PDF 依赖在 Python 3.14 下可用，不能推断整个后续技术栈兼容。实际安装版本另存 environment-freeze.txt。', '',
              '本步骤完成选材并停下。下一步为阶段 0 / 步骤 4：冻结试点清单版本、选择理由和哈希基线；暂未开始阶段 1 的解析与稳定分块。', '']
    (FOLDER / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Built {len(selected)} pilot entries and report')


if __name__ == '__main__':
    main()
