# 自动化评测台指南（run_eval.py）

> 本仓库自带的轻量自动化评测台，**纯 Python 标准库**实现，无外部依赖，可在 CI 跑。落地 `policies/llm-eval-methodology.md` 第 4 节的规则 grader + pass@k + 回归 + A/B。
>
> 何时读：执行 `/AI评测`、`/AI调优` 跑评测/回归时；接 CI 时。

---

## 设计取舍

- **确定性优先、CI 友好**：默认对每条用例里**已捕获的 `output`** 做规则评测（不在 CI 里调模型），保证可复现、零依赖、可阻断。
- **LLM-judge 可插拔**：`judge` 类断言默认 dry-run（跳过、不计入失败），需要真打分时用 `--judge-cmd` 接外部 judge（如平台 API）。
- **真实使用两段式**：先用你的 AI 服务对评测集 `input` 跑出 `output`（写回 jsonl 的 `output`/`outputs`），再用本台评测。这样评测台本身不耦合任何模型。

---

## 评测集 JSONL 字段

一行一用例（schema 见 `assets/eval-dataset.schema.json`）：

```jsonc
{
  "id": "sup-001",                       // 必填，唯一
  "bucket": "production",                // production|adversarial|edge|failure_replay
  "route": "客服-退款",                   // 意图/子任务
  "input": "用户问句或结构化输入",         // 必填
  "output": "被测服务的实际输出",          // 评测对象（单次）
  "outputs": ["尝试1","尝试2","尝试3"],    // 可选，多次尝试→算 pass@k/pass^k（与 output 二选一）
  "assertions": [                         // 必填，≥1
    {"type": "contains", "value": "退款", "dimension": "accuracy"},
    {"type": "not_contains", "value": "免费"},
    {"type": "json_valid"},
    {"type": "judge", "dimension": "helpfulness", "min_score": 4, "rubric": "..."}
  ],
  "reference": "（可选）标准答案",
  "weight": 1.0,                          // 可选，默认 1
  "date_added": "2026-06-05",
  "tags": ["核心路径"]
}
```

## grader（断言）类型

| type | value | 判定 | grader 类 |
|---|---|---|---|
| `contains` | 子串 | output 含 value | 规则 |
| `not_contains` | 子串 | output 不含 value | 规则 |
| `equals` | 字符串 | output 去空白后等于 value | 规则 |
| `regex` | 正则 | output 匹配 value | 规则 |
| `json_valid` | — | output 可解析为 JSON | 规则 |
| `json_schema_keys` | 键名数组 | output 是 JSON 且含全部键 | 规则 |
| `max_length` | 整数 | len(output) ≤ value | 规则 |
| `min_length` | 整数 | len(output) ≥ value | 规则 |
| `judge` | — | LLM-judge 打分 ≥ `min_score` | 模型（需 --judge-cmd，否则跳过） |

每条断言可带 `dimension`，用于分维度通过率聚合。

---

## CLI

```bash
# 基础：跑评测 + 出报告 + 存结果
python scripts/run_eval.py --dataset eval-dataset.jsonl \
  --report eval-report.md --result eval-result.json

# 回归 / A-B：与基线对比
python scripts/run_eval.py --dataset eval-dataset.jsonl \
  --baseline baseline-result.json --report eval-report.md \
  --regression-threshold 0.05

# 接真实 LLM-judge（外部命令；读 stdin JSON，写 stdout JSON）
python scripts/run_eval.py --dataset eval-dataset.jsonl --judge-cmd "python my_judge.py"
```

| 参数 | 含义 | 默认 |
|---|---|---|
| `--dataset` | 评测集 jsonl（必填） | — |
| `--report` | 输出 Markdown 评测报告 | 不写 |
| `--result` | 输出结果 JSON（可作下次 baseline） | 不写 |
| `--baseline` | 基线结果 JSON，做回归/A-B | 无 |
| `--regression-threshold` | 相对下降超此比例判回归 | 0.05 |
| `--judge-cmd` | 外部 judge 命令，无则 judge 断言跳过 | 无（dry-run） |
| `--fail-under` | 总通过率低于此值进程退出码=1（CI 阻断） | 无 |

退出码：`--fail-under` 未达 或 检出回归 → 1，否则 0（便于 CI 门禁）。

### judge-cmd 协议

外部 judge 命令从 **stdin 读** 一个 JSON：`{"output":..., "reference":..., "rubric":..., "dimension":...}`，向 **stdout 写** 一个 JSON：`{"score": 1-5 或 0-1, "reasoning": "..."}`。评测台据 `min_score` 判通过。这样 judge 用什么模型/平台完全解耦（可对接 `references/hellobike-platform-api.md`）。

---

## 输出

**result JSON**（结构化，可作 baseline）：含 `summary`（总用例/通过/通过率/加权分/pass@1/pass@k/pass^k）、`by_bucket`、`by_route`、`by_dimension`、`failures`（id+失败断言）、`failure_clusters`、`dataset_meta`。

**评测报告 Markdown**（`assets/eval-report-template.md` 结构）：摘要表、分桶/分路由/分维度、pass@k、失败用例与聚类、与基线对比（回归项）、剩余风险。

---

## 接 CI（分层）

```yaml
# 每次 PR：确定性层，小集，快
- run: python scripts/run_eval.py --dataset evals/smoke.jsonl --fail-under 0.9
# 合并主干 / 夜间：评估层，大集 + judge，异步
- run: python scripts/run_eval.py --dataset evals/full.jsonl --judge-cmd "python judge.py" --baseline evals/baseline.json
```

把"某次评测用的数据集版本"绑定到 git commit；评测集随代码版本化（小集 JSONL 进仓库，大集用 DVC/平台）。
