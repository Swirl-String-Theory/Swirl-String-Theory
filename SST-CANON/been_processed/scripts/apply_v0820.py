#!/usr/bin/env python3
"""Build v0.8.20: v0.8.19 + to_do_patches queue (chronos, contact, rank9, SSDL)."""
from __future__ import annotations

import shutil
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import apply_metadata, copy_edition, edition_dir, main_tex

VERSION = "0.8.20"
PREV = "0.8.19"


def insert_edition_note(version: str) -> None:
    from canon_edition import EDITION_CONFIG

    main = main_tex(version)
    cfg = EDITION_CONFIG[version]
    anchor = f"        \\subsubsection{{v{cfg['prev']}}}"
    block = (
        f"        \\subsubsection{{v{version}}}\n"
        f"            {cfg['note']}\n\n"
    )
    text = main.read_text(encoding="utf-8")
    if f"\\subsubsection{{v{version}}}" not in text:
        text = text.replace(anchor, block + anchor, 1)
        main.write_text(text, encoding="utf-8")


def main() -> None:
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing; build v0.8.19 first")

    copy_edition(PREV, VERSION)
    apply_metadata(VERSION)
    insert_edition_note(VERSION)

    src_zenodo = edition_dir(PREV) / f"SST_CANON-v{PREV}.zenodo.json"
    dst_zenodo = edition_dir(VERSION) / f"SST_CANON-v{VERSION}.zenodo.json"
    if src_zenodo.is_file() and not dst_zenodo.is_file():
        shutil.copy2(src_zenodo, dst_zenodo)

    print(
        f"v{VERSION} scaffold: v{PREV} copy + metadata. "
        f"Apply to_do_patches queue manually or via apply script."
    )


if __name__ == "__main__":
    main()
