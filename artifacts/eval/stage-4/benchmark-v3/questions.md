# 阶段 4 关系路径覆盖题集 v3

共 40 题：8 道直接证据控制题、24 道跨论文关系路径题、8 道错误关系/无证据题。全题都设计为后续完整生成比较。
本题集是接触过语料和历史失败的开发集；参考要点来自冻结原文，不是独立人工金标。此版本尚未运行 Hybrid / Hybrid+Graph 对照。

## 固定来源与判分

- 每个必要事实单元按任一已核查来源命中计覆盖；题目所需事实单元之间按 AND 计算。
- 路径覆盖单独核查：关系方向、实体类型、来源块与页码均须匹配；引用格式正确不等于关系判断正确。
- 反例题核对题干中的指定边是否缺乏来源，且区分“当前证据未建立”与“证明从未发生”。
- 共享数据集不自动建立方法继承、因果、受控比较或普遍性能优越性。
- 图边存储整块精确原文与来源位置；不能把自动生成的图路径当作原文直接声明。

## 逐题题干、金标和来源

### F01 · fact

G-Retriever 将相关子图检索表述成什么优化问题？

**参考答案要点：** G-Retriever 将相关子图检索表述为 Prize-Collecting Steiner Tree（PCST）优化。

**必要事实：** G-Retriever 将图检索表述为 Prize-Collecting Steiner Tree 优化。

- `pcst`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`，PDF 第 1—1 页，块 `chunk_3a7f7a1f47b2586d9d9877afb9110567`；完整片段见 benchmark.json 和对应 Example。

### F02 · fact

KG-GPT 的三个处理阶段是什么，先后顺序怎样？

**参考答案要点：** Sentence Segmentation → Graph Retrieval → Inference。

**必要事实：** KG-GPT 三步为 Sentence Segmentation、Graph Retrieval、Inference。

- `kggpt`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`，PDF 第 1—1 页，块 `chunk_61e96cb10e247f7d002b4163920cc737`；完整片段见 benchmark.json 和对应 Example。

### F03 · fact

ToG-R 相对 ToG 是什么关系？替换了哪类剪枝，并报告什么调用上界？

**参考答案要点：** ToG-R 是 ToG 的变体，以随机实体剪枝替代 LLM 实体剪枝；论文给出的调用上界分别为 ToG 的 2ND+D+1、ToG-R 的 ND+D+1。

**必要事实：** ToG-R 用随机实体剪枝替代 LLM 实体剪枝；ToG 调用数 2ND+D+1，ToG-R 为 ND+D+1。

- `togr`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 22—22 页，块 `chunk_91a4a2e6943ad6a8074492d3f7229692`；完整片段见 benchmark.json 和对应 Example。

### F04 · fact

HippoRAG 用什么查询概念驱动的图算法连接跨段落证据？

**参考答案要点：** 它抽取查询关键概念作为种子，在知识图上运行 Personalized PageRank（PPR）。

**必要事实：** HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。

### F05 · fact

KGP 图中的节点和边分别可以表示什么？遍历代理负责什么？

**参考答案要点：** 节点可表示段落或文档结构；边可表示词法/语义相似或文档内结构；LLM 遍历代理选择邻居并收集支持段落。

**必要事实：** KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。

### F06 · fact

Tree-of-Traversals 的阈值、最大深度、最大扩展数分别会怎样结束搜索？

**参考答案要点：** 超过答案阈值可找到答案并停止；max depth 强制转入 done；max expansions 停止探索并返回 Cannot find answer。

**必要事实：** Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。

### F07 · fact

LPKG 如何把 KG 用于复杂问答规划？

**参考答案要点：** 它从 KG 构造 planning data，并用这些数据微调小模型的规划能力。

**必要事实：** LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。

- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 1—1 页，块 `chunk_e07b345ba2a42d01f295e47f196061d5`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 8—9 页，块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`；完整片段见 benchmark.json 和对应 Example。

### F08 · fact

Roadmap 将 LLM 与 KG 融合归纳为哪三条路线？

**参考答案要点：** KG-enhanced LLMs、LLM-augmented KGs、Synergized LLMs + KGs。

**必要事实：** 三类路线为 KG-enhanced LLMs、LLM-augmented KGs、Synergized LLMs + KGs。

- `roadmap`：Unifying Large Language Models and Knowledge Graphs: A Roadmap，`Surveys/010_Unifying Large Language Models and Knowledge Graphs A Roadmap.pdf`，PDF 第 1—1 页，块 `chunk_f9acd01074a4f478a8d9fe8c7e77be91`；完整片段见 benchmark.json 和对应 Example。

### R01 · cross

比较 ToG 与 ToG-2：问题到证据的流程中，搜索算法、实体和文档分别怎样参与？

**参考答案要点：** ToG 以 LLM 代理迭代束搜索探索 KG；ToG-2 将实体连接到文档，并交替进行图检索和上下文检索。

**必要事实：** ToG 将 LLM 当作代理，迭代执行 KG beam search，探索实体、关系和推理路径。；ToG-2 通过实体连接文档，用文档作为实体上下文，交替进行图检索与上下文检索。

**判分边界：** 不能因流程不同就断言 ToG-2 在所有条件下更优。

- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 1—1 页，块 `chunk_e09b5a88c34014513aad6c0d6121f790`；完整片段见 benchmark.json 和对应 Example。
- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 3—4 页，块 `chunk_d6a1257a27b9a4e3fd151b8c87ebf491`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 1—1 页，块 `chunk_9b63637ef18ed2d67ff105ef55092df3`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 3—3 页，块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`；完整片段见 benchmark.json 和对应 Example。

### R02 · cross

比较 HippoRAG 与 RoG：查询种子、关系路径计划和最终证据各处于哪一步？

**参考答案要点：** HippoRAG 用查询概念作 PPR 种子，在一次检索中整合跨段落信息；RoG 先生成 KG 约束的关系路径计划，再检索有效路径供推理。

**必要事实：** HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 不能把 RoG 的关系路径计划说成 PPR，也不能据此建立技术继承。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R03 · cross

CuriousLLM 如何增强 KGP？它的 Follow-upQA 训练样本把什么作为输入和目标？

**参考答案要点：** CuriousLLM 自述为对 KGP 的增强；KGP 使用文档图和遍历代理收集段落，Follow-upQA 以问题和证据为输入、以后续问题为目标。成本/幻觉评价属于论文作者报告。

**必要事实：** KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。

**判分边界：** 增强方向是 CuriousLLM → KGP，不得反转，也不能把作者报告说成此系统的复现实测。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。

### R04 · cross

StructGPT 与 LPKG 分别在推理和训练阶段怎样使用结构化数据或 KG？

**参考答案要点：** StructGPT 在回答时通过专门接口迭代读取结构化证据；LPKG 从 KG 构造 planning data 并微调规划能力。

**必要事实：** StructGPT 通过专门接口迭代读取结构化证据，再让 LLM 根据已取得信息推理。；LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。

**判分边界：** 不能把推理时读取接口等同于训练数据构建。

- `struct`：StructGPT: A General Framework for Large Language Model to Reason over Structured Data，`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`，PDF 第 1—1 页，块 `chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`；完整片段见 benchmark.json 和对应 Example。
- `struct`：StructGPT: A General Framework for Large Language Model to Reason over Structured Data，`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`，PDF 第 9—10 页，块 `chunk_bd4734d2765e2147cac924fe8ba38d85`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 1—1 页，块 `chunk_e07b345ba2a42d01f295e47f196061d5`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 8—9 页，块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`；完整片段见 benchmark.json 和对应 Example。

### R05 · cross

ToG 和 RoG 都用 KG，分别如何处理推理时搜索与训练阶段的知识？

**参考答案要点：** ToG 被描述为无需额外训练的在线 KG 搜索；RoG 包含 KG 知识蒸馏训练，推理时再进行关系路径计划与路径检索。

**必要事实：** ToG 将自身描述为 training-free，支持即插即用且无需额外训练。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** RoG 推理模块可接入其他 LLM 不等于整套 RoG 没有训练。

- `tog_training`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 1—1 页，块 `chunk_e09b5a88c34014513aad6c0d6121f790`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R06 · cross

比较 ToG-2 与 LPKG：图知识分别服务于什么阶段和目标？

**参考答案要点：** ToG-2 在推理时协作检索图和上下文；LPKG 用 KG 派生的规划数据进行训练。

**必要事实：** ToG-2 通过实体连接文档，用文档作为实体上下文，交替进行图检索与上下文检索。；LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。

**判分边界：** 共享 KG/QA 目标不表示训练协议或算法相同。

- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 1—1 页，块 `chunk_9b63637ef18ed2d67ff105ef55092df3`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 3—3 页，块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 1—1 页，块 `chunk_e07b345ba2a42d01f295e47f196061d5`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 8—9 页，块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`；完整片段见 benchmark.json 和对应 Example。

