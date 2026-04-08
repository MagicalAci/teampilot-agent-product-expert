# Demo Packaging

一个可交付的 demo 包至少应包含：

- brief
- design system
- demo 入口文件
- preflight checklist
- walkthrough
- developer handoff

## 打包前检查

1. 目标平台正确
2. walkthrough 与页面一致
3. design system 与实现一致
4. 已知限制已写清

## 推荐交接顺序

1. 先看 `brief/demo-brief.md`
2. 再看 `design-system/MASTER.md`
3. 再打开 `demo/`
4. 最后看 `review/` 与 `handoff/`

## 部署上线

打包完成后，可通过 `/Demo上线` 将 Web 或 H5 demo 部署到云端：

```bash
python scripts/run_pipeline.py deploy --output-root ./outputs/demo-slug --platform vercel
```

支持的平台：

| 平台 | 适用场景 | 命令参数 |
|------|----------|----------|
| Vercel | 默认推荐，支持静态 + Serverless | `--platform vercel` |
| Surge.sh | 纯静态极速分享 | `--platform surge` |
| Netlify | 需要表单/Identity | `--platform netlify` |
| Cloudflare Pages | 团队已有凭证 | `--platform cloudflare` |

部署成功后会在 `deploy/deploy-result.md` 中记录在线 URL。

详细的平台安装、认证与故障排除参见 `references/demo-deploy-guide.md`。
