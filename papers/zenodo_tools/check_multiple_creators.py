#!/usr/bin/env python3
"""Check for config files with multiple creators."""

import json
import sys
from pathlib import Path

# Handle encoding
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Checking for Config Files with Multiple Creators")
    print("=" * 80)
    print()
    
    config_files = list(base_dir.rglob('*.zenodo.json'))
    files_with_multiple = []
    
    for config_file in sorted(config_files):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            creators = config_data.get('creators', [])
            if len(creators) > 1:
                files_with_multiple.append({
                    'file': str(config_file.relative_to(base_dir)),
                    'count': len(creators),
                    'creators': creators
                })
        except Exception as e:
            print(f"Error reading {config_file.name}: {e}")
    
    if files_with_multiple:
        print(f"Found {len(files_with_multiple)} files with multiple creators:")
        print()
        for item in files_with_multiple:
            print(f"  {item['file']} ({item['count']} creators)")
            for i, creator in enumerate(item['creators'], 1):
                name = creator.get('name', 'Unknown')
                affiliation = creator.get('affiliation', 'No affiliation')
                orcid = creator.get('orcid', 'No ORCID')
                print(f"    {i}. {name} | {affiliation} | {orcid}")
            print()
    else:
        print("[OK] All config files have only one creator!")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
