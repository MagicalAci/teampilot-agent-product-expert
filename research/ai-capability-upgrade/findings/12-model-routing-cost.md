# 域 12：模型路由、推理优化与成本/缓存

> 研究子代理：model-routing-cost ｜ 回写：`research/ai-capability-upgrade/findings/12-model-routing-cost.md`
> 来源标注：〔web〕= 本轮 WebSearch/WebFetch 核实（2026-06，附 URL）；〔知识〕= 既有知识、未本轮逐条联网核实（按保守口径，只用确有其物的框架/论文/产品，把握不准标"(待核实)"）。
> 成熟度口径：`事实标准`（行业默认/已成规范）、`成熟`（生产广泛使用）、`成长`（活跃、生产可用但仍演进）、`实验`（论文/原型/preview）。
> 边界：本域聚焦 **"同样的活，怎么用更少的钱/时间/算力办成"**——模型分级路由（成本-质量角度）、级联、三层缓存（prompt/结果/语义）、推理服务与系统优化、量化部署成本意识、思考预算成本、token 经济/FinOps/预算护栏、自托管 vs API 权衡。**路由的意图判定/语义路由机制**见域 3（本域只取成本-性能-缓存角度，不重复其意图分类）；**工具结果缓存的记忆角度**见域 6、**工具接口角度**见域 4；**推理时算力换质量的推理范式角度**见域 1；**成本可观测的遥测基建**（OTel GenAI）见域 9；**自动 prompt 优化省 token** 见域 11。

---

## 领域概述

「模型路由与成本/缓存」是 Agent 的**经济引擎**——它不改变"做什么"，只优化"用什么档位的模型、是否复用算过的结果、花多少 token/钱/延迟把活办成"。2025-2026 这一层的范式跃迁有四条主线：①**路由成为产品默认形态**：GPT‑5 把 fast/thinking 的实时 router 内置进单一入口；OpenRouter/LiteLLM/Portkey/Helicone 等每个生产网关都内置了路由，"简单查询走便宜模型、难查询走贵模型"从工程技巧变成基础设施默认能力，公开基准显示路由可在保 95% 前沿质量的同时省 30–85% 成本。②**缓存从单层走向三层叠加**：prompt/前缀 KV 缓存（厂商侧，命中省 50–90%）+ 结果缓存（按"工具名+入参"键，带 TTL）+ 语义缓存（嵌入近似命中），三者叠加 batch API（离线 50% 折扣）可把"对的工作负载"成本砍 75–95%。③**思考预算成为最贵的旋钮**：推理模型的"思考 token"按输出价计费却不可见，`reasoning_effort`/`thinking budget` 在 minimal 与 high 间能产生 30–80× 的成本摆动——"默认不要用最高档"成为新成本纪律。④**预算从"可观测"走向"可强制"**：业界开始严格区分 observability（Langfuse/Helicone 只记录、不能拒绝调用）与 enforcement（网关/circuit breaker 能在超预算时返回 429 / 停止），跑飞的 Agent 循环成为头号成本事故源。

对「产品专家 Agent」而言，本域既"近"又"远"。**近**在于：它是 **Cursor 原生**消费方，模型由 IDE 提供、无自有 serving，因此 vLLM/SGLang/量化这类**重 serving 基建对它当前不适用**（标 P2，仅"若未来自托管 router/embedding/rerank 小模型"参考）；但**成本纪律可以、且应该文件化**。**远**在于：`policies/agent-team-methodology.md` **第四部分第 2 节"Token 优化"**已有方法论意识——"模型分级路由：简单转换/确定性任务用轻量模型或直接编辑，复杂推理/架构才上重模型""系统提示瘦身""长任务用后台/子代理隔离上下文"——但**全是原则、无落地约定**：没有模型分级决策表、没有 prompt 缓存/前缀稳定化意识、没有语义缓存、没有思考预算档位、没有任务级成本预算护栏。

具体缺口点名两处昂贵调用：①`skills/research-toolkit/protocols/subagent-search.md` 一次 `/竞品分析` 默认扇出 **8 个平台子代理**（Firecrawl 爬取、各社媒 MCP、WebSearch），每个都是高成本调用，且协议明文"**默认每次新建独立搜索任务，不读取旧任务**"——意味着同一产品两周内研究两次会**全量重爬**，无任何结果/语义缓存复用；②`skills/aibi-query/SKILL.md` 的 DBOPS `sqlQuery` 调用、表结构探查、`references/查询案例库.md`（11 个案例可作少样本复用）——同样无"相同查询走缓存"约定（值得注意：作业监督库本身有 `t_ai_context_cache` 表，是被研究业务方都在用缓存、而我们自己的 Agent 反而没有的反差）。本域要回答的就是：**在不自建 serving 的前提下，把"模型分级 + 级联 + 缓存复用 + 思考预算 + 预算护栏"沉淀成可被契约测试断言的文件化成本纪律。**

---

## SOTA 技术目录

> 共 70 条，按子类分组。列：技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源。
> 与域 3 的分工：域 3 讲路由"**怎么判**意图/语义/复杂度"，本域 A 组只取**成本-质量**视角（路由器作为省钱杠杆，不重复其分类机制）。

