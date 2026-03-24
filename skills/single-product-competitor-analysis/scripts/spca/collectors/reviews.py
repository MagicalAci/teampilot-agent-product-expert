from pathlib import Path

from spca.collectors.common import collect_directory


def collect_reviews(product_slug: str, imports_root: Path):
    return collect_directory(product_slug, "reviews", imports_root / "reviews")
