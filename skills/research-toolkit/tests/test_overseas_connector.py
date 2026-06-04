"""海外调研通道（last30days 连接器）集成契约测试。

守护 last30days 作为 research-toolkit 海外采集通道的接入：协议、连接器参考、
SKILL.md 命令与平台、安装协议降级，都必须存在且自洽。
"""

import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


class OverseasConnectorContractTest(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        path = SKILL_ROOT / relative_path
        self.assertTrue(path.exists(), f"缺少文件：{relative_path}")
        return path.read_text(encoding="utf-8")

    def test_overseas_protocol_exists_and_covers_core_contract(self):
        protocol = self._read("protocols/overseas-research.md")
        for marker in [
            "last30days",
            "03-normalized/overseas",
            "降级",
            "Reddit",
            "Polymarket",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, protocol)

    def test_connector_reference_exists_with_install_and_license(self):
        connector = self._read("references/last30days-connector.md")
        for marker in [
            "npx skills add mvanhorn/last30days-skill",
            "Python 3.12",
            "MIT",
            "降级",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, connector)

    def test_skill_registers_overseas_command_and_channel(self):
        skill = self._read("SKILL.md")
        for marker in [
            "/海外调研",
            "last30days",
            "protocols/overseas-research.md",
            "references/last30days-connector.md",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)

    def test_tooling_protocol_documents_overseas_degradation(self):
        tooling = self._read("protocols/tooling-and-installation.md")
        self.assertIn("last30days", tooling)
        for status in ["已安装", "需安装", "需登录初始化", "当前降级模式"]:
            with self.subTest(status=status):
                self.assertIn(status, tooling)


if __name__ == "__main__":
    unittest.main()
