# 域 8：企业级 Agent 工程与 AgentOps

> 研究者：主代理直接产出（域 8 子代理两轮均 `resource_exhausted` 失败，环境联网/模型配额严重受限）。
> 来源标注：本域**以训练知识为主、未逐条联网核实**（与域 10 同因：本轮联网基础设施受限），来源统一标〔知识〕；版本号/GA 状态/具体能力可能已演进，把握不准处标"(待核实)"，**未编造**不存在的平台/产品。可用时建议后续做一次联网校验刷新。
> 边界：本域聚焦 **Agent 的"平台面"——部署运行/身份授权/多租户/生命周期(AgentOps)/成本SLA治理/合规**。运行时注入防御与护栏见域 10；评估质量/judge/轨迹见域 9；编排状态机/handoff/durable 机制见域 2；缓存/路由/推理成本**技术细节**见域 12（本域只取其"治理面"）；对外代理互操作 A2A/AGNTCY 见域 2。本域只取这些主题的**企业工程/运营角度**并交叉引用。

---

## 领域概述

「企业级 Agent 工程与 AgentOps」回答的是：**一个 Agent 从 demo 走向"团队/组织级生产系统"时，怎么部署、怎么给身份与权限、怎么多租户隔离、怎么按生命周期持续交付与治理、怎么把成本与可靠性管住、怎么满足合规审计**。2025-2026 这一层的范式跃迁有四条主线：①**大厂把"托管 Agent 运行时"做成产品**——AWS Bedrock AgentCore、Google Vertex AI Agent Engine、Microsoft Azure AI Foundry Agent Service、Salesforce Agentforce、LangGraph Platform 等，把"会话/状态托管 + 身份 + 记忆 + 可观测 + 沙箱工具执行"打包成平台，开发者不再自己拼运行时；②**"Agent 身份"成为新的安全/治理焦点**——非人类身份(NHI)爆发，OAuth 2.1 scoped token、on-behalf-of 委托、最小权限、短期凭据成为 agent 接工具/数据的默认要求，业界开始讨论"agent 专用身份标准"；③**LLMOps 演进为 AgentOps**——评估(域9)/可观测/版本化/CI-CD/金丝雀/回滚围绕"多步轨迹 + 工具 + 成本"重建，"评估即发布门禁"成为共识；④**治理从"软建议"走向"可强制 + 可审计"**——预算熔断、policy-as-code、审批流、审计日志，叠加 EU AI Act / NIST AI RMF / ISO/IEC 42001 的合规压力，"跑飞的自主 Agent"成为头号运营与成本事故源。

对「产品专家 Agent」而言，本域**大部分是"远"的（P2）**：它是 **Cursor 原生、轻量聚焦、近似单用户**的 Agent——没有自有 serving、不做多租户、不对外提供 SLA，因此"托管运行时 / 多租户隔离 / 企业 SSO / 平台级 durable"这些**重企业基建当前不适用**，盲目引入会与"轻量聚焦"定位冲突。但本域有**四类企业实践值得"轻量化采纳"为 P0/P1**，因为它们本质是"纪律"而非"基建"：① 把已有的 `/经验写回` + 契约测试 + `/安全扫描` + `/检查Agent更新` 显式定义成一条 **AgentOps 生命周期(build→eval→ship→govern)**，让自我进化有章可循；② **MCP/连接器最小权限 + 凭据卫生**（与域 10 运行时防御同源）；③ 不可逆动作的**审计追溯**轻量化（动作/影响/批准/结果留痕）；④ **任务级成本预算护栏**（与域 12 成本纪律同源）。本域的核心价值就是：**把企业级"管得住、合得规、可追溯"的思想，裁剪成 Cursor 原生可落地的文件化纪律，并明确划出"现在不做、未来产品化才做"的 P2 边界。**

---

## SOTA 技术目录

> 按子类分组，共 **52 条**（10 子类）。成熟度口径：`事实标准`（行业默认/已成规范）、`成熟`（生产广泛使用）、`成长`（活跃、生产可用但仍演进）、`实验`（早期/preview）。本域条目绝大多数标〔知识〕（未本轮联网核实）。

