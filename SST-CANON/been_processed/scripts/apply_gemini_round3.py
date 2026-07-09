#!/usr/bin/env python3
"""Apply Gemini round-3 epistemic patch (calibrated identity relabels, Pauli a_cut, galaxy note)."""
import sys
from _paths import ROOT, SCRIPTS_DIR

MARKER = "The cutoff \\(a_{\\rm cut}\\) is not the resolved physical tube radius"

MAIN_REPLACEMENTS = [
    (
        "        \\textbf{[DERIVED WITHIN CALIBRATION]}: Once the Compton anchoring relation $\\rc=\\vchar/\\omega_c$ is combined with the electron-radius closure $\\rc=\\alpha\\hbar/(2m_ec)$, the identity $\\vchar=\\alpha c/2$ follows algebraically.\n\n        \\textbf{[CRITICAL NOTE]} This is not an independent derivation of $\\alpha$; $\\alpha$ enters through the adopted electron-radius / core-radius calibration. The status is therefore algebraic-within-calibration, not empirical discovery.",
        "        \\textbf{[CALIBRATED ALGEBRAIC IDENTITY]}: Once the Compton anchoring relation $\\rc=\\vchar/\\omega_c$ is combined with the electron-radius closure $\\rc=\\alpha\\hbar/(2m_ec)$, the identity $\\vchar=\\alpha c/2$ follows by direct substitution.\n\n        \\textbf{[CRITICAL NOTE]} This is not an independent fluid-dynamical derivation of $\\alpha$ or of the characteristic speed. The fine-structure constant enters through the adopted electron-radius / horn-radius calibration, so the result is a calibrated algebraic identity rather than an emergent theorem.",
    ),
    (
        "        where $\\Omega$ is a coarse-grained local rotation rate and $K$ has dimensions $\\mathrm{kg\\,m^{-3}\\,s}$. This relation records the canonical bridge between a sparse effective bulk density and a high-density horn-envelope normalization; it is not a resolved local-tube density law unless $a_{\\rm core}$ is supplied.\n\n        \\textbf{[DERIVED COROLLARY]}:",
        "        where $\\Omega$ is a coarse-grained local rotation rate and $K$ has dimensions $\\mathrm{kg\\,m^{-3}\\,s}$. This relation records the canonical bridge between a sparse effective bulk density and a high-density horn-envelope normalization; it is not a resolved local-tube density law unless $a_{\\rm core}$ is supplied.\n\n        \\textbf{[CRITICAL NOTE]} Eq.~\\eqref{eq:coarse_grain_density} is not an additional zero-parameter theorem unless the averaging prescription that defines $\\Omega$ is fixed independently of the data being fitted. If $\\Omega$ is chosen phenomenologically, the relation is a bridge ansatz and $K$ is a calibration transfer coefficient, not a new prediction.\n\n        \\textbf{[DERIVED COROLLARY]}:",
    ),
    (
        "        \\textbf{[DERIVED] Canonical form}: substituting $\\vchar = \\omega_c \\rc$ into Eq.~\\eqref{eq:Fmax_def} gives $F_{\\rm swirl}^{\\max} = \\hbar\\omega_c/2\\rc$, the Compton energy scale divided by twice the canonical circulation radius. Numerically, $F_{\\rm swirl}^{\\max} = 29.053507\\;\\text{N}$.",
        "        \\textbf{[CALIBRATED ALGEBRAIC IDENTITY] Canonical form}: substituting $\\vchar = \\omega_c \\rc$ into Eq.~\\eqref{eq:Fmax_def} gives $F_{\\rm swirl}^{\\max} = \\hbar\\omega_c/2\\rc$, the Compton energy scale divided by twice the canonical circulation radius. Numerically, $F_{\\rm swirl}^{\\max} = 29.053507\\;\\text{N}$.",
    ),
    (
        "        \\textbf{[DERIVED] Consistency check}: Eqs.~\\eqref{eq:Fmax_em}--\\eqref{eq:Fmax_rho} are equivalent given $\\vchar = \\alpha c/2$ and the standard identity $e^2/(4\\pi\\varepsilon_0) = \\alpha\\hbar c$. Their mutual agreement constitutes a non-trivial numerical self-consistency test of the primitive set.",
        "        \\textbf{[CALIBRATED ALGEBRAIC IDENTITY] Consistency check}: Eqs.~\\eqref{eq:Fmax_em}--\\eqref{eq:Fmax_rho} are equivalent given $\\vchar = \\alpha c/2$ and the standard identity $e^2/(4\\pi\\varepsilon_0) = \\alpha\\hbar c$. Their mutual agreement is an internal algebraic coherence test of the calibrated chain, not an independent dynamical prediction.",
    ),
    (
        "        \\textbf{[DERIVED]} The ratio of the two tension scales reduces exactly to",
        "        \\textbf{[CALIBRATED ALGEBRAIC IDENTITY]} The ratio of the two tension scales reduces exactly to",
    ),
    (
        "        \\textbf{[SPECULATIVE] Interpretation}: the hierarchy between the electromagnetic and gravitational force scales in SST is not an unexplained numerical coincidence but the ratio of the two fundamental coupling constants of the electron. The structured medium is $\\sim\\!10^{42}$ times stiffer than the space-time geometry at the canonical circulation scale, and this stiffness ratio equals $\\alpha/(4\\alpha_g)$ exactly.",
        "        \\textbf{[SPECULATIVE] Interpretation}: the hierarchy between the electromagnetic and gravitational force scales may be organized by the ratio of the two electron coupling constants. This is an interpretive compression of calibrated constants; by itself it does not prove a new medium-dynamical stiffness law.",
    ),
    (
        "        The three interpretations are collected in Table~\\ref{tab:Fmax_triple}. Together they identify $F_{\\rm swirl}^{\\max}$ as the \\emph{structural tension threshold of the medium}: the scale at which a physical system --- gravitational, electrostatic, or mechanical --- exhausts its capacity to store energy in the current configuration and must either fail topologically, form a horizon, or release energy as radiation.",
        "        The three interpretations are collected in Table~\\ref{tab:Fmax_triple}. Together they organize $F_{\\rm swirl}^{\\max}$ as a \\emph{calibrated structural tension scale}. The table is useful for cross-sector bookkeeping, but the equalities are algebraic consequences of the same calibrated electron-scale constants unless a separate medium-dynamical derivation is supplied.",
    ),
    (
        "          Medium stiffer than spacetime by $\\alpha/4\\alpha_g$ &\n          {[Derived]} \\\\[6pt]",
        "          Calibrated electron-coupling ratio $\\alpha/4\\alpha_g$ &\n          {[Calibrated identity]} \\\\[6pt]",
    ),
    (
        "          Quarter of max.\\ Coulomb force at circulation scale &\n          {[Derived]} \\\\[6pt]",
        "          Quarter of max.\\ Coulomb force at circulation scale &\n          {[Calibrated identity]} \\\\[6pt]",
    ),
    (
        "        \\textbf{[SPECULATIVE] Canonical interpretation}: $F_{\\rm swirl}^{\\max}$ is the tension at which the structured \\ae ther medium reaches its topological integrity limit. It plays the same organisational role for the electromagnetic and mechanical sectors that $F_{\\rm gr}^{\\max} = c^4/4G$ plays for the gravitational sector. Their ratio is precisely the ratio of the two fundamental coupling constants of the electron.",
        "        \\textbf{[SPECULATIVE] Canonical interpretation}: $F_{\\rm swirl}^{\\max}$ is retained as a candidate tension scale for topological integrity of the structured medium. Its comparison with $F_{\\rm gr}^{\\max}=c^4/4G$ is a calibrated electron-normalized analogy, not a theorem that gravitational and electromagnetic stiffness have already been derived from the substrate.",
    ),
    (
        "        \\textbf{[DERIVED]}: Interaction depends on circulation amplitude $\\gamma(r,t)$.",
        "        \\textbf{[BRIDGE ANSATZ]}: This is an orthodox-operator perturbation template whose coefficient depends on the SST circulation amplitude $\\gamma(r,t)$. Because \\(\\hat L_z\\) is imported from the standard quantum Hamiltonian, Eq.~\\eqref{eq:sst_correction} is not a first-principles derivation of quantum angular momentum from the substrate.",
    ),
    (
        """        \\textbf{[DERIVED]} SST bridge: if two identical electron-candidate loops are forced into the same spatial state,
        regularization at the physical tube radius \\(a_{\\rm core}\\) yields the overlap penalty
        \\begin{align}
            V_{\\mathrm{Pauli}}(\\mathbf{d})
            \\approx
            \\frac{\\rho_{\\!f}\\Gamma_0^2}{4\\pi}
            \\oint\\!\\!\\oint
            \\frac{d\\mathbf{l}_1\\cdot d\\mathbf{l}_2}
            {\\sqrt{\\lVert \\mathbf{r}_1(\\theta_1)-\\mathbf{r}_2(\\theta_2)+\\mathbf{d}\\rVert^2+a_{\\rm core}^2}},
            \\label{eq:pauli_barrier_regularized}
        \\end{align}
        with maximal-overlap scale
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}
            \\approx
            \\frac{\\rho_{\\!f}\\Gamma_0^2}{4\\pi}\\left(\\frac{L}{a_{\\rm core}}\\right)\\mathcal{O}(1).
            \\label{eq:pauli_barrier_scale}
        \\end{align}

        Using the canonical values
        \\begin{align}
            \\rho_{\\!f} &= 7.0 \\times 10^{-7}\\ \\mathrm{kg\\,m^{-3}}, \\nonumber\\\\
            r_c &= 1.40897017 \\times 10^{-15}\\ \\mathrm{m}, \\nonumber\\\\
            \\Gamma_0 &= 2\\pi r_c \\lVert \\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}} \\rVert
            \\approx 9.6836\\times 10^{-9}\\ \\mathrm{m^2\\,s^{-1}},
        \\end{align}
        and \\(L \\sim 2\\pi a_0\\) at the hydrogenic scale, the legacy
        benchmark obtained in the closure limit \\(a_{\\rm core}=r_c\\) is
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm core}=r_c)
            \\sim 1.23\\times 10^{-18}\\ \\mathrm{J}
            \\sim 7.6\\ \\mathrm{eV}.
            \\label{eq:pauli_barrier_numeric}
        \\end{align}
        Away from this closure limit the scaling is
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm core})
            \\sim
            V_{\\mathrm{Pauli}}^{\\max}(r_c)
            \\left(\\frac{r_c}{a_{\\rm core}}\\right).
            \\label{eq:pauli_barrier_acore_scaling}
        \\end{align}

        \\textbf{[CRITICAL NOTE]} This is retained as a canonical scale benchmark, not yet as a closed theorem. Its role is
        to show that the exclusion-energy estimate falls in an atomically relevant window rather than at obviously
        pathological scales.

        As written, Eq.~\\eqref{eq:pauli_barrier_numeric} should be interpreted as an order-of-magnitude benchmark attached to the canonical constants and to the closure-limit choice \\(a_{\\rm core}=r_c\\), not yet as a unique parameter-free prediction.""",
        """        \\textbf{[ORTHODOX]} Regularized filament-energy template: if two identical electron-candidate loops are forced into the same spatial state, a short-distance cutoff \\(a_{\\rm cut}\\) gives the overlap penalty
        \\begin{align}
            V_{\\mathrm{Pauli}}(\\mathbf{d};a_{\\rm cut})
            \\approx
            \\frac{\\rho_{\\!f}\\Gamma_0^2}{4\\pi}
            \\oint\\!\\!\\oint
            \\frac{d\\mathbf{l}_1\\cdot d\\mathbf{l}_2}
            {\\sqrt{\\lVert \\mathbf{r}_1(\\theta_1)-\\mathbf{r}_2(\\theta_2)+\\mathbf{d}\\rVert^2+a_{\\rm cut}^2}},
            \\label{eq:pauli_barrier_regularized}
        \\end{align}
        with maximal-overlap scale
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm cut})
            \\approx
            \\frac{\\rho_{\\!f}\\Gamma_0^2}{4\\pi}\\left(\\frac{L}{a_{\\rm cut}}\\right)\\mathcal{O}(1).
            \\label{eq:pauli_barrier_scale}
        \\end{align}

        Using the canonical values
        \\begin{align}
            \\rho_{\\!f} &= 7.0 \\times 10^{-7}\\ \\mathrm{kg\\,m^{-3}}, \\nonumber\\\\
            r_c &= 1.40897017 \\times 10^{-15}\\ \\mathrm{m}, \\nonumber\\\\
            \\Gamma_0 &= 2\\pi r_c \\vchar
            \\approx 9.6836\\times 10^{-9}\\ \\mathrm{m^2\\,s^{-1}},
        \\end{align}
        and \\(L \\sim 2\\pi a_0\\) at the hydrogenic scale, the legacy benchmark corresponds to the cutoff calibration \\(a_{\\rm cut}=r_c\\):
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm cut}=r_c)
            \\sim 1.23\\times 10^{-18}\\ \\mathrm{J}
            \\sim 7.6\\ \\mathrm{eV}.
            \\label{eq:pauli_barrier_numeric}
        \\end{align}
        Away from this cutoff calibration the scaling is
        \\begin{align}
            V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm cut})
            \\sim
            V_{\\mathrm{Pauli}}^{\\max}(r_c)
            \\left(\\frac{r_c}{a_{\\rm cut}}\\right).
            \\label{eq:pauli_barrier_acut_scaling}
        \\end{align}

        \\textbf{[CRITICAL NOTE]} The cutoff \\(a_{\\rm cut}\\) is not the resolved physical tube radius \\(a_{\\rm core}\\).  The benchmark choice \\(a_{\\rm cut}=r_c\\) is retained only as a legacy ultraviolet regularization scale.  It must not be read as \\(a_{\\rm core}=r_c\\), and it is not a theorem-level derivation of Pauli exclusion from ideal Euler dynamics.

        As written, Eq.~\\eqref{eq:pauli_barrier_numeric} is an order-of-magnitude, cutoff-calibrated benchmark attached to the canonical constants. A physical resolved-core calculation must provide \\(a_{\\rm core}\\), the tube profile, and the relation between that profile and \\(a_{\\rm cut}\\) independently.""",
    ),
    (
        "        \\textbf{[SPECULATIVE]} The explicit galaxy-fit profile below is a phenomenological closure ansatz, not a theorem.\n    \n    \\subsection{Effective dark acceleration law}",
        "        \\textbf{[SPECULATIVE]} The explicit galaxy-fit profile below is a phenomenological closure ansatz, not a theorem.\n\n        \\textbf{[CRITICAL NOTE]} The canonical \\(\\rhoF=7.0\\times10^{-7}\\,\\mathrm{kg\\,m^{-3}}\\) is an effective medium parameter, not an ordinary gravitating baryonic/cosmological rest-mass density. Applying it on galactic scales requires a separate coupling and screening law. Without that law, the galaxy-scale pressure profile is a fit ansatz only and must not be interpreted as a literal dense fluid through which stars experience ordinary hydrodynamic drag.\n    \n    \\subsection{Effective dark acceleration law}",
    ),
]

