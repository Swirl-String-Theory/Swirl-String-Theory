# Route B BEMv15 normalizer law

BEMv15 starts the analytic step after BEMv14.

BEMv14 showed, across multiple grid families, that the certified-length budget repeatedly selects:

\[
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
\]

BEMv15 does **not** run a new BEM solve. It ingests Stage A/B/C/D results and writes a conditional normalizer-law certificate.

## Run on Stage A/B/C/D zips

```bash
python routeB_RT_bem_v15_normalizer_law.py \
  --inputs outputs_routeB_BEM_v14_stageABC.zip,outputs_routeB_BEM_v14_stageD.zip \
  --outdir outputs_routeB_BEM_v15_normalizer_law
```

## Outputs

```text
bemv15_stage_summary.csv
bemv15_consensus_summary.csv
bemv15_budget_points.csv
bemv15_exponent_scan.csv
bemv15_normalizer_law_certificate.csv
bemv15_normalizer_law_appendix.tex
bemv15_normalizer_law_report.md
run_config_v15.json
```

## Core statement

Under:

1. mode-extensivity of the truncated pair spectral action,
2. length-scale covariance of the finite R--T density,

the minimal separable monomial normalizer is:

\[
\boxed{
\mathcal N_{\rm RT}=M_{\max}L_{\rm cert}^{2}.
}
\]

## Important limitation

The exponent \(b=2\) cannot be learned from single-knot data alone because \(L_{\rm cert}(3_1)\) is fixed across the current grids. BEMv15 therefore marks the result as conditional.

The next gate should be a heat-kernel / DtN proof or a multi-knot certified-length test.
