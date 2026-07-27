#!/usr/bin/env python3
"""Ingest validated v0.8.28 endpoint from patch package into been_processed."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from _paths import ROOT

from canon_edition import EDITION_CONFIG, edition_dir, main_tex, rt_tex

VERSION = "0.8.28"
PREV = "0.8.27"
TODO_PATCHES = ROOT.parent / "to_do_patches"
PACKAGE = TODO_PATCHES / "0.8.28_patch_package"
ARCHIVE = ROOT / "sources" / "v0.8.28_action_phase_clock"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex"

# Remaining packages to move into sources after 0.8.28 ingest (0.8.28 moved separately).
OLDER_PACKAGE_MOVES: list[tuple[str, str]] = [
    ("0.8.20-eight-source-patch-series", "v0.8.20_eight_source_patch_series"),
    ("0.8.22-0.8.23", "v0.8.22_0.8.23_patch_package"),
    ("0.8.23-to-v0.8.24-patch-package", "v0.8.24_patch_package"),
    ("0.8.25-clean-patch", "v0.8.25_clean_patch"),
    ("SST_CANON-v0.8.25-clean-patch", "v0.8.25_clean_patch"),
    ("0.8.25-to-0.8.26", "v0.8.26_patch_package"),
]


def ingest_tex() -> None:
    if not PACKAGE.is_dir():
        raise SystemExit(f"missing patch package: {PACKAGE}")
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
    ):
        src = PACKAGE / name
        if not src.is_file():
            raise SystemExit(f"missing finished file: {src}")
        shutil.copy2(src, dst / name)
        print(f"ingested {name}")


def copy_nonrelease() -> None:
    src = PACKAGE / NONRELEASE
    if not src.is_file():
        print(f"no {NONRELEASE} in package (skip)")
        return
    shutil.copy2(src, edition_dir(VERSION) / NONRELEASE)
    print(f"copied {NONRELEASE} into edition folder (not input by main)")


def copy_reference_pdf() -> None:
    src = PACKAGE / f"SST_CANON-v{VERSION}.pdf"
    if not src.is_file():
        print("no packaged PDF to copy")
        return
    out = edition_dir(VERSION) / "$out"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out / f"SST_CANON-v{VERSION}.pdf")
    print(f"copied reference PDF -> $out/{src.name}")


def _move_dir(src: Path, dest: Path) -> Path:
    """Move src directory to dest; nest under from_to_do_patches if dest exists."""
    if not src.is_dir():
        return dest
    if dest.exists():
        nest = dest / "from_to_do_patches"
        nest.mkdir(parents=True, exist_ok=True)
        dest = nest / src.name
        if dest.exists():
            dest = nest / f"{src.name}_moved"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    print(f"moved {src.name} -> {dest.relative_to(ROOT)}")
    return dest


def move_package_to_sources() -> None:
    """Move the whole 0.8.28 package into sources (archive = move, not copy)."""
    if not PACKAGE.is_dir():
        print(f"package already moved or missing: {PACKAGE}")
        return
    if ARCHIVE.exists():
        # Prefer nesting package contents when archive already present
        final = _move_dir(PACKAGE, ARCHIVE)
    else:
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(PACKAGE), str(ARCHIVE))
        final = ARCHIVE
        print(f"moved 0.8.28_patch_package -> {ARCHIVE.relative_to(ROOT)}")
    readme = final / "INGEST_README.md" if final.is_dir() else ARCHIVE / "INGEST_README.md"
    # If we nested, write readme at ARCHIVE root as well
    targets = [ARCHIVE / "INGEST_README.md"]
    if final != ARCHIVE and final.is_dir():
        targets.append(final / "INGEST_README.md")
    body = "\n".join(
        [
            "# v0.8.28 action--phase mass--shell clock ingest (archived)",
            "",
            "Finished release edition lives in `been_processed/v0.8.28/`.",
            "This folder is the moved `to_do_patches/0.8.28_patch_package`.",
            "Nonrelease `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2` is NOT input by main Canon.",
            "Do not `git apply` into been_processed — that would rename/remove v0.8.27.",
            "",
        ]
    )
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    print(f"wrote INGEST_README under {ARCHIVE.relative_to(ROOT)}")


def move_older_todo_packages() -> None:
    """Move remaining to_do_patches package folders into been_processed/sources."""
    sources = ROOT / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    seen_src: set[str] = set()
    for src_name, dest_name in OLDER_PACKAGE_MOVES:
        if src_name in seen_src:
            continue
        src = TODO_PATCHES / src_name
        if not src.is_dir():
            continue
        seen_src.add(src_name)
        dest = sources / dest_name
        _move_dir(src, dest)


def seed_zenodo_json() -> None:
    """Create mint-ready .zenodo.json without inheriting a stale deposit/DOI."""
    dst = edition_dir(VERSION) / f"SST_CANON-v{VERSION}.zenodo.json"
    src = edition_dir(PREV) / f"SST_CANON-v{PREV}.zenodo.json"
    data: dict = {}
    if src.is_file():
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data.pop("deposit_id", None)
    data.pop("doi", None)
    data["title"] = (
        f"Swirl-String-Theory Canon v{VERSION} — "
        "Canonical Reference and Research Framework"
    )
    data["version"] = f"v{VERSION}"
    data["tex_file"] = (
        f"SST-CANON/been_processed/v{VERSION}/SST_CANON-v{VERSION}.tex"
    )
    data.setdefault("pdf_output_dir", "$out")
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"seeded {dst.name} (no deposit_id/doi - Mint via GUI)")


def clear_borrowed_doi() -> None:
    """Remove temporary parent DOI so Mint can assign a unique deposit DOI."""
    tex = main_tex(VERSION)
    content = tex.read_text(encoding="utf-8")
    new = re.sub(
        r"\\newcommand\{\\paperdoi\}\{[^}]*\}",
        r"\\newcommand{\\paperdoi}{}",
        content,
        count=1,
    )
    new = re.sub(r"%!\s*DOI\s*=\s*[^\n]+\n?", "", new, count=1)
    if new != content:
        tex.write_text(new, encoding="utf-8")
        print("cleared borrowed \\paperdoi (Mint will assign)")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing")
    ingest_tex()
    copy_nonrelease()
    clear_borrowed_doi()
    copy_reference_pdf()
    seed_zenodo_json()
    move_package_to_sources()
    move_older_todo_packages()

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION} in ingested main tex")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit("missing \\canonversion for 0.8.28")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    if PACKAGE.is_dir():
        raise SystemExit("0.8.28 package still in to_do_patches after move")
    if not ARCHIVE.exists():
        raise SystemExit(f"archive missing: {ARCHIVE}")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
