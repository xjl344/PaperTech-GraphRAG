# 16 题三步优化结果

运行：`5351b670c38d41348d772f73a4ab2517`；题集 SHA-256：`fcbffc2cd3012d7e49daa8361e202f2b6211095974236c48dc8bfe057f7fb7f6`。

## 第一步：真实检索候选诊断

逐题保存 fulltext、dense、graph、融合前后及重排后候选和来源位置。候选快照不包含金标；金标只用于后续离线覆盖计算。

| 检查项 | 完成数 |
|---|---:|
| 题目候选快照 | 16/16 |

已知支持块首次缺失位置（按必要事实计数；未命中支持池不等于确定漏召回）：

| 分类 | 必要事实数 |
|---|---:|
| no_known_support_in_any_retrieval_channel | 3 |
| support_reached_final_ranking | 33 |
| candidate_lost_after_initial_fusion | 2 |

## 第二步：固定候选选择对照

| 策略 | 平均冻结事实覆盖 | 全事实覆盖题数 | 平均序列化字节 |
|---|---:|---:|---:|
| Budget-before | 33.33% | 2 / 16 | 5342.5 |
| Evidence-first | 36.46% | 3 / 16 | 5490.9 |
| Diverse-evidence-first | 37.50% | 2 / 16 | 5526.1 |

选择策略：`Diverse-evidence-first`。规则：highest aggregate frozen support-unit coverage; tie-break by lower serialized evidence/path bytes。

与第一步基线相比，优化选择器的题目级事实覆盖变化：2 题提高、13 题持平、1 题退化（R22）。平均覆盖提高 4.17 个百分点；这是有限支持池对齐，不是答案语义准确率。原文优先策略全事实覆盖 3/16，去重策略为 2/16，故两者取舍需看逐题目标。

## 第三步：端到端回答对照

| 组别 | 生成调用 | 平均事实覆盖 | 平均生成秒 | 输入 Token | 输出 Token |
|---|---:|---:|---:|---:|---:|
| Baseline | 16 | 33.33% | 5.70 | 29444 | 8028 |
| Optimized | 16 | 37.50% | 5.76 | 30142 | 7637 |

引用结构校验：31/32 通过；校验失败题：R18-Baseline。通过仅说明引用 ID/原文片段格式有效，不代表引用足以支持答案全部断言。

端到端逐题对照中，优化组与基线组各生成 16 次；平均生成时延分别为 5.76 秒和 5.70 秒，Token 消耗分别为 30,142/7,637 与 29,444/8,028（输入/输出）。模型随机性未重复估计。

分类指标（优化策略的证据覆盖；按冻结题型分组）：

| 题型 | 题数 | 平均事实覆盖 | 全事实覆盖题数 |
|---|---:|---:|---:|
| cross | 16 | 37.50% | 2 |

语义正确性及引用是否支持每项断言仍需独立人工逐题审查；没有使用自动指标冒充语义评分。

| 题号 | 基线答案状态 | 优化答案状态 | 基线/优化事实覆盖 | 答案差异 | Trace |
|---|---|---|---:|---|---|
| R03 | partial | partial | 50% / 50% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/bd43cf0c-1f3a-4978-a5ab-0e34b263fd67?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/05524bfa-a81e-438c-9c06-1d556f9b2c30?poll=true) |
| R04 | partial | partial | 0% / 50% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/eaaa1ffa-5cda-4691-ae75-0739b4f4151b?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d9abe45e-1ed4-4365-9dc7-0036ac9517b9?poll=true) |
| R05 | ok | ok | 50% / 50% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/c4ec31df-93fe-43a3-bad3-812eceb34690?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/0c2a3ea7-71a3-4a7f-b375-23eb48d6d9f8?poll=true) |
| R06 | partial | partial | 100% / 100% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/775bc5c6-ee04-494e-8e59-d1bdf665b291?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/f444a93d-04e6-4c98-9754-6ce5d886286d?poll=true) |
| R08 | partial | partial | 33% / 33% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/4e86ec91-4370-4b2c-b84e-e0d0b16ed26f?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/da6b26af-f766-4877-b26c-65792f7acfd4?poll=true) |
| R09 | partial | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/2bfb81ff-a200-46cb-b4da-a65c8d8e1024?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/303a7e78-cc93-4307-a132-2ecb33840dac?poll=true) |
| R11 | partial | partial | 50% / 50% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/12947c9b-3fdc-45d9-9aea-2c4b0ece58da?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/1aa70b6b-a7ea-4e6a-91a9-ceea4b55934d?poll=true) |
| R12 | partial | ok | 50% / 100% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/ac14af3f-9f31-4c58-ba7a-21d2a4c8f932?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b5a6f0c5-c4bc-4ea7-969a-04d46cd12821?poll=true) |
| R13 | partial | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/c42c116f-e428-431b-82ff-e28d4b2b3bd4?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6471054f-4dfe-4e9b-956f-e4d2fb61f486?poll=true) |
| R18 | citation_error | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/105c8dab-06f9-4c64-ab6e-35f440009f79?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/da7249da-e533-4c00-bfb4-4c0d740b681c?poll=true) |
| R19 | partial | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d220c186-6ef0-449c-a982-a75ccca60f70?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d7e1d8d4-1665-471c-9038-9a08ead5181f?poll=true) |
| R20 | partial | partial | 33% / 33% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/b2e1c41a-20a7-47f2-b96a-641fdedb99bb?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/6dfa94a7-a4de-4d25-a071-4abe17c0d713?poll=true) |
| R21 | partial | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d983c667-f441-43f1-a248-cae450d23d94?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/907762f6-c1f5-4f61-ae6e-e53336714ac6?poll=true) |
| R22 | ok | partial | 100% / 67% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/0c491791-b985-4038-a135-1e20a4e13f44?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/e28cce83-3127-4763-8566-951eeb088971?poll=true) |
| R23 | partial | partial | 0% / 0% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/c4a098b6-e027-410f-88f6-f89457f9f736?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/8a09d0ab-2ac3-4037-bdcd-e19a799bc0ad?poll=true) |
| R24 | partial | partial | 67% / 67% | 不同 | [基线](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/2c097e8d-f788-4102-92dd-0eccc0511c5b?poll=true) · [优化](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/54183410-13fd-4dad-86c6-1e9b53d756ec?poll=true) |

完整逐题回答、原文、候选与位置、引用、图路径、Token 和调用 Trace 见 `summary.json` 与每题 JSON；候选阶段明细见 `*-candidates.json`；逐必要事实的候选阶段归因见 `retrieval-diagnosis.json`。

该题集是按旧 Graph 失败筛选的诊断子集，不代表整体总体收益。一步和二步指标是冻结支持池对齐；生成结果仅完成自动引用结构核验，语义审查仍待人工完成。
