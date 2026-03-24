from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from eppo.runtime import (
    check_env,
    default_output_root,
    init_delivery,
    managed_root,
    run_asset_validator,
    validate_output_root,
)
from eppo.validators import (
    collect_local_asset_refs,
    delivery_documents,
    validate_evidence_log,
    validate_placeholders,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable runtime CLI for education-prd-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_env_parser = subparsers.add_parser("check-env", help="Read-only environment check")
    check_env_parser.add_argument("--managed-root", default=None)
    check_env_parser.add_argument("--json", action="store_true")

    bootstrap_parser = subparsers.add_parser("bootstrap-tools", help="Bootstrap managed runtime")
    bootstrap_parser.add_argument("--managed-root", default=None)
    bootstrap_parser.add_argument("--repair", action="store_true")
    bootstrap_parser.add_argument("--json", action="store_true")

    init_parser = subparsers.add_parser("init-delivery", help="Seed a portable delivery skeleton")
    init_parser.add_argument("slug")
    init_parser.add_argument("--title", default="")
    init_parser.add_argument("--owner", default="AI Agent")
    init_parser.add_argument("--base-dir", default=".")
    init_parser.add_argument("--output-root", default="")
    init_parser.add_argument("--overwrite", action="store_true")
    init_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate delivery contract and asset references")
    validate_parser.add_argument("--output-root", default=".")
    validate_parser.add_argument("--prd", default="")
    validate_parser.add_argument("--contract-only", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    smoke_parser = subparsers.add_parser("package-smoke", help="Run a minimal standalone smoke flow")
    smoke_parser.add_argument("--slug", default="demo-product")
    smoke_parser.add_argument("--title", default="Demo Product")
    smoke_parser.add_argument("--json", action="store_true")

    return parser


def emit(payload, *, as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if isinstance(payload, dict):
            for key, value in payload.items():
                print(f"{key}: {value}")
        else:
            print(payload)
    return 0


def cmd_check_env(args: argparse.Namespace) -> int:
    return emit(check_env(managed_root(args.managed_root)), as_json=args.json)


def cmd_bootstrap_tools(args: argparse.Namespace) -> int:
    bootstrap_script = Path(__file__).resolve().parents[1] / "bootstrap_product_planning_tools.py"
    command = [
        sys.executable,
        str(bootstrap_script),
        "repair" if args.repair else "doctor",
    ]
    if args.managed_root:
        command.extend(["--managed-root", args.managed_root])
    if args.json:
        command.append("--json")

    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def cmd_init_delivery(args: argparse.Namespace) -> int:
    base_dir = Path(args.base_dir).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else default_output_root(base_dir, args.slug)
    manifest = init_delivery(
        output_root,
        args.slug,
        title=args.title or args.slug,
        owner=args.owner,
        overwrite=args.overwrite,
    )
    return emit(manifest, as_json=args.json)


def cmd_validate(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root).resolve()
    prd_path = Path(args.prd).resolve() if args.prd else output_root / "prd.md"
    contract_status = validate_output_root(output_root, prd_path=prd_path)
    if not contract_status["ok"]:
        if args.json:
            print(json.dumps(contract_status, ensure_ascii=False, indent=2))
        else:
            print("contract validation failed")
            for item in contract_status["missing"]:
                print(f"- missing: {item}")
        return 1

    documents = delivery_documents(output_root)
    asset_result = run_asset_validator(documents)
    strict_errors: list[str] = []
    referenced_assets = collect_local_asset_refs(documents, output_root)
    if not args.contract_only:
        strict_errors.extend(validate_placeholders(documents))
        strict_errors.extend(validate_evidence_log(output_root, referenced_assets))
    payload = {
        **contract_status,
        "documents_checked": [str(path) for path in documents],
        "asset_validator_exit_code": asset_result.returncode,
        "asset_validator_stdout": asset_result.stdout.strip(),
        "asset_validator_stderr": asset_result.stderr.strip(),
        "strict_errors": strict_errors,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"output_root: {payload['output_root']}")
        print(f"prd_path: {payload['prd_path']}")
        print(f"asset_validator_exit_code: {payload['asset_validator_exit_code']}")
        if payload["asset_validator_stdout"]:
            print(payload["asset_validator_stdout"])
        for error in strict_errors:
            print(f"strict_error: {error}")
    if asset_result.returncode != 0:
        return asset_result.returncode
    if strict_errors:
        return 1
    return 0


def cmd_package_smoke(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        output_root = default_output_root(base_dir, args.slug)
        manifest = init_delivery(
            output_root,
            args.slug,
            title=args.title,
            owner="Smoke Test",
            overwrite=True,
        )
        fixture_root = Path(__file__).resolve().parents[2] / "fixtures" / "demo-product"
        shutil.copytree(fixture_root, output_root, dirs_exist_ok=True)

        contract_status = validate_output_root(output_root)
        documents = delivery_documents(output_root)
        asset_result = run_asset_validator(documents)
        strict_errors = validate_placeholders(documents)
        strict_errors.extend(
            validate_evidence_log(output_root, collect_local_asset_refs(documents, output_root))
        )
        payload = {
            "manifest": manifest,
            "contract_ok": contract_status["ok"],
            "asset_validator_exit_code": asset_result.returncode,
            "asset_validator_stdout": asset_result.stdout.strip(),
            "strict_errors": strict_errors,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"smoke_output_root: {manifest['output_root']}")
            print(f"contract_ok: {payload['contract_ok']}")
            print(f"asset_validator_exit_code: {payload['asset_validator_exit_code']}")
            if payload["asset_validator_stdout"]:
                print(payload["asset_validator_stdout"])
            for error in strict_errors:
                print(f"strict_error: {error}")
        return 0 if contract_status["ok"] and asset_result.returncode == 0 and not strict_errors else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check-env":
        return cmd_check_env(args)
    if args.command == "bootstrap-tools":
        return cmd_bootstrap_tools(args)
    if args.command == "init-delivery":
        return cmd_init_delivery(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "package-smoke":
        return cmd_package_smoke(args)
    parser.error(f"unsupported command: {args.command}")
    return 2
