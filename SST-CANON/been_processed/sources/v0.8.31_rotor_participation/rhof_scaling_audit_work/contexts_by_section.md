# SST_CANON-v0.8.31.tex

##  /  / 

### lines 82-90
```latex
\newcommand{\swirlarrow}{\mathchoice{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowleft}}}
\newcommand{\swirlarrowcw}{\mathchoice{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowright}}{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowright}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowright}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowright}}}
\newcommand{\vswirl}{\mathbf{v}_{\swirlarrow}}
\newcommand{\vswirlcw}{\mathbf{v}_{\swirlarrowcw}}
\newcommand{\rhoF}{{\rho_{\!f}}}
\newcommand{\rhoSub}{{\rho_{\mathrm{sub}}}}
\newcommand{\rhoEff}{{\rho_{\mathrm{eff}}^{(0)}}}
\newcommand{\Jomega}{{\mathcal{J}_{\omega}}}
\newcommand{\muell}{{\mu_{\ell}}}
```

## Author's Origin Note: From Impedance and Resonance to Vorticity /  / 

### lines 210-218
```latex
relative vortex clocks was developed in order to provide a more coherent
dynamical substrate for that earlier program.

This historical order matters. The present Canon must not imply that the
current symbols $\Gamma_0$, $\rhoF$, and $\rc$ were the original ontological
starting point. They are candidate parameters of a later continuum
representation. The older and more persistent commitment is structural:
freely propagating radiation and bound matter are different dynamical regimes
of one underlying medium, and their coupling is controlled by the response and
```

## Formal Foundations / Primitive Structure of the Theory / 

### lines 1217-1230
```latex
        We define the Swirl-String Theory (SST) as a continuum-based framework built on a minimal set of primitive quantities.
        
        \textbf{Primitive calibration set:}
        \begin{align}
            \mathcal{P}_{\mathrm{cal}} = \{ \rhoF, \vchar, \omega_c \}
        \end{align}
        
        where:
        \begin{itemize}
            \item $\rhoF\equiv\rhoEff$ is the calibrated quasi-static effective inertial-response density of the selected collective SST sector,
            \item $\vchar=\lVert\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert$ is the canonical characteristic swirl-speed magnitude,
            \item $\omega_c$ is the Compton angular frequency.
        \end{itemize}

```

### lines 1239-1249
```latex
        \textbf{[ORTHODOX]}: $\omega_c = \frac{m_e c^2}{\hbar}$ is a standard physical constant.
        
        \textbf{[SPECULATIVE]}: The identification of $\omega_c$ as the primitive Compton phase frequency of the SST carrier is an SST postulate; it is not a local vorticity variable.

        \textbf{[CALIBRATED / PROVENANCE GUARD]}: Within $\mathcal{P}_{\mathrm{cal}}$, the members $\vchar$ and $\omega_c$ are pinned by CODATA constants through $\vchar=\alpha c/2$ and $\omega_c=m_ec^2/\hbar$, whereas $\rhoF\equiv\rhoEff=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}$ is retained at \emph{two significant figures} with no canon-level derivation and, at present, no explicitly stated independent calibration observable. The quoted value is a point calibration with unresolved systematic uncertainty; two-significant-figure notation is not a statistical confidence interval. The historical VAM expression from which the decimal value was inherited has dimensions $\mathrm{kg\,m^{-1}}$, not $\mathrm{kg\,m^{-3}}$, and is therefore registered as a rotational-microinertia coefficient rather than as a derivation of $\rhoF$; see Subsection~\ref{subsec:rt_historical_rhof_provenance_audit}. Candidate reduction routes, e.g.\ the research-track cosmological impedance lift $\rhoF=\chi_\Lambda(\rc/\ell_P)\rho_\Lambda$ with $\chi_\Lambda\simeq1.37$ and $\rho_\Lambda=\Lambda c^2/(8\pi G)$, are not canon derivations. In particular, the smaller central-value residual of the present-epoch choice $\chi_\Lambda=2\Omega_{\Lambda,0}$ has no promotion force without an epoch-invariant mechanism and a covariance-aware uncertainty model; see Section~\ref{sec:rt_rhof_cosmological_impedance_route} and Subsection~\ref{subsec:ssdl_monopole_dtn}. Every quantity linear in $\rhoF$ (the swirl energy density $\rhoE$, the mass-equivalent density $\rhoM$, the Pauli-barrier benchmark, and dark-sector pressure amplitudes) inherits the unresolved relative uncertainty of $\rhoF$, and no claim requiring $\rhoF$ at better than the stated calibration precision may be promoted.

        \textbf{[DEPENDENCY GUARD]}: In the present primitive architecture, $\rhoF$, $\vchar$, and $\omega_c$ are independent calibration entries. Therefore uncertainty or hypothetical epoch dependence assigned to $\rhoF$ propagates into $\rhoE$, $\rhoM$, pressure amplitudes, and other explicitly $\rhoF$-dependent quantities, but it does \emph{not} by itself shift $\vchar$, $\omega_c$, $\rc=\vchar/\omega_c$, or the Compton closure chain. Such propagation would require an additional constitutive relation and must be labeled separately. A future edition must either state the explicit calibration target that fixes $\rhoF$ or demote $\rhoF$ to an interval-valued effective parameter.


    \subsection{Density Ontology and Backward-Compatible Symbol Rule}
        \label{subsec:density_ontology_v0830}
```

## Formal Foundations / Density Ontology and Backward-Compatible Symbol Rule / 

### lines 1270-1283
```latex
            \label{eq:density_ontology_v0830}
        \end{align}
        The legacy house symbol is retained for backward compatibility as
        \begin{align}
            \boxed{\rhoF\equiv\rhoEff}
            \label{eq:rhof_effective_response_alias}
        \end{align}
        throughout the current release.  No equality
        $\rhoSub=\rhoF$, $\Jomega=\muell$, or
        $\Jomega=\rhoF\ell^2$ is canonical unless an explicit microscopic or
        homogenization theorem supplies the required profile, length, and
        participation measure.

        \textbf{[DIMENSIONAL GUARD].}
```

### lines 1300-1308
```latex
            \frac12\Jomega\lVert\boldsymbol\omega\rVert^2,
            \qquad
            [\boldsymbol\theta]=1.
        \end{align}
        Writing $\tfrac12\rhoF|\boldsymbol\omega|^2$ without an independently
        defined squared length is dimensionally invalid.  A future bridge may
        derive a relation of the form
        \begin{align}
            \Jomega
```

### lines 1315-1323
```latex

        \textbf{[ONTOLOGICAL STATUS].}
        The existence of a material substrate density $\rhoSub>0$ is part of
        Axiom~1, but its numerical value is not fixed in the present Canon.
        The calibrated $\rhoF$ instead belongs to the long-wavelength effective
        response model and must not be cited as a measured ordinary rest-mass
        density of the vacuum or of a resolved vortex tube.

        \textbf{[CANON / QUASI-STATIC RESPONSE GUARD].}
```

### lines 1327-1335
```latex
        long-wavelength branch, the backward-compatible scalar is defined only
        by the quasi-static limit
        \begin{align}
            \boxed{
            \rhoF\equiv\rhoEff
            :=
            \frac13\operatorname{tr}
            \left[
            \lim_{\omega\to0,\,\mathbf{k}\to\mathbf0}
```

### lines 1339-1347
```latex
            \label{eq:rhof_quasistatic_response_limit}
        \end{align}
        whenever this limit exists.  Equation~\eqref{eq:rhof_quasistatic_response_limit}
        fixes the meaning of the symbol; it does not derive its calibrated
        numerical value.  The scalar $\rhoF$ must not be extrapolated to core
        frequencies, finite wave number, or local material compression without
        a separately derived constitutive law.

        \textbf{[CANON / PARTICIPATION GUARD].}
```

### lines 1349-1357
```latex
        squared length, geometry factor, and mode-participation functional are
        independently obtained.  The compact-rotor matching construction
        reproduces a horn-envelope line-inertia coefficient but leaves a
        participation factor of order $10^{-26}$ between the microscopic
        $r_c$ normalization and the calibrated $\rhoF$; see
        Subsection~\ref{subsec:rt_twist_rotor_participation_audit}.  Neither an
        equivalent millimetre length nor a fitted participation factor may be
        cited as a predicted coherence length, cell spacing, or physical line
        separation.
```

## Formal Foundations / Circulation Quantization / 

### lines 1415-1423
```latex
        \end{align}
        
        \textbf{[ORTHODOX]}: Circulation quantization appears in superfluid systems.
        
        \textbf{[DERIVED within the calibrated chain]}: In SST, $\Gamma_0$ is no longer an independent input but follows from Eq.~\ref{eq:rc_definition}. Since $\rc$ itself carries the [CALIBRATED CHAIN GUARD] of Subsection~\ref{subsec:derived_horn_circulation_radius}, this derived status is relative to the calibrated primitive set $(\rhoF,\vchar,\omega_c)$; it must not be cited as an independent hydrodynamic derivation of the circulation quantum.
    
\subsection{Bounded-Domain Biot--Savart Admissibility}
        \label{subsec:bounded_domain_biot_savart}

```

## Formal Foundations / Density and Inertia Hierarchy / 

### lines 1701-1713
```latex
        \begin{align}
            \rhoSub
            &\quad \text{(unfixed material substrate density)},
            \\
            \rhoF\equiv\rhoEff
            &\quad \text{(calibrated quasi-static effective response)},
            \\
            \rhoE
            &= \tfrac12 \rhoF \, \vchar{}^2
            \quad \text{(swirl energy density in the effective sector)},
            \\
            \rhoM
            &= \rhoE / c^2
```

### lines 1724-1732
```latex
        \end{align}

        \textbf{[ORTHODOX] Definition}: $\rhoM=\rhoE/c^2$ is the mass-equivalent density associated with the swirl kinetic accounting above; in orthodox limits, total energy $E$ in a region still yields mass density $E/c^2$.

        \textbf{[CANON / NON-IDENTIFICATION]}: Numerical or dimensional agreement between two entries does not identify their physical roles. In particular, $\rhoSub$, $\rhoF$, $\Jomega$, $\muell$, and $\rhohorn$ remain distinct unless a separately labeled constitutive theorem relates them.
    
    \subsection{Horn-Envelope Density Closure}
        
        The density formerly denoted as a ``core density'' is now interpreted as an
```

## Formal Foundations / Reparametrized Zero-Parameter Corollary / 

### lines 1795-1803
```latex

    \subsection{Reparametrized Zero-Parameter Corollary}
        \label{subsec:zero_parameter_corollary}

        Older SST canon layers often used the triplet $(\Gamma_0,\rhoF,\rc)$ as the primitive parameterization. In the present \canonversion{} architecture, Eq.~\eqref{eq:rc_definition} and Eq.~\eqref{eq:gamma0} show that this is a reparameterization of the present primitive calibration set $(\rhoF,\vchar,\omega_c)$ rather than a distinct axiom.

        Explicitly,

        \begin{align}
```

