# SST Canon v0.8.27 audit: action--phase mass--shell clock route

## Verdict

The requested route was **not yet present** in v0.8.27.

### Already present

- Main canon lines 1483--1512: a canonical Swirl-Clock definition with Lorentz form.
- Main canon lines 3833--4060: explicit separation of foliation time, proper time, circulation delay, radar coordinates, and the operational Lorentz map.
- Main canon lines 4044--4060: carrier-local turnover rate \(\Omega_0=\omega_c\), but no translational Hamiltonian dressing of that rate.
- Main canon lines 4970--5005: action--angle variables occur only in the KAM stability interface; they are not coupled to translational momentum or the Compton clock.
- Research track lines 8490--8513: a conditional light-clock derivation of \(d\tau/dt=\sqrt{1-u^2/c^2}\).

### Missing in v0.8.27

- No equation of the form
  \[
  H(P,I)=\sqrt{P^2c^2+E_0^2(I)}.
  \]
- No derivation
  \[
  \dot\theta=\left.\partial_IH\right|_P=\Omega_0E_0/H=\Omega_0/\gamma.
  \]
- No fixed-momentum derivative guard.
- No low-momentum check yielding \(M_0=E_0/c^2\).
- No worldline-phase distinction between \(H/\hbar\) at fixed position and \(E_0/(\hbar\gamma)\) along the carrier.
- No theorem showing that the separable mass shell leaves rest-shape extrema unchanged.
- No mass-shell, velocity, phase-rate, or shape residual protocol.

### Semantic gap found

The existing clock language allows a resolved local speed, an internal swirl-speed evaluation, and relative translational speed to appear near the same Swirl-Clock notation. v0.8.28 adds an explicit discipline: \(\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\) is an internal characteristic speed and must not be silently used as the whole-carrier translational speed \(V\).

## v0.8.28 patch policy

1. Preserve the operational Swirl-Clock and light-clock route.
2. Add the mass--shell/action--phase route as an independent conditional derivation.
3. Link its nonrelativistic expansion to the existing \(M_0=E_0/c^2\) normalization.
4. Retire translation-induced flattening, stretching, and uniform core-thinning hypotheses.
5. Keep the unresolved step explicit: SST must derive the mass shell, the internal action, and monometricity from the substrate.
