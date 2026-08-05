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

### Provenance of Supplementary Data S1

`Supplementary_Data_S1_Gilbert_trefoil_record.xml` contains a third-party
Fourier record of the trefoil. The coefficient payload is preserved verbatim
from the supplied local source copy; a structured provenance header has been
added by the manuscript author.

The embedded source identifies the originating dataset as **Database of Ideal
Knots 3-10 crossings**, compiled by **Brian Gilbert**, with source date
`6/11/2016 2:12:11 p.m.` (date locale unstated). The corresponding Knot Atlas
resource is the page `Ideal knots` and the file-history entry for
`Ideal.txt.gz`, uploaded by user `BrianGilbert` on 6 November 2016. The local
source copy used for extraction is `ideal_favorites.txt`; its retrieval date was
not recorded.

No file-specific licence statement was found in the supplied record or on the
Knot Atlas file page. Public redistribution status is therefore unresolved.
Before distributing the XML coefficient payload, confirm the applicable terms;
otherwise exclude the XML and supply source-identification and extraction
instructions. Attribution does not by itself resolve redistribution rights.

The record is diagnostic only. No scalar result in the article depends on it:
the metadata length is used for the Fourier branch, and the reconstructed
geometry is used only for the curvature and writhe diagnostics reported in the
appendix.

After editing, regenerate and verify the manifest with:

```bash
python 0006-build-manifest.py --root .
python 0007-verify-release.py --root .
```

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

<!-- PAPER1_RELEASE_NOTE_v0.2.1 -->
## Release version note

The manuscript source is release **v0.2.1**. Files whose names still contain
`v0.2.0`, including numerical JSON/validation artifacts, are frozen outputs of
the v0.2.0 computational run and intentionally retain their original names.
They must not be silently relabelled as regenerated v0.2.1 results.
