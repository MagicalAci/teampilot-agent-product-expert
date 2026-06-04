---
name: research-toolkit
description: 统一调研分析工具包 — 支持单产品深度分析、方向调研、市场全景、用户研究等多种任务类型，含国内/海外双采集通道
version: 1.0.0
commands:
  - /深度调研
  - /海外调研
  - /爬取
  - /体验引导
  - /调研安装
  - /调研体检
  - /调研授权
  - /调研打包
triggers:
  - 竞品分析
  - 产品调研
  - 市场调研
  - 用户研究
  - 方向调研
  - 赛道分析
  - 深度调研
  - 海外调研
  - 出海调研
  - 海外舆情
review_criteria:
  - label: "入口指令覆盖：可按 /深度调研、/爬取、/体验引导、/调研安装、/调研体检、/调研授权、/调研打包 七条指令触发对应流程。"
  - label: "启动合规性：首启必须通过 bootstrap.sh --doctor，且无阻断错误后才允许进入采集。"
  - label: "任务隔离：未获用户明确授权时，不复用旧任务日志、决策和报告。"
  - label: "关键词完整性：采集前至少覆盖核心词、别名词、功能词、长尾词、评价词、问题词、竞品词。"
  - label: "平台产物规范：每个平台产出 summary.md 与 data.csv 两类标准文件。"
  - label: "海外通道合规：命中海外/出海场景时启用 last30days 海外采集通道，引擎不可用必须显式降级并写明盲区，不静默跳过。"
  - label: "采集门禁：每平台有效样本默认 ≥ 200，低于门槛必须回问用户是否补抓。"
  - label: "成稿门禁：REVIEW_GATE 放行 + 三轮事实核查 + 体验报告 + 写作计划全部完成后才能导出。"
  - label: "章节流水线：每章必须执行 章节合同→章节撰写→配图→章节事实校验。"
  - label: "事实核查闭环：全稿需完成三轮独立事实核查，落地轮次记录文件。"
  - label: "证据可追溯：关键判断附可点击证据索引，图注与正文结论一致。"
---

# Research Toolkit (RTK) — 统一调研分析工具包

RTK 是自带工具链安装、质量门禁、逐章写作流水线和社媒深度采集的一站式调研 Skill。它合并了 SPCA（单产品竞品分析）的成熟写作体系和 LRS（本地调研系统）的工具链能力，支持从单品深拆到赛道全景的 5 种任务类型。

三层分工不变：

- **人**：给目标、做判断、给洞察、拍板决策
- **AI**：提问、梳理、补盲区、组织证据、共创正文、保证交付
- **工具**：DeerFlow 深度研究、MediaCrawler/XHS-Downloader 国内社媒采集、last30days 海外社媒采集、脚本归档统计

两条采集通道并行：

- **国内通道**：小红书 / 微博 / B站 / 知乎 + App Store + 官网，一平台一子代理
- **海外通道**：Reddit / X / YouTube / Hacker News / TikTok / Polymarket 等，由 last30days 单引擎多平台覆盖（协议见 `protocols/overseas-research.md`，连接器见 `references/last30days-connector.md`）

---

## 1. 任务类型矩阵

| 类型 | 适用场景 | 章节数 | 社媒目标/平台 | 核查轮次 | 主交付物 | 详细定义 |
|------|----------|--------|--------------|----------|----------|----------|
| **单产品深度** | 对某一竞品做全方位拆解 | 10 章 | ≥ 200 条/平台 | 3 轮 | 深度分析报告 | `task-types/single-product.md` |
| **方向调研** | 新方向启动前的可行性判断 | 8 章 | ≥ 200 条/平台 | 3 轮 | 方向调研报告 + 竞品追踪表 | `task-types/direction-research.md` |
| **市场全景** | 多产品（≥ 3）横向对比 | 6 章 | ≥ 100 条/平台/产品 | 2 轮 | 对比矩阵报告 | `task-types/market-landscape.md` |
| **用户研究** | 聚焦用户痛点和需求 | 7 章 | ≥ 300 条/平台（三层证据） | 3 轮 | 用户洞察报告 | `task-types/user-research.md` |
| **自定义** | 用户自带分析框架 | 用户定义 | 用户指定（默认 200） | 2-3 轮 | 用户定义 | `task-types/custom.md` |

AI 在 Phase 0 自动识别任务类型，用户确认后锁定。锁定后章节结构、采集标准、门禁规则从对应类型文件加载。

---

