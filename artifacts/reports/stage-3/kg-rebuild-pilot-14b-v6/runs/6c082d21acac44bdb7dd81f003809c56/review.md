# kg-rebuild-pilot-14b-v6 重新抽取

同一批120块；新提示词、前置分流与冻结v5校验共同生效。STaRK不适用；自动保留不等于人工正确。

状态：completed；已处理 120/120；调用模型 58 块，跳过 62 块，失败 0 块。

候选 83；自动保留 18；拒绝 65。

Token：47175 输入 / 9379 输出；累计处理 2219.5 秒。

| 论文 | 块数 | 模型完成 | 跳过 | 失败 | 候选 | 保留 | 拒绝 | v4保留（旧校验） |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering | 28 | 28 | 0 | 0 | 49 | 17 | 32 | 32 |
| StructGPT: A General Framework for Large Language Model to Reason over Structured Data | 33 | 30 | 3 | 0 | 34 | 1 | 33 | 19 |
| STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases | 59 | 0 | 59 | 0 | 0 | 0 | 0 | 28 |

拒绝原因：{"table_or_template_example": 5, "implementation_object_not_named_technology": 3, "component_not_explicitly_listed": 6, "subject_not_method_anchored": 7, "evidence_quote_not_in_chunk": 34, "generic_entity": 1, "control_object_not_parameter": 7, "relation_signature_not_allowed": 2}

跳过原因：{"chunk_kind_excluded:example": 3, "benchmark_paper_not_applicable": 59}

## 逐块与逐条结果

### G-Retriever · 块 0 · 页 1-1 · completed

`chunk_a001225c0afa46199e503f9e9f8bd803`；类型 body；跳过原因 None；17.38s；Token 643/8


<details><summary>完整来源块</summary>

G-Retriever: Retrieval-Augmented Generation for
Textual Graph Understanding and
Question Answering
Xiaoxin He1
Yijun Tian2
Yifei Sun1
Nitesh V. Chawla2
Thomas Laurent3
Yann LeCun4,5
Xavier Bresson1
Bryan Hooi1
{xiaoxin, yifeisun, xaviercs, bhooi}@comp.nus.edu.sg
{yijun.tian, nchawla}@nd.edu, tlaurent@lmu.edu, yann@cs.nyu.edu
1National University of Singapore
2University of Notre Dame
3Loyola Marymount University
4New York University
5Meta AI


</details>

### G-Retriever · 块 1 · 页 1-1 · completed

`chunk_3a7f7a1f47b2586d9d9877afb9110567`；类型 body；跳过原因 None；119.25s；Token 799/520

