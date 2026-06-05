# 自建工具 / MCP 创作协议（MCP & Tool Authoring）

这是产品专家 Agent 从"**只会用工具（MCP 消费方）**"走向"**会造工具**"的判据与流程。当前缺"何时自建 MCP/工具 vs 消费 vs 写 skill"的判据，也无自建 MCP 的 build→eval→iterate 流程。本协议补上。

> 细节编目见 `findings/04-tools-mcp.md`。工具使用规范见 `tool-use-protocol.md`；技能编写/测试方法论见 `agent-team-methodology.md` 第二、三部分（"造工具"与"写技能"共用 build→eval→iterate 内核）。

---

## 1. 造 / 买 / 降级判据

| 情形 | 选择 |
|---|---|
| 高频复用、且**无现成 MCP/连接器** | **造**（自建 MCP/工具，沉淀进仓库） |
| 已有上游 MCP/skill | **买/接**（连接器化：按需 `npx skills i` 安装 + 不可用降级，遵循现有连接器纪律） |
| 一次性、隔离、无复用 | **主代理直办**，不造工具（避免过度工程） |

## 2. 自建 MCP/工具流程（build → eval → iterate）

1. **原型**：本地 MCP server / 脚本跑通核心能力。
2. **按 Anthropic 工具原则定义**：name / 命名空间 / description（即提示词）/ input schema / 高信噪返回 / 错误返回（见 `tool-use-protocol.md`）。
3. **eval**：真实多步任务上测**调用准确率 / token / 错误率**（BFCL 式视角）；接 `agent-trajectory-eval.md` 的工具调用 grader。
4. **契约测试**：存在性 + 关键能力 + 失败降级（与仓库测试纪律一致）。
5. **连接器化沉淀**：包装成"按需安装 + 不可用降级 + `summary.md` 透明记录"的连接器；过 `/安全扫描`（第三方信任分级，`agent-security-scan.md`）。

## 3. 接入自我进化
反复奏效的工具操作先记为"本能"（`agent-team-methodology.md` 第四部分），攒够证据经 `/经验写回` 升级为自建工具/连接器，走 `agentops-lifecycle.md` 的 build→eval→ship→govern 门禁。

## 4. 与本仓库接线
- `submission-review-contract.md` 写回评审项："若新增工具/MCP，是否走了 authoring 流程 + 契约测试 + 安全扫描"。
- 北极星：Anthropic"让 Agent 读 eval transcript 自动改工具"（需 eval 基建，P2）。

## 何时查阅
- 纠结"该不该自建工具/MCP" → §1
- 决定自建后怎么做 → §2–§3
