# SST v0.8.12 evidence pack -> SST Canon v0.8.17 port audit

## Executive verdict

The evidence pack remains usable for SST Canon v0.8.17, but it must be interpreted as a mixed bundle:

1. **Numerical verification suite:** still valid for the stable numerical claims; it passes in this environment.
2. **Canon text patches 0004/0005:** already present in the supplied `SST_CANON-v0.8.17(1).tex` and `SST_CANON-v0.8.17-research-track(1).tex`.
3. **Workbench patch 0008:** still valid, but only if `scripts/ideal_source.py` and `scripts/ab_knot.py` are installed with the patched GUI script.
4. **SSTcore / Workbench code patches 0001--0003 and 0006--0007:** semantically still relevant, but their live integration cannot be re-verified from the canon `.tex` files alone; apply/test inside the respective repositories.

## Verification result

The v0.8.17-compatible verification suite was run after porting the header/status text.

```text
return code: 0
                 (correct prefactor m_e/e; B_core=B_QED=4.414e9 T)
```

The suite is still a numerical claim ledger. It is not a LaTeX compilation test and it does not prove full canon consistency.

## v0.8.17 canon text patch status

### 0004 — main canon notes

Status: **applied in supplied v0.8.17(1)**.

Port file:
`patches/0004-spoorAB-main-canon-notes-v0.8.17.patch`

Markers confirmed in patched main canon:

- `generic calculus property`
- `alpha-suppressed`
- `Madelung amplitude does not violate substrate incompressibility`

### 0005 — research-track notes

Status: **applied in supplied v0.8.17-research-track(1)**.

Port file:
`patches/0005-spoorAB-research-track-notes-v0.8.17.patch`

Markers confirmed in patched research-track:

- `2.8\times10^{3}\,\mathrm{Pa}`
- `orthodox Cooper-pair description`
- `not a stiffness theorem`

### 0008 — fseries / ideal resolver

Status: **still correct but incomplete as a standalone patch**.

Required integration:

1. Copy `scripts/ideal_source.py` and `scripts/ab_knot.py` into each Workbench `gui_tabs/` directory that contains `generate_knot_fseries.py`.
2. Apply `patches/0008-generate-fseries-ideal-source-and-relax-off.patch` to both copies of `generate_knot_fseries.py`.
3. Test with an AB id such as `3:1:1`.
4. Confirm the emitted `.fseries` header says either `unrelaxed Fremlin ideal` or `re-relaxed (NON-canonical toy functional)`.

## Files in this bundle

```text
patches/
  0004-spoorAB-main-canon-notes-v0.8.17.patch
  0005-spoorAB-research-track-notes-v0.8.17.patch
  0008-generate-fseries-ideal-source-and-relax-off.patch
  0001/0002/0003/0006/0007 original code patches
  sstcore_v0_8_17_alignment_ALL.patch

scripts/
  sst_v0_8_17_verification_suite.py
  ideal_source.py
  ab_knot.py
  run_helicity_AB.py
  reproduce_pauli_barrier.py
  reproduce_em_qed_normalization.py
  fit_galactic_swirl_rotation_sparc.py

patched/
  SST_CANON-v0.8.17.evidence-patched.tex
  SST_CANON-v0.8.17-research-track.evidence-patched.tex

results/
  suite_results_v0_8_17.json
  suite_stdout.txt
  suite_stderr.txt
```

## Recommended merge order

1. Main canon text patch 0004, if not already present.
2. Research-track text patch 0005, if not already present.
3. Workbench GUI patch 0008 with helper files.
4. Repository-local verification:
   - run `python scripts/sst_v0_8_17_verification_suite.py`
   - grep for the six critical marker phrases in the canon files.
   - run GUI fseries generation with `relax=False`.

## Do not overclaim

The suite still contains calibrated identities and obstruction ledgers. In particular:

- `G_swirl` remains calibrated while `t_p` contains orthodox `G`.
- the alpha finite-cell section remains an obstruction/coincidence ledger, not an alpha derivation.
- SPARC/galactic machinery remains research-track because the coherence-length law is not derived.
- `rho_f` is a microscopic/effective SST density; unscreened galaxy-scale use is explicitly falsifiable.
