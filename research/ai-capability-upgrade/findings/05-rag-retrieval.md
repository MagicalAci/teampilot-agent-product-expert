# 域 5：RAG 与检索增强

> 子代理：rag-retrieval ｜ 回写：`research/ai-capability-upgrade/findings/05-rag-retrieval.md`
> 来源标注：〔web〕= 本轮用 WebSearch/MCP 搜索工具（2026-06 联网核实），附 URL；〔知识〕= 训练知识、未逐条联网复核（已尽量只用确有其物的库/论文/产品）；〔本地〕= 直接读本仓库文件/环境 MCP descriptor 得到；〔cross-ref〕= 引用其它域 findings 的结论。
> 边界：本域聚焦**把外部语料变成"可检索、可重排、可接地引用"的检索栈**——分块/嵌入/向量库/索引、混合检索与融合、重排、查询变换、Agentic/自适应/纠错 RAG、GraphRAG、多模态/视觉文档 RAG、长上下文 vs RAG 之争。**记忆/上下文供给角度**（write/select/compress/isolate、claude-mem 作记忆后端、长上下文 vs RAG 的"记忆视角"）见域 6；**对话内查询改写/澄清**见域 7；**RAG 评测指标本体**（faithfulness / context precision / RAGAS / nDCG harness）见域 9；**接地安全/防检索注入/防工具投毒**见域 10；**工具 RAG（按语义检索"工具"而非"知识"）**见域 4；**模型/语义缓存成本**见域 12。本域只取这些主题的**检索工程角度**并交叉引用。

---

## 领域概述

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是把"模型权重之外的知识"在推理时检索进上下文的工程栈。它已从 2023 的"naive 检索-拼接-生成"演化为一条**多段流水线**：①**索引侧**（分块 → 嵌入 → 建向量/混合索引）；②**检索侧**（查询变换 → 混合召回 → 重排 → 接地引用）；③**编排侧**（静态流水线 → Agentic/自适应/纠错循环）。2025-2026 的范式跃迁有五条主线：**(1) 高 ROI 单点上移到"上下文化分块"**——Anthropic Contextual Retrieval（给每块 LLM 生成 50-100 token 上下文前缀再嵌入+BM25）单独降检索失败 49%、配重排 67%，成为"最划算的一次改造"〔web〕；**(2) 嵌入进入"多模态 + 开源反超"时代**——Qwen3-Embedding-8B 开源登顶多语 MTEB（~70.6），Gemini Embedding 多模态领跑英文（~68.3），BGE-M3 一模型同出 dense+sparse+多向量〔web〕；**(3) 混合检索 + RRF 成事实标准、各库内建**（BM25+dense 用 Reciprocal Rank Fusion 融合，k=60 默认，纯向量在真实查询上约 40% 失手）〔web〕；**(4) RAG 从静态流水线转向 Agentic/自适应/纠错**——Self-RAG（反思 token 自评）、CRAG（评分文档→低置信兜底）、Adaptive-RAG（按复杂度路由检索深度）、A-RAG（把检索接口暴露给模型自主多粒度取数），实测 Agentic 比 Enhanced 平均 +2.8 NDCG@10〔web〕；**(5) "RAG 没死、长上下文没杀死它，分工变了"**——RAG 比百万 token 长上下文约便宜 1250×、快 30-60×，且 lost-in-the-middle 在 10M 窗口里"中间更大"；2026 共识是**混合：检索缩窄 → 长上下文推理**，检索退为"控制平面"（选择/溯源/引用/权限/新鲜度/成本路由）〔web〕。

**对「产品专家 Agent」这是一个"几乎从零"的能力域，但杠杆极高。** 它当前**没有任何显式检索层**：`skills/research-toolkit/`（RTK）的范式是"采集 → 规范化（`03-normalized/<platform>/summary.md` + `data.csv`）→ 人 + LLM 读全文 → 逐章写作 + 三轮事实核查"，证据靠**人工放置的可点击角标 `[n](路径)`**（见 `protocols/evidence-guide.md`）。这是"**全文喂入 / 人读 / grep 式定位**"，不是 RAG——它没有分块、没有嵌入、没有索引、没有重排、没有"检索前查询改写"。在小语料下没问题，但单产品任务 ≥200 条/平台 × 8 平台 = **1600+ 条社媒证据 + 官网/定价/App 全文**，全部塞进上下文做分析会撞上 context rot（域 6 已论证）、且无法"精确定位到支撑某条强判断的那一段证据"。`skills/aibi-query/` 是 **text-to-SQL**（自然语言→DBOPS 查询），属结构化检索，但它把 `references/数据库全景.md`（63 张表）+ `references/查询案例库.md`（11 案例）**全量读入上下文**生成 SQL——这正是"schema/few-shot 检索（Table-RAG）"的潜在改造点。`.cursor/rules/task-navigator.mdc` 在"任务启动"明确要读 `knowledge/`，但**仓库中尚无 `knowledge/` 目录、更无任何检索层**；环境已挂 **claude-mem MCP**（域 6 核实，自带 `search`/FTS + `build_corpus`/`query_corpus` 语义检索原语），等于"**检索后端已在手边，但 RAG 检索工程（分块/混合/重排/接地）未应用**"。

因此本域的命题是：**产品专家 Agent 不需要立刻上重型向量库，但应先把"检索前查询改写 + 混合检索 + 重排 + 上下文化引用"这套 SOTA 流水线，文件化为一条 Cursor 原生、可立即执行的 `retrieval-protocol.md` 行为协议**（即便后端只是 grep + claude-mem search + WebSearch，也按这套纪律做），把已有的 RTK 证据体系、aibi-query schema、claude-mem、`knowledge/` 串成可检索可接地的闭环。下文 SOTA 目录穷尽企业级 + 应用级 + 研究前沿，对标与落地建议逐项点名本仓库文件。

---

## SOTA 技术目录

> 按子类分组，共 **86 条**（11 子类）。成熟度口径：`事实标准`（行业默认/已成规范）、`成熟`（生产广泛使用）、`成长`（活跃、生产可用但仍演进）、`实验`（论文/原型/preview）。说明：MTEB/BEIR 分数、库版本号各来源口径不一，本表取**方向性参考**并标来源，不作精确承诺。

### A. RAG 总体范式与检索栈演进

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Naive RAG | 检索固定 top-k → 拼接 → 生成，单趟无优化 | 入门基线、小语料 | 事实标准（基线） | Lewis et al. 2020；通用 | 〔web〕 |
| Advanced / Enhanced RAG | 在 naive 上加 pre-retrieval（查询改写）+ post-retrieval（重排/压缩） | 检索质量不够时的第一档升级 | 成熟 | Gao et al. RAG Survey 2023；LangChain/LlamaIndex | 〔web〕 |
| Modular RAG | 把路由/记忆/融合/检索拆成可插拔模块按需编排 | 复杂多源/多策略系统 | 成长 | Modular RAG 综述；LlamaIndex Workflows | 〔web〕 |
| 两阶段检索（retrieve-then-rerank） | 廉价召回 top-N（混合）→ 精排重排到 top-k | 几乎所有生产 RAG 的骨架 | 事实标准 | 通用；ColBERT/cross-encoder 配套 | 〔web〕 |
| 检索即"控制平面"（retrieval as control plane） | 长上下文时代，检索退为选择/溯源/引用/权限/新鲜度/成本路由的治理层 | 决定"为什么仍要检索"的认知框架 | 成长（2026 共识） | Signal/Ragie/Wire 2026 | 〔web〕 |

