"""
09 - 视觉定位 Grounding
让模型定位图片中目标物体的位置，返回 <bbox> 坐标。
坐标格式: <bbox>x1 y1 x2 y2</bbox>，值域 0-999（归一化坐标）。
"""

import base64
import struct
import zlib
import json
import requests

API_URL = "https://fat-aibrain-large-model-engine.hellobike.cn/v1/chat/completions"
SECRET_KEY = "sk-Vh5iZI1erTwgnXKXbGQsqbC_saQknnGO2a90byMFSKA"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SECRET_KEY}",
}


def create_test_png(width: int = 20, height: int = 20) -> bytes:
    """生成测试用彩色 PNG。"""
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            if x < width // 2 and y < height // 2:
                raw += b"\xff\x00\x00"
            elif x >= width // 2 and y < height // 2:
                raw += b"\x00\xff\x00"
            elif x < width // 2:
                raw += b"\x00\x00\xff"
            else:
                raw += b"\xff\xff\x00"

    def chunk(ct, d):
        c = ct + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def visual_grounding(
    image_b64: str,
    prompt: str,
    model: str = "Doubao-Seed-2.0-Pro-0215",
) -> str:
    """视觉定位 — 返回包含 <bbox> 坐标的描述。"""
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
        "temperature": 0.2,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def parse_bboxes(text: str) -> list[dict]:
    """从模型回复中提取 <bbox> 坐标。"""
    import re
    bboxes = []
    for match in re.finditer(r"<bbox>(\d+)\s+(\d+)\s+(\d+)\s+(\d+)</bbox>", text):
        bboxes.append({
            "x1": int(match.group(1)),
            "y1": int(match.group(2)),
            "x2": int(match.group(3)),
            "y2": int(match.group(4)),
        })
    return bboxes


if __name__ == "__main__":
    print("=== 视觉定位 Grounding 示例 ===\n")

    png_bytes = create_test_png(20, 20)
    b64 = base64.b64encode(png_bytes).decode()

    result = visual_grounding(
        b64,
        "定位图片中每个颜色区域的位置，用 <bbox> 坐标标注每个区域",
    )
    print(f"定位结果:\n{result}\n")

    bboxes = parse_bboxes(result)
    if bboxes:
        print(f"解析到 {len(bboxes)} 个 bbox:")
        for i, box in enumerate(bboxes):
            print(f"  [{i}] x1={box['x1']}, y1={box['y1']}, x2={box['x2']}, y2={box['y2']}")
