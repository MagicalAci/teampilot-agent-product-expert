# Agent 轨迹评估与可观测（Agent Trajectory Eval）

这是产品专家 Agent 的**闭环脊椎**——给 `llm-eval-methodology.md`（单轮 EDD：四桶/三类 grader/G-Eval/κ/pass@k/A-B/OTel 基础）补上它最缺的"**整条 run 的轨迹 / 完成判定 / 在线可观测**"。没有这一层，所有能力增强都无法量化证明"真的变好"，自我进化闭环就断裂。

> 与 `llm-eval-methodology.md` 分工：评测集/grader 分层/judge 校准/pass@k/A-B/OTel 基础 = `[对齐]` 那边、不重写；**Agent 轨迹评估 / 完成判定 judge / run-trace 可观测 / With-skill vs Baseline 闭环 = `[新增]` 本文件**。细节编目见 `findings/09-eval-observability.md`（73 条）。

---

## 1. 轨迹数据模型（从"单轮 output"到"多步 run"）

一条任务的产出不只是最终文本，而是一条**轨迹**：
```jsonc
{"id":"...", "route":"调研-单产品",
 "output": {"tool_calls":[{"name":"WebSearch","args":{"q":"..."}}, ...],
            "steps": ["plan","collect","analyze","verify"],
            "final":"...最终结论..."},
 "assertions":[{"type":"tool_called","value":"WebSearch"},
               {"type":"step_efficiency","value":8},
               {"type":"task_completion","dimension":"完成度","min_score":4}]}
```
`scripts/run_eval.py`（在 `skills/ai-planning-orchestrator/scripts/`）已扩展支持以下**轨迹 grader**：

| grader 类型 | 评什么 | value |
|---|---|---|
| `tool_called` | 该工具被调用过 | 工具名 或 名列表 |
| `tool_args_match` | 某工具以匹配参数被调用 | `{tool, args}`（args 子集匹配）|
| `tool_sequence` | 工具按序（子序列）被调用 | 工具名有序列表 |
| `step_efficiency` | 步数不超预算 | 最大步数（int）|
| `task_completion` | 任务是否完成（judge 或 completed 标志）| judge 量规；或输出含 `completed:true` |

## 2. 完成判定 + 轨迹 judge

- **完成判定**：对照 `brief.md` 目标的**高层验证**（非表层"产物存在"），统一走 `self-critique-and-grounding.md` 的 checklist；可编程的字段用 `json_schema_keys` 断言，开放式用 `task_completion` judge。
- **轨迹 judge 量规**：维度 = 完成度 / 工具选择正确 / 步骤效率 / 安全合规；judge 模型 ≠ 被测模型族，judge 用 ensemble 并报 TPR/TNR（接 `llm-eval-methodology.md` judge 合同）。
- verifier/PRM 近似：先用"LLM-judge 轻量过程检查 + reflect-when-stuck"近似过程级校验，不重训（P2 再评估 GenPRM/Agent-as-a-Judge）。

## 3. run-trace 可观测（最小约定，OTel-GenAI 风格）

任务过程记录到 `tasks/{task}/.meta/run-trace.jsonl`（**observability，非 enforcement**），span 名对齐 OTel GenAI：
- `invoke_agent` / `execute_tool` / `invoke_workflow`；字段含 `工具名 / 入参摘要 / 重试次数 / 是否 fallback / 预算用量 / 结果`。
- 与 `orchestration-runtime.md` 的状态账本、`cost-discipline-methodology.md` 的 `cost-log` 互补——一份记编排状态、一份记成本、一份记轨迹。
- 重平台（Langfuse/Phoenix）= P2 触发式，现在不引。

## 4. 闭环：With-skill vs Baseline（自我进化的标尺）

`/经验写回` 合并前，除现有契约测试（存在性），附 **With-skill vs Baseline 量化 + pass@k**：同一组任务带/不带新增 skill/policy 各跑，比分维度通过率 + Cohen's d（`run_eval.py` 已内置 baseline 回归 + A/B）。关键指标回归即阻断合并。这把"契约测试 = 存在性"升级为"质量评分"，是闭环成立的关键。

## 5. user simulator（多轮能力回归，P1）
受任务 slot schema 约束的"模拟用户"跑可复现多轮场景，按 end-state（是否满足 brief）+ 过程信号（是否触发正确澄清/未过度追问/是否引导成功）评分（借 τ²-bench 思想），产物喂 `run_eval.py`。

## 与本仓库接线
- 评测台 `skills/ai-planning-orchestrator/scripts/run_eval.py` 已加 §1 的轨迹 grader。
- `submission-review-contract.md` / `agentops-lifecycle.md`（P1）的 eval 门禁引用本文件；`/AI评测`、`/AI调优` 复用。

## 何时查阅
- 评 agent 的轨迹/工具/完成度 → §1–§2
- 记 run-trace 可观测 → §3；自我进化量化 → §4
