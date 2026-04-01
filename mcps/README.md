# MCP 依赖说明

当前产品专家 Agent 有两项能力对 MCP 依赖较强：「单产品分析」和「SQL 数据查询分析」。其他能力默认可以在无 MCP 的情况下工作。

## 单产品分析推荐 MCP

- `user-firecrawl`：官网结构、SEO 页面、知乎内容等网页抓取与结构化抽取
- `user-app-insight`：App Store 评分、评论、版本历史
- `user-xiaohongshu`：小红书帖子与评论层
- `user-weibo`：微博帖子与评论层
- `user-bilibili`：B 站视频与评论层

## SQL 数据查询分析推荐 MCP

- `user-antv-chart`：在聊天中直接渲染漏斗图、柱状图、饼图、折线图、雷达图等可视化图表

## 降级策略

- 如果某个 MCP 缺失，单产品分析仍可退化到 `WebSearch / WebFetch` 或人工补料模式。
- SQL 数据查询分析中，如果 `user-antv-chart` 缺失，可降级为纯文本 Markdown 表格输出，不影响 SQL 查询和洞察分析。
- MCP 登录态、Cookie 或 API Key 不会被静默伪造；skill 应明确提示当前是"已安装 / 需安装 / 需登录初始化 / 当前降级模式"中的哪一种。
- 产品策划与 AI策划默认以本地文档、脚本和已有资产为主，不把 MCP 作为硬前置条件。
