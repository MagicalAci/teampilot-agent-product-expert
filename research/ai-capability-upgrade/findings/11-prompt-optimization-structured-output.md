# 域 11：Prompt/上下文优化与结构化输出

> 子代理：prompt-optimization-structured-output ｜ 回写：`research/ai-capability-upgrade/findings/11-prompt-optimization-structured-output.md`
> 来源标注：〔web〕= 本轮 WebSearch/WebFetch 联网核实（2026-06）；〔知识〕= 训练知识、未逐条复核（已尽量只用确有其物的框架/论文/产品，把握不准的标"(待核实)"）；〔本地〕= 直接读本仓库文件得到。
> 边界：本域聚焦 **"自动 Prompt 优化 + 结构化输出强约束 + Prompt 工程化管理"** 这一层——即 **机器替人调提示、解码层强制 schema、提示资产工程化** 三件事。**手写提示技巧**（零样本/少样本/CoT/角色/受限生成等 22 项）已在 `policies/prompt-engineering-techniques.md`，本域**对齐不重写**，只标注"哪些已覆盖、本域新增什么"。其余交叉引用：ACE 的**记忆演化角度**与上下文压缩见域 6；优化/结构化所需的**评分与 eval 基建**（评测集、LLM-as-judge、A/B 显著性）见域 9；**输出安全/PII 过滤/越狱**见域 10；策略先行写法已在 `skills/ai-planning-orchestrator/references/prompt-strategy-first.md`（本域引用并增强，不另起炉灶）。

---

## 领域概述

**Prompt 优化与结构化输出**是把"提示词从手艺变成工程"的两条主线。第一条主线**自动 Prompt 优化（Automatic Prompt Optimization, APO）**：不再靠人逐版手调，而是给定一个**评测指标 + 小训练集**，让算法（进化/反思/类梯度/贝叶斯搜索）自动搜出更优的指令与示例。2025-2026 的范式定论是：**自然语言反思比标量奖励是更富信息的学习媒介**——GEPA（ICLR 2026 oral）用"读执行轨迹→自然语言诊断→帕累托进化"在 35× 更少 rollouts 下超过强化学习 GRPO 平均 10pp、超过头号 prompt 优化器 MIPROv2 over 10pp；DSPy 3.0 已把 GEPA/SIMBA/GRPO 收进统一编译器〔web〕。第二条主线**结构化输出（Structured Output）**：从"提示模型尽量输出 JSON"升级为"**解码器在采样层物理上无法吐出违反 schema 的 token**"——OpenAI Structured Outputs(`json_schema`+`strict:true`) 在复杂 schema 上拿到 **100%** 合规（对比 JSON mode 只保证语法合法、不保证结构），Anthropic(`output_config.format`)/Gemini(`response_schema`) 2026 年初已全部 GA，底层都是**受限解码（constrained decoding）**：XGrammar/llguidance 把 JSON Schema 编译成 PDA/CFG，逐 token 算掩码、屏蔽非法分支〔web〕。

这两条主线在工程上由第三层**Prompt 资产管理**串起来：**prompt registry + 版本化 + 运行时 A/B + 可观测**（Langfuse、PromptLayer）让"哪个版本在跑、改了什么、为什么退化"可追溯；**输出契约工程**（Pydantic/Instructor/BAML/Zod）让 LLM 输出像有类型的 API 一样被校验、reask、兜底。一个值得反复强调的纪律是 **"schema 合规 ≠ 语义正确"**：解码层保证字段齐全、类型对、枚举合法，但模型仍可能把 `sentiment` 填错——所以生产做法是**三层防御：生成时强约束（strict/grammar）→ 边界校验（Pydantic/语义断言）→ 分布监控 + reask 兜底**〔web〕。

对「产品专家 Agent」这是**已有半套、缺强约束与自动化**的域。它**已经做对了策略先行**：`prompt-strategy-first.md` 的五步转化（解析策略→映射→六段 Prompt→覆盖率自检→评测迭代）、`prompt-strategy-card-template.md` 的策略→指令映射表、`tuning-report-template.md` 的 **GEPA 式人工失败归因（ASI）+ A/B（p 值/Cohen's d）+ Pareto 取舍**、`prompt-vX.Y.md` 版本约定——这套方法论的"形"与 GEPA/DSPy 高度同构，只是**全靠人手跑**。三个真实缺口：①**自动 Prompt 优化没真正接入**——`/AI调优` 把 GEPA/DSPy 列为"下一步是否引入自动化调优"，但没有可执行的 protocol、没有"何时该上 DSPy/GEPA、指标契约怎么写、产物怎么版本化"的约定；②**结构化输出是"软约束"**——六段 Prompt 的"输出规范"段是"给 schema/范例**提示**模型输出 JSON"，**不是** strict/受限解码强约束，AI 脚本工程化时缺"能用一方 strict/schema 就别靠提示"的硬规定；③**跨能力没有统一 output schema 契约**——五个能力各有结构化产物（策略卡、PRD、评测/调优报告、看板），但没有机器可校验的统一 schema 契约层（Pydantic/Zod 式），产物间的字段一致性靠人肉。下面逐项编目并给落地建议。

---

## SOTA 技术目录

> 按子类分组，共 **58 条**。成熟度：实验 / 成长 / 成熟 / 事实标准。**与 `prompt-engineering-techniques.md` 的关系**：A–C 类是该 22 项手写技巧的"自动化上层"（机器替人调）；D 类是工程化管理层（仓库已有 git 版本化雏形）；E–G 类是该文件"受限生成"一条的**强约束工程实现**（仓库目前是软约束）。

### A. 自动 Prompt 优化 · 框架与编译器（机器替人调，工程级）

