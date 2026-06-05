# 域 2：多代理协作与编排框架

> 子代理：multi-agent-orchestration ｜ 回写：`research/ai-capability-upgrade/findings/02-multi-agent-orchestration.md`
> 来源标注：〔web〕= 本次联网核实（2025-2026 框架现状/版本）；〔知识〕= 训练知识、未逐条复核（已尽量只用确有其物的框架/论文）。
> 边界：本域聚焦**多代理"团队"的协作拓扑、编排框架与运行时机制（状态/持久化/handoff/失败防护）**。单体 Agent 的推理范式（ReAct/Plan-and-Execute/反思）见域 1；语义/模型/查询路由见域 3；MCP·工具·沙箱·computer-use 工程见域 4；记忆/RAG 基建见域 5、6；轨迹评估/LLM-as-judge/可观测见域 9；护栏/HITL 安全见域 10。本域与它们交叉处只做引用、不展开。

---

## 领域概述

「多代理编排」回答的是**"把一个任务拆给几个代理、它们怎么协作、谁拥有最终产出、出错怎么办、中断怎么续"**。2025-2026 的关键转变有三：① 框架从百花齐放走向**收敛与生产化**——AutoGen+Semantic Kernel 合并为 Microsoft Agent Framework、OpenAI Swarm 被 Agents SDK 取代、CrewAI 脱离 LangChain 独立；② **"图/状态机 + checkpointer + 持久化执行"成为编排事实标准底座**（LangGraph 引领，MAF/ADK 2.0/Pydantic AI 跟进），并把 durable execution 从"工作流基建"挪进"代理运行时中心"；③ 学界把**失败模式系统化**（MAST 14 模式，42% 是"系统设计/规范"问题而非模型能力），并出现"**何时不该上多代理**"的强力反方（Cognition《Don't Build Multi-Agents》）。

对「产品专家 Agent」的直接意义：它的现状是 **Cursor 原生单体 Agent + `agent-team-methodology` 的 6 种团队模式（流水线/扇出扇入/专家池/生成-检验/监督者/层级委托）**。这 6 模式与 LangGraph/Anthropic 的拓扑高度同构，**方法论选型层面已对标到位**；真正的差距是——**它们是"靠模型遵守的方法论文档"，缺一层"运行时引擎语义"：没有显式状态对象、没有 handoff 契约、没有 stall 检测/失败防护、不能断点续跑**。本域的核心结论是：这一层**绝大部分可以"提示化/文件化"实现**（借鉴 Magentic-One 的"Orchestrator + Task/Progress 双账本 + stall→reset&replan"），**无需引入 LangGraph/Temporal 这类重运行时框架**——把"状态账本文件 + 子代理契约 + MAST 失败防护清单 + 恢复协议"写进 policy 即可逼近运行时语义。

---

## SOTA 技术目录

> 按子类分组，共 **50 条**。成熟度：实验 / 成长 / 成熟 / 事实标准 / 收敛中（指框架正被合并或继任）。

### A. 编排框架（代码/图/角色/事件驱动；多数需引入运行时）

