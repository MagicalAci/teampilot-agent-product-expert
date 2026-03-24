---
name: single-product-competitor-analysis
display_name: "单产品竞品分析共创"
description: "面向单一产品竞品研究的人机共创 Skill，覆盖澄清、采集、体验引导、逐章共写与事实校验交付。"
category: research
version: "1.0.0"
review_criteria:
  - label: "入口指令覆盖：可按 /竞品分析、/爬取、/竞品引导 三条指令触发对应流程。"
  - label: "启动合规性：首启必须通过 bootstrap-macos.sh doctor，且无阻断错误后才允许 init。"
  - label: "任务隔离：未获用户明确授权时，不复用旧任务日志、决策和报告。"
  - label: "关键词完整性：采集前至少给出并核对核心词、别名词、功能词、长尾词、评价词、问题词、竞品词。"
  - label: "平台产物规范：每个平台都产出 summary.md 与 data.csv 两类标准文件。"
  - label: "样本量门槛：每个平台有效样本默认不少于 200，低于门槛必须回问是否补抓。"
  - label: "审核闸门：搜索阶段需通过独立审核代理复核，未放行不得进入正式写作。"
  - label: "章节流程完整：每章必须执行 章节合同→章节撰写→配图→章节事实校验。"
  - label: "事实核查闭环：全稿需完成三轮独立事实核查，并落地轮次记录文件。"
  - label: "证据可追溯：关键判断需附可点击证据索引，图注与正文结论保持一致。"
---

# 竞品分析共创 Skill

这个 skill 的目标不是“自动写完报告”，而是把工作分成三层：

- 人：给目标、做判断、给洞察、拍板决策
- AI：提问、梳理、补盲区、组织证据、共创正文、保证交付
- 工具：建目录、采集归档、转结构化数据、统计样本量、切视频帧、做校验

## 首次启动（macOS）

这个 skill 的外部入口已经改成 `bootstrap-macos.sh`，不要再默认让用户手动准备 Python、`pip install` 或系统 `ffmpeg`。

首启顺序：

1. 先运行 `bash "~/.cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" doctor`
2. 如果 doctor 没报阻断错误，再运行 `bash "~/.cursor/skills/single-product-competitor-analysis/scripts/bootstrap-macos.sh" init --task-card "..."`
3. 后续 `collect / analyze / export / validate / extract-frames` 都继续走同一个 bootstrap 入口

首启默认会做的事：

- 自动准备 Homebrew Python 与受管 venv
- 自动安装 `requirements.txt` 里的 Python 依赖
- 自动准备 `ffmpeg`
- 输出 MCP 检查结果：`已安装 / 需安装 / 需登录初始化 / 当前降级模式`

边界：

- 账号登录、扫码、Cookie 初始化不会被静默伪造
- MCP 缺失时必须明确告知降级，而不是假装采到了数据
- 详细协议见 `references/first-run-bootstrap.md`

## 何时使用

优先用于这些场景：

- `/竞品分析 [产品名]`
- `/爬取 [主题或平台]`
- `/竞品引导 [产品名]`
- “帮我做单个产品的竞品分析”
- “帮我抓某个平台的资料并整理出来”
- “带我一步步体验这个产品并沉淀截图/录屏/洞察”

不要用于：

- 行业全景扫描
- 多产品横向矩阵为主
- 只要功能清单，不要分析和决策建议

## 三条指令

### 1. `/竞品分析 [产品名]`

启动全流程。

它负责：

1. 澄清任务卡
2. 创建任务文件夹
3. 规划关键词和长尾词
4. 组织并发采集
5. 核对采集结果
6. 引导真实体验
7. 查漏补缺
8. 规划写作并逐章共写
9. 三轮事实核查
10. SVG 可视化补图

默认行为：

- 每次都新建一个独立任务目录和独立报告文件
- 不默认复用上一次同产品任务
- 只有用户明确说“继续某任务 / 参考某任务 / 挂到某任务”时，才允许接旧任务

