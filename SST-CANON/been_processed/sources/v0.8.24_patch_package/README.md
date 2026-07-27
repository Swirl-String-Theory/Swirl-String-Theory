# SST Canon v0.8.23 -> v0.8.24 patch package

This package upgrades the current dot-named v0.8.23 sources:

- `SST_CANON-v0.8.23.tex`
- `SST_CANON-v0.8.23-research-track.tex`

to:

- `SST_CANON-v0.8.24.tex`
- `SST_CANON-v0.8.24-research-track.tex`

The package is built directly against the two supplied v0.8.23 files. It does
not include the underscore-filename workaround because the authoritative local
filenames use dots and already match the `\input{...}` convention.

## Recommended route

Use `SST_CANON-v0.8.23-to-v0.8.24-GIT-RENAME.patch.diff`.
It edits and renames both files in one operation:

```bash
git apply --check SST_CANON-v0.8.23-to-v0.8.24-GIT-RENAME.patch.diff
git apply SST_CANON-v0.8.23-to-v0.8.24-GIT-RENAME.patch.diff
```

The command works in a Git worktree and also in a plain directory when Git is
installed. The two v0.8.23 source files must be byte-identical to the supplied
baseline.

## Portable GNU patch route

First copy the v0.8.23 sources to the new names, then apply the combined patch:

```bash
cp SST_CANON-v0.8.23.tex SST_CANON-v0.8.24.tex
cp SST_CANON-v0.8.23-research-track.tex SST_CANON-v0.8.24-research-track.tex
patch --dry-run -p1 --binary < SST_CANON-v0.8.23-to-v0.8.24-COMBINED.patch.diff
patch -p1 --binary < SST_CANON-v0.8.23-to-v0.8.24-COMBINED.patch.diff
```

Separate MAIN and research-track patches are included for targeted inspection.

## Scope

The release implements the verified core--torsion normalization repair,
compact-U(1) attribution and phase gate, three link-spacing scenarios,
zero-legacy star-basis separation, four-class failure taxonomy, geometry
certification Canon Rule, material--link sector-separation postulate,
conditional two-speed lemma, heading/terminology repairs, and precision hygiene.

See `CHANGELOG.md` and `VALIDATION.md` for the exact changes and tests.
