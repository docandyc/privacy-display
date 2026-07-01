"""Rerun the simulated corpus benchmark with Surya and merge the result."""

import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_RESULT = PROJECT_ROOT / "experiments" / "results" / "corpus_multi_engine.json"
EXPECTED_SURYA_VERSION = "0.14.7"


def validate_existing_results(existing: object) -> None:
    """Require reusable Tesseract and EasyOCR result objects."""
    if not isinstance(existing, dict):
        raise ValueError("existing corpus result must be a JSON object")
    for engine in ("tesseract", "easyocr"):
        if not isinstance(existing.get(engine), dict):
            raise ValueError(f"existing corpus result is missing {engine}")


def merge_results(existing: dict, surya_report: dict) -> dict:
    """Keep the two existing engines and replace all other entries with Surya."""
    validate_existing_results(existing)
    if not isinstance(surya_report.get("surya"), dict):
        raise ValueError("Surya rerun did not produce a surya result")
    return {
        "tesseract": existing["tesseract"],
        "easyocr": existing["easyocr"],
        "surya": surya_report["surya"],
    }


def write_json_atomic(path: Path, payload: dict) -> None:
    """Atomically replace a JSON file using a temporary sibling."""
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def run_surya_only(result_path: str | Path, runner) -> dict:
    """Run Surya into temporary storage, leaving the destination intact on failure."""
    destination = Path(result_path)
    existing = json.loads(destination.read_text(encoding="utf-8"))
    validate_existing_results(existing)

    with tempfile.TemporaryDirectory(
        prefix=".corpus-surya-",
        dir=destination.parent,
    ) as temp_dir:
        surya_report = runner(
            n=4,
            epsilon=8 / 255,
            engines=["surya"],
            output_dir=temp_dir,
            merge_existing=False,
            progress_interval=1,
        )
        merged = merge_results(existing, surya_report)
        write_json_atomic(destination, merged)
        return merged


def check_surya_runtime() -> None:
    """Fail fast when the environment cannot run the pinned Surya adapter."""
    installed = version("surya-ocr")
    if installed != EXPECTED_SURYA_VERSION:
        raise RuntimeError(
            f"expected surya-ocr {EXPECTED_SURYA_VERSION}, found {installed}"
        )

    from src.attack.ocr_evaluator import OCREvaluator

    if "surya" not in OCREvaluator().engines:
        raise RuntimeError("Surya is not available in this Python environment")


def print_summary(report: dict) -> None:
    labels = {
        "tesseract": "Tesseract",
        "easyocr": "EasyOCR",
        "surya": "Surya",
    }
    print("\n最终 Table 5 OCR 结果：")
    for engine in ("tesseract", "easyocr", "surya"):
        row = report[engine]
        reduction = row.get("paired_reduction", {}).get("mean", 0.0)
        print(
            f"  {labels[engine]:10s} N={int(row.get('n_samples', 0)):3d} "
            f"原始={float(row.get('original_mean', 0.0)):.1%} "
            f"单子帧={float(row.get('subframe_mean', 0.0)):.1%} "
            f"降幅={float(reduction):.1%}"
        )


def main(argv=None, *, runner=None, runtime_checker=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "只运行模拟 Table 5 的 Surya OCR，并与既有 Tesseract/EasyOCR "
            "结果安全合并。"
        )
    )
    parser.add_argument(
        "--result",
        type=Path,
        default=DEFAULT_RESULT,
        help="existing corpus_multi_engine.json to update",
    )
    args = parser.parse_args(argv)

    destination = args.result.resolve()
    print("Table 5 Surya-only 重跑：只运行 Surya，保留 Tesseract/EasyOCR。", flush=True)
    print(f"结果文件：{destination}", flush=True)
    print(f"Surya 设备：{os.environ.get('SURYA_DEVICE', 'auto')}", flush=True)

    (runtime_checker or check_surya_runtime)()
    if runner is None:
        from src.evaluation.benchmark import run_corpus_multi_engine

        runner = run_corpus_multi_engine

    report = run_surya_only(destination, runner=runner)
    print_summary(report)
    print("PaddleOCR 已移除，结果已原子写回。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
