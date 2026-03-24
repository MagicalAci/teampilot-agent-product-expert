def analyze_competition(user_analysis: dict, sentiment_analysis: dict, seo_analysis: dict, monetization_analysis: dict) -> dict:
    focus_points = []

    top_segments = user_analysis.get("top_segments_by_signal", [])
    if top_segments:
        focus_points.append(f"当前用户信号最高的人群：{top_segments[0]['segment']}")

    positive_signals = sentiment_analysis.get("positive_theme_signals", [])
    if positive_signals:
        focus_points.append(f"当前正向主题信号：{positive_signals[0]['theme']}")

    negative_signals = sentiment_analysis.get("negative_theme_signals", [])
    if negative_signals:
        focus_points.append(f"当前负向主题信号：{negative_signals[0]['theme']}")

    if seo_analysis.get("seo_records_count", 0) > 0:
        focus_points.append("已采回 SEO 与内容样本，可继续核对它是否承担获客职责")

    if monetization_analysis.get("value_gate_signals"):
        focus_points.extend(monetization_analysis["value_gate_signals"][:2])

    return {
        "candidate_focus_points": focus_points[:6],
        "user_questions": [
            "哪些信号可以上升成竞争优势，哪些还只是待验证现象？",
            "哪些风险来自真实产品体验，哪些只是公开评论噪音？",
            "在给出跟/避/绕/观察之前，还缺哪类证据？",
        ],
    }
