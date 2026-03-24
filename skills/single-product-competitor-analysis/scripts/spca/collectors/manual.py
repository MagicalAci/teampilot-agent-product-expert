from pathlib import Path

from spca.collectors.common import collect_directory


def collect_manual(product_slug: str, manual_root: Path):
    return collect_directory(product_slug, "manual", manual_root)
