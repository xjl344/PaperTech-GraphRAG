# 阶段 4 关系导向题集 v2

40 道题：4 道事实、4 道改写、24 道跨文本关系、8 道反例。可回答题中跨文本占 75%；24 道跨文本题均需要至少两篇不同论文的原文，部分需要三篇。

这是接触过语料和既有失败的开发集。来源由 Codex 核查，不等同独立人工金标。v1 的题目、分数和失败记录保留，新旧总分不可直接比较。

## 运行与检查

在项目根目录执行；以下检查只读语料、无需启动 Neo4j 或调用模型：

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
python -X utf8 scripts/freeze-stage4-v2.py --check
```

需要重新评测时，显式选择 v2（会调用 Cloudflare 与 DeepSeek；最多 64 次生成请求，不在本次题集修改中执行）：

```powershell
python -X utf8 scripts/eval-stage4.py --benchmark benchmark-v2
```

v2 原始结果写入 `artifacts/reports/stage-4/benchmark-v2/`；原来的 `report-stage4.py` 仍只负责 v1 报表。

每轮对照会先创建并核对 LangSmith Dataset，再把两组结果作为 Experiment 关联到同一题目。离线题单与上传状态保存在本目录，上传失败只补传已有结果。

## 判读规则

- 基础题仅评检索；跨文本题和反例按证据门控生成，两组设置一致。
- 每题必要事实必须齐全：一方证据不能代替另一方；引用有效不等于关系成立。
- 按关系方向、实体角色、来源覆盖和缺口表达逐项核查；反例可用证据纠正前提，无须一律拒答。
- 分别报告基础题、跨文本题和反例；不预设 Graph 胜出，也不为当前已入图关系定制金标。
- 分析链是评分提纲，不是生产图边或完整路径金标；“共同数据集”不能推出继承、因果或性能优越。
- 支持池采用逐项核查的原文，不按关键词共现自动扩展；尚未穷举全部等价来源，池外材料需另行审阅。

## 题目与预期关系

### F01 · fact

G-Retriever 把相关子图检索形式化成什么优化问题？

预期要点：G-Retriever 将图检索表述为 Prize-Collecting Steiner Tree 优化。

- `pcst`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，PDF 第 1—1 页；`chunk_3a7f7a1f47b2586d9d9877afb9110567`。

### F02 · fact

KG-GPT 的三个主要处理步骤是什么？

预期要点：KG-GPT 三步为 Sentence Segmentation、Graph Retrieval、Inference。

- `kggpt`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，PDF 第 1—1 页；`chunk_61e96cb10e247f7d002b4163920cc737`。

### F03 · fact

STaRK 是什么类型的基准，覆盖哪三个应用领域？

预期要点：STaRK 覆盖产品搜索、学术论文搜索和精准医疗。

- `stark`：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases，PDF 第 1—1 页；`chunk_6b5383484693f6226010eab8143f80d6`。

### F04 · fact

Roadmap 将 LLM 与 KG 的融合归纳为哪三类路线？

预期要点：三类路线为 KG-enhanced LLMs、LLM-augmented KGs、Synergized LLMs + KGs。

- `roadmap`：Unifying Large Language Models and Knowledge Graphs: A Roadmap，PDF 第 1—1 页；`chunk_f9acd01074a4f478a8d9fe8c7e77be91`。

### P01 · paraphrase

HippoRAG 怎样从查询概念出发，在一次检索中联系分散的段落？

预期要点：HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

### P02 · paraphrase

RoG 怎样先安排关系路线，再获取实际证据来回答问题？

预期要点：RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。

- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### P03 · paraphrase

Tree-of-Traversals 怎样限制搜索，以及不同停止条件分别意味着什么？

预期要点：Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。

### P04 · paraphrase

LPKG 怎样利用 KG 获得规划训练信号，从而帮助复杂问题的检索？

预期要点：LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。

- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 1—1 页；`chunk_e07b345ba2a42d01f295e47f196061d5`。

### R01 · cross

比较 ToG 与 ToG-2：从问题到证据，LLM、实体关系和文档分别如何参与？画出两条检索流程，并引用两篇论文。

预期要点：ToG 用 LLM 迭代束搜索探索 KG；ToG-2 以实体连接文档，并用文档上下文辅助图检索，两者工作流不同。

关系提纲：ToG → LLM 束搜索 → KG 路径；ToG-2 → 实体连接文档 → 图/上下文交替检索

判读边界：不能只凭名称或工作流差异断言 ToG-2 在所有任务优于 ToG。

- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 1—1 页；`chunk_e09b5a88c34014513aad6c0d6121f790`。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 1—1 页；`chunk_9b63637ef18ed2d67ff105ef55092df3`。

### R02 · cross

比较 HippoRAG 与 RoG：查询概念、关系路径计划和实际证据分别处在什么位置？说明两种方法如何连接分散事实。

预期要点：HippoRAG 用查询概念作为 PPR 种子整合跨片段信息；RoG 先生成关系路径计划，再检索实际推理路径。

关系提纲：查询概念 → PPR → 跨片段检索；关系路径计划 → KG 路径检索 → 推理

判读边界：不能把 RoG 的关系路径计划写成 PPR，也不能据共同目标推导技术继承。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R03 · cross

结合 KGP 和 CuriousLLM 原文，后者针对前者提出了什么增强？把多文档图、遍历代理、后续问题及其监督信号串起来，并区分作者评价与已验证事实。

预期要点：KGP 构图并让代理收集段落；CuriousLLM 原文将自身描述为增强，引入追问机制及问题/证据到后续问题的训练信号。对 KGP 成本和幻觉的评价须归于 CuriousLLM 作者。

关系提纲：KGP → 多文档图/遍历代理；CuriousLLM → 追问增强 → Follow-upQA

判读边界：不能反转增强方向，也不能把作者报告当成本系统复现实验结论。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，PDF 第 1—1 页；`chunk_b959214e888053dae53b16a5259d7ea9`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。

### R04 · cross

比较 StructGPT 与 LPKG：一个方法在回答时如何获得证据，另一个方法在训练时如何获得规划数据？说明 KG/结构化数据在两者中的不同角色。

预期要点：StructGPT 在推理时经接口迭代读取结构化证据；LPKG 从 KG 派生规划数据并微调模型。

关系提纲：结构化数据 → 接口读取 → 推理；KG → 规划训练数据 → 微调规划能力

判读边界：不能把推理时读取接口等同训练数据构建，也不能认为两者共享训练协议。

- `struct`：StructGPT: A General Framework for Large Language Model to Reason over Structured Data，PDF 第 1—1 页；`chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad`。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 1—1 页；`chunk_e07b345ba2a42d01f295e47f196061d5`。

### R05 · cross

ToG 和 RoG 都利用 KG 推理，为什么不能据此把两者都归为免训练方法？分别追踪 KG 在在线搜索和训练中的作用。

预期要点：ToG 声明无需额外训练；RoG 明确包括从 KG 蒸馏知识的训练，同时支持推理时接入其他 LLM。

关系提纲：ToG → 免额外训练的在线搜索；RoG → KG 蒸馏训练 + 路径检索

判读边界：推理模块可接入任意 LLM 不等于整套方法没有训练。

- `tog_training`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 1—1 页；`chunk_e09b5a88c34014513aad6c0d6121f790`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R06 · cross

比较 ToG-2 与 LPKG：图知识分别怎样帮助文档证据检索和问题规划？说明二者发生在训练还是推理阶段。

预期要点：ToG-2 免训练地交替检索图和上下文；LPKG 以 KG 派生数据微调规划能力。

关系提纲：ToG-2 → 推理时图/文档协作；LPKG → KG 规划数据 → 训练

判读边界：不能因为都连接 KG 与 QA 就视为同一阶段或同一算法。

- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 1—1 页；`chunk_9b63637ef18ed2d67ff105ef55092df3`。
- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 1—1 页；`chunk_e07b345ba2a42d01f295e47f196061d5`。

### R07 · cross

比较 HippoRAG 与 KGP 的图表示：图从什么材料构造，检索时沿什么关联获取证据？说明二者为何不能直接共享一种“节点就是段落”的解释。

预期要点：HippoRAG 用 LLM 将语料转成无模式 KG、由查询概念启动 PPR；KGP 节点表示段落或文档结构，边为相似或结构关系。

关系提纲：语料 → HippoRAG 无模式 KG → PPR；多文档 → KGP 段落/结构图 → 遍历代理

判读边界：不能把 KGP 的节点定义直接套到 HippoRAG。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，PDF 第 1—1 页；`chunk_b959214e888053dae53b16a5259d7ea9`。

### R08 · cross

G-Retriever 与 ToG-2 都用图帮助获取上下文，但它们选择证据的机制怎样不同？分别连接输入规模问题、相关子图选择以及实体和文档的协作。

预期要点：G-Retriever 用 PCST 表述相关子图检索以控制大图输入；ToG-2 交替进行图检索与上下文检索。

关系提纲：大图上下文限制 → G-Retriever PCST 子图；实体/文档 → ToG-2 双向协作

判读边界：不能据都用图就声称 ToG-2 使用 PCST，也不能声称两者实测资源相同。

- `pcst`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，PDF 第 1—1 页；`chunk_3a7f7a1f47b2586d9d9877afb9110567`。
- `grscale`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，PDF 第 2—3 页；`chunk_5c9e14854565607ec53c355da481c451`。
- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 1—1 页；`chunk_9b63637ef18ed2d67ff105ef55092df3`。

### R09 · cross

从 ToG 与 ToG-2 的评测段落出发，找出共同使用的 WebQSP 与 QALD10-en，分别给出“方法→数据集”的来源，再说明为什么这个连接不能证明优劣或继承。

预期要点：两篇均列出 WebQSP 和 QALD10-en；这是评测数据集关联，不是方法继承或受控性能比较。

关系提纲：ToG → WebQSP/QALD10-en ← ToG-2

判读边界：不能把共享数据集路径当成 IMPROVES_UPON 或因果关系。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 5—5 页；`chunk_deb9eea46e529705dffdd1103729c44c`。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 6—6 页；`chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

