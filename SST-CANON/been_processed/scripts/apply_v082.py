#!/usr/bin/env python3
"""Apply v0.8.2 canon patches to been_processed/v0.8.2 copies (diff-fidelity)."""
from _paths import ROOT, SCRIPTS_DIR

MAIN = ROOT / "v0.8.2" / "SST_CANON-v0.8.2.tex"
RT = ROOT / "v0.8.2" / "SST_CANON-v0.8.2-research-track.tex"

HORN_SUBSECTION = r"""    \subsection{Derived Horn/Circulation Radius}
        \label{subsec:derived_horn_circulation_radius}

        The quantity previously denoted as the characteristic ``core radius'' is fixed more precisely as a
        Compton-locked horn/circulation radius:
        \begin{align}
            \rc \equiv R_{\mathrm{horn}}
            = \frac{\vnorm}{\omega_c}
            = \frac{\hbar\vnorm}{m_e c^2}
            = \frac{\alpha\hbar}{2m_e c}
            = \frac{r_e}{2}.
            \label{eq:rc_definition}
        \end{align}
        Here
        \begin{align}
            \omega_c \equiv \frac{m_e c^2}{\hbar}
            \label{eq:omega_c_compton}
        \end{align}
        is the electron Compton angular frequency. Thus $\rc$ is the radius at which the canonical
        tangential swirl speed $\vnorm$ is obtained at the Compton angular frequency.

        \textbf{[CANON / NOTATION]}: $\omega_c$ denotes the Compton angular frequency. It must not be confused with the local vorticity scale. If $\omega_{\mathrm{vort},c}$ denotes the local vorticity of a rigid local rotation, then
        \begin{align}
            \omega_{\mathrm{vort},c}=2\omega_c,
            \qquad
            R_{\mathrm{horn}}=\frac{2\vnorm}{\omega_{\mathrm{vort},c}}.
        \end{align}

        \textbf{[CANON / SEMANTIC RULE]}: $\rc$ is not the resolved physical vortex-tube radius. The local tube/core thickness is denoted by $a_{\mathrm{core}}$ and remains a separate geometric or variational quantity:
        \begin{align}
            a_{\mathrm{core}} \neq \rc.
        \end{align}

        \textbf{[DERIVED] Consequence}: Eq.~\eqref{eq:rc_definition} removes $\rc$ as an independent parameter while avoiding the earlier ambiguity between horn-envelope scale, tube radius, and vorticity.
"""

OLD_DERIVED = r"""    \subsection{Derived Length Scale}
        
        The characteristic core radius is defined as:
        
        \begin{align}
            \rc = \frac{\vnorm}{\omega_c}
            \label{eq:rc_definition}
        \end{align}
        
        \textbf{[SPECULATIVE] Definition}: We treat Eq.~\eqref{eq:rc_definition} as a canonical closure relation linking the characteristic core scale to the primitive pair $(\vnorm,\omega_c)$.

        \textbf{[DERIVED] Consequence}: This removes $r_c$ as an independent parameter and eliminates one source of circular parameterization.
"""

CRITICAL_NOTE = r"""
        \textbf{[CRITICAL NOTE AFTER RADIUS DISAMBIGUATION].}
        Equation~\eqref{eq:core_density} defines a canonical density associated
        with the neutral circulation envelope at scale \(\rc\). It should not be
        read as the material density of the microscopic rotation-dominated tube.
        If a local tube mass density is required, it must be introduced through
        the separate tube radius \(a_{\rm core}\) and a corresponding local
        tube-volume model. Thus \(\rhocore\) is retained as a calibrated
        envelope-equivalent density, while \(a_{\rm core}\) controls local
        filament cutoffs and reconnection-scale modelling.
"""