### B. 分块（Chunking）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 固定大小分块 | 按字符/token 定长切（+overlap） | 最简基线、同构短文本 | 事实标准（基线，精度低） | 通用 | 〔web〕 |
| 递归分块（recursive） | 按分隔符层级递归切，512-token 务实默认 | 生产默认起点 | 成熟（默认） | LangChain `RecursiveCharacterTextSplitter` | 〔web〕 |
| 文档结构感知分块 | 按 Markdown/代码/标题/表格等自然结构切 | 结构化文档（手册/代码/财报） | 成熟 | Unstructured；LlamaIndex node parsers | 〔web〕 |
| 语义分块（semantic） | 按相邻句嵌入相似度找语义断点 | 主题混杂/叙事型文档 | 成长 | LlamaIndex SemanticSplitter | 〔web〕 |
| 层级父子 / small-to-big / auto-merging | 小块检索、命中后回溯父块/合并相邻块喂上下文 | 既要精准命中又要完整上下文 | 成熟（de facto 生产模式） | LlamaIndex AutoMergingRetriever / ParentDocument | 〔web〕 |
| 句窗检索（sentence-window） | 检索单句、生成时扩展其前后窗口 | 高精度定位 + 需周边语境 | 成熟 | LlamaIndex SentenceWindow | 〔知识〕 |
| Anthropic Contextual Retrieval | 嵌入前用 LLM 生成 50-100 token 块级上下文前缀（+Contextual BM25） | 检索"对了文档却错了块"、高 ROI 单点 | 成长（生产标准） | Anthropic 2024-09：失败 -49%，配重排 -67%，$1.02/1M（prompt 缓存） | 〔web〕 |
| Late Chunking（晚分块） | 先用长上下文模型整文档嵌入→再切块（token 级语境向量），无 LLM 调用 | 长文跨段依赖、想省 LLM 成本 | 成长 | Jina AI 2024；仅助 dense、不助 BM25 | 〔web〕 |
| Agentic / metadata-enriched 分块 | LLM 自主决定块边界 / 给块加治理元数据（来源/时效/实体） | 高价值语料、企业治理 | 成长 | 各家；Atlan 企业上下文层 | 〔web〕 |

### C. 嵌入：表征范式 + SOTA 模型

| 技术/模型 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Dense 稠密嵌入（单向量双塔） | 文本映射到稠密向量比余弦相似 | 语义检索默认 | 事实标准 | 通用 sentence-transformers | 〔web〕 |
| Sparse 稀疏（BM25 / 学习式 SPLADE） | 词面权重稀疏向量；SPLADE 学隐式查询扩展 | 精确词/术语/代码；SPLADE 补同义 | 事实标准（BM25）/成长（SPLADE） | Robertson BM25；SPLADE（BERT 词表 30,522 维，需 GPU） | 〔web〕 |
| ColBERT 多向量后期交互（MaxSim） | 保 token 级向量，查询-文档 token 两两 MaxSim 打分 | 高召回/多面查询/域漂移 | 成长 | ColBERTv2；存储×2-3、延迟高 | 〔web〕 |
| Matryoshka 表征学习（MRL） | 一次训练得可截断的嵌套维度，按需降维省存储 | 想动态权衡精度/存储 | 成长 | Kusupati et al. 2022；Gemini/Jina/Nomic 支持 flex dims | 〔web/知识〕 |
| 指令微调嵌入（instruction-tuned） | 用 task-type/指令前缀定制检索/分类/聚类向量 | 任务特化检索 | 成长 | Gemini task-type；E5-instruct；BGE-en-ICL | 〔web〕 |
| Gemini Embedding 001/2（Google） | 英文 MTEB ~68.3 领跑，原生多模态（text/img/video/audio/PDF），3072 维 | 多模态 + 易用 API 默认 | 成熟（API 默认） | Google，GA 2025 | 〔web〕 |
| Qwen3-Embedding-8B（阿里） | 多语 MTEB ~70.6 登顶，开源 Apache 2.0，32K 上下文 | 自托管/多语/长文/数据主权 | 成长 | Alibaba Qwen；首个开源霸榜 | 〔web〕 |
| NV-Embed-v2（NVIDIA） | 基于 Llama-3.1-8B 的开源高检索嵌入 | 自托管、高检索分 | 成长 | NVIDIA；CC-BY-NC | 〔web〕 |
| Cohere Embed v4 | 企业多模态（text+图），128K 上下文，可出 dense+sparse | 企业、长文、噪声数据、VPC | 成熟 | Cohere | 〔web〕 |
| Voyage-3.x（含 code/legal/finance 专版） | 域专精嵌入，Anthropic Contextual Retrieval 推荐之一 | 代码/法律/金融垂域 | 成熟 | Voyage AI（MongoDB） | 〔web〕 |
| Jina Embeddings v4 / v5 | 多模态 + MRL + LoRA 适配（v4 3.8B）/ 小型自托管（v5 ~677M） | 多模态/可适配/轻量自托管 | 成长 | Jina AI | 〔web〕 |
| BGE-M3（BAAI） | 一模型三功能：dense + sparse + ColBERT 多向量，100+ 语言 | 想一套模型搞定混合检索、MIT 自托管 | 成熟（自托管经典） | BAAI，MIT，568M | 〔web〕 |
| OpenAI text-embedding-3 / Nomic v2 / Snowflake Arctic / mxbai | 通用生态默认 / 超轻量（137M MoE）/ 企业 / 轻量英文 | 已在 OpenAI 生态 / 极致轻量自托管 | 成熟 | OpenAI；Nomic；Snowflake；Mixedbread | 〔web〕 |

### D. 向量库与索引

