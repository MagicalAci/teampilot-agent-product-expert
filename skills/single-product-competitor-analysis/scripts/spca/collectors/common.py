import json
from pathlib import Path

from spca.config import CHANNEL_DEFAULTS
from spca.utils import now_iso


def _load_payload(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return "json_array", None, payload, {}
        if isinstance(payload, dict):
            return "json_object", None, payload.get("items", []), payload
    if suffix == ".jsonl":
        items = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
        return "jsonl", None, items, {}
    body = path.read_text(encoding="utf-8")
    return "text", body, [], {}


def collect_directory(product_slug: str, channel: str, directory: Path):
    defaults = CHANNEL_DEFAULTS[channel]
    records = []
    if not directory.exists():
        return records

    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        payload_kind, body, items, metadata = _load_payload(path)
        source_id = f"{channel}-{path.stem}-{len(records) + 1}"
        title = metadata.get("title") or path.stem.replace("-", " ").replace("_", " ")
        uri = metadata.get("url") or metadata.get("uri")
        content_type = metadata.get("content_type") or path.suffix.lower().lstrip(".") or "text"
        records.append(
            {
                "source_id": source_id,
                "product_slug": product_slug,
                "channel": channel,
                "source_tier": defaults["tier"],
                "title": title,
                "uri": uri,
                "local_path": str(path),
                "content_type": content_type,
                "collected_at": now_iso(),
                "payload_kind": payload_kind,
                "body": body,
                "items": items,
                "metadata": metadata,
            }
        )
    return records
