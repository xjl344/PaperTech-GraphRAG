# 额外路径预算：答案语义审查

未观察到整体提升：三组均答出 11/18 个必要要点，完整覆盖全部必要要点均 1/4 题；R11 局部增、R23 局部退，R12/R13 核心持平。

仅实际增加路径改变输入的 R11/R12/R13/R23；4 题×3 组。其余 12 题未做此次语义审查，不得外推为 16 题准确率。

Codex AI；非盲审、非独立人工专家。事后诊断口径，不是新预注册基准成绩。按冻结题干/参考答案拆分 18 个必要要点，各要点 0/1；接受有来源的同义表述。要点数不等权于题数，不从程序 ok/partial 推断语义分数。

原文 6000 字节不变，额外路径预算 0/800/1200。使用已有回答，新模型调用为 0。

| 题号 | Path-0 | Path-800 | Path-1200 | 判读 |
|---|---:|---:|---:|---|
| R11 | 2/4 | 3/4 | 3/4 | 局部更完整：加路径两组补出 KG-GPT 跳数/指标，但仍漏 Freebase 的迁移训练角色，三组均未完整回答。 |
| R12 | 4/4 | 4/4 | 4/4 | 持平：基线已答出全部核心内容。partial→ok 是程序状态变化，不是语义知识提升；题干不要求 109 题，未提数量不扣分。 |
| R13 | 1/4 | 1/4 | 1/4 | 核心内容持平且缺失：三组均漏子集关系与两篇语料设置。800 组另有无依据的确定断言；1200 组不确定性措辞较稳。 |
| R23 | 4/6 | 3/6 | 3/6 | 局部退化：加路径两组省掉基线已解释的随机剪枝机制；三组都缺 Tree-of-Traversals 两种预算的具体停止行为。 |

三组各 11/18 要点；全部必要要点完整覆盖均为 1/4 题。该结果不是 16 题总体正确率。

R11 缺 Freebase 迁移原文，R13 缺子集/语料设置原文，R23 缺 Tree-of-Traversals 预算原文。新增路径主要是 EVALUATED_ON，另有 ToG-R→ToG 的 IMPROVES_UPON，未补齐这些缺口。

全 16 题的生成含引用校验 P95：6.090→6.656→7.288 秒；输入 Token：30630→31450→31872。多花预算后，当前证据未显示整体语义收益。

每组每题仅一次生成；所见一增一退不能单独证明路径因果或统计显著性。正确克制与完整回答分开记录。未发现额外问题不等于穷尽证明回答完全正确。

[原 16 题总览、柱状图、分类、Token 与完整详情](dashboard.html) · [语义审查网页](semantic-review.html) · [结构化逐项审查](semantic-review.json)

[LangSmith 三组对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/d48a738f-b627-424c-b8e4-8aca624510c1/compare?selectedSessions=0691329f-c143-40fd-b576-e425640e3143,b5f4897a-910d-401f-8e63-4e18b465f679,597afc3e-7394-40cc-a615-dc1c47f96b2b)

## R11

参考答案：KG-GPT 报告 MetaQA 各跳数 Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是预训练/迁移来源，扩展实验使用 1000 个训练样本。

局部更完整：加路径两组补出 KG-GPT 跳数/指标，但仍漏 Freebase 的迁移训练角色，三组均未完整回答。

### Path-0：2/4

程序状态 `partial` 仅作记录。

**完整回答**

RoG 原文说明 WebQSP 与 CWQ 的背景知识图是 Freebase，并给出规模“about 88 million entities, 20 thousand relations, and 126 million triples”[chunk_229cb41ae3582cc199c9ee25c4956269]；附录构造的 KG 统计表把 Freebase 单列为 2,566,291 个实体、7,058 个关系、8,309,195 条三元组，同时把 Wiki-Movie 单列为 43,234 个实体、9 个关系、133,582 条三元组，表中未逐字说明两者角色差异[chunk_297df214042add51d3facf35d1934a3d]。Wiki-Movies 的角色有原文直接说明：RoG 选取“based on Wiki-Movies KGs”的 MetaQA-3hop，并从训练集取 1000 个样本，用于“evaluate the transferability of RoG to other KGs”[chunk_297df214042add51d3facf35d1934a3d]。除该迁移评估用途外，未能从所给块中读出 Freebase 与 Wiki-Movies 在 RoG 流程中的其他分工；“跳数与指标”方面，所给块没有对 RoG 在这两种 KG 上按跳数报告指标的句子，流程证据不足。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| KG-GPT 的 MetaQA 1/2/3-hop 与 Hits@1 | 遗漏 | 未回答 | KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models p.4 `chunk_3f7eb65828761447433c66c28ad111a4` | chunk_3f7eb65828761447433c66c28ad111a4 |
| Wiki-Movies 是 MetaQA-3hop 的知识图谱 | 已回答 | based on Wiki-Movies KGs | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| RoG 扩展实验取 1000 个训练样本 | 已回答 | 从训练集取 1000 个样本 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| Freebase 是向 Wiki-Movies 迁移前的训练来源 | 遗漏 | 未回答 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.20 `chunk_f5c88d605f651f26c093f30b836a98aa` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/0691329f-c143-40fd-b576-e425640e3143/r/92c38cc0-8d79-5018-8acf-ac457c904a40)；reference_example_id `677f727e-3b2e-5d3b-b3f2-b6f48518d6bb`。

原生成 Trace：原记录未提供 URL；可由上述已同步的 Experiment 查看已有回答与 Token 子运行。

### Path-800：3/4

程序状态 `partial` 仅作记录。

**完整回答**

