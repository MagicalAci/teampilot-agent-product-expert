# 域 1：Agent 推理范式与架构

> 子代理：agent-reasoning ｜ 回写：`research/ai-capability-upgrade/findings/01-agent-reasoning.md`
> 来源标注：〔web〕= 本次联网核实；〔知识〕= 训练知识、未逐条复核（已尽量只用确有其物的框架/论文）。
> 边界：本域聚焦**单体 Agent 的推理范式与控制流**。多代理编排框架（LangGraph/AutoGen/CrewAI/A2A）见域 2；语义/模型路由见域 3；MCP·沙箱·computer-use 工程见域 4；记忆/RAG 基础设施见域 5、6；verifier/评估工程见域 9。本域只取这些主题的**推理范式角度**并做交叉引用。

---

## 领域概述

「Agent 推理范式」指 LLM 在完成任务时**如何组织思考、行动与自我修正的控制流**——从一次性回答，到"边想边做"（ReAct）、"先规划后执行"（Plan-and-Execute/ReWOO）、"生成后自检"（Self-Refine/Reflexion）、"搜索式择优"（ToT/LATS），再到"代码即动作"（CodeAct）与"推理模型 + test-time compute"。它是 Agent 的"思维骨架"，直接决定准确率、成本、可控性与可观测性。

对「产品专家 Agent」尤其重要：它的五项能力（调研/产品策划/AI策划/Demo/SQL）都是**多步、长链路、需自检**的任务。当前编排靠 `task-navigator`（主动分阶段规划）+ `agent-team-methodology`（6 种**团队**架构模式）——但这两者解决的是"任务怎么拆给谁做"，**唯独缺一层"单个 Agent 在一步内该用哪种推理范式"的系统化显式知识**。行业共识（Anthropic《Building Effective Agents》）是：**能用确定性 workflow 就别上自主 agent，按需逐级加自主性**；产品专家 Agent 已具备团队级模式，但缺单代理级的"推理模式选择 + 反思自检 + test-time 用算力"的显式范式库，这正是本域要补的缺口。

---

## SOTA 技术目录

> 按子类分组，共 **48 条**。成熟度：实验 / 成长 / 成熟 / 事实标准。

### 0. 基础概念与自主性分级

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| 单步 LLM 调用 | 一次提示一次输出，无工具/无循环 | 分类、抽取、改写等确定性子任务 | 事实标准 | 任意 LLM API | 〔知识〕 |
| Workflow vs Agent | Workflow=人预定义控制流；Agent=模型自主决定步骤/工具/终止 | 流程可预测→workflow；开放、需灵活→agent | 事实标准（行业共识） | Anthropic《Building Effective Agents》 | 〔web〕 |
| 自主性分级 | 把 agent 自主度分层（控制流/工具/终止谁决定），由低到高逐级放权 | 决定该给多少自主性、何时收回人控 | 成长 | HuggingFace smolagents "levels of agency"；类比 L0–L5 | 〔知识〕 |
| Augmented LLM（增强 LLM） | LLM + 检索 + 工具 + 记忆，作为一切 agent 的最小构建块 | 任何 agent 的底座单元 | 事实标准 | Anthropic 同文；function calling | 〔web〕 |

