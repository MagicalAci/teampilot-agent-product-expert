"""
06 - 多轮对话上下文管理
通过维护 messages 数组实现多轮对话，模型能理解完整对话历史。
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


class ChatSession:
    """多轮对话管理器 — 维护 messages 上下文。"""

    def __init__(self, system_prompt: str, model: str = "Doubao-Seed-2.0-Mini-0215"):
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.messages,
            "temperature": 0.7,
        }
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        resp.raise_for_status()

        reply = resp.json()["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    @property
    def turn_count(self) -> int:
        return len([m for m in self.messages if m["role"] == "user"])


if __name__ == "__main__":
    print("=== 多轮对话示例 ===\n")

    session = ChatSession(
        system_prompt="你是一个AI产品策划专家，帮助用户逐步完善AI方案。",
        model="Doubao-Seed-2.0-Mini-0215",
    )

    conversation = [
        "我想做一个AI自动批改作文的功能",
        "批改维度应该包含哪些？",
        "技术架构上推荐用什么方案？",
        "总结一下我们刚才讨论的要点",
    ]

    for user_msg in conversation:
        print(f"[用户 - 第{session.turn_count + 1}轮] {user_msg}")
        reply = session.chat(user_msg)
        print(f"[助手] {reply[:200]}{'...' if len(reply) > 200 else ''}")
        print()

    print(f"对话总轮数: {session.turn_count}")
    print(f"消息数组长度: {len(session.messages)}")
