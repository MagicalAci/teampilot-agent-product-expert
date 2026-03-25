from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Optional

from rtk.config import MCP_REQUIREMENTS, build_bootstrap_manifest

INTERACTIVE_AUTH_REQUIREMENTS = {"cursor-tab-session", "login-or-cookie", "cookie"}


def find_mcp_install_paths(server_id: str, home: Optional[Path] = None) -> list[str]:
    base_home = home or Path.home()
    projects_root = base_home / ".cursor" / "projects"
    if not projects_root.exists():
        return []
    matches = []
    for candidate in projects_root.glob(f"*/mcps/{server_id}"):
        matches.append(str(candidate.resolve()))
    return sorted(set(matches))


def detect_mcp_status(home: Optional[Path] = None) -> dict:
    servers = []
    blocking = []
    degraded = []
    for item in MCP_REQUIREMENTS:
        install_paths = find_mcp_install_paths(item["server_id"], home=home)
        installed = bool(install_paths)
        needs_login = installed and item["auth_requirement"] in INTERACTIVE_AUTH_REQUIREMENTS
        if not installed and item["required"]:
            status = "需安装"
            blocking.append(item["server_id"])
            degraded.append(item["fallback"])
        elif not installed:
            status = "当前降级模式"
            degraded.append(item["fallback"])
        elif needs_login:
            status = "需登录初始化"
            degraded.append(item["fallback"])
        else:
            status = "已安装"
        servers.append(
            {
                **item,
                "status": status,
                "installed": installed,
                "needs_login": needs_login,
                "install_paths": install_paths,
            }
        )
    return {
        "servers": servers,
        "blocking": blocking,
        "degraded": degraded,
    }


def detect_ffmpeg_status(env: Optional[dict] = None) -> dict:
    runtime_env = env or os.environ
    override = runtime_env.get("RTK_FFMPEG_BIN")
    if override:
        override_path = Path(override).expanduser()
        if override_path.exists():
            return {
                "available": True,
                "bin": str(override_path.resolve()),
                "source": "env",
            }
    system_bin = shutil.which("ffmpeg")
    return {
        "available": system_bin is not None,
        "bin": system_bin,
        "source": "path" if system_bin else "missing",
    }


def collect_doctor_status(home: Optional[Path] = None, env: Optional[dict] = None) -> dict:
    manifest = build_bootstrap_manifest(home=home)
    venv_python = Path(manifest["managed_runtime"]["venv"]) / "bin" / "python"
    system_python = shutil.which("python3")
    mcp = detect_mcp_status(home=home)
    ffmpeg = detect_ffmpeg_status(env=env)

    notes = []
    if not venv_python.exists():
        notes.append("受管 venv 尚未创建，先运行 bootstrap-macos.sh 任一命令即可自动准备。")
    if not ffmpeg["available"]:
        notes.append("ffmpeg 尚不可用，bootstrap-macos.sh 会在首启时自动安装。")
    if mcp["blocking"]:
        notes.append("存在阻断型 MCP 缺失，真实交互路径与登录后页面分析会降级。")
    if any(item["status"] == "需登录初始化" for item in mcp["servers"]):
        notes.append("部分 MCP 已安装但仍需登录 / Cookie / 扫码初始化，完成后请重新运行 doctor。")

    return {
        "managed_runtime": {
            **manifest["managed_runtime"],
            "root_exists": Path(manifest["managed_runtime"]["root"]).exists(),
            "venv_exists": Path(manifest["managed_runtime"]["venv"]).exists(),
            "python_bin": str(venv_python.resolve()) if venv_python.exists() else None,
        },
        "system_packages": manifest["system_packages"],
        "python": {
            "available": venv_python.exists() or system_python is not None,
            "system_python3": system_python,
        },
        "ffmpeg": ffmpeg,
        "mcp": mcp,
        "notes": notes,
    }


# ── LRS Doctor Functions (ported from local-research-system) ────────────────

REQUIRED_COMMANDS = ("git", "python3")
OPTIONAL_COMMANDS = ("uv", "docker", "node", "pnpm", "gh")
ENV_KEYS = (
    "ARK_API_KEY",
    "TAVILY_API_KEY",
    "INFOQUEST_API_KEY",
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "SERPAPI_API_KEY",
)
MEDIACRAWLER_AUTH_ENV = "MEDIACRAWLER_AUTH_READY"
MIN_DEEP_PYTHON = (3, 12)


def _command_status(name: str) -> dict:
    resolved = shutil.which(name)
    return {
        "installed": bool(resolved),
        "path": resolved or "",
    }


