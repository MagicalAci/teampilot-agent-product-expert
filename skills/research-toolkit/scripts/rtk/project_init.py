from __future__ import annotations

import shutil
from pathlib import Path

from .doctor import build_doctor_payload, render_doctor_text
from .runtime import (
    DEFAULT_RUNTIME_HOME,
    now_iso,
    read_json_asset,
    read_text_asset,
    write_json,
    write_text,
)


DIRECTORIES = ("drafts", "evidence", "analysis", "delivery", ".meta")


def _render_template(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def init_project(slug: str, title: str, output_root: Path, overwrite: bool = False) -> dict:
    if output_root.exists() and overwrite:
        shutil.rmtree(output_root)
    elif output_root.exists():
        raise FileExistsError(f"输出目录已存在: {output_root}")

    output_root.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (output_root / relative).mkdir(parents=True, exist_ok=True)

    doctor_payload = build_doctor_payload()
    replacements = {
        "__SLUG__": slug,
        "__TITLE__": title,
        "__CREATED_AT__": now_iso(),
        "__OUTPUT_ROOT__": str(output_root),
        "__RUNTIME_HOME__": str(DEFAULT_RUNTIME_HOME),
    }

    manifest = _render_template(
        read_text_asset("project-manifest-template.json"),
        replacements,
    )
    outline = _render_template(
        read_text_asset("report-outline-template.md"),
        {"__TITLE__": title},
    )

    payload = read_json_asset("project-manifest-template.json")
    payload["slug"] = slug
    payload["title"] = title
    payload["createdAt"] = replacements["__CREATED_AT__"]
    payload["workspaceOutputRoot"] = replacements["__OUTPUT_ROOT__"]
    payload["runtimeHome"] = replacements["__RUNTIME_HOME__"]
    payload["modes"] = {
        "basicReady": doctor_payload["basic_ready"],
        "deepReady": doctor_payload["deep_ready"],
        "socialReady": doctor_payload["social_ready"],
    }

    write_json(output_root / "manifest.json", payload)
    write_text(output_root / "drafts" / "00-report-outline.md", outline)
    write_text(output_root / "evidence" / "_evidence-index.csv", read_text_asset("evidence-index-template.csv") + "\n")
    write_text(output_root / ".meta" / "doctor-report.md", render_doctor_text(doctor_payload))
    write_text(output_root / ".meta" / "README.md", manifest)

    return {
        "slug": slug,
        "title": title,
        "output_root": str(output_root),
        "directories": [str(output_root / relative) for relative in DIRECTORIES],
        "manifest": str(output_root / "manifest.json"),
    }