### A. 企业级 Agent 平台 / 托管运行时（大厂"开箱即用"栈）

| 平台/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| AWS Bedrock AgentCore | 托管 Agent 运行时套件：Runtime(会话隔离执行)+Gateway(工具/MCP)+Identity+Memory+Observability+Browser/Code 工具 | AWS 栈、要托管运行时+身份+记忆+可观测一体 | 成长(2025 preview→GA 推进中，待核实) | AWS Bedrock AgentCore | 〔知识〕 |
| AWS Bedrock Agents | 早期托管 Agent（action groups + KB + guardrails），AgentCore 之前的形态 | 简单托管 agent、RAG+工具编排 | 成熟 | AWS Bedrock Agents | 〔知识〕 |
| Google Vertex AI Agent Engine | 托管 agent 运行时（部署/伸缩/会话/记忆/追踪），配 ADK 与 Agent Builder | GCP/Gemini 栈、要托管部署 ADK 代理 | 成长 | Vertex AI Agent Engine(原 Reasoning Engine) | 〔知识〕 |
| Microsoft Azure AI Foundry Agent Service | 托管 agent 服务（线程/工具/连接器/追踪/内容安全），配 Agent Framework | Azure 栈、企业治理与连接器 | 成长 | Azure AI Foundry Agent Service | 〔知识〕 |
| Microsoft Copilot Studio | 低代码企业 Agent 搭建（含自主/触发式 agent、连接器、DLP/治理） | M365 生态、业务用户搭 agent | 成熟 | Copilot Studio | 〔知识〕 |
| Salesforce Agentforce | CRM 原生 agent 平台（Atlas 推理引擎 + Agent Builder + Actions + 防护） | Salesforce 生态、客服/销售 agent | 成长 | Agentforce (1.0/2.0，待核实) | 〔知识〕 |
| LangGraph Platform | 把 LangGraph 图编排上托管：长程有状态部署 + 持久化 + 可观测(LangSmith) | 已用 LangGraph、要生产托管 | 成长 | LangChain LangGraph Platform | 〔知识〕 |
| IBM watsonx Orchestrate | 企业 agent 编排与目录（技能/agent 复用、治理） | 企业流程自动化、IBM 栈 | 成长 | watsonx Orchestrate | 〔知识〕 |
| ServiceNow AI Agents / Now Assist | ITSM/工作流原生 agent，编排进企业流程 | ServiceNow 生态运营自动化 | 成长 | ServiceNow AI Agents | 〔知识〕 |
| 垂直/独立平台 | Sierra(客服)、Cohere North、Writer、Glean Agents、Adept/其它 | 特定场景或独立栈 | 成长 | 多家 | 〔知识〕 |

### B. 部署 / Serving / 会话状态托管

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 托管会话/线程状态 | 平台托管 thread/session 状态，免自建状态存储 | 多轮、跨请求续接 | 成熟 | Foundry threads / Vertex sessions / OpenAI Conversations | 〔知识〕 |
| 受管沙箱工具执行（规模化） | 平台侧隔离执行代码/工具（microVM/容器），多租户安全 | 跑不可信代码/CodeAct 上量 | 成长 | E2B / AgentCore Runtime / Daytona(待核实) | 〔知识〕 |
| Serverless / 事件驱动 agent | 按需触发、无常驻、按用量计费 | 间歇负载、成本敏感 | 成长 | Lambda+Bedrock / Cloud Run / Inngest(域2) | 〔知识〕 |
| 自托管 agent 运行时 | 自己跑编排+模型网关（数据驻留/合规/成本） | 强合规、要控数据与成本 | 成长 | LangGraph 自托管 / 自建 | 〔知识〕 |
| 弹性伸缩与并发隔离 | 每会话/租户隔离 + 自动扩缩 | 上量、多用户并发 | 成熟 | 各云平台 | 〔知识〕 |

