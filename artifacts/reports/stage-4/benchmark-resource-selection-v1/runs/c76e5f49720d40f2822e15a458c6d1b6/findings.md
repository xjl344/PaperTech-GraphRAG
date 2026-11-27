# benchmark-resource-selection-v1

状态：completed。40道已曝光开发题；无生成，不作泛化验收。

|组别|跨论文候选覆盖|跨论文最终覆盖|全来源题数|跨论文胜/平/负|
|---|---:|---:|---:|---|

[LangSmith实验对照](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/datasets/7c31a7f5-f273-4721-a38c-e0c3645f1ac8/compare?selectedSessions=bb8c9541-99ce-451e-9487-9cceed5aa87f,8f2d4393-e723-402e-a1b1-6c8b15848d40,f09dcff1-01cd-40e5-bd11-fe39a0706c42,8c1d5661-be9d-4d55-8f1a-f2025cff0843,cca20699-580a-4654-942e-05678f56e5cb,84b59f09-fea7-4f57-ae22-cf677b9c895f)

|Named-6000-8|59.72%|33.33%|2/24|0/24/0|
|Named-6000-12|59.72%|33.33%|2/24|0/24/0|
|Named-8000-8|59.72%|37.50%|4/24|2/22/0|
|Named-8000-12|59.72%|37.50%|4/24|2/22/0|
|Score-6000-8|59.72%|31.25%|2/24|0/23/1|
|Score-8000-12|59.72%|37.50%|4/24|2/22/0|

生成Token=0；新Embedding调用=0。历史模型Token不计作本轮消费。离线回放耗时、数据库检索耗时与新重排推理耗时分别记录，不当作完整在线响应时延。
8道negative只列来源诊断，不计主指标；论文覆盖与必要原文覆盖分开。

