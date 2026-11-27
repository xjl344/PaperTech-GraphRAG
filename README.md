# PaperTech-GraphRAG

本机单用户论文证据研究工作台（当前冻结 14 篇 GraphRAG 论文、980 个正文/附录分块）。生产默认链路（`Workflow.for_workbench`）已升级为：**云端查询规划器（多跳拆解 + 简单单论文快速通道）→ Cloudflare BGE-M3 + Neo4j 双路混合召回 → 查询感知 QA-Graph + 14 篇结构化方法卡导航 → 上下文增强本地 GPU FP16 重排 → Balanced-MMR 多样性证据预算（18KB / 12 块）→ `source-choice-v3` (`[E#:q#]`) 单点引用与前提核验（`premise_check`）→ 后台异步 LangSmith Trace**。

最新实测验收（均已同步 LangSmith Dataset/Experiment 且远端批量核验 100% 通过）：
- **40 题开发集最终闭环 (`benchmark-v5-final-v1`)**：32 题来源覆盖 **87.50%**（25/32 全覆盖；事实 100%、跨论文 83.33%），输出 Token 下降 23.4%，8/8 反例全部语义识破，详见 [40 题报告](artifacts/reports/stage-4/benchmark-v5-final-v1/runs/142445977caf4321998af9713424faba/report/findings.md)。
- **18 题全新未见泛化集 (`benchmark-holdout-v1`，与旧 40 题零重叠)**：对比优化前基线 `Legacy-Hybrid`，14 题来源覆盖 **46.43% → 95.24%（+48.81 pp，10 增 / 4 平 / 0 退，上游零漏检）**，4/4 反例全部规范拒答，可交付语义完整正确率（`ai_delegated`）**4/18 → 15/18（原始生成 18/18 均正确，3 条格式边界已在生产解析器修补）**，详见 [18 题泛化报告](artifacts/reports/stage-4/benchmark-holdout-v1/runs/f3889ede3e1a47598620e440f38c6f6f/report/findings.md) 与 [逐题语义核查](artifacts/reports/stage-4/benchmark-holdout-v1/runs/f3889ede3e1a47598620e440f38c6f6f/report/semantic-review.md)。
- **全量回归测试**：`221/221` 项单元测试全部通过。

## 生产工作台一键启动（Windows / PowerShell）

在 `E:\PaperTech-GraphRAG` 目录运行（[scripts/run.ps1](scripts/run.ps1) 会自动处理 E 盘缓存路径，并在 `.venv` 遇到 `_ctypes` 限制时自动回退基础解释器 + `PYTHONPATH`）：

```powershell
# 0) 首次或重启电脑后，先确保本地 E 盘 Neo4j 已启动
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-neo4j.ps1 -Start

# 1) 启动本地 Streamlit 网页工作台（启动后浏览器打开 http://127.0.0.1:8501）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ui

# 2) 单次生产问答（默认启用全部优化配置与异步 Trace）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ask -QueryMode cloud -Question "比较 HippoRAG 与 RoG 的多跳检索机制"

# 3) 常驻交互对话（预热一次 GPU 重排器，连续提问更快；/exit 退出）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task chat -QueryMode cloud

# 4) 运行全部 221 条本地单元测试（不产生云端调用）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task test-all
```

> 网页端（[app.py](app.py)）左侧边栏可随时开关：向量来源（云端/本地/仅全文）、本地 GPU 重排、云端查询规划器、QA-Graph + 14 篇方法卡导航、前提核验；主界面支持展示前提核验表、查询规划与方法卡命中槽位、图路径、`[E#:q#]` 逐字核验引文与原文证据定位。

## 阶段 1：快速运行（PDF 解析与冻结语料）

在 `E:\PaperTech-GraphRAG` 中运行。当前使用项目 `.venv` 中的 Python 3.14.6；现有基础解释器仍位于原 C 盘位置。无需激活环境，也不依赖 `py` 启动器。