## 2. 命令系统

### 斜杠命令

| 命令 | 作用 | 执行入口 |
|------|------|----------|
| `/深度调研 [产品/方向]` | 主入口。AI 自动识别任务类型，走完整 Phase 0-7 流程 | 全流程 SOP |
| `/海外调研 [主题]` | 海外通道快捷入口。对 Reddit/X/YouTube/HN/TikTok/Polymarket 等海外平台采集 + 归一 + 洞察 | Phase 2 海外通道（last30days） |
| `/爬取 [平台] [关键词]` | 调用 MediaCrawler/XHS-Downloader 做关键词搜索采集 | Phase 2 子流程 |
| `/体验引导` | 引导用户完成 App/Web 实测体验，录入截图/录屏/洞察 | Phase 4 子流程 |
| `/调研安装` | 安装 DeerFlow + MediaCrawler + XHS-Downloader 全套工具链 | `bash scripts/bootstrap.sh --with-stack --doctor` |
| `/调研体检` | 环境 + MCP + API Key + 工具链全面检查 | `bash scripts/bootstrap.sh --doctor` |
| `/调研授权` | 小红书 QR 授权流程 | `python scripts/run_pipeline.py run-social-auth --platform xhs --open-qr --json` |
| `/调研打包` | 构建可分发的 Skill 压缩包（排除 outputs/dist/__pycache__） | `python scripts/run_pipeline.py build-release --json` |

### 自然语言触发

以下表达会自动路由到 RTK：

```
"帮我调研下 XXX"        → /深度调研 XXX
"看看 XXX 怎么样"        → /深度调研 XXX（单产品深度）
"XXX 这个方向值得做吗"   → /深度调研 XXX（方向调研）
"对比一下 A、B、C"       → /深度调研 A B C（市场全景）
"XXX 的用户到底要什么"   → /深度调研 XXX（用户研究）
"海外怎么看 XXX"         → /海外调研 XXX（海外通道）
"Reddit/X/YouTube 上 XXX 口碑" → /海外调研 XXX
"XXX 出海/海外竞品舆情"  → /海外调研 XXX
"抓一下小红书上关于 XXX" → /爬取 xhs XXX
"带我体验下 XXX"         → /体验引导
```

---

## 3. 执行 SOP — `/深度调研` 全流程

```text
Phase 0  需求澄清          ← 1 轮对话，锁定任务类型和目标
Phase 1  环境检查            ← doctor，不就绪则引导安装
Phase 2  数据采集            ← DeerFlow + MCP 子 Agent + MediaCrawler
Phase 3  证据规范化 & 分析   ← 证据分级 + 缺口分析 + 六维分析
Phase 4  体验报告            ← 引导用户实测（单产品/方向调研必需）
Phase 5  逐章写作            ← 章节合同 → 撰写 → 配图 → 章节校验
Phase 6  三轮事实核查        ← round-1 → round-2 → round-3
Phase 7  成稿门禁 & 导出     ← REVIEW_GATE 放行 → 导出正式报告
```

### Phase 0 — 需求澄清（1 轮对话）

AI 做四件事：

1. **识别任务类型**：根据用户描述判断属于 5 种类型中的哪一种，向用户确认
2. **确认调研目标**：锁定产品名/方向名、核心链接、分析目标、重点看什么、禁区限制
3. **提炼搜索关键词**：覆盖核心词、别名词、功能词、长尾词、评价词、问题词、竞品词（7 类）
4. **生成 task-card.json**：参照 `task-card.template.json` 和 `schemas/task-card.schema.json`

默认值（不必追问）：

- 默认完整章节顺序推进
- 默认纳入 App 深度体验
- 默认按最高标准交付
- "当前我方产品是什么"可延后到写"对我方建议"前再补问

用户确认后：

- 落盘 `00-admin/TASK_CARD.md`
- 落盘 `01-plan/PROCESS_LOG.md` + `KEY_DECISIONS.md`
- 落盘 `02-imports/SEARCH_KEYWORDS.md` + `SEARCH_KEYWORDS.csv`
- 进入 Phase 1

### Phase 1 — 环境检查 & 工具链就绪

```bash
bash scripts/bootstrap.sh --doctor
```

检查三层就绪状态：

| 层级 | 含义 | 检查项 |
|------|------|--------|
| `basic_ready` | 基础可用 | Python 3、venv、API Key（ARK/TAVILY）、MCP 连接 |
| `deep_ready` | 深度研究可用 | DeerFlow 路径存在 + 模型连通 |
| `social_ready` | 社媒采集可用 | MediaCrawler 路径 + 登录态（`.auth.ready`） |

