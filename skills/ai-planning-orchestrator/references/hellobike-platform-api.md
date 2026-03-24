# 幻视大模型平台 API 调用文档

> 本文档是 AI策划 Skill 的内置参考，供执行 `/AI脚本` 或 `/AI策划` 时直接查阅。
> 当需要写模型客户端、配置平台鉴权、选择模型时，优先看这份文档。

## 1. 平台概述

幻视是哈啰内部的大模型服务平台（代号 Jarvis），对话接口兼容 OpenAI 格式。2025.09.08 起，新版 chat 接口不再封装入参/出参，直接透传各厂商模型原生能力（思考开启、思考长度控制、结构化输出等）。

## 2. 当前应用凭证

| 项 | 值 |
|---|---|
| **APPID** | `AppHomeworkMonitorService` |
| **Secret Key** | `sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA` |
| **Agent ID** | `1349344319163531264` |

> 以上凭证用于盯盯学习监督业务，其他业务需在幻视平台申请自己的 APPID 和 Secret Key。

## 3. 可用模型与选型指南

### 3.1 模型清单

| 模型名称 | 定位 | 上下文 | 深度思考 | 适用场景 |
|---|---|---|---|---|
| **Doubao-Seed-2.0-Mini-0215** | 轻量快速 | 256k | 支持（4 档思考长度） | 低时延、高并发、成本敏感。效果≈Doubao-Seed-1.6。适合简单文案生成、分类、提取等轻量任务 |
| **Doubao-Seed-2.0-Pro-0215** | 旗舰全能 | 超长 | 支持 | 复杂推理、长链路 Agent 任务、多模态理解、多步规划、视频理解、高难度分析 |
| **Doubao-Seed-2.0-Lite-0215** | 均衡型 | 长上下文 | 支持 | 非结构化信息处理、内容创作、搜索推荐、数据分析等生产型工作。综合能力超 Doubao-Seed-1.8，成本显著优化 |

### 3.2 选型决策树

```
用户需求进来
│
├── 需要复杂推理 / 多步规划 / 多模态 / 视频理解？
│   └── YES → Doubao-Seed-2.0-Pro-0215
│
├── 需要内容创作 / 数据分析 / 多源融合 / 结构化输出？
│   └── YES → Doubao-Seed-2.0-Lite-0215
│
├── 简单分类 / 提取 / 短文案 / 高并发 / 成本优先？
│   └── YES → Doubao-Seed-2.0-Mini-0215
│
└── 不确定 → 默认 Doubao-Seed-2.0-Mini-0215（成本最低），效果不够再升级
```

### 3.3 选型原则

1. **成本优先用 Mini**：大部分简单生成任务（卡片文案、摘要、分类）Mini 就够
2. **质量优先用 Pro**：涉及复杂逻辑链、多约束推理、Agent 工具调用时用 Pro
3. **均衡场景用 Lite**：内容创作、报告生成、数据分析等需要稳定质量但不需要极端推理的场景
4. **先 Mini 后升级**：开发阶段先用 Mini 跑通流程，效果不够再切 Lite 或 Pro

## 4. API 端点

### 4.1 各环境地址

| 环境 | chat_url | 网络 | 稳定性 |
|---|---|---|---|
| **fat**（测试） | `https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions` | 办公网 | 不保证 |
| **uat** | `https://uat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions` | 办公网 | 不保证 |
| **pre** | `https://pre-aibrain-large-model-engine.hellobike.cn/v1/chat/completions` | 办公网 | 较稳定 |
| **prod-fast** | `https://aibrain-large-model-engine-fast.hellobike.cn/v1/chat/completions` | 服务内网 | 稳定 |
| **prod-common** | `https://aibrain-large-model-engine-common.hellobike.cn/v1/chat/completions` | 服务内网 | 稳定 |
| **prod-slow** | `https://aibrain-large-model-engine-slow.hellobike.cn/v1/chat/completions` | 服务内网 | 稳定 |

### 4.2 超时配置

| 环境 | 流式首包 | 流式整体 | 非流式 | 建议用途 |
|---|---|---|---|---|
| fat / uat / pre | 30s | 120s | 120s | 开发测试 |
| prod-fast | 3s | 10s | 10s | 快速响应场景 |
| prod-common | 10s | 30s | 30s | 常规场景 |
| prod-slow | 1min | 15min | 15min | 深度思考 / 长生成 |

**选择建议**：
- 开发测试阶段统一用 `fat` 或 `pre`
- 线上简单生成用 `prod-fast` 或 `prod-common`
- 线上深度思考 / 长文本用 `prod-slow`

## 5. 请求格式

### 5.1 鉴权方式

```
Authorization: Bearer {Secret_Key}
```

注意 `Bearer` 和 Key 之间有一个空格。

### 5.2 必填 Headers

