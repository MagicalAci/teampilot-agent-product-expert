#!/usr/bin/env python3
"""Initialize AI planning deliverables from local templates."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create AI PRD, test report, and developer README from templates."
    )
    parser.add_argument("slug", help="Slug used in output file names")
    parser.add_argument(
        "--title",
        default="",
        help="Optional display title used to replace template placeholders",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write generated files into",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    return parser.parse_args()


def render_template(content: str, title: str) -> str:
    today = date.today()
    replacements = {
        "[项目名 / 能力名]": title,
        "[功能 / 版本 / 能力]": title,
        "YYYY-MM-DD": today.isoformat(),
        "YYYY.MM.DD": today.strftime("%Y.%m.%d"),
    }
    for source, target in replacements.items():
        content = content.replace(source, target)
    return content


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    title = args.title.strip() or args.slug
    output_dir = Path(args.output_dir).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    assets_dir = skill_root / "assets"

    templates = {
        "ai-prd-template.md": output_dir / f"{args.slug}-ai-prd.md",
        "test-record-template.md": output_dir / f"{args.slug}-ai-test-report.md",
        "developer-readme-template.md": output_dir / f"{args.slug}-bundle-readme.md",
        "script-bundle-manifest-template.md": output_dir / f"{args.slug}-bundle-manifest.md",
    }

    created = []
    for template_name, output_path in templates.items():
        template_path = assets_dir / template_name
        content = template_path.read_text(encoding="utf-8")
        rendered = render_template(content, title)
        write_file(output_path, rendered, args.overwrite)
        created.append(output_path)

    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
