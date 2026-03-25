from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from .doctor import build_doctor_payload
from .runtime import (
    COMPONENT_SPECS,
    DEFAULT_CRAWLERS_ROOT,
    DEFAULT_RUNTIME_HOME,
    DEFAULT_VENDOR_ROOT,
    LOCAL_ENV_EXAMPLE_PATH,
    command_preview,
    read_text_asset,
    resolve_component_path,
    write_text,
)


ENV_TEMPLATE = """# Local research system environment
# Core providers
ARK_API_KEY=
TAVILY_API_KEY=
ARK_MODEL_ID=

# Optional providers
# INFOQUEST_API_KEY=
# OPENAI_API_KEY=
# DEEPSEEK_API_KEY=
# SERPAPI_API_KEY=

# Local paths and auth
DEERFLOW_ROOT=
MEDIACRAWLER_ROOT=
XHS_DOWNLOADER_ROOT=
MEDIACRAWLER_AUTH_READY=
"""


def bootstrap_tools() -> dict:
    _refresh_common_path_entries()
    runtime_home = DEFAULT_RUNTIME_HOME
    vendor_root = DEFAULT_VENDOR_ROOT
    crawlers_root = DEFAULT_CRAWLERS_ROOT
    created: list[str] = []

    for path in (runtime_home, vendor_root, crawlers_root):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))

    config_path = runtime_home / "config.toml"
    if not config_path.exists():
        write_text(config_path, read_text_asset("default-config.toml"))
        created.append(str(config_path))

    env_path = LOCAL_ENV_EXAMPLE_PATH
    if not env_path.exists():
        write_text(env_path, ENV_TEMPLATE)
        created.append(str(env_path))

    payload = build_doctor_payload()
    return {
        "runtime_home": str(runtime_home),
        "created": created,
        "doctor": payload,
    }


def bootstrap_release(
    *,
    with_stack: bool,
    install_deerflow: bool,
    install_mediacrawler: bool,
    install_xhs_downloader: bool,
    run_doctor: bool,
    dry_run: bool,
) -> dict:
    bootstrap_payload = bootstrap_tools()
    should_install_stack = with_stack or any((install_deerflow, install_mediacrawler, install_xhs_downloader))
    stack_payload = None
    if should_install_stack:
        stack_payload = install_stack(
            install_deerflow=install_deerflow,
            install_mediacrawler=install_mediacrawler,
            install_xhs_downloader=install_xhs_downloader,
            dry_run=dry_run,
        )
    doctor_payload = build_doctor_payload()
    return {
        "runtime_home": bootstrap_payload["runtime_home"],
        "bootstrap": bootstrap_payload,
        "stack": stack_payload,
        "doctor": doctor_payload,
        "doctor_requested": run_doctor,
        "with_stack": should_install_stack,
        "text": "Bootstrap release plan ready" if dry_run else "Bootstrap release finished",
    }


def _run(command: list[str], *, cwd: Path | None = None, dry_run: bool, command_log: list[str]) -> None:
    command_log.append(command_preview(command, cwd))
    if dry_run:
        return
    subprocess.run(command, cwd=str(cwd) if cwd else None, check=True)


def _run_shell(command: str, *, dry_run: bool, command_log: list[str]) -> None:
    command_log.append(command)
    if dry_run:
        return
    subprocess.run(["sh", "-c", command], check=True)


def _refresh_common_path_entries() -> None:
    entries = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        str(Path.home() / ".local" / "bin"),
        str(Path.home() / ".cargo" / "bin"),
        str(Path.home() / ".local" / "share" / "uv" / "bin"),
    ]
    current = os.environ.get("PATH", "").split(os.pathsep)
    merged = [entry for entry in entries if Path(entry).exists()] + [entry for entry in current if entry]
    seen: set[str] = set()
    deduped: list[str] = []
    for entry in merged:
        if entry in seen:
            continue
        seen.add(entry)
        deduped.append(entry)
    os.environ["PATH"] = os.pathsep.join(deduped)


def _sudo_prefix() -> list[str]:
    geteuid = getattr(os, "geteuid", None)
    if geteuid is None or geteuid() == 0:
        return []
    if shutil.which("sudo"):
        return ["sudo"]
    raise RuntimeError("当前系统需要 sudo 或 root 权限来自动安装宿主依赖。")


