# Zenodo Scripts Organization - Complete

## Summary

All Zenodo-related scripts have been moved to the `zenodo_tools/` directory and all path references have been updated.

## What Was Done

1. **Created `zenodo_tools/` directory** in the SwirlStringTheory root
2. **Moved 24 scripts** to the new directory
3. **Updated all path references**:
   - Changed hardcoded `Path(r'c:\workspace\projects\SwirlStringTheory')` to `Path(__file__).parent.parent`
   - This allows scripts to find the root directory regardless of where they're located
4. **Fixed CSV file references** in scripts that had hardcoded paths
5. **Created README.md** in zenodo_tools/ with documentation

## Scripts Moved

- Core: `zenodo_automation.py`, `create_zenodo_configs.py`, `smart_zenodo_workflow.py`, `zenodo_gui.py`
- Comparison: `compare_local_zenodo.py`
- Cleanup: `cleanup_duplicate_deposits.py`, `fix_duplicate_dois.py`
- Analysis: `quick_review.py`, `list_today_deposits.py`, `check_recent_deposits.py`, `analyze_zenodo_status.py`
- Processing: `process_specific_files.py`, `process_sst23.py`, `process_sst33_enhanced.py`, `render_three_files.py`, `render_new_doi_files.py`
- Utilities: `check_actual_doi_status.py`, `list_files_without_doi.py`, `list_files_needing_doi.py`, `check_dois.py`, `list_zenodo_papers.py`, `check_drafts.py`, `process_failed_files.py`
- Examples: `zenodo_example.py`

## Path Updates

All scripts now use:
- **Base directory**: `Path(__file__).parent.parent` (goes up to SwirlStringTheory root)
- **Zenodo token**: `../zenodo.py` (parent directory - unchanged)
- **CSV files**: `base_dir / 'filename.csv'` (in root directory)

## Verification

- ✅ All scripts compile without errors
- ✅ Imports work correctly (all scripts in same directory)
- ✅ Path references updated to use relative paths
- ✅ CSV file references fixed

## Usage

Scripts can be run from either location:

```bash
# From root directory
python zenodo_tools/smart_zenodo_workflow.py

# From zenodo_tools directory
cd zenodo_tools
python smart_zenodo_workflow.py
```

Both methods work because scripts use `Path(__file__).parent.parent` to find the root directory.
