import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from spca.collectors import COLLECTOR_MAP  # noqa: E402
from spca.normalizers import build_gap_list, normalize_sources  # noqa: E402


class NormalizeEvidenceTest(unittest.TestCase):
    def test_normalize_sources_creates_evidence_and_reviews(self):
        fixture_root = SKILL_ROOT / "fixtures" / "demo-product"
        imports_root = fixture_root / "imports"
        manual_root = fixture_root / "manual"
        product_slug = "demo-study-app"

        raw_records = []
        for channel, collector in COLLECTOR_MAP.items():
            root = manual_root if channel == "manual" else imports_root
            raw_records.extend(collector(product_slug, root))

        evidence_records, review_samples = normalize_sources(raw_records)
        gaps = build_gap_list(evidence_records, review_samples)

        self.assertGreaterEqual(len(raw_records), 6)
        self.assertGreaterEqual(len(evidence_records), 6)
        self.assertGreaterEqual(len(review_samples), 5)
        self.assertTrue(any(record["evidence_pool"] == "pricing_monetization" for record in evidence_records))
        self.assertTrue(any(sample["sentiment_label"] == "negative" for sample in review_samples))
        self.assertIsInstance(gaps, list)


if __name__ == "__main__":
    unittest.main()
