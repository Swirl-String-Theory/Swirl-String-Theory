#!/usr/bin/env python3
"""Build v0.8.33 main/RT by re-porting Lagrangian worldsheet hunks onto orphaned v0.8.32."""
from __future__ import annotations

import re
from pathlib import Path


ABSTRACT_ADDON = (
    " Version~0.8.33 additionally fixes the differential-form degree rules for any "
    "covariant vortex-worldsheet description, introduces a guarded parity-sensitive "
    "response interface, and replaces inherited gauge-emergence assertions by an "
    "explicit algebra, representation, anomaly, and phenomenology certification ladder."
)

EDITION_NOTE_0833 = """\
        \\subsubsection{v0.8.33}
            \\textbf{v0.8.33} adds the covariant vortex-worldsheet form-degree
            guard, including the correct distinction between a two-form worldsheet
            coupling and three-form flux integration; introduces a Research-Track
            Kalb--Ramond/worldsheet action with source, scale-separation, and
            reconnection gates; separates a parity-odd kinetic-helicity operator
            from a parity-even chiral-alignment term; and replaces inherited
            director-counting and pure-gauge arguments by a staged gauge-emergence
            certification ladder covering mode census, closure, Jacobi identity,
            representations, charge separation, anomalies, running couplings, and
            out-of-sample phenomenology on top of v0.8.32.

"""

HEADER_0833 = (
    "%! v0.8.33 edition: covariant vortex-worldsheet, chirality-response, and "
    "gauge-certification audit on top of v0.8.32.\n"
)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)


