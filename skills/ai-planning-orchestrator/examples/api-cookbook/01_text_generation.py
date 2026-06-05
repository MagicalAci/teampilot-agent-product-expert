"""
01 - 文本生成（基础）
最简单的 API 调用，验证连通性和基本参数。
"""

import os
import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
    "X-App-Id": "AppHomeworkMonitorService",
    "X-Agent-Id": "1349344319163531264",
}


def text_generation(prompt: str, model: str = "Doubao-Seed-2.0-Mini-0215") -> dict:
    """最基础的文本生成调用。"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的AI助手。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    models = [
        "Doubao-Seed-2.0-Mini-0215",
        "Doubao-Seed-2.0-Lite-0215",
        "Doubao-Seed-2.0-Pro-0215",
    ]

    for model in models:
        print(f"\n{'='*60}")
        print(f"模型: {model}")
        print("=" * 60)

        result = text_generation("用一句话介绍AI策划是什么", model=model)
        choice = result["choices"][0]["message"]
        usage = result["usage"]

        print(f"回复: {choice['content'][:200]}")
        print(f"Token: input={usage.get('prompt_tokens', 'N/A')}, "
              f"output={usage.get('completion_tokens', 'N/A')}, "
              f"total={usage.get('total_tokens', 'N/A')}")
