#!/usr/bin/env python3
"""Build v0.8.3 from v0.8.2 copies (diff-fidelity)."""
import shutil
from _paths import ROOT, SCRIPTS_DIR

V082 = ROOT / "v0.8.2"
V083 = ROOT / "v0.8.3"
BLOCKS = ROOT / "blocks"

OLD_PARTICLE = r"""    \subsection{Particle-Candidate Mapping Layer}
        \label{subsec:integration_knotmap}

        \textbf{[SPECULATIVE]} Working dictionary: a minimal knot / composition mapping retained from earlier SST work is summarized
        in Table~\ref{tab:particle_candidate_mapping}. This table is organizational rather than definitive; it records
        the current topological assignments used by the mass and taxonomy program.

        \begin{table}[h]
        \centering
        \caption{Minimal knot-class to particle-candidate summary retained in v0.8.1.}
        \label{tab:particle_candidate_mapping}
        \begin{tabular}{lll}
        \hline
        Knot class / composition & Candidate & Status / role \\
        \hline
        $3_1$ & electron & baseline lepton calibration \\
        $T(2,5)$ or equivalent higher torus class & muon & lepton hierarchy candidate \\
        $T(2,7)$ or equivalent higher torus class & tau & lepton hierarchy candidate \\
        $5_2 + 5_2 + 6_1$ & proton & composite baryon candidate \\
        analogous nearby composite class & neutron & composite baryon candidate \\
        \hline
        \end{tabular}
        \end{table}

        \textbf{[CRITICAL NOTE]} Table~\ref{tab:particle_candidate_mapping} is a working dictionary only. A full canonical
        assignment requires an explicit invariant set and a mass-functional comparison program.
"""

NEW_PARTICLE_BLOCK = (BLOCKS / "framed_tube_particle_v083.tex").read_text(encoding="utf-8")

PAULI_OLD = r"""        \textbf{[DERIVED]} SST bridge: if two identical electron-candidate loops are forced into the same spatial state,
        regularization at the core radius \(r_c\) yields the overlap penalty
        \begin{align}
            V_{\mathrm{Pauli}}(\mathbf{d})
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}
            \oint\!\!\oint
            \frac{d\mathbf{l}_1\cdot d\mathbf{l}_2}
            {\sqrt{\lVert \mathbf{r}_1(\theta_1)-\mathbf{r}_2(\theta_2)+\mathbf{d}\rVert^2+r_c^2}},
            \label{eq:pauli_barrier_regularized}
        \end{align}
        with maximal-overlap scale
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}\left(\frac{L}{r_c}\right)\mathcal{O}(1).
            \label{eq:pauli_barrier_scale}
        \end{align}

        Using the canonical values
        \begin{align}
            \rho_{\!f} &= 7.0 \times 10^{-7}\ \mathrm{kg\,m^{-3}}, \nonumber\\
            r_c &= 1.40897017 \times 10^{-15}\ \mathrm{m}, \nonumber\\
            \Gamma_0 &= 2\pi r_c \lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert
            \approx 9.6836\times 10^{-9}\ \mathrm{m^2\,s^{-1}},
        \end{align}
        and \(L \sim 2\pi a_0\) at the hydrogenic scale, one obtains the benchmark estimate
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}
            \sim 1.23\times 10^{-18}\ \mathrm{J}
            \sim 7.6\ \mathrm{eV}.
            \label{eq:pauli_barrier_numeric}
        \end{align}

        \textbf{[CRITICAL NOTE]} This is retained as a canonical scale benchmark, not yet as a closed theorem. Its role is
        to show that the exclusion-energy estimate falls in an atomically relevant window rather than at obviously
        pathological scales.

        As written, Eq.~\eqref{eq:pauli_barrier_numeric} should be interpreted as an order-of-magnitude benchmark attached to the canonical constants, not yet as a unique parameter-free prediction.
"""

