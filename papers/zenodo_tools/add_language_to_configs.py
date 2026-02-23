#!/usr/bin/env python3
"""
Add language field to all .zenodo.json config files.
Sets language to "eng" (English) for all configs.
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

def add_language_to_config(config_file: Path, language: str = "eng") -> bool:
    """Add language field to a config file if it doesn't exist."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Check if language already exists
        if 'language' in config_data:
            if config_data['language'] == language:
                return False  # Already correct
            else:
                print(f"  Updating language: {config_data['language']} -> {language}")
        else:
            print(f"  Adding language: {language}")
        
        # Add/update language
        config_data['language'] = language
        
        # Write back
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"  Error updating {config_file.name}: {e}")
        return False

def update_template(base_dir: Path, language: str = "eng") -> bool:
    """Update the template file as well."""
    template_file = base_dir / 'zenodo_config_template.json'
    
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template_data['language'] = language
            
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
    
    parser = argparse.ArgumentParser(description='Add language field to all Zenodo config files')
    parser.add_argument('--language', default='eng', help='Language code (default: eng for English)')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Add Language to Config Files")
    print("=" * 80)
    print()
    print(f"Language: {args.language}")
    print()
    
    # Update template first
    update_template(base_dir, args.language)
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
        
        if add_language_to_config(config_file, args.language):
            updated_count += 1
            print(f"  [OK] Updated")
        else:
            skipped_count += 1
            print(f"  [SKIP] Already has correct language")
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
