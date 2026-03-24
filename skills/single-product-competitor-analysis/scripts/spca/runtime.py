from pathlib import Path
from typing import Optional

from spca.config import PLATFORM_BACKEND_PRIORITY, PLATFORM_OUTPUT_ORDER, PLATFORM_SAMPLE_TARGETS
from spca.utils import ensure_dir, now_compact, read_json, slugify, write_json, write_text

PLATFORMS = PLATFORM_OUTPUT_ORDER
TASK_MODES = {"full", "crawl", "guide"}


def load_task_card(task_card_path: Path) -> dict:
    task_card = read_json(task_card_path)
    task_card["task_mode"] = normalize_task_mode(task_card.get("task_mode"))
    if "product_slug" not in task_card or not task_card.get("product_slug"):
        base_name = task_card.get("product_name") or task_card.get("analysis_goal") or task_card_path.stem
        task_card["product_slug"] = slugify(base_name)
    if not task_card.get("task_slug"):
        task_card["task_slug"] = f"{task_card['product_slug']}-{now_compact()}"
        write_json(task_card_path, task_card)
    return task_card


def normalize_task_mode(value: Optional[str]) -> str:
    if value in TASK_MODES:
        return value
    return "full"


def detect_workspace_root(task_card_path: Path) -> Path:
    task_root = task_card_path.parent.resolve()
    if (task_root / ".cursor").exists() or (task_root / "docs").exists():
        return task_root

    skill_root = Path(__file__).resolve().parents[2]
    if skill_root.parent.name == "skills" and skill_root.parent.parent.name == ".cursor":
        return skill_root.parent.parent.parent

    return task_root


def default_output_root(workspace_root: Path, task_card: dict) -> Path:
    task_mode = task_card["task_mode"]
    slug = task_card["task_slug"]
    if task_mode == "crawl":
        return workspace_root / "docs" / "workspaces" / "research" / "_data" / "crawl-tasks" / slug
    if task_mode == "guide":
        return workspace_root / "docs" / "workspaces" / "research" / "_data" / "guide-tasks" / slug
    return (
        workspace_root
        / "docs"
        / "workspaces"
        / "research"
        / "_data"
        / "single-product"
        / task_card["product_slug"]
        / slug
    )


def default_report_path(task_card: dict, output_root: Path) -> Path:
    if task_card["task_mode"] == "full":
        return output_root / "06-writing" / f"{task_card['task_slug']}.md"
    return output_root / "exports" / "final-report.md"


def resolve_paths(task_card: dict, task_card_path: Path) -> dict:
    workspace_root = detect_workspace_root(task_card_path)

    output_root = (
        Path(task_card["output_root"]).resolve()
        if task_card.get("output_root")
        else default_output_root(workspace_root, task_card)
    )
    if task_card["task_mode"] == "full":
        # Full tasks always keep the main report inside the task folder.
        report_path = default_report_path(task_card, output_root)
    else:
        report_path = (
            Path(task_card["report_path"]).resolve()
            if task_card.get("report_path")
            else default_report_path(task_card, output_root)
        )
    imports_root = (
        Path(task_card["imports_root"]).resolve()
        if task_card.get("imports_root")
        else task_card_path.parent / "imports"
    )
    manual_root = (
        Path(task_card["manual_root"]).resolve()
        if task_card.get("manual_root")
        else task_card_path.parent / "manual"
    )

    return {
        "workspace_root": workspace_root,
        "task_mode": task_card["task_mode"],
        "task_card": output_root / "task-card.json",
        "output_root": output_root,
        "imports_root": imports_root,
        "manual_root": manual_root,
        "admin_root": output_root / "00-admin",
        "process_root": output_root / "01-process",
        "keywords_root": output_root / "02-keywords",
        "platforms_root": output_root / "03-platforms",
        "experience_root": output_root / "04-experience",
        "synthesis_root": output_root / "05-synthesis",
        "writing_root": output_root / "06-writing",
        "factcheck_root": output_root / "07-factcheck",
        "visuals_root": output_root / "08-visuals",
        "raw_root": output_root / "raw",
        "normalized_root": output_root / "normalized",
        "analysis_root": output_root / "analysis",
        "exports_root": output_root / "exports",
        "report_path": report_path,
        "workspace_products_root": report_path.parent,
    }