HORN_ENVELOPE = r"""        \subsection{Horn-Envelope Density Normalization}
            The electron rest-energy normalization may be written as an effective horn-envelope density relation,
            \begin{align}
                \rho_{\mathrm{horn}}^{\mathrm{eff}}
                \equiv
                \frac{m_e c^2}{2\pi \vnorm^2 R_{\mathrm{horn}}^3}.
                \label{eq:rho_horn_eff}
            \end{align}
            This relation is dimensionally exact,
            \begin{align}
                \left[\frac{m_e c^2}{v^2 r^3}\right]
                =
                \mathrm{kg\,m^{-3}},
            \end{align}
            but its interpretation is now restricted.

            \textbf{[CANON / SEMANTIC RULE]}: Eq.~\eqref{eq:rho_horn_eff} is an effective horn-envelope or normalization density. It is not a measured local material density of the resolved vortex tube. Any resolved-tube model must use $a_{\mathrm{core}}$, a profile function, or ropelength/finite-thickness data rather than silently identifying $a_{\mathrm{core}}=\rc$.

            \textbf{[CANON / MASS-FUNCTIONAL NOTE]}: Existing mass-functionals that use $\rho_{\mathrm{core}}\rc^3$ should be read as horn-envelope normalizations unless a separate local-core profile is explicitly introduced.
"""

OLD_CORE_DENSITY_INTEGRATION = r"""        \subsection{Core density closure}
            Writing the electron rest energy as localized swirl energy inside a core region leads to the closure
            \begin{align}
                \rho_{\mathrm{core}}
                \sim
                \frac{m_e c^2}{2\pi v_{\swirlarrow}^2 r_c^3},
            \end{align}
            which is the form already recorded in Eq.~\eqref{eq:core_density}. This relation is dimensionally exact:
            \begin{align}
                \left[\frac{m_e c^2}{v^2 r^3}\right]
                =
                \frac{\mathrm{kg\,m^2\,s^{-2}}}{\mathrm{m^2\,s^{-2}}\,\mathrm{m^3}}
                = \mathrm{kg\,m^{-3}}.
            \end{align}
"""

EDITION_NOTE = r"""        \subsection{Canon edition notes (v0.8.2)}
            \textbf{v0.8.2} integrates radius/density semantic correction: $\rc \equiv R_{\mathrm{horn}}$, separate $a_{\mathrm{core}}$, and horn-envelope density normalization per conversation and highres diffs.
"""


