"""Unseen 18-question Holdout Generalization Evaluation (benchmark-holdout-v1).

Tests true out-of-sample generalization across all 14 papers with ZERO overlap
against the 40-question benchmark-v4 development set:
  - 6 unseen factual cases (H-F01..H-F06)
  - 8 unseen cross-paper comparison / protocol cases (H-R01..H-R08)
  - 4 unseen false-premise / out-of-corpus negative cases (H-N01..H-N04)

Compares Legacy-Hybrid (pre-optimization Stage-4 baseline) vs Production-Final
(Balanced-MMR + source-choice-v3 [E1:q2] + Cloud Query Planner + QA-Graph +
14-Paper Method Cards + concise premise_check).
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
import sqlite3
import time
import uuid

from .audit import now
from .corpus import load_corpus
from .evaluation import criterion_source_coverage, linear_quantile, support_metrics
from .evaluation_datasets import METRICS, load_benchmark, stable_id, write_json
from .evaluation_details import DetailedEvaluationDataset, PROFILE, detailed_output
from .ingest import atomic_json
from .isolated_graph import IsolatedGraph
from .local_models import run_worker, vector_metadata
from .method_cards import MethodCardNavigator, load_aux_vectors
from .p3_evaluation import CARDS_REL, CLAIM_VECS_REL, SLOT_VECS_REL
from .p5_final_evaluation import _verify_remote_batched_strict
from .providers import Providers
from .rerank_service import close_workers
from .retrieval import normalize
from .settings import settings
from .workflow import Workflow

VERSION = 'benchmark-holdout-v1'
ARMS = ('Legacy-Hybrid', 'Production-Final')
ARM_CONFIGS = {
    'Legacy-Hybrid': dict(
        graph_enabled=False, graph_query_aware=False, use_method_cards=False, path_budget=0,
        rerank_contextual=False, rerank_windowed=False, evidence_budget=6000, evidence_max=8,
        source_policy='named_first', score_policy='fixed', reservation_policy='legacy',
        citation_protocol='source-choice-v1', query_planner=False, premise_check=False,
    ),
    'Production-Final': dict(
        graph_enabled=True, graph_query_aware=True, use_method_cards=True, path_budget=1200,
        rerank_contextual=True, rerank_windowed=False, evidence_budget=18000, evidence_max=12,
        source_policy='named_first', score_policy='relative', reservation_policy='subquery_balanced',
        citation_protocol='source-choice-v3', query_planner=True, premise_check=True,
    ),
}
CODE_FILES = (
    'src/papertech/entity_aliases.py', 'src/papertech/local_models.py',
    'src/papertech/isolated_graph.py', 'src/papertech/method_cards.py',
    'src/papertech/query_planner.py', 'src/papertech/rerank_runtime.py',
    'src/papertech/rerank_service.py', 'src/papertech/retrieval.py',
    'src/papertech/evidence_context.py', 'src/papertech/citations.py',
    'src/papertech/providers.py', 'src/papertech/workflow.py',
    'src/papertech/graph_store.py', 'src/papertech/holdout_evaluation.py',
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _holdout_specs():
    """Return (cases, units) for 18 brand-new unseen holdout questions."""
    units = {
        # --- 6 Factual ---
        'HF01_domains': dict(
            answer_point='STaRK 覆盖三个领域：商品搜索（STARK-AMAZON）、学术论文检索（STARK-MAG）、精准医疗（STARK-PRIME），由模拟用户与半结构化知识库（SKB）交互的大规模合成问答对和作为真实参考的小规模人工问答对组成。',
            primary_chunk='chunk_6b5383484693f6226010eab8143f80d6',
            known_support_chunks=['chunk_6b5383484693f6226010eab8143f80d6', 'chunk_2c06f903c181ffbdb1246026daa909b0'],
        ),
        'HF01_reranker_eval': dict(
            answer_point='LLM Reranker（GPT-4-turbo 与 Claude3）对 ada-002 的 top-k 候选重排：合成查询 k=20、人工查询 k=10；因计算开销高仅在随机 10% 测试查询样本上评测。',
            primary_chunk='chunk_bb730573725b148aa7913e7f17bb9261',
            known_support_chunks=['chunk_bb730573725b148aa7913e7f17bb9261'],
        ),
        'HF02_setup': dict(
            answer_point='StructGPT 错误分析选取三个不同结构化数据类型数据集（正文列 WebQSP、WTQ、Spider；图 3 统计 WebQSP、WikiSQL、Spider），每集随机抽样 100 条错误分为五类（Selection Error、Reasoning Error、Generation Format Error、Hallucination、Other Errors）。',
            primary_chunk='chunk_b21e952cc42e9ffedbde26c85006586c',
            known_support_chunks=['chunk_b21e952cc42e9ffedbde26c85006586c'],
        ),
        'HF02_dist': dict(
            answer_point='图 3 显示 WebQSP（KGQA）中 Selection Error 占主导（74%）；Spider（Text-to-SQL）中 Reasoning Error 占主导（63%，Selection Error 占 21%）。',
            primary_chunk='chunk_c9e4e94b591dab5929ea0ee5c7f0817b',
            known_support_chunks=['chunk_c9e4e94b591dab5929ea0ee5c7f0817b'],
        ),
        'HF03_variants': dict(
            answer_point='MindMap 消融比较了 Neighbor-only 与 Path-only 两种变体；合并两者后 GenMedGPT-5k 的 BERTScore F1（0.7960 vs 0.7072/0.7002）与幻觉量化（0.5890 vs 0.3894/0.3854）显著提升；Neighbor-only 更利于事实准确度，Path-only 更擅长寻找外部相关信息。',
            primary_chunk='chunk_f91f666883d4d6df7614b58321f41800',
            known_support_chunks=['chunk_f91f666883d4d6df7614b58321f41800', 'chunk_070763ffa4f4fcab7e4a133c464907f3'],
        ),
        'HF03_p1': dict(
            answer_point='在 ExplainCPE 指令提示消融中，加入要求 LLM 结合自身已有知识的提示模板 p1（"combine with the knowledge you already have"）将准确率提升了 8.2%（61.7% vs w/o p1 的 53.5%）。',
            primary_chunk='chunk_070763ffa4f4fcab7e4a133c464907f3',
            known_support_chunks=['chunk_070763ffa4f4fcab7e4a133c464907f3'],
        ),
        'HF04_qlora': dict(
            answer_point='CuriousLLM（KGP-Mistral）以 Mistral-7B-Instruct-v0.2 为底座，用 next-token prediction 与 QLoRA（8-bit、LoRA rank=32、lr=1e-5、batch size=12、90%-5%-5% 划分）在 Follow-upQA 上微调，同等算力下相比原 KGP 训练 T5 减少 85% 训练时间。',
            primary_chunk='chunk_fb24ed864a9886ec8722f831391af3b7',
            known_support_chunks=['chunk_fb24ed864a9886ec8722f831391af3b7'],
        ),
        'HF04_mdr': dict(
            answer_point='MDR-KG 的 BERT 段落编码器在 HotpotQA 上按 MDR 方法训练：给定初始检索段落预测后续支持段落，缩小共同回答问题的段落对距离并用负采样拉大无关段落距离。',
            primary_chunk='chunk_69407b618c1969f701e74bd3cf523c95',
            known_support_chunks=['chunk_69407b618c1969f701e74bd3cf523c95'],
        ),
        'HF05_ablation': dict(
            answer_point='RoG 去掉 planning 后退化为仅靠问题作答的常规 LLM，因缺乏知识 F1 大幅下滑（WebQSP 70.81→49.69，CWQ 56.17→33.76）；去掉 reasoning 后虽因返回更多答案提高 Recall（79.85 / 67.89），但受检索路径噪声影响 Precision 骤降（46.90 / 18.88）。',
            primary_chunk='chunk_41f164dcc97380b68b515cce682cba4b',
            known_support_chunks=['chunk_41f164dcc97380b68b515cce682cba4b', 'chunk_8ff52490cf78a4324c98eaf422d29221'],
        ),
        'HF05_top3': dict(
            answer_point='RoG 使用指令微调后的 LLaMA2-Chat-7B 经 beam-search 生成 top-3（K=3）关系路径；继续增加 K 会引入更多噪声路径和检索开销，对最终效果增益甚微。',
            primary_chunk='chunk_2a54af5657f5157d4c806c5daace0980',
            known_support_chunks=['chunk_2a54af5657f5157d4c806c5daace0980', 'chunk_a3b2c707435931fa6249f247cd7d79fc'],
        ),
        'HF06_finqa': dict(
            answer_point='因 Wikipedia 常在 LLM 预训练中曝光，ToG-2 收集 2023 年中国上市公司财报（17,013 篇文档）构建含 7 类关系（subsidiary company、main business、supplier、sibling company、bulk transaction、subsidiary、customer）的金融 KG，并人工设计 97 道多跳问题（ToG-FinQA）。',
            primary_chunk='chunk_8eeb2944a7ceb3bfebc67f8259978867',
            known_support_chunks=['chunk_8eeb2944a7ceb3bfebc67f8259978867', 'chunk_c3c4750bf9f19cd0c1822ea01143d334'],
        ),
        'HF06_graphrag': dict(
            answer_point='GraphRAG 在大规模语料上的建图索引计算成本难以承受，因此论文仅在 ToG-FinQA 上评测了 GraphRAG。',
            primary_chunk='chunk_03f04d6779a13e52c52c60284bd82092',
            known_support_chunks=['chunk_03f04d6779a13e52c52c60284bd82092'],
        ),
        # --- 8 Cross-Paper ---
        'HR01_tog': dict(
            answer_point='ToG 默认设置宽度 N=3、深度 Dmax=3（开销随深度线性增长且超过 3 跳后仅少数问题需要、增益递减）；其纯 KG 剪枝中 LLM 剪枝优于 BM25 与 SentenceBERT。',
            primary_chunk='chunk_8b9e861ea949a3eb2fc9ed5a97b24644',
            known_support_chunks=['chunk_8b9e861ea949a3eb2fc9ed5a97b24644', 'chunk_270d9350248b566ed224ba5147a295a2'],
        ),
        'HR01_tog2': dict(
            answer_point='ToG-2 在 AdvHotpotQA 实体上下文剪枝实验中对比 BGE-Reranker、MiniLM、BGE-Embedding、BM25 与 LLM：BGE-Reranker（DRM）在更长上下文与更多候选 K 下表现最佳且性价比与泛化性更高，而 LLM 受输入长度制约表现下降。',
            primary_chunk='chunk_d4f6a4a037b6e147680603d67ba56fc0',
            known_support_chunks=['chunk_5d7ff60c6e6d8ed3d35fddd69c75e903', 'chunk_d4f6a4a037b6e147680603d67ba56fc0'],
        ),
        'HR02_gret': dict(
            answer_point='G-Retriever 在 soft prompt tuning 中冻结 LLM 参数 θ、仅通过反向传播更新软提示参数 Pe（另设 Tuned LLM 用 LoRA 微调 Llama2-7b）；其局限在于当前检索组件是静态不可训练的（static retrieval component）。',
            primary_chunk='chunk_169332db0b56d09ba086374fa84a2040',
            known_support_chunks=['chunk_169332db0b56d09ba086374fa84a2040', 'chunk_255b9d4a6fbbac0cf6621acf84251f72', 'chunk_f800cd4e8fa59900491c3efa5f890329'],
        ),
        'HR02_lpkg': dict(
            answer_point='LPKG 将规划与 QA 解耦：仅用 KG 规划数据对规划 LLM（CodeQwen1.5-7B-Chat、Llama3-8B-Instruct）做 LoRA 微调，固定 QA LLM（GPT-3.5）以消除 QA 能力差异；40 条错例分析表明检索模型错误影响最大。',
            primary_chunk='chunk_8b27c0cb47d598cdda2eb2204b132786',
            known_support_chunks=['chunk_8b27c0cb47d598cdda2eb2204b132786', 'chunk_231843bdac931319ba29f46e6be14d6d'],
        ),
        'HR03_kgp': dict(
            answer_point='KGP 在固定总检索段落预算下，增大 branching factor 初期会增加通往答案的推理路径使性能上升，但继续增大会挤占初始种子节点数量、降低对文档 KG 的覆盖率，导致性能下降。',
            primary_chunk='chunk_e1a39884458dd5c4e4ae63ae1126a5d5',
            known_support_chunks=['chunk_e1a39884458dd5c4e4ae63ae1126a5d5', 'chunk_0498eae1a386ebf0d6d488dedfd6381d'],
        ),
        'HR03_curious': dict(
            answer_point='CuriousLLM 在 Table 3 中显示提前终止变体 KGP_Mistral_ET 在四个 MD-QA 数据集上的 Acc/EM 略低于完整版 KGP_Mistral（如 HotpotQA Acc 72.20 vs 73.80、2WikiMQA 46.00 vs 49.40、IIRC 34.80 vs 36.69、MuSiQue 34.80 vs 36.50），但在 HotpotQA/IIRC/MuSiQue 上仍高于 KGP_T5。',
            primary_chunk='chunk_9c4ed8fb017cd0f15b601822cb9b8718',
            known_support_chunks=['chunk_9c4ed8fb017cd0f15b601822cb9b8718'],
        ),
        'HR04_kggpt': dict(
            answer_point='KG-GPT 在 FACTKG 与 MetaQA 上测试 12-shot / 8-shot / 4-shot（MetaQA 3-hop 从 94.0 降至 46.6）；每集抽 100 条错例分析显示图检索阶段错误最少，而跳数增加会显著推高句子分割错误。',
            primary_chunk='chunk_13719303fa087942493eb1fb55fd4c52',
            known_support_chunks=['chunk_3f7eb65828761447433c66c28ad111a4', 'chunk_13719303fa087942493eb1fb55fd4c52'],
        ),
        'HR04_structgpt': dict(
            answer_point='StructGPT 在 TableQA 与 Text-to-SQL 中使用 32 个 in-context exemplars；每集抽 100 条错例分析显示 WebQSP（KGQA）以 Selection Error 占主导（74%），Spider（Text-to-SQL）以 Reasoning Error 占主导（63%）。',
            primary_chunk='chunk_c9e4e94b591dab5929ea0ee5c7f0817b',
            known_support_chunks=['chunk_c11d51b003e670a9b0426a34b4b70425', 'chunk_1efd4680d043944e45eb1947af46faa9',
                                  'chunk_b21e952cc42e9ffedbde26c85006586c', 'chunk_c9e4e94b591dab5929ea0ee5c7f0817b'],
        ),
        'HR05_graphqa': dict(
            answer_point='G-Retriever 的 GraphQA 标准化整合 ExplaGraphs（常识推理）、SceneGraphs（视觉 QA）、WebQSP（多跳 KGQA）三个现有数据集为统一文本属性图问答格式。',
            primary_chunk='chunk_e3039cc70fdc7caf88ff60d3a386ed29',
            known_support_chunks=['chunk_e3039cc70fdc7caf88ff60d3a386ed29', 'chunk_255b9d4a6fbbac0cf6621acf84251f72'],
        ),
        'HR05_stark': dict(
            answer_point='STaRK 覆盖商品、学术论文、精准医疗三个半结构化知识库（SKB）；微调小型稠密模型 DPR/QAGNN 因参数量小且易过拟合表现不佳，而 GPT-4 / Claude3 Reranker 在语言更丰富细腻的人工查询上尤为突出。',
            primary_chunk='chunk_a407e76d3edfaf1a9413559721b56299',
            known_support_chunks=['chunk_6b5383484693f6226010eab8143f80d6', 'chunk_a407e76d3edfaf1a9413559721b56299', 'chunk_a58abbb14497e4834ba62385406a1d89'],
        ),
        'HR06_hippo': dict(
            answer_point='HippoRAG 使用现成 GPT-3.5-turbo-1106 与 Contriever/ColBERTv2（不微调），仅用 100 条 MuSiQue 训练样本调两个超参（同义词阈值 τ=0.8、PPR 阻尼系数 0.5）；从 MuSiQue、2WikiMultiHopQA、HotpotQA 验证集各抽 1000 题并汇集候选段落作为语料。',
            primary_chunk='chunk_fe5363c7abef240f62c37ad4ab224530',
            known_support_chunks=['chunk_fe5363c7abef240f62c37ad4ab224530', 'chunk_3fa28005a4df0de5249826585cf9d713'],
        ),
        'HR06_lpkg': dict(
            answer_point='LPKG 使用 Wikipedia 语料 + Contriever-MS 取 Top 5，评测 HotPotQA/2WikiMQA/MuSiQue/Bamboogle/CLQA-Wiki；为对比常规蒸馏，从三集训练集各抽 3000 题（共 9000 题）让 GPT-3.5 蒸馏规划微调 CodeQwen（DLPKG），在未见集 Bamboogle 上验证 KG 派生数据更优。',
            primary_chunk='chunk_80af5b3aa25d71d17409ebe2b757ab19',
            known_support_chunks=['chunk_8b27c0cb47d598cdda2eb2204b132786', 'chunk_b5d503a2d2586e2d55d4e0841114a942',
                                  'chunk_80af5b3aa25d71d17409ebe2b757ab19', 'chunk_231843bdac931319ba29f46e6be14d6d'],
        ),
        'HR07_roadmap': dict(
            answer_point='Roadmap 综述中 KEPLER 用 LLM 编码实体文本描述并联合优化知识嵌入与语言建模目标；DRAGON 双向融合文本片段与 KG 子图，用 MLM 与 KG 链接预测两项自监督任务联合预训练。',
            primary_chunk='chunk_3ca88dd0b19ec139e7b11b5359f2dbc2',
            known_support_chunks=['chunk_3ca88dd0b19ec139e7b11b5359f2dbc2'],
        ),
        'HR07_tot': dict(
            answer_point='Tree-of-Traversals 是零样本算法，不微调黑盒 LLM 且不依赖固定 schema，通过 KG 接口（SPARQL / API）与动作状态机（ASM）经树搜索动态扩展局部子图。',
            primary_chunk='chunk_0cb3c2dcbacf18237a13b232366d2be8',
            known_support_chunks=['chunk_0cb3c2dcbacf18237a13b232366d2be8', 'chunk_622fbe3ed4198464c25fb8d606b691dd'],
        ),
        'HR07_mindmap': dict(
            answer_point='MindMap 是即插即用提示流水线，通过路径与邻居探索从外部 KG 检索证据子图，再用提示引导 LLM 将外部事实与自身隐式知识融合推理，无需微调。',
            primary_chunk='chunk_c36c0155590c0da356beed7403c524ae',
            known_support_chunks=['chunk_c36c0155590c0da356beed7403c524ae', 'chunk_070763ffa4f4fcab7e4a133c464907f3', 'chunk_f91f666883d4d6df7614b58321f41800'],
        ),
        'HR08_kgp': dict(
            answer_point='KGP 先由 LLM 分类问题关注文档结构还是内容：结构类提取 Page/Table 等关键词直接检索结构节点；内容类以 TF-IDF 初始化种子段落后由微调遍历代理迭代扩展邻居。',
            primary_chunk='chunk_84038d4c6f7949959af0974d04ee2379',
            known_support_chunks=['chunk_84038d4c6f7949959af0974d04ee2379'],
        ),
        'HR08_hippo': dict(
            answer_point='HippoRAG 指出 path-finding multi-hop 问题在多个候选路径并存时需要找到连接多个实体的特定关联路径，简单迭代检索容易因分支过多而迷失。',
            primary_chunk='chunk_900d1ff5b080ca47760a93ddc7d9e173',
            known_support_chunks=['chunk_900d1ff5b080ca47760a93ddc7d9e173'],
        ),
        'HR08_tog2': dict(
            answer_point='ToG-2 在 AdvHotpotQA 案例中区分 Both-enhanced（三元组链接推导中间实体 + 该实体文档上下文确认答案）与 Doc-enhanced（三元组链接引导，最终从目标实体文档上下文找到答案）。',
            primary_chunk='chunk_a5be5bd1049658e91cbad5ab416957de',
            known_support_chunks=['chunk_a5be5bd1049658e91cbad5ab416957de'],
        ),
        # --- 4 Negative ---
        'HN01_hippo_not_ft': dict(
            answer_point='HippoRAG 并未用 LoRA 微调 GPT-3.5 或 Contriever；原文使用现成 GPT-3.5-turbo-1106 与 Contriever/ColBERTv2，100 条 MuSiQue 训练样本仅用于调节同义词阈值 τ=0.8 和 PPR 阻尼系数 0.5 两个超参。',
            primary_chunk='chunk_fe5363c7abef240f62c37ad4ab224530',
            known_support_chunks=['chunk_fe5363c7abef240f62c37ad4ab224530'],
        ),
        'HN02_lpkg_decoupled': dict(
            answer_point='LPKG 将规划 LLM 与 QA LLM 解耦：仅用 KG 派生规划数据对规划 LLM（CodeQwen1.5-7B-Chat、Llama3-8B-Instruct）做 LoRA 微调，QA LLM 固定为 GPT-3.5 保持不变，并非全参联合微调或替换 QA LLM。',
            primary_chunk='chunk_8b27c0cb47d598cdda2eb2204b132786',
            known_support_chunks=['chunk_8b27c0cb47d598cdda2eb2204b132786', 'chunk_36fd3f5ddb484701ba81edeecc069767'],
        ),
        'HN03_gret_frozen_static': dict(
            answer_point='G-Retriever 在 Soft Prompt Tuning 中冻结 LLM 权重 θ、仅更新软提示 Pe（LoRA 属于单独的 Tuned LLM 设置），且论文明确指出当前检索组件是静态不可训练的（static retrieval component）。',
            primary_chunk='chunk_169332db0b56d09ba086374fa84a2040',
            known_support_chunks=['chunk_169332db0b56d09ba086374fa84a2040', 'chunk_255b9d4a6fbbac0cf6621acf84251f72', 'chunk_f800cd4e8fa59900491c3efa5f890329'],
        ),
        'HN04_ooc_fabricated': dict(
            answer_point='当前 14 篇语料中不存在 GraphOmni-2099 方法或 BioSTaRK-XL 基准，无法报告对比 F1 或继承章节；语料中仅有 MindMap（评测 GenMedGPT-5k/CMCQA/ExplainCPE）与 STaRK（含 STARK-PRIME）。',
            primary_chunk='chunk_c36c0155590c0da356beed7403c524ae',
            known_support_chunks=['chunk_c36c0155590c0da356beed7403c524ae', 'chunk_6b5383484693f6226010eab8143f80d6'],
        ),
    }

    cases = [
        dict(id='H-F01', category='fact', generate=True,
             question='STaRK 基准覆盖哪三个应用领域？它如何把合成问答对与人工生成问答对结合，并对 LLM Reranker 采用怎样的评测候选数 k 和抽样比例？',
             units=['HF01_domains', 'HF01_reranker_eval'],
             expected_answer='STaRK 覆盖商品搜索（STARK-AMAZON）、学术论文检索（STARK-MAG）、精准医疗（STARK-PRIME）三个领域，由大规模合成问答对与小规模人工参考问答对组成；LLM Reranker（GPT-4-turbo、Claude3）重排 ada-002 候选，合成查询 k=20、人工查询 k=10，并在随机 10% 测试样本上评测。'),
        dict(id='H-F02', category='fact', generate=True,
             question='StructGPT 的错误分析选取了哪三个代表不同结构化数据类型的基准、各自抽样多少条失败案例？在 WebQSP（KGQA）与 Spider（Text-to-SQL）上占主导的错误类型和比例分别是多少？',
             units=['HF02_setup', 'HF02_dist'],
             expected_answer='StructGPT 错误分析按三种结构化数据各随机抽样 100 条失败案例并分为 5 类（正文列 WebQSP、WTQ、Spider，图 3 统计 WebQSP、WikiSQL、Spider）；图 3 中 WebQSP（KGQA）以 Selection Error 为主（74%），Spider（Text-to-SQL）以 Reasoning Error 为主（63%，Selection Error 21%）。'),
        dict(id='H-F03', category='fact', generate=True,
             question='MindMap 在消融实验中比较了哪两种证据探索变体？结合 Table 8 与 ExplainCPE 上的指令提示消融，说明合并两种探索和加入提示模板 p1 分别带来了什么影响。',
             units=['HF03_variants', 'HF03_p1'],
             expected_answer='MindMap 比较了 Neighbor-only 与 Path-only 变体；合并两者在 GenMedGPT-5k 的 BERTScore F1（0.7960）和幻觉量化（0.5890）上显著优于任一单一变体，其中 Neighbor-only 更利于事实准确度而 Path-only 更利于寻找外部信息；提示模板 p1（结合自身已有知识）使准确率提升 8.2%（61.7% vs 53.5%）。'),
        dict(id='H-F04', category='fact', generate=True,
             question='CuriousLLM（KGP-Mistral）采用什么底座模型与微调配置在 Follow-upQA 上训练？它在训练时间上相对原 KGP 的 T5 模型有何变化，并说明其 MDR-KG 段落编码器的训练思路。',
             units=['HF04_qlora', 'HF04_mdr'],
             expected_answer='CuriousLLM 以 Mistral-7B-Instruct-v0.2 为底座，用 next-token prediction 与 QLoRA（8-bit、rank=32、lr=1e-5、batch size=12，90%-5%-5% 划分）微调，在相同算力下较原 KGP 的 T5 减少 85% 训练时间；MDR-KG 用 BERT 段落编码器在 HotpotQA 上按 MDR 训练，给定初始段落预测后续支持段落，拉近共同支持段落距离并用负采样推远无关段落。'),
        dict(id='H-F05', category='fact', generate=True,
             question='RoG 消融实验去掉 planning 模块（w/o planning）或去掉 reasoning 模块（w/o reasoning）分别会导致什么现象？论文为什么最终只用 beam-search 生成 top-3 关系路径？',
             units=['HF05_ablation', 'HF05_top3'],
             expected_answer='去掉 planning 后 RoG 退化为常规 LLM，缺乏 KG 知识导致 WebQSP/CWQ F1 大降（70.81→49.69、56.17→33.76）；去掉 reasoning 虽提高 Recall 但因路径噪声导致 Precision 骤降（46.90 / 18.88）。RoG 采用 beam-search 生成 top-3（K=3）关系路径，因为更多路径会增加检索噪声与耗时而对最终效果增益甚微。'),
        dict(id='H-F06', category='fact', generate=True,
             question='ToG-2 为什么专门构建了 ToG-FinQA 数据集？它的语料来源、图谱关系类型数量与问答规模分别是多少，为什么 GraphRAG 只在 ToG-FinQA 上参与了评测？',
             units=['HF06_finqa', 'HF06_graphrag'],
             expected_answer='因 Wikipedia 常出现在 LLM 预训练语料中，ToG-2 收集 2023 年中国上市公司财报（17,013 篇文档）构建含 7 类关系的金融 KG 与 97 道人工多跳问题（ToG-FinQA）；因 GraphRAG 在大语料上的索引建图成本难以承受，仅在 ToG-FinQA 上对其进行评测。'),
        dict(id='H-R01', category='cross', generate=True,
             question='对比 ToG 与 ToG-2 的剪枝与深度宽度设置：ToG 在默认宽度与深度上为何选 N=3、Dmax=3 且 LLM 剪枝优于 BM25/SentenceBERT？而 ToG-2 在基于上下文的实体剪枝实验中为何转而选用 BGE-Reranker（DRM）而不是 LLM 剪枝？',
             units=['HR01_tog', 'HR01_tog2'],
             expected_answer='ToG 默认 N=3、Dmax=3（计算开销随深度线性增长且超过 3 跳增益递减），其纯三元组剪枝中 LLM 优于 BM25/SentenceBERT；ToG-2 融入长文档上下文后，在 AdvHotpotQA 剪枝对比中 BGE-Reranker（DRM）对长上下文与大候选集 K 容忍度更好、性价比与泛化性更高，而 LLM 受输入长度制约表现下降。'),
        dict(id='H-R02', category='cross', generate=True,
             question='比较 G-Retriever 与 LPKG 的参数高效训练设计：各自冻结了哪些模块、微调了哪些参数或模型？G-Retriever 当前的检索组件有何局限，LPKG 在错误分析中又指出哪一环影响最大？',
             units=['HR02_gret', 'HR02_lpkg'],
             expected_answer='G-Retriever 在 soft prompt tuning 中冻结 LLM 权重 θ 仅训练软提示 Pe（另有 LoRA 微调配置），局限是当前检索组件静态不可训练；LPKG 解耦规划与 QA，仅对规划 LLM（CodeQwen1.5-7B-Chat、Llama3-8B-Instruct）做 LoRA 微调而固定 QA LLM（GPT-3.5），错例分析显示检索模型错误影响最大。'),
        dict(id='H-R03', category='cross', generate=True,
             question='对比 KGP 与 CuriousLLM 在遍历开销控制上的发现：KGP 固定上下文预算时增大 branching factor 为何性能先升后降？CuriousLLM 引入提前终止变体（KGP_Mistral_ET）后，在四个 MD-QA 数据集上的表现相对完整版 KGP_Mistral 有何变化？',
             units=['HR03_kgp', 'HR03_curious'],
             expected_answer='KGP 在固定总检索段落预算下，增大 branching factor 初期可提供更多候选路径提升效果，但过大会挤压初始种子节点数、降低 KG 覆盖率从而使效果下滑；CuriousLLM 的提前终止版 KGP_Mistral_ET 在四个 MD-QA 集上 Acc/EM 略低于完整版 KGP_Mistral，但在 HotpotQA/IIRC/MuSiQue 上仍高于 KGP_T5。'),
        dict(id='H-R04', category='cross', generate=True,
             question='对比 KG-GPT 与 StructGPT 在少样本示例与错误瓶颈上的发现：两篇论文分别在什么任务上使用了多少 in-context exemplars？各自抽样 100 条错例分析后，哪个环节的错误最突出或最少？',
             units=['HR04_kggpt', 'HR04_structgpt'],
             expected_answer='KG-GPT 在 FACTKG 与 MetaQA 上测试 12/8/4-shot，每集 100 条错例分析显示图检索阶段错误最少、而跳数增加会显著加剧句子分割错误；StructGPT 在 TableQA 与 Text-to-SQL 上使用 32 个 in-context exemplars，每集 100 条错例显示 WebQSP（KGQA）以 Selection Error 为主（74%）、Spider（Text-to-SQL）以 Reasoning Error 为主（63%）。'),
        dict(id='H-R05', category='cross', generate=True,
             question='对比 G-Retriever 提出的 GraphQA 基准与 STaRK 基准：二者分别整合或构建了哪三个数据集/领域，查询与知识表示形态有何不同？STaRK 中小型微调稠密检索器（DPR、QAGNN）为何表现不佳，而 LLM Reranker 又在什么类型的查询上尤为突出？',
             units=['HR05_graphqa', 'HR05_stark'],
             expected_answer='GraphQA 整合 ExplaGraphs（常识推理）、SceneGraphs（视觉 QA）与 WebQSP（KGQA）为统一文本属性图问答格式；STaRK 覆盖商品（STARK-AMAZON）、学术（STARK-MAG）和精准医疗（STARK-PRIME）三个半结构化知识库（含合成与人工查询）。STaRK 中微调小型模型 DPR/QAGNN 因参数量小、易过拟合而表现不佳；GPT-4/Claude3 Reranker 在语言更细腻多样的人工查询上表现尤为突出。'),
        dict(id='H-R06', category='cross', generate=True,
             question='比较 HippoRAG 与 LPKG 在检索器、评测子集与训练方式上的差异：二者各使用什么检索器，各自如何从 MuSiQue / 2WikiMultiHopQA / HotpotQA 构造评测集？为什么 LPKG 额外与 GPT-3.5 蒸馏规划数据（DLPKG）做了对比，而 HippoRAG 只调了哪两个超参数？',
             units=['HR06_hippo', 'HR06_lpkg'],
             expected_answer='HippoRAG 使用现成 GPT-3.5-turbo-1106 与 Contriever/ColBERTv2，不微调模型、仅在 100 条 MuSiQue 训练样本上调同义词阈值 τ=0.8 与 PPR 阻尼系数 0.5，并从三集验证集各抽 1000 题汇集候选段落建语料；LPKG 用 Wikipedia + Contriever-MS Top 5 评测四常规集与 CLQA-Wiki，另从三集训练集各抽 3000 题（共 9000 题）用 GPT-3.5 蒸馏规划训练 DLPKG，在未见集 Bamboogle 上证明 KG 派生数据优于常规教师蒸馏。'),
        dict(id='H-R07', category='cross', generate=True,
             question='对比 Roadmap 综述中的预训练融合模型（如 KEPLER、DRAGON）与 Tree-of-Traversals、MindMap 这类推理期即插即用方法：前者通过什么联合目标在预训练期融合 KG，后两者又分别怎样在不微调黑盒 LLM 的前提下接入外部 KG？',
             units=['HR07_roadmap', 'HR07_tot', 'HR07_mindmap'],
             expected_answer='Roadmap 综述中 KEPLER 联合优化知识嵌入与语言建模目标，DRAGON 双向融合文本与 KG 子图并以 MLM 与 KG 链接预测自监督预训练；Tree-of-Traversals 零样本不微调黑盒 LLM，靠 KG 接口（SPARQL/API）与动作状态机经树搜索扩展局部子图；MindMap 即插即用不微调，通过路径与邻居探索检索 KG 子图并提示 LLM 融合外部事实与隐式知识。'),
        dict(id='H-R08', category='cross', generate=True,
             question='KGP、HippoRAG 与 ToG-2 各自强调了一类常规检索难以处理的问题场景：请分别说明 KGP 如何区分文档结构类与内容类问题、HippoRAG 定义的 "path-finding multi-hop" 问题难在哪里，以及 ToG-2 的 Both-enhanced 与 Doc-enhanced 案例如何体现图与文档的协作。',
             units=['HR08_kgp', 'HR08_hippo', 'HR08_tog2'],
             expected_answer='KGP 先由 LLM 判别结构类（提取 Page/Table 关键词直取结构节点）或内容类（TF-IDF 种子段落 + 微调代理遍历邻居）；HippoRAG 的 path-finding multi-hop 难在多条候选路径并存时需锁定连接多个实体的特定路径，简单迭代易迷失；ToG-2 的 Both-enhanced 同时靠三元组推导中间实体并用其文档定位答案，Doc-enhanced 则以三元组引导并从目标实体文档提取最终答案。'),
        dict(id='H-N01', category='negative', generate=True,
             question='有人总结说：HippoRAG 在 MuSiQue 的 100 条训练样本上用 LoRA 微调了 GPT-3.5 和 Contriever，所以才能在多跳问答上超越 IRCoT。这种说法符合原文吗？请指出原文实际做法。',
             units=['HN01_hippo_not_ft'],
             expected_answer='不符合原文。HippoRAG 并未对 GPT-3.5 或 Contriever 进行微调（更无 LoRA）；原文使用现成的 GPT-3.5-turbo-1106 和 Contriever/ColBERTv2，100 条 MuSiQue 训练样本仅用于调节同义词阈值 τ=0.8 和 PPR 阻尼系数 0.5 两个超参数。'),
        dict(id='H-N02', category='negative', generate=True,
             question='LPKG 之所以在 HotPotQA 和 CLQA-Wiki 上击败 ReAct 和 Self-Ask，是因为它把规划 LLM 和回答用的 QA LLM 一起在 Wikidata15k 上做了全参数微调并统一换成了 Llama3-8B，对吗？',
             units=['HN02_lpkg_decoupled'],
             expected_answer='不对。LPKG 将规划与 RAG/QA 解耦为两个独立模型：仅用 Wikidata15k 派生的规划数据对规划 LLM（CodeQwen1.5-7B-Chat 或 Llama3-8B-Instruct）做 LoRA 微调，而 QA LLM 固定为 GPT-3.5 不变以对齐基线、消除 QA 模型差异。'),
        dict(id='H-N03', category='negative', generate=True,
             question='根据 G-Retriever 论文，它在 Soft Prompt Tuning 阶段同时端到端更新了 Llama2-7b 全部权重以及可训练的 PCST 检索模块，从而消除了检索误差，这一描述准确吗？',
             units=['HN03_gret_frozen_static'],
             expected_answer='不准确。第一，Soft Prompt Tuning 期间 LLM 参数 θ 冻结，梯度仅更新软提示 Pe（LoRA 属于单独的 Tuned LLM 配置）；第二，论文结论的局限性明确指出当前 G-Retriever 采用静态检索组件（static retrieval component），检索模块尚未可训练。'),
        dict(id='H-N04', category='negative', generate=True,
             question='请对比 GraphOmni-2099 与 MindMap 在 BioSTaRK-XL 医疗基准上的 F1 分数，并说明 GraphOmni-2099 在哪一章继承了 STaRK-PRIME 的检索协议。',
             units=['HN04_ooc_fabricated'],
             expected_answer='无法回答该对比，必须拒答或明确指出越界：当前 14 篇语料中不存在 GraphOmni-2099 方法或 BioSTaRK-XL 基准；语料中仅有 MindMap（评测 GenMedGPT-5k、CMCQA、ExplainCPE）与 STaRK（含 STARK-PRIME），二者间亦无该跨基准评测记录。'),
    ]
    return cases, units


class SharedQ00Providers(Providers):
    """Share precomputed Q00 cloud embeddings across both arms; live-embed subqueries for Production-Final."""
    def __init__(self, cfg, audit, q00_vectors=None):
        super().__init__(cfg, audit)
        self.q00_vectors = dict(q00_vectors or {})

    def embedding(self, request_id, texts):
        missing = [t for t in texts if t not in self.q00_vectors]
        if missing:
            fetched = super().embedding(request_id, missing)
            for t, vec in zip(missing, fetched):
                self.q00_vectors[t] = list(vec)
        return [list(self.q00_vectors[t]) for t in texts]


def freeze(root):
    directory = root / 'artifacts/eval/stage-4' / VERSION
    bench_path = directory / 'benchmark.json'
    cards_path = root / CARDS_REL
    cards_sha = sha(cards_path)
    code_hashes = {name: sha(root / name) for name in CODE_FILES}
    if bench_path.exists():
        bench, digest, _ = load_benchmark(root, VERSION)
        if bench.get('code_sha256') != code_hashes or bench.get('method_cards_sha256') != cards_sha:
            raise RuntimeError('frozen_holdout_code_or_cards_changed')
        return bench, digest, directory

    corpus_id, papers, chunks = load_corpus(root)
    chunk_map = {c['chunk_id']: c for c in chunks}
    # Verify zero question overlap with benchmark-v4
    v4_bench, v4_sha, _ = load_benchmark(root, 'benchmark-v4')
    v4_questions = {c['question'].strip() for c in v4_bench['cases']}

    cases, units = _holdout_specs()
    for uid, u in units.items():
        if u['primary_chunk'] not in chunk_map:
            raise ValueError(f'missing_primary_chunk:{uid}:{u["primary_chunk"]}')
        for cid in u['known_support_chunks']:
            if cid not in chunk_map:
                raise ValueError(f'missing_support_chunk:{uid}:{cid}')
        primary = chunk_map[u['primary_chunk']]
        u['paper_id'] = primary['paper_id']
        u['title'] = primary['title']
        u['page_start'] = primary['page_start']
        u['page_end'] = primary['page_end']
    for case in cases:
        if case['question'].strip() in v4_questions:
            raise ValueError(f'holdout_overlap_with_v4:{case["id"]}')
        paper_titles = []
        for uid in case['units']:
            for cid in units[uid]['known_support_chunks']:
                t = chunk_map[cid]['title']
                if t not in paper_titles:
                    paper_titles.append(t)
        case['source_papers'] = paper_titles
        case['min_source_papers'] = 0 if case['category'] == 'negative' else len(paper_titles)
        case['answerable'] = case['category'] != 'negative'
        case['negative_kind'] = (None if case['answerable']
                                 else ('out_of_corpus' if case['id'] == 'H-N04' else 'false_premise'))
        case['relation_review'] = dict(
            evidence='核对全部必要事实、引用与原文；没有来源时不得补造。',
            semantics='核对方法归属、实体角色、实验设置与方向；未见题集须独立人工/代理语义判读。',
            uncertainty='反例题必须直接纠正错误前提或拒答越界实体，不得迎合题干伪前提。',
        )

    cfg = settings(root)
    selected_keys = ('DEEPSEEK_MODEL', 'CLOUD_BGE_MODEL', 'CLOUD_BGE_PROVIDER',
        'LOCAL_RERANKER_PATH', 'LOCAL_RERANKER_PYTHON', 'LOCAL_RERANKER_DEVICE',
        'LOCAL_RERANKER_DTYPE', 'LOCAL_RERANKER_PERSISTENT')
    models = {key: cfg.get(key) for key in selected_keys}
    models['LOCAL_RERANKER_BATCH_SIZE'] = int(cfg.get('LOCAL_RERANKER_BATCH_SIZE', 4))

    bench = dict(
        version=VERSION, created_at=now(), corpus_id=corpus_id,
        dev_benchmark_checked='benchmark-v4', dev_benchmark_sha256=v4_sha, overlap_with_dev=0,
        graph_snapshot=deepcopy(v4_bench['graph_snapshot']),
        method_cards_path=CARDS_REL, method_cards_sha256=cards_sha,
        arms=list(ARMS), arm_configs=deepcopy(ARM_CONFIGS), models=models, code_sha256=code_hashes,
        dataset_description='18 题全新未见泛化测试集（6 事实 + 8 跨论文 + 4 反例/伪前提，与 40 题 benchmark-v4 零重叠）：Legacy-Hybrid 基线 vs Production-Final 完整方案端到端泛化实测。',
        prior_exposure='zero_exposure: 所有 18 道题在架构与参数调优完成后首次构建并冻结，用于检验真实样本外泛化能力。',
        scoring=deepcopy(v4_bench['scoring']),
        comparison=dict(mode='unseen_holdout_end_to_end_generalization', arms=list(ARMS), generation=True),
        controls=dict(
            arms=list(ARMS), arm_configs=deepcopy(ARM_CONFIGS), backend='neo4j',
            shared_q00_vectors='identical Cloudflare Q00 query embeddings across both arms; Production-Final additionally embeds planned subqueries',
            execution_order='alternate arm order by case index',
            gold_exclusion='question text only; gold pools and reference tables isolated',
        ),
        units=units, cases=cases,
    )
    directory.mkdir(parents=True, exist_ok=True)
    write_json(bench_path, bench)
    digest = sha(bench_path)
    (directory / 'benchmark.sha256').write_text(digest + '\n', encoding='utf-8')
    return bench, digest, directory


def paired_holdout_comparisons(summary):
    pairs = {}
    for row in summary['results']:
        pairs.setdefault(row['case_id'], {})[row['arm']] = row
    comparisons = {}
    for case_id, rows in pairs.items():
        if set(rows) != set(ARMS):
            comparisons[case_id] = dict(status='incomplete_pair', available_arms=sorted(rows))
            continue
        base, opt = rows[ARMS[0]], rows[ARMS[1]]
        b_ids = {e['chunk_id'] for e in base.get('evidence') or []}
        o_ids = {e['chunk_id'] for e in opt.get('evidence') or []}
        diffs = {k: (opt['metrics'][k] - base['metrics'][k]
                     if opt['metrics'].get(k) is not None and base['metrics'].get(k) is not None else None)
                 for k in METRICS}
        comparisons[case_id] = dict(
            status='paired', prod_minus_legacy=diffs, legacy_status=base['status'], prod_status=opt['status'],
            shared_evidence=sorted(b_ids & o_ids), added_evidence=sorted(o_ids - b_ids), removed_evidence=sorted(b_ids - o_ids),
            interpretation='记录 18 题未见集上 Production-Final 相对 Legacy-Hybrid 的端到端覆盖与引用差异；语义正确率需单独核查标注。',
        )
    return comparisons


class HoldoutDataset(DetailedEvaluationDataset):
    def __init__(self, root, version=VERSION, client=None, allow_enrichment=False):
        super().__init__(root, version, client, allow_enrichment=allow_enrichment)
        self.payload['description'] = self.bench['dataset_description']
        self.payload['metadata'].pop('no_model_comparison_run', None)
        for example in self.payload['examples']:
            example['outputs']['result_display']['location'] = '本题关联的 Legacy-Hybrid / Production-Final Experiment runs'
        write_json(self.directory / 'langsmith-dataset.json', self.payload)
        for example in self.payload['examples']:
            write_json(self.directory / 'cases' / (example['metadata']['case_id'] + '.json'), example)
        write_json(self.directory / 'detail-contract.json', dict(detail_profile=PROFILE,
            benchmark_sha256=self.digest,
            examples_sha256=hashlib.sha256(json.dumps(self.payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()))

    def sync_run(self, summary_path, answer_mode='full'):
        summary_path = Path(summary_path)
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        cases = {c['id']: c for c in self.bench['cases']}
        comparisons = paired_holdout_comparisons(summary)
        started = datetime.fromisoformat(summary['started'])
        ledger = self.root / 'data/rag.sqlite3'
        payloads = []
        for idx, row in enumerate(summary['results']):
            cid, arm = row['case_id'], row['arm']
            case = cases[cid]
            rid = stable_id(self.digest, summary['run_id'], cid, arm)
            ts = started + timedelta(microseconds=idx)
            out = detailed_output(row, case, self.bench, self.chunks)
            out['answer_local_file'] = cid + ('-prod.json' if arm == ARMS[1] else '-legacy.json')
            out['paired_comparison'] = comparisons[cid]
            if row.get('premise_check') is not None:
                out['premise_check'] = deepcopy(row['premise_check'])
            metrics = {k: row['metrics'].get(k) for k in METRICS if case['category'] != 'negative'}
            payload = dict(
                id=rid, name='stage4-holdout-evaluation', run_type='chain',
                inputs=dict(question=case['question']), outputs=out,
                reference_example_id=stable_id(self.digest, cid),
                start_time=ts, end_time=ts,
                extra=dict(metadata=dict(benchmark=self.bench['version'], benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], request_id=row['request_id'], case_id=cid,
                    arm=arm, capture_mode='evaluation_result_import', detail_profile=PROFILE)),
                tags=[self.bench['version'], arm, case['category']],
                _arm=arm, _metrics=metrics,
            )
            if ledger.exists():
                with sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True) as conn:
                    timing = conn.execute('SELECT started,finished FROM requests WHERE id=?', (row['request_id'],)).fetchone()
                if timing and timing[0] and timing[1]:
                    payload['start_time'], payload['end_time'] = map(datetime.fromisoformat, timing)
                    payload['outputs']['request_wall_seconds'] = (payload['end_time'] - payload['start_time']).total_seconds()
            usage = row.get('usage')
            if usage and usage.get('prompt_tokens') is not None and usage.get('completion_tokens') is not None:
                payload.update(prompt_tokens=usage['prompt_tokens'], completion_tokens=usage['completion_tokens'],
                    total_tokens=usage['prompt_tokens'] + usage['completion_tokens'])
            payload['_metrics'].update(
                retrieval_compute_seconds=row.get('retrieval_compute_seconds'),
                request_wall_seconds=payload['outputs'].get('request_wall_seconds'),
                evidence_count=len(row.get('evidence') or []),
                citation_ok=1.0 if row.get('status') != 'citation_error' else 0.0,
            )
            payloads.append(payload)
        write_json(summary_path.parent / 'langsmith-experiments.json', dict(
            benchmark=self.bench['version'], benchmark_sha256=self.digest, detail_profile=PROFILE,
            runs=json.loads(json.dumps(payloads, default=str))))
        write_json(summary_path.parent / 'per-question-comparison.json', comparisons)
        dataset = self.sync_dataset()
        client, experiments = self.client, []
        for arm in ARMS:
            name = f"papertech-{self.bench['version']}-{summary['run_id'][:12]}-{arm}"
            project = client.create_project(name, reference_dataset_id=dataset.id, upsert=True,
                description='18 题全新未见集泛化对照：Legacy-Hybrid vs Production-Final 完整结果。',
                metadata=dict(detail_profile=PROFILE, benchmark_sha256=self.digest,
                    original_run_id=summary['run_id'], arm=arm, original_status=summary['status']))
            expected = {p['id']: p for p in payloads if p['_arm'] == arm}
            existing = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            def upload(payload):
                client.create_run(project_name=name, **{k: v for k, v in payload.items() if not k.startswith('_')})
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(upload, [p for rid, p in expected.items() if rid not in existing]))
            present = {str(f.id) for f in client.list_feedback(run_ids=list(expected))} if expected else set()
            jobs = []
            for payload in expected.values():
                for key, value in payload['_metrics'].items():
                    fid = stable_id(payload['id'], key)
                    if value is not None and fid not in present:
                        jobs.append(dict(run_id=payload['id'], key=key, score=float(value), feedback_id=fid,
                            session_id=project.id, start_time=payload['start_time'], stop_after_attempt=1,
                            comment='18 题未见集自动指标；覆盖与引用状态不代表语义正确率。'))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda job: client.create_feedback(**job), jobs))
            verified = {str(r.id): r for r in client.list_runs(project_id=project.id, is_root=True)}
            if set(verified) != set(expected):
                raise ValueError('holdout_run_readback_mismatch')
            native_usage = self.sync_generation_usage(expected, verified, name)
            feedback = {str(f.id): f for f in client.list_feedback(run_ids=list(expected))} if expected else {}
            checked = sum(1 for p in expected.values() for k, v in p['_metrics'].items()
                          if v is not None and stable_id(p['id'], k) in feedback)
            client.update_project(project.id, end_time=datetime.now(timezone.utc))
            experiments.append(dict(arm=arm, project_id=str(project.id), runs_verified=len(verified),
                feedback_verified=checked, generation_usage_runs_verified=native_usage['verified'], detail_profile=PROFILE))
        self.status.update(status='experiments_verified', original_run_id=summary['run_id'],
            answer_mode='full', result_status=summary['status'], experiments=experiments,
            comparison_url=f"{dataset.url}/compare?selectedSessions=" + ','.join(e['project_id'] for e in experiments))
        write_json(summary_path.parent / 'langsmith-status.json', self.status)
        write_json(self.status_path, self.status)
        return self.status


def _mean(vals):
    nums = [v for v in vals if v is not None]
    return sum(nums) / len(nums) if nums else None


def _summarize_arm(rows, bench):
    ans = [r for r in rows if r['category'] != 'negative']
    cross = [r for r in rows if r['category'] in ('cross', 'cross_paper')]
    fact = [r for r in rows if r['category'] in ('fact', 'factual_control')]
    neg = [r for r in rows if r['category'] == 'negative']
    def block(items):
        return dict(
            count=len(items),
            recall5=_mean([r['metrics']['recall5'] for r in items]),
            recall8=_mean([r['metrics']['recall8'] for r in items]),
            mrr40=_mean([r['metrics']['mrr40'] for r in items]),
            evidence_coverage=_mean([r['metrics']['evidence_coverage'] for r in items]),
            all_units=sum(1 for r in items if r['metrics'].get('all_units')),
        )
    statuses = Counter(r['status'] for r in rows)
    neg_statuses = Counter(r['status'] for r in neg)
    gen_prompt = sum((r.get('usage') or {}).get('prompt_tokens') or 0 for r in rows)
    gen_comp = sum((r.get('usage') or {}).get('completion_tokens') or 0 for r in rows)
    cases_by_id = {c['id']: c for c in bench['cases']}
    attr = Counter()
    for r in ans:
        case = cases_by_id[r['case_id']]
        pool_ranked = {x['chunk_id'] for x in r.get('ranked') or []}
        ev_ids = {e['chunk_id'] for e in r.get('evidence') or []}
        for uid in case['units']:
            gold = set(bench['units'][uid]['known_support_chunks'])
            if gold & ev_ids:
                attr['covered'] += 1
            elif gold & pool_ranked:
                attr['in_pool_not_selected'] += 1
            else:
                attr['upstream_pool_miss'] += 1
    wall_s = [r['request_wall_seconds'] for r in rows if r.get('request_wall_seconds') is not None]
    return dict(
        answerable=block(ans), factual_control=block(fact), cross_paper=block(cross),
        negative=dict(count=len(neg), statuses=dict(neg_statuses), refused=neg_statuses.get('refused', 0)),
        statuses=dict(statuses), citation_errors=statuses.get('citation_error', 0),
        avg_evidence_count=_mean([len(r.get('evidence') or []) for r in rows]),
        gen_prompt_tokens=gen_prompt, gen_completion_tokens=gen_comp, gen_total_tokens=gen_prompt + gen_comp,
        unit_attribution=dict(attr),
        wall_p50=linear_quantile(wall_s, 0.5) if wall_s else None,
        wall_p95=linear_quantile(wall_s, 0.95) if wall_s else None,
    )


def render_report(root, summary_path):
    summary_path = Path(summary_path)
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    bench, digest, _ = load_benchmark(root, summary['benchmark'])
    by_arm = {arm: [r for r in summary['results'] if r['arm'] == arm] for arm in ARMS}
    stats = {arm: _summarize_arm(by_arm[arm], bench) for arm in ARMS}
    comparisons = paired_holdout_comparisons(summary)
    b, o = stats[ARMS[0]], stats[ARMS[1]]
    cases_by_id = {c['id']: c for c in bench['cases']}
    rows_by_key = {(r['case_id'], r['arm']): r for r in summary['results']}
    deltas = Counter()
    for cid, comp in comparisons.items():
        if cases_by_id[cid]['category'] == 'negative' or comp.get('status') != 'paired':
            continue
        d = comp['prod_minus_legacy']['evidence_coverage']
        deltas['improved' if d > 1e-9 else ('regressed' if d < -1e-9 else 'tied')] += 1
    out_dir = summary_path.parent / 'report'
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / 'comparison.json', dict(benchmark=bench['version'], benchmark_sha256=digest,
        run_id=summary['run_id'], status=summary['status'], stats=stats, deltas=dict(deltas),
        dataset_sync=summary.get('dataset_sync'), remote_verification=summary.get('remote_verification'),
        per_case=comparisons))

    def pct(v): return f'{v*100:.2f}%' if v is not None else 'N/A'
    def pp(a, x): return f'{(x-a)*100:+.2f} pp' if a is not None and x is not None else 'N/A'
    def sec(v): return f'{v:.3f}s' if v is not None else 'N/A'
    ls_url = (summary.get('dataset_sync') or {}).get('comparison_url') or ''
    n_ans, n_cross, n_fact, n_neg, n_all = (
        b['answerable']['count'], b['cross_paper']['count'], b['factual_control']['count'],
        b['negative']['count'], len(bench['cases'])
    )

    md = [
        f"# {bench['version']} 18 题全新未见泛化评测报告（Legacy-Hybrid vs Production-Final）",
        '',
        f"- 运行 ID：`{summary['run_id']}`；模型：`{bench['models'].get('DEEPSEEK_MODEL')}`；题集 SHA-256：`{digest}`。",
        f"- 样本外声明：18 道题与 `benchmark-v4`（40 题）**零重叠**，覆盖 14 篇论文的新机制/消融/误差分析/伪前提陷阱。",
        '',
        f'## 1. 核心指标对比（{n_ans} 道可回答题 + {n_neg} 道反例）',
        '',
        '| 指标 | Legacy-Hybrid | Production-Final | 差值 (Prod − Legacy) |',
        '|---|---:|---:|---:|',
        f"| **{n_ans} 题最终来源支持单元覆盖** | {pct(b['answerable']['evidence_coverage'])} | **{pct(o['answerable']['evidence_coverage'])}** | **{pp(b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage'])}** |",
        f"| **{n_ans} 题必要来源全覆盖题数** | {b['answerable']['all_units']}/{n_ans} | **{o['answerable']['all_units']}/{n_ans}** | **{o['answerable']['all_units']-b['answerable']['all_units']:+d} 题** |",
        f"| **{n_cross} 题跨论文关系来源覆盖** | {pct(b['cross_paper']['evidence_coverage'])} ({b['cross_paper']['all_units']}/{n_cross}) | **{pct(o['cross_paper']['evidence_coverage'])} ({o['cross_paper']['all_units']}/{n_cross})** | **{pp(b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage'])}** |",
        f"| {n_fact} 题事实题来源覆盖 | {pct(b['factual_control']['evidence_coverage'])} ({b['factual_control']['all_units']}/{n_fact}) | {pct(o['factual_control']['evidence_coverage'])} ({o['factual_control']['all_units']}/{n_fact}) | {pp(b['factual_control']['evidence_coverage'], o['factual_control']['evidence_coverage'])} |",
        f"| 事实单元归因 | `{b['unit_attribution']}` | `{o['unit_attribution']}` | covered {o['unit_attribution'].get('covered',0)-b['unit_attribution'].get('covered',0):+d} |",
        f"| **引用协议失败 (`citation_error`, {n_all}题)** | {b['citation_errors']}/{n_all} | **{o['citation_errors']}/{n_all}** | **{o['citation_errors']-b['citation_errors']:+d} 条** |",
        f"| **反例拒答数 (`refused`, {n_neg}题)** | {b['negative']['refused']}/{n_neg} | **{o['negative']['refused']}/{n_neg}** | **{o['negative']['refused']-b['negative']['refused']:+d} 题** |",
        f"| 生成输入 / 输出 / 总 Token | {b['gen_prompt_tokens']:,} / {b['gen_completion_tokens']:,} / {b['gen_total_tokens']:,} | {o['gen_prompt_tokens']:,} / {o['gen_completion_tokens']:,} / {o['gen_total_tokens']:,} | - |",
        f"| 请求墙钟 P50 / P95 | {sec(b['wall_p50'])} / {sec(b['wall_p95'])} | {sec(o['wall_p50'])} / {sec(o['wall_p95'])} | - |",
        f"| 全量 {n_all} 题程序状态 | `{b['statuses']}` | `{o['statuses']}` | - |",
        '',
        f"逐题覆盖变化（{n_ans} 题）：**{deltas.get('improved',0)} 增 / {deltas.get('tied',0)} 平 / {deltas.get('regressed',0)} 退**。",
        '',
        '## 2. LangSmith 与核验',
        '',
        f"- 远端实时 Trace 批量核验：`verified={(summary.get('remote_verification') or {}).get('verified')}`，span 数 `{(summary.get('remote_verification') or {}).get('finished_count')}/{(summary.get('remote_verification') or {}).get('span_count')}`，pending `{(summary.get('remote_verification') or {}).get('pending_events')}`。",
        f"- Dataset/Experiment 同步：`status={(summary.get('dataset_sync') or {}).get('status')}`；对照链接：{ls_url or 'pending'}",
    ]
    (out_dir / 'findings.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    bars = [
        (f'来源覆盖 ({n_ans}题)', b['answerable']['evidence_coverage'], o['answerable']['evidence_coverage']),
        (f'跨论文 ({n_cross}题)', b['cross_paper']['evidence_coverage'], o['cross_paper']['evidence_coverage']),
        (f'全覆盖比例 ({n_ans}题)', b['answerable']['all_units']/max(1, n_ans), o['answerable']['all_units']/max(1, n_ans)),
        (f'引用通过率 ({n_all}题)', 1 - b['citation_errors']/n_all, 1 - o['citation_errors']/n_all),
        (f'反例拒答 ({n_neg}题)', b['negative']['refused']/max(1, n_neg), o['negative']['refused']/max(1, n_neg)),
    ]
    svg = ['<svg viewBox="0 0 780 240" width="100%" style="max-width:780px;background:#fff;border:1px solid #e5e7eb;border-radius:8px">']
    for idx, (label, bv, ov) in enumerate(bars):
        x = 50 + idx * 145
        bh, oh = int((bv or 0)*150), int((ov or 0)*150)
        svg.append(f'<rect x="{x}" y="{185-bh}" width="42" height="{bh}" fill="#94a3b8" rx="3"/>')
        svg.append(f'<text x="{x+21}" y="{179-bh}" font-size="11" text-anchor="middle">{(bv or 0)*100:.1f}%</text>')
        svg.append(f'<rect x="{x+48}" y="{185-oh}" width="42" height="{oh}" fill="#2563eb" rx="3"/>')
        svg.append(f'<text x="{x+69}" y="{179-oh}" font-size="11" text-anchor="middle" fill="#1d4ed8">{(ov or 0)*100:.1f}%</text>')
        svg.append(f'<text x="{x+45}" y="208" font-size="11" text-anchor="middle">{html.escape(label)}</text>')
    svg.append('<rect x="460" y="10" width="12" height="12" fill="#94a3b8"/><text x="476" y="20" font-size="11">Legacy-Hybrid</text>')
    svg.append('<rect x="595" y="10" width="12" height="12" fill="#2563eb"/><text x="611" y="20" font-size="11">Production-Final</text>')
    svg.append('</svg>')

    cards = []
    for case in bench['cases']:
        cid = case['id']
        rb, ro = rows_by_key[(cid, ARMS[0])], rows_by_key[(cid, ARMS[1])]
        def panel(title, row):
            trace = row.get('trace_url') or ''
            tl = f'<a href="{html.escape(trace)}" target="_blank">Trace</a>' if trace else 'N/A'
            return (f"<div style='flex:1;min-width:300px;border:1px solid #e2e8f0;padding:10px;border-radius:6px;background:#f8fafc'>"
                    f"<h4>{html.escape(title)} · status=<code>{html.escape(str(row['status']))}</code> · cov={pct(row['metrics'].get('evidence_coverage'))} · cites={len(row.get('citations') or [])} · {tl}</h4>"
                    f"<pre style='white-space:pre-wrap;font-size:12px'>{html.escape(str(row.get('answer') or ''))}</pre></div>")
        cards.append(
            f"<details style='margin:8px 0;border:1px solid #cbd5e1;border-radius:6px;padding:8px'>"
            f"<summary><strong>{html.escape(cid)}</strong> [{html.escape(case['category'])}] {html.escape(case['question'])} — "
            f"Legacy: <code>{html.escape(str(rb['status']))}</code> ({pct(rb['metrics'].get('evidence_coverage'))}) → "
            f"Prod: <code>{html.escape(str(ro['status']))}</code> ({pct(ro['metrics'].get('evidence_coverage'))})</summary>"
            f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin-top:8px'>{panel(ARMS[0], rb)}{panel(ARMS[1], ro)}</div></details>"
        )
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(bench['version'])}</title>
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:1280px;margin:20px auto;padding:0 16px}}</style></head>
<body><h1>{html.escape(bench['version'])} 18 题全新未见泛化评测仪表板</h1>
<p>运行 ID: <code>{html.escape(summary['run_id'])}</code> · LangSmith: {f'<a href="{html.escape(ls_url)}" target="_blank">{html.escape(ls_url)}</a>' if ls_url else 'pending'}</p>
<h2>汇总指标对比</h2>{''.join(svg)}<h2>18 题逐题对比</h2>{''.join(cards)}</body></html>"""
    (out_dir / 'dashboard.html').write_text(page, encoding='utf-8')
    return out_dir