### A. 提示级推理结构（单次/少次调用内塑形思考，**对单体 Agent 立刻可用**）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Chain-of-Thought (CoT) | 让模型"分步推理"再给答案 | 任何需要多步推理的任务 | 事实标准 | Wei et al. 2022 | 〔web〕 |
| Zero-shot CoT | "Let's think step by step"零样本触发 CoT | 无示例时快速提质 | 事实标准 | Kojima et al. 2022 | 〔web〕 |
| Self-Consistency | 采样多条 CoT，多数投票取最一致答案 | 高风险/数值/判断题需稳态 | 成熟 | Wang et al. 2022/23 | 〔web〕 |
| Least-to-Most / 分解式提示 | 先拆成由易到难子问题再逐个解 | 组合泛化、符号操作、长链推理 | 成熟 | Zhou et al. 2022；Khot et al. 2022 | 〔web〕 |
| Step-Back Prompting | 先退一步抽象出通用原理，再解具体题 | 知识密集、需先定原则 | 成熟 | Zheng et al. 2023 | 〔web〕 |
| Tree of Thoughts (ToT) | 把中间想法当搜索节点，分支+回溯 | 需探索多路径、可回退（解谜/规划） | 成长 | Yao et al. 2023 | 〔web〕 |
| Graph of Thoughts (GoT) | 想法组成图，可聚合/反馈/复用节点 | 需合并多条思路的复杂任务 | 实验 | Besta et al. 2023/24 | 〔web〕 |
| Plan-and-Solve | 先生成计划再按计划解，减少漏步 | 比裸 CoT 更稳的零样本多步 | 成熟 | Wang et al. 2023 | 〔web〕 |
| Self-Discover | 让模型从原子推理模块**自组合**出任务专属推理结构 | 复杂、结构异质的任务；比 CoT-SC 省 10–40× 算力 | 成长 | Zhou et al. 2024 (DeepMind/NeurIPS) | 〔web〕 |
| Branch-Solve-Merge | 分支→分别解→合并 | 可并行子问题的评估/生成 | 实验 | Saha et al. 2023 | 〔web〕 |
| RAP（Reasoning via Planning） | 把 LLM 当世界模型 + MCTS 做规划 | 需前瞻模拟的推理 | 实验 | Hao et al. 2023 | 〔web〕 |
| Chain-of-Verification (CoVe) | 先答→自生成核查问题→据此修订 | 抑制幻觉、事实类输出 | 成长 | Dhuliawala et al. 2023/24 | 〔web〕 |

### B. Agentic 推理-行动循环（"思考+工具"控制流，**多步 agent 核心**）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| ReAct | 交替"推理(Thought)→行动(Action)→观察(Observation)"循环 | 需调工具/检索且边做边修正 | 事实标准 | Yao et al. 2022/23；LangGraph ReAct | 〔web〕 |
| Function/Tool Calling 循环 | 模型产结构化工具调用→执行→回灌结果 | 任务可预测、调几个工具即可 | 事实标准 | OpenAI/Anthropic 工具调用 | 〔web〕 |
| Reflexion | 失败后用"语言化自我反思"写入记忆，下一轮改进 | 可多次尝试、有成败信号 | 成熟 | Shinn et al. 2023 | 〔web〕 |
| Self-Refine | 自己产反馈→自己改，迭代精修 | 有明确质量维度、可迭代 | 成熟 | Madaan et al. 2023 | 〔web〕 |
| CRITIC | 用外部工具（搜索/解释器）校验并修正输出 | 需"工具接地"的事实/代码校验 | 成长 | Gou et al. 2023/24 | 〔web〕 |
| Plan-and-Execute | 规划器先出计划，执行器逐步执行（必要时重规划） | 长链路、步骤较稳定 | 成熟 | LangChain Plan-and-Execute；BabyAGI 谱系 | 〔web〕 |
| ReWOO | 计划与观察解耦：一次性出带变量的计划，worker 执行无需每步重问 LLM | 省 token、减少往返、可并行 | 成长 | Xu et al. 2023 | 〔web〕 |
| LLM Compiler | 把工具调用编排成依赖图，独立子任务**并行执行** | 多工具、有并行度的任务降延迟 | 成长 | Kim et al. 2024 | 〔web〕 |
| AdaPlanner | 解耦规划仍可据环境反馈**自适应改计划** | 环境会变、需在线纠偏 | 成长 | Sun et al. 2023 | 〔web〕 |
| LATS（语言 Agent 树搜索） | ReAct + MCTS，模型既当提议者又当评估者，提交前先搜索择优 | 难任务、可承受高算力、动作部分可逆 | 实验/成长 | Zhou et al. 2023/24 | 〔web〕 |
| CodeAct（代码即动作） | 用**可执行 Python 代码**作为统一动作空间，替代 JSON 工具调用 | 多步/带逻辑/批量工具操作；自调试 | 成长（快速上升） | Wang et al. 2024 (CodeActAgent)；Microsoft Agent Framework | 〔web〕 |

