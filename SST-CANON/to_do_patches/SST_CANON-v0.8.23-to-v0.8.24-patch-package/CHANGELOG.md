# SST Canon v0.8.24 integration changelog

Baseline: `SST_CANON-v0.8.23.tex` plus
`SST_CANON-v0.8.23-research-track.tex`.

## Normative repairs

### Core--torsion normalization

- Corrects the theorem target from
  `M_torsion = 2 E_0 I / c_T^2` to
  `M_torsion = E_0 I / c_T^2`.
- Defines `E_0[K]` as the complete rest energy.
- Replaces the old scalar residual by the trace-based scale residual
  `chi_hat = c_T^2 tr(M_torsion)/(3 E_0)`.
- Adds the independent Frobenius anisotropy residual `delta_aniso`.
- Requires both `chi_hat = 1` and `delta_aniso = 0` for every admitted stable
  carrier with one common parameter set.
- Treats `M_core` versus `E_0/c_s^2` only as an NLSE diagnostic, not as an
  automatic theorem.
- Extends the numerical ladder to round ring -> axisymmetric torus -> trefoil
  `3_1` -> mirror trefoil -> figure-eight `4_1`.

### Compact link-field status and phase gate

- Labels the minimal real-time compact `U(1)` link action as an orthodox
  structural template derived from the Wilson/Kogut--Susskind construction.
- Separates the orthodox template from the SST-specific substrate-torsion
  identification, coefficient provenance, source coupling, and material-sector
  interpretation.
- Adds a mandatory `3+1`-dimensional Coulomb/deconfinement gate.
- Distinguishes Polyakov's `2+1`-dimensional monopole-instanton result from the
  `3+1`-dimensional Coulomb/confining phase problem.
- Defines plaquette branch integers and a closed-cell defect charge; a single
  plaquette branch event is explicitly not promoted to a monopole.
- Requires dilute rather than condensed defects, vanishing transverse mass gap
  under refinement, and nonconfining long-distance loop behaviour.
- States explicitly that link-field deconfinement and material Helmholtz/Kelvin
  preservation are related gates but not identical statements.

### Link-spacing and ultraviolet guard

- Records the calibrated response target
  `kappa_l/iota_l = 1/(pi alpha)^2 ~= 1.9027e3` under `a_l = r_c`.
- Demotes that reduction to
  `[HISTORICAL BRIDGE / CALIBRATED ILLUSTRATION]` until a scale scenario is
  selected and certified.
- Separates three interpretations:
  1. literal fixed lattice;
  2. regulator with continuum limit;
  3. relational/dynamical adjacency graph.
- For the literal lattice records separately:
  - Brillouin-zone coordinate scale `~440 MeV`;
  - maximum axis-branch energy `~280 MeV`;
  - cubic-corner branch value `~485 MeV`;
  - `a_l <= 4.4e-22 m` merely to admit a `1.4 PeV` first-zone mode.

### Zero-legacy closure

- Rewrites the symbolic closure in the independent star basis
  `(rho_star, Gamma_star, r_star)`.
- Moves `(rho_F, Gamma_0, r_c)` into a separate calibrated-consistency map.
- Requires a dependency ledger and prohibits the `[PREDICTION]` label after a
  calibrated map has been used.

### Failure taxonomy

Replaces the flat falsifier list with four classes:

- Class E: empirical falsifiers;
- Class T: theoretical/model-closure falsifiers;
- Class N: numerical/certification failures;
- Class M: methodological-integrity failures.

A Class-M event invalidates the derivation claim and returns the result to
calibrated-consistency status; it does not by itself falsify the physical
hypothesis.

## Canonized methodological rules

- Promotes the KnotPlot--Ridgerunner geometry status ladder to a formal
  Definition and binding `[CANON RULE]`.
- Adds a cross-document operating rule requiring every result to state its mode
  (`symbolic`, `calibrated-consistency`, or `prediction`) and epistemic label.
- Adds the foundational Material--Link Sector Separation postulate with the
  canonical `Delta Gamma_C = 0` gate and explicit exceptions.
- Formalizes `c_s = v_char/sqrt(2)` as a strictly conditional lemma whose four
  hypotheses are exposed.

## Explicit non-promotions

The release does not canonize:

- the alpha response route as a prediction;
- QSS as a closed physical sector;
- the factor-9 contact rank as an `SU(3)` or gluon derivation;
- golden-layer dressings as derived energetics;
- the `theta = pi` spinorial selection mechanism.

## Structural and editorial repairs

- Updates all active edition and companion references to v0.8.24.
- Keeps the authoritative dot-based filename convention.
- Removes stale `canon-0.8.1-research-track.tex` pointers.
- Repairs merged/empty heading commands and child-heading hierarchy in the
  affected research-track sections.
- Replaces `Æther element(s)` with `substrate element(s)` in the link-field
  microstructure; `Einstein--Æther` remains reserved for the orthodox EFT
  comparison layer.
- Reduces the quoted stiffness target to `~6.3e10 Pa`, consistent with the
  precision of the density input.
- Adds seven bibliography entries for compact lattice gauge theory, phase
  structure, and the 1.4-PeV photon observation.
