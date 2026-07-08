#!/usr/bin/env python3
"""Apply Lorentz-type swirl-stress patch (default v0.8.15).

Canon: hydrodynamic Lorentz-type force density (no Rosetta objects).
Research track: EM-to-swirl correspondence, SST-44 stress, f_link pending.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "sec:lorentz_type_force_density_as_swirl_stress"

MAIN_ANCHOR = (
    "        \\textbf{[DERIVED] Observables / falsifiers:} (i) consistency of a pressure profile reconstructed from archived $v_\\theta(r)$ with the radial gradient implied by \\eqref{eq:swirl_pressure_law}; (ii) null test: systematic sign or scale mismatch of the reconstructed $dp_{\\mathrm{swirl}}/dr$ relative to $v_\\theta^2/r$ across validated radial windows excludes the applicability of the balance in those windows.\n\n"
    "    \\subsection{Minimal effective Lagrangian bridge}"
)

MAIN_BLOCK = r"""        \textbf{[DERIVED] Observables / falsifiers:} (i) consistency of a pressure profile reconstructed from archived $v_\theta(r)$ with the radial gradient implied by \eqref{eq:swirl_pressure_law}; (ii) null test: systematic sign or scale mismatch of the reconstructed $dp_{\mathrm{swirl}}/dr$ relative to $v_\theta^2/r$ across validated radial windows excludes the applicability of the balance in those windows.

    \subsection{Lorentz-Type Force Density as Swirl Stress}
    \label{sec:lorentz_type_force_density_as_swirl_stress}

        \paragraph{Status labels.}
        The vector identity used in this section is \textbf{[ORTHODOX]}.  The
        definition of the swirl-force density is \textbf{[DERIVED]} as a hydrodynamic
        force-density structure.  The numerical SST scales are \textbf{[CALIBRATED]}
        with respect to the canonical constants
        \(\rhoF\), \(\rc\), and \(\vchar\).
        No microscopic electromagnetic element-force law is canonized here.

        \paragraph{Hydrodynamic identity.}
        For incompressible inviscid flow,
        \[
        \nabla\cdot\mathbf v=0,
        \qquad
        \boldsymbol{\omega}=\nabla\times\mathbf v .
        \]
        The convective acceleration satisfies the exact identity
        \[
        (\mathbf v\cdot\nabla)\mathbf v
        =
        \nabla\!\left(\frac12|\mathbf v|^2\right)
        -
        \mathbf v\times\boldsymbol{\omega}.
        \]
        Equivalently,
        \[
        \boxed{
        \mathbf v\times\boldsymbol{\omega}
        =
        \nabla\!\left(\frac12|\mathbf v|^2\right)
        -
        (\mathbf v\cdot\nabla)\mathbf v .
        }
        \]
        This provides the hydrodynamic structure behind a Lorentz-type transverse
        force-density term.

        \paragraph{Swirl-force density.}
        SST defines the local swirl-force density
        \[
        \boxed{
        \mathbf f_{\circlearrowleft}
        =
        \rhoF\mathbf v\times\boldsymbol{\omega}.
        }
        \]
        Its dimensional consistency is
        \[
        [\rhoF\mathbf v\times\boldsymbol{\omega}]
        =
        \mathrm{kg\,m^{-3}}\,
        \mathrm{m\,s^{-1}}\,
        \mathrm{s^{-1}}
        =
        \mathrm{N\,m^{-3}},
        \]
        as required for a force density.

        \paragraph{Bernoulli relation and sign convention.}
        The scalar quantity
        \[
        p_{\circlearrowleft}
        =
        \frac12\rhoF|\mathbf v|^2
        \]
        is the dynamic swirl-pressure scale.  It should not be confused with the
        static pressure, which decreases in high-swirl regions in the usual
        Bernoulli sense.  For stationary Euler flow with constant
        \(\rhoF\) and no external body force,
        \[
        \rhoF(\mathbf v\cdot\nabla)\mathbf v
        =
        -\nabla p_{\mathrm{stat}} .
        \]
        Using the identity above gives
        \[
        \boxed{
        \rhoF\mathbf v\times\boldsymbol{\omega}
        =
        \nabla\!\left(
        p_{\mathrm{stat}}
        +
        \frac12\rhoF|\mathbf v|^2
        \right).
        }
        \]
        Thus the swirl-force density is canonically tied to the gradient of total
        Euler pressure, not to an independently postulated electromagnetic force law.

        \paragraph{Closed-loop observables.}
        SST assigns canonical status to integrated and topological observables rather
        than to a unique microscopic segment-to-segment force kernel.  The canonical
        loop observables include circulation,
        \[
        \Gamma
        =
        \oint_C \mathbf v\cdot d\boldsymbol{\ell},
        \]
        helicity,
        \[
        H
        =
        \int_V \mathbf v\cdot\boldsymbol{\omega}\,d^3x,
        \]
        and the Gauss linking number,
        \[
        Lk(C_1,C_2)
        =
        \frac{1}{4\pi}
        \oint_{C_1}\oint_{C_2}
        \frac{
        (d\mathbf x_1\times d\mathbf x_2)\cdot(\mathbf x_1-\mathbf x_2)
        }{
        |\mathbf x_1-\mathbf x_2|^3
        }.
        \]
        Distinct local force kernels may yield identical closed-loop observables.
        Therefore SST canonizes circulation, helicity, linking number, pressure
        differences, and net forces, but not a unique microscopic electromagnetic
        element-force law.

        \paragraph{Canonical scales.}
        Using the canonical SST constants
        \[
        \vchar
        =
        1.09384563\times10^6\,\mathrm{m\,s^{-1}},
        \qquad
        \rc
        =
        1.40897017\times10^{-15}\,\mathrm m,
        \qquad
        \rhoF
        =
        7.0\times10^{-7}\,\mathrm{kg\,m^{-3}},
        \]
        the natural circulation scale is
        \[
        \Gamma_0
        =
        2\pi \rc\vchar
        =
        9.68361920\times10^{-9}\,\mathrm{m^2\,s^{-1}}.
        \]
        The associated dynamic swirl-pressure scale is
        \[
        p_{\circlearrowleft,0}
        =
        \frac12\rhoF\vchar^2
        =
        4.1877439\times10^{5}\,\mathrm{Pa}.
        \]
        This value is the canonical SST stress scale for Lorentz-type
        force-density analogies and coincides with the calibrated source-pressure
        scale used in the swirl-pressure sector.

        \paragraph{Canonical conclusion.}
        The canonized result is not a replacement of Maxwell--Lorentz electrodynamics.
        The canonized result is the hydrodynamic statement that a Lorentz-type
        transverse force-density structure has the exact SST form
        \[
        \boxed{
        \mathbf f_{\circlearrowleft}
        =
        \rhoF\mathbf v\times\boldsymbol{\omega}
        =
        \rhoF
        \nabla\!\left(\frac12|\mathbf v|^2\right)
        -
        \rhoF(\mathbf v\cdot\nabla)\mathbf v .
        }
        \]
        Accordingly, magnetic-type force densities in SST are interpreted as
        effective projections of pressure, vorticity, and closed-loop topology in the
        substrate.

    \subsection{Minimal effective Lagrangian bridge}"""

RT_ANCHOR = (
    "\\textbf{[CANON INTERPRETATION].}\n"
    "The canon may retain the two-speed discipline and the open impedance lemma. It should not promote the Lorentz clock factor to hard canon through the NLSE core alone.\n"
)

RT_BLOCK = r"""\textbf{[CANON INTERPRETATION].}
The canon may retain the two-speed discipline and the open impedance lemma. It should not promote the Lorentz clock factor to hard canon through the NLSE core alone.