### C. Anthropic《Building Effective Agents》6 构建块（**已是事实标准词汇**）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Prompt Chaining | 任务拆成顺序步骤，上一步输出喂下一步，中间设"gate"校验 | 步骤可预测、可线性分解 | 事实标准 | Anthropic 同文 | 〔web〕 |
| Routing | 先分类输入再路由到专门化的后续处理/模型 | 输入类型多样、需分而治之 | 事实标准 | Anthropic 同文 | 〔web〕 |
| Parallelization（Sectioning + Voting） | 并行跑独立子任务（分段）或同任务多跑取票（投票） | 可并行/需多样性或多重校验 | 事实标准 | Anthropic 同文 | 〔web〕 |
| Orchestrator-Workers | 中央 LLM 动态拆任务、派给 worker、再综合（子任务运行时才定） | 任务不可预先分解、复杂多变 | 事实标准 | Anthropic 多代理研究系统（+90.2% vs 单代理） | 〔web〕 |
| Evaluator-Optimizer | 一个生成、另一个按明确标准评/反馈，循环到达标 | 有清晰评价标准、迭代有增益 | 事实标准 | Anthropic 同文 | 〔web〕 |
| Autonomous Agent | LLM 在循环里自主用工具+读环境反馈，自定终止 | 开放式、步数不定、需灵活 | 成长 | Anthropic 同文；编码/计算机使用 agent | 〔web〕 |

### D. Computer-Use / GUI / 代码动作型 Agent（**多需外部基础设施**，见域 4）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Claude Computer Use | VLM 直接看截图、操作鼠标键盘完成 GUI 任务 | 无 API 的 GUI 流程自动化 | 成长 | Anthropic 2024 | 〔web〕 |
| OpenAI Operator / CUA | Computer-Using Agent，浏览器/桌面里替你操作 | Web 任务、表单、信息获取 | 成长 | OpenAI Operator (CUA) | 〔web〕 |
| UI-TARS / UI-TARS-2 | 原生端到端 GUI agent 模型，多轮 RL 训练，SOTA on OSWorld 等 | 需强 GUI 接地与长程操作 | 成长 | 字节 UI-TARS, UI-TARS-2 (2025) | 〔web〕 |
| CoAct-1 | 混合多代理：GUI 操作 + 直接写代码执行，互补提效 | GUI 与可编程操作并存 | 实验 | CoAct-1 (2025) | 〔web〕 |

### E. Test-Time Compute / 推理模型 / Verifier（**推理新范式，部分立刻可用**）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Test-Time Compute Scaling | 把更多算力放在**推理时**（多采样/搜索/反思）换准确率 | 难题、值得用算力换质量 | 成熟 | DeepMind 2024（推理时 vs 训练时缩放） | 〔web〕 |
| 推理模型 / LRM | 答前先生成长推理链（内置 CoT+自纠） | 数学/代码/复杂规划 | 事实标准（已成产品默认档） | OpenAI o1/o3、DeepSeek-R1、QwQ、Gemini Thinking | 〔web〕 |
| 混合推理 / Thinking Budget | 可开关"思考"模式、可调思考预算/reasoning effort | 按任务难度平衡质量与成本 | 成熟 | Claude 3.7 Sonnet、IBM Granite 3.2、Gemini、o 系列 | 〔web〕 |
| Best-of-N + Verifier | 采样 N 个解，用验证器/奖励模型择优 | 有验证器、可并行采样 | 成长 | 通用 test-time 方法 | 〔web〕 |
| PRM / ORM（过程/结果奖励模型） | PRM 给**每一步**打分，ORM 只评最终答案 | 训练/筛选推理链、引导搜索 | 成长（研究→产品） | Lightman et al.；各推理模型后训练 | 〔web〕 |
| Verifier-Guided Search / List-wise 校验 | 用验证器引导搜索；列表式比较优于单条打分/投票 | agent 多 rollout 择优 | 成长 | 《Scaling Test-time Compute for LLM Agents》2025 | 〔web〕 |
| 自适应反思（reflect-when-stuck） | 不每步都反思，**只在表现差/受阻时**反思更有效 | 控反思成本、避免过度思考 | 成长 | 同上 2025 实证 | 〔web〕 |

