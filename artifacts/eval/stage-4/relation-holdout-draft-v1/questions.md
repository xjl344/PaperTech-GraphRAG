# 新题目预览：Graph-only 与 Hybrid

**状态：草案，供用户审阅；未运行检索、未调用模型、未上传。**

新一轮只保留 Graph-only 与 Hybrid；历史三组记录原样保留。

8道事实控制＋24道跨论文关系＋8道错误前提核对。同一14篇论文、同一冻结图。
本轮换具体考点与论文组合，不以旧题换说法。部分事实已被接触，不能称作独立盲测。

先按原文拟题，再审计图中来源关联；不按哪组能赢来换题，不补图、不补别名。

## 题目清单

### 8道基础控制题

- **F01** HippoRAG 的 node specificity 如何计算？一个概念出现的段落越多，权重如何变化，这个权重在 PPR 前还是后使用？
- **F02** G-Retriever 怎样处理边奖励大于边成本、从而产生负边成本的情况？虚拟节点的奖励和新边成本如何设置？
- **F03** STaRK 的 LLM 重排实验对合成问题和人工问题分别重排多少候选？是否评测了全部测试问题，为什么？
- **F04** ToG-2 在第一次图检索前做了哪些准备？如果初始文档已经足够回答，还必须进入图搜索吗？
- **F05** MindMap 得到路径与邻居证据后，怎样减少信息过载并保留多样性？最终证据图怎样交给后续聚合阶段？
- **F06** StructGPT 在 KGQA、TableQA 和 Text-to-SQL 中，返回结果一定都是自然语言答案吗？请区分可以直接回答和需要执行的输出。
- **F07** KG-GPT 增大 top-k 关系数时，FACTKG 与 MetaQA 的效果是否相同？请区分检索三元组数量和任务准确率。
- **F08** KGP 的 TF-IDF 建图什么时候连接两个段落？为什么把文档标题也加入关键词集合？

### 24道跨论文关系题

- **R01** G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。
- **R02** LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。
- **R03** CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。
- **R04** KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。
- **R05** MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。
- **R06** ToG 的束搜索与 Tree-of-Traversals 的搜索状态回溯各保留什么选择机会？后者发现低价值状态后怎样换路？
- **R07** 请从论文库找出两种让“语义上相关的材料”在图中连起来的不同办法：一种连接不同叫法的概念，另一种学习相邻支持段落。分别说明建边依据和训练信号。
- **R08** ToG-2 和 STaRK 都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？
- **R09** HippoRAG 的“查询节点加邻居”消融与 KG-GPT 的 top-k 关系实验，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。
- **R10** 请找两篇直接讨论图证据冗余的工作：一篇分析图变密后支持事实覆盖与精度的取舍，另一篇通过聚类、采样保持多样性。它们分别控制哪个阶段？
- **R11** 面对结构化材料放不进提示词的问题，G-Retriever 与 StructGPT 分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。
- **R12** ToG-R 与 ToG-2 对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。
- **R13** CuriousLLM 复用的 MDR 段落编码器与 HippoRAG 的同义边编码器，分别学习或比较什么？请区分“下一段支持证据”和“概念名称相似”。
- **R14** RoG 的受约束广度优先搜索与 Tree-of-Traversals 的动作状态机怎样分别限制下一步动作？比较预先关系序列与可行操作空间。
- **R15** LPKG 的 CLQA-Wiki 与 STaRK 各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。
- **R16** StructGPT 与 KG-GPT 处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。
- **R17** KGP 为什么用真实邻居段落去匹配模型预测的下一条证据？结合 CuriousLLM 对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。
- **R18** 请从论文库举两个“图方法仍使用向量”的例子：一个用于把问题实体映射到图节点，另一个用于检索相关节点和边。比较向量所在的阶段，不能只回答方法名。
- **R19** G-Retriever 冻结 LLM 的软提示训练与 ToG-2 的 training-free 分别意味着什么？比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。
- **R20** ToG 的 training-free 和 StructGPT 的 zero-shot/few-shot 是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。
- **R21** KGP 预测下一段证据与 RoG 生成关系路径后，分别怎样约束实际检索？比较邻居段落的相似匹配与沿关系序列的图搜索。
- **R22** MindMap 的证据图合并和 CuriousLLM 的追问各会怎样改变后续可用信息？区分重组织已有证据与请求继续找证据。
- **R23** 请找出一项按候选答案条目集合衡量 Recall@k 的工作，以及一项可能生成 SQL 的结构化问答工作。为什么前者的 Recall@k 不能直接作为后者的 SQL 执行正确率？
- **R24** HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。

### 8道错误前提核对题

- **N01** “只要使用知识图谱，系统就不会再用向量相似度。”HippoRAG 与 G-Retriever 的方法细节能支持这句话吗？
- **N02** G-Retriever 冻结了 LLM，所以它没有任何需要训练的组件，也不使用软提示。这一说法符合原文吗？
- **N03** KGP 的图越密，支持事实覆盖和精度就必定一起提高；MindMap 因而也无需裁剪证据。请核对两项前提。
- **N04** STaRK 的 GPT-4 和 Claude3 重排器是在全部测试问题上、用相同候选数评测的吗？请指出这个说法省略的条件。
- **N05** HippoRAG 的消融已经证明，只要把查询节点的一跳邻居都加进来，就一定比只用查询节点效果好。原文是否这样报告？
- **N06** KGP 中模型预测的下一段证据能直接当作已核查原文引用吗？请用论文关于出生日期的例子检查。
- **N07** ToG-2 无论初始文档是否充分，都必须先完成一次图遍历才能回答。请检查它首次检索前后的控制流程。
- **N08** StructGPT 的所有任务都必须直接输出自然语言答案，因此它不涉及需要执行的 SQL。请核对原文的任务和结果定义。

## 审阅提示与后续口径

- 主指标拟为24道跨论文题的最终必要事实来源覆盖；同时报告候选召回、整题全覆盖和退化题。
- 8道反例本轮只核查来源召回，不以其检索结果判断模型是否纠正前提。
- 无实体锚点须计失败；Graph-only不回退Hybrid，不为新题补边/改别名。
- 草案来源为已核查的最小支持集合，并非全库穷尽金标。执行前需审核等价来源及完整原子事实。
- 原文块被图关联不等于本题事实已经建边；不把下面的静态审计当作预计分数。
- 关系题来源块关联分布：{'all_source_blocks_linked': 5, 'some_source_blocks_linked': 9, 'no_source_blocks_linked': 10}。详见 source-link-audit.json。
- 审阅完成后另冻正式版本与SHA-256，先核对LangSmith Dataset再运行两组Experiment。

## 每题参考要点、完整来源与位置

### F01

HippoRAG 的 node specificity 如何计算？一个概念出现的段落越多，权重如何变化，这个权重在 PPR 前还是后使用？

**参考要点（待审）：**

- 节点 i 的 specificity 为 1/|Pi|，Pi 是抽取出该节点的段落集合；出现段落越多权重越低；PPR 前与查询节点概率相乘。（chunk_3847660df4256f0bd39f8b49c7b9864e）

**相对旧题：** 新增节点加权细节

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 5–5；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_3847660df4256f0bd39f8b49c7b9864e`

**字符位置：** `[{"pdf_page": 5, "start_char": 789, "end_char": 2205, "chunk_start_char": 0, "chunk_end_char": 1416, "block_bboxes": [[107.641, 169.384, 504.345, 321.332], [108.0, 338.585, 227.887, 350.54], [108.0, 363.493, 166.381, 373.456]]}]`

```text
Node Specificity. We introduce node specificity as a neurobiologically plausible way to further
improve retrieval. It is well known that global signals for word importance, like inverse document
frequency (IDF), can improve information retrieval. However, in order for our brain to leverage IDF
for retrieval, the number of total “passages” encoded would need to be aggregated with all node
activations before memory retrieval is complete. While simple for normal computers, this process
would require activating connections between an aggregator neuron and all nodes in the hippocampal
index every time retrieval occurs, likely introducing prohibitive computational overhead. Given
these constraints, we propose node specificity as an alternative IDF signal which requires only local
signals and is thus more neurobiologically plausible. We define the node specificity of node i as
si = |Pi|−1, where Pi is the set of passages in P from which node i was extracted, information that
is already available at each node. Node specificity is used in retrieval by multiplying each query node
probability #»n with si before PPR; this allows us to modulate each of their neighborhood’s probability
as well as their own. We illustrate node specificity in Figure 2 through relative symbol size: the
Stanford logo grows larger than the Alzheimer’s symbol since it appears in fewer documents.
3
Experimental Setup
3.1
Datasets

```

### F02

G-Retriever 怎样处理边奖励大于边成本、从而产生负边成本的情况？虚拟节点的奖励和新边成本如何设置？

**参考要点（待审）：**

- Pe>Ce 时用虚拟节点替代原边，虚拟节点奖励 Pe-Ce，连接两个端点的新边成本为0。（chunk_5832b6bfb3218fc28548dbb991a42540）

**相对旧题：** 新增优化算法实现细节

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 7–7；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_5832b6bfb3218fc28548dbb991a42540`

**字符位置：** `[{"pdf_page": 7, "start_char": 2023, "end_char": 3540, "chunk_start_char": 0, "chunk_end_char": 1517, "block_bboxes": [[108.0, 410.428, 504.667, 436.729], [107.691, 441.585, 505.389, 538.896], [108.0, 553.177, 213.703, 563.14], [108.0, 571.643, 505.744, 605.024], [236.931, 611.056, 504.667, 624.69], [108.0, 630.433, 489.146, 642.121], [107.751, 646.942, 504.003, 667.924]]}]`

```text
cost(S) = |ES| × Ce,
(8)
and Ce denotes a predefined cost per edge, which is adjustable to control the subgraph size.
The original PCST algorithm is designed for node prizes only. However, given the significance of
edge semantics in certain scenarios, we adapt the algorithm to accommodate edge prizes as follows:
Consider an edge e with a cost Ce and a prize Pe. If Ce > Pe, it can be treated as a reduced edge cost
of Ce −Pe. However, if Pe > Ce, negative edge costs are not allowed in the original algorithm. Our
solution involves replacing edge e with a ‘virtual node’ ve, connected to both endpoints of e. This
virtual node is assigned a prize of Pe −Ce, and the cost of the two new edges leading to the virtual
node is set to zero. This modification effectively mirrors the original problem, as including edge e
in the original graph is analogous to including the virtual node in the modified graph. Finally, we
optimize the PCST problem using a near-linear time approach [9].
5.4
Answer Generation
Graph Encoder. Let S∗= (V ∗, E∗) represent the retrieved subgraph. We use a graph encoder to
model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].
Our approach for encoding the retrieved subgraph is defined as follows:
hg = POOL(GNNϕ1(S∗)) ∈Rdg,
(9)
Here, POOL denotes the mean pooling operation, and dg is the dimension of the graph encoder.
Projection Layer. We incorporate a multilayer perceptron (MLP) to align the graph token with the
vector space of the LLM:

```

### F03

STaRK 的 LLM 重排实验对合成问题和人工问题分别重排多少候选？是否评测了全部测试问题，为什么？

**参考要点（待审）：**

- 合成问题 k=20，人工问题 k=10；因计算成本高，只在随机10%测试问题上评测这些重排器。（chunk_bb730573725b148aa7913e7f17bb9261）

