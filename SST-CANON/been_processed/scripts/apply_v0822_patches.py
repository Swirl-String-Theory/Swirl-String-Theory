#!/usr/bin/env python3
"""Apply operational-spacetime + QSS patches onto v0.8.22.

The Downloads cumulative patch equals incremental ∪ QSS exactly; we apply the
two sequential diffs for provenance and archive all three.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import edition_dir, main_tex, rt_tex

VERSION = "0.8.22"
PREV = "0.8.21"
DOWNLOADS = Path.home() / "Downloads"
ARCHIVE_DIR = ROOT / "sources" / "v0.8.22_operational_spacetime_qss"

# Apply sequential pair (not the cumulative union) to avoid double-application.
PATCHES: list[tuple[str, str]] = [
    (
        "SST_CANON-v0.8.21-operational-spacetime-incremental.patch.diff",
        "axiom:operational_spacetime_vortex_matter",
    ),
    (
        "SST_CANON-v0.8.21-quasinormal-swirl-spectroscopy.patch.diff",
        "sec:rt_quasinormal_swirl_spectroscopy",
    ),
]

# Archive-only (redundant with the two applied above).
CUMULATIVE = "SST_CANON-v0.8.21-qss-operational-spacetime-cumulative.patch.diff"


def rewrite_patch(src: Path) -> str:
    """Rewrite v0.8.21 filenames; drop git index headers that can cause silent skips."""
    lines: list[str] = []
    for line in src.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("diff --git ") or line.startswith("index "):
            continue
        lines.append(
            line.replace(f"SST_CANON-v{PREV}", f"SST_CANON-v{VERSION}")
        )
    return "".join(lines)


def label_present(marker: str) -> bool:
    needle = f"\\label{{{marker}}}"
    for path in (rt_tex(VERSION), main_tex(VERSION)):
        if path.is_file() and needle in path.read_text(encoding="utf-8"):
            return True
    return False


def git_apply(patch_body: str, target: Path) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".diff",
        delete=False,
        newline="\n",
    ) as tmp:
        tmp.write(patch_body)
        tmp_path = Path(tmp.name)
    try:
        for mode in ("--check", None):
            args = ["git", "apply", "--whitespace=nowarn"]
            if mode:
                args.append(mode)
            args.append(str(tmp_path))
            proc = subprocess.run(args, cwd=target, capture_output=True, text=True)
            combined = (proc.stdout or "") + (proc.stderr or "")
            if proc.returncode != 0 or "Skipped patch" in combined:
                raise SystemExit(
                    f"{' '.join(args)} failed (rc={proc.returncode}):\n{combined}"
                )
    finally:
        tmp_path.unlink(missing_ok=True)


def insert_edition_note() -> None:
    from canon_edition import EDITION_CONFIG

    main = main_tex(VERSION)
    cfg = EDITION_CONFIG[VERSION]
    anchor = f"        \\subsubsection{{v{cfg['prev']}}}"
    block = (
        f"        \\subsubsection{{v{VERSION}}}\n"
        f"            {cfg['note']}\n\n"
    )
    text = main.read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" in text:
        print(f"SKIP edition note v{VERSION}: already present")
        return
    if anchor not in text:
        raise SystemExit(f"edition-note anchor not found: {anchor}")
    main.write_text(text.replace(anchor, block + anchor, 1), encoding="utf-8")
    print(f"Inserted edition note v{VERSION}")


def archive_sources() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    names = [name for name, _ in PATCHES] + [CUMULATIVE]
    for name in names:
        src = DOWNLOADS / name
        if src.is_file():
            shutil.copy2(src, ARCHIVE_DIR / name)
    readme = ARCHIVE_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# v0.8.22 operational spacetime + QSS patches (archived)",
                "",
                "Applied in order to `been_processed/v0.8.22/`:",
                "",
                "1. `...-operational-spacetime-incremental.patch.diff`",
                "2. `...-quasinormal-swirl-spectroscopy.patch.diff`",
                "",
                "The cumulative file equals the exact union of (1) and (2) and is",
                "archived for provenance only (not applied separately).",
                "",
                "Source location: `~/Downloads/` at build time.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Archived under {ARCHIVE_DIR.relative_to(ROOT)}")


def main() -> None:
    target = edition_dir(VERSION)
    if not target.is_dir():
        raise SystemExit(f"v{VERSION} missing; run apply_v0822.py first")

    for name, marker in PATCHES:
        src = DOWNLOADS / name
        if not src.is_file():
            # fall back to archive if Downloads cleaned
            src = ARCHIVE_DIR / name
        if not src.is_file():
            raise SystemExit(f"missing patch: {name}")
        if label_present(marker):
            print(f"SKIP {name}: {marker} already present")
            continue
        print(f"Applying {name}")
        git_apply(rewrite_patch(src), target)
        if not label_present(marker):
            raise SystemExit(f"after apply, marker still missing: {marker}")
        print(f"Applied {name}")

    insert_edition_note()
    archive_sources()
    print(f"v{VERSION} operational-spacetime + QSS patches done.")


if __name__ == "__main__":
    main()
