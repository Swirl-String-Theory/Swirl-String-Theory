# Source → canon integration index

| Source file | Integrated in | Location in canon |
|-------------|---------------|-------------------|
| `em_gravity_canon_block.tex` | **v0.8.4** | Main: `\ref{subsec:canonical_em_gravity_closure}` |
| `finite_cell_obstruction.tex` | **v0.8.4** | Main: `\ref{subsec:finite_cell_alpha_obstruction}` |
| `canon_rhorn_omega_c_correction_block.tex` | **v0.8.2** | `\ref{subsec:derived_horn_circulation_radius}` |
| `canon_blocks_from_current_conversation.tex` | **v0.8.2–v0.8.3** | Horn density, framed-tube, particle table |
| `research_track_blocks_from_current_conversation.tex` | **v0.8.4** | Research-track after particle mapping |
| Highres audit `.tex` / `.diff` | **v0.8.5** | Euler discipline, R-to-T bookkeeping, twist-ladder RT |
| `apply_calibrated_audit.py` | **v0.8.5** | `[CALIBRATED]` / epistemic taxonomy |
| `framed_selflinking_spinorial_block.tex` | **v0.8.6** | `\ref{subsec:framed_selflinking_spinorial}` |
| `spinstats_z2_sector_block.tex` | **v0.8.7** | Z₂ / θ=π paragraph in framed-selflinking subsection |
| `spinstats_bibliography_block.tex` | **v0.8.7** | WilczekZee, Volovik, Autti, ChenTanizaki bibitems |
| `SST_CANON_v0.8.5_Gemini_audit_patch.diff` | **v0.8.8** | Primitive calibration notation, conditional labels, Pauli cutoff |
| `SST_CANON-v0.8.5-triadic-gravity-response.diff` | **v0.8.9** | Main: `\ref{subsec:triadic_gravity_response_corollary}`; RT diagnostics |
| `SST_CANON_v0.8.9_Gemini_round2_patch.diff` | **v0.8.10** | `\vchar`/`uswirl` notation, delay sign, CALIBRATED IDENTITY |
| `SST_CANON_v0.8.10_final_hygiene_patch.diff` | **v0.8.11** | Residual `\vswirl`→`\vchar`/`\uswirl` cleanup, EMG numerics, RT bridges |
| `SST_CANON_v0.8.11_Gemini_round3_epistemic_patch.diff` | **v0.8.12** | Identity relabels, Pauli `a_{\rm cut}`, coarse-grain caveat, galaxy-scale $\rhoF$ note (distinct from evidence-pack 0004/0005) |
| `SST_CANON_v0.8.12_relativity_emergence_conversation.md` | **v0.8.13** | Main: `\ref{subsec:tensor_speed_naturalness}`; RT: `\ref{sec:rt_relativity_emergence_ladder}` + relativity bib |
| `SST_v0.8.12_core_torsion_canon_patch.diff` | **v0.8.14** | Main: `\ref{subsec:two_speed_clock_discipline}` + α-gate guard; RT: `\ref{sec:rt_core_torsion_impedance_matching}` |
| `SST_v0.8.14_lorentz_swirl_stress_patch.md` | **v0.8.15** | Main: `\ref{sec:lorentz_type_force_density_as_swirl_stress}`; RT: `\ref{sec:research_em_to_swirl_force_density_correspondence}` |
| `SST_v0.8.15_conversation_audit_and_patch.md` + `patch_blocks_v0_8_15.tex` | **v0.8.16** | Patch A: `\ref{eq:canonical_pressure_optical_locking}`; Patch B: `\ref{sec:rt_no_monopole_transport_stress_audit}`; Patch C: SST-73 |
| `verify_pressure_optical_locking.py` | **v0.8.16** | Numerical check for pressure–optical locking constants |
| `sst_v0_8_16_patch_bundle/` + `patch_canon.txt` | **v0.8.17** | T-foliation remark; Route-I SST-63/23/56; ropelength convention; SST-73/63/64/34 corpus notes |
| `0004-spoorAB-main-canon-notes.patch` | **v0.8.17** (in-place) | ζ(3) generic calculus; γ α-suppressed; Madelung ρ_ψ incompressibility note |
| `0005-spoorAB-research-track-notes.patch` | **v0.8.17** RT (in-place) | Galactic dp/dr falsifier; Cooper-pair calibrated input; V_horn envelope normalization |
| `sst_canon_v0.8.17_guardrails_v2.patch` | **v0.8.18** | Calibration guards, kernel normalization, EM prefactor, $\rhohorn$ baseline, RT falsifier bounds |
| `sst_canon_v0.8.17_guardrails_v2_to_v3_resolved_tube.patch` | **v0.8.18** (after v2) | Resolved-tube reach/thickness; `app:resolved_tube_contact_stress_geometry` |
| `v0.8.18_four_insights_audit.patch` | **v0.8.18** (in-place) | Four topology/stability appendices audit; $Q_8$ benchmark; bib cites (Annala, Kleckner, Pisanty, Ricca) |
| `v0.8.18_four_insights_audit_v2.patch` | **v0.8.18** (in-place, after v1) | Knot-energy normal form; $E/E_0$ + $\alpha_C/L/H$ + $I_G$ scalarization |
| `0002-v0818-golden-layer-hyperbolic-rapidity.patch` | **v0.8.18** (in-place) | Main: `eq:golden_layer_rapidity_*`; RT: `eq:rt_golden_layer_*`, transfer matrix |
| `0001-v0818-euler-probe-transport-polish.patch` | **v0.8.18** (in-place) | Magnus guardrail; `eq:rt_*_transport`; Zhang bib; dimensional/axis subsecs |
| `0001-v0818-compton-horn-gswirl-balance-angle.patch` | **v0.8.18** (in-place) | `eq:Fmax_planck_suppressed`; `eq:canonical_gswirl_compton_reduction`; `sec:rt_compton_horn_balance_angle` |
| `hybrid_density_source_swirl_clock.patch` | **v0.8.18** RT (in-place) | `app:research_hybrid_density_source_swirl_clock`; hybrid $\mu/G/M$ interpolation |
| *(in-place)* | **v0.8.18** | Canonical time ontology (`subsec:canonical_time_ontology`); $\tau_{\rm circ}$ / $\tau_A$ policy |
| `apply_v085.py` … `apply_v0818.py` | **v0.8.5–v0.8.18** | Reproducible incremental build |

