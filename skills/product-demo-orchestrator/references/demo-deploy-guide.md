# Demo 部署上线指南

本指南覆盖四个推荐部署平台的安装、认证、部署与故障排除。

## 平台选择决策

| 场景 | 推荐平台 | 原因 |
|------|----------|------|
| 纯静态 demo + 快速分享 | Surge.sh | 零配置，一条命令 |
| 需要后端 API / AI 能力 | Vercel | Serverless Functions 支持 Node/Python |
| 团队内部长期使用 | Cloudflare Pages | 团队已有凭证，无限带宽 |
| 需要表单/Identity 等 | Netlify | 内置表单处理与 Identity 服务 |
| 未指定 | Vercel | 综合能力最强，免费额度充足 |

## 前置条件

- Node.js >= 18（所有平台均通过 `npx` 调用）
- demo 已通过 `validate` 校验
- stack 为 `web` 或 `h5`（SwiftUI 不支持在线部署）

---

## 一、Vercel（推荐）

### 安装与认证

```bash
# 全局安装（可选，npx 会自动下载）
npm install -g vercel

# 登录（首次需要）
vercel login
```

### 部署

```bash
# 预览部署（生成唯一 URL）
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel

# 生产部署
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel --prod

# 指定项目名
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel --project-name my-demo
```

### 直接使用 CLI

```bash
cd outputs/demo-slug/demo/web
npx vercel --yes          # 预览
npx vercel --yes --prod   # 生产
```

### Serverless Functions（API/AI 支持）

在 demo 目录下创建 `api/` 文件夹：

```
demo/web/
├── index.html
└── api/
    └── hello.js    # → /api/hello
```

```javascript
// api/hello.js
export default function handler(req, res) {
  res.json({ message: 'Hello from API' });
}
```

### 环境变量

```bash
vercel env add API_KEY
```

### 免费额度

- 100 deployments/day
- 100GB 带宽/月
- Serverless Function 执行时间 100GB-hrs/月

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `Error: No framework detected` | 正常，静态 HTML 不需要框架，Vercel 会作为静态站点部署 |
| 部署成功但页面空白 | 检查 `index.html` 是否在部署目录根层级 |
| API 路由 404 | 确保 `api/` 在部署目录根层级，文件导出 default function |

---

## 二、Surge.sh（极速分享）

### 安装与认证

```bash
# 全局安装（可选）
npm install -g surge

# 首次使用会自动引导创建账号（邮箱+密码）
```

### 部署

```bash
# 通过 pipeline
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform surge

# 指定域名
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform surge --project-name my-cool-demo
```

### 直接使用 CLI

```bash
npx surge ./outputs/demo-slug/demo/web                          # 随机域名
npx surge ./outputs/demo-slug/demo/web my-cool-demo.surge.sh    # 指定域名
```

### SPA 路由支持

如果 demo 使用客户端路由（React Router 等），需要在部署目录复制一份：

```bash
cp index.html 200.html
```

### 免费额度

- 无限发布
- 基本 SSL（surge.sh 子域名）
- 不支持后端/Serverless

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `Aborted - Loss of internet` | 检查网络连接，或使用代理 |
| 域名已被占用 | 换一个子域名，如 `my-demo-v2.surge.sh` |
| 刷新页面 404 | 创建 `200.html`（复制 `index.html`） |

---

## 三、Netlify

### 安装与认证

```bash
# 全局安装
npm install -g netlify-cli

# 登录
netlify login
```

### 部署

```bash
# 通过 pipeline
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform netlify

# 生产部署
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform netlify --prod
```

### 直接使用 CLI

```bash
npx netlify-cli deploy --dir=./outputs/demo-slug/demo/web            # 草稿
npx netlify-cli deploy --dir=./outputs/demo-slug/demo/web --prod     # 生产
```

### Serverless Functions

在部署目录下创建 `netlify/functions/`：

```
demo/web/
├── index.html
└── netlify/
    └── functions/
        └── hello.js    # → /.netlify/functions/hello
```

### 免费额度

- 300 分钟构建/月
- 100GB 带宽/月
- 125K Serverless Function 请求/月

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `Error: Not linked to a site` | 运行 `netlify init` 或 `netlify link` 先关联站点 |
| 部署后未更新 | 确认使用了 `--prod`，否则是草稿部署 |

---

## 四、Cloudflare Pages

### 安装与认证

```bash
# 全局安装
npm install -g wrangler

# 登录
wrangler login
```

### 部署

```bash
# 通过 pipeline
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform cloudflare

# 指定项目名
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform cloudflare --project-name my-demo
```

### 直接使用 CLI

```bash
npx wrangler pages deploy ./outputs/demo-slug/demo/web --project-name my-demo
```

### Workers（后端逻辑）

Cloudflare Pages 支持 Functions 目录：

```
demo/web/
├── index.html
└── functions/
    └── api/
        └── hello.js    # → /api/hello
```

### 免费额度

- 无限带宽
- 500 次构建/月
- Workers 100K 请求/天

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `Error: Missing account ID` | 运行 `wrangler login` 或设置 `CLOUDFLARE_ACCOUNT_ID` |
| 项目不存在 | 首次部署会自动创建项目 |

---

## 安全提醒

- **不要部署包含 API Key、Token 等敏感信息的 demo**。如需调用外部 API，使用平台的环境变量功能。
- 部署的 demo 默认公开可访问。如需限制访问，使用 Vercel 的 Password Protection 或 Surge Pro 的密码保护。
- 免费额度的 demo URL 可能在一段时间后过期或被回收，注意及时备份。

## 部署后分享

部署成功后，会生成 `deploy/deploy-result.md` 记录：

- 在线访问 URL
- 部署平台与时间
- 注意事项与限制

将 URL 直接分享给需要查看的人即可。如需更美观的分享页，可将 URL 嵌入飞书文档或企业微信。
