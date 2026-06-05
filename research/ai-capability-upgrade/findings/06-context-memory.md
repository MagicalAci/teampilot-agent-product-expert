# 域 6：上下文工程与记忆系统

> 子代理：context-memory ｜ 回写：`research/ai-capability-upgrade/findings/06-context-memory.md`
> 来源标注：〔web〕= 本轮 WebSearch/WebFetch 联网核实（2025-2026）；〔知识〕= 训练知识、未逐条复核（已尽量只用确有其物的框架/论文）；〔本地〕= 直接读本环境 MCP descriptor 得到。
> 边界：本域聚焦**上下文窗口的供给/压缩/卸载** + **跨会话记忆的分类/框架/生命周期**。检索机制本身（向量库/混合检索/重排/GraphRAG/Agentic RAG）见域 5；反思/Reflexion/Self-Refine 的**推理范式角度**见域 1；子代理上下文隔离 / artifact 写文件 / plan 存 Memory 的**运行时语义**见域 2；prompt 优化（DSPy/GEPA）与模板版本化见域 11；记忆基准与自进化评分闭环的 eval 基建见域 9。本域只取这些主题的**上下文/记忆角度**并交叉引用。

---

## 领域概述

**上下文工程（context engineering）** 是 prompt engineering 的自然延伸：prompt engineering 关注"写什么指令"，context engineering 关注"在推理的每一步往有限的上下文窗口里**喂什么 token**"——系统指令、工具、MCP、外部数据、消息历史、记忆全都要策展（Anthropic、Cognition 已把它定性为"构建可靠 agent 的第一要务"）〔web〕。其核心物理约束是 **注意力预算有限、上下文是边际收益递减的稀缺资源**：实证（Chroma 2025）显示所有前沿模型都有 **context rot**——性能随输入长度增长而退化，且这与经典的 **lost-in-the-middle**（位置型失准）是两个独立现象〔web〕。业界把上下文操作收敛成四范式：**写出(write)/选入(select)/压缩(compress)/隔离(isolate)**〔web〕。

**记忆系统** 则是把上下文窗口装不下、或需跨会话复用的信息持久化到窗口之外。学界以 **CoALA**（Princeton 2023）为标准框架，把 agent 记忆分为 **工作记忆（活跃上下文）** 与 **长期记忆：情景(episodic)/语义(semantic)/程序(procedural)**〔web〕。2025-2026 已涌现一批成熟框架（MemGPT/Letta、Mem0、Zep/Graphiti、LangMem、Cognee、A-MEM），共识是：**记忆不是"存储"而是"系统"——必须有写入/检索/巩固/遗忘/冲突解决的生命周期规则，只 append 不演化的记忆会随时间退化**〔web〕；且 **记忆≠RAG**（RAG 重检索质量、无状态；记忆重随时间适应、有状态），生产里多数二者并用〔web〕。

对「产品专家 Agent」这是**最薄弱、却最高杠杆**的域：它当前的"记忆"≈任务文件夹过程文档 + 仓库文件 +`/经验写回`手动写回 PR（一种**离线人审的程序记忆**），**没有跨会话情景/语义记忆、没有上下文压缩引擎、没有 scratchpad/笔记机制、没有上下文预算 policy**。而本环境恰好已挂载 **claude-mem MCP**（21 个工具，3 层 token 省工作流），可直接补上"跨会话情景 + 语义记忆"这一层——这是本域落地建议的核心。

---

## SOTA 技术目录

> 按子类分组，共 **52 条**。成熟度：实验 / 成长 / 成熟 / 事实标准。

### 0. 基础概念与上下文工程总框架

| 技术/概念 | 一句话 | 何时用 | 成熟度 | 代表实现/论文 | 来源 |
|---|---|---|---|---|---|
| Context Engineering（定义） | 策展并维护推理时进入上下文窗口的最优 token 集（含 prompt 之外的一切） | 任何多轮/长程 agent | 事实标准（新共识） | Anthropic《Effective context engineering for AI agents》 | 〔web〕 |
| Prompt vs Context engineering | prompt=写指令"说什么"；context=动态供给"喂什么"（系统指令+历史+检索+工具+记忆） | 从单轮提示转向多轮 agent 时的范式切换 | 事实标准 | Anthropic；Cognition (Walden Yan)："context engineering 是 #1 job" | 〔web〕 |
| 注意力预算（attention budget） | 上下文是有限资源、边际收益递减；每个新 token 都消耗注意力预算 | 决定"放多少/放什么"的根本约束 | 成长 | Anthropic 同文 | 〔web〕 |
| Write/Select/Compress/Isolate 四范式 | 上下文工程的四类操作：写到窗口外 / 选回窗口 / 压缩 / 拆分隔离 | 给上下文策略归类的总框架 | 成长（广泛采用） | LangChain (Lance Martin)；`langchain-ai/context_engineering` | 〔web〕 |
| "最小高信号 token 集"原则 | 找到能最大化目标达成概率的**最小**高信号 token 集 | 上下文取舍的指导原则 | 成长 | Anthropic 同文 | 〔web〕 |
| CoALA 认知架构 | 把语言 agent 形式化为 工作记忆 + 长期记忆(语义/情景/程序) | 设计记忆体系的理论底座 | 成长（学术标准） | Sumers/Yao et al. 2023 (arXiv 2309.02427) | 〔web〕 |