### R07 · cross

HippoRAG 与 KGP 的图节点/边从什么材料构成，检索如何回到证据？

**参考答案要点：** HippoRAG 将语料转为无模式 KG，以查询概念启动 PPR；KGP 用段落/文档结构作为节点，以相似或结构关系连边，再由代理收集支持段落。

**必要事实：** HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。

**判分边界：** 不能把 KGP 的节点定义直接套到 HippoRAG。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。

### R08 · cross

G-Retriever 与 ToG-2 怎样选择或组织用于生成的证据？

**参考答案要点：** G-Retriever 用 PCST 选择相关子图以控制大图上下文；ToG-2 通过实体连接文档并交替检索图与上下文。

**必要事实：** 整图文本化会超过上下文窗口，直接截断丢信息；G-Retriever 选择相关子图以扩展到大图。；G-Retriever 将图检索表述为 Prize-Collecting Steiner Tree 优化。；ToG-2 通过实体连接文档，用文档作为实体上下文，交替进行图检索与上下文检索。

**判分边界：** 不能声称 ToG-2 使用 PCST，也不能从机制描述推出两者资源实测相同。

- `grscale`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`，PDF 第 2—3 页，块 `chunk_5c9e14854565607ec53c355da481c451`；完整片段见 benchmark.json 和对应 Example。
- `pcst`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`，PDF 第 1—1 页，块 `chunk_3a7f7a1f47b2586d9d9877afb9110567`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 1—1 页，块 `chunk_9b63637ef18ed2d67ff105ef55092df3`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 3—3 页，块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`；完整片段见 benchmark.json 和对应 Example。

### R09 · cross

ToG 与 ToG-2 共同评测了哪些数据集？这条共享数据集关系能证明什么？

**参考答案要点：** 两篇都列出 WebQSP 和 QALD10-en；这只建立各自的评测关联，不能证明方法继承或受控性能优劣。

**必要事实：** ToG 在 KBQA 中使用 WebQSP、QALD10-en，也覆盖 Creak；共同数据集不保证一致实验条件。原文称各数据集采用 exact match accuracy (Hits@1)。；ToG-2 实验包含 WebQSP、QALD10-en、AdvHotpotQA 等，不能仅据数据集名称判定胜负。AdvHotpotQA 是 HotpotQA 挑战子集；FEVER/Creak 用 Acc.，其他用 EM；知识来源为 full Wikipedia/Wikidata。

**判分边界：** 共享数据集不等于相同划分、底座、知识来源或比较协议。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 5—5 页，块 `chunk_deb9eea46e529705dffdd1103729c44c`；完整片段见 benchmark.json 和对应 Example。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 6—6 页，块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`；完整片段见 benchmark.json 和对应 Example。

### R10 · cross

HippoRAG 与 Tree-of-Traversals 各自评测的 2Wiki 数据集名称是什么？其跨事实检索机制有何不同？

**参考答案要点：** HippoRAG 使用 2WikiMultiHopQA 并用 PPR；Tree-of-Traversals 列出 2WikiMultiHop，并搜索动作树。数据集名称和协议须分别保留。

**必要事实：** HippoRAG 主要评估 MuSiQue(answerable)、2WikiMultiHopQA，也纳入 HotpotQA。每个验证集取 1000 题，将对应支持和干扰段落组成检索语料。；Tree-of-Traversals 在 2WikiMultiHop、QALD-10 评估。；HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。

**判分边界：** 名称相似不证明划分、语料、底座或指标相同。

- `hippods`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 5—5 页，块 `chunk_3fa28005a4df0de5249826585cf9d713`；完整片段见 benchmark.json 和对应 Example。
- `totds`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 5—5 页，块 `chunk_a8ce6be635ba6abbbc71daeb86e809e9`；完整片段见 benchmark.json 和对应 Example。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。

### R11 · cross

比较 KG-GPT 与 RoG 的 MetaQA 实验：跳数/指标、Wiki-Movies 与 Freebase 分别是什么角色？

