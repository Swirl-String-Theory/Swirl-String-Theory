#!/usr/bin/env python3
"""Ingest validated v0.8.35 release endpoint from zip into been_processed."""
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
    paperkeywords_tex,
    rt_tex,
    sync_paperkeywords_in_tex,
)

VERSION = "0.8.35"
PREV = "0.8.34"
TODO_PATCHES = ROOT.parent / "to_do_patches"
ZIP_NAME = "SST_CANON-v0.8.35_release_patch.zip"
ZIP_PATH = TODO_PATCHES / ZIP_NAME
PACKAGE_NAME = "SST_CANON-v0.8.35_release_patch"
PACKAGE = TODO_PATCHES / PACKAGE_NAME
REVIEW_NAME = "SST_CANON-v0.8.35_canon_protocol_review.md"
REVIEW_PATH = TODO_PATCHES / REVIEW_NAME
ARCHIVE = ROOT / "sources" / "v0.8.35_transverse_projector_response"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex"


def extract_package() -> Path:
    patched_main = PACKAGE / f"SST_CANON-v{VERSION}.tex"
    if PACKAGE.is_dir() and patched_main.is_file():
        print(f"using existing package folder {PACKAGE.name}")
        return PACKAGE
    if not ZIP_PATH.is_file():
        raise SystemExit(f"missing zip: {ZIP_PATH}")
    PACKAGE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(PACKAGE)
    if not patched_main.is_file():
        raise SystemExit(f"extract failed; expected {patched_main}")
    print(f"extracted {ZIP_NAME} -> {PACKAGE.name}")
    return PACKAGE


def ingest_tex(package: Path) -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
        NONRELEASE,
    ):
        src = package / name
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
        print("cleared borrowed \\paperdoi / %! DOI (Mint will assign)")
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
    data["keywords"] = paperkeywords_tex(VERSION).split(", ")
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"seeded {dst.name} (no deposit_id/doi - Mint via GUI)")


CHANGELOG_TEXT = """# SST Canon v0.8.35 — transverse-projector / finite-core response changelog

**Zenodo (one line):** transverse-projector 8pi/3 origin, alpha-blind finite-core response, helicity-constrained twist energy, and EM matching guards.

## Summary

Release on top of v0.8.34: isotropic transverse-projector origin of the
`8π/3` factor, radius/diameter ropelength conversion, bare-projector and
constant-tube no-gos, alpha-blind finite-core response with `c_L=0`, and
helicity-constrained parity-even twist energy linked to the gauge-emergence
ladder. Nonrelease speculative appendix v0.3 is intentionally unchanged.

## What is new

1. Derives `∫_{S²} t_i (δ_ij − k̂_i k̂_j) t_j dΩ = 8π/3` from spatial isotropy.
2. Separates diameter-normalized `L/D` from radius-normalized `L/a`
   (`(8π/3)(L/D) = (4π/3)(L/a)`).
3. Reclassifies the previous finite-cell mode-count decomposition as historical
   bookkeeping rather than the unique origin of the prefactor.
4. Adds bare-projector and constant-circular-tube-volume no-go results.
5. Adds the alpha-blind finite-core response
   `Δ_micro^(+) = c_κ I_κ² + c_Ω I_Ω² + c_C C_contact + ⋯` with `c_L = 0`.
6. Uses `SL = Wr + Tw` as a helicity-sector constraint.
7. Derives the parity-even twist-energy bound
   `I_Ω² ≥ (4π²)/(L/D) (SL − Wr)²`.
8. Keeps linear helicity in the separate parity-odd / theta-like channel.
9. Links the response to the existing gauge-emergence certification ladder
   before any identification with `α⁻¹`.
10. Adds bend, twist, contact, holdout, cross-representation, cross-knot, and
    final-trefoil calibration gates.

## Numerical convention guard

- High-resolution branch: `L/D = 16.3714672385`, `L/a = 32.7429344770`,
  `Δ = −0.1172840362`.
- Gilbert branch: `L/D = 16.371637`, `L/a = 32.743274`,
  `Δ = −0.1187062268`.
- Branches may not be mixed.

## Protocol review (archived companion)

`SST_CANON-v0.8.35_canon_protocol_review.md` rates the package
**conditionally acceptable / not yet protocol-clean**: compound epistemic
umbrella tags should be decomposed to paragraph-level primary tags
(recommended follow-up: v0.8.35a or v0.8.36). Scientific content and
derivations are acceptable as a guarded research programme; the EM claim
remains open.

## Deferred

- Paragraph-level epistemic tag cleanup (protocol review P1/P2)
- Biot–Savart / `F_swirl^max` mechanical-tension protocol

## Source

- Release zip: `SST_CANON-v0.8.35_release_patch.zip`
- Base: Canon v0.8.34 → `been_processed/v0.8.35/`
- Ingest: `scripts/apply_v0835.py`
"""


def write_changelogs() -> None:
    edition_cl = edition_dir(VERSION) / "CHANGELOG.md"
    edition_cl.write_text(CHANGELOG_TEXT, encoding="utf-8")
    print(f"wrote {edition_cl.relative_to(ROOT)}")


def move_to_sources(package: Path) -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "CHANGELOG.md").write_text(CHANGELOG_TEXT, encoding="utf-8")
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.35 transverse-projector / finite-core response ingest",
                "",
                "Finished release edition lives in `been_processed/v0.8.35/`.",
                "This folder holds the release zip extract, validation artifacts,",
                "and the archived canon-protocol review.",
                "Patched `.tex` files were taken from the release package root.",
                "See `CHANGELOG.md`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for src in (package, ZIP_PATH, REVIEW_PATH):
        if not src.exists():
            continue
        dest = ARCHIVE / src.name
        if dest.exists():
            nest = ARCHIVE / "from_to_do_patches"
            nest.mkdir(parents=True, exist_ok=True)
            dest = nest / src.name
        shutil.move(str(src), str(dest))
        print(f"moved {src.name} -> {dest.relative_to(ROOT)}")


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
    kws = paperkeywords_tex(VERSION)
    if "_" in kws:
        raise SystemExit(f"underscore in paperkeywords: {kws}")
    seed_zenodo_json()
    write_changelogs()
    move_to_sources(package)

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION}")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit(f"missing \\canonversion for {VERSION}")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    for leftover in (PACKAGE, ZIP_PATH, REVIEW_PATH):
        if leftover.exists():
            raise SystemExit(f"still in to_do_patches: {leftover.name}")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
