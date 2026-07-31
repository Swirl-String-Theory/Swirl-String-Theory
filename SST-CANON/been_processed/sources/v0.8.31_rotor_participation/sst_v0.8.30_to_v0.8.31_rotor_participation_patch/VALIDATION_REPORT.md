# Validation Report - SST Canon v0.8.31

## Patch validation

- Both unified diffs pass GNU `patch --dry-run` against the packaged v0.8.30 sources.
- Applying each diff with `patch -o` produces byte-identical copies of the packaged v0.8.31 sources.
- Original v0.8.30 files are not modified by the provided application scripts.
- CRLF line endings are preserved in both target files.

## Source validation

- Main and Research Track labels were scanned jointly: no duplicate labels.
- The new cross-reference labels resolve:
  - `eq:rhof_quasistatic_response_limit`
  - `subsec:rt_twist_rotor_participation_audit`
  - `eq:rt_rotor_matching_microinertia`
  - `eq:rt_rotor_line_inertia_reformulation`
  - `eq:rt_rotor_speed_tautology`
  - `eq:rt_kelvin_bending_dispersion_guard`
  - `eq:rt_rc_scale_effective_inertia`
  - `eq:rt_participation_gap`
  - `eq:rt_equivalent_response_length`
  - `eq:rt_weighted_macro_response`

## LaTeX validation

Command:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error SST_CANON-v0.8.31.tex
```

Result:

- PDF generated successfully;
- 234 A4 pages;
- zero fatal LaTeX errors;
- zero unresolved references;
- zero unresolved citations;
- zero multiply defined labels.

Existing non-fatal underfull/overfull box warnings remain editorial layout warnings and were not treated as mathematical failures.

## Visual validation

Selected pages were rendered at 150 dpi and visually inspected:

- title/version page;
- main quasi-static response and participation guards;
- v0.8.31 changelog entry;
- compact-rotor reformulation and tautology audit;
- twist/Kelvin guard, participation gap, equivalent response length, and promotion gates;
- transition back into the existing cosmological impedance route.

No clipping, overlapping text, missing glyphs, malformed boxes, or broken cross-references were observed.

## Scientific scope check

The release does not derive a new primitive. It records:

```text
J_omega^rot = pi r_c^2 rho_horn^eff
             = 2.4282114e-11 kg m^-1
[REFORMULATION / MATCHING ANSATZ]
```

and keeps:

```text
rho_f = rho_eff^(0) = 7.0e-7 kg m^-3
[CALIBRATED QUASI-STATIC EFFECTIVE RESPONSE].
```

The values

```text
phi_dyn = 5.7229e-26
ell_rho,eq = 5.8897 mm
```

are diagnostic reparameterizations only. They are not promoted to physical cell sizes, coherence lengths, or vortex separations.
