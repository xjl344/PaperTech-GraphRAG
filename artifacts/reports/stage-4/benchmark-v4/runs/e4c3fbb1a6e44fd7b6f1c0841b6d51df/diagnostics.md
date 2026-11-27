# 逐题协议与来源诊断

以下检查重读已保存的输出，没有重新调用模型。引用通过只表示协议有效；来源齐全也不代表结论都受原文支持。

| 题目 | 组别 | 程序状态 | 引用协议 | 原题所需论文均入选 | 缺少来源论文数 |
|---|---|---|---|---|---:|
| F01 | Hybrid | ok | passed | True | 0 |
| F01 | Hybrid+Graph | ok | passed | True | 0 |
| F02 | Hybrid+Graph | ok | passed | True | 0 |
| F02 | Hybrid | ok | passed | True | 0 |
| F03 | Hybrid | ok | passed | True | 0 |
| F03 | Hybrid+Graph | ok | passed | True | 0 |
| F04 | Hybrid+Graph | ok | passed | True | 0 |
| F04 | Hybrid | ok | passed | True | 0 |
| F05 | Hybrid | ok | passed | True | 0 |
| F05 | Hybrid+Graph | ok | passed | True | 0 |
| F06 | Hybrid+Graph | ok | passed | True | 0 |
| F06 | Hybrid | ok | passed | True | 0 |
| F07 | Hybrid | ok | passed | True | 0 |
| F07 | Hybrid+Graph | ok | passed | True | 0 |
| F08 | Hybrid+Graph | ok | passed | True | 0 |
| F08 | Hybrid | ok | passed | True | 0 |
| R01 | Hybrid | partial | passed | True | 0 |
| R01 | Hybrid+Graph | ok | passed | True | 0 |
| R02 | Hybrid+Graph | partial | passed | True | 0 |
| R02 | Hybrid | citation_error | failed | True | 0 |
| R03 | Hybrid | ok | passed | True | 0 |
| R03 | Hybrid+Graph | ok | passed | True | 0 |
| R04 | Hybrid+Graph | ok | passed | True | 0 |
| R04 | Hybrid | ok | passed | True | 0 |
| R05 | Hybrid | ok | passed | True | 0 |
| R05 | Hybrid+Graph | ok | passed | True | 0 |
| R06 | Hybrid+Graph | partial | passed | True | 0 |
| R06 | Hybrid | ok | passed | True | 0 |
| R07 | Hybrid | partial | passed | True | 0 |
| R07 | Hybrid+Graph | partial | passed | True | 0 |
| R08 | Hybrid+Graph | partial | passed | True | 0 |
| R08 | Hybrid | partial | passed | True | 0 |
| R09 | Hybrid | partial | passed | True | 0 |
| R09 | Hybrid+Graph | partial | passed | True | 0 |
| R10 | Hybrid+Graph | partial | passed | True | 0 |
| R10 | Hybrid | partial | passed | True | 0 |
| R11 | Hybrid | partial | passed | True | 0 |
| R11 | Hybrid+Graph | partial | passed | True | 0 |
| R12 | Hybrid+Graph | ok | passed | True | 0 |
| R12 | Hybrid | ok | passed | True | 0 |
| R13 | Hybrid | partial | passed | True | 0 |
| R13 | Hybrid+Graph | partial | passed | True | 0 |
| R14 | Hybrid+Graph | partial | passed | True | 0 |
| R14 | Hybrid | partial | passed | True | 0 |
| R15 | Hybrid | ok | passed | True | 0 |
| R15 | Hybrid+Graph | ok | passed | True | 0 |
| R16 | Hybrid+Graph | partial | passed | True | 0 |
| R16 | Hybrid | partial | passed | True | 0 |
| R17 | Hybrid | partial | passed | True | 0 |
| R17 | Hybrid+Graph | partial | passed | True | 0 |
| R18 | Hybrid+Graph | partial | passed | True | 0 |
| R18 | Hybrid | partial | passed | True | 0 |
| R19 | Hybrid | partial | passed | True | 0 |
| R19 | Hybrid+Graph | partial | passed | True | 0 |
| R20 | Hybrid+Graph | partial | passed | True | 0 |
| R20 | Hybrid | partial | passed | True | 0 |
| R21 | Hybrid | partial | passed | True | 0 |
| R21 | Hybrid+Graph | partial | passed | True | 0 |
| R22 | Hybrid+Graph | ok | passed | True | 0 |
| R22 | Hybrid | ok | passed | True | 0 |
| R23 | Hybrid | citation_error | failed | True | 0 |
| R23 | Hybrid+Graph | partial | passed | True | 0 |
| R24 | Hybrid+Graph | citation_error | failed | True | 0 |
| R24 | Hybrid | citation_error | failed | True | 0 |
| N01 | Hybrid | partial | passed | True | 0 |
| N01 | Hybrid+Graph | partial | passed | True | 0 |
| N02 | Hybrid+Graph | partial | passed | True | 0 |
| N02 | Hybrid | partial | passed | True | 0 |
| N03 | Hybrid | partial | passed | True | 0 |
| N03 | Hybrid+Graph | citation_error | failed | True | 0 |
| N04 | Hybrid+Graph | partial | passed | True | 0 |
| N04 | Hybrid | partial | passed | True | 0 |
| N05 | Hybrid | partial | passed | True | 0 |
| N05 | Hybrid+Graph | partial | passed | True | 0 |
| N06 | Hybrid+Graph | partial | passed | True | 0 |
| N06 | Hybrid | refused | passed | True | 0 |
| N07 | Hybrid | ok | passed | True | 0 |
| N07 | Hybrid+Graph | ok | passed | True | 0 |
| N08 | Hybrid+Graph | partial | passed | True | 0 |
| N08 | Hybrid | ok | passed | True | 0 |