| 技术·框架 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **LangGraph** | 低层图/状态机编排：节点=函数/代理，边=控制流，自带 checkpointer/durable/HITL/time-travel | 需可审计状态、断点恢复、复杂分支的生产编排 | 事实标准（开源编排） | LangChain LangGraph；用户 Klarna/Replit/Elastic | 〔web〕 |
| **LangGraph Platform + LangSmith** | 长程有状态代理的托管部署 + 追踪/可观测 | 要把图编排上生产、看轨迹/状态转移 | 成长 | LangChain（交叉域 9） | 〔web〕 |
| **Microsoft Agent Framework (MAF)** | AutoGen+SK 合并继任者；graph workflows 支持 sequential/concurrent/handoff/group + checkpointing/streaming/HITL/time-travel | .NET/Python 生产级多代理；要 durability/治理 | 成长（2025 新，收敛中） | microsoft/agent-framework | 〔web〕 |
| **AutoGen (v0.4 actor/事件驱动)** | 对话式多代理、actor 消息模型；并发好但长程会话漂移 | 研究/迭代推理/群聊式协作 | 成熟→被 MAF 继任 | microsoft/autogen | 〔web〕 |
| **Semantic Kernel** | 企业级 SDK（连接器/内容审核/遥测）；新增多代理编排 | 已有 SK 存量；新项目转 MAF | 成熟→维护（SK=MAF v1.x） | Microsoft SK | 〔web〕 |
| **Magentic-One** | 通用 Orchestrator + 4 专家代理；**Task Ledger + Progress Ledger + stall→replan** | 开放式、解法路径未知、需动态协作 | 研究→产品（进 MAF/SK 的 Magentic orchestration） | Microsoft Research 2024 | 〔web〕 |
| **OpenAI Agents SDK** | Swarm 生产继任者；handoffs + agents-as-tools + guardrails + tracing + sessions + durable（2026） | 轻量、handoff/triage 式多代理 | 成长（事实标准之一） | openai-agents（py/ts），v0.17+ | 〔web〕 |
| **OpenAI Swarm** | 实验原型（routines + handoffs），证明"多代理只需极少基建" | —（已废弃，迁 Agents SDK） | 废弃 | OpenAI Swarm（README 已重定向） | 〔web〕 |
| **CrewAI** | 角色制 **Crews**（role/goal/backstory）+ 事件驱动 **Flows**（@start/@listen/@router/@persist） | 角色团队隐喻、快速原型；~10 代理内 | 成长（最快出原型） | crewAI（已脱离 LangChain） | 〔web〕 |
| **LlamaIndex Workflows** | 事件驱动 step/handler 编排；RAG 重场景；llama-deploy 部署 | 文档/检索密集的代理流水线 | 成长 | LlamaIndex；LlamaCloud | 〔web〕 |
| **Google ADK** | workflow agents（Sequential/Parallel/Loop）+ graph-based workflows（2.0）+ agent routing | Google Cloud/Gemini 栈；确定性+图混合 | 成长 | google/adk（py/ts/go/java） | 〔web〕 |
| **Pydantic AI** | 类型优先、validation-first；pydantic-graph；durable execution 一等公民（2026） | Python 强类型输出/校验为先 | 成长 | Pydantic AI | 〔web〕 |
| **Mastra** | TypeScript 优先；createWorkflow（sequential/parallel/loop/foreach）类型安全 | TS/Node 栈代理工作流 | 成长 | Mastra | 〔web〕 |
| **MetaGPT** | SOP 编码的角色制（产品经理/架构师/工程师），"软件公司"隐喻 | 结构化、流程可写成 SOP 的生成任务 | 成长 | MetaGPT；AFlow 同团队（交叉域 1） | 〔知识〕 |
| **Haystack** | pipeline/agent 框架，NLP/RAG 起家 | 检索/问答密集流水线 | 成熟（RAG 域） | deepset Haystack | 〔知识〕 |
| **Dify / n8n / Flowise（可视化 flow）** | 低代码拖拽编排；AI 多为"节点"而非一等运行时原语，代理深度浅 | 业务集成/自动化、非工程团队 | 成熟（低代码） | Dify/n8n/Flowise/Zapier/Make | 〔web〕 |

### B. 协作拓扑 / 编排模式（**多为方法论，对单体 Agent 立刻可借鉴**）

| 模式 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **Supervisor（hub-and-spoke）** | 中央 supervisor 路由 worker、收集、综合；清晰失败归因 | 大多数企业用例的起点 | 事实标准 | langgraph-supervisor；OpenAI manager | 〔web〕 |
| **Hierarchical 层级** | supervisor of supervisors，按功能聚类分层 | worker >6 或需团队级共享上下文 | 成熟 | LangGraph 多级 supervisor | 〔web〕 |
| **Network / peer-to-peer** | 任意代理对任意代理通信 | 灵活协作，但难调试、易漂移 | 成长 | LangGraph network 模式 | 〔web〕 |
| **Handoff / Swarm** | **控制权转移**：专家接管"下一回合的回复" | 路由本身即流程、要专家直接答 | 成长 | OpenAI handoff()；langgraph-swarm | 〔web〕 |
| **Agents-as-tools** | manager **保留所有权**，把专家当工具调用并综合 | 要一个代理拥有最终答案、统一护栏 | 事实标准 | OpenAI Agent.as_tool() | 〔web〕 |
| **Triage / Routing** | 分诊代理按输入类型路由专家 | 输入异质、需分而治之 | 事实标准 | OpenAI triage；（交叉域 3） | 〔web〕 |
| **Orchestrator-Workers** | 运行时动态拆/派/合（子任务运行时才定） | 任务不可预先分解、复杂多变 | 事实标准 | Anthropic 多代理研究（+90.2% vs 单）| 〔web〕 |
| **Planner-Executor** | 规划器先出计划、执行器逐步执行（可重规划） | 长链路、步骤较稳定 | 成熟 | LangChain Plan-and-Execute（交叉域 1） | 〔web〕 |
| **Evaluator-Optimizer（生成-评审）** | 一个生成、一个按标准评/反馈，循环到达标 | 有清晰评价标准、迭代有增益 | 事实标准 | Anthropic 同文；ADK LoopAgent | 〔web〕 |
| **Map-Reduce / Fan-out-Fan-in** | 并行独立子任务 → 聚合（分段/投票） | 可并行/需多样性或多重校验 | 事实标准 | ADK ParallelAgent+JoinNode；asyncio.gather | 〔web〕 |
| **Debate / Society of Minds** | 多代理辩论/陪审团，降过度自信、提真实性 | 高风险判断、需对冲单点幻觉 | 成长 | Du et al. debate；Sibyl jury（交叉域 1） | 〔web〕 |
| **Blackboard / Global Workspace** | 共享黑板 + 代理**自主认领**（去中央派活），可审计"思维日志" | 数据发现/异质来源/对抗式验证 | 成长（研究强） | LLM Blackboard（数据发现 +13~57%）；MAVEN | 〔web〕 |
| **Group Chat（角色制群聊）** | 角色制轮流发言、共享会话 | 头脑风暴/多视角讨论 | 成长 | AutoGen GroupChat；SK group | 〔web〕 |

