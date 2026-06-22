# Route B BEMv7 spectral-length budget

BEMv7 implements the corrected component logic:

\[
\alpha^{-1}_{\rm pred,blind}
=
\frac12\left[
N_{\rm soft}V_{\rm soft}L_{\rm HK}(3_1)
+
\Delta_{\rm RT}^{\rm ren}(3_1/0_1)
\right].
\]

It separates the large leading scale from the finite correction:

\[
L_{\rm HK}(K)=2\pi\,\frac{A_{\rm lead}(K)}{A_{\rm lead}(0_1)}.
\]

No CODATA alpha is used.

## Outputs

```text
hk_length_coefficients.csv
spectral_length_estimate.csv
finite_rt_correction.csv
alpha_component_budget.csv
blind_alpha_prediction_v7.md
```

BEMv7 also creates or reuses a BEMv5 output folder containing raw spectra.

## Fast run

```bash
python routeB_RT_bem_v7_spectral_length_budget.py  --ideal ideal.txt   --outdir outputs_routeB_BEM_v7_fast   --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1   --n-center 12 --n-theta 4 --n-sphere 32   --length-fit-min-M 4   --counterterm-fit-min-M 4
```

## More serious run

```bash
python routeB_RT_bem_v7_spectral_length_budget.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v7   --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1,5:1:1,5:1:2   --n-center 48 --n-theta 8 --n-sphere 256   --length-fit-min-M 10   --counterterm-fit-min-M 10
```

## Reuse BEMv5 output

```bash
python routeB_RT_bem_v7_spectral_length_budget.py   --from-bemv5-outdir outputs_routeB_BEM_v5_fast   --outdir outputs_routeB_BEM_v7_from_v5
```

## Interpretation

BEMv7 is not yet an alpha derivation. It is the first component-budget version. The next gate is convergence: \(L_{\rm HK}\), \(\Delta_{\rm RT}^{\rm ren}\), and the total blind budget must stabilize under mesh, tube-radius, and outer-boundary refinement.