PAULI_NEW = r"""        \textbf{[DERIVED]} SST bridge: if two identical electron-candidate loops are forced into the same spatial state,
        regularization at the physical tube radius \(a_{\rm core}\) yields the overlap penalty
        \begin{align}
            V_{\mathrm{Pauli}}(\mathbf{d})
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}
            \oint\!\!\oint
            \frac{d\mathbf{l}_1\cdot d\mathbf{l}_2}
            {\sqrt{\lVert \mathbf{r}_1(\theta_1)-\mathbf{r}_2(\theta_2)+\mathbf{d}\rVert^2+a_{\rm core}^2}},
            \label{eq:pauli_barrier_regularized}
        \end{align}
        with maximal-overlap scale
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}\left(\frac{L}{a_{\rm core}}\right)\mathcal{O}(1).
            \label{eq:pauli_barrier_scale}
        \end{align}

        Using the canonical values
        \begin{align}
            \rho_{\!f} &= 7.0 \times 10^{-7}\ \mathrm{kg\,m^{-3}}, \nonumber\\
            r_c &= 1.40897017 \times 10^{-15}\ \mathrm{m}, \nonumber\\
            \Gamma_0 &= 2\pi r_c \lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}} \rVert
            \approx 9.6836\times 10^{-9}\ \mathrm{m^2\,s^{-1}},
        \end{align}
        and \(L \sim 2\pi a_0\) at the hydrogenic scale, the legacy
        benchmark obtained in the closure limit \(a_{\rm core}=r_c\) is
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}(a_{\rm core}=r_c)
            \sim 1.23\times 10^{-18}\ \mathrm{J}
            \sim 7.6\ \mathrm{eV}.
            \label{eq:pauli_barrier_numeric}
        \end{align}
        Away from this closure limit the scaling is
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}(a_{\rm core})
            \sim
            V_{\mathrm{Pauli}}^{\max}(r_c)
            \left(\frac{r_c}{a_{\rm core}}\right).
            \label{eq:pauli_barrier_acore_scaling}
        \end{align}

        \textbf{[CRITICAL NOTE]} This is retained as a canonical scale benchmark, not yet as a closed theorem. Its role is
        to show that the exclusion-energy estimate falls in an atomically relevant window rather than at obviously
        pathological scales.

        As written, Eq.~\eqref{eq:pauli_barrier_numeric} should be interpreted as an order-of-magnitude benchmark attached to the canonical constants and to the closure-limit choice \(a_{\rm core}=r_c\), not yet as a unique parameter-free prediction.
"""

BIB_INSERT = r"""
            \bibitem{Rolfsen1976}
            D.~Rolfsen,
            \newblock \emph{Knots and Links},
            \newblock Publish or Perish (1976); AMS Chelsea reprint (2003).

            \bibitem{Conway1970}
            J.~H.~Conway,
            \newblock An enumeration of knots and links, and some of their algebraic properties,
            \newblock in \emph{Computational Problems in Abstract Algebra}, Pergamon Press (1970), pp.~329--358,
            \newblock DOI: 10.1016/B978-0-08-012975-4.50034-5.
"""

BIB_KIDA = r"""
            \bibitem{KidaTakaoka1994}
            S.~Kida and M.~Takaoka,
            \newblock Vortex reconnection,
            \newblock Annual Review of Fluid Mechanics \textbf{26} (1994), 169--189,
            \newblock DOI: 10.1146/annurev.fl.26.010194.001125.

            \bibitem{KoplikLevine1993}
            J.~Koplik and H.~Levine,
            \newblock Vortex reconnection in superfluid helium,
            \newblock Physical Review Letters \textbf{71} (1993), 1375--1378,
            \newblock DOI: 10.1103/PhysRevLett.71.1375.
"""

STATE_TAXONOMY = r"""        \subsection{State-transition taxonomy from the trefoil-closure discussion}
            The present conversation also fixes a useful state-transition taxonomy:
            \begin{align}
                \text{smooth deformation/binding} &: K=3_1\ \text{preserved},\\
                \text{R-to-T closure/nucleation} &: K\ \text{created at a boundary event},\\
                \text{annihilation or weak capture} &: K\ \text{converted with compensation}.
            \end{align}
            This taxonomy prevents ordinary atomic binding, non-Euler closure,
            and true particle conversion from being conflated.

"""