### A. 记忆分类（CoALA + 认知科学）

| 记忆类型 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 工作记忆 / in-context | 活跃上下文窗口：当前任务态、近期轮次、scratchpad；会话结束即逝 | 即时推理/规划/工具结果暂存 | 事实标准 | CoALA working memory；KV cache 是其物理载体 | 〔web〕 |
| 短期记忆（对话历史） | 单会话内的轮次/缓冲 | 单会话连续性 | 事实标准 | 通用 chat history | 〔web〕 |
| 情景记忆 episodic | 带时间戳的具体经历（对话轮/工具调用/观察），可回忆"上次发生了什么" | 跨会话连续性、复用过往经验/案例 | 成长 | Generative Agents 记忆流；Letta recall；claude-mem observations/timeline | 〔web〕 |
| 语义记忆 semantic | 去情景化的事实/偏好/领域知识（向量库或知识图谱） | 个性化、事实复用 | 成长 | Mem0；Zep；LangMem profiles/collections | 〔web〕 |
| 程序记忆 procedural | "怎么做"的技能/工作流/规则，显式存技能库或隐式入权重/prompt | 复用成功流程、agent 自改行为 | 成长 | Voyager skill library；LangMem(改prompt)；**本仓库 skills/policies 即此类** | 〔web〕 |
| 组织/上下文记忆（企业第 5 类） | 受治理的定义/血缘/实体身份/访问策略 | 企业数据 agent（CoALA 4 类外的补充） | 成长 | Atlan | 〔web〕 |

### B. 记忆框架 / 系统

| 框架 | 一句话 | 何时用 | 成熟度 | 代表实现/论文 | 来源 |
|---|---|---|---|---|---|
| MemGPT / Letta | OS 隐喻：分层记忆(core/recall/archival)，agent 用函数调用自行"换页"进出上下文 | 自主长程 agent、要 agent 自管记忆 | 成长 | Packer et al. 2023；Letta（MemGPT 团队） | 〔web〕 |
| Letta sleep-time agent（memory_rethink） | 后台二级模型在会话间**整体重写**记忆块=巩固而非检索 | 记忆巩固/重组 | 成长 | Letta；Synix 源码分析 | 〔web〕 |
| Mem0 | 抽取-检索流水线 + 向量(可选图)后端，跨会话个性化；最易落地 | 即插即用个性化（chatbot 记偏好） | 成长（生产就绪） | Mem0 (arXiv 2504.19413)；$24M 融资、SOC2 | 〔web〕 |
| Zep / Graphiti | **时序知识图谱**：每条事实带有效期窗口，新信息使旧事实失效但保留历史 | 需时序推理/事实演变追踪 | 成长 | Zep (arXiv 2501.13956)；LongMemEval 63.8% vs Mem0 49.0% | 〔web〕 |
| LangMem | LangChain SDK：语义(collections/profiles)/情景(few-shot)/程序(优化prompt)；hot-path 工具 + 后台巩固 | 已用 LangGraph、想三类记忆 | 成长 | LangChain 2025；`create_manage_memory_tool` | 〔web〕 |
| Cognee | ECL(Extract-Cognify-Load) 把数据→知识图谱(图+向量+关系三库)；`memify` 巩固/剪枝/重赋权 | 把文档/仓库建成"公司大脑" | 成长 | Cognee/Topoteretes；有 MCP server | 〔web〕 |
| A-MEM | Zettelkasten 风：每条记忆=原子笔记(关键词/标签/上下文)，自动建语义链 + 新记忆触发旧记忆**演化** | 需自组织、自演化的记忆网 | 实验（NeurIPS'25） | Xu et al. 2025 (arXiv 2502.12110) | 〔web〕 |
| Generative Agents（记忆流+反思） | 记忆流(观察+重要度+时间戳+embedding) + 周期反思综合 + 检索(近因×重要×相关) | 长程多轮、需经验积累 | 成长（学术影响大） | Park et al. 2023 | 〔web〕 |
| Voyager skill library | 把验证过的可执行程序当技能存库，按 NL 描述索引、按需组合 | 程序记忆的代表实现 | 成长 | Wang et al. 2023a | 〔web〕 |
| **claude-mem（本环境已挂载）** | 观察/记忆存储 + 3 层 token 省工作流(search→timeline→get_observations)；FTS + corpus；按 projectId 作用域 | **给单体 agent 直接接跨会话情景/语义记忆** | 成长（环境内可用） | `user-claude-mem` / `plugin-claude-mem-mcp-search` MCP | 〔本地〕 |
| Honcho | 专注用户表征/记忆；LongMemEval 90.4%、BEAM 强，仅用 11.4% 上下文 | 个性化助手 | 成长 | Honcho evals | 〔web〕 |
| Hindsight / MemPalace 等新系统 | TEMPR 检索+实体消解+KG+重排，10M token 仍 SOTA(64.1% BEAM) | 超大规模记忆检索 | 实验 | Vectorize | 〔web〕 |