def patch_main(text: str) -> str:
    if OLD_DERIVED not in text:
        raise SystemExit("OLD_DERIVED block not found in main tex")
    text = text.replace(OLD_DERIVED, HORN_SUBSECTION)

    text = text.replace(
        r"\rhocore &\quad \text{(saturated vortex-core density)}.",
        r"\rhocore &\quad \text{(canonical saturated envelope-equivalent density)}.",
    )

    anchor = (
        r"\textbf{[DERIVED] Consequence}: Within that closure, $\rhocore$ is no longer an independent parameter."
    )
    if CRITICAL_NOTE.strip() not in text:
        text = text.replace(anchor, anchor + CRITICAL_NOTE)

    reps = [
        (
            "from the Compton energy stored over the core cross-section",
            "from the Compton energy stored over the canonical circulation cross-section",
        ),
        (
            "the Compton energy scale divided by twice the core radius",
            "the Compton energy scale divided by twice the canonical circulation radius",
        ),
        (
            "over the core cross-section. It is",
            "over the canonical circulation cross-section. It is",
        ),
        (
            "consistent with the canonical core closure",
            "consistent with the canonical neutral-circulation closure",
        ),
        (
            "at the core scale, and this stiffness ratio",
            "at the canonical circulation scale, and this stiffness ratio",
        ),
        (
            "equal to the vortex core radius $\\rc$",
            "equal to the canonical circulation radius $\\rc$",
        ),
        (
            "The maximal Coulomb repulsion at core scale is exactly",
            "The maximal Coulomb repulsion at the canonical circulation scale is exactly",
        ),
        (
            "quarter-Coulomb force at core scale. The medium sustains one quarter of the maximum proton--proton Coulomb repulsion before the topological structure of the vortex core fails",
            "quarter-Coulomb force at the canonical circulation scale. The medium sustains one quarter of the maximum proton--proton Coulomb repulsion before the neutral circulation envelope reaches its structural limit",
        ),
        (
            "associated with the vortex core scale, this reduces to:",
            "associated with the neutral circulation scale, this reduces to:",
        ),
        (
            "The intrinsic delay of the vortex loop is identical",
            "The intrinsic delay of the neutral circulation loop is identical",
        ),
    ]
    for old, new in reps:
        text = text.replace(old, new)

    if OLD_CORE_DENSITY_INTEGRATION not in text:
        raise SystemExit("integration Core density closure block not found")
    text = text.replace(OLD_CORE_DENSITY_INTEGRATION, HORN_ENVELOPE)

    text = text.replace(
        "%! v0.8.1 edition: branched from v0.8.0 with dark-sector/galactic canonization integration in the main text.",
        "%! v0.8.2 edition: horn/circulation radius and envelope-density semantic correction (been_processed).",
    )
    text = text.replace(
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.1}",
        r"\newcommand{\papertitle}{Swirl-String-Theory Canon-v0.8.2}",
    )
    text = text.replace("Version v0.8.1\\par", "Version v0.8.2\\par")
    text = text.replace(
        r"\input{SST_CANON-v0.8.1-research-track}",
        r"\input{SST_CANON-v0.8.2-research-track}",
    )
    if EDITION_NOTE.strip() not in text:
        marker = r"        \subsection{Open theorem ladder}"
        text = text.replace(marker, EDITION_NOTE + "\n\n" + marker)

    return text


def patch_rt(text: str) -> str:
    reps = [
        (
            "narrow relative to the core-scale carrier, whereas $\\tau_p\\lesssim T_{\\mathrm{SST}}$ is broadband at the canonical core scale.",
            "narrow relative to the canonical circulation-scale carrier, whereas $\\tau_p\\lesssim T_{\\mathrm{SST}}$ is broadband at the canonical circulation scale.",
        ),
        (
            "For the canonical core scale,",
            "For the canonical circulation scale,",
        ),
        (
            r"\subsection{Core-Scale Calibration and the QED Critical Field}",
            r"\subsection{Canonical Circulation-Scale Calibration and the QED Critical Field}",
        ),
        (
            "At the SST core scale the characteristic angular vorticity scale is",
            "At the SST canonical circulation scale the characteristic angular frequency scale is",
        ),
    ]
    for old, new in reps:
        text = text.replace(old, new)
    text = text.replace(
        r"This companion document collects those sectors that remain useful for continuity and future development but are too long, too provisional, or too phenomenology-specific for the core body of \textit{Swirl-String-Theory\_Canon-v0.8.1}.",
        r"This companion document collects those sectors that remain useful for continuity and future development but are too long, too provisional, or too phenomenology-specific for the core body of \textit{Swirl-String-Theory\_Canon-v0.8.2}.",
    )
    text = text.replace(
        r"\textbf{Editorial note (v0.8.1):}",
        r"\textbf{Editorial note (v0.8.2):}",
    )
    text = text.replace(
        r"developed in the core document under \verb|SST_CANON-v0.8.1.tex|, subsection \texttt{Maximal Swirl Tension}",
        r"developed in the core document under \verb|been_processed/v0.8.2/SST_CANON-v0.8.2.tex|, subsection \texttt{Maximal Swirl Tension}",
    )
    return text


def main():
    main_tex = MAIN.read_text(encoding="utf-8")
    MAIN.write_text(patch_main(main_tex), encoding="utf-8")
    rt_tex = RT.read_text(encoding="utf-8")
    RT.write_text(patch_rt(rt_tex), encoding="utf-8")
    print("v0.8.2 patches applied.")


if __name__ == "__main__":
    main()
