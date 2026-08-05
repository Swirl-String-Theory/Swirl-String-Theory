# SST Canon v0.8.35 — Canon-protocol review

## Verdict

**Conditionally acceptable, but not yet protocol-clean.**

The mathematical core of the v0.8.35 insertion is largely sound and the release package is reproducible, but the epistemic classification is too coarse in several places. The new module combines orthodox input, exact deductions, modelling ansätze, calibration conventions, computational benchmarks, and an open electromagnetic bridge under compound block labels. This conflicts with the Canon reading guide, which requires a primary epistemic tag at statement level and treats role labels as secondary qualifiers.

Recommended release status: **hold for a small v0.8.35a protocol patch** or incorporate the corrections in v0.8.36.

## Highest-priority findings

### P1 — Main subsection has one obsolete umbrella tag

File: `SST_Template.tex`, lines 6862–6866.

Current:

```latex
\textbf{[BRIDGE ANSATZ / SPECULATIVE FIT].}
```

This tag cannot classify the exact projector identity, the radius/diameter conversion, the no-go result, the finite-core operator ansatz, and the electromagnetic bridge simultaneously.

Recommended:

```latex
\textbf{[MIXED STATUS / SEE PARAGRAPH-LEVEL TAGS].}
```

Then tag each paragraph separately.

### P1 — The research-track status block collapses four different claims

File: `SST_CANON-v0.8.35-research-track.tex`, lines 10669–10687.

Current:

```latex
\textbf{[ORTHODOX INPUT / DERIVED KINEMATIC IDENTITY / RESEARCH MATCHING PROGRAMME].}
```

Recommended decomposition:

1. Projector and isotropic second moment: `[ORTHODOX INPUT]`.
2. Integral identity and local-projector no-go: `[DERIVED / CONDITIONAL NO-GO]`.
3. Finite-core response basis: `[ANSATZ / RESEARCH]`.
4. Electromagnetic identification: `[BRIDGE / THEOREM TARGET]`.

The sentence “Only the first statement is presently closed” is inconsistent with the later verdict, because the radius/diameter conversion and constant-tube no-go are also closed under their declared assumptions.

Recommended replacement:

```latex
The first two statements are closed under their explicitly declared geometric
and kinematic assumptions. The operator basis in item 3 is an ansatz whose
completeness and coefficients remain open. Item 4 is a bridge/theorem target.
```

### P1 — The finite-core expansion is an ansatz, not a consequence of Euler–Biot–Savart alone

File: research track, lines 10874–10917; main Canon, lines 6942–6962.

The form

```latex
\Delta_{\rm micro}^{(+)}
=
c_\kappa\mathcal I_{\kappa^2}
+c_\Omega\mathcal I_{\Omega^2}
+c_C\mathcal C_{\rm contact}+\cdots
```

is a symmetry-motivated candidate operator basis. Euler–Biot–Savart dynamics does not by itself prove that this basis is complete, local, analytic, or sufficient. In particular, `\mathcal C_{\rm contact}` is not defined in the new module.

Recommended tag:

```latex
\textbf{[ANSATZ / RESEARCH OPERATOR BASIS].}
```

Add an explicit definition of `\mathcal C_{\rm contact}`, its normalization, parity, locality/nonlocality, and regulator dependence.

### P1 — `c_L=0` is a protocol convention, not a derived physical coefficient

File: research track, lines 10911–10917; main Canon, lines 6957–6962.

Recommended wording:

```latex
\textbf{[CALIBRATION CONVENTION / IDENTIFIABILITY GUARD].}
We impose c_L\equiv0 by definition of the leading normalization, so that a
length counterterm cannot be fitted after the target is exposed. This is not a
microscopic prediction; if the microscopic calculation produces a length
renormalization, it must be absorbed into a separately derived leading
coefficient.
```

### P1 — Exact geometric self-linking is being conflated with the thin-tube helicity bridge

Main Canon, lines 6964–6971, states

```latex
\frac{\mathcal H}{\Gamma^2}=SL=Wr+Tw.
```

The geometric identity `SL=Wr+Tw` is exact for a framed ribbon. The relation between fluid helicity and self-linking is conditional on the thin-tube model, circulation/profile assumptions, and absence of reconnection. The research track itself uses `\simeq` for the helicity relation.

Recommended:

```latex
\textbf{[ORTHODOX GEOMETRIC IDENTITY / THIN-TUBE BRIDGE].}
SL=Wr+Tw,
\qquad
\frac{\mathcal H}{\Gamma^2}\simeq SL
```

with the assumptions stated immediately.

## Medium-priority findings

### P2 — “Exact kinematic origin” is too broad

Main Canon, lines 6881–6905.