### C. 上下文管理 / 缓存 / 压缩 / 卸载

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| KV cache（请求内） | prefill 的 K/V 存 GPU 复用，使解码 O(N) 而非 O(N²) | 所有推理引擎默认 | 事实标准 | 通用；DeepSeek MLA 压缩 ~4× | 〔web〕 |
| Prompt caching（跨请求） | 缓存稳定前缀的 KV，命中则跳过重算，省 50-90% 成本、降 ~80% TTFT | 大固定上下文反复引用(RAG/多轮/many-shot) | 成熟 | Anthropic(显式 `cache_control`,读省90%,TTL 5min/1h)、OpenAI(自动>1024tok,读省50%)、DeepSeek(自动磁盘,64tok块)、Gemini | 〔web〕 |
| KV cache offloading | 把 KV 从 GPU 卸到 CPU/SSD/远程存储分层，跨请求/重启持久 | 自建推理、长上下文复用 | 成长 | vLLM + LMCache；NetApp/VAST(TTFT 降 99%) | 〔web〕 |
| Compaction（压实） | 接近窗口上限时把历史摘要后重启，保留决策/未决 bug/最近文件 | 长程对话/任务 | 成熟（一方 API） | Anthropic `compact_20260112`(≥50K 触发)；Claude Code | 〔web〕 |
| Context editing / tool-result clearing | 阈值后清除陈旧工具结果/思考块，server-side 策展 | 重工具调用的 agentic 流 | 成熟（一方 API） | Anthropic `clear_tool_uses_20250919`；单独 +29%、配 memory +39% | 〔web〕 |
| Memory tool（文件式） | agent 通过文件系统在上下文外存取信息，跨会话建知识库 | 跨会话项目态 | 成长（beta） | Anthropic `memory_20250818`(Sonnet 4.5) | 〔web〕 |
| 结构化笔记 / scratchpad / agentic memory | agent 定期把笔记写到上下文外(NOTES.md/todo)，需要时再拉回 | 长程任务防遗忘 | 成长（最佳实践） | Anthropic；Claude Code NOTES.md；Manus todo 文件 | 〔web〕 |
| Context offloading（上下文卸载） | 把大产物/历史写外部文件，上下文只留轻量引用 | 大产物保真、省 token | 成熟（最佳实践） | Anthropic 子代理→filesystem（交叉域 2） | 〔web〕 |
| 对话摘要（summarization） | 在 agent 轨迹中插入摘要步，蒸馏历史（如 115k→60k） | 多步长轨迹/agent-agent 交接 | 成熟 | LangChain；Cognition(微调摘要模型做交接) | 〔web〕 |
| Just-in-time 检索 | 不预载全部，运行时按需用轻量标识(路径/链接)动态取 | 大知识面、上下文宝贵 | 成长 | Anthropic 同文 | 〔web〕 |
| 子代理上下文隔离 | 专精子代理各自干净窗口干活，只回 1-2k token 蒸馏摘要 | 复杂研究/技术深挖 | 成熟 | Anthropic 多代理（交叉域 2） | 〔web〕 |
| 上下文窗口预算管理 | 把窗口当有限预算，最大化相关 token、最小化无关 token | 长上下文任务 | 成长 | Chroma；Anthropic | 〔web〕 |

### D. 上下文退化（失败模式，**设计护栏所依据**）

| 现象 | 一句话 | 警惕场景 | 成熟度 | 代表证据 | 来源 |
|---|---|---|---|---|---|
| Lost-in-the-middle | U 型曲线：开头/结尾注意强、中间弱，中段 +30% 失准 | 长上下文里关键信息放中段 | 成熟（被反复验证） | Liu et al. Stanford/TACL 2024 | 〔web〕 |
| Context rot（上下文腐烂） | 性能随输入长度增长而退化（与位置无关），18 模型全中 | 即使没到窗口上限也退化 | 成长（2025 形式化） | Chroma 2025 (Hong/Troynikov/Huber) | 〔web〕 |
| 注意力稀释（attention dilution） | 注意力二次方，100K token = ~100 亿对关系，被摊薄 | 解释长上下文退化机理 | 成长 | Morph；Anthropic | 〔web〕 |
| Distractor interference（干扰项干扰） | 语义相似但无关的内容主动**误导**模型 | RAG/长上下文噪声 | 成长 | Chroma；Morph | 〔web〕 |
| 上下文四种失败 | poisoning(幻觉入context被反复引用) / distraction(分心) / confusion(无关工具/信息混淆) / clash(自相矛盾) | 诊断长上下文/记忆失败 | 成长 | Drew Breunig 2025《How Contexts Fail》 | 〔web〕 |
| 记忆膨胀 / 上下文降级 | append-only 致矛盾累积、prompt 膨胀、检索噪声 | 不做演化的记忆 | 成长 | 多篇 2025 综述（含 arXiv 2509.25250） | 〔web〕 |

### E. 记忆操作（生命周期：写/选/压/隔 + 巩固/遗忘/冲突）

