#!/usr/bin/env python3
"""Unified CLI for product-demo-orchestrator."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


STACKS = ("web", "h5", "swiftui")
DEPLOY_PLATFORMS = ("vercel", "surge", "netlify", "cloudflare")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable runtime CLI for product-demo-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a demo delivery")
    init_parser.add_argument("slug")
    init_parser.add_argument("--title", default="")
    init_parser.add_argument("--stack", choices=STACKS, required=True)
    init_parser.add_argument("--output-root", default=".")
    init_parser.add_argument("--overwrite", action="store_true")
    init_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a demo delivery")
    validate_parser.add_argument("--output-root", required=True)

    package_parser = subparsers.add_parser("package", help="Package a demo delivery")
    package_parser.add_argument("--output-root", required=True)
    package_parser.add_argument("--output", required=True)
    package_parser.add_argument("--root-name", default="")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy a demo to a cloud platform")
    deploy_parser.add_argument("--output-root", required=True)
    deploy_parser.add_argument("--platform", choices=DEPLOY_PLATFORMS, default="vercel")
    deploy_parser.add_argument("--project-name", default="")
    deploy_parser.add_argument("--prod", action="store_true")
    deploy_parser.add_argument("--json", action="store_true")

    smoke_parser = subparsers.add_parser("package-smoke", help="Run init + validate + package across stacks")
    smoke_parser.add_argument("--json", action="store_true")

    return parser


def script_path(name: str) -> Path:
    return Path(__file__).resolve().parent / name


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def cmd_init(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        str(script_path("init_demo_delivery.py")),
        args.slug,
        "--stack",
        args.stack,
        "--output-root",
        args.output_root,
    ]
    if args.title:
        command.extend(["--title", args.title])
    if args.overwrite:
        command.append("--overwrite")
    if args.json:
        command.append("--json")
    result = run_command(command)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def cmd_validate(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        str(script_path("validate_demo_assets.py")),
        "--output-root",
        args.output_root,
    ]
    result = run_command(command)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def cmd_package(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        str(script_path("package_demo_bundle.py")),
        "--output-root",
        args.output_root,
        "--output",
        args.output,
    ]
    if args.root_name:
        command.extend(["--root-name", args.root_name])
    result = run_command(command)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def cmd_deploy(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        str(script_path("deploy_demo.py")),
        "--output-root",
        args.output_root,
        "--platform",
        args.platform,
    ]
    if args.project_name:
        command.extend(["--project-name", args.project_name])
    if args.prod:
        command.append("--prod")
    if args.json:
        command.append("--json")
    result = run_command(command)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def cmd_package_smoke(args: argparse.Namespace) -> int:
    payload: dict[str, object] = {"stacks": {}}
    ok = True

    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        for stack in STACKS:
            slug = f"demo-{stack}"
            output_root = base / slug
            bundle_path = base / "dist" / f"{slug}.zip"

            init_result = run_command(
                [
                    sys.executable,
                    str(script_path("init_demo_delivery.py")),
                    slug,
                    "--title",
                    f"Demo {stack.upper()}",
                    "--stack",
                    stack,
                    "--output-root",
                    str(output_root),
                    "--overwrite",
                    "--json",
                ]
            )
            validate_result = run_command(
                [
                    sys.executable,
                    str(script_path("validate_demo_assets.py")),
                    "--output-root",
                    str(output_root),
                ]
            )
            package_result = run_command(
                [
                    sys.executable,
                    str(script_path("package_demo_bundle.py")),
                    "--output-root",
                    str(output_root),
                    "--output",
                    str(bundle_path),
                    "--root-name",
                    slug,
                ]
            )

            stack_ok = (
                init_result.returncode == 0
                and validate_result.returncode == 0
                and package_result.returncode == 0
                and bundle_path.exists()
            )
            ok = ok and stack_ok
            payload["stacks"][stack] = {
                "ok": stack_ok,
                "init_exit_code": init_result.returncode,
                "validate_exit_code": validate_result.returncode,
                "package_exit_code": package_result.returncode,
                "bundle_exists": bundle_path.exists(),
            }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for stack, summary in payload["stacks"].items():
            print(f"{stack}: {summary}")
    return 0 if ok else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "package":
        return cmd_package(args)
    if args.command == "deploy":
        return cmd_deploy(args)
    if args.command == "package-smoke":
        return cmd_package_smoke(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
