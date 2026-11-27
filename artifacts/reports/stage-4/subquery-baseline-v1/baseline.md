# 子查询基线冻结 v1

本文件冻结图谱对照前的子查询链路。五个来源实验均已完成 LangSmith Dataset/Experiment 读回校验；本次只做本地独立汇总，没有重新调用模型。

## 冻结配置

- 分流：query-router-fix，包含 R11 的 quote 规范化修复。
- 召回：原问题 vs 原问题加子查询，全文 Top20 + dense Top20，候选上限 40。
- 候选策略：完整并集上的原问题重排、归属子查询重排、max 融合。
- 证据策略：6000 bytes / 8 blocks / named_first。
- 图谱和答案生成：排除。

## 主要结果

| 层级 | 方案 | 必要来源覆盖 | 来源命中 |
|---|---|---:|---:|
| 候选40 | Original | 59.72% | 29/49 |
| 候选40 | Expanded | 68.06% | 33/49 |
| 完整并集重排 | Original | 70.83% | 34/49 |
| 完整并集重排 | Owner | 74.31% | 36/49 |
| 证据6000/8 | Original-Reused | 31.25% | 15/49 |
| 证据6000/8 | Owner-Clean | 41.67% | 20/49 |

## R11 修复增量

- 路由差异数：1。
- R11 Original：1/2 进入并集，1/2 留在40条。
- R11 修复后 Expanded：1/2 进入并集，1/2 留在40条。
- 修复恢复了子查询链路，但没有补回 R11.S02。

## 使用边界

- 24 题和 49 个必要来源属于已曝光开发集，不是泛化验收。
- 覆盖率只表示来源是否进入候选或证据，不代表答案语义正确率。
- R11 修复是单独增量；其余 23 题没有被重新重排。
- 后续图谱对照应固定使用本文件的题集、来源池、预算和评分口径，另建 benchmark 版本。

## LangSmith 来源
- router_fix: dataset 5a66b27d-0f93-4e20-b796-22d397f184c7; comparison https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/5a66b27d-0f93-4e20-b796-22d397f184c7/compare?selectedSessions=2679d4cf-07d9-4055-ae81-d8b7870035dc,a5e86f17-68db-4b16-9753-daa9d49437f0
- recall_full: dataset 267ea085-39ea-4815-99dd-b2f36f2b1954; comparison https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/267ea085-39ea-4815-99dd-b2f36f2b1954/compare?selectedSessions=9239e993-2f34-4d5e-aac2-804257c80ca2,c29992a9-535c-42d7-ad1b-1ce89a6efa20
- recall_router_fix: dataset 4539be45-c34f-48ea-931d-ecdf1518878e; comparison https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/4539be45-c34f-48ea-931d-ecdf1518878e/compare?selectedSessions=376930ea-d7f2-4150-992e-68ff6d342868,6b50a156-c8e1-4934-b340-24e66844e07e
- policy: dataset b0aefb4a-a733-4151-8def-4e0cbf8e5942; comparison https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/b0aefb4a-a733-4151-8def-4e0cbf8e5942/compare?selectedSessions=608743bc-108f-4685-9502-883f8de4c6a6,e6512f9f-201c-4d23-9998-03f684d400ee,805f25ba-a657-48de-8a1b-aaacea4174e8,a81b8658-347b-4a6d-90da-42a9c5634204,fd0d33a8-4138-4c99-a0b5-49f5ecb5754d,2cd82e14-931e-4806-bfd8-553d3f8fcfee,daf86c62-4bf6-4829-b383-50ced0e89874,04a195f2-b394-4d44-9bfe-94c957da01df
- rerank_clean: dataset a0cbbb0a-b809-4ada-871b-9cdc9da9b8ab; comparison https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/a0cbbb0a-b809-4ada-871b-9cdc9da9b8ab/compare?selectedSessions=06481603-5634-48e8-9d5d-ddcc0ed7794f,7f40e948-e8ff-4cb4-8dca-aac93b3ba797,66db67bd-5933-45b5-9ea7-49407421603c