### A. 模型分级路由（成本-质量视角）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 强/弱二级路由（RouteLLM） | 偏好数据训练路由器，简单 query 走弱模型、难 query 走强模型，成本阈值控权衡 | 想省钱不降质、强弱二选一 | 成熟 | LMSYS/Berkeley RouteLLM（MT-Bench 省 85%@95% GPT-4 质量） | 〔web〕(域3已核) |
| 产品内置实时 router | 单入口内置 router 在 fast/thinking 档实时切换，用户无感 | 想"一个入口自动分快慢档" | 成熟 | OpenAI GPT‑5 router；Claude 自适应 thinking | 〔web〕(域3已核) |
| 网关 Auto Router | 网关分析提示自动选当前性价比最优模型，可限定候选池 | 多模型可选、想一键最优 | 成熟 | OpenRouter `openrouter/auto`（Not Diamond 驱动） | 〔web〕(域3已核) |
| 推荐层路由器（非代理） | 只给"该用哪个模型"的建议，<60ms，不接管流量 | 已有网关、只要选型建议 | 成熟 | Not Diamond（60+ 模型） | 〔web〕(域3已核) |
| 商用路由网关 | 以"模型可解释/性能预测"选模型，故障自动改投 | 企业级、要可靠性+成本 | 成熟 | Martian Model Router | 〔web〕(域3已核) |
| 多供应商动态路由（质量×成本×延迟） | 跨供应商按实时基准在质量/价格/延迟三维择优 | 多供应商、要按 SLA 选 | 成长 | Unify（unify.ai 路由器）(待核实其 2026 形态) | 〔知识〕 |
| 网关侧预算感知路由 | 路由前看各 provider 当期预算余额，超额跳过该 provider | 多 provider、要硬控成本 | 成熟 | LiteLLM `provider_budget_config`；Portkey | 〔web〕 |
| 云厂商托管 Model Router | 云平台内置路由（含质量/成本权衡），开箱即用 | 已在该云栈、不想自建 | 成长 | Azure AI Foundry Model Router（RouterArena 收录） | 〔web〕(域3已核) |
| 嵌入/小模型前置分级器 | 用 embedding/小编码器先判复杂度再选档，亚毫秒、成本低两数量级 | 高频、要省路由本身的钱 | 成熟 | semantic-router；ModernBERT+LoRA 信号层 | 〔web〕(域3已核) |
| 路由基准（成本可证伪） | Oracle/Zero 基线 + 商用vsOSS 横评，发现"商用路由器偏贵、OSS 常更具性价比" | 选型路由器、警惕为贵而贵 | 实验 | RouterBench(2403.12031)；RouterArena(2510.00202) | 〔web〕(域3已核) |

### B. 级联与置信度升级（Cascade / Confidence Escalation）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| FrugalGPT 级联 | 先调最便宜模型，质量打分器判不够再逐级升级，可串 3+ 个 API | 大量简单请求、阶梯式省钱 | 成长 | FrugalGPT（Chen 2023, arXiv 2305.05176；省 50–98%，或同价 +4% 准确） | 〔web〕 |
| 三类省钱策略框架 | prompt 适配（缩提示）+ LLM 近似（缓存/微调小模型）+ LLM 级联 | 系统性降本的总纲 | 成长 | FrugalGPT 三策略（TMLR 2024） | 〔web〕 |
| 校准式级联路由（calibration-first） | 把 token 边际不确定性经等渗回归校准成"错误概率"，再按约束成本最小化选阈值 | 想要"免每工作负载调阈值"的最优级联 | 实验 | UCCI（arXiv 2605.18796；生产 NER 省 31%@F1 0.91，胜 FrugalGPT 阈值法） | 〔web〕 |
| 置信度门控升级 | 弱模型答案置信/校验分低于阈值→升级强模型或转人工 | 要可控质量门 + HITL | 成长 | 通用 cascade；LangGraph 置信度路由 | 〔web〕(域3已核) |
| 生成-检验式升级（强验弱） | 弱模型先答、强模型/verifier 仅做校验，只在校验不过时重算 | 校验比生成便宜的任务 | 成长 | LLM-as-judge 把关 + 重试（对齐域9 verifier） | 〔知识〕 |
| 自一致性预算版（早停） | 多采样投票但按置信度提前停采，省掉冗余采样 | 推理任务想要 self-consistency 又怕贵 | 实验 | Adaptive/Early-Stopping Self-Consistency | 〔知识〕 |
| 难度预判路由（省检索/省算力） | 小 LM 先判 query 复杂度→选 无检索/单跳/多跳 或 弱/强模型 | 简单问题想省、难问题要够深 | 成长 | Adaptive-RAG（与域3/域5 协同） | 〔web〕(域3已核) |

### C. 缓存层一：Prompt / 前缀 KV 缓存（厂商侧，最高 ROI）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| OpenAI 自动 prompt caching | 提示 ≥1024 token 自动命中最长公共前缀，缓存输入约 5 折、无写入溢价、无需改代码 | 用 OpenAI 系、有稳定系统提示/长前缀 | 事实标准 | OpenAI Prompt Caching（省≈50%、延迟降≤80%，TTL 5–10min） | 〔web〕 |
| Anthropic 显式 cache_control | 手动标缓存断点（≤4 个，序 tools→system→messages），写入 1.25×(5min)/2.0×(1h)、读取 0.1×（省 90%） | 用 Claude、有大段静态前缀/工具定义 | 事实标准 | Anthropic Prompt Caching（读省 90%、延迟降 85%；break-even≈1.4 次读） | 〔web〕 |
| Gemini 显式上下文缓存 | 显式建缓存（≥32K token 起 + 按小时存储费），读取省约 75%，默认 TTL 1h 可调 | 超大且复用的上下文 | 成熟 | Gemini context caching（含隐式自动缓存） | 〔web〕 |
| DeepSeek 上下文（硬盘）缓存 | 前缀重复时自动命中，缓存读约 1 折（≈90% 折扣），无需配置 | 用 DeepSeek、重复前缀多 | 成熟 | DeepSeek context caching（自动前缀缓存） | 〔web〕 |
| 前缀稳定化纪律（cache-friendly 提示结构） | 把静态内容（系统提示/工具定义/案例库）放最前、变动内容放最后，最大化前缀命中 | 任何用前缀缓存的场景 | 成熟 | 通用最佳实践（"$720→$72"靠加 3 个 cache_control） | 〔web〕 |
| 缓存感知路由（cache-aware routing） | 网关/serving 把同前缀请求路由到持有该 KV 的实例，抬升命中率 | 多实例部署、要复用 KV | 成长 | vLLM/SGLang 路由器；Dynamo KV-aware routing | 〔web〕 |
| 缓存命中可观测 | 用 `cached_tokens`/`cache_read_input_tokens` 等字段监控命中率，低则查前缀漂移 | 想验证缓存真的省到钱 | 成熟 | OpenAI `prompt_tokens_details.cached_tokens`；Anthropic usage 字段 | 〔web〕 |