不就绪 → 按缺失项引导安装（`/调研安装`）或授权（`/调研授权`）。
DeerFlow/MediaCrawler 缺失时明确降级，不静默跳过。

### Phase 2 — 数据采集

四条并行采集通道：

**① DeerFlow 深度研究**（方向调研/单产品均用）

```bash
python scripts/run_pipeline.py run-research \
  --topic "[调研主题]" \
  --keywords "[关键词列表]" \
  --slug "[task-slug]" --json
```

产出市场格局、融资数据、行业报告等结构化数据。DeerFlow 不可用时降级为 WebSearch + WebFetch 手动补充。

**② MCP 子 Agent 并行采集**

按 `protocols/subagent-search.md` 组织：

- 先列子代理清单（`05-synthesis/SUBAGENT_ROSTER.md`）
- 每个子代理负责一个平台
- 单批最多 4 个并行
- 每个子代理输出标准产物：`03-normalized/<platform>/summary.md` + `data.csv`

默认国内平台：`web` / `appstore` / `xiaohongshu` / `weibo` / `bilibili` / `zhihu` / `seo` / `pricing`

默认海外平台（走通道 ⑤）：`reddit` / `x` / `youtube` / `hackernews` / `tiktok` / `polymarket`（按需扩 `instagram` / `threads` / `bluesky`）

**③ MediaCrawler 主动采集**（`social_ready` 时）

```bash
python scripts/run_pipeline.py run-social \
  --platform xhs \
  --keywords "关键词1,关键词2" --json
```

小红书必须分别采集帖子层和评论层。XHS-Downloader 用于单链接补抓。

**④ 用户手动补充**

截图、录屏、访谈记录等 → 存入 `02-imports/`

**⑤ 海外采集通道**（`last30days`，海外/出海场景）

```bash
# 由 reasoning model 生成查询计划后调用海外引擎，详见 references/last30days-connector.md
python3 [last30days.py] "[海外主题]" --plan "[查询计划]" --emit=md \
  --save-dir "[task-root]/02-imports/last30days"
```

一个引擎覆盖 Reddit / X / YouTube / Hacker News / TikTok / Polymarket / Instagram / Threads / Bluesky / Web，按真实互动量打分并跨源合并。产出归一到 `03-normalized/overseas/`（协议见 `protocols/overseas-research.md`）。引擎不可用时降级为 firecrawl/exa + WebSearch 逐平台补抓，不静默跳过。

**采集审核门禁**（硬门禁）：

- 采集完成后交给独立 `research-review` 子代理审核
- 不合格定向打回指定子代理
- 最多 5 轮
- 未放行 → 不能进入写作
- 产出 `05-synthesis/REVIEW_GATE.md`

| 平台 | 默认阈值 | 降级条件 |
|------|----------|----------|
| 单产品/方向调研 | ≥ 200 条/平台 | 用户明确接受 |
| 市场全景 | ≥ 100 条/平台/产品 | 用户明确接受 |
| 用户研究 | ≥ 300 条/平台 | 不可降级 |

### Phase 3 — 证据规范化 & 分析

**① 证据分级**

| 等级 | 定义 | 示例 |
|------|------|------|
| **A 级** | 官方页面、定价页、帮助中心、实测截图、录屏 | 官网首页截图、价格表 |
| **B 级** | 应用商店评论、社媒帖子/评论、论坛讨论、媒体访谈 | 小红书测评帖、知乎回答 |
| **C 级** | 聚合文章、二手转载、非官方总结、AI 生成推断 | 行业白皮书中的间接引用 |

规则：关键事实用 A 级，用户观点至少 B 级，C 级不得单独支撑核心结论。

**② 缺口分析**

AI 逐平台检查覆盖度，列出哪些维度缺数据、为什么缺、影响哪条判断。

**③ 六维分析建模**

根据任务类型对齐分析维度：产品 / 用户 / 社媒 / SEO / 商业化 / 竞争。

### Phase 4 — 体验报告（单产品/方向调研必需）

引导用户做 App/Web 实测：

1. AI 生成体验脚本 `04-experience/EXPERIENCE_SCRIPT.md`
2. 一步步指导用户体验关键路径（注册→核心功能→付费节点）
3. 每步解释为什么重要，指导截图/录屏
4. 追问用户感受、判断和反直觉洞察
5. 录屏自动抽帧：`python scripts/extract_video_frames.py --every-n-frames 10`
6. 产出 `04-experience/EXPERIENCE_REPORT.md`

