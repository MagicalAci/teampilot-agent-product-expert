# 域 3：意图识别与路由（Intent Recognition & Routing）

> 子代理：intent-routing｜回写：`findings/03-intent-routing.md`
> 标注规范：〔web〕= 本次 WebSearch/WebFetch 核实；〔知识〕= 既有领域知识（未逐条联网验证，但属业内共识）。
> 成熟度口径：`生产成熟` / `成长期` / `前沿研究` / `实验性`。

## 领域概述

"路由"是 Agent 拿到一条输入后、在生成前做出的**一次或多次离散决策**：这条请求属于哪个意图/任务类型？该交给哪个能力、哪个数据源、哪个模型、哪个子代理？还是该先反问澄清、或直接拒答转人工？2024-2026 年这一层已从"关键词/命令硬匹配"演进为四条并行技术线：**意图分类**（LLM/小编码器/嵌入/零样本）、**语义路由**（嵌入原型 + 阈值兜底，如 semantic-router）、**模型分级路由**（RouteLLM、GPT‑5 实时 router、OpenRouter Auto、Not Diamond、Martian，按成本-质量/复杂度/置信度选模型）、**任务·查询路由**（Agent handoff/triage、LangGraph supervisor、RAG 的 RouterQueryEngine/self-query/Adaptive-RAG）。同时配套两类"软"机制日趋成熟：**澄清/反问**（从提示技巧走向 EVPI/信息增益的"该问还是该做"决策）与**护栏式路由**（超范围拒答、低置信降级、转人工）。核心共识：路由要可分类、可设阈值兜底、可观测可评测——"无匹配返回 None → 走兜底"比"勉强猜一个"更安全。〔web〕

## SOTA 技术目录

> 共 45 条，按子类分组。列：技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源。

### A. 意图分类（Intent Classification）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| LLM 提示分类（零/少样本 + reasoning+intent） | LLM（可零/少样本）输出 `<reasoning><intent>`，正则取标签分派；冷启动即用 | 类目 5-30、无标注、类目快变、要可解释 | 生产成熟 | Anthropic Ticket Routing；GPT/Claude/Qwen2.5（零样本可超 BERT-base） | 〔web〕 |
| 结构化输出 + enum schema | 约束 LLM 只能输出枚举意图，杜绝解析漂移 | 要稳定可解析、低工程成本 | 生产成熟 | OpenAI/Anthropic structured outputs | 〔web〕 |
| 微调小编码器（DeBERTa-v3/BERT） | 编码器+分类头微调，亚毫秒延迟、成本低两个数量级 | 高 QPS(>50/s)、严延迟(<10ms)、有标注 | 生产成熟 | DeBERTa-v3、BERT；BANKING77 基准 | 〔web〕 |
| 嵌入最近邻分类 | query 向量与"意图描述向量"比相似度取最近 | 廉价粗分意图、做昂贵分类的前置一跳 | 生产成熟 | 任意 embedding（OpenAI/BGE/FastEmbed） | 〔web〕 |
| 检索增强提示分类（RAG few-shot） | 检索最相似示例进提示，按"由远到近"排序降近因偏差 | 细粒度/语义相近类目、数据稀缺 | 成长期 | RAG-prompting on BANKING77（GPT-4o 可超编码器） | 〔web〕 |
| 复杂度分类器（Adaptive-RAG 式） | 小 LM 预测查询复杂度→选检索强度，标签自动采集 | 想按难度分级处理，省算力 | 前沿研究 | starsuzi/Adaptive-RAG | 〔web〕 |

