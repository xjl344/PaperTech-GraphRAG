# kg-rebuild-pilot-14b-v4 extraction pilot review

> Independent, non-production JSON graph. Every Claim remains pending manual semantic review.
> A located quote and schema-valid relation do not by themselves establish semantic correctness.

## Run summary

- Run ID: `1313ba7eb0f54d8d84715767bae93d9d`
- Model: `qwen2.5:14b` (7cdf5a0187d5c58cc5d369b255592f7841d1c4696d45a8c8a9489440385b22f6)
- Status: `completed`; 120/120 chunks completed; 0 failed
- Claims: 79 accepted from 28 chunks; 31 candidates rejected
- Relation counts: `{"CONTROLLED_BY": 8, "HAS_COMPONENT": 57, "IMPLEMENTS": 14}`
- Quote offsets map back to source page spans: 79/79
- Duplicate subject–predicate–object triples across chunks: 1
- Tokens: 86,918 input / 13,384 output
- Model time: 2823.1s; wall time: 2026-11-25T10:26:02.285523+00:00 to 2026-11-25T11:09:29.303433+00:00

## Per-paper coverage

| Paper | Eligible chunks | Chunks with claims | Claim coverage | Accepted claims | Rejected candidates | Seconds | Input / output tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering | 28 | 11 | 39.3% | 32 | 4 | 836.7 | 20,455 / 3,978 |
| StructGPT: A General Framework for Large Language Model to Reason over Structured Data | 33 | 9 | 27.3% | 19 | 16 | 897.1 | 24,256 / 4,216 |
| STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases | 59 | 8 | 13.6% | 28 | 11 | 1089.3 | 42,207 / 5,190 |

## Rejection reasons

- `evidence_quote_not_in_chunk`: 28
- `relation_signature_not_allowed`: 3

## Claims and original quotes

### G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering

1. **G-Retriever — CONTROLLED_BY → soft prompting**; p.1–1; `pending`
   - Source span: p.1 chars 1505–1578; chunk `chunk_3a7f7a1f47b2586d9d9877afb9110567`
   - Quote: “which can be fine-tuned to enhance graph understanding via soft prompting”

2. **G-Retriever — HAS_COMPONENT → Prize-Collecting Steiner Tree optimization problem**; p.1–1; `pending`
   - Source span: p.1 chars 1580–1806; chunk `chunk_3a7f7a1f47b2586d9d9877afb9110567`
   - Quote: “To resist hallucination and to allow for textual graphs that greatly exceed the LLM’s context window size, G-Retriever performs RAG over a graph by formulating this task as a Prize-Collecting Steiner Tree optimization problem.”

3. **RAG component — IMPLEMENTS → selective retrieval of relevant graph parts**; p.2–3; `pending`
   - Source span: p.2 chars 5991–6161; chunk `chunk_5c9e14854565607ec53c355da481c451`
   - Quote: “G-Retriever overcomes these issues with its RAG component, which allows for effective scaling to larger graphs by selectively retrieving only relevant parts of the graph.”

4. **LMs for text encoding — HAS_COMPONENT → encoding function**; p.4–4; `pending`
   - Source span: p.4 chars 1360–1415; chunk `chunk_2d2863e6cf527b25ae6c871d76ab83cd`
   - Quote: “an LM encodes these attributes as: zn = LM(xn) ∈Rd, (1)”

5. **LLM with prompt tuning — CONTROLLED_BY → weights θ**; p.4–4; `pending`
   - Source span: p.4 chars 2057–2219; chunk `chunk_2d2863e6cf527b25ae6c871d76ab83cd`
   - Quote: “The LLM, parameterized by weights θ, takes a sequence of tokens X, and a prompt P as input, and generates a sequence of tokens Y = {y1, y2, . . . , yr} as output.”

6. **encoding function — IMPLEMENTS → text attribute encoding**; p.4–4; `pending`
   - Source span: p.4 chars 1360–1415; chunk `chunk_2d2863e6cf527b25ae6c871d76ab83cd`
   - Quote: “an LM encodes these attributes as: zn = LM(xn) ∈Rd, (1)”

