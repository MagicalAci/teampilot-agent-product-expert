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
  - label: "策略先行：写提示词前先有提示词策略卡（策略→可判定指令映射 + 覆盖率 ≥95%），不直接堆 Prompt"
  - label: "评测集质量：评测集单一 scope、四桶齐备(生产/对抗/边界/回放)、规模达 route 下限、已脱敏去污染"
  - label: "评测体系有效：维度+权重+阈值明确；grader 分层(规则优先,开放式才上 judge)；judge 模型≠被测族且经金标校准"
  - label: "评测与调优闭环：评测报告含失败聚类与回归对比；调优报告基于失败归因(每轮≤3-5处)且有 A/B 证明不退步"
---

# AI策划主 Skill

## Overview

这是一个面向同学快速开展 AI 策划的通用 Skill，把一项 AI 能力从方案到落地、再到可度量可调优，拆成一条**评测驱动开发（EDD）闭环**：

```
①定策略 → ②写提示词 → ③建AI服务 → ④汇总评测集 → ⑤评测体系 → ⑥自动化评测 → ⑦评测报告/调优报告
  (策略卡)  (策略先行)   (12-factor)   (黄金集)      (量规/grader)  (run_eval/pass@k)  (回归+GEPA式调优)
                                                                          └── 回归保护 ──┘
```

稳定入口：

- AI PRD（含**策略先行的提示词**）
- AI脚本（**12-factor 的 AI 服务构建**）
- AI测试报告（软件能跑）
- **AI评测 / AI调优 / 评测集**（质量好不好、可回归、可调优）
- 如有需要，再补开发可接入的脚本包

它不是某个业务的专用写作器，而是一套"先定策略、再写 PRD/提示词、再建服务、再评测、再调优"的固定方法。

> **写 Prompt 合同 / 系统提示前**：先做**提示词策略卡**——把策略翻译成可判定指令再撰写（见 `references/prompt-strategy-first.md`）；提示词技术目录见 `policies/prompt-engineering-techniques.md`（22 个技术 + Prompt 合同最小清单）。
> **建 AI 服务前**：查阅 `references/ai-service-construction.md`（12-factor、结构化输出校验、有界重试/幂等、fallback、预算、降级、run 级可观测）。
> **建评测/调优前**：查阅 `policies/llm-eval-methodology.md`（评测驱动开发方法论：评测集/评测体系/自动化评测/LLM-as-judge/调优）+ `references/eval-driven-development.md`（落地 SOP）。多子代理编排见 `policies/agent-team-methodology.md`。

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

用于测试 AI 脚本，并输出正式测试报告（软件层面：能不能跑、输出是否合法）。

### `/评测集 [对象]`

汇总 / 构建 / 体检评测集（黄金集）。产出 `eval-dataset.jsonl`（四桶：生产 60% / 对抗 15% / 边界 15% / 失败回放 10%）+ 评测集体检报告。见 `references/eval-driven-development.md`。

### `/AI评测 [对象]`

搭评测体系（维度+量规+grader+judge）并跑自动化评测。产出评分量规 + `eval-result.json` + 评测报告（含分维度、pass@k、失败聚类、回归对比）。**与 `/AI测试` 的区别**：测试问"能不能跑"，评测问"好不好、能否回归、能否调优"。

### `/AI调优 [对象]`

基于评测报告做**定向调优**（GEPA 式失败归因 → 每轮改 3–5 处 → A/B 回归对照）。产出新版提示词/服务 + 调优报告。

## Mode Deliverables

| 命令 | 默认产物 |
|---|---|
| `/AI策划` | AI PRD + AI 脚本 + AI 测试报告 + 可选脚本包 |
| `/AIPRD` | AI PRD（含提示词策略卡） |
| `/AI脚本` | AI 脚本 + 样例 + README / 调用文档 |
| `/AI测试` | AI 测试报告 |
| `/评测集` | 评测集 `eval-dataset.jsonl` + 体检报告 |
| `/AI评测` | 评分量规 + 评测结果 JSON + 评测报告 |
| `/AI调优` | 新版提示词/服务 + 调优报告 |

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

### 6. `/评测集`、`/AI评测`、`/AI调优` 工作流（评测驱动开发）

完整 SOP 见 `references/eval-driven-development.md`，方法论事实源是 `policies/llm-eval-methodology.md`。要点：

- **`/评测集`**：定单一 scope → 四桶采集（生产/对抗/边界/失败回放，脱敏去污染）→ 每条写可判定断言 → 跑 `scripts/aggregate_eval_dataset.py` 体检（schema/配比/规模）。
- **`/AI评测`**：定维度+权重+阈值 → grader 分层（规则优先，开放式才上 judge）→ 用 judge 时先校准（judge≠被测族、量规+模型版本钉死、≥50 条金标量 Cohen's κ）→ 跑 `scripts/run_eval.py` 出报告。
- **`/AI调优`**：从评测报告失败聚类做归因（ASI）→ 每轮改 3–5 处 → `run_eval.py --baseline` 做 A/B 回归 → 出调优报告；不回退已验证有效的改动。

机械工作优先复用：

- `scripts/run_eval.py`（自动化评测台：规则 grader + pass@k + 回归 + A/B + 可插拔 judge）
- `scripts/aggregate_eval_dataset.py`（评测集合并 + 校验 + 体检）
- `scripts/gen_eval_report.py`（报告渲染 + 调优骨架）