首次准备 PDF 依赖（已经安装时可跳过）：

```powershell
New-Item -ItemType Directory -Force -Path .cache\temp | Out-Null
$env:TEMP = Join-Path (Get-Location) '.cache\temp'
$env:TMP = $env:TEMP
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --cache-dir .cache\pip -r requirements-pdf.txt
```

日常运行：

```powershell
# 本地处理完整的 14 篇冻结试点；已有结果校验后复用
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ingest

# 实际重解析，并比较相同版本的结果；不会覆盖不同的旧结果
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ingest -ForceReparse

# 独立复核原文、定位和重跑稳定性
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task verify

# 合成 PDF 故障注入与回归测试
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task test
```

`ExecutionPolicy Bypass` 仅针对这个 PowerShell 进程，不修改用户或系统的永久策略。若只想运行 Python，可以直接执行 `scripts/ingest-pilot.py`、`scripts/verify-ingestion.py` 或 `scripts/test-ingestion.py`；推荐通过 `run.ps1`，它会将本进程 `TEMP/TMP`、pip 缓存和 Python 字节码缓存放入 E 盘项目 `.cache`。

阶段 1 不需要 API Key、模型、数据库服务或联网。只有首次安装依赖需要下载软件包。

## 数据流与代码入口

`pilot-v1` 冻结清单 → 校验源 PDF 哈希 → SQLite 提交任务状态 → 独立子进程本地提取 → 按章节候选和长度预算分块 → 核查原文范围 → 提交解析结果与终态 → 独立验证。

- `src/papertech/pdf.py`：页面文本、块坐标、章节候选、稳定分块和范围校验。
- `src/papertech/ingest.py`：SQLite 任务状态、子进程超时、失败隔离、缓存与历史版本。
- `scripts/ingest-pilot.py`：完整冻结试点的导入入口。
- `scripts/verify-ingestion.py`：重新读取所有源页面，验证全部片段范围并生成定位图。
- `tests/test_ingest.py`：原文定位、参考文献保护、失败隔离、版本历史、中断恢复等测试。

`Paper ID` 由相对路径和源内容哈希决定；`Parse ID` 还包括解析配置、PyMuPDF 版本和解析代码哈希；`Chunk ID` 绑定解析版本、页码/字符范围与文本哈希。源内容或处理策略变化会生成新结果，旧记录保留。

## 输出位置

| 路径 | 内容 |
|---|---|
| `database/` | 只读使用的原始 PDF 和 CSV；不移动、覆盖或重命名 |
| `artifacts/exports/pilot-v1/` | 冻结试点清单及选材依据 |
| `data/extracted/<paper_id>/<parse_id>/document.json` | 页面文本、位置、章节候选和片段 |
| `data/ingest.sqlite3` | 论文、解析、片段索引及逐次任务/运行状态 |
| `artifacts/logs/ingest/<run_id>/` | 每次批处理摘要、失败队列，重跑不覆盖以前的记录 |
| `artifacts/reports/stage-1/current-parses.json` | 独立验证后的当前版本白名单，后续阶段从此读取 |
| `artifacts/reports/stage-1/` | 阶段报告、完整性验证、定位样例图和测试证据 |

旧解析历史可能包含已修复策略生成的结果。后续索引必须只使用 `current-parses.json` 列出的已验证版本，不能将所有历史片段一起导入。

## 当前限制

章节边界由规则推测，所以文档状态明确为 `degraded`；这表示结构标签尚未经逐项人工确认，原文字符位置仍可精确核对。参考文献保留但不供方法关系抽取；无法识别参考文献边界时，该篇所有片段默认不进入关系抽取。

片段目标约 500 个估算 Token，并未加载模型分词器。页码是从 1 开始的 PDF 物理页号，字符范围对应当前解析版本的页面文本，采用左闭右开区间。坐标为原文文本块的边框，不能当作逐字符精确框。跨页片段逐段保存来源，不以单个页码掩盖跨页范围。

