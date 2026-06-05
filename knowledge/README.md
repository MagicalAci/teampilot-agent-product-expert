# knowledge/ — 产品专家 Agent 跨任务知识库

这是产品专家 Agent 的**跨任务知识沉淀目录**，被 `.cursor/rules/task-navigator.mdc`（任务启动读取）与 `policies/retrieval-protocol.md`、`policies/memory-protocol.md` 引用。

## 用途

- **可复用的领域知识**：行业常识、产品口径、方法论速查、历史结论的提炼（高信号、可跨任务复用）。
- **检索/记忆后端的语料源**：用 claude-mem `build_corpus` 把本目录 + 历史 `tasks/*/deliverables/` 建成语义 corpus，`query_corpus` 作 `retrieval-protocol.md` 的语义检索后端；不可用时降级 grep。
- **真源边界**：本目录与仓库文件是 **source of truth**；claude-mem 记忆是 advisory（冲突以仓库为准，见 `memory-protocol.md`）。

## 写入纪律（接 memory-protocol 白名单）

- 只写**可复用的高信号结论**（决策、口径、踩坑、判断框架），**不 dump 原文 / 中间废稿 / 大段采集数据**（那些落 `tasks/{task}/deliverables/`，这里只留提炼与引用）。
- 收尾按 `memory-protocol.md` 的结构化观察字段（kind / 决策 / 结论 / 口径与依据 / gotcha / 未决项 / 来源）沉淀。

## 结构（按需创建子目录）

```
knowledge/
├── README.md          ← 本文件
├── domain/            ← 领域知识（行业/赛道/用户）
├── playbooks/         ← 方法论速查与可复用框架
└── glossary.md        ← 口径与术语表（按需）
```

> 当前为脚手架；随任务积累按 `memory-protocol.md` 增量写入，并按需 `build_corpus` 建语义索引。
