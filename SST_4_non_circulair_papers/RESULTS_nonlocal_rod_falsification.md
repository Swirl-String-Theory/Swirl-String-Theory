# Falsification run — non-local extension of the Hopf-soliton rod model

Date: 3 August 2026
Code: `tab.py`, `fast2.py`, `sens.py` (+ `falsify_nonlocal_rod.py`, the slow reference version)
Status: **preregistered gate F4 FAILS at the quoted central values, but the failure is not robust.**

---

## Model under test

Reference (Harland–Speight–Sutcliffe, Phys. Rev. D **83**, 065008 (2011), arXiv:1010.3189):

    E_HSS = ∫₀^L [ 1 + κ² + C (α′ − τ)² ] ds

Proposed extension — one new term, one new parameter:

    E_nl = (g/2) ∮∮ t(s)·t(s′) / √( |γ(s) − γ(s′)|² + a² ) ds ds′

with `a` = rod thickness `R`, fixed self-consistently by HSS's own rule `R = L₁/2π = r₁`.

---

## Module 1 — implementation validated against published numbers

Analytic axial sector: minimizing `E(r) = 2πr + 2π(1+CQ²)/r` gives `r = √(1+CQ²)`,
`L = 2πr`, `E = 4πr`.

| Q | E computed | E published | L computed | L published |
|---|---|---|---|---|
| 1 | 17.09 | 17.09 | 8.55 | 8.55 |
| 2 | 26.36 | 26.36 | 13.18 | 13.18 |
| 3 | 36.96 | 36.96 | 18.48 | 18.48 |

Michell window reproduced: first buckling at Q = 3 requires `C ∈ [0.5774, 0.8660)`.
HSS chose `C = 0.85`, inside. **Implementation validated.**

## Module 2 — non-local kernel validated

Exact scaling reduction derived and checked: `E_self(r,a) = r·F(a/r)` with
`F(x) = π ∫₀^{2π} cos u / √(4 sin²(u/2) + x²) du`.

| r | a | scaling form | brute-force O(n²) | thin-ring asymptote 2πr(ln 8r/a − 2) |
|---|---|---|---|---|
| 10 | 0.10 | 294.3503 | 294.3503 | 294.3428 |
| 5 | 0.05 | 147.1752 | 147.1752 | 147.1714 |
| 1.36 | 1.36 | 3.3597 | 3.3597 | 0.6788 |

Scaling form matches brute force to all digits, and matches the classical thin-ring
result in the thin limit. **Kernel validated.**

Note the last row: at the model's actual operating point the asymptote is wrong by a
factor 5.

---

## Module A — a genuine positive result

At `g = 0` the circular rod has `E = 4πr` and `L = 2πr`, so

    E₂/E₁ ≡ L₂/L₁   identically, for every C.

The Skyrme–Faddeev targets are `E₂/E₁ = 1.63` and `L₂/L₁ = 1.45` — **12.4% apart**.

**No choice of C can fit both.** The non-local term breaks the virial relation
`E = 2L` and is therefore not an optional refinement: it is the minimal ingredient
that makes the two axial observables independent at all. This is an argument for the
term that neither I nor HSS had stated.

---

## Module B — calibration

Two parameters, two observables, exactly determined:

    C = 0.86802      g = 0.52842      residual = 8.5 × 10⁻²⁰
    E₂/E₁ = 1.6300   L₂/L₁ = 1.4500   (both hit exactly)
    thickness a = R = r₁ = 1.11231    E₁ = 18.993

`g > 0`: the term raises the energy of compact configurations, the sign required.

### GATE F4 — DECISIVE, PREREGISTERED

    Michell window (first buckling at Q=3):  C ∈ [0.5774, 0.8660)
    Fitted C = 0.86802                        → OUTSIDE, by 0.23%
    Implied first buckling charge:            Q = 2

**RESULT: FAIL.**

The fitted model buckles the circular rod at Q = 2, contradicting the established
Skyrme–Faddeev result that Q = 1 and Q = 2 minimizers are axially symmetric and the
first buckled minimizer is Q = 3.

This is exactly the degeneracy predicted in advance as F4: C and g both raise the
energy of compact configurations, so calibrating them jointly pushes C past its
allowed ceiling.

### Robustness — the failure does not survive input uncertainty

The SF targets are quoted to three significant figures. Refitting over a grid:

