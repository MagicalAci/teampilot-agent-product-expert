import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNNER = SKILL_ROOT / "scripts" / "run_pipeline.py"


class PipelineSmokeTest(unittest.TestCase):
    def test_package_smoke_passes_for_all_supported_stacks(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "package-smoke", "--json"],
            cwd=SKILL_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(sorted(payload["stacks"].keys()), ["h5", "swiftui", "web"])
        for stack, summary in payload["stacks"].items():
            with self.subTest(stack=stack):
                self.assertTrue(summary["ok"])
                self.assertTrue(summary["bundle_exists"])
                self.assertEqual(summary["init_exit_code"], 0)
                self.assertEqual(summary["validate_exit_code"], 0)
                self.assertEqual(summary["package_exit_code"], 0)


class DeploySmokeTest(unittest.TestCase):
    """Test deploy subcommand without actually deploying (no CLI installed)."""

    def test_deploy_rejects_swiftui_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            init_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "init", "demo-swift",
                    "--title", "SwiftUI Test",
                    "--stack", "swiftui",
                    "--output-root", str(output_root),
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            deploy_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "deploy",
                    "--output-root", str(output_root),
                    "--platform", "vercel",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(deploy_result.returncode, 1)
            payload = json.loads(deploy_result.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertIn("swiftui", payload.get("error", "").lower())

    def test_deploy_accepts_web_stack_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            init_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "init", "demo-web",
                    "--title", "Web Test",
                    "--stack", "web",
                    "--output-root", str(output_root),
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            deploy_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "deploy",
                    "--output-root", str(output_root),
                    "--platform", "vercel",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(deploy_result.stdout)
            self.assertIn(payload["stack"], ["web"])
            self.assertNotEqual(payload.get("status"), "error")

    def test_deploy_accepts_h5_stack_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            init_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "init", "demo-h5",
                    "--title", "H5 Test",
                    "--stack", "h5",
                    "--output-root", str(output_root),
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            deploy_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "deploy",
                    "--output-root", str(output_root),
                    "--platform", "vercel",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(deploy_result.stdout)
            self.assertIn(payload["stack"], ["h5"])
            self.assertNotEqual(payload.get("status"), "error")

    def test_deploy_fails_without_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            deploy_result = subprocess.run(
                [
                    sys.executable, str(RUNNER), "deploy",
                    "--output-root", tmp,
                    "--platform", "surge",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(deploy_result.returncode, 1)
            payload = json.loads(deploy_result.stdout)
            self.assertEqual(payload["status"], "error")


if __name__ == "__main__":
    unittest.main()
