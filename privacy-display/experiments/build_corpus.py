"""
测试语料生成（改进项 C2）

原 benchmark 仅用 1 张合成图，第一版语料也只有 12 张。投稿 IEEE Access
前需要更接近论文实验的样本量和分层统计。本脚本默认生成 12 类 × 10 变体
= 120 张可复现合成语料，并输出:

  - data/test_images/*.png
  - data/test_images/ground_truth.json
  - data/test_images/corpus_metadata.json

运行: python experiments/build_corpus.py
"""

import sys
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "data" / "test_images"


BASE_CORPUS = [
    {
        "slug": "en_short",
        "category": "short_secret",
        "language": "en",
        "layout": "single",
        "font_base": 34,
        "texts": [
            "PASSWORD admin123",
            "ROOT TOKEN 7fa91c",
            "API KEY sk-test-4821",
            "VPN CODE 928441",
            "LOGIN otp 614209",
        ],
    },
    {
        "slug": "en_sentence",
        "category": "sentence",
        "language": "en",
        "layout": "single",
        "font_base": 27,
        "texts": [
            "The quick brown fox jumps over the lazy dog",
            "Quarterly revenue increased by fifteen percent",
            "Do not forward this confidential report",
            "Prototype release is scheduled for Friday",
            "Camera resistant display masking is active",
        ],
    },
    {
        "slug": "zh_short",
        "category": "short_secret",
        "language": "zh",
        "layout": "single",
        "font_base": 34,
        "texts": [
            "机密文件 严禁外传",
            "账号权限 临时授权",
            "内部资料 禁止拍摄",
            "客户档案 仅限本人",
            "安全口令 六位验证",
        ],
    },
    {
        "slug": "zh_sentence",
        "category": "sentence",
        "language": "zh",
        "layout": "single",
        "font_base": 27,
        "texts": [
            "本季度营业收入同比增长百分之十五",
            "会议纪要包含尚未公开的项目计划",
            "屏幕信息需要抵御智能眼镜拍摄",
            "系统在高刷新率下进行时间分片显示",
            "测试样本覆盖中文句子和敏感字段",
        ],
    },
    {
        "slug": "mixed",
        "category": "mixed_credentials",
        "language": "mixed",
        "layout": "single",
        "font_base": 29,
        "texts": [
            "用户 user@mail.com 密码 Pa$$w0rd",
            "项目 Alpha-7 负责人 王工",
            "token eyJhbGc user=andy",
            "订单 A2026 金额 ¥8192",
            "邮箱 qa-team@example.cn",
        ],
    },
    {
        "slug": "digits",
        "category": "numbers",
        "language": "symbol",
        "layout": "single",
        "font_base": 33,
        "texts": [
            "1234567890 3.14159 0xFF2A",
            "987-654-3210 2026/06/12",
            "Budget 482,913.75 USD",
            "SN 09A7-4C22-88F1",
            "IP 192.168.31.42:8080",
        ],
    },
    {
        "slug": "code",
        "category": "code",
        "language": "code",
        "layout": "multi",
        "font_base": 22,
        "texts": [
            "def login(pwd):\n    return hash(pwd)",
            "if token.expired:\n    refresh(token)",
            "SELECT id, salary\nFROM staff\nWHERE role='admin';",
            "privateKey = load_key()\nsign(data, privateKey)",
            "curl -H 'Auth: Bearer xxx'\nhttps://api.local/v2",
        ],
    },
    {
        "slug": "table",
        "category": "table",
        "language": "en",
        "layout": "multi",
        "font_base": 21,
        "texts": [
            "ID  Name   Salary\n01  Alice  9500\n02  Bob    8200",
            "Dept   Cost   Risk\nR&D    128K   High\nOps    092K   Low",
            "Rank  Model   CER\n1     OCR-A   0.02\n2     OCR-B   0.11",
            "Acct   Limit   Used\nA102   50000   31800\nB219   12000   9400",
            "Host       Port  Status\n10.0.1.7   443   open\n10.0.1.9   22    open",
        ],
    },
    {
        "slug": "paragraph",
        "category": "paragraph",
        "language": "en",
        "layout": "multi",
        "font_base": 21,
        "texts": [
            "This document contains confidential\nfinancial data for Q4 2026\nDo not distribute externally",
            "The audit draft includes supplier\npricing assumptions and margin\nforecasts for internal review only",
            "Screen privacy must be evaluated\nagainst snapshot streaming and\ncontinuous reconstruction attacks",
            "A stronger attacker may search the\nphase of the display cycle before\nrunning OCR on recovered frames",
            "The prototype validates algorithms\nbut production use still requires\nGPU compositor integration",
        ],
    },
    {
        "slug": "account",
        "category": "financial",
        "language": "symbol",
        "layout": "multi",
        "font_base": 25,
        "texts": [
            "Card 4532-1234-5678-9010\nCVV 123 Exp 08/29",
            "IBAN CN99 1234 5678 0001\nAmount 82,410.00",
            "Payroll acct 6222 0200 1029\nName Alice Zhang",
            "Invoice INV-2026-044\nTax ID 91330100MA",
            "Transfer code 840219\nBank ref ZX-7719-A",
        ],
    },
    {
        "slug": "zh_paragraph",
        "category": "paragraph",
        "language": "zh",
        "layout": "multi",
        "font_base": 23,
        "texts": [
            "第三章 核心算法\n时间分片掩模将每帧拆分\n人眼积分后还原完整图像",
            "项目评审材料\n包含预算安排和人员名单\n请勿通过摄像设备传播",
            "实验结果显示\n单子帧难以被 OCR 识别\n完整周期平均仍可还原",
            "系统采用随机点阵掩模\n并结合互补对抗噪声\n提升单帧防护鲁棒性",
            "后续工作需要补充\n真实手机拍摄与人因实验\n以支撑期刊投稿",
        ],
    },
    {
        "slug": "url_token",
        "category": "url_token",
        "language": "symbol",
        "layout": "single",
        "font_base": 23,
        "texts": [
            "https://api.site.com/v2?token=eyJhbGc",
            "ssh://deploy@10.2.3.4:2222/prod",
            "https://intra.local/pay?id=ZX9012",
            "s3://secret-bucket/reports/q4.xlsx",
            "otpauth://totp/acme?secret=JBSWY3DPE",
        ],
    },
]


