# 子查询拆分审阅预览

- 规则版本：`question-spans-v1`
- 来源题集：`benchmark-relation-holdout-v1`
- 题集 SHA-256：`6f0b9710ce0a265304b63fee8e8bd91e1a18f2cf0337e13753b211cdcbe6ceba`
- 约束：拆分仅使用题面和方法别名，不使用金标、正文或图谱；未调用模型。

状态：仅文本预览，未运行检索、Embedding、重排、生成或 LangSmith 对照实验。

24 题分类：{'method_only': 11, 'span': 9, 'no_anchor': 4}；共 41 条子查询。

拆分函数只接收题面；脚本从旧题集中投影 id/question，不把金标交给拆分函数。
字符偏移：Python 字符索引，0 起始、左闭右开。
首版限制：任一方法缺少明确描述时，本题所有方法都退回方法名；不解前者/后者等指代。
方法名回退表示任务信息不足；明确从句也不表示完整保留了比较任务。
质量检查：R09、R20 只保留技术描述，没有完整问句；R15、R17 的整题回退过于保守。
现有题目已用于开发，不能作为新的泛化验收。

## R01

题面：G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。
审阅状态：`method_only`
- `SQ01` G-Retriever [method_only]：G-Retriever
  - spans: method[0:11]=G-Retriever
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` KG-GPT [method_only]：KG-GPT
  - spans: method[14:20]=KG-GPT
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [11:14]  与 
- [20:73]  所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。

## R02

题面：LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。
审阅状态：`method_only`
- `SQ01` LPKG [method_only]：LPKG
  - spans: method[0:4]=LPKG
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` RoG [method_only]：RoG
  - spans: method[7:10]=RoG
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [4:7]  和 
- [10:62]  都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。

## R03

题面：CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。
审阅状态：`method_only`
- `SQ01` CuriousLLM [method_only]：CuriousLLM
  - spans: method[0:10]=CuriousLLM
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` StructGPT [method_only]：StructGPT
  - spans: method[13:22]=StructGPT
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [10:13]  与 
- [22:71]  的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。

## R04

题面：KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。
审阅状态：`method_only`
- `SQ01` KGP [method_only]：KGP
  - spans: method[0:3]=KGP
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` STaRK [method_only]：STaRK
  - spans: method[6:11]=STaRK
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [3:6]  与 
- [11:56]  的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。

## R05

题面：MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。
审阅状态：`method_only`
- `SQ01` MindMap [method_only]：MindMap
  - spans: method[0:7]=MindMap
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` G-Retriever [method_only]：G-Retriever
  - spans: method[10:21]=G-Retriever
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [7:10]  与 
- [21:75]  都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。

## R06

题面：ToG 的束搜索与 Tree-of-Traversals 的搜索状态回溯各保留什么选择机会？后者发现低价值状态后怎样换路？
审阅状态：`span`
- `SQ01` ToG [span]：ToG 的束搜索 各保留什么选择机会？
  - spans: method_clause[0:8]=ToG 的束搜索; shared_question[36:46]=各保留什么选择机会？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` Tree-of-Traversals [span]：Tree-of-Traversals 的搜索状态回溯 各保留什么选择机会？
  - spans: method_clause[10:36]=Tree-of-Traversals 的搜索状态回溯; shared_question[36:46]=各保留什么选择机会？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [8:10] 与 
- [46:61] 后者发现低价值状态后怎样换路？

## R07

题面：请从论文库找出两种让“语义上相关的材料”在图中连起来的不同办法：一种连接不同叫法的概念，另一种学习相邻支持段落。分别说明建边依据和训练信号。
审阅状态：`no_anchor`
子查询：无（保持原问题路径）

## R08

题面：ToG-2 和 STaRK 都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？
审阅状态：`method_only`
- `SQ01` ToG-2 [method_only]：ToG-2
  - spans: method[0:5]=ToG-2
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` STaRK [method_only]：STaRK
  - spans: method[8:13]=STaRK
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [5:8]  和 
- [13:63]  都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？

## R09

题面：HippoRAG 的“查询节点加邻居”消融与 KG-GPT 的 top-k 关系实验，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。
审阅状态：`span`
- `SQ01` HippoRAG [span]：HippoRAG 的“查询节点加邻居”消融
  - spans: method_clause[0:21]=HippoRAG 的“查询节点加邻居”消融
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` KG-GPT [span]：KG-GPT 的 top-k 关系实验
  - spans: method_clause[23:42]=KG-GPT 的 top-k 关系实验
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [21:23] 与 
- [42:71] ，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。