7. **G-Retriever — HAS_COMPONENT → Indexing**; p.6–6; `pending`
   - Source span: p.6 chars 2226–2348; chunk `chunk_2da94a87e97c2e0f30e8eec5659e202d`
   - Quote: “G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.”

8. **G-Retriever — HAS_COMPONENT → Retrieval**; p.6–6; `pending`
   - Source span: p.6 chars 2226–2348; chunk `chunk_2da94a87e97c2e0f30e8eec5659e202d`
   - Quote: “G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.”

9. **G-Retriever — HAS_COMPONENT → Subgraph Construction**; p.6–6; `pending`
   - Source span: p.6 chars 2226–2348; chunk `chunk_2da94a87e97c2e0f30e8eec5659e202d`
   - Quote: “G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.”

10. **G-Retriever — HAS_COMPONENT → Generation**; p.6–6; `pending`
   - Source span: p.6 chars 2226–2348; chunk `chunk_2da94a87e97c2e0f30e8eec5659e202d`
   - Quote: “G-Retriever comprises four main steps: indexing, retrieval, subgraph construction and generation, as depicted in Figure 3.”

11. **RAG approach — HAS_COMPONENT → node and graph embeddings generation**; p.6–7; `pending`
   - Source span: p.6 chars 2444–2536; chunk `chunk_8c5476c0307c733adb60d1afe861e4d2`
   - Quote: “We initiate the RAG approach by generating node and graph embeddings using a pre-trained LM.”

12. **RAG approach — HAS_COMPONENT → nearest neighbor data structure**; p.6–7; `pending`
   - Source span: p.6 chars 2537–2607; chunk `chunk_8c5476c0307c733adb60d1afe861e4d2`
   - Quote: “These embeddings are then stored in a nearest neighbor data structure.”

13. **retrieval — HAS_COMPONENT → k-nearest neighbors retrieval approach**; p.6–7; `pending`
   - Source span: p.6 chars 3127–3250; chunk `chunk_8c5476c0307c733adb60d1afe861e4d2`
   - Quote: “Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors retrieval approach.”

14. **k-nearest neighbors retrieval approach — IMPLEMENTS → argtopkn∈V cos(zq, zn) and argtopke∈E cos(zq, ze)**; p.6–7; `pending`
   - Source span: p.6 chars 3367–3462; chunk `chunk_8c5476c0307c733adb60d1afe861e4d2`
   - Quote: “The retrieval operation is defined as: Vk = argtopkn∈V cos(zq, zn) Ek = argtopke∈E cos(zq, ze),”

15. **retrieval — CONTROLLED_BY → k (number of nearest neighbors)**; p.6–7; `pending`
   - Source span: p.6 chars 3127–3250; chunk `chunk_8c5476c0307c733adb60d1afe861e4d2`
   - Quote: “Next, to identify the most relevant nodes and edges for the current query, we use a k-nearest neighbors retrieval approach.”

16. **Prize-Collecting Steiner Tree (PCST) — HAS_COMPONENT → Edge prize assignment**; p.7–7; `pending`
   - Source span: p.7 chars 1737–1772; chunk `chunk_04c0673f276b70d320674636d537dc80`
   - Quote: “Edge prizes are assigned similarly.”

17. **PCST algorithm adaptation — HAS_COMPONENT → virtual node**; p.7–7; `pending`
   - Source span: p.7 chars 2535–2633; chunk `chunk_5832b6bfb3218fc28548dbb991a42540`
   - Quote: “Our solution involves replacing edge e with a ‘virtual node’ ve, connected to both endpoints of e.”

18. **PCST algorithm adaptation — CONTROLLED_BY → Ce**; p.7–7; `pending`
   - Source span: p.7 chars 2141–2386; chunk `chunk_5832b6bfb3218fc28548dbb991a42540`
   - Quote: “The original PCST algorithm is designed for node prizes only. However, given the significance of edge semantics in certain scenarios, we adapt the algorithm to accommodate edge prizes as follows: Consider an edge e with a cost Ce and a prize Pe.”

