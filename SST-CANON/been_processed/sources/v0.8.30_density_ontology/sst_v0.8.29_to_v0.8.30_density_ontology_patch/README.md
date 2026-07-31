# SST Canon v0.8.29 -> v0.8.30

## Scope

This patch is the density-ontology and historical-provenance release. It does not attempt a new numerical derivation of `rho_f`.

The patch:

1. separates the unknown material substrate density `rho_sub` from the calibrated effective response `rho_f = rho_eff^(0)`;
2. introduces distinct symbols for rotational microinertia `J_omega` and line inertia `mu_l`;
3. records the traced VAM-7 origin of the inherited `7e-7` decimal;
4. corrects the historical dimensional interpretation from `kg m^-3` to `kg m^-1`;
5. freezes `rho_f` as a constant quasi-static response coefficient in the canonical master equation;
6. preserves the v0.8.29 SSDL, force-gate, uncertainty, and epoch-invariance audit unchanged.

## Epistemic result

The release keeps

```text
rho_f = rho_eff^(0) = 7.0e-7 kg m^-3
[CALIBRATED EFFECTIVE RESPONSE]
```

and separately records

```text
J_omega^VAM ~= 6.84e-7 kg m^-1
[HISTORICAL ORIGIN / CONDITIONAL ANSATZ]
```

No equality between these quantities is asserted. A conversion requires an independently derived geometry, participation measure, and squared length.

## Files

- `patches/0001-main-canon-density-ontology.diff`
- `patches/0002-research-track-historical-provenance.diff`
- `patches/SST_CANON-v0.8.29_to_v0.8.30-combined.diff`
- `patched/SST_CANON-v0.8.30.tex`
- `patched/SST_CANON-v0.8.30-research-track.tex`
- `validation/SST_CANON-v0.8.30-validation-build.pdf`
- `VALIDATION_REPORT.md`
- `PATCH_MANIFEST.yml`
- `SHA256SUMS.txt`

## Apply with GNU patch

From a directory containing the two v0.8.29 source files:

```bash
./apply_patch.sh
```

The script creates new v0.8.30 files and leaves the v0.8.29 inputs unchanged.

Manual application:

```bash
patch --batch -o SST_CANON-v0.8.30.tex \
  SST_CANON-v0.8.29.tex \
  < patches/0001-main-canon-density-ontology.diff

patch --batch -o SST_CANON-v0.8.30-research-track.tex \
  SST_CANON-v0.8.29-research-track.tex \
  < patches/0002-research-track-historical-provenance.diff
```

## Explicitly deferred

The following remain planned for later releases:

- v0.8.31: rotor relabeling, twist/bend guard, and participation-gap audit;
- v0.8.32: preregistered Biot-Savart tension protocol for `F_swirl^max`;
- any dependency-DAG promotion based on new numerical results.
