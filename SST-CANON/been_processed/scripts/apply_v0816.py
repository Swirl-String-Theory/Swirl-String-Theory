#!/usr/bin/env python3
"""Build v0.8.16: v0.8.15 + sharp-conclusions audit patch (A/B/C)."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.15" / "SST_CANON-v0.8.15.tex").is_file():
        run(SCRIPTS_DIR / "apply_v0815.py")
    copy_edition("0.8.15", "0.8.16")
    run(SCRIPTS_DIR / "apply_sharp_conclusions_0816.py", "0.8.16")
    apply_metadata("0.8.16")
    print("v0.8.16 built: v0.8.15 + sharp-conclusions audit patch.")


if __name__ == "__main__":
    main()
