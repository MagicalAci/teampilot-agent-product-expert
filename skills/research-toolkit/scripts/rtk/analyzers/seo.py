from collections import Counter


def analyze_seo(evidence_records: list[dict]) -> dict:
    seo_records = [record for record in evidence_records if record["channel"] == "seo"]
    titles = [record["title"] for record in seo_records]
    intents = Counter()

    for title in titles:
        lowered = title.lower()
        if any(word in lowered for word in ["how", "怎么", "指南", "教程"]):
            intents["问题意图"] += 1
        elif any(word in lowered for word in ["best", "top", "对比", "比较"]):
            intents["比较意图"] += 1
        else:
            intents["品牌/产品意图"] += 1

    return {
        "seo_records_count": len(seo_records),
        "top_titles": titles[:5],
        "intent_breakdown": dict(intents),
        "candidate_questions": build_seo_questions(intents, titles),
        "signal_summary": "已提取内容标题和关键词意图分布，可继续和用户一起判断 SEO 角色。",
    }


def build_seo_questions(intents: Counter, titles: list[str]) -> list[str]:
    questions = []
    if intents:
        lead_intent = intents.most_common(1)[0][0]
        questions.append(f"当前标题信号偏向 `{lead_intent}`，这是否符合该产品的获客策略？")
    if not titles:
        questions.append("当前几乎没有 SEO 样本，是否需要补博客、落地页或 SERP 截图？")
    else:
        questions.append("这些标题是品牌承接、问题承接，还是对比拦截？")
    questions.append("内容页与产品转化页之间是否已经形成明确连接？")
    return questions
