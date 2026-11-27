# 16 题路径预算逐题归因

原文始终固定 6000 字节，额外增加路径预算；本表是程序证据归因，不是答案语义评分。

0 保持原文优先、路径使用剩余空间；800/1200 为额外路径预算。三组原文逐块相同，总上限为 6000/6800/7200。

[汇总报告](report.md) · [完整回答、原文及 Trace](dashboard.html)

## R03

结合 KGP 和 CuriousLLM 原文，后者针对前者提出了什么增强？把多文档图、遍历代理、后续问题及其监督信号串起来，并区分作者评价与已验证事实。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 50.0% | 50.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | kgp | kgp | kgp |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：原始快照无图路径

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：原始快照无图路径

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/a1e50362-00db-47fd-8e19-95197d970bff?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/c55ab896-5a80-4598-96ec-ea3a2d093387?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/f4f2802d-29dc-49dd-8bfb-9cda80cfdb63?poll=true)

## R04

比较 StructGPT 与 LPKG：一个方法在回答时如何获得证据，另一个方法在训练时如何获得规划数据？说明 KG/结构化数据在两者中的不同角色。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | struct, lpdata | struct, lpdata | struct, lpdata |
| 程序状态 | ok | ok | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 1 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d7c532f9-0522-4ff5-8783-d0d5647f2e4d?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/cde3bba8-f5b1-4e7a-aad7-d2a4794ec699?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/e4da888f-2911-4ba7-870a-68be5fa207f2?poll=true)

## R05

ToG 和 RoG 都利用 KG 推理，为什么不能据此把两者都归为免训练方法？分别追踪 KG 在在线搜索和训练中的作用。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 50.0% | 50.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | rog | rog | rog |
| 程序状态 | ok | ok | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 19 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 19 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/43929255-aaac-4855-b73f-96cf25807182?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/764f9a36-c7ac-46a8-9c44-19fe6911cfe5?poll=true)

## R06

比较 ToG-2 与 LPKG：图知识分别怎样帮助文档证据检索和问题规划？说明二者发生在训练还是推理阶段。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 100.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | 无 | 无 | 无 |
| 程序状态 | partial | partial | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 24 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 24 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6e74a108-d26a-4518-9087-471a3baf8b2b?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/a9e72523-ef95-4b1e-a299-13d6ae386a34?poll=true)

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

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 23 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 23 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/2edf573f-dcf6-4876-aa39-7ffdf4f8e13a?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/5110a4f2-a741-4c82-922d-5fc836eaf1a3?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d24751f0-c8a9-4cea-8c32-be893000624a?poll=true)

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
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 40 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/4f578948-eb26-4dc8-bf1e-0abfe8fa0075?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/589a2098-0efc-4a71-86ea-c6e84a913bb1?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/3eb8cee7-af92-4ebe-9792-f24d60b4447e?poll=true)

## R11

沿“KG-GPT/RoG→MetaQA→跳数与指标/知识来源”比较两篇实验。RoG 中 Freebase 与 Wiki-Movies 分别承担什么角色？每个角色须给出原文。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 50.0% | 50.0% | 50.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 1 | 2 |
| 路径字节 | 0 | 451 | 902 |
| 未覆盖事实 | rogmeta | rogmeta | rogmeta |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：已采用 1 条；支持原文未入选，禁止发送路径 5 条；配额不足或已达 4 条上限 2 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：已采用 2 条；支持原文未入选，禁止发送路径 5 条；配额不足或已达 4 条上限 1 条

各组回答 Trace：[Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/779691aa-c50d-48fd-b7a1-7c2acf5bbea1?poll=true)

## R12

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 与 LPKG 的 CLQA-Wiki 怎样分别连接到知识来源？虽然都涉及 Wikidata，二者考察的关系推理能力有何区别？

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 100.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 1 | 2 |
| 路径字节 | 0 | 509 | 997 |
| 未覆盖事实 | 无 | 无 | 无 |
| 程序状态 | partial | ok | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 10 条；已采用 1 条；配额不足或已达 4 条上限 4 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 10 条；已采用 2 条；配额不足或已达 4 条上限 3 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/5fee2338-6e22-4522-81b0-c0e61cbd0ad4?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9c22227c-2df2-4dc8-a85d-e4072f37a55b?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/bce36f04-7a8c-4ff2-ace5-f78c4a50e91a?poll=true)

## R13

HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 是什么关系？引用两篇的设置说明，判断能否直接用结果数字比较两种检索方法。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 1 | 1 |
| 路径字节 | 0 | 459 | 459 |
| 未覆盖事实 | hippods, tog2ds | hippods, tog2ds | hippods, tog2ds |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7c3e2272-4efb-4822-ab93-7c2de4a2baf4?poll=true)

