# 阶段 3 委托审核逐条记录

审核人：Codex；类型：用户明确委托的 AI 语义审核；策略：evidence-review-v1。

这不是独立人工专家核验，也不是阶段 4 的答案评测。原始候选、引句和实体均未改写；
证据不完整或类型错误时拒绝原候选，不把审核结果反写成模型原始输出。

判据：主体归属准确、端点类型正确、关系方向正确、引句及上下文支持、保留配置/采样限制；
性能超过、调用技术、分类表或文字相似本身都不能证明技术继承。

## 1 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 5–5 页。

关系：matching passages based on cosine similarity —IMPROVES_UPON→ token by token comparison

Claim：`3c475397876ae50f245ccfc772113b7bfbf32060b5e9a35531fdafc0a5351a76`；Chunk：`chunk_ba08d3e55b962d6032077a51bafe9eca`。

原文引句：

> To
> address this issue, we opt to match passages based
> on cosine similarity instead. Our analyses indicate
> that while most exact matches exhibit similarity
> scores around 0.99, some pairs with scores as low
> as 0.9 are also considered equivalent.

决定理由：关系不支持：改用余弦匹配不等于在逐token比较方法上形成技术继承。

## 2 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 5–5 页。

关系：Keyword-based approaches such as TF-IDF and BM25 —ADDRESSES→ lack the reasoning capabilities necessary for complex MD-QA tasks

Claim：`50123cf6d31c74f0951b683ba4bd6f76e181b064c419a864d42789b2c5c83969`；Chunk：`chunk_e70c99ac4d7bb0dfce44433041d60838`。

原文引句：

> Keyword-based approaches such as TF-IDF and
> BM25 lack the reasoning capabilities necessary for
> complex MD-QA tasks.

决定理由：语义反转：原文说TF-IDF/BM25缺乏推理能力，没有说它们解决此问题。

## 3 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 6–6 页。

关系：KGP_Mistral_ET (Ours) —EVALUATED_ON→ 4 multi-document question answering (MD-QA) benchmark datasets

Claim：`2a1e929979a93300f7039c21a54b806c0663af26624defb2b86d19a1b052b53a`；Chunk：`chunk_9c4ed8fb017cd0f15b601822cb9b8718`。

原文引句：

> KGP_Mistral_ET is the version of our method with early termination. KGP_T5 is a strong baseline.

决定理由：证据不足：引句仅解释提前终止版本，且客体是四个未命名数据集的集合。

## 4 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 6–6 页。

关系：KGP_Mistral (Ours) —EVALUATED_ON→ 4 multi-document question answering (MD-QA) benchmark datasets

Claim：`3a44c47cfc7228bc1b7cd0c8acc800650b00287dfd9951da63a33ee98af77d75`；Chunk：`chunk_9c4ed8fb017cd0f15b601822cb9b8718`。

原文引句：

> KGP_Mistral is
> our method. KGP_Mistral_ET is the version of our method with early termination. KGP_T5 is a strong baseline.

决定理由：证据不足：引句仅标识方法，没有列出评测数据集，客体不具体。

## 5 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 6–6 页。

关系：KGP_T5 —EVALUATED_ON→ 4 multi-document question answering (MD-QA) benchmark datasets

Claim：`8163bc60cf5ce43a89bbf9c4e8d203ea87faba5b305c47acd984180634e15106`；Chunk：`chunk_9c4ed8fb017cd0f15b601822cb9b8718`。

原文引句：

> KGP_Mistral is
> our method. KGP_Mistral_ET is the version of our method with early termination. KGP_T5 is a strong baseline.

决定理由：证据不足：强基线的说明不支持在四个具体数据集上的评测。

## 6 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 6–6 页。

关系：KGP_Mistral (Ours) —IMPROVES_UPON→ KGP_Mistral_ET (Ours)

Claim：`b6b540aabf26c6679ff72b4e16d6f59ed09b40f57c6b739597ab073b1e3e0fbf`；Chunk：`chunk_9c4ed8fb017cd0f15b601822cb9b8718`。

原文引句：

> KGP_Mistral is
> our method. KGP_Mistral_ET is the version of our method with early termination.

决定理由：方向不支持：提前终止变体与原方法的区别不能推出原方法改进该变体。

## 7 · 拒绝

论文：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 6–6 页。

关系：KGP_Mistral (Ours) —IMPROVES_UPON→ KGP_T5

Claim：`a3419f8890af5cd0beb703b75988450b3a797eeec3fd36bb7a873c291e8ef3da`；Chunk：`chunk_9c4ed8fb017cd0f15b601822cb9b8718`。

原文引句：

> KGP_Mistral is
> our method. KGP_Mistral_ET is the version of our method with early termination. KGP_T5 is a strong baseline.

决定理由：关系不支持：标识强基线不证明KGP_Mistral继承或改进KGP_T5。

## 8 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 1–1 页。

关系：G-Retriever —IMPROVES_UPON→ baselines

Claim：`6268a33a1f44f3056e834cfd99b2b2d60d0bae56862fc36da58b04f38b53946f`；Chunk：`chunk_3a7f7a1f47b2586d9d9877afb9110567`。

原文引句：

> Empirical evaluations
> show that our method outperforms baselines on textual graph tasks from multiple
> domains, scales well with larger graph sizes, and mitigates hallucination.

决定理由：泛化实体与关系混淆：baselines未具体命名，性能胜出不是技术继承。

## 9 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 1–1 页。

关系：G-Retriever —EVALUATED_ON→ textual graph tasks from multiple domains

Claim：`9b57b52aa5e41962aa75a66ea96dc2d8beac7f60e5b7ce5f606cb999f3e57768`；Chunk：`chunk_3a7f7a1f47b2586d9d9877afb9110567`。

原文引句：

> Empirical evaluations
> show that our method outperforms baselines on textual graph tasks from multiple
> domains, scales well with larger graph sizes, and mitigates hallucination.

决定理由：实体类型错误：textual graph tasks是任务集合，不是具体Dataset。

## 10 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 2–2 页。

关系：baseline method —ADDRESSES→ hallucination in Graph LLMs

Claim：`268e248da7afe119aa39cf8dbdf614702b0ba8fa4950babd90e7a3a89439073e`；Chunk：`chunk_99b18cdbb0bd9a36674e8b314d553ad3`。

原文引句：

> In particular, we employ a baseline method that adapts MiniGPT-4 [57] to graphs,
> where a frozen LLM interacts with a trainable GNN that encodes graph data as a soft prompt, as in
> GraphToken [31]. Our findings, shown in Table 1, indicate that hallucination, an important problem
> in text-based LLMs, is also prevalent in Graph LLMs.

决定理由：语义反转：该基线展示了幻觉现象，没有证明其缓解幻觉。

## 11 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 2–2 页。

关系：baseline method —IMPROVES_UPON→ MiniGPT-4 [57]

Claim：`1da063e9768a1a2f5d48769112f7e83b423ce3ea43f452956959b3194f17e864`；Chunk：`chunk_99b18cdbb0bd9a36674e8b314d553ad3`。

原文引句：

> In particular, we employ a baseline method that adapts MiniGPT-4 [57] to graphs

决定理由：主体不明确：baseline method不能作为跨论文可辨识的方法实体。

## 12 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 2–2 页。

关系：baseline method —ADDRESSES→ inability to recall the entire graph structure from a single graph embedding

Claim：`b44c25cf4df4984c11b5b0c3851ec0307b2afb40c43322a3406ece9a5efc752f`；Chunk：`chunk_99b18cdbb0bd9a36674e8b314d553ad3`。

原文引句：

> leading to the generation
> of incorrect nodes or edges during the QA task.

决定理由：证据不足：引句只描述错误节点/边的生成，没有支持所述解决关系。

## 13 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 6–7 页。

关系：Generating node and graph embeddings using a pre-trained LM —IMPROVES_UPON→ Using text attributes directly for node embedding

Claim：`c491be0840837187fe9208fb758bdd1dbf697a26793ae6cda1890ad2bd2489e8`；Chunk：`chunk_8c5476c0307c733adb60d1afe861e4d2`。

原文引句：

> We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.
> These embeddings are then stored in a nearest neighbor data structure.

决定理由：关系不支持：生成嵌入并存储不证明对另一具体方法的技术改进。

## 14 · 批准

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 6–7 页。

关系：Using SentenceBert for embedding generation —ADDRESSES→ Generating node and graph embeddings

Claim：`b090aed4a33011cc9b50837b0f60c22d3488902d82cc3dac9998e1528fddcbbd`；Chunk：`chunk_8c5476c0307c733adb60d1afe861e4d2`。

原文引句：

> Utilizing a pre-trained LM, such as
> SentenceBert [34], we apply the LM to xn, yielding the representation zn:

决定理由：来源全文明确以SentenceBert等预训练LM编码节点并对边作同类处理；支持嵌入生成任务，不主张效果优势。

## 15 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 6–7 页。

关系：k-nearest neighbors retrieval approach —EVALUATED_ON→ Set of ‘relevant nodes/edges’ based on the similarity between the query and each node or edge

Claim：`85dd5e5235904bd88704403b16bcf71ec0330940c2ff654f5cd993daab9e5e6b`；Chunk：`chunk_8c5476c0307c733adb60d1afe861e4d2`。

原文引句：

> Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors
> retrieval approach. This method yields a set of ‘relevant nodes/edges’ based on the similarity between
> the query and each node or edge.

决定理由：实体类型错误：检索所得相关节点/边集合不是评测数据集。

## 16 · 批准

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 7–7 页。

关系：Prize-Collecting Steiner Tree algorithm —ADDRESSES→ filter out irrelevant nodes and edges; enhance efficiency in graph processing

Claim：`2f88abc128b212599f84458915230839899bb637259e7d50d9ae61da7fb757a7`；Chunk：`chunk_04c0673f276b70d320674636d537dc80`。

原文引句：

> The Prize-Collecting Steiner Tree algorithm [2] serves as our primary method
> for identifying such optimally sized and relevant subgraphs. See Step 3 in Figure 3.

决定理由：来源段落明确把过滤无关节点/边与控制图规模作为目标，并指定PCST为实现方法。

## 17 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 8–9 页。

关系：G-Retriever —EVALUATED_ON→ Not specified in the chunk, but implied by context of Table 3 and Table 4 evaluations.

Claim：`3c692c8bb6c3caacfaf3a79e00fa3c4e689751422a26e9145fd4f3d5e4309ff3`；Chunk：`chunk_e2737c14a5cd36e6bd408af049fd0aac`。

原文引句：

> Table 3 demonstrates the effectiveness of our method across three datasets in various configurations.

决定理由：无效实体：客体是Not specified占位文本，未识别具体数据集。

## 18 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 8–9 页。

关系：G-Retriever w/ LoRA —EVALUATED_ON→ Not specified in the chunk, but implied by context of Table 3 and Table 4 evaluations.

Claim：`45a1a7abb18f36b729afced6af2c0b86c5023b2d644b90eda5205fdcceaa7fd4`；Chunk：`chunk_e2737c14a5cd36e6bd408af049fd0aac`。

原文引句：

> Table 3 demonstrates the effectiveness of our method across three datasets in various configurations.

决定理由：无效实体：客体是Not specified占位文本，未识别具体数据集。

## 19 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 8–9 页。

关系：G-Retriever —IMPROVES_UPON→ Frozen LLM w/ PT

Claim：`dc1f2b6732fe1afaac57b203969c5604d8733cccf8c3799d7e8074c2758b4a3c`；Chunk：`chunk_e2737c14a5cd36e6bd408af049fd0aac`。

原文引句：

> In the inference-only setting, G-Retriever surpasses all baselines. Notably, LLM can perform even
> better when no graph knowledge is provided (i.e., question only), which might be attributed to the
> complexity and potential noise in the knowledge.

决定理由：关系混淆：推理设置下性能胜出不足以证明对Frozen LLM w/ PT的技术继承。

## 20 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 8–9 页。

关系：G-Retriever w/ LoRA —IMPROVES_UPON→ Tuned LLM

Claim：`1f8d3f4a747cda700ff89b50eb5df82784aca6df85d17c5d33286af3fe1a9ae2`；Chunk：`chunk_e2737c14a5cd36e6bd408af049fd0aac`。

原文引句：

> Furthermore, when tuned with
> LoRA, G-Retriever achieves the best performance.

决定理由：关系混淆：LoRA设置下最好成绩不足以证明对Tuned LLM的技术继承。

## 21 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 8–9 页。

关系：G-Retriever —IMPROVES_UPON→ GraphToken [31]

Claim：`eaa76bfbf059e972cc8d5891c1d5e3083f9b234956cf733ac2bdd37cca077acf`；Chunk：`chunk_e2737c14a5cd36e6bd408af049fd0aac`。

原文引句：

> For frozen LLM with prompt tuning, G-Retriever
> outperforms traditional prompt tuning and GraphToken [31], a graph prompt tuning-based method,
> with average performance increases of 40.6% and 30.8% respectively.

决定理由：关系混淆：特定设置下优于GraphToken不等于在其基础上改进。

## 22 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —IMPROVES_UPON→ Baseline

Claim：`f7b56af7740c75b0d64c8097cf9fadd23310911608a64d1501d7cfb99208499a`；Chunk：`chunk_aba70e6f2f67df9b074a9e14ead47b00`。

原文引句：

> w/o Graph Encoder
> 54.62 ± 0.78
> ↓22.51%
> w/o Projection Layer
> 69.70 ± 0.68
> ↓1.11%
> w/o Textualized Graph
> 56.96 ± 1.83
> ↓19.19%
> w/o Retrieval
> 63.84 ± 0.41
> ↓9.43%

决定理由：证据不足：消融数值没有完整比较对象；Baseline也不是具体方法实体。

## 23 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —ADDRESSES→ Efficiency Evaluation

Claim：`a007a6565c2b8e9f4ba1d3ba0a816b23774cc909aa3340275120bde1e952e92d`；Chunk：`chunk_aba70e6f2f67df9b074a9e14ead47b00`。

原文引句：

> The efficiency of our approach is highlighted by the data in Table 4. Implementing our graph-based
> retrieval significantly decreases the number of tokens required to describe the graphs in text, reduces
> the number of nodes in graphs, and speeds up the training process.

决定理由：实体表述错误：Efficiency Evaluation是评测活动，不能直接充当被解决的问题。

## 24 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —ADDRESSES→ Hallucination Mitigation

Claim：`eebe10b969f40274abb2bfefee46bdf4a33b36e688fa72b661545fe0a3e8b31b`；Chunk：`chunk_aba70e6f2f67df9b074a9e14ead47b00`。

原文引句：

> 6.4
> Mitigation of Hallucination

决定理由：证据不足：只有小节标题，未说明G-Retriever如何缓解幻觉。

## 25 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —EVALUATED_ON→ 100 responses from both our method and the baseline (i.e., LLM with graph prompt tuning)

Claim：`6c7de930adbcd2b063deea156d5a215d706b7cbc116c5d34769f0cb1135fee75`；Chunk：`chunk_675c20afd5f26d294c1e46627fdf87c2`。

原文引句：

> We manually reviewed 100 responses from
> both our method and the baseline (i.e., LLM with graph prompt tuning), verifying the existence
> of the nodes and edges referenced in the model’s output within the actual graph.

决定理由：实体类型错误：人工检查的100个回答不是具名Dataset。

## 26 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —IMPROVES_UPON→ LLM with graph prompt tuning

Claim：`3a22ff98fe2a052893f290829032fdb93cfcf5a4c9c18004c18778b6408bfb6f`；Chunk：`chunk_675c20afd5f26d294c1e46627fdf87c2`。

原文引句：

> Table 5 shows
> that G-Retriever significantly reduces hallucinations by 54% compared to the baseline, as our graph
> retrieval ensures that the data is sourced directly from the actual graph, leading to less hallucination.

决定理由：关系混淆：幻觉率相对基线下降不证明对该基线的技术继承。

## 27 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：G-Retriever —ADDRESSES→ hallucination in answering graph-related questions

Claim：`6d20fc633f10a70c436d35c9770e7e28e853e6898b18046102afa11983e6f6cc`；Chunk：`chunk_675c20afd5f26d294c1e46627fdf87c2`。

原文引句：

> To evaluate hallucination, we instructed the models to answer graph-related questions, specifically
> identifying supporting nodes or edges from the graph.

决定理由：证据不足：引句是测评任务描述，未陈述G-Retriever解决幻觉。

## 28 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：graph encoder and textualized graph —ADDRESSES→ performance drops in the pipeline

Claim：`f136cfed4211a16232c9dbbe4004a0a3d8353d1a5d25cc8def358f0f4cb5d0a9`；Chunk：`chunk_675c20afd5f26d294c1e46627fdf87c2`。

原文引句：

> As
> shown in Table 6, there are performance drops when any of these components are removed, with the
> graph encoder and textualized graph showing declines of 22.51% and 19.19%, respectively.

决定理由：关系不支持：移除组件后性能下降不等于组件专门解决performance drops；主体也是组件集合。

## 29 · 拒绝

论文：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 9–9 页。

关系：retrieval on graphs —ADDRESSES→ performance drops in the pipeline

Claim：`1e4c7d308bc7a3582cd824f3f6795e8dee0b1278b85d5c22e3be287997f0acdc`；Chunk：`chunk_675c20afd5f26d294c1e46627fdf87c2`。

原文引句：

> Additionally, the retrieval on graphs is also important to the overall performance.

决定理由：证据不足：重要性陈述不证明retrieval on graphs解决所抽取的问题。

## 30 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 1–1 页。

关系：HippoRAG —IMPROVES_UPON→ IRCoT

Claim：`24a6cec0780f9d0704964b03462355b431bcf4b9c6aeae7c0b65f8d9b8cb9898`；Chunk：`chunk_59677fe889f95e3e84ca00ba132a54fd`。

原文引句：

> and integrating HippoRAG into IRCoT brings further substantial gains.

决定理由：配置混淆：HippoRAG与IRCoT组合带来增益，不是HippoRAG继承IRCoT。

## 31 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 1–1 页。

关系：HippoRAG —EVALUATED_ON→ multi-hop question answering (QA)

Claim：`1aad92b859d169a00d1a5c1af38f15caf0685f9219687c1f86c5f3ab99d63152`；Chunk：`chunk_59677fe889f95e3e84ca00ba132a54fd`。

原文引句：

> We compare HippoRAG
> with existing RAG methods on multi-hop question answering (QA) and show that
> our method outperforms the state-of-the-art methods remarkably, by up to 20%.

决定理由：实体类型错误：multi-hop QA是任务，不是具体Dataset。

## 32 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 1–1 页。

关系：HippoRAG —COMPARES_WITH→ existing RAG methods

Claim：`db654fad4d3a4e0cd44c2126884b1d0a2a1a306cf4e95dfeb15c636d823c99c4`；Chunk：`chunk_59677fe889f95e3e84ca00ba132a54fd`。

原文引句：

> We compare HippoRAG
> with existing RAG methods on multi-hop question answering (QA) and show that
> our method outperforms the state-of-the-art methods remarkably, by up to 20%.

决定理由：实体不具体：existing RAG methods未被识别为单一具名比较方法。

## 33 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 2–3 页。

关系：HippoRAG —IMPROVES_UPON→ current RAG methods [10, 35, 53, 70, 71]

Claim：`3e751a84322c4dbc4b8d4b02b1708f988c45394d4063cc279fe6c87b2ccb8414`；Chunk：`chunk_ffb475af5faa17fe0fd9f25c731d61e8`。

原文引句：

> on two popular multi-hop QA
> benchmarks, MuSiQue [77] and 2WikiMultiHopQA [33]. Additionally, HippoRAG’s online retrieval
> process is 10 to 30 times cheaper and 6 to 13 times faster than current iterative retrieval methods
> like IRCoT [78], while still achieving comparable performance.

决定理由：关系混淆且对象泛化：成本/速度对比不证明对current RAG methods的技术继承。

## 34 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 2–3 页。

关系：HippoRAG —EVALUATED_ON→ MuSiQue [77] and 2WikiMultiHopQA [33]

Claim：`a33f894f0690fead563fd3256cd49a8215a0b29868757a558da901ce9a3cd455`；Chunk：`chunk_ffb475af5faa17fe0fd9f25c731d61e8`。

原文引句：

> on two popular multi-hop QA
> benchmarks, MuSiQue [77] and 2WikiMultiHopQA [33].

决定理由：复合实体：把MuSiQue与2WikiMultiHopQA合成一个Dataset节点，应拆成独立候选。

## 35 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 2–3 页。

关系：HippoRAG —EVALUATED_ON→ HotpotQA

Claim：`1a29b947863464c1715caf705d659fcee166caa23ae28a28a31d8767f3aebd78`；Chunk：`chunk_ffb475af5faa17fe0fd9f25c731d61e8`。

原文引句：

> and even obtain improvements on HotpotQA, a less challenging multi-hop QA dataset.

决定理由：配置归属不精确：来源此处HotpotQA增益对应HippoRAG与IRCoT组合，候选未保留组合条件。

## 36 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 2–3 页。

关系：HippoRAG —COMPARES_WITH→ IRCoT [78]

Claim：`38352054614c962418bc50ca51dceab7da100d3d3400ad9a3f317aec303744fd`；Chunk：`chunk_ffb475af5faa17fe0fd9f25c731d61e8`。

原文引句：

> while still achieving comparable performance.

决定理由：证据不足：引句未包含IRCoT或比较对象，仅凭片段外补充不能完整支持。

## 37 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 3–4 页。

关系：HippoRAG —IMPROVES_UPON→ PageRank algorithm [30]

Claim：`029e2364c535ed7b5e499a4015c298e778dc675ab1006dca915f36c6764c9bf6`；Chunk：`chunk_eaf42f9945053a085ff4b160247ddf6a`。

原文引句：

> To imitate this efficient graph search process, we leverage the Personalized PageRank
> (PPR) algorithm [30], a version of PageRank that distributes probability across a graph only through
> a set of user-defined source nodes.

决定理由：关系混淆：使用Personalized PageRank不表示HippoRAG改进了PageRank算法。

## 38 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 3–4 页。

关系：HippoRAG —ADDRESSES→ Online Retrieval

Claim：`90643a9c88d2dbc975e81a6f7110fc574cefc1ce2781325e699faf87dafb8ab3`；Chunk：`chunk_eaf42f9945053a085ff4b160247ddf6a`。

原文引句：

> These same three components are then leveraged to perform online retrieval
> by mirroring the human brain’s memory retrieval process.

决定理由：来源Online Retrieval小节明确描述该框架的查询实体抽取、链接和在线检索流程；只确认任务用途。

## 39 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 4–4 页。

关系：HippoRAG —IMPROVES_UPON→ Personalized PageRank algorithm

Claim：`8f3509bf5a66baa4a5b1a1689472365e302ab5e849b51f04d2bd41bdfc978cc4`；Chunk：`chunk_2b91faafba587efd8a416d2355639ee0`。

原文引句：

> We then leverage the
> Personalized PageRank algorithm to enable context-based retrieval and extract Professor Thomas.

决定理由：关系混淆：利用PPR完成检索不是对PPR算法本身的技术改进。

## 40 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 4–4 页。

关系：HippoRAG —EVALUATED_ON→ passages into open KG triples, which are then added to our artificial hippocampal index

Claim：`316bee8f28f5eec09e41a403a2e1550fe1463677efb0e2ae0d4040b8793e88a6`；Chunk：`chunk_2b91faafba587efd8a416d2355639ee0`。

原文引句：

> For offline indexing (Middle),
> we use an LLM to process passages into open KG triples, which are then added to our artificial
> hippocampal index, while our synthetic parahippocampal regions (PHR) detect synonymy.

决定理由：实体类型错误：处理为KG三元组的passages及流程描述不是Dataset。

## 41 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 4–4 页。

关系：HippoRAG —EVALUATED_ON→ named entities from a query while our parahippocampal retrieval encoders link them to our hippocampal index

Claim：`9f4e1dfe4ef77828907205ddbb3e349720da27829c6d676bdb1ecd0767cf05b8`；Chunk：`chunk_2b91faafba587efd8a416d2355639ee0`。

原文引句：

> In the
> example above, triples involving Professor Thomas are extracted and integrated into the KG. For
> online retrieval (Bottom), our LLM neocortex extracts named entities from a query while our
> parahippocampal retrieval encoders link them to our hippocampal index.

决定理由：实体类型错误：查询实体抽取/链接流程不是Dataset。

## 42 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–5 页。

关系：HippoRAG —EVALUATED_ON→ MuSiQue (answerable)

Claim：`70cea20e7a0443f6faca64e9fc228cd3fb49d7d04e98bbd76335fd26808427da`；Chunk：`chunk_3fa28005a4df0de5249826585cf9d713`。

原文引句：

> We evaluate our method’s retrieval capabilities primarily on two challenging multi-hop QA bench-
> marks, MuSiQue (answerable) [77] and 2WikiMultiHopQA [33].

决定理由：实验设置明确评测HippoRAG在MuSiQue answerable子集上的检索；保留1000条验证集采样条件于来源上下文。

## 43 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–5 页。

关系：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA

Claim：`cdc252ae7549ba66f43a113278975737318353b1a6c9ea51c76ee3047de0f000`；Chunk：`chunk_3fa28005a4df0de5249826585cf9d713`。

原文引句：

> We evaluate our method’s retrieval capabilities primarily on two challenging multi-hop QA bench-
> marks, MuSiQue (answerable) [77] and 2WikiMultiHopQA [33].

决定理由：实验设置明确列出2WikiMultiHopQA作为检索评测数据集；仅确认评测关系。

## 44 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–5 页。

关系：HippoRAG —EVALUATED_ON→ HotpotQA

Claim：`343f86df68b018d5440c3b259036c001d0acc753dbeb7ce360c6ccff15f4a8e0`；Chunk：`chunk_3fa28005a4df0de5249826585cf9d713`。

原文引句：

> For completeness, we also
> include the HotpotQA [89] dataset even though it has been found to be a much weaker test for
> multi-hop reasoning due to many spurious signals [77], as we also show in Appendix B.

决定理由：实验设置明确将HotpotQA纳入评测，同时保留作者对其多跳难度偏弱的限制。

## 45 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–6 页。

关系：HippoRAG —EVALUATED_ON→ MuSiQue

Claim：`c980c9a25fe4e838823b0713a182b5c96e5230938e1661e58cab191e47573723`；Chunk：`chunk_8cc831cc45851cce50b9f34648070765`。

原文引句：

> HippoRAG outperforms all baselines on MuSiQue and
> 2WikiMultiHopQA and achieves comparable performance on the less challenging HotpotQA dataset.

决定理由：Table 2说明明确报告HippoRAG在MuSiQue的单步检索实验；不把胜出表述转成继承边。

## 46 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–6 页。

关系：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA

Claim：`b1c9edf9b62bccb6624cc1d5ca409aed1e14c2a9e095fb95f2b7dcb368823051`；Chunk：`chunk_8cc831cc45851cce50b9f34648070765`。

原文引句：

> HippoRAG outperforms all baselines on MuSiQue and
> 2WikiMultiHopQA and achieves comparable performance on the less challenging HotpotQA dataset.

决定理由：Table 2说明明确报告HippoRAG在2WikiMultiHopQA的单步检索实验。

## 47 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 5–6 页。

关系：HippoRAG —EVALUATED_ON→ HotpotQA

Claim：`ef9d52716427c011b0bff0da79aa97d00266a544d55e1d9abd4c6e0186ba421e`；Chunk：`chunk_8cc831cc45851cce50b9f34648070765`。

原文引句：

> HippoRAG outperforms all baselines on MuSiQue and
> 2WikiMultiHopQA and achieves comparable performance on the less challenging HotpotQA dataset.

决定理由：Table 2说明明确报告HippoRAG在HotpotQA取得可比表现，支持评测关系。

## 48 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–6 页。

关系：HippoRAG (Contriever) —EVALUATED_ON→ 2Wiki

