---
name: education-prd-orchestrator
display_name: "教育产品策划主编排"
description: "证据驱动的产品策划主 Skill，支持产品定义闸门、章节编排、配图与文档校验的一体化 PRD 交付。"
category: product
version: "1.0.0"
review_criteria:
  - label: "入口指令可用性：/产品策划 与 /产品策划校验 能分别触发编写与校验流程。"
  - label: "任务卡冻结：在写作前明确交付物、受众、决策问题与范围。"
  - label: "证据先行：结论形成前完成证据清单与证据包整理。"
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

Use this skill as the single orchestrator for conclusion-oriented PRD work.

This package is designed to work as a portable personal skill under `~/.cursor/skills/education-prd-orchestrator/`.
Default outputs should go to a standalone delivery root such as `outputs/<slug>/`.
If the current workspace already has a stronger house structure like `docs/workspaces/product/`, you may mirror the final assets there, but never assume that structure exists.

Before calling local scripts, bootstrap the managed runtime once:

- `python scripts/bootstrap_product_planning_tools.py doctor`
- On macOS without a ready `python3`, use `bash scripts/bootstrap-macos.sh doctor`

## 两条指令

### 1. `/产品策划 [主题]`

用于启动或继续一次产品文档工作。

适用场景：

- 从 0 开始写 PRD
- 迭代已有 PRD
- 只补某一章
- 只补总览图
- 把一次产品工作流沉淀成 SOP 或 skill

默认行为：

1. 冻结任务卡
2. 建证据包
3. 过定义闸门
4. 路由章节 agent
5. 补图
6. 同步版本并校验

### 2. `/产品策划校验 [文档或主题]`

用于校验已有产物，而不是直接从头重写。

适用场景：

- 现有 PRD 有没有口径冲突
- 图和文是否一致
- 是否缺总领层
- 是否缺证据支撑
- 版本与索引是否同步

默认行为：

1. 读取现有文档和相关资产
2. 对照定义、结构、证据、图文关系做检查
3. 输出缺口、风险和修正建议
4. 如果用户明确要求，也可直接修正文档

Default execution order:

1. Freeze the task card
2. Gather evidence
3. Pass the definition gate
4. Route the relevant chapter agent
5. Add overview or chapter diagrams
6. Sync versions and validate

If the user only wants one chapter, one diagram, or the SOP itself, run the smallest useful subset, but do not skip the definition gate unless the upstream definition is already stable in the current document.

## Default Deliverables

- Portable output root: `outputs/<slug>/`
- Main document: `outputs/<slug>/prd.md`
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

### 1. Freeze the task card

- Confirm the target deliverable, audience, decision question, and current scope.
- Reuse the stable document if the user is clearly iterating an existing file.
- If there are multiple plausible goals, stop and ask the user to choose.

### 2. Gather evidence

- Read the `Evidence Agent` section in [references/agent-map.md](references/agent-map.md).
- Build an evidence inventory before drafting conclusions.
- If CSV, XLSX, screenshots, transcripts, or current PRD files exist, use scripts for the mechanical pass and keep human judgment for interpretation.

### 3. Pass the definition gate

- Read the `Definition Agent` section in [references/agent-map.md](references/agent-map.md).
- Always freeze:
  - what the product is
  - dual-end or role relationships
  - what the product is not
  - what the V1 main chain is
- Do not draft late chapters on unstable definitions.

### 4. Route chapter agents

- Read the relevant section in [references/agent-map.md](references/agent-map.md):
  - Chapter 1 Agent
  - Chapter 2 Agent
  - Chapter 3 Agent
  - Chapter 4 Agent
  - Chapter 5 Agent

Default chapter order is `1 -> 5`. If the user only requests one chapter, still inherit the latest stable upstream definition and evidence.

### 5. Add diagrams

- Read the `Diagram Agent` section in [references/agent-map.md](references/agent-map.md).
- Overview diagrams come after the chapter conclusion is stable.
- Prefer one diagram per job:
  - one for "from where to where"
  - one for "what functions exist and how they relate"
- Export SVG to PNG before inserting into the document.

### 6. Stop at user checkpoints

- Read [references/user-checkpoints.md](references/user-checkpoints.md).
- Never silently invent:
  - current product behavior
  - screenshots not seen
  - AI outputs not experienced
  - missing strategic decisions
- If evidence is missing or definitions diverge, stop and request exactly what the user must provide next.

### 7. Sync and validate

- Read the `Sync Agent` section in [references/agent-map.md](references/agent-map.md).
- Update the document version, review handoff notes, and image references inside the portable output root.
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
- Example invocations: [examples/example-invoke.md](examples/example-invoke.md)
- Example validation command: [examples/example-validation-command.md](examples/example-validation-command.md)
- Example checkpoint asks: [examples/example-user-checkpoint.md](examples/example-user-checkpoint.md)
- Example chapter outputs: [examples/example-chapter-output.md](examples/example-chapter-output.md)
- Example diagram brief: [examples/example-diagram-brief.md](examples/example-diagram-brief.md)
- Portable benchmark: [examples/portable-benchmark/README.md](examples/portable-benchmark/README.md)
- Benchmark case: [examples/hanxue-liaoliao-benchmark/README.md](examples/hanxue-liaoliao-benchmark/README.md)
- Package scope: [references/package-scope.md](references/package-scope.md)
- Developer handoff: [references/developer-handoff.md](references/developer-handoff.md)
- PRD template asset: [assets/prd-template.md](assets/prd-template.md)
- INDEX log template: [assets/index-log-template.md](assets/index-log-template.md)
- User checkpoint template: [assets/user-checkpoint-template.md](assets/user-checkpoint-template.md)
- Diagram brief template: [assets/diagram-brief-template.md](assets/diagram-brief-template.md)
- HTML page template: [assets/html-page-template.html](assets/html-page-template.html)
- Chart template: [assets/chart-template.html](assets/chart-template.html)
- Search plan template: [assets/search-plan-template.md](assets/search-plan-template.md)
- Evidence log template: [assets/evidence-log-template.csv](assets/evidence-log-template.csv)
- Evidence rules: [references/evidence-rules.md](references/evidence-rules.md)
- HTML design rules: [references/html-design-rules.md](references/html-design-rules.md)
- Visualization protocol: [references/visualization-protocol.md](references/visualization-protocol.md)

Read only the files needed for the current phase. Keep the orchestration path small and deterministic.