import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNNER = SKILL_ROOT / "scripts" / "run_pipeline.py"


class PipelineSmokeTest(unittest.TestCase):
    def test_package_smoke_passes(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "package-smoke", "--json"],
            cwd=SKILL_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["contract_ok"])
        self.assertEqual(payload["asset_validator_exit_code"], 0)
        self.assertEqual(payload["strict_errors"], [])

    def test_init_delivery_contract_only_validation_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "outputs" / "demo-skeleton"
            init_result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "init-delivery",
                    "demo-skeleton",
                    "--title",
                    "Demo Skeleton",
                    "--output-root",
                    str(output_root),
                    "--overwrite",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0, msg=init_result.stdout + init_result.stderr)

            validate_result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "validate",
                    "--output-root",
                    str(output_root),
                    "--contract-only",
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, msg=validate_result.stdout + validate_result.stderr)
            payload = json.loads(validate_result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["asset_validator_exit_code"], 0)

    def test_fixture_overlay_can_pass_strict_validate(self):
        fixture_root = SKILL_ROOT / "fixtures" / "demo-product"
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "outputs" / "fixture-demo"
            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "init-delivery",
                    "fixture-demo",
                    "--title",
                    "Fixture Demo",
                    "--output-root",
                    str(output_root),
                    "--overwrite",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            shutil.copytree(fixture_root, output_root, dirs_exist_ok=True)

            validate_result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "validate",
                    "--output-root",
                    str(output_root),
                    "--json",
                ],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, msg=validate_result.stdout + validate_result.stderr)
            payload = json.loads(validate_result.stdout)
            self.assertEqual(payload["strict_errors"], [])


if __name__ == "__main__":
    unittest.main()
