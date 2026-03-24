import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNNER = SKILL_ROOT / "scripts" / "run_pipeline.py"
FIXTURE_ROOT = SKILL_ROOT / "fixtures" / "demo-product"


def mark_final_delivery_ready(output_root: Path) -> None:
    (output_root / "05-synthesis" / "REVIEW_GATE.md").write_text(
        """# 审核门禁

## 采集门禁

| 轮次 | 审核代理 | 结论 | 打回给谁 | 原因 | 是否放行 |
|---|---|---|---|---|---|
| 1 | `research-review` | `通过` |  | `fixture smoke test` | `是` |

## 成稿门禁

- `WRITING_PLAN.md` 章节状态：`ready`
- `FACTCHECK_PLAN.md` 章节校验：`ready`
- `VISUAL_PLAN.md` 图证回填：`ready`
- `07-factcheck/round-1.md`：`ready`
- `07-factcheck/round-2.md`：`ready`
- `07-factcheck/round-3.md`：`ready`
- `07-factcheck/final-status.md`：`ready`
- `04-experience/EXPERIENCE_REPORT.md`：`ready`
- 成稿放行：`是`
""",
        encoding="utf-8",
    )
    (output_root / "06-writing" / "WRITING_PLAN.md").write_text(
        """# 文档撰写计划

## 状态

- all chapters: `done`
- visuals: `done`
- factcheck: `done`
""",
        encoding="utf-8",
    )
    (output_root / "07-factcheck" / "FACTCHECK_PLAN.md").write_text(
        """# 三轮事实核查计划

## 章节事实校验总表

| 章节 | 强判断校验 | 角标校验 | 图文对应 | 图片路径校验 | 中文化校验 | 是否通过 | 问题摘要 |
|---|---|---|---|---|---|---|---|
| `2. 分析建模` | `pass` | `pass` | `pass` | `pass` | `pass` | `yes` | `ok` |
""",
        encoding="utf-8",
    )
    (output_root / "08-visuals" / "VISUAL_PLAN.md").write_text(
        """# 可视化规划

## 章节配图总表

| 章节 | 判断点 | 是否必须有真实图 | 可用素材路径 | 应补图类型 | 推荐版式 | 图号 | 图注草案 | 插入位置 | 当前状态 |
|---|---|---|---|---|---|---|---|---|---|
| `3. 产品分析` | `双端口入口承接差异` | `是` | `04-experience/screenshots/example.png` | `真实截图` | `对比板` | `图 3-1` | `已回填` | `3.1 后` | `done` |
""",
        encoding="utf-8",
    )
    (output_root / "07-factcheck" / "final-status.md").write_text(
        """# 成稿终审状态

- 三轮核查是否完成：`是`
- 图证覆盖是否完成：`是`
- 章节事实校验是否完成：`是`
- 成稿放行：`是`
- 终审备注：`ok`
""",
        encoding="utf-8",
    )