### C. Agent 身份与授权（NHI · 最小权限 · 委托）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 非人类身份（NHI）治理 | 给 agent/服务一个可治理身份（非复用人类账号），可发证/吊销/审计 | 任何 agent 调企业资源 | 成长 | Okta/Auth0 for AI Agents、Microsoft Entra Agent ID(待核实) | 〔知识〕 |
| OAuth 2.1 + scoped token | agent 用最小作用域、短期 token 访问 API/工具 | agent 接第三方/企业 API | 事实标准 | MCP 远程 OAuth 2.1(域4)、各 IdP | 〔知识〕 |
| On-behalf-of / 委托授权 | agent 以"代表某用户"的受限权限行事，权限不超过用户本人 | 多租户、用户数据访问 | 成熟 | OBO flow（OAuth）、各云 | 〔知识〕 |
| 最小权限 / RBAC / ABAC | 按角色/属性精确授权，默认拒绝 | 所有特权操作 | 事实标准 | IAM 通用 | 〔知识〕 |
| 短期凭据 / 密钥托管 | 动态短期凭据替代长期密钥，集中托管轮转 | 防密钥泄露/长期暴露 | 成熟 | Vault / Secrets Manager / KMS | 〔知识〕 |
| 工作负载身份（SPIFFE/SPIRE） | 给工作负载发可验证身份（mTLS/SVID），零信任互信 | 服务/agent 间零信任通信 | 成长 | SPIFFE/SPIRE | 〔知识〕 |
| Agent 身份新兴标准 | 业界在推"agent 专用身份/凭据"规范（可发现+可问责） | 跨组织 agent 协作前瞻 | 实验 | 多家提案(待核实) | 〔知识〕 |
| 工具/数据访问的内外隔权 | 外部内容/低信任来源不得触发高权限工具（防注入提权） | 防间接注入提权（接域10） | 成长 | Dual-LLM/能力控制(域10) | 〔知识〕 |

### D. 多租户 · 隔离 · 数据驻留

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 租户隔离（数据/会话/记忆） | 按 tenant 隔离存储、会话与记忆，杜绝串户 | SaaS 多客户 | 事实标准 | 平台多租户设计 | 〔知识〕 |
| 命名空间 / projectId 作用域 | 用 namespace/项目 ID 隔离记忆与检索（轻量隔离） | 单实例多项目/任务 | 成熟 | claude-mem projectId（域6）、向量库 namespace | 〔知识〕 |
| 数据驻留 / 区域合规 | 数据存指定区域，满足主权/合规 | GDPR/数据主权 | 成熟 | 各云 region 控制 | 〔知识〕 |
| 每租户预算/限流 | 按租户配额防单租户拖垮系统/超支 | 多租户成本与公平 | 成长 | 网关配额（接 F/域12） | 〔知识〕 |

### E. AgentOps 生命周期（LLMOps → AgentOps）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| build→eval→ship→run→monitor→govern | agent 全生命周期闭环：构建→评估门禁→发布→运行→监控→治理 | 任何要持续迭代的 agent | 成长（新共识） | AgentOps 实践 | 〔知识〕 |
| 评估即发布门禁（eval gate） | 发布前必须过评估集阈值，回归即阻断（接域9） | 防质量回退上线 | 成长 | LangSmith/Langfuse/CI（域9） | 〔知识〕 |
| Agent 版本化 + 变更管理 | prompt/工具/模型/policy 改动均版本化、可追溯、可回滚 | 改动多、要可回溯 | 成熟 | prompt registry（域11）、git | 〔知识〕 |
| 金丝雀 / 灰度 / 影子发布 | 新版小流量先发或影子对比，验稳再全量 | 高风险变更上线 | 成熟 | 部署平台通用 | 〔知识〕 |
| AgentOps 平台 | 专门做 agent 监控/评估/成本/会话回放的运营台 | 上量后的统一运营 | 成长 | AgentOps.ai / Maxim / Galileo / Arize / W&B Weave / Langfuse(域9) | 〔知识〕 |
| 提示/工具/模型解耦发布 | 把易变的 prompt/工具/模型与代码解耦，免重部署即可改 | 快速迭代、运行时切换 | 成长 | prompt registry + 配置中心 | 〔知识〕 |
| 数据飞轮 / 生产反馈回流 | 线上失败→评测集→优化→再发布的闭环 | 持续改进 | 成长 | 评测集"失败回放"桶（域9/llm-eval） | 〔知识〕 |

