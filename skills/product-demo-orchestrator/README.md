# 产品 Demo 开发编排

这是产品专家 Agent 的第 4 个重型能力包，用于快速启动并交付可演示的产品 demo。

## 支持的平台

- `web`
- `h5`
- `swiftui`

## 主命令

- `/Demo开发`
- `/Demo设计系统`
- `/Demo脚手架`
- `/Demo打磨`
- `/Demo校验`

## 目录结构

- `assets/`：初始化模板
- `references/`：方法与规则
- `scripts/`：初始化、校验、打包
- `tests/`：smoke test

## 本地 smoke test

```bash
python scripts/run_pipeline.py package-smoke --json
```