19. **graph encoder — IMPLEMENTS → Graph Attention Network (GAT)**; p.7–7; `pending`
   - Source span: p.7 chars 3095–3221; chunk `chunk_5832b6bfb3218fc28548dbb991a42540`
   - Quote: “We use a graph encoder to model the structure of this graph, specifically using a standard Graph Attention Network (GAT) [43].”

20. **MLPϕ2 — IMPLEMENTS → dimension reduction or transformation of graph embedding**; p.7–8; `pending`
   - Source span: p.7 chars 3540–3623; chunk `chunk_33c8e2f0ed11ba682036fc475dffc954`
   - Quote: “ˆhg = MLPϕ2(hg) ∈Rdl, (10) where dl is the dimension of the LLM’s hidden embedding.”

21. **LLM Generation with Graph Prompt Tuning — CONTROLLED_BY → θ**; p.7–8; `pending`
   - Source span: p.8 chars 577–811; chunk `chunk_33c8e2f0ed11ba682036fc475dffc954`
   - Quote: “The final stage involves generating the answer Y given the graph token ˆhg, acting as a soft prompt, and the text embedder output ht. These inputs are fed through the self-attention layers of a pretrained frozen LLM, with parameter θ.”

22. **SentenceBert — IMPLEMENTS → LM**; p.8–8; `pending`
   - Source span: p.8 chars 1232–1328; chunk `chunk_255b9d4a6fbbac0cf6621acf84251f72`
   - Quote: “In the indexing step, we use SentenceBert [34] as the LM to encode all node and edge attributes.”

23. **Llama2-7b — IMPLEMENTS → LLM**; p.8–8; `pending`
   - Source span: p.8 chars 1329–1450; chunk `chunk_255b9d4a6fbbac0cf6621acf84251f72`
   - Quote: “In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.”

24. **Graph Transformer — IMPLEMENTS → graph encoder**; p.8–8; `pending`
   - Source span: p.8 chars 1329–1450; chunk `chunk_255b9d4a6fbbac0cf6621acf84251f72`
   - Quote: “In the generation step, we use the open-source Llama2-7b [42] as the LLM and Graph Transformer [37] as the graph encoder.”

25. **G-Retriever — HAS_COMPONENT → ∆Prompt tuning**; p.8–9; `pending`
   - Source span: p.8 chars 3364–3441; chunk `chunk_e2737c14a5cd36e6bd408af049fd0aac`
   - Quote: “Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.”

26. **G-Retriever — HAS_COMPONENT → LoRA**; p.8–9; `pending`
   - Source span: p.8 chars 3364–3441; chunk `chunk_e2737c14a5cd36e6bd408af049fd0aac`
   - Quote: “Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.”

27. **G-Retriever w/ LoRA — HAS_COMPONENT → LoRA**; p.8–9; `pending`
   - Source span: p.8 chars 3364–3441; chunk `chunk_e2737c14a5cd36e6bd408af049fd0aac`
   - Quote: “Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.”

28. **G-Retriever w/ LoRA — HAS_COMPONENT → ∆LoRA**; p.8–9; `pending`
   - Source span: p.8 chars 3364–3441; chunk `chunk_e2737c14a5cd36e6bd408af049fd0aac`
   - Quote: “Furthermore, when tuned with LoRA, G-Retriever achieves the best performance.”

29. **G-Retriever — HAS_COMPONENT → Graph Encoder**; p.9–9; `pending`
   - Source span: p.9 chars 516–567; chunk `chunk_aba70e6f2f67df9b074a9e14ead47b00`
   - Quote: “∆G-Retriever w/o Graph Encoder 54.62 ± 0.78 ↓22.51%”