|题号|组别|候选覆盖|最终覆盖|与控制组差异|失败来源及阶段|
|---|---|---:|---:|---|---|
|F01|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F01|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F01|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F01|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F01|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F01|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F02|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F02|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F02|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F02|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F02|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F02|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F03|Named-6000-8|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F03|Named-6000-12|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F03|Named-8000-8|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F03|Named-8000-12|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F03|Score-6000-8|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F03|Score-8000-12|100.00%|0.00%|tie +0.00%|F03.S01 context_selection|
|F04|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F04|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F04|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F04|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F04|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F04|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F05|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F05|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F05|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F05|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F05|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F05|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F06|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F06|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F06|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F06|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F06|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F06|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F07|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F07|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F07|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F07|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F07|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F07|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F08|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F08|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|F08|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|F08|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|F08|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|F08|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|R01|Named-6000-8|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R01|Named-6000-12|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R01|Named-8000-8|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R01|Named-8000-12|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R01|Score-6000-8|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R01|Score-8000-12|100.00%|50.00%|tie +0.00%|R01.S02 context_selection|
|R02|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|R02|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|R02|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|R02|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|R02|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|R02|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|R03|Named-6000-8|100.00%|50.00%|tie +0.00%|R03.S01 context_selection|
|R03|Named-6000-12|100.00%|50.00%|tie +0.00%|R03.S01 context_selection|
|R03|Named-8000-8|100.00%|100.00%|win +50.00%|齐全|
|R03|Named-8000-12|100.00%|100.00%|win +50.00%|齐全|
|R03|Score-6000-8|100.00%|50.00%|tie +0.00%|R03.S01 context_selection|
|R03|Score-8000-12|100.00%|100.00%|win +50.00%|齐全|
|R04|Named-6000-8|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R04|Named-6000-12|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R04|Named-8000-8|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R04|Named-8000-12|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R04|Score-6000-8|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R04|Score-8000-12|50.00%|0.00%|tie +0.00%|R04.S01 upstream_missing；R04.S02 context_selection|
|R05|Named-6000-8|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R05|Named-6000-12|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R05|Named-8000-8|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R05|Named-8000-12|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R05|Score-6000-8|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R05|Score-8000-12|50.00%|0.00%|tie +0.00%|R05.S01 upstream_missing；R05.S02 context_selection|
|R06|Named-6000-8|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Named-6000-12|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Named-8000-8|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Named-8000-12|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Score-6000-8|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R06|Score-8000-12|0.00%|0.00%|tie +0.00%|R06.S01 upstream_missing；R06.S02 upstream_missing|
|R07|Named-6000-8|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R07|Named-6000-12|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R07|Named-8000-8|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R07|Named-8000-12|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R07|Score-6000-8|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R07|Score-8000-12|50.00%|50.00%|tie +0.00%|R07.S01 upstream_missing|
|R08|Named-6000-8|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Named-6000-12|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Named-8000-8|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Named-8000-12|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Score-6000-8|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R08|Score-8000-12|0.00%|0.00%|tie +0.00%|R08.S01 upstream_missing；R08.S02 upstream_missing|
|R09|Named-6000-8|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R09|Named-6000-12|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R09|Named-8000-8|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R09|Named-8000-12|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R09|Score-6000-8|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R09|Score-8000-12|100.00%|50.00%|tie +0.00%|R09.S02 context_selection|
|R10|Named-6000-8|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R10|Named-6000-12|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R10|Named-8000-8|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R10|Named-8000-12|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R10|Score-6000-8|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R10|Score-8000-12|50.00%|50.00%|tie +0.00%|R10.S01 upstream_missing|
|R11|Named-6000-8|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R11|Named-6000-12|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R11|Named-8000-8|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R11|Named-8000-12|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R11|Score-6000-8|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R11|Score-8000-12|50.00%|0.00%|tie +0.00%|R11.S01 context_selection；R11.S02 upstream_missing|
|R12|Named-6000-8|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R12|Named-6000-12|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R12|Named-8000-8|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R12|Named-8000-12|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R12|Score-6000-8|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R12|Score-8000-12|100.00%|0.00%|tie +0.00%|R12.S01 context_selection；R12.S02 context_selection|
|R13|Named-6000-8|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R13|Named-6000-12|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R13|Named-8000-8|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R13|Named-8000-12|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R13|Score-6000-8|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R13|Score-8000-12|50.00%|0.00%|tie +0.00%|R13.S01 context_selection；R13.S02 upstream_missing|
|R14|Named-6000-8|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R14|Named-6000-12|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R14|Named-8000-8|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R14|Named-8000-12|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R14|Score-6000-8|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R14|Score-8000-12|50.00%|50.00%|tie +0.00%|R14.S01 upstream_missing|
|R15|Named-6000-8|100.00%|50.00%|tie +0.00%|R15.S02 context_selection|
|R15|Named-6000-12|100.00%|50.00%|tie +0.00%|R15.S02 context_selection|
|R15|Named-8000-8|100.00%|100.00%|win +50.00%|齐全|
|R15|Named-8000-12|100.00%|100.00%|win +50.00%|齐全|
|R15|Score-6000-8|100.00%|50.00%|tie +0.00%|R15.S02 context_selection|
|R15|Score-8000-12|100.00%|100.00%|win +50.00%|齐全|
|R16|Named-6000-8|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R16|Named-6000-12|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R16|Named-8000-8|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R16|Named-8000-12|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R16|Score-6000-8|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R16|Score-8000-12|100.00%|50.00%|tie +0.00%|R16.S01 context_selection|
|R17|Named-6000-8|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R17|Named-6000-12|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R17|Named-8000-8|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R17|Named-8000-12|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R17|Score-6000-8|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R17|Score-8000-12|50.00%|50.00%|tie +0.00%|R17.S01 upstream_missing|
|R18|Named-6000-8|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Named-6000-12|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Named-8000-8|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Named-8000-12|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Score-6000-8|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R18|Score-8000-12|0.00%|0.00%|tie +0.00%|R18.S01 upstream_missing；R18.S02 upstream_missing|
|R19|Named-6000-8|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R19|Named-6000-12|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R19|Named-8000-8|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R19|Named-8000-12|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R19|Score-6000-8|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R19|Score-8000-12|100.00%|50.00%|tie +0.00%|R19.S01 context_selection|
|R20|Named-6000-8|50.00%|50.00%|tie +0.00%|R20.S01 upstream_missing|
|R20|Named-6000-12|50.00%|50.00%|tie +0.00%|R20.S01 upstream_missing|
|R20|Named-8000-8|50.00%|50.00%|tie +0.00%|R20.S01 upstream_missing|
|R20|Named-8000-12|50.00%|50.00%|tie +0.00%|R20.S01 upstream_missing|
|R20|Score-6000-8|50.00%|0.00%|loss -50.00%|R20.S01 upstream_missing；R20.S02 context_selection|
|R20|Score-8000-12|50.00%|50.00%|tie +0.00%|R20.S01 upstream_missing|
|R21|Named-6000-8|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Named-6000-12|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Named-8000-8|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Named-8000-12|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Score-6000-8|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R21|Score-8000-12|0.00%|0.00%|tie +0.00%|R21.S01 upstream_missing；R21.S02 upstream_missing|
|R22|Named-6000-8|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R22|Named-6000-12|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R22|Named-8000-8|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R22|Named-8000-12|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R22|Score-6000-8|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R22|Score-8000-12|50.00%|50.00%|tie +0.00%|R22.S01 upstream_missing|
|R23|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|R23|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|R23|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|R23|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|R23|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|R23|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|R24|Named-6000-8|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|R24|Named-6000-12|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|R24|Named-8000-8|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|R24|Named-8000-12|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|R24|Score-6000-8|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|R24|Score-8000-12|33.33%|0.00%|tie +0.00%|R24.S01 upstream_missing；R24.S02 upstream_missing；R24.S03 reranker_threshold|
|N01|Named-6000-8|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Named-6000-12|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Named-8000-8|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Named-8000-12|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Score-6000-8|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N01|Score-8000-12|0.00%|0.00%|tie +0.00%|N01.S01 upstream_missing；N01.S02 upstream_missing|
|N02|Named-6000-8|100.00%|0.00%|tie +0.00%|N02.S01 context_selection|
|N02|Named-6000-12|100.00%|0.00%|tie +0.00%|N02.S01 context_selection|
|N02|Named-8000-8|100.00%|100.00%|win +100.00%|齐全|
|N02|Named-8000-12|100.00%|100.00%|win +100.00%|齐全|
|N02|Score-6000-8|100.00%|0.00%|tie +0.00%|N02.S01 context_selection|
|N02|Score-8000-12|100.00%|100.00%|win +100.00%|齐全|
|N03|Named-6000-8|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N03|Named-6000-12|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N03|Named-8000-8|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N03|Named-8000-12|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N03|Score-6000-8|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N03|Score-8000-12|50.00%|0.00%|tie +0.00%|N03.S01 context_selection；N03.S02 upstream_missing|
|N04|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N04|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|N04|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|N04|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|N04|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N04|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|N05|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N05|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|N05|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|N05|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|N05|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N05|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|N06|Named-6000-8|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N06|Named-6000-12|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N06|Named-8000-8|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N06|Named-8000-12|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N06|Score-6000-8|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N06|Score-8000-12|0.00%|0.00%|tie +0.00%|N06.S01 upstream_missing|
|N07|Named-6000-8|100.00%|0.00%|tie +0.00%|N07.S01 context_selection|
|N07|Named-6000-12|100.00%|0.00%|tie +0.00%|N07.S01 context_selection|
|N07|Named-8000-8|100.00%|100.00%|win +100.00%|齐全|
|N07|Named-8000-12|100.00%|100.00%|win +100.00%|齐全|
|N07|Score-6000-8|100.00%|0.00%|tie +0.00%|N07.S01 context_selection|
|N07|Score-8000-12|100.00%|100.00%|win +100.00%|齐全|
|N08|Named-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N08|Named-6000-12|100.00%|100.00%|tie +0.00%|齐全|
|N08|Named-8000-8|100.00%|100.00%|tie +0.00%|齐全|
|N08|Named-8000-12|100.00%|100.00%|tie +0.00%|齐全|
|N08|Score-6000-8|100.00%|100.00%|tie +0.00%|齐全|
|N08|Score-8000-12|100.00%|100.00%|tie +0.00%|齐全|
