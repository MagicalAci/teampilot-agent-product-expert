# API Cookbook — 能力积木库

> 每个文件都是一个**独立可运行**的 Python 示例，覆盖幻视平台的一项 API 能力。
> 在实际 AI 策划中，按需组合这些积木搭建多 Agent 流程。

## 快速开始

```bash
# 所有示例只依赖 requests，无其他外部依赖
pip install requests

# 运行任意示例
python 01_text_generation.py
python 05_context_caching.py
python 11_multi_agent_pipeline.py
```

## 示例索引

| # | 文件 | 能力 | 难度 | 说明 |
|---|------|------|------|------|
| 01 | `01_text_generation.py` | 文本生成 | 基础 | 最简调用，验证连通性 |
| 02 | `02_streaming.py` | 流式输出 | 基础 | SSE 逐 token 输出 |
| 03 | `03_deep_thinking.py` | 深度思考 | 基础 | reasoning_content + reasoning_tokens |
| 04 | `04_continuation_prefix.py` | 续写模式 | 进阶 | prefix=true 续写 |
| 05 | `05_context_caching.py` | 上下文缓存 | 进阶 | 创建缓存 + 命中验证 + 成本对比 |
| 06 | `06_multi_turn_context.py` | 多轮对话 | 基础 | 上下文管理 |
| 07 | `07_image_understanding.py` | 图片理解 | 进阶 | base64 图片输入 |
| 08 | `08_video_understanding.py` | 视频理解 | 进阶 | 视频 URL 输入 |
| 09 | `09_visual_grounding.py` | 视觉定位 | 高级 | bbox 坐标返回 |
| 10 | `10_structured_json_output.py` | 结构化输出 | 进阶 | prompt 引导 JSON（平台不支持 response_format） |
| 11 | `11_multi_agent_pipeline.py` | 多 Agent 编排 | 高级 | 分析→策略→生成 三阶段串联 |

## 使用场景

**不是让你照抄这些示例**，而是在 AI 策划中按需组合：

- 简单文案生成 → 01 + 10
- 需要推理的分析 → 03 + 10
- 长 System Prompt 场景 → 05（缓存降本）
- 多模态审核/识别 → 07 或 08 + 09
- 完整业务流程 → 11（多 Agent 串联）

## 与 Skill 的关系

这些示例是 `/AI脚本` 工作流中的**参考代码**。实际执行 `/AI脚本` 时：

1. 先从 AI PRD 冻结字段合同和 Prompt 合同
2. 按业务需求从 cookbook 中选取需要的能力
3. 组合成项目专用的 AI 脚本
4. 用 `/AI测试` 验证

## 平台限制速查

详见 `references/platform-capabilities.md`，这里列几个高频坑：

- `response_format`（json_object / json_schema）**不可用** → 用 prompt 引导 JSON
- 图片/视频 **外网 URL 不可访问** → 用 base64 编码嵌入
- `/v1/files` 端点 **不存在** → 文档内容需先提取为文本
- 默认开启深度思考 → 不需要传 `thinking` 参数，想关闭时设 `thinking: disabled`（注意有些场景不生效）