def _env_status(name: str) -> dict:
    value = os.environ.get(name, "")
    return {
        "configured": bool(value),
        "present": bool(value),
    }


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _version_text() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def build_doctor_payload() -> dict:
    from rtk.runtime import (
        DEFAULT_DEERFLOW_ROOT,
        DEFAULT_MEDIACRAWLER_ROOT,
        DEFAULT_RUNTIME_HOME,
        DEFAULT_XHS_DOWNLOADER_ROOT,
        LOCAL_ENV_EXAMPLE_PATH,
        LOCAL_ENV_PATH,
        resolve_component_path,
    )

    required = {name: _command_status(name) for name in REQUIRED_COMMANDS}
    optional = {name: _command_status(name) for name in OPTIONAL_COMMANDS}
    envs = {name: _env_status(name) for name in ENV_KEYS}

    local_env_exists = LOCAL_ENV_PATH.exists()
    local_env_example_exists = LOCAL_ENV_EXAMPLE_PATH.exists()
    runtime_home = DEFAULT_RUNTIME_HOME
    config_path = runtime_home / "config.toml"
    resolved_deerflow_root = resolve_component_path("deerflow")
    resolved_mediacrawler_root = resolve_component_path("mediacrawler")
    resolved_xhs_downloader_root = resolve_component_path("xhs_downloader")

    deerflow_root = resolved_deerflow_root or DEFAULT_DEERFLOW_ROOT
    mediacrawler_root = resolved_mediacrawler_root or DEFAULT_MEDIACRAWLER_ROOT
    xhs_downloader_root = resolved_xhs_downloader_root or DEFAULT_XHS_DOWNLOADER_ROOT
    mediacrawler_auth_marker = mediacrawler_root / ".auth.ready"
    mediacrawler_auth_ready = _is_truthy(os.environ.get(MEDIACRAWLER_AUTH_ENV, "")) or mediacrawler_auth_marker.exists()
    xhs_downloader_ready = resolved_xhs_downloader_root is not None
    mediacrawler_keyword_ready = resolved_mediacrawler_root is not None and mediacrawler_auth_ready
    uv_ready = optional["uv"]["installed"]
    python_deep_ready = sys.version_info[:2] >= MIN_DEEP_PYTHON or uv_ready
    core_model_ready = envs["ARK_API_KEY"]["configured"]
    search_provider_ready = envs["TAVILY_API_KEY"]["configured"] or envs["INFOQUEST_API_KEY"]["configured"]

    basic_ready = all(item["installed"] for item in required.values())
    deep_ready = basic_ready and uv_ready and python_deep_ready and resolved_deerflow_root is not None
    social_ready = basic_ready and (
        mediacrawler_keyword_ready or xhs_downloader_ready
    )

    next_steps: list[str] = []
    if not required["git"]["installed"]:
        next_steps.append("先安装 git。")
    if not required["python3"]["installed"]:
        next_steps.append("先安装 python3。")
    if not config_path.exists():
        next_steps.append("运行 python scripts/run_pipeline.py bootstrap-tools --json 生成运行时目录和默认配置。")
    if not local_env_example_exists:
        next_steps.append(f"先生成本地私有环境模板：{LOCAL_ENV_EXAMPLE_PATH}。")
    if not local_env_exists:
        next_steps.append(f"如需本机持久化密钥，请创建 {LOCAL_ENV_PATH}。")
    if not core_model_ready:
        next_steps.append(f"在 {LOCAL_ENV_PATH} 或当前 shell 中配置 ARK_API_KEY，作为默认 DeerFlow 模型。")
    if not search_provider_ready:
        next_steps.append(
            f"首次联网搜索前，在 {LOCAL_ENV_PATH} 中配置 TAVILY_API_KEY（推荐）或 INFOQUEST_API_KEY（可选）。"
        )
    if not uv_ready:
        next_steps.append("如需深度模式或自动安装第三方组件，先安装 uv。")
    if not python_deep_ready:
        next_steps.append("如需真实 DeerFlow 深度模式，请使用 Python 3.12+。")
    if resolved_deerflow_root is None:
        next_steps.append(f"如需深度模式，把 DeerFlow 准备到 {deerflow_root}。")
    if resolved_mediacrawler_root is None:
        next_steps.append(f"如需社媒模式，把 MediaCrawler 准备到 {mediacrawler_root}。")
    elif not mediacrawler_auth_ready:
        next_steps.append(
            f"MediaCrawler 已找到，但仍需授权信号：设置 {MEDIACRAWLER_AUTH_ENV}=1 或创建 {mediacrawler_auth_marker}。"
        )
    if not xhs_downloader_ready:
        next_steps.append(f"如需额外复用 XHS-Downloader，把它准备到 {xhs_downloader_root}。")

    first_run_command = "bash scripts/bootstrap.sh --with-stack --doctor"
    auth_command = "/本地调研授权"
    if not basic_ready or not config_path.exists() or not local_env_example_exists:
        primary_action = {
            "kind": "command",
            "message": f"先只做这一步：{first_run_command}",
            "command": first_run_command,
            "reply_when_done": "跑好了",
        }
    elif not search_provider_ready:
        primary_action = {
            "kind": "edit_env",
            "message": f"现在只差搜索 key。去 {LOCAL_ENV_PATH} 里填上 TAVILY_API_KEY，填好后回复：配好了",
            "env_file_path": str(LOCAL_ENV_PATH),
            "env_key": "TAVILY_API_KEY",
            "reply_when_done": "配好了",
        }
    elif resolved_mediacrawler_root is not None and not mediacrawler_auth_ready:
        primary_action = {
            "kind": "auth",
            "message": f"现在只差小红书登录态。运行 {auth_command}，扫码后回复：扫好了",
            "command": auth_command,
            "reply_when_done": "扫好了",
        }
    else:
        primary_action = {
            "kind": "ready",
            "message": "环境已就绪，可以继续当前目标命令。",
        }

    return {
        "runtime_home": str(runtime_home),
        "python_version": _version_text(),
        "python_deep_ready": python_deep_ready,
        "local_env": {
            "path": str(LOCAL_ENV_PATH),
            "exists": local_env_exists,
            "example_path": str(LOCAL_ENV_EXAMPLE_PATH),
            "example_exists": local_env_example_exists,
        },
        "provider_policy": {
            "default_model_env": "ARK_API_KEY",
            "first_run_search_env": "TAVILY_API_KEY",
            "optional_search_env": "INFOQUEST_API_KEY",
            "optional_model_envs": ["OPENAI_API_KEY", "DEEPSEEK_API_KEY"],
            "legacy_search_envs": ["SERPAPI_API_KEY"],
        },
        "paths": {
            "config": str(config_path),
            "deerflow_root": str(deerflow_root),
            "mediacrawler_root": str(mediacrawler_root),
            "xhs_downloader_root": str(xhs_downloader_root),
        },
        "connectors": {
            "resolved_mediacrawler_root": str(resolved_mediacrawler_root) if resolved_mediacrawler_root else None,
            "resolved_xhs_downloader_root": str(resolved_xhs_downloader_root) if resolved_xhs_downloader_root else None,
            "mediacrawler_auth_ready": mediacrawler_auth_ready,
            "mediacrawler_keyword_ready": mediacrawler_keyword_ready,
            "mediacrawler_auth_env": MEDIACRAWLER_AUTH_ENV,
            "mediacrawler_auth_marker": str(mediacrawler_auth_marker),
            "xhs_downloader_ready": xhs_downloader_ready,
        },
        "required_commands": required,
        "optional_commands": optional,
        "env": envs,
        "basic_ready": basic_ready,
        "deep_ready": deep_ready,
        "social_ready": social_ready,
        "recommended_next_steps": next_steps,
        "onboarding": {
            "first_run_command": first_run_command,
            "local_env_path": str(LOCAL_ENV_PATH),
            "auth_command": auth_command,
            "reply_words": {
                "after_bootstrap": "跑好了",
                "after_env_setup": "配好了",
                "after_auth": "扫好了",
            },
            "primary_action": primary_action,
        },
    }


