from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .doctor import build_doctor_payload, render_doctor_text
from .install import ensure_deerflow_managed_files, ensure_deerflow_runtime_home
from .project_init import DIRECTORIES, init_project
from .runtime import command_preview, extract_json_object, now_iso, resolve_component_path, write_json, write_text
from .bridges.social_bridge import build_social_auth_plan, build_social_plan, run_social_plan


def default_output_root(slug: str) -> Path:
    return Path.cwd() / "outputs" / slug


def normalize_slug(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", lowered).strip("-")
    return cleaned or "research-run"


def derive_social_keywords(topic: str, explicit_keywords: str | None) -> list[str]:
    if explicit_keywords:
        return [item.strip() for item in explicit_keywords.split(",") if item.strip()]
    candidates = [
        topic,
        f"{topic} 测评",
        f"{topic} 体验",
        f"{topic} 教程",
        f"{topic} 推荐",
        f"{topic} 避雷",
    ]
    seen: set[str] = set()
    keywords: list[str] = []
    for item in candidates:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        keywords.append(normalized)
    return keywords


def build_research_card(topic: str, explicit_keywords: str | None) -> dict:
    keywords = derive_social_keywords(topic, explicit_keywords)
    return {
        "topic": topic,
        "primary_question": f"围绕"{topic}"完成深度研究与社媒证据采集。",
        "keywords": keywords,
        "keywords_csv": ",".join(keywords),
        "social_strategy": "keywords-first",
        "comment_depth": "posts_comments_subcomments",
    }


def run_research(
    *,
    topic: str,
    slug: str | None,
    title: str | None,
    output_root: str | None,
    platform: str,
    keywords: str | None,
    url: str | None,
    skip_deep: bool,
    skip_social: bool,
    overwrite: bool,
    dry_run: bool,
) -> dict:
    resolved_slug = normalize_slug(slug or topic)
    resolved_title = title or topic
    resolved_output_root = Path(output_root) if output_root else default_output_root(resolved_slug)
    doctor_payload = build_doctor_payload()
    api_smoke = run_api_smoke(dry_run=dry_run)
    research_card = build_research_card(topic, keywords)

    payload = {
        "slug": resolved_slug,
        "title": resolved_title,
        "topic": topic,
        "research_card": research_card,
        "output_root": str(resolved_output_root),
        "generated_at": now_iso(),
        "steps": {
            "doctor": doctor_payload,
            "api_smoke": api_smoke,
            "project_init": build_project_step(
                slug=resolved_slug,
                title=resolved_title,
                output_root=resolved_output_root,
                overwrite=overwrite,
                dry_run=dry_run,
            ),
            "deep_step": build_deep_step(
                topic=topic,
                output_root=resolved_output_root,
                skip_deep=skip_deep,
                deep_ready=doctor_payload["deep_ready"],
                dry_run=dry_run,
            ),
            "social_step": build_social_step(
                topic=topic,
                platform=platform,
                keywords=research_card["keywords_csv"],
                url=None,
                output_root=resolved_output_root,
                skip_social=skip_social,
                social_ready=doctor_payload["connectors"]["mediacrawler_keyword_ready"],
                mediacrawler_installed=doctor_payload["connectors"]["resolved_mediacrawler_root"] is not None,
                dry_run=dry_run,
            ),
        },
        "text": "Research dry-run prepared" if dry_run else "Research orchestration finished",
    }

    if dry_run:
        return payload

    prepare_output_root(
        slug=resolved_slug,
        title=resolved_title,
        output_root=resolved_output_root,
        overwrite=overwrite,
    )

    write_text(resolved_output_root / ".meta" / "doctor-report.md", render_doctor_text(doctor_payload))
    write_json(resolved_output_root / ".meta" / "api-smoke.json", api_smoke)
    write_json(resolved_output_root / "analysis" / "research-plan.json", payload)

    deep_step = materialize_deep_step(payload["steps"]["deep_step"])
    social_step = materialize_social_step(payload["steps"]["social_step"])
    payload["steps"]["deep_step"] = deep_step
    payload["steps"]["social_step"] = social_step

    write_json(resolved_output_root / ".meta" / "orchestrator-run.json", payload)
    write_text(resolved_output_root / "drafts" / "10-research-summary.md", render_summary(payload))
    return payload


def prepare_output_root(*, slug: str, title: str, output_root: Path, overwrite: bool) -> None:
    manifest_path = output_root / "manifest.json"
    if manifest_path.exists():
        for directory in DIRECTORIES:
            (output_root / directory).mkdir(parents=True, exist_ok=True)
        return
    init_project(slug=slug, title=title, output_root=output_root, overwrite=overwrite)


def build_project_step(*, slug: str, title: str, output_root: Path, overwrite: bool, dry_run: bool) -> dict:
    return {
        "status": "planned" if dry_run else "pending",
        "slug": slug,
        "title": title,
        "output_root": str(output_root),
        "manifest_path": str(output_root / "manifest.json"),
        "overwrite": overwrite,
    }


def build_deep_step(*, topic: str, output_root: Path, skip_deep: bool, deep_ready: bool, dry_run: bool) -> dict:
    if skip_deep:
        return {"status": "skipped", "reason": "skip_deep"}
    deerflow_root = resolve_component_path("deerflow")
    if deerflow_root is None or not deep_ready:
        return {"status": "blocked", "reason": "deep_not_ready"}

    managed_files = ensure_deerflow_managed_files(deerflow_root, dry_run=dry_run)
    backend_root = deerflow_root / "backend"
    deerflow_runtime_home = ensure_deerflow_runtime_home(deerflow_root, dry_run=dry_run)
    config_path = deerflow_root / "config.local-research-system.yaml"
    bridge_path = Path(__file__).resolve().parent / "bridges" / "deerflow_bridge.py"
    command = [
        "uv",
        "run",
        "--project",
        str(backend_root),
        "python",
        str(bridge_path),
        "--prompt",
        topic,
        "--config-path",
        str(config_path),
        "--thread-id",
        f"research-{normalize_slug(topic)}",
    ]
    return {
        "status": "planned" if dry_run else "pending",
        "engine": "deerflow",
        "resolved_paths": {
            "deerflow_root": str(deerflow_root),
            "backend_root": str(backend_root),
            "config_path": str(config_path),
            "deer_flow_home": str(deerflow_runtime_home),
        },
        "managed_files": managed_files,
        "command_preview": command_preview(command, backend_root),
        "command": command,
        "runtime_env": {
            "DEER_FLOW_HOME": str(deerflow_runtime_home),
            "DEER_FLOW_HOST_BASE_DIR": str(deerflow_runtime_home),
        },
        "response_path": str(output_root / "analysis" / "deerflow-response.json"),
    }


def materialize_deep_step(step: dict) -> dict:
    if step["status"] != "pending":
        return step
    command = step.pop("command")
    runtime_env = step.get("runtime_env", {})
    env = os.environ.copy()
    env.update(runtime_env)
    result = subprocess.run(command, cwd=step["resolved_paths"]["backend_root"], capture_output=True, text=True, check=False, env=env)
    step["stdout"] = result.stdout
    step["stderr"] = result.stderr
    step["returncode"] = result.returncode
    if result.returncode != 0:
        step["status"] = "error"
        return step
    bridge_payload = extract_json_object(result.stdout)
    step["status"] = "completed"
    step["bridge_result"] = bridge_payload
    write_json(Path(step["response_path"]), bridge_payload)
    return step


def build_social_step(
    *,
    topic: str,
    platform: str,
    keywords: str | None,
    url: str | None,
    output_root: Path,
    skip_social: bool,
    social_ready: bool,
    mediacrawler_installed: bool,
    dry_run: bool,
) -> dict:
    if skip_social:
        return {"status": "skipped", "reason": "skip_social"}
    if not social_ready:
        if mediacrawler_installed:
            auth_plan = build_social_auth_plan(platform=platform, open_qr=True)
            return {
                "status": "auth_required",
                "reason": "mediacrawler_auth_missing",
                "auth_plan": auth_plan,
                "next_action": "现在只差小红书登录态。先运行 /本地调研授权，给用户二维码；扫码后让用户只回复：扫好了。",
                "reply_when_done": "扫好了",
            }
        return {
            "status": "blocked",
            "reason": "social_not_ready",
            "next_action": "先只做这一步：bash scripts/bootstrap.sh --with-stack --doctor",
            "reply_when_done": "跑好了",
        }

    try:
        plan = build_social_plan(
            platform=platform,
            engine="auto",
            keywords=keywords,
            url=url,
            output_root=str(output_root / "evidence" / "social"),
            login_type="qrcode",
            headless=False,
            get_comment=True,
            get_sub_comment=True,
            save_data_option="jsonl",
            cookie=None,
            proxy=None,
        )
    except RuntimeError as exc:
        return {"status": "blocked", "reason": str(exc)}

    preview_payload = run_social_plan(plan, dry_run=True)
    preview_payload["status"] = "planned" if dry_run else "pending"
    preview_payload["topic"] = topic
    preview_payload["plan"] = serialize_social_plan(plan)
    return preview_payload


def materialize_social_step(step: dict) -> dict:
    if step["status"] != "pending":
        return step
    plan = deserialize_social_plan(step.pop("plan"))
    result = run_social_plan(plan, dry_run=False)
    result["status"] = "completed"
    return result


def serialize_social_plan(plan: dict) -> dict:
    return {
        "engine": plan["engine"],
        "mode": plan["mode"],
        "cwd": str(plan["cwd"]),
        "command": plan["command"],
        "output_root": str(plan["output_root"]),
        "resolved_paths": plan["resolved_paths"],
    }


def deserialize_social_plan(plan: dict) -> dict:
    return {
        "engine": plan["engine"],
        "mode": plan["mode"],
        "cwd": Path(plan["cwd"]),
        "command": plan["command"],
        "output_root": Path(plan["output_root"]),
        "resolved_paths": plan["resolved_paths"],
    }


def render_summary(payload: dict) -> str:
    lines = [
        f"# {payload['title']}",
        "",
        f"- 主题: `{payload['topic']}`",
        f"- 项目标识: `{payload['slug']}`",
        f"- 输出目录: `{payload['output_root']}`",
        f"- 关键词: `{payload['research_card']['keywords_csv']}`",
        "",
        "## 编排结果",
    ]
    for name, step in payload["steps"].items():
        status = step.get("status", "recorded")
        lines.append(f"- `{name}`: {status}")
    lines.append("")
    lines.append("## 原始产物")
    lines.append("- `.meta/orchestrator-run.json`")
    lines.append("- `.meta/api-smoke.json`")
    lines.append("- `analysis/research-plan.json`")
    if payload["steps"]["deep_step"].get("status") == "completed":
        lines.append("- `analysis/deerflow-response.json`")
    return "\n".join(lines) + "\n"


def run_api_smoke(*, dry_run: bool) -> dict:
    providers = {
        "ark": {
            "env": "ARK_API_KEY",
            "url": "https://ark.cn-beijing.volces.com/api/v3/models",
            "kind": "openai-compatible",
        },
        "tavily": {
            "env": "TAVILY_API_KEY",
            "url": "https://api.tavily.com/search",
            "kind": "search",
        },
    }
    optional_providers = {
        "infoquest": {
            "env": "INFOQUEST_API_KEY",
            "kind": "reserved",
            "note": "InfoQuest 已保留到本地环境，但当前默认搜索链路仍走 Tavily。",
        },
        "openai": {
            "env": "OPENAI_API_KEY",
            "url": "https://api.openai.com/v1/models",
            "kind": "openai-compatible",
        },
        "deepseek": {
            "env": "DEEPSEEK_API_KEY",
            "url": "https://api.deepseek.com/v1/models",
            "kind": "openai-compatible",
        },
        "serpapi": {
            "env": "SERPAPI_API_KEY",
            "url": "https://serpapi.com/search.json",
            "kind": "search",
        },
    }
    results: dict[str, dict] = {}
    for name, config in providers.items():
        results[name] = _probe_provider(config, dry_run=dry_run)
    for name, config in optional_providers.items():
        if not os.environ.get(config["env"], "").strip():
            continue
        if config["kind"] == "reserved":
            results[name] = {
                "env": config["env"],
                "configured": True,
                "status": "reserved",
                "note": config["note"],
            }
            continue
        results[name] = _probe_provider(config, dry_run=dry_run)
    return {"dry_run": dry_run, "providers": results}


def _probe_provider(config: dict, *, dry_run: bool) -> dict:
    token = os.environ.get(config["env"], "")
    base = {
        "env": config["env"],
        "configured": bool(token),
        "url": config["url"],
    }
    if not token:
        base["status"] = "missing"
        return base
    if dry_run:
        base["status"] = "planned"
        return base
    try:
        if config["kind"] == "openai-compatible":
            request = urllib.request.Request(
                config["url"],
                headers={"Authorization": f"Bearer {token}"},
                method="GET",
            )
        elif config["env"] == "TAVILY_API_KEY":
            data = json.dumps({"api_key": token, "query": "health check", "max_results": 1}).encode("utf-8")
            request = urllib.request.Request(
                config["url"],
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        else:
            query = urllib.parse.urlencode({"engine": "google", "q": "health check", "api_key": token})
            request = urllib.request.Request(f"{config['url']}?{query}", method="GET")

        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read(200).decode("utf-8", errors="replace")
            base["status"] = "ok"
            base["http_status"] = response.status
            base["body_preview"] = body
            return base
    except urllib.error.HTTPError as exc:
        base["status"] = "error"
        base["http_status"] = exc.code
        base["body_preview"] = exc.read(200).decode("utf-8", errors="replace")
        return base
    except Exception as exc:
        base["status"] = "error"
        base["error"] = str(exc)
        return base
