# Revision notes - manuscript v0.2.1

## Scientific change

The main addition is an explicit gate-ordering result.

G0-G3 may determine an alpha-free geometric candidate such as

\[
\alpha_{\rm geom}=D_{\rm geom}/\bar\lambda_C,
\]

but they cannot establish that this number is the electromagnetic fine-structure constant. G4 is therefore the unique **electromagnetic-identification gate**, because it must derive the Maxwell kinetic coefficient, the source normalization, the bulk-defect response matching, and the electromagnetic self-energy shape factor. G5 is strictly the out-of-sample comparison of the G4 output with measured \(\alpha\).

This formulation is slightly more precise than saying that G0-G3 cannot produce any alpha-like number: they can produce a dimensionless candidate, but not identify it as the electromagnetic coupling.

## Applied patches

1. Added the gate-ordering remark and rewired G5 as a child of G4.
2. Added explicit numerical-provenance language for the high-resolution trefoil value and attached it to G0.
3. Changed table row H from `Gamma_eff implicit` to `--- (no explicit circulation)`.
4. Restored the Ohanian citation in the formal-speed discussion.
5. Restored the scoped statement:
   - within the frozen closure family, there is one free coefficient and one comparison datum;
   - unfreezing the conventions reopens G0-G4.
6. Updated manuscript version to 0.2.1.

## Build verification

- Compiled with `pdflatex` twice.
- Output: 18 pages.
- No unresolved references or fatal layout errors.
- Rendered all pages for visual inspection.
- Remaining warnings are limited to harmless underfull bibliography boxes and the standard REVTeX/nameref warning.
