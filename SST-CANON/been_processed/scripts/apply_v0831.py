#!/usr/bin/env python3
"""Ingest v0.8.31 rotor-participation endpoint + archive rho_f scaling audit."""
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

VERSION = "0.8.31"
PREV = "0.8.30"
TODO_PATCHES = ROOT.parent / "to_do_patches"

ROTOR_ZIP_NAME = "SST_CANON-v0.8.30_to_v0.8.31-rotor-participation-patch.zip"
ROTOR_ZIP = TODO_PATCHES / ROTOR_ZIP_NAME
ROTOR_PACKAGE_NAME = "sst_v0.8.30_to_v0.8.31_rotor_participation_patch"
ROTOR_PACKAGE = TODO_PATCHES / ROTOR_PACKAGE_NAME

RHOF_ZIP_NAME = "SST_CANON-v0.8.31-rhof-scaling-audit-phase1.zip"
RHOF_ZIP = TODO_PATCHES / RHOF_ZIP_NAME
RHOF_PACKAGE_NAME = "rhof_scaling_audit_work"
RHOF_PACKAGE = TODO_PATCHES / RHOF_PACKAGE_NAME

ARCHIVE = ROOT / "sources" / "v0.8.31_rotor_participation"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex"


def _extract_zip(zip_path: Path, expected_dir: Path, marker: Path) -> Path:
    """Unzip into to_do_patches if the package folder is not present."""
    if expected_dir.is_dir() and marker.is_file():
        print(f"using existing package folder {expected_dir.name}")
        return expected_dir
    if not zip_path.is_file():
        raise SystemExit(f"missing zip: {zip_path}")
    TODO_PATCHES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(TODO_PATCHES)
    if not marker.is_file():
        raise SystemExit(f"extract failed; expected {marker}")
    print(f"extracted {zip_path.name} -> {expected_dir.name}")
    return expected_dir


def extract_rotor_package() -> Path:
    patched_main = ROTOR_PACKAGE / "patched" / f"SST_CANON-v{VERSION}.tex"
    return _extract_zip(ROTOR_ZIP, ROTOR_PACKAGE, patched_main)


def extract_rhof_package() -> Path:
    readme = RHOF_PACKAGE / "AUDIT_PHASE1.md"
    return _extract_zip(RHOF_ZIP, RHOF_PACKAGE, readme)


def ingest_tex(package: Path) -> None:
    dst = edition_dir(VERSION)
    dst.mkdir(parents=True, exist_ok=True)
    patched = package / "patched"
    for name in (
        f"SST_CANON-v{VERSION}.tex",
        f"SST_CANON-v{VERSION}-research-track.tex",
    ):
        src = patched / name
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


def write_archive_changelog(archive: Path) -> None:
    text = "\n".join(
        [
            "# SST Canon v0.8.31 — rotor participation + rho_f scaling audit",
            "",
            "## Summary",
            "",
            "Two companion packages shipped together as v0.8.31:",
            "",
            "1. **Rotor / participation patch** — finished main + research-track tex",
            "   (source of `been_processed/v0.8.31/`).",
            "2. **rho_f scaling audit, phase 1** — dependency inventory and family",
            "   ledger against the v0.8.31 sources; **no Canon tex edits**.",
            "",
            "Does **not** claim a new numerical derivation of `rho_f`, `J_omega`,",
            "or a new SST primitive.",
            "",
            "## What is new (canon tex — rotor participation)",
            "",
            "1. Defines `rho_f = rho_eff^(0)` exclusively as the isotropic",
            "   quasi-static (`omega->0`, `k->0`) effective-inertia limit.",
            "2. Classifies the compact Compton-gap rotor normalization as a",
            "   matching ansatz / reformulation.",
            "3. Identifies `J_omega^rot` with the horn-envelope line-inertia",
            "   coefficient rather than a new constant.",
            "4. Records `c_omega = v_swirl` as a definitional identity.",
            "5. Separates linear internal twist waves from quadratic Kelvin bending.",
            "6. Quantifies the unresolved participation gap",
            "   `phi_dyn = 5.7229e-26` and diagnostic length",
            "   `ell_rho,eq = 5.8897 mm` (not a predicted physical cell size).",
            "7. Adds a weighted, frequency-dependent macro-response representation",
            "   and explicit promotion gates.",
            "8. Preserves the v0.8.30 density ontology and VAM-7 provenance.",
            "",
            "## Companion (archived only — rho_f scaling audit phase 1)",
            "",
            "- Scans 206 `\\\\rhoF` / `\\\\rho_{\\\\!f}` occurrences (85 main, 121 RT).",
            "- Classifies equation families A/B/C/Q/X under rescaling",
            "  `S_lambda: rho_eff^(0) -> lambda rho_eff^(0)`.",
            "- Provisional verdict: no clean class-C pin of absolute `rho_eff^(0)`;",
            "  `7.0e-7` treated as legacy reference normalization; physical",
            "  quasi-static coefficient remains unfixed pending Q-sector audit.",
            "- Deferred to a later edition: orphaned-normalization patch /",
            "  parameter-budget lemma (phase 2).",
            "",
            "## Epistemic result",
            "",
            "- `rho_f = rho_eff^(0) = 7.0e-7 kg m^-3` remains the calibrated",
            "  quasi-static effective-response number in the published canon,",
            "  with the phase-1 audit archived as companion evidence that a",
            "  clean absolute pin is not yet available.",
            "- `J_omega^rot = pi r_c^2 rho_horn^eff = 2.4282114e-11 kg m^-1`",
            "  is `[REFORMULATION / MATCHING ANSATZ]`.",
            "- Neither `phi_dyn` nor `ell_rho,eq` is promoted to a physical scale.",
            "",
            "## Deferred",
            "",
            "- v0.8.32: preregistered Biot–Savart / mechanical-tension protocol",
            "  for `F_swirl^max`",
            "- rho_f phase 2: detector-level C-trace, Q-sector audit, possible",
            "  orphaned-normalization patch",
            "",
        ]
    )
    (archive / "CHANGELOG.md").write_text(text, encoding="utf-8")
    print("wrote CHANGELOG.md")


