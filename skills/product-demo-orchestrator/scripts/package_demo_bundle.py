#!/usr/bin/env python3
"""Package a demo delivery directory into a zip bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


EXCLUDED_NAMES = {".DS_Store", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a product demo delivery into zip")
    parser.add_argument("--output-root", required=True, help="Delivery root")
    parser.add_argument("--output", required=True, help="Zip output path")
    parser.add_argument("--root-name", default="", help="Root directory inside the zip")
    return parser.parse_args()


def iter_files(root: Path) -> list[Path]:
    return sorted(
        candidate
        for candidate in root.rglob("*")
        if candidate.is_file()
        and candidate.name not in EXCLUDED_NAMES
        and candidate.suffix not in EXCLUDED_SUFFIXES
    )


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    output_path = Path(args.output).resolve()
    root_name = args.root_name.strip() or output_root.name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in iter_files(output_root):
            relative = file_path.relative_to(output_root)
            archive.write(file_path, Path(root_name) / relative)
            written += 1

    print(f"OK {output_path} ({written} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
