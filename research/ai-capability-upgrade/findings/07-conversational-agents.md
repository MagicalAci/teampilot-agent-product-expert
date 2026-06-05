# 域 7：对话式 Agent 与对话管理（Conversational Agents & Dialog Management）

> 子代理：conversational-agents ｜ 回写：`research/ai-capability-upgrade/findings/07-conversational-agents.md`
> 标注规则：〔web〕= 本轮 WebSearch/WebFetch 核实（2025-2026）；〔知识〕= 既有领域知识，未逐条联网复核（按保守口径陈述）。
> 边界：本域聚焦**一段对话怎么被管理**——状态跟踪 / 槽位 / 澄清修复 / 主动·ambient / 多轮一致 / 语音 / 转人工 / 对话评估。**澄清/反问的"路由决策角度"（EVPI/信息增益、护栏拒答、转人工触发）已在域 3（意图路由）展开**，本域只取其"对话循环内的落地形态"（槽位感知澄清、grounding、确认、repair）并交叉引用；查询改写的"检索角度"与域 5（RAG）协同；persona 的"长期记忆角度"与域 6（记忆）协同；对话评估的"评测基建角度"与域 9（评估可观测）协同。

---

## 领域概述

"对话管理"是 Agent 在多轮交互里**维持一个可被检视的对话状态、决定每轮该问还是该做、并在偏差时修复共识**的那层控制流。它从经典任务型对话（TOD）的"NLU→DST→Policy→NLG"四件套，演化为 2025-2026 的两条主线：**(1) LLM 原生对话管理**——用 schema 提示让冻结大模型直接做开放词表 DST + 对话策略（SGP-TOD），把"结构化状态"当成可靠动作/确认的锚；**(2) 交互式协作**——研究实证 LLM "知道歧义却不反问"（比人类少 3× 澄清、16× 追问），于是 grounding/澄清/repair、混合主动、主动·ambient agent（notify/question/review + Agent Inbox + human-on-the-loop）成为新焦点。语音侧则分裂为**级联 STT-LLM-TTS**与**端到端 speech-to-speech**（OpenAI Realtime API 2025-08 GA），共同被"300-500ms 延迟预算 + 语义 turn detection + barge-in"三件事支配。评估上，单控环境（τ-bench）已升级为**双控、带 user simulator 的 τ²-bench**——结论是"引导用户"才是真实瓶颈（GPT 在双控电信域 pass@1 从 ~56% 跌到 34%）。对「产品专家 Agent」而言：它当前是**任务式多轮**（Cursor 聊天 + skill 内硬编码 user checkpoint + 提示技巧"处理歧义" + task-navigator 主动规划），**缺一层显式、跨能力统一的对话状态/槽位 + 系统化澄清引擎 + 主动确认 + 置信度驱动的转人工/降级**——这正是本域要补的缺口。

---

## SOTA 技术目录

> 按子类分组，共 **42 条**。列：技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源。成熟度：事实标准 / 成熟 / 成长 / 研究。

### A. 对话状态跟踪 / 槽位填充 / 任务型对话（DST / Slot Filling / TOD）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 槽位-值对状态（slot-value DST） | 把多轮里抽到的意图/约束维护成结构化"对话的记忆" | 任何需可靠取参、调 API/查库、做确认的任务 | 事实标准 | MultiWOZ / SGD 基准；JGA 为主指标 | 〔web〕 |
| 意图 + 实体抽取（NLU） | 每轮先判意图、再抽槽位实体，喂给状态管理器 | 经典 TOD 前端；与域 3 意图分类同源 | 事实标准 | 编码器槽标注 / LLM 结构化抽取 | 〔知识〕 |
| Schema-Guided DST（SGD） | 用"服务/槽位 + 描述"做 schema，零样本迁移到新域 | 域/槽位频繁变、不想为每域标注 | 成熟 | SGD 数据集；schema 编码 + cross-attention | 〔web〕 |
| 开放词表 DST（open-vocabulary） | 不固定 ontology 值，按槽名/描述动态抽值 | 值不可枚举（自由文本、长尾） | 成长 | NAACL'25 zero-shot 开放词表 pipeline | 〔web〕 |
| SGP-TOD（schema 提示建 TOD） | 冻结 LLM + DST Prompter + Policy Prompter，免训练达 SOTA 零样本 | 想用大模型直接当 TOD，不微调 | 成长 | Zhang et al. EMNLP'23（MultiWOZ/RADDLE/STAR） | 〔web〕 |
| DST-as-QA | 把"该槽现在是什么值"重写成问答题逐槽问 | 想用通用 QA 能力做可解释 DST | 成长 | NAACL'25 long.387（域分类 + QA） | 〔web〕 |
| DST-as-SRP（自精化提示） | 把 LLM 当黑盒状态跟踪器，自生成→自精化提示 | 无 ontology、要适应新槽 | 研究 | NAACL'25 long.387（首提 SRP） | 〔web〕 |
| 混合 DST（ML 抽取 + 确定性状态机） | 用 ML 理解话语、用规则/状态管理器做更新 | 要可控可观测、显式处理纠错 | 成熟（工程主流） | 2025 实践指南"hybrid"范式 | 〔web〕 |
| 纠错/改写处理（state update） | 显式处理"不，改成周六"这类覆盖/编辑 | 用户中途改主意、纠正槽值 | 成熟 | 状态管理器 merge/overwrite/confirm 逻辑 | 〔web〕 |
| 对话策略 / policy skeleton | 据当前状态决定下一动作（问/查/确认/收尾） | 需可控对话流程、新域加规则即扩展 | 成熟 | SGP-TOD Policy Prompter；policy skeleton | 〔web〕 |
| 多模态 / 语音 DST | 把 DST 扩到语音端（WavLM 对齐 LLM）端到端 | 语音 TOD、口语状态跟踪 | 研究 | Sedláček et al. 2025-06 spoken DST | 〔web〕 |

