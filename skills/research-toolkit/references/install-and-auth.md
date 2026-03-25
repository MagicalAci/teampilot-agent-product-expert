# Install And Auth

## 接手人最短路径

如果你是第一次接手这套 Skill，优先只记住这一条：

```bash
bash scripts/bootstrap.sh --with-stack --doctor
```

然后按下面的极简规则继续：

- 缺 `TAVILY_API_KEY`：去 `~/.local/share/cursor-research/.env.research-toolkit` 里填，填完回复 `配好了`
- 缺小红书登录态：运行 `/调研授权`，扫完回复 `扫好了`
- 三层模式都 ready：直接继续 `/深度调研`

## 最小安装顺序

1. 放置 Skill 包到对应目录
2. 先运行 `bash scripts/bootstrap.sh --with-stack --doctor`
3. 根据 doctor 输出补本机私有环境变量与登录授权
4. 缺社媒登录态时，运行 `/调研授权`
5. 需要社媒抓取时，运行 `/爬取`
6. 需要整条链路时，运行 `/深度调研`

如果宿主机缺少 `python3`，`bootstrap.sh` 会优先尝试自动安装。
如果宿主机缺少 `git` / `uv` / `node`，安装链路会继续自动补齐。

## 本机私有环境文件

默认把真实密钥写到：

```text
~/.local/share/cursor-research/.env.research-toolkit
```

模板文件：

```text
~/.local/share/cursor-research/.env.research-toolkit.example
```

这个文件属于**用户本机私有配置**，不应进入可分发 Skill 包或 git 仓库。

## 环境变量

- `ARK_API_KEY`
- `TAVILY_API_KEY`
- `INFOQUEST_API_KEY`（可选）
- `OPENAI_API_KEY`（可选）
- `DEEPSEEK_API_KEY`（可选）
- `SERPAPI_API_KEY`（可选）
- `DEERFLOW_ROOT`（可选）
- `MEDIACRAWLER_ROOT`（可选）
- `XHS_DOWNLOADER_ROOT`（可选）
- `MEDIACRAWLER_AUTH_READY`（可选，但 MediaCrawler 进入社媒模式时建议显式设置）

默认策略：

- 默认 DeerFlow 模型：`ARK_API_KEY`
- 首次联网搜索引导：`TAVILY_API_KEY`
- `INFOQUEST_API_KEY` 作为可选本地搜索补充

## DeerFlow

默认安装 / 复用路径优先级：

```text
~/.local/share/cursor-research/vendor/deer-flow
```

官方真实集成方式：

- clone repo：`https://github.com/bytedance/deer-flow.git`
- 运行时：优先使用嵌入式 `DeerFlowClient`
- managed config：`config.research-toolkit.yaml`
- managed env 模板：`.env.research-toolkit.example`

如果 `DEERFLOW_ROOT` 显式传入，则只认该路径，不再回退到别的候选目录。

全流程示例：

```bash
python scripts/run_pipeline.py run-research --topic "AI coding voice tools" --keywords "AI coding voice tools,AI coding voice tools 测评,AI coding voice tools 体验" --slug demo --json
```

## MediaCrawler

默认安装 / 复用路径：

```text
~/crawlers/MediaCrawler
```

如果路径存在但平台未登录，仍然不应宣称 `social_ready` 可直接使用。

当前包要求额外的授权信号二选一：

- 环境变量：`MEDIACRAWLER_AUTH_READY=1`
- 标记文件：`~/crawlers/MediaCrawler/.auth.ready`

这个信号的含义不是"包帮你登录了"，而是"你已经在外部把登录和授权处理完了，可以允许 Skill 进入社媒模式"。

推荐授权方式：

```bash
python scripts/run_pipeline.py run-social-auth --platform xhs --open-qr --json
```

这个命令会：

1. 拉起真实小红书登录页
2. 自动提取二维码
3. 把二维码保存到本机运行时目录
4. 自动弹出二维码图片
5. 等待你扫码
6. 登录成功后写入 `~/crawlers/MediaCrawler/.auth.ready`

标准引导话术：

```text
现在只差小红书登录态。
我会直接给你二维码。
扫完后回复：扫好了
```

## 正式分发

维护者不应把开发目录原样打包给别人。

请使用：

```bash
python scripts/run_pipeline.py build-release --json
```

正式分发包会自动排除：

- `outputs/`
- `dist/`
- `__pycache__/`
- `*.pyc`

关键词抓取示例：

```bash
python scripts/run_pipeline.py run-social --platform xhs --keywords "AI口语,编程学习" --json
```

## XHS-Downloader

默认安装 / 复用路径：

```text
~/crawlers/XHS-Downloader
```

官方真实集成方式：

- clone repo：`https://github.com/JoeanAmier/XHS-Downloader.git`
- 依赖安装：`uv sync --no-dev --python 3.12`
- 如果 `XHS_DOWNLOADER_ROOT` 显式传入，则只认该路径

单链接抓取示例（fallback / 补抓）：

```bash
python scripts/run_pipeline.py run-social --platform xhs --url "https://www.xiaohongshu.com/explore/123456" --json
```
