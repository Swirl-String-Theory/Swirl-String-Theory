# Canonization Plan — Dark Sector / Galactic Program

## Language and Source Override Policy
This policy overrides all earlier salvage notes.

### Non-negotiable canon-writing rule
Final canon text may use:
- **SST language only**,
- **orthodox scientific language only** when stating general physics or mathematics,
- and only terminology compatible with **Canon v0.7+ and later**.

Final canon text may **not** use:
- VAM-era wording,
- VAM ontology labels,
- old æther-era rhetorical framing,
- or any phrasing that does not already fit the SST v0.7+ style.

### Interpretation rule for older sources
Older sources may be used only as:
- internal historical prompts,
- equation seeds,
- topology hints,
- benchmark patterns,
- or falsification ideas.

They must never be imported textually. Any retained content must be fully rewritten as:
1. **orthodox statement**,
2. **SST-native statement**,
3. explicit status label,
4. benchmark / falsifier path.

### Practical filter
Use this filter for all pre-v0.7 or VAM-era material:
\[
	ext{old source}
	o
	ext{extract bare idea only}
	o
	ext{rewrite in orthodox language}
	o
	ext{rewrite in SST v0.7+ language}
	o
	ext{test against current canon}
\]

If a source cannot survive this filter cleanly, it is discarded.


## Purpose
This canvas tracks the path from late **v0.8.x** staging to eventual **CANON** status for the following targets:

1. **Dark-sector Euler pressure law**
2. **Dark taxonomy**
3. **Galactic swirl law**
4. **Experimental probes as falsification program**
5. **Benchmark / reproducibility layer**
6. **Topological reference identities**

The focus is not document layout, but **canonization readiness**.

---

## Canonization States
Use exactly these labels for tracking:

- **HOLD** — preserve, clarify, or collect material only
- **BRIDGE** — structured SST layer, but not yet strong enough for full canon
- **CANON-CANDIDATE** — close to canon; missing only limited derivation/benchmark items
- **CANON** — accepted into core canon or mandatory canon appendix

---

## Core Rule for Canonization
A section becomes **CANON** only when all three are satisfied:

1. **Mathematical clarity**
   - definitions are explicit
   - limits are checked
   - dimensions are correct
   - status labels are clean

2. **Logical closure**
   - assumptions are stated
   - relation to existing SST primitives is explicit
   - dependence on fitted ansätze is identified
   - open steps are isolated rather than hidden

3. **Falsifiability / reproducibility**
   - at least one benchmark, observable, or failure mode is stated
   - equations can be re-evaluated from archived inputs
   - numerical pipeline is reproducible

---

# Master Tracker

| Item | Current State | Target State | Priority | Blocking Issue | Next Promotion Gate |
|---|---|---:|---:|---|---|
| 1. Dark-sector Euler pressure law | BRIDGE | CANON | Very High | needs formal embedding into SST source language | derive and freeze canon form + limits + observables |
| 2. Dark taxonomy | HOLD | CANON | High | ontology not yet uniquely anchored to observables | define taxonomy variables and attach to measurable consequences |
| 3. Galactic swirl law | BRIDGE | CANON | Very High | profile still ansatz-level | replace or justify ansatz with source-chain / benchmark path |
| 4. Experimental probes | HOLD | CANON-BRIDGE | Medium | lab-to-theory mapping not uniquely closed | define probe classes and null-result implications |
| 5. Benchmark / reproducibility layer | BRIDGE | CANON | High | needs fixed package/script/archive standard | define mandatory benchmark protocol |
| 6. Topological reference identities | CANON-CANDIDATE | CANON | High | needs final frozen scope and notation | adopt as mandatory appendix toolkit |

---

# Validated Gap-Matrix (v0.8.0 Core + Research-Track)

This matrix converts the tracker into closure-ready gaps that can be actioned directly.

