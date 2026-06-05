# 域 9：评估、Verifier 与可观测

> 子代理：eval-observability ｜ 回写：`research/ai-capability-upgrade/findings/09-eval-observability.md`
> 来源标注：〔web〕= 本次（2026-06）联网核实，附 URL；〔知识〕= 训练知识、未逐条复核（已尽量只用确有其物的框架/论文/产品）。
> 边界：本域聚焦**"对不对（质量评估）＋追得到（轨迹可观测）"**。**评测集四桶/三类 grader/G-Eval/judge 偏差校正/pass@k/A-B/OTel 基础**已在 `policies/llm-eval-methodology.md` 成文——本域**对齐引用不重写**，只补它欠缺的"**Agent 轨迹 / 在线 / verifier**"视角。交叉边界：RAG 检索指标（faithfulness/context precision）→域 5；安全 red-team/越狱/PII 评测→域 10；prompt 自动优化的评分（DSPy/GEPA 内部 metric）→域 11；模型路由成本评测→域 12；单体推理的 Best-of-N+verifier 推理角度→域 1。

---

## 领域概述

「评估、Verifier 与可观测」是 Agent 的**标尺与仪表盘**：离线（offline，发布前）回答"今天对不对"，在线（online，生产中）回答"持续对不对、漂没漂"，verifier/过程级校验回答"**每一步**对不对"。2025-2026 的范式跃迁有三条主线：① 评估对象从**单轮文本**（input→output）转向**多步轨迹**（thought→tool call→observation→…→final），评测从"只看终答"升级为"**轨迹级 + 组件级**"（DeepEval trace/span、Ragas ToolCallAccuracy、Agent-as-a-Judge）；② **可验证奖励/过程监督**成为可靠性核心拼图——ORM→PRM→生成式 GenRM/GenPRM、Agent-as-a-Judge，把"评分"做成可训练、可引导搜索的系统；③ **可观测标准化**——OpenTelemetry GenAI 语义约定把 model span / agent span / tool span / MCP span 统一成跨厂商词汇，Langfuse/Phoenix/Galileo 等围绕它形成"trace + 在线 eval + guardrail"闭环。

**与本仓库已有 `llm-eval-methodology.md` 的分工（务必先读后者）**：现有 policy 已是一套**完整且高质量的"单轮 EDD"方法论**——评测集四桶配比（生产 60/对抗 15/边界 15/回放 10）、三类 grader（规则/judge/人工，确定性地板）、**G-Eval + 五大偏差校正 + Cohen's κ 校准 + judge 合同**、pass@k/pass^k、回归/A-B（配对 t 检验 + Cohen's d）、OTel GenAI 第 6 节、`scripts/run_eval.py` 轻量评测台。**这些本域不重写，只对齐引用。** 本域**新增**的是现有 policy **结构性缺失**的四块：
- （新增 1）**Agent 轨迹评估**：完成率（task completion）、**工具调用准确率**（tool selection / argument correctness）、计划质量/遵循度、步骤效率、轨迹级失败定位——现有 `run_eval.py` 的评测单元是"一条 `input`→一条 `output`"，**没有"一条任务→一整条多步轨迹"的数据模型与 grader**。
- （新增 2）**完成判定 + 轨迹 judge**：把现有"单轮 G-Eval judge"延伸到"**对整条 run 的高层目标级判定**"（回应域 2 P1-2 通用 reviewer、MAST 轨迹诊断）。
- （新增 3）**verifier / PRM / 过程级校验**：现有 policy 无此概念（回应域 1 P2"无运行时验证器"）。
- （新增 4）**Agent 轨迹/能力基准 + user simulator + 在线 agent 可观测**：现有 policy 第 6 节只给"model 调用级 OTel + 平台名"，**缺 agent span / 工具调用准确率 / user simulator / 完成率基准**这一整层。

**对标缺口（点名文件）**：产品专家 Agent 已有 `skills/ai-planning-orchestrator/`（`/AI评测`·`/AI调优`·`/评测集`）+ `scripts/run_eval.py`（规则 grader/pass@k/回归/A-B/可插拔 judge）+ `skills/research-toolkit/` 三轮事实核查 + `tests/test_product_expert_agent.py` 契约测试。但：①评测台是**单轮文本评测**，没有"轨迹/完成率/工具调用准确率"；②**契约测试是"文件存在 + 关键词"的存在性校验，不是质量评分**（`test_product_expert_agent.py` 全是 `assertTrue(path.exists())` 与 `assertIn(keyword)`）；③**无 user simulator**（五能力都靠真人对话，无法自动化跑多轮）；④**无线上可观测**（OTel GenAI 只在 policy 里"提了"，无落地的 run-trace 约定与 span 名）。本域给出 P0「**轨迹/完成判定 checklist + 可观测最小约定**」protocol，与现有 EDD policy 互补。

---

## SOTA 技术目录

> 按子类分组，共 **73 条**（部分条目聚合多个同类基准/工具，实际点名技术 ≈85）。成熟度：实验 / 成长 / 成熟 / 事实标准。标 `[对齐]` = 已被 `llm-eval-methodology.md` 覆盖、本域仅引用；标 `[新增]` = 现有 policy 缺、本域补充。企业级 + 应用级 + 研究前沿都收。

### A. 离线 Eval Harness / 平台（框架层，横向选型）

