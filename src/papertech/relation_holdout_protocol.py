"""Source-first, immutable new-question protocol; no retrieval or model calls."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re

from .corpus import load_corpus
from .evaluation_datasets import load_benchmark, write_json
from .evaluation_details import source_detail

DRAFT_SHA = '67a4616c691da99588ab870e2c7a2be6429c385d31799fe2d4e61bb3735a49c1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(text):
    return re.sub(r'\s+', '', text).casefold()


def freeze_protocol(root, version, arms, files):
    folder = root / 'artifacts/eval/stage-4' / version
    target = folder / 'benchmark.json'
    if target.exists():
        return load_benchmark(root, version)[0]
    draft_path = root / 'artifacts/eval/stage-4/relation-holdout-draft-v1/questions-draft.json'
    if sha(draft_path) != DRAFT_SHA:
        raise ValueError('approved_draft_changed')
    draft = json.loads(draft_path.read_text(encoding='utf8'))
    parent, parent_sha, _ = load_benchmark(root, 'benchmark-retrieval-v1')
    corpus_id, papers, chunks = load_corpus(root)
    chunk_map = {c['chunk_id']: c for c in chunks}
    if corpus_id != draft['corpus_id'] or len(chunks) != 980 or len(papers) != 14:
        raise ValueError('corpus_changed')
    audit = json.loads((draft_path.parent / 'source-link-audit.json').read_text(encoding='utf8'))
    if audit['graph_sha256'] != parent['graph_snapshot']['sha256']:
        raise ValueError('graph_audit_mismatch')
    strata = {r['case_id']: r['status'] for r in audit['per_case']}
    units, cases, reviews = {}, [], []
    for original in draft['cases']:
        case = deepcopy(original)
        case.update(units=[], generate=False, answerable=case['category'] != 'negative',
            negative_kind='false_or_overgeneralized_premise' if case['category'] == 'negative' else None,
            min_source_papers=len(case['source_papers']), reasoning_chain=None,
            must_not_claim='不得接受题干错误前提。' if case['category'] == 'negative' else None,
            expected_answer='\n'.join(f['requirement'] for f in case['reference_facts']),
            graph_source_link_stratum=strata[case['id']], reference_criteria=[])
        for criterion in original['criteria']:
            cid = criterion['source_chunk_id']
            source = chunk_map[cid]
            frozen = draft['sources'][cid]
            if any(source[k] != frozen[k] for k in frozen):
                raise ValueError('draft_source_changed')
            if sha_text(source['text']) != source['text_sha256'] or not source['source_spans']:
                raise ValueError('source_hash_or_location_invalid')
            uid = criterion['id'].replace('.C', '.S')
            # One source requirement remains one metric unit. Splitting its display
            # criteria must not overweight a paragraph with more punctuation.
            equivalents = [c for c in chunks if c['paper_id'] == source['paper_id'] and
                canonical(source['text']) in canonical(c['text'])]
            pool = list(dict.fromkeys([cid] + [c['chunk_id'] for c in equivalents]))
            units[uid] = dict(id=uid, answer_point=criterion['requirement'], primary_chunk=cid,
                known_support_chunks=pool, paper_id=source['paper_id'], title=source['title'],
                page_start=source['page_start'], page_end=source['page_end'], source_text=source['text'],
                support_sources=[source_detail(chunk_map[c]) for c in pool],
                support_review='Codex 原文核对；加入同论文完整包含原文的等价块。支持池非穷尽，非人工独立金标。')
            case['units'].append(uid)
            clauses = [t.strip('。 ') for t in re.split('[；。]', criterion['requirement']) if t.strip('。 ')]
            for clause in clauses:
                case['reference_criteria'].append(dict(id=f"{case['id']}.A{len(case['reference_criteria'])+1:02d}",
                    requirement=clause, unit_ids=[uid], supporting_chunks_by_unit={uid: pool},
                    source_rule='仅判该条件的必要来源是否可用；语义正确性本轮不评分。', score_values=[0, 1]))
            reviews.append(dict(unit_id=uid, primary_chunk=cid, known_support_chunks=pool,
                original_text_verified=True, source_hash_verified=True, page_spans_verified=True,
                equivalence_rule='same-paper full normalized source containment; semantic paraphrase pools not exhaustive'))
        case.pop('criteria')
        case['answer_review'] = 'Codex 对原文核对的参考要点；本轮无生成，不进行答案语义或拒答评分。'
        cases.append(case)
    distribution = dict(Counter(c['category'] for c in cases))
    if distribution != dict(fact=8, cross=24, negative=8) or len({c['question'] for c in cases}) != 40:
        raise ValueError('approved_question_distribution_changed')
    controls = deepcopy(parent['controls'])
    controls.update(arms=list(arms), order='alternate two arms by case index')
    controls.pop('dense_only_top', None)
    previous_run = root / 'artifacts/reports/stage-4/benchmark-retrieval-v1/runs/a7e1923337d74d8fa2a34c73b255f522/execution-contract.json'
    previous_runtime = json.loads(previous_run.read_text(encoding='utf8'))
    for name, digest in previous_runtime['code_sha256'].items():
        if name not in ('scripts/eval-stage4.py', 'src/papertech/evaluation_details.py') and sha(root / name) != digest:
            raise ValueError('previous_retrieval_implementation_changed')
    bench = dict(version=version, corpus_id=corpus_id, papers=len(papers), chunks=len(chunks),
        approved_draft_sha256=DRAFT_SHA, previous_protocol_sha256=parent_sha,
        cases=cases, units=units, distribution=distribution,
        dataset_description='同语料40道新问题迁移诊断：Graph-only / Hybrid，仅检索。包含旧事实的新组合；不是独立盲测或答案准确率测试。',
        prior_exposure='题目先按论文原文提出，再审计固定图；图曾参考历史开发题与来源。本轮不补边、不增别名、不调阈值。',
        comparison=dict(mode='independent_retrieval', arms=list(arms), excluded_arms=['Dense-only'], generation=False),
        models=dict(embedding=parent['models']['embedding'], reranker=parent['models']['reranker'], generation='not run'),
        controls=controls, graph_snapshot=deepcopy(parent['graph_snapshot']),
        unchanged_runtime={k: previous_runtime[k] for k in ('models', 'endpoints')},
        scoring=dict(primary='24道cross题最终必要来源覆盖率的逐题宏平均；Graph-only minus Hybrid配对差。',
            unit='每项参考来源要求一个单元；同单元已核查等价块OR，必要来源单元AND；不是逐字事实正确率。',
            secondary=['candidate pool coverage@40', 'Recall@5', 'Recall@8', 'MRR@40', 'all source units covered', 'required paper coverage'],
            denominator='32道正例；24道cross单列；8道negative只展示纠错来源诊断，不计主召回与拒答准确率。',
            retrieval_only=True, semantic_review='not applicable: no answer generation',
            bootstrap=dict(seed=20261122, paired_resamples=10000, interval='percentile 95%, case-level paired macro coverage',
                scope='fixed 24-question diagnostic set; not a population guarantee; subgroups descriptive'),
            failure_attribution='post-hoc frozen support-pool IDs; no support IDs enter candidate production',
            source_pool_limit='完整包含原文的同论文等价块已审计；其他语义等价段落可能未列入。另报论文覆盖但不当作事实覆盖。',
            negative_policy='source diagnostics only; exclude from aggregate recall; no refusal correctness',
            reporting='aggregate, categories, graph-source-link strata, named/discovery, paired deltas and CI, charts, latency, usage, all 40 details and traces'),
        source_link_audit=audit, source_review=reviews,
        code_sha256={name: sha(root / name) for name in files})
    write_json(target, bench)
    (folder / 'benchmark.sha256').write_text(sha(target) + '\n', encoding='utf8')
    write_json(folder / 'source-review.json', dict(status='pre-run-source-reviewed', reviews=reviews,
        semantic_equivalence_exhaustive=False, generation=False, graph_changed=False))
    return bench


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()
