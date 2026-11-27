# 阶段 3 在线 GraphRAG 闭环验收

2026-11-14，执行及委托复核：Codex。范围为 14 篇试点的在线功能收尾；没有启动阶段 4 正式 Hybrid 对照，没有扩量。

当前链路已真实运行：Cloudflare BGE-M3 问题向量 → Neo4j 全文/Dense → 实体锚定与受限两跳图扩展 → 本地 GPU FP16 重排 → 证据和路径组装 → 已配置平台的 DeepSeek → 来源引用校验。运行开始/结束与已知 Token 实时提交 LangSmith，并远端回读确认。

## 功能与数据检查

- 冻结语料 `pilot-v1`，当前 corpus `a6a19e2e97b11d9c450e`；14 篇、980 块，源 PDF 与解析产物哈希复查通过。
- 672 个抽取目标均已处理；411 候选中批准 89、拒绝 322、待审核 0。批准并不代表关系召回完整或每篇都有语义边。
- Neo4j 当前语义边：`EVALUATED_ON=59`、`ADDRESSES=28`、`COMPARES_WITH=1`、`IMPROVES_UPON=1`；没有接纳 `PROPOSES`。89 条 Claim 的 Chunk、Paper、页码、解析身份及逐字来源复查错误 0；旧阶段的重复写入证据保留。本轮在线查询没有改写这些关系。
- ToG/Think-on-Graph、ToG-2/Think-on-Graph 2.0 两组查询别名有第 1 页原文依据，且不会把 ToG-2 或 ToG-R 当作 ToG。别名只用于锚定，不合并原始实体；其他实体仍精确匹配，未声称完成全面消歧。
- 图扩展最多两跳、40 个种子、每层 40 个节点、每节点采纳最多 8 条邻边、最多 40 路径、10 秒数据库查询期限。多取一条邻边仅用于检测截断；服务器仍可能扫描/排序更多邻边，不能把返回上限说成物理扫描量上限。
- 白名单关系及 Claim/端点/来源均绑定当前 corpus 和 approved 状态。可反向遍历关系，但返回 `subject/object` 保留原始事实方向。图超时/失败保留 Hybrid 并记录降级。
- 全文/Dense 各 Top 20，三路 RRF 后最多 40 候选。最多 8 条证据，证据选项和实际送入的图路径共用 6000 UTF-8 字节预算；问题和系统指令不在该预算内，实际输入 Token 仍以供应商 Usage 为准。
- 只将来源引句确实出现在本次生成原文中的图路径传给模型，最多 4 条。比较题先保留已识别双方论文各一条高排证据，缺方标 partial；当前通用多方法比较及自动冲突裁决未实现。

完整机器复查见 [verification.json](verification.json)，测试见 [online-tests.txt](../online-tests.txt)。最终 72 项回归覆盖图超时、GPU/OOM 不转 CPU、NaN 拒用、数据库断连不生成、引用越界、超时不重发、进程复用及原有解析/建图边界；故障注入是模拟，并未人为破坏真实服务。

## 真实验收样例

以下是功能验收小样，无正式金标集或质量阈值，不计算 Recall/MRR/P95，也不作 GraphRAG 优于 Hybrid 的结论。

| 样例 | 最终状态 | 全请求耗时 | GPU 热重排 | 送入生成的路径 | 上下文字节 |
|---|---|---:|---:|---:|---:|
| ToG-2 评估数据集 | ok | 15.16 s | 1.16 s | 1 | 5366 |
| ToG / ToG-2 比较 | partial | 17.18 s | 1.04 s | 1 | 4607 |
| HippoRAG / PPR | partial | 15.21 s | 1.16 s | 0 | 5973 |

全请求耗时从 `Workflow.ask` 进入到返回，包含同步 LangSmith 上传和 URL 回读，**不含已先执行的 GPU 预热**；阶段计时包含开始事件的上传等待，但不含本阶段结束事件的上传等待。这里不以单项推理速度替代用户实际等待时间。

三条最终样例及真实官方 Trace：