### lines 1805-1818
```latex
            = 2\pi \frac{\vchar{}^2}{\omega_c}.
            \label{eq:gamma0_reparam}
        \end{align}

        Hence any dimensional SST quantity written in terms of $(\Gamma_0,\rhoF,\rc)$ can be rewritten in terms of $(\rhoF,\vchar,\omega_c)$ with no new calibration input.

        A coarse-grained density law retained from earlier canon layers is

        \begin{align}
            \rhoF = K\,\Omega,
            \qquad
            K = \frac{\rhocore \, \rc}{\vchar},
            \label{eq:coarse_grain_density}
        \end{align}
```

## Formal Foundations / Canonical Master Equation / 

### lines 1832-1850
```latex

        First define the local swirl energy density and its mass-equivalent form:

        \begin{align}
            \rhoE(x,t) &= \frac{1}{2}\rhoF\,\norm{\uswirl(x,t)}^2 \\
            \rhoM(x,t) &= \frac{\rhoE(x,t)}{c^2}
        \end{align}

        \textbf{[CANON / CONSTANT-RESPONSE GUARD].}
        In Eq.~\eqref{eq:sst_master_equation}, spatial and temporal variation
        resides in $\uswirl(x,t)$ and in the explicitly local derived fields;
        $\rhoF\equiv\rhoEff$ is the calibrated quasi-static response coefficient.
        A dispersive or inhomogeneous effective response must be introduced as a
        distinct object such as $\rho_{\rm eff}(\omega,\mathbf k;\mathbf x,t)$.
        It must not be represented by silently promoting $\rhoF$ to a local
        material-density field.

        Using Eq.~\ref{eq:swirl_clock}, the local Swirl-Clock factor is

```

### lines 1903-1911
```latex
        The canonical SST master equation is therefore
        \begin{align}
            M_K(x,t)
            &= \rhoM(x,t)\,\rc^3\,\Pi_K\,\Xi_K\,\SwirlClock(x,t)^{-2} \\
            &= \left( \frac{\rhoF\,\norm{\uswirl(x,t)}^2}{2c^2} \right)
               \rc^3
               \left( \frac{\lambda_c}{\pi \rc} \right)^{G(K)}
               \left[ \alpha_C\,C(K) + \beta_L\,L(K) + \gamma_H\,\mathcal{H}(K) \right]
               \varphi^{-2k(K)}
```

### lines 1919-1927
```latex
        \end{align}

        \textbf{[DERIVED] Dimensional check}:
        \begin{align}
            \left[ \frac{\rhoF\,\norm{\uswirl}^2}{c^2} \rc^3 \right] = \mathrm{kg}
        \end{align}
        and all remaining factors are dimensionless, so Eq.~\ref{eq:sst_master_equation} has the correct mass dimension.

        \textbf{[CANON / SEMANTIC RULE]}: the factor \(\rc^3\) in Eq.~\eqref{eq:sst_master_equation} is a canonical horn/envelope normalization volume scale. It is not a resolved physical tube volume unless a separate model sets \(a_{\rm core}=\rc\). Resolved tube energies, cutoffs, and local vorticity estimates must use \(a_{\rm core}\) or an explicit profile.
```

## Formal Foundations / Summary of Dependency Structure / 

### lines 1957-1965
```latex
        
        The full dependency chain is:
        
        \begin{align}
        (\rhoF, \vchar, \omega_c)
            \rightarrow \rc
            \rightarrow \Gamma_0
            \rightarrow (\rhoE, \rhoM, \rhocore)
            \rightarrow \SwirlClock
```

## Formal Foundations / Maximal Swirl Tension / 

### lines 1991-1999
```latex
    \label{sec:Fmax}

        \subsubsection{Definition and canonical form}

        Within the primitive calibration set $\mathcal{P}_{\mathrm{cal}} = \{\rhoF, \vchar, \omega_c\}$, a characteristic force scale emerges naturally from the Compton energy stored over the canonical circulation cross-section. We define the \emph{maximal swirl tension} as

        \begin{align}
            F_{\rm swirl}^{\max}
            \;=\; \frac{\vchar\,\hbar}{2\rc^2}
```

## Axiomatic Framework / Axiom 1: Continuum Substrate / 

### lines 2201-2212
```latex
        All physical structures arise as configurations within this medium; no discrete particles are assumed at the fundamental level.

        \textbf{[CANON / LEVEL-SEPARATION GUARD].}
        Axiom~1 does not numerically identify $\rhoSub$ with the calibrated
        effective response $\rhoF\equiv\rhoEff$.  Equations written with
        $\rhoF$ in the current Canon are long-wavelength effective-sector
        equations unless a resolved material-density model is supplied.  Any
        future equality $\rhoSub=\rhoF$ requires an independent homogenization
        or response theorem.
    
    \subsection{Axiom 2: Existence of Stable Vortex Filaments}
        
```

## Swirl--Electromagnetic Bridge / Minimal transverse field sector / 

### lines 3017-3025
```latex

        \begin{align}
            \mathcal{L}_{\mathrm{rad}}
            =
            \frac{\rhoF}{2}\,\lVert \partial_t \mathbf{A}_{\mathrm{eff}}\rVert^2
            -
            \frac{K_\gamma}{2}\,\lVert \nabla\times\mathbf{A}_{\mathrm{eff}}\rVert^2.
            \label{eq:rad_lagrangian}
        \end{align}
```

### lines 3028-3036
```latex

        \begin{align}
            \frac{1}{c_\gamma^2}\partial_t^2 \mathbf{A}_{\mathrm{eff}} - \nabla^2 \mathbf{A}_{\mathrm{eff}} = 0,
            \qquad
            c_\gamma^2 = \frac{K_\gamma}{\rhoF}.
            \label{eq:vector_wave_Aeff}
        \end{align}

        \textbf{[CANONICAL FOUNDATIONAL IDENTIFICATION].}
```

### lines 3042-3055
```latex
        Within the quadratic bridge model this fixes the target stiffness
        \begin{align}
            K_\gamma
            =
            \rhoF c^2
            =
            6.3\times10^{10}\ \mathrm{Pa}.
            \label{eq:r_phase_torsion_stiffness_target}
        \end{align}
        Equation~\eqref{eq:r_phase_torsion_stiffness_target} is dimensionally a shear/torsion stiffness target. Here $\rhoF\equiv\rhoEff$ is the quasi-static inertial coefficient of the displacement field $\mathbf A_{\mathrm{eff}}$, not the unresolved material density $\rhoSub$. Substituting the measured value of~\(c\) calibrates the bridge; it is not yet a microscopic derivation of~\(K_\gamma\).

        \textbf{[NO-ACOUSTIC-MODE GUARD].}
        The speed \(c_\gamma\) is not an ordinary sound speed. In the exact incompressible SST substrate, density compression is excluded and pressure enforces a constraint on each foliation slice. The luminal branch belongs to the independent transverse torsion/director sector represented by \(\mathbf A_{\mathrm{eff}}\) \cite{BarceloLiberatiVisser2026}.

```

## Swirl--Electromagnetic Bridge / Swirl pressure law / 

### lines 3182-3220
```latex

        For steady axisymmetric swirl, Euler radial balance gives

        \begin{align}
            \frac{1}{\rhoF}\frac{dp_{\mathrm{swirl}}}{dr} = \frac{v_\theta(r)^2}{r}.
            \label{eq:swirl_pressure_law}
        \end{align}

        For a locally rigid rotation profile $v_\theta(r)=\Omega r$, Eq.~\eqref{eq:swirl_pressure_law} integrates to

        \begin{align}
            p_{\mathrm{swirl}}(r) = p_0 + \frac{1}{2}\rhoF \Omega^2 r^2,
            \label{eq:swirl_pressure_rigid}
        \end{align}

        while for an exterior irrotational profile $v_\theta(r)=\Gamma/(2\pi r)$ one finds

        \begin{align}
            p_{\mathrm{swirl}}(r) = p_\infty - \frac{\rhoF\Gamma^2}{8\pi^2 r^2}.
            \label{eq:swirl_pressure_irrotational}
        \end{align}

        In a flat rotation curve with asymptotically constant azimuthal speed $v_\theta(r)\to v_0$ as $r$ grows in a window where the radial balance \eqref{eq:swirl_pressure_law} remains valid, integration yields the logarithmic tail
        \begin{align}
            p_{\mathrm{swirl}}(r)
            =
            p_0 + \rhoF v_0^2 \ln\!\left(\frac{r}{r_0}\right),
            \label{eq:swirl_pressure_flat_tail}
        \end{align}
        for suitable reference radius $r_0$ and offset $p_0$ within that window.

        \textbf{[ORTHODOX] Assumption block:} Eq.~\eqref{eq:swirl_pressure_law} is taken in the usual incompressible, inviscid, stationary, axisymmetric regime with azimuthal-dominant flow, so that radial drift, viscosity, and stratification corrections are subleading in the domain of validity.

        \textbf{[ORTHODOX] Dimensional check:}
        $\bigl[\rhoF^{-1}\,dp/dr\bigr]=\mathrm{m\,s^{-2}}=\bigl[v_\theta^2/r\bigr]$.

        \textbf{[ORTHODOX]}: Eq.~\eqref{eq:swirl_pressure_law} is the ordinary radial Euler balance for steady swirl \cite{Batchelor1967,Saffman1992}.

        \textbf{[DERIVED SST ROLE]}: this pressure law is the canonical bridge between localized circulation and large-scale force analogies. Interpreting $p_{\mathrm{swirl}}$ as a dark-sector classifier or support layer is an SST model step, logically separate from the orthodox fluid derivation.
```

## Swirl--Electromagnetic Bridge / Lorentz-Type Force Density as Swirl Stress / Status labels.

### lines 3228-3236
```latex
        The vector identity used in this section is \textbf{[ORTHODOX]}.  The
        definition of the swirl-force density is \textbf{[DERIVED]} as a hydrodynamic
        force-density structure.  The numerical SST scales are \textbf{[CALIBRATED]}
        with respect to the canonical constants
        \(\rhoF\), \(\rc\), and \(\vchar\).
        No microscopic electromagnetic element-force law is canonized here.

        \paragraph{Hydrodynamic identity.}
        For incompressible inviscid flow,
```

## Swirl--Electromagnetic Bridge / Lorentz-Type Force Density as Swirl Stress / Swirl-force density.

### lines 3265-3278
```latex
        \[
        \boxed{
        \mathbf f_{\circlearrowleft}
        =
        \rhoF\mathbf v\times\boldsymbol{\omega}.
        }
        \]
        Its dimensional consistency is
        \[
        [\rhoF\mathbf v\times\boldsymbol{\omega}]
        =
        \mathrm{kg\,m^{-3}}\,
        \mathrm{m\,s^{-1}}\,
        \mathrm{s^{-1}}
```

