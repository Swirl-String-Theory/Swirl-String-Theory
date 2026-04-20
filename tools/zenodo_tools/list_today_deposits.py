#!/usr/bin/env python3
"""List all deposits created today and identify which config files exist."""

import json
import sys
from datetime import datetime
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

def main():
    base_dir = Path(__file__).parent.parent
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    print("=" * 80)
    print("Deposits Created Today")
    print("=" * 80)
    print()
    
    # Get all deposits
    all_deposits = automation.list_deposits(published_only=False, limit=100)
    
    # Filter to today (2026-01-27)
    today = datetime.now().date()
    today_deposits = []
    
    for deposit in all_deposits:
        created = deposit.get('created', '')
        if created:
            try:
                created_date = datetime.fromisoformat(created.replace('Z', '+00:00')).date()
                if created_date == today:
                    today_deposits.append(deposit)
            except:
                pass
    
    print(f"Total deposits found: {len(all_deposits)}")
    print(f"Deposits created today: {len(today_deposits)}")
    print()
    
    # Check which have config files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    config_dois = {}
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            doi = config_data.get('doi', '')
            if doi:
                config_dois[doi] = {
                    'config_file': str(config_file.relative_to(base_dir)),
                    'title': config_data.get('title', ''),
                    'tex_file': config_data.get('tex_file', '')
                }
        except:
            pass
    
    print(f"Config files found: {len(config_dois)}")
    print()
    
    # Group deposits
    with_config = []
    without_config = []
    
    for deposit in today_deposits:
        metadata = deposit.get('metadata', {})
        prereserve = metadata.get('prereserve_doi', {})
        doi = prereserve.get('doi', '') if prereserve else ''
        if not doi:
            doi = metadata.get('conceptdoi', '') or metadata.get('doi', '')
        
        deposit_id = deposit.get('id', 'N/A')
        title = metadata.get('title', 'Untitled')
        
        if doi in config_dois:
            with_config.append({
                'id': deposit_id,
                'doi': doi,
                'title': title,
                'config': config_dois[doi]['config_file']
            })
        else:
            without_config.append({
                'id': deposit_id,
                'doi': doi,
                'title': title
            })
    
    print("=" * 80)
    print(f"Deposits WITH Config Files: {len(with_config)}")
    print("=" * 80)
    for item in sorted(with_config, key=lambda x: int(x['id']), reverse=True)[:30]:
        print(f"  ID: {item['id']} | DOI: {item['doi']}")
        print(f"  Title: {item['title'][:70]}...")
        print(f"  Config: {item['config']}")
        print()
    
    if len(with_config) > 30:
        print(f"  ... and {len(with_config) - 30} more")
        print()
    
    print("=" * 80)
    print(f"Deposits WITHOUT Config Files: {len(without_config)}")
    print("=" * 80)
    print("(These might be duplicates or incorrectly created)")
    print()
    for item in sorted(without_config, key=lambda x: int(x['id']), reverse=True)[:30]:
        print(f"  ID: {item['id']} | DOI: {item['doi']}")
        print(f"  Title: {item['title'][:70]}...")
        print()
    
    if len(without_config) > 30:
        print(f"  ... and {len(without_config) - 30} more")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total deposits today: {len(today_deposits)}")
    print(f"  - With config files: {len(with_config)}")
    print(f"  - Without config files: {len(without_config)}")
    print()
    print("Note: The API only returns the last 100 deposits.")
    print("If you see 227 on Zenodo, there may be more deposits beyond the API limit.")

if __name__ == '__main__':
    main()