RoG 的实验中，Freebase 被描述为 WebQSP 和 CWQ 两个数据集的背景知识图（背景知识来源），原文称“Freebase (Bollacker et al., 2008) is the background knowledge graph for both datasets”[chunk_229cb41ae3582cc199c9ee25c4956269]。Wiki-Movies 则被描述为 MetaQA-3hop 数据集所基于的知识图，原文称“the MetaQA-3hop dataset (Zhang et al., 2018) which is based on Wiki-Movies KGs”[chunk_297df214042add51d3facf35d1934a3d]。关于沿“KG-GPT/RoG→MetaQA→跳数与指标/知识来源”的比较，现有证据不足以完成：KG-GPT 的 MetaQA 结果只列 1-hop、2-hop、3-hop 的 Hits@1，未说明其所用知识来源[chunk_3f7eb65828761447433c66c28ad111a4]；RoG 方面仅见 MetaQA-3hop 基于 Wiki-Movies 及 1000 个训练样本的说明，未见其 MetaQA 指标或完整评测流程[chunk_297df214042add51d3facf35d1934a3d]。因此两篇在知识来源与指标上的可比条件证据不足。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| KG-GPT 的 MetaQA 1/2/3-hop 与 Hits@1 | 已回答 | KG-GPT 的 MetaQA 结果只列 1-hop、2-hop、3-hop 的 Hits@1 | KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models p.4 `chunk_3f7eb65828761447433c66c28ad111a4` | chunk_3f7eb65828761447433c66c28ad111a4 |
| Wiki-Movies 是 MetaQA-3hop 的知识图谱 | 已回答 | MetaQA-3hop 数据集所基于的知识图 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| RoG 扩展实验取 1000 个训练样本 | 已回答 | 1000 个训练样本 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| Freebase 是向 Wiki-Movies 迁移前的训练来源 | 遗漏 | 未回答 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.20 `chunk_f5c88d605f651f26c093f30b836a98aa` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/b5f4897a-910d-401f-8e63-4e18b465f679/r/dbf0107a-2a76-5ac2-aac2-75521d45a6e4)；reference_example_id `677f727e-3b2e-5d3b-b3f2-b6f48518d6bb`。

原生成 Trace：原记录未提供 URL；可由上述已同步的 Experiment 查看已有回答与 Token 子运行。

### Path-1200：3/4

程序状态 `partial` 仅作记录。

**完整回答**

RoG 的 MetaQA-3hop 建立在 Wiki-Movies KG 上：原文称“We further select the MetaQA-3hop dataset (Zhang et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split”，即该数据集以 Wiki-Movies 为知识来源 [chunk_297df214042add51d3facf35d1934a3d]。Freebase 在 RoG 中是背景知识图：原文称 WebQSP 与 CWQ “contain up to 4-hop questions. Freebase ... is the background knowledge graph for both datasets” [chunk_229cb41ae3582cc199c9ee25c4956269]。关于 MetaQA 跳数与指标，KG-GPT 的表头为“MetaQA 1-hop/2-hop/3-hop”且指标为“Hits@1”，给出 8-shot 95.8/93.8/68.8 [chunk_3f7eb65828761447433c66c28ad111a4]；RoG 证据仅给出 MetaQA-3hop 的样本数与“#hop=3” [chunk_297df214042add51d3facf35d1934a3d]，其 MetaQA 指标与逐跳结果在同一证据中未提供。两篇在 MetaQA 上的底座模型、shot 设置与指标口径的可比性证据不足：KG-GPT 原文只称其为 few-shot 场景 [chunk_3f7eb65828761447433c66c28ad111a4]，RoG 对 MetaQA 实验设置的直接原文不足。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| KG-GPT 的 MetaQA 1/2/3-hop 与 Hits@1 | 已回答 | KG-GPT 的表头为“MetaQA 1-hop/2-hop/3-hop”且指标为“Hits@1” | KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models p.4 `chunk_3f7eb65828761447433c66c28ad111a4` | chunk_3f7eb65828761447433c66c28ad111a4 |
| Wiki-Movies 是 MetaQA-3hop 的知识图谱 | 已回答 | RoG 的 MetaQA-3hop 建立在 Wiki-Movies KG 上 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| RoG 扩展实验取 1000 个训练样本 | 已回答 | We select 1000 samples from the training split | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.17 `chunk_297df214042add51d3facf35d1934a3d` | chunk_297df214042add51d3facf35d1934a3d |
| Freebase 是向 Wiki-Movies 迁移前的训练来源 | 遗漏 | 未回答 | Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.20 `chunk_f5c88d605f651f26c093f30b836a98aa` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/597afc3e-7394-40cc-a615-dc1c47f96b2b/r/f18ae3dc-c9e3-5494-860f-411ee1684e68)；reference_example_id `677f727e-3b2e-5d3b-b3f2-b6f48518d6bb`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/779691aa-c50d-48fd-b7a1-7c2acf5bbea1?poll=true

### 参考原文与位置

**KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models p.4 · chunk_3f7eb65828761447433c66c28ad111a4**

Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf

