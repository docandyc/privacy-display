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

MPLCONFIGDIR="${MPLCONFIGDIR:-${TMPDIR:-/tmp}/privacy-display-matplotlib}"
export MPLCONFIGDIR
mkdir -p "$MPLCONFIGDIR"

RUN_TESTS=1
RUN_FULL_OFFLINE=0
RUN_VLM_LIVE=0
RUN_REAL_CAPTURE=0
RUN_DETECTION_SUITE=0

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
  --detection-suite  Also run the COCO/MOT17 multi-detector suite if datasets exist.
  --real-capture   Also finalize already collected real camera capture artifacts.
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
    --detection-suite)
      RUN_DETECTION_SUITE=1
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
  SURYA_PYTHON="${SURYA_PYTHON:-$ROOT_DIR/.venv-surya/bin/python}"
  if [[ ! -x "$SURYA_PYTHON" ]]; then
    echo "Missing Surya environment: $SURYA_PYTHON" >&2
    echo "Create it before running --full-offline, or set SURYA_PYTHON." >&2
    exit 1
  fi
  run_cmd "$SURYA_PYTHON" -c "from src.evaluation.benchmark import run_corpus_multi_engine; run_corpus_multi_engine(engines=['tesseract','easyocr','surya'], merge_existing=True)"
  run_python experiments/attack_analysis.py
  run_python experiments/detection_attack.py
  run_python experiments/view_attack.py
  run_python experiments/unet_reconstruction.py
  # Full corpus (samples-per-category 20 >= largest category bucket => all 120)
  # for tight bootstrap CIs on the publication-facing ablations.
  run_python experiments/component_ablation.py --samples-per-category 20 --max-samples 120
  run_python experiments/recognizer_generalization.py --engines tesseract --samples-per-category 20 --max-samples 120
  run_python experiments/perceptual_ablation.py --samples-per-category 20 --max-samples 120
  run_python experiments/pareto_sweep.py --samples-per-category 20 --max-samples 120
  run_python experiments/strong_attack_extra.py --samples-per-category 20 --max-samples 120
  run_python experiments/adaptive_attack_ablation.py --samples-per-category 20 --max-samples 120
  run_python experiments/camera_pipeline_ablation.py --samples-per-category 20 --max-samples 120
  run_python experiments/screen_privacy_baselines.py --samples-per-category 20 --max-samples 120
  run_python experiments/brightness_compensation_ablation.py --samples-per-category 20 --max-samples 120
  run_python experiments/mask_granularity_ablation.py --samples-per-category 20 --max-samples 120
  # epsilon sweep (8 budgets) and seed sweep (10 seeds) carry an extra inner
  # multiplier, so use a stratified subset to keep runtime bounded.
  run_python experiments/noise_epsilon_sweep.py --samples-per-category 5 --max-samples 60
  run_python experiments/seed_sensitivity.py --seeds 10 --samples-per-category 5 --max-samples 60
fi

if [[ "$RUN_DETECTION_SUITE" -eq 1 ]]; then
  # Heavy, GPU-oriented; device auto-detected. Each block is skipped when its
  # dataset is absent so the offline reproduction path never hard-fails.
  COCO_ROOT="${COCO_ROOT:-data/coco}"
  MOT17_ROOT="${MOT17_ROOT:-data/MOT17}"
  if [[ -f "$COCO_ROOT/annotations/instances_val2017.json" ]]; then
    run_python experiments/coco_detection_attack.py --coco-root "$COCO_ROOT"
  else
    echo "[reproduce] skip COCO suite: $COCO_ROOT/annotations/instances_val2017.json not found" >&2
  fi
  if [[ -d "$MOT17_ROOT/train" ]]; then
    run_python experiments/mot_video_detection.py --mot-root "$MOT17_ROOT"
    run_python experiments/mot_tracking_attack.py --mot-root "$MOT17_ROOT"
  else
    echo "[reproduce] skip MOT suite: $MOT17_ROOT/train not found" >&2
  fi
fi

run_python experiments/vlm_readability_analysis.py --dry-run --samples-per-category 1
run_python experiments/vlm_prompt_ablation.py --dry-run --samples-per-category 1
run_python experiments/vlm_model_ablation.py --dry-run --samples-per-category 3

if [[ "$RUN_REAL_CAPTURE" -eq 1 ]]; then
  run_python experiments/finalize_real_capture_artifacts.py
fi

if [[ "$RUN_VLM_LIVE" -eq 1 ]]; then
  if [[ -z "${SILICONFLOW_API_KEY:-}" ]]; then
    echo "SILICONFLOW_API_KEY is required for --with-vlm-live" >&2
    exit 2
  fi
  run_python experiments/vlm_readability_analysis.py --samples-per-category 1
  run_python experiments/vlm_model_ablation.py --samples-per-category 3
fi

run_python experiments/publication_summary.py
run_python experiments/reproducibility_manifest.py

cat <<'EOF'

[reproduce] Artifacts refreshed:
  experiments/results/publication_summary.json
  experiments/results/publication_summary.md
  experiments/results/reproducibility_manifest.json
EOF
