# Validation Report - SST Canon v0.8.30

## Patch validation

- Both unified diffs pass GNU `patch --dry-run` against the v0.8.29 sources.
- Applying each diff with `patch -o` produces byte-identical copies of the packaged v0.8.30 sources.
- Original v0.8.29 files are not modified by the provided application script.
- CRLF line endings are preserved in both target files.

## Source validation

- Main source labels scanned: no duplicates across main Canon and Research Track.
- No remaining `rho_f(x,t)` occurrence exists in the canonical master equation.
- New cross-reference labels resolve:
  - `subsec:density_ontology_v0830`
  - `eq:density_ontology_v0830`
  - `eq:rhof_effective_response_alias`
  - `eq:rotational_translational_inertia_bridge_target`
  - `subsec:rt_historical_rhof_provenance_audit`
  - `eq:rt_vam7_historical_microinertia`
  - `eq:rt_vam7_microinertia_closed_form`

## LaTeX validation

Command:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_CANON-v0.8.30.tex
```

Result:

- PDF generated successfully;
- 231 A4 pages;
- zero fatal LaTeX errors;
- zero unresolved references;
- zero unresolved citations;
- zero multiply defined labels.

Existing non-fatal underfull/overfull box warnings remain editorial layout warnings and were not introduced as mathematical failures.

## Visual validation

Selected pages were rendered with PDFium at 150 dpi and visually inspected:

- title/version page;
- density provenance and ontology pages;
- Axiom 1 level-separation pages;
- source-register/changelog pages;
- historical VAM-7 provenance audit;
- transition into the existing SSDL route.

No clipping, overlapping text, missing glyphs, broken equation boxes, or malformed references were observed.

## Scientific scope check

The patch changes semantic status and provenance, not numerical calibration:

```text
rho_f = rho_eff^(0) = 7.0e-7 kg m^-3
```

remains calibrated, while the historical expression is recorded separately as

```text
J_omega^VAM ~= 6.84e-7 kg m^-1.
```

The patch does not claim a microphysical derivation of either quantity and does not modify the v0.8.29 SSDL result.