| 技术/框架 | 一句话定义 | 何时用 | 成熟度 | 代表实现/论文 | 来源 |
|---|---|---|---|---|---|
| DSPy（声明式编译器） | 把 prompt 写成 **Signature（输入→输出类型）+ Module**，用 optimizer 自动编译出指令与示例；"programming, not prompting" | 多模块 LLM 流水线、想把提示当可优化程序 | 事实标准（研究/前沿生产） | Khattab et al.；`stanfordnlp/dspy` 3.0 | 〔web〕 |
| DSPy BootstrapFewShot | 用 teacher 模型自举生成并筛选少样本示例，编进 prompt | 起步、没把握什么有用时的默认 | 成长 | DSPy optimizer | 〔web〕 |
| DSPy MIPROv2 | 贝叶斯优化在 **指令+示例联合空间**搜索；`auto=light/medium/heavy` 控预算；3.0 加自动超参 | 指令和示例都要一起调、有 200+ 例与算力 | 成长 | DSPy；MIPROv2 (EMNLP 2024) | 〔web〕 |
| DSPy COPRO | 协同优化指令（仅指令、坐标上升式） | 指令看着不对、示例没问题 | 成长 | DSPy optimizer | 〔web〕 |
| **DSPy GEPA** | 反思式遗传-帕累托：读执行轨迹→自然语言诊断失败→变异指令→Pareto 前沿选优；metric 须返回 `Prediction(score, feedback)` | 有强 reflection LM + 可塑反馈的指标；少 rollouts 要大提升 | 成长（快速上升） | Agrawal et al. 2025 (arXiv 2507.19457)，**ICLR 2026 oral** | 〔web〕 |
| DSPy SIMBA | 从自定义反馈学习的强 prompt 优化器（擅长 agentic/长程） | 失败有可命名的共性模式 | 实验 | DSPy 3.0 | 〔web〕 |
| DSPy GRPO（via Arbor） | 在 DSPy 程序上做 RL 权重训练（非纯 prompt） | prompt-only 触顶且模型可调 | 实验 | DSPy 3.0 + Arbor | 〔web〕 |
| DSPy KNNFewShot | 按输入相似度 kNN 动态选示例 | 大训练集、不同输入需不同示例 | 成长 | DSPy optimizer | 〔web〕 |
| DSPy Adapter & Type / BAMLAdapter | 3.0 用 `dspy.Type` 做类型化 I/O、`BAMLAdapter` 做 schema 对齐解析 | 想要类型化结构化输出 + 可扩展适配 | 成长 | DSPy 3.0 | 〔web〕 |
| **GEPA（独立库）** | 同 GEPA 算法，脱离 DSPy 可"优化任意文本组件"（prompt/代码/调度策略/agent 架构） | 不想绑 DSPy、要优化非 prompt 文本系统 | 成长 | `gepa-ai/gepa`（optimize-anything）；50+ 生产用例(Shopify/Comet) | 〔web〕 |

### B. 自动 Prompt 优化 · 研究方法（算法谱系，多为论文/参考实现）

| 技术 | 一句话定义 | 何时用 | 成熟度 | 代表论文/实现 | 来源 |
|---|---|---|---|---|---|
| APE（Automatic Prompt Engineer） | LLM 提议候选指令→另一 LLM 评分→蒙特卡洛搜索选最优；常追平/超过人写 | 单指令零样本任务的自动撰写 | 成长 | Zhou et al. 2022/2023 | 〔web〕 |
| APO / ProTeGi（textual gradients） | 用错分样本生成"伪梯度"（自然语言批评）+ beam search 迭代改 prompt，类比梯度下降 | 有标注小集、想要可解释的定向修改 | 成长 | Pryzant et al. 2023（"Textual Gradients" 出处） | 〔web〕 |
| OPRO（Optimization by PROmpting） | 把"历史 prompt + 其分数"塞进 meta-prompt，让 LLM 当优化器提下一版 | 无梯度、用 LLM 做黑盒优化 | 成长 | Yang et al. 2023（GSM8K 80.2%："深呼吸一步步来"） | 〔web〕 |
| EvoPrompt | 把 LLM 接进进化算法（GA + 差分进化 DE），变异/交叉/差分演化 prompt 种群 | 想要快收敛的离散 prompt 搜索 | 成长 | Guo et al. ICLR 2024（BBH 最高 +25%） | 〔web〕 |
| PromptBreeder | 自指改进：同时进化**任务 prompt 与变异 prompt**（hypermutation）+ Lamarckian 逆推 | 要自演化、跳出局部最优 | 实验 | Fernando et al. ICML 2024（GSM8K 零样本 83.9%） | 〔web〕 |
| TextGrad | 文本版自动微分：把系统建成计算图，LLM 反向传播"文本梯度"（自然语言批评）优化变量 | 用 PyTorch 式 API 优化 prompt/代码/方案 | 成长 | Yuksekgonul et al. 2025（**Nature** vol 639）；`zou-group/textgrad` | 〔web〕 |
| PromptWizard | 任务感知流水线：迭代改进 + 少样本合成/筛选 + 专家人设统一风格 | 要一条龙自动产出可用 prompt | 成长 | Agarwal et al. 2024（微软） | 〔web〕 |
| AutoPrompt | 基于梯度的离散触发词搜索（早期奠基，针对 MLM） | 研究/历史脉络参照 | 成长（奠基） | Shin et al. 2020 | 〔知识〕 |
| **ACE（Agentic Context Engineering）** | 把上下文当"演化 playbook"：Generator/Reflector/Curator + **增量 delta**，防 brevity bias / context collapse；离线优化系统 prompt、在线优化 agent 记忆 | prompt + 记忆一体的自进化（北极星，交叉域 6） | 实验 | Stanford/SambaNova/UCB 2025 (arXiv 2510.04618)；+10.6% agent/+8.6% finance | 〔web〕 |
| Dynamic Cheatsheet | 测试时学习：维护可复用"备忘单"外部记忆，累积成功/失败策略，无需标注 | 推理时自适应、跨题复用策略 | 实验 | Suzgun et al. 2025 (arXiv 2504.07952)；ACE 前作（Gen-Curator） | 〔web〕 |

### C. few-shot 示例选择（自动选/排示例，喂给上面或直接用）