| 技术/产品 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| HNSW（分层可导航小世界图） | 图索引，高召回低延迟，内存型默认 | 绝大多数实时检索 | 事实标准 | 各库默认索引 | 〔web〕 |
| IVF（倒排 + 聚类） | 向量分桶、查时只搜近桶 | 大规模、容忍召回-延迟权衡 | 成熟 | FAISS IVF | 〔web〕 |
| DiskANN / StreamingDiskANN | SSD 上的图索引，内存有界，亿级单机 | 大规模、内存吃紧 | 成长 | Microsoft DiskANN；pgvectorscale 0.6 | 〔web〕 |
| 量化（PQ/SQ/二值） | 压缩向量省内存（乘积/标量/binary 量化） | 内存/成本敏感、超大规模 | 成熟 | FAISS PQ；各库量化 | 〔web〕 |
| GPU 索引（CAGRA） | GPU 加速构建/检索，十亿级 | 海量 + 有 GPU 预算 | 成长 | Milvus/RAFT CAGRA | 〔web〕 |
| pgvector（+pgvectorscale +ParadeDB） | Postgres 扩展，向量与业务数据同库、零新依赖 | 已用 Postgres、<50M 向量 | 成熟（2026 默认起点） | pgvector 0.8；Timescale pgvectorscale | 〔web〕 |
| Qdrant | Rust 自托管首选，payload 过滤一流，p50 ~4ms | 自托管、实时、强过滤 | 成熟 | Qdrant 1.13，Apache 2.0 | 〔web〕 |
| Weaviate | 原生 hybrid + 多租户隔离 + 内置向量化模块 | 要一流混合检索/多租户 SaaS | 成熟 | Weaviate 1.30 | 〔web〕 |
| Milvus / Zilliz | 十亿级、多索引（IVF/HNSW/DiskANN）、GPU 加速 | 100M-1B+ 企业规模 | 成熟 | Milvus 2.5 / Zilliz Cloud | 〔web〕 |
| Pinecone（Serverless） | 全托管零运维、可预测扩展，含合规（SOC2/HIPAA） | 不想运维、要托管默认 | 成熟 | Pinecone Serverless v3 | 〔web〕 |
| LanceDB / Chroma | 嵌入式（Lance 列式/多模态、本地优先）/ 原型首选 | 本地/边缘/原型、单进程 | 成熟（嵌入式） | LanceDB；Chroma | 〔web〕 |
| Turbopuffer | 对象存储（S3）无服务器向量库，冷数据极便宜 | 大规模 + 冷查询 + 成本优先 | 成长 | Turbopuffer（Notion 2025 采用） | 〔web〕 |
| Vespa / FAISS / sqlite-vec | hybrid+多向量一流引擎 / 经典库 / 嵌入式 SQLite 向量 | 大搜索栈 / 自建 / 极轻嵌入 | 成熟 | Vespa；Meta FAISS；sqlite-vec | 〔web〕 |

### E. 混合检索与融合

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 混合检索（BM25 + dense） | 词面精确 + 语义召回并行后融合，互补盲区 | 几乎所有生产 RAG | 事实标准（table-stakes） | 各库内建 | 〔web〕 |
| RRF（倒数排名融合） | 按排名（非分数）`Σ 1/(k+rank)` 融合，免分数归一，k=60 默认 | 融合异构检索器的默认法 | 事实标准 | Cormack et al. SIGIR 2009；OpenSearch/ES/Azure/Mongo/Weaviate 内建 | 〔web〕 |
| 加权 RRF / 按域权重 | 给 dense/BM25/SPLADE 不同权重（技术文档 boost BM25） | 已知某检索器在本域更强 | 成长 | ParadeDB；Mongo `$rankFusion`；Weaviate `alpha` | 〔web〕 |
| 分数归一融合（relativeScoreFusion） | min-max/L2 归一后加权相加（非纯排名） | 需要保留分数幅度信息 | 成长 | Weaviate relativeScoreFusion；OpenSearch normalization-processor | 〔web〕 |
| 稀疏-稠密统一模型 | 一个模型同出 dense + sparse（+多向量），免管两套 | 想简化混合检索栈 | 成长 | BGE-M3；Cohere Embed v4 | 〔web〕 |

### F. 重排（Reranking）

| 技术/产品 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Cross-encoder 重排 | 查询-文档联合编码精排 top-N → top-k（约 64% 生产系统用） | 召回够但精度不足 | 成熟（主流范式） | sentence-transformers cross-encoder | 〔web〕 |
| Cohere Rerank 3.5 | 托管 API 重排，100+ 语言，4096 token/doc | 不想自托管、要可靠性/SLA | 成熟（API 默认） | Cohere `rerank-v3.5`，~$1/1k 查询 | 〔web〕 |
| BGE-reranker-v2-m3 / -Gemma（BAAI） | 最常部署开源重排，m3 轻量 ~0.6B / Gemma ~9B 高质（MIT） | 自托管、多语、有 GPU | 成熟 | BAAI；BEIR ~71.5 / ~73.7 | 〔web〕 |
| Qwen3-Reranker（0.6B/4B/8B） | 开源高质量重排，BEIR ~71-77 | 自托管要顶级质量 | 成长 | Alibaba Qwen | 〔web〕 |
| Jina ColBERT v2 / Jina Reranker v2 | 后期交互重排 / 轻量多语 API 重排 | 多面查询单阶段 / 快速接入 | 成长 | Jina AI；BEIR ~70/~69 | 〔web〕 |
| LLM 列表式重排（RankLLM） | 用 LLM 直接对候选列表排序（listwise） | 零样本、复杂相关性判断 | 成长 | RankGPT / RankZephyr / RankVicuna | 〔web〕 |
| Voyage rerank-2.5 | 指令跟随式重排（可按指令调权） | 需按业务指令定制相关性 | 成长 | Voyage AI | 〔web〕 |
| ZeroEntropy zerank-2 / ms-marco-MiniLM | 校准概率多语 API 重排 / 超快英文小重排器 | 要可比概率分 / 英文原型 | 成长/成熟 | ZeroEntropy；MiniLM-L-6/L-12 | 〔web〕 |
| 视觉重排（MonoQwen-Vision / MonoVLM） | 对图像页候选做相关性重排 | 视觉文档 RAG 二阶段 | 实验 | MonoQwen-Vision | 〔web〕 |
| AnswerDotAI `rerankers`（统一抽象） | 一套 API 跨 cross-encoder/ColBERT/RankLLM/API/视觉 | 想在配置层换重排后端 | 成长 | answerdotai/rerankers | 〔web〕 |

### G. 查询变换（Query Transformation）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 查询改写（Rewrite-Retrieve-Read） | LLM 把模糊/口语/省略的 query 改写清晰再检索 | query 含噪、口语、指代 | 成熟 | Ma et al. 2023；LangChain | 〔web〕 |
| HyDE（假设文档嵌入） | 先让 LLM 生成"假设答案"，嵌入它来检索真实文档 | 短/生硬 query 语义召回弱、无标注对 | 成长 | Gao et al. 2022 | 〔web〕 |
| Multi-Query（多查询扩展） | 生成多个改写、各自召回取并集（默认 3） | query 歧义、词表不匹配 | 成熟 | LangChain `MultiQueryRetriever` | 〔web〕 |
| RAG-Fusion | Multi-Query + 用 RRF 融合多路排名（非简单并集） | 多视角改写都能捞到不同好块 | 成长 | Rackauckas/Raudaschl 2024 | 〔web〕 |
| Step-Back Prompting | 抽象出上位概念检索背景知识再答具体题 | query 过窄、需先取框架性背景 | 成长 | Zheng et al. 2023（PaLM-2L +27% TimeQA） | 〔web〕 |
| 查询分解（decomposition / sub-question） | 把复合/多跳问题拆成原子子问题分别检索再合成 | 多跳、跨源、比较类 | 成熟 | LlamaIndex `SubQuestionQueryEngine` | 〔web〕 |
| 路由式检索（query routing） | 按 query 类型路由到不同索引/数据源/策略 | 多源/多库、异构语料 | 成长 | LlamaIndex Router；语义路由（交叉域 3） | 〔web〕 |