def _ensure_homebrew(*, dry_run: bool, command_log: list[str]) -> str:
    _refresh_common_path_entries()
    brew = shutil.which("brew")
    if brew:
        return brew
    if platform.system() != "Darwin":
        raise RuntimeError("当前不是 macOS，不能自动安装 Homebrew。")
    _run_shell(
        'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        dry_run=dry_run,
        command_log=command_log,
    )
    _refresh_common_path_entries()
    brew = shutil.which("brew") or ("/opt/homebrew/bin/brew" if Path("/opt/homebrew/bin/brew").exists() else None)
    if not brew:
        raise RuntimeError("Homebrew 安装完成后仍未找到 brew。")
    return brew


def _install_os_packages(packages: list[str], *, dry_run: bool, command_log: list[str]) -> None:
    system = platform.system()
    if system == "Darwin":
        brew = _ensure_homebrew(dry_run=dry_run, command_log=command_log)
        _run([brew, "install", *packages], dry_run=dry_run, command_log=command_log)
        return

    if system != "Linux":
        raise RuntimeError(f"当前系统 {system} 暂不支持自动安装宿主依赖，请手动安装: {', '.join(packages)}")

    sudo = _sudo_prefix()
    if shutil.which("apt-get"):
        _run([*sudo, "apt-get", "update"], dry_run=dry_run, command_log=command_log)
        _run([*sudo, "apt-get", "install", "-y", *packages], dry_run=dry_run, command_log=command_log)
        return
    if shutil.which("dnf"):
        _run([*sudo, "dnf", "install", "-y", *packages], dry_run=dry_run, command_log=command_log)
        return
    if shutil.which("yum"):
        _run([*sudo, "yum", "install", "-y", *packages], dry_run=dry_run, command_log=command_log)
        return
    if shutil.which("pacman"):
        _run([*sudo, "pacman", "-Sy", "--noconfirm", *packages], dry_run=dry_run, command_log=command_log)
        return
    if shutil.which("zypper"):
        _run([*sudo, "zypper", "--non-interactive", "install", *packages], dry_run=dry_run, command_log=command_log)
        return

    raise RuntimeError(f"未检测到受支持的 Linux 包管理器，无法自动安装: {', '.join(packages)}")


def _ensure_git(*, dry_run: bool, command_log: list[str]) -> None:
    _refresh_common_path_entries()
    if shutil.which("git"):
        return
    _install_os_packages(["git"], dry_run=dry_run, command_log=command_log)
    _refresh_common_path_entries()


def _ensure_node(*, dry_run: bool, command_log: list[str]) -> None:
    _refresh_common_path_entries()
    if shutil.which("node"):
        return
    if platform.system() == "Darwin":
        packages = ["node"]
    elif shutil.which("apt-get"):
        packages = ["nodejs", "npm"]
    elif shutil.which("pacman"):
        packages = ["nodejs", "npm"]
    else:
        packages = ["nodejs"]
    _install_os_packages(packages, dry_run=dry_run, command_log=command_log)
    _refresh_common_path_entries()


def _ensure_uv(*, dry_run: bool, command_log: list[str]) -> None:
    _refresh_common_path_entries()
    if shutil.which("uv"):
        return

    brew = shutil.which("brew")
    if platform.system() == "Darwin" and not brew:
        brew = _ensure_homebrew(dry_run=dry_run, command_log=command_log)
    if brew:
        _run([brew, "install", "uv"], dry_run=dry_run, command_log=command_log)
        _refresh_common_path_entries()
        return

    installer_url = "https://astral.sh/uv/install.sh"
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".sh") as handle:
        script_path = Path(handle.name)
        if not dry_run:
            with urllib.request.urlopen(installer_url, timeout=20) as response:
                handle.write(response.read().decode("utf-8"))
    _run(["sh", str(script_path)], dry_run=dry_run, command_log=command_log)
    if not dry_run and script_path.exists():
        script_path.unlink()
    _refresh_common_path_entries()
    if not dry_run and not shutil.which("uv"):
        raise RuntimeError("uv 安装完成后仍未找到命令。")