| Item | Present in v0.8.0 now | Validated gap | Required closure action | Promotion readiness |
|---|---|---|---|---|
| 1. Dark-sector Euler pressure law | Yes (core swirl-pressure bridge exists) | assumptions, regime boundaries, and observables/falsifiers are not frozen as one promotion package | freeze assumptions + limits + dimensional check + 2 observables/falsifiers + reproducible input path | BRIDGE -> CANON-CANDIDATE pending freeze |
| 2. Dark taxonomy | Yes (compact visible/quasi-dark/dark rule exists) | still descriptive; no fully measurable classifier table with class-wise falsifiers | lock variable set, decision rules, overlap resolution, observables, and one falsifier per class | HOLD -> BRIDGE pending classifier freeze |
| 3. Galactic swirl law | Partial (staging profile and principles exist) | branch decision (legacy-refine vs source-derived) not frozen; benchmark route not formalized | define branch gate, freeze notation/limits, and bind to rotation-curve benchmark workflow | BRIDGE remains until branch gate is closed |
| 4. Experimental probes | Partial (probe classes listed) | no strict equation-under-test and null-result meaning per probe | map each probe to equation + null-result + confounders + expected sign | HOLD -> BRIDGE when mapping is complete |
| 5. Benchmark / reproducibility layer | Yes (strong baseline in core + research-track) | no single mandatory protocol template reused across sectors | freeze one protocol schema: inputs, scripts, CSV outputs, tolerances, uncertainty, rerun steps | BRIDGE -> CANON-CANDIDATE after protocol freeze |
| 6. Topological reference identities | Partial-strong (key identities present, distributed) | toolkit scope and notation are not frozen in one mandatory appendix block | freeze identity set + notation + citation order as canonical internal toolkit | CANON-CANDIDATE -> CANON after scope freeze |

## Gap-Matrix Notes
- Item 6 and Item 5 are still the fastest high-confidence canonization wins.
- Item 1 should be promoted before Item 3 finalization.
- Item 2 should be symmetry-first but must include helicity/instability filtering before CANON promotion.
- Item 4 is a falsification layer and should not be used as substitute derivation.

---

# 1. Dark-Sector Euler Pressure Law

## Goal
Promote the radial pressure law from useful bridge relation to **formal canon anchor** for the dark-sector program.

## Working canonical equation
\[
\frac{1}{\rho}\frac{d p_{\text{swirl}}}{dr} = \frac{v(r)^2}{r}
\]

Flat-tail limit:
\[
v(r) \to v_0
\quad\Longrightarrow\quad
p_{\text{swirl}}(r)=p_0+\rho v_0^2 \ln\!\left(\frac{r}{r_0}\right)
\]

## Why this is the anchor
- It is stronger than a fit formula.
- The structure comes from stationary radial Euler balance for azimuthal drift.
- The SST-specific layer is the interpretation of this pressure field as a dark-sector driver or classifier.

## Required for CANON
- [ ] Explicit derivation from stationary axisymmetric Euler balance
- [ ] Precise assumptions listed: incompressible, inviscid, stationary, azimuthal-dominant flow
- [ ] Small- and large-\(r\) limits stated
- [ ] Dimensional check included
- [ ] Relation to SST source variables stated
- [ ] At least two observables or falsifiers attached
- [ ] Distinction frozen between **orthodox derivation** and **SST interpretation**

## Promotion path
- **Now:** BRIDGE
- **Next:** CANON-CANDIDATE after derivation + assumptions + limits are frozen
- **Final:** CANON when connected to observables and reproducible reconstruction workflow

## Open questions
- What exactly is the SST source chain for \(v(r)\) in galactic settings?
- Which density should be used in each layer: effective \(\rho_{\!f}\), coarse-grained bulk density, or another derived sector variable?
- Under what conditions does the pressure law remain valid if radial drift or stratification is present?

---

# 2. Dark Taxonomy

## Goal
Create a **stable SST taxonomy** separating visible, quasi-dark, and dark sectors in a way that is not purely verbal.

## Desired output
A canon-ready classification with explicit variables such as:
- chirality / achirality
- helicity or near-zero helicity
- low-order instability count
- possible knot-topology markers
- coupling visibility to long-range swirl structure

## Required for CANON
- [ ] Minimal variable set fixed
- [ ] Taxonomy written as a decision table or rule set
- [ ] Each class linked to at least one observable or phenomenological consequence
- [ ] Connection to existing SST topology sector is explicit
- [ ] Ambiguous overlapping classes removed
- [ ] At least one falsifier for each class

## Suggested development order
1. Start with three bins only:
   - visible
   - quasi-dark
   - dark
2. Add optional refinement later:
   - achiral
   - low-helicity
   - instability-filtered
3. Only then connect to galactic phenomenology

## Promotion path
- **Now:** HOLD
- **Next:** BRIDGE after rule-based taxonomy exists
- **Next:** CANON-CANDIDATE after observables are assigned
- **Final:** CANON once tied to the dark-sector pressure / galactic law framework

