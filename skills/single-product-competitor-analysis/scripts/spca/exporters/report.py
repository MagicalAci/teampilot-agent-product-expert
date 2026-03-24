from spca.utils import now_iso


def build_report_context(task_card: dict, paths: dict, evidence_records: list[dict], review_samples: list[dict], analysis: dict, gaps: list[str]) -> dict:
    return {
        "generated_at": now_iso(),
        "task": {
            "mode": task_card.get("task_mode", "full"),
            "slug": task_card.get("task_slug", task_card["product_slug"]),
        },
        "product": {
            "name": task_card["product_name"],
            "slug": task_card["product_slug"],
            "primary_url": task_card.get("primary_url", ""),
            "analysis_goal": task_card.get("analysis_goal", ""),
            "focus_dimensions": task_card.get("focus_dimensions", []),
        },
        "counts": {
            "sources": analysis["source_count"],
            "evidence": len(evidence_records),
            "review_samples": len(review_samples),
        },
        "gaps": gaps,
        "analysis": {
            "product_overview": analysis["product_overview"],
            "user_analysis": analysis["user_analysis"],
            "social_sentiment": analysis["social_sentiment"],
            "seo_content": analysis["seo_content"],
            "monetization": analysis["monetization"],
            "competition": analysis["competition"],
        },
        "paths": {
            "output_root": str(paths["output_root"]),
            "report_path": str(paths["report_path"]),
        },
    }