### C. 状态与持久化 / 运行时语义（**本域核心差距，多需运行时但可"文件化"近似**）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **Graph State（共享状态对象）** | 统一 TypedDict/Pydantic 状态贯穿执行，承载任务/中间结果/最终输出 | 任何需跨节点传状态的编排 | 事实标准 | LangGraph StateGraph | 〔web〕 |
| **Checkpointer（持久化快照）** | 每超步快照状态，thread_id 恢复（InMemory→Postgres） | 要崩溃恢复、rewind 重试 | 事实标准 | LangGraph PostgresSaver | 〔web〕 |
| **Durable Execution** | journal 重放 / DB checkpoint：崩溃后从最后成功步恢复，不重复付 token | 长程、贵 token、多副作用的生产代理 | 成长→2026 基线 | 见下四行 | 〔web〕 |
| **Temporal** | 企业级 durable 标准，deterministic replay；重运维 | 大规模、跨服务、复杂重试/超时 | 成熟 | Temporal（2026 $300M/$5B） | 〔web〕 |
| **Inngest / Trigger.dev** | 事件驱动、step 记忆化、serverless 友好、代理原语 | 中小/serverless 事件驱动代理 | 成长 | Inngest；Trigger.dev | 〔web〕 |
| **Restate** | 单二进制、per-object 状态、低延迟、轻量 | 有状态低延迟调用 | 成长 | Restate | 〔web〕 |
| **DBOS** | Postgres 原生、零新基建、状态/执行入库 | 想把状态全留在 Postgres、零运维 | 成长 | DBOS（Stonebraker/Zaharia） | 〔web〕 |
| **HITL Interrupt / suspend-resume** | 在任意点暂停、人审/改状态、再恢复 | 需人审/纠偏的关键步 | 事实标准 | LangGraph interrupt；MAF（交叉域 10） | 〔web〕 |
| **Time-travel / replay** | 回到第 N 步、换提示重跑 | 调试/择优/分支探索 | 成长 | LangGraph；LangGraph Studio | 〔web〕 |
| **Task Ledger + Progress Ledger（Magentic-One）** | **账本即状态**（facts/guesses/plan）+ 每轮 5 问进度账本 + stall 计数→reset&replan | 开放任务的"轻量可提示化运行时" | 研究→产品 | Magentic-One；MAF Magentic orchestration | 〔web〕 |
| **Saga / 补偿回滚** | 多步部分失败时自动补偿回滚到一致态 | 跨步骤事务、要原子性 | 成长 | Saga pattern for AI workflows | 〔web〕 |

### D. 互操作协议（**对外代理协作；当前多为"重引入"**）

| 协议 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **A2A（Agent2Agent）** | 代理间"HTTP"：Agent Card 发现 + JSON-RPC，跨框架/厂商协作 | 要和外部/异构代理互通 | 成长（事实标准化中，150+ 机构） | Linux Foundation / AAIF（原 Google）| 〔web〕 |
| **MCP（Model Context Protocol）** | agent-to-tool 标准；与 A2A 互补 | 代理接工具/数据（域 4 详） | 事实标准 | Anthropic MCP（AAIF 治理） | 〔web〕 |
| **ACP（IBM Agent Comm. Protocol）** | 单运行时内代理消息总线；已并入 A2A | —（收敛进 A2A） | 收敛中 | IBM ACP | 〔web〕 |
| **AGNTCY（Internet of Agents）** | 发现/身份/SLIM 消息/可观测 的基建套件，用 A2A+MCP | 规模化"代理互联网"基建 | 成长 | Cisco Outshift；Linux Foundation | 〔web〕 |

