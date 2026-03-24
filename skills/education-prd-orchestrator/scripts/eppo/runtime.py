from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


REQUIRED_OUTPUT_DIRS = ("images", "html", "charts", "evidence", "review")
DEFAULT_MANAGED_ROOT = Path.home() / ".cursor" / "skills-runtime" / "education-prd-orchestrator"


def skill_root() -> Path:
    return Path(__file__).resolve().parents[2]


def scripts_root() -> Path:
    return skill_root() / "scripts"


def asset_path(name: str) -> Path:
    return skill_root() / "assets" / name


def managed_root(path: str | None = None) -> Path:
    raw = path or os.environ.get("EPPO_MANAGED_ROOT") or str(DEFAULT_MANAGED_ROOT)
    return Path(raw).expanduser().resolve()


def venv_python_path(runtime_root: Path) -> Path:
    bin_dir = runtime_root / "venv" / ("Scripts" if os.name == "nt" else "bin")
    exe_name = "python.exe" if os.name == "nt" else "python"
    return bin_dir / exe_name


def default_output_root(base_dir: Path, slug: str) -> Path:
    return base_dir.resolve() / "outputs" / slug


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_template(content: str, *, title: str, owner: str) -> str:
    today = date.today().isoformat()
    replacements = {
        "[产品名]": title,
        "YYYY-MM-DD": today,
        "[负责人]": owner,
    }
    for source, target in replacements.items():
        content = content.replace(source, target)
    return content


def review_summary_template(title: str, slug: str) -> str:
    return f"""# Review Summary

- 项目标题：`{title}`
- 交付 slug：`{slug}`
- 当前状态：`draft`

## 当前检查清单

- [ ] PRD 主文档已生成并完成第一轮结构搭建
- [ ] 证据目录已建立，来源分类清楚
- [ ] HTML 页面稿与图表目录已就绪
- [ ] 图片引用校验已执行
- [ ] 如存在仓库内镜像路径，已完成同步
"""


def handoff_template(title: str, slug: str, output_root: Path) -> str:
    return f"""# Handoff

- 项目标题：`{title}`
- 交付 slug：`{slug}`
- 交付根目录：`{output_root}`

## 交付物

- 主文档：`{output_root / "prd.md"}`
- 图片目录：`{output_root / "images"}`
- HTML 页面稿：`{output_root / "html"}`
- 图表目录：`{output_root / "charts"}`
- 证据目录：`{output_root / "evidence"}`

## 待确认

- [ ] 产品定义已经冻结
- [ ] 证据缺口已补齐
- [ ] 图文口径一致
"""


def directory_note_template(title: str, section: str, hints: list[str]) -> str:
    bullet_lines = "\n".join(f"- {item}" for item in hints)
    return f"""# {section}

> 项目：`{title}`

{bullet_lines}
"""


def maybe_copy_asset(template_name: str, output_path: Path, *, overwrite: bool) -> None:
    source = asset_path(template_name)
    if not source.exists():
        return
    write_text(output_path, source.read_text(encoding="utf-8"), overwrite=overwrite)