### F. 自动化 Agent 设计 / 自我进化（**北极星，需 eval 基建+算力**，见域 9 + 自进化闭环）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| ADAS | 用固定 meta-agent 自动**生成/迭代**下游 agent 设计，按基准评分反馈 | 想自动搜索 agent 架构 | 实验 | Hu et al. 2024（Automated Design of Agentic Systems） | 〔web〕 |
| AFlow | 把 agentic workflow 表示为代码，用 MCTS 搜索最优工作流 | 自动优化工作流结构 | 实验 | Zhang et al. 2024（MetaGPT 团队） | 〔知识〕 |
| Darwin Gödel Machine (DGM) | 自指自改：agent **重写自身代码**变成更好的编码 agent，存档+开放式进化 | 自我改进 agent（SWE-bench 20%→50%） | 实验 | Sakana AI 2025 (arXiv 2505.22954) | 〔web〕 |
| DGM-Hyperagents (DGM-H) | 把任务 agent 与 meta-agent 合一且**改进机制本身也可改**（元认知自改） | 跨域自我加速改进 | 实验 | Meta/UBC 2025（HyperAgents） | 〔web〕 |

### G. 记忆增强推理（**推理角度**；记忆基建见域 6）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表框架·产品·论文 | 来源 |
|---|---|---|---|---|---|
| Generative Agents（记忆流+反思） | 记忆流 + 周期性反思综合 + 检索影响后续行为 | 长程、多轮、需"经验积累" | 成长（学术影响大） | Park et al. 2023 | 〔知识〕 |
| 记忆增强 Agent 循环 | 把跨会话长期记忆接入推理回路（提取/巩固/检索/遗忘） | 需跨会话连续性的助手 | 成长 | MemGPT/Letta、Mem0、A-MEM（交叉引用域 6） | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **推理模型成为默认底座，"thinking budget" 可调**〔web〕：o1/o3、DeepSeek-R1、Claude 3.7（可调思考时长）、Gemini Thinking、Granite 3.2（可开关思考）——agent 设计从"靠提示堆 CoT"转向"选模型档位 + 调推理预算"。
2. **Test-time compute 成为新缩放维度**〔web〕：DeepMind 论证推理时缩放可媲美训练时缩放；agent 端 Best-of-N、beam/tree search、self-consistency 成为提质标准件。
3. **"知道何时反思"比"一直反思"更重要**〔web〕：2025《Scaling Test-time Compute for LLM Agents》实证——每步都反思收益不明显，**受阻时才反思**、且 **list-wise 校验/合并优于投票或单条打分**。
4. **CodeAct（代码即动作）快速主流化**〔web〕：用可执行代码当动作空间，比 JSON 工具调用更省轮次/token（Microsoft Agent Framework 报告 ~50% 延迟、>60% token 下降），并天然支持自调试、批量与并行工具操作。
5. **Orchestrator-Workers 多代理成生产级模式**〔web〕：Anthropic 多代理研究系统比单代理 +90.2%，但 token ~15×——**只对高价值复杂查询划算**；并把"计划写入记忆防截断 + CitationAgent 归因 + 工具描述自动改写"作为工程要点。
6. **GUI / Computer-Use agent 从"框架拼装"转向"原生端到端模型"**〔web〕：UI-TARS-2 多轮 RL，在 OSWorld/AndroidWorld/WindowsArena 超过 Claude/OpenAI 的 computer-use 基线；CoAct-1 用"GUI+代码"混合提效。
7. **自我进化 agent 从"meta-agent 设计"走向"自改代码"**〔web〕：ADAS→AFlow（搜工作流）→DGM（自重写代码、开放式进化）→DGM-H（连"改进机制"也可改）——是产品专家 `/经验写回` 自进化闭环的"北极星"，但需 eval 基建与沙箱。
8. **Verifier/PRM 成为 agent 可靠性的关键拼图**〔web〕：过程奖励模型给每一步打分，引导搜索与筛选；趋势是"领域专用验证器"比通用模型层解决多步推理更可行。
9. **"先 workflow，后 agent；按需加自主性"成为行业默认设计纪律**〔web〕：Anthropic 明确反对一上来就上自主多代理；推荐从最简模式起步、可观测、限递归与调用数——这条纪律本身就是产品专家应显式写入的范式。
10. **上下文工程（context engineering）取代"prompt 调参"成为 agent 主战场**〔web〕：长程 agent 靠"把计划/中间结论写入记忆、分上下文给子代理、压缩与防截断"维持连贯——推理质量越来越受上下文供给方式制约（交叉域 6）。

---

