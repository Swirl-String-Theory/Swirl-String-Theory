# BEMv18 KnotPlot-aware extended scan

Deze variant ondersteunt nu ook jouw nieuw toegevoegde KnotPlot-notatie:

```text
K11a367
K11a247
```

Deze worden als echte run-targets opgenomen als ze in jouw lokale `ideal.txt` staan.

Daarnaast catalogiseert hij de links:

```text
L2a1
L4a1
L5a1
L6a1
L8a1
L6a4
L6n1
```

maar hij draait die **niet standaard**, omdat de huidige BEMv8/BEMv13 route single-component centerline knots verwacht. Links hebben een aparte multi-component parser nodig.

## Default target policy

Run-targets:

```text
all ordinary knots up to and including 7 crossings
+ 8_1, 9_1, 9_2, 10_1
+ K11a367, K11a247 if present
```

Catalog-only links:

```text
L2a1, L4a1, L5a1, L6a1, L8a1, L6a4, L6n1
```

## Plan run

```bash
python routeB_RT_bem_v18_extended_local_scan_knotplot.py --ideal ideal.txt --outdir outputs_routeB_BEM_v18_knotplot_plan --dry-run-plan
```

## Fast run

```bash
python routeB_RT_bem_v18_extended_local_scan_knotplot.py --ideal ideal.txt --outdir outputs_routeB_BEM_v18_knotplot_fast --run --n-center 8 --n-theta 3 --n-sphere 14 --tube-fraction 0.34 --outer-factor 2.4 --pair-fit-min-M 4 --length-samples 2000
```

## Production run

```bash
python routeB_RT_bem_v18_extended_local_scan_knotplot.py --ideal ideal.txt --outdir outputs_routeB_BEM_v18_knotplot --run --n-center 24 --n-theta 5 --n-sphere 96 --tube-fraction 0.30 --outer-factor 3.0 --pair-fit-min-M 8 --length-samples 12000
```

## Outputs

```text
target_catalog_run_available.csv
target_catalog_links_available.csv
target_catalog_missing_or_skipped.csv
targets_run_available.json
targets_links_available.json
run_manifest.csv
aggregate/bemv18_exponent_certificate.csv
aggregate/bemv18_length_exponent_scan.csv
aggregate/bemv18_raw_multiknot_budget.csv
```

## Notes on K11 aliases

The file `BEMv18_knotplot_aliases.json` keeps the alias metadata separate. I did **not** hard-rename `K11a367` and `K11a247` to `11_1` and `11_2`, because the exact ordering can be adjusted there without changing the solver. The actual BEM run uses the IDs from `ideal.txt`.