| 技术/框架 | 一句话定义 | 何时用 | 成熟度 | 代表实现·论文 | 来源 |
|---|---|---|---|---|---|
| **DeepEval** | pytest 式 LLM 评测，50+ 指标；**agent 专项**：TaskCompletion/ToolCorrectness/ArgumentCorrectness/PlanQuality/PlanAdherence/StepEfficiency，trace（端到端）+ span（组件级） | 接 CI 按维度打分阻断；要 agent 轨迹评估 | 成熟 `[新增-agent部分]` | confident-ai/deepeval（MIT） | 〔web〕 |
| **promptfoo** | YAML/CLI 声明式提示词回归 + red-team（500+ 攻击向量） | 提示词/模型选型对比、快速回归、红队 | 成熟 `[对齐]` | promptfoo（MIT） | 〔web〕 |
| **Ragas** | RAG 起家，已扩 agent：**AgentGoalAccuracy / ToolCallAccuracy / TopicAdherence / MultiTurnSample / AspectCritic** | RAG 忠实度 + agent 目标/工具调用准确率 | 成熟 `[新增-agent部分]` | explodinggradients/ragas（Apache-2.0，EACL 2024） | 〔web〕 |
| **Inspect AI** | UK AISI 出品；Dataset→**Solver**→**Scorer** 可编程；内置 ReAct/Deep Agent/multi-agent、agent bridge（接 OpenAI Agents SDK/LangChain/Pydantic AI）、**沙箱（Docker/K8s）+ token/时钟/调用数 policy limits**、200+ 评测、log viewer | 把评测当生产基建：agent + 工具 + 安全沙箱 + 可审计 | 成熟（治理事实标准） `[新增-agent部分]` | UKGovernmentBEIS/inspect_ai（MIT，2.1k★，v0.3.x） | 〔web〕 |
| **lm-evaluation-harness** | EleutherAI，200+ 学术基准、标准化模型/任务接口 | 学术基准跨模型横评 | 事实标准（学术横评） `[对齐]` | EleutherAI/lm-evaluation-harness（MIT） | 〔web〕 |
| **OpenAI Evals** | 轻量模板化 harness，含 model-graded（judge）；现以 Evals API 形态 | 快速搭任务专属测试、模板复用 | 成熟 `[对齐]` | openai/evals + Evals API | 〔web〕 |
| **Braintrust** | 一体化 eval + trace + experiments 平台；中 2025 起发 GenAI-semconv 兼容 span + OTLP | 要 managed 评测 + 实验 + 可观测一体 | 成长 | braintrust.dev | 〔web〕 |
| **LangSmith（eval）** | LangChain 原生 datasets/experiments/在线 eval；`LANGSMITH_TRACING=true` 导 OTLP | LangChain/LangGraph 栈团队 | 成长 | LangChain LangSmith | 〔web〕 |
| **Arize Phoenix（evals）** | OTel 原生、开源；强在 embeddings/**drift** 与 trace eval | 开源自托管 + 漂移/嵌入分析 | 成长 | Arize-ai/phoenix（Apache-2.0） | 〔web〕 |
| **MLflow LLM/Agent Eval** | 实验跟踪平台内置 LLM/agent 评测 + judge + 报告可视化 | 已用 MLflow 的团队接 agent eval | 成长 | mlflow（Apache-2.0） | 〔web〕 |
| **LightEval / OpenCompass / HELM / VLMEvalKit** | 轻量后端无关流水线 / 标准化大集 / 斯坦福整体评估 / 多模态评测 | leaderboard 式、标准化复现、多模态 | 成长~成熟 `[对齐]` | HF LightEval；OpenCompass；Stanford HELM；VLMEvalKit | 〔web〕 |

### B. LLM-as-Judge / 评委可靠性（judge 方法 + 校准 + 判 agent 轨迹）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表实现·论文 | 来源 |
|---|---|---|---|---|---|
| **G-Eval** | 打分前先让 judge 生成链式评估步骤（CoT）再据此打分 | 开放式质量（连贯/有用/切题/忠实度） | 成熟 `[对齐]` | Liu et al. EMNLP 2023 | 〔web〕 |
| **Pairwise + Bradley-Terry** | 成对比较择优；Chatbot Arena 已从在线 Elo 迁到 **BT 联合拟合**（排名更稳） | A/B 两版模型/提示词、相对判断 | 成熟 `[对齐-偏差部分]` | Chatbot Arena；Bradley-Terry | 〔web〕 |
| **Listwise / 多候选排序** | 一次比较/排序多个候选，优于逐条打分或多数投票 | agent 多 rollout 择优 | 成长 `[新增]` | 《Scaling Test-time Compute for LLM Agents》2025 | 〔web〕 |
| **Prometheus 2** | 开源细粒度 rubric 评委模型（替代闭源 judge，降成本/可控） | 自托管 judge、需细粒度量规 | 成长 | Prometheus 2（KAIST/开源） | 〔web〕 |
| **Arena-Hard / Arena-Hard-Auto / BenchBuilder** | 自动从真实流量"挖硬 prompt"，对前沿模型分离度高、与人偏好高相关、成本低 | 自建高分离度自动评测集 | 成长 | Li et al. 2024 | 〔web〕 |
| **AlpacaEval 2（length-controlled）** | 长度受控自动评测，专治 judge 长度偏差，与 Arena 相关性更高 | 去啰嗦偏差的快速自动评测 | 成熟 `[对齐-偏差部分]` | AlpacaEval 2 | 〔web〕 |
| **五大偏差校正** | 位置/啰嗦/自偏好/校准漂移/量规泄漏 → 顺序交换、反啰嗦判据、judge≠被测族、钉版本、中性措辞 | 任何上 LLM-judge 的流程 | 成熟 `[对齐]` | llm-eval-methodology 第 3 节 | 〔web〕 |
| **校准统计学** | Cohen's κ + **Krippendorff's α** + **TPR/TNR（优于 agreement%）** + McNemar/Wilcoxon 配对检验 + bootstrap CI + OPRO 迭代量规 | judge 上线前/季度重校准 | 成熟 `[对齐-κ；新增-TPR/TNR/α]` | AI Evals；Galtea guide | 〔web〕 |
| **Judge 可靠性基准** | 评"评委"本身：JudgeBench（客观正确性，GPT-4o 在硬题≈随机）、RewardBench / RewardBench 2、RM-Bench、LongJudgeBench（长文） | 选 judge 模型/验证 judge 可信度 | 成长 `[新增]` | Tan et al. JudgeBench 2024；Lambert/Malik RewardBench(2) | 〔web〕 |
| **Ensemble judge（多评委投票）** | 单评委不稳→多模型/多次投票降方差、提一致 | judge κ 不达标、高风险判定 | 成长 `[新增]` | AgentProp-Bench：substring κ=0.049→3-LLM ensemble κ=0.432 | 〔web〕 |
| **Agent-as-a-Judge** | **用 agentic 系统评 agentic 系统**：judge 自己规划/读文件/调工具/读轨迹，给**中间步骤反馈**，远超 LLM-as-judge、接近人评 | 评多步轨迹（代码/任务），要过程级反馈 | 实验→成长 `[新增]` | Zhuge et al. 2024（DevAI 55 任务/365 需求，8 模块）ICML 2025 | 〔web〕 |
| **AJ-Bench** | 评"Agent-as-a-Judge"本身的环境感知基准：search/DS/GUI 三域，155 任务/516 轨迹，F1；判 info acquisition/state/process | 选/验证轨迹判官；研究前沿 | 实验 `[新增]` | Shi et al. 2026（aj-bench.github.io，最佳 F1≈0.72 未饱和） | 〔web〕 |

### C. Verifier / 奖励模型 / 过程级校验（回应域 1 P2"无运行时 verifier/PRM"）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表实现·论文 | 来源 |
|---|---|---|---|---|---|
| **ORM（结果奖励模型）** | 只对最终答案打分（对/错） | 终态可判、训练/筛选最终解 | 成长 `[新增]` | 各推理模型后训练 | 〔知识〕 |
| **PRM（过程奖励模型）** | 给推理链**每一步**打分，定位首个错误步 | 引导搜索、过程监督、错误定位 | 成长 `[新增]` | Lightman《Let's Verify Step by Step》；Qwen2.5-Math-PRM | 〔知识〕 |
| **GenRM / 生成式验证器** | 把奖励建模重构为**下一 token 预测**（"Is correct? Yes/No"概率），天然支持 CoT + 多数投票，用推理时算力提验证精度 | 验证可与生成统一、要 test-time 提验证 | 成长 `[新增]` | Zhang et al.《Generative Verifiers》arXiv:2408.15240（DeepMind） | 〔web〕 |
| **GenPRM** | 生成式 PRM：每步**显式 CoT + 代码验证**再判；RPE 标注；test-time scaling 下 1.5B>GPT-4o、7B>Qwen2.5-Math-PRM-72B（ProcessBench） | 数学/代码强校验、可当 critic 引导精修 | 实验→成长 `[新增]` | Zhao et al. GenPRM AAAI 2026（arXiv:2504.00891） | 〔web〕 |
| **ProcessBench** | 评 PRM"能否定位过程错误"的基准 | 选/验证 PRM | 成长 `[新增]` | ProcessBench（Qwen 团队） | 〔web〕 |
| **Best-of-N + Verifier / Verifier-guided search** | 采样 N 解用验证器/奖励模型择优；验证器引导搜索 | 有验证器、可并行采样的高风险产出 | 成长 `[新增；交叉域1]` | 通用 test-time 方法；2025 list-wise 校验 | 〔web〕 |
| **RLVR（可验证奖励）** | 每场景配 write-action verifier，使评测集**直接可用于 RL 训练**（评测-训练一体） | 评测同时产可验证奖励信号 | 成长 `[新增；交叉域1]` | GAIA2/ARE write-action verifier | 〔web〕 |

### D. Agent 轨迹 / 能力评估基准（**现有 policy 最缺的一整层**）

| 基准 | 一句话定义 | 测什么能力 | 成熟度 | 现状（2026） | 来源 |
|---|---|---|---|---|---|
| **τ-bench** | Tool-Agent-User 交互，airline/retail 域，**pass^k 端态校验** + LLM user simulator | 工具调用 + 守策略 + 多轮对话可靠性 | 成熟（会话 agent 标杆） | Yao et al. 2024（arXiv:2406.12045） | 〔web〕 |
| **τ²-bench** | **双控 Dec-POMDP**（telecom），agent 与用户**都能用工具**改共享状态，含**可靠 user simulator**（受工具/可观测态约束） | 协调 + 沟通 + **引导用户**；分离 reasoning vs communication 错误 | 成长（ICML 2026 Oral） | Barres et al. 2025（arXiv:2506.07982），no-user→dual-control 显著掉分 | 〔web〕 |
| **τ³-bench** | τ-bench 最新：**全双工语音** + **knowledge/RAG**（banking 97 任务/698 文档）+ 75+ 任务质量修复 | 语音 agent + 检索后行动 + 任务质量 | 成长（2026-03 发布） | sierra-research/tau2-bench v1.0.0，leaderboard taubench.com | 〔web〕 |
| **AgentBench** | LLM-as-agent 跨 8 个交互环境（OS/DB/KG/卡牌/购物等）统一评测 | 多环境自主 agent 成功率 | 成熟 | THUDM，ICLR 2024 | 〔web〕 |
| **GAIA** | 助手通用能力（web 搜索 + 工具 + 多模态），**read-only**，答案唯一可判 | 真实助手任务的检索/推理 | 成熟 | Mialon et al.（Meta/HF） | 〔web〕 |
| **GAIA2 / ARE** | Meta+HF：800/1000 场景 ×10 universes，**异步动态环境** + **write-action verifier**（动作级校验，可做 RLVR）+ **Pareto（性能×成本）评分** | 执行/搜索/适应/时序/歧义/多 agent 协作 | 成长（ICLR 2026 Oral） | GPT-5(high) 仅 42% pass@1；ARE 开源 | 〔web〕 |
| **SWE-bench / Verified** | 真实 GitHub issue 修复；Verified=500 人筛子集 | 代码库级 bug 修复 | 事实标准→**污染**（OpenAI 已停报 Verified） | swebench.com；Verified 最高 ~81% | 〔web〕 |
| **SWE-bench Pro（SEAL）** | 1865 多语言（Py/Go/TS/JS）、GPL+私有库**抗污染**、跨 4.1 文件/107 行、250-turn 统一 harness | 长程多文件工程（抗污染） | 成长（2026 前沿标准） | Scale AI SEAL，同模型 Verified 81%→Pro ~46% | 〔web〕 |
| **SWE-bench Multilingual / Multimodal / Lite / CodeClash** | 9 语言 300 / 视觉 issue 517（私有测试）/ 轻量子集 / 目标导向开发对战 | 跨语言、多模态、低成本、目标级编码 | 成长 | swebench.com（CodeClash 2025-11） | 〔web〕 |
| **WebArena / VisualWebArena / WebArena-Verified** | 自托管可复现 web 任务（购物/论坛/GitLab/CMS/地图/wiki）程序化校验；Visual=需视觉推理 | 浏览器自主操作 | 成熟 | 单 agent 最高 ~61.7%，系统 ~71%；GPT-5.4 WebArena-Verified 67.3% | 〔web〕 |
| **Online-Mind2Web / WebVoyager / BrowseComp** | 真实在线网站浏览任务 / 端到端网页导航 / 难信息检索 | 在线浏览鲁棒性 | 成长 | GPT-5.4 Online-Mind2Web 92.8%；Surfer 2 WebVoyager 97.1% | 〔web〕 |
| **OSWorld / OSWorld-Verified** | 369 真实桌面任务，**执行校验**；Verified=厂商自报严格变体 | 跨应用桌面自主（Win/macOS/Linux） | 成长 | 已超 72.4% 人类基线（Holo3 80.4%、Claude Opus 4.x ~72%、GPT-5.4 75%） | 〔web〕 |
| **AndroidWorld / WindowsAgentArena / MobileWorld** | 移动/桌面 GUI 执行校验 | 移动/桌面 GUI agent | 成长（AndroidWorld 近饱和 ~90%） | xlang/Google 系；MobileWorld 更难 | 〔web〕 |
| **Terminal-Bench（2.0）** | 终端/命令行任务完成 | CLI/终端 agent | 成长 | 与 OSWorld/BrowseComp 并称"核心三件套" | 〔web〕 |
| **BFCL（v1–v4）** | Berkeley 函数调用榜，**AST 匹配 + 可执行校验**（非 LLM-judge）；v4=**Agentic 40%**（web 搜索/记忆/格式敏感）+ Multi-Turn 30% | **工具/函数调用准确率**（多步/多轮/agentic） | 事实标准（工具调用） | gorilla.cs.berkeley.edu，BFCL V4 ICML 2025 | 〔web〕 |
| **AppWorld** | 可执行 app 生态、跨 app 多步任务、代码式 API 调用，执行校验 | 真实 app 工具编排 | 成长 | AppWorld（ACL 2024 best paper） | 〔知识〕 |
| **ToolBench / ToolLLM** | 大规模工具调用（49 域 / 3451 工具） | 工具检索 + 调用泛化 | 成熟 | Qin et al.（ToolLLM） | 〔web〕 |
| **MCP-Bench / MCPEval / MCPToolBench++ / MCPWorld / LiveMCPBench** | **MCP 协议级**评测：28 服务器/250 工具（fuzzy 指令/多跳）；自动生成-验证-评估-judge-simulate；4000+ 服务器 AST/DAG/Pass@K；API/GUI/混合 | MCP 生态工具选择/参数/编排（回应域 4） | 成长 | MCP-Bench(Accenture,ICLR2026)；MCPEval(Salesforce)；MCPToolBench++ | 〔web〕 |
| **GDPval / TheAgentCompany** | 知识工作**产出质量**（对标人类专家交付物）/ 模拟公司端到端企业工作流 | 经济价值/企业流水线（交叉域 8） | 成长 | OpenAI GDPval；TheAgentCompany | 〔web〕 |
| **ReliabilityBench** | 生产级可靠性三维：**k-trial 一致性 × ε-扰动鲁棒 × λ-故障容忍**（混沌工程注入超时/限流/schema 漂移），Reliability Surface；correctness=**端态等价**非文本相似 | 上线前压测"production-readiness" | 实验 | arXiv:2601.06112（ReAct>Reflexion under stress） | 〔web〕 |
| **AgentBench-Live** | **方差感知**编码 agent 榜：≥3 trials、报 min/max/median（同 agent 同任务可摆 70 分）、Docker 沙箱 + pytest + LLM-judge | 诚实报方差而非单跑均值 | 实验 | jackjin1997/AgentBench-Live（MIT） | 〔web〕 |
| **AgentProp-Bench** | 工具 agent 的 judge 可靠性 + 错误**传播级联** + 运行时拦截缓解（2000 任务/2300 轨迹/100 人标） | 验证"自动判官可不可信" | 实验 | arXiv:2604.16706（substring κ=0.049；ensemble κ=0.432） | 〔web〕 |

### E. User Simulator（双控环境 / 引导用户能力评估，交叉域 7）

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **LLM user simulator** | 用 LLM 扮"用户"自动驱动多轮对话，使会话 agent 可批量自动评测 | 无法/不便拉真人跑多轮回归 | 成长 `[新增]` | τ-bench/τ²-bench 内置 | 〔web〕 |
| **环境耦合 user simulator** | 模拟用户行为受**可用工具 + 可观测状态**约束（不会瞎编不存在的设置/矛盾陈述），大幅降模拟噪声 | 要把"agent 错"与"模拟噪声"分开 | 成长 `[新增]` | τ²-bench tightly-coupled simulator | 〔web〕 |
| **双控引导用户评估（Dec-POMDP）** | 用户也持工具改共享状态，评 agent **引导用户动手**的能力 | 评技术支持/协作型 agent | 成长 `[新增；交叉域7]` | τ²-bench telecom（no-user→dual-control 显著掉分） | 〔web〕 |
| **多轮场景 user simulation（评测流水线内）** | harness 自动从任务/服务器生成多轮场景并跑模拟对话再 judge | MCP/工具 agent 多轮自动评测 | 成长 `[新增]` | MCPEval `generate-scenarios`/`simulate`/`evaluate-multiturn` | 〔web〕 |

### F. 在线评估 / 可观测（OTel GenAI 语义约定 + 平台）

| 技术/平台 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **OTel GenAI 语义约定** | 跨厂商统一词汇：**model span**（`chat`/`text_completion`/`embeddings`）+ **agent span**（`create_agent`/`invoke_agent`/`execute_tool`/`invoke_workflow`）+ **MCP 子规范**（2025 末）+ 内容采集**三模式** + 评估结果事件；关键属性 `gen_ai.operation.name`/`provider.name`/`request.model`/`agent.id|name|version`/`tool.call.arguments|result`/`usage.*` | 解耦"埋点 ↔ 平台"，一套 dashboard 跨 SDK | 成长→事实标准（词汇层） `[对齐-基础；新增-agent/tool/MCP span]` | OTel GenAI SIG（2024-04 立项），v1.41 仍 Development，`OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` | 〔web〕 |
| **Langfuse** | 开源 LLM/agent 可观测；OTel 端点摄取 + trace/eval/成本归因 | 自托管、数据驻留、成本可控 | 成熟（开源可观测主力） | langfuse/langfuse（2026 被 ClickHouse 收购） | 〔web〕 |
| **Arize Phoenix** | OTel 原生、纯开源；trace + **embeddings/drift** 分析 | RAG 漂移 + agent trace 自托管 | 成熟 | Arize-ai/phoenix | 〔web〕 |
| **LangSmith** | LangChain 原生 trace/eval/dataset，可导 OTLP | LangChain/LangGraph 栈 | 成长 | LangChain | 〔web〕 |
| **Helicone** | **代理网关**式：零代码改动追踪 + 成本 | 想最省事接成本/调用追踪 | 成长 | Helicone（proxy gateway） | 〔web〕 |
| **OpenLLMetry** | Traceloop：hook 常见 SDK，**自动**发 OTel 兼容 span，落任意 collector | 不想改代码、要 OTel 原生 | 成长 | traceloop/openllmetry | 〔web〕 |
| **Braintrust / Datadog LLM Obs / SigNoz / Honeycomb GenAI** | managed eval+trace / APM 厂商 LLM 可观测 / 开源 APM / 蜂巢 GenAI | 已用对应 APM 生态 | 成长 | 各厂 | 〔web〕 |
| **Galileo Agent Reliability Platform** | **Luna-2 小模型 judge**：97% 更便宜、sub-200ms@100% 采样；agentic 指标（flow adherence/task completion/conversation quality/agent efficiency）；**工具执行前实时 guardrail**；session 级；OTel 基座、接 CrewAI/LangGraph/OpenAI Agent SDK/LlamaIndex/Strands | 100% 流量在线 eval + 实时护栏（成本可控） | 成长 `[新增]` | rungalileo.io（Luna-2 SLM judge） | 〔web〕 |
| **整条 run 级 trace（非只终答）** | 工具选择/重试次数/fallback 触发/预算用量/轨迹都可见 | agent 线上排障与归因 | 成长 `[对齐-policy第6节已提；新增-agent span落地]` | OTel agent span + 平台 | 〔web〕 |
| **在线 eval / drift / guardrail metrics / 采样 judge** | 生产持续打分 + 漂移检测 + 护栏指标；**只对随机样本跑 LLM-judge**控成本（监控成本随流量有界） | 上线后持续质量 + 成本可控监控 | 成长 `[新增]` | Phoenix drift；Galileo Luna；Sampled-Prompt-Eval 模式 | 〔web〕 |

### G. Eval-Driven CI / 自进化评分闭环

| 技术/模式 | 一句话定义 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| **pass@k / pass^k** | k 次至少 1 成功 / k 次全成功（关键路径 pass^k） | 识别高方差/不稳定流程 | 成熟 `[对齐]` | `run_eval.py` 已实现 | 〔web〕 |
| **分层 CI（确定性层→评估层）** | commit 跑规则 grader（快、阻断）；夜间/合并跑 judge（大集、异步） | 控评测成本 | 成熟 `[对齐]` | llm-eval 第 4.1 + `run_eval.py --fail-under` | 〔web〕 |
| **回归检测 + 配对 A/B** | 与 baseline 比，维度跌超阈值即阻断；配对 t/Cohen's d | 防版本回退、选版本 | 成熟 `[对齐]` | `run_eval.py compare_baseline` | 〔web〕 |
| **方差感知报告（min/max/median）** | 不只报均值，报 ≥3 trials 的极差（同 agent 同任务可摆数十分） | agent 评测必备（高随机性） | 成长 `[新增]` | AgentBench-Live | 〔web〕 |
| **With-skill vs Baseline 量化** | 带/不带某技能各跑全集，配对统计 + pass@k 证明技能"真有用" | `/经验写回` 升级为评估驱动（回应域 1/6/11） | 成长 `[新增]` | 本仓库 A/B 机制 + GEPA 反思（llm-eval 5.2） | 〔知识〕 |
| **完成判定 / 高层目标级验证 checklist** | 对照 brief 目标逐项验证（非"产物存在"表层），防过早终止（MAST FM-3.1/3.3） | 五能力成稿/出结论前统一闸 | 成长 `[新增；回应域2 P1-2]` | ChatDev 高层验证 +15.6%（MAST） | 〔web〕 |
| **轨迹 LLM-judge 诊断（MAST）** | 用 LLM-judge 给多代理轨迹打 14 失败模式标签（κ=0.88） | 多代理复盘归因 | 成熟 `[新增；回应域2]` | MAST（NeurIPS 2025） | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **评估从"终答"转向"轨迹"成为分水岭**〔web〕：DeepEval 把指标挂到 trace（端到端）与 span（组件级），提供 TaskCompletion/ToolCorrectness/ArgumentCorrectness/PlanQuality/PlanAdherence/StepEfficiency；Ragas 加 AgentGoalAccuracy/ToolCallAccuracy/TopicAdherence——业界共识："agent 可能用错误/低效/不安全的路径得到正确答案，只评终答会漏判"。
2. **Agent-as-a-Judge 兴起，超越 LLM-as-a-Judge**〔web〕：让评判官自己规划/读文件/调工具/读轨迹给中间反馈，在 DevAI 上 Judge Shift 从 LLM-judge 的 31% 降到 0.27%、接近人评；2026 出现 AJ-Bench（环境感知判官基准，最佳 F1≈0.72 未饱和）与首篇《A Survey on Agent-as-a-Judge》。
3. **"自动判官"本身需要被验证——substring/contains 判 agent 接近随机**〔web〕：AgentProp-Bench 实测子串判定与人标 κ=0.049（chance-level），3-LLM ensemble 才到 κ=0.432（moderate）；JudgeBench 显示 GPT-4o 在硬正确性判定上≈随机——"判官可信度"成为独立工程问题（直接打脸"contains 就够了"）。
4. **过程奖励从判别式走向生成式（GenRM/GenPRM）**〔web〕：把奖励建模重构为下一 token 预测 + CoT + 代码验证 + 多数投票，用 test-time 算力提验证精度；GenPRM 1.5B 经 test-time scaling 超 GPT-4o、7B 超 72B PRM（ProcessBench，AAAI 2026）——verifier 正从"标量打分器"变成"会推理会跑代码的小评审"。
5. **会话 agent 评测进入"双控/语音/知识"三连跳**〔web〕：τ-bench→τ²-bench（双控 Dec-POMDP，评 agent **引导用户动手**，no-user→dual-control 显著掉分，ICML 2026 Oral）→τ³-bench（全双工语音 + banking RAG，2026-03）；**可靠 user simulator（受环境/工具约束）**成为把"agent 错"与"模拟噪声"分开的关键。
6. **SWE-bench Verified 被判"污染"，前沿迁向抗污染 Pro**〔web〕：OpenAI 审计发现全部前沿模型与 Verified 有训练重叠、59% 硬题测试有缺陷，已停报 Verified；同一 Claude Opus 4.5 在 Verified 80.9% 但 SEAL 的 SWE-bench Pro 仅 45.9%——"评测集构建质量 = 评测可信度"，去污染（decontamination）成硬指标。
7. **计算机使用 agent 越过人类基线，但靠"统一 harness"才可比**〔web〕：OSWorld-Verified 上 Holo3 80.4%、GPT-5.4 75% 已超 72.4% 人类基线；但 SEAL 用 250-turn 统一工具链证明"同模型换 harness 分数砍半"——**scaffold（规划/记忆/恢复）与评测环境本身**已是变量，比裸模型分更决定结果。
8. **OTel GenAI 语义约定成跨厂商可观测词汇，但仍 Development**〔web〕：2024-04 立项的 GenAI SIG 已扩到 model/agent/tool/MCP/内容采集/质量评估六层，span 名（`chat`/`invoke_agent`/`execute_tool`/`invoke_workflow`）与关键属性事实上稳定一年余；但 v1.41 仍标 Development、属性名可能变，需 `OTEL_SEMCONV_STABILITY_OPT_IN` 锁版本——"先按约定埋点、锁住版本"是当前最优解。
9. **在线 eval 用"小模型判官 + 采样"压成本，guardrail 在工具执行前触发**〔web〕：Galileo Luna-2 把 LLM-judge 蒸馏成 SLM，sub-200ms@100% 采样、便宜 97%，session 级指标 + 工具执行前实时护栏；通用模式是"全量 trace 进监控、只对随机样本跑 LLM-judge"使监控成本随流量有界——线下找已知失败、线上找未知失败/漂移。
10. **可靠性 = 一致性 × 鲁棒性 × 容错，单跑成功率已不够**〔web〕：ReliabilityBench 引入 k-trial/ε-扰动/λ-故障三维 Reliability Surface + 混沌工程注入（超时/限流/schema 漂移），correctness 用"端态等价"非文本相似；并发现简单 ReAct 在压力下反超复杂 Reflexion——"production-readiness"评测正把 SRE 的混沌工程搬进 agent eval。

---

## 对标产品专家 Agent

> 核心结论：现有 `llm-eval-methodology.md` + `scripts/run_eval.py` 是一套**优秀的"单轮文本 EDD"**，但**缺"agent 轨迹 / 完成率 / 工具调用准确率 / user simulator / 在线可观测"整层**；契约测试是**存在性**非质量评分。补法仍可"**轻量文件化/提示化**"——把"轨迹评测数据模型 + 完成判定 checklist + OTel 风格 run-trace 约定"写进 policy 并扩 `run_eval.py`，**不引入 DeepEval/Inspect AI/Langfuse 重栈**（需要时再映射过去）。

| 我们现状 | 差距（点名文件） | 建议增强（P0/P1/P2） |
|---|---|---|
| `scripts/run_eval.py` 评测单元是"一条 `input`→一条 `output`/`outputs`"，grader 为 contains/regex/json/length/judge | **无 agent 轨迹数据模型**：没有"一条任务→thought/tool_call/observation 多步轨迹"，无法评**完成率/工具选择/参数正确性/步骤效率**（DeepEval/Ragas 已是标配） | **P0**：扩 `run_eval.py` JSONL schema + grader（`tool_called`/`tool_args_match`/`tool_sequence`/`step_efficiency`/`task_completion`(judge)）；新增 `policies/agent-trajectory-eval.md` | 
| `policies/llm-eval-methodology.md` 单轮 EDD 完整（四桶/三类grader/G-Eval/κ/pass@k/A-B/OTel） | 是**单轮**方法论，**无"整条 run 的轨迹/完成判定/在线"章节**；OTel 只到 model 调用级，无 agent/tool span 落地 | **P0**：新增 `policies/agent-trajectory-eval.md` 作"轨迹/完成判定 checklist + 可观测最小约定"，与现有 policy **互补对齐**（开篇声明"单轮看这边、轨迹看那边"） |
| `tests/test_product_expert_agent.py` 全是 `assertTrue(path.exists())` + `assertIn(关键词)` | **契约测试 = 存在性校验，非质量评分**（回应域 1 P2-2、域 6/11） | **P1**：`/经验写回` PR 模板新增"**With-skill vs Baseline 量化 + pass@k**"附件；评分闸纳入合并门槛（仍人审） |
| `skills/research-toolkit/` 三轮事实核查 = 写死在 research 的 evaluator | 验证**只在 research 有**；其他四能力无"完成判定/高层目标级验证"，易过早终止/表层验证（MAST FM-3.1/3.3） | **P0**：抽通用"**完成判定 checklist**"（对照 brief 目标逐项、防过早终止）入 `policies/submission-review-contract.md`，五能力共用（合域 2 P1-2 reviewer 契约） |
| 评测全靠真人对话跑多轮（无 user simulator） | **无 user simulator**：会话/多轮能力（如 AI 陪练、客服式 PRD 走查）**无法自动化回归** | **P1**：`policies/agent-trajectory-eval.md` 加"**user-simulator-lite**"——用受"任务卡+可用工具+期望终态"约束的 LLM 扮用户跑多轮（借 τ²-bench 耦合思想），产物喂 `run_eval.py` |
| 无运行时 verifier/PRM 概念（域 1 P2） | 多步轨迹无**过程级**校验，错误沿链传播无早停（AgentProp-Bench：参数错→0.62 概率传到错终答） | **P2**：先用"**LLM-judge 轻量过程检查 + reflect-when-stuck**"近似 PRM（本域提供 judge-rubric）；远期评估 GenPRM/Agent-as-a-Judge（重算力） |
| `policies/llm-eval-methodology.md` 第 6 节只列 OTel + 平台名，无落地 | **无线上可观测**：run 的工具选择/重试/fallback/预算无结构化记录，断点/复盘无据 | **P1**：定义 `tasks/{task}/.meta/run-trace.jsonl` **OTel-GenAI-风格最小约定**（span 名对齐 `invoke_agent`/`execute_tool`/`invoke_workflow` + 工具/重试/预算字段），与域 2 `orchestration-state.md` 互补 |
| judge 合同已含 κ 校准（policy 第 3 节，单轮） | 缺"**判 agent 轨迹**的 judge 量规"与 agent 侧"ensemble + TPR/TNR"校准（substring 判 agent≈随机） | **P1**：扩 `assets/judge-rubric-template.md` 增"轨迹 judge 量规"（完成度/工具正确/效率/安全）；judge 合同补"agent judge 用 ensemble + 报 TPR/TNR" |
| 契约测试是离线人触发；无在线/方差视角 | 无 pass@k **方差报告**（agent 高随机，单跑均值骗人）、无在线漂移/采样 judge | **P2**：`run_eval.py` 报告补 min/max/median（≥3 trials）；线上可观测平台（Langfuse/Phoenix）为 P2 触发式（需基建） |

---

## 落地建议

> 原则：**对齐而非重写** `llm-eval-methodology.md`（单轮 EDD 不动），只补"轨迹/完成判定/在线/verifier"层；先做"对单体 Agent 立刻可用"的 policy/protocol/轻量脚本扩展（P0/P1），需重栈（DeepEval/Inspect AI/Langfuse/GenPRM）的标 P2 并交叉引用。每条给"放哪文件 / 做什么 / 验收信号（尽量可被 `tests/` 断言）"。

### P0-1【头号】新增 `policies/agent-trajectory-eval.md`（轨迹/完成判定 checklist + 可观测最小约定）
- **放哪**：`policies/agent-trajectory-eval.md`（新文件，与 `llm-eval-methodology.md` **平级互补**——开篇明写"**单轮文本 EDD → llm-eval-methodology；多步 agent 轨迹/完成率/在线 → 本文件**"，避免重叠）。
- **做什么**：Why-First 写法，含 ①**轨迹评测数据模型**：一条任务 = `{task, trajectory:[{thought,tool,args,observation}], final, ground_truth_state}`；②**完成判定 checklist**（对照任务目标逐项、端态校验优先于文本相似、防过早终止 MAST FM-3.1）；③**工具调用准确率**口径（tool selection / argument correctness / 顺序 / 步骤效率，对齐 DeepEval/Ragas/BFCL）；④**可观测最小约定**：`tasks/{task}/.meta/run-trace.jsonl`，span 名对齐 **OTel GenAI**（`invoke_agent`/`execute_tool`/`invoke_workflow`）+ 字段（工具选择/重试次数/fallback/预算 token/轨迹），与域 2 `orchestration-state.md` 互补；⑤"哪些复用 llm-eval（桶/grader/κ/pass@k），哪些是新增"对照表。
- **验收信号**：`tests/test_product_expert_agent.py` 新增断言——文件存在且含标记 `轨迹`/`完成判定`/`工具调用准确率`/`run-trace.jsonl`/`invoke_agent`/`execute_tool`；且显式引用 `llm-eval-methodology.md` 做边界声明。

### P0-2 扩 `scripts/run_eval.py`：轨迹感知 grader + 完成判定 judge 位
- **放哪**：`skills/ai-planning-orchestrator/scripts/run_eval.py` + `assets/eval-dataset.schema.json` + `references/eval-harness-guide.md`。
- **做什么**：JSONL 用例可选带 `trajectory`/`expected_tools`/`final_state`；新增确定性 grader：`tool_called`（命中期望工具集）、`tool_args_match`（参数 JSON 子集匹配）、`tool_sequence`（顺序/DAG）、`step_efficiency`（实际步数 ≤ 期望×系数）、`end_state_equiv`（端态等价，借 ReliabilityBench 思想）；judge 类新增 `task_completion`（走现有 `--judge-cmd` 协议，rubric=完成度）。**保持纯标准库、零依赖、可复现**的现有取舍不变。
- **验收信号**：`skills/ai-planning-orchestrator/tests/test_eval_harness.py` 新增断言——上述 grader 类型可解析并对样例 trajectory 给出 pass/fail；`eval-harness-guide.md` 文档含新 grader 表。

### P0-3 通用"完成判定 / 高层目标级验证" checklist 入审核契约（合域 2 P1-2）
- **放哪**：`policies/submission-review-contract.md`（已存在）+ 被 `policies/agent-trajectory-eval.md` 引用；五能力成稿/出结论前统一引用（research 三轮核查可对齐复用）。
- **做什么**：定义最小 reviewer 闸——**对照 `tasks/{task}/brief.md` 目标逐项验证**（高层而非"产物存在"表层）、完成判定 checklist（每项目标→证据→达标？）、明确"**未达标不得终止**"（防 MAST FM-3.1/3.3，ChatDev 高层验证 +15.6%）。
- **验收信号**：契约含 `高层目标级验证`/`完成判定 checklist`/`防过早终止` 标记；至少 1 个能力（建议 PRD 或 SQL）接入并在测试断言"产出含目标级验证痕迹"。

### P1-1 `/经验写回` 升级为"评估驱动"：With-skill vs Baseline 量化（回应域 1 P2-2、域 6/11）
- **放哪**：`policies/submission-review-contract.md` 写回模板 + `policies/agent-team-methodology.md` 第三/四部分（自我进化）。
- **做什么**：写回 PR 必须附"**带技能 vs 不带技能各跑同一评测集**"的 `run_eval.py` 结果（配对均分 + Cohen's d + pass@k + 回归项）；新技能"通过率/完成率显著 ≥ baseline 且无关键维度回退"方可合并（仍人审）。把契约测试的"存在性"升级为"**存在性 + 量化对比**"双门槛。
- **验收信号**：写回模板含 `With-skill vs Baseline`/`pass@k`/`Cohen's d`/`回归项` 字段；门禁说明"量化未达标则打回"。

### P1-2 user-simulator-lite（会话/多轮能力可自动化回归）
- **放哪**：`policies/agent-trajectory-eval.md` 的"user simulator"小节 + 一段可选 `skills/ai-planning-orchestrator/scripts/` 模拟驱动器（轻量）。
- **做什么**：用受"**任务卡 + 可用工具 + 期望终态**"约束的 LLM 扮用户（借 τ²-bench"耦合环境降噪"思想，禁止编造不存在的状态），自动跑多轮对话产出 `trajectory`，再喂 P0-2 的 `run_eval.py`；先覆盖 1–2 个会话型场景（如 AI 陪练/客服式走查）。
- **验收信号**：协议含 `user-simulator`/`受工具与终态约束`/`多轮` 标记；至少 1 个多轮场景能自动跑出 trajectory 并被评测。

### P1-3 run-trace 可观测最小约定 + 轨迹 judge 量规
- **放哪**：`policies/agent-trajectory-eval.md`（run-trace 约定）+ `skills/ai-planning-orchestrator/assets/judge-rubric-template.md`（扩"轨迹 judge 量规"）。
- **做什么**：①落地 `tasks/{task}/.meta/run-trace.jsonl`（span 名对齐 OTel GenAI，记工具选择/重试/fallback/预算/轨迹）；②judge-rubric 增"轨迹量规"（完成度/工具正确/步骤效率/安全 四维 + 取证要求）；③judge 合同补"**判 agent 轨迹用 ensemble + 报 TPR/TNR**"（因 substring 判 agent≈随机，AgentProp-Bench κ=0.049）。
- **验收信号**：模板含 `run-trace.jsonl`/`invoke_agent`/`轨迹量规`/`ensemble`/`TPR/TNR` 标记；至少一个任务实跑生成 run-trace。

### P2-1 verifier/PRM 近似（先 LLM-judge 过程检查，远期 GenPRM/Agent-as-a-Judge）
- **放哪**：`policies/agent-trajectory-eval.md` 的"过程级校验"小节（交叉域 1）。
- **做什么**：当前用"**LLM-judge 轻量过程检查 + reflect-when-stuck**"近似 PRM（受阻才查，控成本）；记为北极星：需高可靠多步校验时，评估 GenPRM（生成式 PRM）或 Agent-as-a-Judge（用 agent 评轨迹），但**需重算力/沙箱**，谨慎。
- **验收信号**：小节含 `过程级校验`/`reflect-when-stuck`/`GenPRM 北极星` 说明；不引入重依赖。

### P2-2 重栈映射 + 在线可观测平台（触发式，需基建）
- **放哪**：`policies/agent-trajectory-eval.md` 末"何时上重栈"小节。
- **做什么**：写清映射触发条件——需大规模/团队协作评测→DeepEval/Inspect AI（沙箱+200+评测）；需 RAG 指标→Ragas（交叉域 5）；需线上 trace/drift→Langfuse/Arize Phoenix（OTel 原生）；需 100% 流量在线护栏→Galileo Luna 式 SLM judge。**当前轻量定位下不立即引入**，仅给触发条件与对接点（run-trace 已按 OTel 约定，迁移成本低）。
- **验收信号**：小节含各重栈"触发条件 + 对接点"表；不产生立即依赖。

---

## 参考来源

- **Agent 轨迹评测综述/指南**〔web〕：Confident AI《LLM Agent Evaluation Metrics 2026: Tool Calling, Task Completion, Reasoning, Trace-Based》— https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide ；DeepEval Agent Eval — https://deepeval.com/guides/guides-ai-agent-evaluation ；MLflow《Top 5 Agent Evaluation Frameworks 2026》— https://mlflow.org/top-5-agent-evaluation-frameworks/ ；Agent Patterns Catalog《Agent-as-a-Judge / Eval Harness》— https://www.agentpatternscatalog.org/patterns/agent-as-judge/ 。
- **离线 harness**〔web〕：DeepEval — https://github.com/confident-ai/deepeval ；promptfoo — https://github.com/promptfoo/promptfoo ；Ragas（AgentGoalAccuracy/ToolCallAccuracy）— https://github.com/explodinggradients/ragas ；Inspect AI（UK AISI，agent/sandbox/policy limits）— https://github.com/UKGovernmentBEIS/inspect_ai ， https://inspect.aisi.org.uk/ ；lm-evaluation-harness — https://github.com/EleutherAI/lm-evaluation-harness ；OpenAI Evals — https://github.com/openai/evals ；Braintrust/LangSmith/Phoenix/MLflow 见《8 LLM Eval Tools Ranked》— https://techsy.io/en/blog/best-llm-evaluation-tools ；harness 工程实证《Towards Evaluation Engineering》— https://arxiv.org/html/2605.24213v1 。
- **LLM-as-Judge / 评委可靠性**〔web〕：AI Evals《LLM-as-Judge》（四段 prompt/三偏差/TPR-TNR/校准环）— https://www.aievals.co/techniques/llm-as-judge ；Galtea《LLM as a Judge Complete Guide》（gold set/七指标/OPRO）— https://galtea.ai/blog/llm-as-a-judge-the-complete-guide ；Deepchecks《Judge Calibration》— https://deepchecks.com/llm-judge-calibration-automated-issues/ ；《Rubric-Based Evals & LLM-as-a-Judge》（Bradley-Terry/Arena-Hard/AlpacaEval2/McNemar/Wilcoxon/Krippendorff）— https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80 ；《Benchmarking LLM-as-a-Judge for Long-Form》(JudgeBench/RewardBench/RM-Bench/LongJudgeBench)— https://arxiv.org/html/2606.01629v1 。
- **Agent-as-a-Judge / 判官基准**〔web〕：Zhuge et al.《Agent-as-a-Judge》(DevAI)— https://arxiv.org/pdf/2410.10934 ， https://github.com/metauto-ai/agent-as-a-judge ；AJ-Bench — https://aj-bench.github.io/ （arXiv:2604.18240）；《A Survey on Agent-as-a-Judge》— https://arxiv.org/html/2601.05111 ；AgentProp-Bench（substring κ=0.049）— https://arxiv.org/pdf/2604.16706 。
- **Verifier / PRM / GenRM / GenPRM**〔web〕：Zhang et al.《Generative Verifiers: Reward Modeling as Next-Token Prediction》— https://arxiv.org/pdf/2408.15240 ；Zhao et al.《GenPRM》AAAI 2026 — https://ojs.aaai.org/index.php/AAAI/article/view/40797 ， https://github.com/RyanLiu112/GenPRM （arXiv:2504.00891）；PRM/ORM（Lightman《Let's Verify Step by Step》；Qwen2.5-Math-PRM；ProcessBench）〔知识〕。
- **Agent 轨迹/能力基准**〔web〕：τ-bench(arXiv:2406.12045)/τ²-bench(arXiv:2506.07982, ICML 2026 Oral — https://icml.cc/virtual/2026/oral/71171 ， https://sierra.ai/uk/blog/benchmarking-agents-in-collaborative-real-world-scenarios )/τ³-bench — https://github.com/sierra-research/tau2-bench ， https://taubench.com ；GAIA2/ARE（Meta+HF）— https://ai.meta.com/research/publications/are-scaling-up-agent-environments-and-evaluations/ ， https://facebookresearch.github.io/meta-agents-research-environments/ ， OpenReview ICLR 2026 — https://openreview.net/forum?id=9gw03JpKK4 ；SWE-bench 全家 — https://www.swebench.com/ ， https://github.com/swe-bench/SWE-bench ；SWE-bench Pro(SEAL)— https://www.morphllm.com/swe-bench-pro ；OSWorld/WebArena/AndroidWorld/GDPval — https://agentmarketcap.ai/blog/2026/04/10/computer-use-benchmark-guide-osworld-appagent-androidworld-webagent ， https://leaderboard.steel.dev/ ， https://gentic.news/computer-use ；GPT-5.4 computer-use 数据 — https://openai.com/index/introducing-gpt-5-4/ ；BFCL V4 — https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html （ICML 2025）；AgentBench(THUDM, ICLR 2024)〔web〕；ToolBench/ToolLLM〔web〕。
- **MCP 评测**〔web〕：MCP-Bench（Accenture，ICLR 2026）— https://ar5iv.labs.arxiv.org/html/2508.20453 ， https://github.com/Accenture/mcp-bench ；MCPEval（Salesforce，含 simulate/multi-turn judge）— https://arxiv.org/html/2507.12806v2 ， https://github.com/SalesforceAIResearch/MCPEval ；MCPToolBench++（4000+ servers，AST/DAG/Pass@K）— https://www.emergentmind.com/topics/mcptoolbench ；MCPWorld（API/GUI/hybrid，arXiv:2506.07672）。
- **可靠性/方差基准**〔web〕：ReliabilityBench（k/ε/λ Reliability Surface，混沌工程）— https://arxiv.org/pdf/2601.06112 ；AgentBench-Live（方差感知 min/max）— https://github.com/jackjin1997/AgentBench-Live 。
- **在线评估 / 可观测 / OTel GenAI**〔web〕：OTel GenAI 语义约定（v1.41，agent/tool/MCP span）— Greptime《How OpenTelemetry Traces LLM Calls, Agent Reasoning, MCP Tools》 https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions ， Jacar《Agent observability with OTel GenAI semconv 2026》 https://jacar.es/en/otel-genai-observabilidad-agentes/ ， 官方 https://opentelemetry.io/docs/specs/semconv/gen-ai/ ；可观测栈对比 — Zylos《AI Agent Observability》 https://zylos.ai/research/2026-05-01-ai-agent-observability-llm-telemetry-production ， digitalapplied《AI Agent Observability 2026》 https://www.digitalapplied.com/blog/ai-agent-observability-2026-tracing-monitoring-stack-guide ， Veltrix《Langfuse/OpenLLMetry/OTel 2026》 https://veltrix.ge/blog/llm-observability-langfuse-otel-2026 ；Galileo Agent Reliability Platform（Luna-2 SLM judge）— https://www.prnewswire.com/news-releases/galileo-announces-free-agent-reliability-platform-302508172.html 。
- **本仓库对标文件**：`policies/llm-eval-methodology.md`（单轮 EDD，本域对齐）；`skills/ai-planning-orchestrator/scripts/run_eval.py`（规则 grader/pass@k/回归/A-B/judge 位）；`skills/ai-planning-orchestrator/references/eval-harness-guide.md`、`assets/eval-dataset.schema.json`、`assets/judge-rubric-template.md`；`tests/test_product_expert_agent.py`（存在性契约测试）；`policies/submission-review-contract.md`；`skills/research-toolkit/`（三轮事实核查）。

> **诚实声明**：本轮 tavily MCP（`tavily_search`）返回 `Invalid API key` 不可用；exa MCP（`web_search_exa`）可用并贡献 Agent-as-a-Judge/AJ-Bench/Survey 三条；其余 〔web〕 经内置 WebSearch/WebFetch 本轮核实。标 〔知识〕者（ORM/PRM-Lightman、AppWorld 细节）为训练知识、确有其物但未本轮逐条开页复核。各基准"最高分/排名"为本轮快照（2026-05~06），随榜单更新会变。
