#!/usr/bin/env bash
set -euo pipefail

if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

COCO_ROOT="${COCO_ROOT:-data/coco}"
MOT17_ROOT="${MOT17_ROOT:-data/MOT17}"
RESULTS_DIR="${RESULTS_DIR:-experiments/results}"
MODELS="${MODELS:-yolo26x,rtdetr-x,faster_rcnn,retinanet}"
ATTACKS="${ATTACKS:-clean,single_subframe,temporal_average}"
N="${N:-4}"
EPSILON="${EPSILON:-0.03137254901960784}"
CONF="${CONF:-0.25}"
IMGSZ="${IMGSZ:-640}"
SEED="${SEED:-0}"
COCO_DEVICE="${COCO_DEVICE:-cuda:0}"
MOT_DEVICE="${MOT_DEVICE:-cuda:1}"
TRACK_DEVICE="${TRACK_DEVICE:-cuda:0}"
PARALLEL="${PARALLEL:-1}"

mkdir -p "$RESULTS_DIR"

COMMON_ARGS=(--models "$MODELS" --attacks "$ATTACKS" --n "$N" --epsilon "$EPSILON" --conf "$CONF" --imgsz "$IMGSZ" --seed "$SEED" --output-dir "$RESULTS_DIR")
COCO_ARGS=("${COMMON_ARGS[@]}" --coco-root "$COCO_ROOT" --device "$COCO_DEVICE")
MOT_ARGS=("${COMMON_ARGS[@]}" --mot-root "$MOT17_ROOT" --device "$MOT_DEVICE")
TRACK_ARGS=("${COMMON_ARGS[@]}" --mot-root "$MOT17_ROOT" --device "$TRACK_DEVICE")

if [ "${SMOKE:-0}" = "1" ]; then
  COCO_ARGS+=(--smoke)
  MOT_ARGS+=(--smoke)
  TRACK_ARGS+=(--smoke)
fi
if [ -n "${COCO_MAX_IMAGES:-}" ]; then
  COCO_ARGS+=(--max-images "$COCO_MAX_IMAGES")
fi
if [ -n "${MOT_MAX_FRAMES:-}" ]; then
  MOT_ARGS+=(--max-frames "$MOT_MAX_FRAMES")
  TRACK_ARGS+=(--max-frames "$MOT_MAX_FRAMES")
fi
if [ -n "${MOT_SEQUENCES:-}" ]; then
  MOT_ARGS+=(--sequences "$MOT_SEQUENCES")
  TRACK_ARGS+=(--sequences "$MOT_SEQUENCES")
fi
if [ "${NO_EXTERNAL_TRACKER:-0}" = "1" ]; then
  TRACK_ARGS+=(--no-external-tracker)
fi
# HOTA via TrackEval: export TRACKEVAL_ROOT=/path/to/TrackEval (inherited by the
# experiment) to fill the HOTA column. Set NO_HOTA=1 to skip the MOTChallenge
# export + TrackEval entirely.
if [ "${NO_HOTA:-0}" = "1" ]; then
  TRACK_ARGS+=(--no-hota)
elif [ -n "${TRACKEVAL_ROOT:-}" ]; then
  TRACK_ARGS+=(--trackeval-root "$TRACKEVAL_ROOT")
fi

echo "[suite] python: $PYTHON_BIN"
echo "[suite] COCO root: $COCO_ROOT"
echo "[suite] MOT17 root: $MOT17_ROOT"
echo "[suite] results: $RESULTS_DIR"
echo "[suite] models: $MODELS"

if [ "$PARALLEL" = "1" ]; then
  echo "[suite] running COCO detection and MOT frame detection in parallel"
  "$PYTHON_BIN" experiments/coco_detection_attack.py "${COCO_ARGS[@]}" &
  coco_pid=$!
  "$PYTHON_BIN" experiments/mot_video_detection.py "${MOT_ARGS[@]}" &
  mot_pid=$!
  wait "$coco_pid"
  wait "$mot_pid"
else
  "$PYTHON_BIN" experiments/coco_detection_attack.py "${COCO_ARGS[@]}"
  "$PYTHON_BIN" experiments/mot_video_detection.py "${MOT_ARGS[@]}"
fi

echo "[suite] running MOT tracking"
"$PYTHON_BIN" experiments/mot_tracking_attack.py "${TRACK_ARGS[@]}"

echo "[suite] refreshing publication summary and reproducibility manifest"
"$PYTHON_BIN" experiments/publication_summary.py
"$PYTHON_BIN" experiments/reproducibility_manifest.py

echo "[suite] done"
echo "  $RESULTS_DIR/coco_detection_attack.json"
echo "  $RESULTS_DIR/mot_video_detection.json"
echo "  $RESULTS_DIR/mot_tracking_attack.json"
