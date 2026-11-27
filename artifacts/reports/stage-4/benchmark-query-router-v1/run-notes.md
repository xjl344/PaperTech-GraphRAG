# 通用问题分流诊断

实测已完成：模型拟选择 llm 19 题、rule 5 题，其中 llm 2 题因引文校验失败回退；实际为 llm 17、rule 5、fallback 2，共57条补充子查询。24次原生模型调用，输入Token 9,334，输出Token 3,364；累计墙钟789.79秒，平均32.91秒/题，中位32.06秒。加载25.42秒、提示计算24.64秒、输出计算738.02秒；24题均正常stop，无输出截断。46项相关单测通过。

Codex题面审阅：路由21题合理、2题可商榷、1题不合理；18题的补充查询总体可用但多题存在缺项或仍复合，6题需要修正或拒绝使用（R02、R05、R06、R09、R11、R19）。这不是18/24的检索准确率，也不是独立人工路由正确率。具体审阅见运行目录review-notes.json和quality-review.md。

关键失败：R19误把LLM当主语，规则候选遗漏G-Retriever且被模型错误接受；R06接受遗漏后半句目标的规则候选；R05拆分过细并偏离方法比较；R09漏改引号、R11删空格使题面引文逐字校验失败；R02的技术项归属依赖列表顺序，需要明确依据。代码未针对这些题号增加分支。

本轮为保持原题基线与通用分流器的配对文本诊断，不能与上一轮8/20机械通过率直接作同口径提升比较：协议、问题覆盖和子查询生成方式均有变化，也没有测实际召回。

本轮用24道既有跨论文开发题测试通用问题分流器，版本 `benchmark-query-router-v1`，run `6181b95b9e3545f58ab4ceaa8c1789d9`。冻结完成并回读核对 LangSmith Dataset 24 Examples 后才调用模型。原题和参考来源未修改，参考答案仅保存在 Dataset reference outputs。

运行时模型只收到 `question` 与 `rule_candidate`。不传题号、参考答案、图谱、论文原文、方法别名目录或上一轮审阅信息。问题复杂度按“多个独立可查证的证据目标、是否需指代和跨句归属理解”判断，不按问题长度或名称数量设阈值。

四种模型决策：`no_split` 保持原题；`rule` 使用通用语法产生的规则候选；`llm` 生成2至4个补充查询；`unclear` 无法安全拆分而保持原题。额外 `fallback` 表示输出校验失败，不能与模型主动判断不拆混淆。所有路径都保留原问题，未运行实际检索。

代码只有一条窄语法规则：多个英文命名主语直接通过“的”修饰各自主题，再跟明确的并行问句。无论文名称清单和题号分支，不尝试按关键词背出论文关系。规则只提出候选，模型仍需判断它是否足够。该规则也可能误识别嵌套名词，如把 R19 中 LLM 当成主语；本轮将观察模型是否拒绝错误规则候选，不在运行中按题修补。

本轮放宽了上一轮过于复杂的局部/共享字段协议：子查询允许自然改写，另提供题面连续原文作为判断依据。程序只检查JSON结构、合法路由、规则候选存在性、子查询数、引文存在性、重复查询，以及新增英文术语。中文新事实、技术归属和目标完整性需另做语义审阅；格式通过不计作语义正确。

两组 Experiment 的技术标签沿用现有上传接口：`Rule` 实际为原问题保持基线（零模型调用）；`Local-LLM` 实际为通用分流流程，内部可以选择规则、模型或不拆。它不是“纯规则拆分 vs 纯模型拆分”对照。

分流也由模型判断，因此每题均有一次本地模型调用；选择 rule 或 no_split 并不意味着没有模型成本。模型是已有 Ollama `qwen2.5:14b`，Q4_K_M；temperature=0、seed=42、num_ctx=8192、num_predict=1400。同一次响应完成路由和必要的拆分，不二次询问，不自动修复和重试。模型不能全部装入本机RTX3060 Laptop 6GB显存，时延包括CPU参与与加载。

这24道题全部是跨论文题，且此前已经用于开发。可以检查通用分流流程在复杂题上的行为、语义错误和描述性拆分，但不能估算它对简单题的误拆率，也不能把结果当作独立泛化验收。若大多数题选择llm，不能仅凭分布判断分类器无效或有效。

逐题语义审阅来源为Codex，明确不是独立人工评分。`route_quality`与`query_quality`分开判断；模型路线合理但查询漏项可分别记录。不会为了评估拆分而读取参考答案、再把论文知识补回题面。

文件：`src/papertech/query_router_diagnostic.py`（通用语法、模型提示、校验与运行）；`scripts/eval-stage4.py`（正式入口注册）；`src/papertech/evaluation_details.py`（Dataset注册）；复用已有上传器记录Experiment及原生Token子Trace。未修改workflow检索路径。

执行新运行：`.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-query-router-v1`。

只补传：`.\.venv\Scripts\python.exe -X utf8 scripts/sync-evaluation-dataset.py --benchmark benchmark-query-router-v1 --run-summary artifacts/reports/stage-4/benchmark-query-router-v1/runs/6181b95b9e3545f58ab4ceaa8c1789d9/summary.json --upload --answer-mode full`。

重建报告：`.\.venv\Scripts\python.exe -X utf8 scripts/report-query-router.py --run-summary artifacts/reports/stage-4/benchmark-query-router-v1/runs/6181b95b9e3545f58ab4ceaa8c1789d9/summary.json`。

本地与远端核对：`.\.venv\Scripts\python.exe -X utf8 scripts/verify-query-router.py --run-summary artifacts/reports/stage-4/benchmark-query-router-v1/runs/6181b95b9e3545f58ab4ceaa8c1789d9/summary.json --remote`。
