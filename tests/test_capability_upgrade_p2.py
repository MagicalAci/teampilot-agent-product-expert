"""AI 能力升级 Phase 3（P2）契约测试。

守护 6 个 P2 实现级协议（触发式重基建）、零依赖检索脚手架、以及
manifest / task-navigator / SYNTHESIS 接线。
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


P2_POLICY_MARKERS = {
    "policies/advanced-retrieval-p2.md": [
        "CRAG", "Adaptive-RAG", "GraphRAG", "LightRAG", "ColPali", "sqlite-vec", "时序", "触发判定", "retrieval_index.py",
    ],
    "policies/codeact-execution-p2.md": [
        "CodeAct", "脚本优先", "沙箱", "E2B", "受管 venv", "降级",
    ],
    "policies/durable-execution-p2.md": [
        "durable", "状态文件", "Temporal", "DBOS", "断点续跑", "触发判定",
    ],
    "policies/self-hosted-serving-p2.md": [
        "vLLM", "SGLang", "量化", "embedding", "rerank", "自托管", "触发判定",
    ],
    "policies/productization-readiness-p2.md": [
        "多租户", "SSO", "身份", "SLA", "EU AI Act", "ISO/IEC 42001", "触发判定",
    ],
    "policies/self-evolving-agent-p2.md": [
        "ACE", "Generator", "Reflector", "Curator", "增量 delta", "helpful", "ADAS", "DGM", "北极星",
    ],
}


class CapabilityUpgradeP2ContractTest(unittest.TestCase):
    def test_p2_policies_exist_with_markers(self):
        for rel, markers in P2_POLICY_MARKERS.items():
            path = REPO_ROOT / rel
            with self.subTest(file=rel):
                self.assertTrue(path.exists(), f"缺少 {rel}")
                text = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, text, f"{rel} 缺标记 {marker}")

    def test_retrieval_scaffold_exists(self):
        self.assertTrue((REPO_ROOT / "scripts" / "retrieval_index.py").exists())
        self.assertTrue((REPO_ROOT / "tests" / "test_retrieval_index.py").exists())

    def test_manifest_and_navigator_register_p2(self):
        manifest = read(".teampilot/agent.yml")
        navigator = read(".cursor/rules/task-navigator.mdc")
        for rel in P2_POLICY_MARKERS:
            with self.subTest(policy=rel):
                self.assertIn(rel, manifest)
                self.assertIn(rel, navigator)

    def test_p0p1_protocols_point_to_p2(self):
        # 各 P0/P1 协议应指向对应 P2 文档（可发现性）
        self.assertIn("advanced-retrieval-p2.md", read("policies/retrieval-protocol.md"))
        self.assertIn("codeact-execution-p2.md", read("policies/tool-use-protocol.md"))
        self.assertIn("durable-execution-p2.md", read("policies/orchestration-runtime.md"))
        self.assertIn("self-hosted-serving-p2.md", read("policies/cost-discipline-methodology.md"))
        self.assertIn("self-evolving-agent-p2.md", read("policies/agentops-lifecycle.md"))

    def test_synthesis_marks_phase3_spec_complete(self):
        synth = read("research/ai-capability-upgrade/SYNTHESIS.md")
        self.assertIn("spec-complete", synth)
        self.assertIn("retrieval_index.py", synth)


if __name__ == "__main__":
    unittest.main()