| 操作 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 写入/编码（write/encode） | 决定什么值得记（决策/偏好/gotcha/口径）而非全记 | 记忆质量起点 | 成长 | LangMem；Mem0 抽取 | 〔web〕 |
| 检索/选择（retrieve/select） | 按相关×近因×重要度取回（向量/图/FTS/混合） | 把记忆拉回上下文 | 成长 | Generative Agents 三因子；claude-mem search→timeline | 〔web〕 |
| 巩固（consolidation） | 把多条情景抽象为语义规则（常需显式触发/启发式） | 降噪、形成 schema | 成长 | LangMem 后台；Letta sleep-time；Cognee `memify`；睡眠启发 replay/gist | 〔web〕 |
| 遗忘/衰减（forgetting/decay） | 按 近因×相关×效用 复合分剪枝/降权陈旧记忆 | 防膨胀、控成本 | 成长 | Intelligent Decay(arXiv 2509.25250，降 22% token)；Continuum Memory | 〔web〕 |
| 更新/冲突解决（update/conflict） | 新信息使旧事实失效、合并矛盾、保留历史 | 事实演变；记忆与来源不一致 | 成长 | Zep 有效期失效；LangMem 去重合并矛盾 | 〔web〕 |
| 记忆演化（evolution） | 新记忆触发既有记忆的内容/标签/链更新 | 自组织记忆网 | 实验 | A-MEM | 〔web〕 |
| 反思（reflection） | 周期性把低层观察综合成高层洞见，写回记忆影响后续 | 长程经验积累 | 成长 | Generative Agents；Reflexion（交叉域 1） | 〔web〕 |
| 个性化记忆（personalization） | 抽取并持久化用户偏好/约定，跨会话复用 | 助手类产品 | 成长 | Mem0；LangMem profiles；Honcho | 〔web〕 |
| 时序有效性（temporal validity） | 事实带 valid-from/valid-to，支持"某时点为真"的时间旅行查询 | 需追踪事实何时成立 | 成长 | Zep/Graphiti 双时态 | 〔web〕 |

### F. 长上下文 vs RAG vs 外部记忆（取舍）

| 方案 | 一句话 | 何时用 | 成熟度 | 代表 | 来源 |
|---|---|---|---|---|---|
| 长上下文（full-context） | 全部历史塞进窗口，透明但无界增长且会 context rot | 短交互、调试透明、< 数万 token | 事实标准（基线） | 通用 | 〔web〕 |
| RAG（检索增强） | 查询时从外部索引取 chunk，**无状态**、会话结束即忘 | 大文档语料的事实检索（广度） | 成熟 | 详见域 5 | 〔web〕 |
| 外部记忆（agent memory） | **有状态**持久化，跨会话存"学到了什么"，会演化/巩固 | 跨会话连续性（深度/连续） | 成长 | Letta/Mem0/Zep/Cognee | 〔web〕 |
| "记忆 ≠ RAG" | RAG 重检索质量；长上下文重序列处理；记忆重随时间适应 | 选型不要混为一谈 | 成长（共识） | Stamile 2025；Atlan | 〔web〕 |
| 混合（RAG + 记忆） | 生产共识：RAG 做广度知识、记忆做个性化连续性 | 多数生产 agent | 成长（2026 共识） | Atlan | 〔web〕 |
| MEM1 | 把记忆与推理耦合训练，每轮只保留紧凑内部状态，**常数级**内存 | 高效长程 agent | 实验 | MEM1 2025 (arXiv 2506.15841) | 〔web〕 |
| Continuum Memory（CMA）6 条件 | 真记忆须满足：持久/选择保留/检索驱动突变/联想路由/时序连续/巩固抽象，否则只是 RAG | 评判"是不是真记忆" | 实验 | arXiv 2601.09913 | 〔web〕 |

### G. 自我进化上下文（记忆 × 自改，**北极星**，交叉域 1/9/11）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表 | 来源 |
|---|---|---|---|---|---|
| ACE（Agentic Context Engineering） | 把上下文当"演化 playbook"：Generator/Reflector/Curator + **增量 delta 更新**，避免 context collapse / brevity bias；+10.6% agent / +8.6% finance，靠执行反馈无需标注 | 在线/离线自改上下文与 agent 记忆 | 实验（ICLR'26） | Stanford Zhang et al. 2025 (arXiv 2510.04618) | 〔web〕 |
| Dynamic Cheatsheet | 测试时把可复用策略累积成"备忘单"注入后续 | 测试时自适应记忆 | 实验 | ACE 前作 | 〔web〕 |
| GEPA（反射式 prompt 进化） | 遗传-帕累托反射进化优化 prompt（压缩向，与 ACE 的"扩充"互补） | prompt 优化（交叉域 11） | 实验 | 2025；DSPy 生态 | 〔web〕 |
| Reflexion-as-memory | 把失败的语言化反思写入记忆，下轮改进 | 可多次尝试、有成败信号 | 成熟 | Shinn et al. 2023（交叉域 1） | 〔web〕 |
| LangMem prompt optimizer（procedural） | 从轨迹+反馈自动改系统 prompt（gradient/prompt_memory/metaprompt） | 程序记忆自进化 | 成长 | LangMem | 〔web〕 |

### H. 评估与基准（**读榜须警惕方法学**）

