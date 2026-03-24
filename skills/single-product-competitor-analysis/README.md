# 竞品分析共创 Skill

这个目录现在承载一个 `一目录、三指令` 的 skill：

- `/竞品分析`：全流程编排
- `/爬取`：采集与平台输出
- `/竞品引导`：真实体验引导与素材沉淀

它不是“自动分析器”，而是：

- 人负责目标、判断、洞察和拍板
- AI 负责提问、梳理、补盲区、共创正文和交付
- 工具负责建目录、采集归档、统计样本量、切视频帧、做校验

## 0. 从哪里开始

第一次真正运行这套 skill，优先从 `task-card.template.json` 开始，不要手写空白 `task-card.json`。

推荐顺序：

1. 复制 `task-card.template.json` 到你的工作目录，例如 `./spca-task-card.json`
2. 先改 `product_name`、`primary_url`、`analysis_goal`
3. 按需要再改 `platforms`
4. 明确保留或改写 `output_root`、`imports_root`、`manual_root`
5. 先运行 `bootstrap-macos.sh doctor` 做首启自检，再运行 `bootstrap-macos.sh init`

说明：

- 单独下载 skill 包时，优先使用 `task-card.template.json` 里的显式路径，不依赖仓库根目录推断
- `imports_root` 放平台原始资料
- `manual_root` 放人工补充截图、录屏、抽帧和笔记

首次启动与运行依赖：

- macOS 首入口统一走 `bootstrap-macos.sh`，不要再直接把 `run_pipeline.py` 当成用户入口
- `bootstrap-macos.sh` 会自动准备受管运行时：Homebrew Python、`~/.cursor/skills-runtime/single-product-competitor-analysis/venv`、`requirements.txt` 里的 Python 依赖、以及 `ffmpeg`
- `doctor` 入口：`bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" doctor`
- `repair` 入口：`bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" repair`
- 如果你是把 skill 解压到别的目录，下面命令里的 `.cursor/skills/single-product-competitor-analysis/` 只是“仓库内安装路径示意”，请替换成你的实际 skill 路径
- MCP 和登录态不会被静默伪造。脚本会检测并提示 `已安装 / 需安装 / 需登录初始化 / 当前降级模式`
- 详细首启协议见 `references/first-run-bootstrap.md`

## 1. 用户怎么唤起

### `/竞品分析`

```markdown
/竞品分析 Duolingo
分析目标：判断它为什么留存高，以及哪些做法值得 iXue 借鉴。
重点关注：用户、社媒、SEO、商业化。
```

### `/爬取`

```markdown
/爬取 小红书 Duolingo
目标：先把家长和学生视角的真实讨论抓回来。
```

也可以不写平台：

```markdown
/爬取 Duolingo
重点抓社媒和应用商店评价。
```

### `/竞品引导`

```markdown
/竞品引导 Duolingo
重点引导我体验核心学习路径和会员触发节点。
```

## 2. 默认行为

### `/竞品分析`

- 澄清需求
- 建任务文件夹
- 规划关键词
- 并发采集
- 核对结果
- 引导真实体验
- 查漏补缺
- 写作规划
- 逐章共写
- 事实核查
- SVG 补图

默认规则：

- 默认完整章节顺序推进，不问“先看哪个模块”
- 默认纳入 App 深度体验
- 默认按最高标准交付
- 只追问真正影响这轮判断的重点
- 默认每次新建独立任务，不复用之前同产品任务
- 只有用户明确说“继续/参考/挂到某任务”时，才允许接旧任务
- 全流程主报告必须写在当前任务目录内，默认是 `06-writing/<task-slug>.md`

### `/爬取`

- 默认新建轻量采集任务
- 不默认挂到当前 `/竞品分析` 任务
- 只有用户明确说“挂到当前任务 / 继续某任务 / 参考某任务”时，才允许复用旧任务
- 搜索阶段必须先列子代理清单，再按批次并发
- 每个搜索子代理必须输出自己的 `summary.md + data.csv`
- AI 基于采回数据做平台总结，但 `summary.md` 必须聚焦平台分析，不写成采集汇报
- 但不直接把单平台内容写成全局正式结论
- 搜索结束后必须先过审核代理，不合格就打回，最多 5 轮
- `REVIEW_GATE` 没明确放行前，不允许导出正式报告

`summary.md` 推荐统一为 6 个章节：

1. 本轮任务概况
2. 样本与证据面
3. 关键事实信号
4. 平台洞察与启发
5. 风险、噪音与缺口
6. 需要用户确认 / 补充

补充规则：

- `summary.md` 的主体应该是 `功能认知 / 用户画像 / 用户反馈 / 行为路径 / 关键原话 / 关键链接`
- 工具调用、去噪轮次、安装过程只应作为简短样本说明，不应占据主体

### `/竞品引导`

- 默认新建轻量体验任务
- 不默认挂到当前 `/竞品分析` 任务
- 只有用户明确说“挂到当前任务 / 继续某任务 / 参考某任务”时，才允许复用旧任务
- AI 逐步引导体验、追问洞察、组织截图/录屏/切帧
- 体验结束后必须额外产出 `04-experience/EXPERIENCE_REPORT.md`
- 高标准流程请显式使用 `--every-n-frames 10` 抽取关键图
- 最终正文里的真实体验图，优先按 `30%` 宽度嵌入

