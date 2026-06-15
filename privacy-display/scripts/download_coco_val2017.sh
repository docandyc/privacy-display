#!/usr/bin/env bash
set -euo pipefail

ROOT="${COCO_ROOT:-data/coco}"
mkdir -p "$ROOT"

echo "[COCO] target: $ROOT"
if [ ! -d "$ROOT/val2017" ]; then
  curl -L --retry 3 -o "$ROOT/val2017.zip" "http://images.cocodataset.org/zips/val2017.zip"
  unzip -q -n "$ROOT/val2017.zip" -d "$ROOT"
else
  echo "[COCO] val2017 already exists"
fi

if [ ! -f "$ROOT/annotations/instances_val2017.json" ]; then
  curl -L --retry 3 -o "$ROOT/annotations_trainval2017.zip" "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
  unzip -q -n "$ROOT/annotations_trainval2017.zip" -d "$ROOT"
else
  echo "[COCO] annotations already exist"
fi

echo "[COCO] ready:"
echo "  images:      $ROOT/val2017"
echo "  annotations: $ROOT/annotations/instances_val2017.json"
