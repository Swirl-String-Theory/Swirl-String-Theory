# SST Canon v0.8.28 — evidence pack audit

**Auditor role:** adversarial reviewer / consistency auditor
**Sources used (CANON_SOURCE_HIERARCHY §1):**

| Level | File | Role here |
|---|---|---|
| 1 | `SST_CANON-v0_8_28.tex` (7313 lines, `\canonversion{0.8.28}`) | primary source of truth |
| 1 | `SST_CANON-v0_8_28-research-track.tex` (11152 lines) | companion, `\input` at main-canon line 6684 |
| 4 | `SSTcore` **0.8.18** (PyPI, installed) | computational mirror |
| — | `sst_v0_8_17_evidence_pack_port.zip` | predecessor pack, ported forward |

**Predecessor:** `AUDIT_REPORT_v0_8_17.md` (v0.8.12 suite ported to v0.8.17).
This edition re-derives the ledger against v0.8.28 rather than re-labelling it.

**Pack revision v2** merges the reviewed material from a parallel ChatGPT
evidence pack. See `CROSS_AUDIT_chatgpt_pack.md` for the point-by-point review
of what was adopted, what was rejected, and why. New findings from that merge
are m6, m7 and m8 below; the suite grew from 111 to 128 graded checks.

---

## 1. Executive verdict

**[READY WITH MINOR PATCHES].**

The v0.8.28 numerical layer is internally consistent. All 111 graded checks in
the new suite pass, including every identity in the primitive calibration chain,
the corrected `16 pi^2` Rydberg form, the `M_0 = (m_e/4) L_tot` transparency
identity, and the full action–phase residual set. No fatal issue was found.

Three things are worth stating plainly, because the pack is designed not to
flatter the canon:

1. **The v0.8.28 delta is a guard, not a new derivation.** The action–phase
   mass–shell route (`H = sqrt(P^2c^2 + E_0^2)` → `d(theta)/dT = Omega_0/gamma`)
   is textbook Hamiltonian mechanics applied to an assumed carrier. Its canon
   value is that it *retires* the flattening/stretching/core-thinning
   hypotheses and supplies a falsifiable residual protocol. The canon labels
   this correctly (`[ORTHODOX FORM / SST BRIDGE / CONDITIONAL DERIVATION]`);
   that label must survive future editions.
2. **The residual protocol is discriminating.** This was not obvious and is now
   demonstrated: a counter-model with an explicit momentum–shape coupling
   returns `Delta_q` up to `1.9e-1`, growing monotonically in `P`, while the
   separable bridge returns `< 7e-10`. A reported `Delta_q = 0` therefore
   carries information rather than being vacuously satisfiable.
3. **The pass rate is not evidence for SST.** 111/111 confirms that the canon is
   algebraically self-consistent under its own calibration. Most of those checks
   are `[CALIBRATED]` identities whose agreement is forced once
   `vchar = alpha c/2` is adopted. The ledger says so at every such line.

---

## 2. Fatal issues

**None identified.**

Specifically checked and *not* found: dimensional errors in the primitive chain,
duplicate `\label` keys (320 main / 505 RT, zero duplicates), unresolved
references (0 after accounting for the `\input`), sign or factor-2 regressions
in `F_swirl^max`, and collapse of `[CALIBRATED]`/`[CONDITIONAL]` into
`[DERIVED]` (the v0.8.4 regression class).

---

## 3. Major issues

### M1 — SSTcore lags the canon by ten versions `[CODE LAG]` / `[API GAP]`

Installed `SSTcore 0.8.18` vs canon `v0.8.28`. The primitive-chain layer is
still aligned: all 17 live code-vs-canon comparisons in section
`sstcore_alignment` pass, including `compute_G_swirl`, the non-reduced
`geometric_gate`, and the patched `vorticity_from_swirl_clock` convention.

What is missing:

- no entry point for the v0.8.28 action–phase mass–shell bridge, hence no code
  path for `Delta_shell`, `Delta_V`, `Delta_Omega`, `Delta_q`;
- no helper exposing `M_0(T) = (m_e/4) L_tot(T)`, so the v0.8.26 transparency
  identity is enforced only in Python.

