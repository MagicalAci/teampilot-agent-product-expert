#!/usr/bin/env python3
"""Export SVG diagrams to PNG files for portable PRD delivery."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export SVG files to PNG")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--size", type=int, default=3200)
    return parser.parse_args()


def build_jobs(paths: Sequence[str], input_dir: str | None, output_dir: str | None) -> list[tuple[Path, Path]]:
    jobs: list[tuple[Path, Path]] = []
    if input_dir:
        source_root = Path(input_dir).expanduser().resolve()
        if not source_root.is_dir():
            raise SystemExit(f"input directory does not exist: {source_root}")
        target_root = Path(output_dir).expanduser().resolve() if output_dir else source_root
        for svg_path in sorted(source_root.rglob("*.svg")):
            relative = svg_path.relative_to(source_root)
            jobs.append((svg_path, target_root / relative.with_suffix(".png")))
        return jobs

    if len(paths) == 2 and paths[0].lower().endswith(".svg") and paths[1].lower().endswith(".png"):
        return [
            (
                Path(paths[0]).expanduser().resolve(),
                Path(paths[1]).expanduser().resolve(),
            )
        ]

    target_root = Path(output_dir).expanduser().resolve() if output_dir else None
    for raw in paths:
        svg_path = Path(raw).expanduser().resolve()
        if svg_path.suffix.lower() != ".svg":
            raise SystemExit(f"expected .svg input, got: {svg_path}")
        png_path = target_root / f"{svg_path.stem}.png" if target_root else svg_path.with_suffix(".png")
        jobs.append((svg_path, png_path))
    return jobs


def export_with_qlmanage(svg_path: Path, png_path: Path, size: int) -> None:
    qlmanage = shutil.which("qlmanage")
    if not qlmanage:
        raise SystemExit(
            "qlmanage is required on macOS to export SVG to PNG. "
            "Run `bash scripts/bootstrap-macos.sh doctor` first."
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        result = subprocess.run(
            [qlmanage, "-t", "-s", str(size), "-o", str(temp_root), str(svg_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "").strip()
            raise SystemExit(f"qlmanage failed for {svg_path.name}: {message}")

        rendered = next(iter(sorted(temp_root.glob("*.png"))), None)
        if rendered is None:
            raise SystemExit(f"no PNG generated for {svg_path.name}")

        png_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rendered, png_path)


def main() -> int:
    args = parse_args()
    jobs = build_jobs(args.paths, args.input_dir, args.output_dir)
    if not jobs:
        print("no svg files found")
        return 0

    for svg_path, png_path in jobs:
        if not svg_path.is_file():
            raise SystemExit(f"svg file does not exist: {svg_path}")
        export_with_qlmanage(svg_path, png_path, args.size)
        print(f"exported {svg_path} -> {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