### F. 成本 / SLA / 可靠性治理（治理面，技术细节见域 12/2）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 预算/配额 + 熔断（enforcement） | 不只观测、能在超预算/超步数时拒绝调用或停机 | 防 agent 跑飞烧钱 | 成长 | 网关 circuit breaker（接域12） | 〔知识〕 |
| Observability vs Enforcement 区分 | 记录(只看) ≠ 强制(能拦)；治理要二者兼备 | 设计成本护栏时 | 成长 | Langfuse/Helicone(观测) + 网关(强制) | 〔知识〕 |
| LLM/Agent FinOps | 按 tenant/feature/route 归集成本，可归因可预测 | 成本可见与分摊 | 成长 | 各可观测平台成本视图 | 〔知识〕 |
| 全局步数/轮次/时间预算 | 给 agent 设最大步数/工具调用/时长上限，超限收敛 | 防无限循环（接域2） | 成熟 | 各框架 max_iterations | 〔知识〕 |
| SLA / 可靠性目标 | 定义可用性/延迟/成功率目标并监控 | 对外服务承诺 | 成熟 | 通用 SRE | 〔知识〕 |
| Durable execution（平台级） | 崩溃后从断点恢复不重复付费（机制见域2） | 长程、贵、有副作用 | 成长 | Temporal/DBOS（域2） | 〔知识〕 |
| 优雅降级 / 兜底 | 模型/工具不可用时降级而非整体失败 | 韧性 | 成熟 | fallback 路由（域12） | 〔知识〕 |

### G. 治理 / 合规 / 审计（可强制 + 可追溯）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 审计日志 / 可追溯 | 谁/何时/对什么/凭何批准 做了什么，结构化留痕 | 合规、事后取证、责任归属 | 成熟 | 平台审计 + OTel(域9) | 〔知识〕 |
| Policy-as-code | 把准入/权限/合规规则写成可执行策略，自动校验拦截 | 规模化治理、可审计 | 成长 | OPA/Rego、各平台 policy | 〔知识〕 |
| 审批流 / 变更评审 | 高风险变更/动作走审批，留批准记录 | 高风险/不可逆操作 | 成熟 | 通用工单/PR 评审 | 〔知识〕 |
| NIST AI RMF | AI 风险管理框架（治理/映射/度量/管理） | 组织级治理对齐 | 成熟 | NIST AI 100-1/600-1 | 〔知识〕 |
| EU AI Act | 欧盟 AI 法（按风险分级义务，分阶段生效） | 面向欧盟、合规义务 | 成长（落地中） | EU AI Act | 〔知识〕 |
| ISO/IEC 42001 | AI 管理体系（AIMS）认证标准 | 体系化合规认证 | 成长 | ISO/IEC 42001:2023 | 〔知识〕 |
| 负责任 AI / 模型卡 / 数据血缘 | 公平/透明/可解释 + 模型卡 + 数据来源血缘 | 合规与信任 | 成熟 | 各 RAI 工具链 | 〔知识〕 |

### H. 规模化人机协同运营（运营面，机制见域 7/10）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Agent Inbox / 审批队列 | 把"需人确认"的 agent 请求汇成收件箱，批量审/批 | 规模化 human-on-the-loop | 成长 | LangChain Agent Inbox | 〔知识〕 |
| 高风险动作前审批（HITL） | 外发/删除/写库/发布前停下等批准（机制见域10） | 不可逆动作 | 事实标准 | LangGraph interrupt（域2/10） | 〔知识〕 |
| 升级 / 转人工（escalation） | 低置信/超范围/失败时转人工坐席 | 客服/高风险 | 成熟 | 各客服 agent 平台 | 〔知识〕 |
| Human-on-the-loop 监督 | 人监督一批 agent、按需介入而非逐条操作 | 上量后的监督模式 | 成长 | ambient agent（域7） | 〔知识〕 |

