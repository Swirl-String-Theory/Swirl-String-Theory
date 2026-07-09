#!/usr/bin/env python3
"""Build v0.8.9: v0.8.8 + triadic gravity-response corollary and research-track diagnostics."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.8" / "SST_CANON-v0.8.8.tex").is_file():
        run(SCRIPTS_DIR / "apply_v088.py")
    copy_edition("0.8.8", "0.8.9")
    run(SCRIPTS_DIR / "apply_triadic_gravity.py", "0.8.9")
    apply_metadata("0.8.9")
    print("v0.8.9 built: v0.8.8 + triadic gravity-response patch.")


if __name__ == "__main__":
    main()