### H. Agentic / 自适应 / 纠错 RAG

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Self-RAG | 训练模型产"反思 token"，自评是否要检索、检索/生成是否可用 | 想让模型自判检索必要性与质量 | 成长 | Asai et al. 2024 | 〔web〕 |
| CRAG（纠错式 RAG） | 轻量评估器给检索文档打分，低置信触发 web 兜底/查询改写 | 检索质量不稳、需纠错回路 | 成长 | Yan et al. 2024 | 〔web〕 |
| Adaptive-RAG | 分类器按 query 复杂度路由：不检索 / 单步 / 多步 | 想按难度省检索成本 | 成长 | Jeong et al. 2024 | 〔web〕 |
| RAPTOR | 递归摘要建层级树，支持多层级/全局检索 | 长文档/需全局综合 | 成长 | Sarthi et al. 2024 | 〔web〕 |
| FLARE / IRCoT | 前瞻式主动检索 / 检索与 CoT 交织迭代 | 长文生成、多跳推理 | 成长 | Jiang 2023；Trivedi 2023 | 〔web〕 |
| Agentic RAG（检索为工具、LLM 控流） | LLM 自主决定是否/如何改写、再检索、换源，工具式调用检索 | 复杂、开放、需动态决策 | 成长（2026 主线） | LangGraph/LlamaIndex；实测 +2.8 NDCG@10 vs Enhanced | 〔web〕 |
| A-RAG（分层检索接口） | 把 keyword/semantic/chunk 级检索接口暴露给模型自主多粒度取数 | 需模型驱动的自适应检索 | 实验 | A-RAG 2026（arXiv 2602.03442） | 〔web〕 |
| RQ-RAG / MA-RAG / 自纠错编排 | 查询澄清细化 / 多代理分工 / router+corrective+pre-act 三代理 | 研究前沿、强多步自纠 | 实验 | RQ-RAG；MA-RAG；FLAIRS-39 2026 | 〔web〕 |

### I. GraphRAG / 知识图谱 RAG

| 技术/产品 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Microsoft GraphRAG | 抽实体关系图 + 社区检测 + 层级摘要做全局综合 | 跨文档全局综合/"主题级"问答 | 成长 | Microsoft 2024（86% vs 32% 基线，但 ~40K token 贵） | 〔web〕 |
| LazyGraphRAG | 查询时按需建图 + 增量索引，砍预索引成本 | 想要 GraphRAG 质量但怕索引贵 | 成长 | Microsoft；报道 -6000x 成本 | 〔web〕 |
| LightRAG | 知识图 + 向量双层检索（low/high/hybrid） | 要图结构又要低延迟/低成本 | 成长 | Guo et al. 2025（~10K token，延迟更低） | 〔web〕 |
| HippoRAG / HippoRAG 2 | Personalized PageRank "人工海马体"做联想式多跳，省 token | 多跳推理 + 持续学习 + 成本敏感 | 成长 | OSU NLP（NeurIPS'24 / ICML'25，~1K token，10-30× 便宜） | 〔web〕 |
| PathRAG | 流式剪枝冗余关系路径，砍上下文 token | 嫌 GraphRAG/LightRAG 上下文冗余 | 实验 | PathRAG 2025（token -44%，胜 GraphRAG 60.4%） | 〔web〕 |
| OG-RAG | 本体接地、schema 约束抽取降幻觉 | 强 schema/合规域 | 实验 | OG-RAG（幻觉 -40%） | 〔web〕 |

### J. 多模态 / 视觉文档 RAG

| 技术/产品 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| ColPali | VLM（PaliGemma 3B）把 PDF 页当图，late-interaction MaxSim over patch，免 OCR | 视觉富文档（图表/表格/版面） | 成长 | Faysse et al. 2024（ICLR'25，立 ViDoRe 基准） | 〔web〕 |
| ColQwen2 / ColQwen3 | Qwen-VL 骨干、ViDoRe v1/v2 SOTA，多语/任意分辨率 | 2025-2026 视觉检索默认 | 成长 | ColVision 家族；TomoroAI colqwen3-embed-4b | 〔web〕 |
| MUVERA / FDE（固定维编码） | 把多向量压成单向量做 ANN，再精排，解 ColBERT/ColPali 存储爆炸 | 多向量上生产规模 | 实验 | Google MUVERA 2024 | 〔web〕 |
| Byaldi / 视觉 RAG 工具链 | ColPali 系 RAG 封装：PDF→图→索引→检索 | 快速搭视觉文档检索 | 成长 | AnswerDotAI Byaldi；microsoft/multi-modal-rag-with-colpali | 〔web〕 |
| 视觉检索 + VLM 生成 | 检索相关图页 → VLM（Qwen2-VL/Llava）读图作答 | 端到端视觉文档问答 | 成长 | HF cookbook；Mixpeek | 〔web〕 |
| Document AI / 版面解析（OCR 派） | 传统 OCR + 版面/表格抽取再走文本 RAG（对照视觉派） | 需结构化抽字段/可审计 | 成熟 | Azure/Google Document AI；Unstructured | 〔web/知识〕 |

### K. RAG 忠实度 / 接地 / 引用（交叉域 9/10，仅检索工程角度）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 引用/溯源接地（citation/attribution） | 答案每条结论带可点击来源、可回溯到检索块 | 任何要可信/可审计的输出 | 成熟 | 通用；本仓库 `evidence-guide` 角标雏形 | 〔web〕 |
| 忠实度/接地评测（faithfulness/groundedness） | 判答案是否被检索内容支撑（防"对的文档错的话"） | RAG 上线/回归前（评测本体见域 9） | 成长 | RAGAS；Vectara HHEM（详见域 9） | 〔web/cross-ref〕 |
| 检索质量指标（context precision/recall, nDCG/MRR/Recall@k） | 量化检索栈而非生成（先修检索再修生成） | 调分块/嵌入/重排时（harness 见域 9） | 成熟 | BEIR；RAGAS retrieval metrics | 〔web/cross-ref〕 |
| 检索接地安全（防注入/防投毒） | 把检索/网页内容当不可信数据，不让其"指令"被执行 | 接外部语料/采集结果（详见域 10） | 成长 | OWASP；Microsoft Prompt Shields（详见域 10） | 〔cross-ref〕 |

---

## 2025-2026 前沿与趋势