def init_workspace(task_card: dict, task_card_path: Path) -> dict:
    paths = resolve_paths(task_card, task_card_path)
    task_mode = paths["task_mode"]

    for key in base_directory_keys(task_mode):
        ensure_dir(paths[key])
    ensure_dir(paths["imports_root"])
    ensure_dir(paths["manual_root"])

    if task_mode in {"full", "crawl"}:
        for channel in ["web", "reviews", "social", "seo", "pricing"]:
            ensure_dir(paths["imports_root"] / channel)
        for platform in PLATFORMS:
            platform_root = ensure_dir(paths["platforms_root"] / platform)
            ensure_dir(platform_root / "assets")

    if task_mode in {"full", "guide"}:
        ensure_dir(paths["experience_root"] / "uploads")
        ensure_dir(paths["experience_root"] / "frames")
        ensure_dir(paths["experience_root"] / "screenshots")
        ensure_dir(paths["experience_root"] / "notes")
        ensure_dir(paths["manual_root"] / "uploads")
        ensure_dir(paths["manual_root"] / "screenshots")
        ensure_dir(paths["manual_root"] / "frames")
        ensure_dir(paths["manual_root"] / "notes")

    if task_mode == "full":
        ensure_dir(paths["visuals_root"] / "svg")
        ensure_dir(paths["visuals_root"] / "png")

    write_json(paths["task_card"], task_card)
    seed_workspace_files(paths, task_card)
    return paths


def base_directory_keys(task_mode: str) -> list[str]:
    keys = [
        "output_root",
        "admin_root",
        "process_root",
        "raw_root",
        "normalized_root",
        "analysis_root",
        "exports_root",
        "workspace_products_root",
    ]
    if task_mode in {"full", "crawl"}:
        keys.extend(["keywords_root", "platforms_root", "synthesis_root"])
    if task_mode in {"full", "guide"}:
        keys.append("experience_root")
    if task_mode == "full":
        keys.extend(["writing_root", "factcheck_root", "visuals_root"])
    return keys


def seed_workspace_files(paths: dict, task_card: dict) -> None:
    task_mode = paths["task_mode"]
    seed_text(paths["admin_root"] / "TASK_CARD.md", build_task_card_md(task_card))
    seed_text(paths["process_root"] / "PROCESS_LOG.md", process_log_template(task_card))
    seed_text(paths["process_root"] / "KEY_DECISIONS.md", decision_log_template(task_card))

    if task_mode in {"full", "crawl"}:
        seed_text(paths["keywords_root"] / "SEARCH_KEYWORDS.md", keyword_template(task_card))
        seed_text(paths["keywords_root"] / "SEARCH_KEYWORDS.csv", "keyword,category,reason,confirmed\n")
        seed_text(paths["imports_root"] / "README.md", imports_root_template(task_card))
        for platform in PLATFORMS:
            platform_root = paths["platforms_root"] / platform
            seed_text(platform_root / "summary.md", platform_summary_template(platform))
            seed_text(
                platform_root / "data.csv",
                "id,source_id,source_channel,title,url,local_path,tier,platform,collected_at,author,publish_date,likes,comments,shares,keyword,rating,tags,text\n",
            )

    if task_mode in {"full", "guide"}:
        seed_text(paths["experience_root"] / "EXPERIENCE_SCRIPT.md", experience_script_template(task_card))
        seed_text(paths["experience_root"] / "EXPERIENCE_REPORT.md", experience_report_template(task_card))
        seed_text(paths["manual_root"] / "README.md", manual_root_template(task_card))

    if task_mode == "full":
        seed_text(paths["synthesis_root"] / "SUBAGENT_ROSTER.md", subagent_roster_template(task_card))
        seed_text(paths["synthesis_root"] / "REVIEW_GATE.md", review_gate_template(task_card))
        seed_text(paths["writing_root"] / "WRITING_PLAN.md", writing_plan_template(task_card))
        seed_text(paths["factcheck_root"] / "FACTCHECK_PLAN.md", factcheck_plan_template(task_card))
        seed_text(paths["factcheck_root"] / "round-1.md", factcheck_round_template(task_card, 1))
        seed_text(paths["factcheck_root"] / "round-2.md", factcheck_round_template(task_card, 2))
        seed_text(paths["factcheck_root"] / "round-3.md", factcheck_round_template(task_card, 3))
        seed_text(paths["factcheck_root"] / "final-status.md", factcheck_final_status_template(task_card))
        seed_text(paths["visuals_root"] / "VISUAL_PLAN.md", visual_plan_template(task_card))
    if task_mode == "crawl":
        seed_text(paths["synthesis_root"] / "SUBAGENT_ROSTER.md", subagent_roster_template(task_card))
        seed_text(paths["synthesis_root"] / "REVIEW_GATE.md", review_gate_template(task_card))


