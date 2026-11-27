# v4 图谱关系评测题集

40 题：8 道事实控制题、24 道跨论文关系题、8 道反例。沿用 v3 冻结图，不修改旧题集或图谱。

**状态：模型对照未运行；在线 Workflow 接入隔离图仍待完成。**

这是按已知图谱和历史材料设计的开发集；不作为未见测试集或图扩展普遍胜出的证据。

## 判分约定

- 检索支持池覆盖、图参考路径、引用有效性、答案语义分开报告。
- 每项必要事实按 0/1 记录，保留原文引用及审查说明；不能用命中块 ID 代替语义评分。
- 全对需满足全部事实，且无关键关系错误或捏造；负例需纠正前提并限定证据边界。
- 跨论文题可以需要多条独立子图，不把它们画成一条不存在的连续路径。
- 下面的来源原文、预期路径、判分项均属于 reference outputs，仅 question 可进入被测输入。

## 逐题参考答案、判分与原文

### F01 · 优化问题与子图选择 · fact

G-Retriever 怎样把相关子图检索转化成优化问题？请说明问题名称、被选择的对象，并引用原文。

**参考答案：** G-Retriever 将相关子图检索建模为 Prize-Collecting Steiner Tree（PCST）优化问题，选择与问题相关的子图。

**逐项判分：**

- `F01.C01`：优化问题是 Prize-Collecting Steiner Tree（PCST）。（来源：pcst）
- `F01.C02`：选择对象是相关子图，不是无差别输入整张图。（来源：pcst）

**考查关系：** FORMULATES_AS, SELECTS

- 参考路径 `pcst.P01`：G-Retriever —FORMULATES_AS→ Prize-Collecting Steiner Tree —SELECTS→ relevant subgraph

**完整来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 页 1—1；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；块 `chunk_3a7f7a1f47b2586d9d9877afb9110567`。

字符位置：`[{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}]`

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

### F02 · 阶段顺序 · fact

按 KG-GPT 论文，把句子分割、图检索和推理按执行顺序排列，并分别说明它们做什么。

**参考答案：** 先 Sentence Segmentation 划分句子，再 Graph Retrieval 检索相关图组件，最后 Inference 得出逻辑结论。

**逐项判分：**

- `F02.C01`：句子分割先于图检索，图检索先于推理。（来源：kggpt）
- `F02.C02`：三个阶段分别负责划分句子、检索相关图组件和得出逻辑结论。（来源：kggpt）

**考查关系：** HAS_STAGE, PRECEDES

- 参考路径 `kggpt.P01`：KG-GPT —HAS_STAGE→ Sentence Segmentation —PRECEDES→ Graph Retrieval —PRECEDES→ Inference

**完整来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 页 1—1；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；块 `chunk_61e96cb10e247f7d002b4163920cc737`。

字符位置：`[{"pdf_page": 1, "start_char": 237, "end_char": 1173, "chunk_start_char": 0, "chunk_end_char": 936, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.516, 240.528, 273.87, 489.67], [70.866, 504.681, 153.68, 516.636]]}]`

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

### F03 · 变体方向与调用上界 · fact

ToG-R 是谁的变体，替换了哪种实体剪枝？在相同 N、D 下，论文给出的两种 LLM 调用公式相差多少？

**参考答案：** ToG-R 是 ToG 的变体，以随机实体剪枝替代 LLM 实体剪枝。ToG 为 2ND+D+1，ToG-R 为 ND+D+1，相差 ND 次调用；这是公式差值，不是本项目测得的时延。

**逐项判分：**

- `F03.C01`：变体方向为 ToG-R 指向 ToG。（来源：togr）
- `F03.C02`：随机实体剪枝替代 LLM 实体剪枝。（来源：togr）
- `F03.C03`：ToG 和 ToG-R 的公式依次为 2ND+D+1 和 ND+D+1。（来源：togr）
- `F03.C04`：相同 N、D 下公式差为 ND，不能把它当成墙钟时延差。（来源：togr）

**考查关系：** CLAIMS_BENEFIT, HAS_CALL_BOUND, USES_COMPONENT, VARIANT_OF

- 参考路径 `togr.P01`：ToG-R —VARIANT_OF→ ToG
- 参考路径 `togr.P02`：ToG-R —USES_COMPONENT→ random entity pruning
- 参考路径 `togr.P03`：ToG-R —CLAIMS_BENEFIT→ lower LLM-call cost and reasoning time
- 参考路径 `togr.P04`：ToG-R —CLAIMS_BENEFIT→ reduced risk with unfamiliar intermediate entities
- 参考路径 `togr.P05`：ToG —USES_COMPONENT→ LLM-based entity pruning
- 参考路径 `togr.P06`：ToG —HAS_CALL_BOUND→ 2ND + D + 1 LLM calls
- 参考路径 `togr.P07`：ToG-R —HAS_CALL_BOUND→ ND + D + 1 LLM calls

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 22—22；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_91a4a2e6943ad6a8074492d3f7229692`。

字符位置：`[{"pdf_page": 22, "start_char": 662, "end_char": 2113, "chunk_start_char": 0, "chunk_end_char": 1451, "block_bboxes": [[107.641, 238.664, 505.247, 402.282]]}]`

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

### F04 · 算法输入与跨段落证据 · fact

HippoRAG 收到新问题后，用什么作为 PPR 的种子？PPR 在什么结构上运行，要把哪些信息联系起来？

**参考答案：** 从问题识别关键概念，以查询概念为种子，在由语料转成的无模式知识图上运行 Personalized PageRank，整合跨段落信息用于检索。

**逐项判分：**

- `F04.C01`：种子来自问题的关键概念。（来源：hippo）
- `F04.C02`：算法是 Personalized PageRank，在无模式 KG 上运行。（来源：hippo）
- `F04.C03`：目标是整合跨段落信息用于检索。（来源：hippo）

**考查关系：** CONNECTS, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

### F05 · 图表示与代理职责 · fact

KGP 的文档图怎样定义节点和边？LLM 图遍历代理负责收集什么？请区分图结构与代理动作。

**参考答案：** 节点表示段落或文档结构（如页面、表格）；边表示段落间语义/词法相似或文档结构关系。LLM 遍历代理沿节点导航并收集支持段落。

**逐项判分：**

- `F05.C01`：节点可以是段落，也可以是页面、表格等文档结构。（来源：kgp）
- `F05.C02`：边可以表示语义/词法相似，也可以表示文档结构关系。（来源：kgp）
- `F05.C03`：遍历代理导航并收集支持段落。（来源：kgp）

**考查关系：** COLLECTS, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, USES_AGENT

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

### F06 · 停止条件与预算终止 · fact

Tree-of-Traversals 中，节点值超过答案阈值、达到 max depth、达到 max expansions 三种情况各会怎样结束？

**参考答案：** 找到节点值超过阈值的答案时停止；达到 max depth 强制转入 done 作答；达到 max expansions 停止探索并返回 Cannot find answer。后两者不自动表示答案正确。

**逐项判分：**

- `F06.C01`：找到节点值超过阈值的答案时停止。（来源：totbound）
- `F06.C02`：max depth 强制转入 done 状态作答。（来源：totbound）
- `F06.C03`：max expansions 停止探索并返回 Cannot find answer。（来源：totbound）
- `F06.C04`：预算终止与成功找到答案不能混为一谈。（来源：totbound）

**考查关系：** BOUNDED_BY, CONNECTS, HAS_STOP_CONDITION, RETURNS

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

### F07 · 训练来源与训练用途 · fact

LPKG 如何把知识图中的信息用于提升小模型的复杂问答规划能力？请给出数据来源到训练用途的链条。

**参考答案：** 从知识图构造 planning data，再用这些规划数据微调小模型，提升其复杂问答中的规划能力。

**逐项判分：**

- `F07.C01`：规划数据来源是知识图。（来源：lpdata）
- `F07.C02`：KG 派生的 planning data 用于微调。（来源：lpdata）
- `F07.C03`：训练目标是提升复杂问答规划能力，不能仅描述为在线读取 KG。（来源：lpdata）

**考查关系：** CONNECTS, DERIVES_TRAINING_DATA_FROM, HAS_STAGE, USES_TRAINING_SIGNAL

- 参考路径 `lpdata.P01`：LPKG —DERIVES_TRAINING_DATA_FROM→ knowledge graph
- 参考路径 `lpdata.P02`：LPKG —USES_TRAINING_SIGNAL→ planning data —CONNECTS→ small model fine-tuning
- 参考路径 `lpdata.P03`：LPKG —HAS_STAGE→ complex QA planning

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 1—1；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_e07b345ba2a42d01f295e47f196061d5`。

字符位置：`[{"pdf_page": 1, "start_char": 576, "end_char": 1608, "chunk_start_char": 0, "chunk_end_char": 1032, "block_bboxes": [[157.758, 205.751, 384.313, 233.647], [87.516, 247.152, 273.866, 520.203], [70.866, 534.529, 153.68, 546.484]]}]`

```text
Abstract
Improving the performance of large language
models (LLMs) in complex question-answering
(QA) scenarios has always been a research fo-
cal point. Recent studies have attempted to en-
hance LLMs’ performance by combining step-
wise planning with external retrieval. While
effective for advanced models like GPT-3.5,
smaller LLMs face challenges in decomposing
complex questions, necessitating supervised
fine-tuning. Previous work has relied on man-
ual annotation and knowledge distillation from
teacher LLMs, which are time-consuming and
not accurate enough. In this paper, we intro-
duce a novel framework for enhancing LLMs’
planning capabilities by using planning data
derived from knowledge graphs (KGs). LLMs
fine-tuned with this data have improved plan-
ning capabilities, better equipping them to han-
dle complex QA tasks that involve retrieval.
Evaluations on multiple datasets, including our
newly proposed benchmark, highlight the ef-
fectiveness of our framework and the benefits
of KG-derived planning data.
1
```

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 8—9；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`。

字符位置：`[{"pdf_page": 8, "start_char": 3661, "end_char": 4405, "chunk_start_char": 0, "chunk_end_char": 744, "block_bboxes": [[306.142, 552.544, 381.209, 564.499], [305.804, 574.956, 526.318, 775.47]]}, {"pdf_page": 9, "start_char": 0, "end_char": 754, "chunk_start_char": 745, "chunk_end_char": 1499, "block_bboxes": [[180.817, 292.104, 414.46, 302.067], [70.866, 324.955, 125.334, 336.91], [70.866, 346.852, 290.946, 371.348], [70.593, 373.953, 290.947, 452.691], [70.473, 455.399, 289.317, 547.583]]}]`

```text
Conclusion
In this paper, we try to enhance the planning ability
in retrieval-augmented LLMs using KGs. Specifi-
cally, we design a framework for Learning to Plan
from KG (LPKG). The proposed LPKG framework
first utilizes the rich patterns in the KGs to con-
struct planning data, then fine-tune planning LLMs
based on such data to enable them to conduct plan-
ning on downstream datasets, and ultimately get
the final answer through parsing and execution.
The experimental results reveal the excellent per-
formance of the LPKG framework and also demon-
strate the effectiveness of using KG-sourced data to
enhance LLMs’ planning ability. Finally, we con-
struct CLQA-Wiki, providing a more challenging
complex QA benchmark for the community.

Figure 4: Fine-grained evaluation based on question types.
Limitation
In our view, the limitations of our work at the cur-
rent stage mainly stem from two aspects:
(1) During the fine-tuning phase of planning
LLMs, we simply mixed various types of ques-
tions together uniformly for training. We have not
yet explored the impact of question type distribu-
tion on the experimental results, which could be
the focus of future work.
(2) At present, the datasets we test have explicit
types of questions (multi-hop, comparison, and
union/intersection), but in reality, some question
types may be implicit or even not be included in
the types we define. The future direction of our
work can be to study planning methods for these
types of unclear questions.
```

### F08 · 分类体系 · fact

Roadmap 综述把 LLM 与 KG 的结合分成哪三条路线？请保留三类名称，避免把其中一类当作全部路线。

**参考答案：** 三条路线为 KG-enhanced LLMs、LLM-augmented KGs 和 Synergized LLMs + KGs。

**逐项判分：**

- `F08.C01`：包含 KG-enhanced LLMs。（来源：roadmap）
- `F08.C02`：包含 LLM-augmented KGs。（来源：roadmap）
- `F08.C03`：包含 Synergized LLMs + KGs。（来源：roadmap）

**考查关系：** CLASSIFIES, HAS_CATEGORY

- 参考路径 `roadmap.P01`：Unifying Large Language Models and Knowledge Graphs: A Roadmap —CLASSIFIES→ LLM-KG integration —HAS_CATEGORY→ KG-enhanced LLMs
- 参考路径 `roadmap.P02`：LLM-KG integration —HAS_CATEGORY→ LLM-augmented KGs
- 参考路径 `roadmap.P03`：LLM-KG integration —HAS_CATEGORY→ Synergized LLMs + KGs

**完整来源：** Unifying Large Language Models and Knowledge Graphs: A Roadmap；PDF 页 1—1；`Surveys/010_Unifying Large Language Models and Knowledge Graphs A Roadmap.pdf`；块 `chunk_f9acd01074a4f478a8d9fe8c7e77be91`。

字符位置：`[{"pdf_page": 1, "start_char": 228, "end_char": 1869, "chunk_start_char": 0, "chunk_end_char": 1641, "block_bboxes": [[68.125, 167.798, 543.877, 299.997]]}]`

```text
Abstract—Large language models (LLMs), such as ChatGPT and GPT4, are making new waves in the field of natural language
processing and artificial intelligence, due to their emergent ability and generalizability. However, LLMs are black-box models, which
often fall short of capturing and accessing factual knowledge. In contrast, Knowledge Graphs (KGs), Wikipedia and Huapu for example,
are structured knowledge models that explicitly store rich factual knowledge. KGs can enhance LLMs by providing external knowledge
for inference and interpretability. Meanwhile, KGs are difficult to construct and evolve by nature, which challenges the existing methods
in KGs to generate new facts and represent unseen knowledge. Therefore, it is complementary to unify LLMs and KGs together and
simultaneously leverage their advantages. In this article, we present a forward-looking roadmap for the unification of LLMs and KGs.
Our roadmap consists of three general frameworks, namely, 1) KG-enhanced LLMs, which incorporate KGs during the pre-training and
inference phases of LLMs, or for the purpose of enhancing understanding of the knowledge learned by LLMs; 2) LLM-augmented KGs,
that leverage LLMs for different KG tasks such as embedding, completion, construction, graph-to-text generation, and question
answering; and 3) Synergized LLMs + KGs, in which LLMs and KGs play equal roles and work in a mutually beneficial way to enhance
both LLMs and KGs for bidirectional reasoning driven by both data and knowledge. We review and summarize existing efforts within
these three frameworks in our roadmap and pinpoint their future research directions.
```

### R01 · 搜索算法与协作检索 · cross

比较 ToG 与 ToG-2：前者由什么代理用什么搜索算法探索 KG，后者如何让实体、文档和两种检索相互配合？

**参考答案：** ToG 由 LLM 代理迭代执行 KG 束搜索，探索实体、关系和推理路径。ToG-2 用实体连接文档、以文档作为实体上下文，交替进行图检索和上下文检索。

**逐项判分：**

- `R01.C01`：ToG 的 LLM 代理迭代执行 KG 束搜索。（来源：tog）
- `R01.C02`：ToG 探索实体、关系与推理路径。（来源：tog）
- `R01.C03`：ToG-2 用实体连接文档，并把文档作为实体上下文。（来源：tog2）
- `R01.C04`：ToG-2 交替进行图检索和上下文检索。（来源：tog2）

**考查关系：** ALTERNATES, CONNECTS, RETRIEVES_FROM, USES_AGENT, USES_ALGORITHM

**错误边界：** 不能因流程不同就断言 ToG-2 在所有条件下更优。

- 参考路径 `tog.P01`：ToG —USES_AGENT→ LLM agent
- 参考路径 `tog.P02`：ToG —USES_ALGORITHM→ iterative beam search —RETRIEVES_FROM→ knowledge graph
- 参考路径 `tog.P03`：iterative beam search —CONNECTS→ entity and relation paths

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 1—1；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_e09b5a88c34014513aad6c0d6121f790`。

