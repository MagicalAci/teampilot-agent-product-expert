---
name: ai-planning-orchestrator
display_name: "AI策划全流程编排"
description: "面向 AI 方案落地的通用编排 Skill，支持 AI PRD、脚本开发、测试报告与开发交接产物的一体化交付。"
category: product
version: "1.0.0"
review_criteria:
  - label: "交付链路完整性：/AI策划 默认至少覆盖 AI PRD、AI脚本、AI测试报告三项核心产物"
  - label: "模式匹配准确性：/AI策划、/AIPRD、/AI脚本、/AI测试 的产物范围与用户要求一致"
  - label: "任务卡冻结：开始前明确交付模式、交付对象、模板约束、平台硬约束及已有上游资产"
  - label: "PRD结构完整性：AI PRD 默认包含输入数据结构定义、AI策略、提示词模块、AI脚本四段主链路"
  - label: "Prompt合同完整性：Prompt 明确人设、任务、规则、输出规范、严格禁止、思考链，并冻结字段与回退口径"
  - label: "脚本交付完备性：脚本至少包含生成器或编排器、模型客户端、API handler 示例、demo、样例、README 与脚本包清单"
  - label: "开发前置条件正确：仅在已有 AI PRD 或已冻结字段合同和 Prompt 合同后开发脚本"
  - label: "测试报告有效性：测试报告包含测试范围、运行环境、用例与结果、关键结论、剩余风险"
  - label: "真实调用验证：至少覆盖必要的 CLI 或脚本调用、API handler 或 route 调用、结构化输出兼容性验证"
  - label: "口径一致性：文档、代码、样例、压缩包中的字段与 Prompt 口径一致，且包含字段回退方案"
---

# AI策划主 Skill

## Overview

这是一个面向同学快速开展 AI 策划的通用 Skill，用来把一项 AI 能力从方案到落地拆成 4 条稳定入口：

- AI PRD
- AI脚本
- AI测试报告
- 如有需要，再补开发可接入的脚本包

它不是某个业务的专用写作器，而是一套"先策划、再写 PRD、再开发脚本、再测试验证"的固定方法。

## 四条指令

### `/AI策划 [主题]`

用于全流程开始，默认串起：

1. 冻结任务卡
2. 撰写 AI PRD
3. 开发 AI 脚本
4. 测试 AI 脚本并输出测试报告
5. 如需交接开发，再补最小脚本包

### `/AIPRD [主题]`

用于单独撰写或刷新 AI PRD。

### `/AI脚本 [主题]`

用于单独开发 AI 脚本、接口示例、输入输出样例，以及给开发/联调同学看的 README 与调用文档。

它可以包含最小可运行自测 / 单测，但不默认产出正式 AI 测试报告；正式测试报告由 `/AI测试` 负责。

### `/AI测试 [对象]`

用于测试 AI 脚本，并输出正式测试报告。

## Mode Deliverables

| 命令 | 默认产物 |
|---|---|
| `/AI策划` | AI PRD + AI 脚本 + AI 测试报告 + 可选脚本包 |
| `/AIPRD` | AI PRD |
| `/AI脚本` | AI 脚本 + 样例 + README / 调用文档 |
| `/AI测试` | AI 测试报告 |

如果用户只要其中一段，就运行对应模式，不强制全量重做。

## Workflow

### 1. 冻结任务卡

先确认：

- 这轮要做全流程，还是只做 PRD / 脚本 / 测试
- 交付对象是谁：产品、AI、开发、联调同学，还是评审方
- 是否存在官方模板、外部规范、或固定章节顺序
- 是否有平台配置、输出字段、模型能力的硬约束
- 当前是否已经有上游资产：PRD、脚本、测试日志、Prompt 文档

如果存在多种合理理解，先回到用户，不要边写边猜。

### 2. 读取模板与基线资产

优先顺序：

- 官方模板或外部文档
- 当前 AI PRD
- 当前脚本或生成器
- 当前 AI测试报告 / 测试日志
- 当前脚本包 README
- Prompt 文档

如果用户给的是 Feishu / Wiki 模板，优先用 MCP 读取后再开始写文档。

### 3. `/AIPRD` 工作流

默认 AI PRD 的主链路是：

1. `输入数据结构定义`
2. `AI策略`
3. `提示词模块`
4. `AI脚本`

