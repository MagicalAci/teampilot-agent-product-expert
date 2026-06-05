# AI 能力升级 · 总综合：增强路线图与自我进化闭环

> 本文件综合 `findings/01–12`（12 域、共 ~700 条带出处 SOTA 技术编目）的"对标 + 落地建议"，回答用户的核心诉求：**我们要怎么增强、完善、闭环**。
> 阅读顺序：先看 §1 一页结论 → §2 跨域整合（20+ 提案如何收敛成 ~12 个落点，避免重复造文件）→ §3 三期路线图 → §4 自我进化闭环 → §5 task-navigator 整合热点 → §6 不做清单 → §7 最小可落地集（MVP）。
> 定位红线：**Cursor 原生、轻量聚焦**——P0/P1 一律是"文件化纪律（policy/rule/protocol）+ 已挂载 MCP（claude-mem）+ 轻量脚本"，**零重框架**；向量库/GraphRAG/沙箱/durable runtime/自托管 serving/多租户一律 P2，明确"现在不做"。
> 数据诚实度：域 1–7、9、11、12 本轮**联网核实**（标〔web〕）；域 8、10 因联网/配额受限**以训练知识为主**（标〔知识〕），建议后续补一次联网校验。本次研究本身三次 `resource_exhausted` 已成为域 8/12"成本预算护栏"的反面教材并写入建议。

---

## §1 一页结论

### 12 域各一句话结论（现状→最高杠杆缺口）

| 域 | 一句话结论 | 最高优先 P0 落点 |
|---|---|---|
| 1 推理范式 | 有团队级 6 模式，缺**单代理"一步内用哪种推理范式"**的显式库 | `agent-reasoning-paradigms.md` |
| 2 多代理编排 | 6 模式选型到位，缺**运行时语义**（状态账本/stall/恢复/子代理契约/MAST 防护） | `orchestration-runtime.md` |
| 3 意图路由 | 纯命令+关键词硬匹配，缺**语义路由+置信度+澄清门禁+护栏** | `intent-routing-and-dialog.md` + `intent-router.mdc` |
| 4 工具/MCP | 优秀的消费方纪律，缺**工具使用通用规范+最小权限+MCP 运行时安全** | `tool-use-protocol.md` |
| 5 RAG 检索 | **完全无检索层**（采集后喂全文/grep），缺查询变换+混合检索+重排+接地 | `retrieval-protocol.md` |
| 6 上下文记忆 | 最薄弱最高杠杆，缺**跨会话记忆+上下文压缩+预算**（claude-mem 已挂未用） | `memory-protocol.md`（接 claude-mem） |
| 7 对话管理 | 任务式多轮，缺**显式对话状态/槽位+系统化澄清+转人工降级** | 并入 `intent-routing-and-dialog.md` |
| 8 企业级 AgentOps | 近单用户，企业基建多为 P2；但缺**显式 AgentOps 生命周期+成本护栏** | `agentops-lifecycle.md` + 成本护栏 |
| 9 评估可观测 | 有单轮 EDD，缺**agent 轨迹评估+完成判定+在线可观测**（契约测试只验存在性） | `agent-trajectory-eval.md` + 扩 `run_eval.py` |
| 10 安全护栏 | 有配置面扫描+人工纪律，缺**运行时间接注入防护+输入输出校验+HITL 审批闸** | `agent-safety-protocol.md` |
| 11 Prompt优化/结构化输出 | 有人工策略卡+调优，缺**自动优化接入+结构化输出强约束** | 扩 `prompt-engineering-techniques.md`（强约束） |
| 12 模型路由/成本 | 有 Token 优化"原则"，缺**落地的模型分级+缓存复用+预算护栏** | `cost-discipline-methodology.md` |

### 五个跨域共性缺口（这才是真正要补的"根"）