体验报告须说明哪些素材将进入哪些章节，待补素材标注阻塞哪一章。

市场全景类型 → 抽样体验（核心流程即可），用户研究类型 → 可跳过。

### Phase 5 — 逐章写作

加载任务类型对应的章节结构（见 `task-types/*.md`），生成 `06-writing/WRITING_PLAN.md`。

**每章走固定四步流水线（不可缩减）**：

```
步骤 1  章节合同    回填 WRITING_PLAN.md — 判断边界、证据清单、必备表格、配图需求、阻塞项
步骤 2  章节撰写    正文 + 表格 + 证据角标 [n](路径) + 图位需求
步骤 3  配图        优先真实截图/录屏抽帧 → 再补结构图；图注必须中文且说明判断点
步骤 4  章节事实校验  检查强判断降级、证据角标、图文对应、路径有效、留白
```

写作规则：

- 总结最后回写，证据附录最后统一汇编
- 真实截图存在时必须下沉到对应章节，不能只丢附录
- 产品、用户、商业化、竞争章节默认检查是否需要图
- 正文不出现采集过程、写作过程、AI 思维过程
- `WRITING_PLAN.md` 按 `assets/writing-plan-table-template.md` 格式生成

### Phase 6 — 三轮事实核查

三轮都必须调用独立只读 `research-review` 子代理，不允许主代理手动降级代审。

| 轮次 | 聚焦点 | 产出文件 |
|------|--------|----------|
| Round 1 | 章节级：强判断、证据角标、图文对应 | `07-factcheck/round-1.md` |
| Round 2 | 全稿级：章节间一致性、总结与正文回指 | `07-factcheck/round-2.md` |
| Round 3 | 交叉验证：图证覆盖、中文图注、路径有效、评论层证据可追溯 | `07-factcheck/round-3.md` |

每轮结果回填 `07-factcheck/FACTCHECK_PLAN.md`。
用户研究类型第 2 轮替换为"痛点交叉验证专项"。
市场全景类型降级为 2 轮（章节级 + 全稿级）。

### Phase 7 — 成稿门禁 & 导出

成稿门禁必须同时满足（协议详见 `protocols/review-gate.md`）：

- [ ] `WRITING_PLAN.md` 各章状态完整，每章走过四步流水线
- [ ] `07-factcheck/` 三轮核查完整（或用户明确降级为两轮）
- [ ] `04-experience/EXPERIENCE_REPORT.md` 存在（单产品/方向类型）
- [ ] `08-visuals/VISUAL_PLAN.md` 已回填
- [ ] 正文图证覆盖关键章节
- [ ] 主报告位于当前任务目录内 `06-writing/<task-slug>.md`

放行后执行导出：

```bash
python scripts/run_pipeline.py export-report --slug <task-slug> --json
```

未放行 → 定向打回（写明打回哪章、缺什么、是撰写/配图/校验问题）。

---

## 4. 质量门禁体系

两道硬门禁，跳过任何一道均为违规：

### 4.1 采集门禁（Phase 2 结束时）

| 检查项 | 标准 | 不达标处理 |
|--------|------|-----------|
| 子代理是否全部执行 | 每个指定平台都有子代理 | 打回缺失平台 |
| 标准产物是否存在 | 每平台 `summary.md` + `data.csv` | 打回指定子代理 |
| 样本量是否达标 | 按任务类型阈值 | 回问用户 → 补抓/降级 |
| 是否越级写成正式结论 | 子代理只写平台级洞察 | 打回重写 summary |
| 小红书是否有评论层 | 帖子层 + 评论层分开 | 补抓评论 |

审核循环最多 5 轮。第 5 轮仍不达标 → 停下向用户汇报，由用户决定降标准/改范围/终止。

### 4.2 成稿门禁（Phase 7）

| 检查项 | 标准 |
|--------|------|
| 章节流水线完整 | 每章都走过 合同→撰写→配图→校验 |
| 事实核查完整 | 三轮（或降级后两轮）核查文件存在 |
| 图证覆盖 | 产品/用户/商业化/竞争章节有真实产品图 |
| 图注规范 | 中文图注、说明判断点、本地素材路径 |
| 回指一致 | 总结⇔正文⇔附录之间判断一致 |
| 评论层可追溯 | 引用"评论区反馈"时能追到评论层数据 |
| 主报告路径 | 在当前任务目录内，未写回共享路径 |