### D. 缓存层二：结果缓存（Exact / 确定性结果复用）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 精确结果缓存（key=输入哈希） | 用"模型+参数+完整提示"哈希做键存返回，完全相同请求直接返缓存、零生成 | 确定性、可复现的重复调用 | 成熟 | 通用 LLM cache；LangChain `InMemory/SQLite/RedisCache` | 〔知识〕 |
| 工具调用结果缓存（key=工具名+入参） | 按"工具名+规范化入参"缓存工具返回，带 TTL；同一抓取/查询窗口内复用 | 同参工具被反复调（抓取/查库/检索） | 成熟 | 通用 agent 工具缓存（工具角度见域4、记忆角度见域6） | 〔知识〕 |
| TTL / 失效策略 | 给缓存项设存活期与失效条件，平衡新鲜度与命中率（时效数据短 TTL、静态长 TTL） | 数据有时效、不能永久复用 | 成熟 | RedisVL `ttl`；GPTCache eviction（cachetools/Redis LRU） | 〔web〕 |
| 幂等键 / 请求去重 | 给副作用调用带 idempotency key，重复提交不重复执行/计费 | 重试、并发、网络抖动场景 | 成熟 | OpenAI/Stripe 式 idempotency key | 〔知识〕 |
| 任务级产物复用（读旧任务） | 开工先查同对象的历史产物（summary/data.csv）能否增量复用，而非全量重跑 | 同对象被多次研究/查询 | 成长 | 本仓库缺口（subagent-search 明文"不读旧任务"） | 〔知识〕 |

### E. 缓存层三：语义缓存（Semantic Cache，近似命中）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 嵌入相似度语义缓存 | 把 query 向量化，与历史问向量做相似度搜索，足够近就返历史答，跳过生成 | 换种说法的重复问多（研究显示 31% query 语义相似） | 成长 | GPTCache（zilliztech，集成 LangChain/LlamaIndex） | 〔web〕 |
| 托管语义缓存服务 | REST API + 自动嵌入的全托管语义缓存，免自建索引 | 不想自运维 Redis/向量库 | 成长 | Redis LangCache（private preview） | 〔web〕 |
| 库内语义缓存类 | 代码里 `check/store` 工作流，可设距离阈值、TTL、可过滤字段 | 自控 Redis、要与应用数据同库 | 成熟 | RedisVL `SemanticCache`（distance_threshold≈0.1，默认 HF 向量器） | 〔web〕 |
| 网关内置语义缓存 | LLM 网关把语义缓存做成开关，命中直接返、不计 LLM 费 | 用网关、想"一键开缓存" | 成长 | Portkey（purpose-built）；LiteLLM（Redis 基础版） | 〔web〕 |
| 类目感知阈值 + 兜底 | 不同意图设不同相似阈值，低于阈值不命中（防错答），命中加置信标注 | 防"似是而非"的错误命中 | 成长 | vLLM 类目感知语义缓存；GPTCache 阈值 | 〔web〕(域3已核) |
| 语义缓存风险纪律 | 显式列出"绝不可缓存"类（实时/个性化/带时间敏感结论），避免返回过期或张冠李戴 | 任何上语义缓存的系统 | 成长 | 通用最佳实践（hit 误判是语义缓存头号坑） | 〔知识〕 |

### F. 推理服务与系统优化（P2：仅"若未来自托管"参考）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| PagedAttention（分页 KV） | 像 OS 分页一样管理 KV 显存，消碎片、支持高并发，吞吐 14–24× | 自托管高并发推理 | 事实标准 | vLLM PagedAttention | 〔web〕 |
| 自动前缀缓存（APC） | 哈希前缀块 + LRU 淘汰，跨请求复用共享前缀的 KV；V1 默认开、近零开销 | 系统提示/few-shot 复用 | 事实标准 | vLLM V1（prefix caching 默认开） | 〔web〕 |
| RadixAttention（基数树 KV） | 用基数树做 token 级前缀复用（不受块对齐限制），前缀重场景吞吐至多 6.4× | 多轮/RAG/few-shot 高前缀重叠 | 成熟 | SGLang RadixAttention（H100 较 vLLM +29% 吞吐） | 〔web〕 |
| Continuous batching（连续批处理） | 请求级动态拼批、完成即出，不等整批，吞吐数倍于静态批 | 任何在线 serving | 事实标准 | vLLM/TGI/SGLang 等均内置 | 〔web〕 |
| Chunked prefill（分块预填） | 把长 prefill 切块与 decode 同批，平衡 TTFT 与 ITL | 长输入 + 在线低延迟 | 成熟 | vLLM V1（默认开，优先 decode） | 〔web〕 |
| Speculative decoding（投机解码） | 草稿模型/头先猜多 token，主模型并行校验，降 ITL（内存瓶颈下） | 中低 QPS、要低延迟 | 成熟 | vLLM 支持 EAGLE3/MTP/draft/ngram/suffix；Medusa | 〔web〕 |
| FP8 KV cache | KV 用 FP8 存，显存近半、可服务更长上下文/更多并发 | 显存吃紧、长上下文 | 成熟 | vLLM V1 FP8 KV（H100/Ada 原生） | 〔web〕 |
| 解耦式服务（disaggregated serving） | 把计算密集的 prefill 与访存密集的 decode 拆到不同 GPU 池，各自最优并行 | 数据中心级、长输入中等输出 | 成长 | NVIDIA Dynamo；TensorRT-LLM disagg；llm-d | 〔web〕 |
| KV 高速传输库（NIXL） | prefill→decode 的 KV 直接 GPU-GPU 非阻塞传输（NVLink/IB/UCX） | 解耦服务的 KV 搬运 | 成长 | NVIDIA NIXL（Dynamo 一部分，llm-d 复用） | 〔web〕 |
| KV-aware 智能路由 | 路由器按各 decode worker 持有的 KV 块决定去哪、能否跳过 prefill | 多 worker、要复用已算 KV | 成长 | Dynamo / TensorRT-LLM KV-aware routing | 〔web〕 |
| KV 缓存分层卸载 | 把冷 KV 从 GPU 卸到 CPU/NVMe，扩有效缓存容量 | 长会话/大上下文复用 | 成长 | Dynamo KV Cache Manager；LMCache | 〔web〕 |
| 高吞吐推理引擎（生态广） | 成熟开源 serving，硬件/模型覆盖广、生态大 | 多硬件（TPU/Trainium）/最大模型兼容 | 事实标准 | vLLM；HuggingFace TGI | 〔web〕 |
| 厂商极致优化引擎 | 编译期优化 + 自定义 kernel，单卡极限吞吐/延迟 | NVIDIA 硬件、要榨干性能 | 成熟 | NVIDIA TensorRT-LLM | 〔web〕 |

