# SST Canon v0.8.36 — Maxwell / spectro stack changelog

**Zenodo (one line):** Maxwell swirl-tonic, kinetic closure, dynamical-field / reciprocal-stress / mechanical falsifiers, and spectroscopic-response guards.

## Summary

Single edition on top of v0.8.35 stacking all six `to_do_patches` items:
configuration-resolved spectroscopic-response (re-port from v0.8.34),
Maxwell–SST kinetic closure (with dimensional spectro correction),
Maxwell-blind mechanical falsifier, reciprocal-stress audit, dynamical field
closure, and material swirl–tonic vorticity-potential representation.

## What is new (per package)

1. **Spectroscopic response (v0.1.0, re-port):** configuration-resolved
   spectroscopic-response guard on the master mass equation; RT generalized
   King diagnostics programme (Ishiyama et al.).
2. **Kinetic closure:** internal-mode thermodynamic gate, knot kinetic
   closure `f_K`, knot-ensemble stress vs Euler/Bernoulli pressure,
   orientation isotropization; replaces dimensionally incomplete
   `Γ²/(4πξL)` energy-gap claim with a true energy-difference ledger.
3. **Blind mechanical falsifier:** Maxwell-inspired target-blind mechanical
   closure falsifier (main + RT).
4. **Reciprocal stress:** reciprocal-stress audit (main + RT).
5. **Dynamical field closure:** transverse-mode / displacement-current /
   gravitational energy-deficit gates (DFC–T/D/G).
6. **Swirl-tonic:** material swirl–tonic potential `A_st^(m) := v`, Stokes /
   holonomy falsifier, material–link sector separation; edition bump to
   v0.8.36.

## Source

- Patches archived under `been_processed/sources/v0.8.36_maxwell_spectro_stack/`
- Base: Canon v0.8.35 → `been_processed/v0.8.36/`
- Ingest: `scripts/apply_v0836.py`
