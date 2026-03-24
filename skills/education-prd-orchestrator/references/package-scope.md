# Package Scope

## zip 必带

这些文件和目录应随包一起分发：

- `SKILL.md`
- `README.md`
- `requirements.txt`
- `agents/openai.yaml`
- `assets/`
- `references/`
- `scripts/`
- `fixtures/demo-product/`
- `tests/`

## 推荐一起带

- `examples/portable-benchmark/`
- `examples/example-invoke.md`
- `examples/example-validation-command.md`
- `examples/example-user-checkpoint.md`

## 可选保留

- `examples/hanxue-liaoliao-benchmark/`

它是 repo 参考 benchmark，不是独立运行的必要样本。

## 不应打进 zip 的东西

- 当前项目的 `outputs/` 或其他任务产出
- `.venv/`、runtime logs、临时目录
- 根目录下历史 zip 包
- 与这个 skill 无关的工作空间文档

## 打包后至少怎么验

1. 解压到 `~/.cursor/skills/education-prd-orchestrator/`
2. 跑 `python scripts/run_pipeline.py bootstrap-tools`
3. 跑 `python scripts/run_pipeline.py package-smoke --json`
4. 确认 smoke 返回 `contract_ok: true`、`asset_validator_exit_code: 0`、`strict_errors: []`