### G. 量化与部署成本意识（P2：仅 awareness，不落地）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| FP8 推理 | 权重/激活用 8 位浮点，吞吐↑显存↓，质量近无损（新硬件原生） | H100/Ada 上自托管 | 成熟 | TensorRT-LLM/vLLM FP8（H100 原生） | 〔知识〕 |
| INT8 量化 | 8 位整型权重，显存约半、广泛兼容 | 显存/成本敏感部署 | 成熟 | LLM.int8()/bitsandbytes；SmoothQuant | 〔知识〕 |
| AWQ（激活感知权重量化） | 按激活重要性保护关键权重做 4bit 量化，质量损失小 | 4bit 自托管要保质量 | 成熟 | AWQ（MIT，arXiv 2306.00978） | 〔知识〕 |
| GPTQ | 基于二阶信息的训练后 4bit 权重量化 | 离线把大模型压到单卡 | 成熟 | GPTQ（arXiv 2210.17323） | 〔知识〕 |
| GGUF / llama.cpp 量化 | CPU/边缘端友好的多档量化格式（Q4_K_M 等） | 本地/边缘/无 GPU 跑小模型 | 成熟 | llama.cpp / GGUF | 〔知识〕 |
| KV cache 量化 | 把 KV 缓存量化（FP8/INT8/INT4）省显存、扩上下文 | 长上下文显存瓶颈 | 成长 | KIVI；vLLM FP8 KV | 〔知识〕 |

### H. 思考预算 / 推理成本控制（最贵旋钮）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| reasoning_effort 档位（OpenAI） | `none/minimal/low/medium/high/(xhigh)` 控内部思考量；思考 token 按**输出价**计费 | GPT‑5 系，按任务难度选档 | 事实标准 | GPT‑5.1+ `reasoning_effort`（默认 medium；minimal 0–200 tok vs high 8K–32K+，成本差 30–80×） | 〔web〕 |
| budget_tokens / effort（Anthropic） | extended thinking 设思考 token 上限；Opus/Sonnet 4.6 起 `effort`(low/med/high/max) 取代之 | Claude，要硬上限或档位 | 成熟 | Claude extended thinking（须 `max_tokens > budget_tokens`） | 〔web〕 |
| thinkingBudget / thinkingLevel（Gemini） | 2.5 用数值 `thinkingBudget`(0=关/-1=动态/上限随变体)，3.x 用 `thinkingLevel`(minimal..high) | Gemini，要精细或枚举控思考 | 成熟 | Gemini 2.5 thinkingBudget / Gemini 3 thinkingLevel | 〔web〕 |
| "默认不要最高档"纪律 | 默认中/低档，仅难任务升 high；high 在简单任务上既贵又可能掉准 | 所有用推理模型的场景 | 成长 | 通用最佳实践（medium 已在付隐藏思考费） | 〔web〕 |
| 思考 token 预算与 max_tokens 协同 | 思考算进输出预算，须为可见答案多留几千 token，否则截断/空答 | 任何开思考的调用 | 成熟 | OpenAI/Anthropic 文档（"8000/8000"是最常见错误） | 〔web〕 |
| 动态/自适应思考（hybrid reasoning） | 模型按任务自行决定思考多少；可关可开 | 想"简单快答、难才深想" | 成长 | Claude adaptive thinking；Gemini dynamic(-1) | 〔web〕 |
| 推理换检索/工具（推理范式角度→域1） | 用 test-time compute 换质量属推理范式，本域只提醒其**成本**含义 | 见域1 | — | （cross-ref 域1） | 〔知识〕 |