## R18

比较 KG-GPT 与 RoG：句子分割、图检索、关系路径规划分别属于哪套流程？把输入到证据再到推理的顺序写清楚。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | kggpt, rog | kggpt, rog | kggpt, rog |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7d4d849c-47dc-4f91-9208-9daed275e9e8?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/8c61c345-9488-474f-a390-8585173498f6?poll=true)

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

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 35 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 35 条；已采用 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7d345d1e-b646-425a-a363-78e5e18ca15b?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/27640755-02e2-4460-b9a7-c76bd3a985d3?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/07367806-c879-4cb9-8882-b0af640fced4?poll=true)

## R20

比较 ToG-2、HippoRAG 与 KGP 如何把文档中的分散信息联系起来。分别说明图与文档的连接方式，以及检索最终怎样回到支持证据。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 33.3% | 33.3% | 33.3% |
| 必要来源齐全 | 否 | 否 | 否 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | hippo, kgp | hippo, kgp | hippo, kgp |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 38 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 38 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/fb2244bc-5977-4e66-9446-e5c2bc3063b7?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/ad93e636-94ce-44d9-bc23-8b586c93afb5?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/8da33082-1bad-4fa3-b16a-652ff9c968bf?poll=true)

## R21

围绕“有限上下文或有限搜索预算下如何保留必要证据”，比较 G-Retriever、Tree-of-Traversals 与 CuriousLLM 的机制。哪些是子图选择，哪些是搜索边界，哪些是证据缺口信号？

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | grscale, totbound, curious | grscale, totbound, curious | grscale, totbound, curious |
| 程序状态 | partial | partial | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 6 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/83c9a16f-6bc1-4541-a350-c520125bf9ed?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/502cf14f-c864-42ec-aa9a-7e1c097920d2?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/f11e5aa1-7abb-4b4c-9b52-af0aeaf672d3?poll=true)

## R22

比较 LPKG、CuriousLLM 与 RoG 的训练信号和推理用途：图派生规划数据、问题与支持证据生成追问、KG 支持的关系路径分别属于谁？不能只回答三者都用了 KG。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 100.0% | 100.0% | 100.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 3 | 3 | 3 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | 无 | 无 | 无 |
| 程序状态 | ok | ok | ok |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 4 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 4 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b2a52a6f-95b6-4a51-8214-e3df066d910a?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/f29c7086-403c-4b68-8657-b8d3f21187d6?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/0f0bf94f-b123-4dba-ab67-7ae367280bc4?poll=true)

## R23

ToG/ToG-R 的搜索宽度和深度怎样联系到 LLM 调用次数？再与 Tree-of-Traversals 的深度、扩展预算对照，说明为什么这些公式/上限不能直接换算成统一运行时排名。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 0.0% | 0.0% | 0.0% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 1 | 1 |
| 路径字节 | 0 | 445 | 445 |
| 未覆盖事实 | togr, totbound | togr, totbound | togr, totbound |
| 程序状态 | partial | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 39 条；已采用 1 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/899a6b5a-8170-411f-85d4-4b2d2fd29406?poll=true) · [Path-800](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/3a45a4e9-0146-447a-8a4c-e1f0db7b8aa1?poll=true) · [Path-1200](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b5643cbd-5fe5-41d3-8f3c-24ef8c96d558?poll=true)

## R24

结合 LPKG 的 CLQA-Wiki 与 Tree-of-Traversals 的 2Wiki/MusicBrainz-x-Wikidata 描述，区分“多跳”“交并逻辑”“跨 KG”三种任务关系，并逐项绑定到相应证据。

| 项目 | Path-0 | Path-800 | Path-1200 |
|---|---|---|---|
| 冻结事实覆盖 | 66.7% | 66.7% | 66.7% |
| 必要来源齐全 | 是 | 是 | 是 |
| 原文块数 | 4 | 4 | 4 |
| 路径数 | 0 | 0 | 0 |
| 路径字节 | 0 | 0 | 0 |
| 未覆盖事实 | totds | totds | totds |
| 程序状态 | citation_error | partial | partial |

**Path-800 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 15 条

**Path-1200 相对 Path-0：**

- 新增原文：无
- 移除原文：无
- 丢失事实：无
- 新增事实：无
- 图路径去向：支持原文未入选，禁止发送路径 15 条

各组回答 Trace：[Path-0](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/90194a23-4a5b-45d1-b28c-fb014e3a3a87?poll=true)

