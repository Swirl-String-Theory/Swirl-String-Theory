#!/usr/bin/env python3
"""Create Zenodo config for SST-33_Enhanced_Heat_Transport_via_Swirl_Coupling.tex"""

import json
import re
import sys
import time
import requests
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py
from create_zenodo_configs import extract_metadata_from_latex, add_doi_to_latex

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
    tex_file = base_dir / 'SST-33_Heat_Transport' / 'SST-33_Enhanced_Heat_Transport_via_Swirl_Coupling.tex'
    
    print("=" * 80)
    print("Creating Zenodo Config for SST-33_Enhanced_Heat_Transport_via_Swirl_Coupling")
    print("=" * 80)
    print()
    
    if not tex_file.exists():
        print(f"Error: File not found: {tex_file}")
        return
    
    # Extract metadata
    print("Extracting metadata...")
    metadata = extract_metadata_from_latex(tex_file)
    
    if not metadata.get('title'):
        print("Error: No title found")
        return
    
    print(f"Title: {metadata['title']}")
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Create deposit
    print("\nCreating draft deposit on Zenodo...")
    url = f"{automation.base_url}/api/deposit/depositions"
    zenodo_metadata = {
        "metadata": {
            "title": metadata['title'],
            "creators": metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
            "description": metadata.get('description', ''),
            "keywords": metadata.get('keywords', []),
            "upload_type": "publication",
            "publication_type": "article",
            "access_right": "open",
            "license": "cc-by-4.0",
        }
    }
    if metadata.get('publication_date'):
        zenodo_metadata['metadata']['publication_date'] = metadata['publication_date']
    
    response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
    
    if response.status_code == 201:
        deposit = response.json()
        deposit_id = str(deposit['id'])
        print(f"Created deposit: {deposit_id}")
        
        # Get DOI
        metadata_zenodo = deposit.get('metadata', {})
        prereserve = metadata_zenodo.get('prereserve_doi', {})
        if prereserve and 'doi' in prereserve:
            doi = prereserve['doi']
        else:
            doi = metadata_zenodo.get('conceptdoi', '') or metadata_zenodo.get('doi', '')
        
        if not doi:
            time.sleep(1)
            for retry in range(3):
                deposit_info = automation.get_deposit_info(deposit_id)
                if deposit_info:
                    metadata_zenodo = deposit_info.get('metadata', {})
                    prereserve = metadata_zenodo.get('prereserve_doi', {})
                    if prereserve and 'doi' in prereserve:
                        doi = prereserve['doi']
                        break
                    doi = metadata_zenodo.get('conceptdoi', '') or metadata_zenodo.get('doi', '')
                    if doi:
                        break
                time.sleep(1)
        
        if doi:
            print(f"[OK] Got DOI: {doi}")
            
            # Create config
            config_file = tex_file.with_suffix('.zenodo.json')
            config_data = {
                'title': metadata['title'],
                'creators': metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', []),
                'publication_date': metadata.get('publication_date', ''),
                'doi': doi,
                'tex_file': str(tex_file.relative_to(base_dir)),
                'upload_type': 'publication',
                'publication_type': 'article',
                'deposit_id': deposit_id
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Created config: {config_file.name}")
            
            # Add DOI to LaTeX
            print("\nAdding DOI to LaTeX file...")
            if add_doi_to_latex(tex_file, doi):
                print(f"[OK] Added DOI to LaTeX file")
                print(f"\n[OK] Successfully processed SST-33_Enhanced_Heat_Transport")
            else:
                print(f"[ERROR] Failed to add DOI to LaTeX file")
        else:
            print("[ERROR] No DOI returned")
    else:
        print(f"[ERROR] Failed to create deposit: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == '__main__':
    main()
