#!/usr/bin/env python3
"""Ingest validated v0.8.29 Fermat/optics endpoint from zip into been_processed."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from _paths import ROOT

from canon_edition import EDITION_CONFIG, edition_dir, main_tex, rt_tex

VERSION = "0.8.29"
PREV = "0.8.28"
TODO_PATCHES = ROOT.parent / "to_do_patches"
ZIP_NAME = "SST_CANON-v0.8.29_fermat_optics_patch.zip"
ZIP_PATH = TODO_PATCHES / ZIP_NAME
PACKAGE_NAME = "SST_CANON-v0.8.29_fermat_patch"
PACKAGE = TODO_PATCHES / PACKAGE_NAME
ARCHIVE = ROOT / "sources" / "v0.8.29_fermat_optics"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex"


def extract_package() -> Path:
    """Unzip into to_do_patches if the finished package folder is not present."""
    if PACKAGE.is_dir() and (PACKAGE / f"SST_CANON-v{VERSION}.tex").is_file():
        print(f"using existing package folder {PACKAGE.name}")
        return PACKAGE
    if not ZIP_PATH.is_file():
        raise SystemExit(f"missing zip: {ZIP_PATH}")
    TODO_PATCHES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(TODO_PATCHES)
    if not (PACKAGE / f"SST_CANON-v{VERSION}.tex").is_file():
        raise SystemExit(f"extract failed; expected {PACKAGE / f'SST_CANON-v{VERSION}.tex'}")
    print(f"extracted {ZIP_NAME} -> {PACKAGE.name}")
    return PACKAGE


def ingest_tex(package: Path) -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
    ):
        src = package / name
        if not src.is_file():
            raise SystemExit(f"missing finished file: {src}")
        shutil.copy2(src, dst / name)
        print(f"ingested {name}")


def copy_nonrelease_from_prev() -> None:
    src = edition_dir(PREV) / NONRELEASE
    if not src.is_file():
        print(f"no {NONRELEASE} in v{PREV} (skip)")
        return
    shutil.copy2(src, edition_dir(VERSION) / NONRELEASE)
    print(f"copied {NONRELEASE} from v{PREV} (not input by main)")


def clear_borrowed_doi() -> None:
    """Ensure \\paperdoi is empty so Mint can assign a unique deposit DOI."""
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


def move_package_and_zip_to_sources(package: Path) -> None:
    """Move extracted package and original zip into sources archive."""
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    if package.is_dir():
        dest_pkg = ARCHIVE / package.name
        if dest_pkg.exists():
            nest = ARCHIVE / "from_to_do_patches"
            nest.mkdir(parents=True, exist_ok=True)
            dest_pkg = nest / package.name
        shutil.move(str(package), str(dest_pkg))
        print(f"moved {package.name} -> {dest_pkg.relative_to(ROOT)}")
    if ZIP_PATH.is_file():
        dest_zip = ARCHIVE / ZIP_NAME
        if dest_zip.exists():
            nest = ARCHIVE / "from_to_do_patches"
            nest.mkdir(parents=True, exist_ok=True)
            dest_zip = nest / ZIP_NAME
        shutil.move(str(ZIP_PATH), str(dest_zip))
        print(f"moved {ZIP_NAME} -> {dest_zip.relative_to(ROOT)}")
    readme = ARCHIVE / "INGEST_README.md"
    readme.write_text(
        "\n".join(
            [
                "# v0.8.29 Fermat / optical-mode ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.29/`.",
                "This folder holds the moved zip and extracted patch package.",
                "No packaged PDF was supplied; render after Mint.",
                "Nonrelease appendix copied from v0.8.28 is NOT input by main Canon.",
                "Do not `git apply` into been_processed — that would rename/remove v0.8.28.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {readme.relative_to(ROOT)}")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing")

    package = extract_package()
    ingest_tex(package)
    copy_nonrelease_from_prev()
    clear_borrowed_doi()
    seed_zenodo_json()
    move_package_and_zip_to_sources(package)

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION} in ingested main tex")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit("missing \\canonversion for 0.8.29")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    if PACKAGE.is_dir() or ZIP_PATH.is_file():
        raise SystemExit("package/zip still in to_do_patches after move")
    if not ARCHIVE.exists():
        raise SystemExit(f"archive missing: {ARCHIVE}")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
