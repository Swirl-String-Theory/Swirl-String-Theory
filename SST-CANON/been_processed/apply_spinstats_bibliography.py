#!/usr/bin/env python3
"""Add spinstats bibliography entries to a canon edition (default v0.8.7)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLOCK = ROOT / "blocks" / "spinstats_bibliography_block.tex"
MARKER = "\\bibitem{WilczekZee1983}"
ANCHOR = "        \\end{thebibliography}"


def apply(version: str = "0.8.7") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    text = main.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"spinstats bibliography already present in v{version}.")
        return
    block = BLOCK.read_text(encoding="utf-8")
    if ANCHOR not in text:
        raise SystemExit(f"bibliography anchor not found in v{version}")
    text = text.replace(ANCHOR, block + ANCHOR, 1)
    main.write_text(text, encoding="utf-8")
    print(f"spinstats bibliography applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.7"
    apply(version)


if __name__ == "__main__":
    main()