## R10

题面：请找两篇直接讨论图证据冗余的工作：一篇分析图变密后支持事实覆盖与精度的取舍，另一篇通过聚类、采样保持多样性。它们分别控制哪个阶段？
审阅状态：`no_anchor`
子查询：无（保持原问题路径）

## R11

题面：面对结构化材料放不进提示词的问题，G-Retriever 与 StructGPT 分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。
审阅状态：`method_only`
- `SQ01` G-Retriever [method_only]：G-Retriever
  - spans: method[17:28]=G-Retriever
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` StructGPT [method_only]：StructGPT
  - spans: method[31:40]=StructGPT
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [0:17] 面对结构化材料放不进提示词的问题，
- [28:31]  与 
- [40:83]  分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。

## R12

题面：ToG-R 与 ToG-2 对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。
审阅状态：`method_only`
- `SQ01` ToG-R [method_only]：ToG-R
  - spans: method[0:5]=ToG-R
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` ToG-2 [method_only]：ToG-2
  - spans: method[8:13]=ToG-2
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [5:8]  与 
- [13:65]  对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。

## R13

题面：CuriousLLM 复用的 MDR 段落编码器与 HippoRAG 的同义边编码器，分别学习或比较什么？请区分“下一段支持证据”和“概念名称相似”。
审阅状态：`span`
- `SQ01` CuriousLLM [span]：CuriousLLM 复用的 MDR 段落编码器 分别学习或比较什么？
  - spans: method_clause[0:24]=CuriousLLM 复用的 MDR 段落编码器; shared_question[43:53]=分别学习或比较什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` HippoRAG [span]：HippoRAG 的同义边编码器 分别学习或比较什么？
  - spans: method_clause[26:42]=HippoRAG 的同义边编码器; shared_question[43:53]=分别学习或比较什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [24:26] 与 
- [42:43] ，
- [53:75] 请区分“下一段支持证据”和“概念名称相似”。

## R14

题面：RoG 的受约束广度优先搜索与 Tree-of-Traversals 的动作状态机怎样分别限制下一步动作？比较预先关系序列与可行操作空间。
审阅状态：`span`
- `SQ01` RoG [span]：RoG 的受约束广度优先搜索 怎样分别限制下一步动作？
  - spans: method_clause[0:14]=RoG 的受约束广度优先搜索; shared_question[41:53]=怎样分别限制下一步动作？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` Tree-of-Traversals [span]：Tree-of-Traversals 的动作状态机 怎样分别限制下一步动作？
  - spans: method_clause[16:41]=Tree-of-Traversals 的动作状态机; shared_question[41:53]=怎样分别限制下一步动作？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [14:16] 与 
- [53:69] 比较预先关系序列与可行操作空间。

## R15

题面：LPKG 的 CLQA-Wiki 与 STaRK 各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。
审阅状态：`method_only`
- `SQ01` LPKG [method_only]：LPKG
  - spans: method[0:4]=LPKG
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` STaRK [method_only]：STaRK
  - spans: method[19:24]=STaRK
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [4:19]  的 CLQA-Wiki 与 
- [24:68]  各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。

## R16

题面：StructGPT 与 KG-GPT 处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。
审阅状态：`method_only`
- `SQ01` StructGPT [method_only]：StructGPT
  - spans: method[0:9]=StructGPT
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` KG-GPT [method_only]：KG-GPT
  - spans: method[12:18]=KG-GPT
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [9:12]  与 
- [18:72]  处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。

## R17