def init_delivery(output_root: Path, slug: str, *, title: str, owner: str, overwrite: bool) -> dict[str, str]:
    output_root = output_root.resolve()
    for directory in REQUIRED_OUTPUT_DIRS:
        ensure_dir(output_root / directory)

    prd_template = asset_path("prd-template.md").read_text(encoding="utf-8")
    rendered_prd = render_template(prd_template, title=title, owner=owner)
    write_text(output_root / "prd.md", rendered_prd, overwrite=overwrite)

    index_log = asset_path("index-log-template.md").read_text(encoding="utf-8")
    write_text(output_root / "review" / "index-log-template.md", index_log, overwrite=overwrite)
    write_text(
        output_root / "review" / "review-summary.md",
        review_summary_template(title, slug),
        overwrite=overwrite,
    )
    write_text(
        output_root / "review" / "handoff.md",
        handoff_template(title, slug, output_root),
        overwrite=overwrite,
    )

    write_text(
        output_root / "evidence" / "README.md",
        directory_note_template(
            title,
            "Evidence",
            [
                "把搜索记录、截图索引、CSV/XLSX 汇总和人工补充材料放在这里。",
                "后续可继续补 `search-plan.md`、`evidence-log.csv` 等模板化文件。",
            ],
        ),
        overwrite=overwrite,
    )
    write_text(
        output_root / "html" / "README.md",
        directory_note_template(
            title,
            "HTML Drafts",
            [
                "这里放页面稿、功能稿和可直接预览的 HTML 交付件。",
                "默认每个页面稿都应配一段“解决什么问题”的说明。",
            ],
        ),
        overwrite=overwrite,
    )
    write_text(
        output_root / "charts" / "README.md",
        directory_note_template(
            title,
            "Charts",
            [
                "这里放图表 HTML、SVG、PNG 和原始数据文件。",
                "图表要能对应到正文中的具体判断，而不是只做装饰。",
            ],
        ),
        overwrite=overwrite,
    )
    write_text(
        output_root / "images" / "README.md",
        directory_note_template(
            title,
            "Images",
            [
                "结构图优先保存 SVG 源文件，再导出 PNG 供正文引用。",
                "真实截图和生成图都要保留可追溯的文件名。",
            ],
        ),
        overwrite=overwrite,
    )

    maybe_copy_asset("user-checkpoint-template.md", output_root / "review" / "user-checkpoint-template.md", overwrite=overwrite)
    maybe_copy_asset("diagram-brief-template.md", output_root / "images" / "diagram-brief-template.md", overwrite=overwrite)
    maybe_copy_asset("html-page-template.html", output_root / "html" / "page-template.html", overwrite=overwrite)
    maybe_copy_asset("chart-template.html", output_root / "charts" / "chart-template.html", overwrite=overwrite)
    maybe_copy_asset("chart-data-template.csv", output_root / "charts" / "chart-data-template.csv", overwrite=overwrite)
    maybe_copy_asset("search-plan-template.md", output_root / "evidence" / "search-plan.md", overwrite=overwrite)
    maybe_copy_asset("evidence-log-template.csv", output_root / "evidence" / "evidence-log.csv", overwrite=overwrite)

    manifest = {
        "slug": slug,
        "title": title,
        "output_root": str(output_root),
        "prd": str(output_root / "prd.md"),
        "images": str(output_root / "images"),
        "html": str(output_root / "html"),
        "charts": str(output_root / "charts"),
        "evidence": str(output_root / "evidence"),
        "review": str(output_root / "review"),
    }
    write_text(
        output_root / "review" / "delivery-manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2),
        overwrite=overwrite,
    )
    return manifest


def check_env(runtime_root: Path) -> dict[str, Any]:
    runtime_root = runtime_root.resolve()
    bootstrap_status_path = runtime_root / "logs" / "bootstrap-status.json"
    bootstrap_status = None
    if bootstrap_status_path.exists():
        bootstrap_status = json.loads(bootstrap_status_path.read_text(encoding="utf-8"))

    requirements_file = skill_root() / "requirements.txt"
    requirements_hash_file = runtime_root / "requirements.sha256"
    venv_python = venv_python_path(runtime_root)

    return {
        "ready": venv_python.exists() and requirements_hash_file.exists(),
        "managed_root": str(runtime_root),
        "venv_python": str(venv_python),
        "requirements_file": str(requirements_file),
        "requirements_hash_present": requirements_hash_file.exists(),
        "bootstrap_status_path": str(bootstrap_status_path),
        "bootstrap_status": bootstrap_status,
        "qlmanage_available": bool(shutil.which("qlmanage")),
    }


def validate_output_root(output_root: Path, *, prd_path: Path | None = None) -> dict[str, Any]:
    output_root = output_root.resolve()
    prd_path = prd_path.resolve() if prd_path else output_root / "prd.md"
    missing = []
    if not prd_path.exists():
        missing.append(str(prd_path))
    for directory in REQUIRED_OUTPUT_DIRS:
        candidate = output_root / directory
        if not candidate.exists():
            missing.append(str(candidate))
    return {
        "ok": not missing,
        "output_root": str(output_root),
        "prd_path": str(prd_path),
        "missing": missing,
    }


def run_asset_validator(file_paths: list[Path]) -> subprocess.CompletedProcess[str]:
    validator = scripts_root() / "validate_prd_assets.py"
    return subprocess.run(
        [sys.executable, str(validator), *[str(path) for path in file_paths]],
        text=True,
        capture_output=True,
        check=False,
    )