### B. 语义路由（Semantic Routing）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| 嵌入原型路由（semantic-router） | 每路由配若干例句→向量空间最近匹配，绕开慢 LLM；支持全本地 encoder | "模糊 if/else"、毫秒级意图/工具决策、隐私/离线 | 生产成熟 | aurelio-labs/semantic-router（v0.1.12, MIT；本地 Mistral-7B 可超 GPT-3.5） | 〔web〕 |
| 相似度阈值 + None 兜底 | 低于阈值不强匹配，返回 `None` 触发兜底/澄清 | 要拒绝误路由、设计 fallback/passthrough | 生产成熟 | semantic-router `RouteChoice(name=None)` | 〔web〕 |
| 混合路由（密集+稀疏） | 嵌入语义 + 关键词稀疏向量融合，兼顾泛化与精确词 | 含专有名词/术语、纯语义易漏 | 成长期 | semantic-router `HybridRouter` | 〔web〕 |
| 动态路由（function schema 取参） | 命中路由后用 LLM 抽取结构化参数再调函数 | 路由后需带参执行（如平台+关键词） | 成长期 | semantic-router dynamic routes | 〔web〕 |
| 多路由召回（multi-route） | 一次返回多个命中路由+分数，支持多意图 | 一句话含多意图/需并行能力 | 成长期 | semantic-router `retrieve_multiple_routes` | 〔web〕 |

### C. 模型分级路由（Model-tier / Cost-Quality Routing）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| RouteLLM（偏好数据训练） | 强/弱双模型间按 query 路由，成本阈值控权衡；可迁移 | 想省钱不降质、二选一强弱模型 | 生产成熟 | LMSYS/Berkeley RouteLLM（MF/BERT/causal；MT-Bench 省 85%@95% GPT-4） | 〔web〕 |
| GPT‑5 实时 router | 系统内置 router 在 fast(main) 与 thinking 间实时切换，按类型/复杂度/工具需求/显式意图 | "一个入口自动分快慢档"的产品级范式 | 生产成熟 | OpenAI GPT‑5（2025-08，real-signal 持续训练） | 〔web〕 |
| OpenRouter Auto Router | `openrouter/auto` 分析提示自动选优模型，可用 plugins 限定候选 | 不知用户会发什么、想一键最优 | 生产成熟 | OpenRouter（由 Not Diamond 驱动；候选含 Claude4.5/GPT‑5.1/Gemini3.1/DeepSeek3.2） | 〔web〕 |
| Not Diamond | 推荐层（非代理），<60ms 决策，预训练+自训路由，含提示优化 | 已有网关、只想要"选哪个模型"的建议 | 生产成熟 | Not Diamond（60+ 模型，10万次/月免费） | 〔web〕 |
| Martian Model Router | 首个商用模型路由网关，靠"模型可解释/映射"预测表现，故障自动改投 | 企业级网关、要可靠性+成本 | 生产成熟 | Martian（Accenture 战略投资） | 〔web〕 |
| 级联 Cascade / FrugalGPT | 先调便宜模型，质量/置信不足再逐级升级 | 大量简单请求、想阶梯式省钱 | 成长期 | FrugalGPT（Chen et al. 2023）；通用 cascade | 〔知识〕 |
| 置信度/不确定性路由 | 按分类器或答案置信度分流：低→重试/转人工，中→人审，高→直行 | 要可控质量门、HITL 升级 | 成长期 | LangGraph 编排（conf≤0.69 重规划/≤0.89 人审） | 〔web〕 |
| 信号驱动路由（vLLM Semantic Router） | ModernBERT/mmBERT LoRA 抽 域/意图/模态/安全/事实 信号，用布尔 DSL 组策略 | Mixture-of-Models 多模型部署、可声明式改策略 | 成长期 | vLLM Semantic Router v0.1 "Iris"（2026-01；MoM 模型族） | 〔web〕 |
| 学术路由器谱系 | GNN(GraphRouter)/K-means(Universal)/对比学习(RouterDC)/项目反应理论(IRT-Router)/成本-准确(CARROT) | 研究/自建高级路由器选型参考 | 前沿研究 | RouterArena 收录的 9 类 OSS 路由器 | 〔web〕 |
| 路由基准（RouterBench/RouterArena） | RouterBench 立 Oracle/Zero 基线免推理评测；RouterArena 统一横评商用+OSS（含 Azure Model Router 等），发现商用路由器偏贵、OSS 常更具性价比 | 评测/选型路由器、警惕"为贵而贵" | 前沿研究 | RouterBench(arXiv 2403.12031)；RouterArena(arXiv 2510.00202) | 〔web〕 |

