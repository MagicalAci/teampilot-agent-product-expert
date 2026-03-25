---
name: education-prd-orchestrator
display_name: "产品策划主编排"
description: "覆盖从用户画像到 PRD 交付的完整产品策划能力，支持全流程编排、阶段跳入和已有产物校验。"
category: product
version: "2.0.0"
review_criteria:
  - label: "入口指令可用性：/产品策划 与 /产品策划校验 能分别触发编写与校验流程。"
  - label: "任务卡冻结：在执行前明确交付物、受众、决策问题与范围。"
  - label: "证据先行：结论形成前完成证据清单与证据包整理。"
  - label: "上游方法论覆盖：根据任务需要使用用户画像、用户故事、用户旅程、痛点抽象、方案构思、假设验证、功能优先级等方法论。"
  - label: "定义闸门：稳定冻结产品定义、角色关系、非范围与 V1 主链路后再写后续章节。"
  - label: "章节编排一致性：章节输出与最新定义、证据口径保持一致。"
  - label: "图文一致：总览图与功能架构图与章节定义一致，且导出 PNG 后正确引用。"
  - label: "用户检查点合规：证据缺失或定义分歧时必须停下并向用户索取关键信息。"
  - label: "版本同步：文档版本、交接说明、资源引用在输出根目录内同步更新。"
  - label: "交付结构完整：按 outputs/<slug>/ 产出主文档、图片、证据和 review 目录。"
  - label: "资产校验通过：校验脚本运行后无图片引用断链或关键资源缺失。"
---

# 产品策划主 Skill

## Quick Start

Use this skill as the single orchestrator for full-cycle product planning, from user research through PRD delivery.

This package is designed to work as a portable personal skill under `~/.cursor/skills/education-prd-orchestrator/`.
Default outputs should go to a standalone delivery root such as `outputs/<slug>/`.
If the current workspace already has a stronger house structure like `docs/workspaces/product/`, you may mirror the final assets there, but never assume that structure exists.

Before calling local scripts, bootstrap the managed runtime once:

- `python scripts/bootstrap_product_planning_tools.py doctor`
- On macOS without a ready `python3`, use `bash scripts/bootstrap-macos.sh doctor`

## 两条指令

### 1. `/产品策划 [主题]`

用于启动或继续一次产品策划工作。

适用场景：

- 从 0 到 1 做完整产品策划（画像 → 故事 → 旅程 → 痛点 → 方案 → 假设 → 优先级 → PRD）
- 只补某一个阶段（如只做用户画像，或只写 PRD）
- 迭代已有 PRD
- 把一次产品工作流沉淀成 SOP 或 skill

默认行为：

1. 冻结任务卡
2. 建证据包
3. 用户画像
4. 用户故事
5. 用户旅程
6. 核心痛点抽象
7. 方案构思
8. 核心假设
9. 功能列表与优先级
10. 过定义闸门
11. 路由章节 agent（PRD 写作）
12. 补图
13. 同步版本并校验

### 2. `/产品策划校验 [文档或主题]`

用于校验已有产物，而不是直接从头重写。

适用场景：

- 现有 PRD 有没有口径冲突
- 图和文是否一致
- 是否缺总领层
- 是否缺证据支撑
- 上游阶段产物（画像、故事、优先级等）是否与 PRD 一致
- 版本与索引是否同步

默认行为：

1. 读取现有文档和相关资产
2. 对照定义、结构、证据、图文关系做检查
3. 输出缺口、风险和修正建议
4. 如果用户明确要求，也可直接修正文档

## 完整产品策划路径

```
冻结任务卡 → 建证据包 → 用户画像 → 用户故事 → 用户旅程
    → 核心痛点抽象 → 方案构思 → 核心假设 → 功能列表与优先级
    → 定义闸门 → PRD 章节写作 → 配图 → 同步校验
```

如果用户只要其中某个阶段，运行最小有用子集。但跳入后续阶段时，必须继承上游已有的稳定产物。

## Default Deliverables

- Portable output root: `outputs/<slug>/`
- Main document: `outputs/<slug>/prd.md`
- User persona: `outputs/<slug>/user-persona.md`
- User stories: `outputs/<slug>/user-stories.md`
- User journey: `outputs/<slug>/user-journey.md`
- Hypothesis log: `outputs/<slug>/hypothesis.md`
- Feature priority: `outputs/<slug>/feature-priority.md`
- Diagram assets: `outputs/<slug>/images/`
- HTML drafts: `outputs/<slug>/html/`
- Chart assets: `outputs/<slug>/charts/`
- Evidence pack: `outputs/<slug>/evidence/`
- Review handoff: `outputs/<slug>/review/`

