# 输出契约（Output Contract）

这是产品专家 Agent 的**关键产物机器可校验规范**——补"产物字段一致性靠人肉模板、机器无法校验"的缺口。把策略卡、AI PRD、评测报告、调优报告等关键交付物的**必填段与跨产物引用**定成 schema 契约，让 `tests/` 能断言"字段齐不齐、能否回溯"。

> 细节编目见 `findings/11-prompt-optimization-structured-output.md`。结构化输出的**强约束生成**（strict/受限解码）见 `prompt-engineering-techniques.md` 第 4 节；本文件管"**产物层**的契约与校验"。

---

## 1. 契约即 schema（先描述再生成）

关键结构化产物先用 **JSON Schema / Pydantic / Zod** 描述必填段与字段类型，再生成；模板里用稳定锚点标记（如 `<!-- schema: tuning-report v1 -->` + 必填 `##` 段），让契约测试可断言。

| 产物 | 必填段（示例） | 跨产物引用 |
|---|---|---|
| 提示词策略卡 | 目标 / 策略→指令映射 / 输出规范 / 覆盖率 | — |
| AI PRD | 问题 / 目标 / 方案 / 输入输出契约 / 风险 | → 策略卡 |
| 评测报告 | 测试对象与版本 / 评测集 / 维度分 / pass@k / 失败聚类 / 回归 | → 评测集版本 |
| 调优报告 | ASI 失败归因 / 每轮改动 / A-B(p,d) / Pareto / 回溯规则 | **调优报告.回溯规则 → 策略卡.规则编号** |

## 2. reask / 兜底（强约束落不到时的健壮性）

运行时**校验失败 → 把错误回喂 reask（≤3 次，退避）→ 仍失败降级（默认值 / 转人工 / 换软约束）**；`refusal`/拒答当一等错误处理（Instructor 模式）。铁律重申：**schema 合规 ≠ 语义正确**，必叠加语义断言（接 `self-critique-and-grounding.md`）。

## 3. 与本仓库接线
- 各 skill `assets/*.md` 模板加机器可校验锚点；`tests/` 对每类产物断言"必填段齐 + 关键字段非空 + 跨引用编号能对上"。
- AI 脚本工程化（`ai-service-construction.md`）的"输出可靠性"含：强约束级别声明 + 校验 + reask + 兜底 + 分布漂移备忘五项。
- `eval-report-template.md` 增"格式合规率 / 解析失败率"指标行（接 `llm-eval-methodology.md`）。

## 何时查阅
- 定义/校验关键交付物字段 → §1
- 输出解析健壮性 → §2
