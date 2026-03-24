# Portable Benchmark

这是 `education-prd-orchestrator` 的自包含 benchmark 说明。

它和 `hanxue-liaoliao-benchmark/` 的区别是：

- `hanxue-liaoliao-benchmark/` 是当前项目里的真实产物参考
- `portable-benchmark/` 是独立分发版的运行基线说明
- 真正用于自动化 smoke 的样本在 `fixtures/demo-product/`

## benchmark 目标

说明一份“可独立分发、可跑 validator、可给 reviewer 看”的最小交付应该至少包含：

1. `prd.md`
2. `images/` 下的真实图证或结构图
3. `html/` 下的页面稿
4. `charts/` 下的图表稿
5. `evidence/evidence-log.csv`
6. `review/` 下的 handoff 与 review summary

## 推荐验证命令

```bash
python scripts/run_pipeline.py package-smoke --json
```

## 对 reviewer 的意义

如果一个外部用户把 skill 解压到自己的 `~/.cursor/skills/` 后，连这套最小 smoke 都跑不过，就说明这个 skill 还不算真正独立可分发。