### R10 · cross

把 HippoRAG 与 Tree-of-Traversals 通过各自原文中的 2Wiki 测试集名称连接起来，再比较它们如何完成跨事实检索。保留数据集原始名称及设置差异。

预期要点：保留两篇不同名称；HippoRAG 用 PPR，Tree-of-Traversals 搜索动作树。HippoRAG 使用抽取的验证集问题，Tree-of-Traversals 列出所用模型，不能默认协议一致。

关系提纲：HippoRAG → 2WikiMultiHopQA；Tree-of-Traversals → 2WikiMultiHop；PPR 对照动作树搜索

判读边界：名称相近不证明划分、语料、底座和指标一致。

- `hippods`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 5—5 页；`chunk_3fa28005a4df0de5249826585cf9d713`。
- `totds`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 5—5 页；`chunk_a8ce6be635ba6abbbc71daeb86e809e9`。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。

### R11 · cross

沿“KG-GPT/RoG→MetaQA→跳数与指标/知识来源”比较两篇实验。RoG 中 Freebase 与 Wiki-Movies 分别承担什么角色？每个角色须给出原文。

预期要点：KG-GPT 报告 MetaQA 各跳数 Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是预训练/迁移来源，扩展实验使用 1000 个训练样本。

关系提纲：KG-GPT → MetaQA 1/2/3-hop → Hits@1；RoG → MetaQA-3hop → Wiki-Movies；Freebase → 迁移起点