### I. Token 经济 / FinOps / 预算护栏（observability vs enforcement）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 成本可观测（observability，只记录） | 记录每次调用的 token/成本/延迟，按模型/团队/标签归集，**但不能拒绝调用** | 想看清钱花哪了 | 成熟 | Langfuse；Helicone；OpenLLMetry（OTel cost，基建见域9） | 〔web〕 |
| 预算强制（enforcement，能拒绝） | 超预算时网关直接返回 **429**/停止，Redis 跨实例同步花费 | 要硬控、防跑飞 | 成熟 | LiteLLM `max_budget+budget_duration`（超额→429）；Portkey 治理 | 〔web〕 |
| 多并发预算窗口 | 同一 key 同时挂多个独立预算窗（如 $10/时 且 $500/月），各自计数重置 | 既防突刺又控月总 | 成长 | LiteLLM `budget_limits`（PR #24883，BudgetExceededError=429） | 〔web〕 |
| Agent 级循环熔断 | 给每会话设 `max_iterations` / `max_budget_per_session`，跑飞即断 | 防 Agent 死循环烧钱（头号事故源） | 成长 | LiteLLM Agent Gateway（per-session 上限） | 〔web〕 |
| Batch API（离线 5 折） | 异步 24h SLA 换 input+output **各 50%** 折扣，可与缓存叠加至省 ≈95% | 可等的批量活（评测/数据富化/夜间报告） | 成熟 | OpenAI Batch(50K/批)；Anthropic Message Batches(100K/批)；Bedrock batch | 〔web〕 |
| 错峰 / 自动缓存折扣 | 低价基座 + 自动前缀缓存（无 batch 也能省） | 用 DeepSeek 等低价模型 | 成长 | DeepSeek（自动上下文缓存 ≈90% 折扣） | 〔web〕 |
| 任务级成本预算（per-task budget） | 开工前按任务类型估"该花多少"，定上限与降级路径，跑超先停问 | 高扇出/长任务（如 8 子代理竞品分析） | 成长 | 本仓库缺口（agent-team-methodology 仅有原则） | 〔知识〕 |
| 上下文压缩省 token（→域6） | 压缩/隔离上下文降 token，是省钱手段但机制属上下文工程 | 见域6 | — | （cross-ref 域6 write/compress/isolate） | 〔知识〕 |
| 系统提示瘦身 / 渐进式披露 | 把"模型已知/用不上"的话删掉、细节下沉 references 按需加载 | 长系统提示/大 skill | 成熟 | 本仓库 `agent-team-methodology` 第二/四部分已有意识 | 〔知识〕 |

---

## 2025-2026 前沿与趋势

1. **路由成为基础设施默认能力，而非可选项**：GPT‑5 把 fast/thinking 实时 router 内置进单一入口；OpenRouter Auto、LiteLLM、Portkey、Cloudflare/Kong AI Gateway 等几乎每个生产网关都内置成本-质量路由。"简单走便宜、难走贵"已是默认形态。〔web〕
2. **prompt/前缀缓存是 2026 最高 ROI 的单点降本**：OpenAI 自动缓存省≈50%、Anthropic 显式缓存读取省 90% 且延迟降 85%、DeepSeek/Gemini 各有 90%/75% 折扣；有公开案例靠加 3 个 `cache_control` 把月账单从 $720 砍到 $72。研究称约 31% 的 LLM 查询与历史语义相似——无缓存即漏钱。〔web〕
3. **三层缓存 + Batch 可叠加到省 ≈95%**：前缀缓存（厂商侧）+ 结果/语义缓存（应用侧）+ Batch API（离线各 50%）可叠乘；Anthropic 明确"批量 + 缓存"对合格负载可降到标准价的约 5%。降本从"单点技巧"变成"可组合的纪律栈"。〔web〕
4. **思考预算是新出现的"最贵旋钮"**：推理 token 按输出价计费且不可见，GPT‑5.1 在 minimal 与 high 间成本差达 30–80×（单条难 query ≈$0.004 vs $0.18）。三家旋钮收敛为枚举档（OpenAI `reasoning_effort`、Gemini `thinkingLevel`、Anthropic `effort`），"默认不用最高档"成为显式成本纪律。〔web〕
5. **预算从"可观测"分化出"可强制"**：业界开始严格区分 observability（Langfuse/Helicone 只记录）与 enforcement（LiteLLM 超额返回 429、Portkey 治理）。跑飞的 Agent 循环被点名为头号成本事故源，催生 per-session `max_iterations`/`max_budget` 熔断。〔web〕
6. **级联从"学阈值"走向"先校准"**：FrugalGPT（省 50–98%）奠基后，2026 的 UCCI 指出"该工程化的是**校准**而非调阈值"——把 token 边际不确定性等渗校准成错误概率，在生产 NER 上省 31% 且胜过 FrugalGPT 式学习阈值。〔web〕
7. **token 级前缀复用（RadixAttention）成多轮/RAG 的最大杠杆**：SGLang 基数树做 token 级 KV 复用（不受块对齐限制），前缀重场景较 vLLM 吞吐至多 6.4×、整体 +29%；但高并发（>150）因 Python GIL 反被 vLLM 的 C++ PagedAttention 反超——选型要看流量形态。〔web〕
8. **解耦式服务（prefill/decode 分离）成为数据中心级新范式**：NVIDIA Dynamo / TensorRT-LLM / llm-d 把计算密集的 prefill 与访存密集的 decode 拆到不同 GPU 池，用 NIXL 做 GPU-GPU KV 直传 + KV-aware 路由，独立优化 TTFT/TPOT。对无自有 serving 的消费方是"了解即可"的 P2。〔web〕
9. **路由器选型进入"可基准、可证伪"阶段**：RouterBench/RouterArena 横评发现"商用路由器倾向选贵模型、OSS 路由器常更具性价比"——降本决策要用基准说话，警惕"为贵而贵"。〔web〕(域3已核)
10. **"读旧产物 + 缓存复用"被确立为 Agent 默认纪律**：FrugalGPT 把"缓存=零成本响应"列为级联三支柱之一；网关把语义缓存做成开关。与之对照，仍坚持"每次新建、不读旧任务"的全量重跑流程，在 2026 成本语境下已是明确反模式。〔web〕/〔知识〕

---

## 对标产品专家 Agent

