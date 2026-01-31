#!/usr/bin/env python3
"""Check which files actually have DOIs in their LaTeX files."""

import json
import re
from pathlib import Path
from collections import defaultdict

def has_doi_in_latex(tex_file: Path) -> tuple[bool, str]:
    """Check if file has a valid DOI. Returns (has_doi, doi_or_empty)."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for DOI pattern - look anywhere in the file
        doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
        if doi_match:
            doi = doi_match.group(0)
            # Check it's not a placeholder (must have actual digits)
            if re.match(r'10\.5281/zenodo\.\d+$', doi):
                return True, doi
        return False, ''
    except:
        return False, ''

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Files Without DOI (Actual Status)")
    print("=" * 80)
    print()
    
    # Check all .tex files in SST-xx folders
    tex_files = []
    for folder in base_dir.iterdir():
        if folder.is_dir() and re.match(r'^SST-\d+', folder.name):
            for tex_file in folder.rglob('*.tex'):
                if tex_file.is_file():
                    # Only standalone documents
                    try:
                        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        if '\\begin{document}' not in content:
                            continue
                        if '\\title' not in content and '\\papertitle' not in content:
                            continue
                        # Exclude cover letters
                        if 'coverletter' in tex_file.name.lower() or 'cover_letter' in tex_file.name.lower():
                            continue
                        tex_files.append(tex_file)
                    except:
                        continue
    
    files_without_doi = []
    files_with_doi = []
    
    for tex_file in tex_files:
        has_doi, doi = has_doi_in_latex(tex_file)
        folder = str(tex_file.parent.relative_to(base_dir))
        filename = tex_file.name
        
        if has_doi:
            files_with_doi.append({
                'folder': folder,
                'file': filename,
                'doi': doi
            })
        else:
            files_without_doi.append({
                'folder': folder,
                'file': filename
            })
    
    # Group by folder
    by_folder = defaultdict(list)
    for item in files_without_doi:
        by_folder[item['folder']].append(item['file'])
    
    print(f"Files WITH DOI: {len(files_with_doi)}")
    print(f"Files WITHOUT DOI: {len(files_without_doi)}")
    print()
    
    if files_without_doi:
        print("=" * 80)
        print("FILES WITHOUT DOI")
        print("=" * 80)
        print()
        
        for folder in sorted(by_folder.keys()):
            files = sorted(by_folder[folder])
            print(f"[{folder}]")
            for filename in files:
                print(f"  - {filename}")
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files checked: {len(tex_files)}")
    print(f"Files with DOI: {len(files_with_doi)}")
    print(f"Files without DOI: {len(files_without_doi)}")
    print(f"Folders with files needing DOI: {len(by_folder)}")

if __name__ == '__main__':
    main()
