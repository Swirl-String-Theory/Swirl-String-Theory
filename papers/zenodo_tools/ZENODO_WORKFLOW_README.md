# Zenodo Workflow Tools

## Overview

This directory contains improved tools for managing Zenodo deposits with intelligent checks and a GUI for viewing all papers.

## New Tools

### 1. `smart_zenodo_workflow.py`

An intelligent workflow script that:

1. **Checks config for existing DOI** - Before creating a new entry, verifies if the `.zenodo.json` config file already has a DOI
2. **Checks for duplicate titles** - Searches Zenodo to see if a paper with the same title already exists
3. **Updates metadata** - If a title exists on Zenodo, compares local config metadata with Zenodo metadata and updates if needed
4. **Renders and uploads PDFs** - If both the config and LaTeX file have matching DOIs, automatically renders the PDF (2 passes) and uploads it to Zenodo

#### Usage

```bash
# From SwirlStringTheory root
python zenodo_tools/smart_zenodo_workflow.py

# Or from zenodo_tools directory
cd zenodo_tools
python smart_zenodo_workflow.py
```

The script will:
- Find all SST-xx folders with `.tex` files
- Process each paper through the smart workflow
- Display status and actions taken for each file

#### Workflow Logic

1. **Config has DOI + LaTeX has DOI (matching)**: Ready to render/upload
2. **Config has DOI + LaTeX missing DOI**: Adds DOI to LaTeX
3. **Config has DOI + LaTeX has different DOI**: Updates LaTeX with config DOI
4. **No config DOI + Title exists on Zenodo**: Uses existing deposit, creates config, adds DOI to LaTeX
5. **No config DOI + Title doesn't exist**: Creates new deposit, gets DOI, creates config, adds DOI to LaTeX

### 2. `zenodo_gui.py`

A graphical user interface that displays:

- All SST-xx folders recursively
- `.tex` files with DOI status
- `.pdf` files with update status
- `.zenodo.json` config files with DOI information

#### Usage

```bash
# From SwirlStringTheory root
python zenodo_tools/zenodo_gui.py

# Or from zenodo_tools directory
cd zenodo_tools
python zenodo_gui.py
```

#### Features

- **Tree View**: Hierarchical display of folders and files
- **File Details**: Click any file to see detailed information
- **Status Indicators**: 
  - Shows if LaTeX files have DOIs
  - Shows if PDFs are up to date
  - Shows config file contents
- **Refresh**: Reload file structure
- **Expand/Collapse**: Navigate the tree easily

#### GUI Columns

- **File/Folder**: Name of the file or folder
- **Type**: File type (LaTeX, PDF, Config, Folder)
- **DOI**: DOI if available
- **Status**: Current status (Has DOI, No DOI, etc.)

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- `zenodo_automation.py` module
- `create_zenodo_configs.py` module (for metadata extraction)
- Zenodo API token in `../zenodo.py`

## Workflow Recommendations

1. **First Time Setup**:
   - Run `smart_zenodo_workflow.py` to process all papers
   - This will create configs, get DOIs, and sync everything

2. **Regular Updates**:
   - Use `zenodo_gui.py` to view status of all papers
   - Run `smart_zenodo_workflow.py` periodically to:
     - Update metadata if changed locally
     - Render and upload new PDFs
     - Sync DOIs between config and LaTeX

3. **Adding New Papers**:
   - Add the `.tex` file to an SST-xx folder
   - Run `smart_zenodo_workflow.py` - it will automatically:
     - Check if title exists (avoid duplicates)
     - Create deposit if needed
     - Get DOI and add to both config and LaTeX
     - Render and upload PDF

## Status Codes

- **ready**: Config and LaTeX have matching DOI, ready for upload
- **updated**: DOI was added or updated in LaTeX
- **found**: Found existing deposit on Zenodo, synced locally
- **new**: Created new deposit on Zenodo
- **error**: Something went wrong (check message)

## Notes

- The script respects rate limits with small delays between API calls
- PDFs are only rendered if the LaTeX file is newer than the PDF
- Metadata updates only occur if there are actual differences
- Title matching is case-insensitive and handles minor formatting differences