| E₂/E₁ | L₂/L₁ | C | g | Michell | first buckle |
|---|---|---|---|---|---|
| 1.60 | 1.43 | 0.7824 | 0.5261 | PASS | 3 |
| 1.60 | 1.45 | 0.8177 | 0.4155 | PASS | 3 |
| 1.60 | 1.47 | 0.8530 | 0.3256 | PASS | 3 |
| 1.63 | 1.43 | 0.8285 | 0.6606 | PASS | 3 |
| **1.63** | **1.45** | **0.8680** | **0.5284** | **FAIL** | **2** |
| 1.63 | 1.47 | 0.9077 | 0.4223 | FAIL | 2 |
| 1.66 | 1.43 | 0.8754 | 0.8145 | FAIL | 2 |
| 1.66 | 1.45 | 0.9194 | 0.6557 | FAIL | 2 |
| 1.66 | 1.47 | 0.9638 | 0.5300 | FAIL | 2 |

**PASS in 4 of 9 variants.** C spans 0.782–0.964 across the grid; the window edge
0.866 sits in the middle of that spread.

Honest verdict: **the gate fails at the central values but flips within the precision
of the published inputs.** The test as preregistered is therefore *not decisive at the
available data precision*. That is itself the finding — a two-observable calibration
does not constrain this model well enough to be falsified or confirmed.

---

## Module C — axial tower overshoots

With the fitted parameters:

| Q | r | L | E | E/E₁ | Q^0.75 | deviation |
|---|---|---|---|---|---|---|
| 1 | 1.112 | 6.99 | 18.99 | 1.000 | 1.000 | +0.0% |
| 2 | 1.613 | 10.13 | 30.96 | 1.630 | 1.682 | −3.1% |
| 3 | 2.161 | 13.58 | 45.38 | 2.389 | 2.280 | +4.8% |
| 4 | 2.717 | 17.07 | 61.02 | 3.213 | 2.828 | +13.6% |
| 5 | 3.272 | 20.56 | 77.40 | 4.075 | 3.344 | +21.9% |
| 6 | 3.823 | 24.02 | 94.30 | 4.965 | 3.834 | +29.5% |
| 7 | 4.370 | 27.46 | 111.60 | 5.876 | 4.304 | +36.5% |

The original defect was that rod energies grow **too slowly** (−8% to −17%). The
non-local term **overcorrects**: the axial tower now grows too fast (+37% at Q = 7).

Caveat, stated plainly: the axial branch is an upper bound for Q ≥ 3, since the true
minimizers are buckled, linked or knotted. The requirement becomes that the Q = 7
trefoil sit 26.8% below the axial value, against 25.3% in the g = 0 model. So the
overshoot is *not* by itself fatal — but it removes the headroom that motivated the
extension.

---

## Module D — the operating point has no small parameter

The self-consistency condition `R = r₁` yields

    a / r₁ = 1.0000  exactly.

The rod's thickness equals its own ring radius: a torus with no hole. There is no
thin-tube regime anywhere in this model, so any expansion organized in powers of
`a/r` or `Dκ` has expansion parameter of order unity.

This is the same pathology independently identified in the ropelength manuscript
(κ̂ = Dκ = 2 at contact for the ideal trefoil). Finding it again, in an unrelated
model fitted to unrelated data, suggests it is generic to tight-knot energetics
rather than an artefact of either construction.

---

## Verdict

| item | result |
|---|---|
| Implementation vs HSS published values | **validated exactly** |
| Non-local kernel vs brute force and thin-ring limit | **validated** |
| Non-local term is *necessary* (E₂/E₁ ≠ L₂/L₁) | **new positive result** |
| Two-parameter fit to Q = 1, 2 | exact, C = 0.868, g = 0.528 |
| **Gate F4 (Michell buckling)** | **FAIL at central values; PASS in 4/9 nearby variants** |
| Axial tower scaling | overcorrects, +36.5% at Q = 7 |
| Thin-tube expansion parameter | 1.0 — no small parameter exists |

**Bottom line.** The proposal is not cleanly falsified and not confirmed. It fails its
own preregistered gate at the published central values, by 0.23%, and the outcome
reverses within the quoted precision of those values. The honest conclusion is that
the axial sector carries too little information to decide, and that the decisive test
requires the non-axial minimizers — i.e. the relaxation runs that were deliberately
avoided here.

**What would decide it.** Three additional observables, in order of cost:
1. `L₃/L₁` and `E₃/E₁` for the buckled Q = 3 soliton (one relaxation run).
2. The link energies at Q = 4, 5, 6 (two circles plus a mutual interaction; no
   relaxation needed, but a 3-parameter minimization).
3. Higher-precision SF values for `E₂/E₁` and `L₂/L₁`, which would alone settle
   gate F4.

Item 3 is free if the numbers exist in the Skyrme–Faddeev literature at more than
three significant figures. That should be checked before any further computation.
