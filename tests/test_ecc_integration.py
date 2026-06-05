"""ECC 借鉴集成契约测试：AgentShield 安全扫描连接器 + 方法论 ECC 增补。

守护 /安全扫描 连接器与方法论 ECC 节存在、自洽，并被 agent manifest / 命令路由
/ 提交评审契约正确接线。仅做连接器与方法论借鉴，不引入 ECC 框架代码。
"""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SECURITY_PATH = REPO_ROOT / "policies" / "agent-security-scan.md"
METHODOLOGY_PATH = REPO_ROOT / "policies" / "agent-team-methodology.md"
MANIFEST_PATH = REPO_ROOT / ".teampilot" / "agent.yml"
ROUTER_PATH = REPO_ROOT / ".cursor" / "rules" / "product-expert-commands.mdc"


class EccIntegrationContractTest(unittest.TestCase):
    def test_security_scan_connector_exists_and_self_consistent(self):
        self.assertTrue(SECURITY_PATH.exists(), "缺少 policies/agent-security-scan.md")
        text = SECURITY_PATH.read_text(encoding="utf-8")
        for marker in [
            "ecc-agentshield",
            "AgentShield",
            "降级",
            "MIT",
            "/安全扫描",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_methodology_has_ecc_cherry_pick_section(self):
        text = METHODOLOGY_PATH.read_text(encoding="utf-8")
        for marker in ["ECC", "持续学习", "Token", "worktree", "验证循环"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_security_scan_wired_into_manifest_and_router(self):
        manifest = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertIn("policies/agent-security-scan.md", manifest)
        self.assertIn("/安全扫描", manifest)

        router = ROUTER_PATH.read_text(encoding="utf-8")
        self.assertIn("/安全扫描", router)


if __name__ == "__main__":
    unittest.main()
