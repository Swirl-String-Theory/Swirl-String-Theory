#!/usr/bin/env python3
"""Build v0.8.17: v0.8.16 + sst_v0_8_16_patch_bundle + patch_canon.txt."""
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition

ROOT = Path(__file__).resolve().parent


def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.16" / "SST_CANON-v0.8.16.tex").is_file():
        run(ROOT / "apply_v0816.py")
    copy_edition("0.8.16", "0.8.17")
    run(ROOT / "apply_v0817_bundle.py", "0.8.17")
    apply_metadata("0.8.17")
    print("v0.8.17 built: v0.8.16 + patch bundle + ropelength convention block.")


if __name__ == "__main__":
    main()