Claim：`e7d4009a6e07ce1207c8461837f76a0e2f00bae8167f9b8d8fa7f796834f02d4`；Chunk：`chunk_18bee03d708874e36549c17129df7d7f`。

原文引句：

> HippoRAG (Contriever)
> 41.0
> 52.1
> 71.5
> 89.5
> 59.0
> 76.2
> 57.2
> 72.6

决定理由：引句缺少表头：孤立数值行无法自行证明2Wiki列的归属；保留已明确支持的评测候选即可。

## 49 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–6 页。

关系：HippoRAG (ColBERTv2) —EVALUATED_ON→ HotpotQA

Claim：`11e4a3f549be1c5ca62b0e9f7292b3663fd649ac6135377763d485c1216484b6`；Chunk：`chunk_18bee03d708874e36549c17129df7d7f`。

原文引句：

> HippoRAG (ColBERTv2)
> 40.9
> 51.9
> 70.7
> 89.1
> 60.5
> 77.7
> 57.4
> 72.9

决定理由：引句缺少表头：孤立数值行无法完整证明HotpotQA数据集归属。

## 50 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–6 页。

关系：IRCoT + ColBERTv2 —EVALUATED_ON→ MuSiQue

Claim：`dde73e1a25c78c03d6e1536fc9981b8042f03f9bcf5caf9256dbf81f7df5eb97`；Chunk：`chunk_18bee03d708874e36549c17129df7d7f`。

原文引句：

> IRCoT + ColBERTv2
> 41.7
> 53.7
> 64.1
> 74.4
> 67.9
> 82.0
> 57.9
> 70.0

决定理由：引句缺少表头：孤立IRCoT数值行无法完整证明MuSiQue数据集归属。

## 51 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–7 页。

关系：HippoRAG —EVALUATED_ON→ MuSiQue

Claim：`670eacc289f3067ba1ec27636a69accb03f50985930cc52fb476c4105067afca`；Chunk：`chunk_b1e16d1c0cce0b7a5286e2e0f30b9821`。

原文引句：

> on our main
> datasets, MuSiQue and 2WikiMultiHopQA, while achieving competitive performance on HotpotQA.

决定理由：来源Single-Step Retrieval Results明确主体HippoRAG及MuSiQue；支持评测事实而非普遍优势。

## 52 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–7 页。

关系：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA

Claim：`35abdfbb8eb7d3aa01911d8eeb2c3b6d8b26fbf105c0eee59742cf0b693f9ca6`；Chunk：`chunk_b1e16d1c0cce0b7a5286e2e0f30b9821`。

原文引句：

> on our main
> datasets, MuSiQue and 2WikiMultiHopQA, while achieving competitive performance on HotpotQA.

决定理由：来源Single-Step Retrieval Results明确主体HippoRAG及2WikiMultiHopQA；支持评测事实。

## 53 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–7 页。

关系：HippoRAG —EVALUATED_ON→ HotpotQA

Claim：`6e60213fbfbcf0f7f6d5916c3b3a1f99c3898eff7816899d07c1bd828dc24f27`；Chunk：`chunk_b1e16d1c0cce0b7a5286e2e0f30b9821`。

原文引句：

> on our main
> datasets, MuSiQue and 2WikiMultiHopQA, while achieving competitive performance on HotpotQA.

决定理由：来源Single-Step Retrieval Results明确主体HippoRAG及HotpotQA；支持评测事实。

## 54 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–7 页。

关系：HippoRAG —IMPROVES_UPON→ Propositionizer

Claim：`b5ac02ff397e807fd19512281caacbaa06a1cdd7d275623e64d822d77e24836a`；Chunk：`chunk_b1e16d1c0cce0b7a5286e2e0f30b9821`。

原文引句：

> HippoRAG outperforms all other methods,
> including recent LLM-augmented baselines such as Propositionizer and RAPTOR, on our main
> datasets, MuSiQue and 2WikiMultiHopQA, while achieving competitive performance on HotpotQA.

决定理由：关系混淆：胜过Propositionizer的实验结果不证明技术继承。

## 55 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 6–7 页。

关系：HippoRAG —IMPROVES_UPON→ RAPTOR

Claim：`6341e788e6c617888c60df82b2e87d38642cba779f303614127f93e1c3ef3384`；Chunk：`chunk_b1e16d1c0cce0b7a5286e2e0f30b9821`。

原文引句：

> HippoRAG outperforms all other methods,
> including recent LLM-augmented baselines such as Propositionizer and RAPTOR, on our main
> datasets, MuSiQue and 2WikiMultiHopQA, while achieving competitive performance on HotpotQA.

决定理由：关系混淆：胜过RAPTOR的实验结果不证明技术继承。

## 56 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 7–7 页。

关系：REBEL —EVALUATED_ON→ MuSiQue training set

Claim：`9c342dd53e457098d8b645b8309abfd86a3f02dd943ed1556d4c2bf4bafa66c6`；Chunk：`chunk_9954ac297e86a9093f805de039efb2b4`。

原文引句：

> We then perform a small-scale
> intrinsic evaluation using the CaRB [6] framework for OpenIE. We find that both Llama-3.1-Instruct

决定理由：证据不足：引句是CaRB/OpenIE评测介绍，没有完整支持REBEL在MuSiQue训练集上的关系。

## 57 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 7–7 页。

关系：GPT-3.5 —EVALUATED_ON→ MuSiQue training set

Claim：`3ec54654348e4bfc71918ea0071cace14c4ffd7290fd37bd60746a54023f76c0`；Chunk：`chunk_9954ac297e86a9093f805de039efb2b4`。

原文引句：

> We then perform a small-scale
> intrinsic evaluation using the CaRB [6] framework for OpenIE. We find that both Llama-3.1-Instruct

决定理由：证据不足：引句没有GPT-3.5及MuSiQue训练集的完整评测关系。

## 58 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 7–7 页。

关系：Llama-3.1-8B —EVALUATED_ON→ MuSiQue training set

Claim：`f2cfc581719100e1f0e8e981c290637e52542294fb0c0e09c641d866ae219250`；Chunk：`chunk_9954ac297e86a9093f805de039efb2b4`。

原文引句：

> We then perform a small-scale
> intrinsic evaluation using the CaRB [6] framework for OpenIE. We find that both Llama-3.1-Instruct

决定理由：证据不足：Llama-3.1-Instruct的截断句无法支持该模型版本与MuSiQue训练集。

## 59 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 7–7 页。

关系：Llama-3.1-70B —EVALUATED_ON→ MuSiQue training set

Claim：`a8f1c76fec648c90faf54040dd5e07f46553c4dafca5dc689725bbd252399dc2`；Chunk：`chunk_9954ac297e86a9093f805de039efb2b4`。

原文引句：

> We then perform a small-scale
> intrinsic evaluation using the CaRB [6] framework for OpenIE. We find that both Llama-3.1-Instruct

决定理由：证据不足：Llama-3.1-Instruct的截断句无法支持70B版本与MuSiQue训练集。

## 60 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：PPR —IMPROVES_UPON→ simple baselines

Claim：`fc9d4fa1d1346d36dbd0a6adb623f70f2b6b76d2e2dab67a15a558e0e9b3964d`；Chunk：`chunk_8245d0849e8cf0df364eb6980d96843c`。

原文引句：

> First, we find that PPR is a much more effective method
> for including associations for retrieval on all three datasets compared to both simple baselines.

决定理由：关系混淆且对象泛化：PPR优于simple baselines不证明具体技术继承。

## 61 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：node specificity —EVALUATED_ON→ MuSiQue and HotpotQA

Claim：`28d7a577efb35276c9777f259fa9920c3b2285a8f3d9e1511c3797532e63c183`；Chunk：`chunk_8245d0849e8cf0df364eb6980d96843c`。

原文引句：

> node specificity obtains considerable improvements on
> MuSiQue and HotpotQA and yields almost no change in 2WikiMultiHopQA.

决定理由：复合Dataset与主体不精确：MuSiQue和HotpotQA应分开，node specificity是组件而非具名完整方法。

## 62 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：HippoRAG —IMPROVES_UPON→ ColBERTv2

Claim：`3f351de468754ec06ce911d939f07c19a97dc8f623bbaffe744e9fd0c1d7d2d9`；Chunk：`chunk_f2730b810f92d04b5307ad0780e7ace5`。

原文引句：

> Table 6: All-Recall metric. We measure the percentage of queries for which all supporting passages
> are successfully retrieved (all-recall, denoted as AR@2 or AR@5) and find even larger performance
> improvements for HippoRAG.

决定理由：关系混淆：All-Recall改进不证明HippoRAG继承ColBERTv2，且引句没有比较对象。

## 63 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：HippoRAG —ADDRESSES→ multi-hop QA

Claim：`5fd3b08028e13067687cd5f8e0aba407ca6c029625a05ebb66750db07ca05dce`；Chunk：`chunk_f2730b810f92d04b5307ad0780e7ace5`。

原文引句：

> A major advantage of HippoRAG over conventional RAG methods in multi-hop QA is its ability
> to perform multi-hop retrieval in a single step.

决定理由：引句明确HippoRAG通过单步多跳检索服务multi-hop QA；只确认面向任务的关系。

## 64 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：HippoRAG —EVALUATED_ON→ MuSiQue

Claim：`030925126d692054783f98a5ac14754ec50c98520526ce95c69ced9d5da5adfd`；Chunk：`chunk_f2730b810f92d04b5307ad0780e7ace5`。

原文引句：

> Table 6: All-Recall metric. We measure the percentage of queries for which all supporting passages
> are successfully retrieved (all-recall, denoted as AR@2 or AR@5) and find even larger performance
> improvements for HippoRAG.

决定理由：证据不足：引句未包含MuSiQue；邻近表格结果应另用完整引句抽取。

## 65 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA

Claim：`376b324ef43aafdf42806476135fc9c75e43f9a58e69865859ecce207e91ebb4`；Chunk：`chunk_f2730b810f92d04b5307ad0780e7ace5`。

原文引句：

> Table 6: All-Recall metric. We measure the percentage of queries for which all supporting passages
> are successfully retrieved (all-recall, denoted as AR@2 or AR@5) and find even larger performance
> improvements for HippoRAG.

决定理由：证据不足：引句未包含2WikiMultiHopQA；邻近表格结果应另用完整引句抽取。

## 66 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：HippoRAG —IMPROVES_UPON→ standard RAG methods

Claim：`340c450c78888ebf8d23de295384c4d08c43ef2f018a42796de24938cb9eb840`；Chunk：`chunk_ac51522ee28010366179ed4733266ace`。

原文引句：

> something that standard RAG methods would be unable to do
> directly

决定理由：泛化实体且证据不足：standard RAG methods不具体，局部能力差异不是继承。

## 67 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 8–8 页。

关系：IRCoT —IMPROVES_UPON→ HippoRAG

Claim：`d775ce5a43a1b8ec45e32d26a46d81c2960b5c37388991fc7f489d5bcdf7f2d7`；Chunk：`chunk_ac51522ee28010366179ed4733266ace`。

原文引句：

> as shown
> in Appendix G, it is 10-30 times more expensive and 6-13 times slower than ours in terms of online
> retrieval

决定理由：方向与关系错误：IRCoT更慢更贵的对比不能证明IRCoT改进HippoRAG。

## 68 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 10–10 页。

关系：Earlier works in this category —ADDRESSES→ Graph-Augmented Reading Comprehension

Claim：`d3321af97114357a6320823d29b0d982c8d3f341258690d5c347bc53a60283a2`；Chunk：`chunk_513a6dee6b9d2e8bac593f0a139f9ba4`。

原文引句：

> Graph-Augmented Reading Comprehension. Earlier works in this category are mainly supervised
> methods which mix signal from a hyperlink or co-occurrence graph with a language model through a
> graph neural network (GNN) [20, 67, 65]. More recent works use LLMs and introduce knowledge
> graph triples directly into the LLM prompt [57, 43, 47]. Although these works share HippoRAG’s
> use of graphs for multi-hop QA, their generation-based improvements are fully complementary to
> HippoRAG’s, which are solely based on improved retrieval.

决定理由：主体不具体：Earlier works in this category是未解析的文献集合。

## 69 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 10–10 页。

关系：Earlier works in this category —IMPROVES_UPON→ HippoRAG’s use of graphs for multi-hop QA

Claim：`bf0b31790dd69b193a1a40ba86a1e2297c541f3326e2ce1b4cacfb3e9f3564d0`；Chunk：`chunk_513a6dee6b9d2e8bac593f0a139f9ba4`。

原文引句：

> Although these works share HippoRAG’s
> use of graphs for multi-hop QA, their generation-based improvements are fully complementary to
> HippoRAG’s, which are solely based on improved retrieval.

决定理由：关系不支持：原文强调互补，不是改进继承；两个端点也非具体方法。

## 70 · 批准

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 10–10 页。

关系：HippoRAG —ADDRESSES→ Graph-Augmented Retrieval

Claim：`6d88023222e2af0ce06ad00bc61cb87f1bf2a52810c603729332597ae5140411`；Chunk：`chunk_513a6dee6b9d2e8bac593f0a139f9ba4`。

原文引句：

> Graph-Augmented Retrieval. In this second category, previous work trains a re-ranking module
> which can traverse a graph made using Wikipedia hyperlinks [16, 100, 54, 14, 4, 44]. HippoRAG,
> in contrast, builds a KG from scratch using LLMs and performs multi-hop retrieval without any
> supervision, making it much more adaptable.

决定理由：来源明确HippoRAG自建KG并无监督执行多跳检索，支持Graph-Augmented Retrieval用途。

## 71 · 拒绝

论文：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 10–10 页。

关系：HippoRAG —IMPROVES_UPON→ previous work trains a re-ranking module which can traverse a graph made using Wikipedia hyperlinks

Claim：`aa4959d1f46b485e6566b918a408852465a589c619f6d4840acae66e771dba52`；Chunk：`chunk_513a6dee6b9d2e8bac593f0a139f9ba4`。

原文引句：

> Graph-Augmented Retrieval. In this second category, previous work trains a re-ranking module
> which can traverse a graph made using Wikipedia hyperlinks [16, 100, 54, 14, 4, 44]. HippoRAG,
> in contrast, builds a KG from scratch using LLMs and performs multi-hop retrieval without any
> supervision, making it much more adaptable.

决定理由：对象不是单一方法，且与前人方案不同不等于在前人方法基础上改进。

## 72 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 2–2 页。

关系：KG-GPT —IMPROVES_UPON→ fully-supervised models

Claim：`b24af049d5703075bf1acc6a4ce7080a131a43c3ff0b94026a53fdd09dcbf769`；Chunk：`chunk_cfe612908773552496db582da6b6b26c`。

原文引句：

> KG-GPT
> shows competitive performance compared to other
> fully-supervised models, even outperforming some.

决定理由：关系混淆且对象泛化：competitive/outperforming fully-supervised models不是技术继承。

## 73 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 3–4 页。

关系：KG-GPT —EVALUATED_ON→ FACTKG

Claim：`57142a9cad2033c5c977fac9926450d4cfafe3d56df9a9ad99e9c78a65d3d21d`；Chunk：`chunk_3aa0cdece98e31f453ae4c5546e718b8`。

原文引句：

> We evaluated the models’ prediction capability for
> labels (i.e. Supported or Refuted) and presented
> the accuracy score in Table 1.

决定理由：引句缺少数据集与主体：仅说明标签预测和Table 1，保留后续有明确FACTKG表注的候选。

## 74 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 3–4 页。

关系：12-shot ChatGPT —EVALUATED_ON→ FACTKG

Claim：`8e36a31b42a9b22ddc4291c0d230a57effd38cdb1a0b1f8942f7fb275410f254`；Chunk：`chunk_3aa0cdece98e31f453ae4c5546e718b8`。

原文引句：

> It also outperforms 12-shot ChatGPT by 4.20%.

决定理由：证据不足：4.20%比较未标出FACTKG，不能作为完整评测引句。

## 75 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 3–4 页。

关系：KG-GPT —IMPROVES_UPON→ Claim Only models BERT, BlueBERT, and Flan-T5

Claim：`d88a6887439d20e6b1985a5ba717edd05f08e5bb6474ca8dc7044582f2124fc1`；Chunk：`chunk_3aa0cdece98e31f453ae4c5546e718b8`。

原文引句：

> KG-GPT
> outperforms Claim Only models BERT, BlueBERT,
> and Flan-T5 with performance enhancements of
> 7.48%, 12.75%, and 9.98% absolute, respectively.

决定理由：复合方法实体且关系混淆：对BERT/BlueBERT/Flan-T5的分数差不是技术继承。

## 76 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 3–4 页。

关系：KG-GPT —IMPROVES_UPON→ 12-shot ChatGPT

Claim：`160132bcf9cff0537b8cb92cd46b3835e2b551229dd3cd764162eb89b0aa2941`；Chunk：`chunk_3aa0cdece98e31f453ae4c5546e718b8`。

原文引句：

> It also outperforms 12-shot ChatGPT by 4.20%.

决定理由：关系混淆：优于12-shot ChatGPT的分数不证明继承。

## 77 · 批准

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 4–4 页。

关系：KG-GPT —EVALUATED_ON→ FACTKG

Claim：`2911bd60ee910fa40bdac6e28f0abdf2b51f977c5107f19546eece3657d07edd`；Chunk：`chunk_3f7eb65828761447433c66c28ad111a4`。

原文引句：

> Table 1: The performance of the models on FACTKG.

决定理由：来源Table 1含KG-GPT行及FACTKG表注，明确支持该数据集上的评测。

## 78 · 批准

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 4–4 页。

关系：KG-GPT —EVALUATED_ON→ MetaQA

Claim：`e8ffc6a429c28ff81684f0ea21a3a60b9ca28e69ad35eca40449e4c2fe00e450`；Chunk：`chunk_3f7eb65828761447433c66c28ad111a4`。

原文引句：

> Table 2: The performance of the models on MetaQA
> (Hits@1).

决定理由：来源Table 2含KG-GPT行与MetaQA各跳数结果，表注明确数据集和Hits@1。

## 79 · 批准

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 4–4 页。

关系：KG-GPT —EVALUATED_ON→ MetaQA

Claim：`9ad4c9c553df77c7ad7b7ab737a9a05e6d4b52a7147a002d35aed5a8bfe03167`；Chunk：`chunk_6d513ef9de004b3c675d2c25a69d5330`。

原文引句：

> The findings on MetaQA are presented in Table 2.

决定理由：来源紧接着报告KG-GPT在MetaQA的1/2/3-hop成绩，支持评测关系。

## 80 · 拒绝

论文：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 4–4 页。

关系：KG-GPT —IMPROVES_UPON→ KV-Mem

Claim：`5d80c64c7320b11182a9e9bb380d7705e5a5c6efa180e9a4dfdfbabf3973756f`；Chunk：`chunk_6d513ef9de004b3c675d2c25a69d5330`。

原文引句：

> it surpasses KV-Mem by margins of
> 0.1%, 11.7%, and 45.1% across three distinct tasks
> respectively, signifying its superior performance.

决定理由：关系混淆：各任务上超过KV-Mem的分数不证明技术继承。

## 81 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 1–1 页。

关系：Directly prompting LLMs without providing any context —EVALUATED_ON→ 2WikiMQA

Claim：`41fbe56d275d38d682bf28866e493de0c80a0d902b5fcb1149cc3de12566c65f`；Chunk：`chunk_8c219a27ca5b91f3ae28f8a01544943e`。

原文引句：

> directly prompting LLMs without providing
> any context, i.e., None, achieves only 25.07%/10.58% F1
> and 18.60%/4.60% EM on 2WikiMQA/MuSiQue

决定理由：引句直接报告无上下文提示策略在2WikiMQA上的F1/EM，来源说明开发集抽样。

## 82 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 1–1 页。

关系：Directly prompting LLMs without providing any context —EVALUATED_ON→ MuSiQue

Claim：`dcd6bd036cff4d60750d57b5c40114063082d486fc6445b2ba5c7e3fafdd971b`；Chunk：`chunk_8c219a27ca5b91f3ae28f8a01544943e`。

原文引句：

> directly prompting LLMs without providing
> any context, i.e., None, achieves only 25.07%/10.58% F1
> and 18.60%/4.60% EM on 2WikiMQA/MuSiQue

决定理由：引句直接报告无上下文提示策略在MuSiQue上的F1/EM，来源说明开发集抽样。

## 83 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 2–2 页。

关系：instruction fine-tuning strategy —IMPROVES_UPON→ LLM-based KG traversal agent

Claim：`23dc5371c080205ce0e33e0ab277bc4b25a455f541393670eee65076daf863b8`；Chunk：`chunk_4c2f9284ed69432f1dd6ad5217a9a783`。

原文引句：

> we apply the instruction fine-tuning strategy to
> augment the reasoning capability of the LLM-based KG
> traversal agent and hence refrain from repeatedly prompting
> non-open-sourced LLMs for evidence generation.

决定理由：端点角色错误：训练策略用于增强代理，不是策略作为新方法继承代理。

## 84 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 3–3 页。

关系：TAGME (Min et al. 2019) —ADDRESSES→ adding structural nodes to the graph based on document structures

Claim：`36042f6246f30321eefe1dfc4671d65f34084248f5c67ad046215eebcff9d749`；Chunk：`chunk_7a6934ab0623f3f791297f3fe38b2b8c`。

原文引句：

> In addition to passage nodes, we further add structural
> nodes into the graph by extracting document structures via
> Extract-PDF 3.

决定理由：主体错配：引句明确结构提取工具为Extract-PDF，不支持TAGME完成此功能。

## 85 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 4–4 页。

关系：TAGME —EVALUATED_ON→ HotpotQA

Claim：`7c4012c37a0dcba7ddebf4640bdcc141eaff43200352a7301e6d6e9e51c097f9`；Chunk：`chunk_720b9036bf8c30eaf69c980fccbcec6d`。

原文引句：

> For TAGME, we empirically
> find it identifies a larger quantity of entities mentioned in
> a single passage, which leads to a denser graph and causes
> the starting SF-EM of TAGME to be already around 0.95.

决定理由：证据不足：TAGME图密度与SF-EM描述没有在引句中标出HotpotQA。

## 86 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 5–5 页。

关系：KGP method —IMPROVES_UPON→ TF-IDF search

Claim：`d635a209c1f339dba3db9682e029545dc3c7226727831691ea82d7709be43d5b`；Chunk：`chunk_84038d4c6f7949959af0974d04ee2379`。

原文引句：

> we first initialize seeding passages Vs
> and the reasoning path queue P by TF-IDF search.

决定理由：关系混淆：KGP调用TF-IDF初始化不表示继承改进TF-IDF。

## 87 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 5–5 页。

关系：KGP method —EVALUATED_ON→ MD-QA dataset

Claim：`cb5e881e87364b31dc7e1619744e68bd0b04a345c8bcb58734a3e6214ba7d8d5`；Chunk：`chunk_84038d4c6f7949959af0974d04ee2379`。

原文引句：

> for our proposed KGP
> method for MD-QA.

决定理由：实体类型错误：MD-QA dataset是未具名任务类别，且引句只陈述方法用途。

## 88 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 5–6 页。

关系：KGP —EVALUATED_ON→ different baselines

Claim：`ca381432b81a3fd5105ce41fd000f097f31c8926927c2ad6a5e595c2ff7219d0`；Chunk：`chunk_b926195b594b5226494ac67d3237e329`。

原文引句：

> How well does KGP perform MD-QA
> compared with existing baselines?

决定理由：实体类型错误：different baselines是比较方法集合，不是Dataset。

## 89 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KGP-T5 —EVALUATED_ON→ HotpotQA

Claim：`8c18ce5594ae4f910274934b0fecd198da3b0c9c576da3fb4fc7d5868e807dc6`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：主体归属不足：引句说all baselines，而KGP-T5是本文提出方法，不能据此直接绑定。

## 90 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KGP-T5 —EVALUATED_ON→ IIRC

Claim：`b5a1122fdb9742499742b677a4c642c37ef503619b25779c231ec8aaf639fb97`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：主体归属不足：引句说all baselines，而KGP-T5是本文提出方法，不能据此直接绑定。

## 91 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：MDR —EVALUATED_ON→ HotpotQA

Claim：`7cc895a1d02c11a3fbdb82a97ca3750ae170120a8b2576fc2458d05a3bdd780c`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：来源明确将MDR列为被比较基线，并陈述这些基线在HotpotQA与IIRC的评测差异。

## 92 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：MDR —EVALUATED_ON→ IIRC

Claim：`b01f29fd3dc0a612a3309939c89a07facd5abc5b04ea75aecde907c41de68b15`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：来源明确将MDR列为被比较基线，并陈述其在IIRC的评测；不主张跨数据集优劣普适。

## 93 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：DPR —EVALUATED_ON→ HotpotQA

Claim：`ba3b5f955771d3353bffe92f4d0525d3ec7856ea4a4c573e3fef8eee5b01a315`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：来源明确DPR为比较基线，随后报告全体基线在HotpotQA/IIRC的表现。

## 94 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：DPR —EVALUATED_ON→ IIRC

Claim：`6cb360acc57f99c4753e9ee71f6664110a3e5240ab6d2cf1aff25a66e1bf8a56`；Chunk：`chunk_ee213298980e063a4877d996dcfff281`。

原文引句：

> By comparing
> the MD-QA performance across different datasets, we find
> that all baselines perform better on HotpotQA than on IIRC.

决定理由：来源明确DPR为比较基线，随后报告全体基线在IIRC的表现。

## 95 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KNN-MDR —IMPROVES_UPON→ KNN-ST

Claim：`8257b1fc165a421437386e03d94fb659e2a5821326dbb3fce2bf73dfb6487fd1`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> KNN-MDR achieves better performance
> than KNN-ST when the density of the two constructed KGs
> is the same.

决定理由：关系混淆：相同密度下KNN-MDR成绩更好不证明继承KNN-ST。

## 96 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：TAGME —EVALUATED_ON→ MD-QA

Claim：`218809372f27db47a8adf0352e1e29c3c1f4e1a7a27b510bfcc950c06000566d`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> studying its impact on the performance and the neighbor
> matching time of MD-QA using KGP-T5.

决定理由：实体类型错误：MD-QA是任务，system_inference也无法补出具名Dataset。

## 97 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KNN-MDR —ADDRESSES→ Neighbor matching efficiency

Claim：`bc4187307e52a42ba7e381a342ac5c05b1ad7433a353790f4de202ce315aa910`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> the neighbor matching efficiency decreases as the
> candidate pool, i.e., Nj in Eq (1), increases.

决定理由：证据不足：效率随候选池下降是观测，未证明KNN-MDR解决此问题。

## 98 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KNN-ST —ADDRESSES→ Neighbor matching efficiency

Claim：`e725afe0fe8f5d6a79dc7848556da244ea9f0e96c0e697e967f15e50aab9c05e`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> the neighbor matching efficiency decreases as the
> candidate pool, i.e., Nj in Eq (1), increases.

决定理由：证据不足：效率随候选池下降是观测，未证明KNN-ST解决此问题。

## 99 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KNN-MDR —ADDRESSES→ KG density

Claim：`776cbab71640f2f914491fef8a7bc0f611de3bd4376cbfad96abf2312f3b6dd2`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> As evidenced
> in Figure 6, we observe a similar trend, i.e., as KG density
> increases, the F1/EM increases and stays stable while the
> latency for selecting the most promising neighbors to visit
> next also increases.

决定理由：关系不支持：图密度与分数/延迟权衡不等于KNN-MDR解决KG density问题。

## 100 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 6–6 页。

关系：KNN-ST —ADDRESSES→ KG density

Claim：`973e06102c4d5ab8ea73ab3c1fd3425a6ef20506fbcfc948cf880b6372640a68`；Chunk：`chunk_3ba8d13b3fdeb6b301aa9aa15f1315d1`。

原文引句：

> As evidenced
> in Figure 6, we observe a similar trend, i.e., as KG density
> increases, the F1/EM increases and stays stable while the
> latency for selecting the most promising neighbors to visit
> next also increases.