**相对旧题：** 新增评测范围与成本条件

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 7–7；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_bb730573725b148aa7913e7f17bb9261`

**字符位置：** `[{"pdf_page": 7, "start_char": 2413, "end_char": 3663, "chunk_start_char": 0, "chunk_end_char": 1250, "block_bboxes": [[108.0, 494.427, 504.004, 558.972], [107.691, 571.321, 452.128, 581.284], [108.0, 589.391, 504.004, 621.402], [108.0, 628.984, 505.247, 671.905]]}]`

```text
• LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of
top-k ada-002 results by reranking them using large language models. We employ GPT-4-turbo
(gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized
queries and k = 10 for human-generated queries. Given a query, the LLMs assign a satisfaction
score from 0 to 1 to each candidate entity based on textual and relational information. Due to high
computational costs, we evaluate these rerankers on a random 10% sample of test queries.
The performance of these models are measured using standard retrieval metrics below.
• Hit@k assesses whether the correct item is among the top-k results from the model. We used
k = 1 and k = 5 for evaluation. At k = 1, it evaluates the accuracy of the top recommendation; at
k = 5, it examines the model’s precision in a wider recommendation set.
• Recall@k measures the proportion of relevant items in the top-k results. For synthesized queries,
k = 20 is used, as the answer length of all of the queries in our benchmarks are equal or smaller
then 20. This metric offers insight into the model’s ability to identify all relevant items, particularly
in scenarios where missing any could be critical.

```

### F04

ToG-2 在第一次图检索前做了哪些准备？如果初始文档已经足够回答，还必须进入图搜索吗？

**参考要点（待审）：**

- 先实体链接、Topic Prune，再从初始主题实体关联文档中用稠密模型取 top-k 块；LLM 判断证据充分即可停止，无需进一步检索。（chunk_362a4aa0f89367fe96563183423db354）

**相对旧题：** 新增首次图检索前的早停顺序

**来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF物理页 4–4；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；`chunk_362a4aa0f89367fe96563183423db354`

**字符位置：** `[{"pdf_page": 4, "start_char": 1380, "end_char": 2784, "chunk_start_char": 0, "chunk_end_char": 1404, "block_bboxes": [[108.0, 471.527, 504.004, 525.556], [144.53, 515.234, 366.053, 527.918], [108.0, 532.529, 504.004, 564.41], [108.0, 554.447, 504.003, 586.328], [108.249, 600.998, 289.634, 610.961], [108.0, 621.291, 504.002, 664.361], [211.214, 652.888, 261.535, 666.723], [108.0, 650.552, 504.002, 677.951], [119.378, 665.973, 159.504, 679.955], [145.1, 665.973, 202.938, 679.955], [188.534, 665.973, 235.681, 680.075], [221.277, 666.71, 267.832, 680.075], [263.857, 666.71, 281.741, 679.892], [277.766, 665.973, 322.408, 679.892]]}]`

```text
Given a question q, ToG-2 first identifies the entities present in q and links them to entities in the
KG. This step can be done by different entity linking (EL) methods, such as LLMs or specialized EL
tools 1. Then, ToG-2 performs a Topic Prune (TP) step to select suitable entities as starting points
of exploring in a KG, which prompts the LLM to evaluate q and appearing entities, selecting topic
entities E0
topic = {e1, e2, . . . , eN} and N is determined by LLM.
Prior to the 1st-round graph retrieval, ToG-2 uses dense retrieval models (DRMs, including dual-
tower and single-tower models) to extract the top-k chunks from the documents associated with
the initial topic entities E0
topic. The LLM then evaluates whether this information is sufficient to
answer the question, drawing on its own knowledge. If it concludes that the available information is
adequate, no further steps will be required.
3.2
HYBRID KNOWLEDGE EXPLORATION
The following will illustrate how ToG-2 iteratively harmonizes and tightly couples heterogeneous
knowledge. The iterative process will be explained in two main parts, Context-enhanced Graph
Search and Knowledge-guided Context Retrieval.
Formally, in the i-th iteration, the topic
entities are denoted as Ei
topic = {ei
1, ei
2, . . . , ei
j} and their preceding triple paths are Pi−1 =
{P i−1
1
, P i−1
2
, . . . , P i−1
j
}, P i−1
j
= {p0
j, p1
j, . . . , pi−1

```

### F05

MindMap 得到路径与邻居证据后，怎样减少信息过载并保留多样性？最终证据图怎样交给后续聚合阶段？

**参考要点（待审）：**

- 按头实体聚类并对子图采样，裁剪路径与邻居证据图；LLM 再把不同证据子图合并为统一推理图。（chunk_18e6db2a25659ad12b8e68e6cc51dfda）

**相对旧题：** 新增剪枝及证据聚合细节

**来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF物理页 4–4；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；`chunk_18e6db2a25659ad12b8e68e6cc51dfda`

**字符位置：** `[{"pdf_page": 4, "start_char": 2813, "end_char": 3840, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[70.473, 467.882, 291.043, 546.646], [147.557, 533.981, 204.244, 547.145], [70.528, 535.628, 291.042, 641.465], [70.866, 652.14, 269.761, 663.049], [70.866, 669.733, 289.132, 694.188], [70.866, 683.033, 290.941, 761.921], [81.775, 764.519, 290.944, 775.483]]}]`

```text
q . This approach incor-
porates additional query-related evidence into Gq.
After exploration, we update Vq with newly added
intermediate nodes from bridging pathways. To
manage information overhead and maintain diver-
sity, we prune Gpath
q
and Gnei
q
by clustering and
sampling sub-graphs based on their head entities.
These pruning steps result in the final evidence
graph Gq, optimizing information while preserving
diversity. Specific details are shown in Appendix
E. We show the hallucination influence of results
using path-based exploration and neighbor-based
exploration components in the experiment part.
3.2
Step II: Evidence Graph Aggregation
In this phase, LLM is instructed to consolidate the
diverse evidence sub-graphs G∗
q into a unified rea-
soning graph Gm. This reasoning graph Gm, upon
completion, serves as an external augmented graph
input for Step III, providing a holistic perspective
on all evidence sub-graphs to enhance the output
generation process.
To generate the final additional knowledge sub-

```

### F06

StructGPT 在 KGQA、TableQA 和 Text-to-SQL 中，返回结果一定都是自然语言答案吗？请区分可以直接回答和需要执行的输出。

**参考要点（待审）：**

- 三类任务分别处理KG、表格、数据库；结果可以是自然语言自由回答，也可以是需执行以取得答案的SQL等结构化表达式。（chunk_3a66017788061f8f662ca365c955591a）

**相对旧题：** 新增输出契约

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 3–3；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_3a66017788061f8f662ca365c955591a`

**字符位置：** `[{"pdf_page": 3, "start_char": 1457, "end_char": 2482, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[191.464, 462.942, 224.205, 479.919], [212.74, 462.942, 288.634, 480.561], [70.866, 471.949, 280.313, 495.113], [70.866, 483.925, 289.133, 508.636], [70.866, 518.514, 291.042, 732.843], [81.775, 735.146, 278.466, 773.66], [306.142, 72.649, 374.705, 84.604], [306.142, 94.622, 375.306, 105.531]]}]`

```text
i
, c(h)
j )}, where c(k)
i
and c(h)
j
denote the i-th and j-th columns in the
k-th and h-th tables, respectively.
Problem Statement. This work mainly focuses
on using LLMs to solve complex reasoning tasks
based on structured data. Formally, it can be de-
scribed as a question answering task: given a nat-
ural language question q and an accessible struc-
tured data S (e.g., a knowledge graph, a table, or
database), the LLM needs to extract useful evi-
dence from S and then generates the expected re-
sult to answer the question q based on the extracted
evidence. According to the task requirement, the
generated result can be either free-form answers
in natural language or structured expressions (e.g.,
SQL statements) to be executed for obtaining the
answer from S. Since we consider three types of
structured data (Section 4), our tasks can be instan-
tiated as follows:
• KG based question answering (KGQA)
• Table based question answering (TableQA)
• DB based semantic parsing (Text-to-SQL)
4
Approach
4.1
Overview

```

### F07

KG-GPT 增大 top-k 关系数时，FACTKG 与 MetaQA 的效果是否相同？请区分检索三元组数量和任务准确率。

**参考要点（待审）：**

- FACTKG 随k增加检索三元组增多但准确率变化不大；MetaQA 中更大的k检索到更多重要三元组，性能改善。（chunk_fbbb8f38df6e66a40727407ca912ae1a）

**相对旧题：** 新增分任务消融结果

**来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF物理页 5–5；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；`chunk_fbbb8f38df6e66a40727407ca912ae1a`

**字符位置：** `[{"pdf_page": 5, "start_char": 0, "end_char": 1290, "chunk_start_char": 0, "chunk_end_char": 1290, "block_bboxes": [[70.866, 73.498, 290.946, 219.953], [70.866, 231.257, 221.095, 242.166], [70.528, 248.08, 290.949, 367.465], [70.528, 370.426, 289.139, 408.543], [70.866, 410.882, 289.132, 449.164], [70.866, 462.518, 145.933, 474.473]]}]`

```text
ceeding 90%, in both the 1-hop and 2-hop scenar-
ios, even with a minimal set of four examples. In
contrast, in both the FACTKG and MetaQA 3-hop
scenarios, the performance of the 4-shot learning
scenario was similar to that of the baselines which
did not utilize graph evidence. This similarity sug-
gests that LLMs may struggle to interpret com-
plex data features when equipped with only four
shots. Thus, the findings highlight the importance
of formulating in-context examples according to
the complexity of the task.
4.4.2
Top-K Relation Retrieval
Table 11 shows the performance according to the
value of k in FACTKG. As a result, performance
did not significantly vary depending on the value of
k. Table 12 illustrates the average number of triples
retrieved for both supported and refuted claims, de-
pending on k. Despite the increase in the number
of triples as the value of k grows, it does not im-
pact the accuracy. This suggests that the additional
triples are not significantly influential.
In MetaQA, the performance and the average
number of retrieved triples are also depicted in
Table 13 and Table 14, respectively. Unlike the
FACTKG experiment, as the value of k rises in
MetaQA, it appears that more significant triples are
retrieved, leading to improved performance.
5

```

### F08

KGP 的 TF-IDF 建图什么时候连接两个段落？为什么把文档标题也加入关键词集合？

**参考要点（待审）：**

- 先做TF-IDF关键词提取，加入文档标题因为部分问题关注标题实体；共享任一关键词的两个段落连接。（chunk_1da329a96f21568de531f98b40b330e7）

**相对旧题：** 新增词法建图规则

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 3–3；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_1da329a96f21568de531f98b40b330e7`

**字符位置：** `[{"pdf_page": 3, "start_char": 2234, "end_char": 3823, "chunk_start_char": 0, "chunk_end_char": 1589, "block_bboxes": [[54.0, 584.764, 292.505, 704.407], [319.5, 284.592, 558.005, 469.988]]}]`

```text
TF-IDF KG Construction
For adding edges according to
lexical similarity, we first apply TF-IDF keyword extrac-
tion (Ramos et al. 2003) over each document to filter out
meaningless words such as supporting verbs and articles,
which also reduces the dimension of bag-of-word (BOW)
features, sparsifies the constructed graph and increases the
graph traversal efficiency. In addition, we add the document
title into the extracted keyword set since some questions fo-
cus on title entities. We collect the extracted keywords from
all documents to form the keyword space W and then con-
nect two passages if they share any common keyword in W.
KNN-ST/MDR KG Construction
For adding edges ac-
cording to semantic similarity, we can readily employ pre-
existing models such as sentence transformers to gener-
ate passage embedding Xi for each node vi and subse-
quently compute pairwise similarity matrix to construct the
K-nearest neighbor (KNN) graph. However, these off-the-
shelf models, typically trained on tasks not so-related to
MD-QA, may not adequately encapsulate necessary logical
associations in their embedding similarity demanded by the
question. To overcome this problem, we follow the train-
ing strategy of MDR (Xiong et al. 2020) and train a sen-
tence encoder by predicting the subsequent supporting facts
based on previously supporting facts, thereby endowing the
encoder with reasoning capability. Consequently, the em-
bedding similarity and the corresponding constructed KNN
graph fundamentally encapsulate the necessary logical asso-
ciations between different passages.

```

### R01

G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。

**参考要点（待审）：**

- G-Retriever 面向带文本属性的图，生成文本回答并标出相关图部分，涵盖场景图、常识及知识图推理。（chunk_3a7f7a1f47b2586d9d9877afb9110567）
- KG-GPT 用于KG事实验证及KGQA，通过分割、图检索、推理处理结构化知识。（chunk_61e96cb10e247f7d002b4163920cc737）

**相对旧题：** 已有事实的新任务/输出对齐，非全新事实

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 1–1；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_3a7f7a1f47b2586d9d9877afb9110567`

**字符位置：** `[{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}]`

```text
Abstract
Given a graph with textual attributes, we enable users to ‘chat with their graph’:
that is, to ask questions about the graph using a conversational interface. In re-
sponse to a user’s questions, our method provides textual replies and highlights the
relevant parts of the graph. While existing works integrate large language models
(LLMs) and graph neural networks (GNNs) in various ways, they mostly focus
on either conventional graph tasks (such as node, edge, and graph classification),
or on answering simple graph queries on small or synthetic graphs. In contrast,
we develop a flexible question-answering framework targeting real-world textual
graphs, applicable to multiple applications including scene graph understanding,
common sense reasoning, and knowledge graph reasoning. Toward this goal, we
first develop a Graph Question Answering (GraphQA) benchmark with data col-
lected from different tasks. Then, we propose our G-Retriever method, introducing
the first retrieval-augmented generation (RAG) approach for general textual graphs,
which can be fine-tuned to enhance graph understanding via soft prompting. To
resist hallucination and to allow for textual graphs that greatly exceed the LLM’s
context window size, G-Retriever performs RAG over a graph by formulating this
task as a Prize-Collecting Steiner Tree optimization problem. Empirical evaluations
show that our method outperforms baselines on textual graph tasks from multiple
domains, scales well with larger graph sizes, and mitigates hallucination. 1
1

```

**来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF物理页 1–1；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；`chunk_61e96cb10e247f7d002b4163920cc737`

**字符位置：** `[{"pdf_page": 1, "start_char": 237, "end_char": 1173, "chunk_start_char": 0, "chunk_end_char": 936, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.516, 240.528, 273.87, 489.67], [70.866, 504.681, 153.68, 516.636]]}]`

```text
Abstract
While large language models (LLMs) have
made considerable advancements in under-
standing and generating unstructured text, their
application in structured data remains underex-
plored. Particularly, using LLMs for complex
reasoning tasks on knowledge graphs (KGs)
remains largely untouched. To address this,
we propose KG-GPT, a multi-purpose frame-
work leveraging LLMs for tasks employing
KGs. KG-GPT comprises three steps: Sentence
Segmentation, Graph Retrieval, and Inference,
each aimed at partitioning sentences, retriev-
ing relevant graph components, and deriving
logical conclusions, respectively. We evalu-
ate KG-GPT using KG-based fact verification
and KGQA benchmarks, with the model show-
ing competitive and robust performance, even
outperforming several fully-supervised models.
Our work, therefore, marks a significant step
in unifying structured and unstructured data
processing within the realm of LLMs.1
1

```

### R02

LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。

**参考要点（待审）：**

- LPKG 把落地的KG模式转成复杂问题及自然语言子问题，训练后解析并执行计划。（chunk_072d1d7f534ffdbb7644a330aeea94fa）
- RoG 生成KG约束的关系路径计划，用于检索有效推理路径。（chunk_58e7ae48fdb49536bc066f6e74ccd2a0）

**相对旧题：** 新增计划表示差异，不复问训练来源

**来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF物理页 2–2；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；`chunk_072d1d7f534ffdbb7644a330aeea94fa`

**字符位置：** `[{"pdf_page": 2, "start_char": 188, "end_char": 1158, "chunk_start_char": 0, "chunk_end_char": 970, "block_bboxes": [[70.473, 136.708, 291.045, 405.126]]}]`

```text
Knowledge Graphs (KGs) (Pan et al., 2017b,a)
usually store accurate knowledge in a structured
way. We find that a KG pattern can be viewed as
the abstract of a complex question, as shown in
Figure 1, which reveals the connection between
question planning and patterns. This opens up
the possibility of constructing training data to en-
hance the planning capabilities of LLMs using KGs.
Specifically, we start by grounding predefined pat-
terns in an open-domain KG to extract numerous
instances, which we then verbalize into complex
questions and corresponding sub-questions in nat-
ural language. In this way, we effectively create
a large number of accurate planning data for fine-
tuning. Being fine-tuned with these planning data,
LLMs’ capability of generating plans for complex
questions is enhanced, resulting in better final an-
swers by parsing and executing these plans. We
refer to this innovative framework as Learning to
Plan from Knowledge Graphs (LPKG).

```

**来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF物理页 1–1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`

**字符位置：** `[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

```text
ABSTRACT
Large language models (LLMs) have demonstrated impressive reasoning abili-
ties in complex tasks. However, they lack up-to-date knowledge and experience
hallucinations during reasoning, which can lead to incorrect reasoning processes
and diminish their performance and trustworthiness. Knowledge graphs (KGs),
which capture vast amounts of facts in a structured format, offer a reliable source
of knowledge for reasoning. Nevertheless, existing KG-based LLM reasoning
methods only treat KGs as factual knowledge bases and overlook the importance
of their structural information for reasoning. In this paper, we propose a novel
method called reasoning on graphs (RoG) that synergizes LLMs with KGs to
enable faithful and interpretable reasoning. Specifically, we present a planning-
retrieval-reasoning framework, where RoG first generates relation paths grounded
by KGs as faithful plans. These plans are then used to retrieve valid reasoning
paths from the KGs for LLMs to conduct faithful reasoning. Furthermore, RoG
not only distills knowledge from KGs to improve the reasoning ability of LLMs
through training but also allows seamless integration with any arbitrary LLMs dur-
ing inference. Extensive experiments on two benchmark KGQA datasets demon-
strate that RoG achieves state-of-the-art performance on KG reasoning tasks and
generates faithful and interpretable reasoning results1.
1

```

### R03

CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。

**参考要点（待审）：**

- CuriousLLM 用问题和支持证据生成后续问题来指导补充检索；充分时用特殊token。（chunk_43145c0748762d6b4c650c65721f826f）
- StructGPT 迭代接口调用、线性化与生成，接口负责读取证据，LLM负责推理。（chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad）

**相对旧题：** 已有机制的新跨论文中间产物组合

**来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF物理页 1–1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；`chunk_43145c0748762d6b4c650c65721f826f`

**字符位置：** `[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

```text
Abstract
Large Language Models (LLMs) have achieved
significant success in open-domain question an-
swering. However, they continue to face chal-
lenges such as hallucinations and knowledge
cutoffs. These issues can be mitigated through
in-context learning by providing LLMs with
relevant context before generating answers.
Recent literature proposes Knowledge Graph
Prompting (KGP) which integrates knowledge
graphs with an LLM-based traversal agent
to substantially enhance document retrieval
quality. However, KGP requires costly fine-
tuning with large datasets and remains prone
to hallucination. In this paper, we propose
CuriousLLM, an enhancement that integrates
a curiosity-driven reasoning mechanism into
an LLM agent. This mechanism enables the
agent to generate relevant follow-up questions,
thereby guiding the information retrieval pro-
cess more efficiently. Central to our approach
is the development of the new Follow-upQA
dataset, which includes questions and support-
ing evidence as input, with follow-up ques-
tions serving as ground truths. These follow-
up questions either inquire about what is still
missing to fully answer the user’s query or
use special tokens to signify that the retrieved
evidence is sufficient. Our experiments show
that CuriousLLM significantly boosts LLM per-
formance in multi-document question answer-
ing (MD-QA), circumventing the substantial
computational costs and latency from the orig-
inal KGP framework. Source code: https:
//github.com/zukangy/KGP-CuriousLLM.
1

```

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 1–1；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`

**字符位置：** `[{"pdf_page": 1, "start_char": 480, "end_char": 1582, "chunk_start_char": 0, "chunk_end_char": 1102, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.565, 238.04, 273.783, 523.046], [70.866, 535.569, 153.68, 547.524]]}]`

```text
Abstract
In this paper, we aim to improve the reason-
ing ability of large language models (LLMs)
over structured data in a unified way.
In-
spired by the studies on tool augmentation for
LLMs, we develop an Iterative Reading-then-
Reasoning (IRR) framework to solve question
answering tasks based on structured data, called
StructGPT. In this framework, we construct
the specialized interfaces to collect relevant ev-
idence from structured data (i.e., reading), and
let LLMs concentrate on the reasoning task
based on the collected information (i.e., rea-
soning). Specially, we propose an invoking-
linearization-generation procedure to support
LLMs in reasoning on the structured data with
the help of the interfaces. By iterating this
procedure with provided interfaces, our ap-
proach can gradually approach the target an-
swers to a given query. Experiments conducted
on three types of structured data show that
StructGPT greatly improves the performance
of LLMs, under the few-shot and zero-shot set-
tings. Our codes and data are publicly available
at https://github.com/RUCAIBox/StructGPT.
1

```

### R04

KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。

**参考要点（待审）：**

- KGP 的图遍历代理检索支持段落，节点也可包含文档结构。（chunk_b959214e888053dae53b16a5259d7ea9）
- STaRK 以SKB中的节点实体为真值答案，不是论文支持段落。（chunk_2c06f903c181ffbdb1246026daa909b0）

**相对旧题：** 新增不同检索对象的评价关系

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 1–1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_b959214e888053dae53b16a5259d7ea9`

**字符位置：** `[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

```text
Abstract
The ‘pre-train, prompt, predict’ paradigm of large language
models (LLMs) has achieved remarkable success in open-
domain question answering (OD-QA). However, few works
explore this paradigm in multi-document question answer-
ing (MD-QA), a task demanding a thorough understanding
of the logical associations among the contents and structures
of documents. To fill this crucial gap, we propose a Knowl-
edge Graph Prompting (KGP) method to formulate the right
context in prompting LLMs for MD-QA, which consists of
a graph construction module and a graph traversal module.
For graph construction, we create a knowledge graph (KG)
over multiple documents with nodes symbolizing passages or
document structures (e.g., pages/tables), and edges denoting
the semantic/lexical similarity between passages or document
structural relations. For graph traversal, we design an LLM-
based graph traversal agent that navigates across nodes and
gathers supporting passages assisting LLMs in MD-QA. The
constructed graph serves as the global ruler that regulates the
transitional space among passages and reduces retrieval la-
tency. Concurrently, the graph traversal agent acts as a local
navigator that gathers pertinent context to progressively ap-
proach the question and guarantee retrieval quality. Extensive
experiments underscore the efficacy of KGP for MD-QA, sig-
nifying the potential of leveraging graphs in enhancing the
prompt design and retrieval augmented generation for LLMs.
Our code: https://github.com/YuWVandy/KG-LLM-MDQA.
1

```

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 1–2；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_2c06f903c181ffbdb1246026daa909b0`

**字符位置：** `[{"pdf_page": 1, "start_char": 2018, "end_char": 2822, "chunk_start_char": 0, "chunk_end_char": 804, "block_bboxes": [[213.748, 488.924, 375.099, 501.701], [227.954, 523.982, 235.037, 532.185], [130.657, 509.872, 282.762, 531.915], [245.763, 540.827, 286.644, 546.296], [170.95, 507.828, 198.851, 514.664], [108.0, 635.613, 504.002, 678.354], [108.498, 693.226, 378.708, 713.912], [108.0, 733.145, 505.571, 742.022], [10.94, 220.04, 37.62, 560.0]]}, {"pdf_page": 2, "start_char": 0, "end_char": 753, "chunk_start_char": 805, "chunk_end_char": 1558, "block_bboxes": [[250.771, 74.612, 457.407, 81.471], [114.002, 97.247, 166.032, 104.106], [178.071, 85.86, 494.285, 117.566], [114.002, 133.189, 155.678, 140.049], [176.146, 121.802, 498.168, 153.508], [114.002, 176.643, 158.16, 183.503]]}]`

```text
Synthesized
Q&A Pairs (Large)
Human-Generated
Q&A Pairs (Small)
…
Need Fabric Guard 
water repellant that 
blocks harmful UV rays
Participants
[
]
…
Provide reference
Generate
Figure 1: STARK features queries on Semi-structured Knowledge Base (SKB) with textual and
relational knowledge, with node entities as ground-truth answers. STARK consists of synthesized
queries simulating user interactions with a SKB and human-generated queries which provide an
authentic reference. It evaluates LLM retrieval systems’ performance in providing accurate responses.
∗‡Equal first-author / senior contribution.
Correspondence: {shirwu, jamesz, jure}@cs.stanford.edu.
38th Conference on Neural Information Processing Systems (NeurIPS 2024) Track on Datasets and Benchmarks.
arXiv:2404.13207v3  [cs.IR]  20 Oct 2024

Example query
Title of ground-truth items(s)
STARK-AMAZON
Looking for durable Dart World brand dart flights that
<Amazon Standard Flights>
resist easy tearing. Any recommendations?
<Dart World Broken Glass Flight> (+12 more)
What are recommended scuba diving weights for experienced divers
<Sea Pearls Vinyl Coated Lace Thru Weight>
that would fit well with my Gorilla PRO XL waterproof bag?
STARK-MAG
Search publications by Hao-Sheng Zeng on non-Markovian dynamics.
<Distribution of non-Markovian intervals...>
<Comparison between non-Markovian...>
What are some nanofluid heat transfer research papers published by
<A Numerical Study on Convection Around A
scholars from Philadelphia University?
Suqare Cylinder using AL2O3-H2O Nanofluid>
STARK-PRIME

```

### R05

MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。

**参考要点（待审）：**

- MindMap 用LLM把证据子图合成统一推理图，再供后续生成。（chunk_18e6db2a25659ad12b8e68e6cc51dfda）
- G-Retriever 用GAT编码子图、均值池化得到图向量，再由MLP投影到LLM空间。（chunk_5832b6bfb3218fc28548dbb991a42540）

**相对旧题：** 新增图表示到模型输入的对齐

**来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF物理页 4–4；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；`chunk_18e6db2a25659ad12b8e68e6cc51dfda`

**字符位置：** `[{"pdf_page": 4, "start_char": 2813, "end_char": 3840, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[70.473, 467.882, 291.043, 546.646], [147.557, 533.981, 204.244, 547.145], [70.528, 535.628, 291.042, 641.465], [70.866, 652.14, 269.761, 663.049], [70.866, 669.733, 289.132, 694.188], [70.866, 683.033, 290.941, 761.921], [81.775, 764.519, 290.944, 775.483]]}]`

```text
q . This approach incor-
porates additional query-related evidence into Gq.
After exploration, we update Vq with newly added
intermediate nodes from bridging pathways. To
manage information overhead and maintain diver-
sity, we prune Gpath
q
and Gnei
q
by clustering and
sampling sub-graphs based on their head entities.
These pruning steps result in the final evidence
graph Gq, optimizing information while preserving
diversity. Specific details are shown in Appendix
E. We show the hallucination influence of results
using path-based exploration and neighbor-based
exploration components in the experiment part.
3.2
Step II: Evidence Graph Aggregation
In this phase, LLM is instructed to consolidate the
diverse evidence sub-graphs G∗
q into a unified rea-
soning graph Gm. This reasoning graph Gm, upon
completion, serves as an external augmented graph
input for Step III, providing a holistic perspective
on all evidence sub-graphs to enhance the output
generation process.
To generate the final additional knowledge sub-

```

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 7–7；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_5832b6bfb3218fc28548dbb991a42540`

**字符位置：** `[{"pdf_page": 7, "start_char": 2023, "end_char": 3540, "chunk_start_char": 0, "chunk_end_char": 1517, "block_bboxes": [[108.0, 410.428, 504.667, 436.729], [107.691, 441.585, 505.389, 538.896], [108.0, 553.177, 213.703, 563.14], [108.0, 571.643, 505.744, 605.024], [236.931, 611.056, 504.667, 624.69], [108.0, 630.433, 489.146, 642.121], [107.751, 646.942, 504.003, 667.924]]}]`

```text
cost(S) = |ES| × Ce,
(8)
and Ce denotes a predefined cost per edge, which is adjustable to control the subgraph size.
The original PCST algorithm is designed for node prizes only. However, given the significance of
edge semantics in certain scenarios, we adapt the algorithm to accommodate edge prizes as follows:
Consider an edge e with a cost Ce and a prize Pe. If Ce > Pe, it can be treated as a reduced edge cost
of Ce −Pe. However, if Pe > Ce, negative edge costs are not allowed in the original algorithm. Our
solution involves replacing edge e with a ‘virtual node’ ve, connected to both endpoints of e. This
virtual node is assigned a prize of Pe −Ce, and the cost of the two new edges leading to the virtual
node is set to zero. This modification effectively mirrors the original problem, as including edge e
in the original graph is analogous to including the virtual node in the modified graph. Finally, we
optimize the PCST problem using a near-linear time approach [9].
5.4
Answer Generation
Graph Encoder. Let S∗= (V ∗, E∗) represent the retrieved subgraph. We use a graph encoder to
model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].
Our approach for encoding the retrieved subgraph is defined as follows:
hg = POOL(GNNϕ1(S∗)) ∈Rdg,
(9)
Here, POOL denotes the mean pooling operation, and dg is the dimension of the graph encoder.
Projection Layer. We incorporate a multilayer perceptron (MLP) to align the graph token with the
vector space of the LLM:

```

### R06

ToG 的束搜索与 Tree-of-Traversals 的搜索状态回溯各保留什么选择机会？后者发现低价值状态后怎样换路？

**参考要点（待审）：**

- ToG 用LLM代理迭代执行图上的束搜索，探索实体关系与推理路径。（chunk_e09b5a88c34014513aad6c0d6121f790）
- Tree-of-Traversals 示例在低价值状态后回溯到最佳备选状态，再重新选择扩展。（chunk_50dee9a8765be04263849aca87ab67d3）

**相对旧题：** 新增失败后换路机制

**来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF物理页 1–1；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；`chunk_e09b5a88c34014513aad6c0d6121f790`

**字符位置：** `[{"pdf_page": 1, "start_char": 517, "end_char": 2163, "chunk_start_char": 0, "chunk_end_char": 1646, "block_bboxes": [[278.288, 276.647, 333.722, 288.602], [143.507, 303.075, 469.793, 532.166], [108.299, 556.334, 205.989, 568.289]]}]`

```text
ABSTRACT
Although large language models (LLMs) have achieved significant success in vari-
ous tasks, they often struggle with hallucination problems, especially in scenarios
requiring deep and responsible reasoning. These issues could be partially addressed
by introducing external knowledge graphs (KG) in LLM reasoning. In this paper,
we propose a new LLM-KG integrating paradigm “LLM ⊗KG” which treats the
LLM as an agent to interactively explore related entities and relations on KGs
and perform reasoning based on the retrieved knowledge. We further implement
this paradigm by introducing a new approach called Think-on-Graph (ToG), in
which the LLM agent iteratively executes beam search on KG, discovers the most
promising reasoning paths, and returns the most likely reasoning results. We use
a number of well-designed experiments to examine and illustrate the following
advantages of ToG: 1) compared with LLMs, ToG has better deep reasoning power;
2) ToG has the ability of knowledge traceability and knowledge correctability by
leveraging LLMs reasoning and expert feedback; 3) ToG provides a flexible plug-
and-play framework for different LLMs, KGs and prompting strategies without
any additional training cost; 4) the performance of ToG with small LLM models
could exceed large LLM such as GPT-4 in certain scenarios and this reduces the
cost of LLM deployment and application. As a training-free method with lower
computational cost and better generality, ToG achieves overall SOTA in 6 out of
9 datasets where most previous SOTAs rely on additional training. Our code is
publicly available at https://github.com/IDEA-FinAI/ToG.
1

```

**来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF物理页 2–2；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；`chunk_50dee9a8765be04263849aca87ab67d3`

**字符位置：** `[{"pdf_page": 2, "start_char": 1267, "end_char": 2108, "chunk_start_char": 0, "chunk_end_char": 841, "block_bboxes": [[370.61, 221.801, 421.171, 226.237], [419.771, 251.404, 427.607, 255.311], [493.514, 222.33, 501.778, 226.237], [470.519, 186.912, 478.783, 190.82], [464.968, 149.909, 473.37, 153.816], [467.083, 251.404, 475.484, 255.311], [441.259, 165.503, 477.303, 171.365], [441.884, 171.318, 476.68, 177.179], [387.265, 140.658, 407.847, 150.89], [404.177, 150.173, 412.631, 154.081], [431.665, 203.564, 456.624, 209.425], [452.281, 222.858, 460.663, 226.766], [395.983, 152.023, 398.862, 157.885], [377.482, 188.762, 459.565, 195.945], [443.295, 225.502, 446.183, 231.363], [122.736, 291.559, 124.688, 295.85], [124.272, 296.165, 126.223, 300.456], [94.004, 309.982, 149.786, 314.811], [143.134, 325.774, 149.992, 328.993], [129.755, 298.358, 136.613, 301.577], [105.474, 280.592, 135.385, 285.42], [105.993, 285.417, 134.868, 290.246], [109.577, 325.993, 116.532, 329.212], [118.35, 300.771, 120.884, 305.599], [163.856, 282.023, 272.288, 321.699], [288.522, 312.918, 311.9, 320.952], [307.612, 285.353, 326.474, 288.992], [298.024, 312.918, 342.496, 324.133], [316.201, 299.935, 329.527, 305.171], [361.117, 277.042, 514.097, 326.68], [70.866, 350.187, 524.41, 372.18], [70.866, 396.05, 289.139, 433.978]]}]`

```text
v=0.2
v=0.4
v=1.0
v=0.7
v=0.7
v=0.0
v=0.0
Select Inception
and Interstellar
I should 
ExpandKG
v=0.9
Select cast 
v=0.8
2
3
4
5
?
?
Select cast 
Select director
v=0.7
v=0.7
Select Inception
and Interstellar
v=0.8
4
4⃝Since the previous selection
yielded low-value states, the
model backtracks to the best
alternative state.
Answer: 
Michael Caine
Select cast 
Answer: 
Unknown
v=1.0
v=0.0
v=0.8
5
5⃝Tree-of-Traversals now has all the infor-
mation needed for the query and generates
two answers. The correct answer is given a
high value by the LLM and is returned to
the user.
Figure 1: An example of how Tree-of-Traversals uses a KG interface for the query, “What actor played in both
Inception and Interstellar?”.
quires no training, functions with black-box access
to the LLM, and works with any API accessible
KG. Our contributions are:

```

### R07

请从论文库找出两种让“语义上相关的材料”在图中连起来的不同办法：一种连接不同叫法的概念，另一种学习相邻支持段落。分别说明建边依据和训练信号。

**参考要点（待审）：**

- HippoRAG 用检索编码器表示的余弦相似度超过阈值来增加同义边。（chunk_008861356c216ab780f62dad7796e2d4）
- KGP 的MDR句子编码器学习由已知支持事实预测后续支持事实，再用嵌入相似构建KNN图。（chunk_1da329a96f21568de531f98b40b330e7）

**相对旧题：** 新增建边细节组合及无方法名入口

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 4–4；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_008861356c216ab780f62dad7796e2d4`

**字符位置：** `[{"pdf_page": 4, "start_char": 1381, "end_char": 2535, "chunk_start_char": 0, "chunk_end_char": 1154, "block_bboxes": [[107.253, 445.556, 505.658, 575.749]]}]`

```text
Offline Indexing. Our indexing process involves processing a set of passages P using an instruction-
tuned LLM L and a retrieval encoder M. As seen in Figure 2 we first use L to extract a set of noun
phrase nodes N and relation edges E from each passage in P via OpenIE. This process is done via
1-shot prompting of the LLM with the prompts shown in Appendix I. Specifically, we first extract a
set of named entities from each passage. We then add the named entities to the OpenIE prompt to
extract the final triples, which also contain concepts (noun phrases) beyond named entities. We find
that this two-step prompt configuration leads to an appropriate balance between generality and bias
towards named entities. Finally, we use M to add the extra set of synonymy relations E′ discussed
above when the cosine similarity between two entity representations in N is above a threshold τ. As
stated above, this introduces more edges to our hippocampal index and allows for more effective
pattern completion. This indexing process defines a |N| × |P| matrix P, which contains the number
of times each noun phrase in the KG appears in each original passage.

```

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 3–3；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_1da329a96f21568de531f98b40b330e7`

**字符位置：** `[{"pdf_page": 3, "start_char": 2234, "end_char": 3823, "chunk_start_char": 0, "chunk_end_char": 1589, "block_bboxes": [[54.0, 584.764, 292.505, 704.407], [319.5, 284.592, 558.005, 469.988]]}]`

```text
TF-IDF KG Construction
For adding edges according to
lexical similarity, we first apply TF-IDF keyword extrac-
tion (Ramos et al. 2003) over each document to filter out
meaningless words such as supporting verbs and articles,
which also reduces the dimension of bag-of-word (BOW)
features, sparsifies the constructed graph and increases the
graph traversal efficiency. In addition, we add the document
title into the extracted keyword set since some questions fo-
cus on title entities. We collect the extracted keywords from
all documents to form the keyword space W and then con-
nect two passages if they share any common keyword in W.
KNN-ST/MDR KG Construction
For adding edges ac-
cording to semantic similarity, we can readily employ pre-
existing models such as sentence transformers to gener-
ate passage embedding Xi for each node vi and subse-
quently compute pairwise similarity matrix to construct the
K-nearest neighbor (KNN) graph. However, these off-the-
shelf models, typically trained on tasks not so-related to
MD-QA, may not adequately encapsulate necessary logical
associations in their embedding similarity demanded by the
question. To overcome this problem, we follow the train-
ing strategy of MDR (Xiong et al. 2020) and train a sen-
tence encoder by predicting the subsequent supporting facts
based on previously supporting facts, thereby endowing the
encoder with reasoning capability. Consequently, the em-
bedding similarity and the corresponding constructed KNN
graph fundamentally encapsulate the necessary logical asso-
ciations between different passages.

```

### R08

ToG-2 和 STaRK 都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？

**参考要点（待审）：**

- ToG-2 增加上下文时BGE重排器收益较好，而LLM有效性下降，作者指出LLM受输入长度限制并考虑成本。（chunk_d4f6a4a037b6e147680603d67ba56fc0）
- STaRK 的LLM重排因成本高仅测试随机10%问题，合成/人工候选数为20/10。（chunk_bb730573725b148aa7913e7f17bb9261）

**相对旧题：** 新增重排条件及资源限制

**来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF物理页 9–9；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；`chunk_d4f6a4a037b6e147680603d67ba56fc0`

**字符位置：** `[{"pdf_page": 9, "start_char": 289, "end_char": 1176, "chunk_start_char": 0, "chunk_end_char": 887, "block_bboxes": [[108.0, 269.013, 504.003, 366.877], [108.249, 381.665, 259.02, 391.628], [327.215, 480.573, 502.587, 490.536]]}]`

```text
Then we conduct another experiment in Figure 3b to find the best setting of context numbers K.
Our findings indicate that BGE-Reranker tends to yield better results with longer context inputs,
whereas LLM shows diminished effectiveness. Nevertheless, the overall performance of the pruning
tool using BGE-Reranker slightly exceeds that of the LLM. We attribute this outcome to the fact that
reasonably more contexts allow for greater tolerance toward irrelevant documents, and DRMs can
handle a large number of candidates. While LLM possesses strong discriminative capabilities and
offers greater flexibility, its performance is significantly constrained by the input length. Thus, we
opt for entity pruning based on the DRM approach, considering its advantages in cost-effectiveness
and enhanced generalization.
4.5.3
WIDTH & DEPTH SETTINGS
Figure 4: Width and depth settings analysis.

```

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 7–7；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_bb730573725b148aa7913e7f17bb9261`

**字符位置：** `[{"pdf_page": 7, "start_char": 2413, "end_char": 3663, "chunk_start_char": 0, "chunk_end_char": 1250, "block_bboxes": [[108.0, 494.427, 504.004, 558.972], [107.691, 571.321, 452.128, 581.284], [108.0, 589.391, 504.004, 621.402], [108.0, 628.984, 505.247, 671.905]]}]`

```text
• LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of
top-k ada-002 results by reranking them using large language models. We employ GPT-4-turbo
(gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized
queries and k = 10 for human-generated queries. Given a query, the LLMs assign a satisfaction
score from 0 to 1 to each candidate entity based on textual and relational information. Due to high
computational costs, we evaluate these rerankers on a random 10% sample of test queries.
The performance of these models are measured using standard retrieval metrics below.
• Hit@k assesses whether the correct item is among the top-k results from the model. We used
k = 1 and k = 5 for evaluation. At k = 1, it evaluates the accuracy of the top recommendation; at
k = 5, it examines the model’s precision in a wider recommendation set.
• Recall@k measures the proportion of relevant items in the top-k results. For synthesized queries,
k = 20 is used, as the answer length of all of the queries in our benchmarks are equal or smaller
then 20. This metric offers insight into the model’s ability to identify all relevant items, particularly
in scenarios where missing any could be critical.

```

### R09

HippoRAG 的“查询节点加邻居”消融与 KG-GPT 的 top-k 关系实验，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。

**参考要点（待审）：**

- HippoRAG 不做PPR而直接加查询邻居的替代方法，比只用查询节点更差。（chunk_8245d0849e8cf0df364eb6980d96843c）
- KG-GPT FACTKG 增大k准确率变化不大，MetaQA 增大k表现改善。（chunk_fbbb8f38df6e66a40727407ca912ae1a）

**相对旧题：** 新增跨论文消融关系

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 8–8；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_8245d0849e8cf0df364eb6980d96843c`

**字符位置：** `[{"pdf_page": 8, "start_char": 179, "end_char": 1441, "chunk_start_char": 0, "chunk_end_char": 1262, "block_bboxes": [[108.0, 101.594, 504.004, 177.122], [107.641, 183.38, 504.344, 248.056], [108.0, 265.266, 377.707, 275.229]]}]`

```text
PPR Alternatives. As shown in Table 5 (rows 5-6), to examine how much of our results are due to
the strength of PPR, we replace the PPR output with the query node probability #»n multiplied by node
specificity values (row 5) and a version of this that also distributes a small amount of probability to the
direct neighbors of each query node (row 6). First, we find that PPR is a much more effective method
for including associations for retrieval on all three datasets compared to both simple baselines. It is
interesting to note that adding the neighborhood of Rq nodes without PPR leads to worse performance
than only using the query nodes themselves.
Ablations. As seen in Table 5 (rows 7-8), node specificity obtains considerable improvements on
MuSiQue and HotpotQA and yields almost no change in 2WikiMultiHopQA. This is likely because
2WikiMultiHopQA relies on named entities with little differences in terms of term weighting. In
contrast, synonymy edges have the largest effect on 2WikiMultiHopQA, suggesting that noisy entity
standardization is useful when most relevant concepts are named entities, and improvements to
synonymy detection could lead to stronger performance in other datasets.
5.2
HippoRAG’s Advantage: Single-Step Multi-Hop Retrieval

```

**来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF物理页 5–5；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；`chunk_fbbb8f38df6e66a40727407ca912ae1a`

**字符位置：** `[{"pdf_page": 5, "start_char": 0, "end_char": 1290, "chunk_start_char": 0, "chunk_end_char": 1290, "block_bboxes": [[70.866, 73.498, 290.946, 219.953], [70.866, 231.257, 221.095, 242.166], [70.528, 248.08, 290.949, 367.465], [70.528, 370.426, 289.139, 408.543], [70.866, 410.882, 289.132, 449.164], [70.866, 462.518, 145.933, 474.473]]}]`

```text
ceeding 90%, in both the 1-hop and 2-hop scenar-
ios, even with a minimal set of four examples. In
contrast, in both the FACTKG and MetaQA 3-hop
scenarios, the performance of the 4-shot learning
scenario was similar to that of the baselines which
did not utilize graph evidence. This similarity sug-
gests that LLMs may struggle to interpret com-
plex data features when equipped with only four
shots. Thus, the findings highlight the importance
of formulating in-context examples according to
the complexity of the task.
4.4.2
Top-K Relation Retrieval
Table 11 shows the performance according to the
value of k in FACTKG. As a result, performance
did not significantly vary depending on the value of
k. Table 12 illustrates the average number of triples
retrieved for both supported and refuted claims, de-
pending on k. Despite the increase in the number
of triples as the value of k grows, it does not im-
pact the accuracy. This suggests that the additional
triples are not significantly influential.
In MetaQA, the performance and the average
number of retrieved triples are also depicted in
Table 13 and Table 14, respectively. Unlike the
FACTKG experiment, as the value of k rises in
MetaQA, it appears that more significant triples are
retrieved, leading to improved performance.
5

```

### R10

请找两篇直接讨论图证据冗余的工作：一篇分析图变密后支持事实覆盖与精度的取舍，另一篇通过聚类、采样保持多样性。它们分别控制哪个阶段？

**参考要点（待审）：**

- KGP 图变密时支持事实覆盖上升而精度下降；这是建图/邻居候选的取舍。（chunk_720b9036bf8c30eaf69c980fccbcec6d）
- MindMap 对已探索的路径和邻居证据子图聚类采样，属于证据选择与压缩。（chunk_18e6db2a25659ad12b8e68e6cc51dfda）

**相对旧题：** 新增冗余控制与无方法名入口

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 4–4；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_720b9036bf8c30eaf69c980fccbcec6d`

**字符位置：** `[{"pdf_page": 4, "start_char": 1020, "end_char": 2619, "chunk_start_char": 0, "chunk_end_char": 1599, "block_bboxes": [[54.0, 519.102, 292.505, 704.407], [319.5, 290.474, 558.005, 410.026]]}]`

```text
To verify the constructed KGs indeed encode the neces-
sary information for MD-QA, we randomly sample ques-
tions from HotpotQA and construct KGs over the set of
documents for each of these questions using our proposed
methods. We vary the hyperparameters to control the spar-
sity of the constructed KG and measure how much percent-
age of the supporting facts are covered by neighbors of the
seeding passages initially searched by TF-IDF. More details
about the four construction methods and their hyperparame-
ters are included in Section 8.5 in Supplementary. As shown
in Figure 5, as the constructed graph becomes denser, the
chance that the neighboring node passages hit the support-
ing facts increases (i.e., SF-EM increases) although the re-
dundant information also increases (i.e., the precision de-
creases). Given the common keywords shared between one
passage to all other passages are typically far less than the
total number of passages across all documents, the density of
the constructed graph by TF-IDF would be upper-bounded,
causing lower SF-EM (evidenced by SF-EM below 0.7 in
Figure 5 for TF-IDF curve). For TAGME, we empirically
find it identifies a larger quantity of entities mentioned in
a single passage, which leads to a denser graph and causes
the starting SF-EM of TAGME to be already around 0.95.
In addition, since KNN-MDR is pre-trained by predicting
the next supporting facts (Xiong et al. 2020) on HotpotQA,
it achieves better trade-off than KNN-ST where the embed-
dings are directly obtained from the sentence transformer
without dataset-specific pre-training.

```

**来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF物理页 4–4；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；`chunk_18e6db2a25659ad12b8e68e6cc51dfda`

**字符位置：** `[{"pdf_page": 4, "start_char": 2813, "end_char": 3840, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[70.473, 467.882, 291.043, 546.646], [147.557, 533.981, 204.244, 547.145], [70.528, 535.628, 291.042, 641.465], [70.866, 652.14, 269.761, 663.049], [70.866, 669.733, 289.132, 694.188], [70.866, 683.033, 290.941, 761.921], [81.775, 764.519, 290.944, 775.483]]}]`

```text
q . This approach incor-
porates additional query-related evidence into Gq.
After exploration, we update Vq with newly added
intermediate nodes from bridging pathways. To
manage information overhead and maintain diver-
sity, we prune Gpath
q
and Gnei
q
by clustering and
sampling sub-graphs based on their head entities.
These pruning steps result in the final evidence
graph Gq, optimizing information while preserving
diversity. Specific details are shown in Appendix
E. We show the hallucination influence of results
using path-based exploration and neighbor-based
exploration components in the experiment part.
3.2
Step II: Evidence Graph Aggregation
In this phase, LLM is instructed to consolidate the
diverse evidence sub-graphs G∗
q into a unified rea-
soning graph Gm. This reasoning graph Gm, upon
completion, serves as an external augmented graph
input for Step III, providing a holistic perspective
on all evidence sub-graphs to enhance the output
generation process.
To generate the final additional knowledge sub-

```

### R11

面对结构化材料放不进提示词的问题，G-Retriever 与 StructGPT 分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。

**参考要点（待审）：**

- G-Retriever 通过相关子图选择缓解整图文本化超窗口或截断丢信息的问题。（chunk_5c9e14854565607ec53c355da481c451）
- StructGPT 指出整份结构化数据线性化太大，以专门接口操纵和缩小所需记录范围。（chunk_296f2400fee163aad415c87ede01d3fa）

**相对旧题：** 新论文组合的输入裁剪位置比较

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 2–3；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_5c9e14854565607ec53c355da481c451`

**字符位置：** `[{"pdf_page": 2, "start_char": 5377, "end_char": 6545, "chunk_start_char": 0, "chunk_end_char": 1168, "block_bboxes": [[108.0, 586.878, 505.247, 673.291], [107.671, 679.55, 504.666, 722.414], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 3, "start_char": 0, "end_char": 302, "chunk_start_char": 1169, "chunk_end_char": 1471, "block_bboxes": [[168.567, 79.054, 443.126, 89.017], [115.77, 114.927, 128.937, 121.901], [249.671, 108.103, 269.888, 112.519], [254.373, 133.834, 265.179, 138.25], [253.452, 120.655, 299.773, 127.581], [276.078, 115.32, 279.876, 119.736], [275.608, 135.402, 324.86, 141.388], [307.236, 120.968, 330.932, 125.385], [309.393, 108.103, 327.516, 112.519], [240.86, 148.186, 489.169, 163.13], [115.77, 201.212, 202.238, 208.186]]}]`

```text
Enhancing Scalability and Efficiency in Graph LLMs. Recent research endeavors have explored
translating graphs into natural language, such as by flattening nodes and edges into a text sequence,
enabling their processing by LLMs for graph-based tasks [56, 6]. However, this method faces critical
scalability issues. Converting a graph with thousands of nodes and edges into a text sequence results
in an excessive number of tokens, surpassing the input capacity of many LLMs. An alternative of
truncating the graph text sequence to fit the LLM’s input token limit leads to loss of information and
response quality. G-Retriever overcomes these issues with its RAG component, which allows for
effective scaling to larger graphs by selectively retrieving only relevant parts of the graph.
Tailoring the RAG Approach to Graphs. Existing RAG methodologies are primarily designed
for simpler data types or knowledge graphs, where information is retrieved in a manner isolated
from the graph structure [7, 1, 36, 16]. Hence, we introduce a new retrieval approach for general
textual graphs. Notably, we formulate subgraph retrieval as a Prize-Collecting Steiner Tree (PCST)
2

Table 1: Observation and mitigation of hallucination in graph LLMs.
User
elephants
grass
eating
bushes
in
river
on the side of
standing by
elephant
What kind of animal is in the bushes?
Answer the question and list the nodes or edges from the graph that support your answer.
LLM w/ Graph Prompt Tuning

```

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 1–1；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_296f2400fee163aad415c87ede01d3fa`

**字符位置：** `[{"pdf_page": 1, "start_char": 2343, "end_char": 3728, "chunk_start_char": 0, "chunk_end_char": 1385, "block_bboxes": [[305.749, 215.202, 526.225, 497.177], [305.629, 502.637, 526.317, 594.744]]}]`

```text
issues is to augment LLMs with external knowl-
edge resources, so as to amend the incorrect gen-
erations. Among these resources, structured data
(e.g., knowledge graphs and databases), has been
widely used as the carrier of the required knowl-
edge for LLMs. Unlike plain text, structured data is
organized in a standardized format, conforming to
some logical data model. For example, knowledge
graphs (KGs) are often organized as fact triples
that state the relations between head entities and
tail entities, and data tables are organized in the
form of column-indexed records by rows. How-
ever, as structured data has special data formats
or schemas that LLMs have not seen during pre-
training, they may be not fully grasped or under-
stood by LLMs (Wei et al., 2021). A straightfor-
ward way to solve this problem is to linearize the
structured data into a sentence that LLMs can well
understand. While, the amount of structured data
is often vast, making it infeasible to include all the
data records in the input prompt.
Regarding the above challenges, we are inspired
by the tool manipulation strategy for augmenting
the abilities of LLMs (Schick et al., 2023; Nakano
et al., 2021). Our basic idea is to incorporate spe-
cialized interfaces (e.g., extracting columns from
tables) to manipulate the structured data records.
With these interfaces, we can effectively reduce the

```

### R12

ToG-R 与 ToG-2 对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。

**参考要点（待审）：**

- ToG-R 以随机实体剪枝替代ToG中的LLM实体剪枝。（chunk_91a4a2e6943ad6a8074492d3f7229692）
- ToG-2 以文档作为实体上下文以支持图检索，并用实体联接文档。（chunk_9b63637ef18ed2d67ff105ef55092df3）

**相对旧题：** 已有关系的新实体消歧/筛选组合

**来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF物理页 22–22；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；`chunk_91a4a2e6943ad6a8074492d3f7229692`

**字符位置：** `[{"pdf_page": 22, "start_char": 662, "end_char": 2113, "chunk_start_char": 0, "chunk_end_char": 1451, "block_bboxes": [[107.641, 238.664, 505.247, 402.282]]}]`

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

**来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF物理页 1–1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；`chunk_9b63637ef18ed2d67ff105ef55092df3`

**字符位置：** `[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

```text
Retrieval-augmented generation (RAG) has improved large language models
(LLMs) by using knowledge retrieval to overcome knowledge deficiencies. How-
ever, current RAG methods often fall short of ensuring the depth and complete-
ness of retrieved information, which is necessary for complex reasoning tasks.
In this work, we introduce Think-on-Graph 2.0 (ToG-2), a hybrid RAG frame-
work that iteratively retrieves information from both unstructured and structured
knowledge sources in a tight-coupling manner.
Specifically, ToG-2 leverages
knowledge graphs (KGs) to link documents via entities, facilitating deep and
knowledge-guided context retrieval. Simultaneously, it utilizes documents as en-
tity contexts to achieve precise and efficient graph retrieval. ToG-2 alternates
between graph retrieval and context retrieval to search for in-depth clues rele-
vant to the question, enabling LLMs to generate answers. We conduct a series
of well-designed experiments to highlight the following advantages of ToG-2:
1) ToG-2 tightly couples the processes of context retrieval and graph retrieval,
deepening context retrieval via the KG while enabling reliable graph retrieval
based on contexts; 2) it achieves deep and faithful reasoning in LLMs through
an iterative knowledge retrieval process of collaboration between contexts and
the KG; and 3) ToG-2 is training-free and plug-and-play compatible with vari-
ous LLMs. Extensive experiments demonstrate that ToG-2 achieves overall state-
of-the-art (SOTA) performance on 6 out of 7 knowledge-intensive datasets with
GPT-3.5, and can elevate the performance of smaller models (e.g
```

### R13

CuriousLLM 复用的 MDR 段落编码器与 HippoRAG 的同义边编码器，分别学习或比较什么？请区分“下一段支持证据”和“概念名称相似”。

**参考要点（待审）：**

- CuriousLLM 延用MDR训练，使用HotpotQA学习支持段落对接近、无关段落远离以建图。（chunk_69407b618c1969f701e74bd3cf523c95）
- HippoRAG 对抽取的概念表示计算余弦相似度，用阈值增加同义边。（chunk_008861356c216ab780f62dad7796e2d4）

**相对旧题：** 新增编码器目标与粒度比较

**来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF物理页 3–4；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；`chunk_69407b618c1969f701e74bd3cf523c95`

**字符位置：** `[{"pdf_page": 3, "start_char": 2170, "end_char": 3088, "chunk_start_char": 0, "chunk_end_char": 918, "block_bboxes": [[305.782, 520.593, 526.225, 775.496], [294.911, 794.449, 300.366, 805.358]]}, {"pdf_page": 4, "start_char": 0, "end_char": 706, "chunk_start_char": 919, "chunk_end_char": 1625, "block_bboxes": [[101.172, 72.192, 374.599, 117.873], [100.934, 96.461, 494.102, 189.564], [303.058, 144.327, 494.104, 177.674], [101.172, 192.143, 453.704, 213.694]]}]`

```text
In the original KGP experiments, construct-
ing KG by multi-hop dense retriever (MDR-KG)
(Wang et al., 2023) outperforms other KG con-
struction approaches, such as k-nearest neigh-
bors (KNN) (Cunningham and Delany, 2021) and
TF-IDF. Following the methodology for building
MDR-KG , we employ the MDR training technique
(Xiong et al., 2021) to develop a BERT-based pas-
sage encoder using the HotpotQA dataset. This
encoder is trained to predict subsequent supporting
passages given an initial retrieved passage. The
goal is to minimize the distances between passage
pairs that are used together to answer questions
in HotpotQA while simultaneously increasing the
distances between unrelated passages through neg-
ative sampling. This training technique equips the
encoder with reasoning capabilities, enabling it to
understand the logical associations between differ-
ent passages. Finally, we construct our KGs by
3

Example 1
Example 2
(Input) Question:
(Input) Question:
In what city is the university, for which Kim En-
glish played college basketball, located?
Tina Charles and Maya Moore were teammates on
the UConn women’s team that won championships
in what years?
(Input) Given:
(Input) Given:
Kim English played college basketball for the Uni-
versity of Missouri before being selected by the
Detroit Pistons with the 44th overall pick in the
2012 NBA draft.
In 2009 and 2010, Tina Charles and her teammate
Maya Moore led the Connecticut Huskies to two
undefeated national championships.
(Ground Truth) Follow-up Question:
(Ground Truth) Follow-up Question:
In which city is the University of Missouri located?
NA

```

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 4–4；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_008861356c216ab780f62dad7796e2d4`

**字符位置：** `[{"pdf_page": 4, "start_char": 1381, "end_char": 2535, "chunk_start_char": 0, "chunk_end_char": 1154, "block_bboxes": [[107.253, 445.556, 505.658, 575.749]]}]`

```text
Offline Indexing. Our indexing process involves processing a set of passages P using an instruction-
tuned LLM L and a retrieval encoder M. As seen in Figure 2 we first use L to extract a set of noun
phrase nodes N and relation edges E from each passage in P via OpenIE. This process is done via
1-shot prompting of the LLM with the prompts shown in Appendix I. Specifically, we first extract a
set of named entities from each passage. We then add the named entities to the OpenIE prompt to
extract the final triples, which also contain concepts (noun phrases) beyond named entities. We find
that this two-step prompt configuration leads to an appropriate balance between generality and bias
towards named entities. Finally, we use M to add the extra set of synonymy relations E′ discussed
above when the cosine similarity between two entity representations in N is above a threshold τ. As
stated above, this introduces more edges to our hippocampal index and allows for more effective
pattern completion. This indexing process defines a |N| × |P| matrix P, which contains the number
of times each noun phrase in the KG appears in each original passage.

```

### R14

RoG 的受约束广度优先搜索与 Tree-of-Traversals 的动作状态机怎样分别限制下一步动作？比较预先关系序列与可行操作空间。

**参考要点（待审）：**

- RoG 从问题实体出发，沿计划的关系序列执行受约束BFS，检索有效推理路径。（chunk_3e71dc58ca336959686a576311cb5e3a）
- Tree-of-Traversals 的ASM定义与KG交互的可行动作、状态及提示模板；树搜索管理搜索轨迹和回溯。（chunk_0cb3c2dcbacf18237a13b232366d2be8）

**相对旧题：** 新增搜索可行性约束比较

**来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF物理页 6–6；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；`chunk_3e71dc58ca336959686a576311cb5e3a`

**字符位置：** `[{"pdf_page": 6, "start_char": 45, "end_char": 1138, "chunk_start_char": 0, "chunk_end_char": 1093, "block_bboxes": [[108.0, 82.256, 503.997, 116.149], [108.0, 122.764, 326.45, 134.58], [172.564, 147.427, 206.776, 157.39], [187.662, 158.204, 191.456, 165.178], [209.625, 140.687, 227.754, 164.094], [233.376, 145.126, 247.772, 155.089], [230.607, 161.168, 250.037, 168.643], [252.196, 140.687, 330.629, 164.094], [336.252, 145.126, 350.648, 155.089], [333.482, 161.168, 352.912, 168.643], [355.072, 147.427, 367.804, 157.39], [369.688, 136.361, 382.42, 155.089], [369.6, 161.518, 382.51, 168.492], [384.167, 147.298, 504.0, 158.232], [108.0, 170.192, 504.001, 191.473], [108.249, 210.433, 277.552, 220.396], [108.0, 232.292, 504.0, 265.898], [152.592, 268.742, 293.946, 280.328], [297.459, 265.449, 322.777, 279.675], [326.039, 265.449, 354.369, 278.833], [108.0, 265.388, 504.003, 312.937]]}]`

```text
z = <PATH> r1 <SEP> r2 <SEP> . . . <SEP> rl </PATH>
where <PATH>, <SEP>, </PATH> are special tokens indicating the start, separator, and end of the
relation path, respectively3.
Therefore, the optimization of Lplan can be achieved as
arg max
θ
1
|Z∗|
X
z∈Z∗
log Pθ(z|q) =
1
|Z∗|
X
z∈Z∗
log
|z|
Y
i=1
Pθ(ri|r<i, q),
(8)
where Pθ(z|q) denotes the prior distribution of generating faithful relation path z, and Pθ(ri|r<i, q)
denotes the probability of each token in z generated by LLMs.
4.4
RETRIEVAL-REASONING MODULE
Retrieval. Given a question q and a relation path as plan z, the retrieval module aims to retrieve the
reasoning paths wz from KG G. The retrieval process can be conducted by finding paths in G that
start from the question entities eq and follow the relation paths z, formulated as
Wz = {wz(eq, e∗)|wz(eq, e∗) = eq
r1
−→e1
r2
−→. . .
rl
−→ea∗, wz(eq, e∗) ∈G}.
(9)
We adopt a constrained breadth-first search to retrieve the reasoning paths wz from KGs. In exper-
iments, all retrieved paths are used for reasoning. The detailed retrieval algorithm can be found in
Appendix A.3.

```

**来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF物理页 2–2；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；`chunk_0cb3c2dcbacf18237a13b232366d2be8`

**字符位置：** `[{"pdf_page": 2, "start_char": 2406, "end_char": 3845, "chunk_start_char": 0, "chunk_end_char": 1439, "block_bboxes": [[79.521, 559.21, 290.95, 610.85], [70.866, 622.754, 290.95, 660.774], [70.866, 672.997, 182.671, 684.952], [70.528, 695.075, 289.139, 773.686], [305.749, 396.054, 526.224, 623.667], [306.142, 636.148, 461.477, 647.057]]}]`

```text
3. Development of a new dataset to test com-
bined reasoning over a general and a domain-
specific KG, and evaluation of Tree-of-
Traversals on this dataset.
We conduct detailed experiments on three mod-
els of varied sizes hosted on Amazon Bedrock and
present detailed ablation studies.
2
Tree-of-Traversals
The Tree-of-Traversals algorithm maintains a local
KG subgraph that is repeatedly expanded until it
contains all the information required by an LLM
to answer the given query. At the start, a local
KG subgraph is initialized to contain the entities
present in the original query. It is then expanded
using a tree search algorithm to choose actions and
thoughts generated by an LLM in order to obtain
relevant knowledge from the KG using a KG inter-
face. The algorithm halts when the LLM is able
to answer the original query using the local KG
subgraph as context. Tree-of-Traversals consists of
three major components. (1) A knowledge graph
interface implemented to interact with one or more
required KGs. (2) An action state machine (ASM)
which is a finite state machine that defines the fea-
sible space of actions, states, and prompt templates
when the LLM interacts with a KG to expand the
local KG subgraph. (3) A tree search algorithm
which defines the overall LLM search trajectory
such as best first search, backtrack upon making a
mistake, and termination condition when an answer
is found.
2.1
Knowledge Graph Interface

```

### R15

LPKG 的 CLQA-Wiki 与 STaRK 各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。

**参考要点（待审）：**

- CLQA-Wiki 覆盖多跳、比较、交集、并集，强调逻辑操作及可能多答案。（chunk_ab66789d9bc91de68948962d6c3f0011）
- STaRK 将关系条件与复杂文本属性一起构造自然查询，真值是答案条目/实体。（chunk_6b5383484693f6226010eab8143f80d6）

**相对旧题：** 已有来源的新需求/答案约束组合

**来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF物理页 2–2；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；`chunk_ab66789d9bc91de68948962d6c3f0011`

**字符位置：** `[{"pdf_page": 2, "start_char": 1158, "end_char": 2387, "chunk_start_char": 0, "chunk_end_char": 1229, "block_bboxes": [[70.473, 416.616, 290.949, 603.847], [70.506, 615.603, 290.949, 775.47], [306.142, 72.649, 399.883, 84.604]]}]`

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

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 1–1；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_6b5383484693f6226010eab8143f80d6`

**字符位置：** `[{"pdf_page": 1, "start_char": 324, "end_char": 2018, "chunk_start_char": 0, "chunk_end_char": 1694, "block_bboxes": [[283.758, 245.19, 328.243, 257.145], [143.866, 269.807, 469.789, 454.391], [205.19, 610.031, 248.703, 620.969], [211.6, 599.33, 240.929, 607.533], [216.449, 585.557, 238.006, 593.76], [385.922, 619.315, 478.763, 627.518], [437.928, 589.928, 443.83, 596.764], [144.476, 619.045, 160.888, 627.248], [352.298, 589.067, 382.359, 597.271], [260.676, 563.411, 293.347, 571.614], [283.166, 474.459, 315.256, 485.396], [302.055, 504.115, 386.419, 520.044], [298.079, 528.776, 350.265, 544.62], [370.448, 534.987, 376.35, 541.823], [401.047, 502.427, 449.478, 514.664], [373.918, 519.121, 381.0, 527.324], [161.972, 549.841, 211.15, 564.335], [164.844, 565.505, 209.149, 570.006], [177.292, 570.096, 195.824, 574.597], [324.724, 518.31, 331.806, 526.514], [263.612, 620.935, 339.71, 629.138], [354.51, 529.231, 392.389, 541.536]]}]`

```text
Abstract
Answering real-world complex queries, such as complex product search, often
requires accurate retrieval from semi-structured knowledge bases that involve blend
of unstructured (e.g., textual descriptions of products) and structured (e.g., en-
tity relations of products) information. However, many previous works studied
textual and relational retrieval tasks as separate topics. To address the gap, we
develop STARK, a large-scale Semi-structure retrieval benchmark on Textual
and Relational Knowledge Bases. Our benchmark covers three domains: product
search, academic paper search, and queries in precision medicine. We design a
novel pipeline to synthesize realistic user queries that integrate diverse relational
information and complex textual properties, together with their ground-truth an-
swers (items). We conduct rigorous human evaluation to validate the quality of
our synthesized queries. We further enhance the benchmark with high-quality
human-generated queries to provide an authentic reference. STARK serves as a
comprehensive testbed for evaluating the performance of retrieval systems driven
by large language models (LLMs). Our experiments suggest that STARK presents
significant challenges to the current retrieval and LLM systems, highlighting the
need for more capable semi-structured retrieval systems.
[
]
Answer:
Query
Semi-structured KB (SKB)
…
User
Retrieve
Evaluate
STARK
Please suggest a HEAD 
tennis racquet for casual
player?
[
]
Looking for stylish kids 
bike helmets that suit a 
Superman bike.
…
Construct with
simulated users
…
Can you find a
push-along tricycle 
from Radio Flyer that is
both fun and safe for 
my kids?
…
LLM Retrieval system
[
]

```

### R16

StructGPT 与 KG-GPT 处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。

**参考要点（待审）：**

- StructGPT 覆盖KGQA、TableQA、Text-to-SQL，可输出待执行的SQL表达式。（chunk_3a66017788061f8f662ca365c955591a）
- KG-GPT 针对KG事实验证与KGQA，不凭此推断其具备数据库SQL生成能力。（chunk_61e96cb10e247f7d002b4163920cc737）

**相对旧题：** 新增可执行输出与事实判断关系

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 3–3；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_3a66017788061f8f662ca365c955591a`

**字符位置：** `[{"pdf_page": 3, "start_char": 1457, "end_char": 2482, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[191.464, 462.942, 224.205, 479.919], [212.74, 462.942, 288.634, 480.561], [70.866, 471.949, 280.313, 495.113], [70.866, 483.925, 289.133, 508.636], [70.866, 518.514, 291.042, 732.843], [81.775, 735.146, 278.466, 773.66], [306.142, 72.649, 374.705, 84.604], [306.142, 94.622, 375.306, 105.531]]}]`

```text
i
, c(h)
j )}, where c(k)
i
and c(h)
j
denote the i-th and j-th columns in the
k-th and h-th tables, respectively.
Problem Statement. This work mainly focuses
on using LLMs to solve complex reasoning tasks
based on structured data. Formally, it can be de-
scribed as a question answering task: given a nat-
ural language question q and an accessible struc-
tured data S (e.g., a knowledge graph, a table, or
database), the LLM needs to extract useful evi-
dence from S and then generates the expected re-
sult to answer the question q based on the extracted
evidence. According to the task requirement, the
generated result can be either free-form answers
in natural language or structured expressions (e.g.,
SQL statements) to be executed for obtaining the
answer from S. Since we consider three types of
structured data (Section 4), our tasks can be instan-
tiated as follows:
• KG based question answering (KGQA)
• Table based question answering (TableQA)
• DB based semantic parsing (Text-to-SQL)
4
Approach
4.1
Overview