---

## 5. 证据分级与降级表达

### 分级标准

| 等级 | 来源 | 可支撑 |
|------|------|--------|
| A | 官网、定价页、帮助中心、实测截图、录屏、官方公告 | 核心事实和关键判断 |
| B | App Store 评论、社媒帖子/评论、论坛讨论、媒体访谈 | 用户观点和口碑趋势 |
| C | 聚合文章、二手转载、非官方总结 | 仅辅助，不单独撑结论 |

### 降级表达规范

遇到证据不足时，必须按三步处理：

1. 写清"缺什么"
2. 写清"为什么缺"
3. 写清"影响哪条判断"

标准表达模板：

```
"当前无法确认该产品真实付费转化表现，原因是未拿到支付前页面和转化数据，
因此商业判断主要基于定价结构与用户反馈推断。"
```

强判断词自查清单（出现以下词时检查证据是否够强）：

- "不是……而是……" / "已经" / "本质上" / "主战场" / "战略性"
- 只有公开页面 + 评论 + 体验素材时 → 改用较低强度表述

---

## 6. 接手人引导协议

当新接手人首次使用 RTK 时，采用**傻瓜式三件套**引导策略：

**原则**：每次只给一步操作 + 一个明确的回复词 + 等用户回复后再给下一步。

### 首次启动引导流程

```
AI: 你好！我来帮你配置调研环境。
    请先回复"安装"两个字，我帮你自动准备环境。

→ 用户回复"安装"

AI: [执行 bash scripts/bootstrap.sh --with-stack --doctor]
    [检查输出，判断就绪状态]

    ✅ 基础环境已就绪。
    ⚠️ 缺少小红书登录态。
    请回复"授权"，我帮你打开扫码页面。

→ 用户回复"授权"

AI: [执行 run-social-auth --platform xhs --open-qr]
    二维码已弹出，请用小红书 App 扫码。
    扫完后回复"扫好了"。

→ 用户回复"扫好了"

AI: ✅ 全部就绪！
    现在你可以输入 /深度调研 [产品名] 开始调研。
```

### 缺 API Key 时的引导

```
AI: 环境检查发现缺少 TAVILY_API_KEY。
    请打开这个文件填入你的 Key：
    ~/.local/share/cursor-research/.env.research-toolkit
    填完后回复"配好了"。

→ 用户回复"配好了"

AI: [重新运行 doctor 验证]
    ✅ API Key 验证通过。
```

---

## 7. Skill 包目录结构