### E. 失败模式与"何时不该上多代理"（**最该立刻吸收的方法论**）

| 主题 | 一句话 | 何时用/启示 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **MAST 失败分类法** | 14 模式 / 3 类（规范 41.8% · 对齐 36.9% · 验证 21.3%），LLM-judge 诊断轨迹 | 设计/复盘多代理的"病历本" | 成熟（基准，κ=0.88） | UC Berkeley 等 2025（NeurIPS） | 〔web〕 |
| **FC1 规范类（42%）** | 违背任务/角色规范、**步骤重复(17%)**、上下文丢失、**不识别终止条件(10%)** | 显式角色/终止条件/状态防丢 | — | MAST FM-1.1~1.5 | 〔web〕 |
| **FC2 对齐类（37%）** | **不澄清就乱猜(12%)**、任务跑偏、信息隐瞒、忽略他人输入、**推理-行动错位(14%)** | 强制"不确定即澄清"+ 交叉核对 | — | MAST FM-2.1~2.6 | 〔web〕 |
| **FC3 验证类（21%）** | **过早终止(8%)**、无/不完整验证、错误验证（表层通过实则有 bug） | 高层目标级验证（ChatDev +15.6%） | — | MAST FM-3.1~3.3 | 〔web〕 |
| **《Don't Build Multi-Agents》（Cognition）** | write-heavy 任务用**单线程连续上下文**更可靠；多代理上下文碎片化、隐式决策冲突会复合 | 编码/强一致产出别盲目拆代理 | 成长（行业辩论） | Cognition 2025 | 〔web〕 |
| **read vs write 任务二分** | read-heavy（调研/探索）宜多代理并行；write-heavy（编码/口径一致）宜单代理 | 拆代理前先判任务读写性质 | 成长（共识） | philschmid；Cognition×Anthropic | 〔web〕 |
| **Token 经济（4× vs 15×）** | 多代理 ~15× chat token（单代理 ~4×），只对高价值复杂任务划算 | 拆代理要算 ROI | 成熟（实测） | Anthropic；philschmid | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **框架大合并/收敛**〔web〕：AutoGen+Semantic Kernel → **Microsoft Agent Framework**；Swarm → **OpenAI Agents SDK**；CrewAI 脱离 LangChain 独立。编排栈从"百花齐放"走向"少数生产级标准"，选型风险下降。
2. **"图/状态机 + checkpointer"成编排事实底座**〔web〕：LangGraph 引领，MAF、Google ADK 2.0、Pydantic AI 都补齐 graph + 持久化 + HITL + time-travel——**显式状态对象**成为可靠多代理的前提。
3. **Durable execution 从基建挪进"代理运行时中心"（2026 基线）**〔web〕：Temporal（$300M/$5B、AI 公司贡献 1.86 万亿次执行）、Inngest、Restate、DBOS；LangGraph/Pydantic AI/Agents SDK 都把 durable 列为一等特性——因 LLM 成本/时长/可靠性，"无 durable 的生产代理几乎不可行"。
4. **Handoff vs Agents-as-tools 成为多代理的"第一设计抉择"**〔web〕：核心是"**谁拥有面向用户的最终回复**"。Handoff=转移所有权（适合 triage/路由）；as-tool=主代理保留所有权并综合（适合强一致产出）。OpenAI/LangGraph 都把它作为核心原语。
5. **互操作协议成形并中立化**〔web〕：A2A 进 Linux Foundation、与 MCP 同归 **AAIF（Agentic AI Foundation）** 治理，150+ 机构；分层栈 = MCP（工具）+ A2A（代理）+ AGNTCY（发现/身份/可观测）。
6. **失败模式被系统化（MAST）**〔web〕：14 模式 3 类，**42% 是"系统设计/规范"问题而非模型能力**——意味"结构化设计 + 分层验证"比换模型更治本；LLM-as-judge 诊断轨迹成标准件（交叉域 9）。ChatDev 仅加一个"高层目标级验证"步即 +15.6%。
7. **"单 vs 多代理"辩论收敛为任务依赖**〔web〕：Cognition（write-heavy→单线程）vs Anthropic（read-heavy→多代理），共识 = **read 并行宜多、write 一致宜单**；两边都把"**上下文工程**"列为头号纪律（交叉域 6）。
8. **Magentic-One 的"Orchestrator + 双账本 + stall→replan"成开放任务通用范式**〔web〕：Task Ledger（事实/计划）+ Progress Ledger（每轮 5 问 JSON：是否完成/是否有进展/是否原地打转/下一发言者/指令）+ stall 计数超阈值→清空重规划——**这是"轻量可提示化运行时"的最佳范本**，无需重框架即可借鉴。
9. **Blackboard / Global Workspace 回潮**〔web〕：共享黑板 + 代理**自主认领**（去中央派活），在数据发现/对抗式验证上显著优于 master-slave，并天然产出可审计"思维日志"（MAVEN 用它做对抗式验证防幻觉累积）。
10. **角色制 ↔ 事件驱动双形态可互嵌**〔web〕：CrewAI Crews（自治角色）↔ Flows（事件驱动控制），LlamaIndex/Mastra/ADK 都走"模板 workflow + 图/事件"双轨——确定性业务流与动态编排可在同一系统内嵌套。

