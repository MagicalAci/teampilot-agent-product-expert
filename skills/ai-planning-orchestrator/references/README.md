# References

推荐按这个顺序读：

**策略 → 提示词 → 服务（撰写前）**
1. `prompt-strategy-first.md` — ★ 策略先行的提示词工程（先定策略再撰写，5 步法 + 覆盖率自检）
2. `ai-service-construction.md` — ★ AI 服务构建最佳实践（12-factor、结构化输出、重试/幂等、降级、可观测）

**流程与平台**
3. `execution-sop.md`
4. `hellobike-platform-api.md`
5. `platform-capabilities.md` — ★ 平台能力实测矩阵（哪些能用、哪些不能、替代方案）

**评测驱动开发（建好之后）**
6. `eval-driven-development.md` — ★ EDD 落地 SOP（`/评测集`、`/AI评测`、`/AI调优` 工作流）
7. `eval-harness-guide.md` — ★ 自动化评测台 `run_eval.py` 使用指南（grader/CLI/CI）

**交接与验收**
8. `developer-handoff.md`
9. `review-checklist.md`
10. `package-scope.md`

使用方式：

- 要写提示词（先定策略再撰写）时，先看 `prompt-strategy-first.md`（配 `policies/prompt-engineering-techniques.md`）
- 要落地 AI 脚本/服务、设计 handler/重试/降级/可观测时，先看 `ai-service-construction.md`
- 要判断这轮是 `/AI策划`、`/AIPRD`、`/AI脚本` 还是 `/AI测试` 时，先看 `execution-sop.md`
- 要选模型、写模型客户端、配鉴权、用缓存时，先看 `hellobike-platform-api.md`
- 要确认平台实际支持哪些能力、有什么限制，先看 `platform-capabilities.md`
- 要建评测集、跑评测、调优时，先看 `eval-driven-development.md`（方法论事实源是 `policies/llm-eval-methodology.md`）
- 要用自动化评测台、接 CI 时，先看 `eval-harness-guide.md`
- 要给开发补 README / 调用文档时，先看 `developer-handoff.md`
- 要验收 PRD / 脚本 / 测试报告 / 评测报告时，先看 `review-checklist.md`
- 要给开发打包时，先看 `package-scope.md`
