"""
Generate a reproducibility manifest for publication-facing experiments.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.reproducibility_manifest import write_reproducibility_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment reproducibility manifest.")
    parser.add_argument(
        "--project-root",
        default=str(ROOT),
        help="Project root containing experiments/, src/, and tests/.",
    )
    parser.add_argument(
        "--output",
        default="experiments/results/reproducibility_manifest.json",
        help="Output JSON path, relative to project root unless absolute.",
    )
    args = parser.parse_args()

    manifest = write_reproducibility_manifest(args.project_root, args.output)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(args.project_root) / output_path

    result_count = sum(1 for item in manifest["result_files"] if item["exists"])
    source_count = sum(1 for item in manifest["source_files"] if item["exists"])
    print(f"Wrote {output_path}")
    print(json.dumps({
        "result_files_present": result_count,
        "source_files_present": source_count,
        "git_dirty": manifest["git"]["dirty"],
        "secret_values_recorded": manifest["secret_policy"]["record_secret_values"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