判读边界：不能把 Freebase 写成该 MetaQA 测试 KG，也不能从不匹配实验协议直接判胜负。

- `kggptds`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，PDF 第 4—4 页；`chunk_3f7eb65828761447433c66c28ad111a4`。
- `rogmeta`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 20—20 页；`chunk_f5c88d605f651f26c093f30b836a98aa`。

### R12 · cross

Tree-of-Traversals 的 MusicBrainz-x-Wikidata 与 LPKG 的 CLQA-Wiki 怎样分别连接到知识来源？虽然都涉及 Wikidata，二者考察的关系推理能力有何区别？

预期要点：前者要求跨两个 KG 综合推理；后者从 Wikidata 子集构建，覆盖 multi-hop、comparison、intersection、union。

关系提纲：MusicBrainz-x-Wikidata → MusicBrainz + Wikidata；CLQA-Wiki → Wikidata 子集 → 四类逻辑题

判读边界：共享 Wikidata 不能推出同一题集或相同难度。

- `totmusic`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 5—6 页；`chunk_f4962498025654850621ee329d0af7d6`。
- `lpbench`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 2—2 页；`chunk_ab66789d9bc91de68948962d6c3f0011`。

### R13 · cross

HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 是什么关系？引用两篇的设置说明，判断能否直接用结果数字比较两种检索方法。

预期要点：ToG-2 将 AdvHotpotQA 描述为 HotpotQA 的挑战子集；HippoRAG 抽取验证集并组成候选语料，ToG-2 使用 full Wiki，不能直接横比。

关系提纲：HippoRAG → HotpotQA；ToG-2 → AdvHotpotQA → HotpotQA 挑战子集

判读边界：不能把父数据集与子集视为相同测试协议。

