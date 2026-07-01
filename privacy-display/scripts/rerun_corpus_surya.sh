#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SURYA_PYTHON="${SURYA_PYTHON:-$ROOT_DIR/.venv-surya/bin/python}"

if [[ ! -x "$SURYA_PYTHON" ]]; then
  echo "Missing Surya Python environment: $SURYA_PYTHON" >&2
  exit 1
fi

export SURYA_DEVICE="${SURYA_DEVICE:-auto}"
cd "$ROOT_DIR"
exec "$SURYA_PYTHON" experiments/rerun_corpus_surya.py "$@"