## Swirl--Electromagnetic Bridge / Lorentz-Type Force Density as Swirl Stress / Bernoulli relation and sign convention.

### lines 3285-3312
```latex
        The scalar quantity
        \[
        p_{\circlearrowleft}
        =
        \frac12\rhoF|\mathbf v|^2
        \]
        is the dynamic swirl-pressure scale.  It should not be confused with the
        static pressure, which decreases in high-swirl regions in the usual
        Bernoulli sense.  For stationary Euler flow with constant
        \(\rhoF\) and no external body force,
        \[
        \rhoF(\mathbf v\cdot\nabla)\mathbf v
        =
        -\nabla p_{\mathrm{stat}} .
        \]
        Using the identity above gives
        \[
        \boxed{
        \rhoF\mathbf v\times\boldsymbol{\omega}
        =
        \nabla\!\left(
        p_{\mathrm{stat}}
        +
        \frac12\rhoF|\mathbf v|^2
        \right).
        }
        \]
        Thus the swirl-force density is canonically tied to the gradient of total
```

## Swirl--Electromagnetic Bridge / Lorentz-Type Force Density as Swirl Stress / Canonical scales.

### lines 3354-3362
```latex
        \rc
        =
        1.40897017\times10^{-15}\,\mathrm m,
        \qquad
        \rhoF
        =
        7.0\times10^{-7}\,\mathrm{kg\,m^{-3}},
        \]
        the natural circulation scale is
```

### lines 3370-3378
```latex
        The associated dynamic swirl-pressure scale is
        \[
        p_{\circlearrowleft,0}
        =
        \frac12\rhoF\vchar{}^2
        =
        4.1877439\times10^{5}\,\mathrm{Pa}.
        \]
        This value is the canonical SST stress scale for Lorentz-type
```

## Swirl--Electromagnetic Bridge / Lorentz-Type Force Density as Swirl Stress / Canonical conclusion.

### lines 3386-3399
```latex
        \[
        \boxed{
        \mathbf f_{\circlearrowleft}
        =
        \rhoF\mathbf v\times\boldsymbol{\omega}
        =
        \rhoF
        \nabla\!\left(\frac12|\mathbf v|^2\right)
        -
        \rhoF(\mathbf v\cdot\nabla)\mathbf v .
        }
        \]
        Accordingly, magnetic-type force densities in SST are interpreted as
        effective projections of pressure, vorticity, and closed-loop topology in the
```

## Spectroscopic Constraints / Precision electroweak bridge: lessons from the CMS \texorpdfstring{$W$ / Latent-to-observable map.

### lines 3859-3867
```latex
                \chi_W,\,
                \mathcal{L}_W,\,
                \mathcal{H}_W,\,
                \SwirlClock_W,\,
                \rhoF^{\rm eff},\,
                \uswirl^{\rm eff}
                \Bigr),
            \end{equation}
            where:
```

### lines 3870-3878
```latex
                \item $\chi_W$ is chirality / handedness label,
                \item $\mathcal{L}_W$ is an effective geometric length scale,
                \item $\mathcal{H}_W$ is a helicity/linkage content,
                \item $\SwirlClock_W$ is the local clock factor for the mode,
                \item $\rhoF^{\rm eff}$ and $\uswirl^{\rm eff}$ are the coarse-grained medium density and effective local swirl-velocity field seen by the excitation.
            \end{itemize}
            
            The experimentally accessible distribution is then not a bare function of $m_W$ alone, but a projected density
            \begin{equation}
```

## Relational Time Framework / Canonical Electromagnetic--Gravity Closure / Gravity projection.

### lines 4663-4671
```latex

        The canonical pressure anchor remains the incompressible Euler radial balance
        \begin{align}
            \boxed{
            \frac{1}{\rhoF}\frac{dp_{\mathrm{swirl}}}{dr}
            =
            \frac{v_\theta(r)^2}{r}.
            }
            \label{eq:canonical_emg_euler_anchor}
```

## Relational Time Framework / Canonical Electromagnetic--Gravity Closure / Numerical hierarchy.

### lines 4769-4777
```latex

        \paragraph{Numerical hierarchy.}
        At the canonical speed \(\vchar=1.09384563\times10^6\,\mathrm{m\,s^{-1}}\),
        \begin{align}
            \frac{1}{2}\rhoF\vchar{}^2
            &=
            4.1877439\times10^5\,\mathrm{Pa},
            \\
            \SwirlClock
```

## Relational Time Framework / Triadic Gravity-Response Corollary / Local Euler locking of pressure and optical projections.

### lines 4850-4863
```latex
        The three modes may share a common source state but are not mutually identical.

        \paragraph{Local Euler locking of pressure and optical projections.}
        Under the additional assumptions of a passive, stationary, inviscid Euler
        region with constant \(\rhoF\), the pressure and optical projections are not
        independent.  Bernoulli reconstruction gives
        \begin{align}
            \delta p_{\mathrm{swirl}}
            =
            -\frac{1}{2}\rhoF\lVert\uswirl\rVert^2,
        \end{align}
        while the clock/optical closure gives
        \begin{align}
            n_\gamma
```

### lines 4874-4882
```latex
        \begin{align}
            \boxed{
            \delta n_\gamma
            =
            -\frac{\delta p_{\mathrm{swirl}}}{\rhoF c^2}
            }
            \label{eq:canonical_pressure_optical_locking}
        \end{align}
        with validity restricted to the passive Euler regime.  Forcing, damping,
```

### lines 4886-4900
```latex
        model.  Thus the refined diagnostic statement is not three fully independent
        channels, but two locally locked projections plus one nonlocal Poisson/bulk
        response whenever Eq.~\eqref{eq:canonical_weak_gravity_closure} is invoked.

        With \(\rhoF=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}\),
        \begin{align}
            \frac{1}{\rhoF c^2}
            &=
            1.58950008\times10^{-11}\,\mathrm{Pa^{-1}},
            \\
            \frac{1}{2}\rhoF\vchar{}^2
            &=
            4.1877439\times10^5\,\mathrm{Pa},
            \\
            \delta n_\gamma
```

## Integration of Prior Canon Versions / Retained from the early canon layers / 

### lines 5156-5164
```latex

    \subsection{Retained from the early canon layers}
        From the v0.1.x--v0.3.x line, the present canon retains the primitive closure logic:
        \begin{itemize}
            \item a continuum substrate with unfixed material density $\rhoSub$, represented in the current long-wavelength sector by the calibrated effective response $\rhoF\equiv\rhoEff$,
            \item a core scale $r_c$ fixed by Compton anchoring,
            \item circulation quantization through $\Gamma_0 = 2\pi \rc \, \vchar$,
            \item the interpretation of matter as stable organized structures rather than point primitives.
        \end{itemize}
```

## Integration of Prior Canon Versions / Notation and density cleanup / 

### lines 5190-5198
```latex
        \begin{align}
            \rhoSub
            &\quad \text{unfixed material substrate density},
            \nonumber\\
            \rhoF\equiv\rhoEff
            &\quad \text{calibrated quasi-static effective inertial response},
            \nonumber\\
            \Jomega
            &\quad \text{rotational/twist microinertia density},
```

### lines 5215-5223
```latex
        \end{align}
        Any older passage that identifies a single symbol with more than one of
        these roles is superseded by the present separation.  In particular, the
        historical decimal $7\times10^{-7}$ does not establish an equality between
        $\Jomega$ in $\mathrm{kg\,m^{-1}}$ and $\rhoF$ in
        $\mathrm{kg\,m^{-3}}$.

    \subsection{Topology-first reinterpretation of layers}
        A major consolidation from the recent lepton and knot-mass program is the separation between topology and layering. Knot type is retained as the primary identity label, while Golden-layer or thermal ladder indices are treated as dressing or coherence variables rather than species-defining labels. This prevents the canon from over-reading numerical layer fits as ontological identities.
```

## Integration of Prior Canon Versions / Hydrodynamic Exchange and the Pauli Barrier / 

### lines 5550-5558
```latex
        incompressible medium, the Biot--Savart interaction energy is \cite{Batchelor1967}
        \begin{align}
            E_{\mathrm{int}}
            =
            \frac{\rho_{\!f}\Gamma_1\Gamma_2}{4\pi}
            \oint_{C_1}\oint_{C_2}
            \frac{d\mathbf{l}_1\cdot d\mathbf{l}_2}
            {\lVert \mathbf{r}_1 - \mathbf{r}_2 \rVert}.
            \label{eq:biot_savart_interaction}
```

### lines 5561-5569
```latex
        \textbf{[ORTHODOX]} Regularized filament-energy template: if two identical electron-candidate loops are forced into the same spatial state, a short-distance cutoff \(a_{\rm cut}\) gives the overlap penalty
        \begin{align}
            V_{\mathrm{Pauli}}(\mathbf{d};a_{\rm cut})
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}
            \oint\!\!\oint
            \frac{d\mathbf{l}_1\cdot d\mathbf{l}_2}
            {\sqrt{\lVert \mathbf{r}_1(\theta_1)-\mathbf{r}_2(\theta_2)+\mathbf{d}\rVert^2+a_{\rm cut}^2}},
            \label{eq:pauli_barrier_regularized}
```

### lines 5571-5585
```latex
        with maximal-overlap scale
        \begin{align}
            V_{\mathrm{Pauli}}^{\max}(a_{\rm cut})
            \approx
            \frac{\rho_{\!f}\Gamma_0^2}{4\pi}\left(\frac{L}{a_{\rm cut}}\right)\mathcal{O}(1).
            \label{eq:pauli_barrier_scale}
        \end{align}

        Using the canonical values
        \begin{align}
            \rho_{\!f} &= 7.0 \times 10^{-7}\ \mathrm{kg\,m^{-3}}, \nonumber\\
            r_c &= 1.40897017 \times 10^{-15}\ \mathrm{m}, \nonumber\\
            \Gamma_0 &= 2\pi r_c \vchar
            \approx 9.6836\times 10^{-9}\ \mathrm{m^2\,s^{-1}},
        \end{align}
```

## Integration of Prior Canon Versions / Numerical Benchmark Layer / 

### lines 5634-5642
```latex
            \item mode definitions (predictive vs.\ exact-closure),
            \item uncertainty propagation on canonical constants and geometric factors,
            \item theorem-style pass/fail metadata (including tail-quality checks, postchecks, and extrapolation summaries),
            \item explicit separation between practical best-estimate closure and theorem-level closure,
            \item normalization of legacy constant names into SST notation (\(\rhoF,\rc,\Gamma_0\)) while preserving numerical values.
        \end{itemize}

        This requirement is included to keep the benchmark layer falsifiable and reproducible, rather than merely illustrative.

```

## Discussion and Limits / What is established at canon level / 

