# 阶段 1：14 篇论文证据底座验收

- 日期：2026-11-13；执行人：Codex。原文核查由程序及 Codex 查看定位图完成，未声称额外人工复审。
- 语料版本：`pilot-v1`；解析版本：`pdf-v1.1`；环境：Windows / Python 3.14.6 / PyMuPDF 2.1。
- 结论：阶段 1 功能与可追溯性验收通过；章节标签按启发式降级交付。
- 模型、Prompt、图 Schema、检索索引、问答评测集：本阶段均未使用。

## 结果

| 指标 | 结果 |
|---|---:|
| 已处理论文 | 14 |
| 页面 | 307 |
| 当前版本片段 | 980 |
| 跨页片段 | 250 |
| 参考文献/边界后保护区片段 | 308 |
| 终态为结构降级的文档 | 14 |
| 解析失败 / 未完成 | 0 / 0 |
| 独立重新读取核对的源页 | 全部 307 页 |
| 自动核对原文范围的片段 | 全部 980 个 |
| 保存的定位样例 | 37 个，覆盖全部 14 篇 |
| 合成 PDF 回归测试 | 11 项通过，0 失败 |

每块估算 Token 不超过 500；章节边界会产生较短块，因此不将“目标约 500”解释成所有块固定长度。完整逐篇结果、配置与警告见 `verification.json`。当前解析器实现哈希记录在其中，代码变化将产生新的 Parse ID。

| 论文编号 | 页数 | 片段数 | 参考文献保护区片段 | 跨页片段 |
|---|---:|---:|---:|---:|
| Methods-015 | 25 | 74 | 6 | 23 |
| Methods-018 | 18 | 57 | 19 | 17 |
| Methods-024 | 23 | 61 | 31 | 14 |
| Methods-035 | 31 | 96 | 50 | 27 |
| Methods-059 | 13 | 37 | 15 | 9 |
| Methods-112 | 23 | 67 | 39 | 21 |
| Methods-181 | 11 | 32 | 4 | 7 |
| Methods-191 | 24 | 77 | 12 | 23 |
| Methods-209 | 22 | 73 | 11 | 11 |
| Methods-211 | 18 | 62 | 28 | 14 |
| Methods-215 | 31 | 88 | 19 | 27 |
| Methods-229 | 15 | 49 | 16 | 12 |
| Surveys-010 | 28 | 136 | 46 | 25 |
| Resources-002 | 25 | 71 | 12 | 20 |

## 标识与数据流

冻结清单 → 源文件哈希校验 → SQLite 提交 pending/running 任务 → 独立子进程提取 → 稳定分块与原文校验 → 提交文件与 SQLite 终态 → 独立重读源页验收。

- Paper ID 包含相对路径语义和源 SHA-256，不仅依赖文件名。
- Parse ID 还包含处理配置、解析代码 SHA-256 和 PyMuPDF 版本。同一论文的不同处理结果保留各自版本。
- Chunk ID 绑定 Paper/Parse、文本哈希和完整来源范围。跨页块保存各页的字符范围和相应块坐标。
- 页码是 PDF 物理页号（从 1 开始）；字符范围基于该解析版本页面文本，左闭右开。坐标是 PDF 文本块框，不等同于字符级框。

逐篇结果位于 `data/extracted/<paper_id>/<parse_id>/document.json`。任务状态、页数、片段数、耗时、源前后哈希、警告和错误保存于 `data/ingest.sqlite3`，每次运行另有 `artifacts/logs/ingest/<run_id>/summary.json` 与 `failure-queue.json`。

状态先提交再执行子进程。单篇超时预算为 60 秒，页数上限 200，每页上限 200,000 字符，不做 OCR、不自动重试。单篇失败写明原因后继续其他论文。OS 文件锁阻止同项目并发导入；进程异常退出后，未终结任务在下一次运行恢复为 interrupted，保留以前的终态。

## 可重复性与版本历史

修复版本完成了首次解析、强制重解析和缓存复用三次运行：

| 运行 | Run ID | 当前结果 |
|---|---|---|
| 首次 pdf-v1.1 | `20261113T192311-e5d33c3c8c` | 14 篇结构降级；980 块 |
| 完整重解析 | `20261113T192527-d1b2e2f953` | 内容逐字节相同；标识、数量不变 |
| 缓存复用 | `20261113T192710-2c8d194e6b` | 14 篇均 reused；980 块 |

