<!-- fe68721d-d4ed-4ce4-8418-82ab11178d0c 365ad6ff-84b7-47e7-9ff2-9297fb47a2f3 -->
# Restructure SST Canon v0.5.11 → v0.5.12

## Overview

Transform the document from a linear structure to a tight "Canon spine" with clearly marked modules and appendices. All content will be preserved but reorganized according to the user's detailed analysis.

## Current Structure Analysis

The document currently has:

- Main sections (1-50+) in linear order
- Appendices starting at line 2958
- Mixed canonical/research/empirical content throughout

## New Structure: Part I-IV + Reorganized Appendices

### Part I – Foundations (Core Canon Spine)

1. **Preface: Reader Pathways** (keep as-is, line ~193)
2. **Sevenfold Genesis of the Swirling Cosmos** (keep, add explicit cross-references to technical sections, line ~209)
3. **Core Axioms (SST)** (keep, line ~429)
4. **Canon Governance and Status Taxonomy** (keep, compress knot taxonomy figure reference, line ~351)
5. **Classical Invariants: Chronos–Kelvin and Clock–Radius Transport** (keep, line ~1052)
6. **Classical Invariants and Swirl Quantization** (keep, line ~1079)
7. **Canonical Constants and Effective Densities** (keep, line ~1118)
8. **Effective Medium: Coarse-Graining Derivation of $\rho_f$** (keep, line ~1248)
9. **Historical Context** (NEW: compress "Historical and Conceptual Evolution" section ~943 to 1-2 paragraphs)

### Part II – Geometry, Fields, and Lagrangian

10. **Formal Structure and Canonical Framework** (keep, line ~505)
11. **Genus-2 Foliation and Topological Compactification** (keep, possibly shorten, line ~1265)
12. **Knot Taxonomy** (move figure from governance section here, reference line ~425)
13. **The Swirl–Electromagnetic Bridge** (keep, line ~1342)
14. **Swirl–EM Emergence** (keep, line ~1384)
15. **Unified SST Lagrangian** (keep, add "Canonical Hamiltonian Density" subsection promoting content from appendix, line ~1592)
16. **Master Equations and Canonical Relations** (keep, line ~1609)

### Part III – Gravity, Hydrogen, and Cosmology

17. **Swirl Gravitation and the Hydrogen–Gravity Mechanism** (keep, line ~2169)
18. **Hydrogen Master Equations** (keep soft-core + Bohr recovery summary, detailed derivation stays in appendices, line ~1796)
19. **Cosmological Term and Three-Swirl Circulation Law** (combine sections ~2630 and ~2719, keep compact)
20. **Invariant Mass from the Canonical Lagrangian + Benchmark Table** (PROMOTE from appendix ~3825 to main text, keep derivation details in appendix)
21. **Derivations and Numerical Benchmarks** (keep, line ~2859)
22. **Systematic Dimensional & Recovery Checks** (keep, line ~2929)
23. **Canonical Status and Outlook** (keep, line ~2947)

### Part IV – Modules and Applications (Research Track)

24. **Symmetry and Dark-Knot Classification** (compact version, keep definition + rule, move details to appendix, line ~761)
25. **Engineered Bulk Signaling Channel (BASC)** (brief summary, point to appendix, line ~1523)
26. **Swirl Pressure Law (Euler Corollary)** (brief summary, point to appendix, line ~2024)
27. **Canonical Closure for the Gamma Coil** (brief summary, point to appendix, line ~2040)
28. **Quantum Measurement: Kernel Law + Near-Field Corollary** (keep kernel law, move bounds to appendix, line ~2189)
29. **Quantum Computing Sector** (1-2 page preview, compress from line ~2217)
30. **SST Unruh Scaling and Two-Vacuum Structure** (1-2 page summary, compress sections ~4517 and ~4560)

### Appendices (Reorganized)

- **Appendix A**: Swirl Hamiltonian Density (full derivation, line ~3604)
- **Appendix B**: Swirl Coulomb Potential Derivation (line ~3007)
- **Appendix C**: Hydrogen Soft-Core Numerics (line ~3652)
- **Appendix D**: Photon/Unknot Sector Details (line ~3671)
- **Appendix E**: Swirl Pressure Law—Galaxy-Scale Integrals (line ~3685)
- **Appendix F**: Calibration Protocol Notes and Experimental Status (combine ~3700, ~3710, move Kairos bifurcations and TB/NR protocols from main text)
- **Appendix G**: Knot Stability and Protection (full detail, line ~4123)
- **Appendix H**: Hyperbolic Volume Computation Pipeline (compress ~4379 to 1-2 paragraphs, move full details here)
- **Appendix I**: Rosetta→Code Consistency Rules (compress ~4471 to 1-2 paragraphs, move full details here)
- **Appendix J**: Derivation of the Swirl→Bulk Coupling $\mathcal{G}$ / $G_{\text{swirl}}$ (line ~4000)
- **Appendix K**: Quantum/Unruh Technical Derivations (detailed equations from sections ~4517, ~4560)
- **Appendix L**: Conversation-Derived Insights (optional, line ~4012)
- **Appendix M**: Historical and Conceptual Evolution (full VAM timeline, moved from main text ~943)
- **Appendix N**: Golden Principle and Discrete Layering (move from main text if needed, line ~571)
- **Appendix O**: Self-Similarity and Stability (move from main text if needed, line ~520)