def _build_deerflow_model_block() -> str:
    ark_model_id = resolve_ark_model_id()
    if os.environ.get("ARK_API_KEY"):
        return """  - name: doubao-default
    display_name: Doubao Seed 1.6 Flash
    use: deerflow.models.patched_deepseek:PatchedChatDeepSeek
    model: __ARK_MODEL_ID__
    api_base: https://ark.cn-beijing.volces.com/api/v3
    api_key: $ARK_API_KEY
    max_tokens: 8192
    supports_vision: false""".replace("__ARK_MODEL_ID__", ark_model_id)
    if os.environ.get("DEEPSEEK_API_KEY"):
        return """  - name: deepseek-default
    display_name: DeepSeek Default
    use: deerflow.models.patched_deepseek:PatchedChatDeepSeek
    model: deepseek-chat
    api_key: $DEEPSEEK_API_KEY
    max_tokens: 8192
    supports_thinking: true
    supports_vision: false
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled"""
    if os.environ.get("OPENAI_API_KEY"):
        return """  - name: openai-default
    display_name: OpenAI Default
    use: langchain_openai:ChatOpenAI
    model: gpt-4o-mini
    api_key: $OPENAI_API_KEY
    max_tokens: 4096
    temperature: 0.7
    supports_vision: true"""
    return """  - name: doubao-default
    display_name: Doubao Seed 1.6 Flash
    use: deerflow.models.patched_deepseek:PatchedChatDeepSeek
    model: __ARK_MODEL_ID__
    api_base: https://ark.cn-beijing.volces.com/api/v3
    api_key: $ARK_API_KEY
    max_tokens: 8192
    supports_vision: false""".replace("__ARK_MODEL_ID__", ark_model_id)


