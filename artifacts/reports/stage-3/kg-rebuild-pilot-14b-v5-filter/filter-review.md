# kg-rebuild-pilot-14b-v5-filter

离线重验 v4 已接受的 79 条 Claim；没有重新调用模型。旧 v4 与生产图谱均未修改。

- 输入：`artifacts\reports\stage-3\kg-rebuild-pilot-14b-v4\runs\1313ba7eb0f54d8d84715767bae93d9d\checkpoint.json`
- 候选：79 条；v4 预先拒绝 31 条（保持原记录）
- 新规则接受：9 条；拒绝：70 条
- 模型调用：0

## 按论文汇总

| 论文 | 输入候选 | 新规则接受 | 新规则拒绝 |
|---|---:|---:|---:|
| G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering | 32 | 8 | 24 |
| StructGPT: A General Framework for Large Language Model to Reason over Structured Data | 19 | 1 | 18 |
| STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases | 28 | 0 | 28 |

## 拒绝原因

- `benchmark_paper_not_applicable`：28
- `subject_not_method_anchored`：12
- `implementation_object_not_named_technology`：6
- `table_or_template_example`：4
- `generic_entity`：4
- `entity_marker_or_delta`：3
- `component_not_explicitly_listed`：3
- `ablation_does_not_establish_component`：3
- `chunk_kind_excluded:example`：3
- `control_object_not_parameter`：2
- `prior_work_context`：2

## 逐条结果

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 2 · `body`

- **拒绝：`control_object_not_parameter`** `G-Retriever --CONTROLLED_BY--> soft prompting`；引文：which can be fine-tuned to enhance graph understanding via soft prompting
- **拒绝：`table_or_template_example`** `G-Retriever --HAS_COMPONENT--> Prize-Collecting Steiner Tree optimization problem`；引文：To resist hallucination and to allow for textual graphs that greatly exceed the LLM’s context window size, G-Retriever performs RAG over a graph by formulating this task as a Prize-Collecting Steiner Tree optimization problem.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 8 · `body`

- **拒绝：`implementation_object_not_named_technology`** `RAG component --IMPLEMENTS--> selective retrieval of relevant graph parts`；引文：G-Retriever overcomes these issues with its RAG component, which allows for effective scaling to larger graphs by selectively retrieving only relevant parts of the graph.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 12 · `body`

- **拒绝：`subject_not_method_anchored`** `LMs for text encoding --HAS_COMPONENT--> encoding function`；引文：an LM encodes these attributes as: zn = LM(xn) ∈Rd, (1)
- **拒绝：`subject_not_method_anchored`** `LLM with prompt tuning --CONTROLLED_BY--> weights θ`；引文：The LLM, parameterized by weights θ, takes a sequence of tokens X, and a prompt P as input, and generates a sequence of tokens Y = {y1, y2, . . . , yr} as output.
- **拒绝：`implementation_object_not_named_technology`** `encoding function --IMPLEMENTS--> text attribute encoding`；引文：an LM encodes these attributes as: zn = LM(xn) ∈Rd, (1)

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 18 · `body_mixed`

- **保留** `G-Retriever --HAS_COMPONENT--> Indexing`；页 6；引文：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- **保留** `G-Retriever --HAS_COMPONENT--> Retrieval`；页 6；引文：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- **保留** `G-Retriever --HAS_COMPONENT--> Subgraph Construction`；页 6；引文：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.
- **保留** `G-Retriever --HAS_COMPONENT--> Generation`；页 6；引文：G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 19 · `body`

- **拒绝：`subject_not_method_anchored`** `RAG approach --HAS_COMPONENT--> node and graph embeddings generation`；引文：We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.
- **拒绝：`subject_not_method_anchored`** `RAG approach --HAS_COMPONENT--> nearest neighbor data structure`；引文：These embeddings are then stored in a nearest neighbor data structure.
- **拒绝：`subject_not_method_anchored`** `retrieval --HAS_COMPONENT--> k-nearest neighbors retrieval approach`；引文：Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors retrieval approach.
- **拒绝：`implementation_object_not_named_technology`** `k-nearest neighbors retrieval approach --IMPLEMENTS--> argtopkn∈V cos(zq, zn) and argtopke∈E cos(zq, ze)`；引文：The retrieval operation is defined as: Vk = argtopkn∈V cos(zq, zn) Ek = argtopke∈E cos(zq, ze),
- **拒绝：`subject_not_method_anchored`** `retrieval --CONTROLLED_BY--> k (number of nearest neighbors)`；引文：Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors retrieval approach.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 20 · `body`

