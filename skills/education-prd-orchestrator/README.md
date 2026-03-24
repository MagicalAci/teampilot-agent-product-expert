# 产品策划主 Skill

这个目录承载一个 `一目录、两指令` 的产品策划 skill：

- `/产品策划`：启动或继续一次产品文档工作
- `/产品策划校验`：校验已有 PRD / 产品文档并指出缺口或直接修正

它不是“自动写文档工具”，而是：

- 人负责目标、判断、拍板和关键取舍
- AI 负责编排证据、冻结定义、组织章节、补图和交付
- 脚本负责统计、索引、导出和校验这类机械劳动

它的目标形态不是“只能在当前仓库里用”，而是：

- 可以作为个人 zip skill 解压到 `~/.cursor/skills/education-prd-orchestrator/`
- 默认在独立交付目录里产出文档、图片、HTML、图表和证据
- 如果宿主工作区本来就有更强的项目文档结构，再做兼容写回

## 1. Skill 标题

- 对外标题：`产品策划主 Skill`
- 展示标题：`产品策划`
- 内部目录名：`education-prd-orchestrator`

## 2. Skill 描述

证据驱动的产品策划主 Skill。通过 `/产品策划` 与 `/产品策划校验` 两条指令，编排证据收集、产品定义闸门、章节 agent、配图 agent、用户检查点、版本同步与文档校验，用于章节化 PRD、产品文档、双端产品定义、V1 范围、核心功能、总览流程图和功能架构图。

## 3. 外部安装与首启自测

### 安装位置

把整个目录解压到：

```text
~/.cursor/skills/education-prd-orchestrator/
```

### 首次自测

至少跑这两条：

```bash
python scripts/run_pipeline.py bootstrap-tools
python scripts/run_pipeline.py package-smoke --json
```

如果是 macOS 且本机还没有 `python3`，先跑：

```bash
bash scripts/bootstrap-macos.sh doctor
```

### 自测通过信号

- `package-smoke` 返回 `contract_ok: true`
- `asset_validator_exit_code: 0`
- `strict_errors: []`

## 4. 用户怎么唤起

### `/产品策划`

```markdown
/产品策划 和韩雪聊聊教育
目标：整理成完整 PRD，并补总览流程图和功能架构图。
```

### `/产品策划校验`

```markdown
/产品策划校验 和韩雪聊聊教育
检查当前 PRD 是否缺总领层、图文口径是否一致、版本与交付说明是否同步。
```

## 4.1 首次运行先做环境自检

如果要调用本目录里的本地脚本，先跑一次 bootstrap：

```bash
python scripts/bootstrap_product_planning_tools.py doctor
```

在 macOS 上，如果本机连 `python3` 都没有，可以直接用：

```bash
bash scripts/bootstrap-macos.sh doctor
```

它会尽量自动补齐运行时、创建 skill 自己的 `.venv`，并安装 `requirements.txt` 里的依赖。

## 5. 默认行为

### `/产品策划`

- 冻结任务卡
- 建证据包
- 过定义闸门
- 路由章节 agent
- 进入配图
- 同步版本并校验

### `/产品策划校验`

- 读取现有文档和相关资产
- 检查定义、结构、证据、图文关系
- 输出缺口、风险和修正建议
- 如果用户明确要求，可直接修正文档

## 6. 默认交付路径

### 独立分发默认路径

默认把产出写到一个独立交付根目录：

```text
outputs/<slug>/
├── prd.md
├── images/
├── html/
├── charts/
├── evidence/
└── review/
```

### 仓库内兼容路径

如果当前工作区本来就有产品文档库，例如 `docs/workspaces/product/`，可以额外兼容写回：

- `docs/workspaces/product/prd/<slug>.md`
- `docs/workspaces/product/prd/images/<slug>/`
- `docs/workspaces/product/INDEX.md`

但这不是 skill 的唯一默认前提，不能要求使用者必须处在这套仓库里。

## 7. 对外分发目录

```text
education-prd-orchestrator/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── assets/
│   ├── README.md
│   ├── chart-template.html
│   ├── evidence-log-template.csv
│   ├── html-page-template.html
│   ├── prd-template.md
│   ├── index-log-template.md
│   ├── search-plan-template.md
│   ├── user-checkpoint-template.md
│   └── diagram-brief-template.md
├── examples/
│   ├── README.md
│   ├── example-invoke.md
│   ├── example-validation-command.md
│   ├── example-user-checkpoint.md
│   ├── example-chapter-output.md
│   ├── example-diagram-brief.md
│   ├── portable-benchmark/
│   │   └── README.md
│   └── hanxue-liaoliao-benchmark/
│       └── README.md
├── fixtures/
│   └── demo-product/
│       └── ...
├── references/
│   ├── README.md
│   ├── sop.md
│   ├── orchestration-rules.md
│   ├── prompt-rules.md
│   ├── user-checkpoints.md
│   ├── folder-structure.md
│   ├── agent-map.md
│   ├── review-criteria.md
│   ├── evidence-rules.md
│   ├── html-design-rules.md
│   ├── visualization-protocol.md
│   ├── package-scope.md
│   └── developer-handoff.md
├── scripts/
    ├── README.md
    ├── analyze_chat_csv.py
    ├── analyze_kb_xlsx.py
    ├── build_screenshot_index.py
    ├── bootstrap_product_planning_tools.py
    ├── bootstrap-macos.sh
    ├── doctor-macos.sh
    ├── export_svg_to_png.py
    ├── init_product_planning_delivery.py
    ├── run_pipeline.py
    ├── validate_prd_assets.py
    └── eppo/
        ├── __init__.py
        ├── cli.py
        └── runtime.py
└── tests/
│   ├── test_skill_contracts.py
│   ├── test_pipeline_smoke.py
│   └── test_asset_validators.py
```

## 8. 审核标准

详细版本见 `references/review-criteria.md`。这里的“审核”指审核别人使用这个 skill 后提交的最终产出文档，而不是审核 skill 包本身。至少看：

- [ ] 文档回答的产品决策问题明确，开头就知道这份稿子在回答什么
- [ ] 产品定义、范围取舍、模块关系和双端关系没有打架
- [ ] 关键结论有真实证据支撑，不是把猜测写成事实
- [ ] 总览流程图、功能架构图、表格等结构化表达已经补齐
- [ ] 图文关系成立，配图能支撑正文而不是独立摆图
- [ ] 功能描述、依赖和验收方式足以支撑后续设计/开发/评审继续往下走
- [ ] 版本、索引、图片路径和归档动作完整，提交后 reviewer 能顺利接手

## 9. Benchmark

当前内置的基准案例：

- `examples/hanxue-liaoliao-benchmark/`

它当前是一个“项目内参考 benchmark”，主要用来说明“高标准成品长什么样”。
对外独立分发时，它不应被当作唯一可运行样本，当前已经由 `portable-benchmark` + `fixtures/demo-product` 补齐自包含基线。

同时现在已经补上：

- `examples/portable-benchmark/`
- `fixtures/demo-product/`

前者给人看，后者给 smoke test 和 validator 跑。
