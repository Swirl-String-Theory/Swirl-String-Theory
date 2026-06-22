# Route B BEMv16 heat-kernel normalizer

BEMv16 is the analytic/proof-obligation step after BEMv15.

It does **not** run a new BEM solve and it does **not** use observed alpha.

It certifies the conditional normalizer:

\[
\boxed{
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
}
\]

## Run

```bash
python routeB_RT_bem_v16_heat_kernel_normalizer.py \
  --v15-outdir outputs_routeB_BEM_v15_normalizer_law \
  --outdir outputs_routeB_BEM_v16_heat_kernel
```

## Outputs

```text
bemv16_proof_obligations.csv
bemv16_scaling_law_table.csv
bemv16_normalizer_derivation.csv
bemv16_v15_numeric_link.csv
bemv16_heat_kernel_certificate.csv
bemv16_heat_kernel_appendix.tex
bemv16_heat_kernel_report.md
run_config_v16.json
```

## Status

BEMv16 proves the normalizer only conditionally:

1. R--T maps are first-order DtN/Steklov boundary operators.
2. The pair action is mode-extensive in \(M_{\max}\).
3. The residual finite density has second-order length covariance.

Under these assumptions:

\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

The next gate is BEMv17: derive the \(L_{\rm cert}^{2}\) covariance from the principal symbol / heat-kernel coefficients.