决定理由：关系不支持：图密度与分数/延迟权衡不等于KNN-ST解决KG density问题。

## 101 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 7–7 页。

关系：Random agent —ADDRESSES→ Collecting irrelevant passages during graph traversal

Claim：`580f0037155c4beaeb56f697c851558607e9efb811679631c6f4c051c9627374`；Chunk：`chunk_0498eae1a386ebf0d6d488dedfd6381d`。

原文引句：

> Because the random
> agent only blindly traverses the KG without any guidance
> from LLM, it unavoidably collects irrelevant passages and
> hence achieves the worst performance than others under
> LLMs’ guidance.

决定理由：语义反转：random agent收集无关片段且表现差，没有解决这一问题。

## 102 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 7–7 页。

关系：KGP —IMPROVES_UPON→ TF-IDF

Claim：`808c997d55419f3dd831d8518d0bccebdd737e7eff764b26c8f9ffe571e480e2`；Chunk：`chunk_e1a39884458dd5c4e4ae63ae1126a5d5`。

原文引句：

> TF-IDF is slightly faster
> than KGP because it is a purely heuristic-based method.

决定理由：关系不支持：TF-IDF更快的对比既非KGP胜出，也非技术继承。

## 103 · 批准

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 11–11 页。

关系：MDR —EVALUATED_ON→ HotpotQA

Claim：`3ea6b72a2af77f1a26254bdb4692c6294763900b88e24e6e796d88b004f20699`；Chunk：`chunk_493cae01f9aa8bd905c9df0bc48019a8`。

原文引句：

> We limit the search
> depth to 2 as answering questions in HotpotQA requires
> at most 2-hop reasoning steps (Xiong et al. 2020).

决定理由：来源MDR专属条目说明在HotpotQA上采用深度2的检索配置，支持评测用途。

## 104 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 11–11 页。

关系：IRCoT —IMPROVES_UPON→ IR-CoT code (Trivedi et al. 2022a)

Claim：`abf5458bd881eaba3312c353f383621230f81f5af2af7477b2fbd0dfd1584f61`；Chunk：`chunk_493cae01f9aa8bd905c9df0bc48019a8`。

原文引句：

> Instead of directly employing the original IR-
> CoT code (Trivedi et al. 2022a), we modify it based
> on our problem setting.

决定理由：配置不明确：本文修改的IRCoT实现与原始代码需要区分，不能把同名方法写成自我继承。

## 105 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 13–13 页。

关系：KNN-MDR —IMPROVES_UPON→ KNN-ST

Claim：`fed2319de7ef44f5baa5c9e3bf6c1a991847e3649f92db91aedd4f47101cf8a0`；Chunk：`chunk_d9eb528a051dc54a057f53f0af7fe0e6`。

原文引句：

> However, on MuSiQue, KNN-MDR achieves the
> worst trade-off between Precision and SF-EM compared
> with KNN-ST and TF-IDF.

决定理由：语义反转且关系混淆：原文说KNN-MDR权衡最差，不支持改进KNN-ST。

## 106 · 拒绝

论文：Knowledge Graph Prompting for Multi-Document Question Answering；PDF 13–13 页。

关系：KNN-MDR —ADDRESSES→ Quality of KG on MuSiQue

Claim：`1bb9a8a391a70d58813bf3e51f12e395ab872688154e50c8e1dd44af52d614be`；Chunk：`chunk_d9eb528a051dc54a057f53f0af7fe0e6`。

原文引句：

> The general
> trend is similar to the one in Figure 5, i.e., as the graph
> becomes denser, the precision decreases while the SF-EM
> increases. However, on MuSiQue, KNN-MDR achieves the
> worst trade-off between Precision and SF-EM compared
> with KNN-ST and TF-IDF.

决定理由：证据不支持解决：原文报告密度权衡及KNN-MDR较差结果，不证明解决MuSiQue图质量。

## 107 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 2–3 页。

关系：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs —IMPROVES_UPON→ existing methods in RAG

Claim：`11fc3a7abdad489e339f76d0c9276c51b790643def84553679b27f70c1d0a54d`；Chunk：`chunk_138af1a69359eb7561c5d06fe25de0c0`。

原文引句：

> Our approach uses planning
> data from KGs to facilitate more efficient RAG.

决定理由：对象泛化与关系混淆：更有效RAG不证明对existing methods的技术继承。

## 108 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 2–3 页。

关系：existing methods in RAG —EVALUATED_ON→ QA tasks where answers are directly sourced from KGs

Claim：`970a783c17d739797aacccf96849b592ac99a0554c3cbb91854320421027b1f4`；Chunk：`chunk_138af1a69359eb7561c5d06fe25de0c0`。

原文引句：

> While aiding in KGQA
> tasks where answers are directly sourced from

决定理由：实体类型错误：答案来自KG的QA任务不是具体Dataset，句子还被截断。

## 109 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 2–3 页。

关系：existing methods in RAG —COMPARES_WITH→ Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs

Claim：`e3855487c30fb1dde5a1319a0f655759db60fa25f645bde4a8642dddc8d6b861`；Chunk：`chunk_138af1a69359eb7561c5d06fe25de0c0`。

原文引句：

> Our approach uses planning
> data from KGs to facilitate more efficient RAG.

决定理由：证据不足：介绍自身使用KG规划数据，没有具体对照方法或比较行为。

## 110 · 批准

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 5–6 页。

关系：LPKG —EVALUATED_ON→ CLQA-Wiki

Claim：`ae6b2ff89cf717ddddf3a09c55a16e63d688c17e1b355475f090d3dec950caa8`；Chunk：`chunk_b5d503a2d2586e2d55d4e0841114a942`。

原文引句：

> Finally, we conduct
> testing on our benchmark CLQA-Wiki.

决定理由：来源实验设置与RQ4明确LPKG在自建CLQA-Wiki上测试；只确认评测事实。

## 111 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 6–6 页。

关系：Direct —COMPARES_WITH→ Framework proposed in the paper

Claim：`5e241f5c99fd3842982b26c9601ed1f43404aff495e80619249781112edd1970`；Chunk：`chunk_c29b1beb1a7c48f679fa8aa27e231137`。

原文引句：

> We compare our framework to various
> baselines: • Direct: Directly input the original
> question into LLM.

决定理由：实体不具体：Framework proposed in the paper未解析为LPKG，不能作为稳定方法节点。

## 112 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 7–7 页。

关系：CodeQwen1.5-7B-Chat —IMPROVES_UPON→ GPT-3.5

Claim：`e766a25bdab1771e8efa2b7f0472433c003554c7be5e3cfb8a0152a368294c87`；Chunk：`chunk_bca043f33502bdedb273cd4b0ffe1769`。

原文引句：

> CodeQwen1.5-7B-Chat,
> which is significantly inferior to GPT-3.5 across
> all datasets in planning ability before fine-tuning,
> exhibits a notable enhancement after fine-tuning
> on KG-based planning data, especially achieving
> better results than GPT-3.5 on 2WikiMQA and
> MuSiQue.

决定理由：关系混淆且配置丢失：KG微调后部分数据集胜过GPT-3.5不证明CodeQwen继承它。

## 113 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 8–8 页。

关系：fine-tuning using planning data from KG —IMPROVES_UPON→ fine-tuning using planning data distilled from GPT-3.5

Claim：`53e45b0f471aa0aad6db34315458b0383b8dd80c534ee777c56ade72f0d3359c`；Chunk：`chunk_231843bdac931319ba29f46e6be14d6d`。

原文引句：

> using planning data con-
> structed from KG yields better performance than
> using planning data distilled from GPT-3.5.

决定理由：关系混淆：两种规划数据来源的分数差不是技术继承。

## 114 · 批准

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 8–8 页。

关系：LPKG with Llama3 —EVALUATED_ON→ CLQA-Wiki benchmark

Claim：`d4b07cce3b16499f2366de27ec84d3d119aa906812e04edf601b092381fa2dad`；Chunk：`chunk_231843bdac931319ba29f46e6be14d6d`。

原文引句：

> We then conduct testing based on
> the CLQA-Wiki benchmark.

决定理由：来源RQ4明确CLQA-Wiki实验仅用LPKG with Llama3，支持该配置的评测关系。

## 115 · 拒绝

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 8–8 页。

关系：LPKG with Llama3 —IMPROVES_UPON→ CodeQwen1.5-7B-Chat

Claim：`9bfa674a53bb8fed52f0cc6909770cc7ae57a0b7749256c38dc0a45bf7ef1435`；Chunk：`chunk_231843bdac931319ba29f46e6be14d6d`。

原文引句：

> Since Llama3-8B-Instruct is more powerful than
> CodeQwen1.5-7B-Chat as shown in Table 2, we
> only conduct LPKG with Llama3 here.

决定理由：关系混淆：Llama3更强的模型比较不证明LPKG with Llama3继承CodeQwen。

## 116 · 批准

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 8–8 页。

关系：LPKG(Llama3) —ADDRESSES→ complex logic questions

Claim：`720b8bd51b60044182e185cc7d4da898e9c2f7ec71e62768685567b57bcd376e`；Chunk：`chunk_7d8a9ac9d054b8b2a730410c6aafbaec`。

原文引句：

> LPKG(Llama3) performs more prominently
> on some complex questions, such as the 3p, 2i, and
> 2u questions

决定理由：来源明确LPKG(Llama3)用于3p/2i/2u复杂逻辑问题并给出实验结论；不推广到全部逻辑题。

## 117 · 批准

论文：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 8–8 页。

关系：LPKG(Llama3) —ADDRESSES→ 2i questions

Claim：`c2d5e3789ab51bc5508caddfe41512e08d9b46b8c3cb8b344f4ecb2f9ccb98b7`；Chunk：`chunk_7d8a9ac9d054b8b2a730410c6aafbaec`。

原文引句：

> LPKG(Llama3) could identify it as a
> 2i question and provide the correct sub-questions
> and planning steps, thereby helping to obtain the
> correct answer during final parsing and execution.

决定理由：案例明确LPKG(Llama3)识别2i问题并生成正确子问题/规划；仅确认其处理此类问题的用途。

## 118 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 4–5 页。

关系：MindMap —IMPROVES_UPON→ previous retrieval-augmented LLMs

Claim：`5fccea7a25fb4794f66b332a33c3d7a421f2a7400db8b628bcaf5619ad22a091`；Chunk：`chunk_8ef1b4863836f1f958a83a3660b9aae9`。

原文引句：

> We find that previous retrieval-augmented LLMs
> tend to rephrase the retrieved facts without ex-

决定理由：证据不足：引句截断在对前人方法的描述，未建立MindMap的改进继承。

## 119 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 4–5 页。

关系：MindMap —EVALUATED_ON→ GenMedGPT-5k, CMCQA, ExplainCPE

Claim：`53699c3c7d3a20aae4122c243e3584d93d8d48f12e155b62f018c203eb4cbc11`；Chunk：`chunk_8ef1b4863836f1f958a83a3660b9aae9`。

原文引句：

> Table 1: The statistics of the used datasets.

决定理由：复合Dataset：三个数据集合并成单节点，且引句只是统计表标题。

## 120 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 4–5 页。

关系：MindMap —EVALUATED_ON→ EMCKG, CMCKG

Claim：`eef2f35b75368a9502c738e586e4e5805adfdf2c99df4ec200917fd6e19ae75f`；Chunk：`chunk_8ef1b4863836f1f958a83a3660b9aae9`。

原文引句：

> Table 1: The statistics of the used datasets.

决定理由：复合实体且角色含混：两个KG集合并成Dataset节点；表题不足以支持评测。

## 121 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–5 页。

关系：MindMap —COMPARES_WITH→ BM25 retriever, Text Embedding retriever, and KG retriever

Claim：`6183a85f77aae563d7d4a464b22c49cccba0fb92c687a7dabc118b2d297a9c12`；Chunk：`chunk_c36c0155590c0da356beed7403c524ae`。

原文引句：

> Additionally, we consider three
> retrieval-augmented baselines: BM25 retriever,
> Text Embedding retriever, and KG retriever, see
> instruction details in Appendix D.

决定理由：复合Method：把BM25、Embedding和KG三种基线合为一个实体，需拆分后另审。

## 122 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–5 页。

关系：Evaluation Metrics —EVALUATED_ON→ GenMedGPT-5K answers in the medical domain questions

Claim：`50a6a0b1ad19b67e09aca84e87170d55721da99b953d9658f89221d4f80eb0e9`；Chunk：`chunk_05cb7a010c4bfc94987b28747217fd98`。

原文引句：

> We used GenMedGPT-5K to test how LLMs deal
> with question-answering in the medical domain,
> where LLMs need to answer with disease diagnosis,
> drug recommendation, and test recommendation.

决定理由：主体类型错误：Evaluation Metrics是小节/评测概念，不是接受测试的方法。

## 123 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —EVALUATED_ON→ GenMedGPT-5k

Claim：`d461e2696bd916896b9214439f86a9e38cf313311e8fac924185971ebcf159d7`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> on GenMedGPT-5k.

决定理由：引句过短：仅on GenMedGPT-5k不能单独支持完整关系；原表有信息但需重新选完整引句。

## 124 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —EVALUATED_ON→ CMCQA dataset

Claim：`c248d2063a6cc9f9ed139dca67e896bd0c4dca4169487143c4fabb829568dc51`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> for CMCQA dataset.

决定理由：引句过短：仅for CMCQA dataset无法单独支撑MindMap评测关系；保留后续完整表注候选。

## 125 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —COMPARES_WITH→ GPT-3.5

Claim：`d854fdc7c10e41f7900952574cbc9dc11a62d2fe95ab64fa43eb43f367b97507`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> GPT-3.5

决定理由：引句仅一个模型名，不支持两方法的比较行为，系统推断不能替代完整证据。

## 126 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —COMPARES_WITH→ BM25 Retriever

Claim：`de513e5d7d30c7620170e19a048c51455ceba8164166fde04668722eef462b46`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> BM25 Retriever

决定理由：引句仅BM25名称，未包含MindMap或比较关系，需选完整表注。

## 127 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —COMPARES_WITH→ Embedding Retriver

Claim：`697a3ed7b90d765a761c9d082f17e3b57608adc44713dd0e6089797e13e18cd1`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> Embedding Retriever

决定理由：端点拼写错误Retriver且引句仅方法名称，不能批准原样候选。

## 128 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —COMPARES_WITH→ KG Reriever

Claim：`a49929a0d6514110365d8e1469ce928cfd85d835e30c73033f19a5c5119a34fe`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> KG Retriever

决定理由：端点拼写错误Reriever且引句仅方法名称，不能批准原样候选。

## 129 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 5–6 页。

关系：MindMap —COMPARES_WITH→ GPT-4

Claim：`6cb3aba19759b983defcfaf41938035eac6fc2ad663980d2d9a6a6071c6ff94b`；Chunk：`chunk_59c68c408db03a2f73445795e7c57c73`。

原文引句：

> GPT-4

决定理由：引句仅GPT-4名称，不支持两方法比较关系。

## 130 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：MindMap —IMPROVES_UPON→ BERTScore

Claim：`a3c315fe9de66b80bea7a4de3288a25a9b524575b8c7fe7485faf70f93e920d3`；Chunk：`chunk_65cf7f8bc35a3052eb4e0d1773d09507`。

原文引句：

> While BERTScore
> shows similar results among methods, MindMap
> exhibits a slight improvement, possibly due to the
> shared tone in medical responses.

决定理由：实体类型与关系错误：BERTScore是指标，不能作为被MindMap技术改进的方法。

## 131 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：MindMap —IMPROVES_UPON→ KG Retriever

Claim：`6c28cc1ecc4933d34a7330742eb15345bd99c8ccd30070e426bba059c464f1ea`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> MindMap still outshines all retrieval-based meth-
> ods, including KG Retriever.

决定理由：关系混淆：结果优于KG Retriever不证明继承该方法。

## 132 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：MindMap —ADDRESSES→ robustness of MindMap concerning the factual correctness of KG

Claim：`73de103fcb00aa6ebf50eda1f0e9605ff2762155875ef7131aa602d61bd0141f`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> In addressing the robustness of MindMap concern-
> ing the factual correctness of KG, we leverage
> the identical KG dataset employed in the second
> dataset - ExplainPE.

决定理由：证据只说明要考察鲁棒性，未证实MindMap解决KG事实正确性问题。

## 133 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：MindMap —EVALUATED_ON→ identical KG dataset employed in the second dataset - ExplainPE

Claim：`94df3573c66e0e78483cf1676de5c81089028987cdff140a9e4e01a1466412d8`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> In addressing the robustness of MindMap concern-
> ing the factual correctness of KG, we leverage
> the identical KG dataset employed in the second
> dataset - ExplainPE.

决定理由：Dataset身份不明确：客体是关系性描述而非规范具名数据集，ExplainPE也需消歧。

## 134 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：MindMap —EVALUATED_ON→ accuracy of the generated choice and the quality of the explanations

Claim：`4d3dd759abab9edc02fade85394ec239edf46c83db28d8e2dd384e8b7df7e491`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> We evaluate all methods based on the accuracy of
> the generated choice and the quality of the expla-
> nations.

决定理由：实体类型错误：答案准确率与解释质量是指标，不是Dataset。

## 135 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：GPT-4 —EVALUATED_ON→ accuracy of the generated choice and the quality of the explanations

Claim：`324c43d220d84a4baa4d5ff80a0ded0c1d544a319ae381641542f6dfaac7a694`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> We evaluate all methods based on the accuracy of
> the generated choice and the quality of the expla-
> nations.

决定理由：实体类型错误：答案准确率与解释质量是指标，不是Dataset。

## 136 · 拒绝

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–6 页。

关系：GPT-4 —EVALUATED_ON→ BERTScore and GPT-4 ranking for assessing explanation quality

Claim：`b53aab1ebfe95d6d51e78222129c169f2555c8de13ae9c050f51e6ec43a800a9`；Chunk：`chunk_c5f5d6aafa2e2a3f895d9c4588961777`。

原文引句：

> For assessing explanation quality, we use
> BERTScore and GPT-4 ranking.

决定理由：实体类型错误：BERTScore与GPT-4排名是评估方式，不是Dataset。

## 137 · 批准

论文：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 6–7 页。

关系：MindMap —EVALUATED_ON→ CMCQA

Claim：`30814aa95197f1de5cb0efe9ff19c123a214b35afd029895f16299b0a55bb330`；Chunk：`chunk_91ab4f17396428b71094655d96c29bb6`。

原文引句：

> Table 5: The pair-wise comparison by GPT-4 on the winning rate of MindMap v.s. baselines on disease diagnosis
> and drug recommendation on CMCQA.

决定理由：完整Table 5表注明确MindMap与基线在CMCQA上评测；只接受数据集关系，不采用GPT-4评判分数作为本项目验证。

## 138 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 1–1 页。

关系：RoG —IMPROVES_UPON→ existing KG-based LLM reasoning methods

