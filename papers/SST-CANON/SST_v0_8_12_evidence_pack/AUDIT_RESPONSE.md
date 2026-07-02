# AUDIT_RESPONSE.md — Response to the external (Gemini) audit of SST Canon v0.8.12

This document records the SST co-editor verdict on each point of the external
audit, cross-checked against the actual canon / research-track / SSTcore source,
and the concrete action taken. Verdicts use the canon's own label taxonomy
(`[ORTHODOX] [DERIVED] [CALIBRATED] [CONDITIONAL] [SPECULATIVE] [CRITICAL NOTE]`),
NOT the external audit's ad-hoc labels.

## Meta-observations on the external audit

1. The external audit's "current label" field is empty for nearly every item; it
   was produced without reading the canon's existing labels. As a result it
   re-flags items the canon already labels `[BRIDGE ANSATZ]`, `[SPECULATIVE]`, or
   whose dimensional caveats are already disclosed.
2. Its proposed labels (`[calibrated algebraic identity]`,
   `[speculative interpretation]`, `[bridge ansatz]`) are NOT in the canon set.
   Adopting them verbatim would reintroduce label drift. They are mapped:
   `calibrated algebraic identity -> [CALIBRATED]`,
   `speculative interpretation -> [SPECULATIVE]`,
   `bridge ansatz -> [SPECULATIVE]/[CONDITIONAL]`.
3. It missed the real Chronos-Kelvin issue (the factor-2 vorticity-vs-angular-
   frequency convention, fixed in patch 0001) and instead raised an over-read
   "Lagrangian kinematics" objection.

## Per-point verdict and action

| # | External claim | Their severity | Verdict | Action |
|---|---|---|---|---|
| §1  | lambda_c ambiguity in 4/alpha gate | HARD | VALID, already resolved in CODE (full_compton_wavelength); canon-text only | = audit BG-1; covered by canon-text note; CODE correct (sstcore_alignment section) |
| §2.1| Rydberg tautology | RHET | VALID, already `[CALIBRATED]` consistency check | none (already labeled) |
| §2.2| G_swirl circular (t_p contains G) | BRIDGE | VALID, already `[CALIBRATED]` | none (already labeled) |
| §2.3| F_max*4 = Coulomb | RHET | VALID, already `[CALIBRATED]` algebraic identity | none (already labeled) |
| §3.1| Chronos-Kelvin "breaks Lagrange" | HARD | OVERSTATED / misreading | real issue = factor-2 convention -> **patch 0001** |
| §3.2| V_horn=2pi^2 r_c^3 violates a_core!=r_c | HARD | PARTIAL (clarity) | **patch 0005 / B3** critical note (envelope vol, not tube) |
| §3.3| Galactic Euler -> ~2800 Pa | HARD | VALID number, already research-track `[SPECULATIVE]` | **patch 0005 / A2** critical note + falsifier number |
| §4.1| A=(m_e/e)u bakes electron into vacuum | HARD | OVERSTATED (m_e/e dimensionally forced) | normalization bridge; `[CALIBRATED]` (em_qed section) |
| §4.2| Madelung rho_psi vs incompressibility | BRIDGE | PARTIAL, already `[SPECULATIVE]` | **patch 0004 / B4** critical note (rho_psi != substrate) |
| §4.3| Meissner imports 2M_e, -2e | BRIDGE | VALID | **patch 0005 / A3** import flag, x-ref Sec 8.6 |
| §5.1| Trefoil m=1 -> Mobius breaks Calugareanu | HARD | WRONG (twist knots are orientable) | none (verified: SL=pq integer framing; construction-twist != self-linking) |
| §5.2| theta=pi fermion posit forced | RHET | VALID, already `[POSIT, pinned]/[OPEN]` | none (already labeled) |
| §6.1| zeta(3) generic not theory-specific | RHET | VALID | **patch 0004 / B2** downgrade to generic-calculus `[CALIBRATED]` |
| §6.2| Atomic dH ~ O(alpha^3) breaks spectroscopy | HARD | PARTIAL: already `[BRIDGE ANSATZ]`, missing magnitude note | **patch 0004 / A1** critical note (gamma must be alpha-suppressed) |
| §6.3| B_e~S_e numerology (J s vs J m^2, /5) | SPEC | VALID, dim-mismatch already disclosed | recommend downgrade `[SPECULATIVE]` (disclosure already present) |
| §6.4| Delay kappa free parameter | BRIDGE | VALID, already research-track | none (already research-track) |
| §7  | Suite tests "99% trivial" | -- | UNFAIR / misreading | suite includes torus self-linking, A_K plateau, Onsager, obstruction ledger; triviality IS the [CALIBRATED] labeling point |

## Net-new work delivered

- **patch 0001** chronos-Kelvin vorticity factor-2 (the real §3.1 issue).
- **patch 0004** (main canon): A1 alpha-spectroscopy note, B2 zeta(3) downgrade, B4 Madelung clarification.
- **patch 0005** (research-track): A2 galactic dp falsifier, A3 Meissner imports, B3 horn-volume clarification.
- **scripts**: reproduce_pauli_barrier.py (§claim 38), reproduce_em_qed_normalization.py (§claims 61/67, with m_e/e correction), fit_galactic_swirl_rotation_sparc.py (§claim 42, research-track).

All other external points were either already handled by existing labels or were
over-reads/misreadings and required no change.