| 基准 | 一句话 | 何时用 | 成熟度 | 代表 | 来源 |
|---|---|---|---|---|---|
| LoCoMo | 长多会话对话 QA(单跳/多跳/时序/开域/对抗)，但仅 16-26k token、易被绕过 | 记忆 QA（注意已过时） | 成长（争议） | arXiv 2402.17753 | 〔web〕 |
| LongMemEval | 500 题 × ~115k token，五能力(抽取/多会话推理/时序/知识更新/弃答) | 长对话记忆 | 成长 | arXiv 2410.10813 | 〔web〕 |
| BEAM | 10M token、10 能力，逐题 rubric 评分 | 极长上下文记忆 | 实验（新） | BEAM 2025 | 〔web〕 |
| Letta Leaderboard | 固定框架/工具、动态生成记忆交互，评**模型**的记忆管理能力 | 模型级记忆能力对比 | 成长 | Letta | 〔web〕 |
| 基准可信度警示 | top_k>语料、超大窗口吞全量等会**绕过检索**；LLM-judge 随模型漂移 ~10 分 | 读任何记忆榜单前 | 成长（重要） | Vectorize；Continua；Zep 批评 Mem0 | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **"上下文工程"取代"prompt 调参"成为 agent 工程第一要务。**〔web〕 Anthropic 与 Cognition 罕见地高度趋同：可靠性 = 上下文质量；prompt engineering 退为 context engineering 的一个子集（写系统指令）。这直接抬升了"记忆 + 上下文供给"在 agent 设计中的权重。
2. **context rot 被实证为普遍现象，且 ≠ lost-in-the-middle。**〔web〕 Chroma 2025 测 18 个前沿模型，全部随输入长度退化（与位置无关）；叠加 Stanford 的位置型 U 形失准。结论：**百万 token 窗口 ≠ 百万 token 可靠**，必须主动做上下文窗口管理，而非"塞得下就塞"。
3. **上下文管理从"自建编排"下沉为"一方 API 能力"。**〔web〕 Anthropic 把 compaction(`compact_20260112`)、context editing/tool-result clearing(`clear_tool_uses_20250919`)、memory tool(`memory_20250818`) 做成原生特性；实测 context editing 单独 +29%、配 memory tool +39%——**收益来自上下文管理而非模型本身**。
4. **记忆框架百花齐放但"各押一种架构"。**〔web〕 Letta=可编辑文本块/文件、Mem0=向量(+实体)、Zep/Graphiti=时序知识图谱、Cognee=实体抽取流水线、A-MEM=Zettelkasten 自演化。选型应按**架构契合度**而非榜单分数。
5. **"记忆是系统不是存储"成为共识：演化是一等公民。**〔web〕 多篇 2025 工作强调 **巩固(consolidation) + 遗忘(forgetting)** 必须内建——只 append 的记忆会矛盾累积、prompt 膨胀、检索变噪。出现"Intelligent Decay"(近因×相关×效用)、睡眠启发的 replay/gist、Letta sleep-time `memory_rethink`、Cognee `memify`。
6. **时序知识图谱成为"事实会变"场景的强解。**〔web〕 Zep/Graphiti 给每条事实加有效期窗口，新信息使旧事实失效但保留历史，LongMemEval 上显著优于扁平向量（63.8% vs 49.0%）——对"竞品迭代、价格变化、口径更新"等产品调研场景天然契合。
7. **自进化上下文(ACE)把"记忆"与"自我改进"打通。**〔web〕 ACE(Stanford 2025) 把上下文当"演化 playbook"，用 Generator/Reflector/Curator + **增量 delta** 累积策略，避免"context collapse / brevity bias"，靠执行反馈无需标注即 +10.6%——这正是`/经验写回`自进化闭环的"北极星形态"。
8. **结构化笔记/scratchpad + 上下文卸载成长程 agent 标配。**〔web〕 Claude Code 用 NOTES.md、Manus 用 todo 文件把状态写到窗口外按需拉回；子代理各用干净窗口、只回 1-2k token 蒸馏摘要（与域 2 的 artifact 写文件同源）。
9. **记忆基准集体"信任危机"，催生更难的新基准。**〔web〕 LoCoMo(仅 16-26k token)、LongMemEval 被指易被"超大窗口吞全量/top_k>语料"绕过，LLM-judge 换模型就漂 10 分；BEAM(10M token)、MemoryArena、Locomo-Plus、Hindsight 试图替代但尚未形成标准。
10. **prompt caching 成本工程化、被所有主流厂商支持。**〔web〕 Anthropic(显式)/OpenAI(自动)/DeepSeek(磁盘自动 64tok 块)/Gemini 都支持，读省 50-90%、TTFT 降 80%——**把稳定的系统指令/policy/skills 前置**即可顺带吃到缓存红利。

---

## 对标产品专家 Agent