### lines 5708-5716
```latex

    \subsection{What is established at canon level}
        The present document supports the following as canon-level structures:
        \begin{itemize}
            \item the primitive constant chain $(\rhoF, v_{\swirlarrow}, \omega_c) \to R_{\mathrm{horn}}\equiv r_c \to \Gamma_0$,
            \item the Swirl-Clock as the coarse-grained relational time factor,
            \item delay-induced mode selection as the preferred discreteness mechanism,
            \item the atomic bridge and spectroscopic sectors as compatibility filters,
            \item the topology-first program for mass organization.
```

## Historical Notebook and Proto-Canon Provenance Register / High-priority source concordance / 

### lines 5858-5866
```latex
    \texttt{NB2012-P044--P055} & Circulation, vortices, toroidal cores, and time/mass associated with rotation. & Euler-vorticity sector, finite-thickness carrier geometry, and relational clock response. \\
    \texttt{NB2012-P069--P071} & Oscillator propagation speed, capacitance, vacuum response, and constant dependencies. & Link inertia/stiffness, constitutive response, impedance, and non-circularity ledger. \\
    \texttt{NB2013-P010/P019/P045} & Transition dynamics, caution about numerical closure, and relative-rotation/time interpretation. & Transition-action research programme, calibration guard, and observer-dependent kinematics. \\
    \texttt{DOC2013-CANON-001} & First coherent constant-chain and excitation model. & Historical bridge only; inputs and algebra are audited before any prediction claim. \\
    \texttt{VAM7-DENSITY-2025} & Electron energy assigned to $\omega=\alpha\omega_c$ over $r_e^3/3$, producing the inherited decimal. & Reclassified as $\Jomega^{\rm VAM}$ with units $\mathrm{kg\,m^{-1}}$; no derivation of $\rhoF$ follows. \\
    \texttt{PROJ2026-KNOTPLOT-RR-001} & Candidate generation, topology verification, constrained tightening, and mesh export. & Bound-mode geometry certification and input domain for a future response/impedance operator. \\
    \bottomrule
    \end{tabularx}
    \end{center}
```

## Topological reference toolkit /  / 

### lines 5887-5895
```latex
            \item Basic torus-knot invariants as needed in the mass program (e.g.\ minimal crossing number, braid index, genus) with fixed naming consistent with Rolfsen notation in the main text.
            \item C\u{a}lug\u{a}reanu--White--Fuller relation $Lk=Tw+Wr$ for framed ribbons (already recalled as Eq.~\eqref{eq:calugareanu} in the integration layer).
        \end{enumerate}

        \textbf{[ORTHODOX]}: each item is classical mathematics \cite{Moffatt1969,White1969,Batchelor1967}. \textbf{[DERIVED]}: scope and notation for v0.8.x are frozen to this list plus house symbols $(\rhoF,\Gamma,\rc,\mathcal{H})$ without parallel aliases.

    \section{Full Derivations}
        \label{sec:appendix_derivations}

```

## Conversation-Derived Insights / Canon edition notes / 

### lines 6073-6097
```latex
            internal twist waves from quadratic Kelvin bending, quantifies the
            unresolved micro--macro participation gap
            $\phi_{\rm dyn}=5.7229\times10^{-26}$ and the equivalent
            normalization length $\ell_{\rho,\rm eq}=5.8897\,\mathrm{mm}$,
            and defines $\rhoF$ exclusively as the quasi-static isotropic limit
            of the effective-inertia response on top of v0.8.30.

        \subsubsection{v0.8.30}
            \textbf{v0.8.30} separates the unfixed material substrate density
            $\rhoSub$ from the calibrated quasi-static effective response
            $\rhoF\equiv\rhoEff$, introduces distinct notation for rotational
            microinertia $\Jomega$ and line inertia $\muell$, corrects the
            historical provenance of the inherited $7\times10^{-7}$ decimal,
            forbids dimensionally invalid $\rhoF|\boldsymbol\omega|^2$ energy
            expressions without a derived squared length, freezes $\rhoF$ as a
            constant response coefficient in the canonical master equation, and
            moves the detailed VAM-7 provenance audit to the Research Track on top
            of v0.8.29.

        \subsubsection{v0.8.29}
            \textbf{v0.8.29} strengthens the provenance guard for the calibrated background density $\rhoF$, distinguishes two-significant-figure notation from a statistical uncertainty model, adds the primitive dependency guard preventing unsupported propagation into $\vchar$, $\omega_c$, $\rc$, or the Compton chain, and audits the research-track cosmological impedance/SSDL route through an explicit epoch-invariance gate, covariance-aware precision guard, exact large-number identity, and force-hierarchy reformulation on top of v0.8.28.

        \subsubsection{v0.8.28}
            \textbf{v0.8.28} adds the action--phase mass--shell clock bridge \(H(P,I)=\sqrt{P^2c^2+E_0^2(I)}\), derives the internal carrier phase rate \(\Omega_0/\gamma\) at fixed momentum, links the low-momentum expansion to the canonical inertia normalization \(M_0=E_0/c^2\), separates translational clock dressing from the internal \(\vchar\) diagnostic, records that no flattening/stretching/core-thinning hypothesis is required, and adds research-track mass-shell, phase-rate, velocity, and shape-stability residuals on top of v0.8.27.

```

### lines 6140-6148
```latex
        \subsubsection{v0.8.13}
            \textbf{v0.8.13} adds the relativity-emergence audit: the internal tensor-speed naturalness proposition (\S\ref{subsec:tensor_speed_naturalness}, conditional $c_{13}=0$) in the main canon, the research-track Relativity Emergence Ladder (\S\ref{sec:rt_relativity_emergence_ladder}) separating derivable SR/GR kinematics from the open Einstein-dynamics program, and relativity/induced-gravity/cosmology bibliography on top of v0.8.12.

        \subsubsection{v0.8.12}
            \textbf{v0.8.12} applies the Gemini round-3 epistemic audit: $\mathcal{P}_{\mathrm{cal}}$-aligned identity relabels, coarse-grain density caveat, Pauli $a_{\rm cut}$ disambiguation, galaxy-scale $\rhoF$ note, and research-track EM-bridge limits on top of v0.8.11.

        \subsubsection{v0.8.11}
            \textbf{v0.8.11} completes the final hygiene pass: consistent $\mathcal{P}_{\mathrm{cal}}$, $\vchar$ vs.\ $\uswirl$ usage in EMG, framed self-linking, W-boson sector, and research-track numerical bridges on top of v0.8.10.

```

## Conversation-Derived Insights / Trefoil closure and persistence discipline / Domain-spectral helicity optimization guard.

### lines 6432-6440
```latex
        \end{align}
        If $\mathbf V=\boldsymbol\omega$, the denominator in
        Eq.~\eqref{eq:canon_isoperimetric_spectral_equivalence} is enstrophy,
        not the SST kinetic energy
        $\tfrac12\rhoF\int|\uswirl|^2d^3x$.  The two optimization problems must
        not be identified without an explicit constitutive relation.

        A smooth global optimizer over all fixed-volume domains would have
        nonzero constant $|\mathbf V|$ on each boundary component, toroidal
```

## Effective Quantum Bridge / Purpose and status / 

### lines 6717-6725
```latex
        \textbf{[DERIVED]} SST may use these formulas as a coarse-grained field representation once a local amplitude density and phase have been specified.
        
        \textbf{[SPECULATIVE]} The identification of the resulting fields with branch-resolved swirl carriers remains an SST interpretation.

        \textbf{[CRITICAL NOTE]}: $\rho_\psi$ is a coarse-grained mode-support density of the emergent carrier field, \emph{not} a compression of the incompressible material substrate $\rhoSub$ (Axiom~1, $\nabla\cdot\mathbf v=0$). It is also distinct from the calibrated quasi-static response $\rhoF\equiv\rhoEff$. These are different objects, so the Madelung amplitude does not violate substrate incompressibility.
    
    \subsection{Amplitude--phase decomposition}
        Introduce an effective complex mode field
        \begin{align}
```

## Dark-Sector and Galactic Continuum Law / Purpose and status / 

### lines 6817-6825
```latex
        \textbf{[DERIVED]} SST reinterprets that balance as a candidate large-scale acceleration source.
        
        \textbf{[SPECULATIVE]} The explicit galaxy-fit profile below is a phenomenological closure ansatz, not a theorem.

        \textbf{[CRITICAL NOTE]} The canonical \(\rhoF=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}\) is an effective medium parameter, not an ordinary gravitating baryonic/cosmological rest-mass density. Applying it on galactic scales requires a separate coupling and screening law. Without that law, the galaxy-scale pressure profile is a fit ansatz only and must not be interpreted as a literal dense fluid through which stars experience ordinary hydrodynamic drag.
    
    \subsection{Effective dark acceleration law}
        Starting from the steady radial pressure law of Eq.~\eqref{eq:swirl_pressure_law},
        \begin{align}
```

## Dark-Sector and Galactic Continuum Law / Effective dark acceleration law / 

### lines 6822-6838
```latex
    
    \subsection{Effective dark acceleration law}
        Starting from the steady radial pressure law of Eq.~\eqref{eq:swirl_pressure_law},
        \begin{align}
            \frac{1}{\rhoF}\frac{dp_{\mathrm{swirl}}}{dr}
            =
            \frac{v_\theta(r)^2}{r},
        \end{align}
        define the effective SST acceleration by
        \begin{align}
            a_{\mathrm{SST}}(r)
            :=
            \frac{1}{\rhoF}\frac{dp_{\mathrm{swirl}}}{dr}.
            \label{eq:appendix_dark_accel}
        \end{align}
        Then
        \begin{align}
```

# SST_CANON-v0.8.31-research-track.tex

## Dark-sector and galactic canonization execution package (v0.8.x) / Stage-0 freeze: topology toolkit and benchmark protocol / 

### lines 318-326
```latex
\end{enumerate}

\textbf{[DERIVED] Notation freeze:} one notation family is used in this package:
\[
\rhoF,\quad v_\theta(r),\quad p_{\mathrm{swirl}}(r),\quad
\mathcal{H}(K),\quad N_u^{(1)}(K),\quad \Gamma,\quad \kappa,\quad \SwirlClock.
\]
No parallel symbol aliases are introduced for the same quantity.

```

## Dark-sector and galactic canonization execution package (v0.8.x) / Stage-1 freeze: dark-sector Euler pressure anchor / 

### lines 337-345
```latex

\subsection{Stage-1 freeze: dark-sector Euler pressure anchor}
\textbf{[ORTHODOX] Euler radial balance (steady, axisymmetric, azimuthal-dominant):}
\begin{align}
    \frac{1}{\rhoF}\frac{dp_{\mathrm{swirl}}}{dr}
    =
    \frac{v_\theta(r)^2}{r}.
    \label{eq:exec_swirl_pressure}
\end{align}
```