```text
full
BERT
65.20
BlueBERT
59.93
zero-shot
Flan-T5
62.70
12-shot
ChatGPT
68.48
With Evidence
full
GEAR
77.65
12-shot
KG-GPT
72.68
8-shot
67.68
4-shot
59.53
Table 1: The performance of the models on FACTKG.
Except for ChatGPT and KG-GPT, all performances are
obtained from Kim et al. (2023).
Training
Methods
MetaQA
MetaQA
MetaQA
Strategy
1-hop
2-hop
3-hop
full
KV-Mem
96.2
82.7
48.9
GraftNet
97.0
94.8
77.7
EmbedKGQA
97.5
98.8
94.8
NSM
97.1
99.9
98.9
UniKGQA
97.5
99.0
99.1
12-shot
ChatGPT
60.0
23.0
38.7
12-shot
96.3
94.4
94.0
8-shot
KG-GPT
95.8
93.8
68.8
4-shot
94.7
92.8
46.6
Table 2: The performance of the models on MetaQA
(Hits@1). The best results for each task and those of
12-shot KG-GPT are in bold.
of the sentence segmentation and graph retrieval
stages. The qualitative results including the graphs
retrieved by KG-GPT are in Appendix E.1.
Nonetheless, when compared to GEAR, a fully
supervised model built upon KGs, KG-GPT ex-
hibits certain limitations. KG-GPT achieves an ac-
curacy score of 72.68%, which is behind GEAR’s
77.65%. This performance gap illustrates the ob-
stacles encountered by KG-GPT in a few-shot sce-
nario, namely the difficulty in amassing a suffi-
cient volume of information from the restricted
data available. Hence, despite the notable progress
achieved with KG-GPT, there is clear room for im-
provement to equal or surpass the performance of
KG-specific supervised models like GEAR.
4.2
MetaQA

```

**Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning p.20 · chunk_f5c88d605f651f26c093f30b836a98aa**

Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf

```text
A.7.1
TRANSFERABILITY TO OTHER KGS
We evaluate the transferability of RoG to other KGs. We select the MetaQA-3hop dataset (Zhang
et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split
and utilize two training strategies to finetune RoG: 1) training from scratch, where we directly train
RoG from LLaMA2-Chat with 1000 samples; 2) transfer from Freebase, where we conduct a further
finetuning based on RoG trained for Freebase. The results are shown in Table 12. From results, we
can see that transfer from Freebase achieves better performance than training from scratch, which
demonstrates the transferability of RoG to other KGs.
We also compare the training time on Freebase and transferring to Wiki-Movies KGs. From results
shown in Table 13, we can see that the training time on Freebase is 38 hours, while the transferring
time is only 2 hours. This demonstrates the efficiency of transferring RoG to other KGs.

```

## R12

参考答案：前者要求跨两个 KG 综合推理；后者从 Wikidata 子集构建，覆盖 multi-hop、comparison、intersection、union。

持平：基线已答出全部核心内容。partial→ok 是程序状态变化，不是语义知识提升；题干不要求 109 题，未提数量不扣分。

### Path-0：4/4

程序状态 `partial` 仅作记录。

**完整回答**

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 是为此前不存在的“综合多个 KG 信息回答单个问题”场景新建的数据集，包含109个需要同时用 MusicBrainz 与 Wikidata 信息推理的问题，由人工标注者按“在这两个KG之间找推理路径”的指示构造 [chunk_f4962498025654850621ee329d0af7d6]；该工作还主张其算法可用任意数量的KG增强LLM [chunk_ac2dd6acd17189360638268b42945e7b]。LPKG 的 CLQA-Wiki 则从 Wikidata 的一个子集构建，以“如上所述的丰富模式”接地 [chunk_ab66789d9bc91de68948962d6c3f0011]。能力考察上，CLQA-Wiki 均匀覆盖 multi-hop、comparison、intersection、union 四类问题，并被作者描述为现有复杂QA基准多聚焦多跳和比较、缺少逻辑操作 [chunk_ab66789d9bc91de68948962d6c3f0011]；MusicBrainz-x-Wikidata 的证据只说明问题需要同时使用两个KG的信息进行推理，未给出与CLQA-Wiki对应的题型分类描述 [chunk_f4962498025654850621ee329d0af7d6]。因此二者虽都涉及Wikidata，但原文对CLQA-Wiki有明确的四类题型覆盖面陈述，对MusicBrainz-x-Wikidata缺少同口径的题型分解，不能据此断言两者在具体关系推理类型上逐一对应或互有优劣；两数据集也未提供可比较的统一实验条件。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| MusicBrainz-x-Wikidata 连接 MusicBrainz 和 Wikidata | 已回答 | 同时用 MusicBrainz 与 Wikidata | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| 前者要求跨两个 KG 综合推理 | 已回答 | 综合多个 KG 信息回答单个问题 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| CLQA-Wiki 来自 Wikidata 子集 | 已回答 | 从 Wikidata 的一个子集构建 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |
| CLQA-Wiki 覆盖多跳、比较、交集、并集 | 已回答 | multi-hop、comparison、intersection、union 四类问题 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/0691329f-c143-40fd-b576-e425640e3143/r/5c9d338c-6681-52f9-b98e-615e60273fd1)；reference_example_id `2a56d042-4207-53d5-a39d-96d2febd9a2a`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/5fee2338-6e22-4522-81b0-c0e61cbd0ad4?poll=true

### Path-800：4/4

程序状态 `ok` 仅作记录。