def build_report_markdown(context: dict, evidence_records: list[dict], review_samples: list[dict]) -> str:
    product = context["product"]
    analysis = context["analysis"]
    product_overview = analysis["product_overview"]
    user_analysis = analysis["user_analysis"]
    sentiment = analysis["social_sentiment"]
    seo = analysis["seo_content"]
    monetization = analysis["monetization"]
    competition = analysis["competition"]

    return f"""# 【{product['name']}】竞品分析文档

| 项目 | 内容 |
|---|---|
| 分析对象 | `{product['name']}` |
| 分析目标 | `{product.get('analysis_goal') or '待补充'}` |
| 文档价值 | `帮助团队把采集结果转成可共创、可追溯、可决策的竞品分析文档。` |
| 分析日期 | `{context['generated_at']}` |
| 更新记录 | `v1.0 章节骨架 / {context['generated_at']}` |

## 1. 总结

> 本章必须在全部章节完成并经用户确认后回填。

- 待回填：一句话结论
- 待回填：为什么值得研究
- 待回填：对我方最重要的启发
- 待回填：优势与不足

## 2. 分析建模

| 分析模块 | 为什么分析 | 希望得到的结论 | 当前证据状态 |
|---|---|---|---|
| 产品分析 | 看清产品骨架、核心路径和转化节点。 | 待确认产品真正的价值入口。 | 官方页 `{product_overview['official_pages_count']}` 条 / 功能结构 `{product_overview['feature_records_count']}` 条 |
| 用户分析 | 看清谁是核心用户、谁被优先服务、谁被忽略。 | 待确认高价值人群与分层方式。 | 评论样本 `{context['counts']['review_samples']}` 条 / 人群信号 `{user_analysis['segment_count']}` 组 |
| 社媒分析 | 看清外部世界如何理解和传播这个产品。 | 待确认传播点、槽点和情绪分布。 | 情绪分布 `{format_dict(sentiment.get('counts', {}))}` |
| SEO 与内容分析 | 看清搜索和内容是否在承担获客职责。 | 待确认内容承接结构和关键词角色。 | SEO 样本 `{seo['seo_records_count']}` 条 |
| 商业化分析 | 看清怎么收费、在哪里触发付费。 | 待确认价值兑现时机与拦截点。 | 定价样本 `{monetization['pricing_records_count']}` 条 |
| 竞争判断 | 把前面章节压缩成决策问题。 | 待确认哪些现象可以上升成真正判断。 | 待结合全部章节共创 |

## 3. 产品分析

### 当前证据信号

- 官方与产品页证据数：`{product_overview['official_pages_count']}`
- 功能结构证据数：`{product_overview['feature_records_count']}`
- 标题样本：{join_or_default(product_overview['top_titles'])}

### AI 待追问

{format_bullets(product_overview.get('candidate_questions', []))}

### 写作占位

- 待回填：产品定位
- 待回填：核心场景
- 待回填：一级模块
- 待回填：核心路径
- 待回填：转化节点

## 4. 用户分析

### 当前证据信号

- 人群信号组数：`{user_analysis['segment_count']}`
- 人群排序：{format_segments(user_analysis.get('top_segments_by_signal', []))}
- 可能的决策路径线索：{join_or_default(user_analysis.get('decision_path_signal_titles', []))}

### AI 待追问

{format_bullets(user_analysis.get('candidate_questions', []))}

### 写作占位

- 待回填：用户类型总览
- 待回填：核心用户类型
- 待回填：JTBD 与行为路径
- 待回填：关键人物画像

## 5. 社媒分析

### 当前证据信号

- 情绪分布：`{format_dict(sentiment.get('counts', {}))}`
- 正向主题信号：{join_or_default([row['theme'] for row in sentiment.get('positive_theme_signals', [])])}
- 负向主题信号：{join_or_default([row['theme'] for row in sentiment.get('negative_theme_signals', [])])}
- 代表性原话：
{format_quotes(review_samples)}

### AI 待追问

{format_bullets(sentiment.get('candidate_questions', []))}

### 写作占位

- 待回填：主流传播认知
- 待回填：高频正向主题
- 待回填：高频负向主题
- 待回填：风险与机会

## 6. SEO 与内容分析

### 当前证据信号

- SEO 记录数：`{seo['seo_records_count']}`
- 标题样本：{join_or_default(seo.get('top_titles', []))}
- 意图分布：`{format_dict(seo.get('intent_breakdown', {}))}`

### AI 待追问

{format_bullets(seo.get('candidate_questions', []))}

### 写作占位

- 待回填：内容结构
- 待回填：关键词意图
- 待回填：承接页与转化连接

## 7. 商业化分析

### 当前证据信号

- 定价样本数：`{monetization['pricing_records_count']}`
- 已识别价格点：{join_or_default(monetization.get('price_points', []))}
- 付费触发信号：{join_or_default(monetization.get('value_gate_signals', []))}

### AI 待追问

{format_bullets(monetization.get('candidate_questions', []))}

### 写作占位

- 待回填：套餐结构
- 待回填：权益边界
- 待回填：付费触发点
- 待回填：转化时机

## 8. 竞争判断

### 当前待核对焦点

{format_bullets(competition.get('candidate_focus_points', []))}

### AI 待追问

{format_bullets(competition.get('user_questions', []))}

### 写作占位

- 待回填：真正强项
- 待回填：真正短板
- 待回填：护城河与脆弱点
- 待回填：跟 / 避 / 绕 / 观察

## 9. 对我方建议

> 本章必须建立在前面所有章节已确认的基础上回填。

- 待回填：用户策略建议
- 待回填：产品策略建议
- 待回填：增长策略建议
- 待回填：商业化策略建议
- 待回填：未来 30 天验证动作

## 10. 证据附录

- 证据条数：`{context['counts']['evidence']}`
- 评论样本数：`{context['counts']['review_samples']}`
- 当前缺口：{join_or_default(context.get('gaps', []))}
- 样例证据标题：{join_or_default([record['title'] for record in evidence_records[:8]])}
"""


def join_or_default(values: list[str]) -> str:
    filtered = [value for value in values if value]
    return "；".join(filtered) if filtered else "待补充"


def format_bullets(values: list[str]) -> str:
    if not values:
        return "- 待补充"
    return "\n".join(f"- {value}" for value in values)


def format_dict(values: dict) -> str:
    if not values:
        return "待补充"
    return "；".join(f"{key}: {value}" for key, value in values.items())


def format_segments(segments: list[dict]) -> str:
    if not segments:
        return "待补充"
    return "；".join(f"{segment['segment']}({segment['count']})" for segment in segments)


def format_quotes(review_samples: list[dict]) -> str:
    if not review_samples:
        return "- 待补充"
    top = review_samples[:4]
    return "\n".join(f"- `{sample['platform']}`：{sample['text'][:80]}" for sample in top)
