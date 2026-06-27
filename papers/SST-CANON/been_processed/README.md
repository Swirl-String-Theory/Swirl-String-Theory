# SST Canon — been_processed

Copy-only archive: **root `SST_CANON-v0.8.1*.tex` files are never modified.**
All conversation patches are integrated in incremental copies below.

## Layout

| Path | Contents |
|------|----------|
| `sources/` | Copies of conversation diffs, patches, blocks, triage (originals remain in parent `SST-CANON/`) |
| `blocks/` | Reusable LaTeX blocks referenced by v0.8.2–v0.8.4 |
| `v0.8.2/` | Horn/circulation radius + envelope density semantic correction |
| `v0.8.3/` | Framed-tube ontology, trefoil closure, particle dictionary, Pauli `a_core` |
| `v0.8.4/` | EM–gravity bridge, finite-cell α obstruction summary, research-track extensions |

## Diff audit (what was applied)

### v0.8.2
- **Source:** `conversation_canon_patch.diff`, `highres_conversation_canon_followup.diff` (terminology + density hunks only)
- **Main:** Replace `Derived Length Scale` → `Derived Horn/Circulation Radius` (`-` in conversation diff)
- **Main:** `\rhocore` envelope label + critical note after `\eqref{eq:core_density}` (highres diff)
- **Main:** F_max / Coulomb / delay terminology pass (highres diff `-`/`+` lines)
- **Main:** Integration `Core density closure` → `Horn-Envelope Density Normalization` (conversation diff)
- **Skipped in v0.8.2:** framed-tube, particle table, trefoil topology, EMG, Pauli `a_core`

### v0.8.3
- **Source:** `conversation_canon_patch.diff`, `trefoil_closure_canon.diff`, remaining `highres` hunks
- **Main:** Framed-tube + attachment gate; updated particle table (conversation diff)
- **Main:** Twist-ladder + Euler preservation + Kairos event (trefoil diff `+` only)
- **Main:** R-to-T bridge + photon torsion bookkeeping (trefoil + highres; merged, not duplicated)
- **Main:** Electron trefoil persistence; Pauli `a_core`; softcore radius rule (highres diff)
- **Main:** State-transition taxonomy + trefoil appendix discipline; bibitems Rolfsen, Conway, Kida, Koplik
- **Skipped insert:** trefoil diff `Core-radius disambiguation` subsection (duplicate of v0.8.2 horn-radius content; no extra deletes)

### v0.8.4
- **Source:** `em_gravity_canon_block.tex`, condensed `finite_cell_obstruction_canon_block.tex`, `research_track_blocks_from_current_conversation.tex`
- **Main:** Inlined `em_gravity_canon_block.tex` before Unified Interpretation (`\ref{subsec:canonical_em_gravity_closure}`)
- **Main:** Finite-cell α obstruction summary in integration appendix
- **Research track:** Quark twist, gear/Borromean analogues, trefoil–gear kinematics, parked Higgs hypothesis

## Build

From repository root (uses `out/` via `latexmkrc`):

```powershell
cd papers/SST-CANON/been_processed/v0.8.2
latexmk -pdf -jobname=SST_CANON-v0.8.2 SST_CANON-v0.8.2.tex

cd ../v0.8.3
latexmk -pdf -jobname=SST_CANON-v0.8.3 SST_CANON-v0.8.3.tex

cd ../v0.8.4
latexmk -pdf -jobname=SST_CANON-v0.8.4 SST_CANON-v0.8.4.tex
```

## Scripts

- `apply_v082.py`, `apply_v083.py`, `apply_v084.py` — reproducible patch application

PDF output after compile: `out/SST_CANON-v0.8.x.pdf` (repo root) and `v0.8.x/$out/` (local aux from pdflatex).
