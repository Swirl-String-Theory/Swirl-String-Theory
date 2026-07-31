# SST Canon v0.8.31 — rotor participation + rho_f scaling audit

## Summary

Two companion packages shipped together as v0.8.31:

1. **Rotor / participation patch** — finished main + research-track tex
   (source of `been_processed/v0.8.31/`).
2. **rho_f scaling audit, phase 1** — dependency inventory and family
   ledger against the v0.8.31 sources; **no Canon tex edits**.

Does **not** claim a new numerical derivation of `rho_f`, `J_omega`,
or a new SST primitive.

## What is new (canon tex — rotor participation)

1. Defines `rho_f = rho_eff^(0)` exclusively as the isotropic
   quasi-static (`omega->0`, `k->0`) effective-inertia limit.
2. Classifies the compact Compton-gap rotor normalization as a
   matching ansatz / reformulation.
3. Identifies `J_omega^rot` with the horn-envelope line-inertia
   coefficient rather than a new constant.
4. Records `c_omega = v_swirl` as a definitional identity.
5. Separates linear internal twist waves from quadratic Kelvin bending.
6. Quantifies the unresolved participation gap
   `phi_dyn = 5.7229e-26` and diagnostic length
   `ell_rho,eq = 5.8897 mm` (not a predicted physical cell size).
7. Adds a weighted, frequency-dependent macro-response representation
   and explicit promotion gates.
8. Preserves the v0.8.30 density ontology and VAM-7 provenance.

## Companion (archived only — rho_f scaling audit phase 1)

- Scans 206 `\\rhoF` / `\\rho_{\\!f}` occurrences (85 main, 121 RT).
- Classifies equation families A/B/C/Q/X under rescaling
  `S_lambda: rho_eff^(0) -> lambda rho_eff^(0)`.
- Provisional verdict: no clean class-C pin of absolute `rho_eff^(0)`;
  `7.0e-7` treated as legacy reference normalization; physical
  quasi-static coefficient remains unfixed pending Q-sector audit.
- Deferred to a later edition: orphaned-normalization patch /
  parameter-budget lemma (phase 2).

## Epistemic result

- `rho_f = rho_eff^(0) = 7.0e-7 kg m^-3` remains the calibrated
  quasi-static effective-response number in the published canon,
  with the phase-1 audit archived as companion evidence that a
  clean absolute pin is not yet available.
- `J_omega^rot = pi r_c^2 rho_horn^eff = 2.4282114e-11 kg m^-1`
  is `[REFORMULATION / MATCHING ANSATZ]`.
- Neither `phi_dyn` nor `ell_rho,eq` is promoted to a physical scale.

## Deferred

- v0.8.32: preregistered Biot–Savart / mechanical-tension protocol
  for `F_swirl^max`
- rho_f phase 2: detector-level C-trace, Q-sector audit, possible
  orphaned-normalization patch