30. **G-Retriever — HAS_COMPONENT → Projection Layer**; p.9–9; `pending`
   - Source span: p.9 chars 568–608; chunk `chunk_aba70e6f2f67df9b074a9e14ead47b00`
   - Quote: “w/o Projection Layer 69.70 ± 0.68 ↓1.11%”

31. **G-Retriever — HAS_COMPONENT → Textualized Graph**; p.9–9; `pending`
   - Source span: p.9 chars 609–651; chunk `chunk_aba70e6f2f67df9b074a9e14ead47b00`
   - Quote: “w/o Textualized Graph 56.96 ± 1.83 ↓19.19%”

32. **G-Retriever — HAS_COMPONENT → Retrieval**; p.9–9; `pending`
   - Source span: p.9 chars 652–685; chunk `chunk_aba70e6f2f67df9b074a9e14ead47b00`
   - Quote: “w/o Retrieval 63.84 ± 0.41 ↓9.43%”

### StructGPT: A General Framework for Large Language Model to Reason over Structured Data

1. **two-stage framework — HAS_COMPONENT → LLMs for evidence collection**; p.3–3; `pending`
   - Source span: p.3 chars 2627–2913; chunk `chunk_02c26b2202e7a91f83446553752c8fb6`
   - Quote: “An intuitive idea is to conduct a two-stage frame- work as prior studies on retrieval-augmented ap- proaches (Izacard et al., 2022; Oguz et al., 2022), in which LLMs are employed to first collect suf- ficient evidence relating to the question and then figure out the answer by the LLMs.”

2. **two-stage framework — HAS_COMPONENT → LLMs for answering questions**; p.3–3; `pending`
   - Source span: p.3 chars 2627–2913; chunk `chunk_02c26b2202e7a91f83446553752c8fb6`
   - Quote: “An intuitive idea is to conduct a two-stage frame- work as prior studies on retrieval-augmented ap- proaches (Izacard et al., 2022; Oguz et al., 2022), in which LLMs are employed to first collect suf- ficient evidence relating to the question and then figure out the answer by the LLMs.”

3. **interface of structure data — IMPLEMENTS → accurate, efficient data access and filtering**; p.3–3; `pending`
   - Source span: p.3 chars 3585–3954; chunk `chunk_02c26b2202e7a91f83446553752c8fb6`
   - Quote: “The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).”

4. **approach — HAS_COMPONENT → interface of structure data**; p.3–3; `pending`
   - Source span: p.3 chars 3585–3954; chunk `chunk_02c26b2202e7a91f83446553752c8fb6`
   - Quote: “The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).”

5. **approach — HAS_COMPONENT → LLMs for reasoning**; p.3–3; `pending`
   - Source span: p.3 chars 3585–3954; chunk `chunk_02c26b2202e7a91f83446553752c8fb6`
   - Quote: “The basic idea of our approach is to disentangle the two processes of reading and reasoning for LLMs: we utilize the interface of structure data to implement accurate, efficient data access and filtering (obtaining the relevant evi- dence), and further utilize the reasoning ability of LLMs to figure out the final plan or result for the question (fulfilling the task).”

6. **Extract_Tables_Infomration — HAS_COMPONENT → T**; p.4–4; `pending`
   - Source span: p.4 chars 709–741; chunk `chunk_c0d2bbf48afc9940787c84d1f1a259b5`
   - Quote: “Extract_Tables_Infomration ({T})”

7. **Extract_Column_Name — HAS_COMPONENT → T**; p.4–4; `pending`
   - Source span: p.4 chars 1017–1040; chunk `chunk_c0d2bbf48afc9940787c84d1f1a259b5`
   - Quote: “Extract_Column_Name (T)”

8. **Extract_Neighbor_Relations — HAS_COMPONENT → Jeff Probst**; p.4–4; `pending`
   - Source span: p.4 chars 1495–1536; chunk `chunk_c0d2bbf48afc9940787c84d1f1a259b5`
   - Quote: “Extract_Neighbor_Relations(“Jeff Probst”)”