字符位置：`[{"pdf_page": 1, "start_char": 517, "end_char": 2163, "chunk_start_char": 0, "chunk_end_char": 1646, "block_bboxes": [[278.288, 276.647, 333.722, 288.602], [143.507, 303.075, 469.793, 532.166], [108.299, 556.334, 205.989, 568.289]]}]`

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

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 3—4；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_d6a1257a27b9a4e3fd151b8c87ebf491`。

字符位置：`[{"pdf_page": 3, "start_char": 2828, "end_char": 3753, "chunk_start_char": 0, "chunk_end_char": 925, "block_bboxes": [[107.691, 575.993, 504.005, 641.11], [108.249, 658.672, 211.179, 668.635], [108.249, 680.202, 293.39, 690.165], [108.0, 700.313, 504.002, 732.268], [303.509, 752.194, 308.49, 762.157]]}, {"pdf_page": 4, "start_char": 0, "end_char": 487, "chunk_start_char": 926, "chunk_end_char": 1413, "block_bboxes": [[108.0, 27.813, 293.095, 37.776], [108.0, 80.423, 232.161, 94.255], [108.0, 82.759, 503.999, 105.19], [108.249, 122.764, 201.665, 132.727], [107.641, 143.134, 504.002, 165.406], [121.495, 154.164, 146.392, 167.216], [141.966, 154.164, 166.242, 167.346], [162.093, 153.426, 199.6, 167.216], [182.67, 154.164, 243.19, 168.665], [239.041, 154.164, 280.776, 168.123], [276.627, 154.164, 444.946, 168.123], [108.0, 155.598, 504.003, 179.71], [213.519, 168.214, 238.417, 181.266], [233.991, 168.214, 258.266, 181.397], [254.117, 168.214, 313.207, 181.266], [298.969, 167.568, 337.139, 181.919], [322.624, 168.214, 360.938, 182.233]]}]`

```text
ToG implements the “LLM ⊗KG” paradigm by asking LLM to perform beam search on knowledge
graph. Specifically, it prompts the LLM to iteratively explore multiple possible reasoning paths on
KGs until the LLM determines that the question can be answered based on the current reasoning
paths. ToG constantly updates and maintains top-N reasoning paths P = {p1, p2, . . . , pN} for the
question x after each iteration, where N denotes the width of beam search. The entire inference
process of ToG contains the following 3 phases: initialization, exploration, and reasoning.
2.1
THINK-ON-GRAPH
2.1.1
INITIALIZATION OF GRAPH SEARCH
Given a question, ToG leverages the underlying LLM to localize the initial entity of the reasoning
paths on knowledge graph. This phase can be regarded as the initialization of the top-N reasoning
paths P. ToG first prompts LLMs to automatically extract the topic entities in question and gets the
3

Published as a conference paper at ICLR 2024
top-N topic entities E0 = {e0
1, e0
2, ..., e0
N} to the question. Note that the number of topic entities
might possibly be less than N.
2.1.2
EXPLORATION
At the beginning of the D-th iteration, each path pn consists of D −1 triples, i.e., pn =
{(ed
s,n, rd
j,n, ed
o,n)}D−1
d=1 , where ed
s,n and ed
o,n denote subject and object entities, rd
j,n is a specific
relation between them, (ed
s,n, rd
j,n, ed
o,n) and (ed+1
s,n , rd+1
j,n , ed+1
```

- 参考路径 `tog2.P01`：ToG-2 —CONNECTS→ entities linked to documents
- 参考路径 `tog2.P02`：ToG-2 —ALTERNATES→ graph retrieval
- 参考路径 `tog2.P03`：ToG-2 —ALTERNATES→ context retrieval
- 参考路径 `tog2.P04`：graph retrieval —CONNECTS→ context retrieval

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 1—1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_9b63637ef18ed2d67ff105ef55092df3`。

字符位置：`[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

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

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 3—3；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

字符位置：`[{"pdf_page": 3, "start_char": 223, "end_char": 1439, "chunk_start_char": 0, "chunk_end_char": 1216, "block_bboxes": [[108.0, 112.073, 504.003, 253.634], [108.299, 272.586, 217.097, 284.541]]}]`

```text
The advantage of ToG-2 can be summarized as: (1) In-depth retrieval: ToG-2 achieves in-depth
and reliable context retrieval through the guide of KGs and performs precise graph retrieval by
treating documents as node contexts, achieving a tight-coupling combination of KG and text RAG,
enabling deep and comprehensive retrieval processes. (2) Faithful reasoning: ToG-2 iteratively
performs a collaborative retrieval process based on KG and text, using retrieved heterogeneous
knowledge as the basis for LLM reasoning and enhancing the faithfulness of LLM-generated con-
tent (3) Efficiency and Effectiveness: a) ToG-2 is a training-free and plug-and-play framework that
can be applied to various LLMs; b) ToG-2 can be executed between any associated KG and docu-
ment database, while for purely document database, entities can be extracted from the documents
first, and then a graph can be constructed through relation extraction or entity co-occurrence (Edge
et al., 2024); c) ToG-2 achieves new SOTA performances on various complex knowledge reasoning
datasets and can elevate the reasoning capabilities of smaller LLMs, e.g., Llama2-13B to a level
comparable to direct reasoning with powerful LLMs like GPT-3.5.
2
```

### R02 · 查询种子与关系计划 · cross

面对多跳问题，HippoRAG 与 RoG 怎样分别从问题走到证据？请区分查询种子、PPR、关系路径计划和有效推理路径。

**参考答案：** HippoRAG 以查询关键概念为种子运行 PPR，整合跨段落证据。RoG 先生成由 KG 约束的关系路径计划，再用计划检索有效推理路径供 LLM 推理。二者机制不同，不能互换算法名。

**逐项判分：**

- `R02.C01`：HippoRAG 以查询概念启动 PPR 并整合跨段落信息。（来源：hippo）
- `R02.C02`：RoG 先生成 KG 约束的关系路径计划。（来源：rog）
- `R02.C03`：RoG 根据计划检索有效推理路径，再供 LLM 推理。（来源：rog）

**考查关系：** CONNECTS, HAS_STAGE, TRAINED_WITH, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 不能把 RoG 的关系路径计划说成 PPR，也不能据此建立技术继承。

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R03 · 增强方向与监督目标 · cross

CuriousLLM 与 KGP 的增强关系朝哪个方向？结合 KGP 的遍历任务，说明 CuriousLLM 的 Follow-upQA 输入、监督目标和证据充分信号。

**参考答案：** CuriousLLM 是对 KGP 的增强；KGP 的代理收集支持段落。Follow-upQA 以问题和支持证据为输入、后续问题为目标，也用特殊 token 表示已有证据充分。

**逐项判分：**

- `R03.C01`：KGP 遍历代理收集支持段落。（来源：kgp）
- `R03.C02`：增强方向是 CuriousLLM 指向 KGP。（来源：curious）
- `R03.C03`：Follow-upQA 输入是问题和支持证据，目标是后续问题。（来源：curious）
- `R03.C04`：特殊 token 表示证据充分，作者报告的收益不能写成本项目实测。（来源：curious）

**考查关系：** COLLECTS, ENHANCES, GENERATES, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, HAS_TARGET, USES_AGENT, USES_INPUT

**错误边界：** 增强方向是 CuriousLLM → KGP，不得反转，也不能把作者报告说成此系统的复现实测。

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

### R04 · 推理接口与训练数据 · cross

StructGPT 和 LPKG 都使用结构化知识，但知识进入系统的阶段相同吗？请分别追踪专门接口与 KG 派生规划数据的用途。

**参考答案：** 不同。StructGPT 在回答时通过专门接口迭代读取结构化证据，再让 LLM 推理；LPKG 从 KG 构造 planning data，用于微调规划能力。

**逐项判分：**

- `R04.C01`：StructGPT 通过专门接口取得结构化证据。（来源：struct）
- `R04.C02`：读取与基于证据推理迭代进行。（来源：struct）
- `R04.C03`：LPKG 用 KG 派生的规划数据微调规划能力。（来源：lpdata）
- `R04.C04`：推理时接口访问与训练数据构建属于不同阶段。（来源：struct, lpdata）

**考查关系：** CONNECTS, DERIVES_TRAINING_DATA_FROM, HAS_STAGE, USES_COMPONENT, USES_TRAINING_SIGNAL

**错误边界：** 不能把推理时读取接口等同于训练数据构建。

- 参考路径 `struct.P01`：StructGPT —USES_COMPONENT→ dedicated interface —CONNECTS→ structured evidence —CONNECTS→ LLM reasoning

**完整来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 页 1—1；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；块 `chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`。

字符位置：`[{"pdf_page": 1, "start_char": 480, "end_char": 1582, "chunk_start_char": 0, "chunk_end_char": 1102, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.565, 238.04, 273.783, 523.046], [70.866, 535.569, 153.68, 547.524]]}]`

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

**完整来源：** StructGPT: A General Framework for Large Language Model to Reason over Structured Data；PDF 页 9—10；`Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf`；块 `chunk_bd4734d2765e2147cac924fe8ba38d85`。

字符位置：`[{"pdf_page": 9, "start_char": 2518, "end_char": 3569, "chunk_start_char": 0, "chunk_end_char": 1051, "block_bboxes": [[306.142, 459.593, 381.209, 471.548], [306.142, 491.833, 526.225, 773.66]]}, {"pdf_page": 10, "start_char": 0, "end_char": 2, "chunk_start_char": 1052, "chunk_end_char": 1054, "block_bboxes": [[70.866, 72.649, 147.917, 84.604]]}]`

```text
Conclusion
In this work, we proposed a general framework for
improving the zero-shot reasoning ability of LLMs
over structured data, namely StructGPT. In our ap-
proach, we first constructed the specialized inter-
faces that support accurate and efficient data ac-
cess, and then proposed an invoking-linearization-
generation procedure that leverages LLMs to read
and perform reasoning based on the interface. By
iterating the above procedure using the interfaces
sequentially, LLMs can progressively capture more
useful and detailed evidence and finally generate
the answer.
To verify the effectiveness of our
approach, we implemented our approach on KG
based QA, table based QA and DB based semantic
parsing tasks. Experimental results on 8 datasets
show that our approach can boost the zero-shot per-
formance of LLMs by a large margin, and achieve
comparable performance as full-data supervised-
tuning methods. We also provide detailed error
analysis to point out the weakness of our approach,
for enlighting other researchers in related areas.

7
```

- 参考路径 `lpdata.P01`：LPKG —DERIVES_TRAINING_DATA_FROM→ knowledge graph
- 参考路径 `lpdata.P02`：LPKG —USES_TRAINING_SIGNAL→ planning data —CONNECTS→ small model fine-tuning
- 参考路径 `lpdata.P03`：LPKG —HAS_STAGE→ complex QA planning

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 1—1；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_e07b345ba2a42d01f295e47f196061d5`。

字符位置：`[{"pdf_page": 1, "start_char": 576, "end_char": 1608, "chunk_start_char": 0, "chunk_end_char": 1032, "block_bboxes": [[157.758, 205.751, 384.313, 233.647], [87.516, 247.152, 273.866, 520.203], [70.866, 534.529, 153.68, 546.484]]}]`

```text
Abstract
Improving the performance of large language
models (LLMs) in complex question-answering
(QA) scenarios has always been a research fo-
cal point. Recent studies have attempted to en-
hance LLMs’ performance by combining step-
wise planning with external retrieval. While
effective for advanced models like GPT-3.5,
smaller LLMs face challenges in decomposing
complex questions, necessitating supervised
fine-tuning. Previous work has relied on man-
ual annotation and knowledge distillation from
teacher LLMs, which are time-consuming and
not accurate enough. In this paper, we intro-
duce a novel framework for enhancing LLMs’
planning capabilities by using planning data
derived from knowledge graphs (KGs). LLMs
fine-tuned with this data have improved plan-
ning capabilities, better equipping them to han-
dle complex QA tasks that involve retrieval.
Evaluations on multiple datasets, including our
newly proposed benchmark, highlight the ef-
fectiveness of our framework and the benefits
of KG-derived planning data.
1
```

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 8—9；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`。

字符位置：`[{"pdf_page": 8, "start_char": 3661, "end_char": 4405, "chunk_start_char": 0, "chunk_end_char": 744, "block_bboxes": [[306.142, 552.544, 381.209, 564.499], [305.804, 574.956, 526.318, 775.47]]}, {"pdf_page": 9, "start_char": 0, "end_char": 754, "chunk_start_char": 745, "chunk_end_char": 1499, "block_bboxes": [[180.817, 292.104, 414.46, 302.067], [70.866, 324.955, 125.334, 336.91], [70.866, 346.852, 290.946, 371.348], [70.593, 373.953, 290.947, 452.691], [70.473, 455.399, 289.317, 547.583]]}]`

```text
Conclusion
In this paper, we try to enhance the planning ability
in retrieval-augmented LLMs using KGs. Specifi-
cally, we design a framework for Learning to Plan
from KG (LPKG). The proposed LPKG framework
first utilizes the rich patterns in the KGs to con-
struct planning data, then fine-tune planning LLMs
based on such data to enable them to conduct plan-
ning on downstream datasets, and ultimately get
the final answer through parsing and execution.
The experimental results reveal the excellent per-
formance of the LPKG framework and also demon-
strate the effectiveness of using KG-sourced data to
enhance LLMs’ planning ability. Finally, we con-
struct CLQA-Wiki, providing a more challenging
complex QA benchmark for the community.

Figure 4: Fine-grained evaluation based on question types.
Limitation
In our view, the limitations of our work at the cur-
rent stage mainly stem from two aspects:
(1) During the fine-tuning phase of planning
LLMs, we simply mixed various types of ques-
tions together uniformly for training. We have not
yet explored the impact of question type distribu-
tion on the experimental results, which could be
the focus of future work.
(2) At present, the datasets we test have explicit
types of questions (multi-hop, comparison, and
union/intersection), but in reality, some question
types may be implicit or even not be included in
the types we define. The future direction of our
work can be to study planning methods for these
types of unclear questions.
```

### R05 · 免训练与蒸馏训练 · cross

ToG 的 training-free 与 RoG 的 KG 知识蒸馏分别描述什么？RoG 推理时能接入其他 LLM，是否等于整个方法不需要训练？

**参考答案：** ToG 自述为无需额外训练的即插即用方法。RoG 包含 KG 知识蒸馏训练，推理时生成关系计划并检索路径；可接入其他 LLM 不等于整套方法没有训练。

**逐项判分：**

- `R05.C01`：ToG 描述为 training-free、无需额外训练。（来源：tog_training）
- `R05.C02`：RoG 包含从 KG 蒸馏知识的训练。（来源：rog）
- `R05.C03`：RoG 推理时做关系计划和路径检索。（来源：rog）
- `R05.C04`：兼容其他推理 LLM 不能推出全流程免训练。（来源：rog）

**考查关系：** CONNECTS, HAS_STAGE, TRAINED_WITH, USES_COMPONENT, USES_TRAINING_MODE

**错误边界：** RoG 推理模块可接入其他 LLM 不等于整套 RoG 没有训练。

- 参考路径 `tog_training.P01`：ToG —USES_TRAINING_MODE→ training-free
- 参考路径 `tog_training.P02`：ToG —USES_COMPONENT→ plug-and-play across LLMs and KGs

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 1—1；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_e09b5a88c34014513aad6c0d6121f790`。

字符位置：`[{"pdf_page": 1, "start_char": 517, "end_char": 2163, "chunk_start_char": 0, "chunk_end_char": 1646, "block_bboxes": [[278.288, 276.647, 333.722, 288.602], [143.507, 303.075, 469.793, 532.166], [108.299, 556.334, 205.989, 568.289]]}]`

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

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R06 · 图知识使用阶段 · cross

ToG-2 与 LPKG 中的图知识分别在什么阶段发挥作用、服务什么目标？请分别说明协作检索与规划数据的路径。

**参考答案：** ToG-2 在推理时让图检索和上下文检索交替协作，寻找问题证据；LPKG 从 KG 构造规划数据并用于微调，提升复杂问答规划能力。

**逐项判分：**

