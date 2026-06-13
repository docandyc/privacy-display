"""
Generate paper/thesis-ready tables from experiment result JSON files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.evaluation.publication_summary import (  # noqa: E402
    SUMMARY_JSON,
    SUMMARY_MD,
    write_publication_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate publication result summary")
    parser.add_argument("--results-dir", default="experiments/results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = write_publication_summary(args.results_dir)
    print(f"Wrote {Path(args.results_dir) / SUMMARY_JSON}")
    print(f"Wrote {Path(args.results_dir) / SUMMARY_MD}")
    print(f"OCR engines: {len(summary['ocr']['engines'])}")
    print(f"Strong attacks: {len(summary['strong_camera']['attacks'])}")
    print(f"VLM result available: {summary['vlm']['available']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
