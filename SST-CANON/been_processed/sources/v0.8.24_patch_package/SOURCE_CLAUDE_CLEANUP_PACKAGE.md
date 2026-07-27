# CANON v0.8.24 — Opschonings- en canonisatiepakket

Bronbasis: `SST_CANON-v0_8_23.tex` (main) + `SST_CANON-v0_8_23-research-track.tex` (RT).
Alle regelnummers verwijzen naar de geüploade v0.8.23-bestanden. Alle LaTeX-blokken zijn drop-in bedoeld; pas labels/namen aan waar je eigen conventie afwijkt.

Prioriteitsvolgorde: **P1 → P2/P3 → P4 → P5/P6 → C-promoties → R-redactie.**
P1 moet vóór elke numerieke run; anders test SSTcore tegen een fout criterium.

---

## DEEL 1 — Normatieve fixes

### P1 — Core–torsion normalisatie (factor 2) — GEVERIFIEERD TEGEN DE BRON

**Bevinding.** De boxed target staat op twee plaatsen:

- MAIN r. 1485, `eq:core_torsion_impedance_gate_main`
- RT r. 9008, `eq:rt_core_torsion_matching_lemma`

beide als `M_torsion =? (2E_0/c_T²) I`, met RT r. 9012 als "equivalent": `ΔE = E_0 u²/c_T²`.

De Lorentz-expansie voor een carrier met rustenergie `E_0`:
`E(u) = γE_0 = E_0 + ½E_0 u²/c² + O(u⁴)`, dus `ΔE = ½ u^T M u` ⇒ `M = E_0/c² · I`.

**Doorslaggevend intern bewijs:** de canon's eigen Density Hierarchy (MAIN, direct ná de
Two-Speed sectie) definieert `ρ_M = ρ_E/c²` met [ORTHODOX]-tag: *"total energy E in a
region still yields mass density E/c²"*. De 2E_0-target is dus in tegenspraak met de
canon's eigen orthodoxe massa-energieconventie. Vermoedelijke oorsprong: verwarring van
de niet-relativistische KE-inversie `M = 2E_kin/u²` met de rustenergierelatie `M = E_0/c²`.

**Enige reddingsroute** (niet aanbevolen): `E_0[K]` expliciet definiëren als de *halve*
rustenergie via een equipartitie-/viriaalclaim. Die claim is voor de resolved-tube
functional `E_SI + T_eff L + B_eff∮κ² + E_twist` generiek onwaar (geen 50/50-verdeling
gegarandeerd) en botst met de frase "rest-swirl energy". Kies dus: `E_0` = totale
rustenergie, `M = E_0/c²`.

**Drop-in vervanging — RT, vervang het lemma-blok (r. ~8998–9035):**