## Blocking issue
The taxonomy is not yet unique. It must stop being a conceptual list and become a **classification map**.

---

# 3. Galactic Swirl Law

## Goal
Canonize a galactic-scale swirl law, not necessarily identical to the old one, but strong enough to serve as the SST galactic closure layer.

## Legacy profile to preserve as staging reference
\[
v(r)=\frac{C_{\text{core}}}{\sqrt{1+(r_c/r)^2}} + C_{\text{tail}}\left(1-e^{-r/r_c}\right)
\]

## Canonization principle
The final galactic swirl law does **not** need to equal the legacy formula. It only needs to:
- recover acceptable inner and outer limits,
- connect to the dark-sector pressure law,
- support benchmark comparison to rotation curves,
- and be stated with explicit assumptions.

## Required for CANON
- [ ] Law written in canon notation
- [ ] Small-\(r\) limit checked
- [ ] Flat-tail / large-\(r\) limit checked
- [ ] Pressure reconstruction shown from item 1
- [ ] Source assumptions listed
- [ ] Parameter meanings fixed
- [ ] Benchmark route against observed rotation curves defined
- [ ] Failure modes listed

## Development branches
### Branch A — keep legacy structure, refine constants
Useful if the old law already behaves well enough.

### Branch B — derive a new source-based law
Preferred if a cleaner SST closure can be built from source terms, pressure, topology, or clock-sector coupling.

## Promotion path
- **Now:** BRIDGE
- **Next:** CANON-CANDIDATE after limits + pressure reconstruction + source assumptions are frozen
- **Final:** CANON after benchmark layer is attached

## Key design rule
Do **not** canonize a galactic profile merely because it fits. Canonize it only if it is a controlled SST layer.

---

# 4. Experimental Probes as Falsification Program

## Goal
Preserve experimental ideas, but convert them into a **disciplined falsification layer** rather than informal support.

## Probe classes
- astrophysical probes
- laboratory pressure/swirl analog probes
- HV-coil / thrust-inspired probes
- optical / torsional coupling probes
- null tests for dark-sector interpretation

## Required for promotion to CANON-BRIDGE
- [ ] Probe class list frozen
- [ ] For each probe: what equation is being tested?
- [ ] For each probe: what null result weakens or kills the claim?
- [ ] Confounders listed
- [ ] Theory-to-measurement mapping explicit

## Rule
Experimental probes do **not** canonize a law by themselves. They only strengthen a law already stated mathematically.

## Promotion path
- **Now:** HOLD
- **Next:** BRIDGE after equations-to-probes mapping exists
- **Later:** possible canon appendix once mature and standardized

---

# 5. Benchmark / Reproducibility Layer

## Goal
Make reproducibility a mandatory canon support structure.

## Required outputs
- benchmark tables
- archived CSV outputs
- script / package paths
- predictive vs closure mode separation
- uncertainty propagation rules
- versioned pipeline description

## Required for CANON
- [ ] Benchmark protocol template frozen
- [ ] Required outputs defined
- [ ] Predictive vs closure mode clearly distinguished
- [ ] Numerical tolerances specified
- [ ] Archive naming/versioning rule frozen
- [ ] Minimal rerun procedure stated

## Canon role
This should become a **mandatory appendix layer**, not optional commentary.

## Promotion path
- **Now:** BRIDGE
- **Next:** CANON-CANDIDATE after protocol freeze
- **Final:** CANON when attached to every promoted quantitative sector

---

# 6. Topological Reference Identities

## Goal
Freeze a standard mathematical toolkit that the rest of the canon can cite internally.

## Must include
- Gauss linking integral
- helicity in ideal fluids
- thin-tube helicity reduction
- Hopf invariant
- basic torus-knot invariants
- Călugăreanu–White–Fuller relation

## Why this should canonize early
- orthodox mathematics
- stable and reusable
- directly supports topology-first SST sectors
- reduces dependence on scattered notes and side papers

## Required for CANON
- [ ] scope frozen
- [ ] notation aligned with SST house style
- [ ] no redundant variants
- [ ] relation to topology kernel clarified
- [ ] appendix cross-reference structure fixed

## Promotion path
- **Now:** CANON-CANDIDATE
- **Final:** CANON as mandatory appendix toolkit

---

