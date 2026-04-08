---
name: product-demo-orchestrator
display_name: "产品Demo开发编排"
description: "面向 Web、H5 与 SwiftUI 产品 demo 的重型编排 Skill，覆盖 brief 冻结、设计系统、脚手架初始化、页面打磨、校验与交接，以及一键部署上线。"
category: product
version: "1.0.0"
review_criteria:
  - label: "入口命令完整：/Demo开发、/Demo设计系统、/Demo脚手架、/Demo打磨、/Demo校验、/Demo上线 能分别覆盖对应子流程。"
  - label: "brief 冻结合规：开始前明确 demo 目标、受众、平台、时长、必须展示路径与非目标范围。"
  - label: "平台选择正确：Web、H5、SwiftUI 的交付骨架与用户目标一致，不混淆平台约束。"
  - label: "设计系统完整：输出主风格、页面结构、色板、字体、关键组件、反模式与页面级覆盖。"
  - label: "脚手架可用：初始化后目录、README、入口文件与交接文档完整存在。"
  - label: "打磨顺序正确：先基线界面，再处理无障碍、元信息与动效性能，不跳步。"
  - label: "演示可讲述：必须保留 demo walkthrough，能说明推荐演示路径与关键镜头。"
  - label: "校验脚本有效：validate 能识别缺失文件、缺少标题或平台入口异常。"
  - label: "打包结果可交付：package 能产出 zip，且保留 design system、demo 文件与 handoff。"
  - label: "交接信息完整：必须说明运行方式、已知限制、后续研发接手点。"
  - label: "部署上线可用：deploy 能将 web/h5 demo 部署到云端并返回可访问 URL，SwiftUI 正确拒绝并给出替代建议。"
---

# 产品 Demo 开发主 Skill

## Overview

这是一个面向产品 demo 开发的重型 orchestrator skill，用来把一次 demo 交付拆成稳定的 6 段：

1. 冻结 brief
2. 产出轻量设计系统
3. 初始化平台脚手架
4. 打磨 UI 与交互
5. 校验、打包与交接
6. 部署上线与分享

它不是通用前端百科，也不是纯设计文档模板，而是一个“能直接起 demo 交付骨架”的工作流 skill。

## 六条指令

### `/Demo开发 [主题]`

用于启动完整 demo 流程，默认串起：

1. 冻结 demo brief
2. 生成 design system
3. 选择 stack 并初始化交付骨架
4. 打磨页面与演示路径
5. 运行校验并打包
6. 部署上线并分享链接（可选，用户确认后执行）

### `/Demo设计系统 [主题]`

只产出或刷新 demo 的设计系统，不默认初始化代码骨架。

### `/Demo脚手架 [主题]`

只做平台选择、初始化输出目录、生成入口文件与交接模板。

### `/Demo打磨 [输出目录或主题]`

用于在已有骨架上补齐基线 UI、无障碍、metadata 与动效性能。

### `/Demo校验 [输出目录或主题]`

用于校验已有 demo 资产是否齐全，并输出适合评审与交接的检查结论。

### `/Demo上线 [输出目录或主题]`

将已完成的 Web 或 H5 demo 部署到云端，获取可分享的在线链接。支持四个平台：

- **Vercel**（默认推荐）：支持静态部署 + Serverless Functions，适合需要后端 API / AI 的 demo
- **Surge.sh**：零配置极速分享，适合纯静态 demo 的快速预览
- **Netlify**：支持表单处理与 Serverless Functions
- **Cloudflare Pages**：团队已有凭证，无限带宽，适合长期保留

SwiftUI demo 不支持在线部署，会提示替代方案（录屏 / 代码仓库链接）。

## 支持的平台

- `web`：桌面或响应式网页 demo，默认输出 `demo/web/index.html`
- `h5`：移动端 H5 demo，默认输出 `demo/h5/index.html`
- `swiftui`：SwiftUI 原生 demo，默认输出 `demo/swiftui/*.swift`

如果用户没有明确平台，必须先停下来确认，不要边做边猜。

## Default Deliverables

- `outputs/<slug>/demo-config.json`
- `outputs/<slug>/brief/demo-brief.md`
- `outputs/<slug>/design-system/MASTER.md`
- `outputs/<slug>/design-system/pages/home.md`
- `outputs/<slug>/review/preflight-checklist.md`
- `outputs/<slug>/review/demo-walkthrough.md`
- `outputs/<slug>/handoff/developer-handoff.md`
- `outputs/<slug>/demo/README.md`
- `outputs/<slug>/demo/web/index.html` 或 `outputs/<slug>/demo/h5/index.html` 或 `outputs/<slug>/demo/swiftui/*.swift`
- `outputs/<slug>/deploy/deploy-result.md`（部署上线后生成）