```latex
\subsection{Core--Torsion Impedance Matching Lemma}

Let $K$ be a localized closed swirl-string configuration with total
rest-swirl energy $E_0[K]$ (the full rest energy of the configuration;
no partition convention is implied). Define the torsion-dressed inertial
tensor by the quadratic stored-energy response
\begin{align}
    \Delta E_{\rm torsion}[K;\mathbf u]
    =
    \frac12\,\mathbf u^{\mathsf T}
    \mathsf M_{\rm torsion}[K]\,
    \mathbf u
    +O(\lVert\mathbf u\rVert^4).
\end{align}
The Lorentz-compatible closure, consistent with the canonical
mass-equivalence rule $\rhoM=\rhoE/c^2$, is
\begin{align}
    \boxed{
    \mathsf M_{\rm torsion}[K]
    \stackrel{?}{=}
    \frac{E_0[K]}{c_T^2}\,\mathsf I
    }
    \label{eq:rt_core_torsion_matching_lemma}
\end{align}
or equivalently
\begin{align}
    \Delta E_{\rm torsion}[K;u]
    \stackrel{?}{=}
    \frac12\,E_0[K]\frac{u^2}{c_T^2}+O(u^4),
\end{align}
matching the expansion $\gamma E_0 = E_0 + \tfrac12 E_0 u^2/c_T^2 + O(u^4)$.

\textbf{[NORMALIZATION NOTE, v0.8.24].} Earlier canon versions stated the
target as $2E_0[K]/c_T^2$. That form is inconsistent with the canonical
rule $\rhoM=\rhoE/c^2$ unless $E_0$ is redefined as half the rest energy;
no such convention is adopted. The corrected target above supersedes it.

Define the normalized scale residual and the anisotropy residual
\begin{align}
    \widehat{\chi}_K^{(T)}
    &=
    \frac{c_T^2}{E_0[K]}\,
    \lambda_{\rm iso}\!\left(\mathsf M_{\rm torsion}[K]\right),
    \\
    \delta_{\rm aniso}(K)
    &=
    \frac{\bigl\lVert
        \mathsf M_{\rm torsion}[K]
        -\tfrac13\operatorname{tr}\!\bigl(\mathsf M_{\rm torsion}[K]\bigr)\mathsf I
    \bigr\rVert_F}{\bigl\lVert\mathsf M_{\rm torsion}[K]\bigr\rVert_F}.
\end{align}
The bridge closes only if, within numerical and topological tolerance,
\begin{align}
    \widehat{\chi}_K^{(T)}=1
    \qquad\text{and}\qquad
    \delta_{\rm aniso}(K)=0 .
\end{align}
A correct average scale with $\delta_{\rm aniso}\neq0$ yields
direction-dependent inertia and fails monometricity; the scale test alone
is therefore insufficient.

\textbf{[OPEN LEMMA].}
The joint condition above, for \emph{all} admitted stable carriers with
one common set of link/torsion parameters, is the falsifiable theorem
target. Per-knot retuning of $K_T$ demotes the result to calibrated
matching.
```

**Bijbehorende wijzigingen elders:**

1. MAIN r. 1485: `2E_0[K]` → `E_0[K]` in `eq:core_torsion_impedance_gate_main`
   (plus dezelfde normalization note in één regel).
2. RT r. 9040, numerieke testlijst item 1:
   `2E_0[K]/c_s^2` → `E_0[K]/c_s^2` (zelfde conventie, akoestische laag).
3. Vervang de testlijst door de uitgebreide versie:

```latex
\begin{enumerate}
    \item the NLSE boost coefficient $M_{\rm core}[K]$ and its comparison
          to $E_0[K]/c_s^2$, not to $E_0[K]/c^2$;
    \item the torsion-dressed tensor $\mathsf M_{\rm torsion}[K]$, the
          residuals $\widehat{\chi}_K^{(T)}$ and $\delta_{\rm aniso}(K)$,
          and their mesh- and geometry-convergence;
    \item a geometry ladder: (i) round ring, (ii) axisymmetric torus
          carrier, (iii) trefoil $3_1$, (iv) mirror trefoil, (v) figure-eight
          $4_1$ --- the ring/torus stages isolate response-operator errors
          from genuine topological effects before any knot is interpreted;
    \item a stiffness sweep $K_T$ verifying whether
          $\widehat{\chi}_K^{(T)}=1$ occurs at $c_T=c$ with one common
          parameter set, or only after per-carrier retuning;
    \item the circulation-normalization ratio
          $\mathcal R_\Gamma=(h_*/m_*)/\Gamma_0$ (unity under the canonical
          single-winding convention);
    \item the trefoil-locked source test comparing $T_{2,3}$ against
          generic helical sources.
\end{enumerate}
```

---

### P2 — Orthodoxe attributie van de compacte U(1) link-actie

**Locatie:** RT `sec:rt_minimal_link_field_action`, subsubsectie
"Minimal compact link action", direct ná `eq:rt_minimal_compact_link_action`.