| 技术 | 一句话定义 | 何时用 | 成熟度 | 代表实现/论文 | 来源 |
|---|---|---|---|---|---|
| kNN/相似度检索选例 | 用句向量(Sentence-BERT)余弦相似度取最像测试样本的示例 | 最常用基线、有示例库时 | 成熟 | Liu et al. 2022；DSPy KNNFewShot | 〔web〕 |
| 多样性/子模选择 | 平衡相关性与多样性（子模优化）选覆盖广、低冗余的子集；最优维度(相似 vs 多样)随任务变 | 纯相似度产生冗余误导集时 | 成长 | ICL 选例文献（2024 综述） | 〔web〕 |
| IDS 迭代示例选择 | 先对测试样本跑 Zero-shot-CoT，用推理路径迭代选"既多样又强相关"的示例 + 多数投票 | 推理/QA/分类，单维选择不够时 | 实验 | Iterative Demonstration Selection (EMNLP 2024) | 〔web〕 |
| RAG few-shot / 动态示例库 | 把"成功 input→output"存库，运行时按当前输入检索注入（情景记忆即few-shot） | 任务多样、想随用随取最贴例 | 成长 | LangMem few-shot；DSPy；交叉域 6 | 〔web〕 |
| 示例排序 / 位置偏差 | 示例顺序敏感：同一组示例从 prompt 头移到尾可摆动准确率达 ~20%、翻转近半预测（DPP/positional bias） | 排示例、决定放开头还是结尾 | 成长 | "Where to show Demos" EMNLP 2025；Lu et al. 2022 | 〔web〕 |
| 标签/近因偏差校准 | 缓解 majority-label / recency / common-token 偏差（如 contextual calibration） | 分类类 ICL 输出抖动 | 成长 | Zhao et al. 2021；Fei et al. 2023 | 〔web〕 |

### D. Prompt 管理 / 版本化 / 工程化（提示作为受治理资产）

| 技术/平台 | 一句话定义 | 何时用 | 成熟度 | 代表实现/产品 | 来源 |
|---|---|---|---|---|---|
| git-based prompt 版本化 | prompt 当代码版本化（`prompt-vX.Y`），diff/回滚/评审 | 轻量、单仓库、人审流程 | 事实标准 | **本仓库已有** `prompt-vX.Y.md` 约定 | 〔本地〕 |
| Prompt Registry（与代码解耦） | prompt 存"注册表"，按 name+version/label 取用，不重新部署即可改 | 提示频改、非技术同事参与 | 成长 | PromptLayer Registry；Langfuse Prompts | 〔web〕 |
| Langfuse Prompts | OSS(MIT) prompt 版本化 + registry + 运行时 A/B(label) + 追踪/评测/数据集一体 | 要 prompt 管理 + 可观测 + eval 同栈 | 成熟 | Langfuse（2026-01 被 ClickHouse 收购） | 〔web〕 |
| PromptLayer | 日志优先：自动记录每次调用、registry + Dynamic Release Labels 路由版本 | 轻量、重日志与协作、快速迭代 | 成熟 | PromptLayer | 〔web〕 |
| LangSmith / Humanloop / Maxim | LangChain 生态追踪 + 评测 / 人反馈闭环 / 全生命周期实验 | 已用对应生态 | 成熟 | LangSmith、Humanloop、Maxim AI | 〔web〕 |
| 运行时 A/B / canary | 给版本打 `prod-a`/`prod-b` 标签随机分流，按延迟/成本/质量分对比；金丝雀小流量先行 | 数据集测过、想线上小流量验证 | 成长 | Langfuse A/B；PromptLayer Labels | 〔web〕 |
| 模板系统（变量化） | 把可复用 prompt 抽成模板 + 变量（Jinja2 式），规模化与一致性 | 多场景复用同一骨架 | 成熟 | **本仓库已有**（prompt-engineering-techniques #3） | 〔本地〕 |
| Prompt 评测集挂钩版本 | 每个 prompt 版本绑评测集跑分，版本切换可回溯到分数（交叉域 9） | 想让"版本→质量"可追溯 | 成长 | Langfuse Experiments/Datasets | 〔web〕 |

### E. 结构化输出 · 一方 API（Provider-native，能用就别靠提示）

| 技术 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **OpenAI Structured Outputs** | `response_format:{type:"json_schema",strict:true}`，CFG 引擎在采样层强制，复杂 schema **100%** 合规 | 任何要可靠 schema 的 OpenAI 调用（2026 默认） | 事实标准 | gpt-4o-2024-08-06+（100% vs gpt-4-0613 <40%）；SDK 直接吃 Pydantic/Zod | 〔web〕 |
| OpenAI JSON mode（遗留） | `json_object` 只保证**语法**合法 JSON，不保证结构 | 老模型或写不出 schema 时 | 成熟（遗留） | OpenAI（2023.11，2026 已"legacy"） | 〔web〕 |
| Anthropic Structured Outputs | `output_config.format`(type=json_schema) 约束响应为合 schema 的 JSON | Claude 要确定 JSON 结构 | 成熟 | GA 2026-02（Sonnet/Opus/Haiku 4.5；原 beta `output_format`） | 〔web〕 |
| Anthropic strict tool use | 工具定义加 `strict:true` → 语法约束采样，保证工具入参合 `input_schema` | agentic 要类型安全函数调用 | 成熟 | Claude 平台 / Bedrock / Vertex | 〔web〕 |
| Gemini structured output | `response_schema` + `responseMimeType:"application/json"`；2025 起支持 anyOf/$ref/enum、保留字段顺序 | Gemini 要 schema 级约束 | 成熟 | Gemini 2.5/3.x；86% 经验覆盖、支持 schema 100% 合规 | 〔web〕 |
| Function/Tool calling 取 JSON | 用函数调用的参数 schema 间接拿结构化对象（早于专门 SO） | 既要结构又要触发外部动作 | 事实标准 | OpenAI/Anthropic/Gemini 通用 | 〔web〕 |

### F. 受限/约束解码（Constrained Decoding，开源推理层引擎）

| 技术 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| XGrammar | 把 CFG/JSON Schema 编成下推自动机(PDA)，批量约束解码、语法缓存复用；~40µs/token | 自托管模型默认首选、长生成 | 成熟 | `mlc-ai/xgrammar`；**vLLM & SGLang 默认**；MLSys 2025，100× 提速 | 〔web〕 |
| llguidance / guidance | Rust，逐 token 即时算掩码(~50µs)、几乎零启动；擅长动态/多租户、复杂交错 | 复杂 grammar、要低 TTFT | 成熟 | `guidance-ai/llguidance`；**现为 OpenAI 结构化输出引擎底座**（微软） | 〔web〕 |
| Outlines | 由约束建有限状态机(FSM)、预算所有状态的 token 掩码 | 通用约束生成 | 成长 | `dottxt-ai/outlines`；vLLM 后端之一（Outlines Core 进行中） | 〔web〕 |
| lm-format-enforcer | JSON Schema/正则约束，但**允许模型控制空白/字段顺序/可选**（减少分布扭曲）；支持批量/beam | 在意输出质量、要可选字段 | 成长 | `noamgat/lm-format-enforcer`（需 logit 访问，不适用 API 模型） | 〔web〕 |
| jsonformer | 逐字段生成：结构 token(括号/逗号)由程序填，仅"值"交给模型 | 简单扁平 schema | 成长（受限） | `1rgs/jsonformer`（嵌套/anyOf 弱） | 〔web〕 |
| LMQL | 查询级 DSL，把生成与约束(where 子句)混写 | 要在一段里混合生成+约束逻辑 | 成长 | LMQL | 〔知识〕 |
| GBNF 语法（llama.cpp） | 用 GBNF（BNF 变体）定义文法约束本地模型输出 | llama.cpp 本地推理 | 成熟 | llama.cpp grammars | 〔web〕 |
| SynCode | 文法约束解码，面向编程语言/形式语法（CFG + 增量解析） | 生成代码/SQL 等需合法语法 | 实验 | SynCode（论文/库） | 〔知识〕 |
| vLLM guided decoding / structural_tag | vLLM 统一入口：`guided_json/regex/choice/grammar`，auto 选后端；`structural_tag` 在标签内约束 | 自托管 serving 要结构化 | 成熟 | vLLM（≥0.8.5；xgrammar 默认，回退 outlines） | 〔web〕 |