> 现状定性：**Cursor 原生、无自有 serving、模型由 IDE 提供**；`agent-team-methodology` 第四部分有"模型分级/瘦身/隔离上下文"的**原则意识但零落地约定**；研究/SQL 两条最贵链路都**无缓存、无预算、无读旧产物**。下表"建议增强"中 **P0=可纯文件化的成本纪律（policy/protocol/rule，不依赖任何基建）**，P1=轻量脚本/约定，P2=需重 serving 基建（标交叉域）。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `agent-team-methodology.md` 第四部分有"模型分级路由：简单任务轻量模型/直接编辑，复杂才上重模型"一句原则 | 只有原则、**无决策表**：什么子任务算"简单"、对应哪档、子代理派发时怎么选档，全靠模型即兴 | **P0** 新建 `policies/model-tier-routing.md` 成本分级决策表：把研究内 5 类任务 / PRD 各章 / SQL 各步映射到 低/中/高 档与"是否开思考"，被方法论第四部分与 navigator 引用 |
| 全程 Cursor 单模型，无快/慢档显式约定，思考强度由 IDE 默认决定 | 简单子任务（关键词扩展、数据归一、平台 summary、配图提示）也可能在高思考档跑，贵且慢（high 比 minimal 贵 30–80×） | **P0** 思考预算档位纪律写进同一 policy：默认中/低档，仅"规划/事实核查裁决/跨源综合"升高档；点名"默认不用最高档" |
| `subagent-search.md` 明文"**默认每次新建独立搜索任务，不读取旧任务**"，一次 `/竞品分析` 扇出 8 平台子代理 | 同一产品两周内研究两次=**全量重爬**，8 条高成本链路零复用；无结果缓存、无语义缓存、无"读旧产物增量" | **P0** 改 `subagent-search.md` 加"复用门禁"：开工先查 `tasks/*/03-platforms/<platform>/` 是否有近期同对象产物，新鲜则增量补采而非重爬；**P1** 给平台抓取结果加 (平台+对象+日期) 结果缓存约定 |
| `aibi-query` DBOPS `sqlQuery`、表结构探查每次现查；`references/查询案例库.md` 有 11 案例 | 相同/相似查询每次重打 DBOPS；表结构(`information_schema`)反复探查；案例库未被当少样本/结果缓存复用 | **P1** `aibi-query` 加"查询复用"：相同 SQL 走会话内结果缓存、表结构探查结果缓存到 `~/.aibi/`；案例库作前缀稳定的少样本（吃 prompt 缓存） |
| 无任何任务级成本预算或循环熔断 | 高扇出/长任务（8 子代理、深度版看板）无"该花多少"上限，跑飞无人叫停（业界头号成本事故） | **P0** 新建 `policies/cost-budget-protocol.md`：按任务类型给"预估调用量/子代理数/最大轮次"软预算与降级路径，超限先停问；对应 `max_iterations` 思想（纯约定，无需网关） |
| 系统提示/skill 正文较长，但已有"节约上下文"意识（方法论第二部分） | 未对齐"prompt 缓存友好结构"：静态内容（命令路由/能力库/案例库）与变动内容混排，吃不满前缀缓存 | **P1** 提示结构纪律：把稳定的系统级内容前置、任务变量后置，最大化 IDE/模型侧前缀缓存命中（写进 prompt-engineering-techniques 或新 policy） |
| 无成本可观测：不知道一次任务花了多少调用/token | 无法回流优化，`/经验写回` 缺"哪步最贵"的数据 | **P2** 轻量成本日志：任务 `.meta/` 记每阶段调用次数/子代理数/大致 token 量级（observability，非 enforcement），反哺 `/经验写回`（基建对齐域9） |
| 无自托管 serving（vLLM/SGLang/量化/解耦/spec decode 全不适用） | — （当前不是差距，是定位） | **P2（仅若未来自托管）** 若未来要本地跑 router/embedding/rerank 小模型，再参考 F 组（vLLM APC / SGLang RadixAttention / FP8 / continuous batching）；现在**不引入** |
| 级联/置信度升级无约定 | 子代理派发未利用"先弱后强、强验弱"省钱；判断/裁决都用同一档 | **P1** 级联纪律入 `model-tier-routing.md`：采集/归一/分类用低档子代理产出，主代理用高档**仅做裁决/校验**（生成-检验式），对标 FrugalGPT/UCCI |

---

## 落地建议

> 每条给三要素：**放哪个文件 / 做什么 / 验收信号**（验收信号尽量可被 `tests/` 契约测试断言：文件存在 + 关键标记 + 触发词）。务实区分：**P0 = 纯文件化成本纪律（policy/protocol/rule，对单体 Agent 立刻可用、零基建）**；P1 = 轻量约定/脚本；P2 = 需重基建（标交叉域）。

### P0（可文件化的成本纪律，立刻可做）

1. **新建 `policies/cost-discipline-methodology.md`（成本纪律总纲）**
   - 做什么：定义四支柱——①**模型/思考分级**（任务→档位决策表）②**缓存复用三层**（前缀友好结构 / 结果缓存 / 读旧产物）③**任务级预算与降级**（预估上限 + 超限先停问）④**Batch/错峰意识**（可等的活走离线）。被 `agent-team-methodology.md` 第四部分"Token 优化"从"原则"升级引用为"落地约定"。
   - 验收：文件存在且含"模型分级决策表""缓存复用门禁""任务预算护栏""思考预算档位"四个二级标题；`agent-team-methodology.md` 第四部分有一句"落地约定见 `cost-discipline-methodology.md`"。

2. **新建 `policies/model-tier-routing.md`（模型/思考分级决策表）**
   - 做什么：一张表把本仓库具体子任务映射到 `低/中/高` 档 + `是否开思考` + `用子代理低档还是主代理高档`：归一/分类/关键词扩展/平台 summary/配图提示=低档不开思考；PRD 撰写/跨源综合=中档；任务规划/三轮事实核查裁决/竞争判断=高档。明确"默认不用最高思考档"。对标 GPT‑5 router / RouteLLM / FrugalGPT 级联思想。
   - 验收：表含 ≥10 行任务→档位映射；含触发词"默认中低档""仅裁决用高档"；`research-toolkit` 与 `agent-team-methodology` 子代理派发段各引用一次。

3. **改 `skills/research-toolkit/protocols/subagent-search.md`（加"复用门禁"，最高价值单点）**
   - 做什么：在"默认每次新建独立搜索任务"前增设**复用判定**：开工先扫 `tasks/*/03-platforms/<platform>/summary.md` 是否存在同对象、近 N 天的产物——新鲜则**增量补采**（只补缺口平台/新增证据），过期或不存在才全量扇出；把"全量重爬"从默认改为"显式选择"。
   - 验收：协议含"复用门禁/读旧产物"小节与触发词"增量补采""近 N 天"；契约测试断言文件含"复用"且不再是无条件"不读取旧任务"。