9. **Extract_Column_Name — HAS_COMPONENT → Team**; p.4–4; `pending`
   - Source span: p.4 chars 1537–1564; chunk `chunk_c0d2bbf48afc9940787c84d1f1a259b5`
   - Quote: “Extract_Column_Name(“Team”)”

10. **Extract_Table&Column_Name — HAS_COMPONENT → mus_vis**; p.4–4; `pending`
   - Source span: p.4 chars 1565–1601; chunk `chunk_c0d2bbf48afc9940787c84d1f1a259b5`
   - Quote: “Extract_Table&Column_Name(“mus_vis”)”

11. **Extract_Table&Column_Name (D) — HAS_COMPONENT → interface**; p.4–5; `pending`
   - Source span: p.4 chars 3729–3881; chunk `chunk_785bb2357da95f231566a7893e116b3f`
   - Quote: “we devise two functions as follows: • Extract_Table&Column_Name (D): extracts the names of all the tables and their contained columns from the database.”

12. **LLM for Generation — HAS_COMPONENT → input prompts design**; p.5–5; `pending`
   - Source span: p.5 chars 2007–2105; chunk `chunk_5159a5fa625d869d5a21e72e43b4b713`
   - Quote: “After linearization, we design two types of input prompts for LLMs to fulfill different purposes1:”

13. **Table-based Question Answering (TableQA) — HAS_COMPONENT → Extract_Column_Name**; p.6–6; `pending`
   - Source span: p.6 chars 232–406; chunk `chunk_a1264db566130c104275b807d750904a`
   - Quote: “first, we invoke Extract_Column_Name (T ) to extract all column names of a table, linearize them, and leverage LLMs to select the relevant ones {c} according to the question.”

14. **IRR — HAS_COMPONENT → reading-then-reasoning**; p.6–7; `pending`
   - Source span: p.6 chars 4270–4379; chunk `chunk_2cdccff3910b914ee3f18d9beda20684`
   - Quote: “our method is a general iterative reading-then-reasoning (IRR) framework that can be used for different LLMs.”

15. **IRR — CONTROLLED_BY → in-context exemplars**; p.7–7; `pending`
   - Source span: p.7 chars 3327–3454; chunk `chunk_358a932cf9be09a75cae0606806b9318`
   - Quote: “By adding a few in- context exemplars (i.e., 15 for WQSP and 32 for MQA) to LLMs, we can further improve the model performance.”

16. **IRR — HAS_COMPONENT → interfaces for KG**; p.7–7; `pending`
   - Source span: p.7 chars 3455–3612; chunk `chunk_358a932cf9be09a75cae0606806b9318`
   - Quote: “In our approach, we devise interfaces for KG to efficiently read the relevant information, and leverage LLMs to extract useful parts and per- form reasoning.”

17. **interfaces for KG — IMPLEMENTS → efficiently read the relevant information**; p.7–7; `pending`
   - Source span: p.7 chars 3455–3612; chunk `chunk_358a932cf9be09a75cae0606806b9318`
   - Quote: “In our approach, we devise interfaces for KG to efficiently read the relevant information, and leverage LLMs to extract useful parts and per- form reasoning.”

18. **+ IRR (ours) — CONTROLLED_BY → 32 in-context exemplars**; p.7–8; `pending`
   - Source span: p.7 chars 4308–4406; chunk `chunk_1efd4680d043944e45eb1947af46faa9`
   - Quote: “when adding 32 in-context exemplars to the LLMs, they can obtain further performance improvements.”

19. **our proposed method — HAS_COMPONENT → Extract_Neighbor_Relations function**; p.8–8; `pending`
   - Source span: p.8 chars 1974–2165; chunk `chunk_c11d51b003e670a9b0426a34b4b70425`
   - Quote: “In each iteration, we first invoke the Ex- tract_Neighbor_Relations function to extract the neighboring relations (e.g., birthplace, residence, and education) of the topic entity “Harper Lee””

### STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases

