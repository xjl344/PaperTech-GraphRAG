"""Freeze a source-verified v3 benchmark and build its isolated evidence graph."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus
from papertech.ingest import atomic_json
from papertech.kg import locate_quote

TARGET = ROOT / 'artifacts/eval/stage-4/benchmark-v3'
V2 = ROOT / 'artifacts/eval/stage-4/benchmark-v2/benchmark.json'
VERSION = 'benchmark-v3'


SCHEMA = {
    'schema_version': 'papertech-evidence-graph-v3',
    'description': 'Question-focused, source-backed academic evidence graph. Every edge is a claim with exact source provenance.',
    'node_types': ['Paper', 'Method', 'Problem', 'Stage', 'Component', 'Algorithm', 'Optimization', 'GraphComponent',
        'Dataset', 'KnowledgeBase', 'Task', 'Metric', 'EvaluationSetting', 'TrainingSignal', 'TrainingMode', 'Benefit', 'Formula', 'Parameter',
        'StopCondition', 'Outcome', 'GraphRepresentation', 'NodeType', 'EdgeType', 'Taxonomy', 'Category',
        'EvidenceSignal', 'QuestionType', 'Parameter'],
    'relationship_signatures': [
        ['Paper', 'PROPOSES', 'Method'],
        ['Method', 'ADDRESSES', 'Problem'],
        ['Method', 'HAS_STAGE', 'Stage'], ['Stage', 'PRECEDES', 'Stage'],
        ['Stage', 'USES_COMPONENT', 'Component'], ['Method', 'USES_COMPONENT', 'Component'],
        ['Stage', 'CONNECTS', 'Component'], ['Component', 'CONNECTS', 'Component'],
        ['Method', 'USES_ALGORITHM', 'Algorithm'], ['Method', 'FORMULATES_AS', 'Optimization'],
        ['Optimization', 'SELECTS', 'GraphComponent'], ['GraphComponent', 'CONNECTS', 'Component'],
        ['Algorithm', 'USES_INPUT', 'Component'],
        ['Algorithm', 'CONNECTS', 'Component'], ['Algorithm', 'RETRIEVES_FROM', 'KnowledgeBase'],
        ['Method', 'CONNECTS', 'Component'],
        ['Method', 'ALTERNATES', 'Component'], ['Method', 'RETRIEVES_FROM', 'KnowledgeBase'],
        ['Method', 'EVALUATED_ON', 'Dataset'], ['Dataset', 'DERIVED_FROM', 'Dataset'],
        ['Dataset', 'USES_KNOWLEDGE_BASE', 'KnowledgeBase'], ['Dataset', 'HAS_TASK', 'Task'],
        ['Method', 'TARGETS_TASK', 'Task'],
        ['Method', 'REPORTS_METRIC', 'Metric'], ['EvaluationSetting', 'USES_DATASET', 'Dataset'],
        ['EvaluationSetting', 'USES_KNOWLEDGE_BASE', 'KnowledgeBase'],
        ['EvaluationSetting', 'REPORTS_METRIC', 'Metric'],
        ['EvaluationSetting', 'HAS_SAMPLE_SETTING', 'Parameter'],
        ['Method', 'USES_EVALUATION_SETTING', 'EvaluationSetting'],
        ['Method', 'TRAINED_WITH', 'TrainingSignal'], ['Method', 'DERIVES_TRAINING_DATA_FROM', 'KnowledgeBase'],
        ['Method', 'USES_TRAINING_MODE', 'TrainingMode'], ['Method', 'USES_TRAINING_SIGNAL', 'TrainingSignal'],
        ['Method', 'ENHANCES', 'Method'], ['Method', 'VARIANT_OF', 'Method'],
        ['Method', 'CLAIMS_BENEFIT', 'Benefit'], ['Method', 'HAS_CALL_BOUND', 'Formula'],
        ['Method', 'HAS_GRAPH_REPRESENTATION', 'GraphRepresentation'],
        ['GraphRepresentation', 'HAS_NODE_TYPE', 'NodeType'], ['GraphRepresentation', 'HAS_EDGE_TYPE', 'EdgeType'],
        ['Method', 'USES_AGENT', 'Component'], ['Component', 'COLLECTS', 'Component'],
        ['Method', 'GENERATES', 'EvidenceSignal'], ['EvidenceSignal', 'USES_INPUT', 'Component'],
        ['EvidenceSignal', 'HAS_TARGET', 'Component'], ['Method', 'HAS_STOP_CONDITION', 'StopCondition'],
        ['StopCondition', 'RETURNS', 'Outcome'], ['Parameter', 'CONNECTS', 'Outcome'],
        ['TrainingSignal', 'CONNECTS', 'Component'], ['Method', 'BOUNDED_BY', 'Parameter'],
        ['Paper', 'CLASSIFIES', 'Taxonomy'], ['Taxonomy', 'HAS_CATEGORY', 'Category'],
        ['Dataset', 'HAS_QUESTION_TYPE', 'QuestionType'], ['Method', 'COMPARES_WITH', 'Method'],
        ['Method', 'IMPROVES_UPON', 'Method'],
    ],
    'provenance': ['paper_id', 'title', 'source_relative_path', 'source_sha256', 'parse_id', 'chunk_id',
        'page_start', 'page_end', 'source_spans', 'text_sha256', 'evidence_quote', 'claim_kind', 'review_status'],
    'claim_policy': 'Exact quote must be a substring of the validated body chunk. Curated normalization never implies an unsupported causal, lineage, evaluation, or universal-performance claim.',
}


# Each path is an ordered list of (subject_type, subject, predicate, object_type, object).
# These are curated relations, each backed by the unit's frozen full source chunk.
UNIT_PATHS = {
    'pcst': [
        [('Method','G-Retriever','FORMULATES_AS','Optimization','Prize-Collecting Steiner Tree'),
         ('Optimization','Prize-Collecting Steiner Tree','SELECTS','GraphComponent','relevant subgraph')],
    ],
    'kggpt': [
        [('Method','KG-GPT','HAS_STAGE','Stage','Sentence Segmentation'),
         ('Stage','Sentence Segmentation','PRECEDES','Stage','Graph Retrieval'),
         ('Stage','Graph Retrieval','PRECEDES','Stage','Inference')],
    ],
    'struct': [
        [('Method','StructGPT','USES_COMPONENT','Component','dedicated interface'),
         ('Component','dedicated interface','CONNECTS','Component','structured evidence'),
         ('Component','structured evidence','CONNECTS','Component','LLM reasoning')],
    ],
    'stark': [
        [('Dataset','STaRK','HAS_TASK','Task','product search'),
         ('Dataset','STaRK','HAS_TASK','Task','academic paper search'),
         ('Dataset','STaRK','HAS_TASK','Task','precision medicine retrieval')],
    ],
    'roadmap': [
        [('Paper','Unifying Large Language Models and Knowledge Graphs: A Roadmap','CLASSIFIES','Taxonomy','LLM-KG integration'),
         ('Taxonomy','LLM-KG integration','HAS_CATEGORY','Category','KG-enhanced LLMs'),
         ('Taxonomy','LLM-KG integration','HAS_CATEGORY','Category','LLM-augmented KGs'),
         ('Taxonomy','LLM-KG integration','HAS_CATEGORY','Category','Synergized LLMs + KGs')],
    ],
    'totmusic': [
        [('Method','Tree-of-Traversals','EVALUATED_ON','Dataset','MusicBrainz-x-Wikidata'),
         ('Dataset','MusicBrainz-x-Wikidata','USES_KNOWLEDGE_BASE','KnowledgeBase','MusicBrainz'),
         ('Dataset','MusicBrainz-x-Wikidata','USES_KNOWLEDGE_BASE','KnowledgeBase','Wikidata'),
         ('Dataset','MusicBrainz-x-Wikidata','HAS_TASK','Task','109 cross-KG questions')],
    ],
    'lpbench': [
        [('Dataset','CLQA-Wiki','DERIVED_FROM','Dataset','Wikidata subset'),
         ('Dataset','CLQA-Wiki','HAS_QUESTION_TYPE','QuestionType','multi-hop'),
         ('Dataset','CLQA-Wiki','HAS_QUESTION_TYPE','QuestionType','comparison'),
         ('Dataset','CLQA-Wiki','HAS_QUESTION_TYPE','QuestionType','intersection'),
         ('Dataset','CLQA-Wiki','HAS_QUESTION_TYPE','QuestionType','union')],
    ],
    'mind': [
        [('Method','MindMap','USES_COMPONENT','Component','LLM implicit knowledge'),
         ('Method','MindMap','RETRIEVES_FROM','KnowledgeBase','external knowledge graph'),
         ('Method','MindMap','USES_COMPONENT','Component','mind map reasoning path'),
         ('Method','MindMap','TARGETS_TASK','Task','medical question answering')],
    ],
    'tog2': [
        [('Method','ToG-2','CONNECTS','Component','entities linked to documents'),
         ('Method','ToG-2','ALTERNATES','Component','graph retrieval'),
         ('Method','ToG-2','ALTERNATES','Component','context retrieval'),
         ('Component','graph retrieval','CONNECTS','Component','context retrieval')],
    ],
    'hippo': [
        [('Method','HippoRAG','USES_COMPONENT','Component','LLM corpus transformation'),
         ('Component','LLM corpus transformation','CONNECTS','Component','schemaless knowledge graph'),
         ('Method','HippoRAG','USES_ALGORITHM','Algorithm','Personalized PageRank'),
         ('Algorithm','Personalized PageRank','USES_INPUT','Component','query concepts as seeds'),
         ('Algorithm','Personalized PageRank','CONNECTS','Component','cross-passage evidence')],
    ],
    'curious': [
        [('Method','CuriousLLM','ENHANCES','Method','KGP'),
         ('Method','CuriousLLM','GENERATES','EvidenceSignal','follow-up question'),
         ('EvidenceSignal','follow-up question','USES_INPUT','Component','question and evidence'),
         ('EvidenceSignal','follow-up question','HAS_TARGET','Component','next question'),
         ('Method','CuriousLLM','GENERATES','EvidenceSignal','evidence-sufficient special token')],
    ],
    'rog': [
        [('Method','RoG','HAS_STAGE','Stage','planning'),
         ('Stage','planning','CONNECTS','Component','KG-constrained relation path plan'),
         ('Method','RoG','HAS_STAGE','Stage','retrieval'),
         ('Stage','retrieval','CONNECTS','Component','valid reasoning paths'),
         ('Method','RoG','TRAINED_WITH','TrainingSignal','KG knowledge distillation')],
    ],
    'kgp': [
        [('Method','KGP','HAS_GRAPH_REPRESENTATION','GraphRepresentation','document knowledge graph'),
         ('GraphRepresentation','document knowledge graph','HAS_NODE_TYPE','NodeType','passage'),
         ('GraphRepresentation','document knowledge graph','HAS_NODE_TYPE','NodeType','document structure'),
         ('GraphRepresentation','document knowledge graph','HAS_EDGE_TYPE','EdgeType','lexical or semantic similarity'),
         ('GraphRepresentation','document knowledge graph','HAS_EDGE_TYPE','EdgeType','intra-document structure'),
         ('Method','KGP','USES_AGENT','Component','LLM graph traversal agent'),
         ('Component','LLM graph traversal agent','COLLECTS','Component','supporting passages')],
    ],
    'totbound': [
        [('Method','Tree-of-Traversals','HAS_STOP_CONDITION','StopCondition','node value exceeds answer threshold'),
         ('StopCondition','node value exceeds answer threshold','RETURNS','Outcome','answer found'),
         ('Method','Tree-of-Traversals','BOUNDED_BY','Parameter','max depth'),
         ('Parameter','max depth','CONNECTS','Outcome','forced transition to done'),
         ('Method','Tree-of-Traversals','BOUNDED_BY','Parameter','max expansions'),
         ('Parameter','max expansions','CONNECTS','Outcome','Cannot find answer')],
    ],
    'grscale': [
        [('Method','G-Retriever','FORMULATES_AS','Optimization','Prize-Collecting Steiner Tree'),
         ('Optimization','Prize-Collecting Steiner Tree','SELECTS','GraphComponent','relevant subgraph'),
         ('GraphComponent','relevant subgraph','CONNECTS','Component','bounded LLM context')],
    ],
    'lpdata': [
        [('Method','LPKG','DERIVES_TRAINING_DATA_FROM','KnowledgeBase','knowledge graph'),
         ('Method','LPKG','USES_TRAINING_SIGNAL','TrainingSignal','planning data'),
         ('TrainingSignal','planning data','CONNECTS','Component','small model fine-tuning'),
         ('Method','LPKG','HAS_STAGE','Stage','complex QA planning')],
    ],
    'tog': [
        [('Method','ToG','USES_AGENT','Component','LLM agent'),
         ('Method','ToG','USES_ALGORITHM','Algorithm','iterative beam search'),
         ('Algorithm','iterative beam search','RETRIEVES_FROM','KnowledgeBase','knowledge graph'),
         ('Algorithm','iterative beam search','CONNECTS','Component','entity and relation paths')],
    ],
    'tog_training': [
        [('Method','ToG','USES_TRAINING_MODE','TrainingMode','training-free'),
         ('Method','ToG','USES_COMPONENT','Component','plug-and-play across LLMs and KGs')],
    ],
    'togr': [
        [('Method','ToG-R','VARIANT_OF','Method','ToG'),
         ('Method','ToG-R','USES_COMPONENT','Component','random entity pruning'),
         ('Method','ToG-R','CLAIMS_BENEFIT','Benefit','lower LLM-call cost and reasoning time'),
         ('Method','ToG-R','CLAIMS_BENEFIT','Benefit','reduced risk with unfamiliar intermediate entities'),
         ('Method','ToG','USES_COMPONENT','Component','LLM-based entity pruning'),
         ('Method','ToG','HAS_CALL_BOUND','Formula','2ND + D + 1 LLM calls'),
         ('Method','ToG-R','HAS_CALL_BOUND','Formula','ND + D + 1 LLM calls')],
    ],
    'togds': [
        [('Method','ToG','EVALUATED_ON','Dataset','WebQSP'),
         ('Method','ToG','EVALUATED_ON','Dataset','QALD10-en'),
         ('Method','ToG','EVALUATED_ON','Dataset','Creak'),
         ('Method','ToG','REPORTS_METRIC','Metric','exact match accuracy (Hits@1)')],
    ],
    'tog2ds': [
        [('Method','ToG-2','EVALUATED_ON','Dataset','WebQSP'),
         ('Method','ToG-2','EVALUATED_ON','Dataset','QALD10-en'),
         ('Method','ToG-2','EVALUATED_ON','Dataset','AdvHotpotQA'),
         ('Method','ToG-2','EVALUATED_ON','Dataset','FEVER'),
         ('Method','ToG-2','EVALUATED_ON','Dataset','Creak'),
         ('Dataset','AdvHotpotQA','DERIVED_FROM','Dataset','HotpotQA'),
         ('EvaluationSetting','ToG-2 evaluation','USES_KNOWLEDGE_BASE','KnowledgeBase','full Wikipedia and Wikidata'),
         ('EvaluationSetting','ToG-2 evaluation','REPORTS_METRIC','Metric','Accuracy on FEVER and Creak'),
         ('EvaluationSetting','ToG-2 evaluation','REPORTS_METRIC','Metric','EM on other datasets'),
         ('Method','ToG-2','USES_EVALUATION_SETTING','EvaluationSetting','ToG-2 evaluation')],
    ],
    'hippods': [
        [('Method','HippoRAG','EVALUATED_ON','Dataset','MuSiQue (answerable)'),
         ('Method','HippoRAG','EVALUATED_ON','Dataset','2WikiMultiHopQA'),
         ('Method','HippoRAG','EVALUATED_ON','Dataset','HotpotQA'),
         ('EvaluationSetting','HippoRAG retrieval corpus','HAS_SAMPLE_SETTING','Parameter','1000 validation questions per dataset'),
         ('EvaluationSetting','HippoRAG retrieval corpus','USES_KNOWLEDGE_BASE','KnowledgeBase','supporting and distractor passages'),
         ('Method','HippoRAG','USES_EVALUATION_SETTING','EvaluationSetting','HippoRAG retrieval corpus')],
    ],
    'totds': [
        [('Method','Tree-of-Traversals','EVALUATED_ON','Dataset','2WikiMultiHop'),
         ('Method','Tree-of-Traversals','EVALUATED_ON','Dataset','QALD-10')],
    ],
    'kggptds': [
        [('Method','KG-GPT','EVALUATED_ON','Dataset','FACTKG'),
         ('Method','KG-GPT','EVALUATED_ON','Dataset','MetaQA'),
         ('EvaluationSetting','KG-GPT MetaQA evaluation','USES_DATASET','Dataset','MetaQA 1-hop'),
         ('EvaluationSetting','KG-GPT MetaQA evaluation','USES_DATASET','Dataset','MetaQA 2-hop'),
         ('EvaluationSetting','KG-GPT MetaQA evaluation','USES_DATASET','Dataset','MetaQA 3-hop'),
         ('EvaluationSetting','KG-GPT MetaQA evaluation','REPORTS_METRIC','Metric','Hits@1'),
         ('Method','KG-GPT','USES_EVALUATION_SETTING','EvaluationSetting','KG-GPT MetaQA evaluation')],
    ],
    'rogmeta': [
        [('Method','RoG','EVALUATED_ON','Dataset','MetaQA-3hop'),
         ('Dataset','MetaQA-3hop','USES_KNOWLEDGE_BASE','KnowledgeBase','Wiki-Movies'),
         ('Method','RoG','DERIVES_TRAINING_DATA_FROM','KnowledgeBase','Freebase'),
         ('Method','RoG','USES_TRAINING_SIGNAL','TrainingSignal','1000 MetaQA-3hop training samples'),
         ('EvaluationSetting','RoG transfer experiment','USES_KNOWLEDGE_BASE','KnowledgeBase','Freebase to Wiki-Movies transfer'),
         ('Method','RoG','USES_EVALUATION_SETTING','EvaluationSetting','RoG transfer experiment')],
    ],
}


CONTROLS = [
    ('G-Retriever 将相关子图检索表述成什么优化问题？', ['pcst'], 'G-Retriever 将相关子图检索表述为 Prize-Collecting Steiner Tree（PCST）优化。'),
    ('KG-GPT 的三个处理阶段是什么，先后顺序怎样？', ['kggpt'], 'Sentence Segmentation → Graph Retrieval → Inference。'),
    ('ToG-R 相对 ToG 是什么关系？替换了哪类剪枝，并报告什么调用上界？', ['togr'], 'ToG-R 是 ToG 的变体，以随机实体剪枝替代 LLM 实体剪枝；论文给出的调用上界分别为 ToG 的 2ND+D+1、ToG-R 的 ND+D+1。'),
    ('HippoRAG 用什么查询概念驱动的图算法连接跨段落证据？', ['hippo'], '它抽取查询关键概念作为种子，在知识图上运行 Personalized PageRank（PPR）。'),
    ('KGP 图中的节点和边分别可以表示什么？遍历代理负责什么？', ['kgp'], '节点可表示段落或文档结构；边可表示词法/语义相似或文档内结构；LLM 遍历代理选择邻居并收集支持段落。'),
    ('Tree-of-Traversals 的阈值、最大深度、最大扩展数分别会怎样结束搜索？', ['totbound'], '超过答案阈值可找到答案并停止；max depth 强制转入 done；max expansions 停止探索并返回 Cannot find answer。'),
    ('LPKG 如何把 KG 用于复杂问答规划？', ['lpdata'], '它从 KG 构造 planning data，并用这些数据微调小模型的规划能力。'),
    ('Roadmap 将 LLM 与 KG 融合归纳为哪三条路线？', ['roadmap'], 'KG-enhanced LLMs、LLM-augmented KGs、Synergized LLMs + KGs。'),
]

CROSSES = [
    ('比较 ToG 与 ToG-2：问题到证据的流程中，搜索算法、实体和文档分别怎样参与？',['tog','tog2'],'ToG 以 LLM 代理迭代束搜索探索 KG；ToG-2 将实体连接到文档，并交替进行图检索和上下文检索。','不能因流程不同就断言 ToG-2 在所有条件下更优。'),
    ('比较 HippoRAG 与 RoG：查询种子、关系路径计划和最终证据各处于哪一步？',['hippo','rog'],'HippoRAG 用查询概念作 PPR 种子，在一次检索中整合跨段落信息；RoG 先生成 KG 约束的关系路径计划，再检索有效路径供推理。','不能把 RoG 的关系路径计划说成 PPR，也不能据此建立技术继承。'),
    ('CuriousLLM 如何增强 KGP？它的 Follow-upQA 训练样本把什么作为输入和目标？',['kgp','curious'],'CuriousLLM 自述为对 KGP 的增强；KGP 使用文档图和遍历代理收集段落，Follow-upQA 以问题和证据为输入、以后续问题为目标。成本/幻觉评价属于论文作者报告。','增强方向是 CuriousLLM → KGP，不得反转，也不能把作者报告说成此系统的复现实测。'),
    ('StructGPT 与 LPKG 分别在推理和训练阶段怎样使用结构化数据或 KG？',['struct','lpdata'],'StructGPT 在回答时通过专门接口迭代读取结构化证据；LPKG 从 KG 构造 planning data 并微调规划能力。','不能把推理时读取接口等同于训练数据构建。'),
    ('ToG 和 RoG 都用 KG，分别如何处理推理时搜索与训练阶段的知识？',['tog_training','rog'],'ToG 被描述为无需额外训练的在线 KG 搜索；RoG 包含 KG 知识蒸馏训练，推理时再进行关系路径计划与路径检索。','RoG 推理模块可接入其他 LLM 不等于整套 RoG 没有训练。'),
    ('比较 ToG-2 与 LPKG：图知识分别服务于什么阶段和目标？',['tog2','lpdata'],'ToG-2 在推理时协作检索图和上下文；LPKG 用 KG 派生的规划数据进行训练。','共享 KG/QA 目标不表示训练协议或算法相同。'),
    ('HippoRAG 与 KGP 的图节点/边从什么材料构成，检索如何回到证据？',['hippo','kgp'],'HippoRAG 将语料转为无模式 KG，以查询概念启动 PPR；KGP 用段落/文档结构作为节点，以相似或结构关系连边，再由代理收集支持段落。','不能把 KGP 的节点定义直接套到 HippoRAG。'),
    ('G-Retriever 与 ToG-2 怎样选择或组织用于生成的证据？',['grscale','pcst','tog2'],'G-Retriever 用 PCST 选择相关子图以控制大图上下文；ToG-2 通过实体连接文档并交替检索图与上下文。','不能声称 ToG-2 使用 PCST，也不能从机制描述推出两者资源实测相同。'),
    ('ToG 与 ToG-2 共同评测了哪些数据集？这条共享数据集关系能证明什么？',['togds','tog2ds'],'两篇都列出 WebQSP 和 QALD10-en；这只建立各自的评测关联，不能证明方法继承或受控性能优劣。','共享数据集不等于相同划分、底座、知识来源或比较协议。'),
    ('HippoRAG 与 Tree-of-Traversals 各自评测的 2Wiki 数据集名称是什么？其跨事实检索机制有何不同？',['hippods','totds','hippo','totbound'],'HippoRAG 使用 2WikiMultiHopQA 并用 PPR；Tree-of-Traversals 列出 2WikiMultiHop，并搜索动作树。数据集名称和协议须分别保留。','名称相似不证明划分、语料、底座或指标相同。'),
    ('比较 KG-GPT 与 RoG 的 MetaQA 实验：跳数/指标、Wiki-Movies 与 Freebase 分别是什么角色？',['kggptds','rogmeta'],'KG-GPT 报告 MetaQA 1/2/3-hop Hits@1；RoG 的 MetaQA-3hop 基于 Wiki-Movies，Freebase 是迁移训练来源，并取 1000 个训练样本。','不能把 Freebase 写成 RoG MetaQA 测试 KG，也不以协议不一致的数字直接排名。'),
    ('MusicBrainz-x-Wikidata 与 CLQA-Wiki 各自怎样关联知识来源，题型有什么差别？',['totmusic','lpbench'],'Tree-of-Traversals 的 MusicBrainz-x-Wikidata 要综合两个 KG；CLQA-Wiki 来自 Wikidata 子集，含 multi-hop、comparison、intersection、union。','都出现 Wikidata 不表示同一数据集或相同题型。'),
    ('HippoRAG 的 HotpotQA 与 ToG-2 的 AdvHotpotQA 有何数据集关系和设置差异？',['hippods','tog2ds'],'ToG-2 把 AdvHotpotQA 描述为 HotpotQA 的挑战子集；HippoRAG 从验证集抽取问题并组合支持/干扰段落，ToG-2 报告 full Wikipedia/Wikidata 设置。','不能把父集与挑战子集视为相同测试协议。'),
    ('ToG 与 ToG-2 对 Creak/QA 报告的指标与知识来源设置有何不同？跨论文比较还缺哪些条件？',['togds','tog2ds'],'按原文保留 ToG 的 exact match accuracy（Hits@1）；ToG-2 对 Creak/FEVER 报告 Acc.、其他数据集报告 EM，并写明 full Wikipedia/Wikidata。还须逐项核对划分、底座和提示条件。','指标名称相近不等于受控比较；未提供的 ToG 条件不能补写。'),
    ('Tree-of-Traversals 和 CuriousLLM 各用什么继续检索、停止或表示证据充分的机制？',['totbound','curious'],'Tree-of-Traversals 用阈值、max depth、max expansions，三者停止含义不同；CuriousLLM 训练追问并用特殊 token 表示证据充分。','预算上限/强制 done 不等于答案正确，也不能把 token 当作本项目的运行时停止器。'),
    ('MindMap 与 RoG 如何把知识带入答案？可解释路径能否自动保证答案正确？',['mind','rog'],'MindMap 结合 LLM 隐式知识和外部 KG 并展示 mind map；RoG 通过关系计划检索有效推理路径。路径可追溯仍须逐项检查原文是否支持结论。','可解释性不等于所有结论都通过事实验证。'),
    ('STaRK 与 MindMap 分别是什么类型的工作、涉及什么医学任务？这些信息能否证明 MindMap 在 STaRK 上评测过？',['stark','mind'],'STaRK 是覆盖精准医疗等领域的检索基准；MindMap 是包含医学 QA 场景的 KG prompting 方法。所给来源不能建立 MindMap EVALUATED_ON STaRK。','证据不足不能写成“证明从未评测”，也不能捏造分数。'),
    ('KG-GPT 与 RoG 的处理流程分别如何排序？句子分割、关系规划、图/路径检索和推理属于哪一方？',['kggpt','rog'],'KG-GPT 是 Sentence Segmentation → Graph Retrieval → Inference；RoG 是 planning → retrieval → reasoning，且先规划关系路径。','共有“检索/推理”步骤不代表流程相同或存在继承。'),
    ('ToG、HippoRAG、RoG 分别怎样完成多跳关联？',['tog','hippo','rog'],'ToG 迭代束搜索；HippoRAG 用查询种子驱动 PPR；RoG 先规划关系路径再检索有效路径。','共同处理多跳不表示使用相同图操作或计算成本。'),
    ('ToG-2、HippoRAG、KGP 如何把图和文档/段落连接，再获得支持证据？',['tog2','hippo','kgp'],'ToG-2 用实体连接文档并协作检索；HippoRAG 从语料抽取图并用 PPR 跨片段检索；KGP 以段落/结构为图节点并通过代理收集支持段落。','三者节点、边和检索过程不可混为同一种表示。'),
    ('比较 G-Retriever、Tree-of-Traversals、CuriousLLM：它们分别约束上下文、搜索空间还是证据缺口？',['grscale','totbound','curious'],'G-Retriever 选择相关子图；Tree-of-Traversals 设深度与扩展边界；CuriousLLM 学习追问或给出证据充分信号。','不能从机制差异直接推出统一条件下速度或 Token 优势。'),
    ('LPKG、CuriousLLM、RoG 的训练信号和推理用途分别是什么？',['lpdata','curious','rog'],'LPKG 用 KG 派生 planning data；CuriousLLM 用问题和证据生成后续问题；RoG 有 KG 蒸馏训练，并在推理时做关系路径计划/检索。','不能互换监督目标或臆测训练数据完全相同。'),
    ('比较 ToG/ToG-R 调用公式与 Tree-of-Traversals 搜索预算，为什么不能直接给统一运行时排名？',['togr','totbound'],'ToG 与 ToG-R 的公式是 LLM 调用上界；Tree-of-Traversals 的 max depth/expansions 是搜索边界。两者不是同一量，也不等于墙钟时延。','不能反转变体方向，也不能将调用上界当作跨方法实测时延。'),
    ('结合 CLQA-Wiki、2WikiMultiHop、MusicBrainz-x-Wikidata，区分多跳、交并逻辑与跨 KG 任务。',['lpbench','totds','totmusic'],'CLQA-Wiki 明列多跳/比较/交/并；2WikiMultiHop 是多跳任务；MusicBrainz-x-Wikidata 要结合两个 KG。','这些属性可并存，不能由一项属性推出数据集没有其他题型。'),
]

NEGATIVES = [
    ('HippoRAG 与 RoG 都做图上多跳推理，能否断言“RoG 直接继承 HippoRAG 的 PPR”？',['hippo','rog'],'unsupported_lineage','两篇原文分别支持 PPR 检索与关系路径规划；给定来源未建立 RoG 继承 HippoRAG/PPR 的关系。'),
    ('ToG 与 ToG-2 都评测 WebQSP，是否足以证明“ToG-2 在所有数据集和所有底座上严格优于 ToG”？',['togds','tog2ds'],'unsupported_universal_performance','共同评测关联不支持全称优越性；还需匹配划分、底座、知识来源、提示与完整结果。'),
    ('KGP 和 HippoRAG 都使用文档图，所以两者是否都是“段落节点、语义相似边”？',['kgp','hippo'],'graph_representation_conflation','KGP 明确包含段落或文档结构节点及相似/结构边；HippoRAG 把语料转为无模式 KG，节点语义不能直接互换。'),
    ('KG-GPT 和 RoG 都涉及 MetaQA，是否能把 RoG 的 Freebase 迁移来源认作两者共同的 MetaQA 测试 KG？',['kggptds','rogmeta'],'training_test_role_conflation','RoG 的 MetaQA-3hop 基于 Wiki-Movies；Freebase 是迁移训练来源，不是该测试 KG。'),
    ('STaRK 有精准医疗领域、MindMap 有医学 QA，是否足以建立 MindMap→EVALUATED_ON→STaRK 并给出分数？',['stark','mind'],'unsupported_evaluation_edge','所给段落未建立该评测边或分数；只能说明当前证据不足，不能声称证明从未评测。'),
    ('给出虚构方法 NebulaGraphRAG-2099 继承 HippoRAG 后，在 LunarQA-2099 上相对 RoG 的官方精确提升分数。',[],'no_corpus_answer','冻结语料没有这些方法、基准或分数的证据；应指出无来源，不编造继承链和数值。'),
    ('CuriousLLM 说自己增强 KGP，能否反向推出“KGP 用 CuriousLLM 的 Follow-upQA 训练”？',['kgp','curious'],'reversed_enhancement_direction','来源支持 CuriousLLM 增强 KGP 的方向；没有证据表明 KGP 使用 Follow-upQA 训练。'),
    ('Tree-of-Traversals 达到 max depth 或 max expansions，是否都代表证据充分且答案正确？',['totbound','curious'],'budget_stop_success_conflation','max depth 强制进入 done，max expansions 返回 Cannot find answer；CuriousLLM 的充分证据 token 含义不同，均不自动保证答案正确。'),
]


def norm(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def stable_id(*values):
    return hashlib.sha256('\0'.join(map(str, values)).encode('utf-8')).hexdigest()


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def make_cases(units):
    cases = []
    for i, (question, keys, answer) in enumerate(CONTROLS, 1):
        cases.append(dict(id=f'F{i:02}', category='fact', question=question, units=keys,
            answerable=True, negative_kind=None, generate=True, min_source_papers=1,
            reasoning_chain='；'.join(units[k]['answer_point'] for k in keys),
            expected_answer=answer, must_not_claim=None))
    for i, (question, keys, answer, invalid) in enumerate(CROSSES, 1):
        cases.append(dict(id=f'R{i:02}', category='cross', question=question, units=keys,
            answerable=True, negative_kind=None, generate=True, min_source_papers=2,
            reasoning_chain='；'.join(units[k]['answer_point'] for k in keys),
            expected_answer=answer, must_not_claim=invalid,
            relation_review=dict(evidence='覆盖每个必要事实并逐条引用其来源原文。',
                semantics='核对关系方向、实体角色、训练/测试角色、数据集设置和指标。',
                synthesis='区分论文直接主张与跨来源分析；共享实体不自动构成因果或方法继承。',
                uncertainty='来源没有说明的条件须标为未知，不可补造。')))
    for i, (question, keys, kind, answer) in enumerate(NEGATIVES, 1):
        cases.append(dict(id=f'N{i:02}', category='negative', question=question, units=keys,
            answerable=False, negative_kind=kind, generate=True,
            min_source_papers=2 if keys else 0, reasoning_chain=None,
            expected_answer=answer, must_not_claim='不确认题干中无来源的关系或数值；说明证据边界。'))
    for case in cases:
        case['source_papers'] = sorted({units[key]['paper_id'] for key in case['units']})
    return cases


def base_units(v2, chunks):
    selected = set(key for c in CONTROLS for key in c[1])
    selected.update(key for c in CROSSES for key in c[1])
    selected.update(key for c in NEGATIVES for key in c[1])
    units = {}
    for key in sorted(selected):
        unit = dict(v2['units'][key])
        sources = []
        for source in unit['support_sources']:
            chunk = chunks[source['chunk_id']]
            if source['source_text'] != chunk['text']:
                raise ValueError('frozen_source_text_differs_from_active_corpus:' + key)
            sources.append(dict(chunk_id=chunk['chunk_id'], paper_id=chunk['paper_id'],
                parse_id=chunk['parse_id'], title=chunk['title'],
                source_relative_path=chunk['source_relative_path'], page_start=chunk['page_start'],
                page_end=chunk['page_end'], source_spans=chunk['source_spans'],
                text_sha256=chunk['text_sha256'], section=chunk.get('section'), text=chunk['text']))
        unit['support_sources'] = sources
        units[key] = unit
    return units


def build_claims(units, cases):
    claims, paths_by_unit = [], {}
    allowed = {tuple(sig) for sig in SCHEMA['relationship_signatures']}
    for unit_id, declared_paths in UNIT_PATHS.items():
        if unit_id not in units:
            continue
        source = next(s for s in units[unit_id]['support_sources'] if s['chunk_id'] == units[unit_id]['primary_chunk'])
        # A question's supporting subgraph may branch. Split statements into real
        # edge-contiguous paths rather than presenting unrelated edges as a chain.
        paths = []
        for declared in declared_paths:
            segment = []
            for triple in declared:
                subject = (triple[0], norm(triple[1]))
                previous_object = (segment[-1][3], norm(segment[-1][4])) if segment else None
                if segment and subject != previous_object:
                    paths.append(segment)
                    segment = []
                segment.append(triple)
            if segment:
                paths.append(segment)
        path_records = []
        for pi, triples in enumerate(paths, 1):
            claim_ids = []
            for ei, (st, subject, predicate, ot, obj) in enumerate(triples, 1):
                if (st, predicate, ot) not in allowed:
                    raise ValueError(f'relation_signature_not_allowed:{unit_id}:{st}:{predicate}:{ot}')
                quote = source['text']
                if not quote or quote not in source['text']:
                    raise ValueError('claim_quote_not_exact:' + unit_id)
                cid = stable_id(VERSION, unit_id, pi, ei, st, norm(subject), predicate, ot, norm(obj), source['chunk_id'])
                claim = dict(claim_id=cid, unit_id=unit_id, path_id=f'{unit_id}.P{pi:02}',
                    subject_type=st, subject=subject, predicate=predicate, object_type=ot, object=obj,
                    claim_kind='source_grounded_curated_relation', review_status='verified_against_source',
                    evidence_quote=quote, provenance={k: source[k] for k in (
                        'paper_id','title','source_relative_path','parse_id','chunk_id','page_start','page_end',
                        'source_spans','text_sha256')},
                    source_hash=hashlib.sha256(quote.encode('utf-8')).hexdigest(),
                    qualifier='必须保留原文限定；graph edge 表示被引论文中的这一局部主张。')
                claims.append(claim)
                claim_ids.append(cid)
            path_records.append(dict(unit_id=unit_id, path_id=f'{unit_id}.P{pi:02}',
                nodes=[dict(type=triples[0][0], name=triples[0][1])] +
                    [dict(type=t[3], name=t[4]) for t in triples], claim_ids=claim_ids))
        paths_by_unit[unit_id] = path_records
    return claims, paths_by_unit


def build_benchmark():
    v2_raw = V2.read_bytes()
    v2 = json.loads(v2_raw)
    corpus_id, papers, chunks_list = load_corpus(ROOT)
    chunks = {c['chunk_id']: c for c in chunks_list}
    units = base_units(v2, chunks)
    cases = make_cases(units)
    if len(cases) != 40 or len({c['question'] for c in cases}) != 40:
        raise ValueError('benchmark_must_have_40_unique_questions')
    claims, paths_by_unit = build_claims(units, cases)
    paper_map={p['paper_id']:p for p in papers}
    prior_claims=load_legacy_claims(chunks,paper_map,corpus_id)
    prior_manifest=[dict(claim_id=c['claim_id'],paper_id=c['provenance']['paper_id'],
        chunk_id=c['provenance']['chunk_id'],predicate=c['predicate'],source_hash=c['source_hash'])
        for c in prior_claims]
    spec = {
        'version': VERSION, 'corpus_id': corpus_id, 'papers': len(papers), 'chunks': len(chunks),
        'source_benchmark_sha256': digest_bytes(v2_raw), 'cases': cases, 'units': units,
        'graph_schema': SCHEMA, 'graph_claims': claims, 'paths_by_unit': paths_by_unit,
        'prior_graph_snapshot': {'source':'data/kg.sqlite3 approved kg-schema-v2 claims, revalidated read-only',
            'claim_count':len(prior_claims),'claim_manifest_sha256':digest_bytes(json.dumps(
                prior_manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')),
            'claim_ids':[c['claim_id'] for c in prior_claims]},
        'author': '原文核查与关系边由 Codex 整理；非独立人工金标。',
        'prior_exposure': '基于已分析的同一 14 篇论文与历史失败诊断，属于开发/诊断集，不是未见测试集。',
        'models': {'generation': 'DeepSeek-V4-Flash (configured provider)', 'embedding': 'BGE-M3 (configured provider)',
            'reranker': 'bge-reranker (configured local model)'},
        'controls': {'arms': ['Hybrid','Hybrid+Graph'], 'same_question_set': True,
            'generation_subset': [c['id'] for c in cases], 'generation_policy': 'All 40 questions require a full answer in a future comparison.',
            'graph_namespace': 'isolated benchmark-v3 SQLite graph; production Neo4j graph is not written.',
            'graph_claim_source': 'Curated relations from frozen support excerpts, not model-generated claims.'},
        'scoring': {'primary': 'SupportRecall@5; within one fact unit supporting sources are OR, required fact units are AND.',
            'secondary': ['SupportRecall@8','MRR@40','selected evidence unit coverage','all required units coverage'],
            'answer_review': 'All required facts and citations; direction, entity roles, train/test role, evaluation setup and unsupported claims reviewed separately.',
            'graph_coverage': 'Each answerable relation case must expose a source-backed path for every required unit; negative cases must not contain their prohibited edge.',
            'denominator': '32 answerable questions; 24 cross-paper relation questions reported separately; 8 negative cases reported separately.',
            'interpretation': 'retrieval coverage, citation validity, graph-path coverage and semantic answer correctness are separate results; no assumption that graph wins.'},
        'freeze_inputs': {'benchmark_v2_sha256': digest_bytes(v2_raw),
            'corpus_manifest_sha256': hashlib.sha256((ROOT/'artifacts/exports/pilot-v1/pilot-manifest.json').read_bytes()).hexdigest(),
            'active_parse_manifest_sha256': hashlib.sha256((ROOT/'artifacts/reports/stage-1/current-parses.json').read_bytes()).hexdigest()},
    }
    spec['validation'] = validate_benchmark(spec, chunks)
    return spec, chunks, papers


def validate_benchmark(bench, chunks):
    cases = bench['cases']
    counts = Counter(c['category'] for c in cases)
    if counts != Counter(fact=8, cross=24, negative=8):
        raise ValueError('category_counts_mismatch')
    if len(bench['units']) != 25:
        raise ValueError('unexpected_selected_unit_count')
    claim_by_id = {c['claim_id']: c for c in bench['graph_claims']}
    if len(claim_by_id) != len(bench['graph_claims']):
        raise ValueError('duplicate_claim_id')
    for unit_id, unit in bench['units'].items():
        if unit['primary_chunk'] not in chunks or unit['primary_chunk'] not in unit['known_support_chunks']:
            raise ValueError('primary_source_missing:' + unit_id)
        for s in unit['support_sources']:
            chunk = chunks[s['chunk_id']]
            if chunk.get('content_kind') == 'references' or chunk['paper_id'] != s['paper_id']:
                raise ValueError('invalid_source_kind_or_paper:' + unit_id)
            if (chunk['text'] != s['text'] or chunk['text_sha256'] != s['text_sha256'] or
                    hashlib.sha256(s['text'].encode('utf-8')).hexdigest() != s['text_sha256']):
                raise ValueError('source_excerpt_hash_mismatch:' + unit_id)
    for claim in bench['graph_claims']:
        src = chunks[claim['provenance']['chunk_id']]
        if claim['evidence_quote'] != src['text'] or claim['evidence_quote'] not in src['text']:
            raise ValueError('edge_quote_not_exact:' + claim['claim_id'])
        if src.get('content_kind') == 'references':
            raise ValueError('reference_section_used_as_evidence')
        if claim['review_status'] != 'verified_against_source':
            raise ValueError('unverified_graph_claim')
    for c in cases:
        if c['answerable'] and not c['units']:
            raise ValueError('answerable_case_missing_units:' + c['id'])
        actual_papers = sorted({bench['units'][u]['paper_id'] for u in c['units']})
        if actual_papers != c['source_papers']:
            raise ValueError('case_paper_manifest_mismatch:' + c['id'])
        if c['category'] == 'cross' and (len(actual_papers) < 2 or not c.get('relation_review')):
            raise ValueError('cross_case_requires_two_papers:' + c['id'])
        if c['generate'] is not True:
            raise ValueError('v3_all_cases_must_generate')
        if any(u not in bench['paths_by_unit'] for u in c['units']):
            raise ValueError('question_unit_has_no_graph_path:' + c['id'])
    if len({c['id'] for c in cases}) != 40:
        raise ValueError('case_id_collision')
    return {'cases': len(cases), 'categories': dict(counts), 'units': len(bench['units']),
        'source_papers_used': len({p for c in cases for p in c['source_papers']}),
        'graph_claims': len(bench['graph_claims']), 'claim_quotes_exact': True,
        'external_model_calls': 0, 'evaluation_calls': 0}


def node_id(node_type, name):
    return stable_id('entity-v3', node_type, norm(name))


def load_legacy_claims(chunks, papers, corpus_id):
    db = ROOT / 'data/kg.sqlite3'
    con = sqlite3.connect(f'file:{db.as_posix()}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT * FROM kg_claims WHERE corpus_id=? AND review_status='approved' AND validation_status='valid' ORDER BY paper_title,page_start,claim_id", (corpus_id,)).fetchall()
        result=[]
        allowed={tuple(x) for x in SCHEMA['relationship_signatures']}
        for row in rows:
            r=dict(row)
            chunk=chunks.get(r['chunk_id'])
            paper=papers.get(r['paper_id'])
            if not chunk or not paper or chunk['paper_id']!=r['paper_id'] or chunk['parse_id']!=r['parse_id']:
                raise ValueError('legacy_claim_source_identity_mismatch:'+r['claim_id'])
            if r['source_sha256']!=paper['source_sha256'] or r['page_start']!=chunk['page_start'] or r['page_end']!=chunk['page_end']:
                raise ValueError('legacy_claim_source_metadata_mismatch:'+r['claim_id'])
            sig=(r['subject_type'],r['predicate'],r['object_type'])
            if sig not in allowed:
                raise ValueError('legacy_claim_signature_not_in_v3:'+r['claim_id'])
            exact=locate_quote(chunk['text'],r['evidence_quote'])
            if not exact:
                raise ValueError('legacy_claim_quote_not_located:'+r['claim_id'])
            source=dict(paper_id=r['paper_id'],title=chunk['title'],source_relative_path=chunk['source_relative_path'],
                source_sha256=paper['source_sha256'],parse_id=chunk['parse_id'],chunk_id=chunk['chunk_id'],
                page_start=chunk['page_start'],page_end=chunk['page_end'],source_spans=chunk['source_spans'],
                text_sha256=chunk['text_sha256'])
            result.append(dict(claim_id=r['claim_id'],unit_id='legacy-v2',path_id='legacy-v2:'+r['claim_id'],
                subject_type=r['subject_type'],subject=r['subject'],predicate=r['predicate'],
                object_type=r['object_type'],object=r['object'],claim_kind='legacy-v2:'+r['claim_kind'],
                review_status='approved_legacy_v2',evidence_quote=exact,provenance=source,
                source_hash=hashlib.sha256(exact.encode('utf-8')).hexdigest(),
                qualifier='legacy_v2_review_note: '+(r.get('review_note') or 'approved in kg.sqlite3; source quote revalidated against active chunk')))
        return result
    finally:
        con.close()


def create_graph_db(path, bench, papers, chunks, legacy_claims):
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    try:
        con.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE graph_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE entities(entity_id TEXT PRIMARY KEY,entity_type TEXT NOT NULL,name TEXT NOT NULL,normalized_name TEXT NOT NULL);
        CREATE UNIQUE INDEX entity_norm ON entities(entity_type,normalized_name);
        CREATE TABLE papers(paper_id TEXT PRIMARY KEY,title TEXT NOT NULL,source_relative_path TEXT NOT NULL,source_sha256 TEXT NOT NULL);
        CREATE TABLE source_chunks(chunk_id TEXT PRIMARY KEY,paper_id TEXT NOT NULL REFERENCES papers(paper_id),parse_id TEXT NOT NULL,
          page_start INTEGER NOT NULL,page_end INTEGER NOT NULL,source_relative_path TEXT NOT NULL,text_sha256 TEXT NOT NULL,text TEXT NOT NULL);
        CREATE TABLE claims(claim_id TEXT PRIMARY KEY,unit_id TEXT NOT NULL,path_id TEXT NOT NULL,subject_type TEXT NOT NULL,subject TEXT NOT NULL,
          predicate TEXT NOT NULL,object_type TEXT NOT NULL,object TEXT NOT NULL,claim_kind TEXT NOT NULL,review_status TEXT NOT NULL,
          evidence_quote TEXT NOT NULL,provenance_json TEXT NOT NULL,source_hash TEXT NOT NULL,qualifier TEXT NOT NULL);
        CREATE TABLE edges(claim_id TEXT PRIMARY KEY REFERENCES claims(claim_id),subject_id TEXT NOT NULL REFERENCES entities(entity_id),
          object_id TEXT NOT NULL REFERENCES entities(entity_id),predicate TEXT NOT NULL);
        CREATE TABLE claim_sources(claim_id TEXT NOT NULL REFERENCES claims(claim_id),chunk_id TEXT NOT NULL REFERENCES source_chunks(chunk_id),
          PRIMARY KEY(claim_id,chunk_id));
        CREATE INDEX edge_subject ON edges(subject_id,predicate);
        CREATE INDEX edge_object ON edges(object_id,predicate);
        CREATE TABLE question_units(case_id TEXT NOT NULL,unit_id TEXT NOT NULL,PRIMARY KEY(case_id,unit_id));
        CREATE TABLE question_paths(case_id TEXT NOT NULL,unit_id TEXT NOT NULL,path_id TEXT NOT NULL,ordinal INTEGER NOT NULL,
          claim_id TEXT NOT NULL REFERENCES claims(claim_id),PRIMARY KEY(case_id,unit_id,path_id,ordinal));
        ''')
        meta = {'schema_version': SCHEMA['schema_version'], 'benchmark': VERSION,
            'benchmark_source_sha256': bench['source_benchmark_sha256'], 'namespace': 'isolated-only'}
        con.executemany('INSERT INTO graph_meta VALUES(?,?)', sorted(meta.items()))
        con.executemany('INSERT INTO papers VALUES(?,?,?,?)',
            [(p['paper_id'],p['title'],p['source_relative_path'],p['source_sha256']) for p in papers.values()])
        con.executemany('INSERT INTO source_chunks VALUES(?,?,?,?,?,?,?,?)',
            [(c['chunk_id'],c['paper_id'],c['parse_id'],c['page_start'],c['page_end'],c['source_relative_path'],c['text_sha256'],c['text'])
             for c in chunks.values()])
        graph_claims=list(bench['graph_claims'])+legacy_claims
        if len({c['claim_id'] for c in graph_claims})!=len(graph_claims):
            raise ValueError('v3_and_legacy_claim_id_collision')
        entities = {}
        for c in graph_claims:
            for typ, name in ((c['subject_type'], c['subject']), (c['object_type'], c['object'])):
                eid = node_id(typ, name)
                entities[eid] = (eid, typ, name, norm(name))
        con.executemany('INSERT OR IGNORE INTO entities VALUES(?,?,?,?)', entities.values())
        for c in graph_claims:
            con.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                c['claim_id'],c['unit_id'],c['path_id'],c['subject_type'],c['subject'],c['predicate'],
                c['object_type'],c['object'],c['claim_kind'],c['review_status'],c['evidence_quote'],
                json.dumps(c['provenance'],ensure_ascii=False,sort_keys=True),c['source_hash'],c['qualifier']))
            con.execute('INSERT INTO edges VALUES(?,?,?,?)', (c['claim_id'],node_id(c['subject_type'],c['subject']),
                node_id(c['object_type'],c['object']),c['predicate']))
            con.execute('INSERT INTO claim_sources VALUES(?,?)',(c['claim_id'],c['provenance']['chunk_id']))
        for case in bench['cases']:
            for unit_id in case['units']:
                con.execute('INSERT INTO question_units VALUES(?,?)',(case['id'],unit_id))
                for path in bench['paths_by_unit'][unit_id]:
                    for ordinal, cid in enumerate(path['claim_ids'], 1):
                        con.execute('INSERT INTO question_paths VALUES(?,?,?,?,?)',
                            (case['id'],unit_id,path['path_id'],ordinal,cid))
        con.commit()
    finally:
        con.close()


def audit_graph(path, bench, chunks):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        counts = {table: con.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
            for table in ('papers','source_chunks','entities','claims','edges','question_units','question_paths')}
        expected_claims=len(bench['graph_claims'])+bench['prior_graph_snapshot']['claim_count']
        if counts['claims'] != expected_claims or counts['edges'] != counts['claims']:
            raise ValueError('isolated_graph_row_count_mismatch')
        case_results = []
        for case in bench['cases']:
            unit_results = []
            for unit_id in case['units']:
                paths = []
                for pathrec in bench['paths_by_unit'][unit_id]:
                    rows = [dict(r) for r in con.execute('''SELECT c.claim_id,c.predicate,c.subject_type,c.subject,c.object_type,c.object,
                        c.evidence_quote,c.provenance_json FROM question_paths qp JOIN claims c ON c.claim_id=qp.claim_id
                        WHERE qp.case_id=? AND qp.unit_id=? AND qp.path_id=? ORDER BY qp.ordinal''',
                        (case['id'],unit_id,pathrec['path_id']))]
                    expected = pathrec['claim_ids']
                    if [r['claim_id'] for r in rows] != expected:
                        raise ValueError('ordered_path_claim_mismatch:' + case['id'] + ':' + unit_id)
                    actual_nodes = ([dict(type=rows[0]['subject_type'],name=rows[0]['subject'])] +
                        [dict(type=r['object_type'],name=r['object']) for r in rows]) if rows else []
                    if (len(pathrec['nodes']) != len(actual_nodes) or any(
                            wanted['type'] != actual['type'] or norm(wanted['name']) != norm(actual['name'])
                            for wanted,actual in zip(pathrec['nodes'],actual_nodes))):
                        raise ValueError('declared_path_nodes_do_not_match_edges:' + case['id'] + ':' + pathrec['path_id'])
                    for previous,current in zip(rows,rows[1:]):
                        if (previous['object_type'],norm(previous['object']))!=(current['subject_type'],norm(current['subject'])):
                            raise ValueError('path_edges_do_not_connect:' + case['id'] + ':' + pathrec['path_id'])
                    for row in rows:
                        prov=json.loads(row['provenance_json']); chunk=chunks[prov['chunk_id']]
                        if row['evidence_quote'] != chunk['text'] or row['evidence_quote'] not in chunk['text']:
                            raise ValueError('audited_quote_not_source_substring:' + row['claim_id'])
                    paths.append(dict(path_id=pathrec['path_id'],nodes=pathrec['nodes'],edges=[{
                        'claim_id':r['claim_id'],'subject':r['subject'],'predicate':r['predicate'],'object':r['object'],
                        'source_chunk':json.loads(r['provenance_json'])['chunk_id'],
                        'page_start':json.loads(r['provenance_json'])['page_start'],
                        'page_end':json.loads(r['provenance_json'])['page_end']} for r in rows]))
                if not paths:
                    raise ValueError('question_unit_path_missing:' + case['id'] + ':' + unit_id)
                unit_results.append(dict(unit_id=unit_id,source_paper=bench['units'][unit_id]['title'],
                    source_chunk=bench['units'][unit_id]['primary_chunk'],
                    pages=[bench['units'][unit_id]['page_start'],bench['units'][unit_id]['page_end']],paths=paths))
            absent_checks = []
            if case['id'] in ('N01','N02','N04','N05','N07','N08'):
                forbidden = {
                    'N01':('Method','RoG','INHERITS_FROM','Method','HippoRAG'),
                    'N02':('Method','ToG-2','UNIVERSALLY_OUTPERFORMS','Method','ToG'),
                    'N04':('Dataset','MetaQA-3hop','USES_KNOWLEDGE_BASE','KnowledgeBase','Freebase test KG'),
                    'N05':('Method','MindMap','EVALUATED_ON','Dataset','STaRK'),
                    'N07':('Method','KGP','TRAINED_WITH','TrainingSignal','Follow-upQA'),
                    'N08':('StopCondition','max expansions','RETURNS','Outcome','correct answer')}
                st,s,p,ot,o=forbidden[case['id']]
                present=con.execute('''SELECT count(*) FROM claims WHERE subject_type=? AND subject=? AND predicate=? AND object_type=? AND object=?''',
                    (st,s,p,ot,o)).fetchone()[0]
                if present:
                    raise ValueError('prohibited_edge_present:' + case['id'])
                absent_checks.append(dict(prohibited_edge_absent=True,subject=s,predicate=p,object=o,
                    boundary='absence applies only to this frozen question-focused graph/source set'))
            case_results.append(dict(case_id=case['id'],category=case['category'],question=case['question'],
                status='covered' if case['units'] else 'negative_anchor_absence_checked',
                source_units=len(case['units']),distinct_source_papers=len(case['source_papers']),
                relation_claims=sum(len(p['claim_ids']) for u in case['units'] for p in bench['paths_by_unit'][u]),
                unit_paths=unit_results,negative_checks=absent_checks))
        passed=sum(r['status']=='covered' for r in case_results)
        n06=next((r for r in case_results if r['case_id']=='N06'),None)
        if passed != 39 or n06 is None or n06['status']!='negative_anchor_absence_checked':
            raise ValueError('question_coverage_count_mismatch')
        db_hash=hashlib.sha256(path.read_bytes()).hexdigest()
        return dict(status='passed',benchmark=VERSION,graph_namespace='isolated SQLite; production graph untouched',
            question_coverage=dict(total=40,covered=passed,negative_no_corpus=1,failed=0),
            graph_counts=counts,source_claims=len(bench['graph_claims']),legacy_approved_claims=bench['prior_graph_snapshot']['claim_count'],
            exact_quote_claims=counts['claims'],
            source_units_verified=len(bench['units']),relation_paths_verified=sum(len(r['unit_paths']) for r in case_results),
            graph_sha256=db_hash,cases=case_results,
            limitations=['关系图针对冻结的 40 题和 25 个已核查来源单元，不是对全部 980 个块的穷尽抽取。',
                '每条边均保留整块精确原文及页码；审核是来源核对，不是独立人工专家审查。',
                'N06 的零来源检查不能证明语料外或未来材料中不存在该名称。'])
    finally:
        con.close()


def dataset_payload(bench, digest):
    examples=[]
    for case in bench['cases']:
        refs=[]
        for key in case['units']:
            u=bench['units'][key]
            refs.extend([{k:s[k] for k in ('chunk_id','paper_id','parse_id','title','source_relative_path',
                'page_start','page_end','source_spans','text_sha256','section','text')}
                for s in u['support_sources']])
        refs=list({x['chunk_id']:x for x in refs}.values())
        examples.append(dict(id=stable_id(digest,case['id']),inputs={'question':case['question']},
            outputs={'expected_answer':case['expected_answer'],'answerable':case['answerable'],
                'negative_kind':case['negative_kind'],'required_facts':[bench['units'][k]['answer_point'] for k in case['units']],
                'source_references':[{'unit_id':k,'answer_point':bench['units'][k]['answer_point'],
                    'paper_id':bench['units'][k]['paper_id'],'title':bench['units'][k]['title'],
                    'primary_chunk':bench['units'][k]['primary_chunk'],'pages':[bench['units'][k]['page_start'],bench['units'][k]['page_end']]}
                    for k in case['units']],
                'source_evidence':refs,'relation_outline':case['reasoning_chain'],
                'relation_review':case.get('relation_review'), 'must_not_claim':case['must_not_claim'],
                'scoring_rules':bench['scoring'],'expected_graph_paths':[bench['paths_by_unit'][k] for k in case['units']],
                'result_fields':['full answer','ranked candidates and scores','evidence and citation locations',
                    'graph paths','per-fact coverage and gaps','stage timings','tokens','paired differences','trace URLs']},
            metadata={'case_id':case['id'],'category':case['category'],'benchmark':VERSION,
                'benchmark_sha256':digest,'corpus_id':bench['corpus_id'],
                'review_origin':'curated source review; not independent human gold'},split=[case['category']]))
    return dict(name='papertech-stage4-'+VERSION,
        description='40 道关系路径覆盖开发题；题目、金标、完整来源块和位置与冻结哈希绑定。尚未运行模型对照。',
        metadata={'benchmark':VERSION,'benchmark_sha256':digest,'graph_schema_version':SCHEMA['schema_version'],
            'capture_scope':'question references, full source excerpts and location, expected graph paths and scoring rules',
            'no_model_comparison_run':True},examples=examples)


def render_questions(bench):
    lines=['# 阶段 4 关系路径覆盖题集 v3','',
        '共 40 题：8 道直接证据控制题、24 道跨论文关系路径题、8 道错误关系/无证据题。全题都设计为后续完整生成比较。',
        '本题集是接触过语料和历史失败的开发集；参考要点来自冻结原文，不是独立人工金标。此版本尚未运行 Hybrid / Hybrid+Graph 对照。','',
        '## 固定来源与判分','',
        '- 每个必要事实单元按任一已核查来源命中计覆盖；题目所需事实单元之间按 AND 计算。',
        '- 路径覆盖单独核查：关系方向、实体类型、来源块与页码均须匹配；引用格式正确不等于关系判断正确。',
        '- 反例题核对题干中的指定边是否缺乏来源，且区分“当前证据未建立”与“证明从未发生”。',
        '- 共享数据集不自动建立方法继承、因果、受控比较或普遍性能优越性。',
        '- 图边存储整块精确原文与来源位置；不能把自动生成的图路径当作原文直接声明。','',
        '## 逐题题干、金标和来源','']
    for c in bench['cases']:
        lines += [f"### {c['id']} · {c['category']}",'',c['question'],'',
            '**参考答案要点：** '+c['expected_answer'],'',
            '**必要事实：** '+('；'.join(bench['units'][k]['answer_point'] for k in c['units']) if c['units'] else '冻结语料无对应来源。'),'']
        if c.get('must_not_claim'):
            lines += ['**判分边界：** '+c['must_not_claim'],'']
        for key in c['units']:
            u=bench['units'][key]
            for s in u['support_sources']:
                lines.append(f"- `{key}`：{s['title']}，`{s['source_relative_path']}`，PDF 第 {s['page_start']}—{s['page_end']} 页，块 `{s['chunk_id']}`；完整片段见 benchmark.json 和对应 Example。")
        lines.append('')
    return '\n'.join(lines)


def render_graph_audit(audit):
    lines=['# v3 隔离图路径覆盖审计','',
        f"状态：`{audit['status']}`；覆盖 {audit['question_coverage']['covered']}/40 个有来源题，N06 单列为无语料来源负例；失败 {audit['question_coverage']['failed']}。",
        f"隔离图节点 {audit['graph_counts']['entities']}、有来源关系声明 {audit['graph_counts']['claims']}；精确引句 {audit['exact_quote_claims']} 条。SHA-256：`{audit['graph_sha256']}`。",'',
        '| 题号 | 类型 | 来源单元 | 论文数 | 核验关系边 | 状态 |','|---|---|---:|---:|---:|---|']
    for r in audit['cases']:
        lines.append(f"| {r['case_id']} | {r['category']} | {r['source_units']} | {r['distinct_source_papers']} | {r['relation_claims']} | {r['status']} |")
    lines += ['', '## 范围限制','']+[f'- {x}' for x in audit['limitations']]
    return '\n'.join(lines)+'\n'


def freeze():
    if TARGET.exists():
        raise RuntimeError('benchmark-v3 target exists; refusing to overwrite frozen artifacts')
    staging=TARGET.with_name(TARGET.name+'.building')
    if staging.exists():
        raise RuntimeError('benchmark-v3 staging target exists; inspect it before retrying')
    bench,chunks,paper_list=build_benchmark()
    staging.mkdir(parents=True)
    try:
        (staging/'graph-schema.json').write_text(json.dumps(SCHEMA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        graph_path=staging/'isolated-graph.sqlite3'
        legacy=load_legacy_claims(chunks,{p['paper_id']:p for p in paper_list},bench['corpus_id'])
        manifest=[dict(claim_id=c['claim_id'],paper_id=c['provenance']['paper_id'],chunk_id=c['provenance']['chunk_id'],
            predicate=c['predicate'],source_hash=c['source_hash']) for c in legacy]
        if len(legacy)!=bench['prior_graph_snapshot']['claim_count'] or digest_bytes(json.dumps(
                manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))!=bench['prior_graph_snapshot']['claim_manifest_sha256']:
            raise ValueError('prior_graph_snapshot_changed_after_blueprint')
        create_graph_db(graph_path,bench,{p['paper_id']:p for p in paper_list},chunks,legacy)
        audit=audit_graph(graph_path,bench,chunks)
        if audit['status']!='passed':
            raise RuntimeError('graph_coverage_audit_failed')
        bench['graph_build']={'database':'isolated-graph.sqlite3','schema_file':'graph-schema.json',
            'graph_sha256':audit['graph_sha256'],'claim_count':audit['graph_counts']['claims'],
            'node_count':audit['graph_counts']['entities'],'build_kind':'curated, source verified; no production graph writes'}
        raw=(json.dumps(bench,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        digest=digest_bytes(raw)
        (staging/'benchmark.json').write_bytes(raw)
        (staging/'benchmark.sha256').write_text(digest+'\n',encoding='ascii')
        payload=dataset_payload(bench,digest)
        atomic_json(staging/'langsmith-dataset.json',payload)
        (staging/'questions.md').write_text(render_questions(bench),encoding='utf-8')
        atomic_json(staging/'graph-path-coverage.json',audit)
        (staging/'graph-path-coverage.md').write_text(render_graph_audit(audit),encoding='utf-8')
        for example in payload['examples']:
            case_id=example['metadata']['case_id']
            atomic_json(staging/'cases'/(case_id+'.json'),example)
        atomic_json(staging/'langsmith-status.json',dict(benchmark=VERSION,benchmark_sha256=digest,
            status='local_dataset_ready_not_uploaded',examples_expected=40,model_comparison='not_run',
            note='Remote dataset sync is left for the comparison stage; no LangSmith experiment was created.'))
        staging.rename(TARGET)
    except Exception:
        shutil.rmtree(staging)
        raise
    print(json.dumps(dict(status='frozen',benchmark=VERSION,benchmark_sha256=digest,
        graph_sha256=audit['graph_sha256'],cases=40,graph_claims=audit['graph_counts']['claims'],
        graph_nodes=audit['graph_counts']['entities'],coverage='39/40 source-backed; N06 is explicit no-corpus negative',
        model_comparison='not_run'),ensure_ascii=False))


def check():
    raw=(TARGET/'benchmark.json').read_bytes()
    digest=digest_bytes(raw)
    if digest!=(TARGET/'benchmark.sha256').read_text(encoding='ascii').strip():
        raise ValueError('benchmark_hash_mismatch')
    bench=json.loads(raw)
    corpus_id,papers,chunks_list=load_corpus(ROOT)
    if bench['corpus_id']!=corpus_id:
        raise ValueError('active_corpus_changed_after_freeze')
    chunks={c['chunk_id']:c for c in chunks_list}
    summary=validate_benchmark(bench,chunks)
    legacy=load_legacy_claims(chunks,{p['paper_id']:p for p in papers},corpus_id)
    manifest=[dict(claim_id=c['claim_id'],paper_id=c['provenance']['paper_id'],chunk_id=c['provenance']['chunk_id'],
        predicate=c['predicate'],source_hash=c['source_hash']) for c in legacy]
    if len(legacy)!=bench['prior_graph_snapshot']['claim_count'] or digest_bytes(json.dumps(
            manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))!=bench['prior_graph_snapshot']['claim_manifest_sha256']:
        raise ValueError('prior_graph_snapshot_changed_after_freeze')
    if json.loads((TARGET/'graph-schema.json').read_text(encoding='utf-8'))!=SCHEMA:
        raise ValueError('schema_artifact_differs_from_script')
    audit=audit_graph(TARGET/'isolated-graph.sqlite3',bench,chunks)
    if audit['graph_sha256']!=bench['graph_build']['graph_sha256']:
        raise ValueError('isolated_graph_hash_mismatch')
    if audit['question_coverage']['failed']!=0:
        raise ValueError('question_path_audit_failed')
    if (TARGET/'questions.md').read_text(encoding='utf-8')!=render_questions(bench):
        raise ValueError('readable_question_export_mismatch')
    if (TARGET/'graph-path-coverage.md').read_text(encoding='utf-8')!=render_graph_audit(audit):
        raise ValueError('readable_graph_audit_mismatch')
    payload=dataset_payload(bench,digest)
    local=json.loads((TARGET/'langsmith-dataset.json').read_text(encoding='utf-8'))
    if local!=payload or len(local['examples'])!=40:
        raise ValueError('local_dataset_mismatch')
    print(json.dumps(dict(status='verified',benchmark=VERSION,benchmark_sha256=digest,
        graph_sha256=audit['graph_sha256'],counts=summary,coverage=audit['question_coverage'],
        model_comparison='not_run'),ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--freeze',action='store_true',help='write the immutable v3 benchmark and isolated graph')
    action.add_argument('--check-blueprint',action='store_true',help='validate candidate questions and source/path declarations without writes')
    action.add_argument('--check',action='store_true',help='verify frozen v3 hashes, examples and graph paths')
    args=parser.parse_args()
    if args.freeze:
        freeze()
    elif args.check_blueprint:
        bench,chunks,papers=build_benchmark()
        print(json.dumps(dict(status='blueprint_verified',validation=bench['validation'],
            distinct_sources=len({s['chunk_id'] for u in bench['units'].values() for s in u['support_sources']}),
            output_writes=0),ensure_ascii=False))
    else:
        check()


if __name__=='__main__':
    main()