### I. Agent 注册 / 目录 / 发现 / 互操作（对外协作，详见域 2）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Agent 注册表 / 能力目录 | 登记可用 agent/技能及其能力，供发现与复用 | 多 agent/多技能组织 | 成长 | watsonx Orchestrate 目录、A2A Agent Card | 〔知识〕 |
| A2A（Agent2Agent） | 跨框架/厂商 agent 互操作协议（Agent Card + JSON-RPC） | 与外部异构 agent 协作 | 成长（详见域2） | Linux Foundation/AAIF | 〔知识〕 |
| MCP Registry | 工具/server 的可发现注册表（域4） | 工具治理与发现 | 成长 | 官方 MCP Registry（域4） | 〔知识〕 |
| AGNTCY / Internet of Agents | 发现/身份/消息/可观测的代理互联基建 | 规模化代理互联前瞻 | 成长（详见域2） | Cisco Outshift/LF | 〔知识〕 |

### J. 运营可观测（运营面，评估/追踪基建见域 9）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 运营仪表盘（成功率/成本/延迟） | 把 agent 运行健康度做成运营看板 | 上量后的日常运营 | 成长 | Arize/Galileo/Langfuse(域9) | 〔知识〕 |
| 会话回放 / 轨迹审查 | 回放问题会话定位失败步（接域9轨迹评估） | 事故复盘/调试 | 成长 | 各 AgentOps 平台 | 〔知识〕 |
| 在线漂移 / 异常告警 | 监控质量/成本/分布漂移并告警 | 防线上悄悄退化 | 成长 | 可观测平台 + judge 采样(域9) | 〔知识〕 |

---

## 2025-2026 前沿与趋势

1. **大厂把"托管 Agent 运行时"产品化**〔知识〕：AWS Bedrock AgentCore、Vertex AI Agent Engine、Azure AI Foundry Agent Service、LangGraph Platform 把"会话/状态托管 + 身份 + 记忆 + 工具/沙箱执行 + 可观测"打包，开发者从"自拼运行时"转向"用平台 + 写编排"。
2. **"Agent 身份(NHI)"成独立安全品类**〔知识〕：agent 不再复用人类账号或长期密钥，转向最小权限 scoped token + on-behalf-of 委托 + 短期凭据；IdP 厂商（Okta/Auth0、Microsoft Entra 等）推"AI agent 身份"产品，业界讨论 agent 专用身份标准。
3. **LLMOps 正式演进为 AgentOps**〔知识〕：评估/可观测/版本化/CICD 围绕"多步轨迹 + 工具 + 成本"重建；"评估即发布门禁、回归即阻断"成为共识（与域 9 强耦合）。
4. **治理从"可观测"走向"可强制"**〔知识〕：业界严格区分 observability（只记录）与 enforcement（能在超预算/超步数时拒绝/熔断）；"跑飞的自主 Agent"被列为头号运营与成本事故源。
5. **合规压力实质化**〔知识〕：EU AI Act 分阶段生效、NIST AI RMF、ISO/IEC 42001 推动组织把 AI 治理从 PPT 落到 policy-as-code + 审计日志 + 审批流。
6. **低代码企业 Agent 平台普及**〔知识〕：Copilot Studio、Agentforce、watsonx Orchestrate 让业务用户搭 agent，治理(DLP/权限/审计)成为这些平台的核心卖点而非附属。
7. **"评估 + 可观测"市场爆发**〔知识〕：AgentOps.ai、Maxim、Galileo、Arize、W&B Weave、Langfuse 等专做 agent 监控/评估/会话回放/成本，OTel GenAI 语义约定成为跨平台标准底座（域 9）。
8. **多 agent 互操作标准化与目录化**〔知识〕：A2A（Agent Card + 注册发现）+ MCP Registry + AGNTCY 让 agent/工具"可发现、可复用、可治理"（域 2/4）。
9. **成本治理成一等工程**〔知识〕：LLM/Agent FinOps（按 tenant/feature/route 归因）、每租户预算配额、缓存与路由（域 12）从"优化技巧"变成"上生产的前置条件"。
10. **"单用户 demo → 团队/组织产品"是最大跃迁点**〔知识〕：身份、多租户、审计、SLA、成本治理这些"非功能性"工程，往往是 agent 从好用 demo 走向可托付生产系统的真正瓶颈，而非模型能力。

