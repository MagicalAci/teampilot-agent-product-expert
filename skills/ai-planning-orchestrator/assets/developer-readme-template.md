# AI脚本交付 README - [项目名 / 能力名]

> **适用命令**: `/AI脚本` 或 `/AI策划`  
> **交付日期**: YYYY-MM-DD  
> **版本号**: Vx.x  
> **面向对象**: Backend / H5 / iOS / Android / 联调同学

## 1. 交付概览

- 这次交付解决什么问题
- 包里哪些内容可直接接入
- 哪些内容只是样例 / 参考实现

## 2. 目录结构

```text
[bundle-root]/
├── src/
├── examples/
├── tests/
├── docs/
└── README.md
```

## 3. 入口文件

| 类型 | 路径 | 作用 |
|---|---|---|
| 核心生成器 | `[path]` | `[标准化 / 编排 / 汇总]` |
| 模型客户端 | `[path]` | `[调用模型平台]` |
| Route / Handler | `[path]` | `[HTTP 接入示例]` |
| Demo 脚本 | `[path]` | `[本地验证入口]` |
| 测试文件 | `[path]` | `[单元 / 集成验证]` |

## 4. 配置项

| 配置项 | 是否必填 | 默认值 / 来源 | 说明 |
|---|---|---|---|
| `chat_url` | 是 / 否 | | |
| `model` | 是 / 否 | | |
| `APPID` | 是 / 否 | | |
| `agent ID` | 是 / 否 | | |
| `Secret Key / API Key` | 是 / 否 | | |
| `thinking` | 是 / 否 | | |

## 5. 调用方式

### 5.1 CLI / Demo

```bash
[command]
```

说明：

- 输入文件路径：
- 输出文件路径：
- 适用场景：

### 5.2 HTTP / Route

```bash
curl -X POST "[url]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [token-if-needed]" \
  -d @examples/input.json
```

说明：

- 请求方法：
- 请求路径：
- 必填 headers：
- 请求体样例位置：
- 返回样例位置：

### 5.3 输入输出样例

| 类型 | 路径 | 说明 |
|---|---|---|
| 输入样例 | `[path]` | `[可直接跑]` |
| 输出样例 | `[path]` | `[与 PRD 字段一致]` |

## 6. 验证命令

```bash
[unit test command]
[demo command]
[route test command]
```

## 7. 已知限制

- 当前模型对结构化输出的限制
- 当前脚本未覆盖的边界
- 当前包不负责的能力

## 8. 目标项目还需补的能力

- 鉴权 / Secret 注入
- CORS / 网关放行
- 监控 / 日志 / traceId
- 正式环境配置
