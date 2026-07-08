# Source conversation — Relativity Emergence (SR/GR from SST) → v0.8.13

Origin: audit conversation (Claude + ChatGPT) on whether SR/GR can be derived
from the SST substrate axioms. This is the source record for the v0.8.13 patch.

## What was integrated

- **Main canon** (`\ref{subsec:tensor_speed_naturalness}`, "Internal Tensor-Speed
  Naturalness"): the conditional `c_{13}=0` proposition, inserted right after
  "Observational Constraint from Tensor-Mode Speed". Upgrades the luminal
  tensor-speed condition from an external observational constraint to an internal
  naturalness condition, conditional on the SST transverse-mode identification.
  Status: `[DERIVED, conditional]`, explicitly NOT a derivation of the
  Einstein–Hilbert dynamics; limited to the spin-2 sector.

- **Research track** (`\ref{sec:rt_relativity_emergence_ladder}`, "Relativity
  Emergence Ladder in SST"): the seven-component ladder with honest epistemic
  labels —
  1. primitive structure + Swirl-Clock,
  2. light-clock Lorentz factor `[DERIVED, conditional]`,
  3. monometricity theorem target `[OPEN CANON GAP: MONOMETRICITY]` (two speeds
     `c` and `v_swirl = αc/2`),
  4. analogue-metric bridge `[CONDITIONAL BRIDGE]` (only for the hyperbolic
     transverse sector; not from incompressibility alone),
  5. weak equivalence principle (energy-source + metric-coupling routes),
  6. Newtonian limit `[CONDITIONAL]`,
  7. Einstein dynamics — three candidate routes (thermodynamic/Jacobson,
     Sakharov induced gravity with `N_req ≈ 7.6×10³⁹`, IR-EFT universality with
     the severe Λ problem `ρ_f/ρ_Λ ≈ 1.2×10²⁰`, `ρ_core/ρ_Λ ≈ 6.6×10⁴⁴`),
  plus the tensor-speed naturalness restatement and a final honest status
  statement.

- **Bibliography** (main canon `thebibliography`): Einstein1905, Einstein1915,
  BarceloLiberatiVisser2011, Jacobson1995, Sakharov1967, JacobsonMattingly2001,
  FosterJacobson2006, Abbott2017GW170817, Mohr2025CODATA, Planck2018Cosmology.
  (Unruh1981 already present; reused, not duplicated.)

## Key epistemic verdict (from conversation)

- Canonizable now: small `c_{13}=0` proposition + status labels.
- Research-track now: Relativity Emergence Ladder.
- NOT canonizable now: full Einstein field equations from incompressible
  Euler/Biot–Savart primitives — flagged as an open program with three routes.
- Correction retained: the analogue/Unruh route needs a hyperbolic transverse
  sector; it does not follow from incompressibility alone.

## Build

```powershell
cd SST-CANON/been_processed
python apply_v0813.py
```