### lines 349-365
```latex
    v_\theta(r)\to v_0
    \quad\Longrightarrow\quad
    p_{\mathrm{swirl}}(r)
    =
    p_0 + \rhoF v_0^2\ln\!\left(\frac{r}{r_0}\right).
\end{align}

\textbf{[DERIVED] Assumption block:}
incompressible, inviscid, stationary, axisymmetric, azimuthal-dominant flow, with validity restricted to regions where radial drift and stratification corrections are subleading.

\textbf{[DERIVED] Dimensional check:}
\[
\left[\frac{1}{\rhoF}\frac{dp}{dr}\right]
=
\frac{\mathrm{kg\,m^{-2}\,s^{-2}}}{\mathrm{kg\,m^{-3}}}
=
\mathrm{m\,s^{-2}}
```

### lines 369-377
```latex

\textbf{[SPECULATIVE] SST interpretation:}
Eq.~\eqref{eq:exec_swirl_pressure} is interpreted as a classifier/driver layer for dark-sector support. This interpretation is model-level and separate from the orthodox derivation.

\textbf{[CRITICAL NOTE]}: Applying Eq.~\eqref{eq:exec_swirl_pressure} unscreened with the microscopic $\rhoF=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}$ at galactic scales ($v_\theta\sim200\,\mathrm{km\,s^{-1}}$, $r\sim10\,\mathrm{kpc}$) gives $dp/dr\sim10^{-16}\,\mathrm{Pa\,m^{-1}}$ and $\Delta p\sim2.8\times10^{3}\,\mathrm{Pa}$ over $1\,\mathrm{kpc}$, far above the observed ISM. The swirl pressure is not the thermal ISM pressure, but no screening/scaling law for $\rhoF$ across scales is yet derived; this sector stays research-track and is falsifiable on exactly this point.

\textbf{[DERIVED] Attached observables/falsifiers:}
\begin{enumerate}
    \item Rotation-curve consistency after pressure reconstruction from archived $v_\theta(r)$ data.
```

## Candidate CANON-v0.8.x Modules from Swirl-Flux, Envelope, and Reconnection Analysis /  / 

### lines 484-492
```latex
    \providecommand{\vswirl}{\mathbf{v}_{\!\swirlarrow}}
\providecommand{\vchar}{v_{\!\boldsymbol{\circlearrowleft}}^{\ast}}
\providecommand{\uswirl}{\mathbf{u}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\omegaswirl}{\boldsymbol{\omega}_{\!\boldsymbol{\circlearrowleft}}}
    \providecommand{\rhoF}{\rho_{\!f}}
    \providecommand{\rhoE}{\rho_{\!E}}
    \providecommand{\rhoM}{\rho_{\!m}}
    \providecommand{\rhocore}{\rho_{\mathrm{core}}}
    \providecommand{\rc}{r_c}
```

## Candidate CANON-v0.8.x Modules from Swirl-Flux, Envelope, and Reconnection Analysis / R/T Pseudomomentum--Impulse Exchange / 

### lines 695-703
```latex
        \(\mathbf I_T\) denotes T-phase vorticity impulse,
        \[
            \mathbf I_T
            =
            \frac{\rhoF}{2}
            \int_{\Omega}
            \mathbf x\times\boldsymbol\omega\,d^3x .
        \]
        The dimension is
```

### lines 711-719
```latex
        For a thin circular swirl string of circulation \(\Gamma\) and radius \(R\),
        \[
            \mathbf I_T
            =
            \rhoF\Gamma\pi R^2\hat{\mathbf n}.
        \]
        The core circulation scale is
        \[
            \Gamma_0
```

## Candidate CANON-v0.8.x Modules from Swirl-Flux, Envelope, and Reconnection Analysis / Spherical Pressure Envelopes / 

### lines 787-801
```latex
        For inviscid incompressible SST flow,
        \[
            \nabla p_{\mathrm{SST}}
            =
            \rhoF(\mathbf v\cdot\nabla)\mathbf v .
        \]
        For an azimuthal swirl profile \(v_\theta(r)\),
        \[
            \frac{dp}{dr}
            =
            \rhoF\frac{v_\theta^2(r)}{r}.
        \]
        If
        \[
            v_\theta(r)=\frac{\Gamma}{2\pi r},
```

### lines 803-834
```latex
        then
        \[
            \frac{dp}{dr}
            =
            \rhoF\frac{\Gamma^2}{4\pi^2r^3},
        \]
        and hence
        \[
            p(r)
            =
            p_\infty
            -
            \frac{\rhoF\Gamma^2}{8\pi^2r^2}.
        \]
        Therefore
        \[
            \Delta p(r)
            =
            p_\infty-p(r)
            =
            \frac{\rhoF\Gamma^2}{8\pi^2r^2}
            =
            \frac{1}{2}\rhoF v_\theta^2(r).
        \]
        
        At the canonical swirl speed,
        \[
            \frac{1}{2}\rhoF\vchar{}^2
            =
            4.18774392\times10^5\,\mathrm{Pa}.
        \]
        At the core-density stress scale,
```

## Candidate CANON-v0.8.x Modules from Swirl-Flux, Envelope, and Reconnection Analysis / Non-Holonomic Gravity Claims / 

### lines 961-969
```latex

% Safe local macro guards; harmless if the Canon preamble already defines these.
\providecommand{\swirlarrow}{\mathchoice{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowleft}}{\mkern-2mu\scriptscriptstyle\boldsymbol{\circlearrowleft}}}
\providecommand{\vswirl}{\mathbf{v}_{\!\swirlarrow}}
\providecommand{\rhoF}{{\rho_{\!f}}}
\providecommand{\rhoE}{\rho_{\!E}}
\providecommand{\rhoM}{\rho_{\!m}}
\providecommand{\rc}{{r_c}}
\providecommand{\vchar}{v_{\!\boldsymbol{\circlearrowleft}}^{\ast}}
```

## Mode-Locked Swirl-Coil Excitation and \texorpdfstring{$\vchar=f\Delta x$ / Canonical interpretation / 

### lines 1251-1263
```latex
The relevant energy-density comparison is
\begin{equation}
\rhoE
=
\frac{1}{2}\rhoF \vnorm^2.
\end{equation}
Using
\[
\rhoF = 7.0\times10^{-7}\,\mathrm{kg\,m^{-3}},
\qquad
\vnorm = 1.09384563\times10^{6}\,\mathrm{m\,s^{-1}},
\]
one obtains
```

## Research Appendices: Topology, Stability, and Fluid Mechanics / Research Appendix: Reconnection Decay as a Stability Falsifier / Energetic jump condition.

### lines 1755-1770
```latex
where $E_{\rm b}^{ij}$ is the local core-contact or phase-slip barrier. A useful leading slender-tube scale is
\begin{equation}
    E_{\rm tube}(K)
    \simeq
    \frac{\rhoF\Gamma_0^2}{4\pi}\,
    \ell_K
    \ln\!\left(\frac{R_{\rm out}}{a_{\rm rec}}\right).
    \label{eq:sst_slender_tube_energy_hitting}
\end{equation}
The units are
\begin{equation}
    [\rhoF\Gamma_0^2\ell_K]
    =
    \left(\frac{\rm kg}{{\rm m}^3}\right)
    \left(\frac{{\rm m}^4}{{\rm s}^2}\right)
    ({\rm m})
```

## Research Appendices: Topology, Stability, and Fluid Mechanics / Research Appendix: Reconnection Decay as a Stability Falsifier / Falsification rule.

### lines 1826-1839
```latex
For a slender swirl tube, the standard leading envelope energy scale is
\begin{equation}
    E_{\rm tube}(K)
    \simeq
    \frac{\rhoF\Gamma^2}{4\pi}\,\ell_K\ln\!\left(\frac{R}{\rc}\right),
    \label{eq:slender_tube_energy_scale}
\end{equation}
where $\Gamma$ is circulation, $\ell_K$ is centerline length, and $R$ is the outer cutoff. The units check:
\begin{equation}
    [\rhoF\Gamma^2\ell_K]
    = \frac{\mathrm{kg}}{\mathrm m^3}\frac{\mathrm m^4}{\mathrm s^2}\mathrm m
    = \mathrm{kg}\,\mathrm m^2\mathrm s^{-2}=\mathrm J.
\end{equation}

```

## Research Appendices: Topology, Stability, and Fluid Mechanics / Research Appendix: Topological Fluid Mechanics and the SST Energy Functional / Falsifier.

### lines 2071-2079
```latex
For a slender swirl tube, the leading hydrodynamic energy scale is
\begin{equation}
    E_{\rm env}
    \simeq
    \frac{\rhoF\Gamma^2}{4\pi}\,\ell_K\ln\!\left(\frac{R}{\rc}\right),
    \label{eq:env_energy_tfm}
\end{equation}
where $\ell_K$ is the tube centerline length. The core contribution can be represented by a line-tension term
\begin{equation}
```

### lines 2083-2091
```latex
Near contacts and curvature corrections may be encoded by
\begin{equation}
    E_{\rm geom}[K]
    =T_{\rm core}\ell_K
    +\frac{\rhoF\Gamma^2}{4\pi}\ell_K\ln\!\left(\frac{R}{\rc}\right)
    +\beta_{\kappa}\int_K \kappa_s^2\,ds
    +\beta_{\rm nc}\,C_{\rm near}(K).
    \label{eq:geometric_energy_functional}
\end{equation}
```

## Research Appendices: Topology, Stability, and Fluid Mechanics / Research Appendix: Topological Fluid Mechanics and the SST Energy Functional / Energy-symbol guard.

### lines 2142-2150
```latex
$\mathscr E_V$ is enstrophy while
\begin{align}
    E_{\rm kin}
    =
    \frac{\rhoF}{2}\int_{\Omega}|\uswirl|^2d^3x
    \label{eq:rt_isoperimetric_kinetic_energy_guard}
\end{align}
is kinetic energy.  Maximizing helicity per enstrophy is not automatically the
same problem as minimizing SST rest energy at fixed helicity.  Any use of
```

## Research Appendices: Topology, Stability, and Fluid Mechanics / Research Appendix: Topological Fluid Mechanics and the SST Energy Functional / Operational diagnostics.

### lines 2254-2262
```latex
\subsubsection{Canon discipline}
The functional in Eq.~\eqref{eq:tfm_to_sst_eff} should be used as follows:
\begin{enumerate}
    \item \textbf{[ORTHODOX]} Use $\Gamma$, $\mathcal H$, $Lk$, writhe, twist, and ropelength as established geometric/topological descriptors.
    \item \textbf{[DERIVED]} Within a chosen tube model, derive the units and leading energy scaling from $\rhoF$, $\Gamma$, $\ell_K$, and $\rc$.
    \item \textbf{[SPECULATIVE]} Only after this, map a relaxed topological class to an SST particle sector.
\end{enumerate}

\subsection{Research Appendix: Resolved-Tube Criticality and Contact-Stress Geometry}
```

## Research-Track particle and clock ansatz / Resolved finite-core energy functional / 

### lines 3744-3752
```latex
self-induction energy.  It may be represented generally as
\begin{equation}
E_{\rm SI}^{(a)}
=
\frac{\rhoF\Gamma_K^2}{8\pi}
\oint_{\gamma_K}
\oint_{\gamma_K}
\bm{t}(s)\cdot\bm{t}(s')\,
\mathcal{K}_{a_{\rm core}}
```

