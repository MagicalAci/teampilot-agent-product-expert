#!/usr/bin/env python3
"""Initialize a portable delivery folder for product planning work."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eppo.runtime import default_output_root, init_delivery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a standalone PRD delivery skeleton from local templates."
    )
    parser.add_argument("slug", help="Slug used in the output directory")
    parser.add_argument("--title", default="", help="Optional display title")
    parser.add_argument("--owner", default="AI Agent", help="Owner used in seeded files")
    parser.add_argument("--base-dir", default=".", help="Base directory for outputs/<slug>")
    parser.add_argument("--output-root", default="", help="Override the full output root")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing seeded files")
    parser.add_argument("--json", action="store_true", help="Print a JSON manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = (
        Path(args.output_root).resolve()
        if args.output_root
        else default_output_root(Path(args.base_dir).resolve(), args.slug)
    )
    manifest = init_delivery(
        output_root,
        args.slug,
        title=args.title or args.slug,
        owner=args.owner,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        for key, value in manifest.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
