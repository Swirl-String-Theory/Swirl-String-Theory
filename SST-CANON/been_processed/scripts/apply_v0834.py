#!/usr/bin/env python3
"""Build v0.8.34 by applying ideal-knot-regime patch onto v0.8.33."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from _apply_unified_diff import apply_unified_diff
from _paths import ROOT

from canon_edition import (
    EDITION_CONFIG,
    edition_dir,
    main_tex,
    paperkeywords_tex,
    rt_tex,
    sync_paperkeywords_in_tex,
)

VERSION = "0.8.34"
PREV = "0.8.33"
TODO_PATCHES = ROOT.parent / "to_do_patches"
PATCH_NAME = "SST_CANON-v0.8.31-ideal-knot-regime.patch"
PATCH_PATH = TODO_PATCHES / PATCH_NAME
ARCHIVE = ROOT / "sources" / "v0.8.34_ideal_knot_regime"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex"

EDITION_NOTE = r"""        \subsubsection{v0.8.34}
            \textbf{v0.8.34} adds the regime-of-applicability guard for ideal-knot
            geometry (compact finite-core versus slender-filament diagnostics),
            excludes the compact ideal-knot reference from automatic LIA/KAM
            promotion, records the Moffatt--Ricca single-tube helicity bridge,
            and adds Research-Track compact-to-slender carrier-state and
            Kirchhoff--Cosserat stationary-shape diagnostic sections with
            explicit promotion gates on top of v0.8.33.

