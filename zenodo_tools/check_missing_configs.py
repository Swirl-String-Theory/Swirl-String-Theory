#!/usr/bin/env python3
"""
Check if all SST-xx.tex files have corresponding config files.
If not, try to fetch config from Zenodo using DOI from LaTeX file.
"""

import json
import re
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

def extract_doi_from_latex(tex_file: Path) -> str | None:
    """Extract DOI from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for \paperdoi{10.5281/zenodo.xxx}
        doi_match = re.search(r'\\paperdoi\{([^}]+)\}', content)
        if doi_match:
            return doi_match.group(1)
        
        # Look for \newcommand{\paperdoi}{10.5281/zenodo.xxx}
        doi_match = re.search(r'\\newcommand\{\\paperdoi\}\{([^}]+)\}', content)
        if doi_match:
            return doi_match.group(1)
        
        # Look for 10.5281/zenodo.xxx pattern
        doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
        if doi_match:
            return f"10.5281/zenodo.{doi_match.group(1)}"
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file: {e}")
        return None

def get_deposit_from_doi(automation: ZenodoAutomation, doi: str) -> dict | None:
    """Get deposit information from DOI."""
    try:
        # Extract record ID from DOI (10.5281/zenodo.1234567 -> 1234567)
        record_id = doi.split('.')[-1]
        
        # Try published record first
        url = f"{automation.base_url}/api/records/{record_id}"
        response = requests.get(url, headers=automation.headers)
        
        if response.status_code == 200:
            return response.json()
        
        # If not found, try draft deposit
        url = f"{automation.base_url}/api/deposit/depositions/{record_id}"
        response = requests.get(url, headers=automation.headers)
        
        if response.status_code == 200:
            deposit = response.json()
            # Convert deposit format to record-like format
            return {
                'id': deposit.get('id'),
                'metadata': deposit.get('metadata', {})
            }
        
        print(f"    Failed to get deposit: {response.status_code}")
        return None
    except Exception as e:
        print(f"    Error fetching deposit: {e}")
        return None

def create_config_from_zenodo(zenodo_record: dict, tex_file: Path, base_dir: Path) -> bool:
    """Create config file from Zenodo record."""
    try:
        metadata = zenodo_record.get('metadata', {})
        
        # Extract deposit ID (for drafts) or record ID (for published)
        record_id = zenodo_record.get('id', '')
        deposit_id = zenodo_record.get('id', '')  # Same for published records
        
        # Get DOI
        doi = metadata.get('doi', '')
        if not doi:
            prereserve = metadata.get('prereserve_doi', {})
            doi = prereserve.get('doi', '') if prereserve else ''
        
        # Create config data
        config_data = {
            "title": metadata.get('title', 'Untitled'),
            "creators": metadata.get('creators', []),
            "description": metadata.get('description', ''),
            "keywords": metadata.get('keywords', []),
            "publication_date": metadata.get('publication_date', ''),
            "doi": doi,
            "tex_file": str(tex_file.relative_to(base_dir)),
            "upload_type": metadata.get('upload_type', 'publication'),
            "publication_type": metadata.get('publication_type', 'preprint'),
            "access_right": metadata.get('access_right', 'open'),
            "license": metadata.get('license', 'cc-by-4.0'),
            "deposit_id": str(deposit_id)
        }
        
        # Add language if present
        if metadata.get('language'):
            config_data['language'] = metadata['language']
        else:
            config_data['language'] = 'eng'
        
        # Add communities if present
        if metadata.get('communities'):
            config_data['communities'] = metadata['communities']
        
        # Write config file
        config_file = tex_file.with_suffix('.zenodo.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"    Error creating config: {e}")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Check Missing Config Files for SST-xx.tex")
    print("=" * 80)
    print()
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Find all SST-xx folders
    sst_folders = []
    for folder in base_dir.iterdir():
        if folder.is_dir() and re.match(r'^SST-\d+', folder.name):
            sst_folders.append(folder)
    
    sst_folders.sort(key=lambda x: x.name)
    
    print(f"Found {len(sst_folders)} SST-xx folders")
    print()
    
    missing_configs = []
    found_configs = []
    
    for folder in sst_folders:
        folder_name = folder.name
        expected_tex = folder / f"{folder_name}.tex"
        expected_config = folder / f"{folder_name}.zenodo.json"
        
        if expected_tex.exists():
            if expected_config.exists():
                found_configs.append((folder_name, expected_tex, expected_config))
            else:
                missing_configs.append((folder_name, expected_tex, expected_config))
    
    print(f"Files with config: {len(found_configs)}")
    print(f"Files missing config: {len(missing_configs)}")
    print()
    
    if not missing_configs:
        print("All SST-xx.tex files have config files!")
        return
    
    print("=" * 80)
    print("Files Missing Config Files")
    print("=" * 80)
    print()
    
    for folder_name, tex_file, config_file in missing_configs:
        print(f"Checking: {folder_name}")
        print(f"  LaTeX: {tex_file.name}")
        
        # Try to extract DOI from LaTeX
        doi = extract_doi_from_latex(tex_file)
        
        if doi:
            print(f"  Found DOI: {doi}")
            
            # Get deposit from Zenodo
            print(f"  Fetching from Zenodo...")
            record = get_deposit_from_doi(automation, doi)
            
            if record:
                print(f"  [OK] Found record on Zenodo")
                
                # Create config file
                if create_config_from_zenodo(record, tex_file, base_dir):
                    print(f"  [OK] Created config file: {config_file.name}")
                else:
                    print(f"  [ERROR] Failed to create config file")
            else:
                print(f"  [ERROR] Record not found on Zenodo")
        else:
            print(f"  [SKIP] No DOI found in LaTeX file")
        
        print()
    
    # Count actually created configs
    created_count = 0
    for folder_name, tex_file, config_file in missing_configs:
        if config_file.exists():
            created_count += 1
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files with config: {len(found_configs)}")
    print(f"Files missing config: {len(missing_configs)}")
    print(f"Configs created: {created_count}")
    print(f"Still missing: {len(missing_configs) - created_count}")

if __name__ == '__main__':
    main()