### B. 澄清 / Grounding / 修复（Clarification / Grounding / Repair，路由决策角度见域 3）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| ask-or-act 决策（该问还是该做） | 欠规约时判定"反问"还是"按单一解释直答" | 输入模糊/缺关键槽位时的第一道闸 | 成长 | Clarify-When-Necessary（NAACL'25 findings.306） | 〔web〕 |
| INTENT-SIM（意图熵估计） | 用"用户意图分布的熵"判断该不该澄清 | 想要任务无关、稳健的"何时问"信号 | 研究 | NAACL'25 findings.306 | 〔web〕 |
| 结构化不确定性 + EVPI（工具参数） | 在工具参数空间维护概率信念，用完美信息期望值选最值问 | 工具调用缺参、防幻觉补参（与域 3 EVPI 同源） | 研究 | Structured Uncertainty（arXiv 2511.08798） | 〔web〕 |
| 未来轮建模（double-turn 偏好） | 用"未来一轮的预期结果"打偏好标，教模型判何时澄清 | 训练/对齐"该问 vs 该答" | 研究 | Modeling Future Turns（ICLR 2025） | 〔web〕 |
| 交互式澄清（恢复欠规约损失） | 检测欠规约→针对性追问→用回答补全，显著回血 | 复杂任务指令含糊（代码/SE） | 成长 | Ambig-SWE（交互比非交互 +74%） | 〔web〕 |
| "识别≠行动"差距 | 模型能判出歧义却默认直答；检索上下文反而更不爱问 | 设计提示时须强制"surface 歧义" | 研究（警示） | Knowing but Not Showing（arXiv 2605.25284） | 〔web〕 |
| Grounding acts（建立共识动作） | 澄清 / 确认(acknowledgment) / 追问 三类对话行为建共同地基 | 想让多轮"对齐理解"而非假设共识 | 研究 | Grounding Gaps（NAACL'24 long.348） | 〔web〕 |
| Repair / RequestRepair（共识修复） | 检测到"裂痕(friction)"时请求/执行修复，重建共同地基 | 误解已发生、需挽回任务 | 研究 | Rifts 基准（Microsoft, ACL'25；LLM 比人少 3× 澄清/16× 追问） | 〔web〕 |
| 显式 / 隐式确认（confirmation） | 高风险槽位前显式复述确认；低风险隐式带过 | 不可逆/高代价动作前的接地 | 事实标准 | 经典 TOD confirmation 策略 | 〔知识〕 |
| 一次性问全（batch clarification） | 缺多个槽位时合并成一轮问清，避免挤牙膏 | 欠规约请求集中补全 | 成熟（最佳实践） | 与域 3"ask-or-act 门禁"一致 | 〔web〕 |

### C. 混合主动 / 主动 / Ambient（Mixed-initiative / Proactive / Ambient）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 混合主动对话（mixed-initiative） | 人机都能发起：模型该接管时接管、该让位时让位 | 协作式任务，纯被动答会低效 | 成熟（理念） | Horvitz 混合主动原则；现代 grounding 双向 initiative | 〔知识〕/〔web〕 |
| Ambient agent（环境信号驱动） | 不靠聊天框，对事件流持续响应、仅在要紧时找人 | 后台长跑、监控/邮件/告警类 | 成长 | LangChain Ambient Agents（邮件助手参考实现） | 〔web〕 |
| 三种 HITL 交互模式 | notify（通知）/ question（求输入）/ review（求批准） | 给 ambient/主动 agent 设人类介入点 | 成长 | LangChain Agent Inbox（通用 interrupt schema） | 〔web〕 |
| Agent Inbox（收件箱式 UX） | 邮件/工单式 UI 汇总所有待人处理的 agent 事项 | 多 agent、多待办需统一收口 | 成长 | dev.agentinbox.ai（接 LangGraph interrupt） | 〔web〕 |
| Human-on-the-loop（在环上） | 展示全部中间步、可暂停/纠偏/续跑，而非每步卡审 | 后台任务、用户容忍更长时延 | 成长 | LangChain UX for Agents：on-the-loop | 〔web〕 |
| 主动引导 / 跟进建议 | 主动出"下一步该问/该做"的 follow-up，降用户认知负荷 | 用户说不清需求、需被引导 | 成长 | Proactive Guidance（ACL'25 industry.50） | 〔web〕 |
| 主动信息探询（info probing） | 在对话中主动挖隐性需求/外部情报，平衡满意度与采集 | 客服/调研型，要"边服务边挖洞察" | 研究 | Proactive Info Probing（arXiv 2604.11077）；ICL-AIF（先出 3 条动作建议再答） | 〔web〕 |
| 空闲时算力主动预备（idle-time） | 用户空闲时预测未来需求、后台预取证据写入记忆 | 多轮可预测、想降感知时延 | 研究 | ProAct（arXiv 2605.25971，Future-State Prediction + Idle-Time Acquisition） | 〔web〕 |
| 主动建议 UX（accept/reject/timing） | 建议可一键接受/删除、择时呈现不打扰、反馈回流 | IDE/共享工作区式主动助手 | 成长 | Need Help?（CHI 2025 编程主动助手） | 〔web〕 |