---

## 对标产品专家 Agent

> 核心问题：**6 模式方法论怎么补"运行时"语义（状态 / handoff / 失败防护 / 可恢复）？** 答案：**不必引入 LangGraph/Temporal 重框架**，用"状态账本文件 + 子代理契约 + MAST 失败防护清单 + 恢复协议"把运行时语义"文件化/提示化"即可（范本 = Magentic-One 双账本）。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `agent-team-methodology.md` 6 种团队模式，与 LangGraph/Anthropic 拓扑同构，**选型层已到位** | 是"靠模型遵守的方法论文档"，**无运行时引擎语义**：无显式状态对象、无 handoff 契约、无 stall/失败防护、无断点恢复 | **P0**：新增"编排运行时层"——状态账本文件约定 + 子代理契约 + 失败防护清单（见落地 P0-1~P0-3） |
| `task-navigator` 任务启动即多阶段派能力 | **未先判"单代理是否更优 / read 还是 write 任务"**——write-heavy（PRD 成稿/SQL 口径/Demo 代码）盲目拆代理会触发 Cognition 警告的"上下文碎片化、隐式决策冲突" | **P0**：规划前加"单 vs 多代理 + read/write"判定步（落地 P0-4） |
| "子代理只回主代理、主代理裁决"（`subagent-search.md`） | 实为 **agents-as-tools**（主代理保留所有权）——对 write 一致性是**对的**（合 Cognition），但**未显式化**"何时该 handoff 转移所有权 vs 保持 as-tool"，子代理也无标准输入/输出契约 | **P1**：写明默认 as-tool；仅 triage/路由才 handoff + 子代理契约模板（落地 P0-2/P1-1） |
| 单批 ≤4、最大重试 2-3、层级 ≤2 | 有预算护栏但**缺"stall 检测→reset&replan"语义**；无"进度账本"判断是否在原地打转；无全局轮次/时间预算 | **P0**：引入 Magentic-One 式 Progress Ledger（每批次 5 问）+ stall 计数→重规划（落地 P0-1） |
| `SUBAGENT_ROSTER.md` / 任务目录过程文档 = 准状态 | 是**松散文档非结构化状态对象**；不能据此断点续跑；上下文清空/会话切换后编排进度丢失（对应 MAST FM-1.4 上下文丢失） | **P0**：升级为结构化"编排状态文件"（Task+Progress Ledger），充当**轻量 checkpointer**、支持恢复（落地 P0-1） |
| 生成-检验：research 三轮事实核查 = evaluator-optimizer | 验证**写死在 research**，其他四能力无独立验证；可能表层验证（FM-3.3）/过早终止（FM-3.1） | **P1**：抽通用 reviewer 契约——**高层目标级验证**（非表层）+ 完成判定 checklist + 防过早终止（落地 P1-2，交叉域 9） |
| HITL = skill 内 user checkpoint（必须停下确认） | 是确认点，但**未标准化** interrupt/resume 语义（"中断即写状态、恢复即读状态"） | **P1**：把 checkpoint 标准化为"写状态→暂停→读状态续跑"（落地 P1-3，交叉域 10） |
| 子代理信息汇总靠主代理读产物 | 无防 **FM-2.4 信息隐瞒**机制——子代理可能漏报"我知道但主代理不知道的关键约束"；主代理也未强制交叉核对（FM-2.5 忽略输入） | **P1**：子代理输出契约强制含"关键约束/未决问题/置信度"字段（落地 P0-2） |
| 工具层是 MCP 消费方，全是内部 `Task` 子代理 | **无对外代理互操作**（A2A/MCP-as-server）；无法与外部/异构代理协作 | **P2**：关注 A2A/AAIF；当前内部子代理已够，需要对外协作时再评估（重引入，交叉域 4） |
| 长任务（全景调研）无 durable 执行 | 中断需整段重跑、逐 LLM 重付 token（对应 durable 缺失） | **P2**：先用状态文件做"应用级断点续跑"近似；真要 durable 再引入 Temporal/DBOS（重，落地 P2-2） |

