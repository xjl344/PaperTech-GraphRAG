# 16 题路径预算逐题归因

固定真实候选，三组总预算均为 6000 字节；本表是程序证据归因，不是答案语义评分。

0 为原文优先、路径使用剩余空间；800/1200 为专用路径配额，原文预算分别为 5200/4800。

[汇总报告](report.md) · [完整回答、原文及 Trace](dashboard.html)

## R03

结合 KGP 和 CuriousLLM 原文，后者针对前者提出了什么增强？把多文档图、遍历代理、后续问题及其监督信号串起来，并区分作者评价与已验证事实。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 50.0% | 50.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | kgp | kgp | kgp |
| 程序状态 | citation_error | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_f783bd933d0d2a437496939e022a776a
- 丢失事实：无
- 新增事实：无
- 图路径去向：原始快照无图路径

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_9f06285c9b321c365675a3b670256a07
- 丢失事实：无
- 新增事实：无
- 图路径去向：原始快照无图路径

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/e891baca-709e-4361-bc7a-c058fdec37d6?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/dbe155b1-5487-4922-bde6-20718896042c?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7a0a7107-e6c9-4300-ab07-9bcbf78097e3?poll=true)

## R04

比较 StructGPT 与 LPKG：一个方法在回答时如何获得证据，另一个方法在训练时如何获得规划数据？说明 KG/结构化数据在两者中的不同角色。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | struct, lpdata | struct, lpdata | struct, lpdata |
| 程序状态 | ok | ok | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_072d1d7f534ffdbb7644a330aeea94fa
- 移除原文：chunk_73bc55c51e0886e7dda37a98fe4fe0cb, chunk_80af5b3aa25d71d17409ebe2b757ab19
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 1 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_0bd33867fd3e8c1883e6ad37bcb38ec6
- 移除原文：chunk_73bc55c51e0886e7dda37a98fe4fe0cb, chunk_80af5b3aa25d71d17409ebe2b757ab19
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d23afe55-b0ac-4c20-ad38-e30995be9742?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d54cb4db-c2af-483a-8141-05fd259178b5?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/1c61595b-509e-4956-9a82-d82884f2dc55?poll=true)

## R05

ToG 和 RoG 都利用 KG 推理，为什么不能据此把两者都归为免训练方法？分别追踪 KG 在在线搜索和训练中的作用。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | rog | tog_training, rog | tog_training, rog |
| 程序状态 | ok | citation_error | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_529e795e797b26de48cdc1fe5cbea79c
- 移除原文：chunk_e09b5a88c34014513aad6c0d6121f790
- 丢失事实：tog_training：ToG 将自身描述为 training-free，支持即插即用且无需额外训练。
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 19 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_44ca1868cc8294f6cfe2d5991cbd0d4b
- 移除原文：chunk_e09b5a88c34014513aad6c0d6121f790
- 丢失事实：tog_training：ToG 将自身描述为 training-free，支持即插即用且无需额外训练。
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 19 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/a176a3d7-4589-400b-b2c6-6f5d748c7189?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/cc0355fa-db17-475b-8741-88d4381a935b?poll=true)

## R06

比较 ToG-2 与 LPKG：图知识分别怎样帮助文档证据检索和问题规划？说明二者发生在训练还是推理阶段。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 100.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | 无 | 无 | 无 |
| 程序状态 | ok | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_4e496c498fc0ed5a85dbab9bf21e5612
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 24 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_4e496c498fc0ed5a85dbab9bf21e5612
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 24 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/2d616ffb-f186-4dcc-a93d-87d5a30b8d9b?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/e07c36f2-2837-4d29-b2a2-2a6f705f4d63?poll=true)

## R08

G-Retriever 与 ToG-2 都用图帮助获取上下文，但它们选择证据的机制怎样不同？分别连接输入规模问题、相关子图选择以及实体和文档的协作。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 33.3% | 33.3% | 33.3% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | pcst, grscale | pcst, grscale | pcst, grscale |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_44ca1868cc8294f6cfe2d5991cbd0d4b
- 移除原文：chunk_9b63637ef18ed2d67ff105ef55092df3
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 23 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_44ca1868cc8294f6cfe2d5991cbd0d4b
- 移除原文：chunk_9b63637ef18ed2d67ff105ef55092df3
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 23 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/ea2618af-950a-44ed-840b-ca094e4ccfd7?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6ff60e7c-2b6c-48f8-931a-bf26ed269b5a?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/32df3dc7-e0c3-4616-89e8-c263215a405b?poll=true)

## R09

从 ToG 与 ToG-2 的评测段落出发，找出共同使用的 WebQSP 与 QALD10-en，分别给出“方法→数据集”的来源，再说明为什么这个连接不能证明优劣或继承。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | togds, tog2ds | togds, tog2ds | togds, tog2ds |
| 程序状态 | ok | partial | citation_error |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_b5d573a408ceb1009fa63dcd9cdd6a1c
- 移除原文：chunk_031b7aaba8f20d011a94bb6a15b0f3b1
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

