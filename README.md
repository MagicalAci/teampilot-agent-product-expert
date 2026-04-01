# 产品专家 Agent

这是 TeamPilot 的 Cursor 原生产品专家 Agent 仓库，已经从轻量示例升级为可直接使用的完整版本。仓库本身就是 Agent 的事实源，包含：

- Agent manifest：`.teampilot/agent.yml`
- Cursor 命令规则：`.cursor/rules/product-expert-commands.mdc`
- 五个完整能力包：`skills/`
- 提交与评审约束：`policies/`
- MCP 依赖说明：`mcps/README.md`
- 仓库级回归测试：`tests/`

## 当前版本

- Slug：`product-expert`
- Version：`0.9.0`
- Repo：`MagicalAci/teampilot-agent-product-expert`

## 架构特性

- **任务领航规则**（`task-navigator.mdc`，`alwaysApply: true`）：Agent 在任务启动后主动阅读 brief，分析目标，匹配能力组合，输出分阶段工作规划，征求确认后按计划执行。
- **命令路由规则**（`product-expert-commands.mdc`）：用户发出 `/指令` 时精确路由到对应 Skill。

## 五个能力点

### 1. 调研分析（Research Toolkit）

- 主 skill：`skills/research-toolkit/SKILL.md`
- 主命令：`/深度调研 [产品/方向]`
- 子命令：`/爬取`、`/体验引导`、`/调研安装`、`/调研体检`、`/调研授权`、`/调研打包`
- 适用场景：单产品深度分析、方向/赛道调研、市场全景对比、用户研究、自定义调研
- 工具链：DeerFlow 深度研究、MediaCrawler/XHS-Downloader 社媒采集、MCP 并行采集

### 2. 产品策划

- 主 skill：`skills/education-prd-orchestrator/SKILL.md`
- 主命令：`/产品策划`
- 子命令：`/产品策划校验`
- 适用场景：PRD 撰写、章节编排、总览图与功能图补齐、已有产物校验

### 3. AI策划

- 主 skill：`skills/ai-planning-orchestrator/SKILL.md`
- 主命令：`/AI策划`
- 子命令：`/AIPRD`、`/AI脚本`、`/AI测试`
- 适用场景：AI PRD、Prompt 合同、脚本开发、测试报告、最小交接包

### 4. Demo开发

- 主 skill：`skills/product-demo-orchestrator/SKILL.md`
- 主命令：`/Demo开发`
- 子命令：`/Demo设计系统`、`/Demo脚手架`、`/Demo打磨`、`/Demo校验`
- 适用场景：Web、H5、SwiftUI demo，产品演示页，评审演示骨架，产品 walkthrough 与开发交接

### 5. SQL 数据查询分析（AIBI）

- 主 skill：`skills/aibi-query/SKILL.md`
- 命令：
  - `/SQL [提问]` — **快速版**，聊天内直接输出结论 + 数据表 + 图表，不写文件
  - `/SQL深度 [提问]` — **深度版**，生成 HTML 看板 + CSV 数据表 + 完整洞察分析
- 适用场景：查看业务运营数据、分析核心指标、生成数据看板、跑 SQL 查询
- 数据库覆盖：

| 数据库 | 业务 | 线上数据 |
|--------|------|----------|
| sparklab_starcard | 星卡（追星小卡鉴定 + 站姐活动电商） | ✅ |
| sparklab_picbook | 绘本（AI 绘本阅读硬件 + 语音合成） | ✅ |
| sg_sparklab_poptoy | 泡泡玩具（AI 玩偶社区 + 聊天 + IAP） | ✅ |
| 其他 5 个库 | 测肤/社交/作业等 | ❌ 暂未部署 |

- 首次使用：需申请 DBOPS 只读权限 + 提供 SSO Token，Skill 会自动引导
- 附带资料：63 张表完整结构、11 个查询案例、DBOPS API 规范、HTML 看板模板

## 快速开始

1. 在 Cursor 或 TeamPilot 中安装这个 Agent。
2. 使用 `/查看能力` 查看五个能力点及其子命令。
3. 按任务类型直接进入对应命令：
   - 调研分析：`/深度调研 豆包爱学`
   - 产品策划：`/产品策划 家长端留存提升方案`
   - AI策划：`/AI策划 PRD 生成 Agent`
   - Demo开发：`/Demo开发 AI 陪练产品首页 demo，目标平台：H5`
   - SQL 快速查询：`/SQL 帮我看下星卡最近的用户和订单情况`
   - SQL 深度分析：`/SQL深度 出一份绘本产品的完整运营分析报告`

## 目录说明

- `skills/research-toolkit/`：单产品分析完整 skill 包，含 assets、examples、references、scripts、tests、schemas、fixtures
- `skills/education-prd-orchestrator/`：产品策划完整 skill 包，含 assets、examples、references、scripts、tests、fixtures
- `skills/ai-planning-orchestrator/`：AI策划完整 skill 包，含 assets、examples、references、scripts、tests
- `skills/product-demo-orchestrator/`：Demo开发完整 skill 包，含 assets、references、scripts、tests
- `skills/aibi-query/`：SQL 数据查询分析 skill 包，含 references（数据库全景/查询案例/查询规范）、templates（HTML 看板）、scripts（Token 管理）
- `policies/submission-review-contract.md`：统一提交与评审契约
- `mcps/README.md`：单产品分析依赖的 MCP 与降级说明
- `tests/test_product_expert_agent.py`：仓库级能力映射与入口回归

## 本地回归

```bash
python3 -m venv /tmp/product-expert-agent-venv
source /tmp/product-expert-agent-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m unittest tests/test_product_expert_agent.py
python -m unittest discover -s skills/research-toolkit/tests -p "test_*.py"
python -m unittest discover -s skills/education-prd-orchestrator/tests -p "test_*.py"
python -m unittest discover -s skills/ai-planning-orchestrator/tests -p "test_*.py"
python -m unittest discover -s skills/product-demo-orchestrator/tests -p "test_*.py"
```

## 演进方式

使用 TeamPilot 的 `/更新请求` 或 `/经验写回`，系统会自动向该仓库创建 PR，由维护者审核合并。
