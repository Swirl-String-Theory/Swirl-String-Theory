# Validation report - SST CANON v0.8.31 to v0.8.32

## Input identity

The patch was generated against the user's exact local `(2)` source files.

| Source | SHA-256 |
|---|---|
| `SST_CANON-v0.8.31.tex` | `06c7f5bacfde31d1503bc45de8e7854946b56924c4c18551ecb99d05402f55b3` |
| `SST_CANON-v0.8.31-research-track.tex` | `312e87055334681add3b680284d0e9a50063fce7b13c689386aa6b4e4335b18c` |
| `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex` | `e1b24a4d22a4261b748467352eb37e5c3d1bc8093fafc1ed677b2803110a0236` |

## Patch integrity

- GNU `patch --dry-run`: passed for both Canon files.
- Applied outputs are byte-identical to the packaged v0.8.32 sources.
- The non-release speculative document is byte-identical to its v0.8.31 input.
- Main output SHA-256: `87d9c54e99593dff9d672a6f52da7fd6b3a3e98754708d6c502fe9131a9e9e30`
- Research Track output SHA-256: `a3bfff07e8461396dad6402ba8e02f5e41e79b54fb9ae4ea21145ef8fcea174d`

## Scientific gates implemented

1. `rho_ref = 7.0e-7 kg m^-3` is retained only as:
   `[LEGACY REFERENCE NORMALIZATION / PROVENANCE INVALIDATED]`.
2. The physical `rho_f == rho_eff^(0)` is:
   `[UNFIXED QUASI-STATIC EFFECTIVE RESPONSE]`.
3. `rho_f` is removed from the primitive calibration set.
4. The four VAM-7 provenance defects are registered:
   dimensional failure, documented `8/3` volume backfit, cosmological error
   of approximately `1.9e18`, and incompatible vorticity scales differing
   by `2/alpha ~= 274.07`.
5. The source-free radiation/torsion normalization no-go is added.
6. A complete pre-patch occurrence ledger classifies all 206 density-symbol
   occurrences under the A/B/C/Q/X protocol.
7. SSDL is retained only as a legacy numerical coincidence diagnostic.
8. Selected absolute numerical amplitudes are explicitly marked
   legacy-reference normalized.

## Scaling ledger

- Main Canon occurrences: 85
- Research Track occurrences: 121
- Total: 206
- Class A: 12
- Class B: 18
- Class C: 139
- Class Q: 9
- Class X: 28

Class C and Q entries are candidate dependencies, not automatically valid
calibration observables. The v0.8.32 text records that no present class-C or
class-Q measurement map independently fixes `rho_eff^(0)`.

## LaTeX build

Command:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_CANON-v0.8.32.tex
```

Result:

- Build completed successfully.
- PDF: 237 A4 pages.
- Fatal LaTeX errors: 0.
- Unresolved references: 0.
- Unresolved citations: 0.
- Duplicate labels: 0.
- The raw-underscore keyword error in the local v0.8.31 source is removed.

The inherited document still emits non-fatal overfull/underfull box warnings
in older sections. These were not globally reformatted because this patch is
scientifically scoped and should not introduce bulk typography changes.
The new primitive-status, source-free normalization, Lorentz-force status,
VAM-7 provenance, participation, and scaling-audit pages were rendered and
visually inspected; no clipping or overlap was observed on those pages.

## Scope exclusion

The v0.8.32 patch does not add the preregistered
`F_swirl^max`/Biot-Savart mechanical-tension protocol. That remains a later,
separate patch so that the orphaned-normalization adjudication stays
independently reviewable.
