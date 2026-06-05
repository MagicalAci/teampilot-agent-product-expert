#!/usr/bin/env python3
"""轻量混合检索索引（纯标准库 BM25 + RRF，密集层可选）。

落地 policies/advanced-retrieval-p2.md §1 的"嵌入式混合索引"零依赖入口：
- 对 03-normalized 证据 / 任意 {id,text} 语料建 BM25 词面索引并检索 top-k；
- 中文友好分词（ASCII 词 + CJK 单字 + CJK 双字 gram）；
- 密集层可选：设 EMBED_ENDPOINT（OpenAI 兼容 /embeddings）时叠加 dense + RRF 融合，
  未配置或不可用则降级为纯 BM25（不报错）。

设计取舍：零第三方依赖、可被 tests/ 直接 import 调用；网络仅在显式配置 EMBED_ENDPOINT 时使用。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter
from pathlib import Path

_ASCII = re.compile(r"[a-z0-9]+")
_CJK = re.compile(r"[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    """中英混合分词：ASCII 词 + CJK 单字 + CJK 相邻双字 gram。"""
    if not text:
        return []
    low = text.lower()
    tokens = _ASCII.findall(low)
    cjk = _CJK.findall(low)
    tokens.extend(cjk)
    tokens.extend(cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1))
    return tokens


class BM25:
    """标准 BM25（k1=1.5, b=0.75），纯标准库。"""

    def __init__(self, docs: list[dict], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize(d.get("text", "")) for d in docs]
        self.doc_len = [len(t) for t in self.doc_tokens]
        self.avgdl = (sum(self.doc_len) / len(self.doc_len)) if self.doc_len else 0.0
        self.freqs = [Counter(t) for t in self.doc_tokens]
        df: Counter = Counter()
        for toks in self.doc_tokens:
            for term in set(toks):
                df[term] += 1
        n = len(docs)
        self.idf = {
            term: math.log(1 + (n - d + 0.5) / (d + 0.5)) for term, d in df.items()
        }

    def search(self, query: str, k: int = 10) -> list[tuple[int, float]]:
        q = tokenize(query)
        scores = []
        for i, freq in enumerate(self.freqs):
            dl = self.doc_len[i] or 1
            s = 0.0
            for term in q:
                if term not in freq:
                    continue
                idf = self.idf.get(term, 0.0)
                tf = freq[term]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
                s += idf * (tf * (self.k1 + 1)) / (denom or 1)
            if s > 0:
                scores.append((i, s))
        scores.sort(key=lambda x: -x[1])
        return scores[:k]


def _embed(texts: list[str], endpoint: str, model: str | None) -> list[list[float]] | None:
    """可选密集层：调 OpenAI 兼容 /embeddings；任何失败返回 None（降级）。"""
    import urllib.request

    try:
        payload = {"input": texts, "model": model or os.environ.get("EMBED_MODEL", "text-embedding-3-small")}
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ.get('EMBED_API_KEY', '')}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [item["embedding"] for item in data.get("data", [])]
    except Exception:
        return None  # 降级为纯 BM25


def _cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return num / (na * nb)


def rrf_fuse(*rankings: list[int], k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion：多路排名（doc 索引列表）融合，多路命中者靠前。"""
    score: Counter = Counter()
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            score[idx] += 1.0 / (k + rank + 1)
    return [idx for idx, _ in score.most_common()]


def search(docs: list[dict], query: str, k: int = 10, embed_endpoint: str | None = None) -> list[dict]:
    """主入口：BM25（+可选 dense RRF）检索，返回 [{id,text,score}] top-k。"""
    bm = BM25(docs)
    bm_hits = bm.search(query, k=max(k * 3, 20))
    bm_rank = [i for i, _ in bm_hits]

    endpoint = embed_endpoint or os.environ.get("EMBED_ENDPOINT")
    if endpoint:
        doc_vecs = _embed([d.get("text", "") for d in docs], endpoint, None)
        q_vec = _embed([query], endpoint, None)
        if doc_vecs and q_vec:
            dense = sorted(
                range(len(docs)), key=lambda i: -_cosine(q_vec[0], doc_vecs[i])
            )[: max(k * 3, 20)]
            fused = rrf_fuse(bm_rank, dense)
            return [
                {"id": docs[i].get("id", i), "text": docs[i].get("text", ""), "rank": r + 1}
                for r, i in enumerate(fused[:k])
            ]

    bm_score = dict(bm_hits)
    return [
        {"id": docs[i].get("id", i), "text": docs[i].get("text", ""), "score": round(bm_score[i], 4)}
        for i in bm_rank[:k]
    ]


def load_docs(path: Path) -> list[dict]:
    """从 JSONL（每行 {id,text}）或目录（每个 .md/.txt 文件一条）加载语料。"""
    docs: list[dict] = []
    if path.is_dir():
        for f in sorted(path.rglob("*")):
            if f.suffix.lower() in {".md", ".txt"} and f.is_file():
                docs.append({"id": str(f.relative_to(path)), "text": f.read_text(encoding="utf-8", errors="ignore")})
    else:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
                docs.append({"id": obj.get("id"), "text": obj.get("text", "")})
    return docs


def main() -> int:
    ap = argparse.ArgumentParser(description="轻量混合检索（BM25 + 可选 dense RRF）")
    ap.add_argument("--corpus", required=True, help="JSONL({id,text}) 或目录")
    ap.add_argument("--query", required=True)
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()
    docs = load_docs(Path(args.corpus).resolve())
    if not docs:
        raise SystemExit("[retrieval_index] 语料为空")
    hits = search(docs, args.query, k=args.k)
    print(json.dumps({"query": args.query, "n_docs": len(docs), "hits": hits}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
