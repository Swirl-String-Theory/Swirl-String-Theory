# Transverse Projection and Finite-Core Response of Tight Knotted Vortex Tubes

Orthodox preprint-style reformulation of a geometric and finite-core vortex-response programme.

## Contents

- `Transverse_Projection_and_Finite_Core_Response_of_Tight_Knotted_Vortex_Tubes.pdf` — compiled 19-page article.
- `Transverse_Projection_and_Finite_Core_Response_of_Tight_Knotted_Vortex_Tubes.tex` — self-contained `revtex4-2` LaTeX source with an inline bibliography and TikZ figures.
- `VALIDATION.json` — build and PDF checks.
- `SHA256SUMS.txt` — file hashes.

## Build

```bash
pdflatex -interaction=nonstopmode -halt-on-error Transverse_Projection_and_Finite_Core_Response_of_Tight_Knotted_Vortex_Tubes.tex
pdflatex -interaction=nonstopmode -halt-on-error Transverse_Projection_and_Finite_Core_Response_of_Tight_Knotted_Vortex_Tubes.tex
pdflatex -interaction=nonstopmode -halt-on-error Transverse_Projection_and_Finite_Core_Response_of_Tight_Knotted_Vortex_Tubes.tex
```

The bibliography is embedded in the `.tex` file, so BibTeX is not required.

## Epistemic scope

The article derives the isotropic transverse-projector identity and standard Euler–Biot–Savart relations. It treats finite-core coefficients and electromagnetic gauge-stiffness identification as open matching problems. The fine-structure constant is used only as an external final-test target, not as calibration input.
