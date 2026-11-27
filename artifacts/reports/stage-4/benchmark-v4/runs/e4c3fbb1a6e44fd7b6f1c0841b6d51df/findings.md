# benchmark-v4 实测结果

运行 `e4c3fbb1a6e44fd7b6f1c0841b6d51df` 已完成 40 题 × 2 组，共 80 条结果、80 次 DeepSeek 生成。题集 SHA-256 为 `2904af152a4bffd86119cbbf030d0ac658e909cc22d1abdf2b4d398f67d02451`；两组基础全文/Dense 候选逐题一致，图组只增加冻结 v3 隔离图扩展。

## 是否提升

有小幅检索排序提升，但没有“全面提升”。排除 8 道反例后的 32 道可回答题上：

| 指标 | Hybrid | Hybrid＋Graph | Graph−Hybrid |
|---|---:|---:|---:|
| SupportRecall@5 | 61.20% | 62.76% | +1.56 个百分点 |
| SupportRecall@8 | 69.01% | 70.57% | +1.56 个百分点 |
| MRR@40 | 0.5791 | 0.5864 | +0.0073 |
| 最终来源支持单元覆盖 | 61.20% | 60.68% | −0.52 个百分点 |
| 必要来源全部覆盖题数 | 13/32 | 12/32 | −1 题 |

逐题变化为：Recall@5 1 增、31 平、0 退；Recall@8 1 增、31 平、0 退；MRR 2 增、30 平、0 退；最终来源支持覆盖 1 增、30 平、1 退。增益来自少数题的排序前移，整体提升很小；图扩展没有增加最终证据覆盖，且有一题出现证据退化。

跨论文关系题单独看，Recall@5 从 48.26% 提到 50.35%，最终来源覆盖从 48.26% 降到 47.57%，必要来源全部覆盖题数从 5 降到 4。8 道事实控制题两组均为 100% 来源支持覆盖、8/8 必要来源全部覆盖。8 道反例不计入召回分母；Hybrid 拒答 1 题，图组没有拒答，但程序状态不能当作答案准确率。

## 代价与状态

- 检索计算 P50/P95：Hybrid `0.918/1.057s`；Hybrid＋Graph `1.011/1.186s`。图组约增加 10%–12% 检索计算时延。
- 请求墙钟 P95：Hybrid `9.530s`；Hybrid＋Graph `9.311s`。该值含实际 tracing 开销，不用于判断图扩展计算成本。
- 已知生成 Token：Hybrid 输入/输出 `72,018/16,583`；图组 `85,454/16,646`。图组多 `13,436` 输入 Token（约 18.7%），因为本轮允许最多 1200 字节额外图路径上下文；这不是同 Token 预算消融。
- 程序状态：Hybrid `ok 17 / partial 19 / citation_error 3 / refused 1`；图组 `ok 16 / partial 22 / citation_error 2`。引用协议失败 5 条，均保留完整模型草稿供诊断，没有自动重生成。

## 逐题解释

每题详情位于 `report/dashboard.html`、`report/comparison.json` 和本目录的 `Fxx-*.json` / `Rxx-*.json` / `Nxx-*.json`。新增的 `criterion_source_coverage` 逐判分点显示来源是否进入证据上下文；`semantic_score=null` 明确表示尚无独立人工语义评分。

R06 是典型退化：Hybrid 选中了 LPKG 的完整结论块，图组只选中较短的 LPKG 方法块，导致图组缺少“规划数据用于训练规划能力”的来源。图路径存在不等于路径证据被最终选择，也不等于答案关系判断正确。

## LangSmith 与验证

- Dataset `papertech-stage4-benchmark-v4` 已核对 40/40 Example、40/40 详细 Example、89 条来源展示记录。
- Hybrid Experiment 已核对 40 条 run、320 条反馈、40 个生成用量子 run；Hybrid＋Graph 同样为 40/320/40。
- [LangSmith 两组对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/a82228b8-0434-40b7-9311-1dca5e330ceb/compare?selectedSessions=3c8ecf01-a3a6-442f-90d0-5d97f6ebb395,4bfb5ec7-67eb-4a80-9df0-713ee7b33a0f)
- 本地 `verification.json` 的全部配置、配对、哈希、预算、候选一致性、远端 Experiment/反馈和原始 Trace 回读均通过。批量核验回读 80 个根 Trace、共 400 个 Trace span，0 个 pending event；原始 Trace URL 已补齐到 80/80 逐题结果。

本轮只证明这套冻结开发集和图扩展配置的检索差异，不证明答案语义正确率、统计显著性或 Graph 在生产全量语料上优于 Hybrid。下一步应优先修复证据选择中的来源保留/路径挤占问题，再进行独立人工语义评分。
