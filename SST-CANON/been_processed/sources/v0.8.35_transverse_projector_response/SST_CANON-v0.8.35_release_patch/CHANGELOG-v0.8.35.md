# SST Canon v0.8.35 release patch

## Patched release files

- `SST_Template.tex`
- `SST_CANON-v0.8.35-research-track.tex`

## Reviewed but intentionally unchanged

- `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex`

The speculative appendix explicitly states that its contents are outside the
release Canon and may change without a Canon version increment. No v0.8.35
claim depends on that appendix, so changing or renaming it would blur the
release/non-release boundary.

## Canon changes

1. Derives
   \[
   \int_{S^2}t_i(\delta_{ij}-\hat k_i\hat k_j)t_j\,d\Omega=8\pi/3
   \]
   from spatial isotropy.
2. Separates diameter-normalized \(L/D\) from radius-normalized \(L/a\):
   \[
   \frac{8\pi}{3}\frac LD
   =
   \frac{4\pi}{3}\frac La.
   \]
3. Reclassifies the previous finite-cell mode-count decomposition as historical
   bookkeeping rather than the unique origin of the prefactor.
4. Adds bare-projector and constant-circular-tube-volume no-go results.
5. Adds the alpha-blind finite-core response
   \[
   \Delta_{\rm micro}^{(+)}
   =
   c_\kappa I_{\kappa^2}
   +c_\Omega I_{\Omega^2}
   +c_C C_{\rm contact}+\cdots,
   \qquad c_L=0.
   \]
6. Uses \(SL=Wr+Tw\) as a helicity-sector constraint.
7. Derives the parity-even twist-energy bound
   \[
   I_{\Omega^2}\ge
   \frac{4\pi^2}{L/D}(SL-Wr)^2.
   \]
8. Keeps linear helicity in the separate parity-odd/theta-like response channel.
9. Links the response to the existing gauge-emergence certification ladder
   before any identification with \(\alpha^{-1}\).
10. Adds bend, twist, contact, holdout, cross-representation, cross-knot, and
    final-trefoil calibration gates.

## Numerical convention guard

- High-resolution branch:
  \(L/D=16.3714672385\), \(L/a=32.7429344770\),
  \(\Delta=-0.1172840362\).
- Gilbert branch:
  \(L/D=16.371637\), \(L/a=32.743274\),
  \(\Delta=-0.1187062268\).

The branches may not be mixed.