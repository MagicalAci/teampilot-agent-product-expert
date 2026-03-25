"""
07 - 图片理解
通过 base64 编码传入图片，让模型识别和描述图片内容。

注意：幻视平台无法访问外网 URL，必须用 base64 编码嵌入图片。
图片最小尺寸要求 14x14 像素。
"""

import base64
import io
import json
import struct
import zlib
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


def create_test_png(width: int = 20, height: int = 20) -> bytes:
    """生成一个测试用的彩色 PNG 图片（纯 Python，无外部依赖）。"""
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            if x < width // 2 and y < height // 2:
                raw += b"\xff\x00\x00"   # 左上: 红
            elif x >= width // 2 and y < height // 2:
                raw += b"\x00\xff\x00"   # 右上: 绿
            elif x < width // 2:
                raw += b"\x00\x00\xff"   # 左下: 蓝
            else:
                raw += b"\xff\xff\x00"   # 右下: 黄

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def image_understanding(image_b64: str, prompt: str, model: str = "Doubao-Seed-2.0-Mini-0215") -> str:
    """图片理解 — 传入 base64 编码的图片。"""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
        "temperature": 0.7,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def image_from_file(file_path: str) -> str:
    """从文件读取图片并转为 base64。"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


if __name__ == "__main__":
    print("=== 图片理解示例 ===\n")

    # 生成测试图片
    png_bytes = create_test_png(20, 20)
    b64 = base64.b64encode(png_bytes).decode()
    print(f"测试图片: 20x20 四色块, base64 长度: {len(b64)}")

    # 调用图片理解
    result = image_understanding(b64, "描述这张图片的颜色分布和布局")
    print(f"\n识别结果:\n{result}")

    print("\n--- 实际使用时 ---")
    print('b64 = image_from_file("screenshot.png")')
    print('result = image_understanding(b64, "这个页面的布局有什么问题？")')
