#!/usr/bin/env bash
set -euo pipefail

ROOT="${MOT17_ROOT:-data/MOT17}"
URL="${MOT17_URL:-https://motchallenge.net/data/MOT17.zip}"
mkdir -p "$ROOT"

echo "[MOT17] target: $ROOT"
if [ ! -d "$ROOT/train" ]; then
  curl -L --retry 3 -o "$ROOT/MOT17.zip" "$URL"
  unzip -q -n "$ROOT/MOT17.zip" -d "$ROOT"
  if [ -d "$ROOT/MOT17/train" ] && [ ! -d "$ROOT/train" ]; then
    mv "$ROOT/MOT17/"* "$ROOT/"
    rmdir "$ROOT/MOT17" || true
  fi
else
  echo "[MOT17] train split already exists"
fi

echo "[MOT17] ready:"
echo "  root: $ROOT"
echo "  expected sequences: $ROOT/train/MOT17-*/img1 and $ROOT/train/MOT17-*/gt/gt.txt"
