# education-prd-orchestrator / scripts

可独立分发的脚本入口，负责环境自检、交付目录初始化和基础校验。

## 快速开始

```bash
python scripts/run_pipeline.py check-env
python scripts/run_pipeline.py bootstrap-tools
python scripts/run_pipeline.py init-delivery demo-product --title "Demo Product"
python scripts/run_pipeline.py validate --output-root outputs/demo-product
```

## 脚本清单

| 脚本 | 用途 |
|------|------|
| `run_pipeline.py` | 统一 CLI 入口（`check-env / bootstrap-tools / init-delivery / validate / package-smoke`） |
| `bootstrap_product_planning_tools.py` | 创建 managed `.venv`、安装 `requirements.txt`、写出环境状态 |
| `bootstrap-macos.sh` | 在 macOS 上自动补 Homebrew / `python3`，再调用 Python bootstrap |
| `doctor-macos.sh` | macOS 快速健康检查包装脚本 |
| `init_product_planning_delivery.py` | 从本地模板播种 `outputs/<slug>/` 交付骨架 |
| `analyze_chat_csv.py` | 汇总客服聊天 CSV 的关键词与消息分布 |
| `analyze_kb_xlsx.py` | 汇总知识库 XLSX 的 sheet、关键词和命中情况 |
| `build_screenshot_index.py` | 扫描截图目录并生成索引 |
| `export_svg_to_png.py` | 将 SVG 结构图导出为 PNG 供正文引用 |
| `validate_prd_assets.py` | 校验 Markdown / HTML 中引用的图片路径是否存在 |
| `eppo/` | 共享运行时、初始化和 CLI 逻辑 |

## 交付根目录约定

`init-delivery` 默认创建：

```text
outputs/<slug>/
├── prd.md
├── images/
├── html/
├── charts/
├── evidence/
└── review/
```

## 典型命令

### 1. 只看环境状态

```bash
python scripts/run_pipeline.py check-env --json
```

### 2. 自动补环境

```bash
python scripts/run_pipeline.py bootstrap-tools --json
```

macOS 无 `python3` 时：

```bash
bash scripts/bootstrap-macos.sh doctor
```

### 3. 初始化一套交付骨架

```bash
python scripts/run_pipeline.py init-delivery hanxue-liaoliao --title "和韩雪聊聊教育"
```

### 4. 校验交付目录

```bash
python scripts/run_pipeline.py validate --output-root outputs/hanxue-liaoliao
```

### 5. 跑最小 smoke

```bash
python scripts/run_pipeline.py package-smoke --json
```
