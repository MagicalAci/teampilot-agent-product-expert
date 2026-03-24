# Skill 包结构建议

这份文档定义 `single-product-competitor-analysis` 对外分发时推荐采用的 skill 骨架。

## 推荐骨架

```text
single-product-competitor-analysis/
├── SKILL.md
├── README.md
├── assets/
├── examples/
├── references/
├── scripts/
├── tests/        # 可选
├── schemas/      # 可选
└── fixtures/     # 可选
```

## 四个标准目录各自做什么

### `assets/`

放可复用的表现层资产，而不是具体案例证据。

适合放：

- 图板版式模板
- 图注规范
- 通用视觉块
- 少量共用说明图

不适合放：

- 某个案例独有的截图
- 某次任务的录屏抽帧

### `examples/`

放示例和 benchmark 案例库。

适合放：

- 一份高标准成稿案例
- 示例任务目录
- 示例主报告
- 示例写作计划

### `references/`

放规则、协议、检查清单和结构说明。

适合放：

- Skill 包结构说明
- 章节流水线说明
- 协议索引
- 审核清单

### `scripts/`

放自动化脚本和运行时能力。

适合放：

- 目录初始化
- 数据整理
- 抽帧
- 校验
- `bootstrap-macos.sh` / `doctor-macos.sh`

补充约束：

- bootstrap 脚本应随 skill 一起分发
- 受管运行时不要直接塞进 zip
- 运行时状态默认落到 `~/.cursor/skills-runtime/single-product-competitor-analysis/`

## 统一命名建议

- 优先使用 `assets / examples / references / scripts`
- 不要混用 `example / demos / refs / helpers` 这类多套命名
- 目录越少越稳定，职责越清晰越好

## 是否所有 Skill 都必须长这样

不是。

建议如下：

- `轻量 skill`：保留 `SKILL.md + README.md + scripts/` 即可
- `中等复杂度 skill`：建议补 `references/`
- `重交付型 skill`：建议完整采用 `assets / examples / references / scripts`

## 对当前 Skill 的约束

对 `single-product-competitor-analysis` 来说，这套骨架是推荐标准，不改变现有任务目录结构。

需要明确区分：

- `skill 包结构`：服务对外分发、下载使用、案例学习
- `任务目录结构`：服务一次具体竞品分析任务的执行

前者可以标准化成 `assets / examples / references / scripts`。
后者继续保持现在的 `00-admin` 到 `08-visuals` 基准线。