**Recommendation:** `[CODE PATCH REQUIRED]`. Minimum viable surface:
`sst_action_phase.h` / `.cpp` with `mass_shell_hamiltonian(P, E0)`,
`internal_phase_rate(P, E0, Omega0)`, `residual_vector(...)`, plus
`sst_action_phase_py.cpp` bindings and a regression test pinned to
`results/rt_action_phase_residuals.json`.
**Do not** patch the canon for this; the canon is ahead, which is the correct
direction.

### M2 — `rho_f` provenance remains the single open primitive

The canon states this itself (`[CALIBRATED / PROVENANCE GUARD]`, §2.2):
`rho_f = 7.0e-7 kg m^-3` at **two significant figures**, with no stated
independent calibration observable. Everything linear in `rho_f` inherits it:

| Quantity | Value in this pack | Usable precision |
|---|---|---|
| `rho_E` | `4.1877439e5 Pa` | 2 s.f. |
| `rho_m` | `4.659494e-12 kg m^-3` | 2 s.f. |
| Pauli benchmark | `7.69 eV` | 1–2 s.f. |
| `T_KT` (Onsager) | `3.783383e-1 K` | 2 s.f. |

The suite prints these to full float precision *because they are algebra
checks*, and flags the ceiling in the same section. **Reviewer risk:** any
downstream text quoting `T_KT = 0.3783 K` or the Pauli barrier to three digits
is over-claiming. Recommend a canon-level sentence forbidding it, or the
demotion to an interval-valued parameter the guard already anticipates.

### M3 — Benchmark table still reads as a five-for-five mass prediction

`Table tab:benchmark_summary_structure` (main canon, `subsec:integration_benchmarks`)
lists `e`, `mu`, `tau`, `p`, `n` with `m_exp = m_SST` and `rel. error = 0`.
The `[CRITICAL NOTE]` beneath it correctly says this is *exact-closure* mode and
not an independent prediction — but the table itself, which is what a referee
scans first, is a perfect-agreement table with information content zero.

This was flagged at v0.8.27 and is **unchanged in v0.8.28**.

**Recommendation:** `[CANON PATCH REQUIRED]` — see patch `0003`, which makes the
tautology visible inside the table (caption + column headers), so the guard no
longer depends on the reader reaching the note below.

### M4 — Rydberg and gate identities remain the highest-value referee targets

Unchanged structurally, restated because the pack now verifies both directions:

- `R_inf = vchar^3/(pi r_c c^3)` reduces exactly to `alpha^2 m_e c/(4 pi hbar)`;
  `m_e` hides in `r_c`, `alpha` in both `vchar` and `r_c`.
- `lambda_c/(pi r_c) = 4/alpha` requires the **non-reduced** `lambda_c = h/(m_e c)`.
  With the reduced wavelength the gate is `(4/alpha)/(2 pi) = 87.24` (audit
  BG-1). SSTcore uses the non-reduced form; canon and code agree.

Both are labelled correctly today. The audit note is: these are the two places
where a single careless edit converts a consistency check into an apparent
derivation of `alpha`.

---

## 4. Minor issues

### m1 — stale `omega_c` in the research track (8 occurrences) `[CANON PATCH REQUIRED]`

The RT companion prints `omega_c = 7.76344066e20 s^-1` in eight places. Every
CODATA route gives `7.7634407e20`:

| Route | `omega_c` (s^-1) |
|---|---|
| CODATA-2018 `m_e c^2/hbar` | `7.763440711050e20` |
| CODATA-2022 `m_e c^2/hbar` | `7.763440721618e20` |
| from `m_e c^2 = 0.51099895000 MeV` | `7.763440711108e20` |
| **canon printed** | **`7.76344066e20`** |

The 8th significant digit is wrong (rel. dev. `6.4e-9`), and the three
`Omega_e(V)` entries in the Compton specialization table were computed from the
stale value, so they carry the same error. Patch `0002` fixes all eleven values.

### m2 — `F_swirl^max` printed value `[CANON PATCH REQUIRED]`

Main canon prints `29.053507 N` (2 occurrences). The calibrated chain gives
`29.0535101 N`; the 7th significant digit should read `29.053510`. The canon's
own statement that the Rydberg form agrees "to ~1e-7 relative precision" is
consistent with this, so only the printed constant is wrong. Patch `0001`.

### m3 — companion coupling is `\input`, not standalone `[RESOLVED — no action]`

