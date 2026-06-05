"""
08 - 视频理解
传入视频 URL，让模型分析视频内容。
仅 Pro 模型支持视频理解，需要较长超时时间。

注意：视频 URL 需要平台可访问（内网或公网可达）。
"""

import os
import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


def video_understanding(
    video_url: str,
    prompt: str,
    model: str = "Doubao-Seed-2.0-Pro-0215",
) -> str:
    """视频理解 — 传入视频 URL，返回分析结果。"""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "video_url", "video_url": {"url": video_url}},
                ],
            }
        ],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("=== 视频理解示例 ===\n")

    # 使用公开测试视频
    VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"

    print(f"视频: {VIDEO_URL}")
    print("分析中（可能需要 30-60 秒）...\n")

    result = video_understanding(VIDEO_URL, "详细描述这个视频的内容、场景和主要事件")
    print(f"分析结果:\n{result}")