### D. 查询路由 / RAG 路由（Query / Retrieval Routing）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| RouterQueryEngine / RouterRetriever | selector 把查询路由到合适的查询引擎/索引（单选或多选） | 多索引/多数据源、要按问题选源 | 生产成熟 | LlamaIndex（LLM/Pydantic Single/Multi Selector） | 〔web〕 |
| 检索增强路由（选项过多时） | 路由候选本身很多时，先索引候选再检索匹配 | 工具/数据源成百上千 | 成长期 | LlamaIndex `ToolRetrieverRouterQueryEngine`（beta） | 〔web〕 |
| Self-query / metadata 路由 | LLM 从自然语言推断"元数据过滤条件 + 查询串"再查库 | 带结构化属性的库（品类/时间/价格） | 生产成熟 | LangChain SelfQueryRetriever；LlamaIndex VectorIndexAutoRetriever | 〔web〕 |
| Adaptive-RAG（按复杂度路由） | 分类器把问题路由到 无检索/单跳/多跳迭代 三档 | 简单问题想省、多跳问题要够深 | 成长期 | Adaptive-RAG + LangGraph `RouteQuery` | 〔web〕 |
| Self-RAG / CRAG（自反思纠错路由） | 给检索/答案打分，按分路由到 重写/再检索/转网搜 | 要自我纠错、降幻觉 | 成长期 | Self-RAG、CRAG（LangGraph 实现） | 〔web〕 |
| 多源路由（route-to-source） | 在 本地向量库 / 网搜 / 直接 LLM 参数知识 间择源 | 既有内部知识又需时效信息 | 生产成熟 | LangGraph Adaptive RAG `route_question` | 〔web〕 |

### E. 任务路由 / Triage（Task Routing / Handoff）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| Anthropic Routing workflow | 先分类再导向专门化后续任务，关注点分离、各用专属提示 | 类目清晰、分开处理更好 | 生产成熟 | Anthropic《Building Effective Agents》 | 〔web〕 |
| Agent handoff / triage（vs agents-as-tools） | triage agent 把 handoff 当工具移交控制权给专家；或用 as_tool 让经理保留所有权汇总 | 专家"接管"对话 vs 经理汇总 | 生产成熟 | OpenAI Agents SDK `handoff()`（input_type 元数据、on_handoff 记日志） | 〔web〕 |
| Supervisor + Command 动态路由 | supervisor LLM 出结构化决策→`Command(goto,update)` 同时改状态并路由 | 分支取决于刚学到的信息、需带上下文 | 生产成熟 | LangGraph（现推荐手写 tool-based supervisor） | 〔web〕 |
| Agent swarm（点对点 handoff） | 无中心协调，任一 agent 用 `Command(goto=peer)` 交棒 | 职责边界清晰、要直接协商 | 成长期 | LangGraph swarm | 〔web〕 |
| 技能/工具路由 | 用语义路由/分类把请求映射到技能或工具，规模可达数千 | 工具/技能多、塞进上下文太贵 | 成长期 | semantic-router 工具路由；vLLM `mom-toolcall-sentinel` | 〔web〕 |

### F. 多意图 / 意图漂移（Multi-intent & Intent Drift）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| 多意图检测（MIDLM） | 双向 LLM 先测"意图个数"再做多标签选择 | 一句话含多个意图 | 前沿研究 | MIDLM（COLING 2025） | 〔web〕 |
| 意图漂移检测（DeepContext） | 有状态 RNN 跨轮聚合 turn 嵌入，捕捉意图随轮次的轨迹漂移 | 多轮里目标渐变/对抗性诱导 | 前沿研究 | DeepContext（arXiv 2602.16935） | 〔web〕 |
| 对话路由 STAY/BRANCH/ROUTE | LLM 判定话题是否转移→留在/新建/回到分支，保上下文聚焦 | 长对话话题跳变、上下文窗口要瘦身 | 实验性 | DriftOS/driftos-core | 〔web〕 |
| 漂移雷达（基线 vs 当前意图） | 在时间序信号上判"原始目标是否悄悄偏移"并给证据+置信 | 长周期任务防目标偏离 | 实验性 | Intent Drift Radar（Gemini 3 集成投票） | 〔web〕 |

