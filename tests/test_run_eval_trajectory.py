"""run_eval.py 轨迹 grader 的真实执行测试（闭环脊椎验证）。

不只检查 run_eval.py 含标记，而是**实际运行**新轨迹 grader
（tool_called/tool_args_match/tool_sequence/step_efficiency/task_completion）
在样例轨迹评测集上，断言通过率、回归检测与 A/B 机制真能工作。
"""

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_EVAL = REPO_ROOT / "skills" / "ai-planning-orchestrator" / "scripts" / "run_eval.py"
EVAL_DIR = REPO_ROOT / "research" / "ai-capability-upgrade" / "eval"


def _load():
    spec = importlib.util.spec_from_file_location("run_eval", RUN_EVAL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


re_mod = _load()


class TrajectoryGraderTest(unittest.TestCase):
    def test_individual_trajectory_graders(self):
        traj = {
            "tool_calls": [
                {"name": "WebSearch", "args": {"q": "x"}},
                {"name": "sql_query", "args": {"db": "sparklab_starcard"}},
            ],
            "steps": ["a", "b", "c"],
            "completed": True,
        }
        cases = [
            ({"type": "tool_called", "value": "WebSearch"}, True),
            ({"type": "tool_called", "value": "missing_tool"}, False),
            ({"type": "tool_args_match", "value": {"tool": "sql_query", "args": {"db": "sparklab_starcard"}}}, True),
            ({"type": "tool_args_match", "value": {"tool": "sql_query", "args": {"db": "wrong"}}}, False),
            ({"type": "tool_sequence", "value": ["WebSearch", "sql_query"]}, True),
            ({"type": "tool_sequence", "value": ["sql_query", "WebSearch"]}, False),
            ({"type": "step_efficiency", "value": 5}, True),
            ({"type": "step_efficiency", "value": 2}, False),
            ({"type": "task_completion"}, True),
        ]
        for assertion, expected in cases:
            ok, _ = re_mod.grade_assertion(traj, assertion, None, {})
            with self.subTest(assertion=assertion):
                self.assertEqual(ok, expected, f"{assertion} 期望 {expected} 实得 {ok}")

    def test_baseline_dataset_all_pass(self):
        cases = re_mod.load_dataset(EVAL_DIR / "sample-trajectory.jsonl")
        result = re_mod.evaluate(cases, None)
        self.assertEqual(result["summary"]["graded_cases"], 3)
        self.assertEqual(result["summary"]["pass_rate"], 1.0)

    def test_regressed_dataset_detects_failure_and_regression(self):
        baseline = re_mod.evaluate(re_mod.load_dataset(EVAL_DIR / "sample-trajectory.jsonl"), None)
        regressed = re_mod.evaluate(re_mod.load_dataset(EVAL_DIR / "sample-trajectory-regressed.jsonl"), None)
        self.assertLess(regressed["summary"]["pass_rate"], 1.0)
        failed_ids = {f["id"] for f in regressed["failures"]}
        self.assertIn("rtk-001", failed_ids)
        cmp = re_mod.compare_baseline(regressed, baseline, 0.05)
        self.assertTrue(cmp["has_regression"], "退化版应被检出回归")


if __name__ == "__main__":
    unittest.main()
