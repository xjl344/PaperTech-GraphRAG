# 逐题协议与来源诊断

以下检查重读已保存的输出，没有重新调用模型。引用通过只表示协议有效；来源齐全也不代表结论都受原文支持。

| 题目 | 组别 | 程序状态 | 引用协议 | 原题所需论文均入选 | 缺少来源论文数 |
|---|---|---|---|---|---:|
| F01 | Hybrid | evidence_only | not_generated | True | 0 |
| F01 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| F02 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| F02 | Hybrid | evidence_only | not_generated | True | 0 |
| F03 | Hybrid | evidence_only | not_generated | True | 0 |
| F03 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| F04 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| F04 | Hybrid | evidence_only | not_generated | True | 0 |
| P01 | Hybrid | evidence_only | not_generated | True | 0 |
| P01 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| P02 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| P02 | Hybrid | evidence_only | not_generated | True | 0 |
| P03 | Hybrid | evidence_only | not_generated | True | 0 |
| P03 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| P04 | Hybrid+Graph | evidence_only | not_generated | True | 0 |
| P04 | Hybrid | evidence_only | not_generated | True | 0 |
| R01 | Hybrid | partial | passed | True | 0 |
| R01 | Hybrid+Graph | partial | passed | True | 0 |
| R02 | Hybrid+Graph | partial | passed | True | 0 |
| R02 | Hybrid | partial | passed | True | 0 |
| R03 | Hybrid | ok | passed | False | 1 |
| R03 | Hybrid+Graph | ok | passed | False | 1 |
| R04 | Hybrid+Graph | partial | passed | False | 1 |
| R04 | Hybrid | partial | passed | False | 1 |
| R05 | Hybrid | citation_error | failed | True | 0 |
| R05 | Hybrid+Graph | partial | passed | False | 1 |
| R06 | Hybrid+Graph | partial | passed | False | 1 |
| R06 | Hybrid | partial | passed | False | 1 |
| R07 | Hybrid | ok | passed | True | 0 |
| R07 | Hybrid+Graph | citation_error | failed | True | 0 |
| R08 | Hybrid+Graph | citation_error | failed | False | 1 |
| R08 | Hybrid | partial | passed | False | 1 |
| R09 | Hybrid | partial | passed | True | 0 |
| R09 | Hybrid+Graph | partial | passed | False | 1 |
| R10 | Hybrid+Graph | citation_error | failed | True | 0 |
| R10 | Hybrid | partial | passed | False | 1 |
| R11 | Hybrid | partial | passed | False | 1 |
| R11 | Hybrid+Graph | partial | passed | False | 1 |
| R12 | Hybrid+Graph | partial | passed | False | 1 |
| R12 | Hybrid | partial | passed | False | 1 |
| R13 | Hybrid | partial | passed | False | 1 |
| R13 | Hybrid+Graph | partial | passed | False | 1 |
| R14 | Hybrid+Graph | partial | passed | True | 0 |
| R14 | Hybrid | partial | passed | True | 0 |
| R15 | Hybrid | partial | passed | True | 0 |
| R15 | Hybrid+Graph | partial | passed | True | 0 |
| R16 | Hybrid+Graph | partial | passed | True | 0 |
| R16 | Hybrid | partial | passed | True | 0 |
| R17 | Hybrid | partial | passed | True | 0 |
| R17 | Hybrid+Graph | partial | passed | True | 0 |
| R18 | Hybrid+Graph | partial | passed | False | 1 |
| R18 | Hybrid | citation_error | failed | False | 1 |
| R19 | Hybrid | citation_error | failed | False | 1 |
| R19 | Hybrid+Graph | partial | passed | False | 2 |
| R20 | Hybrid+Graph | partial | passed | False | 2 |
| R20 | Hybrid | partial | passed | False | 2 |
| R21 | Hybrid | partial | passed | False | 1 |
| R21 | Hybrid+Graph | partial | passed | False | 1 |
| R22 | Hybrid+Graph | partial | passed | False | 1 |
| R22 | Hybrid | partial | passed | False | 1 |
| R23 | Hybrid | partial | passed | False | 1 |
| R23 | Hybrid+Graph | partial | passed | False | 1 |
| R24 | Hybrid+Graph | partial | passed | False | 1 |
| R24 | Hybrid | partial | passed | False | 1 |
| N01 | Hybrid | partial | passed | True | 0 |
| N01 | Hybrid+Graph | partial | passed | True | 0 |
| N02 | Hybrid+Graph | ok | passed | False | 1 |
| N02 | Hybrid | ok | passed | False | 1 |
| N03 | Hybrid | partial | passed | True | 0 |
| N03 | Hybrid+Graph | partial | passed | True | 0 |
| N04 | Hybrid+Graph | partial | passed | False | 1 |
| N04 | Hybrid | citation_error | failed | True | 0 |
| N05 | Hybrid | partial | passed | True | 0 |
| N05 | Hybrid+Graph | ok | passed | True | 0 |
| N06 | Hybrid+Graph | refused | passed | True | 0 |
| N06 | Hybrid | refused | passed | True | 0 |
| N07 | Hybrid | partial | passed | False | 1 |
| N07 | Hybrid+Graph | ok | passed | False | 1 |
| N08 | Hybrid+Graph | ok | passed | True | 0 |
| N08 | Hybrid | ok | passed | True | 0 |

