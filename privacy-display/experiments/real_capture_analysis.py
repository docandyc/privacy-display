"""
Analyze manually collected real camera captures.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.real_capture import (  # noqa: E402
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    run_real_capture_ocr,
    write_capture_template,
)


def _parse_engines(value: str) -> list[str]:
    engines = [part.strip() for part in value.split(",") if part.strip()]
    if not engines:
        raise argparse.ArgumentTypeError("at least one OCR engine is required")
    return engines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Real camera capture OCR analysis")
    parser.add_argument("--capture-dir", default="experiments/real_captures")
    parser.add_argument("--metadata", default="metadata.json")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--engines", type=_parse_engines, default=["tesseract"])
    parser.add_argument("--ocr-timeout", type=float, default=10.0)
    parser.add_argument(
        "--init-template",
        action="store_true",
        help="Write experiments/real_captures/metadata_template.json and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.init_template:
        out = write_capture_template(args.capture_dir)
        print(f"Wrote real capture metadata template: {out}")
        return 0

    report = run_real_capture_ocr(
        capture_dir=args.capture_dir,
        metadata_file=args.metadata,
        output_dir=args.output_dir,
        engines=args.engines,
        ocr_timeout=args.ocr_timeout,
    )
    print(f"Wrote {Path(args.output_dir) / REAL_CAPTURE_JSON}")
    print(f"Wrote {Path(args.output_dir) / REAL_CAPTURE_MD}")
    print(
        "Real capture OCR complete: "
        f"captures={report['config']['n_captures']} rows={report['config']['n_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
