# benchmark-v5-final-v1 最终版端到端 40 题对照报告（P3-RoundRobin-V2 vs P4-BalancedMMR-V3）

- 运行 ID：`142445977caf4321998af9713424faba`；模型：`deepseek-v4.1-flash`；题集 SHA-256：`7ddf3cfa20dc51d011f9451fac81f28ac74533b19d0c7b16421d1066a82ba001`。
- 两组共享同一份 Query Plan、同批查询向量与相同 QA-Graph+MethodCard 候选池，严格隔离 **Balanced-MMR 证据选择 + `source-choice-v3` (`[E1:q2]`) 单点引用协议**。

## 1. 核心指标对比（32 道可回答题 + 8 道反例）

| 指标 | P3-RoundRobin-V2 | P4-BalancedMMR-V3 | 差值 (P4 − P3) |
|---|---:|---:|---:|
| **32 题最终来源支持单元覆盖** | 86.98% | **87.50%** | **+0.52 pp** |
| **32 题必要来源全覆盖题数** | 25/32 | **25/32** | **+0 题** |
| **24 题跨论文关系来源覆盖** | 82.64% (17/24) | **83.33% (17/24)** | **+0.69 pp** |
| 8 题事实控制覆盖 | 100.00% (8/8) | 100.00% (8/8) | +0.00 pp |
| 事实单元归因（64 单元） | `{'covered': 53, 'in_pool_not_selected': 11}` | `{'covered': 53, 'in_pool_not_selected': 10, 'upstream_pool_miss': 1}` | covered +0 |
| **引用协议失败 (`citation_error`, 40题)** | 1/40 | **2/40** | **+1 条** |
| **反例拒答数 (`refused`, 8题)** | 6/8 | **6/8** | **+0 题** |
| 生成输入 / 输出 / 总 Token | 219,871 / 24,655 / 244,526 | 216,373 / **18,877** / 235,250 | 输出 -5,778 |
| 请求墙钟 P50 / P95 | 14.227s / 20.703s | 12.008s / 27.329s | - |
| 全量 40 题程序状态 | `{'ok': 23, 'partial': 9, 'citation_error': 1, 'refused': 7}` | `{'ok': 26, 'citation_error': 2, 'partial': 4, 'refused': 8}` | - |

逐题覆盖变化（32 题）：**1 增 / 30 平 / 1 退**。

## 2. LangSmith 与核验

- 远端实时 Trace 批量核验：`verified=True`，span 数 `476/476`，pending `0`。
- Dataset/Experiment 同步：`status=experiments_verified`；对照链接：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/e5de250b-0468-421f-9799-c13fbf70f058/compare?selectedSessions=0fa090e7-6def-435e-bf0d-9e3e8367326a,cfdc9e31-157d-4950-88a4-ad97cc48fa04
