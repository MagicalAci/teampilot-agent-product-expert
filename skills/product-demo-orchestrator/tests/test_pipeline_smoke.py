import json
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
