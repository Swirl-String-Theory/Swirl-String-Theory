#!/usr/bin/env python3
"""Apply to_do_patches queue onto v0.8.20 edition files."""
from __future__ import annotations

from _paths import ROOT, SCRIPTS_DIR

SOURCES = ROOT / "sources"
V20 = ROOT / "v0.8.20"
RT = V20 / "SST_CANON-v0.8.20-research-track.tex"
MAIN = V20 / "SST_CANON-v0.8.20.tex"


def extract_hunk(patch_path: Path, target_substr: str) -> str:
    """Extract added lines from the hunk whose --- line contains target_substr."""
    lines = patch_path.read_text(encoding="utf-8").splitlines()
    active = False
    in_hunk = False
    out: list[str] = []
    for line in lines:
        if line.startswith("--- ") and target_substr in line:
            active = True
            in_hunk = False
            out = []
            continue
        if line.startswith("+++ ") and active:
            continue
        if line.startswith("--- ") and active and out:
            break
        if not active:
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if in_hunk:
            if line.startswith("+") and not line.startswith("+++"):
                out.append(line[1:])
            elif line.startswith(" ") or line.startswith("-"):
                continue
    return "\n".join(out).rstrip() + "\n\n"


def insert_once(text: str, anchor: str, block: str, label: str) -> str:
    if label in text:
        print(f"SKIP {label}: already present")
        return text
    if anchor not in text:
        raise SystemExit(f"ANCHOR NOT FOUND for {label}")
    return text.replace(anchor, anchor + block, 1)


def apply_chronos(rt: str) -> str:
    block = extract_hunk(
        SOURCES / "v0.8.20_chronos_kelvin_hitting_conditions.patch",
        "research-track",
    )
    anchor = (
        "    \\mathcal H(K_i)\\neq \\mathcal H(K_{i+1}).\n"
        "\\end{equation}\n\n"
        "\\subsubsection{Dimensionless diagnostic}"
    )
    rt = insert_once(rt, anchor, block, "subsubsec:chronos_kelvin_hitting_conditions")
    return rt


def apply_contact(rt: str) -> str:
    block = extract_hunk(
        SOURCES / "v0.8.20_contact_pressure_saturation.patch",
        "research-track",
    )
    anchor = (
        "for a discrete swirl-stress/contact-force map, not yet canonical physical\n"
        "forces.\n\n"
        "\\subsubsection{Contact-map refinement of the topological kernel}"
    )
    return insert_once(rt, anchor, block, "subsec:rt_contact_pressure_saturation_swirl_clock")


def apply_rank9(main: str, rt: str) -> tuple[str, str]:
    main_block = extract_hunk(
        SOURCES / "v0.8.20_rank9_contact_channels.patch",
        "SST_CANON-v0.8.19.tex",
    )
    main_anchor = (
        "        anomaly cancellation, and realistic mixing matrices remain open work.\n\n"
        "    \\section{Discussion and Limits}"
    )
    main = insert_once(main, main_anchor, main_block, "sec:rt_colored_contact_rank_nine")

    rt_block = extract_hunk(
        SOURCES / "v0.8.20_rank9_contact_channels.patch",
        "research-track",
    )
    rt_anchor = (
        "Small $\\chi_{\\rm contact}$ means that the candidate state is not merely short;\n"
        "it is approximately contact-critical under the declared energy model.\n\n"
        "\\paragraph{Minimal falsifier for this appendix.}"
    )
    # Use unique label check only on RT body, not refs in edition note
    if "\\label{sec:rt_colored_contact_rank_nine}" not in rt:
        if rt_anchor not in rt:
            raise SystemExit("rank9 RT anchor not found")
        rt = rt.replace(rt_anchor, rt_anchor + "\n" + rt_block, 1)

    if "Research-track contact-channel guard" not in main:
        main = insert_once(main, main_anchor, main_block, "Research-track contact-channel guard")
    return main, rt


def apply_ssdl(rt: str) -> str:
    block = (SOURCES / "v0.8.20_ssdl_research_track_block.tex").read_text(encoding="utf-8").rstrip() + "\n\n"
    anchor = (
        "vacuum sector and the local incompressible swirl medium.\n\n"
        "\\subsection{Tensor-speed naturalness}"
    )
    return insert_once(rt, anchor, block, "subsec:ssdl_monopole_dtn")


def apply_particle_clock(rt: str) -> str:
    block = (SOURCES / "v0.8.20_research_track_particle_clock_ansatz_block.tex").read_text(encoding="utf-8").rstrip() + "\n\n"
    anchor = (
        "    \\text{taxonomy refinement required.}\n"
        "\\end{equation}\n\n"
        "% ----------------------------------------------------------\n"
        "% Bibliography entries to merge into the main thebibliography\n"
    )
    return insert_once(rt, anchor, block, "app:research-track")


def main() -> None:
    rt = RT.read_text(encoding="utf-8")
    main_text = MAIN.read_text(encoding="utf-8")

    rt = apply_chronos(rt)
    RT.write_text(rt, encoding="utf-8")
    print("Applied chronos_kelvin")

    rt = apply_contact(rt)
    RT.write_text(rt, encoding="utf-8")
    print("Applied contact_pressure")

    main_text, rt = apply_rank9(main_text, rt)
    MAIN.write_text(main_text, encoding="utf-8")
    RT.write_text(rt, encoding="utf-8")
    print("Applied rank9")

    rt = apply_ssdl(rt)
    RT.write_text(rt, encoding="utf-8")
    print("Applied SSDL")

    rt = apply_particle_clock(rt)
    RT.write_text(rt, encoding="utf-8")
    print("Applied particle_clock_ansatz")


if __name__ == "__main__":
    main()
