# 三个失败片段的诊断、定向重试与实时追踪

日期：2026-11-14。仅处理原运行 `2ec77731331a4875ac6ed256bfebdc62` 的三个失败片段，其余片段未重新推理。新运行保留了原始任务、审核快照与旧 Trace，未把旧失败直接改成成功。

## 实际结果

| 片段 | 本次观察 | 最终结果 |
|---|---|---|
| ToG-2 第6页，`chunk_16f86a00cebdf5e10d83c3a540fbc7f7` | 首次返回 HTTP 500，用量未知；单独再试得到 1200 Token、`done_reason=length`，提高到2400后输出1510 Token、`stop` | 抽取完成，6条候选程序校验通过；逐条AI委托审核后全部批准入图 |
| ToG-2 第16页，`chunk_031b7aaba8f20d011a94bb6a15b0f3b1` | 原1200额度下输出994 Token、`stop` | 抽取完成；7条候选的引句不符合逐字匹配，被程序拒绝 |
| ToG 第5页，`chunk_deb9eea46e529705dffdd1103729c44c` | 1200 Token、`done_reason=length`；提高到2400后输出1421 Token、`stop` | 抽取完成；8条候选把 Dataset 当主体、Method 当客体，违反关系方向，被程序拒绝 |

两个片段在新运行中有直接证据确认输出上限触发。第二个片段未复现原错误。旧日志只记录了 `ValueError`，不能把新观察当成旧运行三个错误的已确认根因。新运行第一次 HTTP 500 已记录状态和堆栈位置，当时还没有保留服务错误正文，具体原因仍未知；后续代码已增加安全服务错误摘要记录，没有把500推断为输出触顶。

最终三个片段均成功处理。新增6条审核结果和理由见 [review-results.json](review-results.json)，候选及完整来源上下文见 [review-snapshot.json](review-snapshot.json)。新增关系仍保留模型原始端点（包含数据集来源括注），尚未全面做别名对齐。审核身份为 `Codex / ai_delegated / evidence-review-v1`，不冒充独立人工专家验证。

当前审核总数411条：批准89、拒绝322、待审核0。新6条关系的 Neo4j 来源校验与重复写入检查见 [review-verification.json](review-verification.json)。原始669个成功片段加本次恢复的3个片段覆盖672个抽取目标；覆盖率不等于关系召回率，也不保证每篇论文有可信语义边。

## Token 与诊断

本次共6次实际请求，其中5次有用量：已知输入3564、输出6325 Token，包含两次被截断的失败生成；1次HTTP 500用量未知，不能按零理解。不换算金额，不把原运行的缓存计数或旧历史Trace相加。完整元数据及逐次尝试见 [summary.json](summary.json)。

`data/kg.sqlite3` 新增 `kg_attempts`：每次尝试独立保存开始/结束、HTTP状态、错误分类、异常类型、堆栈位置、JSON错误位置、停止原因、额度、各类耗时与Token。模型原始输出只保存在本地 `diagnostic_json`，写入时过滤已配置密钥。对任意HTTP错误不自动重试；只有收到 `done_reason=length` 或输出Token达到额度时，才从1200提高至2400、最多4800，最多3次。此次没有用到4800。

任务汇总的Token是最终结果对应的一次调用；`attempt_totals` 和本报告的Token是所有尝试的已知小计，包含失败生成。HTTP 500属于未知用量，原任务与失败记录保留。

## 官方实时追踪

后续抽取、审核、入图确认、问答节点和供应商调用默认在开始与结束时同步提交 LangSmith 运行元数据。开始事件发送后才进入推理；结束时更新终态与原生Token。当前格式为 `papertech-live-v1`，`capture_mode=live`。本地持久事件队列在 `data/live-traces.sqlite3`；网络/鉴权错误时保留待上传事件，后续操作自动尝试补传，或使用下面的 `--flush` 命令。断网时不能保证实时可见。

只上传标识、状态、模型/版本、额度、耗时、停止原因、错误分类、审核决定与Token；不上传PDF、片段正文、引句、向量、原始模型输出或密钥。运行级实时追踪不等于逐Token流式传输或GPU/CPU/内存监测。图写入的事件命名为“确认”，它的耗时不代表Neo4j完整写入耗时。

三片段重试的首轮5个Span：
[官方Trace](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/d759f5e7-0053-4ad5-a572-3669c2c5fa8f?poll=true)。首轮接入时发现SDK要求结束时间为datetime对象，部分事件临时排队；修复后已经补发并逐条核验，不能把排队期间的事件宣称为当时已实时可见。

第一个片段的单独重试3个Span：
[官方Trace](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/83834964-09e4-4f9c-b616-58dfc93a0988?poll=true)。已在任务仍运行时远端核验根任务与第二次尝试处于运行中；最终结束状态、5次有用量调用的原生Token均核对一致。

新增6条审核和6条入图确认共12个Span均远端核验，真实URL见 [review-live-verification.json](review-live-verification.json)。两次抽取运行8个Span加这12个，共20个记录；不与旧版历史补传Trace混算。

## 修改与复查

修改：`src/papertech/kg.py`、`audit.py`、`providers.py`、`workflow.py` 和 `scripts/stage3.py`；新增 `src/papertech/live_traces.py`、`scripts/verify-live-traces.py`。`scripts/report-extraction-retry.py` 和 `scripts/review-retry.py`用于本次证据导出和明确的六项审核决定。对应回归在 `tests/test_kg.py`、`tests/test_live_traces.py`，使用说明更新在 `README.md`。没有修改`.env`、源PDF或网页。

```powershell
# 本次项目虚拟环境启动器存在基础解释器访问问题，使用已有解释器加载项目依赖
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\stage3-live-pycache'
$taskPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'

# 后续仅重试某次运行的失败片段；已恢复的本次任务无需重复调用
& $taskPython -X utf8 scripts/stage3.py extract --retry-failed <run_id>

# 恢复待上传事件并远端核对本次最终运行
& $taskPython -X utf8 scripts/verify-live-traces.py --flush --run-id 36c03f4aa7c94e85812a998982a09145

# 仅核验六条已批准关系；不改写审核决定和时间
& $taskPython -X utf8 scripts/review-retry.py --verify-only

& $taskPython -X utf8 -m unittest discover -s tests -v
```

48项回归通过，包含截断升级、非截断错误不重试、500诊断、失败Token保留、未审核不入图、实时开始先于工作、SDK时间类型和断网有序补传。测试记录见 [live-tests.txt](../live-tests.txt)。首次全量测试出现一次旧解析测试的Windows文件替换拒绝访问，单项复查和随后全量检查均通过。新增/修改Python文件编译通过。没有开始阶段4评测。
