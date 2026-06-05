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
- Version：`0.25.0`
- Repo：`MagicalAci/teampilot-agent-product-expert`

## 架构特性

- **任务领航规则**（`task-navigator.mdc`，`alwaysApply: true`）：Agent 在任务启动后主动阅读 brief，分析目标，匹配能力组合，输出分阶段工作规划，征求确认后按计划执行。
- **命令路由规则**（`product-expert-commands.mdc`）：用户发出 `/指令` 时精确路由到对应 Skill。

## 五个能力点

### 1. 调研分析（Research Toolkit）

- 主 skill：`skills/research-toolkit/SKILL.md`
- 主命令：`/深度调研 [产品/方向]`
- 子命令：`/海外调研`、`/爬取`、`/体验引导`、`/调研安装`、`/调研体检`、`/调研授权`、`/调研打包`
- 适用场景：单产品深度分析、方向/赛道调研、市场全景对比、用户研究、海外/出海调研、自定义调研
- 工具链：DeerFlow 深度研究、MediaCrawler/XHS-Downloader 国内社媒采集、last30days 海外社媒采集（Reddit/X/YouTube/HN/TikTok/Polymarket）、MCP 并行采集
- 双通道：国内通道（小红书/微博/B站/知乎）+ 海外通道（last30days 引擎，按需 `npx skills add mvanhorn/last30days-skill -g` 安装，不可用时自动降级）

### 2. 产品策划

- 主 skill：`skills/education-prd-orchestrator/SKILL.md`
- 主命令：`/产品策划`
- 子命令：`/产品策划校验`
- 适用场景：PRD 撰写、章节编排、总览图与功能图补齐、已有产物校验

### 3. AI策划

- 主 skill：`skills/ai-planning-orchestrator/SKILL.md`
- 主命令：`/AI策划`
- 子命令：`/AIPRD`、`/AI脚本`、`/AI测试`、`/评测集`、`/AI评测`、`/AI调优`
- 适用场景：策略先行提示词、AI PRD、Prompt 合同、AI 服务构建（12-factor）、脚本开发、测试报告、最小交接包，以及**评测驱动开发闭环**（评测集汇总、评测体系、自动化评测 pass@k/回归/A-B、评测报告与 GEPA 式调优报告）

### 4. Demo开发

- 主 skill：`skills/product-demo-orchestrator/SKILL.md`
- 主命令：`/Demo开发`
- 子命令：`/Demo设计系统`、`/Demo脚手架`、`/Demo打磨`、`/Demo校验`、`/Demo上线`
- 适用场景：Web、H5、SwiftUI demo，产品演示页，评审演示骨架，产品 walkthrough 与开发交接，一键部署上线分享

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

## 一键安装（复制代码块内容粘贴到 Cursor 聊天框即可）

> 无需 GitHub 账号或仓库权限，任何团队成员均可直接安装。

````text
请在 Cursor 中帮我安装并启用 产品专家 Agent。
请直接执行安装，不要只解释命令。

## 第一步：执行安装

直接运行下面这条命令：

curl -fsSL https://teampilot.magicalaci.cn/api/agents/product-expert/install?format=script&version=0.25.0 | bash

如果上面的命令执行失败或超时，改用下面的备用方式：

AGENT_DIR="$HOME/TeamPilot/agents/product-expert/0.25.0"
mkdir -p "$AGENT_DIR"
git clone https://github.com/MagicalAci/teampilot-agent-product-expert.git "$AGENT_DIR"

无论哪种方式，安装失败都不要卡住，直接把报错信息告诉我。

## 第二步：安装完成后读取这些文件

- ~/TeamPilot/agents/product-expert/0.25.0/QUICKSTART.md
- ~/TeamPilot/agents/product-expert/0.25.0/.teampilot/agent.yml
- 不要依赖仓库 README.md 作为当前版本能力和命令的最终事实源；README 只能补充背景。

如果 QUICKSTART.md 不存在，则读取以下文件代替：
- ~/TeamPilot/agents/product-expert/0.25.0/.cursor/rules/product-expert-commands.mdc

## 当前版本信息

- 名称：产品专家 Agent（product-expert）
- 版本：0.21.0
- 仓库：MagicalAci/teampilot-agent-product-expert
- 简介：内置调研分析（单产品/方向/全景/用户研究）、产品策划、AI策划、Demo开发、SQL数据查询分析五项完整能力的 Cursor 原生 Agent。
- 本地目录：~/TeamPilot/agents/product-expert/0.25.0

## 核心能力入口参考