**完整回答**

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 数据集要求同时使用 MusicBrainz 与 Wikidata 两个知识图谱的信息进行推理：原文称该数据集“containing 109 questions that require reasoning with information from both MusicBrainz and Wikidata”[chunk_f4962498025654850621ee329d0af7d6]，且 MusicBrainz 是深领域音乐数据库而 Wikidata 含通用知识[chunk_f4962498025654850621ee329d0af7d6]。LPKG 的 CLQA-Wiki 则从 Wikidata 的一个子集构建，原文称“we construct a Comprehensive Logical QA benchmark, CLQA-Wiki, from a subset of Wikidata”[chunk_ab66789d9bc91de68948962d6c3f0011]。关系推理能力区别：CLQA-Wiki 均匀覆盖多跳、比较、交集和并集类型问题，原文称“The CLQA-Wiki benchmark evenly covers multi-hop, comparison, intersection, and union types of questions”[chunk_ab66789d9bc91de68948962d6c3f0011]；MusicBrainz-x-Wikidata 侧重跨两个 KG 综合信息，原文称该数据集“requiring reasoning with information from both MusicBrainz and Wikidata”[chunk_f4962498025654850621ee329d0af7d6]，且是为测试多 KG 推理能力而创建[chunk_f4962498025654850621ee329d0af7d6]。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| MusicBrainz-x-Wikidata 连接 MusicBrainz 和 Wikidata | 已回答 | 同时使用 MusicBrainz 与 Wikidata | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| 前者要求跨两个 KG 综合推理 | 已回答 | 侧重跨两个 KG 综合信息 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| CLQA-Wiki 来自 Wikidata 子集 | 已回答 | 从 Wikidata 的一个子集构建 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |
| CLQA-Wiki 覆盖多跳、比较、交集、并集 | 已回答 | 多跳、比较、交集和并集类型问题 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/b5f4897a-910d-401f-8e63-4e18b465f679/r/22cfb2e5-5ad5-5c36-b99b-6bbb09d5726a)；reference_example_id `2a56d042-4207-53d5-a39d-96d2febd9a2a`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/9c22227c-2df2-4dc8-a85d-e4072f37a55b?poll=true

### Path-1200：4/4

程序状态 `ok` 仅作记录。

**完整回答**

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 是作者新建的数据集，要求同时使用 MusicBrainz 和 Wikidata 两个知识图谱的信息进行推理，用于测试多知识图谱推理能力 [chunk_f4962498025654850621ee329d0af7d6]；该数据集被用于评测 Tree-of-Traversals [chunk_406249e1d98db3baa838606c7a974998]。LPKG 的 CLQA-Wiki 是从 Wikidata 的一个子集构建的综合逻辑问答基准，覆盖多跳、比较、交集和并集类型问题 [chunk_ab66789d9bc91de68948962d6c3f0011]。区别在于：MusicBrainz-x-Wikidata 侧重跨两个知识图谱来源综合信息进行推理 [chunk_f4962498025654850621ee329d0af7d6]；CLQA-Wiki 侧重在 Wikidata 上考察多跳、比较、交集和并集等逻辑操作型复杂问答 [chunk_ab66789d9bc91de68948962d6c3f0011]。原文未给出两者在相同模型或协议下的可比结果，因此不能据此判断优劣。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| MusicBrainz-x-Wikidata 连接 MusicBrainz 和 Wikidata | 已回答 | 同时使用 MusicBrainz 和 Wikidata | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| 前者要求跨两个 KG 综合推理 | 已回答 | 侧重跨两个知识图谱来源综合信息 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 `chunk_f4962498025654850621ee329d0af7d6` | chunk_f4962498025654850621ee329d0af7d6 |
| CLQA-Wiki 来自 Wikidata 子集 | 已回答 | 从 Wikidata 的一个子集构建 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |
| CLQA-Wiki 覆盖多跳、比较、交集、并集 | 已回答 | 多跳、比较、交集和并集类型问题 | Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 `chunk_ab66789d9bc91de68948962d6c3f0011` | chunk_ab66789d9bc91de68948962d6c3f0011 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/597afc3e-7394-40cc-a615-dc1c47f96b2b/r/50e27a89-2a2b-5d7a-bc51-2222e97d56a6)；reference_example_id `2a56d042-4207-53d5-a39d-96d2febd9a2a`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/bce36f04-7a8c-4ff2-ace5-f78c4a50e91a?poll=true

### 参考原文与位置

**Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.5 · chunk_f4962498025654850621ee329d0af7d6**

Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf

```text
MusicBrainz-x-Wikidata Dataset One novel
use-case of Tree-of-Traversals is synthesizing and
reasoning over multiple knowledge graph sources.
There is no existing dataset that requires synthesiz-
ing information from multiple KGs to answer indi-
vidual questions. Therefore, to test the reasoning
ability using multiple KGs, we create a new dataset,
MusicBrainz-x-Wikidata, containing 109 questions
that require reasoning with information from both
MusicBrainz and Wikidata. Unlike Wikidata which
contains general knowledge, MusicBrainz is a deep
domain-specific database on the music industry.
The vast majority of this information is unlikely to
be known by large language models. We construct
the MusicBrainz-x-Wikidata dataset with human
annotators who were provided with instructions
to find reasoning paths between these two KGs,
the question types to focus on, and some example
questions. The curated questions were checked for
ambiguity and sensibility. By design, each question
4https://github.com/KGQA/QALD-10

2WikiMultiHop (↑)
Algorithm
Claude-Instant
Llama2-70b
Llama2-13b
Chain-of-Thought
25.2
30.4
26.8
ReAct
5.8
30.4
6.8
ReAct→CoT
27.0 (84.8%)
41.6 (41.6%)
23.6 (71.8%)
FLARe
35.0
45.4
34.8
Chain-of-Traversals
42.6
45.0
31.0
Tree-of-Traversals
63.0
56.6
37.3
QALD-10 (↑)
Algorithm
Claude-Instant
Llama2-70b
Llama2-13b

```

**Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs p.2 · chunk_ab66789d9bc91de68948962d6c3f0011**

Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf

```text
Additionally, we construct a Comprehensive
Logical QA benchmark, CLQA-Wiki, from a sub-
set of Wikidata (Vrandecic and Krötzsch, 2014) via
grounding rich patterns as aforementioned. Exist-
ing complex QA benchmarks (Yang et al., 2018; Ho
et al., 2020; Press et al., 2023; Trivedi et al., 2022)
primarily focus on multi-hop and comparison-type
questions and lack logical operations. Furthermore,
most questions are labeled with only one answer,
whereas in reality, they often have multiple correct
answers. The CLQA-Wiki benchmark evenly cov-
ers multi-hop, comparison, intersection, and union
types of questions, which is more comprehensive
and challenging for complex QA evaluation.
Our contributions can be summarized as follows:
(1) We introduce a novel framework LPKG that
enhances the planning ability of LLMs using data
constructed from KG patterns; (2) We develop a
comprehensive and challenging evaluation bench-
mark, named CLQA-Wiki, to more effectively as-
sess the performance of LLMs on complex QA
tasks; (3) Our proposed framework LPKG achieves
better results than popular baselines on multiple
conventional complex QA benchmarks, and we
verify the effectiveness of the introduction of KG-
sourced planning data.
2

```