首版不做 OCR，也不恢复公式/表格结构；页眉页脚、脚注、图内文本可能保留在正文流中。模型依赖与后续技术栈的 Python 3.14 兼容性仍需逐项验证。

最新验收结果与已知限制见 [阶段 1 报告](artifacts/reports/stage-1/report.md)，详细目标见 [计划](plan.md)。

## 阶段 2：运行与配置

```powershell
# 依赖（已安装则跳过）；沿用上方 TEMP/TMP 设置
.\.venv\Scripts\python.exe -m pip install --cache-dir .cache\pip -r requirements-rag.txt

# 下载校验、配置、启动 E 盘本地 Neo4j；不安装 Windows 服务、不用 Docker
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-neo4j.ps1 -Start

# 本地向量构建，可续跑；随后幂等写入 Neo4j
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task embed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task index

# 显式使用本地查询向量；生成与追踪仍取决于现有配置
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ask -QueryMode local -Question 'HippoRAG 如何利用 Personalized PageRank 检索？'

# 省略 -QueryMode 时为 auto；当前已配置 Cloudflare，会使用云端查询向量
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ask -Question 'Think-on-Graph retrieval'

# 证据工作台（关闭 PowerShell 中的进程可停止）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ui

# 本地功能/故障测试，模拟供应商，不需要真实密钥
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task test-rag
```

工作台默认仅绑定 `127.0.0.1`。浏览器访问 Streamlit 控制台给出的本地地址。查询结果含原文、论文标题、源文件、PDF 物理页码、片段 ID 和跨页字符范围，可导出 JSON；证据查找结果不冒充模型答案。

`.env` 已生成并被 Git 忽略；本地 Neo4j 随机密码只放此文件。填写云端时参照 [.env.example](.env.example)：分别填 Base URL（到 `/v1` 或供应商 API 根路径）、API Key、准确模型 ID。程序会追加 `/embeddings` 或 `/chat/completions`，不要重复写这些尾部路径。DeepSeek thinking 关闭和 JSON 输出参数仍需实网核实，API 返回参数错误不会自动重试。

文档继续使用本地 BGE-M3 建库，当前在线查询使用已通过兼容性检查的 Cloudflare BGE-M3。DeepSeek、云端向量、LangSmith 均留空时不会调用这些服务；现有配置已填入，正式 Neo4j 问答会真实调用。`--backend offline` 不生成，但如选择 cloud 查询模式仍会请求查询向量；完全离线诊断须同时用 `--query-mode none`。402 阻止状态持久保存。

LangSmith 配置可用时，抽取尝试、审核、入图确认及问答节点/供应商调用默认在开始和结束时同步发送运行元数据。留空或上传失败时，事件按顺序保存在 `data/live-traces.sqlite3`，后续操作自动尝试补传；也可运行 `scripts/verify-live-traces.py --flush` 恢复队列。旧版问答快照仍留本地，`run.ps1 -Task traces` 是旧快照的显式补传入口，不参与实时 Token 汇总。上传成功后仅使用 SDK 返回的真实 URL；上传失败不阻断结果。元数据追踪不上传论文正文、引句、向量或模型原始输出。

本地 BGE-M3 仍只读复用原 CPU 环境用于离线建库。在线 reranker 使用项目 `.runtime/gpu-reranker` 内的 CUDA PyTorch，FP16、batch size 1，在同一父进程内复用；GPU 出错跳过并记录，不自动切到 CPU。Qwen 与 reranker 不同时驻留 GPU。模型均只从本地加载；Embedding 超过 8192 Token 明确失败，重排文本对最多 1024 Token，截断状态写入摘要。新 CLI 进程仍需冷启动，连续问答用下方 `chat`。

