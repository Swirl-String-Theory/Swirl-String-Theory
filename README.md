# 🌌 Swirl–String Theory (SST)

Canonical repository for **Swirl–String Theory (SST)**: a research program exploring how **fluid-like kinematics**, **topology**, and **field-theoretic structure** might co-organize into particle spectra, clocks, and interactions.

SST is historically continuous with earlier internal drafts labeled *Vortex Æther Model (VAM)*, but this repo uses **SST** as the public-facing name and notation.

> If spacetime can bend, why shouldn’t it knot?

---

## 🔗 Reproducible notebooks (Google Colab)

These are executable “proof notebooks” used to reproduce core calculations and cross-checks:

- **Invariant atom mass from knots**  
  https://colab.research.google.com/drive/14IzdlPc_I_pfavO901TTgycSm_kuPed-?usp=drive_link

- **General Relativity comparisons / benchmarks**  
  https://colab.research.google.com/drive/1jDTTO9eBmuBjCTqenZmj_Ualwfha1Y2N?usp=drive_link

- **Thermodynamics / scaling derivations**  
  https://colab.research.google.com/drive/15gIl0Eqp_Pnh-xn3qGKxnwi9J3JB8oy0?usp=drive_link

- **Misc / work-in-progress notebook**  
  https://colab.research.google.com/drive/1_SFxUWF0mKfta4Id49WPhbVx_3RZZfcH?usp=drive_link

