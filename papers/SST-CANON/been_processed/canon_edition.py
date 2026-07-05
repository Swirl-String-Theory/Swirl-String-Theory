#!/usr/bin/env python3
"""Shared helpers for SST canon edition copies and metadata bumps."""
from __future__ import annotations

import re
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
    "0.8.13": {
        "prev": "0.8.12",
        "header": "%! v0.8.13 edition: relativity emergence ladder (SR/GR audit) (been_processed).",
        "note": (
            r"\textbf{v0.8.13} adds the relativity-emergence audit: the internal tensor-speed naturalness "
            r"proposition (\S\ref{subsec:tensor_speed_naturalness}, conditional $c_{13}=0$) in the main canon, "
            r"the research-track Relativity Emergence Ladder "
            r"(\S\ref{sec:rt_relativity_emergence_ladder}) separating derivable SR/GR kinematics from the open "
            r"Einstein-dynamics program, and relativity/induced-gravity/cosmology bibliography on top of v0.8.12."
        ),
    },
    "0.8.14": {
        "prev": "0.8.13",
        "header": "%! v0.8.14 edition: core-torsion / two-speed clock discipline (been_processed).",
        "note": (
            r"\textbf{v0.8.14} adds the two-speed clock discipline "
            r"(\S\ref{subsec:two_speed_clock_discipline}: $\vchar$ vs.\ $c$, NLSE core sound speed "
            r"$c_s=\vchar/\sqrt{2}$, research-track gate), the $\alpha$-gate guard on $\lambda_c/(\pi\rc)=4/\alpha$, "
            r"and the research-track core--torsion impedance-matching lemma "
            r"(\S\ref{sec:rt_core_torsion_impedance_matching}) on top of v0.8.13."
        ),
    },
    "0.8.15": {
        "prev": "0.8.14",
        "header": "%! v0.8.15 edition: Lorentz-type swirl-stress / EM correspondence (been_processed).",
        "note": (
            r"\textbf{v0.8.15} adds the canon hydrodynamic Lorentz-type swirl-force density "
            r"(\S\ref{sec:lorentz_type_force_density_as_swirl_stress}: Bernoulli tie, loop observables, "
            r"calibrated scales) and the research-track EM-to-swirl correspondence with "
            r"$\lambda_{\mathrm{EM}\to\circlearrowleft}$, SST-44 stress closure, and pending "
            r"$\mathbf f_{\mathrm{link}}$ (\S\ref{sec:research_em_to_swirl_force_density_correspondence}) "
            r"on top of v0.8.14."
        ),
    },
    "0.8.16": {
        "prev": "0.8.15",
        "header": "%! v0.8.16 edition: pressure-optical locking and no-monopole audit (been_processed).",
        "note": (
            r"\textbf{v0.8.16} adds the pressure--optical locking relation "
            r"(Eq.~\ref{eq:canonical_pressure_optical_locking}) in the Triadic Gravity-Response Corollary, "
            r"the research-track no-monopole transport-stress audit "
            r"(\S\ref{sec:rt_no_monopole_transport_stress_audit}), and the relativity falsifier ladder "
            r"on top of v0.8.15. SST-73 receives matching critical notes on Candidate C and "
            r"$[\alpha_{\grav}]=\mathrm{s^2}$."
        ),
    },
    "0.8.17": {
        "prev": "0.8.16",
        "header": "%! v0.8.17 edition: T-foliation discipline and corpus integration bundle (been_processed).",
        "note": (
            r"\textbf{v0.8.17} adds the T-foliation versus local Swirl-Clock remark "
            r"(Eq.~\ref{eq:absolute_T_local_tau_layers}), the ropelength/trefoil-$\alpha$ convention guard, "
            r"Route-I SST-63/23/56 integration in the research track, and aligned updates in SST-73, SST-63, "
            r"SST-64 v2, and SST-34 on top of v0.8.16."
        ),
    },
    "0.8.18": {
        "prev": "0.8.17",
        "header": "%! v0.8.18 edition: guardrails v2 + resolved-tube v3 + four-insights v2 + euler transport + time ontology + compton-horn + hybrid clock (been_processed).",
        "note": (
            r"\textbf{v0.8.18} adds calibration-chain guardrails (rc/$\alpha$ gates, kernel normalization, "
            r"EM prefactor, $\rhohorn$ baseline fix), research-track observational falsifier bounds, orthodox "
            r"resolved-tube reach/thickness definitions, the four topology/stability research appendices, "
            r"the research-track knot-energy normal form with $I_G$ scalarization, Euler/Magnus probe-transport "
            r"polish, canonical time ontology with no-bare-$\tau$ policy, golden-layer hyperbolic rapidity guards, "
            r"Planck-suppressed $F_{\rm swirl}^{\max}$ reparameterization, Compton--horn $G_{\mathrm{swirl}}$ "
            r"reduction guard and balance-angle diagnostic, hybrid density-source Swirl-Clock benchmark, "
            r"and the contact-stress geometry research appendix on top of v0.8.17."
        ),
    },
}