1. **"RAG 没死，长上下文没杀死它——分工变了。"** 〔web〕 RAG 比百万 token 长上下文约**便宜 1250×、快 30-60×**（长上下文单查询 $15+/30-60s vs RAG ~$0.0x/~1s）；RAG 框架使用量 2024→2026 涨 **400%**、约 **60% 生产 LLM 应用仍用 RAG**。长上下文（Llama 4 Scout 10M、Gemini 1M）单针召回 ~99%，但**多事实召回掉到 ~60%**、BABILong 显示模型"有效只用 10-20% 上下文"，lost-in-the-middle 在 10M 窗口里"中间更大"。2026 赢家是**混合：检索缩窄 → 长上下文推理**，检索退为"控制平面"（选择/溯源/引用/权限/新鲜度/成本路由）。
2. **最划算的一次改造是"上下文化分块 + 混合 + 重排"三件套叠加。** 〔web〕 Anthropic Contextual Retrieval 给每块 LLM 生成 50-100 token 上下文前缀：仅上下文嵌入降失败 ~35%、+Contextual BM25 到 ~49%、**+重排到 ~67%**；预处理一次性约 $1.02/1M token（靠 prompt 缓存）。结论被反复验证："embeddings+BM25 > 单 embeddings、top-20 优于 top-5、加重排再加分，且全部可叠加"。
3. **嵌入进入"多模态 + 开源反超"时代。** 〔web〕 首次有开源模型（Qwen3-Embedding-8B ~70.6）登顶多语 MTEB、压过所有 API；Gemini Embedding（~68.3）以原生五模态（text/img/video/audio/PDF）领跑英文与多模态；Cohere Embed v4 出首个生产级多模态 + 128K；BGE-M3 一模型同出 dense+sparse+多向量。选型从"看 MTEB 谁高"转向"先定模态/语言/自托管需求"。
4. **混合检索 + RRF 成事实标准、各库内建。** 〔web〕 纯向量在真实查询上约 **40% 失手**；BM25+dense 用 RRF（按排名非分数、k=60 默认）融合已是 table-stakes，OpenSearch/Elasticsearch/Azure AI Search/MongoDB Atlas/Weaviate 全内建；加权 RRF 按域调权（技术文档 boost BM25），SPLADE 学习式稀疏在 BEIR 上超 BM25 但要 GPU。
5. **重排成生产默认，开源逼平 API。** 〔web〕 约 **64% 生产 RAG 系统用重排**；最常部署开源 BGE-reranker-v2-m3，质量上 Qwen3-Reranker/BGE-Gemma 已逼近或超 Cohere Rerank 3.5（自托管约在 100 万查询/天后划算）；出现统一抽象层 AnswerDotAI `rerankers`（一套 API 跨 cross-encoder/ColBERT/RankLLM/视觉）。
6. **查询变换从"全用"转向"按失败模式选用 + 轻量路由"。** 〔web〕 共识规则：query 模糊→改写、词表不匹配→Multi-Query、语义鸿沟→HyDE、过窄→Step-Back、多跳→分解；**堆叠多种变换"很少帮忙、常常有害"**，应先修语料/索引、再用轻量路由按 query 复杂度选一种；运行时由 Agent 决定而非写死。
7. **RAG 从静态流水线转向 Agentic / 自适应 / 纠错。** 〔web〕 Self-RAG（反思 token 自评）、CRAG（评分文档→低置信 web 兜底）、Adaptive-RAG（按复杂度路由检索深度）、A-RAG（把检索接口暴露给模型自主多粒度取数）；实验对比 **Agentic 比 Enhanced 平均 +2.8 NDCG@10**（query 越偏离问句格式，自适应改写增益越大，NQ 上 +7.8）。LangGraph 成有状态 agentic 检索编排标准。
8. **GraphRAG 分化为四条路线、各有取舍。** 〔web〕 全局综合（Microsoft GraphRAG，86% 但 ~40K token 贵）↔ 省钱多跳（HippoRAG 2，~1K token、10-30× 便宜）↔ 增量低成本（LazyGraphRAG，查询时建图 -6000x）↔ 上下文剪枝（PathRAG，token -44%、胜 GraphRAG 60%）↔ 本体接地（OG-RAG，幻觉 -40%）。无通用赢家，按"全局 vs 多跳 vs 成本 vs 精度"选。
9. **视觉文档 RAG（ColPali/ColQwen）免 OCR 直接"看页"成新范式。** 〔web〕 把 PDF 页渲染成图、用 VLM 出 patch 级多向量、late-interaction MaxSim 检索，跳过脆弱的 OCR/版面解析管线，在视觉富内容上超最强文本 RAG；ColQwen2/3 居 ViDoRe SOTA、2026 默认；多向量存储贵→用 MUVERA/FDE 压成单向量先 ANN 再精排。
10. **向量库格局四分、pgvector 成默认起点。** 〔web〕 市场裂成"全托管（Pinecone/Zilliz/Weaviate Cloud）/ 自托管开源（Qdrant/Milvus）/ 嵌入式（LanceDB/Chroma/sqlite-vec）/ 用现成（pgvector/Redis/OpenSearch/Mongo）"四类；**已在 Postgres、<50M 向量首选 pgvector(+pgvectorscale)**，海量上 Milvus，自托管实时上 Qdrant，冷数据省钱上对象存储型 Turbopuffer（Notion 2025 采用）。

---

## 对标产品专家 Agent

