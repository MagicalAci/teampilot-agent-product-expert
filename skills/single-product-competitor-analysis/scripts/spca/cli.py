import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

from spca.analyzers import (
    analyze_competition,
    analyze_monetization,
    analyze_product_overview,
    analyze_seo,
    analyze_sentiment,
    analyze_user,
)
from spca.collectors import COLLECTOR_MAP
from spca.config import (
    CHANNEL_BACKEND_PRIORITY,
    CHANNEL_OUTPUT_PLATFORMS,
    CHANNEL_PLATFORM_FALLBACKS,
    PLATFORM_BACKEND_PRIORITY,
    PLATFORM_OUTPUT_ORDER,
    PLATFORM_SAMPLE_TARGETS,
    PLATFORM_TO_CHANNEL,
)
from spca.doctor import collect_doctor_status
from spca.exporters import build_report_context, build_report_markdown
from spca.normalizers import build_gap_list, normalize_sources
from spca.runtime import init_workspace, load_task_card, resolve_paths
from spca.utils import read_json, read_jsonl, slugify, write_csv, write_json, write_jsonl, write_text
from spca.validators import validate_pipeline_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="SPCA structured pipeline")
    parser.add_argument("command", choices=["init", "collect", "analyze", "export", "validate", "doctor"])
    parser.add_argument("--task-card", dest="task_card")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.command == "doctor":
        return cmd_doctor(json_output=args.json_output)
    if not args.task_card:
        parser.error("--task-card is required unless command is doctor")

    task_card_path = Path(args.task_card).resolve()
    task_card = load_task_card(task_card_path)

    handlers = {
        "init": cmd_init,
        "collect": cmd_collect,
        "analyze": cmd_analyze,
        "export": cmd_export,
        "validate": cmd_validate,
    }
    return handlers[args.command](task_card, task_card_path)


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
            "backend_priority": {channel: CHANNEL_BACKEND_PRIORITY.get(channel, []) for channel in channels},
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

    write_json(paths["analysis_root"] / "product-overview.json", product_overview)
    write_json(paths["analysis_root"] / "user-analysis.json", user_analysis)
    write_json(paths["analysis_root"] / "social-sentiment.json", social_sentiment)
    write_json(paths["analysis_root"] / "seo-content.json", seo_content)
    write_json(paths["analysis_root"] / "monetization.json", monetization)
    write_json(paths["analysis_root"] / "competition.json", competition)

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
        {
            "title": record["title"],
            "pool": record["evidence_pool"],
            "tier": record["tier"],
            "platform": record["platform"],
        }
        for record in evidence_records
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


def cmd_doctor(*, json_output: bool) -> int:
    status = collect_doctor_status()
    if json_output:
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0

    managed_runtime = status["managed_runtime"]
    ffmpeg = status["ffmpeg"]
    print("# SPCA Doctor")
    print("")
    print(f"- 受管运行时目录：`{managed_runtime['root']}`")
    print(f"- venv 是否存在：`{'是' if managed_runtime['venv_exists'] else '否'}`")
    print(f"- ffmpeg 是否可用：`{'是' if ffmpeg['available'] else '否'}`")
    print(f"- MCP 阻断项：`{', '.join(status['mcp']['blocking']) or '无'}`")
    print("")
    print("## MCP 状态")
    for item in status["mcp"]["servers"]:
        print(f"- `{item['server_id']}`：`{item['status']}`")
    if status["notes"]:
        print("")
        print("## 提示")
        for note in status["notes"]:
            print(f"- {note}")
    return 0


def export_platform_outputs(paths: dict, raw_records: list[dict], task_card: dict) -> None:
    grouped_records = defaultdict(list)
    grouped_rows = defaultdict(list)
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
- 是否做过安装 / 初始化 / 登录：`待补充`
- 是否发生降级：`待补充`
- 当前样本量：`{sample_count}`
- 目标数量：至少 `{target}` 条/篇
- 阈值判断：`{threshold_note}`

## 2. 样本与证据面

- 本轮抓取范围：`待补充`
- 代表性样本：`{sample_titles}`
- 当前证据边界：`待补充`

## 3. 关键事实信号

- 当前明显信号：

## 4. 平台洞察与启发

- 基于本平台证据的初步洞察：
- 候选判断：
- 对后续分析最有帮助的启发：

## 5. 风险、噪音与缺口

- 当前噪音与风险：
- 还缺什么：
- 建议补抓方向：

## 6. 需要用户确认 / 补充

- 是否接受当前样本量：
- 是否有误读需要纠正：
- 是否需要补充私有信息 / 登录后页面 / 录屏截图：
- 是否需要优先深挖某类用户 / 某个问题：

## 边界提醒

