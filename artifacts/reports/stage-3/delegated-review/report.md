# 阶段 3：委托审核与官方运行追踪

执行日期：2026-11-14。范围：冻结的 14 篇试点、正式抽取运行 `2ec77731331a4875ac6ed256bfebdc62`。

## 审核结果

用户明确委托 Codex 完成审核。已逐条审阅全部 405 条程序校验后的候选，批准 83 条、拒绝 322 条、待审核 0 条。83 条均已确认写入 Neo4j；图中有 91 个 KGEntity，关系来源覆盖 13 篇论文的 46 个片段。CuriousLLM 的 7 条候选全部拒绝，不能声称每篇都已有可信语义边。

审核类型为 `ai_delegated`，审核者为 Codex，策略为 `evidence-review-v1`，不是独立人工专家核验。未调用本地 Qwen 或其他项目模型重新充当裁判；也未执行阶段 4 的答案评分。

| 接纳关系 | 数量 |
|---|---:|
| ADDRESSES | 28 |
| EVALUATED_ON | 53 |
| IMPROVES_UPON | 1 |
| COMPARES_WITH | 1 |
| PROPOSES | 0 |

这些是带来源的 Claim 数，同一关系的不同引句分别保留，不代表 83 个不同的研究结论。拒绝理由主要包括：实体类型错误、未命名或复合实体、主体错配、否定语义反转、把实验胜出当成技术继承，以及引句不能充分支持关系。

批准前检查方法/问题/数据集身份、主体归属、关系方向、原文引句与上下文，以及采样、底座模型、组合方案和局部案例的限制。引句、端点、置信标记均保留抽取原样；不通过时拒绝原候选，不把修改后的说法冒充模型原始输出。仅大小写/Unicode 规范化后的精确名称合并，不新增模糊消歧或强制合并别名。

逐条决定、来源路径、页码、Claim/Chunk ID、引句及具体理由见 [完整审核记录](review-log.md)。原始候选与来源全文见 [冻结快照](snapshot.json)，可机读决定见 [decisions.json](decisions.json)，实际持久化与入图确认见 [review-results.json](review-results.json)，清单哈希与逐篇统计见 [summary.json](summary.json)。

## LangSmith 官方追踪

实际使用已有 `.env` 中的 LangSmith 配置，项目为 `papertech`；未改写密钥。正式链接、上传和远端回读结果以 [langsmith-status.json](langsmith-status.json) 为准，元数据补传载荷保存在 [langsmith-outbox.json](langsmith-outbox.json)。网页不作为官方监测交付。

当前格式 `stage3-metadata-v2` 包含 1,079 条记录：抽取根任务 1 条、672 个片段记录、审核根任务 1 条、405 条审核/入图记录。上传后按两个 trace_id 分页回读，核对全部 ID 和结束状态。重跑使用同一格式与来源身份生成稳定 UUID，不新增相同版本的 Trace。

正式入口：[抽取过程](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9b2838dd-a606-54ab-9ee7-1590c4debf70?poll=true) · [委托审核与入图](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9527ab20-0624-5e23-975c-e9507bb5724c?poll=true)。需要登录该 LangSmith 工作区。

远端已逐项核对 668 次成功推理的原生 `prompt_tokens` / `completion_tokens` 与本地一致；缓存片段不作为额外 LLM 调用计数。3 次失败以错误状态展示，用量没有记录，不能假定为 0。[载荷与密钥检查](safety-verification.json)核对补传载荷不存在正文、引句、向量和密钥字段，并扫描本地报告没有出现已配置密钥值。

- 抽取记录：运行状态、片段序号/标识、版本、记录的开始/结束时间、候选/程序拒绝数量、输入/输出 Token、失败代码。成功真实推理以 LLM span 上报；缓存复用作为链路事件，不再计作新推理 Token。
- 审核记录：委托 AI 审核身份、规则版本、候选标识、批准/拒绝、图写入是否确认。逐条语义理由和论文证据留在本地，未作为索引监测载荷上传。
- 对外只上传建图/审核的运行元数据，不上传 PDF、片段全文、引句、向量、密钥或授权头。
- 提交 Token 计数，不换算为货币；LangSmith 自身界面可能有通用费用栏目，本项目未提交单价或费用估算。