% ============================================================
% Research-track patch: EM-to-swirl correspondence and stress closure
% ============================================================

\subsection{Research Track: EM-to-Swirl Force-Density Correspondence}
\label{sec:research_em_to_swirl_force_density_correspondence}

\paragraph{Status labels.}
The correspondence proposed in this section is \textbf{[SPECULATIVE]} and
\textbf{[PENDING DERIVATION]}.  It is not a canonical replacement of
Maxwell--Lorentz electrodynamics.  It is a Rosetta-level research bridge
between electromagnetic force density and SST substrate stress.

\paragraph{Structural correspondence.}
The electromagnetic Lorentz force density is
\[
\mathbf f_{\mathrm{EM}}
=
\rho_e\mathbf E+\mathbf J\times\mathbf B .
\]
The magnetic part has the same force-density dimension as the SST
swirl-force density,
\[
[\mathbf J\times\mathbf B]
=
\mathrm{N\,m^{-3}},
\qquad
[\rhoF\mathbf v\times\boldsymbol{\omega}]
=
\mathrm{N\,m^{-3}}.
\]
Hence the most conservative Rosetta correspondence is
\[
\boxed{
\mathbf J\times\mathbf B
\;\longleftrightarrow\;
\lambda_{\mathrm{EM}\to\circlearrowleft}\,
\rhoF\mathbf v\times\boldsymbol{\omega}.
}
\]
Since both sides already carry units of force density,
\[
\boxed{
[\lambda_{\mathrm{EM}\to\circlearrowleft}]=1 .
}
\]
The coefficient
\(\lambda_{\mathrm{EM}\to\circlearrowleft}\) is therefore dimensionless.
It is not fixed by dimensional analysis and remains
\textbf{[SPECULATIVE / PENDING DERIVATION]} until a field-level dictionary or
normalization condition is specified.