# Dependency Graph

## Foundational order
1. **Topological reference identities**
2. **Benchmark / reproducibility layer**
3. **Dark-sector Euler pressure law**
4. **Dark taxonomy**
5. **Galactic swirl law**
6. **Experimental probes**

## Dependency notes
- Item 3 can become CANON before item 2 is fully complete, but not safely without at least a draft benchmark standard.
- Item 5 should not become CANON before item 3 is frozen.
- Item 2 strengthens every other promoted sector.
- Item 6 is the easiest early canonization win.

---

# Immediate Work Queue

## Wave 1 — easiest canon wins
- [ ] Freeze topological reference identities scope
- [ ] Freeze benchmark/reproducibility protocol skeleton
- [ ] Write final dark-sector Euler law section with status labels

## Wave 2 — convert bridge to structured canon-candidate
- [ ] Define dark taxonomy variables and class rules
- [ ] Build galactic swirl law draft in canon notation
- [ ] Attach limits and pressure reconstruction

## Wave 3 — falsification and benchmark attachment
- [ ] Define benchmark data path for galactic law
- [ ] Add observables/falsifiers for dark taxonomy
- [ ] Sort experimental probes by directness and confounder load

---

# Execution Checklist (Operator Mode)

Use this as a direct execution list. Do not promote any item without passing all required checks.

## Stage 0 — Freeze infrastructure first
- [ ] **Item 6 scope freeze:** identity list fixed (Gauss linking, helicity, thin-tube reduction, Hopf, torus-knot invariants, Călugăreanu-White-Fuller).
- [ ] **Item 6 notation freeze:** one notation convention used everywhere (no parallel symbol variants).
- [ ] **Item 5 protocol freeze:** mandatory benchmark template fixed (input constants, script/package path, archived CSV, uncertainty propagation, rerun instructions).
- [ ] **Stage-0 pass condition:** Item 6 and Item 5 have explicit frozen checklists and no unresolved notation conflicts.

## Stage 1 — Promote pressure-law anchor (Item 1)
- [ ] Derivation statement frozen from stationary axisymmetric Euler radial balance.
- [ ] Assumption block frozen: incompressible, inviscid, stationary, azimuthal-dominant, and explicit validity limits.
- [ ] Limits frozen: small-\(r\), large-\(r\), and flat-tail interpretation.
- [ ] Dimensional consistency block included.
- [ ] Orthodox derivation and SST interpretation separated with status labels.
- [ ] At least two observables/falsifiers attached with reproducible benchmark path.
- [ ] **Stage-1 pass condition:** Item 1 can be promoted to CANON-CANDIDATE.

## Stage 2 — Convert taxonomy into measurable classifier (Item 2)
- [ ] Minimal variable set frozen (symmetry, chirality/amphichirality, helicity, low-order instability count).
- [ ] Decision-rule table frozen (visible, quasi-dark, dark).
- [ ] Ambiguity handling frozen (overlap and tie-break rule).
- [ ] One baseline template example and one falsifier defined per class.
- [ ] Link to large-scale swirl behavior made explicit.
- [ ] **Stage-2 pass condition:** Item 2 can be promoted to BRIDGE (or CANON-CANDIDATE if observables are complete).

## Stage 3 — Galactic law branch gate and closure (Item 3)
- [ ] **Branch gate closed:** choose Branch A (legacy refine) or Branch B (source-derived law).
- [ ] Parameter meanings and assumptions frozen in canonical notation.
- [ ] Small-\(r\) and flat-tail limits validated.
- [ ] Pressure reconstruction path from Item 1 attached.
- [ ] Rotation-curve benchmark route defined with data and rerun protocol.
- [ ] Failure modes listed explicitly.
- [ ] **Stage-3 pass condition:** Item 3 can be promoted to CANON-CANDIDATE.

## Stage 4 — Probe falsification map (Item 4)
- [ ] Probe classes frozen.
- [ ] For each probe: equation under test fixed.
- [ ] For each probe: null-result meaning fixed.
- [ ] For each probe: confounders and mitigation notes listed.
- [ ] For each probe: measurable output and expected sign/trend listed.
- [ ] **Stage-4 pass condition:** Item 4 can be promoted to CANON-BRIDGE.

