#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from deerflow.client import DeerFlowClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Embedded DeerFlow bridge")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--config-path", required=True)
    parser.add_argument("--thread-id", default="local-research-system")
    parser.add_argument("--model-name")
    parser.add_argument("--subagent-enabled", action="store_true")
    parser.add_argument("--disable-thinking", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    client = DeerFlowClient(
        config_path=args.config_path,
        model_name=args.model_name,
        thinking_enabled=not args.disable_thinking,
        subagent_enabled=args.subagent_enabled,
    )
    content = client.chat(args.prompt, thread_id=args.thread_id)
    payload = {
        "ok": True,
        "thread_id": args.thread_id,
        "content": content,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
