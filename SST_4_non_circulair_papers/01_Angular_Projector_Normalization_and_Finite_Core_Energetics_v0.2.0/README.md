# Angular-Projector Normalization and Finite-Core Energetics - v0.2.0

This package contains the revised orthodox manuscript, compiled PDF, audit response,
changelog, a source diff from v0.1.0, and reproducibility material for the stored
Fourier trefoil record.

## Main files

- `Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.tex`
- `Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.pdf`
- `CHANGELOG_v0.2.0.md`
- `AUDIT_RESPONSE_v0.2.0.md`
- `VALIDATION_v0.2.0.json`

## Supplementary reproducibility files

- `Supplementary_Data_S1_Gilbert_trefoil_record.xml`
- `Supplementary_Code_S1_numerical_checks.py`
- `Supplementary_Numerical_Checks_v0.2.0.json`

Run the numerical checks with:

```bash
python Supplementary_Code_S1_numerical_checks.py
```

Compile the manuscript with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.tex
pdflatex -interaction=nonstopmode -halt-on-error Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.tex
pdflatex -interaction=nonstopmode -halt-on-error Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.tex
```

The bibliography is embedded in the LaTeX source; BibTeX is not required.
Old exploratory archive papers are not cited or used as scientific support.
