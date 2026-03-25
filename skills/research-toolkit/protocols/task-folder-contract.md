# 任务文件夹协议

这个 skill 现在支持三种任务形态：

- 全流程竞品任务
- 轻量采集任务
- 轻量体验任务

## 1. 全流程竞品任务

触发：

- `/竞品分析 [产品名]`

默认路径：

```text
docs/workspaces/research/_data/single-product/<product-slug>/<task-slug>/
```

最少必须包含：

- `00-admin/`
- `01-process/`
- `02-keywords/`
- `03-platforms/`
- `04-experience/`
- `05-synthesis/`
- `06-writing/`
- `07-factcheck/`
- `08-visuals/`

主报告默认位置：

```text
06-writing/<task-slug>.md
```

## 2. 轻量采集任务

触发：

- `/爬取 [主题或平台]`
- 默认新建独立采集任务
- 只有用户明确要求挂到旧任务时才允许复用

默认路径：

```text
docs/workspaces/research/_data/crawl-tasks/<task-slug>/
```

最少必须包含：

- `00-admin/`
- `01-process/`
- `02-keywords/`
- `03-platforms/`

## 3. 轻量体验任务

触发：

- `/竞品引导 [产品名]`
- 默认新建独立体验任务
- 只有用户明确要求挂到旧任务时才允许复用

默认路径：

```text
docs/workspaces/research/_data/guide-tasks/<task-slug>/
```

最少必须包含：

- `00-admin/`
- `01-process/`
- `04-experience/`

## 4. 强制文档

### 全流程任务

- `00-admin/TASK_CARD.md`
- `01-process/PROCESS_LOG.md`
- `01-process/KEY_DECISIONS.md`
- `02-keywords/SEARCH_KEYWORDS.md`
- `05-synthesis/SUBAGENT_ROSTER.md`
- `05-synthesis/REVIEW_GATE.md`
- `06-writing/WRITING_PLAN.md`
- `07-factcheck/FACTCHECK_PLAN.md`
- `08-visuals/VISUAL_PLAN.md`

初始化建议：

- `WRITING_PLAN.md` 优先按 `assets/writing-plan-table-template.md` 生成
- `FACTCHECK_PLAN.md` 和 `VISUAL_PLAN.md` 优先按 `assets/chapter-ops-tables.md` 里的表格生成

### 轻量采集任务

- `00-admin/TASK_CARD.md`
- `01-process/PROCESS_LOG.md`
- `01-process/KEY_DECISIONS.md`
- `02-keywords/SEARCH_KEYWORDS.md`
- `05-synthesis/SUBAGENT_ROSTER.md`
- `05-synthesis/REVIEW_GATE.md`

### 轻量体验任务

- `00-admin/TASK_CARD.md`
- `01-process/PROCESS_LOG.md`
- `01-process/KEY_DECISIONS.md`
- `04-experience/EXPERIENCE_SCRIPT.md`
- `04-experience/EXPERIENCE_REPORT.md`

## 5. 原则

- 每次默认新建任务目录，不复用之前同产品任务
- 只有用户明确要求继续或引用旧任务时，才能读取旧任务目录
- 每轮关键讨论都要补到 `PROCESS_LOG.md`
- 每个关键选择都要补到 `KEY_DECISIONS.md`
- 平台资料、截图、录屏、关键帧都要落盘
- 脚本可以创建空模板，但过程内容要由 AI 基于真实对话归纳填写
- 主报告必须保留在当前任务目录内，不允许写回共享稳定路径