## Research Track: KAM-Caged Knot States / Local induction as the integrable reference layer / 

### lines 4401-4409
```latex
    T_{\Lambda}L[\mathbf X],
    \qquad
    T_{\Lambda}
    =
    \frac{\rhoF\Gamma^2}{4\pi}\Lambda.
    \label{eq:rt_kam_lia_hamiltonian}
\end{equation}
Here \([T_{\Lambda}]=\mathrm{J\,m^{-1}}=\mathrm N\), so
\([H_{\rm LIA}]=\mathrm J\).
```

## Research Track: KAM-Caged Knot States / Preregistered falsifiers and promotion rule / Child-level analogy.

### lines 5082-5090
```latex

% --- Minimal macro safety for standalone insertion ---
\providecommand{\vswirl}{\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\vnorm}{\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert}
\providecommand{\rhoF}{\rho_{\!f}}
\providecommand{\rhoE}{\rho_{\!E}}
\providecommand{\rhoM}{\rho_{\!m}}
\providecommand{\rhocore}{\rho_{\text{core}}}
\providecommand{\rc}{r_c}
```

## Swirl-String Response and Resonance Framework / Research Track: Quasinormal Swirl Spectroscopy and Spectral-Robustness Gate / 

### lines 5704-5712
```latex
            \nabla\cdot\mathbf v_0 &= 0,
            \\
            (\mathbf v_0\cdot\nabla)\mathbf v_0
            &=
            -\frac{1}{\rhoF}\nabla p_0.
            \label{eq:rt_qss_background_euler}
        \end{align}
        A translating or rotating vortex is therefore treated as a
        \emph{relative equilibrium}; the translation and rotation generators belong to
```

### lines 5730-5738
```latex
            (\mathbf v_0\cdot\nabla)\mathbf u
            +
            (\mathbf u\cdot\nabla)\mathbf v_0
            =
            -\frac{1}{\rhoF}\nabla\pi.
            \label{eq:rt_qss_linearized_euler}
        \end{equation}
        Introducing the Leray projector \(\mathbb P\) onto the admissible
        divergence-free subspace gives
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Euler-Decomposed Swirl Gravity and Probe Transport / 

### lines 6761-6769
```latex
\subsubsection{Canonical pressure acceleration}
    \begin{align}
        \mathbf{a}_{P}
        =
        -\frac{1}{\rho_{\!f}}\nabla p_{\mathrm{swirl}}.
        \label{eq:rt_scalar_pressure_acceleration}
    \end{align}

\subsubsection{Euler decomposition}
```

### lines 6774-6782
```latex
        \boldsymbol{\omega}\times\mathbf{u}
        +
        \nabla\left(\frac{u^2}{2}\right)
        =
        -\frac{1}{\rho_{\!f}}\nabla p_{\mathrm{swirl}}.
        \label{eq:rt_euler_decomposed_swirl_balance}
    \end{align}

\subsubsection{Filament Magnus transport}
```

### lines 6784-6792
```latex
    \begin{align}
        \mathbf{F}_{\mathrm{M}}^{(K)}
        =
        \int_K
        \rho_{\!f}\Gamma_K
        \mathbf{T}(s)\times
        \left[
            \mathbf{U}_K(s)-\mathbf{u}(\mathbf{X}(s))
        \right]ds.
```

### lines 6797-6805
```latex
    In the local-induction approximation,
    \begin{align}
        \mathbf{f}_{\kappa}
        \simeq
        -\frac{\rho_{\!f}\Gamma_K^2}{4\pi}
        \Lambda_K\kappa\,\mathbf{N}.
        \label{eq:rt_curvature_self_transport}
    \end{align}

```

### lines 6808-6821
```latex
    filament. The corresponding local density
    \begin{align}
        \mathbf{f}_{\mathrm{M}}
        =
        \rho_{\!f}\Gamma_K\,
        \mathbf{T}\times(\mathbf{U}_K-\mathbf{u})
    \end{align}
    has units
    \begin{align}
        [\rho_{\!f}\Gamma_K\Delta U]
        =
        \mathrm{kg\,m^{-3}}\,\mathrm{m^2\,s^{-1}}\,\mathrm{m\,s^{-1}}
        =
        \mathrm{N\,m^{-1}}.
```

### lines 6826-6845
```latex
        &=
        2\pi \rc\vchar
        =
        9.6836192\times10^{-9}\ \mathrm{m^2\,s^{-1}},\\
        \rho_{\!f}\Gamma_0
        &=
        6.7785334\times10^{-15}
        \frac{\mathrm{N\,m^{-1}}}{\mathrm{m\,s^{-1}}},\\
        \rho_{\!f}\Gamma_0\vchar
        &=
        7.4146692\times10^{-9}\ \mathrm{N\,m^{-1}}.
    \end{align}
    Thus, with \(\rho_{\!f}\), the Magnus layer is a weak background-transport
    term rather than a replacement for the saturated core force scale
    \(F_{\mathrm{swirl}}^{\max}=29.053507\ \mathrm{N}\). Replacing
    \(\rho_{\!f}\) by \(\rho_{\mathrm{core}}\) would change the physical sector and
    is not allowed in this transport estimate.

\subsubsection{Axis/off-axis swirl interpretation}
    For an axisymmetric galactic swirl field
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Hybrid Density-Source Swirl-Clock Benchmark / 

### lines 6889-6897
```latex
% Local macro safety block
% ------------------------------------------------------------
\providecommand{\swirlarrow}{\boldsymbol{\circlearrowleft}}
\providecommand{\vswirl}{\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\rhoF}{\rho_{\!f}}
\providecommand{\rhoE}{\rho_{\!E}}
\providecommand{\rhoM}{\rho_{\!m}}
\providecommand{\SwirlClock}{S_{(t)}^{\boldsymbol{\circlearrowleft}}}

```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Hybrid Density-Source Swirl-Clock Benchmark / Density-source mass closure.

### lines 6958-6971
```latex
\rho_{\!m}^{\rm eff}
=
\frac{\rhoE}{c^2}
=
\frac{\rhoF\,\|\vswirl\|^2}{2c^2}.
}
\label{eq:rt_density_source_mass_closure}
\end{equation}
This form keeps the source term aligned with the canonical density hierarchy
$\rhoE=\tfrac12\rhoF\|\vswirl\|^2$ and $\rhoM=\rhoE/c^2$.

\paragraph{Phenomenological spherical test profile.}
For numerical benchmarks one may use the non-canonical profile
\begin{equation}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Hybrid Density-Source Swirl-Clock Benchmark / Irrotational compression and boundary response.

### lines 7007-7015
```latex
\label{eq:rt_irrotational_boundary_velocity}
\end{equation}
with pressure response inherited from Euler radial balance,
\begin{equation}
\frac{1}{\rhoF}\frac{dp_{\rm swirl}}{dr}
=\frac{v_{\theta}^{2}}{r}.
\label{eq:rt_boundary_pressure_balance}
\end{equation}
Thus compression of the boundary at fixed circulation increases
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Swirl--Electromagnetic Normalization by Vorticity / 

### lines 7066-7074
```latex
\providecommand{\vnorm}{\lVert\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert}
\providecommand{\vchar}{v_{\!\boldsymbol{\circlearrowleft}}^{\ast}}
\providecommand{\uswirl}{\mathbf{u}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\omegaswirl}{\boldsymbol{\omega}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\rhoF}{\rho_{\!f}}
\providecommand{\rhoE}{\rho_{\!E}}
\providecommand{\rhoM}{\rho_{\!m}}
\providecommand{\rc}{r_c}
\providecommand{\Fmax}{F_{\max}^{\rm swirl}}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Kelvin Impulse Bridge / 

### lines 7511-7527
```latex
    \(R\), and core radius \(a\), the classical ring scalings are
    \begin{align}
        E_{\rm ring}
        &=
        \frac{1}{2}\rhoF\Gamma^2 R
        \left[
            \ln\left(\frac{8R}{a}\right)-\alpha_{\rm ring}
        \right],
        \label{eq:ring_energy}
        \\
        P_{\rm ring}
        &=
        \rhoF\Gamma\pi R^2,
        \label{eq:ring_impulse}
        \\
        V_{\rm ring}
        &=
```

### lines 7542-7550
```latex
        },
        \qquad
        P_{\rm swirl}
        =
        \rhoF\Gamma\pi R^2.
        \label{eq:hbar_k_kelvin_impulse_bridge}
    \end{equation}
    The coefficient \(\eta_I\) is not a free fit parameter in the final
    theory.  It must be determined from the same SI-normalization that fixes
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Pressure Envelopes and Spherical Equilibrium / 

### lines 7619-7627
```latex
    Bernoulli-type swirl balance
    \begin{equation}
        p
        +
        \frac{1}{2}\rhoF\vnorm^2
        =
        p_0,
        \label{eq:bernoulli_swirl_pressure}
    \end{equation}
```

### lines 7629-7637
```latex
    \begin{equation}
        \Delta p
        =
        -
        \frac{1}{2}\rhoF
        \Delta\left(\vnorm^2\right).
        \label{eq:pressure_defect}
    \end{equation}
    This pressure defect can generate attraction-like behavior in the
```

### lines 7661-7669
```latex
        \quad
        &\Delta p
        =
        -
        \frac{1}{2}\rhoF
        \Delta(\vnorm^2),
        \qquad
        d\tau_{\rm loc}/dt_\infty
        =
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Claims Retained / 

### lines 7747-7755
```latex
        \item Kelvin impulse may provide the bridge to photon momentum:
        \[
            \hbar k
            \leftrightarrow
            \eta_I\rhoF\Gamma\pi R^2.
        \]
        
        \item Reconnection belongs to a separate transition sector and should
        not be mixed with ideal knot conservation.
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Pressure equivalence lemma / 

### lines 8110-8139
```latex
unless an additional non-divergence density closure or boundary source is
specified.

\subsection{Pressure equivalence lemma}
For an incompressible inviscid medium with constant \(\rhoF\),
\begin{align}
    \partial_i u_i=0,
\end{align}
and no external body force, the Euler equation is
\begin{align}
    \rhoF\left(\partial_t u_i + u_j\partial_j u_i\right)
    =
    -\partial_i p .
\end{align}
Taking the divergence and using \(\partial_i u_i=0\) gives
\begin{align}
    \partial_i\partial_j\left(\rhoF u_i u_j\right)
    =
    -\nabla^2p .
    \label{eq:rt_pressure_equivalence_euler_identity}
\end{align}
Therefore the SST-73 transport-stress candidate
\begin{align}
    \nabla^2\Phi_{\mathrm{tr}}
    =
    \lambda\,\partial_i\partial_j\left(\rhoF u_i u_j\right)
\end{align}
is equivalent to
\begin{align}
    \nabla^2\left(\Phi_{\mathrm{tr}}+\lambda p\right)=0 .
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / No-monopole theorem for smooth compact stress sources / 

### lines 8157-8165
```latex
    S(\mathbf{x})
    =
    \partial_i\partial_j\Sigma_{ij},
    \qquad
    \Sigma_{ij}=\rhoF u_i u_j,