\paragraph{Relation to the canonical flux-impulse channel.}
The canonical SST electromagnetic bridge proceeds through phase, flux, and
flux-piercing variables, including the effective Faraday/flux-impulse
channel and the flux quantum
\[
\Phi_0=\frac{h}{2e}.
\]
The bulk correspondence
\[
\mathbf J\times\mathbf B
\;\longleftrightarrow\;
\lambda_{\mathrm{EM}\to\circlearrowleft}
\rhoF\mathbf v\times\boldsymbol{\omega}
\]
is therefore not an independent canonical EM bridge.  It is a candidate
continuum-limit or bulk-stress projection of the already canonical
phase/flux channel.  A canonical upgrade requires showing how the flux
observable, phase winding, and current density reduce to a definite
\(\lambda_{\mathrm{EM}\to\circlearrowleft}\) in the continuum limit.

\paragraph{Possible field-level dictionary.}
A possible but non-canonical dictionary is the classical hydrodynamic analogy
\[
\mathbf A
\;\longleftrightarrow\;
\alpha_A\mathbf v,
\qquad
\mathbf B=\nabla\times\mathbf A
\;\longleftrightarrow\;
\alpha_A\boldsymbol{\omega},
\]
and
\[
\mu_0\mathbf J
=
\nabla\times\mathbf B
\;\longleftrightarrow\;
\alpha_A\nabla\times\boldsymbol{\omega}.
\]
The constants and normalization implied by
\(\alpha_A\) are not fixed here.  This dictionary is retained only as a
research-track route toward deriving
\(\lambda_{\mathrm{EM}\to\circlearrowleft}\).

\paragraph{Stress closure and SST-44 tensor.}
The canonical swirl-stress candidate is the symmetric Cauchy-type stress
used in the SST-44 appendix,
\[
\sigma^{(44)}_{ij}
=
\rhoF v_i v_j
+
\rhoF \rc^2
\left(
\omega_i\omega_j-\frac12\delta_{ij}|\boldsymbol{\omega}|^2
\right)
-
\delta_{ij}\frac12\rhoF|\mathbf v|^2 .
\]
Because this tensor already contains the isotropic dynamic-pressure term
\[
-\delta_{ij}\frac12\rhoF|\mathbf v|^2,
\]
one must not also add an independent
\(-\nabla p_{\circlearrowleft}\) term with
\[
p_{\circlearrowleft}
=
\frac12\rhoF|\mathbf v|^2 .
\]
Otherwise the Bernoulli contribution is counted twice.

