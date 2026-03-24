from pathlib import Path

from spca.collectors.common import collect_directory


def collect_pricing(product_slug: str, imports_root: Path):
    return collect_directory(product_slug, "pricing", imports_root / "pricing")
