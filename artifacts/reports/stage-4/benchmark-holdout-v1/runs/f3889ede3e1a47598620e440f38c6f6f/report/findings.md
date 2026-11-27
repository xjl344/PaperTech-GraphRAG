# benchmark-holdout-v1 18 题全新未见泛化评测报告（Legacy-Hybrid vs Production-Final）

- 运行 ID：`f3889ede3e1a47598620e440f38c6f6f`；模型：`deepseek-v4.1-flash`；题集 SHA-256：`3b871c53c664e26d9190ec6c102290b4991ce068960ce8572ee5a9305c85dfe6`。
- 样本外声明：18 道题与 `benchmark-v4`（40 题）**零重叠**，覆盖 14 篇论文的新机制/消融/误差分析/伪前提陷阱。

## 1. 核心指标对比（14 道可回答题 + 4 道反例）

| 指标 | Legacy-Hybrid | Production-Final | 差值 (Prod − Legacy) |
|---|---:|---:|---:|
| **14 题最终来源支持单元覆盖** | 46.43% | **95.24%** | **+48.81 pp** |
| **14 题必要来源全覆盖题数** | 4/14 | **13/14** | **+9 题** |
| **8 题跨论文关系来源覆盖** | 37.50% (2/8) | **91.67% (7/8)** | **+54.17 pp** |
| 6 题事实题来源覆盖 | 58.33% (2/6) | 100.00% (6/6) | +41.67 pp |
| 事实单元归因 | `{'covered': 13, 'upstream_pool_miss': 4, 'in_pool_not_selected': 13}` | `{'covered': 28, 'in_pool_not_selected': 2}` | covered +15 |
| **引用协议失败 (`citation_error`, 18题)** | 1/18 | **3/18** | **+2 条** |
| **反例拒答数 (`refused`, 4题)** | 0/4 | **4/4** | **+4 题** |
| 生成输入 / 输出 / 总 Token | 34,108 / 7,057 / 41,165 | 96,121 / 8,605 / 104,726 | - |
| 请求墙钟 P50 / P95 | 8.744s / 9.486s | 15.933s / 17.946s | - |
| 全量 18 题程序状态 | `{'ok': 3, 'partial': 14, 'citation_error': 1}` | `{'ok': 9, 'citation_error': 3, 'partial': 2, 'refused': 4}` | - |

逐题覆盖变化（14 题）：**10 增 / 4 平 / 0 退**。

## 2. LangSmith 与核验

- 远端实时 Trace 批量核验：`verified=True`，span 数 `219/219`，pending `0`。
- Dataset/Experiment 同步：`status=experiments_verified`；对照链接：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/c5323228-5528-4db6-a6b4-642d361eaf3e/compare?selectedSessions=e4b3851d-b5fe-4a44-8a34-2285b262ce53,1df3dffe-5513-45ce-9af2-f680133ab87d