### D. 多轮一致性 / 上下文携带 / 对话改写（Consistency / Carryover / Rewriting）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 对话式查询改写（history-aware） | 把"它/那个"等省略的 follow-up 改写成自洽独立查询再检索 | 对话式 RAG、多轮调研检索（与域 5 协同） | 事实标准 | LangChain `create_history_aware_retriever` / contextualize-question | 〔web〕 |
| 指代消解 / standalone question | 显式补全代词/省略，使每轮可独立理解 | 多轮里引用前文实体 | 成熟 | 改写 prompt"形成不依赖历史的独立问题" | 〔web〕 |
| 话题切换 / 上下文携带 | 判 STAY/BRANCH/ROUTE，留在/新建/回到话题分支 | 长对话话题跳变、上下文要瘦身 | 成长 | DriftOS STAY/BRANCH/ROUTE（详见域 3） | 〔web〕 |
| 意图漂移检测 | 跨轮聚合，判"原始目标是否悄悄偏移" | 长周期任务防跑偏（详见域 3） | 研究 | DeepContext / Intent Drift Radar（域 3） | 〔web〕 |
| Persona / 身份漂移 | 长会话后语气/人设/前后一致性衰减（8-12 轮可降 >30%） | 任何长对话、要稳住人设/口吻 | 研究（警示） | Identity Drift（arXiv 2412.00804：越大越漂、设 persona 也不够） | 〔web〕 |
| Persona 一致性度量 + 多轮 RL | 用 prompt-to-line/line-to-line/Q&A 一致性当奖励做多轮 RL | 想系统性压低 persona 漂移 | 研究 | NeurIPS'25 多轮 RL（不一致 -55%） | 〔web〕 |
| 风格/语气一致性监测与修复 | 用潜在风格嵌入算"偏离度"，超阈值触发重校准提示 | 企业级、要可观测的 persona 稳定 | 成长（业界） | EchoMode/SyncScore + EWMA 修复协议 | 〔web〕 |
| 多轮上下文工程 | 截断历史（近 N 轮/token 预算）、防截断、域术语表注入 | 控成本+降漂移+提检索精度 | 成熟（最佳实践） | history 截断 + 改写缓存 + glossary（与域 6 协同） | 〔web〕 |

### E. 语音 Agent（Voice：STT-LLM-TTS / Realtime / Turn-taking）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 端到端 speech-to-speech（Realtime） | 单模型听-想-说，省去 STT/TTS 拼接，最低 hop、情感更自然 | 低延迟、强 prosody、单供应商可接受 | 成熟（GA） | OpenAI Realtime API（2025-08 GA, gpt-realtime；支持 MCP/图像/SIP）；gpt-realtime-2 可调 reasoning effort | 〔web〕 |
| 级联 STT-LLM-TTS pipeline | STT→LLM→TTS 三段流式拼接，逐段可换模型可观测 | 要选型自由/多语种/合规/可审计 | 事实标准 | Pipecat / LiveKit Agents 管线；各段独立供应商 | 〔web〕 |
| VAD（语音活动检测） | 帧级判"有声/静音"，turn detection 的第一层 | 任何实时语音、抗背景噪/短停顿 | 事实标准 | Silero VAD | 〔web〕 |
| 语义 turn detection（端点预测） | 读部分转写+语调判"是否说完一个完整意思"，比纯静音更准 | 减少误打断、等完整 utterance | 成长（快速主流） | Smart Turn v3（Pipecat）/ TEN Turn Detection / Easy Turn / LiveKit turn detector / Deepgram Flux；FastTurn（研究） | 〔web〕 |
| Endpointing | 据转写信号"够强"即判结束，不必等静音，更快 | 想压低回合切换延迟 | 成熟 | STT 内置 endpointing | 〔web〕 |
| Barge-in（打断） | 输出时仍保持检测，听到用户说话立刻掐 TTS 交回 STT | 用户要能随时打断长回复 | 事实标准（期望） | LiveKit/Pipecat barge-in；AEC 回声消除防自触发 | 〔web〕 |
| 延迟预算（300-500ms，流式重叠） | 全链路 p50 ~300-500ms，靠各段流式重叠而非串行等待 | 任何生产语音 agent 的硬约束 | 事实标准 | STT 部分转写→LLM→TTS 首字节重叠；区域同置 | 〔web〕 |
| OSS 语音框架 | 自托管、模型无关、可控可观测 | >10-50k 分钟/月、数据主权、低延迟 | 成熟 | LiveKit Agents（Apache 2.0, AgentSession+SFU+SIP）/ Pipecat（BSD-2, FrameProcessor 管线, transport-agnostic）/ Daily Bots | 〔web〕 |
| 托管语音平台 | 自带电话/可视化流程/分析，几小时上线 | 快速上线、<10k 分钟/月、无语音工程团队 | 成熟 | Vapi（BYO 模型, DX 强）/ Retell（呼叫中心, warm transfer, 分析） | 〔web〕 |
| 流式 STT 供应商 | 低延迟流式转写、部分结果、说话人分离 | 级联管线的识别段 | 成熟 | Deepgram Nova-3（~150ms TTFT）/ AssemblyAI Universal（精度优）/ Speechmatics Ursa | 〔web〕 |
| 流式 TTS 供应商 | 流式首音频快、可换音色/情感 | 级联管线的合成段 | 成熟 | Cartesia Sonic（~40-95ms 首音频）/ ElevenLabs Flash·Turbo v2.5（质优） | 〔web〕 |
| 全双工 / 同时说听 | 双向同时音频流，更接近真人重叠对话 | 研究/前沿全双工对话 | 研究 | Moshi（défossez 2024）等 full-duplex | 〔知识〕 |
| 其他 Realtime 供应商 | OpenAI 协议成事实标准，多家兼容/竞争 | 想多模型/更高音质/更广语种 | 成长 | Gemini Live（2.5/3.1 Flash Live）/ xAI Grok Voice Agent API（2025-12）/ Hume EVI 3 / Inworld Realtime | 〔web〕 |

