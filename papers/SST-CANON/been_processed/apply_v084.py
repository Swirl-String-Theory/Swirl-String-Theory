#!/usr/bin/env python3
"""Build v0.8.4 from v0.8.3 copies."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V083 = ROOT / "v0.8.3"
V084 = ROOT / "v0.8.4"
BLOCKS = ROOT / "blocks"

EDITION_V084 = r"""        \subsection{Canon edition notes (v0.8.4)}
            \textbf{v0.8.4} integrates the canonical EM--gravity bridge, finite-cell $\alpha$ obstruction summary, and extended research-track taxonomy blocks.

"""


def bump_version(text: str, ver: str, prev: str) -> str:
    if f"v0.8.4 edition" in text or f"Canon-{ver}" in text:
        return text
    text = text.replace(f"%! {prev} edition:", f"%! {ver} edition:", 1)
    text = text.replace(
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-{prev}}}",
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-{ver}}}",
    )
    text = text.replace(f"Version {prev}\\par", f"Version {ver}\\par")
    text = text.replace(
        rf"\input{{SST_CANON-{prev}-research-track}}",
        rf"\input{{SST_CANON-{ver}-research-track}}",
    )
    return text


def patch_main(text: str) -> str:
    em = (BLOCKS / "em_gravity_canon_block.tex").read_text(encoding="utf-8")
    finite = (BLOCKS / "finite_cell_obstruction_canon_block.tex").read_text(encoding="utf-8")

    unified_anchor = r"%    \section{Unified Interpretation}"
    if "subsec:canonical_em_gravity_closure" not in text:
        text = text.replace(unified_anchor, em + "\n\n" + unified_anchor)
    else:
        # upgrade legacy \input-only integration to inlined block
        text = text.replace(
            r"\input{../blocks/em_gravity_canon_block.tex}" + "\n\n" + unified_anchor,
            em + "\n\n" + unified_anchor,
        )

    open_ladder = r"        \subsection{Open theorem ladder}"
    if "subsec:finite_cell_alpha_obstruction" not in text:
        text = text.replace(open_ladder, finite + open_ladder)

    if "Canon edition notes (v0.8.4)" not in text:
        text = text.replace(
            r"        \subsection{Canon edition notes (v0.8.3)}",
            EDITION_V084 + r"        \subsection{Canon edition notes (v0.8.3)}",
        )

    return bump_version(text, "v0.8.4", "v0.8.3")


def patch_rt(text: str) -> str:
    rt_blocks = (ROOT / "sources" / "research_track_blocks_from_current_conversation.tex").read_text(
        encoding="utf-8"
    )
    anchor = r"\subsection{Hydrodynamic Exchange and the Pauli Barrier}"
    if "subsec:rt_quark_twist_quasi_unknot" not in text:
        text = text.replace(anchor, rt_blocks + "\n\n" + anchor)

    text = text.replace(
        r"\textit{Swirl-String-Theory\_Canon-v0.8.3}",
        r"\textit{Swirl-String-Theory\_Canon-v0.8.4}",
    )
    text = text.replace(
        r"\textbf{Editorial note (v0.8.3):}",
        r"\textbf{Editorial note (v0.8.4):}",
    )
    text = text.replace(
        r"been_processed/v0.8.3/SST_CANON-v0.8.3.tex",
        r"been_processed/v0.8.4/SST_CANON-v0.8.4.tex",
    )
    return bump_version(text, "v0.8.4", "v0.8.3")


def main():
    V084.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V083 / "SST_CANON-v0.8.3.tex", V084 / "SST_CANON-v0.8.4.tex")
    shutil.copy2(
        V083 / "SST_CANON-v0.8.3-research-track.tex",
        V084 / "SST_CANON-v0.8.4-research-track.tex",
    )
    main_path = V084 / "SST_CANON-v0.8.4.tex"
    rt_path = V084 / "SST_CANON-v0.8.4-research-track.tex"
    main_path.write_text(patch_main(main_path.read_text(encoding="utf-8")), encoding="utf-8")
    rt_path.write_text(patch_rt(rt_path.read_text(encoding="utf-8")), encoding="utf-8")
    print("v0.8.4 built.")


if __name__ == "__main__":
    main()
