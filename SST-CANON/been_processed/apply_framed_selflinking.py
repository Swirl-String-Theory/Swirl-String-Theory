#!/usr/bin/env python3
"""Insert framed self-linking block into a canon edition (default v0.8.6)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLOCK = ROOT / "blocks" / "framed_selflinking_spinorial_block.tex"
ANCHOR = (
    "        Topology protects existing closed carriers; it does not by itself provide\n"
    "        an ideal-Euler mechanism for creating them.\n"
)
MARKER = "subsec:framed_selflinking_spinorial"


def apply(version: str = "0.8.6") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    text = main.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"framed self-linking block already present in v{version}.")
        return
    block = BLOCK.read_text(encoding="utf-8")
    if ANCHOR not in text:
        raise SystemExit(f"anchor not found in v{version} main canon")
    text = text.replace(ANCHOR, ANCHOR + "\n" + block + "\n", 1)
    main.write_text(text, encoding="utf-8")
    print(f"framed self-linking block applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.6"
    apply(version)


if __name__ == "__main__":
    main()