The identity

```latex
\int_{S^2}t_iP_{ij}t_j\,d\Omega=\frac{8\pi}{3}
```

is exact. Its use as the coefficient of `\mathscr R_0` is an ansatz/definition. Recommended wording:

```latex
an exact origin of the numerical factor within the declared transverse-projector response ansatz
```

### P2 — The no-go result needs its domain stated in the tag

The constant-tube volume result is valid for a constant circular cross-section, before interior overlap, and within a valid tubular-neighbourhood/reach regime. Recommended tag:

```latex
\textbf{[DERIVED / CONDITIONAL GEOMETRIC NO-GO].}
```

### P2 — Numerical branches need explicit benchmark labels

Research track, lines 11044–11089.

Recommended:

```latex
\textbf{[COMPUTATIONAL BENCHMARK / DECLARED COMPARISON TARGET].}
```

The arithmetic values of `\Delta` are derived from the declared geometry and comparison value; they are not predictions.

### P2 — Main Canon depends on a research-track equation

Main Canon line 6978 cites `eq:rt_alpha_twist_energy_bound_v0835`. This is technically valid in the combined build, but it weakens the stated architectural rule that the research-track companion is not required for minimal core closure. Either reproduce the one-line bound in the main Canon or phrase the main text as a summary with no logical dependence on the companion.

### P2 — Orthodox source attribution is incomplete in the inserted module

The new section directly uses the isotropic tensor moment, tubular-coordinate Jacobian, Euler/Biot–Savart energy, Călugăreanu–White–Fuller theorem, thin-tube helicity bridge, and Maxwell/gauge-action normalization. Existing bibliography entries cover several of these, but the new section should cite them locally rather than relying on distant earlier sections.

## Recommended paragraph-level tags

| Claim | Recommended primary/role tags |
|---|---|
| `P_{ij}=\delta_{ij}-\hat k_i\hat k_j` and isotropic second moment | `[ORTHODOX INPUT]` |
| `\int t_iP_{ij}t_j d\Omega=8\pi/3` | `[DERIVED]` |
| Definition of `\mathscr R_0` | `[ANSATZ / DEFINITION]` |
| `\Delta_{\rm local\ projector}=0` | `[DERIVED / CONDITIONAL NO-GO]` |
| Radius/diameter conversion | `[DERIVED / CONVENTION GUARD]` |
| Constant circular tube volume identity | `[ORTHODOX GEOMETRY / DERIVED REWRITE]` |
| Constant-tube geometry-sensitive correction vanishes | `[DERIVED / CONDITIONAL NO-GO]` |
| Euler and Biot–Savart energy | `[ORTHODOX]` |
| Regularized finite-core functional | `[BRIDGE / DEFINITION]` |
| Curvature/twist/contact response expansion | `[ANSATZ / RESEARCH]` |
| `c_L\equiv0` | `[CALIBRATION CONVENTION / IDENTIFIABILITY GUARD]` |
| `SL=Wr+Tw` | `[ORTHODOX]` |
| `\mathcal H/\Gamma^2\simeq SL` | `[BRIDGE / CONDITIONAL]` |
| Twist-energy lower bound | `[DERIVED]` |
| Linear helicity term belongs to parity-odd channel | `[DERIVED CLASSIFICATION / CONDITIONAL BRIDGE]` |
| Maxwell/gauge-stiffness action | `[ORTHODOX TARGET FORM / BRIDGE]` |
| `\mathscr R_{\rm SST}=\alpha_{\rm eff}^{-1}` | `[THEOREM TARGET / RESEARCH]` |
| HR and Gilbert numerical values | `[COMPUTATIONAL BENCHMARK]` |
| Alpha-blind campaign and holdouts | `[RESEARCH / FALSIFIER PROTOCOL]` |

## Release-package checks

- SHA-256 manifest: PASS.
- Main + research-track label uniqueness: PASS, 936 labels and no duplicates.
- LaTeX build: PASS; no undefined references/citations and no fatal errors.
- PDF generated: PASS, 254 pages.
- Layout: the new pages render legibly; the long compound status heading produces an overfull-box warning and should be shortened by the proposed decomposition.
- Validation limitation: the package proves internal output integrity, but the claimed exact application to the original v0.8.34 bytes cannot be independently rechecked from this archive because the v0.8.34 source files are not included.

## Final classification

- **Scientific content:** acceptable as a guarded research programme.
- **Mathematical derivations:** projector identity, convention conversion, and twist bound are sound under the stated assumptions.
- **Electromagnetic claim:** correctly left open.
- **Canon protocol:** **not fully compliant yet**, primarily because labels are attached to multi-status blocks instead of individual material claims.