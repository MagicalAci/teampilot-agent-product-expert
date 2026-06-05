# 单代理推理范式库（Agent Reasoning Paradigms）

这是产品专家 Agent 的**单代理推理范式库**——回答"**一个 Agent 在一步/一段任务里，该用哪种思考-行动控制流**"。它与 `agent-team-methodology.md` 互为**微观/宏观**：后者管"任务拆给几个代理、怎么协作"（团队级），本文件管"单个代理一步内怎么想、怎么做、怎么自纠"（推理级）。

> 来源蒸馏自业界共识与公开论文（Anthropic《Building Effective Agents》、ReAct、Self-Refine、Reflexion、ReWOO、CodeAct、test-time compute 等），技术名为通用知识；本文件只做**方法论目录 + 选型指引**。细节编目见 `research/ai-capability-upgrade/findings/01-agent-reasoning.md`（48 条 SOTA）。

---

## 0. 头号纪律：workflow 优先，按需加自主性

**能用确定性 workflow 解决，就别上自主 agent。**（Anthropic 行业共识）按需逐级放权，别一上来就给最大自主度。

**自主性分级**（由低到高，决定"谁说了算"）：

| 级 | 控制流 / 工具 / 终止由谁定 | 何时用 |
|---|---|---|
| L0 单步调用 | 全人预定义 | 分类/抽取/改写等确定性子任务 |
| L1 Workflow（提示链/路由） | 人定流程，模型填空 | 流程可预测、可线性分解 |
| L2 工具循环（ReAct） | 模型决定调哪个工具，人限边界 | 需边做边查、步数中等 |
| L3 自主 agent | 模型自定步骤/工具/终止 | 开放式、步数不定 |

**纪律**：默认从最低够用级起步；越往上越要配**预算护栏**（`cost-discipline-methodology.md`）+ **自检闸**（`self-critique-and-grounding.md`）+ **失败防护**（`orchestration-runtime.md`）。

---

## 1. 推理范式选择决策树

```
任务是确定性子任务（分类/抽取/改写/格式化）？
├── 是 → 单步调用（L0），别加循环
└── 否 → 步骤可预测、可线性分解？
        ├── 是 → Workflow：Prompt Chaining + 步间 gate（每步校验再进）
        └── 否 → 需要调工具/检索、边做边修正？
                ├── 是 → 可并行的独立取数多吗？
                │       ├── 多 → ReWOO / 并行工具（一次性规划 + 并行执行，省往返）
                │       └── 少 → ReAct（思考→行动→观察 循环）
                └── 否 → 需要先规划再执行（长链路、步骤较稳）？
                        ├── 是 → Plan-and-Execute（规划器出计划，执行器逐步，必要时重规划）
                        └── 否 → 需多路径择优 / 答案易抖？ → Self-Consistency / ToT（高算力换质量）
```

凡"生成后需把关质量"的，叠加 **Self-Refine / 反思**（见 §3 与 `self-critique-and-grounding.md`）。

---

## 2. 范式目录（何时用 / 与本仓库哪个能力匹配）

| 范式 | 一句话 | 何时用 | 本仓库匹配 |
|---|---|---|---|
| **Prompt Chaining** | 拆成顺序步骤，上一步输出喂下一步，中间设 gate | 步骤可预测 | PRD 章节流水线、调研 Phase 0–7 |
| **Routing** | 先分类输入再路由专门处理 | 输入类型多样 | 命令/意图路由（见 `intent-routing-and-dialog.md`） |
| **ReAct** | 交替"推理→行动→观察"循环 | 需调工具/检索、边做边修 | 调研采集、SQL 探查、多轮取证 |
| **Plan-and-Execute** | 先出计划再逐步执行（可重规划） | 长链路、步骤较稳 | PRD 成稿、Demo 开发、全景调研 |
| **ReWOO** | 一次性出带变量的计划，worker 并行执行无需每步问 LLM | 多工具、有并行度、省 token | 多平台采集汇总（与扇出/扇入配合） |
| **Self-Refine** | 自己产反馈→自己改，迭代精修 | 有明确质量维度、可迭代 | 五能力成稿前自检（统一走 `self-critique-and-grounding.md`） |
| **Reflexion-lite** | 失败后语言化反思写入记忆，下轮改进 | 可多次尝试、有成败信号 | 调优迭代、核查未通过的重做 |
| **Self-Consistency** | 同问多路径采样取多数 | 高风险判断、答案易抖 | SQL 口径、竞品定性、PRD 关键结论 |
| **CodeAct（脚本即动作）** | 用一段可执行脚本完成多步/批量工具操作 | 多步批量、可并行（需脚本环境） | aibi/research 流水线（P2，见 `tool-use-protocol.md`） |

---

## 3. 反思与"用算力换质量"

- **reflect-when-stuck（不要每步都反思）**：实证显示"每步都反思"收益不明显且贵；**只在自评不达标/受阻时**才进入反思修订。控成本。
- **Self-Refine 最大轮次 2–3**（与门禁"最多 5 轮"对齐），防无限循环；不达标则降级表达或转人工，而非空转。
- **test-time compute / 思考预算**：按任务难度选模型档与思考预算——简单确定性任务用轻量档/不开思考；复杂推理（规划、裁决、核查）才上高档/开思考。**高风险产出做 Self-Consistency 多采样取一致**。档位决策见 `cost-discipline-methodology.md` 的"模型分级决策表"，反思/接地的统一闸见 `self-critique-and-grounding.md`。

---

## 4. 与本仓库接线

- `.cursor/rules/task-navigator.mdc` 的"预检判定块"在分阶段规划时标注**每阶段用哪种推理范式（理由）**，引用本文件决策树。
- 出结论/成稿前统一过 `self-critique-and-grounding.md` 的自检闸。
- 团队级编排（拆几个代理）见 `agent-team-methodology.md`；编排运行时语义见 `orchestration-runtime.md`。

## 何时查阅
- 任务启动选推理模式 / 判断自主度 → §0–§1
- 写某能力的执行 SOP、决定"该不该上自主循环" → §1–§2
- 控反思与算力成本 → §3 + `cost-discipline-methodology.md`
