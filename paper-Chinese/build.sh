#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$script_dir"

latexmk -g main.tex

if grep -Eq 'Citation .* undefined|There were undefined references|Label\(s\) may have changed' main.log; then
  echo "Build failed: unresolved citations or cross-references remain in main.log." >&2
  exit 1
fi

echo "Built $script_dir/main.pdf with all citations and cross-references resolved."