### F. 转人工 / 兜底 / 对话分析 / 评估（Escalation / Fallback / Analytics / Eval）

| 技术 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 转人工升级（escalation/handoff） | 检测受挫/显式求助/KB 置信低→交人工接管 | 答不了/高风险/用户要真人 | 事实标准 | NeMo Guardrails escalation flow（详见域 3）；Retell warm transfer | 〔web〕 |
| 置信度驱动兜底 | 按答案/检索置信度分流：低→重试/澄清/转人工 | 要可控质量门、HITL 升级 | 成长 | 置信阈值路由（与域 3 H 组一致） | 〔web〕 |
| 对话总结 / 交接简报 | 把多轮对话压成结构化摘要（诉求/已做/未决/证据）供交接 | 转人工/换会话/写回时保连续性 | 成熟 | 摘要 + 字段化 handoff（与域 2 交接契约一致） | 〔知识〕 |
| 双控多轮评估（τ²-bench） | 人和 agent 都能用工具、共享动态环境，评"协作+引导用户" | 评多轮任务完成 + 沟通协调 | 成长 | τ²-bench（Dec-POMDP；双控下 pass@1 显著下降）；τ-bench 前身 | 〔web〕 |
| User simulator（用户模拟器） | 受工具/可观测状态约束的模拟用户，跑可复现多轮评测 | 自动化多轮评估、回归 | 成长 | τ/τ²-bench 模拟用户；SABER 任务修正 | 〔web〕 |
| 多维奖励/end-state 评估 | 按 DB 终态 / 环境断言 / 历史核对 / 动作匹配 综合判成败 | 多轮任务"看终态而非每步" | 成长 | τ²-bench `reward_basis`（DB/COMMUNICATE/ACTION 乘积） | 〔web〕 |
| 对话质量分析（call analytics） | 自动分析通话/对话：完成率、跑题、情绪、失败点 | 运营复盘、找改进点 | 成熟（商用） | Retell/Vapi call analytics；LLM-as-judge 对话评分（域 9） | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **对话状态从"显式 ontology"走向"schema 提示 + 开放词表 + 自精化"**〔web〕：SGP-TOD/DST-as-QA/DST-as-SRP 证明冻结大模型可零样本做 DST，不再需逐域标注；但"结构化状态"本身没消失——它仍是可靠确认/取参/防漂移的锚，趋势是"LLM 理解 + 确定性状态机更新"的混合。
2. **"知道歧义却不反问"被实证为系统性缺陷**〔web〕：Rifts（ACL'25）量化 LLM 比人少 3× 澄清、16× 追问；Knowing-but-Not-Showing 指出检索上下文反而更抑制反问；Ambig-SWE 显示一旦交互可 +74%——"主动 grounding/澄清"成为可衡量、可干预的独立能力，而非提示小技巧。
3. **澄清从提示技巧升级为决策理论**〔web〕：INTENT-SIM（意图熵）、EVPI（工具参数空间的完美信息期望值）、double-turn 未来轮偏好，把"该问/问哪条/何时停"形式化为可优化目标（与域 3 趋势同源，本域强调其在对话循环+槽位空间的落地）。
4. **Ambient / 主动 agent 成为新形态**〔web〕：LangChain 把"事件驱动 + notify/question/review + Agent Inbox + human-on-the-loop"做成参考实现；主动性从"客服反问"扩展到"空闲时预取证据"（ProAct）、"主动挖业务情报"（info probing）——交互范式从"用户发起的聊天"转向"agent 在后台跑、要紧时找人"。
5. **语音 agent 双线并进且各有最佳场景**〔web〕：端到端 speech-to-speech（OpenAI Realtime 2025-08 GA, gpt-realtime/-2）主打最低 hop + 自然 prosody；级联 STT-LLM-TTS 主打选型自由/合规/可观测/成本（>10-50k 分钟/月自托管省 ~80%）。OpenAI 的 Realtime 事件 schema 成了别家兼容的事实协议。
6. **语义 turn detection 取代纯 VAD 静音阈值**〔web〕：Smart Turn v3 / TEN / Deepgram Flux / LiveKit turn detector 用"语调 + 语义"判完整意思，仅 ~20ms 开销却大幅减少误打断——"自然停顿不抢话"成为对话质量分水岭；barge-in + AEC 是标配。
7. **300-500ms 延迟预算靠"全段流式重叠"达成**〔web〕：最大杀手是 LLM 首 token，故语音侧优先选 TTFT<300ms 的中档模型（GPT-4o-mini/Haiku/Gemini Flash）而非最强推理模型；区域同置 + 预热上下文 + prompt 缓存是工程要点（真实生产中位常 1.4-1.7s，p99 3-5s）。
8. **评估从单控转向"双控 + 引导用户"**〔web〕：τ²-bench 让用户也能用工具操作共享环境，发现"引导用户/沟通协调"才是真瓶颈（GPT pass@1 从 ~56% 跌到双控电信域 34%）；评估口径走向 end-state + 多维奖励（DB/COMMUNICATE/ACTION）+ 可复现 user simulator。
9. **persona/语气漂移被单列为长会话失败模式**〔web〕：Identity Drift（越大越漂、设 persona 也不够、8-12 轮降 >30%）、多轮 RL 一致性奖励（-55%）、SyncScore+EWMA 实时修复——"人设稳定"从靠系统提示一锤子，转向"可观测 + 触发式重校准"。
10. **对话式 RAG 把"查询改写"前置为必备层**〔web〕：history-aware retriever / contextualize-question 把省略的 follow-up 改写成自洽查询，用小模型做改写降延迟、缓存改写结果——多轮检索一致性主要靠"改写"而非堆 embedding（与域 5 协同）。

