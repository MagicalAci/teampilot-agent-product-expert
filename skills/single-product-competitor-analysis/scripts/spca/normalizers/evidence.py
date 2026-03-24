from collections import Counter

from spca.config import CHANNEL_DEFAULTS
from spca.utils import excerpt_text, summarize_text

POSITIVE_TERMS = ["好用", "喜欢", "方便", "清晰", "省时", "值得", "满意", "有效"]
NEGATIVE_TERMS = ["麻烦", "贵", "卡顿", "问题", "不准", "复杂", "退款", "广告"]


def _pool_for_channel(channel: str, title: str) -> str:
    lowered = title.lower()
    if channel == "web" and any(word in lowered for word in ["feature", "功能", "结构"]):
        return "feature_structure"
    return CHANNEL_DEFAULTS[channel]["pool"]


def _platform_for_channel(channel: str, metadata: dict) -> str:
    return metadata.get("platform") or CHANNEL_DEFAULTS[channel]["platform"]


def _sentiment_label(text: str) -> str:
    positive_hits = sum(1 for term in POSITIVE_TERMS if term in text)
    negative_hits = sum(1 for term in NEGATIVE_TERMS if term in text)
    if positive_hits > negative_hits:
        return "positive"
    if negative_hits > positive_hits:
        return "negative"
    return "neutral"


def _evidence_record(source: dict, index: int, title: str, text: str, metadata: dict) -> dict:
    channel = source["channel"]
    return {
        "evidence_id": f"{source['source_id']}-e{index}",
        "product_slug": source["product_slug"],
        "source_id": source["source_id"],
        "channel": channel,
        "evidence_pool": _pool_for_channel(channel, title),
        "tier": source["source_tier"],
        "title": title,
        "uri": metadata.get("url") or metadata.get("uri") or source.get("uri"),
        "local_path": source["local_path"],
        "platform": _platform_for_channel(channel, metadata),
        "page_stage": metadata.get("page_stage") or "unknown",
        "summary": summarize_text(text),
        "excerpt": excerpt_text(text),
        "tags": metadata.get("tags", []),
        "metadata": metadata,
    }


def normalize_sources(source_records: list[dict]) -> tuple[list[dict], list[dict]]:
    evidence_records = []
    review_samples = []

    for source in source_records:
        if source["payload_kind"] == "text":
            evidence_records.append(
                _evidence_record(source, 1, source["title"], source.get("body") or "", source["metadata"])
            )
            continue

        items = source.get("items", [])
        if not items:
            evidence_records.append(
                _evidence_record(source, 1, source["title"], "", source["metadata"])
            )
            continue

        for index, item in enumerate(items, start=1):
            title = item.get("title") or item.get("name") or source["title"]
            text = item.get("text") or item.get("body") or item.get("content") or json_fallback(item)
            metadata = {
                **source["metadata"],
                **{k: v for k, v in item.items() if k not in {"text", "body", "content"}},
            }
            evidence = _evidence_record(source, index, title, text, metadata)
            evidence_records.append(evidence)

            if source["channel"] in {"reviews", "social", "manual"} and text:
                review_samples.append(
                    {
                        "sample_id": f"{source['source_id']}-s{index}",
                        "product_slug": source["product_slug"],
                        "source_id": source["source_id"],
                        "evidence_id": evidence["evidence_id"],
                        "platform": evidence["platform"],
                        "author": item.get("author"),
                        "rating": item.get("rating"),
                        "text": text,
                        "sentiment_label": _sentiment_label(text),
                        "tags": item.get("tags", []),
                        "metadata": metadata,
                    }
                )

    return evidence_records, review_samples


def json_fallback(item: dict) -> str:
    prioritized = []
    for key in ["summary", "description", "comment", "quote"]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            prioritized.append(value.strip())
    if prioritized:
        return " ".join(prioritized)
    return " ".join(str(value).strip() for value in item.values() if str(value).strip())


def build_gap_list(evidence_records: list[dict], review_samples: list[dict]) -> list[str]:
    pools = Counter(record["evidence_pool"] for record in evidence_records)
    gaps = []
    required = {
        "official_pages": "缺官网与产品页证据",
        "pricing_monetization": "缺定价与商业化证据",
        "reviews_feedback": "缺评论与用户反馈证据",
        "social_sentiment": "缺社媒证据",
        "seo_content": "缺 SEO 与内容证据",
    }
    for pool, message in required.items():
        if pools[pool] == 0:
            gaps.append(message)
    if len(review_samples) < 5:
        gaps.append("评论样本不足，建议补充应用商店评论、社媒原话或访谈摘要")
    if pools["screenshots_recordings"] == 0:
        gaps.append("缺截图或录屏补料，登录后页面与深层路径判断可信度有限")
    return gaps
