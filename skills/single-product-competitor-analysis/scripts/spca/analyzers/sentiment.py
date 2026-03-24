from collections import Counter, defaultdict

THEME_RULES = {
    "AI准确性": ["不准", "识别", "误判", "答错", "准确"],
    "价格与会员": ["贵", "会员", "订阅", "付费", "价格"],
    "体验流畅度": ["卡", "闪退", "加载", "复杂", "麻烦"],
    "内容与题库": ["内容", "题库", "讲解", "资料", "课程"],
    "结果反馈": ["反馈", "报告", "成长", "效果", "提升"],
}


def analyze_sentiment(review_samples: list[dict]) -> dict:
    sentiment_counter = Counter(sample["sentiment_label"] for sample in review_samples)
    positive_themes = Counter()
    negative_themes = Counter()
    sample_quotes = defaultdict(list)

    for sample in review_samples:
        text = sample["text"]
        matched_theme = "其他"
        for theme, keywords in THEME_RULES.items():
            if any(keyword in text for keyword in keywords):
                matched_theme = theme
                break

        if sample["sentiment_label"] == "positive":
            positive_themes[matched_theme] += 1
        elif sample["sentiment_label"] == "negative":
            negative_themes[matched_theme] += 1

        if len(sample_quotes[matched_theme]) < 2:
            sample_quotes[matched_theme].append(text)

    return {
        "counts": dict(sentiment_counter),
        "positive_theme_signals": build_theme_rows(positive_themes, sample_quotes),
        "negative_theme_signals": build_theme_rows(negative_themes, sample_quotes),
        "dominant_sentiment_signal": sentiment_counter.most_common(1)[0][0] if sentiment_counter else "neutral",
        "candidate_questions": build_sentiment_questions(positive_themes, negative_themes),
    }


def build_theme_rows(counter: Counter, sample_quotes: dict) -> list[dict]:
    rows = []
    for theme, count in counter.most_common(5):
        rows.append(
            {
                "theme": theme,
                "count": count,
                "quotes": sample_quotes[theme],
            }
        )
    return rows


def build_sentiment_questions(positive_themes: Counter, negative_themes: Counter) -> list[str]:
    positive_top = positive_themes.most_common(1)
    negative_top = negative_themes.most_common(1)
    questions = []
    if positive_top:
        questions.append(f"正向信号目前集中在 `{positive_top[0][0]}`，这是真优势还是短期传播点？")
    if negative_top:
        questions.append(f"负向信号目前集中在 `{negative_top[0][0]}`，它是高频问题还是高严重度问题？")
    questions.append("当前社媒样本是否已经覆盖到目标用户，而不只是高活跃发声用户？")
    return questions