```text
research-toolkit/
├── SKILL.md                          # 本文件 — Skill 核心定义
├── README.md                         # 对外说明文档
├── task-card.template.json           # 任务卡模板
├── template.md                       # 报告大纲模板
├── demo-document.md                  # 演示文档
├── examples.md                       # 示例索引
│
├── task-types/                       # ═══ 任务类型定义 ═══
│   ├── single-product.md            # 单产品深度分析（10 章）
│   ├── direction-research.md        # 方向/赛道调研（8 章）
│   ├── market-landscape.md          # 市场全景对比（6 章）
│   ├── user-research.md             # 用户研究（7 章）
│   └── custom.md                    # 自定义调研
│
├── protocols/                        # ═══ 执行协议 ═══
│   ├── review-gate.md               # 采集门禁 + 成稿门禁协议
│   ├── subagent-search.md           # 子代理搜索并发协议
│   ├── platform-output-contract.md  # 平台标准产物规范
│   ├── phase-output-contract.md     # 阶段产出标准
│   ├── task-folder-contract.md      # 任务文件夹结构协议
│   ├── writing-collaboration.md     # 逐章共写协议
│   ├── fact-check.md                # 事实核查协议
│   ├── evidence-guide.md            # 证据映射与降级策略
│   ├── experience-asset.md          # 体验素材管理协议
│   ├── crawl-playbook.md            # 社媒爬取执行手册
│   ├── overseas-research.md         # 海外调研通道协议（last30days）
│   ├── visualization.md             # 可视化与配图协议
│   ├── tooling-and-installation.md  # 工具链安装与降级协议
│   ├── user-supplement-checklist.md # 用户补充素材检查清单
│   └── cursor-interaction-simulation.md # Cursor 交互模拟协议
│
├── references/                       # ═══ 参考文档 ═══
│   ├── install-and-auth.md          # 安装 + 授权完整指南
│   ├── quality-gates.md             # 质量门禁快速参考
│   ├── folder-structure.md          # 输出目录结构说明
│   ├── evidence-rules.md            # 证据规则详细版
│   ├── deerflow-runtime.md          # DeerFlow 运行时说明
│   ├── mediacrawler-connector.md    # MediaCrawler 连接器说明
│   ├── last30days-connector.md      # last30days 海外调研引擎连接器
│   ├── chapter-agent-pipeline.md    # 章节代理流水线说明
│   ├── first-run-bootstrap.md       # 首次启动详细协议
│   ├── skill-package-structure.md   # Skill 包分发结构
│   └── README.md                    # 参考文档索引
│
├── assets/                           # ═══ 模板与资产 ═══
│   ├── writing-plan-table-template.md   # WRITING_PLAN.md 表格模板
│   ├── chapter-ops-tables.md            # FACTCHECK_PLAN + VISUAL_PLAN 表格模板
│   ├── chapter-visual-blocks.md         # 章节配图规格
│   ├── report-outline-template.md       # 报告大纲模板
│   ├── evidence-index-template.csv      # 证据索引 CSV 模板
│   ├── doctor-report-template.md        # 体检报告模板
│   ├── project-manifest-template.json   # 项目清单模板
│   ├── default-config.toml              # 默认配置
│   ├── deerflow-config.template.yaml    # DeerFlow 配置模板
│   ├── deerflow.env.template            # DeerFlow 环境变量模板
│   └── README.md                        # 资产索引
│
├── scripts/                          # ═══ 自动化脚本 ═══
│   ├── bootstrap.sh                 # 首启安装 + 体检（入口脚本）
│   ├── build-release.sh             # 构建分发包
│   ├── run_pipeline.py              # Python 主编排器
│   ├── extract_video_frames.py      # 视频关键帧提取
│   └── rtk/                         # Python 工具链模块
│       ├── cli.py                   # CLI 入口
│       ├── config.py                # 配置加载
│       ├── doctor.py                # 环境诊断
│       ├── install.py               # 工具链安装
│       ├── runtime.py               # 运行时管理
│       ├── orchestrator.py          # 流程编排
│       ├── project_init.py          # 项目初始化
│       ├── release.py               # 打包发布
│       ├── utils.py                 # 通用工具
│       ├── bridges/                 # 外部工具桥接
│       │   ├── deerflow_bridge.py   # DeerFlow 桥接
│       │   ├── social_bridge.py     # MediaCrawler 桥接
│       │   └── mediacrawler_auth.py # 小红书授权
│       ├── collectors/              # 数据采集器
│       │   ├── web.py / social.py / reviews.py / seo.py / pricing.py / manual.py
│       │   └── common.py
│       ├── normalizers/             # 数据规范化
│       │   └── evidence.py
│       ├── analyzers/               # 分析器
│       │   ├── user.py / sentiment.py / seo.py / monetization.py / competition.py
│       │   └── __init__.py
│       ├── validators/              # 校验器
│       │   └── pipeline.py
│       └── exporters/               # 导出器
│           └── report.py
│
├── schemas/                          # ═══ JSON Schema ═══
│   ├── task-card.schema.json        # 任务卡校验
│   ├── review-sample.schema.json    # 审核样本校验
│   └── report-context.schema.json   # 报告上下文校验
│
├── fixtures/                         # ═══ 测试数据 ═══
│   └── demo-product/               # 演示用测试数据集
│
├── examples/                         # ═══ 基准案例库 ═══
│   ├── README.md                    # 案例索引
│   └── doubao-aixue-benchmark/      # 豆包爱学基准案例（高标准成稿样例）
│
└── agents/                           # ═══ Agent 配置 ═══
    └── openai.yaml                  # OpenAI Agent 配置
```

---

## 8. 协议文件索引