---

## 对标产品专家 Agent

> 现状基线：**任务式多轮**——Cursor 聊天承载多轮；各 skill 内有硬编码的 user checkpoint 强制确认；提示层有"处理歧义"技巧；`task-navigator` 任务启动即主动分阶段规划并征求确认；`product-expert-commands` 命令/自然语言路由到 5 能力。**没有**显式跨能力统一的对话状态跟踪(DST)、没有槽位填充框架、没有系统化澄清/反问引擎、没有 grounding/repair、没有置信度驱动的转人工/降级、没有主动/ambient 形态、没有对话级评估。下面逐项给"现状→差距→增强(P0/P1/P2)"，重点回答**任务式多轮 → 加 DST + 系统化澄清引擎 + 主动确认 + 转人工/降级**。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| 各 skill 内有 user checkpoint 强制确认（如 research-toolkit Phase 0、PRD/Demo 校验点） | 确认是**写死在各 skill 的硬编码停顿点**，无统一"对话状态/槽位"模型；跨能力不一致、状态散落聊天历史易丢（对应域 2 FM1.4 丢历史） | **P0**：定义**显式对话状态约定**（每能力一个最小 slot schema：已知槽/缺失槽/已确认槽/待办），落 `tasks/{task}/.meta/dialog-state.json`，与域 2 编排状态文件互补 |
| task-navigator 主动规划+先建议再问；提示技巧"处理歧义" | 无歧义检测、无"该问还是该做"门禁、无信息增益判据——欠规约请求易**直接开跑**或**挤牙膏式反复追问**（命中 Rifts 实证的"少澄清"缺陷） | **P0**：**系统化澄清引擎**（ask-or-act 门禁）——仅当关键槽位缺失才澄清、**一次性问全**、借 EVPI/EIG 判"问的价值>打断成本"（与域 3 落地建议 6 对齐，本域补"槽位感知"版本） |
| 每能力关键槽位（产品名/目标/范围/数据库）靠模型隐式判断 | 无 **schema 化槽位定义**、无槽位填充/纠错框架（用户"不，改成 X"无显式覆盖逻辑） | **P0**：把 5 能力关键槽位 **schema 化**（slot 名/必填/校验/确认级别），用"LLM 抽取 + 确定性更新（merge/overwrite/confirm）"混合范式，借鉴 SGP-TOD/混合 DST |
| 5 能力外/低置信仅 SQL 无库时口头提醒（护栏散见域 3） | 无**统一转人工/降级**、无置信度驱动兜底——高风险产出（PRD 结论、SQL 口径、竞品判断）无"没把握就降级/求人审"的闭环 | **P0/P1**：**置信度驱动的转人工/降级 protocol**——低置信/无证据/超范围→显式降级表达或建议人工复核；与域 3 护栏路由、域 2 HITL 中断点衔接 |
| 多轮靠 Cursor 聊天历史，调研/SQL 多轮 follow-up 直接喂检索 | 无**对话改写/指代消解**：多轮调研检索时"它/那个/再深一点"易丢上下文、检索漂移 | **P1**：在 research/aibi 多轮检索前加 **history-aware 查询改写**（把 follow-up 改写成自洽独立查询），与域 5 RAG 协同 |
| persona 靠 task-navigator 的"产品专家"口吻 + 各 skill 各自语气 | 长会话 **persona/语气漂移**、跨 skill 风格不一致（命中 Identity Drift 实证） | **P1**：**persona/语气一致性约定**（统一口吻/边界/拒答风格）+ 长任务阶段性"对照基线自检"，必要时重申人设 |
| 全靠用户发起；task-navigator 只在任务启动时规划 | 无**主动跟进建议**、无 notify/question/review 模式、无"阶段完成→主动建议下一步"的结构化交互 | **P1**：**主动跟进 + 阶段确认**——每阶段结束主动给"下一步建议 + 待确认项"，借鉴 ambient 的 notify/question/review（轻量版，不引重框架） |
| 提交契约要求"对话摘要/关键过程记录" | 摘要是**人工写**、无结构化交接简报字段、无对话质量自评 | **P1**：**对话总结/交接简报模板**（诉求/已做/未决/证据/置信），写回与转人工复用；可挂 LLM-as-judge 轻量对话自评（域 9） |
| 五能力均为多步长链路任务、无多轮质量度量 | 无**多轮任务完成率/对话质量评估**、无 user simulator，无法回归"澄清是否问对、是否引导成功" | **P2**：**多轮对话评估**——借 τ²-bench 思路建轻量 user simulator + end-state 检查，评"澄清门禁/引导/完成率"（与域 9 评估基建协同） |
| 纯文本 Cursor 交互，无语音 | 无语音 agent 形态（产品专家场景以文本为主，语音非当前刚需） | **P2（北极星）**：暂不引语音；仅备忘——若未来需"语音访谈调研/口播 Demo 讲解"，按 级联 vs Realtime + 语义 turn + 300-500ms 预算 选型 |

