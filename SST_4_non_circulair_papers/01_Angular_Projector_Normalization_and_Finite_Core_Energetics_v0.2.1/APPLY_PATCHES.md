# Patch set — Angular-Projector Normalization, v0.2.0 → v0.2.1 FINAL

This release contains four sequential unified diffs plus three cross-platform
release/verification scripts. Apply from the directory containing the pristine
v0.2.0 manuscript and supplementary files.

## Linux / macOS / Git Bash

```bash
for p in 0001-fourier-reconstruction-branch \
         0002-curvature-overshoot-and-naturalness \
         0003-framing-mirror-sector \
         0004-s1-provenance; do
  patch -p0 --dry-run < "$p.diff" || { echo "FAILED: $p"; exit 1; }
  patch -p0           < "$p.diff" || exit 1
done

python 0005-release-hygiene.py --root .
python 0006-build-manifest.py --root .
python 0007-verify-release.py --root .
```

To compile and audit the LaTeX result when `pdflatex` is installed:

```bash
python 0007-verify-release.py --root . --compile
python 0006-build-manifest.py --root .
python 0007-verify-release.py --root .
```

## Windows PowerShell

```powershell
$patches = @(
  "0001-fourier-reconstruction-branch",
  "0002-curvature-overshoot-and-naturalness",
  "0003-framing-mirror-sector",
  "0004-s1-provenance"
)

foreach ($p in $patches) {
  Get-Content "$p.diff" -Raw | patch -p0 --dry-run
  if ($LASTEXITCODE -ne 0) { throw "Dry-run failed: $p" }
  Get-Content "$p.diff" -Raw | patch -p0
  if ($LASTEXITCODE -ne 0) { throw "Patch failed: $p" }
}

py -3 0005-release-hygiene.py --root .
py -3 0006-build-manifest.py --root .
py -3 0007-verify-release.py --root .
```

## Patch contents

### 0001 — Fourier reconstruction branch

Adds the reconstruction value

\[
\mathcal L_D^{\rm rec}=16.3724604307,
\]

its `+50.30 ppm` separation from the metadata value and `+60.67 ppm`
separation from \(L_a/2\), the corresponding projector value
`137.1616038`, and the external excess `916.58 ppm`.

### 0002 — curvature overshoot and naturalness

Uses the computed diagnostic
\(\mathcal I_{\kappa^2}=19.32\) and
\(\hat\kappa_{\max}=2.1668\). The coefficient
\(6.07\times10^{-3}\) is now described as an **optimistic lower estimate**,
conditional on correcting the overshoot not increasing the curvature integral.
No strict variational lower bound is claimed.

### 0003 — mirror framing sector

Adds the \(SL=+3\) row and records the approximately \(235\times\) spread
across the three framing sectors.

### 0004 — Supplementary Data S1 provenance

Completes all provenance fields supported by the supplied source:

- dataset: `Database of Ideal Knots 3-10 crossings`;
- compiler: Brian Gilbert;
- embedded source date retained verbatim;
- historical source: The Knot Atlas, `Ideal knots` / `Ideal.txt.gz`;
- local source: `ideal_favorites.txt`;
- retrieval date: not recorded;
- file-specific licence: not established;
- public redistribution status: unresolved.

The coefficient payload is described as preserved verbatim; the provenance
header is explicitly identified as newly added.

### 0005 — release hygiene

Updates the internal manuscript version to `0.2.1`, renames the LaTeX source
accordingly, and records that numerical files retaining `v0.2.0` in their names
are frozen computational artifacts rather than regenerated v0.2.1 outputs.

### 0006–0007 — manifest and release verification

The manifest builder is deterministic and idempotent. The verifier checks:

- internal/file version consistency;
- all four scientific patches;
- absence of `[FILL IN]`;
- XML well-formedness;
- payload/header wording;
- licence/redistribution guard;
- SHA-256 integrity;
- optionally, LaTeX compilation and unresolved/overfull warnings.

## Important submission guard

The available provenance identifies the data and its compiler, but it does not
establish file-specific redistribution permission. Do not distribute the XML
coefficient payload publicly until the applicable terms are confirmed. An
alternative is to omit the payload and provide extraction instructions tied to
the cited Knot Atlas source.
