"""Freeze an original-text evidence set before any stage-4 retrieval run."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from papertech.corpus import load_corpus
from papertech.ingest import atomic_json
from papertech.settings import settings
from papertech.audit import now

# Each unit is an independently checked source fact, not an edge copied as truth.
U={
 'pcst':('chunk_3a7f7a1f47b2586d9d9877afb9110567','G-Retriever 将图检索表述为 Prize-Collecting Steiner Tree 优化。',['Prize-Collecting Steiner Tree']),
 'kggpt':('chunk_61e96cb10e247f7d002b4163920cc737','KG-GPT 三步为 Sentence Segmentation、Graph Retrieval、Inference。',['Sentence','Segmentation','Graph Retrieval','Inference']),
 'struct':('chunk_5e3e5be8ab828aaf3e59c9fdf0aae2ad','StructGPT 采用 Iterative Reading-then-Reasoning，专门接口读证据后交给 LLM 推理。',['Iterative Reading-then-','Reasoning','specialized interfaces']),
 'stark':('chunk_6b5383484693f6226010eab8143f80d6','STaRK 覆盖产品搜索、学术论文搜索和精准医疗。',['product','academic paper','precision medicine']),
 'roadmap':('chunk_f9acd01074a4f478a8d9fe8c7e77be91','三类路线为 KG-enhanced LLMs、LLM-augmented KGs、Synergized LLMs + KGs。',['KG-enhanced LLMs','LLM-augmented KGs','Synergized LLMs']),
 'totmusic':('chunk_f4962498025654850621ee329d0af7d6','MusicBrainz-x-Wikidata 有 109 题，需要结合 MusicBrainz 与 Wikidata。',['109 questions','MusicBrainz','Wikidata']),
 'lpbench':('chunk_ab66789d9bc91de68948962d6c3f0011','CLQA-Wiki 来自 Wikidata 子集，覆盖 multi-hop、comparison、intersection、union。',['Wikidata','multi-hop','comparison','intersection','union']),
 'mind':('chunk_2f4809d54362f998c1c0710e915a721b','MindMap 合并 LLM 隐式知识与外部 KG，以 mind map 展示推理路径，重点包括医学问答。',['implicit and external knowledge','medical domains']),
 'tog2':('chunk_9b63637ef18ed2d67ff105ef55092df3','ToG-2 通过实体连接文档，用文档作为实体上下文，交替进行图检索与上下文检索。',['link documents via entities','alternates','context retrieval']),
 'hippo':('chunk_a58244558a2137d85a4b8e53d5c4ebaf','HippoRAG 抽取查询关键概念，以它们为种子在 KG 上运行 PPR，跨片段整合信息。',['query concepts as the seeds','Personalized PageRank']),
 'curious':('chunk_43145c0748762d6b4c650c65721f826f','CuriousLLM 生成后续问题查缺补漏；Follow-upQA 用问题和证据作输入、后续问题作真值，也用特殊 token 表示证据充分。',['Follow-upQA','follow-up','special tokens']),
 'rog':('chunk_58e7ae48fdb49536bc066f6e74ccd2a0','RoG 先生成 KG 约束的关系路径计划，再检索有效推理路径供 LLM 推理。',['relation paths','faithful plans','retrieve valid reasoning']),
 'kgp':('chunk_b959214e888053dae53b16a5259d7ea9','KGP 的节点为段落或文档结构，边为语义/词法相似或结构关系，LLM 遍历代理收集支持段落。',['nodes symbolizing passages','edges denoting','traversal agent']),
 'totbound':('chunk_dac5f23e1b87249cf88eff5c6cc54355','Tree-of-Traversals 用 max depth 和 max expansions 控制搜索，达到扩展限额时返回 Cannot find answer。',['max depth','max expansions','Cannot find answer']),
 'grscale':('chunk_5c9e14854565607ec53c355da481c451','整图文本化会超过上下文窗口，直接截断丢信息；G-Retriever 选择相关子图以扩展到大图。',['surpassing the input capacity','truncating','selectively retrieving']),
 'lpdata':('chunk_e07b345ba2a42d01f295e47f196061d5','LPKG 从 KG 构造 planning data，用于微调小模型的复杂问答规划能力。',['planning data','derived from knowledge graphs','fine-tuned']),
 'tog':('chunk_e09b5a88c34014513aad6c0d6121f790','ToG 将 LLM 当作代理，迭代执行 KG beam search 探索实体/关系和推理路径，免额外训练。',['beam search','without','training']),
 'togr':('chunk_91a4a2e6943ad6a8074492d3f7229692','ToG-R 用随机实体剪枝替代 LLM 实体剪枝；ToG 调用数 2ND+D+1，ToG-R 为 ND+D+1。',['2ND + D + 1','ND + D + 1','random entity pruning']),
 'togds':('chunk_deb9eea46e529705dffdd1103729c44c','ToG 在 KBQA 中使用 WebQSP、QALD10-en，也覆盖 Creak；共同数据集不保证一致实验条件。',['WebQSP','QALD10-en','Creak']),
 'tog2ds':('chunk_16f86a00cebdf5e10d83c3a540fbc7f7','ToG-2 实验包含 WebQSP、QALD10-en、AdvHotpotQA 等，不能仅据数据集名称判定胜负。',['WebQSP','QALD','AdvHotpotQA']),
 'hippods':('chunk_3fa28005a4df0de5249826585cf9d713','HippoRAG 主要评估 MuSiQue(answerable)、2WikiMultiHopQA，也纳入 HotpotQA。',['MuSiQue','2WikiMultiHopQA','HotpotQA']),
 'totds':('chunk_a8ce6be635ba6abbbc71daeb86e809e9','Tree-of-Traversals 在 2WikiMultiHop、QALD-10 评估。',['2WikiMultiHop','QALD-10']),
 'kggptds':('chunk_3f7eb65828761447433c66c28ad111a4','KG-GPT 表中包含 FACTKG 与 MetaQA(Hits@1)。',['FACTKG','MetaQA']),
 'rogmeta':('chunk_f5c88d605f651f26c093f30b836a98aa','RoG 的迁移/扩展实验选 MetaQA-3hop，基于 Wiki-Movies，并取 1000 个训练样本。',['MetaQA-3hop','1000 samples','Wiki-Movies']),
}

SPECS=[
 ('F01','fact','G-Retriever 把相关子图检索形式化成什么优化问题？',['pcst']),
 ('F02','fact','KG-GPT 的三个处理步骤分别是什么？',['kggpt']),
 ('F03','fact','StructGPT 的 IRR 全称是什么，接口与 LLM 分别负责什么？',['struct']),
 ('F04','fact','STaRK 检索基准覆盖哪三个应用领域？',['stark']),
 ('F05','fact','Unifying Large Language Models and Knowledge Graphs: A Roadmap 将融合路线分成哪三类？',['roadmap']),
 ('F06','fact','Tree-of-Traversals 的 MusicBrainz-x-Wikidata 有多少题，涉及哪两个知识来源？',['totmusic']),
 ('F07','fact','LPKG 提出的 CLQA-Wiki 来自什么知识图谱，覆盖哪些逻辑题型？',['lpbench']),
 ('F08','fact','MindMap 如何结合模型内部知识和外部知识，论文重点提到哪个问答领域？',['mind']),
 ('P01','paraphrase','ToG-2 怎样让结构化关系与文档段落互相帮助检索，而不是把两路结果简单拼接？',['tog2']),
 ('P02','paraphrase','HippoRAG 怎样从问题中的关键概念出发，在一次检索里关联分散段落？',['hippo']),
 ('P03','paraphrase','CuriousLLM 如何判断还缺哪些材料，训练这种追问能力的数据输入与目标是什么？',['curious']),
 ('P04','paraphrase','RoG 在真正回答问题前先安排什么路线，随后怎样沿路线找可靠材料？',['rog']),
 ('P05','paraphrase','KGP 如何把多文档片段组织成可以导航的网络，网络节点、连线与导航者各是什么？',['kgp']),
 ('P06','paraphrase','Tree-of-Traversals 如何防止一直搜索下去，达到搜索预算后怎么处理？',['totbound']),
 ('P07','paraphrase','G-Retriever 为什么不把整个大图直接转成文本或截断后交给模型，它如何控制输入规模？',['grscale']),
 ('P08','paraphrase','LPKG 不依赖大量人工编写的分解示范时，从哪里获得规划训练信号，用它改善什么能力？',['lpdata']),
 ('C01','cross','比较 ToG 与 ToG-2 的知识检索机制：前者怎样探索图，后者怎样联动图与文档？分别引用两篇论文。',['tog','tog2']),
 ('C02','cross','比较 HippoRAG 和 RoG：前者用什么图算法整合信息，后者如何用关系路径制定计划？不要把关联解释为继承。',['hippo','rog']),
 ('C03','cross','比较 ToG 和 ToG-2 的评估数据集：各自是否包含 WebQSP 与 QALD10-en，能否仅据共同数据集断定谁更好？',['togds','tog2ds']),
 ('C04','cross','比较 HippoRAG 与 Tree-of-Traversals 的多跳测试集：两文分别使用什么名称的 2Wiki 数据集，还有哪些测试集？保留原文名称差异。',['hippods','totds']),
 ('C05','cross','比较 KG-GPT 与 RoG 对 MetaQA 的评估：前者出现什么基准和指标，后者扩展实验是哪种跳数、什么知识来源？',['kggptds','rogmeta']),
 ('C06','cross','比较 KGP 和 CuriousLLM 的下一步证据搜索：KGP 的图遍历代理怎样收集段落，CuriousLLM 怎样利用后续问题？',['kgp','curious']),
 ('C07','cross','ToG-R 相对 ToG 改了什么剪枝方式，两者 LLM 调用次数公式怎样变化？这是作者的效率主张还是所有场景的已证优越性？',['togr']),
 ('C08','cross','比较 StructGPT 和 LPKG：谁用接口迭代读取结构化证据，谁用 KG 构造的数据训练规划能力？',['struct','lpdata']),
 ('N01','negative','请给出 NebulaGraphRAG-2099 在 LunarQA-2099 的官方精确准确率。',[]),
 ('N02','negative','根据这14篇论文，告诉我今天北京实时气温是多少。',[]),
 ('N03','negative','ToG-2 是否已经证明在所有任务、所有底座模型上都严格优于 ToG？请检查这个前提，不能把部分实验外推到所有场景。',['togds','tog2ds']),
 ('N04','negative','请从这些论文给出作者 DeepSeek 服务账户的 API 密钥和本月账单金额。',[]),
]
GENERATE={'F01','F04','P03','P07','C01','C03','C05','N01','N02','N03'}


def norm(s):return ' '.join(s.casefold().split())


def main():
    target=ROOT/'artifacts/eval/stage-4/benchmark-v1'
    if target.exists():raise RuntimeError('frozen_benchmark_exists_no_overwrite')
    corpus,papers,chunks=load_corpus(ROOT); cmap={c['chunk_id']:c for c in chunks}
    units={}
    for name,(cid,answer,terms) in U.items():
        source=cmap[cid]
        if not all(norm(term) in norm(source['text']) for term in terms):
            raise ValueError('gold_anchor_not_in_source:'+name)
        alternatives=[c['chunk_id'] for c in chunks if c['paper_id']==source['paper_id']
                      and c['content_kind']!='references' and all(norm(t) in norm(c['text']) for t in terms)]
        units[name]=dict(id=name,answer_point=answer,primary_chunk=cid,known_support_chunks=alternatives,
            paper_id=source['paper_id'],title=source['title'],page_start=source['page_start'],page_end=source['page_end'],
            source_text=source['text'],anchor_terms=terms)
    cases=[dict(id=cid,category=cat,question=q,units=keys,generate=cid in GENERATE,
                answerable=cat!='negative',negative_kind='unsupported_universal_claim' if cid=='N03' else 'no_corpus_answer' if cat=='negative' else None)
           for cid,cat,q,keys in SPECS]
    cfg=settings(ROOT)
    paths=list((ROOT/'src/papertech').glob('*.py'))+[Path(__file__)]
    contract=dict(version='benchmark-v1',frozen_at=now(),corpus_id=corpus,papers=len(papers),chunks=len(chunks),
        author='Codex delegated source review, not an independent human benchmark',
        prior_exposure='Stage3 previously used ToG/ToG-2 and HippoRAG examples; this is a development evaluation, not a held-out benchmark.',
        cases=cases,units=units,models={k:cfg.get(k) for k in ('CLOUD_BGE_PROVIDER','CLOUD_BGE_MODEL','DEEPSEEK_MODEL','LOCAL_RERANKER_DEVICE','LOCAL_RERANKER_DTYPE')},
        controls=dict(fulltext_top=20,dense_top=20,candidates=40,evidence_max=8,context_bytes=6000,hops=2,degree=8,graph_paths=40,
                      rerank_threshold=.05,max_pair_tokens=1024,rrf_k=60,query_vectors='one batched cloud call, reused unchanged across paired arms',
                      order='odd numbered case Hybrid first, even Graph first; one warmup; no response retries',generation_subset=sorted(GENERATE)),
        scoring=dict(primary='macro SupportRecall@5: fraction of required evidence units with any known supporting chunk among top5 reranked candidates',
          secondary=['SupportRecall@8','MRR@40: reciprocal first rank containing any known supporting unit','selected evidence unit coverage','all-units coverage'],
          denominator='24 answerable questions; negatives separately; negatives with counterevidence excluded from recall aggregate',
          relevance='known source support pool, not exhaustive relevance judgments; absence from pool does not prove irrelevance',
          latency='retrieval compute measured around production methods, excludes audit stage uploads and shared cloud embedding batch; generation separately timed incl provider tracing',
          p95='numpy linear quantile over 24 single runs per arm, descriptive and unstable; not SLA or significance',
          answer_review='10 frozen pairs; source-based delegated review of keypoints, citation support and gaps; no automated LLM judge; no acceptance threshold invented',
          interpretation='report paired gains, ties and regressions; no superiority or expansion decision from a single small development set'),
        code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    target.mkdir(parents=True)
    atomic_json(target/'benchmark.json',contract)
    digest=hashlib.sha256((target/'benchmark.json').read_bytes()).hexdigest()
    (target/'benchmark.sha256').write_text(digest+'\n',encoding='ascii')
    print(json.dumps(dict(status='frozen',cases=len(cases),units=len(units),generated_pairs=len(GENERATE),sha256=digest)))


if __name__=='__main__':main()