## Stage 5 — Promotion review pass
- [ ] Every promoted item satisfies mathematical clarity, logical closure, and reproducibility/falsifiability gates.
- [ ] No item promoted on fit quality alone.
- [ ] Cross-item dependencies respected (Item 1 before Item 3 final canonization).
- [ ] **Stage-5 pass condition:** promotion labels updated consistently in the Master Tracker.

---

# Promotion Gates by Item

## Item 1 — Dark-sector Euler pressure law
**Promote to CANON when:** derivation, assumptions, limits, and observables are frozen.

## Item 2 — Dark taxonomy
**Promote to CANON when:** classes are rule-based, tied to observables, and integrated with item 1 or 3.

## Item 3 — Galactic swirl law
**Promote to CANON when:** source structure or justified closure is fixed and benchmark route exists.

## Item 4 — Experimental probes
**Promote to CANON-BRIDGE when:** every probe is attached to a specific equation and null-result meaning.

## Item 5 — Benchmark / reproducibility layer
**Promote to CANON when:** a mandatory protocol exists and is reusable across sectors.

## Item 6 — Topological reference identities
**Promote to CANON when:** scope and notation are frozen.

---

# Working Decisions Log

## Current strategic decision
The **first major dark-sector canonization target** is not the full galaxy theory. It is the **Dark-sector Euler pressure law**.

## Current secondary decision
The **Galactic swirl law** should be treated as a controlled closure layer built above item 1, not as a stand-alone fit formula.

## Current staging decision
The **Topological reference identities** and **Benchmark / reproducibility layer** should be promoted early because they stabilize everything else.

---

# Notes / Future Append-Only Updates

Use this section to append:
- revised equations
- decision changes
- benchmark requirements
- source-chain ideas for galactic closure
- taxonomy refinements

---

# Added SST-Native Salvage Notes — SST-02 and SST-04

## SST-02 — taxonomy skeleton only
Use this source only for a compact SST-native taxonomy skeleton.

Keep:
- unknotted sectors as bosonic or carrier-like excitation class
- torus-knot sectors as charged-lepton class
- chiral hyperbolic sectors as quark-class seed
- high-symmetry amphichiral sectors as neutral or dark-candidate seed
- first-generation anchors as historical topology prompts only: 31 for charged-lepton baseline, 52 and 61 for first quark-layer baseline

Do not freeze from this source:
- full species-by-species dictionary as canon fact
- higher-generation assignments as fixed canon
- neutrino identity claims as closed canon
- exact dark-state identity claims as closed canon

Canon-plan impact:
- supports Item 2: Dark taxonomy
- supports Item 6: Topological or taxonomy appendix

Rewrite target:
Convert SST-02 material into a rule-based classifier, written in current SST house language, with explicit status labels, and without treating the old particle table as final doctrine.

## SST-21 — primary symmetry source for taxonomy
Use this source as the strongest current SST-native source for a symmetry-first taxonomy.

Keep:
- symmetry-first classification by reversibility, amphichirality, allowed periods, and full symmetry group
- invariant set for taxonomy tables: crossing number, braid index, genus, number of components, and where useful hyperbolic volume
- torus-knot ladder as charged-lepton symmetry baseline: 31, 51, 71
- amphichiral subsector as the cleanest current seed for the dark-sector classifier
- internal subdivision of the amphichiral subsector into positive and negative amphichiral branches as a possible refinement layer

Do not freeze from this source:
- the statement dark sector equals amphichiral sector as an already closed final theorem
- the full particle mapping table as settled canon fact
- every listed exceptional knot as already-accepted physical state
- the invariant mass kernel as mandatory core canon for the current dark-sector program

Canon-plan impact:
- strongly strengthens Item 2: Dark taxonomy
- strongly strengthens Item 6: Topological or taxonomy appendix
- gives a cleaner SST-native replacement for most taxonomy salvage previously taken from older sources

Rewrite target:
Use SST-21 to rebuild Item 2 around a symmetry-first classifier:
1. visible sector candidates: chiral sectors
2. quasi-dark candidates: near-balanced or weak-coupling sectors
3. dark candidates: amphichiral sectors
4. optional refinement: positive versus negative amphichirality

Promotion consequence:
Item 2 should now be built primarily from SST-21, with older SST notes used only for secondary support.

## v0.6.0 canon line — dynamic filter for taxonomy and benchmark protocol
Use this source not as authority over v0.8.x, but as a strong SST-native seed for two things:
- a dynamic filter on the dark taxonomy,
- and a benchmark or calibration protocol skeleton.

