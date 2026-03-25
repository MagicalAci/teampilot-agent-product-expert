import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from rtk.cli import file_marks_ready, final_delivery_gate_status  # noqa: E402


class SkillContractsTest(unittest.TestCase):
    def test_task_card_template_exists_and_has_minimum_fields(self):
        template_path = SKILL_ROOT / "task-card.template.json"
        self.assertTrue(template_path.exists(), "缺少 task-card.template.json")

        payload = json.loads(template_path.read_text(encoding="utf-8"))
        self.assertIn("product_name", payload)
        self.assertIn("analysis_goal", payload)
        self.assertIn("output_root", payload)
        self.assertIn("imports_root", payload)
        self.assertIn("manual_root", payload)

    def test_benchmark_passes_current_final_delivery_gate(self):
        benchmark_root = SKILL_ROOT / "examples" / "doubao-aixue-benchmark"
        ok, blockers = final_delivery_gate_status(
            {
                "synthesis_root": benchmark_root / "05-synthesis",
                "experience_root": benchmark_root / "04-experience",
                "writing_root": benchmark_root / "06-writing",
                "factcheck_root": benchmark_root / "07-factcheck",
                "visuals_root": benchmark_root / "08-visuals",
            }
        )
        self.assertTrue(ok, "\n".join(blockers))

    def test_file_marks_ready_rejects_chinese_pending_markers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "status.md"
            path.write_text("已按新骨架重排，待补关键原话\n", encoding="utf-8")
            self.assertFalse(file_marks_ready(path))

    def test_bootstrap_docs_exist_and_use_bootstrap_entry(self):
        first_run_doc = SKILL_ROOT / "references" / "first-run-bootstrap.md"
        self.assertTrue(first_run_doc.exists(), "缺少首启协议文档")

        for relative_path in [
            "README.md",
            "SKILL.md",
            "examples.md",
            "protocols" + "/" + "tooling-and-installation.md",
        ]:
            text = (SKILL_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertTrue(
                "bootstrap" in text,
                f"{relative_path} 未声明 bootstrap 首入口",
            )

    def test_installation_protocol_mentions_doctor_statuses(self):
        protocol = (SKILL_ROOT / "protocols" / "tooling-and-installation.md").read_text(encoding="utf-8")
        for marker in ["已安装", "需安装", "需登录初始化", "当前降级模式"]:
            self.assertIn(marker, protocol)


if __name__ == "__main__":
    unittest.main()
