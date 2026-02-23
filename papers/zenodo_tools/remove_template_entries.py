#!/usr/bin/env python3
"""
Remove Zenodo entries and config files for template files (journal.tex).
These are templates, not actual papers.
"""

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

def delete_deposit(automation: ZenodoAutomation, deposit_id: str) -> bool:
    """Delete a deposit from Zenodo."""
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
    response = requests.delete(url, headers=automation.headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"    [ERROR] Failed to delete deposit: {response.status_code}")
        print(f"      Error: {response.text}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove template entries (journal.tex) from Zenodo and delete config files')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation and delete automatically')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Remove Template Entries (journal.tex)")
    print("=" * 80)
    print()
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Find all config files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    # Find config files that reference journal.tex
    template_configs = []
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            tex_file = config_data.get('tex_file', '')
            if tex_file and 'journal.tex' in tex_file:
                template_configs.append((config_file, config_data))
        except:
            pass
    
    if not template_configs:
        print("No template config files found.")
        return
    
    print(f"Found {len(template_configs)} template config file(s):")
    print()
    
    for config_file, config_data in template_configs:
        deposit_id = config_data.get('deposit_id', 'N/A')
        title = config_data.get('title', 'Untitled')
        tex_file = config_data.get('tex_file', 'N/A')
        
        print(f"  Config: {config_file.relative_to(base_dir)}")
        print(f"    Title: {title}")
        print(f"    Tex file: {tex_file}")
        print(f"    Deposit ID: {deposit_id}")
        print()
    
    # Ask for confirmation
    if not args.yes:
        try:
            response = input(f"Delete {len(template_configs)} deposit(s) from Zenodo and remove config file(s)? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return
        except EOFError:
            print("No input available. Use --yes flag to delete automatically.")
            return
    
    print()
    print("Deleting deposits and config files...")
    print()
    
    deleted_deposits = 0
    deleted_configs = 0
    errors = 0
    
    for config_file, config_data in template_configs:
        deposit_id = config_data.get('deposit_id', '')
        title = config_data.get('title', 'Untitled')
        
        print(f"Processing: {config_file.name}")
        
        # Delete from Zenodo if deposit_id exists
        if deposit_id:
            print(f"  Deleting deposit {deposit_id} from Zenodo...")
            if delete_deposit(automation, deposit_id):
                print(f"    [OK] Deleted deposit")
                deleted_deposits += 1
            else:
                print(f"    [ERROR] Failed to delete deposit")
                errors += 1
        else:
            print(f"  [SKIP] No deposit_id in config")
        
        # Delete config file
        try:
            config_file.unlink()
            print(f"  [OK] Deleted config file")
            deleted_configs += 1
        except Exception as e:
            print(f"  [ERROR] Failed to delete config file: {e}")
            errors += 1
        
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Deleted deposits: {deleted_deposits}")
    print(f"Deleted config files: {deleted_configs}")
    print(f"Errors: {errors}")
    print(f"Total processed: {len(template_configs)}")

if __name__ == '__main__':
    main()