### G. 输出契约工程 + 可靠性（类型化契约、reask、兜底）

| 技术 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Pydantic（schema 即契约） | 用 Python 类型类定义输出 schema，自动校验/解析；几乎所有 SO 库的底座 | 任何 Python 侧结构化输出 | 事实标准 | Pydantic v2 | 〔web〕 |
| Instructor | patch 客户端，`response_model=` 直接拿校验过的对象，校验失败**自动 reask**（把错误回喂）、流式 partial | 想"定义模型就拿结构化数据" | 成熟 | `567-labs/instructor` v1.15（Py/TS/Go/Ruby/Rust，15+ provider） | 〔web〕 |
| PydanticAI | Pydantic 团队官方 agent 运行时：类型化工具 + 可回放数据集 + evals + 看板 | 需要 agent 而非纯抽取 | 成长 | `ai.pydantic.dev` | 〔web〕 |
| BAML | 用 DSL 定义函数/schema，编译多语言客户端 + **schema-aligned parsing**（容错解析+重试） | 想要强类型、跨语言、抗脏输出 | 成长 | BoundaryML BAML；DSPy 3.0 收 BAMLAdapter | 〔web〕 |
| Zod / TypeChat | TS 侧 schema 校验(Zod) / 用 TS 类型生成约束并校验修复(TypeChat) | TS/前端栈结构化输出 | 事实标准(Zod)/成长(TypeChat) | Zod；microsoft/TypeChat | 〔知识〕 |
| reask/retry 循环 | 校验失败把错误信息回喂模型重试（Tenacity 退避，`max_retries`） | 软约束/自校验失败要自愈 | 成熟 | Instructor max_retries；通用模式 | 〔web〕 |
| schema 自校验 + 语义断言 | 生成后用 Pydantic/断言做边界校验：**schema 合规≠语义正确**，叠加业务断言 | 字段对但值可能错（30%）时 | 成长 | "JSON mode is not a contract" 三层防御 | 〔web〕 |
| 解析失败兜底 / refusal 处理 | 把 refusal 当一等错误、解析失败有降级路径（默认值/转人工/换软约束） | 生产健壮性 | 成长 | OpenAI refusal 字段；生产实践 | 〔web〕 |
| 分布漂移监控 | 监控输出分布，模型更新会无声改变分布，需事故 playbook | 长期生产、模型常更新 | 成长 | 生产可靠性实践（交叉域 9） | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **"自然语言反思 > 标量奖励"成为 Prompt 优化新范式。**〔web〕 GEPA（ICLR 2026 oral）论证：让 LLM **读完整执行轨迹（推理/工具调用/报错）做自然语言诊断**，比从稀疏标量奖励学更高效——跨任务超 RL 的 GRPO 平均 6–10pp、最高 19pp，且用 **35× 更少 rollouts**（100–500 次 vs 5,000–25,000+）；超头号优化器 MIPROv2 over 10pp（AIME-2025 +12pp）。这与本仓库 `tuning-report-template.md` 的"失败归因 ASI + 一般化修法"完全同构——**我们手做的正是 GEPA 的人肉版**。

2. **DSPy 3.0 把"提示优化"沉淀为统一编译器栈。**〔web〕 3.0 收齐 GEPA（反思进化）、SIMBA（自定义反馈）、GRPO（RL via Arbor）、MIPROv2（贝叶斯，加自动超参）、`dspy.Type`/Adapter/BAMLAdapter（类型化 I/O）、MLflow 3.0 可观测——"programming, not prompting" 从理念变成可生产工具链。选型口诀已成熟：指令不对用 COPRO/GEPA、都弱有预算用 MIPROv2/GEPA、agent/工具任务用 GEPA。

3. **结构化输出从"提示"升级为"解码层物理强制"，且已是各厂一方能力。**〔web〕 OpenAI(`strict:true`)、Anthropic(`output_config.format`，2026-02 GA)、Gemini(`response_schema`) 全部到位，底层都是受限解码：**采样层屏蔽违反 schema 的 token**，OpenAI 复杂 schema 合规从 gpt-4-0613 <40% 提到 **100%**。结论：**"能用一方 strict/schema 就别靠提示让模型输出 JSON"**。

4. **受限解码引擎收敛到 XGrammar/llguidance 两强。**〔web〕 XGrammar（PDA + 语法缓存，~40µs/token）成为 **vLLM 与 SGLang 默认**、MLSys 2025 提速 100×；llguidance（Rust，即时算掩码~50µs、零启动）**已成为 OpenAI 结构化输出引擎底座**（微软）。Outlines（FSM 预算掩码）因启动开销退居其次。自托管选 XGrammar、要复杂交错选 guidance。

5. **"schema 合规 ≠ 语义正确"成为生产铁律，催生三层防御。**〔web〕 完美 schema 强制仍可能 30% 答错（如 `{"sentiment":"positive"}` 语法/类型/枚举全对但判断错）。生产共识：**Layer1 生成时强约束（strict/grammar）→ Layer2 边界校验（Pydantic/语义断言）→ Layer3 分布监控 + reask 兜底**；强约束是"一下午就能落地的便宜部分"，难的是语义校验层与漂移事故 playbook。

