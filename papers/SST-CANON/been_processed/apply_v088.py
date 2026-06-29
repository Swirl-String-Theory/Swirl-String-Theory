#!/usr/bin/env python3
"""Build v0.8.8: v0.8.7 + Gemini epistemic/notation audit."""
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition

ROOT = Path(__file__).resolve().parent


def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    run(ROOT / "apply_v087.py")
    copy_edition("0.8.7", "0.8.8")
    run(ROOT / "apply_gemini_audit.py", "0.8.8")
    apply_metadata("0.8.8")
    print("v0.8.8 built: v0.8.7 + Gemini audit.")


if __name__ == "__main__":
    main()
