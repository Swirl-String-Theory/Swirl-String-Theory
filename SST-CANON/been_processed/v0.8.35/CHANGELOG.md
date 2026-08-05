# SST Canon v0.8.35 — transverse-projector / finite-core response changelog

**Zenodo (one line):** transverse-projector 8pi/3 origin, alpha-blind finite-core response, helicity-constrained twist energy, and EM matching guards.

## Summary

Release on top of v0.8.34: isotropic transverse-projector origin of the
`8π/3` factor, radius/diameter ropelength conversion, bare-projector and
constant-tube no-gos, alpha-blind finite-core response with `c_L=0`, and
helicity-constrained parity-even twist energy linked to the gauge-emergence
ladder. Nonrelease speculative appendix v0.3 is intentionally unchanged.

## What is new

1. Derives `∫_{S²} t_i (δ_ij − k̂_i k̂_j) t_j dΩ = 8π/3` from spatial isotropy.
2. Separates diameter-normalized `L/D` from radius-normalized `L/a`
   (`(8π/3)(L/D) = (4π/3)(L/a)`).
3. Reclassifies the previous finite-cell mode-count decomposition as historical
   bookkeeping rather than the unique origin of the prefactor.
4. Adds bare-projector and constant-circular-tube-volume no-go results.
5. Adds the alpha-blind finite-core response
   `Δ_micro^(+) = c_κ I_κ² + c_Ω I_Ω² + c_C C_contact + ⋯` with `c_L = 0`.
6. Uses `SL = Wr + Tw` as a helicity-sector constraint.
7. Derives the parity-even twist-energy bound
   `I_Ω² ≥ (4π²)/(L/D) (SL − Wr)²`.
8. Keeps linear helicity in the separate parity-odd / theta-like channel.
9. Links the response to the existing gauge-emergence certification ladder
   before any identification with `α⁻¹`.
10. Adds bend, twist, contact, holdout, cross-representation, cross-knot, and
    final-trefoil calibration gates.

## Numerical convention guard

- High-resolution branch: `L/D = 16.3714672385`, `L/a = 32.7429344770`,
  `Δ = −0.1172840362`.
- Gilbert branch: `L/D = 16.371637`, `L/a = 32.743274`,
  `Δ = −0.1187062268`.
- Branches may not be mixed.

## Protocol review (archived companion)

`SST_CANON-v0.8.35_canon_protocol_review.md` rates the package
**conditionally acceptable / not yet protocol-clean**: compound epistemic
umbrella tags should be decomposed to paragraph-level primary tags
(recommended follow-up: v0.8.35a or v0.8.36). Scientific content and
derivations are acceptable as a guarded research programme; the EM claim
remains open.

## Deferred

- Paragraph-level epistemic tag cleanup (protocol review P1/P2)
- Biot–Savart / `F_swirl^max` mechanical-tension protocol

## Source

- Release zip: `SST_CANON-v0.8.35_release_patch.zip`
- Base: Canon v0.8.34 → `been_processed/v0.8.35/`
- Ingest: `scripts/apply_v0835.py`