---

## 对标产品专家 Agent

> 核心命题：产品专家 Agent 是 **Cursor 原生、轻量聚焦、近似单用户**，多数企业级特性是 **P2（未来面向团队/组织产品化才做）**；但有 **4 类"纪律型"企业实践值得轻量化采纳为 P0/P1**——它们本质是把已有资产（`/经验写回`、契约测试、`/安全扫描`、连接器纪律）**显式成体系**，而非引入重基建。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `/经验写回`·`/更新请求`→PR+契约测试人审合并；`/安全扫描`；`/检查Agent更新`；`submission-review-contract.md` | 自我进化的各环节**未串成显式生命周期**：build(写回)→eval(测试)→ship(合并)→govern(扫描/版本) 散落，无"门禁顺序与准入"总图 | **P0**：新增 `policies/agentops-lifecycle.md`（或并入 `submission-review-contract.md`），把现有环节定义成 **build→eval→ship→govern 闭环 + 各阶段准入门禁**（接域9评估门禁、域10安全闸） |
| 契约测试 = 文件存在性 + 关键词（域9已指出） | 无"评估即发布门禁"——写回质量靠人审，无量化阈值阻断回退 | **P1**：把"With-skill vs Baseline 量化 + pass@k"设为写回合并门禁（与域9/域1/域11 同一条闭环） |
| MCP/连接器：按需安装 + 不可用降级 + 人工降级清单（强项） | **无最小权限模型 / 凭据卫生纪律**：连接器/MCP 未按读/写/破坏性分级，密钥管理无显式约定 | **P1**：在 `tool-use-protocol.md`(域4)/`agent-safety-protocol.md`(域10) 增"工具最小权限 + 凭据卫生（短期/集中/不进仓库）+ 内外隔权"（接域10 P1-1） |
| 写操作走 Cursor 原生确认；`/安全扫描` 写回前跑 | **不可逆动作无结构化审计追溯**：做了哪些外发/删除/写库、是否经批准，无留痕 | **P1**：不可逆动作轻量审计日志（动作/影响/批准/结果），落 `tasks/{task}/.meta/`（与域10 P2-1 同一条） |
| `agent-team-methodology` 第四部分有 Token 优化意识 | **无任务级成本预算护栏**：长任务/扇出无"最大子代理数/调用数/预算"硬上限与超限收敛（本次三轮 `resource_exhausted` 正是反面教材！） | **P0/P1**：成本预算护栏写入 `policies/`（接域12）——单任务最大子代理/调用/重试上限 + 超限"收敛出当前最佳"而非空转（直接呼应本次限流事故） |
| `task-navigator` 能力库 = 隐式"agent 目录"；五能力清晰 | 能力目录是**散文式**，非结构化可发现清单（轻量"注册表"） | **P2**：把五能力做成结构化能力清单（名/触发/输入槽/产物），供路由(域3)与未来发现复用——轻量即可，不引 A2A |
| 单用户、无多租户/SLA/SSO/serving | 多租户隔离、企业 SSO、对外 SLA、平台级 durable、托管 serving | **P2（明确不做）**：与"轻量聚焦"冲突；仅当产品专家 Agent 要**面向团队/组织产品化**时再评估，届时优先"复用大厂托管平台"而非自建 |
| 无合规义务（内部工具） | EU AI Act/ISO 42001/policy-as-code/模型卡 | **P2（备忘）**：当前内部使用无强制合规；若对外产品化，按风险分级补合规 |

---

## 落地建议