> 核心命题：产品专家 Agent **没有显式检索层**——RTK 采集后"喂全文 / 人读 / grep 式定位"，aibi-query 是 text-to-SQL 全量读 schema，`knowledge/` 被 `task-navigator.mdc` 引用却**尚不存在**、更无检索；claude-mem 检索后端已挂载但 RAG 工程未应用。下表逐项"现状→差距→增强（P0/P1/P2）"，点名本仓库具体文件/skill。**原则**：先把 SOTA 检索流水线**文件化为行为协议（P0，后端可只是 grep+claude-mem+WebSearch）**，再按需上轻量基建（P1/P2）。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| RTK 采集 → `03-normalized/<platform>/summary.md`+`data.csv` → 人 + LLM **读全文**做六维分析；无分块/嵌入/索引/重排 | **完全无检索层**：1600+ 条社媒证据 + 官网/定价/App 全文全塞上下文做分析 → context rot（域 6）、无法精确定位"支撑某条强判断的那段证据" | **P0**：新增 `policies/retrieval-protocol.md`，把"**检索前查询改写 + 混合检索 + LLM 重排 + 上下文化引用**"定为行为协议（即便后端只是 grep + claude-mem search + WebSearch 也按此纪律）；RTK 分析阶段引用它 |
| Phase 0 已提炼"7 类关键词"（核心/别名/功能/长尾/评价/问题/竞品词）用于**采集** | 这套关键词扩展只服务"采、抓"，**没有服务"检索前查询变换"**：分析/核查时不做 HyDE/multi-query/step-back/分解，直接按原问法找证据 | **P0**：在 `retrieval-protocol.md` 写"按失败模式选一种查询变换"决策表（模糊→改写、多跳→分解、过窄→step-back、语义弱→HyDE），复用已有 7 类关键词作 multi-query 素材；**禁止无脑堆叠** |
| 证据靠人工放 `[n](路径)` 角标（`evidence-guide.md`），证据分级 A/B/C（`evidence-rules.md`） | 引用是**人手放置、无"检索→重排→接地"自动化**；规范化时证据块不自带语境（脱离原文易误读，正是 Contextual Retrieval 要解的问题） | **P0**：规范化 `03-normalized` 时给每条证据加 **1-2 行"上下文头"**（产品/平台/时间/支撑什么判断），是 Anthropic Contextual Retrieval 的文件级手动版，提升后续核查可检索性与引用准确度 |
| 三轮事实核查（`fact-check.md`）由独立 `research-review` 子代理读稿核验 | 核查是"通读比对"，**无"为每条强判断检索候选证据 → 重排 → 取最忠实者引用"的接地回路** | **P0/P1**：核查回路加 **LLM 重排（listwise）**——对每条强判断从证据池（grep/claude-mem）召回候选→LLM 按忠实度重排→引用 top（交叉域 9 提供 faithfulness 判据） |
| `task-navigator.mdc` 要求启动读 `knowledge/`；环境挂 claude-mem（FTS + corpus，域 6） | `knowledge/` **目录尚不存在**、无索引；claude-mem 的 `build_corpus/query_corpus` 语义检索**未被用作 RAG 后端** | **P1**：用 claude-mem `build_corpus` 把 `knowledge/` + 历史 `deliverables/` 建语义 corpus，`query_corpus` 作轻量语义检索后端（无需独立向量库，交叉域 6） |
| aibi-query 把 `references/数据库全景.md`（63 表）+ `查询案例库.md`（11 案例）**全量读入**上下文生成 SQL | 库/表/案例增多后"全量塞 schema"会提示膨胀、选表变难；**无 schema/few-shot 检索**（Table-RAG） | **P1**：aibi-query 加 **Table-RAG-lite**——按问题语义检索相关表 + few-shot 案例再注入（而非全量），复用 Tool-RAG 思路（交叉域 4 P1-2） |
| RTK 大量产物是**截图/录屏抽帧/App Store 截图/定价页**（`04-experience`、`08-visuals`） | 视觉证据靠人看，无**视觉文档检索**：无法"按图表/版面内容检索某张截图/某页 PDF" | **P2**：重基建——视觉富语料引入 ColPali/ColQwen 视觉 RAG（免 OCR 直接"看页"检索），需 GPU/多向量存储，标 P2（交叉域：多模态成本） |
| "市场全景"任务横比多产品（`market-landscape.md`），竞品/价格/功能随时间变 | 无**知识图谱 RAG**做"产品-功能-公司-价格"实体关系的全局综合；竞品迭代/价格变化无时序事实管理 | **P2**：全景类任务试 GraphRAG/LightRAG 做全局综合 + 借 Zep 时序图管"价格/口径随时间失效但留史"（交叉域 6 时序记忆） |
| RTK 已有"DeerFlow/MCP 不可用 → 降级 WebSearch+WebFetch"（`tooling-and-installation.md`） | 这是**朴素降级**，未形式化为 **CRAG/Adaptive-RAG**（评分检索结果不足 → 触发 web 兜底 / 按复杂度选检索深度） | **P2**：把降级升级为**纠错式检索**——证据不足/置信低时自动触发 web 兜底 + 记录"为何兜底"，按任务复杂度路由检索深度（Adaptive-RAG 思路） |

---

## 落地建议

> 原则：与本仓库"Cursor 原生、轻量聚焦、policy/rule/protocol 文件化、不引重运行时"一致。**P0 = 不需任何新基建、立刻可用的检索行为协议**（后端用 grep + claude-mem search + WebSearch 即可）；P1 = 用已挂载 claude-mem / 轻量嵌入式存储；P2 = 需重基建（视觉 RAG/GraphRAG/向量库），交叉引用兄弟域。每条给"放哪个文件 / 做什么 / 验收信号"（验收信号尽量可被 `tests/` 契约测试断言：文件存在 + 关键标记 + 触发词）。

### P0-1 新增检索协议 `policies/retrieval-protocol.md`（本域核心交付）
- **放哪**：`policies/retrieval-protocol.md`（新文件，与 `agent-team-methodology.md`/`prompt-engineering-techniques.md`/`llm-eval-methodology.md` 平级）；`.cursor/rules/task-navigator.mdc` 的"任务启动—主动分析"段加一句"涉及在已采集语料/`knowledge/`/记忆中找证据时，先读 `retrieval-protocol.md`"。
- **做什么**：Why-First 写法，把 SOTA 流水线落成**四步行为纪律**（后端无关）：①**检索前查询变换**（按失败模式选一种：模糊→改写、多跳→分解、过窄→step-back、语义弱→HyDE；复用 RTK 7 类关键词作 multi-query 素材；明确"**禁止无脑堆叠**、先修语料再加变换"）；②**混合检索**（词面 grep/`data.csv` 字段过滤 + 语义 claude-mem `search`/`query_corpus`/WebSearch 并行召回，RRF 心智："多路都命中的证据优先"）；③**重排**（对召回 top-N 用 **LLM listwise 重排**按相关性/忠实度排序，取 top-k 再读/引——零基建即可做）；④**上下文化引用**（引用证据时带"上下文头"，对齐 Contextual Retrieval）。附"何时用 RAG vs 直接全文喂入"判据（小语料/单文档可直接喂；>~数百条证据或跨任务复用走检索）。
- **验收信号**：`tests/test_product_expert_agent.py`（或新增 `tests/test_retrieval_protocol.py`）断言文件存在且含标记 `查询变换`/`混合检索`/`RRF`/`重排`/`上下文化引用`/`禁止堆叠`；至少 `research-toolkit` 或 `aibi-query` 的 SKILL/protocol 引用到它。

### P0-2 证据"上下文化"+ 上下文头（Contextual Retrieval 文件级手动版）
- **放哪**：`skills/research-toolkit/protocols/evidence-guide.md` + `references/evidence-rules.md` 增"证据上下文头"小节；规范条款写进 `retrieval-protocol.md`。
- **做什么**：规范化 `03-normalized/<platform>/data.csv`/`summary.md` 时，给每条关键证据加 **1-2 行上下文头**：`{产品}·{平台}·{时间}·{该证据支撑什么判断/属哪维度}`，再进引用与核查池。这让证据块"自带语境"——正是 Anthropic Contextual Retrieval 解决"块脱离原文即失义"的低成本手动版，直接提升 P0-1 检索/重排与引用准确度。
- **验收信号**：`data.csv` 含"上下文头/上下文/context"列或 `summary.md` 证据条目带上下文头；契约测试断言规范化产物存在该字段；一次真实任务里强判断引用可追到带上下文头的证据。

