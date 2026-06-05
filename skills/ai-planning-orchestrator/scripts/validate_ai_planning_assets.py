#!/usr/bin/env python3
"""Validate AI planning deliverables and required sections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PRD_HEADINGS = (
    "## 输入数据结构定义",
    "## AI策略",
    "## 提示词模块",
    "## AI脚本",
)

TEST_REPORT_HEADINGS = (
    "## 1. 测试范围",
    "## 2. 测试环境",
    "## 3. 执行记录",
    "## 4. 关键输出结论",
    "## 5. 风险与限制",
)

BUNDLE_README_HEADINGS = (
    "## 1. 交付概览",
    "## 2. 目录结构",
    "## 3. 入口文件",
    "## 4. 配置项",
    "## 5. 调用方式",
    "## 6. 验证命令",
    "## 7. 已知限制",
    "## 8. 目标项目还需补的能力",
)

STRATEGY_CARD_HEADINGS = (
    "## 1. 策略规则集",
    "## 2. 映射设计",
    "## 3. 六段 Prompt",
    "## 4. 覆盖率自检",
)

EVAL_REPORT_HEADINGS = (
    "## 1. 评测对象",
    "## 2. 评测集",
    "## 3. 评测体系",
    "## 4. 总体结果",
    "## 6. 失败用例与聚类",
    "## 7. 与基线对比",
)

TUNING_REPORT_HEADINGS = (
    "## 1. 调优对象",
    "## 2. 失败归因",
    "## 3. 变更清单",
    "## 4. A/B 对比",
    "## 5. 回归结论",
    "## 6. 采用决策",
)

VALID_BUCKETS = {"production", "adversarial", "edge", "failure_replay"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate AI PRD, test report, developer README, and required files."
    )
    parser.add_argument("--prd", help="AI PRD markdown file")
    parser.add_argument("--test-report", help="AI test report markdown file")
    parser.add_argument("--bundle-readme", help="Developer README markdown file")
    parser.add_argument("--strategy-card", help="Prompt strategy card markdown file")
    parser.add_argument("--eval-report", help="AI eval report markdown file")
    parser.add_argument("--tuning-report", help="AI tuning report markdown file")
    parser.add_argument("--eval-dataset", help="Eval dataset JSONL file to validate")
    parser.add_argument(
        "--require-file",
        action="append",
        default=[],
        help="Additional file or directory that must exist. Can be passed multiple times.",
    )
    return parser.parse_args()


def validate_markdown(path: Path, headings: tuple[str, ...]) -> dict:
    result = {"path": str(path), "exists": path.exists(), "missing_headings": []}
    if not path.exists():
        return result

    content = path.read_text(encoding="utf-8")
    result["missing_headings"] = [heading for heading in headings if heading not in content]
    return result


def validate_eval_dataset(path: Path) -> dict:
    result = {"path": str(path), "exists": path.exists(), "total": 0, "errors": []}
    if not path.exists():
        return result
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            result["errors"].append(f"#{idx} JSON 解析失败: {exc}")
            continue
        result["total"] += 1
        if not case.get("id"):
            result["errors"].append(f"#{idx} 缺少 id")
        if case.get("bucket") not in VALID_BUCKETS:
            result["errors"].append(f"#{idx} bucket 非法: {case.get('bucket')!r}")
        if "input" not in case:
            result["errors"].append(f"#{idx} 缺少 input")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            result["errors"].append(f"#{idx} assertions 应为非空数组")
    return result


def main() -> int:
    args = parse_args()
    summary: dict[str, object] = {"documents": {}, "missing_files": []}

    if args.prd:
        summary["documents"]["prd"] = validate_markdown(
            Path(args.prd).resolve(), PRD_HEADINGS
        )
    if args.test_report:
        summary["documents"]["test_report"] = validate_markdown(
            Path(args.test_report).resolve(), TEST_REPORT_HEADINGS
        )
    if args.bundle_readme:
        summary["documents"]["bundle_readme"] = validate_markdown(
            Path(args.bundle_readme).resolve(), BUNDLE_README_HEADINGS
        )
    if args.strategy_card:
        summary["documents"]["strategy_card"] = validate_markdown(
            Path(args.strategy_card).resolve(), STRATEGY_CARD_HEADINGS
        )
    if args.eval_report:
        summary["documents"]["eval_report"] = validate_markdown(
            Path(args.eval_report).resolve(), EVAL_REPORT_HEADINGS
        )
    if args.tuning_report:
        summary["documents"]["tuning_report"] = validate_markdown(
            Path(args.tuning_report).resolve(), TUNING_REPORT_HEADINGS
        )

    if args.eval_dataset:
        summary["eval_dataset"] = validate_eval_dataset(Path(args.eval_dataset).resolve())

    missing_files = []
    for item in args.require_file:
        candidate = Path(item).resolve()
        if not candidate.exists():
            missing_files.append(str(candidate))
    summary["missing_files"] = missing_files

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    has_document_issue = any(
        (not value["exists"]) or bool(value["missing_headings"])
        for value in summary["documents"].values()
    )
    dataset = summary.get("eval_dataset")
    has_dataset_issue = bool(dataset) and ((not dataset["exists"]) or bool(dataset["errors"]))
    if has_document_issue or missing_files or has_dataset_issue:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
