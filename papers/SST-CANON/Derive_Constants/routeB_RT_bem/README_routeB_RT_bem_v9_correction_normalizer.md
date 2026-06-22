# Route B BEMv9 finite-correction normalizer audit

BEMv8 restored the leading length scale, but the finite pair correction remained too large in raw units.

BEMv9 scans alpha-blind finite-correction normalizers:

\[
\Delta F_{\rm phys}^{(q)}
=
\frac{\Delta F_{\rm pair}}{\mathcal N_q}.
\]

Then it computes:

\[
\alpha^{-1}_{\rm pred,blind}^{(q)}
=
\frac12
\left[
N_{\rm soft}V_{\rm soft}L_{\rm long}
+
\Delta F_{\rm phys}^{(q)}
\right].
\]

No observed alpha is used.

## Outputs

```text
finite_correction_normalizers.csv
alpha_budget_v9_candidates.csv
correction_gate_report.md
blind_alpha_prediction_v9.md
run_config_v9.json
```

If BEMv9 launches BEMv8 internally, it also writes:

```text
bemv8_base/
```

## Fast reuse of existing BEMv8 run

```bash
python routeB_RT_bem_v9_correction_normalizer.py \
  --from-bemv8-outdir outputs_routeB_BEM_v8_fast \
  --outdir outputs_routeB_BEM_v9_from_v8
```

## Full run

```bash
python routeB_RT_bem_v9_correction_normalizer.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v9 \
  --ideal-xml-knot-ids 0:1:1,3:1:1,4:1:1 \
  --n-center 48 --n-theta 8 --n-sphere 256 \
  --length-samples 24000 \
  --pair-fit-min-M 10
```

## Default normalizers

```text
raw
Mmax
sqrtM
L
L2
L3
NsoftV
NsoftV_L
leading_full
leading_half
M_L
sqrtM_L
M_L2
```

A normalizer passes the first gate only if:

\[
|\Delta F_{\rm phys}|/(N_{\rm soft}V_{\rm soft}L_{\rm long}) \le 0.05.
\]

That threshold is not an alpha fit. It is only a subleading-correction gate.

## Interpretation

BEMv9 is still not a derivation. It identifies which internal normalizers make the finite correction subleading. The next gate is convergence: the same normalizer must remain stable under BEMv6-style mesh/tube/outer-boundary refinement.
