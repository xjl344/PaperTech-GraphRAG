# benchmark-v5-graph-v1 实测对比报告（Strong-Hybrid-P2 vs Strong-Hybrid+QA-Graph+MethodCard）

- 运行 ID：`688a7351cda240aead9317da1471a777`；题集 SHA-256：`b334219c49189062fecc4030d1c07b9b7336c6ee820ad3dd3fd0f339f198465d`；状态：`completed`。
- 对照设计：40 题 × 2 组，两组共享同一次云端 Query Plan 与同一批查询向量，在第二步强 Hybrid 基线上严格启停 **Query-aware Claim 向量图扩展 + 14 篇结构化方法卡导航 + 独立 1200B 路径预算**。

## 1. 汇总指标（32 道可回答题 + 8 道反例）

| 指标 | Strong-Hybrid-P2 | Strong-Hybrid+QA-Graph+MethodCard | 差值 |
|---|---:|---:|---:|
| SupportRecall@5 (32题) | 64.84% | 64.84% | +0.00 pp |
| SupportRecall@8 (32题) | 73.96% | 75.00% | +1.04 pp |
| MRR@40 (32题) | 0.6604 | 0.6604 | +0.0000 |
| **最终来源支持单元覆盖 (32题)** | 84.64% | **85.68%** | **+1.04 pp** |
| **必要来源全部覆盖题数 (32题)** | 22/32 | **23/32** | **+1 题** |
| 事实单元归因（64 单元） | `{'covered': 52, 'in_pool_not_selected': 11, 'upstream_pool_miss': 1}` | `{'covered': 53, 'in_pool_not_selected': 11}` | covered +1 |
| 引用协议失败 (`citation_error`, 40题) | 3/40 | 4/40 | +1 条 |
| 反例拒答数 (`refused`, 8题) | 4/8 | 5/8 | +1 题 |

逐题变化（32 题）：Recall@5 0 增 / 32 平 / 0 退；最终来源覆盖 1 增 / 31 平 / 0 退。

## 2. 分类指标

| 类别 | 指标 | Strong-Hybrid-P2 | Strong-Hybrid+QA-Graph+MethodCard | 差值 |
|---|---|---:|---:|---:|
| 事实控制 (8题) | 最终来源覆盖 / 全覆盖 | 100.00% (8/8) | 100.00% (8/8) | +0.00 pp |
| 跨论文关系 (24题) | Recall@5 | 53.12% | 53.12% | +0.00 pp |
| 跨论文关系 (24题) | **最终来源覆盖 / 全覆盖** | 79.51% (14/24) | **80.90% (15/24)** | **+1.39 pp** |
| 反例 (8题) | 程序状态分布 | `{'refused': 4, 'partial': 1, 'ok': 2, 'citation_error': 1}` | `{'refused': 5, 'citation_error': 3}` | refused +1 |

## 3. 时延、图/方法卡命中、Token 与状态

| 项目 | Strong-Hybrid-P2 | Strong-Hybrid+QA-Graph+MethodCard |
|---|---:|---:|
| 图扩展+方法卡导航耗时 P50 / P95 | 0.000s / 0.000s | 0.098s / 0.156s |
| 检索计算 P50 / P95（注：第二组复用同题缓存规划与向量） | 4.159s / 8.334s | 4.166s / 9.651s |
| 平均采用图路径数 / 方法卡导航候选数 | 0.00 / 0.00 | 1.77 / 14.25 |
| 生成输入 / 输出 / 合计 Token | 193,337 / 24,138 / 217,475 | 220,959 / 24,372 / 245,331 |
| 全量 40 题程序状态 | `{'ok': 22, 'citation_error': 3, 'partial': 9, 'refused': 6}` | `{'ok': 22, 'partial': 8, 'refused': 6, 'citation_error': 4}` |

## 4. LangSmith 与核验

- 远端实时 Trace 批量核验：`verified=False`，span 数 `478/479`，pending `0`。
- Dataset/Experiment 同步：`status=experiments_verified`；对照链接：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/0437d7c1-c732-4806-a9b0-ab2828d46cf9/compare?selectedSessions=3f398266-bcc6-4187-855b-399167307d3b,2325c53c-6117-4644-836b-0cd4809f55a1

> 说明：上述支持池覆盖、反例程序拒答状态与引用状态均为自动统计，不等于独立人工语义正确率；本轮仍为已曝光开发集对照，不预设图扩展胜出。