def seed_text(path: Path, content: str) -> None:
    if not path.exists():
        write_text(path, content)


def build_task_card_md(task_card: dict) -> str:
    return f"""# 任务卡

## 基础信息

- 任务模式：`{task_card.get('task_mode', 'full')}`
- 任务 ID：`{task_card.get('task_slug', '')}`
- 产品名：`{task_card.get('product_name', '')}`
- 产品别名：`{task_card.get('product_slug', '')}`
- 主链接：`{task_card.get('primary_url', '')}`
- 分析目标：`{task_card.get('analysis_goal', '')}`
- 核心问题：`{task_card.get('key_question', '')}`
- 产品类型：`{task_card.get('product_type', 'unknown')}`

## 任务策略

- 默认行为：`每次新建任务，不复用旧任务`
- 如需继续旧任务或引用旧证据，必须在任务卡里显式指定
- 当前任务目录：`{task_card.get('task_slug', '')}`

## 重点维度

{bullet_list(task_card.get('focus_dimensions', []))}
"""


def process_log_template(task_card: dict) -> str:
    return f"""# 过程文档

> 产品：`{task_card.get('product_name', '')}`

## 记录规则

- 每次人与 AI 的关键讨论都要补一条记录
- 每条记录要写“讨论了什么、结论是什么、还缺什么”
- 没有结论时，也要写清“暂未决”

## 记录表

| 时间 | 阶段 | 人的输入/判断 | AI 的反馈/建议 | 结论 | 后续动作 |
|---|---|---|---|---|---|
"""


def decision_log_template(task_card: dict) -> str:
    return f"""# 关键决策文档

> 产品：`{task_card.get('product_name', '')}`

| 决策点 | 选择 | 理由 | 证据/依据 | 影响章节 | 是否已确认 |
|---|---|---|---|---|---|
"""


def keyword_template(task_card: dict) -> str:
    product_name = task_card.get("product_name", "")
    return f"""# 搜索关键词与长尾词

## 核心要求

- 不只搜产品名
- 要补充别名、功能词、问题词、评价词、竞品词、长尾词
- 和用户核对后再正式启动搜索与爬取

## 关键词清单

### 核心词

- `{product_name}`

### 长尾方向

- `{product_name} 评测`
- `{product_name} 怎么样`
- `{product_name} 会员`
- `{product_name} 退款`
- `{product_name} 家长`
- `{product_name} 学生`
- `{product_name} 替代`
"""


def experience_script_template(task_card: dict) -> str:
    return f"""# 产品体验引导脚本

> 产品：`{task_card.get('product_name', '')}`

## 目标

- 引导用户先体验最关键的功能路径
- 要求用户边体验边记录截图、录屏和洞察
- 明确每一步为什么重要

## 建议顺序

1. 进入首页或入口页
2. 完成首次核心任务
3. 进入登录后主界面
4. 触达会员/付费节点
5. 查看结果页、历史页、报告页

## 每一步要记录

- 你做了什么
- 你看到了什么
- 你觉得哪里顺、哪里卡
- 有没有反直觉的设计
- 建议截图或录屏文件名
"""


