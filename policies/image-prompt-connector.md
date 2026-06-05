# 图片提示词连接器（nano-banana-pro）

`/图片提示词` 是产品专家 Agent 的**视觉提示词助手命令**（跨能力工具，与 `/安全扫描` 同类，不算第 6 个产品能力）。当产品工作需要产图——PRD 配图/总览图、Demo 视觉资产、海报、缩略图、电商图、信息图等——它从 10000+ 条精选 Nano Banana Pro（Gemini 图像模型）提示词里按使用场景智能检索，给出可直接用的提示词 + 样例图，并能按你的内容"改写"出定制提示词。

> **来源与许可**：连接 [YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill](https://github.com/YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill)（MIT，作者 YouMind）。本仓库只做**连接器集成**（按需安装 + 不可用降级），**不 vendor** 那 10000+ 条提示词数据（上游每天两次自动同步，vendor 会立刻过时）。

---

## 何时用

- `/产品策划` 需要 PRD 封面/总览图/功能配图时
- `/Demo开发` 需要视觉资产、占位图、视觉风格参考时
- `/深度调研` / 内容需要海报、缩略图、信息图时
- 任何"帮我想个图怎么画 / 给我个出图提示词"的场景

## 提示词类目（上游）

社媒贴文（10000+）、产品营销（3600+）、头像（1000+）、海报/传单（470+）、信息图（450+）、电商（370+）、游戏资产（370+）、漫画/分镜（280+）、YouTube 缩略图（170+）、App/Web 设计（160+）等。

## 安装（按需）

```bash
# 通用安装器（自动识别 Cursor/Claude Code/Codex 等）
npx skills i YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill

# 或 OpenClaw
clawhub install nano-banana-pro-prompts-recommend
```

安装后该技能自带 token 高效检索（grep 式，不整文件加载），并每天两次自动更新提示词库。

## 两种用法

1. **直接检索**：用一句话描述需求 → 返回最多 3 条匹配（含译名/描述 + 可复制的英文提示词 + 样例图 + 是否需参考图）。
   - 例：`/图片提示词 赛博朋克风格头像`、`/图片提示词 旅行博客文章封面`、`/图片提示词 白底产品图`
2. **内容改写（Remix）**：贴入文章/脚本/PRD 段落 → 推荐风格模板 → 追问几个个性化问题（性别/情绪/场景）→ 产出贴合内容的定制提示词。

## 与现有能力的衔接

- **产品策划**：PRD 配图阶段（见 `skills/education-prd-orchestrator` 的 visualization 协议）可先用本命令拿到出图提示词，再交给图像模型生成，存入 `images/`
- **Demo 开发**：视觉资产/设计系统取图前，用本命令对齐风格
- 输出始终给**英文提示词**用于生成；说明文字用中文

## 降级（未安装/无网络时）

不静默跳过。改用手写提示词骨架：`主体 + 风格 + 构图 + 光照 + 色调 + 细节 + 负向约束`，并说明这是降级（未接入 nano-banana 库，覆盖面有限）。出图提示词工程方法见 `policies/prompt-engineering-techniques.md`。

## 归属

- 来源：https://github.com/YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill ，MIT，作者 YouMind
- 提示词由 YouMind.com 通过公开社区搜集；本包仅做连接器集成，数据与更新归上游
