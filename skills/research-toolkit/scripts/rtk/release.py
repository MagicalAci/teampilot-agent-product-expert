from __future__ import annotations

import shutil
from pathlib import Path

from .runtime import SKILL_ROOT, now_iso, write_json

EXCLUDED_PARTS = {
    "dist",
    "outputs",
    "__pycache__",
    ".pytest_cache",
}
EXCLUDED_NAMES = {
    ".DS_Store",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def _should_exclude(relative_path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in relative_path.parts):
        return True
    if relative_path.name in EXCLUDED_NAMES:
        return True
    if relative_path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def build_release(*, output_dir: str | None = None) -> dict:
    skill_root = SKILL_ROOT
    dist_root = Path(output_dir).expanduser() if output_dir else skill_root / "dist"
    staging_root = dist_root / "research-toolkit"
    release_tag = now_iso().replace(":", "").replace("-", "").replace("+", "_")
    archive_base = dist_root / f"research-toolkit-{release_tag}"
    archive_path = archive_base.with_suffix(".zip")
    manifest_path = dist_root / "release-manifest.json"

    if staging_root.exists():
        shutil.rmtree(staging_root)
    dist_root.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()

    copied_files: list[str] = []
    for source in skill_root.rglob("*"):
        relative_path = source.relative_to(skill_root)
        if _should_exclude(relative_path):
            continue
        target = staging_root / relative_path
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_files.append(str(relative_path))

    created_archive = shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(dist_root),
        base_dir=staging_root.name,
    )
    payload = {
        "skill_root": str(skill_root),
        "dist_root": str(dist_root),
        "staging_root": str(staging_root),
        "archive_path": created_archive,
        "excluded_parts": sorted(EXCLUDED_PARTS),
        "excluded_suffixes": sorted(EXCLUDED_SUFFIXES),
        "copied_files_count": len(copied_files),
        "sample_files": copied_files[:20],
        "generated_at": now_iso(),
    }
    write_json(manifest_path, payload)
    payload["manifest_path"] = str(manifest_path)
    return payload
