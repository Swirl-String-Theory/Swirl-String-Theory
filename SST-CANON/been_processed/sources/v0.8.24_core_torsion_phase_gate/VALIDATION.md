# Validation report

## Baseline

The supplied v0.8.23 pair was compiled with three `pdflatex` passes:

- 209 pages;
- 0 undefined-reference/citation warnings after convergence;
- 0 multiply-defined-label warnings;
- 56 overfull-box warnings.

## Patched v0.8.24

The applied v0.8.24 pair was compiled with three `pdflatex` passes:

- 213 A4 pages;
- 0 undefined references;
- 0 undefined citations;
- 0 multiply-defined-label warnings;
- 0 rerun-required cross-reference warnings;
- 57 overfull-box warnings, predominantly inherited/cosmetic.

The newly introduced long axiom-dependency chain was reflowed into a multiline
aligned equation; the initial 400-pt overflow was removed before packaging.

## Static checks

- CRLF line endings preserved in both `.tex` files.
- No stale `canon-0.8.1-research-track.tex` pointer.
- No `Æther element(s)` terminology remains outside the Einstein--Æther EFT
  comparison context.
- No active `2E_0/c_T^2` theorem target remains; occurrences of `2E_0` are
  confined to explicit historical normalization notes.
- No concatenated `\subsection`/`\subsubsection` commands remain at the audited
  merge-artifact locations.
- All seven new citation keys resolve in the combined build.

## Patch reproducibility

Two independent application routes were tested from clean copies of the exact
v0.8.23 sources:

1. `git apply` with automatic rename;
2. GNU `patch --binary` after copying to the v0.8.24 names.

Both routes produced byte-identical `.tex` files to the applied sources included
in this package.

## Visual verification

The compiled PDF was rendered and inspected at the title/TOC and the principal
changed pages, including the geometry-certification rule, falsifier taxonomy,
two-speed normalization, material--link postulate, deconfinement gate,
link-spacing scenarios, and corrected core--torsion lemma. No clipping,
overlap, black glyph blocks, or broken equations were observed on those pages.