题面：KGP 为什么用真实邻居段落去匹配模型预测的下一条证据？结合 CuriousLLM 对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。
审阅状态：`method_only`
- `SQ01` KGP [method_only]：KGP
  - spans: method[0:3]=KGP
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`
- `SQ02` CuriousLLM [method_only]：CuriousLLM
  - spans: method[31:41]=CuriousLLM
  - fallback: `coordinated_methods_with_unassigned_details`; warnings: `shared_details_not_assigned`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [3:31]  为什么用真实邻居段落去匹配模型预测的下一条证据？结合 
- [41:81]  对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。

## R18

题面：请从论文库举两个“图方法仍使用向量”的例子：一个用于把问题实体映射到图节点，另一个用于检索相关节点和边。比较向量所在的阶段，不能只回答方法名。
审阅状态：`no_anchor`
子查询：无（保持原问题路径）

## R19

题面：G-Retriever 冻结 LLM 的软提示训练与 ToG-2 的 training-free 分别意味着什么？比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。
审阅状态：`span`
- `SQ01` G-Retriever [span]：G-Retriever 冻结 LLM 的软提示训练 分别意味着什么？
  - spans: method_clause[0:25]=G-Retriever 冻结 LLM 的软提示训练; shared_question[49:57]=分别意味着什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` ToG-2 [span]：ToG-2 的 training-free 分别意味着什么？
  - spans: method_clause[27:48]=ToG-2 的 training-free; shared_question[49:57]=分别意味着什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [25:27] 与 
- [57:89] 比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。

## R20

题面：ToG 的 training-free 和 StructGPT 的 zero-shot/few-shot 是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。
审阅状态：`span`
- `SQ01` ToG [span]：ToG 的 training-free
  - spans: method_clause[0:19]=ToG 的 training-free
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` StructGPT [span]：StructGPT 的 zero-shot/few-shot
  - spans: method_clause[22:52]=StructGPT 的 zero-shot/few-shot
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [19:22]  和 
- [52:87]  是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。

## R21

题面：KGP 预测下一段证据与 RoG 生成关系路径后，分别怎样约束实际检索？比较邻居段落的相似匹配与沿关系序列的图搜索。
审阅状态：`span`
- `SQ01` KGP [span]：KGP 预测下一段证据 分别怎样约束实际检索？
  - spans: method_clause[0:11]=KGP 预测下一段证据; shared_question[25:36]=分别怎样约束实际检索？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` RoG [span]：RoG 生成关系路径 分别怎样约束实际检索？
  - spans: method_clause[13:23]=RoG 生成关系路径; shared_question[25:36]=分别怎样约束实际检索？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [11:13] 与 
- [23:25] 后，
- [36:58] 比较邻居段落的相似匹配与沿关系序列的图搜索。

## R22

题面：MindMap 的证据图合并和 CuriousLLM 的追问各会怎样改变后续可用信息？区分重组织已有证据与请求继续找证据。
审阅状态：`span`
- `SQ01` MindMap [span]：MindMap 的证据图合并 各会怎样改变后续可用信息？
  - spans: method_clause[0:14]=MindMap 的证据图合并; shared_question[30:43]=各会怎样改变后续可用信息？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` CuriousLLM [span]：CuriousLLM 的追问 各会怎样改变后续可用信息？
  - spans: method_clause[16:30]=CuriousLLM 的追问; shared_question[30:43]=各会怎样改变后续可用信息？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [14:16] 和 
- [43:61] 区分重组织已有证据与请求继续找证据。

## R23

题面：请找出一项按候选答案条目集合衡量 Recall@k 的工作，以及一项可能生成 SQL 的结构化问答工作。为什么前者的 Recall@k 不能直接作为后者的 SQL 执行正确率？
审阅状态：`no_anchor`
子查询：无（保持原问题路径）

## R24

题面：HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。
审阅状态：`span`
- `SQ01` HippoRAG [span]：HippoRAG 的节点 specificity 分别改变了什么？
  - spans: method_clause[0:24]=HippoRAG 的节点 specificity; shared_question[62:70]=分别改变了什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ02` G-Retriever [span]：G-Retriever 的节点/边奖励 分别改变了什么？
  - spans: method_clause[25:44]=G-Retriever 的节点/边奖励; shared_question[62:70]=分别改变了什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`
- `SQ03` KG-GPT [span]：KG-GPT 的 top-k 参数 分别改变了什么？
  - spans: method_clause[45:62]=KG-GPT 的 top-k 参数; shared_question[62:70]=分别改变了什么？
  - fallback: `None`; warnings: `cross_method_comparison_not_rewritten`

未进入子查询的题面片段（包括连接词，不等同于必须补回的任务内容）：

- [24:25] 、
- [44:45] 、
- [70:104] 按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。
