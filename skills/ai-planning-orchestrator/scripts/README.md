# Scripts 索引

这些脚本只负责机械劳动，不替代 AI / 人的判断。

## 当前脚本

### 策划 / 交付
- `init_ai_planning_delivery.py`
  - 初始化 AI PRD、AI测试报告、开发 README、脚本包清单；`--with-eval` 同时 scaffold 策略卡/评测集/量规/评测报告/调优报告
- `validate_ai_planning_assets.py`
  - 校验 PRD / 测试报告 / README / 策略卡 / 评测报告 / 调优报告关键章节 + 评测集 JSONL
- `package_ai_script_bundle.py`
  - 把指定文件 / 目录打成 zip
- `export_svg_to_png.js`
  - 把 SVG 导出成 PNG

### 评测驱动开发（纯标准库，可在 CI 跑）
- `run_eval.py`
  - 自动化评测台：规则 grader + pass@k + 回归 + A/B + 可插拔 LLM-judge（见 `references/eval-harness-guide.md`）
- `aggregate_eval_dataset.py`
  - 评测集合并 + schema 校验 + 去重 + 桶配比/规模体检
- `gen_eval_report.py`
  - 从 result JSON 渲染评测报告，并可生成调优报告骨架

## 推荐顺序

1. 初始化：

```bash
python scripts/init_ai_planning_delivery.py demo-agent --output-dir ./out
```

2. 校验：

```bash
python scripts/validate_ai_planning_assets.py \
  --prd ./out/demo-agent-ai-prd.md \
  --test-report ./out/demo-agent-ai-test-report.md \
  --bundle-readme ./out/demo-agent-bundle-readme.md
```

3. 打包：

```bash
python scripts/package_ai_script_bundle.py ./dist/demo-agent.zip ./out
```

## 评测驱动开发推荐顺序

1. 评测集体检：

```bash
python scripts/aggregate_eval_dataset.py ./out/demo-agent-eval-dataset.jsonl \
  --report ./out/eval-dataset-health.md
```

2. 跑自动化评测（出报告 + 存结果）：

```bash
python scripts/run_eval.py --dataset ./out/demo-agent-eval-dataset.jsonl \
  --report ./out/eval-report.md --result ./out/eval-result.json
```

3. 回归 / A-B（与基线对比）：

```bash
python scripts/run_eval.py --dataset ./out/demo-agent-eval-dataset.jsonl \
  --baseline ./out/eval-result.json --report ./out/eval-report-v2.md
```