6. **输出契约工程标准化：Pydantic/Zod 为底，Instructor/BAML 加 reask。**〔web〕 Instructor（v1.15，多语言、15+ provider）把"定义 Pydantic 模型 → 拿校验过的对象 + 校验失败自动 reask（错误回喂）"做成默认；BAML 的 **schema-aligned parsing** 容错解析脏 JSON 并重试；DSPy 3.0 直接收 BAMLAdapter。LLM 输出正被当"有类型的 API"对待。

7. **Prompt 资产管理工业化：registry + 运行时 A/B + 版本绑评测。**〔web〕 Langfuse（OSS，2026-01 被 ClickHouse 收购）、PromptLayer 把 prompt 从代码里拆出来——按 name+version/label 取用、不重新部署即可改、`prod-a/prod-b` 标签随机分流并按延迟/成本/质量对比、版本绑评测集可追溯"哪个版本在跑、改了什么、为什么退化"。本仓库 `prompt-vX.Y.md` 是其轻量人审版。

8. **自进化上下文（ACE/Dynamic Cheatsheet）把"Prompt 优化"与"记忆"打通。**〔web〕 ACE（arXiv 2510.04618）用 Generator/Reflector/Curator + **增量 delta** 把上下文当"演化 playbook"，离线优化系统 prompt、在线优化 agent 记忆，靠执行反馈无需标注即 +10.6%/+8.6%，且专治 **brevity bias / context collapse**（整篇重写会丢细节）——这恰是 `/经验写回`"全量重写文档"的病根（交叉域 6）。

9. **few-shot 从"静态精选"转向"动态检索 + 位置感知"。**〔web〕 共识：kNN 相似度选例是基线但易冗余误导，最优维度（相似 vs 多样）随任务变，子模/迭代(IDS)选例更稳；**示例顺序是一等变量**——同一组示例从头移到尾可摆动准确率 ~20%、翻转近半预测（EMNLP 2025 DPP bias）。落到本仓库：少样本"放末尾（近因）"的直觉对，但要把示例选择/排序当可测变量。

10. **GEPA 式自动优化正在企业级落地、降本显著。**〔web〕 `gepa-ai/gepa`（optimize-anything）报告 50+ 生产用例（Shopify、Comet ML 等）；Databricks 用开源模型 + 自动 prompt 优化"90× 更便宜"地打平 Claude Opus 4.1；GEPA 还把 ARC-AGI agent 32%→89%、编码 agent 在 Jinja 任务 55%→82%。自动优化已从论文走向"省钱的工程手段"。

---

## 对标产品专家 Agent

