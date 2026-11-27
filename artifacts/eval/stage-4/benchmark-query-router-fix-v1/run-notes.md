# R11 quote 校验修复与离线重放

本版本不重新调用分流模型。它从 `benchmark-query-router-v1` 保存的 `parsed_output` 重放统一校验逻辑。

- 修复内容：精确 quote 先匹配；失败后去空白匹配；再失败后统一 `？?、，,、：:、（）()` 后匹配；所有成功路径均把索引映射回题面原文 `start/end`。
- 不修改 prompt。
- R11 从 `fallback` 恢复为 `llm`，保留模型原输出的4条子查询。
- 其余23题 route 和子查询与原归档结果完全一致。
- 重放记录使用上传时的当前时间戳，原始模型 Trace/时间保留在来源数据里，避免 LangSmith 拒绝超过24小时的历史 run。

离线命令：

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/replay-router-fix.py
```

证据：`benchmark.json` 内的 `replay_changes`、`route-diff.json`、本地 runs 下的 `replay-diff.json`。此次修复是通用 quote 定位，不包含对 R11 的题目特判。
