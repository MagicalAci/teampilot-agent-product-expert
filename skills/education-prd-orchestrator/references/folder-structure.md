# 文件夹结构

## Skill 包结构

这个 skill 统一使用这套骨架：

```text
education-prd-orchestrator/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── assets/
│   ├── README.md
│   ├── prd-template.md
│   ├── user-persona-template.md
│   ├── user-story-template.md
│   ├── user-journey-template.md
│   ├── hypothesis-template.md
│   ├── feature-priority-template.md
│   └── ...
├── examples/
│   ├── README.md
│   └── ...
├── fixtures/
│   └── demo-product/
│       └── ...
├── references/
│   ├── README.md
│   ├── methodology/
│   │   ├── user-persona.md
│   │   ├── user-story.md
│   │   ├── user-journey.md
│   │   ├── pain-point-abstraction.md
│   │   ├── solution-ideation.md
│   │   ├── hypothesis-validation.md
│   │   └── feature-prioritization.md
│   └── ...
├── scripts/
│   ├── README.md
│   ├── run_pipeline.py
│   └── ...
└── tests/
    └── ...
```

## 四个标准目录职责

### `assets/`

放模板资产和可复用骨架：

- PRD 模板（通用 7 章结构）
- 用户画像模板
- 用户故事模板
- 用户旅程模板
- 核心假设模板
- 功能优先级模板
- INDEX 日志模板
- 用户检查点模板
- 配图 brief 模板

### `examples/`

放如何触发 skill、如何回问用户、章节产物长什么样。

也承载 benchmark 案例。

### `references/`

放流程规则、agent 说明、文件结构、prompt 规范。

`references/methodology/` 子目录放产品方法论知识库。

也承载对最终提交文档的审核标准。

### `scripts/`

放统计、导出、索引、校验脚本。

### `fixtures/`

放给 smoke test 和 validator 使用的最小可运行样本。

### `tests/`

放技能包的契约测试、smoke tests 和 validator 测试。

## 实际产出路径

### 独立分发默认路径

默认产出写到一个便于打包和交付的独立目录：

```text
outputs/<slug>/
├── prd.md
├── user-persona.md
├── user-stories.md
├── user-journey.md
├── hypothesis.md
├── feature-priority.md
├── images/
│   ├── *.svg
│   └── *.png
├── html/
│   └── *.html
├── charts/
│   ├── *.html
│   ├── *.svg
│   └── *.png
├── evidence/
│   ├── evidence-log.csv
│   ├── screenshot-index.md
│   └── imports/
└── review/
    ├── review-summary.md
    └── handoff.md
```

### 仓库内兼容写回

如果宿主工作区本来就有产品文档库，可以额外镜像写回：

```text
docs/workspaces/product/
├── INDEX.md
└── prd/
    ├── <slug>.md
    └── images/
        └── <slug>/
            ├── *.svg
            └── *.png
```

但这只是可选兼容路径，不是独立 skill 的默认前提。

## 可选辅助产物

按需创建：

```text
outputs/<slug>/review/
├── implementation-plan.md
└── validation-report.md
```

## 输入材料来源

输入材料不要求放进 skill 目录。

常见来源：

- 用户提供的截图目录
- 会议纪要
- CSV / XLSX
- 现有 PRD 或既有方案文档
- 知识库文档
- 用户访谈记录

这些属于任务输入，不属于 skill 资产。
