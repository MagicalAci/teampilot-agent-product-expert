"""
02 - 流式输出
SSE (Server-Sent Events) 逐 token 返回，适合需要实时展示的场景。
"""

import os
import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
    "Accept": "text/event-stream",
}


def stream_chat(prompt: str, model: str = "Doubao-Seed-2.0-Mini-0215"):
    """流式调用，逐 chunk 输出。"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "temperature": 0.7,
    }
    with requests.post(API_URL, headers=HEADERS, json=payload, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        full_content = ""
        full_reasoning = ""

        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].strip()
            if data_str == "[DONE]":
                break

            chunk = json.loads(data_str)
            delta = chunk["choices"][0].get("delta", {})

            if delta.get("reasoning_content"):
                full_reasoning += delta["reasoning_content"]

            if delta.get("content"):
                print(delta["content"], end="", flush=True)
                full_content += delta["content"]

        print()
        return {"content": full_content, "reasoning": full_reasoning}


if __name__ == "__main__":
    print("=== 流式输出示例 ===\n")
    result = stream_chat("用三句话解释什么是多Agent系统")
    print(f"\n完整回复长度: {len(result['content'])} 字符")
    if result["reasoning"]:
        print(f"推理过程长度: {len(result['reasoning'])} 字符")