1. **Instantiate Semi-structured Knowledge Base — HAS_COMPONENT → Relation template**; p.4–5; `pending`
   - Source span: p.5 chars 412–522; chunk `chunk_a430196a4fbe542e637ec87530659be3`
   - Quote: “Instantiate Semi-structured Knowledge Base Relation template Check satisfaction e.g., “Belongs to Radio Flyer””

2. **Relation template — IMPLEMENTS → Check satisfaction**; p.4–5; `pending`
   - Source span: p.5 chars 412–522; chunk `chunk_a430196a4fbe542e637ec87530659be3`
   - Quote: “Instantiate Semi-structured Knowledge Base Relation template Check satisfaction e.g., “Belongs to Radio Flyer””

3. **Sample Relational Requirements — HAS_COMPONENT → relation template construction**; p.5–5; `pending`
   - Source span: p.5 chars 1497–1832; chunk `chunk_aa14e2cd58a1f4d4b47738406e4cecde`
   - Quote: “For each query, we sample a practical relation template constructed with expert/domain knowledge, e.g., “(a product) belongs to <brand>” and ground it with sampled entities (i.e., a specific brand), e.g., “belongs to Radio Flyer”. This relational requirement yields a set of candidate entities, i.e., products belonging to Radio Flyer.”

4. **Extracting Textual Properties — HAS_COMPONENT → property extraction from textual document**; p.5–5; `pending`
   - Source span: p.5 chars 1869–2226; chunk `chunk_aa14e2cd58a1f4d4b47738406e4cecde`
   - Quote: “We randomly sample a candidate entity from the first step, referred to as the gold answer, from which LLMs extract properties that align with the interests of specific roles (e.g., customers, researchers, or doctors) in its textual document. In Figure 3, we extract multiple properties about the functionality and user experience from a Radio Flyer product.”

5. **Combining Textual and Relational Information — HAS_COMPONENT → query synthesis from properties and requirements**; p.5–5; `pending`
   - Source span: p.5 chars 2278–2555; chunk `chunk_aa14e2cd58a1f4d4b47738406e4cecde`
   - Quote: “We use two LLMs to synthesize queries from textual properties and relational requirements, enhancing diversity and reducing bias arise from relying on a single LLM. The first LLM focuses on generating natural, role-specific, and style-consistent (e.g., ArXiv searches) queries.”

6. **Combining Textual and Relational Information — HAS_COMPONENT → context enrichment and rephrasing**; p.5–5; `pending`
   - Source span: p.5 chars 2556–2701; chunk `chunk_aa14e2cd58a1f4d4b47738406e4cecde`
   - Quote: “The second LLM enriches the context and rephrases queries, which poses the need for advanced reasoning to comprehend them under complex contexts.”

7. **Small Dense Retrievers — HAS_COMPONENT → dense embeddings**; p.7–7; `pending`
   - Source span: p.7 chars 1378–1516; chunk `chunk_9d9ee136eacc99fb94f97a46f3bb2c7b`
   - Quote: “These compact models generate dense embeddings for both queries and documents, computing retrieval scores based on embedding similarities.”

8. **LLM-based Dense Retrievers — HAS_COMPONENT → dense embeddings**; p.7–7; `pending`
   - Source span: p.7 chars 1806–1900; chunk `chunk_9d9ee136eacc99fb94f97a46f3bb2c7b`
   - Quote: “These models leverage LLMs to generate dense embeddings that are more contextually expressive.”

9. **Multivector Retrievers — HAS_COMPONENT → overlapping chunks**; p.7–7; `pending`
   - Source span: p.7 chars 2026–2137; chunk `chunk_9d9ee136eacc99fb94f97a46f3bb2c7b`
   - Quote: “multi-ada-002 splits each document into overlapping chunks and embeds them using the same encoder as the query.”

10. **Multivector Retrievers — HAS_COMPONENT → token-level embeddings**; p.7–7; `pending`
   - Source span: p.7 chars 2277–2412; chunk `chunk_9d9ee136eacc99fb94f97a46f3bb2c7b`
   - Quote: “ColBERTv2 represents each document as multiple token-level embeddings for fine-grained matching, capturing richer semantic information.”

