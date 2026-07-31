#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PATCH_DIR="$HERE/patches"

MAIN="$ROOT/SST_CANON-v0.8.31.tex"
RT="$ROOT/SST_CANON-v0.8.31-research-track.tex"

for f in "$MAIN" "$RT"; do
  [[ -f "$f" ]] || { echo "Missing source file: $f" >&2; exit 2; }
done

check_sha() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    echo "SHA-256 mismatch for $file" >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 3
  }
}

check_sha "$MAIN" "06c7f5bacfde31d1503bc45de8e7854946b56924c4c18551ecb99d05402f55b3"
check_sha "$RT" "312e87055334681add3b680284d0e9a50063fce7b13c689386aa6b4e4335b18c"

cp "$MAIN" "$ROOT/SST_CANON-v0.8.32.tex"
cp "$RT" "$ROOT/SST_CANON-v0.8.32-research-track.tex"

patch "$ROOT/SST_CANON-v0.8.32.tex"   < "$PATCH_DIR/0001-main-canon-orphaned-normalization.diff"
patch "$ROOT/SST_CANON-v0.8.32-research-track.tex"   < "$PATCH_DIR/0002-research-track-provenance-scaling-audit.diff"

echo "Created:"
echo "  $ROOT/SST_CANON-v0.8.32.tex"
echo "  $ROOT/SST_CANON-v0.8.32-research-track.tex"
