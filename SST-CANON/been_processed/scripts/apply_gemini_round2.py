#!/usr/bin/env python3
"""Apply Gemini round-2 audit (vchar/uswirl discipline, delay sign, epistemic labels)."""
import sys
from _paths import ROOT, SCRIPTS_DIR

MARKER = "DERIVED WITHIN CALIBRATION"

MAIN_REPLACEMENTS = [
    (
        "        Empirically:\n        \n        \\begin{align}\n            \\eta_0 \\approx \\frac{\\alpha}{2}\n        \\end{align}\n        \n        \\textbf{[CALIBRATED] Empirical closure}: Within the present canonical calibration, this fixes the characteristic swirl velocity \\emph{from} the fine-structure constant ($\\vnorm=\\alpha c/2$); $\\alpha$ is an input here, not an output.\n\n        \\textbf{[CRITICAL NOTE]} This relation should be read as a calibrated SST closure unless and until it is re-derived from a deeper dynamical sector.",
        "        Within the present calibrated constant chain:\n        \n        \\begin{align}\n            \\eta_0 = \\frac{\\alpha}{2}\n        \\end{align}\n        \n        \\textbf{[DERIVED WITHIN CALIBRATION]}: Once the Compton anchoring relation $\\rc=\\vchar/\\omega_c$ is combined with the electron-radius closure $\\rc=\\alpha\\hbar/(2m_ec)$, the identity $\\vchar=\\alpha c/2$ follows algebraically.\n\n        \\textbf{[CRITICAL NOTE]} This is not an independent derivation of $\\alpha$; $\\alpha$ enters through the adopted electron-radius / core-radius calibration. The status is therefore algebraic-within-calibration, not empirical discovery.",
    ),
    (
        "        \\begin{align}\n            \\rhoE(x) &= \\frac{1}{2}\\rhoF(x)\\,\\norm{\\vswirl(x)}^2 \\\\\n            \\rhoM(x) &= \\frac{\\rhoE(x)}{c^2}\n        \\end{align}\n\n        Using Eq.~\\ref{eq:swirl_clock}, the local Swirl-Clock factor is\n\n        \\begin{align}\n            \\SwirlClock(x) = \\sqrt{1 - \\frac{\\norm{\\vswirl(x)}^2}{c^2}}\n        \\end{align}",
        "        \\begin{align}\n            \\rhoE(x,t) &= \\frac{1}{2}\\rhoF(x,t)\\,\\norm{\\uswirl(x,t)}^2 \\\\\n            \\rhoM(x,t) &= \\frac{\\rhoE(x,t)}{c^2}\n        \\end{align}\n\n        Using Eq.~\\ref{eq:swirl_clock}, the local Swirl-Clock factor is\n\n        \\begin{align}\n            \\SwirlClock(x,t) = \\sqrt{1 - \\frac{\\norm{\\uswirl(x,t)}^2}{c^2}}\n        \\end{align}",
    ),
    (
        "        \\begin{align}\n            M_K(x)\n            &= \\rhoM(x)\\,\\rc^3\\,\\Pi_K\\,\\Xi_K\\,\\SwirlClock(x)^{-2} \\\\\n            &= \\left( \\frac{\\rhoF(x)\\,\\norm{\\vswirl(x)}^2}{2c^2} \\right)\n               \\rc^3\n               \\left( \\frac{\\lambda_c}{\\pi \\rc} \\right)^{G(K)}\n               \\left[ \\alpha_C\\,C(K) + \\beta_L\\,L(K) + \\gamma_H\\,\\mathcal{H}(K) \\right]\n               \\varphi^{-2k(K)}\n               \\SwirlClock(x)^{-2}\n            \\label{eq:sst_master_equation}\n        \\end{align}",
        "        \\begin{align}\n            M_K(x,t)\n            &= \\rhoM(x,t)\\,\\rc^3\\,\\Pi_K\\,\\Xi_K\\,\\SwirlClock(x,t)^{-2} \\\\\n            &= \\left( \\frac{\\rhoF(x,t)\\,\\norm{\\uswirl(x,t)}^2}{2c^2} \\right)\n               \\rc^3\n               \\left( \\frac{\\lambda_c}{\\pi \\rc} \\right)^{G(K)}\n               \\left[ \\alpha_C\\,C(K) + \\beta_L\\,L(K) + \\gamma_H\\,\\mathcal{H}(K) \\right]\n               \\varphi^{-2k(K)}\n               \\SwirlClock(x,t)^{-2}\n            \\label{eq:sst_master_equation}\n        \\end{align}",
    ),
    (
        "            \\left[ \\frac{\\rhoF\\,\\norm{\\vswirl}^2}{c^2} \\rc^3 \\right] = \\mathrm{kg}",
        "            \\left[ \\frac{\\rhoF\\,\\norm{\\uswirl}^2}{c^2} \\rc^3 \\right] = \\mathrm{kg}",
    ),
    (
        "        \\textbf{[CALIBRATED]} The Rydberg constant is recoverable from the three SST primitives without $e$, $\\varepsilon_0$, or $m_e$ appearing \\emph{explicitly}:",
        "        \\textbf{[CALIBRATED IDENTITY]} The Rydberg constant is recoverable from the three SST calibration variables without $e$, $\\varepsilon_0$, or $m_e$ appearing \\emph{explicitly}:",
    ),
    (
        "        This is a benchmark for the internal non-redundancy of the primitive set. \\textbf{[CRITICAL NOTE]} Substituting the canonical definitions $\\vnorm=\\alpha c/2$ and $\\rc=\\vnorm/\\omega_c=\\alpha\\hbar/(2m_ec)$ reduces Eq.~\\eqref{eq:Rydberg_SST} \\emph{exactly} to the standard $R_\\infty=\\alpha^2 m_e c/(4\\pi\\hbar)$ (verified to machine precision): $m_e$ is hidden inside $\\rc$ and $\\alpha$ inside both $\\vnorm$ and $\\rc$. The identity is therefore a consistency check, not an independent non-circular derivation of $R_\\infty$. Combining Eq.~\\eqref{eq:Rydberg_SST} with Eq.~\\eqref{eq:Fmax_def} yields the compact relation",
        "        This is a benchmark for algebraic consistency of the calibration chain, not for independent non-redundancy of the primitive set. \\textbf{[CRITICAL NOTE]} Substituting the canonical definitions $\\vchar=\\alpha c/2$ and $\\rc=\\vchar/\\omega_c=\\alpha\\hbar/(2m_ec)$ reduces Eq.~\\eqref{eq:Rydberg_SST} \\emph{exactly} to the standard $R_\\infty=\\alpha^2 m_e c/(4\\pi\\hbar)$ (verified to machine precision): $m_e$ is hidden inside $\\rc$ and $\\alpha$ inside both $\\vchar$ and $\\rc$. The identity is therefore a consistency check, not an independent non-circular derivation of $R_\\infty$. Combining Eq.~\\eqref{eq:Rydberg_SST} with Eq.~\\eqref{eq:Fmax_def} yields the compact relation",
    ),
    (
        "        Substituting into Eq.~\\ref{eq:delay_phase} yields:\n        \n        \\begin{align}\n            \\Omega = \\omega_0 + \\kappa \\sin(\\Omega \\tau)\n            \\label{eq:mode_condition}\n        \\end{align}\n        \n        This transcendental equation admits a discrete set of stable solutions $\\Omega_n$ determined by the delay parameter $\\tau$.",
        "        Substituting into Eq.~\\ref{eq:delay_phase} yields $\\phi(t-\\tau)-\\phi(t)=-\\Omega\\tau$, hence:\n        \n        \\begin{align}\n            \\Omega = \\omega_0 - \\kappa \\sin(\\Omega \\tau)\n            \\label{eq:mode_condition}\n        \\end{align}\n        \n        This transcendental equation admits a discrete set of stable solutions $\\Omega_n$ determined by the delay parameter $\\tau$. The sign convention is not physically unique---one may absorb it into $\\kappa$ or reverse the delay argument---but the displayed form is the direct consequence of Eq.~\\eqref{eq:delay_phase} as written.",
    ),
    (
        "            \\SwirlClock(x)=\\sqrt{1-\\frac{\\norm{\\vswirl(x)}^2}{c^2}}.",
        "            \\SwirlClock(x,t)=\\sqrt{1-\\frac{\\norm{\\uswirl(x,t)}^2}{c^2}}.",
    ),
    (
        "            Substitution gives the algebraic mode condition\n            \\begin{align}\n                \\Omega = \\omega_0 + \\kappa \\sin(\\Omega\\tau),\n            \\end{align}\n            which admits multiple branches labelled by the effective phase winding across the delay interval.",
        "            Substitution gives the algebraic mode condition\n            \\begin{align}\n                \\Omega = \\omega_0 - \\kappa \\sin(\\Omega\\tau),\n            \\end{align}\n            where the minus sign follows from $\\sin[-\\Omega\\tau]=-\\sin(\\Omega\\tau)$. This admits multiple branches labelled by the effective phase winding across the delay interval.",
    ),
    (
        "            \\textbf{[DERIVED-IN-MODEL / OPEN].}\n            A parameter-light finite-cell variational construction for an ideal trefoil filament\n            yields a leading dimensionless scale",
        "            \\textbf{[BRIDGE ANSATZ / SPECULATIVE FIT].}\n            A parameter-light finite-cell variational construction for an ideal trefoil filament,\n            containing partially open modelling choices, yields a leading dimensionless scale",
    ),
]