Claim：`c0e7a0924d20c3a17a7fd67221a7d5a2971986e2d5cebbfee28ae6c2306741b6`；Chunk：`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

原文引句：

> Nevertheless, existing KG-based LLM reasoning
> methods only treat KGs as factual knowledge bases and overlook the importance
> of their structural information for reasoning.

决定理由：对象泛化且关系不支持：前人忽略结构信息并不证明RoG从具体前人方法继承。

## 139 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 2–2 页。

关系：planning-retrieval-reasoning framework —EVALUATED_ON→ two benchmark KGQA datasets

Claim：`b4ec31c43662951b04f11d5d60bec68e7644f958886ab0df139bd22f5a2c8d60`；Chunk：`chunk_8d1de153f62070216bf23df5989bda21`。

原文引句：

> We conduct extensive experiments on two benchmark KGQA datasets,
> and the results demonstrate that RoG achieves state-of-the-art performance on KG reasoning tasks
> and generates faithful and interpretable reasoning results.

决定理由：Dataset不具体：two benchmark KGQA datasets是数量描述，不是单一数据集。

## 140 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 2–2 页。

关系：RoG —IMPROVES_UPON→ different LLMs during inference

Claim：`6bd56fb04445ac4194dce5689729f99e079bd6898e00e94cad70b585a3e0e8aa`；Chunk：`chunk_8d1de153f62070216bf23df5989bda21`。

原文引句：

> Moreover, the planning module of RoG
> can be plug-and-play with different LLMs during inference to improve their performance.

决定理由：对象不具体且关系混淆：规划模块增强不同LLM不构成对某一具体方法的继承。

## 141 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 4–4 页。

关系：relation paths —ADDRESSES→ hallucination issues in LLMs leading to wrong answers

Claim：`77ec3b12a89332a1151b52035d2967f18a237e52fc560ed24d23ede62bfe67f4`；Chunk：`chunk_1a304dbb449afc8300e4e658f4306fd5`。

原文引句：

> By using relation paths,
> we can always retrieve the latest knowledge from KGs for reasoning. Therefore, relation paths can
> serve as faithful plans for reasoning the answer to KGQA task.

决定理由：主体类型含混：relation paths是结构化表示，不是明确命名方法；引句也未完整声称解决幻觉。

## 142 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 4–4 页。

关系：relation paths —EVALUATED_ON→ KGQA task

Claim：`f5ad1890de3a12565e3a38f3c2c999f607831e8c621f4907d221065769d09cfb`；Chunk：`chunk_1a304dbb449afc8300e4e658f4306fd5`。

原文引句：

> Therefore, relation paths can
> serve as faithful plans for reasoning the answer to KGQA task.

决定理由：实体类型错误：KGQA task是任务，relation paths不是具名完整方法。

## 143 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 4–4 页。

关系：relation paths —COMPARES_WITH→ dynamically updated entities in KGs

Claim：`955defbd37eaeb73b48914606b5b7c5ee07f60ad7467c2525c9553e896499d3e`；Chunk：`chunk_1a304dbb449afc8300e4e658f4306fd5`。

原文引句：

> Moreover, compared to the dynamically
> updated entities, the relations in KGs are more stable (Wang et al., 2023a). By using relation paths,
> we can always retrieve the latest knowledge from KGs for reasoning.

决定理由：实体类型错误：KG中动态实体不是Method，稳定性比较不是方法实验对照。

## 144 · 批准

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 4–5 页。

关系：minimizing the KL divergence with the posterior distribution of faithful relation paths Q(z) —ADDRESSES→ planning optimization

Claim：`31ef5f33fe5943e529aa70f71efdec2f79c22411e7fe8c4586d4d9caa4d675d7`；Chunk：`chunk_f045808d791542465c32f3e2a25c26c5`。

原文引句：

> Planning optimization. In planning optimization, we aim to distill the knowledge from KGs into
> LLMs to generate faithful relation paths as plans. This can be achieved by minimizing the KL
> divergence with the posterior distribution of faithful relation paths Q(z), which can be approximated
> by the valid relation paths in KGs.

决定理由：引句明确通过最小化KL散度把KG路径知识蒸馏进LLM，服务planning optimization；作为具体优化技术用途保留。

## 145 · 批准

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 4–5 页。

关系：maximizing the expectation that retrieval-reasoning module generates correct answers based on the relation paths and KGs —ADDRESSES→ retrieval-reasoning optimization

Claim：`73f197ad4076406a9c18ca5ffdbd3667625cd984ef17b11ee2c1bd60d2d05f4a`；Chunk：`chunk_f045808d791542465c32f3e2a25c26c5`。

原文引句：

> The former term maximizes the
> expectation that retrieval-reasoning module generates correct answers based on the relation paths
> and KGs (retrieval-reasoning optimization).

决定理由：引句明确最大化检索推理模块正确回答的期望用于retrieval-reasoning optimization；不主张性能优越性。

## 146 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 6–6 页。

关系：reasoning module —EVALUATED_ON→ Z∗K, G

Claim：`b7d5e88090452cf39fa5e4cb2b2c5c9f13a2b22e1efd49b4c636f8724fd9d9af`；Chunk：`chunk_0747f2e01aa5287eda70d13997604b5c`。

原文引句：

> arg max
> θ
> log Pθ(a|q, Z∗
> K, G) = log
> X
> z∈Z∗
> K
> X
> wz∈Wz
> |a|
> Y
> i=1
> Pθ(ti|t<i, q, wz),

决定理由：实体类型错误：公式变量Z与G不是Dataset，优化式不是评测证据。

## 147 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 7–7 页。

关系：RoG —EVALUATED_ON→ WebQSP

Claim：`730d1e093936cd3bb5df2162615904dad0a2ffb32b161c16808bc6fdfbb1f6b5`；Chunk：`chunk_2a54af5657f5157d4c806c5daace0980`。

原文引句：

> In this section, we compare RoG with other baselines on KGQA tasks. The results
> are shown in Table 1. Our method achieves the best performance on both datasets across most
> metrics.

决定理由：引句未标WebQSP；虽上下文有明确结果，当前保存引句不能独立支撑具体数据集，需补证据再抽取。

## 148 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 7–7 页。

关系：RoG —EVALUATED_ON→ CWQ

Claim：`b01514e9f1c9febb8648fd01ba929cf137ea3f74231ae5513d40289a376804e2`；Chunk：`chunk_2a54af5657f5157d4c806c5daace0980`。

原文引句：

> In this section, we compare RoG with other baselines on KGQA tasks. The results
> are shown in Table 1. Our method achieves the best performance on both datasets across most
> metrics.

决定理由：引句未标CWQ；虽上下文有明确结果，当前保存引句不能独立支撑具体数据集，需补证据再抽取。

## 149 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 7–8 页。

关系：retrieval-augmented approaches —IMPROVES_UPON→ conventional embedding-based methods

Claim：`4a53e8714c6b8de5dab510fbfe857265117aa19ea85a49aa1dc1114042be440f`；Chunk：`chunk_337b776419fe0d299cd973609da26513`。

原文引句：

> Among other methods, retrieval-augmented approaches outperform conventional embedding-based
> methods by retrieving relevant subgraphs from KGs, which reduces reasoning complexity.

决定理由：两个端点均为方法大类，且性能对比不证明技术继承。

## 150 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 7–8 页。

关系：LLMs+KGs methods —EVALUATED_ON→ WebQSP, CWQ

Claim：`8bbbc90039a2e77f15687786e059479ea02d31c732b7aef5a6367abb5a6e09c7`；Chunk：`chunk_337b776419fe0d299cd973609da26513`。

原文引句：

> The
> LLMs+KGs methods achieve the second-best performance, which demonstrates the effectiveness of
> unifying KGs and LLMs for reasoning.

决定理由：主体为方法集合且Dataset为两个数据集的复合节点，不能原样接纳。

## 151 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 7–8 页。

关系：LLMs+KGs methods —IMPROVES_UPON→ LLMs-based methods

Claim：`6ef9303c31b184f1a4caf9abf79ffef011584183c3eb4dafc91698cde0632f0c`；Chunk：`chunk_337b776419fe0d299cd973609da26513`。

原文引句：

> Although LLMs-based methods achieve comparable
> performance, they are limited by hallucinations and lack of knowledge as shown in Section 5.4.

决定理由：关系不支持：可比性能与LLM局限不能证明LLMs+KGs继承LLMs-based方法。

## 152 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–8 页。

关系：RoG w/o reasoning —IMPROVES_UPON→ RoG w/o planning

Claim：`9aa264515333fede50038aa0abc08f66f82f061e06976f7a4751d35ee832bdd1`；Chunk：`chunk_41f164dcc97380b68b515cce682cba4b`。

原文引句：

> RoG w/o reasoning
> 46.90
> 79.85
> 49.56
> 18.88
> 67.89
> 22.26

决定理由：证据仅孤立数值行，且消融性能比较不能写成技术继承。

## 153 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–8 页。

关系：RoG w/ vote reasoning —IMPROVES_UPON→ RoG w/o reasoning

Claim：`74194c9e8a9c227f5b48b80bc628c18e9dcc1be5ee1a833b54cb6a941add634b`；Chunk：`chunk_41f164dcc97380b68b515cce682cba4b`。

原文引句：

> RoG w/ vote reasoning
> 54.80
> 60.44
> 47.96
> 22.92
> 47.98
> 26.52

决定理由：证据仅孤立数值行，且投票推理与移除推理的比较不能写成技术继承。

## 154 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–8 页。

关系：RoG w/ planning —EVALUATED_ON→ WebQSP

Claim：`7a126205a14261d5c005550368368e17d43d307be3b9d44fb8157e9941779c51`；Chunk：`chunk_41f164dcc97380b68b515cce682cba4b`。

原文引句：

> ChatGPT + RoG Planning
> 81.51
> 71.60
> 52.68
> 48.51

决定理由：主体配置错配：引句ChatGPT+RoG Planning不能抽象成RoG w/planning；还缺数据集表头。

## 155 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–8 页。

关系：RoG w/ planning —EVALUATED_ON→ CWQ

Claim：`36c124025c2446026203237c0d16a1a89048a7ee867bcfc87da71ded2692b9bf`；Chunk：`chunk_41f164dcc97380b68b515cce682cba4b`。

原文引句：

> Alpaca-7B + RoG Planning
> 56.16
> 74.20
> 44.04
> 38.46

决定理由：主体配置错配：引句Alpaca+RoG Planning未保留模型条件；还缺数据集表头。

## 156 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–9 页。

关系：integrating the planning module of RoG with different LLMs during inference —EVALUATED_ON→ Table 3

Claim：`f57a680430e8a96bbfe1305066378c5fd65654080b833ef176d980c7fae3b689`；Chunk：`chunk_0f20a533abc64e441acfeb96ebf313e2`。

原文引句：

> The results are presented in Table 3.

决定理由：实体类型错误：Table 3是引用定位，不是Dataset。

## 157 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 8–9 页。

关系：integrating the planning module of RoG with different LLMs during inference —ADDRESSES→ extracting the number of answers from LLM’s output

Claim：`e8a7e866edb1071f89fc6ef413f36dab1ea74290165fc87720c6b660db08290c`；Chunk：`chunk_0f20a533abc64e441acfeb96ebf313e2`。

原文引句：

> To
> account for the fact that it is difficult to extract
> the number of answers from LLM’s output. We
> only report the Hits@1 and Recall metrics.

决定理由：语义错配：因难提取答案数而仅报告指标，不是规划模块解决答案计数问题。

## 158 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 9–9 页。

关系：RoG —IMPROVES_UPON→ ChatGPT+CoT

Claim：`5d24f1b12c7fec16f56486b415b7809e8eef19fe2c5dad25770f2054414c7837`；Chunk：`chunk_7d9e24b10c382d84f416c7e5d421edb4`。

原文引句：

> In Table 4, we can
> find that ChatGPT+CoT suffers from the lack of knowledge issue and cannot answer the question.
> On the contrary, RoG can generate faithful relation paths and retrieve valid reasoning paths from
> KGs for reasoning.

决定理由：关系混淆：个别案例显示检索优势不证明RoG继承ChatGPT+CoT。

## 159 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 9–9 页。

关系：RoG —IMPROVES_UPON→ ChatGPT+CoT

Claim：`62044ddfdde5bf5f6cf86b3a750823e2e6710ac5dd82d0aa8cdd763c8627d11b`；Chunk：`chunk_7d9e24b10c382d84f416c7e5d421edb4`。

原文引句：

> In Table 5, we can see that ChatGPT+CoT suffers from hallucinations and generates incorrect
> answers. In contrast, although the retrieved reasoning paths contain noises, the reasoning module
> can identify the correct reasoning paths and conduct faithful reasoning.

决定理由：关系混淆：案例避免幻觉不证明RoG继承ChatGPT+CoT。

## 160 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 19–19 页。

关系：UniKGQA (Jiang et al., 2022) —EVALUATED_ON→ KGQA tasks

Claim：`4c128eeb293192b81bc2fd6733530db1cc9c8a99536bb37265c25c964a2e6e63`；Chunk：`chunk_c06b25ada7bf3b7a3e3fbae04ecc161f`。

原文引句：

> UniKGQA (Jiang et al., 2022) unifies the graph retrieval and reasoning process into a single
> model with LLMs, which achieves state-of-the-art performance on KGQA tasks.

决定理由：实体类型错误：KGQA tasks是任务类别，不是具体Dataset。

## 161 · 批准

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG finetuned from scratch —EVALUATED_ON→ MetaQA-3hop dataset

Claim：`ce888380eb20f5e0bf5f6e329ed627b6bfb745179495a69492c9c345b23ef981`；Chunk：`chunk_f5c88d605f651f26c093f30b836a98aa`。

原文引句：

> We select the MetaQA-3hop dataset (Zhang
> et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split
> and utilize two training strategies to finetune RoG: 1) training from scratch, where we directly train
> RoG from LLaMA2-Chat with 1000 samples; 2) transfer from Freebase, where we conduct a further
> finetuning based on RoG trained for Freebase. The results are shown in Table 12.

决定理由：来源明确MetaQA-3hop上从LLaMA2-Chat训练RoG并在Table 12报告结果，保留1000训练样本条件。

## 162 · 批准

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG transfer from Freebase —EVALUATED_ON→ MetaQA-3hop dataset

Claim：`eb5cdb983e1d4d9e7a0b882a26ae5bbf41d5690fc1360b4a068f952341f131ad`；Chunk：`chunk_f5c88d605f651f26c093f30b836a98aa`。

原文引句：

> We select the MetaQA-3hop dataset (Zhang
> et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split
> and utilize two training strategies to finetune RoG: 1) training from scratch, where we directly train
> RoG from LLaMA2-Chat with 1000 samples; 2) transfer from Freebase, where we conduct a further
> finetuning based on RoG trained for Freebase. The results are shown in Table 12.

决定理由：来源明确把Freebase训练后的RoG迁移到MetaQA-3hop并报告结果，支持目标数据集评测关系。

## 163 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG transfer from Freebase —IMPROVES_UPON→ RoG finetuned from scratch

Claim：`53906db01e5cfa0d006e972fa565b8d85a950bcb2c60b65f96d8ea6142f88092`；Chunk：`chunk_f5c88d605f651f26c093f30b836a98aa`。

原文引句：

> From results, we
> can see that transfer from Freebase achieves better performance than training from scratch, which
> demonstrates the transferability of RoG to other KGs.

决定理由：关系混淆：迁移训练胜于从头训练是策略对比，不是方法技术继承。

## 164 · 批准

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG —EVALUATED_ON→ MetaQA-3hop dataset

Claim：`4ec95a19a79311c58a68e54e1b0f54a2968e6afc51da1c48e4b15bfe9071a7bd`；Chunk：`chunk_f5c88d605f651f26c093f30b836a98aa`。

原文引句：

> We select the MetaQA-3hop dataset (Zhang
> et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split
> and utilize two training strategies to finetune RoG: 1) training from scratch, where we directly train
> RoG from LLaMA2-Chat with 1000 samples; 2) transfer from Freebase, where we conduct a further
> finetuning based on RoG trained for Freebase. The results are shown in Table 12.

决定理由：同一来源明确RoG两种训练设置的MetaQA-3hop评测；不把训练来源Freebase误作目标Dataset。

## 165 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG transfer from Freebase —EVALUATED_ON→ Freebase

Claim：`52571fc62c9adaef6e18dad143c930e1488f137d426d927ea627738a5952643e`；Chunk：`chunk_f5c88d605f651f26c093f30b836a98aa`。

原文引句：

> We select the MetaQA-3hop dataset (Zhang
> et al., 2018) which is based on Wiki-Movies KGs. We select 1000 samples from the training split
> and utilize two training strategies to finetune RoG: 1) training from scratch, where we directly train
> RoG from LLaMA2-Chat with 1000 samples; 2) transfer from Freebase, where we conduct a further
> finetuning based on RoG trained for Freebase. The results are shown in Table 12.

决定理由：角色错误：Freebase是迁移训练来源KG，该引句的目标评测集是MetaQA-3hop。

## 166 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG trained on single dataset —EVALUATED_ON→ WebQSP or CWQ datasets

Claim：`d625597747a618c3bf9849d110edf473f137a1aa4b74ca8f5c6413c73bf9b749`；Chunk：`chunk_c56673127e6033eeeee53e2b317aac94`。

原文引句：

> we finetune RoG jointly on the training set of both WebQSP and CWQ datasets to
> maximize the ability of RoG for reasoning on Freebase. To fairly compare with other methods (e.g.,
> UniKGQA (Jiang et al., 2022)) that are only trained on single dataset, we provide additional results
> of the performance of RoG trained on single dataset.

决定理由：复合Dataset：WebQSP or CWQ未拆分，且引句偏向训练设置而非具体测试关系。

## 167 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 20–20 页。

关系：RoG trained on multiple datasets —IMPROVES_UPON→ RoG trained on single dataset

Claim：`e5b47f5f58984d3d18b240c13d72d3048b054c3c994f810a2f06ae00b8480755`；Chunk：`chunk_c56673127e6033eeeee53e2b317aac94`。

原文引句：

> we can also find that jointly training RoG on multiple datasets can further improve the
> performance.

决定理由：关系混淆：联合训练提高表现不构成对单集训练方法的技术继承。

## 168 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 23–23 页。

关系：location.location.people born here —ADDRESSES→ people.person.place of birth

Claim：`fd7d868509cf7cc1703390d33ca66db0e2b9016d7e5fa5e62bcfab31884e2a90`；Chunk：`chunk_b939a8cc38623112fef4180acd2b209f`。

原文引句：

> z1 : location.location.people born here
> z2 : people.person.place of birth

决定理由：实体类型错误：两个KG关系谓词不是Method和Problem，映射关系也非ADDRESSES。

## 169 · 拒绝

论文：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 23–23 页。

关系：sports.sports championship event.champion —ADDRESSES→ sports.mascot.team →sports.sports team.championships

Claim：`15380900171dcd819d05d19962ea4d5eef9b77047315e1ea1a063494d02f19d6`；Chunk：`chunk_b939a8cc38623112fef4180acd2b209f`。

原文引句：

> z1 : sports.mascot.team →sports.sports championship event.champion
> z2 : sports.mascot.team →sports.sports team.championships

决定理由：实体类型错误：图谱路径/谓词不是方法与问题实体。

## 170 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 2–3 页。

关系：STaRK benchmarking pipeline —EVALUATED_ON→ three SKBs built from extensive texts and millions of entity relations from public sources

Claim：`eee3daa646690be958d04fb07bab6fc1ad7a4f82048b373321a66e974b76ddd9`；Chunk：`chunk_d2b23cd8bdf5bc8999476417e6019f5b`。

原文引句：

> We develop a novel pipeline that simulates user queries and constructs precise ground truth answers
> using three SKBs built from extensive texts and millions of entity relations from public sources.

决定理由：复合Dataset且阶段角色错误：三SKB用于基准构建，不是具名单一评测集。

## 171 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 3–3 页。

关系：STaRK —EVALUATED_ON→ Semi-structured Knowledge Bases

Claim：`b3798792250857d0ace2ad2bbfd93030e56437c019abb57ce0f6b6ca6ffa1e97`；Chunk：`chunk_77331dc18e1518cd0c883724d737af4f`。

原文引句：

> Figure 2: Demonstration of Semi-structured Knowledge Bases, where each knowledge base combines
> both textual and relational information in a complex way, making the retrieval tasks challenging.

决定理由：对象不具体：Semi-structured Knowledge Bases是知识库类别，图示不构成方法评测。

## 172 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 3–3 页。

关系：STaRK —IMPROVES_UPON→ LLM retrieval systems

Claim：`40b92a37854cb79bf5a9db948b2ce1390b6b8bc00ba586411c5204cc490bb309`；Chunk：`chunk_77331dc18e1518cd0c883724d737af4f`。

原文引句：

> We conduct extensive experiments on LLM retrieval systems, highlighting challenges in handling
> textual and relational data and latency on large-scale SKBs with millions of entities or relations.
> Finally, we offer insights into building more capable retrieval systems to handle real-world complexity.

决定理由：关系错误：基准用于揭示挑战，不是对LLM retrieval systems作技术继承。

## 173 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 7–7 页。

关系：LLM Rerankers: Claude3 and GPT-4 rerankers —IMPROVES_UPON→ ada-002 results

Claim：`44c7eb4418de280f1b09879cfc3de9b155d0ab5987f3cf6f85a01bdfcf65e9e4`；Chunk：`chunk_bb730573725b148aa7913e7f17bb9261`。

原文引句：

> These models improve the precision of
> top-k ada-002 results by reranking them using large language models.

决定理由：复合Method：Claude3与GPT-4重排器合并，客体ada结果是输出而非方法。

## 174 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 7–7 页。

关系：Hit@k —EVALUATED_ON→ random 10% sample of test queries

Claim：`6f9b6206a195d1bffbd2d17292be58eb7b774cd9ed0fcf05a4871b84ef066a8f`；Chunk：`chunk_bb730573725b148aa7913e7f17bb9261`。

原文引句：

> Due to high
> computational costs, we evaluate these rerankers on a random 10% sample of test queries.

决定理由：主体类型错误：Hit@k是评估指标，不是被测试的方法。

## 175 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 7–7 页。

关系：Hit@k —ADDRESSES→ accuracy of the top recommendation; at k = 5, it examines the model’s precision in a wider recommendation set.

Claim：`debb9537a8057021ea63fa740aa3bdc44707678a2eef4524ce9879699d7581b2`；Chunk：`chunk_bb730573725b148aa7913e7f17bb9261`。

原文引句：

> At k = 1, it evaluates the accuracy of the top recommendation; at
> k = 5, it examines the model’s precision in a wider recommendation set.

决定理由：指标不是解决研究问题的方法；将指标定义硬映射ADDRESSES会污染图谱。

## 176 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 7–7 页。

关系：Recall@k —ADDRESSES→ model’s ability to identify all relevant items, particularly in scenarios where missing any could be critical.

Claim：`b08158b6f270befb047d64a75a878f64dad925860c198b9326e528df10f44bf4`；Chunk：`chunk_bb730573725b148aa7913e7f17bb9261`。

原文引句：

> This metric offers insight into the model’s ability to identify all relevant items, particularly
> in scenarios where missing any could be critical.

决定理由：指标不是解决研究问题的方法；Recall@k定义不构成ADDRESSES语义。

## 177 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：BM25 —EVALUATED_ON→ full synthesized test sets and random 10% samples from these sets

Claim：`fbf393077abcfd5b51f4c47c5ab81371593d67107205be9e45f061dc26c31860`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> Table 6 presents the results on both the full synthesized test sets
> and random 10% samples from these sets. In both cases, BM25, despite its simplicity, proves to
> be a strong baseline, outperforming the dense retrieval models such as ANCE.

决定理由：Dataset不具体：full test sets及10%样本是划分描述，未明确STaRK具体子集。

## 178 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：finetuned DPR and QAGNN —IMPROVES_UPON→ BM25

Claim：`668b2ad0216182878bf78b62eb65dff11a53072aa9afb97a1ba9b49717be6547`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> In both cases, BM25, despite its simplicity, proves to
> be a strong baseline, outperforming the dense retrieval models such as ANCE.

决定理由：无依据推断：引句只说BM25优于ANCE，不涉及DPR/QAGNN改进BM25。

## 179 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：ada-002 —EVALUATED_ON→ full synthesized test sets and random 10% samples from these sets

Claim：`f88fbfcf622e4aa5c35c43d94174b0c60f2a03c825888f251c7e07d4a68e1f49`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> Among the larger models, ada-002 benefits from superior pretrained embeddings and significantly
> outperforms LLM2Vec by a large margin.

决定理由：Dataset不具体：划分描述不是单一具名数据集，且引句只有模型比较。

## 180 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：GritLM-7b —EVALUATED_ON→ full synthesized test sets and random 10% samples from these sets

Claim：`299ea73d6c5d46e1e8543d4e69472376b4917d72d1e658ab45c857b63b0acc4f`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> GritLM-7b delivers excellent performance, surpassing
> the ada-002 model overall.

决定理由：Dataset不具体：划分描述不是单一具名数据集，且引句只有模型比较。

## 181 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：LLM2Vec —IMPROVES_UPON→ BM25

Claim：`016739a6f0ac98b36bd6e3912f62bf7b4019774270425a6969d54696310d4234`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> In both cases, BM25, despite its simplicity, proves to
> be a strong baseline, outperforming the dense retrieval models such as ANCE.

决定理由：无依据推断：引句没有LLM2Vec优于或继承BM25的信息。

## 182 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：multi-ada-002 —EVALUATED_ON→ full synthesized test sets and random 10% samples from these sets

Claim：`8089d2990365c91578d499799b539266562598268a43784641f7068ad6b8b153`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> For multivector retrievers, we
> found that multi-ada-002 generally outperforms ada-002, indicating that using multiple vectors per
> document enhances retrieval effectiveness.

决定理由：Dataset不具体：测试划分集合不应作为单独Dataset节点。

## 183 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 8–8 页。

关系：ColBERTv2 —EVALUATED_ON→ full synthesized test sets and random 10% samples from these sets

Claim：`5fe4cfb38a3978603ef178cb85bd722300b365a378e74d9033b4f4c0c123b07d`；Chunk：`chunk_a407e76d3edfaf1a9413559721b56299`。

原文引句：

> For multivector retrievers, we
> found that multi-ada-002 generally outperforms ada-002, indicating that using multiple vectors per
> document enhances retrieval effectiveness. Similarly, fine-grained representation allows ColBERTv2
> to capture subtle semantic nuances between queries and documents, leading to largely improved
> retrieval accuracy.

决定理由：Dataset不具体：测试划分集合不应作为单独Dataset节点。

## 184 · 批准

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 9–9 页。

关系：GPT-4 reranker —EVALUATED_ON→ STARK-AMAZON

Claim：`662292f3276b5af4b1c6efdd60e63cc08cae4d4b881ed5587bd0f5d771e255f0`；Chunk：`chunk_a8be21889a1afd7a234a4d0521059da8`。

原文引句：

> the GPT-4 reranker
> achieving Recall@20 scores of 55% on STARK-AMAZON, 49% on STARK-MAG, and 34% on
> STARK-PRIME.

决定理由：引句明确GPT-4 reranker在STARK-AMAZON报告Recall@20，支持数据集评测关系。

## 185 · 批准

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 9–9 页。

关系：GPT-4 reranker —EVALUATED_ON→ STARK-MAG

Claim：`252a701b7992c64f1d1846efe64521975257c633b413db6a83a8378c455f77b6`；Chunk：`chunk_a8be21889a1afd7a234a4d0521059da8`。

原文引句：

> the GPT-4 reranker
> achieving Recall@20 scores of 55% on STARK-AMAZON, 49% on STARK-MAG, and 34% on
> STARK-PRIME.

决定理由：引句明确GPT-4 reranker在STARK-MAG报告Recall@20，支持数据集评测关系。

## 186 · 批准

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 9–9 页。

关系：GPT-4 reranker —EVALUATED_ON→ STARK-PRIME

Claim：`28385483e5ff2bdae2cce23e4c1aa5373b283be986abd54044fbcd815542ed6e`；Chunk：`chunk_a8be21889a1afd7a234a4d0521059da8`。

原文引句：

> the GPT-4 reranker
> achieving Recall@20 scores of 55% on STARK-AMAZON, 49% on STARK-MAG, and 34% on
> STARK-PRIME.

决定理由：引句明确GPT-4 reranker在STARK-PRIME报告Recall@20，支持数据集评测关系。

## 187 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 10–10 页。

关系：ada-002 model —IMPROVES_UPON→ LLM reranker

Claim：`edf94ecb20a48578cbf61a5e23e781ea05834d8cb9d05bde9adf94e650388d4b`；Chunk：`chunk_6dd550e53fe21bea25cc6a6fbe58e406`。

原文引句：

> In contrast, the LLM reranker significantly improves the
> results by reasoning about the relationship between the query and each paper, resulting in scores that
> more accurately reflect relevance.

决定理由：方向错误：原文是LLM重排改善ada检索结果；性能增强也不等于继承。

## 188 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 10–10 页。

关系：ada-002 model —EVALUATED_ON→ benchmark

Claim：`07b68bd736b0400bf0d294b907f879d57ca74a119c9d703d99571453314f2877`；Chunk：`chunk_6dd550e53fe21bea25cc6a6fbe58e406`。

原文引句：

> To highlight the importance of reasoning ability for achieving good performance on
> our benchmark, we present a case study in Figure 6, comparing the ada-002 model with the Claude3
> Reranker.

决定理由：Dataset不具体：benchmark没有明确到STaRK子集，不能形成稳定Dataset实体。

## 189 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 10–10 页。

关系：LLM reranker —EVALUATED_ON→ benchmark

Claim：`f5bdedddd1e905aa9319d23d6ace289b2f9d70d651143e498bae00b699ff55f2`；Chunk：`chunk_6dd550e53fe21bea25cc6a6fbe58e406`。

原文引句：

> To highlight the importance of reasoning ability for achieving good performance on
> our benchmark, we present a case study in Figure 6, comparing the ada-002 model with the Claude3
> Reranker.

决定理由：方法与Dataset均不具体：LLM reranker应明确Claude3，benchmark应明确具体子集。

## 190 · 拒绝

论文：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 10–10 页。

关系：STARK —EVALUATED_ON→ three large-scale retrieval datasets with human-generated queries and an automated pipeline to simulate realistic user queries

Claim：`1205bfbd0c8fe7bf996303034645df90004493ddd83b5c281d043f1f37c3f33a`；Chunk：`chunk_d1cc05944fdd1169c721b7f82ce10526`。

原文引句：

> We contribute three large-scale retrieval datasets with human-generated
> queries and an automated pipeline to simulate realistic user queries.

决定理由：角色与类型错误：STaRK是基准贡献，三数据集/生成管线描述不是单个评测对象。

## 191 · 批准

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 1–2 页。

关系：Iterative Reading-then-Reasoning (IRR) framework —ADDRESSES→ how to design suitable interfaces for specific tasks and how to utilize them for reasoning by LLMs

Claim：`e8f854ebf3001fa5c469365eea00d4caf2bced919a83edf621d8a1a599803780`；Chunk：`chunk_9f421de75aed07b68340cb2f2471a79e`。

原文引句：

> To implement the interface-augmented
> approach, there remain two key problems, namely
> how to design suitable interfaces for specific tasks
> and how to utilize them for reasoning by LLMs,
> which are the focus of this work.

决定理由：来源同段明确IRR/StructGPT利用结构化接口迭代读取推理，支持所述接口设计与使用问题。

## 192 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours) —IMPROVES_UPON→ Davinci-003

Claim：`6f2f5b1813dc8c507856c2397ea50285b4962fedad3daa97405fb4a87f39cad1`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours)
> 71.9
> 94.4
> 59.5
> 70.2

决定理由：关系混淆：孤立表格行不能证明IRR对Davinci-003的技术继承。

## 193 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours, few-shot) —IMPROVES_UPON→ Davinci-003

Claim：`8ca82d2c4a6625d1f74f10f60d4a9decdc43de861477dab116d14aaafadf79de`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours, few-shot)
> 69.6
> 97.1
> 97.3
> 87.0

决定理由：配置不精确且关系混淆：few-shot行数值不能证明继承Davinci-003。

## 194 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours) —IMPROVES_UPON→ ChatGPT

Claim：`9eaf5a9e308db2c78fa31e9e6efb77e2d17272de0a6f7d57304a55f9ea9d9502`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours)
> 72.6
> 94.2
> 93.9
> 80.2

决定理由：关系混淆：IRR增强ChatGPT的实验结果不等于技术继承。

## 195 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours, few-shot) —IMPROVES_UPON→ ChatGPT

Claim：`34f87de7f05df006710ddaeed138439feb37393ac5eac1de828119927c4a4618`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours, few-shot)
> 69.6
> 97.1
> 97.3
> 87.0

决定理由：关系混淆且引句无ChatGPT：few-shot数值行不能支撑继承边。

## 196 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours) —EVALUATED_ON→ KGQA

Claim：`65cc1a4be03df813df3662622a29958678c6fb6074685f80f4f0a1278021a1b5`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours)
> 71.9
> 94.4
> 59.5
> 70.2

决定理由：实体类型错误：KGQA是任务，不是具名Dataset；引句也是孤立数值行。

## 197 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–7 页。

关系：IRR (ours, few-shot) —EVALUATED_ON→ KGQA

Claim：`f245bd39e654412e2ce3fe11ceb24c401fcc1e1bdbba8041ef12cb50b6efe847`；Chunk：`chunk_358a932cf9be09a75cae0606806b9318`。

原文引句：

> + IRR (ours, few-shot)
> 69.6
> 97.1
> 97.3
> 87.0

决定理由：实体类型错误：KGQA是任务，不是具名Dataset；引句也是孤立数值行。

## 198 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–8 页。

关系：+ IRR (ours) —EVALUATED_ON→ WTQ, WikiSQL, TabFact

Claim：`ac4834dd9e45c259a18d29eb55c86b5570dcdb09665a0c46ebf7c63c42e501b2`；Chunk：`chunk_1efd4680d043944e45eb1947af46faa9`。

原文引句：

> Table 2 shows the re-
> sults on three TableQA datasets. First, with the
> full table as the prompt, ChatGPT can also achieve
> comparable performance on WTQ and TabFact as
> full-data supervised-tuning methods, but performs
> not well on more difficult WikiSQL datasets.

决定理由：复合Dataset与配置丢失：三个数据集合为一节点，+IRR未保留底座模型。

## 199 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–8 页。

关系：+ IRR (ours) —IMPROVES_UPON→ ChatGPT

Claim：`99328e1f4a786689f7f290786562af38e95c1dfe4d2548e841432984b97dcf2e`；Chunk：`chunk_1efd4680d043944e45eb1947af46faa9`。

原文引句：

> Second, our proposed method can consis-
> tently improve the performance of two LLMs a
> lot in both three datasets.

决定理由：关系混淆：方法增强两LLM不证明对ChatGPT的技术继承，主体配置也不明确。

## 200 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–8 页。

关系：+ IRR (ours, few-shot) —EVALUATED_ON→ WTQ, WikiSQL, TabFact

Claim：`156caafc777564aeb5594aa134500cc8edee0be1dca336a10a55853207cf2a89`；Chunk：`chunk_1efd4680d043944e45eb1947af46faa9`。

原文引句：

> Table 2 shows the re-
> sults on three TableQA datasets. First, with the
> full table as the prompt, ChatGPT can also achieve
> comparable performance on WTQ and TabFact as
> full-data supervised-tuning methods, but performs
> not well on more difficult WikiSQL datasets.

决定理由：复合Dataset与配置丢失：三个数据集合为一节点，+IRR few-shot未保留底座模型。

## 201 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 7–8 页。

关系：+ IRR (ours, few-shot) —IMPROVES_UPON→ + IRR (ours)

Claim：`8f3368754cbb4c16b27b5ee9e2320f0921e62992fd7585dc97c3f34a9604c084`；Chunk：`chunk_1efd4680d043944e45eb1947af46faa9`。

原文引句：

> Table 2 shows the re-
> sults on three TableQA datasets. First, with the
> full table as the prompt, ChatGPT can also achieve
> comparable performance on WTQ and TabFact as
> full-data supervised-tuning methods, but performs
> not well on more difficult WikiSQL datasets.

决定理由：证据不支持：引句谈ChatGPT全表提示结果，不证明few-shot IRR继承普通IRR。

## 202 · 拒绝

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 8–8 页。

关系：extract relevant tables and columns —ADDRESSES→ alleviates the influence of irrelevant information for LLMs to generate the SQL query

Claim：`05fb8072858cecb9f453a7cdc33381045ac85b16a17b4d4751119c69bf13e7b8`；Chunk：`chunk_c11d51b003e670a9b0426a34b4b70425`。

原文引句：

> As our proposed method can extract relevant ta-
> bles and columns, it also alleviates the influence
> of irrelevant information for LLMs to generate the
> SQL query.

决定理由：实体角色表达错误：客体是已经alleviates的效果句，非问题名称；保留原候选不修改后拒绝。

## 203 · 批准

论文：StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 8–8 页。

关系：invoke the Extract_Neighbor_Relations function —ADDRESSES→ extracting the neighboring relations of the topic entity

Claim：`cb8df5ac69161ea96415a7842edf930a689f8907b91ea2bba356924e8bf63404`；Chunk：`chunk_c11d51b003e670a9b0426a34b4b70425`。

原文引句：

> In each iteration, we first invoke the Ex-
> tract_Neighbor_Relations function to extract the
> neighboring relations (e.g., birthplace, residence,
> and education) of the topic entity “Harper Lee”

决定理由：引句明确调用Extract_Neighbor_Relations提取主题实体相邻关系，支持该具体函数的任务用途。

## 204 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 1–1 页。

关系：Think-on-Graph 2.0 —ADDRESSES→ knowledge deficiencies in large language models (LLMs)

Claim：`70acd3e6cf40f2e5a3de19ecb9095e708357bb9f53f83db561d9e1e72044f72a`；Chunk：`chunk_9b63637ef18ed2d67ff105ef55092df3`。

原文引句：

> Retrieval-augmented generation (RAG) has improved large language models
> (LLMs) by using knowledge retrieval to overcome knowledge deficiencies.

决定理由：主体错配：背景介绍RAG总体缓解知识缺失，不能直接归给Think-on-Graph 2.0。

## 205 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 2–3 页。

关系：Think-on-Graph 2.0 (ToG-2) —EVALUATED_ON→ retrieved information

Claim：`8fb5eb0a252dd081d0af5ae829cd3b0036cc02038720c3e1b1f0d2733b990090`；Chunk：`chunk_fd05fc6099086f633f4ad41747c6caac`。

原文引句：

> If the retrieved information is insufficient
> to answer the question, the next round of retrieval continues for searching more in-depth clues.

决定理由：实体类型错误：retrieved information是中间检索结果，不是Dataset。

## 206 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 3–3 页。

关系：ToG-2 —IMPROVES_UPON→ direct reasoning with powerful LLMs like GPT-3.5

Claim：`e488f5e5292c942d84c5dccc49d6437820d697217eac8396f37db328605be376`；Chunk：`chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