## 引用失败细节

### R02 / Hybrid

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

HippoRAG 一侧：原文明确写道“Given a new query, HippoRAG identifies the key concepts in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query concepts as the seeds, to integrate information across passages for retrieval”，即查询种子是问题中的关键概念，PPR 以这些概念为种子在知识图谱上运行以实现跨段落检索 [chunk_a58244558a2137d85a4b8e53d5c4ebaf]。同段还称“PPR enables HippoRAG to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a single retrieval step”，说明它通过 PPR 探索图路径而非显式生成关系路径 [chunk_a58244558a2137d85a4b8e53d5c4ebaf]。关于路径发现类多跳问题，原文称“HippoRAG leverages its web of associations in its hippocampal index and graph search algorithm to determine that Professor Thomas is relevant to this query and retrieves his passages appropriately”，即借助关联网络与图搜索完成检索 [chunk_900d1ff5b080ca47760a93ddc7d9e173]。RoG 一侧：所给证据只表明“the importance of relation paths for improving the reasoning performance of LLMs on complex questions”，并在不同跳数上比较 RoG 与其变体 [chunk_853c2cdb088533bc71f93f42690919ae]；没有任何引句描述 RoG 的查询种子、关系路径计划如何生成、或从问题到有效推理路径的具体流程，因此 RoG 的流程证据不足，无法与 HippoRAG 逐环节对比。

### R23 / Hybrid

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "citation:chunk_9eadf098f08b0e28d9965aeb46062d4e",
    "citation:chunk_dac5f23e1b87249cf88eff5c6cc54355",
    "citation:chunk_e3ad7608dae3913ef4231b54065c5882"
  ],
  "declared_but_not_inline": [
    "chunk_9eadf098f08b0e28d9965aeb46062d4e",
    "chunk_dac5f23e1b87249cf88eff5c6cc54355",
    "chunk_e3ad7608dae3913ef4231b54065c5882"
  ],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

ToG 算法以“depth limit Dmax 与 sample limit N”为要求，ToG-R 同样以“depth limit Dmax sam-
ple limit N”为要求[citation:chunk_9eadf098f08b0e28d9965aeb46062d4e]。Tree-of-Traversals 中，“The max depth was chosen analytically to be minimal while enabling answering of most
questions”[citation:chunk_e3ad7608dae3913ef4231b54065c5882]，而“The maximum expansions cutoff was chosen
purely to ensure the model does not hang on a sin-
gle question too long. The actual value is somewhat
arbitrary and has minimal impact on accuracy”[citation:chunk_e3ad7608dae3913ef4231b54065c5882]。其搜索在“max depth of the
tree search, after which the algorithm is forced to
transition to the done state”和“max expansions after which the model halts
exploration and returns "Cannot find answer"”两处边界下进行[citation:chunk_dac5f23e1b87249cf88eff5c6cc54355]。这些证据只说明各方法自身设定的深度、采样/扩展和停止条件，并未给出可将它们换算为墙钟时延的统一计时协议或跨方法时延对照，因此无法据此直接排出跨方法墙钟时延排名（证据不足）。

### R24 / Hybrid+Graph

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "Mongolia, Kazakhstan, North Korea"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