```

**来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF物理页 1–1；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；`chunk_61e96cb10e247f7d002b4163920cc737`

**字符位置：** `[{"pdf_page": 1, "start_char": 237, "end_char": 1173, "chunk_start_char": 0, "chunk_end_char": 936, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.516, 240.528, 273.87, 489.67], [70.866, 504.681, 153.68, 516.636]]}]`

```text
Abstract
While large language models (LLMs) have
made considerable advancements in under-
standing and generating unstructured text, their
application in structured data remains underex-
plored. Particularly, using LLMs for complex
reasoning tasks on knowledge graphs (KGs)
remains largely untouched. To address this,
we propose KG-GPT, a multi-purpose frame-
work leveraging LLMs for tasks employing
KGs. KG-GPT comprises three steps: Sentence
Segmentation, Graph Retrieval, and Inference,
each aimed at partitioning sentences, retriev-
ing relevant graph components, and deriving
logical conclusions, respectively. We evalu-
ate KG-GPT using KG-based fact verification
and KGQA benchmarks, with the model show-
ing competitive and robust performance, even
outperforming several fully-supervised models.
Our work, therefore, marks a significant step
in unifying structured and unstructured data
processing within the realm of LLMs.1
1

```

### R17

KGP 为什么用真实邻居段落去匹配模型预测的下一条证据？结合 CuriousLLM 对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。

**参考要点（待审）：**

- KGP 示例中模型可预测错误出生日期，再从真实文档邻居匹配段落以纠正；预测证据不是已核实原文。（chunk_adcc17b94d9058357729c73998e78ba9）
- CuriousLLM 作者观察原KGP虽能猜到缺失证据，仍可能使用无关或错误关键词而妨碍检索。（chunk_f58319afb1c636475f807715f48a7a93）

**相对旧题：** 新增原始论文与后续分析交叉核对

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 5–5；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_adcc17b94d9058357729c73998e78ba9`

