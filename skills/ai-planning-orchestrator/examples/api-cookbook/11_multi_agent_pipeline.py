"""
11 - 多 Agent 串联编排
真实的 AI 策划不是单个 prompt，而是多个 Agent 各司其职、串联协作。
本示例演示一个三阶段 pipeline: 需求分析 → 方案设计 → 内容生成。

每个 Agent 有独立的 system prompt 和职责边界，
上一个 Agent 的输出作为下一个 Agent 的输入。
"""

import json
import time
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


class Agent:
    """单个 Agent — 有独立的角色定义和模型配置。"""

    def __init__(self, name: str, system_prompt: str, model: str = "Doubao-Seed-2.0-Mini-0215"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model

    def run(self, user_input: str, temperature: float = 0.7) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": temperature,
        }
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class AgentPipeline:
    """多 Agent 串联编排器。"""

    def __init__(self, agents: list[Agent]):
        self.agents = agents
        self.trace: list[dict] = []

    def run(self, initial_input: str) -> str:
        current_input = initial_input
        for i, agent in enumerate(self.agents):
            print(f"\n{'='*60}")
            print(f"[Stage {i+1}/{len(self.agents)}] {agent.name} ({agent.model})")
            print(f"{'='*60}")
            print(f"输入: {current_input[:150]}...")

            start = time.time()
            output = agent.run(current_input)
            elapsed = time.time() - start

            self.trace.append({
                "agent": agent.name,
                "model": agent.model,
                "input_preview": current_input[:100],
                "output_preview": output[:100],
                "elapsed_seconds": round(elapsed, 2),
            })

            print(f"输出: {output[:300]}{'...' if len(output) > 300 else ''}")
            print(f"耗时: {elapsed:.2f}s")

            current_input = output

        return current_input


# === 定义三个 Agent ===

analyst = Agent(
    name="需求分析师",
    system_prompt="""你是一个AI产品需求分析师。
你的任务是：接收一个粗略的AI功能需求，输出结构化的需求分析。
输出必须包含：
1. 核心问题定义（一句话）
2. 目标用户画像（2-3个特征）
3. 关键输入数据（列出字段）
4. 期望输出结果（列出字段）
5. 质量指标（2-3个可量化指标）
简洁准确，不要写多余的过渡语。""",
    model="Doubao-Seed-2.0-Mini-0215",
)

architect = Agent(
    name="方案架构师",
    system_prompt="""你是一个AI方案架构师。
你的任务是：接收需求分析结果，输出技术方案设计。
输出必须包含：
1. 推荐模型和理由
2. Prompt 设计策略（分几个模块、每个模块职责）
3. 数据流设计（输入→处理→输出）
4. 降级策略（模型不可用或输出异常时怎么办）
5. 成本估算思路
基于幻视平台能力设计，可用模型: Mini/Lite/Pro。""",
    model="Doubao-Seed-2.0-Lite-0215",
)

generator = Agent(
    name="内容生成器",
    system_prompt="""你是一个AI脚本生成器。
你的任务是：接收技术方案，输出一个核心 Prompt 模块的完整定义。
输出必须包含：
1. 模块名称
2. 人设
3. 任务
4. 规则（3-5条）
5. 输出规范（JSON 结构）
6. 严格禁止（2-3条）
7. 思考链（模型内部推理步骤）
格式统一使用 markdown，每个部分用 ## 标题。""",
    model="Doubao-Seed-2.0-Mini-0215",
)

if __name__ == "__main__":
    print("=== 多 Agent Pipeline 示例 ===")
    print("流程: 需求分析师 → 方案架构师 → 内容生成器\n")

    pipeline = AgentPipeline([analyst, architect, generator])
    final_output = pipeline.run(
        "我想做一个AI自动生成课后练习题的功能，根据课堂内容和学生水平生成个性化的练习题"
    )

    print(f"\n{'='*60}")
    print("Pipeline 执行追踪:")
    print("=" * 60)
    for step in pipeline.trace:
        print(f"  {step['agent']}: {step['elapsed_seconds']}s ({step['model']})")
