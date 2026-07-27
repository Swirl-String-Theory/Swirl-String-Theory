# SST CANON v0.8.20 — complete eight-source patch series

This package uses the exact Canon and Research-Track files re-uploaded by the user
as `SST_CANON-v0.8.20(2).tex` and
`SST_CANON-v0.8.20-research-track(2).tex`. Inside the package they are stored
under the canonical target filenames.

Apply patches `0001` through `0008` in lexical order. Patches `0001`–`0005` are
the unchanged, previously validated Round-1 patches. Patches `0006`–`0008` are
rebased onto the exact endpoint of `0005`.

No document version number is changed.

## Apply all patches

```bash
scripts/apply_all_8.sh /path/to/target
```

```powershell
.\scripts\apply_all_8.ps1 -Target C:\path\to\target
```

The Research-Track `.tex` is an include fragment rather than a standalone
LaTeX document. It is therefore validated through compilation of the main Canon,
which inputs the fragment.
