# Scripts 索引

这些脚本只负责机械劳动，不替代 AI / 人的判断。

## 当前脚本

- `init_ai_planning_delivery.py`
  - 初始化 AI PRD、AI测试报告、开发 README、脚本包清单
- `validate_ai_planning_assets.py`
  - 校验 PRD / 测试报告 / README 是否有关键章节，文件是否齐全
- `package_ai_script_bundle.py`
  - 把指定文件 / 目录打成 zip
- `export_svg_to_png.js`
  - 把 SVG 导出成 PNG

## 推荐顺序

1. 初始化：

```bash
python scripts/init_ai_planning_delivery.py demo-agent --output-dir ./out
```

2. 校验：

```bash
python scripts/validate_ai_planning_assets.py \
  --prd ./out/demo-agent-ai-prd.md \
  --test-report ./out/demo-agent-ai-test-report.md \
  --bundle-readme ./out/demo-agent-bundle-readme.md
```

3. 打包：

```bash
python scripts/package_ai_script_bundle.py ./dist/demo-agent.zip ./out
```
