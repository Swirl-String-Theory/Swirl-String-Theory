# SST v0.8.31 — rho_f Scaling Audit, Phase 1

## Scope

This audit applies the rescaling

\[
\mathscr S_\lambda:\qquad \rho_{\rm eff}^{(0)}\mapsto \lambda\rho_{\rm eff}^{(0)},\qquad \lambda>0,
\]

to the active v0.8.31 main Canon and Research Track. The historical number
\(7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}\) is treated separately as a legacy reference normalization whose provenance has been invalidated.

The scan found **206 textual occurrences** of `\\rhoF` or `\\rho_{\\!f}`:

- main Canon: **85**;
- Research Track: **121**.

This is a dependency audit, not yet a v0.8.32 patch.

## Classification scheme

- **A — exact cancellation:** the observable is invariant without introducing a new fitted coefficient.
- **B — removable/covariant normalization:** invariance requires a linked field, stiffness, pressure, source coefficient, or fitted kernel to co-scale.
- **C — absolute-amplitude candidate:** a force, pressure, energy, impulse, mass, or detector amplitude changes under \(\mathscr S_\lambda\) and could in principle determine the coefficient.
- **Q — quantum/action normalization:** classical equations may be invariant while the absolute action, source coupling, fluctuation amplitude, or statistical weight is not.
- **X — invalid, historical, or semantically mismatched:** the occurrence cannot currently be used to determine \(\rho_{\rm eff}^{(0)}\).

A family may carry a compound label such as `C/X` when it has the right dimensional sensitivity but uses the wrong density ontology or an unclosed regularization.

## Phase-1 family ledger

| ID | Location / equation family | Class | Scaling result | Preliminary adjudication |
|---|---|---:|---|---|
| F01 | Primitive set and provenance guard, main lines 1221–1245 | X | Historical number is inserted directly | Replace `[CALIBRATED]` by legacy reference / orphaned normalization; physical \(\rho_{\rm eff}^{(0)}\) remains unfixed. |
| F02 | Density ontology and quasi-static limit, main lines 1274–1355 | B | Definition survives; numerical value is not fixed | Canon-safe semantic layer. |
| F03 | \(\rho_E=\tfrac12\rho_F v^2\), \(\rho_M=\rho_E/c^2\), main lines 1705–1712 | C | Absolute energy and mass-equivalent densities scale as \(\lambda\) | Candidate only if an absolute independent energy-density observable exists. None is presently specified. |
| F04 | Coarse-grained law \(\rho_F=K\Omega\), main lines 1814–1825 | B/X | Can be inverted by choosing \(\Omega\) or \(K\) | Phenomenological reparameterization, not a pinning equation. |
| F05 | Canonical master mass equation \(M_K\propto\rho_F\Xi_K\), main lines 1836–1935 | B | \(\rho_F\to\lambda\rho_F\) is absorbed by \(\Xi_K\to\lambda^{-1}\Xi_K\) | Absolute particle masses do not pin \(\rho_F\) while topology-kernel coefficients remain matching coefficients. |
| F06 | Source-free radiation action, main lines 3021–3052 | B/Q | \(K_\gamma\to\lambda K_\gamma\), \(A\to\lambda^{-1/2}A\) preserves the quadratic sector | Wave speed fixes only \(K_\gamma/\rho_F\). Source or quantum normalization is still open. |
| F07 | \(K_\gamma=\rho_Fc^2\), main line 3046 | B | Co-scales exactly | Identity/target stiffness, not an independent calibration. |
| F08 | Euler radial acceleration \(\rho_F^{-1}dp/dr=v_\theta^2/r\), main lines 3186–3216; RT lines 341–361 | A | \(p\to\lambda p\) cancels \(\rho_F\) | Rotation curves and accelerations do not determine the absolute coefficient. |
| F09 | Absolute swirl pressure, stress and force density, main lines 3193–3208, 3269–3395 | C | \(p,\sigma,f\propto\lambda\) | Genuine candidate only if SST provides an independently normalized pressure/force transducer. No such map is canonized. |
| F10 | Optical/time projection using \(\delta p/(\rho_Fc^2)\), main lines 4854–4898 | A | Pressure and denominator co-scale | Clock/optical ratio is invariant and cannot pin \(\rho_F\). |
| F11 | Galactic acceleration \(a=\rho_F^{-1}dp/dr\), main lines 6821–6835 | A | Exact cancellation | Galaxy kinematics cannot determine \(\rho_F\); absolute pressure remains separately model-dependent. |
| F12 | Pauli barrier \(V_{\rm Pauli}\propto\rho_F\Gamma_0^2\), main lines 5554–5598 | C/X | Absolute barrier scales as \(\lambda\) | Candidate amplitude is contaminated by an unclosed cutoff and by use of effective response as filament material density. Not a valid calibration observable. |
| F13 | Orthodox filament energy templates using \(\rho_F\Gamma^2\), RT lines 1759–2258 and related blocks | C/X | Energies and tensions scale as \(\lambda\) | Resolved filament formulas require material/tube density, not automatically quasi-static \(\rho_F\). Density ontology must be repaired before use. |
| F14 | Kelvin impulse \(I_T=\rho_F\Gamma\pi R^2\), RT lines 699–715 and 7515–7751 | C/X | Absolute impulse scales as \(\lambda\) | Could pin a density only with an independently normalized R-phase pseudomomentum and a valid effective-density dictionary. Currently speculative. |
| F15 | Pressure-envelope and Euler-force diagnostics, RT lines 791–830, 5708–5734, 6765–6841 | A/C | Acceleration cancels; absolute pressure/force scales | No clean pin without an absolute coupling law. |
| F16 | Pressure-Poisson/stress-source equations, RT lines 8114–8208 | B/C | Normalized velocity solution may be invariant; absolute stress source scales | Requires boundary conditions and a detector/source map; not yet a calibration. |
| F17 | Historical VAM density construction, RT lines 9144–9268 | X | Wrong dimensions and invalid cosmological confirmation | Retain only as provenance erratum and \(\mathcal J_\omega^{\rm VAM}\) history. |
| F18 | Participation diagnostic \(\phi_{\rm dyn}=\rho_F/(\pi\rho_{\rm horn})\), RT lines 9398–9462 | B | Merely rewrites the target value | Diagnostic, not derivation. |
| F19 | Cosmological impedance and SSDL lifts, RT lines 9471–9851 | X | Inputs reconstruct the target; \(G\) and epoch factors are imported | Exact data reparameterization / research consistency relation, no evidential pinning. |
| F20 | Minimal relational link-field action, RT lines 10300–10460 | Q/B | Field/source normalization can absorb \(\rho_F\) until a charge coupling is fixed | Quantum/source audit required. |
| F21 | Core–torsion action and impedance, RT lines 10609–10638 | B/Q | \(K_T/\rho_F\) fixes speed; \(Z_T\) remains absolute | A separately derived impedance or fluctuation amplitude could become a valid C/Q observable. |
| F22 | EM-to-swirl correspondence with free \(\lambda_{\rm EM\to swirl}\), RT lines 10769–10910 | B | \(\rho_F\) trades against the free correspondence coefficient | Cannot pin \(\rho_F\) until the field dictionary fixes the coupling independently. |
| F23 | Hill-vortex / Taylor-column analog benchmarks, RT lines 11168–11234 | C | Laboratory analogue energies and forces scale as \(\lambda\) | They determine the analogue-fluid density, not the cosmic SST response, absent a transduction theorem. |
| F24 | Numerical tables and legacy pressure benchmarks | X | Scale with the inserted reference value | Regression fixtures only; no evidential content. |

