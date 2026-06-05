# AI 能力升级 · 研究路线图与子代理共享 Brief

> 本文件是「产品专家 Agent AI 能力升级」研究的**总路线图**，同时充当所有研究子代理的**共享上下文 brief**。
> 每个研究子代理开工第一步必须**完整读本文件**，再按"子代理产出契约"产出本域 findings。

---

## 1. 背景：被研究/被增强的对象是谁

「产品专家 Agent」是一个 **Cursor 原生**的产品从业者 Agent，定位**轻量聚焦**（不引入 LangGraph/Temporal 这类重运行时框架，优先把能力**文件化/提示化**为 policy / rule / protocol）。它有五项核心能力（skills）：

| 能力 | 目录 | 干什么 |
|---|---|---|
| 调研分析 | `skills/research-toolkit/` | 单产品/方向/全景/用户研究，含国内外社媒采集、体验、写作、三轮事实核查 |
| 产品策划 | `skills/education-prd-orchestrator/` | 从 0 到 1 写 PRD、校验文档与证据链 |
| AI 策划 | `skills/ai-planning-orchestrator/` | AI PRD、AI 脚本（服务工程化）、AI 测试/评测/调优（评测驱动开发） |
| Demo 开发 | `skills/product-demo-orchestrator/` | 可演示可交接的 Web/H5 demo + 上线 |
| SQL 数据查询 | `skills/aibi-query/` | 自然语言 → DBOPS 查询 → 结论/看板 |

**已有方法论库（policies/）**：`agent-team-methodology`（6 种团队架构模式 + 技能编写/测试 + 运维增量）、`llm-eval-methodology`（评测驱动开发 EDD 七段闭环）、`prompt-engineering-techniques`（22 个提示技术）、`agent-security-scan`（AgentShield 安全扫描）、`submission-review-contract`（写回审核契约）、`image-prompt-connector`。

**已有规则（.cursor/rules/）**：`task-navigator`（任务启动即主动分阶段规划、跨能力编排）、`product-expert-commands`（命令路由）。

**自我进化机制**：`/经验写回`、`/更新请求` → 整理方法写回仓库 PR + 契约测试（`tests/test_product_expert_agent.py` 仓库级 + 各 skill 的 `tests/test_*.py`），人审合并。

**运行时身份**：典型 **MCP 消费方** + 子代理编排者。可用 MCP/连接器：firecrawl、app-insight、小红书/微博/B站/抖音采集、antv-chart、google-trends、**claude-mem（21 工具，跨会话记忆）**、tavily、exa、serpapi、cursor-ide-browser 等。子代理通过 `Task` 工具按批次并行派发，**只回主代理、由主代理裁决**（agents-as-tools 模式）。

---

## 2. 研究使命

用户判断：**我们的 AI 能力在 agent 架构层、编排层、MCP/工具层、RAG 与上下文记忆层、意图/路由层、对话层缺少最先进的东西**，要求"穷尽式"扫描业界最先进做法（企业级 + 应用级），然后给出**怎么增强、完善、闭环**。

本研究分三步：
1. **穷尽式 SOTA 编目**：12 个域，每域产出一份 findings（≥45 条带出处的技术条目 + 趋势 + 对标 + 落地建议）。
2. **综合**：把 12 域的 P0/P1/P2 落地建议去重、排序、串成一张**增强路线图**，落到本仓库具体文件。
3. **闭环设计**：定义"研究 → 增强 → 评测 → 经验写回 → 再评测"的自我进化闭环。

> 关于"10000 个最先进方式"：以**穷尽式技术目录**实现——12 域 × ~50 条 ≈ 600+ 条带出处条目，覆盖"方方面面"；以质量与可追溯出处取胜，不堆无源数字。

---

## 3. 完整 12 域地图

