from spca.analyzers.competition import analyze_competition
from spca.analyzers.monetization import analyze_monetization
from spca.analyzers.seo import analyze_seo
from spca.analyzers.sentiment import analyze_sentiment
from spca.analyzers.user import analyze_user


def analyze_product_overview(evidence_records: list[dict]) -> dict:
    official = [record for record in evidence_records if record["evidence_pool"] == "official_pages"]
    features = [record for record in evidence_records if record["evidence_pool"] == "feature_structure"]
    pricing = [record for record in evidence_records if record["evidence_pool"] == "pricing_monetization"]
    top_titles = [record["title"] for record in (official + features)[:5]]
    return {
        "official_pages_count": len(official),
        "feature_records_count": len(features),
        "pricing_records_count": len(pricing),
        "top_titles": top_titles,
        "candidate_questions": [
            "哪个模块最像核心价值入口？",
            "关键转化节点是否埋在公开页面还是登录后页面？",
            "哪些标题只是营销包装，哪些真正对应产品骨架？",
        ],
        "signal_summary": "已提取官网、功能页和定价页的基础结构信号，适合继续和用户一起确认产品骨架。",
    }
