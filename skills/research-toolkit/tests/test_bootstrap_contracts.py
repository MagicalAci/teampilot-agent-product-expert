import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
RUNNER = SCRIPTS_ROOT / "run_pipeline.py"
BOOTSTRAP = SCRIPTS_ROOT / "bootstrap-macos.sh"
DOCTOR = SCRIPTS_ROOT / "doctor-macos.sh"

sys.path.insert(0, str(SCRIPTS_ROOT))

from rtk.config import build_bootstrap_manifest  # noqa: E402
from rtk.doctor import detect_mcp_status  # noqa: E402


class BootstrapContractsTest(unittest.TestCase):
    def test_bootstrap_scripts_exist_and_help_lists_supported_commands(self):
        self.assertTrue(BOOTSTRAP.exists(), "缺少 bootstrap-macos.sh")
        self.assertTrue(DOCTOR.exists(), "缺少 doctor-macos.sh")

        result = subprocess.run(
            ["bash", str(BOOTSTRAP), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIn("doctor", result.stdout)
        self.assertIn("repair", result.stdout)
        self.assertIn("extract-frames", result.stdout)

    def test_doctor_command_supports_json_without_task_card(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "doctor", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("managed_runtime", payload)
        self.assertIn("mcp", payload)
        self.assertIn("ffmpeg", payload)
        self.assertIn("toolchain", payload)
        self.assertIn("readiness", payload)

    def test_bootstrap_manifest_declares_managed_runtime_and_mcp_dependencies(self):
        manifest = build_bootstrap_manifest(home=Path("/tmp/rtk-home"))

        self.assertIn(".cursor/skills-runtime/research-toolkit", manifest["managed_runtime"]["root"])
        self.assertEqual(manifest["system_packages"]["python_formula"], "python@3.11")
        self.assertEqual(manifest["system_packages"]["ffmpeg_formula"], "ffmpeg")
        self.assertTrue(
            any(item["server_id"] == "cursor-ide-browser" for item in manifest["mcp_dependencies"])
        )

    def test_doctor_classifies_required_and_installed_mcp_servers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            installed_server = home / ".cursor" / "projects" / "demo-project" / "mcps" / "user-firecrawl"
            installed_server.mkdir(parents=True, exist_ok=True)

            status = detect_mcp_status(home=home)
            browser = next(item for item in status["servers"] if item["server_id"] == "cursor-ide-browser")
            firecrawl = next(item for item in status["servers"] if item["server_id"] == "user-firecrawl")

            self.assertEqual(browser["status"], "需安装")
            self.assertIn("cursor-ide-browser", status["blocking"])
            self.assertEqual(firecrawl["status"], "已安装")
            self.assertTrue(firecrawl["installed"])

    def test_doctor_marks_auth_bound_servers_as_login_init(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            xiaohongshu = home / ".cursor" / "projects" / "demo-project" / "mcps" / "user-xiaohongshu"
            xiaohongshu.mkdir(parents=True, exist_ok=True)

            status = detect_mcp_status(home=home)
            target = next(item for item in status["servers"] if item["server_id"] == "user-xiaohongshu")

            self.assertEqual(target["status"], "需登录初始化")


if __name__ == "__main__":
    unittest.main()