**字符位置：** `[{"pdf_page": 5, "start_char": 1622, "end_char": 3271, "chunk_start_char": 0, "chunk_end_char": 1649, "block_bboxes": [[54.0, 387.595, 292.505, 638.654], [54.0, 639.649, 292.505, 704.406]]}]`

```text
Figure 4 presents the content-based question asking ‘In
what year was the creator of the current arrangement of
Simpson’s Theme born?’. We use TF-IDF search to initial-
ize the seeding passage Node 1, which reads: ‘Alf Heiberg
Clausen (born March 28, 1941) is an American film com-
poser’. Subsequently, we prefix the currently retrieved-
context (Node 1) with the question and prompt the LLM to
generate the next evidence required to approach the question
one step closer. Because we augment the reasoning capabil-
ity of the LLM by instruction fine-tuning, it is expected to
recognize the logical association between the question and
the currently retrieved context. Consequently, it can predict
the subsequent passage that maintains logical coherence, al-
beit may contain factual mistakes, i.e., ‘Alf Clausen (born
April 16, 1941) is an American composer of film and tele-
vision scores.’ To rectify this potential factual mistake, we
select nodes from the candidate neighbors that match the
most with the LLM-generated passage, in this case, Node
4 ‘Alf Heiberg Clausen (born March 28, 1941) is an Ameri-
can film composer’. Since this passage sources directly from
documents, it inherently ensures the validity of the informa-
tion. Then we prompt LLMs along with the retrieved context
Node 1 and 4 for the answer.
Additionally, for questions asking about document struc-
tures, we extract the document structure names and locate
their corresponding structural nodes in the KG. For the table
node, we retrieve its markdown formatted content while for
the page node, we traverse its one-hop neighbor and obtain
passages belonging to that page.

```

