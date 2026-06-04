# 海外调研协议（Overseas Research）

这份协议定义 `/海外调研` 以及 `/深度调研` 命中海外/出海场景时，如何用 last30days 引擎做海外社媒舆情采集，并把结果归一到本包的标准产物体系。

海外通道与国内通道是**并行的两条采集线**，不是替代关系：

- **国内通道**：小红书 / 微博 / B站 / 知乎 + App Store + 官网，按"一平台一子代理"拆分（见 `subagent-search.md`）
- **海外通道**：Reddit / X / YouTube / Hacker News / TikTok / Polymarket / Instagram / Threads / Bluesky / Web，由 **last30days 单引擎多平台覆盖**（见 `references/last30days-connector.md`）

---

## 1. 何时走海外通道

满足任一条件即应纳入海外通道：

- 调研对象是**海外产品 / 出海方向 / 英文社区**（如 Notion、Perplexity、Character.ai、海外 AI 学习工具）
- 用户明确要"看海外怎么说""Reddit / X / YouTube 上的口碑""出海竞品舆情"
- 国内平台证据不足，需要海外社区交叉验证
- 任务类型是市场全景或方向调研，且赛道有显著海外样本

`/海外调研 [主题]` 是海外通道的**快捷主入口**：跳过国内平台，直接对海外平台做一轮采集 + 归一 + 洞察；如需进入完整成稿流水线，再转 `/深度调研`。

---

## 2. 海外平台矩阵

| 平台 | last30days 数据面 | 免费/需 Key | 证据特征 |
|------|------------------|------------|----------|
| Reddit | 帖子 + 高赞评论（含 upvote 数） | 免费 | 最真实的群众观点，评论层强 |
| Hacker News | 技术圈共识，points + comments | 免费 | 开发者/技术决策视角 |
| Polymarket | 真金白银下注的赔率（odds） | 免费 | 事件概率信号，非观点 |
| GitHub | 人物 PR 速度 / 仓库 star / release | 免费 | 工程落地与产品动态 |
| X / Twitter | 热评、专家长帖、突发反应 | 浏览器登录 / Key | 第一时间信号 |
| YouTube | 长视频字幕里的可引用观点 | yt-dlp（免费） | 深度评测 |
| TikTok / Instagram / Threads | 创作者口播字幕 + 互动量 | ScrapeCreators Key | 大众文化信号 |
| Bluesky | AT 协议帖子 | App password | 后 Twitter 迁移层 |
| Web | 编辑视角的报道/对比 | 免费/Brave Key | 多信号之一，不单独支撑 |

打分哲学：**按真实互动量（赞、评论、下注、star）排序，社交相关度优先于 SEO 相关度。** 同一故事在多平台出现时合并为一个证据簇。

---

## 3. 在 Phase 2 的位置

海外通道作为 Phase 2 数据采集的**第 ⑤ 条通道**，与 DeerFlow、国内 MCP 子代理、MediaCrawler 并行：

```text
Phase 2 数据采集
├── ① DeerFlow 深度研究（市场格局/融资/行业报告）
├── ② 国内 MCP 子代理（小红书/微博/B站/知乎/官网/App Store …）
├── ③ MediaCrawler 主动采集（国内社媒，social_ready 时）
├── ④ 用户手动补充（截图/录屏/访谈）
└── ⑤ 海外采集通道（last30days：Reddit/X/YouTube/HN/TikTok/Polymarket …）
```

由独立 `overseas-research` 子代理负责，遵循 `subagent-search.md` 的并发原则（单批最多 4 个子代理，海外通道整体算 1 个子代理位）。

---

## 4. 标准执行流程

1. **就绪检查**：确认 last30days 已安装、Python 3.12+ 可用（详见连接器文档）。不可用 → 进入降级（见第 6 节）。
2. **预解析（Pre-Flight）**：作为 reasoning model，先解析主题对应的海外实体——X handle、GitHub 用户/仓库、subreddit、YouTube 频道、TikTok 标签，生成查询计划（last30days 的 `--plan`）。
3. **跑引擎**：调用 `last30days.py`（命令模板见连接器文档），产出 raw markdown + 综合简报。
4. **落原始件**：把引擎产出的 raw/brief 原样存入 `02-imports/last30days/<slug>-raw.md`，便于追溯。
5. **归一为标准件**：把引擎结果归一到 `03-normalized/overseas/`：
   - `summary.md`：六章结构（与国内平台 summary 对齐，见下）
   - `data.csv`：逐条原始证据（含平台、链接、互动量、发布时间、引用原话）
