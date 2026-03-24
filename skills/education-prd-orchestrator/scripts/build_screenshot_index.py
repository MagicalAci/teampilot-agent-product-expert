#!/usr/bin/env python3
"""Build a markdown screenshot index for a directory."""

from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a screenshot index in markdown.")
    parser.add_argument("directory", help="Directory to scan recursively")
    parser.add_argument(
        "--base",
        default="",
        help="Optional base path used for relative path output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    directory = Path(args.directory).resolve()
    base = Path(args.base).resolve() if args.base else directory

    files = sorted(
        [path for path in directory.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES]
    )

    print("| 序号 | 文件名 | 相对路径 |")
    print("|------|--------|----------|")
    for index, path in enumerate(files, start=1):
        relative = path.relative_to(base) if path.is_relative_to(base) else path
        print(f"| {index} | {path.name} | `{relative}` |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
