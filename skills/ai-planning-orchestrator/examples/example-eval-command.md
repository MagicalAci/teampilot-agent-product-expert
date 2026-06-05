# 评测驱动开发示例指令

> 配合 `references/eval-driven-development.md` 与 `policies/llm-eval-methodology.md`。

## `/评测集` 汇总 / 构建评测集

```markdown
/评测集 课堂讲题 Agent
目标：为讲题 Agent 建一个单一 scope 的评测集（route=讲解一道题）。
要求：
1. 四桶齐备：生产样本(脱敏)60% / 对抗15% / 边界15% / 失败回放10%
2. 每条写可判定断言（contains/json_valid/json_schema_keys/regex…）
3. 跑 aggregate_eval_dataset.py 体检：schema、桶配比、规模(≥30)
4. 历史事故各转 3–5 条复现用例，永久留在失败回放桶
```

## `/AI评测` 搭评测体系并跑评测

```markdown
/AI评测 课堂讲题 Agent
目标：搭评测体系并跑自动化评测，出可回归的评测报告。
要求：
1. 维度+权重+阈值：准确性/引导性/格式合规/安全
2. grader 分层：能用规则判的用规则；开放式(引导性)才上 LLM-judge
3. 用 judge 时：judge≠被测模型族、模型+量规版本钉死、≥50 条金标量 Cohen's κ
4. 跑 run_eval.py 出报告，含分维度、pass@k、失败聚类
```

## `/AI调优` 基于评测报告定向调优

```markdown
/AI调优 课堂讲题 Agent
目标：基于评测报告做定向调优并证明不退步。
要求：
1. 从失败聚类做归因(ASI)：为什么错，不是只知道错了
2. 本轮只改 3–5 处，回溯到提示词策略卡对应规则
3. run_eval.py --baseline 做 A/B 回归对照
4. 出调优报告：改了什么、A/B 数据、回归结论、采用理由
5. 不回退已验证有效的改动
```

## 命令行（脚本直跑）

```bash
# 评测集体检
python scripts/aggregate_eval_dataset.py evals/讲题.jsonl --report evals/health.md

# 跑评测 + 出报告 + 存结果
python scripts/run_eval.py --dataset evals/讲题.jsonl \
  --report evals/report-v1.md --result evals/result-v1.json

# 调优后做回归 / A-B
python scripts/run_eval.py --dataset evals/讲题.jsonl \
  --baseline evals/result-v1.json --report evals/report-v2.md --fail-under 0.9

# 接真实 LLM-judge（外部命令读 stdin JSON、写 stdout JSON）
python scripts/run_eval.py --dataset evals/讲题.jsonl --judge-cmd "python judge.py"
```
