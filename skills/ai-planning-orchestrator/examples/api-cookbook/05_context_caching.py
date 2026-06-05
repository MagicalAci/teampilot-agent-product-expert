"""
05 - 上下文缓存
将不变的 System Prompt 缓存起来，后续请求只传变化部分。
命中缓存可节省约 50% 成本、降低 30%+ 延迟。
"""

import os
import json
import time
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "")
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}

LONG_SYSTEM_PROMPT = """你是一个专业的AI教育课程规划师。你的核心能力包括：
1. 基于布鲁姆分类法设计教学目标（记忆→理解→应用→分析→评价→创造）
2. 运用建构主义学习理论设计互动环节
3. 采用ADDIE课程设计模型（分析→设计→开发→实施→评估）
4. 结合加涅九大教学事件编排课堂流程
5. 针对K12学生的认知发展阶段调整教学策略
6. 设计差异化教学方案，适应不同学习风格
你必须遵循以下规则：
- 每个教学目标必须可测量、可评估
- 教学活动必须有明确的时间分配
- 必须包含形成性评估和总结性评估
- 课程设计必须考虑学生的先验知识"""


def create_cache(model: str = "Doubao-Seed-2.0-Mini-0215") -> tuple[str, dict]:
    """第一步：创建缓存，返回 (response_id, usage)。"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": LONG_SYSTEM_PROMPT},
            {"role": "user", "content": "你好，请确认你已理解你的角色。"},
        ],
        "caching": {"type": "enabled"},
        "ttl": 300,
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["id"], data.get("usage", {})


def use_cache(cache_id: str, question: str, model: str = "Doubao-Seed-2.0-Mini-0215") -> dict:
    """第二步：使用缓存发送后续请求。"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "previous_response_id": cache_id,
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("=== 上下文缓存示例 ===\n")

    # Step 1: 创建缓存
    print("[Step 1] 创建缓存...")
    cache_id, usage1 = create_cache()
    print(f"  缓存 ID: {cache_id}")
    print(f"  首次 token: {json.dumps(usage1)}")

    # 等待缓存生效
    time.sleep(2)

    # Step 2: 使用缓存
    questions = [
        "帮我设计一节小学三年级数学课，主题是分数的认识",
        "这节课的课堂互动环节应该怎么设计？",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n[Step 2.{i}] 使用缓存: {q[:30]}...")
        result = use_cache(cache_id, q)
        usage = result.get("usage", {})
        ptd = usage.get("prompt_tokens_details", usage.get("input_tokens_details", {}))
        cached = ptd.get("cached_tokens", 0)
        total_input = usage.get("prompt_tokens", usage.get("input_tokens", 0))

        print(f"  回复: {result['choices'][0]['message']['content'][:150]}...")
        print(f"  输入 token: {total_input}")
        print(f"  缓存命中:  {cached}")
        print(f"  缓存命中率: {cached/total_input*100:.1f}%" if total_input else "  N/A")
