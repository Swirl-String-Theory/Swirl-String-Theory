# SST Canon v0.8.28 -> v0.8.29 Fermat / optical-mode patch

## Scope

This package implements the canon-safe conclusions extracted from:

- Chenni Xu et al. (2026), *Photon-Sphere Modes in Curved Optical Microcavities: A Black-Hole Analogue Laser*, Advanced Science 13, e17466, DOI 10.1002/advs.202517466.

## Main-canon changes

1. Bumps the working edition to v0.8.29.
2. Adds a concise Fermat-metric optical-geometry guard next to the existing Swirl-Clock / optical closure.
3. Fixes the hierarchy:
   - index gradient / caustic candidate;
   - stationary Fermat circumference / circular light-ring candidate;
   - vanishing clock factor / horizon-like degeneracy candidate.
4. Makes explicit that no external SST light ring, event horizon, Einstein dynamics, or black-hole ontology is canonized.
5. Adds the source bibliography entry and an edition note.

## Research-track changes

1. Adds the general static Fermat reduction
   `d ell_F^2 = (B/A) dr^2 + (C/A) dphi^2`.
2. Derives the conditional SST light-ring gate
   `d[r/S_(t)]/dr = 0` and velocity-profile form
   `-r u u' = c^2-u^2`.
3. Audits the exterior inverse-radius profile and finds the formal radius
   `r_* = 7.27030e-18 m = 5.16001e-3 r_c`, inside the core and outside the profile's domain of validity.
4. Adds the Gaussian-curvature / Jacobi instability gate.
5. Adds the conditional high-m eikonal potential structure.
6. Adds spatial mode tomography using localized drive scans and adjoint overlap.
7. Refines the existing `photonless sphere / optical caustic` wording to `photonless appearance / optical caustic`.
8. Adds an apparatus-gain self-consistency guard: order-unity index modification would require `Q_gamma ~ 1.50229e5` at the canonical single-pass shift.
9. Retains the strict QSM complex-pole, absorber-convergence, and boundary-discrimination requirements.

## Epistemic status

- Fermat reduction and Jacobi stability: `[ORTHODOX]`.
- Mapping `n_gamma = S_(t)^(-1)` to a Fermat conformal factor: `[CONDITIONAL SST INTERPRETATION]`.
- Light-ring and eikonal formulas: `[RESEARCH TRACK]`, blocked until an actual SST wave branch/principal symbol is derived.
- Exterior inverse-radius result: `[PROFILE-SPECIFIC EXCLUSION]`.
- Spatial mode tomography: `[METHOD / HIGH-PRIORITY RESEARCH]`.

## Files

- `SST_CANON-v0.8.29.tex`
- `SST_CANON-v0.8.29-research-track.tex`
- `SST_CANON-v0.8.28_to_v0.8.29_fermat_optics.diff`
- `BUILD_VALIDATION.txt`

## Applying the patch

### Safest non-Git route

Place these package files beside the two v0.8.28 source files and run:

```bash
bash apply_patch.sh
```

The script preserves v0.8.28 and creates the two v0.8.29 files.

### Git route

From a repository containing the two v0.8.28 files:

```bash
git apply --check SST_CANON-v0.8.28_to_v0.8.29_fermat_optics.git.diff
git apply SST_CANON-v0.8.28_to_v0.8.29_fermat_optics.git.diff
```

The Git patch performs the v0.8.28 -> v0.8.29 renames and applies the content changes.
