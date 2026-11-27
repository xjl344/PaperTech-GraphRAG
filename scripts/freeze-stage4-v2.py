"""Build/check the source-grounded relation-focused development benchmark offline."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.audit import now
from papertech.corpus import load_corpus
from papertech.ingest import atomic_json
from papertech.settings import settings

TARGET = ROOT / 'artifacts/eval/stage-4/benchmark-v2'
V1 = ROOT / 'artifacts/eval/stage-4/benchmark-v1/benchmark.json'


# Gold comes from paper text, independently of whether the current graph has an edge.
# Each cross case needs sources from at least two distinct papers.
# (question, required units, analytical relation chain, expected synthesis, invalid inference)
RELATIONS = [
    ('比较 ToG 与 ToG-2：从问题到证据，LLM、实体关系和文档分别如何参与？画出两条检索流程，并引用两篇论文。',
     ['tog', 'tog2'], 'ToG → LLM 束搜索 → KG 路径；ToG-2 → 实体连接文档 → 图/上下文交替检索',
     'ToG 用 LLM 迭代束搜索探索 KG；ToG-2 以实体连接文档，并用文档上下文辅助图检索，两者工作流不同。',
     '不能只凭名称或工作流差异断言 ToG-2 在所有任务优于 ToG。'),
    ('比较 HippoRAG 与 RoG：查询概念、关系路径计划和实际证据分别处在什么位置？说明两种方法如何连接分散事实。',
     ['hippo', 'rog'], '查询概念 → PPR → 跨片段检索；关系路径计划 → KG 路径检索 → 推理',
     'HippoRAG 用查询概念作为 PPR 种子整合跨片段信息；RoG 先生成关系路径计划，再检索实际推理路径。',
     '不能把 RoG 的关系路径计划写成 PPR，也不能据共同目标推导技术继承。'),
    ('结合 KGP 和 CuriousLLM 原文，后者针对前者提出了什么增强？把多文档图、遍历代理、后续问题及其监督信号串起来，并区分作者评价与已验证事实。',
     ['kgp', 'curious'], 'KGP → 多文档图/遍历代理；CuriousLLM → 追问增强 → Follow-upQA',
     'KGP 构图并让代理收集段落；CuriousLLM 原文将自身描述为增强，引入追问机制及问题/证据到后续问题的训练信号。对 KGP 成本和幻觉的评价须归于 CuriousLLM 作者。',
     '不能反转增强方向，也不能把作者报告当成本系统复现实验结论。'),
    ('比较 StructGPT 与 LPKG：一个方法在回答时如何获得证据，另一个方法在训练时如何获得规划数据？说明 KG/结构化数据在两者中的不同角色。',
     ['struct', 'lpdata'], '结构化数据 → 接口读取 → 推理；KG → 规划训练数据 → 微调规划能力',
     'StructGPT 在推理时经接口迭代读取结构化证据；LPKG 从 KG 派生规划数据并微调模型。',
     '不能把推理时读取接口等同训练数据构建，也不能认为两者共享训练协议。'),
    ('ToG 和 RoG 都利用 KG 推理，为什么不能据此把两者都归为免训练方法？分别追踪 KG 在在线搜索和训练中的作用。',
     ['tog_training', 'rog'], 'ToG → 免额外训练的在线搜索；RoG → KG 蒸馏训练 + 路径检索',
     'ToG 声明无需额外训练；RoG 明确包括从 KG 蒸馏知识的训练，同时支持推理时接入其他 LLM。',
     '推理模块可接入任意 LLM 不等于整套方法没有训练。'),
    ('比较 ToG-2 与 LPKG：图知识分别怎样帮助文档证据检索和问题规划？说明二者发生在训练还是推理阶段。',
     ['tog2', 'lpdata'], 'ToG-2 → 推理时图/文档协作；LPKG → KG 规划数据 → 训练',
     'ToG-2 免训练地交替检索图和上下文；LPKG 以 KG 派生数据微调规划能力。',
     '不能因为都连接 KG 与 QA 就视为同一阶段或同一算法。'),
    ('比较 HippoRAG 与 KGP 的图表示：图从什么材料构造，检索时沿什么关联获取证据？说明二者为何不能直接共享一种“节点就是段落”的解释。',
     ['hippo', 'kgp'], '语料 → HippoRAG 无模式 KG → PPR；多文档 → KGP 段落/结构图 → 遍历代理',
     'HippoRAG 用 LLM 将语料转成无模式 KG、由查询概念启动 PPR；KGP 节点表示段落或文档结构，边为相似或结构关系。',
     '不能把 KGP 的节点定义直接套到 HippoRAG。'),
    ('G-Retriever 与 ToG-2 都用图帮助获取上下文，但它们选择证据的机制怎样不同？分别连接输入规模问题、相关子图选择以及实体和文档的协作。',
     ['pcst', 'grscale', 'tog2'], '大图上下文限制 → G-Retriever PCST 子图；实体/文档 → ToG-2 双向协作',
     'G-Retriever 用 PCST 表述相关子图检索以控制大图输入；ToG-2 交替进行图检索与上下文检索。',
     '不能据都用图就声称 ToG-2 使用 PCST，也不能声称两者实测资源相同。'),
    ('从 ToG 与 ToG-2 的评测段落出发，找出共同使用的 WebQSP 与 QALD10-en，分别给出“方法→数据集”的来源，再说明为什么这个连接不能证明优劣或继承。',
     ['togds', 'tog2ds'], 'ToG → WebQSP/QALD10-en ← ToG-2',
     '两篇均列出 WebQSP 和 QALD10-en；这是评测数据集关联，不是方法继承或受控性能比较。',
     '不能把共享数据集路径当成 IMPROVES_UPON 或因果关系。'),
    ('把 HippoRAG 与 Tree-of-Traversals 通过各自原文中的 2Wiki 测试集名称连接起来，再比较它们如何完成跨事实检索。保留数据集原始名称及设置差异。',
     ['hippods', 'totds', 'hippo', 'totbound'], 'HippoRAG → 2WikiMultiHopQA；Tree-of-Traversals → 2WikiMultiHop；PPR 对照动作树搜索',
     '保留两篇不同名称；HippoRAG 用 PPR，Tree-of-Traversals 搜索动作树。HippoRAG 使用抽取的验证集问题，Tree-of-Traversals 列出所用模型，不能默认协议一致。',
     '名称相近不证明划分、语料、底座和指标一致。'),
    ('沿“KG-GPT/RoG→MetaQA→跳数与指标/知识来源”比较两篇实验。RoG 中 Freebase 与 Wiki-Movies 分别承担什么角色？每个角色须给出原文。',
     ['kggptds', 'rogmeta'], 'KG-GPT → MetaQA 1/2/3-hop → Hits@1；RoG → MetaQA-3hop → Wiki-Movies；Freebase → 迁移起点',
     'KG-GPT 报告 MetaQA 各跳数 Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是预训练/迁移来源，扩展实验使用 1000 个训练样本。',
     '不能把 Freebase 写成该 MetaQA 测试 KG，也不能从不匹配实验协议直接判胜负。'),
    ('Tree-of-Traversals 的 MusicBrainz-x-Wikidata 与 LPKG 的 CLQA-Wiki 怎样分别连接到知识来源？虽然都涉及 Wikidata，二者考察的关系推理能力有何区别？',
     ['totmusic', 'lpbench'], 'MusicBrainz-x-Wikidata → MusicBrainz + Wikidata；CLQA-Wiki → Wikidata 子集 → 四类逻辑题',
     '前者要求跨两个 KG 综合推理；后者从 Wikidata 子集构建，覆盖 multi-hop、comparison、intersection、union。',
     '共享 Wikidata 不能推出同一题集或相同难度。'),
    ('HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 是什么关系？引用两篇的设置说明，判断能否直接用结果数字比较两种检索方法。',
     ['hippods', 'tog2ds'], 'HippoRAG → HotpotQA；ToG-2 → AdvHotpotQA → HotpotQA 挑战子集',
     'ToG-2 将 AdvHotpotQA 描述为 HotpotQA 的挑战子集；HippoRAG 抽取验证集并组成候选语料，ToG-2 使用 full Wiki，不能直接横比。',
     '不能把父数据集与子集视为相同测试协议。'),
    ('比较 ToG 与 ToG-2 对 Creak 及 QA 任务的评测指标，再结合两篇对知识来源/数据设置的说明，列出跨论文性能比较仍需核对的条件。',
     ['togds', 'tog2ds'], 'ToG → 各任务 Hits@1；ToG-2 → Creak/FEVER Acc. + 其他 EM；比较 → 协议核对',
     '按原文保留 ToG 所称 exact match accuracy (Hits@1)；ToG-2 对 Creak/FEVER 用 Acc.，其他用 EM，并说明 full Wiki。还需核对划分、底座、来源和提示条件。',
     '不能只凭相同或近似指标名宣布受控优劣，也不能补写 ToG 未提供的设置。'),
    ('比较 Tree-of-Traversals 与 CuriousLLM 如何表达“还要继续找证据”或“停止”。区分最大深度、最大扩展数、找到答案阈值和表示证据充分的特殊 token。',
     ['totbound', 'curious'], '动作树 → 阈值/深度/扩展预算；追问训练 → 缺失证据问题/充分证据 token',
     'Tree-of-Traversals 达阈值可停止，最大深度强制 done，最大扩展数返回 Cannot find answer；CuriousLLM 用追问或特殊 token 表示缺口/充分。',
     '不能把两种预算终止都写成成功，也不能把特殊 token 当成本项目已实现的停止器。'),
    ('MindMap 与 RoG 都讨论可解释推理。分别追踪其外部 KG、模型内部知识或关系计划怎样进入答案，说明一张可解释路径为何不自动保证答案正确。',
     ['mind', 'rog'], 'MindMap → 内隐知识 + 外部 KG → mind map；RoG → 关系计划 → 有效路径 → 推理',
     'MindMap 结合内隐与外部知识并展示思维图；RoG 用 KG 支持的关系计划检索路径。路径可追溯仍需核对每项结论是否受证据支持。',
     '不能把可解释性或作者的 faithful 表述等同所有答案已验证正确。'),
    ('STaRK 和 MindMap 都涉及医学相关任务：分别是什么类型的基准或方法、原文描述了什么医学场景？这些段落能否证明 MindMap 在 STaRK 上接受过评测？',
     ['stark', 'mind'], 'STaRK → 半结构检索基准 → 精准医疗；MindMap → KG 提示方法 → 医学 QA',
     'STaRK 是含精准医疗领域的检索基准，MindMap 是重点包含医学 QA 的方法；所引段落不足以建立 MindMap EVALUATED_ON STaRK。',
     '主题重合不能作为评测关系证据；不足以证明不等于证明从未评测。'),
    ('比较 KG-GPT 与 RoG：句子分割、图检索、关系路径规划分别属于哪套流程？把输入到证据再到推理的顺序写清楚。',
     ['kggpt', 'rog'], 'KG-GPT → 句子分割 → 图检索 → 推理；RoG → 关系计划 → 路径检索 → 推理',
     'KG-GPT 的三步为 Sentence Segmentation、Graph Retrieval、Inference；RoG 的三段为 planning、retrieval、reasoning，其中先生成关系路径计划。',
     '不能把共有检索/推理步骤当成相同规划器或继承证据。'),
    ('在 ToG、HippoRAG 与 RoG 中，分别找出“LLM 逐步探索图”“查询种子驱动图算法”“先规划关系路径再取证”的方法。每项给出一篇原文，并比较多跳关联发生在哪一步。',
     ['tog', 'hippo', 'rog'], 'ToG → 束搜索；HippoRAG → PPR；RoG → 关系计划/路径检索',
     '三种描述分别对应 ToG、HippoRAG、RoG；多跳关联分别通过交互搜索、一次 PPR 检索及计划约束的路径检索实现。',
     '不能因为都处理多跳就认为推理步骤或计算代价相同。'),
    ('比较 ToG-2、HippoRAG 与 KGP 如何把文档中的分散信息联系起来。分别说明图与文档的连接方式，以及检索最终怎样回到支持证据。',
     ['tog2', 'hippo', 'kgp'], '实体连接文档/上下文协作；语料抽图/PPR 跨片段；段落结构图/代理遍历',
     'ToG-2 用实体连接文档并交替检索；HippoRAG 从语料抽图并用 PPR 整合跨片段信息；KGP 用段落/结构节点及代理收集支持段落。',
     '不能把三种图的节点、边及检索过程当成同一表示。'),
    ('围绕“有限上下文或有限搜索预算下如何保留必要证据”，比较 G-Retriever、Tree-of-Traversals 与 CuriousLLM 的机制。哪些是子图选择，哪些是搜索边界，哪些是证据缺口信号？',
     ['grscale', 'totbound', 'curious'], '输入规模 → 子图选择；搜索空间 → 有界树搜索；证据缺口 → 追问/充分 token',
     'G-Retriever 选择相关子图；Tree-of-Traversals 限制深度和扩展；CuriousLLM 学习追问或输出证据充分信号。三者约束对象不同。',
     '不能没有同条件实验就声称任一机制必然最快或最省 Token。'),
    ('比较 LPKG、CuriousLLM 与 RoG 的训练信号和推理用途：图派生规划数据、问题与支持证据生成追问、KG 支持的关系路径分别属于谁？不能只回答三者都用了 KG。',
     ['lpdata', 'curious', 'rog'], 'KG → LPKG 规划数据；问题+证据 → CuriousLLM 追问；KG → RoG 关系路径计划',
     '逐项区分 LPKG 的 KG 派生规划数据、CuriousLLM Follow-upQA 的输入/目标，以及 RoG 的关系路径计划与 KG 蒸馏训练。',
     '不能把三种监督目标互换，也不能臆测完全相同的训练数据。'),
    ('ToG/ToG-R 的搜索宽度和深度怎样联系到 LLM 调用次数？再与 Tree-of-Traversals 的深度、扩展预算对照，说明为什么这些公式/上限不能直接换算成统一运行时排名。',
     ['togr', 'totbound'], 'ToG → 2ND+D+1；ToG-R → ND+D+1；Tree-of-Traversals → depth/expansions 边界',
     'ToG-R 用随机实体剪枝减少调用，公式如原文；Tree-of-Traversals 有不同动作树搜索及预算。调用公式、搜索上限与墙钟时延不是同一量。',
     '不能反转 ToG-R 与 ToG 的变体关系，也不能从不同预算直接推出实测速度。'),
    ('结合 LPKG 的 CLQA-Wiki 与 Tree-of-Traversals 的 2Wiki/MusicBrainz-x-Wikidata 描述，区分“多跳”“交并逻辑”“跨 KG”三种任务关系，并逐项绑定到相应证据。',
     ['lpbench', 'totds', 'totmusic'], 'CLQA-Wiki → 多跳/比较/交/并；2Wiki → 多跳；MusicBrainz-x-Wikidata → 跨 KG',
     'CLQA-Wiki 明列四类逻辑题，2Wiki 段描述多跳模板，MusicBrainz-x-Wikidata 要求结合两个 KG；任务属性不同。',
     '不能推断其他数据集绝不含交并题，也不能把跨 KG 与多跳逻辑视为互斥概念。'),
]

NEGATIVES = [
    ('因为 HippoRAG 和 RoG 都处理图上多跳推理，能否据两篇的方法描述断言“RoG 直接继承了 HippoRAG 的 PPR”？请检查关系和方向。',
     ['hippo', 'rog'], 'unsupported_lineage', '原文分别支持 PPR 与关系路径规划，不能建立所声称的继承关系。'),
    ('ToG 与 ToG-2 都使用 WebQSP，因此“ToG-2 在所有数据集和所有底座上严格优于 ToG”成立吗？请从共享数据集关系的证据边界作答。',
     ['togds', 'tog2ds'], 'unsupported_universal_claim', '共同数据集不能推出全称优越性；需配对实验与完整适用条件。'),
    ('KGP 和 HippoRAG 都从文档获得图，所以“它们的每个图节点都是一个段落，边都是段落语义相似度”成立吗？分别核对原文。',
     ['kgp', 'hippo'], 'representation_conflation', 'KGP 有段落/结构节点与多种边，HippoRAG 是语料抽取的无模式 KG，不能套用统一节点/边定义。'),
    ('KG-GPT 和 RoG 都评测 MetaQA；RoG 又写了 transfer from Freebase，是否可推出两篇 MetaQA 实验的测试 KG 都是 Freebase？',
     ['kggptds', 'rogmeta'], 'training_test_role_conflation', 'RoG 明确 MetaQA-3hop 基于 Wiki-Movies；Freebase 为迁移来源，不能把共享基准和训练来源拼成测试 KG。'),
    ('仅因 STaRK 有精准医疗领域、MindMap 讨论医学 QA，能否建立“MindMap→EVALUATED_ON→STaRK”并报告测试分数？',
     ['stark', 'mind'], 'unsupported_evaluation_edge', '两篇相关段落没有提供该评测关系或分数；说明缺证据，不捏造数值，也不声称证明从未测试。'),
    ('请给出 NebulaGraphRAG-2099 继承 HippoRAG 后，在 LunarQA-2099 上相对 RoG 提升的官方精确分数，并画出继承链。',
     [], 'no_corpus_answer', '没有这些虚构方法、基准和分数的语料依据，应拒绝编造继承链与数值。'),
    ('CuriousLLM 说自己增强了 KGP，是否意味着“KGP 以 CuriousLLM 的 Follow-upQA 为训练来源”？请结合两篇原文检查方向。',
     ['kgp', 'curious'], 'reversed_enhancement', 'CuriousLLM 描述自身的增强及 Follow-upQA；不能反向推出 KGP 使用后者训练数据。'),
    ('Tree-of-Traversals 达到 max depth 和 max expansions 时，都像 CuriousLLM 的特殊 token 一样表示“证据已经充分、答案正确”吗？',
     ['totbound', 'curious'], 'termination_success_conflation', '最大深度强制 done、最大扩展数返回无法找到答案；CuriousLLM 的 token 是充分证据信号，不能等同成功或正确性保证。'),
]

# Explicitly reviewed alternatives, including the previous round's missed sources.
ALTERNATIVES = {
    'tog': ['chunk_d6a1257a27b9a4e3fd151b8c87ebf491'],
    'tog2': ['chunk_c9284a24e2b28b371a7e43a2bc6ae3c2'],
    'lpdata': ['chunk_cea61ca4533fd32e6f63ea730fb194ab'],
    'struct': ['chunk_bd4734d2765e2147cac924fe8ba38d85'],
}


def build():
    corpus, papers, chunks = load_corpus(ROOT)
    cmap = {c['chunk_id']: c for c in chunks}
    old = json.loads(V1.read_text(encoding='utf-8'))
    units = deepcopy(old['units'])
    # Keyword co-occurrence alone does not establish complete factual support.
    for key, unit in units.items():
        unit['known_support_chunks'] = [unit['primary_chunk']] + ALTERNATIVES.get(key, [])
        unit['support_review'] = 'Codex source review; non-exhaustive; not independent human annotation'
        unit['support_sources'] = [dict(chunk_id=cid, paper_id=cmap[cid]['paper_id'],
            page_start=cmap[cid]['page_start'], page_end=cmap[cid]['page_end'],
            text_sha256=cmap[cid]['text_sha256'], source_text=cmap[cid]['text'])
            for cid in unit['known_support_chunks']]
    # A mechanism paragraph is not sufficient evidence for a training-free claim.
    units['tog_training'] = deepcopy(units['tog'])
    units['tog_training'].update(id='tog_training',
        answer_point='ToG 将自身描述为 training-free，支持即插即用且无需额外训练。',
        known_support_chunks=[units['tog']['primary_chunk']],
        support_sources=units['tog']['support_sources'][:1])
    units['tog']['answer_point'] = 'ToG 将 LLM 当作代理，迭代执行 KG beam search，探索实体、关系和推理路径。'
    units['struct']['answer_point'] = 'StructGPT 通过专门接口迭代读取结构化证据，再让 LLM 根据已取得信息推理。'
    units['togds']['answer_point'] += '原文称各数据集采用 exact match accuracy (Hits@1)。'
    units['tog2ds']['answer_point'] += 'AdvHotpotQA 是 HotpotQA 挑战子集；FEVER/Creak 用 Acc.，其他用 EM；知识来源为 full Wikipedia/Wikidata。'
    units['hippods']['answer_point'] += '每个验证集取 1000 题，将对应支持和干扰段落组成检索语料。'
    units['totbound']['answer_point'] += '找到超过阈值的答案可停止；max depth 强制进入 done，与 max expansions 的失败终止不同。'
    units['curious']['answer_point'] += '作者明确将 CuriousLLM 描述为针对 KGP 的增强；其成本/幻觉评价归属于作者报告。'
    units['rog']['answer_point'] += '包含 KG 知识蒸馏训练；推理时可接入其他 LLM 不表示整套方法免训练。'
    units['rogmeta']['answer_point'] += 'Freebase 是迁移训练来源，不是该 MetaQA-3hop 的测试知识图谱。'
    cases = []
    base = [('F01', 'fact', 'G-Retriever 把相关子图检索形式化成什么优化问题？', 'pcst'),
            ('F02', 'fact', 'KG-GPT 的三个主要处理步骤是什么？', 'kggpt'),
            ('F03', 'fact', 'STaRK 是什么类型的基准，覆盖哪三个应用领域？', 'stark'),
            ('F04', 'fact', 'Roadmap 将 LLM 与 KG 的融合归纳为哪三类路线？', 'roadmap'),
            ('P01', 'paraphrase', 'HippoRAG 怎样从查询概念出发，在一次检索中联系分散的段落？', 'hippo'),
            ('P02', 'paraphrase', 'RoG 怎样先安排关系路线，再获取实际证据来回答问题？', 'rog'),
            ('P03', 'paraphrase', 'Tree-of-Traversals 怎样限制搜索，以及不同停止条件分别意味着什么？', 'totbound'),
            ('P04', 'paraphrase', 'LPKG 怎样利用 KG 获得规划训练信号，从而帮助复杂问题的检索？', 'lpdata')]
    for cid, category, question, unit in base:
        cases.append(dict(id=cid, category=category, question=question, units=[unit],
            answerable=True, negative_kind=None, generate=False, min_source_papers=1,
            reasoning_chain=None, expected_answer=units[unit]['answer_point'], must_not_claim=None))
    for n, (question, keys, chain, answer, invalid) in enumerate(RELATIONS, 1):
        cases.append(dict(id=f'R{n:02}', category='cross', question=question, units=keys,
            answerable=True, negative_kind=None, generate=True, min_source_papers=2,
            reasoning_chain=chain, expected_answer=answer, must_not_claim=invalid,
            relation_review=dict(evidence='必须覆盖全部必要事实并引用每篇所需原文',
                semantics='逐项检查关系方向、实体角色、任务/实验条件',
                synthesis='区分原文直接关系与跨来源分析，不将分析链冒充已入图事实',
                uncertainty='缺任何必要环节须部分回答/说明缺口，不补写关系')))
    for n, (question, keys, kind, answer) in enumerate(NEGATIVES, 1):
        cases.append(dict(id=f'N{n:02}', category='negative', question=question, units=keys,
            answerable=False, negative_kind=kind, generate=True,
            min_source_papers=2 if keys else 0, reasoning_chain=None,
            expected_answer=answer, must_not_claim='不得认可题干中未经支持的关系或编造数值。'))
    for case in cases:
        case['source_papers'] = sorted({units[k]['paper_id'] for k in case['units']})
    cfg = settings(ROOT)
    controls = deepcopy(old['controls'])
    controls['generation_subset'] = [c['id'] for c in cases if c['generate']]
    controls['generation_policy'] = '基础 8 题仅检索；24 道关系题与 8 道反例按证据门控生成，最多 64 次配对生成调用。'
    return dict(version='benchmark-v2', frozen_at=now(), corpus_id=corpus,
        papers=len(papers), chunks=len(chunks), cases=cases, units=units,
        author='Codex 原文核查；非独立人工金标',
        prior_exposure='关系导向的开发集，包含已知失败题及相近问题，不是未见测试集；不能与 v1 总分直接比较。',
        source_benchmark_sha256=hashlib.sha256(V1.read_bytes()).hexdigest(),
        models={k: cfg.get(k) for k in old['models']}, controls=controls,
        scoring=dict(primary='沿用 SupportRecall@5；事实单元内支持来源 OR，必要事实单元之间 AND。',
            secondary=old['scoring']['secondary'], denominator='32 道可回答题；其中 24 道跨文本题另报；8 反例单列，不计召回总分。',
            relevance='仅原文核查后的有限支持池；没有穷举所有等价来源，池外不等于不相关。',
            latency=old['scoring']['latency'], p95='按各类别及全部可回答题分别计算，单次小样本不表示 SLA。',
            answer_review='R01—R24、N01—N08 两组均逐项核对预期答案、全部来源、关系方向/角色与缺口表达；不以引用格式代替语义核查。',
            relation_gold='reasoning_chain 为人工可审阅的分析提纲，不是生产图路径金标；共享基准、分析比较不自动对应图谱 Schema 边。',
            interpretation='分别报告基础、跨文本、反例表现；新旧题集分布不同，不能由总分变化推导系统改善或 Graph 胜出。'),
        code_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'src/papertech').glob('*.py')) + [Path(__file__)]})


def validate(bench):
    corpus, papers, chunks = load_corpus(ROOT)
    cmap = {c['chunk_id']: c for c in chunks}
    if (bench['corpus_id'], bench['papers'], bench['chunks']) != (corpus, len(papers), len(chunks)):
        raise ValueError('benchmark_corpus_mismatch')
    if hashlib.sha256(V1.read_bytes()).hexdigest() != bench['source_benchmark_sha256']:
        raise ValueError('v1_benchmark_changed')
    cases = bench['cases']
    if len({c['id'] for c in cases}) != len(cases) or len({c['question'] for c in cases}) != len(cases):
        raise ValueError('duplicate_case')
    categories = Counter(c['category'] for c in cases)
    if categories != Counter(fact=4, paraphrase=4, cross=24, negative=8):
        raise ValueError('category_distribution_changed')
    for unit in bench['units'].values():
        if unit['primary_chunk'] not in unit['known_support_chunks']:
            raise ValueError('primary_source_missing')
        if unit['source_text'] != cmap[unit['primary_chunk']]['text']:
            raise ValueError('primary_text_changed')
        if [s['chunk_id'] for s in unit['support_sources']] != unit['known_support_chunks']:
            raise ValueError('support_snapshot_mismatch')
        for source in unit['support_sources']:
            chunk = cmap[source['chunk_id']]
            if chunk['content_kind'] == 'references' or chunk['paper_id'] != unit['paper_id']:
                raise ValueError('foreign_or_reference_source')
            for key in ('paper_id', 'page_start', 'page_end', 'text_sha256', 'source_text'):
                if source[key] != chunk['text' if key == 'source_text' else key]:
                    raise ValueError('support_source_changed:' + key)
    used_papers = set()
    for case in cases:
        actual = sorted({bench['units'][key]['paper_id'] for key in case['units']})
        if actual != case['source_papers'] or len(actual) < case['min_source_papers']:
            raise ValueError('cross_case_missing_sources:' + case['id'])
        if case['answerable'] and not case['units']:
            raise ValueError('answerable_without_source')
        if case['category'] == 'cross' and (not case['reasoning_chain'] or not case['must_not_claim']):
            raise ValueError('missing_relation_rubric')
        used_papers.update(actual)
    if len(used_papers) != len(papers):
        raise ValueError('paper_coverage_incomplete')
    if bench['controls']['generation_subset'] != [c['id'] for c in cases if c['generate']]:
        raise ValueError('generation_subset_mismatch')
    return dict(status='verified', cases=len(cases), categories=dict(categories),
        cross_paper_cases=24, cross_share_of_answerable=0.75, source_papers=len(used_papers),
        units=len(bench['units']), reviewed_supports=sum(len(u['known_support_chunks']) for u in bench['units'].values()),
        generation_pairs=sum(c['generate'] for c in cases), external_calls=0)


def render(bench):
    lines = ['# 阶段 4 关系导向题集 v2', '',
        '40 道题：4 道事实、4 道改写、24 道跨文本关系、8 道反例。可回答题中跨文本占 75%；24 道跨文本题均需要至少两篇不同论文的原文，部分需要三篇。', '',
        '这是接触过语料和既有失败的开发集。来源由 Codex 核查，不等同独立人工金标。v1 的题目、分数和失败记录保留，新旧总分不可直接比较。', '',
        '## 运行与检查', '', '在项目根目录执行；以下检查只读语料、无需启动 Neo4j 或调用模型：', '',
        '```powershell', "$env:PYTHONPATH = (Join-Path $PWD '.venv\\Lib\\site-packages') + ';' + (Join-Path $PWD 'src')",
        'python -X utf8 scripts/freeze-stage4-v2.py --check', '```', '',
        '需要重新评测时，显式选择 v2（会调用 Cloudflare 与 DeepSeek；最多 64 次生成请求，不在本次题集修改中执行）：', '',
        '```powershell', 'python -X utf8 scripts/eval-stage4.py --benchmark benchmark-v2', '```', '',
        'v2 原始结果写入 `artifacts/reports/stage-4/benchmark-v2/`；原来的 `report-stage4.py` 仍只负责 v1 报表。', '',
        '每轮对照会先创建并核对 LangSmith Dataset，再把两组结果作为 Experiment 关联到同一题目。离线题单与上传状态保存在本目录，上传失败只补传已有结果。', '',
        '## 判读规则', '',
        '- 基础题仅评检索；跨文本题和反例按证据门控生成，两组设置一致。',
        '- 每题必要事实必须齐全：一方证据不能代替另一方；引用有效不等于关系成立。',
        '- 按关系方向、实体角色、来源覆盖和缺口表达逐项核查；反例可用证据纠正前提，无须一律拒答。',
        '- 分别报告基础题、跨文本题和反例；不预设 Graph 胜出，也不为当前已入图关系定制金标。',
        '- 分析链是评分提纲，不是生产图边或完整路径金标；“共同数据集”不能推出继承、因果或性能优越。',
        '- 支持池采用逐项核查的原文，不按关键词共现自动扩展；尚未穷举全部等价来源，池外材料需另行审阅。', '',
        '## 题目与预期关系', '']
    for c in bench['cases']:
        lines += [f"### {c['id']} · {c['category']}", '', c['question'], '',
                  f"预期要点：{c['expected_answer']}", '']
        if c['reasoning_chain']:
            lines += [f"关系提纲：{c['reasoning_chain']}", '']
        if c['must_not_claim']:
            lines += [f"判读边界：{c['must_not_claim']}", '']
        for key in c['units']:
            u = bench['units'][key]
            lines.append(f"- `{key}`：{u['title']}，PDF 第 {u['page_start']}—{u['page_end']} 页；`{u['primary_chunk']}`。")
        lines.append('')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify the frozen v2 benchmark without model calls')
    args = parser.parse_args()
    if args.check:
        raw = (TARGET / 'benchmark.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != (TARGET / 'benchmark.sha256').read_text().strip():
            raise ValueError('benchmark_modified')
        bench = json.loads(raw)
        for name, expected in bench['code_sha256'].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise ValueError('frozen_code_changed:' + name)
        if (TARGET / 'questions.md').read_text(encoding='utf-8') != render(bench):
            raise ValueError('readable_questions_differ')
        print(json.dumps(validate(bench), ensure_ascii=False))
        return
    if TARGET.exists():
        raise RuntimeError('frozen_benchmark_exists_no_overwrite')
    bench = build()
    result = validate(bench)
    TARGET.mkdir(parents=True)
    atomic_json(TARGET / 'benchmark.json', bench)
    digest = hashlib.sha256((TARGET / 'benchmark.json').read_bytes()).hexdigest()
    (TARGET / 'benchmark.sha256').write_text(digest + '\n', encoding='ascii')
    (TARGET / 'questions.md').write_text(render(bench), encoding='utf-8')
    print(json.dumps(dict(result, status='frozen', sha256=digest), ensure_ascii=False))


if __name__ == '__main__':
    main()
