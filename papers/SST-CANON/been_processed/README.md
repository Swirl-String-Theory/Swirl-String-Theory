# SST Canon — been_processed

Copy-only archive: **root `SST_CANON-v0.8.1*.tex` files are never modified.**
Each conversation patch gets its own incremental edition.

## Layout

| Path | Contents |
|------|----------|
| `sources/` | Copies of conversation diffs, patches, blocks, triage |
| `blocks/` | Reusable LaTeX blocks |
| `v0.8.2/` … `v0.8.8/` | Incremental canon editions |

## Edition map (one patch → one version)

| Version | Adds on top of previous |
|---------|-------------------------|
| **v0.8.2** | Horn/circulation radius, envelope density, highres terminology |
| **v0.8.3** | Framed-tube ontology, trefoil closure, particle dictionary, Pauli `a_core` |
| **v0.8.4** | EM–gravity bridge, finite-cell α obstruction, research-track extensions |
| **v0.8.5** | Highres conversation audit + CALIBRATED circularity honesty |
| **v0.8.6** | Framed self-linking / spinorial lepton ladder (`subsec:framed_selflinking_spinorial`) |
| **v0.8.7** | Z₂ spinstats / CP¹ substrate paragraph + bibliography |
| **v0.8.8** | Gemini epistemic/notation audit (`\mathcal{P}_{\mathrm{cal}}`, `a_{\rm cut}`, etc.) |
| **v0.8.9** | Triadic gravity-response corollary + flame/caustic/shell research-track diagnostics |
| **v0.8.10** | Gemini round-2: `\vchar`/`uswirl` discipline, delay sign, epistemic relabeling |
| **v0.8.11** | Final hygiene: consistent `\mathcal{P}_{\mathrm{cal}}`, EMG/RT notation cleanup |
| **v0.8.12** | Gemini round-3: epistemic relabels, Pauli `a_{\rm cut}`, galaxy `\rhoF` caveat |

## Rebuild chain

```powershell
cd papers/SST-CANON/been_processed
python apply_v0812.py
```

Individual steps: `apply_v085.py` … `apply_v0812.py`.

Shared metadata: `canon_edition.py`. Patch blocks: `apply_framed_selflinking.py`, `apply_spinstats_z2.py`, `apply_spinstats_bibliography.py`, `apply_gemini_audit.py`.

## Build PDF

```powershell
cd papers/SST-CANON/been_processed/v0.8.8
pdflatex -interaction=nonstopmode SST_CANON-v0.8.8.tex
pdflatex -interaction=nonstopmode SST_CANON-v0.8.8.tex
```

Output: `out/SST_CANON-v0.8.x.pdf` at repo root (after copy).