新增数据：`data/embeddings.sqlite3` 为按模型指纹/文本哈希的向量缓存；`data/rag.sqlite3` 为请求、节点、调用、候选、402 阻止和 Trace 队列；`.runtime/` 为 Neo4j、Java、数据库和日志；`.cache/model-jobs/` 为本地推理任务与日志。上述运行数据均留在 E 盘。报告见 [阶段 2 验证记录](artifacts/reports/stage-2/verification.json)。

学习调用链：`scripts/stage2.py` → `corpus.py` 校验当前白名单 → `workflow.py` 的 LangGraph 节点 → `graph_store.py` 双路召回 → `local_models.py` 本地重排 → `citations.py` 校验引句 → `audit.py` 落账。`providers.py` 只负责有界 HTTP 调用，`traces.py` 只负责有限补传，UI 复用同一个工作流。

## 阶段 3：可信建图与 GraphRAG

本阶段仅处理冻结的 14 篇试点。模型通过本机 Ollama `qwen2.5:7b-instruct` 对当前版本白名单里的正文/附录片段提出关系候选；参考文献片段不输入模型。候选必须属于固定的关系端点 Schema，且引句必须逐字出现在来源片段中。相似名称只按 Unicode 规范化后的精确名称合并，不做模糊自动消歧。候选先进入人工复核队列，只有批准关系会写入 Neo4j 并参与最多 2 跳图扩展。

```powershell
# 单片段本地冒烟已用于核实 Ollama 和结构化输出；完整试点抽取
.\.venv\Scripts\python.exe -X utf8 scripts\stage3.py extract

# 检查最近任务进度、逐篇状态、人工复核队列和 Neo4j 图计数
.\.venv\Scripts\python.exe -X utf8 scripts\stage3.py inspect

# 中断后按运行 ID 续跑，ID 显示在命令输出和 current-run.json 中
.\.venv\Scripts\python.exe -X utf8 scripts\stage3.py extract --resume <run_id>

# 打开含自动刷新进度和人工审核面板的工作台
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ui
```

每个正文片段的状态、错误类型和输入/输出 Token 保存在 `data/kg.sqlite3`；检查点和逐篇进度位于 `artifacts/reports/stage-3/runs/<run_id>/`。Ollama 每个片段的本地推理日志由服务管理。这里记录 Token 用量，不按货币估价。工作台的“批准并写入图谱”会再次核对当前 Neo4j 片段、解析版本、原文引句、页码和源文件哈希；图查询异常时会保留基础 Hybrid 结果。

2026-11-14：原 405 条候选经 AI 委托审核批准 83、拒绝 322；后续恢复的 3 个片段新增批准 6 条，当前批准 89、待审核 0，672 个抽取目标均已处理。审核身份、理由和时间保存在 SQLite、报告和 Neo4j；这不等同独立专家核验，也不保证关系召回完整。

监测交付使用 LangSmith 官方项目 `papertech`，当前格式为 `stage3-metadata-v2`；这是对已有运行记录的历史补传，不冒充实时采集。正式 Trace 链接、逐条审核、运行方式、验证证据和缺口见 [阶段 3 委托审核与追踪报告](artifacts/reports/stage-3/delegated-review/report.md)。`scripts/trace-stage3.py --upload` 显式补传元数据，`--verify-only` 仅核对远端；不会上传论文全文、引句或向量。每次补传同版本使用稳定 UUID。

后续运行默认使用 `papertech-live-v1` 实时事件。抽取的每次尝试在 `kg_attempts` 表单独记录，包含停止原因、HTTP 状态、Token、耗时、JSON 解析位置、错误堆栈位置及本地原始输出（已过滤已配置密钥）。仅观察到 `done_reason=length` 或输出 Token 达到额度时，才从 1200 提高至 2400、最多 4800；其他错误不自动增加额度。最终任务 Token 与“全部尝试 Token”分开记录，失败调用用量未知时不能视为零。已完成的历史运行和审核快照保持原样。

