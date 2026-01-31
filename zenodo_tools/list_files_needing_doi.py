#!/usr/bin/env python3
"""List all files that need DOIs."""

import csv
from collections import defaultdict
from pathlib import Path

base_dir = Path(__file__).parent.parent
csv_file = base_dir / 'zenodo_comparison.csv'

if not csv_file.exists():
    print("Error: zenodo_comparison.csv not found. Run compare_local_zenodo.py first.")
    exit(1)

files_needing_doi = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Status'] == 'NEEDS_DOI':
            files_needing_doi.append({
                'folder': row['Folder'],
                'file': row['File']
            })

# Group by folder
by_folder = defaultdict(list)
for item in files_needing_doi:
    by_folder[item['folder']].append(item['file'])

print("=" * 80)
print(f"FILES NEEDING DOIs ({len(files_needing_doi)} total)")
print("=" * 80)
print()

for folder in sorted(by_folder.keys()):
    files = sorted(set(by_folder[folder]))  # Remove duplicates
    print(f"[{folder}]")
    for filename in files:
        print(f"  - {filename}")
    print()

print(f"\nTotal: {len(files_needing_doi)} files in {len(by_folder)} folders")
