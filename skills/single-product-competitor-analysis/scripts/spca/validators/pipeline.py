from pathlib import Path
from typing import Optional

from spca.config import (
    CHANNEL_OUTPUT_PLATFORMS,
    CHANNEL_PLATFORM_FALLBACKS,
    PLATFORM_OUTPUT_ORDER,
    PLATFORM_TO_CHANNEL,
    REQUIRED_REPORT_HEADINGS,
)
from spca.utils import read_json, read_jsonl, read_text, slugify


def validate_schema_payload(schema_path: Path, payload) -> list[str]:
    from jsonschema import Draft202012Validator

    schema = read_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(payload), key=str):
        errors.append(error.message)
    return errors


def validate_pipeline_outputs(paths: dict, schema_root: Path) -> dict:
    errors = []

    task_card_path = paths["task_card"]
    report_context_path = paths["exports_root"] / "report-context.json"
    report_path = paths["report_path"]
    task_card = None

    if task_card_path.exists():
        task_card = read_json(task_card_path)
        errors.extend(
            validate_schema_payload(schema_root / "task-card.schema.json", task_card)
        )
    else:
        errors.append("缺 task-card.json")

    if report_context_path.exists():
        errors.extend(
            validate_schema_payload(
                schema_root / "report-context.schema.json",
                read_json(report_context_path),
            )
        )
    else:
        errors.append("缺 report-context.json")

    source_records_path = paths["raw_root"] / "source-records.jsonl"
    if source_records_path.exists():
        source_records = read_jsonl(source_records_path)
        if not source_records:
            errors.append("source-records.jsonl 为空")
        for index, payload in enumerate(source_records, start=1):
            record_errors = validate_schema_payload(schema_root / "source-record.schema.json", payload)
            errors.extend(f"source[{index}] {message}" for message in record_errors)
        for platform in expected_platform_outputs(task_card, source_records):
            platform_root = paths["platforms_root"] / platform
            summary_path = platform_root / "summary.md"
            data_path = platform_root / "data.csv"
            if not summary_path.exists():
                errors.append(f"平台产物缺失：{platform}/summary.md")
            if not data_path.exists():
                errors.append(f"平台产物缺失：{platform}/data.csv")
            else:
                csv_text = read_text(data_path).strip()
                if not csv_text:
                    errors.append(f"平台产物为空：{platform}/data.csv")
                elif len(csv_text.splitlines()) <= 1:
                    errors.append(f"平台产物只有表头：{platform}/data.csv")
    elif task_card and task_card.get("task_mode", "full") in {"full", "crawl"}:
        errors.append("缺 source-records.jsonl")

    if task_card and task_card.get("task_mode", "full") in {"full", "guide"}:
        experience_report_path = resolve_task_file(paths, "experience_root", report_path.parent.parent / "04-experience") / "EXPERIENCE_REPORT.md"
        if not experience_report_path.exists():
            errors.append("缺 `04-experience/EXPERIENCE_REPORT.md`")

    if task_card and task_card.get("task_mode", "full") == "full":
        writing_plan_path = resolve_task_file(paths, "writing_root", report_path.parent) / "WRITING_PLAN.md"
        factcheck_root = resolve_task_file(paths, "factcheck_root", report_path.parent.parent / "07-factcheck")
        visuals_root = resolve_task_file(paths, "visuals_root", report_path.parent.parent / "08-visuals")

        if not writing_plan_path.exists():
            errors.append("缺 `06-writing/WRITING_PLAN.md`")
        if not (factcheck_root / "FACTCHECK_PLAN.md").exists():
            errors.append("缺 `07-factcheck/FACTCHECK_PLAN.md`")
        if not (visuals_root / "VISUAL_PLAN.md").exists():
            errors.append("缺 `08-visuals/VISUAL_PLAN.md`")
        for name in ["round-1.md", "round-2.md", "round-3.md", "final-status.md"]:
            if not (factcheck_root / name).exists():
                errors.append(f"缺 `07-factcheck/{name}`")

    evidence_records_path = paths["normalized_root"] / "evidence-records.jsonl"
    if evidence_records_path.exists():
        evidence_records = read_jsonl(evidence_records_path)
        for index, payload in enumerate(evidence_records, start=1):
            record_errors = validate_schema_payload(schema_root / "evidence-record.schema.json", payload)
            errors.extend(f"evidence[{index}] {message}" for message in record_errors)

    review_samples_path = paths["normalized_root"] / "review-samples.jsonl"
    if review_samples_path.exists():
        review_samples = read_jsonl(review_samples_path)
        for index, payload in enumerate(review_samples, start=1):
            record_errors = validate_schema_payload(schema_root / "review-sample.schema.json", payload)
            errors.extend(f"review[{index}] {message}" for message in record_errors)

    if not report_path.exists():
        errors.append(f"缺主报告：{report_path}")
    else:
        report_text = read_text(report_path)
        for heading in REQUIRED_REPORT_HEADINGS:
            if heading not in report_text:
                errors.append(f"报告缺少章节：{heading}")

    return {"ok": not errors, "errors": errors}


def resolve_task_file(paths: dict, key: str, default: Path) -> Path:
    value = paths.get(key)
    if value:
        return Path(value)
    return default


def expected_platform_outputs(task_card: Optional[dict], source_records: list[dict]) -> list[str]:
    if task_card:
        task_mode = task_card.get("task_mode", "full")
        if task_mode == "full":
            requested = requested_platforms(task_card)
            return requested or [platform for platform in PLATFORM_OUTPUT_ORDER if platform != "manual"]
        if task_mode == "crawl":
            requested = requested_platforms(task_card)
            return requested or [platform for platform in PLATFORM_OUTPUT_ORDER if platform not in {"manual"}]
    return expected_platform_outputs_from_sources(source_records)


def requested_platforms(task_card: dict) -> list[str]:
    platforms = []
    for raw in task_card.get("platforms") or []:
        normalized = slugify(raw)
        if normalized in CHANNEL_OUTPUT_PLATFORMS:
            for platform in CHANNEL_OUTPUT_PLATFORMS[normalized]:
                add_platform(platforms, platform)
            continue
        add_platform(platforms, output_platform_name(raw, PLATFORM_TO_CHANNEL.get(normalized, normalized)))

    if platforms:
        return platforms

    for channel in task_card.get("channels") or []:
        normalized = slugify(channel)
        for platform in CHANNEL_OUTPUT_PLATFORMS.get(normalized, [CHANNEL_PLATFORM_FALLBACKS.get(normalized, normalized)]):
            add_platform(platforms, platform)
    return platforms


def expected_platform_outputs_from_sources(source_records: list[dict]) -> list[str]:
    platforms = []
    for source in source_records:
        items = source.get("items") or []
        if items:
            for item in items:
                add_platform(
                    platforms,
                    output_platform_name(item.get("platform") or source.get("metadata", {}).get("platform"), source["channel"]),
                )
            continue
        add_platform(
            platforms,
            output_platform_name(source.get("metadata", {}).get("platform"), source["channel"]),
        )
    return platforms


def add_platform(platforms: list[str], platform: str) -> None:
    if platform and platform not in platforms:
        platforms.append(platform)


def output_platform_name(value: Optional[str], channel: str) -> str:
    if value:
        normalized = slugify(value)
        if normalized:
            return normalized
    if channel == "social":
        raise ValueError("social channel records must include a concrete platform")
    return CHANNEL_PLATFORM_FALLBACKS.get(channel, channel)
