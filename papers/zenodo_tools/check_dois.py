#!/usr/bin/env python3
"""
Script to check all LaTeX files for DOI entries in their preambles.
"""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict

def extract_preamble(file_path):
    """Extract the preamble including abstract (everything up to and including abstract section)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find positions of key markers
        doc_start = content.find('\\begin{document}')
        abstract_end = content.find('\\end{abstract}')
        
        # If abstract exists and comes after \begin{document}, search up to abstract end
        if abstract_end != -1:
            if doc_start == -1 or abstract_end > doc_start:
                # Abstract is after document start or document start doesn't exist
                # Include everything up to and including the abstract
                return content[:abstract_end + len('\\end{abstract}')]
        
        # If no abstract or abstract comes before document, search up to \begin{document}
        if doc_start != -1:
            return content[:doc_start]
        
        # If no \begin{document}, use entire file
        return content
    except Exception as e:
        return None

def find_doi_in_preamble(preamble):
    r"""Search for DOI pattern 10.5281/zenodo.xxx anywhere in the preamble."""
    if not preamble:
        return None
    
    # Search for the pattern 10.5281/zenodo. followed by digits anywhere in the preamble
    # This will catch all formats: \newcommand{\paperdoi}{...}, %! DOI = ..., DOI: ..., etc.
    doi_pattern = r'10\.5281/zenodo\.(\d+)'
    match = re.search(doi_pattern, preamble, re.IGNORECASE)
    
    if match:
        doi = match.group(0)  # Get the full match (10.5281/zenodo.xxxxx)
        # Exclude placeholder patterns like zenodo.xxx, zenodo.xxxx, zenodo.xxxxxxxx
        if not re.search(r'zenodo\.(xxx+|xxxx+|xxxxxxxx+)', doi, re.IGNORECASE):
            return doi
    
    return None

def main():
    base_dir = Path(__file__).parent.parent
    
    results = []
    doi_to_files = defaultdict(list)
    
    # Find all .tex files
    tex_files = list(base_dir.rglob('*.tex'))
    
    print(f"Found {len(tex_files)} LaTeX files. Scanning for DOIs...\n")
    
    for tex_file in sorted(tex_files):
        relative_path = tex_file.relative_to(base_dir)
        
        # Only process files that contain \begin{document} (exclude input files)
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if '\\begin{document}' not in content:
                continue  # Skip input files that don't have \begin{document}
        except Exception:
            continue  # Skip files that can't be read
        
        preamble = extract_preamble(tex_file)
        doi = find_doi_in_preamble(preamble)
        
        results.append({
            'file': str(relative_path),
            'doi': doi
        })
        
        if doi:
            doi_to_files[doi].append(str(relative_path))
    
    # Group by folder
    folder_results = defaultdict(list)
    
    for r in results:
        # Extract folder path (everything before the last backslash)
        file_path = r['file']
        if '\\' in file_path:
            folder = '\\'.join(file_path.split('\\')[:-1])
        else:
            folder = '.'  # Root level files
        folder_results[folder].append(r)
    
    # Write CSV file with folder grouping
    csv_path = base_dir / 'DOI_Status.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Folder', 'File', 'Has_DOI', 'DOI', 'Is_Duplicate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort folders
        for folder in sorted(folder_results.keys()):
            folder_files = folder_results[folder]
            
            # Check if folder has any DOI
            has_any_doi = any(f['doi'] for f in folder_files)
            
            if has_any_doi:
                # Only show files with DOI
                for r in sorted(folder_files, key=lambda x: x['file']):
                    if r['doi']:  # Only include files with DOI
                        doi = r['doi']
                        is_duplicate = 'Yes' if len(doi_to_files.get(doi, [])) > 1 else 'No'
                        # Extract just the filename
                        filename = r['file'].split('\\')[-1]
                        writer.writerow({
                            'Folder': folder,
                            'File': filename,
                            'Has_DOI': 'Yes',
                            'DOI': doi,
                            'Is_Duplicate': is_duplicate
                        })
            else:
                # Folder has no DOI - show "no doi"
                writer.writerow({
                    'Folder': folder,
                    'File': 'no doi',
                    'Has_DOI': 'No',
                    'DOI': '',
                    'Is_Duplicate': 'No'
                })
    
    print(f"CSV report written to: {csv_path}\n")
    
    # Print results
    print("=" * 100)
    print("DOI STATUS REPORT")
    print("=" * 100)
    print(f"\nTotal files scanned: {len(results)}\n")
    
    # Files with DOI
    with_doi = [r for r in results if r['doi']]
    without_doi = [r for r in results if not r['doi']]
    
    print(f"Files WITH DOI: {len(with_doi)}")
    print(f"Files WITHOUT DOI: {len(without_doi)}\n")
    
    # Check for duplicates
    duplicates = {doi: files for doi, files in doi_to_files.items() if len(files) > 1}
    
    if duplicates:
        print("=" * 100)
        print("DUPLICATE DOIs FOUND:")
        print("=" * 100)
        for doi, files in sorted(duplicates.items()):
            print(f"\nDOI: {doi}")
            for file in files:
                print(f"  - {file}")
        print()
    else:
        print("No duplicate DOIs found.\n")
    
    # Detailed list grouped by folder
    print("=" * 100)
    print("DETAILED LIST (Grouped by Folder):")
    print("=" * 100)
    
    for folder in sorted(folder_results.keys()):
        folder_files = folder_results[folder]
        has_any_doi = any(f['doi'] for f in folder_files)
        
        print(f"\n[{folder}]")
        if has_any_doi:
            # Show only files with DOI
            for r in sorted(folder_files, key=lambda x: x['file']):
                if r['doi']:
                    duplicate_marker = " [DUPLICATE]" if len(doi_to_files.get(r['doi'], [])) > 1 else ""
                    filename = r['file'].split('\\')[-1]  # Just the filename
                    print(f"  {filename}{duplicate_marker}")
                    print(f"    DOI: {r['doi']}")
        else:
            print(f"  no doi")
    
    # Summary statistics
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total files: {len(results)}")
    print(f"With DOI: {len(with_doi)} ({100*len(with_doi)/len(results):.1f}%)")
    print(f"Without DOI: {len(without_doi)} ({100*len(without_doi)/len(results):.1f}%)")
    print(f"Unique DOIs: {len(doi_to_files)}")
    print(f"Duplicate DOIs: {len(duplicates)}")

if __name__ == '__main__':
    main()
