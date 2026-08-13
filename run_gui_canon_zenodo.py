#!/usr/bin/env python3
"""Launch the SST Canon Zenodo Version Manager GUI from the repo root."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GUI = ROOT / "tools" / "zenodo_tools" / "GUI_canon_zenodo.py"


def main() -> None:
    if not GUI.is_file():
        print(f"GUI not found: {GUI}", file=sys.stderr)
        sys.exit(1)
    sys.path.insert(0, str(GUI.parent))
    runpy.run_path(str(GUI), run_name="__main__")


if __name__ == "__main__":
    main()
