# SST Canon — been_processed

Copy-only archive: **root `SST_CANON-v0.8.1*.tex` files are never modified.**
Each conversation patch gets its own incremental edition.

## Layout

| Path | Contents |
|------|----------|
| `sources/` | **All** conversation diffs, patch blocks, audits, verify scripts, evidence packs (canonical archive) |
| `blocks/` | Reusable LaTeX blocks integrated into editions |
| `v0.8.2/` … `v0.8.19/` | Incremental canon editions (`$out/` = build artifacts) |

The `papers/SST-CANON/` root holds only `latexmkrc`, `archive/`, and `been_processed/` — no patch source files.

## Edition map (one patch → one version)

| Version | Adds on top of previous |
|---------|-------------------------|
| **v0.8.2** | Horn/circulation radius, envelope density, highres terminology |
| **v0.8.3** | Framed-tube ontology, trefoil closure, particle dictionary, Pauli `a_core` |
| **v0.8.4** | EM–gravity bridge, finite-cell α obstruction, research-track extensions |
| **v0.8.5** | Highres conversation audit + CALIBRATED circularity honesty |
| **v0.8.6** | Framed self-linking / spinorial lepton ladder (`subsec:framed_selflinking_spinorial`) |
| **v0.8.7** | Z₂ spinstats / CP¹ substrate paragraph + bibliography |
| **v0.8.8** | Epistemic/notation audit (`\mathcal{P}_{\mathrm{cal}}`, `a_{\rm cut}`, etc.) |
| **v0.8.9** | Triadic gravity-response corollary + flame/caustic/shell research-track diagnostics |
| **v0.8.10** | `\vchar`/`uswirl` discipline, delay sign, epistemic relabeling |
| **v0.8.11** | Final hygiene: consistent `\mathcal{P}_{\mathrm{cal}}`, EMG/RT notation cleanup |
| **v0.8.12** | epistemic relabels, Pauli `a_{\rm cut}`, galaxy `\rhoF` caveat |
| **v0.8.13** | Relativity emergence: main-canon `c_{13}=0` naturalness + research-track Relativity Emergence Ladder |
| **v0.8.14** | Two-speed clock discipline (`\vchar` vs `c`, NLSE `c_s`) + α-gate guard + research-track core–torsion impedance lemma |
| **v0.8.15** | Lorentz-type swirl-stress (canon) + EM-to-swirl correspondence / SST-44 stress (research track) |
| **v0.8.16** | Pressure–optical locking + no-monopole audit + relativity falsifier ladder (+ SST-73 notes) |
| **v0.8.17** | RC1: `\vchar{}^n` superscript fix, `\alpha_{\mathrm{grav}}`, RT bib guard (`\ifresearchtrackincluded`), G7 ring-constant audit + cross-ref, geometric `M_0(T)` baseline branch, orthodox Planck/Schwarzschild reparam note, companion-header hygiene. **RC2 (release-clean):** p.119 boxed summary → quote (drop uncited eq label), `\AE{}`-modes fix, range-exact `tabularx` on two particle-candidate tables only, targeted v0.8.1 phrase/comment cleanup. **TOC/appendix restructure** (appendices A–O only in TOC, Appendix D edition notes nested, research-track parents L–O). |
| **v0.8.18** | **Guardrails v2:** calibration-chain guards (rc/$\alpha$ gates, kernel normalization scale, EM prefactor $m_e/e$, Rydberg dimensional guard, $\rhohorn$ fix in `M_0(T)` baseline, matching-ansatz relabel on explicit kernel), RT observational falsifier bounds (GW170817, pulsar $\hat\alpha_{1,2}$). **Resolved-tube v3:** orthodox reach/thickness definitions (`eq:a_core_reach_thickness`), research appendix `app:resolved_tube_contact_stress_geometry`. **Four-insights v1+v2:** topology/stability appendices, $Q_8$, cites; **v2:** knot-energy normal form (`eq:research_track_energy_normal_form`), $I_G$ scalarization in RT energy equations. **Golden-layer hyperbolic rapidity.** **Euler/Magnus probe-transport polish** (`eq:rt_*_transport`, Zhang bib). **Canonical time ontology** (`subsec:canonical_time_ontology`); no-bare-$\tau$ policy ($\tau_{\rm circ}$, $\tau_A$). **Compton--horn / $G_{\mathrm{swirl}}$:** Planck-suppressed `eq:Fmax_planck_suppressed`, reduction guard `eq:canonical_gswirl_compton_reduction`, RT balance-angle diagnostic `sec:rt_compton_horn_balance_angle`. **Hybrid density-source Swirl-Clock benchmark** (`app:research_hybrid_density_source_swirl_clock`). |
| **v0.8.19** | **Canonization queue (01–06):** orthodox ropelength/thickness foundation (`subsec:orthodox_ropelength_thickness_convention`, `eq:canon_ropelength_rad`); derived thin-filament energy anchor (`eq:canon_thin_filament_energy_scale`); scalarized screening functional $E_{\rm screen}$ (`eq:research_track_IG_scalarization`, `eq:sst_screen_energy_research_track`); geometric mass density/dimensional audit (`eq:mass_equivalent_density_guard`, `eq:geometric_mass_exposure_branch`, `eq:mass_benchmark_tuple`); geometric impedance bridge (`sec:appendix_geometric_impedance_bridge`); stricter reintegration rules. **Audit bundle (in-place):** `[CALIBRATED]`/`[CONDITIONAL]` reading guide; unified `\SwirlClock(x,t)` with `\norm{\uswirl}` in `eq:swirl_clock` and Axiom 7; `\rhohorn`/`16\pi^2` F_max hygiene; Poisson–clock bridge (`eq:clock_potential_normalization`, `eq:poisson_clock_emg_identification`); EMG sector guards; trefoil precision; `eq:pure_geometric_mass_baseline_collapse`. **Foucault RT:** `subsec:rt_foucault_swirl_clock_probe`. **Projected swirl-vorticity frequency:** `eq:rt_projected_swirl_vorticity_frequency` + RMS/Swirl-Clock diagnostics. **Dark taxonomy + operator clock:** benchmark CSV schema; `eq:rt_dark_symmetry_metadata_vector`; `subsec:rt_operator_swirl_clock_visibility`. **Claude audit cleanup:** geometric impedance bridge demoted to RT (`sec:rt_geometric_impedance_bridge`); main appendix pointer guard; $T_{\rm core}$ free-symbol guard; `eq:nonabelian_extended_energy` aligned to $E_{\rm screen}$ notation. |

## Rebuild chain

```powershell
cd papers/SST-CANON/been_processed
python apply_v0819.py
```

Individual steps: `apply_v085.py` … `apply_v0819.py`.

Shared metadata: `canon_edition.py`. Patch blocks: `apply_framed_selflinking.py`, `apply_spinstats_z2.py`, `apply_spinstats_bibliography.py`, `apply_gemini_audit.py`.

## Build PDF

```powershell
cd papers/SST-CANON/been_processed/v0.8.19
latexmk -pdf -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.19.tex
```

Or manually (three passes):

```powershell
cd papers/SST-CANON/been_processed/v0.8.19
pdflatex -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.19.tex
pdflatex -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.19.tex
pdflatex -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.19.tex
```

Output: `v0.8.19/$out/SST_CANON-v0.8.19.pdf` (auxiliary files stay in `$out/`; source `.tex` files remain in the edition folder).
