#!/usr/bin/env python3
"""Check if files with DOI but not published are drafts on Zenodo."""

import csv
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

# Read files with DOI but not online
base_dir = Path(__file__).parent.parent
csv_file = base_dir / 'zenodo_comparison.csv'
has_doi_not_online = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Status'] == 'HAS_DOI_NOT_ONLINE' and row['DOI']:
            has_doi_not_online.append({
                'file': f"{row['Folder']}\\{row['File']}",
                'doi': row['DOI'].strip()
            })

print("=" * 80)
print("Checking if files with DOI but not published are drafts on Zenodo")
print("=" * 80)
print()

token = read_token_from_zenodo_py()
if not token:
    print("Error: No Zenodo token found")
    exit(1)

automation = ZenodoAutomation(token, sandbox=False)

# Get all deposits (including drafts)
print("Fetching all deposits (published + drafts)...")
all_deposits = automation.list_deposits(published_only=False, limit=100)

# Create a mapping of DOI to deposit info
doi_to_deposit = {}
for deposit in all_deposits:
    metadata = deposit.get('metadata', {})
    doi = metadata.get('doi', '')
    conceptdoi = metadata.get('conceptdoi', '')
    submitted = deposit.get('submitted', False)
    
    if doi:
        doi_to_deposit[doi] = {
            'id': deposit.get('id'),
            'title': metadata.get('title', 'Untitled'),
            'submitted': submitted,
            'url': deposit.get('links', {}).get('html', ''),
            'state': 'published' if submitted else 'draft'
        }
    if conceptdoi:
        doi_to_deposit[conceptdoi] = {
            'id': deposit.get('id'),
            'title': metadata.get('title', 'Untitled'),
            'submitted': submitted,
            'url': deposit.get('links', {}).get('html', ''),
            'state': 'published' if submitted else 'draft'
        }

print(f"Found {len(doi_to_deposit)} deposits with DOIs\n")

# Check each file
found_as_draft = []
found_as_published = []
not_found = []

for item in has_doi_not_online:
    doi = item['doi']
    if doi in doi_to_deposit:
        deposit_info = doi_to_deposit[doi]
        if deposit_info['state'] == 'draft':
            found_as_draft.append({
                'file': item['file'],
                'doi': doi,
                'deposit_id': deposit_info['id'],
                'title': deposit_info['title'],
                'url': deposit_info['url']
            })
        else:
            found_as_published.append({
                'file': item['file'],
                'doi': doi,
                'title': deposit_info['title'],
                'url': deposit_info['url']
            })
    else:
        not_found.append(item)

print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

if found_as_draft:
    print(f"✓ Found as DRAFTS on Zenodo ({len(found_as_draft)}):")
    print()
    for item in found_as_draft:
        print(f"  {item['file']}")
        print(f"    DOI: {item['doi']}")
        print(f"    Title: {item['title']}")
        print(f"    Deposit ID: {item['deposit_id']}")
        print(f"    URL: {item['url']}")
        print()

if found_as_published:
    print(f"⚠ Found as PUBLISHED on Zenodo ({len(found_as_published)}):")
    print("  (These might be different versions or the comparison missed them)")
    print()
    for item in found_as_published:
        print(f"  {item['file']}")
        print(f"    DOI: {item['doi']}")
        print(f"    Title: {item['title']}")
        print(f"    URL: {item['url']}")
        print()

if not_found:
    print(f"✗ NOT FOUND on Zenodo ({len(not_found)}):")
    print("  (These DOIs don't exist as deposits - might be old/invalid)")
    print()
    for item in not_found:
        print(f"  {item['file']}")
        print(f"    DOI: {item['doi']}")
        print()