### 7. `/AI策划` 全流程串联

`/AI策划` 默认顺序是：

1. 先跑 `/AIPRD`（含提示词策略卡）
2. 再跑 `/AI脚本`（按 `ai-service-construction.md` 工程化）
3. 然后 `/AI测试`（软件能跑）
4. 视质量要求再跑 `/评测集` → `/AI评测` → `/AI调优`（质量度量与回归）

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
  - 从模板初始化 AI PRD、AI测试报告、开发 README、脚本包清单；`--with-eval` 同时 scaffold 策略卡/评测集/量规/评测报告/调优报告。
- `scripts/validate_ai_planning_assets.py`
  - 校验 PRD、测试报告、README、策略卡、评测报告、调优报告关键章节 + 评测集 JSONL。
- `scripts/package_ai_script_bundle.py`
  - 把源码、样例、文档打成开发可接入的 zip。
- `scripts/export_svg_to_png.js`
  - 把 SVG 流程图导出成 PNG，方便插入 PRD 或 README。
- `scripts/run_eval.py`
  - **自动化评测台**（纯标准库）：规则 grader + pass@k + 回归 + A/B + 可插拔 LLM-judge。见 `references/eval-harness-guide.md`。
- `scripts/aggregate_eval_dataset.py`
  - 评测集合并 + schema 校验 + 去重 + 桶配比/规模体检。
- `scripts/gen_eval_report.py`
  - 从评测结果 JSON 渲染评测报告，并可生成调优报告骨架。

## Model Selection

执行 `/AI脚本` 或 `/AI策划` 时，根据任务复杂度选择模型：

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 简单文案 / 分类 / 提取 / 高并发 | `Doubao-Seed-2.0-Mini-0215` | 成本最低，响应最快，效果≈1.6 |
| 内容创作 / 数据分析 / 结构化输出 | `Doubao-Seed-2.0-Lite-0215` | 均衡型，超越 1.8，成本优化 |
| 复杂推理 / Agent / 多模态 / 长链路 | `Doubao-Seed-2.0-Pro-0215` | 旗舰全能，复杂任务首选 |
| 图片理解 / 视觉定位 Grounding | `Doubao-Seed-2.0-Pro-0215` | 多模态能力最强 |
| 视频理解 | `Doubao-Seed-2.0-Pro-0215` | 仅 Pro 支持 |
| **LLM-as-judge 评测** | `Doubao-Seed-2.0-Pro-0215`（且**≠被测模型族**） | judge 要强且与被测异族，防自偏好；`temperature=0` |

默认先用 Mini，效果不够再升级。详细 API 文档见 `references/hellobike-platform-api.md`。

> **judge 选型铁律**：评测用的 judge 模型不能和被测模型同族（自偏好偏差 +10–25%）；judge 模型版本 + 量规版本要钉死成合同；用前先用 ≥50 条人工金标量 Cohen's κ 校准（见 `policies/llm-eval-methodology.md` 第 3.3 节）。

## API Capability Cookbook

每个 API 能力都有独立可运行的示例代码，位于 `examples/api-cookbook/`。

在 AI 策划中，这些示例不是让你照抄，而是按需组合的"能力积木"：

| 积木 | 适用场景 | 示例 |
|------|---------|------|
| 文本生成 + 结构化输出 | 简单生成类任务 | `01` + `10` |
| 深度思考 + 结构化输出 | 需要推理的分析任务 | `03` + `10` |
| 上下文缓存 | 长 System Prompt 降本 | `05` |
| 图片/视频理解 + Grounding | 多模态审核/识别 | `07` / `08` + `09` |
| 多 Agent Pipeline | 完整业务流程 | `11` |

详见 `examples/api-cookbook/README.md`。

## Resources

**方法论（先读）**
- **策略先行提示词**：`references/prompt-strategy-first.md`
- **AI 服务构建**：`references/ai-service-construction.md`
- **评测驱动开发 SOP**：`references/eval-driven-development.md`
- **自动化评测台指南**：`references/eval-harness-guide.md`
- 评测方法论事实源：`policies/llm-eval-methodology.md`
- 提示词技术目录：`policies/prompt-engineering-techniques.md`

**模板**
- AI PRD：`assets/ai-prd-template.md`
- 测试报告：`assets/test-record-template.md`
- 开发 README：`assets/developer-readme-template.md`
- 脚本包清单：`assets/script-bundle-manifest-template.md`
- 提示词策略卡：`assets/prompt-strategy-card-template.md`
- 评测集 + Schema：`assets/eval-dataset-template.jsonl` / `assets/eval-dataset.schema.json`
- 评分量规：`assets/judge-rubric-template.md`
- 评测报告：`assets/eval-report-template.md`
- 调优报告：`assets/tuning-report-template.md`

**平台与流程**
- **平台 API 文档**：`references/hellobike-platform-api.md`
- **平台能力实测矩阵**：`references/platform-capabilities.md`
- 执行 SOP：`references/execution-sop.md`
- 评审清单：`references/review-checklist.md`
- 脚本交付范围：`references/package-scope.md`
- 开发交接说明：`references/developer-handoff.md`

**示例与脚本**
- 示例指令：`examples/example-invoke.md`
- 评测示例指令：`examples/example-eval-command.md`
- **API 能力积木库**：`examples/api-cookbook/README.md`
- 脚本用法：`examples/example-validation-command.md`
- Scripts 索引：`scripts/README.md`