def render_doctor_text(payload: dict) -> str:
    onboarding = payload.get("onboarding", {})
    primary_action = onboarding.get("primary_action", {})
    lines = [
        "本地调研体检结果",
        f"- 基础模式: {'就绪' if payload['basic_ready'] else '未就绪'}",
        f"- 深度模式: {'就绪' if payload['deep_ready'] else '未就绪'}",
        f"- 社媒模式: {'就绪' if payload['social_ready'] else '未就绪'}",
        f"- Python: {payload['python_version']}",
        f"- 本机私有环境文件: {payload['local_env']['path']}",
        "",
        "接手人下一步：",
    ]
    if primary_action:
        lines.append(f"- {primary_action.get('message', '环境已就绪')}")
        reply_when_done = primary_action.get("reply_when_done")
        if reply_when_done:
            lines.append(f"- 做完后回复：{reply_when_done}")
    lines.extend(
        [
            "",
            "必需命令：",
        ]
    )
    for name, status in payload["required_commands"].items():
        marker = "OK" if status["installed"] else "MISSING"
        lines.append(f"- {name}: {marker}")
    lines.append("")
    lines.append("详细后续建议：")
    for item in payload["recommended_next_steps"] or ["当前没有额外阻塞项。"]:
        lines.append(f"- {item}")
    return "\n".join(lines)
