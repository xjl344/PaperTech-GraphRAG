# benchmark-v4-p0-v2 实测对比报告（Baseline-Legacy vs P0-Optimized）

- 运行 ID：`14f182748b734967817ba248aa4ec88b`；题集 SHA-256：`f5135e2751c2efcc083b6b5bdd1ffc973e2caf8e5dac66b7ef4ea9b3179683f8`；状态：`completed`。
- 对照设计：40 题 × 2 组（纯 Hybrid，均关闭图扩展），共享同一批冻结 Cloudflare BGE-M3 查询向量与相同 Neo4j 上游候选，严格隔离 P0 三件套（1.1a 上下文微批重排 + 1.2 18000/12 轮转保底与相对阈值 + 1.3 `[E1]` 短编号与精确正则）。

## 1. 汇总指标（32 道可回答题）

| 指标 | Baseline-Legacy | P0-Optimized | 差值 (P0 - Baseline) |
|---|---:|---:|---:|
| SupportRecall@5 | 61.20% | 61.72% | +0.52 pp |
| SupportRecall@8 | 69.01% | 68.49% | -0.52 pp |
| MRR@40 | 0.5791 | 0.5821 | +0.0030 |
| 最终来源支持单元覆盖 | 61.20% | 75.26% | +14.06 pp |
| 必要来源全部覆盖题数 | 13/32 | 19/32 | +6 题 |
| 引用协议失败 (`citation_error`) | 0/40 | 2/40 | +2 条 |

逐题变化（32 题）：Recall@5 3 增 / 27 平 / 2 退；最终来源覆盖 9 增 / 23 平 / 0 退。

## 2. 分类指标

| 类别 | 指标 | Baseline-Legacy | P0-Optimized | 差值 |
|---|---|---:|---:|---:|
| 事实控制 (8题) | 最终来源覆盖 / 全覆盖 | 100.00% (8/8) | 100.00% (8/8) | +0.00 pp |
| 跨论文关系 (24题) | Recall@5 | 48.26% | 48.96% | +0.69 pp |
| 跨论文关系 (24题) | 最终来源覆盖 / 全覆盖 | 48.26% (5/24) | 67.01% (11/24) | +18.75 pp |
| 反例 (8题) | 程序状态分布 | `{'partial': 6, 'refused': 1, 'ok': 1}` | `{'partial': 5, 'ok': 2, 'citation_error': 1}` | refused -1 |

## 3. 时延、证据规模、Token 与状态

| 项目 | Baseline-Legacy | P0-Optimized |
|---|---:|---:|
| 检索计算 P50 / P95 | 0.876s / 0.994s | 0.908s / 1.079s |
| 重排耗时 P50 / P95 | 0.830s / 0.958s | 0.873s / 1.030s |
| 请求墙钟 P50 / P95（含生成与追踪） | 9.262s / 12.401s | 9.420s / 12.155s |
| 平均证据块数 / 平均字节 | 3.55 / 5677 B | 10.05 / 17080 B |
| 生成输入 / 输出 / 总 Token | 72,018 / 16,834 / 88,852 | 184,365 / 13,221 / 197,586 |
| 全量 40 题程序状态 | `{'ok': 16, 'partial': 23, 'refused': 1}` | `{'ok': 19, 'partial': 19, 'citation_error': 2}` |

## 4. LangSmith 与核验

- 远端 Trace 核验：`verified=False`，span 数 `405`，pending `0`。
- Dataset/Experiment 同步：`status=experiments_verified`；对照链接：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/4f4238f2-ab63-4eb5-bf3c-97958b8b1a41/compare?selectedSessions=7e46c8fe-16f2-45c5-a13a-bf44572bf438,67715740-7128-4934-b6f5-08f69bc0e817

> 说明：上述支持池覆盖与引用状态均为程序自动统计，不等于独立人工语义正确率；本轮仍为已曝光开发集对照。
