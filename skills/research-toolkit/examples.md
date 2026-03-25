# 使用示例

如果你是第一次下载这个 skill，建议先看：

1. `examples/README.md`
2. `examples/doubao-aixue-benchmark/README.md`
3. 再回来看这份 `examples.md`

说明：

- `examples.md` 负责放“怎么唤起 skill、期望行为是什么”
- `examples/` 目录负责放“高标准成品案例长什么样”

## 启动前一步

第一次跑脚本时，优先先复制模板：

```bash
cp ".cursor/skills/research-toolkit/task-card.template.json" "./spca-task-card.json"
```

然后至少修改：

- `product_name`
- `primary_url`
- `analysis_goal`
- 需要的话再改 `platforms`

如果是单独下载 skill 包场景，建议保留 `output_root / imports_root / manual_root` 的显式路径。

首次启动前，先跑一次 bootstrap doctor：

```bash
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" doctor
```

如果需要强制重装受管运行时：

```bash
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" repair
```

## 指令 1：`/竞品分析`

```markdown
/竞品分析 Duolingo
分析目标：判断它为什么留存高，以及哪些做法值得 iXue 借鉴。
重点关注：用户、社媒、SEO、商业化。
```

期望行为：

- AI 先澄清目的、重点和限制
- AI 不直接搜索，先核关键词
- AI 在每轮关键讨论后沉淀过程文档和关键决策
- AI 默认创建新的独立任务目录，而不是沿用旧任务
- AI 的主报告默认写到当前任务目录 `06-writing/<task-slug>.md`

## 示例 1：信息不足时先补需求

输入：

```markdown
/竞品分析 Kimi 学习版
```

期望行为：

- AI 不问“先看哪个模块”“是否要 App 深度体验”“文档给谁看”
- AI 直接按默认规则：完整顺序推进、默认深度体验、默认最高标准
- AI 只追问分析目的、这轮重点看什么、有没有特殊限制
- 用户确认后才真正启动

## 示例 2：关键词先核对

输入：

```markdown
/竞品分析 Duolingo
分析目标：看它为什么增长快。
```

期望行为：

- AI 先给核心词、别名词、功能词、长尾词、评价词、问题词、竞品词
- 用户补自己的搜索思路和洞察

## 指令 2：`/爬取`

### 示例 3：默认新建轻量采集任务

输入：

```markdown
/爬取 小红书 Duolingo
目标：先抓学生和家长视角的真实讨论。
```

期望行为：

- AI 默认新建轻量采集任务
- AI 先列出搜索子代理清单，而不是自己单线去搜
- AI 明确搜索词和样本量目标
- 小红书子代理单独落 `03-platforms/xiaohongshu/summary.md` 和 `03-platforms/xiaohongshu/data.csv`
- AI 基于采回数据做平台总结和缺口说明
- 搜索结束后先过审核代理，不合格就打回对应子代理

### 示例 4：独立启动轻量采集任务

输入：

```markdown
/爬取 AI 记账 App
重点抓应用商店评论和微博反馈。
```

期望行为：

- 无论当前是否已有别的任务，AI 默认新建轻量采集任务
- AI 先确认平台、目标和阈值
- 如果某个平台样本量低于 `200`，AI 回来问用户是否继续

## 指令 3：`/竞品引导`

### 示例 5：挂到当前任务里引导真实体验

输入：

```markdown
/竞品引导 Duolingo
重点引导我体验核心学习路径和会员触发节点。
```

期望行为：

- 只有用户明确说“挂到当前任务”时，AI 才允许接当前任务
- AI 告诉用户先体验什么、为什么重要、每一步看什么
- AI 引导用户录屏、截图、说出自己的感受和洞察
- 对视频做逐帧切图并存档

### 示例 6：独立启动体验任务

输入：

```markdown
/竞品引导 某 AI 记账 App
我想单独体验它的会员转化路径。
```

期望行为：

- 无论当前是否已有别的任务，AI 默认新建轻量体验任务
- AI 先规划体验顺序
- 体验后追问“哪里顺、哪里卡、哪里反直觉、哪里值得学”

## 示例 7：进入写作规划

输入：

```markdown
/竞品分析写作规划
资料和体验都差不多了，开始规划写作。
```

期望行为：

- AI 先共创“分析建模”
- 再逐章进入：产品分析、用户分析、社媒分析、SEO 与内容分析、商业化分析、竞争判断、对我方建议

## 示例 8：事实核查与可视化

输入：

```markdown
/竞品分析校验
把事实核查和可视化补图也一起安排。
```

期望行为：

- 先跑三轮事实核查
- 三轮都必须走独立只读 `research-review` 子代理
- 再决定哪些位置需要简单关键的 SVG 图
- 图只做结构化辅助，不打断正文

## 示例 9：搜索门禁

输入：

```markdown
/爬取 豆包爱学
重点抓官方结构、评论、社媒和 SEO。
```

期望行为：

- AI 明确列出哪个子代理调研哪部分
- AI 进一步拆到平台级子代理，如 `appstore/xiaohongshu/weibo/bilibili/zhihu/seo`
- 单批最多 4 个子代理并发
- 子代理结束后先走审核代理
- 审核不通过就打回，最多 5 轮

## 开发辅助脚本

```bash
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" init --task-card "./spca-task-card.json"
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" collect --task-card "./spca-task-card.json"
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" analyze --task-card "./spca-task-card.json"
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" export --task-card "./spca-task-card.json"
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" validate --task-card "./spca-task-card.json"
bash ".cursor/skills/research-toolkit/scripts/bootstrap-macos.sh" extract-frames --input demo.mp4 --output-dir path/to/frames --every-n-frames 10
```
