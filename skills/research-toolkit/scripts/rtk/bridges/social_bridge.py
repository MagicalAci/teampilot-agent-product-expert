from __future__ import annotations

import subprocess
from pathlib import Path

from rtk.runtime import AUTH_ROOT, DEFAULT_RUNTIME_HOME, SKILL_ROOT, command_preview, now_iso, resolve_component_path


def _default_output_root() -> Path:
    slug = now_iso().replace(":", "-")
    return DEFAULT_RUNTIME_HOME / "social-runs" / slug


def build_social_plan(
    *,
    platform: str,
    engine: str,
    keywords: str | None,
    url: str | None,
    output_root: str | None,
    login_type: str,
    headless: bool,
    get_comment: bool,
    get_sub_comment: bool,
    save_data_option: str,
    cookie: str | None,
    proxy: str | None,
) -> dict:
    if not keywords and not url:
        raise RuntimeError("run-social 至少需要 --keywords 或 --url 之一。")

    mediacrawler_root = resolve_component_path("mediacrawler")
    xhs_downloader_root = resolve_component_path("xhs_downloader")

    selected_engine = engine
    if engine == "auto":
        if url and platform == "xhs" and xhs_downloader_root is not None:
            selected_engine = "xhs_downloader"
        elif mediacrawler_root is not None:
            selected_engine = "mediacrawler"
        elif url and platform == "xhs" and xhs_downloader_root is not None:
            selected_engine = "xhs_downloader"
        else:
            raise RuntimeError("未检测到可用社媒引擎。请先运行 install-stack 安装或复用爬虫。")

    resolved_output_root = Path(output_root) if output_root else _default_output_root()

    if selected_engine == "mediacrawler":
        if mediacrawler_root is None:
            raise RuntimeError("未检测到 MediaCrawler 安装。请先运行 install-stack --mediacrawler。")
        return _build_mediacrawler_plan(
            repo_root=mediacrawler_root,
            platform=platform,
            keywords=keywords,
            url=url,
            output_root=resolved_output_root,
            login_type=login_type,
            headless=headless,
            get_comment=get_comment,
            get_sub_comment=get_sub_comment,
            save_data_option=save_data_option,
        )

    if selected_engine == "xhs_downloader":
        if platform != "xhs":
            raise RuntimeError("XHS-Downloader 只支持 xhs 平台。")
        if not url:
            raise RuntimeError("XHS-Downloader 需要 --url。")
        if xhs_downloader_root is None:
            raise RuntimeError("未检测到 XHS-Downloader 安装。请先运行 install-stack --xhs-downloader。")
        return _build_xhs_downloader_plan(
            repo_root=xhs_downloader_root,
            url=url,
            output_root=resolved_output_root,
            cookie=cookie,
            proxy=proxy,
        )

    raise RuntimeError(f"不支持的社媒引擎: {selected_engine}")


def build_social_auth_plan(*, platform: str, open_qr: bool = True) -> dict:
    mediacrawler_root = resolve_component_path("mediacrawler")
    if mediacrawler_root is None:
        raise RuntimeError("未检测到 MediaCrawler 安装。请先运行 install-stack --mediacrawler。")

    qr_output = AUTH_ROOT / f"{platform}-login-qrcode.png"
    auth_ready_marker = mediacrawler_root / ".auth.ready"
    bridge_path = SKILL_ROOT / "scripts" / "rtk" / "bridges" / "mediacrawler_auth.py"
    command = [
        "uv",
        "run",
        "python",
        str(bridge_path),
        "--repo-root",
        str(mediacrawler_root),
        "--platform",
        platform,
        "--qr-output",
        str(qr_output),
        "--auth-ready-marker",
        str(auth_ready_marker),
    ]
    if open_qr:
        command.append("--open-qr")

    return {
        "engine": "mediacrawler_auth",
        "mode": "auth",
        "cwd": str(mediacrawler_root),
        "command": command,
        "output_root": str(qr_output.parent),
        "resolved_paths": {
            "mediacrawler_root": str(mediacrawler_root),
            "qr_code_path": str(qr_output),
            "auth_ready_marker": str(auth_ready_marker),
        },
        "command_preview": command_preview(command, mediacrawler_root),
    }


def _build_mediacrawler_plan(
    *,
    repo_root: Path,
    platform: str,
    keywords: str | None,
    url: str | None,
    output_root: Path,
    login_type: str,
    headless: bool,
    get_comment: bool,
    get_sub_comment: bool,
    save_data_option: str,
) -> dict:
    mode = "search" if keywords else "detail"
    evidence_root = output_root / "mediacrawler" / platform
    command = [
        "uv",
        "run",
        "main.py",
        "--platform",
        platform,
        "--lt",
        login_type,
        "--type",
        mode,
        "--headless",
        "yes" if headless else "no",
        "--get_comment",
        "yes" if get_comment else "no",
        "--get_sub_comment",
        "yes" if get_sub_comment else "no",
        "--save_data_option",
        save_data_option,
        "--save_data_path",
        str(evidence_root),
    ]
    if keywords:
        command.extend(["--keywords", keywords])
    if url:
        command.extend(["--specified_id", url])
    return {
        "engine": "mediacrawler",
        "mode": mode,
        "cwd": repo_root,
        "command": command,
        "output_root": evidence_root,
        "resolved_paths": {
            "mediacrawler_root": str(repo_root),
            "output_root": str(evidence_root),
        },
    }


def _build_xhs_downloader_plan(
    *,
    repo_root: Path,
    url: str,
    output_root: Path,
    cookie: str | None,
    proxy: str | None,
) -> dict:
    evidence_root = output_root / "xhs-downloader"
    command = [
        "uv",
        "run",
        "main.py",
        "--url",
        url,
        "--work_path",
        str(evidence_root),
    ]
    if cookie:
        command.extend(["--cookie", cookie])
    if proxy:
        command.extend(["--proxy", proxy])
    return {
        "engine": "xhs_downloader",
        "mode": "detail",
        "cwd": repo_root,
        "command": command,
        "output_root": evidence_root,
        "resolved_paths": {
            "xhs_downloader_root": str(repo_root),
            "output_root": str(evidence_root),
        },
    }


def run_social_plan(plan: dict, *, dry_run: bool) -> dict:
    preview = command_preview(plan["command"], plan["cwd"])
    payload = {
        "engine": plan["engine"],
        "mode": plan["mode"],
        "resolved_paths": plan["resolved_paths"],
        "command_preview": preview,
        "text": "Social dry-run prepared" if dry_run else "Social crawler finished",
    }
    if dry_run:
        return payload

    Path(plan["output_root"]).mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        plan["command"],
        cwd=str(plan["cwd"]),
        capture_output=True,
        text=True,
        check=False,
    )
    payload["stdout"] = result.stdout
    payload["stderr"] = result.stderr
    payload["returncode"] = result.returncode
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return payload
