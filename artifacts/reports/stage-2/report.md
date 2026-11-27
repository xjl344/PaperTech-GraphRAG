# 阶段 2：本地证据检索交付

2026-11-13，Codex 执行。用户授权完成整个阶段；片段使用本地 bge-m3，云端 bge-m3 与 DeepSeek API 留空。当前交付本地基础 RAG 工作流；真实云端模型回答、用量账单、跨端向量兼容性和人工质量验收仍待执行，不以模拟测试替代。

## 实际结果

- 只读取阶段 1 当前白名单 `pdf-v1.1`，14 篇、980 个片段；未把旧版 993 块混入索引。源 PDF 哈希复核一致。
- 本地 bge-m3 的 CLS 向量经 L2 归一化，维度 1024、有限、非零。975 个去重文本向量覆盖全部 980 块；重复文本命中缓存。
- 全量运行耗时 958.656 秒（约 16 分钟），CPU，8 线程；真实模型分词后最长片段 560 Token，未截断。该次全量运行开始于资源采样代码加入前，完整峰值内存未采集，不补估。
- 重跑 980/980 命中缓存，约 7.703 秒；这是启动、校验权重与读取缓存的耗时，不能当作重新推理耗时。该次进程峰值工作集约 767 MiB，不能推论为全量推理峰值。
- E 盘项目内运行 Neo4j Community 5.26.12、Zulu Java 21.0.13；实际 14 Paper、980 Chunk、980 HAS_CHUNK 来源边，另有版本状态节点 Corpus。全文和向量索引均 ONLINE。重复写入数量不增长。
- 全文为 Neo4j Lucene 9.11.1，字段 `text/title`，分析器 `standard-no-stop-words`，同步更新；部署的 IndexSearcher 类引用 BM25Similarity。向量使用 cosine、1024 维、HNSW 和默认量化，具体索引参数见 `verification.json`。两路按 RRF k=60 合并，不直接相加原始分数。
- HippoRAG 中英混合问题：全文 20、Dense 20，去重 29；真实本地 reranker 后给出 4 条原文证据，正文上下文 5769 UTF-8 字节。每项有真实论文、PDF 页码、片段与跨页字符范围。
- 云端未配置时真实全文召回可用，返回 `evidence_only`；没有调用生成服务或假装给出综合答案。无命中测试返回 `refused`。
- Streamlit 1.67.0 的真实 localhost agent API 已验证初次打开、空问题提示、查询、证据及导出控件；mypy 检查通过。未做浏览器像素检查。

## 工程交付

`settings/corpus/local_models/graph_store/retrieval/workflow/providers/citations/audit/traces` 分担配置、当前语料校验、本地推理、参数化 Neo4j、双路召回、LangGraph 编排、HTTP 重试、引用校验、持久审计和 Trace 补传。入口为 `scripts/stage2.py`、`scripts/run.ps1` 和 `app.py`，详细命令见项目 README。

两路各最多 20、合并最多 40；上下文最多 8 块且正文 JSON ≤6000 UTF-8 字节（用字节上界保守约束常用 byte-BPE Token 数，不声称已核实 DeepSeek tokenizer）。输入问题 ≤2000 字符，系统提示和问题在正文预算之外，生成最多 2048 Token。重排对最多 1024 Token，可能截断，运行摘要明确记录。

本地默认 CPU，推理使用 E 盘已有 Python 3.12.14 / Torch 2.13.0+cpu / Transformers 5.14.1 环境，主程序与数据库驱动在项目独立 Python 3.14.6 `.venv`。共享模型与推理环境只读使用；可在 `.env` 调整解释器路径。没有把失败的 GPU 依赖下载标为已安装或已验证。

SQLite 在外部调用前提交请求/尝试状态，保留阶段耗时、每路候选、结果、Usage、估算成本、402 阻止及 Trace 队列。无用量不记 0，单价为空不估价；累计已知费用 ≥5 元提示告警；DeepSeek 402 阻止状态需要人工显式复位。读超时/发送后断连不重发，HTTP 500/503 未能确认未完成时也不重发。模拟检查通过不等于供应商账单已核对。

引用检查校验 JSON、当前证据白名单、内联 ID 一致性和连续原文引句；不自动重新生成以掩盖错误。它不能证明句子的科学正确性、所有陈述均受引句支持或冲突已正确裁决，这些仍需阶段 3 人工核查。基础阶段 `graph_paths=[]`，没有执行语义关系建图或图遍历。

## 配置与后续边界

`.env` 已生成并忽略，只含本地 Neo4j 随机密码；云端 bge-m3、DeepSeek、LangSmith 及价格均留空。查询没有发出真实云端请求。Neo4j 默认使用报告已关闭。

填写云端 bge-m3 后，先执行 `run.ps1 -Task compatibility`，4 条固定中英文文本比较本地和云端向量，最低 cosine ≥0.999 方可启用；记录绑定端点/模型/本地指纹，30 天后过期。同名同维不等于相同向量空间，此检查也不保证供应商以后不变更模型。

DeepSeek 需填写真实模型名/Base URL/Key，并核实 thinking disabled、JSON 输出、用量和价格参数。LangSmith 需真实配置后验证上传，当前 URL 为 null、Trace 本地待传；有界补传与断网恢复只有模拟测试。检索无召回可确定拒答；自然语言中的证据充分性、语义冲突及各类问题的拒答准确率未做真实质量验收。

阶段 2 的本地功能交付完成；云端接入和阶段 3 人工金标/质量评测待用户填写配置后继续。本次不扩量，不进入关系抽取。测试检查为 22 项阶段 2 测试与 11 项阶段 1 回归，通过记录见相应报告。实施中失败与修复单独留在 `implementation-notes.json`。

## 核验证据

- `embedding-initial.json`：全量实际推理；`embedding.json`：全缓存重跑。
- `index.json`、`verification.json`：Neo4j 服务版本、索引参数、实际计数、重复写入及真实检索。
- `requests/`：真实请求结果；`data/rag.sqlite3`：阶段/候选/底账（本地忽略，不提交数据库）。
- `test-results.txt`、`test-summary.json`：模拟供应商/故障、引用及 LangGraph 检查；`ui-verification.json`：真实运行页面检查。
- `audit-summary.json`：请求/队列/调用数量与凭据扫描；`environment-freeze.txt`：项目环境依赖。