## SST v0.8.12 evidence-pack patch status

| Patch | Integrated in | Verification |
|-------|---------------|--------------|
| `0001`–`0003` / `sstcore_v0_8_12_alignment_ALL.patch` | **SSTcore** (live) | `SSTcore/tests/test_canon_v0_8_12_alignment.py` |
| `0004-spoorAB-main-canon-notes.patch` | **v0.8.17** main canon | grep: `generic calculus property`, `alpha-suppressed`, `Madelung amplitude does not violate` |
| `0005-spoorAB-research-track-notes.patch` | **v0.8.17** research track | grep: `Cooper-pair description`, `stiffness theorem`, `2.8\\times10^{3}` |
| `0006-sweep-v10_3-robustness-fixes.patch` | **SST-Workbench** `experiments/trefoil/closure/sstcore/` | BS-scan guards, fp64 opt-in |
| `0007-gui-v9_3-bs-scan-guard.patch` | **SST-Workbench** trefoil GUI | `a_lo>=a_hi` degeneracy guard |
| `0008` + `ideal_source.py` | **SST-Workbench** both `gui_tabs/` copies | grep: `resolve_ideal_txt`, `relax=False`; AB `3:1:1` e2e test |

## Additional sources (moved from `papers/SST-CANON/` root)

| Source file / folder | Role |
|----------------------|------|
| `PATCH_MANIFEST.md` | v0.8.16 patch bundle index and merge order |
| `patch_canon.txt` | Canon patch notes |
| `core_torsion_impedance_research_track.tex` | Original core–torsion RT block (integrated v0.8.14) |
| `finite_cell_obstruction.tex` / `.pdf` | Finite-cell α obstruction source |
| `SST_v0_8_12_evidence_pack/` | v0.8.12 audit patches, scripts, results |
| `sst_v0_8_12_audit_cleanup.patch` | v0.8.12 cleanup patch |
| `SST_v0.8.12_claim_traceability_overview.md` | Claim traceability audit |
| `sst_v0_8_12_verification_suite.py` | Verification suite (also in evidence pack) |
| `reproduce_pauli_barrier.py`, `reproduce_em_qed_normalization.py`, `fit_galactic_swirl_rotation_sparc.py` | Repro scripts |
| `SST_Canon_v0.8.12_Evidence_Bundle.zip`, `sst_v0_8_16_patch_bundle.zip` | Archived bundles |
| `0008-generate-fseries-ideal-source-and-relax-off.patch` | fseries tooling patch |
