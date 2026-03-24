# 产品专家 Agent

这是 TeamPilot 的 Cursor 原生产品专家 Agent 仓库，已经从轻量示例升级为可直接使用的完整版本。仓库本身就是 Agent 的事实源，包含：

- Agent manifest：`.teampilot/agent.yml`
- Cursor 命令规则：`.cursor/rules/product-expert-commands.mdc`
- 三个完整能力包：`skills/`
- 提交与评审约束：`policies/`
- MCP 依赖说明：`mcps/README.md`
- 仓库级回归测试：`tests/`

## 当前版本

- Slug：`product-expert`
- Version：`0.3.0`
- Repo：`MagicalAci/teampilot-agent-product-expert`

## 四个能力点

### 1. 单产品分析

- 主 skill：`skills/single-product-competitor-analysis/SKILL.md`
- 主命令：`/竞品分析`
- 兼容别名：`/单产品分析`
- 子命令：`/爬取`、`/竞品引导`
- 适用场景：单个产品竞品研究、平台资料采集、真实体验引导、逐章写作与事实核查

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

## 快速开始

1. 在 Cursor 或 TeamPilot 中安装这个 Agent。
2. 使用 `/查看能力` 查看四个能力点及其子命令。
3. 按任务类型直接进入对应命令：
   - 单产品分析：`/单产品分析 豆包爱学`
   - 产品策划：`/产品策划 家长端留存提升方案`
   - AI策划：`/AI策划 PRD 生成 Agent`
   - Demo开发：`/Demo开发 AI 陪练产品首页 demo，目标平台：H5`

## 目录说明

- `skills/single-product-competitor-analysis/`：单产品分析完整 skill 包，含 assets、examples、references、scripts、tests、schemas、fixtures
- `skills/education-prd-orchestrator/`：产品策划完整 skill 包，含 assets、examples、references、scripts、tests、fixtures
- `skills/ai-planning-orchestrator/`：AI策划完整 skill 包，含 assets、examples、references、scripts、tests
- `skills/product-demo-orchestrator/`：Demo开发完整 skill 包，含 assets、references、scripts、tests
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
python -m unittest discover -s skills/single-product-competitor-analysis/tests -p "test_*.py"
python -m unittest discover -s skills/education-prd-orchestrator/tests -p "test_*.py"
python -m unittest discover -s skills/ai-planning-orchestrator/tests -p "test_*.py"
python -m unittest discover -s skills/product-demo-orchestrator/tests -p "test_*.py"
```

## 演进方式

使用 TeamPilot 的 `/更新请求` 或 `/经验写回`，系统会自动向该仓库创建 PR，由维护者审核合并。