## R13

参考答案：ToG-2 将 AdvHotpotQA 描述为 HotpotQA 的挑战子集；HippoRAG 抽取验证集并组成候选语料，ToG-2 使用 full Wiki，不能直接横比。

核心内容持平且缺失：三组均漏子集关系与两篇语料设置。800 组另有无依据的确定断言；1200 组不确定性措辞较稳。

### Path-0：1/4

程序状态 `partial` 仅作记录。

**完整回答**

证据不足：原文没有说明 HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 之间存在何种关系。HippoRAG 只说明在 HotpotQA 上与最强检索基线比较，并报告使用同一 QA reader 时 F1 的改进 [chunk_d374bd95d509d622be8512f20e59b674]；ToG-2 的结果表把 AdvHotpotQA 列为一个数据集，并在 GPT-3.5-turbo 条件下报告 EM [chunk_2e13f6f43858420cb85904c33d3b39df]。没有证据表明两者使用相同的数据划分、底座模型或指标（HippoRAG 使用 EM/F1 与 recall@k，ToG-2 表列为 EM），因此不能直接用结果数字比较两种检索方法；可比性所必需的条件在原文中缺失 [chunk_8cc831cc45851cce50b9f34648070765]。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| AdvHotpotQA 是 HotpotQA 的挑战子集 | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| HippoRAG 每个验证集取 1000 题并汇集支持/干扰段落 | 遗漏 | 未回答 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models p.5 `chunk_3fa28005a4df0de5249826585cf9d713` | 未提供；谨慎结论允许跨来源分析 |
| ToG-2 使用 full Wikipedia/Wikidata | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| 不直接用结果数字排名（只计谨慎结论，设置解释另计） | 已回答 | 不能直接用结果数字比较 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |

判分说明：只给不能直接比较这一结论分；必要设置另三项均未答出。


- 无依据/误导表述：“原文没有说明”。把本轮未检索到关系扩张为论文没有说明；冻结参考原文实际给出了挑战子集关系。

- 无依据/误导表述：“可比性所必需的条件在原文中缺失”。证据上下文不全不等于论文中没有实验设置。

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/0691329f-c143-40fd-b576-e425640e3143/r/e78f2793-0989-5a17-9ac7-a97458a7beee)；reference_example_id `0bddf756-87d9-5dd1-8711-02dce358bf1f`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/7c3e2272-4efb-4822-ab93-7c2de4a2baf4?poll=true

### Path-800：1/4

程序状态 `partial` 仅作记录。

**完整回答**

两条证据支持的共同点仅是数据集名称：HippoRAG 在含 HotpotQA 的数据集上评测，ToG-2 在 AdvHotpotQA 上评测，二者并非同一数据集，关系不明确。[chunk_8cc831cc45851cce50b9f34648070765] HippoRAG 使用 recall@2/recall@5 报告检索性能，并用 exact match 和 F1 报告 QA 性能；比较对象包括 BM25、Contriever、GTR、ColBERTv2 等检索方法和 IRCoT。[chunk_8cc831cc45851cce50b9f34648070765][chunk_d374bd95d509d622be8512f20e59b674] ToG-2 在 AdvHotpotQA 等数据集上使用 GPT-3.5-turbo，其表格以 EM 为单位。[chunk_2e13f6f43858420cb85904c33d3b39df] 这些说明显示：数据集不同（HotpotQA 与 AdvHotpotQA），检索指标与表格单位不同，底座模型设置不一致。因此，不能仅凭这些设置说明直接把 HippoRAG 的 HotpotQA 结果与 ToG-2 的 AdvHotpotQA 检索结果数字作比较；流程证据不足以判断可比性。[chunk_d374bd95d509d622be8512f20e59b674][chunk_2e13f6f43858420cb85904c33d3b39df]

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| AdvHotpotQA 是 HotpotQA 的挑战子集 | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| HippoRAG 每个验证集取 1000 题并汇集支持/干扰段落 | 遗漏 | 未回答 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models p.5 `chunk_3fa28005a4df0de5249826585cf9d713` | 未提供；谨慎结论允许跨来源分析 |
| ToG-2 使用 full Wikipedia/Wikidata | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| 不直接用结果数字排名（只计谨慎结论，设置解释另计） | 已回答 | 不能仅凭这些设置说明直接把 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |

判分说明：只给不能直接比较这一结论分；必要设置另三项均未答出。


- 无依据/误导表述：“底座模型设置不一致”。给定证据没有说明 HippoRAG 的底座，不能把未知断言为不一致。

- 无依据/误导表述：“AdvHotpotQA 检索结果数字”。ToG-2 表格 EM 是问答结果，不能当作检索指标。

- 无依据/误导表述：“二者并非同一数据集，关系不明确”。未识别挑战子集关系；所附 HippoRAG 单侧引用不能支持两者关系判断。

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/b5f4897a-910d-401f-8e63-4e18b465f679/r/e6d50dd4-ff79-5d99-bd03-99214e54871f)；reference_example_id `0bddf756-87d9-5dd1-8711-02dce358bf1f`。

原生成 Trace：原记录未提供 URL；可由上述已同步的 Experiment 查看已有回答与 Token 子运行。

