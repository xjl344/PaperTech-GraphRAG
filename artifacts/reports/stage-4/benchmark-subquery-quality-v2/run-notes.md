# 本地模型子查询拆分：实测说明

执行版本：`benchmark-subquery-quality-v2`。运行 ID：`6a14f53faa46423bb578a6854ff7350c`。

固定 24 道已曝光跨论文开发题，与现有规则版配对；没有运行检索、Embedding、重排或问题回答。只给本地模型原问题和题面点名的方法名；参考答案、必要来源和原文仅在 Dataset reference outputs 展示，未输入模型。

模型是本机 Ollama 中已有的 `qwen2.5:14b`，Q4_K_M，digest 为 `7cdf5a0187d5c58cc5d369b255592f7841d1c4696d45a8c8a9489440385b22f6`。temperature=0、seed=42、num_ctx=8192、num_predict=2200；一次输出，没有自动修复或重试。

硬件为 RTX 3060 Laptop 6GB。14B 模型不能完全装入显存，Ollama 报告驻留显存约 4.2GB，其余计算涉及 CPU。原生耗时分别记录 load/prompt_eval/eval duration，墙钟统计包含模型加载；同机已有模型/系统负载与首题加载会影响结果，不将本次时延外推其他部署。

规则版：24 条结果、41 条子查询，其中 11 题回退方法名、9 题保留从句、4 题不拆。模型版：24 条结果，其中 4 题无锚点而跳过，20 次实际模型调用。8/20 通过严格来源/字段一致性校验，12/20 被拒绝。拒绝时保留完整的结构化模型输出，子查询集合为空，没有偷偷回退、补词、重写标签或重新请求模型。

首个拒绝原因分别为：非原题连续片段 2 题、shared_only 与非空局部描述冲突 7 题、共享内容含方法或悬空指代 2 题、局部与共享重叠 1 题。此处按首个错误计数，并非穷尽所有问题。部分失败是抽取协议不兼容或自报字段错误，不意味着模型完全没有理解任务。

Token 为 Ollama 原生计数：输入 9,939，输出 2,942。20 次请求累计墙钟 635.55 秒，平均 31.78 秒，含加载 19.82 秒；未发生输出预算截断。没有为了补 LangSmith 数据再运行模型。

语义审阅按冻结 rubric 检查方法归属、任务保留和未解析信息。审阅者为 Codex，非独立人工，不读金标推定方法归属。严格实际可用输出相对规则版：5 胜、6 平、13 负；其中 4 个平为无锚点保持原题。胜也包含仅增加部分主题的信息，不代表完整子查询合格；明确列为可用改善的只有 R08、R12、R17。R21 的列表归属仍需复核，不记优势。

结论边界：此结果仅评价当前“模型选择原文片段＋字段约束＋程序拼接”方案，不能证明所有大模型拆分方式无效，也不能证明检索效果变化。本轮不进入 C1/C2。

后续设计建议（尚未执行）：规则先保留可靠的明确从句；模型只处理规则回退题；程序预切题面从句并编号，由模型选择编号及归属，降低逐字抄写失败；将可从非空局部描述推导的 assignment 字段移出模型硬约束，但继续拒绝无来源技术词和无依据方法配对。另测这套更简单协议后，才考虑候选覆盖实验。

执行：`.\.venv\Scripts\python.exe -X utf8 scripts/eval-stage4.py --benchmark benchmark-subquery-quality-v2`。会新建模型运行，旧版代码变动会被哈希门禁拒绝；已有结果只需补传，不重跑。

只重新生成报告：`.\.venv\Scripts\python.exe -X utf8 scripts/report-subquery-quality.py --run-summary artifacts/reports/stage-4/benchmark-subquery-quality-v2/runs/6a14f53faa46423bb578a6854ff7350c/summary.json`。

只核对本地与远端：`.\.venv\Scripts\python.exe -X utf8 scripts/verify-subquery-quality.py --run-summary artifacts/reports/stage-4/benchmark-subquery-quality-v2/runs/6a14f53faa46423bb578a6854ff7350c/summary.json --remote`。

代码入口为 `src/papertech/subquery_diagnostic.py`；正式 CLI 和 Dataset 工厂分别在 `scripts/eval-stage4.py`、`src/papertech/evaluation_details.py` 注册。本次不修改 workflow 的检索调用路径。实际运行模块与入口快照位于对应 eval 版本的 runtime-snapshot 中；v1 为已保留的中断开发记录。
