# Patch sources archive

All conversation diffs, patch blocks, audit notes, verify scripts, and evidence
packs live here. Nothing patch-related remains in `papers/SST-CANON/` root
(only `latexmkrc`, `archive/`, and `been_processed/`).

- **Integration map:** `INTEGRATION_INDEX.md` (source → edition)
- **Latest bundle index:** `PATCH_MANIFEST.md` (v0.8.16 merge order)
- **Evidence pack:** `SST_v0_8_12_evidence_pack/` (patches, scripts, results)

Rebuild latest edition:

```powershell
cd papers/SST-CANON/been_processed
python apply_v0816.py
```
