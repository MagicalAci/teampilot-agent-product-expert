"""Unified CLI for the Research Toolkit.

Merges SPCA's structured analysis pipeline (init/collect/analyze/export/validate)
with LRS's toolchain commands (install-stack/run-deerflow/run-social/run-research).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from rtk.analyzers import (
    analyze_competition,
    analyze_monetization,
    analyze_product_overview,
    analyze_seo,
    analyze_sentiment,
    analyze_user,
)
from rtk.collectors import COLLECTOR_MAP
from rtk.config import (
    CHANNEL_BACKEND_PRIORITY,
    CHANNEL_OUTPUT_PLATFORMS,
    CHANNEL_PLATFORM_FALLBACKS,
    PLATFORM_BACKEND_PRIORITY,
    PLATFORM_OUTPUT_ORDER,
    PLATFORM_SAMPLE_TARGETS,
    PLATFORM_TO_CHANNEL,
)
from rtk.doctor import collect_doctor_status
from rtk.exporters import build_report_context, build_report_markdown
from rtk.normalizers import build_gap_list, normalize_sources
from rtk.runtime import init_workspace, load_task_card, resolve_paths
from rtk.utils import read_json, read_jsonl, slugify, write_csv, write_json, write_jsonl, write_text
from rtk.validators import validate_pipeline_outputs

# ---------------------------------------------------------------------------
# Lazy imports for toolchain commands (only loaded when needed)
# ---------------------------------------------------------------------------


def _lazy_doctor_payload():
    from rtk.doctor import build_doctor_payload, render_doctor_text
    return build_doctor_payload, render_doctor_text


def _lazy_install():
    from rtk.install import bootstrap_release, bootstrap_tools, install_stack
    from rtk.install import ensure_deerflow_managed_files, ensure_deerflow_runtime_home
    return bootstrap_release, bootstrap_tools, install_stack, ensure_deerflow_managed_files, ensure_deerflow_runtime_home


def _lazy_release():
    from rtk.release import build_release
    return build_release


def _lazy_project_init():
    from rtk.project_init import init_project
    return init_project


def _lazy_orchestrator():
    from rtk.orchestrator import run_research
    return run_research


def _lazy_social():
    from rtk.bridges.social_bridge import build_social_plan, run_social_plan
    return build_social_plan, run_social_plan


def _lazy_runtime_ext():
    from rtk.runtime import SKILL_ROOT, AUTH_ROOT, command_preview, extract_json_object, resolve_component_path
    return SKILL_ROOT, AUTH_ROOT, command_preview, extract_json_object, resolve_component_path


# ---------------------------------------------------------------------------
# Unified output helper
# ---------------------------------------------------------------------------

def _emit(payload: dict, json_mode: bool) -> None:
    if json_mode:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return
    if "text" in payload:
        sys.stdout.write(payload["text"] + "\n")
    else:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Package smoke check
# ---------------------------------------------------------------------------

REQUIRED_PACKAGE_FILES = (
    "SKILL.md",
    "README.md",
    "requirements.txt",
    "agents/openai.yaml",
    "protocols/review-gate.md",
    "protocols/evidence-guide.md",
    "protocols/writing-collaboration.md",
    "protocols/fact-check.md",
    "protocols/crawl-playbook.md",
    "schemas/task-card.schema.json",
    "task-types/single-product.md",
    "task-types/direction-research.md",
    "scripts/run_pipeline.py",
    "scripts/bootstrap.sh",
    "scripts/bootstrap-macos.sh",
    "scripts/build-release.sh",
    "scripts/rtk/cli.py",
    "scripts/rtk/config.py",
    "scripts/rtk/doctor.py",
    "scripts/rtk/bridges/deerflow_bridge.py",
    "scripts/rtk/bridges/social_bridge.py",
    "scripts/rtk/bridges/mediacrawler_auth.py",
    ".gitignore",
)


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research Toolkit — unified research & analysis pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── SPCA pipeline commands ──

    p_init = sub.add_parser("init", help="Initialize task workspace from a task card")
    p_init.add_argument("--task-card", required=True)
    p_init.add_argument("--task-type", choices=["single-product", "direction", "market-landscape", "user-research", "custom"])

    p_collect = sub.add_parser("collect", help="Run sub-agent collection from imports/")
    p_collect.add_argument("--task-card", required=True)

    p_analyze = sub.add_parser("analyze", help="Normalize evidence and run analyzers")
    p_analyze.add_argument("--task-card", required=True)

    p_export = sub.add_parser("export", help="Export report (requires gate pass)")
    p_export.add_argument("--task-card", required=True)

    p_validate = sub.add_parser("validate", help="Schema and artifact completeness check")
    p_validate.add_argument("--task-card", required=True)

    # ── Toolchain commands ──

    p_doctor = sub.add_parser("doctor", help="Environment + MCP + toolchain health check")
    p_doctor.add_argument("--json", action="store_true")

    p_install = sub.add_parser("install-stack", help="Install DeerFlow / MediaCrawler / XHS-Downloader")
    p_install.add_argument("--deerflow", action="store_true")
    p_install.add_argument("--mediacrawler", action="store_true")
    p_install.add_argument("--xhs-downloader", action="store_true")
    p_install.add_argument("--dry-run", action="store_true")
    p_install.add_argument("--json", action="store_true")

    p_bootstrap = sub.add_parser("bootstrap-release", help="Bootstrap host runtime + optional stack install")
    p_bootstrap.add_argument("--with-stack", action="store_true")
    p_bootstrap.add_argument("--deerflow", action="store_true")
    p_bootstrap.add_argument("--mediacrawler", action="store_true")
    p_bootstrap.add_argument("--xhs-downloader", action="store_true")
    p_bootstrap.add_argument("--doctor", action="store_true")
    p_bootstrap.add_argument("--dry-run", action="store_true")
    p_bootstrap.add_argument("--json", action="store_true")

    p_deerflow = sub.add_parser("run-deerflow", help="Deep research via DeerFlow bridge")
    p_deerflow.add_argument("--prompt", required=True)
    p_deerflow.add_argument("--thread-id", default="research-toolkit")
    p_deerflow.add_argument("--model-name")
    p_deerflow.add_argument("--subagent-enabled", action="store_true")
    p_deerflow.add_argument("--disable-thinking", action="store_true")
    p_deerflow.add_argument("--config-path")
    p_deerflow.add_argument("--dry-run", action="store_true")
    p_deerflow.add_argument("--json", action="store_true")

    p_social = sub.add_parser("run-social", help="Active social media collection via MediaCrawler/XHS")
    p_social.add_argument("--platform", default="xhs")
    p_social.add_argument("--engine", choices=["auto", "mediacrawler", "xhs_downloader"], default="auto")
    p_social.add_argument("--keywords")
    p_social.add_argument("--url")
    p_social.add_argument("--output-root")
    p_social.add_argument("--login-type", default="qrcode")
    p_social.add_argument("--save-data-option", default="jsonl")
    p_social.add_argument("--cookie")
    p_social.add_argument("--proxy")
    p_social.add_argument("--headless", action="store_true")
    p_social.add_argument("--get-comment", action="store_true")
    p_social.add_argument("--get-sub-comment", action="store_true")
    p_social.add_argument("--dry-run", action="store_true")
    p_social.add_argument("--json", action="store_true")

    p_auth = sub.add_parser("run-social-auth", help="QR code auth for MediaCrawler")
    p_auth.add_argument("--platform", default="xhs")
    p_auth.add_argument("--open-qr", action="store_true")
    p_auth.add_argument("--json", action="store_true")

    p_research = sub.add_parser("run-research", help="End-to-end research orchestrator")
    p_research.add_argument("--topic", required=True)
    p_research.add_argument("--slug")
    p_research.add_argument("--title")
    p_research.add_argument("--output-root")
    p_research.add_argument("--platform", default="xhs")
    p_research.add_argument("--keywords")
    p_research.add_argument("--url")
    p_research.add_argument("--skip-deep", action="store_true")
    p_research.add_argument("--skip-social", action="store_true")
    p_research.add_argument("--overwrite", action="store_true")
    p_research.add_argument("--dry-run", action="store_true")
    p_research.add_argument("--json", action="store_true")

    p_smoke = sub.add_parser("package-smoke", help="Validate package file contract")
    p_smoke.add_argument("--json", action="store_true")

    p_release = sub.add_parser("build-release", help="Build clean distributable zip")
    p_release.add_argument("--output-dir")
    p_release.add_argument("--json", action="store_true")

    p_frames = sub.add_parser("extract-frames", help="Extract video frames via ffmpeg")
    p_frames.add_argument("input_video")
    p_frames.add_argument("--output-dir")
    p_frames.add_argument("--fps", type=float, default=1.0)
    p_frames.add_argument("--json", action="store_true")

    return parser


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd = args.command

    # ── SPCA pipeline commands (require --task-card) ──

    if cmd in {"init", "collect", "analyze", "export", "validate"}:
        task_card_path = Path(args.task_card).resolve()
        task_card = load_task_card(task_card_path)
        handlers = {
            "init": cmd_init,
            "collect": cmd_collect,
            "analyze": cmd_analyze,
            "export": cmd_export,
            "validate": cmd_validate,
        }
        return handlers[cmd](task_card, task_card_path)

    # ── Toolchain commands ──

    if cmd == "doctor":
        return cmd_doctor_merged(json_output=args.json)

    if cmd == "install-stack":
        _, _, install_stack_fn, _, _ = _lazy_install()
        payload = install_stack_fn(
            install_deerflow=args.deerflow,
            install_mediacrawler=args.mediacrawler,
            install_xhs_downloader=args.xhs_downloader,
            dry_run=args.dry_run,
        )
        payload["text"] = "Install stack plan ready" if args.dry_run else "Install stack finished"
        _emit(payload, args.json)
        return 0

    if cmd == "bootstrap-release":
        bootstrap_release_fn, _, _, _, _ = _lazy_install()
        payload = bootstrap_release_fn(
            with_stack=args.with_stack,
            install_deerflow=args.deerflow,
            install_mediacrawler=args.mediacrawler,
            install_xhs_downloader=args.xhs_downloader,
            run_doctor=args.doctor,
            dry_run=args.dry_run,
        )
        _emit(payload, args.json)
        return 0

    if cmd == "run-deerflow":
        payload = _run_deerflow(
            prompt=args.prompt,
            thread_id=args.thread_id,
            model_name=args.model_name,
            subagent_enabled=args.subagent_enabled,
            disable_thinking=args.disable_thinking,
            config_path=args.config_path,
            dry_run=args.dry_run,
        )
        _emit(payload, args.json)
        return 0

    if cmd == "run-social":
        payload = _run_social(
            platform=args.platform,
            engine=args.engine,
            keywords=args.keywords,
            url=args.url,
            output_root=args.output_root,
            login_type=args.login_type,
            headless=args.headless,
            get_comment=args.get_comment,
            get_sub_comment=args.get_sub_comment,
            save_data_option=args.save_data_option,
            cookie=args.cookie,
            proxy=args.proxy,
            dry_run=args.dry_run,
        )
        _emit(payload, args.json)
        return 0

    if cmd == "run-social-auth":
        payload = _run_social_auth(
            platform=args.platform,
            open_qr=args.open_qr,
            json_mode=args.json,
        )
        _emit(payload, args.json)
        return 0

    if cmd == "run-research":
        run_research_fn = _lazy_orchestrator()
        payload = run_research_fn(
            topic=args.topic,
            slug=args.slug,
            title=args.title,
            output_root=args.output_root,
            platform=args.platform,
            keywords=args.keywords,
            url=args.url,
            skip_deep=args.skip_deep,
            skip_social=args.skip_social,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        _emit(payload, args.json)
        return 0

    if cmd == "package-smoke":
        SKILL_ROOT, *_ = _lazy_runtime_ext()
        missing = [f for f in REQUIRED_PACKAGE_FILES if not (SKILL_ROOT / f).exists()]
        payload = {"contract_ok": not missing, "missing_files": missing, "skill_root": str(SKILL_ROOT)}
        payload["text"] = "Package smoke passed" if not missing else "Package smoke failed"
        _emit(payload, args.json)
        return 0 if not missing else 1

    if cmd == "build-release":
        build_release_fn = _lazy_release()
        payload = build_release_fn(output_dir=args.output_dir)
        payload["text"] = f"Release built at {payload['archive_path']}"
        _emit(payload, args.json)
        return 0

    if cmd == "extract-frames":
        return _run_extract_frames(args)

    parser.error(f"Unsupported command: {cmd}")
    return 2


# ---------------------------------------------------------------------------
# Merged doctor (SPCA MCP checks + LRS toolchain checks)
# ---------------------------------------------------------------------------

def cmd_doctor_merged(*, json_output: bool) -> int:
    spca_status = collect_doctor_status()

    lrs_payload = {}
    try:
        build_doctor_payload_fn, render_doctor_text_fn = _lazy_doctor_payload()
        lrs_payload = build_doctor_payload_fn()
    except Exception:
        pass

    merged = {
        "managed_runtime": spca_status.get("managed_runtime", {}),
        "ffmpeg": spca_status.get("ffmpeg", {}),
        "mcp": spca_status.get("mcp", {}),
        "notes": spca_status.get("notes", []),
        "toolchain": {
            "deerflow": lrs_payload.get("connectors", {}).get("deerflow", "not_checked"),
            "mediacrawler": lrs_payload.get("connectors", {}).get("mediacrawler", "not_checked"),
            "xhs_downloader": lrs_payload.get("connectors", {}).get("xhs_downloader", "not_checked"),
            "social_ready": lrs_payload.get("readiness", {}).get("social_ready", False),
            "deep_ready": lrs_payload.get("readiness", {}).get("deep_ready", False),
        },
        "api_keys": lrs_payload.get("env_vars", {}),
        "readiness": {
            "basic_ready": lrs_payload.get("readiness", {}).get("basic_ready", True),
            "deep_ready": lrs_payload.get("readiness", {}).get("deep_ready", False),
            "social_ready": lrs_payload.get("readiness", {}).get("social_ready", False),
            "full_ready": (
                lrs_payload.get("readiness", {}).get("basic_ready", False)
                and lrs_payload.get("readiness", {}).get("deep_ready", False)
                and lrs_payload.get("readiness", {}).get("social_ready", False)
            ),
        },
        "primary_action": lrs_payload.get("primary_action"),
    }

    if json_output:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        return 0

    print("# Research Toolkit Doctor\n")

    mr = merged["managed_runtime"]
    if mr:
        print(f"- 受管运行时：`{mr.get('root', 'N/A')}`")
        print(f"- venv：`{'✓' if mr.get('venv_exists') else '✗'}`")

    ff = merged["ffmpeg"]
    if ff:
        print(f"- ffmpeg：`{'✓' if ff.get('available') else '✗'}`")

    tc = merged["toolchain"]
    print(f"\n## 工具链")
    print(f"- DeerFlow：`{tc['deerflow']}`")
    print(f"- MediaCrawler：`{tc['mediacrawler']}`")
    print(f"- XHS-Downloader：`{tc['xhs_downloader']}`")

    rd = merged["readiness"]
    print(f"\n## 就绪状态")
    print(f"- 基础就绪：`{'✓' if rd['basic_ready'] else '✗'}`")
    print(f"- 深度就绪 (DeerFlow)：`{'✓' if rd['deep_ready'] else '✗'}`")
    print(f"- 社媒就绪 (MediaCrawler)：`{'✓' if rd['social_ready'] else '✗'}`")
    print(f"- 全部就绪：`{'✓' if rd['full_ready'] else '✗'}`")

    mcp_data = merged["mcp"]
    if mcp_data and mcp_data.get("servers"):
        print(f"\n## MCP 状态")
        for item in mcp_data["servers"]:
            print(f"- `{item['server_id']}`：`{item['status']}`")

    notes = merged["notes"]
    pa = merged.get("primary_action")
    if pa or notes:
        print(f"\n## 下一步")
        if pa:
            print(f"- **优先操作**：{pa}")
        for note in notes:
            print(f"- {note}")

    return 0


# ---------------------------------------------------------------------------
# SPCA pipeline command implementations
# ---------------------------------------------------------------------------

def cmd_init(task_card: dict, task_card_path: Path) -> int:
    paths = init_workspace(task_card, task_card_path)
    print(f"initialized: {paths['output_root']}")
    return 0


def cmd_collect(task_card: dict, task_card_path: Path) -> int:
    paths = init_workspace(task_card, task_card_path)
    if task_card.get("task_mode") == "guide":
        print("collect skipped: guide task does not collect platform sources")
        return 0

    channels = resolve_channels(task_card)
    raw_records = []
    for channel in channels:
        collector = COLLECTOR_MAP[channel]
        root = paths["manual_root"] if channel == "manual" else paths["imports_root"]
        raw_records.extend(collector(task_card["product_slug"], root))

    write_jsonl(paths["raw_root"] / "source-records.jsonl", raw_records)
    write_json(
        paths["raw_root"] / "source-registry.json",
        {
            "product_slug": task_card["product_slug"],
            "source_count": len(raw_records),
            "channels": channels,
            "backend_priority": {ch: CHANNEL_BACKEND_PRIORITY.get(ch, []) for ch in channels},
        },
    )
    export_platform_outputs(paths, raw_records, task_card)
    print(f"collected: {len(raw_records)} sources")
    return 0


def cmd_analyze(task_card: dict, task_card_path: Path) -> int:
    paths = init_workspace(task_card, task_card_path)
    source_records = read_jsonl(paths["raw_root"] / "source-records.jsonl")
    evidence_records, review_samples = normalize_sources(source_records)
    gaps = build_gap_list(evidence_records, review_samples)

    write_jsonl(paths["normalized_root"] / "evidence-records.jsonl", evidence_records)
    write_jsonl(paths["normalized_root"] / "review-samples.jsonl", review_samples)
    write_json(paths["normalized_root"] / "gap-list.json", {"gaps": gaps})

    product_overview = analyze_product_overview(evidence_records)
    user_analysis = analyze_user(review_samples, evidence_records)
    social_sentiment = analyze_sentiment(review_samples)
    seo_content = analyze_seo(evidence_records)
    monetization = analyze_monetization(evidence_records)
    competition = analyze_competition(
        user_analysis=user_analysis,
        sentiment_analysis=social_sentiment,
        seo_analysis=seo_content,
        monetization_analysis=monetization,
    )

    for name, data in [
        ("product-overview", product_overview),
        ("user-analysis", user_analysis),
        ("social-sentiment", social_sentiment),
        ("seo-content", seo_content),
        ("monetization", monetization),
        ("competition", competition),
    ]:
        write_json(paths["analysis_root"] / f"{name}.json", data)

    write_json(
        paths["analysis_root"] / "run-summary.json",
        {
            "product_slug": task_card["product_slug"],
            "source_count": len(source_records),
            "evidence_count": len(evidence_records),
            "review_sample_count": len(review_samples),
            "gaps": gaps,
        },
    )
    print(f"analyzed: {len(evidence_records)} evidence / {len(review_samples)} review samples")
    return 0


def cmd_export(task_card: dict, task_card_path: Path) -> int:
    paths = init_workspace(task_card, task_card_path)
    if task_card.get("task_mode") == "full":
        gate_ok, blockers = final_delivery_gate_status(paths)
        if not gate_ok:
            print("export blocked: 成稿门禁未通过，禁止导出正式报告")
            for blocker in blockers:
                print(f"- {blocker}")
            return 1

    if task_card.get("task_mode") == "full" and not review_gate_allows_export(paths):
        print("export blocked: REVIEW_GATE 未明确放行，禁止导出正式报告")
        return 1

    evidence_records = read_jsonl(paths["normalized_root"] / "evidence-records.jsonl")
    review_samples = read_jsonl(paths["normalized_root"] / "review-samples.jsonl")
    run_summary = read_json(paths["analysis_root"] / "run-summary.json")
    gaps = read_json(paths["normalized_root"] / "gap-list.json").get("gaps", [])

    analysis = {
        "source_count": run_summary["source_count"],
        "product_overview": read_json(paths["analysis_root"] / "product-overview.json"),
        "user_analysis": read_json(paths["analysis_root"] / "user-analysis.json"),
        "social_sentiment": read_json(paths["analysis_root"] / "social-sentiment.json"),
        "seo_content": read_json(paths["analysis_root"] / "seo-content.json"),
        "monetization": read_json(paths["analysis_root"] / "monetization.json"),
        "competition": read_json(paths["analysis_root"] / "competition.json"),
    }
    context = build_report_context(task_card, paths, evidence_records, review_samples, analysis, gaps)
    write_json(paths["exports_root"] / "report-context.json", context)

    summary_rows = [
        {"title": r["title"], "pool": r["evidence_pool"], "tier": r["tier"], "platform": r["platform"]}
        for r in evidence_records
    ]
    write_csv(paths["exports_root"] / "evidence-summary.csv", summary_rows)

    markdown = build_report_markdown(context, evidence_records, review_samples)
    write_text(paths["report_path"], markdown)
    write_text(paths["exports_root"] / "final-report.md", markdown)
    print(f"exported: {paths['report_path']}")
    return 0


def cmd_validate(task_card: dict, task_card_path: Path) -> int:
    paths = init_workspace(task_card, task_card_path)
    schema_root = Path(__file__).resolve().parents[2] / "schemas"
    result = validate_pipeline_outputs(paths, schema_root)
    write_json(paths["exports_root"] / "validation-result.json", result)
    if result["ok"]:
        print("validation: ok")
        return 0
    for error in result["errors"]:
        print(f"validation error: {error}")
    return 1


# ---------------------------------------------------------------------------
# Toolchain command implementations
# ---------------------------------------------------------------------------

def _run_deerflow(
    *,
    prompt: str,
    thread_id: str,
    model_name: str | None,
    subagent_enabled: bool,
    disable_thinking: bool,
    config_path: str | None,
    dry_run: bool,
) -> dict:
    SKILL_ROOT, _, command_preview_fn, extract_json_fn, resolve_fn = _lazy_runtime_ext()
    _, _, _, ensure_managed_fn, ensure_home_fn = _lazy_install()

    uv = shutil.which("uv") or "uv"
    deerflow_root = resolve_fn("deerflow")
    if deerflow_root is None:
        raise SystemExit("未检测到 DeerFlow。先运行：bash scripts/bootstrap.sh --with-stack --doctor")

    ensure_managed_fn(deerflow_root, dry_run=dry_run)
    resolved_config = Path(config_path) if config_path else deerflow_root / "config.research-toolkit.yaml"
    backend_root = deerflow_root / "backend"
    ensure_home_fn(deerflow_root, dry_run=dry_run)
    bridge_path = SKILL_ROOT / "scripts" / "rtk" / "bridges" / "deerflow_bridge.py"

    command = [
        uv, "run", "--project", str(backend_root),
        "python", str(bridge_path),
        "--prompt", prompt,
        "--thread-id", thread_id,
        "--config-path", str(resolved_config),
    ]
    if model_name:
        command.extend(["--model-name", model_name])
    if subagent_enabled:
        command.append("--subagent-enabled")
    if disable_thinking:
        command.append("--disable-thinking")

    if dry_run:
        return {"status": "dry_run", "command": command_preview_fn(command)}

    env = {**os.environ, "DEERFLOW_RUNTIME_HOME": str(deerflow_root)}
    proc = subprocess.run(command, capture_output=True, text=True, env=env, cwd=str(backend_root))
    result = extract_json_fn(proc.stdout) if proc.returncode == 0 else None
    return result or {
        "status": "error",
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:] if proc.stdout else "",
        "stderr_tail": proc.stderr[-2000:] if proc.stderr else "",
    }


def _run_social(
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
    dry_run: bool,
) -> dict:
    build_plan_fn, run_plan_fn = _lazy_social()
    plan = build_plan_fn(
        platform=platform,
        engine=engine,
        keywords=keywords.split(",") if keywords else None,
        url=url,
        output_root=output_root,
        login_type=login_type,
        headless=headless,
        get_comment=get_comment,
        get_sub_comment=get_sub_comment,
        save_data_option=save_data_option,
        cookie=cookie,
        proxy=proxy,
    )
    if dry_run:
        plan["status"] = "dry_run"
        return plan
    return run_plan_fn(plan)


def _run_social_auth(*, platform: str, open_qr: bool, json_mode: bool) -> dict:
    SKILL_ROOT, AUTH_ROOT, _, extract_json_fn, resolve_fn = _lazy_runtime_ext()
    mediacrawler_root = resolve_fn("mediacrawler")
    if mediacrawler_root is None:
        raise SystemExit("未检测到 MediaCrawler。先运行：bash scripts/bootstrap.sh --with-stack --doctor")

    auth_script = SKILL_ROOT / "scripts" / "rtk" / "bridges" / "mediacrawler_auth.py"
    uv = shutil.which("uv") or "uv"
    command = [
        uv, "run", "--project", str(mediacrawler_root),
        "python", str(auth_script),
        "--platform", platform,
        "--mediacrawler-root", str(mediacrawler_root),
        "--auth-root", str(AUTH_ROOT),
    ]
    if open_qr:
        command.append("--open-qr")

    proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
    result = extract_json_fn(proc.stdout)
    if result and result.get("status") == "login_success":
        marker = AUTH_ROOT / ".auth.ready"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("ok")
        result["text"] = "MediaCrawler 授权完成。"
        result["reply_words"] = "扫好了"
    elif result:
        result.setdefault("text", f"授权状态：{result.get('status', 'unknown')}")
        result["reply_words"] = "扫好了"
    else:
        result = {
            "status": "error",
            "text": "授权脚本未返回结果",
            "stdout_tail": proc.stdout[-2000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-2000:] if proc.stderr else "",
        }
    return result


def _run_extract_frames(args) -> int:
    script_path = Path(__file__).resolve().parents[1] / "extract_video_frames.py"
    cmd = [sys.executable, str(script_path), args.input_video, "--fps", str(args.fps)]
    if args.output_dir:
        cmd.extend(["--output-dir", args.output_dir])
    return subprocess.call(cmd)


# ---------------------------------------------------------------------------
# SPCA helper functions (unchanged)
# ---------------------------------------------------------------------------

def export_platform_outputs(paths: dict, raw_records: list[dict], task_card: dict) -> None:
    grouped_records: dict[str, list] = defaultdict(list)
    grouped_rows: dict[str, list] = defaultdict(list)
    for record in raw_records:
        rows_by_platform = flatten_record_rows(record)
        for platform, rows in rows_by_platform.items():
            grouped_records[platform].append(record)
            grouped_rows[platform].extend(rows)

    targets = ordered_platforms(requested_output_platforms(task_card) + list(grouped_rows.keys()))
    for platform in targets:
        rows = grouped_rows.get(platform, [])
        records = grouped_records.get(platform, [])
        platform_root = paths["platforms_root"] / platform
        if rows:
            write_csv(platform_root / "data.csv", rows)
        write_text(platform_root / "summary.md", build_platform_summary(platform, records, rows))


def build_platform_summary(platform: str, records: list[dict], rows: list[dict]) -> str:
    target = PLATFORM_SAMPLE_TARGETS.get(platform, 200)
    sample_count = len(rows)
    source_count = len({row["source_id"] for row in rows}) if rows else len(records)
    sample_titles = "；".join(row["title"] for row in rows[:5]) if rows else "待补充"
    tools = join_or_default(
        PLATFORM_BACKEND_PRIORITY.get(
            platform,
            CHANNEL_BACKEND_PRIORITY.get(channel_for_platform(platform), []),
        )
    )
    threshold_note = (
        f"当前样本量低于 {target}，需向用户确认是否接受当前样本量，或继续扩大搜索范围。"
        if sample_count < target
        else "当前样本量已达到默认阈值，但是否进入下一步仍需 AI 与用户共同核对。"
    )
    return f"""# {platform} 平台分析总结

