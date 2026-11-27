# 来源保留第一步：16 道失败题诊断

根据用户“主要针对知识图谱 RAG 表现不好的题创建新数据集，进行第一步”的授权，本次实现问题驱动的来源识别与证据保留。没有重新运行完整 40 题。

从旧 `benchmark-v2` 的实际图组结果中，按“跨文本题最终上下文缺少至少一篇必要论文”选择全部符合条件的 16 题。它们在旧组的来源齐全率必然为 0，属于有偏的失败诊断集；改善幅度不能外推为总体性能改善。问题、必要事实、支持池继承 v2 原样保留，没有看结果后补标。

新版本为 `benchmark-source-coverage-v1`，运行 `e1283443e92d4181ab64cd2dd645fa13`。运行前保存旧代码快照与哈希，再进行修改。

[柱状图、基础指标与全部逐题信息](runs/e1283443e92d4181ab64cd2dd645fa13/dashboard.html) · [完整对照表](runs/e1283443e92d4181ab64cd2dd645fa13/comparison.md) · [LangSmith 两组对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1/compare?selectedSessions=192a58b3-51a6-4b4d-b8c2-561c4f791fb6,0ffd459f-df3e-4692-9520-c300d1ac1252)

| 指标 | Graph-before | Graph-after |
|---|---:|---:|
| 必要论文全部入选 | 0 / 16 | 15 / 16 |
| 每题必要论文覆盖的均值 | 50.00% | 97.92% |
| 冻结支持池事实覆盖的均值 | 23.96% | 33.33% |
| 必要事实全部覆盖 | 0 / 16 | 2 / 16 |
| 新模型调用 | 0 | 0 |

事实覆盖逐题为 4 题提高、11 题持平、1 题退化。来源保留功能有效，但尚未解决选对具体段落的问题，也没有证据表明新答案正确率提高。

## 改动与边界

- `src/papertech/entity_aliases.py`：扩展来源目录到全部 14 篇论文，另记录 ToG-R 与同论文的关联。别名绑定可回查的本论文原文；支持英文名紧邻中文及常见连字符；ToG、ToG-2、ToG-R 的实体名称保持区分，同论文来源去重。
- `src/papertech/workflow.py`：问题显式涉及多个已知论文来源时识别为比较问题，覆盖“结合”“分别”等不含原关键词的表达。
- `src/papertech/evidence_context.py`：先为问题涉及的论文保留一个合格原文块，再按原排名填充。选择时为其他来源预留最小可行空间，遇到长块可改选同论文较短的合格块；分数门槛、6000 字节预算与最多 8 块的上限保留。没有切短原文或读取金标。缺口中记录合格候选数和未入选原因。
- `scripts/freeze-source-coverage.py`：冻结诊断子集与执行前代码，拒绝覆盖已有版本。
- `scripts/eval-source-coverage.py`：复现旧证据、回放新选择、创建详细 Dataset 和两组 Experiment，保存图表和逐题诊断；支持仅补传既有结果。
- `src/papertech/evaluation_details.py`：诊断集的参考页面明确“证据回放、无新生成”，保留继承的参考答案和完整原文，不把旧题的生成标志误当成本轮计划。
- `tests/test_source_coverage.py` 及原图查询测试：验证来源目录、别名边界、无关键词多来源、来源保留、预算、低分缺口、旧结果复现与金标继承。

本轮固定旧图组的候选、重排分数、返回路径、6000 字节预算与路径处理策略，只重新执行证据组装。修改前 16 条输出与上一轮逐块一致；两个组的候选和分数一致。新版别名也用于后续实时图实体匹配，但它对实时图检索的影响没有在本轮回放中验证。

## 保留的失败

R18 从 50% 事实覆盖降到 0：加入 RoG 来源后，KG-GPT 已标注主支持段被预算挤出；选入的 RoG 段也没有命中主支持池。来源出现不能替代事实支持，该退化单列在图表、逐题数据与 LangSmith 诊断反馈中。金标未穷举，不据此断言所有新段落都无用。

R20 仍缺 KGP：固定候选中没有通过当前证据有效性、分数阈值及单块预算门槛的 KGP 文本，程序报告缺口，没有为凑齐篇数强行选入低分来源。

下一步应针对这些剩余失败处理证据互补性和段落粒度；本次没有继续改变路径预算、重排模型、图 Schema 或生成策略。

## 验证与使用

99 项全套回归通过；最后的同论文变体识别调整后，8 项来源保留测试再次通过。16 个详细 Example、两组各 16 条结果及各 128 条数值反馈、各 16 条逐题诊断均已远端回读。页面包含汇总柱状图、基础指标、逐题原文/候选/路径/事实缺口及历史回答/Token/Trace。页面交互使用 Node DOM 模拟检查，不声称浏览器视觉验收。

新生成调用为 0，新生成 Token 为“不适用”；旧回答、引用和 Usage 显式保存在 `parent_generation`，不能当作优化后的生成结果。原生运行时延为本次证据组装时间，不是完整检索或端到端生成时间。最终哈希、来源/预算、远端与页面检查见运行目录 `delivery-verification.json`。

仅重建页面或补传既有回放，不调用模型：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\source-coverage-pycache'
python -X utf8 scripts/eval-source-coverage.py --resume artifacts/reports/stage-4/benchmark-source-coverage-v1/runs/e1283443e92d4181ab64cd2dd645fa13/summary.json
# 需要恢复上传时，在同一命令末尾加 --upload。
```

原 v1/v2 冻结契约与成绩不改写。生产代码已改变，旧 `eval-stage4.py --benchmark benchmark-v2` 的代码哈希保护会阻止把新算法记成旧版本；如后续需要真实生成对照，应另行冻结新执行契约，继续使用本诊断题集的既定问题与评分口径。