## 对标产品专家 Agent

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| `agent-team-methodology.md` 有 6 种**团队**架构模式（Pipeline/扇出扇入/专家池/生成-检验/监督者/层级），且与 Anthropic workflow 模式高度同构 | 覆盖的是"任务拆给谁/几个代理"，**缺单代理级"一步内用哪种推理范式"的显式库**（ReAct/Plan-and-Execute/ReWOO/Self-Refine/CodeAct 等无成文指引） | **P0**：新增 `policies/agent-reasoning-paradigms.md` 单代理推理范式库（与 team-methodology 互为"微观/宏观"） |
| `task-navigator.mdc` 任务启动即主动分阶段规划，并征求确认 | 规划是"分阶段派能力"，**未先判定"确定性 workflow vs 自主 agent / 该用什么推理范式 / 自主度多高"** | **P0**：在 task-navigator 规划前加"推理模式 + 自主性分级"选择步，引用新范式库 |
| 调研有阶段门禁（采集/成稿门禁、三轮事实核查），生成-检验子代理 = evaluator-optimizer | 自检是**团队级、写死在 research 流程**里，缺**可复用的单代理 Self-Refine/Reflexion-lite/CoVe 反思闸**（其他四能力没有统一自检回路） | **P0**：抽出可复用"反思自检 protocol"，五能力共用；事实类输出默认挂 CoVe | 
| `prompt-engineering-techniques.md` 有 22 个提示技术（含 CoT、少样本、受限生成…） | 多为**单轮提示技巧**，缺 **agentic 推理结构**（Self-Discover 组合、Self-Consistency、Step-back、ToT、Least-to-most）与"何时用哪种"的选择指引 | **P1**：审计 22 技术，补齐"推理结构子集"并与范式库交叉链接 |
| 模型层默认单档；无"思考预算/推理模型"用法指引 | 未利用 **test-time compute / 推理模型 / thinking budget / Best-of-N**——高风险产出（PRD 结论、SQL 口径、竞品判断）未做多采样取一致 | **P1**：写"按任务难度选模型档 + 高风险产出 self-consistency"指引；交叉域 12 | 
| 工具层是 MCP/连接器消费方，JSON 式工具调用 | 无 **CodeAct（代码即动作）**：多步/批量工具编排（如多平台采集汇总、SQL+图表）逐个 JSON 调用，轮次/token 高，无并行 | **P2**（需沙箱）：在已能跑脚本的 aibi-query/research 引入"CodeAct-lite：能写一段脚本完成的多步工具操作就别逐个调" |
| 自进化靠 `/经验写回`→PR+契约测试（人审合并） | 是"人触发的离线进化"，**无自动评估驱动的搜索/自改**（ADAS/AFlow/DGM 思路）；契约测试是存在性校验，非质量评分 | **P2**：把 DGM/ADAS 设为北极星——补 eval 基建（域 9）后，让 `/经验写回` 增"With-skill vs Baseline 量化评分"闭环 |
| 无运行时验证器/PRM 概念 | 多步轨迹无"过程级"校验；错误沿链传播无早停 | **P2**：先用"LLM-as-judge 轻量过程检查 + reflect-when-stuck"近似 PRM（域 9 提供 judge），避免重训 |

---

## 落地建议

> 原则：先做"对单体 Agent 立刻可用"的提示/policy/rule 层（P0/P1），需基建的（沙箱/eval/记忆）标 P2 并交叉引用兄弟域。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 新增单代理推理范式库 `policies/agent-reasoning-paradigms.md`
- **放哪**：`policies/agent-reasoning-paradigms.md`（新文件，与 `agent-team-methodology.md` 平级，互为"微观推理 / 宏观团队"）。
- **做什么**：Why-First 写法，含 ①**模式选择决策树**（单步？→直接答；多步可预测？→Plan-and-Execute/Prompt-Chaining + gate；需调工具边做边修？→ReAct；可并行工具？→ReWOO/LLM-Compiler 思路；需择优搜索？→ToT/Self-Consistency；开放不定步？→自主 agent + 限递归）；②**自主性分级**与"先 workflow 后 agent"纪律；③每范式的"何时用 / 何时别用 / 与本仓库哪个能力匹配"（如：research 多平台汇总→ReWOO/并行；PRD 成稿→Plan-and-Solve+Self-Refine；SQL 口径→Self-Consistency+CoVe）。引用 Anthropic 同文 + 本文件表格。
- **验收信号**：`tests/test_product_expert_agent.py` 新增断言——文件存在且含标记 `ReAct`/`Plan-and-Execute`/`Self-Refine`/`自主性分级`/`workflow 优先`；`task-navigator` 与 `product-expert-commands` 能引用到它。

