#!/usr/bin/env python3
"""Analyze which files need to be added to Zenodo."""

import csv
from pathlib import Path

# Read DOI status
base_dir = Path(__file__).parent.parent
csv_file = base_dir / 'DOI_Status.csv'

files_needing_doi = []
files_with_doi = []
folders_with_doi = set()
folders_needing_doi = set()

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        folder = row['Folder']
        filename = row['File']
        has_doi = row['Has_DOI'] == 'Yes'
        
        if filename == 'no doi':
            folders_needing_doi.add(folder)
        elif has_doi:
            files_with_doi.append((folder, filename, row['DOI']))
            folders_with_doi.add(folder)
        else:
            files_needing_doi.append((folder, filename))
            folders_needing_doi.add(folder)

print("=" * 80)
print("ZENODO STATUS ANALYSIS")
print("=" * 80)
print()
print(f"Folders WITH at least one DOI: {len(folders_with_doi)}")
print(f"Folders NEEDING DOI: {len(folders_needing_doi)}")
print(f"Files WITH DOI: {len(files_with_doi)}")
print(f"Files NEEDING DOI: {len(files_needing_doi)}")
print()

print("=" * 80)
print("FOLDERS THAT NEED DOIs (no files with DOI in folder)")
print("=" * 80)
for folder in sorted(folders_needing_doi):
    if folder not in folders_with_doi:
        print(f"  {folder}")

print()
print("=" * 80)
print("FILES THAT NEED DOIs (in folders that already have some DOIs)")
print("=" * 80)
# Group by folder
by_folder = {}
for folder, filename in files_needing_doi:
    if folder not in by_folder:
        by_folder[folder] = []
    by_folder[folder].append(filename)

for folder in sorted(by_folder.keys()):
    if folder in folders_with_doi:
        print(f"\n[{folder}]")
        for filename in sorted(by_folder[folder]):
            print(f"  - {filename}")