11. **LLM Rerankers — HAS_COMPONENT → Claude3 and GPT-4 rerankers**; p.7–7; `pending`
   - Source span: p.7 chars 2415–2574; chunk `chunk_bb730573725b148aa7913e7f17bb9261`
   - Quote: “LLM Rerankers: Claude3 and GPT-4 rerankers [11, 62]. These models improve the precision of top-k ada-002 results by reranking them using large language models.”

12. **LLM Rerankers — CONTROLLED_BY → k = 20 for synthesized queries and k = 10 for human-generated queries**; p.7–7; `pending`
   - Source span: p.7 chars 2575–2725; chunk `chunk_bb730573725b148aa7913e7f17bb9261`
   - Quote: “We employ GPT-4-turbo (gpt-4-1106-preview) and Claude3 (claude-3-opus), setting k = 20 for synthesized queries and k = 10 for human-generated queries.”

13. **Claude3 and GPT-4 rerankers — IMPLEMENTS → reranking using large language models**; p.7–7; `pending`
   - Source span: p.7 chars 2468–2574; chunk `chunk_bb730573725b148aa7913e7f17bb9261`
   - Quote: “These models improve the precision of top-k ada-002 results by reranking them using large language models.”

14. **metapath (field_of_study →paper) — IMPLEMENTS → requires an initial field_of_study entity to be filled in the corresponding query template**; p.16–17; `pending`
   - Source span: p.17 chars 749–890; chunk `chunk_10d454ac29067e7d1a22b8d6200af9e5`
   - Quote: “For example, the metapath (field_of_study →paper) requires an initial field_of_study entity to be filled in the corresponding query template.”

15. **multi-hop metapaths — IMPLEMENTS → requires an institution entity and a field_of_study entity to initialize the query**; p.16–17; `pending`
   - Source span: p.17 chars 891–1062; chunk `chunk_10d454ac29067e7d1a22b8d6200af9e5`
   - Quote: “For multi-hop metapaths, the last metapath (institution →author →paper ←field_of_study) requires an institution entity and a field_of_study entity to initialize the query.”

16. **synthesized queries — HAS_COMPONENT → multi-hop templates**; p.17–17; `pending`
   - Source span: p.17 chars 1107–1254; chunk `chunk_32b00088ff0d314f29a780a21391a70c`
   - Quote: “For synthesized queries, we listed 28 multi-hop templates designed by experts to cover various relation types and ensure their practical relevance.”

17. **query 'What is the drug that targets the genes or proteins expressed in <anatomy>?' — HAS_COMPONENT → multi-hop templates**; p.17–17; `pending`
   - Source span: p.17 chars 1255–1600; chunk `chunk_32b00088ff0d314f29a780a21391a70c`
   - Quote: “For instance, the query “What is the drug that targets the genes or proteins expressed in <anatomy>?” serves applications in precision medicine and pharmacogenomics, aiding researchers and healthcare professionals in identifying drugs that act on genes or proteins associated with specific anatomical areas and enabling more targeted treatments.”

18. **(drug →[carrier] →gene/protein →[carrier] →drug) — HAS_COMPONENT → [carrier]**; p.17–17; `pending`
   - Source span: p.17 chars 2601–2719; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(drug →[carrier] →gene/protein →[carrier] →drug): "What is the drug that has common gene/protein carrier with <drug>?"”

19. **(anatomy →[expression present] →gene/protein →enzyme →drug) — HAS_COMPONENT → [expression present]**; p.17–17; `pending`
   - Source span: p.17 chars 2721–2907; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(anatomy →[expression present] →gene/protein →enzyme →drug): "What is the drug that some genes or proteins act as an enzyme upon, where the genes or proteins are expressed in <anatomy>?"”

20. **(cellular_component →[interacts with] →gene/protein →[carrier] →drug) — HAS_COMPONENT → [interacts with]**; p.17–17; `pending`
   - Source span: p.17 chars 2909–3068; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(cellular_component →[interacts with] →gene/protein →[carrier] →drug): "What is the drug carried by genes or proteins that interact with <cellular_component>?"”

