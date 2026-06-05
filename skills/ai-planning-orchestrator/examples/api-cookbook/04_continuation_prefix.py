"""
04 - 续写模式
通过 assistant message 的 prefix=true，让模型从指定文本继续生成。
适合补全、续写、格式化输出等场景。
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


def continuation(
    user_prompt: str,
    prefix_text: str,
    model: str = "Doubao-Seed-2.0-Mini-0215",
) -> str:
    """续写模式 — 模型从 prefix_text 开始继续生成。"""
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": prefix_text, "prefix": True},
        ],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("=== 续写模式示例 ===\n")

    # 示例1: 续写诗词
    result = continuation(
        user_prompt="写一首关于AI的五言绝句",
        prefix_text="算法织星河，",
    )
    print(f"诗词续写: 算法织星河，{result}\n")

    # 示例2: 续写 JSON（强制以特定格式开头）
    result = continuation(
        user_prompt='生成一个学生信息JSON，包含name、age、score',
        prefix_text='{"name": "',
    )
    print(f'JSON续写: {{"name": "{result}\n')

    # 示例3: 续写分析报告
    result = continuation(
        user_prompt="分析在线教育App的用户留存问题",
        prefix_text="## 问题分析\n\n根据数据显示，",
    )
    print(f"报告续写:\n## 问题分析\n\n根据数据显示，{result[:300]}...")