\end{align}
with \(\Sigma_{ij}\) smooth and compactly supported, or decaying sufficiently
fast at infinity.  The monopole moment is
\begin{align}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Equivalence-principle consequence of the density source / 

### lines 8204-8212
```latex
    \rhoM^{\mathrm{eff}}
    =
    \frac{\rhoE}{c^2},
    \qquad
    \rhoE=\frac{1}{2}\rhoF\lVert\uswirl\rVert^2,
\end{align}
then
\begin{align}
    M_{\mathrm{grav}}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Einstein dynamics: three candidate routes / Route III: infrared EFT universality.

### lines 9140-9148
```latex

\textbf{[CRITICAL NOTE]} The cosmological-constant problem is severe
\cite{Planck2018Cosmology}:
\begin{align}
    \frac{\rho_{\!f}}{\rho_\Lambda}
    \approx
    1.2\times10^{20},
    \qquad
    \frac{\rho_{\mathrm{horn}}^{\mathrm{eff}}}{\rho_\Lambda}
```

### lines 9151-9159
```latex
\end{align}
The first ratio is not arbitrary: it is close to one power of the
core--Planck impedance ratio \(r_c/\ell_P\).  This observation motivates
the research-track density route below, without changing the canonical
status of \(\rho_{\!f}\) in the main text.



\subsection{Historical Provenance Audit of the Inherited Density Decimal}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Historical Provenance Audit of the Inherited Density Decimal / Source and status.

### lines 9162-9170
```latex
\paragraph{Source and status.}
\textbf{[HISTORICAL ORIGIN / NOT A CURRENT DERIVATION].}
The early VAM paper registered as \texttt{VAM7-DENSITY-2025} is the traced
source of the decimal later rounded to
$\rhoF=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}$.  The source assigned the
electron rest energy to a vorticity scale
\begin{align}
    \omega_{\rm VAM}
    =
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Historical Provenance Audit of the Inherited Density Decimal / Dimensional adjudication.

### lines 9217-9225
```latex
    =
    \frac12\mathcal J_{\omega}^{\rm VAM}
    |\boldsymbol\omega|^2,
\end{align}
not $\tfrac12\rhoF|\boldsymbol\omega|^2$.

\paragraph{Closed historical form and open assumptions.}
Using $r_e=\alpha\hbar/(m_ec)$, the coefficient becomes
\begin{align}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Historical Provenance Audit of the Inherited Density Decimal / Canon consequence.

### lines 9241-9249
```latex
The early calculation explains the historical origin of the decimal but
cannot justify the current effective density.  The present edition therefore
keeps
\begin{align}
    \rhoF\equiv\rhoEff
    =
    7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}
\end{align}
as a calibrated quasi-static response and records
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Historical Provenance Audit of the Inherited Density Decimal / Cosmological non-confirmation.

### lines 9264-9272
```latex
$\Lambda\sim10^{-52}\,\mathrm{m^{-2}}$, the orthodox relation
$\rho_\Lambda=\Lambda c^2/(8\pi G)$ instead gives a scale of order
$10^{-27}\,\mathrm{kg\,m^{-3}}$.  The historical cosmological comparison
therefore does not independently confirm either
$\mathcal J_{\omega}^{\rm VAM}$ or $\rhoF$.  The separately guarded SSDL
route below is retained only as a Research-Track consistency relation.

\subsection{Twist-Rotor Status and Micro--Macro Participation Audit}
\label{subsec:rt_twist_rotor_participation_audit}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Twist-Rotor Status and Micro--Macro Participation Audit / Participation-gap diagnostic.

### lines 9394-9410
```latex
    =
    1.2231589\times10^{19}\,\mathrm{kg\,m^{-3}},
    \label{eq:rt_rc_scale_effective_inertia}
\end{align}
not the calibrated $\rhoF$.  The required scalar participation ratio is
therefore
\begin{align}
    \boxed{
    \phi_{\rm dyn}
    :=
    \frac{\rhoF}{\rho_{\rm eff}^{(\rc)}}
    =
    \frac{\rhoF}{\pi\rhohorn}
    =
    5.7229\times10^{-26}
    }.
    \label{eq:rt_participation_gap}
```

### lines 9413-9421
```latex
\begin{align}
    \boxed{
    \ell_{\rho,\rm eq}
    :=
    \sqrt{\frac{\mathcal J_{\omega}^{\rm rot}}{\rhoF}}
    =
    \frac{\rc}{\sqrt{\phi_{\rm dyn}}}
    =
    5.8897\,\mathrm{mm}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Twist-Rotor Status and Micro--Macro Participation Audit / Promotion gates.

### lines 9448-9466
```latex
long-wavelength limit of Eq.~\eqref{eq:rt_weighted_macro_response}, as fixed
by Eq.~\eqref{eq:rhof_quasistatic_response_limit}.

\paragraph{Promotion gates.}
A micro--macro derivation of $\rhoF$ may be promoted only if it:
\begin{enumerate}
    \item computes the participation functional without using $\rhoF$,
          $\phi_{\rm dyn}$, or $\ell_{\rho,\rm eq}$ as fitted inputs;
    \item converges under representative-volume size, discretization, and
          boundary-condition refinement;
    \item preserves the twist/bend distinction and the calibrated units; and
    \item predicts at least one independent response observable in addition
          to the target value of $\rhoF$.
\end{enumerate}
Until these gates close, $\rhoF$ remains
\textbf{[CALIBRATED QUASI-STATIC EFFECTIVE RESPONSE]}.

\subsection{Cosmological Impedance Route for the Background Density}
\label{sec:rt_rhof_cosmological_impedance_route}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Cosmological Impedance Route for the Background Density / Status.

### lines 9467-9476
```latex

\paragraph{Status.}
\textbf{[RESEARCH TRACK / NOT CANON-DERIVED].}
This subsection records a candidate route for reducing the calibrated
background density \(\rho_{\!f}\) to a cosmological vacuum input plus a
UV--IR impedance lift. It does not promote \(\rho_{\!f}\) out of the
primitive calibration set in the main canon.

The orthodox vacuum mass-equivalent density associated with a cosmological
constant is
```

### lines 9497-9505
```latex
    \rho_\Lambda &\simeq 5.85\times10^{-27}\,\mathrm{kg\,m^{-3}} .
\end{align}
The ratio required to obtain the canonical SST background density is
\begin{align}
    \frac{\rho_{\!f}}{\rho_\Lambda}
    \simeq
    1.20\times10^{20} .
\end{align}
This is close to the one-power core--Planck ratio
```

### lines 9509-9540
```latex
    8.72\times10^{19},
\end{align}
which suggests the line-impedance ansatz
\begin{align}
    \rho_{\!f}
    =
    \chi_\Lambda
    \left(\frac{r_c}{\ell_P}\right)
    \rho_\Lambda,
    \qquad
    \chi_\Lambda
    =
    \frac{\rho_{\!f}\ell_P}{r_c\rho_\Lambda}
    \simeq
    1.37379 .
    \label{eq:rt_rhof_lambda_chi}
\end{align}
Two non-equivalent simple closures are retained as controlled ansatzes:
\begin{align}
    \rho_{\!f}^{(c_s)}
    &:={}
    \sqrt{2}
    \left(\frac{r_c}{\ell_P}\right)
    \rho_\Lambda
    \simeq
    7.21\times10^{-7}\,\mathrm{kg\,m^{-3}},
    \\
    \rho_{\!f}^{(\Omega_0)}
    &:={}
    2\Omega_{\Lambda,0}
    \left(\frac{r_c}{\ell_P}\right)
    \rho_\Lambda
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Cosmological Impedance Route for the Background Density / Canonical conclusion.

### lines 9571-9579
```latex

\paragraph{Canonical conclusion.}
Equation~\eqref{eq:rt_rhof_lambda_chi} is a preregisterable falsifier route,
but not a completed derivation. The main canon must continue to label
\(\rho_{\!f}\) as a calibrated effective background density. Promotion to
\textbf{[CONDITIONAL DERIVED]} requires closure of four independent gates:
source coupling, normal-resolution normalization, separatrix-radius
projection, and epoch invariance.  Neither the smaller residual of
\(2\Omega_{\Lambda,0}\) nor the structural simplicity of \(\sqrt{2}\) closes
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Status.

### lines 9589-9597
```latex
\(R_\partial\)-normalization of the spherical exterior monopole
Dirichlet-to-Neumann (DtN) sector.  It does not prove the constitutive
coupling of the cosmological vacuum density \(\rho_\Lambda\) to an SST
separatrix source, and it does not replace the calibrated status of
\(\rho_{\!f}\).

\paragraph{Exterior boundary problem.}
Let \(\partial\mathcal B\) be a spherical externally resolved separatrix
of radius \(R_\partial\).  In the exterior region \(r\ge R_\partial\), let
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Monopole projection.

### lines 9669-9677
```latex
\end{align}
Including a present-epoch vacuum projection factor gives the compact
SSDL candidate
\begin{align}
    \rho_{\!f}^{\rm SSDL}
    =
    \frac{\Omega_{\Lambda,0}}{L_p}
    \Pi_0\Lambda_\partial^{-1}\Pi_0[\rho_\Lambda] .
    \label{eq:rt_ssdl_operator_form}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Electron separatrix candidate.

### lines 9687-9695
```latex
\end{align}
The spherical-monopole reduction of Eq.~\eqref{eq:rt_ssdl_operator_form}
then becomes
\begin{align}
    \rho_{\!f}^{\rm SSDL}
    =
    \Omega_{\Lambda,0}
    \left(\frac{R_e}{L_p}\right)
    \rho_\Lambda .
```

### lines 9704-9719
```latex
    &\Omega_{\Lambda,0}&=0.685,
\end{align}
one obtains
\begin{align}
    \rho_{\!f}^{\rm SSDL}
    =
    6.9806682\times10^{-7}\,\mathrm{kg\,m^{-3}},
\end{align}
which differs from the calibrated canon value
\(\rho_{\!f}=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}}\) by
\(-0.2762\%\).  This numerical agreement is not a derivation of
\(\rho_{\!f}\); it is a falsifiable research-track target.

\paragraph{Algebraic content of the electron lift.}
Define the unreduced Planck mass
\begin{align}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Algebraic content of the electron lift.

### lines 9753-9761
```latex
\end{align}
allows Eq.~\eqref{eq:rt_ssdl_electron_candidate} to be rewritten as
\begin{align}
    \boxed{
    \frac{\rho_{\!f}^{\rm SSDL}}{\rho_\Lambda}
    =
    \frac{4\Omega_{\Lambda,0}\sqrt{\alpha_g}}{\mathfrak h}
    } .
    \label{eq:rt_ssdl_force_gate_reformulation}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Conditional no-go for a dynamical \(\Omega_\Lambda(z)\) closure.

