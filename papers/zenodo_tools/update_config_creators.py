#!/usr/bin/env python3
"""
Update all .zenodo.json config files to include the standard creator information
from zenodo_config_template.json
"""

import json
import sys
from pathlib import Path

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

# Standard creator from template
STANDARD_CREATOR = {
    "name": "Omar Iskandarani",
    "affiliation": "Independent Researcher, Groningen, The Netherlands",
    "orcid": "0009-0006-1686-3961"
}

def update_config_file(config_path: Path) -> bool:
    """Update a config file with standard creator information."""
    try:
        # Read existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Check if creators need updating
        needs_update = False
        current_creators = config_data.get('creators', [])
        
        # Check if creators match the standard
        if not current_creators:
            needs_update = True
        else:
            # Check if first creator matches standard
            first_creator = current_creators[0] if current_creators else {}
            if (first_creator.get('name') != STANDARD_CREATOR['name'] or
                first_creator.get('affiliation') != STANDARD_CREATOR['affiliation'] or
                first_creator.get('orcid') != STANDARD_CREATOR['orcid']):
                needs_update = True
        
        if needs_update or len(current_creators) > 1:
            # Always use only the standard creator - remove any duplicates
            config_data['creators'] = [STANDARD_CREATOR.copy()]
            
            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"  Error updating {config_path.name}: {e}")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Updating Zenodo Config Files with Standard Creator Information")
    print("=" * 80)
    print()
    print(f"Standard Creator:")
    print(f"  Name: {STANDARD_CREATOR['name']}")
    print(f"  Affiliation: {STANDARD_CREATOR['affiliation']}")
    print(f"  ORCID: {STANDARD_CREATOR['orcid']}")
    print()
    
    # Find all .zenodo.json files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    print(f"Found {len(config_files)} config files")
    print()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for config_file in sorted(config_files):
        print(f"Processing: {config_file.relative_to(base_dir)}")
        
        if update_config_file(config_file):
            print(f"  [OK] Updated creators")
            updated_count += 1
        else:
            print(f"  [SKIP] Already has correct creator")
            skipped_count += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Updated: {updated_count}")
    print(f"Already correct: {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(config_files)}")

if __name__ == '__main__':
    main()
