# 高级检索（P2 · 重基建，触发式启用）

这是 `retrieval-protocol.md`（P0 零基建检索四步）的**重基建延伸**。P0 用 grep + claude-mem + WebSearch 已覆盖 ~80% 检索需求；本文件定义**何时、如何**上更重的检索基建，以及每项的选型与降级。**默认不启用**——只有命中触发条件才按本文件实施，避免与"轻量聚焦"定位冲突。

> 来源 `findings/05-rag-retrieval.md`（86 条 SOTA）。轻量实现：`scripts/retrieval_index.py`（纯标准库 BM25+RRF，密集层可选）已落地，是本文件 §1 的零依赖入口。

---

## 0. 触发判定（先判要不要上）

| 触发条件 | 启用项 |
|---|---|
| 单任务证据 **> ~800 条**、grep 已显著变慢/召回差 | §1 嵌入式混合索引 |
| 检索结果质量不稳、需自动纠错与按难度分流 | §2 CRAG / Adaptive-RAG |
| 市场全景类、需"产品-功能-公司-价格"全局综合 | §3 GraphRAG-lite + 时序事实 |
| 截图/录屏/PDF 等**视觉富语料**需按内容检索 | §4 ColPali 视觉 RAG（需 GPU，最重） |

不命中 → 留在 `retrieval-protocol.md` 的 P0 四步。

## 1. 嵌入式混合索引（最轻的 P2，已有脚手架）

- **零依赖入口**：`scripts/retrieval_index.py` 纯标准库 **BM25 + RRF**（词面）对 `03-normalized` 证据建索引，CLI 检索 top-k；**密集层可选**——配置 `EMBED_ENDPOINT`（OpenAI 兼容 `/embeddings`）时叠加 dense + RRF 融合，未配置则降级纯 BM25。
- **要上向量库时选型**（仍坚持嵌入式优先、不起服务）：`sqlite-vec` / `LanceDB`（进程内、无服务）> Qdrant/Weaviate（需起服务，更重）。嵌入模型：BGE-M3（一模型出 dense+sparse，可本地）或 API（按隐私/成本）。
- **降级**：索引不可用 → 回退 P0 grep + claude-mem。

## 2. CRAG / Adaptive-RAG（纠错式 + 自适应深度）

把 `retrieval-protocol.md` 现有"工具不可用→降级 WebSearch"升级为：
- **CRAG（纠错式）**：检索结果先评分（足够 / 不足 / 有歧义）→ 不足时自动触发 web 兜底 + 查询改写重检 + 记录"为何兜底"。
- **Adaptive-RAG（按难度分流）**：小 LM/规则预判查询复杂度 → 简单直答 / 单步检索 / 多步检索，省算力。
- 这两项**几乎零基建**（行为+评分），可直接并入 `retrieval-protocol.md` 的"接地回路"，是 P2 里最该先做的。

## 3. GraphRAG-lite + 时序知识图谱

- 全景类任务对"产品-功能-公司-价格"实体关系建图做**全局综合**；选型按成本：**LightRAG / HippoRAG 2**（轻）> Microsoft GraphRAG（重，慎用）。最轻可先用"实体-关系 markdown 表 + 引用"手工图，不起图数据库。
- **时序事实**（价格/口径会变）：借 **Zep/Graphiti** 时序图思想——旧事实失效但保留历史（与 `memory-protocol.md` 冲突仲裁一致：仓库为真源）。
- 落点：`skills/research-toolkit/task-types/market-landscape.md` 的可选增强。

## 4. ColPali 视觉 RAG（最重，GPU 门槛）

- 截图/录屏抽帧/App Store 截图/定价页 PDF → **ColPali/ColQwen2 免 OCR 视觉检索**（页渲染成图→VLM 多向量→MaxSim；多向量用 MUVERA/FDE 压缩）。
- **需 GPU + 多向量存储**，最重；先评估 OCR 派（Document AI + 文本检索）是否够用，再决定是否上视觉派。默认不做。

## 5. 与本仓库接线
- `retrieval-protocol.md` 的"P2 远期"小节指向本文件；`scripts/retrieval_index.py` 是 §1 入口。
- 评测：检索质量（召回/忠实度）走 `agent-trajectory-eval.md` + `llm-eval-methodology.md`（Ragas 式 faithfulness/context precision）。

## 何时查阅
- 证据量大/检索质量差/全景综合/视觉语料 → §0 判触发 → 对应小节
