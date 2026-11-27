# benchmark-v2 实测与判读

2026-11-15，运行 `a2ab6cdee7144b96b7627ac96582fc87` 已完成 40 题配对执行：Hybrid 与 Hybrid＋Graph 各 40 条结果，真实生成各 32 次。基础事实与改写各 4 题仅检索，24 道跨文本关系题与 8 道反例均实际生成。模型结果记录于当天 15:34—15:45（北京时间）；之后进行远端核验和展示导出，不重复调用模型。

[汇总与分类对照](runs/a2ab6cdee7144b96b7627ac96582fc87/report/comparison.md) · [离线指标、柱状图与 40 题详情](runs/a2ab6cdee7144b96b7627ac96582fc87/report/dashboard.html) · [逐题协议与来源诊断](runs/a2ab6cdee7144b96b7627ac96582fc87/diagnostics.md)

| 指标 | Hybrid | Hybrid＋Graph |
|---|---:|---:|
| SupportRecall@5，32 道可回答题 | 54.17% | 52.60% |
| SupportRecall@8 | 65.10% | 63.54% |
| MRR@40 | 0.5322 | 0.5541 |
| 入选证据的必要事实覆盖 | 44.79% | 44.79% |
| 全部必要事实覆盖题数 | 8 / 32 | 8 / 32 |
| 跨文本 24 题 Recall@5 | 38.89% | 36.81% |
| 跨文本入选证据的必要事实覆盖 | 26.39% | 26.39% |
| 检索计算 P95，秒 | 1.318 | 1.371 |
| 请求墙钟 P95，秒 | 10.110 | 10.131 |
| 实际生成调用 | 32 | 32 |
| 已知输入 / 输出 Token | 57704 / 13963 | 56278 / 13542 |
| 引用协议失败 | 4 | 3 |

召回、MRR 与事实覆盖的分母排除 8 道反例；请求墙钟、状态及 Token 保留全部 40 题。检索计算排除共享云向量、追踪上传和生成；请求墙钟包含追踪开销，排除共享预热和批量向量。64 次生成 Usage 均已返回；共享 Cloudflare 批次 Usage 未返回，保留 unknown，不计算金额。

## 观察到的差异

- 本轮没有观察到图扩展带来的覆盖收益。32 道可回答题的 Recall@5 为 31 道持平、1 道退化；MRR 为 3 道上升、2 道下降、27 道持平。两组基础全文与 Dense 候选一致。
- R05 是唯一 Recall@5 退化题：Hybrid 中 ToG、RoG 主支持分别位于第 3、4；图组 ToG 升到第 2，RoG 主支持退出最终 40 候选。该题 Recall 从 100% 降至 50%，MRR 却从 1/3 升至 1/2，说明首次命中更早不等于比较双方证据更齐。
- R09 中 Hybrid 保留 ToG 第 6 页实验表与 ToG-2 来源，图组丢失 ToG 表；主支持池未包括这个等价表格来源，两组最终覆盖都记为 0，分数没有反映该差异。
- 两组各有 8 条 evidence_only、23 条 partial、1 条 refused；Hybrid 另外 4 条 ok / 4 条 citation_error，图组为 5 条 ok / 3 条 citation_error。这些是程序状态，不是正确率。N06 为真实生成后的拒答。

## 引用与来源问题

7 条失败分别为 R05/H、R07/G、R08/G、R10/G、R18/H、R19/H、N04/H。涉及使用 q1/q2 代替 chunk ID、抄入原论文文献号、错误 chunk ID、无效 quote_id 及生成 Schema 失败。原结果保留；可解析失败草稿仅标为诊断材料，未当作有效回答。

80 条结果均做了协议与必要论文来源检查。48 条跨文本结果中，17 条入选证据包含全部所需论文；这只能说明来源出现，不能证明相关论断被支持。另对 R03、R05、R07、R08、R09、R11、N04、N06、N08 的两组结果定向核对原文，记录在运行目录的 `source-review.json`，并关联逐题诊断。核查由 Codex 执行，没有独立专家逐题语义评分。

R07 的 KGP 方法及结论片段、R09 的 ToG 结果表等有效支持未纳入冻结支持池；保留当前分数，不后验修改 v2 金标。不能把低覆盖简单解释为没有有效证据，也不能把来源篇数、引用形式或 ok 状态解释为答案正确。需要补充来源池时应创建新版本，再做可比较的复验。

## 复现与验证

本轮冻结题集 SHA-256 为 `c26881d38a57a0460dd5a946468de9923e1dca65d372c25d8063fde5081c78ec`。旧 v1 题集与成绩保留；两版题型分布不同，不能用总体分数变化判断系统变好或变差。本轮没有修改生产检索/生成算法。

80 条记录的指标重算、来源引句、可接受引用、生成路径与预算程序检查通过。14 篇 / 980 块 / 89 条批准关系不变；源哈希不变，图逻辑哈希不变，613 条返回图路径的 Claim/Chunk/引句血缘检查通过。这些程序检查不替代语义质量检查。89 项本地回归通过，详细输出在本次运行目录的 `test-results.txt`；远端与展示最终交付检查见同目录 `delivery-verification.json`。

单次开发集运行没有独立重复实验或统计显著性结论。未采集整机 CPU/RAM/温度曲线，没有完整生产图路径金标或全面独立语义评分；本轮交付不改变扩量准入状态。

仅重建页面，无模型调用：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\stage4-v2-pycache'
python -X utf8 scripts/report-evaluation.py --benchmark benchmark-v2 --run-summary artifacts/reports/stage-4/benchmark-v2/runs/a2ab6cdee7144b96b7627ac96582fc87/summary.json
```

LangSmith Dataset 每题一条 Example，参考答案与来源在 reference outputs；每组 Experiment 保存 40 条实际结果、完整逐题信息、原生时延/Token 与指标反馈。远端入口及回读状态保存在运行目录的 `langsmith-status.json`，总览页面直接链接两组对照。后续断网恢复仅补传保存结果，不重放模型。

原生 Token 展示单独核查时发现，LangSmith 不会仅凭 chain 创建参数中的 Token 填充原生统计。已按本地供应商调用账本为每组导入 32 条 LLM 子记录，使用实际调用时间、Usage 与稳定 ID，父记录仍是原 40 条结果。子记录仅表达已发生的调用，没有重发模型、改变答案或增加实际 Token。每题及项目汇总原生统计均另行回读。修复后 19 项评测相关回归通过（含新增 2 项），代码导出版本另记于最终交付验证，不回写运行前冻结契约。
