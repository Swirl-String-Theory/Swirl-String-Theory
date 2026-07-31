#!/usr/bin/env python3
"""Ingest validated v0.8.32 orphaned-normalization endpoint into been_processed."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from _paths import ROOT

from canon_edition import (
    EDITION_CONFIG,
    edition_dir,
    main_tex,
    rt_tex,
    sync_paperkeywords_in_tex,
)

VERSION = "0.8.32"
PREV = "0.8.31"
TODO_PATCHES = ROOT.parent / "to_do_patches"
ZIP_NAME = "SST_CANON-v0.8.31_to_v0.8.32-orphaned-normalization-patch.zip"
ZIP_PATH = TODO_PATCHES / ZIP_NAME
PACKAGE_NAME = "sst_v0.8.31_to_v0.8.32_orphaned_normalization_patch"
PACKAGE = TODO_PATCHES / PACKAGE_NAME
ARCHIVE = ROOT / "sources" / "v0.8.32_orphaned_normalization"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex"


def extract_package() -> Path:
    patched_main = PACKAGE / "patched" / f"SST_CANON-v{VERSION}.tex"
    if PACKAGE.is_dir() and patched_main.is_file():
        print(f"using existing package folder {PACKAGE.name}")
        return PACKAGE
    if not ZIP_PATH.is_file():
        raise SystemExit(f"missing zip: {ZIP_PATH}")
    TODO_PATCHES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(TODO_PATCHES)
    if not patched_main.is_file():
        raise SystemExit(f"extract failed; expected {patched_main}")
    print(f"extracted {ZIP_NAME} -> {PACKAGE.name}")
    return PACKAGE


def ingest_tex(package: Path) -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    patched = package / "patched"
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
        NONRELEASE,
    ):
        src = patched / name
        if not src.is_file():
            if name == NONRELEASE:
                prev = edition_dir(PREV) / NONRELEASE
                if prev.is_file():
                    shutil.copy2(prev, dst / NONRELEASE)
                    print(f"copied {NONRELEASE} from v{PREV}")
                    continue
            raise SystemExit(f"missing finished file: {src}")
        shutil.copy2(src, dst / name)
        print(f"ingested {name}")


def clear_borrowed_doi() -> None:
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
    else:
        print("\\paperdoi already empty / mint-ready")


def seed_zenodo_json() -> None:
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


def write_archive_changelog(archive: Path) -> None:
    text = "\n".join(
        [
            "# SST Canon v0.8.32 — orphaned-normalization changelog",
            "",
            "## Summary",
            "",
            "Orphaned-normalization adjudication and complete rho_f scaling audit",
            "on top of v0.8.31 (phase-2 of the v0.8.31 companion audit).",
            "",
            "## What is new",
            "",
            "1. Removes `7.0e-7 kg m^-3` from the primitive calibration set.",
            "2. Registers `rho_ref` as `[LEGACY REFERENCE NORMALIZATION / PROVENANCE INVALIDATED]`.",
            "3. Leaves physical `rho_f ≡ rho_eff^(0)` numerically unfixed.",
            "4. Records all four VAM-7 provenance defects.",
            "5. Adds A/B/C/Q/X response-scaling audit and source-free radiation no-go.",
            "6. Converts selected absolute amplitudes to legacy-reference benchmarks.",
            "7. Nonrelease speculative appendix remains v0.2 (byte-identical).",
            "",
            "## Deferred",
            "",
            "- v0.8.33: covariant vortex-worldsheet / gauge-certification (separate package)",
            "- Later: Biot–Savart / `F_swirl^max` mechanical-tension protocol",
            "",
        ]
    )
    (archive / "CHANGELOG.md").write_text(text, encoding="utf-8")
    print("wrote CHANGELOG.md")


def move_package_and_zip_to_sources(package: Path) -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_archive_changelog(ARCHIVE)
    for src in (package, ZIP_PATH):
        if not src.exists():
            continue
        dest = ARCHIVE / src.name
        if dest.exists():
            nest = ARCHIVE / "from_to_do_patches"
            nest.mkdir(parents=True, exist_ok=True)
            dest = nest / src.name
        shutil.move(str(src), str(dest))
        print(f"moved {src.name} -> {dest.relative_to(ROOT)}")
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.32 orphaned-normalization ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.32/`.",
                "Patched `.tex` files were taken from `patched/`.",
                "See `CHANGELOG.md` for the edition delta.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing")

    package = extract_package()
    ingest_tex(package)
    clear_borrowed_doi()
    if sync_paperkeywords_in_tex(VERSION):
        print("synced \\paperkeywords from EDITION_KEYWORDS")
    seed_zenodo_json()
    move_package_and_zip_to_sources(package)

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION}")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit(f"missing \\canonversion for {VERSION}")
    if "LEGACY REFERENCE NORMALIZATION" not in text:
        raise SystemExit("orphaned-normalization content missing")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    if PACKAGE.is_dir() or ZIP_PATH.is_file():
        raise SystemExit("package/zip still in to_do_patches after move")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
