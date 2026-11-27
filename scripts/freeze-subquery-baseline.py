"""Freeze completed subquery experiments as a reusable pre-KG baseline.

This command only reads completed local artifacts and verified LangSmith
statuses. It does not call a model, retrieval index, reranker, or LangSmith
write API.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from papertech.evaluation_datasets import write_json
VERSION = "subquery-baseline-v1"
SOURCE = {
    "router_fix": ("benchmark-query-router-fix-v1", "c22f0bb403e744139598cee5161cde3b"),
    "recall_full": ("benchmark-subquery-recall-v1", "e158c260284d4273b8b55c9bd7a8b8f7"),
    "recall_router_fix": ("benchmark-subquery-recall-router-fix-v1", "e73ddd804e6c4dd6a54873ec47b74727"),
    "policy": ("benchmark-subquery-recall-policy-v1", "436a8f4429df42c3b6fafe2c12216b5b"),
    "rerank_clean": ("benchmark-subquery-rerank-clean-v1", "f4738bf1db924730b67f99a6c971c9ea"),
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_source(name):
    version, run_id = SOURCE[name]
    folder = ROOT / "artifacts/reports/stage-4" / version / "runs" / run_id
    summary_path = folder / "summary.json"
    benchmark_path = ROOT / "artifacts/eval/stage-4" / version / "benchmark.json"
    status_path = benchmark_path.parent / "langsmith-status.json"
    if not summary_path.exists() or not benchmark_path.exists() or not status_path.exists():
        raise FileNotFoundError(name)
    summary = read(summary_path)
    benchmark = read(benchmark_path)
    status = read(status_path)
    benchmark_sha = sha(benchmark_path)
    stored_sha = (benchmark_path.parent / "benchmark.sha256").read_text(encoding="utf8").strip()
    if summary.get("status") != "completed":
        raise ValueError(f"{name}: source run not completed")
    if summary.get("benchmark_sha256") != benchmark_sha or stored_sha != benchmark_sha:
        raise ValueError(f"{name}: benchmark hash mismatch")
    if status.get("status") != "experiments_verified" or status.get("examples_verified") != 24:
        raise ValueError(f"{name}: LangSmith readback not verified")
    return dict(name=name, version=version, run_id=run_id, folder=folder,
                summary=summary, benchmark=benchmark, benchmark_sha256=benchmark_sha,
                summary_sha256=sha(summary_path), langsmith=status)


def recall_aggregate(summary):
    rows = summary["results"]
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        group = [r for r in rows if r["arm"] == arm]
        if len(group) != 24:
            raise ValueError(f"recall {arm}: expected 24 rows")
        facts = [f for r in group for f in r["facts"]]
        out[arm] = dict(
            questions=24,
            source_total=len(facts),
            cap40_coverage=sum(r["metrics"]["cap40_coverage"] for r in group) / 24,
            union_coverage=sum(r["metrics"]["union_coverage"] for r in group) / 24,
            cap40_source_hits=sum(bool(f["retained"]) for f in facts),
            union_source_hits=sum(bool(f["union_hit"]) for f in facts),
            cap40_complete=sum(bool(r["metrics"]["cap40_all"]) for r in group),
            union_complete=sum(bool(r["metrics"]["union_all"]) for r in group),
            avg_candidate_union=sum(len(r["candidates"]) for r in group) / 24,
        )
    return out


def router_aggregate(summary):
    rows = summary["results"]
    expected = {(f"R{i:02d}", arm) for i in range(1, 25) for arm in ("Rule", "Local-LLM")}
    if {(r["case_id"], r["arm"]) for r in rows} != expected:
        raise ValueError("router: incomplete Rule/Local-LLM pairs")
    out = {}
    for arm in ("Rule", "Local-LLM"):
        group = [r for r in rows if r["arm"] == arm]
        out[arm] = dict(
            questions=24,
            valid_outputs=sum(bool(r.get("valid")) for r in group),
            split_applied=sum(bool(r.get("subqueries")) for r in group),
            subqueries=sum(len(r.get("subqueries", [])) for r in group),
            model_calls=sum(r.get("model_calls", 0) for r in group),
        )
    return out


def policy_aggregate(summary):
    rows = summary["results"]
    if len(rows) != 192:
        raise ValueError("policy: expected 8 arms x 24 rows")
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        group = [r for r in rows if r["arm"] == arm]
        facts = [f for r in group for f in r["facts"]]
        out[arm] = dict(
            questions=len(group),
            coverage=sum(r["metrics"]["cap40_coverage"] for r in group) / len(group),
            source_hits=sum(bool(f["retained"]) for f in facts),
            source_total=len(facts),
            complete=sum(bool(r["metrics"]["cap40_all"]) for r in group),
        )
    return out


def rerank_aggregate(summary):
    rows = summary["results"]
    if len(rows) != 72:
        raise ValueError("rerank_clean: expected 3 arms x 24 rows")
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        group = [r for r in rows if r["arm"] == arm]
        efacts = [f for r in group for f in r["evidence_facts"]]
        out[arm] = dict(
            questions=len(group),
            top40_coverage=sum(r["metrics"]["top40_coverage"] for r in group) / 24,
            top40_source_hits=sum(bool(f["retained"]) for r in group for f in r["facts"]),
            source_total=sum(len(r["facts"]) for r in group),
            top40_complete=sum(bool(r["metrics"]["top40_all"]) for r in group),
            evidence_coverage=sum(r["evidence_metrics"]["coverage"] for r in group) / 24,
            evidence_source_hits=sum(bool(f["selected"]) for f in efacts),
            evidence_complete=sum(bool(r["evidence_metrics"]["all"]) for r in group),
            evidence_blocks=sum(r["evidence_metrics"]["evidence_count"] for r in group),
            rerank_pairs=sum(r["compute"]["pairs"] for r in group),
            rerank_seconds=sum(r["compute"]["inference_seconds"] for r in group),
        )
    return out


def build():
    loaded = {name: load_source(name) for name in SOURCE}
    recall_fix = loaded["recall_router_fix"]["summary"]
    r11 = {
        r["arm"]: dict(
            union_coverage=r["metrics"]["union_coverage"],
            cap40_coverage=r["metrics"]["cap40_coverage"],
            source_hits=sum(bool(f["union_hit"]) for f in r["facts"]),
            retained_hits=sum(bool(f["retained"]) for f in r["facts"]),
            candidate_count=len(r["candidates"]),
        )
        for r in recall_fix["results"] if r["case_id"] == "R11"
    }
    route_diff = loaded["router_fix"]["folder"] / "replay-diff.json"
    route_changes = len(read(route_diff).get("changes", [])) if route_diff.exists() else None
    manifest = dict(
        version=VERSION,
        created_at=datetime.now(timezone.utc).isoformat(),
        status="frozen",
        purpose="冻结知识图谱对照前的子查询检索基线；不修改图谱、不运行模型。",
        scope=dict(questions=24, necessary_sources=49, corpus="980 chunks / 14 papers",
                   development_only=True, answer_generation=False, graph_excluded=True),
        selected_baseline=dict(
            router="benchmark-query-router-fix-v1",
            retrieval="Expanded vs Original from benchmark-subquery-recall-v1",
            candidate_policy="Rerank-OwnerSubquery-Union40",
            evidence_policy="Owner-Clean, 6000 bytes / 8 blocks / named_first",
        ),
        measurements=dict(
            router=router_aggregate(loaded["router_fix"]["summary"]),
            retrieval=recall_aggregate(loaded["recall_full"]["summary"]),
            candidate_policy=policy_aggregate(loaded["policy"]["summary"]),
            rerank_and_evidence=rerank_aggregate(loaded["rerank_clean"]["summary"]),
            r11_router_fix=dict(route_change_count=route_changes, R11=r11),
        ),
        interpretation=dict(
            retrieval="Expanded improves necessary-source coverage in the full recall comparison; this is source coverage, not answer accuracy.",
            policy="Quota-N9 and RoundRobin-40 are tied at 33/49; owner reranking reaches 36/49 before evidence selection.",
            evidence="Owner-Clean retains 20/49 necessary sources under 6000 bytes / 8 blocks.",
            router_fix="R11 fallback to llm repair restores four subqueries, but R11 remains 1/2 necessary sources.",
            limitation="24 questions and support pools are exposed development material; rerank/evidence runs predate the isolated R11 rerun for the other 23 rows.",
            semantic_accuracy="not evaluated",
        ),
        source_runs={},
        hashes={},
    )
    for name, item in loaded.items():
        manifest["source_runs"][name] = dict(
            benchmark=item["version"], run_id=item["run_id"],
            benchmark_sha256=item["benchmark_sha256"], summary_sha256=item["summary_sha256"],
            dataset_id=item["langsmith"].get("dataset_id"),
            dataset_url=item["langsmith"].get("dataset_url"),
            comparison_url=item["langsmith"].get("comparison_url"),
            experiments=item["langsmith"].get("experiments", []),
        )
        manifest["hashes"][f"artifacts/eval/stage-4/{item['version']}/benchmark.json"] = item["benchmark_sha256"]
        manifest["hashes"][f"artifacts/reports/stage-4/{item['version']}/runs/{item['run_id']}/summary.json"] = item["summary_sha256"]
    return manifest


def write_freeze():
    eval_dir = ROOT / "artifacts/eval/stage-4" / VERSION
    report_dir = ROOT / "artifacts/reports/stage-4" / VERSION
    eval_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    existing_path = eval_dir / "baseline.json"
    if existing_path.exists():
        manifest = read(existing_path)
        if manifest.get("version") != VERSION or manifest.get("status") != "frozen":
            raise ValueError("existing baseline manifest is invalid")
        if sha(existing_path) != (eval_dir / "baseline.sha256").read_text(encoding="utf8").strip():
            raise ValueError("existing baseline hash mismatch")
        current = build()
        old = dict(manifest)
        old.pop("created_at", None)
        current.pop("created_at", None)
        if old != current:
            raise ValueError("source artifacts changed; create a new baseline version")
        return manifest
    manifest = build()
    write_json(eval_dir / "baseline.json", manifest)
    (eval_dir / "baseline.sha256").write_text(sha(eval_dir / "baseline.json") + "\n", encoding="utf8")
    m = manifest["measurements"]
    r = m["retrieval"]
    e = m["rerank_and_evidence"]
    lines = [
        "# 子查询基线冻结 v1", "",
        "本文件冻结图谱对照前的子查询链路。五个来源实验均已完成 LangSmith Dataset/Experiment 读回校验；本次只做本地独立汇总，没有重新调用模型。", "",
        "## 冻结配置", "",
        "- 分流：query-router-fix，包含 R11 的 quote 规范化修复。",
        "- 召回：原问题 vs 原问题加子查询，全文 Top20 + dense Top20，候选上限 40。",
        "- 候选策略：完整并集上的原问题重排、归属子查询重排、max 融合。",
        "- 证据策略：6000 bytes / 8 blocks / named_first。",
        "- 图谱和答案生成：排除。", "",
        "## 主要结果", "",
        "| 层级 | 方案 | 必要来源覆盖 | 来源命中 |",
        "|---|---|---:|---:|",
        f"| 候选40 | Original | {r['Original']['cap40_coverage']:.2%} | {r['Original']['cap40_source_hits']}/49 |",
        f"| 候选40 | Expanded | {r['Expanded']['cap40_coverage']:.2%} | {r['Expanded']['cap40_source_hits']}/49 |",
        f"| 完整并集重排 | Original | {m['candidate_policy']['Rerank-Original-Union40']['coverage']:.2%} | {m['candidate_policy']['Rerank-Original-Union40']['source_hits']}/49 |",
        f"| 完整并集重排 | Owner | {m['candidate_policy']['Rerank-OwnerSubquery-Union40']['coverage']:.2%} | {m['candidate_policy']['Rerank-OwnerSubquery-Union40']['source_hits']}/49 |",
        f"| 证据6000/8 | Original-Reused | {e['Original-Reused']['evidence_coverage']:.2%} | {e['Original-Reused']['evidence_source_hits']}/49 |",
        f"| 证据6000/8 | Owner-Clean | {e['Owner-Clean']['evidence_coverage']:.2%} | {e['Owner-Clean']['evidence_source_hits']}/49 |",
        "", "## R11 修复增量", "",
        f"- 路由差异数：{m['r11_router_fix']['route_change_count']}。",
        f"- R11 Original：{m['r11_router_fix']['R11']['Original']['source_hits']}/2 进入并集，{m['r11_router_fix']['R11']['Original']['retained_hits']}/2 留在40条。",
        f"- R11 修复后 Expanded：{m['r11_router_fix']['R11']['Expanded']['source_hits']}/2 进入并集，{m['r11_router_fix']['R11']['Expanded']['retained_hits']}/2 留在40条。",
        "- 修复恢复了子查询链路，但没有补回 R11.S02。", "",
        "## 使用边界", "",
        "- 24 题和 49 个必要来源属于已曝光开发集，不是泛化验收。",
        "- 覆盖率只表示来源是否进入候选或证据，不代表答案语义正确率。",
        "- R11 修复是单独增量；其余 23 题没有被重新重排。",
        "- 后续图谱对照应固定使用本文件的题集、来源池、预算和评分口径，另建 benchmark 版本。", "",
        "## LangSmith 来源",
    ]
    for name, source in manifest["source_runs"].items():
        lines.append(f"- {name}: dataset {source['dataset_id']}; comparison {source['comparison_url']}")
    (report_dir / "baseline.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    write_json(report_dir / "baseline.json", manifest)
    return manifest


if __name__ == "__main__":
    manifest = write_freeze()
    print(json.dumps(dict(version=VERSION, status=manifest["status"],
                          eval_manifest=f"artifacts/eval/stage-4/{VERSION}/baseline.json",
                          report=f"artifacts/reports/stage-4/{VERSION}/baseline.md",
                          source_runs=len(manifest["source_runs"])),
                ensure_ascii=False, indent=2))
