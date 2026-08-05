# Patch set — Angular-Projector Normalization, v0.2.0 → v0.2.1

Four sequential unified diffs. Apply in numeric order from the directory
containing the v0.2.0 source files.

```bash
for p in 0001-fourier-reconstruction-branch \
         0002-curvature-overshoot-and-naturalness \
         0003-framing-mirror-sector \
         0004-s1-provenance; do
  patch -p0 --dry-run < "$p.diff" || { echo "FAILED: $p"; break; }
  patch -p0           < "$p.diff"
done
sha256sum * > SHA256SUMS.txt     # 0004 edits the XML, so the manifest changes
```

All four verified with `patch -p0 --dry-run` against pristine v0.2.0 sources,
applied in sequence, then compiled: exit 0, zero undefined references, zero
overfull boxes. `Supplementary_Data_S1_*.xml` re-validated with an XML parser
after patching.

## What each patch does

**0001 — Fourier reconstruction branch (5 hunks, .tex)**
Supplementary Code S1 computes `L_D = 16.3724604307` and stores it in
`VALIDATION_v0.2.0.json`, but the manuscript never quotes it. Adds it to the
prose, the provenance table, and Fig. 4 as a third branch point:
+50.30 ppm vs metadata, +60.67 ppm vs `L_a/2`, giving `(8π/3)L_D = 137.1616038`
and an external excess of 916.58 ppm. The metadata–reconstruction separation is
~4.85× the branch separation the paper currently foregrounds. Also adds
`\label{app:fourier-reconstruction}`.

**0002 — curvature overshoot and naturalness (2 hunks, .tex)**
Replaces the round `I_κ² = 20` row with the computed 19.32 (→ required
`c_κ = −6.07×10⁻³`), and quantifies the overshoot: `κ̂_max = 2.1668` against the
thickness bound 2, an 8.3% excess. Since overshoot inflates `I_κ²` and
`|c_κ| = |Δ|/I_κ²`, the quoted `6×10⁻³` is relabelled a **lower** bound on
`|c_κ|`. The appendix gets the actual numbers instead of "slightly different".

**0003 — mirror framing sector (1 hunk, .tex)**
Adds the `SL = +3` row (bound 99.34, `c_Ω = −1.20×10⁻³`) and replaces
"almost two orders" with the true spread across all three sectors, ≈235×.

**0004 — Supplementary Data S1 provenance (3 files)**
Adds a structured provenance header to the XML (purpose, record description,
reconstruction caveat, integrity note) with the origin/version/retrieval/licence
fields marked **[FILL IN]** — these cannot be supplied without knowing the
source. Adds a matching README section flagging that the filename still carries
an attribution ("Gilbert") that appears nowhere in the manuscript. Adds one
clause to the .tex pointing at the header.

## Verified numbers

| quantity | value |
|---|---|
| `L_D` reconstruction | 16.3724604307 |
| radius-normalized | 32.744920861 |
| `(8π/3)·L_D` | 137.1616038 |
| external excess | 916.58 ppm |
| vs metadata / vs `L_a/2` | +50.30 / +60.67 ppm |
| `I_κ²` (S1) → required `c_κ` | 19.32 → −6.07×10⁻³ |
| `κ̂_max` vs bound 2 | 2.1668 (+8.3%) |
| `SL = +3` bound / `c_Ω` | 99.34 / −1.20×10⁻³ |
| framing spread | 234–235× |

## Retracted from my earlier review

I flagged a duplicated `\int\dd^3x\int\dd^3x'` in `eq:vorticity-energy-v020` as
blocking. **That was my error.** The source reads
`\int\!\dd^3x\int\!\dd^3x'` — one integral over `x`, one over `x'`, which is the
correct double integral for the Biot–Savart energy. No patch is needed and none
is included. Please disregard that item.
