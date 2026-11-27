# v1 中断说明

本轮任务为本地模型对子查询拆分的探索性开发诊断，不运行检索、Embedding、重排或回答生成。

v1 run：`3f4af1fe8c1c4b0c83859f6712005249`。已完成 Rule 5 条、Local-LLM 4 条；R05 的模型请求被取消，没有完成输出和 Token 计数。不将这份不完整结果用作 24 题指标。

R01 将方法专属描述放入两个方法的共享任务，并重复放入自己的局部描述；R02 丢失任务信息，仅留下带“它们”的问题。决定停止继续调用，保留所有已完成结果。没有依据金标调整提示词。

随后建立 `benchmark-subquery-quality-v2`，固定新的提示词和校验规则再运行完整 24 题。v1 不覆盖，继续允许通过 sync-evaluation-dataset.py 补传历史结果。

注意：PowerShell 管道输入进程被 Ctrl-C 终止时，没有执行 Python finally；因此依据已保存记录与已观察到的停止原因，将遗留 running 状态修正为 interrupted。此修正未改变任何模型输出或评分。

上传重试时修正了 LangSmith LLM 子 Span 所需的 dotted_order；只上传原结果，无模型重放。v1 Dataset 24 Examples 已核对，Rule 5 条和 Local-LLM 4 条及对应机械反馈均已核对。
