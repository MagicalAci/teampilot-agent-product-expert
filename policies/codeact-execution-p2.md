# CodeAct 与沙箱执行（P2 · 脚本优先，沙箱触发式）

这是 `tool-use-protocol.md` 的执行面延伸。核心范式：**能用一段脚本完成的多步/批量工具操作，就写脚本（CodeAct），而不是逐个 JSON 工具调用**——省轮次/token、可并行、可自调试。CodeAct-lite（脚本优先）**现在就能用**；真正的隔离**沙箱**是触发式重基建。

> 来源 `findings/04-tools-mcp.md` + `findings/01-agent-reasoning.md`（CodeAct）。Microsoft Agent Framework 报告 CodeAct 相比 JSON 工具调用 ~50% 延迟、>60% token 下降。

---

## 1. CodeAct-lite（脚本优先，现在可用、零新基建）

判定：一个任务里**对同类工具/数据做多步或批量操作**（多平台采集汇总、SQL+图表流水线、批量规范化）时——
- **写一段脚本**（Python/shell）一次完成 + 自调试，而不是逐个 JSON 调工具；
- 本仓库已有大量 `scripts/`（research `run_pipeline.py`、aibi、eval 等）就是这个模式，CodeAct-lite 是把它显式为纪律；
- **无脚本环境时降级**为现有逐步工具调用（不静默失败）。

## 2. 何时升级到隔离沙箱（触发式重基建）

| 触发条件 | 处理 |
|---|---|
| 要执行**不可信/模型生成的代码**（如让模型写代码处理脏数据） | 上隔离沙箱 |
| 多租户 / 对外 / 需强隔离 | 上隔离沙箱（接 `productization-readiness-p2.md`） |
| 仅本机可信脚本、单用户 | **不需要**——受管 venv / 子进程即可 |

## 3. 沙箱选型（触发后）

| 方案 | 隔离强度 | 何时用 |
|---|---|---|
| 受管 venv / 子进程 + 超时/资源限 | 弱（同机） | 本机可信脚本（当前默认够用） |
| **gVisor** 容器 | 中（syscall 拦截） | 中等不可信、容器化 |
| **E2B / Firecracker microVM** | 强（microVM） | 跑不可信/模型生成代码、规模化 |

- 配 **Anthropic「code execution with MCP」模式**：把 MCP server 暴露成文件系统里的代码 API，Agent 写代码按需加载工具、在沙箱内处理中间数据（单场景 token -98.7%）。
- 默认**断网 + 最小权限 + 超时**；与 `agent-safety-protocol.md` 的内外隔权、高风险 HITL 一致。

## 4. 与本仓库接线
- `tool-use-protocol.md` 的"P2"小节指向本文件；CodeAct-lite 写进其调用机制条款。
- 自建工具/MCP 的脚本化沉淀走 `mcp-tool-authoring.md`；轨迹/token 评测走 `agent-trajectory-eval.md`。

## 何时查阅
- 多步/批量工具操作 → §1 脚本优先（现在就做）
- 要跑不可信/生成代码 → §2–§3 沙箱选型（触发式）
