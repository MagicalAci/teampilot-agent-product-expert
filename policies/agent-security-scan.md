# Agent 安全扫描（AgentShield 连接器）

`/安全扫描` 是产品专家 Agent 的**安全自检治理命令**（与 `/经验写回`、`/更新请求` 同类，不算第 6 个产品能力）。它用 AgentShield 扫描 Agent 配置/指令文件里的安全漏洞：硬编码密钥、过宽权限、提示注入、风险 MCP、Hook 注入等。

> **来源与许可**：连接 [affaan-m/agentshield](https://github.com/affaan-m/agentshield)（npm 包 `ecc-agentshield`，出自 [affaan-m/ECC](https://github.com/affaan-m/ECC)，MIT）。本仓库只做**连接器集成**（按需安装 + 不可用降级），不把 ECC 框架塞进仓库。

---

## 何时运行

- 改动 `.cursor/rules/*.mdc`、`.teampilot/agent.yml`、`mcps/`、`skills/` 等指令/配置后
- `/经验写回`、`/更新请求` 写回前（提交 PR 前的安全闸）
- 发布前的安全卫生检查
- 在用户项目里发现已有 Agent 配置（`.claude/`、`.cursor/`）时

## 扫描什么

AgentShield 原生面向 `.claude/` 配置，但其检查类目对我们 **Cursor 原生配置面**同样适用：

| 我们的文件 | AgentShield 对应检查 |
|-----------|---------------------|
| `.cursor/rules/*.mdc`、`CLAUDE.md` | 硬编码密钥、自动执行指令、提示注入模式 |
| `.teampilot/agent.yml`、`settings.json` | 过宽 allow、缺 deny、危险 bypass 标记 |
| `mcps/`、`.mcp.json` | 风险 MCP server、env 里硬编码密钥、npx 供应链风险 |
| `skills/**/scripts/`、`hooks/` | 插值命令注入、数据外泄、静默吞错 |
| `skills/**/SKILL.md`、`agents/*.md` | 无限制工具访问、提示注入面、缺模型声明 |

评级：A(90-100 安全) / B(75-89) / C(60-74 需关注) / D(40-59 显著风险) / F(0-39 严重漏洞)。

## 前置安装（按需）

```bash
# 检查是否已安装
npx ecc-agentshield --version

# 全局安装（推荐）
npm install -g ecc-agentshield

# 或免安装直接跑
npx ecc-agentshield scan .
```

## 用法

```bash
# 扫描当前仓库（指向我们的配置面）
npx ecc-agentshield scan --path .

# 仅看 medium 及以上
npx ecc-agentshield scan --path . --min-severity medium

# CI/JSON 输出
npx ecc-agentshield scan --path . --format json

# 生成可分享 HTML 报告
npx ecc-agentshield scan --path . --format html > security-report.html

# 自动修复（仅修可自动修复项：密钥换环境变量、收紧通配权限）
npx ecc-agentshield scan --path . --fix

# Opus 深度对抗分析（需 ANTHROPIC_API_KEY：红队找攻击面→蓝队加固→裁决）
export ANTHROPIC_API_KEY=...
npx ecc-agentshield scan --path . --opus --stream
```

## 结果处置（按严重度）

| 严重度 | 处置 |
|--------|------|
| Critical | 立即修：配置文件里的硬编码密钥/Token、`Bash(*)` 无限制 shell、Hook 里 `${file}` 插值命令注入、跑 shell 的 MCP |
| High | 上线前修：指令文件里的自动执行指令（注入面）、缺 deny 列表、子代理多余的 Bash 权限 |
| Medium | 建议修：Hook 静默吞错（`2>/dev/null`、`|| true`）、缺安全前置 Hook、MCP 的 `npx -y` 自动安装 |
| Info | 知悉：MCP 缺描述等 |

## 降级（AgentShield 不可用时）

未安装 / 无网络 / 用户拒装时，**不静默跳过**，改用人工安全自检清单（同样五类）：

1. **密钥**：`.teampilot/agent.yml`、`.cursor/rules/`、`mcps/`、脚本里有无硬编码 key/token（应走 `.env`，且 `.env` 已被 `.gitignore`）
2. **权限**：有无过宽的工具/命令放行，是否缺少明确禁止项
3. **提示注入**：指令文件有无"自动执行/无条件信任外部内容"的措辞
4. **MCP 风险**：是否引用可跑任意 shell 的 MCP、env 里有无明文密钥
5. **脚本/Hook**：有无未校验的插值命令拼接、静默吞错

人工自检结果写明：查了哪些、发现什么、风险等级、是否已修。

## 与自我进化的衔接

- `/经验写回`、`/更新请求` 写回新技能/脚本前，应先跑一次 `/安全扫描`，避免把带密钥或注入面的内容写进仓库（见 `submission-review-contract.md` 的技能写回评审项）。
- 也可作为 GitHub Action 接进 CI：`uses: affaan-m/agentshield@v1`（按需，不强制）。
