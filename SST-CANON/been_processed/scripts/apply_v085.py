#!/usr/bin/env python3
"""Build v0.8.5: v0.8.4 + highres audit + CALIBRATED relabeling only."""
import shutil
import subprocess
import sys
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata

CANON = ROOT.parent
V085 = ROOT / "v0.8.5"

HIGHRES_MAIN = CANON / "SST_CANON-v0.8.4_corrected_review_patch.highres_conversation_audit.tex"
HIGHRES_RT = (
    CANON
    / "SST_CANON-v0.8.4-research-track_corrected_review_patch.highres_conversation_audit.tex"
)


def run(script: Path) -> None:
    subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def sync_highres() -> None:
    V085.mkdir(parents=True, exist_ok=True)
    if not HIGHRES_MAIN.is_file():
        raise FileNotFoundError(f"Missing highres audit main: {HIGHRES_MAIN}")
    if not HIGHRES_RT.is_file():
        raise FileNotFoundError(f"Missing highres audit research track: {HIGHRES_RT}")
    shutil.copy2(HIGHRES_MAIN, V085 / "SST_CANON-v0.8.5.tex")
    shutil.copy2(HIGHRES_RT, V085 / "SST_CANON-v0.8.5-research-track.tex")


def main() -> None:
    run(SCRIPTS_DIR / "apply_v084.py")
    sync_highres()
    run(SCRIPTS_DIR / "apply_calibrated_audit.py")
    apply_metadata("0.8.5")
    print("v0.8.5 built: v0.8.4 + highres + CALIBRATED audits.")


if __name__ == "__main__":
    main()