"""

HEADER = (
    "%! v0.8.34 edition: ideal-knot regime, compact-to-slender carrier "
    "hypothesis, and Kirchhoff--Cosserat diagnostic guards on top of v0.8.33.\n"
)


def copy_from_prev() -> None:
    src = edition_dir(PREV)
    dst = edition_dir(VERSION)
    if not src.is_dir():
        raise SystemExit(f"v{PREV} folder missing")
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        f"SST_CANON-v{PREV}.tex",
        f"SST_CANON-v{PREV}-research-track.tex",
        NONRELEASE,
    ):
        s = src / name
        if not s.is_file():
            if name == NONRELEASE:
                print(f"no {NONRELEASE} in v{PREV} (skip)")
                continue
            raise SystemExit(f"missing {s}")
        # Copy under previous names first so patch can target renamed files
        if name.endswith("-research-track.tex"):
            dname = f"SST_CANON-v{VERSION}-research-track.tex"
        elif name.startswith("SST_CANON-v"):
            dname = f"SST_CANON-v{VERSION}.tex"
        else:
            dname = name
        shutil.copy2(s, dst / dname)
        print(f"copied {name} -> {dname}")


def rewrite_patch_for_targets(patch_text: str) -> str:
    """Map v0.8.31(2)(1) filenames in the unified diff to v0.8.34 targets."""
    text = patch_text.replace("\r\n", "\n")
    # Main file headers (appear twice as --- and +++)
    text = re.sub(
        r"^(---|\+\+\+)\s+SST_CANON-v0\.8\.31\(2\)\(1\)\.tex\s*$",
        rf"\1 SST_CANON-v{VERSION}.tex",
        text,
        flags=re.M,
    )
    text = re.sub(
        r"^(---|\+\+\+)\s+SST_CANON-v0\.8\.31-research-track\(2\)\(1\)\.tex\s*$",
        rf"\1 SST_CANON-v{VERSION}-research-track.tex",
        text,
        flags=re.M,
    )
    return text


def apply_adapted_patch(adapted: str) -> None:
    apply_unified_diff(adapted, edition_dir(VERSION))


def bump_version_macros() -> None:
    tex = main_tex(VERSION)
    text = tex.read_text(encoding="utf-8")
    text = re.sub(
        r"%! v0\.8\.33 edition:[^\n]*\n",
        HEADER,
        text,
        count=1,
    )
    text = text.replace(
        r"\newcommand{\canonversion}{0.8.33}",
        r"\newcommand{\canonversion}{0.8.34}",
        1,
    )
    text = text.replace(
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.33}",
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.34}",
        1,
    )
    text = re.sub(
        r"\\newcommand\{\\paperdoi\}\{[^}]*\}",
        r"\\newcommand{\\paperdoi}{}",
        text,
        count=1,
    )
    text = re.sub(r"%!\s*DOI\s*=\s*[^\n]+\n?", "", text, count=1)
    text = text.replace(
        r"\input{SST_CANON-v0.8.33-research-track}",
        r"\input{SST_CANON-v0.8.34-research-track}",
        1,
    )
    if r"\subsubsection{v0.8.34}" not in text:
        if r"\subsubsection{v0.8.33}" not in text:
            raise SystemExit("v0.8.33 edition note missing; cannot insert v0.8.34")
        text = text.replace(
            "        \\subsubsection{v0.8.33}\n",
            EDITION_NOTE + "        \\subsubsection{v0.8.33}\n",
            1,
        )
    tex.write_text(text, encoding="utf-8")
    print("bumped main version macros + edition note")

    rt = rt_tex(VERSION)
    rtext = rt.read_text(encoding="utf-8")
    rtext = rtext.replace(
        "Companion to Swirl-String-Theory Canon-v0.8.33",
        "Companion to Swirl-String-Theory Canon-v0.8.34",
    )
    rtext = rtext.replace(
        "Swirl-String-Theory\\_Canon-v0.8.33",
        "Swirl-String-Theory\\_Canon-v0.8.34",
    )
    rtext = rtext.replace("SST\\_CANON-v0.8.33.tex", "SST\\_CANON-v0.8.34.tex")
    rtext = rtext.replace("SST_CANON-v0.8.33.tex", "SST_CANON-v0.8.34.tex")
    rt.write_text(rtext, encoding="utf-8")
    print("bumped research-track companion pointers")


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
    # Sync keywords from edition config (no underscores)
    data["keywords"] = paperkeywords_tex(VERSION).split(", ")
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"seeded {dst.name} (no deposit_id/doi - Mint via GUI)")


def write_archive_and_move_patch() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "CHANGELOG.md").write_text(
        "\n".join(
            [
                "# SST Canon v0.8.34 — ideal-knot regime changelog",
                "",
                "## Summary",
                "",
                "Ideal-knot regime-of-applicability guards and Research-Track",
                "compact-to-slender / Kirchhoff–Cosserat diagnostics on top of v0.8.33.",
                "",
                "## What is new",
                "",
                "1. Main: `subsec:ideal_knot_regime_guard` (compact reference,",
                "   finite-core vs slender diagnostics, Kirchhoff–Cosserat",
                "   non-equivalence, Moffatt–Ricca helicity bridge, use policy).",
                "2. Main: compact-state exclusion from automatic LIA/KAM promotion.",
                "3. Main: helicity bookkeeping points to single-tube Moffatt–Ricca.",
                "4. RT: `subsec:rt_compact_to_slender_state` with promotion gates.",
                "5. RT: `subsec:rt_kirchhoff_cosserat_guard` diagnostic-only bridge.",
                "6. Bibliography: MoffattRicca1992, Fukumoto2007, JohannsEtAl2021",
                "   (+ Mohr2025CODATA in RT).",
                "",
                "## Source",
                "",
                f"- `{PATCH_NAME}` applied onto v0.8.33 → v0.8.34.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.34 ideal-knot-regime ingest (archived)",
                "",
                "Finished release edition lives in `been_processed/v0.8.34/`.",
                "Built by copying v0.8.33 and applying the archived patch.",
                "See `CHANGELOG.md`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if PATCH_PATH.is_file():
        dest = ARCHIVE / PATCH_NAME
        if dest.exists():
            nest = ARCHIVE / "from_to_do_patches"
            nest.mkdir(parents=True, exist_ok=True)
            dest = nest / PATCH_NAME
        shutil.move(str(PATCH_PATH), str(dest))
        print(f"moved {PATCH_NAME} -> {dest.relative_to(ROOT)}")
    print("wrote archive CHANGELOG + INGEST_README")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not PATCH_PATH.is_file():
        raise SystemExit(f"missing patch: {PATCH_PATH}")

    copy_from_prev()

    raw = PATCH_PATH.read_text(encoding="utf-8")
    adapted = rewrite_patch_for_targets(raw)
    apply_adapted_patch(adapted)

    bump_version_macros()
    if sync_paperkeywords_in_tex(VERSION):
        print("synced \\paperkeywords from EDITION_KEYWORDS")
    kws = paperkeywords_tex(VERSION)
    if "_" in kws:
        raise SystemExit(f"underscore in paperkeywords: {kws}")

    seed_zenodo_json()
    write_archive_and_move_patch()

    text = main_tex(VERSION).read_text(encoding="utf-8")
    rt = rt_tex(VERSION).read_text(encoding="utf-8")
    if "subsec:ideal_knot_regime_guard" not in text:
        raise SystemExit("ideal_knot_regime_guard missing from main")
    if "subsec:rt_compact_to_slender_state" not in rt:
        raise SystemExit("rt_compact_to_slender_state missing from RT")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit("edition note missing")
    if f"\\newcommand{{\\canonversion}}{{{VERSION}}}" not in text:
        raise SystemExit("canonversion macro missing")
    if PATCH_PATH.is_file():
        raise SystemExit("patch still in to_do_patches after move")
    print(f"v{VERSION} ingest complete.")


if __name__ == "__main__":
    main()