原文引句：

> can elevate the reasoning capabilities of smaller LLMs, e.g., Llama2-13B to a level
> comparable to direct reasoning with powerful LLMs like GPT-3.5.

决定理由：关系混淆：较小模型达到较强模型水平不证明ToG-2继承GPT-3.5直接推理。

## 207 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 3–3 页。

关系：ToG-2 —EVALUATED_ON→ various complex knowledge reasoning datasets

Claim：`4a91df8aac1b4f88e742bce9486c5a399b0fd94de9225daf4ec129996d2c5ae8`；Chunk：`chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

原文引句：

> achieves new SOTA performances on various complex knowledge reasoning
> datasets

决定理由：Dataset不具体：various complex reasoning datasets是集合描述。

## 208 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 3–3 页。

关系：ToG-2 —IMPROVES_UPON→ existing hybrid RAG approaches

Claim：`301d9bc53daeb0be70a80d4ce6fedd0f9b551a215d1124b43070a967be760fa5`；Chunk：`chunk_529e795e797b26de48cdc1fe5cbea79c`。

原文引句：

> In this work, ToG-2
> aims to tightly couple KG-based RAG and text-based RAG methods, enabling both in-depth context
> retrieval and precise graph retrieval to enhance complex reasoning performances of LLMs.

决定理由：对象泛化：existing hybrid RAG approaches非具名方法，结合两类检索不自动构成继承。

## 209 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 7–7 页。

关系：ToG-2’s performance —IMPROVES_UPON→ baseline methods

Claim：`dae1af3d1ad036b3315c70ffd59b04267988ab235521be3dab6e0cebb5dcb43d`；Chunk：`chunk_eff9e47d69abba56a62073720f2bd77b`。

原文引句：

> We mainly use GPT-3.5-turbo as the backbone LLM for a fair comparison to other baselines.

决定理由：主体类型错误：ToG-2's performance不是Method；公平比较说明不支持改进关系。

## 210 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–8 页。

关系：ToG-2 —EVALUATED_ON→ ToG-FinQA

Claim：`6bc920be6036eda4dc2e89c6722b83e1dfba8b090a7a2e77c8fe11deccf882b6`；Chunk：`chunk_b2b1f9967726b7979691a73a7daba4af`。

原文引句：

> we conduct an extra evaluation in our established ToG-FinQA
> dataset.

决定理由：来源明确ToG-2在自建ToG-FinQA额外评测并与CoT/RAG对照，支持评测关系。

## 211 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–8 页。

关系：ToG-2 —EVALUATED_ON→ AdvHotpotQA

Claim：`37cd529eceed2450f79a568fadbf2a07430bf31d4be75717d38b83fe0c3c497c`；Chunk：`chunk_b2b1f9967726b7979691a73a7daba4af`。

原文引句：

> The experimental
> results are shown in Table 3.

决定理由：引句仅Table 3定位，未包含AdvHotpotQA；需重新选择完整证据。

## 212 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–8 页。

关系：ToG-2 —EVALUATED_ON→ FEVER

Claim：`0ee2682b7a779cb5f5df3776422791f4e497b33b688d3caa9cf71323e4845052`；Chunk：`chunk_b2b1f9967726b7979691a73a7daba4af`。

原文引句：

> The experimental
> results are shown in Table 3.

决定理由：引句仅Table 3定位，未包含FEVER；需重新选择完整证据。

## 213 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–8 页。

关系：ToG-2 —IMPROVES_UPON→ direct reasoning by more powerful LLMs, e.g., GPT-3.5-turbo

Claim：`9e4d07d8aa75ea39d422a1ff0d6ee0d76dd0c083cc6a0c58628ffaafbd744e5e`；Chunk：`chunk_a27025c247baa354ac6ee877d6df28aa`。

原文引句：

> We observe that ToG-2 can elevate the reasoning capability of weaker LLMs, e.g., Llama-3-8B,
> Qwen2-7B to the level of direct reasoning by more powerful LLMs, e.g., GPT-3.5-turbo, which
> supports our intuition that ToG-2 helps LLMs with knowledge and comprehension bottlenecks.

决定理由：关系混淆：增强弱模型达到强模型水平不构成对强模型直接推理的技术继承。

## 214 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：BGE-Reranker —EVALUATED_ON→ AdvHotpotQA

Claim：`b415770a1f661b30a808d2addc24ef5c1008ffd6b644663090adbf8471258e36`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> In this experiment, we evaluate different methods for relevance scoring on a sampled
> set from AdvHotpotQA. In addition to the three DRM models—BGE-Embedding, BGE-reranker,
> and Minilm—we also tested the sparse retrieval model BM25 and generative ranking with LLMs.

决定理由：引句明确BGE-reranker参与AdvHotpotQA采样集相关性打分实验；保留采样/组件条件。

## 215 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：BGE-Reranker —IMPROVES_UPON→ Minilm

Claim：`b8c74e213db7fc40fca828d404020f95ad5f8091b2d66a8b323326dbbb40d7cf`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> The BGE-Reranker demonstrates the best performance, followed by
> Minilm, which serves as a lighter alternative to the former.

决定理由：关系混淆：最佳表现与轻量替代的对比不证明BGE-Reranker继承Minilm。

## 216 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：BM25 —EVALUATED_ON→ AdvHotpotQA

Claim：`b7bfd82ab7b593cbff4f5470a4baef58dc6d0d98aafecc7d28ce0138b1bdcae1`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> In this experiment, we evaluate different methods for relevance scoring on a sampled
> set from AdvHotpotQA. In addition to the three DRM models—BGE-Embedding, BGE-reranker,
> and Minilm—we also tested the sparse retrieval model BM25 and generative ranking with LLMs.

决定理由：引句明确BM25参与AdvHotpotQA采样集相关性打分实验，仅接受评测关系。

## 217 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：Minilm —EVALUATED_ON→ AdvHotpotQA

Claim：`05f0825d66fd9af5f1be9dfb51a94d2ed8265529f920a9ba0cf5abdefb00f627`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> In this experiment, we evaluate different methods for relevance scoring on a sampled
> set from AdvHotpotQA. In addition to the three DRM models—BGE-Embedding, BGE-reranker,
> and Minilm—we also tested the sparse retrieval model BM25 and generative ranking with LLMs.

决定理由：引句明确Minilm参与AdvHotpotQA采样集相关性打分实验，仅接受评测关系。

## 218 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：BGE-Embedding —EVALUATED_ON→ AdvHotpotQA

Claim：`78fc93b92b2a8ef5548ba315f7d1853ff89a186b91eff62cb5973a72c9a95500`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> In this experiment, we evaluate different methods for relevance scoring on a sampled
> set from AdvHotpotQA. In addition to the three DRM models—BGE-Embedding, BGE-reranker,
> and Minilm—we also tested the sparse retrieval model BM25 and generative ranking with LLMs.

决定理由：引句明确BGE-Embedding参与AdvHotpotQA采样集相关性打分实验，仅接受评测关系。

## 219 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 8–9 页。

关系：Generative-based tools —EVALUATED_ON→ AdvHotpotQA

Claim：`72f4d99df56aff0dbb9761056b381bf48673b139ed5c8a0bf47d4811e710e59d`；Chunk：`chunk_5d7ff60c6e6d8ed3d35fddd69c75e903`。

原文引句：

> In this experiment, we evaluate different methods for relevance scoring on a sampled
> set from AdvHotpotQA. In addition to the three DRM models—BGE-Embedding, BGE-reranker,
> and Minilm—we also tested the sparse retrieval model BM25 and generative ranking with LLMs.

决定理由：方法不具体：Generative-based tools未明确实际模型/方案，不能形成稳定方法实体。

## 220 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 9–9 页。

关系：ToG-2 —EVALUATED_ON→ several datasets

Claim：`13146108681165e8ac6e70deb6ff2a8d88669a85f32ed81881012d8d0385bda7`；Chunk：`chunk_5850f1e050af430b0a9f17150c790c83`。

原文引句：

> can achieve slightly
> higher performances on several datasets as shown in
> Appendix B.3 Table 7.

决定理由：Dataset不具体：several datasets未识别为具名数据集。

## 221 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 9–9 页。

关系：ToG-2 —EVALUATED_ON→ different datasets

Claim：`162da5507083c3b367a927776202659c26ba185c4b4265c6719f63d94eec7772`；Chunk：`chunk_5850f1e050af430b0a9f17150c790c83`。

原文引句：

> We compare the specific runtime between ToG and
> ToG-2 on different datasets in Appendix B.4 Table

决定理由：Dataset不具体：different datasets未识别为具名数据集。

## 222 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 9–9 页。

关系：ToG-2 —ADDRESSES→ efficiency in reasoning process

Claim：`9cd1f2d6ff4e1e8b72959e1d35cd8bdd681851ed077b5b1fa49612b00a701d96`；Chunk：`chunk_5850f1e050af430b0a9f17150c790c83`。

原文引句：

> the reasoning process of ToG-2 needs at
> most 2D+(D−1)+1 calls to the LLM.

决定理由：证据不足：调用次数上界不等于解决效率问题，缺少对用途/改进的完整说明。

## 223 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 10–10 页。

关系：ToG-2 —IMPROVES_UPON→ CoT

Claim：`f257609430cf48dd39b0a8ee05b8cd26a6f7d4996c5cd21e7b57ac1ed8bb2b89`；Chunk：`chunk_a5be5bd1049658e91cbad5ab416957de`。

原文引句：

> We also compare the outputs of ToG-2 and CoT regarding the selected questions. As shown in
> Appendix B.1 Table 5, ToG-2 alleviates the hallucination issues of LLMs compared to CoT with
> in-depth knowledge retrieval, and tends to refuse answers more often when faced with insufficient
> knowledge.

决定理由：关系混淆：对照选定问题的幻觉行为不证明ToG-2技术继承CoT。

## 224 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 10–10 页。

关系：ToG-2 —EVALUATED_ON→ AdvHotpotQA and ToG-FinQA

Claim：`75793c9a26d8d8baade3c2395b2a5ed75cf908cfdac8d1c625500cbffd0b188a`；Chunk：`chunk_a5be5bd1049658e91cbad5ab416957de`。

原文引句：

> More cases in AdvHotpotQA and ToG-FinQA are shown in Appendix D.

决定理由：复合Dataset：AdvHotpotQA与ToG-FinQA应为两个节点，不能原样批准。

## 225 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 10–10 页。

关系：ToG-2 —ADDRESSES→ hallucination issues of LLMs

Claim：`6b1a96234459a5072bbc85a452413ab8bf695e4294ea6995fe991a6d5daedbd0`；Chunk：`chunk_a5be5bd1049658e91cbad5ab416957de`。

原文引句：

> We also compare the outputs of ToG-2 and CoT regarding the selected questions. As shown in
> Appendix B.1 Table 5, ToG-2 alleviates the hallucination issues of LLMs compared to CoT with
> in-depth knowledge retrieval, and tends to refuse answers more often when faced with insufficient
> knowledge.

决定理由：引句明确作者在选定问题案例中观察ToG-2通过深度检索缓解幻觉；仅作为作者局部主张保留。

## 226 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 10–11 页。

关系：ToG-2 —IMPROVES_UPON→ existing RAG systems based on KGs or texts

Claim：`e2f28140191e11d165af45aea07fe31b6efe69e12935ab5a7569fe706de08821`；Chunk：`chunk_44ca1868cc8294f6cfe2d5991cbd0d4b`。

原文引句：

> outperform existing various LLM reasoning methods and RAG methods without additional
> training costs.

决定理由：关系混淆与对象泛化：outperform无训练成本不证明继承某个具体RAG方法。

## 227 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 10–11 页。

关系：ToG-2 —EVALUATED_ON→ different LLMs of various sizes

Claim：`35a8470670f15d898ef653dd802d037a9d310896c91e1d6ed2eeed626e51c70b`；Chunk：`chunk_44ca1868cc8294f6cfe2d5991cbd0d4b`。

原文引句：

> Experimental results demonstrate that ToG-2 can significantly improve LLMs of different
> sizes and outperform existing various LLM reasoning methods and RAG methods without additional
> training costs.

决定理由：实体类型错误：不同大小的LLM是模型条件，不是Dataset。

## 228 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 14–14 页。

关系：ToG-2 —IMPROVES_UPON→ baselines

Claim：`5dc023f8ef24f9e2e4ea3ec4ceaf0946cafc62c51063e02891ca2d03ef7f1e5d`；Chunk：`chunk_4e496c498fc0ed5a85dbab9bf21e5612`。

原文引句：

> Even though ToG-2 consistently outperforms the baselines across various datasets, it still faces
> significant bottlenecks when it comes to information retrieval.

决定理由：对象不具体：baselines泛化，胜出与瓶颈说明不构成技术继承。

## 229 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 14–15 页。

关系：ToG-2 —EVALUATED_ON→ Creak

Claim：`4a2e820dbfb73e05e536c40c3ff9733d395960516706a567e6283f7995f7a69e`；Chunk：`chunk_a68d09dd1334dcb0207c235cca9292cf`。

原文引句：

> Table 6: Distribution of answer types for ToG-2 on the Creak dataset.

决定理由：Table 6明确ToG-2在Creak上做答案类型分析；来源说明50案例抽查，保留范围限制。

## 230 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 14–15 页。

关系：ToG-2 —ADDRESSES→ Performance discrepancy between ToG and ToG-2 on the Creak dataset

Claim：`2e1b4ad1083cea30e944666893d30a5ad6f1d58a77ef4f54da3205b9ce37d2d4`；Chunk：`chunk_a68d09dd1334dcb0207c235cca9292cf`。

原文引句：

> As we observed a performance discrepancy between ToG and ToG-2 on the Creak dataset in Table 1,
> we aim to provide a more detailed analysis on this particular dataset.

决定理由：研究分析目的不是解决关系：解释两方法差异不表示ToG-2解决该差异。

## 231 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 14–15 页。

关系：ToG-2 —IMPROVES_UPON→ ToG

Claim：`042deceb591ac169d7a4fb52d185b41f93ff02e8a8d07a10ca7239fca2257751`；Chunk：`chunk_a68d09dd1334dcb0207c235cca9292cf`。

原文引句：

> As a result, ToG already performs well on this dataset, and the richer entity
> document information utilized by ToG-2 does not provide significant additional benefits.

决定理由：证据反向：原文说Creak上新增文档信息没有显著额外收益，不能支持改进继承。

## 232 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 16–17 页。

关系：ToG-2 —IMPROVES_UPON→ ToG

Claim：`e97fdaadce7d3f7c5ce04ca2bdd4f65b222505d0b14b39df4451097209b9b343`；Chunk：`chunk_734b4d6c3516e11a7a54795847f3f56f`。

原文引句：

> Does ToG-2 improve graph exploring efficiency compared to ToG? Therefore, we first statis-
> tically compared the runtime of ToG and ToG-2 across different stages under the same settings.

决定理由：引句是研究问题及比较步骤，不是已证实的技术继承结论。

## 233 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 16–17 页。

关系：ToG-2 —EVALUATED_ON→ HotpotQA

Claim：`d0c4d9cf36fbab8713aedb98ba96415e7ed0bda66fcde990b59b928fec12e841`；Chunk：`chunk_734b4d6c3516e11a7a54795847f3f56f`。

原文引句：

> To better illustrate the efficiency of our method compared to the baselines, we analyze the average
> total runtime and API call counts for each method on HotpotQA.

决定理由：来源运行时间小节明确比较ToG-2与基线在HotpotQA的耗时/API调用数，支持评测关系。

## 234 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 16–17 页。

关系：ToG-2 —EVALUATED_ON→ Table 9

Claim：`8e47e50515b1f016ab0b68ffd22bbd3a8f66160e05e9958b5e600906c57d92ab`；Chunk：`chunk_734b4d6c3516e11a7a54795847f3f56f`。

原文引句：

> The results are summarized in
> Table 9 below.

决定理由：实体类型错误：Table 9是结果定位，不是Dataset。

## 235 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：CoK —EVALUATED_ON→ WikiData, Wikipedia, and DPR

Claim：`7cc3f45612e992e5c4f1f5fee33c3873d847fb9b23ec09c20b5623cafc87e7f8`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> To ensure fairness in comparison, we restricted the knowledge domain to factual data from
> WikiData, Wikipedia, and DPR. We also adopted the update rationales at once setting
> from the original implementation.

决定理由：复合实体且角色错误：WikiData/Wikipedia为知识源，DPR为检索器，不能合为Dataset。

## 236 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：NaiveRAG —EVALUATED_ON→ entity documents encountered during ToG-2 iterations

Claim：`fd0e44c57c5447ffb38fe7b01c39ddce0e6ee9a4c2487a6bf8e743c034fba94c`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> To simulate a retrieval corpus, we use all entity documents encountered during ToG-2
> iterations.

决定理由：Dataset不具体：ToG-2迭代遇到的实体文档是构造检索语料的方法描述，不是具名评测集。

## 237 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：CoK —IMPROVES_UPON→ ToG

Claim：`d2104b49339ac3a04c6a329e45fe907aed414fa6adefd4cb8004e2a71076ca2a`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> To ensure fairness in comparison, we restricted the knowledge domain to factual data from
> WikiData, Wikipedia, and DPR. We also adopted the update rationales at once setting
> from the original implementation.

决定理由：证据不支持：CoK实现公平性说明没有ToG比较或技术继承。

## 238 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：ToG-2 —IMPROVES_UPON→ ToG

Claim：`cada524a0f6d0b2c3accbfaedd2c2fabc106bb7bc7459ccd84233ee0b0308ab6`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> For each question, ToG-2 requires up to 2D + (D −1) + 1 API calls, where:

决定理由：证据不足：单独API调用上界不能证明ToG-2继承ToG。

## 239 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：NaiveRAG —COMPARES_WITH→ ToG-2

Claim：`1cf95b7d030944f3853c1e435dc5fa86266aaa32ac2f6a8017db78bb2e729c15`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> To simulate a retrieval corpus, we use all entity documents encountered during ToG-2
> iterations.

决定理由：证据不支持比较：使用ToG-2探索文档构建检索语料不等于两方法已做对照。

## 240 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：NaiveRAG —COMPARES_WITH→ ToG

Claim：`51cccf239c775853efaba00ae953902a0a6b16ef96f543ee12dccd8bf12c8628`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> CoK: To ensure fairness in comparison, we restricted the knowledge domain to factual data from
> WikiData, Wikipedia, and DPR. We also adopted the update rationales at once setting
> from the original implementation.

决定理由：主体错配：引句描述CoK知识域设定，未出现NaiveRAG或ToG对照。

## 241 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：CoK —COMPARES_WITH→ ToG-2

Claim：`aebcbbd92dbd62acc4f5bc42895081936f29d04a98a569e559295466e55332e4`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> To ensure fairness in comparison, we restricted the knowledge domain to factual data from
> WikiData, Wikipedia, and DPR. We also adopted the update rationales at once setting
> from the original implementation.

决定理由：证据不支持比较：CoK公平性设定未明确ToG-2对照。

## 242 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–17 页。

关系：ToG-2 —COMPARES_WITH→ ToG

Claim：`8b5b276e972ff73f772fd2406bc0c00a475547ef6e1e3faefabfd9be76e90597`；Chunk：`chunk_635558ad0cf82fb9b2de3d6fba4d2af0`。

原文引句：

> For each question, ToG-2 requires up to 2D + (D −1) + 1 API calls, where:

决定理由：证据不足：引句只有ToG-2调用上界，没有ToG或显式比较。

## 243 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 17–18 页。

关系：threshold experiments in Relation Prune (RP) —EVALUATED_ON→ HotpotQA dataset

Claim：`8df1d9481d629ccf39f1ec21ee3f2f86d4c22c4b199ba3af236f0fd4145e8171`；Chunk：`chunk_5d25160c57959537a69f54de53dc09b8`。

原文引句：

> we compared the effects of three thresholds (0.2, 0.5, and 0.8) on the final
> results in the HotpotQA dataset.

决定理由：主体类型错误：threshold experiments是实验活动而非Method；应抽具体RP配置再审核。

## 244 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —EVALUATED_ON→ WebQSP

Claim：`6d41bdfd306a5ad206fa261fc38937de56ad991460c89da2593c04671c59d77b`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> For the WebQSP, Zero-Shot-RE, QALD-10-en, and Creak datasets, we computed pairwise t-tests
> comparing ToG-2 with CoK and ToG as in Table 12.

决定理由：引句明确ToG-2在WebQSP结果上与CoK/ToG比较；只接受评测关系，不复用其显著性为本项目结论。

## 245 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —EVALUATED_ON→ Zero-Shot-RE

Claim：`ced088fad3b9c3a84483f915aeed21bec2ec03658b979c6caa6c9a15b9022b91`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> For the WebQSP, Zero-Shot-RE, QALD-10-en, and Creak datasets, we computed pairwise t-tests
> comparing ToG-2 with CoK and ToG as in Table 12.

决定理由：引句明确ToG-2在Zero-Shot-RE结果上做对照分析，支持评测关系。

## 246 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —EVALUATED_ON→ QALD-10-en

Claim：`2ed85e9a47d1cab93cab1173b99cf42c01465e3bbc870d462b456f56b73d1deb`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> For the WebQSP, Zero-Shot-RE, QALD-10-en, and Creak datasets, we computed pairwise t-tests
> comparing ToG-2 with CoK and ToG as in Table 12.

决定理由：引句明确ToG-2在QALD-10-en结果上做对照分析，支持评测关系。

## 247 · 批准

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —EVALUATED_ON→ Creak

Claim：`b819c4ff25108a172dc7d2ef7de202323e5fb313b0f56493e7678ef82b580162`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> For the WebQSP, Zero-Shot-RE, QALD-10-en, and Creak datasets, we computed pairwise t-tests
> comparing ToG-2 with CoK and ToG as in Table 12.

决定理由：引句明确ToG-2在Creak结果上做对照，且来源注明与ToG差异不显著；仅确认评测。

## 248 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —IMPROVES_UPON→ CoK

Claim：`80efac850809424992b74897dbbf9fe929520284034706be31ef13cc00385937`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> Table 12: ToG-2 significantly outperforms CoK and ToG on most datasets (p < 0.05), except on
> Creak where the difference with ToG is not significant (p > 0.9), indicating similar performance on
> this dataset.

决定理由：关系混淆：统计胜出不证明ToG-2技术继承CoK。

## 249 · 拒绝

论文：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 19–19 页。

关系：ToG-2 —IMPROVES_UPON→ ToG

Claim：`6a66f1a74348426e2c75fc3b26d180a042590a718095643f2ecc5c56190fc849`；Chunk：`chunk_bb6434ecbc91c99f9e81bd6e4191b3c9`。

原文引句：

> Table 12: ToG-2 significantly outperforms CoK and ToG on most datasets (p < 0.05), except on
> Creak where the difference with ToG is not significant (p > 0.9), indicating similar performance on
> this dataset.

决定理由：关系混淆：显著性表只支持条件化性能比较，不能独立支撑ToG-2继承ToG。

## 250 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 2–2 页。

关系：LLM ⊕KG —EVALUATED_ON→ SPARQL query for question about Canberra's majority party

Claim：`d822fb34a66de2e22a45f8be07e96b2196a6f688bea8d536a4a580ffac0bc00d`；Chunk：`chunk_2c40abfab84598e99ea233dec5fd1c23`。

原文引句：

> Response: SELECT ?country ?party WHERE {
> ?canberra dbprop:isLocatedIn ?country .
> ?country dbprop:majorityParty ?party .
> }

决定理由：实体类型错误：单例SPARQL查询不是Dataset。

## 251 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 2–2 页。

关系：LLM ⊕KG —EVALUATED_ON→ Triples related to Canberra and Australia

Claim：`d6853e131d9866842bbec29359b9df904d823f4a335f1a2406e2690bb8ce3472`；Chunk：`chunk_2c40abfab84598e99ea233dec5fd1c23`。

原文引句：

> Looking for 
> triples related 
> to Canberra
> The most relevant one is (Canberra, 
> capital of, Australia). Information not 
> enough for answering the question. 
> Looking for triples related to Australia
> The most relevant one is (Australia, 
> prime minister, Anthony Albanese).
> I know that Anthony Albanese is from 
> Labor Party.

决定理由：实体类型错误：Canberra/Australia示例三元组不是Dataset。

## 252 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 2–3 页。

关系：Think-on-Graph (ToG) —IMPROVES_UPON→ beam search algorithm in KG/LLM reasoning

Claim：`fd91e241d312ac2ae512a824c8cd42807996a51929338a19dd227b07613f1326`；Chunk：`chunk_92e5d004a12fc8fd1f2a524170ac0d91`。

原文引句：

> Using the beam search algorithm (Jurafsky & Martin,
> 2009) in KG/LLM reasoning (Atif et al., 2023; Sun et al., 2023a; Xie et al., 2023; Liu et al., 2024),
> ToG allows LLM to dynamically explore a number of reasoning paths in KG and make decisions
> accordingly.

决定理由：关系混淆：使用beam search不等于改进beam search算法本身。

## 253 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 2–3 页。

关系：Think-on-Graph (ToG) —EVALUATED_ON→ input question, initial entities, KGs

Claim：`8da78aa9624d983ba411a72db95970d55446f6a5c6237946d066cfe8cfcb60a1`；Chunk：`chunk_92e5d004a12fc8fd1f2a524170ac0d91`。

原文引句：

> Given an input question, ToG first identifies initial entities and then iteratively calls the
> LLM to retrieve relevant triples from KGs through exploration (looking for relevant triples in KG via
> “on graph” step) and reasoning (deciding on the most relevant triples via “think” step) until adequate

决定理由：实体类型错误：输入问题、初始实体、KG是输入组件集合，不是评测集。

## 254 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 3–3 页。

关系：ToG —IMPROVES_UPON→ LLM explainability

Claim：`df97f0717ad7e83c261b1838fcfe2201708f74c8b8e944a2588561edf634255d`；Chunk：`chunk_b160799030dcc4aeb6145d3dd00db7f3`。

原文引句：

> Explicit, editable reasoning
> paths improve the explainability of the reasoning process of LLMs, and enable the tracing and
> correction of the provenances of models’ outputs.

决定理由：客体类型错误：LLM explainability是问题/属性，不是Method，不能接IMPROVES_UPON。

## 255 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 3–3 页。

关系：ToG —ADDRESSES→ LLM explainability

Claim：`217f506318d8eb51b9b0a55eacacb7d8e2a97272d98fd89132821d8659d9b90d`；Chunk：`chunk_b160799030dcc4aeb6145d3dd00db7f3`。

原文引句：

> Explicit, editable reasoning
> paths improve the explainability of the reasoning process of LLMs, and enable the tracing and
> correction of the provenances of models’ outputs.

决定理由：来源负责推理段明确ToG显式可编辑路径提升可解释性与来源追溯；作为作者主张保留。

## 256 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 3–3 页。

关系：ToG —ADDRESSES→ LLM knowledge-update efficiency

Claim：`6ff99df897d483c0a35accab25849b53404684cd29b5586fb5c63ba250baaf9a`；Chunk：`chunk_b160799030dcc4aeb6145d3dd00db7f3`。

原文引句：

> Under ToG
> framework, knowledge can be updated frequently via KG instead of LLM whose knowledge-update
> is expensive and slow.

决定理由：引句明确ToG通过更新KG替代昂贵缓慢的模型知识更新，支持知识更新效率问题。

## 257 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 3–3 页。

关系：ToG —ADDRESSES→ small LLM competitiveness

Claim：`d9e1b0c13a6a6b1ee2a3fd7f33bd26530b26404165d71dd8c63a4a4faee46baf`；Chunk：`chunk_b160799030dcc4aeb6145d3dd00db7f3`。

原文引句：

> ToG enhances the reasoning ability of small LLMs (e.g., LLAMA2-70B) to
> be competitive with big LLMs (e.g., GPT-4).

决定理由：引句明确作者提出ToG增强较小模型竞争力；保留原文示例和作者主张，不当成本项目实测。

## 258 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 5–5 页。

关系：ToG-R —IMPROVES_UPON→ ToG

Claim：`6703b0be7841bd99d2a31ecde0835217a83da15af824a56c597b444510f4f728`；Chunk：`chunk_aa272a627cf75d5bf907fe3a860356c4`。

原文引句：

> Compared to ToG, ToG-R offers two key benefits: 1) It eliminates the need for the process of pruning
> entities using the LLM, thereby reducing the overall cost and reasoning time. 2) ToG-R primarily
> emphasizes the literal information of relations, mitigating the risk of misguided reasoning when the
> literal information of intermediate entities is missing or unfamiliar to the LLM.

决定理由：来源明确ToG-R是ToG变体，替换实体剪枝并列出成本/时间与实体缺失方面的改进；限于这些设计目标，不表示所有数据集更准。

## 259 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 6–7 页。

关系：ToG with GPT-4 —EVALUATED_ON→ QALD10-en, WebQuestions, Zero-Shot RE and Creak, CWQ, GrailQA, Zero-Shot RE

Claim：`cc2d58ba3b71e054289ad97b4fcb9ce7981e57a13ae49ec63ec7f67f45318e03`；Chunk：`chunk_853a28afafe05201ef953b7076d05b6b`。

原文引句：

> ToG with GPT-4 and its weaker version ToG with ChatGPT
> can win the competition in all datasets. In particular, the improvement of 1.6% on open-domain QA
> dataset WebQuestions demonstrates the ToG’s generality on open-domain QA tasks.

决定理由：复合Dataset：多个数据集并入单节点且有重复名称，不能原样接纳。

## 260 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 6–7 页。

关系：ToG —EVALUATED_ON→ QALD10-en, WebQuestions, Zero-Shot RE and Creak, CWQ, GrailQA, Zero-Shot RE

Claim：`fd7575154c6f454e60728d4fe2661f4574b8ca2d9a03856e7041069b40c74508`；Chunk：`chunk_853a28afafe05201ef953b7076d05b6b`。

原文引句：

> ToG with GPT-4 and its weaker version ToG with ChatGPT
> can win the competition in all datasets. In particular, the improvement of 1.6% on open-domain QA
> dataset WebQuestions demonstrates the ToG’s generality on open-domain QA tasks.

决定理由：复合Dataset：多个数据集并入单节点，不能形成原子关系。

## 261 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 6–7 页。

关系：ToG —IMPROVES_UPON→ ToG-R

Claim：`b3a5d6a83d262a8310e4427920782b5ff8905f0f2116d33e6fde7d794c9a97f0`；Chunk：`chunk_853a28afafe05201ef953b7076d05b6b`。

原文引句：

> ToG outperforms ToG-R on most datasets since the triple-based reasoning paths provide additional
> intermediate entity information compared to the relation chains retrieved by ToG-R.

决定理由：关系混淆：ToG多数数据集优于ToG-R不证明ToG从自身变体技术继承。

## 262 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–7 页。

关系：ToG —EVALUATED_ON→ CWQ

Claim：`453362e41688bdce3d66d91cc845416814c67fe3b5df14a3d76cb9aff4c6e592`；Chunk：`chunk_eeb7d164f0b4a2603ef9be122083c59b`。

原文引句：

> we evaluate how different backbone models affect its
> performance on two datasets CWQ and WebQSP.

决定理由：来源明确评测ToG在CWQ上的不同底座影响，支持数据集关系并保留底座设置上下文。

## 263 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–7 页。

关系：ToG —EVALUATED_ON→ WebQSP

Claim：`4837f8b33dc40cbba3075a547257d53a9a3f9913cfd8fefda5098df061b40ad1`；Chunk：`chunk_eeb7d164f0b4a2603ef9be122083c59b`。

原文引句：

> we evaluate how different backbone models affect its
> performance on two datasets CWQ and WebQSP.

决定理由：来源明确评测ToG在WebQSP上的不同底座影响，支持数据集关系。

## 264 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–7 页。

关系：CoT —EVALUATED_ON→ CWQ

Claim：`a913ffadfbe1ba4540f0ac9cafdb735f5db8b309404abeab35b93548d402fcff`；Chunk：`chunk_eeb7d164f0b4a2603ef9be122083c59b`。

原文引句：

> Table 2 shows that, as we expected, the performance
> of CoT improves with the size (also reflecting partially the reasoning ability) of backbone models
> (GPT-4 > ChatGPT > Llama-2).

决定理由：引句未包含CWQ；不能只依靠表编号保存不完整评测证据。

## 265 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–7 页。

关系：CoT —EVALUATED_ON→ WebQSP

Claim：`6021c5a77afed997fb349a392895d4ce13d8b1f55084bbd81c21e6b3ef5c4cab`；Chunk：`chunk_eeb7d164f0b4a2603ef9be122083c59b`。

原文引句：

> Table 2 shows that, as we expected, the performance
> of CoT improves with the size (also reflecting partially the reasoning ability) of backbone models
> (GPT-4 > ChatGPT > Llama-2).

决定理由：引句未包含WebQSP；不能只依靠表编号保存不完整评测证据。

## 266 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–8 页。

关系：ToG —EVALUATED_ON→ CWQ, WebQSP

Claim：`e333118be3602ce2c909f3096a5f19267c36fd7e486b88a1ef51b5d76d65571e`；Chunk：`chunk_8b9e861ea949a3eb2fc9ed5a97b24644`。

原文引句：

> ToG achieves significant improvements with different source
> KGs on CWQ and WebQSP, compared to CoT.

决定理由：复合Dataset：CWQ与WebQSP合成一个节点，应拆分后再审核。

## 267 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–8 页。

关系：ToG —IMPROVES_UPON→ CoT

Claim：`3d8b7c3e90fe6c080ae5b8112dbd78cf330dbe1161a0d90b610d5da8c37f074b`；Chunk：`chunk_8b9e861ea949a3eb2fc9ed5a97b24644`。

原文引句：

> ToG achieves significant improvements with different source
> KGs on CWQ and WebQSP, compared to CoT.

决定理由：关系混淆：在两数据集上胜过CoT不代表技术继承。

## 268 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–8 页。

关系：ToG —ADDRESSES→ Do search depth and width matter for ToG?

Claim：`ea984e47f6e334b83c042894b79914a192bd215e2408987aaa6aed63a50d604d`；Chunk：`chunk_8b9e861ea949a3eb2fc9ed5a97b24644`。

原文引句：

> Do search depth and width matter for ToG?

决定理由：证据只是研究问题，没有说明已解决或具体方法作用。

## 269 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 7–8 页。

关系：ToG —ADDRESSES→ Do different KGs affect ToG’s performance?

Claim：`654583283ee57ea454a39fb4927b3048d92d99565817cedf540ad996832b1788`；Chunk：`chunk_8b9e861ea949a3eb2fc9ed5a97b24644`。

原文引句：

> Do different KGs affect ToG’s performance?

决定理由：证据只是研究问题，没有说明已解决或具体方法作用。

## 270 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 8–9 页。

关系：BM25 or SentenceBERT —IMPROVES_UPON→ LLM

Claim：`cc05a407ff8e5835d2acb477de5ae5deb09532e85b874c0d2b8261f21dd1e4bc`；Chunk：`chunk_bdd2301d529922318ec27681c94f593a`。

原文引句：

> after utilizing the BM25 or SentenceBERT, we
> only need D + 1 calls to the LLM instead of 2ND + D + 1 as we discuss in Section 2.1.3, which
> enhances the efficiency of ToG.

决定理由：复合Method且关系错误：以BM25/SentenceBERT替代剪枝模型是配置替换，不是对泛化LLM的技术继承。

## 271 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 8–9 页。

关系：LLM —ADDRESSES→ Performance Degradation

Claim：`98d52f69b91c5de2935197eab3da94fdf4b47c7d37033b5200d535085c45f49c`；Chunk：`chunk_bdd2301d529922318ec27681c94f593a`。

原文引句：

> The replacement of
> the LLM with either BM25 or SentenceBERT results in
> the significant performance degradation of our approach.

决定理由：主体不具体：LLM是模型大类，替换后的退化也不足以构成独立解决关系。

## 272 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 9–9 页。

关系：ToG —ADDRESSES→ errors or uncertainties in ToG answers

Claim：`026b4ef21c1070fa44cd9c7c1e47b1ddc64d13f322ad566651a2c5255e44d716`；Chunk：`chunk_52ee1f45e2c1f12a8b5f07f236964ded`。

原文引句：

> errors or uncertainties in ToG answers are discovered by human users/experts or other LLMs, ToG
> has the ability to trace back and examine the reasoning path, find suspicious triples with errors, and
> correct them.

决定理由：引句明确ToG可回溯路径、定位可疑三元组并纠错；来源说明需要用户/专家/其他LLM参与，不表示自动保证正确。

## 273 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 10–10 页。

关系：Think-on-Graph (ToG) —IMPROVES_UPON→ existing fine-tuning-based methods and prompting-based methods

Claim：`42cd298dc872ba31e3632404d02bf52ee01c795d1f8c8b4f208e07f53b2646ba`；Chunk：`chunk_b78209859c4376c24c898742978604f0`。

原文引句：

> outperforms existing fine-tuning-based methods and prompting-based methods without additional
> training cost and mitigates the hallucination issue of LLMs.

决定理由：关系混淆且对象泛化：胜过两大类方法不支持具体继承。

## 274 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 17–18 页。

关系：ToG —IMPROVES_UPON→ naive beam search

Claim：`9b7b7713d1f2f5acb83ba5490b9dc36d2bd29dc2ba4ba1104e605be568cb6bae`；Chunk：`chunk_7436e453884a1d9b7acd9aef4a28b0b4`。

原文引句：

> We believe that ToG can partially alleviate this issue by
> considering the top-N reasoning paths.

决定理由：引句只表达部分缓解的观点，未标明naive beam search或明确技术继承。

## 275 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 17–18 页。

关系：ToG —EVALUATED_ON→ CWQ and WebQSP

Claim：`c1551bb06ea11d39d6c508f0e83589d139331b9c669aa9a333c3a09db1353389`；Chunk：`chunk_7436e453884a1d9b7acd9aef4a28b0b4`。

原文引句：

> We conduct naive top1-beam search methods for ToG on
> CWQ and WebQSP.

决定理由：复合Dataset且配置不精确：两个数据集合并，原文还是naive top1消融设置。

## 276 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG —IMPROVES_UPON→ ToG-R

Claim：`772a450b85d10da95a1e88eb25a706d35bbb55d0487aaee775fbe8cc478bb120`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> For ToG-R,
> the disparity between the two is primarily evident in the CWQ dataset, where the percentage of
> intervals (25,50] in ToG results is quite significant (nearly 40%), whereas ToG-R results tend to be
> more evenly distributed as shown in Figure 11. We contend that this discrepancy arises from the
> disregard of entity, thereby enhancing the diversity of explored relations.

决定理由：分布差异不构成技术继承，原文未证明ToG改进ToG-R。

## 277 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG —EVALUATED_ON→ CWQ

Claim：`57ade68e4423d1720724529da7523742c0b19f35dff90e1149f8e963867b9a56`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> For ToG-R,
> the disparity between the two is primarily evident in the CWQ dataset, where the percentage of
> intervals (25,50] in ToG results is quite significant (nearly 40%), whereas ToG-R results tend to be
> more evenly distributed as shown in Figure 11.

决定理由：引句明确报告ToG在CWQ上的路径重叠区间，支持案例/路径分析层面的评测。

## 278 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG —EVALUATED_ON→ WebQSP

Claim：`b8e7abb632be1f36528622b4ba13dab725e432e87e6d6c8f7f25ed355871fe02`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> Figure 10: The explored path overlap ratio of ToG on CWQ, WebQSP, and GrailQA datasets.

决定理由：Figure 10完整图注明确ToG在WebQSP的探索路径重叠分析，支持评测关系。

## 279 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG —EVALUATED_ON→ GrailQA

Claim：`61be3c3f32511960116832ffdae9adb9ff29ee0c7e5117f703b1b52046c5526b`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> Figure 10: The explored path overlap ratio of ToG on CWQ, WebQSP, and GrailQA datasets.

决定理由：Figure 10完整图注明确ToG在GrailQA的探索路径重叠分析，支持评测关系。

## 280 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG-R —EVALUATED_ON→ CWQ

Claim：`d07e700f0dfef2307dbaffcea491c80db1878e1726bd1e873cda949ef0864849`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> For ToG-R,
> the disparity between the two is primarily evident in the CWQ dataset, where the percentage of
> intervals (25,50] in ToG results is quite significant (nearly 40%), whereas ToG-R results tend to be
> more evenly distributed as shown in Figure 11.

决定理由：引句同时包含ToG-R与CWQ的路径分布分析，支持评测关系。

## 281 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG-R —EVALUATED_ON→ WebQSP

Claim：`2fb09a10eeab06b24df6e5a1436e2d5177a304b5822f4c8f37955590e25217f0`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> Figure 11: The path overlap ratio of ToG-R on CWQ, WebQSP, and GrailQA datasets.

决定理由：Figure 11完整图注明确ToG-R在WebQSP的路径重叠分析。

## 282 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 19–20 页。

关系：ToG-R —EVALUATED_ON→ GrailQA

Claim：`a3438d59f219a0820445c59ae291ddff20f5d8350bdbad246e14f4c00320cb76`；Chunk：`chunk_c558da35a49faad6c4cbcb0f6cd6d9cf`。

原文引句：

> Figure 11: The path overlap ratio of ToG-R on CWQ, WebQSP, and GrailQA datasets.

决定理由：Figure 11完整图注明确ToG-R在GrailQA的路径重叠分析。

## 283 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 20–21 页。

关系：ToG-R —EVALUATED_ON→ CWQ and WebQSP dataset

Claim：`80e031565c1423124f863c8b5a17818d1b36784953fb9296f09979dd9b1e0bca`；Chunk：`chunk_729fce1e558e36caab6046b7e5a8ca4a`。

原文引句：

> of questions with different reasoning depths are shown in Figure 12. We analyze the performances
> of ToG, ToG-R, and CoT on testing questions of both datasets with different reasoning depths.

决定理由：复合Dataset：CWQ与WebQSP合为单节点，需拆分。

## 284 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 20–21 页。

关系：CoT —EVALUATED_ON→ CWQ and WebQSP dataset

Claim：`196f251eb0c17ad6bdd67a9b4cd1343a58f6e4a0a37665928adff5bf60edf661`；Chunk：`chunk_729fce1e558e36caab6046b7e5a8ca4a`。

原文引句：

> of questions with different reasoning depths are shown in Figure 12. We analyze the performances
> of ToG, ToG-R, and CoT on testing questions of both datasets with different reasoning depths.

决定理由：复合Dataset：CWQ与WebQSP合为单节点，需拆分。

## 285 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 20–21 页。

关系：ToG —EVALUATED_ON→ CWQ and WebQSP dataset

Claim：`15adc2d4a65a8d0da0560bf20d32c77ebe3250e25352c3ce09d2a4376f9e751c`；Chunk：`chunk_729fce1e558e36caab6046b7e5a8ca4a`。

原文引句：

> of questions with different reasoning depths are shown in Figure 12. We analyze the performances
> of ToG, ToG-R, and CoT on testing questions of both datasets with different reasoning depths.

决定理由：复合Dataset：CWQ与WebQSP合为单节点，需拆分。

## 286 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 20–21 页。

关系：CoT —IMPROVES_UPON→ ToG and ToG-R

Claim：`43afb4000ecbf12ea4f6e5ab639fe3d0786e9f2e94318e93baff1b834ae23002`；Chunk：`chunk_729fce1e558e36caab6046b7e5a8ca4a`。

原文引句：

> Conversely, ToG and ToG-R can partially
> counteract the performance degradation caused by the increment of reasoning depths of questions,
> especially on CWQ.

决定理由：语义反转与复合对象：原文ToG/ToG-R缓解退化，不是CoT改进它们。

## 287 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–21 页。

关系：replacing LLM with small models such as BM25 and Sentence-BERT in pruning step —IMPROVES_UPON→ pruning step using full LLM calls

Claim：`96558d8820fbfba15d5a818bc4f2e1cb814e76fcbf67fcd419fcd22492b791ba`；Chunk：`chunk_beb4580eff94eef584b0b4d58d070c2c`。

原文引句：

> A technical route is to replace
> LLM with small models such as BM25 and Sentence-BERT in the pruning step since the small
> models are much faster than LLM calling. In this way, we can reduce the number of LLM calling
> from 2ND+D +1 to D +1.

决定理由：复合替换策略不构成单一方法继承，原文还明确速度收益伴随精度损失。

## 288 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–21 页。

关系：increasing search width —IMPROVES_UPON→ pruning step using SentenceBERT as the pruning model

Claim：`86912c7a037e1dee0e2f639f9bd7ff8dc351ea5a8c2309c84d1917396f2f631f`；Chunk：`chunk_beb4580eff94eef584b0b4d58d070c2c`。

原文引句：

> To alleviate the issue of the
> performance degradation, we can appropriately increase the search width to compensate the loss
> because increasing search width can improve the chance of the optimal path to be selected in the pool
> and it doesn’t affect the number of LLM calling.

决定理由：端点角色错误：搜索宽度是超参数修改，不是独立Method对另一方法的继承。

## 289 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–21 页。

关系：increasing search width from 3 to 5 —EVALUATED_ON→ WebQSP

Claim：`b04606c6d9724b3b3ac2bb3c2a6c6b17a69a246113309731970ac7c1cb91fcdd`；Chunk：`chunk_beb4580eff94eef584b0b4d58d070c2c`。

原文引句：

> To empirically verify this, we increase the search
> width from 3 to 5 and reevaluate ToG with SentenceBERT as the pruning model on WebQSP.

决定理由：主体配置缺失：实际评测ToG+SentenceBERT剪枝+宽度3到5，候选仅保留超参数动作。

## 290 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–22 页。

关系：unifying the prompts in the same pruning step —ADDRESSES→ Reducing computational complexity from O(ND) to O(D)

Claim：`eaec5f72d6000601a910a1f78b3bfd81bb5512fbe058ac0849e9e6153c6832fb`；Chunk：`chunk_2a773898d4837d44bc3ec29b329f1825`。

原文引句：

> Reducing computational complexity from O(ND) to O(D) by unifying the prompts in
> the same pruning step.

决定理由：引句明确统一同一步剪枝提示用于将调用复杂度O(ND)降至O(D)；仅为论文方案主张。

## 291 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–22 页。

关系：employing LLM at once to score all components of N candidate sets —ADDRESSES→ speeding up the pruning step

Claim：`9fa2c08a494a6cf98540012844b36716d9a8644640f69ed1c2f87a171e8a7260`；Chunk：`chunk_2a773898d4837d44bc3ec29b329f1825`。

原文引句：

> Another solution on speeding up the pruning step is to employ the LLM at
> once to score all components of N candidate sets for obtaining top-N candidates, instead of calling
> the LLM N times to score N candidate sets separately.

决定理由：引句明确一次批量评分N候选集合替代N次调用以加速剪枝，支持具体技术用途。

## 292 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–22 页。

关系：optimizing pruning step —ADDRESSES→ making the actual calls of LLMs much less than the previously estimated and closer to some common prompting methods such as CoT-SC

Claim：`6e80dbd5fb46f952b0b0d78c85c64e88234953e9d0b6ac8aeabb17506ba57f11`；Chunk：`chunk_2a773898d4837d44bc3ec29b329f1825`。

原文引句：

> Optimizing pruning step to make the actual calls of LLMs much less than the previously
> estimated 2ND + D + 1 and closer to some common prompting methods such as CoT-SC.

决定理由：主体过度泛化：optimizing pruning step只是目标式描述，未识别具体优化技术。

## 293 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 21–22 页。

关系：ToG's initialize the search from the entity mostly aligning with the keyword in question —ADDRESSES→ computational time (cost or complexity) in the inference phase mainly depends on how many times calling LLM

Claim：`9076c5e3d46d44fe16a92b1bce7592de754a6ee068f9c4c7ece8de3ea038c840`；Chunk：`chunk_2a773898d4837d44bc3ec29b329f1825`。

原文引句：

> For each question, ToG needs at most 2ND+D+1
> times. Meanwhile, ToG-R needs at most ND + D + 1 times as mentioned in Section 2.

决定理由：证据不支持：调用次数上界不能说明按关键词初始化解决计算成本。

## 294 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 22–22 页。

关系：ToG —EVALUATED_ON→ Figure 3

Claim：`bfbd66d402cdd3dc6357e4c2b3b712d2dd2cb29be8ecdbf2ce6de98a53205194`；Chunk：`chunk_91a4a2e6943ad6a8074492d3f7229692`。

原文引句：

> the performance is usually good enough when the search
> width N=3 as we tested in Figure 3

决定理由：实体类型错误：Figure 3是图定位，不是Dataset。

## 295 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 22–22 页。

关系：ToG-R —EVALUATED_ON→ Figure 3

Claim：`988d17b198297ccb85ca9ea44e487465974bfa2c009586393f43145461c1e2fc`；Chunk：`chunk_91a4a2e6943ad6a8074492d3f7229692`。

原文引句：

> the performance is usually good enough when the search
> width N=3 as we tested in Figure 3

决定理由：实体类型错误：Figure 3是图定位，不是Dataset。

## 296 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 22–22 页。

关系：ToG —IMPROVES_UPON→ LLM-only

Claim：`1068a8932c3f653d9d9b2b9f7effbe83a8be7c26cc510b4b515e2e92c7023e48`；Chunk：`chunk_91a4a2e6943ad6a8074492d3f7229692`。

原文引句：

> So
> the computational time is about 21 times longer than that of LLM-only.

决定理由：证据反向且关系混淆：耗时约21倍更长不能支持改进LLM-only。

## 297 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 22–22 页。

关系：ToG-R —IMPROVES_UPON→ LLM-only

Claim：`34a3f4f1f87e1ac6382bec98a5ba9ff63b6b9b96a9fea2182bfef1c4115e12b6`；Chunk：`chunk_91a4a2e6943ad6a8074492d3f7229692`。

原文引句：

> saving nearly half of computational time.

决定理由：证据不足：节约一半耗时的引句缺少比较基线，且不证明继承LLM-only。

## 298 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 22–22 页。

关系：ToG-R —COMPARES_WITH→ ToG

Claim：`ee3feee413c8af4edb8441c34697318a8caa62eddabc16094b5b4b0acae18e60`；Chunk：`chunk_91a4a2e6943ad6a8074492d3f7229692`。

原文引句：

> With a similar performance
> to ToG, its variant ToG-R only calls LLM for ND + D + 1 times by using random entity pruning
> instead of LLM-based entity pruning, saving nearly half of computational time.

决定理由：引句明确ToG-R与ToG在表现、剪枝和调用数上作比较；仅记录比较关系。

## 299 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 23–24 页。

关系：Fine-Tuning —EVALUATED_ON→ ComplexWebQuestions

Claim：`44e4a40cc566ae10ef1a879d09202ee8835630137f3762b4244947ada2754026`；Chunk：`chunk_35aaa835320ae2ebcab47d7482d603ba`。

原文引句：

> Table 10: The statics of Fine-Tuning, prompting-based methods of ComplexWebQuestions dataset.

决定理由：主体是训练策略大类Fine-Tuning，不是可辨识具体方法。

## 300 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 23–24 页。

关系：Fine-Tuning —EVALUATED_ON→ WebQSP

Claim：`ad8cf0601e22ae9c5a8d2d42010939ad66d79c760deff4febb3c901acda258be`；Chunk：`chunk_35aaa835320ae2ebcab47d7482d603ba`。

原文引句：

> Table 11: The statics of Fine-Tuning, prompting-based methods of WebQSP dataset.

决定理由：主体是训练策略大类Fine-Tuning，不是可辨识具体方法。

## 301 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 23–24 页。

关系：Fine-Tuning —EVALUATED_ON→ GrailQA

Claim：`571d6e3e0887c04a3122d616e6a66682de1f02031a92a36286846885d924bb51`；Chunk：`chunk_35aaa835320ae2ebcab47d7482d603ba`。

原文引句：

> Table 12: The statics of Fine-Tuning, prompting-based methods of GrailQA dataset

决定理由：主体是训练策略大类Fine-Tuning，不是可辨识具体方法。

## 302 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 24–25 页。

关系：Fine-Tuning —EVALUATED_ON→ QALD10-en

Claim：`a67695eaf43c251c952006355ab28cbfe64a67b112790542e3428b0cadb67a5b`；Chunk：`chunk_cfe4f3279c22a4cc8b3c7352fd275bb6`。

原文引句：

> Table 13: The statics of Fine-Tuning, prompting-based methods of QALD10-en dataset.

决定理由：主体是训练策略大类Fine-Tuning，不是可辨识具体方法。

## 303 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 24–25 页。

关系：Fine-Tuning —EVALUATED_ON→ SimpleQuetsions

Claim：`1bd44e323bea992c743d768ed9c7085561083fb65d849c34f63262b8bc19f112`；Chunk：`chunk_cfe4f3279c22a4cc8b3c7352fd275bb6`。

原文引句：

> Table 14: The statics of Fine-Tuning, prompting-based methods of SimpleQuetsions dataset.

决定理由：主体为策略大类，Dataset名SimpleQuetsions还需消歧纠错，不能原样接纳。

## 304 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 24–25 页。

关系：Fine-Tuning —EVALUATED_ON→ WebQuestions

Claim：`1b586ec45f8a7dce5508de5bdaa64360dbc428040c0b33e5aba0f16913842598`；Chunk：`chunk_cfe4f3279c22a4cc8b3c7352fd275bb6`。

原文引句：

> Table 15: The statics of Fine-Tuning, prompting-based methods of WebQuestions dataset.

决定理由：主体是训练策略大类Fine-Tuning，不是可辨识具体方法。

## 305 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 24–25 页。

关系：MetaRAG —EVALUATED_ON→ Wikipedia

Claim：`ffd3073cc7be1d63cba0f9da33c12a884f7b6452a704e1192d5c304e32664150`；Chunk：`chunk_cfe4f3279c22a4cc8b3c7352fd275bb6`。

原文引句：

> MetaRAG
> 78.7
> Wikipedia
> 81.3
> single ngram
> 83.7
> KGI_1
> 84.4
> Re2G (Glass et al., 2022)
> 87.7
> ChatGPT
> ToG-R
> 75.3
> ToG
> 76.8
> GPT-4
> ToG-R
> 75.5
> ToG
> 77.1

决定理由：表格错列：Wikipedia出现在方法/来源行，孤立表格不证明MetaRAG在Wikipedia作为评测集测试。

## 306 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：Multitask DPR + BART —EVALUATED_ON→ T-REx dataset

Claim：`dab7d816a6ed09c941227ad7c277eb5f7352db7846bc437f002f937f84bbdf57`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> Multitask DPR + BART
> 58.0

决定理由：引句只有模型与数值，没有T-REx数据集或表头，证据不完整。

## 307 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：MetaRAG —EVALUATED_ON→ T-REx dataset

Claim：`6fa8ad8bd9350a5d32e2fa41b6fd8a849a6d73e83e21840bbddc2e5718422e15`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> MetaRAG
> 71.6

决定理由：引句只有MetaRAG与数值，没有T-REx数据集或表头。

## 308 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：KGI_1 —EVALUATED_ON→ T-REx dataset

Claim：`43580001f9a0f06ae85b1726d9773e73ee17d5c83bac482939fffa5a5a068ffe`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> KGI_1
> 72.6

决定理由：引句只有KGI_1与数值，没有T-REx数据集或表头。

## 309 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：Wikipedia —EVALUATED_ON→ T-REx dataset

Claim：`012c4f88566da62bb369c0c4bd5a67205d162b63cd3eaa84386eece215d7d807`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> Wikipedia
> 74.0

决定理由：实体角色含混：Wikipedia不是明确方法，且引句缺T-REx表头。

## 310 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：single ngram —EVALUATED_ON→ T-REx dataset

Claim：`0ac0bfd9354ee0c5baac4ad06f018e64da7bb2d23cfa6f407bbf19fc3fd453a2`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> single ngram
> 74.6

决定理由：引句只有single ngram与数值，没有T-REx数据集或表头。

## 311 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：ChatGPT —EVALUATED_ON→ T-REx dataset

Claim：`41c502684efd0b47cc5ac71bfff99c54cceb12eb6373a329acc61fd8c96a33c4`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> ChatGPT
> ToG-R
> 86.5

决定理由：配置错配：引句对应ChatGPT+ToG-R，不是裸ChatGPT，且缺数据集。

## 312 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：ToG-R —EVALUATED_ON→ T-REx dataset

Claim：`5fb87cbab7949c8d7e5e30ba6bc44285ccd535706344aae743629b5cfe767dfd`；Chunk：`chunk_49581be104ea412de611088357015646`。

原文引句：

> ChatGPT
> ToG-R
> 86.5

决定理由：配置丢失且引句缺Dataset：ToG-R未保留ChatGPT底座，不能据孤立行批准。

## 313 · 批准

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：ToG —EVALUATED_ON→ CWQ dataset

Claim：`06d95b0daee0dad62500c382fef2a64e4af88e1a378573f19ca4a18914ceaeaf`；Chunk：`chunk_b631364a3a51eca4618b8e3fbe13f7b8`。

原文引句：

> In this section, we present a case analysis of the CWQ dataset to evaluate the utility and limitations
> of the ToG.

决定理由：引句明确ToG在CWQ做效用与局限案例分析；来源为四例分析，不扩大为新全量测评。

## 314 · 拒绝

论文：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 25–25 页。

关系：ToG —COMPARES_WITH→ IO, CoT and the New Bing search engine

Claim：`77dd10b928f4461df76c995d5e878950e67f98def930cf40d01e4664eef57474`；Chunk：`chunk_b631364a3a51eca4618b8e3fbe13f7b8`。

原文引句：

> We compared ToG with IO, CoT and the New Bing search engine4.

决定理由：复合Method：IO/CoT/New Bing合成单节点，需拆分后保留独立比较关系。

## 315 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 1–1 页。

关系：Tree-of-Traversals —EVALUATED_ON→ two popular benchmark datasets

Claim：`96eb0ce94e67d3834522871c9fb0894749cbd33a77aa25fde2287ea20a62f6e3`；Chunk：`chunk_c684fea40eeaf98c4d80f0c62119849d`。

原文引句：

> We evaluate on two popular benchmark
> datasets.

决定理由：Dataset不具体：two popular benchmark datasets未命名。

## 316 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 1–1 页。

关系：Tree-of-Traversals —IMPROVES_UPON→ black-box LLMs

Claim：`f33425967188797ff2cece637b5b9ab304ce6653c9d580a9eaa80df4597bcbdd`；Chunk：`chunk_c684fea40eeaf98c4d80f0c62119849d`。

原文引句：

> enables augmentation
> of black-box LLMs with one or more KGs.

决定理由：对象泛化且关系混淆：增强black-box LLMs不证明继承某一具体方法。

## 317 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 2–2 页。

关系：Tree-of-Traversals —EVALUATED_ON→ 2WikiMultiHop and QALD-10

Claim：`6650063ac8cbaf36425d5674fb1d50273dbe6ad1ca68136c8cac2916297b32cb`；Chunk：`chunk_db3f4b0797f0910ec556e6c6930ef07b`。

原文引句：

> Evaluation of Tree-of-Traversals on two ques-
> tion answering tasks: 2WikiMultiHop and
> QALD-10 and comparison with baselines.

决定理由：复合Dataset：2WikiMultiHop与QALD-10合成单节点。

## 318 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 2–2 页。

关系：Tree-of-Traversals —COMPARES_WITH→ baselines

Claim：`704fb7e2caef2bc008c552ed1820e6b4c832acfb06110079ae7c3ea61d6421ce`；Chunk：`chunk_db3f4b0797f0910ec556e6c6930ef07b`。

原文引句：

> Evaluation of Tree-of-Traversals on two ques-
> tion answering tasks: 2WikiMultiHop and
> QALD-10 and comparison with baselines.

决定理由：方法不具体：baselines未辨识具体对照对象。

## 319 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 2–2 页。

关系：Tree-of-Traversals —IMPROVES_UPON→ a local KG subgraph that is repeatedly expanded until it contains all the information required by an LLM to answer the given query

Claim：`04aebdb494396f4895960e562410ac0a35581b323b02f38ecf596e1e0db2e69e`；Chunk：`chunk_0cb3c2dcbacf18237a13b232366d2be8`。

原文引句：

> The Tree-of-Traversals algorithm maintains a local
> KG subgraph that is repeatedly expanded until it
> contains all the information required by an LLM
> to answer the given query.

决定理由：客体类型错误：局部KG子图及扩展过程不是另一Method。

## 320 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 4–4 页。

关系：Tree-of-Traversals tree search algorithm —ADDRESSES→ search space bounding

Claim：`b3cba0fe4e95ecbcf9e0181b8c516c85d05c20bd047833cbc24ac17a5b42b41e`；Chunk：`chunk_dac5f23e1b87249cf88eff5c6cc54355`。

原文引句：

> To bound the search space
> we add two hyper-parameters: max depth of the
> tree search, after which the algorithm is forced to
> transition to the done state (i.e., answer the query),
> and max expansions after which the model halts
> exploration and returns "Cannot find answer".

决定理由：来源明确Tree-of-Traversals以最大深度和扩展数限制搜索，超限结束/拒答，支持搜索空间约束。

## 321 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 4–5 页。

关系：Tree-of-Traversals —ADDRESSES→ exploration of the action space

Claim：`5f8789d2b0e15721864505edf8a0361c133c573e0bae6723bd2db139c1e087e3`；Chunk：`chunk_226ee68d6f0960540c826792e6f5b531`。

原文引句：

> These
> values are then used to guide the exploration of
> the action space.

决定理由：来源Value Function Guidance明确Tree-of-Traversals用LLM节点价值引导动作空间搜索，支持用途。

## 322 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 5–5 页。

关系：Tree-of-Traversals —EVALUATED_ON→ 2WikiMultiHop Dataset

Claim：`b8f9e5e0a66c0a1293cd19b445c02e8374f7151e439e193604e9181705fd0857`；Chunk：`chunk_a8ce6be635ba6abbbc71daeb86e809e9`。

原文引句：

> We first evaluate the Tree-of-Traversals algorithm
> on two common tasks used for evaluating an LLM’s
> knowledge: 2WikiMultiHop and QALD-10.

决定理由：引句明确Tree-of-Traversals在2WikiMultiHop评测，来源说明三种底座；不合并QALD为一实体。

## 323 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–7 页。

关系：Tree-of-Traversals —EVALUATED_ON→ 2WikiMultiHop

Claim：`36b9a422e34cc1bc63ae53dfb8f2c9f94812e58ead8b2ab902d0b77c1d56ad19`；Chunk：`chunk_406249e1d98db3baa838606c7a974998`。

原文引句：

> Table 1 presents the results of our experiments on
> 2WikiMultiHop and QALD-10.

决定理由：来源Results明确报告Tree-of-Traversals在2WikiMultiHop的实验，支持评测事实。

## 324 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–7 页。

关系：Tree-of-Traversals —EVALUATED_ON→ QALD-10

Claim：`788d66c10fad008c6545146f7428c2aab521b12234210fb9263b80cbc73dc767`；Chunk：`chunk_406249e1d98db3baa838606c7a974998`。

原文引句：

> Table 1 presents the results of our experiments on
> 2WikiMultiHop and QALD-10.

决定理由：来源Results明确报告Tree-of-Traversals在QALD-10的实验，支持评测事实。

## 325 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–7 页。

关系：Tree-of-Traversals —EVALUATED_ON→ MusicBrainz-x-Wikidata

Claim：`e0744ecc275d215295fee2282a159c3d87a1646f87565c399487a794878d319e`；Chunk：`chunk_406249e1d98db3baa838606c7a974998`。

原文引句：

> On MusicBrainz-x-Wikidata (Table 2), which
> contains challenging reasoning questions requiring
> access to two KGs, there is an average of 37.4%
> relative improvement from Tree-of-Traversals over
> Chain-of-Traversals as shown in Table 2.

决定理由：引句明确Tree-of-Traversals在MusicBrainz-x-Wikidata上的结果；仅接受Dataset关系。

## 326 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–7 页。

关系：Tree-of-Traversals —IMPROVES_UPON→ Chain-of-Traversals

Claim：`34466d02867bebcd3ced0ee7724f67572fe9a34f55c4e505a07ef4ff15c15d47`；Chunk：`chunk_406249e1d98db3baa838606c7a974998`。

原文引句：

> Compared
> to Chain-of-Traversals, Tree-of-Traversals further
> improves performance.

决定理由：关系混淆：性能较Chain-of-Traversals好不足以证明继承；本文将Chain视为分支因子1的变体。

## 327 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–8 页。

关系：Tree-of-Traversals —IMPROVES_UPON→ Chain-of-Traversals

Claim：`8bad7d5a607c4d1119fd6f6a846a76933139e68a30fd622d93dd5eb55accf508`；Chunk：`chunk_f381347013975ddbbd59d9d2e9198e70`。

原文引句：

> Tree-of-Traversals
> 40.4
> 23.4
> 16.5
> Table 2: EM-in on MusicBrainz-x-Wikidata dataset.

决定理由：引句缺比较对象，孤立Tree结果行不支持技术继承。

## 328 · 批准

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 7–8 页。

关系：Tree-of-Traversals —EVALUATED_ON→ MusicBrainz-x-Wikidata

Claim：`96268ce7b862a738daf2368f014a8e239980397d1f5522e4980cdbb1269808d3`；Chunk：`chunk_f381347013975ddbbd59d9d2e9198e70`。

原文引句：

> Table 2: EM-in on MusicBrainz-x-Wikidata dataset.

决定理由：来源Table 2明确Tree-of-Traversals行与MusicBrainz-x-Wikidata表注，支持该集评测。

## 329 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 8–8 页。

关系：ReAct→CoT —IMPROVES_UPON→ CoT

Claim：`b9c112f4aa298b8afde99f5bb70b535717e0658d4471c7b202e72cd59ffdc5c5`；Chunk：`chunk_de3c9f51149251b0107325a7b92035cd`。

原文引句：

> ReAct→CoT still improves
> over CoT on both 2WikiMultiHop and QALD-10.

决定理由：关系混淆：ReAct到CoT组合的分数优势不等于具体技术继承。

## 330 · 拒绝

论文：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 9–10 页。

关系：Tree-of-Traversals —EVALUATED_ON→ English versions of KGs and datasets

Claim：`d45cde9812b314b314f9b51e63819f77bf353591d5858e77251e0b5ac5cbdddb`；Chunk：`chunk_c9487cbd571de7247dab7359aeb33936`。

原文引句：

> Our evaluation is limited to only English
> versions of KGs and datasets. Tree-of-Traversals
> should be evaluated in other languages to ensure
> consistent and fair experience.

决定理由：Dataset不具体：English versions of KGs and datasets是范围限制，不是具名数据集。

## 331 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 6–7 页。

关系：LLM-augmented KG embedding —ADDRESSES→ encoding the textual descriptions of entities and relations in KGs

Claim：`228eaefb5e6669c7df10fea6a93fffd096fdd34055e96a12deb8b82f458c02be`；Chunk：`chunk_0acc8d7e24d50270a979f9b37c31f676`。

原文引句：

> apply LLMs to enrich representations of KGs by
> encoding the textual descriptions of entities and
> relations.

决定理由：方法大类：LLM-augmented KG embedding未识别具体技术，综述分类不直接当作单一Method。

## 332 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 6–7 页。

关系：LLM-augmented KG completion —ADDRESSES→ utilize LLMs to encode text or generate facts for better KGC performance

Claim：`f2c0d92c1ea1f9e080d4fc1ba18804c68483ae9bb9797ab619cc416ee9abc0c8`；Chunk：`chunk_0acc8d7e24d50270a979f9b37c31f676`。

原文引句：

> utilize LLMs to encode text or generate facts for
> better KGC performance.

决定理由：方法大类与目标混淆：KG completion类目及目标句不构成具体方法关系。

## 333 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：KG-enhanced LLM pre-training —IMPROVES_UPON→ ERNIE [35]

Claim：`311ebe32b7ee79f7f2e53d4aec17c3476583d34f2c833de667f10a9561c17f8f`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> KG-enhanced LLM pre-training
> ERNIE [35]
> 2019
> E

决定理由：分类表不是继承：KG-enhanced pretraining是ERNIE的类别，不是改进ERNIE的方法。

## 334 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：Integrating KGs into Training Objective —IMPROVES_UPON→ GLM [102]

Claim：`01024439df0209a80326fa2d507a72dd35ab4208ae042168cd8e3cfe90a1f623`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> Integrating KGs into Training Objective
> GLM [102]
> 2020
> C

决定理由：分类表不是继承：训练目标类别不表示改进GLM。

## 335 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：Integrating KGs into Language Model Inputs —IMPROVES_UPON→ CoLAKE [107]

Claim：`4eb340a002408836ebedff971e597934b700cccf07a2bfa2f77c3386bcc80538`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> Integrating KGs into Language Model Inputs
> CoLAKE [107]
> 2020
> E

决定理由：分类表不是继承：输入集成类别不表示改进CoLAKE。

## 336 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：KG-enhanced LLM inference —IMPROVES_UPON→ KGLM [113]

Claim：`e7ede5ead8ff9a44691999049fa1360698966f147df6ef6a532464e2ee172848`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> KG-enhanced LLM inference
> KGLM [113]
> 2019
> E

决定理由：分类表不是继承：KG inference类别不表示改进KGLM。

## 337 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：Retrival-augmented knowledge fusion —IMPROVES_UPON→ REALM [114]

Claim：`20482a6b53090cc9f8fff6bfa57d1587c35e45b20f523706022bd629e2a9e01c`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> Retrival-augmented knowledge fusion
> REALM [114]
> 2020
> E

决定理由：分类表不是继承：retrieval knowledge fusion类别不表示改进REALM。

## 338 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：KGs Instruction-tuning —IMPROVES_UPON→ OntoPrompt [110]

Claim：`34bebf1def34e1a8b2518b4d38ca18e4259629d5e3314338085d0a7729dd67bc`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> KGs Instruction-tuning
> OntoPrompt [110]
> 2022
> E + D

决定理由：分类表不是继承：instruction-tuning类别不表示改进OntoPrompt。

## 339 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：KGs Prompting —IMPROVES_UPON→ Mindmap [65]

Claim：`3228de685c1b4d51d34ec095cf8c25668c43173c4720c254ba8aa07ed2a43ba5`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> KGs Prompting
> Mindmap [65]
> 2023
> E + D

决定理由：分类表不是继承：KG prompting类别不表示改进MindMap。

## 340 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 7–7 页。

关系：KGs for LLM probing —IMPROVES_UPON→ LPAQA [118]

Claim：`6d2f3c56c387c336788b63779d714603e1d4afa44d6fca6cf3791214ec2c30b3`；Chunk：`chunk_bb6c258ff3a6d9e0cb0053c1e9330d43`。

原文引句：

> KGs for LLM probing
> LPAQA [118]
> 2020
> E

决定理由：分类表不是继承：probing类别不表示改进LPAQA。

## 341 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：KALM —IMPROVES_UPON→ LLMs

Claim：`8c293ba126c59c1a23873f0c9448d1a97ad89978982c116463ea9b6cd7dcb2cd`；Chunk：`chunk_3beb28682a38078eab6b92eae915913a`。

原文引句：

> Similarly, KALM [91] enhances the input
> tokens by incorporating entity embeddings and includes
> an entity prediction pre-training task in addition to the
> token-only pre-training objective.

决定理由：对象不具体：LLMs大类无法作为KALM的确定技术前身。

## 342 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：KEPLER —IMPROVES_UPON→ LLMs

Claim：`cf679524e66495464cc6c57e9ac9d6ef3b55cd248be9267ec7b2b3e7cf829e6d`；Chunk：`chunk_3beb28682a38078eab6b92eae915913a`。

原文引句：

> Finally, KEPLER [40] directly employs both
> knowledge graph embedding training objective and Masked
> token pre-training objective into a shared transformer-based
> encoder.

决定理由：对象不具体：共享编码器训练目标不证明KEPLER继承某个未命名LLM。

## 343 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：Deterministic LLM —IMPROVES_UPON→ LLMs

Claim：`2c90141bf634d7f413076b7efd0a56006dab330c3a4f7d8cf7b4a3782c06bdd0`；Chunk：`chunk_3beb28682a38078eab6b92eae915913a`。

原文引句：

> It only masks the span that has a deterministic entity as the
> question and introduces additional clue contrast learning
> and clue classification objective.

决定理由：对象不具体且引句无主体：新增目标不能支持对LLMs大类的继承。

## 344 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：WKLM —IMPROVES_UPON→ LLMs

Claim：`34a70a4c81ba7646f8293cb1cf365ee7ced5bab331c24007854b6f0821d73288`；Chunk：`chunk_3beb28682a38078eab6b92eae915913a`。

原文引句：

> WKLM [106] first replaces
> entities in the text with other same-type entities and then
> feeds them into LLMs. The model is further pre-trained to
> distinguish whether the entities have been replaced or not.

决定理由：对象不具体：实体替换预训练不证明WKLM继承某个具体LLM方法。

## 345 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：ERNIE 3.0 [101] —IMPROVES_UPON→ Direct knowledge triple concatenation method

Claim：`553e2ae7e96e558bb48f3a9f5d618174a75f1cd2a8f64f645ea39715e76306cb`；Chunk：`chunk_76d41557bcb13368e687ddf304c4823b`。

原文引句：

> However,
> such direct knowledge triple concatenation method allows
> the tokens in the sentence to intensively interact with the
> tokens in the knowledge sub-graph, which could result in
> Knowledge Noise [36]. To solve this issue, K-BERT [36] takes
> the first step to inject the knowledge triple into the sentence
> via a visible matrix where only the knowledge entities have
> access to the knowledge triple information, while the tokens
> in the sentences can only see each other in the self-attention
> module.

决定理由：主体错配：引句描述K-BERT解决知识噪声，不是ERNIE 3.0改进直接拼接。

## 346 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–8 页。

关系：K-BERT [36] —ADDRESSES→ Knowledge Noise

Claim：`e550ce871a38216c16dffca6e12f4a6a7c183abcc4d9138ce1ee678e733a19e4`；Chunk：`chunk_76d41557bcb13368e687ddf304c4823b`。

原文引句：

> To solve this issue, K-BERT [36] takes
> the first step to inject the knowledge triple into the sentence
> via a visible matrix where only the knowledge entities have
> access to the knowledge triple information, while the tokens
> in the sentences can only see each other in the self-attention
> module.

决定理由：来源前句明确Knowledge Noise，紧接着说明K-BERT可见矩阵限制交互来解决该问题；作为综述作者归纳保留，非原论文复验。

## 347 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–9 页。

关系：KGs Instruction-tuning —EVALUATED_ON→ instruction-tuning datasets

Claim：`137b504ca19cecf5ae97e9a84fe167fb653fe3609e37cca0c62decec783c619e`；Chunk：`chunk_172b595be2772856ff4cac52163a736a`。

原文引句：

> LLMs finetuned on these
> datasets can extract both factual and structural knowledge
> from KGs, enhancing the reasoning ability of LLMs.

决定理由：Dataset不具体且阶段角色错误：instruction-tuning datasets是训练数据类目，不是具名评测集。

## 348 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–9 页。

关系：KGs Instruction-tuning —IMPROVES_UPON→ injecting factual knowledge into LLMs

Claim：`493aca84dd4a5b744af4ae862146ee24f3a98ace8a1b0adfb89f91d1ce0be59b`；Chunk：`chunk_172b595be2772856ff4cac52163a736a`。

原文引句：

> Instead of injecting factual knowledge into LLMs, the KGs

决定理由：证据截断且对象非具名Method，不能推出instruction-tuning技术继承。

## 349 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–9 页。

关系：OntoPrompt —EVALUATED_ON→ downstream tasks

Claim：`83a9c5e11639818c15feb165074a7d0cbf4c819453dcfb53a7cf84a5b2a67267`；Chunk：`chunk_172b595be2772856ff4cac52163a736a`。

原文引句：

> OntoPrompt
> [110] proposes an ontology-enhanced prompt-tuning that
> can place knowledge of entities into the context of LLMs,
> which are further finetuned on several downstream tasks.

决定理由：实体类型错误：downstream tasks是任务集合，不是Dataset。

## 350 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 8–9 页。

关系：RoG —EVALUATED_ON→ KG structure

Claim：`f083f0189386a3b521ecfd4ada4ad78db73f1d40fb47bcf10a425de9295b132e`；Chunk：`chunk_172b595be2772856ff4cac52163a736a`。

原文引句：

> To better reason on graphs, RoG [112] presents a
> planning-retrieval-reasoning framework. RoG is finetuned
> on KG structure to generate relation paths grounded by KGs
> as faithful plans.

决定理由：实体类型错误：KG structure是训练知识结构，不是评测Dataset。

## 351 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：Retrieval-Augmented Knowledge Fusion —IMPROVES_UPON→ RAG [92]

Claim：`d0d4367128b2feb75b3c6ddb3e11cbafa6105dcdf1fbdc7f2ffcca991955cdfb`；Chunk：`chunk_a4ba79086f76756d856ed610b0b47fee`。

原文引句：

> Story-fragments
> [127] further improves architecture by adding an additional
> module to determine salient knowledge entities and fuse
> them into the generator to improve the quality of generated
> long stories.

决定理由：主体错配：引句描述Story-fragments新增模块，不能归给Retrieval-Augmented Knowledge Fusion类目。

## 352 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：Retrieval-Augmented Knowledge Fusion —EVALUATED_ON→ open-domain QA

Claim：`612734b939d6ff8b4498abe97b074e1da2d6836eda5993e57ac5c59942f38a5a`；Chunk：`chunk_a4ba79086f76756d856ed610b0b47fee`。

原文引句：

> The experimental results
> show that RAG outperforms other parametric-only and
> non-parametric-only baseline models in open-domain QA.

决定理由：主体错配与Dataset错误：引句主体RAG，open-domain QA是任务不是具名数据集。

## 353 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：Retrieval-Augmented Knowledge Fusion —ADDRESSES→ inject knowledge into LLMs during inference

Claim：`3786b083a5e35a3a83d513249eabab233d57ef2d5ea6cc5c0333c19b74d85dfd`；Chunk：`chunk_a4ba79086f76756d856ed610b0b47fee`。

原文引句：

> Retrieval-Augmented
> Knowledge
> Fusion
> is
> a
> popular
> method to inject knowledge into LLMs during inference.

决定理由：主体是技术类别而非辨识具体方法，避免将综述分类直接作为统一方法实体。

## 354 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：Li et al. —EVALUATED_ON→ triples

Claim：`4f7c0acd51ed894492058ddf559f3398e04603f883d2f1c84de799745b57ada0`；Chunk：`chunk_dc4ccefbfd31fbfc43c0f498079c965d`。

原文引句：

> Li
> et al. [64] adopt the pre-defined template to convert each
> triple into a short sentence, which can be understood by
> LLMs for reasoning.

决定理由：端点类型错误：Li et al.是作者群体，triples是输入数据形式，不是Method和Dataset。

## 355 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：Mindmap —ADDRESSES→ converting structured KGs into text sequences

Claim：`db98871fe666f6e30bfd42de0e10a8a25cb0c8b2b182c2964ba544957d3bd2e6`；Chunk：`chunk_dc4ccefbfd31fbfc43c0f498079c965d`。

原文引句：

> Mindmap [65] designs a KG prompt to
> convert graph structure into a mind map that enables LLMs
> to perform reasoning by consolidating the facts in KGs and
> the implicit knowledge from LLMs.

决定理由：来源KG prompting段明确MindMap把图结构转为提示中的思维导图，支持结构化KG的文本化任务；作为综述归纳保留。

## 356 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：ChatRule —ADDRESSES→ converting structured KGs into text sequences

Claim：`4f6f29a304481693a49a10eb874454cda8dbc5934f3a92199cf5af3330dcc9cd`；Chunk：`chunk_dc4ccefbfd31fbfc43c0f498079c965d`。

原文引句：

> ChatRule [116] sam-
> ples several relation paths from KGs, which are verbalized
> and fed into LLMs. Then, LLMs are prompted to generate
> meaningful logical rules that can be used for reasoning.

决定理由：引句明确ChatRule把采样关系路径verbalized后送入LLM，支持KG路径文本化用途；非原论文复验。

## 357 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 9–9 页。

关系：CoK —ADDRESSES→ converting structured KGs into text sequences

Claim：`07f0fd900e882f1a03ad1656e154dccf2e32bdae3dd1ed268b6fe72ab1968667`；Chunk：`chunk_dc4ccefbfd31fbfc43c0f498079c965d`。

原文引句：

> CoK
> [117] proposes a chain-of-knowledge prompting that uses a
> sequence of triples to elicit the reasoning ability of LLMs to
> reach the final answer.

决定理由：证据不完整：使用三元组序列推理没有明确说明文本转换步骤，不能直接接受所抽问题。

## 358 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 10–10 页。

关系：Autoprompt [119] —IMPROVES_UPON→ manually defined prompt templates

Claim：`dbe286e775fe019c2f3c93c91b1fb2786857f3fa0def277b530df29e31ce548d`；Chunk：`chunk_b77f03a43d39a42965477d20fa582191`。

原文引句：

> Unlike using manually defined prompt templates,
> Autoprompt [119] proposes an automated method, which
> is based on the gradient-guided search to create prompts.

决定理由：对象不具体：手工模板是技术类别，自动生成替代不等于在具名方法上技术继承。

## 359 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 10–10 页。

关系：LLM-facteval [121] —EVALUATED_ON→ KGs

Claim：`27f63241e0337fcd8314d4c9c978fdd6723af99d4092aedd3d5619a986c7efbb`；Chunk：`chunk_b77f03a43d39a42965477d20fa582191`。

原文引句：

> LLM-facteval [121] designs a systematic framework that
> automatically generates probing questions from KGs. The
> generated questions are then used to evaluate the factual
> knowledge stored in LLMs.

决定理由：Dataset不具体且角色错误：KGs是生成探测题的来源，不是明确评测集。

## 360 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 10–10 页。

关系：BioLAMA [129] —EVALUATED_ON→ medical knowledge graphs

Claim：`79dab32f921241fe271a7f187556446653d2f9fd70297c4df6d85d39599b55ba`；Chunk：`chunk_b77f03a43d39a42965477d20fa582191`。

原文引句：

> Instead of probing the general knowledge by using
> the encyclopedic and commonsense knowledge graphs,
> BioLAMA [129] and MedLAMA [120] probe the medical
> knowledge in LLMs by using medical knowledge graphs.

决定理由：Dataset不具体：medical knowledge graphs是领域集合而非具名数据集。

## 361 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 10–10 页。

关系：MedLAMA [120] —EVALUATED_ON→ medical knowledge graphs

Claim：`e1af1f03dcdfdb8bdf647b7029968721d3e443ed63614ccdeeed7d0f28343867`；Chunk：`chunk_b77f03a43d39a42965477d20fa582191`。

原文引句：

> Instead of probing the general knowledge by using
> the encyclopedic and commonsense knowledge graphs,
> BioLAMA [129] and MedLAMA [120] probe the medical
> knowledge in LLMs by using medical knowledge graphs.

决定理由：Dataset不具体：medical knowledge graphs是领域集合而非具名数据集。

## 362 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 12–12 页。

关系：KG-BERT [26] —EVALUATED_ON→ triple (h, r, t) as a text sequence

Claim：`50b7dfc96f4ee8628cf2e81df6e4a263c659bbd87dca3fbd51d3c93639861436`；Chunk：`chunk_6ce8f0a4dc3d0a9b4c697c1ed1ac0c93`。

原文引句：

> KG-BERT [26]
> represents a triple (h, r, t) as a text sequence and encodes
> it with LLM Fig. 16(a).
> x = [CLS] Texth [SEP] Textr [SEP] Textt [SEP],
> (5)

决定理由：实体类型错误：三元组文本表示是输入形式，不是Dataset。

## 363 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 12–12 页。

关系：KG-BERT [26] —IMPROVES_UPON→ encoder-only LLMs to encode textual information as well as KG facts

Claim：`442c5ee33a8e5e45b063282368da374b46d0aa6469f6328dec473e89a468bcc5`；Chunk：`chunk_6ce8f0a4dc3d0a9b4c697c1ed1ac0c93`。

原文引句：

> this line of work
> first uses encoder-only LLMs to encode textual information
> as well as KG facts. Then, they predict the plausibility
> of the triples or masked entities by feeding the encoded
> representation into a prediction head, which could be a
> simple MLP or conventional KG score function (e.g., TransE
> [33] and TransR [185]).

决定理由：关系混淆与对象泛化：编码器工作流程不是KG-BERT技术前身方法的证据。

## 364 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 12–12 页。

关系：PKGC —EVALUATED_ON→ triplet (h, r, t)

Claim：`b4a35193865daf2e5f68ccc9cc993d0e64e7aefb5791b0bf039e8f9dfcf5732d`；Chunk：`chunk_ba9be863434d879145d3c81a91640412`。

原文引句：

> PKGC [139]
> assesses the validity of a triplet (h, r, t) by transforming the
> triple and its supporting information into natural language
> sentences with pre-defined templates.

决定理由：实体类型错误：triplet(h,r,t)是输入单位，不是Dataset。

## 365 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 12–12 页。

关系：LASS —IMPROVES_UPON→ KG-BERT

Claim：`be45e4c21bd9bb19fdee27895a9f87c717ca802362fc2a3b0a728f0b24f096ae`；Chunk：`chunk_ba9be863434d879145d3c81a91640412`。

原文引句：

> LASS [140]
> observes that language semantics and graph structures are
> equally vital to KGC. As a result, LASS is proposed to
> jointly learn two types of embeddings: semantic embedding
> and structure embedding.

决定理由：证据未包含KG-BERT，提出双嵌入不足以证明LASS继承KG-BERT。

## 366 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 13–13 页。

关系：Entity Description Prediction (EDP) —ADDRESSES→ challenges of open-world KGC

Claim：`b070e35af8eec33ecb97c0df4d74bfe33e3c3cd59a358933fc5924428177b19b`；Chunk：`chunk_fdffeffc56ad04f8c112ce4b3213f94e`。

原文引句：

> OpenWorld KGC [142] expands the MEM-KGC model to
> address the challenges of open-world KGC with a pipeline
> framework, where two sequential MLM-based modules are
> defined: Entity Description Prediction (EDP), an auxiliary
> module that predicts a corresponding entity with a given
> textual description;

决定理由：主体范围错配：整体OpenWorld KGC管线面向开放世界挑战，EDP只是预测实体的辅助模块。

## 367 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：KG-S2S —IMPROVES_UPON→ previous KGC methods

Claim：`7ee1bf92813f061b5913155711028811e557351d52e05595221f4b5d8532c13d`；Chunk：`chunk_698f515094512215946d5aeda85c3347`。

原文引句：

> The model is distinct
> from previous KGC methods, in which it is randomly ini-
> tialized rather than using pre-trained models.

决定理由：对象泛化且关系不支持：与以往方法不同不表示继承，未具名previous KGC methods。

## 368 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：KG-S2S —EVALUATED_ON→ various types of KGC tasks, including Static KGC, Temporal KGC, and Few-shot KGC

Claim：`10c590b530689cee74d17fbbcd5de3e89dda718cd8753bf84912f5158fe5da85`；Chunk：`chunk_698f515094512215946d5aeda85c3347`。

原文引句：

> KG-S2S [147]
> is a comprehensive framework that can be applied to var-
> ious types of KGC tasks, including Static KGC, Temporal
> KGC, and Few-shot KGC.

决定理由：实体类型错误：静态/时序/few-shot KGC是任务类别集合，不是Dataset。

## 369 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：KG-S2S —ADDRESSES→ four key requirements of such models: scalability, quality, versatility, and simplicity

Claim：`acfd847bd83bb69b6aaaa7e721b8445aceb02f61609a7c3e1d443f0ba3b32e65`；Chunk：`chunk_698f515094512215946d5aeda85c3347`。

原文引句：

> To address these objectives, the proposed model employs a
> straightforward T5 small architecture.

决定理由：主体归属不清：来源开头T5-small四目标段属于前一模型，随后才介绍KG-S2S，不能跨段误绑定。

## 370 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：KG-S2S —IMPROVES_UPON→ standard triple KG fact

Claim：`029f67756907aa2d0ca82f03bdf6b6ff42e7fd6661aaa168f2db799e7abc7649`；Chunk：`chunk_698f515094512215946d5aeda85c3347`。

原文引句：

> To achieve this objective, KG-S2S
> reformulates the standard triple KG fact by introducing an
> additional element, forming a quadruple (h, r, t, m), where
> m represents the additional ”condition” element.

决定理由：客体类型错误：standard triple KG fact是表示形式，不是Method。

## 371 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：PaE —IMPROVES_UPON→ LLMs as Encoders

Claim：`d2a4d6ec24c2241eba22713a92e5b7b796a5d937b900f1dad583a46f41ed78b1`；Chunk：`chunk_853634b759a3d322c1de0d2b12626eb8`。

原文引句：

> Therefore, the PaE
> framework is much easier to finetune since we can only
> optimize the prediction heads and freeze the LLMs.

决定理由：方法大类比较不支持技术继承：易微调理由没有具体前身方法。

## 372 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：PaE —COMPARES_WITH→ PaG

Claim：`1688ba4d9e4994c47341bd809abac9c0fa557b12c153e9857917f12929389538`；Chunk：`chunk_853634b759a3d322c1de0d2b12626eb8`。

原文引句：

> Comparison between PaE and PaG.

决定理由：概念比较标题不足：PaE/PaG是框架类别，此处不是具体方法实验比较，避免把标题硬映射。

## 373 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 14–14 页。

关系：PaG —COMPARES_WITH→ PaE

Claim：`f7696b726760101ea98f4007301b501e8964b629d5f208904f925d64567055e0`；Chunk：`chunk_853634b759a3d322c1de0d2b12626eb8`。

原文引句：

> Comparison between PaE and PaG.

决定理由：概念比较标题不足：PaG/PaE是框架类别，此处不是具体方法实验比较。

## 374 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 15–15 页。

关系：initialize LLM-based coreferences resolution by replacing the previous LSTM encoder [208] with BERT —IMPROVES_UPON→ the previous LSTM encoder [208]

Claim：`8b1718a470f8c1646d66ca6b6c2730a9de576c12b4ddf8c6bf94d4409d58acc7`；Chunk：`chunk_eec189839351a22519a03dca5220fcc6`。

原文引句：

> initialize LLM-based coreferences resolution by replacing
> the previous LSTM encoder [208] with BERT. This work is
> followed by the introduction of SpanBERT [155] which is
> pre-trained on BERT architecture with a span-based masked
> language model (MLM).

决定理由：主体不是具名完整方法：替换LSTM编码器的动作未解析论文方案，不能原样建继承边。

## 375 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 15–15 页。

关系：CorefQA formulates coreference resolution as a question answering task —EVALUATED_ON→ question answering task

Claim：`5b70723a4a40bef60518f2e87cad153ecfa0434fca3ca70454990f160008c1dc`；Chunk：`chunk_eec189839351a22519a03dca5220fcc6`。

原文引句：

> CorefQA [210] formulates coreference
> resolution as a question answering task, where contextual
> queries are generated for each candidate mention and the
> coreferent spans are extracted from the document using the
> queries.

决定理由：实体类型错误：question answering task是任务重构，不是Dataset。

## 376 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 16–16 页。

关系：PiVE [163] —IMPROVES_UPON→ a smaller LLM like T5 to correct the errors in KGs generated by a larger LLM (e.g., ChatGPT)

Claim：`5324b2fa06947f369ffaddcb25c86af869c9d1bd53071d86285fb5af27cf4d79`；Chunk：`chunk_75ef96282698daad6c75bd596fc12226`。

原文引句：

> PiVE [163] proposes a prompting with
> an iterative verification framework that utilizes a smaller
> LLM like T5 to correct the errors in KGs generated by a
> larger LLM (e.g., ChatGPT).

决定理由：客体角色错误：小LLM纠错是PiVE自身实现描述，不是被其改进的另一Method。

## 377 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 16–16 页。

关系：COMET —IMPROVES_UPON→ constructs commonsense KGs by using existing tuples as a seed set of knowledge on which to train

Claim：`4b30da4a3eff8cc6bd5874e01d57aeb30e250a9b340d7efd176ee094444599b0`；Chunk：`chunk_e8d793e8b4540ae836e1d27c89d7ce15`。

原文引句：

> COMET [164]
> proposes a commonsense transformer model that constructs
> commonsense KGs by using existing tuples as a seed set of
> knowledge on which to train. Using this seed set, a LLM
> learns to adapt its learned representations to knowledge
> generation, and produces novel tuples that are high quality.

决定理由：客体角色错误：利用种子元组训练是COMET自身流程，不是另一方法。

## 378 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 16–16 页。

关系：BertNet —EVALUATED_ON→ competitive quality, diversity, and novelty with a richer set of new and complex relations

Claim：`aa86ad58535e30d6579788fb4bd119d9b3d8f4e547a9a2d6fcf054e71c4692d4`；Chunk：`chunk_e8d793e8b4540ae836e1d27c89d7ce15`。

原文引句：

> The constructed KGs show competitive quality,
> diversity, and novelty with a richer set of new and complex
> relations, which cannot be extracted by previous methods.

决定理由：实体类型错误：quality/diversity/novelty是效果属性，不是Dataset。

## 379 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 16–16 页。

关系：BertNet —IMPROVES_UPON→ previous methods

Claim：`c85795f05b03357ba79f3a123b964e1d1892e8998da3bcc7a0c2c95310835e5f`；Chunk：`chunk_e8d793e8b4540ae836e1d27c89d7ce15`。

原文引句：

> The constructed KGs show competitive quality,
> diversity, and novelty with a richer set of new and complex
> relations, which cannot be extracted by previous methods.

决定理由：对象不具体且关系混淆：previous methods无法识别，能力差异不等于技术继承。

## 380 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：JointGT —IMPROVES_UPON→ Ribeiro et al. [167]'s method

Claim：`336b8318dd0352166ab21e0433b1f17076dde7c27cebeb9ef25af872531ee66b`；Chunk：`chunk_13a426323d6550b9e56e04de8aeaed65`。

原文引句：

> Interestingly,
> Ribeiro et al. [167] also find that continue pre-training could
> further improve model performance.

决定理由：主体错配：引句只提Ribeiro继续预训练观点，没有JointGT继承关系。

## 381 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：JointGT —EVALUATED_ON→ input sub-KGs and corresponding text

Claim：`b5fa32a3a47f4c193ef96c7cdb6b3cbd12dc36c7f8396ddbe7067cf965247437`；Chunk：`chunk_13a426323d6550b9e56e04de8aeaed65`。

原文引句：

> Given input sub-KGs and corresponding text, JointGT first
> represents the KG entities and their relations as a sequence
> of tokens, then concatenate them with the textual tokens
> which are fed into LLM.

决定理由：实体类型错误：输入子KG与对应文本是数据形式，不是具名评测集。

## 382 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：JointGT —ADDRESSES→ explicitly incorporate rich graph semantics in KGs

Claim：`c189feeafaa3455aa282e9f017738a072d7c713497c5dc382578b36cb96dba3d`；Chunk：`chunk_13a426323d6550b9e56e04de8aeaed65`。

原文引句：

> To enhance LLMs with KG structure information,
> JointGT [42] proposes to inject KG structure-preserving
> representations into the Seq2Seq large language models.

决定理由：引句明确JointGT向Seq2Seq注入保结构KG表示以融合图语义，来源说明具体层和目标；作为综述主张保留。

## 383 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：Li et al. [168] —ADDRESSES→ few-shot scenario

Claim：`2ee8a92936b2a842ac264fecf69744fab1f90a314cc1b3c465d48e8b3f60568d`；Chunk：`chunk_13a426323d6550b9e56e04de8aeaed65`。

原文引句：

> Li et al. [168] focus on the few-shot
> scenario.

决定理由：主体不是方法：Li et al.作者组与focus on few-shot不能形成具名技术解决关系。

## 384 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：LLMs as classifiers for relation prediction —IMPROVES_UPON→ shallow neural networks

Claim：`fd243d4b8daf5497bd2a628aedf7ea01eba78bd446f6141d90645e0b4bf008aa`；Chunk：`chunk_bec56c976cf7f69e51147e85a05329b8`。

原文引句：

> Lukovnikov et al. [172] are the first to uti-
> lize LLMs as classifiers for relation prediction, resulting in a
> notable improvement in performance compared to shallow
> neural networks.

决定理由：对象泛化且关系混淆：优于浅层神经网络不证明技术继承。

## 385 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：QA-GNN —EVALUATED_ON→ question and candidate answer pairs

Claim：`aa66b36ce44bdfa9f7dde5d823053e9b16467d1477f7024419ed56a0f48b2b57`；Chunk：`chunk_bec56c976cf7f69e51147e85a05329b8`。

原文引句：

> QA-GNN [131]
> uses LLMs to encode the question and candidate answer
> pairs, which are adopted to estimate the importance of
> relative KG entities.

决定理由：实体类型错误：问题/候选答案对是输入单位，不是Dataset。

## 386 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：LLMs as classifiers for relation prediction —ADDRESSES→ relation prediction

Claim：`4b3bc9143441eb62be80e165976941b018db37996e91d5d63e7d51c718603133`；Chunk：`chunk_bec56c976cf7f69e51147e85a05329b8`。

原文引句：

> Lukovnikov et al. [172] are the first to uti-
> lize LLMs as classifiers for relation prediction, resulting in a
> notable improvement in performance compared to shallow
> neural networks.

决定理由：引句明确以LLM分类器执行关系预测；保留具体技术用途，来源归于综述引用[172]而非本项目发明。

## 387 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：QA-GNN —ADDRESSES→ question answering

Claim：`dad1c2d5ddcaa729ed0aeb8db85b87b7b7a5b7948e04bb5949b9e26df4751212`；Chunk：`chunk_bec56c976cf7f69e51147e85a05329b8`。

原文引句：

> QA-GNN [131]
> uses LLMs to encode the question and candidate answer
> pairs, which are adopted to estimate the importance of
> relative KG entities.

决定理由：来源同段明确QA-GNN编码问题/候选答案并构造子图由GNN推理，支持question answering用途。

## 388 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 17–17 页。

关系：Luo et al.'s method for relation retrieval —ADDRESSES→ relation retrieval

Claim：`8960a592acdfea0aa7d536d1abaf67172694fcad07fee3bce5d45b761142979a`；Chunk：`chunk_bec56c976cf7f69e51147e85a05329b8`。

原文引句：

> Luo et al. [173] use LLMs to calculate
> the similarities between relations and questions to retrieve
> related facts, formulated as
> s(r, q) = LLM(r)⊤LLM(q),

决定理由：主体尚未消歧：Luo et al.'s method只有作者描述，未解析成稳定具名方案，暂不强行合并。

## 389 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：Yan et al. [235] —EVALUATED_ON→ x = [CLS] q [SEP] p1 [SEP] · · · [SEP] pn [SEP]

Claim：`f9edfd92508bf32ce91f7d10c4dd9bbf32405f1e13618513babf59e55f569f5d`；Chunk：`chunk_4a9cd0f28567bc89210d1b27b2c754d9`。

原文引句：

> Then, it
> concatenates the question q and all paths p1, . . . , pn to make
> an input sample as
> x = [CLS] q [SEP] p1 [SEP] · · · [SEP] pn [SEP]. (16)

决定理由：实体类型错误：拼接问题/路径的公式是输入样本形式，不是Dataset；作者也未解析成方法。

## 390 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：Yan et al. [235] —IMPROVES_UPON→ entity/relation extractors

Claim：`fb7bd29f094d59996f475c562c6baeb049fab383aa984872c59e7ca768a15bc0`；Chunk：`chunk_4a9cd0f28567bc89210d1b27b2c754d9`。

原文引句：

> Given a candidate answer entity a, it extracts a
> series of paths p1, . . . , pn from KGs. But the second stage is a
> LLM-based answer reasoner. It first verbalizes the paths by
> using the entity names and relation names in KGs.

决定理由：证据不支持：描述路径提取和推理模块不能推出改进entity/relation extractors。

## 391 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：GreaseLM [178] —EVALUATED_ON→ KG facts and language context

Claim：`5d8b832ea8ca5f2a41c684a67089f8c6bf8e8e5befc7191c774ed2b18959eb15`；Chunk：`chunk_b1bd739c57f6cdf536000af5bc1af59a`。

原文引句：

> GreaseLM [178] fuses the representations
> from LLMs and graph neural networks to effectively reason
> over KG facts and language context.

决定理由：实体类型错误：KG facts and language context是知识来源，不是评测数据集。

## 392 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：UniKGQA [43] —EVALUATED_ON→ KGs

Claim：`d39e20ea467d910d76069752897207acc33abc8d16a211cc40bab1e29e49754f`；Chunk：`chunk_b1bd739c57f6cdf536000af5bc1af59a`。

原文引句：

> The second module is a matching information propagation
> module, which propagates the matching information along
> directed edges on KGs for answer reasoning.

决定理由：实体类型错误：KGs是推理载体，不是具名Dataset。

## 393 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：ReLMKG [179] —EVALUATED_ON→ KGs and language context

Claim：`b0046e14a5b31a9761d3a6b13fb2a8b74213dcd3537a948939ba8ff936e83546`；Chunk：`chunk_b1bd739c57f6cdf536000af5bc1af59a`。

原文引句：

> This process utilizes the explicit knowledge contained
> in the structured knowledge graph for reasoning purposes.

决定理由：实体类型错误：KGs and language context是知识来源，不是具名Dataset。

## 394 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 18–18 页。

关系：StructGPT [237] —EVALUATED_ON→ KGs and language context

Claim：`7c00c13f3d5986ad479acceaf834369db3ef286607c2072dd0fbe1cbf565e294`；Chunk：`chunk_b1bd739c57f6cdf536000af5bc1af59a`。

原文引句：

> StructGPT [237] adopts a customized interface to allow large
> language models (e.g., ChatGPT) directly reasoning on KGs
> to perform multi-step question answering.

决定理由：实体类型错误：KGs and language context是推理来源，不是具名Dataset。

## 395 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–19 页。

关系：LLM-KG Fusion Reasoning —IMPROVES_UPON→ KagNet [38]

Claim：`df0a2ffe4e7f9332d66ede54a44932aefbafb1988db1fb0765ac5829f4946423`；Chunk：`chunk_3e6e9684fba4b44fe201725df8351c03`。

原文引句：

> To improve the interac-
> tion between text and knowledge, KagNet [38] proposes
> to first encode the input KG, and then augment the input
> textual representation.

决定理由：分类与实例关系不是技术继承：Fusion Reasoning是类别，KagNet是其方案示例。

## 396 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–19 页。

关系：LLM-KG Fusion Reasoning —IMPROVES_UPON→ MHGRN [234]

Claim：`e1fd6ac194f4a576fb450565c5f76e263f5734fc930e4542e662b2ab13f3d493`；Chunk：`chunk_3e6e9684fba4b44fe201725df8351c03`。

原文引句：

> In contrast, MHGRN [234] uses the
> final LLM outputs of the input text to guide the reasoning
> process on the KGs. Yet, both of them only design a single-
> direction interaction between the text and KGs.

决定理由：分类与实例关系不是技术继承：Fusion Reasoning类别不能作为改进MHGRN的具体方法。

## 397 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–19 页。

关系：QA-GNN [131] —IMPROVES_UPON→ LLM-KG Fusion Reasoning

Claim：`d3899f13b02567320a5b263152f694d0d7505005be5d351a3b5743ee9da961b1`；Chunk：`chunk_3e6e9684fba4b44fe201725df8351c03`。

原文引句：

> To tackle this
> issue, QA-GNN [131] proposes to use a GNN-based model
> to jointly reason over input context and KG information
> via message passing.

决定理由：对象是技术类别，QA-GNN处理单向交互局限不证明继承整个Fusion Reasoning类目。

## 398 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–19 页。

关系：JointLK [245] —IMPROVES_UPON→ QA-GNN [131]

Claim：`66d4a56eddbd68e2137dbcdb8727d6254f7f16a833893df6cd04f25e4efd8d2e`；Chunk：`chunk_3e6e9684fba4b44fe201725df8351c03`。

原文引句：

> JointLK [245] then proposes a framework with fine-grained
> interaction between any tokens in the textual inputs and any
> KG entities through LM-to-KG and KG-to-LM bi-directional
> attention mechanism.

决定理由：证据不足：then与双向注意力说明不证明JointLK从QA-GNN技术继承。

## 399 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–20 页。

关系：GreaseLM [178] —IMPROVES_UPON→ ERNIE [35]

Claim：`c54ab230852175067003e32769c402011f956e9d36e080b7e625bc74fd659ad0`；Chunk：`chunk_e4807dad4de14061968abc8d682e2287`。

原文引句：

> The architecture and
> fusion approach is mostly similar to ERNIE [35] discussed in
> Section 6.1, except that GreaseLM does not use the text-only
> T-encoder to handle input text.

决定理由：关系不支持：架构mostly similar与差异不等于GreaseLM继承或改进ERNIE。

## 400 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 19–20 页。

关系：LLMs as Agents Reasoning —IMPROVES_UPON→ Two encoders to fuse the knowledge

Claim：`ef6d1fd1e26863ceddf6907b9fb31cdbd73b328702e6c413f89f4abd865eb17d`；Chunk：`chunk_e4807dad4de14061968abc8d682e2287`。

原文引句：

> Instead using two encoders
> to fuse the knowledge, LLMs can also be treated as agents
> to interact with the KGs to conduct reasoning [246]

决定理由：两个端点是框架类别/实现描述，替代方案不是具体技术继承。

## 401 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 20–20 页。

关系：LLM-KG Fusion Reasoning —ADDRESSES→ combines the LLM encoder and KG encoder to represent knowledge in a unified manner. It then employs a synergized reasoning module to jointly reason the results.

Claim：`c5d51bf85039e993df7dd0de5fa9fa08a4376402c5351e02efb00496693036be`；Chunk：`chunk_950b2707582c7e6fd06cd6fa9a79f7f1`。

原文引句：

> LLM-KG Fusion Reasoning
> combines the LLM encoder and KG encoder to represent
> knowledge in a unified manner. It then employs a syner-
> gized reasoning module to jointly reason the results.

决定理由：端点结构错误：主体为分类，客体为定义方法自身的长句，非明确Problem实体。

## 402 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 20–20 页。

关系：LLM as Agents for KG reasoning —ADDRESSES→ provides a flexible framework for reasoning on KGs without additional training cost, which can be generalized to different LLMs and KGs.

Claim：`575e3a62e13b3abde6836223db79240209c87fe330dacb2c0748cf0941041e05`；Chunk：`chunk_950b2707582c7e6fd06cd6fa9a79f7f1`。

原文引句：

> LLMs as Agents for KG reasoning provides a
> flexible framework for reasoning on KGs without additional
> training cost, which can be generalized to different LLMs
> and KGs.

决定理由：端点结构错误：主体为分类，客体为优势说明长句，非明确Problem实体。

## 403 · 拒绝

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 20–20 页。

关系：training a neural classifier on a small set of documents [249] —IMPROVES_UPON→ detect hallucination in LLMs

Claim：`60f50d57b993e36d96bc38fc74a248f48e108465b4e6fb1e65145413bec03ccd`；Chunk：`chunk_ebe1671c8c71b3df2be532362d2ecf84`。

原文引句：

> Existing methods strive to detect hallucination by training a
> neural classifier on a small set of documents [249], which are
> neither robust nor powerful to handle ever-growing LLMs.

决定理由：客体类型错误：detect hallucination是任务不是Method，原文还强调旧方法局限。

## 404 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 20–20 页。

关系：using KGs as an external source to validate LLMs [250] —ADDRESSES→ hallucination problem in LLMs

Claim：`5c34c25e25b7e4293a6b29a59f99a6218c4d17479041c802c1d35109e357ec78`；Chunk：`chunk_ebe1671c8c71b3df2be532362d2ecf84`。

原文引句：

> Recently, researchers try to use KGs as an external source
> to validate LLMs [250].

决定理由：来源幻觉检测段明确以外部KG验证LLM内容来检测/评估幻觉；仅保留综述[250]描述的用途，不主张解决全部幻觉。

## 405 · 批准

论文：Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 20–20 页。

关系：combining LLMs and KGs to achieve a generalized fact-checking model that can detect hallucinations across domains [251] —ADDRESSES→ hallucination problem in LLMs

Claim：`e874f18e20f9a18f877a6b5a78b33411d2ce9c2ddf1f3224b6e742b9198a4295`；Chunk：`chunk_ebe1671c8c71b3df2be532362d2ecf84`。

原文引句：

> Further studies combine LLMs
> and KGs to achieve a generalized fact-checking model that
> can detect hallucinations across domains [251]. Therefore,
> it opens a new door to utilizing KGs for hallucination
> detection.

决定理由：引句明确LLM+KG事实核查模型用于跨域幻觉检测；按综述[251]作者主张记录，不当作本项目验证。
