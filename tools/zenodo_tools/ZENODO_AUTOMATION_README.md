# Zenodo Automation Script

This script automates the complete workflow of creating a Zenodo DOI, adding it to your LaTeX paper, compiling to PDF, and uploading everything to Zenodo.

## Features

✅ **Automatic DOI Creation** - Creates a draft deposit on Zenodo and gets the DOI  
✅ **LaTeX Integration** - Automatically adds DOI to your LaTeX file in the standard format  
✅ **PDF Compilation** - Compiles your LaTeX file to PDF  
✅ **File Upload** - Uploads PDF and other files to Zenodo  
✅ **Metadata Management** - Sets title, description, keywords, authors, etc.  
✅ **Draft or Publish** - Creates draft by default (you can review before publishing)  

## Setup

### 1. Get Zenodo API Token

1. Go to https://zenodo.org/account/settings/applications/
2. Create a new personal access token
3. Copy the token

**For testing:** Use Zenodo Sandbox at https://sandbox.zenodo.org/account/settings/applications/

#### Option A: Store token in `../zenodo.py` (Recommended)

Create a file `zenodo.py` in the parent directory (one level up from SwirlStringTheory):

```python
# ../zenodo.py
key = "YOUR_ZENODO_TOKEN_HERE"
```

The script will automatically read the token from this file if you don't provide `--token`.

#### Option B: Provide token via command line

Use the `--token` argument (see Usage section below).

### 2. Install Dependencies

```bash
pip install requests
```

### 3. Ensure LaTeX is Installed

The script uses `pdflatex` to compile your LaTeX files. Make sure you have a LaTeX distribution installed:
- Windows: MiKTeX or TeX Live
- Mac: MacTeX
- Linux: TeX Live

## Usage

### Basic Usage (Extract metadata from LaTeX)

If you have `../zenodo.py` with your token:
```bash
python zenodo_automation.py path/to/paper.tex
```

Or provide token explicitly:
```bash
python zenodo_automation.py path/to/paper.tex --token YOUR_ZENODO_TOKEN
```

This will:
1. Extract title, author, abstract from your LaTeX file
2. Create a draft deposit on Zenodo
3. Get the DOI
4. Add DOI to your LaTeX file
5. Compile to PDF
6. Upload PDF to Zenodo

### With Custom Metadata

Create a JSON file with your metadata (see `zenodo_config_template.json`):

```bash
python zenodo_automation.py paper.tex --token YOUR_TOKEN --metadata metadata.json
```

### Using Zenodo Sandbox (for testing)

```bash
python zenodo_automation.py paper.tex --token YOUR_SANDBOX_TOKEN --sandbox
```

### Publish Immediately (not recommended for first run)

```bash
python zenodo_automation.py paper.tex --token YOUR_TOKEN --publish
```

### Skip PDF Compilation

```bash
python zenodo_automation.py paper.tex --token YOUR_TOKEN --no-compile
```

### List Published Papers

List all your published papers with their DOIs:

```bash
python zenodo_automation.py --list
```

Or use the dedicated script:

```bash
python list_zenodo_papers.py
```

Export to CSV:

```bash
python list_zenodo_papers.py --csv papers.csv
```

List all deposits (including drafts):

```bash
python zenodo_automation.py --list-all
```

## Workflow Steps

The script performs these steps automatically:

1. **Extract Metadata** - Reads title, author, abstract from LaTeX or uses provided JSON
2. **Create Draft Deposit** - Creates a new draft on Zenodo
3. **Get DOI** - Retrieves the assigned DOI (concept DOI for drafts)
4. **Add DOI to LaTeX** - Adds `\newcommand{\paperdoi}{10.5281/zenodo.xxxxx}` to your file
5. **Compile PDF** - Runs `pdflatex` twice to generate PDF
6. **Upload PDF** - Uploads the compiled PDF to Zenodo
7. **Set Metadata** - Updates all metadata fields
8. **Publish (optional)** - Publishes the deposit if `--publish` flag is used

## LaTeX File Requirements

Your LaTeX file should have:
- `\title{...}` - Paper title
- `\author{...}` - Author(s)
- `\begin{abstract}...\end{abstract}` - Abstract (optional but recommended)

The script will add:
```latex
\newcommand{\paperdoi}{10.5281/zenodo.xxxxx}
```

## Metadata Fields

The script supports all Zenodo metadata fields:

- **title** - Paper title
- **creators** - List of authors with name, affiliation, ORCID
- **description** - Abstract or description
- **keywords** - List of keywords
- **upload_type** - Usually "publication"
- **publication_type** - "article", "preprint", "thesis", etc.
- **publication_date** - Publication date (YYYY-MM-DD)
- **access_right** - "open", "embargoed", "restricted", "closed"
- **license** - "cc-by-4.0", "cc-by-sa-4.0", etc.
- **communities** - Zenodo communities to add to
- **related_identifiers** - Related DOIs, arXiv IDs, etc.

## Example: Complete Workflow

```bash
# 1. Create metadata file
cat > paper_metadata.json << EOF
{
  "title": "Swirl-String Theory: A New Approach",
  "creators": [
    {
      "name": "Omar Iskandarani",
      "affiliation": "Independent Researcher",
      "orcid": "0009-0006-1686-3961"
    }
  ],
  "description": "This paper presents a new theoretical framework...",
  "keywords": ["physics", "string theory", "fluid dynamics"],
  "publication_type": "article",
  "publication_date": "2026-01-27",
  "access_right": "open",
  "license": "cc-by-4.0"
}
EOF

# 2. Run automation
python zenodo_automation.py SST-40_Photons_and_Lazers/SST-40_Photon_and_Lasers_EN.tex \
    --token YOUR_TOKEN \
    --metadata paper_metadata.json

# 3. Review draft on Zenodo
# 4. Publish manually or use --publish flag
```

## Important Notes

⚠️ **Draft vs Published**: By default, the script creates a **draft** deposit. You can review it on Zenodo before publishing. Once published, the DOI is permanent and cannot be changed.

⚠️ **Sandbox for Testing**: Always test with `--sandbox` flag first! The sandbox is at https://sandbox.zenodo.org

⚠️ **DOI Format**: Draft deposits get a "concept DOI" that becomes the final DOI when published.

⚠️ **File Size Limits**: Zenodo has limits (50GB total, 100 files per deposit).

⚠️ **LaTeX Compilation**: Make sure your LaTeX file compiles successfully before running the script.

## Troubleshooting

### "pdflatex not found"
- Install a LaTeX distribution (MiKTeX, TeX Live, or MacTeX)
- Make sure `pdflatex` is in your PATH

### "Failed to create deposit"
- Check your API token is correct
- Make sure you're using the right environment (sandbox vs production)
- Check Zenodo API status

### "DOI already exists in file"
- The script detected a DOI already in your LaTeX file
- Remove it manually or the script will skip adding it

### "LaTeX compilation failed"
- Fix LaTeX errors first
- Make sure all required packages are installed
- Check that all input files are accessible

## API Documentation

For more details on Zenodo API:
- https://developers.zenodo.org/
- https://help.zenodo.org/

## License

This script is provided as-is for automating Zenodo workflows.
