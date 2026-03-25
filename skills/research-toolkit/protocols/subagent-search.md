# 搜索子代理协议

这份协议定义 `/竞品分析` 和 `/爬取` 在搜索阶段必须如何拆到平台级子代理。

核心原则：

- 搜索阶段不能由单一代理串行乱搜
- 默认每次新建独立搜索任务，不读取旧任务，除非用户明确要求继续或引用
- 必须显式列出子代理清单、职责、工具、产物和打回条件
- 默认按批次并发，单批最多 4 个子代理
- 每个子代理只负责一个平台或一个明确数据面

## 1. 默认搜索子代理清单

| 子代理名 | subagent_type | 负责平台 | 核心数据源 | 工具优先级 | 必须输出 |
|---|---|---|---|---|---|
| 官网结构 Agent | `research-web` | `web` | 官网、产品页、公开落地页 | Firecrawl → 浏览器 → WebFetch | `03-platforms/web/summary.md` `03-platforms/web/data.csv` |
| App Store Agent | `research-appstore` | `appstore` | App Store 搜索、详情、评论、版本记录 | AppInsight → WebSearch | `03-platforms/appstore/summary.md` `03-platforms/appstore/data.csv` |
| 小红书 Agent | `research-social` | `xiaohongshu` | 小红书笔记、详情评论、标签 | 小红书 MCP → 本地 crawler detail → WebSearch | `03-platforms/xiaohongshu/summary.md` `03-platforms/xiaohongshu/data.csv` |
| 微博 Agent | `research-social` | `weibo` | 微博搜索、热词、内容流 | 微博 MCP → WebSearch → 本地 crawler | `03-platforms/weibo/summary.md` `03-platforms/weibo/data.csv` |
| B站 Agent | `research-social` | `bilibili` | 视频搜索、简介、评论、弹幕摘要 | B站 MCP → WebSearch | `03-platforms/bilibili/summary.md` `03-platforms/bilibili/data.csv` |
| 知乎 / 问答 Agent | `research-comments` | `zhihu` | 问答、长评、测评帖 | Firecrawl → WebSearch → WebFetch | `03-platforms/zhihu/summary.md` `03-platforms/zhihu/data.csv` |
| SEO 承接 Agent | `research-seo` | `seo` | SERP、品牌词、问题词、目录页 | Firecrawl → WebSearch | `03-platforms/seo/summary.md` `03-platforms/seo/data.csv` |
| 商业化 Agent | `research-business` | `pricing` | 定价页、会员页、支付前页 | 浏览器 → WebFetch | `03-platforms/pricing/summary.md` `03-platforms/pricing/data.csv` |

说明：

- 如果本轮不看商业化，可跳过 `pricing`
- 如果本轮没有问答站证据，可跳过 `zhihu`，但必须在过程文档里记明原因
- 社媒不能只跑一个“总 social Agent”，必须拆到平台

### 小红书 Agent 特别要求

- `search xhs` 只负责建立帖子池，不算评论层完成
- 小红书 Agent 必须从帖子池里筛选高互动 / 高评论 / 高代表性帖子，再逐条执行 `detail xhs`
- 目标是把重点帖子下面的全部可抓评论带回来，而不是只保留帖子正文
- `summary.md` 必须分别说明：帖子数、已深挖详情帖数、评论总量、评论层是否抓全
- 如果只有帖子层、没有评论层，默认不能放行为高标准样本，除非用户明确豁免

## 2. 默认批次

### Batch 1

- 官网结构 Agent
- App Store Agent
- 小红书 Agent
- 微博 Agent

### Batch 2

- B站 Agent
- 知乎 / 问答 Agent
- SEO 承接 Agent
- 商业化 Agent

## 3. 每个子代理必须交付

每个子代理结束后都必须交付：

- `03-platforms/<platform>/summary.md`
- `03-platforms/<platform>/data.csv`

`summary.md` 至少包含：

- `1. 本轮任务概况`
- `2. 样本与证据面`
- `3. 关键事实信号`
- `4. 平台洞察与启发`
- `5. 风险、噪音与缺口`
- `6. 需要用户确认 / 补充`

允许：

- 子代理基于当前平台证据提炼局部判断和候选启发
- 写明“这对后续产品分析 / 用户分析 / 社媒分析 / SEO 分析 / 商业化分析有什么帮助”
- 在“需要用户确认 / 补充”里明确提出补料、纠偏和继续采集的请求

不要：

- 把单平台 `summary.md` 写成正式总报告
- 用单平台证据直接替代全局竞争判断
- 直接产出最终版 `跟 / 避 / 绕 / 观察`

`data.csv` 必须保留原始结构化数据，不写战略结论。

## 4. 工具与安装要求

- 每个平台的调用顺序、初始化动作、缺失时的安装和降级策略，统一遵循 [tooling-and-installation-protocol.md](tooling-and-installation-protocol.md)
- 子代理不能假设工具“天然可用”
- 如果首选 MCP 未安装、未登录或缺 Cookie，必须先处理工具状态，再开始采集
- 如果无法安装或初始化，必须在 `summary.md` 里写明已降级到什么方案

## 5. 禁止行为

- 不允许一个代理把所有搜索线全包掉
- 不允许把多个平台混写到一个 `summary.md`
- 不允许只给“最终结论”，不落平台标准件
- 不允许跳过子代理清单，直接说“我去搜一下”
