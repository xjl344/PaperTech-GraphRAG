# DeepInfra BGE-M3 接入准备

依据用户提供的OpenAI兼容接口示例接入；本次没有发送真实DeepInfra请求，云端密钥留空。

- 地址：`https://api.deepinfra.com/v1/openai`；模型：`BAAI/bge-m3`；填写项：`.env` 的 `CLOUD_BGE_API_KEY`。
- 模型请求：`POST /embeddings`、Bearer认证、字符串列表、`encoding_format=float`。按返回index排序，检查数量、1024维、有限数值及非零范数，归一化后使用。
- 供应商调用日志标为deepinfra；429遵从有界退避，结果未知的超时和HTTP500不自动重发；402持久阻止后续调用，需人工处理后显式清除阻止状态。
- CLI自动模式：未配置密钥用本地；配置后进入云端模式，兼容性未通过时只全文检索。已有UI仍使用用户选择的来源。本次未改动UI。
- 兼容性绑定本地索引模型指纹、云端地址、模型名、供应商及有效期。4条合成探针同文本余弦门槛0.999，不发送论文正文。失败/错误/中断使旧批准失效；相同维度但不同空间的模型不能混用。
- 如更换为Qwen等另一种embedding模型，须核实准确模型ID和API，再为同一模型重算论文及查询向量，使用匹配的新索引；不必重新解析PDF或重抽知识图谱。当前代码仍为BGE-M3的1024维索引，不能只替换模型名。
- Token记录保留，不估算价格。LangSmith沿用实时运行元数据；未改动DeepSeek、LangSmith或Neo4j凭据。
- GPU重排增加独立解释器、设备和FP16配置入口；默认CPU/FP32保留。显式CUDA不可用会报错并由工作流记录跳过，不静默改为CPU。没有安装CUDA依赖或启用常驻推理，不能宣称已经解决在线时延。

改动：`.env.example`、本地`.env`、`src/papertech/providers.py`、`cloud_embeddings.py`、`workflow.py`、`local_models.py`、`scripts/stage2.py`、`run.ps1`、`model-worker.py`、`tests/test_cloud_embeddings.py`、`README.md`。

运行方式见README的“DeepInfra BGE-M3查询配置”。模拟验证涵盖真实端点路径/认证请求体、返回排序与Token、错误维度、错误输入、500不重试、缺密钥不联网、同维不同空间拒绝、旧批准失效、模型指纹变化及云端异常脱敏。完整回归结果在 [deepinfra-tests.txt](deepinfra-tests.txt)；真实API、向量兼容性和GPU性能待填密钥及设备准备后核验。
