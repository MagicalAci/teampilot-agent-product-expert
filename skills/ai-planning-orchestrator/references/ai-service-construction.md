# AI 服务构建最佳实践（AI Service Construction）

> 一句话：**一个好的 AI 服务 = 把 LLM 当"只在真正需要概率推理的地方"才出现的普通软件**——其余全是确定性工程：类型化工具、结构化输出校验、有界重试、预算、降级、全链路可观测。
>
> 何时读：执行 `/AI脚本`、`/AI策划` 落地脚本/服务时；设计 route/handler、调用编排、错误处理时。
> 配合：`references/hellobike-platform-api.md`（平台 API）+ `references/platform-capabilities.md`（能力实测）+ `examples/api-cookbook/`（能力积木）+ `policies/llm-eval-methodology.md`（评测）。

---

## 心法：12-Factor Agents

可靠的 AI 服务不是"套一个大框架"，而是把一组**模块化工程概念**嵌进你现有服务。核心几条（蒸馏自 [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)）：

1. **自然语言 → 结构化工具调用**：每次用户意图翻成显式、类型化的工具调用（JSON）。
2. **拥有你的提示词**：提示词是一等代码，能随模型演进调 token 顺序与 system/user 角色。
3. **拥有你的上下文窗口**：不要把整段历史/库表倒进 prompt；主动裁剪——摘要长历史、压缩错误、只放当下相关。上下文是**有限缓存**，做好能省 30–60% token 且提准确率。
4. **工具就是结构化输出**：工具调用本质是模型生成一段符合 schema 的文本——**严格 schema 校验后再执行**，在出事前拦住非法 JSON / 乱来的 SQL。
5. **执行状态与业务状态同存**：状态外置（DB/Redis），重启幂等。
6. **launch / pause / resume**：暴露可安全重放的入口，调度器与开发都能回放某次 run。
7. **高风险步骤路由给人**：把"人审"做成一等的工具调用（HITL）。
8. **控制流留在普通代码里**：用显式编排（OODA/状态机）跑收敛循环，而不是层层嵌 prompt。
9. **把错误压进下一次 prompt**：让模型读到错误摘要从而自愈（但要设最大重试，防死循环）。
10. **小而专的 agent**：宁可多个聚焦 agent，不要一个无所不包的巨型 agent。

> 即使模型越来越强，这些工程技术仍让 LLM 软件更可靠、可扩展、易维护。

---

## 典型生产架构（五层）

```
请求 → ① 编排 Orchestrator（控制流/状态/重试/截止）
        → ② 工具执行 Tool Adapters（鉴权/校验/超时/幂等/结构化错误）
        → ③ 状态管理 State（外置存储/检查点/可恢复）
        → ④ 模型推理 Inference（结构化输出/缓存/路由/fallback）
        → ⑤ 策略与护栏 Policy & Guardrails（输入校验/红线/PII/最小权限）
      ↘ 全链路可观测（run 级事件/预算/追踪）
```

### ① 编排：控制流在你手里

显式 orchestrator 管状态、重试、截止时间，跑收敛循环。设**预算与步数上限**（如单 run ≤25–30 步、token/成本上限）；任一预算超限 → 停 run、记录原因，而不是无限烧钱/死循环。把 LLM 输出当**提议**，提交前必经确定性校验（stochastic-deterministic boundary）。

### ② 工具：类型化 + 守卫

每个工具适配器统一做：请求校验 → 鉴权/策略检查 → schema 归一 → 超时设置 → **幂等键**（写操作必须）→ 结构化错误返回（返回 status，不只是散文）。

- 类型化输入输出：必填字段显式、枚举收窄、自由文本设界。
- 读写分级：写操作比读操作更严格审查。
- 失败时返回结构化 `agent_action` 指令，让上层可自愈。

### ③ 状态：可恢复（durable execution）

