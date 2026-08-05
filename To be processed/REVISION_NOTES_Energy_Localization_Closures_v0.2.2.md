# Revision notes — Energy-Localization Closures, v0.2.1 → v0.2.2

Date: 2 August 2026
Scope: editorial only. No physics, no numerics, no claims changed.

## Changes

**1. Manuscript version bumped** (line 47)
`manuscript version 0.2.1` → `manuscript version 0.2.2`

**2. Companion-manuscript version restored** (bibliography, `\bibitem{Iskandarani2026}`)
`preprint, manuscript version 0.2.1 (2026).` → `preprint, manuscript version 0.2.0 (2026).`

Rationale: the v0.2.0 → v0.2.1 revision bumped this manuscript's own version, and the
global replace also caught the citation to the *companion* paper ("Angular-projector
normalization and finite-core energetics of tight knotted vortex tubes"), which is itself
at v0.2.0 and was not revised. Collateral edit, now reverted.

**3. Gate/test count reconciled with the abstract** (§ Preregistered falsification gates,
intro sentence)

The abstract states "five independent gates" and enumerates G0–G4 — correct. The
`description` list, however, ran G0 through G5 under a single "gate structure" heading,
making it read as six gates. The intro sentence now separates the two categories
explicitly and restates the gate ordering in one line:

> The present article supports the following structure: five theorem gates **G0**–**G4**,
> which must be discharged before any comparison with measurement, followed by a single
> out-of-sample comparison **G5**. Only **G4** can identify a dimensionless model
> coefficient with the electromagnetic coupling; **G0**–**G3** fix the geometric and
> hydrodynamic input that **G4** consumes.

No item labels were changed; `\cref` targets and `\label`s are untouched.

## Verification performed on v0.2.2

- Clean build from scratch with `latexmk -pdf` (revtex4-2, TeX Live).
  **18 pages**, exit status 0.
- **Zero** undefined references or citations in the final pass.
- **Zero** overfull/underfull box warnings.
- **Zero** orphan `\bibitem`s: every one of the 21 bibliography entries is cited at least
  once (`Ohanian1986`, the orphan in v0.2.0, remains correctly cited in
  § "Formal speed relative to c").
- Unified diff `Energy_Localization_Closures_v0.2.1_to_v0.2.2.diff` verified with
  `patch -p0 --dry-run` against the v0.2.1 source: 3 hunks, applies cleanly.
- Line endings: LF throughout, unchanged from v0.2.1.

## Numerical content — unchanged and re-verified

All values re-checked against CODATA 2022 via `scipy.constants`:

| quantity | value |
|---|---|
| `\alpha_geom^{-1}` = (8π/3)·L_D | 137.153 283 2132 |
| residual δ | −855.13 ppm |
| ρ_horn | 3.8934 × 10^18 kg m⁻³ |
| ρ_fil | 5.6824 × 10^16 kg m⁻³ |
| ρ_C | 1.0071 × 10^7 kg m⁻³ |
| ρ_horn / ρ_fil | 68.518 000 = 1/(2α) |
| ρ_fil / ρ_C | 5.642 332 × 10^9 = 16/α⁴ |
| ρ_C closed form | (2/π)·m_e/λ̄_C³ |
| v_θ(a)/c | 274.31 = 2/α_geom |
| v_θ(2ℓ*)/c | 4.1888 = 4π/3 |
| V_tube^geom / V_sphere | 24.5362 = (3/4)(ℓ/r) |

## Status

Submission-ready as an obstruction/consistency paper. No open editorial defects known.
