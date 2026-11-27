# 40 题逐题详细展示

2026-11-15 用户要求本轮 40 道题的每题详细信息全部显示在 Dataset 中，上一次保留现状。已在[原有 v2 Dataset](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/74f19566-1b27-4b3f-bf1e-7d99b149d14b)补齐 40 个 Example，远端逐题回读一致，保留原题目、金标、Example ID 和 Dataset URL。

打开 Dataset 的 Examples，点开任意题查看其 Reference outputs：

| 字段 | 每题内容 |
|---|---|
| case_id / category / expected_answer | 题号、类型与预期答案 |
| required_facts | 每项必需事实及其独立支持池 |
| source_evidence | 各支持片段的完整原文、论文/文件、PDF 页码、字符位置、解析 ID 与哈希；各题共 89 条来源记录 |
| relation_outline / must_not_claim / relation_review | 关系链、不可推出的结论、方向/角色/条件检查 |
| scoring_rules | 覆盖指标、分母、反例和语义核查规则 |
| evaluation_config | 本题是否生成、模型及候选/上下文/图扩展预算 |
| result_display | 本题关联的两组详细实验结果字段说明 |

这是参考信息的展示增补，冻结 benchmark-v2 的哈希仍为 `c26881d38a57a0460dd5a946468de9923e1dca65d372c25d8063fde5081c78ec`。展示格式独立记录为 `per-question-details-v1`；本地 `cases/<题号>.json` 每题一个快照，`detail-contract.json` 保存增补授权、展示导出代码哈希和内容哈希。

## 实际复测后的逐题结果

v2 尚未执行新一轮模型对照，目前没有实际答案或成绩。执行后每题各组关联的 Experiment outputs 将显示：完整答案、全部重排候选及分数与来源、最终证据和引用、全部图路径与生成采用路径、逐事实命中/缺口、检索摘要、逐阶段耗时、Token、供应商调用状态和原 Trace 链接。同题两组还显示指标差值、共用证据、图组新增及丢失的证据。

本次没有修改原冻结生成子集：8 道基础题仍为仅检索评估，24 道关系题和8道反例按证据门控生成。无生成时保留该状态，不捏造模型回答。自动支持池覆盖与两组差异不能代替语义评分，语义核查状态单独标记。

## 改动与运行

- `src/papertech/evaluation_details.py`：逐题参考/结果导出、原 Example 增补、稳定 ID 对齐、完整结果与反馈回读。
- `scripts/sync-evaluation-dataset.py`：增加 `--enrich-details` 入口，仅在旧题目和旧金标完全一致时追加字段；重跑增补不会创建重复题目。
- `scripts/eval-stage4.py`：v2 使用完整结果导出，并保存对应导出代码哈希；v1 沿用既有实现。
- `artifacts/eval/dataset-policy.json`、`AGENTS.md`、宪章与 README：记录用户对本轮逐题详细显示的授权及后续要求。
- `tests/test_evaluation_details.py`：检查 40 题完整性、增补不改原金标及幂等、未知远端修改保护、全部候选/结果字段、配对增减及旧版本保留。

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')

# 检查题集和导出（没有模型调用）
python -X utf8 scripts/freeze-stage4-v2.py --check
python -X utf8 -m unittest discover -s tests -p 'test_evaluation*.py' -v

# 增补/核对远端 40 题详情（没有模型调用）
python -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-v2 --enrich-details --upload

# 明确需要复测时执行，产生真实模型调用；本次未执行
python -X utf8 scripts/eval-stage4.py --benchmark benchmark-v2
```

15 项评测相关测试通过；原题集检查通过；远端 40/40 题详情与 89 条来源记录核对通过。上一次的 Dataset/Experiment 未更新。PDF 二进制、Embedding 数组、密钥及供应商原始响应不上传，日常问答 Trace 仍保持元数据模式。
