# 审核门禁

> 产品：`豆包爱学`

## 审核规则

- 搜索子代理结束后必须先审核
- 不合格就定向打回
- 最多允许 5 轮

## 成稿门禁

- `WRITING_PLAN.md` 章节状态：`ready`
- `FACTCHECK_PLAN.md` 章节校验：`ready`
- `VISUAL_PLAN.md` 图证回填：`ready`
- `07-factcheck/round-1.md`：`ready`
- `07-factcheck/round-2.md`：`ready`
- `07-factcheck/round-3.md`：`ready`
- `07-factcheck/final-status.md`：`ready`
- `04-experience/EXPERIENCE_REPORT.md`：`ready`
- 成稿放行：`是`

## 审核记录

| 轮次 | 审核代理 | 结论 | 打回给谁 | 原因 | 是否放行 |
|---|---|---|---|---|---|
| 1 | `research-review` | `打回` | `App Store Agent` / `小红书 Agent` / `SEO 承接 Agent` | `appstore` 摘要写约 150 条评论，但 `data.csv` 实际仅 47 条记录（其中评论 43 条），样本说明与落盘不一致，且该平台并非结构性空白，应继续补抓；`xiaohongshu` 的 `data.csv` 未按统一 contract 落表，缺少 `id/source_id/source_channel/local_path/tier/platform/collected_at/text` 等标准字段映射；`seo` 的 `data.csv` 缺少必需的 `text` 字段，尚未满足统一核对格式。其余平台未发现把单平台总结越级写成正式总报告的明显问题。 | `否` |
| 2 | `research-review` | `通过` |  | `appstore` 已将评论样本补到 979 条、`data.csv` 总行数 983 与摘要口径一致，达到可分析门槛；`xiaohongshu/data.csv` 已补齐统一 contract 最小字段，并开始把详情帖正文/Top comments 回填到 `text`；`seo/data.csv` 已补齐 `text` 与统一字段。当前可放行到“核对采集结果”阶段，但仍不能直接写正式总报告。` | `是` |
| 3 | `research-review` | `待审核` |  |  | `否` |
| 4 | `research-review` | `待审核` |  |  | `否` |
| 5 | `research-review` | `待审核` |  |  | `否` |

## 第 1 轮审核说明

### 门禁结论

- 本轮**不放行**到“核对采集结果”阶段。
- 原因不是 8 个平台都要重跑，而是当前仍有**1 个需要继续补抓的平台**和**2 个需要回补标准结构的平台**。

### 结构合规判断

- 8 个目标平台的 `summary.md` 与 `data.csv` 文件**均存在**。
- `web`、`appstore`、`weibo`、`bilibili`、`zhihu`、`pricing` 的 `summary.md` 基本覆盖了平台协议要求的 6 类信息。
- 8 个平台的 `summary.md` 暂未发现把单平台内容直接写成正式总报告、最终策略结论、或“跟 / 避 / 绕 / 观察”终局口径的明显越级问题。
- `xiaohongshu/data.csv` 与 `seo/data.csv` **不满足**统一 `data.csv` 最小字段 contract，当前不能直接进入后续统一核对。

### 低样本判定

#### 属于平台本身稀薄 / 结构性空白，可接受进入下一阶段的低样本

- `web`：公开 C 端 Web 入口已撤，当前低样本来自公开面天然狭窄，不是偷懒。
- `weibo`：已用登录浏览器直接验证“几乎无原生讨论”，低样本是平台现实，不是采集没做。
- `zhihu`：站内确实没有“豆包爱学”专项讨论，低样本属于结构性空白。
- `pricing`：公开定价页缺失，当前低样本主要受公开信息面限制；后续更适合在手动体验阶段补 App 内证据，而不是继续泛搜。
- `bilibili`：品牌原生内容确实稀薄，当前 30 条样本已能支撑“声量弱、缺深度测评”这一平台判断；如后续想增强用户反馈厚度，可选补 Top 视频评论/弹幕，但本轮不是主阻塞项。

#### 不是结构性空白，应该继续补抓

- `appstore`：
  - 该平台总评论基数极大，不属于“平台本身没内容”。
  - 当前 `summary.md` 写“~150 条评论”，但 `data.csv` 实际只落了 43 条评论记录，说明样本统计和落盘口径未对齐。
  - 需继续补抓 `recent/helpful` 页，至少把已声称采到的样本完整落盘；更稳妥的做法是扩到 `>= 200` 条，并优先补 1-2 星 / helpful 高权重评论。

### 打回要求

- `App Store Agent`
  - 补抓并落盘更多评论，修正“~150 条”与实际 CSV 记录数不一致的问题。
  - 明确写清每页返回条数、总落盘条数、是否达到 200 阈值。
- `小红书 Agent`
  - 不要求继续补量。
  - 需要把现有 `data.csv` 重新映射到统一字段 contract，至少补齐 `id, source_id, source_channel, title, url, local_path, tier, platform, collected_at, text`。
  - 如当前 CSV 主要存帖子层数据，需把已拿到的详情帖正文/评论证据以可核对方式回填到 `text` 或扩展字段中。
- `SEO 承接 Agent`
  - 不要求继续补量。
  - 需要把现有 `data.csv` 补成统一字段 contract，至少新增 `text` 字段承载 SERP 摘要/说明，避免后续统一核对时无法并表。

## 第 2 轮审核说明

### 门禁结论

- 本轮**放行**到“核对采集结果”阶段。
- 这次放行仅表示搜索阶段标准产物已达到下一步核对门槛，**不表示可以直接写正式总报告**。

### 本轮复核结果

- `appstore`
  - `summary.md` 已把评论量修正为 **979 条**，并明确 recent/helpful 的翻页范围与去重口径。
  - `data.csv` 当前为 **983 行**（4 条元数据 + 979 条评论），与摘要口径一致。
  - 评论样本量已明显超过 `200` 阈值，可进入后续核对与标签复查。

- `xiaohongshu`
  - `data.csv` 已补齐统一 contract 最小字段：`id/source_id/source_channel/title/url/local_path/tier/platform/collected_at/text`。
  - 至少部分详情帖已把正文与 Top comments 回填进 `text`，不再是“只有表头补齐但证据仍不可核对”的状态。
  - 当前仍以帖子层记录为主，但已足够进入“核对采集结果”阶段。

- `seo`
  - `data.csv` 已补齐 `text` 字段，并恢复到统一字段框架。
  - 每条 SERP 记录已有可核对的摘要说明，后续可以并表复核。

### 当前剩余风险（非本轮阻塞项）

- `xiaohongshu` 的 CSV 仍以搜索命中帖为主体，详情帖/评论证据没有完全拆成独立行；后续核对时应优先使用 `detail` 级记录与 `summary.md` 中的原话引用。
- `appstore` 的 helpful 排序会放大高信息量差评，适合风险分析，但不能直接当作总体情绪占比。
- `seo` 仍是 SERP 快照数据，缺少百度浏览器实测、搜索量和权威外链数据，后续只能做承接格局判断，不能外推流量规模。