Optional repository compatibility:

- If the host workspace already uses `docs/workspaces/product/`, you may additionally mirror:
  - the PRD into `docs/workspaces/product/prd/<slug>.md`
  - image assets into `docs/workspaces/product/prd/images/<slug>/`
  - index updates into `docs/workspaces/product/INDEX.md`

For folder conventions, read [references/folder-structure.md](references/folder-structure.md).

## Workflow

### Phase 1. Freeze the task card

- Confirm the target deliverable, audience, decision question, and current scope.
- Determine the starting point: full-cycle from scratch, jump-in at a specific phase, or iterate existing documents.
- Reuse the stable document if the user is clearly iterating an existing file.
- If there are multiple plausible goals, stop and ask the user to choose.

### Phase 2. Gather evidence

- Read the `Evidence Agent` section in [references/agent-map.md](references/agent-map.md).
- Build an evidence inventory before drafting conclusions.
- If CSV, XLSX, screenshots, transcripts, or current PRD files exist, use scripts for the mechanical pass and keep human judgment for interpretation.

### Phase 3. User Persona（用户画像）

- Read the methodology: [references/methodology/user-persona.md](references/methodology/user-persona.md)
- Read the `Persona Agent` section in [references/agent-map.md](references/agent-map.md).
- Based on evidence, build 2-4 user personas.
- Output to `outputs/<slug>/user-persona.md` using template [assets/user-persona-template.md](assets/user-persona-template.md).
- Mark primary persona. Tag data confidence for each persona.
- User checkpoint: if evidence is insufficient to distinguish personas, stop and ask.

### Phase 4. User Story（用户故事）

- Read the methodology: [references/methodology/user-story.md](references/methodology/user-story.md)
- Read the `Story Agent` section in [references/agent-map.md](references/agent-map.md).
- For each persona, convert core goals and pain points into user stories with acceptance criteria.
- Group stories into Epics.
- Output to `outputs/<slug>/user-stories.md` using template [assets/user-story-template.md](assets/user-story-template.md).

### Phase 5. User Journey（用户旅程）

- Read the methodology: [references/methodology/user-journey.md](references/methodology/user-journey.md)
- Read the `Journey Agent` section in [references/agent-map.md](references/agent-map.md).
- Map the primary persona's end-to-end experience, marking emotions, touchpoints, pain points and opportunities.
- Identify key moments: Aha Moment, decision points, friction points.
- Output to `outputs/<slug>/user-journey.md` using template [assets/user-journey-template.md](assets/user-journey-template.md).
- If multi-role, map each role's journey and mark interaction nodes.

### Phase 6. Pain Point Abstraction（核心痛点抽象）

- Read the methodology: [references/methodology/pain-point-abstraction.md](references/methodology/pain-point-abstraction.md)
- Read the `Pain Point Agent` section in [references/agent-map.md](references/agent-map.md).
- Aggregate all pain points from personas, journeys, evidence.
- De-duplicate, merge, and abstract upward to 3-5 core problem domains.
- Rank by impact breadth, depth, solvability, and strategic alignment.
- User checkpoint: confirm the focused problem domains with user before proceeding.

### Phase 7. Solution Ideation（方案构思）

- Read the methodology: [references/methodology/solution-ideation.md](references/methodology/solution-ideation.md)
- Read the `Ideation Agent` section in [references/agent-map.md](references/agent-map.md).
- Generate candidate solutions from product, user, and technical perspectives.
- Filter, compare, and select the winning direction.
- User checkpoint: the solution direction must be confirmed by user.

### Phase 8. Core Hypothesis（核心假设）

- Read the methodology: [references/methodology/hypothesis-validation.md](references/methodology/hypothesis-validation.md)
- Read the `Hypothesis Agent` section in [references/agent-map.md](references/agent-map.md).
- Extract value, usability, feasibility, and viability assumptions from the chosen solution.
- Rank by risk × impact. Design validation methods for high-priority hypotheses.
- Output to `outputs/<slug>/hypothesis.md` using template [assets/hypothesis-template.md](assets/hypothesis-template.md).
- User checkpoint: confirm which hypotheses are verified, which need validation, which are accepted risks.

### Phase 9. Feature List & Prioritization（功能列表与优先级）

