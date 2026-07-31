# SST Canon v0.8.32 — orphaned-normalization changelog

## Summary

Orphaned-normalization adjudication and complete rho_f scaling audit
on top of v0.8.31 (phase-2 of the v0.8.31 companion audit).

## What is new

1. Removes `7.0e-7 kg m^-3` from the primitive calibration set.
2. Registers `rho_ref` as `[LEGACY REFERENCE NORMALIZATION / PROVENANCE INVALIDATED]`.
3. Leaves physical `rho_f ≡ rho_eff^(0)` numerically unfixed.
4. Records all four VAM-7 provenance defects.
5. Adds A/B/C/Q/X response-scaling audit and source-free radiation no-go.
6. Converts selected absolute amplitudes to legacy-reference benchmarks.
7. Nonrelease speculative appendix remains v0.2 (byte-identical).

## Deferred

- v0.8.33: covariant vortex-worldsheet / gauge-certification (separate package)
- Later: Biot–Savart / `F_swirl^max` mechanical-tension protocol