```powershell
# 新建单独运行，仅重试指定旧运行的失败片段
.\.venv\Scripts\python.exe -X utf8 scripts\stage3.py extract --retry-failed <run_id>

# 远端核对该次运行的终态、原生 Token，并取得官方 Trace URL
.\.venv\Scripts\python.exe -X utf8 scripts\verify-live-traces.py --flush --run-id <new_run_id>
```

补传只能恢复已保存事件；断网期间不保证实时可见。这里的实时指运行开始/结束事件实时发送，不代表模型逐 Token 流式上传或机器资源采样。重试修复的具体结果见 [诊断与实时追踪报告](artifacts/reports/stage-3/retry-diagnostics/report.md)。

## Cloudflare BGE-M3 查询配置

当前配置为 `CLOUD_BGE_PROVIDER=cloudflare`、`CLOUD_BGE_MODEL=@cf/baai/bge-m3`，使用 `CLOUDFLARE_ACCOUNT_ID` 与 `CLOUDFLARE_AUTH_TOKEN`。不使用 `CLOUD_BGE_API_KEY` 或 `CLOUD_BGE_BASE_URL`。兼容性探针已通过；当前接口不返回 Usage，按 unknown 保存。DeepSeek 使用用户配置的兼容平台，实测模型 ID 为 `deepseek-v4.1-flash-1017`，不宣称已验证 DeepSeek 官方端点。只统计 Token，不换算金额。

CLI 默认 `auto`：密钥未填时仍用本地问题向量；填写后选云端，但必须先通过兼容性检查，否则仅全文检索并明确降级。论文向量继续使用已有本地 BGE-M3 结果。两端模型同名、维度相同不能保证同一空间；检查比较4条中英文合成探针的本地/云端归一化向量，同文本余弦均≥0.999，并绑定本地模型指纹、供应商、地址和模型名，有效期30天。检查失败、错误或中断都会使旧批准失效。这是初步接入门槛，不替代阶段4检索质量评测。

```powershell
# 当前 Windows 环境可用的运行方式
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\stage3-live-pycache'
$taskPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'

# 填入密钥后再执行：仅发送4条固定合成探针，不发送论文正文
& $taskPython -X utf8 scripts/stage2.py compatibility

# 上一步通过后，CLI自动选择云端问题向量
& $taskPython -X utf8 scripts/stage2.py ask --question 'ToG 使用了哪些评测数据集？'

# 需要时仍可显式选择本地
& $taskPython -X utf8 scripts/stage2.py ask --query-mode local --question 'ToG'
```

已有工作台的来源选项仍由用户选择；本轮未修改网页。`.env` 已配置 `LOCAL_RERANKER_PERSISTENT=true`、cuda/float16 和项目 GPU 解释器，原有密钥保留。模型复用仅限同父进程，并非安装了 Windows 后台服务。

```powershell
# 使用上方 $taskPython 和 PYTHONPATH 设置。启动预热后可连续提问，/exit 退出。
& $taskPython -X utf8 scripts/stage2.py chat

# 本地回归，不使用真实供应商
& $taskPython -X utf8 -m unittest discover -s tests -v

# 只读复查已有验收结果、原文哈希与图谱血缘；不重新调用云端模型
& $taskPython -X utf8 scripts/report-stage3-online.py

# 明确要重新执行真实验收时才运行：会调用 Cloudflare 与 DeepSeek
& $taskPython -X utf8 scripts/verify-stage3-online.py
```

当前检查覆盖图超时保留 Hybrid、GPU/OOM 跳过、NaN 拒用、数据库断连不生成、未知结果不重发、引句编号越界拒绝及常驻进程复用。引句采用 `source-choice-v1`：程序切出原文选项，模型只选择编号，再校验对应原文；未放松逐字匹配。形式引用校验不能代替事实与引句的语义核对。资源、Token、真实 Trace、失败修复和已知限制见 [在线验收报告](artifacts/reports/stage-3/online/report.md)。