RT_REPLACEMENTS = [
    (
        "        the same units as acoustic impedance. This object measures resistance to velocity-driven pressure excitation.",
        "        the same units as acoustic impedance. Here $v_K$ denotes the coarse-grained velocity amplitude of the same mode family $K$ used to define $P_K$; it may be instantiated as a phase-transport speed, local carrier-speed amplitude, or resonant surface-speed amplitude, but the choice must be declared in any benchmark. It is not the canonical scalar speed $\\vchar$ unless the benchmark explicitly specializes to the canonical carrier limit. This object measures resistance to velocity-driven pressure excitation.",
    ),
]


def _vnorm_to_vchar(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        if r"\newcommand{\vnorm}" in line:
            lines.append(line)
        else:
            lines.append(line.replace(r"\vnorm", r"\vchar"))
    return "\n".join(lines)


def _apply_pairs(text: str, pairs: list[tuple[str, str]], strict: bool = False) -> str:
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:100]}...")
    return text


def apply(version: str = "0.8.10") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"Gemini round-2 audit already present in v{version}.")
        return
    mtext = _apply_pairs(mtext, MAIN_REPLACEMENTS, strict=True)
    mtext = _vnorm_to_vchar(mtext)
    rtext = _apply_pairs(rt.read_text(encoding="utf-8"), RT_REPLACEMENTS, strict=True)
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"Gemini round-2 audit applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.10"
    apply(version)


if __name__ == "__main__":
    main()