**来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF物理页 1–1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；`chunk_f58319afb1c636475f807715f48a7a93`

**字符位置：** `[{"pdf_page": 1, "start_char": 3374, "end_char": 3780, "chunk_start_char": 0, "chunk_end_char": 406, "block_bboxes": [[305.324, 574.956, 526.313, 775.443]]}]`

```text
However, during our experiments, we notice that
the original KGP technique involves fine-tuning a
T5 (Raffel et al., 2020) agent with a large corpus.
Despite this, the agent’s performance remains lim-
ited due to hallucination: While correctly predicts
missing evidence, it often uses irrelevant or erro-
neous keywords, which obscure the search for the
actual piece of missing evidence, as shown in Table

```

### R18

请从论文库举两个“图方法仍使用向量”的例子：一个用于把问题实体映射到图节点，另一个用于检索相关节点和边。比较向量所在的阶段，不能只回答方法名。

**参考要点（待审）：**

- HippoRAG 编码问题命名实体，用最高余弦相似度匹配KG节点。（chunk_0b0bc328584472f90acf54bff3d926e1）
- G-Retriever 编码问题及节点/边属性，用KNN和余弦相似度选top-k节点/边。（chunk_8c5476c0307c733adb60d1afe861e4d2）

**相对旧题：** 新增图内向量角色与无方法名入口

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 4–4；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_0b0bc328584472f90acf54bff3d926e1`

**字符位置：** `[{"pdf_page": 4, "start_char": 2535, "end_char": 3562, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[107.671, 581.944, 504.004, 668.501], [108.0, 680.882, 503.997, 701.353], [107.579, 701.695, 505.573, 722.166], [303.509, 742.332, 308.49, 752.295]]}]`

```text
Online Retrieval. During the retrieval process, we prompt L using a 1-shot prompt to extract a set
of named entities from a query q, our previously defined query named entities Cq = {c1, ..., cn}
(Stanford and Alzheimer’s in our Figure 2 example). These named entities Cq from the query are
then encoded by the same retrieval encoder M. Then, the previously defined query nodes are
chosen as the set of nodes in N with the highest cosine similarity to the query named entities
Cq. More formally, query nodes are defined as Rq = {r1, ..., rn} such that ri = ek where k =
arg maxj cosine_similarity(M(ci), M(ej)), represented as the Stanford logo and the Alzheimer’s
purple ribbon symbol in Figure 2.
2Intriguingly, some work in cognitive science has also found a correlation between human word recall and
the output of the PageRank algorithm [25].
4Many details around the hippocampal memory indexing theory are omitted from this study for simplicity.
We encourage interested reader to follow the references in §2.1 for more.
4

