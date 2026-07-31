# SST CANON v0.8.31 -> v0.8.32 patch

## Scope

This patch applies to the user's exact local `(2)` files.

- removes `rho_f = 7.0e-7 kg m^-3` from the primitive calibration set;
- introduces `rho_ref` as a legacy reference normalization;
- leaves `rho_f == rho_eff^(0)` physically unfixed;
- records the four VAM-7 provenance defects;
- adds the A/B/C/Q/X scaling audit and source-free normalization no-go;
- converts selected absolute numerical amplitudes to legacy-reference benchmarks;
- leaves `SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex` byte-identical.

## Source SHA-256

- main: `06c7f5bacfde31d1503bc45de8e7854946b56924c4c18551ecb99d05402f55b3`
- research track: `312e87055334681add3b680284d0e9a50063fce7b13c689386aa6b4e4335b18c`
- speculative: `e1b24a4d22a4261b748467352eb37e5c3d1bc8093fafc1ed677b2803110a0236`

## Files

- `patched/SST_CANON-v0.8.32.tex`
- `patched/SST_CANON-v0.8.32-research-track.tex`
- `patched/SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.2.tex`
- `patches/*.diff`
- `audit/rho_f_scaling_audit_v0.8.32.csv`
- `audit/rho_f_scaling_audit_v0.8.32.md`
- `VALIDATION_REPORT.md`

## Epistemic result

`rho_ref` reproduces historical numerical tables only. It is not an observable calibration.
The physical quasi-static response `rho_eff^(0)` remains an open constitutive coefficient.

## Applying the patch

Linux, WSL, or Git Bash:

```bash
./apply_patch.sh /path/to/canon/folder
```

PowerShell with GNU `patch.exe` available:

```powershell
./apply_patch.ps1 -Root C:\path\to\canon\folder
```

Both scripts verify the exact v0.8.31 source hashes before changing anything.
