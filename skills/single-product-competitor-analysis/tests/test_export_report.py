import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from spca.exporters import build_report_markdown  # noqa: E402


class ExportReportTest(unittest.TestCase):
    def test_report_contains_required_sections(self):
        context = {
            "generated_at": "2026-03-09T00:00:00+00:00",
            "task": {"mode": "full", "slug": "demo-study-app"},
            "product": {
                "name": "Demo Study App",
                "slug": "demo-study-app",
                "primary_url": "https://example.com",
                "analysis_goal": "验证结构化导出",
                "focus_dimensions": ["product", "user", "social"],
            },
            "counts": {"sources": 6, "evidence": 8, "review_samples": 5},
            "gaps": ["缺截图或录屏补料，登录后页面与深层路径判断可信度有限"],
            "analysis": {
                "product_overview": {
                    "official_pages_count": 2,
                    "feature_records_count": 1,
                    "pricing_records_count": 1,
                    "top_titles": ["首页", "功能页"],
                    "candidate_questions": ["哪个模块最像核心价值入口？"],
                    "signal_summary": "已建立产品公开结构底座。",
                },
                "user_analysis": {
                    "segment_count": 2,
                    "top_segments_by_signal": [
                        {"segment": "家长", "candidate_jtbd": "希望快速判断学习效果，并减少陪伴或监督成本", "count": 3}
                    ],
                    "decision_path_signal_titles": ["首页"],
                    "candidate_questions": ["当前高频人群信号偏向 `家长`，这是否真的代表核心用户？"],
                },
                "social_sentiment": {
                    "counts": {"positive": 3, "negative": 1},
                    "positive_theme_signals": [{"theme": "结果反馈"}],
                    "negative_theme_signals": [{"theme": "价格与会员"}],
                    "dominant_sentiment_signal": "positive",
                    "candidate_questions": ["正向信号目前集中在 `结果反馈`，这是真优势还是短期传播点？"],
                },
                "seo_content": {
                    "seo_records_count": 1,
                    "top_titles": ["如何提高作业订正效率"],
                    "intent_breakdown": {"问题意图": 1},
                    "candidate_questions": ["这些标题是品牌承接、问题承接，还是对比拦截？"],
                    "signal_summary": "已提取内容承接与关键词意图。",
                },
                "monetization": {
                    "pricing_records_count": 1,
                    "price_points": ["39"],
                    "value_gate_signals": ["出现试用相关信号"],
                    "candidate_questions": ["当前页面里能否看出免费版与付费版的边界？"],
                    "signal_summary": "已提取价格点和付费触发相关文本信号。",
                },
                "competition": {
                    "candidate_focus_points": ["当前用户信号最高的人群：家长"],
                    "user_questions": ["哪些信号可以上升成竞争优势，哪些还只是待验证现象？"],
                },
            },
        }
        report = build_report_markdown(context, [], [{"platform": "appstore", "text": "很好用"}])
        for heading in [
            "## 1. 总结",
            "## 2. 分析建模",
            "## 10. 证据附录",
        ]:
            self.assertIn(heading, report)
        self.assertIn("待回填", report)


if __name__ == "__main__":
    unittest.main()
