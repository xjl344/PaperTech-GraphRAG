# 24题子查询召回诊断

本轮运行：`e158c260284d4273b8b55c9bd7a8b8f7`。

这是已曝光开发题的召回实验，不是新题泛化验收。复用冻结通用分流结果，未人工修补坏拆分；未调用拆分模型、重排模型或答案生成模型。

## 运行与恢复

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-subquery-recall-v1 --prepare-only
./.venv/Scripts/python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-subquery-recall-v1
```

第二条命令会创建新运行并产生新的 embedding 调用；已有结果补传使用：

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-subquery-recall-v1 --resume artifacts/reports/stage-4/benchmark-subquery-recall-v1/runs/e158c260284d4273b8b55c9bd7a8b8f7/summary.json
./.venv/Scripts/python.exe -X utf8 scripts/analyze-subquery-recall.py artifacts/reports/stage-4/benchmark-subquery-recall-v1/runs/e158c260284d4273b8b55c9bd7a8b8f7/summary.json --sync-review
```

`--resume` 仅同步 Dataset/Experiments，不重跑模型。分析脚本独立核对候选通道、合并次序、来源归因、49个必要来源覆盖与历史基线集合；`--sync-review` 只补传确定性来源原因说明。

## 实测结论

| 口径 | 原问题 | 原问题加子查询 |
|---|---:|---:|
| 逐题平均必要来源覆盖，全部并集 | 59.72% | 77.78% |
| 逐题平均必要来源覆盖，最多40条候选 | 59.72% | 68.06% |
| 全部并集来源数 | 29/49 | 38/49 |
| 最多40条候选来源数 | 29/49 | 33/49 |
| 全来源覆盖题数，全部并集 | 9/24 | 14/24 |
| 全来源覆盖题数，最多40条候选 | 9/24 | 12/24 |
| 检索查询数 | 24 | 81 |

同40条候选口径4题改善、20题持平，没有题目总覆盖率下降。但R24新增S01、丢失原本命中的S03，不能称为逐来源无损。

新增9个必要来源中，5个保留到40条内、4个被截掉；另外1个基线来源被截掉，净增4个。11个来源仍未进入任何查询的全文20＋向量20。

“最多40条”只控制下游候选上限，不控制查询次数或线上分流成本。原题向量复用；57条新子查询一次批量embedding，耗时2.21秒，供应商未返回Token。历史本地分流24次约789.79秒，单独披露，不能当作本轮免费实现的在线能力。

下一步应单独检验：在完整并集上重排是否保住新增来源，再施加候选/证据预算。本轮不能证明重排低分已修复或最终答案改善，也不证明图检索优势。

## 文件与验证

- 新模块：`src/papertech/subquery_recall_diagnostic.py`，独立召回/冻结/上传/报告，不修改生产workflow。
- 新分析器：`scripts/analyze-subquery-recall.py`，独立复算与逐来源中文解释。
- 注册入口：`scripts/eval-stage4.py`、`src/papertech/evaluation_details.py`。
- 新测试：`tests/test_subquery_recall_diagnostic.py`。
- 测试：新增5项、路由8项、详细数据集导出9项，合计22项通过。
- 全部48行结果经独立复算；24题基线候选集合与历史完全一致；每组49个来源计数一致。
- 本地报告目录包含 `index.html` 总览/柱图/分类/全部原文、`source-review.html` 逐题原因、`comparison.json` 指标、`summary.json` 完整记录。
- LangSmith回读验证：24个Example、48条Experiment记录、576项数值反馈；逐题说明反馈另见 `source-review-sync.json`。

冻结代码哈希变化会阻止旧版本重新执行；已有结果的报告和补传仍可使用。不要为补Dataset重跑检索或模型。
