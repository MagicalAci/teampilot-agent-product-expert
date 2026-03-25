# MediaCrawler Connector

MediaCrawler 在这个包里是"可选社媒连接器"，现在已经接入了真实的复用 / 自动安装逻辑。

## 默认检测路径

```text
~/crawlers/MediaCrawler
```

## 使用原则

- 路径不存在：直接降级，不阻塞整体调研
- 路径存在但未登录：提示用户先完成平台登录
- 路径存在且已登录：可进入社媒模式
- `/调研安装` 会优先复用 `~/crawlers/MediaCrawler`，找不到时再 clone 官方仓库
- 新装流程会执行 `uv sync` 和 `uv run playwright install`
- `/爬取 --keywords ...` 默认优先走 MediaCrawler

## 当前包不做的事

- 不自动伪造登录态
- 不把"目录存在"误判成"可抓取"
- 不把社媒模式作为首次可用的硬门槛

## 并行的第二连接器

包里同时支持 `XHS-Downloader`：

- 默认路径：`~/crawlers/XHS-Downloader`
- 官方仓库：`https://github.com/JoeanAmier/XHS-Downloader.git`
- 作用：当 MediaCrawler 不适合当前场景时，作为另一条社媒抓取通道