---
[tinyurl.com/SwirlString Drive with referenced sources and more](https://tinyurl.com/SwirlString)

## 📌 What’s in this repo

### 📄 Papers (`/papers`)
Peer-style manuscripts and appendices (typically `.tex` + compiled `.pdf`).

Topics include:
- swirl-clock time scaling and relational time constructions
- fluid-kinematic reformulations of bound-state structure
- topological / geometric mass models
- bridge papers connecting orthodox many-body physics to SST-style structure

### 💻 Code (`/code` or `/src`)
Python tools and scripts for:
- knot helicity / chirality classification
- mass prediction and benchmarking sweeps
- Biot–Savart-style filament simulations (where used)
- equation extraction / processing from source formats

### 📊 Data (`/data`)
Raw tables and derived results (CSV + outputs), intended to be reproducible from code + notebooks.

---

## 🚀 Quickstart (local)

> If you don’t have a unified `requirements.txt` yet, this section is a template—drop in the real commands once the repo layout stabilizes.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python -m pytest   # if tests exist
```

## 📦 Releases & citation

Finalized papers are archived on Zenodo with DOIs for citation stability.
GitHub releases should match Zenodo records (same version tag).

---

## ⚙️ Tools & Workflow

- Python scripts for **helcity & mass evaluation** (`HelicityCalculationVAMcore.py`, `SST_INVARIANT_MASS*.py`)
- Equation harvesting from `.fseries` source (thanks to [David Fremlin’s knot library](https://david.fremlin.de/knots/index.htm))
- Planned: visualization notebooks for swirl clocks, vortex lensing, and knotted fields.

---

## 🧭 Why This Project?

SST aims to replace arbitrary particle physics “free parameters” with **geometric/topological invariants of swirl strings**.  
Highlights:
- No Yukawas: fermion masses emerge from knot energies.
- Gauge couplings as swirl mixing angles.
- Gravity as structured swirl dynamics, not curvature.
- Time as vortex phase, with a shared **ætheric Now**.

---

## 🔬 Author

**Omar Iskandarani**  
ORCID: [0009-0006-1686-3961](https://orcid.org/0009-0006-1686-3961)

Conceived, written, and (sometimes reluctantly) coded.

---

## ⚠️ Disclaimer

This project may induce:
- spontaneous fluid metaphors,
- academic eye-rolling,
- or a temptation to build copper pyramids with Rodin coils.

Proceed responsibly.

---

## 📬 Feedback

- Open an [issue](https://github.com/swirl-string-theory/swirl-string-theory/issues)
- Fork, remix, or test the Python harnesses
- Or send your critiques directly into the æther.  
  It’s always listening.

---

## License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)  
© 2025 Omar Iskandarani.  
Educational and research use welcome. Commercial reuse requires permission.



## Evaluation Table

| Paper                                                              | SLV | TRC | NWO | CPR | FCP | ES | RC | PEC | Total | Role                    | Venue                    | Submission Status              |
|--------------------------------------------------------------------|----:|----:|----:|----:|----:|---:|---:|----:|------:|-------------------------|--------------------------|--------------------------------|
| SST-67 Variational Quantization                                    |   5 |   4 |   4 |   4 |   4 |  4 |  5 |   4 |    34 | Anchor / Bridge-Anchor  | Physical Review Research | progress                       |
| SST-66 Relational Time and Intrinsic Temporal Stochasticity        |   4 |   4 |   5 |   4 |   3 |  3 |  3 |   3 |    29 | Bridge                  |                          |                                |
| SST-65 Foliation in Mass Equation                                  |   4 |   4 |   4 |   5 |   3 |  3 |  4 |   4 |    31 | Bridge                  |                          |                                |
| SST-64 Covariant                                                   |   5 |   4 |   4 |   5 |   3 |  4 |  4 |   3 |    32 | Bridge                  |                          |                                |
| SST-63 Holograpic                                                  |   4 |   4 |   5 |   5 |   2 |  2 |  3 |   3 |    28 | Bridge                  |                          |                                |
| SST-62 SR GR ARE ONE                                               |   3 |   4 |   3 |   4 |   3 |  3 |  4 |   4 |    28 | Support                 |                          |                                |
| SST-61 Topological Stabilization Ideal Flows                       |   5 |   5 |   4 |   4 |   3 |  5 |  5 |   4 |    35 | Anchor                  |                          |                                |
| SST-60 Swirl-Clock Phase Locking                                   |   5 |   5 |   4 |   5 |   4 |  5 |  5 |   5 |    38 | Anchor                  | EPJP                     |                                |
| SST-59 Atomic Masses from Topological Invariants                   |   4 |   4 |   4 |   5 |   3 |  3 |  4 |   4 |    34 | Bridge                  | JPhysA                   | rejected                       |
| SST-58 vacuum stress energy engineering                            |   4 |   4 |   4 |   3 |   4 |  4 |  4 |   4 |    31 | Bridge                  |                          |                                |
| SST-57 FermionMasses                                               |   3 |   4 |   3 |   3 |   3 |  4 |  5 |   4 |    29 | Support                 |                          |                                |
| SST-56 superfluid                                                  |   5 |   4 |   4 |   3 |   3 |  4 |  5 |   4 |    32 | Bridge                  |                          |                                |
| SST-55 Delay-Induced mode selection Circulating Feedback Systems   |   4 |   4 |   4 |   4 |   3 |  3 |  4 |   4 |    30 | Bridge                  | CHAOS → AIP-A            | TR                             |
| SST-54 Delay-Induced mode discreteness nonlinear ring systems      |   4 |   4 |   4 |   4 |   4 |  4 |  4 |   4 |    32 | Bridge / Constraint     | CHAOS → AIP-A            | TR                             |
| SST-53 Thermodynamic Origin of Quantization                        |   4 |   4 |   4 |   4 |   3 |  3 |  3 |   4 |    29 | Bridge                  |                          |                                |
| SST-52 Kelvin Mode Suppression Gap                                 |   5 |   4 |   4 |   4 |   5 |  4 |  4 |   4 |    34 | Anchor/Constraint       | FoP                      | rejected                       |
| SST-51 Variational Electron Magnetic Moment                        |   3 |   3 |   3 |   3 |   2 |  2 |  3 |   3 |    22 | Support (high-risk)     |                          |                                |
| SST-50 Emergent Equivalence Principle                              |   4 |   3 |   3 |   4 |   2 |  3 |  4 |   4 |    27 | Bridge/Support          | FoP                      | rejected                       |
| SST-49 Emergent InverseSquare Derivations                          |   4 |   4 |   4 |   4 |   4 |  4 |  4 |   4 |    32 | Anchor/Bridge           |                          |                                |
| SST-48 Emergent InverseSquare Law                                  |   4 |   4 |   4 |   4 |   3 |  3 |  3 |   3 |    28 | Support/Bridge          |                          |                                |
| SST-47 Emergent InverseSquare Followup                             |   4 |   4 |   4 |   4 |   4 |  4 |  4 |   4 |    32 | Bridge (redundant)      |                          |                                |
| SST-46 Relational Time of Arrival                                  |   4 |   4 |   4 |   4 |   3 |  4 |  4 |   4 |    31 | Bridge                  | FoP                      | rejected                       |
| SST-45 Golden Rapidity                                             |   3 |   5 |   2 |   2 |   1 |  4 |  5 |   5 |    27 | Auxiliary               |                          |                                |
| SST-44 Canonical Fluid Reformulation                               |   3 |   3 |   4 |   5 |   2 |  2 |  2 |   3 |    24 | Capstone                |                          |                                |
| SST-43 Magnetic Vector                                             |   5 |   5 |   2 |   5 |   3 |  5 |  5 |   4 |    34 | Anchor (Infrastructure) |                          |                                |
| SST-42 Spiraling Light                                             |   4 |   3 |   3 |   3 |   2 |  4 |  4 |   4 |    27 | Support                 |                          |                                |
| SST-41 Water and time                                              |   4 |   5 |   3 |   3 |   3 |  4 |  4 |   5 |    31 | Bridge                  |                          |                                |
| SST-40 Photons and Lazers                                          |   4 |   4 |   2 |   3 |   2 |  5 |  5 |   5 |    30 | Support                 |                          |                                |
| SST-39 Giant Jets and Sprites                                      |   3 |   4 |   2 |   3 |   2 |  2 |  3 |   4 |    23 | Support                 |                          |                                |
| SST-38 Calculate-Knot-Helicity                                     |   5 |   4 |   2 |   5 |   3 |  4 |  5 |   4 |    32 | Anchor (Infrastructure) |                          |                                |
| SST-37 Attosecond-TimeDilation                                     |   4 |   3 |   4 |   3 |   4 |  2 |  3 |   4 |    27 | Support                 |                          |                                |
| SST-36 Wave-Particle Duality                                       |   4 |   4 |   4 |   4 |   3 |  3 |  3 |   4 |    29 | Bridge                  |                          |                                |
| SST-35 Resonance-matched-excitation                                |   5 |   5 |   3 |   5 |   4 |  5 |  5 |   5 |    37 | Anchor (Methods)        |                          |                                |
| SST-34 Hydrogen-Gravity                                            |   4 |   4 |   3 |   4 |   4 |  3 |  4 |   3 |    29 | Bridge/Constraint       |                          |                                |
| SST-34 Thermodynamics (two-scale swelling)                         |   3 |   3 |   3 |   4 |   2 |  1 |  2 |   3 |    21 | Internal / Support      |                          |                                |
| SST-33 Heat Transport                                              |   5 |   4 |   4 |   4 |   4 |  4 |  3 |   4 |    32 | Anchor/Bridge           | Physical Review B        | Not under active consideration |
| SST-32 Canonical Fluid Reformulation                               |   4 |   3 |   4 |   5 |   3 |  2 |  2 |   3 |    26 | Capstone                | frontiersin              | rejected                       |
| SST-31 Canon                                                       |   2 |   3 |   3 |   5 |   2 |  1 |  1 |   3 |    20 | Internal Canon          |                          |                                |
| SST-30 Invariant Atom Masses                                       |   4 |   4 |   3 |   5 |   3 |  4 |  4 |   4 |    31 | Bridge                  |                          |                                |
| SST-29 Kelvin Mode Suppression                                     |   4 |   5 |   4 |   4 |   4 |  4 |  4 |   4 |    33 | Anchor/Constraint       |                          |                                |
| SST-28 Time from Swirl                                             |   4 |   4 |   5 |   5 |   2 |  3 |  3 |   4 |    30 | Bridge/Foundation       |                          |                                |
| SST-27 Resonant Topological Vorticity                              |   3 |   4 |   4 |   2 |   4 |  1 |  2 |   4 |    24 | Internal/Applied        |                          |                                |
| SST-26 Neutrinos                                                   |   2 |   3 |   4 |   3 |   2 |  1 |  2 |   3 |    20 | Internal/High-risk      |                          |                                |
| SST-25 Hydrogenic Orbitals                                         |   4 |   4 |   4 |   5 |   2 |  3 |  2 |   3 |    27 | Support                 |                          |                                |
| SST-24 Thermodynamics                                              |   5 |   5 |   4 |   5 |   4 |  4 |  4 |   4 |    35 | Anchor                  |                          |                                |
| SST-23 Dual Vacuum Unification                                     |   4 |   4 |   5 |   5 |   3 |  3 |  4 |   5 |    33 | Anchor/Bridge           |                          |                                |
| SST-22 Hydrodynamic Origin Hydrogen Old                            |   4 |   5 |   3 |   5 |   3 |  3 |  4 |   5 |    32 | Bridge / Reference      | FoP                      | rejected                       |
| SST-21 Knot Taxonomy                                               |   4 |   5 |   4 |   5 |   3 |  3 |  4 |   4 |    32 | Anchor (Infrastructure) |                          |                                |
| SST-20 Short Hydrodynamic Origin                                   |   5 |   4 |   4 |   5 |   3 |  4 |  4 |   4 |    33 | Bridge / Mini-Anchor    |                          |                                |
| SST-19 Hydrodynamic Origin Hydrogen                                |   4 |   4 |   4 |   5 |   3 |  2 |  3 |   3 |    28 | Capstone / Bridge       | FoP                      | rejected                       |
| SST-18 Unifying EM Gravity                                         |   3 |   3 |   4 |   5 |   2 |  2 |  3 |   4 |    26 | Capstone / Bridge       |                          |                                |
| SST-17 Photon Torsion Wave                                         |   5 |   4 |   4 |   4 |   4 |  3 |  4 |   4 |    32 | Bridge                  | FoP VAM -> SST FoP       | rejected, rejected             |
| SST-16 Non Thermal Field Coupling                                  |   3 |   3 |   4 |   4 |   3 |  2 |  2 |   3 |    24 | Internal / Research     |                          |                                |
| SST-15 Circulation Loop Thermodynamics                             |   5 |   5 |   4 |   4 |   4 |  5 |  5 |   4 |    36 | Anchor                  |                          |                                |
| SST-14 Gravitational Behavior                                      |   3 |   3 |   3 |   3 |   4 |  1 |  2 |   4 |    23 | Internal                |                          |                                |
| SST-13 Gravitational Modulation                                    |   3 |   3 |   4 |   3 |   2 |  2 |  3 |   3 |    23 | Support / High-risk     |                          |                                |
| SST-12 Swirl Pressure Gravitational Acceleration                   |   4 |   4 |   3 |   4 |   3 |  3 |  4 |   4 |    29 | Bridge                  |                          |                                |
| SST-11 Water and Time                                              |   3 |   5 |   2 |   5 |   4 |  2 |  5 |   5 |    31 | Bridge                  |                          |                                |
| SST-10 Impulsive Axisymmetric Forcing                              |   5 |   5 |   3 |   4 |   5 |  4 |  5 |   4 |    35 | Anchor                  |                          |                                |
| SST-09 Energy Impulse Stability                                    |   5 |   5 |   3 |   5 |   4 |  5 |  5 |   4 |    36 | Anchor                  |                          |                                |
| SST-08 Circulation Rigid Rotation                                  |   4 |   4 |   4 |   5 |   3 |  4 |  4 |   4 |    32 | Bridge                  |                          |                                |
| SST-07 Rotational Kinetic Energy                                   |   5 |   5 |   3 |   5 |   4 |  5 |  5 |   5 |    37 | Anchor                  |                          |                                |
| SST-06 Classical Electron Radius                                   |   4 |   4 |   4 |   5 |   3 |  4 |  4 |   4 |    32 | Bridge                  | FoP ---> EPJP            | rejected, consideration        |
| SST-05 Einstein to SST                                             |   4 |   3 |   3 |   4 |   2 |  3 |  4 |   4 |    27 | Bridge                  | FoP Entropy              | rejected, rejected             |
| SST-04 Cosmologie                                                  |   2 |   2 |   3 |   4 |   1 |  1 |  2 |   3 |    18 | Internal                |                          |                                |
| SST-03 Physics Anomalies                                           |   3 |   2 |   3 |   4 |   2 |  1 |  2 |   2 |    19 | Internal                |                          |                                |
| SST-02 Knot Classified                                             |   3 |   2 |   4 |   5 |   2 |  2 |  3 |   3 |    24 | Infrastructure          |                          |                                |
| SST-01 Rosetta                                                     |   5 |   5 |   3 |   5 |   3 |  5 |  5 |   5 |    36 | Anchor                  |                          |                                |
| SST-00 Lagrangian                                                  |   4 |   4 |   5 |   5 |   4 |  3 |  4 |   3 |    32 | Capstone                |                          |                                |


---


## Scoring Dimensions (0–5 each)

**A. Structural Lemma Value (SLV)**
Standalone usefulness if SST context is removed.

**B. Technical Rigor & Closure (TRC)**
Mathematical closure, dimensional consistency, completeness.

**C. Novelty without Ontology (NWO)**
New mechanism or constraint independent of metaphysical claims.

**D. Cross‑Paper Reusability (CPR)**
How often this paper supports or is cited by other SST work.

**E. Falsifiability / Constraint Power (FCP)**
Clear bounds, exclusions, or testable predictions.

**F. Editorial Survivability (ES)**
Likelihood of being sent to review by a mainstream editor.

**G. Rewrite Cost (RC)**
Ease of translating to fully orthodox language.

**H. Pedagogical Equation Clarity (PEC)**
How clearly equations are motivated, introduced, and interpreted.


## Role Labels

* **Anchor** – safest, high‑leverage orthodox lemma
* **Bridge** – connects domains or prepares capstones
* **Capstone** – synthesis / foundation paper
* **Support** – necessary but not a lead submission
* **Internal** – research / development only

---