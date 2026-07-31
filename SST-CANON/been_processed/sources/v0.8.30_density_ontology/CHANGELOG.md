# SST Canon v0.8.30 — density ontology changelog

## Summary

Density-ontology and historical-provenance release on top of v0.8.29.
Does **not** claim a new numerical derivation of `rho_f`.

## What is new

1. Separates unknown material substrate density `rho_sub` from calibrated
   effective response `rho_f = rho_eff^(0)`.
2. Introduces distinct symbols for rotational microinertia `J_omega` and
   line inertia `mu_l`.
3. Records the traced VAM-7 origin of the inherited `7e-7` decimal.
4. Corrects historical dimensional interpretation from `kg m^-3` to
   `kg m^-1` for the VAM microinertia expression.
5. Freezes `rho_f` as a constant quasi-static response coefficient in the
   canonical master equation.
6. Preserves the v0.8.29 SSDL, force-gate, uncertainty, and epoch-invariance
   audit unchanged.

## Epistemic result

- `rho_f = rho_eff^(0) = 7.0e-7 kg m^-3` remains `[CALIBRATED EFFECTIVE RESPONSE]`.
- `J_omega^VAM ~= 6.84e-7 kg m^-1` is `[HISTORICAL ORIGIN / CONDITIONAL ANSATZ]`.
- No equality between these quantities is asserted.

## Deferred

- v0.8.31: rotor relabeling, twist/bend guard, participation-gap audit
- v0.8.32: preregistered Biot–Savart tension protocol for `F_swirl^max`