| 协议文件 | 职责 | 在哪个 Phase 使用 |
|----------|------|-------------------|
| `protocols/review-gate.md` | 采集门禁 + 成稿门禁的通过/打回规则、5 轮限制 | Phase 2、Phase 7 |
| `protocols/subagent-search.md` | 子代理清单、并发规则、单批上限、不能单代理包揽 | Phase 2 |
| `protocols/platform-output-contract.md` | `summary.md` 六章固定结构 + `data.csv` 字段规范 | Phase 2 |
| `protocols/phase-output-contract.md` | 每个 Phase 的必须产出、完成条件、用户确认点 | 全流程 |
| `protocols/task-folder-contract.md` | 任务目录 8 层结构、强制文档清单、隔离原则 | Phase 0 |
| `protocols/writing-collaboration.md` | 逐章四步流水线、章节依赖、WRITING_PLAN 格式 | Phase 5 |
| `protocols/fact-check.md` | 三轮核查流程、独立子代理要求、轮次记录格式 | Phase 6 |
| `protocols/evidence-guide.md` | 10 章的证据来源、必填字段、降级写法、反模式 | Phase 3、Phase 5 |
| `protocols/experience-asset.md` | 截图/录屏/抽帧的命名规范、存放路径、素材引用方式 | Phase 4 |
| `protocols/crawl-playbook.md` | MediaCrawler/XHS-Downloader 调用命令、关键词策略、数据清洗 | Phase 2 |
| `protocols/overseas-research.md` | 海外通道平台矩阵、last30days 调用、产物归一、证据分级映射、降级 | Phase 2 |
| `protocols/visualization.md` | 配图类型决策树、SVG 规格、中文图注规范 | Phase 5 |
| `protocols/tooling-and-installation.md` | DeerFlow/MediaCrawler/XHS 安装路径、降级策略、MCP 状态协议 | Phase 1 |
| `protocols/user-supplement-checklist.md` | 用户需手动补充的素材清单和引导话术 | Phase 4 |
| `protocols/cursor-interaction-simulation.md` | Cursor IDE 内的交互模拟与测试协议 | 开发/调试 |

---

## 9. 任务文件夹结构（8 层）

每个全流程任务生成以下目录结构（协议详见 `protocols/task-folder-contract.md`）：

```text
<task-root>/                          # docs/workspaces/research/_data/<type>/<product>/<task-slug>/
│
├── 00-admin/                         # 管理元数据
│   └── TASK_CARD.md                 # 任务卡（类型、目标、关键词、阈值）
│
├── 01-plan/                          # 过程沉淀
│   ├── PROCESS_LOG.md               # 每轮关键讨论归纳
│   └── KEY_DECISIONS.md             # 关键决策记录（选择 + 理由）
│
├── 02-imports/                       # 原始导入
│   ├── SEARCH_KEYWORDS.md           # 7 类关键词文档
│   ├── SEARCH_KEYWORDS.csv          # 关键词结构化表
│   ├── last30days/                  # 海外引擎原始产出（<slug>-raw.md）
│   └── [用户上传的截图/录屏/文档]
│
├── 03-normalized/                    # 平台标准产物
│   ├── web/                         # summary.md + data.csv
│   ├── appstore/
│   ├── xiaohongshu/
│   ├── weibo/
│   ├── bilibili/
│   ├── zhihu/
│   ├── seo/
│   ├── pricing/
│   └── overseas/                    # 海外通道归一产物（summary.md + data.csv）
│
├── 04-experience/                    # 体验素材
│   ├── EXPERIENCE_SCRIPT.md         # 体验脚本（AI 生成）
│   ├── EXPERIENCE_REPORT.md         # 体验报告（素材→章节映射）
│   ├── uploads/                     # 用户上传原始文件
│   ├── screenshots/                 # 截图
│   ├── frames/                      # 录屏抽帧
│   └── notes/                       # 用户洞察笔记
│
├── 05-synthesis/                     # 整合与审核
│   ├── SUBAGENT_ROSTER.md           # 子代理清单
│   └── REVIEW_GATE.md              # 采集审核结果
│
├── 06-writing/                       # 写作
│   ├── WRITING_PLAN.md              # 章节合同总表（进度追踪核心）
│   └── <task-slug>.md               # 主报告（唯一正式稿）
│
├── 07-factcheck/                     # 事实核查
│   ├── FACTCHECK_PLAN.md            # 核查计划
│   ├── round-1.md                   # 第 1 轮：章节级
│   ├── round-2.md                   # 第 2 轮：全稿级
│   ├── round-3.md                   # 第 3 轮：交叉验证
│   └── final-status.md             # 终审状态
│
└── 08-visuals/                       # 可视化
    ├── VISUAL_PLAN.md               # 配图计划
    ├── svg/                         # SVG 源文件
    └── png/                         # PNG 导出
```

轻量采集任务（`/爬取`）只需：`00-admin` + `01-plan` + `02-imports` + `03-normalized` + `05-synthesis`

轻量体验任务（`/体验引导`）只需：`00-admin` + `01-plan` + `04-experience`

---