6. **证据分级**：按本包 A/B/C 标准映射（见第 5 节）。
7. **交采集审核**：与国内平台一起进入 `REVIEW_GATE`，不合格定向打回。

`03-normalized/overseas/summary.md` 六章（沿用平台标准件结构）：

```text
1. 本轮任务概况      ← 覆盖了哪些海外平台、查询计划、运行参数
2. 样本与证据面      ← 各平台样本量、评论层是否抓到、互动量分布
3. 关键事实信号      ← 跨平台合并后的高互动证据簇（附原话 + 链接）
4. 平台洞察与启发    ← 海外社区独有的判断点、与国内的差异
5. 风险、噪音与缺口  ← 哪些平台没数据/被降级/被关键词陷阱污染
6. 需要用户确认/补充  ← 待补 Key、待补平台、待人工判断项
```

> 多平台数据统一进 `03-normalized/overseas/`（last30days 已做跨源合并）。若某一海外平台需要单独深挖，可拆出 `03-normalized/overseas/<platform>/`，规则与国内平台一致。

---

## 5. 证据分级映射

last30days 的来源映射到本包 A/B/C 分级：

| 本包等级 | 海外来源 | 可支撑 |
|---------|---------|--------|
| **A 级** | 官网/官方公告/官方定价页、官方 GitHub release、实测截图 | 核心事实与关键判断 |
| **B 级** | Reddit 高赞帖/评论、X 专家帖、YouTube 字幕原话、HN 高分讨论、Polymarket 赔率 | 用户观点、口碑趋势、概率信号 |
| **C 级** | Web 聚合报道、二手转载、单条低互动帖 | 仅辅助，不单独撑核心结论 |

规则不变：关键事实用 A 级；用户观点至少 B 级；C 级不得单独支撑核心结论。引用社区原话时必须带可点击链接（last30days 每条证据都带 URL）。

---

## 6. 降级策略

last30days 不可用时（未安装 / Python < 3.12 / 缺必需 Key / 引擎报错），**必须明确降级，不允许静默跳过海外通道**：

| 不可用情形 | 降级路径 |
|-----------|---------|
| 引擎未安装 | 提示 `/调研安装` 或 `npx skills add mvanhorn/last30days-skill -g`；用户拒装则降级 |
| Python < 3.12 | 引擎不可用，降级为 MCP 子代理 |
| 缺平台 Key（X/TikTok 等） | 仅跑免费平台（Reddit/HN/Polymarket/GitHub/YouTube），缺的平台标注盲区 |
| 引擎报错/超时 | 降级为 MCP 子代理逐平台抓 |

降级方案：用 `user-firecrawl` / `user-exa` MCP + `WebSearch` 对 Reddit / X / YouTube / HN 做关键词检索补抓，结果同样归一到 `03-normalized/overseas/`，并在 `summary.md` 第 5 章写明：缺了哪些平台、为什么、影响哪条判断。

降级表达模板：

```text
"本轮海外通道未启用 last30days 引擎，原因是缺少 SCRAPECREATORS_API_KEY，
TikTok/Instagram 数据缺失，海外大众文化信号主要基于 Reddit + YouTube 推断。"
```

---

## 7. 采集门禁（海外）

| 任务类型 | 海外样本默认阈值 | 降级条件 |
|---------|----------------|---------|
| 海外单产品 / 方向调研 | 跨平台合计 ≥ 150 条有效证据 | 用户明确接受 |
| 市场全景（含海外） | 每海外平台 ≥ 50 条 | 用户明确接受 |
| 用户研究（海外） | 跨平台合计 ≥ 200 条（含评论层） | 不可降级 |

低于阈值 → 回问用户是否补抓 / 降标准，不允许默认放行。

---

## 8. 明确禁止

| 编号 | 禁止行为 | 原因 |
|------|----------|------|
| O-01 | last30days 不可用却静默跳过海外通道 | 必须显式降级并写明盲区 |
| O-02 | 把 Web 聚合报道（C 级）当成"海外用户都这么想" | C 级不能过度推广 |
| O-03 | 引用海外社区原话却不带链接 | last30days 每条都有 URL，必须可追溯 |
| O-04 | 把多个海外平台混写却不区分平台与互动量 | 标准件需保留平台与互动信号 |
| O-05 | 命中关键词陷阱（人名数字/泛词）直接硬跑引擎 | 先做 Pre-Flight 重构查询 |
