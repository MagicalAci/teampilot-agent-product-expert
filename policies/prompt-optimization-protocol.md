# 自动 Prompt 优化协议（Prompt Optimization）

这是产品专家 Agent 的**从"人工调优"升级到"自动优化"的可执行路径**。本仓库 `/AI调优` 已做对了"形"——`tuning-report-template.md` 的 ASI 失败归因 + A/B(p/d) + Pareto + `prompt-vX.Y` 版本化，与 GEPA/DSPy 同构——但**全靠人手跑**。本协议定义"何时该上自动优化、怎么接、产物怎么管"。

> 细节编目见 `findings/11-prompt-optimization-structured-output.md`。手写提示技巧见 `prompt-engineering-techniques.md`（含结构化输出强约束）；评测基建见 `llm-eval-methodology.md` + `agent-trajectory-eval.md`；结构化产物契约见 `output-contract.md`。

---

## 1. 升级判据（什么时候从人工转自动）

满足任一即可考虑自动优化：
- 人工 `/AI调优` **≤5 轮仍未收敛**到达标线；
- 该 route 的**评测集 ≥ ~50 条**（自动优化需要足够信号）；
- **同类 prompt 反复调**（值得一次性自动搜索）。

否则继续人工迭代（轻、可控、零依赖），不为自动而自动。

## 2. 选型：GEPA 优先

| 方法 | 何时用 |
|---|---|
| **GEPA**（反思式遗传-帕累托进化） | 首选——少 rollouts、用文本反馈进化提示词，与我们的 ASI 归因天然契合 |
| **DSPy MIPROv2** | 指令 + 少样本示例都要联合优化、样本较多 |
| 仅人工（`/AI调优`） | 样本少 / 轻量 / 一次性 |

## 3. 指标契约（关键接口：复用已有资产）

自动优化器要求 metric 返回 **`score`（数值）+ `feedback`（文本）**。**`feedback` 直接复用 `tuning-report-template.md` 的 ASI 失败归因**（错误信息 / 推理日志 / 违反的判据）——这是我们已有资产到 GEPA 的天然接口，不用另造。

## 4. 产物与版本管理
- 优化后的 prompt 落 `prompt-vX.Y.md`，头部记：**自动优化器 / 预算（rollouts）/ 前后 A/B 对比 / 评测集与分数**（version→score 可追溯）。
- 不回退已验证有效的改动；Pareto 取舍（A 类提升却 B 类回退 → 保留两候选分别评估，不草率用单一总分合并）。
- 落地态：本仓库默认**人工驱动 + 把方法论文件化**，重场景才真的 `pip install dspy` 跑编译（属 `/AI脚本` 工程化产物侧的可选项，不强制）。

## 5. 与本仓库接线
- `skills/ai-planning-orchestrator/`：`/AI调优` 的"是否引入自动化调优"步链到本协议；`tuning-report-template.md` 第 7 节注明"metric feedback = ASI 归因"。
- registry / 运行时 A/B（Langfuse/PromptLayer）= P2 备忘（需平台基建，与 Cursor 原生权衡）。
- 北极星：`/经验写回` 升级为 ACE 式增量演化（交叉 `agentops-lifecycle.md` / `memory-protocol.md`）。

## 何时查阅
- 人工调优触顶、评测集够大 → §1–§3
- 管理优化后 prompt 版本 → §4
