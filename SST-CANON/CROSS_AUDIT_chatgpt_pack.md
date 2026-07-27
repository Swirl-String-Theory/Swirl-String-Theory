# Cross-audit: parallel ChatGPT evidence pack for canon v0.8.28

**Audited artefact:** `sst_v0_8_28_evidence_pack.zip` (ChatGPT), 1.5 MB, 37 files,
self-described as `pack_version: v0.8.28-evidence-port-1`, derived from
`sst_v0_8_17_evidence_pack_port`.

**Method:** unpacked, run independently in this container, diffed line-by-line
against the v0.8.17 predecessor and against the pack in `provenance/`.

---

## 1. Executive verdict

**Genuine port, honestly labelled, with one real bookkeeping defect and one
methodological weakness.** It reproduces its claimed result independently
(99/99 graded checks, return code 0), its epistemic boundary statement is
correct, and it contributes four things worth adopting. It is weaker than this
pack on live code alignment, canon patching, and residual-protocol validation.

Verdict on the ChatGPT pack as a standalone deliverable:
`[READY WITH MINOR PATCHES]` — the CODATA defect (§3.1) must be fixed before it
is used as a provenance record.

---

## 2. What was adopted into this pack

| # | Item | Why it is better than what I had | Where it now lives |
|---|---|---|---|
| A1 | `canon_snapshot/` — freeze the canon the results were produced against | My pack cited the canon by name only. A result with no frozen source cannot be re-audited later. | `canon_snapshot/` + `scripts/manifest_and_drift.py` |
| A2 | `MANIFEST.json` with sha256 per file | Ties every number to the exact artefact that produced it | `MANIFEST.json` |
| A3 | `provenance/` and `legacy_repo_patches/` carried forward | Keeps the v0.8.17 lineage inside the pack instead of assuming the old zip stays reachable | `provenance/`, `legacy_repo_patches/` |
| A4 | `frozen_anchors` section — check the canon's *printed* constants, not just its algebra | I checked identities; I did not systematically check that the printed anchors are correctly rounded. This is where two new defects were found. | suite section `frozen_anchors` |
| A5 | Worldline phase-rate check `\|dPhi/dT\| = E_0/(hbar gamma)` | An independent route to the same clock factor that I had not included | suite section `actionphase` |
| A6 | `P^4` term of the low-momentum expansion | I only verified the `P^2` term | suite section `actionphase` |
| A7 | `check_bool` harness method | Needed for boolean marker assertions inside the ledger | suite harness |
| A8 | `PORT_STATUS` table for historical patch disposition | Clean way to record what was retired vs rebased | `PORT_STATUS_v0_8_28.md` |

**A4 paid for itself immediately.** Applying the idea with a principled
tolerance — the half-ulp of the printed representation rather than a hand-picked
one — surfaced two defects that neither pack had caught:

- `r_c = 1.40897017e-15 m` is **mis-rounded in the 9th digit**. Both CODATA-2018
  and CODATA-2022 give `1.4089701...6`, so the correct 9 s.f. value is
  `1.40897016e-15`. Present 3× in the main canon, 7× in the research track,
  and in 29 corpus files. → **patch `0004`**.
- The legacy `rho_core = 3.8934358266918687e18` carries **17 printed digits**
  and is reproduced by *neither* the exact chain (dev `1.15e-7`) nor the rounded
  anchors (dev `1.02e-7`). It implies `r_c = 1.4089702165e-15`, i.e. a stale
  pre-closure radius. It still appears in SST-01 (Rosetta), SST-05, SST-19,
  SST-21, SST-30, SST-53, SST-69, SST-77. → suite section `legacy_anchors`.

The ChatGPT pack's own version of this check used `rel_tol=2e-7` for
`rho_horn`, which is looser than the defect it was pointed at, so it passed
green over both problems.

---

## 3. What was not adopted, and why

### 3.1 `[CRITICAL NOTE]` Mixed CODATA release — do not carry this forward

The suite silently changes

```
-ALPHA = 7.2973525693e-3      # CODATA-2018
+ALPHA = 7.2973525643e-3      # CODATA-2022
```

while leaving `M_E = 9.1093837015e-31` at its **CODATA-2018** value, and while
the file header and the `sstcore_alignment` section still say
`after patch 0003 CODATA-2018`. `PORT_STATUS` justifies the move
("v0.8.28 has later provenance"), but the move was made for `alpha` only.

Quantified in the new `codata` section: switching a *consistent* set from 2018
to 2022 moves every canon anchor by less than `1e-8`, i.e. below the printed
9 s.f. — and a *mixed* set moves them by less than `1e-8` too. So the error is
numerically immaterial today and **invisible to every anchor check**. It has to
be caught editorially, which is exactly why it should be fixed rather than
tolerated. This pack stays pinned to CODATA-2018 throughout and states the
pin explicitly.