### G. 澄清 / 反问（Clarification & Ambiguity）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| 澄清代理（Clarifying Agent） | 检出歧义/欠规约→发针对性追问，直到信息足够或追问无增益 | 输入模糊、缺关键槽位 | 成长期 | Clarifying Agent 范式（Andukuri 2024 等） | 〔web〕 |
| 不确定性引导澄清（EVPI/EIG） | 用"完美信息期望值/期望信息增益"算该问哪条、何时停 | 想避免过度/不足追问 | 前沿研究 | Structured Uncertainty(arXiv 2511.08798)、Info-Gain(2606.03135) | 〔web〕 |
| 主动信息收集（RFT 奖励） | 强化微调奖励"能挖出隐性需求"的提问，从被动答到主动问 | 复杂开放任务、隐性专家知识 | 前沿研究 | Proactive Info Gathering（EMNLP 2025；Qwen-7B 超 o3-mini 18%） | 〔web〕 |
| 未来轮次建模（double-turn） | 用"未来一轮的价值"训练"该问还是该答"的判断 | 训练模型判断何时澄清 | 前沿研究 | Modeling Future Turns（ICLR 2025） | 〔web〕 |

### H. 护栏式路由（Guardrail Routing）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表框架/产品 | 来源 |
|---|---|---|---|---|---|
| 话题护栏/超范围拒答 | 专用模型判 on/off-topic，跑题→礼貌拒答并引导回域内 | 限定业务边界、防被带偏 | 生产成熟 | NeMo Guardrails topical rails（Llama-3.1 NemoGuard 8B TopicControl） | 〔web〕 |
| 转人工升级（escalation） | 检测受挫/显式请求/KB 置信低→执行 `escalate_to_human` | 答不了/高风险/用户要真人 | 生产成熟 | NeMo Guardrails escalation flow | 〔web〕 |
| 事实置信降级路由 | KB 校验分数低于阈值→不强答，转专家/加免责声明 | 关键事实没把握 | 成长期 | NeMo `verify_against_kb`<0.5 → escalate | 〔web〕 |
| 安全分类路由（越狱/PII） | 越狱/PII 分类器命中→中止或脱敏，作为路由前置闸 | 任何对外/敏感数据场景 | 生产成熟 | vLLM `mom-jailbreak/pii`；NeMo jailbreak detection | 〔web〕 |
| 语义缓存短路 | 命中相似历史问→直接返缓存，跳过生成（按类目设阈值/TTL） | 重复/相似请求多、要降本提速 | 成长期 | GPTCache；vLLM 类目感知语义缓存 | 〔知识〕/〔web〕 |

## 2025-2026 前沿与趋势

1. **"路由即产品默认形态"**：GPT‑5 把 fast/thinking 的实时 router 内置进单一入口，并用"用户切换模型/偏好率/正确性"等真实信号**持续在线训练**路由器——路由从工程技巧变成模型产品的一等公民。〔web〕
2. **编码器小模型回归做"信号层"**：ModernBERT/mmBERT（8K-32K 上下文、RoPE、FlashAttn2、~150-300M 参数）+ LoRA 适配器，成为意图/域/安全分类的性价比首选；vLLM Semantic Router 的 MoM 模型族把"域分类/工具选择/PII/幻觉/反馈"全部做成专用小分类器。〔web〕
3. **成本-质量路由进入"可基准、可证伪"阶段**：RouterBench 给出 Oracle/Zero 基线，RouterArena(2025-10) 横评后指出**商用路由器倾向选贵模型、OSS 路由器常更具性价比**——选型要用基准说话，别迷信品牌。〔web〕
4. **澄清从"提示技巧"升级为"决策理论"**：EVPI（完美信息期望值）、EIG（期望信息增益）、双轮偏好、RFT 奖励，把"该问还是该做、问哪一条、何时停"形式化为可优化目标；在工具调用场景对**工具参数空间**显式建模不确定性，避免幻觉补参。〔web〕
5. **意图漂移成为独立问题**：长会话/长周期任务中"目标悄悄偏移"被单列研究——有状态 RNN(DeepContext)、STAY/BRANCH/ROUTE 对话路由(DriftOS)、基线-当前对比(Intent Drift Radar)，兼用于"上下文瘦身"与"对抗性越狱防护"。〔web〕
6. **混合路由（规则+语义+模型）成主流工程实践**：fusion routing = 关键词 + 嵌入相似度 + BERT 分类多信号融合，按查询复杂度自适应延迟；纯关键词或纯 LLM 都在被"分层兜底"取代。〔web〕
7. **handoff/triage 工程化收敛**：业界共识"先单 agent、契约变了再拆专家"、"handoff 目标 ≤5、超过做两级 triage"、"用 on_handoff 回调记录每次路由"——可观测性被写进最佳实践。〔web〕
8. **RAG 路由从静态管线转向 Agentic**：Adaptive/Self/CRAG 用"复杂度分类 + 自反思打分"动态决定 是否检索/检索几跳/转网搜/重写，路由与检索深度联动。〔web〕
9. **路由的可观测与在线学习闭环**：路由决策（intent/置信度/命中能力/是否澄清）被当作可记录、可回归、可反哺训练的一等数据——与评估·可观测域(09)、运维成本域(12)强耦合。〔web〕

