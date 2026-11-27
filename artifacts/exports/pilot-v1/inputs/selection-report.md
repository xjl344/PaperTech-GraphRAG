# 阶段 0 / 步骤 3：试点选材

- 主题：LLM 与知识图谱结合的检索及多跳问答。
- 规模：14 篇，含 12 篇方法、1 篇综述、1 篇基准。
- 用户明确允许 14 篇，候选全部通过预检后保留；没有为固定数量剔除合格论文。
- 环境：Python 3.14.6 / PyMuPDF 2.1；已安装并完成实际 PDF 解析。

## 选择依据与问题示例

| 编号 | 论文 | 用途与选择理由 | 可测试问题（非正式金标） | 证据 PDF 页 |
|---|---|---|---|---|
| Methods-015 | Think-on-Graph 2.0 | 方法：结构化图与非结构化文本交替检索，覆盖混合证据来源。 | ToG-2 为什么交替执行图检索和上下文检索？ | 1 |
| Methods-018 | Tree-of-Traversals | 方法：以动作接口和树搜索访问一个或多个 KG，可测试工具接口及跨图检索描述。 | Tree-of-Traversals 如何让黑盒 LLM 访问知识图谱？ | 1 |
| Methods-024 | LPKG | 方法：用 KG 派生规划训练数据，并讨论逻辑问答基准，可与免训练方法比较使用条件。 | LPKG 使用什么数据改善小模型的规划能力？ | 1 |
| Methods-035 | HippoRAG | 方法：采用 KG 和 Personalized PageRank，提供与逐步路径搜索不同的检索机制。 | HippoRAG 将哪几类组件组合用于知识整合？ | 1 |
| Methods-059 | CuriousLLM | 方法：正文明确基于 KGP 加入追问式检索，适合核查可溯源的方法变化和停止条件。 | Follow-upQA 的追问何时表示证据已充分？ | 1 |
| Methods-112 | G-Retriever | 方法：文本属性图和子图检索提供另一种图表示、优化与训练设置。 | G-Retriever 将图检索建模为何种优化问题？ | 1 |
| Methods-181 | KG-GPT | 方法：三阶段流程同时涵盖 KGQA 和事实核验，适合验证任务与流水线字段。 | KG-GPT 包含哪三个步骤？ | 1 |
| Methods-191 | RoG | 方法：规划—检索—推理及关系路径，适合核查训练依赖与路径约束。 | RoG 如何将关系路径用作检索计划？ | 1 |
| Methods-209 | KGP | 方法：由文档片段/结构建立图并进行遍历，是多文档问答与 CuriousLLM 对照的原始方法材料。 | KGP 图中的节点和边分别表示什么？ | 1 |
| Methods-211 | MindMap | 方法：以医疗领域问答和 KG 提示补充场景差异，防止将同名指标误当可比实验。 | MindMap 如何结合模型隐式知识和外部 KG 知识？ | 1 |
| Methods-215 | Think-on-Graph | 方法：免训练的 KG 交互式 beam search，可与 ToG-2 的混合来源检索做机制对照。 | ToG 的 LLM agent 如何探索知识图谱？ | 1 |
| Methods-229 | StructGPT | 方法：专用接口读取和推理分离，覆盖 KG、表格和数据库等结构化数据场景。 | StructGPT 如何分离结构化数据读取和推理？ | 1 |
| Surveys-010 | Unifying LLMs and KGs: A Roadmap | 综述：提供三类 LLM/KG 融合框架作为术语与分类背景，不作为某一方法的独立性能证明。 | Roadmap 将 LLM 与 KG 融合分为哪三类框架？ | 1 |
| Resources-002 | STaRK | 基准：文本与关系联合检索，覆盖商品、学术论文和医疗领域，提供评测任务差异材料。 | STaRK 的半结构化检索基准覆盖哪些领域？ | 1 |

## 可解析性与来源检查

全部 14 篇逐页打开与提取，共 307 页；单篇 11–31 页。没有空文本文件，没有去除首尾空白后少于 100 字符的页面，没有密码、超时或解析异常。

14 篇源文件的 SHA-256 均与步骤 2 基线一致，且预检前后未变。清单再次生成时也重新核对源文件哈希。预检只写项目 artifacts，不保存或修改 PDF。

首次 get_text(sort=True) 将部分双栏文字按坐标交错拼接；对照 PDF 首页和 sort=False 的文本后，采用原内容流顺序重跑全部预检。已渲染并检查 14 篇首页概览 first-pages-contact-sheet.png。视觉检查范围是首页，逐页字符统计不能证明所有公式、表格、段落阅读顺序均正确。

selection_evidence 使用 PDF 的物理页号（从 1 开始），字符范围为对应预览页面文本中的 Python 字符索引，左闭右开。引句是定位窗口，可能止于句中；它们用于核查选材依据，不是阶段 1 的稳定片段或人工金标。

## 比较机会与限制

CuriousLLM 在正文第 1、3–5 页明确讨论 KGP、MDR-KG、追问机制和对照设置，可作为后续关系审核的候选。ToG 与 ToG-2 可对照图路径搜索及图/文混合检索机制；本步骤未据名称自动建立 IMPROVES_UPON 等关系。

多篇论文涉及多跳 QA，但输入知识源、模型、训练方式、样本划分与指标不同，不能将论文报告分数直接排序当作公平优劣。G-Retriever、医疗领域 MindMap、STaRK 等提供任务差异；综述仅提供背景分类。当前集合支持证据查找和方法比较的初步题材，不承诺支撑既定 50 题分布或完整技术演进链。

主题由实际目录和候选正文决定。其余 249 篇未进入本轮内容预检，原因是控制单步选材范围；不将它们标记为失败或低质量，也未宣称完成全部语料内容综述。

## 标题与版本备注

- Methods-015：CSV 标题包含 Interpretable；PDF 首页为 Deep and Faithful ... Knowledge-Guided Retrieval Augmented Generation，保留原索引不改写。
- Methods-059：CSV 为 Reasoning-Infused Knowledge Graph Prompting；PDF 当前标题为 LLM-Enhanced Knowledge Graph Reasoning，保留两者。

## 数据流、文件与复现

papers_index.csv + 步骤 2 哈希清单 → probe-pilot.py 在独立子进程逐篇预检 → candidate-checks.json 与逐页预览 → 经阅读记录的 pilot-notes.json → build-pilot-list.py → 试点 JSON/CSV 和本报告。每篇预检限 80 页、45 秒、每页 200,000 字符；失败记录后继续其他候选。

预检标识如 Methods-015 仅用于选材，不是正式 Paper ID。完整原始路径、哈希、页数、用途、示例问题和可回查引句位于 pilot-selection.json；CSV 便于人工查看。预览并非正式解析底座，尚无稳定分块、幂等入库或检索索引。

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --cache-dir .cache\pip -r requirements-pdf.txt
.\.venv\Scripts\python.exe -X utf8 scripts\probe-pilot.py
.\.venv\Scripts\python.exe -X utf8 scripts\build-pilot-list.py
```

首次安装软件包需要网络；PDF 预检和清单生成均为本地操作。当前安装可导入并完成 14 篇解析，只能证明本次 PDF 依赖在 Python 3.14 下可用，不能推断整个后续技术栈兼容。实际安装版本另存 environment-freeze.txt。

本步骤完成选材并停下。下一步为阶段 0 / 步骤 4：冻结试点清单版本、选择理由和哈希基线；暂未开始阶段 1 的解析与稳定分块。