各组回答 Trace：[Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/89fa445f-888e-4c28-a8fd-fa8649793eb4?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/68b4967f-e68e-43a6-8cae-373eaface12e?poll=true)

## R11

沿“KG-GPT/RoG→MetaQA→跳数与指标/知识来源”比较两篇实验。RoG 中 Freebase 与 Wiki-Movies 分别承担什么角色？每个角色须给出原文。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 50.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 1 | 2 |
| 路径字节 | 0 | 451 | 902 |
| 未覆盖事实 | rogmeta | rogmeta | 无 |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_5a1fd5f3826cd78a6219d6bddfaa91da
- 移除原文：chunk_229cb41ae3582cc199c9ee25c4956269, chunk_8ff52490cf78a4324c98eaf422d29221
- 丢失事实：无
- 新增事实：无
- 图路径去向：已采用 1 条；支持原文未入选，禁止发送路径 5 条；配额不足或已达 4 条上限 2 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_f5c88d605f651f26c093f30b836a98aa
- 移除原文：chunk_229cb41ae3582cc199c9ee25c4956269, chunk_8ff52490cf78a4324c98eaf422d29221
- 丢失事实：无
- 新增事实：rogmeta：RoG 的迁移/扩展实验选 MetaQA-3hop，基于 Wiki-Movies，并取 1000 个训练样本。Freebase 是迁移训练来源，不是该 MetaQA-3hop 的测试知识图谱。
- 图路径去向：已采用 2 条；支持原文未入选，禁止发送路径 2 条；配额不足或已达 4 条上限 4 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d3317e48-07f2-49ae-a0cf-3717cdec3aea?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7048a3ad-29f8-4f23-a501-10b318b7192f?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7d6bc1f8-d6f5-4a8a-97cd-2a0225c2bc8e?poll=true)

## R12

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 与 LPKG 的 CLQA-Wiki 怎样分别连接到知识来源？虽然都涉及 Wikidata，二者考察的关系推理能力有何区别？

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 100.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | 无 | 无 | 无 |
| 程序状态 | ok | ok | ok |

**Path-800 相对 Path-0：**

- 新增原文：chunk_4393ed9a076f7e200b63f80b74abf37e
- 移除原文：chunk_406249e1d98db3baa838606c7a974998, chunk_ac2dd6acd17189360638268b42945e7b
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 15 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_4393ed9a076f7e200b63f80b74abf37e
- 移除原文：chunk_406249e1d98db3baa838606c7a974998, chunk_ac2dd6acd17189360638268b42945e7b
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 15 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/52ca6e26-98e9-448f-8a2c-489687bdedc5?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/8982fb23-679b-4949-921a-c6d644341073?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/aad11e71-a1c8-4dcc-957f-05add44c193e?poll=true)

## R13

HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 是什么关系？引用两篇的设置说明，判断能否直接用结果数字比较两种检索方法。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | hippods, tog2ds | hippods, tog2ds | hippods, tog2ds |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_8cc831cc45851cce50b9f34648070765
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_8cc831cc45851cce50b9f34648070765
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

各组回答 Trace：[Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/bef7f064-a78f-421f-8bcc-864475919f74?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/dc921847-28a0-47af-b543-be858c56038c?poll=true)

## R18

比较 KG-GPT 与 RoG：句子分割、图检索、关系路径规划分别属于哪套流程？把输入到证据再到推理的顺序写清楚。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | kggpt, rog | kggpt, rog | kggpt, rog |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_07c5e4db08e2494c1b3712c0d378b9cd
- 移除原文：chunk_cfe612908773552496db582da6b6b26c
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_cfe612908773552496db582da6b6b26c
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/34b1d4b2-7bf7-44a2-b549-9f7c298f7c8b?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/e9304081-1a69-4c47-af2d-adbf130c12a4?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/11433de1-397a-487b-a9a4-f7f816a884ca?poll=true)

## R19

在 ToG、HippoRAG 与 RoG 中，分别找出“LLM 逐步探索图”“查询种子驱动图算法”“先规划关系路径再取证”的方法。每项给出一篇原文，并比较多跳关联发生在哪一步。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 1 | 1 | 1 |
| 路径字节 | 473 | 473 | 473 |
| 未覆盖事实 | tog, hippo, rog | tog, hippo, rog | tog, hippo, rog |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_853c2cdb088533bc71f93f42690919ae
- 移除原文：chunk_482ad8a6ae6b59dc872a9f742d9050ed
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 35 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_853c2cdb088533bc71f93f42690919ae
- 移除原文：chunk_482ad8a6ae6b59dc872a9f742d9050ed
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 35 条；已采用 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/f0c1b79b-5f4c-4c81-8547-f47072931c8a?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/4cab3456-2334-41f2-94a3-bc5783f7af70?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/acbf8de1-3a8b-4fac-b721-b8d0bf91175e?poll=true)