def _extract_between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def _nl(text: str) -> str:
    """Normalize to LF for merge logic; caller may restore CRLF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def merge_main(orphaned_main: str, lag_main: str) -> str:
    out = _nl(orphaned_main)
    lag = _nl(lag_main)

    out = re.sub(r"%! v0\.8\.32 edition:[^\n]*\n", HEADER_0833, out, count=1)
    out = out.replace(
        r"\newcommand{\canonversion}{0.8.32}",
        r"\newcommand{\canonversion}{0.8.33}",
        1,
    )
    out = out.replace(
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.32}",
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.33}",
        1,
    )
    out = out.replace(
        r"\input{SST_CANON-v0.8.32-research-track}",
        r"\input{SST_CANON-v0.8.33-research-track}",
        1,
    )

    marker = "open to falsification."
    _require(marker in out, "abstract end marker missing in orphaned main")
    if "Version~0.8.33 additionally fixes" not in out:
        out = out.replace(marker, marker + ABSTRACT_ADDON, 1)

    ws = _extract_between(
        lag,
        "    \\subsection{Covariant vortex-worldsheet form-degree guard}\n",
        "    \\subsection{Framed self-linking of the swirl string and the spinorial selection of the lepton ladder}\n",
    )
    anchor = (
        "        Topology protects existing closed carriers; it does not by itself provide\n"
        "        an ideal-Euler mechanism for creating them.\n\n"
    )
    _require(anchor in out, "topology-protects anchor missing")
    _require("subsec:covariant_vortex_worldsheet_guard" not in out, "worldsheet already present")
    out = out.replace(anchor, anchor + ws, 1)

    gauge = _extract_between(
        lag,
        "        \\textbf{[CANON TARGET / NON-DERIVATION GUARD].}\n",
        "        A minimal bridge ansatz for the weak mixing angle is\n",
    )
    gauge_anchor = (
        "        with gauge potentials interpreted as holonomy data of "
        "coarse-grained multi-director transport.\n\n"
    )
    _require(gauge_anchor in out, "gauge holonomy anchor missing")
    _require("eq:canon_gauge_dimension_guard" not in out, "gauge guard already present")
    out = out.replace(gauge_anchor, gauge_anchor + gauge, 1)

    _require(r"\subsubsection{v0.8.32}" in out, "orphaned v0.8.32 edition note missing")
    _require(r"\subsubsection{v0.8.33}" not in out, "v0.8.33 note already present")
    out = out.replace(
        "        \\subsubsection{v0.8.32}\n",
        EDITION_NOTE_0833 + "        \\subsubsection{v0.8.32}\n",
        1,
    )

    # Lagrangian patched glues HornNicolis closing onto Wilson on one line; rebuild cleanly.
    bib_block = (
        "            \\bibitem{KalbRamond1974}\n"
        "M.~Kalb and P.~Ramond,\n"
        "\\newblock Classical direct interstring action,\n"
        "\\newblock \\emph{Physical Review D} \\textbf{9} (1974), 2273--2284,\n"
        "\\newblock DOI: \\href{https://doi.org/10.1103/PhysRevD.9.2273}"
        "{10.1103/PhysRevD.9.2273}.\n"
        "\n"
        "\\bibitem{HornNicolisPenco2015}\n"
        "B.~Horn, A.~Nicolis, and R.~Penco,\n"
        "\\newblock Effective string theory for vortex lines in fluids and superfluids,\n"
        "\\newblock \\emph{Journal of High Energy Physics} \\textbf{2015}(10) (2015), 153,\n"
        "\\newblock DOI: \\href{https://doi.org/10.1007/JHEP10(2015)153}"
        "{10.1007/JHEP10(2015)153},\n"
        "\\newblock arXiv: \\href{https://arxiv.org/abs/1507.05635}{1507.05635}.\n"
        "\n"
    )
    wilson = "            \\bibitem{Wilson1974}\n"
    _require(wilson in out, "Wilson1974 bib missing")
    _require(
        r"\bibitem{KalbRamond1974}" not in out,
        "KalbRamond bibitem already in orphaned main",
    )
    _require(r"\bibitem{KalbRamond1974}" in lag, "KalbRamond bibitem missing in Lagrangian main")
    out = out.replace(wilson, bib_block + wilson, 1)

    _require("LEGACY REFERENCE NORMALIZATION" in out, "lost orphaned legacy-ref status")
    _require(r"\rhoRef" in out or "rhoRef" in out, "lost rhoRef macro usage")
    _require("subsec:covariant_vortex_worldsheet_guard" in out, "worldsheet merge incomplete")
    return out


def merge_rt(orphaned_rt: str, lag_rt: str) -> str:
    out = _nl(orphaned_rt)
    lag = _nl(lag_rt)

    out = out.replace(
        "Companion to Swirl-String-Theory Canon-v0.8.32",
        "Companion to Swirl-String-Theory Canon-v0.8.33",
    )
    out = out.replace(
        "Swirl-String-Theory\\_Canon-v0.8.32",
        "Swirl-String-Theory\\_Canon-v0.8.33",
    )
    out = out.replace("SST\\_CANON-v0.8.32.tex", "SST\\_CANON-v0.8.33.tex")
    out = out.replace("SST_CANON-v0.8.32.tex", "SST_CANON-v0.8.33.tex")

    block = _extract_between(
        lag,
        "\\subsection{Research Track: Covariant Two-Form Vortex-Worldsheet Sector}\n",
        "\\subsection{Research Track: Minimal Relational Link--Field Action}\n",
    )
    _require("sec:rt_covariant_two_form_worldsheet" in block, "RT worldsheet block bad")
    _require(
        "sec:rt_gauge_emergence_certification_ladder" in block,
        "gauge ladder missing from RT block",
    )
    _require(
        "sec:rt_covariant_two_form_worldsheet" not in out,
        "RT worldsheet already in orphaned",
    )

    follow = "\\subsection{Research Track: Minimal Relational Link--Field Action}\n"
    _require(follow in out, "link-field subsection missing in orphaned RT")
    out = out.replace(follow, block + follow, 1)

    # RT bibliography inserts (before Taylor1922)
    if "\\bibitem{KalbRamond1974}" in lag and "\\bibitem{KalbRamond1974}" not in out:
        rt_bib = _extract_between(
            lag,
            "\\bibitem{KalbRamond1974}\n",
            "\\bibitem{Taylor1922}\n",
        )
        taylor = "\\bibitem{Taylor1922}\n"
        _require(taylor in out, "Taylor1922 missing in orphaned RT bib")
        out = out.replace(taylor, rt_bib + taylor, 1)

    _require("sec:rt_covariant_two_form_worldsheet" in out, "RT merge failed")
    return out


def write_merged(orphaned_dir: Path, lag_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    om = (orphaned_dir / "SST_CANON-v0.8.32.tex").read_text(encoding="utf-8")
    lm = (lag_dir / "SST_CANON-v0.8.32.tex").read_text(encoding="utf-8")
    ort = (orphaned_dir / "SST_CANON-v0.8.32-research-track.tex").read_text(encoding="utf-8")
    lrt = (lag_dir / "SST_CANON-v0.8.32-research-track.tex").read_text(encoding="utf-8")

    # Preserve CRLF if orphaned sources use it
    nl = "\r\n" if "\r\n" in om else "\n"
    main = merge_main(om, lm).replace("\n", nl)
    rt = merge_rt(ort, lrt).replace("\n", nl)

    (out_dir / "SST_CANON-v0.8.33.tex").write_bytes(main.encode("utf-8"))
    (out_dir / "SST_CANON-v0.8.33-research-track.tex").write_bytes(rt.encode("utf-8"))
    print(f"wrote merged v0.8.33 sources to {out_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: _report_worldsheet_onto_orphaned.py ORPHANED_PATCHED LAG_PATCHED OUT_DIR"
        )
    write_merged(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