The main canon `\input`s the research track at line 6684 inside
`\researchtrackincludedtrue`. Consequently the 35 main→RT and 14 RT→main
pointers all resolve on a normal compile and the "zero undefined references"
standard is met. The RT file has no preamble and therefore **cannot** be
compiled standalone — worth recording so no future edition tries. The marker
checker reports these as `[WARN]`, not `[FAIL]`.

### m4 — filename form of the `\input` `[RESOLVED]`

Line 6684 reads `\input{SST_CANON-v0.8.28-research-track}` (dots), while the
file supplied in Project Knowledge is `SST_CANON-v0_8_28-research-track.tex`
(underscores). **Resolved by the parallel ChatGPT pack**, whose canon snapshot ships the files
with dotted names (`SST_CANON-v0.8.28.tex`). The local filenames use dots;
Project Knowledge sanitizes them on upload. The `\input` is correct and no
action is needed. `scripts/manifest_and_drift.py` accepts both spellings.

### m6 — `r_c` printed value mis-rounded in the 9th digit `[CANON PATCH REQUIRED]`

`r_c = 1.40897017e-15 m` appears 3x in the main canon and 7x in the research
track. The computed value is `1.4089701622e-15` (CODATA-2018) or
`1.4089701594e-15` (CODATA-2022); **both** round to `1.40897016e-15` at 9 s.f.
The printed 9th digit is therefore wrong under either release. Deviation
`5.51e-9` — immaterial physically, but it propagates: the same string appears in
29 files across the paper corpus. Patch `0004` fixes the two canon files only.

### m7 — legacy 17-digit `rho_core` has unknown provenance `[REMOVE FROM CANON]`

`rho_core = 3.8934358266918687e18 kg m^-3` is reproduced by neither the exact
v0.8.28 chain (dev `1.15e-7`) nor the rounded anchors (dev `1.02e-7`). Inverting
it gives `r_c = 1.4089702165e-15 m`, i.e. a pre-closure radius. Its 17 printed
digits are spurious; roughly 7 are meaningful and the 8th onward is wrong.

Still present in SST-01 (Rosetta, line 129), SST-05, SST-19, SST-21, SST-30,
SST-53, SST-69, SST-77. **Not patched here** — a corpus-wide replacement should
be one deliberate pass with a stated target precision, not silent per-paper
re-rounding. Tracked by suite section `legacy_anchors`.

### m8 — canon does not pin a CODATA release `[CANON PATCH RECOMMENDED]`

The bibliography cites `Mohr2025CODATA` (CODATA-2022) while every printed anchor
is CODATA-2018-derived. Suite section `codata` shows the choice is immaterial at
present precision (all anchors shift `< 1e-8`), which is precisely why a mixed
set is invisible to numerical checks and must be prevented editorially. The
parallel ChatGPT pack shipped exactly such a mixed set. One sentence pinning the
release for `P_cal`, mirrored in SSTcore, closes this.

### m5 — `[CALIBRATED]` label variants `[EDITORIAL]`

The main canon uses seven distinct calibrated-family tags (`[CALIBRATED]` ×6,
`[CALIBRATED ALGEBRAIC IDENTITY]` ×4, `[CALIBRATED CHAIN GUARD]` ×2,
`[CALIBRATED IDENTITY]`, `[CALIBRATED CONSISTENCY TEST]`,
`[CALIBRATED ALGEBRAIC IDENTITY / TRANSPARENCY GUARD]`,
`[CALIBRATED / PROVENANCE GUARD]`). Each is individually defensible, but a
grep-based audit — including this pack's own checker — cannot count them as one
class without a lookup table. Recommend fixing a closed sub-vocabulary in a
future edition. No numerical consequence.

---

## 5. Canonisation recommendation