## R20

比较 ToG-2、HippoRAG 与 KGP 如何把文档中的分散信息联系起来。分别说明图与文档的连接方式，以及检索最终怎样回到支持证据。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 33.3% | 33.3% | 33.3% |
| 必要来源齐全 | 否 | 否 | 否 |
| 原文块数 | 4 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | hippo, kgp | hippo, kgp | hippo, kgp |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_44ca1868cc8294f6cfe2d5991cbd0d4b
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 38 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_44ca1868cc8294f6cfe2d5991cbd0d4b
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 38 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9b659f77-8a48-4544-bd45-69765aea7811?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/ef970629-4e87-4e20-9f82-cc7af98f9978?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/95dfb80a-df7a-4d35-8b7c-ad8997a42508?poll=true)

## R21

围绕“有限上下文或有限搜索预算下如何保留必要证据”，比较 G-Retriever、Tree-of-Traversals 与 CuriousLLM 的机制。哪些是子图选择，哪些是搜索边界，哪些是证据缺口信号？

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 4 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | grscale, totbound, curious | grscale, totbound, curious | grscale, totbound, curious |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_4b9f25dbcd34cf81a689e230345e1d86, chunk_ac2dd6acd17189360638268b42945e7b
- 移除原文：chunk_0cb3c2dcbacf18237a13b232366d2be8
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_ac2dd6acd17189360638268b42945e7b
- 移除原文：chunk_0cb3c2dcbacf18237a13b232366d2be8
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9c1a3b74-8b61-46e0-bf7b-18568e90e14a?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/bd681f2f-4c03-49a8-b3a8-ad4319809c81?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/188f0082-6797-45be-a89b-d138448f9cea?poll=true)

## R22

比较 LPKG、CuriousLLM 与 RoG 的训练信号和推理用途：图派生规划数据、问题与支持证据生成追问、KG 支持的关系路径分别属于谁？不能只回答三者都用了 KG。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 66.7% | 33.3% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | 无 | lpdata | lpdata, curious |
| 程序状态 | ok | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_0bd33867fd3e8c1883e6ad37bcb38ec6
- 移除原文：chunk_cea61ca4533fd32e6f63ea730fb194ab
- 丢失事实：lpdata：LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 4 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_0bd33867fd3e8c1883e6ad37bcb38ec6, chunk_e81a3933dd3c4e99786251f6dbc9b66a
- 移除原文：chunk_43145c0748762d6b4c650c65721f826f, chunk_cea61ca4533fd32e6f63ea730fb194ab
- 丢失事实：lpdata：LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。；curious：CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 4 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6ad41feb-a917-418c-b8b8-b9e0ad68445d?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/1518ddc9-87e2-420d-b963-f9ce16513d8f?poll=true)

## R23

ToG/ToG-R 的搜索宽度和深度怎样联系到 LLM 调用次数？再与 Tree-of-Traversals 的深度、扩展预算对照，说明为什么这些公式/上限不能直接换算成统一运行时排名。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 3 |
| 路径数 | 0 | 1 | 1 |
| 路径字节 | 0 | 445 | 445 |
| 未覆盖事实 | togr, totbound | togr, totbound | togr, totbound |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_ac2dd6acd17189360638268b42945e7b
- 移除原文：chunk_f99077c01e2b49914150ff933b0cf783
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：chunk_f99077c01e2b49914150ff933b0cf783
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d54f8b30-3622-4a06-a436-4d9a55cb8175?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/92553752-da97-4e6a-8d42-fca0eb96d423?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6c52a096-b526-47c2-9db9-c73618ffd546?poll=true)

## R24

结合 LPKG 的 CLQA-Wiki 与 Tree-of-Traversals 的 2Wiki/MusicBrainz-x-Wikidata 描述，区分“多跳”“交并逻辑”“跨 KG”三种任务关系，并逐项绑定到相应证据。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 66.7% | 100.0% | 66.7% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 3 | 4 |
| 路径数 | 0 | 1 | 0 |
| 路径字节 | 0 | 505 | 0 |
| 未覆盖事实 | totds | 无 | totds |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：chunk_a8ce6be635ba6abbbc71daeb86e809e9
- 移除原文：chunk_bc1cd12431f46892d2877dff73dab5e5, chunk_db3f4b0797f0910ec556e6c6930ef07b
- 丢失事实：无
- 新增事实：totds：Tree-of-Traversals 在 2WikiMultiHop、QALD-10 评估。
- 图路径去向：支持原文未入选，禁止发送路径 14 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：chunk_4b9f25dbcd34cf81a689e230345e1d86
- 移除原文：chunk_bc1cd12431f46892d2877dff73dab5e5
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 15 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/5f53f682-0a22-47bf-8985-cf39d7b8485e?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9a698224-5a25-4c0d-be44-4c6649d4293d?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b0de591a-9422-4591-bd79-6fecfbb15c3a?poll=true)

