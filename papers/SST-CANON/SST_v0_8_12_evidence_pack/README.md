# SST Canon v0.8.12 — Evidence Pack

Consolidated verification + patch bundle for SST Canon v0.8.12, produced during
the internal audit + external (Gemini) audit response cycle.

## Contents

```
SST_v0_8_12_evidence_pack/
├── README.md                  (this file)
├── AUDIT_RESPONSE.md          per-point verdict on the external audit + actions
├── run_metadata.json          timestamp, env, CODATA release, per-claim PASS/FAIL,
│                              standalone exit codes, patch dry-run status
├── patches/
│   ├── 0001-chronos-kelvin-vorticity.patch          SSTcore: vorticity factor-2 (claim 9)
│   ├── 0002-rho-horn-alias.patch                     SSTcore: rho_core->rho_horn alias (claim 8)
│   ├── 0003-codata2018-pin-and-provenance.patch      SSTcore: CODATA-2018 pin + provenance
│   ├── 0004-spoorAB-main-canon-notes.patch           Canon: alpha-spectro, zeta(3), Madelung notes
│   ├── 0005-spoorAB-research-track-notes.patch       Research-track: galactic dp, Meissner, horn-vol
│   └── sstcore_v0_8_12_alignment_ALL.patch           combined 0001-0003
├── scripts/
│   ├── sst_v0_8_12_verification_suite.py             11-section unified suite (46 checks)
│   ├── reproduce_pauli_barrier.py                    claim 38 [CALIBRATED BENCHMARK]
│   ├── reproduce_em_qed_normalization.py             claims 61/67 (m_e/e; B_core=B_QED)
│   └── fit_galactic_swirl_rotation_sparc.py          claim 42 [RESEARCH-TRACK] (also in-suite: section 'galactic')
└── results/
    └── suite_results.json                            machine-readable suite output
```

## Reproduce

```bash
# full unified verification (46/46 expected)
python3 scripts/sst_v0_8_12_verification_suite.py
python3 scripts/sst_v0_8_12_verification_suite.py --list
python3 scripts/sst_v0_8_12_verification_suite.py --only sstcore_alignment

# standalone reproductions
python3 scripts/reproduce_pauli_barrier.py            # 7.69365 eV
python3 scripts/reproduce_em_qed_normalization.py     # B_core=B_QED=4.414e9 T
python3 scripts/fit_galactic_swirl_rotation_sparc.py  # demo galaxy; --sparc for real data
```

## Apply patches

```bash
# SSTcore source tree:
cd SSTcore-v0.8.12
patch -p1 < .../patches/0001-chronos-kelvin-vorticity.patch
patch -p1 < .../patches/0002-rho-horn-alias.patch
patch -p1 < .../patches/0003-codata2018-pin-and-provenance.patch
#   (note: 0001/0002 add C++ symbols -> rebuild the pybind11 extension)

# Canon LaTeX:
patch -p1 < .../patches/0004-spoorAB-main-canon-notes.patch        # SST_CANON-v0_8_12.tex
patch -p1 < .../patches/0005-spoorAB-research-track-notes.patch    # ...-research-track.tex
```

All five patches are `patch -p1` clean (dry-run verified; see
`run_metadata.json -> patch_dryrun_pass`), CRLF preserved.

## Epistemic note

The verification suite proves the *deterministic* (algebra / calibrated-identity
/ topological / code-alignment) block. Calibrated identities are labeled
`[CALIBRATED]`, posited inputs `[POSIT]`, and the alpha sector is an OBSTRUCTION
ledger — NOT a derivation of alpha. The galactic sector is research-track:
`r_s` is fitted, not derived (coherence-length lemma open). Dependencies: numpy
(matplotlib optional for the galactic plot).