## 阶段 4：Hybrid 与 Hybrid＋Graph 对照

已冻结 24 道可回答题和 4 道反例，完成 56 次检索；预选 10 题进行两组回答，证据阶段拒答后实际调用 DeepSeek 各 8 次。两组共享问题向量、基础召回、重排模型、证据预算和生成设置，只启停图扩展。结果包含 [汇总与逐题对照表](artifacts/reports/stage-4/comparison.md)、[答案核查与失败分析](artifacts/reports/stage-4/answer-review.md) 和 [答案原文](artifacts/reports/stage-4/answers.md)。

本轮未观察到金标召回改善，发现图路径挤占有效证据、事实来源角色混淆，以及金标等价来源漏标。分数是已标注证据覆盖，不是答案准确率；完整路径金标、独立人工语义评分及质量门槛仍待完成，本轮不进入扩量。76 项回归通过，165 个 LangSmith Span 已远端核验。

```powershell
# 复用上方 $taskPython、PYTHONPATH；只读已有运行与 Neo4j，重建结果表，不调用模型
& $taskPython -X utf8 scripts/report-stage4.py
```

`freeze-stage4.py` 用于创建不可覆盖的题目/配置快照；`eval-stage4.py` 会产生真实云端调用，不是查看已有表格的入口。原始结果和失败均保留在报告所链接的运行目录中。

### 关系导向题集 v2（2026-11-15）

新题集见 [40 道题目与评分要点](artifacts/eval/stage-4/benchmark-v2/questions.md)：4 道事实、4 道改写、24 道跨文本关系、8 道反例。可回答题中跨文本题占 75%，均至少需要两篇论文；覆盖方法机制、共同数据集连接、图表示、训练/测试角色、任务属性及错误关系辨析。每题记录必要来源、预期答案和不可推出的结论。

这是有既有语料接触的开发集，尚未执行新一轮评测。分析关系提纲不是生产图路径金标；支持池仍非穷举，不预设图扩展胜出。v1 的冻结题集和成绩保留，新旧题集总分不能直接比较。

```powershell
# 本地检查题集哈希、原文、页码、跨论文来源及题型分布，不调用模型
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
python -X utf8 scripts/freeze-stage4-v2.py --check

# 需要实际重新评测时执行；调用 Cloudflare/DeepSeek，最多 64 次生成请求
python -X utf8 scripts/eval-stage4.py --benchmark benchmark-v2
```

`freeze-stage4-v2.py` 创建不可覆盖的新快照。v2 原始评测结果单独写入 `artifacts/reports/stage-4/benchmark-v2/`；不带 `--benchmark` 的旧评测命令和 `report-stage4.py` 仍使用 v1。

### LangSmith Dataset 与实验对照

2026-11-19：针对 v3 隔离图新建 [v4 题集](artifacts/eval/stage-4/benchmark-v4/questions.md)（[可搜索页面](artifacts/eval/stage-4/benchmark-v4/questions.html)），8 道事实控制＋24 道跨论文关系＋8 道反例，147 个逐项判分点，覆盖 40 种实际关系谓词。[关系映射](artifacts/eval/stage-4/benchmark-v4/coverage.md)逐题说明考查能力。题目、参考答案、原文位置、预期子图和评分规则已冻结；只将问题放入被测输入。v3 图快照与旧题集保留，这是已接触语料的开发集，不是独立未见测试集。模型对照尚未运行；生产 Workflow 仍使用旧 Neo4j 图，正式评测前须完成隔离图接入及运行配置冻结。

```powershell
# 本地核对 v4 题目、图哈希、原文与导出内容；不调用模型
.\.venv\Scripts\python.exe -X utf8 scripts/freeze-stage4-v4.py --check

# 仅登记/恢复上传 Dataset，不生成答案、不创建虚假 Experiment
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v4 --upload
```

