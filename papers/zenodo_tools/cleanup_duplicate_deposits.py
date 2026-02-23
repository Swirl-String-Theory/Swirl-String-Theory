#!/usr/bin/env python3
"""
Identify and optionally delete duplicate/unwanted Zenodo deposits.
Only deletes drafts that don't have corresponding config files.
"""

import argparse
import json
import sys
import requests
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

# Handle encoding
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def delete_deposit(automation, deposit_id: str) -> bool:
    """Delete a draft deposit."""
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
    response = requests.delete(url, headers=automation.headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"    Error deleting {deposit_id}: {response.status_code} - {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Delete duplicate Zenodo deposits')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation and delete automatically')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    print("=" * 80)
    print("Identifying Duplicate/Unwanted Deposits")
    print("=" * 80)
    print()
    
    # Get all config files and their DOIs
    config_files = list(base_dir.rglob('*.zenodo.json'))
    valid_dois = set()
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            doi = config_data.get('doi', '')
            if doi:
                valid_dois.add(doi)
        except:
            pass
    
    print(f"Valid DOIs from config files: {len(valid_dois)}")
    print()
    
    # Get all deposits
    all_deposits = automation.list_deposits(published_only=False, limit=100)
    drafts = [d for d in all_deposits if not d.get('submitted', False)]
    
    print(f"Total draft deposits: {len(drafts)}")
    print()
    
    # Find deposits without valid config files
    deposits_to_delete = []
    
    for deposit in drafts:
        metadata = deposit.get('metadata', {})
        prereserve = metadata.get('prereserve_doi', {})
        doi = prereserve.get('doi', '') if prereserve else ''
        if not doi:
            doi = metadata.get('conceptdoi', '') or metadata.get('doi', '')
        
        deposit_id = deposit.get('id', 'N/A')
        title = metadata.get('title', 'Untitled')
        
        if doi not in valid_dois:
            deposits_to_delete.append({
                'id': deposit_id,
                'doi': doi,
                'title': title
            })
    
    print("=" * 80)
    print(f"Deposits to Delete: {len(deposits_to_delete)}")
    print("=" * 80)
    print()
    
    if not deposits_to_delete:
        print("No deposits to delete - all have config files!")
        return
    
    # Show first 20
    for i, item in enumerate(sorted(deposits_to_delete, key=lambda x: int(x['id']), reverse=True)[:20], 1):
        print(f"{i}. ID: {item['id']} | DOI: {item['doi']}")
        print(f"   Title: {item['title'][:70]}...")
        print()
    
    if len(deposits_to_delete) > 20:
        print(f"... and {len(deposits_to_delete) - 20} more")
        print()
    
    # Ask for confirmation (unless --yes flag)
    if not args.yes:
        print("=" * 80)
        print("WARNING: This will DELETE draft deposits from Zenodo!")
        print("=" * 80)
        print()
        print(f"Found {len(deposits_to_delete)} deposits without config files.")
        print("These appear to be duplicates or incorrectly created.")
        print()
        response = input("Do you want to DELETE these deposits? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Cancelled. No deposits deleted.")
            return
    else:
        print("=" * 80)
        print(f"Auto-deleting {len(deposits_to_delete)} duplicate deposits...")
        print("=" * 80)
        print()
    
    # Delete deposits
    print("\nDeleting deposits...")
    deleted_count = 0
    failed_count = 0
    
    for item in sorted(deposits_to_delete, key=lambda x: int(x['id']), reverse=True):
        deposit_id = item['id']
        print(f"  Deleting {deposit_id}...", end=' ')
        if delete_deposit(automation, deposit_id):
            print("OK")
            deleted_count += 1
        else:
            print("FAILED")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully deleted: {deleted_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(deposits_to_delete)}")

if __name__ == '__main__':
    main()
