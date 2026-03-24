# 工具调用与安装协议

这份协议定义 full 版 `single-product-competitor-analysis` 在 `macOS` 上的首启协议、MCP 状态检查方式、以及平台级降级规则。

## 1. 首入口

所有用户入口统一走：

```bash
bash "~/.cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" doctor
bash "~/.cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" init --task-card "./spca-task-card.json"
```

辅助入口：

```bash
bash "~/.cursor/skills/single-product-competitor-analysis/scripts/doctor-macos.sh"
bash "~/.cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" repair
```

不要再默认让用户手动执行 `run_pipeline.py`、手动 `pip install`、或先装系统 `ffmpeg`。

## 2. doctor 状态字典

`doctor` 会把环境分成 4 类状态：

| 状态 | 含义 | 处理方式 |
|---|---|---|
| `已安装` | 工具或 MCP 已可用 | 直接继续下一步 |
| `需安装` | 当前机器缺少该依赖 | 系统级运行时自动装；MCP 则提示用户补齐 Cursor 侧安装 |
| `需登录初始化` | 工具已存在，但缺登录 / Cookie / 扫码 | 暂停并提示用户完成登录，再继续 |
| `当前降级模式` | 首选链路不可用，正在走 fallback | 可以继续采集，但必须在 `summary.md` 明确盲区 |

## 3. 首启自动做什么

首次通过 `bootstrap-macos.sh` 运行任一命令时，脚本会：

1. 校验当前系统是否为 `macOS`
2. 自动检查并准备 Homebrew
3. 自动准备 `python@3.11`
4. 自动准备 `ffmpeg`
5. 创建受管运行时目录：`~/.cursor/skills-runtime/single-product-competitor-analysis/`
6. 创建受管 venv：`~/.cursor/skills-runtime/single-product-competitor-analysis/venv`
7. 自动安装 `requirements.txt` 里的 Python 依赖
8. 运行 `doctor`，输出 MCP 与降级状态

边界：

- 系统级运行时尽量自动安装
- MCP 是否可用会被检查，但登录 / Cookie / 扫码不会被静默伪造
- 如果用户拒绝登录或缺少某个 MCP，必须明确进入 `当前降级模式`

## 4. MCP 机器清单

当前默认检查以下 MCP：

| server_id | 角色 | 是否阻断 full 版体验 | 登录要求 | 缺失后的降级路径 |
|---|---|---|---|---|
| `cursor-ide-browser` | 深层路径体验、价格页、登录后交互 | `是` | Cursor 浏览器会话 | `WebSearch / WebFetch`，但无法覆盖深层交互路径 |
| `user-firecrawl` | 官网结构、SEO、知乎补抓 | `否` | API Key | `WebSearch / WebFetch` |
| `user-app-insight` | App Store 评分、评论、版本历史 | `否` | 无 | `WebSearch / WebFetch` |
| `user-xiaohongshu` | 小红书帖子与评论层 | `否` | 登录 / Cookie | `WebSearch / WebFetch + 本地 crawler` |
| `user-weibo` | 微博帖子与评论层 | `否` | Cookie | `WebSearch / WebFetch + 本地 crawler` |
| `user-bilibili` | B 站视频与评论层 | `否` | 无 | `WebSearch / WebFetch` |

如果 `doctor` 输出 `需安装`：

- 系统级依赖：由 `bootstrap-macos.sh` 自动处理
- MCP：提示用户在 Cursor 侧完成对应安装，然后重新运行 `doctor`

如果 `doctor` 输出 `需登录初始化`：

- 立即暂停这一路平台采集
- 提示用户完成登录 / Cookie / 扫码
- 完成后重新运行 `doctor`

## 5. 平台级工具优先级

| 平台 | 首选工具 | 首选失败后的处理 | 最终产物 |
|---|---|---|---|
| `web` | Firecrawl + 浏览器 | `WebFetch / WebSearch` | `03-platforms/web/summary.md` `03-platforms/web/data.csv` |
| `appstore` | AppInsight | `WebSearch + WebFetch` | `03-platforms/appstore/summary.md` `03-platforms/appstore/data.csv` |
| `xiaohongshu` | 小红书 MCP + 本地 crawler detail | `WebSearch + WebFetch + 本地 crawler` | `03-platforms/xiaohongshu/summary.md` `03-platforms/xiaohongshu/data.csv` |
| `weibo` | 微博 MCP | `WebSearch + WebFetch + 本地 crawler` | `03-platforms/weibo/summary.md` `03-platforms/weibo/data.csv` |
| `bilibili` | B 站 MCP | `WebSearch + WebFetch` | `03-platforms/bilibili/summary.md` `03-platforms/bilibili/data.csv` |
| `zhihu` | Firecrawl + WebSearch | `WebFetch` | `03-platforms/zhihu/summary.md` `03-platforms/zhihu/data.csv` |
| `seo` | Firecrawl + WebSearch | 浏览器 + WebFetch | `03-platforms/seo/summary.md` `03-platforms/seo/data.csv` |
| `pricing` | 浏览器 + WebFetch | `WebSearch` | `03-platforms/pricing/summary.md` `03-platforms/pricing/data.csv` |

## 6. 平台子代理执行顺序

每个平台子代理都按这个顺序执行：

1. 先跑 `doctor`，确认当前是 `已安装`、`需安装`、`需登录初始化` 还是 `当前降级模式`
2. 尝试首选 MCP / 浏览器链路
3. 缺安装时先补安装；缺登录时先补登录
4. 仍不可用时，明确记录并进入 `当前降级模式`
5. 降级后继续采集，不允许空手进入总结阶段

小红书补充规则：

- 如果 MCP 只能拿到帖子层信息，必须继续用本地 crawler 跑评论层
- 评论层拿不到时，只允许明确降级，不允许假装已经覆盖评论证据池

## 7. `summary.md` 必须回填什么

子代理的 `summary.md` 必须写明：

- 实际用了什么工具
- 为什么没有用首选工具
- `doctor` 当时显示的是 `已安装 / 需安装 / 需登录初始化 / 当前降级模式` 中哪一种
- 是否发生安装 / 登录 / Cookie 初始化
- 当前降级后还剩哪些证据盲区

## 8. 安装与初始化红线

- 不允许因为首选工具失效就直接跳过平台
- 不允许把“工具没装好”伪装成“平台没数据”
- 不允许只写总结、不落 `data.csv`
- 不允许跨平台共用一个 CSV