- Read the methodology: [references/methodology/feature-prioritization.md](references/methodology/feature-prioritization.md)
- Read the `Priority Agent` section in [references/agent-map.md](references/agent-map.md).
- Decompose solution into concrete features. Link each to user stories and personas.
- Apply MoSCoW for rough classification, then RICE or ICE for fine ranking.
- Draw the V1 line. Explicitly list Won't-have items.
- Output to `outputs/<slug>/feature-priority.md` using template [assets/feature-priority-template.md](assets/feature-priority-template.md).
- User checkpoint: V1 scope must be confirmed by user.

### Phase 10. Pass the definition gate

- Read the `Definition Agent` section in [references/agent-map.md](references/agent-map.md).
- Synthesize upstream outputs (persona, story, journey, pain points, solution, hypothesis, features) into:
  - One-line product definition
  - Role relationships (if multi-role)
  - What the product is NOT
  - V1 main chain
- Do not draft PRD chapters on unstable definitions.

### Phase 11. Route chapter agents（PRD 章节写作）

- Read the relevant section in [references/agent-map.md](references/agent-map.md):
  - Chapter 1 Agent: 背景与问题
  - Chapter 2 Agent: 目标用户与场景
  - Chapter 3 Agent: 产品定义与方案
  - Chapter 4 Agent: 范围与边界
  - Chapter 5 Agent: 功能定义
  - Chapter 6 Agent: 流程与交互
  - Chapter 7 Agent: 依赖与风险

Default chapter order is `1 -> 7`. If the user only requests one chapter, still inherit the latest stable upstream definition and evidence.