> 原则：**只采纳"纪律型"企业实践（把已有资产显式成体系），坚决不引重企业基建**（多租户/serving/SSO/durable runtime 标 P2 且默认不做）。与本仓库"Cursor 原生、轻量聚焦"一致。每条给"放哪个文件 / 做什么 / 验收信号"。**本域多数落地与域 9/10/12 同源——综合时应合并，不重复造文件。**

### P0-1 AgentOps 生命周期总纲 `policies/agentops-lifecycle.md`
- **放哪**：`policies/agentops-lifecycle.md`（新；或作为 `submission-review-contract.md` 的"生命周期"前置章节）。
- **做什么**：Why-First 把现有自我进化环节串成一张 **build→eval→ship→run→govern** 闭环图 + 各阶段**准入门禁**：build=`/经验写回` 产出增量 delta（接域6/11 ACE）；eval=契约测试 + With-skill vs Baseline + 轨迹评估（接域9）；ship=PR 人审合并 + 版本号/CHANGELOG（接 `/检查Agent更新`）；govern=`/安全扫描` + red-team 清单（接域10）+ 成本护栏（接域12）。明确"门禁不过不得进入下一阶段"。
- **验收信号**：`tests/test_product_expert_agent.py` 断言文件存在且含标记 `build→eval→ship→govern`/`准入门禁`/`回归阻断`；`submission-review-contract.md` 引用它。

### P0-2 任务级成本预算护栏（直接呼应本次三轮 resource_exhausted 事故）
- **放哪**：`policies/agent-team-methodology.md` 第四部分新增"成本预算护栏"小节（与域12 成本纪律合并）。
- **做什么**：给多代理/扇出任务设**硬上限**——单任务最大并发子代理数（沿用 ≤4）、最大累计子代理数、最大联网调用数、最大重试数、（可选）时间/轮次上限；**超限即收敛**："停止新派、用当前已得最佳结果交付 + 标注未尽项"，而非空转或反复重试（本次教训：失败的子代理反复重试坏掉的 tavily 加剧了限流）。并写"**外部工具/MCP 报限流/鉴权失败时：立即停用该工具、降级备用通道或纯知识，禁止反复重试**"。
- **验收信号**：方法论含 `成本预算护栏`/`超限收敛`/`限流即停用不重试` 标记；契约测试断言标记存在；`subagent-search.md` 引用它。

### P1-1 工具最小权限 + 凭据卫生（与域10 P1-1 合并）
- **放哪**：`policies/tool-use-protocol.md`(域4新建) 或 `policies/agent-safety-protocol.md`(域10新建) 的"最小权限"小节。
- **做什么**：MCP/连接器按 **读/写/破坏性** 分级；破坏性默认需 HITL（接域10 P0-3）；**凭据卫生**：密钥不进仓库（已有 `security_self_check`）、优先短期/环境注入、第三方 MCP 入 `mcps/` 前做信任分级（接域4 P0-3）；**内外隔权**：外部内容不得直接触发特权工具。
- **验收信号**：小节含 `读/写/破坏性`/`凭据卫生`/`内外隔权` 标记；现有 MCP/连接器各标权限级别。

### P1-2 不可逆动作审计追溯（与域10 P2-1 合并）
- **放哪**：`tasks/{task}/.meta/` 增"高风险动作日志" + `submission-review-contract.md` 评审项。
- **做什么**：执行外发/删除/写库/发布等不可逆动作时，结构化留痕 **动作 / 影响范围 / 批准状态(谁何时) / 结果**；轻量 markdown 表或 JSONL 即可。
- **验收信号**：含写/外发动作的任务产出"高风险动作日志"；评审清单含"高风险动作是否留痕+经批准"。

### P1-3 评估即发布门禁（接域9，写回闭环的"硬阈值"）
- **放哪**：`policies/agentops-lifecycle.md` 的 eval 阶段 + `submission-review-contract.md`。
- **做什么**：`/经验写回` 合并前，除现有契约测试外，附 **With-skill vs Baseline 量化 + pass@k**（域9 提供方法/脚本）；关键指标回归即阻断合并。先人审 + 半自动，不引重平台。
- **验收信号**：写回 PR 模板含"量化对比 + pass@k + 是否回归"；门禁纳入合并条件。

