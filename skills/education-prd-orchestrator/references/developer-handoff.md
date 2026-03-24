# Developer Handoff

## 你接手后先看什么

1. `README.md`
2. `scripts/README.md`
3. `references/package-scope.md`
4. `tests/`
5. `fixtures/demo-product/`

## 怎么加新模板

- 模板放到 `assets/`
- 如果希望 `init-delivery` 自动播种，记得在 `scripts/eppo/runtime.py` 的 `maybe_copy_asset(...)` 列表里补上
- 同步更新 `assets/README.md`、`README.md` 和 `SKILL.md`

## 怎么加新 validator

- 先把规则写进 `references/`
- 再把校验逻辑放到 `scripts/eppo/validators.py` 或新建脚本
- 最后补 `tests/test_asset_validators.py`

## 怎么加新 fixture / benchmark

- 自动化基线样本放 `fixtures/`
- 给人阅读的 benchmark 说明放 `examples/`
- 如果新增 fixture，记得让 `package-smoke` 能跑到它

## 每次发版前最少动作

1. `python scripts/run_pipeline.py bootstrap-tools`
2. `python scripts/run_pipeline.py package-smoke --json`
3. `python -m unittest discover -s tests -v`
4. 更新 `README.md` 和 `references/package-scope.md`，确认目录树和命令没有过时
