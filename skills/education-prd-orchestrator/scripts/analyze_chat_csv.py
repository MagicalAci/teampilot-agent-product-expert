#!/usr/bin/env python3
"""Summarize one or more chat-log CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


TEXT_CANDIDATES = (
    "message",
    "content",
    "text",
    "body",
    "question",
    "answer",
    "remark",
    "对话",
    "聊天",
    "记录",
    "内容",
    "消息",
    "提问",
    "回复",
    "备注",
)

STATUS_CANDIDATES = ("status", "state", "result", "状态", "结果")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize chat CSV files.")
    parser.add_argument("files", nargs="+", help="CSV files to inspect")
    parser.add_argument(
        "--keywords",
        default="",
        help="Comma-separated keywords to count across text columns",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of status values to show",
    )
    return parser.parse_args()


def pick_columns(fieldnames: Iterable[str] | None, candidates: tuple[str, ...]) -> list[str]:
    if not fieldnames:
        return []
    lowered = {name.lower(): name for name in fieldnames}
    selected = []
    for candidate in candidates:
        for key, original in lowered.items():
            if candidate in key and original not in selected:
                selected.append(original)
    return selected


def summarize_csv(path: Path, keywords: list[str], top: int) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        text_columns = pick_columns(fieldnames, TEXT_CANDIDATES)
        status_columns = pick_columns(fieldnames, STATUS_CANDIDATES)
        if not text_columns:
            excluded = set(status_columns)
            text_columns = [name for name in fieldnames if name not in excluded]

        row_count = 0
        keyword_counts = Counter()
        status_counts = Counter()

        for row in reader:
            row_count += 1
            text_parts = [str(row.get(column, "")).strip() for column in text_columns]
            merged = " ".join(part for part in text_parts if part)
            for keyword in keywords:
                if keyword:
                    keyword_counts[keyword] += merged.count(keyword)

            for column in status_columns:
                value = str(row.get(column, "")).strip()
                if value:
                    status_counts[value] += 1

    return {
        "file": str(path),
        "rows": row_count,
        "columns": fieldnames,
        "text_columns": text_columns,
        "status_columns": status_columns,
        "keyword_counts": dict(keyword_counts),
        "top_status_values": status_counts.most_common(top),
    }


def main() -> int:
    args = parse_args()
    keywords = [item.strip() for item in args.keywords.split(",") if item.strip()]
    summaries = [summarize_csv(Path(file), keywords, args.top) for file in args.files]
    print(json.dumps({"files": summaries}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
