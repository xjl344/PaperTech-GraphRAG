# 修改与运行说明

新增`src/papertech/rerank_window_diagnostic.py`，实现四题固定候选的整块/窗口诊断、冻结协议、Dataset与Experiment、详细页面。新增`scripts/audit-rerank-inputs.py`审计所有已保存通道的融合结果及真实tokenizer输入；新增`scripts/verify-rerank-window.py`独立核查结果与远端记录；新增`tests/test_rerank_window_diagnostic.py`验证窗口评分对所有候选一致且只接受问题和原文。`scripts/eval-stage4.py`注册新版本入口；`src/papertech/evaluation_details.py`注册补传。没有修改生产候选召回、RRF、重排模型、原文预算或图谱。

版本`benchmark-rerank-window-v1`，冻结SHA-256：`b3890a8864ad2f2ea33457632b880cbcbfebb40085ff9a7dfcf17aa381282b73`。已完成实际运行，不需为查看结果重跑。正式入口如下，会创建新一轮重排记录：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-rerank-window-v1
```

仅补传本次已保存结果：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-rerank-window-v1 --run-summary artifacts/reports/stage-4/benchmark-rerank-window-v1/runs/61acdf61e04848468cf1a387cb03e1b9/summary.json --upload
```

仅独立核查本次结果，不运行模型：

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/verify-rerank-window.py artifacts/reports/stage-4/benchmark-rerank-window-v1/runs/61acdf61e04848468cf1a387cb03e1b9
```

当前Windows环境直接传脚本路径曾触发解释器定位错误，本次实际通过相同venv的stdin＋runpy执行，示例为：

```powershell
@'
import runpy, sys
sys.argv=['scripts/eval-stage4.py','--benchmark','benchmark-rerank-window-v1']
runpy.run_path('scripts/eval-stage4.py',run_name='__main__')
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

真实分词审计使用重排器自己的推理环境与本地tokenizer，未下载模型。原文窗口与输入长度审计位于冻结协议和报告；PDF、向量、密钥与供应商响应未上传。

两个新增重排输入测试和9个Dataset详情回归测试通过；独立核查确认8条结果、4个Example、72项数值反馈、663个原文输入窗口、18个Trace span，整块139个分数完全复现。两组不进行答案生成，Token仅记录本地重排输入长度与处理量，不冒充供应商计费或答案Token。
