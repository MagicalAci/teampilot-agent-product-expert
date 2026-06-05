# 产品化就绪（P2 · 面向团队/组织产品化时）

这是 `agentops-lifecycle.md` 与 `findings/08-enterprise-agentops.md` 的延伸。结论先行：产品专家 Agent 当前是 **Cursor 原生、近似单用户**，多租户/企业 SSO/对外 SLA/合规等**企业基建当前不做**。本文件是一份**产品化就绪清单 + 参考架构选型**——当且仅当要把它**面向团队/组织产品化**时，按此评估，且**优先复用大厂托管平台而非自建**。

> 来源 `findings/08-enterprise-agentops.md`。运行时安全见 `agent-safety-protocol.md`；成本/SLA 治理面见 `cost-discipline-methodology.md`；durable 见 `durable-execution-p2.md`。

---

## 0. 触发判定（默认全否）

仅当"**产品专家 Agent 要服务多个用户 / 跨团队 / 对外**"时启用本文件；单用户内部使用**一律不做**。

## 1. 产品化就绪清单（触发后逐项评估）

| 维度 | 要补什么 | 选型/做法 |
|---|---|---|
| **多租户隔离** | 数据/会话/记忆按 tenant 隔离，杜绝串户 | claude-mem `projectId` 命名空间（轻）→ 平台多租户（重） |
| **Agent 身份与授权** | 非人类身份(NHI) + OAuth2.1 scoped token + on-behalf-of 委托 + 最小权限 | IdP（Okta/Auth0/Entra Agent ID）；MCP 远程 OAuth2.1（接 `agent-security-scan.md`） |
| **企业 SSO** | 接入组织 SSO | OIDC/SAML |
| **对外 SLA / 可靠性** | 可用性/延迟/成功率目标 + durable | `durable-execution-p2.md` + 监控 |
| **成本治理（强制）** | 按 tenant/feature 预算配额 + 熔断 | `cost-discipline-methodology.md` 预算护栏 → 网关 enforcement |
| **合规** | EU AI Act（风险分级义务）/ NIST AI RMF / ISO/IEC 42001 / 数据驻留 | policy-as-code（OPA）+ 审计日志 + 模型卡 |
| **审计追溯** | 谁/何时/对什么/凭何批准 | `agent-safety-protocol.md` 不可逆动作留痕 → 平台审计 |
| **运营** | agent inbox / 升级转人工 / human-on-the-loop | LangChain Agent Inbox 等 |

## 2. 参考架构选型（触发后，优先托管平台）

要托管运行时时，**优先用大厂托管平台**（会话/状态/身份/记忆/可观测一体），而非自拼：
- AWS Bedrock AgentCore · Google Vertex AI Agent Engine · Microsoft Azure AI Foundry Agent Service · Salesforce Agentforce · LangGraph Platform · IBM watsonx Orchestrate。
- 选型依据：现有云栈 + 合规要求 + 是否需低代码（Copilot Studio/Agentforce）。

## 3. 与本仓库接线
- `agentops-lifecycle.md`（build→eval→ship→govern）是单仓库版生命周期；产品化时其 govern 阶段扩展为本文件的合规/多租户/SLA 治理。
- 明确：**当前一律不做，不引入企业基建依赖**；本文件仅作触发式就绪参考。

## 何时查阅
- 仅当要把产品专家 Agent 面向团队/组织产品化时 → §0 判触发 → §1 清单 + §2 选型
