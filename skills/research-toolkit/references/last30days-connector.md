# last30days Connector（海外调研引擎连接器）

last30days 在这个 Skill 包里被视为"可选海外调研引擎"，不是基础模式的硬依赖，定位与 DeerFlow / MediaCrawler 一致：**连接器 + 按需安装 + 不可用时降级**。引擎本体不进本仓库，通过 Agent Skills CLI 或插件市场安装。

- 上游仓库：`mvanhorn/last30days-skill`（MIT License）
- 引擎本体：`scripts/last30days.py`（Python 3.12+，部分平台需 Node）
- 作用：一个引擎覆盖 Reddit / X / YouTube / Hacker News / TikTok / Polymarket / Instagram / Threads / Bluesky / Web，按真实互动量打分并做跨源合并
- 执行协议见 `protocols/overseas-research.md`

## 安装方式

推荐用开放的 Agent Skills CLI 全局安装（Cursor / Codex / Claude Code 等 50+ 宿主通用）：

```bash
npx skills add mvanhorn/last30days-skill -g
# 指定宿主：npx skills add mvanhorn/last30days-skill -g -a cursor
# 更新：    npx skills update last30days -g
```

Claude Code 也可用插件市场：`/plugin marketplace add mvanhorn/last30days-skill` → `/plugin install last30days`。

`/调研安装` 会在工具链安装阶段一并尝试安装 / 检测 last30days（缺失时给出上面的安装指引，不阻塞国内通道）。

## 默认检测路径

```text
~/.cursor/skills/last30days
~/.codex/skills/last30days
~/.claude/skills/last30days
./.skills/last30days        # 项目内安装（不加 -g 时）
```

doctor 命中任一路径下的 `last30days.py` 即视为已安装。

## 运行时要求

- **Python 3.12+**（引擎硬要求；本仓库本地 venv 是 3.9，不能直接跑引擎，必须用系统 3.12+）
- 部分平台依赖：`node`（X 检索的 vendored client）、`yt-dlp`（YouTube 字幕）

## 环境变量 / Key

写入引擎自己的配置（`~/.config/last30days/.env`）或进程环境：

| 来源 | 需要什么 | 成本 |
|------|---------|------|
| Reddit（含评论）+ HN + Polymarket + GitHub | 无 | 免费，开箱即用 |
| X / Twitter | 浏览器登录 x.com 或 `AUTH_TOKEN`/`CT0`/`XAI_API_KEY` | 免费 |
| YouTube | `yt-dlp` | 免费 |
| Bluesky | `BSKY_HANDLE` + `BSKY_APP_PASSWORD` | 免费 |
| TikTok / Instagram / Threads / Pinterest | `SCRAPECREATORS_API_KEY` | 100 免费额度后 PAYG |
| Perplexity Sonar | `OPENROUTER_API_KEY` + `INCLUDE_SOURCES=perplexity` | 按量付费 |
| Web 搜索 | `BRAVE_API_KEY` | 每月 2000 免费 |

研究文件保存目录：`LAST30DAYS_MEMORY_DIR`（默认 `~/Documents/Last30Days/`）。

## 调用方式（本包对接）

作为 reasoning model，你**就是** last30days 的规划器：先做 Pre-Flight 解析海外实体，生成查询计划，再带 `--plan` 调引擎（命名实体主题必须带 `--plan`）。

```bash
# 1) 解析 Python 3.12+
for py in python3.13 python3.12 python3; do command -v "$py" >/dev/null 2>&1 && \
  "$py" -c 'import sys;raise SystemExit(0 if sys.version_info>=(3,12) else 1)' && { L30=$py; break; }; done

# 2) 写查询计划到临时文件（含 --x-handle / --github-user / --subreddits 等解析结果），再调引擎
"$L30" "$SKILL_DIR/scripts/last30days.py" "<主题>" \
  --plan "$QUERY_PLAN_FILE" \
  --emit=md \
  --save-dir "<task-root>/02-imports/last30days"
```

- `--emit=md`：输出适合归一的 markdown（也支持 `--emit=html` 直接生成可分享简报）
- 产出的 `<slug>-raw.md` 落到 `02-imports/last30days/`，再归一到 `03-normalized/overseas/`
- 也可由用户直接用上游的 `/last30days <主题>` 自然语言入口，本包负责把结果归一

## 当前包不做的事

- 不把 last30days 的 Python 引擎与测试拷进本仓库（保持轻量，随上游升级）
- 不在本仓库的 3.9 venv 里跑引擎（引擎需 3.12+）
- 不把"目录存在"误判成"可用"（仍需 Python 3.12+ 与对应平台 Key）
- 不静默伪造平台 Key 或登录态

## 不可用时的降级

未安装 / Python < 3.12 / 缺 Key / 引擎报错时，按 `protocols/overseas-research.md` 第 6 节降级为 `user-firecrawl` / `user-exa` + `WebSearch` 逐平台补抓，并在 `summary.md` 写明盲区。

## 归属与许可

- 来源：https://github.com/mvanhorn/last30days-skill ，MIT License，作者 @mvanhorn
- 本包仅做**连接器集成与产物归一**，引擎著作权与许可归上游所有
- 升级引擎：`npx skills update last30days -g`
