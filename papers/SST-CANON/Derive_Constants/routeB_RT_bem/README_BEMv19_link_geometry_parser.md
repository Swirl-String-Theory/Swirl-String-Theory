# BEMv19 link geometry parser

BEMv19 voegt de aparte multi-component parser toe voor links.

Doel: deze link-ID’s kunnen nu als geometry records worden meegenomen:

```text
L2a1
L4a1
L5a1
L6a1
L8a1
L6a4
L6n1
```

De huidige BEMv8/BEMv13/BEMv18 pipeline is nog single-component. BEMv19 draait daarom nog geen definitieve R--T determinant voor links, maar maakt de geometry-laag klaar.

## Run

```bash
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v19_links \
  --links L2a1,L4a1,L5a1,L6a1,L8a1,L6a4,L6n1
```

## Alle links uit ideal.txt pakken

```bash
python routeB_RT_bem_v19_link_geometry_parser.py \
  --ideal ideal.txt \
  --outdir outputs_routeB_BEM_v19_all_links \
  --include-all-links
```

## Outputs

```text
link_record_catalog.csv
link_component_catalog.csv
link_geometry_summary.csv
link_pair_distances.csv
link_gauss_linking_matrix.csv
link_missing_catalog.csv
link_parser_certificate.csv
link_routeB_integration_plan.md
link_multicomponent_appendix.tex
run_config_v19.json
```

## Wat wordt berekend?

Per link:

- aantal componenten;
- Fourier-coefficients per component;
- numerieke arclength per component;
- totale component-lengte;
- minimumafstand tussen componenten;
- Gauss linking integral per componentpaar;
- afgeronde linking estimate.

## Status

\[
\boxed{
\text{BEMv19: link geometry parser ready; block R--T operator open.}
}
\]

## Volgende stap

BEMv20 moet de single-component boundary map vervangen door een block operator:

\[
\Lambda^{\rm link}_{R/T}
=
(\Lambda^{R/T}_{ab})_{a,b=1}^{m}.
\]

Dan kunnen links echt in dezelfde Route-B spectral determinant komen.
