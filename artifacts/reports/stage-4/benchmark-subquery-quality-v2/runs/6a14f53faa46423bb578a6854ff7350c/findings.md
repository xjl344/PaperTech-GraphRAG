# 规则与本地模型：子查询拆分质量

状态：completed；24道已曝光开发题，不是检索实验。

机械校验不等于语义质量；引用题面原文也可能分错方法。未运行召回、Embedding、重排或答案生成。

|组|已完成题|拆分题|子查询|仅方法名|校验失败|秒|输入Token|输出Token|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|Rule|24|20|41|22|0|0.04|0|0|
|Local-LLM|24|8|16|0|12|635.55|9939|2942|

## R01

G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。

### Rule

- G-Retriever
- KG-GPT

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["fragment_not_in_question: “图问答”是否对应同一种输出任务？比较..."]

## R02

LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。

### Rule

- LPKG
- RoG

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R03

CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。

### Rule

- CuriousLLM
- StructGPT

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R04

KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。

### Rule

- KGP
- STaRK

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R05

MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。

### Rule

- MindMap
- G-Retriever

未解析：[]
校验：[]
### Local-LLM

- MindMap 把图交给模型
- G-Retriever 把图交给模型

未解析：[{"text": "LLM 合并证据子图与 GAT、池化、MLP 的职责", "role": "unresolved", "start": 48, "end": 74, "possible_starts": [48], "offset_ambiguous": false}]
校验：[]

## R06

ToG 的束搜索与 Tree-of-Traversals 的搜索状态回溯各保留什么选择机会？后者发现低价值状态后怎样换路？

### Rule

- ToG 的束搜索 各保留什么选择机会？
- Tree-of-Traversals 的搜索状态回溯 各保留什么选择机会？

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_task_has_method_or_unresolved_pronoun"]

## R07

请从论文库找出两种让“语义上相关的材料”在图中连起来的不同办法：一种连接不同叫法的概念，另一种学习相邻支持段落。分别说明建边依据和训练信号。

### Rule

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]

## R08

ToG-2 和 STaRK 都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？

### Rule

- ToG-2
- STaRK

未解析：[]
校验：[]
### Local-LLM

- ToG-2 对实体上下文数量的分析 分别暴露了哪些成本或输入长度限制？
- STaRK 的候选重排设置 分别暴露了哪些成本或输入长度限制？

未解析：[]
校验：[]

## R09

HippoRAG 的“查询节点加邻居”消融与 KG-GPT 的 top-k 关系实验，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。

### Rule

- HippoRAG 的“查询节点加邻居”消融
- KG-GPT 的 top-k 关系实验

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R10

请找两篇直接讨论图证据冗余的工作：一篇分析图变密后支持事实覆盖与精度的取舍，另一篇通过聚类、采样保持多样性。它们分别控制哪个阶段？

### Rule

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]

## R11

面对结构化材料放不进提示词的问题，G-Retriever 与 StructGPT 分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。

### Rule

- G-Retriever
- StructGPT

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["fragment_not_in_question: 面对结构化材料放不进提示词的问题，分别在哪一步缩小输入？"]

## R12

ToG-R 与 ToG-2 对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。

### Rule

- ToG-R
- ToG-2

未解析：[]
校验：[]
### Local-LLM

- ToG-R 对候选实体分别更依赖哪类信息？
- ToG-2 对候选实体分别更依赖哪类信息？

未解析：[{"text": "随机实体剪枝与文档提供的实体上下文", "role": "unresolved", "start": 31, "end": 48, "possible_starts": [31], "offset_ambiguous": false}]
校验：[]

## R13

CuriousLLM 复用的 MDR 段落编码器与 HippoRAG 的同义边编码器，分别学习或比较什么？请区分“下一段支持证据”和“概念名称相似”。

### Rule

- CuriousLLM 复用的 MDR 段落编码器 分别学习或比较什么？
- HippoRAG 的同义边编码器 分别学习或比较什么？

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_task_has_method_or_unresolved_pronoun"]

## R14

RoG 的受约束广度优先搜索与 Tree-of-Traversals 的动作状态机怎样分别限制下一步动作？比较预先关系序列与可行操作空间。

### Rule

- RoG 的受约束广度优先搜索 怎样分别限制下一步动作？
- Tree-of-Traversals 的动作状态机 怎样分别限制下一步动作？

未解析：[]
校验：[]
### Local-LLM

- RoG 怎样分别限制下一步动作？
- Tree-of-Traversals 怎样分别限制下一步动作？

未解析：[{"text": "预先关系序列与可行操作空间", "role": "unresolved", "start": 55, "end": 68, "possible_starts": [55], "offset_ambiguous": false}]
校验：[]

## R15

LPKG 的 CLQA-Wiki 与 STaRK 各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。