---

## 落地建议

> 原则：先做"对单体 Agent 立刻可用"的 policy/rule/契约层（P0/P1），把运行时语义**文件化/提示化**；需重基建（durable runtime / 对外协议）的标 P2 并交叉引用。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 新增编排运行时层 `policies/orchestration-runtime.md`（六模式的"运行时引擎"）
- **放哪**：`policies/orchestration-runtime.md`（新文件，与 `agent-team-methodology.md` 互补——后者选"用哪种模式"，本文件定"模式怎么跑/出错怎么办/中断怎么续"）。
- **做什么**（借鉴 Magentic-One 双账本）：
  1. **状态账本约定**：每个需多代理的任务在 `tasks/{task}/.meta/orchestration-state.md`（或 `.json`）维护两块——**Task Ledger**（目标 / 已知事实 / 计划 / 硬约束）+ **Progress Ledger**（每批次：已完成 / 待办 / blockers / 下一步派谁 / 是否完成 / **是否在原地打转**）。
  2. **stall 检测 + 重规划**：连续 2-3 个批次"无进展或重复"→ 触发 reset&replan（重写 Task Ledger 与计划），与现有"最大重试 2-3、最多 5 轮"对齐。
  3. **全局预算**：最大批次数 / 最大子代理累计数 / 时间或轮次上限，超限即收敛出"最佳当前答案"而非空转（防 FM-1.5 不识别终止）。
  4. **恢复协议**：主代理每批次结束**先写状态文件**；任务被中断/上下文清空后，**开工第一步读状态文件**续跑（轻量 checkpointer，防 FM-1.4 上下文丢失）。
- **验收信号**：`tests/test_product_expert_agent.py` 断言文件存在且含标记 `Task Ledger`/`Progress Ledger`/`stall`/`reset&replan`/`恢复协议`/`状态文件`；至少 research 全景任务实跑时生成并更新 `orchestration-state.md`。

### P0-2 子代理契约模板 `policies/subagent-contract.md`
- **放哪**：`policies/subagent-contract.md`（新），并被 `skills/research-toolkit/protocols/subagent-search.md` 与 `agent-team-methodology.md` 第一部分引用。
- **做什么**：规定每次派子代理必须带——**输入契约**（目标 / 已知事实 / 边界 / **明确不要做什么**，防 FM-2.3 跑偏）；**输出契约**（标准产物路径 / 结论 / **"我知道但主代理可能不知道的关键约束"**[防 FM-2.4 信息隐瞒] / 置信度 / **未决问题**[逼迫 FM-2.2 澄清]）。默认 **agents-as-tools**（只回主代理，合 Cognition write 一致性）；**handoff 转移所有权仅用于纯 triage/路由**。
- **验收信号**：模板含"输入契约/输出契约/关键约束/未决问题/置信度/as-tool 默认/handoff 边界"标记；子代理派发处引用之；契约测试断言子代理产物含"关键约束"与"未决问题"字段。

### P0-3 MAST 失败防护清单接入 `agent-team-methodology.md`（汇总/门禁强制）
- **放哪**：`agent-team-methodology.md` 第一部分新增"### 5. 失败防护（MAST）"小节 + `policies/submission-review-contract.md` 复用。
- **做什么**：按 MAST 三类列**汇总环节强制 checklist**——
  - **FC1 规范**：每子代理有显式角色+终止条件；防步骤重复（查状态账本去重）；状态防丢（写账本）。
  - **FC2 对齐**：不确定即向主代理/用户澄清；产物含"关键约束"防隐瞒；**主代理交叉核对各子代理输出**防忽略输入与推理-行动错位。
  - **FC3 验证**：reviewer 做**高层目标级验证**（对照 brief 目标，非只查"产物存在"）；完成判定走 checklist；防过早终止。
- **验收信号**：小节含 `FC1/FC2/FC3` 与 `14 模式` 引用；`submission-review-contract.md` 的审核清单纳入这三类；测试断言关键标记存在。

