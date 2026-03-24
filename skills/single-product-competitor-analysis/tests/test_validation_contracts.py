import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from spca.validators import validate_pipeline_outputs  # noqa: E402


class ValidationContractsTest(unittest.TestCase):
    def test_validate_rejects_empty_full_task_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = {
                "task_card": root / "task-card.json",
                "exports_root": root / "exports",
                "report_path": root / "06-writing" / "demo.md",
                "raw_root": root / "raw",
                "platforms_root": root / "03-platforms",
                "normalized_root": root / "normalized",
            }
            for path in [paths["exports_root"], paths["report_path"].parent, paths["raw_root"], paths["platforms_root"]]:
                path.mkdir(parents=True, exist_ok=True)

            paths["task_card"].write_text(
                json.dumps(
                    {
                        "task_mode": "full",
                        "product_name": "Demo Product",
                        "product_slug": "demo-product",
                        "analysis_goal": "验证 validator 会拦截空采集任务"
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (paths["exports_root"] / "report-context.json").write_text(
                json.dumps(
                    {
                        "task": {"mode": "full", "slug": "demo-task"},
                        "product": {
                            "name": "Demo Product",
                            "slug": "demo-product",
                            "analysis_goal": "验证 validator 会拦截空采集任务"
                        },
                        "counts": {"sources": 0, "evidence": 0, "review_samples": 0},
                        "analysis": {
                            "product_overview": {},
                            "user_analysis": {},
                            "social_sentiment": {},
                            "seo_content": {},
                            "monetization": {},
                            "competition": {}
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (paths["raw_root"] / "source-records.jsonl").write_text("", encoding="utf-8")
            paths["report_path"].write_text(
                "\n".join(
                    [
                        "# Demo",
                        "## 1. 总结",
                        "## 2. 分析建模",
                        "## 3. 产品分析",
                        "## 4. 用户分析",
                        "## 5. 社媒分析",
                        "## 6. SEO 与内容分析",
                        "## 7. 商业化分析",
                        "## 8. 竞争判断",
                        "## 9. 对我方建议",
                        "## 10. 证据附录",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = validate_pipeline_outputs(paths, SKILL_ROOT / "schemas")
            self.assertIn("source-records.jsonl 为空", result["errors"])


if __name__ == "__main__":
    unittest.main()
