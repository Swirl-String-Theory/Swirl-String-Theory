#!/usr/bin/env python3
"""Quick review of Zenodo deposit situation."""

import json
import sys
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
    print("QUICK REVIEW: Zenodo Deposit Situation")
    print("=" * 80)
    print()
    
    # Count config files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    valid_dois = set()
    config_titles = {}
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            doi = config_data.get('doi', '')
            if doi:
                valid_dois.add(doi)
                config_titles[doi] = config_data.get('title', '')[:60]
        except:
            pass
    
    print(f"✓ Config files found locally: {len(config_files)}")
    print(f"  (These are the legitimate papers with DOIs)")
    print()
    
    # Get deposits from Zenodo
    all_deposits = automation.list_deposits(published_only=False, limit=100)
    drafts = [d for d in all_deposits if not d.get('submitted', False)]
    
    print(f"⚠ Draft deposits on Zenodo (API limit 100): {len(drafts)}")
    print()
    
    # Count duplicates
    deposits_with_config = 0
    deposits_without_config = 0
    
    for deposit in drafts:
        metadata = deposit.get('metadata', {})
        prereserve = metadata.get('prereserve_doi', {})
        doi = prereserve.get('doi', '') if prereserve else ''
        if not doi:
            doi = metadata.get('conceptdoi', '') or metadata.get('doi', '')
        
        if doi in valid_dois:
            deposits_with_config += 1
        else:
            deposits_without_config += 1
    
    print("=" * 80)
    print("BREAKDOWN:")
    print("=" * 80)
    print(f"  ✓ Legitimate (have config files): {deposits_with_config}")
    print(f"  ✗ Duplicates/Errors (no config):   {deposits_without_config}")
    print(f"  ────────────────────────────────────────────")
    print(f"  Total visible via API:              {len(drafts)}")
    print()
    print(f"  ⚠ You mentioned seeing 227 on Zenodo")
    print(f"     (API only shows last 100, so {227 - 100} more exist)")
    print()
    
    # Show some examples
    print("=" * 80)
    print("SAMPLE: Recent deposits WITHOUT config files (duplicates):")
    print("=" * 80)
    count = 0
    for deposit in sorted(drafts, key=lambda x: int(x.get('id', 0)), reverse=True):
        if count >= 5:
            break
        metadata = deposit.get('metadata', {})
        prereserve = metadata.get('prereserve_doi', {})
        doi = prereserve.get('doi', '') if prereserve else ''
        if not doi:
            doi = metadata.get('conceptdoi', '') or metadata.get('doi', '')
        
        if doi not in valid_dois:
            title = metadata.get('title', 'Untitled')
            deposit_id = deposit.get('id', 'N/A')
            print(f"  ID: {deposit_id} | {title[:65]}...")
            count += 1
    
    print()
    print("=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print(f"  Run 'cleanup_duplicate_deposits.py' to delete {deposits_without_config}+ duplicates")
    print("  This will keep only the {deposits_with_config} legitimate deposits with config files.")
    print("=" * 80)

if __name__ == '__main__':
    main()
