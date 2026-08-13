# SST configuration-resolved spectroscopic-response patch v0.1.0

Target files:

- `SST_CANON-v0.8.34.tex`
- `SST_CANON-v0.8.34-research-track.tex`

Apply from the directory containing those files:

```bash
patch -p1 < diff/0001-configuration-resolved-spectroscopic-response-main.diff
patch -p1 < diff/0002-generalized-king-diagnostics-research-track.diff
```

Alternatively, replace the target files with the patched full copies included in this package.

## Main Canon change

Adds a compact dependency guard next to the canonical master mass equation:

- defines a transition shift as `delta(transition energy)/h`;
- classifies it as a response functional, not a second mass equation;
- prohibits simultaneous use of `delta H_K` and `delta Xi_K` as independent fit directions without an explicit coordinate transformation;
- records that the current Canon does not yet derive a complete atomic energy functional or selection rules.

## Research Track change

Adds a full configuration-resolved linear-response programme:

- compact and resolved response bases;
- tensorial inertia response;
- contact-skeleton observables from strut and kink multipliers;
- explicit variation of `Xi_K`;
- generalized King diagnostics;
- preregistered certification and falsification gates;
- bibliography entry for Ishiyama et al., arXiv:2505.04154v2.

## Validation performed

- both diffs apply cleanly to the supplied v0.8.34 files;
- all newly introduced labels are unique across the patched pair;
- the new citation key is defined once and cited once;
- no existing text outside the insertion regions was modified.
