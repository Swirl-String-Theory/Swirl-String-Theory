#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-.}"
cp "$ROOT/BASE/SST_CANON-v0.8.20.tex" "$TARGET/SST_CANON-v0.8.20.tex"
cp "$ROOT/BASE/SST_CANON-v0.8.20-research-track.tex" "$TARGET/SST_CANON-v0.8.20-research-track.tex"
for p in "$ROOT"/patches/*.diff; do
  echo "Applying $(basename "$p")"
  (cd "$TARGET" && git apply --check "$p" && git apply "$p")
done
