import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / ".teampilot" / "agent.yml"
ROUTER_PATH = REPO_ROOT / ".cursor" / "rules" / "product-expert-commands.mdc"
README_PATH = REPO_ROOT / "README.md"


class ProductExpertAgentRepositoryTest(unittest.TestCase):
    def test_manifest_registers_four_capabilities(self):
        manifest = MANIFEST_PATH.read_text(encoding="utf-8")

        expected_snippets = [
            "title: 调研分析",
            "command: /深度调研",
            "title: 产品策划",
            "command: /产品策划",
            "title: AI策划",
            "command: /AI策划",
            "title: Demo开发",
            "command: /Demo开发",
            "skills/research-toolkit/SKILL.md",
            "skills/education-prd-orchestrator/SKILL.md",
            "skills/ai-planning-orchestrator/SKILL.md",
            "skills/product-demo-orchestrator/SKILL.md",
        ]
        for snippet in expected_snippets:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, manifest)

    def test_router_mentions_aliases_and_subflows(self):
        router = ROUTER_PATH.read_text(encoding="utf-8")
        for command in [
            "/深度调研",
            "/爬取",
            "/体验引导",
            "/调研安装",
            "/调研体检",
            "/调研授权",
            "/产品策划",
            "/产品策划校验",
            "/AI策划",
            "/AIPRD",
            "/AI脚本",
            "/AI测试",
            "/Demo开发",
            "/Demo设计系统",
            "/Demo脚手架",
            "/Demo打磨",
            "/Demo校验",
            "/查看能力",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, router)

    def test_readme_lists_direct_usage_commands(self):
        readme = README_PATH.read_text(encoding="utf-8")
        for snippet in [
            "调研分析",
            "产品策划",
            "AI策划",
            "Demo开发",
            "/深度调研 豆包爱学",
            "/产品策划 家长端留存提升方案",
            "/AI策划 PRD 生成 Agent",
            "/Demo开发 AI 陪练产品首页 demo，目标平台：H5",
            "python -m unittest tests/test_product_expert_agent.py",
        ]:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, readme)

    def test_skill_directories_keep_key_assets(self):
        expected_paths = [
            "skills/research-toolkit/SKILL.md",
            "skills/research-toolkit/scripts/run_pipeline.py",
            "skills/research-toolkit/tests/test_pipeline_smoke.py",
            "skills/education-prd-orchestrator/SKILL.md",
            "skills/education-prd-orchestrator/scripts/run_pipeline.py",
            "skills/education-prd-orchestrator/tests/test_pipeline_smoke.py",
            "skills/ai-planning-orchestrator/SKILL.md",
            "skills/ai-planning-orchestrator/scripts/init_ai_planning_delivery.py",
            "skills/ai-planning-orchestrator/tests/test_pipeline_smoke.py",
            "skills/product-demo-orchestrator/SKILL.md",
            "skills/product-demo-orchestrator/scripts/run_pipeline.py",
            "skills/product-demo-orchestrator/tests/test_pipeline_smoke.py",
        ]
        for relative_path in expected_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).exists(), relative_path)


if __name__ == "__main__":
    unittest.main()