---

## 落地建议

> 原则：与本仓库"Cursor 原生、轻量聚焦、Why-First + 渐进式披露"一致——**用 policy 文件 + .cursor 规则 + 文件约定**补齐"对话状态 / 澄清引擎 / 主动确认 / 转人工降级"，不引重对话框架。**与域 3（意图路由）强协同**：域 3 管"进来一条 query 怎么分类/路由/是否澄清的决策"，本域管"对话循环内怎么维护状态/填槽/确认/修复/收尾"——两者共用同一套澄清门禁与护栏，避免重复造。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 新建对话管理总纲 `policies/dialog-management-protocol.md`
- **放哪**：`policies/dialog-management-protocol.md`（新文件，与 `agent-team-methodology.md`、`intent-routing-methodology.md`（域 3 建议）平级）。
- **做什么**：Why-First 写法，含 ①**对话状态模型**（最小 slot schema：`{capability, known_slots, missing_slots, confirmed_slots, open_issues, confidence}`，落 `tasks/{task}/.meta/dialog-state.json`）；②**ask-or-act 澄清引擎**（缺关键槽→一次性问全；齐备→直接开跑；判据=EVPI/信息增益"问的价值>打断成本"，引域 3）；③**confirmation 分级**（高风险/不可逆槽位前显式复述确认，低风险隐式）；④**grounding/repair 最小规范**（发现误解主动 surface 而非假设共识，引 Rifts 实证）；⑤**转人工/降级**（低置信/无证据/超范围→降级表达或求人审）。
- **验收信号**：`tests/` 契约测试断言文件存在且含标记 `对话状态`/`ask-or-act`/`一次性问全`/`confirmation`/`转人工`；task-navigator 与 product-expert-commands 能引用到它。

### P0-2 task-navigator 增"澄清门禁 + 状态初始化"步
- **放哪**：`.cursor/rules/task-navigator.mdc`（已存在，"任务启动—主动分析"段内）。
- **做什么**：在输出工作规划前加一步——按目标能力的 slot schema 检查关键槽位；**缺失→一次性集中追问**（而非边跑边挤），**齐备→初始化 `dialog-state.json` 并开跑**；规划里显式标注"已确认/待确认"项。引用 `policies/dialog-management-protocol.md`。
- **验收信号**：欠规约请求（如"做个 demo"无主题/平台）触发**一次**集中追问；槽位齐备请求不再无谓追问；任务目录出现 `dialog-state.json`。

### P0-3 五能力关键槽位 schema 化 `policies/capability-slots.yaml`
- **放哪**：`policies/capability-slots.yaml`（新；也可并入 `dialog-management-protocol.md` 附录）。可与域 3 建议的 `capability-utterances.yaml` 并列复用。
- **做什么**：为 5 能力（调研/产品策划/AI策划/Demo/SQL）各列必填槽位 + 校验 + 确认级别。示例：调研={产品/方向名, 调研类型, 平台范围, 深度}；SQL={目标库(三库枚举), 指标, 时间范围}；Demo={主题, 目标平台(Web/H5), 设计风格}。槽位定义同时供"澄清门禁消费"与"契约测试校验"。
- **验收信号**：每能力 ≥3 必填槽 + 校验规则；`dialog-management-protocol` 与契约测试均能加载；SQL 库名走枚举校验（命中无部署库时按 product-expert-commands 提醒）。

### P0-4 转人工 / 降级 protocol（并入 P0-1 + 复用域 3 护栏）
- **放哪**：`policies/dialog-management-protocol.md` 的"转人工/降级"小节 + 复用域 3 `intent-router.mdc` 护栏话术 + `policies/agent-security-scan.md` 边界。
- **做什么**：统一三类兜底话术——**超范围**（非 5 能力→说明边界+替代建议）、**无证据/低置信**（关键事实没把握→降级表达+标注不确定+建议人工核验）、**高风险/不可逆**（PRD 关键结论、SQL 口径、对外资产→显式求确认/人审）。与域 2 HITL 中断点对齐。
- **验收信号**：越界/无库/低置信三类输入各有稳定话术；不再静默硬答；高风险产出前出现"待确认/建议人审"。

### P1-1 对话式查询改写（research / aibi 多轮检索）
- **放哪**：`skills/research-toolkit/protocols/`（检索相关 protocol）+ `skills/aibi-query/`（多轮提问处）；与域 5 RAG 落地协同。
- **做什么**：多轮 follow-up（"它/那个/再深一点/换个平台"）进检索前，先用轻量改写把它**补全成自洽独立查询**（指代消解 + 携带前文实体），再走采集/SQL；改写可缓存。
- **验收信号**：连续多轮调研/查数时，第 2+ 轮 follow-up 不丢主题、检索/取数命中稳定；改写结果可在过程日志查到。