## 对标产品专家 Agent

> 现状：纯**命令路由 + 关键词硬匹配 + task-navigator 隐式能力匹配 + research-toolkit Phase 0 任务类型判定 / 平台子代理扇出**，无语义路由、无模型分级、无显式置信度与澄清门禁、无运行时护栏路由。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `product-expert-commands.mdc` 斜杠命令→skill（确定、可枚举） | 命令本身没问题，但仅覆盖"用户已知命令名"的场景 | **保留**为第一层精确路由；在其上叠加语义层（P0） |
| 自然语言触发靠枚举短语（"帮我调研下""跑个数"）+ skill `triggers:` 关键词 | 无语义泛化：换种说法/近义/夹带就漏；无相似度分数、无兜底 | **P0** 加嵌入语义路由层做"模糊 if/else"：5 能力各配例句库，命中分数<阈值→澄清，匹配不到→不硬猜 |
| task-navigator 做能力匹配+分阶段规划+先建议再问 | 纯模型隐式判断：不可观测、不可评测、无置信度、无明确兜底 | **P0** 路由 protocol：每轮先输出 `reasoning/intent/confidence`，低置信→澄清或回退 navigator；**P1** 把"能力库+组合模式"做成显式路由表+例句库可被回归测试 |
| 澄清只有"Phase 0 需求澄清"提示 + navigator"先给建议" | 无歧义检测、无"该问还是该做"门禁；欠规约请求易直接开跑 | **P0** 澄清门禁（ask-or-act）：仅当关键槽位（产品名/目标/范围/库）缺失才一次性问全，借鉴 EVPI/信息增益思想 |
| 全程 Cursor 单模型，无快/慢、强/弱分档 | 无模型分级路由：简单子任务也用强模型，贵且慢；不会按复杂度开/关 reasoning | **P1** 模型分级策略入 policy：分类/归一/关键词扩展/配图提示走快档（或子代理低档模型），规划/PRD/事实核查裁决走强档；对标 GPT‑5 router / RouteLLM |
| 5 能力外的请求无显式护栏（仅 SQL 无库时口头提醒） | 跑题/越界/超范围无统一拒答与边界说明，无转人工降级 | **P1** 护栏式路由：判定是否属 5 能力，否则礼貌说明边界+给替代建议；低置信/无证据→降级表达或转人工 |
| research-toolkit Phase 0 判 5 种任务类型 + 平台一子代理扇出 | 属"专家池"雏形，但仍隐式；无多意图分解、无跨轮意图漂移检测 | **P1** 多意图路由（命中多能力→输出 pipeline 计划，对应"调研→PRD→Demo"组合）；**P2** 轻量漂移检测：每轮重判 intent，与锁定 task type 不符→提示切换/新任务隔离 |
| `knowledge/` 与 aibi 三库选择靠模型即兴 | 无 self-query/metadata 路由、无多源 route-to-source | **P2** 引入 self-query/metadata 路由用于知识库与多数据库选择（与 RAG 域 05 协同） |
| 无路由日志 | 不知道路由准不准，无法回流改进 | **P2** 路由可观测：每次路由记一行（intent/置信度/能力/是否澄清）入 `.meta/` 或 `PROCESS_LOG.md`，反哺 `/经验写回` |

