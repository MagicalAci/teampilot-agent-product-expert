#!/usr/bin/env python3
"""Bootstrap the portable runtime for education-prd-orchestrator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import Any


DEFAULT_MANAGED_ROOT = Path.home() / ".cursor" / "skills-runtime" / "education-prd-orchestrator"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap managed Python runtime for education-prd-orchestrator."
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("doctor", "repair"),
        default="doctor",
        help="doctor checks and repairs missing pieces, repair forces dependency reinstall.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON status object.",
    )
    parser.add_argument(
        "--managed-root",
        default=os.environ.get("EPPO_MANAGED_ROOT", str(DEFAULT_MANAGED_ROOT)),
        help="Override the managed runtime root.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, text=True, capture_output=True)


def resolve_paths(managed_root_raw: str) -> dict[str, Path]:
    skill_root = Path(__file__).resolve().parents[1]
    managed_root = Path(managed_root_raw).expanduser().resolve()
    venv_dir = managed_root / "venv"
    log_dir = managed_root / "logs"
    requirements_file = skill_root / "requirements.txt"
    requirements_hash_file = managed_root / "requirements.sha256"
    venv_bin_dir = venv_dir / ("Scripts" if os.name == "nt" else "bin")
    return {
        "skill_root": skill_root,
        "managed_root": managed_root,
        "venv_dir": venv_dir,
        "venv_bin_dir": venv_bin_dir,
        "log_dir": log_dir,
        "requirements_file": requirements_file,
        "requirements_hash_file": requirements_hash_file,
    }


def ensure_venv(venv_dir: Path, python_bin: Path) -> Path:
    if not python_bin.exists():
        builder = venv.EnvBuilder(
            with_pip=True,
            clear=False,
            symlinks=os.name != "nt",
        )
        builder.create(str(venv_dir))
    if not python_bin.exists():
        raise RuntimeError(f"failed to create venv python at {python_bin}")
    return python_bin


def install_requirements(
    python_bin: Path,
    requirements_file: Path,
    requirements_hash_file: Path,
    *,
    force: bool,
) -> bool:
    desired_hash = sha256_file(requirements_file)
    current_hash = requirements_hash_file.read_text(encoding="utf-8").strip() if requirements_hash_file.exists() else ""
    should_install = force or current_hash != desired_hash
    if not should_install:
        return False

    run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python_bin), "-m", "pip", "install", "-r", str(requirements_file)])
    requirements_hash_file.parent.mkdir(parents=True, exist_ok=True)
    requirements_hash_file.write_text(desired_hash, encoding="utf-8")
    return True


def detect_capabilities() -> dict[str, Any]:
    system_name = platform.system()
    return {
        "platform": system_name,
        "qlmanage": shutil.which("qlmanage"),
        "python": sys.executable,
        "has_venv": hasattr(venv, "EnvBuilder"),
    }


def write_status_log(status: dict[str, Any], log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    output_path = log_dir / "bootstrap-status.json"
    output_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def bootstrap(managed_root_raw: str, *, force: bool) -> dict[str, Any]:
    paths = resolve_paths(managed_root_raw)
    paths["managed_root"].mkdir(parents=True, exist_ok=True)
    capabilities = detect_capabilities()
    if not capabilities["has_venv"]:
        raise RuntimeError("the current Python runtime does not support venv")

    venv_python_name = "python.exe" if os.name == "nt" else "python"
    python_bin = ensure_venv(paths["venv_dir"], paths["venv_bin_dir"] / venv_python_name)
    installed = install_requirements(
        python_bin,
        paths["requirements_file"],
        paths["requirements_hash_file"],
        force=force,
    )

    status = {
        "ok": True,
        "platform": capabilities["platform"],
        "managed_root": str(paths["managed_root"]),
        "venv_python": str(python_bin),
        "requirements_file": str(paths["requirements_file"]),
        "requirements_installed": installed,
        "qlmanage_available": bool(capabilities["qlmanage"]),
        "qlmanage_path": capabilities["qlmanage"],
        "notes": [
            "Use the managed venv Python to run local scripts.",
            "On macOS, SVG to PNG export prefers qlmanage so no extra image runtime is needed.",
        ],
    }
    write_status_log(status, paths["log_dir"])
    return status


def format_human(status: dict[str, Any]) -> str:
    lines = [
        "environment ready",
        f"- managed_root: {status['managed_root']}",
        f"- venv_python: {status['venv_python']}",
        f"- requirements_installed: {status['requirements_installed']}",
        f"- qlmanage_available: {status['qlmanage_available']}",
    ]
    if not status["qlmanage_available"] and status["platform"] == "Darwin":
        lines.append("- warning: qlmanage not found, SVG export may fail until Quick Look tools are restored")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        status = bootstrap(args.managed_root, force=args.command == "repair")
    except subprocess.CalledProcessError as exc:
        error_status = {
            "ok": False,
            "command": exc.cmd,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
        if args.json:
            print(json.dumps(error_status, ensure_ascii=False, indent=2))
        else:
            print("bootstrap failed")
            if exc.stderr:
                print(exc.stderr.strip())
        return 1
    except Exception as exc:  # pragma: no cover - final guardrail
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"bootstrap failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(format_human(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
