#!/usr/bin/env python3
"""Build v0.8.14: v0.8.13 + core-torsion / two-speed discipline patch."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.13" / "SST_CANON-v0.8.13.tex").is_file():
        run(SCRIPTS_DIR / "apply_v0813.py")
    copy_edition("0.8.13", "0.8.14")
    run(SCRIPTS_DIR / "apply_core_torsion.py", "0.8.14")
    apply_metadata("0.8.14")
    print("v0.8.14 built: v0.8.13 + core-torsion patch.")


if __name__ == "__main__":
    main()
