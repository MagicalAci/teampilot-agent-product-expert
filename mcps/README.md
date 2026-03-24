# MCP 依赖说明

当前产品专家 Agent 只有「单产品分析」能力对 MCP 依赖最强，其他两项能力默认可以在无 MCP 的情况下工作。

## 单产品分析推荐 MCP

- `user-firecrawl`：官网结构、SEO 页面、知乎内容等网页抓取与结构化抽取
- `user-app-insight`：App Store 评分、评论、版本历史
- `user-xiaohongshu`：小红书帖子与评论层
- `user-weibo`：微博帖子与评论层
- `user-bilibili`：B 站视频与评论层

## 降级策略

- 如果某个 MCP 缺失，单产品分析仍可退化到 `WebSearch / WebFetch` 或人工补料模式。
- MCP 登录态、Cookie 或 API Key 不会被静默伪造；skill 应明确提示当前是“已安装 / 需安装 / 需登录初始化 / 当前降级模式”中的哪一种。
- 产品策划与 AI策划默认以本地文档、脚本和已有资产为主，不把 MCP 作为硬前置条件。