1. **运行时语义缺失**：6 团队模式/5 能力都是"靠模型遵守的方法论文档"，没有**显式状态对象 + 断点恢复 + 失败防护**（域2 核心；域6/7 的状态、域8 的生命周期都依赖它）。
2. **没有统一的"自检+接地+完成判定"闸**：自检/幻觉缓解/reviewer/完成判定在域 1、2、9、10 各被提一次，**散落且只在 research 写死**——必须收敛成**一个跨能力共用的协议**。
3. **没有"知识供给层"**：检索（域5）与记忆（域6）双缺——采集 1600+ 条证据全塞上下文（context rot），跨会话从零开始（claude-mem 挂着没用）。这是用户点名的 RAG+记忆缺口。
4. **评测闭环只到"存在性"**：契约测试只验文件在不在，没有**质量评分/轨迹评估/With-skill vs Baseline**（域9）——这是"闭环"二字真正的脊椎，缺它则所有增强无法验证是否真的变好。
5. **成本与安全无运行时护栏**：无任务级预算熔断（域8/12，本次三轮限流即铁证）、无运行时注入防护与高风险 HITL 闸（域10）——"能跑"与"敢上生产"之间的底线工程。

---

## §2 跨域整合：20+ 提案 → ~12 个落点（关键：合并，不重复造）

12 个域独立提出了 **~20 个新 policy/rule**，但**高度重叠**。综合后通过 **6 处关键合并**收敛——这是本次综合最重要的判断，否则会造出一堆互相打架的碎片文件：

| 合并 | 来源域提案 | 收敛为 | 理由 |
|---|---|---|---|
| **合并1（最重要）** | 域1 `self-critique-protocol` + 域10 `幻觉缓解` + 域2 `通用 reviewer 契约` + 域9 `完成判定 checklist` | **`self-critique-and-grounding.md`** | 四者都是"出结论前的质量闸"，本质同一件事：自检→接地引用→完成判定→不达标不终止。散成 4 份必打架 |
| **合并2** | 域3 `intent-routing-methodology` + 域7 `dialog-management-protocol` | **`intent-routing-and-dialog.md`** | 域7 自己点明"与域3 共用同一套澄清门禁与护栏"——进门路由 + 门内对话状态是一条链 |
| **合并3** | 域3 `capability-utterances.yaml` + 域7 `capability-slots.yaml` + 域8 `结构化能力目录` | **`capability-registry.yaml`** | 都是"五能力的结构化描述"：例句(路由用)+槽位(澄清用)+元数据(发现用)合成一份单一真源 |
| **合并4** | 域12 `cost-discipline` + `model-tier-routing` + `cost-budget-protocol` + 域8 `成本护栏` | **`cost-discipline-methodology.md`**（含 model-tier 决策表 + 预算护栏两节） | 成本是一个主题，分级/缓存/预算/级联是它的子节，无需四个文件 |
| **合并5** | 域2 `subagent-contract` | 并入 **`orchestration-runtime.md`** 的"子代理契约"节 | 子代理输入输出契约是编排运行时的一部分 |
| **合并6** | 域10 `工具最小权限` + 域12 `工具结果缓存` | 并入 **`tool-use-protocol.md`** 的相应节 | 都是"工具怎么用"的子条款 |

**合并后的落点清单（~12 个 P0 核心 + 若干扩展/P1）**见 §3 路线图。

---

## §3 三期增强路线图

> 分期原则：**P0 = 零基建、纯文件化、立刻可用且高杠杆**；**P1 = 用已挂载 claude-mem + 轻量约定/脚本**；**P2 = 需重基建，与轻量定位冲突，默认不做（仅记触发条件）**。每项给：落点文件 · 做什么 · 来源域 · 验收信号（尽量可被 `tests/` 契约测试断言）。

### Phase 1 — P0 核心层（11 新文件 + 2 既有文件扩展 + 1 规则改造；零基建）