## Provisional result

### 1. No clean class-C observable has yet been found in the main Canon

Every apparent absolute-amplitude candidate currently suffers from at least one of the following:

1. an adjustable matching coefficient or kernel;
2. a free source/transduction coefficient;
3. an unclosed cutoff or core profile;
4. a density-ontology mismatch;
5. use as a legacy numerical benchmark rather than as an independent measurement.

Therefore the present scan has not found a valid observable that uniquely fixes \(\rho_{\rm eff}^{(0)}\).

### 2. The strongest invariances are already structural

The following sectors are insensitive to the absolute normalization:

\[
\frac{1}{\rho_F}\frac{dp}{dr},\qquad
\frac{K_\gamma}{\rho_F},\qquad
\frac{\delta p}{\rho_Fc^2},\qquad
M_K\propto\rho_F\Xi_K\quad(\Xi_K\ \text{unfixed}).
\]

These cover galaxy acceleration, source-free wave speed, pressure-based clock projections, and the current mass-functional matching layer.

### 3. The unresolved loophole is class Q

The classical field equations may admit a normalization symmetry while the following do not:

- source couplings;
- detector response amplitudes;
- canonical commutators;
- zero-point or thermal fluctuation amplitudes;
- path-integral weight \(e^{iS/\hbar}\);
- independently normalized impedance.

Consequently it is premature to declare \(\rho_{\rm eff}^{(0)}\) a pure convention before the Q-sector is audited.

## Working verdict

\[
\boxed{
\rho_{\rm ref}=7.0\times10^{-7}\ \mathrm{kg\,m^{-3}}
\quad[\mathrm{LEGACY\ REFERENCE\ NORMALIZATION;\ PROVENANCE\ INVALIDATED}]
}
\]

\[
\boxed{
\rho_{\rm eff}^{(0)}
\quad[\mathrm{UNFIXED\ QUASI\!-\!STATIC\ RESPONSE\ COEFFICIENT}]
}
\]

Phase 1 strongly suggests that the absolute value is redundant in the present classical bridge structure, but the parameter-budget reduction to \(\{\alpha\}\) is not yet promoted because the source/action/quantum normalization audit remains open.

## Phase 2

1. Trace every class-C candidate to its final detector-level observable.
2. Audit all field and source redefinitions under \(\mathscr S_\lambda\).
3. Audit the quadratic action, canonical momenta, commutators, and fluctuation amplitudes.
4. Decide whether any invariantly normalized impedance or source coupling survives.
5. Only then write the v0.8.32 orphaned-normalization patch and parameter-budget lemma.