> 核心命题：本仓库 **已做对策略先行 + 人工迭代闭环**（`prompt-strategy-first.md` 五步、`prompt-strategy-card-template.md`、`tuning-report-template.md` 的 ASI+A/B+Pareto、`prompt-vX.Y.md` 版本约定）——这套"形"与 GEPA/DSPy 同构，但**全靠人手跑**。三个缺口对应三层：①自动优化没接入、②结构化输出是软约束、③无统一 output schema 契约。下面逐项"现状→差距→增强(P0/P1/P2)"，点名具体文件。
>
> **先划清"已覆盖 vs 本域新增"**：`prompt-engineering-techniques.md` 已覆盖 **手写技巧层**（零样本/少样本/CoT/角色/受限生成/模板变量/A-B/有效性评估等 22 项）；`prompt-strategy-first.md` 已覆盖 **策略→指令翻译 + 覆盖率自检 + 人工迭代**。本域**新增三层**：自动 Prompt 优化（DSPy/GEPA 真正接入的 protocol）、结构化输出**强约束**（strict/schema/受限解码，而非"提示输出 JSON"）、**跨能力统一 output schema 契约**（Pydantic/Zod 式机器可校验）。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `/AI调优` 用 `tuning-report-template.md` 做**人工**失败归因(ASI)+A/B(p/d)+Pareto，方法论第 5 节标"GEPA 式" | **GEPA/DSPy 只是"形似"未真接入**：报告第 7 节把"是否引入自动化调优 GEPA/DSPy"列为下一步，但**无可执行 protocol**——何时该上、指标契约(score+feedback)怎么写、产物怎么版本化都没定 | **P1**：新增 `policies/prompt-optimization-protocol.md`，定义"人工调优触顶/评测集≥N 时升级到 DSPy GEPA"的判据 + **指标契约**（metric 返回 `score+feedback`，feedback 即 ASI 归因）+ 产物落 `prompt-vX.Y` |
| 六段 Prompt 的"输出规范"段=给 schema/范例**提示**模型输出 JSON（`prompt-strategy-first.md` Step3、`prompt-strategy-card-template.md` §3） | **结构化输出是软约束**：靠提示≠受限解码；AI 脚本工程化(`/AI脚本`)缺"能用一方 strict/`json_schema` 就别靠提示"的硬规定，易出 schema 漂移 | **P0**：在 `prompt-engineering-techniques.md` + `ai-service-construction.md` 立**结构化输出强约束 protocol**："能用一方 strict/schema 就别靠提示；不能则 Pydantic/Zod 校验 + reask 兜底"，给三层防御决策树 |
| 五能力各有结构化产物：策略卡/PRD/评测报告/调优报告/看板（assets/*.md 模板） | **无统一 output schema 契约**：产物字段一致性靠人肉模板，机器无法校验"这份调优报告字段齐不齐、回溯到策略卡哪条" | **P1**：为关键产物定 **schema 契约**（先 JSON Schema/Pydantic 描述，模板加机器可校验标记），`tests/` 断言产物含必填段；交叉域 9 评测产物对齐 |
| `prompt-engineering-techniques.md` #5 "范例选择质量>数量"、#3 模板变量 | **few-shot 选择/排序未工程化**：靠人选 1-3 例、未提"动态检索选例"与"位置/近因偏差"是可测变量 | **P2**：在 `prompt-engineering-techniques.md` 少样本节补"**动态示例库(RAG few-shot)** + 选例(kNN/多样性) + 排序(近因，示例放末尾)"，与域 6 记忆 few-shot 打通 |
| `prompt-vX.Y.md` git 版本化 + `/AI调优` A/B（`tuning-report-template.md` §4） | **无 prompt registry / 运行时 A/B / 版本绑评测**（多属平台层）：版本与评测分数未机器化绑定，A/B 是离线人跑 | **P2**（部分平台层）：约定 prompt 版本**绑评测集分数**写回（version→score 可追溯）；registry/运行时 A/B 记为备忘（Langfuse/PromptLayer，需基建） |
| `tuning-report-template.md` 已要求"新增失败回放用例写回评测集" | **未升级为 ACE 式增量演化**：写回是"整篇重写"易 brevity bias/context collapse（与域 6 同源缺口） | **P2**（北极星，交叉域 6/9）：把 `/经验写回` 升级为 **ACE 三角色 + 增量 delta + helpful/harmful 计数**，待域 9 eval 基建就位 |
| Prompt 合同/系统提示靠人写六段（`execution-sop.md` Step4） | **无 schema-first 抗脏输出解析**：解析失败无标准 reask/兜底约定 | **P1**：结构化输出 protocol 内含 **reask/兜底标准**（校验失败回喂错误重试 ≤N 次→降级默认值/转人工），对齐 Instructor 模式 |

---

## 落地建议

> 原则：与本仓库"Cursor 原生、轻量聚焦、policy/rule/protocol 文件化、不引入重运行时"一致。**不要求真的 pip 装 DSPy 跑编译**（那是 AI 脚本工程化产物侧的可选项），而是把**方法论与硬规定文件化**——让 Agent 写 `/AIPRD`、`/AI脚本`、`/AI调优` 时**默认走强约束 + 可升级到自动优化**。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 结构化输出强约束 protocol（最高优先：把"软约束"改成"强约束"）
- **放哪**：`policies/prompt-engineering-techniques.md` 新增"结构化输出强约束"小节（升级 #8 受限生成）+ `skills/ai-planning-orchestrator/references/ai-service-construction.md` 的输出契约段。
- **做什么**：立**决策树**——①能用模型一方能力（OpenAI `json_schema`+`strict:true` / Anthropic `output_config.format` / Gemini `response_schema` / 工具 `strict`）→**首选，禁止只靠提示**；②自托管模型→受限解码（XGrammar/llguidance/Outlines，vLLM `guided_json`）；③都不行（如 Cursor 内纯提示场景）→ **Pydantic/Zod 定 schema + 校验 + reask 兜底**。写明铁律"**能 strict/schema 就别靠提示输出 JSON**"与"**schema 合规 ≠ 语义正确**，必叠加语义断言"。
- **验收信号**：`tests/test_product_expert_agent.py` 断言 `prompt-engineering-techniques.md` 含标记 `结构化输出强约束`/`strict`/`受限解码`/`schema 合规≠语义正确`；`/AI脚本` 产出的 Prompt 合同输出段标注"约束级别：一方 strict / 受限解码 / 提示+校验 reask"三选一。

### P0-2 输出契约工程 + reask 兜底约定（强约束落不到时的健壮兜底）
- **放哪**：`ai-service-construction.md` + `prompt-strategy-card-template.md` §3"输出规范"段升级。
- **做什么**：约定**契约即 schema**——结构化产物先用 Pydantic（Py）/Zod（TS）/JSON Schema 描述，再生成；运行时 **校验失败→把错误回喂 reask（≤3 次，Tenacity 退避）→仍失败降级（默认值/转人工/换软约束）**；`refusal`/拒答当一等错误处理。给最小代码骨架（Instructor `response_model`+`max_retries` 思路，不绑死库）。
- **验收信号**：策略卡 §3 模板出现"schema 定义（Pydantic/Zod/JSON Schema）"+"reask 上限"+"兜底路径"三字段；契约测试断言模板含 `reask`/`兜底`/`schema` 标记。

### P1-1 自动 Prompt 优化 protocol（把 GEPA/DSPy 从"形似"变"可执行升级路径"）
- **放哪**：新增 `policies/prompt-optimization-protocol.md`；`tuning-report-template.md` 第 7 节"是否引入自动化调优"链到它；`llm-eval-methodology.md` 第 5 节交叉引用。
- **做什么**：定 **升级判据 + 指标契约 + 产物约定**。判据：人工调优"≤5 轮未收敛 / 评测集 ≥ N 例 / 同类 prompt 反复调"→升级到 DSPy `GEPA`（首选，少 rollouts）或 `MIPROv2`（指令+示例都要调、例多）。**指标契约**：metric 必须返回 `score(float) + feedback(str)`——**feedback 直接复用 `tuning-report-template.md` 的 ASI 失败归因**（这是我们已有资产到 GEPA 的天然接口！）。产物：优化后 prompt 落 `prompt-vX.Y`，附"自动优化器/预算/前后 A/B"。给"GEPA vs MIPROv2 vs 仅人工"的选型表。
- **验收信号**：`prompt-optimization-protocol.md` 存在且含 `GEPA`/`MIPROv2`/`score+feedback 指标契约`/`升级判据`；`tuning-report-template.md` 第 7 节出现指向它的链接 + "metric feedback = ASI 归因"一句。

### P1-2 统一 output schema 契约（跨能力产物机器可校验）
- **放哪**：新增 `policies/output-contract.md`（或并入 `submission-review-contract.md`）；各 skill 的 `assets/*.md` 模板加机器可校验标记。
- **做什么**：为关键交付物（策略卡、AI PRD、评测报告、调优报告）各定一份 **schema 契约**（JSON Schema/Pydantic 描述必填段与字段类型 + 跨产物引用如"调优报告.回溯规则 → 策略卡.规则编号"）。模板里用稳定锚点标记（如 `<!-- schema: tuning-report v1 -->` + 必填 `##` 段），让 `tests/` 能断言。
- **验收信号**：`output-contract.md` 存在且列出 4 类产物 schema；`tests/` 对每类产物断言"必填段齐 + 关键字段非空 + 跨引用编号能对上"。

### P1-3 reask/解析健壮性纳入脚本工程化门禁
- **放哪**：`ai-service-construction.md` 的"输出可靠性"小节 + `developer-handoff.md`。
- **做什么**：AI 脚本交接时，输出解析必须有"**强约束级别声明 + 校验 + reask + 兜底 + 分布漂移备忘**"五项；把"schema 合规率""解析失败率"纳入 `/AI评测` 指标（交叉域 9）。
- **验收信号**：交接文档模板含上述五项 checklist；评测报告模板（`eval-report-template.md`）出现"格式合规率/解析失败率"指标行。

### P2-1 few-shot 选择/排序工程化（动态示例库 + 位置感知）
- **放哪**：`prompt-engineering-techniques.md` 少样本节（#5）补充。
- **做什么**：补"**动态示例库（RAG few-shot）**：把成功 input→output 存库按当前输入检索注入（与域 6 claude-mem 情景记忆打通）；**选例**用 kNN 相似度 + 兼顾多样性；**排序**利用近因——最具代表性示例放末尾（与 P3 位置布局一致）；警惕示例顺序可摆动准确率 ~20%"。
- **验收信号**：少样本节出现 `动态示例库/RAG few-shot`、`选例(相似+多样)`、`排序(近因)` 三标记；与 `memory-protocol`（域 6）交叉引用。

### P2-2 Prompt 版本绑评测 + 运行时 A/B（registry，多属平台层）
- **放哪**：`prompt-optimization-protocol.md` 的"版本与评测"小节 + 备忘 `prompt-vX.Y` 约定升级。
- **做什么**：约定每个 `prompt-vX.Y` **绑定其评测集分数**（version→score 可追溯，写进版本头）；registry/运行时 A/B（Langfuse/PromptLayer 的 label 分流）记为**可选平台基建**，不强求落地（与 Cursor 原生定位权衡）。
- **验收信号**：`prompt-vX.Y.md` 版本头模板含"评测集/总达标率/对比上一版"字段；protocol 标注 registry 为 P2 备忘。

### P2-3 ACE 式演化写回（北极星，交叉域 6/9）
- **放哪**：`submission-review-contract.md` + `agent-team-methodology.md` 自我进化部分（与域 6 P2-2 **同一条**，此处从 prompt 优化角度强化）。
- **做什么**：把 `/经验写回` 从"整篇重写"升级为 **ACE 三角色（Generator/Reflector/Curator）+ 增量 delta + helpful/harmful 计数**，避免 brevity bias/context collapse；写回的 prompt/policy 改动要带"带/不带该改动的 With-skill vs Baseline 量化对比"（对齐 `agent-team-methodology` 第三部分 + `llm-eval-methodology` 七段闭环）。
- **验收信号**：写回 PR 模板要求"增量 delta（非整篇重写）+ helpful/harmful 计数 + With-skill vs Baseline 量化"；纳入合并门槛。

---

## 参考来源

**自动 Prompt 优化 · 框架/编译器**
- 〔web〕DSPy 3.0.0 Release（GEPA/SIMBA/GRPO via Arbor、`dspy.Type`/Adapter/BAMLAdapter、MLflow 3.0）— https://github.com/stanfordnlp/dspy/releases/tag/3.0.0
- 〔web〕DSPy《Optimizers: choosing one》（选型表：BootstrapFewShot/KNNFewShot/COPRO/MIPROv2/GEPA/SIMBA…）— https://dspy.ai/diving-deeper/choosing-an-optimizer/
- 〔web〕DSPy《GEPA in depth》+《GEPA Overview》（`Prediction(score, feedback)` 指标契约、reflection_lm、Pareto vs current_best）— https://dspy.ai/diving-deeper/gepa-in-depth/ ；https://dspy.ai/api/optimizers/GEPA/overview/
- 〔web〕GEPA 论文《Reflective Prompt Evolution Can Outperform Reinforcement Learning》Agrawal et al. 2025（arXiv 2507.19457，**ICLR 2026 oral**；超 GRPO 6–10pp/最高 19–20pp、35× 更少 rollouts；超 MIPROv2 >10pp、AIME-2025 +12pp）— https://arxiv.org/abs/2507.19457 ；https://openreview.net/forum?id=RQm2KQTM5r
- 〔web〕GEPA 库（optimize-anything；90× cheaper@Databricks、ARC-AGI 32%→89%、编码 agent 55%→82%、50+ 生产用例）— https://github.com/gepa-ai/gepa ；https://www.morphllm.com/gepa-prompt-optimization
- 〔web〕Databricks《Building SOTA Enterprise Agents 90x Cheaper with Automated Prompt Optimization》— https://www.databricks.com/blog/building-state-art-enterprise-agents-90x-cheaper-automated-prompt-optimization

**自动 Prompt 优化 · 研究方法**
- 〔web〕APO 综述《A Systematic Survey of Automatic Prompt Optimization Techniques》— https://arxiv.org/html/2502.16923v2 ；《APO with Instruction-focused Heuristic-based Search》— https://arxiv.org/html/2502.18746v2
- 〔web〕Cameron Wolfe《Automatic Prompt Optimization》（APE/APO-ProTeGi/EvoPrompt/PromptBreeder 综述）— https://cameronrwolfe.substack.com/p/automatic-prompt-optimization
- 〔web〕EvoPrompt（连接 LLM 与进化算法 GA+DE，BBH +25%）Guo et al. ICLR 2024 — https://github.com/beeevita/EvoPrompt
- 〔web〕PromptBreeder（自指演化任务/变异 prompt，GSM8K 零样本 83.9%）Fernando et al. ICML 2024 — https://openreview.net/pdf?id=9ZxnPZGmPU
- 〔web〕OPRO（"Take a deep breath…" GSM8K 80.2%）Yang et al. 2023；APE Zhou et al.；APO/ProTeGi Pryzant et al. 2023（"Textual Gradients" 出处）；PromptWizard 微软 Agarwal et al. 2024（均见上述综述）
- 〔web〕TextGrad《Automatic "Differentiation" via Text》Yuksekgonul et al. 2025（**Nature** vol 639；PyTorch 式文本反向传播）— https://github.com/zou-group/textgrad ；https://arxiv.org/html/2406.07496v1
- 〔知识〕AutoPrompt（梯度离散触发词搜索）Shin et al. 2020（奠基，针对 MLM）
- 〔web〕ACE《Agentic Context Engineering》Stanford/SambaNova/UCB 2025（arXiv 2510.04618；Generator/Reflector/Curator + 增量 delta；+10.6%/+8.6%；AppWorld）— https://arxiv.org/pdf/2510.04618 ；https://openreview.net/forum?id=eC4ygDs02R ；https://sambanova.ai/blog/ace-open-sourced-on-github
- 〔web〕Dynamic Cheatsheet（测试时学习、自适应外部记忆）Suzgun et al. 2025（arXiv 2504.07952）

**few-shot 示例选择/排序**
- 〔web〕《In-Context Learning with Iterative Demonstration Selection (IDS)》EMNLP 2024（相似 vs 多样任务相关、Zero-shot-CoT 迭代选例）— https://aclanthology.org/2024.findings-emnlp.438.pdf
- 〔web〕《Where to show Demos in Your Prompt: A Positional Bias of ICL》EMNLP 2025（DPP bias：移示例块摆动准确率 ~20%、翻转近半预测）— https://aclanthology.org/2025.emnlp-main.1503.pdf
- 〔web〕《Sequential Example Selection for ICL》ACL 2024 — https://aclanthology.org/2024.findings-acl.312.pdf ；《ICL of Length Biases》（majority/recency/common-token 偏差综述引）— https://arxiv.org/html/2502.06653v1
- 〔知识〕kNN 选例 Liu et al. 2022《What Makes Good In-Context Examples for GPT-3?》；Contextual Calibration（标签偏差）Zhao et al. 2021

**结构化输出 · 一方 API**
- 〔web〕OpenAI《Introducing Structured Outputs in the API》（`json_schema`+`strict:true`，CFG 引擎采样层强制；gpt-4o-2024-08-06 100% vs gpt-4-0613 <40%）— https://openai.com/index/introducing-structured-outputs-in-the-api ；指南 https://developers.openai.com/api/docs/guides/structured-outputs
- 〔web〕OpenAI Structured Outputs vs JSON mode（2026 默认 strict、JSON mode legacy）— https://www.respan.ai/articles/openai-structured-outputs-vs-json-mode ；https://www.digitalapplied.com/blog/openai-structured-outputs-complete-guide
- 〔web〕Anthropic《Structured outputs》（`output_config.format` + strict tool use；2026-02 GA，原 beta `structured-outputs-2025-11-13`/`output_format`）— https://platform.claude.com/docs/en/build-with-claude/structured-outputs ；https://claude.com/blog/structured-outputs-on-the-claude-developer-platform
- 〔web〕Gemini《Structured outputs》（`response_schema`+`responseMimeType`；anyOf/$ref/enum、保留字段顺序）— https://ai.google.dev/gemini-api/docs/structured-output ；JSON Schema Leaderboard（Gemini responseSchema 86% 覆盖/100% 合规）— https://awesomeagents.ai/leaderboards/structured-output-json-leaderboard/

**受限/约束解码**
- 〔web〕vLLM《Structured Outputs》（`guided_json/regex/choice/grammar`、xgrammar 默认回退 outlines、structural_tag）— https://docs.vllm.ai/en/latest/features/structured_outputs/ ；vLLM Blog《Structured Decoding: a gentle introduction》（XGrammar PDA、5× TPOT）— https://vllm.ai/blog/2025-01-14-struct-decode-intro
- 〔web〕XGrammar（PDA/GBNF、vLLM&SGLang 默认、MLSys 2025 100×）— https://github.com/mlc-ai/xgrammar ；Red Hat《Structured outputs in vLLM》— https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses
- 〔web〕llguidance（Rust ~50µs 即时掩码、零启动；**现为 OpenAI 结构化输出引擎底座**；2025-03 并入 vLLM v0.8.2）— https://github.com/guidance-ai/llguidance
- 〔web〕lm-format-enforcer（允许模型控制空白/字段顺序/可选、批量/beam）— https://github.com/noamgat/lm-format-enforcer ；Outlines — https://github.com/dottxt-ai/outlines ；jsonformer — https://github.com/1rgs/jsonformer
- 〔web〕《Structured Output and Constrained Decoding for Production AI Agents (2026)》（XGrammar/llguidance/Outlines 横评、三层模型）— https://zylos.ai/research/2026-04-11-structured-output-constrained-decoding-production-agents-2026
- 〔知识〕LMQL（查询级 DSL 混写生成+约束）；SynCode（编程语言文法约束解码）；llama.cpp GBNF grammars

**输出契约工程 + 可靠性**
- 〔web〕Instructor（Pydantic + `response_model` + `max_retries` 自动 reask、流式 partial、多语言/15+ provider，v1.15）— https://python.useinstructor.com/ ；https://github.com/567-labs/instructor ；reask 文档 — https://github.com/jxnl/instructor/blob/main/docs/concepts/reask_validation.md
- 〔web〕PydanticAI（官方 agent 运行时，类型化工具+评测+看板）— https://ai.pydantic.dev/ ；BAML（schema-aligned parsing，DSPy 3.0 BAMLAdapter）— BoundaryML
- 〔web〕《Structured Output Reliability in Production: Why JSON Mode Is Not a Contract》（**schema 合规≠正确**、三层防御、reask、分布漂移 playbook）— https://tianpan.co/blog/2026-04-20-structured-output-reliability-production ；https://stochasticsandbox.com/posts/structured-output-from-llms-2026-05-05/
- 〔知识〕Pydantic v2 ；Zod ；microsoft/TypeChat（TS 类型→约束→校验修复）

**Prompt 管理/版本化**
- 〔web〕Langfuse Prompts（OSS MIT、registry+版本化+A/B label `prod-a/prod-b`+追踪/评测；2026-01 被 ClickHouse 收购）— https://langfuse.com/docs/prompt-management/features/a-b-testing ；https://www.respan.ai/market-map/compare/langfuse-vs-promptlayer
- 〔web〕PromptLayer（日志优先、Registry + Dynamic Release Labels）；Humanloop/LangSmith/Maxim 对比 — https://www.conbersa.ai/learn/prompt-management-tools-comparison ；https://www.getmaxim.ai/articles/top-5-prompt-management-platforms-in-2025/

**本仓库（对标基线）**
- 〔本地〕`policies/prompt-engineering-techniques.md`（22 项手写技巧，已覆盖手写层）；`policies/llm-eval-methodology.md`（第 5 节 GEPA 式调优、A/B 显著性）
- 〔本地〕`skills/ai-planning-orchestrator/references/prompt-strategy-first.md`（五步转化、六段 Prompt、位置布局 P3）；`references/ai-service-construction.md`、`references/execution-sop.md`、`references/eval-driven-development.md`
- 〔本地〕`skills/ai-planning-orchestrator/assets/`：`prompt-strategy-card-template.md`（策略→指令映射+覆盖率）、`tuning-report-template.md`（ASI 失败归因+A/B+Pareto，`prompt-vX.Y`）、`ai-prd-template.md`、`eval-report-template.md`、`judge-rubric-template.md`
- 〔本地〕`policies/submission-review-contract.md`、`policies/agent-team-methodology.md`（自我进化/With-skill vs Baseline）；`tests/test_product_expert_agent.py`（契约测试落点）