## 3. 关键文档

推荐先按这条顺序读：

1. `SKILL.md`
2. `references/skill-package-structure.md`
3. `references/chapter-agent-pipeline.md`
4. `references/README.md`
5. `examples/README.md`

主规范：

- `SKILL.md`
- `phase-output-contract.md`
- `subagent-search-protocol.md`
- `review-gate-protocol.md`
- `tooling-and-installation-protocol.md`
- `task-folder-contract.md`
- `crawl-playbook.md`
- `platform-output-contract.md`
- `experience-asset-protocol.md`
- `writing-collaboration-protocol.md`
- `fact-check-protocol.md`
- `visualization-protocol.md`
- `evidence-guide.md`

示例与模板：

- `task-card.template.json`
- `examples.md`
- `template.md`
- `demo-document.md`
- `cursor-interaction-simulation.md`

如果要让执行者按表推进，优先看：

- `assets/writing-plan-table-template.md`
- `assets/chapter-ops-tables.md`

## 4. 任务目录

### 全流程任务

```text
docs/workspaces/research/_data/single-product/<product-slug>/<task-slug>/
```

主报告默认位置：

```text
docs/workspaces/research/_data/single-product/<product-slug>/<task-slug>/06-writing/<task-slug>.md
```

### 轻量采集任务

```text
docs/workspaces/research/_data/crawl-tasks/<task-slug>/
```

### 轻量体验任务

```text
docs/workspaces/research/_data/guide-tasks/<task-slug>/
```

## 5. 对外分发时的 Skill 子目录骨架

推荐把 skill 统一组织成以下 4 类目录：

```text
assets/
examples/
references/
scripts/
```

我对这套骨架的建议是：

- `assets/`：放可复用的版式、图注规范、视觉模板、少量共用素材
- `examples/`：放示例文档和案例库，下载后即可直接查看 benchmark
- `references/`：放协议、合同、检查清单、目录规范
- `scripts/`：只放自动化脚本和运行时能力

补充说明：

- 这 4 个目录适合作为大多数 skill 的标准骨架
- 不必为了整齐强行给每个 skill 填满 4 个目录
- code-heavy 的 skill 可以继续额外保留 `tests/`、`schemas/`、`fixtures/`
- 当前 `single-product-competitor-analysis` 会以这套骨架为对外分发基准

## 6. 基准案例库

当前 skill 会内置一个可直接查看的 benchmark：

- `examples/doubao-aixue-benchmark/`

这份案例库不是抽象模板，而是当前高标准成稿的真实案例，默认包含：

- 主报告
- 写作计划
- 体验报告
- 审核门禁
- 可视化计划
- 关键平台总结
- 正文实际引用到的代表性截图与图表

它的作用不是替代模板，而是给后续下载者一个“成品长什么样”的明确上限。

## 7. 辅助脚本

辅助脚本只做机械劳动，不做结论判断。

当前保留的核心能力：

- 初始化目录和模板
- 导入与归档材料
- 统计样本量和覆盖度
- 按平台生成 `summary.md + data.csv`
- 视频逐帧切图（标准命令显式使用 `--every-n-frames 10`）
- 结构校验
- 未过 `REVIEW_GATE` 时阻止导出正式报告
- 主报告强制落在当前任务目录，不允许回写共享稳定路径
- 体验报告与图表资源为正文提供直接输入

工具调用与安装逻辑：

- 先按本 skill 自带的 `tooling-and-installation-protocol.md` 执行
- 如果当前项目仓库额外维护了工具索引，可把它们当“项目级补充信息”再读取
- 单独下载 skill 包时，不要求先依赖仓库外的工具目录

示例：

```bash
cp ".cursor/skills/single-product-competitor-analysis/task-card.template.json" "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" doctor
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" init --task-card "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" collect --task-card "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" analyze --task-card "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" export --task-card "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" validate --task-card "./spca-task-card.json"
bash ".cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" extract-frames --input demo.mp4 --output-dir path/to/frames --every-n-frames 10
```

## 8. 样本量规则

- 每个平台默认目标：至少 `200` 条/篇有效样本
- 低于阈值时，AI 必须回到对话里确认下一步
- 不能把低样本量直接包装成高置信结论

## 9. 写作规则

- 写作必须逐章推进，不允许先一次性导出整稿
- `WRITING_PLAN.md` 必须同时承担章节合同角色，写清每章的判断、证据、表格、配图和完成标准
- 每章完成后都要单独走一次 `配图 -> 章节事实校验`
- 默认顺序：`分析建模 -> 产品分析 -> 用户分析 -> 社媒分析 -> SEO 与内容分析 -> 商业化分析 -> 竞争判断 -> 对我方建议 -> 总结`
- 每章都要有 `本节主证据`，并用 `[1](相对路径)` 这类可点击索引回指到来源文档
- 产品、用户、商业化、竞争四章都要检查是否应下沉真实产品图；每章至少有一张表

## 10. 事实核查规则

- 三轮事实核查都必须调用独立只读 `research-review` 子代理
- 不允许主代理手动降级代审
- 如果子代理不可用，必须停下来向用户说明
- 章节级事实校验不能省略，终稿还要再过一次成稿级视觉与图证审核

## 11. fixture

离线 smoke test 仍使用：

```text
fixtures/demo-product/
```
