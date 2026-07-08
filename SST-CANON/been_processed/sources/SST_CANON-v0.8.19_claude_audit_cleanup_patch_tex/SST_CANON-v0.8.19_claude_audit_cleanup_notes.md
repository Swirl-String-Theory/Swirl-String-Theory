# SST_CANON v0.8.19 — Claude-audit cleanup patch notes

## Baseline

This patch is incremental on top of the latest local v0.8.19 pair already containing the dark-taxonomy/operator-clock patch:

- `SST_CANON-v0.8.19.dark-taxonomy-operator-clock.tex`
- `SST_CANON-v0.8.19-research-track.dark-taxonomy-operator-clock.tex`

The exported patch normalizes the filenames to the normal working names inside the diff:

- `SST_CANON-v0.8.19.tex`
- `SST_CANON-v0.8.19-research-track.tex`

## Claude audit verdict

The Claude audit is mostly correct as a second-opinion audit: it identifies v0.8.19 as a consolidation release and does not introduce a new fatal issue. Most listed fixes were already present in v0.8.19 before this patch.

Actionable leftovers found in the current latest local sources:

1. `T_{\rm core}` was still a free line-tension symbol without a strict source/units guard.
2. A research-track non-Abelian screening block still used the older notation
   `E_{\rm eff}^{(G)}` and coefficients `\alpha_C,\alpha_L,\alpha_H,\alpha_G`.
3. The Geometric Impedance Bridge was still physically guarded, but editorially still placed in the main appendix. Claude's recommendation to move it to the research-track layer is reasonable.
4. The requested numerical checks were not yet bundled as a reproducible script.

## Patch actions

### 1. `T_{\rm core}` free-symbol guard

Added a main-canon guard after the thin-filament energy scale:

```latex
\textbf{[CANON / FREE-SYMBOL GUARD].}
The line tension $T_{\rm core}$ has units
$[T_{\rm core}]={\rm J\,m^{-1}}={\rm N}$ and is not fixed by
Eq.~\eqref{eq:canon_thin_filament_energy_scale}.
```

The guard requires every use of `T_{\rm core}` to identify one of:

- resolved core variational model;
- numerical relaxation scale;
- explicit calibration.

The same rule is mirrored in the research-track topological-fluid mechanics appendix.

### 2. Screening-functional notation cleanup

Replaced the lingering old-style extension

```latex
E_{\rm eff}^{(G)},\quad \alpha_C C + \alpha_L L + \alpha_H \widehat{\mathcal H} + \alpha_G I_G
```

with the scalarized screening form

```latex
\frac{E_{\rm screen}^{(G)}[\mathcal K_G]}{E_0}
=
 a_R\operatorname{Rop}_{\rm rad}(\gamma_K)
+a_C c_{\min}(K)
+a_H\widehat{\mathcal H}(K)
+a_G I_G(\mathcal K_G)+\cdots.
```

After the patch, the patched TeX files contain no remaining occurrences of:

- `E_{\rm eff}`
- `E_{\rm eff}^{(G)}`
- `\alpha_L`
- `sst_eff_energy_old`

### 3. Geometric Impedance Bridge relocation

Main Canon now keeps only a short status guard:

```latex
\section{Geometric Impedance Bridge Status Guard}
\label{sec:appendix_geometric_impedance_bridge}
```

The full bridge lemma is moved to the research-track companion under:

```latex
\section{Research Track: Geometric Impedance Bridge}
\label{sec:rt_geometric_impedance_bridge}
```

The original equation labels are retained in the research-track section:

- `eq:electron_schwarzschild_geometric_bridge`
- `eq:geometric_impedance_phi`

This keeps the bridge available for comparison/normalization/falsifier design while preventing it from reading as part of the closed main-canon derivation chain.

### 4. Numerical verification script

Added standalone script:

```text
verify_v0819_claude_audit_checks.py
```

It checks:

- `F_swirl^max = 16*pi^2*hbar*R_inf^2*c/alpha^5`
- old `32*pi^2` route gives exactly a factor 2 too high
- dimensional scale `rho_horn*r_c^5/lambda_c^2` has kg units
- Groningen Foucault benchmark at `phi = 53.219 deg`

Script output confirms:

```text
16*pi^2 route: 29.0535101958 N
old 32*pi^2 route: 58.1070203917 N  (factor 2.000000)
Omega_F: 5.84047345304e-05 s^-1
T_F: 29.8833521978 h
v_rot: 278.483010742 m/s  (WGS84 equatorial-radius convention)
dt_rot: 37.2757824607 ns/day
dt_height_100m: 0.942742339678 ns/day
```

## Compile validation

Compiled patched main Canon with the research-track companion using `pdflatex` three times.

Result:

- exit code: `0`
- undefined references: none in final run
- multiply-defined labels: none in final run
- only remaining warning observed: ordinary float placement change (`h` to `ht`)

## Status

Recommended for application as a cleanup patch after the dark-taxonomy/operator-clock v0.8.19 patch.
