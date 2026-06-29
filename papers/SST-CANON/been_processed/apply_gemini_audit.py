#!/usr/bin/env python3
"""Apply Gemini epistemic/notation audit to a canon edition (default v0.8.8)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "Primitive calibration set"

MAIN_REPLACEMENTS = [
    (
        r"\newcommand{\vnorm}{\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert}",
        r"\newcommand{\vnorm}{\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert}"
        + "\n"
        + r"\newcommand{\vchar}{v_{\!\boldsymbol{\circlearrowleft}}^{\ast}}"
        + "\n"
        + r"\newcommand{\uswirl}{\mathbf{u}_{\!\boldsymbol{\circlearrowleft}}}"
        + "\n"
        + r"\newcommand{\omegaswirl}{\boldsymbol{\omega}_{\!\boldsymbol{\circlearrowleft}}}",
    ),
    (
        "        \\textbf{Primitive set:}\n"
        "        \\begin{align}\n"
        "            \\mathcal{P} = \\{ \\rhoF, \\vswirl, \\omega_c \\}\n"
        "        \\end{align}\n"
        "        \n"
        "        where:\n"
        "        \\begin{itemize}\n"
        "            \\item $\\rhoF$ is the effective background fluid density,\n"
        "            \\item $\\vswirl$ is the characteristic swirl velocity,\n"
        "            \\item $\\omega_c$ is the Compton angular frequency.\n"
        "        \\end{itemize}\n"
        "        \n"
        "        \\textbf{[ORTHODOX]}: $\\omega_c = \\frac{m_e c^2}{\\hbar}$ is a standard physical constant.",
        "        \\textbf{Primitive calibration set:}\n"
        "        \\begin{align}\n"
        "            \\mathcal{P}_{\\mathrm{cal}} = \\{ \\rhoF, \\vchar, \\omega_c \\}\n"
        "        \\end{align}\n"
        "        \n"
        "        where:\n"
        "        \\begin{itemize}\n"
        "            \\item $\\rhoF$ is the effective background fluid density,\n"
        "            \\item $\\vchar=\\lVert\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert$ is the canonical characteristic swirl-speed magnitude,\n"
        "            \\item $\\omega_c$ is the Compton angular frequency.\n"
        "        \\end{itemize}\n"
        "\n"
        "        \\textbf{[CANON / NOTATION]}: $\\vchar$ is a calibrated scalar speed. The local swirl-velocity field is denoted\n"
        "        \\begin{align}\n"
        "            \\uswirl(\\mathbf{x},t),\n"
        "            \\qquad\n"
        "            \\omegaswirl(\\mathbf{x},t)=\\nabla\\times\\uswirl(\\mathbf{x},t).\n"
        "        \\end{align}\n"
        "        The symbol $\\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}$ without explicit arguments is reserved for the canonical characteristic carrier velocity; it must not be used as the unrestricted local field in bridge equations.\n"
        "        \n"
        "        \\textbf{[ORTHODOX]}: $\\omega_c = \\frac{m_e c^2}{\\hbar}$ is a standard physical constant.",
    ),
    (
        "        \\textbf{[DERIVED]}: Eq.~\\eqref{eq:chronos_kelvin_clock} is the SST rewriting of the same invariant in terms of the Swirl-Clock.",
        "        \\textbf{[CONDITIONAL DERIVED]}: Eq.~\\eqref{eq:chronos_kelvin_clock} is the SST rewriting of the same invariant in terms of the Swirl-Clock, conditional on evaluating the local tangential speed at the fixed horn/circulation scale $\\rc$. It is not a generic radius-transport theorem for an arbitrary resolved tube radius $a_{\\rm core}(t)$.",
    ),
    (
        "        \\textbf{[DERIVED]}: contraction of a material loop drives stronger clock suppression, while expansion relaxes it.",
        "        \\textbf{[CONDITIONAL DERIVED]}: within the horn-anchored approximation, contraction of a material loop drives stronger clock suppression, while expansion relaxes it.",
    ),
    (
        "        (\\rhoF, \\vswirl, \\omega_c)",
        "        (\\rhoF, \\vchar, \\omega_c)",
    ),
    (
        "            \\item All derived quantities depend only on $\\mathcal{P}$\n"
        "            \\item No external parameters are introduced\n"
        "            \\item The theory is closed under its primitive set",
        "            \\item All derived quantities depend on the stated calibration set, explicit orthodox constants, and explicitly labeled bridge assumptions.\n"
        "            \\item No \\emph{unlabeled} external parameters are introduced.\n"
        "            \\item Quantities fixed by $\\alpha$, $m_e$, $\\hbar$, $c$, $R_\\infty$, or $t_p$ are labeled \\textbf{[CALIBRATED]} rather than independent predictions.",
    ),
    (
        "        \\textbf{[DERIVED]}: Discrete mode selection arises from temporal nonlocality alone.",
        "        \\textbf{[CONDITIONAL DERIVED]}: Given the effective DDE ansatz of Eq.~\\eqref{eq:delay_phase}, the delayed feedback equation admits discrete locked branches. The claim that the SST medium obeys this specific DDE remains a bridge assumption, not a first-principles Euler theorem.",
    ),
    (
        "        \\paragraph{Coupling constant closure.}\n"
        "        The weak gravitational coupling is fixed by the canonical SST constants as",
        "        \\paragraph{Electron-normalized coupling calibration.}\n"
        "        The weak gravitational coupling is written in electron-normalized SST variables as",
    ),
    (
        "        Thus the EM--gravity bridge is not a free-parameter assertion. Its topological electromagnetic impulse is normalized by \\(\\Phi_0=h/(2e)\\), while its weak gravitational closure is normalized by \\(G_{\\mathrm{swirl}}\\).",
        "        Thus the EM--gravity bridge is not an unlabeled free-parameter assertion. However, because \\(t_p\\) already contains \\(G\\) in orthodox units, Eq.~\\eqref{eq:canonical_gswirl_emg_closure} is a \\textbf{[CALIBRATED]} electron-normalized consistency identity unless a future SST sector derives \\(t_p\\) or \\(G_{\\mathrm{swirl}}\\) independently from medium dynamics.",
    ),
    (
        "        \\textbf{[DERIVED]}: it can be used internally to separate writhe-dominated from twist-dominated realizations of the same coarse knot class.\\newline\n"
        "        \\textbf{[SPECULATIVE]}: the mapping from sign$(Tw)$ or related chirality measures to particle/antiparticle sectors remains a model hypothesis.",
        "        \\textbf{[DERIVED BOOKKEEPING]}: once a framed curve is specified, the identity separates writhe and twist contributions.\\newline\n"
        "        \\textbf{[SPECULATIVE]}: the claim that writhe-dominated and twist-dominated realizations are dynamically stable physical isomers, or map to particle/antiparticle sectors, remains a model hypothesis.",
    ),
]

RT_REPLACEMENTS = [
    (
        "\\textbf{[DERIVED]}: it can be used internally to separate writhe-dominated from twist-dominated realizations of the same coarse knot class.\n\n"
        "\\textbf{[SPECULATIVE]}: the mapping from $\\operatorname{sign}(Tw)$ or related chirality measures to particle/antiparticle sectors remains a model hypothesis.",
        "\\textbf{[DERIVED BOOKKEEPING]}: once a framed curve is specified, the identity separates writhe and twist contributions.\n\n"
        "\\textbf{[SPECULATIVE]}: the dynamical stability of writhe-dominated or twist-dominated realizations, and the mapping from $\\operatorname{sign}(Tw)$ or related chirality measures to particle/antiparticle sectors, remains a model hypothesis.",
    ),
    (
        "\\textbf{[DERIVED]}: if two identical electron-candidate loops are forced into the same spatial state, regularization at the physical tube radius $a_{\\rm core}$ yields the overlap penalty\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}(d)\n"
        "    \\approx\n"
        "    \\frac{\\rhoF\\Gamma_0^2}{4\\pi}\n"
        "    \\iint\n"
        "    \\frac{d\\ell_1\\cdot d\\ell_2}{\\sqrt{\\norm{r_1(\\theta_1)-r_2(\\theta_2)+d}^2+a_{\\rm core}^2}},\n"
        "\\end{align}\n"
        "with maximal-overlap scale\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}^{\\max}\n"
        "    \\approx\n"
        "    \\frac{\\rhoF\\Gamma_0^2}{4\\pi}\\left(\\frac{L}{a_{\\rm core}}\\right)\\mathcal{O}(1).\n"
        "\\end{align}\n"
        "\n"
        "Using the canonical values\n"
        "\\begin{align}\n"
        "    \\rhoF &= 7.0\\times 10^{-7}\\ \\mathrm{kg\\,m^{-3}}, \\\\\n"
        "    \\rc &= 1.40897017\\times 10^{-15}\\ \\mathrm{m}, \\\\\n"
        "    \\Gamma_0 &= 2\\pi \\rc\\,\\vnorm \\approx 9.6836\\times 10^{-9}\\ \\mathrm{m^2\\,s^{-1}},\n"
        "\\end{align}\n"
        "and $L\\sim 2\\pi a_0$ at the hydrogenic scale, one obtains the benchmark estimate\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}^{\\max} \\sim 1.23\\times 10^{-18}\\ \\mathrm{J} \\sim 7.6\\ \\mathrm{eV}.\n"
        "\\end{align}\n"
        "\n"
        "\\textbf{[CRITICAL NOTE]}: this is retained as a canonical scale benchmark, not yet as a closed theorem. Its role is to show that the exclusion-energy estimate falls in an atomically relevant window rather than at obviously pathological scales.",
        "\\textbf{[DERIVED]}: if two identical electron-candidate loops are forced into the same spatial state, regularization at a short-distance cutoff $a_{\\rm cut}$ yields the overlap penalty\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}(d)\n"
        "    \\approx\n"
        "    \\frac{\\rhoF\\Gamma_0^2}{4\\pi}\n"
        "    \\iint\n"
        "    \\frac{d\\ell_1\\cdot d\\ell_2}{\\sqrt{\\norm{r_1(\\theta_1)-r_2(\\theta_2)+d}^2+a_{\\rm cut}^2}},\n"
        "\\end{align}\n"
        "with maximal-overlap scale\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}^{\\max}\n"
        "    \\approx\n"
        "    \\frac{\\rhoF\\Gamma_0^2}{4\\pi}\\left(\\frac{L}{a_{\\rm cut}}\\right)\\mathcal{O}(1).\n"
        "\\end{align}\n"
        "\n"
        "Using the canonical values\n"
        "\\begin{align}\n"
        "    \\rhoF &= 7.0\\times 10^{-7}\\ \\mathrm{kg\\,m^{-3}}, \\\\\n"
        "    \\rc &= 1.40897017\\times 10^{-15}\\ \\mathrm{m}, \\\\\n"
        "    \\Gamma_0 &= 2\\pi \\rc\\,\\vnorm \\approx 9.6836\\times 10^{-9}\\ \\mathrm{m^2\\,s^{-1}},\n"
        "\\end{align}\n"
        "and \\(L\\sim 2\\pi a_0\\) at the hydrogenic scale, the legacy benchmark corresponds to the cutoff calibration \\(a_{\\rm cut}=\\rc\\). This does \\emph{not} identify the resolved tube radius \\(a_{\\rm core}\\) with \\(\\rc\\); it only fixes the ultraviolet cutoff used in this benchmark. One obtains\n"
        "\\begin{align}\n"
        "    V_{\\mathrm{Pauli}}^{\\max} \\sim 1.23\\times 10^{-18}\\ \\mathrm{J} \\sim 7.6\\ \\mathrm{eV}.\n"
        "\\end{align}\n"
        "\n"
        "\\textbf{[CRITICAL NOTE]}: this is retained as a cutoff-calibrated scale benchmark, not yet as a closed theorem. Its role is to show that the exclusion-energy estimate falls in an atomically relevant window rather than at obviously pathological scales. A physical resolved-core calculation must use an independently specified \\(a_{\\rm core}\\) or profile model.",
    ),
    ("\\textbf{[DERIVED] Minimal classifier variables:}", "\\textbf{[SPECULATIVE] Classifier variables:}"),
    (
        "\\textbf{[DERIVED] Decision rules (symmetry-first, then stability-filtered):}",
        "\\textbf{[SPECULATIVE] Decision rules (symmetry-first, then stability-filtered):}",
    ),
    ("\\textbf{[DERIVED] Ambiguity tie-break:}", "\\textbf{[CANON WORKFLOW NOTE] Ambiguity tie-break:}"),
    (
        "\\textbf{[DERIVED] Baseline templates and falsifiers:}",
        "\\textbf{[SPECULATIVE] Baseline templates and falsifiers:}",
    ),
    (
        "\\textbf{[DERIVED] Branch-gate decision:} Branch A (legacy profile refine) is selected for current v0.8.x closure because it preserves tested limits while allowing benchmark traceability.",
        "\\textbf{[CANON WORKFLOW NOTE] Branch-gate decision:} Branch A (legacy profile refine) is selected for current v0.8.x closure because it preserves tested limits while allowing benchmark traceability.",
    ),
    (
        "\\textbf{[DERIVED]} probe classes are fixed as astrophysical, laboratory pressure/swirl analog, HV-coil/thrust-inspired, optical/torsional coupling, and null dark-sector tests.",
        "\\textbf{[CANON WORKFLOW NOTE]} probe classes are fixed as astrophysical, laboratory pressure/swirl analog, HV-coil/thrust-inspired, optical/torsional coupling, and null dark-sector tests.",
    ),
    (
        "    \\providecommand{\\vswirl}{\\mathbf{v}_{\\!\\swirlarrow}}",
        "    \\providecommand{\\vswirl}{\\mathbf{v}_{\\!\\swirlarrow}}\n"
        "\\providecommand{\\vchar}{v_{\\!\\boldsymbol{\\circlearrowleft}}^{\\ast}}\n"
        "\\providecommand{\\uswirl}{\\mathbf{u}_{\\!\\boldsymbol{\\circlearrowleft}}}\n"
        "\\providecommand{\\omegaswirl}{\\boldsymbol{\\omega}_{\\!\\boldsymbol{\\circlearrowleft}}}",
    ),
    (
        "        In the dissipative, measurement, or decay sector, reconnection is allowed:\n"
        "        \\[\n"
        "            \\frac{D\\mathcal K}{Dt}\\neq0.\n"
        "        \\]\n"
        "        The helicity budget is written",
        "        In the dissipative, measurement, or decay sector, reconnection is allowed only as a non-ideal event:\n"
        "        \\[\n"
        "            \\frac{D\\mathcal K}{Dt}\\neq0.\n"
        "        \\]\n"
        "        This is not a free creation mechanism. A reconnection claim must state the trigger class, e.g. \\(\\nu_{\\rm eff}>0\\), a boundary injection, a phase-slip singularity, a resolved-core collapse, or an explicit external forcing term.\n"
        "        The helicity budget is written",
    ),
    ("        \\nabla\\times\\vswirl .", "        \\nabla\\times\\uswirl(\\mathbf{x},t) ."),
    ("        \\frac{m_e}{e}\\vswirl,", "        \\frac{m_e}{e}\\uswirl(\\mathbf{x},t),"),
    ("            \\frac{m_e}{e}\\vswirl.", "            \\frac{m_e}{e}\\uswirl(\\mathbf{x},t)."),
    ("    \\frac{m_e}{e}\\vswirl,", "    \\frac{m_e}{e}\\uswirl(\\mathbf{x},t),"),
]


def _apply_replacements(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        if old not in text:
            continue
        text = text.replace(old, new, 1)
    return text


def apply(version: str = "0.8.8") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"Gemini audit already present in v{version}.")
        return
    if r"\newcommand{\vchar}" not in mtext:
        mtext = mtext.replace(
            r"\newcommand{\vnorm}{\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert}",
            r"\newcommand{\vnorm}{\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert}"
            + "\n"
            + r"\newcommand{\vchar}{v_{\!\boldsymbol{\circlearrowleft}}^{\ast}}"
            + "\n"
            + r"\newcommand{\uswirl}{\mathbf{u}_{\!\boldsymbol{\circlearrowleft}}}"
            + "\n"
            + r"\newcommand{\omegaswirl}{\boldsymbol{\omega}_{\!\boldsymbol{\circlearrowleft}}}",
            1,
        )
    mtext = _apply_replacements(mtext, MAIN_REPLACEMENTS[1:])
    if MARKER not in mtext:
        raise SystemExit(f"Gemini audit incomplete in v{version} main canon")
    rtext = _apply_replacements(rt.read_text(encoding="utf-8"), RT_REPLACEMENTS)
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"Gemini audit applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.8"
    apply(version)


if __name__ == "__main__":
    main()
