# 示例：内置脚本怎么跑

## 初始化

```bash
python scripts/init_ai_planning_delivery.py lesson-agent --output-dir ./out
```

## 校验

```bash
python scripts/validate_ai_planning_assets.py \
  --prd ./out/lesson-agent-ai-prd.md \
  --test-report ./out/lesson-agent-ai-test-report.md \
  --bundle-readme ./out/lesson-agent-bundle-readme.md
```

## 打包

```bash
python scripts/package_ai_script_bundle.py \
  ./dist/lesson-agent.zip \
  ./src \
  ./examples \
  ./tests \
  ./out/lesson-agent-ai-prd.md \
  ./out/lesson-agent-ai-test-report.md \
  ./out/lesson-agent-bundle-readme.md \
  --root-name lesson-agent
```