- **拒绝：`subject_not_method_anchored`** `Prize-Collecting Steiner Tree (PCST) --HAS_COMPONENT--> Edge prize assignment`；引文：Edge prizes are assigned similarly.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 21 · `body`

- **保留** `graph encoder --IMPLEMENTS--> Graph Attention Network (GAT)`；页 7；引文：We use a graph encoder to model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].
- **拒绝：`subject_not_method_anchored`** `PCST algorithm adaptation --HAS_COMPONENT--> virtual node`；引文：Our solution involves replacing edge e with a ‘virtual node’ ve, connected to both endpoints of e.
- **拒绝：`subject_not_method_anchored`** `PCST algorithm adaptation --CONTROLLED_BY--> Ce`；引文：The original PCST algorithm is designed for node prizes only. However, given the significance of edge semantics in certain scenarios, we adapt the algorithm to accommodate edge prizes as follows: Consider an edge e with a cost Ce and a prize Pe.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 22 · `body`

- **拒绝：`implementation_object_not_named_technology`** `MLPϕ2 --IMPLEMENTS--> dimension reduction or transformation of graph embedding`；引文：ˆhg = MLPϕ2(hg) ∈Rdl, (10) where dl is the dimension of the LLM’s hidden embedding.
- **拒绝：`subject_not_method_anchored`** `LLM Generation with Graph Prompt Tuning --CONTROLLED_BY--> θ`；引文：The final stage involves generating the answer Y given the graph token ˆhg, acting as a soft prompt, and the text embedder output ht. These inputs are fed through the self-attention layers of a pretrained frozen LLM, with parameter θ.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 23 · `body`

- **保留** `SentenceBert --IMPLEMENTS--> LM`；页 8；引文：In the indexing step, we use SentenceBert [34] as the LM to encode all node and edge attributes.
- **保留** `Llama2-7b --IMPLEMENTS--> LLM`；页 8；引文：In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.
- **保留** `Graph Transformer --IMPLEMENTS--> graph encoder`；页 8；引文：In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 24 · `body`

- **拒绝：`entity_marker_or_delta`** `G-Retriever --HAS_COMPONENT--> ∆Prompt tuning`；引文：Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.
- **拒绝：`component_not_explicitly_listed`** `G-Retriever --HAS_COMPONENT--> LoRA`；引文：Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.
- **拒绝：`component_not_explicitly_listed`** `G-Retriever w/ LoRA --HAS_COMPONENT--> LoRA`；引文：Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.
- **拒绝：`entity_marker_or_delta`** `G-Retriever w/ LoRA --HAS_COMPONENT--> ∆LoRA`；引文：Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering · 块 25 · `body`

- **拒绝：`table_or_template_example`** `G-Retriever --HAS_COMPONENT--> Graph Encoder`；引文：∆G-Retriever w/o Graph Encoder 54.62 ± 0.78 ↓22.51%
- **拒绝：`ablation_does_not_establish_component`** `G-Retriever --HAS_COMPONENT--> Projection Layer`；引文：w/o Projection Layer 69.70 ± 0.68 ↓1.11%
- **拒绝：`ablation_does_not_establish_component`** `G-Retriever --HAS_COMPONENT--> Textualized Graph`；引文：w/o Textualized Graph 56.96 ± 1.83 ↓19.19%
- **拒绝：`ablation_does_not_establish_component`** `G-Retriever --HAS_COMPONENT--> Retrieval`；引文：w/o Retrieval 63.84 ± 0.41 ↓9.43%

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 39 · `body`