- **检查点**：在有意义的边界持久化状态，恢复从"最后一个好点"开始，而不是从第 1 步。
- **幂等**：步骤被跑两次也安全，否则重试会造成重复扣费/重复发送。
- **失败分类**：区分可重试（429/网络抖动）/ 致命（400/非法调用）/ 需升级；durable execution 不是无限重试，是**策略驱动的恢复**。
- 死信队列 + 补偿动作（saga）：多步副作用半途失败要能补偿，失败工作进可检视的队列而非堵住流水线。

### ④ 模型推理：结构化输出 + 重试 + fallback + 缓存

- **结构化输出**：优先 `json_schema`，不支持则 `json_object` + schema 校验兜底（见 `platform-capabilities.md` 实测矩阵；**不要把"文档说支持"当"接口实测支持"**）。
- **有界重试**：指数退避 + 抖动，尊重 `Retry-After`；分清可重试/不可重试；设最大次数。
- **fallback 链**：失败时切模型/切提供商；或降级到更小模型。
- **缓存降本**：长 System Prompt 用上下文缓存（见 cookbook `05`）；语义缓存命中重复问。
- **模型分级路由**：简单分类/抽取用 Mini，内容创作/结构化用 Lite，复杂推理/多模态用 Pro（见 `SKILL.md` Model Selection）。先用 Mini，不够再升。

### ⑤ 护栏：安全与最小权限

输入侧不无条件信任外部内容（防注入，见 `policies/agent-security-scan.md`）；输出侧 PII/红线过滤；工具按最小权限授予；高风险动作要人审。对照 **OWASP LLM Top 10**（注入、不安全输出处理、过度代理等）。

### 优雅降级（不只降模型，降整个工作流）

故障时可逐级降级：agentic 工作流 → 单轮生成；禁用写工具 → 只读模式；裁剪步数；走缓存/检索-only；高风险动作要求人审。

---

## 全链路可观测（run 级，不只最终答案）

发射结构化事件：`run_started` / `model_call_started` / `model_call_completed` / `tool_call_started` / `tool_call_failed` / `retry_scheduled` / `budget_exceeded` / `fallback_activated`。追踪工具选择、预算用量、重试次数、fallback 是否触发。

标准化用 [OpenTelemetry GenAI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/)：`gen_ai.request.model`、`gen_ai.usage.input_tokens/output_tokens`、`gen_ai.response.finish_reasons`；内容默认不采集、按需 opt-in。评估分用 `gen_ai.evaluation.result` 事件挂到对应 span（见 `policies/llm-eval-methodology.md` 第 6 节）。

---

## 与本仓库脚本层对齐

`/AI脚本` 的脚本层至少包含（见 `execution-sop.md` Step 5）：核心生成器/编排器、模型客户端、route/handler 示例、demo、输入输出样例、单测、README/调用文档、脚本包清单。把本文件的可靠性模式落进去：

- 模型客户端封装：结构化输出 + 有界重试 + fallback + 超时。
- handler：输入校验 + 幂等 + 结构化错误 + run 级事件。
- demo/样例：覆盖正常 + 异常/降级路径。

> 服务建好后，立刻进 `/AI评测`：服务质量要用评测集度量，不能靠"跑通了"自我感觉良好（见 `eval-driven-development.md`）。

---

## 自检清单（落地 AI 服务前）

- [ ] 工具调用都是类型化结构化输出，执行前 schema 校验
- [ ] 上下文主动裁剪（摘要/压缩），不裸塞全历史
- [ ] 重试有界（退避+抖动+最大次数），区分可重试/致命
- [ ] 写操作有幂等键；状态外置可恢复（检查点）
- [ ] 有 fallback 链 + 预算/步数上限 + 优雅降级路径
- [ ] 结构化输出按实测矩阵选 `json_schema`/`json_object`，有字段回退口径
- [ ] run 级可观测：关键事件 + token/成本 + 重试/fallback 可见
- [ ] 护栏：防注入、PII、最小权限、高风险人审