- `hippods`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 5—5 页；`chunk_3fa28005a4df0de5249826585cf9d713`。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 6—6 页；`chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

### R14 · cross

比较 ToG 与 ToG-2 对 Creak 及 QA 任务的评测指标，再结合两篇对知识来源/数据设置的说明，列出跨论文性能比较仍需核对的条件。

预期要点：按原文保留 ToG 所称 exact match accuracy (Hits@1)；ToG-2 对 Creak/FEVER 用 Acc.，其他用 EM，并说明 full Wiki。还需核对划分、底座、来源和提示条件。

关系提纲：ToG → 各任务 Hits@1；ToG-2 → Creak/FEVER Acc. + 其他 EM；比较 → 协议核对

判读边界：不能只凭相同或近似指标名宣布受控优劣，也不能补写 ToG 未提供的设置。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 5—5 页；`chunk_deb9eea46e529705dffdd1103729c44c`。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 6—6 页；`chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

### R15 · cross

比较 Tree-of-Traversals 与 CuriousLLM 如何表达“还要继续找证据”或“停止”。区分最大深度、最大扩展数、找到答案阈值和表示证据充分的特殊 token。

预期要点：Tree-of-Traversals 达阈值可停止，最大深度强制 done，最大扩展数返回 Cannot find answer；CuriousLLM 用追问或特殊 token 表示缺口/充分。

关系提纲：动作树 → 阈值/深度/扩展预算；追问训练 → 缺失证据问题/充分证据 token

判读边界：不能把两种预算终止都写成成功，也不能把特殊 token 当成本项目已实现的停止器。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。

### R16 · cross

MindMap 与 RoG 都讨论可解释推理。分别追踪其外部 KG、模型内部知识或关系计划怎样进入答案，说明一张可解释路径为何不自动保证答案正确。

预期要点：MindMap 结合内隐与外部知识并展示思维图；RoG 用 KG 支持的关系计划检索路径。路径可追溯仍需核对每项结论是否受证据支持。

关系提纲：MindMap → 内隐知识 + 外部 KG → mind map；RoG → 关系计划 → 有效路径 → 推理

判读边界：不能把可解释性或作者的 faithful 表述等同所有答案已验证正确。

- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，PDF 第 1—1 页；`chunk_2f4809d54362f998c1c0710e915a721b`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R17 · cross

STaRK 和 MindMap 都涉及医学相关任务：分别是什么类型的基准或方法、原文描述了什么医学场景？这些段落能否证明 MindMap 在 STaRK 上接受过评测？

预期要点：STaRK 是含精准医疗领域的检索基准，MindMap 是重点包含医学 QA 的方法；所引段落不足以建立 MindMap EVALUATED_ON STaRK。

关系提纲：STaRK → 半结构检索基准 → 精准医疗；MindMap → KG 提示方法 → 医学 QA

判读边界：主题重合不能作为评测关系证据；不足以证明不等于证明从未评测。

- `stark`：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases，PDF 第 1—1 页；`chunk_6b5383484693f6226010eab8143f80d6`。
- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，PDF 第 1—1 页；`chunk_2f4809d54362f998c1c0710e915a721b`。

### R18 · cross

比较 KG-GPT 与 RoG：句子分割、图检索、关系路径规划分别属于哪套流程？把输入到证据再到推理的顺序写清楚。

预期要点：KG-GPT 的三步为 Sentence Segmentation、Graph Retrieval、Inference；RoG 的三段为 planning、retrieval、reasoning，其中先生成关系路径计划。

关系提纲：KG-GPT → 句子分割 → 图检索 → 推理；RoG → 关系计划 → 路径检索 → 推理

判读边界：不能把共有检索/推理步骤当成相同规划器或继承证据。

- `kggpt`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，PDF 第 1—1 页；`chunk_61e96cb10e247f7d002b4163920cc737`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R19 · cross

在 ToG、HippoRAG 与 RoG 中，分别找出“LLM 逐步探索图”“查询种子驱动图算法”“先规划关系路径再取证”的方法。每项给出一篇原文，并比较多跳关联发生在哪一步。

预期要点：三种描述分别对应 ToG、HippoRAG、RoG；多跳关联分别通过交互搜索、一次 PPR 检索及计划约束的路径检索实现。

关系提纲：ToG → 束搜索；HippoRAG → PPR；RoG → 关系计划/路径检索

判读边界：不能因为都处理多跳就认为推理步骤或计算代价相同。

- `tog`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 1—1 页；`chunk_e09b5a88c34014513aad6c0d6121f790`。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R20 · cross