### P0-4 task-navigator 加"单 vs 多代理 + read/write"判定步
- **放哪**：`.cursor/rules/task-navigator.mdc`（已存在，"任务启动—主动分析"段内，输出规划前）。
- **做什么**：规划前显式判定——**write-heavy/强一致**（PRD 成稿、SQL 口径、Demo 代码、AI 脚本）→ **优先单代理 + 工具/串行**（避免上下文碎片化）；**read-heavy/可并行**（多平台调研、竞品扫描、海外舆情）→ 多代理 fan-out；并引用域 1"先 workflow 后 agent、按需加自主性"。在分阶段规划里标注每阶段"单/多代理（理由）"。
- **验收信号**：规划输出含"单/多代理：<判定>（理由）"一行；20 条触发 eval 中——write-heavy 任务选单代理、read-heavy 选多代理的命中率达标。

### P1-1 handoff vs as-tool 显式化
- **放哪**：并入 `policies/subagent-contract.md` 或 `agent-team-methodology.md` 第三部分"子代理 vs 主代理直办"。
- **做什么**：补一张小决策表——"专家要直接拥有最终回复/路由即流程 → handoff；主代理要综合多专家产出并统一把关 → as-tool（默认）"。明确本仓库默认 as-tool。
- **验收信号**：文件含 `handoff`/`agents-as-tools`/`所有权` 标记与决策表；与现有"子代理只回主代理"表述一致不冲突。

### P1-2 通用 reviewer 契约（高层验证 / 完成判定 / 防过早终止）
- **放哪**：`policies/`（可与域 1 的"反思自检 protocol"合并）+ `submission-review-contract.md`。
- **做什么**：定义独立 reviewer 的最小职责——**对照 brief.md 目标逐项验证**（高层而非表层）、完成判定 checklist、明确"未达标不得终止"。五能力成稿/出结论前统一引用（research 已有门禁可对齐）。交叉域 9 提供 LLM-as-judge。
- **验收信号**：契约含"高层目标级验证/完成判定 checklist/防过早终止"标记；至少 1 个能力（建议 PRD 或 SQL）接入并在测试断言"产出含目标级验证痕迹"。

### P1-3 HITL interrupt/resume 标准化
- **放哪**：`policies/orchestration-runtime.md`"恢复协议"小节扩展 + 各 skill 的 user checkpoint 处。
- **做什么**：把"user checkpoint"升级为标准 interrupt/resume——**中断点先写状态文件再暂停**；用户回复后**读状态文件续跑**，不重复已完成步。交叉域 10（安全/HITL）。
- **验收信号**：协议含"中断写状态→暂停→读状态续跑"；至少一个 skill 的 checkpoint 改为此模式。

### P2-1 关注代理互操作协议（对外协作时再引入）
- **放哪**：`policies/` 备忘 + 交叉域 4（MCP/工具）。
- **做什么**：跟踪 A2A/AAIF 进展；当前定位（Cursor 原生 + MCP 消费方）下**内部 `Task` 子代理已够**，**不立即引入** A2A/AGNTCY（重）。仅当需"产品专家与外部/异构代理协作"时，评估把自身能力暴露为 A2A/MCP server。
- **验收信号**：备忘记录"现状内部子代理足够 + A2A 触发条件"；不产生立即代码改动。

### P2-2 durable execution（先文件近似，真需要才上重框架）
- **放哪**：`policies/orchestration-runtime.md`（与 P0-1 共享状态文件机制）。
- **做什么**：先用 P0-1 的状态账本文件做"**应用级断点续跑**"（崩溃/中断后从账本恢复），覆盖 80% 需求；仅当出现"超长程、跨进程、强一致事务"硬需求时，再评估 Temporal/DBOS（重运维，与"轻量聚焦"定位冲突，谨慎）。
- **验收信号**：协议写明"状态文件断点续跑为默认，durable runtime 为 P2 触发式选项"；不引入框架依赖。

---

## 参考来源

