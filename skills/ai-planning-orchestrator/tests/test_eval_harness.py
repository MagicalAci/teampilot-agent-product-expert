import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
ASSETS = SKILL_ROOT / "assets"
RUN_EVAL = SCRIPTS / "run_eval.py"
AGGREGATE = SCRIPTS / "aggregate_eval_dataset.py"
GEN_REPORT = SCRIPTS / "gen_eval_report.py"
INIT = SCRIPTS / "init_ai_planning_delivery.py"
VALIDATE = SCRIPTS / "validate_ai_planning_assets.py"
TEMPLATE_DATASET = ASSETS / "eval-dataset-template.jsonl"


def _run(args, **kwargs):
    return subprocess.run(
        [sys.executable, *args],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )


class EvalHarnessTest(unittest.TestCase):
    def test_aggregate_template_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            merged = Path(tmp) / "merged.jsonl"
            report = Path(tmp) / "health.md"
            res = _run(
                [str(AGGREGATE), str(TEMPLATE_DATASET), "--out", str(merged), "--report", str(report)]
            )
            self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
            payload = json.loads(res.stdout)
            self.assertEqual(payload["total"], 6)
            self.assertEqual(payload["errors"], [])
            self.assertEqual(set(payload["by_bucket"]), {"production", "adversarial", "edge", "failure_replay"})
            self.assertTrue(merged.exists())
            self.assertTrue(report.exists())

    def test_run_eval_pass_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.md"
            result = Path(tmp) / "result.json"
            res = _run(
                [str(RUN_EVAL), "--dataset", str(TEMPLATE_DATASET),
                 "--report", str(report), "--result", str(result)]
            )
            self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
            summary = json.loads(res.stdout)
            self.assertEqual(summary["pass_rate"], 1.0)
            self.assertEqual(summary["graded_cases"], 6)
            self.assertFalse(summary["has_regression"])
            self.assertTrue(report.exists())
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertIn("summary", data)
            self.assertIn("by_dimension", data)
            self.assertIn("failure_clusters", data)

    def test_run_eval_detects_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.json"
            # 先建基线
            base = _run([str(RUN_EVAL), "--dataset", str(TEMPLATE_DATASET), "--result", str(baseline)])
            self.assertEqual(base.returncode, 0, msg=base.stdout + base.stderr)

            # 构造回退数据集：让一条用例失败
            regressed = Path(tmp) / "regressed.jsonl"
            lines = TEMPLATE_DATASET.read_text(encoding="utf-8").splitlines()
            new_lines = []
            for line in lines:
                if not line.strip():
                    continue
                case = json.loads(line)
                if case.get("id") == "demo-fail-001":
                    case["output"] = "需要收取手续费。"  # 触发 not_contains 失败
                new_lines.append(json.dumps(case, ensure_ascii=False))
            regressed.write_text("\n".join(new_lines), encoding="utf-8")

            res = _run([str(RUN_EVAL), "--dataset", str(regressed), "--baseline", str(baseline)])
            self.assertEqual(res.returncode, 1, msg=res.stdout + res.stderr)
            summary = json.loads(res.stdout)
            self.assertTrue(summary["has_regression"])
            self.assertLess(summary["pass_rate"], 1.0)

    def test_run_eval_fail_under_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            # fail-under 高于实际通过率 → 退出码 1
            res = _run([str(RUN_EVAL), "--dataset", str(TEMPLATE_DATASET), "--fail-under", "1.1"])
            self.assertEqual(res.returncode, 1, msg=res.stdout + res.stderr)

    def test_gen_report_and_tuning_skeleton(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "result.json"
            _run([str(RUN_EVAL), "--dataset", str(TEMPLATE_DATASET), "--result", str(result)])
            report = Path(tmp) / "r.md"
            skeleton = Path(tmp) / "tune.md"
            res = _run(
                [str(GEN_REPORT), "--result", str(result),
                 "--report", str(report), "--tuning-skeleton", str(skeleton)]
            )
            self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
            self.assertTrue(report.exists())
            self.assertTrue(skeleton.exists())
            self.assertIn("失败归因", skeleton.read_text(encoding="utf-8"))

    def test_init_with_eval_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            slug = "demo-eval"
            init = _run(
                [str(INIT), slug, "--title", "评测Demo", "--output-dir", str(out),
                 "--with-eval", "--overwrite"]
            )
            self.assertEqual(init.returncode, 0, msg=init.stdout + init.stderr)
            strategy = out / f"{slug}-prompt-strategy-card.md"
            eval_report = out / f"{slug}-eval-report.md"
            tuning_report = out / f"{slug}-tuning-report.md"
            dataset = out / f"{slug}-eval-dataset.jsonl"
            for p in (strategy, eval_report, tuning_report, dataset):
                self.assertTrue(p.exists(), p)

            val = _run(
                [str(VALIDATE),
                 "--strategy-card", str(strategy),
                 "--eval-report", str(eval_report),
                 "--tuning-report", str(tuning_report),
                 "--eval-dataset", str(dataset)]
            )
            self.assertEqual(val.returncode, 0, msg=val.stdout + val.stderr)
            payload = json.loads(val.stdout)
            for name, summary in payload["documents"].items():
                with self.subTest(document=name):
                    self.assertTrue(summary["exists"])
                    self.assertEqual(summary["missing_headings"], [])
            self.assertEqual(payload["eval_dataset"]["errors"], [])


if __name__ == "__main__":
    unittest.main()
