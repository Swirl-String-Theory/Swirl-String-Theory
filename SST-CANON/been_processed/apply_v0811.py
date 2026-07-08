#!/usr/bin/env python3
"""Build v0.8.11: v0.8.10 + final notation hygiene patch."""
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition

ROOT = Path(__file__).resolve().parent


def run(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def main() -> None:
    if not (ROOT / "v0.8.10" / "SST_CANON-v0.8.10.tex").is_file():
        run(ROOT / "apply_v0810.py")
    copy_edition("0.8.10", "0.8.11")
    run(ROOT / "apply_final_hygiene.py", "0.8.11")
    apply_metadata("0.8.11")
    print("v0.8.11 built: v0.8.10 + final hygiene patch.")


if __name__ == "__main__":
    main()
