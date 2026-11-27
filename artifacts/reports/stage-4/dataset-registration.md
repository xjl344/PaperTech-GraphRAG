# 2026-11-15：版本化题集与 LangSmith 对照

用户要求历史、本轮及后续每次对照都创建 Dataset，不能仅依靠零散 Trace。现已将本地冻结题集映射为 Example，把历史两组结果映射为关联同一题目的 Experiment。

| 项目 | benchmark-v1 | benchmark-v2 |
|---|---|---|
| 题目 | 24 可回答＋4 反例 | 32 可回答＋8 反例 |
| 跨文本关系题 | 原 cross 类 8 题，其中 ToG-R 变体题实际来自单篇 | 24 题，全部至少两篇，部分三篇 |
| 跨文本占可回答题 | 原类别标记 33.3%，不能等同严格跨篇比例 | 75% |
| 远端 Dataset 回读 | 28 Examples 内容一致 | 40 Examples 内容一致 |
| Experiment | Hybrid / Hybrid＋Graph 各 28 条 | 尚未运行，不创建虚构结果 |
| 指标反馈 | 各 120 条，共 240 条，远端逐项核对 | 尚无新分数 |
| 模型调用 | 复用已有 56 条结果，本次无新调用 | 本次仅创建题集，无新调用 |

- [v1 两组逐题对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/f9c0f19c-5da4-4f62-a450-b83c83b5eddd/compare?selectedSessions=029b0d26-8d59-4d92-9f2c-2d958e029de7,1e14a769-6ea0-4419-a78a-144cad303565)
- [v2 关系题 Dataset](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/74f19566-1b27-4b3f-bf1e-7d99b149d14b)
- [v2 题目、答案要点与来源](../../eval/stage-4/benchmark-v2/questions.md)

## 怎样判读差异

Dataset 的 inputs 只有问题；reference outputs 保存参考要点、来源 ID 与关系边界，不会输入被测检索或模型。每个 Experiment 的结果用 reference_example_id 关联原题。按 category/split 查看基础、跨文本和反例，按 metrics 查看已标注支持单元覆盖，不将引用格式、ok/partial 状态或反馈分数当成答案准确率。

重点查看 C01 与 C05 的 outputs.source_review：C01 原金标支持池漏标，两组指标未显示图路径挤掉方法证据的实际退化；C05 图组引用虽有效，却将 Freebase 训练迁移来源误作 MetaQA 测试 KG。其余预选题的既有核查摘要同样回填，不冒充独立人工语义评分。

当前按项目现有展示范围上传结果摘要、状态、指标、来源 ID、原 Trace 链接与核查说明。完整生成答案保存在原运行目录的逐题 JSON；PDF、原文片段、向量与原始供应商响应不上传。`dataset-policy.json` 记录展示策略，后续用户确认可以更新。

历史实验的包装 Span 是结果导入，不模拟当时实时过程，其零时长不代表原始请求耗时；实际检索计算时延保存在 outputs.retrieval_compute_seconds。LangSmith Feedback 将小数保留到 4 位，回读按该精度核对，outputs.metrics 与本地文件保留精确值。

## 文件与运行

- `AGENTS.md`、`artifacts/eval/dataset-policy.json`：后续对照的持久约定及展示范围。
- `scripts/freeze-stage4-v2.py`、`benchmark-v2/benchmark.json`、`questions.md`：来源核查、40 题冻结快照与可读题单。
- `src/papertech/evaluation_datasets.py`：本地导出、稳定 ID 去重、Dataset/Experiment 同步及远端回读。
- `scripts/sync-evaluation-dataset.py`：已有数据集和结果补传，不调用模型。
- `scripts/eval-stage4.py`：显式选择版本，有 LangSmith 配置时在模型调用前成功核对 Dataset；结束/中断后同步已有结果。v2 结果与 v1 分目录。
- `README.md`、`plan.md`、`PROJECT_CHARTER.md`：运行说明、当前断点及 Dataset 的外发范围。
- `tests/test_evaluation_datasets.py`：金标隔离、来源外发边界、版本匹配及结果配对检查。

在项目根目录使用 PowerShell：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')

# 检查题集；没有模型调用
python -X utf8 scripts/freeze-stage4-v2.py --check
python -X utf8 -m unittest discover -s tests -p 'test_evaluation*.py' -v

# 补传历史对照；不重跑模型
python -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v1 --run-summary artifacts/reports/stage-4/runs/4981b3a1a81b49f1a47e3bd8022275cc/summary.json --upload

# 需要执行新一轮模型对照时使用；会产生真实调用，本次未执行
python -X utf8 scripts/eval-stage4.py --benchmark benchmark-v2
```

本机 `.venv/Scripts/python.exe` 的基础解释器路径当前失效；上述方式沿用项目既有运行说明，使用 PATH 中可用的 Python 3.14.6 加项目依赖，不修改 Python 安装。

## 验证与限制

新题集已检查哈希、语料/源文件、来源文本/页码、题目唯一性、跨篇数量、14 篇覆盖及生成子集。9 项评测相关测试通过，命令行版本参数检查通过。v1 Dataset/56 条结果/240 条反馈、v2 Dataset 的实际回读记录分别保存于各题集的 `langsmith-status.json`；历史运行目录另留导入快照与状态。

这次没有执行新模型评测。新题集仍是开发集，支持池不穷举，不是独立人工金标；分析关系提纲不是完整生产图路径金标。没有据此修复生产检索、宣布图扩展更好或通过扩量准入。原来的 `report-stage4.py` 仍只重建 v1 报表，v2 的结果表应在实际运行后生成。
