# R11 分流修复后的定向召回

基于 `benchmark-query-router-fix-v1` 离线重放，只重新召回 R11 的四条修复后子查询。原问题 Q0 和全部其他题目复用既有候选；无 rerank、无证据选择、无答案生成。R11 新子查询一次批量 embedding，调用兼容门禁通过的同一 BGE-M3，再分别执行生产全文20和向量20查询。

## 结果

- 路由差异只有 R11：`fallback` → `llm`，4条子查询；其他23题查询计划完全相同。
- R11 候选数从原来的31增加到90，新增4条检索查询。
- R11 必要来源仍为1/2：S01命中并保留，S02在四条子查询的全文Top20与向量Top20中仍未命中。
- 原问题和子查询扩展后的 R11 来源覆盖率均为50%；该分流校验 bug 修复没有带来 S02 的召回改善。
- 新增4条子查询 embedding 共一次批量调用，约1.82秒；供应商未报告Token。没有重新调用分流模型。

LangSmith 已验证24个 Example、Original/Expanded 各24条实验结果。其余23题为原结果回放上下文，不是本轮重新测量。

完整结果：同目录下 `route-and-recall-diff.json`、`summary.json`、`comparison.json`、`index.html`；LangSmith 链接见 `langsmith-status.json`。

运行主体：

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-subquery-recall-router-fix-v1
```

若只需补传已完成结果（不重新 embedding 或召回）：

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/sync-router-fix-recall.py <已有summary.json>
```
