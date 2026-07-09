#!/usr/bin/env python3
"""Build v0.8.12: v0.8.11 + Gemini round-3 epistemic patch."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.11" / "SST_CANON-v0.8.11.tex").is_file():
        run(SCRIPTS_DIR / "apply_v0811.py")
    copy_edition("0.8.11", "0.8.12")
    run(SCRIPTS_DIR / "apply_gemini_round3.py", "0.8.12")
    apply_metadata("0.8.12")
    print("v0.8.12 built: v0.8.11 + Gemini round-3 epistemic patch.")


if __name__ == "__main__":
    main()