### P0-2 task-navigator 增"推理模式 + 自主性"选择步
- **放哪**：`.cursor/rules/task-navigator.mdc`（已存在，"任务启动—主动分析"段后）。
- **做什么**：在输出工作规划前，加一句显式判定："本任务是确定性 workflow 还是需自主 agent？用哪种推理范式？自主度多高？"——并在分阶段规划里标注每阶段的推理范式；引用 `policies/agent-reasoning-paradigms.md`。
- **验收信号**：规划输出含"推理模式：<范式>（理由）"一行；20 条触发 eval 中——简单确定性任务选 workflow、复杂开放任务选 autonomous+反思，命中率达标。

### P0-3 抽出可复用"反思自检 protocol"（Self-Refine / CoVe / Reflexion-lite）
- **放哪**：`policies/self-critique-protocol.md`（新）或并入范式库；五能力在"成稿/出结论前"统一引用（research 已有门禁可对齐复用）。
- **做什么**：定义最小自检闸——生成→按该任务质量维度自评→（有问题且未超 2–3 轮）修订；事实类输出默认挂 **CoVe**（自生成核查问题→核对→修订）；明确"**只在自评不达标/受阻时**才进入反思"，控成本（采纳 2025 reflect-when-stuck 实证）。
- **验收信号**：协议文件含"最大重试 2–3 轮""CoVe""reflect-when-stuck"标记；至少 1 个能力（建议 PRD 或 SQL）接入并在契约测试里断言"产出含自检/核查痕迹"。

### P1-1 提示技术审计：补齐 agentic 推理结构子集
- **放哪**：`policies/prompt-engineering-techniques.md`（已存在的 22 技术）。
- **做什么**：审计是否覆盖 Self-Consistency / Self-Discover（组合推理模块）/ Step-back / Least-to-most / ToT；缺则补，并与范式库交叉链接（"提示技巧"↔"推理范式"分层）。
- **验收信号**：文件含上述至少 4 项新条目且各带"何时用 + 边界"；与范式库双向链接可达。

### P1-2 test-time compute 使用指引
- **放哪**：`policies/agent-reasoning-paradigms.md` 的"用算力换质量"小节 + `agent-team-methodology.md` 第四部分"Token 优化"对齐。
- **做什么**：写"**按任务难度选模型档/思考预算**；高风险产出（PRD 关键结论、SQL 口径、竞品判断）做 **Self-Consistency 多采样取一致**或双跑交叉校验"；明确"简单转换/确定性任务用轻量档，复杂推理才上重档/开思考"。
- **验收信号**：指引含"thinking budget/reasoning effort""self-consistency""高风险产出"标记；与域 12 模型路由建议不冲突。

### P2-1 CodeAct-lite（需沙箱，交叉域 4）
- **放哪**：`skills/aibi-query/` 与 `skills/research-toolkit/`（已能跑脚本处）的 protocol。
- **做什么**：指引"**能用一段脚本完成的多步/批量工具操作（多平台采集汇总、SQL+图表流水线）就写脚本，别逐个 JSON 调**"，沙箱内执行 + 自调试；无沙箱时降级为现有逐步调用。
- **验收信号**：协议含"代码即动作/脚本优先""沙箱降级"说明；至少一条数据/采集流水线改为脚本化并在测试中可跑。

### P2-2 自进化闭环升级为"评估驱动"（北极星：ADAS/DGM，交叉域 9）
- **放哪**：`policies/submission-review-contract.md` + `agent-team-methodology.md` 第三/四部分。
- **做什么**：待域 9 提供 eval 基建后，把 `/经验写回` 的契约测试从"存在性"升级为 **With-skill vs Baseline 量化评分 + pass@k**；远期可试"meta-agent 提候选改法→自动评分→择优"的 ADAS-lite（限沙箱+人审，借鉴 DGM 的存档/安全护栏）。
- **验收信号**：写回 PR 模板要求附"带/不带技能的量化对比 + pass@k"；评分闸纳入合并门槛。