def _render_text(text: str, font_size: int, layout: str, variant: int) -> np.ndarray:
    from PIL import Image, ImageDraw, ImageFont

    lines = text.split("\n")
    n_lines = len(lines)
    pad = 20 + (variant % 3) * 4
    line_h = int(font_size * (1.35 + 0.03 * (variant % 2)))
    width = 720 + (variant % 4) * 40
    height = pad * 2 + line_h * n_lines + (variant % 3) * 8

    bg = 245 - (variant % 4) * 4
    fg = 12 + (variant % 3) * 8
    img = Image.new("RGB", (width, height), color=(bg, bg, bg))
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

    if variant % 5 == 4:
        for x in range(0, width, 64):
            draw.line((x, 0, x, height), fill=(230, 230, 230), width=1)

    for i, line in enumerate(lines):
        x = pad + (variant % 2) * 6
        y = pad + i * line_h
        draw.text((x, y), line, fill=(fg, fg, fg), font=font)
        if layout == "single" and variant % 6 == 5:
            draw.line((x, y + line_h - 4, width - pad, y + line_h - 4), fill=(210, 210, 210), width=1)

    return np.array(img)


def iter_corpus_specs(samples_per_template: int = 10) -> list[dict]:
    """Return deterministic corpus item specs."""
    if samples_per_template <= 0:
        raise ValueError("samples_per_template must be positive")
    specs: list[dict] = []
    for base in BASE_CORPUS:
        for variant in range(samples_per_template):
            text = base["texts"][variant % len(base["texts"])]
            suffix = "" if variant < len(base["texts"]) else f" #{variant + 1:02d}"
            if base["layout"] == "multi" and suffix:
                text = f"{text}\nSample {variant + 1:02d}"
            elif suffix:
                text = f"{text}{suffix}"
            font_size = max(16, base["font_base"] + ((variant % 5) - 2) * 2)
            name = f"{base['slug']}_{variant:02d}"
            specs.append({
                "name": name,
                "text": text,
                "font_size": font_size,
                "layout": base["layout"],
                "category": base["category"],
                "language": base["language"],
                "variant": variant,
            })
    return specs


# Backward-friendly constant: callers can inspect default planned corpus.
CORPUS = iter_corpus_specs()


def build(samples_per_template: int = 10) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth: dict[str, str] = {}
    metadata: dict[str, dict] = {}

    for spec in iter_corpus_specs(samples_per_template):
        img = _render_text(
            spec["text"],
            spec["font_size"],
            spec["layout"],
            spec["variant"],
        )
        from PIL import Image
        path = OUT_DIR / f"{spec['name']}.png"
        Image.fromarray(img).save(path)
        truth = spec["text"].replace("\n", " ")
        ground_truth[spec["name"]] = truth
        metadata[spec["name"]] = {
            "truth": truth,
            "category": spec["category"],
            "language": spec["language"],
            "layout": spec["layout"],
            "font_size": spec["font_size"],
            "variant": spec["variant"],
            "width": int(img.shape[1]),
            "height": int(img.shape[0]),
        }
        print(
            f"  生成 {spec['name']}.png  ({img.shape[1]}x{img.shape[0]})  "
            f"[{spec['category']}/{spec['language']}/{spec['layout']}] "
            f"«{truth[:36]}»"
        )

    gt_path = OUT_DIR / "ground_truth.json"
    meta_path = OUT_DIR / "corpus_metadata.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, ensure_ascii=False, indent=2)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n共 {len(ground_truth)} 张测试图，ground truth → {gt_path}")
    print(f"语料元数据 → {meta_path}")
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


def load_corpus_metadata() -> dict:
    """加载语料元数据；旧语料缺失 metadata 时返回空字典。"""
    meta_path = OUT_DIR / "corpus_metadata.json"
    if not meta_path.exists():
        return {}
    with open(meta_path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    build()