- **拒绝：`prior_work_context`** `two-stage framework --HAS_COMPONENT--> LLMs for evidence collection`；引文：An intuitive idea is to conduct a two-stage frame- work as prior studies on retrieval-augmented ap- proaches (Izacard et al., 2022; Oguz et al., 2022), in which LLMs are employed to first collect suf- ficient evidence relating to the question and then figure out the answer by the LLMs.
- **拒绝：`prior_work_context`** `two-stage framework --HAS_COMPONENT--> LLMs for answering questions`；引文：An intuitive idea is to conduct a two-stage frame- work as prior studies on retrieval-augmented ap- proaches (Izacard et al., 2022; Oguz et al., 2022), in which LLMs are employed to first collect suf- ficient evidence relating to the question and then figure out the answer by the LLMs.
- **拒绝：`implementation_object_not_named_technology`** `interface of structure data --IMPLEMENTS--> accurate, efficient data access and filtering`；引文：The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).
- **拒绝：`generic_entity`** `approach --HAS_COMPONENT--> interface of structure data`；引文：The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).
- **拒绝：`generic_entity`** `approach --HAS_COMPONENT--> LLMs for reasoning`；引文：The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 41 · `example`

- **拒绝：`generic_entity`** `Extract_Tables_Infomration --HAS_COMPONENT--> T`；引文：Extract_Tables_Infomration ({T})
- **拒绝：`generic_entity`** `Extract_Column_Name --HAS_COMPONENT--> T`；引文：Extract_Column_Name (T)
- **拒绝：`chunk_kind_excluded:example`** `Extract_Neighbor_Relations --HAS_COMPONENT--> Jeff Probst`；引文：Extract_Neighbor_Relations(“Jeff Probst”)
- **拒绝：`chunk_kind_excluded:example`** `Extract_Column_Name --HAS_COMPONENT--> Team`；引文：Extract_Column_Name(“Team”)
- **拒绝：`chunk_kind_excluded:example`** `Extract_Table&Column_Name --HAS_COMPONENT--> mus_vis`；引文：Extract_Table&Column_Name(“mus_vis”)

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 43 · `body`

- **拒绝：`table_or_template_example`** `Extract_Table&Column_Name (D) --HAS_COMPONENT--> interface`；引文：we devise two functions as follows: • Extract_Table&Column_Name (D): extracts the names of all the tables and their contained columns from the database.

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 44 · `body`

- **拒绝：`subject_not_method_anchored`** `LLM for Generation --HAS_COMPONENT--> input prompts design`；引文：After linearization, we design two types of input prompts for LLMs to fulfill different purposes1:

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 47 · `body`

- **拒绝：`table_or_template_example`** `Table-based Question Answering (TableQA) --HAS_COMPONENT--> Extract_Column_Name`；引文：first, we invoke Extract_Column_Name (T ) to extract all column names of a table, linearize them, and leverage LLMs to select the relevant ones {c} according to the question.

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 50 · `body`

- **拒绝：`component_not_explicitly_listed`** `IRR --HAS_COMPONENT--> reading-then-reasoning`；引文：our method is a general iterative reading-then-reasoning (IRR) framework that can be used for different LLMs.

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 52 · `body_mixed`

- **保留** `IRR --HAS_COMPONENT--> interfaces for KG`；页 7；引文：In our approach, we devise interfaces for KG to efficiently read the relevant information, and leverage LLMs to extract useful parts and per- form reasoning.
- **拒绝：`control_object_not_parameter`** `IRR --CONTROLLED_BY--> in-context exemplars`；引文：By adding a few in- context exemplars (i.e., 15 for WQSP and 32 for MQA) to LLMs, we can further improve the model performance.
- **拒绝：`implementation_object_not_named_technology`** `interfaces for KG --IMPLEMENTS--> efficiently read the relevant information`；引文：In our approach, we devise interfaces for KG to efficiently read the relevant information, and leverage LLMs to extract useful parts and per- form reasoning.

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 53 · `body`

- **拒绝：`entity_marker_or_delta`** `+ IRR (ours) --CONTROLLED_BY--> 32 in-context exemplars`；引文：when adding 32 in-context exemplars to the LLMs, they can obtain further performance improvements.

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data · 块 54 · `body`

