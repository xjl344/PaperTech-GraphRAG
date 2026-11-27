# benchmark-v5-rerank-diversity-v2 零云端费用离线三组消融报告

- 运行 ID：`5134b6745dc94b3ba927d318ac260361`；题集 SHA-256：`fcdcd87adc1a64e7e164bb0fe15b04411557c24c91aff9cf5eec526d68f23d85`；云端调用：**0 次 DeepSeek / 0 次 Cloudflare**。
- 固定父运行候选池：`artifacts/reports/stage-4/benchmark-v5-graph-v1/runs/688a7351cda240aead9317da1471a777`（`Strong-Hybrid+QA-Graph+MethodCard`），纯本地验证 **跨子查询均衡配额 + MMR 去重** 与 **块内滑动引文窗精排** 对残余 11 个池内未入选单元的改善。

## 1. 三组核心指标对比（32 道可回答题）

| 指标 | P3-Baseline | Balanced-MMR | WindowRerank+Balanced-MMR |
|---|---:|---:|---:|
| SupportRecall@5 (32题) | 64.84% | 64.84% | **65.62%** |
| SupportRecall@8 (32题) | 75.00% | 75.00% | **79.17%** |
| MRR@40 (32题) | 0.6604 | 0.6604 | **0.7042** |
| **最终来源支持单元覆盖 (32题)** | 85.68% | **89.32%** | **88.54%** |
| **必要来源全覆盖题数 (32题)** | 23/32 | **25/32** | **25/32** |
| **跨论文关系来源覆盖 (24题)** | 80.90% (15/24) | **85.76% (17/24)** | **84.72% (17/24)** |
| 事实控制来源覆盖 (8题) | 100.00% (8/8) | 100.00% (8/8) | 100.00% (8/8) |
| 事实单元归因（64 单元） | `{'covered': 53, 'in_pool_not_selected': 11}` | `{'covered': 55, 'in_pool_not_selected': 9}` | `{'covered': 54, 'in_pool_not_selected': 10}` |
| 相对基线逐题变化 (32题) | 基线 | 3 增 / 28 平 / 1 退 | 3 增 / 27 平 / 2 退 |
| 平均证据块 / 字节 | 10.53 / 18360 B | 10.55 / 18499 B | 10.55 / 18393 B |
| 本地处理耗时 P50 / P95 | 0.003s / 0.008s | 0.016s / 0.030s | 4.615s / 6.724s |

## 2. LangSmith 对照链接

- 同步状态：`experiments_verified`；三组在线对照：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d7db79c0-088a-4aed-96d4-decef5835283/compare?selectedSessions=a883d84c-11bc-43df-8285-adab04fdc010,87c4d730-29b2-4dd2-a991-c44669d455cc,797b6b5d-4791-4ca0-bff3-44bdcd4227af

> 说明：本轮为 0 云端费用的离线检索与证据选择消融，不含新答案生成，覆盖率不代表人工语义准确率。