## 引用失败细节

### R05 / Hybrid

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "q1",
    "q2"
  ],
  "declared_but_not_inline": [
    "chunk_229cb41ae3582cc199c9ee25c4956269",
    "chunk_270d9350248b566ed224ba5147a295a2",
    "chunk_e09b5a88c34014513aad6c0d6121f790"
  ],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

ToG 被明确描述为免训练方法：其框架无需额外训练成本[q2]，且原文称“ToG is a training-free prompting-based method”[q2]。就 KG 的在线搜索作用而言，ToG 将 LLM 视为代理，在 KG 上交互式探索相关实体和关系，并基于检索到的知识进行推理[q1]；LLM 代理迭代地在 KG 上执行 beam search，发现最有希望的推理路径[q1]。RoG 在所提供的证据中缺少对其训练过程或 KG 在训练中作用的直接描述，现有片段仅说明评估数据集和 Freebase 背景知识图[q1]，以及提及规划模块可与其他 LLM 集成[q1]，但未给出训练流程证据，因此无法仅凭这些证据追踪 RoG 中 KG 在训练中的作用。

### R07 / Hybrid+Graph

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "30"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

HippoRAG 的图由 LLM 将语料转换为无模式知识图（schemaless knowledge graph）来构造：“using an LLM to transform a corpus into a schemaless knowledge graph (KG) as our artificial hippocampal index”[chunk_a58244558a2137d85a4b8e53d5c4ebaf]。KGP 则在给定文档上构造图，节点表示段落或文档结构，边表示段落间的词汇/语义相似性或文档内结构关系：“construct a KG over the given documents with nodes symbolizing passages or document structures and edges denoting their lexical/semantic similarity between passages or intra-document structural relations”[chunk_4c2f9284ed69432f1dd6ad5217a9a783]。检索时，HippoRAG 识别查询关键概念作种子，在 KG 上运行 Personalized PageRank 沿图路径探索子图：“runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query concepts as the seeds... PPR enables HippoRAG to explore KG paths and identify relevant subgraphs”[chunk_a58244558a2137d85a4b8e53d5c4ebaf]。KGP 则用 LLM 图遍历代理交替生成下一步证据并选择邻居访问：“an LLM-based KG traversal agent, which can alternatively generate the next evidence... and select the most promising neighbor to visit from the constructed KG”[chunk_4c2f9284ed69432f1dd6ad5217a9a783]。因此 KGP 的节点明确可对应段落，而 HippoRAG 的 KG 是作为“人工海马索引”的无模式图、检索沿概念种子经 PPR 展开，不把“节点就是段落”作为其图构造与检索定义；二者不能直接共享同一种节点解释，因为节点含义与遍历机制在原文中描述不同 [chunk_a58244558a2137d85a4b8e53d5c4ebaf][chunk_4c2f9284ed69432f1dd6ad5217a9a783]。

### R08 / Hybrid+Graph

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [],
  "declared_but_not_inline": [],
  "unknown_chunk_references": [
    "chunk_9b63637ef18ed2b67ff105ef55092df3"
  ]
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

在证据中，ToG-2 的机制有直接描述：它从问题中抽取主题实体作为图搜索起点，每轮在 KG 上做关系检索扩展候选实体，并检索这些候选实体关联文档中的相关文本 [chunk_fd05fc6099086f633f4ad41747c6caac]；随后依据上下文检索结果剪枝候选实体、更新主题实体集并作为下一轮起点 [chunk_fd05fc6099086f633f4ad41747c6caac]。其整体定位是紧耦合的 KG×Text 混合 RAG，用 KG 通过实体连接文档以引导深度上下文检索，同时把文档作为实体上下文以实现精确图检索 [chunk_9b63637ef18ed2b67ff105ef55092df3]；检索在图检索与上下文检索之间交替进行 [chunk_9b63637ef18ed2b67ff105ef55092df3]。关于输入规模问题，所给证据没有专门表述 ToG-2 如何处理输入规模，流程证据不足。关于 G-Retriever 的机制（包括其如何选择相关子图、如何处理输入规模、实体与文档如何协作），所给证据完全未提及，因此无法与 ToG-2 做机制层面的对比；这不是推断其不存在，而是证据缺口。

### R10 / Hybrid+Graph