PRD chapters now pull directly from upstream deliverables:
- Chapter 1 pulls from evidence pack
- Chapter 2 pulls from user personas and user journeys
- Chapter 3 pulls from solution ideation and core hypothesis
- Chapter 4 pulls from feature priority (V1 line + Won't-have)
- Chapter 5 pulls from feature priority details and user stories
- Chapter 6 pulls from user journeys and feature interactions
- Chapter 7 pulls from hypothesis validation and evidence gaps

### Phase 12. Add diagrams

- Read the `Diagram Agent` section in [references/agent-map.md](references/agent-map.md).
- Overview diagrams come after the chapter conclusion is stable.
- Prefer one diagram per job:
  - one for "from where to where"
  - one for "what functions exist and how they relate"
- Export SVG to PNG before inserting into the document.

### Phase 13. Stop at user checkpoints

- Read [references/user-checkpoints.md](references/user-checkpoints.md).
- Never silently invent:
  - current product behavior
  - screenshots not seen
  - AI outputs not experienced
  - missing strategic decisions
- If evidence is missing or definitions diverge, stop and request exactly what the user must provide next.

### Phase 14. Sync and validate

- Read the `Sync Agent` section in [references/agent-map.md](references/agent-map.md).
- Update the document version, review handoff notes, and image references inside the portable output root.
- Ensure upstream deliverables (persona, stories, journey, hypothesis, priority) are consistent with final PRD.
- If a repository-level product index already exists, sync it as an optional mirror instead of treating it as a hard requirement.
- Run the validation scripts before claiming completion.

## Shared Prompt Rules

All internal agents must follow [references/prompt-rules.md](references/prompt-rules.md).

Non-negotiable rules:

- Write in conclusion-oriented PRD style.
- Separate evidence, judgment, and open questions.
- Do not output internal reasoning or tool logs into the final document.
- Use one stable term for one concept.
- Keep diagrams and text on the same product definition.

## Product Methodology Knowledge Base

The following reference files serve as methodology knowledge base. They are NOT mandatory invocations — agents should consult them when the current phase needs methodological guidance:

- User Persona: [references/methodology/user-persona.md](references/methodology/user-persona.md)
- User Story: [references/methodology/user-story.md](references/methodology/user-story.md)
- User Journey: [references/methodology/user-journey.md](references/methodology/user-journey.md)
- Pain Point Abstraction: [references/methodology/pain-point-abstraction.md](references/methodology/pain-point-abstraction.md)
- Solution Ideation: [references/methodology/solution-ideation.md](references/methodology/solution-ideation.md)
- Core Hypothesis: [references/methodology/hypothesis-validation.md](references/methodology/hypothesis-validation.md)
- Feature Prioritization: [references/methodology/feature-prioritization.md](references/methodology/feature-prioritization.md)

Read only when the current phase needs it. Do not preload all methodology files at once.

## Scripts

- `scripts/analyze_chat_csv.py`
  - Summarize chat-log CSV files and keyword coverage.
- `scripts/bootstrap_product_planning_tools.py`
  - Create the managed `.venv`, install `requirements.txt`, and print environment status.
- `scripts/bootstrap-macos.sh`
  - Install missing macOS prerequisites, then call the Python bootstrap.
- `scripts/doctor-macos.sh`
  - Quick macOS health check wrapper around bootstrap.
- `scripts/run_pipeline.py`
  - Unified CLI for `check-env`, `bootstrap-tools`, `init-delivery`, `validate`, and `package-smoke`.
- `scripts/init_product_planning_delivery.py`
  - Seed a standalone `outputs/<slug>/` delivery skeleton from local templates.
- `scripts/analyze_kb_xlsx.py`
  - Summarize workbook sheets and keyword coverage.
- `scripts/build_screenshot_index.py`
  - Build a markdown screenshot index from a folder.
- `scripts/export_svg_to_png.py`
  - Export one or more SVG diagrams to PNG.
- `scripts/validate_prd_assets.py`
  - Validate image references inside markdown documents.

Use scripts for mechanical work only. Use agent references for product judgment.

## Success Criteria

- Upstream deliverables (persona, stories, journey, pain points, hypothesis, feature priority) are consistent and traceable.
- The product definition is consistent across all chapters and diagrams.
- Every chapter is evidence-backed and conclusion-oriented.
- Required user checkpoints were not skipped.
- Diagram assets render successfully and are inserted correctly.
- The portable delivery root stays internally consistent, and any optional repository mirror stays in sync with it.
- Validation scripts report no broken asset references.

## Resources

- SOP: [references/sop.md](references/sop.md)
- Orchestration rules: [references/orchestration-rules.md](references/orchestration-rules.md)
- Prompt rules: [references/prompt-rules.md](references/prompt-rules.md)
- Folder structure: [references/folder-structure.md](references/folder-structure.md)
- User checkpoints: [references/user-checkpoints.md](references/user-checkpoints.md)
- Evidence rules: [references/evidence-rules.md](references/evidence-rules.md)
- HTML design rules: [references/html-design-rules.md](references/html-design-rules.md)
- Visualization protocol: [references/visualization-protocol.md](references/visualization-protocol.md)
- Package scope: [references/package-scope.md](references/package-scope.md)
- Developer handoff: [references/developer-handoff.md](references/developer-handoff.md)
- Review criteria: [references/review-criteria.md](references/review-criteria.md)
- PRD template: [assets/prd-template.md](assets/prd-template.md)
- User persona template: [assets/user-persona-template.md](assets/user-persona-template.md)
- User story template: [assets/user-story-template.md](assets/user-story-template.md)
- User journey template: [assets/user-journey-template.md](assets/user-journey-template.md)
- Hypothesis template: [assets/hypothesis-template.md](assets/hypothesis-template.md)
- Feature priority template: [assets/feature-priority-template.md](assets/feature-priority-template.md)
- INDEX log template: [assets/index-log-template.md](assets/index-log-template.md)
- User checkpoint template: [assets/user-checkpoint-template.md](assets/user-checkpoint-template.md)
- Diagram brief template: [assets/diagram-brief-template.md](assets/diagram-brief-template.md)
- HTML page template: [assets/html-page-template.html](assets/html-page-template.html)
- Chart template: [assets/chart-template.html](assets/chart-template.html)
- Search plan template: [assets/search-plan-template.md](assets/search-plan-template.md)
- Evidence log template: [assets/evidence-log-template.csv](assets/evidence-log-template.csv)
- Example invocations: [examples/example-invoke.md](examples/example-invoke.md)
- Example validation command: [examples/example-validation-command.md](examples/example-validation-command.md)
- Example checkpoint asks: [examples/example-user-checkpoint.md](examples/example-user-checkpoint.md)
- Example chapter outputs: [examples/example-chapter-output.md](examples/example-chapter-output.md)
- Example diagram brief: [examples/example-diagram-brief.md](examples/example-diagram-brief.md)
- Portable benchmark: [examples/portable-benchmark/README.md](examples/portable-benchmark/README.md)
- Benchmark case: [examples/hanxue-liaoliao-benchmark/README.md](examples/hanxue-liaoliao-benchmark/README.md)

Read only the files needed for the current phase. Keep the orchestration path small and deterministic.
