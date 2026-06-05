# 记忆协议（Memory Protocol）

这是产品专家 Agent 的**跨会话记忆读写规范**——补上"最薄弱却最高杠杆"的缺口：当前"记忆"≈ 任务文件夹过程文档 + 仓库文件 + `/经验写回` 手动 PR（离线人审的程序记忆），**没有跨会话情景/语义记忆**——新会话从零开始，"上次同类调研踩过的坑 / 某竞品口径 / 用户偏好"无法自动召回。本环境已挂 **claude-mem MCP**，可直接补上这层。

> 细节编目见 `research/ai-capability-upgrade/findings/06-context-memory.md`（52 条 SOTA、CoALA 记忆分类、claude-mem 接入评估）。检索机制见 `retrieval-protocol.md`；上下文预算见 `context-budget.md`。

---

## 1. 读时机 / 写时机 / 写什么

### 读（检索记忆）—— 任务/阶段启动先做
任务或阶段启动时，先按任务关键词**检索历史记忆**（同类对象、口径、踩坑）：命中则纳入规划，并在规划里标一行"已检索历史记忆：<命中/无>"。

### 写（观察写入）—— 阶段/任务收尾做
收尾写**结构化观察**，字段固定：
`kind / 决策 / 结论 / 口径与依据 / gotcha（踩坑）/ 未决项 / 来源`

### 写入白名单（关键，防记忆变噪）
**只写可复用的高信号结论**——决策、口径、踩坑、可复用判断框架。**绝不 dump 原文 / 中间废稿 / 大段采集数据**（那些写文件，记忆只留引用）。记忆是"系统"不是"垃圾场"。

---

## 2. 记忆后端：claude-mem（已挂载，零新依赖）

- 选用 `user-claude-mem`（环境内另有镜像 `plugin-claude-mem-mcp-search`，择一）。
- **作用域**：`projectId =` 仓库名（跨任务复用）或 task slug（任务内）。
- **读用官方 3 层省 token 工作流**：`search(query)` → `timeline(anchor=ID)` → `get_observations([IDs])`（先过滤再取全文，省约 10× token）；语义检索用 `query_corpus`。
- **写用** `observation_add`（按 §1 白名单与字段）。
- **降级**：MCP 不可用 → 回退本地 `tasks/{task}/memory/`（`episodic.md` 情景 / `semantic.md` 事实口径），保证离线可用与可人审。

---

## 3. 真源与冲突仲裁

- **仓库文件 / 任务产物 = source of truth；claude-mem 记忆 = advisory（参考）**。
- 记忆与仓库冲突 → **以仓库为准**；事实演变（旧竞品数据 vs 新数据）→ 旧记忆**失效但保留历史**（借 Zep 时序思想），不是直接覆盖。
- `/经验写回` 仍是**治理级程序记忆**（人审、可追溯、进仓库）；claude-mem 是**低摩擦 working recall（机器管理）**——二者互补，不互替。

---

## 4. 笔记机制（scratchpad，对抗 context rot）
长任务把"进展/决策/未决/下一步"写 `tasks/{task}/.notes/scratchpad.md`（窗口外），需要时拉回——与 `orchestration-runtime.md` 的状态账本互补（账本管编排状态，scratchpad 管思考过程）。

## 5. 与本仓库接线 + 生命周期（P1/P2）
- `task-navigator.mdc` 预检判定块加"先检索历史记忆"一步；收尾走观察写入。
- **P1**：建 `knowledge/` 目录 + 历史 `deliverables/` 用 `build_corpus` 建语义 corpus，作 `retrieval-protocol.md` 的语义后端。
- **P2 生命周期**：巩固（多条情景抽象成语义条目）/ 遗忘（近因×相关×效用衰减标归档）/ ACE 式演化写回——待 `agent-trajectory-eval.md` 评估基建就位后做。

## 何时查阅
- 任务启动该不该先查记忆、收尾写什么 → §1
- 用 claude-mem 读写与降级 → §2；冲突仲裁 → §3
