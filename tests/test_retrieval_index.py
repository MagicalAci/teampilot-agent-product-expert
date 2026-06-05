"""scripts/retrieval_index.py 契约测试（纯标准库 BM25，无网络）。"""

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "retrieval_index.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("retrieval_index", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ri = _load_module()


DOCS = [
    {"id": "a", "text": "豆包爱学是一款 AI 学习产品，主打拍照搜题和答疑辅导"},
    {"id": "b", "text": "泡泡玛特盲盒潮玩手办收藏，与学习无关"},
    {"id": "c", "text": "AI 学习硬件词典笔点读笔教育工具"},
    {"id": "d", "text": "天气预报今天晴朗适合出行"},
]


class RetrievalIndexTest(unittest.TestCase):
    def test_module_file_exists(self):
        self.assertTrue(MODULE_PATH.exists())

    def test_tokenize_cjk_and_ascii(self):
        toks = ri.tokenize("AI学习")
        for expected in ["ai", "学", "习", "学习"]:
            with self.subTest(tok=expected):
                self.assertIn(expected, toks)

    def test_bm25_ranks_relevant_doc_top(self):
        hits = ri.search(DOCS, "拍照搜题答疑", k=4)
        self.assertTrue(hits, "应有命中")
        self.assertEqual(hits[0]["id"], "a", f"最相关应为 a，实际 {hits[0]}")
        # 无关文档不应排在最前
        top_ids = [h["id"] for h in hits[:2]]
        self.assertNotIn("d", top_ids)

    def test_search_degrades_without_endpoint(self):
        # 未配置 EMBED_ENDPOINT → 纯 BM25，返回带 score 字段、不报错
        hits = ri.search(DOCS, "AI 学习", k=3, embed_endpoint=None)
        self.assertTrue(all("score" in h for h in hits))
        self.assertLessEqual(len(hits), 3)

    def test_rrf_fuse_favors_common(self):
        # 两路都靠前的 idx 2 应排第一
        fused = ri.rrf_fuse([2, 0, 1], [2, 1, 0])
        self.assertEqual(fused[0], 2)


if __name__ == "__main__":
    unittest.main()