CANON_BASE_KEYWORDS: list[str] = [
    "Swirl String Theory",
    "SST",
    "Canon",
    "Topological Hydrodynamics",
    "Knot Theory",
    "Relational Time",
    "Delay Dynamics",
    "Epistemic Classification",
]

EDITION_KEYWORDS: dict[str, list[str]] = {
    "0.8.2": ["circulation radius", "envelope density"],
    "0.8.3": ["framed-tube ontology", "trefoil closure", "particle dictionary"],
    "0.8.4": ["EM-gravity bridge", "fine-structure constant"],
    "0.8.5": ["circularity audit", "calibrated inputs"],
    "0.8.6": ["framed self-linking", "spinorial lepton ladder"],
    "0.8.7": ["Z2 spinstats", "CP1 substrate"],
    "0.8.8": ["epistemic notation", "calibration scales"],
    "0.8.9": ["triadic gravity response", "research track"],
    "0.8.10": ["swirl clock", "vchar discipline"],
    "0.8.11": ["notation hygiene", "EMG correspondence"],
    "0.8.12": ["Pauli exclusion", "galaxy rotation curve"],
    "0.8.13": ["relativity emergence", "SR GR audit"],
    "0.8.14": ["two-speed clock", "alpha gate", "impedance matching"],
    "0.8.15": ["Lorentz-type swirl stress", "EM-swirl correspondence", "SST-44"],
    "0.8.16": ["pressure-optical locking", "no-monopole audit", "relativity falsifier"],
    "0.8.17": [
        "T-foliation",
        "ropelength convention",
        "vacuum dual medium",
        "research track corpus",
    ],
    "0.8.18": [
        "calibration guardrails",
        "kernel normalization",
        "Einstein-Aether falsifiers",
        "resolved tube",
        "contact-stress geometry",
        "compton horn balance angle",
        "hybrid density source swirl clock",
    ],
}


def canon_keywords(version: str) -> list[str]:
    """Merge base + edition keywords, deduplicated (case-insensitive)."""
    seen: set[str] = set()
    out: list[str] = []
    for kw in CANON_BASE_KEYWORDS + EDITION_KEYWORDS.get(version, []):
        key = kw.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(kw.strip())
    return out


def paperkeywords_tex(version: str) -> str:
    """Comma-separated keywords for \\paperkeywords macro."""
    return ", ".join(canon_keywords(version))


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

    companion_line = (
        f"%! Companion to Swirl-String-Theory Canon-v{version} "
        f"(included from \\texttt{{SST\\_CANON-v{version}.tex}} before the manual bibliography)."
    )
    rtext = re.sub(
        r"%! Companion to Swirl-String-Theory Canon-v[^\n]+",
        companion_line,
        rtext,
        count=1,
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

    keywords = paperkeywords_tex(version)
    mtext = re.sub(
        r"\\newcommand\{\\paperkeywords\}\{[^}]*\}",
        rf"\\newcommand{{\\paperkeywords}}{{{keywords}}}",
        mtext,
        count=1,
    )

    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")


def sync_paperkeywords_in_tex(version: str) -> bool:
    """Update \\paperkeywords in an edition's main tex file."""
    tex = main_tex(version)
    if not tex.is_file():
        return False
    text = tex.read_text(encoding="utf-8")
    keywords = paperkeywords_tex(version)
    new_text, n = re.subn(
        r"\\newcommand\{\\paperkeywords\}\{[^}]*\}",
        rf"\\newcommand{{\\paperkeywords}}{{{keywords}}}",
        text,
        count=1,
    )
    if n == 0:
        return False
    tex.write_text(new_text, encoding="utf-8")
    return True


def sync_all_paperkeywords() -> list[str]:
    """Update \\paperkeywords for every v0.8.xx edition folder with a main tex file."""
    updated: list[str] = []
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or not re.match(r"^v0\.8\.\d+$", folder.name):
            continue
        version = folder.name.lstrip("v")
        if sync_paperkeywords_in_tex(version):
            updated.append(version)
    return updated


if __name__ == "__main__":
    synced = sync_all_paperkeywords()
    print(f"Updated paperkeywords in {len(synced)} editions: {', '.join(synced)}")
