# benchmark-v5-rerank-diversity-v1 零云端费用离线三组消融报告

- 运行 ID：`74e511de819e4deab7b075ef92e8ec0d`；题集 SHA-256：`7662799530b177ceed6bf54c5fdd1afea00ba44c926054d65687d0a404e96a15`；云端调用：**0 次 DeepSeek / 0 次 Cloudflare**。
- 固定父运行候选池：`artifacts/reports/stage-4/benchmark-v5-graph-v1/runs/688a7351cda240aead9317da1471a777`（`Strong-Hybrid+QA-Graph+MethodCard`），纯本地验证 **跨子查询均衡配额 + MMR 去重** 与 **块内滑动引文窗精排** 对残余 11 个池内未入选单元的改善。

## 1. 三组核心指标对比（32 道可回答题）

| 指标 | P3-Baseline | Balanced-MMR | WindowRerank+Balanced-MMR |
|---|---:|---:|---:|
| SupportRecall@5 (32题) | 64.84% | 64.84% | **65.62%** |
| SupportRecall@8 (32题) | 75.00% | 75.00% | **79.17%** |
| MRR@40 (32题) | 0.6604 | 0.6604 | **0.7042** |
| **最终来源支持单元覆盖 (32题)** | 85.68% | **85.16%** | **87.50%** |
| **必要来源全覆盖题数 (32题)** | 23/32 | **24/32** | **25/32** |
| **跨论文关系来源覆盖 (24题)** | 80.90% (15/24) | **80.21% (16/24)** | **83.33% (17/24)** |
| 事实控制来源覆盖 (8题) | 100.00% (8/8) | 100.00% (8/8) | 100.00% (8/8) |
| 事实单元归因（64 单元） | `{'covered': 53, 'in_pool_not_selected': 11}` | `{'covered': 52, 'in_pool_not_selected': 12}` | `{'covered': 53, 'in_pool_not_selected': 11}` |
| 相对基线逐题变化 (32题) | 基线 | 2 增 / 27 平 / 3 退 | 3 增 / 26 平 / 3 退 |
| 平均证据块 / 字节 | 10.53 / 18360 B | 10.57 / 18462 B | 10.47 / 18450 B |
| 本地处理耗时 P50 / P95 | 0.003s / 0.006s | 0.016s / 0.038s | 4.132s / 5.743s |

## 2. LangSmith 对照链接

- 同步状态：`experiments_verified`；三组在线对照：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/fa0016df-b712-41cc-92a4-ce777a9b197e/compare?selectedSessions=8adcb8f2-f81b-453a-a58f-f8d87ea8ed8a,9da19a97-9e35-4819-93e6-e49b9fcbe1f1,d87bd76c-daea-48a4-8f23-33c3a16f3401

> 说明：本轮为 0 云端费用的离线检索与证据选择消融，不含新答案生成，覆盖率不代表人工语义准确率。
