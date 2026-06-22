# Route B BEMv17 principal-symbol / heat-kernel audit

BEMv17 sharpens the BEMv16 conditional certificate.

BEMv16 said:

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}
\]

provided mode-extensivity and second-order length covariance hold.

BEMv17 identifies the exact principal-symbol obligation:

\[
\sigma\!\left[\log(\Lambda_R\Lambda_T^{-1})\right]
=
q_{-2}(x,\xi)
+
q_{-3}(x,\xi)+\cdots
\]

after soft-sector removal and pair subtraction.

If the first surviving residual is \(q_{-2}\), then:

\[
\Delta F_{\rm phys}
=
\frac{\Delta F_{\rm pair}}
{M_{\max}L_{\rm cert}^{2}}.
\]

## Run

```bash
python routeB_RT_bem_v17_principal_symbol_heat_kernel.py \
  --v16-outdir outputs_routeB_BEM_v16_heat_kernel \
  --outdir outputs_routeB_BEM_v17_principal_symbol
```

## Outputs

```text
bemv17_symbol_hierarchy.csv
bemv17_heat_kernel_coefficients.csv
bemv17_exponent_uniqueness.csv
bemv17_proof_gap_register.csv
bemv17_principal_symbol_certificate.csv
bemv17_principal_symbol_appendix.tex
bemv17_principal_symbol_report.md
run_config_v17.json
```

## Status

BEMv17 is still conditional. It does not derive alpha.

It says the next exact mathematical target is:

\[
\boxed{
q_{-2}(x,\xi)
}
\]

as the first surviving pair-subtracted R--T residual symbol.