- 拒绝 `table_or_template_example`：{"claim_id": "c466e5f9f91f509209e7bea2473b291fc4f7dfab97b926af6a90dc5f345c922e", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_3a7f7a1f47b2586d9d9877afb9110567", "subject_type": "Method", "subject": "G-Retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Graph Question Answering (GraphQA) benchmark", "evidence_quote": "Then, we propose our G-Retriever method, introducing\nthe first retrieval-augmented generation (RAG) approach for general textual graphs,\nwhich can be fine-tuned to enhance graph understanding via soft prompting.", "quote_match_method": "whitespace_normalized", "quote_start": 922, "quote_end": 1133, "source_spans": [{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}], "page_start": 1, "page_end": 1, "section": "Abstract", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `implementation_object_not_named_technology`：{"claim_id": "012e53dc1237739fdcb11e26eb44bab824f76715eef4b63b226c4ba292da6550", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_3a7f7a1f47b2586d9d9877afb9110567", "subject_type": "Component", "subject": "Graph Question Answering (GraphQA) benchmark", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "data collection from different tasks", "evidence_quote": "Then, we propose our G-Retriever method, introducing\nthe first retrieval-augmented generation (RAG) approach for general textual graphs,\nwhich can be fine-tuned to enhance graph understanding via soft prompting.", "quote_match_method": "whitespace_normalized", "quote_start": 922, "quote_end": 1133, "source_spans": [{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}], "page_start": 1, "page_end": 1, "section": "Abstract", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "5e7ea1955937755d05a802fa9bc6f4ef9bf73a455350e3c8dd3ae32a304646f8", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_3a7f7a1f47b2586d9d9877afb9110567", "subject_type": "Method", "subject": "G-Retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "retrieval-augmented generation (RAG) approach", "evidence_quote": "Then, we propose our G-Retriever method, introducing\nthe first retrieval-augmented generation (RAG) approach for general textual graphs,\nwhich can be fine-tuned to enhance graph understanding via soft prompting.", "quote_match_method": "whitespace_normalized", "quote_start": 922, "quote_end": 1133, "source_spans": [{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}], "page_start": 1, "page_end": 1, "section": "Abstract", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `table_or_template_example`：{"claim_id": "ea001727493703a7edd1df83722d9260cb196a9168073a97639e45807234d01a", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_3a7f7a1f47b2586d9d9877afb9110567", "subject_type": "Component", "subject": "retrieval-augmented generation (RAG) approach", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "Prize-Collecting Steiner Tree optimization problem", "evidence_quote": "To\nresist hallucination and to allow for textual graphs that greatly exceed the LLM’s\ncontext window size, G-Retriever performs RAG over a graph by formulating this\ntask as a Prize-Collecting Steiner Tree optimization problem.", "quote_match_method": "whitespace_normalized", "quote_start": 1134, "quote_end": 1360, "source_spans": [{"pdf_page": 1, "start_char": 446, "end_char": 1988, "chunk_start_char": 0, "chunk_end_char": 1542, "block_bboxes": [[283.758, 307.967, 328.243, 319.922], [143.507, 333.439, 469.787, 539.841], [108.0, 562.422, 190.814, 574.377]]}], "page_start": 1, "page_end": 1, "section": "Abstract", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 2 · 页 1-2 · completed

`chunk_3230a7429a621a89f8fef1361c527b3a`；类型 body；跳过原因 None；2.87s；Token 777/8


<details><summary>完整来源块</summary>

Introduction
Graphs and Large Language Models (LLMs). The advent of LLMs has significantly shaped the
artificial intelligence landscape. As these models are applied to increasingly diverse tasks, their ability
to process complex structured data will be increasingly vital. In particular, in our interconnected
world, a significant portion of real-world data inherently possesses a graph structure, such as the
Web, e-commerce, recommendation systems, knowledge graphs, and many others. Moreover, many
of these involve graphs with textual attributes (i.e., textual graphs), making them well-suited for
LLM-centric methods. This has spurred interest in combining graph-based technologies, particularly
graph neural networks (GNNs), with LLMs to enhance their reasoning on graphs [44, 15, 24].
The Present Work: Enabling ‘Chat With Your Graph’. While existing works integrate LLMs and
GNNs in various ways, they mostly focus on conventional graph tasks such as node, edge and graph
1Our codes and datasets are available at: https://github.com/XiaoxinHe/G-Retriever
arXiv:2402.07630v3  [cs.LG]  27 May 2024

New Benchmark
GraphQA
New Architecture
G-Retriever
Techniques
Retrieval Augmented Generation
Graph Prompt Tuning
Graph Textualization


</details>

### G-Retriever · 块 3 · 页 2-2 · completed

`chunk_58a54700941a16a03add8585787df2a8`；类型 body；跳过原因 None；2.72s；Token 874/8


<details><summary>完整来源块</summary>

Sure! Here's an example of a 500-word advertisement
for the place based on the scene graph:
"Experience the breathtaking beauty of our place,
where the rolling hills meet the sparkling water of the
swimming pool. Take a leisurely stroll through the
lush green fields, and let the gentle breeze caress
your face as you gaze out at the picturesque view. The
sheep graze peacefully in the distance, their white
coats glistening in the sunlight. The sky is a brilliant
blue, with fluffy white clouds drifting lazily across.
Come and bask in the serene ambiance of our place,
where the natural beauty will leave you in awe."
Unified Conversational Interface
grazing on
above
eating
grass
water
moutains
covered
Scene Graph
sky
blue, clear, cloudly
sheep
white, fluffy
Knowledge Graph
benjamin franklin
lighting rod
glass harmonica
franklin
stove
inventions
inventors
bifocals
inventions
inventions
women
change
appearance
addiction
stop
positive
human
searching for
perfection
capable of
created by
is not a
not capable of
cosmetic
surgery
receive action
Explanation Graph
used for
part of
The explanation graph provides a detailed analysis of
the reasons why women undergo cosmetic surgery.
According to the graph, the main reasons include the
desire to change one's appearance, the influence of
societal beauty standards, and the addiction to
searching for perfection. These reasons are further
supported by the various nodes and edges in the
graph, which provide additional insights into the
motivations and consequences of cosmetic surgery.
Firstly, the node labeled "human" highlights the
fundamental human desire to feel attractive and
confident in one's appearance...


</details>

### G-Retriever · 块 4 · 页 2-2 · completed

`chunk_0c3502e2ebdf2179881b5102545bcd35`；类型 body；跳过原因 None；24.56s；Token 788/110

- 拒绝 `subject_not_method_anchored`：{"claim_id": "3b3fef70520363653a98a108f9d8600c388bb8589f68763e60ccc60f80ce63c1", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_0c3502e2ebdf2179881b5102545bcd35", "subject_type": "Method", "subject": "flexible question-answering framework", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "complex and real-world graphs", "evidence_quote": "In contrast,\nwe develop a flexible question-answering framework targeting complex and real-world graphs.", "quote_match_method": "whitespace_normalized", "quote_start": 1291, "quote_end": 1395, "source_spans": [{"pdf_page": 2, "start_char": 1804, "end_char": 3392, "chunk_start_char": 0, "chunk_end_char": 1588, "block_bboxes": [[184.065, 130.247, 257.276, 137.626], [292.82, 130.247, 375.355, 137.626], [399.438, 155.655, 482.101, 190.816], [400.15, 129.297, 482.595, 144.512], [108.0, 210.739, 505.65, 253.375], [107.641, 292.253, 505.247, 335.01]]}], "page_start": 2, "page_end": 2, "section": "Introduction", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Write a 500-word argument essay based on the
information provided in the explanation graph.
Write an 500-word advertisement for this place in the
scene graph that would make people want to visit it.
Great! Based on the provided knowledge graph,
here's an educational tour that highlights interesting
facts and connections related to Benjamin Franklin's
inventions and other notable achievements:
1. Franklin's Lightning Rod: Start by exploring
Franklin's most famous invention - the lightning rod.
Discover how Franklin's invention protected buildings
from lightning strikes and how it changed the way
people understood electricity...
What else did ben franklin invent? 
Surrounding this question, develop an educational
tour through the knowledge graph, highlighting
interesting facts and connections in an engaging way.
Figure 1: We develop a flexible question-answering framework targeting real-world textual graph ap-
plications via a unified conversational interface. Presented here are examples showcasing the model’s
adeptness in handling generative and creative queries in practical graph-related tasks: common sense
reasoning, scene understanding, and knowledge graph reasoning, respectively.
classification [8], or answering simple questions on small or synthetic graphs [44, 31]. In contrast,
we develop a flexible question-answering framework targeting complex and real-world graphs. This
framework enables users to ‘chat with their graph’ via a unified conversational interface, representing
a leap towards intuitive interaction with graph data, as demonstrated in Figure 1.


</details>

### G-Retriever · 块 5 · 页 2-2 · completed

`chunk_67201fef435f6ac14b79550309c5d685`；类型 body；跳过原因 None；2.58s；Token 703/8


<details><summary>完整来源块</summary>

The Need for a Comprehensive GraphQA Benchmark. Question answering (QA) is a fundamen-
tally important task in natural language processing, serving as a key benchmark for assessing LLMs
and providing a unified interface for various capabilities. Despite extensive research in QA, a com-
prehensive benchmark specifically tailored for the graph modality is lacking. In contrast to existing
benchmarks that focus on basic graph-based reasoning tasks such as node degree, edge existence, and
shortest path [6, 44], our benchmark addresses complex and real-world graph applications including
common sense reasoning, scene understanding, and knowledge graph reasoning (refer to Figure 2).
This is vital for measuring progress toward a model capable of answering a wide range of questions
about graphs from diverse applications.
New Architecture for GraphQA. To enable effective and efficient graph QA, even on large graphs,
we propose G-Retriever, a new framework combining the strengths of GNNs, LLMs, and RAG
(Figure 3). Next, we will discuss the motivation, strengths, and details of our model.


</details>

### G-Retriever · 块 6 · 页 2-2 · completed

`chunk_99b18cdbb0bd9a36674e8b314d553ad3`；类型 body；跳过原因 None；2.46s；Token 694/8


<details><summary>完整来源块</summary>

Tackling Hallucination in Graph LLMs. LLMs are prone to hallucination, a phenomenon where the
generated content is factually inaccurate or nonsensical [12]. We validate the presence of this issue in
graph settings. In particular, we employ a baseline method that adapts MiniGPT-4 [57] to graphs,
where a frozen LLM interacts with a trainable GNN that encodes graph data as a soft prompt, as in
GraphToken [31]. Our findings, shown in Table 1, indicate that hallucination, an important problem
in text-based LLMs, is also prevalent in Graph LLMs. This may be attributed to the baseline’s
inability to recall the entire graph structure from a single graph embedding, leading to the generation
of incorrect nodes or edges during the QA task. In contrast, by employing RAG for direct information
retrieval from the actual graph, our G-Retriever mitigates this issue, as substantiated by Table 1.


</details>

### G-Retriever · 块 7 · 页 2-3 · completed

`chunk_5c9e14854565607ec53c355da481c451`；类型 body；跳过原因 None；50.22s；Token 816/220

- 保留（待审）：G-Retriever --HAS_COMPONENT--> RAG component
  - 引文偏移 614:784：G-Retriever overcomes these issues with its RAG component, which allows for effective scaling to larger graphs by selectively retrieving only relevant parts of the graph.
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "RAG component", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "Prize-Collecting Steiner Tree (PCST)", "evidence_quote": "Notably, we formulate subgraph retrieval as a Prize-Collecting Steiner Tree (PCST) problem.", "claim_kind": "author_assertion", "confidence": 1.0}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 8 · 页 3-3 · completed

`chunk_0e365600a243ad5257f9003b561ff2ea`；类型 body；跳过原因 None；2.84s；Token 829/8


<details><summary>完整来源块</summary>

[Incorrect response with hallucinated nodes and edges]
The animal in the bushes is a deer.
Nodes:
* Deer (node 1)
* Bushes (node 2)
Edges:
* Deer →Bushes (edge 1)
* Deer →Grass (edge 2)
* Bushes →Grass (edge 3)
G-Retriever (Ours)
[Correct response with accurate node and edge references]
Based on the information provided in the graph, the animal in the bushes is an elephant.
The nodes that support this answer are:
* Node 1: The elephant is mentioned in the first line of the graph.
The edges that support this answer are:
* The edge connects the elephant to the bushes, indicating that the elephant is in the bushes.
Therefore, the answer to the question is: The animal in the bushes is an elephant.
optimization problem, which takes the neighborhood information into account during retrieval. This
also allows the return of a subgraph most relevant to a query, thereby improving explainability.
The contributions of this paper are outlined as follows:
• Pioneering the integration of Graph RAG. We present the first retrieval approach for
general textual graph tasks, which greatly enhances scalability and efficiency.
• Enabling ‘Chat with Your Graph’. We develop a flexible question answering framework
to handle complex and real-world textual graphs through a unified conversational interface.
• Introducing A Novel GraphQA Benchmark. We introduce a diverse benchmark targeted
at real-world graph question answering, filling a crucial research gap.
• Empirical Findings. We demonstrate the efficiency and effectiveness of G-Retriever in
multiple domains and present the significant finding of hallucination in graph LLMs.
2


</details>

### G-Retriever · 块 9 · 页 3-3 · completed

`chunk_5716891bb093d42ffa4073facdcc97d3`；类型 body；跳过原因 None；2.61s；Token 820/8


<details><summary>完整来源块</summary>

Related Work
Graphs and Large Language Models. A significant body of research has emerged at the intersection
of graph-based techniques and LLMs [30, 24, 15, 44, 54]. This exploration spans diverse aspects,
ranging from the design of general graph models [47, 25, 51, 19, 40, 31], and multi-modal architec-
tures [23, 49] to practical applications. Noteworthy applications include fundamental graph reason-
ing [52, 3, 56], node classification [8, 11, 39, 5, 50, 4, 33], graph classification/regression [32, 55],
and leveraging LLMs for knowledge graph-related tasks [41, 14, 29].
Retrieval-Augmented Generation (RAG). The concept of Retrieval-Augmented Generation, initially
proposed by Lewis et al. [21], has gained increased attention for its ability to mitigate the issue of
hallucination within LLMs and enhance trustworthiness and explainability [7]. Despite its success in
language-related tasks, the application of retrieval-based approaches to general graph tasks remains
largely unexplored. Most existing work focuses primarily on the knowledge graph [38, 1, 36, 16].
Our research is the first to apply a retrieval-based approach to general graph tasks, marking a novel
advancement in the field and demonstrating the versatility of RAG beyond language processing.


</details>

### G-Retriever · 块 10 · 页 3-4 · completed

`chunk_7fad08f1067bacecc294e3e817cc7d59`；类型 body；跳过原因 None；2.69s；Token 863/8


<details><summary>完整来源块</summary>

Parameter-Efficient Fine-Tuning (PEFT). The field of LLMs has witnessed significant advance-
ments through various parameter-efficient fine-tuning techniques. These methodologies have played
a crucial role in refining LLMs, boosting their performance while minimizing the need for extensive
parameter training. Notable among these techniques are prompt tuning, as introduced by Lester
et al. [20], and prefix tuning, proposed by Li and Liang [22]. Furthermore, methods like LoRA [10],
3

and the LLaMA-adapter [53], have been influential. These advancements in PEFT have laid the
foundation for the development of sophisticated multimodal models. Prominent examples in this
domain include MiniGPT-4 [57], LLaVA [26], and NExT-Chat [46]. There are also emerging efforts
in applying PEFT to graph LLMs, such as GraphLLM [3] and GraphToken [31] for basic graph
reasoing tasks and GNP [41] for multi-option QA on knowledge graphs.
3
Formalization
This section establishes the notation and formalizes key concepts related to textual graphs, language
models for text encoding, and large language models and prompt tuning.
Textual Graphs. A textual graph is a graph where nodes and edges possess textual attributes.
Formally, it can be defined as G = (V, E, {xn}n∈V , {xe}e∈E), where V and E represent the sets
of nodes and edges, respectively. Additionally, xn ∈DLn and xe ∈DLe denote sequential text
associate with a node n ∈V or an edge e ∈E, where D represents the vocabulary, and Ln and Le
signify the length of the text associated with the respective node or edge.


</details>

### G-Retriever · 块 11 · 页 4-4 · completed

`chunk_2d2863e6cf527b25ae6c871d76ab83cd`；类型 body；跳过原因 None；125.68s；Token 864/544

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "LLMs for Text Encoding", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "LMs", "evidence_quote": "Language models (LMs) are essential for encoding the text attributes associated with nodes and edges, thereby learning representations that capture their semantic meaning.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Large Language Models and Prompt Tuning", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "LLMs", "evidence_quote": "LLMs have introduced a new paradigm for task-adaptation known as “pre-train, prompt, and predict”.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "LLMs", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "pre-train, prompt, and predict paradigm", "evidence_quote": "LLMs have introduced a new paradigm for task-adaptation known as “pre-train, prompt, and predict”, replacing the traditional “pre-train, fine-tune” paradigm.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `generic_entity`：{"claim_id": "4cb3234ae019732f9aa7e4cfc4123dd84ec42d41fc33a865279896bc4c537a94", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_2d2863e6cf527b25ae6c871d76ab83cd", "subject_type": "Method", "subject": "LLMs for Text Encoding", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "d", "evidence_quote": "where zn is the output of the LM, and d is the dimension of the output vector.", "quote_match_method": "exact", "quote_start": 340, "quote_end": 418, "source_spans": [{"pdf_page": 4, "start_char": 1076, "end_char": 2569, "chunk_start_char": 0, "chunk_end_char": 1493, "block_bboxes": [[108.0, 258.525, 504.67, 301.382], [264.033, 301.437, 504.667, 315.072], [107.641, 320.025, 416.61, 331.712], [108.0, 336.476, 505.771, 401.152], [107.691, 407.347, 504.003, 439.358], [226.35, 456.96, 291.686, 467.894], [294.533, 446.972, 307.265, 464.751], [294.445, 471.18, 307.355, 478.154], [309.011, 456.96, 504.667, 467.894], [108.0, 486.164, 504.0, 508.89]]}], "page_start": 4, "page_end": 4, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "6599fef67ea7dd3542dbfbbb3d456622ac12912689692da825c5ef9830ab50d1", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_2d2863e6cf527b25ae6c871d76ab83cd", "subject_type": "Method", "subject": "Large Language Models and Prompt Tuning", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "θ", "evidence_quote": "The LLM, parameterized by weights θ, takes a sequence of tokens X, and a prompt P as input, and\ngenerates a sequence of tokens Y = {y1, y2, . . . , yr} as output.", "quote_match_method": "whitespace_normalized", "quote_start": 981, "quote_end": 1143, "source_spans": [{"pdf_page": 4, "start_char": 1076, "end_char": 2569, "chunk_start_char": 0, "chunk_end_char": 1493, "block_bboxes": [[108.0, 258.525, 504.67, 301.382], [264.033, 301.437, 504.667, 315.072], [107.641, 320.025, 416.61, 331.712], [108.0, 336.476, 505.771, 401.152], [107.691, 407.347, 504.003, 439.358], [226.35, 456.96, 291.686, 467.894], [294.533, 446.972, 307.265, 464.751], [294.445, 471.18, 307.355, 478.154], [309.011, 456.96, 504.667, 467.894], [108.0, 486.164, 504.0, 508.89]]}], "page_start": 4, "page_end": 4, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Language Models for Text Encoding. In the context of textual graphs, language models (LMs)
are essential for encoding the text attributes associated with nodes and edges, thereby learning
representations that capture their semantic meaning. For a node n with text attributes xn ∈DLn, an
LM encodes these attributes as:
zn = LM(xn) ∈Rd,
(1)
where zn is the output of the LM, and d is the dimension of the output vector.
Large Language Models and Prompt Tuning. LLMs have introduced a new paradigm for task-
adaptation known as “pre-train, prompt, and predict”, replacing the traditional “pre-train, fine-tune”
paradigm. In this paradigm, the LLM is first pre-trained on a large corpus of text data to learn general
language representations. Then, rather than fine-tuning the model on task-specific labeled data, the
model is prompted with a textual prompt that specifies the task and context. Subsequently, the model
generates the output directly based on the prompt and the input.
The LLM, parameterized by weights θ, takes a sequence of tokens X, and a prompt P as input, and
generates a sequence of tokens Y = {y1, y2, . . . , yr} as output. Formally, the probability distribution
of the output sequence given the concatenated input sequence and prompt, i.e., [P; X], is defined as
pθ(Y |[P; X]) =
r
Y
i=1
pθ(yi|y<i, [P; X]).
(2)
Here, y<i represents the prefix of sequence y up to position i −1, and p(yi|y<i, [P; X]) represents
the probability of generating token yi given y<i and [P; X].


</details>

### G-Retriever · 块 12 · 页 4-5 · completed

`chunk_169332db0b56d09ba086374fa84a2040`；类型 body；跳过原因 None；109.64s；Token 763/478

- 保留（待审）：text embedder --IMPLEMENTS--> embedding space
  - 引文偏移 191:240：where dl is the dimension of the embedding space.
- 拒绝 `control_object_not_parameter`：{"claim_id": "accb6e6a978f60a2ea5b7f58bc8efe68fdf45d02baa68b40259faec5399b66d6", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_169332db0b56d09ba086374fa84a2040", "subject_type": "Method", "subject": "g-retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "Pe", "evidence_quote": "Soft prompts can be represented as parameters\nPe ∈Rq×dl, where q is the length of the prompt.", "quote_match_method": "whitespace_normalized", "quote_start": 241, "quote_end": 334, "source_spans": [{"pdf_page": 4, "start_char": 2569, "end_char": 3658, "chunk_start_char": 0, "chunk_end_char": 1089, "block_bboxes": [[107.641, 513.591, 505.245, 590.939], [108.0, 608.276, 291.106, 620.231], [108.0, 633.684, 503.999, 665.473], [108.0, 681.015, 185.22, 690.977], [108.0, 701.464, 505.244, 722.407], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 5, "start_char": 0, "end_char": 95, "chunk_start_char": 1090, "chunk_end_char": 1185, "block_bboxes": [[185.448, 79.054, 426.244, 89.017], [117.51, 101.084, 452.891, 108.232]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `control_object_not_parameter`：{"claim_id": "e833939c4e90edee8dc77868ca02e6f83c862237580b1f469da31bc81bfdcb15", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_169332db0b56d09ba086374fa84a2040", "subject_type": "Method", "subject": "g-retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "dl", "evidence_quote": "where dl is the dimension of the embedding space.", "quote_match_method": "exact", "quote_start": 191, "quote_end": 240, "source_spans": [{"pdf_page": 4, "start_char": 2569, "end_char": 3658, "chunk_start_char": 0, "chunk_end_char": 1089, "block_bboxes": [[107.641, 513.591, 505.245, 590.939], [108.0, 608.276, 291.106, 620.231], [108.0, 633.684, 503.999, 665.473], [108.0, 681.015, 185.22, 690.977], [108.0, 701.464, 505.244, 722.407], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 5, "start_char": 0, "end_char": 95, "chunk_start_char": 1090, "chunk_end_char": 1185, "block_bboxes": [[185.448, 79.054, 426.244, 89.017], [117.51, 101.084, 452.891, 108.232]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "2c8903976d86ada7eb2c305196182a6258e87db685d1ac9d55c4d6ec75e85916", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_169332db0b56d09ba086374fa84a2040", "subject_type": "Method", "subject": "g-retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "text embedder", "evidence_quote": "Given a series of p tokens\nX = {x1, x2, . . . , xp}, after being processed by the text embedder, it forms a matrix Xe ∈Rp×dl", "quote_match_method": "whitespace_normalized", "quote_start": 65, "quote_end": 189, "source_spans": [{"pdf_page": 4, "start_char": 2569, "end_char": 3658, "chunk_start_char": 0, "chunk_end_char": 1089, "block_bboxes": [[107.641, 513.591, 505.245, 590.939], [108.0, 608.276, 291.106, 620.231], [108.0, 633.684, 503.999, 665.473], [108.0, 681.015, 185.22, 690.977], [108.0, 701.464, 505.244, 722.407], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 5, "start_char": 0, "end_char": 95, "chunk_start_char": 1090, "chunk_end_char": 1185, "block_bboxes": [[185.448, 79.054, 426.244, 89.017], [117.51, 101.084, 452.891, 108.232]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "9f34dbb4e2242cdfc0d990f0c677449951b467e9ee740658f615c25859c5d941", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_169332db0b56d09ba086374fa84a2040", "subject_type": "Method", "subject": "g-retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "self-attention layers in LLM", "evidence_quote": "This combined matrix is processed by the\nself-attention layers in LLM as usual.", "quote_match_method": "whitespace_normalized", "quote_start": 437, "quote_end": 516, "source_spans": [{"pdf_page": 4, "start_char": 2569, "end_char": 3658, "chunk_start_char": 0, "chunk_end_char": 1089, "block_bboxes": [[107.641, 513.591, 505.245, 590.939], [108.0, 608.276, 291.106, 620.231], [108.0, 633.684, 503.999, 665.473], [108.0, 681.015, 185.22, 690.977], [108.0, 701.464, 505.244, 722.407], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 5, "start_char": 0, "end_char": 95, "chunk_start_char": 1090, "chunk_end_char": 1185, "block_bboxes": [[185.448, 79.054, 426.244, 89.017], [117.51, 101.084, 452.891, 108.232]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Soft prompt tuning eliminates the need for manual prompt design. Given a series of p tokens
X = {x1, x2, . . . , xp}, after being processed by the text embedder, it forms a matrix Xe ∈Rp×dl,
where dl is the dimension of the embedding space. Soft prompts can be represented as parameters
Pe ∈Rq×dl, where q is the length of the prompt. The prompt is then concatenated with the embedded
input, forming a single matrix [Pe; Xe] ∈R(q+p)×dl. This combined matrix is processed by the
self-attention layers in LLM as usual. Training involves maximizing the likelihood of Y through
backpropagation, with gradient updates applied solely to Pe, while θ remains fixed.
4
Proposed GraphQA Benchmark
Our GraphQA represents a comprehensive and diverse benchmark for graph question-answering. It
is tailored to assess the capabilities of models in answering a wide range of questions about graphs
across diverse domains.
4.1
Data Format
Each entry in the GraphQA benchmark consists of a textual graph, a question related to the graph,
and one or more corresponding answers, as illustrated in Figure 2.
4

Table 2: Summary of datasets used in GraphQA benchmark.
Dataset
ExplaGraphs
SceneGraphs
WebQSP


</details>

### G-Retriever · 块 13 · 页 5-5 · completed

`chunk_9523f0c45d52efdd32deb8aeebf8264b`；类型 body；跳过原因 None；3.84s；Token 976/8


<details><summary>完整来源块</summary>

#Graphs
2,766
100,000
4,737
Avg. #Nodes
5.17
19.13
1370.89
Avg. #Edges
4.25
68.44
4252.37
Node Attribute
Commonsense concepts
Object attributes (e.g., color, shape)
Entities in Freebase
Edge Attribute
Commonsense relations
Relations (e.g., actions, spatial relations)
Relations in Freebase
Task
Common sense reasoning
Scene graph question answering
Knowledge based question answering
Evaluation Matrix
Accuracy
Accuracy
Hit@1
    counter
desire
Answer
Textualized Graph
node_id, node_attr
0, women and men
1, citizens
2, have same rights
3, women
4, help the country
5, be in combat
src, edge_attr, dst
0, is a,1
1, causes, 2
2, causes, 3
3, capable of, 4
4, desires, 5
citizens
women and
men
women
help the country
have same rights
is a
capable of
causes
Explanation Graph
be in combat
causes
Question
Arguement 1: Women should not be in combat.
Arguement 2: Women and men have the same rights.
Question: Do argument 1 and argument 2 support or counter each other?
Answer in one word in the form of 'support' or 'counter'.
Scene Graph
woman
computer
in front of
person
sitting
to the right of
node_id, node_attr
2, name: computer; (x,y,w,h): (8, 119, 34, 32)
3, name: person; attribute: sitting; (x,y,w,h): (169, 75, 49, 40)
15, name: woman; (x,y,w,h): (255, 18, 235, 292)
src, edge_attr, dst
15, to the right of, 3
2, in front of, 3
Answer
  yes
Textualized Graph
Question


</details>

### G-Retriever · 块 14 · 页 5-5 · completed

`chunk_2e822aca3c5121569377d101d6b5cd20`；类型 body；跳过原因 None；2.75s；Token 825/8


<details><summary>完整来源块</summary>

Question: Is there a woman to the right of the person behind the
computer?
justin bieber
jeremy
bieber
jaxon bieber
Answer
  jaxon bieber
Textualized Graph
node_id, node_attr
15, justin bieber
294, jaxon bieber
356, jeremy bieber
551, m.0gxnnwp
src, edge_attr, dst
15, people.person.parents, 356
15, people.person.sibling_s, 551
356, people.person.children, 294
551, people.sibling_relationship.sibling, 294
m.0gxnnwp
Knowledge Graph
sibling_s
sibling
children
parents
Question
Question: what is the name of justin bieber brother
Figure 2: Illustrative examples from the GraphQA benchmark datasets.
Textual Graphs. The textual graph is converted into a natural language format, resulting in a list of
nodes and edges, akin to a CSV file format. It is important to note that while multiple methods exist
for textualizing a graph, our focus is not on identifying the optimal solution. Instead, we prioritize
a straightforward yet empirically effective approach for representing graphs in natural language,
facilitating the benchmark’s use in diverse GraphQA scenarios.
Questions and Answers. Questions are designed to explore specific elements or relationships within
the graph. Answers, residing within the attributes of nodes or edges, often require multi-hop reasoning
for accurate identification.
4.2
Description of Datasets


</details>

### G-Retriever · 块 15 · 页 5-5 · completed

`chunk_e3039cc70fdc7caf88ff60d3a386ed29`；类型 body；跳过原因 None；2.60s；Token 796/8


<details><summary>完整来源块</summary>

The GraphQA benchmark integrates three existing datasets: ExplaGraphs, SceneGraphs, and
WebQSP. Table 2 presents the summary statistics of these datasets. It is important to note that these
datasets were not originally developed for this work. However, a significant contribution of our
research is the standardization and processing of these diverse datasets into a uniform data format
suitable for the GraphQA benchmark. These datasets, previously utilized in different contexts, are
reintroduced with a new focus tailored for GraphQA. For a detailed comparison with the original
datasets, see the Appendix C.
ExplaGraphs is a dataset for generative commonsense reasoning, focusing on creating explanation
graphs for stance prediction in debates. It offers detailed, unambiguous commonsense-augmented
graphs to evaluate arguments supporting or refuting a belief. The primary task is to assess whether
arguments are supportive or contradictory, using accuracy as the metric. We have converted the
triplet-form provided in Saha et al. [35] into a standard graph format.
SceneGraphs, a visual question answering dataset, includes 100,000 scene graphs. Each graph
details objects, attributes, and relations within an image. This dataset challenges users with tasks
requiring spatial understanding and multi-step inference. The task is to answer open-ended questions
based on a textual description of a scene graph, evaluated on accuracy. We have sampled from the
GQA dataset [13] and constructed standard graphs from the provided JSON files.


</details>

### G-Retriever · 块 16 · 页 5-6 · completed

`chunk_dbf906122a150b7fb99efaf3217e4263`；类型 body；跳过原因 None；2.71s；Token 901/8


<details><summary>完整来源块</summary>

WebQSP is a large-scale multi-hop knowledge graph QA dataset consisting of 4,737 questions. It was
proposed by Yih et al. [48] and, following Luo et al. [28], utilizes a subset of Freebase, encompassing
facts within 2-hops of entities mentioned in the questions. The task involves answering questions that
5

Graph Encoder
Question: What is the name
of justin bieber brother?
Step 1: Indexing
Storage
Step 2: Retrieval
Step 3: Subgraph Construction
LLM
(Self Attention Layers)
LLM
(Text Embedder)
Step 4: Generation
bieber
jaxon
Projection
justin
bieber
jeremy
bieber
parent
jaxon
bieber
children
sibling
m.0gxnnwp
sibling
all bad
album
record
producer
profession
canada
nationality
male
gender
LM
node attributes
justin bieber, this is justin bieber, jeremy bieber, 
justin bieber fan club, justin ...
sibling, sibling_s, hangout, friendship, friend ...
LM
LM
justin
bieber
jeremy
bieber
parent
jaxon
bieber
children
sibling
m.0gxnnwp
sibling
node_id, node_attr
15, justin bieber
294, jaxon bieber
356, jeremy bieber
551, m.0gxnnwp
src, edge_attr, dst
294, parents, 356
356, children, 15
551, sibling, 294
551, sibling, 15
Question: What is the name
of justin bieber brother?
Answer:
edge attributes
frozen
trainable


</details>

### G-Retriever · 块 17 · 页 6-6 · completed

`chunk_2da94a87e97c2e0f30e8eec5659e202d`；类型 body_mixed；跳过原因 None；135.46s；Token 826/589

- 保留（待审）：G-Retriever --HAS_COMPONENT--> Indexing
  - 引文偏移 1317:1439：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- 保留（待审）：G-Retriever --HAS_COMPONENT--> Retrieval
  - 引文偏移 1317:1439：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- 保留（待审）：G-Retriever --HAS_COMPONENT--> Subgraph Construction
  - 引文偏移 1317:1439：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- 保留（待审）：G-Retriever --HAS_COMPONENT--> Generation
  - 引文偏移 1317:1439：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- 保留（待审）：Retrieval --IMPLEMENTS--> PCST optimization problem for subgraph retrieval
  - 引文偏移 1137:1224：To adapt RAG to graphs, we formulate subgraph retrieval as a PCST optimization problem.
- 拒绝 `implementation_object_not_named_technology`：{"claim_id": "4b335ebcd016215a9dd162efc323b93648fad37053d619b6c9dc5ca0dab5e2a4", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_2da94a87e97c2e0f30e8eec5659e202d", "subject_type": "Component", "subject": "Indexing", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "Graph indexing for efficient query processing", "evidence_quote": "Indexing: Graphs are indexed for efficient query\nprocessing;", "quote_match_method": "whitespace_normalized", "quote_start": 51, "quote_end": 111, "source_spans": [{"pdf_page": 6, "start_char": 909, "end_char": 2444, "chunk_start_char": 0, "chunk_end_char": 1535, "block_bboxes": [[108.0, 216.502, 504.353, 270.219], [108.0, 292.552, 503.997, 313.499], [108.0, 330.132, 187.371, 342.087], [107.641, 354.551, 505.247, 430.106], [107.641, 436.402, 505.74, 457.379], [108.0, 471.631, 168.064, 481.593]]}], "page_start": 6, "page_end": 6, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 18 · 页 6-7 · completed

`chunk_8c5476c0307c733adb60d1afe861e4d2`；类型 body；跳过原因 None；118.50s；Token 836/513

- 保留（待审）：node and graph embeddings generation --IMPLEMENTS--> pre-trained LM
  - 引文偏移 229:338：Utilizing a pre-trained LM, such as SentenceBert [34], we apply the LM to xn, yielding the representation zn:
- 保留（待审）：g-retriever --HAS_COMPONENT--> k-nearest neighbors retrieval approach
  - 引文偏移 683:806：Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors retrieval approach.
- 拒绝 `relation_signature_not_allowed`：{"subject_type": "Component", "subject": "k-nearest neighbors retrieval approach", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "k", "evidence_quote": "This method yields a set of ‘relevant nodes/edges’ based on the similarity between the query and each node or edge.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "6c7158ae81792bca8be6584b16c1051c6b953b689daceff88a80d43723926028", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_8c5476c0307c733adb60d1afe861e4d2", "subject_type": "Method", "subject": "g-retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "node and graph embeddings generation", "evidence_quote": "We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.", "quote_match_method": "exact", "quote_start": 0, "quote_end": 92, "source_spans": [{"pdf_page": 6, "start_char": 2444, "end_char": 3469, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[107.532, 491.621, 505.745, 512.568], [107.691, 516.443, 504.002, 540.477], [264.033, 545.592, 504.667, 559.227], [107.641, 564.665, 505.74, 585.768], [108.0, 599.995, 169.449, 609.957], [108.0, 619.83, 503.996, 640.932], [265.056, 639.471, 504.667, 653.105], [108.0, 661.736, 504.002, 693.441], [245.833, 700.025, 504.667, 726.771], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 7, "start_char": 0, "end_char": 417, "chunk_start_char": 1026, "chunk_end_char": 1443, "block_bboxes": [[107.641, 74.177, 504.344, 118.591], [108.0, 131.379, 230.889, 141.341]]}], "page_start": 6, "page_end": 7, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `implementation_object_not_named_technology`：{"claim_id": "b7a41abef009c90cdcf96cac3755b3bc6b7d5b62dd2062a3cdb8fbacb78733d7", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_8c5476c0307c733adb60d1afe861e4d2", "subject_type": "Component", "subject": "k-nearest neighbors retrieval approach", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "cosine similarity function", "evidence_quote": "We use the cosine similarity\nfunction, cos(·, ·), to measure the similarity between the query representation and the node/edge\nembeddings.", "quote_match_method": "whitespace_normalized", "quote_start": 1097, "quote_end": 1235, "source_spans": [{"pdf_page": 6, "start_char": 2444, "end_char": 3469, "chunk_start_char": 0, "chunk_end_char": 1025, "block_bboxes": [[107.532, 491.621, 505.745, 512.568], [107.691, 516.443, 504.002, 540.477], [264.033, 545.592, 504.667, 559.227], [107.641, 564.665, 505.74, 585.768], [108.0, 599.995, 169.449, 609.957], [108.0, 619.83, 503.996, 640.932], [265.056, 639.471, 504.667, 653.105], [108.0, 661.736, 504.002, 693.441], [245.833, 700.025, 504.667, 726.771], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 7, "start_char": 0, "end_char": 417, "chunk_start_char": 1026, "chunk_end_char": 1443, "block_bboxes": [[107.641, 74.177, 504.344, 118.591], [108.0, 131.379, 230.889, 141.341]]}], "page_start": 6, "page_end": 7, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 19 · 页 7-7 · completed

`chunk_04c0673f276b70d320674636d537dc80`；类型 body；跳过原因 None；84.60s；Token 866/370

- 保留（待审）：node prize assignment --IMPLEMENTS--> cosine similarity
  - 引文偏移 967:1088：Our approach assigns higher prize values to nodes and edges more relevant to the query, as measured by cosine similarity.
- 拒绝 `relation_signature_not_allowed`：{"subject_type": "Component", "subject": "node prize assignment", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "k", "evidence_quote": "Specifically, the top k nodes/edges are assigned descending prize values from k down to 1, with the rest assigned zero.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "06de2f4d251abfcb78e0d6745d87802f3d29f891275432a3fea27a38e2f65cc3", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_04c0673f276b70d320674636d537dc80", "subject_type": "Method", "subject": "Prize-Collecting Steiner Tree (PCST)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "node prize assignment", "evidence_quote": "The node prize assignment is as follows:", "quote_match_method": "exact", "quote_start": 1209, "quote_end": 1249, "source_spans": [{"pdf_page": 7, "start_char": 417, "end_char": 2023, "chunk_start_char": 0, "chunk_end_char": 1606, "block_bboxes": [[107.641, 151.52, 505.245, 237.771], [108.0, 244.107, 504.344, 297.796], [195.1, 312.629, 239.265, 322.822], [242.027, 305.745, 504.667, 329.495], [108.0, 336.619, 505.29, 359.067], [187.776, 366.935, 248.014, 378.997], [212.323, 379.647, 254.007, 394.01], [258.478, 366.502, 272.874, 376.465], [255.667, 382.954, 274.929, 390.585], [277.341, 368.804, 320.948, 378.997], [325.973, 366.502, 340.369, 376.465], [323.161, 382.954, 342.423, 390.585], [344.835, 368.675, 504.667, 378.997], [107.641, 399.878, 131.98, 409.841]]}], "page_start": 7, "page_end": 7, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "607e9d2ec68206dffaed4c0c82935cb43e1ceff6a27a699d73951d6431aa1c81", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_04c0673f276b70d320674636d537dc80", "subject_type": "Method", "subject": "Prize-Collecting Steiner Tree (PCST)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "edge prize assignment", "evidence_quote": "Edge prizes are assigned similarly.", "quote_match_method": "exact", "quote_start": 1320, "quote_end": 1355, "source_spans": [{"pdf_page": 7, "start_char": 417, "end_char": 2023, "chunk_start_char": 0, "chunk_end_char": 1606, "block_bboxes": [[107.641, 151.52, 505.245, 237.771], [108.0, 244.107, 504.344, 297.796], [195.1, 312.629, 239.265, 322.822], [242.027, 305.745, 504.667, 329.495], [108.0, 336.619, 505.29, 359.067], [187.776, 366.935, 248.014, 378.997], [212.323, 379.647, 254.007, 394.01], [258.478, 366.502, 272.874, 376.465], [255.667, 382.954, 274.929, 390.585], [277.341, 368.804, 320.948, 378.997], [325.973, 366.502, 340.369, 376.465], [323.161, 382.954, 342.423, 390.585], [344.835, 368.675, 504.667, 378.997], [107.641, 399.878, 131.98, 409.841]]}], "page_start": 7, "page_end": 7, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 20 · 页 7-7 · completed

`chunk_5832b6bfb3218fc28548dbb991a42540`；类型 body；跳过原因 None；94.07s；Token 839/410

- 保留（待审）：g-retriever --HAS_COMPONENT--> Graph Encoder
  - 引文偏移 1072:1198：We use a graph encoder to model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].
- 保留（待审）：Graph Encoder --IMPLEMENTS--> Graph Attention Network (GAT)
  - 引文偏移 1072:1198：We use a graph encoder to model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].
- 保留（待审）：Projection Layer --IMPLEMENTS--> multilayer perceptron (MLP)
  - 引文偏移 1413:1516：We incorporate a multilayer perceptron (MLP) to align the graph token with the vector space of the LLM:
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "914e803a4b2465bfc72d680f4bff76e838e1a421905179624248daa04b345dbf", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_5832b6bfb3218fc28548dbb991a42540", "subject_type": "Method", "subject": "g-retriever", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Projection Layer", "evidence_quote": "We incorporate a multilayer perceptron (MLP) to align the graph token with the\nvector space of the LLM:", "quote_match_method": "whitespace_normalized", "quote_start": 1413, "quote_end": 1516, "source_spans": [{"pdf_page": 7, "start_char": 2023, "end_char": 3540, "chunk_start_char": 0, "chunk_end_char": 1517, "block_bboxes": [[108.0, 410.428, 504.667, 436.729], [107.691, 441.585, 505.389, 538.896], [108.0, 553.177, 213.703, 563.14], [108.0, 571.643, 505.744, 605.024], [236.931, 611.056, 504.667, 624.69], [108.0, 630.433, 489.146, 642.121], [107.751, 646.942, 504.003, 667.924]]}], "page_start": 7, "page_end": 7, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

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


</details>

### G-Retriever · 块 21 · 页 7-8 · completed

`chunk_33c8e2f0ed11ba682036fc475dffc954`；类型 body；跳过原因 None；122.74s；Token 878/519

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Text Embedder", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "text embedder", "evidence_quote": "We map the result to an embedding ht using a text embedder, which is the first layer of a pretrained and frozen LLM:", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "text embedder", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "pretrained and frozen LLM", "evidence_quote": "We map the result to an embedding ht using a text embedder, which is the first layer of a pretrained and frozen LLM:", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "107e4d42cacbe869dfa4d3f664fe36c47dc7698166455a9869853a7c85f69b69", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_33c8e2f0ed11ba682036fc475dffc954", "subject_type": "Method", "subject": "LLM Generation with Graph Prompt Tuning", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "graph token ˆhg", "evidence_quote": "The final stage involves generating the answer Y\ngiven the graph token ˆhg, acting as a soft prompt, and the text embedder output ht.", "quote_match_method": "whitespace_normalized", "quote_start": 863, "quote_end": 996, "source_spans": [{"pdf_page": 7, "start_char": 3540, "end_char": 3825, "chunk_start_char": 0, "chunk_end_char": 285, "block_bboxes": [[107.641, 667.803, 504.668, 696.604], [107.671, 701.368, 503.997, 722.384], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 8, "start_char": 0, "end_char": 1199, "chunk_start_char": 286, "chunk_end_char": 1485, "block_bboxes": [[108.0, 74.048, 505.744, 118.591], [107.641, 118.842, 504.668, 144.127], [108.0, 150.323, 503.998, 195.035], [203.353, 204.585, 289.783, 217.818], [292.633, 196.336, 305.365, 214.114], [292.545, 220.544, 305.455, 227.518], [307.111, 203.824, 504.668, 217.818], [107.641, 229.125, 505.24, 267.744], [108.0, 282.166, 191.017, 294.121]]}], "page_start": 7, "page_end": 8, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "3bf57cd1c09b78f134221dab95207e1feb357b627545503811353cab54dfcfb6", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_33c8e2f0ed11ba682036fc475dffc954", "subject_type": "Method", "subject": "LLM Generation with Graph Prompt Tuning", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "text embedder output ht", "evidence_quote": "The final stage involves generating the answer Y\ngiven the graph token ˆhg, acting as a soft prompt, and the text embedder output ht.", "quote_match_method": "whitespace_normalized", "quote_start": 863, "quote_end": 996, "source_spans": [{"pdf_page": 7, "start_char": 3540, "end_char": 3825, "chunk_start_char": 0, "chunk_end_char": 285, "block_bboxes": [[107.641, 667.803, 504.668, 696.604], [107.671, 701.368, 503.997, 722.384], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 8, "start_char": 0, "end_char": 1199, "chunk_start_char": 286, "chunk_end_char": 1485, "block_bboxes": [[108.0, 74.048, 505.744, 118.591], [107.641, 118.842, 504.668, 144.127], [108.0, 150.323, 503.998, 195.035], [203.353, 204.585, 289.783, 217.818], [292.633, 196.336, 305.365, 214.114], [292.545, 220.544, 305.455, 227.518], [307.111, 203.824, 504.668, 217.818], [107.641, 229.125, 505.24, 267.744], [108.0, 282.166, 191.017, 294.121]]}], "page_start": 7, "page_end": 8, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `subject_not_method_anchored`：{"claim_id": "015bd2baef43365cfb4670fd7a90e2b025388b32506f6a13532c29d5dcc50e1d", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_33c8e2f0ed11ba682036fc475dffc954", "subject_type": "Method", "subject": "LLM Generation with Graph Prompt Tuning", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "θ", "evidence_quote": "These inputs are\nfed through the self-attention layers of a pretrained frozen LLM, with parameter θ.", "quote_match_method": "whitespace_normalized", "quote_start": 997, "quote_end": 1097, "source_spans": [{"pdf_page": 7, "start_char": 3540, "end_char": 3825, "chunk_start_char": 0, "chunk_end_char": 285, "block_bboxes": [[107.641, 667.803, 504.668, 696.604], [107.671, 701.368, 503.997, 722.384], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 8, "start_char": 0, "end_char": 1199, "chunk_start_char": 286, "chunk_end_char": 1485, "block_bboxes": [[108.0, 74.048, 505.744, 118.591], [107.641, 118.842, 504.668, 144.127], [108.0, 150.323, 503.998, 195.035], [203.353, 204.585, 289.783, 217.818], [292.633, 196.336, 305.365, 214.114], [292.545, 220.544, 305.455, 227.518], [307.111, 203.824, 504.668, 217.818], [107.641, 229.125, 505.24, 267.744], [108.0, 282.166, 191.017, 294.121]]}], "page_start": 7, "page_end": 8, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

ˆhg = MLPϕ2(hg) ∈Rdl,
(10)
where dl is the dimension of the LLM’s hidden embedding.
Text Embedder. To leverage the text-reasoning capabilities of LLMs, we transform the retrieved
subgraph S∗into a textual format. This transformation involves flattening the textual attributes of the
7

nodes and edges, as illustrated in the green box in Figure 2. We refer to this operation as textualize(·).
Subsequently, we combine the textualized graph with the query to generate a response. Let xq denote
the query; we concatenate it with the textualized graph textualize(S∗). We then map the result to an
embedding ht using a text embedder, which is the first layer of a pretrained and frozen LLM:
ht = TextEmbedder([textualize(S∗); xq]) ∈RL×dl,
(11)
where [; ] represents the concatenation operation, and L is the number of tokens.
LLM Generation with Graph Prompt Tuning. The final stage involves generating the answer Y
given the graph token ˆhg, acting as a soft prompt, and the text embedder output ht. These inputs are
fed through the self-attention layers of a pretrained frozen LLM, with parameter θ. The generation
process is represented as follows:
pθ,ϕ1,ϕ2(Y |S∗, xq) =
r
Y
i=1
pθ,ϕ1,ϕ2(yi|y<i, [ˆhg; ht]),
(12)
where [ˆhg; ht] concatenates the graph token ˆhg and the text embedder output ht. While θ is frozen,
the graph token ˆhg receives gradients, enabling the optimization of the parameters of the graph
encoder ϕ1 and the projection layer ϕ2 through standard backpropagation.
6


</details>

### G-Retriever · 块 22 · 页 8-8 · completed

`chunk_255b9d4a6fbbac0cf6621acf84251f72`；类型 body；跳过原因 None；98.06s；Token 743/425

- 保留（待审）：g-retriever --HAS_COMPONENT--> SentenceBert [34]
  - 引文偏移 33:129：In the indexing step, we use SentenceBert [34] as the LM to encode all node and edge attributes.
- 保留（待审）：g-retriever --HAS_COMPONENT--> Llama2-7b [42]
  - 引文偏移 130:251：In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.
- 保留（待审）：g-retriever --HAS_COMPONENT--> Graph Transformer [37]
  - 引文偏移 130:251：In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.
- 保留（待审）：LLM --IMPLEMENTS--> LoRA [10]
  - 引文偏移 555:604：3) Tuned LLM: Fine-tuning the LLM with LoRA [10].

<details><summary>完整来源块</summary>

Experiments
6.1
Experiment Setup
In the indexing step, we use SentenceBert [34] as the LM to encode all node and edge attributes. In
the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37]
as the graph encoder. Additional details are provided in Appendix B.1.
6.2
Main Results
In our experiments, we consider three model configurations: 1) Inference-only: Using a frozen LLM
for direct question answering; 2) Frozen LLM w/ prompt tuning (PT): Keeping the parameters of the
LLM frozen and adapting only the prompt; 3) Tuned LLM: Fine-tuning the LLM with LoRA [10].
We provide more details in Appendix B.2.
Table 3: Performance comparison across ExplaGraphs, SceneGraphs, and WebQSP datasets for
different configurations, including Inference-only, Frozen LLM with prompt tuning (PT), and Tuned
LLM settings. Mean scores and standard deviations (mean ± std) are presented. The first best result
for each task is highlighted in bold and the second best result is highlighted with an underline.
Setting


</details>

### G-Retriever · 块 23 · 页 8-9 · completed

`chunk_e2737c14a5cd36e6bd408af049fd0aac`；类型 body；跳过原因 None；24.52s；Token 1070/100

- 拒绝 `control_object_not_parameter`：{"claim_id": "d1678f25fdac7a307561d4c7a27b5e1a47d019263738d358a0c209c7d2632d8c", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_e2737c14a5cd36e6bd408af049fd0aac", "subject_type": "Method", "subject": "G-Retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "LoRA", "evidence_quote": "Furthermore, when tuned with\nLoRA, G-Retriever achieves the best performance.", "quote_match_method": "whitespace_normalized", "quote_start": 1126, "quote_end": 1203, "source_spans": [{"pdf_page": 8, "start_char": 2238, "end_char": 3444, "chunk_start_char": 0, "chunk_end_char": 1206, "block_bboxes": [[116.201, 498.241, 467.855, 507.431], [116.201, 528.353, 168.977, 537.319], [198.537, 513.409, 463.799, 552.263], [116.201, 573.409, 186.184, 582.375], [198.537, 558.465, 476.415, 597.593], [116.201, 613.483, 159.876, 622.449], [198.537, 603.521, 476.444, 632.686], [107.641, 647.005, 505.742, 722.407], [303.509, 742.332, 308.49, 752.295]]}, {"pdf_page": 9, "start_char": 0, "end_char": 119, "chunk_start_char": 1207, "chunk_end_char": 1326, "block_bboxes": [[182.35, 79.054, 429.343, 89.017], [130.164, 100.968, 446.349, 114.916]]}], "page_start": 8, "page_end": 9, "section": "Method", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Method
ExplaGraphs
SceneGraphs
WebQSP
Inference-only
Zero-shot
0.5650
0.3974
41.06
Zero-CoT [18]
0.5704
0.5260
51.30
CoT-BAG [44]
0.5794
0.5680
39.60
KAPING [1]
0.6227
0.4375
52.64
Frozen LLM w/ PT
Prompt tuning
0.5763 ± 0.0243
0.6341 ± 0.0024
48.34 ± 0.64
GraphToken [31]
0.8508 ± 0.0551
0.4903 ± 0.0105
57.05 ± 0.74
G-Retriever
0.8516 ± 0.0092
0.8131 ± 0.0162
70.49 ± 1.21
∆Prompt tuning
↑47.77%
↑28.23%
↑45.81%
Tuned LLM
LoRA
0.8538 ± 0.0353
0.7862 ± 0.0031
66.03 ± 0.47
G-Retriever w/ LoRA
0.8705 ± 0.0329
0.8683 ± 0.0072
73.79 ± 0.70
∆LoRA
↑1.95%
↑11.74%
↑10.44%
Table 3 demonstrates the effectiveness of our method across three datasets in various configurations.
In the inference-only setting, G-Retriever surpasses all baselines. Notably, LLM can perform even
better when no graph knowledge is provided (i.e., question only), which might be attributed to the
complexity and potential noise in the knowledge. For frozen LLM with prompt tuning, G-Retriever
outperforms traditional prompt tuning and GraphToken [31], a graph prompt tuning-based method,
with average performance increases of 40.6% and 30.8% respectively. Furthermore, when tuned with
LoRA, G-Retriever achieves the best performance.
8

Table 4: Retrieval on graphs significantly improves efficiency.
Dataset
Before Retrieval (Avg.)
After Retrieval (Avg.)


</details>

### G-Retriever · 块 24 · 页 9-9 · completed

`chunk_aba70e6f2f67df9b074a9e14ead47b00`；类型 body；跳过原因 None；76.52s；Token 924/332

- 拒绝 `control_object_not_parameter`：{"claim_id": "b60cbbd20c999f066f28f33093beacae6b2c747d163ceabc93bf738bb5ca58e0", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_aba70e6f2f67df9b074a9e14ead47b00", "subject_type": "Method", "subject": "G-Retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "tokens", "evidence_quote": "Implementing our graph-based\nretrieval significantly decreases the number of tokens required to describe the graphs in text, reduces\nthe number of nodes in graphs, and speeds up the training process.", "quote_match_method": "whitespace_normalized", "quote_start": 663, "quote_end": 862, "source_spans": [{"pdf_page": 9, "start_char": 119, "end_char": 1326, "chunk_start_char": 0, "chunk_end_char": 1207, "block_bboxes": [[193.888, 115.937, 479.54, 124.903], [130.164, 130.781, 481.836, 150.258], [107.691, 173.694, 287.85, 194.889], [194.333, 206.433, 279.857, 215.558], [114.136, 221.76, 253.608, 250.651], [303.029, 173.769, 490.826, 183.98], [303.083, 195.475, 490.444, 204.817], [303.083, 210.527, 488.798, 249.705], [108.0, 277.619, 221.374, 287.581], [107.691, 298.275, 505.246, 362.783], [108.0, 378.665, 246.659, 388.627]]}], "page_start": 9, "page_end": 9, "section": "Method", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `control_object_not_parameter`：{"claim_id": "ce4c98aa0f5a05f96b234c6fa1c4c16f2d0147ebc0024805f4636cabd6465b3a", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_aba70e6f2f67df9b074a9e14ead47b00", "subject_type": "Method", "subject": "G-Retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "nodes", "evidence_quote": "Implementing our graph-based\nretrieval significantly decreases the number of tokens required to describe the graphs in text, reduces\nthe number of nodes in graphs, and speeds up the training process.", "quote_match_method": "whitespace_normalized", "quote_start": 663, "quote_end": 862, "source_spans": [{"pdf_page": 9, "start_char": 119, "end_char": 1326, "chunk_start_char": 0, "chunk_end_char": 1207, "block_bboxes": [[193.888, 115.937, 479.54, 124.903], [130.164, 130.781, 481.836, 150.258], [107.691, 173.694, 287.85, 194.889], [194.333, 206.433, 279.857, 215.558], [114.136, 221.76, 253.608, 250.651], [303.029, 173.769, 490.826, 183.98], [303.083, 195.475, 490.444, 204.817], [303.083, 210.527, 488.798, 249.705], [108.0, 277.619, 221.374, 287.581], [107.691, 298.275, 505.246, 362.783], [108.0, 378.665, 246.659, 388.627]]}], "page_start": 9, "page_end": 9, "section": "Method", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `control_object_not_parameter`：{"claim_id": "b7082cf5fc2fe85210777c520a53c4d5350f9ebbff96f89975b4724b714e0bdb", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_42a876c95c3fe85af679c0dbc03a8a7d", "paper_title": "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering", "chunk_id": "chunk_aba70e6f2f67df9b074a9e14ead47b00", "subject_type": "Method", "subject": "G-Retriever", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "training time", "evidence_quote": "Implementing our graph-based\nretrieval significantly decreases the number of tokens required to describe the graphs in text, reduces\nthe number of nodes in graphs, and speeds up the training process.", "quote_match_method": "whitespace_normalized", "quote_start": 663, "quote_end": 862, "source_spans": [{"pdf_page": 9, "start_char": 119, "end_char": 1326, "chunk_start_char": 0, "chunk_end_char": 1207, "block_bboxes": [[193.888, 115.937, 479.54, 124.903], [130.164, 130.781, 481.836, 150.258], [107.691, 173.694, 287.85, 194.889], [194.333, 206.433, 279.857, 215.558], [114.136, 221.76, 253.608, 250.651], [303.029, 173.769, 490.826, 183.98], [303.083, 195.475, 490.444, 204.817], [303.083, 210.527, 488.798, 249.705], [108.0, 277.619, 221.374, 287.581], [107.691, 298.275, 505.246, 362.783], [108.0, 378.665, 246.659, 388.627]]}], "page_start": 9, "page_end": 9, "section": "Method", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/112_G-Retriever Retrieval-Augmented Generation for Textual Graph Understanding and Question An.pdf", "source_sha256": "c88093cd95417a12b8c7166ecc1132c9b52d077a4f73f84e7100e25722902b98", "parse_id": "parse_7fe0408b3ffa33102e8edc4a4986dd24", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

# Tokens
# Nodes
Min/Epoch
# Tokens
# Nodes
Min/Epoch
SceneGraphs
1,396
19
123.1
235 (↓83%)
5 (↓74%)
86.8 (↓29%)
WebQSP
100,627
1,371
18.7
610 (↓99%)
18 (↓99%)
6.2(↓67%)
Table 5: Quantitative comparison of halluci-
nation on the SceneGraphs dataset.
Baseline
G-Retriever
Valid Nodes
31%
77%
Valid Edges
12%
76%
Fully Valid Graphs
8%
62%
Table 6: Ablation study on the WebQSP dataset.
Method
Hit@1
∆G-Retriever
w/o Graph Encoder
54.62 ± 0.78
↓22.51%
w/o Projection Layer
69.70 ± 0.68
↓1.11%
w/o Textualized Graph
56.96 ± 1.83
↓19.19%
w/o Retrieval
63.84 ± 0.41
↓9.43%
6.3
Efficiency Evaluation
The efficiency of our approach is highlighted by the data in Table 4. Implementing our graph-based
retrieval significantly decreases the number of tokens required to describe the graphs in text, reduces
the number of nodes in graphs, and speeds up the training process. Specifically, for the SceneGraphs
dataset, tokens decreased by 83%, nodes by 74%, and training time by 29%. For the WebQSP dataset,
tokens decreased by 99%, nodes by 99%, and training time by 67%. These substantial reductions
demonstrate the method’s efficiency and potential in managing large-scale graph data.
6.4
Mitigation of Hallucination


</details>

### G-Retriever · 块 25 · 页 9-9 · completed

`chunk_675c20afd5f26d294c1e46627fdf87c2`；类型 body；跳过原因 None；2.89s；Token 828/8


<details><summary>完整来源块</summary>

To evaluate hallucination, we instructed the models to answer graph-related questions, specifically
identifying supporting nodes or edges from the graph. We manually reviewed 100 responses from
both our method and the baseline (i.e., LLM with graph prompt tuning), verifying the existence
of the nodes and edges referenced in the model’s output within the actual graph. Table 5 shows
that G-Retriever significantly reduces hallucinations by 54% compared to the baseline, as our graph
retrieval ensures that the data is sourced directly from the actual graph, leading to less hallucination.
See Appendix F for details.
6.5
Ablation Study
In this ablation study, we assess the individual impact of key components within our pipeline. As
shown in Table 6, there are performance drops when any of these components are removed, with the
graph encoder and textualized graph showing declines of 22.51% and 19.19%, respectively. This
demonstrates their complementary effects in representing the graph in both textual and embedded
formats. Additionally, the retrieval on graphs is also important to the overall performance. Further
details are available in Appendix B.3. We also present additional studies on our framework: it is
robust to the choice of graph encoders (see Appendix B.4) and benefits from the increased scale of
LLMs (see Appendix B.5).
Additionally, we include a detailed comparison with existing retrieval methods (see Appendix D), a
discussion on the complexity (see Appendix E), and demonstrations on how to use G-Retriever to
‘chat with your graph’ (see Appendix G).
7


</details>

### G-Retriever · 块 26 · 页 9-10 · completed

`chunk_f800cd4e8fa59900491c3efa5f890329`；类型 body；跳过原因 None；2.48s；Token 589/8


<details><summary>完整来源块</summary>

Conclusion
In this work, we introduce a new GraphQA benchmark for real-world graph question answering and
present G-Retriever, an architecture adept at complex and creative queries. Experimental results show
that G-Retriever surpasses baselines in textual graph tasks across multiple domains, scales effectively
with larger graph sizes, and demonstrates resistance to hallucination.
9

Limitations and Future Work: Currently, G-Retriever employs a static retrieval component. Future
developments could investigate more sophisticated RAG where the retrieval is trainable.


</details>

### G-Retriever · 块 27 · 页 10-10 · completed

`chunk_684103b0fae5fe9eb99fbf7fc78aad31`；类型 body；跳过原因 None；2.37s；Token 511/8


<details><summary>完整来源块</summary>

Acknowledgment
XB is supported by NUS Grant ID R-252-000-B97-133.


</details>

### StructGPT · 块 0 · 页 1-1 · completed

`chunk_a7df67e7fd088df02cfb3cdf0e560925`；类型 body；跳过原因 None；2.55s；Token 615/8


<details><summary>完整来源块</summary>

StructGPT: A General Framework for Large Language Model
to Reason over Structured Data
Jinhao Jiang1,3∗, Kun Zhou2,3∗, Zican Dong1, Keming Ye4,
Wayne Xin Zhao1,3† and Ji-Rong Wen1,2,3
1Gaoling School of Artificial Intelligence, Renmin University of China.
2School of Information, Renmin University of China.
3Beijing Key Laboratory of Big Data Management and Analysis Methods.
4University of Electronic Science and Technology of China.
jiangjinhao@ruc.edu.cn, batmanfly@gmail.com


</details>

### StructGPT · 块 1 · 页 1-1 · completed

`chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`；类型 body；跳过原因 None；46.53s；Token 739/204

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "IRR framework", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "specialized interfaces", "evidence_quote": "In this framework, we construct the specialized interfaces to collect relevant ev-idence from structured data (i.e., reading)", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "specialized interfaces", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "invoking-linearization-generation procedure", "evidence_quote": "we propose an invoking-linearization-generation procedure to support LLMs in reasoning on the structured data with the help of the interfaces.", "claim_kind": "author_assertion", "confidence": 1}

<details><summary>完整来源块</summary>

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


</details>

### StructGPT · 块 2 · 页 1-1 · completed

`chunk_a2951c70c36ae010415c4248bbed8a33`；类型 body；跳过原因 None；2.66s；Token 712/8


<details><summary>完整来源块</summary>

Introduction
Recently, large language models (LLMs) (Brown
et al., 2020; Zhao et al., 2023) have made remark-
able advancements in the NLP field.
Existing
work (Ouyang et al., 2022a; Zhang et al., 2022) has
demonstrated that LLMs (e.g., ChatGPT or GPT-
4 (OpenAI, 2023)) have strong zero-shot capability
to solve a broad range of tasks using specially de-
signed prompts, without task-specific fine-tuning.
Despite the successes, recent work has also re-
vealed that LLMs may generate unfaithful informa-
tion in conflict with the factual knowledge (Li et al.,
2023b), and also fall short of mastering domain-
specific or real-time knowledge (Schick et al., 2023;
Peng et al., 2023). A direct solution to the above
∗Equal contributions.
† Corresponding author.


</details>

### StructGPT · 块 3 · 页 1-1 · completed

`chunk_296f2400fee163aad415c87ede01d3fa`；类型 body；跳过原因 None；2.64s；Token 816/8


<details><summary>完整来源块</summary>

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


</details>

### StructGPT · 块 4 · 页 1-2 · completed

`chunk_9f421de75aed07b68340cb2f2471a79e`；类型 body；跳过原因 None；50.60s；Token 847/223

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Iterative Reading-then-Reasoning (IRR) framework", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "invoking-linearization-generation procedure", "evidence_quote": "Specifically, we propose an invoking-linearization-generation procedure to support LLMs in reading and reasoning on the structured data with the help of the external interfaces.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "invoking-linearization-generation procedure", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "iterating this procedure with provided interfaces", "evidence_quote": "By iterating this procedure with provided interfaces, we can gradually approach the target answer to a given question.", "claim_kind": "author_assertion", "confidence": 1}

<details><summary>完整来源块</summary>

search space of the data records, and more accu-
rately identify the required evidence to fulfill spe-
cific tasks. In this way, LLMs can concentrate on
reasoning based on the evidence obtained from the
interfaces. To implement the interface-augmented
approach, there remain two key problems, namely
how to design suitable interfaces for specific tasks
and how to utilize them for reasoning by LLMs,
which are the focus of this work.
To design suitable interfaces, we regard multi-
ple types of structured data as black-box systems,
and design the interfaces to provide accurate, effi-
cient data access and filtering for LLMs. For each
arXiv:2305.09645v2  [cs.CL]  23 Oct 2023

interface, its implementation is dependent on the
characteristic of the structured data, while its func-
tionality is general to all LLMs, with just a few
arguments for specifying the data requirements.
Based on these interfaces, we propose an Itera-
tive Reading-then-Reasoning (IRR) framework for
LLMs to utilize the interfaces to solve the tasks
based on structured data, namely StructGPT. This
framework considers two major functions to ful-
fill different tasks, namely collecting relevant evi-
dence (reading) and inferring the answer or plan-
ning subsequent steps (reasoning). Specifically, we
propose an invoking-linearization-generation pro-
cedure to support LLMs in reading and reasoning
on the structured data with the help of the external
interfaces. By iterating this procedure with pro-
vided interfaces, we can gradually approach the
target answer to a given question.


</details>

### StructGPT · 块 5 · 页 2-2 · completed

`chunk_9b4e995f8e1442d2cbb88ade921b87f1`；类型 body；跳过原因 None；2.74s；Token 724/8


<details><summary>完整来源块</summary>

To our knowledge, this is the first work that ex-
plores how to support LLMs in reasoning on multi-
ple types of structured data (including tables, KGs,
and DBs) in a unified paradigm. To evaluate the ef-
fectiveness of our approach, we conduct extensive
experiments on a wide range of tasks (e.g., KG-
based question answering (KGQA), Table-based
question answering (TableQA), and DB-based Text-
to-SQL). Experimental results on 8 datasets demon-
strate that our approach can effectively enhance the
reasoning performance of LLMs on structured data
in zero-shot and few-shot settings, even compara-
ble with competitive full-data supervised-tuning
methods. For example, in KGQA, TableQA, and
Text-to-SQL tasks, our approach yields an increase
of 11.4% of Hits@1 on WebQSP, 4.2% of accu-
racy in TabFact, and 4.7% of execution accuracy
in Spider respectively, compared to directly using
ChatGPT in the zero-shot setting.
2


</details>

### StructGPT · 块 6 · 页 2-2 · completed

`chunk_554414fc3894b4f266281da6de0b5d29`；类型 body；跳过原因 None；2.71s；Token 872/8


<details><summary>完整来源块</summary>

Related Work
Reasoning over Structured Data.
Structured
data (e.g., knowledge graphs, tables, and databases)
is an important knowledge carrier for a variety of
QA and reasoning tasks. Early work focuses on
designing specific model architectures tailored for
each type of structured data, such as graph neu-
ral networks (Sun et al., 2018), table Transform-
ers (Herzig et al., 2020), and tree-structured de-
coder (Wang et al., 2020). While achieving re-
markable performance, these approaches lack gen-
erality for various types of structured data and are
hard to be transferred across different tasks. Re-
cently, with the success of pre-trained language
models (PLMs) (e.g., T5 (Raffel et al., 2020),
BART (Lewis et al., 2020)), several methods (Raf-
fel et al., 2020; Khashabi et al., 2020) have adopted
PLMs as the general encoder or solver for different
structured data and tasks. Among them, Unified-
SKG (Xie et al., 2022) unifies a number of rea-
soning tasks over structured data into a text-to-text
format, which concatenates the question and the
linearized structured data as input, and then fine-
tunes T5 to learn to generate the answer. However,
UnifiedSKG also requires to tune the model param-
eters, and is unable to handle large-scale structured
data under the limitation of the maximum input
length. Instead, our method can utilize the LLM to
perform reasoning on structured data without train-
ing, and also leverage the interfaces of structured
data to better manipulate vast structured data.


</details>

### StructGPT · 块 7 · 页 2-2 · completed

`chunk_e86107abde0e1c9bd07e9c18aeccb3e4`；类型 body；跳过原因 None；2.69s；Token 880/8


<details><summary>完整来源块</summary>

LLMs for Structured Data. Benefitting from
the strong few-shot and zero-shot capability, re-
cent studies have leveraged LLMs to perform rea-
soning over structured data (Chen et al., 2023; Li
et al., 2023a; Cheng et al., 2022; Rajkumar et al.,
2022). Existing work can be roughly divided into
two types. The first type of method linearizes the
structured data into a sentence (e.g., table rows),
and feeds it into the LLMs to generate the answer
according to in-context exemplars (Cheng et al.,
2022; Chen, 2023). For complex questions or struc-
tured data, they first decompose it into multiple
simple and short ones and then perform lineariza-
tion and generation (Ye et al., 2023). Another type
of method leverages LLMs to evaluate the plausi-
bility of the solution plan based on the knowledge
base (Gu et al., 2023), or first generate a solution
draft with in-context exemplars and then revise the
draft grounding on the knowledge base (Li et al.,
2023c). However, most of them only focus on a
specific type of structured data, and are lack of gen-
erality across various data and tasks. In StructGPT,
we provide a unified paradigm that is general to
various structured data and downstream tasks.
3
Preliminary
In this section, we introduce the definition of struc-
tured data, which mainly consists of three com-
monly used types. Then we present the unified
problem statement.
Structured Data. Structured data (e.g., data ta-
bles and knowledge graphs) refers to the data that


</details>

### StructGPT · 块 8 · 页 3-3 · completed

`chunk_7362d71477696d08d87c2498f341ea13`；类型 body；跳过原因 None；2.72s；Token 884/8


<details><summary>完整来源块</summary>

is in a standardized format, conforming to some
logical data model (Xie et al., 2022; Chen et al.,
2009). Due to the formal structure, it is easy and
efficient to access and query structured data us-
ing formal languages (e.g., SQL and SPARQL
for databases) or specific algorithms (e.g., triples
search for knowledge graphs). In this work, we
mainly focus on three types of structured data,
namely knowledge graphs (KG), data tables (Ta-
ble), and databases (DB), since they play an impor-
tant role as the knowledge source in helping solve
complex reasoning tasks, described as follows.
• Knowledge Graph. A knowledge graph (KG)
consists of a number of triples to store the fac-
tual knowledge, denoted as G = {⟨e, r, e′⟩|e, e′ ∈
E, r ∈R}, where E and R denote the set of enti-
ties and relations, respectively. A triple ⟨e, r, e′⟩
represents the fact that there is a relation r between
the head entity e and the tail entity e′.
• Data Table. A data table T (table in short) con-
tains multiple columns {ci}C
i=1 and rows {lj}R
j=1,
where each row lj denotes a data record formatted
by the attributes indexed by columns {ci}C
i=1, and
vi,j denotes the content in the cell corresponding
to the position at column i and row j.
• Database. A database (DB) typically consists
of N data tables, denoted as D = {T1, T2, ..., TN}.
Besides the column names, the foreign keys across
all tables are also available to link the data from
two tables, denoted as {(c(k)


</details>

### StructGPT · 块 9 · 页 3-3 · completed

`chunk_3a66017788061f8f662ca365c955591a`；类型 body；跳过原因 None；2.57s；Token 745/8


<details><summary>完整来源块</summary>

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


</details>

### StructGPT · 块 10 · 页 3-3 · completed

`chunk_02c26b2202e7a91f83446553752c8fb6`；类型 body；跳过原因 None；49.24s；Token 895/216

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "iterative reading-then-reasoning", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "interface of structured data", "evidence_quote": "we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evidence)", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "interface of structured data", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "accurate, efficient data access and filtering", "evidence_quote": "we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evidence)", "claim_kind": "author_assertion", "confidence": 1.0}

<details><summary>完整来源块</summary>

In this work, we assume that LLMs have to rely
on the evidence contained in the structured data
to solve the three tasks described in Section 3.
An intuitive idea is to conduct a two-stage frame-
work as prior studies on retrieval-augmented ap-
proaches (Izacard et al., 2022; Oguz et al., 2022),
in which LLMs are employed to first collect suf-
ficient evidence relating to the question and then
figure out the answer by the LLMs. However, such
an approach is not directly applicable to structured
data. Although LLMs are capable of solving di-
verse tasks in natural language, they have limited
capacities in accurately representing and under-
standing structured data, especially for their con-
tained domain-specific knowledge (Moiseev et al.,
2022; Emelin et al., 2022).
To address this difficulty, our solution is inspired
by the use of specialized tools in solving complex
tasks for LLMs (Nakano et al., 2021; Gao et al.,
2022b; Schick et al., 2023). We noted that struc-
tured data is well organized and supports easy ac-
cess via formal language or queries (called inter-
face for generality). The basic idea of our approach
is to disentangle the two processes of reading and
reasoning for LLMs: we utilize the interface of
structure data to implement accurate, efficient data
access and filtering (obtaining the relevant evi-
dence), and further utilize the reasoning ability of
LLMs to figure out the final plan or result for the
question (fulfilling the task). In this way, LLMs can
concentrate on the reasoning process in answering
the question, without considering the specialized
approach to reading the structure data.


</details>

### StructGPT · 块 11 · 页 3-4 · skipped

`chunk_d755b392a1954f2b53e23e4968d18904`；类型 example；跳过原因 chunk_kind_excluded:example；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Specially, in our framework, we encapsulate
the structure data as a black-box system, and pro-
vide specific interfaces for LLMs to access the
contained data. Further, we propose an invoking-
linearization-generation procedure that enables
LLMs to read and extract useful evidence from
structured data via the corresponding interface. By
iterating the above procedure with provided inter-
faces, we can gradually obtain the answers by lever-
aging the superior reasoning abilities of LLMs.
4.2
Interfaces for Structured Data
Due to the standardized data formats, structured
data is often equipped with efficient data manage-
ment ways, e.g., SQL for the database. In our
approach, we aim to provide LLMs with special-

The Jeff
Probst Show
nominee
Jeff 
Probst
Lisa Ann 
Russell
spouse
Lisa
is_a
TV    
producer
Survivor
nominee
is_a
Talk
show
Extract_Triples (e, {r})
>>> input: ET(“Jeff Probst”,[“spouse”])
>>> output: [(Jeff Probst,spouse,Lisa Ann Russell)]
Extract_Neighbor_Relations (e)
>>> input: ENR(“Jeff Probst”)
>>> output: [spouse, is_a]
Extract_Columns (T, {c})
>>> input: EC(“Team”,[“Stadium”])
>>> output: [(Provident),…,(DW)]
Team
Stadium
Capacity
Bradford Bulls
Provident
27,000
…
…
…
Wigan Warriors
DW
25,138
Extract_SubTable (T, {c}, {j})
>>> input: ES(“Team”,[“Stadium”],[0,1,…,13])
>>> output: [(Provident),…,(DW)]
Extract_Table&Column_Name (D)


</details>

### StructGPT · 块 12 · 页 4-4 · skipped

`chunk_c0d2bbf48afc9940787c84d1f1a259b5`；类型 example；跳过原因 chunk_kind_excluded:example；0.00s；Token 0/0


<details><summary>完整来源块</summary>

>>> input: ETN(“mus_vis”)
>>> output: [visit, visitor, museum]
Extract_Tables_Infomration ({T})
>>> input: ETI([“visitor”]])
>>> output: [(visitor, (ID,…,Age), NULL)]
Mus_ID
Num_Ticket
visitor_ID
Total_spent
…
…
…
…
ID
Name
Level_of_mem
Age
…
…
…
…
visit
visitor
Mus_ID
Name
Num_Staff
Open_Year
…
…
…
…
museum
visit.Museum_ID→meseum.Museum_ID
visit.visitor_ID→visitor.ID
Extract_Column_Name (T)
>>> input: ECN(“Team”)
>>> output: [Team,Stadium,Capacity]
“spouse, is_a”
“Team,…,Capacity”
“visitor(*,ID,…,);…”
Linearization
Who is the wife of Jeff Probst?
what is the last stadium listed on this chart?
How many visitors below age 30 are there?
Question
KGQA
TableQA
Text-to-SQL
spouse
Stadium
visitor
LLM
Generation
Lisa Ann Russell
Final Answer or Executable SQL
DW
SELECT count(*) FROM visitor WHERE age < 30
Structured Data
Interfaces
KG
Table
DB
Extract_Neighbor_Relations(“Jeff Probst”)
Extract_Column_Name(“Team”)
Extract_Table&Column_Name(“mus_vis”)
Invoking
is_a
producer
or
Figure 1: The overview of the proposed iterative reading-then-reasoning approach. We design specialized interfaces
for reading structured data, and iterate the invoking-linearization-generation procedure to utilize LLMs for perform-
ing reasoning on the interfaces, until deriving the final answer or executable SQL.
ized interfaces, helping LLMs to read and utilize
the structured data. Next, we present the specially
designed interfaces for KG, table, and DB.


</details>

### StructGPT · 块 13 · 页 4-4 · skipped

`chunk_88de9ef01acd16c34fde2c9091445dd8`；类型 example；跳过原因 chunk_kind_excluded:example；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Interfaces for Knowledge Graph.
When per-
forming complex reasoning on a KG, existing
work (Sun et al., 2018) typically starts from a cer-
tain entity (about the question topic), and jumps
along with the relations until reaching the answer.
In this process, LLMs should be aware of the neigh-
boring relations of the current entity, and the neigh-
boring triples with certain relations to the current
entity. Based on it, LLMs can select the relevant
relations and triples from them to find the answer.
For this purpose, we devise two functions for as-
sisting LLMs to accomplish the above operations.
• Extract_Neighbor_Relations (e): extracts all
the neighboring relations of the entity e.
• Extract_Triples (e, {r}): extracts all the triples
with the relation in {r} and head entity e.
Interfaces for Table.
Given a data table, LLMs
need to know its contained column names, and
can access the content by row or column, enabling
LLMs to extract its sub-table containing relevant
columns and rows. Thus, we define three functions:
• Extract_Column_Name (T ): extracts all the
column names of a table T .
• Extract_Columns (T , {c}): extracts the con-
tents of columns from a table T by indices {c}.
• Extract_SubTable (T , {c}, {j}): extracts the
sub-table specified by the column indices {c} and
row indices {j} from a table T .


</details>

### StructGPT · 块 14 · 页 4-5 · completed

`chunk_785bb2357da95f231566a7893e116b3f`；类型 body；跳过原因 None；130.19s；Token 848/561

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "StructGPT", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Tables_Information ({T })", "evidence_quote": "we devise two functions as follows: • Extract_Tables_Information ({T }): extracts the table names, column names, and foreign keys from a set of tables {T }.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "StructGPT", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "invoking an interface for extracting the relevant information from the structured data", "evidence_quote": "In this step, we aim to invoke an interface for extracting the relevant information from the structured data.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `table_or_template_example`：{"claim_id": "70a78b25c467dd5fb50e080cd0f397c8d1a63fb8523962b7dc958e9b4afcfaa0", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_cedbfddc8030ded4258640a1e0a0a733", "paper_title": "StructGPT: A General Framework for Large Language Model to Reason over Structured Data", "chunk_id": "chunk_785bb2357da95f231566a7893e116b3f", "subject_type": "Method", "subject": "StructGPT", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Table&Column_Name (D)", "evidence_quote": "we devise two functions as follows:\n• Extract_Table&Column_Name (D): extracts\nthe names of all the tables and their contained\ncolumns from the database.", "quote_match_method": "whitespace_normalized", "quote_start": 308, "quote_end": 460, "source_spans": [{"pdf_page": 4, "start_char": 3421, "end_char": 4003, "chunk_start_char": 0, "chunk_end_char": 582, "block_bboxes": [[306.142, 598.179, 526.217, 690.55], [306.142, 693.704, 524.415, 732.105], [306.142, 735.258, 524.412, 773.66]]}, {"pdf_page": 5, "start_char": 0, "end_char": 1032, "chunk_start_char": 583, "chunk_end_char": 1615, "block_bboxes": [[70.866, 73.452, 278.444, 84.361], [70.866, 91.037, 290.943, 223.972], [70.866, 233.953, 290.949, 366.988]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf", "source_sha256": "8a6c0a67fe20ebefb8a25e504cfb6d42436b25f88793fd1e2e07e2d1cb29653b", "parse_id": "parse_0f17805b3b51899f139913f99df23591", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `table_or_template_example`：{"claim_id": "293936e25e26b1fd6d89321d64d4f5c94518e7b5dc279ecc134286bd51a31c04", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_cedbfddc8030ded4258640a1e0a0a733", "paper_title": "StructGPT: A General Framework for Large Language Model to Reason over Structured Data", "chunk_id": "chunk_785bb2357da95f231566a7893e116b3f", "subject_type": "Component", "subject": "Extract_Table&Column_Name (D)", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "extracting the names of all the tables and their contained columns from the database", "evidence_quote": "• Extract_Table&Column_Name (D): extracts\nthe names of all the tables and their contained\ncolumns from the database.", "quote_match_method": "whitespace_normalized", "quote_start": 344, "quote_end": 460, "source_spans": [{"pdf_page": 4, "start_char": 3421, "end_char": 4003, "chunk_start_char": 0, "chunk_end_char": 582, "block_bboxes": [[306.142, 598.179, 526.217, 690.55], [306.142, 693.704, 524.415, 732.105], [306.142, 735.258, 524.412, 773.66]]}, {"pdf_page": 5, "start_char": 0, "end_char": 1032, "chunk_start_char": 583, "chunk_end_char": 1615, "block_bboxes": [[70.866, 73.452, 278.444, 84.361], [70.866, 91.037, 290.943, 223.972], [70.866, 233.953, 290.949, 366.988]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf", "source_sha256": "8a6c0a67fe20ebefb8a25e504cfb6d42436b25f88793fd1e2e07e2d1cb29653b", "parse_id": "parse_0f17805b3b51899f139913f99df23591", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}
- 拒绝 `table_or_template_example`：{"claim_id": "374ced2be09f05f9d67945121b3a31e195fc0eb78d3a3dab216bc28f8e453ff1", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_cedbfddc8030ded4258640a1e0a0a733", "paper_title": "StructGPT: A General Framework for Large Language Model to Reason over Structured Data", "chunk_id": "chunk_785bb2357da95f231566a7893e116b3f", "subject_type": "Component", "subject": "Extract_Tables_Information ({T })", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "extracting the table names, column names, and foreign keys from a set of tables {T }", "evidence_quote": "• Extract_Tables_Information ({T }): extracts\nthe table names, column names, and foreign keys\nfrom a set of tables {T }.", "quote_match_method": "whitespace_normalized", "quote_start": 461, "quote_end": 581, "source_spans": [{"pdf_page": 4, "start_char": 3421, "end_char": 4003, "chunk_start_char": 0, "chunk_end_char": 582, "block_bboxes": [[306.142, 598.179, 526.217, 690.55], [306.142, 693.704, 524.415, 732.105], [306.142, 735.258, 524.412, 773.66]]}, {"pdf_page": 5, "start_char": 0, "end_char": 1032, "chunk_start_char": 583, "chunk_end_char": 1615, "block_bboxes": [[70.866, 73.452, 278.444, 84.361], [70.866, 91.037, 290.943, 223.972], [70.866, 233.953, 290.949, 366.988]]}], "page_start": 4, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf", "source_sha256": "8a6c0a67fe20ebefb8a25e504cfb6d42436b25f88793fd1e2e07e2d1cb29653b", "parse_id": "parse_0f17805b3b51899f139913f99df23591", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Interfaces for Database.
Considering a simpli-
fied setting when querying the database, LLMs
should be aware of all the contained tables and
columns (by name) for relevant tables selection,
and can also acquire the detailed columns and for-
eign keys from the selected tables to search for the
answer. Thus, we devise two functions as follows:
• Extract_Table&Column_Name (D): extracts
the names of all the tables and their contained
columns from the database.
• Extract_Tables_Information ({T }): extracts
the table names, column names, and foreign keys
from a set of tables {T }.

4.3
Reading and Reasoning with Interfaces
Based on the above interfaces, we propose a gen-
eral invoking-linearization-generation procedure
that can be iterated in multiple turns for utilizing
LLMs to perform reading and reasoning on struc-
tured data. For each iteration, based on the cur-
rently collected data, we first invoke an interface to
extract relevant evidence from structure data, then
linearize it into a textual prompt, and finally feed
the prompt into the LLM for generation (selecting
useful data or predicting the answer).
Invoking an Interface.
In this step, we aim to
invoke an interface for extracting the relevant infor-
mation from the structured data. According to the
designed interfaces in Section 4.2, we construct the
input based on the currently available data (e.g., en-
tity and table), and then invoke the interface to ob-
tain more detailed relevant information (e.g., neigh-
boring relations and column names), which will be
fed into LLMs for collecting useful information or
generating the answer.


</details>

### StructGPT · 块 15 · 页 5-5 · completed

`chunk_5159a5fa625d869d5a21e72e43b4b713`；类型 body；跳过原因 None；97.52s；Token 882/422

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Information Linearization", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "concatenation of relations and triples into a long sentence", "evidence_quote": "For the information from KG (i.e., relations and triples), we concatenate them into a long sentence marked by specific separation and boundary symbols.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Information Linearization", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "conversion of table and database contents into triples", "evidence_quote": "For table and database, we leverage the same way to linearize the extracted table names or column names. While for contents in columns and rows, we follow existing work (Pasupat and Liang, 2015) that first converts them into triples, where head entities are the row indices, relations are column names, and tail entities are the content in the cell", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "LLM for Generation", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "input prompts to elicit evidence selection ability", "evidence_quote": "The first type of prompts mostly adopts the following pattern: “Here are [Y]. Which [X] are most relevant to answer the question [Q]”. It aims to elicit the ability of LLMs to select useful evidence (i.e., [X]) from linearized extracted information (i.e., [Y]), according to the question (i.e., [Q]).", "claim_kind": "author_assertion", "confidence": 1}

<details><summary>完整来源块</summary>

Information Linearization.
Given the extracted
information, we convert it into a textual sentence
that can be understood by LLMs. For the infor-
mation from KG (i.e., relations and triples), we
concatenate them into a long sentence marked by
specific separation and boundary symbols. For ta-
ble and database, we leverage the same way to lin-
earize the extracted table names or column names.
While for contents in columns and rows, we follow
existing work (Pasupat and Liang, 2015) that first
converts them into triples, where head entities are
the row indices, relations are column names, and
tail entities are the content in the cell, e.g., “(row 1,
year, 1896)” and “(row 1, city, Athens)”. Then, for
each row, we extract the row indices in the front
and omit it in the triples, to compose a simplified
sentence, e.g., “row 1: (year, 1896), (city, Athens)”.
For multiple rows, we concatenate them into a long
sentence via a special separation symbol.
LLM for Generation.
After linearization, we
design two types of input prompts for LLMs to
fulfill different purposes1:
• The first type of prompts mostly adopts the fol-
lowing pattern: “Here are [Y]. Which [X] are most
relevant to answer the question [Q]”. It aims to
elicit the ability of LLMs to select useful evidence
1Note that our used prompts are not always consistent with
the two examples, as we have rewritten them to better adapt
to the specific datasets and extracted information.
(i.e., [X]) from linearized extracted information
(i.e., [Y]), according to the question (i.e., [Q]).


</details>

### StructGPT · 块 16 · 页 5-5 · completed

`chunk_dad0510834e8348ffea381beed9d2c75`；类型 body；跳过原因 None；2.68s；Token 669/8


<details><summary>完整来源块</summary>

• The second type of prompt follows the pattern:
“Based on [Y], please generate [Z] for the question
[Q]”. It aims to predict the targeted results (i.e.,
[Z]) for the given question (i.e., [Q]) based on the
linearized extracted information (i.e., [Y]). Note
that the targeted results can be either the answer
string or executable formal language (e.g., SQL)
that can lead to the final answer.
By iterating the above invoking-linearization-
generation procedure on designed interfaces, LLMs
can progressively capture more useful evidence for
deriving the final answer.
4.4
Instantiated Downstream Tasks
In the following, we describe the instances of the
above general workflow for the tasks described
in Section 3, since they deal with very different
structure data and vary in the task settings.


</details>

### StructGPT · 块 17 · 页 5-5 · completed

`chunk_55f3e1163ab88d1a50c645afccb9afe1`；类型 body；跳过原因 None；88.70s；Token 859/384

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "invoking-linearization-generation procedure", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "Extract_Neighbor_Relation(eT )", "evidence_quote": "First, we invoke the interface Extract_Neighbor_Relation(eT ) to extract the candidate one-hop relations, linearize them to compose the input prompt, and then leverage the LLM to select the useful relations {r} according to the question.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "invoking-linearization-generation procedure", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "Extract_Triples (eT , {r})", "evidence_quote": "Then, based on {r}, we invoke the Extract_Triples (eT , {r}) interface to collect the relevant triples for the head entity eT and relation in {r}, then linearize this information, and finally employ the LLM to select the most relevant triples", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `component_not_explicitly_listed`：{"claim_id": "f9d1d917154344ca728bf9590825d6c39b5b707ee53565471916e02af914139c", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_cedbfddc8030ded4258640a1e0a0a733", "paper_title": "StructGPT: A General Framework for Large Language Model to Reason over Structured Data", "chunk_id": "chunk_55f3e1163ab88d1a50c645afccb9afe1", "subject_type": "Method", "subject": "iterative reading-then-reasoning", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "invoking-linearization-generation procedure", "evidence_quote": "Starting from eT ,\nwe perform the invoking-linearization-generation\nprocedure two times using the two interfaces in\nKG sequentially.", "quote_match_method": "whitespace_normalized", "quote_start": 419, "quote_end": 551, "source_spans": [{"pdf_page": 5, "start_char": 3378, "end_char": 4902, "chunk_start_char": 0, "chunk_end_char": 1524, "block_bboxes": [[305.749, 356.238, 526.316, 773.66]]}], "page_start": 5, "page_end": 5, "section": "Related Work", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf", "source_sha256": "8a6c0a67fe20ebefb8a25e504cfb6d42436b25f88793fd1e2e07e2d1cb29653b", "parse_id": "parse_0f17805b3b51899f139913f99df23591", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

KG-based Question Answering (KGQA).
This
task aims to find the answer entities for the question
based on the KG. Following existing work (Sun
et al., 2018), we denote the mentioned entity in
the given question q as the topic entity eT , and
assume it has been linked to some specific en-
tity on the KG through existing linking tools (e.g.,
Google Knowledge Graph Search API) or mod-
els (e.g., ELQ (Li et al., 2020)). Starting from eT ,
we perform the invoking-linearization-generation
procedure two times using the two interfaces in
KG sequentially. First, we invoke the interface
Extract_Neighbor_Relation(eT ) to extract the can-
didate one-hop relations, linearize them to com-
pose the input prompt, and then leverage the LLM
to select the useful relations {r} according to the
question. Then, based on {r}, we invoke the Ex-
tract_Triples (eT , {r}) interface to collect the rel-
evant triples for the head entity eT and relation in
{r}, then linearize this information, and finally em-
ploy the LLM to select the most relevant triples,
whose tail entities will be considered as the final
answer. Besides, we can also consider the multi-
hop KGQA task (Lan et al., 2021), where after
selecting the triples of the current hop, the LLM
should assess whether the current information is
sufficient to answer the question. Then, LLMs will
make according actions based on the assessment,
i.e., stopping the iterations for producing the an-
swer or continuing the iterations on next-hop tail
entities from selected triples.


</details>

### StructGPT · 块 18 · 页 6-6 · completed

`chunk_a1264db566130c104275b807d750904a`；类型 body；跳过原因 None；281.77s；Token 831/1178

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Table-based Question Answering (TableQA)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Column_Name (T)", "evidence_quote": "first, we invoke Extract_Column_Name (T) to extract all column names of a table, linearize them, and leverage LLMs to select the relevant ones {c} according to the question.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Table-based Question Answering (TableQA)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Columns (T, {c})", "evidence_quote": "Then, we invoke Extract_Columns (T , {c}) to extract the contents of all relevant columns, and select the useful row indices {j} by LLMs.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "Table-based Question Answering (TableQA)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_SubTable (T, {c}, {j})", "evidence_quote": "Subsequently, we further invoke Extract_SubTable (T , {c}, {j}) to generate the sub-table for the question.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "Extract_Column_Name (T)", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "linearization and selection of column names", "evidence_quote": "first, we invoke Extract_Column_Name (T) to extract all column names of a table, linearize them, and leverage LLMs to select the relevant ones {c} according to the question.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "Extract_Columns (T, {c})", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "linearization and selection of column contents", "evidence_quote": "Then, we invoke Extract_Columns (T , {c}) to extract the contents of all relevant columns, and select the useful row indices {j} by LLMs.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "Extract_SubTable (T, {c}, {j})", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "generation of sub-table for question answering", "evidence_quote": "Subsequently, we further invoke Extract_SubTable (T , {c}, {j}) to generate the sub-table for the question.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "DB-based Semantic Parsing (Text-to-SQL)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Table&Column_Name (D)", "evidence_quote": "first, we invoke Extract_Table&Column_Name (D) to obtain all the table names and their column names in the DB, linearize them, and utilize the LLM to select the relevant table names.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "DB-based Semantic Parsing (Text-to-SQL)", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Tables_Information ({T})", "evidence_quote": "Then, we invoke Extract_Tables_Information ({T}) to obtain all the relevant information (i.e., column names and foreign keys) from these tables.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "Extract_Table&Column_Name (D)", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "linearization and selection of table names and column names", "evidence_quote": "first, we invoke Extract_Table&Column_Name (D) to obtain all the table names and their column names in the DB, linearize them, and utilize the LLM to select the relevant table names.", "claim_kind": "author_assertion", "confidence": 1}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "Extract_Tables_Information ({T})", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "linearization and selection of table information", "evidence_quote": "Then, we invoke Extract_Tables_Information ({T}) to obtain all the relevant information (i.e., column names and foreign keys) from these tables.", "claim_kind": "author_assertion", "confidence": 1}

<details><summary>完整来源块</summary>

Table-based Question Answering (TableQA).
For TableQA, we typically need to answer the
question according to the content in the given ta-
ble. We also perform the above procedure by us-
ing the three interfaces in turn. Concretely, first,
we invoke Extract_Column_Name (T ) to extract
all column names of a table, linearize them, and
leverage LLMs to select the relevant ones {c}
according to the question. Then, we invoke Ex-
tract_Columns (T , {c}) to extract the contents of
all relevant columns, and select the useful row in-
dices {j} by LLMs. Subsequently, we further in-
voke Extract_SubTable (T , {c}, {j}) to generate
the sub-table for the question. Based on the lin-
earized sub-table, the LLM finally generates the
answer to the question.
DB-based Semantic Parsing (Text-to-SQL).
This task focuses on generating a SQL query that
can be executed to obtain the required information
from a database. To achieve this goal, first, we
invoke Extract_Table&Column_Name (D) to ob-
tain all the table names and their column names
in the DB, linearize them, and utilize the LLM
to select the relevant table names. Then, we in-
voke Extract_Tables_Information ({T }) to obtain
all the relevant information (i.e., column names and
foreign keys) from these tables. Similarly, by lin-
earizing this information and composing the input
prompt, the LLM can generate an executable SQL
for the given question.
5


</details>

### StructGPT · 块 19 · 页 6-6 · completed

`chunk_5a1fd5f3826cd78a6219d6bddfaa91da`；类型 body；跳过原因 None；2.93s；Token 853/8


<details><summary>完整来源块</summary>

Experiment
We conduct experiments on three complex rea-
soning tasks over structured data, i.e., KGQA,
TableQA, and DB based text-to-SQL.
5.1
Datasets
For KG based QA (KGQA), we adopt two
benchmark datasets, i.e., WebQuestionsSP (We-
bQSP) (Yih et al., 2016) and MetaQA (Zhang et al.,
2018) for evaluation. The answer entities in We-
bQSP require up to 2-hop reasoning on the Free-
base KG. In contrast, MetaQA contains questions
in the movie domain, whose answer entities are up
to 3 hops away from the topic entities on a movie
KG (based on OMDb). According to the num-
ber of hops, it is split into three sub-datasets, i.e.,
MetaQA-1hop, MetaQA-2hop, and MetaQA-3hop.
For Table based QA (TableQA), we adopt
three widely-used datasets, weakly-supervised Wik-
iSQL (WikiSQL) (Zhong et al., 2017), WikiTable-
Questions (WTQ) (Pasupat and Liang, 2015), and
TabFact (Chen et al., 2020). The first two are typ-
ical table-based question answering datasets, and
the third one is a multiple-choice dataset that con-
centrates on table fact verification. WikiSQL re-
quires filtering and aggregating information over
the table content, and the WTQ demands more
advanced reasoning capabilities (e.g., sorting). Tab-
Fact needs to judge whether the provided statement
agrees with the facts stored in a table.


</details>

### StructGPT · 块 20 · 页 6-6 · completed

`chunk_48d9cd08853110685bb8562077cf5228`；类型 body；跳过原因 None；2.69s；Token 859/8


<details><summary>完整来源块</summary>

For DB based semantic parsing (Text-to-SQL),
we adopt three public datasets, i.e., Spider (Yu et al.,
2018), Spider-SYN (Gan et al., 2021), and Spider-
Realistic (Deng et al., 2021). Spider is a typical
Text-to-SQL dataset covering 20 databases with a
set of 1034 evaluation samples. Spider-SYN and
Spider-Realistic are two more challenging datasets
derived from Spider. Concretely, Spider-SYN man-
ually substitutes the synonyms in natural language
questions, while Spider-Realistic removes the ques-
tions in the evaluation set that explicitly mention
the required columns’ names.
5.2
Evaluation Metrics
For KGQA, we employ Hits@1 which assesses
whether the top-1 predicted answer is correct. In
our approach, we focus on generating the most con-
fident answer and then checking if the prediction
hits any target. As LLMs may generate multiple
answers, we also conducted a manual double-check
finally (Tan et al., 2023), to judge if wrong answers
are included. For TableQA, we adopt two eval-
uation metrics, namely denotation accuracy and
accuracy. In WTQ and WikiSQL, denotation accu-
racy is employed to evaluate whether the predicted
answer is the same as the gold answer based on
set-level equivalence. In TabFact, we adopt ac-
curacy to assess the correctness of the prediction.
For Text-to-SQL, we adopt the execution accuracy
(EX) to assess whether the execution results of the
predicted SQL and the gold SQL are the same.
5.3
Baselines
We compare our method with competitive full-


</details>

### StructGPT · 块 21 · 页 6-7 · completed

`chunk_2cdccff3910b914ee3f18d9beda20684`；类型 body；跳过原因 None；2.78s；Token 957/8


<details><summary>完整来源块</summary>

data supervised-tuning baselines tailored to these
tasks. Specifically, our method is a general iterative
reading-then-reasoning (IRR) framework that can
be used for different LLMs. And we test our IRR
with two different LLMs, i.e., Davinci-003 (text-
davinci-003 (Ouyang et al., 2022b)) and Chat-

GPT (i.e., gpt-3.5-turbo 2), under zero-shot and
few-shot settings 3. Considering the evolution of
the closed large language model, e.g., ChatGPT, we
have further conducted supplementary experiments
on three datasets (i.e., WebQSP, WTQ, and Spider)
using the latest August version of ChatGPT. The re-
sults are presented in Appendix A. For KGQA, we
select KV-Mem (Miller et al., 2016), GragtNet (Sun
et al., 2018), EmbedKGQA (Saxena et al., 2020),
NSM (He et al., 2021), and UniKGQA (Jiang et al.,
2023). For TableQA, we select MAPO (Liang
et al., 2018), TAPAS (Herzig et al., 2020; Eisensch-
los et al., 2020), UnifiedSKG (T5-3B) (Xie et al.,
2022), TAPEX (Liu et al., 2022), and DATER (Ye
et al., 2023). For Text-to-SQL, we select RAT-
SQL+BERTLarge (Wang et al., 2020), TKK-
Large (Gao et al., 2022a), T5-3B+PICARD (Raffel
et al., 2020), RASAT+PICARD (Qi et al., 2022),
and RESDSQL-3B+NatSQL (Li et al., 2023a).


</details>

### StructGPT · 块 22 · 页 7-7 · completed

`chunk_d2344015fa6af178ba74731f12fd393c`；类型 body；跳过原因 None；2.85s；Token 890/8


<details><summary>完整来源块</summary>

Additionally, we incorporate baselines that em-
ploy Davinci-003 and ChatGPT directly for achiev-
ing the aforementioned tasks in a zero-shot setting.
To ensure a fair comparison, we utilize the same
instruction prompt to evaluate them, ensuring that
the only difference with our method is the usage
of structured data. Specifically, in KGQA datasets,
we follow existing work (Tan et al., 2023) that uti-
lizes LLMs to answer the questions without using
KG. In TableQA and Text-to-SQL, we feed the re-
quired information of tables with questions into
LLMs (Liu et al., 2023c,a), without special treat-
ment for the overlength problem.
5.4
Results and Analysis
We show the results on KGQA, TableQA, and Text-
to-SQL tasks and analyze them respectively.
Evaluation on KGQA. Table 1 shows the results
on KGQA datasets. First, LLMs can achieve per-
formance comparable to the supervised learning
model (i.e., 61.2 of ChatGPT v.s. 66.4 of GraftNet
and 48.3 of Davinci-003 v.s. 46.7 of KV-Mem) on
the WebQSP dataset, in a zero-shot setting with-
out using KGs. It demonstrates that LLMs indeed
grasp a certain amount of knowledge that can help
them answer complex questions.
However, on
more difficult datasets that require multi-hop rea-
soning (e.g., MetaQA-2hop and MetaQA-3hop),
the two LLMs perform not well. It indicates that
2https://platform.openai.com/docs/models/gpt-3-5
3In our experiment, we use the June version of Davinci-003
and ChatGPT.


</details>

### StructGPT · 块 23 · 页 7-7 · completed

`chunk_358a932cf9be09a75cae0606806b9318`；类型 body_mixed；跳过原因 None；46.97s；Token 1044/197

- 保留（待审）：IRR (ours) --HAS_COMPONENT--> interfaces for KG
  - 引文偏移 1093:1182：In our approach, we devise interfaces for KG to efficiently read the relevant information
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "IRR procedure", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "sequential reading-then-reasoning", "evidence_quote": "We leverage the IRR procedure on devised interfaces sequentially, which can progressively capture more useful detailed evidence for finally obtaining the answer.", "claim_kind": "author_assertion", "confidence": 1}

<details><summary>完整来源块</summary>

Table 1:
Results of different methods for KGQA
(Hits@1 in percent). We copy the results in the first
block from He et al. (2021) and Jiang et al. (2023). The
best results of each block are highlighted in bold.
Methods
WQSP
MQA
1hop
MQA
2hop
MQA
3hop
KV-Mem
46.7
96.2
82.7
48.9
GraftNet
66.4
97.0
94.8
77.7
EmbedKGQA
66.6
97.5
98.8
94.8
NSM
68.7
97.1
99.9
98.9
UniKGQA
75.1
97.5
99.0
99.1
Davinci-003
48.3
52.1
25.3
42.5
+ IRR (ours)
71.9
94.4
59.5
70.2
+ IRR (ours, few-shot)
71.0
97.1
93.5
75.3
ChatGPT
61.2
61.9
31.0
43.2
+ IRR (ours)
72.6
94.2
93.9
80.2
+ IRR (ours, few-shot)
69.6
97.1
97.3
87.0
LLMs can not solely rely on their own knowledge
to answer difficult questions, and their augmen-
tation with KGs is necessary. In contrast, when
incorporating our proposed method to access KG,
the performance of Davinci-003 and ChatGPT can
be both substantially improved, indicating the ef-
fectiveness of our proposed method for supporting
LLMs reasoning over KG. By adding a few in-
context exemplars (i.e., 15 for WQSP and 32 for
MQA) to LLMs, we can further improve the model
performance. In our approach, we devise interfaces
for KG to efficiently read the relevant information,
and leverage LLMs to extract useful parts and per-
form reasoning. We leverage the IRR procedure
on devised interfaces sequentially, which can pro-
gressively capture more useful detailed evidence
for finally obtaining the answer.


</details>

### StructGPT · 块 24 · 页 7-8 · completed

`chunk_1efd4680d043944e45eb1947af46faa9`；类型 body；跳过原因 None；25.70s；Token 986/106

- 拒绝 `control_object_not_parameter`：{"claim_id": "737b7e0062eee274f45fb2a5c5196466a5e22203131166abfab13604edd4e709", "graph_version": "kg-rebuild-pilot-14b-v4", "paper_id": "paper_cedbfddc8030ded4258640a1e0a0a733", "paper_title": "StructGPT: A General Framework for Large Language Model to Reason over Structured Data", "chunk_id": "chunk_1efd4680d043944e45eb1947af46faa9", "subject_type": "Method", "subject": "IRR", "predicate": "CONTROLLED_BY", "object_type": "Parameter", "object": "32 in-context exemplars", "evidence_quote": "when\nadding 32 in-context exemplars to the LLMs, they\ncan obtain further performance improvements.", "quote_match_method": "whitespace_normalized", "quote_start": 531, "quote_end": 629, "source_spans": [{"pdf_page": 7, "start_char": 3777, "end_char": 4556, "chunk_start_char": 0, "chunk_end_char": 779, "block_bboxes": [[306.142, 559.33, 526.221, 773.647]]}, {"pdf_page": 8, "start_char": 0, "end_char": 624, "chunk_start_char": 780, "chunk_end_char": 1404, "block_bboxes": [[70.557, 71.668, 290.791, 141.418], [75.944, 157.275, 284.054, 166.242], [75.944, 173.793, 276.237, 226.595], [75.944, 234.065, 276.24, 297.826]]}], "page_start": 7, "page_end": 8, "section": "Experiment", "claim_kind": "author_assertion", "confidence": 1.0, "review_status": "pending", "source_relative_path": "Methods/229_StructGPT A General Framework for Large Language Model to Reason over Structured Data.pdf", "source_sha256": "8a6c0a67fe20ebefb8a25e504cfb6d42436b25f88793fd1e2e07e2d1cb29653b", "parse_id": "parse_0f17805b3b51899f139913f99df23591", "model": "qwen2.5:14b", "prompt_version": "kg-rebuild-pilot-14b-v4", "schema_version": "kg-rebuild-pilot-14b-v4"}

<details><summary>完整来源块</summary>

Evaluation on TableQA. Table 2 shows the re-
sults on three TableQA datasets. First, with the
full table as the prompt, ChatGPT can also achieve
comparable performance on WTQ and TabFact as
full-data supervised-tuning methods, but performs
not well on more difficult WikiSQL datasets. It also
indicates that LLMs have the capability of under-
standing the knowledge within table data to some
extent. Second, our proposed method can consis-
tently improve the performance of two LLMs a
lot in both three datasets. At the same time, when
adding 32 in-context exemplars to the LLMs, they
can obtain further performance improvements. It
indicates the effectiveness of our proposed method
in helping LLMs reasoning over Table. Our ap-
proach provides a more effective way for LLMs to

Table 2: Results of different methods for TableQA (de-
notation accuracy for WTQ and WikiSQL, accuracy for
TabFact). We copy the results of TAPAS on TabFact
from Eisenschlos et al. (2020), and others in the first
block from their original papers. The best results of
each block are highlighted in bold.
Methods
WTQ
WikiSQL
TabFact
MAPO
43.8
72.6
-
TAPAS
48.8
83.6
81.0
UnifiedSKG (T5-3B)
49.3
86.0
83.7
TAPEX
57.5
89.5
84.2
DATER
65.9
-
93.0
Davinci-003
34.8
49.1
80.7
+ IRR (ours)
39.2
51.8
76.5
+ IRR (ours, few-shot)
57.0
64.6
87.3
ChatGPT
43.3
51.6
82.9
+ IRR (ours)
48.4
54.4
87.1
+ IRR (ours, few-shot)
52.2
65.6
87.6


</details>

### StructGPT · 块 25 · 页 8-8 · completed

`chunk_c11d51b003e670a9b0426a34b4b70425`；类型 body；跳过原因 None；29.37s；Token 819/127

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "irr", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "Extract_Neighbor_Relations function", "evidence_quote": "In each iteration, we first invoke the Extract_Neighbor_Relations function to extract the neighboring relations (e.g., birthplace, residence, and education) of the topic entity “Harper Lee”", "claim_kind": "author_assertion", "confidence": 1.0}

<details><summary>完整来源块</summary>

iteratively access and utilize the relevant informa-
tion from the table, which reduces the influence of
irrelevant and redundant information.
Evaluation on Text-to-SQL. Table 3 shows the
results on DB-based datasets. First, with all the
information from DB (table names, column names,
and foreign keys) as the prompt, the LLMs have
the capability of directly generating a suitable SQL
query of the question, performing well on all three
datasets. Whereas, the performance of LLMs is
not better than competitive full-data supervised-
tuning methods, showing the difficulty of this task.
As our proposed method can extract relevant ta-
bles and columns, it also alleviates the influence
of irrelevant information for LLMs to generate the
SQL query. Simultaneously, with the assistance of
32 in-context exemplars, LLMs exhibit enhanced
comprehension of the mapping between natural
language questions and their corresponding SQL
queries. The consistent performance improvements
over the three datasets whenever in zero-shot or
few-shot settings also indicate the effectiveness of
our proposed method.
Case Study. We show an example of KGQA in
Figure 2, to help understand the working process
of our method. Given the question, the interfaces
of the structured data are sequentially invoked to
iteratively extract more useful and detailed infor-
mation. In each iteration, we first invoke the Ex-
tract_Neighbor_Relations function to extract the
neighboring relations (e.g., birthplace, residence,
and education) of the topic entity “Harper Lee”,


</details>

### StructGPT · 块 26 · 页 8-8 · completed

`chunk_71d97b54ef1d2890107dd19905658ddc`；类型 body_mixed；跳过原因 None；3.66s；Token 999/8


<details><summary>完整来源块</summary>

Table 3: Performance comparison of different methods
for Text-to-SQL (execution accuracy in percent). We
copy the results of RAT-SQL+BERTLarge and TKK-
Large from Deng et al. (2021) and Gao et al. (2022a),
respectively. And we copy the results of the other three
methods in the first block from Liu et al. (2023b). The
best results of each block are highlighted in bold.
Methods
Spider
Spider-
SYN
Spider-
Realistic
RAT-SQL + BERTLarge
72.3
-
62.1
TKK-Large
73.2
60.5
64.4
T5-3B + PICARD
79.3
69.8
71.4
RASAT + PICARD
80.5
70.7
71.9
RESDSQL-3B + NatSQL
84.1
76.9
81.9
Davinci-003
68.8
60.1
63.2
+ IRR (ours)
69.5
60.3
64.2
+ IRR (ours, few-shot)
72.7
63.2
70.7
ChatGPT
70.1
58.6
63.4
+ IRR (ours)
74.8
62.0
70.3
+ IRR (ours, few-shot)
77.8
64.0
72.0
then linearize them and compose the input prompt.
Here, we utilize the instruction (i.e., provide only
one relevant relation that’s present in the candidate)
to elicit the LLM to generate the most relevant rela-
tion, i.e., education. Based on the selected relation,
we further invoke the Extract_Triples function to
extract the triples with the relation to the topic en-
tity. After linearization, another instruction (i.e.,
you just need to provide only one answer entity), is
adopted for guiding the LLM to generate the final
answer, i.e., Monroe County High School. Besides,
we show the representative examples of TableQA
and Text-to-SQL in Appendix B.


</details>

### StructGPT · 块 27 · 页 8-9 · completed

`chunk_b21e952cc42e9ffedbde26c85006586c`；类型 body；跳过原因 None；2.86s；Token 889/8


<details><summary>完整来源块</summary>

Error Analysis. To systemically analyze the short-
comings of our approach, we first select three
datasets (i.e., WebQSP, WTQ, and Spider) with
different types of structured data, and randomly
sample 100 error cases from each dataset. Then,
we manually examine these failures and classify
them into five categories:
• Selection Error: the relevant information has
not been selected by the LLM.
• Reasoning Error: given the extracted relevant
information, the LLM fails to generate the ground-
truth answer or SQL.
• Generation Format Error: the generated an-
swer is in an abnormal format that fails to be iden-
tified by our result parser.
• Hallucination: the generated results are incon-
sistent with the extracted information.
• Other Errors: other uncategorizable errors.

Question: what highschool did harper lee go to?
Invoke: Extract_Neighbor_Relations (Harper Lee)
Return: [education … birthplace]
Generate
“(Harper Lee, education, CVT_0); … ”
Extract_Triples (Harper Lee, [education])
The candidate relations: education … birthplace.
The question is …
Provide only one relevant relation that's present 
in the candidates …
The relevant relation: education. 
The triples are: (Harper Lee, education, 
CVT_0) ... Based on these triples … give me 
the final answer entity.  
You just need to provide only one answer entity. 
If you think …
Answer: Monroe County High School
Generate
Return: 
[(Harper Lee, education, CVT_0) … ]
Linearize: 
Linearize: “education … birthplace”
CVT_0
Oxford
college
Harpe Lee
CVT_1
education
education
Monroe 
County
high 
school
type
type
···
···
institution
institution


</details>

### StructGPT · 块 28 · 页 9-9 · completed

`chunk_c9e4e94b591dab5929ea0ee5c7f0817b`；类型 body；跳过原因 None；2.63s；Token 807/8


<details><summary>完整来源块</summary>

···
residence
birthplace
···
CVT_0
Oxford
college
Harpe Lee
CVT_1
education
education
Monroe 
County
high 
school
type
type
···
···
institution
institution
···
residence
birthplace
···
Invoke: 
Figure 2: Case study of our method on WebQSP.
21%
63%
8%
4%4%
Spider (Text-to-SQL)
28%
30%
34%
8%
WikiSQL (TableQA)
Selection Error
Reasoning Error
Generating Format Error
Hallucination
Other Errors
74%
2%
8%
3%
13%
WebQSP (KGQA)
Figure 3: Proportions of different error types in three datasets over different types of structured data.
We show the statistics in Figure 3. First, for
the three datasets, the distributions of occurring
errors are different. In WikiSQL, the frequencies
of generation format, selection, and reasoning er-
rors are relatively uniform. Whereas, in WebQSP,
the selection error is the major error type (74%),
since the KGQA task requires selecting the most
relevant one from thousands of relations, which is
not easy work. In Spider, reasoning error occurs
more (62%), since the Text-to-SQL task requires
LLMs to generate a SQL that can be executed to
obtain the answer, which is also hard for LLMs.


</details>

### StructGPT · 块 29 · 页 9-9 · completed

`chunk_8d5981baad51236ec56533d7ee1eaf56`；类型 body；跳过原因 None；2.37s；Token 605/8


<details><summary>完整来源块</summary>

According to the error distributions, it is promis-
ing to refine the major error cases to specifically im-
prove the performance on each dataset. Concretely,
we can devise more high-quality prompts that elicit
LLMs to carefully make decisions when selecting
and reasoning on KGQA and Text-to-SQL tasks, re-
spectively. Besides, we also consider adding more
interfaces and iteration turns for decomposing the
hard problem into multiple simple ones, to simplify
the complex reasoning task for better performance.
We will try the above solutions in our future work.
6


</details>

### StructGPT · 块 30 · 页 9-10 · completed

`chunk_bd4734d2765e2147cac924fe8ba38d85`；类型 body；跳过原因 None；80.87s；Token 711/359

- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "StructGPT", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "specialized interfaces", "evidence_quote": "we first constructed the specialized interfaces that support accurate and efficient data access, and then proposed an invoking-linearization-generation procedure that leverages LLMs to read and perform reasoning based on the interface.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Method", "subject": "StructGPT", "predicate": "HAS_COMPONENT", "object_type": "Component", "object": "invoking-linearization-generation procedure", "evidence_quote": "we first constructed the specialized interfaces that support accurate and efficient data access, and then proposed an invoking-linearization-generation procedure that leverages LLMs to read and perform reasoning based on the interface.", "claim_kind": "author_assertion", "confidence": 1.0}
- 拒绝 `evidence_quote_not_in_chunk`：{"subject_type": "Component", "subject": "invoking-linearization-generation procedure", "predicate": "IMPLEMENTS", "object_type": "Mechanism", "object": "LLMs to read and perform reasoning based on the interface", "evidence_quote": "we first constructed the specialized interfaces that support accurate and efficient data access, and then proposed an invoking-linearization-generation procedure that leverages LLMs to read and perform reasoning based on the interface.", "claim_kind": "author_assertion", "confidence": 1.0}

<details><summary>完整来源块</summary>

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


</details>

### StructGPT · 块 31 · 页 10-10 · completed

`chunk_393f6af76087a71bf9db9f2bb64f4662`；类型 body；跳过原因 None；3.33s；Token 708/8


<details><summary>完整来源块</summary>

Limitations
Although StructGPT demonstrates remarkable per-
formance across tasks over structured data, there
are some limitations of our method.
First, the
two LLMs used in our model, i.e., ChatGPT and
Davinci-003, have a strong capability of following
instructions. Hence, more experiments are required
to evaluate our method with in-context learning
on other LLMs that perform poorly at instruction
following. Similarly, we only evaluate question
answering tasks based on structured data. Future
work should include wider evaluation scenarios
to evaluate the universality of our method, e.g.,
data-to-text and formal-language-to-text (Xie et al.,
2022). Finally, since it is difficult to control the an-
swer format during the generation process of LLMs
in different datasets, there are several format errors
in generated texts as shown in Section 5. Therefore,
the performance of our method can be further im-
proved by meticulously designing the prompt and
answer parsing for different datasets.


</details>

### StructGPT · 块 32 · 页 10-10 · completed

`chunk_a50a6e195a0ad65f6376744d407841fd`；类型 body；跳过原因 None；2.38s；Token 589/8


<details><summary>完整来源块</summary>

Acknowledgments
This work was partially supported by National Nat-
ural Science Foundation of China under Grant No.
62222215, Beijing Natural Science Foundation un-
der Grant No. 4222027 and L233008. And this
work is also partially supported by the Outstanding
Innovative Talents Cultivation Funded Programs
2022 of Renmin University of China. Xin Zhao is
the corresponding author.


</details>

### STaRK · 块 0 · 页 1-1 · skipped

`chunk_8de1e06d1827ae3f8e7d83e7e454573b`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

STARK: Benchmarking LLM Retrieval on Textual
and Relational Knowledge Bases
Shirley Wu∗§, Shiyu Zhao∗§, Michihiro Yasunaga§, Kexin Huang§, Kaidi Cao§, Qian Huang§,
Vassilis N. Ioannidis†, Karthik Subbian†, James Zou‡§, Jure Leskovec‡§
§Department of Computer Science, Stanford University
†Amazon
https://stark.stanford.edu/


</details>

### STaRK · 块 1 · 页 1-1 · skipped

`chunk_6b5383484693f6226010eab8143f80d6`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

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


</details>

### STaRK · 块 2 · 页 1-2 · skipped

`chunk_2c06f903c181ffbdb1246026daa909b0`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

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


</details>

### STaRK · 块 3 · 页 2-2 · skipped

`chunk_66ad8da2f5e6a86bcc68ea9123cfaaad`；类型 table；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Could you provide a list of investigational drugs that
<(S)-3-phenyllactic Acid>,
interact with genes or proteins active in the epididymal region?
<Anisomycin>, <Puromycin>
Search for diseases without known treatments and induce
<Intrahepatic Cholestasis>
pruritus in pregnant women, potentially associated with Autoimmune.
Please find pathways involving the POLR3D gene within nucleoplasm.
<RNA Polymerase III Chain Elongation>
Which gene or protein associated with lichen amyloidosis can
<OSMR>, <IL31RA>
bind interleukin-31 to activate the PI3K/AKT and MAPK pathways?
Table 1: STARK QA examples which involve semi-structured (relational and textual) information.
1


</details>

### STaRK · 块 4 · 页 2-2 · skipped

`chunk_6eeace58b42c6743729b039d5685093b`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Introduction
Natural-language queries are the primary form of how humans acquire information [17, 21, 27].
For example, users on e-commerce sites wish to express complex information needs by combining
free-form elements and constraints, such as “Can you help me find a push-along tricycle from
Radio Flyer that’s both fun and safe for my kid?”in product search. Medical scientists may ask
questions like “What disease is associated with the PNPLA8 gene and presents with hypotonia as a
symptom?”. Answering such queries is crucial for enhancing user experience, supporting informed
decision-making, and preventing hallucination.


</details>

### STaRK · 块 5 · 页 2-2 · skipped

`chunk_e820b5ccf6fdbe423d102b79202b58a6`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

To answer such queries, the underlying knowledge can be represented in semi-structured knowledge
bases (SKBs) [35, 40, 50], which integrate unstructured data, such as natural language descriptions
and expressions (e.g., description of the tricycle), with structured data, like entity interactions on
knowledge graphs (e.g., a tricycle “brand” is Radio Flyer). This allows the SKBs to represent
comprehensive knowledge in specific applications, making them indispensable in domains such as
e-commerce [15], social media [31], and precision medicine [8, 18, 23].
Limitations of prior works. Prior works focused on either purely textual queries on unstructured
knowledge [12, 14, 20, 24, 25, 29, 53, 55] or structured SQL [59, 59, 60, 60] or knowledge graph
queries [2, 4, 7, 13, 16, 45–47, 57, 58], which are limited in the span of knowledge and inadequate
to study the complexities of retrieval on SKBs. Recently, large language models (LLMs) have
demonstrated significant potential on information retrieval tasks [14, 30, 43, 61]. Nevertheless, it
remains an open question of how effectively LLMs can be applied to the challenging retrieval tasks
on SKBs. Moreover, the existing works mainly focus mainly on general knowledge, e.g., from
Wikipedia. However, the knowledge may commonly come from private sources, requiring retrieval
systems to operate on private SKBs. Therefore, there is a gap of how current LLM retrieval systems
handle the complex textual and relational requirements in queries that can involve private knowledge.
Present work. To address this gap, we present 

</details>

### STaRK · 块 6 · 页 2-3 · skipped

`chunk_d2b23cd8bdf5bc8999476417e6019f5b`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

a large-scale Semi-structure retrieval benchmark
on Textual and Relational Knowledge Bases (STARK) (Figure 1). The key technical challenge
that we solve is how to accurately simulate user queries on SKBs. This difficulty arises from the
interdependence of textual and relational information, which leads to challenges in precisely construct
the ground-truth answers from millions of candidates. Additionally, ensuring that queries are useful
and resembles real-world scenarios adds further complexity to the benchmarking process.
We develop a novel pipeline that simulates user queries and constructs precise ground truth answers
using three SKBs built from extensive texts and millions of entity relations from public sources. We
validate the quality of queries in our benchmark through detailed analysis and human evaluation,
focusing on their naturalness, diversity, and practicality. Furthermore, we incorporate 274 human-
generated queries to compare with synthesized queries and enrich the testing scenarios. With STARK,
we delve deeper into retrieval tasks on SKBs, evaluate the capability of current retrieval systems, and
provide insights for future advancement. Key features of STARK are:
• Natural-sounding queries on SKBs (Table 1): Queries in our benchmark incorporate rich
relational information and complex textual properties. Additionally, these queries closely mirror
the types of questions users would naturally ask in real-life scenarios, e.g., with flexible query
formats and possibly with additional contexts.
2

has brand
has
brand


</details>

### STaRK · 块 7 · 页 3-3 · skipped

`chunk_ce6e94a5f51961056f7e4bb8fd4c9092`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Title: Ultimate Stroll 'N Tricycle
Feature: - AGES 1 TO 5 YEARS ...
Dimensions: 37.2”x34.3”x22”
Description: The ultimate grow-with-me 
trike. There are 4 ways to ride ...
Review: #1 :Very sturdy and good ...
Customer Q&A:
Q: Is it easy to assemble?
A: Semi - easy to assemble :-) ...
has
brand
has
brand
also
bought
Amazon Semi-structured Knowledge Base
also
viewed
MAG Semi-structured Knowledge Base
paper has
field of study
author writes paper
author belongs
to institute
paper
cites paper
paper cites paper
Prime Semi-structured Knowledge Base
author
writes paper
Drug
Gene
Protein
Disease
Molecular function
Anatomy
Pathway
interact with
carrier
interact with
carrier
expression
present
interact with
indication/contraindication
Phenotype
present/absent
associated 
with
Name: GPANK1
Alias: DYRK1AP3,
PAHX-AP, PAHXAP1
Description: 
This gene encodes 
a protein which is 
thought to play a 
role in immunity.
Multiple alternatively 
spliced variants, 
encoding the same 
protein, have been 
identified.
Name: GM1 
gangliosidosis type I
Definiton:
GM1 gangliosidosis 
type 1 is the severe 
infantile form of GM1 
gangliosidosis with 
variable neurological 
manifestations... 
Epidemiology: 
Type 1 is the most 
frequent form but the 
exact prevalence is 
not known.
paper has
field of study
author
writes paper
. . .
has color
Red
Wooden
Furniture
has
category
Pink
has color
Title: Distribution of non-Markovian 
intervals for open qubit systems
Abstract: We study non-
Markovianity of open qubit systems
Publication Date: 2011-11-01
Venue: Chinese Physics B


</details>

### STaRK · 块 8 · 页 3-3 · skipped

`chunk_77331dc18e1518cd0c883724d737af4f`；类型 body_mixed；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Figure 2: Demonstration of Semi-structured Knowledge Bases, where each knowledge base combines
both textual and relational information in a complex way, making the retrieval tasks challenging.
• Context-specific reasoning: The queries entail reasoning capabilities specific to the context. This
includes the ability to infer customer interests, understand specialized field descriptions, and deduce
relationships involving multiple subjects mentioned within the query. For example, the context “I
had a dozen 2.5-inch Brybelly air hockey pucks, so I’m trying to find matching strikers.” entails the
user’s interest in looking for complementary products. Such reasoning capabilities are crucial for
accurately interpreting and responding to the nuanced requirements of each query.
• Diverse domains: Our benchmark spans three knowledge bases* for applications including product
recommendation, academic paper search, and precision medicine inquiries. STARK provides a
comprehensive evaluation of retrieval systems across diverse contexts and domains.
We conduct extensive experiments on LLM retrieval systems, highlighting challenges in handling
textual and relational data and latency on large-scale SKBs with millions of entities or relations.
Finally, we offer insights into building more capable retrieval systems to handle real-world complexity.
2
Benchmarking Retrieval Tasks over Textual and Relational Knowledge
2.1
Problem Definition


</details>

### STaRK · 块 9 · 页 3-4 · skipped

`chunk_55f5c53241444144d0171ae7918bf3da`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

We are given a Semi-Structured Knowledge Base (SKB), which consists of a knowledge graph
G and a collection of free text documents D. Formally, let G = (V, E) be the knowledge graph,
where V is the set of nodes and E ⊆V × V is the set of edges representing relationships between
nodes. D = S
i∈V Di be the collection of free-form text documents associated with the nodes,
where Di is the set of documents associated with node i. For example, the product knowledge graph
in e-commerce can capture relationships between products and brands/colors/categories, and the
corresponding text documents include product descriptions, reviews, etc.
We define the tasks on our benchmark datasets as follows: Given the knowledge graph G = (V, E), a
collection of free text documents D, and a query Q, the output is a set of nodes A ⊆V such that for
each node i ∈A, it satisfies the relational requirements imposed by the structure of G as specified in
Q, and the associated documents Di satisfy the textual requirements specified in Q.
2.2
Semi-structured Knowledge Bases (SKBs)
As shown Figure 2, we construct three large-scale SKBs with the relational and textual information
with each entity. See Table 2 for the basic data statistics and Appendix A.1 for details.
*Explore the SKBs at https://stark.stanford.edu/skb_explorer.html
3

Table 2: Data statistics of our constructed semi-structured knowledge bases
#entity
#relation
avg.
#entities
#relations
#tokens
types
types
degree


</details>

### STaRK · 块 10 · 页 4-4 · skipped

`chunk_ff801092852abe64c55baf9fb9177ccc`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

STARK-AMAZON
4
5
18.2
1,035,542
9,443,802
592,067,882
STARK-MAG
4
4
43.5
1,872,968
39,802,116
212,602,571
STARK-PRIME
10
18
125.2
129,375
8,100,498
31,844,769


</details>

### STaRK · 块 11 · 页 4-4 · skipped

`chunk_f10698cd511919a68438905eb9971303`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Amazon Semi-structured Knowledge Base. The SKB features four entity types: product,
brand, color, and category, and five relation types: also_bought, also_viewed be-
tween product entities, and has_brand/color/category associated with the products. We
derive the textual information of product nodes by combining Amazon Product Reviews [15] with
Amazon Q&A Data [32]. This provides a rich amount of texts, including product descriptions and
customer reviews. For other entities, we extract their names or titles as the textual attributes. Amazon
SKB features an extensive textual data largely contributed from customer reviews and Q&A.
MAG Semi-structured Knowledge Base. This SKB includes node entities of paper, author,
institute, and field_of_study. We derive its relational structure by extracting a subgraph
from obgn-mag [19], which contains shared paper nodes with obgn-papers100M [19] and all non-
paper nodes. We filter out non-English language papers as we only consider single-lingual queries.
The paper documents include their titles and abstracts. Additionally, we integrating details from
the Microsoft Academic Graph database (version 2019-03-22) [44, 50], providing extra textual
information like paper venue, author and institution names. This SKB demonstrates a large number
of relations associate with paper nodes, especially on citation and authorship relations.
Prime Semi-structured Knowledge Base. We leverage the exisiting knowledge graph PrimeKG [8]
which contains ten entity types including disease, gene/protein, and eighteen relation
types, such as associated_with, indication. Compared to the Amazon and MAG SKBs,
Prime SKB is 

</details>

### STaRK · 块 12 · 页 4-4 · skipped

`chunk_73977e3c45d03873b66abdf8357638dd`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

denser and features a greater variety of relation types. While PrimeKG provides
text information on disease and drug entities, we integrate the data from multiple databases
for gene/protein and pathway entities such as genomic position, gene activity summary and
pathway orthologous event.
2.3
Retrieval Tasks on Semi-structured Knowledge Bases


</details>

### STaRK · 块 13 · 页 4-4 · skipped

`chunk_2e5c252a20f9d962ff5b880ff6b29e54`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Our retrieval benchmark (Table 3) consists of three novel retrieval-based question-answering datasets,
each comprising synthesized train/val/test sets with 9k to 14k queries in total and a high-quality
human-generate query set. The queries synthesize relational and textual knowledge, mirroring
real-world queries in terms of natural-sounding property and flexible formats.
STARK-AMAZON. The task aims at product recommendation, with a notable 68% of the synthesized
queries yielding more than one ground truth answer. The dataset prioritizes customer-oriented criteria,
highlighting textual elements such as product quality, functionality, and style. Moreover, it incorporate
single-hop relational aspects (Appendix A.2) into the queries, including brand, category, and product
connections (e.g., complementary or substitute items). The queries are framed in conversation-like
formats, enriching the context and enhancing the dataset’s relevance to real-world scenarios.
STARK-MAG. Beyond the single-hop relational requirements in STARK-AMAZON, STARK-
MAG emphasizes the fusion between the textual requirements with multi-hop queries for precise
academic paper search. For example, “Are there any papers from King’s College London” highlights
the metapath (institution →author →paper) on the relational structure. We designed
three single-hop and four multi-hop relational query templates (Appendix A.3). The textual aspects
focus on the paper’s topic, methodology, and contribution etc.
STARK-PRIME. The task is to answer complex biomedicine inquiries. For synthesized queries, we
developed 28 multi-hop query template

</details>

### STaRK · 块 14 · 页 4-5 · skipped

`chunk_a430196a4fbe542e637ec87530659be3`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

s (Appendix A.4) to cover various relation types and ensure
their practical relevance. For example, the template “What is the drug that targets genes or proteins
in <anatomy>?” aids precision medicine by identifying treatments targeted to specific anatomical
areas. For drug, disease, gene/protein, and pathway entities, the queries are a hybrid
of relational and textual requirements. For entities such as effect/phenotype, the queries rely
solely on relational data due to limited textual information. We exhibit three distinct user roles –
medical scientist, doctor, and patient – for generating queries about drug and disease, which diversify
the language to comprehensively evaluate the retrieval systems.
4

Table 3: Statistics on the STARK benchmark datasets.
#queries
#queries w/
average
train / val / test
multiple answers
#answers
Synthesized
(Sec 2.4, 2.5)
STARK-AMAZON
9,100
7,082
17.99
0.65 / 0.17 / 0.18
STARK-MAG
13,323
6,872
2.78
0.60 / 0.20 / 0.20
STARK-PRIME
11,204
4,188
2.56
0.55 / 0.20 / 0.25
Human-generated
(Sec 2.6)
STARK-AMAZON
81
64
19.50
For testing only
STARK-MAG
84
34
3.26
STARK-PRIME
98
41
2.77
Instantiate
Semi-structured
Knowledge Base
Relation template
Check satisfaction
e.g., “Belongs to Radio Flyer”
②Textual properties
Products
①
Relational
information
Filtering nodes
Extract
④Ground truth nodes
③Query
Gold node
Filtered node
“Can you help me find a push-along 
tricycle from Radio Flyer that’s both 
fun and safe for my kid?””


</details>

### STaRK · 块 15 · 页 5-5 · skipped

`chunk_b8338106a2a8141a9afa85360439cfc4`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

1) “push-along tricycle” (Source from Description)
2) “fun and safe for kids” (Source from Review: “My 
son loves it and still rides it at 3!... Very safe as long
as the big kids don't ride it and scrape their knees…”)
<Tricycle #1>, < Tricycle #2>
Radio Flyer Products
Other nodes
…
Figure 3: The construct pipeline to generate our semi-structured retrieval datasets.
2.4
Benchmark Construction: Synthesized Queries
In Figure 3, we present a novel pipeline that synthesizes the SKB queries and automatically generates
the ground truth answers. The key idea is to entangle relational and textual information during
synthesis and disentangle them during answer filtering. It involves four steps as follows:


</details>

### STaRK · 块 16 · 页 5-5 · skipped

`chunk_aa14e2cd58a1f4d4b47738406e4cecde`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

• 1) Sample Relational Requirements: For each query, we sample a practical relation template
constructed with expert/domain knowledge, e.g., “(a product) belongs to <brand>”
and ground it with sampled entities (i.e., a specific brand), e.g., “belongs to Radio Flyer”. This
relational requirement yields a set of candidate entities, i.e., products belonging to Radio Flyer.
• 2) Extracting Textual Properties: We randomly sample a candidate entity from the first step,
referred to as the gold answer, from which LLMs extract properties that align with the interests
of specific roles (e.g., customers, researchers, or doctors) in its textual document. In Figure 3, we
extract multiple properties about the functionality and user experience from a Radio Flyer product.
• 3) Combining Textual and Relational Information: We use two LLMs to synthesize queries
from textual properties and relational requirements, enhancing diversity and reducing bias arise
from relying on a single LLM. The first LLM focuses on generating natural, role-specific, and
style-consistent (e.g., ArXiv searches) queries. The second LLM enriches the context and rephrases
queries, which poses the need for advanced reasoning to comprehend them under complex contexts.
• 4) Filtering Additional Answers: Finally, we employ multiple LLMs to verify if the candidates
from the first step meet the extracted textual properties. Only candidates passing all LLM verifica-
tions are included in the final ground truth set. To assess the precision of this filtering mechanism,
we compute the average ratios for the gold answers to be verified, which are 86.

</details>

### STaRK · 块 17 · 页 5-6 · skipped

`chunk_96e9fcf05033660e3eaa3b9e533528fe`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

6%, 98.9%, and
92.3% on the three datasets, highlighting our efficacy in yielding high-quality ground truth answers.
This dataset construction pipeline is automatic, efficient, and broadly applicable to the SKBs in our
formulation. We include all of the prompts and the LLMs versions in the above steps in Appendix E.
2.5
Synthesized Data Distribution Analysis and Human Evaluation
• Query and Answer Length. Query length (in words) reflects the amount of user-provided context
information, while the number of answers indicates query ambiguity/concreteness. Figure 4 shows
similar query length distributions across the datasets, with most queries around 16 words. Longer
queries (up to 50 words) often mention other entities or provide detailed context. Notably, STARK-
AMAZON has a significant long-tail pattern, with about 22% of the answers have more than 30
entities, reflecting diverse e-commerce recommendations and ambiguous user queries.
5

Query length
Density
Answer length
STARK-AMAZON
STARK-MAG
STARK-PRIME
STARK-AMAZON
STARK-MAG
STARK-PRIME
Figure 4: Distribution of query and answer lengths on STARK datasets.
Table 4: Query diversity measurement on STARK.
See Appendix B for the metric definition.
Shannon Entropy
Type-Token Ratio
STARK-AMAZON
10.39
0.179
STARK-MAG
10.25
0.180
STARK-PRIME
9.63
0.143
Reference article
10.44
0.261
Figure 5: Average relative composition of rela-
tional vs. textual information.
Textual Information
Relational Information
STARK-AMAZON
STARK-MAG
STARK-PRIME


</details>

### STaRK · 块 18 · 页 6-6 · skipped

`chunk_14422ecb69f88241dd100b309916fc19`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

• Query Diversity. A diverse set of queries poses challenges for broader applicability to meet
varying user demands. We measure query diversity using Shannon Entropy for word distribution
and Type-Token Ratio (TTR) for unique words. Higher values indicate greater lexical diversity.
Table 4 shows high Shannon Entropy and steady TTR across all datasets. For reference, we compute
these metrics for the Wikipedia page of Barack Obama†.
• Proportionality of Relational vs.Textual Information. Our benchmark queries feature the com-
position of textual and relational information. To understand the distribution of information types,
we calculate the average ratio of relational to textual requirements by word count in the queries
across each dataset. Note that the ratios do not directly reflect their importance in determining final
answers. Figure 5 shows varying ratios, which highlights different emphases on textual versus
relational requirements and challenges retrieval systems to adapt to different distributions.


</details>

### STaRK · 块 19 · 页 6-6 · skipped

`chunk_fae5216c8de50dfefc153da415610ba6`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Human evaluation. We qualitatively assess sampled queries from our benchmark for naturalness
(resembling natural conversation), diversity (covering various question structures and complexities),
and practicality (relevance to real-world situations) with 63 participants. Evaluation results, converted
from a 5-point Likert-like scale to a positive/tie/negative scale, show positive and non-negative rates
in Table 10 (Appendix D.1). On average, 94.1%, 85.3%, and 89.4% of participants rated the queries
neutral or above in naturalness, diversity, and practicality, respectively. These results validate the
quality of our benchmark and its potential for diverse and realistic retrieval tasks.
2.6
Benchmark Construction: Human-Generated Queries


</details>

### STaRK · 块 20 · 页 6-7 · skipped

`chunk_40c7a8566795976b09d6c0cad5592aec`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

To enhance our benchmark’s practical relevance, we engaged 31 participants (22 native English
speakers) to generate 263 queries across three SKBs following the detailed instructions (Appendix C)
along with our interactive platform. We manually verified and filtered the ground truth answers to
ensure the answer correctness. Table 3 shows the statistics of the human-generated datasets. Finally,
we analyzed the commonalities and differences between synthesized and human-generated queries.
Commonality. The number of answers of synthesized and human-generated queries are comparable,
indicating a similar level of query ambiguity. Moreover, we observe that most styles of human-
generated queries are covered in the synthesized dataset. For example, Table 5 highlights their
similarities in short product queries, specific author/field inquiries, and complex contextual queries.
Difference. We find that human-generated queries often exhibit more unique expressions compared
to synthesized ones, such as "Give me a fat cross and road tire that works with my Diamondback
bicycle tube" and "this sneaky bone-killing culprit". This discovery suggests a future direction for
our benchmark to incorporate modern and dynamic language nuances.
†https://en.wikipedia.org/wiki/Barack_Obama
6

Table 5: Comparison of Human-generated and Synthesized Queries
Query Type
Human-generated Query
Synthesized Query
Short and Direct
Red sweatshirt for proud Montreal Cana-
diens
Suggestions for a Suunto bike mount?
Specific
Author & Field
Find me papers that discuss improving
condenser performance authored by
Stojan Hrnjak
Show me papers by Seung-Hyeok Kye that
discuss separability criteria.
Complex Context


</details>

### STaRK · 块 21 · 页 7-7 · skipped

`chunk_0d073822f79abb22a99653ed90478ed9`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Help me. I am trying to diagnose a patient
with persistent joint pain, and I suspect a
condition where the bone is dying due to
compromised blood supply, often linked
to factors like steroid use, ... what’s the
name of this sneaky bone-killing culprit?
I’m experiencing joint pain accompanied
by swelling... I’m concerned about med-
ications aggravating my fuzzy eyesight
and potential blood clotting complica-
tions. Could you recommend treatments
while minimizing these side effects?
3


</details>

### STaRK · 块 22 · 页 7-7 · skipped

`chunk_9d9ee136eacc99fb94f97a46f3bb2c7b`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Experiments
3.1
Baseline Retrieval Models and Evaluation Metrics
We extensively evaluate five classes of retrieval models described below.
• Sparse Retriever: BM25 [39] is a traditional yet powerful sparse retrieval method based on term
frequency-inverse document frequency (TF-IDF). It computes relevance scores by considering the
frequency of query terms in documents, adjusted for term rarity and document length.
• Small Dense Retrievers: DPR [26], ANCE [52], and QAGNN [56]. These compact models
generate dense embeddings for both queries and documents, computing retrieval scores based on
embedding similarities. They serve as baselines for comparison with LLM-based dense retrievers.
• LLM-based Dense Retrievers: text-embedding-ada-002 (abbrev. ada-002) [36], voyage-
large-2-instruct (abbrev. voyage-l2-instruct) [1], LLM2Vec-Meta-Llama-3-8B-Instruct-mntp
(abbrev. LLM2Vec) [3], and GritLM-7b [33]. These models leverage LLMs to generate dense
embeddings that are more contextually expressive.
• Multivector Retrievers: multi-ada-002 [36] and ColBERTv2 [41]. Beyond ada-002 which
represents a document as an embedding, multi-ada-002 splits each document into overlapping
chunks and embeds them using the same encoder as the query. Similarity scores between the query
and chunks are aggregated using the average of the top-3 similarities, which we found to perform
best. ColBERTv2 represents each document as multiple token-level embeddings for fine-grained
matching, capturing richer semantic information.


</details>

### STaRK · 块 23 · 页 7-7 · skipped

`chunk_bb730573725b148aa7913e7f17bb9261`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

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


</details>

### STaRK · 块 24 · 页 7-8 · skipped

`chunk_56985246c2b5e3130cfbdaafae0f9366`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

• Mean Reciprocal Rank (MRR) is a statistic for evaluating the average effectiveness of a predictive
model. It calculates the reciprocal of the rank at which the first relevant item appears in the list of
predictions. This metric emphasizes the importance of the rank of the first correct answer, which is
crucial in many practical applications where the first correct answer is often the most impactful.
7

Table 6: Testing results on STARK-Syn(thesized).


</details>

### STaRK · 块 25 · 页 8-8 · skipped

`chunk_0365cffe276d7592e2170b25f169cd95`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

STARK-AMAZON
STARK-MAG
STARK-PRIME
Hit@1
Hit@5
R@20
MRR
Hit@1
Hit@5
R@20
MRR
Hit@1
Hit@5
R@20
MRR
Full Testing Dataset
BM25
44.94
67.42
53.77
55.30
25.85
45.25
45.69
34.91
12.75
27.92
31.25
19.84
DPR (roberta)
15.29
47.93
44.49
30.20
10.51
35.23
42.11
21.34
4.46
21.85
30.13
12.38
ANCE (roberta)
30.96
51.06
41.95
40.66
21.96
36.50
35.32
29.14
6.53
15.67
16.52
11.05
QAGNN (roberta)
26.56
50.01
52.05
37.75
12.88
39.01
46.97
29.12
8.85
21.35
29.63
14.73
ada-002
39.16
62.73
53.29
50.35
29.08
49.61
48.36
38.62
12.63
31.49
36.00
21.41
voyage-l2-instruct
40.93
64.37
54.28
51.60
30.06
50.58
50.49
39.66
10.85
30.23
37.83
19.99
LLM2Vec
21.74
41.65
33.22
31.47
18.01
34.85
35.46
26.10
10.10
22.49
26.34
16.12
GritLM-7b
42.08
66.87
56.52
53.46
37.90
56.74
46.40
47.25
15.57
33.42
39.09
24.11
multi-ada-002
40.07
64.98
55.12
51.55
25.92
50.43
50.80
36.94
15.10
33.56
38.05
23.49
ColBERTv2
46.10
66.02
53.44
55.51
31.18
46.42
43.94
38.39
11.75
23.85
25.04
17.39
Random 10% Sample
BM25
42.68
67.07
54.48
54.02
27.81
45.48
44.59
35.97
13.93
31.07
32.84
21.68
DPR (roberta)
16

</details>

### STaRK · 块 26 · 页 8-8 · skipped

`chunk_68269bfac20d6385f48d0521476d3820`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

.46
50.00
42.15
30.20
11.65
36.84
42.30
21.82
5.00
23.57
30.50
13.50
ANCE (roberta)
30.09
49.27
41.91
39.30
22.89
37.26
44.16
30.00
6.78
16.15
17.07
11.42
QAGNN (roberta)
25.00
48.17
51.65
36.87
12.03
37.97
47.98
28.70
7.14
17.14
32.95
16.27
ada-002
39.02
64.02
49.30
50.32
28.20
52.63
49.25
38.55
15.36
31.07
37.88
23.50
voyage-l2-instruct
43.29
67.68
56.04
54.20
34.59
50.75
50.75
42.90
12.14
31.42
37.34
21.23
LLM2Vec
18.90
37.80
34.73
28.76
19.17
33.46
29.85
26.06
9.29
20.7
25.54
15.00
GritLM-7b
43.29
71.34
56.14
55.07
38.35
58.64
46.38
48.25
16.79
34.29
41.11
24.99
multi-ada-002
40.85
62.80
52.47
51.54
25.56
50.37
53.03
36.82
15.36
32.86
40.99
23.70
ColBERTv2
44.31
65.24
51.00
55.07
31.58
47.36
45.72
38.98
15.00
26.07
27.78
19.98
Claude3 Reranker
45.49
71.13
53.77
55.91
36.54
53.17
48.36
44.15
17.79
36.90
35.57
26.27
GPT4 Reranker
44.79
71.17
55.35
55.69
40.90
58.18
48.60
49.00
18.28
37.28
34.05
26.55
Table 7: Testing results on STARK-Human(-Generated).
STARK-AMAZON
STARK-MAG
STARK-PRIME


</details>

### STaRK · 块 27 · 页 8-8 · skipped

`chunk_7425ece3f15adbe76a360ccd771e494f`；类型 table；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Method
Hit@1
Hit@5
R@20
MRR
Hit@1
Hit@5
R@20
MRR
Hit@1
Hit@5
R@20
MRR


</details>

### STaRK · 块 28 · 页 8-8 · skipped

`chunk_de2dbf0e468f51f7e7ba04c99d9d85db`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

BM25
27.16
51.85
29.23
18.79
32.14
41.67
32.46
37.42
22.45
41.84
42.32
30.37
DPR (roberta)
16.05
39.51
15.23
27.21
4.72
9.52
25.00
7.90
2.04
9.18
10.69
7.05
ANCE (roberta)
25.93
54.32
23.69
37.12
25.00
30.95
27.24
27.98
7.14
13.27
11.72
10.07
QAGNN (roberta)
22.22
49.38
21.54
31.33
20.24
26.19
28.76
25.53
6.12
13.27
17.62
9.39
ada-002
39.50
64.19
35.46
52.65
28.57
41.67
35.95
35.81
17.35
34.69
41.09
26.35
voyage-l2-instruct
35.80
62.96
33.01
47.84
22.62
36.90
32.44
29.68
16.33
32.65
39.01
24.33
LLM2Vec
29.63
46.91
21.21
38.61
16.67
28.57
21.74
21.59
9.18
21.43
26.77
15.24
GritLM-7b
40.74
71.60
36.30
53.21
34.52
44.04
34.57
38.72
25.51
41.84
48.10
34.28
multi-ada-002
46.91
72.84
40.22
58.74
23.81
41.67
39.85
31.43
24.49
39.80
47.21
32.98
ColBERTv2
33.33
55.56
29.03
43.77
33.33
36.90
30.50
35.97
15.31
26.53
25.56
19.67
Claude3 Reranker
53.09
74.07
35.46
62.11
38.10
45.24
35.95
42.00
28.57
46.94
41.61
36.32
GPT4 Reranker
50.62
75.31
35.46
61.06
36.90
46.43
35.95
40.65
28.57
44.90
41.61
34.82
3.2
Results and Analysis


</details>

### STaRK · 块 29 · 页 8-8 · skipped

`chunk_a407e76d3edfaf1a9413559721b56299`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Results on synthesized queries. Table 6 presents the results on both the full synthesized test sets
and random 10% samples from these sets. In both cases, BM25, despite its simplicity, proves to
be a strong baseline, outperforming the dense retrieval models such as ANCE. We observe that
finetuned DPR and QAGNN, exhibit insufficient performance. This underperformance is likely due
to their relatively small model sizes and the risk of overfitting during training. These issues present
challenges in effectively training the models on SKBs, where the entity documents can be hard to
differentiate without capturing detailed information.
Among the larger models, ada-002 benefits from superior pretrained embeddings and significantly
outperforms LLM2Vec by a large margin. GritLM-7b delivers excellent performance, surpassing
the ada-002 model overall. In contrast, LLM2Vec underperforms due to its limited context length,
which is insufficient for encoding the lengthy documents in the SKBs. For multivector retrievers, we
found that multi-ada-002 generally outperforms ada-002, indicating that using multiple vectors per
document enhances retrieval effectiveness. Similarly, fine-grained representation allows ColBERTv2
to capture subtle semantic nuances between queries and documents, leading to largely improved
retrieval accuracy.


</details>

### STaRK · 块 30 · 页 8-9 · skipped

`chunk_5804814c1d568658cfb52af78d4849db`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

However, both GritLM-7b and ColBERTv2 generally underperform compared to the rerankers
on the random split, especially in terms of Hit@k metrics. This suggests that while these dense
retriever models effectively capture semantic information, they may not fully grasp the nuanced
relevance judgments required for top-tier retrieval performance. The rerankers, utilizing powerful
LLMs like GPT-4 (gpt-4-1106-preview) and Claude3 (claude-3-opus), excel by re-evaluating the
top candidates and assigning satisfaction scores based on a deeper understanding of the query and
document content. This process allows them to better discern subtle contextual cues and relational
8

Table 8: Latency (s) of the retrieval systems on STARK.
DPR
QAGNN
ada-002
multi-ada-002
Claude3 Reranker
GPT4 Reranker
STARK-AMAZON
2.34
2.32
5.71
4.87
27.24
24.76
STARK-MAG
0.94
1.35
2.25
3.14
22.60
23.43
STARK-PRIME
0.92
1.29
0.54
0.90
29.14
26.97
Average
1.40
1.65
2.83
2.97
26.33
25.05
A 
B 
C 
D
Title: Nonlinear piezoelectricity in 
… Modeling and experimental 
identification
Abstract: … model for … nonlinear 
piezoelectric … linear piezoelectric 
modeling … nonlinear coefficients
Institute: University of Michigan
Cites paper: 
1. … nonlinear piezoelectric 
vibrational … 2. … piezoelectric  
energy 4. … piezoelectric … 
(15 cited papers have related key 
words)
Title: Nonlinear optimization of 
acoustic energy harvesting using 
piezoelectric devices
Abstract: … piezoelectric inserts 
… nonlinear processing … 
piezoelectric actuators …


</details>

### STaRK · 块 31 · 页 9-9 · skipped

`chunk_08a5cd319ff231eccd2c5f254340213d`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Institute: Institut national des 
sciences Appliquées de Lyon
Cites paper: 7. … piezoelectric 
conversion … 9. … piezoelectric 
vibration … 
(2 cited papers have related key 
words)
Title: Modelling of hysteretic 
behavior of piezoceramic materials 
under electrical loading
Abstract: … piezoceramic materials 
… deformation of piezoceramics …
Institute: École nationale 
d'ingénieurs du Val de Loire
Cites paper: 


</details>

### STaRK · 块 32 · 页 9-9 · skipped

`chunk_0db666b43cd08db4f0f802be8e8740a5`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

1. Ultrasonic characterization of 
electrochemically etched porous 
silicon 
(0 cited paper has related key 
words)
Title: Modelling nonlinearity in 
piezoceramic transducers: …
Abstract: Quadratic nonlinear 
materials … weak nonlinearity … 
nonlinear response … nonlinear 
equivalent electrical circuits
Institute: École nationale 
d'ingénieurs du Val de Loire
Cites paper: 1. … fouling in a planar 
setup … 2. Second order ultrasonic 
guided wave mutual interactions … 
(0 cited paper has related key words)
Are there any Physics research 
papers from École nationale 
d'ingénieurs du Val de Loire that 
discuss nonlinear modeling of 
piezoelectric elements?
Ground truth:  [A , B] 
:
ada-002
Claude3 Reranker 
Rank
Rank
Figure 6: A case study on STARK-MAG shows that ada-002 overranks non-ground truth papers C
and D due to repeated keywords in the relational information “cites paper”. After reranking with
Claude3, it correctly prioritizes ground truth papers A and B with accurate reasoning and analysis.
information that dense retrievers might overlook. Consequently, LLM rerankers enhance retrieval
precision at the top ranks.


</details>

### STaRK · 块 33 · 页 9-9 · skipped

`chunk_a8be21889a1afd7a234a4d0521059da8`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Finally, regardless of the higher computational costs of the rerankers, their performance remains
suboptimal. For instance, the Hit@1 scores for the GPT-4 reranker are only about 18% on STARK-
PRIMEand 41% on STARK-MAG, indicating that the top-ranked answers are frequently incorrect.
Similarly, the Recall@20 metrics are below 60% across all datasets, with the GPT-4 reranker
achieving Recall@20 scores of 55% on STARK-AMAZON, 49% on STARK-MAG, and 34% on
STARK-PRIME. This suggests that the ranking results miss a significant portion of relevant answers.
The MRR scores are also relatively low, especially for STARK-PRIME, where the GPT-4 reranker
attains an MRR of only around 27%.
The insufficient performances may be attributed to the complexity and diversity of queries in SKBs,
where nuanced understanding and detailed contextual information are crucial. These findings highlight
significant room for improvement in the ranking process.
Results on human-generated dataset. Table 7 presents the testing results on the human-generated
datasets. For example, the rerankers consistently outperform others, showing their reasoning and
context understanding ability. Compared to the synthesized datasets, the performance on human-
generated queries is generally higher for most models, but the overall trends remain consistent. This
indicates that synthesized datasets may be more challenging, highlighting the complexity of the tasks
on our synthesized queries.


</details>

### STaRK · 块 34 · 页 9-9 · skipped

`chunk_a58abbb14497e4834ba62385406a1d89`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Another interesting observation is that the performance of the rerankers is particularly strong on
human-generated queries, which may contain more nuanced language and diverse expressions. This
suggests that rerankers excel in interpreting and leveraging the richness of human language to improve
retrieval accuracy.
Retrieval latency. Latency is crucial for practical retrieval systems, as users expect quick responses.
As shown in Table 8, we evaluated the latency of various models using a single NVIDIA A100-SXM4-
80GB GPU. We observed that the DPR and QAGNN models exhibit lower average latency, making
them suitable for time-sensitive applications. In contrast, the ada-002 and multi-ada-002 models
have moderate latency due to multiple API calls. However, when combined with LLM rerankers, the
9


</details>

### STaRK · 块 35 · 页 10-10 · skipped

`chunk_6dd550e53fe21bea25cc6a6fbe58e406`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

latency increases significantly due to the computational demands of these large models. Therefore, it
is important to balance accuracy and latency, especially for complex queries that require advanced
reasoning capabilities.
Case study. To highlight the importance of reasoning ability for achieving good performance on
our benchmark, we present a case study in Figure 6, comparing the ada-002 model with the Claude3
Reranker. In this example, the query requests papers from a specific institution on a particular
topic. The ada-002 model fails to address the relational aspect of the query because it embeds
entire documents without detailed analysis. This leads to high relevance scores for irrelevant papers
that frequently mention keywords like "nonlinear modeling" and "piezoelectric elements" but do
not satisfy the relational requirement. In contrast, the LLM reranker significantly improves the
results by reasoning about the relationship between the query and each paper, resulting in scores that
more accurately reflect relevance. This underscores the need for reasoning ability to grasp query
complexities.
4


</details>

### STaRK · 块 36 · 页 10-10 · skipped

`chunk_5aaf8c492d28eeeb1c3f69591282d64c`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Related Work


</details>

### STaRK · 块 37 · 页 10-10 · skipped

`chunk_12c7bf0f83434a3659f1e58beafe4b0a`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Unstructured QA Datasets. This research domain consists of methods for retrieving answers from
unstructured text, either from a single document [38] or multiple documents [12, 24, 49, 51, 54]. For
instance, SQuAD [38] is designed for answer extraction within a specific document, while approaches
like HotpotQA [54] and TriviaQA [24] extend to multi-document contexts. Additionally, some
studies utilize search engine outputs as a basis or supplementary data for question answering [28, 34].
However, unstructured QA datasets often lack the depth of relational reasoning commonly required
in answering complex user queries. In contrast, STARK contains queries demanding multi-hop
relational reasoning to challenge model’s ability of handling structured information.
Structured QA Datasets. These datasets challenge models to derive answers from structured sources
such as knowledge graphs [5–7, 13, 16, 47, 58] or tabular data [59, 60]. ComplexWebQuestions [47]
and GraphQA [16] propose challenges in interpreting complex queries and textualizing graph struc-
tures in KBQA, respectively. For tabular data, WikiSQL [60] focuses on translating queries to SQL
for single-table databases, whereas Spider [59] tackles multi-table scenarios. Despite the emphasis
on relational data, the restriction to predefined entities and relationships limits the scope of queries.
STARK integrates textual content within structured frameworks to enhance the depth and breadth of
information retrieval, promoting richer and more nuanced understanding from extensive textual data.
Semi-Structured QA Datasets. This category merges tabular and textual data, presenting challenges
in semi-structur

</details>

### STaRK · 块 38 · 页 10-10 · skipped

`chunk_d1cc05944fdd1169c721b7f82ce10526`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

ed data comprehension. WikiTableQuestions [37] stresses the integration of table
structures with textual elements. TabFact [9], HybridQA [10], and TabMCQ [22] extend this by
combining validation of textual statements with tabular reasoning. However, datasets leveraging
tables as structured frameworks often lack in depicting the rich relational dynamics among entities.
Moreover, prior efforts to link textual and tabular information via external sources have led to
cumbersome data constructs. Addressing these challenges, STARK enhances integration, allowing
for flexible navigation and advanced retrieval within complex semi-structured knowledge bases, and
facilitating more effective relational reasoning and text handling.
5
Conclusion and Future Work
We introduce STARK, the first benchmark to thoroughly evaluate LLM-driven retrieval systems for
semi-structured knowledge bases (SKBs). Featuring diverse, natural-sounding queries that require
context-specific reasoning across diverse domains, STARK sets a new standard for assessing real-
world retrieval systems. We contribute three large-scale retrieval datasets with human-generated
queries and an automated pipeline to simulate realistic user queries. Our experiments on STARK
highlight significant challenges for current models in effectively handling textual and relational
information. STARK paves the way for future research to advance complex, multimodal retrieval
systems, focusing on reducing retrieval latency and enhancing reasoning abiliites.


</details>

### STaRK · 块 39 · 页 10-11 · skipped

`chunk_e0fb338e0bd10ff3cc732c529d93033c`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Our current SKBs are limited to textual and relational information. Future work should incorporate
additional modalities such as images, videos, and speech to provide a more comprehensive information
retrieval system. Despite our anonymization efforts, we acknowledge that privacy remains a potential
concern when extending this work to other domains with real user data, which should be protected to
ensure compliance with privacy regulations.
10

6


</details>

### STaRK · 块 40 · 页 11-11 · skipped

`chunk_68e658fc4bda21abe2f53ef03452993d`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Acknowledgement
We thank group members in Leskovec and Zou labs for providing valuable suggestions and conducting
benchmark construction. We express our gratitude to the following individuals for their assistance in
generating the human-generated queries (ordered by last name):
Michael Bereket, Charlotte Bunne, Yiqun Chen, Ian Covert, Alejandro Dobles, Teddy Ganea,
Bryan He, Mika Sarkin Jain, Weixin Liang, Gavin Li, Jiayi Li, Sheng Liu, Michael Moor, Hamed
Nilforoshan, Rishi Puri, Rishabh Ranjan, Yanay Rosen, Yangyi Shen, Jake Silberg, Elana Simon,
Rok Sosic, Kyle Swanson, Nitya Thakkar, Rahul Thapa, Kevin Wu, Eric Wu, Kailas Vodrahalli.
We especially thank Gavin Li at Stanford University and Zhanghan Wang at New York University for
helping build the interactive interface for our SKBs.
We gratefully acknowledge the support of DARPA under Nos. N660011924033 (MCS); NSF under
Nos. OAC-1835598 (CINES), CCF-1918940 (Expeditions), DMS-2327709 (IHBEM); Stanford Data
Applications Initiative, Wu Tsai Neurosciences Institute, Stanford Institute for Human-Centered AI,
Chan Zuckerberg Initiative, Amazon, Genentech, GSK, Hitachi, SAP, and UCB.


</details>

### STaRK · 块 53 · 页 16-16 · skipped

`chunk_c21aee35b1a9dfd3cb576e5bfb5a4c6c`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

A.2
STARK-AMAZON
Relational query templates. These are the basic relational templates on STARK-AMAZON. Note
that the final relational template can be composed of multiple basic templates. For example, ‘(color
→product ←brand)’ represents a relational template combined from two basic relational
templates.
metapath
Query template
(brand →product)
"Can you list the products made by <brand>?"
(product →product)
"Which products are similar to <product>?"
(color →product)
"Can you provide a list of products that are available in <color>?"
(category →product)
"What products are available in the <category> category?"


</details>

### STaRK · 块 54 · 页 16-17 · skipped

`chunk_10d454ac29067e7d1a22b8d6200af9e5`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

A.3
STARK-MAG
Relational query templates. We constructed seven relational templates below:
16

metapath
multi-hop query template
(author →paper)
"Can you list the papers authored by <author>?"
(paper →paper)
"Which papers have been cited by the paper <pa-
per>?"
(field_of_study →paper)
"Can you provide a list of papers in the field of
<field_of_study>?"
(institution →author →paper)
"What papers have been published by researchers
from <institution>?"
(paper →author →paper)
"What papers have been published by researchers
that are coauthors of <paper>?"
(paper →author →paper
←field_of_study ←paper)
"Can you find papers that share a coauthor with
<paper> and are also in the same field of study?"
(institution →author →
paper ←field_of_study)
"Are there any papers associated with <institu-
tion> and are in the field of <field_of_study>?"
For
example,
the
metapath
(field_of_study →paper)
requires
an
initial
field_of_study entity to be filled in the corresponding query template. For multi-hop metapaths,
the last metapath (institution →author →paper ←field_of_study) requires
an institution entity and a field_of_study entity to initialize the query.


</details>

### STaRK · 块 55 · 页 17-17 · skipped

`chunk_32b00088ff0d314f29a780a21391a70c`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

A.4
STARK-PRIME
Relational query templates. For synthesized queries, we listed 28 multi-hop templates designed by
experts to cover various relation types and ensure their practical relevance.
For instance, the query “What is the drug that targets the genes or proteins expressed in <anatomy>?”
serves applications in precision medicine and pharmacogenomics, aiding researchers and healthcare
professionals in identifying drugs that act on genes or proteins associated with specific anatomical
areas and enabling more targeted treatments.
{
(effect/phenotype →[phenotype absent] →disease ←[!indication] ←drug):
"Find diseases with zero indication drug and are associated with <effect/phenotype>",
(drug →[contraindication] →disease ←[associated with] ←gene/protein):
"Identify diseases associated with <gene/protein> and are contraindicated with <drug>",
(anatomy →[expression present] →gene/protein ←[expression absent] ←anatomy):
"What gene or protein is expressed in <anatomy1> while is absent in <anatomy2>?",
(anatomy →[expression absent] →gene/protein ←[expression absent] ←anatomy):
"What gene/protein is absent in both <anatomy1> and <anatomy2>?",
(drug →[carrier] →gene/protein ←[carrier] ←drug):
"Which target genes are shared carriers between <drug1> and <drug2>?",
(anatomy →[expression present] →gene/protein →[target] →drug):
"What is the drug that targets the genes or proteins which are expressed in <anatomy>?",
(drug →[side effect] →effect/phenotype →[side effect] →drug):


</details>

### STaRK · 块 56 · 页 17-17 · skipped

`chunk_2d02555ebc9e77b34cf8306f68144ddc`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

"What drug has common side effects as <drug>?",
(drug →[carrier] →gene/protein →[carrier] →drug):
"What is the drug that has common gene/protein carrier with <drug>?",
(anatomy →[expression present] →gene/protein →enzyme →drug):
"What is the drug that some genes or proteins act as an enzyme upon,
where the genes or proteins are expressed in <anatomy>?",
(cellular_component →[interacts with] →gene/protein →[carrier] →drug):
"What is the drug carried by genes or proteins that interact with <cellular_component>?",
(molecular_function →[interacts with] →gene/protein →[target] →drug):
"What drug targets the genes or proteins that interact with <molecular_function>?",
(effect/phenotype →[side effect] →drug →[synergistic interaction] →drug):
"What drug has a synergistic interaction with the drug that has <effect/phenotype>
as a side effect?",
(disease →[indication] →drug →[contraindication] →disease):
"What disease is a contraindication for the drugs indicated for <disease>?",
(disease →[parent-child] →disease →[phenotype present] →effect/phenotype):
"What effect or phenotype is present in the sub type of <disease>?",
(gene/protein →[transporter] →drug →[side effect] →effect/phenotype):
"What effect or phenotype is a [side effect] of the drug transported by <gene/protein>?",
(drug →[transporter] →gene/protein →[interacts with] →exposure):
"What exposure may affect <drug>s efficacy by acting on its transporter genes?",
17


</details>

### STaRK · 块 57 · 页 18-18 · skipped

`chunk_4697197dc0d7c2d40e2183b0bb64a38c`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

(pathway →[interacts with] →gene/protein →[ppi] →gene/protein):
"What gene/protein interacts with the gene/protein that related to <pathway>?",
(drug →[synergistic interaction] →drug →[transporter] →gene/protein):
"What gene or protein transports the drugs that have a synergistic interaction with <drug>?",
(biological_process →[interacts with] →gene/protein →[interacts with] →biological_process):
"What biological process has the common interactino pattern with gene or proteins as
<biological_process>?",
(effect/phenotype →[associated with] →gene/protein →[interacts with] →biological_process):
"What biological process interacts with the gene/protein associated with <effect/phenotype>?",
(drug →[transporter] →gene/protein →[expression present] →anatomy):
"What anatomy expressesed by the gene/protein that affect the transporter of <drug>?",
(drug →[target] →gene/protein →[interacts with] →cellular_component):
"What cellular component interacts with genes or proteins targeted by <drug>?",
(biological_process →[interacts with] →gene/protein →[expression absent] →anatomy):
"What anatomy does not express the genes or proteins that interacts with <biological_process>?",
(effect/phenotype →[associated with] →gene/protein →[expression absent] →anatomy):
"What anatomy does not express the genes or proteins associated with <effect/phenotype>?",
(drug →[indication] →disease →[indication] →drug)
& (drug →[synergistic interaction] →drug):


</details>

### STaRK · 块 58 · 页 18-18 · skipped

`chunk_0d9aa18517b7f13cf82f4944d674daab`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

"Find drugs that has a synergistic interaction with <drug> and both are indicated
for the same disease.",
(pathway →[interacts with] →gene/protein →[interacts with] →pathway)
& (pathway →[parent-child] →pathway):
"Find pathway that is related with <pathway> and both can [interacts with] the same gene/protein.",
(gene/protein →[associated with] →disease →[associated with] →gene/protein)
& (gene/protein →[ppi] →gene/protein):
"Find gene/protein that can interect with <gene/protein> and both are associated
with the same disease.",
(gene/protein →[associated with] →effect/phenotype →[associated with] →gene/protein)
& (gene/protein →[ppi] →gene/protein):
"Find gene/protein that can interect with <gene/protein> and both are associated
with the same effect/phenotype."
}
where [·] denotes the relation type.
B
Mathematical Definitions of Shannon Entropy and Type-Token Ratio
Shannon Entropy. Shannon Entropy is a measure of the uncertainty in a set of possible outcomes,
quantifying the amount of information or disorder within a dataset. It is defined as follows:
H(X) = −
n
X
i=1
p(xi) log p(xi)
where X is the set of possible outcomes, p(xi) is the probability of occurrence of the outcome xi,
and n is the total number of unique outcomes. Higher entropy values indicate greater diversity in the
distribution of outcomes.[42]


</details>

### STaRK · 块 59 · 页 18-19 · skipped

`chunk_431ea83d709d633f100fd9a28a4fdca7`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Type-Token Ratio (TTR). The Type-Token Ratio is a measure of lexical diversity, calculated as
the ratio of the number of unique words (types) to the total number of words (tokens) in a text. It is
defined as follows:
TTR = V
N
where V is the number of unique words and N is the total number of words in the text. Higher TTR
values indicate a higher proportion of unique words, reflecting greater lexical diversity. [48]
C
Instructions for Generating Queries
For the process of generating queries by human, the participants were given a list of entity IDs that
we randomly sampled from the entire entity set. Then, they were asked to follow the following
instructions with the support of our built interactive platform at https://stark.stanford.
edu/skb_explorer.html.
18

Task:
1) Given the provided entity ID, review the associated document and any connected entities
and multi-hop paths.
2) Find interesting aspects of the entities by examining both their relational structures and the
textual information available.
3) Write your queries from these aspects such that the entity can satisfy all of them.
Note:
1) Please do not leak the name of the entity in the query.
2) You can skip some entity IDs if you think the knowledge involved is hard to understand.
3) Feel free to be creative with content of your queries, you can also include additional context.
There is NO restriction on how you express the queries.
After collecting the queries, we filtering the ground truth answers manually by human validation.
D


</details>

### STaRK · 块 60 · 页 19-19 · skipped

`chunk_f6e271d15a4e1ba400fdd2a4606f7e18`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

Experiments
D.1
More Experimental Results
Table 10: Positive/Non-negative rates (%) from human evaluation.
Naturalness
Diversity
Practicality
STARK-AMAZON
73.6 / 89.5
68.4 / 89.5
89.5 / 94.7
STARK-MAG
94.7 / 100
73.7 / 84.2
68.4 / 84.2
STARK-PRIME
67.8 / 92.8
71.4 / 82.1
71.4 / 89.3
Average
78.7 / 94.1
71.0 / 85.3
76.4 / 89.4
E
Prompts and LLM versions for Query Synthesization
We summarize the LLM versions in Table 11. We chose these models based on a joint consideration
of their cost, how accurate they are, and whether they were the latest model during different phases of
the project. While we used different LLMs, we checked each step separately to make sure the good
quality in our benchmark datasets.
Table 11: Summary of LLM Versions for Query Synthesization
Step
STARK-AMAZON
STARK-MAG
STARK-PRIME
Step 2: Extracting textual requirements
gpt-3.5-turbo-16k
claude-2.0
claude-2.0
Step 3: Combining relational and textual requirements
claude-2.0, gpt-4-0125-preview
Step 4: Filtering additional answers
claude-2.1, claude-2.0, claude-instant-1.2
E.1
Extracting textual requirements
Prompt for STARK-AMAZON: Textual requirement extraction
You are an intelligent assistant that extracts diverse positive
,→requirements and negative perspectives for an Amazon product.
,→I will give you the following information:
- product: <product name>
19


</details>

### STaRK · 块 61 · 页 20-20 · skipped

`chunk_a3b2306a532e47e3e944783caa87314d`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

- dimensions: <product dimensions>
- weight: <product weight>
- description: <product description>
- features: #1: <feature #1> ...
- reviews:
#1:
summary: <review summary>
text: <full review text>
#2: ...
- Q&A:
#1:
question: <product-related question>
answer: <answer to product-related question>
#2: ...
Based on the given product information, you need to (1) identify the


</details>

### STaRK · 块 62 · 页 20-20 · skipped

`chunk_b9be6b92838d9af8c6edf0e6ff557476`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

,→product’s generic category, (2) list all of the negative
,→perspectives and their sources, and (2) extract up to five
,→hard and five soft requirements relevant to customers’
,→interests along with their sources. (1) For example, the
,→product’s generic category can be "a chess book" or "a phone
,→case for iphone 6", do not use the product name directly. (2)
,→Negative perspectives are those that the product doesn’t
,→fulfill, which come from the negative reviews or Q&A. (3) For
,→the requirements, you should only focus on the product’s
,→advantages and positive perspects. Hard requirements mean that
,→
product must fulfil, such as size and functionality. Soft
,→requirements are not as strictly defined but still desirable,
,→such as a product is easy-to-use. For (2) and (3), each source
,→
is a composite of the key and index (if applicable) separated
,→
by "-", such as "description", "Q&A-#1". You should provide
,→the response in a specific format as follows where "item"
,→refers to the product’s generic category, e.g., "a chess book".
,→
Response format:
{
"item": <the product’s generic category> ,
"negative": [[<source of negative perspective>, <negative
,→perspective description>]],
"hard": [[<source of hard requirement>, <hard requirement
,→description>], ...],
"soft": [[<source of soft requirement>, <soft requirement
,→description>], ...]
}
Here is an example of the response:
{


</details>

### STaRK · 块 63 · 页 20-21 · skipped

`chunk_f559efc327128d44dd34cf0147c3caeb`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

"item": "a camping chair",
"negative": [["reviews-#3", "the chair is not sturdy enough"], ["Q&
,→A-#1", "wrong color"]],
"hard": [["description", "has a breathable mesh back"], ["
,→description", "the arm is adjustable"], ["dimensions", "more
,→than 35 inches long"], ["features-#7", "with a arm rest cup
,→holder"], ["Q&A-#4", "need to come with a carrying bag"]],
"soft": [["description", "suitable for outdoors"], ["features-#9",
,→"compact and save space"], ["reviews-#6", "light and portable
,→"]]
}
This is the information of the product that you need to write
,→response for:
<product_doc>
Response:
20

Prompt for STARK-MAG: Textual requirement extraction
You are a helpful assistant that helps me extract one short
,→requirement (no more than 10 words) about a paper from the
,→paper information that researchers might be interested in. The
,→
requirement can be about the paper content, publication date,
,→
publication venue, etc. The requirement should be general and
,→
not too specific. I will give you the paper information, and
,→you should return a short phrase about the paper, starting
,→with ’the paper...’. This is the paper information:
<doc_info>
Please only return the short and general requirement without
,→additional comments.
Prompt for STARK-PRIME: Textual requirement extraction
You are a helpful assistant that helps me extract <n_properties> from


</details>

### STaRK · 块 64 · 页 21-21 · skipped

`chunk_ae90ae3a0291f9155a23e55d0e3655de`；类型 body；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

,→
a given <target> information that a <role> may be interested
,→in.
<role_instruction>
Each property should be no more than 10 words and start with "the <
,→target>". You should also include the source of each property
,→as indicated in the paragraph names of the information, e.g.,
,→"details.mayo_symptoms", "details.summary", etc. You should
,→return a list of properties and their sources following the
,→format:
[["<short_property1>", "<source1>"], ["<short_property2>", "<source2
,→>"], ...]
This is the information:
<doc_info>
Please provide only the list with <n_properties> in your response.
,→Response:
According to the role assigned to simulate the query content, the <role_instruction> as shown
below is filled in accordingly.
role
role instruction
Doctor
Doctors typically ask questions aimed at diagnosing and treating. Their
questions tend to be direct and practical, focusing on aspects involving side
effects, symptoms, and complications etc.
Medical scientist
Medical scientists often ask questions that reflect the complexity and depth of
the scientific inquiry in the medical field. Their questions tend to be detailed
and specific, focusing on aspects such as: etiology and pathophysiology,
genetic factors, association with pathway, protein, or molecular function.
Patient
Patients typically don’t know the professional medical terminology. Their
questions tend to be straightforward, focusing on practical concerns on the
symptons, effects, and inheritance etc., instead of the detailed mechanisms,
which may also include more context.


</details>

### STaRK · 块 65 · 页 21-22 · skipped

`chunk_1a5dbe0b56a19fc637e75b21017d082e`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

E.2
Combining relational and textual requirements
21

Prompt for STARK-AMAZON: Fuse relational and textual requirements
You are an intelligent assistant that generates queries about an
,→Amazon item. I will provide you with the item name,
,→requirements, and its negative customer reviews. Your task is
,→to create a natural-sounding customer query that leads to the
,→item as the answer, using the requirements that are non-
,→conflicting with the negative reviews, and provide the indices
,→
of the requirements used. For example:
Information:
- item: a soccer rebounder
- requirements:
#1: needs a heavy-duty 1-inch to 3-inch steel tube frame
#2: should be adjustable for practicing different skills
#3: should be durable
#4: usually be viewed together with <SKLZ Star-Kick Hands Free Solo
,→Soccer Trainer>
- negative reviews:
#1: it was broken after a few uses
Response:
{
"index": [1, 2, 4],
"query": "Please recommend a soccer rebounder with a steel frame,
,→about 2 inches thick, that can adapt to different skill
,→levels. We had a blast using the <SKLZ Star-Kick Hands Free
,→Solo Soccer Trainer> with my family, and I’m on the lookout
,→for something similar."
}
As the negative review indicates that the soccer rebouncer lacks


</details>

### STaRK · 块 66 · 页 22-23 · skipped

`chunk_f0e73391d4cf439a4baf379972fb4b45`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

,→durability, your query should only incorporate requirements #1,
,→
#2, and #4 while excluding #3. A requirement should only be
,→excluded if it conflicts with negative feedback or is unlikely
,→
to align with customers’ interests. For relational
,→requirements about another <product>, do not directly use "
,→usually bought/viewed together with <product>" in the query.
,→You must deduce the item’s relationship with <product> into
,→substitute or complement, and create various user scenarios,
,→such as the item should be compatible or used with <product> (
,→for complements) or match in style with <product> (for
,→substitute), to make the queries sound natural. Except for <
,→product>, you should change the description but convey similar
,→
meanings. The query structure is completely flexible. Here is
,→
the information to generate the requirement indices and a
,→natural-sounding query:
Information:
<product_req_and_neg_comments>
Response:
Prompt for STARK-MAG: Fuse relational and textual requirements
You are a helpful assistant that helps me generate a new query by
,→incorporating an additional requirement into a given query,
,→and form a coherent and natural-sounding question.
This is the existing query:
22

<query>
This is the additional requirement:
<additional_textual_requirement>
You should be creative in combining the existing query and
,→requirement, and flexible in structuring the new query, adding
,→
context as needed. Please return the new query without
,→additional comments:
The prompt of a second-time rewrite by GPT-4 Turbo:


</details>

### STaRK · 块 67 · 页 23-23 · skipped

`chunk_4c23ff22bf7b4955aa4d6d9030a83056`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

You are a helpful assistant that helps make a researcher’s query
,→about a paper more natural-sounding, akin to the language used
,→
in ArXiv web searches. You should change the description but
,→convey similar meanings. The query structure is completely
,→flexible. The original query:
"<query>"
Please only output the new query without additional comments:
Prompt for STARK-PRIME: Fuse relational and textual requirements
You are a helpful assistant that helps me generate a natural-sounding
,→
and coherent query as if you were a <role>. The query should
,→be created based on a list of requirements for searching <
,→plural_target> in a database. I will provide you with the
,→requirements in the following format:
[<requirement1>, <requirement2>, ...]
You should create the query based solely on the given requirements.
,→Moreover, you should craft the query from the perspective of a
,→
<role>.
<role_instruction>
For example, a query from a <role> could be
"<example_query>"
You can be flexible in structuring the query and adding additional
,→context. Ensure that the query uses different descriptions
,→than the original property descriptions while retaining
,→similar meanings. The query should sound concise and natural.
,→These are the requirements:
<requirements>
Please create the query based on the given requirements and provide
,→only the query without additional comments. Your response:
The prompt of a second-time rewrite by GPT-4 Turbo:
You are a helpful assistant that helps me rewrite a query that


</details>

### STaRK · 块 68 · 页 23-24 · skipped

`chunk_1c18caac93113a8b1f31c429dcfdb250`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

,→searches for <plural_target> from the perspective of a <role>.
,→
You should maintain the requirements from the original query
,→and the characteristics of the <role>, while being creative
,→and flexible in structuring the query. Ensure the revised
,→query is concise and natural-sounding. Original query: "<query
,→>". Please output only the rewritten query:
E.3
Filtering additional answers
Prompt for STARK-AMAZON: Filtering additional answers
Filter products by general category
23

You are an intelligent assistant that identifies whether an Amazon
,→product belongs to a given category. I will give you the
,→product information. You should only answer yes / no in the
,→response. For examples, the product <SKLZ Star-Kick Hands Free
,→
Solo Soccer Trainer> belongs to the category "soccer trainer"
,→
and the product <Test your Opening, Middlegame and Endgame
,→Play - VOLUME 2> belongs to the category "a chess opening book
,→", while <Baby Girls One-piece Shiny Athletic Leotard Ballet
,→Tutu with Bow> doesn’t belong to category "an adult tutu".
Information:
- product title: <<product_title>>
- product description: <product_description>
Does the product belong to "<target_category>"? Response (yes/no):
Filter products by requirements
You are a helpful assistant that helps me check whether an Amazon


</details>

### STaRK · 块 69 · 页 24-24 · skipped

`chunk_df1f0e1d42eec75ed4c6ad96b8c7d4a5`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

,→product satisfies the given requirements. I will provide you
,→with the product information, which may include the product
,→description, features, reviews, and Q&A from customers. Your
,→task is to assess whether the product meets each requirement
,→based on the provided information. If there is no information
,→that supports the requirement, your response for that
,→requirement is "NA". If there is relevant information that
,→supports the requirement, your response for that requirement
,→is the information source that fulfills the requirement. Each
,→information source is a composite of the key and index (if
,→applicable), separated by "-", such as "description", "
,→features-#3", "Q&A-#1", "reviews-#2". If there are multiple
,→sources,
Response:
{
1: "NA" or [the information sources that satisfy the requirement
,→#1],
2: "NA" or [the information sources that satisfy the requirement
,→#2],
...
}
Here is the product information:
<product_doc>
The requirements are as follows:
<customer_requirements>
Response:
Prompt for STARK-MAG: Filtering additional answers
You are a helpful assistant that helps me verify whether a given <
,→target_node_type> is subject to a requirement. I will provide
,→you with the <target_node_type> information and the
,→requirement, and you should return only a ’True’ or ’False’
,→value, indicating whether the <target_node_type> meets the
,→requirement.
This is the <target_node_type> information:
<doc_info>
24


</details>

### STaRK · 块 70 · 页 25-25 · skipped

`chunk_f86d846031fcfe4e1644057fb158663b`；类型 example；跳过原因 benchmark_paper_not_applicable；0.00s；Token 0/0


<details><summary>完整来源块</summary>

This is the requirement:
<additional_textual_requirement>
Please return only the boolean value without additional comments:
Prompt for STARK-PRIME: Filtering additional answers
You are a helpful assistant tasked with verifying whether a given <
,→target> satisfies each of the provided requirements. I will
,→give you the requirements in the following format:
{1: <requirement1>, 2: <requirement2>, ...}
When evidence in the <target> information confirms a requirement is
,→met, cite the source, for example, ’details.mayo_symptoms’, ’
,→details.summary’. If no direct evidence exists, indicate this
,→with ’NA’. The output in JSON format should be as follows:
{1: ’NA’ or <source1>, 2: ’NA’ or <source2>, ...}
This is the <target> information:
<doc_info>
These are the requirements:
<requirements>
Please provide only the JSON in your response. Response:
25


</details>