def _move_into_archive(src: Path, archive: Path) -> None:
    if not src.exists():
        return
    dest = archive / src.name
    if dest.exists():
        nest = archive / "from_to_do_patches"
        nest.mkdir(parents=True, exist_ok=True)
        dest = nest / src.name
    shutil.move(str(src), str(dest))
    print(f"moved {src.name} -> {dest.relative_to(ROOT)}")


def move_packages_and_zips_to_sources(
    rotor_package: Path,
    rhof_package: Path,
) -> None:
    """Move both zips and extracted packages into sources archive."""
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    write_archive_changelog(ARCHIVE)
    _move_into_archive(rotor_package, ARCHIVE)
    _move_into_archive(ROTOR_ZIP, ARCHIVE)
    _move_into_archive(rhof_package, ARCHIVE)
    _move_into_archive(RHOF_ZIP, ARCHIVE)
    readme = ARCHIVE / "INGEST_README.md"
    readme.write_text(
        "\n".join(
            [
                "# v0.8.31 rotor-participation ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.31/`.",
                "",
                "This folder holds:",
                "",
                "- the rotor-participation zip + extracted patch package",
                "  (`patched/` was the ingest source for the edition `.tex`);",
                "- the companion `rhof_scaling_audit_work` zip + package",
                "  (phase-1 audit only; did not modify Canon sources).",
                "",
                "Do not re-`git apply` into been_processed — that would",
                "rename/remove v0.8.30. Validation PDF from the rotor package",
                "is archival only; Mint/render separately.",
                "Nonrelease appendix copied from v0.8.30 is NOT input by main Canon.",
                "See `CHANGELOG.md` for the edition delta.",
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

    rotor = extract_rotor_package()
    rhof = extract_rhof_package()
    ingest_tex(rotor)
    copy_nonrelease_from_prev()
    clear_borrowed_doi()
    if sync_paperkeywords_in_tex(VERSION):
        print("synced \\paperkeywords from EDITION_KEYWORDS")
    seed_zenodo_json()
    move_packages_and_zips_to_sources(rotor, rhof)

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION} in ingested main tex")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit(f"missing \\canonversion for {VERSION}")
    if not rt_tex(VERSION).is_file():
        raise SystemExit("research-track missing after ingest")
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    for leftover in (ROTOR_PACKAGE, ROTOR_ZIP, RHOF_PACKAGE, RHOF_ZIP):
        if leftover.exists():
            raise SystemExit(f"still in to_do_patches after move: {leftover.name}")
    if not ARCHIVE.exists():
        raise SystemExit(f"archive missing: {ARCHIVE}")
    if not (ARCHIVE / "CHANGELOG.md").is_file():
        raise SystemExit("CHANGELOG.md missing in archive")
    rhof_audit = ARCHIVE / RHOF_PACKAGE_NAME / "AUDIT_PHASE1.md"
    if not rhof_audit.is_file():
        nested = ARCHIVE / "from_to_do_patches" / RHOF_PACKAGE_NAME / "AUDIT_PHASE1.md"
        if not nested.is_file():
            raise SystemExit("rho_f AUDIT_PHASE1.md missing in archive")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