### Rule

- LPKG
- STaRK

未解析：[]
校验：[]
### Local-LLM

- LPKG 各想补足什么评测缺口？
- STaRK 各想补足什么评测缺口？

未解析：[{"text": "交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。", "role": "unresolved", "start": 38, "end": 68, "possible_starts": [38], "offset_ambiguous": false}]
校验：[]

## R16

StructGPT 与 KG-GPT 处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。

### Rule

- StructGPT
- KG-GPT

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["local_and_shared_fragments_overlap"]

## R17

KGP 为什么用真实邻居段落去匹配模型预测的下一条证据？结合 CuriousLLM 对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。

### Rule

- KGP
- CuriousLLM

未解析：[]
校验：[]
### Local-LLM

- KGP 用真实邻居段落去匹配模型预测的下一条证据
- CuriousLLM 对原 KGP 错误关键词的观察 模型生成的“缺失证据”为什么仍需回取原文

未解析：[]
校验：[]

## R18

请从论文库举两个“图方法仍使用向量”的例子：一个用于把问题实体映射到图节点，另一个用于检索相关节点和边。比较向量所在的阶段，不能只回答方法名。

### Rule

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]

## R19

G-Retriever 冻结 LLM 的软提示训练与 ToG-2 的 training-free 分别意味着什么？比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。

### Rule

- G-Retriever 冻结 LLM 的软提示训练 分别意味着什么？
- ToG-2 的 training-free 分别意味着什么？

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R20

ToG 的 training-free 和 StructGPT 的 zero-shot/few-shot 是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。

### Rule

- ToG 的 training-free
- StructGPT 的 zero-shot/few-shot

未解析：[]
校验：[]
### Local-LLM

- ToG training-free
- StructGPT zero-shot/few-shot

未解析：[{"text": "结合两篇方法描述，区分参数更新与提示中示例数量。", "role": "unresolved", "start": 63, "end": 87, "possible_starts": [63], "offset_ambiguous": false}]
校验：[]

## R21

KGP 预测下一段证据与 RoG 生成关系路径后，分别怎样约束实际检索？比较邻居段落的相似匹配与沿关系序列的图搜索。

### Rule

- KGP 预测下一段证据 分别怎样约束实际检索？
- RoG 生成关系路径 分别怎样约束实际检索？

未解析：[]
校验：[]
### Local-LLM

- KGP 邻居段落的相似匹配 怎样约束实际检索？
- RoG 沿关系序列的图搜索 怎样约束实际检索？

未解析：[]
校验：[]

## R22

MindMap 的证据图合并和 CuriousLLM 的追问各会怎样改变后续可用信息？区分重组织已有证据与请求继续找证据。

### Rule

- MindMap 的证据图合并 各会怎样改变后续可用信息？
- CuriousLLM 的追问 各会怎样改变后续可用信息？

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## R23

请找出一项按候选答案条目集合衡量 Recall@k 的工作，以及一项可能生成 SQL 的结构化问答工作。为什么前者的 Recall@k 不能直接作为后者的 SQL 执行正确率？

### Rule

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：[]

## R24

HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。

### Rule

- HippoRAG 的节点 specificity 分别改变了什么？
- G-Retriever 的节点/边奖励 分别改变了什么？
- KG-GPT 的 top-k 参数 分别改变了什么？

未解析：[]
校验：[]
### Local-LLM

- 保持原问题 / 校验失败，见详细记录

未解析：[]
校验：["shared_only_has_local_aspect"]

## 分类统计

```json
{
  "anchored": {
    "Rule": {
      "cases": 20,
      "subqueries": 41,
      "method_only": 22,
      "invalid": 0,
      "seconds": 0.03518339997390285,
      "prompt_tokens": 0,
      "completion_tokens": 0
    },
    "Local-LLM": {
      "cases": 20,
      "subqueries": 16,
      "method_only": 0,
      "invalid": 12,
      "seconds": 635.548827199993,
      "prompt_tokens": 9939,
      "completion_tokens": 2942
    }
  },
  "no_anchor": {
    "Rule": {
      "cases": 4,
      "subqueries": 0,
      "method_only": 0,
      "invalid": 0,
      "seconds": 0.004699799988884479,
      "prompt_tokens": 0,
      "completion_tokens": 0
    },
    "Local-LLM": {
      "cases": 4,
      "subqueries": 0,
      "method_only": 0,
      "invalid": 0,
      "seconds": 0.002615700039314106,
      "prompt_tokens": 0,
      "completion_tokens": 0
    }
  }
}
```

[LangSmith 对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/c367d9c8-da2a-48d6-b609-6d18d7733a41/compare?selectedSessions=e5c2bdd6-1863-44ee-a212-a516dff0ad01,492d6f88-d34a-443d-998a-0b1141d9cd4d)
