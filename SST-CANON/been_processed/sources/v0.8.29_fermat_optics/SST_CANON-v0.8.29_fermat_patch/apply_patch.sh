#!/usr/bin/env bash
set -euo pipefail

OLD_MAIN="SST_CANON-v0.8.28.tex"
OLD_RT="SST_CANON-v0.8.28-research-track.tex"
NEW_MAIN="SST_CANON-v0.8.29.tex"
NEW_RT="SST_CANON-v0.8.29-research-track.tex"
PATCH="SST_CANON-v0.8.29_fermat_optics_content.diff"

for f in "$OLD_MAIN" "$OLD_RT" "$PATCH"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing required file: $f" >&2
    exit 1
  fi
done

if [[ -e "$NEW_MAIN" || -e "$NEW_RT" ]]; then
  echo "Refusing to overwrite existing v0.8.29 files." >&2
  exit 1
fi

cp "$OLD_MAIN" "$NEW_MAIN"
cp "$OLD_RT" "$NEW_RT"

if ! patch --batch --forward -p0 < "$PATCH"; then
  rm -f "$NEW_MAIN" "$NEW_RT"
  echo "Patch failed; copied v0.8.29 files were removed." >&2
  exit 1
fi

echo "Created: $NEW_MAIN"
echo "Created: $NEW_RT"
echo "Build with: pdflatex $NEW_MAIN (run three times for settled references)."