- **拒绝：`subject_not_method_anchored`** `our proposed method --HAS_COMPONENT--> Extract_Neighbor_Relations function`；引文：In each iteration, we first invoke the Ex- tract_Neighbor_Relations function to extract the neighboring relations (e.g., birthplace, residence, and education) of the topic entity “Harper Lee”

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 76 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `Instantiate Semi-structured Knowledge Base --HAS_COMPONENT--> Relation template`；引文：Instantiate Semi-structured Knowledge Base Relation template Check satisfaction e.g., “Belongs to Radio Flyer”
- **拒绝：`benchmark_paper_not_applicable`** `Relation template --IMPLEMENTS--> Check satisfaction`；引文：Instantiate Semi-structured Knowledge Base Relation template Check satisfaction e.g., “Belongs to Radio Flyer”

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 78 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `Sample Relational Requirements --HAS_COMPONENT--> relation template construction`；引文：For each query, we sample a practical relation template constructed with expert/domain knowledge, e.g., “(a product) belongs to <brand>” and ground it with sampled entities (i.e., a specific brand), e.g., “belongs to Radio Flyer”. This relational requirement yields a set of candidate entities, i.e., products belonging to Radio Flyer.
- **拒绝：`benchmark_paper_not_applicable`** `Extracting Textual Properties --HAS_COMPONENT--> property extraction from textual document`；引文：We randomly sample a candidate entity from the first step, referred to as the gold answer, from which LLMs extract properties that align with the interests of specific roles (e.g., customers, researchers, or doctors) in its textual document. In Figure 3, we extract multiple properties about the functionality and user experience from a Radio Flyer product.
- **拒绝：`benchmark_paper_not_applicable`** `Combining Textual and Relational Information --HAS_COMPONENT--> query synthesis from properties and requirements`；引文：We use two LLMs to synthesize queries from textual properties and relational requirements, enhancing diversity and reducing bias arise from relying on a single LLM. The first LLM focuses on generating natural, role-specific, and style-consistent (e.g., ArXiv searches) queries.
- **拒绝：`benchmark_paper_not_applicable`** `Combining Textual and Relational Information --HAS_COMPONENT--> context enrichment and rephrasing`；引文：The second LLM enriches the context and rephrases queries, which poses the need for advanced reasoning to comprehend them under complex contexts.

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 84 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `Small Dense Retrievers --HAS_COMPONENT--> dense embeddings`；引文：These compact models generate dense embeddings for both queries and documents, computing retrieval scores based on embedding similarities.
- **拒绝：`benchmark_paper_not_applicable`** `LLM-based Dense Retrievers --HAS_COMPONENT--> dense embeddings`；引文：These models leverage LLMs to generate dense embeddings that are more contextually expressive.
- **拒绝：`benchmark_paper_not_applicable`** `Multivector Retrievers --HAS_COMPONENT--> overlapping chunks`；引文：multi-ada-002 splits each document into overlapping chunks and embeds them using the same encoder as the query.
- **拒绝：`benchmark_paper_not_applicable`** `Multivector Retrievers --HAS_COMPONENT--> token-level embeddings`；引文：ColBERTv2 represents each document as multiple token-level embeddings for fine-grained matching, capturing richer semantic information.

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 85 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `LLM Rerankers --HAS_COMPONENT--> Claude3 and GPT-4 rerankers`；引文：LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of top-k ada-002 results by reranking them using large language models.
- **拒绝：`benchmark_paper_not_applicable`** `LLM Rerankers --CONTROLLED_BY--> k = 20 for synthesized queries and k = 10 for human-generated queries`；引文：We employ GPT-4-turbo (gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized queries and k = 10 for human-generated queries.
- **拒绝：`benchmark_paper_not_applicable`** `Claude3 and GPT-4 rerankers --IMPLEMENTS--> reranking using large language models`；引文：These models improve the precision of top-k ada-002 results by reranking them using large language models.

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 104 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `metapath (field_of_study →paper) --IMPLEMENTS--> requires an initial field_of_study entity to be filled in the corresponding query template`；引文：For example, the metapath (field_of_study →paper) requires an initial field_of_study entity to be filled in the corresponding query template.
- **拒绝：`benchmark_paper_not_applicable`** `multi-hop metapaths --IMPLEMENTS--> requires an institution entity and a field_of_study entity to initialize the query`；引文：For multi-hop metapaths, the last metapath (institution →author →paper ←field_of_study) requires an institution entity and a field_of_study entity to initialize the query.

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 105 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `synthesized queries --HAS_COMPONENT--> multi-hop templates`；引文：For synthesized queries, we listed 28 multi-hop templates designed by experts to cover various relation types and ensure their practical relevance.
- **拒绝：`benchmark_paper_not_applicable`** `query 'What is the drug that targets the genes or proteins expressed in <anatomy>?' --HAS_COMPONENT--> multi-hop templates`；引文：For instance, the query “What is the drug that targets the genes or proteins expressed in <anatomy>?” serves applications in precision medicine and pharmacogenomics, aiding researchers and healthcare professionals in identifying drugs that act on genes or proteins associated with specific anatomical areas and enabling more targeted treatments.

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 106 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `(drug →[carrier] →gene/protein →[carrier] →drug) --HAS_COMPONENT--> [carrier]`；引文：(drug →[carrier] →gene/protein →[carrier] →drug): "What is the drug that has common gene/protein carrier with <drug>?"
- **拒绝：`benchmark_paper_not_applicable`** `(anatomy →[expression present] →gene/protein →enzyme →drug) --HAS_COMPONENT--> [expression present]`；引文：(anatomy →[expression present] →gene/protein →enzyme →drug): "What is the drug that some genes or proteins act as an enzyme upon, where the genes or proteins are expressed in <anatomy>?"
- **拒绝：`benchmark_paper_not_applicable`** `(cellular_component →[interacts with] →gene/protein →[carrier] →drug) --HAS_COMPONENT--> [interacts with]`；引文：(cellular_component →[interacts with] →gene/protein →[carrier] →drug): "What is the drug carried by genes or proteins that interact with <cellular_component>?"
- **拒绝：`benchmark_paper_not_applicable`** `(molecular_function →[interacts with] →gene/protein →[target] →drug) --HAS_COMPONENT--> [interacts with]`；引文：(molecular_function →[interacts with] →gene/protein →[target] →drug): "What drug targets the genes or proteins that interact with <molecular_function>?"
- **拒绝：`benchmark_paper_not_applicable`** `(effect/phenotype →[side effect] →drug →[synergistic interaction] →drug) --HAS_COMPONENT--> [synergistic interaction]`；引文：(effect/phenotype →[side effect] →drug →[synergistic interaction] →drug): "What drug has a synergistic interaction with the drug that has <effect/phenotype> as a side effect?"
- **拒绝：`benchmark_paper_not_applicable`** `(disease →[indication] →drug →[contraindication] →disease) --HAS_COMPONENT--> [contraindication]`；引文：(disease →[indication] →drug →[contraindication] →disease): "What disease is a contraindication for the drugs indicated for <disease>?"
- **拒绝：`benchmark_paper_not_applicable`** `(gene/protein →[transporter] →drug →[side effect] →effect/phenotype) --HAS_COMPONENT--> [transporter]`；引文：(gene/protein →[transporter] →drug →[side effect] →effect/phenotype): "What effect or phenotype is a [side effect] of the drug transported by <gene/protein>?"
- **拒绝：`benchmark_paper_not_applicable`** `(drug →[transporter] →gene/protein →[interacts with] →exposure) --HAS_COMPONENT--> [interacts with]`；引文：(drug →[transporter] →gene/protein →[interacts with] →exposure): "What exposure may affect <drug>s efficacy by acting on its transporter genes?"

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases · 块 108 · `body`

- **拒绝：`benchmark_paper_not_applicable`** `Find drugs that has a synergistic interaction with <drug> --HAS_COMPONENT--> (pathway →[interacts with] →gene/protein →[interacts with] →pathway) & (pathway →[parent-child] →pathway)`；引文：(pathway →[interacts with] →gene/protein →[interacts with] →pathway) & (pathway →[parent-child] →pathway): "Find pathway that is related with <pathway> and both can [interacts with] the same gene/protein."
- **拒绝：`benchmark_paper_not_applicable`** `Find gene/protein that can interect with <gene/protein> --HAS_COMPONENT--> (gene/protein →[associated with] →disease →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein)`；引文：(gene/protein →[associated with] →disease →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein): "Find gene/protein that can interect with <gene/protein> and both are associated with the same disease."
- **拒绝：`benchmark_paper_not_applicable`** `Find gene/protein that can interect with <gene/protein> --HAS_COMPONENT--> (gene/protein →[associated with] →effect/phenotype →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein)`；引文：(gene/protein →[associated with] →effect/phenotype →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein): "Find gene/protein that can interect with <gene/protein> and both are associated with the same effect/phenotype."


## 解释边界

这些是确定性规则对归档输出的重验结果，不是第二轮人工准确率。引用存在只说明可溯源，不代表语义真实；进入下一阶段前仍需人工复核保留项。STaRK 被标为基准论文，不以方法组件图谱作为抽取目标。
