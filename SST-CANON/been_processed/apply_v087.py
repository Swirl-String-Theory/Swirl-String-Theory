#!/usr/bin/env python3
"""Build v0.8.7: v0.8.6 + Z2 spinstats block + bibliography."""
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition

ROOT = Path(__file__).resolve().parent


def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    run(ROOT / "apply_v086.py")
    copy_edition("0.8.6", "0.8.7")
    run(ROOT / "apply_spinstats_z2.py", "0.8.7")
    run(ROOT / "apply_spinstats_bibliography.py", "0.8.7")
    apply_metadata("0.8.7")
    print("v0.8.7 built: v0.8.6 + Z2 spinstats + bibliography.")


if __name__ == "__main__":
    main()
