# v4 图谱关系题集准备交付

日期：2026-11-19。状态：题集已冻结，LangSmith Dataset 已登记并回读核对；模型对照未运行。

## 本轮变更

- 基于同一 v3 隔离图重新表述 40 道题：8 道事实控制、24 道跨论文关系、8 道反例；保留原 v3 题集。
- 147 个逐项判分点，覆盖 40 种实际关系谓词；每项绑定所需来源单元，并保留来源原文、页码、字符范围、预期子图与错误边界。
- R09 限定共同 KBQA 数据集，避免旧题问全部交集却只列部分答案。训练/测试、增强方向、节点/边表示和停止条件分别核对。
- 题干只放 inputs；参考答案、判分点和预期路径只放 reference outputs。共享 Dataset 导出器补充这些字段，旧 v1/v2 导出行为保留。
- 提供完整 Markdown 题单、可搜索 HTML 页面、逐题 JSON 和关系覆盖表。

## 冻结与验证

- v4 题集 SHA-256：`2904af152a4bffd86119cbbf030d0ac658e909cc22d1abdf2b4d398f67d02451`。
- v3 图 SHA-256：`f2eaae0c534dfa501b66ed80b5cd94c2140163d7a760acb56babd0218bab5d73`，198 实体、204 条关系，未改动。
- v3 题集 SHA-256：`3ffb13a824016b58fd2cb5585bab2f3dbbf9767bd38b714ce148097122f6ac87`，复核未改动。
- `freeze-stage4-v4.py --check` 通过，核对全部冻结内容、原文来源、图哈希、路径连续性及题型分布。39 题有来源，N06 是无来源负例。
- 20 项 `test_evaluation*.py` 测试通过，包括新评分信息保留在 reference outputs、深拷贝隔离以及旧版本导出回归。
- LangSmith 40 个 Example、40 个完整详情、89 条来源展示记录回读通过；具体状态见题集目录的 `langsmith-status.json`。两组 Experiment 尚未创建，模型调用为 0。

Dataset：[papertech-stage4-benchmark-v4](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/a82228b8-0434-40b7-9311-1dca5e330ceb)。

## 使用方式

在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/freeze-stage4-v4.py --check

# 仅恢复 Dataset 上传，不调用模型
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v4 --upload

$env:PYTHONPATH = (Join-Path $PWD 'src')
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p 'test_evaluation*.py'
```

## 尚待完成

生产 Workflow 仍使用旧 Neo4j 图。正式对照前需接入 v3 隔离图、明确禁用 question_units/question_paths 等参考映射作为检索输入，并冻结实际模型配置、代码和两组预算，再从正式评测入口运行。当前 v4 是题目/参考信息快照，不是已经接通的执行配置。

本轮不提供虚构的对照图表或回答。实际运行后仍须同时交付汇总指标、分类柱状图、时延、Token、逐题完整结果和 Trace。

题集与图谱均由已接触语料的 Codex 整理，属于开发诊断集。来源字符串、页码和图路径校验不能代替独立人工语义评分，也不能证明 Graph 优于 Hybrid。跨论文题的多个子图可能不相连，不应强行解释为一条连续路径。