```latex
\textbf{[ORTHODOX / ATTRIBUTION].}
Equation~\eqref{eq:rt_minimal_compact_link_action} is, up to notation, the
Hamiltonian formulation of compact $U(1)$ lattice gauge theory
\cite{Wilson1974,KogutSusskind1975,Kogut1979}. Consequently the discrete
Gauss constraint, the plaquette equation of motion, the linear lattice
dispersion, and the source-free Maxwell--Faraday structure of the infrared
limit are established results of that theory, not SST results. The SST
content of this section is confined to (i) the physical identification of
the link phase with relative torsion between substrate elements, (ii) the
zero-legacy provenance rules imposed on $(a_\ell,I_\ell,K_\ell)$, and
(iii) the Helmholtz-sector separation gate.
```

**Bibitems (MAIN-bibliografie; DOI's gecontroleerd op vorm, verifieer bij invoegen):**

```latex
\bibitem{Wilson1974}
K.~G. Wilson,
\newblock Confinement of quarks,
\newblock \emph{Physical Review D} \textbf{10} (1974), 2445--2459,
\newblock DOI: \href{https://doi.org/10.1103/PhysRevD.10.2445}{10.1103/PhysRevD.10.2445}.

\bibitem{KogutSusskind1975}
J.~Kogut and L.~Susskind,
\newblock Hamiltonian formulation of Wilson's lattice gauge theories,
\newblock \emph{Physical Review D} \textbf{11} (1975), 395--408,
\newblock DOI: \href{https://doi.org/10.1103/PhysRevD.11.395}{10.1103/PhysRevD.11.395}.

\bibitem{Kogut1979}
J.~B. Kogut,
\newblock An introduction to lattice gauge theory and spin systems,
\newblock \emph{Reviews of Modern Physics} \textbf{51} (1979), 659--713,
\newblock DOI: \href{https://doi.org/10.1103/RevModPhys.51.659}{10.1103/RevModPhys.51.659}.

\bibitem{Polyakov1977}
A.~M. Polyakov,
\newblock Quark confinement and topology of gauge theories,
\newblock \emph{Nuclear Physics B} \textbf{120} (1977), 429--458,
\newblock DOI: \href{https://doi.org/10.1016/0550-3213(77)90086-4}{10.1016/0550-3213(77)90086-4}.

\bibitem{Guth1980}
A.~H. Guth,
\newblock Existence proof of a nonconfining phase in four-dimensional
$U(1)$ lattice gauge theory,
\newblock \emph{Physical Review D} \textbf{21} (1980), 2291--2307,
\newblock DOI: \href{https://doi.org/10.1103/PhysRevD.21.2291}{10.1103/PhysRevD.21.2291}.
```

---

### P3 — Deconfinement-/monopool-gate

**Locatie 1:** toevoegen als item in het "Required certification programme"
van de link-actie (na huidig item 3):

```latex
    \item demonstrate that the compact theory sits in the deconfined
    (Coulomb) phase of compact $U(1)$: monopole/plaquette phase-slip
    events must be suppressed rather than condensed
    \cite{Polyakov1977,Guth1980}. In the condensed phase the transverse
    excitation acquires a mass gap and the infrared Maxwell structure
    fails. The weak-coupling Coulomb phase is known to exist in $3{+}1$D
    \cite{Guth1980}; the SST microparameters must be shown to land in it
    without tuning to that outcome;
```

**Locatie 2:** toevoegen aan de falsifier-lijst van de link-actie:

```latex
a monopole/phase-slip proliferation regime in which the transverse mode
acquires a mass gap (compact-$U(1)$ confinement), incompatible with
long-range source-free radiation;
```

**Locatie 3:** koppeling aan de Helmholtz-gate (één alinea, in de
Helmholtz-sector-separation subsubsectie):

```latex
\textbf{[GATE INTERACTION].}
Because $\vartheta_e$ is compact, $2\pi$ plaquette phase slips exist as
dynamical events. These are precisely the microscopic candidates for the
declared source/boundary/reconnection/Kairos exceptions to
$\Delta\Gamma_C=0$. The Helmholtz gate therefore has dynamical content
only in the phase where such events are exponentially suppressed; the
deconfinement condition above and the Helmholtz gate are one and the same
requirement viewed from the field and the loop side respectively.
```

---

### P4 — a_ℓ-scenariosplitsing en dispersie-guard

**Locatie:** RT, direct ná `eq:rt_link_alpha_response_ratio`
(de `α_SST = (1/π)√(ι/κ)`-vergelijking).

```latex
\paragraph{Calibrated targets and scale scenarios.}
\textbf{[CALIBRATED CONSISTENCY TEST].}
Under the special identification $a_\ell=r_c$, matching the kinematic
target $\alpha=2\vchar/c_T$ requires
\begin{align}
    \frac{\kappa_\ell}{\iota_\ell}
    =
    \frac{1}{(\pi\alpha)^2}
    \approx
    1.9027\times10^{3}.
    \label{eq:rt_link_alpha_ratio_target}
\end{align}
This number is a matching target, not a derivation: the route currently
trades one unknown ($\alpha$) for two undetermined response coefficients
plus one scale ansatz. Any proposed microstructure must produce a
stiffness-to-inertia ratio of order $10^{3}$ at $a_\ell=r_c$ without
tuning; absent a mechanism, the fine-structure question is relocated,
not answered.

\textbf{[SCALE-SCENARIO GUARD].}
Three interpretations of $a_\ell$ must be kept distinct:
\begin{description}
    \item[Scenario A (literal fixed lattice).] The dispersion
    Eq.~\eqref{eq:rt_link_lattice_dispersion} is physical, with zone-edge
    momentum $p_{\max}c=\pi\hbar c/a_\ell$. For $a_\ell=r_c$ this gives
    $p_{\max}c\approx440~\mathrm{MeV}$, and order-one deviations from
    $c$ already near $10^{2}~\mathrm{MeV}$. Observed astrophysical
    photons up to $\sim$PeV therefore exclude $a_\ell=r_c$ in this
    scenario and require $a_\ell\lesssim\pi\hbar c/E_{\max}\approx
    6\times10^{-22}~\mathrm{m}$ merely for mode existence, with photon
    time-of-flight and birefringence limits pushing lower still; the
    reduction Eq.~\eqref{eq:rt_link_alpha_response_ratio} then requires
    $\iota_\ell/\kappa_\ell\gtrsim10^{9}$.
    \item[Scenario B (regulator with continuum limit).] $a_\ell$ is a
    computational regulator, $a_\ell\to0$ with fixed continuum response.
    The identification $a_\ell=r_c$ is then not permitted as a physical
    statement, and Eq.~\eqref{eq:rt_link_alpha_response_ratio} survives
    only if the ratio $\iota_\ell/\kappa_\ell$ acquires meaning through
    an independent physical scale.
    \item[Scenario C (relational/dynamical adjacency).] No fixed
    Brillouin zone exists; the sharp zone-edge exclusion does not apply
    directly, and the burden shifts to demonstrating emergent low-energy
    isotropy and the absence of a preferred spacing in correlation
    functions.
\end{description}
Until one scenario is selected and certified,
Eq.~\eqref{eq:rt_link_alpha_response_ratio} carries the status
\textbf{[HISTORICAL BRIDGE / ILLUSTRATION]}, not
\textbf{[RESEARCH HYPOTHESIS with open route]}.
```

*(Getallen: πħc/r_c = π·197.327 MeV·fm / 1.40897 fm = 440.0 MeV;
a_max(PeV) = π·197.327 MeV·fm / 10⁹ MeV ≈ 6.2×10⁻⁷ fm.)*

---

### P5 — Star-basis in de zero-legacy closure

**Locatie:** RT "Zero-legacy dimensional closure"
(`eq:rt_link_zero_legacy_coefficients` t/m `eq:rt_link_alpha_response_ratio`).

Vervang in de zero-legacy vergelijkingen elk gekalibreerd symbool door de
sterretjesbasis, en verplaats de mapping naar één afsluitende alinea:

- `\rhoF` → `\rho_\star`, `\Gamma_0` → `\Gamma_\star`, `r_c` → `r_\star`
  binnen `I_\ell = \iota_\ell\rho_\star a_\ell^5`,
  `K_\ell = \kappa_\ell\rho_\star\Gamma_\star^2 a_\ell`,
  `c_T = (\Gamma_\star/a_\ell)\sqrt{\kappa_\ell/\iota_\ell}` en de
  daaropvolgende ratio-vergelijkingen.

```latex
\paragraph{Calibrated mapping (separate mode).}
\textbf{[CALIBRATED CONSISTENCY MODE].}
Only in this mode may the symbolic basis be mapped onto the current
calibrated chain,
$(\rho_\star,\Gamma_\star,r_\star)\mapsto(\rhoF,\Gamma_0,\rc)$ with
$\Gamma_0=2\pi\rc\vchar$. Because the provenance of
$(\rhoF,\Gamma_0,\rc)$ contains $c$, $\hbar$, $m_e$, and $\alpha$ through
the Compton/electron-radius calibration, no output of this mode may be
labelled \textbf{[PREDICTION]}; the mapping serves consistency and
order-of-magnitude tests only, per the dependency rules of the Genesis
section.
```

Dit sluit de notatie aan op de Genesis-eis dat de zero-legacy basis
symbolisch blijft; de guard stond er al in woorden, nu ook in de symbolen.

---

### P6 — Falsifier-taxonomie (Genesis, "Preregistered falsifiers")

Vervang de vlakke lijst van 11 items door drie klassen (herindeling van de
bestaande items; formuleringen ongewijzigd laten):

```latex
\paragraph{Class E --- empirical falsifiers} (conflict with observation):
items on polarization-, orientation-, or species-dependent low-energy
propagation speed, and on mutually inconsistent characteristic speeds for
clocks, rods, synchronization, and propagation. [huidige items 2, 7]

\paragraph{Class D --- derivational falsifiers} (structural failure of the
model): no stable transverse branch; continuously tunable transition
action or source unit; forced permanent material vorticity from a
source-free pulse; topology or classification change under the declared
refinement pipeline; contact-measure non-convergence despite ropelength
convergence. [huidige items 1, 4, 6, 9, 10]

\paragraph{Class M --- methodological-integrity falsifiers} (the programme
fails as a derivation even if numbers match): $c$-provenance hidden in a
microparameter; $\alpha$ reproduced only after $\alpha$-dependent
calibration; underdetermined microparameters without a selection
principle; precision quoted below the certified geometry-error envelope.
[huidige items 3, 5, 8, 11]
```

Plus één zin: *"A Class M event does not falsify the physical hypothesis;
it voids the derivation claim and returns the result to calibrated
status."* — dat voorkomt de omgekeerde verwarring.

---

## DEEL 2 — Canonisatie-kansen (wat nú verantwoord promoveerbaar is)

### C1 — Maxwell-IR-structuur → [ORTHODOX]
Promotie via P2: zodra de attributie staat, is de hele keten
(Gauss-constraint → plaquette-EOM → dispersie → Maxwell-IR) orthodox
erfgoed en mag hij zonder voorbehoud in de MAIN-interface geciteerd
worden. Paradoxaal maar reëel: demotie naar [ORTHODOX] is hier de
sterkste promotie — het haalt bewijslast wég bij SST.

### C2 — Certificeringsladder → canonieke Definitie + Canon Rule
De ladder (seed < relaxed < near-ideal < strict near-ideal < certified)
is methodologie, geen fysica; canoniseren is risicoloos en bindt alle
sub-papers. Drop-in voor de MAIN (bij de KnotPlot/Ridgerunner-sectie):

```latex
\begin{definition}[Geometry certification ladder]
\label{def:certification_ladder}
Every knot geometry used in a downstream SST claim carries exactly one of
the graded statuses
$\texttt{seed}<\texttt{relaxed candidate}<\texttt{near-ideal candidate}
<\texttt{strict near-ideal}<\texttt{certified smooth upper bound}$,
determined solely by the preregistered gate profile of the release in
which the geometry was produced.
\end{definition}

\textbf{[CANON RULE].} No SST manuscript, benchmark, or numerical result
may cite a geometry above its certified status, silently promote a
geometry between statuses, or weaken a gate profile after inspecting a
physical output. Downstream claims must expose geometry source, topology
certificate, convention, resolution, residual, contact map, and error
envelope.
\end{quote}
```

### C3 — Helmholtz-sector-gate → genummerd [FOUNDATIONAL POSTULATE]
`ΔΓ_C = 0` voor source-free R-fase-propagatie staat nu verspreid (MAIN
photon-sector, RT link-sectie). Het is een definiërende constitutieve
eis, geen empirische claim — promoveerbaar tot postulaat, mét de
Kairos-uitzondering als clausule en de P3-koppeling die hem dynamische
inhoud geeft. Voorstel: als Axiom 9 of als "Foundational Postulate
(Helmholtz sector separation)" direct na Axiom 8, met verwijzing vanuit
beide bestaande passages i.p.v. herhaling.

### C4 — Two-speed discipline → MAIN-lemma [DERIVED, conditional]
`c_s = v_char/√2` volgt strikt uit vier gedeclareerde hypothesen
(GP/NLSE-core, Madelung, Γ_q = Γ_0, ξ = r_c). Formaliseer als
Lemma met die hypotheselijst; de bestaande [DERIVED-CONDITIONAL]-tekst is
al correct — het lemma-format maakt hem citeerbaar in Papers I–IV.

### C5 — Drie gebruiksmodi + extended labels → cross-document Operating Rule
Voeg één Canon Rule toe: *elke SST-sub-paper verklaart per resultaat de
modus (symbolic / calibrated consistency / prediction) en gebruikt de
extended labels van de Genesis-sectie.* Daarmee wordt de epistemische
architectuur bindend buiten de canon zelf — de goedkoopste
geloofwaardigheidswinst in het hele pakket.

### Expliciet NIET canoniseren (met reden, één regel elk)
- **α-route** `(1/π)√(ι/κ)`: na P4 status [HISTORICAL BRIDGE / ILLUSTRATION]
  tot een scenario gecertificeerd is.
- **QSS**: blijft research — vereist eerst de response-operator uit het
  P1-programma.
- **Factor-9 rank-test**: telresultaat over contactkanalen; levert geen
  Lie-algebra, geen structuurconstanten — diagnostiek, geen gauge-sector.
- **Golden-layer dressings**: sectorlabels zonder afgeleide energiebijdrage
  (canon zegt dit zelf al — handhaven).
- **θ = π spinoriale selectie**: gepinde superselectie-input blijft; pas
  aanraken als er een kandidaat-mechanisme bestaat (Fase 4).

---

## DEEL 3 — Redactionele fixes (exacte locaties)

| # | Probleem | Locatie | Fix |
|---|---|---|---|
| R1 | `\input{SST_CANON-v0.8.23-research-track}` matcht bestandsnaam met underscores niet | MAIN r. 6298 | Naamconventie gelijktrekken (punten óf underscores, consequent); build faalt anders fataal |
| R2 | Stale companion-verwijzing `canon-0.8.1-research-track.tex` + v0.8.1-inhoudslijst | MAIN r. 4823 | Versie-agnostisch maken: "the companion research-track file of the current edition" zonder inhoudsopsomming |
| R3 | Twee sectiecommando's op één regel → lege TOC-kop | RT r. 1695 (`\subsubsection{Dimensionless diagnostic}\subsubsection{...}`), RT r. 8202 (`\subsection{Tensor-speed naturalness}\subsection{...}`) | Splitsen; lege kop verwijderen of content geven |
| R4 | Sibling-nesting: `\subsection{Research Track: ...}` direct gevolgd door sibling `\subsection{Motivation}` etc. | RT r. 5650/5652, 5740/5742, 5867/5869 (Kairos-tracks); RT r. 5965/5968, 7544/7547, 8907/8911 (`Purpose and status` als sibling) | Onderliggende blokken demoteren naar `\subsubsection` |
| R5 | Terminologiedrift substraat: "Æther elements" | MAIN r. 2807, 2821; RT r. 8498, 8501, 8523 | → "substrate elements"; "Æther" exclusief reserveren voor Einstein–Æther-vergelijkings-EFT |
| R6 | Precisie-inflatie: `K_T^target = 6.29128625115772348e10 Pa` (18 cijfers) terwijl ρF = 7.0e-7 (2 significante cijfers) | RT `eq:rt_core_torsion_stiffness_target` | `≈ 6.3×10¹⁰ Pa`; cijfers matchen aan de gedeclareerde precisie van ρF — dit is falsifier-11-hygiëne op zichzelf toegepast |
| R7 | 57 overfull hboxes (ergste ~40pt, abstract/keywords-regio) | build-log | Cosmetisch; na inhoudelijke fixes |

---

## DEEL 4 — Concept edition note v0.8.24 (drop-in)

```latex
\subsubsection{v0.8.24}
    \textbf{v0.8.24} corrects the core--torsion impedance target to the
    Lorentz-consistent normalization $\mathsf M_{\rm torsion}=E_0/c_T^2\,
    \mathsf I$ with normalized residual $\widehat{\chi}_K^{(T)}$ and
    anisotropy residual $\delta_{\rm aniso}$ (superseding the earlier
    $2E_0/c_T^2$ form); adds orthodox attribution of the minimal link
    action to compact $U(1)$ lattice gauge theory with the
    deconfinement/monopole-suppression gate and its identification with
    the Helmholtz-sector gate; records the calibrated matching target
    $\kappa_\ell/\iota_\ell=(\pi\alpha)^{-2}\approx1.90\times10^{3}$ and
    the three-scenario status guard on $a_\ell$, downgrading the
    $a_\ell=r_c$ reduction to historical-bridge status; rewrites the
    zero-legacy closure in the symbolic star basis with a separate
    calibrated-mapping mode; splits the preregistered falsifiers into
    empirical, derivational, and methodological-integrity classes;
    promotes the geometry certification ladder to a canonical definition
    and rule, the Helmholtz-sector separation to a foundational
    postulate, and the two-speed core relation to a conditional lemma;
    and applies the companion-file, heading-structure, substrate-
    terminology, and precision-hygiene corrections, on top of v0.8.23.
```

---

## DEEL 5 — Verificatiechecklist na patch

1. `grep -c '2E_0' *.tex` → verwacht 0 (of alleen in de normalization note).
2. `grep -n 'AE ther' *.tex` → alleen Einstein–Æther-context.
3. `grep -n 'canon-0.8.1-research-track' *.tex` → 0 treffers.
4. `grep -n 'subsection{.*}\\\\sub' *.tex` → 0 treffers (samengeplakte koppen).
5. Combined build, 2× pdflatex: 0 undefined references, 0 multiply-defined
   labels (v0.8.23-baseline: 209 pp, beide nul — regressie is dus meetbaar).
6. Standalone MAIN-build met correcte `\input`-naam: compileert.
7. Nieuwe cite-keys (Wilson1974, KogutSusskind1975, Kogut1979, Polyakov1977,
   Guth1980) resolven in de MAIN-bibliografie.