```

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 6–7；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_8c5476c0307c733adb60d1afe861e4d2`

**字符位置：** `[{"pdf_page": 6, "start_char": 2444, "end_char": 3469, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[107.532, 491.621, 505.745, 512.568], [107.691, 516.443, 504.002, 540.477], [264.033, 545.592, 504.667, 559.227], [107.641, 564.665, 505.74, 585.768], [108.0, 599.995, 169.449, 609.957], [108.0, 619.83, 503.996, 640.932], [265.056, 639.471, 504.667, 653.105], [108.0, 661.736, 504.002, 693.441], [245.833, 700.025, 504.667, 726.771], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 7, "start_char": 0, "end_char": 417, "chunk_start_char": 1026, "chunk_end_char": 1443, "block_bboxes": [[107.641, 74.177, 504.344, 118.591], [108.0, 131.379, 230.889, 141.341]]}]`

```text
We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.
These embeddings are then stored in a nearest neighbor data structure.
To elaborate, consider xn ∈DLn as the text attributes of node n. Utilizing a pre-trained LM, such as
SentenceBert [34], we apply the LM to xn, yielding the representation zn:
zn = LM(xn) ∈Rd,
(3)
where d denotes the dimension of the output vector. Similar preprocessing steps are applied to edges.
Refer to Figure 3, Step 1 for an illustrative representation.
5.2
Retrieval
For retrieval, we employ the same encoding strategy to the query xq, to ensure consistent treatment
of textual information:
zq = LM(xq) ∈Rd.
(4)
Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors
retrieval approach. This method yields a set of ‘relevant nodes/edges’ based on the similarity between
the query and each node or edge. The retrieval operation is defined as:
Vk = argtopkn∈V cos(zq, zn)
Ek = argtopke∈E cos(zq, ze),
(5)
6

where zn and ze are the embeddings of node n and edge e, respectively. We use the cosine similarity
function, cos(·, ·), to measure the similarity between the query representation and the node/edge
embeddings. The argtopk operation retrieves the top-k elements based on this similarity, providing a
set of nodes Vk and edges Ek considered most relevant to the query. See Step 2 of Figure 3.
5.3
Subgraph Construction

```

### R19

G-Retriever 冻结 LLM 的软提示训练与 ToG-2 的 training-free 分别意味着什么？比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。

**参考要点（待审）：**

- G-Retriever 冻结LLM但以GNN输出的软提示做高效微调。（chunk_2da94a87e97c2e0f30e8eec5659e202d）
- ToG-2 将自身描述为training-free且可即插即用不同LLM。（chunk_9b63637ef18ed2d67ff105ef55092df3）

**相对旧题：** 新增冻结底座与系统训练条件差异

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 6–6；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_2da94a87e97c2e0f30e8eec5659e202d`

**字符位置：** `[{"pdf_page": 6, "start_char": 909, "end_char": 2444, "chunk_start_char": 0, "chunk_end_char": 1535, "block_bboxes": [[108.0, 216.502, 504.353, 270.219], [108.0, 292.552, 503.997, 313.499], [108.0, 330.132, 187.371, 342.087], [107.641, 354.551, 505.247, 430.106], [107.641, 436.402, 505.74, 457.379], [108.0, 471.631, 168.064, 481.593]]}]`

```text
Figure 3: Overview of the proposed G-Retriever: 1) Indexing: Graphs are indexed for efficient query
processing; 2) Retrieval: The most semantically relevant nodes and edges are retrieved, conditioned
on the query; 3) Subgraph Construction: A connected subgraph is extracted, covering as many
relevant nodes and edges as possible while maintaining a manageable graph size; 4) Generation: An
answer is generated using a ‘graph prompt’, a textualized graph, and the query.
require multi-hop reasoning. Given the possibility of multiple answers for the same question, the
hit@1 metric is used to assess the precision of the top returned answer.
5
G-Retriever
In this section, we introduce G-Retriever, a new architecture tailored for GraphQA, which integrates
the strengths of GNNs, LLMs, and RAG. To allow efficient fine-tuning while preserving the LLM’s
pretrained language capabilities, we freeze the LLM and use a soft prompting approach on the output
of the GNN. Our RAG-based design mitigates hallucinations through direct retrieval of the graph,
while allowing our approach to scale to graphs exceeding the LLM’s context window size. To adapt
RAG to graphs, we formulate subgraph retrieval as a PCST optimization problem. This approach
also allows us to enhance explainability by returning the retrieved subgraph.
G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as
depicted in Figure 3. The implementation details of each step are elaborated in the following sections.
5.1
Indexing

```

**来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF物理页 1–1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；`chunk_9b63637ef18ed2d67ff105ef55092df3`

**字符位置：** `[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

```text
Retrieval-augmented generation (RAG) has improved large language models
(LLMs) by using knowledge retrieval to overcome knowledge deficiencies. How-
ever, current RAG methods often fall short of ensuring the depth and complete-
ness of retrieved information, which is necessary for complex reasoning tasks.
In this work, we introduce Think-on-Graph 2.0 (ToG-2), a hybrid RAG frame-
work that iteratively retrieves information from both unstructured and structured
knowledge sources in a tight-coupling manner.
Specifically, ToG-2 leverages
knowledge graphs (KGs) to link documents via entities, facilitating deep and
knowledge-guided context retrieval. Simultaneously, it utilizes documents as en-
tity contexts to achieve precise and efficient graph retrieval. ToG-2 alternates
between graph retrieval and context retrieval to search for in-depth clues rele-
vant to the question, enabling LLMs to generate answers. We conduct a series
of well-designed experiments to highlight the following advantages of ToG-2:
1) ToG-2 tightly couples the processes of context retrieval and graph retrieval,
deepening context retrieval via the KG while enabling reliable graph retrieval
based on contexts; 2) it achieves deep and faithful reasoning in LLMs through
an iterative knowledge retrieval process of collaboration between contexts and
the KG; and 3) ToG-2 is training-free and plug-and-play compatible with vari-
ous LLMs. Extensive experiments demonstrate that ToG-2 achieves overall state-
of-the-art (SOTA) performance on 6 out of 7 knowledge-intensive datasets with
GPT-3.5, and can elevate the performance of smaller models (e.g
```

### R20

ToG 的 training-free 和 StructGPT 的 zero-shot/few-shot 是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。

**参考要点（待审）：**

- ToG 自述training-free，无需额外训练。（chunk_e09b5a88c34014513aad6c0d6121f790）
- StructGPT 报告zero-shot和few-shot设置，利用接口迭代读取和推理；示例数和参数更新是不同描述维度。（chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad）

**相对旧题：** 已有来源的新设置维度关系；维度区分为审查解释

**来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF物理页 1–1；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；`chunk_e09b5a88c34014513aad6c0d6121f790`

**字符位置：** `[{"pdf_page": 1, "start_char": 517, "end_char": 2163, "chunk_start_char": 0, "chunk_end_char": 1646, "block_bboxes": [[278.288, 276.647, 333.722, 288.602], [143.507, 303.075, 469.793, 532.166], [108.299, 556.334, 205.989, 568.289]]}]`

```text
ABSTRACT
Although large language models (LLMs) have achieved significant success in vari-
ous tasks, they often struggle with hallucination problems, especially in scenarios
requiring deep and responsible reasoning. These issues could be partially addressed
by introducing external knowledge graphs (KG) in LLM reasoning. In this paper,
we propose a new LLM-KG integrating paradigm “LLM ⊗KG” which treats the
LLM as an agent to interactively explore related entities and relations on KGs
and perform reasoning based on the retrieved knowledge. We further implement
this paradigm by introducing a new approach called Think-on-Graph (ToG), in
which the LLM agent iteratively executes beam search on KG, discovers the most
promising reasoning paths, and returns the most likely reasoning results. We use
a number of well-designed experiments to examine and illustrate the following
advantages of ToG: 1) compared with LLMs, ToG has better deep reasoning power;
2) ToG has the ability of knowledge traceability and knowledge correctability by
leveraging LLMs reasoning and expert feedback; 3) ToG provides a flexible plug-
and-play framework for different LLMs, KGs and prompting strategies without
any additional training cost; 4) the performance of ToG with small LLM models
could exceed large LLM such as GPT-4 in certain scenarios and this reduces the
cost of LLM deployment and application. As a training-free method with lower
computational cost and better generality, ToG achieves overall SOTA in 6 out of
9 datasets where most previous SOTAs rely on additional training. Our code is
publicly available at https://github.com/IDEA-FinAI/ToG.
1

```

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 1–1；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`

**字符位置：** `[{"pdf_page": 1, "start_char": 480, "end_char": 1582, "chunk_start_char": 0, "chunk_end_char": 1102, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.565, 238.04, 273.783, 523.046], [70.866, 535.569, 153.68, 547.524]]}]`

```text
Abstract
In this paper, we aim to improve the reason-
ing ability of large language models (LLMs)
over structured data in a unified way.
In-
spired by the studies on tool augmentation for
LLMs, we develop an Iterative Reading-then-
Reasoning (IRR) framework to solve question
answering tasks based on structured data, called
StructGPT. In this framework, we construct
the specialized interfaces to collect relevant ev-
idence from structured data (i.e., reading), and
let LLMs concentrate on the reasoning task
based on the collected information (i.e., rea-
soning). Specially, we propose an invoking-
linearization-generation procedure to support
LLMs in reasoning on the structured data with
the help of the interfaces. By iterating this
procedure with provided interfaces, our ap-
proach can gradually approach the target an-
swers to a given query. Experiments conducted
on three types of structured data show that
StructGPT greatly improves the performance
of LLMs, under the few-shot and zero-shot set-
tings. Our codes and data are publicly available
at https://github.com/RUCAIBox/StructGPT.
1

```

### R21

KGP 预测下一段证据与 RoG 生成关系路径后，分别怎样约束实际检索？比较邻居段落的相似匹配与沿关系序列的图搜索。

**参考要点（待审）：**

- KGP 将预测证据与真实邻居匹配，选择相似的文档段落。（chunk_adcc17b94d9058357729c73998e78ba9）
- RoG 从问题实体沿关系序列进行受约束BFS。（chunk_3e71dc58ca336959686a576311cb5e3a）

**相对旧题：** 新增检索约束实现比较，不复问总体流程

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 5–5；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_adcc17b94d9058357729c73998e78ba9`

**字符位置：** `[{"pdf_page": 5, "start_char": 1622, "end_char": 3271, "chunk_start_char": 0, "chunk_end_char": 1649, "block_bboxes": [[54.0, 387.595, 292.505, 638.654], [54.0, 639.649, 292.505, 704.406]]}]`

```text
Figure 4 presents the content-based question asking ‘In
what year was the creator of the current arrangement of
Simpson’s Theme born?’. We use TF-IDF search to initial-
ize the seeding passage Node 1, which reads: ‘Alf Heiberg
Clausen (born March 28, 1941) is an American film com-
poser’. Subsequently, we prefix the currently retrieved-
context (Node 1) with the question and prompt the LLM to
generate the next evidence required to approach the question
one step closer. Because we augment the reasoning capabil-
ity of the LLM by instruction fine-tuning, it is expected to
recognize the logical association between the question and
the currently retrieved context. Consequently, it can predict
the subsequent passage that maintains logical coherence, al-
beit may contain factual mistakes, i.e., ‘Alf Clausen (born
April 16, 1941) is an American composer of film and tele-
vision scores.’ To rectify this potential factual mistake, we
select nodes from the candidate neighbors that match the
most with the LLM-generated passage, in this case, Node
4 ‘Alf Heiberg Clausen (born March 28, 1941) is an Ameri-
can film composer’. Since this passage sources directly from
documents, it inherently ensures the validity of the informa-
tion. Then we prompt LLMs along with the retrieved context
Node 1 and 4 for the answer.
Additionally, for questions asking about document struc-
tures, we extract the document structure names and locate
their corresponding structural nodes in the KG. For the table
node, we retrieve its markdown formatted content while for
the page node, we traverse its one-hop neighbor and obtain
passages belonging to that page.

```

**来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF物理页 6–6；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；`chunk_3e71dc58ca336959686a576311cb5e3a`

**字符位置：** `[{"pdf_page": 6, "start_char": 45, "end_char": 1138, "chunk_start_char": 0, "chunk_end_char": 1093, "block_bboxes": [[108.0, 82.256, 503.997, 116.149], [108.0, 122.764, 326.45, 134.58], [172.564, 147.427, 206.776, 157.39], [187.662, 158.204, 191.456, 165.178], [209.625, 140.687, 227.754, 164.094], [233.376, 145.126, 247.772, 155.089], [230.607, 161.168, 250.037, 168.643], [252.196, 140.687, 330.629, 164.094], [336.252, 145.126, 350.648, 155.089], [333.482, 161.168, 352.912, 168.643], [355.072, 147.427, 367.804, 157.39], [369.688, 136.361, 382.42, 155.089], [369.6, 161.518, 382.51, 168.492], [384.167, 147.298, 504.0, 158.232], [108.0, 170.192, 504.001, 191.473], [108.249, 210.433, 277.552, 220.396], [108.0, 232.292, 504.0, 265.898], [152.592, 268.742, 293.946, 280.328], [297.459, 265.449, 322.777, 279.675], [326.039, 265.449, 354.369, 278.833], [108.0, 265.388, 504.003, 312.937]]}]`

```text
z = <PATH> r1 <SEP> r2 <SEP> . . . <SEP> rl </PATH>
where <PATH>, <SEP>, </PATH> are special tokens indicating the start, separator, and end of the
relation path, respectively3.
Therefore, the optimization of Lplan can be achieved as
arg max
θ
1
|Z∗|
X
z∈Z∗
log Pθ(z|q) =
1
|Z∗|
X
z∈Z∗
log
|z|
Y
i=1
Pθ(ri|r<i, q),
(8)
where Pθ(z|q) denotes the prior distribution of generating faithful relation path z, and Pθ(ri|r<i, q)
denotes the probability of each token in z generated by LLMs.
4.4
RETRIEVAL-REASONING MODULE
Retrieval. Given a question q and a relation path as plan z, the retrieval module aims to retrieve the
reasoning paths wz from KG G. The retrieval process can be conducted by finding paths in G that
start from the question entities eq and follow the relation paths z, formulated as
Wz = {wz(eq, e∗)|wz(eq, e∗) = eq
r1
−→e1
r2
−→. . .
rl
−→ea∗, wz(eq, e∗) ∈G}.
(9)
We adopt a constrained breadth-first search to retrieve the reasoning paths wz from KGs. In exper-
iments, all retrieved paths are used for reasoning. The detailed retrieval algorithm can be found in
Appendix A.3.

```