### P2-1 结构化能力目录（轻量"注册表"）
- **放哪**：`policies/` 或 `.cursor/rules/` 下一份结构化能力清单（可与域3 `capability-utterances.yaml`、域7 `capability-slots.yaml` 合并为一份 `capability-registry`）。
- **做什么**：把五能力做成结构化条目（名/命令/触发/输入槽/产物/依赖），供路由、澄清门禁、未来发现复用；不引 A2A。
- **验收信号**：清单覆盖五能力且字段齐全；被路由/对话 protocol 引用。

### P2-2 企业基建（明确不做，仅触发式备忘）
- **放哪**：本文件备忘 + `agentops-lifecycle.md` 附录。
- **做什么**：记录触发条件——**仅当产品专家 Agent 要面向团队/组织产品化**时，再评估：托管运行时（优先用大厂平台而非自建）、多租户隔离、企业 SSO/agent 身份、对外 SLA、平台级 durable、合规（EU AI Act/ISO 42001）。当前一律**不做**，避免与轻量定位冲突。
- **验收信号**：备忘列出触发条件清单；不产生立即代码改动。

---

## 参考来源

> 本域**全程未联网核实**（环境联网/配额受限，子代理两轮 `resource_exhausted`），以下均为业界通用平台/标准名，标〔知识〕；版本号/GA 状态/具体能力可能已演进，把握不准处已标"(待核实)"，**未编造**不存在的平台/产品。建议后续做一次联网校验刷新（与域 10 一并）。

- 〔知识〕企业 Agent 平台：AWS Bedrock Agents / Bedrock AgentCore（Runtime/Gateway/Identity/Memory/Observability）；Google Vertex AI Agent Builder / Agent Engine（原 Reasoning Engine）+ ADK；Microsoft Copilot Studio + Azure AI Foundry Agent Service + Agent Framework；Salesforce Agentforce（Atlas 推理引擎）；LangChain LangGraph Platform；IBM watsonx Orchestrate；ServiceNow AI Agents；Sierra；Cohere North；Glean Agents。
- 〔知识〕Agent 身份/授权：OAuth 2.1 + scoped token；On-behalf-of 委托；最小权限/RBAC/ABAC；HashiCorp Vault / AWS Secrets Manager / KMS；SPIFFE/SPIRE 工作负载身份；Okta/Auth0 "for AI Agents"、Microsoft Entra Agent ID（待核实）；MCP 远程 OAuth 2.1（域4）。
- 〔知识〕AgentOps / 可观测 / 评估：AgentOps.ai；Maxim；Galileo；Arize Phoenix；Weights & Biases Weave；Langfuse；LangSmith；OpenTelemetry GenAI 语义约定（域9）。
- 〔知识〕成本/可靠性治理：LLM FinOps（按 tenant/feature/route 归因）；网关 circuit breaker / 预算配额（域12）；Temporal/DBOS durable execution（域2）；SRE/SLA 通用实践。
- 〔知识〕治理/合规：NIST AI RMF（AI 100-1）+ Generative AI Profile（600-1）；EU AI Act；ISO/IEC 42001:2023（AI 管理体系）；OPA/Rego（policy-as-code）；模型卡 / 数据血缘 / 负责任 AI。
- 〔知识〕人机协同运营：LangChain Agent Inbox；LangGraph human-in-the-loop interrupt（域2/10）；ambient agent（域7）。
- 〔知识〕互操作/目录：A2A（Linux Foundation/AAIF，Agent Card + JSON-RPC，域2）；MCP Registry（域4）；AGNTCY / Internet of Agents（Cisco Outshift，域2）。
- 交叉引用：编排状态/durable/A2A 机制（域2）；工具/MCP 与最小权限接口角度（域4）；评估/judge/轨迹/可观测基建（域9）；运行时注入防御/护栏/HITL 机制（域10）；prompt 版本化（域11）；模型路由/缓存/成本技术（域12）。