**参考答案要点：** KG-GPT 报告 MetaQA 1/2/3-hop Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是迁移训练来源，并取 1000 个训练样本。

**必要事实：** KG-GPT 表中包含 FACTKG 与 MetaQA(Hits@1)。；RoG 的迁移/扩展实验选 MetaQA-3hop，基于 Wiki-Movies，并取 1000 个训练样本。Freebase 是迁移训练来源，不是该 MetaQA-3hop 的测试知识图谱。

**判分边界：** 不能把 Freebase 写成 RoG MetaQA 测试 KG，也不以协议不一致的数字直接排名。

- `kggptds`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`，PDF 第 4—4 页，块 `chunk_3f7eb65828761447433c66c28ad111a4`；完整片段见 benchmark.json 和对应 Example。
- `rogmeta`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 20—20 页，块 `chunk_f5c88d605f651f26c093f30b836a98aa`；完整片段见 benchmark.json 和对应 Example。

### R12 · cross

MusicBrainz-x-Wikidata 与 CLQA-Wiki 各自怎样关联知识来源，题型有什么差别？

**参考答案要点：** Tree-of-Traversals 的 MusicBrainz-x-Wikidata 要综合两个 KG；CLQA-Wiki 来自 Wikidata 子集，含 multi-hop、comparison、intersection、union。

**必要事实：** MusicBrainz-x-Wikidata 有 109 题，需要结合 MusicBrainz 与 Wikidata。；CLQA-Wiki 来自 Wikidata 子集，覆盖 multi-hop、comparison、intersection、union。

**判分边界：** 都出现 Wikidata 不表示同一数据集或相同题型。

- `totmusic`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 5—6 页，块 `chunk_f4962498025654850621ee329d0af7d6`；完整片段见 benchmark.json 和对应 Example。
- `lpbench`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 2—2 页，块 `chunk_ab66789d9bc91de68948962d6c3f0011`；完整片段见 benchmark.json 和对应 Example。

### R13 · cross

HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 有何数据集关系和设置差异？

**参考答案要点：** ToG-2 把 AdvHotpotQA 描述为 HotpotQA 的挑战子集；HippoRAG 从验证集抽取问题并组合支持/干扰段落，ToG-2 报告 full Wikipedia/Wikidata 设置。

**必要事实：** HippoRAG 主要评估 MuSiQue(answerable)、2WikiMultiHopQA，也纳入 HotpotQA。每个验证集取 1000 题，将对应支持和干扰段落组成检索语料。；ToG-2 实验包含 WebQSP、QALD10-en、AdvHotpotQA 等，不能仅据数据集名称判定胜负。AdvHotpotQA 是 HotpotQA 挑战子集；FEVER/Creak 用 Acc.，其他用 EM；知识来源为 full Wikipedia/Wikidata。

**判分边界：** 不能把父集与挑战子集视为相同测试协议。

- `hippods`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 5—5 页，块 `chunk_3fa28005a4df0de5249826585cf9d713`；完整片段见 benchmark.json 和对应 Example。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 6—6 页，块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`；完整片段见 benchmark.json 和对应 Example。

### R14 · cross

ToG 与 ToG-2 对 Creak/QA 报告的指标与知识来源设置有何不同？跨论文比较还缺哪些条件？

**参考答案要点：** 按原文保留 ToG 的 exact match accuracy（Hits@1）；ToG-2 对 Creak/FEVER 报告 Acc.、其他数据集报告 EM，并写明 full Wikipedia/Wikidata。还须逐项核对划分、底座和提示条件。

**必要事实：** ToG 在 KBQA 中使用 WebQSP、QALD10-en，也覆盖 Creak；共同数据集不保证一致实验条件。原文称各数据集采用 exact match accuracy (Hits@1)。；ToG-2 实验包含 WebQSP、QALD10-en、AdvHotpotQA 等，不能仅据数据集名称判定胜负。AdvHotpotQA 是 HotpotQA 挑战子集；FEVER/Creak 用 Acc.，其他用 EM；知识来源为 full Wikipedia/Wikidata。

