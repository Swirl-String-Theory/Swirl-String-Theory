#!/usr/bin/env python3
"""Apply core-torsion / two-speed discipline patch (default v0.8.14).

Source: SST_v0.8.12_core_torsion_canon_patch.diff
  * Main canon: "Two-Speed Discipline for Clock Emergence" subsection + alpha-gate guard.
  * Research track: "Core--Torsion Impedance Matching for Inertia Closure" section.
"""
import sys
from _paths import ROOT, SCRIPTS_DIR

MARKER = "subsec:two_speed_clock_discipline"

MAIN_CONSEQUENCE_ANCHOR = (
    "        \\textbf{[DERIVED] Consequence}: Once this identification is adopted, the Swirl-Clock provides a local scalar measure of kinematic time modulation within the medium description.\n"
    "    \n"
    "    \\subsection{Density Hierarchy}"
)

MAIN_TWO_SPEED = r"""        \textbf{[DERIVED] Consequence}: Once this identification is adopted, the Swirl-Clock provides a local scalar measure of kinematic time modulation within the medium description.

    \subsection{Two-Speed Discipline for Clock Emergence}
        \label{subsec:two_speed_clock_discipline}

        The canon distinguishes the canonical horn/circulation speed \(\vchar\) from the transverse causal speed \(c\):
        \begin{align}
            \vchar = 1.09384563\times 10^{6}\ \mathrm{m\,s^{-1}},
            \qquad
            c = 2.99792458\times 10^{8}\ \mathrm{m\,s^{-1}},
            \qquad
            \frac{\vchar}{c}=3.64867628\times10^{-3}.
        \end{align}
        Thus \(\vchar\) is a calibrated circulation/horn speed, not the universal causal speed.

        \textbf{[CANON / SEMANTIC RULE]} The calibrated identity \(\vchar=\alpha c/2\) must not be inverted into a claim that the internal core sound speed equals \(c\).  In a Gross--Pitaevskii / NLSE core model with circulation quantum and healing length
        \begin{align}
            \Gamma_q = \frac{h_*}{m_*},
            \qquad
            \xi = \frac{\hbar_*}{\sqrt{2}\,m_* c_s},
        \end{align}
        imposing \(\Gamma_q=\Gamma_0\) and \(\xi=\rc\) gives
        \begin{align}
            c_s
            =
            \frac{\Gamma_0}{2\sqrt{2}\pi\rc}
            =
            \frac{\vchar}{\sqrt{2}}
            =
            7.73465663\times10^{5}\ \mathrm{m\,s^{-1}}.
            \label{eq:core_sound_speed_vchar_over_sqrt2}
        \end{align}
        Therefore a calculation that closes an inertia ratio as \(u^2/c_s^2\) has produced an internal core-acoustic closure, not yet the Lorentz-compatible ratio \(u^2/c^2\).

        \textbf{[RESEARCH-TRACK GATE]} A Lorentz-compatible derivation of the Swirl-Clock requires a separate transverse torsion/shear sector with propagation speed \(c_T=c\), plus a core--torsion impedance identity of the form
        \begin{align}
            \mathsf M_{\mathrm{torsion}}[K]
            \stackrel{?}{=}
            \frac{2E_0[K]}{c_T^2}\,\mathsf I .
            \label{eq:core_torsion_impedance_gate_main}
        \end{align}
        Until Eq.~\eqref{eq:core_torsion_impedance_gate_main} is derived from a controlled field calculation, the Swirl-Clock remains an orthodox functional form with an SST interpretation, or a derived-conditional bridge result, rather than a hard theorem from the NLSE core alone.

    \subsection{Density Hierarchy}"""

MAIN_ALPHA_GATE_ANCHOR = (
    "            \\Pi_K = \\left( \\frac{\\lambda_c}{\\pi \\rc} \\right)^{G(K)} = \\left( \\frac{4}{\\alpha} \\right)^{G(K)} .\n"
    "        \\end{align}\n\n"
    "        The canonical topological kernel is taken to be"
)