跨 KG（cross-KG）可由 MusicBrainz-x-Wikidata 说明：作者指出该数据集“requiring synthesizing information from multiple KGs to answer individual questions”，且是从 MusicBrainz 与 Wikidata 两个 KG 取信息进行推理 [chunk_f4962498025654850621ee329d0af7d6]。交并逻辑可由该文对既有数据集的批评间接说明：作者称这些数据集“less attention is paid to questions involving intersection and union logic”，并以交集问句“Which country borders with Russia and China at the same time?”为例，其答案为集合 [Mongolia, Kazakhstan, North Korea] [chunk_f8b1ae3d38356062df26e776ba255c06]。至于 CLQA-Wiki 与 2WikiMultiHop 各自如何定义“多跳”，所给证据只在统计表中出现 2WikiMultiHop、并称其属于“multi-hop and comparison-type questions”，没有给出 CLQA-Wiki 的多跳定义或专门解释 [chunk_f4962498025654850621ee329d0af7d6][chunk_f8b1ae3d38356062df26e776ba255c06]。因此，这些属性是否互相排斥，证据不足：跨 KG 例子与交并逻辑讨论出现在不同语境，且既有数据集同时被描述为聚焦多跳与比较型问题、却缺少交并逻辑问题，可见属性可并存而非互斥，但这一点属于推断，原文未直接断言互斥关系 [chunk_f4962498025654850621ee329d0af7d6][chunk_f8b1ae3d38356062df26e776ba255c06]。

### R24 / Hybrid

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [
    "Mongolia, Kazakhstan, North Korea"
  ],
  "declared_but_not_inline": [],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

CLQA-Wiki 未被提供的证据覆盖，无法说明其在这些文献中的具体指代。2WikiMultiHop：Tree-of-Traversals 的实验中 2WikiMultiHop 使用 Wikidata 作为知识图 [chunk_bc1cd12431f46892d2877dff73dab5e5]；该文在描述包含 2WikiMultiHop 在内的数据集时，未提供其多跳属性定义。另一文的作者指出这些数据集“primarily focused on multi-hop and comparison-type questions”，且较少关注交并逻辑问题 [chunk_f8b1ae3d38356062df26e776ba255c06]。交并逻辑：作者用交集问句“Which country borders with Russia and China at the same time?”为例，答案为集合 [Mongolia, Kazakhstan, North Korea]，并称现实问题常见交并逻辑 [chunk_f8b1ae3d38356062df26e776ba255c06]。跨 KG：作者新建 MusicBrainz-x-Wikidata，含 109 个问题，需要结合 MusicBrainz 与 Wikidata 的信息进行推理，并称此前没有要求合成多个 KG 信息回答单题的现有数据集 [chunk_f4962498025654850621ee329d0af7d6]。是否互相排斥：提供的证据未明确说明这些属性彼此排斥或可同时存在；仅能看出跨 KG 数据集被描述为需要合成多源信息 [chunk_f4962498025654850621ee329d0af7d6]，而对多跳与交并的讨论是数据集覆盖偏向问题 [chunk_f8b1ae3d38356062df26e776ba255c06]；关于三者互斥性证据不足。

### N03 / Hybrid+Graph

```json
{
  "status": "failed",
  "reason": "Unknown, missing or inconsistent inline citations",
  "error_type": "ValueError",
  "undeclared_inline_references": [],
  "declared_but_not_inline": [
    "chunk_67a081d945c23e9c2de3a746cbacb122"
  ],
  "unknown_chunk_references": []
}
```

未通过程序校验的模型草稿仅供诊断，不能当作已接受答案。

KGP 的图表示有原文支持：KGP“construct a KG over the given documents with nodes symbolizing passages or document structures and edges denoting their lexical/semantic similarity between passages or intra-document structural relations”[chunk_4c2f9284ed69432f1dd6ad5217a9a783]；摘要同样称节点象征 passages 或 document structures，边表示 passages 间语义/词汇相似或文档结构关系[chunk_b959214e888053dae53b16a5259d7ea9]。KGP 的检索机制是基于图的 LLM 遍历代理：“design an LLM-based KG traversal agent, which can alternatively generate the next evidence ... and select the most promising neighbor to visit from the constructed KG”[chunk_4c2f9284ed69432f1dd6ad5217a9a783]；摘要称该代理“navigates across nodes and gathers supporting passages”[chunk_b959214e888053dae53b16a5259d7ea9]。所给 HippoRAG 证据只涉及不确定性集成时的 passage 分数平均，未描述其图定义或段落节点/语义相似边检索流程，因此不能据此判断把 KGP 图表示直接作为 HippoRAG 图定义是否有依据；此问题证据不足。