- [ToG-2 数据集](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/cbcac66b-6a34-485b-bc5c-b2743dde7b68?poll=true)；本地记录 [tog2-datasets.json](runs/a502daa95f8b42678435f5e209df27d8/tog2-datasets.json)。
- [ToG / ToG-2 比较](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/0f391e24-27d0-4b8e-a8cd-13e5e264c708?poll=true)；本地记录 [tog-comparison.json](runs/37d5c7a46c7b4e92a48a299010a94620/tog-comparison.json)。
- [HippoRAG / PPR](https://smith.langchain.com/o/01386dcd-db0e-4ed5-bcc3-2592e81692e2/projects/p/f755f52c-a0c2-431f-8ded-d4ebe88979de/r/a4b91e27-da11-4970-b0d1-cc91d51c88a7?poll=true)；本地记录 [hipporag.json](runs/37d5c7a46c7b4e92a48a299010a94620/hipporag.json)。

Codex 按本次证据逐段复查：

1. ToG-2 的六个数据集名可回到第 7 页；消融子集及显著性检验分别有第 16、19 页来源。未把任务类型当数据集，也未据此保证完整召回所有实验。
2. 比较题保留双方独立论文来源，最终明确指出缺少具体检索流程及一致实验条件，不能判定整体胜负。初次通过形式校验的版本仍有一句从结果表概括流程，未当作语义通过；收紧提示后定向复验不再补写该流程。现有证据仍不足以完整回答原问题，所以 partial 是有效缺口，不是完整比较能力通过。
3. HippoRAG 的 PPR 种子、KG 路径探索和段落聚合在第 2、4 页有原文支持。该题图召回有 17 条关联路径，但均未在当前生成证据/预算下取得支持，因此没有强塞进生成上下文；回答对“图路径证明力”的缺口作了说明。另有引用精细度限制：命名实体链接描述存在于同一来源片段的其他句子，模型选择的该片段引句主要覆盖段落聚合；自动校验不能判断每一句都被所选引句完整蕴含。该项留作阶段 4 引用语义核查问题。

上述复查是用户委托的 AI 功能核查，不是独立专家审核，也没有以 LLM-as-judge 计算质量得分。逐字引句存在、来源正确与句句语义支持是不同检查；当前自动校验只覆盖前两项。

## 失败诊断与修复

首轮三题都触发 citation_error：模型抄写原文时改写了 PDF 换行、空格或文本。程序按原逐字规则拒绝，未返回伪有效引用，未自动重新生成。原始输出仍在本地阶段记录，旧失败 JSON 与 Trace 保留。

修复采用 `source-choice-v1`：程序把本次原文切为连续、逐字保真的引句选项；模型输出 `chunk_id + quote_id`；程序从已提供的选项取回原文，再做请求白名单、内联引用和原文子串校验。未知编号直接拒绝，不将改写后的文字归一化为“相同”。旧式逐字 quote 输入仍严格校验，用于兼容旧报告与测试。

之后三题引用校验通过。复查发现比较题从表格推断流程及过多附加性能描述，提示进一步要求简洁、事实与所选引句相符、缺流程则说明不足，再只复验比较和 HippoRAG 两题。前后共 8 次实际问答，全部保留；没有把调试题当作独立评测样本或只报最好一轮。逐条初始引用失败分类见 `verification.json` 的 `citation_failures`。

原 0.05 重排过滤阈值未更改；真实查询能通过该门槛。该阈值尚未校准为“语义充分性”或“库外问题”分类器，不能据此宣称拒答正确率。

## GPU 与调用用量

RTX 3060 Laptop，6144 MiB；项目 GPU 环境使用 Python 3.14、PyTorch `2.13.0+cu130`、transformers `5.14.1`，从已有本地 wheel 安装，没有下载大模型或改写原 CPU 环境。

GPU 子环境通过 `--system-site-packages` 复用基础解释器中已有 transformers 等依赖，只在项目内单独安装 CUDA torch；它不是完全封闭的依赖快照。原 `.venv` 和 CPU 模型环境保留。若本机需重新建立该子环境，使用已有 wheel：

```powershell
& $taskPython -m venv --system-site-packages .runtime/gpu-reranker
& ./.runtime/gpu-reranker/Scripts/python.exe -m pip install --no-index --no-deps --cache-dir .cache/pip E:/AI-Infra/wheels/torch-2.13.0+cu130-cp314-cp314-win_amd64.whl
```

- 三次验收进程的冷预热分别为 23.59、20.72、20.39 s，包含解释器导入、模型指纹校验和加载；模型加载自身约 6 s。更早独立探针冷启动 44.59 s，记录在 [gpu-probe.json](gpu-probe.json)，不能保证每次启动固定为 20 s。
- 热重排 34—40 个实际候选约 1.04—1.35 s，batch size 1、FP16、每文本对最多 1024 Token。
- 运行时峰值 PyTorch allocated 约 1.08 GiB；这是该模型的分配量，不是完整进程或整卡占用。
- 三轮约 1 秒采样的整卡峰值分别 2821、2710、2709 MiB，包含桌面等其他进程；不是进程独占显存，也可能漏掉短峰值。原始样本在各运行的 `gpu-samples.json`。
- 此配置中查询向量在云端，所以 GPU 不需要同时加载 BGE-M3；未把 Qwen 与重排同时运行。不据此保证任意其他 GPU 负载下都能共存。
- 常驻是父进程拥有的私有 stdio 子进程，没有开放 HTTP 端口或安装 Windows 服务。父进程退出释放；新 `ask` 仍冷启动，`chat` 先预热再连续复用。超时杀 worker，不自动重放请求；GPU 错误保留召回并跳过重排。

8 次 DeepSeek 用量已知：输入 **14,524**、输出 **5,522** Token，含失败引用生成和修复后的复验；8 次 Cloudflare 均 HTTP 200 但未返回 Usage，全部记 unknown，不计为零。自动供应商重试 0。模型为用户所填兼容平台的 `deepseek-v4.1-flash-1017`，不是已验证的 DeepSeek 官方端点；thinking disabled、max_tokens 2048 和 JSON 模式已实测可用。不计算金额。

## 监测边界与待做项

三轮问答的 30 + 30 + 20 = 80 个 Span 均已远端确认结束；DeepSeek 原生输入/输出 Token 与本地调用记录相符。此计数不含 GPU 预热、早前建图/重试或历史补传，避免重复汇总。元数据包含阶段耗时、召回与证据计数、图锚定/截断、重排设备及峰值分配量；不上传正文、引句、向量或原始输出。缺网时先落本地有序队列，不能保证断网期间远端实时可见。

整卡采样曲线本轮只保存在本地；上传了重排峰值元数据，不宣称完整曲线已实时上传。CPU、系统 RAM、磁盘吞吐/温度、Prometheus/Grafana 尚无本轮完整采集，这些缺口明确保留。未添加网页代替官方监测。

完整依赖版本、当前代码哈希在 `verification.json`；当前快照不能追溯性地充当各次调试之前的完整 Prompt 冻结。阶段 4 必须重新冻结题目/金标、Prompt、模型、K、预算与评分规则，然后受控对照。当前只有两组查询别名、语义边稀疏、比较流程证据不足、引用语义精度和自动冲突判定等限制；不声称通用技术演进推理、质量提升或扩量准入通过。

## 修改和运行

主要修改：`graph_store.py`、`workflow.py`、`providers.py`、`citations.py`、`retrieval.py`、`local_models.py`、`audit.py`；新增 `entity_aliases.py`、`evidence_context.py`、`rerank_runtime.py`、`rerank_service.py` 和私有 worker。新增在线验收与只读报告脚本、边界/故障测试；同步 `.env.example`、README、Plan、Requirements、Validation 和项目宪章。`.env` 只更新非密钥 GPU 字段，保留现有凭据；没有改网页、原 PDF、原 CPU 环境或已审核关系。

```powershell
$env:PYTHONPATH = (Join-Path $PWD '.venv\Lib\site-packages') + ';' + (Join-Path $PWD 'src')
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\stage3-live-pycache'
$taskPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'

# 首次预热后连续问答，/exit 退出；按现有配置真实调用云端
& $taskPython -X utf8 scripts/stage2.py chat

# 回归与只读复查，不重新调用模型
& $taskPython -X utf8 -m unittest discover -s tests -v
& $taskPython -X utf8 scripts/report-stage3-online.py

# 需要重新执行真实小样验收时才运行，会产生新请求
& $taskPython -X utf8 scripts/verify-stage3-online.py
```

本次停在阶段 3 在线功能交付。下一大步是阶段 4：冻结小型问题与证据金标，比较 Hybrid 和 Hybrid＋Graph，正式检查召回、语义支持、引用、延迟和 Token。