The canon itself is ambiguous here: `\bibitem{Mohr2025CODATA}` cites CODATA-2022,
while all printed anchors are CODATA-2018-derived. **Recommendation:** one
sentence in the canon pinning the release used by `P_cal`, mirrored in SSTcore.

### 3.2 `[METHODOLOGY]` `canon_sync` validates only the bundled snapshot

`sec_canon_sync` reads `canon_snapshot/*.tex` — a copy that travels inside the
pack. It therefore cannot fail as long as the pack is intact, and it cannot
detect that the live canon has moved on. A frozen snapshot is valuable for
provenance and worthless as a drift detector unless something compares the two.

Adopted with the fix: `scripts/manifest_and_drift.py` hashes the snapshot
against a live canon directory and classifies `IDENTICAL` / `EOL ONLY` /
`CONTENT DRIFT`. `scripts/check_canon_markers.py` continues to take live paths.

Run against the ChatGPT snapshot, the drift check immediately reports the real
difference (§4.1).

### 3.3 `[SUPERSEDED]` Hand-mirrored SSTcore formulas

`sec_sstcore_alignment` still retypes the C++ formulas in Python and compares
them to canon algebra. That tests transcription, not the library. This pack
calls the installed `SSTcore 0.8.18` directly (17 live comparisons), which is
how the `compute_G_swirl(v, t_p, F_max, r_c, c)` argument order was verified
rather than assumed.

### 3.4 `[GAP]` No canon patches

The ChatGPT pack patches only its own verification suite
(`0001-upgrade-verification-suite-...`). It reports no defect in the canon text.
This pack ships four canon patches (`0001`–`0004`), all dry-run verified,
sequentially applied, with line endings preserved per file.

### 3.5 `[GAP]` Residual protocol asserted, not validated

Its `action_phase` section checks that the mass-shell algebra is self-consistent
— necessary, but it does not test whether `(Delta_shell, Delta_V, Delta_Omega,
Delta_q)` can *distinguish* anything. `scripts/rt_action_phase_residuals.py`
here adds the counter-model: an explicit `H_Pq` coupling drives `Delta_q` to
`1.9e-1`, monotone in `P`, while the separable bridge stays below `7e-10`.
Without that, `Delta_q = 0` is an untested claim about a test.

### 3.6 `[EDITORIAL]` Line endings normalized

The bundled main-canon snapshot was converted CRLF → LF (the research track is
LF in both copies, so only one file is affected). Harmless for reading, but any
patch generated against that copy will not apply cleanly to the CRLF working
file. Patch discipline for this project requires preserving the per-file style.

---

## 4. Findings the ChatGPT pack contributed as evidence

### 4.1 `[PROVISIONAL CANON UPDATE]` The DOI is filled in upstream

Its canon snapshot differs from Project Knowledge in exactly one line:

```
-\newcommand{\paperdoi}{}
+\newcommand{\paperdoi}{10.5281/zenodo.21628167}
```

Everything else is identical after line-ending normalization. So the local
working copy is ahead of Project Knowledge by a Zenodo DOI registration.
**No patch issued** — the upstream copy already has it; this is recorded so the
next Project Knowledge upload is recognised as the stale side.

### 4.2 `[RESOLVED]` The `\input` filename question

My previous audit flagged `\input{SST_CANON-v0.8.28-research-track}` (dots)
against the underscore filename in Project Knowledge, and could not decide from
the upload. The ChatGPT snapshot ships the files as
`SST_CANON-v0.8.28.tex` and `SST_CANON-v0.8.28-research-track.tex` — dotted.

**Conclusion: the local filenames use dots; Project Knowledge sanitizes them.**
The `\input` is correct and the earlier `[UNRESOLVED]` item is closed. The drift
checker accepts both spellings.

---

## 5. Where the two packs agree

Worth stating, because independent agreement is the only part of this that
carries evidential weight:

- Both find the v0.8.28 action–phase route to be an **imported orthodox
  mass shell**, not an SST derivation, and both refuse to upgrade the label.
- Both list the same four open tasks: identify a concrete hydrodynamic action
  `I`, derive the dispersion from the microscopic action, show species-independent
  limiting speed, and compute the residuals on resolved moving-knot solutions.
- Both keep `alpha` as an obstruction ledger with no pass/fail.
- Both keep the galactic sector research-track with `r_s` fitted.
- Neither found a fatal issue in v0.8.28.

Where they disagree, the disagreements are the two rounding defects in §2 and
the CODATA bookkeeping in §3.1 — none of which changes any physical conclusion.

---

## 6. Recommendation

1. Apply canon patches `0001`–`0004` from this pack.
2. Fix the mixed CODATA set in the ChatGPT suite before reusing it, or use the
   suite here, which is pinned and states the pin.
3. Add one canon sentence pinning the CODATA release for `P_cal`.
4. Plan a corpus-wide replacement of the stale 17-digit `rho_core` (29 files);
   this is out of scope for an evidence pack and should be one deliberate pass,
   not silent per-paper re-rounding.
5. Keep the snapshot + drift mechanism in all future packs.
