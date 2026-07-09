#!/usr/bin/env python3
"""Insert Z2 spinstats block into a canon edition (default v0.8.7)."""
import sys
from _paths import ROOT, SCRIPTS_DIR

BLOCK = ROOT / "blocks" / "spinstats_z2_sector_block.tex"
ANCHOR = (
    "        positive values.\n\n"
    "        \\textbf{[OPEN] Derivation of the spinorial boundary condition.}"
)
MARKER = "Why the scalar substrate is bosonic"


def apply(version: str = "0.8.7") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    text = main.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"spinstats Z2 block already present in v{version}.")
        return
    block = BLOCK.read_text(encoding="utf-8")
    if ANCHOR not in text:
        raise SystemExit(f"anchor not found in v{version} main canon")
    text = text.replace(
        ANCHOR,
        "        positive values.\n\n" + block + "\n        \\textbf{[OPEN] Derivation of the spinorial boundary condition.}",
        1,
    )
    main.write_text(text, encoding="utf-8")
    print(f"spinstats Z2 block applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.7"
    apply(version)


if __name__ == "__main__":
    main()