MAIN_ALPHA_GATE = r"""            \Pi_K = \left( \frac{\lambda_c}{\pi \rc} \right)^{G(K)} = \left( \frac{4}{\alpha} \right)^{G(K)} .
        \end{align}

        \textbf{[CANON / ALPHA-GATE GUARD]} The equality \(\lambda_c/(\pi\rc)=4/\alpha\) is a calibrated geometric rewriting inside the present constant chain. It must not be cited as an independent derivation of the fine-structure constant. The finite-cell trefoil result is retained separately as an \(\alpha\)-free sub-per-mille coincidence plus obstruction result in Subsection~\ref{subsec:finite_cell_alpha_obstruction}.


        The canonical topological kernel is taken to be"""

# --- Research track: appended core-torsion impedance section ---
RT_ANCHOR = (
    "explains luminal tensor-mode speed if gravitational tensor modes are transverse\n"
    "substrate waves. The full Einstein field equations remain an open research\n"
    "target, with thermodynamic, induced-gravity, and infrared-EFT routes under\n"
    "active investigation.\n"
    "\\end{quote}\n"
)

RT_SECTION = r"""explains luminal tensor-mode speed if gravitational tensor modes are transverse
substrate waves. The full Einstein field equations remain an open research
target, with thermodynamic, induced-gravity, and infrared-EFT routes under
active investigation.
\end{quote}


%======================================================================
\section{Research Track: Core--Torsion Impedance Matching for Inertia Closure}
\label{sec:rt_core_torsion_impedance_matching}
%======================================================================

\subsection{Purpose and status}

\textbf{[RESEARCH-TRACK].}
This section records the canon-safe form of the inertia-closure programme. It separates the internal NLSE/Gross--Pitaevskii core layer from the transverse torsion/shear radiation layer. The separation is mandatory because the canonical swirl speed \(\vchar\) is much smaller than the observed causal speed \(c\):
\begin{align}
    \frac{\vchar}{c}=3.64867628\times10^{-3}.
\end{align}
A derivation that produces \(u^2/\vchar^2\) or \(u^2/c_s^2\) therefore does not yet derive the Lorentz-compatible factor \(u^2/c^2\).

\subsection{NLSE/Gross--Pitaevskii core diagnostic}

For a defocusing NLSE/Gross--Pitaevskii core with Madelung phase velocity,
\begin{align}
    \mathbf u_{\rm NLS}=\frac{\hbar_*}{m_*}\nabla S,
\end{align}
the circulation quantum and healing length may be written
\begin{align}
    \Gamma_q = \frac{h_*}{m_*}N_\Gamma,
    \qquad
    \xi = \frac{\hbar_*}{\sqrt{2}\,m_*c_s}.
\end{align}
For the single-winding convention \(N_\Gamma=1\), imposing
\begin{align}
    \Gamma_q=\Gamma_0=2\pi\rc\vchar,
    \qquad
    \xi=\rc
\end{align}
gives
\begin{align}
    c_s
    =
    \frac{\Gamma_0}{2\sqrt{2}\pi\rc}
    =
    \frac{\vchar}{\sqrt{2}}
    =
    7.73465663\times10^{5}\ \mathrm{m\,s^{-1}}.
    \label{eq:rt_core_torsion_cs}
\end{align}

\textbf{[DERIVED-CONDITIONAL].}
Equation~\eqref{eq:rt_core_torsion_cs} is a useful internal diagnostic of the core layer. It is not a derivation of the Lorentz signal speed.

\subsection{Transverse torsion/shear causal layer}

A minimal transverse torsion displacement field \(\mathbf A\), with \(\nabla\cdot\mathbf A=0\), may be assigned the quadratic bridge Lagrangian
\begin{align}
    \mathcal L_{\rm torsion}
    =
    \frac12\rhoF\lVert\partial_t\mathbf A\rVert^2
    -
    \frac12K_T\lVert\nabla\times\mathbf A\rVert^2 .
\end{align}
The transverse propagation speed is
\begin{align}
    c_T^2=\frac{K_T}{\rhoF}.
\end{align}
The canon-compatible light-speed identification belongs only to this transverse layer:
\begin{align}
    c_T=c.
\end{align}
Its intensive impedance is
\begin{align}
    Z_T=\rhoF c_T=\sqrt{\rhoF K_T},
\end{align}
which has the units of acoustic impedance, \(\mathrm{kg\,m^{-2}\,s^{-1}}\).

\subsection{Core--Torsion Impedance Matching Lemma}

Let \(K\) be a localized closed swirl-string configuration with rest-swirl energy \(E_0[K]\). Define the torsion-dressed inertial tensor by the quadratic stored-energy response
\begin{align}
    \Delta E_{\rm torsion}[K;\mathbf u]
    =
    \frac12\mathbf u^{\mathsf T}
    \mathsf M_{\rm torsion}[K]
    \mathbf u
    +O(\lVert\mathbf u\rVert^4).
\end{align}
The required Lorentz-compatible closure is
\begin{align}
    \boxed{
    \mathsf M_{\rm torsion}[K]
    \stackrel{?}{=}
    \frac{2E_0[K]}{c_T^2}\,\mathsf I
    }
    \label{eq:rt_core_torsion_matching_lemma}
\end{align}
or equivalently
\begin{align}
    \Delta E_{\rm torsion}[K;u]
    \stackrel{?}{=}
    E_0[K]\frac{u^2}{c_T^2}+O(u^4).
\end{align}
If \(c_T=c\), Eq.~\eqref{eq:rt_core_torsion_matching_lemma} supplies the missing bridge from core inertia to the Lorentz-compatible clock factor.

Define the diagnostic residual
\begin{align}
    \chi_K^{(T)}
    =
    \frac{c_T^2}{2E_0[K]}
    \lambda_{\rm iso}\!\left(\mathsf M_{\rm torsion}[K]\right).
\end{align}
The bridge closes only if
\begin{align}
    \chi_K^{(T)}=1
\end{align}
within numerical and topological tolerance.

\textbf{[OPEN LEMMA].}
The equality \(\chi_K^{(T)}=1\) is the falsifiable theorem target. If numerical torsion-dressing returns a stable non-unity value, the Lorentz clock factor remains a constitutive bridge rather than a derived theorem from the core model.

\subsection{Required numerical tests}

A canon-safe numerical programme must report:
\begin{enumerate}
    \item the NLSE boost coefficient \(M_{\rm core}[K]\) and its comparison to \(2E_0[K]/c_s^2\), not to \(2E_0[K]/c^2\);
    \item the torsion-dressed tensor \(\mathsf M_{\rm torsion}[K]\) and the residual \(\chi_K^{(T)}\);
    \item a stiffness sweep \(K_T\) verifying whether \(\chi_K^{(T)}=1\) occurs naturally at \(c_T=c\) or only after retuning;
    \item the circulation-normalization ratio \(\mathcal R_\Gamma=(h_*/m_*)/\Gamma_0\), which must equal unity under the canonical single-winding convention;
    \item the trefoil-locked source test comparing \(T_{2,3}\) against generic helical sources.
\end{enumerate}

\textbf{[CANON INTERPRETATION].}
The canon may retain the two-speed discipline and the open impedance lemma. It should not promote the Lorentz clock factor to hard canon through the NLSE core alone.
"""


def _apply_pairs(text, pairs, strict=False):
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:120]}...")
    return text


def apply(version: str = "0.8.14") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"core-torsion patch already present in v{version}.")
        return
    mtext = _apply_pairs(
        mtext,
        [
            (MAIN_CONSEQUENCE_ANCHOR, MAIN_TWO_SPEED),
            (MAIN_ALPHA_GATE_ANCHOR, MAIN_ALPHA_GATE),
        ],
        strict=True,
    )
    rtext = _apply_pairs(
        rt.read_text(encoding="utf-8"),
        [(RT_ANCHOR, RT_SECTION)],
        strict=True,
    )
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"core-torsion patch applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.14"
    apply(version)


if __name__ == "__main__":
    main()
