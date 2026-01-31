#!/usr/bin/env python3
"""
Update publication_type in all .zenodo.json config files.
Changes from "article" to "preprint" or "technicalnote".
"""

import json
from pathlib import Path

def update_publication_type(base_dir: Path, new_type: str = "preprint"):
    """Update publication_type in all .zenodo.json files."""
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    updated_count = 0
    skipped_count = 0
    
    print(f"Updating publication_type to '{new_type}' in all config files...")
    print()
    
    for config_file in sorted(config_files):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            current_type = config_data.get('publication_type', '')
            if current_type == new_type:
                skipped_count += 1
                continue
            
            config_data['publication_type'] = new_type
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"  Updated: {config_file.relative_to(base_dir)}")
            print(f"    {current_type} -> {new_type}")
            updated_count += 1
            
        except Exception as e:
            print(f"  ERROR: {config_file.relative_to(base_dir)} - {e}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Updated: {updated_count}")
    print(f"Already correct: {skipped_count}")
    print(f"Total: {len(config_files)}")

def update_template(base_dir: Path, new_type: str = "preprint"):
    """Update the template file as well."""
    template_file = base_dir / 'zenodo_config_template.json'
    
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template_data['publication_type'] = new_type
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            print(f"  Updated template: {template_file.name}")
            return True
        except Exception as e:
            print(f"  ERROR updating template: {e}")
            return False
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update publication_type in all Zenodo config files')
    parser.add_argument('--type', choices=['preprint', 'technicalnote'], default='preprint',
                       help='Publication type to set (default: preprint)')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Update Publication Type")
    print("=" * 80)
    print()
    
    # Update template first
    update_template(base_dir, args.type)
    print()
    
    # Update all config files
    update_publication_type(base_dir, args.type)

if __name__ == '__main__':
    main()