```json
{
  "status": "failed",
  "reason": "generated_schema_validation_failed",
  "error_type": "ValidationError",
  "undeclared_inline_references": [
    "chunk_406249e1d98db3baa838606c7a974998",
    "chunk_b1e16d1c0cce0b7a5286e2e0f30b9821"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

两篇原文对 2Wiki 数据集的命名不同：HippoRAG 原文称其为“2WikiMultiHopQA”，并说明它是主要数据集之一 [chunk_b1e16d1c0cce0b7a5286e2e0f30b9821]；Tree-of-Traversals 原文在结果表中称其为“2WikiMultiHop”，并称在该数据集上取得零样本设定下的 state-of-the-art 结果 [chunk_406249e1d98db3baa838606c7a974998]。因此可按各自原文名称“2WikiMultiHopQA”和“2WikiMultiHop”关联到同一 2Wiki 测试集，但保留名称差异。

HippoRAG 的跨事实检索流程证据不足：原文只报告了检索与 QA 结果，并称 HippoRAG 在 MuSiQue 和 2WikiMultiHopQA 上优于其他方法 [chunk_b1e16d1c0cce0b7a5286e2e0f30b9821]，但所给引句未描述其如何完成跨事实检索。Tree-of-Traversals 的跨事实检索流程有直接描述：它通过所提出的 KG interface 访问知识库，并由 ASM 引导 thought-action procedure 进行树遍历，包括 multiple thoughts/actions、backtracking 和 node value computation [chunk_406249e1d98db3baa838606c7a974998]。

设置差异方面，Tree-of-Traversals 明确是 zero-shot setting，并与其他基线在 2WikiMultiHop 上比较 [chunk_406249e1d98db3baa838606c7a974998]；HippoRAG 原文所述为检索与 QA 实验，报告其最佳检索 backbone 为 ColBERTv2，并给出单步与多步检索结果 [chunk_b1e16d1c0cce0b7a5286e2e0f30b9821]，但所给证据未说明 HippoRAG 在 2Wiki 上是否为 zero-shot，也未给出与 Tree-of-Traversals 可比的数据划分或统一协议。因此不能据现有原文判断两者在 2Wiki 上的公平胜负。

### R18 / Hybrid

```json
{
  "status": "failed",
  "reason": "generated_schema_validation_failed",
  "error_type": "ValidationError",
  "undeclared_inline_references": [
    "chunk_45c598ca774c47ab2be0c3b734efd4de",
    "chunk_e702747b8cb7850698f65ab65a3d7d8c"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

KG-GPT 的三阶段流程由原文明确给出：其框架“is composed of three stages: Sentence Segmentation, Graph Retrieval, and Inference”[chunk_e702747b8cb7850698f65ab65a3d7d8c]，其中“Sentence Segmentation...breaking down sentences”、“Graph Retrieval...sourcing related graph elements”、“Inference...reaching reasoned outcomes”[chunk_45c598ca774c47ab2be0c3b734efd4de]。在输入到证据再到推理的顺序上，KG-GPT 假定给定图 G 与句子 S，并指出“In order to derive a logical conclusion, we need an accurate evidence graph GE⊂G, which we obtain in two stages, Sentence Segmentation and Graph Retrieval”[chunk_e702747b8cb7850698f65ab65a3d7d8c]，即先分段、再检索得到证据图，最后进入推理阶段。关于“关系路径规划”，给定证据中没有出现该术语或对应模块，无法与 KG-GPT 的任一阶段对应。关于 RoG，给定证据未提供其方法描述，因此其是否包含句子分割、图检索或关系路径规划，流程证据不足，无法比较。

### R19 / Hybrid

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "chunk_id缺失"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

ToG 原文显示其以 LLM 逐步探索图：搜索从每轮（深度）的中心实体开始，由 LLM 对边打分并剪枝低分关系，再依据前 N 条推理路径由 LLM 判断作答或达到最大搜索深度，因此多跳关联在迭代的实体扩展与路径推理步骤中形成 [chunk_b160799030dcc4aeb6145d3dd00db7f3]。HippoRAG 的材料将多跳关联归于检索语料中跨段落信息的整合，并把标准多跳问答描述为需要整合段落信息；但所给引句未描述“查询种子驱动图算法”的具体流程，因此该方法的流程证据不足，无法据引句说明多跳关联发生在哪一步 [chunk_d32e1706909cc088dae124d6b0f3893c]。RoG 在所给证据中没有任何原文片段，无法给出其方法与多跳关联步骤，方法证据不足 [chunk_id缺失]。

### N04 / Hybrid

```json
{
  "status": "failed",
  "reason": "Unknown quotation choice",
  "error_type": "ValueError",
  "undeclared_inline_references": [],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

不能推出。就 RoG 而言，其 MetaQA-3hop 实验使用的是基于 Wiki-Movies KGs 的数据集：“We select the MetaQA-3hop dataset (Zhang et al., 2018) which is based on Wiki-Movies KGs” [chunk_f5c88d605f651f26c093f30b836a98aa]。RoG 文中的“transfer from Freebase”指的是先在 Freebase 上训练，再用训练所得模型在 Wiki-Movies KGs 上继续微调，并非把 MetaQA 的测试 KG 设为 Freebase [chunk_f5c88d605f651f26c093f30b836a98aa]。至于 KG-GPT 的 MetaQA 实验，所提供证据仅有示例图的说明，未描述测试 KG，故其流程证据不足 [chunk_bfa2a30300802f424fbbabe46b4f6157]。
