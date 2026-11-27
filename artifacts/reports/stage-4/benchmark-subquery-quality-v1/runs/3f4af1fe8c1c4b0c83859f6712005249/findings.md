# 规则与本地模型：子查询拆分质量

状态：interrupted；24道已曝光开发题，不是检索实验。

机械校验不等于语义质量；引用题面原文也可能分错方法。未运行召回、Embedding、重排或答案生成。

|组|已完成题|拆分题|子查询|仅方法名|校验失败|秒|输入Token|输出Token|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|Rule|5|5|10|10|0|0.01|0|0|
|Local-LLM|4|4|8|0|0|174.35|1506|656|

## R01

G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。

### Rule

- G-Retriever
- KG-GPT

未解析：[]
校验：[]
### Local-LLM

- G-Retriever 比较前者对文本图的回答与可视定位 比较前者对文本图的回答与可视定位 和后者的事实核验及 KGQA
- KG-GPT 和后者的事实核验及 KGQA 比较前者对文本图的回答与可视定位 和后者的事实核验及 KGQA

未解析：[]
校验：[]

## R02

LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。

### Rule

- LPKG
- RoG

未解析：[]
校验：[]
### Local-LLM

- LPKG 它们的计划表示能直接互换吗？
- RoG 它们的计划表示能直接互换吗？

未解析：[{"text": "自然语言子问题与关系路径怎样连接到后续执行", "role": "unresolved", "start": 40, "end": 61, "possible_starts": [40], "offset_ambiguous": false}]
校验：[]

## R03

CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。

### Rule

- CuriousLLM
- StructGPT

未解析：[]
校验：[]
### Local-LLM

- CuriousLLM 比较“追问”和“读取后推理”
- StructGPT 比较“追问”和“读取后推理”

未解析：[{"text": "CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？", "role": "unresolved", "start": 0, "end": 41, "possible_starts": [0], "offset_ambiguous": false}]
校验：[]

## R04

KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。

### Rule

- KGP
- STaRK

未解析：[]
校验：[]
### Local-LLM

- KGP 比较支持段落和答案实体
- STaRK 比较支持段落和答案实体

未解析：[{"text": "KGP 与 STaRK 的检索成功各指找到了什么？", "role": "unresolved", "start": 0, "end": 25, "possible_starts": [0], "offset_ambiguous": false}, {"text": "说明两者的召回分母为什么不能直接混用。", "role": "unresolved", "start": 37, "end": 56, "possible_starts": [37], "offset_ambiguous": false}]
校验：[]

## R05

MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。

### Rule

- MindMap
- G-Retriever

未解析：[]
校验：[]

## 分类统计

```json
{
  "anchored": {
    "Rule": {
      "cases": 5,
      "subqueries": 10,
      "method_only": 10,
      "invalid": 0,
      "seconds": 0.011829400056740269,
      "prompt_tokens": 0,
      "completion_tokens": 0
    },
    "Local-LLM": {
      "cases": 4,
      "subqueries": 8,
      "method_only": 0,
      "invalid": 0,
      "seconds": 174.3526828000322,
      "prompt_tokens": 1506,
      "completion_tokens": 656
    }
  }
}
```

[LangSmith 对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/406747b3-9bfc-43b6-ab19-35d426c52a66/compare?selectedSessions=2c6fdbee-d5ec-455a-aeea-03fc88139a50,9406b92c-4fcd-4ad9-8369-15eb5799860b)