> 核心命题：当前"记忆"= 任务文件夹过程文档 + 仓库文件 +`/经验写回`手动 PR（**离线人审的程序记忆**）。缺的是**跨会话情景/语义记忆**、**上下文压缩/笔记机制**、**上下文预算 policy**。本环境已挂 **claude-mem MCP** 可直接补第一项。下面逐项给"现状→差距→增强(P0/P1/P2)"。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| 记忆 = `tasks/{task}/` 过程文档 + `knowledge/` + 仓库文件，靠下次人工翻看 | **无跨会话情景/语义记忆**：新任务/新会话从零开始，"上次同类调研踩过的坑/某竞品口径/用户偏好"无法自动召回 | **P0**：接入 **claude-mem MCP** 做跨会话**情景(observations/timeline)+语义(corpus/FTS)** 记忆层，按 `projectId` 作用域；任务启动先检索、收尾写观察 |
| `/经验写回`·`/更新请求`= 把方法手动写回仓库 PR + 契约测试（人审合并） | 这是**离线、人触发、人审**的程序记忆，**无低摩擦机器可读记忆、无即时回忆**；且写回是"全量重写文档"易丢细节(brevity bias/context collapse) | **P0**：保留仓库为"治理级程序记忆"；新增机器侧记忆读写 protocol。**P2**：把`/经验写回`升级为 **ACE 式演化 playbook**(Generator/Reflector/Curator + 增量 delta)，交叉域 9 eval |
| 长任务靠任务文件夹分阶段推进（task-navigator） | **上下文窗口内无 compaction/笔记机制**：长链路(竞品深挖、PRD 成稿、多平台采集)有 **context rot / lost-in-the-middle** 风险，无显式"把过程写出去再拉回" | **P0**：立 **scratchpad/NOTES 约定**(进展/决策/未决写窗口外)。**P1**：阶段边界做摘要(compaction 思路)，把过程文档当外部记忆按需拉回 |
| 域 2 已建议子代理产物写文件 + 回轻量引用 | 上下文隔离已有雏形，但**无"记忆读写"协议**：子代理/主代理不知道何时该 search 记忆、写什么进记忆 | **P1**：把记忆读写并入交接契约——任务/阶段启动先 `search` 历史记忆，收尾写结构化 `observation`（决策/结论/gotcha） |
| 无显式上下文预算 policy | 不区分"什么 write 到窗口外 / 什么 select 回来 / 什么 compress / 什么 isolate 给子代理"，全凭模型自觉 | **P1**：新增 `policies/context-budget.md`，把 **write/select/compress/isolate 四范式** 映射到本仓库五能力 |
| 记忆若只增不减（任务文件夹 + 未来 claude-mem） | **无巩固/遗忘/冲突解决**：记忆会膨胀、矛盾(旧竞品数据 vs 新数据)、检索变噪；与仓库文件冲突时无仲裁规则 | **P2**：立巩固/遗忘/冲突 policy——**仓库 = source of truth、记忆 = advisory**；近因×相关×效用衰减；冲突时仓库优先、过期记忆失效保留历史(借 Zep) |
| 提示词靠 `prompt-engineering-techniques.md`，未提缓存 | **未利用 prompt caching**：稳定的 policy/rules/skills 前缀可缓存省成本(多为 Cursor 底层平台事) | **P2**（多属平台层）：约定把**稳定指令前置、易变内容后置**以利缓存命中；记为备忘，不强求 |

### claude-mem MCP 接入可行性评估（重点）

**结论：可行性高、建议试点接入**。〔本地〕+〔web〕

- **现状**：环境内已挂两个**镜像**服务 `user-claude-mem` 与 `plugin-claude-mem-mcp-search`，工具集完全相同(各 21 个)，**择一即可**（建议 `user-claude-mem`）。
- **能力映射**：
  - 写入 → `observation_add`（或别名 `memory_add`）：`projectId`(必填) + `content`/`narrative` + `kind` + `title` + `metadata`。→ **情景记忆**。
  - 检索 → `search`/`observation_search`/`memory_search`（FTS，走 `/v1/search`）+ `timeline`(按 anchor/query 取时序上下文) + `get_observations([IDs])`(只取过滤后的全文)。→ 官方 **3 层工作流 search→timeline→get_observations，"先过滤再取全文，省 10× token"**——本身就是一条现成的上下文预算实践。
  - 语义层 → `build_corpus`/`prime_corpus`/`query_corpus`/`list_corpora`：把语料建成可查 **corpus** → **语义记忆**。
  - 代码 AST → `smart_search`/`smart_outline`/`smart_unfold`(tree-sitter)：对 Demo 开发能力有用。
- **它精确补上**："没有跨会话向量/情景记忆"这一最大缺口，且自带 token 省工作流。
- **风险与约束**：①外部存储的**可用性/持久性**（需降级：MCP 不可用时回退到仓库文件）；②**写入需白名单**（只写决策/结论/口径/gotcha 的结构化摘要，**不 dump 原文**，否则记忆变噪）；③**治理**（与仓库冲突时仓库为准）；④需**遗忘/巩固策略**防膨胀。
- **定位**：claude-mem = **情景/语义 working recall（低摩擦、机器管理）**；仓库 +`/经验写回`= **程序记忆（治理级、人审、可追溯）**——二者**互补**，不互相替代。

---

## 落地建议

> 原则：与本仓库"Cursor 原生、轻量聚焦、文件约定 + policy/rule"定位一致，**不引入重记忆框架**；优先用 **claude-mem MCP（已挂载）+ 文件约定 + policy** 补"跨会话记忆 / 上下文压缩 / 笔记 / 预算"四件事。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 记忆读写 protocol（补"跨会话记忆"的行为规范）
- **放哪**：新增 `policies/memory-protocol.md`；并在 `.cursor/rules/task-navigator.mdc` 的"任务启动—主动分析"段加一步"先检索记忆"。
- **做什么**：定义 **读时机 + 写时机 + 写什么**。读：任务/阶段启动先按任务关键词检索历史记忆（同类竞品、口径、踩坑），命中则纳入规划。写：阶段/任务收尾写**结构化观察**，字段固定 `kind / 决策 / 结论 / 口径与依据 / gotcha / 未决项 / 来源`。明确**写入白名单**（只写可复用的高信号结论，不写原文/中间废稿）。
- **验收信号**：`tests/test_product_expert_agent.py` 断言 `policies/memory-protocol.md` 存在且含标记 `检索记忆`/`观察写入`/`写入白名单`；task-navigator 规划输出含"已检索历史记忆：<命中/无>"一行。