### Path-1200：1/4

程序状态 `partial` 仅作记录。

**完整回答**

HippoRAG 在 HotpotQA 上报告了检索与 QA 结果 [chunk_8cc831cc45851cce50b9f34648070765]，其中提到 HippoRAG 在“less challenging HotpotQA dataset”上与基线表现相当 [chunk_8cc831cc45851cce50b9f34648070765]；其同段还说明 QA 使用 EM 与 F1 指标 [chunk_8cc831cc45851cce50b9f34648070765]。ToG-2 的 AdvHotpotQA 是其评测数据集之一，表 1 标注该列为 EM [chunk_2e13f6f43858420cb85904c33d3b39df]，且 ToG-2 在 AdvHotpotQA 上为 42.9% [chunk_2e13f6f43858420cb85904c33d3b39df]。但现有证据未说明 AdvHotpotQA 与 HotpotQA 的构造、数据划分或题目对应关系，也未给出两种方法在相同底座模型、相同检索/QA协议下的统一评测设置；因此不能仅凭结果数字直接比较两种检索方法。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| AdvHotpotQA 是 HotpotQA 的挑战子集 | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| HippoRAG 每个验证集取 1000 题并汇集支持/干扰段落 | 遗漏 | 未回答 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models p.5 `chunk_3fa28005a4df0de5249826585cf9d713` | 未提供；谨慎结论允许跨来源分析 |
| ToG-2 使用 full Wikipedia/Wikidata | 遗漏 | 未回答 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |
| 不直接用结果数字排名（只计谨慎结论，设置解释另计） | 已回答 | 不能仅凭结果数字直接比较 | Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 未提供；谨慎结论允许跨来源分析 |

判分说明：只给不能直接比较这一结论分；必要设置另三项均未答出。


[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/597afc3e-7394-40cc-a615-dc1c47f96b2b/r/b351dee8-69d5-5fb4-82d1-9d458803ec95)；reference_example_id `0bddf756-87d9-5dd1-8711-02dce358bf1f`。

原生成 Trace：原记录未提供 URL；可由上述已同步的 Experiment 查看已有回答与 Token 子运行。

### 参考原文与位置

**HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models p.5 · chunk_3fa28005a4df0de5249826585cf9d713**

Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf

```text
We evaluate our method’s retrieval capabilities primarily on two challenging multi-hop QA bench-
marks, MuSiQue (answerable) [77] and 2WikiMultiHopQA [33]. For completeness, we also
include the HotpotQA [89] dataset even though it has been found to be a much weaker test for
multi-hop reasoning due to many spurious signals [77], as we also show in Appendix B. To limit
the experimental cost, we extract 1,000 questions from each validation set as done in previous work
[63, 78]. In order to create a more realistic retrieval setting, we follow IRCoT [78] and collect all
candidate passages (including supporting and distractor passages) from our selected questions and
form a retrieval corpus for each dataset. The details of these datasets are shown in Table 1.
Table 1: Retrieval corpora and extracted KG statistics for each of our 1,000 question dev sets.
MuSiQue
2Wiki
HotpotQA
# of Passages (P)
11, 656
6, 119
9, 221
# of Unique Nodes (N)
91, 729
42, 694
82, 157
# of Unique Edges (E)
21, 714
7, 867
17, 523
# of Unique Triples
107, 448
50, 671
98, 709
# of Contriever Synonym Edges (E′)
145, 990
146, 020
159, 112
# of ColBERTv2 Synonym Edges (E′)
191, 636
82, 526
171, 856
3.2
Baselines

```

**Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval p.6 · chunk_16f86a00cebdf5e10d83c3a540fbc7f7**

Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf

```text
EXPERIMENTS
4.1
DATASETS AND METRICS
We evaluated our method on different knowledge-intensive reasoning benchmark datasets, including
two multi-hop KBQA datasets WebQSP (Yih et al., 2016) and QALD10-en (Usbeck et al., 2023), a
multi-hop complex document QA dataset AdvHotpotQA (Ye & Durrett, 2022) which is a challeng-
ing subset of HotpotQA (Yang et al., 2018), a slot filling dataset Zero-Shot RE(Petroni et al., 2021),
and two fact verification dataset FEVER (Thorne et al., 2018) and Creak (Onoe et al., 2021). The
evaluation metric for FEVER and Creak is Accuracy (Acc.), while the metric for other datasets is
Exact Match (EM). Recall and F1 scores are not used since knowledge sources are not limited to
document databases. Following previous work (Li et al., 2024c), full Wikipedia and Wikidata are
used as unstructured and structured knowledge sources for all of these datasets. Compared to the
distractor setting, this full Wiki setting makes the retrieval process more challenging and can better
evaluate the effectiveness of various methods on knowledge reasoning tasks.

```

## R23

参考答案：ToG-R 用随机实体剪枝减少调用，公式如原文；Tree-of-Traversals 有不同动作树搜索及预算。调用公式、搜索上限与墙钟时延不是同一量。

局部退化：加路径两组省掉基线已解释的随机剪枝机制；三组都缺 Tree-of-Traversals 两种预算的具体停止行为。

### Path-0：4/6

程序状态 `partial` 仅作记录。

**完整回答**

