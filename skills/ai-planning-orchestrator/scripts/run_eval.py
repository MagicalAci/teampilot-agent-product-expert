#!/usr/bin/env python3
"""Lightweight automated eval harness for AI planning deliverables.

纯标准库实现的自动化评测台：规则 grader + pass@k + 回归 + A/B + 可插拔 LLM-judge。
方法论见 policies/llm-eval-methodology.md（第 4 节）与 references/eval-harness-guide.md。

设计取舍：
- 默认对每条用例已捕获的 output 做规则评测，不在 CI 里调模型（可复现、零依赖）。
- judge 类断言默认 dry-run（跳过，不计入失败）；用 --judge-cmd 接外部 judge。
- baseline 对比给出回归项 + 均值 A/B（Cohen's d，纯标准库）。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

VALID_BUCKETS = {"production", "adversarial", "edge", "failure_replay"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated evals on a JSONL dataset.")
    parser.add_argument("--dataset", required=True, help="评测集 JSONL 路径")
    parser.add_argument("--report", help="输出 Markdown 评测报告路径")
    parser.add_argument("--result", help="输出结果 JSON 路径（可作下次 baseline）")
    parser.add_argument("--baseline", help="基线结果 JSON，做回归/A-B")
    parser.add_argument(
        "--regression-threshold",
        type=float,
        default=0.05,
        help="相对下降超此比例判回归（默认 0.05）",
    )
    parser.add_argument("--judge-cmd", help="外部 judge 命令；无则 judge 断言跳过")
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="总通过率低于此值则退出码=1（CI 阻断）",
    )
    return parser.parse_args()


def load_dataset(path: Path) -> list[dict]:
    cases = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise SystemExit(f"[run_eval] 第 {line_no} 行不是合法 JSON: {exc}")
    return cases


# ---------------------------------------------------------------------------
# Graders（确定性规则）
# ---------------------------------------------------------------------------

def _as_text(output) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    return json.dumps(output, ensure_ascii=False)


def grade_assertion(output: str, assertion: dict, judge_cmd: str | None, case: dict):
    """返回 (passed, detail)。passed 为 None 表示跳过（不计入通过率）。"""
    atype = assertion.get("type")
    value = assertion.get("value")
    text = _as_text(output)

    if atype == "contains":
        return (str(value) in text, f"应包含 '{value}'")
    if atype == "not_contains":
        return (str(value) not in text, f"不应包含 '{value}'")
    if atype == "equals":
        return (text.strip() == str(value).strip(), f"应等于 '{value}'")
    if atype == "regex":
        try:
            return (re.search(str(value), text) is not None, f"应匹配 /{value}/")
        except re.error as exc:
            return (False, f"正则非法: {exc}")
    if atype == "json_valid":
        try:
            json.loads(text)
            return (True, "应为合法 JSON")
        except (json.JSONDecodeError, TypeError):
            return (False, "应为合法 JSON")
    if atype == "json_schema_keys":
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return (False, "JSON 解析失败，无法核对键")
        if not isinstance(obj, dict):
            return (False, "JSON 顶层应为对象")
        keys = value if isinstance(value, list) else [value]
        missing = [k for k in keys if k not in obj]
        return (not missing, f"缺少键 {missing}" if missing else "键齐全")
    if atype == "max_length":
        return (len(text) <= int(value), f"长度应 ≤ {value}（实际 {len(text)}）")
    if atype == "min_length":
        return (len(text) >= int(value), f"长度应 ≥ {value}（实际 {len(text)}）")
    if atype == "judge":
        if not judge_cmd:
            return (None, "judge 跳过（未配置 --judge-cmd）")
        return _run_judge(output, assertion, judge_cmd, case)

    if atype in {
        "tool_called",
        "tool_args_match",
        "tool_sequence",
        "step_efficiency",
        "task_completion",
    }:
        return _grade_trajectory(atype, output, assertion, judge_cmd, case)

    return (False, f"未知断言类型: {atype}")


def _run_judge(output, assertion: dict, judge_cmd: str, case: dict):
    payload = {
        "output": _as_text(output),
        "reference": case.get("reference", ""),
        "rubric": assertion.get("rubric", ""),
        "dimension": assertion.get("dimension", ""),
    }
    try:
        proc = subprocess.run(
            judge_cmd,
            shell=True,
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return (False, "judge 超时")
    if proc.returncode != 0:
        return (False, f"judge 失败: {proc.stderr.strip()[:200]}")
    try:
        verdict = json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        return (False, f"judge 输出非 JSON: {proc.stdout.strip()[:200]}")
    score = verdict.get("score")
    min_score = assertion.get("min_score", 4)
    if score is None:
        return (False, "judge 未返回 score")
    return (score >= min_score, f"judge 分 {score} (阈值 {min_score})")


# ---------------------------------------------------------------------------
# Agent 轨迹 grader（评一条 run 的工具调用/步骤/完成度，见 policies/agent-trajectory-eval.md）
# ---------------------------------------------------------------------------

def _as_obj(output):
    """把 output 解析成轨迹 dict；失败返回 None。"""
    if isinstance(output, dict):
        return output
    if isinstance(output, str):
        try:
            obj = json.loads(output)
        except json.JSONDecodeError:
            return None
        return obj if isinstance(obj, dict) else None
    return None


def _extract_tool_calls(obj: dict) -> list[dict]:
    """提取工具调用 [{'name':.., 'args':{..}}, ...]，兼容多种字段名。"""
    calls = obj.get("tool_calls") or obj.get("toolCalls") or []
    norm = []
    for c in calls:
        if isinstance(c, dict):
            norm.append(
                {
                    "name": c.get("name") or c.get("tool"),
                    "args": c.get("args") or c.get("arguments") or {},
                }
            )
        elif isinstance(c, str):
            norm.append({"name": c, "args": {}})
    return norm


def _grade_trajectory(atype, output, assertion: dict, judge_cmd, case: dict):
    obj = _as_obj(output)
    if obj is None:
        return (False, "无法解析为轨迹对象（需 JSON dict，含 tool_calls/steps）")
    value = assertion.get("value")
    calls = _extract_tool_calls(obj)
    names = [c["name"] for c in calls]

    if atype == "tool_called":
        wanted = value if isinstance(value, list) else [value]
        missing = [w for w in wanted if w not in names]
        return (not missing, f"缺工具调用 {missing}" if missing else f"已调用 {wanted}")

    if atype == "tool_args_match":
        if not isinstance(value, dict):
            return (False, "tool_args_match 的 value 应为 {tool, args}")
        tool = value.get("tool")
        want_args = value.get("args", {}) or {}
        for c in calls:
            if c["name"] == tool and all(c["args"].get(k) == v for k, v in want_args.items()):
                return (True, f"{tool} 参数匹配 {want_args}")
        return (False, f"{tool} 未以匹配参数 {want_args} 调用")

    if atype == "tool_sequence":
        seq = value if isinstance(value, list) else [value]
        it = iter(names)
        ok = all(any(n == s for n in it) for s in seq)
        return (ok, f"工具应按子序列 {seq}（实际 {names}）")

    if atype == "step_efficiency":
        steps = obj.get("steps")
        n = len(steps) if isinstance(steps, list) else len(calls)
        return (n <= int(value), f"步数 {n} 应 ≤ {value}")

    if atype == "task_completion":
        completed = obj.get("completed")
        if isinstance(completed, bool):
            return (completed, "completed 标志")
        if judge_cmd:
            return _run_judge(output, assertion, judge_cmd, case)
        return (None, "task_completion 跳过（无 completed 标志且未配 --judge-cmd）")

    return (False, f"未知轨迹断言: {atype}")


def grade_attempt(output, assertions: list[dict], judge_cmd, case: dict):
    """评一个 output；返回 (all_pass, score, graded_count, results)。"""
    results = []
    graded = 0
    passed = 0
    for assertion in assertions:
        ok, detail = grade_assertion(output, assertion, judge_cmd, case)
        results.append(
            {
                "type": assertion.get("type"),
                "dimension": assertion.get("dimension"),
                "passed": ok,
                "detail": detail,
            }
        )
        if ok is None:
            continue
        graded += 1
        if ok:
            passed += 1
    all_pass = graded > 0 and passed == graded
    score = (passed / graded) if graded else None
    return all_pass, score, graded, results


def evaluate(cases: list[dict], judge_cmd: str | None) -> dict:
    by_bucket = defaultdict(lambda: {"total": 0, "pass": 0})
    by_route = defaultdict(lambda: {"total": 0, "pass": 0})
    by_dim = defaultdict(lambda: {"total": 0, "pass": 0})
    failures = []
    clusters = defaultdict(int)
    case_scores = []

    graded_cases = 0
    pass1 = 0
    passk = 0
    passhk = 0
    max_attempts = 1
    weighted_num = 0.0
    weighted_den = 0.0
    ungraded = 0

    for case in cases:
        cid = case.get("id", "?")
        bucket = case.get("bucket", "production")
        route = case.get("route", "(default)")
        assertions = case.get("assertions", [])

        if "outputs" in case and isinstance(case["outputs"], list) and case["outputs"]:
            attempts = case["outputs"]
        elif "output" in case:
            attempts = [case["output"]]
        else:
            ungraded += 1
            continue

        max_attempts = max(max_attempts, len(attempts))
        attempt_results = [grade_attempt(o, assertions, judge_cmd, case) for o in attempts]

        # 第一个 attempt 决定分维度统计与失败记录
        first_all_pass, first_score, first_graded, first_detail = attempt_results[0]
        if first_graded == 0:
            ungraded += 1
            continue

        graded_cases += 1
        weight = float(case.get("weight", 1) or 1)

        if first_all_pass:
            pass1 += 1
        if any(a[0] for a in attempt_results):
            passk += 1
        if all(a[0] for a in attempt_results):
            passhk += 1

        if first_score is not None:
            case_scores.append(first_score)
            weighted_num += weight * first_score
            weighted_den += weight

        by_bucket[bucket]["total"] += 1
        by_bucket[bucket]["pass"] += int(first_all_pass)
        by_route[route]["total"] += 1
        by_route[route]["pass"] += int(first_all_pass)

        for res in first_detail:
            if res["passed"] is None:
                continue
            dim = res["dimension"] or "(unspecified)"
            by_dim[dim]["total"] += 1
            by_dim[dim]["pass"] += int(res["passed"])

        if not first_all_pass:
            failed = [r for r in first_detail if r["passed"] is False]
            failures.append(
                {
                    "id": cid,
                    "route": route,
                    "bucket": bucket,
                    "failed": [{"type": r["type"], "detail": r["detail"]} for r in failed],
                }
            )
            for r in failed:
                clusters[f"{route} / {r['type']}"] += 1

    def rate(d):
        return round(d["pass"] / d["total"], 4) if d["total"] else 0.0

    pass_rate = round(pass1 / graded_cases, 4) if graded_cases else 0.0

    summary = {
        "total_cases": len(cases),
        "graded_cases": graded_cases,
        "ungraded_cases": ungraded,
        "passed": pass1,
        "pass_rate": pass_rate,
        "weighted_score": round(weighted_num / weighted_den, 4) if weighted_den else 0.0,
        "pass_at_1": pass_rate,
        "k": max_attempts,
        "pass_at_k": round(passk / graded_cases, 4) if graded_cases else 0.0,
        "pass_hat_k": round(passhk / graded_cases, 4) if graded_cases else 0.0,
    }

    return {
        "summary": summary,
        "by_bucket": {k: {**v, "rate": rate(v)} for k, v in by_bucket.items()},
        "by_route": {k: {**v, "rate": rate(v)} for k, v in by_route.items()},
        "by_dimension": {k: {**v, "rate": rate(v)} for k, v in by_dim.items()},
        "failures": failures,
        "failure_clusters": dict(sorted(clusters.items(), key=lambda x: -x[1])),
        "case_scores": case_scores,
    }


# ---------------------------------------------------------------------------
# Baseline 对比（回归 + A/B）
# ---------------------------------------------------------------------------

def cohens_d(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(b) < 2:
        return None
    sa, sb = statistics.pstdev(a), statistics.pstdev(b)
    pooled = ((sa ** 2 + sb ** 2) / 2) ** 0.5
    if pooled == 0:
        return 0.0
    return round((statistics.mean(b) - statistics.mean(a)) / pooled, 4)


def compare_baseline(current: dict, baseline: dict, threshold: float) -> dict:
    regressions = []

    def check(metric, base_val, cur_val):
        if base_val and base_val > 0:
            rel = (cur_val - base_val) / base_val
            if rel < -threshold:
                regressions.append(
                    {
                        "metric": metric,
                        "baseline": round(base_val, 4),
                        "current": round(cur_val, 4),
                        "rel_change": round(rel, 4),
                    }
                )

    check("pass_rate", baseline["summary"].get("pass_rate", 0), current["summary"].get("pass_rate", 0))
    for dim, cur in current.get("by_dimension", {}).items():
        base = baseline.get("by_dimension", {}).get(dim)
        if base:
            check(f"dim:{dim}", base.get("rate", 0), cur.get("rate", 0))

    d = cohens_d(baseline.get("case_scores", []), current.get("case_scores", []))
    n = min(len(baseline.get("case_scores", [])), len(current.get("case_scores", [])))
    ab = {
        "baseline_mean": round(statistics.mean(baseline["case_scores"]), 4)
        if baseline.get("case_scores")
        else None,
        "current_mean": round(statistics.mean(current["case_scores"]), 4)
        if current.get("case_scores")
        else None,
        "cohens_d": d,
        "effect": _interpret_d(d),
        "n": n,
        "note": "样本充足(n≥20)时 Cohen's d 更可信；样本不足仅供参考" if n < 20 else "",
    }
    return {"regressions": regressions, "has_regression": bool(regressions), "ab": ab}


def _interpret_d(d):
    if d is None:
        return "样本不足"
    ad = abs(d)
    if ad < 0.2:
        return "可忽略"
    if ad < 0.5:
        return "小"
    if ad < 0.8:
        return "中"
    return "大"


# ---------------------------------------------------------------------------
# 报告渲染
# ---------------------------------------------------------------------------

def render_report(result: dict, dataset: str, comparison: dict | None) -> str:
    s = result["summary"]
    lines = [
        f"# AI评测报告（自动生成）",
        "",
        f"> 数据集: `{dataset}`  ·  适用命令: `/AI评测`",
        "",
        "## 1. 总体结果",
        "",
        "| 指标 | 值 |",
        "|---|---|",
        f"| 总用例 | {s['total_cases']} |",
        f"| 已评测 | {s['graded_cases']} |",
        f"| 未评测(缺 output/仅 judge 跳过) | {s['ungraded_cases']} |",
        f"| 通过 | {s['passed']} |",
        f"| 通过率 | {s['pass_rate']:.1%} |",
        f"| 加权分 | {s['weighted_score']:.3f} |",
        f"| pass@1 | {s['pass_at_1']:.1%} |",
        f"| pass@{s['k']} | {s['pass_at_k']:.1%} |",
        f"| pass^{s['k']} | {s['pass_hat_k']:.1%} |",
        "",
        "## 2. 分维度",
        "",
        "| 维度 | 通过 | 总数 | 通过率 |",
        "|---|---|---|---|",
    ]
    for dim, v in result["by_dimension"].items():
        lines.append(f"| {dim} | {v['pass']} | {v['total']} | {v['rate']:.1%} |")

    lines += ["", "## 3. 分桶", "", "| 桶 | 通过 | 总数 | 通过率 |", "|---|---|---|---|"]
    for b, v in result["by_bucket"].items():
        lines.append(f"| {b} | {v['pass']} | {v['total']} | {v['rate']:.1%} |")

    lines += ["", "## 4. 失败用例与聚类", ""]
    if result["failures"]:
        lines += ["| 用例 id | 路由 | 失败断言 |", "|---|---|---|"]
        for f in result["failures"]:
            detail = "; ".join(f"{x['type']}({x['detail']})" for x in f["failed"])
            lines.append(f"| {f['id']} | {f['route']} | {detail} |")
        lines += ["", "**失败聚类（同根因归并）：**", ""]
        for cluster, count in result["failure_clusters"].items():
            lines.append(f"- {cluster}: {count} 次")
    else:
        lines.append("无失败用例。")

    lines += ["", "## 5. 与基线对比（回归 / A-B）", ""]
    if comparison:
        ab = comparison["ab"]
        lines += [
            "| 项 | 值 |",
            "|---|---|",
            f"| 基线均分 | {ab['baseline_mean']} |",
            f"| 本次均分 | {ab['current_mean']} |",
            f"| Cohen's d | {ab['cohens_d']}（效应：{ab['effect']}，n={ab['n']}） |",
            "",
        ]
        if ab["note"]:
            lines.append(f"> {ab['note']}")
            lines.append("")
        if comparison["has_regression"]:
            lines += ["**⚠️ 检出回归：**", "", "| 指标 | 基线 | 本次 | 相对变化 |", "|---|---|---|---|"]
            for r in comparison["regressions"]:
                lines.append(
                    f"| {r['metric']} | {r['baseline']:.1%} | {r['current']:.1%} | {r['rel_change']:+.1%} |"
                )
        else:
            lines.append("未检出回归。")
    else:
        lines.append("（未提供 baseline，跳过回归/A-B 对比。）")

    lines += [
        "",
        "## 6. 剩余风险与结论",
        "",
        "- 未覆盖场景 / 已知限制：（人工补充）",
        "- 是否需要 `/AI调优`：（依据失败聚类判断）",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset).resolve()
    if not dataset_path.exists():
        raise SystemExit(f"[run_eval] 评测集不存在: {dataset_path}")

    cases = load_dataset(dataset_path)
    result = evaluate(cases, args.judge_cmd)

    comparison = None
    if args.baseline:
        baseline_path = Path(args.baseline).resolve()
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            comparison = compare_baseline(result, baseline, args.regression_threshold)
            result["comparison"] = comparison
        else:
            print(f"[run_eval] 警告：baseline 不存在: {baseline_path}", file=sys.stderr)

    result["dataset_meta"] = {"path": str(dataset_path), "case_count": len(cases)}

    if args.result:
        Path(args.result).resolve().write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if args.report:
        report = render_report(result, str(dataset_path), comparison)
        Path(args.report).resolve().write_text(report, encoding="utf-8")

    # 控制台摘要
    s = result["summary"]
    print(
        json.dumps(
            {
                "pass_rate": s["pass_rate"],
                "graded_cases": s["graded_cases"],
                "ungraded_cases": s["ungraded_cases"],
                "pass_at_k": s["pass_at_k"],
                "has_regression": comparison["has_regression"] if comparison else False,
            },
            ensure_ascii=False,
        )
    )

    exit_code = 0
    if args.fail_under is not None and s["pass_rate"] < args.fail_under:
        print(f"[run_eval] 通过率 {s['pass_rate']:.1%} < fail-under {args.fail_under:.1%}", file=sys.stderr)
        exit_code = 1
    if comparison and comparison["has_regression"]:
        print("[run_eval] 检出回归，阻断。", file=sys.stderr)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