- **LangGraph / 状态与持久化**〔web〕：langchain-ai/langgraph（low-level orchestration、durable execution、HITL、memory）— https://github.com/langchain-ai/langgraph ；langgraph-supervisor（hierarchical supervisor、tool-based handoff、checkpointer/store）— https://github.com/langchain-ai/langgraph-supervisor ；AWS《Build multi-agent systems with LangGraph and Amazon Bedrock》（thread/checkpoint）。
- **Microsoft Agent Framework / AutoGen / Semantic Kernel / Magentic**〔web〕：microsoft/agent-framework（sequential/concurrent/handoff/group + checkpointing/HITL/time-travel）— https://github.com/microsoft/agent-framework ；MS Learn Overview — https://learn.microsoft.com/en-us/agent-framework/overview/ ；DevBlogs《SK and MAF》《SK Multi-agent Orchestration（Magentic）》；Visual Studio Magazine（2025-10 合并）。
- **Magentic-One（双账本/stall→replan）**〔web〕：Microsoft Research 文章 — https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/ ；论文 PDF（Task Ledger/Progress Ledger/stall counter ≤2/reset&replan）— https://www.microsoft.com/en-us/research/wp-content/uploads/2024/11/Magentic-One.pdf ；MAF 实现（max_stall_count、5-field progress ledger JSON）— https://nitinksingh.com/posts/maf-v1-16-magentic-orchestration/ ；autogen 源码 `_magentic_one_orchestrator.py`。
- **OpenAI Agents SDK / Swarm（handoff vs as-tool）**〔web〕：Orchestration and handoffs — https://developers.openai.com/api/docs/guides/agents/orchestration ；Agents SDK multi_agent — https://openai.github.io/openai-agents-python/multi_agent/ ；Respan《Agents SDK vs Swarm Migration（v0.17.1, 2026-05）》— https://www.respan.ai/articles/openai-agents-sdk-vs-swarm ；Aurelio AI multi-agent。
- **CrewAI / LlamaIndex / 框架对比**〔web〕：Fordel《AI Agent Frameworks 2026》— https://fordelstudios.com/research/state-of-ai-agent-frameworks-2026 ；bestaiweb《Graph vs Chat vs Crew》（state durability 对比）；AlterSquare《LangGraph vs CrewAI vs AutoGen》（token 5×、max_iterations/circuit breaker）；ZenML《CrewAI Alternatives》（LangGraph/ADK/Pydantic AI 定位）— https://www.zenml.io/blog/crewai-alternatives 。
- **Google ADK / Mastra / Pydantic AI**〔web〕：google/adk-docs workflow-agents（Sequential/Parallel/Loop）— https://github.com/google/adk-docs/blob/main/docs/agents/workflow-agents/index.md ；ADK workflows（graph-based 2.0、JoinNode、agent routing）— https://adk.dev/workflows/ ；Mastra createWorkflow；Pydantic AI（typed + durable，见下条）。
- **Durable execution（运行时）**〔web〕：Inngest《Durable Execution: The Key to Harnessing AI Agents》— https://www.inngest.com/blog/durable-execution-key-to-harnessing-ai-agents ；Zylos《Durable Execution Patterns for AI Agents》（Temporal $300M/$5B、journal replay/DB checkpoint/Saga；LangGraph/Pydantic AI/Agents SDK 采纳）— https://zylos.ai/research/2026-02-17-durable-execution-ai-agents ；youngju.dev《Durable Workflow Engines 2026》（Temporal/Inngest/Restate/DBOS）；digitalapplied《AI Workflow Orchestration Tools 2026》。
- **互操作协议 A2A/ACP/AGNTCY**〔web〕：A2A Protocol 官网 — https://a2a-protocol.org/ ；Google 捐赠 Linux Foundation — https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation ；Linux Foundation press（150+ 机构、2026-04 一周年）；Pickaxe《MCP vs A2A 2026》（AAIF 2025-12、ACP 并入）；Omar Santos《MCP vs A2A vs AGNTCY》（SLIM/Directory/Identity）。
- **失败模式 MAST**〔web〕：《Why Do Multi-Agent LLM Systems Fail?》arXiv 2503.13657 — https://arxiv.org/pdf/2503.13657v2 ；NeurIPS 2025（MAST-Data 1600+ traces、14 模式 3 类、κ=0.88、ChatDev 高层验证 +15.6%）— https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html ；Grigoryan 解读。
- **何时不该上多代理（Cognition×Anthropic）**〔web〕：Cognition《Don't Build Multi-Agents》《Multi-Agents: What's Actually Working》— https://cognition.ai/blog/multi-agents-working ；philschmid《Single vs Multi-Agent System》（read/write、token 4× vs 15× 对比表）— https://www.philschmid.de/single-vs-multi-agents ；Jason Liu《Why Cognition does not use multi-agent systems》；Anthropic 多代理研究（交叉域 1）。
- **Blackboard / Debate / Society of Minds**〔web〕：《LLM-based Multi-Agent Blackboard System》arXiv 2510.01285（数据发现 +13~57%）— https://arxiv.org/html/2510.01285v1 ；《MAVEN》arXiv 2605.07646（blackboard + 对抗式验证 + 知识缓存防幻觉累积）；iSolutions《Language Model Agents in 2025: Society of Mind Revisited》（debate/jury 降过度自信）。