def resolve_ark_model_id() -> str:
    explicit_model_id = os.environ.get("ARK_MODEL_ID", "").strip()
    if explicit_model_id:
        return explicit_model_id

    api_key = os.environ.get("ARK_API_KEY", "").strip()
    fallback = "doubao-seed-1-6-flash-250828"
    if not api_key:
        return fallback

    try:
        request = urllib.request.Request(
            "https://ark.cn-beijing.volces.com/api/v3/models",
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return fallback

    models = payload.get("data", [])
    preferred_names = [
        "doubao-seed-1-6-flash",
        "doubao-seed-1-6",
        "doubao-1-5-pro-32k",
        "doubao-1-5-lite-32k",
    ]
    for preferred_name in preferred_names:
        candidates = [
            model
            for model in models
            if model.get("name") == preferred_name and model.get("status") != "Shutdown"
        ]
        if candidates:
            candidates.sort(key=lambda item: (item.get("created", 0), item.get("id", "")), reverse=True)
            return candidates[0]["id"]

    non_shutdown = [model for model in models if model.get("status") != "Shutdown" and model.get("id")]
    if non_shutdown:
        non_shutdown.sort(key=lambda item: (item.get("created", 0), item.get("id", "")), reverse=True)
        return non_shutdown[0]["id"]
    return fallback


def ensure_deerflow_managed_files(repo_root: Path, *, dry_run: bool = False) -> list[str]:
    created: list[str] = []
    config_path = repo_root / "config.local-research-system.yaml"
    env_template_path = repo_root / ".env.research-toolkit.example"
    desired_config = read_text_asset("deerflow-config.template.yaml").replace("__MODEL_BLOCK__", _build_deerflow_model_block())

    if not config_path.exists() or config_path.read_text(encoding="utf-8") != desired_config:
        if not dry_run:
            write_text(config_path, desired_config)
        created.append(str(config_path))

    if not env_template_path.exists():
        if not dry_run:
            write_text(env_template_path, read_text_asset("deerflow.env.template"))
        created.append(str(env_template_path))

    return created


def ensure_deerflow_runtime_home(repo_root: Path, *, dry_run: bool = False) -> Path:
    runtime_home = repo_root / "backend" / ".deer-flow"
    if not dry_run:
        runtime_home.mkdir(parents=True, exist_ok=True)
    return runtime_home


def install_stack(
    *,
    install_deerflow: bool = False,
    install_mediacrawler: bool = False,
    install_xhs_downloader: bool = False,
    dry_run: bool = False,
) -> dict:
    _refresh_common_path_entries()
    if not any((install_deerflow, install_mediacrawler, install_xhs_downloader)):
        install_deerflow = True
        install_mediacrawler = True
        install_xhs_downloader = True

    bootstrap_payload = bootstrap_tools()
    components: dict[str, dict] = {}

    if install_deerflow:
        components["deerflow"] = _prepare_deerflow(dry_run=dry_run)
    if install_mediacrawler:
        components["mediacrawler"] = _prepare_mediacrawler(dry_run=dry_run)
    if install_xhs_downloader:
        components["xhs_downloader"] = _prepare_xhs_downloader(dry_run=dry_run)

    return {
        "runtime_home": bootstrap_payload["runtime_home"],
        "bootstrap": bootstrap_payload,
        "components": components,
    }


def _base_component_payload(name: str, *, source: str, resolved_path: Path, commands: list[str]) -> dict:
    return {
        "name": COMPONENT_SPECS[name]["display_name"],
        "repo_url": COMPONENT_SPECS[name]["repo_url"],
        "source": source,
        "resolved_path": str(resolved_path),
        "planned_commands": commands,
    }


def _prepare_deerflow(*, dry_run: bool) -> dict:
    existing = resolve_component_path("deerflow")
    commands: list[str] = []
    if existing is not None:
        created_files = ensure_deerflow_managed_files(existing, dry_run=dry_run)
        payload = _base_component_payload("deerflow", source="existing", resolved_path=existing, commands=commands)
        payload["managed_files"] = created_files
        return payload

    target = COMPONENT_SPECS["deerflow"]["default_path"]
    _ensure_git(dry_run=dry_run, command_log=commands)
    _ensure_uv(dry_run=dry_run, command_log=commands)
    _run(["git", "clone", COMPONENT_SPECS["deerflow"]["repo_url"], str(target)], dry_run=dry_run, command_log=commands)
    _run(["uv", "python", "install", "3.12"], dry_run=dry_run, command_log=commands)
    _run(
        ["uv", "sync", "--project", str(target / "backend"), "--python", "3.12"],
        dry_run=dry_run,
        command_log=commands,
    )
    created_files = ensure_deerflow_managed_files(target, dry_run=dry_run)
    payload = _base_component_payload(
        "deerflow",
        source="planned_install" if dry_run else "installed",
        resolved_path=target,
        commands=commands,
    )
    payload["managed_files"] = created_files
    return payload


def _prepare_mediacrawler(*, dry_run: bool) -> dict:
    existing = resolve_component_path("mediacrawler")
    commands: list[str] = []
    if existing is not None:
        return _base_component_payload("mediacrawler", source="existing", resolved_path=existing, commands=commands)

    target = COMPONENT_SPECS["mediacrawler"]["default_path"]
    _ensure_git(dry_run=dry_run, command_log=commands)
    _ensure_uv(dry_run=dry_run, command_log=commands)
    _ensure_node(dry_run=dry_run, command_log=commands)
    _run(["git", "clone", COMPONENT_SPECS["mediacrawler"]["repo_url"], str(target)], dry_run=dry_run, command_log=commands)
    _run(["uv", "sync"], cwd=target, dry_run=dry_run, command_log=commands)
    playwright_command = ["uv", "run", "playwright", "install"]
    if platform.system() == "Linux":
        playwright_command.append("--with-deps")
    _run(playwright_command, cwd=target, dry_run=dry_run, command_log=commands)
    return _base_component_payload(
        "mediacrawler",
        source="planned_install" if dry_run else "installed",
        resolved_path=target,
        commands=commands,
    )


def _prepare_xhs_downloader(*, dry_run: bool) -> dict:
    existing = resolve_component_path("xhs_downloader")
    commands: list[str] = []
    if existing is not None:
        return _base_component_payload("xhs_downloader", source="existing", resolved_path=existing, commands=commands)

    target = COMPONENT_SPECS["xhs_downloader"]["default_path"]
    _ensure_git(dry_run=dry_run, command_log=commands)
    _ensure_uv(dry_run=dry_run, command_log=commands)
    _run(["git", "clone", COMPONENT_SPECS["xhs_downloader"]["repo_url"], str(target)], dry_run=dry_run, command_log=commands)
    _run(["uv", "python", "install", "3.12"], dry_run=dry_run, command_log=commands)
    _run(["uv", "sync", "--no-dev", "--python", "3.12"], cwd=target, dry_run=dry_run, command_log=commands)
    return _base_component_payload(
        "xhs_downloader",
        source="planned_install" if dry_run else "installed",
        resolved_path=target,
        commands=commands,
    )