def experience_report_template(task_card: dict) -> str:
    return f"""# 体验报告

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`

## 1. 当前素材状态

- 已有截图：`待补充`
- 已有录屏：`待补充`
- 已有抽帧：`待补充`
- 还缺什么：`待补充`

## 2. 产品架构判断

- 模块层级：`待补充`
- 核心功能：`待补充`
- 治理边界：`待补充`

## 3. 功能矩阵

| 功能点 | 用户价值 | 产品意义 | 当前不足 |
|---|---|---|---|
| `[待填]` | `[待填]` | `[待填]` | `[待填]` |

## 4. 重点功能路径

- 入口：`待补充`
- 关键交互：`待补充`
- 价值时刻：`待补充`
- 继续讲 / 复盘 / 认证：`待补充`

## 5. 好的洞察与不好的洞察

- 好的洞察：`待补充`
- 不好的洞察：`待补充`

## 6. 进入正文的可复用判断

- `3. 产品分析`：`待补充`
- `4. 用户分析`：`待补充`
- `7. 商业化分析`：`待补充`

## 7. 待补素材清单

- 待补充：哪些素材缺失会阻塞哪一章写作

## 8. 截图 -> 章节 -> 判断

| 截图/录屏素材 | 目标章节 | 要证明的判断 | 推荐版式 | 当前状态 |
|---|---|---|---|---|
| `screenshots/...` | `3. 产品分析` | `[待填]` | `对比板 / 路径板 / 角色板 / 节点板` | `ready / missing` |
"""


def writing_plan_template(task_card: dict) -> str:
    return f"""# 文档撰写计划

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`
> 说明：这不是“一次性出完整正文”的提纲，而是逐章推进的写作执行单。

## 一、实际输出顺序

1. 分析建模
2. 产品分析
3. 用户分析
4. 社媒分析
5. SEO 与内容分析
6. 商业化分析
7. 竞争判断
8. 对我方建议
9. 总结
10. 证据附录与索引

## 二、章节合同总表

| 章节 | 当前状态 | 本章要回答的问题 | 本章核心判断 | 本章主证据 | 必备表格 | 必备截图 / 图表 | 推荐版式 | 是否必须带角标 | 阻塞项 | 完成标准 |
|---|---|---|---|---|---|---|---|---|---|---|
| `1. 总结` | `todo` | 这份报告最后要留下哪几个最终判断？ | `[待全文完成后回填]` | `全文合稿` | `最值得学 / 最该避` | `可选` | `无` | `是` | `前 2-9 章未完成` | `四个最终判断 + 一句建议已回填` |
| `2. 分析建模` | `todo` | 这次分析为什么这样拆？ | `[待填]` | `[1](...) [2](...)` | `分析模块表` | `建模图` | `结构图` | `是` | `[待填]` | `模块、判断目标、边界已清楚` |
| `3. 产品分析` | `todo` | 产品骨架、最短路径、复盘和治理节点是什么？ | `[待填]` | `[1](...) [2](...)` | `功能矩阵 / 路径表` | `真实截图 + 结构图` | `对比板 / 路径板` | `是` | `[待填]` | `路径图板、结构图、功能矩阵齐` |
| `4. 用户分析` | `todo` | 核心用户是谁，被优先服务的是谁？ | `[待填]` | `[1](...) [2](...)` | `用户画像 / JTBD` | `用户旅程图 / 角色板` | `角色板` | `是` | `[待填]` | `用户分层、旅程、角色图齐` |
| `5. 社媒分析` | `todo` | 用户在外部世界怎么理解这个产品？ | `[待填]` | `[1](...) [2](...)` | `平台角色 / 主题矩阵` | `按需补图` | `可选` | `是` | `[待填]` | `正负主题和关键原话齐` |
| `6. SEO 与内容分析` | `todo` | 搜索和内容解释权掌握在谁手里？ | `[待填]` | `[1](...) [2](...)` | `关键词承接表` | `搜索承接图 / 搜索页截图` | `路径板 / 结构图` | `是` | `[待填]` | `承接结构和内容空位已讲清` |
| `7. 商业化分析` | `todo` | 收费边界、认证边界和转化节点是什么？ | `[待填]` | `[1](...) [2](...)` | `定价 / 权益边界表` | `价格页 / 认证页 / 节点板` | `节点板` | `是` | `[待填]` | `节点图、边界表、阶段判断齐` |
| `8. 竞争判断` | `todo` | 它真正强什么、弱什么、哪里可绕开？ | `[待填]` | `前文合稿` | `强弱矩阵` | `判断矩阵图` | `矩阵图` | `是` | `前 2-7 章未完成` | `强弱、护城河、脆弱点齐` |
| `9. 对我方建议` | `todo` | 我方接下来应该怎么做？ | `[待填]` | `前文合稿` | `P0/P1/P2 表` | `一般可选` | `无` | `是` | `前 2-8 章未完成` | `建议能逐条回指前文` |
| `10. 证据附录与索引` | `todo` | 每个关键判断能追到哪里？ | `[索引汇编，不新增结论]` | `全文与素材目录` | `来源索引表` | `图表索引` | `无` | `是` | `正文未完成` | `来源、图表、截图索引齐` |

## 三、章节推进状态表

| 章节 | 章节合同 | 正文撰写 | 配图 | 章节事实校验 | 总编合稿备注 |
|---|---|---|---|---|---|
| `2. 分析建模` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `3. 产品分析` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `4. 用户分析` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `5. 社媒分析` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `6. SEO 与内容分析` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `7. 商业化分析` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `8. 竞争判断` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `9. 对我方建议` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `1. 总结` | `todo` | `todo` | `todo` | `todo` | `[待填]` |
| `10. 证据附录与索引` | `todo` | `todo` | `todo` | `todo` | `[待填]` |

## 四、每章落文前的最小检查

- [ ] 本章问题写清了
- [ ] 本章强判断写清了
- [ ] 本章主证据补齐了
- [ ] 本章至少有一张表
- [ ] 本章该下沉的真实图已经下沉
- [ ] 图注是中文，且说明了证明点
- [ ] 段落里有角标或明确回指
- [ ] 本章没有写成采集过程汇报
"""


