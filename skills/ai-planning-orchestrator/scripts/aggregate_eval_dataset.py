#!/usr/bin/env python3
"""Aggregate, validate, and health-check eval datasets (JSONL).

合并多来源评测集 + schema 校验 + 去重 + 桶配比/规模体检。
方法论见 policies/llm-eval-methodology.md 第 2 节。纯标准库。
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

VALID_BUCKETS = {"production", "adversarial", "edge", "failure_replay"}
VALID_ASSERTIONS = {
    "contains",
    "not_contains",
    "equals",
    "regex",
    "json_valid",
    "json_schema_keys",
    "max_length",
    "min_length",
    "judge",
}
TARGET_RATIO = {"production": 0.60, "adversarial": 0.15, "edge": 0.15, "failure_replay": 0.10}
RATIO_TOLERANCE = 0.10  # 绝对偏差容忍


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate and health-check eval datasets.")
    parser.add_argument("datasets", nargs="+", help="一个或多个 JSONL 评测集")
    parser.add_argument("--out", help="合并去重后的 JSONL 输出路径")
    parser.add_argument("--report", help="体检报告 Markdown 输出路径")
    parser.add_argument("--min-per-route", type=int, default=30, help="每 route 用例数下限（默认 30）")
    parser.add_argument("--strict", action="store_true", help="桶配比/规模告警也以非零退出码")
    return parser.parse_args()


def validate_case(case: dict, idx: int, source: str) -> list[str]:
    errors = []
    prefix = f"[{source}#{idx}]"
    if not isinstance(case, dict):
        return [f"{prefix} 不是 JSON 对象"]
    if not case.get("id"):
        errors.append(f"{prefix} 缺少 id")
    bucket = case.get("bucket")
    if bucket not in VALID_BUCKETS:
        errors.append(f"{prefix} bucket 非法: {bucket!r}（应为 {sorted(VALID_BUCKETS)}）")
    if "input" not in case:
        errors.append(f"{prefix} 缺少 input")
    assertions = case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append(f"{prefix} assertions 应为非空数组")
    else:
        for ai, a in enumerate(assertions):
            atype = a.get("type") if isinstance(a, dict) else None
            if atype not in VALID_ASSERTIONS:
                errors.append(f"{prefix} 断言#{ai} type 非法: {atype!r}")
            if atype in {"contains", "not_contains", "equals", "regex", "max_length", "min_length", "json_schema_keys"} and "value" not in a:
                errors.append(f"{prefix} 断言#{ai}({atype}) 缺少 value")
    return errors


def main() -> int:
    args = parse_args()
    all_cases = []
    errors = []
    seen_ids = {}
    duplicates = []

    for ds in args.datasets:
        path = Path(ds).resolve()
        if not path.exists():
            errors.append(f"文件不存在: {path}")
            continue
        for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"[{path.name}#{idx}] JSON 解析失败: {exc}")
                continue
            case_errors = validate_case(case, idx, path.name)
            errors.extend(case_errors)
            cid = case.get("id")
            if cid in seen_ids:
                duplicates.append(cid)
                continue  # 去重：保留首个
            seen_ids[cid] = True
            all_cases.append(case)

    # 桶配比 + 规模体检
    by_bucket = defaultdict(int)
    by_route = defaultdict(int)
    for c in all_cases:
        by_bucket[c.get("bucket", "?")] += 1
        by_route[c.get("route", "(default)")] += 1

    total = len(all_cases)
    ratio_warnings = []
    if total:
        for bucket, target in TARGET_RATIO.items():
            actual = by_bucket.get(bucket, 0) / total
            if abs(actual - target) > RATIO_TOLERANCE:
                ratio_warnings.append(
                    f"桶 {bucket} 占比 {actual:.0%}，目标 {target:.0%}（偏差超 {RATIO_TOLERANCE:.0%}）"
                )

    size_warnings = []
    if total < args.min_per_route:
        size_warnings.append(f"总用例 {total} < 下限 {args.min_per_route}（回归方差过大）")
    for route, n in by_route.items():
        if n < args.min_per_route:
            size_warnings.append(f"route '{route}' 仅 {n} 条 < 下限 {args.min_per_route}")

    summary = {
        "total": total,
        "by_bucket": dict(by_bucket),
        "by_route": dict(by_route),
        "duplicates_removed": duplicates,
        "errors": errors,
        "ratio_warnings": ratio_warnings,
        "size_warnings": size_warnings,
        "decontamination_reminder": "确认评测集与训练/微调数据、与提示词写死的少样本不重叠（去污染）。",
    }

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            for c in all_cases:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    if args.report:
        report = _render_report(summary, args.min_per_route)
        Path(args.report).resolve().write_text(report, encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if errors:
        return 1
    if args.strict and (ratio_warnings or size_warnings):
        return 1
    return 0


def _render_report(summary: dict, min_per_route: int) -> str:
    lines = [
        "# 评测集体检报告（自动生成）",
        "",
        f"> 适用命令: `/评测集`  ·  方法论: `policies/llm-eval-methodology.md` 第 2 节",
        "",
        "## 1. 规模与配比",
        "",
        f"- 总用例：{summary['total']}",
        "",
        "| 桶 | 数量 | 目标占比 |",
        "|---|---|---|",
    ]
    for bucket, target in TARGET_RATIO.items():
        lines.append(f"| {bucket} | {summary['by_bucket'].get(bucket, 0)} | {target:.0%} |")
    lines += ["", "| route | 数量 |", "|---|---|"]
    for route, n in summary["by_route"].items():
        flag = " ⚠️" if n < min_per_route else ""
        lines.append(f"| {route} | {n}{flag} |")

    lines += ["", "## 2. 校验错误", ""]
    lines += ([f"- ❌ {e}" for e in summary["errors"]] or ["- 无"])
    lines += ["", "## 3. 配比/规模告警", ""]
    warns = summary["ratio_warnings"] + summary["size_warnings"]
    lines += ([f"- ⚠️ {w}" for w in warns] or ["- 无"])
    if summary["duplicates_removed"]:
        lines += ["", f"## 4. 去重", "", f"- 移除重复 id：{summary['duplicates_removed']}"]
    lines += ["", "## 5. 提醒", "", f"- {summary['decontamination_reminder']}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