### P0-3 事实核查接地回路（检索→重排→忠实引用，交叉域 9）
- **放哪**：`skills/research-toolkit/protocols/fact-check.md` 的核查回路；`retrieval-protocol.md` 的"接地"小节。
- **做什么**：把三轮核查从"通读比对"升级为**对每条强判断**：召回候选证据（grep + claude-mem `search`）→ **LLM 按忠实度 listwise 重排** → 仅引用最被支撑者；不足则按 P0-1 走 web 兜底并标注。明确红线：**强判断必须有可重排选出的 A/B 级证据接地**，否则按 `evidence-rules.md` 降级表述（复用现有"缺什么/为何缺/影响哪条判断"模板）。
- **验收信号**：`fact-check.md` 含 `候选召回`/`重排`/`忠实度接地` 标记；一次真实任务的某条强判断留有"候选→重排→引用"痕迹；契约测试断言核查产物含接地说明。

### P1-1 claude-mem corpus 作语义检索后端（落实 RAG 后端，交叉域 6）
- **放哪**：`policies/retrieval-protocol.md` 的"检索后端"小节；与域 6 `policies/memory-protocol.md` 双向链接。
- **做什么**：用 claude-mem `build_corpus`/`prime_corpus` 把 `knowledge/`（**需先建该目录**）+ 历史 `deliverables/` 建语义 corpus，检索走 `query_corpus`（语义）+ `search`（FTS）双路 = 混合检索的"已挂载零新依赖"实现；**降级**：claude-mem 不可用回退 grep + WebSearch。明确"仓库/任务文件 = 真源，corpus = advisory"（与域 6 冲突仲裁一致）。
- **验收信号**：存在 `knowledge/` 且被建成 corpus；一次任务启动出现 `query_corpus`/`search` 调用并把命中纳入规划；claude-mem 宕机模拟下能降级不报错。

### P1-2 aibi-query Table-RAG-lite（schema/few-shot 检索，交叉域 4）
- **放哪**：`skills/aibi-query/SKILL.md` 的"③ 意图解析"步；`references/数据库全景.md`/`查询案例库.md` 加"按需检索"说明。
- **做什么**：库/表增多后，不再全量读 `数据库全景.md`，而是**按问题语义检索相关表 + 相关 few-shot 案例**再注入上下文生成 SQL（Table-RAG / 工具 RAG 思路，交叉域 4 P1-2）；现阶段 4 库可保持全量，写明"表数破阈值（如 >~30 表或多库联查）时启用"。
- **验收信号**：`SKILL.md` 含 `Table-RAG`/`按需检索表`/`案例检索` 标记与触发阈值；阈值内保持现状、阈值外检索注入；契约测试断言阈值说明存在。

### P1-3 轻量混合索引（嵌入式，按需）
- **放哪**：RTK 分析阶段可选脚本（`scripts/` 下）+ `retrieval-protocol.md`"重基建路径"小节。
- **做什么**：当单任务证据量大（如 >~800 条）时，用**嵌入式存储**（sqlite-vec / LanceDB，无需起服务）对 `03-normalized` 建 BM25 + dense 混合索引，分析/核查阶段检索而非读全量；嵌入模型选开源自托管（BGE-M3 一模型出 dense+sparse）或 API（按隐私/成本）。坚持"嵌入式优先、不引重型向量库"。
- **验收信号**：存在可选索引脚本；大语料任务下分析阶段走"检索 top-k"而非全量读；规范含"嵌入式优先 / 何时才上"判据。

### P2-1 视觉文档 RAG（ColPali/ColQwen，截图/PDF 富语料）
- **放哪**：`retrieval-protocol.md` 多模态小节；与 RTK `08-visuals`/`04-experience` 链接（重基建，标 P2）。
- **做什么**：对截图/录屏抽帧/App Store 截图/定价页 PDF 等视觉富证据，引入 **ColPali/ColQwen2 免 OCR 视觉检索**（页渲染成图→VLM 多向量→MaxSim 检索，多向量用 MUVERA/FDE 压缩降存储）；需 GPU/多向量存储，明确标 P2 重基建、先评估再上。
- **验收信号**：规范含视觉 RAG 选型（视觉派 ColQwen vs OCR 派 Document AI + 何时用）；若试点，留有"图页检索→VLM 作答"样例。

### P2-2 GraphRAG / 时序知识图谱（市场全景全局综合，交叉域 6）
- **放哪**：`skills/research-toolkit/task-types/market-landscape.md` 的可选增强；`retrieval-protocol.md` 图检索小节。
- **做什么**：全景类任务对"产品-功能-公司-价格"实体关系建图做**全局综合**（按成本选 LightRAG/HippoRAG 2 而非重的 Microsoft GraphRAG）；价格/口径等"会变的事实"借 **Zep 时序图**（旧事实失效但留史，交叉域 6）。重基建，标 P2。
- **验收信号**：`market-landscape.md` 含"全局综合可用 GraphRAG-lite + 时序事实管理"说明与选型权衡；若试点，留有实体关系图产物。

### P2-3 纠错式 / 自适应检索（升级现有降级，交叉域 9）
- **放哪**：`skills/research-toolkit/protocols/tooling-and-installation.md`（现有降级处）+ `retrieval-protocol.md`"自适应"小节。
- **做什么**：把"工具不可用→降级 WebSearch"升级为 **CRAG/Adaptive-RAG**：检索结果经评分（足够/不足/有歧义）→ 不足时自动触发 web 兜底 + 改写重检 + 记录"为何兜底"；按任务复杂度路由检索深度（简单直答 / 单步 / 多步），省成本。
- **验收信号**：规范含 `检索评分`/`web 兜底`/`检索深度路由` 标记；一次"证据不足→自动兜底"留痕；契约测试断言纠错回路说明存在。

---

## 参考来源

