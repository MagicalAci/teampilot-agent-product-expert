# AI策划 Skill

这个 Skill 用来让同学快速开展 AI 策划，而不是每次重新摸索流程。

目标是让执行者在 Cursor 里高质量完成：

- AI PRD
- AI脚本
- AI测试报告
- 开发 README / 调用文档
- 如有需要，再补开发脚本压缩包

## 适用场景

- 从 0 开始一轮 AI 策划
- 单独撰写 AI PRD
- 单独开发 AI 脚本
- 单独测试 AI 脚本并输出测试报告
- 补齐脚本交接给开发的最小材料

## 四条指令

### `/AI策划`

示例：

```markdown
/AI策划 课堂讲题 Agent
目标：从 0 开始完成 AI PRD、AI脚本、AI测试，并在需要时补开发脚本压缩包。
要求：
1. 严格按官方模板章节顺序写
2. 先锁输入结构，再写策略，再写 Prompt，再落脚本与测试
3. 文档、代码、样例、README、压缩包同口径
```

### `/AIPRD`

示例：

```markdown
/AIPRD 课堂讲题 Agent
目标：只撰写 AI PRD。
要求：
1. 严格按模板递进
2. 明确输入结构、AI策略、提示词模块、AI脚本章节
3. 字段、Prompt、示例三者同口径
```

### `/AI脚本`

示例：

```markdown
/AI脚本 课堂讲题 Agent
目标：只开发 AI 脚本、最小接入材料和开发调用文档。
要求：
1. 先读取已冻结的 AI PRD 或字段合同
2. 补齐核心脚本、样例、README、调用文档
3. 不在字段未冻结时直接写代码
```

### `/AI测试`

示例：

```markdown
/AI测试 课堂讲题 Agent
目标：测试 AI 脚本，并输出正式测试报告。
要求：
1. 覆盖单测、真实调用、结构化输出兼容性验证
2. 输出结论、风险、限制
3. 不只贴日志，要给测试报告
```

## 核心原则

- 先判断这轮是全流程、PRD、脚本还是测试
- 先读模板，再写 PRD
- 先锁字段，再写 Prompt
- 先冻结合同，再开发脚本
- 先跑验证，再写测试报告
- 先写开发调用文档，再说"可交接"
- 先确认最小接入范围，再打包

## 目录结构

```text
ai-planning-orchestrator/
├── SKILL.md                          ← Skill 主定义（Cursor 入口）
├── README.md                         ← 本文件
├── assets/
│   ├── README.md                     ← 模板索引
│   ├── ai-prd-template.md            ← AI PRD 模板
│   ├── test-record-template.md       ← AI 测试报告模板
│   ├── developer-readme-template.md  ← 开发 README / 调用文档模板
│   └── script-bundle-manifest-template.md ← 脚本包清单模板
├── examples/
│   ├── README.md                     ← 示例索引
│   ├── example-invoke.md             ← 四条指令调用示例
│   ├── example-script-command.md     ← /AI脚本 使用示例
│   ├── example-test-command.md       ← /AI测试 使用示例
│   └── example-validation-command.md ← 内置脚本使用示例
├── references/
│   ├── README.md                     ← 参考文档索引
│   ├── hellobike-platform-api.md     ← 幻视平台 API + 模型选型 + 缓存
│   ├── execution-sop.md              ← 执行 SOP
│   ├── developer-handoff.md          ← 开发交接说明
│   ├── review-checklist.md           ← 评审清单
│   └── package-scope.md              ← 脚本包范围定义
└── scripts/
    ├── README.md                     ← 脚本索引
    ├── init_ai_planning_delivery.py  ← 初始化 PRD / 报告 / README
    ├── validate_ai_planning_assets.py← 校验文档章节 + 文件齐全
    ├── package_ai_script_bundle.py   ← 打 zip 交付包
    └── export_svg_to_png.js          ← SVG 导出 PNG
```

## 推荐阅读顺序

1. `SKILL.md`
2. `references/execution-sop.md`
3. `references/hellobike-platform-api.md`
4. `assets/ai-prd-template.md`
5. `references/review-checklist.md`
6. `references/developer-handoff.md`
7. `references/package-scope.md`

## 内置模型选型

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 简单文案 / 分类 / 提取 / 高并发 | `Doubao-Seed-2.0-Mini-0215` | 成本最低，响应最快 |
| 内容创作 / 数据分析 / 结构化输出 | `Doubao-Seed-2.0-Lite-0215` | 均衡型，质量稳定 |
| 复杂推理 / Agent / 多模态 / 长链路 | `Doubao-Seed-2.0-Pro-0215` | 旗舰全能 |

详细 API 端点、鉴权、缓存、超时配置见 `references/hellobike-platform-api.md`。

## 命令矩阵

| 命令 | 解决什么问题 | 默认产物 |
|---|---|---|
| `/AI策划` | 全流程开始 | AI PRD + AI脚本 + AI测试报告 + 可选脚本包 |
| `/AIPRD` | 只做文档策划 | AI PRD |
| `/AI脚本` | 只做脚本开发 | AI 脚本 + 样例 + README / 调用文档 |
| `/AI测试` | 只做脚本测试 | AI测试报告 |

## 交付标准

- AI PRD 必须按固定章节递进
- AI脚本必须建立在已冻结的字段 / Prompt 合同之上
- 开发调用文档必须至少写清 CLI / HTTP 两种接入方式中的适用方式
- AI测试报告必须区分单测、真实调用、兼容性验证
- 如需打包，压缩包必须对齐开发最小接入范围

## 脚本支持

- `scripts/init_ai_planning_delivery.py`：初始化 PRD / 测试报告 / 开发 README / 清单
- `scripts/validate_ai_planning_assets.py`：校验关键文档和文件是否齐全
- `scripts/package_ai_script_bundle.py`：按指定文件列表打 zip
- `scripts/export_svg_to_png.js`：导出 SVG 流程图为 PNG