| Header | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `Content-Type` | string | 是 | 请求类型 | `application/json; charset=utf-8` |
| `Authorization` | string | 是 | Bearer + Secret Key | `Bearer sk-Vh5i...` |
| `Accept` | string | 否 | 流式响应时携带 | `text/event-stream` |

此外，建议携带业务标识头：

| Header | 说明 |
|---|---|
| `X-App-Id` | APPID，用于分摊计费 |
| `X-Agent-Id` | Agent ID，标识具体应用 |

### 5.3 Request Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 模型服务名称，如 `Doubao-Seed-2.0-Mini-0215` |
| `messages` | array | 是 | 消息数组，兼容 OpenAI 格式 |
| `temperature` | number | 否 | 温度，0-2，默认 1 |
| `max_tokens` | number | 否 | 最大输出 token 数 |
| `stream` | boolean | 否 | 是否流式返回 |
| `caching` | object | 否 | 上下文缓存创建开关 |
| `caching.type` | string | 否 | `enabled` / `disabled` |
| `previous_response_id` | string | 否 | 使用已创建的缓存 ID |
| `ttl` | int | 否 | 缓存保存时长（秒），默认 259200 |

**深度思考控制**（豆包模型）：

通过 messages 或模型参数控制思考模式，直接透传火山引擎原生参数：
- `thinking`: `enabled` / `disabled`
- 思考长度：通过模型参数控制（4 档）

### 5.4 非流式请求示例

```bash
curl -X POST "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA" \
  -H "X-App-Id: AppHomeworkMonitorService" \
  -H "X-Agent-Id: 1349344319163531264" \
  -d '{
    "model": "Doubao-Seed-2.0-Mini-0215",
    "messages": [
      {"role": "system", "content": "你是一个专业的AI助手。"},
      {"role": "user", "content": "请用一句话介绍自己。"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### 5.5 流式请求示例

```bash
curl -X POST "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA" \
  -H "Accept: text/event-stream" \
  -H "X-App-Id: AppHomeworkMonitorService" \
  -H "X-Agent-Id: 1349344319163531264" \
  -d '{
    "model": "Doubao-Seed-2.0-Mini-0215",
    "messages": [
      {"role": "system", "content": "你是一个专业的AI助手。"},
      {"role": "user", "content": "请用一句话介绍自己。"}
    ],
    "stream": true
  }'
```

### 5.6 关闭深度思考的请求示例

```bash
curl -X POST "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA" \
  -H "X-App-Id: AppHomeworkMonitorService" \
  -H "X-Agent-Id: 1349344319163531264" \
  -d '{
    "model": "Doubao-Seed-2.0-Mini-0215",
    "messages": [
      {"role": "system", "content": "你是一个专业的AI助手。"},
      {"role": "user", "content": "生成一段JSON。"}
    ],
    "thinking": "disabled",
    "temperature": 0.2,
    "max_tokens": 2048
  }'
```

## 6. 响应格式

响应完全按照对应厂商的出参返回（兼容 OpenAI 格式）。

### 6.1 非流式响应结构

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Doubao-Seed-2.0-Mini-0215",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "total_tokens": 150,
    "prompt_tokens_details": {
      "cached_tokens": 0
    }
  }
}
```

### 6.2 流式响应结构

每个 chunk 以 `data: ` 前缀通过 SSE 返回：

```
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"你"},"index":0}]}

data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"好"},"index":0}]}

data: [DONE]
```

## 7. 上下文缓存

### 7.1 原理

将不变的 Prompt / System Message 创建为缓存，后续请求只需传变化部分。命中缓存的 token 价格约为正常的 **1/5**。

### 7.2 支持缓存的模型

火山系（ARK）：
- Doubao-Seed-2.0-Mini-0215
- Doubao-Seed-2.0-Pro-0215
- Doubao-Seed-2.0-Lite-0215
- Doubao-Seed-1.8-251215
- Doubao-Seed-1.6 系列全部
- Deepseek-V3-0324

百炼系（Qwen）：
- Qwen3-max、Qwen-plus、Qwen-flash-2025-07-28
- Qwen3-VL-Plus、DeepSeek-V3.2-Bailian
- Qwen-plus-prem-formal、Qwen3.5-plus、Qwen3.5-flash
- Qwen 系列不需要设置 TTL，缓存保存 5 分钟，5 分钟内再次命中则 TTL 重置

### 7.3 创建缓存

```bash
curl -X POST "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer {Secret_Key}" \
  -d '{
    "model": "Doubao-Seed-2.0-Mini-0215",
    "messages": [
      {"role": "system", "content": "你是一个专业的学习分析师...（长 System Prompt）"}
    ],
    "caching": {"type": "enabled"},
    "ttl": 259200
  }'
```

返回的 `id` 字段（形如 `resp_xxx` 或 `ctx-xxx`）即为缓存 ID。

