#!/usr/bin/env python3
"""Shared helpers for SST canon edition copies and metadata bumps."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITION_CONFIG = {
    "0.8.5": {
        "prev": "0.8.4",
        "header": "%! v0.8.5 edition: highres conversation audit + CALIBRATED circularity honesty (been_processed).",
        "note": (
            r"\textbf{v0.8.5} adds the highres conversation audit (Euler discipline, R-to-T bookkeeping, "
            r"twist-ladder research track, horn/envelope wording) and the CALIBRATED circularity-honesty "
            r"relabeling on top of v0.8.4."
        ),
    },
    "0.8.6": {
        "prev": "0.8.5",
        "header": "%! v0.8.6 edition: framed self-linking and spinorial lepton ladder (been_processed).",
        "note": (
            r"\textbf{v0.8.6} adds framed-tube self-linking ($SL=pq$), spinorial $\chi=\pm1$ selection, "
            r"and the lepton ladder (\S\ref{subsec:framed_selflinking_spinorial}) on top of v0.8.5."
        ),
    },
    "0.8.7": {
        "prev": "0.8.6",
        "header": "%! v0.8.7 edition: Z2 spinstats sector and CP1 substrate discipline (been_processed).",
        "note": (
            r"\textbf{v0.8.7} adds the scalar-vs-$\mathbb{C}P^1$ substrate argument, the $\theta=\pi$ "
            r"fermionic $\mathbb{Z}_2$ sector, and supporting bibliography on top of v0.8.6."
        ),
    },
    "0.8.8": {
        "prev": "0.8.7",
        "header": "%! v0.8.8 edition: Gemini epistemic/notation audit (been_processed).",
        "note": (
            r"\textbf{v0.8.8} applies the Gemini audit: primitive calibration notation "
            r"($\mathcal{P}_{\mathrm{cal}}$, $\vchar$, $\uswirl$), conditional Kelvin/DDE labels, "
            r"Pauli $a_{\rm cut}$ disambiguation, and research-track epistemic relabeling on top of v0.8.7."
        ),
    },
    "0.8.9": {
        "prev": "0.8.8",
        "header": "%! v0.8.9 edition: triadic gravity-response corollary and diagnostics (been_processed).",
        "note": (
            r"\textbf{v0.8.9} adds the triadic gravity-response corollary "
            r"(\S\ref{subsec:triadic_gravity_response_corollary}) and research-track flame/caustic/shell "
            r"diagnostics plus atomic condensate closure notes on top of v0.8.8."
        ),
    },
    "0.8.10": {
        "prev": "0.8.9",
        "header": "%! v0.8.10 edition: Gemini round-2 calibration notation audit (been_processed).",
        "note": (
            r"\textbf{v0.8.10} applies the Gemini round-2 audit: canonical speed $\vchar$ vs.\ local "
            r"$\uswirl(x,t)$ discipline, $\eta_0$ algebraic-within-calibration status, delay-equation "
            r"sign convention, Rydberg/finite-cell relabeling, and research-track $v_K$ disambiguation on top of v0.8.9."
        ),
    },
    "0.8.11": {
        "prev": "0.8.10",
        "header": "%! v0.8.11 edition: final notation hygiene pass (been_processed).",
        "note": (
            r"\textbf{v0.8.11} completes the final hygiene pass: consistent $\mathcal{P}_{\mathrm{cal}}$, "
            r"$\vchar$ vs.\ $\uswirl$ usage in EMG, framed self-linking, W-boson sector, and research-track "
            r"numerical bridges on top of v0.8.10."
        ),
    },
    "0.8.12": {
        "prev": "0.8.11",
        "header": "%! v0.8.12 edition: Gemini round-3 epistemic patch (been_processed).",
        "note": (
            r"\textbf{v0.8.12} applies the Gemini round-3 epistemic audit: "
            r"$\mathcal{P}_{\mathrm{cal}}$-aligned identity relabels, coarse-grain density caveat, "
            r"Pauli $a_{\rm cut}$ disambiguation, galaxy-scale $\rhoF$ note, and research-track EM-bridge limits "
            r"on top of v0.8.11."
        ),
    },
}


def edition_dir(version: str) -> Path:
    return ROOT / f"v{version}"


def main_tex(version: str) -> Path:
    return edition_dir(version) / f"SST_CANON-v{version}.tex"


def rt_tex(version: str) -> Path:
    return edition_dir(version) / f"SST_CANON-v{version}-research-track.tex"


def copy_edition(from_version: str, to_version: str) -> None:
    src = edition_dir(from_version)
    dst = edition_dir(to_version)
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(main_tex(from_version), main_tex(to_version))
    shutil.copy2(rt_tex(from_version), rt_tex(to_version))


def _replace_header(text: str, version: str) -> str:
    cfg = EDITION_CONFIG[version]
    for ver, other in EDITION_CONFIG.items():
        if other["header"] in text:
            text = text.replace(other["header"], cfg["header"], 1)
            return text
    marker = "%! v"
    idx = text.find(marker)
    if idx == -1:
        raise ValueError(f"edition header not found for v{version}")
    end = text.find("\n", idx)
    return text[:idx] + cfg["header"] + text[end:]


def apply_metadata(version: str) -> None:
    if version not in EDITION_CONFIG:
        raise ValueError(f"unknown edition {version}")
    cfg = EDITION_CONFIG[version]
    prev = cfg["prev"]

    main = main_tex(version)
    rt = rt_tex(version)
    mtext = main.read_text(encoding="utf-8")
    rtext = rt.read_text(encoding="utf-8")

    mtext = _replace_header(mtext, version)
    mtext = mtext.replace(
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-v{prev}}}",
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-v{version}}}",
    )
    mtext = mtext.replace(f"Version v{prev}\\par", f"Version v{version}\\par")
    mtext = mtext.replace(
        rf"\input{{SST_CANON-v{prev}-research-track}}",
        rf"\input{{SST_CANON-v{version}-research-track}}",
    )

    note_block = (
        f"        \\subsection{{Canon edition notes (v{version})}}\n"
        f"            {cfg['note']}\n\n"
    )
    anchor = f"        \\subsection{{Canon edition notes (v{prev})}}"
    if f"Canon edition notes (v{version})" not in mtext:
        mtext = mtext.replace(anchor, note_block + anchor, 1)

    rtext = rtext.replace(
        rf"%! Companion to Swirl-String-Theory Canon-v{prev} (included from \texttt{{SST\_CANON-v{prev}.tex}} before the manual bibliography).",
        rf"%! Companion to Swirl-String-Theory Canon-v{version} (included from \texttt{{SST\_CANON-v{version}.tex}} before the manual bibliography).",
    )
    rtext = rtext.replace(
        rf"\textit{{Swirl-String-Theory\_Canon-v{prev}}}",
        rf"\textit{{Swirl-String-Theory\_Canon-v{version}}}",
    )
    rtext = rtext.replace(
        rf"\textbf{{Editorial note (v{prev}):}}",
        rf"\textbf{{Editorial note (v{version}):}}",
    )
    rtext = rtext.replace(
        rf"been_processed/v{prev}/SST_CANON-v{prev}.tex",
        rf"been_processed/v{version}/SST_CANON-v{version}.tex",
    )
    rtext = rtext.replace(
        rf"\caption{{Minimal knot-class and analogue summary (v{prev} research-track), aligned with main canon semantic corrections.}}",
        rf"\caption{{Minimal knot-class and analogue summary (v{version} research-track), aligned with main canon semantic corrections.}}",
    )

    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
