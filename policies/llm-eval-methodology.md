# 评测驱动开发方法论（LLM Eval & Tuning）

这是产品专家 Agent 的**评测体系参考库**，服务于 **AI策划**（`/AI评测`、`/AI调优`、`/评测集`：建评测集、搭评测体系、跑自动化评测、出评测报告与调优报告）以及任何"方案核心依赖 LLM/Prompt/结构化输出"的能力。

核心主张：**评测是 AI 功能的"单元测试"**。先定义"什么算好"，再写提示词与服务，用固定评测集持续度量、回归、调优——这就是 **评测驱动开发（Eval-Driven Development, EDD）**。

> **来源与许可**：方法论蒸馏自一组开源评测/优化项目的公开实践，技术名词（G-Eval、pass@k、Cohen's κ、Pareto 等）为业界通用知识。本文件只做**方法论目录 + 选型指引 + 落地清单**，不拷贝任何框架源码。主要参考：
> [DeepEval](https://github.com/confident-ai/deepeval)（MIT，pytest 式 LLM 评测，50+ 指标、G-Eval）·
> [promptfoo](https://github.com/promptfoo/promptfoo)（MIT，YAML/CLI 提示词回归 + 红队，500+ 攻击向量）·
> [Ragas](https://github.com/explodinggradients/ragas)（Apache-2.0，RAG 评测）·
> [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai)（UK AISI，离线可复现、安全治理）·
> [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)（MIT，200+ 学术基准）·
> [GEPA](https://github.com/gepa-ai/gepa)（反思式提示进化，arXiv:2507.19457）+ [DSPy](https://github.com/stanfordnlp/dspy)（LM 程序化优化，MIPROv2/GEPA）·
> 可观测：[Langfuse](https://github.com/langfuse/langfuse)·[Arize Phoenix](https://github.com/Arize-ai/phoenix)（Apache-2.0，OTel 原生）·[OpenTelemetry GenAI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/)。
> 配合 `policies/prompt-engineering-techniques.md`（提示词工程）与 `policies/agent-team-methodology.md`（技能编写/测试方法论）使用。

---

## 0. 七段闭环总览（从策略到调优）

一项 AI 能力的完整生命周期，本仓库统一按这条闭环推进：

```
① 定策略      ② 写提示词        ③ 建 AI 服务      ④ 汇总评测集
  (策略卡)  →   (策略先行)   →    (12-factor)   →   (黄金集 60/15/15/10)
                                                          ↓
⑦ 调优报告  ←  ⑥ 评测报告   ←   ⑤ 自动化评测   ←   评测体系(量规+grader)
  (GEPA式)      (可回归)          (分层CI/pass@k)
        └──────────────── 回归保护 ←─────────────────┘
```

- **①② 见** `skills/ai-planning-orchestrator/references/prompt-strategy-first.md`（策略→可判定指令）
- **③ 见** `skills/ai-planning-orchestrator/references/ai-service-construction.md`（AI 服务工程化）
- **④⑤⑥⑦ 见本文件** + `skills/ai-planning-orchestrator/references/eval-driven-development.md`（落地 SOP）+ `references/eval-harness-guide.md`（评测台）

原则：**先有"什么算好"（评测体系 + 评测集），再大改提示词/服务**。否则优化是在没有标尺的情况下盲调。

---

## 1. 选型速查：场景 → 工具/方法

| 你的情形 | 优先方法 | 对标开源 |
|---|---|---|
| 提示词/模型选型对比、快速回归 | 声明式用例 + 规则 grader（contains/regex/schema） | promptfoo |
| 接 CI、按维度打分、阻断发布 | 指标 grader + 阈值门禁（pass/fail） | DeepEval（pytest 式） |
| 开放式质量（连贯/有用/切题）没有标准答案 | LLM-as-judge + G-Eval 量规 | DeepEval G-Eval / Ragas |
| RAG（检索质量、忠实度、上下文相关性） | RAG 专用指标（faithfulness/context precision/recall） | Ragas |
| 安全/越狱/注入/PII 泄露 | 红队对抗集 + 安全 grader | promptfoo red-team / OWASP LLM Top 10 |
| 学术基准、跨模型横评 | 标准基准跑分 | lm-evaluation-harness |
| 自动改提示词、少样本下提升 | 反思式提示进化 / 程序化优化 | GEPA / DSPy（MIPROv2） |
| 线上可观测、追踪每次调用与评估 | OTel GenAI 语义约定 + 平台 | Langfuse / Phoenix |

**本仓库的轻量实现**：不内置上述任何重框架（与"轻量聚焦"定位一致），而是用 `scripts/run_eval.py`（纯标准库的自动化评测台，实现规则 grader + pass@k + 回归 + A/B + LLM-judge 接口位）落地同一套方法论；需要更重的能力时，按本表把方法论映射到对应开源工具。

---

## 2. 评测集汇总（Golden Dataset）

评测集是整个评测体系的地基：**评测集烂，所有分数都在骗你；评测集好，一个 `contains` 都能救命。**

### 2.1 四桶配比（按 route 不是按 app）

| 桶 | 来源 | 占比 | 证明什么 |
|---|---|---|---|
| 生产样本 | 真实流量分层采样（脱敏） | **60%** | 系统扛得住真实流量 |
| 对抗样本 | 越狱/注入语料、红队、扫描器 | **15%** | 系统在攻击下不崩 |
| 边界用例 | 领域专家手写长尾 | **15%** | 系统能处理没见过的长尾 |
| 失败回放 | 历史事故/线上 bug 复现 | **10%** | 系统不在已付过学费的 bug 上回退 |

> **自底向上 > 自顶向下**：先收集真实失败，再据此设计指标（bottom-up），比"先选指标再造数据"（top-down）更能预测线上真实崩溃。**不要只用合成数据**——纯合成集只会把 judge 校准到"合成 prompt"而非真实用户行为；合成只用于补对抗与稀有类。

### 2.2 规模（sizing）

| 规模 | 能做什么 |
|---|---|
| **30 条** | 单 route 回归的最低线（更少则通过率方差太大，1 条失败就抖 3 分） |
| **50 条** | 能稳定检出"大回归" |
| **200 条** | 对 3–5% 的小幅质量变化有统计置信 |
| **300–500 条 / route** | 单条路由的统计显著门槛（180–300 生产 + 45–75 对抗 + 45–75 边界 + 30–50 回放） |
| **>1000 条 / route** | 改用分层采样控成本，而非继续堆量 |

按 **route（意图/子任务）** 切分别建集——支持路由和财务路由的失败方式不同，要分别校准标尺。

### 2.3 评测集是"活文档"

- **事故 → 用例**：每个线上 bug / 事故复盘，转 3–5 条复现用例，钉死期望行为，永久留在"失败回放"桶——修 bug 的那个 PR 就引用这几条做回归。
- **季度复审**：每条打 `date_added`；超 1 年的复审；不再反映产品的归档。
- **去污染（decontamination）**：评测集必须与训练/微调数据、与提示词里写死的少样本**不重叠**，否则分数无意义。
- **定义清晰 scope**：一个评测集只测**一个任务**。三个提示词就要三个评测集。

### 2.4 本仓库的评测集格式

统一用 **JSONL**（一行一用例，git 友好、可 diff），字段见 `skills/ai-planning-orchestrator/assets/eval-dataset.schema.json`，最小字段：

```jsonc
{"id":"sup-001","bucket":"production","route":"客服-退款","input":{...},
 "assertions":[{"type":"contains","value":"退款"},{"type":"json_valid"}],
 "reference":"（可选）标准答案","date_added":"2026-06-05","tags":["核心路径"]}
```

桶配比/规模/schema 的体检由 `scripts/aggregate_eval_dataset.py` 自动检查。

---

## 3. 评测体系（维度 · 量规 · 三类 grader）

### 3.1 评测维度（先选维度+权重+阈值，再造数据）

通用维度（按场景增删、调权重）：

| 维度 | 权重 | 测量方式 | 参考阈值 |
|---|---|---|---|
| 准确性 / 事实正确 | 30% | 规则核对 / 参照答案 / judge | >90% |
| 相关性 / 切题 | 25% | judge 1–5 | >4.0 |
| 安全性 / 无有害输出 | 20% | 关键词/分类器 + judge | <0.1% |
| 格式合规 | 15% | JSON Schema 校验（规则） | >95% |
| 效率 / 延迟成本 | 10% | 监控（token/TTFB） | 按场景 |

场景化维度示例：教学（引导性、难度适配、鼓励性）；RAG（忠实度、上下文相关性、答案相关性）；语音（简洁度、口语自然度、端到端延迟）。

### 3.2 三类 grader（确定性优先）

| grader | 形态 | 适用 | 成本 |
|---|---|---|---|
| **规则 / 代码（确定性）** | contains/regex/equals/json_valid/json_schema/length | 格式、关键词、结构、可编程判真假的 | 最低，最快，可复现 |
| **模型 / LLM-as-judge** | G-Eval 量规打分（开放式质量） | 连贯/有用/切题/忠实度等难以编程判定的 | 中-高，需校准 |
| **人工** | 标注表单 + 量规 | 高风险、安全红线、judge 校准基准 | 最高 |

**确定性地板（deterministic floor）**：在跑 LLM-judge 前，先用规则 grader 拦掉明显失败（格式错、关键词缺、越狱命中），既降本又降噪。能用规则判的，绝不上 judge。

### 3.3 LLM-as-judge 的正确用法（G-Eval + 偏差校正）

LLM-judge 不是"调个 API 打个分"，要当成**需要自己被验证的 ML 系统**。

**G-Eval（Liu et al., EMNLP 2023）**：打分前先让 judge 生成**链式评估步骤（CoT）**再据此打分。"先列检查步骤（①核对事实 ②是否答全问题 ③口吻是否匹配人设）→ 执行 → 再出分"。好处：分更校准、过程可调试。

**量规设计**：拒绝"helpfulness"这种空泛词；用**结构化量规**：每个维度给明确判据 + **取证要求**（强制 judge 引用原文片段）+ 分维度打分 + 留 reasoning 字段。模板见 `assets/judge-rubric-template.md`。

**五大偏差与校正**（务必内建）：

| 偏差 | 现象 | 校正 |
|---|---|---|
| 位置偏差 | 成对比较里 A/B 位置左右胜率 ±10–15pp | 交换顺序各跑一次取平均；两次冲突→判平局/转人工 |
| 啰嗦偏差 | 长答案被高估 | 量规显式扣"无意义冗长"分；高风险用等长子集 |
| 自偏好 | judge 偏爱同族模型输出 +10–25% | **judge 与被测绝不同族**；轮换 judge 模型 |
| 校准漂移 | judge 模型小版本变动→分数变 | 把 **judge 模型版本 + 量规版本钉成不可变合同** |
| 量规泄漏 | 判据措辞偏向某种风格 | 中性措辞；定期人工复核 |

**校准（不可省）**：维护 50–500 条**人工标注**的金标集；用 **Cohen's κ** 量 judge-人类一致性（目标 0.6–0.8+，生产常用 75%+ 一致率）；judge 模型/量规变更或每月/每季**重校准**；判稳定性时 `temperature=0`、同输入多跑看是否翻转。

> 把 judge 当模型训：人工标注=ground truth，Cohen's κ=loss，对抗隐藏用例=留出验证集。κ 掉到阈值以下就**阻断流水线**并排查。

---

## 4. 自动化评测（分层 CI · pass@k · 回归 · A/B）

### 4.1 分层 CI（控成本是关键）

| 层 | 触发 | 用什么 | 规模/时延 |
|---|---|---|---|
| 确定性层 | 每次 commit / PR | 规则 grader（contains/regex/schema） | 50–100 条代表集，<10 分钟 |
| 评估层 | 合并到主干 / 夜间 | LLM-judge（语义/忠实度） | 1000+ 条，异步 |

- **评测集随代码版本化**：小集直接 JSONL 进仓库；大集用 DVC/平台，并把"某次评测用的数据集版本"显式绑定到 git commit。
- **硬阻断**：对关键指标（如任务完成率 TCR / 通过率）设数值阈值，回归即阻断发布。

### 4.2 可靠性指标：pass@k / pass^k

- **pass@k**：k 次尝试至少 1 次成功（pass@1=首试成功率；常用目标 pass@3 > 90%）。
- **pass^k**：k 次全部成功（更高的可靠性门槛，关键路径用 pass^3=100%）。
- 同一任务多跑看通过率，识别**高方差/不稳定**流程。

### 4.3 回归检测

以基线（baseline）为锚，新版任一维度相对下降超阈值（如 5%）即标记回归。最小实现：比较两次 result 的"分维度通过率/均分 delta"，超阈值 → `is_regression=true`。

### 4.4 A/B 对比（提示词 v1 vs v2）

固定同一评测集，两版各跑全集 → 配对 **t 检验**（p<0.05 显著）+ 效应量 **Cohen's d**（>0.8 大 / 0.5–0.8 中 / <0.5 小）。决策：

| p 值 | 效应 | 决策 |
|---|---|---|
| <0.05 | d>0.8 | 采用新版 |
| <0.05 | d<0.5 | 视成本决定 |
| ≥0.05 | — | 保留当前版本 |
| — | 某维度负向 | 不采用，先归因 |

> 本仓库 `scripts/run_eval.py` 内置：规则 grader、pass@k、baseline 回归、A/B 均值对比；统计检验在样本足够时给出，样本不足时降级为"分差 + 提示样本不足"。

---

## 5. 评测报告 & 调优报告

### 5.1 评测报告（可读、可回归、可追溯）

至少含：测试对象与版本 / 评测集（来源·桶配比·规模·版本）/ 评测体系（维度·量规·grader·judge 模型与版本）/ 总分与分维度分 / pass@k / 通过率 / **失败用例清单 + 失败聚类** / 与基线对比（回归项）/ 剩余风险。模板见 `assets/eval-report-template.md`。

### 5.2 调优报告（GEPA 式反思优化）

调优不是瞎改，是**基于失败证据的定向修改**：

1. **失败归因**：从评测报告的失败用例聚类，提炼"为什么错"（不是只知道"错了"）——这就是 GEPA 的 **Actionable Side Information（ASI）**：错误信息、推理日志、违反的判据。
2. **定向修改**：每轮只改 **3–5 处**（隔离变量，明确因果），修复优先级：格式不合规 → 违反禁止项 → 核心流程缺失 → 细节体验。
3. **重测对照**：改后跑同一评测集，与上一版 A/B 对比；**不回退已验证有效的改动**。
4. **Pareto 取舍**：若某改动在 A 类用例提升却在 B 类回退，保留两个候选在前沿上分别评估，而非用单一总分草率合并（GEPA 的 Pareto frontier 思想）。
5. **收敛标准**：策略覆盖率 ≥95%、格式合规 ≥95%、总达标率 ≥75%、迭代 ≤5 轮（达"良好"即可交付）。

**自动化调优（可选，重场景）**：把"metric 返回 分数 + 文本反馈"接给 GEPA/DSPy（`dspy.GEPA`，35× 少于 RL 的 rollouts，+10pp over MIPROv2），让 LLM 反思执行轨迹自动进化提示词。本仓库默认人工驱动迭代，重场景再映射到 GEPA。调优报告模板见 `assets/tuning-report-template.md`。

### 5.3 提示词版本管理

每版独立文件 `prompt-vX.Y.md`，头部标版本+日期+变更+对比数据；变更说明聚焦"改了什么、为什么、对比数据、采用/不采用理由"。

---

## 6. 可观测与在线评估（OTel GenAI）

线下评测（offline，发布前）解决"今天对不对"；线上评估（online，生产中）解决"持续对不对、漂移没漂移"。两者互补：线下集覆盖已知失败，线上+预发对抗测试找未知失败。

- **标准化**：用 [OpenTelemetry GenAI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/) 记录调用：`gen_ai.request.model`、`gen_ai.usage.input_tokens/output_tokens`、`gen_ai.response.finish_reasons`；内容（system/input/output messages）默认**不采集**，按需 opt-in（含敏感数据）。
- **评估结果挂到 span**：用 `gen_ai.evaluation.result` 事件，带 `gen_ai.evaluation.name / score.value / score.label / explanation`，把评估分关联到具体调用。
- **追踪整条 run，不只最终答案**：工具选择、预算用量、重试次数、fallback 是否触发都要可见（见 `references/ai-service-construction.md` 的 run-level 可观测）。
- 平台落地：Langfuse / Arize Phoenix（OTel 原生、开源）。

---

## 7. 最小落地清单（写评测前自检）

做 `/AI评测` 前，至少确认：

- [ ] **scope 单一**：这套评测只测一个任务/route
- [ ] **评测集就位**：JSONL、四桶有标注、规模达 route 下限（≥30 起步）、已脱敏去污染
- [ ] **维度+权重+阈值**：明确"什么算好"且每条可判真假
- [ ] **grader 分层**：能用规则判的用规则，开放式才上 judge
- [ ] **judge 合同**：judge 模型≠被测模型族；judge 模型版本+量规版本已钉死；有 ≥50 条人工金标做校准（κ 达标）
- [ ] **偏差校正**：成对比较做位置交换；量规含反啰嗦判据
- [ ] **基线**：有 baseline 结果可做回归/A-B 对比
- [ ] **报告**：失败用例与聚类、回归项、剩余风险会写进报告

---

## 何时查阅本方法论

- 写 `/AI评测`、`/AI调优`、`/评测集` → 查第 2–5 节 + `references/eval-driven-development.md`
- 设计 LLM-as-judge / 量规 → 查第 3 节 + `assets/judge-rubric-template.md`
- 接 CI / 跑自动化评测台 → 查第 4 节 + `references/eval-harness-guide.md`
- 调优提示词 / 出调优报告 → 查第 5 节 + `assets/tuning-report-template.md`
- 上线可观测 / 在线评估 → 查第 6 节
- 写提示词（策略先行）→ 配 `references/prompt-strategy-first.md` + `policies/prompt-engineering-techniques.md`
- 构建 AI 服务 → 配 `references/ai-service-construction.md`