---

## 参考来源

- Anthropic, *Building Effective Agents*〔web〕 — https://www.anthropic.com/engineering/building-effective-agents ；配套 PDF *Architecture Patterns and Implementation Frameworks*。
- Anthropic, *How we built our multi-agent research system*〔web〕 — https://www.anthropic.com/engineering/multi-agent-research-system （orchestrator-worker，+90.2% vs 单代理，~15× token，CitationAgent，计划写入记忆）。
- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (2022/23)〔web〕；IBM *What is a ReAct Agent* — https://www.ibm.com/think/topics/react-agent 。
- Shinn et al., *Reflexion* (2023)〔web〕；Madaan et al., *Self-Refine* (2023)〔web〕；Gou et al., *CRITIC* (2023/24)〔web〕；Dhuliawala et al., *Chain-of-Verification* (2023/24)〔web〕。
- Xu et al., *ReWOO* (2023)〔web〕；Kim et al., *LLMCompiler* (2024)〔web〕；Sun et al., *AdaPlanner* (2023)〔web〕；Zhou et al., *LATS* (2023/24)〔web〕 — 见综述 *Agentic Tool Use in LLMs* https://arxiv.org/html/2604.00835v1 。
- Yao et al., *Tree of Thoughts* (2023)〔web〕；Besta et al., *Graph of Thoughts* (2023/24)〔web〕 — Cameron Wolfe, *Graph-Based Prompting* https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning 。
- Wei et al., *Chain-of-Thought* (2022)〔web〕；Wang et al., *Self-Consistency* (2022/23)〔web〕；Zhou et al., *Least-to-Most* (2022)〔web〕；Zheng et al., *Step-Back* (2023)〔web〕；Wang et al., *Plan-and-Solve* (2023)〔web〕。
- Zhou et al., *Self-Discover: LLMs Self-Compose Reasoning Structures* (NeurIPS 2024)〔web〕 — https://arxiv.org/html/2402.03620v1 ；DeepMind https://deepmind.google/research/publications/64816/ 。
- Wang et al., *Executable Code Actions Elicit Better LLM Agents (CodeAct)* (2024)〔web〕 — https://arxiv.org/html/2402.01030 ；Microsoft *CodeAct in Agent Framework (Hyperlight)* — https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/ 。
- *UI-TARS* (2025)〔web〕 — https://arxiv.org/html/2501.12326v1 ；*UI-TARS-2 Technical Report* — https://arxiv.org/html/2509.02544v2 ；Anthropic Claude Computer Use；OpenAI Operator (CUA)；CoAct-1。
- 推理模型与 test-time compute：IBM *What Is a Reasoning Model* 〔web〕 — https://www.ibm.com/think/topics/reasoning-model （PRM/ORM、混合推理、thinking budget）；*Scaling Test-time Compute for LLM Agents* (2025)〔web〕 — https://arxiv.org/html/2506.12928v1 （BoN、list-wise 校验、reflect-when-stuck）。
- 综述：*LLM-based Agentic Reasoning Frameworks: A Survey* (2025)〔web〕 — https://arxiv.org/html/2508.17692 ；*A Review of Prominent Paradigms for LLM-Based Agents* (COLING 2025)〔web〕 — https://aclanthology.org/2025.coling-main.652.pdf ；*Agentic AI: Architectures, Taxonomies, and Evaluation* 〔web〕。
- 自我进化：Hu et al., *ADAS* (2024)〔web〕；*Darwin Gödel Machine* (Sakana AI, 2025)〔web〕 — https://arxiv.org/html/2505.22954v3 ， https://sakana.ai/dgm/ ；*HyperAgents / DGM-H* (Meta, 2025)〔web〕 — https://ai.meta.com/research/publications/hyperagents/ ；Zhang et al., *AFlow* (2024)〔知识〕。
- 记忆增强推理：*Mem0* (2025)〔web〕 — https://arxiv.org/html/2504.19413 ；MemGPT/Letta、A-MEM 对比〔web〕；Park et al., *Generative Agents* (2023)〔知识〕（基建细节见域 6）。