class PipelineSmokeTest(unittest.TestCase):
    def test_init_seeds_experience_and_factcheck_templates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            case_root = temp_root / "demo-product"
            shutil.copytree(FIXTURE_ROOT, case_root)

            task_card_path = case_root / "task-card.json"
            task_card = json.loads(task_card_path.read_text(encoding="utf-8"))
            task_card["task_slug"] = "demo-product-init-check"
            output_root = temp_root / "outputs" / task_card["product_slug"]
            task_card["output_root"] = str(output_root)
            task_card_path.write_text(
                json.dumps(task_card, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(RUNNER), "init", "--task-card", str(task_card_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

            self.assertTrue((output_root / "04-experience" / "EXPERIENCE_REPORT.md").exists())
            self.assertTrue((output_root / "07-factcheck" / "round-1.md").exists())
            self.assertTrue((output_root / "07-factcheck" / "round-2.md").exists())
            self.assertTrue((output_root / "07-factcheck" / "round-3.md").exists())
            self.assertTrue((output_root / "07-factcheck" / "final-status.md").exists())

    def test_full_pipeline_smoke(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            case_root = temp_root / "demo-product"
            shutil.copytree(FIXTURE_ROOT, case_root)

            task_card_path = case_root / "task-card.json"
            task_card = json.loads(task_card_path.read_text(encoding="utf-8"))
            task_card["task_slug"] = "demo-product-smoke"
            output_root = temp_root / "outputs" / task_card["product_slug"]
            external_report_path = temp_root / "reports" / "should-not-be-used.md"
            task_card["output_root"] = str(output_root)
            task_card["report_path"] = str(external_report_path)
            task_card_path.write_text(
                json.dumps(task_card, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            for command in ["init", "collect", "analyze", "export", "validate"]:
                if command == "export":
                    mark_final_delivery_ready(output_root)
                result = subprocess.run(
                    [sys.executable, str(RUNNER), command, "--task-card", str(task_card_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

            self.assertTrue((output_root / "exports" / "report-context.json").exists())
            self.assertTrue((output_root / "exports" / "evidence-summary.csv").exists())
            self.assertTrue((output_root / "03-platforms" / "appstore" / "summary.md").exists())
            self.assertTrue((output_root / "03-platforms" / "appstore" / "data.csv").exists())
            self.assertTrue((output_root / "03-platforms" / "xiaohongshu" / "summary.md").exists())
            self.assertTrue((output_root / "03-platforms" / "xiaohongshu" / "data.csv").exists())
            self.assertFalse((output_root / "03-platforms" / "social").exists())
            report_path = output_root / "06-writing" / f"{task_card['task_slug']}.md"
            self.assertTrue(report_path.exists())
            self.assertFalse(external_report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("## 2. 分析建模", report_text)
            self.assertIn("待回填", report_text)

    def test_export_requires_final_delivery_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            case_root = temp_root / "demo-product"
            shutil.copytree(FIXTURE_ROOT, case_root)

            task_card_path = case_root / "task-card.json"
            task_card = json.loads(task_card_path.read_text(encoding="utf-8"))
            task_card["task_slug"] = "demo-product-final-gate"
            output_root = temp_root / "outputs" / task_card["product_slug"]
            task_card["output_root"] = str(output_root)
            task_card_path.write_text(
                json.dumps(task_card, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            for command in ["init", "collect", "analyze"]:
                result = subprocess.run(
                    [sys.executable, str(RUNNER), command, "--task-card", str(task_card_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

            review_gate_path = output_root / "05-synthesis" / "REVIEW_GATE.md"
            review_gate_path.write_text(
                """# 审核门禁

## 采集门禁

| 轮次 | 审核代理 | 结论 | 打回给谁 | 原因 | 是否放行 |
|---|---|---|---|---|---|
| 1 | `research-review` | `通过` |  | `fixture smoke test` | `是` |
""",
                encoding="utf-8",
            )

            export_result = subprocess.run(
                [sys.executable, str(RUNNER), "export", "--task-card", str(task_card_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(export_result.returncode, 0)
            self.assertIn("成稿门禁", export_result.stdout + export_result.stderr)

    @unittest.skipUnless(sys.platform == "darwin", "bootstrap-macos.sh smoke test requires macOS")
    def test_bootstrap_standalone_smoke_from_copied_skill_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            copied_skill_root = temp_root / "single-product-competitor-analysis"
            shutil.copytree(SKILL_ROOT, copied_skill_root)

            case_root = temp_root / "demo-product"
            shutil.copytree(copied_skill_root / "fixtures" / "demo-product", case_root)

            task_card_path = case_root / "task-card.json"
            task_card = json.loads(task_card_path.read_text(encoding="utf-8"))
            task_card["task_slug"] = "copied-bootstrap-smoke"
            output_root = temp_root / "outputs" / task_card["product_slug"]
            task_card["output_root"] = str(output_root)
            task_card_path.write_text(
                json.dumps(task_card, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            fake_ffmpeg = temp_root / "fake-ffmpeg"
            fake_ffmpeg.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_ffmpeg.chmod(0o755)

            stub_root = temp_root / "py-stubs" / "jsonschema"
            stub_root.mkdir(parents=True, exist_ok=True)
            (stub_root / "__init__.py").write_text(
                "class Draft202012Validator:\n"
                "    def __init__(self, schema):\n"
                "        self.schema = schema\n\n"
                "    def iter_errors(self, payload):\n"
                "        return []\n",
                encoding="utf-8",
            )

            bootstrap = copied_skill_root / "scripts" / "bootstrap-macos.sh"
            env = os.environ.copy()
            env["SPCA_SKIP_SYSTEM_INSTALL"] = "1"
            env["SPCA_SKIP_PIP_SYNC"] = "1"
            env["SPCA_REQUIREMENTS_FILE"] = str(temp_root / "missing-requirements.txt")
            env["SPCA_MANAGED_ROOT"] = str(temp_root / ".managed-runtime")
            env["SPCA_FFMPEG_BIN"] = str(fake_ffmpeg)
            env["PYTHONPATH"] = (
                f"{temp_root / 'py-stubs'}:{env['PYTHONPATH']}"
                if env.get("PYTHONPATH")
                else str(temp_root / "py-stubs")
            )

            doctor_result = subprocess.run(
                ["bash", str(bootstrap), "doctor"],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(doctor_result.returncode, 0, msg=doctor_result.stderr or doctor_result.stdout)

            for command in ["init", "collect", "analyze", "export", "validate"]:
                if command == "export":
                    mark_final_delivery_ready(output_root)
                result = subprocess.run(
                    ["bash", str(bootstrap), command, "--task-card", str(task_card_path)],
                    capture_output=True,
                    text=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

            self.assertFalse((Path(env["SPCA_MANAGED_ROOT"]) / "requirements.sha256").exists())
            self.assertTrue((Path(env["SPCA_MANAGED_ROOT"]) / "logs" / "doctor.json").exists())
            self.assertTrue((output_root / "exports" / "validation-result.json").exists())


if __name__ == "__main__":
    unittest.main()
