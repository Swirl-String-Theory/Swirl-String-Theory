#!/usr/bin/env python3
"""
Script to organize all Zenodo-related scripts into zenodo_tools/ directory
and update all path references.
"""

import re
import shutil
from pathlib import Path

# Scripts to move
ZENODO_SCRIPTS = [
    'zenodo_automation.py',
    'create_zenodo_configs.py',
    'smart_zenodo_workflow.py',
    'zenodo_gui.py',
    'compare_local_zenodo.py',
    'cleanup_duplicate_deposits.py',
    'check_recent_deposits.py',
    'list_today_deposits.py',
    'quick_review.py',
    'render_new_doi_files.py',
    'fix_duplicate_dois.py',
    'check_actual_doi_status.py',
    'process_specific_files.py',
    'render_three_files.py',
    'list_files_without_doi.py',
    'list_files_needing_doi.py',
    'check_dois.py',
    'analyze_zenodo_status.py',
    'list_zenodo_papers.py',
    'zenodo_example.py',
    'check_drafts.py',
    'process_failed_files.py',
    'process_sst23.py',
    'process_sst33_enhanced.py',
]

base_dir = Path(r'c:\workspace\projects\SwirlStringTheory')
tools_dir = base_dir / 'zenodo_tools'

def update_paths_in_file(file_path: Path):
    """Update path references in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update base_dir - change from hardcoded path to relative
        # Pattern: base_dir = Path(r'c:\workspace\projects\SwirlStringTheory')
        content = re.sub(
            r"base_dir\s*=\s*Path\(r'c:\\workspace\\projects\\SwirlStringTheory'\)",
            "base_dir = Path(__file__).parent.parent",
            content
        )
        
        # Also handle self.base_dir in classes
        content = re.sub(
            r"self\.base_dir\s*=\s*Path\(r'c:\\workspace\\projects\\SwirlStringTheory'\)",
            "self.base_dir = Path(__file__).parent.parent",
            content
        )
        
        # Update zenodo.py path if needed (should still be ../zenodo.py)
        # But if it says ../../zenodo.py, change to ../zenodo.py
        content = re.sub(
            r"\.\.\/\.\.\/zenodo\.py",
            "../zenodo.py",
            content
        )
        
        # Update imports - if importing from create_zenodo_configs, make sure it's relative
        # Most imports should work since files are in same directory now
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Updated paths in {file_path.name}")
            return True
        else:
            print(f"  No changes needed in {file_path.name}")
            return False
    except Exception as e:
        print(f"  Error updating {file_path.name}: {e}")
        return False

def main():
    print("=" * 80)
    print("Organizing Zenodo Scripts")
    print("=" * 80)
    print()
    
    # Ensure tools directory exists
    tools_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    updated_count = 0
    
    for script_name in ZENODO_SCRIPTS:
        script_path = base_dir / script_name
        
        if script_path.exists():
            print(f"Moving {script_name}...")
            dest_path = tools_dir / script_name
            
            # Move file
            shutil.move(str(script_path), str(dest_path))
            moved_count += 1
            
            # Update paths in file
            if update_paths_in_file(dest_path):
                updated_count += 1
        else:
            print(f"  {script_name} not found, skipping")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Moved {moved_count} scripts")
    print(f"Updated {updated_count} scripts")
    print()
    print(f"All scripts are now in: {tools_dir}")
    print("Path references have been updated to use relative paths.")
    print()
    print("Note: Scripts now use Path(__file__).parent.parent to find the SST root.")

if __name__ == '__main__':
    main()