### 2. `/爬取 [主题或平台]`

启动采集流程。

默认行为：

- 一律新建一个轻量采集任务
- 不默认挂到当前 `/竞品分析` 任务
- 只有用户明确说“挂到当前任务 / 继续当前任务 / 参考某任务”时，才允许复用旧任务

它负责：

- 澄清要抓什么、为什么抓
- 定义搜索词和长尾词
- 调用现有 MCP / 搜索 / 浏览器 / 可选本地 crawler 能力
- 让每个搜索子代理按平台各自落 `summary.md + data.csv`
- 由 AI 做“平台总结 + 缺口说明 + 下一步建议”

### 3. `/竞品引导 [产品名]`

启动真实体验引导。

默认行为：

- 一律新建一个轻量体验任务
- 不默认挂到当前 `/竞品分析` 任务
- 只有用户明确说“挂到当前任务 / 继续当前任务 / 参考某任务”时，才允许复用旧任务

它负责：

- 告诉用户先体验什么
- 每一步解释为什么重要
- 指导截图、录屏、补素材
- 追问人的感受、判断和反直觉洞察
- 对录屏做逐帧切图并存档

## 总规则

### 1. 先澄清，再执行

收到任何一条指令，都不要直接执行。

但 `/竞品分析` 的首轮澄清要尽量少问废话，优先采用这些默认值：

- 默认按完整章节顺序推进，不问“先看哪个模块”
- 默认纳入 App 深度体验，不单独追问
- 默认按最高标准交付，不问“这份文档给谁看”

首轮真正需要确认的只剩：

- 对象是谁
- 这次要解决什么问题
- 这轮重点看什么
- 是否有特殊限制、禁区或必须补看的角度

`当前我方产品是什么` 不再作为启动前必问项。
如果后续需要写“对我方建议”且上下文里仍然没有，再在写作前补问。

### 任务隔离默认开启

除非用户明确要求“继续旧任务 / 引用旧任务 / 对照旧任务”，否则：

- 不读取之前同产品任务的 `PROCESS_LOG.md`
- 不沿用之前任务的 `KEY_DECISIONS.md`
- 不覆盖之前任务目录
- 不把之前的主报告当作当前任务输入
- 当前任务只写入当前任务目录和当前任务报告文件

### 2. 每轮关键讨论都要沉淀

每次人与 AI 的关键讨论，都要沉淀到：

- `01-process/PROCESS_LOG.md`
- `01-process/KEY_DECISIONS.md`

注意：这件事应由 AI 在每轮对话后做归纳，不是靠脚本自动编造内容。

### 3. 关键词一定先核对

在搜索或爬取前，AI 必须先给出并和用户核对：

- 核心词
- 别名词
- 功能词
- 长尾词
- 评价词
- 问题词
- 竞品词

不能只搜产品名。

### 4. `/爬取` 的平台产物必须标准化

每个搜索子代理都要按平台输出：

- `03-platforms/<platform>/summary.md`
- `03-platforms/<platform>/data.csv`

默认平台目录为：

- `web`
- `appstore`
- `xiaohongshu`
- `weibo`
- `bilibili`
- `zhihu`
- `seo`
- `pricing`

搜索阶段必须遵循 [subagent-search-protocol.md](subagent-search-protocol.md)：

- 先列子代理清单
- 明确每个子代理负责什么
- 按批次并发执行
- 不能由单一代理包揽全部搜索
- 每个平台的工具调用、安装、初始化和降级顺序见 [tooling-and-installation-protocol.md](tooling-and-installation-protocol.md)

`summary.md` 的边界：

- 可以写基于本平台证据提炼出的平台洞察、候选判断、策划启发
- 可以写“这对后续章节有什么帮助”
- 不要把单平台总结直接写成全局正式结论
- 不要直接产出最终版 `跟 / 避 / 绕 / 观察`
- 不要让主体变成工具调用、去噪轮次、安装过程等采集过程汇报

`summary.md` 推荐固定为 6 章：

