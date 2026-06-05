"""外部技能集成契约测试：nano-banana 图片提示词连接器 + Prompt_Engineering 方法论。

守护两个新集成的文档存在、自洽，并被 agent manifest / 命令路由 / AI策划 SKILL 接线。
均为连接器/方法论挑拣，不引入外部框架代码。
"""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = REPO_ROOT / "policies" / "image-prompt-connector.md"
PE_PATH = REPO_ROOT / "policies" / "prompt-engineering-techniques.md"
MANIFEST_PATH = REPO_ROOT / ".teampilot" / "agent.yml"
ROUTER_PATH = REPO_ROOT / ".cursor" / "rules" / "product-expert-commands.mdc"
AI_SKILL_PATH = REPO_ROOT / "skills" / "ai-planning-orchestrator" / "SKILL.md"


class ExternalSkillIntegrationsTest(unittest.TestCase):
    def test_image_prompt_connector_exists_and_self_consistent(self):
        self.assertTrue(IMAGE_PATH.exists(), "缺少 policies/image-prompt-connector.md")
        text = IMAGE_PATH.read_text(encoding="utf-8")
        for marker in [
            "nano-banana-pro-prompts-recommend-skill",
            "npx skills i",
            "降级",
            "MIT",
            "/图片提示词",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_prompt_engineering_methodology_exists_and_covers_techniques(self):
        self.assertTrue(PE_PATH.exists(), "缺少 policies/prompt-engineering-techniques.md")
        text = PE_PATH.read_text(encoding="utf-8")
        for marker in [
            "NirDiamant/Prompt_Engineering",
            "CoT",
            "少样本",
            "自洽",
            "角色",
            "提示安全",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_image_prompt_wired_into_manifest_and_router(self):
        manifest = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertIn("policies/image-prompt-connector.md", manifest)
        self.assertIn("/图片提示词", manifest)
        self.assertIn("policies/prompt-engineering-techniques.md", manifest)

        router = ROUTER_PATH.read_text(encoding="utf-8")
        self.assertIn("/图片提示词", router)

    def test_prompt_engineering_wired_into_ai_planning(self):
        skill = AI_SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("prompt-engineering-techniques.md", skill)


if __name__ == "__main__":
    unittest.main()