def subagent_roster_template(task_card: dict) -> str:
    return f"""# 搜索子代理清单

> 产品：`{task_card.get('product_name', '')}`

| 子代理 | 默认 subagent_type | 负责平台 | 默认工具 | 当前状态 | 必须产物 |
|---|---|---|---|---|---|
| 官网结构 Agent | `research-web` | 官网、产品页、公开落地页、信息架构 | `firecrawl / browser / web search` | `待执行` | `03-platforms/web/summary.md` `03-platforms/web/data.csv` |
| App Store Agent | `research-appstore` | App Store 搜索、详情、评分、评论、版本记录 | `app-insight / web search` | `待执行` | `03-platforms/appstore/summary.md` `03-platforms/appstore/data.csv` |
| 小红书 Agent | `research-social` | 小红书笔记、评论、原话、爆点标签 | `xiaohongshu MCP / web search / local crawler` | `待执行` | `03-platforms/xiaohongshu/summary.md` `03-platforms/xiaohongshu/data.csv` |
| 微博 Agent | `research-social` | 微博内容、热词、讨论串、用户抱怨 | `weibo MCP / web search / local crawler` | `待执行` | `03-platforms/weibo/summary.md` `03-platforms/weibo/data.csv` |
| B站 Agent | `research-social` | B站视频、标题、简介、评论和弹幕摘要 | `bilibili MCP / web search` | `待执行` | `03-platforms/bilibili/summary.md` `03-platforms/bilibili/data.csv` |
| 知乎 / 问答 Agent | `research-comments` | 问答站帖子、测评、长评论和链路反馈 | `firecrawl / web search` | `待执行` | `03-platforms/zhihu/summary.md` `03-platforms/zhihu/data.csv` |
| SEO 承接 Agent | `research-seo` | SERP、品牌词、问题词、内容承接结构 | `firecrawl / web search` | `待执行` | `03-platforms/seo/summary.md` `03-platforms/seo/data.csv` |
| 商业化 Agent | `research-business` | 定价、会员、试用、转化节点 | `browser / web search` | `按需执行` | `03-platforms/pricing/summary.md` `03-platforms/pricing/data.csv` |
"""