RT_REPLACEMENTS = [
    (
        "\\providecommand{\\rc}{{r_c}}\n\\providecommand{\\vnorm}{\\lVert \\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}} \\rVert}\n\n\\section{Mode-Locked Swirl-Coil Excitation and \\texorpdfstring{$\\vnorm=f\\Delta x$}{v=f dx} Metrology}",
        "\\providecommand{\\rc}{{r_c}}\n\\providecommand{\\vchar}{v_{\\!\\boldsymbol{\\circlearrowleft}}^{\\ast}}\n\\providecommand{\\vnorm}{\\vchar}\n\n\\section{Mode-Locked Swirl-Coil Excitation and \\texorpdfstring{$\\vchar=f\\Delta x$}{v=f dx} Metrology}",
    ),
    (
        "        \\frac{\\lVert \\mathbf{v}_{\\!\\boldsymbol{\\circlearrowleft}}\\rVert}{r_c},",
        "        \\frac{\\vchar}{r_c},",
    ),
    (
        "    has the correct SI units. This use of \\(\\uswirl(\\mathbf{x},t)\\) is intentional: the EM bridge is a local-field bridge, not a curl of the calibrated scalar speed \\(\\vchar\\).\n    \n    The associated magnetic field is then",
        "    has the correct SI units. This use of \\(\\uswirl(\\mathbf{x},t)\\) is intentional: the EM bridge is a local-field bridge, not a curl of the calibrated scalar speed \\(\\vchar\\).\n\n    \\textbf{[CRITICAL NOTE]} Eq.~\\eqref{eq:swirl_vector_potential_bridge} is a constitutive normalization, not a proof that the full nonlinear Euler vorticity dynamics are isomorphic to vacuum Maxwell theory. The bridge is admissible only in a coarse-grained, transverse, weak-response regime where advective and vortex-stretching terms are either projected out, averaged away, or shown to be subleading by an explicit perturbation estimate.\n    \n    The associated magnetic field is then",
    ),
]


def _apply_pairs(text: str, pairs: list[tuple[str, str]], strict: bool = False) -> str:
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:120]}...")
    return text


def apply(version: str = "0.8.12") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"Gemini round-3 epistemic patch already present in v{version}.")
        return
    mtext = _apply_pairs(mtext, MAIN_REPLACEMENTS, strict=True)
    rtext = _apply_pairs(rt.read_text(encoding="utf-8"), RT_REPLACEMENTS, strict=True)
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"Gemini round-3 epistemic patch applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.12"
    apply(version)


if __name__ == "__main__":
    main()
