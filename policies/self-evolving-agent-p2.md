# 自进化 Agent（P2 北极星 · ACE 写回 + ADAS/DGM）

这是整个 AI 能力升级路线图的**北极星**——把 `/经验写回` 从"人手整篇重写文档"升级为**评估驱动的演化闭环**。它依赖 P0 的评测脊椎（`agent-trajectory-eval.md`）就位、并积累一定真实运行数据后启用。分两级：**ACE 式增量写回（近期可落地为协议+流程）** 与 **ADAS/DGM 式自动 agent 设计（研究前沿，需沙箱+算力，最远）**。

> 来源 `findings/01`（ADAS/DGM）+ `findings/06`（ACE）+ `findings/11`（GEPA）+ `findings/09`（eval）。是 SYNTHESIS §4 闭环的"自我进化"升级。

---

## 0. 为什么要它（现状的病根）

当前 `/经验写回` 是"全量重写文档 + 契约存在性测试"——有两个病：
1. **brevity bias / context collapse**：整篇重写会丢细节、把演化过的经验压扁。
2. **无质量信号**：契约测试只验"存在"，不验"是否真变好"。
ACE 用**增量 delta + 角色分工 + 计数**治第一个；评测脊椎（With-skill vs Baseline）治第二个。

## 1. ACE 式增量写回（三角色 + delta，近期可落地）

把 `/经验写回` 重构为 **Generator / Reflector / Curator** 三角色（可由主代理分阶段扮演，非必须多代理）：

| 角色 | 职责 |
|---|---|
| **Generator** | 产出本次任务的执行轨迹（做了什么、哪步有效/失败） |
| **Reflector** | 对比成功/失败，提炼可复用洞见（为什么有效、边界在哪） |
| **Curator** | 把洞见转成对 skills/policies 的**局部增量更新（delta）**，不整篇重写；维护 **helpful / harmful 计数**，去重剪枝 |

- **增量 delta**：每条经验是"加一条/改一条/标失效"，带 `helpful/harmful` 计数与 `date_added`；计数低/过期的剪枝（接 `memory-protocol.md` 遗忘）。
- **执行反馈驱动**：每次写回附 **With-skill vs Baseline 量化 + pass@k**（`agent-trajectory-eval.md`），关键指标回归即拒绝该 delta（接 `agentops-lifecycle.md` 的 eval 门禁）。

## 2. 触发判定

| 触发条件 | 启用 |
|---|---|
| `agent-trajectory-eval.md` 评测脊椎已用、有 ≥1 个能力的 baseline 与轨迹数据 | §1 ACE 增量写回 |
| 想自动搜索 agent 架构/工作流、且有沙箱+eval+算力 | §3 ADAS/DGM（最远） |
| 数据不足 / 无 baseline | 维持现有 `/经验写回`（人审、整理式） |

## 3. ADAS / DGM 式自动 agent 设计（最远北极星，强护栏）

- **ADAS**：固定 meta-agent 自动**生成/迭代**下游 agent 设计，按基准评分反馈择优。
- **AFlow**：把 agentic workflow 表示为代码，用 MCTS 搜最优工作流。
- **DGM（Darwin Gödel Machine）**：agent **自重写代码**变更好（存档 + 开放式进化 + 安全护栏）。
- 本仓库路径：待 §1 + 沙箱（`codeact-execution-p2.md`）+ eval 基建成熟后，试 **ADAS-lite**——meta 步提候选改法 → `run_eval.py` 自动评分 → 择优 → **仍走人审 + 安全扫描 + red-team 合并门禁**（借鉴 DGM 的存档/护栏，绝不无人值守自改）。

## 4. 与本仓库接线
- `agentops-lifecycle.md` 的 build 阶段、`submission-review-contract.md` 写回评审、`prompt-optimization-protocol.md`（GEPA 自动优化）共同构成这条闭环。
- 安全红线：自进化产物**必过** `red-team-checklist.md` + `/安全扫描` + 人审，绝不自动合并到主干。

## 何时查阅
- 评测脊椎已就位、要升级 `/经验写回` → §1（ACE 增量写回）
- 远期探索自动 agent 设计 → §3（强护栏、人审兜底）
