# 上下文预算协议（Context Budget）

这是产品专家 Agent 的**上下文工程纪律**——补 `memory-protocol.md`（跨会话记忆）之外的"**窗口内 token 怎么花**"。核心物理事实：**上下文是有限的注意力预算、边际收益递减**，且所有前沿模型都有 **context rot**（性能随输入变长而退化）与 lost-in-the-middle（中部失准）。所以长程任务不能"把什么都塞进窗口"，要主动策展。

> 细节编目见 `research/ai-capability-upgrade/findings/06-context-memory.md`。与 `agent-team-methodology.md` 第四部分"Token 优化"、`cost-discipline-methodology.md`（省钱角度）对齐；记忆持久化见 `memory-protocol.md`。

---

## 1. 四范式（write / select / compress / isolate）映射五能力

| 范式 | 做什么 | 本仓库落地 |
|---|---|---|
| **write（写出窗口外）** | 大产物/原始数据写文件，上下文只留引用 | 采集原文/全文落 `deliverables/`、`context/`；过程笔记落 `.notes/scratchpad.md`（接 memory-protocol） |
| **select（按需选回）** | just-in-time 取回需要的片段，而非全量预载 | 用 `retrieval-protocol.md`（grep + claude-mem `query_corpus` + WebSearch）按需检索证据；用 claude-mem `search→timeline→get_observations` 三层只取过滤后全文 |
| **compress（压缩）** | 阶段边界做结构化摘要，丢冗余工具输出 | 长链路任务在阶段边界生成"决策/结论/未决"摘要（compaction），下一阶段以"摘要+最近文件"续跑；子代理只回蒸馏摘要不回原文 |
| **isolate（隔离）** | 把重上下文拆给子代理，主代理只收摘要 | 多平台采集/多视角分析扇出给子代理（接 `orchestration-runtime.md`）；子代理各自承担重上下文、回标准产物 |

---

## 2. 纪律要点

- **注意力预算意识**：每往窗口加一段都问"模型是否已知？没有它会出错吗？一个引用是否胜过整段原文？"——能不放就不放。
- **context rot 真实存在**：长任务默认走 write+compress（落文件+阶段摘要），而非把全程历史堆在窗口。
- **关键信息别埋中部**：重要约束/指令放上下文首尾（对抗 lost-in-the-middle），稳定内容前置还利于 prompt 缓存（`cost-discipline-methodology.md`）。
- **compaction 触发**：单阶段上下文显著增长（或跨阶段切换）时，先压成结构化摘要再继续。

## 3. 与本仓库接线
- `task-navigator.mdc` 预检判定块的"知识供给"项据本协议决定 write/select/compress/isolate。
- research 多平台采集默认 isolate（扇出）+ write（原文落文件）；PRD/Demo 长链路默认 compress（阶段摘要）。
- claude-mem 接入与降级见 `memory-protocol.md`；检索后端见 `retrieval-protocol.md`。

## 何时查阅
- 长链路任务上下文吃紧、要决定"放什么/不放什么" → §1–§2
- 阶段切换前做摘要 → §2 compaction
