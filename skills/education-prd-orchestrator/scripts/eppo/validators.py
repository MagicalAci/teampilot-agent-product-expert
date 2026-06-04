from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable


PLACEHOLDER_RE = re.compile(
    r"\[(?:待填|待补|产品名|页面名|模块名|图表标题|topic|slug|来源名|URL或本地路径|文件名|要证明的价值|要证明的判断|页面角色|谁被优先服务|用户完成什么|结论数字或一句判断)[^\]]*\]"
)
FENCED_CODE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_code_segments(text: str) -> str:
    """Drop fenced/inline code so example asset references in markdown snippets
    are not mistaken for real embedded assets."""
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def delivery_documents(output_root: Path) -> list[Path]:
    documents = [output_root / "prd.md"]
    for folder in ["html", "charts", "review"]:
        folder_path = output_root / folder
        if not folder_path.exists():
            continue
        documents.extend(sorted(folder_path.glob("*.md")))
        documents.extend(sorted(folder_path.glob("*.html")))
    filtered = []
    for path in documents:
        if not path.exists():
            continue
        lowered = path.name.lower()
        if "template" in lowered or lowered == "readme.md":
            continue
        filtered.append(path)
    return filtered


def find_placeholders(text: str) -> list[str]:
    matches = PLACEHOLDER_RE.findall(text)
    if "`draft`" in text or "`todo`" in text:
        matches.append("backtick-status-placeholder")
    return matches


def validate_placeholders(file_paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in file_paths:
        text = path.read_text(encoding="utf-8")
        placeholders = find_placeholders(text)
        if placeholders:
            errors.append(f"placeholder content remains in {path.name}: {', '.join(sorted(set(placeholders)))}")
    return errors


def read_evidence_rows(evidence_path: Path) -> list[dict[str, str]]:
    with evidence_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_evidence_log(output_root: Path, referenced_assets: set[str]) -> list[str]:
    evidence_path = output_root / "evidence" / "evidence-log.csv"
    if not evidence_path.exists():
        return [f"missing evidence log: {evidence_path}"]

    rows = read_evidence_rows(evidence_path)
    if not rows:
        return ["evidence log has no data rows"]

    errors: list[str] = []
    registered_assets: set[str] = set()
    required_fields = [
        "evidence_id",
        "source_type",
        "source_name",
        "source_url_or_path",
        "claim_supported",
        "evidence_strength",
        "status",
    ]

    for index, row in enumerate(rows, start=2):
        for field in required_fields:
            value = (row.get(field) or "").strip()
            if not value:
                errors.append(f"evidence row {index}: missing {field}")
                continue
            if PLACEHOLDER_RE.search(value):
                errors.append(f"evidence row {index}: placeholder remains in {field}")

        local_asset = (row.get("local_asset_path") or "").strip()
        if local_asset:
            if PLACEHOLDER_RE.search(local_asset):
                errors.append(f"evidence row {index}: placeholder remains in local_asset_path")
            else:
                registered_assets.add(Path(local_asset).as_posix())
                if not (output_root / local_asset).exists():
                    errors.append(f"evidence row {index}: local asset missing {local_asset}")

    missing_bindings = sorted(asset for asset in referenced_assets if asset not in registered_assets)
    for asset in missing_bindings:
        errors.append(f"referenced asset is not registered in evidence log: {asset}")
    return errors


def collect_local_asset_refs(file_paths: Iterable[Path], output_root: Path) -> set[str]:
    markdown_image = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    html_image = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
    refs: set[str] = set()
    for path in file_paths:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".md", ".markdown"}:
            text = strip_code_segments(text)
        for match in markdown_image.findall(text) + html_image.findall(text):
            source = match.strip().split("#", 1)[0].split("?", 1)[0]
            if source.startswith(("http://", "https://", "data:")):
                continue
            resolved = (path.parent / source).resolve()
            try:
                refs.add(resolved.relative_to(output_root.resolve()).as_posix())
            except ValueError:
                candidate = (output_root / source).resolve()
                try:
                    refs.add(candidate.relative_to(output_root.resolve()).as_posix())
                except ValueError:
                    continue
    return refs
