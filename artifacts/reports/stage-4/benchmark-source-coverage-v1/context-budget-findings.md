# 第二步：原文与图路径上下文预算

本次沿用第一步冻结的 16 道失败诊断题、参考答案和必要事实，只比较证据/路径组装方式。候选、重排分数、第一步来源保留、原始图路径和 6000 UTF-8 字节预算保持固定；三组逐题回放共 48 条，没有新检索、重排或模型生成。

| 指标 | 第一步基线：路径可挤出原文 | 原文优先：完整路径 | 原文优先：紧凑路径 |
|---|---:|---:|---:|
| 必要来源齐全 | 15/16 | 15/16 | 15/16 |
| 平均必要来源覆盖 | 97.92% | 97.92% | 97.92% |
| 冻结事实覆盖 | 33.33% | 36.46% | 36.46% |
| 全部必要事实覆盖 | 2/16 | 3/16 | 3/16 |
| 平均原文块数 | 3.3125 | 3.6250 | 3.6250 |
| 含路径题数 | 5/16 | 1/16 | 1/16 |
| 平均路径字节 | 214.5 | 41.6 | 29.6 |
| 平均证据与路径序列化字节 | 5342.5 | 5502.9 | 5490.9 |

两种原文优先策略相对第一步都在 1 题提高、15 题持平、0 题退化。R12 从 50% 提高到 100%：补回 Tree-of-Traversals 的 `totmusic` 支持；LPKG 的 `lpbench` 支持在原上下文中已存在。R11、R12、R13、R23 合计保留了 5 个此前被路径预算挤掉的原文块。R18 仍是 0%，该题没有可用入选路径，预算策略无法补足支持段。R20 的 KGP 合格候选缺口也未改变。

紧凑路径与完整路径选出完全相同的原文和事实支持。R19 是唯一保留路径的题，紧凑表示比完整路径少 192 字节，但本次没有新增事实覆盖。路径题从 5 道减至 1 道是预算下的实际代价；没有新生成，不能判断这会如何影响最终回答。

## 实现行为

`evidence_context.assemble` 现在先按固定排序和来源规则选择原文，再用剩余预算容纳路径。完整路径会重复携带原始引句；紧凑路径把引句映射到已选原文的 `chunk_id`、`quote_ids` 和字符范围。路径完整引句仍保留在本地审计结果中，发送给生成器时走紧凑引用结构。引句不在已选原文中时，该路径不会发送。`workflow` 对新旧检索摘要保持兼容。

6000 字节上限严格核对的是 evidence 与 graph-path payload 的 UTF-8 序列化大小，不是 Token，也不含问题、system prompt 和缺口说明。平均组装耗时约 2.4–2.5 毫秒，仅表示本地证据组装。

## 数据集与审计

沿用 `benchmark-source-coverage-v1`，未改冻结题目或金标。LangSmith Dataset URL：

https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1

三组 Experiment 比较：

https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1/compare?selectedSessions=e9ff2c84-4c90-4e26-9119-db841fb362cc,f20a02a7-533c-4e5a-8317-761f762fa221,f178fe19-1d61-4142-8c8a-472c2a5c6f91

Dataset 的 16 个详细 Example、三组各 16 条结果、480 条数值反馈和 48 条结构诊断均已回读核验。每个结果保留逐题证据、所有候选与分数、路径、预算、差异和父运行 Trace。R12 诊断文本更正为 Tree-of-Traversals / `totmusic`，三组远端反馈均已回读；修正原因与前后哈希见运行目录 `report-correction.json`。此更正仅修复文字，不改变执行算法或原始冻结契约。

## 复现与限制

本地柱状图、指标、逐题详情、CSV 和全部 JSON 位于 `context-budget-runs/4b0e586edc95477d89a8fac736814162/`。入口页面为该目录的 `dashboard.html`，逐项结果见 `summary.json` 与 48 个题目/组别 JSON；最终检查在 `delivery-verification.json`。Node DOM 模拟检查覆盖 9 类图表、16 个题目详情、搜索和远端链接，没有做浏览器视觉检查。

在仓库根目录的 PowerShell 中可重建报告并补传已有结果，不会调用模型：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\context-budget-pycache'
python -X utf8 scripts/eval-context-budget.py --resume artifacts/reports/stage-4/benchmark-source-coverage-v1/context-budget-runs/4b0e586edc95477d89a8fac736814162/summary.json --upload
python -X utf8 scripts/verify-context-budget.py --run-summary artifacts/reports/stage-4/benchmark-source-coverage-v1/context-budget-runs/4b0e586edc95477d89a8fac736814162/summary.json --remote
```

105 项全套测试通过。诊断子集刻意选择失败题，不能外推总体收益；事实覆盖是冻结支持池的程序对齐指标，不是语义答案准确率。第一步和第二步均未重新生成答案，也没有独立专家语义评分。要验证回答质量，后续需在同一题集上冻结新执行契约，运行原文优先的端到端生成对照，并逐题审查答案与引用。
