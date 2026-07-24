# SST Canon v0.8.24 -> v0.8.25 clean KAM patch

This package creates Canon v0.8.25 from the two unmodified v0.8.24 LaTeX sources.

The release remains focused on the scientific KAM-stability programme. The periodic exponential modulation, the specific `T(6,9)` three-trefoil construction, the `3 x 3` phase product, and modulo-nine update laws are excluded from the release Canon and release research track. They are preserved in a separately versioned, explicitly non-release speculative appendix.

## Included sources

- `SST_CANON-v0.8.25.tex` - complete patched main Canon.
- `SST_CANON-v0.8.25-research-track.tex` - complete patched release research-track companion.
- `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex` - standalone non-release appendix; it is not input by the Canon.

## Diff files

- `SST_CANON-v0.8.24-to-v0.8.25-clean.diff` - complete rename-aware diff, including the non-release appendix.
- `SST_CANON-v0.8.24-to-v0.8.25-release-only.diff` - main Canon and release research track only.
- `01-main-canon-kam-interface.diff` - main-Canon subpatch.
- `02-research-track-kam-module.diff` - release research-track subpatch.
- `03-nonrelease-speculative-appendix.diff` - creates the standalone appendix.

Equivalent `.patch` copies of the two combined diffs are also included.

## Release scope retained in v0.8.25

The release adds:

1. the distinction between spatial vortex-line confinement (`KAM-S`) and temporal knot-shape stability (`KAM-T`);
2. the LIA/Hasimoto layer as a candidate integrable reference and the finite-core full Biot-Savart correction as a measured `[BRIDGE/RESEARCH]` perturbation;
3. a required relative-equilibrium or periodic-relative-orbit gate;
4. symmetry-reduced Floquet and Krein-signature checks;
5. nonlinear normal-form, twist, non-resonance, Poincare-map, invariant-torus, and action-drift diagnostics;
6. the vector-valued KAM certificate and KAM-0 through KAM-5 promotion ladder;
7. the golden or noble rotation number only as a preregistered controlled null-test hypothesis;
8. rejection of the open golden logarithmic spiral as a closed particle centreline.

The release explicitly does not select a replacement modulation geometry and does not promote a composite link or modulo-class phase law.

## Non-release appendix scope

`SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex` preserves, with hard status guards:

- periodic exponential modulation as `[ANSATZ]`;
- `T(6,9)` as a `[RESEARCH CANDIDATE]` consisting topologically of three trefoils;
- `Z_3 x Z_3` phase labels as a structural Ansatz, with the guard `Z_3 x Z_3 != Z_9`;
- an order-nine carry map as `[SPECULATIVE]` bookkeeping until physically derived;
- the doubling map modulo nine as exact discrete mathematics with open physical status;
- Rodin-style toroidal projection as inspiration only.

The appendix states that none of these items may tune a Canon calibration, optimizer, null test, mesh, initial-condition selector, or stopping rule.

## Applying the complete diff

Place the diff beside the two unmodified v0.8.24 files:

```bash
git apply --check SST_CANON-v0.8.24-to-v0.8.25-clean.diff
git apply SST_CANON-v0.8.24-to-v0.8.25-clean.diff
```

The patch renames the two release files to v0.8.25 and creates the non-release appendix.

To exclude the appendix:

```bash
git apply --check SST_CANON-v0.8.24-to-v0.8.25-release-only.diff
git apply SST_CANON-v0.8.24-to-v0.8.25-release-only.diff
```

## Building

Main Canon plus release research track:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_CANON-v0.8.25.tex
```

Standalone non-release appendix:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex
```

The main Canon inputs only:

```latex
\input{SST_CANON-v0.8.25-research-track}
```

It does not input the speculative appendix.

## Verified regression

| Check | v0.8.24 | v0.8.25 clean |
|---|---:|---:|
| Main PDF pages | 213 | 224 |
| Undefined references | 0 | 0 |
| Undefined citations | 0 | 0 |
| Multiply-defined labels | 0 | 0 |
| LaTeX errors | 0 | 0 |
| Overfull hboxes | 57 | 57 |
| Underfull hboxes | 104 | 104 |

The standalone speculative appendix compiles to 4 pages with zero unresolved references, zero unresolved citations, zero multiply-defined labels, and zero LaTeX errors.

The complete diff passed `git apply --check`, was applied to clean copies of both v0.8.24 sources, and the resulting three source files were byte-compared with the packaged outputs.
