# benchmark-recall-width-v1

状态：completed。40道已曝光开发题；无生成，不作泛化验收。

|组别|跨论文候选覆盖|跨论文最终覆盖|全来源题数|跨论文胜/平/负|
|---|---:|---:|---:|---|

[LangSmith实验对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/922f8637-f7d1-49f9-b7dd-e049320927c7/compare?selectedSessions=13fd2252-d967-488c-9f19-6190ac394907,630fe956-0e29-4629-95a4-c7ded20eeff5,8487b924-f92b-403d-a8ce-ad6d0f834bf0)

|Dense20|59.72%|N/A|0/24|0/24/0|
|Dense40|65.97%|N/A|0/24|3/21/0|
|Dense60|71.53%|N/A|0/24|6/18/0|

生成Token=0；新Embedding调用=0。历史模型Token不计作本轮消费。离线回放耗时、数据库检索耗时与新重排推理耗时分别记录，不当作完整在线响应时延。
8道negative只列来源诊断，不计主指标；论文覆盖与必要原文覆盖分开。

|题号|组别|候选覆盖|最终覆盖|与控制组差异|失败来源及阶段|
|---|---|---:|---:|---|---|
|F01|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F01|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F01|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F02|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F02|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F02|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F03|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F03|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F03|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F04|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F04|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F04|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F05|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F05|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F05|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F06|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F06|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F06|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F07|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F07|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F07|Dense60|100.00%|N/A|tie +0.00%|齐全|
|F08|Dense20|100.00%|N/A|tie +0.00%|齐全|
|F08|Dense40|100.00%|N/A|tie +0.00%|齐全|
|F08|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R01|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R01|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R01|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R02|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R02|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R02|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R03|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R03|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R03|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R04|Dense20|50.00%|N/A|tie +0.00%|R04.S01 upstream_missing|
|R04|Dense40|50.00%|N/A|tie +0.00%|R04.S01 upstream_missing|
|R04|Dense60|50.00%|N/A|tie +0.00%|R04.S01 upstream_missing|
|R05|Dense20|50.00%|N/A|tie +0.00%|R05.S01 upstream_missing|
|R05|Dense40|50.00%|N/A|tie +0.00%|R05.S01 upstream_missing|
|R05|Dense60|50.00%|N/A|tie +0.00%|R05.S01 upstream_missing|
|R06|Dense20|0.00%|N/A|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Dense40|0.00%|N/A|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Dense60|50.00%|N/A|win +50.00%|R06.S01 upstream_missing|
|R07|Dense20|50.00%|N/A|tie +0.00%|R07.S01 upstream_missing|
|R07|Dense40|50.00%|N/A|tie +0.00%|R07.S01 upstream_missing|
|R07|Dense60|50.00%|N/A|tie +0.00%|R07.S01 upstream_missing|
|R08|Dense20|0.00%|N/A|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Dense40|0.00%|N/A|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Dense60|50.00%|N/A|win +50.00%|R08.S01 upstream_missing|
|R09|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R09|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R09|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R10|Dense20|50.00%|N/A|tie +0.00%|R10.S01 upstream_missing|
|R10|Dense40|100.00%|N/A|win +50.00%|齐全|
|R10|Dense60|100.00%|N/A|win +50.00%|齐全|
|R11|Dense20|50.00%|N/A|tie +0.00%|R11.S02 upstream_missing|
|R11|Dense40|50.00%|N/A|tie +0.00%|R11.S02 upstream_missing|
|R11|Dense60|50.00%|N/A|tie +0.00%|R11.S02 upstream_missing|
|R12|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R12|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R12|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R13|Dense20|50.00%|N/A|tie +0.00%|R13.S02 upstream_missing|
|R13|Dense40|50.00%|N/A|tie +0.00%|R13.S02 upstream_missing|
|R13|Dense60|50.00%|N/A|tie +0.00%|R13.S02 upstream_missing|
|R14|Dense20|50.00%|N/A|tie +0.00%|R14.S01 upstream_missing|
|R14|Dense40|50.00%|N/A|tie +0.00%|R14.S01 upstream_missing|
|R14|Dense60|50.00%|N/A|tie +0.00%|R14.S01 upstream_missing|
|R15|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R15|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R15|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R16|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R16|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R16|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R17|Dense20|50.00%|N/A|tie +0.00%|R17.S01 upstream_missing|
|R17|Dense40|50.00%|N/A|tie +0.00%|R17.S01 upstream_missing|
|R17|Dense60|50.00%|N/A|tie +0.00%|R17.S01 upstream_missing|
|R18|Dense20|0.00%|N/A|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Dense40|50.00%|N/A|win +50.00%|R18.S01 upstream_missing|
|R18|Dense60|50.00%|N/A|win +50.00%|R18.S01 upstream_missing|
|R19|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R19|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R19|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R20|Dense20|50.00%|N/A|tie +0.00%|R20.S01 upstream_missing|
|R20|Dense40|50.00%|N/A|tie +0.00%|R20.S01 upstream_missing|
|R20|Dense60|50.00%|N/A|tie +0.00%|R20.S01 upstream_missing|
|R21|Dense20|0.00%|N/A|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Dense40|0.00%|N/A|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Dense60|0.00%|N/A|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R22|Dense20|50.00%|N/A|tie +0.00%|R22.S01 upstream_missing|
|R22|Dense40|100.00%|N/A|win +50.00%|齐全|
|R22|Dense60|100.00%|N/A|win +50.00%|齐全|
|R23|Dense20|100.00%|N/A|tie +0.00%|齐全|
|R23|Dense40|100.00%|N/A|tie +0.00%|齐全|
|R23|Dense60|100.00%|N/A|tie +0.00%|齐全|
|R24|Dense20|33.33%|N/A|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing|
|R24|Dense40|33.33%|N/A|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing|
|R24|Dense60|66.67%|N/A|win +33.33%|R24.S01 upstream_missing|
|N01|Dense20|0.00%|N/A|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Dense40|0.00%|N/A|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Dense60|0.00%|N/A|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N02|Dense20|100.00%|N/A|tie +0.00%|齐全|
|N02|Dense40|100.00%|N/A|tie +0.00%|齐全|
|N02|Dense60|100.00%|N/A|tie +0.00%|齐全|
|N03|Dense20|50.00%|N/A|tie +0.00%|N03.S02 upstream_missing|
|N03|Dense40|50.00%|N/A|tie +0.00%|N03.S02 upstream_missing|
|N03|Dense60|50.00%|N/A|tie +0.00%|N03.S02 upstream_missing|
|N04|Dense20|100.00%|N/A|tie +0.00%|齐全|
|N04|Dense40|100.00%|N/A|tie +0.00%|齐全|
|N04|Dense60|100.00%|N/A|tie +0.00%|齐全|
|N05|Dense20|100.00%|N/A|tie +0.00%|齐全|
|N05|Dense40|100.00%|N/A|tie +0.00%|齐全|
|N05|Dense60|100.00%|N/A|tie +0.00%|齐全|
|N06|Dense20|0.00%|N/A|tie +0.00%|N06.S01 upstream_missing|
|N06|Dense40|0.00%|N/A|tie +0.00%|N06.S01 upstream_missing|
|N06|Dense60|0.00%|N/A|tie +0.00%|N06.S01 upstream_missing|
|N07|Dense20|100.00%|N/A|tie +0.00%|齐全|
|N07|Dense40|100.00%|N/A|tie +0.00%|齐全|
|N07|Dense60|100.00%|N/A|tie +0.00%|齐全|
|N08|Dense20|100.00%|N/A|tie +0.00%|齐全|
|N08|Dense40|100.00%|N/A|tie +0.00%|齐全|
|N08|Dense60|100.00%|N/A|tie +0.00%|齐全|
