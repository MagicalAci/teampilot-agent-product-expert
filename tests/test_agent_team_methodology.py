"""团队架构与技能编写方法论（蒸馏适配自 revfactory/harness）集成契约测试。

守护方法论文档存在、自洽，并被任务领航、提交评审契约、agent manifest 正确接线。
"""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY_PATH = REPO_ROOT / "policies" / "agent-team-methodology.md"
MANIFEST_PATH = REPO_ROOT / ".teampilot" / "agent.yml"
NAVIGATOR_PATH = REPO_ROOT / ".cursor" / "rules" / "task-navigator.mdc"
REVIEW_CONTRACT_PATH = REPO_ROOT / "policies" / "submission-review-contract.md"


class AgentTeamMethodologyContractTest(unittest.TestCase):
    def test_methodology_exists_and_covers_six_patterns(self):
        self.assertTrue(METHODOLOGY_PATH.exists(), "缺少 policies/agent-team-methodology.md")
        text = METHODOLOGY_PATH.read_text(encoding="utf-8")
        for pattern in [
            "Pipeline",
            "Fan-out/Fan-in",
            "Expert Pool",
            "Producer-Reviewer",
            "Supervisor",
            "Hierarchical",
        ]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_methodology_attributes_source_and_license(self):
        text = METHODOLOGY_PATH.read_text(encoding="utf-8")
        for marker in ["revfactory/harness", "Apache-2.0", "Cursor"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_methodology_covers_skill_authoring_and_testing(self):
        text = METHODOLOGY_PATH.read_text(encoding="utf-8")
        for marker in ["Description", "Progressive Disclosure", "Baseline", "经验写回"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_methodology_wired_into_manifest_and_rules(self):
        manifest = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertIn("policies/agent-team-methodology.md", manifest)

        navigator = NAVIGATOR_PATH.read_text(encoding="utf-8")
        self.assertIn("agent-team-methodology.md", navigator)

        review = REVIEW_CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertIn("agent-team-methodology.md", review)


if __name__ == "__main__":
    unittest.main()
