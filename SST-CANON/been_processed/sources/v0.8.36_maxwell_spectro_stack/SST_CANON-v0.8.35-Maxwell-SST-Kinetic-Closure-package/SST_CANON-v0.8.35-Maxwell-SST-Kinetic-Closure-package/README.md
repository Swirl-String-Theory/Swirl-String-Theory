# SST Canon v0.8.35 — Maxwell–SST Kinetic Closure and Internal-Mode Thermodynamic Gate

## Scope

This package is an **in-place research patch for `SST_CANON-v0.8.35`**. It does not bump the Canon version and is intended to coexist conceptually with other v0.8.35-derived branches.

The module develops the question:

> For every SST knot `K`, which translational, orientational, Kelvin, twist, writhe, and core modes are actually coupled by a physical interaction; what are their excitation thresholds or gaps; and what thermodynamic and spectroscopic contribution follows?

It incorporates the first four Maxwell-inspired priorities:

1. **Internal-mode thermodynamic gate.** Coupled, accessible, equilibrated modes must appear in thermodynamic/spectroscopic bookkeeping.
2. **Knot kinetic closure.** A topologically labelled phase-space distribution `f_K` is introduced for ensembles of coherent SST knots/excitations, not for hypothetical substrate particles.
3. **Knot-ensemble stress closure.** Momentum-flux pressure/stress is defined separately from the Euler/Bernoulli pressure of the SST substrate.
4. **Orientation isotropization.** An `SO(3)` orientation marginal and anisotropy tensor provide a held-out ensemble-isotropy test; ensemble isotropy is explicitly not equated with single-knot isotropy.

## Critical Canon correction included

The existing v0.8.x spectroscopic block used

```tex
\Delta_K \sim \frac{\Gamma^2}{4\pi\xi L}
```

as an energy-gap estimate. This is dimensionally incomplete:

```tex
[\Gamma^2/(\xi L)] = m^2 s^{-2},
```

not joules. The patch therefore removes the derived `10^2--10^3 eV` claim and replaces it with a true energy-difference definition from a declared finite-core energy functional.

A second guard is added:

```tex
\omega_{K,a}>0 \not\Rightarrow \Delta_{K,a}>0.
```

A nonzero classical normal-mode frequency is a stiffness statement, not by itself a discrete excitation-energy gap.

## Central activation gate

A mode is experimentally active only when all relevant conditions are met:

```tex
\mathcal G_{K,a}\neq0,
\qquad
E_{\rm drive}\gtrsim\Delta_{K,a},
\qquad
\tau_{K,a}\lesssim t_{\rm obs}.
```

Thus a mode can be suppressed by a true gap, a symmetry/weak-coupling gate, or dynamical freeze-out. These mechanisms are kept epistemically distinct.

## Files

- `SST_CANON-v0.8.35-Maxwell-SST-Kinetic-Closure.patch` — context patch for main Canon + research track.
- `Maxwell-SST-Kinetic-Closure-main-canon.tex` — copy-ready main-Canon replacement/insertion blocks.
- `Maxwell-SST-Kinetic-Closure-research-track.tex` — complete research section.
- `Maxwell-SST-Kinetic-Closure-bibitems.tex` — main and standalone research-track bibliography additions.
- `VALIDATION-Maxwell-SST-Kinetic-Closure.md` — validation scope and limitations.
- `SHA256SUMS.txt` — checksums.

## Application

From a directory containing the v0.8.35 source pair:

```bash
git apply --check SST_CANON-v0.8.35-Maxwell-SST-Kinetic-Closure.patch
git apply SST_CANON-v0.8.35-Maxwell-SST-Kinetic-Closure.patch
```

Then compile by the normal Canon build route, e.g.:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_CANON-v0.8.35.tex
```

If `git apply --check` fails because the exact v0.8.35 source around an anchor differs from the available lineage, use the two copy-ready `.tex` blocks instead of forcing a fuzzy patch.

## Epistemic discipline

The module uses paragraph-level tags rather than a single umbrella status. Orthodox statistical-mechanical forms, derived consistency/no-go statements, SST bridge definitions, ansätze, and falsifier protocols are kept separate. No Maxwell hard-sphere microphysics is imported into the SST substrate ontology.
