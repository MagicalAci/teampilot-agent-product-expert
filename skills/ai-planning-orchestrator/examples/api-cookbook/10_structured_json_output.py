"""
10 - 结构化 JSON 输出

重要：幻视平台不支持 response_format（json_object / json_schema 均报错）。
正确做法是通过 system prompt 强约束 + 低温度实现稳定 JSON 输出。
本示例包含输出校验和重试机制。
"""

import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


def structured_json_output(
    prompt: str,
    json_schema_desc: str,
    model: str = "Doubao-Seed-2.0-Mini-0215",
    max_retries: int = 2,
) -> dict:
    """
    通过 prompt 引导实现结构化 JSON 输出。
    包含输出校验和自动重试。
    """
    system_prompt = f"""你是一个严格的数据生成器。
你只能输出合法的 JSON，不允许输出任何其他文字、解释或 markdown 包装。
输出必须严格符合以下 JSON 结构：
{json_schema_desc}
直接输出 JSON，不要用 ```json 包裹。"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }

    for attempt in range(max_retries + 1):
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        # 去掉可能的 markdown 包装
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if attempt < max_retries:
                payload["messages"].append({"role": "assistant", "content": content})
                payload["messages"].append({
                    "role": "user",
                    "content": "输出不是合法JSON，请重新输出纯JSON，不要有任何其他内容。",
                })
                continue
            raise ValueError(f"经过 {max_retries + 1} 次尝试仍无法获取合法 JSON: {content[:200]}")


if __name__ == "__main__":
    print("=== 结构化 JSON 输出示例 ===\n")

    # 示例1: 简单对象
    result = structured_json_output(
        prompt="生成一个小学三年级学生的信息",
        json_schema_desc='{"name": "string", "age": "integer", "grade": "string", "subjects": ["string"]}',
    )
    print(f"学生信息:\n{json.dumps(result, ensure_ascii=False, indent=2)}\n")

    # 示例2: 复杂嵌套结构
    result = structured_json_output(
        prompt="生成一个AI课堂推荐方案",
        json_schema_desc="""{
  "lesson_plan": {
    "topic": "string",
    "grade": "string",
    "duration_minutes": "integer",
    "objectives": ["string"],
    "activities": [{"name": "string", "type": "string", "duration": "integer"}]
  },
  "ai_config": {
    "model": "string",
    "temperature": "number",
    "use_cache": "boolean"
  }
}""",
        model="Doubao-Seed-2.0-Lite-0215",
    )
    print(f"课堂方案:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
