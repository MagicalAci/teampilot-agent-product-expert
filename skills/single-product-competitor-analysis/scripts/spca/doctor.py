import os
import shutil
from pathlib import Path
from typing import Optional

from spca.config import MCP_REQUIREMENTS, build_bootstrap_manifest

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
    override = runtime_env.get("SPCA_FFMPEG_BIN")
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
