import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / ".teampilot" / "agent.yml"
ROUTER_PATH = REPO_ROOT / ".cursor" / "rules" / "product-expert-commands.mdc"
README_PATH = REPO_ROOT / "README.md"


class ProductExpertAgentRepositoryTest(unittest.TestCase):
    def test_manifest_registers_three_capabilities(self):
        manifest = MANIFEST_PATH.read_text(encoding="utf-8")

        expected_snippets = [
            "version: 0.2.0",
            "title: 单产品分析",
            "command: /竞品分析",
            "title: 产品策划",
            "command: /产品策划",
            "title: AI策划",
            "command: /AI策划",
            "skills/single-product-competitor-analysis/SKILL.md",
            "skills/education-prd-orchestrator/SKILL.md",
            "skills/ai-planning-orchestrator/SKILL.md",
        ]
        for snippet in expected_snippets:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, manifest)

    def test_router_mentions_aliases_and_subflows(self):
        router = ROUTER_PATH.read_text(encoding="utf-8")
        for command in [
            "/单产品分析",
            "/竞品分析",
            "/爬取",
            "/竞品引导",
            "/产品策划",
            "/产品策划校验",
            "/AI策划",
            "/AIPRD",
            "/AI脚本",
            "/AI测试",
            "/查看能力",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, router)

    def test_readme_lists_direct_usage_commands(self):
        readme = README_PATH.read_text(encoding="utf-8")
        for snippet in [
            "单产品分析",
            "产品策划",
            "AI策划",
            "/单产品分析 豆包爱学",
            "/产品策划 家长端留存提升方案",
            "/AI策划 PRD 生成 Agent",
            "python -m unittest tests/test_product_expert_agent.py",
        ]:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, readme)

    def test_skill_directories_keep_key_assets(self):
        expected_paths = [
            "skills/single-product-competitor-analysis/SKILL.md",
            "skills/single-product-competitor-analysis/scripts/run_pipeline.py",
            "skills/single-product-competitor-analysis/tests/test_pipeline_smoke.py",
            "skills/education-prd-orchestrator/SKILL.md",
            "skills/education-prd-orchestrator/scripts/run_pipeline.py",
            "skills/education-prd-orchestrator/tests/test_pipeline_smoke.py",
            "skills/ai-planning-orchestrator/SKILL.md",
            "skills/ai-planning-orchestrator/scripts/init_ai_planning_delivery.py",
            "skills/ai-planning-orchestrator/tests/test_pipeline_smoke.py",
        ]
        for relative_path in expected_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).exists(), relative_path)


if __name__ == "__main__":
    unittest.main()
