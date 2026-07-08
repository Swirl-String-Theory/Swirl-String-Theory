#!/usr/bin/env python3
"""Build v0.8.6: v0.8.5 + framed self-linking block."""
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition

ROOT = Path(__file__).resolve().parent


def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    run(ROOT / "apply_v085.py")
    copy_edition("0.8.5", "0.8.6")
    run(ROOT / "apply_framed_selflinking.py", "0.8.6")
    apply_metadata("0.8.6")
    print("v0.8.6 built: v0.8.5 + framed self-linking.")


if __name__ == "__main__":
    main()