| # | 落点文件 | 做什么（一句） | 来源域 | 验收信号 |
|---|---|---|---|---|
| P0-1 | `policies/agent-reasoning-paradigms.md`（新） | 单代理推理范式库 + 选择决策树（ReAct/Plan-Execute/ReWOO/Self-Refine/CodeAct）+ 自主性分级 + "先 workflow 后 agent" + test-time compute/思考预算 | 1 | 含 `ReAct`/`Plan-and-Execute`/`Self-Refine`/`自主性分级`/`workflow 优先` 标记 |
| P0-2 | `policies/orchestration-runtime.md`（新） | 编排运行时：Task/Progress 双账本 + stall→reset&replan + 恢复协议 + **子代理 I/O 契约** + MAST 失败防护清单 | 2 | 含 `Task Ledger`/`Progress Ledger`/`stall`/`恢复协议`/`子代理契约`/`MAST` |
| P0-3 | `policies/self-critique-and-grounding.md`（新，**合并1**） | 统一质量闸：Self-Refine/CoVe 自检 + 强制引用/接地/abstain + 高层目标级完成判定 + reflect-when-stuck（仅受阻才反思）+ 防过早终止 | 1+2+9+10 | 含 `自检`/`CoVe`/`强制引用`/`abstain`/`完成判定`/`reflect-when-stuck`；至少 PRD 或 SQL 接入 |
| P0-4 | `policies/retrieval-protocol.md`（新） | 检索四步纪律：查询变换→混合检索(grep+claude-mem+WebSearch)→LLM 重排→上下文化引用；后端零向量库即可落地 | 5 | 含 `查询变换`/`混合检索`/`重排`/`上下文化引用`/`禁止堆叠` |
| P0-5 | `policies/memory-protocol.md`（新，接 claude-mem） | 跨会话记忆读写：启动先 `search` 历史、收尾写结构化 observation（白名单）；claude-mem 为后端、仓库为真源、宕机降级本地 | 6 | 含 `检索记忆`/`观察写入`/`写入白名单`；task-navigator 规划含"已检索历史记忆"行 |
| P0-6 | `policies/intent-routing-and-dialog.md`（新，**合并2**）+ `.cursor/rules/intent-router.mdc` | 三层路由（命令→语义→兜底）+ 置信度 + ask-or-act 澄清门禁（缺槽一次性问全）+ 对话状态 slot + confirmation 分级 + 护栏/转人工 | 3+7 | 含 `三层路由`/`置信度`/`ask-or-act`/`一次性问全`/`护栏`；20 条混淆/越界 query 自测路由正确率达标 |
| P0-7 | `policies/capability-registry.yaml`（新，**合并3**） | 五能力单一真源：每能力 例句(≥10) + 必填槽位 + 元数据(命令/产物/依赖)，供路由/澄清/发现复用 | 3+7+8 | 每能力 ≥10 例句 + ≥3 必填槽；被路由与契约测试同时加载 |
| P0-8 | `policies/tool-use-protocol.md`（新，**合并6**） | 工具使用通用规范：Anthropic 工具设计原则 + 工具选择决策表 + 错误处理/降级/透明化(泛化 research 的 doctor) + **最小权限分级** + **结果缓存约定** | 4+10+12 | 含 `命名空间`/`渐进式披露`/`工具错误处理`/`降级`/`读/写/破坏性`/`结果缓存` |
| P0-9 | `policies/agent-safety-protocol.md`（新） | 运行时三防线：①间接注入防护(外部内容一律数据非指令+spotlighting+不外发铁律) ②输入/输出校验(schema+拒答+PII/密钥过滤+引用校验) ③高风险动作 HITL 审批闸 | 10 | 含 `间接注入`/`外部内容一律数据`/`输出过滤`/`PII`/`高风险动作`/`先停后做` |
| P0-10 | `policies/cost-discipline-methodology.md`（新，**合并4**） | 成本纪律：模型/思考分级决策表 + 三层缓存复用门禁 + **任务级预算护栏(超限先停问)** + 级联式派发 + **限流即停用不重试**（本次事故教训） | 12+8 | 含 `模型分级决策表`/`缓存复用门禁`/`预算护栏`/`超限收敛`/`限流即停用不重试` |
| P0-11 | `policies/agent-trajectory-eval.md`（新）+ 扩 `scripts/run_eval.py` | agent 轨迹评估：完成率/工具调用准确率/步骤效率 grader + `run-trace.jsonl`(OTel 风格)最小约定；契约测试从"存在性"补"质量评分" | 9 | `run_eval.py` 加 `tool_called`/`tool_args_match`/`task_completion`；含 `轨迹`/`完成判定`/`run-trace` |
| P0-12 | 扩 `policies/prompt-engineering-techniques.md` | 结构化输出**强约束**决策树：能 strict/json_schema/受限解码就别靠提示；不能则 Pydantic/Zod 校验+reask 兜底；铁律"schema 合规≠语义正确" | 11 | 含 `结构化输出强约束`/`strict`/`受限解码`/`schema 合规≠语义正确` |
| P0-13 | 改 `.cursor/rules/task-navigator.mdc`（**集成热点**，见 §5） | 在"输出工作规划前"插入统一**预检判定块**，引用上述各 protocol（路由/单多代理/推理范式/检索记忆/成本/HITL） | 1+2+3+5+6+10+12 | 规划输出含"路由/单多代理/推理范式/成本预估/已检索记忆"判定行 |

