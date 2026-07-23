#!/usr/bin/env python3
"""Ingest validated v0.8.23 endpoint from to_do_patches into been_processed."""
from __future__ import annotations

import shutil
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import EDITION_CONFIG, edition_dir, main_tex, rt_tex

VERSION = "0.8.23"
PREV = "0.8.22"
TODO = ROOT.parent / "to_do_patches"
ARCHIVE = ROOT / "sources" / "v0.8.23_genesis_link_field"

PATCH_NAMES = [
    "SST_CANON-v0.8.22-to-v0.8.23-APPLY.txt",
    "SST_CANON-v0.8.22-to-v0.8.23-COMBINED.patch.diff",
    "SST_CANON-v0.8.22-to-v0.8.23-GIT-RENAME.patch.diff",
    "SST_CANON-v0.8.22-to-v0.8.23-MAIN.patch.diff",
    "SST_CANON-v0.8.22-to-v0.8.23-RESEARCH.patch.diff",
    "SST_CANON-v0.8.23-CHANGELOG.md",
]


def ingest_tex() -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
    ):
        src = TODO / name
        if not src.is_file():
            raise SystemExit(f"missing finished file: {src}")
        shutil.copy2(src, dst / name)
        print(f"ingested {name}")


def archive_sources() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for name in PATCH_NAMES:
        src = TODO / name
        if src.is_file():
            shutil.copy2(src, ARCHIVE / name)
    readme = ARCHIVE / "README.md"
    if not readme.is_file():
        readme.write_text(
            "\n".join(
                [
                    "# v0.8.23 Genesis / link-field ingest (archived)",
                    "",
                    "Finished edition lives in `been_processed/v0.8.23/`.",
                    "Ingest copies validated `.tex` files; patches are archived for provenance.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    print(f"archived under {ARCHIVE.relative_to(ROOT)}")


def copy_zenodo() -> None:
    src = edition_dir(PREV) / f"SST_CANON-v{PREV}.zenodo.json"
    dst = edition_dir(VERSION) / f"SST_CANON-v{VERSION}.zenodo.json"
    if src.is_file() and not dst.is_file():
        shutil.copy2(src, dst)
        print("copied zenodo.json")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing")
    ingest_tex()
    copy_zenodo()
    archive_sources()
    # Sanity: edition note already present in delivered tex
    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION} in ingested main tex")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
