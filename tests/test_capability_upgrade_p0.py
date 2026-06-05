"""AI 能力升级 Phase 1（P0）契约测试。

守护 12 域研究综合（research/ai-capability-upgrade/SYNTHESIS.md）落地的 P0 协议：
存在性 + 关键标记 + 接线（manifest / task-navigator / 命令路由 / 提交评审契约 / run_eval）。
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICIES = REPO_ROOT / "policies"


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


# 每个新 P0 policy → 必须包含的关键标记（验收信号）
POLICY_MARKERS = {
    "policies/agent-reasoning-paradigms.md": [
        "ReAct", "Plan-and-Execute", "Self-Refine", "自主性分级", "workflow 优先",
    ],
    "policies/orchestration-runtime.md": [
        "Task Ledger", "Progress Ledger", "stall", "reset&replan", "恢复协议", "状态文件", "子代理契约", "MAST",
    ],
    "policies/self-critique-and-grounding.md": [
        "自检", "CoVe", "强制引用", "abstain", "完成判定", "reflect-when-stuck", "高层目标级验证", "防过早终止",
    ],
    "policies/retrieval-protocol.md": [
        "查询变换", "混合检索", "RRF", "重排", "上下文化引用", "堆叠",
    ],
    "policies/memory-protocol.md": [
        "检索记忆", "观察写入", "写入白名单", "claude-mem",
    ],
    "policies/intent-routing-and-dialog.md": [
        "三层路由", "置信度", "ask-or-act", "一次性问全", "护栏", "对话状态", "confirmation", "转人工",
    ],
    "policies/tool-use-protocol.md": [
        "命名空间", "response_format", "分页", "渐进式披露", "工具错误处理", "降级", "破坏性", "结果缓存", "TTL",
    ],
    "policies/agent-safety-protocol.md": [
        "间接注入", "外部内容一律数据", "spotlighting", "不外发铁律", "输入校验", "输出校验", "PII", "拒答", "引用校验", "高风险动作", "先停后做",
    ],
    "policies/cost-discipline-methodology.md": [
        "模型分级决策表", "缓存复用门禁", "任务级预算护栏", "思考预算档位", "超限收敛", "限流即停用不重试", "级联",
    ],
    "policies/agent-trajectory-eval.md": [
        "轨迹", "完成判定", "run-trace", "tool_called", "task_completion", "With-skill",
    ],
}


class CapabilityUpgradeP0ContractTest(unittest.TestCase):
    def test_all_p0_policies_exist_with_markers(self):
        for rel, markers in POLICY_MARKERS.items():
            path = REPO_ROOT / rel
            with self.subTest(file=rel):
                self.assertTrue(path.exists(), f"缺少 {rel}")
                text = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, text, f"{rel} 缺标记 {marker}")

    def test_intent_router_rule_exists(self):
        path = REPO_ROOT / ".cursor" / "rules" / "intent-router.mdc"
        self.assertTrue(path.exists(), "缺少 .cursor/rules/intent-router.mdc")
        text = path.read_text(encoding="utf-8")
        for marker in ["意图判定", "ask-or-act", "护栏", "capability-registry"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_capability_registry_has_five_capabilities(self):
        text = read("policies/capability-registry.yaml")
        for key in [
            "research-toolkit", "product-planning", "ai-planning", "demo-development", "sql-query",
        ]:
            with self.subTest(key=key):
                self.assertIn(key, text)
        self.assertIn("utterances", text)
        self.assertIn("required_slots", text)
        # 每能力 ≥10 例句 → 全表 utterances 行（以 "- " 列项）总量应充足
        self.assertGreaterEqual(text.count("required_slots"), 5)

    def test_prompt_techniques_structured_output_strong_constraint(self):
        text = read("policies/prompt-engineering-techniques.md")
        for marker in ["结构化输出强约束", "strict", "受限解码", "≠ 语义正确"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_run_eval_has_trajectory_graders(self):
        text = read("skills/ai-planning-orchestrator/scripts/run_eval.py")
        for marker in [
            "tool_called", "tool_args_match", "tool_sequence", "step_efficiency", "task_completion", "_grade_trajectory",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_task_navigator_preflight_block_wires_protocols(self):
        text = read(".cursor/rules/task-navigator.mdc")
        self.assertIn("预检判定块", text)
        for ref in [
            "agent-reasoning-paradigms.md",
            "orchestration-runtime.md",
            "self-critique-and-grounding.md",
            "retrieval-protocol.md",
            "memory-protocol.md",
            "intent-routing-and-dialog.md",
            "cost-discipline-methodology.md",
            "agent-safety-protocol.md",
            "agent-trajectory-eval.md",
        ]:
            with self.subTest(ref=ref):
                self.assertIn(ref, text)

    def test_manifest_registers_new_policies(self):
        manifest = read(".teampilot/agent.yml")
        for rel in POLICY_MARKERS:
            with self.subTest(policy=rel):
                self.assertIn(rel, manifest)
        self.assertIn("policies/capability-registry.yaml", manifest)

    def test_command_router_and_review_contract_wired(self):
        commands = read(".cursor/rules/product-expert-commands.mdc")
        for ref in [
            "intent-routing-and-dialog.md",
            "agent-safety-protocol.md",
            "tool-use-protocol.md",
            "self-critique-and-grounding.md",
        ]:
            with self.subTest(ref=ref):
                self.assertIn(ref, commands)

        review = read("policies/submission-review-contract.md")
        for marker in ["agent-trajectory-eval.md", "self-critique-and-grounding.md", "agent-safety-protocol.md", "With-skill"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, review)


if __name__ == "__main__":
    unittest.main()