## 1. 本轮任务概况

- 平台：`{platform}`
- 当前源文件数：`{source_count}`
- 推荐工具：`{tools}`
- 本轮抓取目标：`待补充`
- 实际使用工具：`待补充`
- 当前样本量：`{sample_count}`
- 目标数量：至少 `{target}` 条/篇
- 阈值判断：`{threshold_note}`

## 2. 样本与证据面

- 代表性样本：`{sample_titles}`
- 当前证据边界：`待补充`

## 3. 关键事实信号

- 当前明显信号：

## 4. 平台洞察与启发

- 初步洞察：
- 候选判断：

## 5. 风险、噪音与缺口

- 当前噪音与风险：
- 还缺什么：
- 建议补抓方向：

## 6. 需要用户确认 / 补充

- 是否接受当前样本量：
- 是否有误读需要纠正：
- 是否需要补充私有信息：
"""


def flatten_record_rows(record: dict) -> dict[str, list[dict]]:
    rows_by_platform: dict[str, list] = defaultdict(list)
    items = record.get("items") or []
    if items:
        for index, item in enumerate(items, start=1):
            platform = output_platform_name(
                item.get("platform") or record.get("metadata", {}).get("platform"),
                record["channel"],
            )
            rows_by_platform[platform].append(build_csv_row(record, item, index, platform))
        return rows_by_platform

    platform = output_platform_name(record.get("metadata", {}).get("platform"), record["channel"])
    rows_by_platform[platform].append(build_csv_row(record, {}, 1, platform))
    return rows_by_platform


def build_csv_row(record: dict, item: dict, index: int, platform: str) -> dict:
    metadata = record.get("metadata", {})
    text = item.get("text") or item.get("body") or item.get("content") or ""
    tags = item.get("tags") or metadata.get("tags") or []
    return {
        "id": f"{record['source_id']}-{index}",
        "source_id": record["source_id"],
        "source_channel": record["channel"],
        "title": item.get("title") or item.get("name") or record["title"],
        "url": item.get("url") or item.get("uri") or record.get("uri") or "",
        "local_path": record["local_path"],
        "tier": record["source_tier"],
        "platform": platform,
        "collected_at": record["collected_at"],
        "author": item.get("author") or metadata.get("author") or "",
        "publish_date": item.get("publish_date") or metadata.get("publish_date") or "",
        "likes": item.get("likes") or metadata.get("likes") or "",
        "comments": item.get("comments") or metadata.get("comments") or "",
        "shares": item.get("shares") or metadata.get("shares") or "",
        "keyword": item.get("keyword") or metadata.get("keyword") or "",
        "rating": item.get("rating") or metadata.get("rating") or "",
        "tags": stringify_list(tags),
        "text": compact_text(text),
    }


def compact_text(text: str) -> str:
    return " ".join(str(text).split())


def output_platform_name(value: Optional[str], channel: str) -> str:
    if value:
        normalized = slugify(value)
        if normalized:
            return normalized
    if channel == "social":
        raise ValueError("social channel records must include a concrete platform")
    return CHANNEL_PLATFORM_FALLBACKS.get(channel, channel)


def requested_output_platforms(task_card: dict) -> list[str]:
    platforms = task_card.get("platforms")
    if platforms:
        resolved = []
        for platform in platforms:
            normalized = slugify(platform)
            if normalized in CHANNEL_OUTPUT_PLATFORMS:
                for expanded in CHANNEL_OUTPUT_PLATFORMS[normalized]:
                    if expanded not in resolved:
                        resolved.append(expanded)
                continue
            concrete = output_platform_name(platform, channel_for_platform(platform))
            if concrete not in resolved:
                resolved.append(concrete)
        return resolved

    channels = task_card.get("channels") or []
    if channels:
        resolved = []
        for channel in channels:
            for p in CHANNEL_OUTPUT_PLATFORMS.get(channel, [CHANNEL_PLATFORM_FALLBACKS.get(channel, channel)]):
                if p not in resolved:
                    resolved.append(p)
        return resolved
    return []


def resolve_channels(task_card: dict) -> list[str]:
    requested = task_card.get("channels")
    if requested:
        return [ch for ch in requested if ch in COLLECTOR_MAP]
    requested_platforms = task_card.get("platforms") or []
    if not requested_platforms:
        return list(COLLECTOR_MAP.keys())
    resolved = []
    for p in requested_platforms:
        ch = channel_for_platform(p)
        if ch in COLLECTOR_MAP and ch not in resolved:
            resolved.append(ch)
    return resolved


def channel_for_platform(platform: str) -> str:
    return PLATFORM_TO_CHANNEL.get(slugify(platform), slugify(platform))


def ordered_platforms(values: list[str]) -> list[str]:
    selected = {p for p in values if p}
    if not selected:
        return []
    ordered = [p for p in PLATFORM_OUTPUT_ORDER if p in selected]
    for p in values:
        if p and p not in ordered:
            ordered.append(p)
    return ordered


def join_or_default(values: list[str]) -> str:
    filtered = [v for v in values if v]
    return "；".join(filtered) if filtered else "待补充"


def stringify_list(values) -> str:
    if isinstance(values, list):
        return "；".join(str(v) for v in values if str(v).strip())
    return str(values or "")


def review_gate_allows_export(paths: dict) -> bool:
    review_gate_path = paths["synthesis_root"] / "REVIEW_GATE.md"
    if not review_gate_path.exists():
        return False
    content = review_gate_path.read_text(encoding="utf-8")
    if "成稿放行" in content and ("成稿放行：`是`" in content or "成稿放行：是" in content):
        return True
    for line in content.splitlines():
        if "|" not in line:
            continue
        normalized = line.replace("`", "").replace(" ", "")
        if normalized.startswith("|轮次|") or normalized.startswith("|---|"):
            continue
        if normalized.endswith("|是|"):
            return True
    return False


def final_delivery_gate_status(paths: dict) -> tuple[bool, list[str]]:
    blockers = []
    rg = paths["synthesis_root"] / "REVIEW_GATE.md"
    rg_text = rg.read_text(encoding="utf-8") if rg.exists() else ""
    if "成稿放行：`是`" not in rg_text and "成稿放行：是" not in rg_text:
        blockers.append('`05-synthesis/REVIEW_GATE.md` 未标记\u201c成稿放行：是\u201d')

    exp = paths["experience_root"] / "EXPERIENCE_REPORT.md"
    if not exp.exists():
        blockers.append("缺 `04-experience/EXPERIENCE_REPORT.md`")
    elif not experience_report_has_required_sections(exp):
        blockers.append("`04-experience/EXPERIENCE_REPORT.md` 缺少必备章节")

    if not file_marks_ready(paths["writing_root"] / "WRITING_PLAN.md"):
        blockers.append("`06-writing/WRITING_PLAN.md` 仍有未完成状态")
    if not file_marks_ready(paths["factcheck_root"] / "FACTCHECK_PLAN.md"):
        blockers.append("`07-factcheck/FACTCHECK_PLAN.md` 仍有未完成状态")
    if not file_marks_ready(paths["visuals_root"] / "VISUAL_PLAN.md"):
        blockers.append("`08-visuals/VISUAL_PLAN.md` 仍有未完成状态")

    for name in ["round-1.md", "round-2.md", "round-3.md", "final-status.md"]:
        if not (paths["factcheck_root"] / name).exists():
            blockers.append(f"缺 `07-factcheck/{name}`")

    fs = paths["factcheck_root"] / "final-status.md"
    if fs.exists():
        fst = fs.read_text(encoding="utf-8")
        if "成稿放行：`是`" not in fst and "成稿放行：是" not in fst:
            blockers.append('`07-factcheck/final-status.md` 未标记\u201c成稿放行：是\u201d')
    else:
        blockers.append("缺 `07-factcheck/final-status.md`")

    return (not blockers, blockers)


def file_marks_ready(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    if "`todo`" in text or " todo " in lowered:
        return False
    if "`doing`" in text or " doing " in lowered:
        return False
    if "`no`" in text:
        return False
    for marker in ["待补", "待继续", "待完善", "仍需", "未完成", "未完整"]:
        if marker in text:
            return False
    return True


def experience_report_has_required_sections(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    required = [
        "## 1. 当前素材状态",
        "## 2. 产品架构判断",
        "## 3. 功能矩阵",
        "## 4. 重点功能路径",
        "## 5. 好的洞察与不好的洞察",
        "## 6. 进入正文的可复用判断",
        "## 7. 待补素材清单",
        "## 8. 截图 -> 章节 -> 判断",
    ]
    return all(s in text for s in required)