- /深度调研：统一调研分析能力 — 支持单产品深度分析、方向调研、市场全景、用户研究，自带 DeerFlow 深度研究、MediaCrawler 社媒采集、质量门禁、逐章写作与三轮事实核查。
- /产品策划：证据驱动的产品策划与 PRD 交付能力，覆盖任务卡冻结、定义闸门、章节编排、配图与校验。
- /AI策划：面向 AI 方案落地的产品能力，覆盖 AI PRD、脚本开发、测试报告与最小交接包。
- /Demo开发：面向 Web、H5 与 SwiftUI 的产品 demo 开发能力，覆盖 brief、设计系统、脚手架、打磨、校验、交接与一键部署上线。
- /SQL：星火工坊 AIBI 数据查询分析能力，自然语言提问自动生成 SQL 查询 DBOPS 数据库，输出分析报告。支持快速版（纯聊天输出）和深度版（HTML看板+CSV）。覆盖 sparklab_starcard、sparklab_picbook、sg_sparklab_poptoy 三个线上库。

## 第三步：最后用中文回复我

- 是否安装成功
- 本地安装到了哪个目录
- 这个 Agent 当前版本能做什么
- 当前版本有哪些核心能力入口
- 推荐我先从哪个命令开始，以及原因
````

## 安装后使用

安装完成后，在任意 Cursor 工作区中：

1. 使用 `/查看能力` 查看五个能力点及其子命令
2. 按任务类型直接进入对应命令：
   - 调研分析：`/深度调研 豆包爱学`
   - 海外调研：`/海外调研 Perplexity`
   - 产品策划：`/产品策划 家长端留存提升方案`
   - AI策划：`/AI策划 PRD 生成 Agent`
   - AI评测：`/AI评测 课堂讲题 Agent`（先 `/评测集` 建集，评测后 `/AI调优`）
   - Demo开发：`/Demo开发 AI 陪练产品首页 demo，目标平台：H5`
   - SQL 快速查询：`/SQL 帮我看下星卡最近的用户和订单情况`
   - SQL 深度分析：`/SQL深度 出一份绘本产品的完整运营分析报告`

## 目录说明

- `skills/research-toolkit/`：调研分析完整 skill 包，含国内/海外双采集通道（海外通道见 `protocols/overseas-research.md` + `references/last30days-connector.md`），含 assets、examples、references、scripts、tests、schemas、fixtures
- `skills/education-prd-orchestrator/`：产品策划完整 skill 包，含 assets、examples、references、scripts、tests、fixtures
- `skills/ai-planning-orchestrator/`：AI策划完整 skill 包，含 assets、examples、references、scripts、tests；含**评测驱动开发子系统**（策略先行提示词 + AI服务构建 + 评测集/评测体系/自动化评测台 `run_eval.py`/调优报告）
- `skills/product-demo-orchestrator/`：Demo开发完整 skill 包，含 assets、references、scripts、tests
- `skills/aibi-query/`：SQL 数据查询分析 skill 包，含 references（数据库全景/查询案例/查询规范）、templates（HTML 看板）、scripts（Token 管理）
- `policies/submission-review-contract.md`：统一提交与评审契约
- `policies/agent-team-methodology.md`：团队架构与技能编写方法论（蒸馏适配自 [revfactory/harness](https://github.com/revfactory/harness)，Apache-2.0；并借鉴 [affaan-m/ECC](https://github.com/affaan-m/ECC) 的持续学习/Token优化/并行/验证循环），支撑多子代理编排与 `/经验写回`·`/更新请求` 自我进化
- `policies/agent-security-scan.md`：`/安全扫描` 安全自检连接器（AgentShield / [affaan-m/ECC](https://github.com/affaan-m/ECC)，MIT），按需安装、不可用降级，写回前检查配置/指令的安全漏洞
- `scripts/security_self_check.py`：仓库级安全自检门禁（硬编码密钥 + `.env` 卫生），已接入 CI（`security-self-check.yml`）
- `policies/prompt-engineering-techniques.md`：提示词工程方法论（22 技术蒸馏自 [NirDiamant/Prompt_Engineering](https://github.com/NirDiamant/Prompt_Engineering)），强化 AI策划 与技能编写
- `policies/llm-eval-methodology.md`：评测驱动开发（EDD）方法论（评测集/评测体系/自动化评测/LLM-as-judge/调优，蒸馏自 [DeepEval](https://github.com/confident-ai/deepeval)·[promptfoo](https://github.com/promptfoo/promptfoo)·[Ragas](https://github.com/explodinggradients/ragas)·[Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai)·[GEPA](https://github.com/gepa-ai/gepa)/[DSPy](https://github.com/stanfordnlp/dspy)·[OTel GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)），强化 AI策划 评测/调优
- `policies/image-prompt-connector.md`：`/图片提示词` 连接器（[nano-banana-pro](https://github.com/YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill)，MIT），从 10000+ Gemini 图片提示词检索/改写出图提示词
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