### Phase 2 — P1 增强层（用 claude-mem + 轻量约定）

| # | 落点 | 做什么 | 来源域 |
|---|---|---|---|
| P1-1 | 激活 claude-mem 后端 + 建 `knowledge/` 目录 + 历史 deliverables 建 corpus | 落实 P0-5 的记忆后端与 P0-4 的语义检索后端（`build_corpus`/`query_corpus`） | 5+6 |
| P1-2 | `policies/context-budget.md`（新） | write/select/compress/isolate 四范式映射五能力 + 阶段边界摘要 compaction | 6 |
| P1-3 | `policies/agentops-lifecycle.md`（新） | 把 `/经验写回`+契约测试+`/安全扫描`+`/检查Agent更新` 串成 build→eval→ship→govern 闭环 + 各阶段准入门禁 | 8 |
| P1-4 | `policies/prompt-optimization-protocol.md` + `policies/output-contract.md`（新） | 自动优化升级判据(GEPA/DSPy 接入,metric=score+feedback=ASI 归因) + 关键产物 schema 契约 | 11 |
| P1-5 | `policies/mcp-tool-authoring.md`（新） | 造/买/降级判据 + 自建 MCP 的 build→eval→iterate 流程 | 4 |
| P1-6 | `policies/red-team-checklist.md`（新） | 注入/越狱/外泄/越权四类攻击用例集，写回/发布前过一遍 | 10 |
| P1-7 | `aibi-query` Table-RAG-lite + research/aibi 多轮 history-aware 查询改写 | 表/案例按需检索注入(替代全量读) + follow-up 改写成自洽查询 | 5+7 |
| P1-8 | 扩 `agent-team-methodology.md`（MAST 防护节+级联派发+预算护栏）、`agent-security-scan.md`（MCP 运行时风险）、`submission-review-contract.md`（评估门禁+ACE 写回）、`llm-eval-methodology.md`（轨迹/red-team 节） | 把 P0 协议反向挂进既有方法论库，形成引用闭环 | 多域 |

### Phase 3 — P2 远期/北极星（需重基建，默认不做，仅记触发条件）

> **状态（v0.24.0）**：Phase 3 各项已产出**实现级 P2 协议**（`policies/*-p2.md`，含触发判定 + 选型 + 集成方案），并落地零依赖入口 `scripts/retrieval_index.py`（BM25+RRF）。这些是"**spec-complete + 触发式启用**"——默认不引入重基建（忠于轻量聚焦定位），命中触发条件即按对应 P2 协议实施。映射：检索→`advanced-retrieval-p2.md`；CodeAct/沙箱→`codeact-execution-p2.md`；durable→`durable-execution-p2.md`；自托管 serving→`self-hosted-serving-p2.md`；多租户/合规→`productization-readiness-p2.md`；ACE/ADAS/DGM 自进化→`self-evolving-agent-p2.md`。

