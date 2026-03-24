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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate AI PRD, test report, developer README, and required files."
    )
    parser.add_argument("--prd", help="AI PRD markdown file")
    parser.add_argument("--test-report", help="AI test report markdown file")
    parser.add_argument("--bundle-readme", help="Developer README markdown file")
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
    if has_document_issue or missing_files:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
