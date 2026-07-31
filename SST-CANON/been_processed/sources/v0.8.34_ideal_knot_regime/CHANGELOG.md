# SST Canon v0.8.34 — ideal-knot regime changelog

**Zenodo (one line):** ideal-knot regime guard, compact-to-slender carrier hypothesis, and Kirchhoff--Cosserat diagnostic guards.

## Summary

Ideal-knot regime-of-applicability release on top of v0.8.33.
Does **not** promote Kirchhoff–Cosserat dynamics, LIA on the compact ideal
trefoil, or a completed compact-to-slender trajectory.

## What is new

### Main Canon

1. Adds `subsec:ideal_knot_regime_guard`: compact ideal-trefoil reference
   (`eq:ideal_trefoil_compact_reference`) as a ropelength-critical ansatz,
   not a universal dynamical ground state.
2. Defines compact finite-core vs slender-filament diagnostics
   (`eq:ideal_knot_regime_diagnostics`, `eq:ideal_knot_regime_split`).
3. Records Kirchhoff–Cosserat non-equivalence: rod functionals are
   comparative diagnostics only (`eq:rod_diagnostic_functional`).
4. Prefers the Moffatt–Ricca single-tube helicity bridge
   (`eq:moffatt_ricca_single_tube_helicity`) over elastic-modulus imports.
5. Adds a compact-state exclusion from automatic LIA/KAM promotion.
6. Ties helicity bookkeeping to the single-tube Moffatt–Ricca specialization.

### Research Track

7. Adds `subsec:rt_compact_to_slender_state`: stretch parameter, conditional
   core-volume scaling, Compton-scale excitation hypothesis, Planck-scale
   uniform-core obstruction, and explicit promotion gates/falsifiers.
8. Adds `subsec:rt_kirchhoff_cosserat_guard`: stationary-shape correspondence
   only; rod energy is not a derived SST Hamiltonian.

### Bibliography

9. `MoffattRicca1992`, `Fukumoto2007`, `JohannsEtAl2021` (main + RT);
   `Mohr2025CODATA` in the Research Track.

## Epistemic result

- Ideal trefoil = certified compact reference / finite-core diagnostic input.
- Compact ideal knot is **not** an automatic LIA background.
- Kirchhoff–Cosserat quantities = `[BRIDGE / DIAGNOSTIC ONLY]`.
- Compact-to-slender path remains `[HYPOTHESIS]` until promotion gates pass.

## Deferred

- Biot–Savart / `F_swirl^max` mechanical-tension protocol
- Any promotion of millimetre or Planck scales to uniform electron-core radii
  without removing the stated obstructions

## Source

- Patch: `SST_CANON-v0.8.31-ideal-knot-regime.patch`
- Base: Canon v0.8.33 → edition `been_processed/v0.8.34/`
- Ingest: `scripts/apply_v0834.py`
