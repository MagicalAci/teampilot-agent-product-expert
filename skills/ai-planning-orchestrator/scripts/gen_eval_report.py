#!/usr/bin/env python3
"""Render an eval report (and optional tuning-report skeleton) from a result JSON.

从 run_eval.py 产出的 result JSON 渲染 Markdown 评测报告；
可选据失败聚类生成调优报告骨架。纯标准库，复用 run_eval 的渲染逻辑。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402  (same-directory helper module)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render eval/tuning report from result JSON.")
    parser.add_argument("--result", required=True, help="run_eval.py 产出的 result JSON")
    parser.add_argument("--report", help="输出 Markdown 评测报告路径")
    parser.add_argument(
        "--tuning-skeleton",
        help="按失败聚类生成调优报告骨架（Markdown 路径）",
    )
    return parser.parse_args()


def render_tuning_skeleton(result: dict) -> str:
    clusters = result.get("failure_clusters", {})
    lines = [
        "# AI调优报告（骨架，自动生成）",
        "",
        "> 适用命令: `/AI调优`  ·  方法论: `policies/llm-eval-methodology.md` 第 5 节",
        "",
        "## 1. 调优对象",
        "",
        "- 起始版本：",
        "- 目标版本：",
        "",
        "## 2. 失败归因（ASI）— 据评测报告失败聚类预填",
        "",
        "| 失败聚类 | 出现次数 | 根因（待填） | 一般化修法（待填） |",
        "|---|---|---|---|",
    ]
    if clusters:
        for cluster, count in clusters.items():
            lines.append(f"| {cluster} | {count} | | |")
    else:
        lines.append("| （无失败用例） | 0 | | |")
    lines += [
        "",
        "## 3. 变更清单（本轮 ≤ 3–5 处）",
        "",
        "| # | 改了什么 | 对应根因 | 回溯策略卡规则 |",
        "|---|---|---|---|",
        "| 1 | | | |",
        "",
        "## 4. A/B 对比（跑 run_eval.py --baseline 后回填）",
        "",
        "## 5. 回归结论",
        "",
        "## 6. 采用决策",
        "",
        "## 7. 剩余风险与下一步",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result_path = Path(args.result).resolve()
    if not result_path.exists():
        raise SystemExit(f"[gen_eval_report] result 不存在: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))

    comparison = result.get("comparison")
    dataset = result.get("dataset_meta", {}).get("path", "(unknown)")

    if args.report:
        report = run_eval.render_report(result, dataset, comparison)
        Path(args.report).resolve().write_text(report, encoding="utf-8")
        print(f"评测报告: {args.report}")

    if args.tuning_skeleton:
        skeleton = render_tuning_skeleton(result)
        Path(args.tuning_skeleton).resolve().write_text(skeleton, encoding="utf-8")
        print(f"调优报告骨架: {args.tuning_skeleton}")

    if not args.report and not args.tuning_skeleton:
        print(run_eval.render_report(result, dataset, comparison))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