每轮对照先创建/核对 Dataset，问题作为 inputs，参考要点与来源 ID 作为 reference outputs。Hybrid 和 Hybrid＋Graph 各自作为一个 Experiment，用 reference_example_id 逐题对齐，并保留原 Trace 链接。基础、跨文本及反例可按 split 筛选；指标反馈是检索支持单元得分，不是答案正确率。

持久规则见 [AGENTS.md](AGENTS.md)，展示范围见 [Dataset 策略](artifacts/eval/dataset-policy.json)。按用户对逐题详细展示的后续要求，v2 及后续版本的每个 Example 都显示参考答案、全部必要事实、支持原文及页码/字符位置、关系判读规则和运行配置。每题关联的 Experiment 显示完整回答、全部候选/分数、证据与引用、图路径、逐事实缺口、耗时、Token 和两组差异。PDF 二进制、向量和供应商原始响应保留本地；v1 沿用摘要展示。

```powershell
# 沿用上方 PYTHONPATH；只同步数据集，无模型调用
python -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v2 --upload

# 历史结果回填/失败补传：不会重新生成答案
python -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v1 --run-summary artifacts/reports/stage-4/runs/4981b3a1a81b49f1a47e3bd8022275cc/summary.json --upload
```

各题集目录下 `langsmith-dataset.json` 保存可审阅的上传内容，`langsmith-status.json` 保存远端核查结果与链接。运行目录保留 `langsmith-experiments.json` 作为补传快照。上传按稳定 ID 去重，遇到同版本内容不一致时拒绝覆盖；LangSmith Feedback 保留 4 位小数，精确值保存在实验 outputs.metrics 和本地原始结果。

v2 已在原 Dataset 内补齐 40 题详细参考信息，89 条来源记录回读一致；单题本地快照在 `artifacts/eval/stage-4/benchmark-v2/cases/`。2026-11-15 已执行 40 题配对实测，80 条结果、64 次真实生成，详见 [本轮结果与限制](artifacts/reports/stage-4/benchmark-v2/findings.md)。[实测总览](artifacts/reports/stage-4/benchmark-v2/runs/a2ab6cdee7144b96b7627ac96582fc87/report/dashboard.html) 同时保留汇总指标、分类柱状图、时延、Token、40 题完整详情及 LangSmith 对照入口。图组未观察到覆盖收益；支持池漏标与 7 条引用失败逐题保留，不把覆盖当作准确率。

逐题展示设计见 [逐题展示说明](artifacts/reports/stage-4/per-question-details.md)。初次升级旧的摘要 Example 使用 `--enrich-details`，仅当旧题目和旧金标完全一致时允许补充字段，不修改原题和评分口径。`scripts/report-evaluation.py --benchmark benchmark-v2 --run-summary <summary.json>` 从已有记录重建页面；`scripts/diagnose-evaluation.py` 补充协议、来源及失败草稿诊断，均不调用模型。上传恢复继续使用 `scripts/sync-evaluation-dataset.py`，不为展示重测。

来源保留第一步已完成：从旧 Graph 缺少必要论文来源的题中冻结 16 题诊断集，扩展全部 14 篇论文的名称/别名识别，并按问题保留各论文的合格原文。固定旧候选回放中，必要论文全部入选从 0/16 提高到 15/16，冻结事实覆盖从 23.96% 到 33.33%；保留 1 题退化，没有新生成，不据此宣称答案改善。[改动、限制与运行方式](artifacts/reports/stage-4/benchmark-source-coverage-v1/findings.md) · [汇总与逐题页面](artifacts/reports/stage-4/benchmark-source-coverage-v1/runs/e1283443e92d4181ab64cd2dd645fa13/dashboard.html)。