### P0-2 接入 claude-mem MCP（落实记忆后端）
- **放哪**：`policies/memory-protocol.md` 的"记忆后端"小节 + `product-expert-commands` 路由说明。
- **做什么**：选用 `user-claude-mem`；约定 `projectId =` 仓库名或 `task` slug（跨任务复用用仓库名，任务内用 task slug）。读用官方 **3 层工作流**：`search(query)` → `timeline(anchor=ID)` → `get_observations([IDs])`；语义检索用 `query_corpus`。写用 `observation_add`。**降级**：MCP 不可用时回退到 `tasks/{task}/memory/` 文件（见 P0-3）。
- **验收信号**：一次真实任务里，启动阶段出现 `search`/`timeline` 调用且把命中结论写入规划；收尾出现 `observation_add` 且内容符合白名单；MCP 宕机模拟下能回退到本地记忆文件不报错。

### P0-3 记忆目录约定 + scratchpad/NOTES（补"笔记机制"与降级载体）
- **放哪**：约定 `tasks/{task}/memory/`（`episodic.md` 情景流水 / `semantic.md` 事实与口径）+ `tasks/{task}/.notes/scratchpad.md`（长任务过程笔记）。程序记忆仍走仓库 `skills/policies`。
- **做什么**：长任务把"进展/决策/未决/下一步"写 `scratchpad.md`（窗口外），需要时拉回——对抗 context rot；`memory/` 作为 claude-mem 的**本地镜像/降级载体**，保证离线可用与可人审。
- **验收信号**：长任务目录下出现非空 `scratchpad.md`，且阶段切换时主代理"读 scratchpad 续跑"而非靠聊天历史；`memory/` 与 claude-mem 内容一致(或可对账)。

### P1-1 上下文预算 policy（write/select/compress/isolate 落到本仓库）
- **放哪**：新增 `policies/context-budget.md`，与 `agent-team-methodology.md` 第四部分"Token 优化"对齐。
- **做什么**：把四范式映射到五能力——**write**: 大产物/采集原文写 `deliverables/`、`context/`，上下文留引用；**select**: 用 claude-mem/RAG(域 5) just-in-time 取；**compress**: 阶段边界摘要、子代理只回蒸馏摘要；**isolate**: 多平台采集/多视角分析扇出给子代理（交叉域 2）。写明"上下文是有限预算、context rot 真实存在"的纪律。
- **验收信号**：policy 含 `write/select/compress/isolate` 四节且各带本仓库示例；竞品/采集类任务默认把原文落文件、上下文只留引用。

### P1-2 阶段摘要 / compaction 借鉴（补"压缩引擎"）
- **放哪**：成稿/采集门禁相关 skill + `context-budget.md` 的"压缩"小节。
- **做什么**：长链路任务在阶段边界生成**结构化摘要**（保留决策/结论/未决，丢弃冗余工具输出），下一阶段以"摘要 + 最近若干文件"续跑（仿 Claude Code compaction）；agent-agent 交接也用摘要而非贴原文（仿 Cognition）。
- **验收信号**：长任务出现"阶段摘要"产物；下一阶段输入是"摘要 + 引用"而非全量历史；可观测到 token 占用下降。

### P2-1 巩固 / 遗忘 / 冲突解决 policy（让记忆"是系统不是垃圾场"）
- **放哪**：`policies/memory-protocol.md` 的"记忆生命周期"小节。
- **做什么**：①**巩固**：周期性把多条同类情景抽象成语义条目(口径/规则)写 `semantic.md`/corpus；②**遗忘**：按 近因×相关×效用 标注可归档/降权的陈旧记忆；③**冲突**：**仓库 = source of truth**，记忆与仓库冲突以仓库为准；事实演变用"旧记忆失效但保留历史"(借 Zep 时序)。
- **验收信号**：policy 含 `巩固`/`遗忘`/`冲突仲裁(仓库优先)` 三条；出现一次"旧竞品数据被新数据标记失效但保留"的记录。

### P2-2 ACE 式演化 playbook（北极星：`/经验写回`升级，交叉域 9/11）
- **放哪**：`policies/submission-review-contract.md` + `agent-team-methodology.md` 自我进化部分。
- **做什么**：待域 9 eval 基建就位后，把`/经验写回`从"全量重写文档 + 契约存在性测试"升级为 **ACE 三角色 + 增量 delta**：Generator(产出轨迹) → Reflector(对比成功/失败提炼洞见) → Curator(把洞见转成对 skills/policies 的**局部增量更新 + helpful/harmful 计数**，去重剪枝)，避免 brevity bias / context collapse；用执行反馈(With-skill vs Baseline 量化)驱动。
- **验收信号**：写回 PR 模板要求"增量 delta(而非整篇重写) + 带/不带技能量化对比"；引入 helpful/harmful 计数字段；纳入合并门槛。