TREFOIL_APPENDIX = r"""        \subsection{Trefoil closure and persistence discipline}
            The project-level conclusion is that electron-trefoil creation, if
            retained, must be formulated as a boundary-supported R-to-T closure
            event rather than as ordinary reconnection of an already closed
            ideal-Euler vortex tube. The canon distinction is therefore
            \begin{align}
                \text{pre-closure R-phase support}
                &\xrightarrow{\mathcal{K}_{\rm Kairos}}
                \text{closed }3_1\text{ carrier},\\
                \text{closed }3_1\text{ carrier}
                &\xrightarrow{\rm smooth\ Euler}
                \text{same knot class }3_1 .
            \end{align}
            This keeps the orthodox frozen-in topology constraint intact while
            preserving the SST closure program as a clearly labeled bridge.

            The radius notation is correspondingly split into the local tube
            radius \(a_{\rm core}\), the neutral circulation radius \(\rc\), and
            the classical electron envelope radius \(r_e=2\rc\):
            \begin{align}
                a_{\rm core} \neq \rc,
                \qquad
                r_e=2\rc .
            \end{align}
            Ordinary atomic binding changes the phase envelope of the carrier,
            not its knot class:
            \begin{align}
                e^-_{\rm atom}
                =
                3_1^{\rm core}\otimes\Psi_{n\ell m\sigma}^{\rm envelope} .
            \end{align}

"""

EDITION_V083 = r"""        \subsection{Canon edition notes (v0.8.3)}
            \textbf{v0.8.3} integrates framed-tube ontology, attachment gate, trefoil closure discipline, updated particle dictionary, and Pauli $a_{\rm core}$ regularization per conversation, highres, and trefoil diffs.

"""