- 〔web〕嵌入与 MTEB 2026 — Awesome Agents《Embedding Model Leaderboard: MTEB April 2026》awesomeagents.ai/leaderboards/embedding-model-leaderboard-mteb-april-2026 ；Milvus《Best Embedding Model for RAG 2026》milvus.io/blog/choose-embedding-model-rag-2026.md ；PremAI blog.premai.io/best-embedding-models-for-rag-2026 ；Ailog app.ailog.fr/en/blog/news/rag-benchmark-mteb-2026 ；Mixpeek mixpeek.com/curated-lists/best-embedding-models（Gemini ~68.3 / Qwen3-Embedding-8B ~70.6 / NV-Embed-v2 / Cohere v4 / Voyage / Jina v4-v5 / BGE-M3，分数口径各源不一）。
- 〔web〕向量库 2026 — Chaos&Order《Vector Databases 2026 Deep-Dive》youngju.dev/blog/...2026-deep-dive ；Cadence《Best vector databases for production》cadence.withremote.ai/blog/best-vector-database-production ；SideGuy《10-Way Comparison 2026》sideguysolutions.com ；Awesome Agents awesomeagents.ai/tools/best-ai-vector-databases-2026 ；Encore encore.dev/articles/best-vector-databases（pgvector+pgvectorscale / Qdrant 1.13 / Weaviate 1.30 / Milvus 2.5 / Pinecone Serverless / LanceDB / Chroma / Turbopuffer / Vespa / FAISS / sqlite-vec；HNSW/IVF/DiskANN/CAGRA；多向量首选 Qdrant/Vespa/Weaviate/ParadeDB）。
- 〔web〕分块 — Anthropic《Contextual Retrieval》anthropic.com/engineering/contextual-retrieval（50-100 token 前缀、-49%/-67%、$1.02/1M）；AI Workflow Lab aiworkflowlab.dev/article/rag-chunking-strategies-late-contextual-semantic-2026 ；Digital Applied《RAG Chunking 2026 Playbook》digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook ；Atlan atlan.com/know/chunking-strategies-rag ；ai-system-design-guide 10-contextual-retrieval.md（Late Chunking Jina；small-to-big/auto-merging；sentence-window）。
- 〔web〕混合检索 / RRF / SPLADE — Digital Applied《Hybrid Search BM25, Vector & Reranking Reference 2026》digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026 ；Weaviate《Hybrid Search Explained》weaviate.io/blog/hybrid-search-explained ；ParadeDB《What is RRF》paradedb.com/learn/search-concepts/reciprocal-rank-fusion ；BigData Boutique bigdataboutique.com/blog/reciprocal-rank-fusion-how-it-works-and-when-to-use-it（Cormack et al. SIGIR 2009、k=60、加权 RRF、relativeScoreFusion）；charleschen.ai RRF 调参 wiki。
- 〔web〕重排 — TeachMeIDEA《Reranking in RAG: Cohere & Cross-Encoders》teachmeidea.com/reranking-in-rag-cohere-cross-encoders ；axiomlogica.com《AnswerDotAI rerankers vs BGE vs Jina 2026》；Presenc AI《Best Open-Weight Reranker Models 2026》presenc.ai/research/best-open-weight-reranker-models-2026（Cohere rerank-v3.5；BGE-reranker-v2-m3/Gemma；Qwen3-Reranker；Jina ColBERT v2；RankZephyr；~64% 生产用重排）；BSWEN docs.bswen.com/blog/2026-02-25-best-reranker-models（zerank-2 / MiniLM）。
- 〔web〕查询变换 — bestaiweb.ai《HyDE, Multi-Query & Step-Back》与《When to use HyDE vs Multi-Query vs Step-Back》；dmflow.chat《6 Advanced Query Transformation Architectures》；alexchernysh.com/blog/query-transformation-for-rag ；tianpan.co/blog/2026-04-16-rag-query-rewrite-layer（HyDE / Multi-Query / RAG-Fusion / Step-Back +27% TimeQA / 分解 LlamaIndex SubQuestion；"堆叠常有害、轻量路由按需用"）。
- 〔web〕Agentic / 自适应 / 纠错 RAG — A-RAG arxiv.org/pdf/2602.03442（方法对照表含 Self-RAG/CRAG/Adaptive-RAG/RAPTOR/FLARE/IRCoT/RQ-RAG/MA-RAG/HippoRAG2）；《Is Agentic RAG worth it?》arxiv.org/pdf/2601.07711（Agentic +2.8 NDCG@10 vs Enhanced）；ResearchGate《Development Status of RAG》（Self-RAG→Adaptive→CRAG 演进）；FLAIRS-39 2026《Iterative Self-Correcting Agentic RAG》journals.flvc.org/FLAIRS/article/view/141838（router+corrective+pre-act，faithfulness 0.95 vs 0.79）。原始论文：Self-RAG（Asai 2024）/ CRAG（Yan 2024）/ Adaptive-RAG（Jeong 2024）/ RAPTOR（Sarthi 2024）。
- 〔web〕GraphRAG 系 — Graph Praxis《GraphRAG vs HippoRAG vs PathRAG vs OG-RAG》medium.com/graph-praxis/...（MS GraphRAG 86% vs 32%；LazyGraphRAG -6000x；PathRAG token -44%/胜 GraphRAG 60.4%；OG-RAG 幻觉 -40%）；aiexpjourney.substack.com《Do You Really Need GraphRAG?》（GraphRAG ~40K / LightRAG ~10K / HippoRAG2 ~1K token）；HippoRAG github.com/osu-nlp-group/hipporag（NeurIPS'24 arXiv 2405.14831；HippoRAG 2 ICML'25 arXiv 2502.14802）；LightRAG Guo et al. 2025。
- 〔web〕多模态 / 视觉文档 RAG — Mixpeek《Visual Document Retrieval: ColPali & ColQwen》mixpeek.com/visual-document-retrieval ；HF docs ColQwen2 huggingface.co/docs/transformers/.../colqwen2 ；github.com/microsoft/multi-modal-rag-with-colpali（TomoroAI colqwen3-embed-4b）；HF cookbook multimodal_rag_using_document_retrieval_and_vlms（ColPali Faysse et al. 2024/ICLR'25、ViDoRe、Byaldi、MaxSim、Qwen2-VL 生成、MUVERA/FDE）。
- 〔web〕长上下文 vs RAG — Wire《RAG vs long context: what the 2026 data shows》usewire.io/blog/long-context-vs-rag-what-the-data-shows（1250× 便宜、RAG 用量 +400%、60% 生产用、lost-in-middle -30%）；Signal sunilprakash.com/...002-when-long-context-replaces-rag（BABILong 10-20%、Fabio Akita《Is RAG Dead?》2026-04、检索成控制平面）；Ragie ragie.ai/blog/ragie-on-rag-is-dead ；tianpan.co/blog/2026-04-09-long-context-vs-rag-production-decision-framework（多事实召回 ~60%、实用上限 32-64K）；MindStudio mindstudio.ai/blog/1m-token-context-window-vs-rag-claude。
- 〔本地〕本仓库对标 — `skills/research-toolkit/SKILL.md`（采集→规范化→读全文→逐章写作→三轮核查，无检索层）、`protocols/subagent-search.md`/`evidence-guide.md`/`evidence-rules.md`/`fact-check.md`（人工角标 + A/B/C 分级 + 通读核查）、`skills/aibi-query/SKILL.md`（text-to-SQL、全量读 `references/数据库全景.md` 63 表 + `查询案例库.md` 11 案例）、`.cursor/rules/task-navigator.mdc`（引用 `knowledge/` 但仓库无该目录）。
- 〔cross-ref〕claude-mem MCP（`search`/FTS + `build_corpus`/`query_corpus` 语义检索原语、3 层 search→timeline→get_observations）见域 6 findings/06-context-memory.md（〔本地〕descriptor 核实）；RAG 评测指标本体（faithfulness/context precision/RAGAS/nDCG harness）见域 9；接地安全/防检索注入见域 10；工具 RAG 见域 4；模型/语义缓存成本见域 12；长上下文记忆视角与 write/select/compress/isolate 见域 6。