| Item | Status | Action |
|---|---|---|
| Action–phase mass–shell bridge (main canon) | `[READY FOR CANON]` | keep as is; label must stay `[ORTHODOX FORM / SST BRIDGE / CONDITIONAL DERIVATION]` |
| RT residual vector | `[READY FOR CANON]` | now backed by a discriminating numerical harness |
| `M_0 = (m_e/4) L_tot` transparency identity | `[READY FOR CANON]` | verified to machine precision |
| `16 pi^2` Rydberg erratum | `[READY FOR CANON]` | verified; 32π² guard added to the suite |
| Benchmark table | `[MAJOR REVISION REQUIRED]` | apply patch `0003` |
| `omega_c` / `F_max` / `r_c` printed values | `[CANON PATCH REQUIRED]` | apply patches `0001`, `0002`, `0004` |
| legacy 17-digit `rho_core` (corpus) | `[REMOVE FROM CANON]` | one deliberate corpus pass; not patched here |
| CODATA release pin | `[CANON PATCH RECOMMENDED]` | state the release used by `P_cal` |
| `rho_f` provenance | `[UNRESOLVED]` | state a calibration observable or demote to interval-valued |
| `alpha` ppm closure | `[RESEARCH-TRACK ONLY]` | blocked at gates `G_0`/`G_1`; unchanged |
| `theta = pi` superselection | `[PENDING DERIVATION]` | still `[POSIT]`, pinned by observed statistics |
| SSTcore action–phase API | `[CODE PATCH REQUIRED]` | see M1 |

**Merge order:** `0001` → `0002` → `0003` → `0004` (verified sequentially; CRLF
preserved on the main canon, LF on the RT companion, matching each source file).

---

## 6. Required numerical checks

Performed in this pack (see `results/`):

1. Full primitive-chain algebra against CODATA-2018 — **PASS** (all identities).
2. Corrected `16 pi^2` Rydberg form **and** an explicit guard that the legacy
   `32 pi^2` form equals `2 F_max` — **PASS**.
3. `M_0(T)` geometric baseline → `(m_e/4) L_tot(T)` collapse — **PASS** to
   machine precision; `M_0(3_1) = 4.0929 m_e`, i.e. the branch does not close on
   the electron mass.
4. Action–phase residuals `Delta_shell`, `Delta_V`, `Delta_Omega` at
   `V/c = 0.01 … 0.99` — **PASS** (`< 4.4e-7`, finite-difference floor).
5. Fixed-momentum guard: the forbidden fixed-`V` derivative reproduces
   `gamma^2 - 1` (a factor `4.26` error at `V/c = 0.9`) — **PASS**.
6. Discriminating power of `Delta_q` against a coupled counter-model — **PASS**.
7. Target-free torus self-linking `SL_tor(T(p,q)) = pq` for seven `(p,q)` — **PASS**.
8. Biot–Savart `A_K → 1/(4 pi)` coarse demonstrator — **PASS** (30% tolerance;
   the canonical `0.99992` ratio needs the unbundled `N = 32000` torch sweep).
9. Live SSTcore-vs-canon alignment, 17 comparisons — **PASS**.
10. Canon marker / structural check, 27 required items — **PASS**.
11. Printed-anchor audit at half-ulp tolerance (`frozen_anchors`) — **PASS**,
    with `r_c` and legacy `rho_core` recorded as documented defects.
12. CODATA-2018 vs 2022 release sensitivity (`codata`) — **PASS**, all anchors
    shift `< 1e-8`.
13. Corpus scan for stale hard-coded anchors (`legacy_anchors`) — defect
    confirmed present.
14. Canon snapshot drift vs live Project Knowledge files — **IDENTICAL**.

Still required, **not** in this pack:

- `rho_f` calibration observable, or a defensible interval.
- KAM-T stage-1 numerics.
- Boost-symmetry-breaking / preferred-frame bound — the primary falsifiable
  signature, and still the largest untested commitment in the canon.
- Replacement of the surrogate `E_0(I,q)` in the residual harness by a resolved
  SST filament energy functional with a concrete conserved internal action `I`.
  Until that exists, the action–phase route tests the *protocol*, not SST.
- Full `N = 32000` Biot–Savart robustness sweep.

---

## 7. Do not overclaim

- 111/111 passing is a statement about internal algebraic consistency, not
  empirical support. The majority of the checks are calibrated identities.
- `G_swirl` closes on `G` only because `t_p` imports `G`.
- The `alpha` section records an obstruction and therefore carries **no**
  pass/fail by design.
- The galactic section exercises fit machinery on synthetic data; `r_s` is
  fitted, the coherence-length lemma is open, and no SPARC data is bundled.
- The action–phase bridge is imported orthodox mechanics; the open theorem
  target is unchanged by v0.8.28.