比较 ToG-2、HippoRAG 与 KGP 如何把文档中的分散信息联系起来。分别说明图与文档的连接方式，以及检索最终怎样回到支持证据。

预期要点：ToG-2 用实体连接文档并交替检索；HippoRAG 从语料抽图并用 PPR 整合跨片段信息；KGP 用段落/结构节点及代理收集支持段落。

关系提纲：实体连接文档/上下文协作；语料抽图/PPR 跨片段；段落结构图/代理遍历

判读边界：不能把三种图的节点、边及检索过程当成同一表示。

- `tog2`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 1—1 页；`chunk_9b63637ef18ed2d67ff105ef55092df3`。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，PDF 第 1—1 页；`chunk_b959214e888053dae53b16a5259d7ea9`。

### R21 · cross

围绕“有限上下文或有限搜索预算下如何保留必要证据”，比较 G-Retriever、Tree-of-Traversals 与 CuriousLLM 的机制。哪些是子图选择，哪些是搜索边界，哪些是证据缺口信号？

预期要点：G-Retriever 选择相关子图；Tree-of-Traversals 限制深度和扩展；CuriousLLM 学习追问或输出证据充分信号。三者约束对象不同。

关系提纲：输入规模 → 子图选择；搜索空间 → 有界树搜索；证据缺口 → 追问/充分 token

判读边界：不能没有同条件实验就声称任一机制必然最快或最省 Token。

- `grscale`：G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering，PDF 第 2—3 页；`chunk_5c9e14854565607ec53c355da481c451`。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。

### R22 · cross

比较 LPKG、CuriousLLM 与 RoG 的训练信号和推理用途：图派生规划数据、问题与支持证据生成追问、KG 支持的关系路径分别属于谁？不能只回答三者都用了 KG。

预期要点：逐项区分 LPKG 的 KG 派生规划数据、CuriousLLM Follow-upQA 的输入/目标，以及 RoG 的关系路径计划与 KG 蒸馏训练。

关系提纲：KG → LPKG 规划数据；问题+证据 → CuriousLLM 追问；KG → RoG 关系路径计划

判读边界：不能把三种监督目标互换，也不能臆测完全相同的训练数据。

- `lpdata`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 1—1 页；`chunk_e07b345ba2a42d01f295e47f196061d5`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### R23 · cross

ToG/ToG-R 的搜索宽度和深度怎样联系到 LLM 调用次数？再与 Tree-of-Traversals 的深度、扩展预算对照，说明为什么这些公式/上限不能直接换算成统一运行时排名。

预期要点：ToG-R 用随机实体剪枝减少调用，公式如原文；Tree-of-Traversals 有不同动作树搜索及预算。调用公式、搜索上限与墙钟时延不是同一量。

关系提纲：ToG → 2ND+D+1；ToG-R → ND+D+1；Tree-of-Traversals → depth/expansions 边界

判读边界：不能反转 ToG-R 与 ToG 的变体关系，也不能从不同预算直接推出实测速度。

- `togr`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 22—22 页；`chunk_91a4a2e6943ad6a8074492d3f7229692`。
- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。

### R24 · cross

结合 LPKG 的 CLQA-Wiki 与 Tree-of-Traversals 的 2Wiki/MusicBrainz-x-Wikidata 描述，区分“多跳”“交并逻辑”“跨 KG”三种任务关系，并逐项绑定到相应证据。

预期要点：CLQA-Wiki 明列四类逻辑题，2Wiki 段描述多跳模板，MusicBrainz-x-Wikidata 要求结合两个 KG；任务属性不同。

关系提纲：CLQA-Wiki → 多跳/比较/交/并；2Wiki → 多跳；MusicBrainz-x-Wikidata → 跨 KG

判读边界：不能推断其他数据集绝不含交并题，也不能把跨 KG 与多跳逻辑视为互斥概念。

- `lpbench`：Learning to Plan for Retrieval-Augmented Large Language Models from Knowledge Graphs，PDF 第 2—2 页；`chunk_ab66789d9bc91de68948962d6c3f0011`。
- `totds`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 5—5 页；`chunk_a8ce6be635ba6abbbc71daeb86e809e9`。
- `totmusic`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 5—6 页；`chunk_f4962498025654850621ee329d0af7d6`。

### N01 · negative

因为 HippoRAG 和 RoG 都处理图上多跳推理，能否据两篇的方法描述断言“RoG 直接继承了 HippoRAG 的 PPR”？请检查关系和方向。

