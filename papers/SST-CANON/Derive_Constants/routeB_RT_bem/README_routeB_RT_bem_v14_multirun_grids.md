# BEMv14 multirun over multiple grids

Ja — dit is inderdaad nodig als je meer wilt dan één intra-grid check.

Een enkele BEMv14-run test alleen **stabiliteit binnen één grid-familie**.
De multirun-wrapper test vervolgens of **dezelfde normalizer en blind budget**
ook overeind blijven over meerdere onafhankelijke grid-families.

## Wat dit script doet

Het script `routeB_RT_bem_v14_multirun_grids.py`:

1. draait `routeB_RT_bem_v14_certified_convergence.py` meerdere keren;
2. elke keer met een andere grid-familie;
3. verzamelt per grid de gekozen normalizer;
4. maakt een cross-grid consensus-audit.

## Belangrijkste outputs

- `multigrid_run_manifest.csv`
- `multigrid_selected_normalizers.csv`
- `multigrid_budget_aggregate.csv`
- `multigrid_consensus_summary.csv`
- `multigrid_report.md`

## Quick multirun

```bash
python routeB_RT_bem_v14_multirun_grids.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v14_multirun   --suite-profile quick
```

## Standard multirun

```bash
python routeB_RT_bem_v14_multirun_grids.py   --ideal ideal.txt   --outdir outputs_routeB_BEM_v14_multirun_std   --suite-profile standard
```

## Reuse-mode

Als je al een BEMv13-outputmap hebt en eerst alleen de wrapper wilt testen:

```bash
python routeB_RT_bem_v14_multirun_grids.py   --from-bemv13-outdirs outputs_routeB_BEM_v13_certified   --outdir outputs_routeB_BEM_v14_multirun_reuse   --suite-profile quick
```

Je mag ook meerdere BEMv13-mappen meegeven, één per grid-familie:

```bash
python routeB_RT_bem_v14_multirun_grids.py   --from-bemv13-outdirs outdir1,outdir2,outdir3   --outdir outputs_routeB_BEM_v14_multirun_reuse   --suite-profile quick
```

## Wanneer is dit geslaagd?

Pas als:

1. per grid-familie een stabiele normalizer passeert;
2. dezelfde normalizer terugkomt over meerdere grids;
3. de cross-grid spreiding klein blijft.

Dus ja:

\[
\boxed{
\text{multirun over meerdere grids is de juiste volgende stap.}
}
\]

Maar ook dit blijft nog een **Route-B falsifier/provenance gate**, geen definitieve alpha-afleiding.