## Implementation Steps

### Step 1: Create New Document Structure

- Update version number from v0.5.11 to v0.5.12
- Add `\part{}` commands to organize into Part I-IV
- Reorder sections according to new structure

### Step 2: Compress/Move Sections

- Compress "Historical and Conceptual Evolution" to 1-2 paragraphs in Part I
- Move extended VAM timeline to Appendix M
- Compress "Kairos Bifurcations" and experimental protocols to Appendix F
- Compress "Symmetry and Dark-Knot Classification" details, move full content to Appendix G
- Compress BASC, Gamma Coil, Swirl Pressure Law to brief summaries with appendix pointers
- Compress Quantum Computing Sector to 1-2 page preview
- Compress Unruh sections to 1-2 page summary
- Compress Hyperbolic Volume and Rosetta→Code sections to 1-2 paragraphs with appendix pointers

### Step 3: Promote Appendix Content

- Add "Canonical Hamiltonian Density" subsection to "Unified SST Lagrangian" section, referencing Appendix A
- Move "Invariant Mass from the Canonical Lagrangian" + benchmark table to Part III (after "Emergent Gauge Fields")
- Add boxed $G_{\text{swirl}}$ identity to "Swirl Gravitation" section, referencing Appendix J

### Step 4: Update Cross-References

- Update all `\ref{}` commands to point to new section locations
- Update all `\label{}` commands if section numbers change
- Ensure appendix references use new appendix letters (A, B, C, etc.)

### Step 5: Add Explicit Cross-References

- In "Sevenfold Genesis", add explicit pointers to technical sections (e.g., "Stage 2 → Section X")
- In "Canon Governance", move knot taxonomy figure reference to Part II
- Add cross-references between promoted content and their detailed appendices

### Step 6: Verify Document Structure

- Ensure all sections are properly numbered
- Verify all appendices are properly labeled A, B, C, etc.
- Check that no content is lost in the reorganization
- Verify LaTeX compilation will work with new structure

## Files to Modify

- `SwirlStringTheory/SST-01-Canon/Swirl-String-Theory_Canon-v0.5.11.tex` → Create new file `Swirl-String-Theory_Canon-v0.5.12.tex`

## Key Considerations

- Preserve all existing content (move/compress, don't delete)
- Maintain all mathematical equations and formulas
- Keep all status tags (Canonical/Research/Empirical)
- Update version number throughout document
- Ensure cross-references remain valid
- Maintain document compilation integrity

### To-dos

- [ ] Update version number from v0.5.11 to v0.5.12 in document header and title
- [ ] Add \part{} commands to organize document into Part I (Foundations), Part II (Geometry/Fields/Lagrangian), Part III (Gravity/Hydrogen/Cosmology), Part IV (Modules/Applications)
- [ ] Reorder Part I sections: Preface, Sevenfold Genesis (add cross-refs), Core Axioms, Canon Governance (compress), Classical Invariants, Quantization, Constants, Effective Medium, Historical Context (compressed)
- [ ] Reorder Part II sections: Formal Structure, Genus-2 Foliation, Knot Taxonomy (move figure), Swirl-EM Bridge, Swirl-EM Emergence, Unified Lagrangian (add Hamiltonian subsection), Master Equations
- [ ] Reorder Part III sections: Swirl Gravitation (add G_swirl box), Hydrogen Master Equations, Cosmological Term, Invariant Mass (promote from appendix), Benchmarks, Dimensional Checks, Status/Outlook
- [ ] Create Part IV with compressed modules: Symmetry/Dark-Knots (compact), BASC (summary), Gamma Coil (summary), Quantum Measurement (kernel law only), Quantum Computing (preview), Unruh (summary)
- [ ] Reorganize appendices: A (Hamiltonian), B (Coulomb), C (Hydrogen), D (Photon), E (Pressure), F (Calibrations/Experimental), G (Knot Stability), H (Hyperbolic Volume), I (Rosetta), J (G_swirl), K (Unruh), L (Conversations), M (History), etc.
- [ ] Compress: Historical Evolution (to 1-2 paras), Kairos/Protocols (to appendix), Dark-Knot details (to appendix), BASC/Gamma/Pressure (to summaries), QC Sector (to preview), Unruh (to summary), Hyperbolic/Rosetta (to 1-2 paras)
- [ ] Promote: Add Hamiltonian subsection to Lagrangian section, Move Invariant Mass + benchmarks to Part III, Add G_swirl box to Gravity section
- [ ] Update all \ref{} and \label{} commands to reflect new section locations and appendix letters
- [ ] Add explicit cross-references: Sevenfold Genesis → technical sections, Canon Governance → knot figure location, promoted content → detailed appendices
- [ ] Verify document structure: check section numbering, appendix labeling, no lost content, LaTeX compilation integrity