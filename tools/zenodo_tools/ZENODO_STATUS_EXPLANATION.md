# Zenodo Status Explanation

## HAS_DOI_NOT_ONLINE Status

Files with `HAS_DOI_NOT_ONLINE` fall into two categories:

### 1. Drafts on Zenodo (4 files) - Status: `HAS_DOI_DRAFT`
These files have DOIs that exist as **draft deposits** on Zenodo (not yet published):

- **SST-13_Gravitational_Modulation\SST-13_Gravitational_Modulation.tex**
  - DOI: 10.5281/zenodo.17877038
  - Status: Draft on Zenodo
  - Action: Can be published when ready

- **SST-26_Neutrinos\SST-26_Neutrinos.tex**
  - DOI: 10.5281/zenodo.17877206
  - Status: Draft on Zenodo
  - Action: Can be published when ready

- **SST-27_Resonant_Topological_Vorticity\SST-27_Resonant_Topological_Vorticity_Confinement.tex**
  - DOI: 10.5281/zenodo.17877182
  - Status: Draft on Zenodo
  - Action: Can be published when ready

- **SST-28_Time_from_Swirl\SST-28_Time_from_Swirl.tex**
  - DOI: 10.5281/zenodo.17877012
  - Status: Draft on Zenodo
  - Action: Can be published when ready

### 2. Not Found on Zenodo (11 files) - Status: `HAS_DOI_NOT_ONLINE`
These files have DOIs in the LaTeX but the DOIs **don't exist** on Zenodo. They might be:
- Old/invalid DOIs
- Different versions that were replaced
- DOIs that were never actually created

Files:
- SST-01_Rosetta\VAM_SST_Rosetta.tex - DOI: 10.5281/zenodo.16980378
- SST-15_Circulation_Loop_Thermodynamics\SST-15_Thermodynamics_of_a_Circulation-Loop_Gas_in_an_Incompressible_Fluid_and_the_Classical_Ultraviolet_Problem.tex - DOI: 10.5281/zenodo.17629932
- SST-29_Kelvin_Mode_Suppression\SST-29_Suppression_of_Kelvin-Mode_Thermodynamics_in_Atomic_Orbitals_A_Gapped_Vortex-Filament_Resolution_in_Swirl-String_Theory.tex - DOI: 10.5281/zenodo.18012159
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.3.4.tex - DOI: 10.5281/zenodo.17014358
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.4.4.tex - DOI: 10.5281/zenodo.17101690
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.5.5.tex - DOI: 10.5281/zenodo.17052966
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.5.7.tex - DOI: 10.5281/zenodo.17101841
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.5.10_old.tex - DOI: 10.5281/zenodo.17155748
- SST-31_Canon\previous\Swirl-String-Theory_Canon-v0.5.11.tex - DOI: 10.5281/zenodo.17607006
- SST-31_Canon\Swirl-String-Theory_Canon-v0.7.5.tex - DOI: 10.5281/zenodo.17899592
- template\appendix_2.tex - DOI: 10.5281/zenodo.15566319

**Action for these:** Either:
1. Remove the invalid DOI from the LaTeX file, or
2. Create a new deposit on Zenodo and update the DOI

---

## NEEDS_DOI Status

Files with `NEEDS_DOI` are filtered to only include:
- ✅ Files with `\title` command (actual papers)
- ✅ Files with `\begin{document}` (standalone documents)
- ❌ Excludes cover letters (files with "coverletter" or "cover_letter" in filename)
- ❌ Excludes files without `\title` command

**Total: 82 files** need DOIs (down from 130 after filtering)

These are the files that should be uploaded to Zenodo to get DOIs.

---

## Summary Statistics

- **Files ALREADY ONLINE:** 25 (matched with published Zenodo deposits)
- **Files with DOI (DRAFTS):** 4 (exist as drafts on Zenodo)
- **Files with DOI (NOT FOUND):** 11 (DOIs don't exist on Zenodo)
- **Files NEEDING DOI:** 82 (need to be uploaded)

---

## Files Created

- `zenodo_comparison.csv` - Complete comparison with status codes:
  - `ONLINE` - Published on Zenodo
  - `HAS_DOI_DRAFT` - Draft on Zenodo
  - `HAS_DOI_NOT_ONLINE` - DOI not found on Zenodo
  - `NEEDS_DOI` - Needs to be uploaded (filtered: has `\title`, excludes cover letters)

Run `python compare_local_zenodo.py` to regenerate this analysis.