这是根据 SQLite 已存记录进行的**历史补传**，不能说抽取当时已经有实时 LangSmith tracing。未保存的逐 Token 流、完整尝试历史、GPU/CPU/内存曲线无法追补；三个失败片段的用量未知，不按零用量处理。审核子记录时间代表决定持久化时间，不是每条阅读耗时。

初步格式 v1 的两棵 Trace 仍保留作诊断记录，其 LLM 原生 Token 字段与缓存耗时显示不完整；正式查看与统计应过滤 metadata `trace_format=stage3-metadata-v2`，只使用当前状态文件返回的两条链接，不把格式迁移当成再次抽取或将两个版本的输出数相加。

本地 Streamlit 可以保留作证据查看工具，但不是本次监测完成的证明。

## 验证与已知缺口

[真实 Neo4j 复验](verification.json)：批准清单与入图清单完全一致；83 条关系各有一条语义边；来源血缘错误 0；缺少审核身份/时间/理由的 Claim 为 0。第二次写入全部已批准 Claim 后仍为 83 条，幂等通过。图扩展返回 40 条有来源的路径，核对仅经过批准 Claim、最多 2 跳。源 PDF 与当前解析白名单哈希在执行前重新核对。

更新后的 [42 项回归测试](test-results.txt) 通过，包括待审核不能入图、Schema/引句验证、SQLite 迁移、Trace 断网恢复及现有 RAG 流程。修正了现有问答 Trace URL 获取方式与安装的 LangSmith SDK 签名不兼容的问题；模拟测试现在要求传入远端读取的 Run，不能仅用任意参数假装通过。

抽取覆盖仍为 669/672 个片段（668 个完成、1 个缓存复用）；另 3 个失败，详见 summary.json 中的片段、论文、时刻与 `ValueError` 代码。现有记录不能进一步确认这三个错误的具体原因。本次完成的是已有 405 个候选的审核，没有悄悄重抽或把失败片段标成功。程序先前拒绝的 358 个候选没有绕过结构/引句校验进入审核或图谱。

正式运行 ledger 的输入/输出累计为 411,824 / 98,717 Token，包含 1 个缓存片段携带的 440 / 7 计数；对应本轮有记录的实际成功推理为 411,384 / 98,710 Token。三个失败调用及此前旧运行不能从这两个数推算出真实总消耗。

当前没有接纳 PROPOSES 边，技术继承边也仅 1 条；方法/数据集别名尚未全面对齐。因此这是一张经过委托审核的试点关系图，不能包装成完整的论文技术谱系。两跳/路径数/20 秒查询超时有界；每节点度数硬限制、正式冲突判定和阶段 4 的 Hybrid 对照仍未验收。本次没有启动阶段 4，也没有证明 GraphRAG 优于 Hybrid。

## 运行与复查

正常情况下使用项目 `.venv\Scripts\python.exe` 执行；本次该启动器无法访问其基础解释器，因此实际使用现有系统 Python 3.14.6，并显式加载项目依赖目录完成验证：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$taskPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'

# 复验来源、图写入幂等与受限路径；不重新调用抽取模型
& $taskPython -X utf8 scripts\review-stage3.py verify

# 仅远端核对已有 LangSmith 记录
& $taskPython -X utf8 scripts\trace-stage3.py --verify-only

# 显式补传同版本元数据；不重新抽取论文
& $taskPython -X utf8 scripts\trace-stage3.py --upload

# 本地回归；不调用项目配置的云端生成/向量 API
& $taskPython -X utf8 -m unittest discover -s tests -v
```

新增脚本为 `scripts/review-stage3.py`、`scripts/trace-stage3.py`；入图属性与 SDK 兼容修复位于 `src/papertech/graph_store.py`、`src/papertech/traces.py`，相应回归位于 `tests/test_kg.py`、`tests/test_rag.py`。本次没有改写源 PDF、`.env` 或既有 Git 暂存状态。