def bump_version(text: str, ver: str, prev: str) -> str:
    text = text.replace(
        f"%! {prev} edition:",
        f"%! {ver} edition:",
        1,
    )
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
    twist = (BLOCKS / "twist_ladder_euler.tex").read_text(encoding="utf-8")
    em_blocks = (BLOCKS / "rt_trefoil_em_blocks.tex").read_text(encoding="utf-8")
    persist = (BLOCKS / "electron_trefoil_persistence.tex").read_text(encoding="utf-8")

    sym_gate = (
        r"            \text{symmetry gate} \;\to\; \text{helicity balance gate} \;\to\; \text{stability gate}."
    )
    if "subsec:twist_ladder_closure_convention" not in text:
        text = text.replace(
            sym_gate + "\n        ]\n\n\\section{Swirl--Electromagnetic Bridge}",
            sym_gate + "\n        ]\n\n" + twist + "\n\\section{Swirl--Electromagnetic Bridge}",
        )

    photon_anchor = (
        r"        \textbf{[SPECULATIVE]}: handedness of the local torsional packet is taken to encode polarization, while additional azimuthal phase winding encodes orbital angular momentum.\n\n    \subsection{Swirl pressure law}"
    )
    if "subsec:rt_trefoil_closure_bridge" not in text:
        text = text.replace(
            photon_anchor,
            r"        \textbf{[SPECULATIVE]}: handedness of the local torsional packet is taken to encode polarization, while additional azimuthal phase winding encodes orbital angular momentum."
            + em_blocks
            + r"\n    \subsection{Swirl pressure law}",
        )

    softcore_anchor = (
        r"        In particular, Eq.~\eqref{eq:softcore_potential} is retained as a bridge ansatz only. It is not promoted here to the primary atomic potential.\n\n    \subsection{SST Circulation Correction}"
    )
    radius_rule = r"""
        \textbf{[RADIUS USE RULE].}
        The \(r_c\) appearing in Eq.~\eqref{eq:softcore_potential} is an
        envelope-scale softening length for the neutral circulation response. It
        is not the microscopic tube cutoff. Local tube-overlap, reconnection, or
        filament self-energy calculations use \(a_{\rm core}\) instead.

"""
    if "[RADIUS USE RULE]" not in text:
        text = text.replace(
            softcore_anchor,
            r"        In particular, Eq.~\eqref{eq:softcore_potential} is retained as a bridge ansatz only. It is not promoted here to the primary atomic potential."
            + radius_rule
            + r"    \subsection{SST Circulation Correction}",
        )

    branch_anchor = (
        r"        where an axial displacement field $\xi$ generates local vorticity, the vorticity sources azimuthal swirl, and the loop circulation is normalized by the canonical quantum $\Gamma_0$. This makes the circulation amplitude $\gamma$ the natural canon-level coupling variable rather than a free phenomenological insertion.\n    \n    \subsection{Branch Structure}"
    )
    if "subsec:electron_trefoil_persistence_atomic_binding" not in text:
        text = text.replace(
            branch_anchor,
            r"        where an axial displacement field $\xi$ generates local vorticity, the vorticity sources azimuthal swirl, and the loop circulation is normalized by the canonical quantum $\Gamma_0$. This makes the circulation amplitude $\gamma$ the natural canon-level coupling variable rather than a free phenomenological insertion."
            + persist
            + r"\n    \subsection{Branch Structure}",
        )

    if OLD_PARTICLE in text:
        text = text.replace(OLD_PARTICLE, NEW_PARTICLE_BLOCK)
    else:
        raise SystemExit("OLD_PARTICLE block not found")

    if PAULI_OLD in text:
        text = text.replace(PAULI_OLD, PAULI_NEW)
    else:
        raise SystemExit("PAULI block not found")

    dual_vac = r"        \subsection{Dual-vacuum and photon sector status}"
    if "State-transition taxonomy" not in text:
        text = text.replace(
            dual_vac,
            STATE_TAXONOMY + dual_vac,
        )

    open_ladder = r"        \subsection{Open theorem ladder}"
    if "Trefoil closure and persistence discipline" not in text:
        text = text.replace(open_ladder, TREFOIL_APPENDIX + open_ladder)

    if EDITION_V083.strip() not in text:
        text = text.replace(
            r"        \subsection{Canon edition notes (v0.8.2)}",
            EDITION_V083 + r"        \subsection{Canon edition notes (v0.8.2)}",
        )

    wiens = r"            \bibitem{Wien1896}"
    if "Rolfsen1976" not in text:
        text = text.replace(wiens, BIB_INSERT + wiens)

    moffatt = r"            \bibitem{Moffatt1969}"
    if "KidaTakaoka1994" not in text:
        text = text.replace(moffatt, BIB_KIDA + moffatt)

    return bump_version(text, "v0.8.3", "v0.8.2")