Keep:
- the visible / quasi-dark / dark three-way rule structure
- the idea that dark-sector classification must not rely on invisibility language alone
- the stronger dynamic criterion: dark candidates are filtered by the joint absence of chirality, helicity, and low-order unstable modes
- example role only: figure-eight as dark baseline, Borromean-type link as quasi-dark baseline, trefoil as visible baseline
- calibration-protocol and experimental-status section structure as a reproducibility template

Do not freeze from this source:
- older full canon packaging as authority over v0.8.x
- complete particle dictionary as final doctrine
- any cosmology or application layer merely because it appears in the older canon

Canon-plan impact:
- strongly strengthens Item 2 by adding a symmetry-plus-stability filter
- strengthens Item 5 through calibration-protocol notes and experimental-status blocks
- weakly supports Item 4 by clarifying what kinds of bounds and status summaries belong in the falsification layer

Rewrite target:
Merge SST-21 and v0.6.0 into one classifier logic:
- symmetry identifies candidate sectors
- helicity and low-order instability filter which candidates remain dark, quasi-dark, or visible

Working rule:
Dark taxonomy should no longer be symmetry-only. It should be symmetry-first, then stability-filtered.

## SST-04 — identities + galactic motivation only
Use this source only for canonical identities already compatible with SST and for large-scale organized-swirl motivation.

Keep:
- circulation quantum structure: κ = 2π r_c ||v_swirl||
- quantized circulation: Γ = nκ
- Swirl-Clock time-scaling seed: S_t = sqrt(1 - v^2 / c^2)
- Chronos–Kelvin invariant as canonical bridge idea
- the large-scale idea that organized swirl structure may source galactic-scale support without separate ad hoc dark components

Do not freeze from this source:
- sevenfold genesis as canon requirement
- recursive or fractal universe claims as canon fact
- cosmological-totality claims without benchmark route
- broad anti-ΛCDM claims as already established canon

Canon-plan impact:
- supports Item 3: Galactic swirl law as motivation or closure seed
- supports future Rosetta-v0.8.x identity cards
- weak support for Item 1 only through identity consistency, not derivation

Rewrite target:
Convert SST-04 material into a clean SST identity note, a galactic organized-swirl motivation block, and a benchmark-oriented bridge rather than a cosmological manifesto.

## Updated practical use rule
SST-native pre-v0.8 sources may be used more freely than VAM-era sources, but still do not override the newest canon.

Operational rule:
older SST source -> extract compatible identity or classifier seed -> rewrite in current v0.8.x style -> attach status plus benchmark path.

## Immediate work consequences
When advancing the canonization plan:
- use SST-21 as the primary SST-native source for the first clean draft of the dark-sector classifier
- use the v0.6.0 canon line to add the stability and helicity filter on top of the symmetry classifier
- use SST-02 only as secondary compact support for older particle-sector shorthand
- use SST-04 to support galactic-scale motivation and canonical identity continuity
- use Rosetta-v0.6 later only as a structural example for Rosetta-v0.8.x, not as binding content
- use the v0.5.9 cheat-sheet only as a future Rosetta or cosmology-note prompt, not as current core canon authority

## Source Locator (plan-discussed parts only)
Use this as a quick index while executing this canonization plan. It intentionally includes only sources already discussed in this document.

### Primary canonization workspace (current target)
- `papers/SST-CANON/canonization_plan_dark_sector_v_0_8_x_to_v_0.md`
- `papers/SST-CANON/SST_CANON-v0.8.0.tex`
- `papers/SST-CANON/canon-0.8.0-research-track.tex`

### CANON archive sources (primary historical SST line)
- `papers/SST-CANON/archive/Swirl-String-Theory_CANON-v0.6.0.tex`

### SST-native salvage sources referenced in this plan
- `papers/SST-21_Knot_Taxonomy/SST-21_Knot_Taxonomy.tex` (primary for Item 2 classifier basis)
- `papers/SST-02_Knot_Classified/SST-02_Knot_Classified.tex` (secondary compact taxonomy support)
- `papers/SST-04_Cosmologie/SST-04_Cosmology2.tex` (identities + galactic motivation only)

### VAM source domain (restricted use)
- `papers/VAM/` (use only for idea extraction and benchmark/falsifier prompts; never import wording or ontology into final canon text)

