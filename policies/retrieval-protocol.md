# 检索协议（Retrieval Protocol）

这是产品专家 Agent 的**检索行为协议**——补上当前"**完全没有检索层**"的缺口：调研采集后是"喂全文 / 人读 / grep 式定位"，1600+ 条证据全塞上下文做分析，撞 context rot 且无法精确定位"支撑某条强判断的那段证据"。本协议把业界 RAG 流水线落成**四步行为纪律**，**后端零向量库即可落地**（grep + claude-mem search + WebSearch）。

> 细节编目见 `research/ai-capability-upgrade/findings/05-rag-retrieval.md`（86 条 SOTA）。原则：**先把检索流水线文件化为行为协议（P0，零基建）**，需重基建（向量库/GraphRAG/视觉 RAG）的标 P2。记忆/上下文角度见 `memory-protocol.md`、`context-budget.md`。

---

## 0. 何时走检索 vs 直接全文喂入

- **小语料 / 单文档 / 几十条证据**：直接全文喂入，别为检索而检索。
- **> ~数百条证据、跨任务复用、需精确取证支撑强判断**：走本协议四步。

---

## 1. 四步检索纪律

### ① 检索前查询变换（按失败模式选一种，禁止无脑堆叠）

| 失败模式 | 选用变换 |
|---|---|
| 表述模糊 | 查询改写（rewrite，补全实体/意图）|
| 多跳/复合问题 | 查询分解（decompose 成子查询）|
| 过窄/召回少 | step-back（退一步问更一般的问题）|
| 语义弱、词面对不上 | HyDE（先生成假设答案再拿它去检索）|
| 单一视角漏召回 | multi-query（复用调研 7 类关键词作多查询素材）|

**铁律：先修语料质量再加变换；一次只加一种，禁止把变换无脑叠满**（过度变换反而引噪、增本）。

### ② 混合检索（hybrid）

词面与语义**并行召回**，本仓库零基建实现：
- **词面**：`grep`/ripgrep 关键词、`data.csv` 字段过滤；
- **语义**：claude-mem `search`/`query_corpus`、`WebSearch`。
- **RRF 心智（Reciprocal Rank Fusion）**：多路都命中的证据排前——"既被关键词命中、又被语义命中"的证据最可信。

### ③ 重排（rerank）

对召回的 top-N 用 **LLM listwise 重排**：按"与问题的相关性 / 对结论的忠实度"排序，取 top-k 再读/引。零基建即可做（让模型对候选列表排序），不需 cross-encoder 服务。

### ④ 上下文化引用（contextual citation）

引用证据时带 **1–2 行"上下文头"**：`{产品}·{平台}·{时间}·{支撑什么判断/属哪维度}`——这是 Anthropic Contextual Retrieval 的文件级手动版，让证据块"自带语境"，提升核查与引用准确度。规范化 `03-normalized` 产物时即写入。

---

## 2. 检索后端（零新依赖优先）

| 后端 | 用途 | 降级 |
|---|---|---|
| `grep`/ripgrep | 词面精确定位 | —（永远可用）|
| claude-mem `search`/`query_corpus` | 语义检索（接 `memory-protocol.md`）| 不可用→grep + WebSearch |
| `WebSearch`/`WebFetch` | 外部兜底、实时事实 | 限流→停用不重试（接 `cost-discipline-methodology.md`）|

明确："**仓库/任务文件 = 真源，corpus/记忆 = advisory**"（冲突时以仓库为准，与 `memory-protocol.md` 一致）。

---

## 3. 接地回路（事实核查复用）

把三轮事实核查从"通读比对"升级为：对每条强判断 → 召回候选证据 → LLM 按忠实度重排 → 仅引用最被支撑者；不足则 web 兜底并标注。强判断必须有可重排选出的 A/B 级证据接地，否则按 `evidence-rules.md` 降级表述。与 `self-critique-and-grounding.md` 的"接地"步是同一回路。

## 4. 与本仓库接线 + P2 远期
- `task-navigator.mdc` 预检判定块：需在已采集语料/`knowledge/`/记忆中找证据时，先读本协议。
- `research-toolkit` 分析/核查阶段、`aibi-query`（表/案例按需检索 = Table-RAG-lite）引用本协议。
- **P2 远期**（需重基建，默认不做）：嵌入式混合索引（sqlite-vec/LanceDB，证据 >~800 条时）、CRAG/Adaptive-RAG 纠错式检索、GraphRAG 全局综合、ColPali 视觉 RAG。

## 何时查阅
- 在大语料里找证据、做核查取证 → §1
- 选检索后端 / 降级 → §2；接地 → §3