当前版本的全部源哈希在处理前后及独立核查时一致。V06 的语义包括缓存复用及真正重解析，不以只命中缓存代替实际重跑验证。

数据库保留 14 个 Paper、28 个 Parse 和 1,973 个历史 Chunk。这包括初始 `pdf-v1` 的 993 块和修复后 `pdf-v1.1` 的 980 块，并非同版本重复增长。后续阶段只读取 `current-parses.json` 列出的 14 个已验证结果，不能索引全部历史块。

## 故障与修复记录

1. 初始参考文献策略允许“2021. …”或表格中的 Method 重新打开正文范围。复核实际论文发现后改为：References 区域持续保护，只有显式附录/补充材料边界才恢复可抽取范围；排除四位年份标题，增加独立分行附录检测。修复版本为 `pdf-v1.1`，原 `pdf-v1` 保留为开发历史，不进入当前白名单。回归测试覆盖了年份、通用标签和附录恢复。
2. 首轮测试中 SQLite 的事务上下文没有显式关闭测试连接，导致 Windows 清理临时文件时出现 WinError 32。测试连接改为 `contextlib.closing` 后复验通过；正式导入连接本身已显式关闭。
3. PowerShell 嵌套子进程在沙箱中无法访问实际存在的 C 盘基础解释器。经工具授权，使用已批准的本地运行入口完成测试。生产命令没有修改基础解释器或永久 ExecutionPolicy。
4. unittest 默认 stderr 输出在 PowerShell 重定向时被包装为 NativeCommandError。测试入口改为显式保存结果并输出到 stdout，命令退出码与实际测试结果一致。

真实子进程故障测试在隔离目录中先处理损坏 PDF，再处理正常 PDF：前者进入失败队列，后者成功完成降级解析。重复处理相同批次时，损坏项仍有明确失败，正常项复用，Paper/Parse/Chunk 数量均不增长。证据保存在 `failure-isolation-test.json`；没有损坏真实论文。空文本、短文本分别返回 empty_text 与 text_too_short。版本变化与旧历史保留见 `version-history-test.json`，中断恢复见 `interruption-recovery-test.json`。测试文本日志和测试源哈希见 `test-results.txt`、`test-summary.json`。

## 原文核查与降级限制

`audit_document` 对全部 980 块核查文本哈希、稳定 ID、源范围和覆盖完整性；独立验证脚本再次用 PyMuPDF 读取全部 307 页，并核对 SQLite 与文件结果一致。`location-samples.json` 记录 37 个示例，包含正文、跨页和参考文献片段；定位图覆盖每篇至少一页。已查看 `location-contact-sheet.png`，图中橙色框对应样例覆盖的原文文本块；没有将 14 页视觉抽查说成对所有页面布局的人工验收。

章节标签均由规则推测，故 14 篇都以 degraded 终结，警告为 section_boundaries_heuristic。Methods-211 的 PDF 第 4 页另有一个文本块无法映射到页面文本流，保留 block_geometry_unmapped:4 警告；该页文本和片段字符范围仍通过精确核对，不声称所有字符都有坐标。

参考文献保护采用保守策略：未识别出的附录也可能被保留在 references 保护区中，造成后续关系抽取材料减少；不会为扩大抽取范围而解除不确定保护。找不到参考文献起点时，全篇片段默认不进入方法关系抽取。边界仍需在建图阶段按原文复核。

页眉、页脚、脚注、图内文字可能进入文本流；公式和表格没有结构化恢复。片段长度采用明确记录的估算方法，没有下载模型分词器。字符回查准确不代表章节分类、语义关系或答案质量已验证。

## 验收与运行

V01 使用恢复后盘点证据，V02 使用冻结选材证据，V03—V07 依据本阶段哈希、状态、定位、重跑与故障注入记录通过。降级状态和限制完整保留。这里的通过仅针对阶段 1 数据底座，不包含检索效果、回答正确率或 GraphRAG 收益。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ingest
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task ingest -ForceReparse
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task verify
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1 -Task test
```

阶段 1 本地运行，无云端调用或论文外发。详细代码入口和输出目录见项目根目录 `README.md`。阶段 1 已完成，阶段 2 的 Neo4j、Embedding、问答与外部调用治理尚未开始。
