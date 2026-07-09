#!/usr/bin/env python3
"""Build v0.8.10: v0.8.9 + Gemini round-2 notation/epistemic audit."""
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition

def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.9" / "SST_CANON-v0.8.9.tex").is_file():
        run(SCRIPTS_DIR / "apply_v089.py")
    copy_edition("0.8.9", "0.8.10")
    run(SCRIPTS_DIR / "apply_gemini_round2.py", "0.8.10")
    apply_metadata("0.8.10")
    print("v0.8.10 built: v0.8.9 + Gemini round-2 audit.")


if __name__ == "__main__":
    main()