\paragraph{Two admissible decompositions.}
The full-stress convention is
\[
\boxed{
\mathbf f_{\mathrm{SST}}
=
\nabla\cdot\boldsymbol{\sigma}^{(44)}
+
\mathbf f_{\mathrm{link}} .
}
\]
The split-stress convention is
\[
\boxed{
\mathbf f_{\mathrm{SST}}
=
-\nabla p_{\circlearrowleft}
+
\nabla\cdot\boldsymbol{\sigma}^{\mathrm{dev}}_{\circlearrowleft}
+
\mathbf f_{\mathrm{link}},
}
\]
where
\[
\boldsymbol{\sigma}^{\mathrm{dev}}_{\circlearrowleft}
\equiv
\rhoF\mathbf v\mathbf v
+
\rhoF\rc^2
\left(
\boldsymbol{\omega}\boldsymbol{\omega}
-
\frac12\mathbf I|\boldsymbol{\omega}|^2
\right)
\]
contains the advective and torsional anisotropic parts but excludes the
isotropic dynamic-pressure term.  These two conventions must not be mixed.

\paragraph{Topological link force.}
The link-force term is not yet canonical.  The intended structure is a
topological potential functional
\[
U_{\mathrm{link}}
=
U_{\mathrm{link}}\!\left[
Lk(C_a,C_b),\Gamma_a,\Gamma_b,H
\right],
\]
with force density obtained schematically by variation,
\[
\boxed{
\mathbf f_{\mathrm{link}}
=
-\frac{\delta U_{\mathrm{link}}}{\delta \mathbf x}
}
\]
or, for a collective coordinate \(q\),
\[
\boxed{
F_{\mathrm{link},q}
=
-\frac{\partial U_{\mathrm{link}}}{\partial q}.
}
\]
The linking number is
\[
Lk(C_a,C_b)
=
\frac{1}{4\pi}
\oint_{C_a}\oint_{C_b}
\frac{
(d\mathbf x_a\times d\mathbf x_b)\cdot(\mathbf x_a-\mathbf x_b)
}{
|\mathbf x_a-\mathbf x_b|^3
}.
\]
Until \(U_{\mathrm{link}}\) is specified and normalized,
\(\mathbf f_{\mathrm{link}}\) remains
\textbf{[PENDING DERIVATION]}.

\paragraph{Research-track conclusion.}
The candidate bulk EM-to-swirl mapping is therefore
\[
\boxed{
\mathbf f_{\mathrm{EM}}
=
\rho_e\mathbf E+\mathbf J\times\mathbf B
\quad\leadsto\quad
\mathbf f_{\mathrm{SST}}
=
\nabla\cdot\boldsymbol{\sigma}^{(44)}
+
\mathbf f_{\mathrm{link}}
}
\]
under the full-stress convention, or equivalently
\[
\boxed{
\mathbf f_{\mathrm{SST}}
=
-\nabla p_{\circlearrowleft}
+
\nabla\cdot\boldsymbol{\sigma}^{\mathrm{dev}}_{\circlearrowleft}
+
\mathbf f_{\mathrm{link}}
}
\]
under the split-stress convention.  The correspondence becomes canonizable
only after
\(\lambda_{\mathrm{EM}\to\circlearrowleft}\),
the field-level dictionary, and
\(U_{\mathrm{link}}\)
are derived or experimentally fixed.
"""


def _apply_pairs(text, pairs, strict=False):
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif strict and new not in text:
            raise SystemExit(f"missing expected block:\n{old[:120]}...")
    return text


def apply(version: str = "0.8.15") -> None:
    main = ROOT / f"v{version}" / f"SST_CANON-v{version}.tex"
    rt = ROOT / f"v{version}" / f"SST_CANON-v{version}-research-track.tex"
    mtext = main.read_text(encoding="utf-8")
    if MARKER in mtext:
        print(f"Lorentz swirl-stress patch already present in v{version}.")
        return
    mtext = _apply_pairs(mtext, [(MAIN_ANCHOR, MAIN_BLOCK)], strict=True)
    rtext = _apply_pairs(
        rt.read_text(encoding="utf-8"),
        [(RT_ANCHOR, RT_BLOCK)],
        strict=True,
    )
    main.write_text(mtext, encoding="utf-8")
    rt.write_text(rtext, encoding="utf-8")
    print(f"Lorentz swirl-stress patch applied to v{version}.")


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "0.8.15"
    apply(version)


if __name__ == "__main__":
    main()