def execute(root, prepare_only=False, resume=None):
    bench, digest, _ = freeze(root)
    cfg = settings(root)
    recorder = HoldoutDataset(root, VERSION)
    if resume is not None:
        try:
            summary_path = Path(resume)
            status = recorder.sync_run(summary_path, 'full') if cfg.get('LANGSMITH_API_KEY') else dict(status='skipped_no_key')
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
            summary['dataset_sync'] = status
            atomic_json(summary_path, summary)
            render_report(root, summary_path)
            return status
        finally:
            recorder.close()
    if cfg.get('LANGSMITH_API_KEY'):
        try:
            recorder.sync_dataset()
        except Exception:
            recorder.status.update(status='pending_sync', error_type='sync_failed')
            write_json(recorder.status_path, recorder.status)
            recorder.close()
            raise RuntimeError('dataset_sync_required_before_model_calls') from None
    if prepare_only:
        recorder.close()
        print(json.dumps(dict(status='prepared', benchmark=VERSION, sha256=digest, cases=len(bench['cases'])), ensure_ascii=False), flush=True)
        return dict(status='prepared', benchmark=VERSION, sha256=digest)

    model_id = vector_metadata(root)['model_id']
    claim_vectors = load_aux_vectors(root / CLAIM_VECS_REL, model_id)
    snap = bench['graph_snapshot']
    expander = IsolatedGraph(root / snap['database'], snap['sha256'], claim_vectors=claim_vectors)
    navigator = MethodCardNavigator(root / CARDS_REL, root / SLOT_VECS_REL, model_id)

    run_id = uuid.uuid4().hex
    report_root = root / 'artifacts/reports/stage-4' / VERSION
    destination = report_root / 'runs' / run_id
    destination.mkdir(parents=True)
    workflow = Workflow(root, cfg, query_mode='cloud', graph_enabled=True, graph_expander=expander, method_cards=navigator)
    workflow.providers.client.close()
    provider = SharedQ00Providers(cfg, workflow.audit)
    workflow.providers = provider
    report = dict(run_id=run_id, started=now(), benchmark_sha256=digest, benchmark=VERSION,
                  status='running', arm_configs=deepcopy(ARM_CONFIGS), results=[])
    atomic_json(destination / 'summary.json', report)
    root_ids = []
    try:
        index = workflow.store.inspect()
        if index['counts'] != [dict(chunks=980, papers=14)] or any(r['state'] != 'ONLINE' for r in index['indexes']):
            raise RuntimeError('index_preflight_failed')
        rid = workflow.audit.start('[stage4 holdout shared GPU warmup metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        warm = workflow.audit.stage(rid, 'gpu_warmup', lambda: run_worker(root, cfg, 'rerank',
            [dict(text='Source evidence supports retrieval.')], query='source evidence', timeout=180))
        warm.pop('outputs', None)
        if warm.get('device') != 'cuda':
            raise RuntimeError('gpu_reranker_unavailable')
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(reranker=warm)))

        texts = [normalize(c['question']) for c in bench['cases']]
        if not workflow.compatible():
            raise RuntimeError('cloud_compatibility_gate_failed')
        rid = workflow.audit.start('[stage4 holdout shared cloud query-vector batch metadata]')
        root_ids.append(workflow.audit.live_requests[rid])
        vectors = workflow.audit.stage(rid, 'shared_query_embeddings', lambda: Providers.embedding(provider, rid, texts))
        provider.q00_vectors = dict(zip(texts, vectors))
        workflow.audit.finish(rid, dict(status='completed', retrieval_summary=dict(query_count=len(texts), vector_dimensions=1024)))

        for number, case in enumerate(bench['cases'], 1):
            order_arms = [ARMS[0], ARMS[1]] if number % 2 else [ARMS[1], ARMS[0]]
            for arm in order_arms:
                for key, val in ARM_CONFIGS[arm].items():
                    if key == 'query_planner':
                        workflow.query_planner_enabled = val
                    elif key == 'premise_check':
                        workflow.premise_check_enabled = val
                    elif key == 'use_method_cards':
                        workflow.method_cards = navigator if val else None
                    else:
                        setattr(workflow, key, val)
                req_started = time.monotonic()
                rid = workflow.audit.start(case['question'])
                root_ids.append(workflow.audit.live_requests[rid])
                state = dict(request_id=rid, question=case['question'], errors=[], citations=[], evidence=[],
                             graph_paths=[], usage=None, estimated_cost=None, model_name=None, status='running')
                timings = []
                def retrieve_pipeline():
                    for name in ('validate', 'retrieve', 'graph_expand', 'rerank', 'evidence'):
                        if state.get('status') in ('refused', 'error', 'invalid_input'):
                            break
                        began = time.monotonic()
                        state.update(getattr(workflow, name)(state))
                        timings.append(dict(name=name, seconds=time.monotonic() - began))
                    return dict(retrieval_summary=state.get('retrieval_summary'), status=state['status'],
                                errors=state['errors'], timings=timings)
                workflow.audit.stage(rid, 'retrieval_pipeline', retrieve_pipeline)
                if state['status'] == 'running' and case['generate']:
                    state.update(workflow.audit.stage(rid, 'generate', lambda: workflow.generate(state)))
                    state.update(workflow.audit.stage(rid, 'citations', lambda: workflow.citations(state)))
                result = {k: state.get(k) for k in ('request_id', 'status', 'answer', 'citations', 'premise_check',
                    'evidence', 'graph_paths', 'generation_paths', 'limitations', 'retrieval_summary', 'usage',
                    'model_name', 'errors', 'raw', 'ranked')}
                result.update(
                    case_id=case['id'], question=case['question'], category=case['category'], arm=arm,
                    order=order_arms.index(arm) + 1, generate_requested=case['generate'],
                    compute_timings=timings, retrieval_compute_seconds=sum(t['seconds'] for t in timings),
                    request_wall_seconds=time.monotonic() - req_started,
                    embedding_source='shared Q00 cloud vectors across arms; live planned subquery vectors for Production-Final',
                    stage_timings=[dict(r) for r in workflow.audit.conn.execute('SELECT name,seconds,status FROM stages WHERE request_id=? ORDER BY started', (rid,))],
                    provider_calls=[dict(r) for r in workflow.audit.conn.execute('SELECT provider,attempt,status,http_status,seconds,usage FROM calls WHERE request_id=? ORDER BY started', (rid,))],
                    criterion_source_coverage=criterion_source_coverage(case, [e['chunk_id'] for e in state['evidence']], bench['units']),
                )
                result['metrics'] = support_metrics([r['chunk_id'] for r in state.get('ranked', [])],
                    [e['chunk_id'] for e in state['evidence']], [bench['units'][u] for u in case['units']])
                workflow.audit.finish(rid, result)
                result['trace_url'] = workflow.audit.live.url(workflow.audit.live_requests[rid])
                workflow.audit.finish(rid, result)
                atomic_json(destination / (case['id'] + ('-prod.json' if arm == ARMS[1] else '-legacy.json')), result)
                report['results'].append(result)
                atomic_json(destination / 'summary.json', report)
                print(json.dumps(dict(case=case['id'], arm=arm, status=result['status'],
                    ev_cov=result['metrics']['evidence_coverage'], cites=len(result['citations']),
                    wall=round(result['request_wall_seconds'], 2)), ensure_ascii=False), flush=True)

        report['remote_verification'] = _verify_remote_batched_strict(workflow.audit.live, root_ids)
        report.update(status='completed', finished=now())
        atomic_json(destination / 'summary.json', report)
        atomic_json(report_root / 'latest.json', dict(directory=str(destination)))
    except Exception as exc:
        report.update(status='interrupted', error_code=type(exc).__name__, finished=now())
        atomic_json(destination / 'summary.json', report)
        raise
    finally:
        try:
            if cfg.get('LANGSMITH_API_KEY') and report['results']:
                report['dataset_sync'] = recorder.sync_run(destination / 'summary.json', 'full')
        except Exception as exc:
            report['dataset_sync'] = dict(status='pending_sync', error_type=type(exc).__name__)
            recorder.status.update(report['dataset_sync'])
            write_json(recorder.status_path, recorder.status)
        finally:
            atomic_json(destination / 'summary.json', report)
            if report['results']:
                render_report(root, destination / 'summary.json')
            recorder.close()
            workflow.close()
            expander.close()
            close_workers()
    print(json.dumps(dict(status=report['status'], directory=str(destination),
        remote_verified=(report.get('remote_verification') or {}).get('verified'),
        dataset_sync=(report.get('dataset_sync') or {}).get('status')), ensure_ascii=False), flush=True)
    return report