def patch_rt(text: str) -> str:
    reps = [
        (
            r"\textbf{[DERIVED]}: if two identical electron-candidate loops are forced into the same spatial state, regularization at the core radius $\rc$ yields the overlap penalty",
            r"\textbf{[DERIVED]}: if two identical electron-candidate loops are forced into the same spatial state, regularization at the physical tube radius $a_{\rm core}$ yields the overlap penalty",
        ),
        (
            r"\frac{d\ell_1\cdot d\ell_2}{\sqrt{\norm{r_1(\theta_1)-r_2(\theta_2)+d}^2+\rc^2}}",
            r"\frac{d\ell_1\cdot d\ell_2}{\sqrt{\norm{r_1(\theta_1)-r_2(\theta_2)+d}^2+a_{\rm core}^2}}",
        ),
        (
            r"\frac{\rhoF\Gamma_0^2}{4\pi}\left(\frac{L}{\rc}\right)\mathcal{O}(1).",
            r"\frac{\rhoF\Gamma_0^2}{4\pi}\left(\frac{L}{a_{\rm core}}\right)\mathcal{O}(1).",
        ),
        (
            r"and $L\sim 2\pi a_0$ at the hydrogenic scale, one obtains the benchmark estimate\n\\begin{align}\n    V_{\\mathrm{Pauli}}^{\\max} \\sim 1.23\\times 10^{-18}\\ \\mathrm{J} \\sim 7.6\\ \\mathrm{eV}.\n\\end{align}",
            r"and $L\sim 2\pi a_0$ at the hydrogenic scale, the legacy closure-limit benchmark is\n\\begin{align}\n    V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm core}=\\rc) \\sim 1.23\\times 10^{-18}\\ \\mathrm{J} \\sim 7.6\\ \\mathrm{eV}.\n\\end{align}\nAway from that closure limit,\n\\begin{align}\n    V_{\\mathrm{Pauli}}^{\\max}(a_{\\rm core})\n    \\sim\n    V_{\\mathrm{Pauli}}^{\\max}(\\rc)\n    \\left(\\frac{\\rc}{a_{\\rm core}}\\right).\n\\end{align}",
        ),
    ]
    for old, new in reps:
        text = text.replace(old, new)

    old_table = r"""$3_1$ & electron & baseline lepton calibration \\
$T(2,5)$ or equivalent higher torus class & muon & lepton hierarchy candidate \\
$T(2,7)$ or equivalent higher torus class & tau & lepton hierarchy candidate \\
$5_2 + 5_2 + 6_1$ & proton & composite baryon candidate \\
analogous nearby composite class & neutron & composite baryon candidate \\"""
    new_table = r"""$3_1$ trefoil & electron / positron sector & baseline chiral lepton calibration \\
$T(2,5)$ or equivalent higher torus class & muon & lepton hierarchy candidate \\
$T(2,7)$ or equivalent higher torus class & tau & lepton hierarchy candidate \\
twist/clasp knots, quasi-unknot loops & quark-like defects & research-track fractional boundary winding candidates \\
$5_2+5_2+6_1$ and nearby composites & baryon candidates & legacy mass-functional dictionary, still under audit \\
triple-gear locked analogue & proton-like charged baryon analogue & mechanical model for nonzero exterior collective rotation \\
Borromean-type analogue & neutron-like neutral baryon analogue & mechanical/topological model for zero exterior charge with internal triple linking \\"""
    text = text.replace(old_table, new_table)
    text = text.replace(
        r"\caption{Minimal knot-class to particle-candidate summary retained as a research-track dictionary.}",
        r"\caption{Minimal knot-class and analogue summary (v0.8.3 research-track), aligned with main canon semantic corrections.}",
    )

    text = text.replace(
        r"\textit{Swirl-String-Theory\_Canon-v0.8.2}",
        r"\textit{Swirl-String-Theory\_Canon-v0.8.3}",
    )
    text = text.replace(
        r"\textbf{Editorial note (v0.8.2):}",
        r"\textbf{Editorial note (v0.8.3):}",
    )
    text = text.replace(
        r"been_processed/v0.8.2/SST_CANON-v0.8.2.tex",
        r"been_processed/v0.8.3/SST_CANON-v0.8.3.tex",
    )
    return bump_version(text, "v0.8.3", "v0.8.2")


def main():
    V083.mkdir(parents=True, exist_ok=True)
    shutil.copy2(V082 / "SST_CANON-v0.8.2.tex", V083 / "SST_CANON-v0.8.3.tex")
    shutil.copy2(V082 / "SST_CANON-v0.8.2-research-track.tex", V083 / "SST_CANON-v0.8.3-research-track.tex")

    main_path = V083 / "SST_CANON-v0.8.3.tex"
    rt_path = V083 / "SST_CANON-v0.8.3-research-track.tex"
    main_path.write_text(patch_main(main_path.read_text(encoding="utf-8")), encoding="utf-8")
    rt_path.write_text(patch_rt(rt_path.read_text(encoding="utf-8")), encoding="utf-8")
    print("v0.8.3 built.")


if __name__ == "__main__":
    main()
