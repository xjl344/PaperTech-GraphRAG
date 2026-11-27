"""Prepare a source-first question preview. No retrieval, model calls or uploads."""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from papertech.corpus import load_corpus

TARGET = ROOT / 'artifacts/eval/stage-4/relation-holdout-draft-v1'
# Source aliases are chosen from the verified paper text, before graph auditing.
SOURCES = {
    'specificity': 'chunk_3847660df4256f0bd39f8b49c7b9864e',
    'synonym': 'chunk_008861356c216ab780f62dad7796e2d4',
    'hippolink': 'chunk_0b0bc328584472f90acf54bff3d926e1',
    'hippoablation': 'chunk_8245d0849e8cf0df364eb6980d96843c',
    'virtual': 'chunk_5832b6bfb3218fc28548dbb991a42540',
    'prizes': 'chunk_04c0673f276b70d320674636d537dc80',
    'grvector': 'chunk_8c5476c0307c733adb60d1afe861e4d2',
    'grfreeze': 'chunk_2da94a87e97c2e0f30e8eec5659e202d',
    'grabstract': 'chunk_3a7f7a1f47b2586d9d9877afb9110567',
    'grscale': 'chunk_5c9e14854565607ec53c355da481c451',
    'starkrank': 'chunk_bb730573725b148aa7913e7f17bb9261',
    'starkanswer': 'chunk_2c06f903c181ffbdb1246026daa909b0',
    'starkabstract': 'chunk_6b5383484693f6226010eab8143f80d6',
    'tog2start': 'chunk_362a4aa0f89367fe96563183423db354',
    'tog2rank': 'chunk_d4f6a4a037b6e147680603d67ba56fc0',
    'tog2': 'chunk_9b63637ef18ed2d67ff105ef55092df3',
    'mindprune': 'chunk_18e6db2a25659ad12b8e68e6cc51dfda',
    'mindpath': 'chunk_dd52fbf0ff0cc9bb75c0d06493e98a7a',
    'structresult': 'chunk_3a66017788061f8f662ca365c955591a',
    'struct': 'chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad',
    'structsize': 'chunk_296f2400fee163aad415c87ede01d3fa',
    'kggpttop': 'chunk_fbbb8f38df6e66a40727407ca912ae1a',
    'kggpt': 'chunk_61e96cb10e247f7d002b4163920cc737',
    'kgpbuild': 'chunk_1da329a96f21568de531f98b40b330e7',
    'kgpdensity': 'chunk_720b9036bf8c30eaf69c980fccbcec6d',
    'kgpcorrect': 'chunk_adcc17b94d9058357729c73998e78ba9',
    'kgp': 'chunk_b959214e888053dae53b16a5259d7ea9',
    'curious': 'chunk_43145c0748762d6b4c650c65721f826f',
    'curiousenc': 'chunk_69407b618c1969f701e74bd3cf523c95',
    'curiouserror': 'chunk_f58319afb1c636475f807715f48a7a93',
    'lpplan': 'chunk_072d1d7f534ffdbb7644a330aeea94fa',
    'lpbench': 'chunk_ab66789d9bc91de68948962d6c3f0011',
    'rog': 'chunk_58e7ae48fdb49536bc066f6e74ccd2a0',
    'rogbfs': 'chunk_3e71dc58ca336959686a576311cb5e3a',
    'tog': 'chunk_e09b5a88c34014513aad6c0d6121f790',
    'togr': 'chunk_91a4a2e6943ad6a8074492d3f7229692',
    'totstate': 'chunk_0cb3c2dcbacf18237a13b232366d2be8',
    'totbacktrack': 'chunk_50dee9a8765be04263849aca87ab67d3',
}