### Item-to-source routing for this plan
- **Item 1 (Euler pressure law):** `SST_CANON-v0.8.0.tex` + `archive/Swirl-String-Theory_CANON-v0.6.0.tex` + `SST-04_Cosmology2.tex` (motivation only)
- **Item 2 (Dark taxonomy):** `SST-21_Knot_Taxonomy.tex` (primary) + `SST-02_Knot_Classified.tex` (secondary) + `archive/Swirl-String-Theory_CANON-v0.6.0.tex` (stability/helicity filter)
- **Item 3 (Galactic swirl law):** `SST_CANON-v0.8.0.tex` + `SST-04_Cosmology2.tex` + `archive/Swirl-String-Theory_CANON-v0.6.0.tex`
- **Item 4 (Experimental probes):** `canon-0.8.0-research-track.tex` + benchmark sections in `SST_CANON-v0.8.0.tex` + selected VAM prompts (restricted)
- **Item 5 (Benchmark/reproducibility):** benchmark sections in `SST_CANON-v0.8.0.tex` + `canon-0.8.0-research-track.tex` + `archive/Swirl-String-Theory_CANON-v0.6.0.tex`
- **Item 6 (Topological identities):** topology sections in `SST_CANON-v0.8.0.tex` + `SST-21_Knot_Taxonomy.tex`

### First Open Order (fast start sequence)
Open these files first when actively working each item.

- **Item 1 — Euler pressure law**
  1. `papers/SST-CANON/SST_CANON-v0.8.0.tex`
  2. `papers/SST-CANON/archive/Swirl-String-Theory_CANON-v0.6.0.tex`
  3. `papers/SST-04_Cosmologie/SST-04_Cosmology2.tex`

- **Item 2 — Dark taxonomy**
  1. `papers/SST-21_Knot_Taxonomy/SST-21_Knot_Taxonomy.tex`
  2. `papers/SST-CANON/archive/Swirl-String-Theory_CANON-v0.6.0.tex`
  3. `papers/SST-02_Knot_Classified/SST-02_Knot_Classified.tex`

- **Item 3 — Galactic swirl law**
  1. `papers/SST-CANON/SST_CANON-v0.8.0.tex`
  2. `papers/SST-04_Cosmologie/SST-04_Cosmology2.tex`
  3. `papers/SST-CANON/archive/Swirl-String-Theory_CANON-v0.6.0.tex`

- **Item 4 — Experimental probes**
  1. `papers/SST-CANON/canon-0.8.0-research-track.tex`
  2. `papers/SST-CANON/SST_CANON-v0.8.0.tex`
  3. `papers/VAM/` (only targeted prompt extraction, never wording import)

- **Item 5 — Benchmark/reproducibility**
  1. `papers/SST-CANON/SST_CANON-v0.8.0.tex`
  2. `papers/SST-CANON/canon-0.8.0-research-track.tex`
  3. `papers/SST-CANON/archive/Swirl-String-Theory_CANON-v0.6.0.tex`

- **Item 6 — Topological identities**
  1. `papers/SST-CANON/SST_CANON-v0.8.0.tex`
  2. `papers/SST-21_Knot_Taxonomy/SST-21_Knot_Taxonomy.tex`
  3. `papers/SST-CANON/canonization_plan_dark_sector_v_0_8_x_to_v_0.md`

## Additional promotion gates from SST-21 and v0.6.0

### Item 2 — Dark taxonomy
Add gates:
- [ ] symmetry-first rule set frozen using current SST taxonomy language
- [ ] amphichiral sector treated as a tested classifier proposal, not as an unqualified final theorem
- [ ] positive versus negative amphichiral split evaluated for observable usefulness
- [ ] explicit link added between symmetry class and binding or non-binding behavior in organized large-scale swirl structure
- [ ] helicity and low-order instability filter added so taxonomy is not symmetry-only
- [ ] visible, quasi-dark, and dark classes each have at least one baseline template example and one falsifier

### Item 5 — Benchmark / reproducibility layer
Add gates:
- [ ] calibration protocol note template frozen
- [ ] experimental status and bounds summary format frozen
- [ ] traceability from constants to procedures stated explicitly

### Future Rosetta or cosmology note
Hold only:
- minimal SST to ΛCDM comparison dictionary style from the v0.5.9 cheat-sheet
- observational-falsifier presentation style for later use in Rosetta-v0.8.x or a separate cosmology bridge

