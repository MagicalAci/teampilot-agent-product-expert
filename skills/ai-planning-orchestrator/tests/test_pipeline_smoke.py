import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = SKILL_ROOT / "scripts" / "init_ai_planning_delivery.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_ai_planning_assets.py"
PACKAGE_SCRIPT = SKILL_ROOT / "scripts" / "package_ai_script_bundle.py"


class PipelineSmokeTest(unittest.TestCase):
    def test_init_validate_and_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            output_dir = temp_root / "out"
            bundle_path = temp_root / "dist" / "demo-agent.zip"
            slug = "demo-agent"

            init_result = subprocess.run(
                [
                    sys.executable,
                    str(INIT_SCRIPT),
                    slug,
                    "--title",
                    "Demo Agent",
                    "--output-dir",
                    str(output_dir),
                    "--overwrite",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0, msg=init_result.stdout + init_result.stderr)

            prd = output_dir / f"{slug}-ai-prd.md"
            test_report = output_dir / f"{slug}-ai-test-report.md"
            bundle_readme = output_dir / f"{slug}-bundle-readme.md"
            bundle_manifest = output_dir / f"{slug}-bundle-manifest.md"

            validate_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATE_SCRIPT),
                    "--prd",
                    str(prd),
                    "--test-report",
                    str(test_report),
                    "--bundle-readme",
                    str(bundle_readme),
                    "--require-file",
                    str(bundle_manifest),
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=validate_result.stdout + validate_result.stderr,
            )
            payload = json.loads(validate_result.stdout)
            self.assertEqual(payload["missing_files"], [])
            for name, summary in payload["documents"].items():
                with self.subTest(document=name):
                    self.assertTrue(summary["exists"])
                    self.assertEqual(summary["missing_headings"], [])

            package_result = subprocess.run(
                [
                    sys.executable,
                    str(PACKAGE_SCRIPT),
                    str(bundle_path),
                    str(output_dir),
                    "--root-name",
                    slug,
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                package_result.returncode,
                0,
                msg=package_result.stdout + package_result.stderr,
            )
            self.assertTrue(bundle_path.exists())


if __name__ == "__main__":
    unittest.main()
