#!/usr/bin/env python3
"""Build v0.8.13: v0.8.12 + relativity-emergence patch (SR/GR emergence ladder)."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.12" / "SST_CANON-v0.8.12.tex").is_file():
        run(SCRIPTS_DIR / "apply_v0812.py")
    copy_edition("0.8.12", "0.8.13")
    run(SCRIPTS_DIR / "apply_relativity_emergence.py", "0.8.13")
    apply_metadata("0.8.13")
    print("v0.8.13 built: v0.8.12 + relativity-emergence patch.")


if __name__ == "__main__":
    main()
