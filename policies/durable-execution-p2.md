# 持久化执行（P2 · 状态文件近似优先，durable runtime 触发式）

这是 `orchestration-runtime.md` 恢复协议的延伸。结论先行：**状态账本文件做的"应用级断点续跑"已覆盖 ~80% 需求**；只有出现"超长程 + 跨进程 + 强一致事务"硬需求才上 Temporal/DBOS 这类 durable runtime（重运维，与轻量定位冲突，谨慎）。

> 来源 `findings/02-multi-agent-orchestration.md`。因 LLM 成本/时长/可靠性，"无 durable 的生产代理几乎不可行"——但本仓库是 Cursor 原生单用户编排，文件级近似足矣。

---

## 1. 默认：状态文件断点续跑（已落地）

`orchestration-runtime.md` 的 `tasks/{task}/.meta/orchestration-state.md`（Task/Progress 双账本）= 轻量 checkpointer：
- 主代理**每批次先写状态再继续**；中断/换会话后**开工读状态续跑**，不重复已完成步。
- 这是 journal/checkpoint 思想的文件级实现，**零依赖**，覆盖绝大多数中断恢复。

## 2. 触发判定：何时才需要真 durable runtime

| 触发条件 | 是否上 |
|---|---|
| 单用户、任务级、文件可记状态 | **否**（用 §1 即可） |
| 跨进程/跨服务、需 deterministic replay | 是 |
| 多步**强一致事务**、部分失败要原子回滚（Saga） | 是 |
| 超长程（小时/天级）、高并发、贵 token 不能重付 | 是 |

## 3. 选型（触发后）

| 运行时 | 特点 | 何时选 |
|---|---|---|
| **DBOS** | Postgres 原生、零新基建、状态入库 | 已有 Postgres、想零运维 |
| **Temporal** | 企业级标准、deterministic replay、重运维 | 大规模、跨服务、复杂重试/超时 |
| **Inngest / Restate** | 事件驱动 / 单二进制低延迟 | 中小 serverless / 有状态低延迟 |
| **Saga 补偿** | 多步部分失败自动补偿回滚 | 跨步骤事务要原子性 |

- HITL interrupt/resume 标准化（中断写状态→暂停→读状态续跑）已在 `orchestration-runtime.md` + `agent-safety-protocol.md`，是 durable 的轻量替身。

## 4. 与本仓库接线
- `orchestration-runtime.md` 恢复协议小节指向本文件；明确"状态文件为默认，durable runtime 为 P2 触发式选项，不引入框架依赖"。

## 何时查阅
- 长任务中断恢复 → §1（默认）
- 出现跨进程/强一致/超长程硬需求 → §2 判触发 → §3 选型