## Workflow

### 1. Freeze the brief

先确认：

- 这次 demo 的目标是什么
- 主要受众是谁
- 演示时长是 30 秒、3 分钟还是更长
- 目标平台是 `web`、`h5` 还是 `swiftui`
- 必须展示哪几段主路径
- 这次明确不做什么

如果用户目标里同时包含多个平台，而又没有说明优先级，先停下来确认主交付平台。

### 2. Build a design system

根据 brief 输出：

- 产品气质
- 页面结构
- 色板与字体
- 核心组件
- 关键交互动效
- anti-patterns
- 页面级覆盖规则

设计系统要偏“可演示”和“可实现”，不要生成纯概念风格板。

### 3. Initialize the scaffold

用脚本初始化最小交付骨架：

```bash
python scripts/run_pipeline.py init demo-slug --title "Demo Title" --stack web --output-root ./outputs/demo-slug --overwrite
```

初始化后再开始具体页面实现，不要先写代码再补骨架。

### 4. Polish the demo

打磨顺序固定为：

1. baseline UI
2. accessibility
3. metadata / presentation readiness
4. motion performance
5. demo walkthrough

如果用户只是要“一个能演示的页面”，也至少要经过这 5 步的最小版本。

### 5. Validate and package

校验：

```bash
python scripts/run_pipeline.py validate --output-root ./outputs/demo-slug --json
```

打包：

```bash
python scripts/run_pipeline.py package --output-root ./outputs/demo-slug --output ./dist/demo-slug.zip
```

### 6. Deploy and share

部署前先确认：

- stack 是否为 `web` 或 `h5`（SwiftUI 不支持）
- validate 是否通过
- 用户是否确认要上线

选择平台并部署：

```bash
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel
```

也可指定项目名和生产模式：

```bash
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel --project-name my-demo --prod
```

部署成功后，在 `deploy/deploy-result.md` 中记录在线 URL、平台与时间，并在聊天中直接展示可点击链接。

## User Checkpoints

这些场景必须停下来问用户：

- 平台未明确
- 要同时覆盖 Web、H5、SwiftUI，但未给优先级
- 用户只说“做个 demo”，没说目标受众和演示场景
- 用户要求复用现有代码或设计系统，但没有给路径
- 需要真实品牌素材、图标、截图，而当前上下文里并不存在
- 用户要求直接出原生工程，但没有说明是样例代码还是可编译工程
- 部署平台未指定时，推荐并等用户确认
- 首次使用某部署平台，需要登录认证时
- demo 可能包含敏感信息（API Key、Token 等）时，发出安全警告
- SwiftUI demo 请求上线时，提示不支持并给出替代方案

## Non-Negotiable Rules

- 不要在平台没确定时直接生成入口文件
- 不要把设计系统写成空泛风格描述，必须落到组件、页面结构和禁用项
- 不要跳过 demo walkthrough
- 不要把“可交付”理解成只有页面文件，必须有 handoff 和 review 文档
- 不要只追求好看而忽略 accessibility、metadata 与动效成本
- 不要把 SwiftUI、Web、H5 三种平台的术语和约束混写
- 不要在用户未确认的情况下自动执行部署
- 不要部署包含 API Key、Token 等敏感信息的 demo，必须先警告
- 不要对 SwiftUI demo 尝试在线部署，必须明确提示不支持并建议替代方案

## Scripts

- `scripts/init_demo_delivery.py`
  - 初始化 demo 输出目录、设计系统、review 与 handoff 文档，以及平台入口文件
- `scripts/validate_demo_assets.py`
  - 校验 demo brief、design system、review、handoff 与平台入口文件
- `scripts/package_demo_bundle.py`
  - 把输出目录打成 zip
- `scripts/deploy_demo.py`
  - 将 demo 部署到 Vercel / Surge / Netlify / Cloudflare Pages
- `scripts/run_pipeline.py`
  - 统一 CLI：`init`、`validate`、`package`、`deploy`、`package-smoke`

## Resources

- 简报协议：`references/brief-and-success-metrics.md`
- 设计系统：`references/design-system-lite.md`
- Web/H5 模式：`references/web-h5-demo-patterns.md`
- SwiftUI 模式：`references/swiftui-demo-patterns.md`
- 打磨清单：`references/demo-polish-checklist.md`
- 打包与交接：`references/demo-packaging.md`
- 部署上线：`references/demo-deploy-guide.md`
- 上游复用说明：`references/upstream-inspirations.md`