1. 本轮任务概况
2. 样本与证据面
3. 关键事实信号
4. 平台洞察与启发
5. 风险、噪音与缺口
6. 需要用户确认 / 补充

`summary.md` 应优先覆盖：

- 平台上的功能认知
- 用户画像与行为路径
- 高频正向 / 负向反馈
- 关键原话、关键帖子、关键链接

其中“需要用户确认 / 补充”不是礼貌性提问，而是用来：

- 补证据缺口
- 纠正误读
- 决定是否接受当前样本量
- 请求私有或登录后材料
- 决定下一轮采集优先级

### 5. 样本量不足要回问用户

默认每个平台至少 `200` 条/篇有效样本。

如果低于阈值，AI 必须回到对话里确认：

- 是否接受当前样本量
- 是否继续扩大关键词范围
- 是否增加平台

### 6. 搜完后必须核对，再进入体验

AI 不能“默默采完就继续写”。

子代理搜索阶段结束后，必须先走 [review-gate-protocol.md](review-gate-protocol.md)：

- 用独立审核代理检查
- 不合格就打回指定子代理
- 最多 5 轮
- 没过审核不能进入正式报告
- 脚本层也必须拦截：`REVIEW_GATE` 未放行时，禁止导出正式报告

必须先和用户核对：

- 哪些平台结果可信
- 哪些地方噪音大
- 还要不要补抓

核对后，再进入 `/竞品引导` 或全流程中的体验阶段。

### 7. 写作前先做分析建模

正文不能一口气自动生成。

必须先共创：

1. 分析建模
2. 产品分析
3. 用户分析
4. 社媒分析
5. SEO 与内容分析
6. 商业化分析
7. 竞争判断
8. 对我方建议
9. 总结
10. 证据附录

逐章共写时必须遵守：

- 每章都先列 `本节主证据`
- 关键地方用 `[1](相对路径)` 形式做可点击索引
- 每章至少有一张表
- `WRITING_PLAN.md` 不是普通进度表，而是 10 章的章节合同总表
- 每一章都必须按这条生产线推进：`章节合同 -> 章节撰写 -> 配图 -> 章节事实校验`
- `总结` 只能在所有章节通过后回写；`证据附录` 只能最后统一汇编
- 凡本章存在可用真实产品截图、录屏抽帧、价格页、认证页、权益页、搜索页时，优先在该章内下沉分析，不要只丢到附录
- 产品、用户、商业化、竞争这几章默认都要检查是否需要图
- 图注、表格判断和正文强判断都应带证据索引或明确章节回指
- 正式正文里不出现采集过程、写作过程、AI 思维过程

### 8. 章节配图与事实核查

章节完成后，不是直接进入下一章，而是要再走两步：

1. 先让配图代理决定本章是否需要真实截图、路径图板、角色图板、节点图板或结构图
2. 再让章节事实校验代理检查 `图文对应 / 中文图注 / 本地素材路径 / 证据角标 / 判断降级`

整篇正文完成后：

1. 先三轮事实核查
2. 再补整篇范围内仍缺的关键结构图
3. 最后再跑一次成稿级审核，确认图证覆盖和章节一致性

事实核查的硬规则：

- 章节事实校验不能省略，至少要把结果回填到 `WRITING_PLAN.md` 与 `FACTCHECK_PLAN.md`
- 三轮都必须调用独立只读 `research-review` 子代理
- 不允许主代理手动降级代审
- 每轮都要写 `07-factcheck/round-*.md`
- 主报告必须位于当前任务目录内，不能回写共享稳定路径

## `/竞品分析` 执行顺序

1. 需求唤起与澄清
2. 用户确认后创建任务文件夹
3. 关键词与长尾词核对
4. 并发平台采集
5. 核对采集结果
6. 引导真实体验
7. 查漏补缺
8. 规划写作
9. 逐章共写（每章都走 `合同 -> 撰写 -> 配图 -> 章节事实校验`）
10. 三轮事实核查
11. 全文范围的结构图与补图收尾
12. 成稿终审

