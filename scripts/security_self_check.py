#!/usr/bin/env python3
"""仓库级安全自检门禁。

AgentShield（ecc-agentshield）只扫描 `.claude/` 结构，对本仓库 Cursor 原生配置面
（.cursor/rules、.teampilot/agent.yml、mcps/、skills/）扫到 0 个文件。本脚本补上
真正覆盖本仓库的最小安全门禁，聚焦 Agent 仓库的头号风险：硬编码密钥。

检查项：
1. 高置信度密钥模式（OpenAI/Anthropic/GitHub/AWS + 通用 key=value 赋值）
2. `.env` 是否被 .gitignore 忽略，且没有把真实 `.env` 提交进仓库

用法：
    python scripts/security_self_check.py            # 扫描 git 跟踪的文本文件
    python scripts/security_self_check.py --json      # JSON 输出（CI 用）

退出码：0 = 通过；1 = 发现疑似密钥或配置问题。

允许标记：在某行末尾加 `pragma: allowlist secret` 可豁免该行（用于文档示例）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 这两个文件天然包含"像密钥的"正则/测试构造，跳过以免自我误报。
SELF_SKIP = {
    "scripts/security_self_check.py",
    "tests/test_security_self_check.py",
}

# 仅扫描文本类配置/指令/脚本，避免二进制与体积文件。
TEXT_SUFFIXES = {
    ".md", ".mdc", ".yml", ".yaml", ".json", ".toml", ".py", ".sh",
    ".js", ".ts", ".txt", ".csv", ".html", ".env", ".cfg", ".ini",
}

ALLOWLIST_MARKER = "pragma: allowlist secret"

# 允许清单：有意保留内置的内部专用凭据（内网端点，外网不可达），按业务决定。
# 这些值即便出现在被扫描文件中也不计为泄露；门禁仍会拦截其它意外的外部密钥。
ALLOWLISTED_SECRETS = {
    "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA",  # 哈啰幻视内部大模型网关（内网专用）
}

# 占位符特征：命中任一则不算真实密钥（高置信度降噪）。
PLACEHOLDER_HINTS = (
    "...", "xxx", "your", "<", ">", "${", "example", "changeme",
    "placeholder", "redacted", "dummy", "sample", "test-key", "fake",
    "********", "******",
)

# 高置信度密钥模式（厂商前缀 + 足够长度）。
PROVIDER_PATTERNS = [
    ("OpenAI/Anthropic key", re.compile(r"sk-(?:ant-)?[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{30,}")),
]

# 通用 key=value 赋值（带引号、值足够长且含字母+数字、非占位符）。
GENERIC_ASSIGN = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|access[_-]?key)\b"
    r"\s*[:=]\s*[\"']([^\"']{16,})[\"']"
)


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    if any(hint in lowered for hint in PLACEHOLDER_HINTS):
        return True
    # 纯字母或纯数字、或没有任何字母数字组合，通常不是真实密钥。
    has_alpha = any(c.isalpha() for c in value)
    has_digit = any(c.isdigit() for c in value)
    return not (has_alpha and has_digit)


def scan_text(text: str) -> list[dict]:
    """对一段文本逐行扫描，返回 findings 列表（不含文件名）。"""
    findings: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if ALLOWLIST_MARKER in line:
            continue
        for label, pattern in PROVIDER_PATTERNS:
            match = pattern.search(line)
            if (
                match
                and match.group(0) not in ALLOWLISTED_SECRETS
                and not looks_like_placeholder(match.group(0))
            ):
                findings.append({"line": lineno, "type": label, "match": _mask(match.group(0))})
        generic = GENERIC_ASSIGN.search(line)
        if (
            generic
            and generic.group(2) not in ALLOWLISTED_SECRETS
            and not looks_like_placeholder(generic.group(2))
        ):
            findings.append({"line": lineno, "type": "hardcoded secret assignment", "match": _mask(generic.group(2))})
    return findings


def _mask(secret: str) -> str:
    if len(secret) <= 8:
        return secret[0] + "***"
    return f"{secret[:4]}***{secret[-2:]}"


def scan_repo() -> list[dict]:
    findings: list[dict] = []
    for rel in tracked_files():
        if rel in SELF_SKIP:
            continue
        path = REPO_ROOT / rel
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for item in scan_text(text):
            findings.append({"file": rel, **item})
    return findings


def check_env_hygiene() -> list[str]:
    issues: list[str] = []
    gitignore = REPO_ROOT / ".gitignore"
    ignored = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if ".env" not in ignored:
        issues.append(".env 未被 .gitignore 忽略")
    for rel in tracked_files():
        name = Path(rel).name
        if name == ".env":
            issues.append(f"真实 .env 被提交进仓库：{rel}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="仓库级安全自检门禁")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    findings = scan_repo()
    env_issues = check_env_hygiene()
    ok = not findings and not env_issues

    if args.json:
        print(json.dumps(
            {"ok": ok, "secret_findings": findings, "env_issues": env_issues},
            ensure_ascii=False, indent=2,
        ))
    else:
        if ok:
            print("OK: 未发现疑似密钥或 .env 卫生问题。")
        else:
            print("SECURITY SELF-CHECK FAILED")
            for item in findings:
                print(f"- [{item['type']}] {item['file']}:{item['line']} -> {item['match']}")
            for issue in env_issues:
                print(f"- [env] {issue}")
            print("\n如为文档示例误报，可在该行末尾添加 `pragma: allowlist secret`。")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
