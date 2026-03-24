from pathlib import Path

from spca.collectors.common import collect_directory


def collect_web(product_slug: str, imports_root: Path):
    return collect_directory(product_slug, "web", imports_root / "web")