ToG 的搜索深度与宽度会提高性能，但计算代价随深度线性增加，因此默认将深度和宽度都设为3；当深度超过3后，性能增长会减弱 [chunk_8b9e861ea949a3eb2fc9ed5a97b24644]。ToG 的理论最大 LLM 调用次数为 2ND + D + 1，其中 N 是宽度、D 是深度；但原文指出，由于可能在达到最大深度前提前停止，多数情况下不会达到该上限 [chunk_f99077c01e2b49914150ff933b0cf783]。ToG-R 最多需要 ND + D + 1 次 LLM 调用，并使用随机束搜索（random beam search）代替 LLM 约束的束搜索 [chunk_aa272a627cf75d5bf907fe3a860356c4]。关于 Tree-of-Traversals 的深度和扩展预算如何与 LLM 调用次数对应，现有证据只有结论段，未描述这些参数或调用次数公式，因此这方面的流程证据不足，无法直接对照其深度、扩展预算与 ToG/ToG-R 的公式或上限 [chunk_4b9f25dbcd34cf81a689e230345e1d86]。同样，所给证据没有 Tree-of-Traversals 的实验设置、指标或运行时数据，无法据此换算成统一的运行时排名；不能把 ToG 的公式上限和默认深度/宽度当作跨算法的可比运行时指标 [chunk_8b9e861ea949a3eb2fc9ed5a97b24644][chunk_f99077c01e2b49914150ff933b0cf783][chunk_4b9f25dbcd34cf81a689e230345e1d86]。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| ToG 调用上界 2ND+D+1，并联系搜索宽度/深度 | 已回答 | 2ND + D + 1，其中 N 是宽度、D 是深度 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.22 `chunk_91a4a2e6943ad6a8074492d3f7229692` | chunk_f99077c01e2b49914150ff933b0cf783 |
| ToG-R 调用上界 ND+D+1 | 已回答 | ToG-R 最多需要 ND + D + 1 次 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |
| 以随机剪枝替代 LLM 剪枝解释调用减少 | 已回答 | 随机束搜索（random beam search）代替 LLM 约束的束搜索 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |

判分说明：基线表述为随机束搜索，接受其机制概括；未明确写出实体剪枝范围。

| Tree-of-Traversals max depth 强制进入 done | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| max expansions 达限后失败停止并返回 Cannot find answer | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| 调用上界不能直接换算墙钟时间或跨方法排名 | 已回答 | 不能把 ToG 的公式上限和默认深度/宽度当作跨算法的可比运行时指标 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/0691329f-c143-40fd-b576-e425640e3143/r/7b526de5-2428-50e2-be0e-78422068c277)；reference_example_id `a82a84f3-4084-5af7-a362-dc17268ec178`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/899a6b5a-8170-411f-85d4-4b2d2fd29406?poll=true

### Path-800：3/6

程序状态 `partial` 仅作记录。

**完整回答**

ToG 的搜索深度与宽度对性能及成本的影响在原文中有直接讨论：性能随搜索深度和宽度提升，但由于计算成本随深度线性增加，作者将深度和宽度默认都设为 3；当深度超过 3 后性能增长减弱 [chunk_8b9e861ea949a3eb2fc9ed5a97b24644]。ToG 的最大LLM调用次数由复杂度式给出：2ND+D+1 是最大计算复杂度，且在多数情况下会提前停止、并不需要达到该上限；当 N=3、D=3 时理论最大为 22 次，而四个多跳KBQA数据集的平均调用为 10 到 15 次 [chunk_f99077c01e2b49914150ff933b0cf783]。ToG-R 则“needs at most ND + D + 1 calls to the LLM”，同样多数情况下不需要这么多 [chunk_aa272a627cf75d5bf907fe3a860356c4][chunk_f99077c01e2b49914150ff933b0cf783]。对于 Tree-of-Traversals，所给证据只有结论段，称其为零样本、无模式依赖、无需训练的算法 [chunk_4b9f25dbcd34cf81a689e230345e1d86]；其中没有深度或扩展预算的具体定义、上界公式，也没有其LLM调用次数如何与深度/预算关联的方法描述，因此无法将ToG/ToG-R的调用上界与Tree-of-Traversals的深度、扩展预算作数值换算。也不能据此得到统一运行时排名：ToG/ToG-R的公式含随实际早停变化的“最大/至多”语义，原文明确指出多数情况低于上限 [chunk_f99077c01e2b49914150ff933b0cf783]，而Tree-of-Traversals的对应预算与调用关系证据不足 [chunk_4b9f25dbcd34cf81a689e230345e1d86]。这些公式/上限描述的是调用次数的理论边界而非可比运行时，加上Tree-of-Traversals缺项，无法统一换算为运行时排名。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| ToG 调用上界 2ND+D+1，并联系搜索宽度/深度 | 已回答 | 2ND+D+1 是最大计算复杂度 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.22 `chunk_91a4a2e6943ad6a8074492d3f7229692` | chunk_f99077c01e2b49914150ff933b0cf783 |
| ToG-R 调用上界 ND+D+1 | 已回答 | ToG-R 则“needs at most ND + D + 1 calls | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |
| 以随机剪枝替代 LLM 剪枝解释调用减少 | 遗漏 | 未回答 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |
| Tree-of-Traversals max depth 强制进入 done | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| max expansions 达限后失败停止并返回 Cannot find answer | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| 调用上界不能直接换算墙钟时间或跨方法排名 | 已回答 | 调用次数的理论边界而非可比运行时 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/b5f4897a-910d-401f-8e63-4e18b465f679/r/e966f645-6590-581c-b716-af131e58d00c)；reference_example_id `a82a84f3-4084-5af7-a362-dc17268ec178`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/3a45a4e9-0146-447a-8a4c-e1f0db7b8aa1?poll=true

### Path-1200：3/6

程序状态 `partial` 仅作记录。

**完整回答**

