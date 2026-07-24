#!/usr/bin/env python3
"""Ingest validated v0.8.25 endpoint from clean-patch package into been_processed."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from _paths import ROOT

from canon_edition import EDITION_CONFIG, edition_dir, main_tex, rt_tex

VERSION = "0.8.25"
PREV = "0.8.24"
PACKAGE = ROOT.parent / "to_do_patches" / "SST_CANON-v0.8.25-clean-patch"
ARCHIVE = ROOT / "sources" / "v0.8.25_kam_caged_knot"

ARCHIVE_NAMES = [
    "README_PATCH.md",
    "PATCH_STAT.txt",
    "RELEASE_SCOPE_AUDIT.txt",
    "BUILD_REPORT.txt",
    "SHA256SUMS.txt",
    "SST_CANON-v0.8.25.release.yml",
    "SST_CANON-v0.8.24-to-v0.8.25-clean.diff",
    "SST_CANON-v0.8.24-to-v0.8.25-clean.patch",
    "SST_CANON-v0.8.24-to-v0.8.25-release-only.diff",
    "SST_CANON-v0.8.24-to-v0.8.25-release-only.patch",
    "01-main-canon-kam-interface.diff",
    "02-research-track-kam-module.diff",
    "03-nonrelease-speculative-appendix.diff",
    "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex",
    "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.pdf",
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


def copy_reference_pdf() -> None:
    src = PACKAGE / f"SST_CANON-v{VERSION}.pdf"
    if not src.is_file():
        print("no packaged PDF to copy")
        return
    out = edition_dir(VERSION) / "$out"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out / f"SST_CANON-v{VERSION}.pdf")
    print(f"copied reference PDF -> $out/{src.name}")


def archive_sources() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for name in ARCHIVE_NAMES:
        src = PACKAGE / name
        if src.is_file():
            shutil.copy2(src, ARCHIVE / name)
    readme = ARCHIVE / "INGEST_README.md"
    readme.write_text(
        "\n".join(
            [
                "# v0.8.25 KAM-caged knot-state ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.25/`.",
                "Ingest copies validated release `.tex` files from the clean-patch package.",
                "The speculative appendix `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1` is archived",
                "here only; it is NOT input by the main Canon and is not part of Zenodo release.",
                "Do not `git apply` into been_processed — that would rename/remove v0.8.24.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"archived under {ARCHIVE.relative_to(ROOT)}")


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
        r"\\newcommand\{\\paperdoi\}\{[^}]+\}",
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
    clear_borrowed_doi()
    copy_reference_pdf()
    seed_zenodo_json()
    archive_sources()
    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION} in ingested main tex")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    # Guard: release sources must not pull in non-release appendix
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
