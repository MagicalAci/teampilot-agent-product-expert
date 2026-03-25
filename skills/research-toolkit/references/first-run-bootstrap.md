# 首启自举协议（macOS）

这份文档解释 `research-toolkit` 在新机器上的第一次启动会自动做什么、哪些环节会暂停等待用户、失败后如何恢复。

## 1. 首次启动命令

```bash
bash "~/.cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" doctor
```

如果需要直接开始任务：

```bash
bash "~/.cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" init --task-card "./spca-task-card.json"
```

## 2. 首启自动动作

脚本会按这个顺序执行：

1. 检查当前系统是否为 `macOS`
2. 检查并准备 Homebrew
3. 安装 `python@3.11`
4. 安装 `ffmpeg`
5. 创建受管运行时目录 `~/.cursor/skills-runtime/research-toolkit/`
6. 创建受管 venv
7. 安装 `requirements.txt` 里的 Python 依赖
8. 运行 `doctor`
9. 报告 MCP 状态与当前降级模式

## 3. 哪些情况会暂停等用户

这些步骤不会被脚本静默替你完成：

- Homebrew 安装过程中需要系统权限确认
- 某些 MCP 需要在 Cursor 侧安装
- 小红书 / 微博等平台需要登录、Cookie 或扫码
- 浏览器深层交互需要已有 Cursor 浏览器会话

出现这些情况时，脚本或 doctor 会提示：

- `需安装`
- `需登录初始化`
- `当前降级模式`

## 4. 后续如何继续

当你已经完成安装或登录后，继续运行同一条命令即可：

```bash
bash "~/.cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" doctor
bash "~/.cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" collect --task-card "./spca-task-card.json"
```

## 5. 失败后的修复方式

如果受管运行时损坏、依赖没装完整、或你想强制重新同步依赖：

```bash
bash "~/.cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" repair
```

`repair` 会重新校验受管运行时，并重跑依赖同步。

## 6. 受管运行时位置

默认位置：

```text
~/.cursor/skills-runtime/research-toolkit/
```

其中会包含：

- `venv/`
- `logs/`
- `requirements.sha256`

## 7. 真实边界

这个 skill 已经把本地运行时准备、`ffmpeg`、以及环境自检前置到 bootstrap 层。

但它仍然不是“完全脱离 Cursor 的纯离线爬虫”：

- `collect` 依然主要消费本地导入目录
- 深层网页体验、部分平台抓取、以及登录后页面分析，仍依赖 Cursor 浏览器和 MCP 生态
- MCP 缺失时允许降级，但必须明确记录证据盲区