ToG 的搜索深度 D 与宽度 N 影响性能：原文称 ToG 性能随搜索深度和宽度提升，但计算成本随深度线性增长，因此默认把深度和宽度都设为 3 [chunk_8b9e861ea949a3eb2fc9ed5a97b24644]。ToG 的 LLM 调用次数上限：原文给出 2ND+D+1 是最大计算复杂度，并举例 N=3、D=3 时理论最大为 22 [chunk_f99077c01e2b49914150ff933b0cf783]。ToG-R 的调用次数上限：原文明确称 ToG-R 最多需要 ND+D+1 次 LLM 调用 [chunk_aa272a627cf75d5bf907fe3a860356c4]。两项上限都只是上界：ToG 在多数情况下不会达到 2ND+D+1 次调用，可能提前停止；ToG-R 在多数情况下也不需要 ND+D+1 次调用 [chunk_f99077c01e2b49914150ff933b0cf783]。关于 Tree-of-Traversals 的深度与扩展预算及对应公式：提供的证据中只有结论性概述，称其是零样本、不依赖 schema、无需训练的 KG 推理算法 [chunk_4b9f25dbcd34cf81a689e230345e1d86]，没有给出深度或扩展预算的公式或上限，因此这部分流程证据不足。上述 ToG/ToG-R 上限是 LLM 调用次数上界，其可达性还受提前停止影响 [chunk_f99077c01e2b49914150ff933b0cf783]；同时缺少 Tree-of-Traversals 的预算定义与调用次数证据 [chunk_4b9f25dbcd34cf81a689e230345e1d86]，不能把这些公式/上限直接换算成统一的运行时排名。

| 要点 | 判定 | 回答原句 | 参考来源 | 给模型的支持块 |
|---|---|---|---|---|
| ToG 调用上界 2ND+D+1，并联系搜索宽度/深度 | 已回答 | 2ND+D+1 是最大计算复杂度 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.22 `chunk_91a4a2e6943ad6a8074492d3f7229692` | chunk_f99077c01e2b49914150ff933b0cf783 |
| ToG-R 调用上界 ND+D+1 | 已回答 | ToG-R 最多需要 ND+D+1 次 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |
| 以随机剪枝替代 LLM 剪枝解释调用减少 | 遗漏 | 未回答 | Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.5 `chunk_aa272a627cf75d5bf907fe3a860356c4` | chunk_aa272a627cf75d5bf907fe3a860356c4 |
| Tree-of-Traversals max depth 强制进入 done | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| max expansions 达限后失败停止并返回 Cannot find answer | 遗漏 | 未回答 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |
| 调用上界不能直接换算墙钟时间或跨方法排名 | 已回答 | 不能把这些公式/上限直接换算成统一的运行时排名 | Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 `chunk_dac5f23e1b87249cf88eff5c6cc54355` | 未提供；谨慎结论允许跨来源分析 |

[本题 Experiment 运行记录](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/597afc3e-7394-40cc-a615-dc1c47f96b2b/r/709a9cff-515c-5826-bbb4-31a5fd36ece5)；reference_example_id `a82a84f3-4084-5af7-a362-dc17268ec178`。

原生成 Trace：https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b5643cbd-5fe5-41d3-8f3c-24ef8c96d558?poll=true

### 参考原文与位置

**Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph p.22 · chunk_91a4a2e6943ad6a8074492d3f7229692**

Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf

```text
cand,n. Consequently, it needs N LLM calls for entity pruning and N
calls for relation pruning, respectively, as well as one additional LLM call for reasoning (evaluating if
the information from the current candidate paths are enough or not). We have to point it out that, for
each of the N starting entities, all its neighbor entities/relations are NOT scored one by one. On the
contrary, all its neighbor entities/relations are "translated" into "one" prompt altogether and are sent to
LLM, which output the top-N candidates at one-time. Therefore, each starting entity only calls LLM
once for pruning and so N starting entities calls LLM N times in one iterative step. Consequently,
there are totally 2ND + D times calling after reasoning D steps. In the end, there is an additional
calling that "translate" the final path to user-understandable language and answer the user. Therefore,
ToG requires 2ND + D + 1 LLM calls in total. Since most questions can be answered within 3 hops
(means depth of reasoning path is 3), and the performance is usually good enough when the search
width N=3 as we tested in Figure 3, the total number of LLM calling is 2 × 3 × 3 + 3 + 1 = 22. So
the computational time is about 21 times longer than that of LLM-only. With a similar performance
to ToG, its variant ToG-R only calls LLM for ND + D + 1 times by using random entity pruning
instead of LLM-based entity pruning, saving nearly half of computational time.

```

**Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs p.4 · chunk_dac5f23e1b87249cf88eff5c6cc54355**

Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf

```text
building a search tree over the resulting reasoning
chains. We extend this approach to augment LLMs
with KGs through allowing the generation of ac-
tions in addition to thoughts, and building a search
tree over them. Challenges arise because Tree-of-
Thoughts was not designed to incorporate actions
and was not designed for knowledge intensive ques-
tion answering tasks. As a result, we introduce
some modifications: incorporation of actions via
the ASM, a slightly different search procedure and
stopping condition to better handle QA, and a dif-
ferent sampling procedure for improved diversity
when doing constrained sampling.
Algorithm 1 presents the Tree-of-Traversals tree
search algorithm. Given a query q it begins with
initialization using initialize(q) as described
in Section 2.1. After initialization, it searches by
(1) choosing the unexplored node to expand based
on the node’s value assigned by the value func-
tion (Best First→Depth First as tie-breaker), (2)
sampling k actions from the LLM (k is branching
factor) using the prompt associated with the se-
lected node’s state in the ASM, (3) for each of the
sampled action, applying the transition function,
and (4) evaluating the value of the resulting nodes
with the LLM value function. The search stops
when an answer is found with a node value exceed-
ing the threshold τ. To bound the search space
we add two hyper-parameters: max depth of the
tree search, after which the algorithm is forced to
transition to the done state (i.e., answer the query),
and max expansions after which the model halts
exploration and returns "Cannot find answer".

```

