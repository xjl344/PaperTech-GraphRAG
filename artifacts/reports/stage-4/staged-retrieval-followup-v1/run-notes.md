# 本轮改动、入口和验证方式

本轮分三阶段执行，均沿用已曝光的40道开发题及原参考来源，每阶段创建新冻结版本与LangSmith Dataset。版本变化用于区分实验条件，不把同题重测包装成泛化验收。

1. `benchmark-recall-width-v1`：全文固定20，Dense返回20/40/60；复用历史查询向量，ANN的查询范围仍为100。不重排、不生成，单独评估候选覆盖。
2. `benchmark-resource-selection-v1`：候选及历史重排分数完全固定，分别测6000/8000字节、8/12块，另设取消已有点名论文保底的消融。无模型调用。
3. `benchmark-recall-intervention-v1`：按第一阶段结果选择能补回跨论文来源的最小k；在相同8000字节、12块和已有保底条件下比较。复用旧候选分数，只用原问题为新增候选评分。不改写问题、不增加按方法的召回偏置、不生成回答。

`Dense20/40/60`是Dense返回数量标签，每组都包含原全文Top-20，不是纯向量检索组。

改动文件：

- `src/papertech/retrieval.py`：`select_evidence`新增`evidence_max`参数，默认仍为8，保留原阈值和字节计价。
- `src/papertech/evidence_context.py`：`assemble`与`reserve_sources`传递块数上限，增加显式的`named_first/score_order`实验策略；默认沿用已有点名论文优先。
- `src/papertech/workflow.py`：构造时可显式传入证据字节、块数与保底策略，统一组装参数和`context_budget_bytes`。默认仍为6000字节、8块；没有自动采用实验组配置。
- `scripts/explain-relation-holdout.py`：离线重放读取每条记录的`selection_config`，按实际预算和块数解释跳过来源的原因，历史记录缺省值仍为6000/8。
- `src/papertech/staged_retrieval_diagnostics.py`：三阶段冻结、执行、开发集指标、LangSmith Dataset/Experiment及完整逐题报告。
- `scripts/eval-stage4.py`与`src/papertech/evaluation_details.py`：正式入口及只补传入口注册。
- `scripts/verify-staged-retrieval.py`：独立重算来源指标、核对候选与历史分数、原文位置和LangSmith远端结果。
- `scripts/report-staged-retrieval.py`：汇总三个已完成阶段，记录逐必要来源迁移和逐题胜/平/负，不重跑模型。
- `tests/test_staged_retrieval_diagnostics.py`、`tests/test_context_budget.py`：验证块数上限、保底消融、扩展候选不被截回40、工作流传参及预算回归。

正式运行入口（以下会新建实测运行，不是查看已有结果）：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-recall-width-v1
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-resource-selection-v1
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-recall-intervention-v1
```

每次都先创建并回读该阶段40个Dataset Examples，之后才读索引或调用重排模型。上传中断时只对保存结果补传：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark <对应版本> --run-summary <该运行目录>/summary.json --upload
```

复核与汇总（不运行模型）：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/verify-staged-retrieval.py <该运行目录>
.\.venv\Scripts\python.exe -X utf8 scripts/report-staged-retrieval.py
```

当前Windows环境直接传脚本路径曾遇到venv解释器定位错误，本轮实际通过相同venv的stdin与`runpy`执行。例如：

```powershell
@'
import runpy, sys
sys.argv=['scripts/eval-stage4.py','--benchmark','benchmark-recall-width-v1']
runpy.run_path('scripts/eval-stage4.py',run_name='__main__')
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

38项预算、工作流、Dataset详情及本轮逻辑检查通过；参数化后的默认值精确复现历史80条完整证据选择。各阶段的远端题数、完整输出、数值反馈、时戳、reference_example_id及Trace链接回读结果见每阶段`independent-verification.json`。

原题、金标、图谱、模型、别名与生产默认预算未修改。已有结果保留；运行代码的后续参数化会导致历史版本的“重新实测”哈希门禁拒绝，这是有意避免用新代码伪装历史配置。历史结果查看和只补传不需要重跑模型。
