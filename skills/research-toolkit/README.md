# Research Toolkit (RTK)

统一调研分析工具包，自带工具链、质量门禁、逐章写作。由 SPCA（单产品竞品分析）和 LRS（本地调研系统）合并而来。

## 适用场景

| 场景 | 说明 | 任务类型 |
|------|------|----------|
| 单产品深度分析 | 竞品分析、市场进入评估 | `single-product` |
| 方向/赛道调研 | 新产品启动前验证 | `direction` |
| 市场全景对比 | 多产品横向对比 | `market-landscape` |
| 用户研究 | 痛点挖掘、画像构建 | `user-research` |
| 自定义调研 | 灵活章节结构 | `custom` |

## 快速开始

```bash
# 首次安装（自动准备 Python、venv、ffmpeg、依赖）
bash scripts/bootstrap.sh --with-stack --doctor

# 环境检查
python scripts/run_pipeline.py doctor --json

# 开始调研（在 Cursor 中）
# 输入：/深度调研 Kimi学习版
```

首次安装会自动完成：Homebrew Python 准备、受管 venv 创建、`requirements.txt` 依赖安装、ffmpeg 安装、MCP 状态检测。

## 命令速查

| 命令 | 说明 |
|------|------|
| `/深度调研 [产品名]` | 全流程调研编排（澄清→采集→体验→写作→核查） |
| `/竞品分析 [产品名]` | 单产品竞品分析全流程 |
| `/爬取 [平台] [主题]` | 轻量社媒采集任务 |
| `/竞品引导 [产品名]` | 真实产品体验引导与截图沉淀 |
| `/方向调研 [主题]` | 新方向/赛道可行性验证 |
| `/市场对比 [产品列表]` | 多产品横向对比矩阵 |
| `/用户研究 [主题]` | 用户痛点挖掘与画像构建 |

## 工具链

### 深度研究

- **DeerFlow**：深度研究引擎，支持论文检索、行业报告、市场分析，输出结构化 Markdown

### 社媒采集

- **MediaCrawler**：小红书/抖音/微博/B站关键词搜索与评论采集（支持帖子层+评论层）
- **XHS-Downloader**：小红书图文/视频下载器，按链接批量抓取

### MCP 集成

| MCP 服务 | 用途 |
|----------|------|
| cursor-ide-browser | 官网截图、DOM 分析、产品体验 |
| firecrawl | 网页结构化抓取 |
| app-insight | App Store / Google Play 数据 |
| xiaohongshu | 小红书 API 采集 |
| weibo | 微博数据采集 |
| bilibili | B站数据采集 |

## 目录结构

```
research-toolkit/
├── SKILL.md                    # 核心 Skill 定义
├── README.md                   # 本文件
├── task-card.template.json     # 任务卡模板
├── task-types/                 # 5 种任务类型定义
│   ├── single-product.md
│   ├── direction-research.md
│   ├── market-landscape.md
│   ├── user-research.md
│   └── custom.md
├── protocols/                  # 流程协议（13 份）
│   ├── review-gate.md          # 审核门禁
│   ├── fact-check.md           # 三轮事实核查
│   ├── writing-collaboration.md
│   ├── crawl-playbook.md
│   └── ...
├── scripts/                    # CLI + 工具链
│   ├── bootstrap.sh            # 跨平台首启
│   ├── run_pipeline.py         # 统一 CLI 入口
│   ├── build-release.sh        # 打包分发
│   └── rtk/                    # Python 模块
│       ├── cli.py              # 命令解析与分发
│       ├── doctor.py           # 环境诊断
│       ├── collectors/         # 数据采集器
│       ├── analyzers/          # 分析器
│       └── bridges/            # DeerFlow/MediaCrawler 桥接
├── schemas/                    # JSON Schema 校验
├── assets/                     # 模板与视觉规范
├── references/                 # 参考文档与协议说明
├── examples/                   # 基准案例库
│   └── doubao-aixue-benchmark/ # 真实高标准成稿案例
└── fixtures/                   # 离线测试数据
```

## CLI 命令详情

通过 `python scripts/run_pipeline.py <command>` 调用：

| 命令 | 说明 |
|------|------|
| `init` | 根据 task-card 初始化任务工作区（目录、模板、配置） |
| `collect` | 运行子代理采集，归档到 imports/ |
| `analyze` | 归一化证据源，运行竞争/用户/SEO/商业化分析器 |
| `export` | 导出报告（需通过审核门禁） |
| `validate` | Schema 与产物完整性校验 |
| `doctor` | 环境 + MCP + 工具链健康检查 |
| `install-stack` | 安装 DeerFlow / MediaCrawler / XHS-Downloader |
| `bootstrap-release` | 宿主运行时引导 + 可选工具链安装 |
| `run-deerflow` | 通过 DeerFlow 桥接执行深度研究 |
| `run-social` | 通过 MediaCrawler/XHS 执行社媒采集 |
| `run-social-auth` | MediaCrawler 扫码登录授权 |
| `run-research` | 端到端调研编排（doctor→采集→分析→报告） |
| `package-smoke` | 包文件完整性校验 |
| `build-release` | 构建可分发的 zip 包 |

所有命令均支持 `--json` 输出和 `--dry-run` 预览。

## 质量保障

### 两道门禁

1. **采集门禁**：搜索子代理完成后，独立审核代理检查样本量、平台覆盖、产物完整性。未放行不得进入写作。最多 5 轮打回。
2. **成稿门禁**：正文与图证完成后，检查章节配图、事实校验、证据链。未放行不得作为最终成品。

### 三轮事实核查

| 轮次 | 核查重点 |
|------|----------|
| Round 1 | 事实与来源核对：链接、标题、时间、平台名称 |
| Round 2 | 判断与证据核对：证据充分性、推断/事实区分 |
| Round 3 | 表述与配图核对：图注一致性、视觉证据完整性 |

每轮均由独立只读 `research-review` 子代理执行，不允许主代理代审。每轮结果单独落盘。

### 证据分级

- **强证据**：官方公开数据、截图、原文链接
- **中等证据**：多条用户评论交叉验证的共识
- **弱证据**：单条评论或推断，需降级写法标注

## 分发

```bash
# 构建可分发 zip（自动排除 .git、__pycache__、node_modules）
bash scripts/build-release.sh

# 或通过 CLI
python scripts/run_pipeline.py build-release --output-dir ./dist
```

打包产物包含：SKILL.md、README.md、所有协议/模板/脚本/schema/案例，接手人解压即可 `bootstrap.sh` 首启。

发布前建议先跑一次包完整性校验：

```bash
python scripts/run_pipeline.py package-smoke --json
```

## 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 13+ / Linux (Ubuntu 20+) |
| Python | 3.11+ |
| 必需 API Key | `ARK_API_KEY`（火山方舟，DeerFlow 深度研究） |
| 可选 API Key | `TAVILY_API_KEY`（Tavily 搜索增强） |
| 可选工具 | ffmpeg（视频抽帧）、Homebrew（macOS 自动安装） |

MCP 服务缺失时系统会明确降级提示，不会静默伪造数据。

## 关键文档索引

推荐阅读顺序：

1. `SKILL.md` — 核心 Skill 定义与流程
2. `task-types/` — 各任务类型的章节结构与执行要求
3. `protocols/review-gate.md` — 审核门禁协议
4. `protocols/writing-collaboration.md` — 逐章共写协议
5. `protocols/fact-check.md` — 三轮事实核查协议
6. `examples/doubao-aixue-benchmark/` — 真实高标准成稿案例
