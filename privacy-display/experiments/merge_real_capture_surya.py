"""Replace legacy OCR rows with Surya and aggregate complete position reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.real_capture import REAL_CAPTURE_JSON  # noqa: E402
from src.evaluation.real_capture_merge import (  # noqa: E402
    aggregate_position_reports,
    replace_engine_rows,
    write_real_capture_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    replace = subparsers.add_parser("replace")
    replace.add_argument("--existing", required=True)
    replace.add_argument("--replacement", required=True)

    aggregate = subparsers.add_parser("aggregate")
    aggregate.add_argument("--reports", nargs="+", required=True)
    aggregate.add_argument("--output-dir", default="experiments/results")
    aggregate.add_argument("--ocr-timeout", type=float, default=30.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "replace":
        existing_path = Path(args.existing)
        replacement_path = Path(args.replacement)
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        replacement = json.loads(replacement_path.read_text(encoding="utf-8"))
        updated, stats = replace_engine_rows(
            existing,
            replacement,
            engine="surya",
            remove_engines=("paddleocr", "surya"),
            replacement_source=str(replacement_path),
        )
        write_real_capture_report(existing_path, updated)
        print(json.dumps(stats, ensure_ascii=False))
        return 0

    report, pending = aggregate_position_reports(
        args.reports,
        ocr_timeout=args.ocr_timeout,
    )
    if pending:
        print(
            "Combined report was not regenerated; pending Surya positions: "
            + ", ".join(pending)
        )
        return 0

    output_path = Path(args.output_dir) / REAL_CAPTURE_JSON
    write_real_capture_report(output_path, report)
    print(f"Merged real-capture OCR report: {output_path}")
    print(f"Merged real-capture OCR markdown: {output_path.parent / 'real_capture_ocr.md'}")
    print(
        f"Merged rows={report['config']['n_rows']} "
        f"positions={report['config']['n_positions']} "
        f"engines={','.join(report['config']['engines'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