4. **新建 `policies/cost-budget-protocol.md`（任务级预算护栏，纯约定版）**
   - 做什么：按任务类型给"软预算"——`/竞品分析` 默认子代理数上限（如单批≤4、总≤8 且需理由）、`/SQL深度` 查询次数上限、长任务最大编排轮次；超限时**先停下汇报"已用 X、预算 Y、是否继续"**而非默默烧。把网关 `max_iterations`/`max_budget_per_session` 的思想降维成 Agent 自律约定。
   - 验收：文件含"子代理预算""最大轮次""超限先停问"三标记；`task-navigator.mdc` 引用一句"高扇出任务先看 `cost-budget-protocol.md`"。

5. **改 `.cursor/rules/task-navigator.mdc`（规划阶段加"成本预估"一步）**
   - 做什么：主动分阶段规划时，对高成本阶段（多平台扇出、深度看板、长链路）附一句"预估调用量/档位/是否可复用旧产物"，让用户在确认规划时即看到成本含义。
   - 验收：navigator 规划输出模板含"成本预估/可复用"字段；高扇出任务的规划里出现档位与复用判断。

### P1（轻量约定 / 脚本）

6. **`aibi-query` 加查询复用约定（改 `SKILL.md` + 可选 `scripts/`）**
   - 做什么：相同 SQL 走会话内结果缓存；表结构 `information_schema` 探查结果缓存到 `~/.aibi/schema-cache/`；把 `references/查询案例库.md` 作为**前缀稳定**的少样本固定前置（吃 IDE/模型前缀缓存）。
   - 验收：`SKILL.md` 含"查询/表结构缓存"小节与 TTL 说明；schema 缓存文件路径约定存在。

7. **结果缓存约定（写入 `cost-discipline-methodology.md` 或工具协议）**
   - 做什么：定义"按(工具名+规范化入参+日期窗)缓存工具返回"的通用键与 TTL 口径，供 Firecrawl/WebSearch/各社媒 MCP 抓取复用；明确"实时/个性化/带时效结论"不缓存。
   - 验收：含一张"可缓存 vs 不可缓存"清单 + 键设计示例。

8. **提示前缀稳定化纪律（写入 `policies/prompt-engineering-techniques.md`）**
   - 做什么：约定 system/能力库/案例库等稳定内容前置、任务变量后置，最大化前缀缓存命中；给一个"cache-friendly 提示骨架"示例。
   - 验收：该 policy 新增"前缀稳定化/缓存友好"条目与骨架示例。

9. **级联式子代理派发（写入 `model-tier-routing.md` + `agent-team-methodology` 第一部分）**
   - 做什么：把"扇出/扇入"细化为成本版——采集/归一/分类用**低档子代理**，主代理用**高档仅做裁决/校验**（生成-检验），对标 FrugalGPT/UCCI 的"先弱后强、强验弱"。
   - 验收：方法论"扇出/扇入"段出现"低档采集 + 高档裁决"的成本注脚。

### P2（需重基建 / 仅若未来自托管，标交叉域）

10. **成本可观测日志（轻量版，基建对齐域9）**
    - 做什么：任务 `.meta/cost-log.md` 记每阶段调用次数/子代理数/大致 token 量级（**observability，不做 enforcement**），积累后供 `/经验写回` 找"最贵的步"。完整 OTel GenAI 成本遥测属域9。
    - 验收：完成一个真实任务后 `.meta/` 出现 cost-log；`/经验写回` 能据此点名最贵阶段。

11. **自托管小模型 serving（仅若未来引入 router/embedding/rerank 本地化）**
    - 做什么：**当前不做**。若未来要本地跑路由/嵌入/重排小模型，再按 F 组选型：高前缀重用→SGLang RadixAttention；高并发唯一前缀→vLLM PagedAttention+APC；显存紧→FP8/AWQ；低延迟→speculative decoding。务必先用 RouterBench/RouterArena 式基准证伪"贵=好"。
    - 验收：（占位）`cost-discipline-methodology.md` 标注"自托管 serving 为 P2，触发条件=本地化小模型"，避免过早引入重依赖。

---

## 参考来源

> 〔web〕= 本轮（2026-06）WebSearch 核实；〔web〕(域3已核)= 路由器条目域3 已联网核实、本域复用其成本视角；〔知识〕= 训练知识、未逐条联网复核（仅用确有其物者，把握不准标"(待核实)"）。

**缓存（厂商侧 prompt/前缀）**
- OpenAI Prompt Caching（自动、≥1024 token、≈50% 折扣、无写入溢价）：https://openai.com/index/api-prompt-caching ；https://developers.openai.com/api/docs/guides/prompt-caching 〔web〕
- Anthropic Prompt Caching（cache_control、读省 90%、延迟降 85%、写 1.25×/2.0×）：综述见 https://www.prompthub.us/blog/prompt-caching-with-openai-anthropic-and-google-models ；https://www.finout.io/blog/anthropic-api-pricing 〔web〕
- Gemini context caching（≥32K、读省≈75%、按小时存储费、含隐式缓存）：同 prompthub 对比表 〔web〕
- DeepSeek context caching（自动前缀、读≈90% 折扣）：https://apiscout.dev/guides/deepseek-api-vs-openai-vs-claude-2026 〔web〕
- "三层缓存 + Batch 叠加省 95%"与 "$720→$72" 案例、31% 查询语义相似：https://usagebox.com/articles/prompt-caching-cost-optimization-claude-gpt-gemini-2026 ；https://introl.com/blog/prompt-caching-infrastructure-llm-cost-latency-reduction-guide-2025 〔web〕

