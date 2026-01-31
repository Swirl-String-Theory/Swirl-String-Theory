# Zenodo Tools Directory

This directory contains all scripts related to Zenodo DOI management and automation.

## Directory Structure

All scripts are now organized in `zenodo_tools/` to keep the root directory clean.

## Path References

All scripts use relative paths based on their location:
- **Base directory**: `Path(__file__).parent.parent` (goes up to SwirlStringTheory root)
- **Zenodo token**: `../../zenodo.py` (two levels up from zenodo_tools/, in parent directory of SwirlStringTheory)
- **CSV files**: Located in the root directory (e.g., `zenodo_comparison.csv`, `zenodo_papers.csv`)

## Main Scripts

### Core Workflow
- **`smart_zenodo_workflow.py`** - Intelligent workflow that checks for existing DOIs, avoids duplicates, updates metadata, and renders/uploads PDFs
- **`zenodo_gui.py`** - Graphical interface to view all SST papers, their DOIs, and status

### Automation
- **`zenodo_automation.py`** - Core module for Zenodo API interactions
- **`create_zenodo_configs.py`** - Create Zenodo config files and get DOIs
- **`compare_local_zenodo.py`** - Compare local files with Zenodo deposits

### Utilities
- **`cleanup_duplicate_deposits.py`** - Remove duplicate/unwanted deposits
- **`fix_duplicate_dois.py`** - Fix duplicate `\paperdoi` commands in LaTeX files
- **`render_new_doi_files.py`** - Render PDFs for files with new DOIs
- **`check_actual_doi_status.py`** - Check which files actually have DOIs

### Analysis
- **`quick_review.py`** - Quick overview of deposit status
- **`list_today_deposits.py`** - List deposits created today
- **`check_recent_deposits.py`** - Check recent deposits
- **`analyze_zenodo_status.py`** - Analyze Zenodo status

### Processing
- **`process_specific_files.py`** - Process specific files (SST-23, SST-55, SST-59)
- **`process_sst23.py`** - Process SST-23 specifically
- **`process_sst33_enhanced.py`** - Process SST-33 Enhanced Heat Transport
- **`render_three_files.py`** - Render three specific files

## Usage

All scripts should be run from the `zenodo_tools/` directory or with the full path:

```bash
# From SwirlStringTheory root
cd zenodo_tools
python smart_zenodo_workflow.py

# Or with full path
python zenodo_tools/smart_zenodo_workflow.py
```

## Dependencies

- All scripts import from `zenodo_automation` (in same directory)
- Some scripts import from `create_zenodo_configs` (in same directory)
- All scripts read token from `../../zenodo.py` (parent directory of SwirlStringTheory)

## Notes

- Scripts automatically find the SwirlStringTheory root using `Path(__file__).parent.parent`
- CSV files are read from/written to the root directory
- Zenodo config files (`.zenodo.json`) are stored alongside their `.tex` files in SST-xx folders
