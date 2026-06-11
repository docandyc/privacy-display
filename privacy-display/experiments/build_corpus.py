"""
测试语料生成（改进项 C2）

原 benchmark 仅用 1 张合成图（样本量 n=1，无统计显著性）。本脚本生成
多样化语料：不同字号、版式、语言（中/英/代码/表格/数字），用于产出
mean±std 统计，提升实验严谨性。

运行: python experiments/build_corpus.py
输出: data/test_images/*.png + data/test_images/ground_truth.json
"""

import sys
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "data" / "test_images"


# 语料内容：(文件名, 文本, 字号, 版式)
CORPUS = [
    ("en_short", "PASSWORD admin123", 36, "single"),
    ("en_sentence", "The quick brown fox jumps over the lazy dog", 28, "single"),
    ("zh_short", "机密文件 严禁外传", 36, "single"),
    ("zh_sentence", "本季度营业收入同比增长百分之十五", 28, "single"),
    ("mixed", "用户 user@mail.com 密码 Pa$$w0rd", 30, "single"),
    ("digits", "1234567890 3.14159 0xFF2A", 34, "single"),
    ("code", "def login(pwd):\n    return hash(pwd)", 24, "multi"),
    ("table", "ID  Name   Salary\n01  Alice  9500\n02  Bob    8200", 22, "multi"),
    ("paragraph", "This document contains confidential\nfinancial data for Q4 2026\nDo not distribute externally", 22, "multi"),
    ("account", "Card 4532-1234-5678-9010\nCVV 123 Exp 08/29", 26, "multi"),
    ("zh_paragraph", "第三章 核心算法\n时间分片掩模将每帧拆分\n人眼积分后还原完整图像", 24, "multi"),
    ("url_token", "https://api.site.com/v2?token=eyJhbGc", 24, "single"),
]


def _render_text(text: str, font_size: int, layout: str) -> np.ndarray:
    from PIL import Image, ImageDraw, ImageFont

    lines = text.split("\n")
    n_lines = len(lines)
    pad = 20
    line_h = int(font_size * 1.4)
    width = 720
    height = pad * 2 + line_h * n_lines

    img = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    font = None
    for fp in [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    for i, line in enumerate(lines):
        draw.text((pad, pad + i * line_h), line, fill=(15, 15, 15), font=font)

    return np.array(img)


def build() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth = {}

    for name, text, size, layout in CORPUS:
        img = _render_text(text, size, layout)
        from PIL import Image
        path = OUT_DIR / f"{name}.png"
        Image.fromarray(img).save(path)
        # OCR ground truth 用空格连接（去掉换行便于 CER 计算）
        ground_truth[name] = text.replace("\n", " ")
        print(f"  生成 {name}.png  ({img.shape[1]}x{img.shape[0]})  «{text[:30].replace(chr(10),' ')}»")

    gt_path = OUT_DIR / "ground_truth.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, ensure_ascii=False, indent=2)

    print(f"\n共 {len(CORPUS)} 张测试图，ground truth → {gt_path}")
    return ground_truth


def load_corpus() -> tuple[list, list, list]:
    """加载语料：返回 (images, ground_truths, names)。"""
    from PIL import Image
    gt_path = OUT_DIR / "ground_truth.json"
    if not gt_path.exists():
        build()
    with open(gt_path, encoding="utf-8") as f:
        gt = json.load(f)
    images, truths, names = [], [], []
    for name, text in gt.items():
        p = OUT_DIR / f"{name}.png"
        if p.exists():
            images.append(np.array(Image.open(p).convert("RGB")))
            truths.append(text)
            names.append(name)
    return images, truths, names


if __name__ == "__main__":
    build()
