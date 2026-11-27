# 本轮运行与复核

正式版本：`benchmark-relation-holdout-v1`。

题集SHA-256：`6f0b9710ce0a265304b63fee8e8bd91e1a18f2cf0337e13753b211cdcbe6ceba`。

运行ID：`12b6c032bb3f4992944a1148ddc92bce`。2026-11-22 08:26:59至08:37:03 UTC完成检索，之后仅补传与核验。

本轮新增模块：

- `src/papertech/relation_holdout_protocol.py`：由用户确认草案生成冻结题集、来源要求与评分口径，核对上一轮模型和图谱配置。
- `src/papertech/relation_holdout_evaluation.py`：两组检索运行、Trace核对、Dataset/Experiment上传、总览页面。继承原有候选生成算法，拒绝Dense-only。
- `src/papertech/relation_holdout_report.py`：配对bootstrap、事前分层、逐题CSV和报告。
- `scripts/explain-relation-holdout.py`：仅用已保存候选离线重放证据选择，解释具体预算损失，写入LangSmith反馈。
- `scripts/verify-relation-holdout.py`：独立重算指标并回读远端记录。
- `tests/test_relation_holdout.py`：检查图组不依赖文本/向量、拒绝纯向量组、配对统计按题号对齐。

注册入口：`scripts/eval-stage4.py`；补传注册：`src/papertech/evaluation_details.py`。现有历史题集、历史结果与生产检索/重排/证据选择算法未改动。本轮源代码哈希见冻结题集与`execution-contract.json`。

本轮已经完成。以下正式入口会创建新一轮实测，读取已冻结题目，先回读Dataset，再调用检索所需模型：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-relation-holdout-v1
```

仅补传已有结果，不重测模型：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-relation-holdout-v1 --run-summary artifacts/reports/stage-4/benchmark-relation-holdout-v1/runs/12b6c032bb3f4992944a1148ddc92bce/summary.json --upload
```

仅核验已有记录：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/verify-relation-holdout.py artifacts/reports/stage-4/benchmark-relation-holdout-v1/runs/12b6c032bb3f4992944a1148ddc92bce
```

当前环境曾遇到venv启动器按脚本启动时的解释器定位问题，因此本轮实际使用同一venv的stdin方式执行入口。例如：

```powershell
@'
import runpy, sys
sys.argv = ['scripts/eval-stage4.py', '--benchmark', 'benchmark-relation-holdout-v1']
runpy.run_path('scripts/eval-stage4.py', run_name='__main__')
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

验证结果：18项相关单元检查通过；80条结果独立重算480项指标；核对224个入选来源的原文与位置；两组远端各40条结果与本地完整输出一致；992项数值反馈、80条解释反馈及401个Trace span回读成功。80条证据选择离线重放与实测一致。没有生成调用；图、模型配置与冻结代码哈希保持一致。

首次Trace核验为399/401，后续回读已全部可见。只补查并补传，没有重跑检索；原始耗时与候选记录保留。
