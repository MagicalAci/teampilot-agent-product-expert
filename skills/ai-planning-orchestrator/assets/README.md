# Assets 索引

这里放的是可复用模板，不放具体项目证据。

## 当前资产

### 策划 / 交付
- `ai-prd-template.md`
  - AI PRD 主模板，服务 `/AI策划` 与 `/AIPRD`
- `test-record-template.md`
  - AI测试报告模板，服务 `/AI测试`
- `developer-readme-template.md`
  - 给开发 / 联调用的 README 与调用文档模板
- `script-bundle-manifest-template.md`
  - 脚本压缩包文件清单模板

### 提示词（策略先行）
- `prompt-strategy-card-template.md`
  - 提示词策略卡：策略→可判定指令映射表 + 覆盖率 + 六段 Prompt，服务 `/AIPRD` 写提示词前

### 评测驱动开发
- `eval-dataset-template.jsonl`
  - 评测集模板（JSONL，四桶标注 + 断言），服务 `/评测集`
- `eval-dataset.schema.json`
  - 评测集 JSON Schema（被 `aggregate_eval_dataset.py` / `run_eval.py` 校验）
- `judge-rubric-template.md`
  - LLM-as-judge 评分量规（G-Eval 风格 + 偏差校正），服务 `/AI评测`
- `eval-report-template.md`
  - 评测报告模板，服务 `/AI评测`
- `tuning-report-template.md`
  - 调优报告模板（GEPA 式反思优化），服务 `/AI调优`

## 使用原则

- `assets/` 放模板，不放案例证据
- 项目样例去 `examples/`
- 规则与口径去 `references/`
- 机械初始化优先用 `scripts/init_ai_planning_delivery.py`
