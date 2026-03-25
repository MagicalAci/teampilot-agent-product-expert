# Quality Gates

在声称"可用"之前，至少满足：

- `package-smoke` 通过
- `doctor` 至少返回 `basic_ready: true`
- `init-project` 成功生成完整目录骨架
- 缺少 DeerFlow 或 MediaCrawler 时，系统能明确降级而不是静默失败
- `run-research --dry-run --json` 能返回完整步骤：`doctor`、`api_smoke`、`project_init`、`deep_step`、`social_step`

在声称"深度模式 ready"之前，至少满足：

- DeerFlow 路径存在
- doctor 明确识别为 deep ready
- `run-research` 的 deep step 不是 `blocked`

在声称"社媒模式 ready"之前，至少满足：

- MediaCrawler 路径存在
- 用户已被提醒确认登录/授权状态
- 或 `XHS-Downloader` 已就绪可用于小红书链接抓取