**判分边界：** 指标名称相近不等于受控比较；未提供的 ToG 条件不能补写。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 5—5 页，块 `chunk_deb9eea46e529705dffdd1103729c44c`；完整片段见 benchmark.json 和对应 Example。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 6—6 页，块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`；完整片段见 benchmark.json 和对应 Example。

### R15 · cross

Tree-of-Traversals 和 CuriousLLM 各用什么继续检索、停止或表示证据充分的机制？

**参考答案要点：** Tree-of-Traversals 用阈值、max depth、max expansions，三者停止含义不同；CuriousLLM 训练追问并用特殊 token 表示证据充分。

**必要事实：** Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。

**判分边界：** 预算上限/强制 done 不等于答案正确，也不能把 token 当作本项目的运行时停止器。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。

### R16 · cross

MindMap 与 RoG 如何把知识带入答案？可解释路径能否自动保证答案正确？

**参考答案要点：** MindMap 结合 LLM 隐式知识和外部 KG 并展示 mind map；RoG 通过关系计划检索有效推理路径。路径可追溯仍须逐项检查原文是否支持结论。

**必要事实：** MindMap 合并 LLM 隐式知识与外部 KG，以 mind map 展示推理路径，重点包括医学问答。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 可解释性不等于所有结论都通过事实验证。

- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`，PDF 第 1—1 页，块 `chunk_2f4809d54362f998c1c0710e915a721b`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R17 · cross

STaRK 与 MindMap 分别是什么类型的工作、涉及什么医学任务？这些信息能否证明 MindMap 在 STaRK 上评测过？

**参考答案要点：** STaRK 是覆盖精准医疗等领域的检索基准；MindMap 是包含医学 QA 场景的 KG prompting 方法。所给来源不能建立 MindMap EVALUATED_ON STaRK。

**必要事实：** STaRK 覆盖产品搜索、学术论文搜索和精准医疗。；MindMap 合并 LLM 隐式知识与外部 KG，以 mind map 展示推理路径，重点包括医学问答。

**判分边界：** 证据不足不能写成“证明从未评测”，也不能捏造分数。

- `stark`：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases，`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`，PDF 第 1—1 页，块 `chunk_6b5383484693f6226010eab8143f80d6`；完整片段见 benchmark.json 和对应 Example。
- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`，PDF 第 1—1 页，块 `chunk_2f4809d54362f998c1c0710e915a721b`；完整片段见 benchmark.json 和对应 Example。

### R18 · cross

KG-GPT 与 RoG 的处理流程分别如何排序？句子分割、关系规划、图/路径检索和推理属于哪一方？

**参考答案要点：** KG-GPT 是 Sentence Segmentation → Graph Retrieval → Inference；RoG 是 planning → retrieval → reasoning，且先规划关系路径。

**必要事实：** KG-GPT 三步为 Sentence Segmentation、Graph Retrieval、Inference。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 共有“检索/推理”步骤不代表流程相同或存在继承。

- `kggpt`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`，PDF 第 1—1 页，块 `chunk_61e96cb10e247f7d002b4163920cc737`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R19 · cross

ToG、HippoRAG、RoG 分别怎样完成多跳关联？

**参考答案要点：** ToG 迭代束搜索；HippoRAG 用查询种子驱动 PPR；RoG 先规划关系路径再检索有效路径。

**必要事实：** ToG 将 LLM 当作代理，迭代执行 KG beam search，探索实体、关系和推理路径。；HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 共同处理多跳不表示使用相同图操作或计算成本。

- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 1—1 页，块 `chunk_e09b5a88c34014513aad6c0d6121f790`；完整片段见 benchmark.json 和对应 Example。
- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 3—4 页，块 `chunk_d6a1257a27b9a4e3fd151b8c87ebf491`；完整片段见 benchmark.json 和对应 Example。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R20 · cross

ToG-2、HippoRAG、KGP 如何把图和文档/段落连接，再获得支持证据？

**参考答案要点：** ToG-2 用实体连接文档并协作检索；HippoRAG 从语料抽取图并用 PPR 跨片段检索；KGP 以段落/结构为图节点并通过代理收集支持段落。

**必要事实：** ToG-2 通过实体连接文档，用文档作为实体上下文，交替进行图检索与上下文检索。；HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。

**判分边界：** 三者节点、边和检索过程不可混为同一种表示。

- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 1—1 页，块 `chunk_9b63637ef18ed2d67ff105ef55092df3`；完整片段见 benchmark.json 和对应 Example。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 3—3 页，块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`；完整片段见 benchmark.json 和对应 Example。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。

### R21 · cross

比较 G-Retriever、Tree-of-Traversals、CuriousLLM：它们分别约束上下文、搜索空间还是证据缺口？

**参考答案要点：** G-Retriever 选择相关子图；Tree-of-Traversals 设深度与扩展边界；CuriousLLM 学习追问或给出证据充分信号。

**必要事实：** 整图文本化会超过上下文窗口，直接截断丢信息；G-Retriever 选择相关子图以扩展到大图。；Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。

**判分边界：** 不能从机制差异直接推出统一条件下速度或 Token 优势。

- `grscale`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`，PDF 第 2—3 页，块 `chunk_5c9e14854565607ec53c355da481c451`；完整片段见 benchmark.json 和对应 Example。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。

### R22 · cross

LPKG、CuriousLLM、RoG 的训练信号和推理用途分别是什么？

**参考答案要点：** LPKG 用 KG 派生 planning data；CuriousLLM 用问题和证据生成后续问题；RoG 有 KG 蒸馏训练，并在推理时做关系路径计划/检索。

**必要事实：** LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 不能互换监督目标或臆测训练数据完全相同。

- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 1—1 页，块 `chunk_e07b345ba2a42d01f295e47f196061d5`；完整片段见 benchmark.json 和对应 Example。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 8—9 页，块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### R23 · cross

比较 ToG/ToG-R 调用公式与 Tree-of-Traversals 搜索预算，为什么不能直接给统一运行时排名？

**参考答案要点：** ToG 与 ToG-R 的公式是 LLM 调用上界；Tree-of-Traversals 的 max depth/expansions 是搜索边界。两者不是同一量，也不等于墙钟时延。

**必要事实：** ToG-R 用随机实体剪枝替代 LLM 实体剪枝；ToG 调用数 2ND+D+1，ToG-R 为 ND+D+1。；Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。

**判分边界：** 不能反转变体方向，也不能将调用上界当作跨方法实测时延。

- `togr`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 22—22 页，块 `chunk_91a4a2e6943ad6a8074492d3f7229692`；完整片段见 benchmark.json 和对应 Example。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。

### R24 · cross

结合 CLQA-Wiki、2WikiMultiHop、MusicBrainz-x-Wikidata，区分多跳、交并逻辑与跨 KG 任务。

**参考答案要点：** CLQA-Wiki 明列多跳/比较/交/并；2WikiMultiHop 是多跳任务；MusicBrainz-x-Wikidata 要结合两个 KG。

**必要事实：** CLQA-Wiki 来自 Wikidata 子集，覆盖 multi-hop、comparison、intersection、union。；Tree-of-Traversals 在 2WikiMultiHop、QALD-10 评估。；MusicBrainz-x-Wikidata 有 109 题，需要结合 MusicBrainz 与 Wikidata。

**判分边界：** 这些属性可并存，不能由一项属性推出数据集没有其他题型。

- `lpbench`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`，PDF 第 2—2 页，块 `chunk_ab66789d9bc91de68948962d6c3f0011`；完整片段见 benchmark.json 和对应 Example。
- `totds`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 5—5 页，块 `chunk_a8ce6be635ba6abbbc71daeb86e809e9`；完整片段见 benchmark.json 和对应 Example。
- `totmusic`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 5—6 页，块 `chunk_f4962498025654850621ee329d0af7d6`；完整片段见 benchmark.json 和对应 Example。

### N01 · negative

HippoRAG 与 RoG 都做图上多跳推理，能否断言“RoG 直接继承 HippoRAG 的 PPR”？

**参考答案要点：** 两篇原文分别支持 PPR 检索与关系路径规划；给定来源未建立 RoG 继承 HippoRAG/PPR 的关系。

**必要事实：** HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。；RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 1—1 页，块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`；完整片段见 benchmark.json 和对应 Example。

### N02 · negative

ToG 与 ToG-2 都评测 WebQSP，是否足以证明“ToG-2 在所有数据集和所有底座上严格优于 ToG”？

**参考答案要点：** 共同评测关联不支持全称优越性；还需匹配划分、底座、知识来源、提示与完整结果。

