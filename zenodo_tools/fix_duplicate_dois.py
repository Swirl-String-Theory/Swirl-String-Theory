#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix duplicate \\paperdoi commands in LaTeX files.
Keeps the first occurrence and removes subsequent ones.
Also ensures the DOI matches the one in the .zenodo.json config file.
"""

import json
import re
from pathlib import Path

def find_duplicate_dois(tex_file: Path) -> list:
    """Find all \paperdoi commands in a file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all \newcommand{\paperdoi}{...} patterns
        pattern = r'\\newcommand\{\\paperdoi\}\{([^}]+)\}'
        matches = list(re.finditer(pattern, content))
        
        return matches
    except Exception as e:
        print(f"  Error reading file: {e}")
        return []

def get_correct_doi(config_file: Path) -> str:
    """Get the correct DOI from the config file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data.get('doi', '')
    except:
        return ''

def fix_duplicate_dois(tex_file: Path, correct_doi: str = '') -> bool:
    """Remove duplicate \paperdoi commands, keeping only the first one."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all \newcommand{\paperdoi}{...} patterns
        pattern = r'\\newcommand\{\\paperdoi\}\{([^}]+)\}'
        matches = list(re.finditer(pattern, content))
        
        if len(matches) <= 1:
            # No duplicates
            return False
        
        print(f"  Found {len(matches)} \paperdoi commands")
        
        # Get the first DOI
        first_doi = matches[0].group(1)
        print(f"  First DOI: {first_doi}")
        
        # If we have a correct DOI from config, use that
        if correct_doi and correct_doi != first_doi:
            print(f"  Config DOI: {correct_doi} (different from first)")
            # Replace first occurrence with correct DOI
            content = re.sub(
                pattern,
                f'\\newcommand{{\\paperdoi}}{{{correct_doi}}}',
                content,
                count=1
            )
            # Remove all remaining occurrences
            content = re.sub(pattern, '', content)
        else:
            # Keep first, remove all others
            # Remove all but the first occurrence
            for i, match in enumerate(matches[1:], start=1):
                print(f"  Removing duplicate {i+1}: {match.group(1)}")
                # Remove this occurrence
                start, end = match.span()
                # Also remove any trailing newlines/whitespace
                content_before = content[:start]
                content_after = content[end:]
                # Remove trailing whitespace and newlines
                content_after = content_after.lstrip()
                if content_after.startswith('\n\n'):
                    content_after = content_after[2:]
                elif content_after.startswith('\n'):
                    content_after = content_after[1:]
                content = content_before + content_after
        
        # Write back
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        print(f"  Error fixing file: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Fixing Duplicate \\paperdoi Commands")
    print("=" * 80)
    print()
    
    # Find all .zenodo.json files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    fixed_count = 0
    checked_count = 0
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            doi = config_data.get('doi', '')
            tex_file_path = config_data.get('tex_file', '')
            
            if not doi:
                continue
            
            # Construct full path to tex file
            if tex_file_path:
                tex_file = base_dir / tex_file_path
            else:
                # Try to find tex file in same directory
                tex_file = config_file.with_suffix('.tex')
            
            if not tex_file.exists():
                continue
            
            checked_count += 1
            matches = find_duplicate_dois(tex_file)
            
            if len(matches) > 1:
                print(f"\n{tex_file.relative_to(base_dir)}")
                print(f"  Config DOI: {doi}")
                
                if fix_duplicate_dois(tex_file, doi):
                    fixed_count += 1
                    print(f"  [OK] Fixed")
            elif len(matches) == 1:
                # Check if DOI matches config
                found_doi = matches[0].group(1)
                if found_doi != doi:
                    print(f"\n{tex_file.relative_to(base_dir)}")
                    print(f"  Found DOI: {found_doi}")
                    print(f"  Config DOI: {doi}")
                    print(f"  Updating to match config...")
                    if fix_duplicate_dois(tex_file, doi):
                        fixed_count += 1
                        print(f"  [OK] Updated")
        
        except Exception as e:
            print(f"Error processing {config_file}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files checked: {checked_count}")
    print(f"Files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
