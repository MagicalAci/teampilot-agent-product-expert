"""AI 能力升级 Phase 2（P1）契约测试。

守护 P1 落地的 6 个新协议、3 个既有协议扩展、knowledge/ 脚手架与 skill 接入，
以及 manifest / task-navigator 接线。
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


P1_POLICY_MARKERS = {
    "policies/context-budget.md": [
        "write", "select", "compress", "isolate", "context rot", "注意力预算", "compaction",
    ],
    "policies/agentops-lifecycle.md": [
        "build", "eval", "ship", "govern", "准入门禁", "回归阻断",
    ],
    "policies/prompt-optimization-protocol.md": [
        "GEPA", "MIPROv2", "score", "feedback", "升级判据", "ASI",
    ],
    "policies/output-contract.md": [
        "schema 契约", "Pydantic", "reask", "跨产物引用", "必填段",
    ],
    "policies/mcp-tool-authoring.md": [
        "造", "买", "降级", "build → eval → iterate", "契约测试", "连接器化",
    ],
    "policies/red-team-checklist.md": [
        "提示注入", "越狱", "数据外泄", "越权", "期望安全行为", "garak",
    ],
}


class CapabilityUpgradeP1ContractTest(unittest.TestCase):
    def test_p1_policies_exist_with_markers(self):
        for rel, markers in P1_POLICY_MARKERS.items():
            path = REPO_ROOT / rel
            with self.subTest(file=rel):
                self.assertTrue(path.exists(), f"缺少 {rel}")
                text = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, text, f"{rel} 缺标记 {marker}")

    def test_knowledge_scaffold_exists(self):
        path = REPO_ROOT / "knowledge" / "README.md"
        self.assertTrue(path.exists(), "缺少 knowledge/README.md")
        text = path.read_text(encoding="utf-8")
        for marker in ["build_corpus", "memory-protocol.md", "retrieval-protocol.md", "写入纪律"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_existing_policies_extended(self):
        security = read("policies/agent-security-scan.md")
        for marker in ["MCP 运行时风险", "工具投毒", "rug pull", "不可信响应", "第三方 MCP 信任", "agent-safety-protocol.md"]:
            with self.subTest(security=marker):
                self.assertIn(marker, security)

        team = read("policies/agent-team-methodology.md")
        for marker in ["cost-discipline-methodology.md", "agent-safety-protocol.md", "agentops-lifecycle.md"]:
            with self.subTest(team=marker):
                self.assertIn(marker, team)

        ev = read("policies/llm-eval-methodology.md")
        for marker in ["agent-trajectory-eval.md", "red-team-checklist.md"]:
            with self.subTest(eval=marker):
                self.assertIn(marker, ev)

    def test_aibi_skill_wires_retrieval(self):
        skill = read("skills/aibi-query/SKILL.md")
        for marker in ["Table-RAG-lite", "history-aware", "retrieval-protocol.md"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)

    def test_manifest_and_navigator_register_p1_policies(self):
        manifest = read(".teampilot/agent.yml")
        navigator = read(".cursor/rules/task-navigator.mdc")
        for rel in P1_POLICY_MARKERS:
            with self.subTest(policy=rel):
                self.assertIn(rel, manifest)
                self.assertIn(rel, navigator)


if __name__ == "__main__":
    unittest.main()