| 域 | 名称 | 范围（covers） | 边界（cross-ref，不展开） | 状态 | 产出文件 |
|---|---|---|---|---|---|
| 1 | Agent 推理范式与架构 | 单体 Agent 推理控制流：CoT/ReAct/Plan-Execute/ReWOO/Self-Refine/Reflexion/ToT/LATS/CodeAct、test-time compute、推理模型、自进化(ADAS/DGM) | 团队编排→2；路由→3；记忆基建→6 | ✅ 已完成 | `findings/01-agent-reasoning.md` |
| 2 | 多代理协作与编排框架 | 团队拓扑(supervisor/hierarchical/handoff/as-tool/orchestrator-worker)、编排框架(LangGraph/MAF/CrewAI/ADK)、状态/持久化/durable、失败模式 MAST、何时不该上多代理 | 单体推理→1；A2A 工具角度→4；HITL 安全→10 | ✅ 已完成 | `findings/02-multi-agent-orchestration.md` |
| 3 | 意图识别与路由 | 意图分类、语义路由(semantic-router)、模型分级路由(RouteLLM)、任务/查询路由、澄清(EVPI)、护栏式路由 | 模型路由成本细节→12；对话内澄清落地→7 | ✅ 已完成 | `findings/03-intent-routing.md` |
| 4 | 工具与 MCP 生态 | 工具调用机制、MCP 协议/Registry/生态、工具设计、工具选择/工具RAG、沙箱代码执行、computer-use/浏览器、工具安全、缓存 | CodeAct 推理角度→1；A2A 编排→2；检索→5；OTel→9；注入→10；模型缓存→12 | ✅ 已完成 | `findings/04-tools-mcp.md` |
| 5 | **RAG 与检索增强** | 分块/嵌入/向量库、混合检索(BM25+dense)、重排、查询变换、GraphRAG、Agentic RAG、Adaptive/Self/CRAG、多模态 RAG、RAG 忠实度/接地 | 记忆/上下文角度→6；对话式查询改写→7；RAG 评测指标→9；接地安全→10 | ❌ 待补(Batch1) | `findings/05-rag-retrieval.md` |
| 6 | 上下文工程与记忆系统 | write/select/compress/isolate 四范式、context rot、记忆分类(CoALA)、记忆框架(MemGPT/Mem0/Zep/LangMem)、生命周期、claude-mem 接入 | 检索机制→5；反思推理角度→1；prompt 优化→11；记忆 eval→9 | ✅ 已完成 | `findings/06-context-memory.md` |
| 7 | 对话式 Agent 与对话管理 | DST/槽位、澄清/grounding/repair、混合主动、主动·ambient、语音(级联/端到端)、转人工、对话评估(τ²-bench) | 澄清路由角度→3；查询改写→5；persona 记忆→6；对话评测基建→9 | ✅ 已完成 | `findings/07-conversational-agents.md` |
| 8 | **企业级 Agent 工程与 AgentOps** | 部署运行时/serving、身份与授权(OAuth/scoped/least-priv)、多租户、AgentOps 生命周期(build→ship→run→govern)、成本/SLA 治理、合规、人机协同运营、企业参考架构(Agentforce/Bedrock Agents/Vertex Agent Builder/Copilot Studio/LangGraph Platform) | 安全运行时防御→10；评估可观测→9；编排运行时→2；成本/缓存技术→12 | ❌ 待补(Batch2) | `findings/08-enterprise-agentops.md` |
| 9 | **评估、Verifier 与可观测** | 离线 eval harness、LLM-as-judge/G-Eval、verifier/PRM/ORM、agent 轨迹评估(τ-bench/AgentBench/GAIA/SWE-bench)、user simulator、在线评估/可观测(OTel GenAI/Langfuse/Phoenix)、审计 | 评测方法论已有 policy(llm-eval) 须对齐;RAG 指标→5;安全 red-team→10;自进化评分→1/11 | ❌ 待补(Batch1) | `findings/09-eval-observability.md` |
| 10 | Agent 安全、护栏与对齐 | 威胁框架(OWASP LLM Top10/Agentic/ATLAS/NIST)、提示注入/越狱、运行时护栏、输入输出校验、PII/审核、幻觉缓解、HITL/最小权限/沙箱、身份审计、red-team | 工具投毒接口角度→4；judge 基建→9；受限解码产物→11；自检推理→1 | ⚠️ 已完成但**全程未联网**(原版 100% 训练知识)，Batch2 联网校验刷新 | `findings/10-safety-guardrails.md` |
| 11 | **Prompt/上下文优化与结构化输出** | 自动 prompt 优化(DSPy/MIPROv2/GEPA/APE/ACE)、prompt 版本化/管理、结构化输出/受限解码(JSON Schema/Outlines/guidance/strict)、输出契约、few-shot 选择 | 手写提示技巧已有 policy(prompt-eng) 须对齐;记忆演化 playbook→6;评分→9;输出安全→10 | ❌ 待补(Batch1) | `findings/11-prompt-optimization-structured-output.md` |
| 12 | **模型路由、推理优化与成本/缓存** | 模型分级路由(RouteLLM/Not Diamond/OpenRouter Auto)、级联(cascade/FrugalGPT)、prompt 缓存、语义缓存(GPTCache)、KV-cache/推理服务(vLLM/SGLang)、batching、思考预算成本、token 经济 | 路由的意图判定角度→3；工具结果缓存→4；记忆压缩省 token→6 | ❌ 待补(Batch1) | `findings/12-model-routing-cost.md` |

> 域 8、9 的相邻处划清：**域 9 = 质量评估 + 追踪可观测（对不对、追得到）**；**域 8 = 部署运行/身份多租户/成本SLA治理/生命周期（跑得起、管得住、合得规）**。

---

## 4. 子代理产出契约（每份 findings 必须严格遵守）

输出文件 = `research/ai-capability-upgrade/findings/0N-<slug>.md`，结构与已完成的 7 份**完全一致**：