除非模板明确不同，否则不要跳章，不要改顺序，不要把脚本和测试写到策略前面。

在写策略和 Prompt 之前，先冻结：

- 输入字段
- 输出字段
- 字段层级
- 必填 / 选填
- 回退口径
- 兼容旧协议方式

Prompt 本体统一检查：

- `人设`
- `任务`
- `规则`
- `输出规范`
- `严格禁止`
- `思考链`

### 4. `/AI脚本` 工作流

开始开发前，必须先有以下两者之一：

- 已存在的 AI PRD
- 已冻结的字段合同 + Prompt 合同

脚本层至少包含：

- 核心生成器 / 编排器
- 模型客户端
- route / API handler 示例
- demo 脚本
- 输入输出样例
- README / 调用文档
- 脚本包清单

不要在字段和 Prompt 还漂移时直接开写脚本。

### 5. `/AI测试` 工作流

按项目实际情况至少验证：

1. 单元测试
2. CLI 或脚本真实调用
3. API handler / route 真实调用
4. 结构化输出兼容性验证

测试报告不能只贴命令或日志路径，必须总结：

- 测试范围
- 运行环境
- 用例与结果
- 关键结论
- 剩余风险

### 6. `/AI策划` 全流程串联

`/AI策划` 默认顺序是：

1. 先跑 `/AIPRD`
2. 再跑 `/AI脚本`
3. 最后跑 `/AI测试`

如果用户还需要交接开发，再按 `references/package-scope.md` 和 `references/developer-handoff.md` 补最小脚本包与调用说明。

## User Checkpoints

这些场景必须停下来问用户：

- 官方模板无法读取
- 输出字段和历史实现存在分叉
- 平台 Key / 鉴权方式是否允许写入交付包不明确
- 真实调用环境不可用
- 用户要同时改模板、代码、包结构和平台配置
- 用户只说"做 AI 策划"，但没有说明这轮是全流程、PRD、脚本还是测试

## Non-Negotiable Rules

- 不要把"模型文档说支持"当成"当前接口实测支持"
- 不要把"日志存在"当成"测试报告已完成"
- 不要把"Prompt 写了"当成"映射关系已经清楚"
- 不要遗漏字段回退口径
- 不要让文档、代码、样例、压缩包四套口径并行漂移
- 不要在没有冻结字段和 Prompt 合同的情况下直接写脚本

## Scripts

- `scripts/init_ai_planning_delivery.py`
  - 从模板初始化 AI PRD、AI测试报告、开发 README、脚本包清单。
- `scripts/validate_ai_planning_assets.py`
  - 校验 PRD、测试报告、README 是否有关键章节，文件是否齐全。
- `scripts/package_ai_script_bundle.py`
  - 把源码、样例、文档打成开发可接入的 zip。
- `scripts/export_svg_to_png.js`
  - 把 SVG 流程图导出成 PNG，方便插入 PRD 或 README。

## Model Selection

执行 `/AI脚本` 或 `/AI策划` 时，根据任务复杂度选择模型：

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 简单文案 / 分类 / 提取 / 高并发 | `Doubao-Seed-2.0-Mini-0215` | 成本最低，响应最快，效果≈1.6 |
| 内容创作 / 数据分析 / 结构化输出 | `Doubao-Seed-2.0-Lite-0215` | 均衡型，超越 1.8，成本优化 |
| 复杂推理 / Agent / 多模态 / 长链路 | `Doubao-Seed-2.0-Pro-0215` | 旗舰全能，复杂任务首选 |

默认先用 Mini，效果不够再升级。详细 API 文档见 `references/hellobike-platform-api.md`。

## Resources

- 模版骨架：`assets/ai-prd-template.md`
- 测试报告模板：`assets/test-record-template.md`
- 开发 README 模板：`assets/developer-readme-template.md`
- 脚本包清单模板：`assets/script-bundle-manifest-template.md`
- **平台 API 文档**：`references/hellobike-platform-api.md`
- 执行 SOP：`references/execution-sop.md`
- 评审清单：`references/review-checklist.md`
- 脚本交付范围：`references/package-scope.md`
- 开发交接说明：`references/developer-handoff.md`
- 示例指令：`examples/example-invoke.md`
- 脚本用法：`examples/example-validation-command.md`
- Scripts 索引：`scripts/README.md`