- `R06.C01`：ToG-2 在推理时协作检索图与文档上下文。（来源：tog2）
- `R06.C02`：LPKG 从 KG 派生规划数据。（来源：lpdata）
- `R06.C03`：规划数据用于训练规划能力。（来源：lpdata）
- `R06.C04`：在线检索与训练用途必须分开，不能视为同一训练协议。（来源：tog2, lpdata）

**考查关系：** ALTERNATES, CONNECTS, DERIVES_TRAINING_DATA_FROM, HAS_STAGE, USES_TRAINING_SIGNAL

**错误边界：** 共享 KG/QA 目标不表示训练协议或算法相同。

- 参考路径 `tog2.P01`：ToG-2 —CONNECTS→ entities linked to documents
- 参考路径 `tog2.P02`：ToG-2 —ALTERNATES→ graph retrieval
- 参考路径 `tog2.P03`：ToG-2 —ALTERNATES→ context retrieval
- 参考路径 `tog2.P04`：graph retrieval —CONNECTS→ context retrieval

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 1—1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_9b63637ef18ed2d67ff105ef55092df3`。

字符位置：`[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

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

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 3—3；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

字符位置：`[{"pdf_page": 3, "start_char": 223, "end_char": 1439, "chunk_start_char": 0, "chunk_end_char": 1216, "block_bboxes": [[108.0, 112.073, 504.003, 253.634], [108.299, 272.586, 217.097, 284.541]]}]`

```text
The advantage of ToG-2 can be summarized as: (1) In-depth retrieval: ToG-2 achieves in-depth
and reliable context retrieval through the guide of KGs and performs precise graph retrieval by
treating documents as node contexts, achieving a tight-coupling combination of KG and text RAG,
enabling deep and comprehensive retrieval processes. (2) Faithful reasoning: ToG-2 iteratively
performs a collaborative retrieval process based on KG and text, using retrieved heterogeneous
knowledge as the basis for LLM reasoning and enhancing the faithfulness of LLM-generated con-
tent (3) Efficiency and Effectiveness: a) ToG-2 is a training-free and plug-and-play framework that
can be applied to various LLMs; b) ToG-2 can be executed between any associated KG and docu-
ment database, while for purely document database, entities can be extracted from the documents
first, and then a graph can be constructed through relation extraction or entity co-occurrence (Edge
et al., 2024); c) ToG-2 achieves new SOTA performances on various complex knowledge reasoning
datasets and can elevate the reasoning capabilities of smaller LLMs, e.g., Llama2-13B to a level
comparable to direct reasoning with powerful LLMs like GPT-3.5.
2
```

- 参考路径 `lpdata.P01`：LPKG —DERIVES_TRAINING_DATA_FROM→ knowledge graph
- 参考路径 `lpdata.P02`：LPKG —USES_TRAINING_SIGNAL→ planning data —CONNECTS→ small model fine-tuning
- 参考路径 `lpdata.P03`：LPKG —HAS_STAGE→ complex QA planning

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 1—1；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_e07b345ba2a42d01f295e47f196061d5`。

字符位置：`[{"pdf_page": 1, "start_char": 576, "end_char": 1608, "chunk_start_char": 0, "chunk_end_char": 1032, "block_bboxes": [[157.758, 205.751, 384.313, 233.647], [87.516, 247.152, 273.866, 520.203], [70.866, 534.529, 153.68, 546.484]]}]`

```text
Abstract
Improving the performance of large language
models (LLMs) in complex question-answering
(QA) scenarios has always been a research fo-
cal point. Recent studies have attempted to en-
hance LLMs’ performance by combining step-
wise planning with external retrieval. While
effective for advanced models like GPT-3.5,
smaller LLMs face challenges in decomposing
complex questions, necessitating supervised
fine-tuning. Previous work has relied on man-
ual annotation and knowledge distillation from
teacher LLMs, which are time-consuming and
not accurate enough. In this paper, we intro-
duce a novel framework for enhancing LLMs’
planning capabilities by using planning data
derived from knowledge graphs (KGs). LLMs
fine-tuned with this data have improved plan-
ning capabilities, better equipping them to han-
dle complex QA tasks that involve retrieval.
Evaluations on multiple datasets, including our
newly proposed benchmark, highlight the ef-
fectiveness of our framework and the benefits
of KG-derived planning data.
1
```

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 8—9；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`。

字符位置：`[{"pdf_page": 8, "start_char": 3661, "end_char": 4405, "chunk_start_char": 0, "chunk_end_char": 744, "block_bboxes": [[306.142, 552.544, 381.209, 564.499], [305.804, 574.956, 526.318, 775.47]]}, {"pdf_page": 9, "start_char": 0, "end_char": 754, "chunk_start_char": 745, "chunk_end_char": 1499, "block_bboxes": [[180.817, 292.104, 414.46, 302.067], [70.866, 324.955, 125.334, 336.91], [70.866, 346.852, 290.946, 371.348], [70.593, 373.953, 290.947, 452.691], [70.473, 455.399, 289.317, 547.583]]}]`

```text
Conclusion
In this paper, we try to enhance the planning ability
in retrieval-augmented LLMs using KGs. Specifi-
cally, we design a framework for Learning to Plan
from KG (LPKG). The proposed LPKG framework
first utilizes the rich patterns in the KGs to con-
struct planning data, then fine-tune planning LLMs
based on such data to enable them to conduct plan-
ning on downstream datasets, and ultimately get
the final answer through parsing and execution.
The experimental results reveal the excellent per-
formance of the LPKG framework and also demon-
strate the effectiveness of using KG-sourced data to
enhance LLMs’ planning ability. Finally, we con-
struct CLQA-Wiki, providing a more challenging
complex QA benchmark for the community.

Figure 4: Fine-grained evaluation based on question types.
Limitation
In our view, the limitations of our work at the cur-
rent stage mainly stem from two aspects:
(1) During the fine-tuning phase of planning
LLMs, we simply mixed various types of ques-
tions together uniformly for training. We have not
yet explored the impact of question type distribu-
tion on the experimental results, which could be
the focus of future work.
(2) At present, the datasets we test have explicit
types of questions (multi-hop, comparison, and
union/intersection), but in reality, some question
types may be implicit or even not be included in
the types we define. The future direction of our
work can be to study planning methods for these
types of unclear questions.
```

### R07 · 两种文档图表示 · cross

HippoRAG 与 KGP 都从文档获取证据：各自把语料组织成什么图，又通过什么机制找回跨段落支持？

**参考答案：** HippoRAG 用 LLM 将语料转为无模式 KG，以查询概念启动 PPR 整合跨段落信息；KGP 以段落或文档结构为节点、相似或结构关系为边，由 LLM 遍历代理收集支持段落。

**逐项判分：**

- `R07.C01`：HippoRAG 将语料转为无模式 KG。（来源：hippo）
- `R07.C02`：HippoRAG 以查询种子驱动 PPR。（来源：hippo）
- `R07.C03`：KGP 的节点为段落/文档结构，边为相似/结构关系。（来源：kgp）
- `R07.C04`：KGP 用 LLM 遍历代理收集支持段落。（来源：kgp）

**考查关系：** COLLECTS, CONNECTS, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, USES_AGENT, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 不能把 KGP 的节点定义直接套到 HippoRAG。

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

### R08 · 子图选择与图文协作 · cross

G-Retriever 为什么不把大图全部文本化后直接交给 LLM，它怎样选择证据？ToG-2 又怎样组织图与文档证据？

**参考答案：** 整图文本化可能超过上下文窗口，截断会丢信息。G-Retriever 将子图检索建模为 PCST，选择相关部分；ToG-2 通过实体连接文档，并交替进行图检索和上下文检索。

**逐项判分：**

- `R08.C01`：整图文本化会带来上下文容量问题，直接截断会丢失信息。（来源：grscale）
- `R08.C02`：G-Retriever 用 PCST 建模相关子图检索。（来源：pcst）
- `R08.C03`：通过选择相关子图控制送入模型的图内容。（来源：grscale）
- `R08.C04`：ToG-2 通过实体连接文档，交替检索图和上下文。（来源：tog2）

**考查关系：** ALTERNATES, CONNECTS, FORMULATES_AS, SELECTS

**错误边界：** 不能声称 ToG-2 使用 PCST，也不能从机制描述推出两者资源实测相同。

- 参考路径 `grscale.P01`：G-Retriever —FORMULATES_AS→ Prize-Collecting Steiner Tree —SELECTS→ relevant subgraph —CONNECTS→ bounded LLM context

**完整来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 页 2—3；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；块 `chunk_5c9e14854565607ec53c355da481c451`。

字符位置：`[{"pdf_page": 2, "start_char": 5377, "end_char": 6545, "chunk_start_char": 0, "chunk_end_char": 1168, "block_bboxes": [[108.0, 586.878, 505.247, 673.291], [107.671, 679.55, 504.666, 722.414], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 3, "start_char": 0, "end_char": 302, "chunk_start_char": 1169, "chunk_end_char": 1471, "block_bboxes": [[168.567, 79.054, 443.126, 89.017], [115.77, 114.927, 128.937, 121.901], [249.671, 108.103, 269.888, 112.519], [254.373, 133.834, 265.179, 138.25], [253.452, 120.655, 299.773, 127.581], [276.078, 115.32, 279.876, 119.736], [275.608, 135.402, 324.86, 141.388], [307.236, 120.968, 330.932, 125.385], [309.393, 108.103, 327.516, 112.519], [240.86, 148.186, 489.169, 163.13], [115.77, 201.212, 202.238, 208.186]]}]`

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

- 参考路径 `pcst.P01`：G-Retriever —FORMULATES_AS→ Prize-Collecting Steiner Tree —SELECTS→ relevant subgraph

**完整来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 页 1—1；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；块 `chunk_3a7f7a1f47b2586d9d9877afb9110567`。

字符位置：`[{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}]`

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

- 参考路径 `tog2.P01`：ToG-2 —CONNECTS→ entities linked to documents
- 参考路径 `tog2.P02`：ToG-2 —ALTERNATES→ graph retrieval
- 参考路径 `tog2.P03`：ToG-2 —ALTERNATES→ context retrieval
- 参考路径 `tog2.P04`：graph retrieval —CONNECTS→ context retrieval

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 1—1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_9b63637ef18ed2d67ff105ef55092df3`。

字符位置：`[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

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

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 3—3；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

字符位置：`[{"pdf_page": 3, "start_char": 223, "end_char": 1439, "chunk_start_char": 0, "chunk_end_char": 1216, "block_bboxes": [[108.0, 112.073, 504.003, 253.634], [108.299, 272.586, 217.097, 284.541]]}]`

```text
The advantage of ToG-2 can be summarized as: (1) In-depth retrieval: ToG-2 achieves in-depth
and reliable context retrieval through the guide of KGs and performs precise graph retrieval by
treating documents as node contexts, achieving a tight-coupling combination of KG and text RAG,
enabling deep and comprehensive retrieval processes. (2) Faithful reasoning: ToG-2 iteratively
performs a collaborative retrieval process based on KG and text, using retrieved heterogeneous
knowledge as the basis for LLM reasoning and enhancing the faithfulness of LLM-generated con-
tent (3) Efficiency and Effectiveness: a) ToG-2 is a training-free and plug-and-play framework that
can be applied to various LLMs; b) ToG-2 can be executed between any associated KG and docu-
ment database, while for purely document database, entities can be extracted from the documents
first, and then a graph can be constructed through relation extraction or entity co-occurrence (Edge
et al., 2024); c) ToG-2 achieves new SOTA performances on various complex knowledge reasoning
datasets and can elevate the reasoning capabilities of smaller LLMs, e.g., Llama2-13B to a level
comparable to direct reasoning with powerful LLMs like GPT-3.5.
2
```

### R09 · 共享数据集的连接边界 · cross

仅限两篇实验段落明确列出的 KBQA 数据集，ToG 与 ToG-2 共同包含哪两个？共享这些数据集是否足以证明方法继承或受控性能优劣？

**参考答案：** 共同的 KBQA 数据集是 WebQSP 和 QALD10-en。共享评测对象只建立评测关联，不能单独证明方法继承，也不能在未核对划分、底座、知识来源等条件时给出受控性能结论。

**逐项判分：**

- `R09.C01`：共同 KBQA 数据集包含 WebQSP。（来源：togds, tog2ds）
- `R09.C02`：共同 KBQA 数据集包含 QALD10-en。（来源：togds, tog2ds）
- `R09.C03`：共享数据集不自动建立方法继承。（来源：togds, tog2ds）
- `R09.C04`：性能比较还需匹配划分、底座、知识来源等实验条件。（来源：togds, tog2ds）

**考查关系：** DERIVED_FROM, EVALUATED_ON, REPORTS_METRIC, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE

**错误边界：** 共享数据集不等于相同划分、底座、知识来源或比较协议。

- 参考路径 `togds.P01`：ToG —EVALUATED_ON→ WebQSP
- 参考路径 `togds.P02`：ToG —EVALUATED_ON→ QALD10-en
- 参考路径 `togds.P03`：ToG —EVALUATED_ON→ Creak
- 参考路径 `togds.P04`：ToG —REPORTS_METRIC→ exact match accuracy (Hits@1)

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 5—5；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_deb9eea46e529705dffdd1103729c44c`。

字符位置：`[{"pdf_page": 5, "start_char": 2914, "end_char": 4358, "chunk_start_char": 0, "chunk_end_char": 1444, "block_bboxes": [[108.299, 482.573, 200.083, 494.529], [108.249, 507.855, 235.26, 517.818], [108.249, 528.452, 305.88, 538.415], [107.671, 547.628, 504.824, 656.296], [108.249, 670.178, 310.993, 680.141], [107.532, 689.505, 505.652, 732.293], [303.509, 752.194, 308.49, 762.157]]}]`

```text
EXPERIMENTS
3.1
EXPERIMENTAL DESIGN
3.1.1
DATASETS AND EVALUATION METRICS
In order to test ToG’s ability on multi-hop knowledge-intensive reasoning tasks, we evaluate ToG
on five KBQA datasets (4 Multi-hop and 1 Single-hop): CWQ (Talmor & Berant, 2018), WebQSP
(Yih et al., 2016), GrailQA (Gu et al., 2021), QALD10-en (Perevalov et al., 2022), Simple Questions
(Bordes et al., 2015). Moreover, in order to examine ToG on more generic tasks, we also prepare
one open-domain QA dataset: WebQuestions (Berant et al., 2013); two slot filling datasets: T-REx
(ElSahar et al., 2018) and Zero-Shot RE (Petroni et al., 2021); and one fact-checking dataset: Creak
(Onoe et al., 2021). Note that, for two big datasets GrailQA and Simple Questions, we only randomly
selected 1,000 samples each for testing in order to save computational cost. For all datasets, exact
match accuracy (Hits@1) is used as our evaluation metric following previous works (Li et al., 2023c;
Baek et al., 2023b; Jiang et al., 2023; Li et al., 2023a).
3.1.2
METHODS SELECTED FOR COMPARISON
We compare with standard prompting (IO prompt) (Brown et al., 2020b), Chain-of-Thought prompting
(CoT prompt) (Wei et al., 2022), and Self-Consistency (Wang et al., 2023c) with 6 in-context
exemplars and "step-by-step" reasoning chains. Moreover, for each dataset, we pick previous state-of-
the-art (SOTA) works for comparison. We notice that fine-tuning methods trained specifically on
5
```

- 参考路径 `tog2ds.P01`：ToG-2 —EVALUATED_ON→ WebQSP
- 参考路径 `tog2ds.P02`：ToG-2 —EVALUATED_ON→ QALD10-en
- 参考路径 `tog2ds.P03`：ToG-2 —EVALUATED_ON→ AdvHotpotQA
- 参考路径 `tog2ds.P04`：ToG-2 —EVALUATED_ON→ FEVER
- 参考路径 `tog2ds.P05`：ToG-2 —EVALUATED_ON→ Creak
- 参考路径 `tog2ds.P06`：AdvHotpotQA —DERIVED_FROM→ HotpotQA
- 参考路径 `tog2ds.P07`：ToG-2 evaluation —USES_KNOWLEDGE_BASE→ full Wikipedia and Wikidata
- 参考路径 `tog2ds.P08`：ToG-2 evaluation —REPORTS_METRIC→ Accuracy on FEVER and Creak
- 参考路径 `tog2ds.P09`：ToG-2 evaluation —REPORTS_METRIC→ EM on other datasets
- 参考路径 `tog2ds.P10`：ToG-2 —USES_EVALUATION_SETTING→ ToG-2 evaluation

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 6—6；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

字符位置：`[{"pdf_page": 6, "start_char": 1827, "end_char": 2910, "chunk_start_char": 0, "chunk_end_char": 1083, "block_bboxes": [[108.299, 418.062, 200.083, 430.017], [108.249, 442.645, 239.271, 452.608], [108.0, 463.168, 504.003, 582.72]]}]`

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

### R10 · 数据集名称与检索机制 · cross

HippoRAG 与 Tree-of-Traversals 各自怎样命名所评测的 2Wiki 数据集，又分别怎样进行跨事实检索或搜索？名称相似能否证明协议一致？

**参考答案：** HippoRAG 列出 2WikiMultiHopQA，以查询种子驱动 PPR；Tree-of-Traversals 列出 2WikiMultiHop，搜索由动作与推理链构成的树并设搜索边界。名称相似不能证明划分、语料、底座或指标一致。

**逐项判分：**

- `R10.C01`：HippoRAG 来源名称为 2WikiMultiHopQA。（来源：hippods）
- `R10.C02`：Tree-of-Traversals 来源名称为 2WikiMultiHop。（来源：totds）
- `R10.C03`：HippoRAG 使用查询概念驱动的 PPR。（来源：hippo）
- `R10.C04`：Tree-of-Traversals 搜索动作/推理链构成的树并限制搜索。（来源：totbound）
- `R10.C05`：不能由名称相似认定实验协议一致。（来源：hippods, totds）

**考查关系：** BOUNDED_BY, CONNECTS, EVALUATED_ON, HAS_SAMPLE_SETTING, HAS_STOP_CONDITION, RETURNS, USES_ALGORITHM, USES_COMPONENT, USES_EVALUATION_SETTING, USES_INPUT, USES_KNOWLEDGE_BASE

**错误边界：** 名称相似不证明划分、语料、底座或指标相同。

- 参考路径 `hippods.P01`：HippoRAG —EVALUATED_ON→ MuSiQue (answerable)
- 参考路径 `hippods.P02`：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA
- 参考路径 `hippods.P03`：HippoRAG —EVALUATED_ON→ HotpotQA
- 参考路径 `hippods.P04`：HippoRAG retrieval corpus —HAS_SAMPLE_SETTING→ 1000 validation questions per dataset
- 参考路径 `hippods.P05`：HippoRAG retrieval corpus —USES_KNOWLEDGE_BASE→ supporting and distractor passages
- 参考路径 `hippods.P06`：HippoRAG —USES_EVALUATION_SETTING→ HippoRAG retrieval corpus

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 5—5；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_3fa28005a4df0de5249826585cf9d713`。

字符位置：`[{"pdf_page": 5, "start_char": 2205, "end_char": 3400, "chunk_start_char": 0, "chunk_end_char": 1195, "block_bboxes": [[107.532, 383.68, 505.653, 470.063], [119.512, 481.129, 492.488, 491.322], [314.205, 502.845, 447.078, 511.811], [162.683, 517.888, 447.078, 577.187], [108.0, 592.604, 169.718, 602.566]]}]`

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

- 参考路径 `totds.P01`：Tree-of-Traversals —EVALUATED_ON→ 2WikiMultiHop
- 参考路径 `totds.P02`：Tree-of-Traversals —EVALUATED_ON→ QALD-10

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 5—5；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_a8ce6be635ba6abbbc71daeb86e809e9`。

字符位置：`[{"pdf_page": 5, "start_char": 888, "end_char": 2200, "chunk_start_char": 0, "chunk_end_char": 1312, "block_bboxes": [[70.866, 373.795, 153.883, 385.75], [70.353, 397.537, 290.946, 408.538], [70.506, 409.426, 290.943, 516.91], [70.866, 531.077, 186.841, 541.986], [70.353, 550.22, 289.137, 561.172], [70.866, 563.885, 290.95, 628.908], [70.866, 632.233, 290.941, 751.637], [83.519, 762.682, 248.401, 772.731], [309.977, 73.825, 520.839, 98.283], [357.666, 100.732, 473.149, 111.832]]}]`

```text
Experiments
We evaluate Tree-of-Traversals using three differ-
ent models available on Amazon Bedrock3: Claude-
Instant (claude-instant-v1), Llama2 70b
(llama2-70b-chat-v1), and Llama2 13b
(llama2-13b-chat-v1). AWS Bedrock pro-
vides on-demand access through a single API to
various Foundation Models, including both open
source and black box ones. This is precisely a use
case Tree-of-Traversals is designed for.
3.1
Tasks and Datasets.
We first evaluate the Tree-of-Traversals algorithm
on two common tasks used for evaluating an LLM’s
knowledge: 2WikiMultiHop and QALD-10. To al-
low testing on complex questions requiring knowl-
edge from multiple KGs we create a new dataset
that requires knowledge from multiple KGs.
2WikiMultiHop Dataset (Ho et al., 2020) was
constructed by extracting multi-hop templates from
HotPotQA (Yang et al., 2018), combining tem-
plates to get complex reasoning questions, gener-
ating candidate questions with Wikidata, and then
confirming that the entity mentions for each edge
appear in the Wikipedia paragraphs. Answers to
these questions can be derived from both Wikipedia
and Wikidata (Vrandeˇci´c and Krötzsch, 2014). We
3https://aws.amazon.com/bedrock
Which event was hosted in a venue with a larger
maximum capacity, Fearless Tour: Indianapolis
or Fearless Tour: Omaha?
```

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

### R11 · 训练测试角色与指标 · cross

请对齐 KG-GPT 与 RoG 的 MetaQA 实验：前者报告哪些跳数和指标，后者的 Wiki-Movies、Freebase 与 1000 个样本分别是什么角色？

**参考答案：** KG-GPT 报告 MetaQA 1-hop、2-hop、3-hop 的 Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是迁移前训练来源，1000 个样本取自 MetaQA-3hop 训练划分。

**逐项判分：**

- `R11.C01`：KG-GPT 报告 MetaQA 1/2/3-hop。（来源：kggptds）
- `R11.C02`：上述 MetaQA 指标为 Hits@1。（来源：kggptds）
- `R11.C03`：RoG 的 MetaQA-3hop 基于 Wiki-Movies。（来源：rogmeta）
- `R11.C04`：Freebase 是迁移前训练来源，不能写成该测试 KG。（来源：rogmeta）
- `R11.C05`：1000 个样本来自训练划分，而非测试样本数。（来源：rogmeta）

**考查关系：** DERIVES_TRAINING_DATA_FROM, EVALUATED_ON, REPORTS_METRIC, USES_DATASET, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE, USES_TRAINING_SIGNAL

**错误边界：** 不能把 Freebase 写成 RoG MetaQA 测试 KG，也不以协议不一致的数字直接排名。

- 参考路径 `kggptds.P01`：KG-GPT —EVALUATED_ON→ FACTKG
- 参考路径 `kggptds.P02`：KG-GPT —EVALUATED_ON→ MetaQA
- 参考路径 `kggptds.P03`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 1-hop
- 参考路径 `kggptds.P04`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 2-hop
- 参考路径 `kggptds.P05`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 3-hop
- 参考路径 `kggptds.P06`：KG-GPT MetaQA evaluation —REPORTS_METRIC→ Hits@1
- 参考路径 `kggptds.P07`：KG-GPT —USES_EVALUATION_SETTING→ KG-GPT MetaQA evaluation

**完整来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 页 4—4；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；块 `chunk_3f7eb65828761447433c66c28ad111a4`。

字符位置：`[{"pdf_page": 4, "start_char": 57, "end_char": 1493, "chunk_start_char": 0, "chunk_end_char": 1436, "block_bboxes": [[143.353, 97.415, 274.997, 143.495], [76.209, 164.205, 132.263, 173.955], [146.652, 146.04, 274.997, 180.181], [149.091, 158.232, 274.997, 192.29], [70.557, 205.158, 290.877, 239.106], [75.442, 254.684, 284.569, 273.404], [85.336, 296.402, 96.475, 304.752], [78.31, 275.807, 276.34, 367.731], [70.119, 390.658, 289.494, 424.606], [70.866, 449.144, 289.139, 487.235], [70.593, 490.24, 290.949, 650.24], [70.866, 663.055, 136.004, 673.964]]}]`

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

- 参考路径 `rogmeta.P01`：RoG —EVALUATED_ON→ MetaQA-3hop —USES_KNOWLEDGE_BASE→ Wiki-Movies
- 参考路径 `rogmeta.P02`：RoG —DERIVES_TRAINING_DATA_FROM→ Freebase
- 参考路径 `rogmeta.P03`：RoG —USES_TRAINING_SIGNAL→ 1000 MetaQA-3hop training samples
- 参考路径 `rogmeta.P04`：RoG transfer experiment —USES_KNOWLEDGE_BASE→ Freebase to Wiki-Movies transfer
- 参考路径 `rogmeta.P05`：RoG —USES_EVALUATION_SETTING→ RoG transfer experiment

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 20—20；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_f5c88d605f651f26c093f30b836a98aa`。

字符位置：`[{"pdf_page": 20, "start_char": 348, "end_char": 1306, "chunk_start_char": 0, "chunk_end_char": 958, "block_bboxes": [[108.249, 283.751, 292.912, 293.714], [108.0, 304.529, 504.003, 380.755], [108.0, 387.729, 504.003, 419.609]]}]`

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

### R12 · 知识来源与逻辑题型 · cross

MusicBrainz-x-Wikidata 和 CLQA-Wiki 各从哪些知识来源构建，分别强调跨 KG 还是哪些逻辑题型？它们是否可当作同一基准？

**参考答案：** MusicBrainz-x-Wikidata 的 109 题需要结合 MusicBrainz 和 Wikidata；CLQA-Wiki 来自 Wikidata 子集，覆盖多跳、比较、交和并。出现相同知识库名称不表示同一基准。

**逐项判分：**

- `R12.C01`：MusicBrainz-x-Wikidata 需结合 MusicBrainz 与 Wikidata。（来源：totmusic）
- `R12.C02`：该数据集包含 109 题。（来源：totmusic）
- `R12.C03`：CLQA-Wiki 来自 Wikidata 子集。（来源：lpbench）
- `R12.C04`：题型包括多跳、比较、交、并。（来源：lpbench）
- `R12.C05`：共享 Wikidata 名称不能推出两个基准相同。（来源：totmusic, lpbench）

**考查关系：** DERIVED_FROM, EVALUATED_ON, HAS_QUESTION_TYPE, HAS_TASK, USES_KNOWLEDGE_BASE

**错误边界：** 都出现 Wikidata 不表示同一数据集或相同题型。

- 参考路径 `totmusic.P01`：Tree-of-Traversals —EVALUATED_ON→ MusicBrainz-x-Wikidata —USES_KNOWLEDGE_BASE→ MusicBrainz
- 参考路径 `totmusic.P02`：MusicBrainz-x-Wikidata —USES_KNOWLEDGE_BASE→ Wikidata
- 参考路径 `totmusic.P03`：MusicBrainz-x-Wikidata —HAS_TASK→ 109 cross-KG questions

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 5—6；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_f4962498025654850621ee329d0af7d6`。

字符位置：`[{"pdf_page": 5, "start_char": 3325, "end_char": 4344, "chunk_start_char": 0, "chunk_end_char": 1019, "block_bboxes": [[305.804, 480.537, 526.318, 749.037], [318.794, 762.682, 489.559, 772.731]]}, {"pdf_page": 6, "start_char": 0, "end_char": 314, "chunk_start_char": 1020, "chunk_end_char": 1334, "block_bboxes": [[302.451, 75.747, 392.265, 87.05], [140.608, 95.172, 446.717, 106.081], [146.585, 114.421, 448.688, 192.976], [316.605, 201.022, 378.111, 212.325], [140.608, 220.447, 446.717, 231.356]]}]`

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

- 参考路径 `lpbench.P01`：CLQA-Wiki —DERIVED_FROM→ Wikidata subset
- 参考路径 `lpbench.P02`：CLQA-Wiki —HAS_QUESTION_TYPE→ multi-hop
- 参考路径 `lpbench.P03`：CLQA-Wiki —HAS_QUESTION_TYPE→ comparison
- 参考路径 `lpbench.P04`：CLQA-Wiki —HAS_QUESTION_TYPE→ intersection
- 参考路径 `lpbench.P05`：CLQA-Wiki —HAS_QUESTION_TYPE→ union

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 2—2；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_ab66789d9bc91de68948962d6c3f0011`。

字符位置：`[{"pdf_page": 2, "start_char": 1158, "end_char": 2387, "chunk_start_char": 0, "chunk_end_char": 1229, "block_bboxes": [[70.473, 416.616, 290.949, 603.847], [70.506, 615.603, 290.949, 775.47], [306.142, 72.649, 399.883, 84.604]]}]`

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

### R13 · 父子数据集与检索语料 · cross

HippoRAG 的 HotpotQA 设置与 ToG-2 的 AdvHotpotQA 设置怎样关联？请区分父子数据集、抽样方式与检索知识来源。

**参考答案：** AdvHotpotQA 是 HotpotQA 的挑战子集。HippoRAG 每个验证集取 1000 题，并用对应支持与干扰段落构建检索语料；ToG-2 使用完整 Wikipedia 和 Wikidata。不能直接当作相同检索协议。

**逐项判分：**

- `R13.C01`：AdvHotpotQA 是 HotpotQA 的挑战子集。（来源：tog2ds）
- `R13.C02`：HippoRAG 每个验证集取 1000 题。（来源：hippods）
- `R13.C03`：HippoRAG 用所选问题的支持与干扰段落构成检索语料。（来源：hippods）
- `R13.C04`：ToG-2 使用完整 Wikipedia 和 Wikidata。（来源：tog2ds）
- `R13.C05`：父集/子集关系不等于同一检索协议。（来源：hippods, tog2ds）

**考查关系：** DERIVED_FROM, EVALUATED_ON, HAS_SAMPLE_SETTING, REPORTS_METRIC, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE

**错误边界：** 不能把父集与挑战子集视为相同测试协议。

- 参考路径 `hippods.P01`：HippoRAG —EVALUATED_ON→ MuSiQue (answerable)
- 参考路径 `hippods.P02`：HippoRAG —EVALUATED_ON→ 2WikiMultiHopQA
- 参考路径 `hippods.P03`：HippoRAG —EVALUATED_ON→ HotpotQA
- 参考路径 `hippods.P04`：HippoRAG retrieval corpus —HAS_SAMPLE_SETTING→ 1000 validation questions per dataset
- 参考路径 `hippods.P05`：HippoRAG retrieval corpus —USES_KNOWLEDGE_BASE→ supporting and distractor passages
- 参考路径 `hippods.P06`：HippoRAG —USES_EVALUATION_SETTING→ HippoRAG retrieval corpus

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 5—5；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_3fa28005a4df0de5249826585cf9d713`。

字符位置：`[{"pdf_page": 5, "start_char": 2205, "end_char": 3400, "chunk_start_char": 0, "chunk_end_char": 1195, "block_bboxes": [[107.532, 383.68, 505.653, 470.063], [119.512, 481.129, 492.488, 491.322], [314.205, 502.845, 447.078, 511.811], [162.683, 517.888, 447.078, 577.187], [108.0, 592.604, 169.718, 602.566]]}]`

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

- 参考路径 `tog2ds.P01`：ToG-2 —EVALUATED_ON→ WebQSP
- 参考路径 `tog2ds.P02`：ToG-2 —EVALUATED_ON→ QALD10-en
- 参考路径 `tog2ds.P03`：ToG-2 —EVALUATED_ON→ AdvHotpotQA
- 参考路径 `tog2ds.P04`：ToG-2 —EVALUATED_ON→ FEVER
- 参考路径 `tog2ds.P05`：ToG-2 —EVALUATED_ON→ Creak
- 参考路径 `tog2ds.P06`：AdvHotpotQA —DERIVED_FROM→ HotpotQA
- 参考路径 `tog2ds.P07`：ToG-2 evaluation —USES_KNOWLEDGE_BASE→ full Wikipedia and Wikidata
- 参考路径 `tog2ds.P08`：ToG-2 evaluation —REPORTS_METRIC→ Accuracy on FEVER and Creak
- 参考路径 `tog2ds.P09`：ToG-2 evaluation —REPORTS_METRIC→ EM on other datasets
- 参考路径 `tog2ds.P10`：ToG-2 —USES_EVALUATION_SETTING→ ToG-2 evaluation

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 6—6；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

字符位置：`[{"pdf_page": 6, "start_char": 1827, "end_char": 2910, "chunk_start_char": 0, "chunk_end_char": 1083, "block_bboxes": [[108.299, 418.062, 200.083, 430.017], [108.249, 442.645, 239.271, 452.608], [108.0, 463.168, 504.003, 582.72]]}]`

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

### R14 · 指标与实验条件 · cross

对于共同出现的 Creak，ToG 与 ToG-2 分别怎样表述评价指标？ToG-2 明确写了什么知识来源，为什么仅凭指标名称不能给两者排名？

**参考答案：** ToG 原文将所有数据集指标表述为 exact match accuracy（Hits@1）；ToG-2 对 Creak 使用 Accuracy（Acc.），并使用完整 Wikipedia/Wikidata。指标名称相近不能代替划分、底座、提示和知识来源的协议核对。

**逐项判分：**

- `R14.C01`：ToG 原文指标表述为 exact match accuracy（Hits@1）。（来源：togds）
- `R14.C02`：ToG-2 对 Creak 使用 Accuracy（Acc.）。（来源：tog2ds）
- `R14.C03`：ToG-2 使用完整 Wikipedia 和 Wikidata。（来源：tog2ds）
- `R14.C04`：还需核对划分、底座、提示和知识来源，不能据名称直接排名。（来源：togds, tog2ds）

**考查关系：** DERIVED_FROM, EVALUATED_ON, REPORTS_METRIC, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE

**错误边界：** 指标名称相近不等于受控比较；未提供的 ToG 条件不能补写。

- 参考路径 `togds.P01`：ToG —EVALUATED_ON→ WebQSP
- 参考路径 `togds.P02`：ToG —EVALUATED_ON→ QALD10-en
- 参考路径 `togds.P03`：ToG —EVALUATED_ON→ Creak
- 参考路径 `togds.P04`：ToG —REPORTS_METRIC→ exact match accuracy (Hits@1)

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 5—5；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_deb9eea46e529705dffdd1103729c44c`。

字符位置：`[{"pdf_page": 5, "start_char": 2914, "end_char": 4358, "chunk_start_char": 0, "chunk_end_char": 1444, "block_bboxes": [[108.299, 482.573, 200.083, 494.529], [108.249, 507.855, 235.26, 517.818], [108.249, 528.452, 305.88, 538.415], [107.671, 547.628, 504.824, 656.296], [108.249, 670.178, 310.993, 680.141], [107.532, 689.505, 505.652, 732.293], [303.509, 752.194, 308.49, 762.157]]}]`

```text
EXPERIMENTS
3.1
EXPERIMENTAL DESIGN
3.1.1
DATASETS AND EVALUATION METRICS
In order to test ToG’s ability on multi-hop knowledge-intensive reasoning tasks, we evaluate ToG
on five KBQA datasets (4 Multi-hop and 1 Single-hop): CWQ (Talmor & Berant, 2018), WebQSP
(Yih et al., 2016), GrailQA (Gu et al., 2021), QALD10-en (Perevalov et al., 2022), Simple Questions
(Bordes et al., 2015). Moreover, in order to examine ToG on more generic tasks, we also prepare
one open-domain QA dataset: WebQuestions (Berant et al., 2013); two slot filling datasets: T-REx
(ElSahar et al., 2018) and Zero-Shot RE (Petroni et al., 2021); and one fact-checking dataset: Creak
(Onoe et al., 2021). Note that, for two big datasets GrailQA and Simple Questions, we only randomly
selected 1,000 samples each for testing in order to save computational cost. For all datasets, exact
match accuracy (Hits@1) is used as our evaluation metric following previous works (Li et al., 2023c;
Baek et al., 2023b; Jiang et al., 2023; Li et al., 2023a).
3.1.2
METHODS SELECTED FOR COMPARISON
We compare with standard prompting (IO prompt) (Brown et al., 2020b), Chain-of-Thought prompting
(CoT prompt) (Wei et al., 2022), and Self-Consistency (Wang et al., 2023c) with 6 in-context
exemplars and "step-by-step" reasoning chains. Moreover, for each dataset, we pick previous state-of-
the-art (SOTA) works for comparison. We notice that fine-tuning methods trained specifically on
5
```

- 参考路径 `tog2ds.P01`：ToG-2 —EVALUATED_ON→ WebQSP
- 参考路径 `tog2ds.P02`：ToG-2 —EVALUATED_ON→ QALD10-en
- 参考路径 `tog2ds.P03`：ToG-2 —EVALUATED_ON→ AdvHotpotQA
- 参考路径 `tog2ds.P04`：ToG-2 —EVALUATED_ON→ FEVER
- 参考路径 `tog2ds.P05`：ToG-2 —EVALUATED_ON→ Creak
- 参考路径 `tog2ds.P06`：AdvHotpotQA —DERIVED_FROM→ HotpotQA
- 参考路径 `tog2ds.P07`：ToG-2 evaluation —USES_KNOWLEDGE_BASE→ full Wikipedia and Wikidata
- 参考路径 `tog2ds.P08`：ToG-2 evaluation —REPORTS_METRIC→ Accuracy on FEVER and Creak
- 参考路径 `tog2ds.P09`：ToG-2 evaluation —REPORTS_METRIC→ EM on other datasets
- 参考路径 `tog2ds.P10`：ToG-2 —USES_EVALUATION_SETTING→ ToG-2 evaluation

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 6—6；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

字符位置：`[{"pdf_page": 6, "start_char": 1827, "end_char": 2910, "chunk_start_char": 0, "chunk_end_char": 1083, "block_bboxes": [[108.299, 418.062, 200.083, 430.017], [108.249, 442.645, 239.271, 452.608], [108.0, 463.168, 504.003, 582.72]]}]`

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

### R15 · 继续检索与证据充分信号 · cross

Tree-of-Traversals 的搜索停止机制与 CuriousLLM 的追问/证据充分信号有什么区别？请说明预算耗尽为什么不能等同于证据充分。

**参考答案：** Tree-of-Traversals 可因答案节点超过阈值而停止，也可受 max depth/max expansions 限制，二者分别强制 done 和返回 Cannot find answer；CuriousLLM 生成追问查缺或用特殊 token 表示证据充分。预算耗尽不等于充分或正确。

**逐项判分：**

- `R15.C01`：答案阈值停止与预算终止含义不同。（来源：totbound）
- `R15.C02`：max depth 强制 done，max expansions 返回 Cannot find answer。（来源：totbound）
- `R15.C03`：CuriousLLM 生成追问或输出证据充分特殊 token。（来源：curious）
- `R15.C04`：预算耗尽不能等同于证据充分或答案正确。（来源：totbound, curious）

**考查关系：** BOUNDED_BY, CONNECTS, ENHANCES, GENERATES, HAS_STOP_CONDITION, HAS_TARGET, RETURNS, USES_INPUT

**错误边界：** 预算上限/强制 done 不等于答案正确，也不能把 token 当作本项目的运行时停止器。

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

### R16 · 知识融合与可解释性 · cross

MindMap 与 RoG 分别怎样利用知识构造推理？请区分隐式知识、外部 KG、mind map 和关系路径计划，并说明可解释性结论的边界。

**参考答案：** MindMap 融合 LLM 隐式知识与外部 KG，展示 mind map 推理路径；RoG 先规划由 KG 约束的关系路径，再检索有效推理路径。路径可解释仍需核查结论与证据，不能保证每个回答都正确。

**逐项判分：**

- `R16.C01`：MindMap 融合 LLM 隐式知识与外部 KG。（来源：mind）
- `R16.C02`：mind map 用于呈现推理路径。（来源：mind）
- `R16.C03`：RoG 以关系路径计划指导有效推理路径检索。（来源：rog）
- `R16.C04`：可解释路径不自动保证答案正确。（来源：mind, rog）

**考查关系：** CONNECTS, HAS_STAGE, RETRIEVES_FROM, TARGETS_TASK, TRAINED_WITH, USES_COMPONENT

**错误边界：** 可解释性不等于所有结论都通过事实验证。

- 参考路径 `mind.P01`：MindMap —USES_COMPONENT→ LLM implicit knowledge
- 参考路径 `mind.P02`：MindMap —RETRIEVES_FROM→ external knowledge graph
- 参考路径 `mind.P03`：MindMap —USES_COMPONENT→ mind map reasoning path
- 参考路径 `mind.P04`：MindMap —TARGETS_TASK→ medical question answering

**完整来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 页 1—1；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；块 `chunk_2f4809d54362f998c1c0710e915a721b`。

字符位置：`[{"pdf_page": 1, "start_char": 295, "end_char": 1548, "chunk_start_char": 0, "chunk_end_char": 1253, "block_bboxes": [[157.758, 205.394, 367.277, 233.646], [87.516, 243.186, 273.781, 575.915], [70.866, 586.177, 153.68, 598.132]]}]`

```text
Abstract
Large language models (LLMs) have achieved
remarkable performance in natural language
understanding and generation tasks. However,
they often suffer from limitations such as diffi-
culty in incorporating new knowledge, gener-
ating hallucinations, and explaining their rea-
soning process. To address these challenges,
we propose a novel prompting pipeline, named
MindMap, that leverages knowledge graphs
(KGs) to enhance LLMs’ inference and trans-
parency. Our method enables LLMs to com-
prehend KG inputs and infer with a combina-
tion of implicit and external knowledge. More-
over, our method elicits the mind map of LLMs,
which reveals their reasoning pathways based
on the ontology of knowledge. We evaluate our
method on diverse question & answering tasks,
especially in medical domains, and show sig-
nificant improvements over baselines. We also
introduce a new hallucination evaluation bench-
mark and analyze the effects of different com-
ponents of our method. Our results demonstrate
the effectiveness and robustness of our method
in merging knowledge from LLMs and KGs for
combined inference. To reproduce our results
and extend the framework further, we make our
codebase available at https://github.com/wyl-
willing/MindMap.
1
```

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R17 · 领域重叠与评测关系 · cross

STaRK 和 MindMap 在医学领域分别是什么类型的工作？这些领域信息能否建立 MindMap 在 STaRK 上的评测关系并支持一个分数？

**参考答案：** STaRK 是包含精准医疗检索的基准，也覆盖产品和论文搜索；MindMap 是包含医学 QA 场景的知识图提示方法。给定原文不能建立 MindMap 在 STaRK 上评测的关系或分数，应说明证据不足。

**逐项判分：**

- `R17.C01`：STaRK 是检索基准，覆盖精准医疗、产品搜索和论文搜索。（来源：stark）
- `R17.C02`：MindMap 是在医学 QA 等任务中评估的 KG prompting 方法。（来源：mind）
- `R17.C03`：领域重叠不能建立 MindMap 在 STaRK 上的评测边或分数。（来源：stark, mind）

**考查关系：** HAS_TASK, RETRIEVES_FROM, TARGETS_TASK, USES_COMPONENT

**错误边界：** 证据不足不能写成“证明从未评测”，也不能捏造分数。

- 参考路径 `stark.P01`：STaRK —HAS_TASK→ product search
- 参考路径 `stark.P02`：STaRK —HAS_TASK→ academic paper search
- 参考路径 `stark.P03`：STaRK —HAS_TASK→ precision medicine retrieval

**完整来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 页 1—1；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；块 `chunk_6b5383484693f6226010eab8143f80d6`。

字符位置：`[{"pdf_page": 1, "start_char": 324, "end_char": 2018, "chunk_start_char": 0, "chunk_end_char": 1694, "block_bboxes": [[283.758, 245.19, 328.243, 257.145], [143.866, 269.807, 469.789, 454.391], [205.19, 610.031, 248.703, 620.969], [211.6, 599.33, 240.929, 607.533], [216.449, 585.557, 238.006, 593.76], [385.922, 619.315, 478.763, 627.518], [437.928, 589.928, 443.83, 596.764], [144.476, 619.045, 160.888, 627.248], [352.298, 589.067, 382.359, 597.271], [260.676, 563.411, 293.347, 571.614], [283.166, 474.459, 315.256, 485.396], [302.055, 504.115, 386.419, 520.044], [298.079, 528.776, 350.265, 544.62], [370.448, 534.987, 376.35, 541.823], [401.047, 502.427, 449.478, 514.664], [373.918, 519.121, 381.0, 527.324], [161.972, 549.841, 211.15, 564.335], [164.844, 565.505, 209.149, 570.006], [177.292, 570.096, 195.824, 574.597], [324.724, 518.31, 331.806, 526.514], [263.612, 620.935, 339.71, 629.138], [354.51, 529.231, 392.389, 541.536]]}]`

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

- 参考路径 `mind.P01`：MindMap —USES_COMPONENT→ LLM implicit knowledge
- 参考路径 `mind.P02`：MindMap —RETRIEVES_FROM→ external knowledge graph
- 参考路径 `mind.P03`：MindMap —USES_COMPONENT→ mind map reasoning path
- 参考路径 `mind.P04`：MindMap —TARGETS_TASK→ medical question answering

**完整来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 页 1—1；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；块 `chunk_2f4809d54362f998c1c0710e915a721b`。

字符位置：`[{"pdf_page": 1, "start_char": 295, "end_char": 1548, "chunk_start_char": 0, "chunk_end_char": 1253, "block_bboxes": [[157.758, 205.394, 367.277, 233.646], [87.516, 243.186, 273.781, 575.915], [70.866, 586.177, 153.68, 598.132]]}]`

```text
Abstract
Large language models (LLMs) have achieved
remarkable performance in natural language
understanding and generation tasks. However,
they often suffer from limitations such as diffi-
culty in incorporating new knowledge, gener-
ating hallucinations, and explaining their rea-
soning process. To address these challenges,
we propose a novel prompting pipeline, named
MindMap, that leverages knowledge graphs
(KGs) to enhance LLMs’ inference and trans-
parency. Our method enables LLMs to com-
prehend KG inputs and infer with a combina-
tion of implicit and external knowledge. More-
over, our method elicits the mind map of LLMs,
which reveals their reasoning pathways based
on the ontology of knowledge. We evaluate our
method on diverse question & answering tasks,
especially in medical domains, and show sig-
nificant improvements over baselines. We also
introduce a new hallucination evaluation bench-
mark and analyze the effects of different com-
ponents of our method. Our results demonstrate
the effectiveness and robustness of our method
in merging knowledge from LLMs and KGs for
combined inference. To reproduce our results
and extend the framework further, we make our
codebase available at https://github.com/wyl-
willing/MindMap.
1
```

### R18 · 跨方法阶段对齐 · cross

把 KG-GPT 与 RoG 从问题处理到推理的步骤分别排好：句子分割属于谁，关系路径规划属于谁，检索对象又是什么？

**参考答案：** KG-GPT 为句子分割→图检索→推理，检索相关图组件；RoG 为规划→检索→推理，先生成 KG 约束的关系路径计划，再检索有效推理路径。

**逐项判分：**

- `R18.C01`：KG-GPT 顺序为句子分割、图检索、推理。（来源：kggpt）
- `R18.C02`：KG-GPT 检索相关图组件。（来源：kggpt）
- `R18.C03`：RoG 顺序为规划、检索、推理。（来源：rog）
- `R18.C04`：RoG 用关系路径计划检索有效推理路径。（来源：rog）

**考查关系：** CONNECTS, HAS_STAGE, PRECEDES, TRAINED_WITH

**错误边界：** 共有“检索/推理”步骤不代表流程相同或存在继承。

- 参考路径 `kggpt.P01`：KG-GPT —HAS_STAGE→ Sentence Segmentation —PRECEDES→ Graph Retrieval —PRECEDES→ Inference

**完整来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 页 1—1；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；块 `chunk_61e96cb10e247f7d002b4163920cc737`。

字符位置：`[{"pdf_page": 1, "start_char": 237, "end_char": 1173, "chunk_start_char": 0, "chunk_end_char": 936, "block_bboxes": [[157.758, 214.382, 202.243, 226.337], [87.516, 240.528, 273.87, 489.67], [70.866, 504.681, 153.68, 516.636]]}]`

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

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R19 · 三种多跳机制 · cross

ToG、HippoRAG、RoG 都能连接多跳知识，但各自依靠什么核心操作？请给每个方法对应一个机制，并避免把共同目标当成相同算法。

**参考答案：** ToG 由 LLM 代理迭代束搜索；HippoRAG 以查询概念驱动 PPR 整合跨段落信息；RoG 先规划关系路径再检索有效推理路径。共同处理多跳不表示相同算法或成本。

**逐项判分：**

- `R19.C01`：ToG 对应 LLM 代理与迭代束搜索。（来源：tog）
- `R19.C02`：HippoRAG 对应查询种子驱动的 PPR。（来源：hippo）
- `R19.C03`：RoG 对应关系路径计划及路径检索。（来源：rog）
- `R19.C04`：多跳目标相同不能推出算法或计算成本相同。（来源：tog, hippo, rog）

**考查关系：** CONNECTS, HAS_STAGE, RETRIEVES_FROM, TRAINED_WITH, USES_AGENT, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 共同处理多跳不表示使用相同图操作或计算成本。

- 参考路径 `tog.P01`：ToG —USES_AGENT→ LLM agent
- 参考路径 `tog.P02`：ToG —USES_ALGORITHM→ iterative beam search —RETRIEVES_FROM→ knowledge graph
- 参考路径 `tog.P03`：iterative beam search —CONNECTS→ entity and relation paths

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 1—1；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_e09b5a88c34014513aad6c0d6121f790`。

字符位置：`[{"pdf_page": 1, "start_char": 517, "end_char": 2163, "chunk_start_char": 0, "chunk_end_char": 1646, "block_bboxes": [[278.288, 276.647, 333.722, 288.602], [143.507, 303.075, 469.793, 532.166], [108.299, 556.334, 205.989, 568.289]]}]`

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

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 3—4；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_d6a1257a27b9a4e3fd151b8c87ebf491`。

字符位置：`[{"pdf_page": 3, "start_char": 2828, "end_char": 3753, "chunk_start_char": 0, "chunk_end_char": 925, "block_bboxes": [[107.691, 575.993, 504.005, 641.11], [108.249, 658.672, 211.179, 668.635], [108.249, 680.202, 293.39, 690.165], [108.0, 700.313, 504.002, 732.268], [303.509, 752.194, 308.49, 762.157]]}, {"pdf_page": 4, "start_char": 0, "end_char": 487, "chunk_start_char": 926, "chunk_end_char": 1413, "block_bboxes": [[108.0, 27.813, 293.095, 37.776], [108.0, 80.423, 232.161, 94.255], [108.0, 82.759, 503.999, 105.19], [108.249, 122.764, 201.665, 132.727], [107.641, 143.134, 504.002, 165.406], [121.495, 154.164, 146.392, 167.216], [141.966, 154.164, 166.242, 167.346], [162.093, 153.426, 199.6, 167.216], [182.67, 154.164, 243.19, 168.665], [239.041, 154.164, 280.776, 168.123], [276.627, 154.164, 444.946, 168.123], [108.0, 155.598, 504.003, 179.71], [213.519, 168.214, 238.417, 181.266], [233.991, 168.214, 258.266, 181.397], [254.117, 168.214, 313.207, 181.266], [298.969, 167.568, 337.139, 181.919], [322.624, 168.214, 360.938, 182.233]]}]`

```text
ToG implements the “LLM ⊗KG” paradigm by asking LLM to perform beam search on knowledge
graph. Specifically, it prompts the LLM to iteratively explore multiple possible reasoning paths on
KGs until the LLM determines that the question can be answered based on the current reasoning
paths. ToG constantly updates and maintains top-N reasoning paths P = {p1, p2, . . . , pN} for the
question x after each iteration, where N denotes the width of beam search. The entire inference
process of ToG contains the following 3 phases: initialization, exploration, and reasoning.
2.1
THINK-ON-GRAPH
2.1.1
INITIALIZATION OF GRAPH SEARCH
Given a question, ToG leverages the underlying LLM to localize the initial entity of the reasoning
paths on knowledge graph. This phase can be regarded as the initialization of the top-N reasoning
paths P. ToG first prompts LLMs to automatically extract the topic entities in question and gets the
3

Published as a conference paper at ICLR 2024
top-N topic entities E0 = {e0
1, e0
2, ..., e0
N} to the question. Note that the number of topic entities
might possibly be less than N.
2.1.2
EXPLORATION
At the beginning of the D-th iteration, each path pn consists of D −1 triples, i.e., pn =
{(ed
s,n, rd
j,n, ed
o,n)}D−1
d=1 , where ed
s,n and ed
o,n denote subject and object entities, rd
j,n is a specific
relation between them, (ed
s,n, rd
j,n, ed
o,n) and (ed+1
s,n , rd+1
j,n , ed+1
```

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R20 · 三种图与文档连接 · cross

ToG-2、HippoRAG、KGP 怎样把图与文档/段落证据联系起来？请分别给出图的来源或连接方式，以及取得证据的操作。

**参考答案：** ToG-2 通过实体连接文档并协作检索图与上下文；HippoRAG 从语料转出无模式 KG，用查询种子驱动 PPR 跨段落检索；KGP 用段落/文档结构节点和相似/结构边，由代理收集支持段落。

**逐项判分：**

- `R20.C01`：ToG-2 用实体连接文档并交替检索图和上下文。（来源：tog2）
- `R20.C02`：HippoRAG 从语料构建无模式 KG，以 PPR 跨段落检索。（来源：hippo）
- `R20.C03`：KGP 以段落/文档结构为节点，以相似/结构关系为边。（来源：kgp）
- `R20.C04`：KGP 通过图遍历代理收集段落。（来源：kgp）

**考查关系：** ALTERNATES, COLLECTS, CONNECTS, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, USES_AGENT, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 三者节点、边和检索过程不可混为同一种表示。

- 参考路径 `tog2.P01`：ToG-2 —CONNECTS→ entities linked to documents
- 参考路径 `tog2.P02`：ToG-2 —ALTERNATES→ graph retrieval
- 参考路径 `tog2.P03`：ToG-2 —ALTERNATES→ context retrieval
- 参考路径 `tog2.P04`：graph retrieval —CONNECTS→ context retrieval

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 1—1；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_9b63637ef18ed2d67ff105ef55092df3`。

字符位置：`[{"pdf_page": 1, "start_char": 621, "end_char": 2250, "chunk_start_char": 0, "chunk_end_char": 1629, "block_bboxes": [[143.866, 279.608, 468.139, 530.667]]}]`

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

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 3—3；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_c9284a24e2b28b371a7e43a2bc6ae3c2`。

字符位置：`[{"pdf_page": 3, "start_char": 223, "end_char": 1439, "chunk_start_char": 0, "chunk_end_char": 1216, "block_bboxes": [[108.0, 112.073, 504.003, 253.634], [108.299, 272.586, 217.097, 284.541]]}]`

```text
The advantage of ToG-2 can be summarized as: (1) In-depth retrieval: ToG-2 achieves in-depth
and reliable context retrieval through the guide of KGs and performs precise graph retrieval by
treating documents as node contexts, achieving a tight-coupling combination of KG and text RAG,
enabling deep and comprehensive retrieval processes. (2) Faithful reasoning: ToG-2 iteratively
performs a collaborative retrieval process based on KG and text, using retrieved heterogeneous
knowledge as the basis for LLM reasoning and enhancing the faithfulness of LLM-generated con-
tent (3) Efficiency and Effectiveness: a) ToG-2 is a training-free and plug-and-play framework that
can be applied to various LLMs; b) ToG-2 can be executed between any associated KG and docu-
ment database, while for purely document database, entities can be extracted from the documents
first, and then a graph can be constructed through relation extraction or entity co-occurrence (Edge
et al., 2024); c) ToG-2 achieves new SOTA performances on various complex knowledge reasoning
datasets and can elevate the reasoning capabilities of smaller LLMs, e.g., Llama2-13B to a level
comparable to direct reasoning with powerful LLMs like GPT-3.5.
2
```

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

### R21 · 三种资源与缺口控制 · cross

G-Retriever、Tree-of-Traversals、CuriousLLM 分别怎样处理上下文过大、搜索空间过大和证据缺口？这些机制是否足以给出统一速度排名？

**参考答案：** G-Retriever 选择相关子图控制大图上下文；Tree-of-Traversals 限制搜索深度和扩展数；CuriousLLM 用追问查缺或用特殊 token 表示证据充分。不同控制对象不能代替相同条件下的速度实测。

**逐项判分：**

- `R21.C01`：G-Retriever 通过选择相关子图处理上下文容量问题。（来源：grscale）
- `R21.C02`：Tree-of-Traversals 使用深度和扩展数搜索边界。（来源：totbound）
- `R21.C03`：CuriousLLM 用追问或特殊 token 处理证据缺口。（来源：curious）
- `R21.C04`：不同控制对象不能直接推出统一速度或 Token 排名。（来源：grscale, totbound, curious）

**考查关系：** BOUNDED_BY, CONNECTS, ENHANCES, FORMULATES_AS, GENERATES, HAS_STOP_CONDITION, HAS_TARGET, RETURNS, SELECTS, USES_INPUT

**错误边界：** 不能从机制差异直接推出统一条件下速度或 Token 优势。

- 参考路径 `grscale.P01`：G-Retriever —FORMULATES_AS→ Prize-Collecting Steiner Tree —SELECTS→ relevant subgraph —CONNECTS→ bounded LLM context

**完整来源：** G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering；PDF 页 2—3；`Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf`；块 `chunk_5c9e14854565607ec53c355da481c451`。

字符位置：`[{"pdf_page": 2, "start_char": 5377, "end_char": 6545, "chunk_start_char": 0, "chunk_end_char": 1168, "block_bboxes": [[108.0, 586.878, 505.247, 673.291], [107.671, 679.55, 504.666, 722.414], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 3, "start_char": 0, "end_char": 302, "chunk_start_char": 1169, "chunk_end_char": 1471, "block_bboxes": [[168.567, 79.054, 443.126, 89.017], [115.77, 114.927, 128.937, 121.901], [249.671, 108.103, 269.888, 112.519], [254.373, 133.834, 265.179, 138.25], [253.452, 120.655, 299.773, 127.581], [276.078, 115.32, 279.876, 119.736], [275.608, 135.402, 324.86, 141.388], [307.236, 120.968, 330.932, 125.385], [309.393, 108.103, 327.516, 112.519], [240.86, 148.186, 489.169, 163.13], [115.77, 201.212, 202.238, 208.186]]}]`

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

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

### R22 · 三种训练信号与推理用途 · cross

LPKG、CuriousLLM、RoG 分别学习什么，训练出的能力在问答时怎样使用？请区分规划数据、追问监督与 KG 知识蒸馏。

**参考答案：** LPKG 用 KG 派生 planning data 微调规划能力；CuriousLLM 用问题和证据监督后续问题，指导查缺检索；RoG 从 KG 蒸馏知识，并在推理时生成关系计划、检索有效路径。不能互换训练目标。

**逐项判分：**

- `R22.C01`：LPKG 用 KG 派生规划数据提升复杂问答规划能力。（来源：lpdata）
- `R22.C02`：CuriousLLM 以问题/证据为输入，学习后续问题以指导检索。（来源：curious）
- `R22.C03`：RoG 通过 KG 知识蒸馏训练。（来源：rog）
- `R22.C04`：RoG 推理时做关系计划与有效路径检索。（来源：rog）

**考查关系：** CONNECTS, DERIVES_TRAINING_DATA_FROM, ENHANCES, GENERATES, HAS_STAGE, HAS_TARGET, TRAINED_WITH, USES_INPUT, USES_TRAINING_SIGNAL

**错误边界：** 不能互换监督目标或臆测训练数据完全相同。

- 参考路径 `lpdata.P01`：LPKG —DERIVES_TRAINING_DATA_FROM→ knowledge graph
- 参考路径 `lpdata.P02`：LPKG —USES_TRAINING_SIGNAL→ planning data —CONNECTS→ small model fine-tuning
- 参考路径 `lpdata.P03`：LPKG —HAS_STAGE→ complex QA planning

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 1—1；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_e07b345ba2a42d01f295e47f196061d5`。

字符位置：`[{"pdf_page": 1, "start_char": 576, "end_char": 1608, "chunk_start_char": 0, "chunk_end_char": 1032, "block_bboxes": [[157.758, 205.751, 384.313, 233.647], [87.516, 247.152, 273.866, 520.203], [70.866, 534.529, 153.68, 546.484]]}]`

```text
Abstract
Improving the performance of large language
models (LLMs) in complex question-answering
(QA) scenarios has always been a research fo-
cal point. Recent studies have attempted to en-
hance LLMs’ performance by combining step-
wise planning with external retrieval. While
effective for advanced models like GPT-3.5,
smaller LLMs face challenges in decomposing
complex questions, necessitating supervised
fine-tuning. Previous work has relied on man-
ual annotation and knowledge distillation from
teacher LLMs, which are time-consuming and
not accurate enough. In this paper, we intro-
duce a novel framework for enhancing LLMs’
planning capabilities by using planning data
derived from knowledge graphs (KGs). LLMs
fine-tuned with this data have improved plan-
ning capabilities, better equipping them to han-
dle complex QA tasks that involve retrieval.
Evaluations on multiple datasets, including our
newly proposed benchmark, highlight the ef-
fectiveness of our framework and the benefits
of KG-derived planning data.
1
```

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 8—9；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_cea61ca4533fd32e6f63ea730fb194ab`。

字符位置：`[{"pdf_page": 8, "start_char": 3661, "end_char": 4405, "chunk_start_char": 0, "chunk_end_char": 744, "block_bboxes": [[306.142, 552.544, 381.209, 564.499], [305.804, 574.956, 526.318, 775.47]]}, {"pdf_page": 9, "start_char": 0, "end_char": 754, "chunk_start_char": 745, "chunk_end_char": 1499, "block_bboxes": [[180.817, 292.104, 414.46, 302.067], [70.866, 324.955, 125.334, 336.91], [70.866, 346.852, 290.946, 371.348], [70.593, 373.953, 290.947, 452.691], [70.473, 455.399, 289.317, 547.583]]}]`

```text
Conclusion
In this paper, we try to enhance the planning ability
in retrieval-augmented LLMs using KGs. Specifi-
cally, we design a framework for Learning to Plan
from KG (LPKG). The proposed LPKG framework
first utilizes the rich patterns in the KGs to con-
struct planning data, then fine-tune planning LLMs
based on such data to enable them to conduct plan-
ning on downstream datasets, and ultimately get
the final answer through parsing and execution.
The experimental results reveal the excellent per-
formance of the LPKG framework and also demon-
strate the effectiveness of using KG-sourced data to
enhance LLMs’ planning ability. Finally, we con-
struct CLQA-Wiki, providing a more challenging
complex QA benchmark for the community.

Figure 4: Fine-grained evaluation based on question types.
Limitation
In our view, the limitations of our work at the cur-
rent stage mainly stem from two aspects:
(1) During the fine-tuning phase of planning
LLMs, we simply mixed various types of ques-
tions together uniformly for training. We have not
yet explored the impact of question type distribu-
tion on the experimental results, which could be
the focus of future work.
(2) At present, the datasets we test have explicit
types of questions (multi-hop, comparison, and
union/intersection), but in reality, some question
types may be implicit or even not be included in
the types we define. The future direction of our
work can be to study planning methods for these
types of unclear questions.
```

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### R23 · 调用公式与搜索预算 · cross

ToG/ToG-R 的调用公式与 Tree-of-Traversals 的 max depth/max expansions 各约束什么量？为什么不能把它们直接换算成跨方法墙钟时延排名？

**参考答案：** ToG 与 ToG-R 的公式分别为 2ND+D+1 和 ND+D+1，描述 LLM 调用数量；Tree-of-Traversals 的深度/扩展数限制搜索空间。调用数、深度和扩展数不是同一量，还缺每次调用耗时等条件，不能直接排列墙钟时延。

**逐项判分：**

- `R23.C01`：两种调用公式依次是 2ND+D+1 与 ND+D+1。（来源：togr）
- `R23.C02`：max depth/max expansions 是搜索边界。（来源：totbound）
- `R23.C03`：调用数量、深度、扩展数属于不同量。（来源：togr, totbound）
- `R23.C04`：缺少每次调用耗时等条件，不能直接推断跨方法时延排名。（来源：togr, totbound）

**考查关系：** BOUNDED_BY, CLAIMS_BENEFIT, CONNECTS, HAS_CALL_BOUND, HAS_STOP_CONDITION, RETURNS, USES_COMPONENT, VARIANT_OF

**错误边界：** 不能反转变体方向，也不能将调用上界当作跨方法实测时延。

- 参考路径 `togr.P01`：ToG-R —VARIANT_OF→ ToG
- 参考路径 `togr.P02`：ToG-R —USES_COMPONENT→ random entity pruning
- 参考路径 `togr.P03`：ToG-R —CLAIMS_BENEFIT→ lower LLM-call cost and reasoning time
- 参考路径 `togr.P04`：ToG-R —CLAIMS_BENEFIT→ reduced risk with unfamiliar intermediate entities
- 参考路径 `togr.P05`：ToG —USES_COMPONENT→ LLM-based entity pruning
- 参考路径 `togr.P06`：ToG —HAS_CALL_BOUND→ 2ND + D + 1 LLM calls
- 参考路径 `togr.P07`：ToG-R —HAS_CALL_BOUND→ ND + D + 1 LLM calls

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 22—22；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_91a4a2e6943ad6a8074492d3f7229692`。

字符位置：`[{"pdf_page": 22, "start_char": 662, "end_char": 2113, "chunk_start_char": 0, "chunk_end_char": 1451, "block_bboxes": [[107.641, 238.664, 505.247, 402.282]]}]`

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

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

### R24 · 多跳逻辑与跨知识库 · cross

用 CLQA-Wiki、2WikiMultiHop、MusicBrainz-x-Wikidata 三个例子，说明多跳、交并逻辑和跨 KG 各指什么；这些属性是否互相排斥？

**参考答案：** CLQA-Wiki 明列多跳、比较、交、并；2WikiMultiHop 是多跳任务；MusicBrainz-x-Wikidata 需要联合 MusicBrainz 与 Wikidata。多跳、逻辑运算和跨 KG 是不同维度，可以共存，不能由其一否定其他属性。

**逐项判分：**

- `R24.C01`：CLQA-Wiki 包含多跳、比较、交和并。（来源：lpbench）
- `R24.C02`：2WikiMultiHop 是多跳任务。（来源：totds）
- `R24.C03`：MusicBrainz-x-Wikidata 需要联合两个 KG。（来源：totmusic）
- `R24.C04`：这些任务属性可以共存，不能作互斥推断。（来源：lpbench, totds, totmusic）

**考查关系：** DERIVED_FROM, EVALUATED_ON, HAS_QUESTION_TYPE, HAS_TASK, USES_KNOWLEDGE_BASE

**错误边界：** 这些属性可并存，不能由一项属性推出数据集没有其他题型。

- 参考路径 `lpbench.P01`：CLQA-Wiki —DERIVED_FROM→ Wikidata subset
- 参考路径 `lpbench.P02`：CLQA-Wiki —HAS_QUESTION_TYPE→ multi-hop
- 参考路径 `lpbench.P03`：CLQA-Wiki —HAS_QUESTION_TYPE→ comparison
- 参考路径 `lpbench.P04`：CLQA-Wiki —HAS_QUESTION_TYPE→ intersection
- 参考路径 `lpbench.P05`：CLQA-Wiki —HAS_QUESTION_TYPE→ union

**完整来源：** Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs；PDF 页 2—2；`Methods/024_Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs.pdf`；块 `chunk_ab66789d9bc91de68948962d6c3f0011`。

字符位置：`[{"pdf_page": 2, "start_char": 1158, "end_char": 2387, "chunk_start_char": 0, "chunk_end_char": 1229, "block_bboxes": [[70.473, 416.616, 290.949, 603.847], [70.506, 615.603, 290.949, 775.47], [306.142, 72.649, 399.883, 84.604]]}]`

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

- 参考路径 `totds.P01`：Tree-of-Traversals —EVALUATED_ON→ 2WikiMultiHop
- 参考路径 `totds.P02`：Tree-of-Traversals —EVALUATED_ON→ QALD-10

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 5—5；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_a8ce6be635ba6abbbc71daeb86e809e9`。

字符位置：`[{"pdf_page": 5, "start_char": 888, "end_char": 2200, "chunk_start_char": 0, "chunk_end_char": 1312, "block_bboxes": [[70.866, 373.795, 153.883, 385.75], [70.353, 397.537, 290.946, 408.538], [70.506, 409.426, 290.943, 516.91], [70.866, 531.077, 186.841, 541.986], [70.353, 550.22, 289.137, 561.172], [70.866, 563.885, 290.95, 628.908], [70.866, 632.233, 290.941, 751.637], [83.519, 762.682, 248.401, 772.731], [309.977, 73.825, 520.839, 98.283], [357.666, 100.732, 473.149, 111.832]]}]`

```text
Experiments
We evaluate Tree-of-Traversals using three differ-
ent models available on Amazon Bedrock3: Claude-
Instant (claude-instant-v1), Llama2 70b
(llama2-70b-chat-v1), and Llama2 13b
(llama2-13b-chat-v1). AWS Bedrock pro-
vides on-demand access through a single API to
various Foundation Models, including both open
source and black box ones. This is precisely a use
case Tree-of-Traversals is designed for.
3.1
Tasks and Datasets.
We first evaluate the Tree-of-Traversals algorithm
on two common tasks used for evaluating an LLM’s
knowledge: 2WikiMultiHop and QALD-10. To al-
low testing on complex questions requiring knowl-
edge from multiple KGs we create a new dataset
that requires knowledge from multiple KGs.
2WikiMultiHop Dataset (Ho et al., 2020) was
constructed by extracting multi-hop templates from
HotPotQA (Yang et al., 2018), combining tem-
plates to get complex reasoning questions, gener-
ating candidate questions with Wikidata, and then
confirming that the entity mentions for each edge
appear in the Wikipedia paragraphs. Answers to
these questions can be derived from both Wikipedia
and Wikidata (Vrandeˇci´c and Krötzsch, 2014). We
3https://aws.amazon.com/bedrock
Which event was hosted in a venue with a larger
maximum capacity, Fearless Tour: Indianapolis
or Fearless Tour: Omaha?
```

- 参考路径 `totmusic.P01`：Tree-of-Traversals —EVALUATED_ON→ MusicBrainz-x-Wikidata —USES_KNOWLEDGE_BASE→ MusicBrainz
- 参考路径 `totmusic.P02`：MusicBrainz-x-Wikidata —USES_KNOWLEDGE_BASE→ Wikidata
- 参考路径 `totmusic.P03`：MusicBrainz-x-Wikidata —HAS_TASK→ 109 cross-KG questions

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 5—6；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_f4962498025654850621ee329d0af7d6`。

字符位置：`[{"pdf_page": 5, "start_char": 3325, "end_char": 4344, "chunk_start_char": 0, "chunk_end_char": 1019, "block_bboxes": [[305.804, 480.537, 526.318, 749.037], [318.794, 762.682, 489.559, 772.731]]}, {"pdf_page": 6, "start_char": 0, "end_char": 314, "chunk_start_char": 1020, "chunk_end_char": 1334, "block_bboxes": [[302.451, 75.747, 392.265, 87.05], [140.608, 95.172, 446.717, 106.081], [146.585, 114.421, 448.688, 192.976], [316.605, 201.022, 378.111, 212.325], [140.608, 220.447, 446.717, 231.356]]}]`

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

### N01 · 无依据继承关系 · negative

有人说：RoG 直接继承了 HippoRAG 的 PPR，因为二者都做图上多跳。请依据两篇论文判断这条继承关系，并分别指出已知机制。

**参考答案：** 给定来源不能建立该继承关系。HippoRAG 使用查询种子驱动 PPR；RoG 使用关系路径规划与有效路径检索。共同目标不能证明直接继承，也不能由当前缺证据证明历史上从未有关联。

**逐项判分：**

- `N01.C01`：正确归属 HippoRAG 的 PPR。（来源：hippo）
- `N01.C02`：正确归属 RoG 的关系计划/路径检索。（来源：rog）
- `N01.C03`：不确认无来源的继承边，并限定为当前来源未建立。（来源：hippo, rog）

**考查关系：** CONNECTS, HAS_STAGE, TRAINED_WITH, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

- 参考路径 `rog.P01`：RoG —HAS_STAGE→ planning —CONNECTS→ KG-constrained relation path plan
- 参考路径 `rog.P02`：RoG —HAS_STAGE→ retrieval —CONNECTS→ valid reasoning paths
- 参考路径 `rog.P03`：RoG —TRAINED_WITH→ KG knowledge distillation

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 1—1；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

字符位置：`[{"pdf_page": 1, "start_char": 318, "end_char": 1721, "chunk_start_char": 0, "chunk_end_char": 1403, "block_bboxes": [[278.288, 270.703, 333.722, 282.658], [143.866, 296.104, 468.139, 492.369], [108.299, 514.402, 205.989, 526.357]]}]`

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

### N02 · 无依据全称优越性 · negative

仅根据 ToG 与 ToG-2 都列出 WebQSP，就断言 ToG-2 在所有底座、所有数据集上都更好，依据充分吗？还需要核对什么？

**参考答案：** 不充分。共同评测 WebQSP 只说明评测关联；全称性能结论还需匹配划分、底座、知识来源、提示及完整结果，给定来源不能支持该断言。

**逐项判分：**

- `N02.C01`：拒绝由共同数据集推出所有条件下更优。（来源：togds, tog2ds）
- `N02.C02`：说明划分、底座、知识来源、提示与完整结果仍需核对。（来源：togds, tog2ds）

**考查关系：** DERIVED_FROM, EVALUATED_ON, REPORTS_METRIC, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `togds.P01`：ToG —EVALUATED_ON→ WebQSP
- 参考路径 `togds.P02`：ToG —EVALUATED_ON→ QALD10-en
- 参考路径 `togds.P03`：ToG —EVALUATED_ON→ Creak
- 参考路径 `togds.P04`：ToG —REPORTS_METRIC→ exact match accuracy (Hits@1)

**完整来源：** Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph；PDF 页 5—5；`Methods/215_Think-on-Graph Deep and Responsible Reasoning of Large Language Model with Knowledge Graph.pdf`；块 `chunk_deb9eea46e529705dffdd1103729c44c`。

字符位置：`[{"pdf_page": 5, "start_char": 2914, "end_char": 4358, "chunk_start_char": 0, "chunk_end_char": 1444, "block_bboxes": [[108.299, 482.573, 200.083, 494.529], [108.249, 507.855, 235.26, 517.818], [108.249, 528.452, 305.88, 538.415], [107.671, 547.628, 504.824, 656.296], [108.249, 670.178, 310.993, 680.141], [107.532, 689.505, 505.652, 732.293], [303.509, 752.194, 308.49, 762.157]]}]`

```text
EXPERIMENTS
3.1
EXPERIMENTAL DESIGN
3.1.1
DATASETS AND EVALUATION METRICS
In order to test ToG’s ability on multi-hop knowledge-intensive reasoning tasks, we evaluate ToG
on five KBQA datasets (4 Multi-hop and 1 Single-hop): CWQ (Talmor & Berant, 2018), WebQSP
(Yih et al., 2016), GrailQA (Gu et al., 2021), QALD10-en (Perevalov et al., 2022), Simple Questions
(Bordes et al., 2015). Moreover, in order to examine ToG on more generic tasks, we also prepare
one open-domain QA dataset: WebQuestions (Berant et al., 2013); two slot filling datasets: T-REx
(ElSahar et al., 2018) and Zero-Shot RE (Petroni et al., 2021); and one fact-checking dataset: Creak
(Onoe et al., 2021). Note that, for two big datasets GrailQA and Simple Questions, we only randomly
selected 1,000 samples each for testing in order to save computational cost. For all datasets, exact
match accuracy (Hits@1) is used as our evaluation metric following previous works (Li et al., 2023c;
Baek et al., 2023b; Jiang et al., 2023; Li et al., 2023a).
3.1.2
METHODS SELECTED FOR COMPARISON
We compare with standard prompting (IO prompt) (Brown et al., 2020b), Chain-of-Thought prompting
(CoT prompt) (Wei et al., 2022), and Self-Consistency (Wang et al., 2023c) with 6 in-context
exemplars and "step-by-step" reasoning chains. Moreover, for each dataset, we pick previous state-of-
the-art (SOTA) works for comparison. We notice that fine-tuning methods trained specifically on
5
```

- 参考路径 `tog2ds.P01`：ToG-2 —EVALUATED_ON→ WebQSP
- 参考路径 `tog2ds.P02`：ToG-2 —EVALUATED_ON→ QALD10-en
- 参考路径 `tog2ds.P03`：ToG-2 —EVALUATED_ON→ AdvHotpotQA
- 参考路径 `tog2ds.P04`：ToG-2 —EVALUATED_ON→ FEVER
- 参考路径 `tog2ds.P05`：ToG-2 —EVALUATED_ON→ Creak
- 参考路径 `tog2ds.P06`：AdvHotpotQA —DERIVED_FROM→ HotpotQA
- 参考路径 `tog2ds.P07`：ToG-2 evaluation —USES_KNOWLEDGE_BASE→ full Wikipedia and Wikidata
- 参考路径 `tog2ds.P08`：ToG-2 evaluation —REPORTS_METRIC→ Accuracy on FEVER and Creak
- 参考路径 `tog2ds.P09`：ToG-2 evaluation —REPORTS_METRIC→ EM on other datasets
- 参考路径 `tog2ds.P10`：ToG-2 —USES_EVALUATION_SETTING→ ToG-2 evaluation

**完整来源：** Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval；PDF 页 6—6；`Methods/015_Think-on-Graph 2.0 Deep and Interpretable Large Language Model Reasoning with Knowledge Gr.pdf`；块 `chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

字符位置：`[{"pdf_page": 6, "start_char": 1827, "end_char": 2910, "chunk_start_char": 0, "chunk_end_char": 1083, "block_bboxes": [[108.299, 418.062, 200.083, 430.017], [108.249, 442.645, 239.271, 452.608], [108.0, 463.168, 504.003, 582.72]]}]`

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

### N03 · 图表示张冠李戴 · negative

把 KGP 的“段落节点＋语义相似边”直接作为 HippoRAG 的图定义是否有依据？请分别说明来源支持的表示与检索机制。

**参考答案：** 没有充分依据。KGP 的节点可以是段落或文档结构，边可以是相似或结构关系；HippoRAG 把语料转为无模式 KG，用查询种子启动 PPR。不能直接互换节点和边的语义。

**逐项判分：**

- `N03.C01`：正确描述 KGP 的节点与边。（来源：kgp）
- `N03.C02`：正确描述 HippoRAG 的无模式 KG 与 PPR。（来源：hippo）
- `N03.C03`：拒绝直接互换两种图表示。（来源：kgp, hippo）

**考查关系：** COLLECTS, CONNECTS, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, USES_AGENT, USES_ALGORITHM, USES_COMPONENT, USES_INPUT

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

- 参考路径 `hippo.P01`：HippoRAG —USES_COMPONENT→ LLM corpus transformation —CONNECTS→ schemaless knowledge graph
- 参考路径 `hippo.P02`：HippoRAG —USES_ALGORITHM→ Personalized PageRank —USES_INPUT→ query concepts as seeds
- 参考路径 `hippo.P03`：Personalized PageRank —CONNECTS→ cross-passage evidence

**完整来源：** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models；PDF 页 2—2；`Methods/035_HippoRAG Neurobiologically Inspired Long-Term Memory for Large Language Models.pdf`；块 `chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

字符位置：`[{"pdf_page": 2, "start_char": 1574, "end_char": 2946, "chunk_start_char": 0, "chunk_end_char": 1372, "block_bboxes": [[108.0, 472.448, 504.004, 547.812], [107.671, 554.313, 504.351, 640.564]]}]`

```text
In contrast, our brains are capable of solving challenging knowledge integration tasks like these with
relative ease. The hippocampal memory indexing theory [75], a well-established theory of human
long-term memory, offers one plausible explanation for this remarkable ability. Teyler and Discenna
[75] propose that our powerful context-based, continually updating memory relies on interactions
between the neocortex, which processes and stores actual memory representations, and the C-shaped
hippocampus, which holds the hippocampal index, a set of interconnected indices which point to
memory units on the neocortex and stores associations between them [19, 76].
In this work, we propose HippoRAG, a RAG framework that serves as a long-term memory for LLMs
by mimicking this model of human memory. Our novel design first models the neocortex’s ability to
process perceptual input by using an LLM to transform a corpus into a schemaless knowledge graph
(KG) as our artificial hippocampal index. Given a new query, HippoRAG identifies the key concepts
in the query and runs the Personalized PageRank (PPR) algorithm [30] on the KG, using the query
concepts as the seeds, to integrate information across passages for retrieval. PPR enables HippoRAG
to explore KG paths and identify relevant subgraphs, essentially performing multi-hop reasoning in a
single retrieval step.
```

### N04 · 训练测试角色颠倒 · negative

看到 KG-GPT 与 RoG 都涉及 MetaQA，有人把 Freebase 写成它们共同的 MetaQA 测试 KG。这个结论对吗？请核对 Wiki-Movies、Freebase 和训练样本的角色。

**参考答案：** 给定来源不支持该共同测试 KG 结论。KG-GPT 表列 MetaQA 1/2/3-hop；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是迁移前训练来源，1000 个样本来自训练划分。不能把训练来源当成共同测试 KG。

**逐项判分：**

- `N04.C01`：KG-GPT 来源列出 MetaQA 1/2/3-hop，未据此补造共同 Freebase 测试设置。（来源：kggptds）
- `N04.C02`：MetaQA-3hop 基于 Wiki-Movies。（来源：rogmeta）
- `N04.C03`：Freebase 是迁移前训练来源，1000 个样本来自训练划分。（来源：rogmeta）
- `N04.C04`：拒绝共同 Freebase 测试 KG 的推断。（来源：kggptds, rogmeta）

**考查关系：** DERIVES_TRAINING_DATA_FROM, EVALUATED_ON, REPORTS_METRIC, USES_DATASET, USES_EVALUATION_SETTING, USES_KNOWLEDGE_BASE, USES_TRAINING_SIGNAL

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `kggptds.P01`：KG-GPT —EVALUATED_ON→ FACTKG
- 参考路径 `kggptds.P02`：KG-GPT —EVALUATED_ON→ MetaQA
- 参考路径 `kggptds.P03`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 1-hop
- 参考路径 `kggptds.P04`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 2-hop
- 参考路径 `kggptds.P05`：KG-GPT MetaQA evaluation —USES_DATASET→ MetaQA 3-hop
- 参考路径 `kggptds.P06`：KG-GPT MetaQA evaluation —REPORTS_METRIC→ Hits@1
- 参考路径 `kggptds.P07`：KG-GPT —USES_EVALUATION_SETTING→ KG-GPT MetaQA evaluation

**完整来源：** KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models；PDF 页 4—4；`Methods/181_KG-GPT A General Framework for Reasoning on Knowledge Graphs Using Large Language Models.pdf`；块 `chunk_3f7eb65828761447433c66c28ad111a4`。

字符位置：`[{"pdf_page": 4, "start_char": 57, "end_char": 1493, "chunk_start_char": 0, "chunk_end_char": 1436, "block_bboxes": [[143.353, 97.415, 274.997, 143.495], [76.209, 164.205, 132.263, 173.955], [146.652, 146.04, 274.997, 180.181], [149.091, 158.232, 274.997, 192.29], [70.557, 205.158, 290.877, 239.106], [75.442, 254.684, 284.569, 273.404], [85.336, 296.402, 96.475, 304.752], [78.31, 275.807, 276.34, 367.731], [70.119, 390.658, 289.494, 424.606], [70.866, 449.144, 289.139, 487.235], [70.593, 490.24, 290.949, 650.24], [70.866, 663.055, 136.004, 673.964]]}]`

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

- 参考路径 `rogmeta.P01`：RoG —EVALUATED_ON→ MetaQA-3hop —USES_KNOWLEDGE_BASE→ Wiki-Movies
- 参考路径 `rogmeta.P02`：RoG —DERIVES_TRAINING_DATA_FROM→ Freebase
- 参考路径 `rogmeta.P03`：RoG —USES_TRAINING_SIGNAL→ 1000 MetaQA-3hop training samples
- 参考路径 `rogmeta.P04`：RoG transfer experiment —USES_KNOWLEDGE_BASE→ Freebase to Wiki-Movies transfer
- 参考路径 `rogmeta.P05`：RoG —USES_EVALUATION_SETTING→ RoG transfer experiment

**完整来源：** Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning；PDF 页 20—20；`Methods/191_Reasoning on Graphs Faithful and Interpretable Large Language Model Reasoning.pdf`；块 `chunk_f5c88d605f651f26c093f30b836a98aa`。

字符位置：`[{"pdf_page": 20, "start_char": 348, "end_char": 1306, "chunk_start_char": 0, "chunk_end_char": 958, "block_bboxes": [[108.249, 283.751, 292.912, 293.714], [108.0, 304.529, 504.003, 380.755], [108.0, 387.729, 504.003, 419.609]]}]`

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

### N05 · 领域重叠伪造评测边 · negative

STaRK 涉及精准医疗，MindMap 涉及医学 QA。能否据此补一条 MindMap 在 STaRK 上评测的边并填写分数？请说明证据边界。

**参考答案：** 不能。两篇来源分别说明医学领域关联，但未建立 MindMap 在 STaRK 上评测的关系或分数；只能说明当前证据不足，不能宣称证明它从未评测。

**逐项判分：**

- `N05.C01`：STaRK 来源支持精准医疗检索领域。（来源：stark）
- `N05.C02`：MindMap 来源支持医学 QA 场景。（来源：mind）
- `N05.C03`：不捏造评测边或分数，也不把缺证据说成从未发生。（来源：stark, mind）

**考查关系：** HAS_TASK, RETRIEVES_FROM, TARGETS_TASK, USES_COMPONENT

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `stark.P01`：STaRK —HAS_TASK→ product search
- 参考路径 `stark.P02`：STaRK —HAS_TASK→ academic paper search
- 参考路径 `stark.P03`：STaRK —HAS_TASK→ precision medicine retrieval

**完整来源：** STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases；PDF 页 1—1；`Resources/002_STaRK Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases.pdf`；块 `chunk_6b5383484693f6226010eab8143f80d6`。

字符位置：`[{"pdf_page": 1, "start_char": 324, "end_char": 2018, "chunk_start_char": 0, "chunk_end_char": 1694, "block_bboxes": [[283.758, 245.19, 328.243, 257.145], [143.866, 269.807, 469.789, 454.391], [205.19, 610.031, 248.703, 620.969], [211.6, 599.33, 240.929, 607.533], [216.449, 585.557, 238.006, 593.76], [385.922, 619.315, 478.763, 627.518], [437.928, 589.928, 443.83, 596.764], [144.476, 619.045, 160.888, 627.248], [352.298, 589.067, 382.359, 597.271], [260.676, 563.411, 293.347, 571.614], [283.166, 474.459, 315.256, 485.396], [302.055, 504.115, 386.419, 520.044], [298.079, 528.776, 350.265, 544.62], [370.448, 534.987, 376.35, 541.823], [401.047, 502.427, 449.478, 514.664], [373.918, 519.121, 381.0, 527.324], [161.972, 549.841, 211.15, 564.335], [164.844, 565.505, 209.149, 570.006], [177.292, 570.096, 195.824, 574.597], [324.724, 518.31, 331.806, 526.514], [263.612, 620.935, 339.71, 629.138], [354.51, 529.231, 392.389, 541.536]]}]`

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

- 参考路径 `mind.P01`：MindMap —USES_COMPONENT→ LLM implicit knowledge
- 参考路径 `mind.P02`：MindMap —RETRIEVES_FROM→ external knowledge graph
- 参考路径 `mind.P03`：MindMap —USES_COMPONENT→ mind map reasoning path
- 参考路径 `mind.P04`：MindMap —TARGETS_TASK→ medical question answering

**完整来源：** MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models；PDF 页 1—1；`Methods/211_MindMap Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models.pdf`；块 `chunk_2f4809d54362f998c1c0710e915a721b`。

字符位置：`[{"pdf_page": 1, "start_char": 295, "end_char": 1548, "chunk_start_char": 0, "chunk_end_char": 1253, "block_bboxes": [[157.758, 205.394, 367.277, 233.646], [87.516, 243.186, 273.781, 575.915], [70.866, 586.177, 153.68, 598.132]]}]`

```text
Abstract
Large language models (LLMs) have achieved
remarkable performance in natural language
understanding and generation tasks. However,
they often suffer from limitations such as diffi-
culty in incorporating new knowledge, gener-
ating hallucinations, and explaining their rea-
soning process. To address these challenges,
we propose a novel prompting pipeline, named
MindMap, that leverages knowledge graphs
(KGs) to enhance LLMs’ inference and trans-
parency. Our method enables LLMs to com-
prehend KG inputs and infer with a combina-
tion of implicit and external knowledge. More-
over, our method elicits the mind map of LLMs,
which reveals their reasoning pathways based
on the ontology of knowledge. We evaluate our
method on diverse question & answering tasks,
especially in medical domains, and show sig-
nificant improvements over baselines. We also
introduce a new hallucination evaluation bench-
mark and analyze the effects of different com-
ponents of our method. Our results demonstrate
the effectiveness and robustness of our method
in merging knowledge from LLMs and KGs for
combined inference. To reproduce our results
and extend the framework further, we make our
codebase available at https://github.com/wyl-
willing/MindMap.
1
```

### N06 · 无来源实体与数值拒答 · negative

请给出 NebulaGraphRAG-2099 继承 HippoRAG 的官方证据，并报告它在 LunarQA-2099 上相对 RoG 的精确提升分数。

**参考答案：** 冻结语料没有这些虚构方法、基准、继承关系或分数的来源；应明确无法给出有依据的官方证据和数值，不编造。

**逐项判分：**

- `N06.C01`：明确当前冻结语料没有该方法、基准及关系/分数来源。（来源：无来源拒答）
- `N06.C02`：不编造官方证据、继承链或精确数值。（来源：无来源拒答）

**考查关系：** 无来源实体与数值拒答

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

### N07 · 增强方向反转 · negative

CuriousLLM 增强 KGP，是否意味着反过来 KGP 使用 CuriousLLM 的 Follow-upQA 训练？请给出有来源的方向与各自职责。

**参考答案：** 不能反向推出。来源支持 CuriousLLM 增强 KGP，Follow-upQA 用于学习后续问题；KGP 的遍历代理收集支持段落。给定来源没有建立 KGP 使用 Follow-upQA 训练的边。

**逐项判分：**

- `N07.C01`：增强方向是 CuriousLLM 指向 KGP。（来源：curious）
- `N07.C02`：Follow-upQA 学习后续问题。（来源：curious）
- `N07.C03`：KGP 的代理收集支持段落。（来源：kgp）
- `N07.C04`：不确认反向训练关系。（来源：kgp, curious）

**考查关系：** COLLECTS, ENHANCES, GENERATES, HAS_EDGE_TYPE, HAS_GRAPH_REPRESENTATION, HAS_NODE_TYPE, HAS_TARGET, USES_AGENT, USES_INPUT

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `kgp.P01`：KGP —HAS_GRAPH_REPRESENTATION→ document knowledge graph —HAS_NODE_TYPE→ passage
- 参考路径 `kgp.P02`：document knowledge graph —HAS_NODE_TYPE→ document structure
- 参考路径 `kgp.P03`：document knowledge graph —HAS_EDGE_TYPE→ lexical or semantic similarity
- 参考路径 `kgp.P04`：document knowledge graph —HAS_EDGE_TYPE→ intra-document structure
- 参考路径 `kgp.P05`：KGP —USES_AGENT→ LLM graph traversal agent —COLLECTS→ supporting passages

**完整来源：** Knowledge Graph Prompting for Multi-Document Question Answering；PDF 页 1—1；`Methods/209_Knowledge Graph Prompting for Multi-Document Question Answering.pdf`；块 `chunk_b959214e888053dae53b16a5259d7ea9`。

字符位置：`[{"pdf_page": 1, "start_char": 310, "end_char": 1851, "chunk_start_char": 0, "chunk_end_char": 1541, "block_bboxes": [[154.715, 218.316, 191.786, 228.279], [63.963, 235.864, 282.537, 493.897], [54.0, 509.791, 292.505, 677.594]]}]`

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

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

### N08 · 预算耗尽冒充成功 · negative

Tree-of-Traversals 达到 max expansions 或 max depth 就意味着证据充分、回答正确，并且等同于 CuriousLLM 的充分证据 token，对吗？

**参考答案：** 不对。max expansions 会停止探索并返回 Cannot find answer；max depth 强制 done 作答。CuriousLLM 的特殊 token 表示证据充分，是另一种信号；这些机制都不能自动保证答案正确。

**逐项判分：**

- `N08.C01`：max expansions 返回 Cannot find answer。（来源：totbound）
- `N08.C02`：max depth 强制 done，与扩展耗尽不同。（来源：totbound）
- `N08.C03`：CuriousLLM 的特殊 token 表示证据充分。（来源：curious）
- `N08.C04`：不把预算耗尽等同于充分证据或答案正确。（来源：totbound, curious）

**考查关系：** BOUNDED_BY, CONNECTS, ENHANCES, GENERATES, HAS_STOP_CONDITION, HAS_TARGET, RETURNS, USES_INPUT

**错误边界：** 不确认题干中无来源的关系或数值；说明证据边界。

- 参考路径 `totbound.P01`：Tree-of-Traversals —HAS_STOP_CONDITION→ node value exceeds answer threshold —RETURNS→ answer found
- 参考路径 `totbound.P02`：Tree-of-Traversals —BOUNDED_BY→ max depth —CONNECTS→ forced transition to done
- 参考路径 `totbound.P03`：Tree-of-Traversals —BOUNDED_BY→ max expansions —CONNECTS→ Cannot find answer

**完整来源：** Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs；PDF 页 4—4；`Methods/018_Tree-of-Traversals A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Model.pdf`；块 `chunk_dac5f23e1b87249cf88eff5c6cc54355`。

字符位置：`[{"pdf_page": 4, "start_char": 780, "end_char": 2398, "chunk_start_char": 0, "chunk_end_char": 1618, "block_bboxes": [[70.473, 323.184, 290.949, 496.704], [70.473, 505.386, 290.941, 773.66]]}]`

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

- 参考路径 `curious.P01`：CuriousLLM —ENHANCES→ KGP
- 参考路径 `curious.P02`：CuriousLLM —GENERATES→ follow-up question —USES_INPUT→ question and evidence
- 参考路径 `curious.P03`：follow-up question —HAS_TARGET→ next question
- 参考路径 `curious.P04`：CuriousLLM —GENERATES→ evidence-sufficient special token

**完整来源：** CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting；PDF 页 1—1；`Methods/059_CuriousLLM Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting.pdf`；块 `chunk_43145c0748762d6b4c650c65721f826f`。

字符位置：`[{"pdf_page": 1, "start_char": 252, "end_char": 1774, "chunk_start_char": 0, "chunk_end_char": 1522, "block_bboxes": [[157.758, 221.69, 202.243, 233.645], [87.376, 245.034, 274.616, 649.442], [70.866, 661.499, 153.68, 673.454]]}]`

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