---

## 参考来源

- 〔web〕Anthropic《Effective context engineering for AI agents》（context engineering 定义、注意力预算、context rot、compaction、note-taking/memory tool、子代理隔离、just-in-time）— https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 〔web〕Anthropic 上下文管理一方 API：Claude Cookbook《Context engineering: memory, compaction, and tool clearing》、Context editing 文档（`compact_20260112` / `clear_tool_uses_20250919` / `memory_20250818`，+29%/+39%）— platform.claude.com/docs/en/build-with-claude/context-editing ；platform.claude.com/cookbook ；Anthropic《Prompt caching with Claude》— anthropic.com/news/prompt-caching
- 〔web〕Cognition / Anthropic 上下文工程之争 — patmcguinness.substack.com《The AI Agent Architecture Debate》；medium《The Agent Architecture Wars》（Walden Yan "context engineering is #1 job"）
- 〔web〕LangChain《Context Engineering for Agents》write/select/compress/isolate — rlancemartin.github.io/2025/06/23/context_engineering ；`github.com/langchain-ai/context_engineering`（对话摘要 115k→60k）
- 〔web〕CoALA《Cognitive Architectures for Language Agents》(working/episodic/semantic/procedural) — arXiv 2309.02427 ；Atlan《Types of AI Agent Memory》（+企业第 5 类）— atlan.com/know/types-of-ai-agent-memory
- 〔web〕记忆综述：arXiv 2505.00675（episodic/semantic/procedural/working + KV cache 作为工作记忆载体）；《Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers》arXiv 2603.07670（Generative Agents 记忆流、Voyager 技能库、巩固示例）
- 〔web〕框架：MemGPT/Letta（Packer et al. 2023；Letta sleep-time `memory_rethink`）；Mem0 — arXiv 2504.19413；Zep/Graphiti — arXiv 2501.13956；LangMem — langchain.com/blog/langmem-sdk-launch（语义/情景/程序 + prompt optimizer gradient/prompt_memory/metaprompt）；Cognee — cognee.ai（ECL/`cognify`/`memify`）；A-MEM — arXiv 2502.12110（Zettelkasten 自演化）
- 〔web〕框架横评 — codepointer.substack.com《Agent Memory Systems and Knowledge Graphs: Letta, Mem0, Graphiti, Cognee》；synix.dev《Agent Memory Systems: A Source-Level Analysis of Eight Architectures》；atlan.com《Best AI Agent Memory Frameworks in 2026》
- 〔web〕prompt caching / KV cache — synthorai.io《How KV Cache & TTL Work》（各厂 TTL、DeepSeek MLA 压缩 4×/64tok 块）；medium《Prompt Caching: What It Is, What It Is Not》；KV offloading — vastdata.com ；community.netapp.com（vLLM + LMCache，TTFT 降 99%）
- 〔web〕上下文退化 — Chroma《Context Rot: How Increasing Input Tokens Impacts LLM Performance》(research.trychroma.com，18 模型) ；hivetrail.com ；morphllm.com/context-rot ；Liu et al.《Lost in the Middle》Stanford/TACL 2024 ；Drew Breunig《How Contexts Fail and How to Fix Them》— dbreunig.com/2025/06/22
- 〔web〕记忆生命周期/取舍 — claudiostamile.substack.com《Agent Memory Is Not RAG》；atlan.com《AI Memory System vs RAG》；Intelligent Decay — arXiv 2509.25250（近因×相关×效用，降 22% token，+13.6% 完成率）；Continuum Memory — arXiv 2601.09913（CMA 6 条件）；MEM1 — arXiv 2506.15841
- 〔web〕自进化上下文 — ACE《Agentic Context Engineering》Stanford 2025（arXiv 2510.04618；Generator/Reflector/Curator、增量 delta、+10.6%/+8.6%、AppWorld）— ace-agent.github.io ；openreview.net/forum?id=eC4ygDs02R ；GEPA / Dynamic Cheatsheet（交叉域 11）
- 〔web〕基准与可信度 — LoCoMo arXiv 2402.17753 ；LongMemEval arXiv 2410.10813 ；BEAM / Hindsight — vectorize.io/articles/mempalace-benchmarks ；Honcho — honcho.dev/evals ；Letta Leaderboard — letta.com/blog/benchmarking-ai-agent-memory
- 〔本地〕claude-mem MCP descriptors — `mcps/user-claude-mem/`（21 工具：`observation_add`/`memory_add`、`search`/`observation_search`/`memory_search`、`timeline`、`get_observations`、`build_corpus`/`prime_corpus`/`query_corpus`/`list_corpora`、`smart_search`/`smart_outline`/`smart_unfold` 等；`__IMPORTANT` 定义 3 层 search→timeline→get_observations 工作流，"省 10× token"）；镜像服务 `mcps/plugin-claude-mem-mcp-search/`
- 〔web〕Generative Agents — Park et al. 2023《Generative Agents: Interactive Simulacra of Human Behavior》（记忆流 + 反思 + 近因/重要/相关检索，基建细节）
