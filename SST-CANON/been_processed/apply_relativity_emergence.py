#!/usr/bin/env python3
"""Apply relativity-emergence patch (default v0.8.13).

Integrates the SR/GR emergence audit conversation:
  * Main canon: internal tensor-speed naturalness proposition (c13=0 conditional).
  * Research track: "Relativity Emergence Ladder" chapter.
  * Bibliography: relativity/induced-gravity/cosmology bibitems.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "subsec:tensor_speed_naturalness"

# --- Main canon: c13 naturalness proposition after the tensor-mode constraint ---
TENSOR_ANCHOR = (
    "        \\textbf{[ORTHODOX] Constraint}: any SST realization employing the EFT bridge of Eq.~\\eqref{eq:clock_sector_action}\n"
    "        must preserve Eq.~\\eqref{eq:c13_constraint}.\n\n"
    "    \\subsection{Interpretive Role in the Canon}"
)

TENSOR_NATURALNESS = r"""        \textbf{[ORTHODOX] Constraint}: any SST realization employing the EFT bridge of Eq.~\eqref{eq:clock_sector_action}
        must preserve Eq.~\eqref{eq:c13_constraint}.

    \subsection{Internal Tensor-Speed Naturalness}
    \label{subsec:tensor_speed_naturalness}

        \textbf{[DERIVED, conditional]} In the clock-field / Einstein--\AE ther
        comparison layer, the spin-2 tensor-mode speed is conventionally written as
        \begin{align}
            c_T^2
            =
            \frac{c^2}{1-c_{13}},
            \qquad
            c_{13}:=c_1+c_3 .
            \label{eq:eaether_tensor_speed}
        \end{align}
        Multimessenger observations require \(c_T=c\) to high precision and therefore
        impose \(c_{13}\simeq 0\) observationally \cite{Monitor2017,Abbott2017GW170817}. In SST there is a stronger conditional
        interpretation: if the metric tensor mode of the coarse-grained clock-field
        sector is identified with the transverse excitation mode of the underlying
        medium, and if \(c\) is the canonical transverse propagation speed of that
        medium, then
        \begin{align}
            c_T=c
            \quad\Longrightarrow\quad
            c_{13}=0 .
            \label{eq:c13_internal_identity}
        \end{align}

        \textbf{Status.} Equation~\eqref{eq:c13_internal_identity} is not an
        independent derivation of the Einstein--Hilbert dynamics. It is a conditional
        mode-identification result inside the orthodox Einstein--\AE ther comparison
        layer \cite{JacobsonMattingly2001,FosterJacobson2006}. Its canon role is to upgrade the luminal tensor-speed condition from a
        purely external observational constraint to an internal naturalness condition,
        provided the SST tensor-mode identification is valid.

        \textbf{[CRITICAL NOTE]} The proposition applies only to the spin-2/tensor
        sector. It does not by itself constrain the scalar and vector \(\AE\)-modes,
        nor does it prove monometricity for all matter, gauge, and knot species. The
        full monometricity target and the Einstein-dynamics routes are developed in the
        research track (Relativity Emergence Ladder).

    \subsection{Interpretive Role in the Canon}"""

# --- Main canon: bibliography additions before \end{thebibliography} ---
BIB_ANCHOR = "        \\end{thebibliography}\n\n\\end{document}"
BIB_ADDITIONS = r"""            \bibitem{Einstein1905}
            A.~Einstein,
            \newblock Zur Elektrodynamik bewegter K{\"o}rper,
            \newblock Annalen der Physik \textbf{322} (1905), 891--921,
            \newblock DOI: 10.1002/andp.19053221004.

            \bibitem{Einstein1915}
            A.~Einstein,
            \newblock Die Feldgleichungen der Gravitation,
            \newblock Sitzungsberichte der K{\"o}niglich Preussischen Akademie der Wissenschaften (1915), 844--847,
            \newblock permalink: https://einsteinpapers.press.princeton.edu/vol6-trans/129.

            \bibitem{BarceloLiberatiVisser2011}
            C.~Barcel{\'o}, S.~Liberati, and M.~Visser,
            \newblock Analogue Gravity,
            \newblock Living Reviews in Relativity \textbf{14} (2011), 3,
            \newblock DOI: 10.12942/lrr-2011-3.

            \bibitem{Jacobson1995}
            T.~Jacobson,
            \newblock Thermodynamics of spacetime: The Einstein equation of state,
            \newblock Phys. Rev. Lett. \textbf{75} (1995), 1260--1263,
            \newblock DOI: 10.1103/PhysRevLett.75.1260.

            \bibitem{Sakharov1967}
            A.~D. Sakharov,
            \newblock Vacuum quantum fluctuations in curved space and the theory of gravitation,
            \newblock Dokl. Akad. Nauk SSSR \textbf{177} (1967), 70--71;
            \newblock Sov. Phys. Dokl. \textbf{12} (1968), 1040--1041.

            \bibitem{JacobsonMattingly2001}
            T.~Jacobson and D.~Mattingly,
            \newblock Gravity with a dynamical preferred frame,
            \newblock Phys. Rev. D \textbf{64} (2001), 024028,
            \newblock DOI: 10.1103/PhysRevD.64.024028.

            \bibitem{FosterJacobson2006}
            B.~Z. Foster and T.~Jacobson,
            \newblock Post-Newtonian parameters and constraints on Einstein-\AE ther theory,
            \newblock Phys. Rev. D \textbf{73} (2006), 064015,
            \newblock DOI: 10.1103/PhysRevD.73.064015.

            \bibitem{Abbott2017GW170817}
            B.~P. Abbott et al. (LIGO Scientific Collaboration and Virgo Collaboration),
            \newblock GW170817: Observation of gravitational waves from a binary neutron star inspiral,
            \newblock Phys. Rev. Lett. \textbf{119} (2017), 161101,
            \newblock DOI: 10.1103/PhysRevLett.119.161101.

            \bibitem{Mohr2025CODATA}
            P.~J. Mohr, D.~B. Newell, B.~N. Taylor, and E.~Tiesinga,
            \newblock CODATA recommended values of the fundamental physical constants: 2022,
            \newblock Rev. Mod. Phys. \textbf{97} (2025), 025002,
            \newblock DOI: 10.1103/RevModPhys.97.025002.

            \bibitem{Planck2018Cosmology}
            N.~Aghanim et al. (Planck Collaboration),
            \newblock Planck 2018 results. VI. Cosmological parameters,
            \newblock Astronomy \& Astrophysics \textbf{641} (2020), A6,
            \newblock DOI: 10.1051/0004-6361/201833910.

        \end{thebibliography}

\end{document}"""

# --- Research track: appended Relativity Emergence Ladder chapter ---
RT_ANCHOR = (
    "A positive result must track coherence and vanish under matched non-coherent\n"
    "thermal, electromagnetic, and mechanical controls.\n"
)

RT_CHAPTER = r"""A positive result must track coherence and vanish under matched non-coherent
thermal, electromagnetic, and mechanical controls.

\section{Relativity Emergence Ladder in SST}
\label{sec:rt_relativity_emergence_ladder}

\subsection{Purpose and status}

This section records the precise epistemic status of special-relativistic and
general-relativistic structures inside Swirl--String Theory (SST). The goal is
not to overclaim that general relativity has been derived from incompressible
Euler dynamics. The goal is to separate:
\begin{enumerate}
    \item kinematic consequences of a common propagation cone;
    \item clock and metric bridge structures;
    \item weak-field gravitational closures;
    \item the still-open problem of deriving the Einstein field equations.
\end{enumerate}

\textbf{Status summary.} SST presently supports a conditional reconstruction of
relativistic kinematics for its excitation sector, a conditional weak
equivalence principle, and a conditional Newtonian limit. The full
Einstein--Hilbert dynamics remain an open research target.

\subsection{Primitive structure}

The minimal SST substrate is taken to be an incompressible, inviscid medium on a
preferred foliation,
\begin{align}
    \mathcal{M}_{\mathrm{SST}}
    =
    \mathbb{R}^3 \times \mathbb{R},
    \qquad
    \nabla\cdot \mathbf{v}=0 ,
\end{align}
with structured vorticity, quantized circulation, a canonical transverse
propagation speed \(c\), and a local Swirl--Clock factor
\begin{align}
    S_{(t)}(x)
    =
    \sqrt{1-\frac{u(x)^2}{c^2}} .
    \label{eq:rt_swirl_clock}
\end{align}

\textbf{[ORTHODOX]} The functional form of
Eq.~\eqref{eq:rt_swirl_clock} is the standard Lorentz time-dilation factor.

\textbf{[SST INTERPRETATION]} The velocity \(u(x)\) is interpreted as a local
medium-kinematic state rather than as an abstract spacetime postulate.

\textbf{[CRITICAL NOTE]} If \(c\) is inserted as a primitive signal speed, then
the existence of a limiting cone is not itself derived. What may be derived is
the operational Lorentz kinematics of clocks and rods whose internal dynamics
are mediated only by that cone.

\subsection{Light-clock derivation of the Lorentz factor}

Consider a clock whose tick is defined by a transverse signal moving at speed
\(c\) in the substrate frame. If the clock moves with speed \(u\) relative to
the substrate, then during one half-cycle
\begin{align}
    c^2 \Delta t^2
    =
    u^2 \Delta t^2 + c^2 \Delta \tau^2 .
\end{align}
Therefore
\begin{align}
    \Delta \tau
    =
    \Delta t
    \sqrt{1-\frac{u^2}{c^2}} .
    \label{eq:rt_light_clock_gamma}
\end{align}

\textbf{[DERIVED, conditional]} Equation~\eqref{eq:rt_light_clock_gamma}
derives Lorentz time dilation for clocks whose internal communication is
entirely mediated by substrate excitations with speed \(c\) \cite{Einstein1905}.

\textbf{[OPEN CANON GAP]} Universal Lorentz kinematics for all matter species
requires the stronger monometricity condition below.

\subsection{Monometricity theorem target}

Let \(A\) label low-energy SST excitation species. The principal symbol of the
linearized equations for species \(A\) defines an effective characteristic
surface
\begin{align}
    P_A(k)=0 .
\end{align}
Relativistic universality requires that, at low energy,
\begin{align}
    P_A(k)=0
    \quad\Longleftrightarrow\quad
    g_{\mathrm{eff}}^{\mu\nu} k_\mu k_\nu=0
    \qquad
    \text{for all } A ,
    \label{eq:rt_monometricity}
\end{align}
up to irrelevant conformal factors:
\begin{align}
    g^{\mu\nu}_{\mathrm{eff},A}
    =
    \Omega_A^2(x)\,
    g^{\mu\nu}_{\mathrm{eff}} .
\end{align}

\textbf{[OPEN CANON GAP: MONOMETRICITY]} SST currently contains at least two
distinguished speeds,
\begin{align}
    c,
    \qquad
    \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}
    =
    \frac{\alpha c}{2},
\end{align}
so exact low-energy Lorentz universality is not automatic. The required theorem
is that matter knots, gauge/torsion pulses, and clock excitations share the
same effective cone in the infrared. In condensed-matter language this is the
Fermi-point universality problem \cite{Volovik2003}.

\textbf{Falsifier.} Failure of Eq.~\eqref{eq:rt_monometricity} predicts
species-dependent Lorentz violation and preferred-frame effects.

\subsection{Analogue-metric bridge}

For a hyperbolic perturbation sector with common characteristic speed \(c\),
the linearized excitation equation can be written schematically as
\begin{align}
    \frac{1}{\sqrt{-g_{\mathrm{eff}}}}
    \partial_\mu
    \left(
        \sqrt{-g_{\mathrm{eff}}}\,
        g_{\mathrm{eff}}^{\mu\nu}
        \partial_\nu \phi
    \right)
    =
    0 .
    \label{eq:rt_analogue_metric}
\end{align}

\textbf{[ORTHODOX]} Equations of the form
\eqref{eq:rt_analogue_metric} are standard in analogue-gravity systems
\cite{Unruh1981,BarceloLiberatiVisser2011}.

\textbf{[SST STATUS: CONDITIONAL BRIDGE]} In SST this bridge applies only to the
explicit hyperbolic excitation sector. It does not follow from incompressibility
alone, because incompressible Euler pressure is a constraint field rather than
an ordinary compressional sound mode. The correct conditional statement is: if
the torsion/transverse excitation sector has a hyperbolic principal operator
with speed \(c\), then an effective Lorentz cone follows.

\textbf{[CRITICAL NOTE]} Analogue gravity reproduces curved-spacetime
kinematics for perturbations. It does not, by itself, derive the Einstein field
equations.

\subsection{Weak equivalence principle}

There are two independent conditional routes to the weak equivalence principle.

\paragraph{Energy-source route.}
If both inertial mass and gravitational source strength are determined by the
same localized energy functional,
\begin{align}
    m_i(T)c^2 = E_T,
    \qquad
    m_g(T)c^2 = E_T,
\end{align}
then
\begin{align}
    m_i(T)=m_g(T).
\end{align}

\textbf{[DERIVED, conditional]} This route is valid only if the gravitational
clock/pressure field couples universally to the total localized SST energy
functional.

\paragraph{Metric-coupling route.}
If matter is minimally coupled to a Lorentzian metric and
\(\nabla_\mu T^{\mu\nu}=0\), then the point-particle limit follows geodesic
motion,
\begin{align}
    u^\mu \nabla_\mu u^\nu =0 .
\end{align}

\textbf{[ORTHODOX CONDITIONAL THEOREM]} This is the standard GR result. In SST
it is not yet a primitive-substrate derivation, because the Lorentzian metric
and minimal coupling are assumed at the effective-field-theory level.

\subsection{Newtonian limit}

A Newtonian limit requires a scalar potential satisfying
\begin{align}
    \nabla^2 \Phi
    =
    4\pi G_{\mathrm{eff}}\rho_{\!m}.
    \label{eq:rt_poisson_relativity}
\end{align}
SST can motivate \(\rho_{\!m}=\rho_{\!E}/c^2\) from the local energy accounting,
but Eq.~\eqref{eq:rt_poisson_relativity} remains a closure law unless derived from the
coarse-grained vortex ensemble.

\textbf{[CONDITIONAL]} If Eq.~\eqref{eq:rt_poisson_relativity} is admitted as the
long-wavelength closure, the inverse-square force and Newtonian limit follow.

\textbf{[OPEN CANON GAP]} Derive Eq.~\eqref{eq:rt_poisson_relativity} directly from the
statistical mechanics or coarse-grained pressure response of many swirl strings.

\subsection{Einstein dynamics: three candidate routes}

\paragraph{Route I: thermodynamic gravity.}
Jacobson's route derives the Einstein equation as an equation of state from
\(\delta Q=T\,dS\) applied to local Rindler horizons, assuming an entropy-area
law and the Unruh temperature \cite{Jacobson1995}. In SST this requires:
\begin{align}
    S_{\mathrm{defect}}
    \propto
    A,
    \qquad
    T_{\mathrm{SST}}
    =
    \frac{\hbar a}{2\pi c k_B}.
\end{align}

\textbf{[RESEARCH TRACK]} This is the most promising route because it connects
directly to horizon, boundary, and holographic SST sectors.

\paragraph{Route II: Sakharov induced gravity.}
With ultraviolet cutoff \(\ell_{\mathrm{UV}}\sim r_c\), a schematic induced
gravity estimate gives \cite{Sakharov1967}
\begin{align}
    G_{\mathrm{ind}}
    \sim
    \frac{r_c^2 c^3}{\hbar N}.
\end{align}
Matching Newton's constant requires
\begin{align}
    N_{\mathrm{req}}
    \sim
    \frac{r_c^2 c^3}{\hbar G}
    =
    \left(\frac{r_c}{L_p}\right)^2
    =
    7.60\times10^{39}.
\end{align}

\textbf{[CRITICAL NOTE]} Unless \(N_{\mathrm{req}}\) is independently derived
from SST mode counting, this route only restates the hierarchy
\(r_c/L_p\).

\paragraph{Route III: infrared EFT universality.}
If coarse-grained SST organizes into a diffeomorphism-invariant metric EFT,
then the leading two-derivative action has the form
\begin{align}
    S_{\mathrm{IR}}
    =
    \frac{c^3}{16\pi G_{\mathrm{eff}}}
    \int d^4x \sqrt{-g}\,
    \left(R-2\Lambda\right)
    + S_{\mathrm{matter}}
    + S_{\mathrm{clock}} .
\end{align}

\textbf{[RESEARCH TRACK]} This route explains why Einstein--Hilbert appears as
the leading IR term, but it does not explain why a preferred-foliation
incompressible medium becomes diffeomorphism invariant in the infrared.

\textbf{[CRITICAL NOTE]} The cosmological-constant problem is severe
\cite{Planck2018Cosmology}:
\begin{align}
    \frac{\rho_{\!f}}{\rho_\Lambda}
    \approx
    1.2\times10^{20},
    \qquad
    \frac{\rho_{\mathrm{core}}}{\rho_\Lambda}
    \approx
    6.6\times10^{44}.
\end{align}

\subsection{Tensor-speed naturalness}

In the Einstein--\AE ther comparison layer,
\begin{align}
    c_T^2
    =
    \frac{c^2}{1-c_{13}},
    \qquad
    c_{13}=c_1+c_3 .
\end{align}
If SST tensor modes are identified with transverse substrate waves, and if the
canonical transverse wave speed is \(c\), then
\begin{align}
    c_T=c
    \quad\Rightarrow\quad
    c_{13}=0 .
\end{align}

\textbf{[DERIVED, conditional]} The luminal spin-2 speed is then not a tuning
but an internal consistency condition of the mode identification
\cite{FosterJacobson2006,Abbott2017GW170817}. This mirrors the main-canon
proposition of Section~\ref{subsec:tensor_speed_naturalness}.

\textbf{[LIMIT]} This does not prove the Einstein field equations. It only
fixes the spin-2 propagation speed inside the effective comparison theory.

\subsection{Final status statement}

The accurate SST statement is:

\begin{quote}
SST conditionally reconstructs relativistic kinematics for its low-energy
excitation sector, provided monometricity holds. It provides conditional routes
to the weak equivalence principle and to the Newtonian limit. It naturally
explains luminal tensor-mode speed if gravitational tensor modes are transverse
substrate waves. The full Einstein field equations remain an open research
target, with thermodynamic, induced-gravity, and infrared-EFT routes under
active investigation.
\end{quote}
"""


def _apply_pairs(text: str, pairs, strict=False):
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:120]}...")
    return text


def apply(version: str = "0.8.13") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"relativity-emergence patch already present in v{version}.")
        return
    mtext = _apply_pairs(
        mtext,
        [
            (TENSOR_ANCHOR, TENSOR_NATURALNESS),
            (BIB_ANCHOR, BIB_ADDITIONS),
        ],
        strict=True,
    )
    rtext = _apply_pairs(
        rt.read_text(encoding="utf-8"),
        [(RT_ANCHOR, RT_CHAPTER)],
        strict=True,
    )
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"relativity-emergence patch applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.13"
    apply(version)


if __name__ == "__main__":
    main()
