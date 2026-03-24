#!/usr/bin/env python3
"""Initialize a portable product demo delivery."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


STACKS = ("web", "h5", "swiftui")

COMMON_TEMPLATES = {
    "demo-brief-template.md": "brief/demo-brief.md",
    "design-system-master-template.md": "design-system/MASTER.md",
    "preflight-checklist-template.md": "review/preflight-checklist.md",
    "demo-walkthrough-template.md": "review/demo-walkthrough.md",
    "developer-handoff-template.md": "handoff/developer-handoff.md",
    "demo-readme-template.md": "demo/README.md",
}

STACK_TEMPLATES = {
    "web": {
        "web-demo-template.html": "demo/web/index.html",
    },
    "h5": {
        "h5-demo-template.html": "demo/h5/index.html",
    },
    "swiftui": {
        "swiftui-demo-app-template.swift": "demo/swiftui/DemoApp.swift",
        "swiftui-content-view-template.swift": "demo/swiftui/ContentView.swift",
        "swiftui-design-tokens-template.swift": "demo/swiftui/DesignTokens.swift",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a portable product demo delivery")
    parser.add_argument("slug", help="Slug used in output file names")
    parser.add_argument("--title", default="", help="Display title")
    parser.add_argument("--stack", choices=STACKS, required=True, help="Demo stack")
    parser.add_argument("--output-root", default=".", help="Directory to write generated files into")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    return parser.parse_args()


def render_template(content: str, *, title: str, stack: str) -> str:
    replacements = {
        "[DEMO_TITLE]": title,
        "[DEMO_STACK_LABEL]": stack.upper(),
        "YYYY-MM-DD": date.today().isoformat(),
    }
    for source, target in replacements.items():
        content = content.replace(source, target)
    return content


def write_file(path: Path, content: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def home_page_override(stack: str) -> str:
    return (
        "# Page Override - home\n\n"
        "## 页面目标\n\n"
        f"- 当前平台：`{stack}`\n"
        "- 首页重点：先讲清价值，再进入主路径\n\n"
        "## 只在首页覆盖的规则\n\n"
        "- Hero 区块优先\n"
        "- CTA 不超过 2 个\n"
        "- 保持与 walkthrough 一致\n"
    )


def build_manifest(*, slug: str, title: str, stack: str, output_root: Path, files: list[Path]) -> dict:
    entrypoints = {
        "web": ["demo/web/index.html"],
        "h5": ["demo/h5/index.html"],
        "swiftui": [
            "demo/swiftui/DemoApp.swift",
            "demo/swiftui/ContentView.swift",
            "demo/swiftui/DesignTokens.swift",
        ],
    }
    return {
        "slug": slug,
        "title": title,
        "stack": stack,
        "output_root": str(output_root),
        "created_at": date.today().isoformat(),
        "entrypoints": entrypoints[stack],
        "files": [str(path.relative_to(output_root)) for path in files],
    }


def main() -> int:
    args = parse_args()
    title = args.title.strip() or args.slug
    output_root = Path(args.output_root).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    assets_dir = skill_root / "assets"

    created: list[Path] = []

    for template_name, relative_output in COMMON_TEMPLATES.items():
        template_path = assets_dir / template_name
        rendered = render_template(
            template_path.read_text(encoding="utf-8"),
            title=title,
            stack=args.stack,
        )
        output_path = output_root / relative_output
        write_file(output_path, rendered, overwrite=args.overwrite)
        created.append(output_path)

    for template_name, relative_output in STACK_TEMPLATES[args.stack].items():
        template_path = assets_dir / template_name
        rendered = render_template(
            template_path.read_text(encoding="utf-8"),
            title=title,
            stack=args.stack,
        )
        output_path = output_root / relative_output
        write_file(output_path, rendered, overwrite=args.overwrite)
        created.append(output_path)

    page_override_path = output_root / "design-system" / "pages" / "home.md"
    write_file(page_override_path, home_page_override(args.stack), overwrite=args.overwrite)
    created.append(page_override_path)

    manifest = build_manifest(
        slug=args.slug,
        title=title,
        stack=args.stack,
        output_root=output_root,
        files=created,
    )
    manifest_path = output_root / "demo-config.json"
    write_file(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        overwrite=args.overwrite,
    )
    created.append(manifest_path)

    if args.json:
        print(json.dumps({**manifest, "files": [str(path) for path in created]}, ensure_ascii=False, indent=2))
    else:
        for path in created:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