## `/爬取` 执行顺序

1. 默认新建轻量采集任务；只有用户明确要求时才挂到旧任务
2. 列搜索子代理清单
3. 确认平台、关键词、样本量目标
4. 让平台子代理按批次并发采集
5. 落标准产物 `summary.md + data.csv`
6. 交给审核代理复核
7. 如果样本量不足或证据池缺失，回问用户
8. 复核通过后，才能进入下一阶段

## `/竞品引导` 执行顺序

1. 默认新建轻量体验任务；只有用户明确要求时才挂到旧任务
2. 明确体验目标和重点路径
3. 一步步指导用户体验
4. 记录截图、录屏和洞察
5. 对视频优先显式使用 `--every-n-frames 10` 切图
6. 输出 `04-experience/EXPERIENCE_REPORT.md`
7. 归纳体验后的补充问题和新洞察

## 工具边界

工具层只做这些事：

- 创建任务目录和空模板
- 导入与归档资料
- 生成 `csv/json/jsonl`
- 统计样本量与覆盖度
- 抽取视频关键帧
- 验证结构与索引完整性

工具层不要做这些事：

- 自动判断“用户是谁”
- 自动判断“这个产品为什么成功”
- 自动给“跟 / 避 / 绕 / 观察”
- 自动写总结和正文结论

这些内容应该由 AI 基于技能文档、资料和用户洞察来共创完成。

## 最终报告结构

```markdown
# 【产品名】竞品分析文档

## 1. 总结
## 2. 分析建模
## 3. 产品分析
## 4. 用户分析
## 5. 社媒分析
## 6. SEO 与内容分析
## 7. 商业化分析
## 8. 竞争判断
## 9. 对我方建议
## 10. 证据附录
```

## 参考文件

- [task-card.template.json](task-card.template.json)
- [references/skill-package-structure.md](references/skill-package-structure.md)
- [references/first-run-bootstrap.md](references/first-run-bootstrap.md)
- [references/chapter-agent-pipeline.md](references/chapter-agent-pipeline.md)
- [references/README.md](references/README.md)
- [assets/writing-plan-table-template.md](assets/writing-plan-table-template.md)
- [assets/chapter-ops-tables.md](assets/chapter-ops-tables.md)
- [examples/README.md](examples/README.md)
- [assets/README.md](assets/README.md)
- [README.md](README.md)
- [examples.md](examples.md)
- [phase-output-contract.md](phase-output-contract.md)
- [subagent-search-protocol.md](subagent-search-protocol.md)
- [tooling-and-installation-protocol.md](tooling-and-installation-protocol.md)
- [review-gate-protocol.md](review-gate-protocol.md)
- [task-folder-contract.md](task-folder-contract.md)
- [crawl-playbook.md](crawl-playbook.md)
- [platform-output-contract.md](platform-output-contract.md)
- [experience-asset-protocol.md](experience-asset-protocol.md)
- [writing-collaboration-protocol.md](writing-collaboration-protocol.md)
- [fact-check-protocol.md](fact-check-protocol.md)
- [visualization-protocol.md](visualization-protocol.md)
- [evidence-guide.md](evidence-guide.md)

## Skill 对外分发结构

对外分发时，推荐把 skill 组织成以下骨架：

```text
single-product-competitor-analysis/
├── SKILL.md
├── README.md
├── assets/       # 可复用版式、图注规范、视觉资产
├── examples/     # 示例文档与基准案例库
├── references/   # 协议、合同、检查清单
├── scripts/      # 自动化脚本
└── ...           # code-heavy skill 可额外保留 tests / schemas / fixtures
```

说明：

- `assets / examples / references / scripts` 是推荐的对外分发骨架
- 不要求每个 skill 都填满四个目录，但命名和职责应尽量统一
- 这个 skill 现在内置了 `豆包爱学` 基准案例库，供下载后直接查看高标准成稿样例