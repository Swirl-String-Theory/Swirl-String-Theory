#!/usr/bin/env python3
"""Build/ingest v0.8.33 by re-porting worldsheet package onto v0.8.32 orphaned base."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from _paths import ROOT
from _report_worldsheet_onto_orphaned import write_merged

from canon_edition import (
    EDITION_CONFIG,
    edition_dir,
    main_tex,
    rt_tex,
    sync_paperkeywords_in_tex,
)

VERSION = "0.8.33"
PREV = "0.8.32"
TODO_PATCHES = ROOT.parent / "to_do_patches"
ZIP_NAME = "SST_CANON_v0.8.32_patch_package.zip"
ZIP_PATH = TODO_PATCHES / ZIP_NAME
PACKAGE_NAME = "SST_CANON_v0.8.32_patch_package"
PACKAGE = TODO_PATCHES / PACKAGE_NAME
ARCHIVE = ROOT / "sources" / "v0.8.33_worldsheet_gauge"
NONRELEASE_V3 = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex"


def extract_package() -> Path:
    patched_main = PACKAGE / "patched" / "SST_CANON-v0.8.32.tex"
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


def build_merged_sources(lag_package: Path) -> Path:
    """Merge ingested v0.8.32 + Lagrangian worldsheet → temp dir for 0.8.33."""
    orphaned_src = edition_dir(PREV)
    if not (orphaned_src / "SST_CANON-v0.8.32.tex").is_file():
        raise SystemExit(f"missing ingested v{PREV} main tex")
    lag_patched = lag_package / "patched"
    work = Path(tempfile.mkdtemp(prefix="sst_v0833_merge_"))
    write_merged(orphaned_src, lag_patched, work)
    return work


def ingest_tex(merged_dir: Path, lag_package: Path) -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
    ):
        src = merged_dir / name
        if not src.is_file():
            raise SystemExit(f"missing merged file: {src}")
        shutil.copy2(src, dst / name)
        print(f"ingested {name}")
    nr = lag_package / "patched" / NONRELEASE_V3
    if nr.is_file():
        shutil.copy2(nr, dst / NONRELEASE_V3)
        print(f"ingested {NONRELEASE_V3} (not input by main)")
    else:
        print(f"warning: {NONRELEASE_V3} missing in Lagrangian package")


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
            "# SST Canon v0.8.33 — worldsheet / gauge certification changelog",
            "",
            "## Summary",
            "",
            "Re-port of the Lagrangian recovery package onto the v0.8.32",
            "orphaned-normalization base (not a blind copy of the package's",
            "`patched/` which targeted v0.8.31 without `rho_ref` adjudication).",
            "",
            "## What is new",
            "",
            "1. Covariant vortex-worldsheet form-degree guard (main Canon).",
            "2. Gauge non-derivation / dimension guard (main Canon).",
            "3. Research-Track Kalb–Ramond / two-form worldsheet action.",
            "4. Parity-sensitive helicity-response operator vs chiral alignment.",
            "5. Staged gauge-emergence certification ladder.",
            "6. Nonrelease speculative appendix bumped to v0.3 (Bell/Born programme).",
            "7. Preserves v0.8.32 orphaned-normalization (`rho_ref` legacy; physical",
            "   `rho_eff^(0)` unfixed).",
            "",
            "## Deferred",
            "",
            "- Biot–Savart / `F_swirl^max` mechanical-tension protocol",
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
                "# v0.8.33 worldsheet/gauge ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.33/`.",
                "Built by re-porting this package onto v0.8.32 orphaned base",
                "via `scripts/_report_worldsheet_onto_orphaned.py`.",
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
        raise SystemExit(f"v{PREV} folder missing — run apply_v0832.py first")

    package = extract_package()
    merged = build_merged_sources(package)
    try:
        ingest_tex(merged, package)
    finally:
        shutil.rmtree(merged, ignore_errors=True)

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
        raise SystemExit("orphaned-normalization content missing from v0.8.33")
    if "subsec:covariant_vortex_worldsheet_guard" not in text:
        raise SystemExit("worldsheet guard missing from v0.8.33")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    rt = rt_tex(VERSION).read_text(encoding="utf-8")
    if "sec:rt_covariant_two_form_worldsheet" not in rt:
        raise SystemExit("RT worldsheet section missing")
    if PACKAGE.is_dir() or ZIP_PATH.is_file():
        raise SystemExit("package/zip still in to_do_patches after move")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
