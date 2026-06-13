#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_FALLBACK:-python3}"
fi

ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.local}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

RUN_TESTS=1
RUN_FULL_OFFLINE=0
RUN_VLM_LIVE=0
RUN_REAL_CAPTURE=0

usage() {
  cat <<'EOF'
Usage: scripts/reproduce_all.sh [options]

Refresh publication-facing reproducibility artifacts.

Default safe path:
  - run unit/regression tests
  - run VLM dry-run call-count check
  - regenerate publication_summary.{json,md}
  - regenerate reproducibility_manifest.json

Options:
  --full-offline   Also rerun heavier offline experiments and benchmarks.
  --real-capture   Also analyze manually collected real camera captures.
  --with-vlm-live  Also run the live online VLM benchmark. Requires SILICONFLOW_API_KEY.
  --skip-tests     Skip pytest in this orchestration run.
  -h, --help       Show this help.

No API key value is accepted as an argument. For live VLM, export
SILICONFLOW_API_KEY in the shell environment or put it in local ignored
.env.local before running this script.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full-offline)
      RUN_FULL_OFFLINE=1
      ;;
    --real-capture)
      RUN_REAL_CAPTURE=1
      ;;
    --with-vlm-live)
      RUN_VLM_LIVE=1
      ;;
    --skip-tests)
      RUN_TESTS=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

run_cmd() {
  printf '\n[reproduce]'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

run_python() {
  run_cmd "$PYTHON_BIN" "$@"
}

if [[ "$RUN_TESTS" -eq 1 ]]; then
  run_python -m pytest tests/ -q
fi

if [[ "$RUN_FULL_OFFLINE" -eq 1 ]]; then
  run_python experiments/build_corpus.py
  run_python -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','paddleocr'], merge_existing=True)"
  run_python experiments/attack_analysis.py
  run_python experiments/detection_attack.py
  run_python experiments/view_attack.py
  run_python experiments/unet_reconstruction.py
fi

run_python experiments/vlm_readability_analysis.py --dry-run --samples-per-category 1

if [[ "$RUN_REAL_CAPTURE" -eq 1 ]]; then
  run_python experiments/real_capture_analysis.py --engines tesseract
fi

if [[ "$RUN_VLM_LIVE" -eq 1 ]]; then
  if [[ -z "${SILICONFLOW_API_KEY:-}" ]]; then
    echo "SILICONFLOW_API_KEY is required for --with-vlm-live" >&2
    exit 2
  fi
  run_python experiments/vlm_readability_analysis.py --samples-per-category 1
fi

run_python experiments/publication_summary.py
run_python experiments/reproducibility_manifest.py

cat <<'EOF'

[reproduce] Artifacts refreshed:
  experiments/results/publication_summary.json
  experiments/results/publication_summary.md
  experiments/results/reproducibility_manifest.json
EOF