第二步已完成：固定上述 16 题的候选、分数、路径和来源保留，比较路径挤占原文、原文优先完整路径、原文优先紧凑路径三组，共 48 条回放、0 次模型调用。事实覆盖由 33.33% 提高至 36.46%，1 题提高、15 题持平；R12 恢复 Tree-of-Traversals 的 `totmusic` 支持，R18 与 R20 缺口保留。紧凑路径节省路径字节，但未额外增加事实覆盖；本轮没有测量答案质量。[第二步报告](artifacts/reports/stage-4/benchmark-source-coverage-v1/context-budget-findings.md) · [汇总图表及 16 题详情](artifacts/reports/stage-4/benchmark-source-coverage-v1/context-budget-runs/4b0e586edc95477d89a8fac736814162/dashboard.html) · [LangSmith 三组对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1/compare?selectedSessions=e9ff2c84-4c90-4e26-9119-db841fb362cc,f20a02a7-533c-4e5a-8317-761f762fa221,f178fe19-1d61-4142-8c8a-472c2a5c6f91)。

对这 16 道题的逐题归因已完成：8 题的冻结支持块在最终排序候选中但未进上下文，3 题同时存在未入选和候选/支持池缺口，2 题在最终候选中找不到冻结支持块，另 3 题的支持池已覆盖。候选或支持池缺口尚不能证明真实漏召回；需要先补齐各检索通道候选快照并核对原文，再确定优化方向。[逐题归因、证据排名与候选原文](artifacts/reports/stage-4/benchmark-source-coverage-v1/failure-diagnosis/diagnosis.md) · [交互页面](artifacts/reports/stage-4/benchmark-source-coverage-v1/failure-diagnosis/dashboard.html)。

2026-11-16 已执行下一轮三步优化：真实检索候选通道快照、固定候选下三种选择策略比较、以及 Baseline/Optimized 各 16 次 DeepSeek 端到端生成。去重选择策略的冻结事实覆盖为 37.50%（基线 33.33%），但全事实覆盖为 2/16（Evidence-first 为 3/16），逐题 2 增、13 平、1 退；32 条回答中 31 条通过引用结构校验，尚无独立语义评分。[汇总、分类指标、Token、逐题答案和 Trace](artifacts/reports/stage-4/benchmark-source-coverage-v1/optimization-runs/5351b670c38d41348d772f73a4ab2517/report.md) · [逐题仪表板](artifacts/reports/stage-4/benchmark-source-coverage-v1/optimization-runs/5351b670c38d41348d772f73a4ab2517/dashboard.html) · [LangSmith Baseline/Optimized 逐题对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1/compare?selectedSessions=377ee741-296c-430e-a901-d01ea4c88d3e,8be5e557-4ec4-4987-b695-7d58e201b0a8)。支持池覆盖不代表答案语义正确，R22 退化和 R18 基线引用错误均保留。

2026-11-16 路径配额对照已生成 48 个回答：6000 字节总额内预留 0/800/1200，事实覆盖 36.46%/33.33%/32.29%，来源齐全均 15/16。默认 0 保持原文优先现状；正配额增加路径使用但减少原文覆盖。[汇总、Token、P95 与逐题详情](artifacts/reports/stage-4/benchmark-source-coverage-v1/path-budget-runs/a119401fe1284a1887652f4b0345ceb4/report.md)。入口：python -X utf8 scripts/eval-stage4.py --benchmark benchmark-source-coverage-v1 --path-budget-comparison；已有结果仅用 scripts/eval-path-budget.py --resume 补传，不重新生成。

更正：上一轮路径配额从原文 6000 内扣除，不符合用户要求。已改为原文始终 6000 + 路径额外 800/1200，总上限 6800/7200；三组原文逐块一致。旧实验保留，但不用于判断额外预算的效果。[独立路径预算本轮报告与逐题结果](artifacts/reports/stage-4/benchmark-source-coverage-v1/extra-path-budget-runs/2dba52fe57084f1c998bf35849c79936/report.md)。正式入口：python -X utf8 scripts/eval-stage4.py --benchmark benchmark-source-coverage-v1 --extra-path-budget-comparison。
