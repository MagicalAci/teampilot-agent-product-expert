# 产品专家 Agent

这是 TeamPilot 的 Cursor 原生 Agent 示例仓库。仓库本身就是 Agent 的事实源，包含：

- Agent manifest：`.teampilot/agent.yml`
- Cursor 命令规则：`.cursor/rules/product-expert-commands.mdc`
- 能力 Skill：`skills/`
- 模板：`templates/`
- 提交与评审约束：`policies/`

## 当前版本

- Slug：`product-expert`
- Version：`0.1.0`
- Repo：`MagicalAci/teampilot-agent-product-expert`

## 主要命令

- `/调研`
- `/策划`
- `/AI策划`
- `/查看能力`
- `/检查Agent更新`
- `/更新请求`
- `/经验写回`

## 目录说明

- `skills/research/SKILL.md`：调研能力
- `skills/planning/SKILL.md`：策划能力
- `skills/ai-planning/SKILL.md`：AI 策划能力
- `templates/`：输入模板与输出骨架
- `policies/`：提交与评审约束
- `mcps/README.md`：当前依赖的 MCP 说明

## 演进方式

使用 TeamPilot 的 `/更新请求` 或 `/经验写回`，系统会自动向该仓库创建 PR，由维护者审核合并。