### P1-2 persona / 语气一致性约定
- **放哪**：`policies/dialog-management-protocol.md` 的"persona/语气"小节（或 task-navigator 顶部人设段）。
- **做什么**：统一"产品专家"口吻/边界/拒答风格的最小约定；长任务（多阶段/多子代理）在阶段交接处**对照基线自检语气是否漂移**，必要时重申人设（借鉴 Identity Drift 实证 + SyncScore 触发式重校准的轻量版）。
- **验收信号**：长任务跨阶段语气一致；契约测试含 `persona 一致性` 标记；阶段交接简报含"语气/边界保持"勾选。

### P1-3 主动跟进建议 `.cursor` 规则（notify/question/review 轻量版）
- **放哪**：`.cursor/rules/task-navigator.mdc`（"阶段性汇报"段强化）或新增 `.cursor/rules/proactive-followup.mdc`（`alwaysApply:false`）。
- **做什么**：每阶段完成主动产出三类信号之一——**notify**（汇报本阶段产出+存放位置）、**question**（需用户输入才能继续的集中提问）、**review**（高风险动作前求批准）；并给"下一步建议（推荐能力+理由）"让用户确认（与现有"先给建议再问"衔接，结构化为固定字段）。
- **验收信号**：每阶段结束输出含"产出 / 下一步建议 / 待确认项"三段；高风险阶段不闷头跑完而是 review 求确认。

### P1-4 对话总结 / 交接简报模板（强化提交契约）
- **放哪**：`policies/submission-review-contract.md`（"提交时必须包含—对话摘要"项细化）+ 转人工/写回复用。
- **做什么**：把"对话摘要"升级为**结构化交接简报**：`诉求 / 关键决策与理由 / 已做 / 未决项 / 证据引用 / 置信与风险`；可选挂 LLM-as-judge 轻量对话自评（是否答到目标/是否该早点澄清），评估基建见域 9。
- **验收信号**：提交物含结构化交接简报字段齐全；转人工场景能据简报无缝接管。

### P2-1 多轮对话评估（借鉴 τ²-bench，交叉域 9）
- **放哪**：`tests/` 下新增对话级评测脚本 + `policies/dialog-management-protocol.md` 的"评估"小节。
- **做什么**：建轻量 **user simulator**（受任务 slot schema 约束的模拟用户）跑可复现多轮场景，按 **end-state**（最终产出是否满足 brief.md 目标）+ 过程信号（是否触发了正确的澄清/未过度追问/是否引导成功）评分；先小规模（每能力 5-10 个多轮场景）。
- **验收信号**：能跑出"澄清门禁命中率 / 过度追问率 / 多轮完成率"；纳入 `/经验写回` 的"With-skill vs Baseline"对比（与域 1、域 9 闭环）。

### P2-2 语音 Agent 北极星（仅备忘，不现在引）
- **放哪**：`policies/dialog-management-protocol.md` 附录备忘。
- **做什么**：记录——若未来出现"语音访谈式用户研究 / Demo 口播讲解 / 电话回访"真实需求，按决策树选型：单供应商低延迟→OpenAI Realtime（speech-to-speech）；要选型自由/合规/控成本→级联（Deepgram Nova-3 + 中档 LLM + Cartesia Sonic）+ LiveKit/Pipecat；必配**语义 turn detection + barge-in + 300-500ms 预算 + 流式重叠**。保持轻量，不过度工程。
- **验收信号**：备忘存在；仅在真实语音需求出现时才启动评估，不提前引依赖。

---

## 参考来源

