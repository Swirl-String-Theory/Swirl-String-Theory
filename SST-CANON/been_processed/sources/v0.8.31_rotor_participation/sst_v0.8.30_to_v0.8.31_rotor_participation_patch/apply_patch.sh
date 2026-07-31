#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_BASE="${1:-SST_CANON-v0.8.30.tex}"
RT_BASE="${2:-SST_CANON-v0.8.30-research-track.tex}"
MAIN_OUT="SST_CANON-v0.8.31.tex"
RT_OUT="SST_CANON-v0.8.31-research-track.tex"

for f in "$MAIN_BASE" "$RT_BASE"; do
  [[ -f "$f" ]] || { echo "Missing base file: $f" >&2; exit 1; }
done
for f in "$MAIN_OUT" "$RT_OUT"; do
  [[ ! -e "$f" ]] || { echo "Refusing to overwrite: $f" >&2; exit 1; }
done
command -v patch >/dev/null || { echo "GNU patch is required." >&2; exit 1; }

patch --dry-run --batch "$MAIN_BASE" < "$ROOT/patches/0001-main-canon-quasistatic-response-guard.diff"
patch --dry-run --batch "$RT_BASE" < "$ROOT/patches/0002-research-track-rotor-participation-audit.diff"

patch --batch -o "$MAIN_OUT" "$MAIN_BASE" < "$ROOT/patches/0001-main-canon-quasistatic-response-guard.diff"
patch --batch -o "$RT_OUT" "$RT_BASE" < "$ROOT/patches/0002-research-track-rotor-participation-audit.diff"

echo "Created: $MAIN_OUT"
echo "Created: $RT_OUT"
