# SST CANON v0.8.25 — Patch Pack (audit-driven)

Generated: 2026-07-24. Target files (byte-exact, **CRLF** line endings, UTF-8):

- `SST_CANON-v0_8_25.tex` (7146 lines, 378815 bytes)
- `SST_CANON-v0_8_25-research-track.tex` (10981 lines, 404637 bytes)

All patches are unified diffs with `a/` / `b/` prefixes. Apply with either:

```bash
patch -p1 < patches/01_fmax_rydberg_factor2.diff        # GNU patch, Linux/macOS
git apply patches/01_fmax_rydberg_factor2.diff          # alternative, safest on Windows
```

Apply in numerical order (01 → 06). Patches 01–05 target the main canon;
patch 06 targets the research-track file. All six were dry-run verified
individually against pristine copies and sequentially; the cumulative result
is byte-identical to `final/` and preserves CRLF endings throughout.

**Compile status:** the fully patched pair compiles cleanly with pdflatex
(0 errors, PDF produced). Note: the main file inputs the research track as
`\input{SST_CANON-v0.8.25-research-track}` (dots), so the RT file must be
present under that name locally.

---

## Patch contents

### 01_fmax_rydberg_factor2.diff  — FATAL FIX
`eq:Fmax_Rydberg` (boxed): coefficient `32\pi^2` → `16\pi^2`.
The printed relation gave 58.107 N = 2·F_swirl^max. Correct derivation:
F = m_e c²/(2 r_c), with m_e = 4πħR∞/(α²c) and r_c = α³/(8πR∞), gives
F = 16π²ħR∞²c/α⁵ = 29.0535 N (CODATA, rel. dev. ~1e-7).
Adds an [ERRATUM] sentence documenting the correction.

### 02_rho_calc_retirement.diff  — M2
`eq:Fmax_rho`: replaces the self-referentially defined `\rho_{\rm calc}`
(≡ 4F/(πα²c²r_c²), i.e. defined *from* F, making the equation a tautology)
by the already-canonical `\rhohorn`. Verified: ρ_calc == ρ_horn^eff exactly
(3.8934e18 kg m⁻³). Adds a [NOTATION RETIREMENT] note.

### 03_M0_transparency_guard.diff  — M3
Appends a [CALIBRATED ALGEBRAIC IDENTITY / TRANSPARENCY GUARD] to the
"Pure geometric baseline branch": the branch collapses exactly to
M₀(T) = (m_e/4)·L_tot(T)  (new label `eq:M0_me_quarter_reduction`).
Records: all α's cancel, m_e enters via ρ_horn, trefoil gives 4.0929 m_e
(NOT the electron mass), and benchmarks on this branch inherit m_e as input.
Numerical anchor M₀/L_tot = 2.277346e-31 kg = m_e/4 (machine precision).

### 04_rhof_provenance_guard.diff  — M4
Adds a [CALIBRATED / PROVENANCE GUARD] to "Primitive Structure of the
Theory": ρ_f = 7.0e-7 kg m⁻³ has two significant figures, no canon-level
derivation and no explicitly stated calibration observable; downstream
linear-in-ρ_f quantities inherit few-percent uncertainty; future edition
must state the calibration target or demote ρ_f to an interval.

### 05_label_discipline.diff  — minor label-propagation fixes
(a) Γ₀: `[DERIVED]` → `[DERIVED within the calibrated chain]` with explicit
reference to the r_c [CALIBRATED CHAIN GUARD].
(b) Spring energy `eq:Espring` premise: `[DERIVED]` →
`[CONDITIONAL DERIVED, n=2 posited]` (n=2 is empirically matched, per the
existing [CRITICAL NOTE] in the same subsection).

### 06_rt_dedup_and_label.diff  — research-track file
(a) Adds a [CRITICAL NOTE] duplication guard to the RT header listing the
seven subsections that still have full-text counterparts in the main canon,
declaring the main-canon versions authoritative until de-duplication.
(b) Harmonises the Pauli regularized-template label `[DERIVED]` →
`[ORTHODOX]`, matching the main canon (resolves the detected label conflict).

---

## Verification artefacts

- `verify_v0_8_25_patched.py` — post-patch numerical check suite
  (run: `python3 verify_v0_8_25_patched.py`; requires scipy).
- `final/` — cumulative patched files (reference only; the diffs are the
  deliverable).

## Not patched (deliberate, needs your decision)

- Full de-duplication of the seven migrated sections (structural edit;
  patch 06 only fences it).
- Stale inline version strings (v0.8.1 / v0.8.10 / v0.8.18 architecture
  references) — recommend a `\canonversion` macro in v0.8.26.
- Pre-existing duplicate labels in the main canon (sec:atomic,
  sec:consistency, sec:delay, sec:spectroscopy, sec:unification) — these
  exist in the pristine file (commented/active section pairs) and predate
  this pack.
- RT benchmark table with empty "predictive candidate" cells (M5) — fill
  from archived CSV or replace by protocol text.
