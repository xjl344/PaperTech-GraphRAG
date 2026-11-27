# v4 隔离图正式执行记录

2026-11-20 启动运行 `e4c3fbb1a6e44fd7b6f1c0841b6d51df`，开始时间 `2026-11-20T07:08:16.572670+00:00`。
实际已完成 40 题 × 2 组；结果与判断见本轮 `runs/e4c3fbb1a6e44fd7b6f1c0841b6d51df/findings.md`。
昨天的 `preparation.md`、冻结题单中的“未运行”保留为执行前历史状态。

## 配置与隔离

- 不改动旧 Neo4j 语义图。基础全文和向量检索继续使用 Neo4j；本轮图扩展单独读取 v3 冻结 SQLite 图。
- `IsolatedGraph` 核对 SHA-256，以只读方式打开；SQLite authorizer 拒绝访问 `question_units`、`question_paths` 和 Claim 的 `unit_id/path_id`。种子来自问题实体和真实基础召回结果。
- 题集仍为原 v4，40 题、147 个判分点。参考答案、判分点及预期路径不进入被测检索或生成。
- DeepSeek 配置模型为 `deepseek-v4.1-flash-1017`；Cloudflare `@cf/baai/bge-m3`；本地 BGE reranker 使用 CUDA / FP16 常驻进程。
- 一次批量获取 40 个问题向量，两组共享；两组先后顺序逐题交替，生成设置均为禁用 thinking、最大 2048 输出 Token，供应商默认采样，一组一个样本。
- 两组原文证据均最多 8 块、6000 字节；路径另设最多 1200 字节。图组实际输入可比 Hybrid 长，这是一套图扩展配置的整体效果对照，不能归因为相同实际 Token 下纯粹的图结构收益。
- 基础候选 20 全文＋20 Dense，图候选最多 20，融合最多 40；图遍历最多 2 跳、40 路径、每节点 8 个关系。最终生成最多使用 4 条原文支持完整的路径。
- 开始前保存 `execution-contract.json`，记录模型、依赖版本、端点指纹、预算及代码哈希；结束时重新核对代码和图快照。

## 本轮新增记录

每组每题保存完整回答及模型回答草稿、各召回通道排序和分数、重排候选、原文与引用、全部图路径和生成路径、阶段耗时、调用与 Token、Trace。
147 个判分点逐项显示所需来源是否进入上下文及缺少的来源；`semantic_score=null` 表示尚无独立语义评分，不能把来源存在视为答对。

## 运行及结果恢复

在项目根目录使用 PowerShell：

```powershell
# 以下命令会创建新运行并调用模型；本轮已经启动，查看结果不需要再次执行。
.\.venv\Scripts\python.exe -X utf8 scripts/preflight-stage4-v4.py
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-v4
```

已有结果仅补传，绝不因同步失败重新调用模型：

```powershell
$runDir = 'artifacts/reports/stage-4/benchmark-v4/runs/e4c3fbb1a6e44fd7b6f1c0841b6d51df'
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v4 --run-summary "$runDir/summary.json" --upload
.\.venv\Scripts\python.exe -X utf8 scripts/diagnose-evaluation.py --benchmark benchmark-v4 --run-summary "$runDir/summary.json" --upload
.\.venv\Scripts\python.exe -X utf8 scripts/report-evaluation.py --benchmark benchmark-v4 --run-summary "$runDir/summary.json"
.\.venv\Scripts\python.exe -X utf8 scripts/verify-stage4-v4.py --run-directory $runDir
```

## 已通过的执行前检查

- v4 全部冻结内容与原文、v3 图哈希校验通过。
- 21 项评测相关测试、4 项隔离图测试、12 项上下文预算测试通过。
- Neo4j 980 块、14 篇、两个索引 ONLINE；隔离图三个探针通过；GPU FP16 预热通过。
- LangSmith Dataset 在模型调用前成功核对；最终两组 Experiment 各 40 条 run、320 条反馈和 40 个生成用量子 run 已回读核对。后续批量 Trace 核验回读 80 个根 Trace、共 400 个 span，0 个 pending event，全部结束状态和 Token 核对通过。

本图由已接触语料的 Codex 定向整理，覆盖范围限于开发诊断需要；该题集不作为独立未见测试集，也不与旧题集总分直接比较。
