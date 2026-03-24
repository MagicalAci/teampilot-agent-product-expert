#!/usr/bin/env python3
"""Package AI script deliverables into a zip bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


EXCLUDED_NAMES = {".DS_Store", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package AI script deliverables into zip.")
    parser.add_argument("output", help="Output zip path")
    parser.add_argument("paths", nargs="+", help="Files or directories to include")
    parser.add_argument(
        "--root-name",
        default="ai-script-bundle",
        help="Root directory name inside the zip",
    )
    return parser.parse_args()


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(
            child
            for child in path.rglob("*")
            if child.is_file()
            and child.name not in EXCLUDED_NAMES
            and child.suffix not in EXCLUDED_SUFFIXES
        )
    raise FileNotFoundError(f"Path does not exist: {path}")


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in args.paths:
            source = Path(item).resolve()
            files = iter_files(source)
            base = source.parent if source.is_file() else source

            for file_path in files:
                relative = file_path.name if source.is_file() else file_path.relative_to(base)
                arcname = Path(args.root_name) / relative
                archive.write(file_path, arcname)
                written += 1

    print(f"OK {output_path} ({written} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