### R22

MindMap 的证据图合并和 CuriousLLM 的追问各会怎样改变后续可用信息？区分重组织已有证据与请求继续找证据。

**参考要点（待审）：**

- MindMap 先裁剪，再由LLM合并已取得的证据子图成统一推理图。（chunk_18e6db2a25659ad12b8e68e6cc51dfda）
- CuriousLLM 用追问指出还缺什么以指导后续检索，证据足够则产生特殊信号。（chunk_43145c0748762d6b4c650c65721f826f）

**相对旧题：** 新增证据加工与补充证据的职责对齐

**来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF物理页 4–4；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；`chunk_18e6db2a25659ad12b8e68e6cc51dfda`

**字符位置：** `[{"pdf_page": 4, "start_char": 2813, "end_char": 3840, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[70.473, 467.882, 291.043, 546.646], [147.557, 533.981, 204.244, 547.145], [70.528, 535.628, 291.042, 641.465], [70.866, 652.14, 269.761, 663.049], [70.866, 669.733, 289.132, 694.188], [70.866, 683.033, 290.941, 761.921], [81.775, 764.519, 290.944, 775.483]]}]`

```text
q . This approach incor-
porates additional query-related evidence into Gq.
After exploration, we update Vq with newly added
intermediate nodes from bridging pathways. To
manage information overhead and maintain diver-
sity, we prune Gpath
q
and Gnei
q
by clustering and
sampling sub-graphs based on their head entities.
These pruning steps result in the final evidence
graph Gq, optimizing information while preserving
diversity. Specific details are shown in Appendix
E. We show the hallucination influence of results
using path-based exploration and neighbor-based
exploration components in the experiment part.
3.2
Step II: Evidence Graph Aggregation
In this phase, LLM is instructed to consolidate the
diverse evidence sub-graphs G∗
q into a unified rea-
soning graph Gm. This reasoning graph Gm, upon
completion, serves as an external augmented graph
input for Step III, providing a holistic perspective
on all evidence sub-graphs to enhance the output
generation process.
To generate the final additional knowledge sub-

```

**来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF物理页 1–1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；`chunk_43145c0748762d6b4c650c65721f826f`

**字符位置：** `[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

```text
Abstract
Large Language Models (LLMs) have achieved
significant success in open-domain question an-
swering. However, they continue to face chal-
lenges such as hallucinations and knowledge
cutoffs. These issues can be mitigated through
in-context learning by providing LLMs with
relevant context before generating answers.
Recent literature proposes Knowledge Graph
Prompting (KGP) which integrates knowledge
graphs with an LLM-based traversal agent
to substantially enhance document retrieval
quality. However, KGP requires costly fine-
tuning with large datasets and remains prone
to hallucination. In this paper, we propose
CuriousLLM, an enhancement that integrates
a curiosity-driven reasoning mechanism into
an LLM agent. This mechanism enables the
agent to generate relevant follow-up questions,
thereby guiding the information retrieval pro-
cess more efficiently. Central to our approach
is the development of the new Follow-upQA
dataset, which includes questions and support-
ing evidence as input, with follow-up ques-
tions serving as ground truths. These follow-
up questions either inquire about what is still
missing to fully answer the user’s query or
use special tokens to signify that the retrieved
evidence is sufficient. Our experiments show
that CuriousLLM significantly boosts LLM per-
formance in multi-document question answer-
ing (MD-QA), circumventing the substantial
computational costs and latency from the orig-
inal KGP framework. Source code: https:
//github.com/zukangy/KGP-CuriousLLM.
1

```

### R23

请找出一项按候选答案条目集合衡量 Recall@k 的工作，以及一项可能生成 SQL 的结构化问答工作。为什么前者的 Recall@k 不能直接作为后者的 SQL 执行正确率？

**参考要点（待审）：**

- STaRK Recall@k 计算top-k结果里相关条目的比例。（chunk_bb730573725b148aa7913e7f17bb9261）
- StructGPT 可生成需执行得到答案的SQL；执行正确率与条目召回不是同一指标。（chunk_3a66017788061f8f662ca365c955591a）

**相对旧题：** 新增评价对象/执行语义与无方法名入口

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 7–7；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_bb730573725b148aa7913e7f17bb9261`

**字符位置：** `[{"pdf_page": 7, "start_char": 2413, "end_char": 3663, "chunk_start_char": 0, "chunk_end_char": 1250, "block_bboxes": [[108.0, 494.427, 504.004, 558.972], [107.691, 571.321, 452.128, 581.284], [108.0, 589.391, 504.004, 621.402], [108.0, 628.984, 505.247, 671.905]]}]`

```text
• LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of
top-k ada-002 results by reranking them using large language models. We employ GPT-4-turbo
(gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized
queries and k = 10 for human-generated queries. Given a query, the LLMs assign a satisfaction
score from 0 to 1 to each candidate entity based on textual and relational information. Due to high
computational costs, we evaluate these rerankers on a random 10% sample of test queries.
The performance of these models are measured using standard retrieval metrics below.
• Hit@k assesses whether the correct item is among the top-k results from the model. We used
k = 1 and k = 5 for evaluation. At k = 1, it evaluates the accuracy of the top recommendation; at
k = 5, it examines the model’s precision in a wider recommendation set.
• Recall@k measures the proportion of relevant items in the top-k results. For synthesized queries,
k = 20 is used, as the answer length of all of the queries in our benchmarks are equal or smaller
then 20. This metric offers insight into the model’s ability to identify all relevant items, particularly
in scenarios where missing any could be critical.

```

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 3–3；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_3a66017788061f8f662ca365c955591a`

**字符位置：** `[{"pdf_page": 3, "start_char": 1457, "end_char": 2482, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[191.464, 462.942, 224.205, 479.919], [212.74, 462.942, 288.634, 480.561], [70.866, 471.949, 280.313, 495.113], [70.866, 483.925, 289.133, 508.636], [70.866, 518.514, 291.042, 732.843], [81.775, 735.146, 278.466, 773.66], [306.142, 72.649, 374.705, 84.604], [306.142, 94.622, 375.306, 105.531]]}]`

```text
i
, c(h)
j )}, where c(k)
i
and c(h)
j
denote the i-th and j-th columns in the
k-th and h-th tables, respectively.
Problem Statement. This work mainly focuses
on using LLMs to solve complex reasoning tasks
based on structured data. Formally, it can be de-
scribed as a question answering task: given a nat-
ural language question q and an accessible struc-
tured data S (e.g., a knowledge graph, a table, or
database), the LLM needs to extract useful evi-
dence from S and then generates the expected re-
sult to answer the question q based on the extracted
evidence. According to the task requirement, the
generated result can be either free-form answers
in natural language or structured expressions (e.g.,
SQL statements) to be executed for obtaining the
answer from S. Since we consider three types of
structured data (Section 4), our tasks can be instan-
tiated as follows:
• KG based question answering (KGQA)
• Table based question answering (TableQA)
• DB based semantic parsing (Text-to-SQL)
4
Approach
4.1
Overview

```

### R24

HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。

**参考要点（待审）：**

- HippoRAG specificity 在PPR前调整查询节点概率。（chunk_3847660df4256f0bd39f8b49c7b9864e）
- G-Retriever 依据相关性给节点/边奖励，在连通子图优化中折中奖励和边成本。（chunk_04c0673f276b70d320674636d537dc80）
- KG-GPT 的top-k决定关系检索范围，改变检索三元组数量。（chunk_fbbb8f38df6e66a40727407ca912ae1a）

**相对旧题：** 新增三论文参数作用位置比较

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 5–5；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_3847660df4256f0bd39f8b49c7b9864e`

**字符位置：** `[{"pdf_page": 5, "start_char": 789, "end_char": 2205, "chunk_start_char": 0, "chunk_end_char": 1416, "block_bboxes": [[107.641, 169.384, 504.345, 321.332], [108.0, 338.585, 227.887, 350.54], [108.0, 363.493, 166.381, 373.456]]}]`

```text
Node Specificity. We introduce node specificity as a neurobiologically plausible way to further
improve retrieval. It is well known that global signals for word importance, like inverse document
frequency (IDF), can improve information retrieval. However, in order for our brain to leverage IDF
for retrieval, the number of total “passages” encoded would need to be aggregated with all node
activations before memory retrieval is complete. While simple for normal computers, this process
would require activating connections between an aggregator neuron and all nodes in the hippocampal
index every time retrieval occurs, likely introducing prohibitive computational overhead. Given
these constraints, we propose node specificity as an alternative IDF signal which requires only local
signals and is thus more neurobiologically plausible. We define the node specificity of node i as
si = |Pi|−1, where Pi is the set of passages in P from which node i was extracted, information that
is already available at each node. Node specificity is used in retrieval by multiplying each query node
probability #»n with si before PPR; this allows us to modulate each of their neighborhood’s probability
as well as their own. We illustrate node specificity in Figure 2 through relative symbol size: the
Stanford logo grows larger than the Alzheimer’s symbol since it appears in fewer documents.
3
Experimental Setup
3.1
Datasets

```

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 7–7；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_04c0673f276b70d320674636d537dc80`

**字符位置：** `[{"pdf_page": 7, "start_char": 417, "end_char": 2023, "chunk_start_char": 0, "chunk_end_char": 1606, "block_bboxes": [[107.641, 151.52, 505.245, 237.771], [108.0, 244.107, 504.344, 297.796], [195.1, 312.629, 239.265, 322.822], [242.027, 305.745, 504.667, 329.495], [108.0, 336.619, 505.29, 359.067], [187.776, 366.935, 248.014, 378.997], [212.323, 379.647, 254.007, 394.01], [258.478, 366.502, 272.874, 376.465], [255.667, 382.954, 274.929, 390.585], [277.341, 368.804, 320.948, 378.997], [325.973, 366.502, 340.369, 376.465], [323.161, 382.954, 342.423, 390.585], [344.835, 368.675, 504.667, 378.997], [107.641, 399.878, 131.98, 409.841]]}]`

```text
This step aims to construct a subgraph that encompasses as many relevant nodes and edges as possible,
while keeping the graph size manageable. This approach offers two key benefits: Firstly, it helps
to filter out nodes and edges that are not pertinent to the query. This is crucial because irrelevant
information can overshadow the useful data, potentially diverting the focus of the subsequent LLM
from the information of interest. Secondly, it enhances efficiency; by keeping the graph size
manageable, it becomes feasible to translate the graph into natural language and then input it into the
LLM for processing. The Prize-Collecting Steiner Tree algorithm [2] serves as our primary method
for identifying such optimally sized and relevant subgraphs. See Step 3 in Figure 3.
Prize-Collecting Steiner Tree (PCST). The PCST problem aims to find a connected subgraph that
maximizes the total prize values of its nodes while minimizing the total costs of its edges. Our
approach assigns higher prize values to nodes and edges more relevant to the query, as measured by
cosine similarity. Specifically, the top k nodes/edges are assigned descending prize values from k
down to 1, with the rest assigned zero. The node prize assignment is as follows:
prize(n) =
k −i,
if n ∈Vk and n is the top i node,
0,
otherwise.
(6)
Edge prizes are assigned similarly. The objective is to identify a subgraph, S∗= (V ∗, E∗), that
optimizes the total prize of nodes and edges, minus the costs associated with the size of the subgraph:
S∗=
argmax
S⊆G,
S is connected
X
n∈VS
prize(n) +
X
e∈ES
prize(e) −cost(S),
(7)
where

```

**来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF物理页 5–5；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；`chunk_fbbb8f38df6e66a40727407ca912ae1a`

**字符位置：** `[{"pdf_page": 5, "start_char": 0, "end_char": 1290, "chunk_start_char": 0, "chunk_end_char": 1290, "block_bboxes": [[70.866, 73.498, 290.946, 219.953], [70.866, 231.257, 221.095, 242.166], [70.528, 248.08, 290.949, 367.465], [70.528, 370.426, 289.139, 408.543], [70.866, 410.882, 289.132, 449.164], [70.866, 462.518, 145.933, 474.473]]}]`

```text
ceeding 90%, in both the 1-hop and 2-hop scenar-
ios, even with a minimal set of four examples. In
contrast, in both the FACTKG and MetaQA 3-hop
scenarios, the performance of the 4-shot learning
scenario was similar to that of the baselines which
did not utilize graph evidence. This similarity sug-
gests that LLMs may struggle to interpret com-
plex data features when equipped with only four
shots. Thus, the findings highlight the importance
of formulating in-context examples according to
the complexity of the task.
4.4.2
Top-K Relation Retrieval
Table 11 shows the performance according to the
value of k in FACTKG. As a result, performance
did not significantly vary depending on the value of
k. Table 12 illustrates the average number of triples
retrieved for both supported and refuted claims, de-
pending on k. Despite the increase in the number
of triples as the value of k grows, it does not im-
pact the accuracy. This suggests that the additional
triples are not significantly influential.
In MetaQA, the performance and the average
number of retrieved triples are also depicted in
Table 13 and Table 14, respectively. Unlike the
FACTKG experiment, as the value of k rises in
MetaQA, it appears that more significant triples are
retrieved, leading to improved performance.
5

```

### N01

“只要使用知识图谱，系统就不会再用向量相似度。”HippoRAG 与 G-Retriever 的方法细节能支持这句话吗？

**参考要点（待审）：**

- 不能：HippoRAG 使用向量余弦相似匹配查询实体与节点。（chunk_0b0bc328584472f90acf54bff3d926e1）
- G-Retriever 用向量相似和KNN检索节点与边。（chunk_8c5476c0307c733adb60d1afe861e4d2）

**相对旧题：** 新增图与向量互斥的错误前提

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 4–4；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_0b0bc328584472f90acf54bff3d926e1`

**字符位置：** `[{"pdf_page": 4, "start_char": 2535, "end_char": 3562, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[107.671, 581.944, 504.004, 668.501], [108.0, 680.882, 503.997, 701.353], [107.579, 701.695, 505.573, 722.166], [303.509, 742.332, 308.49, 752.295]]}]`

```text
Online Retrieval. During the retrieval process, we prompt L using a 1-shot prompt to extract a set
of named entities from a query q, our previously defined query named entities Cq = {c1, ..., cn}
(Stanford and Alzheimer’s in our Figure 2 example). These named entities Cq from the query are
then encoded by the same retrieval encoder M. Then, the previously defined query nodes are
chosen as the set of nodes in N with the highest cosine similarity to the query named entities
Cq. More formally, query nodes are defined as Rq = {r1, ..., rn} such that ri = ek where k =
arg maxj cosine_similarity(M(ci), M(ej)), represented as the Stanford logo and the Alzheimer’s
purple ribbon symbol in Figure 2.
2Intriguingly, some work in cognitive science has also found a correlation between human word recall and
the output of the PageRank algorithm [25].
4Many details around the hippocampal memory indexing theory are omitted from this study for simplicity.
We encourage interested reader to follow the references in §2.1 for more.
4

```

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 6–7；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_8c5476c0307c733adb60d1afe861e4d2`

**字符位置：** `[{"pdf_page": 6, "start_char": 2444, "end_char": 3469, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[107.532, 491.621, 505.745, 512.568], [107.691, 516.443, 504.002, 540.477], [264.033, 545.592, 504.667, 559.227], [107.641, 564.665, 505.74, 585.768], [108.0, 599.995, 169.449, 609.957], [108.0, 619.83, 503.996, 640.932], [265.056, 639.471, 504.667, 653.105], [108.0, 661.736, 504.002, 693.441], [245.833, 700.025, 504.667, 726.771], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 7, "start_char": 0, "end_char": 417, "chunk_start_char": 1026, "chunk_end_char": 1443, "block_bboxes": [[107.641, 74.177, 504.344, 118.591], [108.0, 131.379, 230.889, 141.341]]}]`

```text
We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.
These embeddings are then stored in a nearest neighbor data structure.
To elaborate, consider xn ∈DLn as the text attributes of node n. Utilizing a pre-trained LM, such as
SentenceBert [34], we apply the LM to xn, yielding the representation zn:
zn = LM(xn) ∈Rd,
(3)
where d denotes the dimension of the output vector. Similar preprocessing steps are applied to edges.
Refer to Figure 3, Step 1 for an illustrative representation.
5.2
Retrieval
For retrieval, we employ the same encoding strategy to the query xq, to ensure consistent treatment
of textual information:
zq = LM(xq) ∈Rd.
(4)
Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors
retrieval approach. This method yields a set of ‘relevant nodes/edges’ based on the similarity between
the query and each node or edge. The retrieval operation is defined as:
Vk = argtopkn∈V cos(zq, zn)
Ek = argtopke∈E cos(zq, ze),
(5)
6

