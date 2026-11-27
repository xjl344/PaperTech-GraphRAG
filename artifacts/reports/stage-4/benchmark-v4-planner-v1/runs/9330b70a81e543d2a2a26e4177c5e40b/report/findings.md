# benchmark-v4-planner-v1 实测对比报告（P0-SingleQuery vs P2-Planner-OwnerRerank）

- 运行 ID：`9330b70a81e543d2a2a26e4177c5e40b`；题集 SHA-256：`5e50acf752ca88bb0adfe9b64176f71728288a175767ebdea52f4aaf12ad8aa9`；状态：`completed`。
- 对照设计：40 题 × 2 组（纯 Hybrid，均关闭图扩展），在已验证胜出的 P0 配置（1.1a+1.2+1.3）上严格隔离第二步增量（云端 Flash Query Planner + 英文关键词全文检索 + 并发多查询召回 + 归属重排 + 子查询保底 + 结构化 `premise_check`）。

## 1. 汇总指标（32 道可回答题 + 8 道反例）

| 指标 | P0-SingleQuery | P2-Planner-OwnerRerank | 差值 (P2 − P0) |
|---|---:|---:|---:|
| SupportRecall@5 (32题) | 61.72% | 67.19% | +5.47 pp |
| SupportRecall@8 (32题) | 68.49% | 77.34% | +8.85 pp |
| MRR@40 (32题) | 0.5821 | 0.7094 | +0.1273 |
| **最终来源支持单元覆盖 (32题)** | 75.26% | **86.20%** | **+10.94 pp** |
| **必要来源全部覆盖题数 (32题)** | 19/32 | **23/32** | **+4 题** |
| 事实单元归因（64 单元） | `{'covered': 45, 'upstream_pool_miss': 13, 'in_pool_not_selected': 6}` | `{'covered': 53, 'in_pool_not_selected': 10, 'upstream_pool_miss': 1}` | upstream_miss -12 |
| 引用协议失败 (`citation_error`, 40题) | 2/40 | 2/40 | +0 条 |
| 反例拒答数 (`refused`, 8题) | 0/8 | 7/8 | +7 题 |

逐题变化（32 题）：Recall@5 4 增 / 28 平 / 0 退；最终来源覆盖 8 增 / 23 平 / 1 退。

## 2. 分类指标与路由行为

| 类别 | 指标 | P0-SingleQuery | P2-Planner-OwnerRerank | 差值 |
|---|---|---:|---:|---:|
| 事实控制 (8题) | 最终来源覆盖 / 全覆盖 | 100.00% (8/8) | 100.00% (8/8) | +0.00 pp |
| 事实控制 (8题) | Planner 拆分题数（误拆监测） | 0/8 | 1/8 | - |
| 跨论文关系 (24题) | Recall@5 | 48.96% | 56.25% | +7.29 pp |
| 跨论文关系 (24题) | **最终来源覆盖 / 全覆盖** | 67.01% (11/24) | **81.60% (15/24)** | **+14.58 pp** |
| 跨论文关系 (24题) | Planner 拆分题数 | 0/24 | 24/24 | - |
| 反例 (8题) | 程序状态分布 | `{'partial': 5, 'ok': 2, 'citation_error': 1}` | `{'refused': 7, 'partial': 1}` | refused +7 |

## 3. 时延、Planner 开销、Token 与状态

| 项目 | P0-SingleQuery | P2-Planner-OwnerRerank |
|---|---:|---:|
| Planner 路由决策分布 (40题) | - | `{'no_split': 8, 'split': 32}` |
| Planner 耗时 P50 / P95（对比本地14B 32.9s） | - | 3.813s / 6.483s |
| 检索计算 P50 / P95（P2 含规划与多路重排） | 0.978s / 1.181s | 7.275s / 10.783s |
| 重排耗时 P50 / P95 | 0.929s / 1.126s | 1.591s / 2.296s |
| 请求墙钟 P50 / P95（含生成与追踪） | 10.084s / 17.185s | 17.927s / 27.123s |
| Planner 输入 / 输出 Token | 0 / 0 | 17,236 / 9,229 |
| 生成输入 / 输出 Token | 180,586 / 12,756 | 191,988 / 24,621 |
| 全链路 DeepSeek 总 Token | 193,342 | 243,074 |
| 全量 40 题程序状态 | `{'ok': 17, 'partial': 21, 'citation_error': 2}` | `{'ok': 18, 'partial': 12, 'citation_error': 2, 'refused': 8}` |

## 4. LangSmith 与核验

- 远端实时 Trace 批量核验：`verified=True`，span 数 `477/477`，pending `0`。
- Dataset/Experiment 同步：`status=experiments_verified`；对照链接：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/8adbb0df-1475-470c-b9c9-d374977f2732/compare?selectedSessions=7c1bdf1a-3a06-46cc-a088-588db1fb48fd,c4bb1a9a-04d9-4ae4-a554-f055a1220fb1

> 说明：上述支持池覆盖、反例程序拒答状态与引用状态均为自动统计，不等于独立人工语义正确率；本轮仍为已曝光开发集对照。
