import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNNER = SKILL_ROOT / "scripts" / "run_pipeline.py"
FIXTURE_ROOT = SKILL_ROOT / "fixtures" / "demo-product"


def build_case(temp_root: Path, slug: str) -> Path:
    output_root = temp_root / "outputs" / slug
    subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "init-delivery",
            slug,
            "--title",
            "Validator Demo",
            "--output-root",
            str(output_root),
            "--overwrite",
        ],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    shutil.copytree(FIXTURE_ROOT, output_root, dirs_exist_ok=True)
    return output_root


class AssetValidatorTest(unittest.TestCase):
    def test_validate_fails_when_evidence_binding_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = build_case(Path(temp_dir), "missing-evidence-binding")
            evidence_path = output_root / "evidence" / "evidence-log.csv"
            evidence_path.write_text(
                "evidence_id,source_type,source_name,source_url_or_path,local_asset_path,captured_at,claim_supported,evidence_strength,status,used_in_section,figure_number,notes\n"
                "EV001,fixture,Demo Fixture,fixtures/demo-product/prd.md,,2026-03-13,only text,strong,ready,第一章,图 1-1,missing image binding\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(RUNNER), "validate", "--output-root", str(output_root), "--json"],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["strict_errors"])
            self.assertIn("referenced asset is not registered in evidence log", joined)

    def test_validate_fails_when_report_references_missing_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = build_case(Path(temp_dir), "missing-image")
            prd_path = output_root / "prd.md"
            prd_path.write_text(
                "# Broken\n\n![missing](images/not-found.svg)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(RUNNER), "validate", "--output-root", str(output_root), "--json"],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["asset_validator_exit_code"], 1)
            self.assertIn("MISSING", payload["asset_validator_stdout"])

    def test_validate_fails_when_placeholder_remains(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = build_case(Path(temp_dir), "placeholder-left")
            html_path = output_root / "html" / "page-prototype.html"
            html_path.write_text(
                html_path.read_text(encoding="utf-8") + "\n<p>[页面名]</p>\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(RUNNER), "validate", "--output-root", str(output_root), "--json"],
                cwd=SKILL_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["strict_errors"])
            self.assertIn("placeholder content remains", joined)


if __name__ == "__main__":
    unittest.main()
