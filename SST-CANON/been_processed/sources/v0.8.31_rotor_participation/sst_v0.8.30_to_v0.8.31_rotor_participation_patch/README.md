# SST Canon v0.8.30 -> v0.8.31

## Scope

This is the rotor-status, twist/bend, and micro--macro participation audit release.
It does not claim a new derivation of `rho_f`, `J_omega`, or a new SST primitive.

The patch:

1. defines `rho_f = rho_eff^(0)` exclusively as the isotropic quasi-static limit of the effective-inertia response;
2. classifies the compact Compton-gap rotor normalization as a matching ansatz;
3. shows that the rotor construction reproduces the horn-envelope line-inertia coefficient rather than a new constant;
4. records `c_omega = v_swirl` as a definitional identity, not an independent validation;
5. separates linear internal twist waves from quadratic Kelvin bending modes;
6. quantifies the unresolved participation gap `phi_dyn = 5.7229e-26`;
7. records the equivalent response length `ell_rho,eq = 5.8897 mm` strictly as a diagnostic reparameterization;
8. introduces a weighted, frequency-dependent macro-response representation and explicit promotion gates.

## Central status result

```text
J_omega^rot = pi r_c^2 rho_horn^eff
             = 2.4282114e-11 kg m^-1
[REFORMULATION / MATCHING ANSATZ]
```

```text
rho_f = rho_eff^(0) = 7.0e-7 kg m^-3
[CALIBRATED QUASI-STATIC EFFECTIVE RESPONSE]
```

The bridge between them remains open. Neither `phi_dyn` nor `ell_rho,eq` is a predicted cell size, coherence length, or vortex spacing.

## Files

- `patches/0001-main-canon-quasistatic-response-guard.diff`
- `patches/0002-research-track-rotor-participation-audit.diff`
- `patches/SST_CANON-v0.8.30_to_v0.8.31-combined.diff`
- `patched/SST_CANON-v0.8.31.tex`
- `patched/SST_CANON-v0.8.31-research-track.tex`
- `validation/SST_CANON-v0.8.31-validation-build.pdf`
- `VALIDATION_REPORT.md`
- `PATCH_MANIFEST.yml`
- `SHA256SUMS.txt`

## Apply with GNU patch

From a directory containing the two v0.8.30 source files:

```bash
./apply_patch.sh
```

The script creates new v0.8.31 files and leaves the v0.8.30 inputs unchanged.

Manual application:

```bash
patch --batch -o SST_CANON-v0.8.31.tex \
  SST_CANON-v0.8.30.tex \
  < patches/0001-main-canon-quasistatic-response-guard.diff

patch --batch -o SST_CANON-v0.8.31-research-track.tex \
  SST_CANON-v0.8.30-research-track.tex \
  < patches/0002-research-track-rotor-participation-audit.diff
```

## Explicitly deferred

- v0.8.32: preregistered resolved Biot--Savart/mechanical-tension protocol for `F_swirl^max`;
- any promotion of the millimetre equivalent length to a physical scale;
- any dependency-DAG change based on a fitted participation factor;
- changes to the nonrelease speculative document.
