# 幻视平台能力实测矩阵

> 基于 2026.03.25 对 `fat` 环境的真实 API 调用测试。
> 每项能力标注：支持状态、限制条件、替代方案。

## 测试环境

| 项 | 值 |
|---|---|
| 端点 | `fat-aibrain-large-model-engine.hellobike.cn` |
| 测试模型 | Mini / Lite / Pro |
| 测试日期 | 2026.03.25 |

## 能力矩阵

### 完全支持

| 能力 | 状态 | 测试方式 | 示例文件 |
|------|------|---------|---------|
| **文本生成** | PASS | 三个模型均成功 | `01_text_generation.py` |
| **流式输出** | PASS | SSE `data:` 前缀正常 | `02_streaming.py` |
| **深度思考** | PASS | 默认开启，`reasoning_tokens=584` | `03_deep_thinking.py` |
| **续写模式** | PASS | `prefix:true` 续写正常 | `04_continuation_prefix.py` |
| **上下文缓存** | PASS | 创建+命中均成功，`cached_tokens=48` | `05_context_caching.py` |
| **多轮对话** | PASS | messages 数组保持上下文 | `06_multi_turn_context.py` |
| **图片理解** | PASS | base64 编码方式成功 | `07_image_understanding.py` |
| **视频理解** | PASS | Pro 模型，视频 URL 方式 | `08_video_understanding.py` |
| **视觉定位** | PASS | 返回 `<bbox>` 坐标，base64 方式 | `09_visual_grounding.py` |

### 部分支持（有替代方案）

| 能力 | 状态 | 限制 | 替代方案 | 示例文件 |
|------|------|------|---------|---------|
| **结构化输出** | PARTIAL | `response_format`（json_object / json_schema）均报 InvalidParameter | system prompt 强约束 + `temperature: 0.1` + 输出校验重试 | `10_structured_json_output.py` |
| **图片理解(URL)** | PARTIAL | 外网图片 URL 超时（服务端 120s 限制） | 改用 base64 编码嵌入 | `07_image_understanding.py` |
| **视觉定位(URL)** | PARTIAL | 同上，外网 URL 不可访问 | 同上 | `09_visual_grounding.py` |

### 不支持

| 能力 | 状态 | 表现 | 影响 |
|------|------|------|------|
| **文件输入 (File API)** | FAIL | `/v1/files` 返回 404 | 无法上传文件 |
| **文档理解** | FAIL | content type `file` 不支持，仅支持 `text`, `image_url`, `video_url`, `input_audio` | 需先提取文档文本再传入 |
| **Responses API** | FAIL | `/v1/responses` 返回 404 | 使用 Chat Completions API |
| **Embeddings** | FAIL | 模型能力不匹配 | 需单独申请向量化模型 |

## 模型 × 能力矩阵

| 能力 | Mini | Lite | Pro |
|------|------|------|-----|
| 文本生成 | YES | YES | YES |
| 流式输出 | YES | YES | YES |
| 深度思考 | YES | YES | YES |
| 续写模式 | YES | YES | YES |
| 上下文缓存 | YES | YES | YES |
| 图片理解 | YES | YES | YES |
| 视频理解 | 未测试 | 未测试 | YES |
| 视觉定位 | 未测试 | 未测试 | YES |
| 结构化输出(response_format) | NO | NO | NO |

## 关键限制清单

### 网络限制

- **外网 URL 不可访问**：图片/视频的外网 URL 会触发服务端 120 秒超时
- **解决**：图片用 base64 编码嵌入；视频需使用内网可达的 URL

### 参数限制

- **`response_format` 不可用**：`json_object` 和 `json_schema` 类型均报 `InvalidParameter`
- **解决**：通过 system prompt 约束 + 低温度 + 输出校验实现等效效果（见示例 10）

### 端点限制

- **仅 `/v1/chat/completions` 可用**：`/v1/files`、`/v1/responses`、`/v1/context/create` 均返回 404
- **影响**：File API、Responses API 不可用

### 图片限制

- **最小尺寸 14×14 像素**：更小的图片会被拒绝
- **格式要求**：支持 PNG/JPEG，不支持 PDF 等文档格式

### 深度思考

- **默认开启**：不需要传 `thinking` 参数
- **顶层 `thinking` 字符串参数可能报错**：实测 `"thinking": "enabled"` 会报 `Mismatch type`
- **关闭方式**：`"thinking": "disabled"` 在部分场景可生效

## 成本优化建议

1. **用缓存降本**：不变的 System Prompt 创建缓存，命中后 token 价格降至 1/5
2. **默认 Mini**：简单任务用 Mini，效果不够再升级 Lite/Pro
3. **结构化输出用低温度**：`temperature: 0.1` 显著提高 JSON 输出稳定性
4. **图片用合适分辨率**：不需要传原图，缩放到合适尺寸再 base64 编码