21. **(molecular_function →[interacts with] →gene/protein →[target] →drug) — HAS_COMPONENT → [interacts with]**; p.17–17; `pending`
   - Source span: p.17 chars 3070–3222; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(molecular_function →[interacts with] →gene/protein →[target] →drug): "What drug targets the genes or proteins that interact with <molecular_function>?"”

22. **(effect/phenotype →[side effect] →drug →[synergistic interaction] →drug) — HAS_COMPONENT → [synergistic interaction]**; p.17–17; `pending`
   - Source span: p.17 chars 3224–3399; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(effect/phenotype →[side effect] →drug →[synergistic interaction] →drug): "What drug has a synergistic interaction with the drug that has <effect/phenotype> as a side effect?"”

23. **(disease →[indication] →drug →[contraindication] →disease) — HAS_COMPONENT → [contraindication]**; p.17–17; `pending`
   - Source span: p.17 chars 3401–3536; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(disease →[indication] →drug →[contraindication] →disease): "What disease is a contraindication for the drugs indicated for <disease>?"”

24. **(gene/protein →[transporter] →drug →[side effect] →effect/phenotype) — HAS_COMPONENT → [transporter]**; p.17–17; `pending`
   - Source span: p.17 chars 3682–3840; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(gene/protein →[transporter] →drug →[side effect] →effect/phenotype): "What effect or phenotype is a [side effect] of the drug transported by <gene/protein>?"”

25. **(drug →[transporter] →gene/protein →[interacts with] →exposure) — HAS_COMPONENT → [interacts with]**; p.17–17; `pending`
   - Source span: p.17 chars 3842–3986; chunk `chunk_2d02555ebc9e77b34cf8306f68144ddc`
   - Quote: “(drug →[transporter] →gene/protein →[interacts with] →exposure): "What exposure may affect <drug>s efficacy by acting on its transporter genes?"”

26. **Find drugs that has a synergistic interaction with <drug> — HAS_COMPONENT → (pathway →[interacts with] →gene/protein →[interacts with] →pathway) & (pathway →[parent-child] →pathway)**; p.18–18; `pending`
   - Source span: p.18 chars 1554–1759; chunk `chunk_0d9aa18517b7f13cf82f4944d674daab`
   - Quote: “(pathway →[interacts with] →gene/protein →[interacts with] →pathway) & (pathway →[parent-child] →pathway): "Find pathway that is related with <pathway> and both can [interacts with] the same gene/protein."”

27. **Find gene/protein that can interect with <gene/protein> — HAS_COMPONENT → (gene/protein →[associated with] →disease →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein)**; p.18–18; `pending`
   - Source span: p.18 chars 1761–1980; chunk `chunk_0d9aa18517b7f13cf82f4944d674daab`
   - Quote: “(gene/protein →[associated with] →disease →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein): "Find gene/protein that can interect with <gene/protein> and both are associated with the same disease."”

28. **Find gene/protein that can interect with <gene/protein> — HAS_COMPONENT → (gene/protein →[associated with] →effect/phenotype →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein)**; p.18–18; `pending`
   - Source span: p.18 chars 1982–2219; chunk `chunk_0d9aa18517b7f13cf82f4944d674daab`
   - Quote: “(gene/protein →[associated with] →effect/phenotype →[associated with] →gene/protein) & (gene/protein →[ppi] →gene/protein): "Find gene/protein that can interect with <gene/protein> and both are associated with the same effect/phenotype."”

## Interpretation limits

- `author_assertion`, allowed relation signature, and quote matching are automated checks only.
- Section/paragraph attribution, whether a statement describes this paper’s method or prior work, entity naming, and whether a reported setting is truly a control parameter require semantic review.
- This pilot does not measure retrieval quality, graph reachability, or downstream QA accuracy.
- No rows were written to the production graph.
