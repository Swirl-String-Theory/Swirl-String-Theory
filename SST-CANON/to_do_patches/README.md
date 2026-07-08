# SSDL Research-Track Patch for SST_CANON-v0.8.19

This package adds the Separatrix Surface-Density Lift (SSDL) research-track block to `SST_CANON-v0.8.19-research-track.tex` only. It does not modify the main canon.

Status label used in the patch:

`[RESEARCH TRACK / SPHERICAL MONOPOLE DtN NORMALIZATION PROVEN / SOURCE COUPLING OPEN]`

Included files:

- `SST_CANON-v0.8.19-ssdl-research-track.patch` — unified diff.
- `SST_CANON-v0.8.19-research-track-ssdl-patched.tex` — full patched research-track file.
- `ssdl_research_track_block.tex` — standalone inserted LaTeX block.
- `audit_result_v0_2.pure.json` — pure JSON audit result.
- `audit_result_v0_2.json` — JSON plus console output audit result.

Main inserted formula:

```tex
ho_{\!f}^{m SSDL}
=
rac{\Omega_{\Lambda,0}}{L_p}
\Pi_0\Lambda_\partial^{-1}\Pi_0[ho_\Lambda]
```

Numerical target:

`rho_f_ssdl_analytic = 6.98066822781536e-07 kg m^-3`, i.e. `-0.27616817406628247%` relative to `7.0e-7 kg m^-3`.

Open lemmas preserved explicitly:

1. `rho_Lambda` couples as an isotropic normal separatrix source.
2. `Omega_Lambda,0` is the correct projection factor or must be replaced by an SST projection functional.
3. `L_p` is the correct normal resolution thickness.
