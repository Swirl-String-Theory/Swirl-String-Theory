# SST CANON v0.8.32 patch package

## Purpose

This package applies only the scientifically defensible recoveries from `SST-00_Lagrangian.tex` to the current v0.8.31 architecture.

### Release Canon

- Adds a differential-form degree guard for a covariant vortex-worldsheet description.
- States the correct two-form worldsheet coupling and one-cycle dual charge diagnostic.
- Adds an explicit non-identification guard: no automatic `q_B = Gamma_0`, no electromagnetic identification, and no claim that the finite core has already been reduced to a worldsheet EFT.
- Replaces director-counting and pure-gauge shortcuts by an explicit gauge-emergence non-derivation guard.

### Research Track

- Adds a source-coupled Kalb--Ramond/two-form worldsheet action with positive-energy sign convention, conserved worldsheet current, correct form degrees, finite-core matching, slenderness, reconnection, and promotion gates.
- Adds a dimensionally consistent helicity-response operator while separating true parity-odd response from parity-even chirality alignment.
- Adds a staged gauge-emergence certification ladder: mode census, nontrivial curvature, closure, Jacobi, representation/charge separation, anomalies, running couplings, and held-out phenomenology.

### Non-release Speculative Appendix

- Adds an optional Bell/Born/no-signalling test programme with measurement-independence declaration, no-signalling marginals, CHSH/Tsirelson bounds, loophole controls, anti-target-tuning rules, and held-out Born-frequency tests.
- This file remains outside the release Canon and Research Track.

## Explicitly not imported

- The old covariant SST master action.
- The density substitutions between `rho_f`, `rho_m`, and `rho_core`.
- The linear hypercharge map and fitted anomaly cancellation.
- The claim that three `SO(3)` directors derive the Standard Model gauge algebra.
- The claim that a constant theta term dynamically stabilizes vortex knots.
- The internally inconsistent mass tables and helicity classifier.

## Files

- `patched/SST_CANON-v0.8.32.tex`
- `patched/SST_CANON-v0.8.32-research-track.tex`
- `patched/SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex`
- `diffs/0001-main-canon-v0.8.31-to-v0.8.32.diff`
- `diffs/0002-research-track-v0.8.31-to-v0.8.32.diff`
- `diffs/0003-nonrelease-spec-v0.2-to-v0.3.diff`
- `diffs/SST_CANON-v0.8.32-combined.diff`

## Application

The diffs use canonical filenames without the upload suffix `(2)`. Apply from the directory containing the v0.8.31 files, or use the complete patched files directly.

## Validation

- Integrated main Canon compiled successfully with `pdflatex` in three passes.
- Non-release appendix compiled successfully in two passes.
- Final passes contained no unresolved citations, unresolved references, fatal errors, or duplicate-label warnings introduced by this patch.
- All three incremental diffs passed `patch --dry-run -p0` against the supplied source files.
- The detailed result is in `audit/compile-and-structure-audit.txt`.
