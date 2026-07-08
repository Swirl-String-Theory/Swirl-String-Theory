#!/usr/bin/env python3
"""Build v0.8.18: v0.8.17 RC2 + guardrails_v2 + resolved-tube v3 patches."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from canon_edition import apply_metadata, copy_edition, edition_dir, main_tex, rt_tex

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
PATCH_V2 = SOURCES / "sst_canon_v0.8.17_guardrails_v2.patch"
PATCH_V3 = SOURCES / "sst_canon_v0.8.17_guardrails_v2_to_v3_resolved_tube.patch"
VERSION = "0.8.18"
PREV = "0.8.17"


def _rename_patch(src: Path, dst: Path, replacements: list[tuple[str, str]]) -> None:
    text = src.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    dst.write_text(text, encoding="utf-8")


def apply_git_patch(edition: Path, patch_path: Path) -> None:
    subprocess.run(
        ["git", "apply", str(patch_path)],
        check=True,
        cwd=edition,
    )


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


def migrate_gw170817_bibliography(version: str) -> None:
    """Add relativity-ladder bib keys to main thebibliography if missing."""
    main = main_tex(version)
    text = main.read_text(encoding="utf-8")
    if "LIGOVirgoFermiINTEGRAL2017" in text:
        return
    rt = rt_tex(version)
    rt_text = rt.read_text(encoding="utf-8")
    start = rt_text.find("\\bibitem{LIGOVirgoFermiINTEGRAL2017}")
    end = rt_text.find("\\end{thebibliography}", start)
    if start == -1 or end == -1:
        raise RuntimeError("GW170817 bibliography block not found in research track")
    block = rt_text[start:end].strip()
    lines = []
    for line in block.splitlines():
        if line.startswith("\\bibitem"):
            lines.append("")
            lines.append("            " + line)
        elif line.strip():
            lines.append("            " + line.strip())
    insert = "\n".join(lines) + "\n\n"
    text = text.replace("\n        \\end{thebibliography}", "\n" + insert + "        \\end{thebibliography}", 1)
    main.write_text(text, encoding="utf-8")


def main() -> None:
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing; build v0.8.17 first")

    copy_edition(PREV, VERSION)
    edition = edition_dir(VERSION)
    tmp = SOURCES / "_tmp"

    v2 = tmp / "_apply_v2_0818.patch"
    v3 = tmp / "_apply_v3_0818.patch"
    tmp.mkdir(parents=True, exist_ok=True)
    _rename_patch(
        PATCH_V2,
        v2,
        [
            ("SST_CANON-v0.8.17.tex", f"SST_CANON-v{VERSION}.tex"),
            ("SST_CANON-v0.8.17-research-track.tex", f"SST_CANON-v{VERSION}-research-track.tex"),
        ],
    )
    _rename_patch(
        PATCH_V3,
        v3,
        [
            ("SST_CANON-v0.8.17.guardrails_v2.tex", f"SST_CANON-v{VERSION}.tex"),
            ("SST_CANON-v0.8.17-research-track.guardrails_v2.tex", f"SST_CANON-v{VERSION}-research-track.tex"),
        ],
    )

    apply_git_patch(edition, v2)
    apply_git_patch(edition, v3)
    migrate_gw170817_bibliography(VERSION)
    apply_metadata(VERSION)
    insert_edition_note(VERSION)

    src_zenodo = edition_dir(PREV) / f"SST_CANON-v{PREV}.zenodo.json"
    dst_zenodo = edition_dir(VERSION) / f"SST_CANON-v{VERSION}.zenodo.json"
    if src_zenodo.is_file() and not dst_zenodo.is_file():
        shutil.copy2(src_zenodo, dst_zenodo)

    print(f"v{VERSION} built: v{PREV} + guardrails_v2 + resolved-tube v3.")


if __name__ == "__main__":
    main()
