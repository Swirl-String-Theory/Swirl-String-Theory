#!/usr/bin/env python3
"""List all files that still need DOIs."""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

def check_doi_in_latex(tex_file: Path) -> bool:
    """Check if file has a valid DOI."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for DOI pattern
        if re.search(r'10\.5281/zenodo\.\d+', content):
            # Check it's not a placeholder
            if not re.search(r'zenodo\.(xxx+|xxxx+|xxxxxxxx+)', content, re.IGNORECASE):
                return True
        return False
    except:
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Files Still Without DOI")
    print("=" * 80)
    print()
    
    # Read from zenodo_comparison.csv
    csv_file = base_dir / 'zenodo_comparison.csv'
    files_needing_doi = []
    
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Status'] == 'NEEDS_DOI':
                    folder = row['Folder']
                    filename = row['File']
                    if folder and folder != '.':
                        full_path = base_dir / folder / filename
                    else:
                        full_path = base_dir / filename
                    
                    if full_path.exists():
                        files_needing_doi.append({
                            'folder': folder,
                            'file': filename,
                            'path': full_path
                        })
    
    # Also check files with .zenodo.json but no DOI in LaTeX
    config_files = list(base_dir.rglob('*.zenodo.json'))
    files_with_config_but_no_doi = []
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            doi = config_data.get('doi', '')
            tex_file_path = config_data.get('tex_file', '')
            
            if not doi:
                continue
            
            # Construct full path to tex file
            if tex_file_path:
                tex_file = base_dir / tex_file_path
            else:
                tex_file = config_file.with_suffix('.tex')
            
            if tex_file.exists():
                if not check_doi_in_latex(tex_file):
                    files_with_config_but_no_doi.append({
                        'folder': str(tex_file.parent.relative_to(base_dir)),
                        'file': tex_file.name,
                        'path': tex_file,
                        'config_doi': doi
                    })
        except:
            pass
    
    # Group by folder
    by_folder = defaultdict(list)
    for item in files_needing_doi:
        by_folder[item['folder']].append(item)
    
    print(f"Files with NEEDS_DOI status: {len(files_needing_doi)}")
    print(f"Files with config but no DOI in LaTeX: {len(files_with_config_but_no_doi)}")
    print()
    
    if files_needing_doi:
        print("=" * 80)
        print("FILES FROM CSV (NEEDS_DOI status)")
        print("=" * 80)
        print()
        
        for folder in sorted(by_folder.keys()):
            files = sorted(by_folder[folder], key=lambda x: x['file'])
            print(f"[{folder}]")
            for item in files:
                print(f"  - {item['file']}")
            print()
    
    if files_with_config_but_no_doi:
        print("=" * 80)
        print("FILES WITH CONFIG BUT NO DOI IN LATEX")
        print("=" * 80)
        print("(These have .zenodo.json files with DOIs, but the DOI is not in the LaTeX file)")
        print()
        
        by_folder_config = defaultdict(list)
        for item in files_with_config_but_no_doi:
            by_folder_config[item['folder']].append(item)
        
        for folder in sorted(by_folder_config.keys()):
            files = sorted(by_folder_config[folder], key=lambda x: x['file'])
            print(f"[{folder}]")
            for item in files:
                print(f"  - {item['file']} (Config DOI: {item['config_doi']})")
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files needing DOI: {len(files_needing_doi) + len(files_with_config_but_no_doi)}")
    print(f"  - From CSV (NEEDS_DOI): {len(files_needing_doi)}")
    print(f"  - With config but missing in LaTeX: {len(files_with_config_but_no_doi)}")

if __name__ == '__main__':
    main()