where zn and ze are the embeddings of node n and edge e, respectively. We use the cosine similarity
function, cos(·, ·), to measure the similarity between the query representation and the node/edge
embeddings. The argtopk operation retrieves the top-k elements based on this similarity, providing a
set of nodes Vk and edges Ek considered most relevant to the query. See Step 2 of Figure 3.
5.3
Subgraph Construction

```

### N02

G-Retriever 冻结了 LLM，所以它没有任何需要训练的组件，也不使用软提示。这一说法符合原文吗？

**参考要点（待审）：**

- 不符合：冻结LLM但使用GNN输出的软提示进行高效微调。（chunk_2da94a87e97c2e0f30e8eec5659e202d）

**相对旧题：** 新增训练组件归因反例

**来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF物理页 6–6；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；`chunk_2da94a87e97c2e0f30e8eec5659e202d`

**字符位置：** `[{"pdf_page": 6, "start_char": 909, "end_char": 2444, "chunk_start_char": 0, "chunk_end_char": 1535, "block_bboxes": [[108.0, 216.502, 504.353, 270.219], [108.0, 292.552, 503.997, 313.499], [108.0, 330.132, 187.371, 342.087], [107.641, 354.551, 505.247, 430.106], [107.641, 436.402, 505.74, 457.379], [108.0, 471.631, 168.064, 481.593]]}]`

```text
Figure 3: Overview of the proposed G-Retriever: 1) Indexing: Graphs are indexed for efficient query
processing; 2) Retrieval: The most semantically relevant nodes and edges are retrieved, conditioned
on the query; 3) Subgraph Construction: A connected subgraph is extracted, covering as many
relevant nodes and edges as possible while maintaining a manageable graph size; 4) Generation: An
answer is generated using a ‘graph prompt’, a textualized graph, and the query.
require multi-hop reasoning. Given the possibility of multiple answers for the same question, the
hit@1 metric is used to assess the precision of the top returned answer.
5
G-Retriever
In this section, we introduce G-Retriever, a new architecture tailored for GraphQA, which integrates
the strengths of GNNs, LLMs, and RAG. To allow efficient fine-tuning while preserving the LLM’s
pretrained language capabilities, we freeze the LLM and use a soft prompting approach on the output
of the GNN. Our RAG-based design mitigates hallucinations through direct retrieval of the graph,
while allowing our approach to scale to graphs exceeding the LLM’s context window size. To adapt
RAG to graphs, we formulate subgraph retrieval as a PCST optimization problem. This approach
also allows us to enhance explainability by returning the retrieved subgraph.
G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as
depicted in Figure 3. The implementation details of each step are elaborated in the following sections.
5.1
Indexing

```

### N03

KGP 的图越密，支持事实覆盖和精度就必定一起提高；MindMap 因而也无需裁剪证据。请核对两项前提。

**参考要点（待审）：**

- KGP 观察图更密时覆盖上升但精度下降。（chunk_720b9036bf8c30eaf69c980fccbcec6d）
- MindMap 为控制过载和保留多样性进行聚类、采样及剪枝。（chunk_18e6db2a25659ad12b8e68e6cc51dfda）

**相对旧题：** 新增密度/精度单调性反例

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 4–4；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_720b9036bf8c30eaf69c980fccbcec6d`

**字符位置：** `[{"pdf_page": 4, "start_char": 1020, "end_char": 2619, "chunk_start_char": 0, "chunk_end_char": 1599, "block_bboxes": [[54.0, 519.102, 292.505, 704.407], [319.5, 290.474, 558.005, 410.026]]}]`

```text
To verify the constructed KGs indeed encode the neces-
sary information for MD-QA, we randomly sample ques-
tions from HotpotQA and construct KGs over the set of
documents for each of these questions using our proposed
methods. We vary the hyperparameters to control the spar-
sity of the constructed KG and measure how much percent-
age of the supporting facts are covered by neighbors of the
seeding passages initially searched by TF-IDF. More details
about the four construction methods and their hyperparame-
ters are included in Section 8.5 in Supplementary. As shown
in Figure 5, as the constructed graph becomes denser, the
chance that the neighboring node passages hit the support-
ing facts increases (i.e., SF-EM increases) although the re-
dundant information also increases (i.e., the precision de-
creases). Given the common keywords shared between one
passage to all other passages are typically far less than the
total number of passages across all documents, the density of
the constructed graph by TF-IDF would be upper-bounded,
causing lower SF-EM (evidenced by SF-EM below 0.7 in
Figure 5 for TF-IDF curve). For TAGME, we empirically
find it identifies a larger quantity of entities mentioned in
a single passage, which leads to a denser graph and causes
the starting SF-EM of TAGME to be already around 0.95.
In addition, since KNN-MDR is pre-trained by predicting
the next supporting facts (Xiong et al. 2020) on HotpotQA,
it achieves better trade-off than KNN-ST where the embed-
dings are directly obtained from the sentence transformer
without dataset-specific pre-training.

```

**来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF物理页 4–4；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；`chunk_18e6db2a25659ad12b8e68e6cc51dfda`

**字符位置：** `[{"pdf_page": 4, "start_char": 2813, "end_char": 3840, "chunk_start_char": 0, "chunk_end_char": 1027, "block_bboxes": [[70.473, 467.882, 291.043, 546.646], [147.557, 533.981, 204.244, 547.145], [70.528, 535.628, 291.042, 641.465], [70.866, 652.14, 269.761, 663.049], [70.866, 669.733, 289.132, 694.188], [70.866, 683.033, 290.941, 761.921], [81.775, 764.519, 290.944, 775.483]]}]`

```text
q . This approach incor-
porates additional query-related evidence into Gq.
After exploration, we update Vq with newly added
intermediate nodes from bridging pathways. To
manage information overhead and maintain diver-
sity, we prune Gpath
q
and Gnei
q
by clustering and
sampling sub-graphs based on their head entities.
These pruning steps result in the final evidence
graph Gq, optimizing information while preserving
diversity. Specific details are shown in Appendix
E. We show the hallucination influence of results
using path-based exploration and neighbor-based
exploration components in the experiment part.
3.2
Step II: Evidence Graph Aggregation
In this phase, LLM is instructed to consolidate the
diverse evidence sub-graphs G∗
q into a unified rea-
soning graph Gm. This reasoning graph Gm, upon
completion, serves as an external augmented graph
input for Step III, providing a holistic perspective
on all evidence sub-graphs to enhance the output
generation process.
To generate the final additional knowledge sub-

```

### N04

STaRK 的 GPT-4 和 Claude3 重排器是在全部测试问题上、用相同候选数评测的吗？请指出这个说法省略的条件。

**参考要点（待审）：**

- 只用随机10%测试问题；合成问题k=20，人工问题k=10，不能宣称全量同k实验。（chunk_bb730573725b148aa7913e7f17bb9261）

**相对旧题：** 新增实验子样本前提反例

**来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF物理页 7–7；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；`chunk_bb730573725b148aa7913e7f17bb9261`

**字符位置：** `[{"pdf_page": 7, "start_char": 2413, "end_char": 3663, "chunk_start_char": 0, "chunk_end_char": 1250, "block_bboxes": [[108.0, 494.427, 504.004, 558.972], [107.691, 571.321, 452.128, 581.284], [108.0, 589.391, 504.004, 621.402], [108.0, 628.984, 505.247, 671.905]]}]`

```text
• LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of
top-k ada-002 results by reranking them using large language models. We employ GPT-4-turbo
(gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized
queries and k = 10 for human-generated queries. Given a query, the LLMs assign a satisfaction
score from 0 to 1 to each candidate entity based on textual and relational information. Due to high
computational costs, we evaluate these rerankers on a random 10% sample of test queries.
The performance of these models are measured using standard retrieval metrics below.
• Hit@k assesses whether the correct item is among the top-k results from the model. We used
k = 1 and k = 5 for evaluation. At k = 1, it evaluates the accuracy of the top recommendation; at
k = 5, it examines the model’s precision in a wider recommendation set.
• Recall@k measures the proportion of relevant items in the top-k results. For synthesized queries,
k = 20 is used, as the answer length of all of the queries in our benchmarks are equal or smaller
then 20. This metric offers insight into the model’s ability to identify all relevant items, particularly
in scenarios where missing any could be critical.

```

### N05

HippoRAG 的消融已经证明，只要把查询节点的一跳邻居都加进来，就一定比只用查询节点效果好。原文是否这样报告？

**参考要点（待审）：**

- 不是：不做PPR直接加入邻居的替代方法比仅使用查询节点更差。（chunk_8245d0849e8cf0df364eb6980d96843c）

**相对旧题：** 新增算法替代实验方向反例

**来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF物理页 8–8；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；`chunk_8245d0849e8cf0df364eb6980d96843c`

**字符位置：** `[{"pdf_page": 8, "start_char": 179, "end_char": 1441, "chunk_start_char": 0, "chunk_end_char": 1262, "block_bboxes": [[108.0, 101.594, 504.004, 177.122], [107.641, 183.38, 504.344, 248.056], [108.0, 265.266, 377.707, 275.229]]}]`

```text
PPR Alternatives. As shown in Table 5 (rows 5-6), to examine how much of our results are due to
the strength of PPR, we replace the PPR output with the query node probability #»n multiplied by node
specificity values (row 5) and a version of this that also distributes a small amount of probability to the
direct neighbors of each query node (row 6). First, we find that PPR is a much more effective method
for including associations for retrieval on all three datasets compared to both simple baselines. It is
interesting to note that adding the neighborhood of Rq nodes without PPR leads to worse performance
than only using the query nodes themselves.
Ablations. As seen in Table 5 (rows 7-8), node specificity obtains considerable improvements on
MuSiQue and HotpotQA and yields almost no change in 2WikiMultiHopQA. This is likely because
2WikiMultiHopQA relies on named entities with little differences in terms of term weighting. In
contrast, synonymy edges have the largest effect on 2WikiMultiHopQA, suggesting that noisy entity
standardization is useful when most relevant concepts are named entities, and improvements to
synonymy detection could lead to stronger performance in other datasets.
5.2
HippoRAG’s Advantage: Single-Step Multi-Hop Retrieval

```

### N06

KGP 中模型预测的下一段证据能直接当作已核查原文引用吗？请用论文关于出生日期的例子检查。

**参考要点（待审）：**

- 不能：示例生成的日期4月16日不正确，实际文档为3月28日；需要匹配真实邻居原文，预测文本不能当引用。（chunk_adcc17b94d9058357729c73998e78ba9）

**相对旧题：** 新增生成证据与来源混淆反例

**来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF物理页 5–5；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；`chunk_adcc17b94d9058357729c73998e78ba9`

**字符位置：** `[{"pdf_page": 5, "start_char": 1622, "end_char": 3271, "chunk_start_char": 0, "chunk_end_char": 1649, "block_bboxes": [[54.0, 387.595, 292.505, 638.654], [54.0, 639.649, 292.505, 704.406]]}]`

```text
Figure 4 presents the content-based question asking ‘In
what year was the creator of the current arrangement of
Simpson’s Theme born?’. We use TF-IDF search to initial-
ize the seeding passage Node 1, which reads: ‘Alf Heiberg
Clausen (born March 28, 1941) is an American film com-
poser’. Subsequently, we prefix the currently retrieved-
context (Node 1) with the question and prompt the LLM to
generate the next evidence required to approach the question
one step closer. Because we augment the reasoning capabil-
ity of the LLM by instruction fine-tuning, it is expected to
recognize the logical association between the question and
the currently retrieved context. Consequently, it can predict
the subsequent passage that maintains logical coherence, al-
beit may contain factual mistakes, i.e., ‘Alf Clausen (born
April 16, 1941) is an American composer of film and tele-
vision scores.’ To rectify this potential factual mistake, we
select nodes from the candidate neighbors that match the
most with the LLM-generated passage, in this case, Node
4 ‘Alf Heiberg Clausen (born March 28, 1941) is an Ameri-
can film composer’. Since this passage sources directly from
documents, it inherently ensures the validity of the informa-
tion. Then we prompt LLMs along with the retrieved context
Node 1 and 4 for the answer.
Additionally, for questions asking about document struc-
tures, we extract the document structure names and locate
their corresponding structural nodes in the KG. For the table
node, we retrieve its markdown formatted content while for
the page node, we traverse its one-hop neighbor and obtain
passages belonging to that page.

```

### N07

ToG-2 无论初始文档是否充分，都必须先完成一次图遍历才能回答。请检查它首次检索前后的控制流程。

**参考要点（待审）：**

- 不成立：首次图检索前先检索主题实体关联文档；LLM判断足够即可停止。（chunk_362a4aa0f89367fe96563183423db354）

**相对旧题：** 新增早停顺序反例

**来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF物理页 4–4；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；`chunk_362a4aa0f89367fe96563183423db354`

**字符位置：** `[{"pdf_page": 4, "start_char": 1380, "end_char": 2784, "chunk_start_char": 0, "chunk_end_char": 1404, "block_bboxes": [[108.0, 471.527, 504.004, 525.556], [144.53, 515.234, 366.053, 527.918], [108.0, 532.529, 504.004, 564.41], [108.0, 554.447, 504.003, 586.328], [108.249, 600.998, 289.634, 610.961], [108.0, 621.291, 504.002, 664.361], [211.214, 652.888, 261.535, 666.723], [108.0, 650.552, 504.002, 677.951], [119.378, 665.973, 159.504, 679.955], [145.1, 665.973, 202.938, 679.955], [188.534, 665.973, 235.681, 680.075], [221.277, 666.71, 267.832, 680.075], [263.857, 666.71, 281.741, 679.892], [277.766, 665.973, 322.408, 679.892]]}]`

```text
Given a question q, ToG-2 first identifies the entities present in q and links them to entities in the
KG. This step can be done by different entity linking (EL) methods, such as LLMs or specialized EL
tools 1. Then, ToG-2 performs a Topic Prune (TP) step to select suitable entities as starting points
of exploring in a KG, which prompts the LLM to evaluate q and appearing entities, selecting topic
entities E0
topic = {e1, e2, . . . , eN} and N is determined by LLM.
Prior to the 1st-round graph retrieval, ToG-2 uses dense retrieval models (DRMs, including dual-
tower and single-tower models) to extract the top-k chunks from the documents associated with
the initial topic entities E0
topic. The LLM then evaluates whether this information is sufficient to
answer the question, drawing on its own knowledge. If it concludes that the available information is
adequate, no further steps will be required.
3.2
HYBRID KNOWLEDGE EXPLORATION
The following will illustrate how ToG-2 iteratively harmonizes and tightly couples heterogeneous
knowledge. The iterative process will be explained in two main parts, Context-enhanced Graph
Search and Knowledge-guided Context Retrieval.
Formally, in the i-th iteration, the topic
entities are denoted as Ei
topic = {ei
1, ei
2, . . . , ei
j} and their preceding triple paths are Pi−1 =
{P i−1
1
, P i−1
2
, . . . , P i−1
j
}, P i−1
j
= {p0
j, p1
j, . . . , pi−1

```

### N08

StructGPT 的所有任务都必须直接输出自然语言答案，因此它不涉及需要执行的 SQL。请核对原文的任务和结果定义。

**参考要点（待审）：**

- 不成立：包含Text-to-SQL，可返回需执行的SQL结构表达式。（chunk_3a66017788061f8f662ca365c955591a）

**相对旧题：** 新增输出类型反例

**来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF物理页 3–3；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；`chunk_3a66017788061f8f662ca365c955591a`

**字符位置：** `[{"pdf_page": 3, "start_char": 1457, "end_char": 2482, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[191.464, 462.942, 224.205, 479.919], [212.74, 462.942, 288.634, 480.561], [70.866, 471.949, 280.313, 495.113], [70.866, 483.925, 289.133, 508.636], [70.866, 518.514, 291.042, 732.843], [81.775, 735.146, 278.466, 773.66], [306.142, 72.649, 374.705, 84.604], [306.142, 94.622, 375.306, 105.531]]}]`

```text
i
, c(h)
j )}, where c(k)
i
and c(h)
j
denote the i-th and j-th columns in the
k-th and h-th tables, respectively.
Problem Statement. This work mainly focuses
on using LLMs to solve complex reasoning tasks
based on structured data. Formally, it can be de-
scribed as a question answering task: given a nat-
ural language question q and an accessible struc-
tured data S (e.g., a knowledge graph, a table, or
database), the LLM needs to extract useful evi-
dence from S and then generates the expected re-
sult to answer the question q based on the extracted
evidence. According to the task requirement, the
generated result can be either free-form answers
in natural language or structured expressions (e.g.,
SQL statements) to be executed for obtaining the
answer from S. Since we consider three types of
structured data (Section 4), our tasks can be instan-
tiated as follows:
• KG based question answering (KGQA)
• Table based question answering (TableQA)
• DB based semantic parsing (Text-to-SQL)
4
Approach
4.1
Overview

```