def review_gate_template(task_card: dict) -> str:
    return f"""# 审核门禁

> 产品：`{task_card.get('product_name', '')}`

## 审核规则

- 搜索子代理结束后必须先审核
- 不合格就定向打回
- 最多允许 5 轮

## 采集门禁

| 轮次 | 审核代理 | 结论 | 打回给谁 | 原因 | 是否放行 |
|---|---|---|---|---|---|
| 1 | `research-review` | `待审核` |  |  | `否` |

## 成稿门禁

- `WRITING_PLAN.md` 章节状态：`待检查`
- `FACTCHECK_PLAN.md` 章节校验：`待检查`
- `VISUAL_PLAN.md` 图证回填：`待检查`
- `07-factcheck/round-1.md`：`待检查`
- `07-factcheck/round-2.md`：`待检查`
- `07-factcheck/round-3.md`：`待检查`
- `07-factcheck/final-status.md`：`待检查`
- `04-experience/EXPERIENCE_REPORT.md`：`待检查`
- 成稿放行：`否`
"""


def factcheck_plan_template(task_card: dict) -> str:
    return f"""# 三轮事实核查计划

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`

## 执行规则

- 三轮整体验证之前，默认每章已经完成一轮章节事实校验
- 三轮都必须调用独立只读 `research-review` 子代理
- 不允许主代理手动降级代审
- 每轮都要输出独立核查文档

## 章节事实校验总表

| 章节 | 强判断校验 | 角标校验 | 图文对应 | 图片路径校验 | 中文化校验 | 是否通过 | 问题摘要 |
|---|---|---|---|---|---|---|---|
| `2. 分析建模` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `3. 产品分析` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `4. 用户分析` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `5. 社媒分析` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `6. SEO 与内容分析` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `7. 商业化分析` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `8. 竞争判断` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `9. 对我方建议` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `1. 总结` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |
| `10. 证据附录与索引` | `todo` | `todo` | `todo` | `todo` | `todo` | `no` | `[待填]` |

## 单章事实校验模板

| 检查项 | 结果 | 说明 |
|---|---|---|
| 强判断是否超证据 | `pass / fail` | `[待填]` |
| 是否有证据角标或明确回指 | `pass / fail` | `[待填]` |
| 图和正文判断是否一一对应 | `pass / fail` | `[待填]` |
| 图片是否来自当前任务目录 | `pass / fail` | `[待填]` |
| 图注是否中文 | `pass / fail` | `[待填]` |
| 是否仍有英文标签 / 坏图 / 无意义留白 | `pass / fail` | `[待填]` |

## Round 1

- 校验事实陈述和来源链接

## Round 2

- 校验每个判断是否有证据支撑

## Round 3

- 校验证据附录、索引和正文引用是否一致
- 校验主报告路径是否位于当前任务目录内
- 校验图片路径、图号、中文图注和图文绑定是否一致
"""


def factcheck_round_template(task_card: dict, round_number: int) -> str:
    return f"""# Round {round_number} 核查记录

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`

- 本轮核查代理：`research-review`
- 本轮核查范围：`待补充`
- 发现的问题：`待补充`
- 已修正 / 待修正：`待补充`
- 是否允许进入下一轮：`否`
"""


def factcheck_final_status_template(task_card: dict) -> str:
    return f"""# 成稿终审状态

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`

- 三轮核查是否完成：`否`
- 图证覆盖是否完成：`否`
- 章节事实校验是否完成：`否`
- 成稿放行：`否`
- 终审备注：`待补充`
"""