| 主题 | 触发条件 | 来源域 |
|---|---|---|
| 向量库/嵌入混合索引、CRAG/Adaptive-RAG | 单任务证据 >~800 条或跨任务高频复用 | 5 |
| GraphRAG/时序知识图谱、ColPali 视觉 RAG | 市场全景全局综合 / 截图-PDF 富语料 | 5+6 |
| CodeAct + 沙箱代码执行（E2B/受管 venv） | 多步批量工具操作成主流、需安全隔离 | 1+4 |
| durable runtime（Temporal/DBOS） | 超长程、跨进程、强一致事务硬需求（先用状态文件近似） | 2 |
| 自托管 serving（vLLM/SGLang/量化） | 未来本地化 router/embedding/rerank 小模型 | 12 |
| 多租户/企业 SSO/agent 身份/SLA/合规 | 产品专家 Agent 面向团队/组织产品化 | 8 |
| **ACE 式自进化写回（北极星）** | P0-11 eval 基建就位后 | 1+6+9+11 |
| ADAS/DGM 式自动 agent 设计 | eval+沙箱基建成熟，远期 | 1 |

---

## §4 自我进化闭环设计（"闭环"二字的落点）

把零散增强串成一条**可运行、可回归、可追溯**的自我进化闭环——这正是用户要的"闭环"。它对齐 `llm-eval-methodology.md` 七段闭环 + `agent-team-methodology.md` 第三/四部分：

```
① 识别缺口            ② 增强(增量 delta)        ③ 评测(脊椎=域9)
  (research/findings   →  写 policy/rule/protocol  →  契约测试 + With-skill vs
   + 线上失败回流)         (不整篇重写,防 collapse)     Baseline + 轨迹/完成判定 + pass@k
        ↑                                                      │
        │                                                      ▼
  ⑥ 运行时回流 ←──── ⑤ 写回(/经验写回) ←──── ④ 门禁(回归即阻断)
  claude-mem 情景记忆    PR 人审合并            安全扫描+red-team(域10)
  + cost-log + route-log  ACE 式增量+helpful/      + 成本护栏(域8/12)
  (域6/9/12) 反哺①        harmful 计数(北极星)      + 完成判定(域3/9)
        └──────────────── 回归保护 + 数据飞轮 ────────────────┘
```

**这条闭环把 12 个域全部串起来**：
- **脊椎 = 域9**：没有"质量评分/轨迹评估/With-skill vs Baseline"，②的增强就无法证明"真的变好"，闭环断裂。所以 **P0-11（agent-trajectory-eval + 扩 run_eval.py）是闭环能否成立的关键单点**。
- **门禁 = 域8 生命周期 + 域10 安全 + 域12 成本**：③通过后还要过安全(red-team/注入)、成本(预算护栏)、完成判定三道门，才能⑤写回。
- **写回升级（北极星）= 域1/6/11**：把 `/经验写回` 从"整篇重写文档"升级为 **ACE 式增量 delta + helpful/harmful 计数**，避免 brevity bias/context collapse（待 P0-11 就位后做，列 P2）。
- **运行时回流 = 域6/9/12**：claude-mem 情景记忆 + `cost-log` + `route-log` 让"下次同类任务"自动召回经验、点名最贵步、复盘误路由——形成数据飞轮反哺①。

> 一句话：**P0 建"能力"，闭环让能力"持续变强且不退步"**。先把 P0-11 评测脊椎立起来，其余增强才有标尺。

---

## §5 集成热点：`task-navigator.mdc` 改造（所有增强的汇聚点）

7–8 个域都要求"在任务启动规划前加一步判定"。若各自往 `task-navigator` 里塞，它会膨胀失控。**正确做法：task-navigator 只加一个轻量"预检判定块"，具体规则下沉到各 protocol（渐进式披露）**：

现状流程：`读材料 → 分析需求 → 匹配能力 → 分阶段规划 → 征求确认`

改造后，在"分阶段规划"前插入 **预检判定块**（每项一句话 + 指向对应 protocol）：
1. **路由与澄清**（域3/7）：意图+置信度；关键槽位缺失→一次性问全（→ `intent-routing-and-dialog.md`）
2. **单/多代理 + read/write**（域2）：write-heavy 强一致→单代理；read-heavy 可并行→扇出（→ `orchestration-runtime.md`）
3. **推理范式**（域1）：确定性→workflow；需边做边修→ReAct；可并行工具→ReWOO（→ `agent-reasoning-paradigms.md`）
4. **知识供给**（域5/6）：先 `search` 历史记忆；需在语料找证据→走检索协议（→ `memory-protocol.md` / `retrieval-protocol.md`）
5. **成本预估**（域12）：高扇出阶段标档位/预算/可否复用旧产物（→ `cost-discipline-methodology.md`）
6. **高风险标记**（域10）：含外发/删除/写库/发布→标 HITL 审批点（→ `agent-safety-protocol.md`）