### lines 9789-9807
```latex
\end{align}
\textbf{[DERIVED NEGATIVE, CONDITIONAL]} If the present-epoch fit is promoted
to the dynamical law
\(\chi_\Lambda(z)=2\Omega_\Lambda(z)\), then
\(\rho_{\!f}(z)\propto\Omega_\Lambda(z)\) and the background density is not
constant.  That conflicts with the current incompressible constant-background
axiom.  The no-go applies to the dynamical identification; a frozen numerical
choice \(2\Omega_{\Lambda,0}\) is instead retained only as a present-epoch
coincidence record.

\textbf{[DEPENDENCY GUARD]} In the current primitive set, \(\rho_{\!f}\),
\(\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\), and \(\omega_c\) are
independent calibration entries.  A hypothetical change in \(\rho_{\!f}\)
therefore changes \(\rho_{\!E}\), \(\rho_{\!m}\), and other explicitly
\(\rho_{\!f}\)-dependent amplitudes, but does not by itself change
\(r_c=\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}/\omega_c\) or the Compton
closure chain.

\paragraph{Precision and covariance guard.}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Precision and covariance guard.

### lines 9807-9815
```latex
\paragraph{Precision and covariance guard.}
When \(\rho_\Lambda=\Omega_{\Lambda,0}3H_0^2/(8\pi G)\) is substituted into
the SSDL candidate, the central-value expression scales as
\begin{align}
    \rho_{\!f}^{\rm SSDL}
    \propto
    \Omega_{\Lambda,0}^{2}H_0^2 .
\end{align}
Treating \(H_0\) and \(\Omega_{\Lambda,0}\) as independent only for an
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Separatrix Surface-Density Lift via the Spherical Monopole DtN Sector / Normal-resolution normalization guard.

### lines 9840-9855
```latex
    \delta_\perp
    =
    \beta_\perp L_p,
    \qquad
    \rho_{\!f}^{\rm SSDL}
    \propto
    \beta_\perp^{-1} .
    \label{eq:rt_ssdl_normalization_beta}
\end{align}
The present counting convention sets \(\beta_\perp=1\).  Promotion requires
a boundary-layer or spectral theorem fixing this normalization and the
associated cutoff convention without fitting \(\rho_{\!f}\).

\paragraph{Planck-normal mode-count equivalent.}
The discrete normal-stack version of the same route is obtained by
restricting the active response space to the isotropic sector,
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Minimal Relational Link--Field Action / 

### lines 10296-10312
```latex
    \Lambda_\ell\boldsymbol{\mathcal A}_\ell.
\end{align}
In radiation gauge this gives the identifications
\begin{align}
    \rhoF
    =
    \frac{\epsilon_\ell}{\Lambda_\ell^2},
    \qquad
    K_\gamma
    =
    \frac{\mu_\ell^{-1}}{\Lambda_\ell^2},
    \qquad
    \frac{K_\gamma}{\rhoF}
    =
    \frac{1}{\epsilon_\ell\mu_\ell}
    =c_T^2.
    \label{eq:rt_link_to_Aeff_normalization}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Minimal Relational Link--Field Action / Calibrated mapping as a separate mode.

### lines 10437-10445
```latex
Only in this mode may the star basis be mapped onto the current calibrated chain,
\begin{align}
    (\rho_\star,\Gamma_\star,r_\star)
    \mapsto
    (\rhoF,\Gamma_0,\rc),
    \qquad
    \Gamma_0=2\pi\rc\vchar.
    \label{eq:rt_link_calibrated_star_mapping}
\end{align}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Core--Torsion Impedance Matching for Inertia Closure / 

### lines 10605-10619
```latex
A minimal transverse torsion displacement field \(\mathbf A\), with \(\nabla\cdot\mathbf A=0\), may be assigned the quadratic bridge Lagrangian
\begin{align}
    \mathcal L_{\rm torsion}
    =
    \frac12\rhoF\lVert\partial_t\mathbf A\rVert^2
    -
    \frac12K_T\lVert\nabla\times\mathbf A\rVert^2 .
\end{align}
The transverse propagation speed is
\begin{align}
    c_T^2=\frac{K_T}{\rhoF}.
\end{align}
The canonical operational light-speed identification belongs only to this
transverse layer:
\begin{align}
```

### lines 10624-10632
```latex
target
\begin{align}
    K_T^{\mathrm{target}}
    =
    \rhoF c^2
    =
    6.3\times10^{10}\ \mathrm{Pa}.
    \label{eq:rt_core_torsion_stiffness_target}
\end{align}
```

### lines 10634-10642
```latex
the operational postulate. A first-principles closure must obtain this value from
the substrate microphysics without using \(c\) as the same-step input.
Its intensive impedance is
\begin{align}
    Z_T=\rhoF c_T=\sqrt{\rhoF K_T},
\end{align}
which has the units of acoustic impedance, \(\mathrm{kg\,m^{-2}\,s^{-1}}\).

\subsubsection{Core--Torsion Impedance Matching Lemma}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Core--Torsion Impedance Matching for Inertia Closure / Structural correspondence.

### lines 10765-10773
```latex
[\mathbf J\times\mathbf B]
=
\mathrm{N\,m^{-3}},
\qquad
[\rhoF\mathbf v\times\boldsymbol{\omega}]
=
\mathrm{N\,m^{-3}}.
\]
Hence the most conservative Rosetta correspondence is
```

### lines 10775-10783
```latex
\boxed{
\mathbf J\times\mathbf B
\;\longleftrightarrow\;
\lambda_{\mathrm{EM}\to\circlearrowleft}\,
\rhoF\mathbf v\times\boldsymbol{\omega}.
}
\]
Since both sides already carry units of force density,
\[
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Core--Torsion Impedance Matching for Inertia Closure / Relation to the canonical flux-impulse channel.

### lines 10802-10810
```latex
\[
\mathbf J\times\mathbf B
\;\longleftrightarrow\;
\lambda_{\mathrm{EM}\to\circlearrowleft}
\rhoF\mathbf v\times\boldsymbol{\omega}
\]
is therefore not an independent canonical EM bridge.  It is a candidate
continuum-limit or bulk-stress projection of the already canonical
phase/flux channel.  A canonical upgrade requires showing how the flux
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Core--Torsion Impedance Matching for Inertia Closure / Stress closure and SST-44 tensor.

### lines 10840-10866
```latex
used in the SST-44 appendix,
\[
\sigma^{(44)}_{ij}
=
\rhoF v_i v_j
+
\rhoF \rc^2
\left(
\omega_i\omega_j-\frac12\delta_{ij}|\boldsymbol{\omega}|^2
\right)
-
\delta_{ij}\frac12\rhoF|\mathbf v|^2 .
\]
Because this tensor already contains the isotropic dynamic-pressure term
\[
-\delta_{ij}\frac12\rhoF|\mathbf v|^2,
\]
one must not also add an independent
\(-\nabla p_{\circlearrowleft}\) term with
\[
p_{\circlearrowleft}
=
\frac12\rhoF|\mathbf v|^2 .
\]
Otherwise the Bernoulli contribution is counted twice.

\paragraph{Two admissible decompositions.}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Core--Torsion Impedance Matching for Inertia Closure / Two admissible decompositions.

### lines 10889-10899
```latex
where
\[
\boldsymbol{\sigma}^{\mathrm{dev}}_{\circlearrowleft}
\equiv
\rhoF\mathbf v\mathbf v
+
\rhoF\rc^2
\left(
\boldsymbol{\omega}\boldsymbol{\omega}
-
\frac12\mathbf I|\boldsymbol{\omega}|^2
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Taylor-Column Analogues for Finite-Thickness Swirl Strings / 

### lines 10985-10993
```latex
% ============================================================
\subsection{Research Track: Taylor-Column Analogues for Finite-Thickness Swirl Strings}
\label{sec:taylor_column_finite_thickness_swirl_strings}

\providecommand{\rhoF}{\rho_{\!f}}
\providecommand{\vSwirl}{\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}}
\providecommand{\rc}{r_c}
\providecommand{\GammaK}{\Gamma_K}
\providecommand{\GammaZero}{\Gamma_0}
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Taylor-Column Analogues for Finite-Thickness Swirl Strings / Dimensional check.

### lines 11164-11180
```latex
frame where the undisturbed fluid at infinity is at rest, the kinetic energy
splits into an external irrotational contribution and an internal rotational
contribution:
\[
E_{\rm out}=\frac{1}{3}\pi\rho_{\!f}a^3U^2,
\qquad
E_{\rm in}=\frac{23}{21}\pi\rho_{\!f}a^3U^2.
\]
Therefore
\[
\boxed{
E_{\rm tot}=E_{\rm out}+E_{\rm in}
=\frac{10}{7}\pi\rho_{\!f}a^3U^2.
}
\]
This result is used only as a continuum benchmark for finite-thickness
separatrix energetics.  It does not identify a trefoil vortex with a
```

### lines 11230-11238
```latex
is considered.

\paragraph{Dimensional check.}
\[
[\rho_{\!f}R^2\partial_z\Omega^2]
=\mathrm{kg\,m^{-3}}\,\mathrm{m^2}\,\mathrm{m^{-1}s^{-2}}
=\mathrm{kg\,m^{-2}s^{-2}}
=\mathrm{N\,m^{-3}}.
\]
```

## EM, Gravity, Diagnostics, Relativity, and Inertia Research Tracks / Research Track: Taylor-Column Analogues for Finite-Thickness Swirl Strings / Numerical reference for \(U=1\,\mathrm{m\,s^{-1

### lines 11182-11190
```latex

\paragraph{Numerical reference for \(U=1\,\mathrm{m\,s^{-1}}\).}
With
\[
\rho_{\!f}=7.0\times10^{-7}\,\mathrm{kg\,m^{-3}},
\qquad
a=0.0625\,\mathrm m,
\]
one obtains
```

### lines 11203-11223
```latex

If the local background rotation varies along the axis, \(\Omega=\Omega(z)\),
ordinary Euler/Bernoulli balance gives
\[
\frac{1}{\rho_{\!f}}\frac{\partial p}{\partial r}
=\Omega(z)^2r.
\]
Integrating from the axis to the wall yields
\[
p(0,z)=p(R,z)-\frac{1}{2}\rho_{\!f}\Omega(z)^2R^2.
\]
If \(p(R,z)\) is fixed or externally controlled, the axial force density on the
central region is
\[
\boxed{
f_z=-\frac{\partial p(0,z)}{\partial z}
=\frac{1}{2}\rho_{\!f}R^2
\frac{\partial}{\partial z}\left[\Omega(z)^2\right].
}
\]
This force is part of the ordinary vorticity-pressure impulse budget:
```
