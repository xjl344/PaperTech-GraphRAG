# benchmark-holdout-v1 18 题全新未见泛化集逐题语义核查报告

- **审核来源标注（`review_origin`）**：`ai_delegated`（由代理依据冻结原文证据与参考要点逐题核对，**不冒充独立人类领域专家人工评分**）。
- **对应运行**：`f3889ede3e1a47598620e440f38c6f6f`（[findings.md](file:///e:/PaperTech-GraphRAG/artifacts/reports/stage-4/benchmark-holdout-v1/runs/f3889ede3e1a47598620e440f38c6f6f/report/findings.md)）。
- **核心分离原则**：明确区分“检索来源覆盖率”、“引用协议交付状态”与“答案语义正确性”三个维度。

## 1. 语义核查汇总（18 题未见集，与旧 40 题零重叠）

| 维度 | Legacy-Hybrid | Production-Final | 说明 |
|---|---:|---:|---|
| 14 题自动来源覆盖（事实+跨论文） | 46.43% (4/14 全覆盖) | **95.24% (13/14 全覆盖)** | +48.81 pp；10 增 / 4 平 / 0 退；上游零漏检 |
| **可交付答案语义完整正确（18 题）** | **4/18** (`22.2%`) | **15/18** (`83.3%`) | 提升 **+11 题（3.75×）** |
| 可交付答案部分正确/缺要点 | 10/18 | 0/18 | — |
| 严重残缺或引用协议拦截失败 | 4/18 (`H-F06/R04/R05/R08`) | 3/18 (`H-F03/F05/R06`) | 见下方根因说明：3 条原始回答语义均完整正确 |
| 原始生成内容语义完整正确（含被格式拦截 3 条） | 4/18 | **18/18** (`100.0%`) | 0 例事实幻觉、0 例伪造引用 |
| **4 题反例规范拒答 (`status=refused`)** | **0/4** | **4/4 (100%)** | 全部识别伪前提/越界实体并引用反驳原文 |

> **3 条 `citation_error` 复盘（`H-F03`、`H-F05`、`H-R06`）**：三题的回答内容与 `[E#:q#]` 引文均准确对应原文，无幻觉、无缺 `status`；拦截仅因模型在 v3 模式下多输出了 `"citations": []`（`H-F05`、`H-R06`）或说明性注释键 `"_note"`（`H-F03`）。两项无害格式边界已在本轮结束前于 `src/papertech/citations.py` 修补并加入单元测试回归（不改动本冻结运行历史记录）。

## 2. 逐题核查表（18 题）

| 题号 | 类别 | Legacy-Hybrid 语义判读（状态 / 覆盖） | Production-Final 语义判读（状态 / 覆盖） | 关键差异与边界说明 |
|---|---|---|---|---|
| `H-F01` | fact | ✅ 完整正确 (`ok` / 1.0) | ✅ 完整正确 (`ok` / 1.0) | 两组均完整答出 STaRK 三领域、合成+人工、k=20/k=10 与 10% 抽样。 |
| `H-F02` | fact | ⚠️ 部分正确 (`partial` / 0.5) | ✅ 完整正确 (`ok` / 1.0) | Legacy 漏掉三数据集名与 100 条抽样；Prod 完整答出 WebQSP/WTQ/Spider、100 条、74% 与 62%。 |
| `H-F03` | fact | ⚠️ 部分正确 (`partial` / 1.0) | ⚠️ 格式拦截 / 原始语义✅完整 (`citation_error` / 1.0) | Legacy 漏 Table 8 合并结果；Prod 原始回答完整答出 Neighbor/Path-only、Table 8 数值（0.7960/0.5890）及 p1 +8.2%，仅因额外 `_note` 键被拒。 |
| `H-F04` | fact | ⚠️ 部分正确 (`partial` / 0.5) | ✅ 完整正确 (`ok` / 1.0) | Legacy 漏 MDR-KG BERT 编码器训练；Prod 完整覆盖 Mistral-7B QLoRA、-85% 时间与 MDR 正负样本训练。 |
| `H-F05` | fact | ⚠️ 部分正确 (`partial` / 0.5) | ⚠️ 格式拦截 / 原始语义✅完整 (`citation_error` / 1.0) | Legacy 漏 beam-search top-3 理由；Prod 原始回答完整覆盖两项消融与 K=3 噪声/耗时权衡，仅因多余 `"citations": []` 被拒。 |
| `H-F06` | fact | ❌ 严重残缺 (`partial` / 0.0) | ✅ 完整正确 (`ok` / 1.0) | Legacy 漏财报语料/17,013 文档/7 关系/97 题及 GraphRAG 成本原因；Prod 全部准确引用。 |
| `H-R01` | cross | ⚠️ 部分正确 (`partial` / 0.5) | ✅ 完整正确 (`ok` / 1.0) | Legacy 漏 ToG N=3/Dmax=3 理由；Prod 完整对比 ToG 线性开销/增益递减 + LLM 剪枝与 ToG-2 长上下文 BGE-Reranker DRM。 |
| `H-R02` | cross | ⚠️ 部分正确 (`partial` / 1.0) | ✅ 基本完整正确 (`ok` / 1.0) | Legacy 缺冻结与错误分析细节；Prod 完整答出 G-Retriever 冻结/PT/LoRA/静态检索局限与 LPKG LoRA 微调 + 40 条错例分布（检索 17 最高），仅未明写 LPKG QA 固定 GPT-3.5。 |
| `H-R03` | cross | ✅ 完整正确 (`ok` / 1.0) | ✅ 完整正确 (`ok` / 1.0) | 两组均准确答出 KGP 预算下种子覆盖权衡与 CuriousLLM Table 3 ET 略降数值。 |
| `H-R04` | cross | ❌ 失败 (`citation_error` / 0.0) | ✅ 完整正确 (`partial` / 1.0) | Legacy 检索全漏且引用出错；Prod 完整答出 KG-GPT 12-shot + 图检索错最少（17/4/3/0）与 StructGPT 15/32 示例 + 74%/62% 错例分布。 |
| `H-R05` | cross | ❌ 严重残缺 (`partial` / 0.0) | ✅ 完整正确 (`ok` / 1.0) | Legacy 缺 GraphQA 三集名单与 STaRK 检索器分析；Prod 全部准确答出（含 DPR/QAGNN 过拟合与 Reranker 在人工查询占优）。 |
| `H-R06` | cross | ⚠️ 部分正确 (`partial` / 0.5) | ⚠️ 格式拦截 / 原始语义✅完整 (`citation_error` / 1.0) | Legacy 漏 HippoRAG 检索器/1000 题/两超参；Prod 原始回答完整覆盖双方设置与 DLPKG 9000 题对比，仅因多余 `"citations": []` 被拒。 |
| `H-R07` | cross | ⚠️ 部分正确 (`partial` / 0.0) | ✅ 完整正确 (`partial` / 0.333) | 典型分离案例：Prod 自动 chunk 覆盖仅 33.3%，但通过等价原文块（Abstract/Conclusion/Method）准确答全 KEPLER、DRAGON、ToT 与 MindMap 全部要点！ |
| `H-R08` | cross | ❌ 严重残缺 (`partial` / 0.0) | ✅ 完整正确 (`ok` / 1.0) | Legacy 完全漏 KGP 与 ToG-2 案例；Prod 完整覆盖 KGP 结构/内容分流、HippoRAG path-finding（Thomas Südhof）与 ToG-2 Both/Doc-enhanced 两案例。 |
| `H-N01` | negative | ✅ 语义纠正 (`ok` / 1.0) | ✅ 规范拒答 (`refused` / 1.0) | Prod 明确拒答并逐字引用 100 条仅调 τ=0.8 与 PPR=0.5 两个超参。 |
| `H-N02` | negative | ⚠️ 部分纠正 (`partial` / 1.0) | ✅ 规范拒答 (`refused` / 1.0) | Prod 明确指出 LoRA 微调规划 LLM、QA LLM 解耦且固定为 GPT-3.5。 |
| `H-N03` | negative | ⚠️ 部分纠正 (`partial` / 0.0) | ✅ 规范拒答 (`refused` / 1.0) | Prod 准确反驳冻结 LLM + PT、无训练 PCST 与 70.49 检索率（非消除误差）。 |
| `H-N04` | negative | ✅ 语义识破 (`partial` / 0.0) | ✅ 规范拒答 (`refused` / 0.0) | Prod 明确指出语料无 GraphOmni-2099 与 BioSTaRK-XL 并规范拒答。 |