## 落地建议

> 每条给：放哪个文件 · 做什么 · 验收信号。遵循"先方法论文档 + .cursor 规则，可选再做嵌入路由 skill"的渐进式增强，避免一上来就引重依赖。

1. **新建 `policies/intent-routing-methodology.md`（路由方法论总纲，P0）**
   - 做什么：定义**三层路由**——① 命令精确路由（现有）→ ② 语义/分类路由（例句库+阈值）→ ③ 兜底（低置信澄清 / 超范围护栏）；写明置信度档位、澄清触发条件、模型分级原则、护栏边界。被 `task-navigator.mdc` 与 `product-expert-commands.mdc` 引用。
   - 验收：文档含一张"路由决策表"（输入特征→目标能力/动作）；navigator 与 commands 规则各有一句"路由判定依据见此文件"。

2. **新建 `.cursor/rules/intent-router.mdc`（运行时路由规则，P0）**
   - 做什么：规定每轮先做意图判定，结构化输出 `reasoning / intent / confidence / 是否需澄清 / 是否超范围`；置信低→走澄清门禁；超出 5 能力→边界说明+替代建议；命中多意图→产出组合 pipeline 提案。`alwaysApply:false`、由产品专家任务上下文触发。
   - 验收：用 20 条混淆/换说法/复合/越界 query 自测，路由正确率较关键词基线显著上升；越界 query（如"帮我订机票"）稳定走护栏拒答。

3. **新建 `policies/capability-utterances.yaml`（能力例句库，P0）**
   - 做什么：5 能力（调研/产品策划/AI策划/Demo/SQL）各 10-15 条正例 utterances + 若干负例/易混例；研究内部 5 种任务类型各 6-10 条。同一份既供语义路由消费，也供回归测试。
   - 验收：文件可被语义路由 skill 与契约测试同时加载；每能力≥10 正例、≥3 负例。

4. **可选新建 skill `skills/semantic-intent-router/`（嵌入语义路由，P1）**
   - 做什么：基于 `aurelio-labs/semantic-router` + 本地/OpenAI encoder，从 `capability-utterances.yaml` 构建 routes；`scripts/route.py "<query>"` 返回 `RouteChoice(name, score)`；分数<阈值返回 `None`→上层澄清；库/Key 不可用时**降级**为纯 LLM 提示分类（保持 Why-First + 渐进式披露，参照 `agent-team-methodology.md`）。
   - 验收：`route.py "帮我看看豆包爱学怎么样"` → `research-toolkit`(score 高)；`route.py "今天天气"` → `None`（触发护栏）；降级路径在无依赖时仍可运行。

5. **新建 `policies/model-tier-routing.md`（模型分级策略，P1）**
   - 做什么：明确"何时用快/低档（关键词扩展、数据归一、平台 summary、分类、配图提示词）vs 强/高档（任务规划、PRD 撰写、事实核查裁决、跨源综合）vs 子代理并行档"；落到子代理派发时按任务复杂度选 model 与是否开 reasoning。对标 GPT‑5 router / RouteLLM / OpenRouter Auto 的成本-质量思想。
   - 验收：`agent-team-methodology.md` 的子代理派发段落引用本策略；研究子代理扇出时按平台任务难度选档有据可依。

6. **强化澄清门禁（改 `task-navigator.mdc` + research-toolkit Phase 0，P0）**
   - 做什么：把"先给建议再问"升级为 **ask-or-act 门禁**——列出每能力的"关键槽位"，仅当槽位缺失才追问，且**一次性问全**（避免挤牙膏）；槽位齐备则直接给规划/开跑。引用 EVPI/信息增益作为"问的价值>打断成本才问"的判据。
   - 验收：欠规约请求（如"做个 demo"无主题）触发**一次**集中追问而非反复来回；槽位齐备请求不再无谓追问。

7. **护栏 + 转人工统一化（写入 `intent-router.mdc` + 复用 `policies/agent-security-scan.md` 边界，P1）**
   - 做什么：统一"超出 5 能力→说明能力边界+建议外部途径"；研究/SQL 命中无部署库时的提醒并入同一护栏模板；高风险/低置信/无证据→降级表达或建议人工复核。
   - 验收：越界/无库/高风险三类 query 各有稳定话术；不再静默硬答。