- 可以写：基于本平台证据提炼出的平台洞察、候选判断、策划启发
- 不要写：替代全局正式报告的最终结论、跨章节总判断、最终 `跟 / 避 / 绕 / 观察`
"""


def flatten_record_rows(record: dict) -> dict[str, list[dict]]:
    rows_by_platform = defaultdict(list)
    items = record.get("items") or []
    if items:
        for index, item in enumerate(items, start=1):
            platform = output_platform_name(item.get("platform") or record.get("metadata", {}).get("platform"), record["channel"])
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
            for platform in CHANNEL_OUTPUT_PLATFORMS.get(channel, [CHANNEL_PLATFORM_FALLBACKS.get(channel, channel)]):
                if platform not in resolved:
                    resolved.append(platform)
        return resolved
    return []


def resolve_channels(task_card: dict) -> list[str]:
    requested_channels = task_card.get("channels")
    if requested_channels:
        return [channel for channel in requested_channels if channel in COLLECTOR_MAP]

    requested_platforms = task_card.get("platforms") or []
    if not requested_platforms:
        return list(COLLECTOR_MAP.keys())

    resolved = []
    for platform in requested_platforms:
        channel = channel_for_platform(platform)
        if channel in COLLECTOR_MAP and channel not in resolved:
            resolved.append(channel)
    return resolved


def channel_for_platform(platform: str) -> str:
    normalized = slugify(platform)
    return PLATFORM_TO_CHANNEL.get(normalized, normalized)


def ordered_platforms(values: list[str]) -> list[str]:
    selected = {platform for platform in values if platform}
    if not selected:
        return []

    ordered = [platform for platform in PLATFORM_OUTPUT_ORDER if platform in selected]
    unknown = [platform for platform in values if platform not in PLATFORM_OUTPUT_ORDER and platform]
    for platform in unknown:
        if platform not in ordered:
            ordered.append(platform)
    return ordered


def join_or_default(values: list[str]) -> str:
    filtered = [value for value in values if value]
    return "；".join(filtered) if filtered else "待补充"


def stringify_list(values) -> str:
    if isinstance(values, list):
        return "；".join(str(value) for value in values if str(value).strip())
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

    review_gate_path = paths["synthesis_root"] / "REVIEW_GATE.md"
    review_gate_text = review_gate_path.read_text(encoding="utf-8") if review_gate_path.exists() else ""
    if "成稿放行：`是`" not in review_gate_text and "成稿放行：是" not in review_gate_text:
        blockers.append("`05-synthesis/REVIEW_GATE.md` 未明确标记“成稿放行：是”")

    experience_report_path = paths["experience_root"] / "EXPERIENCE_REPORT.md"
    if not experience_report_path.exists():
        blockers.append("缺 `04-experience/EXPERIENCE_REPORT.md`")
    elif not experience_report_has_required_sections(experience_report_path):
        blockers.append("`04-experience/EXPERIENCE_REPORT.md` 缺少必备章节")

    writing_plan_path = paths["writing_root"] / "WRITING_PLAN.md"
    if not file_marks_ready(writing_plan_path):
        blockers.append("`06-writing/WRITING_PLAN.md` 仍有未完成状态")

    factcheck_plan_path = paths["factcheck_root"] / "FACTCHECK_PLAN.md"
    if not file_marks_ready(factcheck_plan_path):
        blockers.append("`07-factcheck/FACTCHECK_PLAN.md` 仍有未完成状态")

    visual_plan_path = paths["visuals_root"] / "VISUAL_PLAN.md"
    if not file_marks_ready(visual_plan_path):
        blockers.append("`08-visuals/VISUAL_PLAN.md` 仍有未完成状态")

    for required_name in ["round-1.md", "round-2.md", "round-3.md", "final-status.md"]:
        file_path = paths["factcheck_root"] / required_name
        if not file_path.exists():
            blockers.append(f"缺 `07-factcheck/{required_name}`")

    final_status_path = paths["factcheck_root"] / "final-status.md"
    if final_status_path.exists():
        final_status_text = final_status_path.read_text(encoding="utf-8")
        if "成稿放行：`是`" not in final_status_text and "成稿放行：是" not in final_status_text:
            blockers.append("`07-factcheck/final-status.md` 未明确标记“成稿放行：是”")
    else:
        blockers.append("缺 `07-factcheck/final-status.md`")

    return (not blockers, blockers)


def file_marks_ready(path: Path) -> bool:
    if not path.exists():
        return False

    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    pending_markers = [
        "待补",
        "待继续",
        "待完善",
        "仍需",
        "未完成",
        "未完整",
    ]
    if "`todo`" in text or " todo " in lowered:
        return False
    if "`doing`" in text or " doing " in lowered:
        return False
    if "`no`" in text:
        return False
    if any(marker in text for marker in pending_markers):
        return False
    return True


def experience_report_has_required_sections(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    required_sections = [
        "## 1. 当前素材状态",
        "## 2. 产品架构判断",
        "## 3. 功能矩阵",
        "## 4. 重点功能路径",
        "## 5. 好的洞察与不好的洞察",
        "## 6. 进入正文的可复用判断",
        "## 7. 待补素材清单",
        "## 8. 截图 -> 章节 -> 判断",
    ]
    return all(section in text for section in required_sections)