def visual_plan_template(task_card: dict) -> str:
    return f"""# 可视化规划

> 产品：`{task_card.get('product_name', '')}`
> 任务：`{task_card.get('task_slug', '')}`

## 原则

- 有真实产品图时，先用真实产品图
- 真实图不够解释结构时，再补结构图
- 每张图都要有中文图注
- 每张图都要能回答“这张图证明什么”

## 章节配图总表

| 章节 | 判断点 | 是否必须有真实图 | 可用素材路径 | 应补图类型 | 推荐版式 | 图号 | 图注草案 | 插入位置 | 当前状态 |
|---|---|---|---|---|---|---|---|---|---|
| `3. 产品分析` | `双端口入口承接差异` | `是` | `04-experience/screenshots/...` | `真实截图` | `对比板` | `图 3-1 ~ 3-4` | `[待填]` | `3.1 后` | `todo` |
| `3. 产品分析` | `首次价值路径` | `是` | `04-experience/frames/...` | `真实截图` | `路径板` | `图 3-x` | `[待填]` | `3.2 后` | `todo` |
| `4. 用户分析` | `不同角色被不同界面承接` | `视情况` | `04-experience/screenshots/...` | `真实截图 + 结构图` | `角色板` | `图 4-x` | `[待填]` | `4.2 后` | `todo` |
| `6. SEO 与内容分析` | `搜索承接格局` | `优先` | `03-platforms/seo/...` | `搜索页截图 / 结构图` | `路径板 / 结构图` | `图 6-x` | `[待填]` | `6.1 或 6.2 后` | `todo` |
| `7. 商业化分析` | `认证或解锁边界` | `是` | `04-experience/screenshots/...` | `真实截图` | `节点板` | `图 7-x` | `[待填]` | `7.1 或 7.2 后` | `todo` |
| `8. 竞争判断` | `强弱与窗口` | `否` | `08-visuals/svg/...` | `结构图` | `矩阵图` | `图 8-x` | `[待填]` | `8.1 后` | `todo` |

## 单章配图执行表

| 图片路径 | 图片类型 | 证明的判断 | 是否真实产品图 | 图注是否中文 | 是否已插入正文 | 备注 |
|---|---|---|---|---|---|---|
| `04-experience/screenshots/example.png` | `截图 / 抽帧 / SVG` | `[待填]` | `是 / 否` | `是 / 否` | `是 / 否` | `[待填]` |
"""


def imports_root_template(task_card: dict) -> str:
    return f"""# imports 目录说明

> 产品：`{task_card.get('product_name', '')}`

请把平台原始资料放到对应目录：

- `web/`
- `reviews/`
- `social/`
- `seo/`
- `pricing/`

支持的常见文件：

- `.json`
- `.jsonl`
- `.md`
- `.txt`

说明：

- `collect` 只会读取这些本地导入目录，不会替你自动联网抓取
- 如果本轮没有导入任何平台资料，后续 `validate` 应视为未达采集门禁
"""


def manual_root_template(task_card: dict) -> str:
    return f"""# manual 目录说明

> 产品：`{task_card.get('product_name', '')}`

这里放人工补充素材：

- `uploads/`
- `screenshots/`
- `frames/`
- `notes/`

这些内容主要服务：

- `04-experience/EXPERIENCE_REPORT.md`
- `06-writing/WRITING_PLAN.md`
- `08-visuals/VISUAL_PLAN.md`
"""


def platform_summary_template(platform: str) -> str:
    target = PLATFORM_SAMPLE_TARGETS.get(platform, 200)
    return f"""# {platform} 平台分析总结

## 1. 本轮任务概况

- 平台：`{platform}`
- 当前状态：`待采集`
- 推荐工具：`{"；".join(PLATFORM_BACKEND_PRIORITY.get(platform, [])) or "待补充"}`
- 本轮抓取目标：`待补充`
- 实际使用工具：`待补充`
- 是否做过安装 / 初始化 / 登录：`待补充`
- 是否发生降级：`待补充`
- 目标数量：至少 `{target}` 条/篇
- 当前样本量：`待补充`
- 阈值判断：`待补充`

## 2. 样本与证据面

- 本轮抓取范围：`待补充`
- 代表性样本：`待补充`
- 当前证据边界：`待补充`

## 3. 关键事实信号

- 当前明显信号：

## 4. 平台洞察与启发

- 基于本平台证据的初步洞察：
- 候选判断：
- 对后续分析最有帮助的启发：

## 5. 风险、噪音与缺口

- 当前噪音与风险：
- 还缺什么：
- 建议补抓方向：

## 6. 需要用户确认 / 补充

- 是否接受当前样本量：
- 是否有误读需要纠正：
- 是否需要补充私有信息 / 登录后页面 / 录屏截图：
- 是否需要优先深挖某类用户 / 某个问题：

## 边界提醒

- 可以写：基于本平台证据提炼出的平台洞察、候选判断、策划启发
- 不要写：替代全局正式报告的最终结论、跨章节总判断、最终 `跟 / 避 / 绕 / 观察`
"""


def bullet_list(values: list[str]) -> str:
    if not values:
        return "- 待补充"
    return "\n".join(f"- `{value}`" for value in values)