并在每阶段产出前挂 **self-critique-and-grounding 闸**（→ `self-critique-and-grounding.md`）。
这样 task-navigator 仍精简，规则可独立演进与测试。

---

## §6 不做清单（同样重要：守住"轻量聚焦"）

明确**现在不做**，避免过度工程把仓库做重、与定位冲突：
- ❌ 不引 LangGraph/AutoGen/CrewAI/Temporal 等**重编排/durable 框架**——用状态账本文件近似（域2）。
- ❌ 不引独立**向量库/GraphRAG/ColPali 视觉 RAG**——P0 检索后端用 grep+claude-mem+WebSearch（域5）。
- ❌ 不引**重护栏框架**(NeMo/Guardrails AI)——用 policy + 复用 `security_self_check` 正则（域10）。
- ❌ 不**真的 pip 装 DSPy 跑编译**作为默认——先把方法论文件化，重场景才接（域11）。
- ❌ 不自建 **serving/多租户/企业 SSO/SLA**——P2，仅产品化时再评估、且优先用大厂托管平台（域8/12）。
- ❌ 不盲目堆并发子代理——**单批 ≤4 + 预算护栏**（本次三轮 `resource_exhausted` 已证盲目并发反伤质量与成本）。

---

## §7 最小可落地集（MVP）与实施建议

若不想一次铺开 13 项 P0，按**杠杆×依赖**排序，**先做这 5 件（MVP）**即可让能力质变且形成闭环骨架：

| 序 | 做什么 | 为什么先做 |
|---|---|---|
| **MVP-1** | `self-critique-and-grounding.md`（合并1） | 一份文件补齐 4 个域的"质量闸"，五能力立刻共享自检+接地+完成判定，杠杆最高 |
| **MVP-2** | `retrieval-protocol.md` + `memory-protocol.md`（接 claude-mem） | 用户点名的 RAG+记忆双缺口；零基建即可让"采集→精准取证"和"跨会话记忆"落地 |
| **MVP-3** | `agent-trajectory-eval.md` + 扩 `run_eval.py` | 立**闭环脊椎**——没有它，其余增强无法验证"真的变好"，闭环不成立 |
| **MVP-4** | `cost-discipline-methodology.md`（含预算护栏+限流即停） | 直接修复本次三轮 `resource_exhausted` 暴露的"无成本护栏"硬伤 |
| **MVP-5** | 改 `task-navigator.mdc` 加预检判定块 | 把上述协议接入主流程，让增强真正被"用起来"而非躺在文件里 |

**实施纪律**（每件都遵循）：
1. 每个新 policy 配**契约测试**（文件存在 + 关键标记 + 触发词）写进 `tests/test_product_expert_agent.py`，跑通全量再合并。
2. 走 §4 闭环：增量 delta（不整篇重写）→ 评测 → 安全/成本门禁 → PR 人审。
3. 严格 Why-First + 渐进式披露（大细节下沉 references/），守住上下文预算。
4. 每件标注来源 findings（可追溯到本次 ~700 条 SOTA 编目）。

---

## 附：findings 索引（细节与 ~700 条 SOTA 编目）

`findings/01-agent-reasoning.md`(48) · `02-multi-agent-orchestration.md`(50) · `03-intent-routing.md`(45) · `04-tools-mcp.md`(77) · `05-rag-retrieval.md`(86) · `06-context-memory.md`(52) · `07-conversational-agents.md`(42) · `08-enterprise-agentops.md`(52,知识为主) · `09-eval-observability.md`(73) · `10-safety-guardrails.md`(50,知识为主) · `11-prompt-optimization-structured-output.md` · `12-model-routing-cost.md`(70)。
路线图与共享 brief 见 `00-roster.md`。
