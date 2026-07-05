# Source — Lorentz-type swirl-stress split patch → v0.8.15

Origin: conversation audit splitting canon (hydrodynamic core only) from
research-track (Rosetta EM correspondence, SST-44 stress, pending f_link).

## Main canon (`\ref{sec:lorentz_type_force_density_as_swirl_stress}`)

Inserted after `\ref{subsec:swirl_pressure_law}`, before Minimal effective Lagrangian bridge.

- `[ORTHODOX]` Euler vector identity v×ω
- `[DERIVED]` swirl-force density f_⟲ = ρ_f v×ω
- Bernoulli / total Euler pressure tie
- Closed-loop observables (Γ, H, Lk) — no microscopic EM element-force law
- `[CALIBRATED]` scales: Γ₀, p_{⟲,0} = 4.19×10⁵ Pa
- Explicit: not a Maxwell–Lorentz replacement

Uses canon macros `\rhoF`, `\rc`, `\vchar`.

## Research track (`\ref{sec:research_em_to_swirl_force_density_correspondence}`)

Appended after core–torsion impedance section.

- `[SPECULATIVE / PENDING]` J×B ↔ λ_{EM→⟲} ρ_f v×ω, [λ]=1 dimensionless
- Flux-impulse channel relation (Φ₀) — not independent canonical bridge
- Field dictionary (α_A) — research route only
- SST-44 stress σ^(44), full vs split decomposition (no double-counting)
- f_link from U_link — `[PENDING DERIVATION]`

## Build

```powershell
cd papers/SST-CANON/been_processed
python apply_v0815.py
# PDF in v0.8.15/$out/
```
