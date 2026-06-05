# 编排运行时层（Orchestration Runtime）

这是产品专家 Agent 的**编排运行时层**——给 `agent-team-methodology.md` 的 6 种团队模式补上"**模式怎么跑 / 出错怎么办 / 中断怎么续**"的运行时语义。核心主张：**不引入 LangGraph/Temporal 等重运行时框架**，用"**状态账本文件 + 子代理契约 + 失败防护清单 + 恢复协议**"把运行时语义**文件化/提示化**（范本 = Microsoft Magentic-One 的双账本）。

> 细节编目见 `research/ai-capability-upgrade/findings/02-multi-agent-orchestration.md`（50 条 SOTA、MAST 失败分类法）。与 `agent-team-methodology.md` 第一部分（选哪种模式）互补：本文件定"模式的运行时怎么落"。

---

## 1. 状态账本（Task Ledger + Progress Ledger）

任何需要**多代理/多阶段**的任务，在 `tasks/{task}/.meta/orchestration-state.md`（或 `.json`）维护两块**状态文件**：

**Task Ledger（任务账本 = 目标与计划）**
- `目标`：本任务要达成什么（对照 brief.md）
- `已知事实`：已确认的关键信息/约束
- `计划`：分阶段步骤 + 每阶段派谁（单/多代理）
- `硬约束`：不能违反的边界（范围/口径/禁止项）

**Progress Ledger（进度账本 = 每批次 5 问，借 Magentic-One）**
每个批次/阶段结束追加一行，回答：
1. 是否完成？（完成判定见 `self-critique-and-grounding.md`）
2. 是否有进展？
3. **是否在原地打转（stall）？**
4. 下一步派谁（哪个子代理/能力）？
5. 给它的明确指令是什么？

---

## 2. stall 检测 → reset&replan

- 连续 **2–3 个批次"无进展或重复同样动作"** = stall → 触发 **reset&replan**：重写 Task Ledger 的计划（换思路，而非重复同一失败动作），与"最大重试 2–3、最多 5 轮"对齐。
- stall 计数超阈值仍无解 → **收敛出"当前最佳答案" + 标注未尽项**，不空转（防 MAST FM-1.5 不识别终止）。
- 与 `cost-discipline-methodology.md` 的预算护栏联动：超预算即收敛。

---

## 3. 恢复协议（轻量 checkpointer）

- 主代理**每批次结束先写状态文件**（先持久化再继续）。
- 任务被中断/上下文清空/换会话后，**开工第一步读 `orchestration-state.md` 续跑**，不重复已完成步（防 MAST FM-1.4 上下文丢失）。
- 这是"应用级断点续跑"，覆盖绝大多数需求；真需要 durable runtime（跨进程强一致事务）才评估 Temporal/DBOS（P2，与轻量定位冲突，谨慎）。

---

## 4. 子代理契约（Subagent Contract）

每次派子代理（`Task` 工具）必须带：

**输入契约**：`目标 / 已知事实 / 边界 / 明确不要做什么`（防 FM-2.3 跑偏）。
**输出契约**：`标准产物路径 / 结论 / 关键约束（我知道但主代理可能不知道的）/ 置信度 / 未决问题`。
- "关键约束"字段防 **FM-2.4 信息隐瞒**；"未决问题"逼迫 **FM-2.2 不确定即澄清**。

**所有权抉择（handoff vs agents-as-tools）**：
- **默认 agents-as-tools**：子代理只回主代理、主代理保留最终产出所有权并综合（合 write-heavy 强一致，本仓库默认）。
- **handoff（转移所有权）仅用于纯 triage/路由**：专家直接拥有下一回合回复。
- 单批并发 ≤ 4；子代理之间不直接通信，由主代理中转裁决。

---

## 5. 失败防护清单（MAST 三类，汇总/门禁强制）

借 **MAST**（Multi-Agent System Failure Taxonomy，14 模式 3 类；42% 是"系统设计/规范"问题而非模型能力）。汇总环节强制自查：

- **FC1 规范类**：每子代理有显式角色 + 终止条件；查状态账本**去重防步骤重复**；写账本**防状态丢失**。
- **FC2 对齐类**：不确定即向主代理/用户**澄清**；产物含"关键约束"**防隐瞒**；主代理**交叉核对**各子代理输出（防忽略输入与推理-行动错位）。
- **FC3 验证类**：reviewer 做**高层目标级验证**（对照 brief 目标，非只查"产物存在"）；走完成判定 checklist；**防过早终止**（见 `self-critique-and-grounding.md`）。

---

## 6. 单 vs 多代理 + read/write 判定（拆代理前先判）

- **write-heavy / 强一致**（PRD 成稿、SQL 口径、Demo 代码、AI 脚本）→ **优先单代理 + 工具/串行**，避免上下文碎片化与隐式决策冲突（Cognition《Don't Build Multi-Agents》）。
- **read-heavy / 可并行**（多平台调研、竞品扫描、海外舆情）→ 多代理 **fan-out/fan-in**。
- 多代理 ~15× token、单代理 ~4×——**只对高价值复杂任务划算**（接 `cost-discipline-methodology.md`）。

## 与本仓库接线
- `task-navigator.mdc` 预检判定块据 §6 标注每阶段"单/多代理（理由）"；多阶段任务生成并更新 `orchestration-state.md`。
- HITL 中断点标准化为"中断写状态→暂停→读状态续跑"（与 `agent-safety-protocol.md` 的高风险审批闸衔接）。

## 何时查阅
- 设计/复盘多代理协作、定状态与恢复 → §1–§3
- 派子代理、定 handoff/as-tool → §4
- 汇总门禁做失败防护 → §5；拆代理前 → §6
