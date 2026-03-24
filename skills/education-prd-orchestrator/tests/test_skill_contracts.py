import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractsTest(unittest.TestCase):
    def test_portable_runtime_files_exist(self):
        expected = [
            "SKILL.md",
            "README.md",
            "requirements.txt",
            "scripts/README.md",
            "scripts/run_pipeline.py",
            "scripts/init_product_planning_delivery.py",
            "scripts/bootstrap_product_planning_tools.py",
            "scripts/bootstrap-macos.sh",
            "scripts/export_svg_to_png.py",
            "scripts/eppo/cli.py",
            "scripts/eppo/runtime.py",
            "scripts/eppo/validators.py",
            "examples/portable-benchmark/README.md",
            "fixtures/demo-product/prd.md",
            "assets/html-page-template.html",
            "assets/chart-template.html",
            "assets/search-plan-template.md",
            "assets/evidence-log-template.csv",
            "references/evidence-rules.md",
            "references/html-design-rules.md",
            "references/visualization-protocol.md",
        ]
        for relative in expected:
            self.assertTrue((SKILL_ROOT / relative).exists(), f"缺少文件: {relative}")

    def test_docs_mention_bootstrap_and_pipeline(self):
        for relative in ["SKILL.md", "README.md", "scripts/README.md"]:
            text = (SKILL_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("bootstrap_product_planning_tools.py", text)
            self.assertIn("run_pipeline.py", text)


if __name__ == "__main__":
    unittest.main()
