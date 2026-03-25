# Folder Structure

默认不要求宿主仓库具备 TeamPilot 的目录结构。

## 当前工作区输出

```text
outputs/<slug>/
├── drafts/
├── evidence/
│   └── social/
├── analysis/
├── delivery/
├── .meta/
└── manifest.json
```

## 全局运行时目录

```text
~/.local/share/cursor-research/
├── config.toml
└── vendor/
    └── deer-flow/
```

## 写入规则

- `evidence/`: 原始材料和索引
- `analysis/`: 中间判断和结构化表
- `drafts/`: 可继续修改的 Markdown
- `delivery/`: 导出物
- `.meta/`: doctor、日志、关键决策

## 主编排器附加产物

- `.meta/api-smoke.json`: 模型 / 搜索 API smoke check 结果
- `.meta/orchestrator-run.json`: 主编排器完整执行记录
- `analysis/research-plan.json`: 全流程计划与步骤状态
- `analysis/deerflow-response.json`: DeerFlow 响应原文（若 deep step 实际运行）
- `drafts/10-research-summary.md`: 主编排器输出的汇总草稿
