# Validation — Maxwell–SST Kinetic Closure patch

## Completed checks

- **LaTeX compilation:** PASS, two consecutive `pdflatex -halt-on-error` passes on the locally available SST Canon source lineage after applying the complete main + research-track modifications.
- **Surrogate `git apply --check`:** PASS against the same locally available lineage renamed to the v0.8.35 target filenames.
- **Control-character scan:** no invalid control characters in the inserted modules.
- **Dimensional check:** `Gamma^2/(xi L)` has units `m^2 s^-2`, so the previous bare expression cannot be an energy in joules.
- **Knot stress:** `[c_i c_j/M_K] [f_K dGamma_K] = J m^-3 = Pa` when the phase-space integral gives number density.
- **Encounter-rate null model:** `[n][v][sigma] = m^-3 m s^-1 m^2 = s^-1`.
- **Canonical substrate scale:** `0.5 rho_f v_swirl^2 = 4.1877439e5 Pa` for `rho_f=7.0e-7 kg m^-3` and `v_swirl=1.09384563e6 m s^-1`.

## Important limitation

The exact byte-for-byte `SST_CANON-v0.8.35.tex` and `SST_CANON-v0.8.35-research-track.tex` sources were not present in the active runtime. The available v0.8.35 protocol review and an existing v0.8.35-to-v0.8.36 patch confirm the target filenames and later Canon structure, but they are not substitutes for the complete v0.8.35 source bytes.

Therefore:

- syntax/LaTeX validation is strong against the available Canon lineage;
- the generated patch is context-anchored and passes a surrogate `git apply --check`;
- **exact application to the user's local v0.8.35 checkout must still begin with `git apply --check`**.

No claim of byte-exact v0.8.35 application certification is made.