**语义 / 结果缓存**
- GPTCache（zilliztech，语义缓存，集成 LangChain/LlamaIndex）：https://github.com/zilliztech/gptcache ；https://gptcache.readthedocs.io 〔web〕
- Redis LangCache（全托管语义缓存，REST + 自动嵌入，private preview）：https://redis.io/docs/latest/develop/ai/langcache/ 〔web〕
- RedisVL `SemanticCache` / `LangCacheSemanticCache`（distance_threshold、TTL）：https://redis.io/docs/latest/develop/ai/redisvl/api/cache/ 〔web〕

**级联 / 成本-质量路由**
- FrugalGPT（prompt 适配 + 近似 + 级联，省 50–98%）：arXiv 2305.05176 ；TMLR 2024 PDF https://lingjiaochen.com/papers/2024_FrugalGPT_TMLR.pdf 〔web〕
- UCCI（校准式级联路由，生产 NER 省 31%@F1 0.91，胜 FrugalGPT 阈值法）：arXiv 2605.18796 https://arxiv.org/html/2605.18796 〔web〕
- nexos.ai FrugalGPT 解读（缓存=零成本响应、级联升级）：https://nexos.ai/blog/frugal-gpt/ 〔web〕
- RouteLLM / GPT‑5 router / OpenRouter Auto / Not Diamond / Martian / Azure Model Router / RouterBench(2403.12031) / RouterArena(2510.00202)：详见 `findings/03-intent-routing.md` 参考来源 〔web〕(域3已核)
- Unify（unify.ai 多供应商质量×成本×延迟路由）：unify.ai （2026 形态待核实）〔知识〕

**推理服务与系统优化（P2）**
- vLLM V1（APC 默认开、chunked prefill、spec decode、FP8 KV、PagedAttention 14–24×）：https://docs.vllm.ai/en/stable/usage/v1_guide.html ；https://blog.vllm.ai/2025/01/27/v1-alpha-release.html ；spec decode https://docs.vllm.ai/en/latest/features/speculative_decoding/ 〔web〕
- SGLang RadixAttention（token 级前缀复用、H100 +29%、前缀重至多 6.4×；高并发 GIL 限制）：https://turion.ai/blog/vllm-vs-sglang-inference-comparison-2026/ ；https://particula.tech/blog/sglang-vs-vllm-inference-engine-comparison 〔web〕
- NVIDIA Dynamo 解耦式服务 + NIXL（prefill/decode 分离、KV-aware 路由、KV Cache Manager）：https://docs.nvidia.com/dynamo/dev/design-docs/disaggregated-serving 〔web〕
- TensorRT-LLM disaggregated serving（trtllm-serve、SLA planner）：https://nvidia.github.io/TensorRT-LLM/1.2.0rc4/features/disagg-serving.html 〔web〕
- llm-d（K8s 原生分布式推理，复用 NIXL，vLLM 调度）：https://developer.nvidia.com/blog/nvidia-dynamo-accelerates-llm-d-community-initiatives-for-advancing-large-scale-distributed-inference/ 〔web〕
- HuggingFace TGI（连续批处理、生态广）〔知识〕

**量化（P2 awareness）**
- AWQ（arXiv 2306.00978）、GPTQ（arXiv 2210.17323）、LLM.int8()/bitsandbytes、SmoothQuant、GGUF/llama.cpp、KIVI（KV 量化）〔知识〕

**思考预算 / 推理成本**
- reasoning_effort（GPT‑5.1+ none/minimal/low/medium/high/xhigh；按输出价计费；minimal vs high 成本差 30–80×）：https://chatgptaihub.com/why-reasoning-effort-matters-tuning-gpt-5-1-reasoning-effort-for-cost-vs-quality/ ；https://www.grube.ai/thinking-in-llms 〔web〕
- Anthropic extended thinking `budget_tokens`/`effort`、Gemini `thinkingBudget`/`thinkingLevel`、`max_tokens>budget_tokens` 纪律：https://qubittool.com/blog/hybrid-reasoning-model-thinking-mode ；https://dev.to/gabrielanhaia/reasoning-effort-low-medium-high-when-each-setting-actually-pays-off-36cp 〔web〕

**FinOps / 预算护栏 / Batch**
- LiteLLM 预算 enforcement（max_budget+budget_duration→429、provider_budget_config、Redis 同步、Agent Gateway per-session 上限）：https://docs.litellm.ai/docs/proxy/users ；https://docs.litellm.ai/docs/proxy/provider_budget_routing 〔web〕
- LiteLLM 多并发预算窗口（BudgetExceededError=429）：PR #24883 https://github.com/BerriAI/litellm/pull/24883 〔web〕
- Portkey vs LiteLLM vs OpenRouter 网关对比（语义缓存/预算/可观测）：https://www.pkgpulse.com/guides/portkey-vs-litellm-vs-openrouter-llm-gateway-2026 ；2026 网关横评 https://www.getmaxim.ai/articles/top-5-ai-gateways-for-optimizing-llm-cost-in-2026/ 〔web〕
- Batch API 50%（OpenAI 50K/批、Anthropic Message Batches 100K/批、Bedrock；与缓存叠加省≈95%）：https://llmcfo.com/research/batch-api-routing ；https://tokenmix.ai/blog/ai-api-webhooks-async 〔web〕
- 成本可观测（observability）Langfuse / Helicone / OpenLLMetry：基建详见 `findings/09-eval-observability.md` 〔知识〕

**本仓库交叉引用**
- `policies/agent-team-methodology.md` 第四部分"Token 优化"（模型分级/瘦身/隔离上下文原则）
- `skills/research-toolkit/protocols/subagent-search.md`（8 平台扇出 + "不读旧任务"全量重爬）
- `skills/aibi-query/SKILL.md`（DBOPS sqlQuery、查询案例库、`t_ai_context_cache` 表反差）
- 域 1（推理范式/test-time compute 成本含义）、域 3（路由意图/语义机制）、域 4（工具结果缓存接口）、域 6（上下文压缩省 token）、域 9（成本遥测/OTel GenAI 基建）