def blueprint():
    cases = []
    def add(cid, category, question, facts, novelty, form='named'):
        cases.append(dict(id=cid, category=category, question=question,
            reference_facts=[dict(source_alias=alias, requirement=text) for alias, text in facts],
            novelty=novelty, query_form=form))

    add('F01','fact','HippoRAG 的 node specificity 如何计算？一个概念出现的段落越多，权重如何变化，这个权重在 PPR 前还是后使用？',
        [('specificity','节点 i 的 specificity 为 1/|Pi|，Pi 是抽取出该节点的段落集合；出现段落越多权重越低；PPR 前与查询节点概率相乘。')], '新增节点加权细节')
    add('F02','fact','G-Retriever 怎样处理边奖励大于边成本、从而产生负边成本的情况？虚拟节点的奖励和新边成本如何设置？',
        [('virtual','Pe>Ce 时用虚拟节点替代原边，虚拟节点奖励 Pe-Ce，连接两个端点的新边成本为0。')], '新增优化算法实现细节')
    add('F03','fact','STaRK 的 LLM 重排实验对合成问题和人工问题分别重排多少候选？是否评测了全部测试问题，为什么？',
        [('starkrank','合成问题 k=20，人工问题 k=10；因计算成本高，只在随机10%测试问题上评测这些重排器。')], '新增评测范围与成本条件')
    add('F04','fact','ToG-2 在第一次图检索前做了哪些准备？如果初始文档已经足够回答，还必须进入图搜索吗？',
        [('tog2start','先实体链接、Topic Prune，再从初始主题实体关联文档中用稠密模型取 top-k 块；LLM 判断证据充分即可停止，无需进一步检索。')], '新增首次图检索前的早停顺序')
    add('F05','fact','MindMap 得到路径与邻居证据后，怎样减少信息过载并保留多样性？最终证据图怎样交给后续聚合阶段？',
        [('mindprune','按头实体聚类并对子图采样，裁剪路径与邻居证据图；LLM 再把不同证据子图合并为统一推理图。')], '新增剪枝及证据聚合细节')
    add('F06','fact','StructGPT 在 KGQA、TableQA 和 Text-to-SQL 中，返回结果一定都是自然语言答案吗？请区分可以直接回答和需要执行的输出。',
        [('structresult','三类任务分别处理KG、表格、数据库；结果可以是自然语言自由回答，也可以是需执行以取得答案的SQL等结构化表达式。')], '新增输出契约')
    add('F07','fact','KG-GPT 增大 top-k 关系数时，FACTKG 与 MetaQA 的效果是否相同？请区分检索三元组数量和任务准确率。',
        [('kggpttop','FACTKG 随k增加检索三元组增多但准确率变化不大；MetaQA 中更大的k检索到更多重要三元组，性能改善。')], '新增分任务消融结果')
    add('F08','fact','KGP 的 TF-IDF 建图什么时候连接两个段落？为什么把文档标题也加入关键词集合？',
        [('kgpbuild','先做TF-IDF关键词提取，加入文档标题因为部分问题关注标题实体；共享任一关键词的两个段落连接。')], '新增词法建图规则')

    add('R01','cross','G-Retriever 与 KG-GPT 所说的“图问答”是否对应同一种输出任务？比较前者对文本图的回答与可视定位，和后者的事实核验及 KGQA。',
        [('grabstract','G-Retriever 面向带文本属性的图，生成文本回答并标出相关图部分，涵盖场景图、常识及知识图推理。'),('kggpt','KG-GPT 用于KG事实验证及KGQA，通过分割、图检索、推理处理结构化知识。')], '已有事实的新任务/输出对齐，非全新事实')
    add('R02','cross','LPKG 和 RoG 都从 KG 学习规划，它们的计划表示能直接互换吗？分别说明自然语言子问题与关系路径怎样连接到后续执行。',
        [('lpplan','LPKG 把落地的KG模式转成复杂问题及自然语言子问题，训练后解析并执行计划。'),('rog','RoG 生成KG约束的关系路径计划，用于检索有效推理路径。')], '新增计划表示差异，不复问训练来源')
    add('R03','cross','CuriousLLM 与 StructGPT 的迭代步骤各会产出什么供下一步使用？比较“追问”和“读取后推理”，不要把中间产物都写成最终答案。',
        [('curious','CuriousLLM 用问题和支持证据生成后续问题来指导补充检索；充分时用特殊token。'),('struct','StructGPT 迭代接口调用、线性化与生成，接口负责读取证据，LLM负责推理。')], '已有机制的新跨论文中间产物组合')
    add('R04','cross','KGP 与 STaRK 的检索成功各指找到了什么？比较支持段落和答案实体，说明两者的召回分母为什么不能直接混用。',
        [('kgp','KGP 的图遍历代理检索支持段落，节点也可包含文档结构。'),('starkanswer','STaRK 以SKB中的节点实体为真值答案，不是论文支持段落。')], '新增不同检索对象的评价关系')
    add('R05','cross','MindMap 与 G-Retriever 都把图交给模型，但图结构进入模型的方式一样吗？比较 LLM 合并证据子图与 GAT、池化、MLP 的职责。',
        [('mindprune','MindMap 用LLM把证据子图合成统一推理图，再供后续生成。'),('virtual','G-Retriever 用GAT编码子图、均值池化得到图向量，再由MLP投影到LLM空间。')], '新增图表示到模型输入的对齐')
    add('R06','cross','ToG 的束搜索与 Tree-of-Traversals 的搜索状态回溯各保留什么选择机会？后者发现低价值状态后怎样换路？',
        [('tog','ToG 用LLM代理迭代执行图上的束搜索，探索实体关系与推理路径。'),('totbacktrack','Tree-of-Traversals 示例在低价值状态后回溯到最佳备选状态，再重新选择扩展。')], '新增失败后换路机制')
    add('R07','cross','请从论文库找出两种让“语义上相关的材料”在图中连起来的不同办法：一种连接不同叫法的概念，另一种学习相邻支持段落。分别说明建边依据和训练信号。',
        [('synonym','HippoRAG 用检索编码器表示的余弦相似度超过阈值来增加同义边。'),('kgpbuild','KGP 的MDR句子编码器学习由已知支持事实预测后续支持事实，再用嵌入相似构建KNN图。')], '新增建边细节组合及无方法名入口', 'discovery')
    add('R08','cross','ToG-2 和 STaRK 都使用重排模型。前者对实体上下文数量的分析与后者的候选重排设置，分别暴露了哪些成本或输入长度限制？',
        [('tog2rank','ToG-2 增加上下文时BGE重排器收益较好，而LLM有效性下降，作者指出LLM受输入长度限制并考虑成本。'),('starkrank','STaRK 的LLM重排因成本高仅测试随机10%问题，合成/人工候选数为20/10。')], '新增重排条件及资源限制')
    add('R09','cross','HippoRAG 的“查询节点加邻居”消融与 KG-GPT 的 top-k 关系实验，是否支持“取更多邻居必然更好”？分别说明结果及适用任务。',
        [('hippoablation','HippoRAG 不做PPR而直接加查询邻居的替代方法，比只用查询节点更差。'),('kggpttop','KG-GPT FACTKG 增大k准确率变化不大，MetaQA 增大k表现改善。')], '新增跨论文消融关系')
    add('R10','cross','请找两篇直接讨论图证据冗余的工作：一篇分析图变密后支持事实覆盖与精度的取舍，另一篇通过聚类、采样保持多样性。它们分别控制哪个阶段？',
        [('kgpdensity','KGP 图变密时支持事实覆盖上升而精度下降；这是建图/邻居候选的取舍。'),('mindprune','MindMap 对已探索的路径和邻居证据子图聚类采样，属于证据选择与压缩。')], '新增冗余控制与无方法名入口', 'discovery')
    add('R11','cross','面对结构化材料放不进提示词的问题，G-Retriever 与 StructGPT 分别在哪一步缩小输入？比较子图检索和专门接口过滤，说明它们是否都需要先把整库文本化。',
        [('grscale','G-Retriever 通过相关子图选择缓解整图文本化超窗口或截断丢信息的问题。'),('structsize','StructGPT 指出整份结构化数据线性化太大，以专门接口操纵和缩小所需记录范围。')], '新论文组合的输入裁剪位置比较')
    add('R12','cross','ToG-R 与 ToG-2 对候选实体分别更依赖哪类信息？比较随机实体剪枝与文档提供的实体上下文，说明两者不能视作同一种实体筛选。',
        [('togr','ToG-R 以随机实体剪枝替代ToG中的LLM实体剪枝。'),('tog2','ToG-2 以文档作为实体上下文以支持图检索，并用实体联接文档。')], '已有关系的新实体消歧/筛选组合')
    add('R13','cross','CuriousLLM 复用的 MDR 段落编码器与 HippoRAG 的同义边编码器，分别学习或比较什么？请区分“下一段支持证据”和“概念名称相似”。',
        [('curiousenc','CuriousLLM 延用MDR训练，使用HotpotQA学习支持段落对接近、无关段落远离以建图。'),('synonym','HippoRAG 对抽取的概念表示计算余弦相似度，用阈值增加同义边。')], '新增编码器目标与粒度比较')
    add('R14','cross','RoG 的受约束广度优先搜索与 Tree-of-Traversals 的动作状态机怎样分别限制下一步动作？比较预先关系序列与可行操作空间。',
        [('rogbfs','RoG 从问题实体出发，沿计划的关系序列执行受约束BFS，检索有效推理路径。'),('totstate','Tree-of-Traversals 的ASM定义与KG交互的可行动作、状态及提示模板；树搜索管理搜索轨迹和回溯。')], '新增搜索可行性约束比较')
    add('R15','cross','LPKG 的 CLQA-Wiki 与 STaRK 各想补足什么评测缺口？比较交并逻辑覆盖和文本属性＋关系条件的组合，并指出真值对象差异。',
        [('lpbench','CLQA-Wiki 覆盖多跳、比较、交集、并集，强调逻辑操作及可能多答案。'),('starkabstract','STaRK 将关系条件与复杂文本属性一起构造自然查询，真值是答案条目/实体。')], '已有来源的新需求/答案约束组合')
    add('R16','cross','StructGPT 与 KG-GPT 处理结构化信息时，哪些任务需要生成可执行表达式，哪些需要判断事实或给出图问答答案？据此比较两者的任务边界。',
        [('structresult','StructGPT 覆盖KGQA、TableQA、Text-to-SQL，可输出待执行的SQL表达式。'),('kggpt','KG-GPT 针对KG事实验证与KGQA，不凭此推断其具备数据库SQL生成能力。')], '新增可执行输出与事实判断关系')
    add('R17','cross','KGP 为什么用真实邻居段落去匹配模型预测的下一条证据？结合 CuriousLLM 对原 KGP 错误关键词的观察，说明模型生成的“缺失证据”为什么仍需回取原文。',
        [('kgpcorrect','KGP 示例中模型可预测错误出生日期，再从真实文档邻居匹配段落以纠正；预测证据不是已核实原文。'),('curiouserror','CuriousLLM 作者观察原KGP虽能猜到缺失证据，仍可能使用无关或错误关键词而妨碍检索。')], '新增原始论文与后续分析交叉核对')
    add('R18','cross','请从论文库举两个“图方法仍使用向量”的例子：一个用于把问题实体映射到图节点，另一个用于检索相关节点和边。比较向量所在的阶段，不能只回答方法名。',
        [('hippolink','HippoRAG 编码问题命名实体，用最高余弦相似度匹配KG节点。'),('grvector','G-Retriever 编码问题及节点/边属性，用KNN和余弦相似度选top-k节点/边。')], '新增图内向量角色与无方法名入口', 'discovery')
    add('R19','cross','G-Retriever 冻结 LLM 的软提示训练与 ToG-2 的 training-free 分别意味着什么？比较是否训练其他组件，避免仅凭底座参数不变就判定整套系统免训练。',
        [('grfreeze','G-Retriever 冻结LLM但以GNN输出的软提示做高效微调。'),('tog2','ToG-2 将自身描述为training-free且可即插即用不同LLM。')], '新增冻结底座与系统训练条件差异')
    add('R20','cross','ToG 的 training-free 和 StructGPT 的 zero-shot/few-shot 是同一个分类维度吗？结合两篇方法描述，区分参数更新与提示中示例数量。',
        [('tog','ToG 自述training-free，无需额外训练。'),('struct','StructGPT 报告zero-shot和few-shot设置，利用接口迭代读取和推理；示例数和参数更新是不同描述维度。')], '已有来源的新设置维度关系；维度区分为审查解释')
    add('R21','cross','KGP 预测下一段证据与 RoG 生成关系路径后，分别怎样约束实际检索？比较邻居段落的相似匹配与沿关系序列的图搜索。',
        [('kgpcorrect','KGP 将预测证据与真实邻居匹配，选择相似的文档段落。'),('rogbfs','RoG 从问题实体沿关系序列进行受约束BFS。')], '新增检索约束实现比较，不复问总体流程')
    add('R22','cross','MindMap 的证据图合并和 CuriousLLM 的追问各会怎样改变后续可用信息？区分重组织已有证据与请求继续找证据。',
        [('mindprune','MindMap 先裁剪，再由LLM合并已取得的证据子图成统一推理图。'),('curious','CuriousLLM 用追问指出还缺什么以指导后续检索，证据足够则产生特殊信号。')], '新增证据加工与补充证据的职责对齐')
    add('R23','cross','请找出一项按候选答案条目集合衡量 Recall@k 的工作，以及一项可能生成 SQL 的结构化问答工作。为什么前者的 Recall@k 不能直接作为后者的 SQL 执行正确率？',
        [('starkrank','STaRK Recall@k 计算top-k结果里相关条目的比例。'),('structresult','StructGPT 可生成需执行得到答案的SQL；执行正确率与条目召回不是同一指标。')], '新增评价对象/执行语义与无方法名入口', 'discovery')
    add('R24','cross','HippoRAG 的节点 specificity、G-Retriever 的节点/边奖励、KG-GPT 的 top-k 参数分别改变了什么？按“排序权重、子图优化、候选数量”对齐，并说明三者不能共用一个参数。',
        [('specificity','HippoRAG specificity 在PPR前调整查询节点概率。'),('prizes','G-Retriever 依据相关性给节点/边奖励，在连通子图优化中折中奖励和边成本。'),('kggpttop','KG-GPT 的top-k决定关系检索范围，改变检索三元组数量。')], '新增三论文参数作用位置比较')

    add('N01','negative','“只要使用知识图谱，系统就不会再用向量相似度。”HippoRAG 与 G-Retriever 的方法细节能支持这句话吗？',
        [('hippolink','不能：HippoRAG 使用向量余弦相似匹配查询实体与节点。'),('grvector','G-Retriever 用向量相似和KNN检索节点与边。')], '新增图与向量互斥的错误前提')
    add('N02','negative','G-Retriever 冻结了 LLM，所以它没有任何需要训练的组件，也不使用软提示。这一说法符合原文吗？',
        [('grfreeze','不符合：冻结LLM但使用GNN输出的软提示进行高效微调。')], '新增训练组件归因反例')
    add('N03','negative','KGP 的图越密，支持事实覆盖和精度就必定一起提高；MindMap 因而也无需裁剪证据。请核对两项前提。',
        [('kgpdensity','KGP 观察图更密时覆盖上升但精度下降。'),('mindprune','MindMap 为控制过载和保留多样性进行聚类、采样及剪枝。')], '新增密度/精度单调性反例')
    add('N04','negative','STaRK 的 GPT-4 和 Claude3 重排器是在全部测试问题上、用相同候选数评测的吗？请指出这个说法省略的条件。',
        [('starkrank','只用随机10%测试问题；合成问题k=20，人工问题k=10，不能宣称全量同k实验。')], '新增实验子样本前提反例')
    add('N05','negative','HippoRAG 的消融已经证明，只要把查询节点的一跳邻居都加进来，就一定比只用查询节点效果好。原文是否这样报告？',
        [('hippoablation','不是：不做PPR直接加入邻居的替代方法比仅使用查询节点更差。')], '新增算法替代实验方向反例')
    add('N06','negative','KGP 中模型预测的下一段证据能直接当作已核查原文引用吗？请用论文关于出生日期的例子检查。',
        [('kgpcorrect','不能：示例生成的日期4月16日不正确，实际文档为3月28日；需要匹配真实邻居原文，预测文本不能当引用。')], '新增生成证据与来源混淆反例')
    add('N07','negative','ToG-2 无论初始文档是否充分，都必须先完成一次图遍历才能回答。请检查它首次检索前后的控制流程。',
        [('tog2start','不成立：首次图检索前先检索主题实体关联文档；LLM判断足够即可停止。')], '新增早停顺序反例')
    add('N08','negative','StructGPT 的所有任务都必须直接输出自然语言答案，因此它不涉及需要执行的 SQL。请核对原文的任务和结果定义。',
        [('structresult','不成立：包含Text-to-SQL，可返回需执行的SQL结构表达式。')], '新增输出类型反例')
    return cases


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    corpus, papers, rows = load_corpus(ROOT)
    chunks = {c['chunk_id']: c for c in rows}
    cases = blueprint()  # No graph reads while selecting questions and facts.
    assert len(cases) == len({c['id'] for c in cases}) == len({c['question'] for c in cases}) == 40
    assert Counter(c['category'] for c in cases) == Counter(fact=8, cross=24, negative=8)
    old = []
    for v in ('benchmark-v1', 'benchmark-v2', 'benchmark-v3', 'benchmark-v4'):
        old.extend(json.loads((ROOT / f'artifacts/eval/stage-4/{v}/benchmark.json').read_text(encoding='utf-8'))['cases'])
    assert not {c['question'] for c in cases} & {c['question'] for c in old}
    for c in cases:
        ids = list(dict.fromkeys(SOURCES[f['source_alias']] for f in c['reference_facts']))
        c['source_chunk_ids'] = ids
        c['source_papers'] = list(dict.fromkeys(chunks[cid]['paper_id'] for cid in ids))
        if c['category'] == 'cross':
            assert len(c['source_papers']) >= 2, c['id']
        c['criteria'] = [dict(id=f'{c["id"]}.C{i:02}', requirement=f['requirement'],
            source_chunk_id=SOURCES[f['source_alias']], score_values=[0, 1])
            for i, f in enumerate(c['reference_facts'], 1)]
        c['answer_review'] = '参考要点为Codex对原文的整理，待用户审阅；推论与作者实验报告须区分。'
    used = set(cid for c in cases for cid in c['source_chunk_ids'])
    source_records = {cid: {k: chunks[cid][k] for k in ('chunk_id','paper_id','parse_id','title','text',
        'text_sha256','source_relative_path','page_start','page_end','source_spans')} for cid in used}
    for src in source_records.values():
        assert hashlib.sha256(src['text'].encode()).hexdigest() == src['text_sha256']
        assert src['text'] and src['page_start'] and src['source_spans']
    content = dict(version='relation-holdout-draft-v1', status='draft_for_user_review_not_run',
        arms=['Graph-only','Hybrid'], excluded_arms=['Dense-only'], corpus_id=corpus,
        distribution=dict(Counter(c['category'] for c in cases)), cases=cases, sources=source_records,
        proposed_protocol=dict(stage='retrieval_only', generation=False, graph_updates=False,
            entity_alias_updates=False, model_or_threshold_tuning=False,
            candidate_max=40, hybrid_channels='fulltext20+dense20', graph_hops=2,
            evidence_bytes=6000, evidence_max=8, prompt_paths=False,
            candidate_pool_scoring='verify all necessary atomic facts; audit equivalent sources before freezing',
            negative_policy='show source retrieval only; exclude from main positive recall; no answer/refusal score',
            reporting='two experiments linked to one dataset; aggregate+category+paired per-case deltas+bootstrap CI+latency+usage+traces',
            scoring_gate='No performance claims before execution; predeclare primary cross-question final fact-source coverage; report zero for no anchors.'),
        design_notes=['题目先按原文起草，之后才审计冻结图来源关联；未调用检索链路或模型。',
            '保留同语料与已整理图，只能称为新问题迁移诊断，不能称为独立盲测或未见语料测试。',
            '新细节考点与已知事实新组合并存；不是简单改写旧40题，也不宣称所有必要事实首次出现。',
            '用户审阅前不创建正式benchmark、不上传Dataset、不创建Experiment、不运行检索或答案生成。'])
    # Persist source-first content before consulting graph membership.
    write(TARGET / 'questions-draft.json', content)
    graph_path = ROOT / 'artifacts/eval/stage-4/benchmark-v3/isolated-graph.sqlite3'
    graph_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    con = sqlite3.connect(graph_path.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        linked = {json.loads(r[0])['chunk_id'] for r in con.execute('SELECT provenance_json FROM claims')}
    finally:
        con.close()
    coverage = []
    for c in cases:
        ids = set(c['source_chunk_ids'])
        n = len(ids & linked)
        coverage.append(dict(case_id=c['id'], category=c['category'], required_source_blocks=len(ids),
            graph_linked_blocks=n, linked_chunk_ids=sorted(ids & linked),
            status='all_source_blocks_linked' if n == len(ids) else 'some_source_blocks_linked' if n else 'no_source_blocks_linked'))
    audit = dict(graph_sha256=graph_hash, per_case=coverage,
        counts=dict(Counter(c['status'] for c in coverage)),
        cross_counts=dict(Counter(c['status'] for c in coverage if c['category']=='cross')),
        limitation='只审计支持原文块是否挂到任何Claim；不能据此说必要事实的边已存在、可两跳到达或会被召回。题目未根据该审计调整。',
        question_selection_before_graph_audit=True, retrieval_calls=0, model_calls=0, uploads=0)
    write(TARGET / 'source-link-audit.json', audit)
    question_sha = hashlib.sha256((TARGET / 'questions-draft.json').read_bytes()).hexdigest()
    write(TARGET / 'draft-manifest.json', dict(status='draft_not_benchmark', questions_sha256=question_sha,
        graph_sha256=graph_hash, source_count=len(used), cases=40, exact_duplicates_with_history=0,
        semantic_overlap='部分已有事实采用新组合，逐题novelty中披露；非独立盲测',
        retrieval_calls=0, model_calls=0, langsmith_uploads=0))
    headings = {'fact':'8道基础控制题', 'cross':'24道跨论文关系题', 'negative':'8道错误前提核对题'}
    lines = ['# 新题目预览：Graph-only 与 Hybrid', '',
        '**状态：草案，供用户审阅；未运行检索、未调用模型、未上传。**', '',
        '新一轮只保留 Graph-only 与 Hybrid；历史三组记录原样保留。', '',
        '8道事实控制＋24道跨论文关系＋8道错误前提核对。同一14篇论文、同一冻结图。',
        '本轮换具体考点与论文组合，不以旧题换说法。部分事实已被接触，不能称作独立盲测。', '',
        '先按原文拟题，再审计图中来源关联；不按哪组能赢来换题，不补图、不补别名。', '',
        '## 题目清单', '']
    for category, heading in headings.items():
        lines += [f'### {heading}', '']
        lines += [f'- **{c["id"]}** {c["question"]}' for c in cases if c['category']==category]
        lines.append('')
    lines += ['## 审阅提示与后续口径', '',
        '- 主指标拟为24道跨论文题的最终必要事实来源覆盖；同时报告候选召回、整题全覆盖和退化题。',
        '- 8道反例本轮只核查来源召回，不以其检索结果判断模型是否纠正前提。',
        '- 无实体锚点须计失败；Graph-only不回退Hybrid，不为新题补边/改别名。',
        '- 草案来源为已核查的最小支持集合，并非全库穷尽金标。执行前需审核等价来源及完整原子事实。',
        '- 原文块被图关联不等于本题事实已经建边；不把下面的静态审计当作预计分数。',
        f'- 关系题来源块关联分布：{audit["cross_counts"]}。详见 source-link-audit.json。',
        '- 审阅完成后另冻正式版本与SHA-256，先核对LangSmith Dataset再运行两组Experiment。', '',
        '## 每题参考要点、完整来源与位置', '']
    for c in cases:
        lines += [f'### {c["id"]}', '', c['question'], '', '**参考要点（待审）：**', '']
        lines += [f'- {f["requirement"]}（{SOURCES[f["source_alias"]]}）' for f in c['reference_facts']]
        lines += ['', '**相对旧题：** '+c['novelty'], '']
        for cid in c['source_chunk_ids']:
            s = source_records[cid]
            lines += [f'**来源：** {s["title"]}；PDF物理页 {s["page_start"]}–{s["page_end"]}；`{s["source_relative_path"]}`；`{cid}`', '',
                '**字符位置：** `'+json.dumps(s['source_spans'],ensure_ascii=False)+'`', '', '```text', s['text'], '```', '']
    (TARGET / 'questions.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    page = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>新关系题草案</title>',
        '<style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 24px;line-height:1.7}details{border:1px solid #ccd5df;padding:12px;margin:10px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f0f4f8;padding:12px}.note{color:#526174}summary{cursor:pointer}</style>',
        '<h1>Graph-only / Hybrid 新题目草案</h1><p><b>未运行检索或模型；未上传LangSmith。</b>40题，8事实＋24跨论文关系＋8前提核对。</p>',
        '<p class="note">新一轮不含Dense-only。题目先按原文起草，随后只做图来源关联审计；同一语料与已接触事实，不能称为独立盲测。点击每题可查参考要点、完整原文与位置。</p>']
    for category, heading in headings.items():
        page.append('<h2>'+heading+'</h2>')
        for c in cases:
            if c['category']!=category: continue
            page.append(f'<details id="{c["id"]}"><summary><b>{c["id"]}</b> {html.escape(c["question"])}</summary>')
            page.append('<p>新考点：'+html.escape(c['novelty'])+'</p><ul>')
            page.extend('<li>'+html.escape(f['requirement'])+'</li>' for f in c['reference_facts'])
            page.append('</ul>')
            for cid in c['source_chunk_ids']:
                s=source_records[cid]
                page.append('<details><summary>'+html.escape(s['title'])+f'；PDF页{s["page_start"]}–{s["page_end"]}</summary><pre>'+html.escape(json.dumps(s,ensure_ascii=False,indent=2))+'</pre></details>')
            page.append('</details>')
    page.append('</html>')
    (TARGET / 'questions.html').write_text('\n'.join(page), encoding='utf-8')
    print(json.dumps(dict(status='draft_ready_not_run', cases=40, arms=content['arms'], sources=len(used),
        categories=content['distribution'], source_link_audit=audit['counts'], cross_source_link_audit=audit['cross_counts'],
        directory=str(TARGET), retrieval_calls=0, model_calls=0, uploads=0),ensure_ascii=False))


if __name__ == '__main__':
    main()