## 10. 工具链速查

### 环境变量

写入 `~/.local/share/cursor-research/.env.research-toolkit`（本机私有，不进 git）：

| 变量 | 必须 | 用途 |
|------|------|------|
| `ARK_API_KEY` | 是 | 火山方舟 API（DeerFlow 默认模型） |
| `TAVILY_API_KEY` | 是 | 联网搜索 |
| `DEERFLOW_ROOT` | 否 | 自定义 DeerFlow 路径（默认 `~/.local/share/cursor-research/vendor/deer-flow`） |
| `MEDIACRAWLER_ROOT` | 否 | 自定义 MediaCrawler 路径（默认 `~/crawlers/MediaCrawler`） |
| `XHS_DOWNLOADER_ROOT` | 否 | 自定义 XHS-Downloader 路径（默认 `~/crawlers/XHS-Downloader`） |
| `MEDIACRAWLER_AUTH_READY` | 否 | 社媒登录态标记（或 `~/crawlers/MediaCrawler/.auth.ready`） |
| `OPENAI_API_KEY` | 否 | 可选备选模型 |
| `DEEPSEEK_API_KEY` | 否 | 可选备选模型 |
| `SERPAPI_API_KEY` | 否 | 可选搜索补充 |
| `SCRAPECREATORS_API_KEY` | 否 | 海外通道 TikTok/Instagram/Threads（last30days） |
| `BRAVE_API_KEY` | 否 | 海外通道 Web 搜索（last30days） |
| `LAST30DAYS_MEMORY_DIR` | 否 | 海外引擎研究文件保存目录（默认 `~/Documents/Last30Days/`） |

> 海外通道完整 Key 矩阵（X / YouTube / Bluesky / Perplexity 等）见 `references/last30days-connector.md`。Reddit / HN / Polymarket / GitHub 免费开箱即用。

### 常用命令

```bash
# 首启安装 + 体检
bash scripts/bootstrap.sh --with-stack --doctor

# 仅体检
bash scripts/bootstrap.sh --doctor

# 小红书 QR 授权
python scripts/run_pipeline.py run-social-auth --platform xhs --open-qr --json

# 社媒关键词采集
python scripts/run_pipeline.py run-social --platform xhs --keywords "关键词1,关键词2" --json

# 单链接补抓
python scripts/run_pipeline.py run-social --platform xhs --url "https://..." --json

# DeerFlow 深度研究
python scripts/run_pipeline.py run-research --topic "主题" --keywords "词1,词2" --slug demo --json

# 海外调研引擎安装（last30days，按需）
npx skills add mvanhorn/last30days-skill -g

# 海外调研采集（reasoning model 先生成查询计划再调引擎，详见连接器文档）
python3 [last30days.py] "海外主题" --plan "[查询计划]" --emit=md --save-dir "[task-root]/02-imports/last30days"

# 全流程（dry-run 验证）
python scripts/run_pipeline.py run-research --dry-run --json

# 视频抽帧
python scripts/extract_video_frames.py --input video.mp4 --every-n-frames 10

# 导出正式报告
python scripts/run_pipeline.py export-report --slug <task-slug> --json

# 构建分发包
python scripts/run_pipeline.py build-release --json
```

---

## 11. 明确禁止

| 编号 | 禁止行为 | 原因 |
|------|----------|------|
| F-01 | 没过采集审核就写正式报告 | 证据基础不牢 |
| F-02 | 样本量不足却默认放行 | 必须回问用户 |
| F-03 | 缺体验素材却写"深度体验结论" | 结论无支撑 |
| F-04 | 审核代理只给一句"通过/不通过" | 必须写明原因和处理方式 |
| F-05 | 主代理手动降级代替 research-review 子代理 | 必须独立审核 |
| F-06 | 跳过采集门禁直接进入成稿门禁 | 两道门禁串行执行 |
| F-07 | 单篇测评文章推出"用户都这么想" | B 级证据不能过度推广 |
| F-08 | 主报告写回共享路径而非任务目录 | 任务隔离原则 |
| F-09 | 复用旧任务的 PROCESS_LOG/KEY_DECISIONS（用户未授权） | 任务隔离原则 |
| F-10 | 正文中出现采集过程、工具调用、AI 思维过程 | 交付物不含实施细节 |
| F-11 | C 级证据单独支撑核心结论 | 必须有 A/B 级交叉 |
| F-12 | 小红书只有帖子层没有评论层却默认放行 | 必须分层采集 |