### 7.4 使用缓存

```bash
curl -X POST "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer {Secret_Key}" \
  -d '{
    "model": "Doubao-Seed-2.0-Mini-0215",
    "messages": [
      {"role": "user", "content": "分析这段学习数据..."}
    ],
    "previous_response_id": "resp_021760509141470..."
  }'
```

### 7.5 验证缓存命中

响应中 `usage.prompt_tokens_details.cached_tokens` 不为 0 即表示命中。

### 7.6 缓存效果

| 指标 | 无缓存 | 有缓存 | 提升 |
|---|---|---|---|
| 单次调用成本 | 100% | ~50% | **节省约 50%** |
| 平均耗时 | 100% | ~69% | **降低约 31%** |
| P90 耗时 | 100% | ~68% | **降低约 32%** |
| P95 耗时 | 100% | ~67% | **降低约 33%** |

**最佳实践**：把不变的 System Prompt 创建为缓存，变化的用户内容通过 user message 传入。

### 7.7 缓存计费

```
缓存费用 = 缓存 token 数 × 缓存存在时间（ttl） × 缓存单价
```

创建缓存会收取额外存储费用，需评估实际场景后使用。

## 8. 各厂商模型参数文档

平台接入方式基于 OpenAI 基本格式，不同厂商的模型参数参考：

| 厂商 | 请求参数文档 | 响应参数文档 |
|---|---|---|
| 豆包/火山引擎 | [请求体](https://www.volcengine.com/docs/82379/1494384#RxN8G2nH) | [非流式](https://www.volcengine.com/docs/82379/1494384#fT1TMaZk) / [流式](https://www.volcengine.com/docs/82379/1494384#jp88SeXS) |
| Qwen（通义千问） | [请求体](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#f4514ce9072sb) | [非流式](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#182c685357r7w) / [流式](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#f0b9c155ad0e0) |
| OpenAI | [请求体](https://platform.openai.com/docs/api-reference/chat/create) | [非流式](https://platform.openai.com/docs/api-reference/chat/object) / [流式](https://platform.openai.com/docs/api-reference/chat_streaming/streaming) |
| Claude | [请求体](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) | 同请求文档 |
| DeepSeek | [请求体](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion) | 同请求文档 |

## 9. 问题排查

### 9.1 X-Trace-Id 链路追踪

每次调用 `chat/completions` 响应头中会返回唯一 `X-Trace-Id`，排查问题时提供此 ID 给平台研发。

**获取方式**：

```bash
curl -i -X POST "https://pre-aibrain-large-model-engine.hellobike.cn/v1/chat/completions" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer {Secret_Key}" \
  -d '{...}'
```

`-i` 参数会同时输出响应头和响应体。

**Python 获取方式**：

```python
import requests

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
for key, value in response.headers.items():
    print(f"{key}: {value}")
```

### 9.2 常见问题

| 问题 | 原因 | 解决 |
|---|---|---|
| 401 Unauthorized | Secret Key 错误或过期 | 检查 Authorization 头格式，确认 Bearer 和 Key 之间有空格 |
| 模型不可用 | 应用未关联该模型 | 在幻视平台应用配置中添加模型 |
| 响应超时 | 超出环境超时限制 | 换用 slow 分组或缩短输入 |
| 缓存未命中 | `previous_response_id` 错误或 TTL 过期 | 检查缓存 ID 是否正确，是否在 TTL 范围内 |
| `json_schema` 不支持 | 当前模型不支持结构化输出 | 在 Prompt 中显式要求 JSON 格式，并用 `temperature: 0.2` 降温 |

## 10. TypeScript 模型客户端参考实现

```typescript
const HELLOBIKE_CONFIG = {
  chatUrl: process.env.HELLOBIKE_CHAT_URL
    || 'https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions',
  secretKey: process.env.HELLOBIKE_SECRET_KEY
    || 'sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA',
  appId: process.env.HELLOBIKE_APP_ID
    || 'AppHomeworkMonitorService',
  agentId: process.env.HELLOBIKE_AGENT_ID
    || '1349344319163531264',
  defaultModel: 'Doubao-Seed-2.0-Mini-0215',
};

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionOptions {
  model?: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  thinking?: 'enabled' | 'disabled';
  stream?: boolean;
}

async function chatCompletion(options: ChatCompletionOptions) {
  const config = HELLOBIKE_CONFIG;

  const response = await fetch(config.chatUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Authorization': `Bearer ${config.secretKey}`,
      'X-App-Id': config.appId,
      'X-Agent-Id': config.agentId,
    },
    body: JSON.stringify({
      model: options.model || config.defaultModel,
      messages: options.messages,
      temperature: options.temperature ?? 0.7,
      max_tokens: options.max_tokens ?? 2048,
      thinking: options.thinking ?? 'disabled',
      stream: options.stream ?? false,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
```
