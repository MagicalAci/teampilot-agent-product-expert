from collections import Counter, defaultdict

SEGMENT_RULES = {
    "家长": ["家长", "孩子", "娃", "作业", "陪学"],
    "学生": ["学生", "背单词", "做题", "刷题", "考试"],
    "老师": ["老师", "教学", "备课", "课堂"],
    "职场用户": ["效率", "会议", "协作", "团队", "工作"],
}


def analyze_user(review_samples: list[dict], evidence_records: list[dict]) -> dict:
    segment_hits = Counter()
    segment_quotes = defaultdict(list)

    for sample in review_samples:
        text = sample["text"]
        matched = False
        for segment, keywords in SEGMENT_RULES.items():
            if any(keyword in text for keyword in keywords):
                segment_hits[segment] += 1
                if len(segment_quotes[segment]) < 2:
                    segment_quotes[segment].append(text)
                matched = True
        if not matched:
            segment_hits["泛用户"] += 1
            if len(segment_quotes["泛用户"]) < 2:
                segment_quotes["泛用户"].append(text)

    top_segments = [
        {
            "segment": segment,
            "count": count,
            "quotes": segment_quotes[segment],
            "candidate_jtbd": infer_jtbd(segment),
        }
        for segment, count in segment_hits.most_common(4)
    ]

    feature_titles = [record["title"] for record in evidence_records if record["channel"] == "web"][:4]
    return {
        "segment_count": len(segment_hits),
        "top_segments_by_signal": top_segments,
        "decision_path_signal_titles": feature_titles,
        "candidate_questions": build_user_questions(top_segments),
    }


def infer_jtbd(segment: str) -> str:
    mapping = {
        "家长": "希望快速判断学习效果，并减少陪伴或监督成本",
        "学生": "希望更快完成任务、拿到反馈并提升结果",
        "老师": "希望提升教学效率与内容组织效率",
        "职场用户": "希望在固定流程中降低协作和沟通摩擦",
        "泛用户": "希望快速获得明确结果并降低试错成本",
    }
    return mapping.get(segment, mapping["泛用户"])


def build_user_questions(top_segments: list[dict]) -> list[str]:
    if not top_segments:
        return [
            "当前评论样本里没有明显的人群信号，是否需要补更多一手用户反馈？",
            "是否存在登录后或付费后才会暴露的高价值用户路径？",
        ]

    lead = top_segments[0]["segment"]
    tail = top_segments[-1]["segment"]
    return [
        f"当前高频人群信号偏向 `{lead}`，这是否真的代表核心用户？",
        f"`{tail}` 的信号较弱，这是样本偏差还是确实被服务不足？",
        "是否还需要引入访谈、客服记录或群聊记录来校正分层？",
    ]
