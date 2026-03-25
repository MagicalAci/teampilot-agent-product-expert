# DeerFlow Runtime

DeerFlow 在这个 Skill 包里被视为"可选深度引擎"，不是基础模式的硬依赖，但现在已经接入了真实安装与真实 bridge。

## 推荐路径

```text
~/.local/share/cursor-research/vendor/deer-flow
```

## 当前包的最小约束

- doctor 会检查 DeerFlow 路径、`uv`、Python 版本以及 managed config 可写性
- 深度模式只在 DeerFlow 路径 ready、`uv` ready、Python 3.12+ 时才建议启用
- 没有 DeerFlow 时，Skill 必须降级到 Cursor 原生基础模式

## 当前包的真实集成方式

- `/调研安装` 或 `python scripts/run_pipeline.py install-stack --deerflow --json`
- 复用已有 DeerFlow，或 clone 到 `~/.local/share/cursor-research/vendor/deer-flow`
- 自动写入 `config.research-toolkit.yaml`
- 自动写入 `.env.research-toolkit.example`
- 通过 `python scripts/run_pipeline.py run-deerflow --prompt "..." --json` 调用嵌入式 `DeerFlowClient`

## 官方常见启动方式（保留）

- `make dev`
- `make docker-init && make docker-start`
- 嵌入式 Python Client

当前包优先绑定嵌入式 Python Client，因为它最适合命令触发型 Skill，不要求先起完整的 HTTP 服务。