**必要事实：** ToG 在 KBQA 中使用 WebQSP、QALD10-en，也覆盖 Creak；共同数据集不保证一致实验条件。原文称各数据集采用 exact match accuracy (Hits@1)。；ToG-2 实验包含 WebQSP、QALD10-en、AdvHotpotQA 等，不能仅据数据集名称判定胜负。AdvHotpotQA 是 HotpotQA 挑战子集；FEVER/Creak 用 Acc.，其他用 EM；知识来源为 full Wikipedia/Wikidata。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`，PDF 第 5—5 页，块 `chunk_deb9eea46e529705dffdd1103729c44c`；完整片段见 benchmark.json 和对应 Example。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`，PDF 第 6—6 页，块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`；完整片段见 benchmark.json 和对应 Example。

### N03 · negative

KGP 和 HippoRAG 都使用文档图，所以两者是否都是“段落节点、语义相似边”？

**参考答案要点：** KGP 明确包含段落或文档结构节点及相似/结构边；HippoRAG 把语料转为无模式 KG，节点语义不能直接互换。

**必要事实：** KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。；HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`，PDF 第 2—2 页，块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`；完整片段见 benchmark.json 和对应 Example。

### N04 · negative

KG-GPT 和 RoG 都涉及 MetaQA，是否能把 RoG 的 Freebase 迁移来源认作两者共同的 MetaQA 测试 KG？

**参考答案要点：** RoG 的 MetaQA-3hop 基于 Wiki-Movies；Freebase 是迁移训练来源，不是该测试 KG。

**必要事实：** KG-GPT 表中包含 FACTKG 与 MetaQA(Hits@1)。；RoG 的迁移/扩展实验选 MetaQA-3hop，基于 Wiki-Movies，并取 1000 个训练样本。Freebase 是迁移训练来源，不是该 MetaQA-3hop 的测试知识图谱。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `kggptds`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`，PDF 第 4—4 页，块 `chunk_3f7eb65828761447433c66c28ad111a4`；完整片段见 benchmark.json 和对应 Example。
- `rogmeta`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`，PDF 第 20—20 页，块 `chunk_f5c88d605f651f26c093f30b836a98aa`；完整片段见 benchmark.json 和对应 Example。

### N05 · negative

STaRK 有精准医疗领域、MindMap 有医学 QA，是否足以建立 MindMap→EVALUATED_ON→STaRK 并给出分数？

**参考答案要点：** 所给段落未建立该评测边或分数；只能说明当前证据不足，不能声称证明从未评测。

**必要事实：** STaRK 覆盖产品搜索、学术论文搜索和精准医疗。；MindMap 合并 LLM 隐式知识与外部 KG，以 mind map 展示推理路径，重点包括医学问答。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `stark`：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases，`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`，PDF 第 1—1 页，块 `chunk_6b5383484693f6226010eab8143f80d6`；完整片段见 benchmark.json 和对应 Example。
- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`，PDF 第 1—1 页，块 `chunk_2f4809d54362f998c1c0710e915a721b`；完整片段见 benchmark.json 和对应 Example。

### N06 · negative

给出虚构方法 NebulaGraphRAG-2099 继承 HippoRAG 后，在 LunarQA-2099 上相对 RoG 的官方精确提升分数。

**参考答案要点：** 冻结语料没有这些方法、基准或分数的证据；应指出无来源，不编造继承链和数值。

**必要事实：** 冻结语料无对应来源。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。


### N07 · negative

CuriousLLM 说自己增强 KGP，能否反向推出“KGP 用 CuriousLLM 的 Follow-upQA 训练”？

**参考答案要点：** 来源支持 CuriousLLM 增强 KGP 的方向；没有证据表明 KGP 使用 Follow-upQA 训练。

**必要事实：** KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`，PDF 第 1—1 页，块 `chunk_b959214e888053dae53b16a5259d7ea9`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。

### N08 · negative

Tree-of-Traversals 达到 max depth 或 max expansions，是否都代表证据充分且答案正确？

**参考答案要点：** max depth 强制进入 done，max expansions 返回 Cannot find answer；CuriousLLM 的充分证据 token 含义不同，均不自动保证答案正确。

**必要事实：** Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。；CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。

**判分边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`，PDF 第 4—4 页，块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`；完整片段见 benchmark.json 和对应 Example。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`，PDF 第 1—1 页，块 `chunk_43145c0748762d6b4c650c65721f826f`；完整片段见 benchmark.json 和对应 Example。