8. **路由可观测（约定写入任务 `.meta/route-log.md` 或 `01-plan/PROCESS_LOG.md`，P2）**
   - 做什么：每次关键路由记一行 `时间 | query 摘要 | intent | confidence | 命中能力 | 是否澄清 | 是否护栏`；积累后可统计路由准确率、澄清率、误路由率，反哺 `/经验写回` 优化例句库与阈值。
   - 验收：完成一个真实任务后 `.meta/` 出现 route-log；`/经验写回` 能据此提出例句库/阈值调整建议。

## 参考来源

- semantic-router（aurelio-labs, v0.1.12, MIT）：https://github.com/aurelio-labs/semantic-router ；文档 https://docs.aurelio.ai/semantic-router 〔web〕
- RouteLLM（LMSYS/Berkeley, v0.2.0）：博客 https://lmsys.org/blog/2024-07-01-routellm/ ；论文 arXiv 2406.18665 ；anyscale/llm-router 〔web〕
- GPT‑5 router：OpenAI《Introducing GPT‑5》https://openai.com/index/introducing-gpt-5/ ；GPT‑5 System Card 〔web〕
- Not Diamond：https://docs.notdiamond.ai/docs/what-is-not-diamond ；AWS Marketplace 条目 〔web〕
- Martian + RouterBench：Accenture 投资公告(businesswire, 2024-09)；RouterBench arXiv 2403.12031 ；https://withmartian.com/post/introducing-routerbench 〔web〕
- OpenRouter Auto Router：https://openrouter.ai/docs/guides/routing/routers/auto-router 〔web〕
- RouterArena：arXiv 2510.00202（2025-10，含 GraphRouter/Universal/CARROT/RouterDC/IRT-Router/Azure Model Router/vLLM SR 谱系）〔web〕
- vLLM Semantic Router："Iris" v0.1 博客 https://vllm.ai/blog/2026-01-05-vllm-sr-iris ；白皮书 https://vllm-semantic-router.com/white-paper.pdf ；MoM 模型族文档 〔web〕
- LlamaIndex Routers/RouterQueryEngine：https://developers.llamaindex.ai/python/framework/module_guides/querying/router/ ；VectorIndexAutoRetriever 文档 〔web〕
- LangChain SelfQueryRetriever：https://python.langchain.com/docs/how_to/self_query/ 〔web〕
- Adaptive-RAG：starsuzi/Adaptive-RAG（"Learning to Adapt RAG through Question Complexity"）；LangGraph Adaptive-RAG 教程 〔web〕
- OpenAI Agents SDK Handoffs/Orchestration：https://openai.github.io/openai-agents-python/handoffs/ ；.../multi_agent/ 〔web〕
- LangGraph supervisor/Command：langchain-ai/langgraph-supervisor（已建议改手写 tool-based supervisor）；多 agent 指南 〔web〕
- Anthropic Routing workflow：https://www.anthropic.com/engineering/building-effective-agents ；Ticket routing 用例 https://docs.anthropic.com/en/docs/about-claude/use-case-guides/ticket-routing 〔web〕
- 意图分类对比：Respan《Intent Classification With LLMs (2026)》；alex-jacobs《Beating BERT?》；arXiv 2602.06370（编码器 vs LLM 成本-延迟）；BANKING77 RAG-prompting（asrjetsjournal）〔web〕
- 多意图/漂移：MIDLM（COLING 2025, 2025.coling-main.179）；DeepContext（arXiv 2602.16935）；DriftOS/driftos-core；Intent Drift Radar 〔web〕
- 澄清/反问：Structured Uncertainty/EVPI（arXiv 2511.08798）；Info-Gain/EIG（arXiv 2606.03135）；Proactive Info Gathering（EMNLP 2025 findings.843）；Modeling Future Turns（ICLR 2025）〔web〕
- 护栏式路由：NeMo Guardrails topical rails / topic_control / escalation；Llama-3.1 NemoGuard 8B TopicControl 〔web〕
- FrugalGPT（级联）：Chen et al. 2023 〔知识〕；GPTCache（语义缓存）〔知识〕
