#!/usr/bin/env python3
"""Validate local image references in markdown files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
FENCED_CODE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")


def strip_code_segments(text: str) -> str:
    """Remove fenced code blocks and inline code spans.

    Image references inside markdown code samples are documentation examples
    (e.g. the PRD template's prototype-image format), not real embedded assets,
    so they must not be treated as missing files.
    """
    text = FENCED_CODE.sub("", text)
    text = INLINE_CODE.sub("", text)
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate markdown image references.")
    parser.add_argument("files", nargs="+", help="Markdown files to validate")
    return parser.parse_args()


def resolve_path(source: str, file_path: Path) -> Path | None:
    source = source.strip()
    if source.startswith(("http://", "https://", "data:")):
        return None
    candidate = Path(source)
    if candidate.is_absolute():
        return candidate
    return (file_path.parent / candidate).resolve()


def collect_references(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() in {".md", ".markdown"}:
        content = strip_code_segments(content)
    return MARKDOWN_IMAGE.findall(content) + HTML_IMAGE.findall(content)


def main() -> int:
    args = parse_args()
    missing = []

    for file_name in args.files:
        file_path = Path(file_name).resolve()
        for source in collect_references(file_path):
            candidate = resolve_path(source, file_path)
            if candidate is not None and not candidate.exists():
                missing.append({"file": str(file_path), "source": source})

    if missing:
        print("MISSING")
        for item in missing:
            print(f"- {item['file']} -> {item['source']}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