### 对话状态 / 槽位 / TOD
- 〔web〕SGP-TOD《Building Task Bots Effortlessly via Schema-Guided LLM Prompting》(EMNLP'23 Findings) — https://aclanthology.org/2023.findings-emnlp.891/ （DST Prompter + Policy Prompter，免训练零样本 SOTA）
- 〔web〕零样本开放词表 DST（域分类 + DST-as-QA + DST-as-SRP）(NAACL'25 long.387) — https://aclanthology.org/2025.naacl-long.387.pdf
- 〔web〕Dialogue State Tracking 综述 / 2025 实践指南（混合 DST、JGA、MultiWOZ/SGD、纠错处理、spoken DST）— emergentmind.com/topics/dialogue-state-tracking-dst ；shadecoder.com（2025 guide）

### 澄清 / Grounding / 修复
- 〔web〕《Clarify When Necessary》+ INTENT-SIM（意图熵）(NAACL'25 findings.306) — https://aclanthology.org/2025.findings-naacl.306.pdf
- 〔web〕《Structured Uncertainty guided Clarification for LLM Agents》EVPI/工具参数 (arXiv 2511.08798) — https://arxiv.org/pdf/2511.08798
- 〔web〕《Modeling Future Conversation Turns to Teach LLMs to Ask Clarifying Questions》(ICLR 2025) — proceedings.iclr.cc/.../97e2df4bb8b2f1913657344a693166a2-Paper-Conference.pdf
- 〔web〕《Ambig-SWE: Interactive Agents to Overcome Underspecificity》(arXiv 2502.13069；交互 +74%) — https://arxiv.org/html/2502.13069v2
- 〔web〕《Knowing but Not Showing: LLMs Recognize Ambiguity but Rarely Ask》(arXiv 2605.25284) — https://arxiv.org/html/2605.25284v1
- 〔web〕《Grounding Gaps in Language Model Generations》(NAACL'24 long.348) — https://aclanthology.org/2024.naacl-long.348.pdf
- 〔web〕《Navigating Rifts in Human-LLM Grounding》+ Rifts 基准 (ACL'25；LLM 少 3× 澄清/16× 追问) — https://arxiv.org/html/2503.13975v2 ；github.com/microsoft/rifts

### 混合主动 / 主动 / Ambient
- 〔web〕LangChain《Introducing Ambient Agents》(notify/question/review、Agent Inbox) — https://www.langchain.com/blog/introducing-ambient-agents
- 〔web〕LangChain《UX for Agents, Part 2: Ambient》(human-on-the-loop) — https://www.langchain.com/blog/ux-for-agents-part-2-ambient ；Agent Inbox UI — dev.agentinbox.ai
- 〔web〕《Proactive Guidance of Multi-Turn Conversation in Industrial Search》(ACL'25 industry.50) — https://aclanthology.org/2025.acl-industry.50.pdf
- 〔web〕《Towards Proactive Information Probing》(arXiv 2604.11077；ICL-AIF) — https://arxiv.org/html/2604.11077v2
- 〔web〕《Anticipate and Learn: Idle-Time Compute in Proactive Agents》ProAct (arXiv 2605.25971) — https://arxiv.org/html/2605.25971v2
- 〔web〕《Need Help? Designing Proactive AI Assistants for Programming》(CHI 2025) — dl.acm.org/doi/10.1145/3706598.3714002

### 多轮一致 / 改写 / persona
- 〔web〕LangChain history-aware retriever / contextualize-question（对话式查询改写）— python.langchain.com `create_history_aware_retriever`
- 〔web〕《Examining Identity Drift in Conversations of LLM Agents》(arXiv 2412.00804；越大越漂、设 persona 也不够) — https://arxiv.org/html/2412.00804v2
- 〔web〕《Consistently Simulating Human Personas with Multi-Turn RL》(NeurIPS 2025；不一致 -55%) — openreview.net/forum?id=A0T3piHiis
- 〔web〕EchoMode/SyncScore + EWMA persona 漂移检测与修复（业界）— medium.com/@seanhongbusiness persona-drift

### 语音 Agent
- 〔web〕OpenAI《Introducing gpt-realtime and Realtime API updates》(2025-08 GA；MCP/图像/SIP；定价) — https://openai.com/index/introducing-gpt-realtime/ ；gpt-realtime-2 模型卡 — developers.openai.com/api/docs/models/gpt-realtime-2 ；Audio guide — developers.openai.com/api/docs/guides/audio
- 〔web〕《Best Voice AI Frameworks 2026》(LiveKit Agents/Pipecat/Vapi/Retell/Daily Bots/OpenAI Realtime) — futureagi.com/blog/best-voice-ai-frameworks-2026
- 〔web〕Vapi vs Retell vs LiveKit / vs Pipecat 对比 — amjid.au ；hamming.ai/resources/best-voice-agent-stack ；assemblyai.com/blog/vapi-vs-pipecat-vs-livekit ；celloip.com
- 〔web〕LiveKit《Turn Detection for Voice Agents: VAD, Endpointing, Model-Based》(barge-in) — livekit.io/blog/turn-detection-voice-agents-vad-endpointing-model-based-detection
- 〔web〕语义 turn detection：Smart Turn v3 / TEN / Easy Turn；《FastTurn》(arXiv 2604.01897) — arxiv.org/html/2604.01897
- 〔web〕延迟预算与供应商：Deepgram Nova-3 / AssemblyAI / Cartesia Sonic / ElevenLabs — introl.com（2025 ASR/TTS guide）；futureagi.com/blog/sub-500ms-voice-ai-guide-2026 ；forasoft.com/blog/article/livekit-ai-agents-guide ；channel.tel/blog/voice-ai-pipeline-stt-tts-latency-budget
- 〔web〕Realtime 替代：inworld.ai/resources/openai-realtime-api-alternatives（Gemini Live / xAI Grok Voice / Hume EVI 3）
- 〔知识〕全双工 Moshi（défossez 2024）

### 转人工 / 评估
- 〔web〕《τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment》(arXiv 2506.07982；Dec-POMDP；双控 pass@1↓) — https://arxiv.org/pdf/2506.07982 ；github.com/sierra-research/tau2-bench（reward_basis DB/COMMUNICATE/ACTION；τ-bench 前身 arXiv 2406.12045；SABER 任务修正）
- 〔web〕NeMo Guardrails escalation / 置信度驱动转人工（详见域 3 H 组）
- 〔知识〕对话总结 / 结构化交接简报；LLM-as-judge 对话评分（评估基建见域 9）

> 交叉引用：澄清/反问的路由决策角度、护栏拒答、置信度路由见 **域 3（intent-routing）**；查询改写/对话式 RAG 检索见 **域 5（rag-techniques）**；persona/上下文压缩的记忆角度见 **域 6（context-memory）**；编排状态/HITL 中断/交接契约见 **域 2（multi-agent-orchestration）**；对话评估的评测基建（user simulator/LLM-as-judge/轨迹）见 **域 9（eval-observability）**。