1. **标题 + 元信息头**：`# 域 N：<名称>` + 子代理名 + 回写路径 + **来源标注规范**（见下）+ **边界说明**（本域聚焦什么、哪些主题交叉引用到哪个域不展开）。
2. **领域概述**（2–4 段）：这一层是什么、2025-2026 范式跃迁主线、**对「产品专家 Agent」的具体意义与当前缺口**（要点名具体 skill/policy/文件）。
3. **SOTA 技术目录**（**≥45 条**，按子类分组的表格）：列 = `技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源`。成熟度口径：`实验/成长/成熟/事实标准`。**尽量穷尽**，企业级 + 应用级 + 研究前沿都要。
4. **2025-2026 前沿与趋势**（**10 条**）：每条一句结论 + 证据/数据 + 〔web〕或〔知识〕标注。
5. **对标产品专家 Agent**（表格）：列 = `我们现状 | 差距 | 建议增强（P0/P1/P2）`。要点名本仓库具体文件/skill/policy。
6. **落地建议**（每条给三要素）：**放哪个文件 / 做什么 / 验收信号**（验收信号尽量可被 `tests/` 契约测试断言：文件存在 + 关键标记 + 触发词）。区分 P0（对单体 Agent 立刻可用的 policy/rule/protocol 层）/ P1 / P2（需重基建，标注交叉域）。
7. **参考来源**：尽量带**可点击 URL**，标 〔web〕（本轮联网核实）/〔知识〕（训练知识未逐条复核）。

**来源标注规范（务必遵守，诚实优先）**：
- 〔web〕= 本轮用 WebSearch/WebFetch 或 MCP 搜索工具（tavily/exa/firecrawl/serpapi）**本轮核实**，附 URL。
- 〔知识〕= 训练知识、未逐条联网复核（**只用确有其物的框架/论文/产品**，把握不准的标"(待核实)"，**严禁编造**不存在的库/论文/数字）。
- 今天是 **2026-06-05**，搜索"latest""2026"版本，给出现状（版本号/合并/继任关系尽量核实）。

**质量基线**：对齐已完成的 `findings/04-tools-mcp.md`（77 条）、`findings/01-agent-reasoning.md`（48 条）的深度与可追溯性。

---

## 5. 编排方法（本研究怎么跑）

- 模式 = **扇出/扇入（Fan-out/Fan-in）+ 生成-检验**：主代理把缺失域并行扇出给子代理 → 子代理各自联网研究并回写 findings → 主代理汇总裁决 → 综合成路线图。
- **单批并发 ≤ 4 个子代理**（`agent-team-methodology` 第一部分硬约束）；子代理之间不直接通信，由主代理中转与冲突裁决；每个子代理聚焦一个域、必落标准产物。
- Batch 1（4）：域 5 / 域 9 / 域 11 / 域 12。Batch 2（2）：域 8 + 域 10 联网刷新。
- 子代理回主代理时附：**1 段摘要（本域最关键的 3 个缺口 + 最高优先 P0）+ findings 文件路径 + 关键未决/置信度**（防 MAST FM-2.4 信息隐瞒）。

---

## 6. 综合产物（研究完成后由主代理产出）

`research/ai-capability-upgrade/SYNTHESIS.md`：
1. **总览**：12 域一句话结论 + 跨域共性缺口（预判：运行时语义/状态、统一自检与接地、评测基建、机器侧记忆、成本治理）。
2. **增强路线图**：把 12 域的 P0/P1/P2 去重合并，按"依赖关系 + 杠杆/成本"排序，落到具体文件（新增 policy / 改 rule / 改 skill / 补 test）。
3. **新增/改动文件清单**：每个文件做什么、被谁引用、验收信号。
4. **自我进化闭环设计**：研究 → 增强 → With-skill vs Baseline 评测 → `/经验写回` → 再评测 的可执行闭环（对齐 `llm-eval-methodology` 七段闭环 + `agent-team-methodology` 第三/四部分）。
5. **实施分期**：P0 先做哪几件（最小可落地集）、P1/P2 排期。

---

## 7. 进度看板

| 域 | 状态 | 备注 |
|---|---|---|
| 1,2,3,4,6,7 | ✅ 已完成 | 前序会话产出，质量达标 |
| 5,9,11,12 | ✅ 已完成 | Batch1 联网产出（域12 因限流重跑一次后完整） |
| 8 | ✅ 已完成 | 子代理两轮 `resource_exhausted` 失败 → **主代理亲写**（知识为主，标未联网） |
| 10 | ✅ 已完成（未联网） | 原版未联网；因全程限流暂未刷新，综合中已标注，建议后续补一次联网校验 |
| SYNTHESIS | ✅ 已完成 | `SYNTHESIS.md`：跨域整合(20→~12) + 三期路线图 + 闭环 + task-navigator 整合 + MVP |

> **限流事故记录**：本次研究子代理共 3 次 `resource_exhausted`（域11 子-子代理、域12 首跑、域8 两轮）。根因=4 并发深度联网 + 子代理派生 + 反复重试失效的 tavily。已转化为 SYNTHESIS §3/§6 的"成本预算护栏 + 限流即停用不重试"建议。tavily MCP 本环境 `Invalid API key` 不可用。
