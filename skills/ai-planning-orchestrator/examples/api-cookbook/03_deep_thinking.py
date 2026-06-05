"""
03 - 深度思考
Doubao-Seed-2.0 系列默认开启深度思考，返回 reasoning_content 字段。
适合需要推理链的复杂分析任务。
"""

import os
import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


def deep_thinking(prompt: str, model: str = "Doubao-Seed-2.0-Pro-0215") -> dict:
    """深度思考调用 — 默认就开启，无需额外参数。"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("=== 深度思考示例 ===\n")

    result = deep_thinking("分析一个在线教育App的AI推荐系统应该包含哪些核心模块，给出架构建议")
    msg = result["choices"][0]["message"]
    usage = result["usage"]

    reasoning = msg.get("reasoning_content", "")
    content = msg.get("content", "")

    # 推理过程（模型内部思考链，不暴露给最终用户）
    if reasoning:
        print(f"[推理过程] ({len(reasoning)} 字符)")
        print(reasoning[:500] + "..." if len(reasoning) > 500 else reasoning)
        print()

    # 最终回复
    print(f"[最终回复] ({len(content)} 字符)")
    print(content[:800] + "..." if len(content) > 800 else content)
    print()

    # Token 统计
    ctd = usage.get("completion_tokens_details", {})
    print(f"Token 统计:")
    print(f"  输入:     {usage.get('prompt_tokens', 'N/A')}")
    print(f"  推理:     {ctd.get('reasoning_tokens', 'N/A')}")
    print(f"  输出:     {usage.get('completion_tokens', 'N/A')}")
    print(f"  总计:     {usage.get('total_tokens', 'N/A')}")