预期要点：原文分别支持 PPR 与关系路径规划，不能建立所声称的继承关系。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。
- `rog`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 1—1 页；`chunk_58e7ae48fdb49536bc066f6e74ccd2a0`。

### N02 · negative

ToG 与 ToG-2 都使用 WebQSP，因此“ToG-2 在所有数据集和所有底座上严格优于 ToG”成立吗？请从共享数据集关系的证据边界作答。

预期要点：共同数据集不能推出全称优越性；需配对实验与完整适用条件。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `togds`：Think-on-Graph: Deep and Responsible Reasoning of Large Language Model with Knowledge Graph，PDF 第 5—5 页；`chunk_deb9eea46e529705dffdd1103729c44c`。
- `tog2ds`：Think-on-Graph 2.0: Deep and Interpretable Large Language Model Reasoning with Knowledge Graph-guided Retrieval，PDF 第 6—6 页；`chunk_16f86a00cebdf5e10d83c3a540fbc7f7`。

### N03 · negative

KGP 和 HippoRAG 都从文档获得图，所以“它们的每个图节点都是一个段落，边都是段落语义相似度”成立吗？分别核对原文。

预期要点：KGP 有段落/结构节点与多种边，HippoRAG 是语料抽取的无模式 KG，不能套用统一节点/边定义。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，PDF 第 1—1 页；`chunk_b959214e888053dae53b16a5259d7ea9`。
- `hippo`：HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models，PDF 第 2—2 页；`chunk_a58244558a2137d85a4b8e53d5c4ebaf`。

### N04 · negative

KG-GPT 和 RoG 都评测 MetaQA；RoG 又写了 transfer from Freebase，是否可推出两篇 MetaQA 实验的测试 KG 都是 Freebase？

预期要点：RoG 明确 MetaQA-3hop 基于 Wiki-Movies；Freebase 为迁移来源，不能把共享基准和训练来源拼成测试 KG。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `kggptds`：KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models，PDF 第 4—4 页；`chunk_3f7eb65828761447433c66c28ad111a4`。
- `rogmeta`：Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning，PDF 第 20—20 页；`chunk_f5c88d605f651f26c093f30b836a98aa`。

### N05 · negative

仅因 STaRK 有精准医疗领域、MindMap 讨论医学 QA，能否建立“MindMap→EVALUATED_ON→STaRK”并报告测试分数？

预期要点：两篇相关段落没有提供该评测关系或分数；说明缺证据，不捏造数值，也不声称证明从未测试。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `stark`：STaRK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases，PDF 第 1—1 页；`chunk_6b5383484693f6226010eab8143f80d6`。
- `mind`：MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models，PDF 第 1—1 页；`chunk_2f4809d54362f998c1c0710e915a721b`。

### N06 · negative

请给出 NebulaGraphRAG-2099 继承 HippoRAG 后，在 LunarQA-2099 上相对 RoG 提升的官方精确分数，并画出继承链。

预期要点：没有这些虚构方法、基准和分数的语料依据，应拒绝编造继承链与数值。

判读边界：不得认可题干中未经支持的关系或编造数值。


### N07 · negative

CuriousLLM 说自己增强了 KGP，是否意味着“KGP 以 CuriousLLM 的 Follow-upQA 为训练来源”？请结合两篇原文检查方向。

预期要点：CuriousLLM 描述自身的增强及 Follow-upQA；不能反向推出 KGP 使用后者训练数据。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `kgp`：Knowledge Graph Prompting for Multi-Document Question Answering，PDF 第 1—1 页；`chunk_b959214e888053dae53b16a5259d7ea9`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。

### N08 · negative

Tree-of-Traversals 达到 max depth 和 max expansions 时，都像 CuriousLLM 的特殊 token 一样表示“证据已经充分、答案正确”吗？

预期要点：最大深度强制 done、最大扩展数返回无法找到答案；CuriousLLM 的 token 是充分证据信号，不能等同成功或正确性保证。

判读边界：不得认可题干中未经支持的关系或编造数值。

- `totbound`：Tree-of-Traversals: A Zero-Shot Reasoning Algorithm for Augmenting Black-box Language Models with Knowledge Graphs，PDF 第 4—4 页；`chunk_dac5f23e1b87249cf88eff5c6cc54355`。
- `curious`：CuriousLLM: Elevating Multi-Document QA with Reasoning-Infused Knowledge Graph Prompting，PDF 第 1—1 页；`chunk_43145c0748762d6b4c650c65721f826f`。
