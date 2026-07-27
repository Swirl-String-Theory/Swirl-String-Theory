# SST Canon v0.8.28 patch package

This package upgrades the supplied v0.8.27 canon and research-track companion to v0.8.28.

## Files

- `SST_CANON-v0.8.28.tex` — patched main canon.
- `SST_CANON-v0.8.28-research-track.tex` — patched research-track companion.
- `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex` — speculative appendix with the translation-induced shape hypotheses marked retired.
- `SST_CANON-v0.8.28.pdf` — compile-verified combined canon, 226 pages.
- `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.pdf` — compile-verified speculative appendix.
- `SST_CANON-v0.8.27_to_v0.8.28.diff` — main-canon unified diff.
- `SST_CANON-v0.8.27-research-track_to_v0.8.28-research-track.diff` — research-track unified diff.
- `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1_to_v0.2.diff` — speculative-appendix unified diff.
- `SST-v0.8.28-combined.patch` — concatenated patch.
- `AUDIT-v0.8.27-action-phase-clock.md` — source audit and rationale.
- `BUILD_REPORT.txt` — compile/audit results.
- `SHA256SUMS.txt` — checksums.

## Core addition

The added bridge is

\[
H(P,I)=\sqrt{P^2c^2+E_0^2(I)},
\qquad
\dot\theta=\left.\partial_IH\right|_P
=\Omega_0{E_0\over H}
={\Omega_0\over\gamma}.
\]

It is classified as an orthodox Hamiltonian form, an SST bridge assumption, and a conditional derivation of internal phase dilation. It is **not** presented as a completed Euler/SST substrate derivation.

## Apply

The patch files were generated against the exact uploaded sources. The easiest route is to use the complete v0.8.28 files directly. To apply the combined patch manually, place the supplied v0.8.27 files in one directory using their canonical filenames and run:

```bash
patch -p0 < SST-v0.8.28-combined.patch
```

The main canon expects the companion filename `SST_CANON-v0.8.28-research-track.tex` in the same directory.
